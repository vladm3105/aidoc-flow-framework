from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

from mcp_server.cleanup.runner import run_clean
from mcp_server.consistency import run_consistency_check
from mcp_server.core.stage_output import (
    STAGE_CREATE,
    STAGE_REMEDIATE,
    STAGE_REVIEW,
    STAGE_VALIDATE,
    resolve_stage_output_dir,
)
from mcp_server.preflight import run_preflight
from mcp_server.prescreening import run_prescreen
from mcp_server.prompts import SourceSection
from mcp_server.remediation import (
    run_remediate_fix_build,
    run_remediation_build,
    run_validate_fix_build,
)
from mcp_server.review import (
    run_project_creation_artifact,
    run_project_creation_build,
    run_project_review_build,
    run_project_review_build_saga,
)
from mcp_server.scan import run_scan
from mcp_server.scoring import compare_scores, show_score, validate_score
from mcp_server.skills.scaffold import scaffold_project_ucx
from mcp_server.validation import run_project_validation_build


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcp")
    subparsers = parser.add_subparsers(dest="command")

    _default_project = os.environ.get("SDD_DEFAULT_PROJECT")
    _project_required = _default_project is None
    _project_help = (
        "Project root (default: $SDD_DEFAULT_PROJECT)" if _default_project else "Project root"
    )

    get_project_parser = subparsers.add_parser(
        "get-project", help="Show resolved default project from environment"
    )

    init_parser = subparsers.add_parser("init", help="Scaffold project-specific UCX assets")
    init_parser.add_argument(
        "--project",
        required=_project_required,
        default=_default_project,
        help=_project_help + " where UCX will be created",
    )
    init_parser.add_argument(
        "--update",
        action="store_true",
        default=False,
        help="Overwrite stale files with latest framework versions (protects persona_mappings.yaml)",
    )
    init_parser.add_argument(
        "--update-mappings",
        action="store_true",
        default=False,
        help="Also reset persona_mappings.yaml to framework defaults (requires --update)",
    )

    review_parser = subparsers.add_parser(
        "review-build", help="Assemble project review prompt and diagnostics artifacts"
    )
    review_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    review_parser.add_argument(
        "--personas",
        nargs="+",
        default=None,
        help="Persona list override. If omitted, loaded from persona_mappings.yaml.",
    )
    review_parser.add_argument("--doc-type", required=True, help="Document type label for metadata")
    review_parser.add_argument(
        "--template", required=True, help="Template file in UCX/prompts/templates/review"
    )
    review_parser.add_argument(
        "--layer", default=None, help="Optional SSD layer directory name (e.g. 01_BRD)"
    )
    review_parser.add_argument("--sections-json", default=None, help="Path to sections JSON array")
    review_parser.add_argument(
        "--document",
        default=None,
        help="Path to document file or document directory for auto section loading",
    )
    review_parser.add_argument("--unified", action="store_true", help="Enable unified context mode")
    review_parser.add_argument(
        "--one-turn", action="store_true", help="Enable one-turn review mode"
    )
    review_parser.add_argument(
        "--review-mode",
        choices=["prompt_only", "saga_parallel"],
        default="prompt_only",
        help="Review execution mode. saga_parallel enables saga journal/reducer scaffolding (parallel scheduler controls are forward-compatible).",
    )
    review_parser.add_argument(
        "--max-parallel-branches",
        type=int,
        default=None,
        help="Max concurrent persona branches for saga_parallel mode",
    )
    review_parser.add_argument(
        "--branch-timeout-seconds",
        type=int,
        default=None,
        help="Per-branch timeout for saga_parallel mode",
    )
    review_parser.add_argument(
        "--max-branch-retries",
        type=int,
        default=None,
        help="Max retry attempts per branch for saga_parallel mode",
    )
    review_parser.add_argument(
        "--retry-backoff-seconds",
        type=int,
        default=None,
        help="Retry backoff seconds for saga_parallel mode",
    )
    review_parser.add_argument(
        "--saga-resume", action="store_true", help="Resume existing saga_parallel review run"
    )
    review_parser.add_argument(
        "--saga-branch-llm-enabled",
        action="store_true",
        help="Enable branch-level LLM fan-out/fan-in for saga_parallel mode",
    )
    review_parser.add_argument("--no-resume", action="store_true", help="Disable session resume")
    review_parser.add_argument("--session-ttl", type=int, default=0, help="Session TTL in seconds")
    review_parser.add_argument(
        "--clean-memory", action="store_true", help="Clean review memory artifacts before execution"
    )
    review_parser.add_argument(
        "--clean-reports",
        action="store_true",
        help="Clean existing report artifacts in output directory",
    )
    review_parser.add_argument(
        "--keep-versions",
        type=int,
        default=0,
        help="Keep latest N existing report versions when cleaning",
    )
    review_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/review",
    )

    review_alias_parser = subparsers.add_parser(
        "review",
        help="Alias for review-build (UCX_v1 compatibility)",
    )
    review_alias_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    review_alias_parser.add_argument(
        "--personas",
        nargs="+",
        default=None,
        help="Persona list override. If omitted, loaded from persona_mappings.yaml.",
    )
    review_alias_parser.add_argument(
        "--doc-type", required=True, help="Document type label for metadata"
    )
    review_alias_parser.add_argument(
        "--template", required=True, help="Template file in UCX/prompts/templates/review"
    )
    review_alias_parser.add_argument(
        "--layer", default=None, help="Optional SSD layer directory name (e.g. 01_BRD)"
    )
    review_alias_parser.add_argument(
        "--sections-json", default=None, help="Path to sections JSON array"
    )
    review_alias_parser.add_argument(
        "--document",
        default=None,
        help="Path to document file or document directory for auto section loading",
    )
    review_alias_parser.add_argument(
        "--unified", action="store_true", help="Enable unified context mode"
    )
    review_alias_parser.add_argument(
        "--one-turn", action="store_true", help="Enable one-turn review mode"
    )
    review_alias_parser.add_argument(
        "--review-mode",
        choices=["prompt_only", "saga_parallel"],
        default="prompt_only",
        help="Review execution mode. saga_parallel enables saga journal/reducer scaffolding (parallel scheduler controls are forward-compatible).",
    )
    review_alias_parser.add_argument(
        "--max-parallel-branches",
        type=int,
        default=None,
        help="Max concurrent persona branches for saga_parallel mode",
    )
    review_alias_parser.add_argument(
        "--branch-timeout-seconds",
        type=int,
        default=None,
        help="Per-branch timeout for saga_parallel mode",
    )
    review_alias_parser.add_argument(
        "--max-branch-retries",
        type=int,
        default=None,
        help="Max retry attempts per branch for saga_parallel mode",
    )
    review_alias_parser.add_argument(
        "--retry-backoff-seconds",
        type=int,
        default=None,
        help="Retry backoff seconds for saga_parallel mode",
    )
    review_alias_parser.add_argument(
        "--saga-resume", action="store_true", help="Resume existing saga_parallel review run"
    )
    review_alias_parser.add_argument(
        "--saga-branch-llm-enabled",
        action="store_true",
        help="Enable branch-level LLM fan-out/fan-in for saga_parallel mode",
    )
    review_alias_parser.add_argument(
        "--no-resume", action="store_true", help="Disable session resume"
    )
    review_alias_parser.add_argument(
        "--session-ttl", type=int, default=0, help="Session TTL in seconds"
    )
    review_alias_parser.add_argument(
        "--clean-memory", action="store_true", help="Clean review memory artifacts before execution"
    )
    review_alias_parser.add_argument(
        "--clean-reports",
        action="store_true",
        help="Clean existing report artifacts in output directory",
    )
    review_alias_parser.add_argument(
        "--keep-versions",
        type=int,
        default=0,
        help="Keep latest N existing report versions when cleaning",
    )
    review_alias_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/review",
    )

    create_parser = subparsers.add_parser(
        "create-build", help="Assemble project creation prompt with SSD layer assets"
    )
    create_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    create_parser.add_argument(
        "--personas",
        nargs="+",
        default=None,
        help="Persona list override. If omitted, loaded from persona_mappings.yaml.",
    )
    create_parser.add_argument(
        "--doc-type", required=True, help="Document type label (e.g. brd, prd)"
    )
    create_parser.add_argument(
        "--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)"
    )
    create_parser.add_argument(
        "--template", required=True, help="Template file in UCX/prompts/templates/creation"
    )
    create_parser.add_argument(
        "--sections-json", default=None, help="Optional path to sections JSON array"
    )
    create_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/creation",
    )

    create_artifact_parser = subparsers.add_parser(
        "create",
        help="Create final document artifact at target path using project/layer templates",
    )
    create_artifact_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    create_artifact_parser.add_argument(
        "--personas",
        nargs="+",
        default=None,
        help="Persona list override. If omitted, loaded from persona_mappings.yaml.",
    )
    create_artifact_parser.add_argument(
        "--doc-type", required=True, help="Document type label (e.g. brd, prd)"
    )
    create_artifact_parser.add_argument(
        "--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)"
    )
    create_artifact_parser.add_argument(
        "--template", required=True, help="Template file in UCX/prompts/templates/creation"
    )
    create_artifact_parser.add_argument(
        "--target", required=True, help="Final target document path to create"
    )
    create_artifact_parser.add_argument(
        "--sections-json", default=None, help="Optional path to sections JSON array"
    )
    create_artifact_parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite target document if it exists"
    )
    create_artifact_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory for creation prompt diagnostics",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Run script-based document structure validation against layer template/schema assets",
    )
    validate_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    validate_parser.add_argument(
        "--doc-type", required=True, help="Document type label (e.g. brd, prd)"
    )
    validate_parser.add_argument(
        "--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)"
    )
    validate_parser.add_argument(
        "--document", required=True, help="Path to document file or document directory"
    )
    validate_parser.add_argument(
        "--tier1-only", action="store_true", help="Evaluate only tier1 checks"
    )
    validate_parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    validate_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Validation output format"
    )
    validate_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/validate",
    )
    validate_parser.add_argument(
        "--validation-report",
        default=None,
        help="Path to existing validation report. Skips re-validation, generates fix artifacts from this report.",
    )

    remediate_parser = subparsers.add_parser(
        "remediate",
        help="Run AI remediation from review findings and generate source-protected derived artifacts",
    )
    remediate_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    remediate_parser.add_argument(
        "--doc-type", required=True, help="Document type label (e.g. brd, prd)"
    )
    remediate_parser.add_argument(
        "--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)"
    )
    remediate_parser.add_argument(
        "--document", required=True, help="Path to document file or document directory"
    )
    remediate_parser.add_argument(
        "--review-report",
        default=None,
        help="Optional path to review report consumed by remediation",
    )
    remediate_parser.add_argument(
        "--remediation-report",
        default=None,
        help="Optional path to existing remediation report consumed by --fix apply phase",
    )
    remediate_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/remediation",
    )
    remediate_parser.add_argument(
        "--fix",
        action="store_true",
        default=False,
        help="Deprecated compatibility flag. Remediation apply runs by default.",
    )
    remediate_parser.add_argument(
        "--executor",
        default="api/claude-sonnet",
        help="API executor name for remediation apply (default: api/claude-sonnet)",
    )
    remediate_parser.add_argument(
        "--timeout", type=int, default=300, help="Executor timeout in seconds"
    )

    remediate_fix_parser = subparsers.add_parser(
        "remediate-fix",
        help="Generate source-protected remediated derived artifacts",
    )
    remediate_fix_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    remediate_fix_parser.add_argument(
        "--doc-type", required=True, help="Document type label (e.g. brd, prd)"
    )
    remediate_fix_parser.add_argument(
        "--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)"
    )
    remediate_fix_parser.add_argument(
        "--document", required=True, help="Path to document file or document directory"
    )
    remediate_fix_parser.add_argument(
        "--remediation-report",
        default=None,
        help="Optional path to remediation report consumed by apply phase",
    )
    remediate_fix_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/remediation",
    )

    validate_fix_parser = subparsers.add_parser(
        "validate-fix",
        help="[DEPRECATED] Use 'validate' instead. Generates validation + fix artifacts.",
    )
    validate_fix_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    validate_fix_parser.add_argument(
        "--doc-type", required=True, help="Document type label (e.g. brd, prd)"
    )
    validate_fix_parser.add_argument(
        "--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)"
    )
    validate_fix_parser.add_argument(
        "--document", required=True, help="Path to document file or document directory"
    )
    validate_fix_parser.add_argument(
        "--validation-report",
        default=None,
        help="Optional path to validation report consumed by fix phase",
    )
    validate_fix_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/validate",
    )

    personas_show_parser = subparsers.add_parser(
        "personas-show", help="Show persona assignments for a project"
    )
    personas_show_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    personas_show_parser.add_argument(
        "--phase", choices=["creation", "review", "remediation"], default=None
    )
    personas_show_parser.add_argument("--doc-type", default=None, help="Filter by document type")
    personas_show_parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="output_format"
    )

    personas_set_parser = subparsers.add_parser(
        "personas-set", help="Update persona list for a phase+doctype"
    )
    personas_set_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    personas_set_parser.add_argument(
        "--phase", required=True, choices=["creation", "review", "remediation"]
    )
    personas_set_parser.add_argument(
        "--doc-type", required=True, help="Document type (e.g. brd, prd, _default)"
    )
    personas_set_parser.add_argument(
        "--personas", nargs="+", required=True, help="Ordered persona names"
    )

    personas_diff_parser = subparsers.add_parser(
        "personas-diff", help="Compare project persona mappings against framework defaults"
    )
    personas_diff_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    personas_diff_parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="output_format"
    )

    env_show_parser = subparsers.add_parser(
        "env-show", help="Show project .env keys without exposing values"
    )
    env_show_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    env_show_parser.add_argument(
        "--format", choices=["text", "json"], default="text", dest="output_format"
    )

    prescreen_parser = subparsers.add_parser(
        "prescreen", help="Prescreen documents for deterministic remediation candidates"
    )
    prescreen_parser.add_argument(
        "--document", required=True, help="Path to document file or document directory"
    )
    prescreen_parser.add_argument(
        "--out", default=None, help="Optional output directory for prescreen artifacts"
    )

    scan_parser = subparsers.add_parser(
        "scan", help="Scan validation or remediation reports for finding category metrics"
    )
    scan_parser.add_argument(
        "--report-file", required=True, help="Path to JSON report file to scan"
    )
    scan_parser.add_argument(
        "--out", default=None, help="Optional output directory for scan artifacts"
    )

    scoring_parser = subparsers.add_parser("scoring", help="Score report quality metrics")
    scoring_subparsers = scoring_parser.add_subparsers(dest="scoring_command")

    scoring_show_parser = scoring_subparsers.add_parser("show", help="Show score for a report")
    scoring_show_parser.add_argument(
        "--report-file", required=True, help="Path to JSON report file"
    )

    scoring_validate_parser = scoring_subparsers.add_parser(
        "validate", help="Validate score threshold for a report"
    )
    scoring_validate_parser.add_argument(
        "--report-file", required=True, help="Path to JSON report file"
    )
    scoring_validate_parser.add_argument(
        "--threshold", type=int, required=True, help="Minimum required score"
    )

    scoring_compare_parser = scoring_subparsers.add_parser(
        "compare", help="Compare scores between baseline and candidate reports"
    )
    scoring_compare_parser.add_argument(
        "--baseline-report-file", required=True, help="Path to baseline JSON report"
    )
    scoring_compare_parser.add_argument(
        "--candidate-report-file", required=True, help="Path to candidate JSON report"
    )

    consistency_parser = subparsers.add_parser(
        "consistency",
        help="Run lightweight artifact lineage and stage consistency checks",
    )
    consistency_parser.add_argument(
        "--target", required=True, help="Path to source document file or document directory"
    )
    consistency_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Consistency output format"
    )
    consistency_parser.add_argument(
        "--out", default=None, help="Optional output directory for consistency artifacts"
    )

    validate_links_parser = subparsers.add_parser(
        "validate-links",
        help="Validate markdown links in documentation files",
    )
    validate_links_parser.add_argument(
        "--target", required=True, help="Path to file or directory to scan"
    )
    validate_links_parser.add_argument(
        "--workspace-root", default=None, help="Workspace root for resolving absolute paths"
    )
    validate_links_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    validate_links_parser.add_argument("--out", default=None, help="Output directory for reports")

    preflight_parser = subparsers.add_parser(
        "preflight",
        help="Run runtime and environment readiness checks before create, review, or remediation stages",
    )
    preflight_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    preflight_parser.add_argument(
        "--context",
        choices=["create", "review", "remediate", "any"],
        default="any",
        help="Operational context for required readiness checks",
    )
    preflight_parser.add_argument(
        "--document", default=None, help="Optional document path to verify"
    )
    preflight_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Preflight output format"
    )
    preflight_parser.add_argument(
        "--out", default=None, help="Optional output directory for preflight artifacts"
    )

    clean_parser = subparsers.add_parser(
        "clean",
        help="Remove obsolete stage artifacts from a document folder",
    )
    clean_parser.add_argument(
        "--project", required=_project_required, default=_default_project, help=_project_help
    )
    clean_parser.add_argument(
        "--document", required=True, help="Path to document file or document directory to clean"
    )
    clean_parser.add_argument(
        "--stages",
        nargs="+",
        choices=["validate", "review", "remediate", "creation", "all"],
        default=["all"],
        help="Stages to clean (default: all)",
    )
    clean_parser.add_argument(
        "--keep", type=int, default=1, help="Number of latest versions to keep per artifact type"
    )
    clean_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="List files that would be deleted (default)",
    )
    clean_parser.add_argument(
        "--apply", action="store_true", help="Delete files instead of dry-run listing"
    )
    clean_parser.add_argument(
        "--out", default=None, help="Optional output directory for cleanup report"
    )

    return parser


def _write_review_controls_artifact(output_dir: Path, args: argparse.Namespace) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    controls_path = output_dir / "review_controls.json"
    controls_payload = {
        "unified": bool(args.unified),
        "one_turn": bool(args.one_turn),
        "review_mode": str(args.review_mode),
        "max_parallel_branches": args.max_parallel_branches,
        "branch_timeout_seconds": args.branch_timeout_seconds,
        "max_branch_retries": args.max_branch_retries,
        "retry_backoff_seconds": args.retry_backoff_seconds,
        "saga_resume": bool(args.saga_resume),
        "saga_branch_llm_enabled": bool(args.saga_branch_llm_enabled),
        "no_resume": bool(args.no_resume),
        "session_ttl": int(args.session_ttl),
        "clean_memory": bool(args.clean_memory),
        "clean_reports": bool(args.clean_reports),
        "keep_versions": int(args.keep_versions),
        "effective_behavior": {
            "clean_memory": "applied",
            "clean_reports": "applied",
            "other_controls": "captured_for_runtime_metadata",
        },
    }
    controls_path.write_text(json.dumps(controls_payload, sort_keys=True), encoding="utf-8")
    return controls_path


_CANONICAL_SOURCE_RE = re.compile(r"^[A-Z]+-\d+_.+\.(md|yaml|yml)$")
_REVIEW_SOURCE_EXTENSIONS = {".md", ".yaml", ".yml"}


def _list_review_document_candidates(document_dir: Path) -> list[Path]:
    candidates = sorted(
        list(document_dir.glob("*.md"))
        + list(document_dir.glob("*.yaml"))
        + list(document_dir.glob("*.yml"))
    )
    return [
        path
        for path in candidates
        if "REVIEW" not in path.name.upper()
        and "REPORT" not in path.name.upper()
        and "_validated" not in path.stem
        and "_remediate_copy" not in path.stem
        and not re.search(r"_remediate_v\d+", path.stem)
        and "_LEGACY" not in path.stem
    ]


def _find_canonical_source(document_dir: Path) -> Path | None:
    source_artifacts = [
        path
        for path in _list_review_document_candidates(document_dir)
        if _CANONICAL_SOURCE_RE.match(path.name)
        and not re.search(r"(appendix|appendices)", path.name, re.IGNORECASE)
    ]
    if len(source_artifacts) == 1:
        return source_artifacts[0]
    if len(source_artifacts) > 1:
        yaml_sources = [p for p in source_artifacts if p.suffix.lower() in {".yaml", ".yml"}]
        if len(yaml_sources) == 1:
            return yaml_sources[0]
    return None


def _collect_review_document_files(document_path: Path) -> list[Path]:
    document_dir = document_path if document_path.is_dir() else document_path.parent
    candidates = _list_review_document_candidates(document_dir)
    if (
        not candidates
        and document_path.is_file()
        and document_path.suffix.lower() in _REVIEW_SOURCE_EXTENSIONS
    ):
        return [document_path]

    selected: list[Path] = []
    canonical_source = _find_canonical_source(document_dir)
    if canonical_source is not None:
        selected.append(canonical_source)
    elif document_path.is_file() and document_path.suffix.lower() in _REVIEW_SOURCE_EXTENSIONS:
        selected.append(document_path)

    appendix_files = [
        path
        for path in candidates
        if path not in selected and re.search(r"(appendix|appendices)", path.name, re.IGNORECASE)
    ]
    selected.extend(appendix_files)

    if selected:
        return selected
    return candidates


def _build_review_sections_from_document(
    document_path: Path,
) -> tuple[list[SourceSection], list[Path]]:
    files = _collect_review_document_files(document_path)
    sections = [
        SourceSection(
            section_id=path.stem,
            title=f"Source: {path.name}",
            content=path.read_text(encoding="utf-8"),
            included=True,
        )
        for path in files
    ]
    return sections, files


def _run_validate_command(
    *,
    project_root: Path,
    document_path: Path,
    doc_type: str,
    layer: str,
    output_dir: Path,
    tier1_only: bool = False,
    strict: bool = False,
    format_: str = "text",
    validation_report_path: Path | None = None,
) -> int:
    """Shared validate logic for both 'validate' and deprecated 'validate-fix' CLI commands."""

    # --- Phase 1: Validate (or load existing report) ---
    if validation_report_path and validation_report_path.exists():
        report_data = json.loads(validation_report_path.read_text(encoding="utf-8"))
        errors = report_data.get("errors", [])
        warnings = report_data.get("warnings", [])
        report_path = validation_report_path
        summary_path = None
    else:
        validation_result = run_project_validation_build(
            project_root=project_root,
            doc_type=doc_type,
            layer=layer,
            document_path=document_path,
            output_dir=output_dir,
        )
        payload = validation_result.report
        errors = payload.get("errors", []) if isinstance(payload, dict) else []
        warnings = payload.get("warnings", []) if isinstance(payload, dict) else []
        report_path = validation_result.report_path
        summary_path = validation_result.summary_path

    if not isinstance(errors, list):
        errors = []
    if not isinstance(warnings, list):
        warnings = []

    if tier1_only:
        effective_errors = [
            item
            for item in errors
            if isinstance(item, str)
            and (
                item.startswith("Missing required custom field")
                or item.startswith("Missing required tag")
            )
        ]
    else:
        effective_errors = [item for item in errors if isinstance(item, str)]

    effective_warnings = [item for item in warnings if isinstance(item, str)]
    failed = len(effective_errors) > 0 or (strict and len(effective_warnings) > 0)

    response_payload: dict[str, object] = {
        "report_path": str(report_path) if report_path else None,
        "summary_path": str(summary_path) if summary_path else None,
        "tier1_only": tier1_only,
        "strict": strict,
        "errors": effective_errors,
        "warnings": effective_warnings,
        "is_valid": not failed,
        "passed": not failed,  # CLI: passed == is_valid (exit code signals result). MCP uses passed=True always.
    }

    # --- Phase 2: Fix (conditional — only when validation fails) ---
    if failed:
        try:
            fix_result = run_validate_fix_build(
                project_root=project_root,
                doc_type=doc_type,
                layer=layer,
                document_path=document_path,
                validation_report=report_path,
                output_dir=output_dir,
            )
            response_payload["fix_generated"] = True
            response_payload["fix_report_path"] = str(fix_result.report_path)
            response_payload["fix_summary_path"] = str(fix_result.summary_path)
            response_payload["derived_paths"] = [str(p) for p in fix_result.derived_paths]
        except (FileNotFoundError, ValueError) as exc:
            print(f"Fix generation failed: {exc}", file=sys.stderr)
            response_payload["fix_generated"] = False
    else:
        response_payload["fix_generated"] = False

    if format_ == "json":
        print(json.dumps(response_payload, sort_keys=True))
    else:
        print(f"Validation report generated at {report_path}")
        if summary_path:
            print(f"Validation summary generated at {summary_path}")
        print(f"Tier1-only mode: {tier1_only}")
        print(f"Strict mode: {strict}")
        print("Validation status: PASSED" if not failed else "Validation status: FAILED")
        if response_payload.get("fix_generated"):
            print(f"Fix report: {response_payload.get('fix_report_path')}")
            print(f"Derived copies: {len(response_payload.get('derived_paths', []))}")

    return 0 if not failed else 1


def _print_personas_table(result: dict) -> None:
    """Print persona mappings as a human-readable table."""
    mappings = result.get("mappings", {})
    if not mappings:
        print("No mappings found.")
        return
    for phase, doctypes in mappings.items():
        print(f"\n{phase.upper()}")
        print("-" * 60)
        for dt, config in sorted(doctypes.items()):
            personas = config.get("personas", []) if isinstance(config, dict) else []
            print(f"  {dt:<12} {', '.join(personas)}")


def _print_diff_summary(result: dict) -> None:
    """Print persona diff as a human-readable summary."""
    summary = result.get("summary", {})
    if summary.get("changed") == 0 and summary.get("added") == 0 and summary.get("removed") == 0:
        print(f"No differences. ({summary.get('unchanged', 0)} entries match framework defaults)")
        return
    for entry in result.get("changed", []):
        print(f"CHANGED  {entry['phase']}.{entry['doc_type']}")
        print(f"  project:  {', '.join(entry['project_personas'])}")
        print(f"  default:  {', '.join(entry['default_personas'])}")
    for entry in result.get("added", []):
        print(f"ADDED    {entry['phase']}.{entry['doc_type']}: {', '.join(entry['personas'])}")
    for entry in result.get("removed", []):
        print(f"REMOVED  {entry['phase']}.{entry['doc_type']}: {', '.join(entry['personas'])}")
    print(
        f"\nSummary: {summary.get('changed', 0)} changed, {summary.get('added', 0)} added, "
        f"{summary.get('removed', 0)} removed, {summary.get('unchanged', 0)} unchanged"
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "get-project":
        default = os.environ.get("SDD_DEFAULT_PROJECT")
        if default:
            print(f"SDD_DEFAULT_PROJECT={default}")
        else:
            print("No default project configured. Set SDD_DEFAULT_PROJECT or pass --project.")
        return 0

    if args.command == "init":
        project_root = Path(args.project).expanduser().resolve()
        force_update = getattr(args, "update", False)
        force_update_mappings = getattr(args, "update_mappings", False)
        if force_update_mappings and not force_update:
            print("init failed: --update-mappings requires --update")
            return 2
        init_result = scaffold_project_ucx(
            project_root=project_root,
            force_update=force_update,
            force_update_mappings=force_update_mappings,
        )
        print(f"Initialized project UCX scaffold at {init_result.project_root}")
        print(f"Created: {init_result.created_count}")
        print(f"Skipped existing: {init_result.skipped_count}")
        if init_result.updated_count:
            print(f"Updated: {init_result.updated_count}")
        if init_result.protected_count:
            print(f"Protected (project-owned): {init_result.protected_count}")
        return 0

    if args.command in {"review-build", "review"}:
        project_root = Path(args.project).expanduser().resolve()
        sections_json = (
            Path(args.sections_json).expanduser().resolve() if args.sections_json else None
        )
        review_document = Path(args.document).expanduser().resolve() if args.document else None
        if sections_json is None and review_document is None:
            print("review-build failed: provide --sections-json or --document")
            return 2

        selected_files: list[Path] = []
        if sections_json is not None:
            payload = json.loads(sections_json.read_text(encoding="utf-8"))
            review_sections = [
                SourceSection(
                    section_id=item["section_id"],
                    title=item["title"],
                    content=item["content"],
                    included=item.get("included", True),
                )
                for item in payload
            ]
            document_dir_for_output = sections_json.parent
        else:
            assert review_document is not None
            review_sections, selected_files = _build_review_sections_from_document(review_document)
            if not review_sections:
                print(
                    "review-build failed: no supported sources found for --document (.md/.yaml/.yml)"
                )
                return 1
            document_dir_for_output = (
                review_document if review_document.is_dir() else review_document.parent
            )

        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REVIEW,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_dir_for_output,
        )

        if args.clean_memory:
            review_memory_dir = project_root / "tmp/review_memory"
            if review_memory_dir.exists():
                shutil.rmtree(review_memory_dir)

        if args.clean_reports and output_dir.exists():
            keep_versions = max(0, int(args.keep_versions))
            candidates = sorted(
                output_dir.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True
            )
            for path in candidates[keep_versions:]:
                if path.is_file():
                    path.unlink()

        if args.review_mode == "saga_parallel":
            review_result = run_project_review_build_saga(
                project_root=project_root,
                personas=args.personas,
                doc_type=args.doc_type,
                template_name=args.template,
                sections=review_sections,
                document_path=review_document,
                layer=args.layer,
                output_dir=output_dir,
                max_parallel_branches=args.max_parallel_branches,
                branch_timeout_seconds=args.branch_timeout_seconds,
                max_branch_retries=int(args.max_branch_retries or 0),
                retry_backoff_seconds=args.retry_backoff_seconds,
                saga_resume=bool(args.saga_resume),
                saga_branch_llm_enabled=bool(args.saga_branch_llm_enabled),
            )
        else:
            review_result = run_project_review_build(
                project_root=project_root,
                personas=args.personas,
                doc_type=args.doc_type,
                template_name=args.template,
                sections=review_sections,
                layer=args.layer,
                output_dir=output_dir,
            )
        controls_path = _write_review_controls_artifact(output_dir=output_dir, args=args)
        print(f"Review prompt generated at {review_result.prompt_path}")
        print(f"Sidecar generated at {review_result.sidecar_path}")
        print(f"Inspection generated at {review_result.inspection_path}")
        if args.review_mode == "saga_parallel":
            print(f"Saga review run id: {review_result.review_run_id}")
            print(f"Saga status: {review_result.saga_status}")
            print(f"Saga journal: {review_result.journal_path}")
        print(f"Review controls artifact generated at {controls_path}")
        if getattr(review_result, "layer_asset_names", None):
            print(f"Layer assets included: {review_result.layer_asset_names}")
        if selected_files:
            print(f"Auto-loaded review files: {[str(path) for path in selected_files]}")
        print(
            "Review controls: "
            f"review_mode={args.review_mode}, unified={args.unified}, one_turn={args.one_turn}, no_resume={args.no_resume}, "
            f"session_ttl={args.session_ttl}, clean_memory={args.clean_memory}, clean_reports={args.clean_reports}, "
            f"keep_versions={args.keep_versions}, max_parallel_branches={args.max_parallel_branches}, "
            f"branch_timeout_seconds={args.branch_timeout_seconds}, max_branch_retries={args.max_branch_retries}, "
            f"retry_backoff_seconds={args.retry_backoff_seconds}, saga_resume={args.saga_resume}, "
            f"saga_branch_llm_enabled={args.saga_branch_llm_enabled}"
        )
        return 0

    if args.command == "create-build":
        project_root = Path(args.project).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        creation_sections = None
        sections_path = None
        if args.sections_json:
            sections_path = Path(args.sections_json).expanduser().resolve()
            payload = json.loads(sections_path.read_text(encoding="utf-8"))
            creation_sections = [
                SourceSection(
                    section_id=item["section_id"],
                    title=item["title"],
                    content=item["content"],
                    included=item.get("included", True),
                )
                for item in payload
            ]
        output_dir = resolve_stage_output_dir(
            stage=STAGE_CREATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=sections_path.parent if sections_path is not None else None,
        )

        creation_result = run_project_creation_build(
            project_root=project_root,
            personas=args.personas,
            doc_type=args.doc_type,
            layer=args.layer,
            template_name=args.template,
            sections=creation_sections,
            output_dir=output_dir,
        )
        print(f"Creation prompt generated at {creation_result.prompt_path}")
        print(f"Layer assets included: {creation_result.layer_asset_names}")
        return 0

    if args.command == "create":
        project_root = Path(args.project).expanduser().resolve()
        target_path = Path(args.target).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        creation_sections = None
        sections_path = None
        if args.sections_json:
            sections_path = Path(args.sections_json).expanduser().resolve()
            payload = json.loads(sections_path.read_text(encoding="utf-8"))
            creation_sections = [
                SourceSection(
                    section_id=item["section_id"],
                    title=item["title"],
                    content=item["content"],
                    included=item.get("included", True),
                )
                for item in payload
            ]

        output_dir = resolve_stage_output_dir(
            stage=STAGE_CREATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=target_path.parent if sections_path is None else sections_path.parent,
        )

        try:
            creation_artifact_result = run_project_creation_artifact(
                project_root=project_root,
                personas=args.personas,
                doc_type=args.doc_type,
                layer=args.layer,
                template_name=args.template,
                target_path=target_path,
                sections=creation_sections,
                output_dir=output_dir,
                overwrite=bool(args.overwrite),
            )
        except (FileExistsError, ValueError) as exc:
            print(f"create failed: {exc}")
            return 1

        print(f"Created document artifact at {creation_artifact_result.target_path}")
        print(f"Template source: {creation_artifact_result.template_source}")
        if creation_artifact_result.prompt_path is not None:
            print(f"Creation prompt generated at {creation_artifact_result.prompt_path}")
        if creation_artifact_result.sidecar_path is not None:
            print(f"Creation sidecar generated at {creation_artifact_result.sidecar_path}")
        if creation_artifact_result.inspection_path is not None:
            print(f"Creation inspection generated at {creation_artifact_result.inspection_path}")
        return 0

    if args.command == "validate":
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        validation_report_path = (
            Path(args.validation_report).expanduser().resolve() if args.validation_report else None
        )
        return _run_validate_command(
            project_root=project_root,
            document_path=document_path,
            doc_type=args.doc_type,
            layer=args.layer,
            output_dir=output_dir,
            tier1_only=bool(args.tier1_only),
            strict=bool(args.strict),
            format_=args.format,
            validation_report_path=validation_report_path,
        )

    if args.command == "remediate":
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        review_report = (
            Path(args.review_report).expanduser().resolve() if args.review_report else None
        )
        remediation_report = (
            Path(args.remediation_report).expanduser().resolve()
            if args.remediation_report
            else None
        )
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REMEDIATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )

        if remediation_report is not None and not args.fix:
            print(
                "Warning: --remediation-report is used only with --fix; ignoring provided remediation report."
            )

        if args.fix and remediation_report is not None:
            try:
                fix_result = run_remediate_fix_build(
                    project_root=project_root,
                    doc_type=args.doc_type,
                    layer=args.layer,
                    document_path=document_path,
                    remediation_report=remediation_report,
                    output_dir=output_dir,
                )
            except (FileNotFoundError, ValueError) as exc:
                print(f"remediate --fix failed: {exc}")
                return 1
            print(f"Remediate-fix report generated at {fix_result.report_path}")
            print(f"Remediate-fix summary generated at {fix_result.summary_path}")
            print(f"Derived artifacts created: {len(fix_result.derived_paths)}")
            return 0

        remediation_result = run_remediation_build(
            project_root=project_root,
            doc_type=args.doc_type,
            layer=args.layer,
            document_path=document_path,
            review_report=review_report,
            output_dir=output_dir,
        )
        print(f"Remediation report generated at {remediation_result.report_path}")
        print(f"Remediation summary generated at {remediation_result.summary_path}")

        if args.fix:
            from mcp_server.remediation import run_remediate_fix_build as _run_fix_build

            try:
                fix_result = _run_fix_build(
                    project_root=project_root,
                    doc_type=args.doc_type,
                    layer=args.layer,
                    document_path=document_path,
                    remediation_report=remediation_result.report_path,
                    output_dir=output_dir,
                )
            except (FileNotFoundError, ValueError) as exc:
                print(f"remediate --fix chain failed: {exc}")
                return 1
            print(f"Remediate-fix report generated at {fix_result.report_path}")
            print(f"Derived artifacts created: {len(fix_result.derived_paths)}")

        return 0

    if args.command == "remediate-fix":
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        remediation_report = (
            Path(args.remediation_report).expanduser().resolve()
            if args.remediation_report
            else None
        )
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REMEDIATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        try:
            remediate_fix_result = run_remediate_fix_build(
                project_root=project_root,
                doc_type=args.doc_type,
                layer=args.layer,
                document_path=document_path,
                remediation_report=remediation_report,
                output_dir=output_dir,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"remediate-fix failed: {exc}")
            return 1
        print(f"Remediate-fix report generated at {remediate_fix_result.report_path}")
        print(f"Remediate-fix summary generated at {remediate_fix_result.summary_path}")
        print(f"Derived artifacts created: {len(remediate_fix_result.derived_paths)}")
        return 0

    if args.command == "validate-fix":
        print("WARNING: validate-fix is deprecated. Use 'validate' instead.", file=sys.stderr)
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        validation_report_path = (
            Path(args.validation_report).expanduser().resolve() if args.validation_report else None
        )
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        return _run_validate_command(
            project_root=project_root,
            document_path=document_path,
            doc_type=args.doc_type,
            layer=args.layer,
            output_dir=output_dir,
            tier1_only=False,
            strict=False,
            format_="json",
            validation_report_path=validation_report_path,
        )

    if args.command == "prescreen":
        document_path = Path(args.document).expanduser().resolve()
        prescreen_output_dir: Path | None = (
            Path(args.out).expanduser().resolve() if args.out else None
        )
        prescreen_result = run_prescreen(
            document_path=document_path, output_dir=prescreen_output_dir
        )
        print(prescreen_result.report_json)
        return 0

    if args.command == "consistency":
        target_path = Path(args.target).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        try:
            consistency_result = run_consistency_check(
                target_path=target_path, output_dir=explicit_out
            )
        except Exception as exc:
            print(f"consistency failed: {exc}")
            return 2

        if args.format == "json":
            print(consistency_result.report_json)
        else:
            print(consistency_result.report_text.rstrip())
            if consistency_result.report_path is not None:
                print(f"Consistency report generated at {consistency_result.report_path}")
            if consistency_result.summary_path is not None:
                print(f"Consistency summary generated at {consistency_result.summary_path}")

        return 0 if consistency_result.passed else 1

    if args.command == "validate-links":
        from mcp_server.link_validation import run_link_validation

        target = Path(args.target).expanduser().resolve()
        ws_root = Path(args.workspace_root).expanduser().resolve() if args.workspace_root else None
        out_dir = Path(args.out).expanduser().resolve() if args.out else None
        try:
            link_result = run_link_validation(
                target_path=target, workspace_root=ws_root, output_dir=out_dir
            )
        except Exception as exc:
            print(f"validate-links failed: {exc}")
            return 2

        if args.format == "json":
            print(link_result.report_json)
        else:
            print(link_result.report_text.rstrip())
            if link_result.report_path is not None:
                print(f"Link validation report generated at {link_result.report_path}")

        return 0 if link_result.passed else 1

    if args.command == "personas-show":
        from mcp_server.skills.persona_manager import show_persona_mappings

        result = show_persona_mappings(
            project_root=Path(args.project).expanduser().resolve(),
            phase=args.phase,
            doc_type=args.doc_type,
        )
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            _print_personas_table(result)
        return 0

    if args.command == "personas-set":
        from mcp_server.skills.persona_manager import set_persona_mapping

        result = set_persona_mapping(
            project_root=Path(args.project).expanduser().resolve(),
            phase=args.phase,
            doc_type=args.doc_type,
            personas=args.personas,
        )
        print(f"Updated {args.phase}.{args.doc_type}: {', '.join(args.personas)}")
        if result.get("previous_personas"):
            print(f"Previous: {', '.join(result['previous_personas'])}")
        return 0

    if args.command == "personas-diff":
        from mcp_server.skills.persona_manager import diff_persona_mappings

        result = diff_persona_mappings(
            project_root=Path(args.project).expanduser().resolve(),
        )
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            _print_diff_summary(result)
        return 0

    if args.command == "env-show":
        from mcp_server.env_manager import show_project_env

        result = show_project_env(
            project_root=Path(args.project).expanduser().resolve(),
        )
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Project: {result['project_root']}")
            print(f".env exists: {result['env_file_exists']}")
            if result["env_file_exists"]:
                print(f"Keys ({result['env_key_count']}): {', '.join(result['env_keys'])}")
                if result.get("blocked_vars"):
                    print(f"Blocked system vars: {', '.join(result['blocked_vars'])}")
                if result.get("api_keys_present"):
                    print(f"API keys present: {', '.join(result['api_keys_present'])}")
                if result.get("ucx_executor_overrides"):
                    print(
                        f"UCX executor overrides: {', '.join(result['ucx_executor_overrides'].keys())}"
                    )
                if result.get("parse_error"):
                    print("Warning: .env file has parse errors")
        return 0

    if args.command == "preflight":
        project_root = Path(args.project).expanduser().resolve()
        preflight_document = Path(args.document).expanduser().resolve() if args.document else None
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        try:
            preflight_result = run_preflight(
                project_root=project_root,
                context=args.context,
                document_path=preflight_document,
                output_dir=explicit_out,
            )
        except Exception as exc:
            print(f"preflight failed: {exc}")
            return 2

        if args.format == "json":
            print(preflight_result.report_json)
        else:
            print(preflight_result.report_text.rstrip())
            if preflight_result.report_path is not None:
                print(f"Preflight report generated at {preflight_result.report_path}")
            if preflight_result.summary_path is not None:
                print(f"Preflight summary generated at {preflight_result.summary_path}")

        return 1 if preflight_result.status == "blocked" else 0

    if args.command == "clean":
        document_path = Path(args.document).expanduser().resolve()
        apply_changes = bool(args.apply)
        dry_run = not apply_changes
        clean_result = run_clean(
            document_path=document_path,
            stages=args.stages,
            keep=max(0, int(args.keep)),
            dry_run=dry_run,
        )

        payload = {
            "dry_run": clean_result.dry_run,
            "deleted": clean_result.deleted,
            "deleted_count": len(clean_result.deleted),
            "kept": clean_result.kept,
            "kept_count": len(clean_result.kept),
            "bytes_freed": clean_result.total_bytes_freed,
        }

        out_dir = Path(args.out).expanduser().resolve() if args.out else None
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
            report_path = out_dir / "clean_report.json"
            report_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            print(f"Clean report generated at {report_path}")

        if dry_run:
            print(
                f"Dry run: {payload['deleted_count']} files would be deleted, {payload['kept_count']} kept"
            )
        else:
            print(f"Deleted: {payload['deleted_count']} files, kept {payload['kept_count']}")
            print(f"Bytes freed: {payload['bytes_freed']}")

        return 0

    if args.command == "scan":
        report_file = Path(args.report_file).expanduser().resolve()
        scan_output_dir: Path | None = Path(args.out).expanduser().resolve() if args.out else None
        scan_result = run_scan(report_file=report_file, output_dir=scan_output_dir)
        print(scan_result.report_json)
        return 0

    if args.command == "scoring":
        if args.scoring_command == "show":
            report_file = Path(args.report_file).expanduser().resolve()
            show_result = show_score(report_file=report_file)
            print(json.dumps(show_result.payload, sort_keys=True))
            return 0
        if args.scoring_command == "validate":
            report_file = Path(args.report_file).expanduser().resolve()
            validate_result = validate_score(report_file=report_file, threshold=int(args.threshold))
            print(json.dumps(validate_result.payload, sort_keys=True))
            return 0 if validate_result.passed else 1
        if args.scoring_command == "compare":
            baseline = Path(args.baseline_report_file).expanduser().resolve()
            candidate = Path(args.candidate_report_file).expanduser().resolve()
            compare_result = compare_scores(
                baseline_report_file=baseline, candidate_report_file=candidate
            )
            print(json.dumps(compare_result.payload, sort_keys=True))
            return 0
        print("scoring requires one of: show, validate, compare")
        return 2

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
