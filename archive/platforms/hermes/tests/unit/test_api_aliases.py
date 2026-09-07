"""Tests for result class property aliases (API consistency)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.consistency.runner import ConsistencyRunResult  # noqa: E402
from mcp_server.link_validation.runner import LinkValidationRunResult  # noqa: E402
from mcp_server.preflight.runner import PreflightRunResult  # noqa: E402
from mcp_server.scoring.runner import ScoreShowResult, ScoreValidateResult  # noqa: E402

# ── ConsistencyRunResult ─────────────────────────────────────────────────────


def test_consistency_result_report_alias() -> None:
    r = ConsistencyRunResult(
        payload={"test": 1},
        report_json="{}",
        report_text="",
        passed=True,
        report_path=None,
        summary_path=None,
    )
    assert r.report == r.payload


def test_consistency_result_is_valid_alias() -> None:
    r = ConsistencyRunResult(
        payload={},
        report_json="{}",
        report_text="",
        passed=True,
        report_path=None,
        summary_path=None,
    )
    assert r.is_valid == r.passed


# ── LinkValidationRunResult ──────────────────────────────────────────────────


def test_link_validation_report_alias() -> None:
    r = LinkValidationRunResult(
        payload={"links": 5},
        report_json="{}",
        report_text="",
        passed=False,
        report_path=None,
        summary_path=None,
    )
    assert r.report == r.payload
    assert r.is_valid == r.passed


# ── PreflightRunResult ───────────────────────────────────────────────────────


def test_preflight_report_alias() -> None:
    r = PreflightRunResult(
        payload={"ctx": "any"},
        report_json="{}",
        report_text="",
        status="ready",
        report_path=None,
        summary_path=None,
    )
    assert r.report == r.payload


def test_preflight_is_ready_true() -> None:
    r = PreflightRunResult(
        payload={},
        report_json="{}",
        report_text="",
        status="ready",
        report_path=None,
        summary_path=None,
    )
    assert r.is_ready is True


def test_preflight_is_ready_false() -> None:
    r = PreflightRunResult(
        payload={},
        report_json="{}",
        report_text="",
        status="degraded",
        report_path=None,
        summary_path=None,
    )
    assert r.is_ready is False


# ── ScoreShowResult ──────────────────────────────────────────────────────────


def test_score_show_report_alias() -> None:
    r = ScoreShowResult(score=80, summary={"errors": 1}, payload={"score": 80})
    assert r.report == r.payload


# ── ScoreValidateResult ──────────────────────────────────────────────────────


def test_score_validate_is_valid_alias() -> None:
    r = ScoreValidateResult(
        score=90,
        threshold=80,
        passed=True,
        payload={"passed": True},
    )
    assert r.report == r.payload
    assert r.is_valid == r.passed
