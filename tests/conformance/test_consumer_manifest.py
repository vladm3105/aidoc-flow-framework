"""Consumer-copy manifest guard (#834).

`docs/PROJECT.md` §7.1 defines the new-project copy as an allowlist: `cp -r`
exactly `{framework,docs,hooks,sdd_doc_lint,tests}`, then prune
`framework/archive` inside the copy. The previous clone-then-denylist
procedure silently shipped canon-dev internals (`.agents/`, `.aidoc/`,
`plans/`, 4.2 MB of frozen `framework/archive/`) into every consumer tree.

This guard locks the contract from the doc side: the copy set parsed from
§7.1 must equal the expected allowlist, every shipped path must exist, the
archive prune must stay documented, and the known-internal paths must stay
out of the shipped set. Changing the consumer set intentionally means
updating the doc AND this manifest together.
"""

import re
import unittest

from _spec import REPO_ROOT

PROJECT_DOC = REPO_ROOT / "docs" / "PROJECT.md"

# The consumer allowlist. Must match the `cp -r .../{...}` line in §7.1.
EXPECTED_SHIP = ("framework", "docs", "hooks", "sdd_doc_lint", "tests")

# Canon-dev paths the reported leak shipped. Top-level entries must stay out
# of the copy set; framework/archive is pruned inside the copy (see below).
KNOWN_INTERNAL_TOP = (".agents", ".aidoc", ".github", "plans")

# Exact prune line §7.1 must carry for the frozen history inside framework/.
ARCHIVE_PRUNE_LINE = "rm -rf .aidoc/framework/framework/archive"


def _doc_text():
    return PROJECT_DOC.read_text(encoding="utf-8")


# Files whose ASCII trees must agree with the installer: stack-policy.yaml
# lives at project root (#1042, regression remainder of #1022/CHG-128).
SCAFFOLD_TEMPLATE = (
    REPO_ROOT / "framework" / "governance" / "aidoc" / "AIDOC-SCAFFOLD-TEMPLATE.md"
)
AIDOC_DOC = REPO_ROOT / "framework" / "governance" / "aidoc" / "AIDOC.md"
PARITY_DOCS = (SCAFFOLD_TEMPLATE, AIDOC_DOC)
INSTALL_SCRIPT = REPO_ROOT / "framework" / "scripts" / "install.sh"

# One tree level is 4 characters: `│   `, `    `, `├── `, or `└── `.
_BRANCH_RE = re.compile(r"^(?:\u2502   |    |\u251c\u2500\u2500 |\u2514\u2500\u2500 )+")


def _stack_policy_placements(text):
    """Yield (lineno, line, under_aidoc) for tree-drawn stack-policy.yaml lines.

    Parses ```text fences as 4-char-per-level trees, tracking ancestor
    directories on a depth stack. Only lines inside fences are considered,
    so prose mentions of stack-policy.yaml never trip the guard.
    """
    in_fence = False
    stack = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            if not in_fence and stripped.startswith("```text"):
                in_fence = True
                stack = []
            else:
                in_fence = False
            continue
        if not in_fence or not stripped:
            continue
        match = _BRANCH_RE.match(raw)
        if match:
            depth = len(match.group(0)) // 4
            name = raw[match.end():]
        else:
            depth = 0
            name = stripped
        first = name.split()[0] if name.split() else ""
        if not first or first == "...":
            continue
        stack = stack[:depth]
        if first.startswith("stack-policy.yaml"):
            yield lineno, raw.rstrip(), any(s.startswith(".aidoc/") for s in stack)
        if first.endswith("/"):
            stack.append(first)


def _ship_from_doc(text):
    match = re.search(r"cp -r /tmp/aidoc-framework/\{([^}]*)\} \.aidoc/framework/", text)
    assert match is not None, (
        "docs/PROJECT.md §7.1 must carry the allowlist copy line "
        "`cp -r /tmp/aidoc-framework/{...} .aidoc/framework/`"
    )
    return tuple(match.group(1).split(","))


class ConsumerManifest(unittest.TestCase):
    def test_ship_set_matches_contract(self):
        """§7.1 copy set is exactly the consumer allowlist (#834)."""
        self.assertEqual(_ship_from_doc(_doc_text()), EXPECTED_SHIP)

    def test_ship_paths_exist(self):
        """Every allowlisted path exists at the repo root."""
        for name in EXPECTED_SHIP:
            self.assertTrue((REPO_ROOT / name).is_dir(), f"allowlisted path missing: {name}")

    def test_internal_paths_not_shipped(self):
        """Known canon-dev internals stay out of the copy set (#834)."""
        ship = set(_ship_from_doc(_doc_text()))
        for name in KNOWN_INTERNAL_TOP:
            self.assertNotIn(name, ship, f"canon-dev path would ship: {name}")
        for name in ("CONTRIBUTING.md", "CHANGELOG.md"):
            self.assertNotIn(name, ship, f"canon-dev doc would ship: {name}")

    def test_archive_prune_documented(self):
        """§7.1 prunes the frozen history inside the copy (#834)."""
        self.assertIn(ARCHIVE_PRUNE_LINE, _doc_text())
        self.assertTrue(
            (REPO_ROOT / "framework" / "archive").is_dir(),
            "prune target framework/archive/ is gone; drop the prune line",
        )

    def test_upgrade_inputs_shipped(self):
        """Upgrade inputs stay inside the shipped framework/ tree."""
        for name in ("VERSION", "CHANGELOG.md"):
            self.assertTrue(
                (REPO_ROOT / "framework" / name).is_file(),
                f"upgrade input missing from shipped tree: framework/{name}",
            )


class ScaffoldStackPolicyParity(unittest.TestCase):
    def test_no_aidoc_nested_stack_policy(self):
        """No tree draws stack-policy.yaml under .aidoc/ (#1042)."""
        bad = []
        for doc in PARITY_DOCS:
            for lineno, line, under_aidoc in _stack_policy_placements(
                doc.read_text(encoding="utf-8")
            ):
                if under_aidoc:
                    bad.append(f"{doc.name}:{lineno}: {line.strip()}")
        self.assertEqual(bad, [], "stack-policy.yaml drawn under .aidoc/")

    def test_root_stack_policy_drawn(self):
        """The template still draws a root stack-policy.yaml (anti-vacuity)."""
        found = [
            (lineno, under_aidoc)
            for lineno, _, under_aidoc in _stack_policy_placements(
                SCAFFOLD_TEMPLATE.read_text(encoding="utf-8")
            )
        ]
        self.assertTrue(found, "template draws no stack-policy.yaml at all")
        self.assertTrue(
            any(not under_aidoc for _, under_aidoc in found),
            "template draws stack-policy.yaml only under .aidoc/",
        )

    def test_installer_scaffolds_root(self):
        """install.sh scaffolds $PROJECT/stack-policy.yaml (#1042)."""
        self.assertIn(
            'policy_doc="$PROJECT/stack-policy.yaml"',
            INSTALL_SCRIPT.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main()
