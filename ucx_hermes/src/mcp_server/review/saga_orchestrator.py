from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import re
import time

from mcp_server.prompts import ContractValidationError, SourceSection
from mcp_server.skills.project_ucx_loader import load_persona_mapping
from mcp_server.skills.project_ucx_loader import load_project_persona_file

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


def _time_bucket() -> str:
    return datetime.utcnow().strftime("%Y%m%d%H")


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


def _write_versioned_json(*, output_dir: Path, stem_prefix: str, payload: dict[str, object]) -> Path:
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
) -> SagaReviewResult:
    if output_dir is None:
        raise ValueError("output_dir is required for saga orchestration")

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
        attempts: dict[str, int] = {
            persona: 0 for persona in personas
        }
        for branch in run.branches.values():
            attempts[branch.persona] = max(attempts.get(branch.persona, 0), int(branch.attempt))
    else:
        run = SagaRunState(
            review_run_id=review_run_id,
            document_path=str(document_path or project_root),
            document_fingerprint=document_fingerprint,
            personas_requested=list(personas),
        )
        journal_path = create_saga_journal(output_dir=output_dir, run=run)
        compensation_count = 0
        attempts = {persona: 0 for persona in personas}

    _safe_transition(journal_path=journal_path, target="FANOUT_STARTED")
    _safe_transition(journal_path=journal_path, target="BRANCH_RUNNING")

    findings: list[dict[str, object]] = []
    max_workers = max(1, min(len(personas), int(max_parallel_branches or len(personas))))
    timeout = int(branch_timeout_seconds) if branch_timeout_seconds else None
    backoff = max(0, int(retry_backoff_seconds or 0))

    completed_personas: set[str] = set()

    while len(completed_personas) < len(personas):
        pending_personas = [p for p in personas if p not in completed_personas]
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
                    for finding in result:
                        finding["branch_id"] = branch_id
                        findings.append(finding)
                    completed_personas.add(persona)
                except Exception as exc:
                    error_code = type(exc).__name__
                    if isinstance(exc, FuturesTimeoutError):
                        error_code = "SagaBranchTimeoutError"

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
                        _safe_transition(journal_path=journal_path, target="ESCALATED")
                        return SagaReviewResult(
                            review_mode="saga_parallel",
                            review_run_id=review_run_id,
                            saga_status="ESCALATED",
                            journal_path=journal_path,
                            prompt_path=None,
                            sidecar_path=None,
                            inspection_path=None,
                            branch_summary={
                                "total": len(personas),
                                "completed": len(completed_personas),
                                "failed": 1,
                            },
                            branch_summary_path=_write_versioned_json(
                                output_dir=output_dir,
                                stem_prefix=f"{doc_id}_{source_stage}_saga_branch_summary",
                                payload={
                                    "review_run_id": review_run_id,
                                    "saga_status": "ESCALATED",
                                    "total": len(personas),
                                    "completed": len(completed_personas),
                                    "failed": 1,
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
                            passed=False,
                        )

        if retries_scheduled > 0:
            if backoff > 0:
                time.sleep(backoff)
            _safe_transition(journal_path=journal_path, target="BRANCH_RUNNING")

    _safe_transition(journal_path=journal_path, target="BRANCH_COMPLETED")
    _safe_transition(journal_path=journal_path, target="FANIN_REDUCED")
    reduced = reduce_persona_findings(findings)
    _safe_transition(journal_path=journal_path, target="SYNTHESIZED")

    aggregate = run_project_review_build(
        project_root=project_root,
        personas=personas,
        doc_type=doc_type,
        template_name=template_name,
        sections=sections,
        layer=layer,
        output_dir=output_dir,
    )
    _safe_transition(journal_path=journal_path, target="CLOSED")

    branch_summary = {"total": len(personas), "completed": len(personas), "failed": 0}
    reducer_summary = {"reduced_count": len(reduced)}
    synthesis_summary = {
        "review_run_id": review_run_id,
        "saga_status": "CLOSED",
        "reduced_count": len(reduced),
        "persona_count": len(personas),
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
        passed=True,
    )
