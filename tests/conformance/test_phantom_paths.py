"""Phantom-path guard (#697).

`GOVERNANCE_RULES.md` never existed in this tree (and was formally rejected
as a framework file), yet six live pointers cited it — including a MANDATORY
PROCESS GATE agents are told to complete. The pointers now resolve to
`DOC_GOVERNANCE_CORE.md`; this guard fails if the phantom filename ever
reappears in a live normative surface.

Scope is deliberately narrow: history keeps its mentions. `plans/` holds
working plans, `framework/archive/**` is frozen, and `DECISIONS.md` /
changelogs record what was once believed (e.g. a consumer project's file in
`DECISIONS.md`). A repo-wide "every backticked .md resolves" check measured
56 files with dangling shorthand, placeholders, and consumer-side paths —
that is a separate cleanup, not this guard.
"""

import unittest

from _spec import REPO_ROOT

SCANNED_ROOTS = (
    REPO_ROOT / "framework",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "GOVERNANCE.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "CLAUDE.md",
)

# History keeps its mentions: frozen archive, decision/changelog records,
# and working plans are not normative pointers.
SKIP_PARTS = ("/archive/",)
SKIP_NAMES = ("DECISIONS.md", "CHANGELOG.md", "CHANGELOG_old.md")


def _live_markdown_files():
    files = []
    for root in SCANNED_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        for path in sorted(root.rglob("*.md")):
            text = str(path)
            if any(part in text for part in SKIP_PARTS):
                continue
            if path.name in SKIP_NAMES:
                continue
            files.append(path)
    return files


class PhantomPathGuard(unittest.TestCase):
    def test_no_governance_rules_phantom(self):
        """No live surface cites the never-existent GOVERNANCE_RULES.md (#697)."""
        offenders = []
        for path in _live_markdown_files():
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if "GOVERNANCE_RULES" in text:
                offenders.append(str(path.relative_to(REPO_ROOT)))
        self.assertEqual(
            offenders,
            [],
            "phantom GOVERNANCE_RULES.md cited — repoint at DOC_GOVERNANCE_CORE.md",
        )
