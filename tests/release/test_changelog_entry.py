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

    def test_changelog_has_entry_for_current_version(self):
        if not CHANGELOG.exists():
            self.skipTest("CHANGELOG.md not present")
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        changelog = CHANGELOG.read_text(encoding="utf-8")
        # The current version's entry may appear in either form (RELEASE-CHANGELOG-
        # TEST-CONVENTION-GAP):
        #   * a released top-level heading — ``## [0.30.0]`` / ``## 0.30.0``; or
        #   * an ``## [Unreleased]`` subsection heading naming the version, the
        #     convention this repo uses — ``### Added — … framework spec X → 0.30.0``.
        # Match the version in any level-2/3 heading line, not just a bracketed
        # top-level one. The trailing lookahead avoids a prefix match (0.30.0 in
        # 0.30.01).
        pattern = rf"^#{{2,3}}\s+.*{re.escape(version)}(?![\d.])"
        self.assertRegex(
            changelog,
            re.compile(pattern, re.MULTILINE),
            f"CHANGELOG.md has no heading naming the current version {version} "
            f"(neither a released '## [{version}]' nor an '[Unreleased]' '### … {version}' entry)",
        )

    def test_no_placeholder_orphans(self):
        if not CHANGELOG.exists():
            self.skipTest("CHANGELOG.md not present")
        changelog = CHANGELOG.read_text(encoding="utf-8")
        for token in ["TBD", "TODO:", "FILL IN"]:
            self.assertNotIn(token, changelog, f"CHANGELOG contains placeholder {token!r}")
