"""Conformance: saga_driver.py honors REVIEW_SAGA.md state machine.

Unit tests for the saga driver's preemptive state-machine logic. Does not
spawn live subprocesses; the live cascade exercises that separately.

Source authority: framework/governance/REVIEW_SAGA.md (transition table)
and framework/governance/REVIEW_CREWS.yaml (per-layer crews).

Per SAGA-PARITY-001 Phase 2 Amendment 1.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "tools"))
import saga_driver  # noqa: E402  (path injection above is intentional)


class TransitionTable(unittest.TestCase):
    """The driver's _ALLOWED_TRANSITIONS table must mirror REVIEW_SAGA.md."""

    def test_driver_has_all_eleven_spec_states(self):
        self.assertEqual(
            set(saga_driver._ALLOWED_TRANSITIONS),
            {
                "PREPARED",
                "FANOUT_STARTED",
                "BRANCH_RUNNING",
                "BRANCH_COMPLETED",
                "BRANCH_FAILED",
                "BRANCH_COMPENSATING",
                "FANIN_REDUCED",
                "SYNTHESIZED",
                "ESCALATED",
                "CLOSED",
                "PARTIAL_TIMEOUT",
            },
        )

    def test_partial_timeout_is_terminal(self):
        """G-R1: PARTIAL_TIMEOUT has no allowed-next transitions."""
        self.assertEqual(saga_driver._ALLOWED_TRANSITIONS["PARTIAL_TIMEOUT"], set())

    def test_closed_is_terminal(self):
        self.assertEqual(saga_driver._ALLOWED_TRANSITIONS["CLOSED"], set())

    def test_escalated_is_terminal(self):
        self.assertEqual(saga_driver._ALLOWED_TRANSITIONS["ESCALATED"], set())

    def test_invalid_transition_raises(self):
        saga = {"status": "PREPARED", "transitions": [], "updated_at": ""}
        with self.assertRaises(ValueError):
            saga_driver.append_transition(saga, from_state="PREPARED", to_state="CLOSED")

    def test_valid_transition_succeeds(self):
        saga = {"status": "PREPARED", "transitions": [], "updated_at": ""}
        saga_driver.append_transition(saga, from_state="PREPARED", to_state="FANOUT_STARTED")
        self.assertEqual(len(saga["transitions"]), 1)
        self.assertEqual(saga["transitions"][0]["from"], "PREPARED")
        self.assertEqual(saga["transitions"][0]["to"], "FANOUT_STARTED")


class ResumeLogic(unittest.TestCase):
    """G-R1: never write `from: PARTIAL_TIMEOUT` — walk transitions[]
    backward to find the resume point."""

    def test_resume_walks_back_from_partial_timeout(self):
        saga = {
            "status": "PARTIAL_TIMEOUT",
            "transitions": [
                {"from": None, "to": "PREPARED"},
                {"from": "PREPARED", "to": "FANOUT_STARTED"},
                {"from": "FANOUT_STARTED", "to": "BRANCH_RUNNING"},
                {"from": "BRANCH_RUNNING", "to": "PARTIAL_TIMEOUT"},
            ],
        }
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "BRANCH_RUNNING")

    def test_resume_no_op_when_not_partial_timeout(self):
        saga = {"status": "FANOUT_STARTED", "transitions": []}
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "FANOUT_STARTED")

    def test_resume_falls_back_to_prepared_if_no_non_pt_entries(self):
        saga = {
            "status": "PARTIAL_TIMEOUT",
            "transitions": [{"from": None, "to": "PARTIAL_TIMEOUT"}],
        }
        saga_driver.resume_from_partial_timeout(saga)
        self.assertEqual(saga["status"], "PREPARED")


class LayerCrewsMatchYaml(unittest.TestCase):
    """Pass-4 A7: assert saga_driver._LAYER_CREWS matches
    framework/governance/REVIEW_CREWS.yaml so drift is caught in CI."""

    def test_layer_crews_match_yaml(self):
        import yaml  # PyYAML — already required by test_review_team.py

        crews_path = _REPO_ROOT / "framework" / "governance" / "REVIEW_CREWS.yaml"
        data = yaml.safe_load(crews_path.read_text())
        layer_order = ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"]
        for i, layer in enumerate(layer_order):
            spec_layer = f"{i + 1:02d}_{layer}"
            expected_crew = set(data["crews"][layer]["review"].keys())
            driver_crew = set(saga_driver._LAYER_CREWS[spec_layer])
            self.assertEqual(
                driver_crew,
                expected_crew,
                f"saga_driver._LAYER_CREWS[{spec_layer!r}] drifted from "
                f"REVIEW_CREWS.yaml: driver={driver_crew} "
                f"yaml={expected_crew}",
            )


if __name__ == "__main__":
    unittest.main()
