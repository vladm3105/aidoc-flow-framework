"""Conformance: every ``framework/governance/*.md`` carries a GD-24 Document Control block."""

import re
import unittest

from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"

# GD-24 exempts playbooks, LEARNED_LESSONS, and scripts — none of which live as
# top-level framework/governance/*.md, so every top-level .md is in scope.
# Archive copies (framework/archive/**) are frozen history, not live docs (#706).
REQUIRED_FIELDS = ("Version", "Status", "Last Updated", "Author", "Framework Version")


def _block_of(path):
    match = re.search(r"^## Document Control\s*\n(.*)", path.read_text(), re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


class DocumentControlBlocks(unittest.TestCase):
    def test_every_governance_doc_carries_document_control(self):
        missing = sorted(
            path.name
            for path in GOVERNANCE.glob("*.md")
            if not re.search(r"^## Document Control", path.read_text(), re.MULTILINE)
        )
        self.assertEqual(missing, [], f"GD-24: Document Control block missing in: {missing}")

    def test_blocks_carry_required_fields(self):
        for path in sorted(GOVERNANCE.glob("*.md")):
            block = _block_of(path)
            if not block:
                continue  # owned by test_every_governance_doc_carries_document_control
            for field in REQUIRED_FIELDS:
                with self.subTest(doc=path.name, field=field):
                    self.assertIsNotNone(
                        re.search(rf"^\|\s*{re.escape(field)}\s*\|.+?\|", block, re.MULTILINE),
                        f"{path.name}: no '{field}' row",
                    )

    def test_block_framework_version_matches_current(self):
        # sync-version-refs.sh propagates framework/VERSION into these rows;
        # the pin must never lag the release it ships in.
        current = (FRAMEWORK / "VERSION").read_text().strip()
        for path in sorted(GOVERNANCE.glob("*.md")):
            block = _block_of(path)
            if not block:
                continue  # owned by test_every_governance_doc_carries_document_control
            with self.subTest(doc=path.name):
                match = re.search(
                    r"^\|\s*Framework Version\s*\|\s*(\S+?)\s*\|", block, re.MULTILINE
                )
                self.assertIsNotNone(match, f"{path.name}: no Framework Version row")
                self.assertEqual(match.group(1), current, f"{path.name}")
