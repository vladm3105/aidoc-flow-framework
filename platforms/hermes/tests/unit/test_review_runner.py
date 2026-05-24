from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.prompts import SourceSection  # noqa: E402
from mcp_server.review import run_project_review_build  # noqa: E402


def _create_project_ucx(root: Path) -> None:
    for relative in [
        Path("UCX/skills/personas"),
        Path("UCX/skills/layer_aliases"),
        Path("UCX/prompts/templates/creation"),
        Path("UCX/prompts/templates/review"),
        Path("UCX/prompts/templates/remediation"),
        Path("UCX/templates"),
        Path("UCX/templates/layers"),
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)

    (root / "UCX/skills/persona_mappings.yaml").write_text('version: "1.0"\n', encoding="utf-8")
    (root / "UCX/skills/personas/architect.md").write_text("Architect persona", encoding="utf-8")
    (root / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text(
        "Review template", encoding="utf-8"
    )
    layer_root = root / "UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "BRD-MVP-TEMPLATE.md").write_text("BRD template layer asset", encoding="utf-8")
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")


def test_run_project_review_build_writes_artifacts(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Architecture",
                content="system architecture and integration",
            ),
            SourceSection(
                section_id="9.0", title="Appendix", content="reference metadata appendix"
            ),
        ],
        output_dir=out,
    )

    assert result.prompt_path is not None and result.prompt_path.exists()
    assert result.sidecar_path is not None and result.sidecar_path.exists()
    assert result.inspection_path is not None and result.inspection_path.exists()
    assert "architect" in result.sidecar_json
    assert result.inspection["doc_type"] == "brd"


def test_run_project_review_build_includes_layer_assets_when_layer_provided(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Architecture",
                content="system architecture and integration",
            ),
            SourceSection(
                section_id="9.0", title="Appendix", content="reference metadata appendix"
            ),
        ],
        layer="01_BRD",
        output_dir=out,
    )

    assert "MCP Actionable Review Rules" in result.prompt_text
    assert "BRD-MVP-TEMPLATE.md" in result.layer_asset_names
    assert "BRD_MVP_SCHEMA.yaml" in result.layer_asset_names
