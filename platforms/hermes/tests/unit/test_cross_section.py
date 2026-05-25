"""Unit tests for generic cross-section validation rules.

Covers:
  SDD-XS-001  Traceability ID Existence
  SDD-XS-002  Readiness Score Plausibility
  SDD-XS-003  Diagram Registry Present
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.validation.cross_section import (  # noqa: E402
    run_cross_section_checks,
    run_cross_section_checks_md,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_lists() -> tuple[list[str], list[str], list[str]]:
    """Return fresh (errors, warnings, passes) lists."""
    return [], [], []


# ---------------------------------------------------------------------------
# SDD-XS-001 -- Traceability ID Existence
# ---------------------------------------------------------------------------


def test_traceability_id_passes_when_all_exist():
    """Traceability referencing an ID present in the document passes."""
    yaml_data = {
        "quality_expectations": [{"id": "BRD.04.07.cfab", "text": "perf"}],
        "traceability": {"upstream": "BRD.04.07.cfab"},
    }
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert not errors
    assert any("SDD-XS-001" in p and "1 traceability IDs exist" in p for p in passes)


def test_traceability_id_errors_on_phantom():
    """Traceability referencing a non-existent ID produces an error."""
    yaml_data = {
        "quality_expectations": [{"id": "BRD.04.07.cfab", "text": "perf"}],
        "traceability": {"upstream": "BRD.04.07.dead"},
    }
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert any("BRD.04.07.dead" in e for e in errors)


def test_traceability_id_works_for_prd():
    """Rule runs for PRD documents with traceability."""
    yaml_data = {
        "features": [{"id": "PRD.01.09.abcd", "desc": "login"}],
        "traceability": {"maps_to": "PRD.01.09.abcd"},
    }
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="prd", errors=errors, warnings=warnings, passes=passes
    )
    assert not errors
    assert any("SDD-XS-001" in p for p in passes)


def test_traceability_id_skips_when_no_traceability():
    """YAML without a traceability key results in a pass (skipped)."""
    yaml_data = {"quality_expectations": [{"id": "BRD.04.07.cfab"}]}
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert not errors
    assert any("skipped" in p for p in passes)


# ---------------------------------------------------------------------------
# SDD-XS-002 -- Readiness Score Plausibility
# ---------------------------------------------------------------------------


def test_readiness_score_warns_100_with_errors():
    """Perfect score with pre-populated errors triggers a warning."""
    yaml_data = {"prd_ready_score": "100/100"}
    errors, warnings, passes = _make_lists()
    errors.append("pre-existing error")
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert any("SDD-XS-002" in w and "recalculate" in w for w in warnings)


def test_readiness_score_passes_100_clean():
    """Perfect score with no errors or warnings is plausible."""
    yaml_data = {"prd_ready_score": "100/100"}
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert not warnings
    assert any("SDD-XS-002" in p and "plausible" in p for p in passes)


def test_readiness_score_detects_field_per_layer():
    """PRD uses ears_ready_score as its readiness field."""
    yaml_data = {"ears_ready_score": "100/100"}
    errors, warnings, passes = _make_lists()
    errors.append("some error")
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="prd", errors=errors, warnings=warnings, passes=passes
    )
    assert any("SDD-XS-002" in w and "ears_ready_score" in w for w in warnings)


def test_readiness_score_skips_unknown_layer():
    """Unknown doc_type results in no score check (no error, no pass)."""
    yaml_data = {"prd_ready_score": "100/100"}
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="unknown", errors=errors, warnings=warnings, passes=passes
    )
    xs002 = [m for m in errors + warnings + passes if "SDD-XS-002" in m]
    assert not xs002


# ---------------------------------------------------------------------------
# SDD-XS-003 -- Diagram Registry Present
# ---------------------------------------------------------------------------


def test_diagram_registry_warns_no_items():
    """Diagram contract present but no diagrams.items triggers a warning."""
    yaml_data = {
        "metadata": {"diagram_standard": {"tags": ["mermaid"]}},
    }
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert any("SDD-XS-003" in w for w in warnings)


def test_diagram_registry_passes_with_items():
    """Diagram contract with populated items passes."""
    yaml_data = {
        "metadata": {"diagram_standard": {"tags": ["mermaid"]}},
        "diagrams": {"items": [{"name": "arch", "path": "arch.svg"}]},
    }
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    assert any("SDD-XS-003" in p and "1 items" in p for p in passes)
    assert not any("SDD-XS-003" in w for w in warnings)


def test_diagram_registry_skips_non_diagram_layer():
    """EARS doc_type is not in _DIAGRAM_LAYERS, so no XS-003 output."""
    yaml_data = {
        "metadata": {"diagram_standard": {"tags": ["mermaid"]}},
    }
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="ears", errors=errors, warnings=warnings, passes=passes
    )
    xs003 = [m for m in errors + warnings + passes if "SDD-XS-003" in m]
    assert not xs003


# ---------------------------------------------------------------------------
# Markdown fallback
# ---------------------------------------------------------------------------


def test_md_fallback_runs_without_crash():
    """run_cross_section_checks_md completes without exception."""
    md_content = "---\ntitle: Test\n---\n\n## Traceability\n\nMaps to BRD.01.07.aaaa\n"
    errors, warnings, passes = _make_lists()
    run_cross_section_checks_md(
        content=md_content, doc_type="brd", errors=errors, warnings=warnings, passes=passes
    )
    # Should not crash; exact results depend on content but lists are populated.
    assert isinstance(errors, list)
    assert isinstance(passes, list)


def test_cumulative_tags_enforces_max_for_iplan():
    """IPLAN documents enforce maximum 8 cumulative tags."""
    yaml_data = {"metadata": {"tags": ["a", "b", "c", "d", "e", "f", "g", "h", "i"]}}
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="iplan", errors=errors, warnings=warnings, passes=passes
    )
    assert any("SDD-XS-004" in e and "max 8" in e for e in errors)


def test_cumulative_tags_passes_within_max_for_tdd():
    """TDD documents pass when tags count <= 7."""
    yaml_data = {"metadata": {"tags": ["a", "b", "c", "d", "e", "f", "g"]}}
    errors, warnings, passes = _make_lists()
    run_cross_section_checks(
        yaml_data=yaml_data, doc_type="tdd", errors=errors, warnings=warnings, passes=passes
    )
    assert not any("SDD-XS-004" in e for e in errors)
    assert any("SDD-XS-004" in p for p in passes)
