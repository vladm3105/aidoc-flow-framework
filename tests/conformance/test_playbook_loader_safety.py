"""Conformance: playbook_loader.py confines reads to the playbook root.

`layer` and `lens` are interpolated into a filesystem path, so an unguarded
resolver lets a caller read any file the process can (PLUGIN-PREPROD-001 L3).

Lives under tests/conformance/ deliberately: the module's other tests are in
tests/unit/, which no hook and no workflow executes, so a guard placed there
would prove itself once and never again.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "tools"))
import playbook_loader  # noqa: E402  (path injection above is intentional)


class TraversalIsRejected(unittest.TestCase):
    ESCAPES = [
        ("../../..", "passwd"),
        ("02_PRD", "../../../../etc/passwd"),
        ("02_PRD/../../..", "secret"),
        ("/etc", "passwd"),
        ("02_PRD", "/etc/passwd"),
    ]

    def test_resolve_rejects_escape(self):
        for layer, lens in self.ESCAPES:
            with self.subTest(layer=layer, lens=lens):
                with self.assertRaises(playbook_loader.PlaybookPathError):
                    playbook_loader.resolve_playbook_path(_REPO_ROOT, layer, lens)

    def test_load_rejects_escape_before_reading(self):
        """The guard must fire even when the traversal target exists — an
        existing target is exactly the case a traversal is aimed at.

        `layer=".."` climbs from `framework/playbooks` to `framework`, so the
        decoy has to live there for this to be the "target exists" case rather
        than a missing-file case that would pass for the wrong reason.
        """
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "framework" / "playbooks").mkdir(parents=True)
            secret = root / "framework" / "secret.md"
            secret.write_text("classified\n")
            self.assertTrue(secret.exists())
            with self.assertRaises(playbook_loader.PlaybookPathError):
                playbook_loader.load_playbook(root, "..", "secret")

    def test_symlinked_file_inside_root_cannot_escape(self):
        """The guard's strongest property, and the one a lexical `..` check
        would not have: it resolves symlinks. Without this, a refactor to a
        cheaper string-based guard passes every other test here."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pb = root / "framework" / "playbooks" / "02_PRD"
            pb.mkdir(parents=True)
            (root / "outside.md").write_text("classified\n")
            os.symlink(root / "outside.md", pb / "leak.md")
            with self.assertRaises(playbook_loader.PlaybookPathError):
                playbook_loader.load_playbook(root, "02_PRD", "leak")

    def test_symlinked_directory_inside_root_cannot_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pb = root / "framework" / "playbooks"
            pb.mkdir(parents=True)
            outside = root / "elsewhere"
            (outside / "02_PRD").mkdir(parents=True)
            (outside / "02_PRD" / "architect.md").write_text("classified\n")
            os.symlink(outside, pb / "evil")
            with self.assertRaises(playbook_loader.PlaybookPathError):
                playbook_loader.load_playbook(root, "evil/02_PRD", "architect")

    def test_null_byte_raises_the_modules_own_error(self):
        """PlaybookPathError subclasses ValueError, so a bare ValueError from
        realpath would escape a caller that catches PlaybookPathError."""
        with self.assertRaises(playbook_loader.PlaybookPathError):
            playbook_loader.resolve_playbook_path(_REPO_ROOT, "02_PRD", "ok\x00")

    def test_empty_segments_rejected(self):
        for layer, lens in (("", "architect"), ("02_PRD", ""), ("  ", "architect")):
            with self.subTest(layer=layer, lens=lens):
                with self.assertRaises(playbook_loader.PlaybookPathError):
                    playbook_loader.resolve_playbook_path(_REPO_ROOT, layer, lens)

    def test_returns_the_path_it_validated(self):
        """The checked path and the returned path must be the same object, or
        a symlinked component swapped between the check and the read escapes a
        check that passed. A legitimate symlink — one resolving *inside* the
        root — is what makes the two differ observably."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            pb = root / "framework" / "playbooks"
            (pb / "real_layer").mkdir(parents=True)
            (pb / "real_layer" / "architect.md").write_text("ok\n")
            os.symlink(pb / "real_layer", pb / "alias_layer")

            path = playbook_loader.resolve_playbook_path(root, "alias_layer", "architect")
            self.assertEqual(path, path.resolve(), "returned an unvalidated path")
            self.assertEqual(path, pb / "real_layer" / "architect.md")
            # and the legitimate symlink is not over-blocked
            self.assertEqual(
                playbook_loader.load_playbook(root, "alias_layer", "architect"), "ok\n"
            )

    def test_legitimate_path_still_resolves(self):
        path = playbook_loader.resolve_playbook_path(_REPO_ROOT, "02_PRD", "chaos_engineer")
        self.assertEqual(
            path, _REPO_ROOT / "framework" / "playbooks" / "02_PRD" / "chaos_engineer.md"
        )

    def test_missing_playbook_still_raises_its_own_error(self):
        with self.assertRaises(playbook_loader.PlaybookMissingError):
            playbook_loader.load_playbook(_REPO_ROOT, "02_PRD", "nonexistent_lens")


if __name__ == "__main__":
    unittest.main()
