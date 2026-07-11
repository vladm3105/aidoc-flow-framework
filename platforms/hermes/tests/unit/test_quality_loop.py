"""HERMES-REVIEW-LOOP-001 (H-7) — the outer review->remediate->re-review loop."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from mcp_server.review import quality_loop as ql  # noqa: E402
from mcp_server.review.saga_models import deterministic_review_run_id  # noqa: E402
from mcp_server.review.saga_orchestrator import _quality_gate_passed  # noqa: E402


@pytest.fixture(autouse=True)
def _restore_event_loop():
    """`_apply_remediation` calls `asyncio.run` (safe in prod — it runs in a worker
    thread via `asyncio.to_thread`). These unit tests drive the loop on the main thread,
    so `asyncio.run` closes + unsets the main event loop; restore a fresh one after each
    test so downstream suites using the deprecated `get_event_loop()` are not polluted."""
    yield
    asyncio.set_event_loop(asyncio.new_event_loop())


# ── LB-7: per-iteration journal discriminator ────────────────────────────────


def test_run_id_iteration_1_is_unchanged() -> None:
    base = deterministic_review_run_id(
        document_path="/p", document_fingerprint="brd:1:5", personas=["a"], time_bucket="2026070100"
    )
    with_iter1 = deterministic_review_run_id(
        document_path="/p",
        document_fingerprint="brd:1:5",
        personas=["a"],
        time_bucket="2026070100",
        iteration=1,
    )
    assert base == with_iter1  # default/iteration-1 stays byte-identical


def test_run_id_iterations_are_distinct() -> None:
    kw = dict(
        document_path="/p", document_fingerprint="brd:1:5", personas=["a"], time_bucket="2026070100"
    )
    ids = {deterministic_review_run_id(**kw, iteration=n) for n in (1, 2, 3)}
    assert len(ids) == 3  # each pass gets a distinct journal id


# ── the quality gate ─────────────────────────────────────────────────────────


def test_gate_none_score_passes() -> None:
    # deterministic / prompt_only path (no numeric score) → PASS → safe single pass
    assert _quality_gate_passed(None) is True
    assert _quality_gate_passed({}) is True


def test_gate_pass_requires_score_and_no_blocking() -> None:
    assert _quality_gate_passed({"score": 92, "gate_threshold": 90, "no_blocking": True}) is True
    # below threshold
    assert _quality_gate_passed({"score": 85, "gate_threshold": 90, "no_blocking": True}) is False
    # at threshold but unresolved P0/P1
    assert _quality_gate_passed({"score": 95, "gate_threshold": 90, "no_blocking": False}) is False


# ── the wrapper control flow (saga + remediation mocked) ──────────────────────


def _fake_result(passed: bool, status: str = "CLOSED") -> SimpleNamespace:
    return SimpleNamespace(
        passed=passed,
        saga_status=status,
        reduced_findings=[{"priority": "P1", "message": "x", "recommended_action": "y"}],
    )


def _install_saga(monkeypatch, outcomes):
    """Replace the saga with one returning `outcomes[i]` per call; record call kwargs."""
    calls: list[dict] = []

    def fake_saga(**kwargs):
        calls.append(kwargs)
        passed, status = outcomes[len(calls) - 1]
        return _fake_result(passed, status)

    monkeypatch.setattr(ql, "run_project_review_build_saga", fake_saga)
    return calls


def _install_remediation(monkeypatch, tmp_path, produce=True):
    """Replace _apply_remediation with one writing a fresh derived copy (or none)."""
    counter = {"n": 0}

    def fake_apply(**kwargs):
        counter["n"] += 1
        if not produce:
            return []
        p = tmp_path / f"doc_remediate_v{counter['n']}.md"
        p.write_text(f"remediated {counter['n']}", encoding="utf-8")
        return [p]

    monkeypatch.setattr(ql, "_apply_remediation", fake_apply)
    return counter


def _run(tmp_path, max_iterations):
    return ql.run_review_quality_loop(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=tmp_path / "doc.md",
        sections=[],
        output_dir=tmp_path,
        executor_name="api/test",
        max_iterations=max_iterations,
    )


def test_pass_on_first_iteration_no_remediation(tmp_path, monkeypatch) -> None:
    calls = _install_saga(monkeypatch, [(True, "CLOSED")])
    rem = _install_remediation(monkeypatch, tmp_path)
    result = _run(tmp_path, max_iterations=3)
    assert result.passed is True
    assert len(calls) == 1  # one review pass
    assert rem["n"] == 0  # no remediation on a first-pass PASS


def test_fail_then_remediate_then_pass(tmp_path, monkeypatch) -> None:
    calls = _install_saga(monkeypatch, [(False, "CLOSED"), (True, "CLOSED")])
    rem = _install_remediation(monkeypatch, tmp_path)
    result = _run(tmp_path, max_iterations=3)
    assert result.passed is True
    assert len(calls) == 2  # review, re-review
    assert rem["n"] == 1  # one remediation between them
    assert calls[0]["is_final_iteration"] is False
    assert calls[1]["iteration"] == 2


def test_caps_at_max_iterations(tmp_path, monkeypatch) -> None:
    calls = _install_saga(monkeypatch, [(False, "CLOSED"), (False, "PARTIAL_TIMEOUT")])
    _install_remediation(monkeypatch, tmp_path)
    result = _run(tmp_path, max_iterations=2)
    assert len(calls) == 2
    assert calls[0]["is_final_iteration"] is False
    assert calls[1]["is_final_iteration"] is True  # final iteration → saga writes PARTIAL_TIMEOUT
    assert result.saga_status == "PARTIAL_TIMEOUT"


def test_no_derived_copy_stops_loop(tmp_path, monkeypatch) -> None:
    calls = _install_saga(monkeypatch, [(False, "CLOSED"), (False, "CLOSED")])
    _install_remediation(monkeypatch, tmp_path, produce=False)
    result = _run(tmp_path, max_iterations=3)
    assert len(calls) == 1  # remediation produced nothing → stop after the first review
    assert result.passed is False


def test_quality_loop_true_threaded_to_saga(tmp_path, monkeypatch) -> None:
    calls = _install_saga(monkeypatch, [(True, "CLOSED")])
    _install_remediation(monkeypatch, tmp_path)
    _run(tmp_path, max_iterations=3)
    assert calls[0]["quality_loop"] is True
    assert calls[0]["iteration"] == 1


# ── review-surfaced fixes ────────────────────────────────────────────────────


def test_gate_findings_reach_the_fixer_prompt() -> None:
    # Finding 1: the gate-failing findings must be rendered into the executor fix prompt,
    # not only the deterministic structural checks.
    block = ql._render_review_findings(
        [
            {
                "priority": "P0",
                "target_layer": "01_BRD",
                "message": "Missing NFR",
                "recommended_action": "Add a latency NFR",
            },
            {"priority": "P1", "category": "traceability", "message": "Orphan FR"},
        ]
    )
    assert "P0" in block and "Missing NFR" in block
    assert "Add a latency NFR" in block
    assert "P1" in block and "Orphan FR" in block
    # empty / None → no block (deterministic path unaffected)
    assert ql._render_review_findings(None) == ""
    assert ql._render_review_findings([]) == ""


def test_executor_failure_stops_loop(tmp_path, monkeypatch) -> None:
    # Finding B: a failed executor apply must not be silently re-reviewed — the loop
    # stops (gate unmet) rather than burning iterations on unchanged content.
    from types import SimpleNamespace as NS

    calls = _install_saga(monkeypatch, [(False, "CLOSED"), (True, "CLOSED")])

    def fake_run_remediation_build(**kwargs):
        return NS(report_path=tmp_path / "rem.json")

    def fake_run_remediate_fix_build(**kwargs):
        p = tmp_path / "doc_remediate_v1.md"
        p.write_text("copy", encoding="utf-8")
        return NS(report_text="fix me", derived_paths=[p])

    async def fake_run_executor(**kwargs):
        return NS(exit_code=1, stdout="", stderr="boom", executor_name="api/test")

    monkeypatch.setattr(ql, "run_remediation_build", fake_run_remediation_build)
    monkeypatch.setattr(ql, "run_remediate_fix_build", fake_run_remediate_fix_build)
    monkeypatch.setattr(ql, "run_executor", fake_run_executor)

    result = _run(tmp_path, max_iterations=3)
    assert len(calls) == 1  # failed apply → stop after the first review
    assert result.passed is False


def test_executor_success_continues_loop(tmp_path, monkeypatch) -> None:
    # Mirror of the above with exit_code 0 → the loop proceeds to re-review.
    from types import SimpleNamespace as NS

    calls = _install_saga(monkeypatch, [(False, "CLOSED"), (True, "CLOSED")])
    captured = {}

    def fake_run_remediation_build(**kwargs):
        return NS(report_path=tmp_path / "rem.json")

    def fake_run_remediate_fix_build(**kwargs):
        p = tmp_path / "doc_remediate_v1.md"
        p.write_text("copy", encoding="utf-8")
        return NS(report_text="fix me", derived_paths=[p])

    async def fake_run_executor(**kwargs):
        captured["prompt"] = kwargs.get("prompt")
        return NS(exit_code=0, stdout="", stderr="", executor_name="api/test")

    monkeypatch.setattr(ql, "run_remediation_build", fake_run_remediation_build)
    monkeypatch.setattr(ql, "run_remediate_fix_build", fake_run_remediate_fix_build)
    monkeypatch.setattr(ql, "run_executor", fake_run_executor)

    result = _run(tmp_path, max_iterations=3)
    assert len(calls) == 2  # remediation succeeded → re-review
    assert result.passed is True
    assert "fix me" in captured["prompt"]  # fix prompt carried through


def test_no_document_path_stops_loop(tmp_path, monkeypatch) -> None:
    # Finding 3: a purely section-based review (document_path=None) that fails the gate
    # cannot be file-remediated → stop, do not remediate the output directory.
    calls = _install_saga(monkeypatch, [(False, "CLOSED"), (True, "CLOSED")])
    rem = _install_remediation(monkeypatch, tmp_path)
    result = ql.run_review_quality_loop(
        project_root=tmp_path,
        doc_type="brd",
        layer="01_BRD",
        document_path=None,
        sections=[],
        output_dir=tmp_path,
        executor_name="api/test",
        max_iterations=3,
    )
    assert len(calls) == 1  # stopped, no remediation attempted
    assert rem["n"] == 0
    assert result.passed is False
