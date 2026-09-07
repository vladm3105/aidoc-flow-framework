"""Conformance: the plugin's vendored `tools/` modules match the canonical ones.

`tools/sync-plugin-framework.sh` copies three modules into
`platforms/claude-code-plugin/tools/`, and that vendored copy is what a
marketplace consumer installs and runs. Re-vendoring is a manual step (CLAUDE.md
§"Durable traps" records that editing these files requires re-copying by hand,
and that a formatter can rewrite the file *after* the copy), so drift is silent:
the canonical copy is what tests import, the vendored copy is what ships.

`test_doc_lint_vendoring.py` covers `sdd_doc_lint/` the same way. These three
modules had no equivalent guard — so a fix applied only to `tools/` would
re-ship the plugin with the unfixed code and CI would stay green.
"""

from __future__ import annotations

import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CANONICAL = _REPO_ROOT / "tools"
_VENDORED = _REPO_ROOT / "platforms" / "claude-code-plugin" / "tools"

# Keep in sync with TOOLS_FILES in tools/sync-plugin-framework.sh.
TOOLS_FILES = ("saga_driver.py", "finding_filter.py", "playbook_loader.py")


class ToolsVendoring(unittest.TestCase):
    def test_vendored_tools_are_byte_identical(self):
        for name in TOOLS_FILES:
            with self.subTest(module=name):
                canonical = _CANONICAL / name
                vendored = _VENDORED / name
                self.assertTrue(canonical.is_file(), f"missing canonical {canonical}")
                self.assertTrue(vendored.is_file(), f"missing vendored {vendored}")
                self.assertEqual(
                    vendored.read_bytes(),
                    canonical.read_bytes(),
                    f"{name} drifted from tools/{name} — re-run tools/sync-plugin-framework.sh",
                )

    def test_sync_script_list_matches_this_test(self):
        """If the sync script grows a fourth module, this guard must grow with
        it — otherwise the new module ships unguarded."""
        script = (_CANONICAL / "sync-plugin-framework.sh").read_text(encoding="utf-8")
        for line in script.splitlines():
            if line.startswith("TOOLS_FILES="):
                declared = tuple(line.split("(", 1)[1].split(")", 1)[0].split())
                self.assertEqual(
                    declared,
                    TOOLS_FILES,
                    "TOOLS_FILES in sync-plugin-framework.sh changed; update "
                    "TOOLS_FILES in this test",
                )
                break
        else:
            self.fail("TOOLS_FILES not found in tools/sync-plugin-framework.sh")


if __name__ == "__main__":
    unittest.main()
