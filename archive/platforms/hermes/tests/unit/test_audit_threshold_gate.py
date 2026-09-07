"""HERMES-ADAPT-ENFORCE-001 — `audit_threshold` raise-only score gate.

Covers the resolver, `validate_score` raise-only behavior, and — critically (F2) —
a handler-level `_dispatch` test that would catch a dead-wiring regression (the
profile being unreachable), which a `validate_score`-only test cannot.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.scoring.runner import (  # noqa: E402
    _resolve_audit_threshold,
    validate_score,
)


def _run(coro):
    """Run a coroutine on the current event loop, creating one if absent.

    Deliberately NOT ``asyncio.run()``: that nulls the process-wide current loop
    on exit, which breaks the rest of the Hermes suite (test_server et al. use the
    ``asyncio.get_event_loop()`` idiom). This reuses/creates a current loop and
    leaves it set, so there is no cross-test pollution.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def _write_report(path: Path, *, doc_type: str, errors: int = 0, warnings: int = 0) -> None:
    # score = max(0, 100 - errors*20 - warnings*5); 2 warnings → 90.
    payload = {"doc_type": doc_type, "summary": {"errors": errors, "warnings": warnings}}
    path.write_text(json.dumps(payload), encoding="utf-8")


# ── resolver ────────────────────────────────────────────────────────────────


def test_resolve_honors_value_at_or_above_default() -> None:
    assert _resolve_audit_threshold({"BRD": 95}, "brd") == 95
    assert _resolve_audit_threshold({"BRD": 90}, "brd") == 90


def test_resolve_ignores_below_default() -> None:
    assert _resolve_audit_threshold({"BRD": 85}, "brd") is None


def test_resolve_normalizes_layer_key() -> None:
    assert _resolve_audit_threshold({"BRD": 95}, "01_brd") == 95
    assert _resolve_audit_threshold({"BRD": 95}, "BRD") == 95


def test_resolve_skips_malformed_and_bool() -> None:
    assert _resolve_audit_threshold({"BRD": "high"}, "brd") is None
    assert _resolve_audit_threshold({"BRD": True}, "brd") is None  # bool is an int subclass
    assert _resolve_audit_threshold({"BRD": 95.0}, "brd") is None  # float, not int


def test_resolve_none_on_missing() -> None:
    assert _resolve_audit_threshold(None, "brd") is None
    assert _resolve_audit_threshold({}, "brd") is None
    assert _resolve_audit_threshold({"BRD": 95}, None) is None
    assert _resolve_audit_threshold({"PRD": 95}, "brd") is None  # different layer


# ── validate_score raise-only ─────────────────────────────────────────────────


def test_raise_applies_and_flips_outcome(tmp_path: Path) -> None:
    report = tmp_path / "brd.json"
    _write_report(report, doc_type="brd", warnings=2)  # score 90
    # caller 80 passes (90>=80); profile 95 raises → 90<95 → fails
    without = validate_score(report_file=report, threshold=80)
    assert without.passed is True
    assert without.payload["threshold"] == 80
    assert without.payload["threshold_source"] == "caller"

    raised = validate_score(report_file=report, threshold=80, audit_threshold={"BRD": 95})
    assert raised.passed is False
    assert raised.payload["threshold"] == 95
    assert raised.payload["threshold_source"] == "profile"


def test_below_default_never_weakens(tmp_path: Path) -> None:
    report = tmp_path / "brd.json"
    _write_report(report, doc_type="brd", warnings=2)  # score 90
    result = validate_score(report_file=report, threshold=80, audit_threshold={"BRD": 85})
    assert result.payload["threshold"] == 80  # 85 < 90 default → ignored
    assert result.payload["threshold_source"] == "caller"
    assert result.passed is True


def test_profile_can_only_raise_not_lower(tmp_path: Path) -> None:
    report = tmp_path / "brd.json"
    _write_report(report, doc_type="brd", warnings=2)  # score 90
    # caller already 95; a profile 90 must NOT lower it to 90
    result = validate_score(report_file=report, threshold=95, audit_threshold={"BRD": 90})
    assert result.payload["threshold"] == 95
    assert result.payload["threshold_source"] == "caller"


def test_malformed_value_skipped(tmp_path: Path) -> None:
    report = tmp_path / "brd.json"
    _write_report(report, doc_type="brd", warnings=2)
    result = validate_score(report_file=report, threshold=80, audit_threshold={"BRD": "high"})
    assert result.payload["threshold"] == 80
    assert result.passed is True


def test_no_profile_unchanged(tmp_path: Path) -> None:
    report = tmp_path / "brd.json"
    _write_report(report, doc_type="brd", warnings=2)
    result = validate_score(report_file=report, threshold=80, audit_threshold=None)
    assert result.payload["threshold"] == 80
    assert result.payload["threshold_source"] == "caller"


def test_interaction_with_tdd_readiness_floor(tmp_path: Path) -> None:
    report = tmp_path / "tdd.json"
    _write_report(report, doc_type="tdd", warnings=2)  # score 90; tdd floor → 90
    # no profile → floor 90
    floored = validate_score(report_file=report, threshold=80)
    assert floored.payload["threshold"] == 90
    assert floored.payload["threshold_source"] == "readiness_floor"
    # profile 95 raises above the floor
    raised = validate_score(report_file=report, threshold=80, audit_threshold={"TDD": 95})
    assert raised.payload["threshold"] == 95
    assert raised.payload["threshold_source"] == "profile"
    # profile 92 also raises above the 90 floor
    raised2 = validate_score(report_file=report, threshold=80, audit_threshold={"TDD": 92})
    assert raised2.payload["threshold"] == 92


# ── handler-level wiring (F2 — catches a dead-wiring regression) ───────────────


def test_dispatch_reaches_profile_and_raises_gate(tmp_path: Path) -> None:
    """The end-to-end path: a `.aidoc/profile.yaml` audit_threshold reaches the gate
    through `_dispatch` → ProjectContext → validate_score. A regression that broke
    the wiring (profile unreachable) would leave `passed=True` here even though the
    validate_score unit tests above still pass."""
    from mcp_server.tool_registry import _dispatch

    project = tmp_path / "proj"
    (project / ".aidoc").mkdir(parents=True)
    (project / ".aidoc" / "profile.yaml").write_text(
        "audit_threshold:\n  BRD: 95\n", encoding="utf-8"
    )
    report = project / "brd_report.json"
    _write_report(report, doc_type="brd", warnings=2)  # score 90

    # with project → profile raises the gate to 95 → 90 < 95 → fails
    with_project = _run(
        _dispatch(
            "sdd_score_validate",
            {"report_file": str(report), "threshold": 80, "project": str(project)},
        )
    )
    assert with_project["threshold"] == 95
    assert with_project["threshold_source"] == "profile"
    assert with_project["passed"] is False

    # without project → ctx is None → gate unchanged → passes
    without_project = _run(
        _dispatch("sdd_score_validate", {"report_file": str(report), "threshold": 80})
    )
    assert without_project["threshold"] == 80
    assert without_project["passed"] is True
