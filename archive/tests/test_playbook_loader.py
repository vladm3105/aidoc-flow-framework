"""Loader helper for layer-and-lens playbook resolution."""

from __future__ import annotations

# Loader lives at platforms/claude-code-plugin/tools/playbook_loader.py
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "platforms" / "claude-code-plugin" / "tools"))


class PlaybookLoaderTests(unittest.TestCase):
    def test_resolves_known_playbook_path(self):
        from playbook_loader import resolve_playbook_path

        path = resolve_playbook_path(
            repo_root=REPO_ROOT,
            layer="02_PRD",
            lens="chaos_engineer",
        )
        self.assertEqual(
            path,
            REPO_ROOT / "framework" / "playbooks" / "02_PRD" / "chaos_engineer.md",
        )

    def test_missing_playbook_raises_with_documented_reason(self):
        from playbook_loader import PlaybookMissingError, load_playbook

        with self.assertRaises(PlaybookMissingError) as cm:
            load_playbook(
                repo_root=REPO_ROOT,
                layer="02_PRD",
                lens="nonexistent_lens",
            )
        self.assertIn("playbook missing:", str(cm.exception))
        self.assertIn("framework/playbooks/02_PRD/nonexistent_lens.md", str(cm.exception))

    def test_load_returns_content_when_file_exists(self):
        from playbook_loader import load_playbook

        # Use a temp playbook file to keep test hermetic.
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            (tmp / "framework" / "playbooks" / "02_PRD").mkdir(parents=True)
            pb = tmp / "framework" / "playbooks" / "02_PRD" / "chaos_engineer.md"
            pb.write_text("---\nlens: chaos_engineer\n---\n# content\n")
            content = load_playbook(
                repo_root=tmp,
                layer="02_PRD",
                lens="chaos_engineer",
            )
            self.assertIn("# content", content)


if __name__ == "__main__":
    unittest.main()
