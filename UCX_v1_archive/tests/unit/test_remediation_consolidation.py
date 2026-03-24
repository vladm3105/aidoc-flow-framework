"""Unit tests for UCRem report consolidation behavior."""

from pathlib import Path

from ucx.api.remediation import UCRemPhase
from ucx.config.settings import UCXConfig


def _build_phase(project_dir: Path) -> UCRemPhase:
    """Create UCRemPhase configured with a temporary project root."""
    config = UCXConfig(model="mock", project_dir=project_dir)
    return UCRemPhase(config=config)


def test_consolidates_referenced_ucrem_report_and_removes_duplicate(tmp_path: Path):
    """UCX remediation should inline external UCRem content for single-report output."""
    project_dir = tmp_path / "project"
    doc_dir = project_dir / "docs" / "02_PRD" / "PRD-01"
    doc_dir.mkdir(parents=True)

    output_path = doc_dir / "PRD-01.UCX_remediation_report_v002.md"
    external_path = doc_dir / "PRD-01.UCRem_remediation_report_v002.md"

    external_path.write_text(
        """---
 title: \"UCRem Report: PRD-01\"

# UCRem Remediation Report: PRD-01

```yaml
fix_id: FIX-P0-001
confidence: auto-safe
target_file: "PRD-01.md"
fix_type: add_section
fix_action:
  position: after
  anchor: "# Title"
  text: |
    Added content
```
""",
        encoding="utf-8",
    )

    ucx_wrapper_content = (
        "UCRem remediation report generated at "
        "`docs/02_PRD/PRD-01/PRD-01.UCRem_remediation_report_v002.md`."
    )

    phase = _build_phase(project_dir)
    consolidated = phase._consolidate_external_ucrem_report(
        content=ucx_wrapper_content,
        doc_path=doc_dir,
        output_path=output_path,
    )

    assert "fix_id: FIX-P0-001" in consolidated
    assert "UCRem remediation report generated at" not in consolidated
    assert not external_path.exists()


def test_keeps_wrapper_content_when_external_report_missing(tmp_path: Path):
    """UCX wrapper should be preserved when referenced external report cannot be resolved."""
    project_dir = tmp_path / "project"
    doc_dir = project_dir / "docs" / "02_PRD" / "PRD-01"
    doc_dir.mkdir(parents=True)

    output_path = doc_dir / "PRD-01.UCX_remediation_report_v001.md"
    wrapper = (
        "UCRem remediation report generated at "
        "`docs/02_PRD/PRD-01/PRD-01.UCRem_remediation_report_v001.md`."
    )

    phase = _build_phase(project_dir)
    consolidated = phase._consolidate_external_ucrem_report(
        content=wrapper,
        doc_path=doc_dir,
        output_path=output_path,
    )

    assert consolidated == wrapper


def test_consolidates_short_ucrem_report_variant(tmp_path: Path):
    """Regex must also match 'UCRem report generated at' (without 'remediation' word)."""
    project_dir = tmp_path / "project"
    doc_dir = project_dir / "docs" / "02_PRD" / "PRD-01"
    doc_dir.mkdir(parents=True)

    output_path = doc_dir / "PRD-01.UCX_remediation_report_v003.md"
    external_path = doc_dir / "PRD-01.UCRem_remediation_report_v003.md"

    external_path.write_text(
        """---
title: "UCRem Report: PRD-01"
---

# UCRem Report

```yaml
fix_id: FIX-P0-001
confidence: auto-safe
target_file: "PRD-01.md"
fix_type: add_section
fix_action:
  position: after
  anchor: "# Title"
  text: |
    Added content
```
""",
        encoding="utf-8",
    )

    # Variant without "remediation" in the reference line (as Claude Opus sometimes emits)
    ucx_wrapper_content = (
        "UCRem report generated at "
        "`docs/02_PRD/PRD-01/PRD-01.UCRem_remediation_report_v003.md`."
    )

    phase = _build_phase(project_dir)
    consolidated = phase._consolidate_external_ucrem_report(
        content=ucx_wrapper_content,
        doc_path=doc_dir,
        output_path=output_path,
    )

    assert "fix_id: FIX-P0-001" in consolidated
    assert "UCRem report generated at" not in consolidated
    assert not external_path.exists()
