"""Conformance: saga_driver.py recovery, disclosure and exit-code contract (RETIRED).

CLEANUP-001 Decisions 5/6: ``tools/saga_driver.py`` was deleted with ``tools/``
(deliberate — the plugin runner is gone). The PLUGIN-PREPROD-001 PR 3 guards
above (B2 opt-in bypass, B3a forced PARTIAL_TIMEOUT, B3b no-clobber, B3c
run-scoped resume, M3 timeout probe, M4 non-zero exit, M5 verdict invalidation,
L2 threshold gate) were the live contract for that driver; they move with it.
Per R4 the guards are NOT weakened to go green — they are retired with their
subject, and this tripwire fails if ``tools/`` returns without them.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


class RetiredSagaDriverRecovery(unittest.TestCase):
    """Tripwire: ``tools/saga_driver.py`` is gone, so the recovery guards have no subject."""

    def test_tools_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "tools").exists(),
            "tools/ is back — resurrect test_saga_driver_recovery with saga_driver",
        )


if __name__ == "__main__":
    unittest.main()
