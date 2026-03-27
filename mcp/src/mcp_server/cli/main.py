from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil

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
from mcp_server.review import run_project_creation_artifact, run_project_creation_build, run_project_review_build
from mcp_server.scan import run_scan
from mcp_server.scoring import compare_scores, show_score, validate_score
from mcp_server.skills.scaffold import scaffold_project_ucx
from mcp_server.validation import run_project_validation_build


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcp")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Scaffold project-specific UCX assets")
    init_parser.add_argument("--project", required=True, help="Project root where docs/UCX will be created")

    review_parser = subparsers.add_parser("review-build", help="Assemble project review prompt and diagnostics artifacts")
    review_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    review_parser.add_argument("--persona", required=True, help="Persona file name without extension")
    review_parser.add_argument("--doc-type", required=True, help="Document type label for metadata")
    review_parser.add_argument("--template", required=True, help="Template file in docs/UCX/prompts/templates/review")
    review_parser.add_argument("--layer", default=None, help="Optional SSD layer directory name (e.g. 01_BRD)")
    review_parser.add_argument("--sections-json", required=True, help="Path to sections JSON array")
    review_parser.add_argument("--unified", action="store_true", help="Enable unified context mode")
    review_parser.add_argument("--one-turn", action="store_true", help="Enable one-turn review mode")
    review_parser.add_argument("--no-resume", action="store_true", help="Disable session resume")
    review_parser.add_argument("--session-ttl", type=int, default=0, help="Session TTL in seconds")
    review_parser.add_argument("--clean-memory", action="store_true", help="Clean review memory artifacts before execution")
    review_parser.add_argument("--clean-reports", action="store_true", help="Clean existing report artifacts in output directory")
    review_parser.add_argument("--keep-versions", type=int, default=0, help="Keep latest N existing report versions when cleaning")
    review_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/review",
    )

    review_alias_parser = subparsers.add_parser(
        "review",
        help="Alias for review-build (UCX_v1 compatibility)",
    )
    review_alias_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    review_alias_parser.add_argument("--persona", required=True, help="Persona file name without extension")
    review_alias_parser.add_argument("--doc-type", required=True, help="Document type label for metadata")
    review_alias_parser.add_argument("--template", required=True, help="Template file in docs/UCX/prompts/templates/review")
    review_alias_parser.add_argument("--layer", default=None, help="Optional SSD layer directory name (e.g. 01_BRD)")
    review_alias_parser.add_argument("--sections-json", required=True, help="Path to sections JSON array")
    review_alias_parser.add_argument("--unified", action="store_true", help="Enable unified context mode")
    review_alias_parser.add_argument("--one-turn", action="store_true", help="Enable one-turn review mode")
    review_alias_parser.add_argument("--no-resume", action="store_true", help="Disable session resume")
    review_alias_parser.add_argument("--session-ttl", type=int, default=0, help="Session TTL in seconds")
    review_alias_parser.add_argument("--clean-memory", action="store_true", help="Clean review memory artifacts before execution")
    review_alias_parser.add_argument("--clean-reports", action="store_true", help="Clean existing report artifacts in output directory")
    review_alias_parser.add_argument("--keep-versions", type=int, default=0, help="Keep latest N existing report versions when cleaning")
    review_alias_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/review",
    )

    create_parser = subparsers.add_parser("create-build", help="Assemble project creation prompt with SSD layer assets")
    create_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    create_parser.add_argument("--persona", required=True, help="Persona file name without extension")
    create_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    create_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    create_parser.add_argument("--template", required=True, help="Template file in docs/UCX/prompts/templates/creation")
    create_parser.add_argument("--sections-json", default=None, help="Optional path to sections JSON array")
    create_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/creation",
    )

    create_artifact_parser = subparsers.add_parser(
        "create",
        help="Create final document artifact at target path using project/layer templates",
    )
    create_artifact_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    create_artifact_parser.add_argument("--persona", required=True, help="Persona file name without extension")
    create_artifact_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    create_artifact_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    create_artifact_parser.add_argument("--template", required=True, help="Template file in docs/UCX/prompts/templates/creation")
    create_artifact_parser.add_argument("--target", required=True, help="Final target document path to create")
    create_artifact_parser.add_argument("--sections-json", default=None, help="Optional path to sections JSON array")
    create_artifact_parser.add_argument("--overwrite", action="store_true", help="Overwrite target document if it exists")
    create_artifact_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory for creation prompt diagnostics",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Run script-based document structure validation against layer template/schema assets",
    )
    validate_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    validate_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    validate_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    validate_parser.add_argument("--document", required=True, help="Path to document file or document directory")
    validate_parser.add_argument("--tier1-only", action="store_true", help="Evaluate only tier1 checks")
    validate_parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    validate_parser.add_argument("--format", choices=["text", "json"], default="text", help="Validation output format")
    validate_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/validate",
    )

    remediate_parser = subparsers.add_parser(
        "remediate",
        help="Generate deterministic remediation findings and report artifacts",
    )
    remediate_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    remediate_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    remediate_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    remediate_parser.add_argument("--document", required=True, help="Path to document file or document directory")
    remediate_parser.add_argument(
        "--review-report",
        default=None,
        help="Optional path to review report consumed by remediation",
    )
    remediate_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/remediation",
    )

    remediate_fix_parser = subparsers.add_parser(
        "remediate-fix",
        help="Generate source-protected remediated derived artifacts",
    )
    remediate_fix_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    remediate_fix_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    remediate_fix_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    remediate_fix_parser.add_argument("--document", required=True, help="Path to document file or document directory")
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
        help="Generate source-protected validation derived artifacts",
    )
    validate_fix_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    validate_fix_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    validate_fix_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    validate_fix_parser.add_argument("--document", required=True, help="Path to document file or document directory")
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

    prescreen_parser = subparsers.add_parser("prescreen", help="Prescreen documents for deterministic remediation candidates")
    prescreen_parser.add_argument("--document", required=True, help="Path to document file or document directory")
    prescreen_parser.add_argument("--out", default=None, help="Optional output directory for prescreen artifacts")

    scan_parser = subparsers.add_parser("scan", help="Scan validation or remediation reports for finding category metrics")
    scan_parser.add_argument("--report-file", required=True, help="Path to JSON report file to scan")
    scan_parser.add_argument("--out", default=None, help="Optional output directory for scan artifacts")

    scoring_parser = subparsers.add_parser("scoring", help="Score report quality metrics")
    scoring_subparsers = scoring_parser.add_subparsers(dest="scoring_command")

    scoring_show_parser = scoring_subparsers.add_parser("show", help="Show score for a report")
    scoring_show_parser.add_argument("--report-file", required=True, help="Path to JSON report file")

    scoring_validate_parser = scoring_subparsers.add_parser("validate", help="Validate score threshold for a report")
    scoring_validate_parser.add_argument("--report-file", required=True, help="Path to JSON report file")
    scoring_validate_parser.add_argument("--threshold", type=int, required=True, help="Minimum required score")

    scoring_compare_parser = scoring_subparsers.add_parser("compare", help="Compare scores between baseline and candidate reports")
    scoring_compare_parser.add_argument("--baseline-report-file", required=True, help="Path to baseline JSON report")
    scoring_compare_parser.add_argument("--candidate-report-file", required=True, help="Path to candidate JSON report")

    consistency_parser = subparsers.add_parser(
        "consistency",
        help="Run lightweight artifact lineage and stage consistency checks",
    )
    consistency_parser.add_argument("--target", required=True, help="Path to source document file or document directory")
    consistency_parser.add_argument("--format", choices=["text", "json"], default="text", help="Consistency output format")
    consistency_parser.add_argument("--out", default=None, help="Optional output directory for consistency artifacts")

    preflight_parser = subparsers.add_parser(
        "preflight",
        help="Run runtime and environment readiness checks before create, review, or remediation stages",
    )
    preflight_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    preflight_parser.add_argument(
        "--context",
        choices=["create", "review", "remediate", "any"],
        default="any",
        help="Operational context for required readiness checks",
    )
    preflight_parser.add_argument("--document", default=None, help="Optional document path to verify")
    preflight_parser.add_argument("--format", choices=["text", "json"], default="text", help="Preflight output format")
    preflight_parser.add_argument("--out", default=None, help="Optional output directory for preflight artifacts")

    return parser


def _write_review_controls_artifact(output_dir: Path, args: argparse.Namespace) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    controls_path = output_dir / "review_controls.json"
    controls_payload = {
        "unified": bool(args.unified),
        "one_turn": bool(args.one_turn),
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


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        project_root = Path(args.project).expanduser().resolve()
        init_result = scaffold_project_ucx(project_root=project_root)
        print(f"Initialized project UCX scaffold at {init_result.project_root}")
        print(f"Created: {init_result.created_count}")
        print(f"Skipped existing: {init_result.skipped_count}")
        return 0

    if args.command in {"review-build", "review"}:
        project_root = Path(args.project).expanduser().resolve()
        sections_json = Path(args.sections_json).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REVIEW,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=sections_json.parent,
        )
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

        if args.clean_memory:
            review_memory_dir = project_root / "tmp/review_memory"
            if review_memory_dir.exists():
                shutil.rmtree(review_memory_dir)

        if args.clean_reports and output_dir.exists():
            keep_versions = max(0, int(args.keep_versions))
            candidates = sorted(output_dir.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
            for path in candidates[keep_versions:]:
                if path.is_file():
                    path.unlink()

        review_result = run_project_review_build(
            project_root=project_root,
            persona=args.persona,
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
        print(f"Review controls artifact generated at {controls_path}")
        if review_result.layer_asset_names:
            print(f"Layer assets included: {review_result.layer_asset_names}")
        print(
            "Review controls: "
            f"unified={args.unified}, one_turn={args.one_turn}, no_resume={args.no_resume}, "
            f"session_ttl={args.session_ttl}, clean_memory={args.clean_memory}, clean_reports={args.clean_reports}, "
            f"keep_versions={args.keep_versions}"
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
            persona=args.persona,
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
                persona=args.persona,
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

        validation_result = run_project_validation_build(
            project_root=project_root,
            doc_type=args.doc_type,
            layer=args.layer,
            document_path=document_path,
            output_dir=output_dir,
        )
        payload = validation_result.report
        errors = payload.get("errors", []) if isinstance(payload, dict) else []
        warnings = payload.get("warnings", []) if isinstance(payload, dict) else []

        if not isinstance(errors, list):
            errors = []
        if not isinstance(warnings, list):
            warnings = []

        if args.tier1_only:
            tier1_errors = [
                item
                for item in errors
                if isinstance(item, str)
                and (
                    item.startswith("Missing required custom field")
                    or item.startswith("Missing required tag")
                )
            ]
            effective_errors = tier1_errors
        else:
            effective_errors = [item for item in errors if isinstance(item, str)]

        effective_warnings = [item for item in warnings if isinstance(item, str)]
        failed = len(effective_errors) > 0 or (args.strict and len(effective_warnings) > 0)

        response_payload = {
            "report_path": str(validation_result.report_path) if validation_result.report_path else None,
            "summary_path": str(validation_result.summary_path) if validation_result.summary_path else None,
            "tier1_only": bool(args.tier1_only),
            "strict": bool(args.strict),
            "errors": effective_errors,
            "warnings": effective_warnings,
            "passed": not failed,
        }

        if args.format == "json":
            print(json.dumps(response_payload, sort_keys=True))
        else:
            print(f"Validation report generated at {validation_result.report_path}")
            print(f"Validation summary generated at {validation_result.summary_path}")
            print(f"Tier1-only mode: {args.tier1_only}")
            print(f"Strict mode: {args.strict}")
            print("Validation status: PASSED" if not failed else "Validation status: FAILED")

        return 0 if not failed else 1

    if args.command == "remediate":
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        review_report = Path(args.review_report).expanduser().resolve() if args.review_report else None
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_REMEDIATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
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
        return 0

    if args.command == "remediate-fix":
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        remediation_report = Path(args.remediation_report).expanduser().resolve() if args.remediation_report else None
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
        project_root = Path(args.project).expanduser().resolve()
        document_path = Path(args.document).expanduser().resolve()
        validation_report = Path(args.validation_report).expanduser().resolve() if args.validation_report else None
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        output_dir = resolve_stage_output_dir(
            stage=STAGE_VALIDATE,
            project_root=project_root,
            output_dir=explicit_out,
            document_dir=document_path if document_path.is_dir() else document_path.parent,
        )
        try:
            validate_fix_result = run_validate_fix_build(
                project_root=project_root,
                doc_type=args.doc_type,
                layer=args.layer,
                document_path=document_path,
                validation_report=validation_report,
                output_dir=output_dir,
            )
        except (FileNotFoundError, ValueError) as exc:
            print(f"validate-fix failed: {exc}")
            return 1
        print(f"Validate-fix report generated at {validate_fix_result.report_path}")
        print(f"Validate-fix summary generated at {validate_fix_result.summary_path}")
        print(f"Derived artifacts created: {len(validate_fix_result.derived_paths)}")
        return 0

    if args.command == "prescreen":
        document_path = Path(args.document).expanduser().resolve()
        prescreen_output_dir: Path | None = Path(args.out).expanduser().resolve() if args.out else None
        prescreen_result = run_prescreen(document_path=document_path, output_dir=prescreen_output_dir)
        print(prescreen_result.report_json)
        return 0

    if args.command == "consistency":
        target_path = Path(args.target).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        try:
            consistency_result = run_consistency_check(target_path=target_path, output_dir=explicit_out)
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
            compare_result = compare_scores(baseline_report_file=baseline, candidate_report_file=candidate)
            print(json.dumps(compare_result.payload, sort_keys=True))
            return 0
        print("scoring requires one of: show, validate, compare")
        return 2

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
