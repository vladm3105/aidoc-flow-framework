"""Conformance: the Claude Code plugin's vendored ``framework/`` bundle stays
byte-identical to the canonical ``framework/`` spec (D-0022).

Claude Code copies only the plugin directory to its cache on install, so the
plugin vendors the spec subtrees it consumes (+ the one root doc its skills
cite) and repoints every reference to ``${CLAUDE_PLUGIN_ROOT}/framework/…``.
The monorepo ``framework/`` stays the single source of truth (D-0013); this
guard fails CI if the generated bundle drifts from canonical — the same ethos
as ``test_doc_lint_vendoring.py``.

Re-sync after editing the canonical spec:
    bash tools/sync-plugin-framework.sh
"""

import unittest

from _spec import REPO_ROOT

CANONICAL = REPO_ROOT / "framework"
BUNDLE = REPO_ROOT / "platforms" / "claude-code-plugin" / "framework"

# Must match tools/sync-plugin-framework.sh.
SUBTREES = ("layers", "governance", "registry")
ROOT_FILES = ("SPEC_DRIVEN_DEVELOPMENT_GUIDE.md",)


def _rel_files(base):
    return {p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file()}


class PluginFrameworkBundle(unittest.TestCase):
    def _expected_relpaths(self):
        expected = set(ROOT_FILES)
        for sub in SUBTREES:
            for rel in _rel_files(CANONICAL / sub):
                expected.add(f"{sub}/{rel}")
        return expected

    def test_bundle_exists(self):
        self.assertTrue(
            BUNDLE.is_dir(),
            f"missing vendored framework bundle: {BUNDLE} — run tools/sync-plugin-framework.sh",
        )

    def test_bundle_fileset_matches_canonical(self):
        expected = self._expected_relpaths()
        actual = _rel_files(BUNDLE)
        missing = expected - actual
        extra = actual - expected
        self.assertFalse(
            missing,
            f"vendored bundle missing {len(missing)} file(s): {sorted(missing)[:10]} — "
            "re-run tools/sync-plugin-framework.sh",
        )
        self.assertFalse(
            extra,
            f"vendored bundle has {len(extra)} stale file(s): {sorted(extra)[:10]} — "
            "re-run tools/sync-plugin-framework.sh",
        )

    def test_bundle_is_byte_identical(self):
        for rel in sorted(self._expected_relpaths()):
            with self.subTest(file=rel):
                canon = CANONICAL / rel
                vend = BUNDLE / rel
                self.assertTrue(vend.is_file(), f"missing bundled file: {vend}")
                self.assertEqual(
                    vend.read_bytes(),
                    canon.read_bytes(),
                    f"platforms/claude-code-plugin/framework/{rel} drifted from canonical "
                    "framework/ — re-run tools/sync-plugin-framework.sh",
                )


if __name__ == "__main__":
    unittest.main()
