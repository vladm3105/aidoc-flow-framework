"""Unit tests for UCRem source-file protection during report generation."""

from pathlib import Path

import pytest

from ucx.api.remediation import UCRemPhase
from ucx.config.settings import UCXConfig
from ucx.prescreening.ucr_analyzer import ScreeningResult


def _build_phase(project_dir: Path) -> UCRemPhase:
    """Create UCRemPhase configured with a temporary project root."""
    config = UCXConfig(model="mock", project_dir=project_dir, load_skills=False)
    return UCRemPhase(config=config)


def test_generate_fixes_restores_unexpected_source_changes(monkeypatch, tmp_path: Path):
    """Remediation generation must not leave source document edits behind."""
    project_dir = tmp_path / "project"
    doc_dir = project_dir / "docs" / "02_PRD" / "PRD-01_platform_architecture"
    prompt_dir = project_dir / "docs" / "UCX" / "remediation"
    doc_dir.mkdir(parents=True)
    prompt_dir.mkdir(parents=True)

    # Minimal project prompt required by UCRem loader.
    prompt_file = prompt_dir / "UCRem_PROMPT_PRD_PROJECT.md"
    prompt_file.write_text("# Test UCRem Prompt\n", encoding="utf-8")

    source_doc = doc_dir / "PRD-01_platform_architecture.md"
    original_content = "# PRD-01\n\nOriginal source content.\n"
    source_doc.write_text(original_content, encoding="utf-8")

    review_report = doc_dir / "PRD-01.UCX_review_report_v001.md"
    review_report.write_text("# Mock review report\n", encoding="utf-8")

    screening = ScreeningResult(
        required_fixers=["chaos_engineer", "chairperson"],
        excluded_fixers=[],
        total_findings=1,
        actionable_findings=1,
    )

    phase = _build_phase(project_dir)

    monkeypatch.setattr("ucx.api.remediation.analyze_ucr_report", lambda *_args, **_kwargs: screening)

    class _MutatingClient:
        def generate(self, _prompt: str) -> str:
            # Simulate unexpected side effect from external tooling.
            source_doc.write_text("# PRD-01\n\nMUTATED by tool.\n", encoding="utf-8")
            return "# UCRem Report: PRD-01\n\nNo fixes.\n"

    phase._ai_client = _MutatingClient()

    fixes, report_path = phase.generate_fixes(
        doc_path=doc_dir,
        review_report=review_report,
    )

    assert fixes == []
    assert report_path.exists()
    assert source_doc.read_text(encoding="utf-8") == original_content


def test_generate_fixes_rejects_source_prd_for_api_call(tmp_path: Path):
    """API callers must remediate only validation-fixed PRD artifacts."""
    project_dir = tmp_path / "project"
    doc_dir = project_dir / "docs" / "02_PRD" / "PRD-01_platform_architecture"
    doc_dir.mkdir(parents=True)

    source_doc = doc_dir / "PRD-01_platform_architecture.md"
    source_doc.write_text("# PRD-01\n", encoding="utf-8")

    review_report = doc_dir / "PRD-01.UCX_review_report_v001.md"
    review_report.write_text("# Mock review report\n", encoding="utf-8")

    phase = _build_phase(project_dir)

    with pytest.raises(ValueError, match="PRD remediation must use a _validation PRD copy"):
        phase.generate_fixes(doc_path=source_doc, review_report=review_report)


def test_generate_fixes_rejects_non_ucx_review_report_for_prd_api_call(tmp_path: Path):
    """API callers must supply a UCX review report for PRD remediation."""
    project_dir = tmp_path / "project"
    doc_dir = project_dir / "docs" / "02_PRD" / "PRD-01_platform_architecture"
    doc_dir.mkdir(parents=True)

    validation_doc = doc_dir / "PRD-01_platform_architecture_validation.md"
    validation_doc.write_text("# PRD-01 validation\n", encoding="utf-8")

    validation_report = doc_dir / "PRD-01_validation_report.md"
    validation_report.write_text("# Mock validation report\n", encoding="utf-8")

    phase = _build_phase(project_dir)

    with pytest.raises(ValueError, match=r"PRD remediation requires a UCX review report"):
        phase.generate_fixes(doc_path=validation_doc, review_report=validation_report)
