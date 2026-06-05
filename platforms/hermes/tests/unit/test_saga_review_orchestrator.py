from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.executor.contracts import ExecutorResult  # noqa: E402
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
    (root / "UCX/prompts/templates/review/UCR_PROMPT_BRD_PROJECT.md").write_text(
        "Review template", encoding="utf-8"
    )
    layer_root = root / "UCX/templates/layers/01_BRD"
    layer_root.mkdir(parents=True, exist_ok=True)
    (layer_root / "BRD-MVP-TEMPLATE.md").write_text("BRD template layer asset", encoding="utf-8")
    (layer_root / "BRD_MVP_SCHEMA.yaml").write_text("schema_version: '1.0'\n", encoding="utf-8")


def test_saga_orchestrator_closed_status(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    document_dir = tmp_path / "docs" / "01_BRD" / "BRD-01_test"
    document_dir.mkdir(parents=True, exist_ok=True)
    (document_dir / "BRD-01_test_validated.md").write_text("validated copy", encoding="utf-8")
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect", "auditor"],
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
        document_path=document_dir,
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
    assert "BRD-01_validation-fixed_saga_branch_summary_v" in result.branch_summary_path.name
    assert "BRD-01_validation-fixed_saga_reducer_summary_v" in result.reducer_summary_path.name
    assert "BRD-01_validation-fixed_saga_synthesis_summary_v" in result.synthesis_summary_path.name


def test_saga_orchestrator_escalated_on_missing_persona(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["missing_persona"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Architecture",
                content="system architecture and integration",
            ),
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


def test_saga_source_stage_detection_and_resume_behavior(tmp_path: Path) -> None:
    _create_project_ucx(tmp_path)
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    source_file = docs / "BRD-02_feature.md"
    source_file.write_text("# source", encoding="utf-8")

    remediated_file = docs / "BRD-02_feature_remediate_v1.md"
    remediated_file.write_text("# remediated", encoding="utf-8")

    out = tmp_path / "tmp/evidence"
    sections = [
        SourceSection(section_id="1.0", title="Architecture", content="system architecture")
    ]

    source_result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=sections,
        document_path=source_file,
        layer="01_BRD",
        output_dir=out,
    )
    assert source_result.branch_summary_path is not None
    assert "BRD-02_source_saga_branch_summary_v" in source_result.branch_summary_path.name

    rem_result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=sections,
        document_path=remediated_file,
        layer="01_BRD",
        output_dir=out,
    )
    assert rem_result.branch_summary_path is not None
    assert "BRD-02_remediated_saga_branch_summary_v" in rem_result.branch_summary_path.name

    journal_payload = json.loads(source_result.journal_path.read_text(encoding="utf-8"))
    journal_payload["status"] = "CLOSED"
    source_result.journal_path.write_text(json.dumps(journal_payload), encoding="utf-8")

    with pytest.raises(ValueError) as exc_info:
        run_project_review_build_saga(
            project_root=tmp_path,
            personas=["architect"],
            doc_type="brd",
            template_name="UCR_PROMPT_BRD_PROJECT.md",
            sections=sections,
            document_path=source_file,
            layer="01_BRD",
            output_dir=out,
            saga_resume=True,
        )
    assert "Cannot resume terminal saga run" in str(exc_info.value)


def test_saga_branch_llm_enabled_collects_branch_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence"

    from mcp_server.review import saga_orchestrator as so

    async def _fake_run_executor(**kwargs):
        _ = kwargs
        return ExecutorResult(
            stdout='{"findings":[{"priority":"P1","category":"quality","message":"Use explicit retries","recommended_action":"Add retry policy","target_layer":"01_BRD"}]}',
            stderr="",
            exit_code=0,
            executor_name="api/openrouter",
            metadata={"model": "openrouter/auto", "usage": {"total_tokens": 123}},
        )

    monkeypatch.setattr(so, "run_executor", _fake_run_executor)

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect", "auditor"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(
                section_id="1.0",
                title="Architecture",
                content="system architecture and integration",
            ),
        ],
        layer="01_BRD",
        output_dir=out,
        executor_name="api/openrouter",
        saga_branch_llm_enabled=True,
    )

    assert result.saga_status == "CLOSED"
    assert result.branch_summary["branch_llm_enabled"] is True
    assert len(result.branch_summary["branches"]) == 2
    assert result.reducer_summary["branch_llm_enabled"] is True
    assert result.reduced_findings is not None
    assert len(result.reduced_findings) >= 1


def test_saga_rollout_phase_c_enables_branch_llm_without_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence-rollout"

    from mcp_server.review import saga_orchestrator as so

    async def _fake_run_executor(**kwargs):
        _ = kwargs
        return ExecutorResult(
            stdout='{"findings":[{"priority":"P1","category":"quality","message":"Bound branch policy","recommended_action":"Keep policy","target_layer":"01_BRD"}]}',
            stderr="",
            exit_code=0,
            executor_name="api/openrouter",
            metadata={"model": "openrouter/auto", "usage": {"total_tokens": 55}},
        )

    monkeypatch.setattr(so, "run_executor", _fake_run_executor)

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture")
        ],
        layer="01_BRD",
        output_dir=out,
        executor_name="api/openrouter",
        project_env={"UCX_REVIEW_SAGA_BRANCH_LLM_PHASE": "C"},
        saga_branch_llm_enabled=None,
    )

    assert result.saga_status == "CLOSED"
    assert result.branch_summary["branch_llm_enabled"] is True
    assert result.branch_summary["rollout_phase"] == "C"


def test_saga_debug_raw_outputs_are_redacted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence-debug"

    from mcp_server.review import saga_orchestrator as so

    async def _fake_run_executor(**kwargs):
        _ = kwargs
        return ExecutorResult(
            stdout='{"findings":[{"priority":"P1","category":"security","message":"Rotate key","recommended_action":"Replace key","target_layer":"01_BRD"}],"debug":"api_key=sk-abcdefghijklmnopqrstuv123456"}',
            stderr="",
            exit_code=0,
            executor_name="api/openrouter",
            metadata={"model": "openrouter/auto", "usage": {"total_tokens": 41}},
        )

    monkeypatch.setattr(so, "run_executor", _fake_run_executor)

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture")
        ],
        layer="01_BRD",
        output_dir=out,
        executor_name="api/openrouter",
        project_env={
            "UCX_REVIEW_SAGA_BRANCH_LLM_ENABLED": "true",
            "UCX_REVIEW_DEBUG_RAW_OUTPUTS": "true",
        },
    )

    raw_outputs = result.branch_summary.get("raw_outputs", [])
    assert isinstance(raw_outputs, list)
    assert len(raw_outputs) == 1
    redacted = str(raw_outputs[0].get("raw_output_redacted", ""))
    assert "sk-abcdefghijklmnopqrstuv123456" not in redacted
    assert "[REDACTED]" in redacted


def test_saga_partial_crew_degrades_above_quorum(tmp_path: Path) -> None:
    # 1 of 2 lenses fails (missing persona). 1/2 == quorum 0.5 -> proceed, degraded.
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence-degrade"

    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect", "missing_persona"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture")
        ],
        layer="01_BRD",
        output_dir=out,
        max_branch_retries=0,
    )

    assert result.saga_status == "CLOSED"
    assert result.passed is True
    assert result.coverage is not None
    assert result.coverage["completed"] == ["architect"]
    assert result.coverage["failed"] == ["missing_persona"]
    assert result.coverage["quorum_met"] is True
    assert result.coverage["low_confidence"] is True
    assert result.reducer_summary_path is not None


def test_saga_review_score_from_lens_scores(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _create_project_ucx(tmp_path)
    out = tmp_path / "tmp/evidence-score"

    from mcp_server.review import saga_orchestrator as so

    async def _fake_run_executor(**kwargs):
        _ = kwargs
        return ExecutorResult(
            stdout=(
                '{"lens_score": 90, "findings":[{"priority":"P2","category":"quality",'
                '"message":"minor polish","recommended_action":"tidy","location":"section 3",'
                '"target_layer":"01_BRD"}]}'
            ),
            stderr="",
            exit_code=0,
            executor_name="api/openrouter",
            metadata={"model": "openrouter/auto", "usage": {"total_tokens": 30}},
        )

    monkeypatch.setattr(so, "run_executor", _fake_run_executor)

    # architect (30) + auditor (20) are both in the framework BRD review crew.
    result = run_project_review_build_saga(
        project_root=tmp_path,
        personas=["architect", "auditor"],
        doc_type="brd",
        template_name="UCR_PROMPT_BRD_PROJECT.md",
        sections=[
            SourceSection(section_id="1.0", title="Architecture", content="system architecture")
        ],
        layer="01_BRD",
        output_dir=out,
        executor_name="api/openrouter",
        saga_branch_llm_enabled=True,
    )

    # Wiring check: lens_score from the executor flows into a computed review_score.
    assert result.saga_status == "CLOSED"
    assert result.review_score is not None
    assert isinstance(result.review_score["score"], float)
    assert "architect" in result.review_score["coverage"]["ran"]


def test_compute_review_score_helper() -> None:
    from mcp_server.review.saga_orchestrator import _compute_review_score

    class _Reduced:
        def __init__(self, priority: str) -> None:
            self.priority = priority

    # Full EARS crew, all 100, P2 finding -> weighted 100, no cap.
    full = _compute_review_score(
        doc_type="ears",
        lens_scores={
            "requirements_specialist": 100.0,
            "tech_lead": 100.0,
            "qa_lead": 100.0,
            "chaos_engineer": 100.0,
            "security_engineer": 100.0,
        },
        reduced=[_Reduced("P2")],
    )
    assert full is not None
    assert full["score"] == 100.0
    assert full["no_blocking"] is True

    # Unresolved P1 caps the score below the gate.
    capped = _compute_review_score(
        doc_type="ears",
        lens_scores={"requirements_specialist": 100.0},
        reduced=[_Reduced("P1")],
    )
    assert capped is not None
    assert capped["score"] == 89.0

    # No lens scores (e.g. deterministic mode) -> None; non-layer doc-type -> None.
    assert _compute_review_score(doc_type="ears", lens_scores={}, reduced=[]) is None
    assert (
        _compute_review_score(doc_type="tasks", lens_scores={"tech_lead": 80.0}, reduced=[]) is None
    )
