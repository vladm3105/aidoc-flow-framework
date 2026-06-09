"""Unit: saga driver reconciles transitions[] + status when SKILL skipped stamping.

Surfaced by SPEC-RT-001 live cascade (2026-06-09): the audit SKILL's
prompt asks the LLM to do TWO writes per branch event — update
`branches[<lens>]` and append a transition entry — and the LLM
stochastically skipped the second write while doing the first. Result:
branches dict said all 5 lenses were `BRANCH_COMPLETED` but transitions[]
held only 2 entries (`None → PREPARED` and `PREPARED → FANOUT_STARTED`),
saga.status stuck at `FANOUT_STARTED`, harness B2 reported `FAIL`
despite verdict.json `combined_status: PASS`.

`reconcile_post_audit(ctx, saga)` deterministically backfills the
missing per-branch transitions from branches[] state and advances
saga.status FANOUT_STARTED → BRANCH_RUNNING → BRANCH_COMPLETED at run
scope. The existing post-audit PASS code path can then fire its
allowed BRANCH_COMPLETED → FANIN_REDUCED transition correctly.

Fixture `fixtures/saga-reconcile/saga-skill-skipped-transitions.json` is
the verbatim captured saga.json from the SPEC-RT-001 worktree cascade
run that exposed the bug.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from saga_driver import SagaContext, reconcile_post_audit  # noqa: E402

# `reconcile_post_audit` reads `saga.branches[]` and `saga.transitions[]`
# from the in-memory dict — it never touches the filesystem. The paths
# below are dummy values to satisfy `SagaContext`'s dataclass; the test
# does not depend on their existence.
_TMPDIR = Path(tempfile.gettempdir())


def _ctx(layer: str = "06_SPEC") -> SagaContext:
    return SagaContext(
        layer=layer,
        layer_type=layer.split("_", 1)[1],
        artifact_id=f"{layer.split('_', 1)[1]}-01",
        artifact_path=_TMPDIR / "nonexistent.md",
        saga_dir=_TMPDIR,
        saga_file=_TMPDIR / "saga.json",
    )


def _branch(status: str, started_at: str = "2026-06-09T16:30:00+00:00") -> dict:
    return {
        "branch_id": "abc123",
        "status": status,
        "attempt": 0,
        "started_at": started_at,
        "ended_at": "2026-06-09T16:40:00+00:00",
    }


class ReconcilePostAuditTests(unittest.TestCase):
    """The reconcile helper backfills missing per-branch transitions and
    advances saga.status when branches[] is the ground truth."""

    def test_backfills_missing_branch_transitions(self):
        """SKILL skipped per-branch transitions; reconcile adds them."""
        saga = {
            "status": "FANOUT_STARTED",
            "iteration": 1,
            "current_phase": "review",
            "branches": {
                "architect": _branch("BRANCH_COMPLETED"),
                "tech_lead": _branch("BRANCH_COMPLETED"),
            },
            "transitions": [
                {"ts": "2026-06-09T16:18:24+00:00", "from": None, "to": "PREPARED", "scope": "run"},
                {
                    "ts": "2026-06-09T16:29:00+00:00",
                    "from": "PREPARED",
                    "to": "FANOUT_STARTED",
                    "scope": "run",
                },
            ],
        }
        reconcile_post_audit(_ctx(), saga)

        branch_transitions = [t for t in saga["transitions"] if t["scope"].startswith("branch:")]
        # 2 lenses × 2 transitions each (FANOUT_STARTED→BRANCH_RUNNING, then →BRANCH_COMPLETED)
        self.assertEqual(len(branch_transitions), 4)
        # All backfilled transitions are marked
        for t in branch_transitions:
            self.assertTrue(t.get("reconciled"))

    def test_advances_run_status_when_all_branches_terminal(self):
        """Reconcile walks saga.status FANOUT_STARTED → BRANCH_COMPLETED at run scope."""
        saga = {
            "status": "FANOUT_STARTED",
            "iteration": 1,
            "current_phase": "review",
            "branches": {
                "architect": _branch("BRANCH_COMPLETED"),
                "tech_lead": _branch("BRANCH_COMPLETED"),
            },
            "transitions": [
                {"ts": "2026-06-09T16:18:24+00:00", "from": None, "to": "PREPARED", "scope": "run"},
                {
                    "ts": "2026-06-09T16:29:00+00:00",
                    "from": "PREPARED",
                    "to": "FANOUT_STARTED",
                    "scope": "run",
                },
            ],
        }
        reconcile_post_audit(_ctx(), saga)
        self.assertEqual(saga["status"], "BRANCH_COMPLETED")
        run_transitions = [t for t in saga["transitions"] if t.get("scope") == "run"]
        # Initial 2 + the 2 newly walked (FANOUT_STARTED→BRANCH_RUNNING, BRANCH_RUNNING→BRANCH_COMPLETED)
        self.assertEqual(len(run_transitions), 4)
        self.assertEqual(run_transitions[-1]["to"], "BRANCH_COMPLETED")

    def test_idempotent_when_skill_already_stamped(self):
        """If transitions already complete, reconcile is a no-op (no duplicates)."""
        saga = {
            "status": "BRANCH_COMPLETED",  # SKILL advanced status correctly
            "iteration": 1,
            "current_phase": "review",
            "branches": {
                "architect": _branch("BRANCH_COMPLETED"),
            },
            "transitions": [
                {"ts": "t1", "from": None, "to": "PREPARED", "scope": "run"},
                {"ts": "t2", "from": "PREPARED", "to": "FANOUT_STARTED", "scope": "run"},
                {
                    "ts": "t3",
                    "from": "FANOUT_STARTED",
                    "to": "BRANCH_RUNNING",
                    "scope": "branch:architect",
                },
                {
                    "ts": "t4",
                    "from": "BRANCH_RUNNING",
                    "to": "BRANCH_COMPLETED",
                    "scope": "branch:architect",
                },
            ],
        }
        original_transition_count = len(saga["transitions"])
        reconcile_post_audit(_ctx(), saga)
        # No new transitions added
        self.assertEqual(len(saga["transitions"]), original_transition_count)
        # saga.status unchanged (not FANOUT_STARTED, so the run-walk doesn't fire)
        self.assertEqual(saga["status"], "BRANCH_COMPLETED")

    def test_skill_partial_stamp_completes_remainder(self):
        """SKILL stamped some branches; reconcile fills only the missing ones."""
        saga = {
            "status": "FANOUT_STARTED",
            "iteration": 1,
            "current_phase": "review",
            "branches": {
                "architect": _branch("BRANCH_COMPLETED"),
                "tech_lead": _branch("BRANCH_COMPLETED"),
            },
            "transitions": [
                {"ts": "t1", "from": None, "to": "PREPARED", "scope": "run"},
                {"ts": "t2", "from": "PREPARED", "to": "FANOUT_STARTED", "scope": "run"},
                # SKILL stamped architect's transitions only
                {
                    "ts": "t3",
                    "from": "FANOUT_STARTED",
                    "to": "BRANCH_RUNNING",
                    "scope": "branch:architect",
                },
                {
                    "ts": "t4",
                    "from": "BRANCH_RUNNING",
                    "to": "BRANCH_COMPLETED",
                    "scope": "branch:architect",
                },
            ],
        }
        reconcile_post_audit(_ctx(), saga)
        # Architect transitions preserved (not duplicated); tech_lead backfilled
        archtitect_t = [t for t in saga["transitions"] if t.get("scope") == "branch:architect"]
        tech_lead_t = [t for t in saga["transitions"] if t.get("scope") == "branch:tech_lead"]
        self.assertEqual(len(archtitect_t), 2)  # not duplicated
        self.assertEqual(len(tech_lead_t), 2)  # backfilled
        # Architect's existing transitions should NOT be marked reconciled
        for t in archtitect_t:
            self.assertFalse(t.get("reconciled"))
        # Tech_lead's backfilled ones SHOULD be marked
        for t in tech_lead_t:
            self.assertTrue(t.get("reconciled"))

    def test_does_not_advance_when_branches_still_running(self):
        """If any branch is still BRANCH_RUNNING, saga.status stays at FANOUT_STARTED."""
        saga = {
            "status": "FANOUT_STARTED",
            "iteration": 1,
            "current_phase": "review",
            "branches": {
                "architect": _branch("BRANCH_COMPLETED"),
                "tech_lead": _branch("BRANCH_RUNNING"),  # still running
            },
            "transitions": [
                {"ts": "t1", "from": None, "to": "PREPARED", "scope": "run"},
                {"ts": "t2", "from": "PREPARED", "to": "FANOUT_STARTED", "scope": "run"},
            ],
        }
        reconcile_post_audit(_ctx(), saga)
        self.assertEqual(saga["status"], "FANOUT_STARTED")  # not advanced

    def test_regression_real_spec_rt_001_saga(self):
        """Replay the verbatim broken SPEC-RT-001 saga.json against reconcile.

        Captured 2026-06-09 from worktree cascade run that produced
        verdict.json PASS @ 95 but stuck saga.status at FANOUT_STARTED
        with only 2 transitions stamped.
        """
        fixture_path = (
            REPO_ROOT
            / "tests"
            / "unit"
            / "fixtures"
            / "saga-reconcile"
            / "saga-skill-skipped-transitions.json"
        )
        saga = json.loads(fixture_path.read_text(encoding="utf-8"))
        # Verify the bug shape BEFORE reconciliation
        self.assertEqual(saga["status"], "FANOUT_STARTED")
        self.assertEqual(len(saga["transitions"]), 2)
        self.assertEqual(len(saga["branches"]), 5)
        for lens, branch in saga["branches"].items():
            self.assertEqual(branch["status"], "BRANCH_COMPLETED")

        reconcile_post_audit(_ctx(), saga)

        # After reconciliation: saga.status walked to BRANCH_COMPLETED;
        # 5 lenses × 2 transitions backfilled + 2 new run-scope transitions
        self.assertEqual(saga["status"], "BRANCH_COMPLETED")
        branch_transitions = [t for t in saga["transitions"] if t["scope"].startswith("branch:")]
        self.assertEqual(len(branch_transitions), 10)  # 5 lenses × (RUNNING + COMPLETED)
        run_transitions = [t for t in saga["transitions"] if t.get("scope") == "run"]
        # Originally 2 (None→PREPARED, PREPARED→FANOUT_STARTED) + 2 new
        # (FANOUT_STARTED→BRANCH_RUNNING, BRANCH_RUNNING→BRANCH_COMPLETED)
        self.assertEqual(len(run_transitions), 4)
        self.assertEqual(run_transitions[-1]["to"], "BRANCH_COMPLETED")


if __name__ == "__main__":
    unittest.main()
