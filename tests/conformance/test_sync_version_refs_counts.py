"""#405: the `replace_in_file_counted` expected counts in
`scripts/sync-version-refs.sh` must match the tree.

The count guard refuses a substitution when a file holds MORE occurrences of a
swept literal than expected, on the theory that the surplus is a historical
mention. That makes each `expected` a claim about the repository, maintained by
hand, whose only previous guard was a comment saying "update this when you add
or remove a current-state row".

Both directions of drift are silent and both are bad:

* Expected too LOW (someone adds a legitimate current-state row): the next bump
  skips that file entirely and its version goes stale — a state the *unguarded*
  script handled correctly, so the guard would have made things worse.
* Expected too HIGH (someone removes a row): the guard stops guarding, and the
  historical-mention corruption #405 was filed about is silently re-enabled.

Neither is detectable by running the script, because both look like a normal
run. This test reads the call sites out of the script and counts for real.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "sync-version-refs.sh"

# `<literal template>` -> the VERSION file supplying the value it interpolates.
_VERSION_SOURCES = {
    "fw_prev": _REPO_ROOT / "framework" / "VERSION",
    "plugin_prev": _REPO_ROOT / "platforms" / "claude-code-plugin" / "VERSION",
    "hermes_prev": _REPO_ROOT / "platforms" / "hermes" / "VERSION",
}

# replace_in_file_counted <path> \
#   "<old literal>" "<new literal>" <expected>
_CALL = re.compile(
    r"replace_in_file_counted\s+(?P<path>\S+)\s*\\\s*\n"
    r"\s*\"(?P<old>[^\"]+)\"\s+\"[^\"]+\"\s+(?P<expected>\d+)",
    re.MULTILINE,
)


def _read_version(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _resolve(template: str) -> tuple[str, str] | None:
    """Turn a shell literal into the string that is in the tree right now.

    The script sweeps `<old>` = the PREVIOUS version, so at rest the tree holds
    the CURRENT one. Substituting the current version is therefore what makes
    the occurrence count meaningful between bumps.
    """
    for var, version_file in _VERSION_SOURCES.items():
        if f"${var}" in template:
            if not version_file.is_file():
                return None
            literal = template.replace(f"${var}", _read_version(version_file))
            # In a double-quoted shell string, \` is a literal backtick.
            return literal.replace("\\`", "`"), var
    return None


class SyncVersionRefsExpectedCounts(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(_SCRIPT.is_file(), f"{_SCRIPT} missing")
        self.source = _SCRIPT.read_text(encoding="utf-8")
        self.calls = list(_CALL.finditer(self.source))

    def test_the_parser_finds_the_call_sites(self):
        """Guard against vacuity: if the script is reformatted so the regex stops
        matching, every other assertion here passes over an empty list."""
        self.assertGreaterEqual(
            len(self.calls),
            11,
            f"found {len(self.calls)} replace_in_file_counted call sites; the "
            "#405 fix converted the plugin (3) and hermes (3) tag fanouts and "
            "the framework-spec fanout (5). A lower number means the regex "
            "stopped matching, not that the guard shrank — check the "
            "call-site formatting.",
        )

    def test_every_expected_count_matches_the_tree(self):
        for m in self.calls:
            path, template, expected = (
                m.group("path"),
                m.group("old"),
                int(m.group("expected")),
            )
            with self.subTest(file=path, literal=template):
                resolved = _resolve(template)
                self.assertIsNotNone(
                    resolved,
                    f"could not resolve {template!r} to a current version — the "
                    "literal interpolates no known *_prev variable",
                )
                literal, _var = resolved
                target = _REPO_ROOT / path
                if not target.is_file():
                    # A target may legitimately be absent in a partial checkout.
                    continue
                actual = target.read_text(encoding="utf-8").count(literal)
                self.assertEqual(
                    actual,
                    expected,
                    f"{path} holds {actual} occurrence(s) of {literal!r} but "
                    f"sync-version-refs.sh expects {expected}. If you added or "
                    f"removed a current-state row, update the call site in the "
                    f"same change; if the surplus is a historical mention, "
                    f"reword it out of the swept literal form instead.",
                )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
