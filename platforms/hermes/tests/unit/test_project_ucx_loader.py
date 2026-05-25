from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.skills import (  # noqa: E402
    PersonaMappingError,
    ProjectSkillsNotFound,
    load_multi_persona_files,
    load_persona_mapping,
    load_project_document_template,
    load_project_layer_assets,
    load_project_prompt_template,
    validate_project_ucx_root,
)
from mcp_server.skills.project_ucx_loader import load_project_persona_file  # noqa: E402

REQUIRED_RELATIVE_PATHS = [
    Path("UCX/skills/personas"),
    Path("UCX/skills/layer_aliases"),
    Path("UCX/prompts/templates/creation"),
    Path("UCX/prompts/templates/review"),
    Path("UCX/prompts/templates/remediation"),
    Path("UCX/templates"),
    Path("UCX/templates/layers"),
]


_DEFAULT_PERSONA_MAPPINGS = (
    'version: "1.0"\ncreation:\n  brd:\n    personas: [architect]\n    mode: sequential\n'
)


def create_runtime_ucx_tree(project_root: Path) -> None:
    for relative in REQUIRED_RELATIVE_PATHS:
        (project_root / relative).mkdir(parents=True, exist_ok=True)
    # Required file: persona_mappings.yaml
    mappings_path = project_root / "UCX/skills/persona_mappings.yaml"
    if not mappings_path.exists():
        (project_root / "UCX/skills/personas/architect.md").write_text(
            "Architect stub", encoding="utf-8"
        )
        mappings_path.write_text(_DEFAULT_PERSONA_MAPPINGS, encoding="utf-8")


def test_validate_project_ucx_root_raises_for_missing_paths(tmp_path: Path) -> None:
    try:
        validate_project_ucx_root(tmp_path)
    except ProjectSkillsNotFound as exc:
        assert exc.error_code == "ProjectSkillsNotFound"
        assert exc.missing_paths
    else:
        raise AssertionError("Expected ProjectSkillsNotFound")


def test_load_project_persona_file_reads_project_specific_persona(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    persona_file = tmp_path / "UCX/skills/personas/architect.md"
    persona_file.write_text("Architect persona", encoding="utf-8")

    result = load_project_persona_file(project_root=tmp_path, persona="architect")
    assert result == "Architect persona"


def test_load_project_prompt_template_reads_project_specific_template(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    template_file = tmp_path / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md"
    template_file.write_text("Review prompt", encoding="utf-8")

    result = load_project_prompt_template(
        project_root=tmp_path,
        phase="review",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
    )
    assert result == "Review prompt"


def test_load_project_document_template_reads_project_specific_template(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    template_file = tmp_path / "UCX/templates/BRD-MVP-TEMPLATE.md"
    template_file.write_text("BRD tuned template", encoding="utf-8")

    result = load_project_document_template(
        project_root=tmp_path,
        template_name="BRD-MVP-TEMPLATE.md",
    )
    assert result == "BRD tuned template"


def test_load_project_layer_assets_reads_authoritative_layer_files(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    layer_root = tmp_path / "UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "BRD-MVP-TEMPLATE.md").write_text("BRD md", encoding="utf-8")
    (layer_root / "BRD-MVP-TEMPLATE.yaml").write_text("doc_id: BRD-01\n", encoding="utf-8")
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")

    assets = load_project_layer_assets(project_root=tmp_path, layer="01_BRD")

    assert "BRD-MVP-TEMPLATE.md" in assets
    assert "BRD-MVP-TEMPLATE.yaml" in assets
    assert "BRD_MVP_SCHEMA.yaml" in assets


def test_load_multi_persona_files_loads_multiple(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    (tmp_path / "UCX/skills/personas/architect.md").write_text("Architect domain", encoding="utf-8")
    (tmp_path / "UCX/skills/personas/tech_lead.md").write_text("Tech lead domain", encoding="utf-8")

    result = load_multi_persona_files(project_root=tmp_path, personas=["architect", "tech_lead"])
    assert len(result) == 2
    assert result[0] == ("architect", "Architect domain")
    assert result[1] == ("tech_lead", "Tech lead domain")


def test_load_persona_mapping_valid(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    (tmp_path / "UCX/skills/personas/architect.md").write_text("Architect", encoding="utf-8")
    mapping_content = (
        'version: "1.0"\n'
        "creation:\n"
        "  brd:\n"
        "    personas: [architect]\n"
        "    mode: sequential\n"
    )
    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text(mapping_content, encoding="utf-8")

    result = load_persona_mapping(project_root=tmp_path)
    assert result["version"] == "1.0"
    assert result["creation"]["brd"]["personas"] == ["architect"]


def test_load_persona_mapping_raises_on_missing_file(tmp_path: Path) -> None:
    # Create dirs without persona_mappings.yaml — manually create tree
    for relative in REQUIRED_RELATIVE_PATHS:
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)
    # validate_project_ucx_root will fail because persona_mappings.yaml is required
    try:
        load_persona_mapping(project_root=tmp_path)
    except ProjectSkillsNotFound:
        pass
    else:
        raise AssertionError("Expected ProjectSkillsNotFound")


def test_validate_persona_mapping_raises_on_missing_version(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text("creation: {}", encoding="utf-8")
    from mcp_server.skills.project_ucx_loader import _invalidate_persona_mapping_cache

    _invalidate_persona_mapping_cache(tmp_path)
    try:
        load_persona_mapping(project_root=tmp_path)
    except PersonaMappingError as exc:
        assert "version" in str(exc)
    else:
        raise AssertionError("Expected PersonaMappingError")


def test_validate_persona_mapping_raises_on_invalid_persona_name(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    mapping_content = (
        'version: "1.0"\n'
        "creation:\n"
        "  brd:\n"
        "    personas: [nonexistent_persona]\n"
        "    mode: sequential\n"
    )
    (tmp_path / "UCX/skills/persona_mappings.yaml").write_text(mapping_content, encoding="utf-8")
    from mcp_server.skills.project_ucx_loader import _invalidate_persona_mapping_cache

    _invalidate_persona_mapping_cache(tmp_path)
    try:
        load_persona_mapping(project_root=tmp_path)
    except ProjectSkillsNotFound as exc:
        assert "nonexistent_persona" in str(exc)
    else:
        raise AssertionError("Expected ProjectSkillsNotFound")
