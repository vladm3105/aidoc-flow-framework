from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def test_main_init_command_scaffolds_project(tmp_path: Path) -> None:
    exit_code = main(["init", "--project", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "docs/UCX/skills/personas/architect.md").exists()
    assert (tmp_path / "docs/UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").exists()


def test_main_without_command_returns_usage_error() -> None:
    exit_code = main([])
    assert exit_code == 2


def test_main_review_build_generates_output_artifacts(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    sections_file = tmp_path / "sections.json"
    sections_file.write_text(
        json.dumps(
            [
                {
                    "section_id": "1.0",
                    "title": "Architecture",
                    "content": "system architecture and integration dependencies",
                },
                {
                    "section_id": "9.0",
                    "title": "Appendix",
                    "content": "reference metadata appendix",
                },
            ]
        ),
        encoding="utf-8",
    )

    out_dir = tmp_path / "tmp/evidence"
    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--persona",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--sections-json",
            str(sections_file),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "review_prompt.txt").exists()
    assert (out_dir / "review_prompt_sidecar.json").exists()
    assert (out_dir / "review_prompt_inspection.json").exists()
    assert (out_dir / "review_controls.json").exists()


def test_main_review_build_with_layer_includes_layer_assets(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    layer_root = tmp_path / "docs/UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "BRD-MVP-TEMPLATE.md").write_text("BRD template layer asset", encoding="utf-8")
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")

    sections_file = tmp_path / "sections.json"
    sections_file.write_text(
        json.dumps(
            [
                {
                    "section_id": "1.0",
                    "title": "Architecture",
                    "content": "system architecture and integration dependencies",
                },
                {
                    "section_id": "9.0",
                    "title": "Appendix",
                    "content": "reference metadata appendix",
                },
            ]
        ),
        encoding="utf-8",
    )

    out_dir = tmp_path / "tmp/evidence-layer"
    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--persona",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--layer",
            "01_BRD",
            "--sections-json",
            str(sections_file),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    prompt = (out_dir / "review_prompt.txt").read_text(encoding="utf-8")
    assert "MCP Actionable Review Rules" in prompt
    assert "BRD_MVP_SCHEMA.yaml" in prompt


def test_main_review_build_without_out_uses_document_stage_dir(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    sections_dir = tmp_path / "docs/01_BRD/BRD-01_platform_architecture"
    sections_dir.mkdir(parents=True, exist_ok=True)
    sections_file = sections_dir / "sections.json"
    sections_file.write_text(
        json.dumps(
            [
                {
                    "section_id": "1.0",
                    "title": "Architecture",
                    "content": "system architecture and integration dependencies",
                }
            ]
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--persona",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--sections-json",
            str(sections_file),
        ]
    )

    default_out = sections_dir / ".ucx/review"
    assert exit_code == 0
    assert (default_out / "review_prompt.txt").exists()


def test_main_review_build_out_ucx_root_appends_stage(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    sections_file = tmp_path / "sections.json"
    sections_file.write_text(
        json.dumps(
            [
                {
                    "section_id": "1.0",
                    "title": "Architecture",
                    "content": "system architecture and integration dependencies",
                }
            ]
        ),
        encoding="utf-8",
    )

    ucx_root = tmp_path / "docs/01_BRD/BRD-01_platform_architecture/.ucx"
    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--persona",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--sections-json",
            str(sections_file),
            "--out",
            str(ucx_root),
        ]
    )

    assert exit_code == 0
    assert (ucx_root / "review/review_prompt.txt").exists()


def test_main_validate_build_without_out_uses_document_stage_dir(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform_architecture"
    doc_dir.mkdir(parents=True, exist_ok=True)
    doc_file = doc_dir / "BRD-01_platform_architecture.md"
    doc_file.write_text(
        """---
title: "Sample"
tags: [brd]
custom_fields:
  document_type: brd
  artifact_type: BRD
  layer: 1
  architecture_approaches: [ai-agent-based]
  priority: shared
  status: draft
---

# BRD-01: Sample
""",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "validate-build",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(doc_file),
        ]
    )

    default_out = doc_dir / ".ucx/validate"
    assert exit_code == 1
    assert (default_out / "validation_report.json").exists()
    assert (default_out / "validation_report.txt").exists()
