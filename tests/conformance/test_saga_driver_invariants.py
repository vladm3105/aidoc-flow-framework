"""Conformance: saga state machine honors REVIEW_SAGA.md (RETIRED).

CLEANUP-001 Decisions 5/6: ``tools/saga_driver.py`` was deleted with ``tools/``
(deliberate — the plugin runner is gone) and ``platforms/hermes`` with
``platforms/``. The eleven-state transition table, terminal-state, append,
resume-walk (G-R1) and ``_LAYER_CREWS``-vs-``REVIEW_CREWS.yaml`` guards above
were the live contract for those drivers; they move with them. Per R4 the guards
are NOT weakened to go green — they are retired with their subjects, and this
tripwire fails if ``tools/`` or ``platforms/`` returns without them.

The framework-side saga contract — ``REVIEW_SAGA.md`` transition prose,
``saga.schema.json`` status enum, and the ``SPEC_TRANSITIONS`` hard-coded pin —
lives in ``test_saga_lifecycle_parity.py``, which stays framework-only.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


class RetiredSagaDriverInvariants(unittest.TestCase):
    """Tripwire: the saga drivers are gone, so the table guards have no subject."""

    def test_tools_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "tools").exists(),
            "tools/ is back — resurrect test_saga_driver_invariants with saga_driver",
        )

    def test_platforms_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "platforms").exists(),
            "platforms/ is back — resurrect the Hermes table half with saga_models",
        )

    def test_saga_spec_prose_survives(self) -> None:
        # The spec authority remains framework data — the drivers' absence must
        # not be misread as the state machine's absence.
        self.assertTrue(
            (_REPO_ROOT / "framework" / "governance" / "REVIEW_SAGA.md").is_file(),
            "framework/governance/REVIEW_SAGA.md is missing — that is a spec defect, not a driver retirement",
        )


if __name__ == "__main__":
    unittest.main()
