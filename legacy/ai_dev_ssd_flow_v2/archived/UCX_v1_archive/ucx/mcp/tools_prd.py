"""MCP Tool definitions for the PRD SDD layer (PLAN-012 workflow).

Exposes six PRD-specific tools with a namespaced ``prd_*`` prefix:

- ``prd_validate_fix``   — Stage 3: create _validation copy
- ``prd_review``         — Stage 4: UCR review → versioned review report
- ``prd_remediate``      — Stage 5: generate fix proposals → remediation report
- ``prd_remediate_apply``— Stage 6: apply fixes → _remediated copy
- ``prd_artifacts``      — Discover and classify all PLAN-012 artifacts in a directory
- ``prd_status``         — Workflow stage check with recommended next action

All tools return structured dicts that include every produced file path so that
agent orchestrators can chain calls without out-of-band coordination.
"""

from pathlib import Path
from typing import Any

from ucx.observability.logging import get_logger

logger = get_logger(__name__)


class PRDTools:
    """Layer-specific MCP tools for the PRD SDD layer (PLAN-012 derived-artifact workflow)."""

    def __init__(self, config: Any) -> None:
        """
        Initialize tools with config.

        Args:
            config: UCX configuration
        """
        self._config = config

    def register(self, mcp: Any) -> None:
        """Register all PRD tools with the MCP server.

        Args:
            mcp: FastMCP instance
        """
        self._register_validate_fix(mcp)
        self._register_review(mcp)
        self._register_remediate(mcp)
        self._register_remediate_apply(mcp)
        self._register_artifacts(mcp)
        self._register_status(mcp)

    # ------------------------------------------------------------------ #
    # Stage 3 — validate-fix                                               #
    # ------------------------------------------------------------------ #

    def _register_validate_fix(self, mcp: Any) -> None:
        """Register the prd_validate_fix tool."""

        @mcp.tool()
        def prd_validate_fix(
            source_prd_path: str,
            dry_run: bool = False,
            max_iterations: int = 3,
        ) -> dict:
            """Create a _validation copy with deterministic validation fixes applied (PLAN-012 Stage 3).

            Reads a canonical source PRD, runs an iterative validate/fix loop (up to
            ``max_iterations`` passes), injects PLAN-012 lineage metadata, and writes
            the result as a ``*_validation.md`` copy alongside the source PRD.
            The source PRD is never modified.

            Args:
                source_prd_path: Path to the canonical source PRD (no _validation or _remediated suffix).
                dry_run: If True, show what would be written without creating files.
                max_iterations: Maximum validate/fix passes before stopping (default 3).

            Returns:
                Dict with keys:
                - output_path (str | None): Created file path (None when dry_run=True)
                - output_path_preview (str): Expected output path in all cases
                - fixes_applied (int): Number of auto-fixes applied
                - iterations_run (int): Actual number of validate/fix iterations
                - remaining_issue_count (int): Issues still present after the loop
                - dry_run (bool): Echoes the dry_run flag
                - processing_stage (str): Always "validation-fixed"
                - source_doc_id (str): Parsed PRD doc_id
                - next_step (str): Recommended next tool call

            Raises:
                FileNotFoundError: If source_prd_path does not exist.
                ValueError: If the file is not a source-stage PRD.
            """
            import shutil
            import tempfile
            from datetime import datetime, timezone

            from ucx.models.enums import DocType
            from ucx.utils.reporting import resolve_doc_id_strict
            from ucx.validators.prd import UnifiedPRDValidator
            from ucx.validators.prd.artifact_ops import (
                append_derivation_history_row,
                extract_prd_identity_fields,
                identify_prd_artifact_stage,
                inject_processing_stage_metadata,
                prd_validation_copy_name,
                prd_validation_report_name,
            )
            from ucx.validators.prd.fixer import PRDFixer

            doc_path = Path(source_prd_path)
            if not doc_path.exists():
                raise FileNotFoundError(f"Source PRD not found: {doc_path}")

            stage = identify_prd_artifact_stage(doc_path)
            if stage != "source":
                raise ValueError(
                    f"prd_validate_fix requires a canonical source PRD (stage='source'). "
                    f"Got stage='{stage}' for '{doc_path.name}'. "
                    f"Pass the original PRD without _validation or _remediated suffix."
                )

            doc_id = resolve_doc_id_strict(doc_path, DocType.PRD)
            source_content = doc_path.read_text(encoding="utf-8")
            fields = extract_prd_identity_fields(source_content)
            source_version = fields.get("version") or "0.0.0"

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_file = Path(tmpdir) / doc_path.name
                shutil.copy2(doc_path, tmp_file)

                validator = UnifiedPRDValidator(strict=False, verbose=False)
                all_actions: list = []
                total_iterations = 0
                remaining: list = []

                for iteration in range(1, max_iterations + 1):
                    total_iterations = iteration
                    val_result = validator.validate(tmp_file.parent)
                    issues = val_result.tier1_issues + val_result.tier2_issues

                    if not issues:
                        break

                    prd_fixer = PRDFixer(dry_run=False, verbose=False)
                    fix_result = prd_fixer.fix(tmp_file, issues)
                    all_actions.extend(fix_result.actions)

                    applied_now = sum(1 for a in fix_result.actions if a.status == "applied")
                    if not fix_result.actions or applied_now == 0:
                        break

                final_val_result = validator.validate(tmp_file.parent)
                remaining = final_val_result.tier1_issues + final_val_result.tier2_issues
                fixed_content = tmp_file.read_text(encoding="utf-8")

            fixed_count = sum(1 for a in all_actions if a.status == "applied")
            derivation_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")

            output_content = inject_processing_stage_metadata(
                fixed_content,
                processing_stage="validation-fixed",
                source_doc_id=doc_id,
                source_version=source_version,
                derived_from=doc_path.name,
            )
            output_content = append_derivation_history_row(
                output_content,
                version=source_version,
                date=derivation_date,
                author="UCX Validation Fixer",
                description=(
                    f"Derived validation-fixed copy from `{doc_path.name}` "
                    f"using `{prd_validation_report_name(doc_id)}`"
                ),
            )

            output_stem = prd_validation_copy_name(doc_path.stem)
            output_path = doc_path.parent / f"{output_stem}.md"

            if not dry_run:
                output_path.write_text(output_content, encoding="utf-8")

            return {
                "output_path": str(output_path) if not dry_run else None,
                "output_path_preview": str(output_path),
                "fixes_applied": fixed_count,
                "iterations_run": total_iterations,
                "remaining_issue_count": len(remaining),
                "dry_run": dry_run,
                "processing_stage": "validation-fixed",
                "source_doc_id": doc_id,
                "next_step": (
                    f"prd_review(prd_path='{output_path}')"
                    if not dry_run
                    else "Run prd_validate_fix without dry_run=True first."
                ),
            }

    # ------------------------------------------------------------------ #
    # Stage 4 — review                                                     #
    # ------------------------------------------------------------------ #

    def _register_review(self, mcp: Any) -> None:
        """Register the prd_review tool."""

        config = self._config

        @mcp.tool()
        def prd_review(prd_path: str) -> dict:
            """Review a PRD and produce a versioned UCX review report (PLAN-012 Stage 4).

            Automatically redirects a source PRD to its ``_validation`` copy via
            ``resolve_prd_review_target()``.  Runs a full UCR review and writes a
            versioned ``*.UCX_review_report_vNNN.md`` file alongside the document.

            Args:
                prd_path: Path to the _validation PRD (or source PRD — auto-redirected).

            Returns:
                Dict with keys:
                - score (int): Overall review score 0-100
                - status (str): Review status value
                - report_path (str): Path to the written review report
                - findings (dict): Findings breakdown by priority {"P0": N, "P1": N, "P2": N}
                - has_critical (bool): True if any P0 findings exist
                - total_findings (int): Sum of all findings
                - validation_prd_path (str): Resolved _validation copy that was reviewed
                - elapsed_time (float): Seconds the review took
                - next_step (str): Recommended next tool call

            Raises:
                FileNotFoundError: If prd_path does not exist.
            """
            from ucx.api.review import UCRPhase
            from ucx.validators.prd.artifact_ops import resolve_prd_review_target

            doc_path = Path(prd_path)
            if not doc_path.exists():
                raise FileNotFoundError(f"PRD not found: {doc_path}")

            resolved_path = resolve_prd_review_target(doc_path)

            ucr = UCRPhase(config=config)
            result = ucr.review("prd", resolved_path)

            return {
                "score": result.score,
                "status": result.status.value,
                "report_path": str(result.report_path),
                "findings": result.findings,
                "has_critical": result.has_critical,
                "total_findings": result.total_findings,
                "validation_prd_path": str(resolved_path),
                "elapsed_time": round(result.elapsed_time, 2),
                "next_step": (
                    f"prd_remediate("
                    f"validation_prd_path='{resolved_path}', "
                    f"review_report_path='{result.report_path}')"
                ),
            }

    # ------------------------------------------------------------------ #
    # Stage 5 — remediate                                                  #
    # ------------------------------------------------------------------ #

    def _register_remediate(self, mcp: Any) -> None:
        """Register the prd_remediate tool."""

        config = self._config

        @mcp.tool()
        def prd_remediate(
            validation_prd_path: str,
            review_report_path: str,
        ) -> dict:
            """Generate fix proposals from a UCX review report (PLAN-012 Stage 5).

            Enforces the PLAN-012 contract at the API level:
            - ``validation_prd_path`` must be a ``processing_stage: validation-fixed`` PRD.
            - ``review_report_path`` must be a ``*.UCX_review_report_vNNN.md`` file.

            Uses multi-persona pre-screening to load only the required fixer personas and
            writes a versioned ``*.UCX_remediation_report_vNNN.md`` alongside the document.

            Args:
                validation_prd_path: Path to the _validation PRD (processing_stage: validation-fixed).
                review_report_path: Path to the ``*.UCX_review_report_vNNN.md`` review report.

            Returns:
                Dict with keys:
                - report_path (str): Path to the written remediation report
                - fix_count (int): Total fix proposals generated
                - auto_safe_count (int): Proposals marked AUTO_SAFE (safe to apply automatically)
                - manual_review_count (int): Proposals requiring human review
                - fixes_summary (list[dict]): First 10 fixes (description, confidence, gate_code)
                - next_step (str): Recommended next tool call

            Raises:
                FileNotFoundError: If inputs not found.
                ValueError: If PLAN-012 contract is violated (wrong stage or wrong report type).
            """
            from ucx.api.remediation import UCRemPhase

            ucrem = UCRemPhase(config=config)
            fixes, report_path = ucrem.generate_fixes(
                doc_path=Path(validation_prd_path),
                review_report=Path(review_report_path),
            )

            auto_safe_count = sum(
                1
                for f in fixes
                if hasattr(f, "confidence") and str(f.confidence).endswith("AUTO_SAFE")
            )

            return {
                "report_path": str(report_path),
                "fix_count": len(fixes),
                "auto_safe_count": auto_safe_count,
                "manual_review_count": len(fixes) - auto_safe_count,
                "fixes_summary": [
                    {
                        "description": getattr(f, "description", str(f))[:120],
                        "confidence": str(getattr(f, "confidence", "UNKNOWN")),
                        "gate_code": getattr(f, "gate_code", ""),
                    }
                    for f in fixes[:10]
                ],
                "next_step": (
                    f"prd_remediate_apply("
                    f"validation_prd_path='{validation_prd_path}', "
                    f"remediation_report_path='{report_path}')"
                ),
            }

    # ------------------------------------------------------------------ #
    # Stage 6 — remediate-apply                                            #
    # ------------------------------------------------------------------ #

    def _register_remediate_apply(self, mcp: Any) -> None:
        """Register the prd_remediate_apply tool."""

        @mcp.tool()
        def prd_remediate_apply(
            validation_prd_path: str,
            remediation_report_path: str,
            dry_run: bool = False,
        ) -> dict:
            """Create a _remediated copy by applying fixes from a remediation report (PLAN-012 Stage 6).

            Parses ``UCX-ACTION`` blocks from the remediation report, applies
            auto-safe text substitutions, injects PLAN-012 lineage metadata, and
            writes the result as a ``*_remediated.md`` copy.  The _validation PRD
            is never modified.

            Args:
                validation_prd_path: Path to the _validation PRD (processing_stage: validation-fixed).
                remediation_report_path: Path to the ``*.UCX_remediation_report_vNNN.md`` report.
                dry_run: If True, return what would be written without creating files.

            Returns:
                Dict with keys:
                - output_path (str | None): Created file path (None when dry_run=True)
                - output_path_preview (str): Expected output path in all cases
                - fixes_applied (int): Number of UCX-ACTION blocks that were applied
                - processing_stage (str): Always "remediated"
                - derived_from (str): Name of the _validation PRD used as input
                - dry_run (bool): Echoes the dry_run flag
                - next_step (str): Recommended next action

            Raises:
                FileNotFoundError: If either input file is not found.
                ValueError: If the input is not a _validation-stage PRD.
            """
            from datetime import datetime, timezone

            from ucx.models.enums import DocType
            from ucx.utils.reporting import resolve_doc_id_strict
            from ucx.validators.prd.artifact_ops import (
                apply_ucx_action_fixes,
                append_derivation_history_row,
                extract_prd_identity_fields,
                identify_prd_artifact_stage,
                inject_processing_stage_metadata,
                prd_remediated_copy_name,
            )

            doc_path = Path(validation_prd_path)
            report_path = Path(remediation_report_path)

            if not doc_path.exists():
                raise FileNotFoundError(f"Validation PRD not found: {doc_path}")
            if not report_path.exists():
                raise FileNotFoundError(f"Remediation report not found: {report_path}")

            stage = identify_prd_artifact_stage(doc_path)
            if stage != "validation-fixed":
                raise ValueError(
                    f"prd_remediate_apply requires a _validation PRD (stage='validation-fixed'). "
                    f"Got stage='{stage}' for '{doc_path.name}'."
                )

            doc_id = resolve_doc_id_strict(doc_path, DocType.PRD)
            validation_content = doc_path.read_text(encoding="utf-8")
            fields = extract_prd_identity_fields(validation_content)
            source_version = fields.get("version") or "0.0.0"
            source_doc_id = fields.get("source_doc_id") or doc_id

            report_content = report_path.read_text(encoding="utf-8")
            applied = apply_ucx_action_fixes(validation_content, report_content)
            fixed_count = applied["count"]
            fixed_content = applied["content"]

            derivation_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00Z")
            output_content = inject_processing_stage_metadata(
                fixed_content,
                processing_stage="remediated",
                source_doc_id=source_doc_id,
                source_version=source_version,
                derived_from=doc_path.name,
            )
            output_content = append_derivation_history_row(
                output_content,
                version=source_version,
                date=derivation_date,
                author="UCX Remediation Apply",
                description=(
                    f"Derived remediated copy from `{doc_path.name}` using `{report_path.name}`"
                ),
            )

            output_stem = prd_remediated_copy_name(doc_path.stem)
            output_path = doc_path.parent / f"{output_stem}.md"

            if not dry_run:
                output_path.write_text(output_content, encoding="utf-8")

            return {
                "output_path": str(output_path) if not dry_run else None,
                "output_path_preview": str(output_path),
                "fixes_applied": fixed_count,
                "processing_stage": "remediated",
                "derived_from": doc_path.name,
                "dry_run": dry_run,
                "next_step": (
                    f"Review and promote '{output_path.name}' as the final PRD version."
                    if not dry_run
                    else "Run prd_remediate_apply without dry_run=True to create the file."
                ),
            }

    # ------------------------------------------------------------------ #
    # Discovery — artifacts                                                 #
    # ------------------------------------------------------------------ #

    def _register_artifacts(self, mcp: Any) -> None:
        """Register the prd_artifacts tool."""

        @mcp.tool()
        def prd_artifacts(prd_dir: str) -> dict:
            """Discover and classify all PLAN-012 artifacts in a PRD directory.

            Scans ``*.md`` files in the directory and categorises each as:
            source PRD, _validation copy, validation report, review report,
            remediation report, or _remediated copy.

            Useful for agents that need to resolve the current set of artifacts
            before deciding which workflow step to run next.

            Args:
                prd_dir: Path to the PRD document directory (e.g. ``docs/02_PRD/PRD-01/``).

            Returns:
                Dict with keys:
                - source_prds (list[str])
                - validation_copies (list[str])
                - validation_reports (list[str])
                - review_reports (list[str])
                - remediation_reports (list[str])
                - remediated_copies (list[str])
                - total_artifacts (int)

            Raises:
                FileNotFoundError: If prd_dir does not exist.
            """
            from ucx.validators.prd.artifact_ops import identify_prd_artifact_stage

            directory = Path(prd_dir)
            if not directory.exists():
                raise FileNotFoundError(f"PRD directory not found: {directory}")

            source_prds: list[str] = []
            validation_copies: list[str] = []
            validation_reports: list[str] = []
            review_reports: list[str] = []
            remediation_reports: list[str] = []
            remediated_copies: list[str] = []

            for md_file in sorted(directory.glob("*.md")):
                name = md_file.name
                if ".UCX_review_report_v" in name:
                    review_reports.append(str(md_file))
                elif ".UCX_remediation_report_v" in name:
                    remediation_reports.append(str(md_file))
                elif name.endswith("_validation_report.md"):
                    validation_reports.append(str(md_file))
                else:
                    artifact_stage = identify_prd_artifact_stage(md_file)
                    if artifact_stage == "source":
                        source_prds.append(str(md_file))
                    elif artifact_stage == "validation-fixed":
                        validation_copies.append(str(md_file))
                    elif artifact_stage == "remediated":
                        remediated_copies.append(str(md_file))

            return {
                "source_prds": source_prds,
                "validation_copies": validation_copies,
                "validation_reports": validation_reports,
                "review_reports": review_reports,
                "remediation_reports": remediation_reports,
                "remediated_copies": remediated_copies,
                "total_artifacts": (
                    len(source_prds)
                    + len(validation_copies)
                    + len(validation_reports)
                    + len(review_reports)
                    + len(remediation_reports)
                    + len(remediated_copies)
                ),
            }

    # ------------------------------------------------------------------ #
    # Discovery — status                                                    #
    # ------------------------------------------------------------------ #

    def _register_status(self, mcp: Any) -> None:
        """Register the prd_status tool."""

        @mcp.tool()
        def prd_status(prd_dir: str) -> dict:
            """Get PLAN-012 workflow status for a PRD directory.

            Checks which stages of the six-step PLAN-012 workflow are complete
            based on artifact presence and returns the recommended next action.

            Stages tracked:
            1. source-exists       — canonical source PRD is present
            2. validation-report   — ``PRD-NN_validation_report.md`` is present
            3. validation-copy     — ``*_validation.md`` copy is present
            4. review-report       — ``*.UCX_review_report_vNNN.md`` is present
            5. remediation-report  — ``*.UCX_remediation_report_vNNN.md`` is present
            6. remediated-copy     — ``*_remediated.md`` copy is present (workflow done)

            Args:
                prd_dir: Path to the PRD document directory.

            Returns:
                Dict with keys:
                - completed_stages (list[str]): Stage IDs that are complete
                - workflow_complete (bool): True when stage-6 is done
                - next_step (str): Recommended next tool call or message
                - artifacts (dict): All discovered artifact paths by category

            Raises:
                FileNotFoundError: If prd_dir does not exist.
            """
            from ucx.validators.prd.artifact_ops import identify_prd_artifact_stage

            directory = Path(prd_dir)
            if not directory.exists():
                raise FileNotFoundError(f"PRD directory not found: {directory}")

            source_prds: list[Path] = []
            validation_copies: list[Path] = []
            validation_reports: list[Path] = []
            review_reports: list[Path] = []
            remediation_reports: list[Path] = []
            remediated_copies: list[Path] = []

            for md_file in sorted(directory.glob("*.md")):
                name = md_file.name
                if ".UCX_review_report_v" in name:
                    review_reports.append(md_file)
                elif ".UCX_remediation_report_v" in name:
                    remediation_reports.append(md_file)
                elif name.endswith("_validation_report.md"):
                    validation_reports.append(md_file)
                else:
                    artifact_stage = identify_prd_artifact_stage(md_file)
                    if artifact_stage == "source":
                        source_prds.append(md_file)
                    elif artifact_stage == "validation-fixed":
                        validation_copies.append(md_file)
                    elif artifact_stage == "remediated":
                        remediated_copies.append(md_file)

            completed: list[str] = []
            if source_prds:
                completed.append("stage-1-source-exists")
            if validation_reports:
                completed.append("stage-2-validation-report")
            if validation_copies:
                completed.append("stage-3-validation-copy")
            if review_reports:
                completed.append("stage-4-review-report")
            if remediation_reports:
                completed.append("stage-5-remediation-report")
            if remediated_copies:
                completed.append("stage-6-remediated-copy")

            if not source_prds:
                next_step = "No source PRD found. Create the canonical source PRD first."
            elif not validation_copies:
                src = str(source_prds[0])
                next_step = f"prd_validate_fix(source_prd_path='{src}')"
            elif not review_reports:
                val = str(validation_copies[0])
                next_step = f"prd_review(prd_path='{val}')"
            elif not remediation_reports:
                val = str(validation_copies[0])
                rev = str(review_reports[-1])
                next_step = (
                    f"prd_remediate("
                    f"validation_prd_path='{val}', "
                    f"review_report_path='{rev}')"
                )
            elif not remediated_copies:
                val = str(validation_copies[0])
                rem = str(remediation_reports[-1])
                next_step = (
                    f"prd_remediate_apply("
                    f"validation_prd_path='{val}', "
                    f"remediation_report_path='{rem}')"
                )
            else:
                next_step = (
                    "Workflow complete. "
                    f"Review and promote '{remediated_copies[-1].name}' as the final PRD version."
                )

            return {
                "completed_stages": completed,
                "workflow_complete": bool(remediated_copies),
                "next_step": next_step,
                "artifacts": {
                    "source_prds": [str(f) for f in source_prds],
                    "validation_copies": [str(f) for f in validation_copies],
                    "validation_reports": [str(f) for f in validation_reports],
                    "review_reports": [str(f) for f in review_reports],
                    "remediation_reports": [str(f) for f in remediation_reports],
                    "remediated_copies": [str(f) for f in remediated_copies],
                },
            }
