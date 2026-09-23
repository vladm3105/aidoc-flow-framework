"""Unit: hooks/sync-version-refs.sh is idempotent and exits clean (CHG-08 #665 remedy).

Re-anchored from the deleted `tools/sync-*.sh` idempotency checks: the live
subject is the version-pin fanout hook. The hook rewrites files and re-stages
(`git add -u`), so this test refuses to run on a dirty tree — a sweep that
finds stale pins would otherwise stage the developer's unrelated changes
alongside its own.
"""

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC = REPO_ROOT / "hooks" / "sync-version-refs.sh"


def _porcelain() -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout


class SyncVersionRefsTests(unittest.TestCase):
    def _run(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SYNC)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_sync_exits_zero(self):
        if _porcelain().strip():
            self.skipTest("working tree dirty — refusing to sweep + re-stage")
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sync_is_idempotent(self):
        """A second consecutive run replaces nothing (no 'replaced' lines)."""
        if _porcelain().strip():
            self.skipTest("working tree dirty — refusing to sweep + re-stage")
        first = self._run()
        self.assertEqual(first.returncode, 0, first.stderr)
        before = _porcelain()
        second = self._run()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn("replaced", second.stdout)
        self.assertEqual(_porcelain(), before, "sync run dirtied the tree")


if __name__ == "__main__":
    unittest.main()
