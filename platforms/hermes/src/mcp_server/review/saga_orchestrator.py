from __future__ import annotations

import asyncio
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from mcp_server.executor.dispatcher import run_executor
from mcp_server.executor.registry import ExecutorConfig, ExecutorType, get_executor
from mcp_server.prompts import ContractValidationError, SourceSection
from mcp_server.skills.project_ucx_loader import load_persona_mapping, load_project_persona_file

from .finding_filter import emit_coverage, filter_findings
from .persona_output_parser import parse_persona_output
from .playbook_loader import PlaybookMissing, load_playbook, normalize_layer
from .review_scoring import score_review
from .runner import run_project_review_build
from .saga_journal import (
    append_compensation_event,
    create_saga_journal,
    load_saga_journal,
    set_branch_state,
    update_run_status,
)
from .saga_models import (
    SagaBranchState,
    SagaRunState,
    deterministic_branch_id,
    deterministic_review_run_id,
)
from .saga_reducer import reduce_persona_findings


@dataclass(frozen=True)
class SagaReviewResult:
    review_mode: str
    review_run_id: str
    saga_status: str
    journal_path: Path
    prompt_path: Path | None
    sidecar_path: Path | None
    inspection_path: Path | None
    branch_summary: dict[str, object]
    branch_summary_path: Path | None
    compensation_summary: dict[str, object]
    reducer_summary: dict[str, object]
    reducer_summary_path: Path | None
    synthesis_summary_path: Path | None
    passed: bool
    reduced_findings: list[dict[str, object]] | None = None
    review_score: dict[str, object] | None = None
    coverage: dict[str, object] | None = None
    playbook_coverage: dict[str, object] | None = None


def _time_bucket() -> str:
    return datetime.now(UTC).strftime("%Y%m%d%H")


_DOC_ID_RE = re.compile(r"([A-Z]+-\d+)")


def _extract_doc_id(*, document_path: Path | None, doc_type: str) -> str:
    if document_path is not None:
        match = _DOC_ID_RE.search(document_path.name.upper())
        if match:
            return match.group(1)
        if document_path.is_dir():
            for candidate in sorted(document_path.glob("*")):
                match = _DOC_ID_RE.search(candidate.name.upper())
                if match:
                    return match.group(1)
    return f"{doc_type.upper()}-00"


def _resolve_source_stage(*, document_path: Path | None) -> str:
    if document_path is None:
        return "validation-fixed"

    name = document_path.name.lower()
    if "_validated" in name:
        return "validation-fixed"
    if "_remediate_copy" in name or re.search(r"_remediate_v\d+", name):
        return "remediated"

    if document_path.is_dir():
        for candidate in sorted(document_path.glob("*")):
            cname = candidate.name.lower()
            if "_validated" in cname:
                return "validation-fixed"
            if "_remediate_copy" in cname or re.search(r"_remediate_v\d+", cname):
                return "remediated"

    return "source"


def _write_versioned_json(
    *, output_dir: Path, stem_prefix: str, payload: dict[str, object]
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"{re.escape(stem_prefix)}_v(\d{{3}})\.json$")

    for _ in range(3):
        max_version = 0
        for path in output_dir.glob(f"{stem_prefix}_v*.json"):
            m = pattern.match(path.name)
            if not m:
                continue
            max_version = max(max_version, int(m.group(1)))
        next_version = max_version + 1
        out_path = output_dir / f"{stem_prefix}_v{next_version:03d}.json"
        try:
            fd = os.open(out_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(payload, sort_keys=True))
            return out_path
        except FileExistsError:
            continue
    raise RuntimeError(f"Unable to allocate versioned saga artifact for prefix={stem_prefix}")


def _as_bool(value: object, *, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _resolve_rollout_phase(project_env: dict[str, str] | None) -> str:
    phase = str((project_env or {}).get("UCX_REVIEW_SAGA_BRANCH_LLM_PHASE", "A")).upper().strip()
    if phase not in {"A", "B", "C"}:
        return "A"
    return phase


def _resolve_branch_llm_enabled(
    *,
    explicit_flag: bool | None,
    project_env: dict[str, str] | None,
) -> bool:
    if explicit_flag is not None:
        return _as_bool(explicit_flag, default=False)

    env = project_env or {}
    if "UCX_REVIEW_SAGA_BRANCH_LLM_ENABLED" in env:
        return _as_bool(env.get("UCX_REVIEW_SAGA_BRANCH_LLM_ENABLED"), default=False)
    if "saga_branch_llm_enabled" in env:
        return _as_bool(env.get("saga_branch_llm_enabled"), default=False)

    # Rollout phase fallback when explicit enablement is not set.
    return _resolve_rollout_phase(project_env) == "C"


_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(sk-[A-Za-z0-9_-]{20,})"),
    re.compile(r"(Bearer\s+[A-Za-z0-9._-]{20,})", re.IGNORECASE),
    re.compile(
        r"((?:api[_-]?key|token|secret)\s*[:=]\s*[\"']?[A-Za-z0-9._-]{8,}[\"']?)", re.IGNORECASE
    ),
)


def _redact_sensitive_text(value: str) -> str:
    redacted = value
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _resolve_review_branch_runtime(
    *,
    project_root: Path,
    doc_type: str,
    persona: str,
    default_timeout: int,
    explicit_executor: str | None,
    explicit_generation_params: dict[str, object] | None,
    explicit_timeout: int | None,
) -> tuple[str, int, dict[str, object]]:
    mapping = load_persona_mapping(project_root=project_root)
    review_map = mapping.get("review", {}) if isinstance(mapping, dict) else {}
    doc_map = review_map.get(doc_type, {}) if isinstance(review_map, dict) else {}

    default_generation: dict[str, object] = {
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": None,
        "max_output_tokens": 4000,
    }

    mapping_executor = ""
    mapping_timeout: int | None = None
    mapping_generation: dict[str, object] = {}

    if isinstance(doc_map, dict):
        mapping_executor = str(doc_map.get("executor", "") or "")
        timeout_raw = doc_map.get("timeout")
        if timeout_raw is not None:
            try:
                mapping_timeout = int(timeout_raw)
            except (TypeError, ValueError):
                mapping_timeout = None

        generation_cfg = doc_map.get("generation", {})
        if isinstance(generation_cfg, dict):
            mapping_generation = dict(generation_cfg)

        overrides = doc_map.get("persona_overrides", {})
        if isinstance(overrides, dict):
            persona_override = overrides.get(persona, {})
            if isinstance(persona_override, dict):
                if persona_override.get("executor"):
                    mapping_executor = str(persona_override.get("executor"))
                po_timeout = persona_override.get("timeout")
                if po_timeout is not None:
                    try:
                        mapping_timeout = int(po_timeout)
                    except (TypeError, ValueError):
                        pass
                po_generation = persona_override.get("generation", {})
                if isinstance(po_generation, dict):
                    mapping_generation.update(po_generation)

    executor_name = explicit_executor or mapping_executor or "api/openrouter"
    timeout = explicit_timeout or mapping_timeout or default_timeout

    generation = dict(default_generation)
    generation.update(mapping_generation)
    if explicit_generation_params:
        for key, value in explicit_generation_params.items():
            if key in generation and value is not None:
                generation[key] = value

    return executor_name, int(timeout), generation


def _branch_prompt_findings(
    *,
    project_root: Path,
    persona: str,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    layer: str | None,
) -> list[dict[str, object]]:
    # Validate persona exists before branch execution.
    load_project_persona_file(project_root=project_root, persona=persona)

    try:
        branch_review = run_project_review_build(
            project_root=project_root,
            personas=[persona],
            doc_type=doc_type,
            template_name=template_name,
            sections=sections,
            layer=layer,
            output_dir=None,
        )
    except ContractValidationError:
        # Fallback for low-signal persona branches where section mapping is empty.
        return [
            {
                "priority": "P1",
                "category": "coverage",
                "persona": persona,
                "message": "No relevant sections mapped for persona branch; fallback coverage finding emitted",
                "target_layer": layer or "spec",
                "recommended_action": "Review persona mapping or broaden section coverage for this persona.",
            }
        ]

    warnings = branch_review.inspection.get("warnings", [])
    sections = branch_review.inspection.get("sections", {})
    included = sections.get("included", []) if isinstance(sections, dict) else []
    skipped = sections.get("skipped", []) if isinstance(sections, dict) else []

    findings: list[dict[str, object]] = []

    included_count = len(included) if isinstance(included, list) else 0
    skipped_count = len(skipped) if isinstance(skipped, list) else 0
    if included_count == 0:
        findings.append(
            {
                "priority": "P1",
                "category": "coverage",
                "persona": persona,
                "message": "Persona branch has zero included sections after mapping",
                "target_layer": layer or "spec",
                "recommended_action": "Adjust section categorization or persona mapping to ensure branch review coverage.",
            }
        )
    elif skipped_count > included_count:
        findings.append(
            {
                "priority": "P2",
                "category": "coverage",
                "persona": persona,
                "message": f"Branch coverage is narrow (included={included_count}, skipped={skipped_count})",
                "target_layer": layer or "spec",
                "recommended_action": "Review skipped sections for potential persona relevance before remediation.",
            }
        )

    if isinstance(warnings, list) and warnings:
        for warning in warnings:
            warning_text = str(warning)
            if "format degradation" in warning_text:
                category = "structure"
                priority = "P1"
                action = "Ensure required format rules are present in prompt structure blocks."
            elif "token budget warning" in warning_text:
                category = "performance"
                priority = "P1"
                action = "Reduce branch context size or split sections to stay within token budget."
            else:
                category = "quality"
                priority = "P2"
                action = "Review warning context and apply corrective edits as needed."
            findings.append(
                {
                    "priority": priority,
                    "category": category,
                    "persona": persona,
                    "message": warning_text,
                    "target_layer": layer or "spec",
                    "recommended_action": action,
                }
            )

    # Deduplicate by message while preserving order.
    unique: list[dict[str, object]] = []
    seen_messages: set[str] = set()
    for finding in findings:
        msg = str(finding.get("message", ""))
        if msg in seen_messages:
            continue
        seen_messages.add(msg)
        unique.append(finding)

    if not unique:
        findings.append(
            {
                "priority": "P2",
                "category": "quality",
                "persona": persona,
                "message": f"review branch completed (included={included_count}, skipped={skipped_count})",
                "target_layer": layer or "spec",
                "recommended_action": "Assess branch-specific findings.",
            }
        )
        return findings
    return unique


def _branch_llm_findings(
    *,
    project_root: Path,
    persona: str,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    layer: str | None,
    branch_id: str,
    attempt: int,
    executor_name: str,
    timeout_seconds: int,
    generation_params: dict[str, object],
    project_env: dict[str, str] | None,
    project_overrides: dict[str, ExecutorConfig] | None,
) -> dict[str, object]:
    try:
        executor_cfg = get_executor(executor_name, project_overrides=project_overrides)
    except KeyError as exc:
        raise RuntimeError("ExecutorRequired") from exc
    if executor_cfg.executor_type != ExecutorType.API:
        raise RuntimeError("ExecutorTypeNotAllowed")

    # HERMES-PARITY-PHASE-2: resolve the per-(layer, lens) playbook for this branch.
    # None → a non-crew branch persona (fact_checker / chairperson→synthesizer): no
    # playbook, no citation floor, branch runs as before. PlaybookMissing → a crew
    # lens whose file is unexpectedly absent: fail the branch (→ BRANCH_FAILED).
    try:
        playbook = load_playbook(layer, persona)
    except PlaybookMissing as exc:
        raise RuntimeError(f"PlaybookMissing: {exc}") from exc

    try:
        branch_review = run_project_review_build(
            project_root=project_root,
            personas=[persona],
            doc_type=doc_type,
            template_name=template_name,
            sections=sections,
            layer=layer,
            output_dir=None,
            playbook_text=playbook.content if playbook else None,
        )
    except ContractValidationError:
        return {
            "findings": [
                {
                    "priority": "P1",
                    "category": "coverage",
                    "message": "No relevant sections mapped for persona branch; fallback coverage finding emitted",
                    "recommended_action": "Review persona mapping or broaden section coverage for this persona.",
                    "target_layer": layer or "spec",
                    "persona": persona,
                    "branch_id": branch_id,
                    "attempt": str(attempt),
                    "parse_status": "deterministic_fallback",
                }
            ],
            "parse_status": "deterministic_fallback",
            "telemetry": {
                "persona": persona,
                "branch_id": branch_id,
                "attempt": attempt,
                "executor": executor_name,
                "model": None,
                "latency_ms": 0,
                "token_usage": None,
                "parse_status": "deterministic_fallback",
            },
        }

    start = time.perf_counter()
    exec_result = asyncio.run(
        run_executor(
            name=executor_name,
            prompt=branch_review.prompt_text,
            working_dir=project_root,
            timeout=timeout_seconds,
            project_env=project_env,
            system_prompt=None,
            project_overrides=project_overrides,
            generation_params=generation_params,
        )
    )
    latency_ms = int((time.perf_counter() - start) * 1000)

    if exec_result.exit_code != 0:
        raise RuntimeError(f"ExecutorFailed: {exec_result.stderr or exec_result.exit_code}")

    parsed = parse_persona_output(
        output_text=exec_result.stdout,
        persona=persona,
        branch_id=branch_id,
        attempt=attempt,
        default_layer=layer or "spec",
    )

    metadata = exec_result.metadata or {}
    token_usage = metadata.get("usage") if isinstance(metadata, dict) else None
    model_name = metadata.get("model") if isinstance(metadata, dict) else None
    redacted_output = _redact_sensitive_text(exec_result.stdout)

    # Citation floor (LLM path only): when a playbook applies, discard findings that
    # do not cite a valid `check` id (or a beyond-checklist tag). Non-crew personas
    # (playbook is None) keep all findings — they have no checklist to cite against.
    branch_findings = parsed.findings
    if playbook is not None:
        branch_findings, _discarded = filter_findings(branch_findings, set(playbook.check_ids))

    return {
        "findings": branch_findings,
        "parse_status": parsed.parse_status,
        "lens_score": parsed.lens_score,
        "no_findings_rationale": parsed.no_findings_rationale,
        "raw_output_redacted": redacted_output,
        "telemetry": {
            "persona": persona,
            "branch_id": branch_id,
            "attempt": attempt,
            "executor": exec_result.executor_name,
            "model": model_name,
            "latency_ms": latency_ms,
            "token_usage": token_usage,
            "parse_status": parsed.parse_status,
        },
    }


def _safe_transition(*, journal_path: Path, target: str) -> None:
    current = load_saga_journal(journal_path=journal_path).status
    if current == target:
        return
    try:
        update_run_status(journal_path=journal_path, target=target)
    except ValueError:
        # Allow idempotent orchestration retries to continue even if the
        # transition was already advanced by prior steps.
        return


def _compute_review_score(
    *,
    doc_type: str,
    lens_scores: dict[str, float],
    reduced: list,
    lens_findings_count: dict[str, int] | None = None,
    no_findings_rationales: dict[str, str | None] | None = None,
) -> dict[str, object] | None:
    """Framework weighted/capped score + coverage from per-persona lens scores.

    Advisory; only computed when LLM branches supplied ``lens_score``s and the
    doc-type maps to a framework crew (``REVIEW_CREWS.yaml``). Returns ``None``
    otherwise (e.g. deterministic-fallback mode, or a non-layer doc-type).
    """
    if not lens_scores:
        return None
    try:
        rs = score_review(
            layer=doc_type,
            lens_scores=lens_scores,
            findings=[{"priority": item.priority} for item in reduced],
            lens_findings_count=lens_findings_count,
            no_findings_rationale=no_findings_rationales,
        )
    except KeyError:
        return None
    result: dict[str, object] = {
        "score": rs.score,
        "raw_weighted": rs.raw_weighted,
        "no_blocking": rs.no_blocking,
        "has_unresolved_p0": rs.has_unresolved_p0,
        "has_unresolved_p1": rs.has_unresolved_p1,
        "gate_threshold": rs.gate_threshold,
        "coverage": {
            "expected": rs.coverage.expected,
            "ran": rs.coverage.ran,
            "missing": rs.coverage.missing,
            "coverage_ratio": rs.coverage.coverage_ratio,
            "quorum_met": rs.coverage.quorum_met,
            "low_confidence": rs.coverage.low_confidence,
        },
    }
    # STRUCTURE-RAT-001 advisories for each lens capped to 95 (REVIEW_TEAM.md).
    if rs.rationale_capped:
        result["advisories"] = [
            {
                "rule": "STRUCTURE-RAT-001",
                "persona": persona,
                "message": (
                    f"Lens '{persona}' scored 100 with zero findings and no "
                    "no_findings_rationale; capped to 95."
                ),
            }
            for persona in rs.rationale_capped
        ]
    return result


def run_project_review_build_saga(
    *,
    project_root: Path,
    personas: list[str] | None,
    doc_type: str,
    template_name: str,
    sections: list[SourceSection],
    document_path: Path | None = None,
    layer: str | None = None,
    output_dir: Path | None = None,
    max_parallel_branches: int | None = None,
    branch_timeout_seconds: int | None = None,
    max_branch_retries: int = 0,
    retry_backoff_seconds: int | None = None,
    saga_resume: bool = False,
    executor_name: str | None = None,
    project_env: dict[str, str] | None = None,
    project_overrides: dict[str, ExecutorConfig] | None = None,
    generation_params: dict[str, object] | None = None,
    saga_branch_llm_enabled: bool | None = None,
    branch_quorum: float = 0.5,
) -> SagaReviewResult:
    if output_dir is None:
        raise ValueError("output_dir is required for saga orchestration")

    # Author self-claim stripping (REVIEW_TEAM.md §Strip author self-claim) now
    # happens at the shared chokepoint `run_project_review_build` (runner.py), which
    # every saga branch + the aggregate call — so no per-fan-out strip is needed here.

    if not personas:
        mapping = load_persona_mapping(project_root=project_root)
        phase_map = mapping.get("review", {}) if isinstance(mapping, dict) else {}
        doc_map = phase_map.get(doc_type) or phase_map.get("_default")
        if not isinstance(doc_map, dict) or not doc_map.get("personas"):
            raise ValueError(
                f"No saga personas resolved for doc_type={doc_type}. Provide personas or define review mapping."
            )
        personas = list(doc_map["personas"])

    doc_id = _extract_doc_id(document_path=document_path, doc_type=doc_type)
    source_stage = _resolve_source_stage(document_path=document_path)

    document_fingerprint = f"{doc_type}:{len(sections)}:{len(personas)}"
    review_run_id = deterministic_review_run_id(
        document_path=project_root,
        document_fingerprint=document_fingerprint,
        personas=personas,
        time_bucket=_time_bucket(),
    )
    journal_path = output_dir / f"{review_run_id}_saga_journal_v001.json"
    if saga_resume and journal_path.exists():
        run = load_saga_journal(journal_path=journal_path)
        if run.status in {"CLOSED", "ESCALATED"}:
            raise ValueError(
                f"Cannot resume terminal saga run: review_run_id={review_run_id}, status={run.status}"
            )
        compensation_count = len(run.compensation_actions)
        attempts: dict[str, int] = dict.fromkeys(personas, 0)
        for branch in run.branches.values():
            attempts[branch.persona] = max(attempts.get(branch.persona, 0), int(branch.attempt))
    else:
        # Derive the schema-enum `layer` from the *required* doc_type when the
        # *optional* --layer is omitted (H-12 F1). normalize_layer accepts either
        # the doc-type form (`brd`) or the directory form (`01_BRD`).
        _, layer_dir = normalize_layer(layer or doc_type)
        run = SagaRunState(
            review_run_id=review_run_id,
            document_path=str(document_path or project_root),
            document_fingerprint=document_fingerprint,
            personas_requested=list(personas),
            artifact_id=doc_id,
            layer=layer_dir,
            iteration=1,
        )
        journal_path = create_saga_journal(output_dir=output_dir, run=run)
        compensation_count = 0
        attempts = dict.fromkeys(personas, 0)

    _safe_transition(journal_path=journal_path, target="FANOUT_STARTED")
    _safe_transition(journal_path=journal_path, target="BRANCH_RUNNING")

    findings: list[dict[str, object]] = []
    branch_telemetry: list[dict[str, object]] = []
    branch_raw_outputs: list[dict[str, object]] = []
    max_workers = max(1, min(len(personas), int(max_parallel_branches or len(personas))))
    timeout = int(branch_timeout_seconds) if branch_timeout_seconds else None
    backoff = max(0, int(retry_backoff_seconds or 0))

    branch_llm_enabled = _resolve_branch_llm_enabled(
        explicit_flag=saga_branch_llm_enabled,
        project_env=project_env,
    )
    rollout_phase = _resolve_rollout_phase(project_env)
    debug_raw_outputs = _as_bool(
        (project_env or {}).get("UCX_REVIEW_DEBUG_RAW_OUTPUTS"), default=False
    )

    if branch_llm_enabled and not executor_name:
        executor_name = "api/openrouter"

    completed_personas: set[str] = set()
    failed_personas: set[str] = set()
    lens_scores: dict[str, float] = {}
    # STRUCTURE-RAT-001 inputs (H-6.1): per-persona post-filter finding count + the
    # lens's `no_findings_rationale` (if any), keyed by Hermes persona name.
    lens_findings_count: dict[str, int] = {}
    no_findings_rationales: dict[str, str | None] = {}

    while len(completed_personas) + len(failed_personas) < len(personas):
        pending_personas = [
            p for p in personas if p not in completed_personas and p not in failed_personas
        ]
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            future_map = {}
            for persona in pending_personas:
                branch_id = deterministic_branch_id(review_run_id=review_run_id, persona=persona)
                attempts[persona] += 1
                set_branch_state(
                    journal_path=journal_path,
                    branch=SagaBranchState(
                        branch_id=branch_id,
                        persona=persona,
                        status="BRANCH_RUNNING",
                        attempt=attempts[persona],
                    ),
                )
                if branch_llm_enabled:
                    branch_executor_name, branch_timeout, branch_generation = (
                        _resolve_review_branch_runtime(
                            project_root=project_root,
                            doc_type=doc_type,
                            persona=persona,
                            default_timeout=300,
                            explicit_executor=executor_name,
                            explicit_generation_params=generation_params,
                            explicit_timeout=timeout,
                        )
                    )
                    future = pool.submit(
                        _branch_llm_findings,
                        project_root=project_root,
                        persona=persona,
                        doc_type=doc_type,
                        template_name=template_name,
                        sections=sections,
                        layer=layer,
                        branch_id=branch_id,
                        attempt=attempts[persona],
                        executor_name=branch_executor_name,
                        timeout_seconds=branch_timeout,
                        generation_params=branch_generation,
                        project_env=project_env,
                        project_overrides=project_overrides,
                    )
                else:
                    future = pool.submit(
                        _branch_prompt_findings,
                        project_root=project_root,
                        persona=persona,
                        doc_type=doc_type,
                        template_name=template_name,
                        sections=sections,
                        layer=layer,
                    )
                future_map[future] = (persona, branch_id)

            retries_scheduled = 0
            for future, (persona, branch_id) in future_map.items():
                try:
                    result = future.result(timeout=timeout)
                    set_branch_state(
                        journal_path=journal_path,
                        branch=SagaBranchState(
                            branch_id=branch_id,
                            persona=persona,
                            status="BRANCH_COMPLETED",
                            attempt=attempts[persona],
                        ),
                    )
                    if branch_llm_enabled:
                        assert isinstance(result, dict)
                        branch_findings = result.get("findings", [])
                        telemetry = result.get("telemetry", {})
                        raw_output_redacted = result.get("raw_output_redacted")
                        lens_score_value = result.get("lens_score")
                        if isinstance(lens_score_value, (int, float)):
                            lens_scores[persona] = float(lens_score_value)
                        if isinstance(branch_findings, list):
                            branch_finding_dicts = [
                                f for f in branch_findings if isinstance(f, dict)
                            ]
                            findings.extend(branch_finding_dicts)
                            # STRUCTURE-RAT-001 (H-6.1): post-filter finding count +
                            # rationale for this persona's branch.
                            lens_findings_count[persona] = len(branch_finding_dicts)
                            rationale_value = result.get("no_findings_rationale")
                            no_findings_rationales[persona] = (
                                str(rationale_value) if isinstance(rationale_value, str) else None
                            )
                        if isinstance(telemetry, dict):
                            branch_telemetry.append(telemetry)
                        if debug_raw_outputs and isinstance(raw_output_redacted, str):
                            branch_raw_outputs.append(
                                {
                                    "persona": persona,
                                    "branch_id": branch_id,
                                    "attempt": attempts[persona],
                                    "raw_output_redacted": raw_output_redacted,
                                }
                            )
                    else:
                        assert isinstance(result, list)
                        for finding in result:
                            finding["branch_id"] = branch_id
                            finding["attempt"] = str(attempts[persona])
                            finding["parse_status"] = "deterministic_fallback"
                            findings.append(finding)
                        branch_telemetry.append(
                            {
                                "persona": persona,
                                "branch_id": branch_id,
                                "attempt": attempts[persona],
                                "executor": None,
                                "model": None,
                                "latency_ms": 0,
                                "token_usage": None,
                                "parse_status": "deterministic_fallback",
                            }
                        )
                    completed_personas.add(persona)
                except Exception as exc:
                    error_code = type(exc).__name__
                    if isinstance(exc, FuturesTimeoutError):
                        error_code = "BranchTimeoutExceeded"
                    elif "ExecutorFailed" in str(exc):
                        error_code = "ExecutorFailed"
                    elif "parse" in str(exc).lower():
                        error_code = "BranchParseFailed"

                    set_branch_state(
                        journal_path=journal_path,
                        branch=SagaBranchState(
                            branch_id=branch_id,
                            persona=persona,
                            status="BRANCH_FAILED",
                            attempt=attempts[persona],
                            error_code=error_code,
                        ),
                    )
                    _safe_transition(journal_path=journal_path, target="BRANCH_FAILED")

                    if attempts[persona] <= max_branch_retries:
                        _safe_transition(journal_path=journal_path, target="BRANCH_COMPENSATING")
                        append_compensation_event(
                            journal_path=journal_path,
                            action={
                                "branch_id": branch_id,
                                "persona": persona,
                                "attempt": attempts[persona],
                                "action": "retry_branch",
                                "reason": str(exc),
                                "error_code": error_code,
                            },
                        )
                        compensation_count += 1
                        retries_scheduled += 1
                    else:
                        # Retries exhausted for this lens: degrade gracefully —
                        # record the failed lens and proceed. The post-fan-out quorum
                        # check decides whether to escalate (REVIEW_TEAM.md resilience).
                        failed_personas.add(persona)

        if retries_scheduled > 0:
            if backoff > 0:
                time.sleep(backoff)
            _safe_transition(journal_path=journal_path, target="BRANCH_RUNNING")

    requested_total = len(personas)
    ran_total = len(completed_personas)
    branch_coverage_ratio = (ran_total / requested_total) if requested_total else 0.0
    quorum_met = ran_total > 0 and branch_coverage_ratio >= branch_quorum
    low_confidence = len(failed_personas) > 0
    coverage: dict[str, object] = {
        "requested": sorted(personas),
        "completed": sorted(completed_personas),
        "failed": sorted(failed_personas),
        "coverage_ratio": round(branch_coverage_ratio, 4),
        "quorum": branch_quorum,
        "quorum_met": quorum_met,
        "low_confidence": low_confidence,
    }

    # Resilience (REVIEW_TEAM.md): proceed on the returned crew + coverage; escalate
    # only below quorum — never a silent pass, never fail for one missing lens.
    if not quorum_met:
        _safe_transition(journal_path=journal_path, target="ESCALATED")
        escalated_summary: dict[str, object] = {
            "total": requested_total,
            "completed": ran_total,
            "failed": len(failed_personas),
            "branch_llm_enabled": branch_llm_enabled,
            "rollout_phase": rollout_phase,
            "debug_raw_outputs": debug_raw_outputs,
            "branches": branch_telemetry,
            "raw_outputs": branch_raw_outputs,
            "coverage": coverage,
        }
        return SagaReviewResult(
            review_mode="saga_parallel",
            review_run_id=review_run_id,
            saga_status="ESCALATED",
            journal_path=journal_path,
            prompt_path=None,
            sidecar_path=None,
            inspection_path=None,
            branch_summary=escalated_summary,
            branch_summary_path=_write_versioned_json(
                output_dir=output_dir,
                stem_prefix=f"{doc_id}_{source_stage}_saga_branch_summary",
                payload={
                    "review_run_id": review_run_id,
                    "saga_status": "ESCALATED",
                    **escalated_summary,
                },
            ),
            compensation_summary={
                "count": compensation_count,
                "max_branch_retries": max_branch_retries,
                "retry_backoff_seconds": backoff,
                "saga_resume": saga_resume,
            },
            reducer_summary={"reduced_count": 0},
            reducer_summary_path=None,
            synthesis_summary_path=None,
            reduced_findings=None,
            passed=False,
            coverage=coverage,
        )

    _safe_transition(journal_path=journal_path, target="BRANCH_COMPLETED")
    _safe_transition(journal_path=journal_path, target="FANIN_REDUCED")
    reduced = reduce_persona_findings(findings)
    review_score = _compute_review_score(
        doc_type=doc_type,
        lens_scores=lens_scores,
        reduced=reduced,
        lens_findings_count=lens_findings_count,
        no_findings_rationales=no_findings_rationales,
    )
    _safe_transition(journal_path=journal_path, target="SYNTHESIZED")

    aggregate = run_project_review_build(
        project_root=project_root,
        personas=sorted(completed_personas),
        doc_type=doc_type,
        template_name=template_name,
        sections=sections,
        layer=layer,
        output_dir=output_dir,
    )
    _safe_transition(journal_path=journal_path, target="CLOSED")

    branch_summary = {
        "total": requested_total,
        "completed": ran_total,
        "failed": len(failed_personas),
    }
    branch_summary["branch_llm_enabled"] = branch_llm_enabled
    branch_summary["rollout_phase"] = rollout_phase
    branch_summary["debug_raw_outputs"] = debug_raw_outputs
    branch_summary["branches"] = branch_telemetry
    branch_summary["raw_outputs"] = branch_raw_outputs
    branch_summary["coverage"] = coverage
    branch_summary["low_confidence"] = low_confidence
    reducer_summary = {
        "reduced_count": len(reduced),
        "branch_llm_enabled": branch_llm_enabled,
        "rollout_phase": rollout_phase,
    }
    # verdict.playbook_coverage (HERMES-PARITY-PHASE-2): counted from the kept,
    # pre-reduce findings (post-dedup keeps only one branch's citation → under-reports).
    playbook_coverage = emit_coverage(findings)
    synthesis_summary = {
        "review_run_id": review_run_id,
        "saga_status": "CLOSED",
        "reduced_count": len(reduced),
        "persona_count": len(personas),
        "branch_llm_enabled": branch_llm_enabled,
        "rollout_phase": rollout_phase,
        "review_score": review_score,
        "coverage": coverage,
        "playbook_coverage": playbook_coverage,
    }

    branch_summary_path = _write_versioned_json(
        output_dir=output_dir,
        stem_prefix=f"{doc_id}_{source_stage}_saga_branch_summary",
        payload={
            "review_run_id": review_run_id,
            "saga_status": "CLOSED",
            **branch_summary,
        },
    )
    reducer_summary_path = _write_versioned_json(
        output_dir=output_dir,
        stem_prefix=f"{doc_id}_{source_stage}_saga_reducer_summary",
        payload={
            "review_run_id": review_run_id,
            "saga_status": "CLOSED",
            **reducer_summary,
        },
    )
    synthesis_summary_path = _write_versioned_json(
        output_dir=output_dir,
        stem_prefix=f"{doc_id}_{source_stage}_saga_synthesis_summary",
        payload=synthesis_summary,
    )

    return SagaReviewResult(
        review_mode="saga_parallel",
        review_run_id=review_run_id,
        saga_status="CLOSED",
        journal_path=journal_path,
        prompt_path=aggregate.prompt_path,
        sidecar_path=aggregate.sidecar_path,
        inspection_path=aggregate.inspection_path,
        branch_summary=branch_summary,
        branch_summary_path=branch_summary_path,
        compensation_summary={
            "count": compensation_count,
            "max_branch_retries": max_branch_retries,
            "retry_backoff_seconds": backoff,
            "saga_resume": saga_resume,
        },
        reducer_summary=reducer_summary,
        reducer_summary_path=reducer_summary_path,
        synthesis_summary_path=synthesis_summary_path,
        reduced_findings=[
            {
                "finding_id": item.finding_id,
                "action_id": item.action_id,
                "priority": item.priority,
                "category": item.category,
                "personas": item.personas,
                "message": item.message,
                "target_layer": item.target_layer,
                "recommended_action": item.recommended_action,
                "provenance": item.provenance,
                "content_hash": item.content_hash,
                "check": item.check,
            }
            for item in reduced
        ],
        passed=True,
        review_score=review_score,
        coverage=coverage,
        playbook_coverage=playbook_coverage,
    )
