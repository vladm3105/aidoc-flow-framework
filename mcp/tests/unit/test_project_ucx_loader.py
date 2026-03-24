from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.skills import (  # noqa: E402
    ProjectSkillsNotFound,
    load_project_document_template,
    load_project_layer_assets,
    load_project_persona_file,
    load_project_prompt_template,
    validate_project_ucx_root,
)


REQUIRED_RELATIVE_PATHS = [
    Path("docs/UCX/skills/personas"),
    Path("docs/UCX/skills/layer_aliases"),
    Path("docs/UCX/prompts/templates/creation"),
    Path("docs/UCX/prompts/templates/review"),
    Path("docs/UCX/prompts/templates/remediation"),
    Path("docs/UCX/templates"),
    Path("docs/UCX/templates/layers"),
]



def create_runtime_ucx_tree(project_root: Path) -> None:
    for relative in REQUIRED_RELATIVE_PATHS:
        (project_root / relative).mkdir(parents=True, exist_ok=True)



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
    persona_file = tmp_path / "docs/UCX/skills/personas/architect.md"
    persona_file.write_text("Architect persona", encoding="utf-8")

    result = load_project_persona_file(project_root=tmp_path, persona="architect")
    assert result == "Architect persona"



def test_load_project_prompt_template_reads_project_specific_template(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    template_file = tmp_path / "docs/UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md"
    template_file.write_text("Review prompt", encoding="utf-8")

    result = load_project_prompt_template(
        project_root=tmp_path,
        phase="review",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
    )
    assert result == "Review prompt"


def test_load_project_document_template_reads_project_specific_template(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    template_file = tmp_path / "docs/UCX/templates/BRD-MVP-TEMPLATE.md"
    template_file.write_text("BRD tuned template", encoding="utf-8")

    result = load_project_document_template(
        project_root=tmp_path,
        template_name="BRD-MVP-TEMPLATE.md",
    )
    assert result == "BRD tuned template"


def test_load_project_layer_assets_reads_authoritative_layer_files(tmp_path: Path) -> None:
    create_runtime_ucx_tree(tmp_path)
    layer_root = tmp_path / "docs/UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "README.md").write_text("Layer guidance", encoding="utf-8")
    (layer_root / "BRD-MVP-TEMPLATE.md").write_text("BRD md", encoding="utf-8")
    (layer_root / "BRD-MVP-TEMPLATE.yaml").write_text("doc_id: BRD-01\n", encoding="utf-8")

    assets = load_project_layer_assets(project_root=tmp_path, layer="01_BRD")

    assert "README.md" in assets
    assert "BRD-MVP-TEMPLATE.md" in assets
    assert "BRD-MVP-TEMPLATE.yaml" in assets
