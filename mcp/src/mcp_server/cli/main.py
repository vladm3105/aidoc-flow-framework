from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp_server.core.stage_output import (
    STAGE_CREATE,
    STAGE_REVIEW,
    STAGE_VALIDATE,
    resolve_stage_output_dir,
)
from mcp_server.prompts import SourceSection
from mcp_server.review import run_project_creation_build, run_project_review_build
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

    validate_parser = subparsers.add_parser(
        "validate-build",
        help="Run script-based document structure validation against layer template/schema assets",
    )
    validate_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    validate_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    validate_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    validate_parser.add_argument("--document", required=True, help="Path to document file or document directory")
    validate_parser.add_argument(
        "--out",
        default=None,
        help="Optional output directory; defaults to <document_dir>/.ucx/validate",
    )

    remediate_parser = subparsers.add_parser(
        "remediate",
        help="Reserved remediation command contract (UCX_v1 compatibility; not implemented)",
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
        help="Reserved remediation apply command contract (UCX_v1 compatibility; not implemented)",
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
        help="Reserved validation-fix command contract (UCX_v1 compatibility; not implemented)",
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

    return parser


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

        review_result = run_project_review_build(
            project_root=project_root,
            persona=args.persona,
            doc_type=args.doc_type,
            template_name=args.template,
            sections=review_sections,
            layer=args.layer,
            output_dir=output_dir,
        )
        print(f"Review prompt generated at {review_result.prompt_path}")
        print(f"Sidecar generated at {review_result.sidecar_path}")
        print(f"Inspection generated at {review_result.inspection_path}")
        if review_result.layer_asset_names:
            print(f"Layer assets included: {review_result.layer_asset_names}")
        return 0

    if args.command == "create-build":
        project_root = Path(args.project).expanduser().resolve()
        explicit_out = Path(args.out).expanduser().resolve() if args.out else None
        creation_sections: list[SourceSection] | None = None
        sections_path: Path | None = None
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

    if args.command == "validate-build":
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
        print(f"Validation report generated at {validation_result.report_path}")
        print(f"Validation summary generated at {validation_result.summary_path}")
        if validation_result.is_valid:
            print("Validation status: PASSED")
            return 0

        print("Validation status: FAILED")
        return 1

    if args.command == "remediate":
        print("Command 'remediate' is defined for UCX_v1 compatibility but is not implemented in MCP yet.")
        print("Use review-build (or review alias) for prompt generation and validate-build for script checks.")
        return 2

    if args.command == "remediate-fix":
        print("Command 'remediate-fix' is defined for UCX_v1 compatibility but is not implemented in MCP yet.")
        print("Use review-build (or review alias) for prompt generation and validate-build for script checks.")
        return 2

    if args.command == "validate-fix":
        print("Command 'validate-fix' is defined for UCX_v1 compatibility but is not implemented in MCP yet.")
        print("Use validate-build for script-based validation output.")
        return 2

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
