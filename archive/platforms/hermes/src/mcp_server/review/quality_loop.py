"""HERMES-REVIEW-LOOP-001 (H-7) Phase 1 — the bounded, opt-in outer
review→remediate→re-review loop.

An outer wrapper over the single-pass ``run_project_review_build_saga``: each
iteration is a **fresh forward saga run** (avoiding the forward-only transition
table). On a failing gate below the iteration/SOFT_DEADLINE cap, it drives the
remediation pipeline (findings → fix prompt → executor apply) and re-reviews the
remediated copy; at the cap the final saga run break-circuits to PARTIAL_TIMEOUT.

Operating constraint: the gate needs a numeric ``review_score``, which only the
``saga_parallel`` + branch-LLM + framework-crew path produces. Off that path the
score is ``None`` → ``_quality_gate_passed`` returns True → the loop closes on the
first pass (a safe single-pass degrade).
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from mcp_server.executor.dispatcher import run_executor
from mcp_server.prompts.context_builder import SourceSection
from mcp_server.remediation import run_remediate_fix_build, run_remediation_build
from mcp_server.review.saga_orchestrator import (
    SagaReviewResult,
    run_project_review_build_saga,
)

# Implementation-defined SOFT_DEADLINE (REVIEW_SAGA.md §Break-circuit MUST — must sit
# a ≥300s buffer below the host's hard timeout). Conservative default; the loop is
# also bounded by `quality_loop_max_iterations`.
SOFT_DEADLINE_SECONDS = 3600.0


def _sections_from_paths(paths: list[Path]) -> list[SourceSection]:
    """Rebuild review sections from the remediated derived copy files (LB-5 — the
    fan-out consumes `sections`, not `document_path`, so a re-review must re-read the
    remediated file)."""
    sections: list[SourceSection] = []
    for raw in paths:
        path = Path(str(raw))
        if path.is_file():
            sections.append(
                SourceSection(
                    section_id=path.stem,
                    title=f"Source: {path.name}",
                    content=path.read_text(encoding="utf-8"),
                    included=True,
                )
            )
    return sections


def _render_review_findings(findings: list[dict[str, object]] | None) -> str:
    """Render the saga's reduced findings as a markdown block appended to the fixer
    prompt, so the executor actually addresses the gate-failing findings — not only the
    deterministic structural checks `run_remediation_build` surfaces on its own. Without
    this the loop can re-review unchanged substance and burn every iteration."""
    if not findings:
        return ""
    lines = ["", "## Review findings to remediate (address every P0/P1 below)"]
    for f in findings:
        priority = str(f.get("priority", "?"))
        target = str(f.get("target_layer") or f.get("category") or "")
        message = str(f.get("message", "")).strip()
        action = str(f.get("recommended_action", "")).strip()
        head = f"- **[{priority}]**"
        if target:
            head += f" ({target})"
        lines.append(f"{head} {message}")
        if action:
            lines.append(f"  - Recommended action: {action}")
    return "\n".join(lines) + "\n"


def _apply_remediation(
    *,
    project_root: Path,
    doc_type: str,
    layer: str | None,
    document_path: Path,
    output_dir: Path,
    executor_name: str,
    timeout: int,
    project_env: dict[str, str] | None,
    project_overrides: dict | None,
    generation_params: dict[str, object] | None,
    review_findings: list[dict[str, object]] | None = None,
) -> list[Path]:
    """Run the remediation pipeline once (findings → fix prompt → executor apply).

    Mirrors the manual `sdd_remediate` drive: `run_remediation_build` →
    `run_remediate_fix_build` (copy + fix prompt) → `run_executor` (applies the fix
    to the derived copy). The gate-failing `review_findings` are appended to the fix
    prompt so the executor addresses them (the deterministic pipeline alone only sees
    structural checks). Returns the remediated derived paths, or `[]` when nothing was
    produced OR the executor apply failed (→ the caller stops the loop, gate unmet).
    """
    remediation = run_remediation_build(
        project_root=project_root,
        doc_type=doc_type,
        layer=layer,
        document_path=document_path,
        review_report=None,
        output_dir=output_dir,
    )
    fix = run_remediate_fix_build(
        project_root=project_root,
        doc_type=doc_type,
        layer=layer,
        document_path=document_path,
        remediation_report=remediation.report_path,
        output_dir=output_dir,
    )
    derived = [Path(str(p)) for p in fix.derived_paths]
    existing = [p for p in derived if p.exists()]
    if not existing:
        return []
    # Apply the fix to the derived copy via the API executor (run_remediate_fix_build
    # is copy-only — LB-2; the executor is the actual apply). asyncio.run is safe here:
    # the wrapper runs in a worker thread (offloaded from the MCP loop), like the saga's
    # own asyncio.run branch dispatch.
    fix_prompt = fix.report_text + _render_review_findings(review_findings)
    exec_result = asyncio.run(
        run_executor(
            name=executor_name,
            prompt=fix_prompt,
            working_dir=existing[0].parent,
            timeout=timeout,
            project_env=project_env,
            system_prompt=None,
            project_overrides=project_overrides,
            generation_params=generation_params,
        )
    )
    # A failed apply is not silently re-reviewed: surface it as "no remediation" so the
    # loop stops with the gate still unmet, rather than re-reviewing unchanged content.
    if exec_result.exit_code != 0:
        return []
    return existing


def run_review_quality_loop(
    *,
    project_root: Path,
    doc_type: str,
    layer: str | None,
    document_path: Path | None,
    sections: list[SourceSection],
    output_dir: Path,
    executor_name: str,
    max_iterations: int,
    executor_timeout: int = 300,
    soft_deadline_seconds: float = SOFT_DEADLINE_SECONDS,
    project_env: dict[str, str] | None = None,
    project_overrides: dict | None = None,
    generation_params: dict[str, object] | None = None,
    **saga_kwargs: object,
) -> SagaReviewResult:
    """Run the bounded review→remediate→re-review loop; returns the final saga result.

    Each pass is a fresh `run_project_review_build_saga` with `quality_loop=True`;
    the run's FANIN_REDUCED gate decides PASS (CLOSED) vs, on the final iteration,
    PARTIAL_TIMEOUT. Non-final failing passes are remediated + re-reviewed here.
    """
    max_iterations = max(1, int(max_iterations))
    iteration = 1
    current_document_path = document_path
    current_sections = sections
    start = time.monotonic()

    while True:
        deadline_hit = (time.monotonic() - start) > soft_deadline_seconds
        is_final = iteration >= max_iterations or deadline_hit
        result = run_project_review_build_saga(
            project_root=project_root,
            doc_type=doc_type,
            layer=layer,
            document_path=current_document_path,
            sections=current_sections,
            output_dir=output_dir,
            executor_name=executor_name,
            project_env=project_env,
            project_overrides=project_overrides,
            generation_params=generation_params,
            iteration=iteration,
            quality_loop=True,
            is_final_iteration=is_final,
            **saga_kwargs,
        )
        # PASS (gate met → CLOSED) or the final iteration (a failing gate already
        # break-circuited to PARTIAL_TIMEOUT inside the run) → done.
        if result.passed or is_final:
            return result

        # Failing gate below the cap → remediate + re-review the remediated copy.
        # File-based remediation needs a concrete document to copy + fix; a purely
        # section-based review (no document_path) cannot be remediated here, so stop
        # the loop with the gate unmet rather than remediating the output directory.
        if current_document_path is None:
            return result
        derived = _apply_remediation(
            project_root=project_root,
            doc_type=doc_type,
            layer=layer,
            document_path=current_document_path,
            output_dir=output_dir,
            executor_name=executor_name,
            timeout=executor_timeout,
            project_env=project_env,
            project_overrides=project_overrides,
            generation_params=generation_params,
            review_findings=result.reduced_findings,
        )
        if not derived:
            # Remediation produced no derived copy (or the executor apply failed) →
            # nothing improved to re-review; return the last review result (gate unmet;
            # do not loop forever re-reviewing unchanged content).
            return result
        current_document_path = derived[0]
        current_sections = _sections_from_paths(derived)
        iteration += 1
