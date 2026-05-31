"""Unit: sync scripts are idempotent and produce byte-identical bundles."""

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK, REPO_ROOT, plugin_bundle_root


def hash_tree(root: Path) -> dict[str, str]:
    """Return {relative-path: sha256-hex} for every file under root."""
    out = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            out[str(path.relative_to(root))] = digest
    return out


class SyncScriptIdempotencyTests(unittest.TestCase):
    def _find_sync(self, *candidates: Path) -> Path | None:
        for c in candidates:
            if c.exists():
                return c
        return None

    def test_sync_plugin_framework_is_idempotent(self):
        sync = self._find_sync(
            FRAMEWORK / "tools" / "sync-plugin-framework.sh",
            REPO_ROOT / "tools" / "sync-plugin-framework.sh",
        )
        if sync is None:
            self.skipTest("sync-plugin-framework.sh not present")

        target = plugin_bundle_root() / "framework"
        before = hash_tree(target)
        result = subprocess.run(
            ["bash", str(sync)],
            cwd=FRAMEWORK,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"sync-plugin-framework exited {result.returncode}:\n{result.stderr}",
        )
        after = hash_tree(target)
        diff = {
            k: (before.get(k), after.get(k))
            for k in set(before) | set(after)
            if before.get(k) != after.get(k)
        }
        self.assertFalse(
            diff, f"sync-plugin-framework.sh not idempotent: {len(diff)} file(s) changed"
        )

    def test_sdd_doc_lint_vendored_sync_is_idempotent(self):
        sync = self._find_sync(
            FRAMEWORK / "tools" / "sdd_doc_lint" / "sync-vendored.sh",
            REPO_ROOT / "tools" / "sdd_doc_lint" / "sync-vendored.sh",
        )
        if sync is None:
            self.skipTest("sdd_doc_lint/sync-vendored.sh not present")
        bundle_lint = plugin_bundle_root() / "sdd_doc_lint"
        before = hash_tree(bundle_lint)
        result = subprocess.run(
            ["bash", str(sync)],
            cwd=FRAMEWORK,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0, f"sync-vendored exited {result.returncode}:\n{result.stderr}"
        )
        after = hash_tree(bundle_lint)
        self.assertEqual(before, after, "sdd_doc_lint vendored sync not idempotent")


if __name__ == "__main__":
    unittest.main()
