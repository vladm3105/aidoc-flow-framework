from __future__ import annotations

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.prompts import (  # noqa: E402
    CreationAssembly,
    SourceSection,
    assemble_project_creation_prompt,
)
from mcp_server.review import CreationRunResult, run_project_creation_build  # noqa: E402
from mcp_server.cli.main import main  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scaffold_creation_fixtures(project_root: Path, layer: str = "01_BRD") -> None:
    """Create minimal project UCX layout with creation assets."""
    for relative in [
        Path("docs/UCX/skills/personas"),
        Path("docs/UCX/skills/layer_aliases"),
        Path("docs/UCX/prompts/templates/creation"),
        Path("docs/UCX/prompts/templates/review"),
        Path("docs/UCX/prompts/templates/remediation"),
        Path("docs/UCX/templates"),
        Path(f"docs/UCX/templates/layers/{layer}"),
    ]:
        (project_root / relative).mkdir(parents=True, exist_ok=True)

    # Persona
    (project_root / "docs/UCX/skills/personas/architect.md").write_text(
        "Architect domain knowledge and system design principles.", encoding="utf-8"
    )

    # Creation prompt template
    (project_root / "docs/UCX/prompts/templates/creation/UCC_PROMPT_BRD_PROJECT.md").write_text(
        "Creation template instructions for BRD generation.", encoding="utf-8"
    )

    # Authoritative SSD layer assets (MVP template + schema)
    (project_root / f"docs/UCX/templates/layers/{layer}/BRD-MVP-TEMPLATE.md").write_text(
        "# BRD MVP TEMPLATE\nSDD authoritative template structure.", encoding="utf-8"
    )
    (project_root / f"docs/UCX/templates/layers/{layer}/BRD_MVP_SCHEMA.yaml").write_text(
        "schema_version: '1.0'\nrequired_sections: [0, 1, 2]\n", encoding="utf-8"
    )

    # Project-tuned document template (optional but present here)
    (project_root / "docs/UCX/templates/BRD-MVP-TEMPLATE.md").write_text(
        "# Project-Tuned BRD Template\nProject-specific overrides applied.", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Unit-level: assemble_project_creation_prompt
# ---------------------------------------------------------------------------

def test_assemble_project_creation_prompt_includes_persona(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert "Architect domain knowledge" in assembly.prompt_text
    assert assembly.persona_text.strip() == "Architect domain knowledge and system design principles."


def test_assemble_project_creation_prompt_includes_creation_template(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert "Creation template instructions for BRD generation" in assembly.prompt_text
    assert "Creation template instructions" in assembly.prompt_template_text


def test_assemble_project_creation_prompt_includes_layer_schema(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert "Authoritative Layer Assets" in assembly.prompt_text
    assert "BRD_MVP_SCHEMA.yaml" in assembly.layer_assets
    assert "required_sections" in assembly.layer_assets["BRD_MVP_SCHEMA.yaml"]


def test_assemble_project_creation_prompt_includes_layer_mvp_template(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert "BRD-MVP-TEMPLATE.md" in assembly.layer_assets
    assert "SDD authoritative template structure" in assembly.layer_assets["BRD-MVP-TEMPLATE.md"]


def test_assemble_project_creation_prompt_includes_project_tuned_template(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert assembly.document_template_text is not None
    assert "Project-Tuned BRD Template" in assembly.document_template_text
    assert "Project-Tuned Template" in assembly.prompt_text


def test_assemble_project_creation_prompt_layer_asset_names_sorted(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    names = sorted(assembly.layer_assets.keys())
    assert "BRD-MVP-TEMPLATE.md" in names
    assert "BRD_MVP_SCHEMA.yaml" in names


def test_assemble_project_creation_prompt_includes_mcp_internal_actionable_rules(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert "MCP Actionable Creation Rules" in assembly.prompt_text
    assert "Do not rely on deprecated `*_MVP_CREATION_RULES.md`" in assembly.prompt_text


def test_assemble_project_creation_prompt_tolerates_missing_project_template(tmp_path: Path) -> None:
    """document_template_text is None when the project-tuned template does not exist."""
    _scaffold_creation_fixtures(tmp_path)
    (tmp_path / "docs/UCX/templates/BRD-MVP-TEMPLATE.md").unlink()

    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert assembly.document_template_text is None
    assert "Project-Tuned Template" not in assembly.prompt_text


def test_assemble_project_creation_prompt_bundle_metadata(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert assembly.bundle.metadata.persona == "architect"
    assert assembly.bundle.metadata.doc_type == "brd"


def test_assemble_project_creation_prompt_with_sections(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    sections = [
        SourceSection(section_id="1.0", title="Business Context", content="functional business workflow"),
        SourceSection(section_id="9.0", title="Glossary", content="reference appendix metadata"),
    ]
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
        sections=sections,
    )
    assert assembly.bundle.metadata.sections_included is not None


def test_assemble_project_creation_prompt_returns_frozen_dataclass(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    assembly = assemble_project_creation_prompt(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )
    assert isinstance(assembly, CreationAssembly)
    try:
        assembly.prompt_text = "mutated"  # type: ignore[misc]
        raise AssertionError("Expected frozen dataclass to raise AttributeError on mutation")
    except (AttributeError, TypeError):
        pass  # frozen dataclass correctly prevents mutation


# ---------------------------------------------------------------------------
# Runner: run_project_creation_build
# ---------------------------------------------------------------------------

def test_run_project_creation_build_writes_artifacts(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    output_dir = tmp_path / "output"

    result = run_project_creation_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
        output_dir=output_dir,
    )

    assert result.prompt_path is not None and result.prompt_path.exists()
    assert result.sidecar_path is not None and result.sidecar_path.exists()
    assert result.inspection_path is not None and result.inspection_path.exists()


def test_run_project_creation_build_prompt_content(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    result = run_project_creation_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )

    assert "Architect domain knowledge" in result.prompt_text
    assert "BRD_MVP_SCHEMA.yaml" in result.prompt_text
    assert "Project-Tuned BRD Template" in result.prompt_text


def test_run_project_creation_build_layer_asset_names(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    result = run_project_creation_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )

    assert "BRD-MVP-TEMPLATE.md" in result.layer_asset_names
    assert "BRD_MVP_SCHEMA.yaml" in result.layer_asset_names


def test_run_project_creation_build_sidecar_is_valid_json(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    result = run_project_creation_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )

    parsed = json.loads(result.sidecar_json)
    assert parsed.get("persona") == "architect"
    assert parsed.get("doc_type") == "brd"


def test_run_project_creation_build_returns_document_template(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    result = run_project_creation_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
    )

    assert result.document_template_text is not None
    assert "Project-Tuned BRD Template" in result.document_template_text


def test_run_project_creation_build_no_output_dir_leaves_no_files(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    result = run_project_creation_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        layer="01_BRD",
        template_name="UCC_PROMPT_BRD_PROJECT.md",
        output_dir=None,
    )

    assert result.prompt_path is None
    assert result.sidecar_path is None
    assert result.inspection_path is None


# ---------------------------------------------------------------------------
# CLI: create-build end-to-end
# ---------------------------------------------------------------------------

def test_cli_create_build_exit_zero(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    output_dir = tmp_path / "cli_output"

    rc = main([
        "create-build",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--out", str(output_dir),
    ])

    assert rc == 0


def test_cli_create_build_writes_prompt_file(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    output_dir = tmp_path / "cli_output"

    main([
        "create-build",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--out", str(output_dir),
    ])

    prompt_file = output_dir / "creation_prompt.txt"
    assert prompt_file.exists()
    content = prompt_file.read_text(encoding="utf-8")
    assert "Architect domain knowledge" in content
    assert "BRD_MVP_SCHEMA.yaml" in content


def test_cli_create_build_writes_sidecar_json(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    output_dir = tmp_path / "cli_output"

    main([
        "create-build",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--out", str(output_dir),
    ])

    sidecar_file = output_dir / "creation_prompt_sidecar.json"
    assert sidecar_file.exists()
    parsed = json.loads(sidecar_file.read_text(encoding="utf-8"))
    assert parsed.get("persona") == "architect"


def test_cli_create_build_without_out_uses_document_dir(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    sections_dir = tmp_path / "docs/01_BRD/BRD-01_platform_architecture"
    sections_dir.mkdir(parents=True, exist_ok=True)
    sections_path = sections_dir / "sections.json"
    sections_path.write_text(
        json.dumps(
            [
                {
                    "section_id": "1.0",
                    "title": "Business Context",
                    "content": "functional business workflow",
                }
            ]
        ),
        encoding="utf-8",
    )

    rc = main([
        "create-build",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--sections-json", str(sections_path),
    ])

    default_out = sections_dir
    assert rc == 0
    assert (default_out / "creation_prompt.txt").exists()
    assert (default_out / "creation_prompt_sidecar.json").exists()


def test_cli_create_writes_final_target_artifact(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    target = tmp_path / "docs/01_BRD/BRD-01_platform_architecture/BRD-01_platform_architecture.md"

    rc = main([
        "create",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--target", str(target),
    ])

    assert rc == 0
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "Project-Tuned BRD Template" in content


def test_cli_create_uses_layer_template_when_project_tuned_missing(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    (tmp_path / "docs/UCX/templates/BRD-MVP-TEMPLATE.md").unlink()
    target = tmp_path / "docs/01_BRD/BRD-02_platform/BRD-02_platform.md"

    rc = main([
        "create",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--target", str(target),
    ])

    assert rc == 0
    assert target.exists()
    content = target.read_text(encoding="utf-8")
    assert "SDD authoritative template structure" in content


def test_cli_create_fails_when_target_exists_without_overwrite(tmp_path: Path) -> None:
    _scaffold_creation_fixtures(tmp_path)
    target = tmp_path / "docs/01_BRD/BRD-03_platform/BRD-03_platform.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("existing", encoding="utf-8")

    rc = main([
        "create",
        "--project", str(tmp_path),
        "--persona", "architect",
        "--doc-type", "brd",
        "--layer", "01_BRD",
        "--template", "UCC_PROMPT_BRD_PROJECT.md",
        "--target", str(target),
    ])

    assert rc == 1
    assert target.read_text(encoding="utf-8") == "existing"
