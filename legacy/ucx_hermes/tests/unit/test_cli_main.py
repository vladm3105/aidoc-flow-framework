from __future__ import annotations

import json
from pathlib import Path
import sys
from importlib import import_module


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.cli.main import main  # noqa: E402


def test_main_init_command_scaffolds_project(tmp_path: Path) -> None:
    exit_code = main(["init", "--project", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / "UCX/skills/personas/architect.md").exists()
    assert (tmp_path / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").exists()


def test_main_init_update_mappings_requires_update(tmp_path: Path, capsys) -> None:
    exit_code = main(["init", "--project", str(tmp_path), "--update-mappings"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "requires --update" in captured.out


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
            "--personas",
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


def test_main_review_build_controls_capture_branch_llm_flag(tmp_path: Path) -> None:
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

    out_dir = tmp_path / "tmp/evidence-controls"
    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--personas",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--sections-json",
            str(sections_file),
            "--review-mode",
            "saga_parallel",
            "--saga-branch-llm-enabled",
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    controls = json.loads((out_dir / "review_controls.json").read_text(encoding="utf-8"))
    assert controls.get("review_mode") == "saga_parallel"
    assert controls.get("saga_branch_llm_enabled") is True


def test_main_review_build_with_layer_includes_layer_assets(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])
    layer_root = tmp_path / "UCX/templates/layers/01_BRD"
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
            "--personas",
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


def test_main_review_build_without_out_uses_document_dir(tmp_path: Path) -> None:
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
            "--personas",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--sections-json",
            str(sections_file),
        ]
    )

    default_out = sections_dir / ".ucx" / "review"
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
            "--personas",
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


def test_main_review_build_document_auto_loads_main_and_appendices(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    document_dir = tmp_path / "docs/01_BRD/BRD-01_platform_architecture"
    document_dir.mkdir(parents=True, exist_ok=True)

    main_doc = document_dir / "BRD-01_platform_architecture.md"
    main_doc.write_text("# Main\n\n## 1. Intro\n", encoding="utf-8")

    appendix_doc = document_dir / "BRD-01_appendices.md"
    appendix_doc.write_text("# Appendices\n\n## A. Extra\n", encoding="utf-8")

    (document_dir / "BRD-01.md").write_text("# Index\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/evidence-document"
    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--personas",
            "architect",
            "--doc-type",
            "brd",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--document",
            str(document_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "review_prompt.txt").exists()
    sidecar = json.loads((out_dir / "review_prompt_sidecar.json").read_text(encoding="utf-8"))
    sections = sidecar.get("sections", {})
    included = sections.get("included", []) if isinstance(sections, dict) else []
    skipped = sections.get("skipped", []) if isinstance(sections, dict) else []
    merged_ids = set(included + skipped)
    assert "BRD-01_platform_architecture" in merged_ids
    assert "BRD-01_appendices" in merged_ids


def test_main_review_build_document_auto_loads_main_and_appendices_across_layers(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    document_dir = tmp_path / "docs/06_SYS/SYS-07_runtime_architecture"
    document_dir.mkdir(parents=True, exist_ok=True)

    main_doc = document_dir / "SYS-07_runtime_architecture.md"
    main_doc.write_text("# Main\n\n## 1. Intro\n", encoding="utf-8")

    appendix_doc = document_dir / "SYS-07_appendices.md"
    appendix_doc.write_text("# Appendices\n\n## A. Extra\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/evidence-document-sys"
    exit_code = main(
        [
            "review-build",
            "--project",
            str(tmp_path),
            "--personas",
            "architect",
            "--doc-type",
            "sys",
            "--template",
            "UCR_PROMPT_BRD_PROJECT.md",
            "--document",
            str(document_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    sidecar = json.loads((out_dir / "review_prompt_sidecar.json").read_text(encoding="utf-8"))
    sections = sidecar.get("sections", {})
    included = sections.get("included", []) if isinstance(sections, dict) else []
    skipped = sections.get("skipped", []) if isinstance(sections, dict) else []
    merged_ids = set(included + skipped)
    assert "SYS-07_runtime_architecture" in merged_ids
    assert "SYS-07_appendices" in merged_ids


def test_main_validate_without_out_uses_document_dir(tmp_path: Path) -> None:
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
            "validate",
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

    default_out = doc_dir / ".ucx" / "validate"
    assert exit_code == 0
    assert (default_out / "BRD-01.ucx.validate.json").exists()
    assert (default_out / "BRD-01.ucx.validate.txt").exists()
    # Passing document should NOT produce fix artifacts
    assert not (default_out / "BRD-01.ucx.validate_fix.json").exists()
    assert not any(default_out.glob("*_validated.*"))


def test_main_validate_failing_doc_produces_fix_artifacts(tmp_path: Path) -> None:
    """When validation fails, the merged validate command also produces fix artifacts."""
    main(["init", "--project", str(tmp_path)])

    doc_dir = tmp_path / "docs/01_BRD/BRD-01_sample"
    doc_dir.mkdir(parents=True, exist_ok=True)
    doc_file = doc_dir / "BRD-01_sample.md"
    doc_file.write_text(
        "# BRD-01: Sample\nTODO refine content\n",
        encoding="utf-8",
    )

    exit_code = main(
        [
            "validate",
            "--project",
            str(tmp_path),
            "--doc-type",
            "brd",
            "--layer",
            "01_BRD",
            "--document",
            str(doc_file),
            "--format",
            "json",
        ]
    )

    validate_out = doc_dir / ".ucx" / "validate"
    assert exit_code == 1  # Validation failed
    assert (validate_out / "BRD-01.ucx.validate.json").exists()
    assert (validate_out / "BRD-01.ucx.validate_fix.json").exists()
    assert any(validate_out.glob("*_validated.*"))


def test_main_consistency_pass_with_complete_artifact_chain(tmp_path: Path) -> None:
    doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform_architecture"
    doc_dir.mkdir(parents=True, exist_ok=True)

    source = doc_dir / "BRD-01_platform_architecture.md"
    source.write_text("# source\n", encoding="utf-8")
    (doc_dir / "BRD-01.ucx.validate.json").write_text("{}", encoding="utf-8")
    (doc_dir / "BRD-01_platform_architecture_validated.md").write_text("# validation copy\n", encoding="utf-8")
    (doc_dir / "BRD-01_platform_architecture_remediate_v1.md").write_text("# remediated v1\n", encoding="utf-8")
    (doc_dir / "BRD-01_validation_remediation_report_v1.md").write_text("# remediation report\n", encoding="utf-8")

    out_dir = tmp_path / "tmp/consistency"
    exit_code = main(
        [
            "consistency",
            "--target",
            str(doc_dir),
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "BRD-01.ucx.consistency.json").exists()
    assert (out_dir / "BRD-01.ucx.consistency.txt").exists()


def test_main_consistency_fails_without_source_artifact(tmp_path: Path) -> None:
    doc_dir = tmp_path / "docs/01_BRD/BRD-01_platform_architecture"
    doc_dir.mkdir(parents=True, exist_ok=True)

    exit_code = main(["consistency", "--target", str(doc_dir), "--format", "json"])
    assert exit_code == 1


def test_main_preflight_ready_for_initialized_project(tmp_path: Path) -> None:
    main(["init", "--project", str(tmp_path)])

    out_dir = tmp_path / "tmp/preflight"
    exit_code = main(
        [
            "preflight",
            "--project",
            str(tmp_path),
            "--context",
            "any",
            "--out",
            str(out_dir),
        ]
    )

    assert exit_code == 0
    assert (out_dir / "preflight_report.json").exists()
    assert (out_dir / "preflight_report.txt").exists()


def test_main_preflight_blocked_for_missing_ucx_root(tmp_path: Path) -> None:
    exit_code = main(["preflight", "--project", str(tmp_path), "--context", "any", "--format", "json"])
    assert exit_code == 1


def test_main_consistency_runtime_error_returns_2(tmp_path: Path, monkeypatch) -> None:
    def _boom(*, target_path, output_dir=None):  # type: ignore[no-untyped-def]
        raise RuntimeError("synthetic consistency failure")

    cli_main_module = import_module("mcp_server.cli.main")
    monkeypatch.setattr(cli_main_module, "run_consistency_check", _boom)
    exit_code = main(["consistency", "--target", str(tmp_path), "--format", "json"])
    assert exit_code == 2


def test_main_preflight_runtime_error_returns_2(tmp_path: Path, monkeypatch) -> None:
    def _boom(*, project_root, context, document_path=None, output_dir=None):  # type: ignore[no-untyped-def]
        raise RuntimeError("synthetic preflight failure")

    cli_main_module = import_module("mcp_server.cli.main")
    monkeypatch.setattr(cli_main_module, "run_preflight", _boom)
    exit_code = main(["preflight", "--project", str(tmp_path), "--context", "any", "--format", "json"])
    assert exit_code == 2
