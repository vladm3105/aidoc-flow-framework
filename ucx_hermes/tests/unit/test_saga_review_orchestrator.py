from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.prompts import SourceSection  # noqa: E402
from mcp_server.review.saga_orchestrator import run_project_review_build_saga  # noqa: E402


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
    (root / "UCX/skills/personas/auditor.md").write_text("Auditor persona", encoding="utf-8")
    (root / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text("Review template", encoding="utf-8")
    layer_root = root / "UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "BRD-MVP-TEMPLATE.md").write_text("BRD template layer asset", encoding="utf-8")
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")


def test_saga_orchestrator_closed_status(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect", "auditor"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture and integration"),
            SourceSection(section_id="9.0", title="Appendix", content="reference metadata appendix"),
        ],
        layer="01_BRD",
        output_dir=out,
    )

    assert result.review_mode == "saga_parallel"
    assert result.saga_status == "CLOSED"
    assert result.passed is True
    assert result.journal_path.exists()
    assert result.reducer_summary["reduced_count"] >= 1
    assert result.branch_summary_path is not None
    assert result.reducer_summary_path is not None
    assert result.synthesis_summary_path is not None
    assert result.branch_summary_path.exists()
    assert result.reducer_summary_path.exists()
    assert result.synthesis_summary_path.exists()
    assert "BRD-00_validation-fixed_saga_branch_summary_v" in result.branch_summary_path.name
    assert "BRD-00_validation-fixed_saga_reducer_summary_v" in result.reducer_summary_path.name
    assert "BRD-00_validation-fixed_saga_synthesis_summary_v" in result.synthesis_summary_path.name


def test_saga_orchestrator_escalated_on_missing_persona(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["missing_persona"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture and integration"),
        ],
        layer="01_BRD",
        output_dir=out,
        max_branch_retries=1,
    )

    assert result.saga_status == "ESCALATED"
    assert result.passed is False
    assert result.compensation_summary["count"] == 1
    assert result.branch_summary_path is not None
    assert result.branch_summary_path.exists()
    assert result.reducer_summary_path is None
    assert result.synthesis_summary_path is None
