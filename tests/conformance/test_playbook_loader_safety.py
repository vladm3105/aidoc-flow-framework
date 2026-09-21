"""Conformance: playbook reads stay confined to the playbook root (RETIRED).

CLEANUP-001 Decision 6: ``tools/playbook_loader.py`` was deleted with ``tools/``
(deliberate — the framework-only repo has no loader subject). The traversal,
symlink-escape, null-byte, empty-segment and validated-path-identity guards above
were the live contract for that module; they move with it. Per R4 the guards are
NOT weakened to go green — they are retired with their subject, and this tripwire
fails if ``tools/`` returns without them.

The framework-side playbook contract (frontmatter pins, layer README presence)
lives in the playbook-manifest conformance tests, not here.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


class RetiredPlaybookLoaderSafety(unittest.TestCase):
    """Tripwire: ``tools/`` is gone, so the loader guards have no subject."""

    def test_tools_are_gone(self) -> None:
        self.assertFalse(
            (_REPO_ROOT / "tools").exists(),
            "tools/ is back — resurrect test_playbook_loader_safety with playbook_loader",
        )

    def test_playbooks_still_exist_as_data(self) -> None:
        # The playbooks remain framework data (not code) — the loader's absence
        # must not be misread as the playbooks' absence.
        self.assertTrue(
            (_REPO_ROOT / "framework" / "playbooks").is_dir(),
            "framework/playbooks/ is missing — that is a spec-structure defect, not a loader retirement",
        )


if __name__ == "__main__":
    unittest.main()
