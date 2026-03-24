from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.prompts import SourceSection  # noqa: E402
from mcp_server.review import run_project_review_build  # noqa: E402


def _create_project_ucx(root: Path) -> None:
    for relative in [
        Path("docs/UCX/skills/personas"),
        Path("docs/UCX/skills/layer_aliases"),
        Path("docs/UCX/prompts/templates/creation"),
        Path("docs/UCX/prompts/templates/review"),
        Path("docs/UCX/prompts/templates/remediation"),
        Path("docs/UCX/templates"),
        Path("docs/UCX/templates/layers"),
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)

    (root / "docs/UCX/skills/personas/architect.md").write_text("Architect persona", encoding="utf-8")
    (root / "docs/UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text("Review template", encoding="utf-8")


def test_run_project_review_build_writes_artifacts(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build(
        project_root=tmp_path,
        persona="architect",
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture and integration"),
            SourceSection(section_id="9.0", title="Appendix", content="reference metadata appendix"),
        ],
        output_dir=out,
    )

    assert result.prompt_path is not None and result.prompt_path.exists()
    assert result.sidecar_path is not None and result.sidecar_path.exists()
    assert result.inspection_path is not None and result.inspection_path.exists()
    assert "architect" in result.sidecar_json
    assert result.inspection["doc_type"] == "brd"
