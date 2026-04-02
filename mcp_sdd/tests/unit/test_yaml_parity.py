"""Tests for YAML parity fixes in consistency, next_action, and scoring."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.consistency.runner import run_consistency_check  # noqa: E402
from mcp_server.tool_registry import _inspect_document_folder  # noqa: E402
from mcp_server.scoring.runner import show_score  # noqa: E402


# ── Consistency: YAML source detection ───────────────────────────────────────


def test_consistency_finds_yaml_source(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    result = run_consistency_check(target_path=tmp_path)
    assert result.passed is True
    assert "missing_source_artifact" not in result.payload.get("errors", [])


def test_consistency_detects_yaml_validation_copy(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    val = tmp_path / "BRD-01_test_validate_copy.yaml"
    val.write_text("title: validation copy\n")
    result = run_consistency_check(target_path=tmp_path)
    details = result.payload.get("details", {})
    assert details.get("validation_copy") == "BRD-01_test_validate_copy.yaml"


def test_consistency_still_works_for_md(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.md"
    src.write_text("# BRD\n")
    result = run_consistency_check(target_path=tmp_path)
    assert result.passed is True
    assert "missing_source_artifact" not in result.payload.get("errors", [])


# ── Next action: YAML source and derived artifact detection ──────────────────


def test_next_action_detects_yaml_source(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    info = _inspect_document_folder(tmp_path)
    assert info["current_stage"] == "created"
    assert "BRD-01_test.yaml" in info["existing_artifacts"]


def test_next_action_detects_yaml_validation_copy(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    val = tmp_path / "BRD-01_test_validate_copy.yaml"
    val.write_text("title: validation copy\n")
    report = tmp_path / "BRD-01.ucx.validate.json"
    report.write_text(json.dumps({"summary": {"errors": 0}}))
    info = _inspect_document_folder(tmp_path)
    assert info["current_stage"] == "validation_fixed"


def test_next_action_detects_yaml_remediated_copy(tmp_path: Path) -> None:
    src = tmp_path / "BRD-01_test.yaml"
    src.write_text("title: test\n")
    rem = tmp_path / "BRD-01_test_remediate_copy.yaml"
    rem.write_text("title: remediated copy\n")
    info = _inspect_document_folder(tmp_path)
    assert info["current_stage"] == "remediated"


# ── Scoring: categorized weights and backward compat ─────────────────────────


def test_score_categorized_weighted(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    report.write_text(json.dumps({
        "summary": {
            "structural_errors": 1,
            "cross_section_errors": 5,
            "warnings": 2,
        }
    }))
    result = show_score(report_file=report)
    # 100 - (1*20) - (5*10) - (2*5) = 100 - 20 - 50 - 10 = 20
    assert result.score == 20


def test_score_backward_compat_no_categories(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    report.write_text(json.dumps({
        "summary": {
            "errors": 3,
            "warnings": 1,
        }
    }))
    result = show_score(report_file=report)
    # 100 - (3*20) - (1*5) = 100 - 60 - 5 = 35
    assert result.score == 35


def test_score_show_returns_category_breakdown(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    report.write_text(json.dumps({
        "summary": {
            "structural_errors": 2,
            "cross_section_errors": 1,
            "warnings": 0,
        }
    }))
    result = show_score(report_file=report)
    assert "structural_errors" in result.summary
    assert "cross_section_errors" in result.summary
    assert result.summary["structural_errors"] == 2
    assert result.summary["cross_section_errors"] == 1
