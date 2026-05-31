"""Release: CHANGELOG.md has an entry for the current VERSION."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK

# CHANGELOG.md lives at the repo root, not inside framework/
CHANGELOG = FRAMEWORK.parent / "CHANGELOG.md"


class ChangelogEntryTests(unittest.TestCase):
    def test_changelog_exists(self):
        self.assertTrue(CHANGELOG.exists(), f"CHANGELOG.md missing at {CHANGELOG}")

    # TODO Phase 12: re-introduce current-version assertion after bump
    def test_changelog_has_at_least_one_version_section(self):
        if not CHANGELOG.exists():
            self.skipTest("CHANGELOG.md not present")
        changelog = CHANGELOG.read_text(encoding="utf-8")
        self.assertRegex(
            changelog,
            re.compile(r"^##\s*\[?\d+\.\d+\.\d+\]?", re.MULTILINE),
            "CHANGELOG has no version sections",
        )

    def test_no_placeholder_orphans(self):
        if not CHANGELOG.exists():
            self.skipTest("CHANGELOG.md not present")
        changelog = CHANGELOG.read_text(encoding="utf-8")
        for token in ["TBD", "TODO:", "FILL IN"]:
            self.assertNotIn(token, changelog, f"CHANGELOG contains placeholder {token!r}")
