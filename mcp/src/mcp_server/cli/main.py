from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp_server.prompts import SourceSection
from mcp_server.review import run_project_creation_build, run_project_review_build
from mcp_server.skills.scaffold import scaffold_project_ucx


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
    review_parser.add_argument("--out", required=True, help="Output directory for generated artifacts")

    create_parser = subparsers.add_parser("create-build", help="Assemble project creation prompt with SSD layer assets")
    create_parser.add_argument("--project", required=True, help="Project root containing docs/UCX")
    create_parser.add_argument("--persona", required=True, help="Persona file name without extension")
    create_parser.add_argument("--doc-type", required=True, help="Document type label (e.g. brd, prd)")
    create_parser.add_argument("--layer", required=True, help="SSD layer directory name (e.g. 01_BRD)")
    create_parser.add_argument("--template", required=True, help="Template file in docs/UCX/prompts/templates/creation")
    create_parser.add_argument("--sections-json", default=None, help="Optional path to sections JSON array")
    create_parser.add_argument("--out", required=True, help="Output directory for generated artifacts")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "init":
        project_root = Path(args.project).expanduser().resolve()
        result = scaffold_project_ucx(project_root=project_root)
        print(f"Initialized project UCX scaffold at {result.project_root}")
        print(f"Created: {result.created_count}")
        print(f"Skipped existing: {result.skipped_count}")
        return 0

    if args.command == "review-build":
        project_root = Path(args.project).expanduser().resolve()
        output_dir = Path(args.out).expanduser().resolve()
        sections_json = Path(args.sections_json).expanduser().resolve()
        payload = json.loads(sections_json.read_text(encoding="utf-8"))
        sections = [
            SourceSection(
                section_id=item["section_id"],
                title=item["title"],
                content=item["content"],
                included=item.get("included", True),
            )
            for item in payload
        ]

        result = run_project_review_build(
            project_root=project_root,
            persona=args.persona,
            doc_type=args.doc_type,
            template_name=args.template,
            sections=sections,
            layer=args.layer,
            output_dir=output_dir,
        )
        print(f"Review prompt generated at {result.prompt_path}")
        print(f"Sidecar generated at {result.sidecar_path}")
        print(f"Inspection generated at {result.inspection_path}")
        if result.layer_asset_names:
            print(f"Layer assets included: {result.layer_asset_names}")
        return 0

    if args.command == "create-build":
        project_root = Path(args.project).expanduser().resolve()
        output_dir = Path(args.out).expanduser().resolve()
        sections = None
        if args.sections_json:
            sections_path = Path(args.sections_json).expanduser().resolve()
            payload = json.loads(sections_path.read_text(encoding="utf-8"))
            sections = [
                SourceSection(
                    section_id=item["section_id"],
                    title=item["title"],
                    content=item["content"],
                    included=item.get("included", True),
                )
                for item in payload
            ]

        result = run_project_creation_build(
            project_root=project_root,
            persona=args.persona,
            doc_type=args.doc_type,
            layer=args.layer,
            template_name=args.template,
            sections=sections,
            output_dir=output_dir,
        )
        print(f"Creation prompt generated at {result.prompt_path}")
        print(f"Layer assets included: {result.layer_asset_names}")
        return 0

    else:
        parser.print_help()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
