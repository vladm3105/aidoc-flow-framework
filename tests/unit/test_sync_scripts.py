"""Unit: hooks/sync-version-refs.sh propagates pins and is idempotent (#688).

The hook rewrites version strings across the tree and re-stages (`git add
-u`), so running it against the real checkout is refused on a dirty tree —
and any agent session dirties the tree by construction. These tests instead
run a COPY of the script against a fixture tree (VERSION + two probe files
carrying one swept form each), which exercises the real counted-replacement
machinery without touching the working tree and without any skip.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNC = REPO_ROOT / "hooks" / "sync-version-refs.sh"
VERSION_FILE = REPO_ROOT / "framework" / "VERSION"


def _old_versions() -> list[str]:
    """The script's OLD_VERSIONS list, in order."""
    match = re.search(r'^OLD_VERSIONS="([^"]+)"', SYNC.read_text(encoding="utf-8"), re.MULTILINE)
    assert match, "sync-version-refs.sh carries no OLD_VERSIONS list"
    return match.group(1).split()


def _fixture(current: str, stale: str) -> Path:
    """A mini-tree the hook can sweep: VERSION + one doc-control row + one
    metadata pin, both stale."""
    tmp = Path(tempfile.mkdtemp(prefix="syncfix-"))
    (tmp / "framework").mkdir()
    (tmp / "framework" / "VERSION").write_text(current + "\n", encoding="utf-8")
    (tmp / "framework" / "probe.md").write_text(
        f"| Framework Version | {stale} |\n", encoding="utf-8"
    )
    (tmp / "framework" / "governance").mkdir()
    (tmp / "framework" / "governance" / "probe.yaml").write_text(
        f'framework_version: "{stale}"\n', encoding="utf-8"
    )
    (tmp / "hooks").mkdir()
    shutil.copy(SYNC, tmp / "hooks" / "sync-version-refs.sh")
    return tmp


def _run(fixture: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(fixture / "hooks" / "sync-version-refs.sh")],
        cwd=fixture,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


class SyncVersionRefsTests(unittest.TestCase):
    def test_sync_propagates_stale_pins(self):
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        result = _run(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        md = (fixture / "framework" / "probe.md").read_text(encoding="utf-8")
        yaml_text = (fixture / "framework" / "governance" / "probe.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"| Framework Version | {current} |", md)
        self.assertIn(f'framework_version: "{current}"', yaml_text)
        # Rename-based write must preserve the target mode (mktemp is 600).
        probe = fixture / "framework" / "probe.md"
        self.assertEqual(oct(probe.stat().st_mode & 0o777), "0o644")

    def test_converter_failure_leaves_target_untouched(self):
        """Fail-closed (#821): a broken converter must not truncate the target.

        A latin-1 byte keeps the swept literal greppable but makes the
        python3 converter raise UnicodeDecodeError. The hook must refuse
        loudly (nonzero exit) and leave the target byte-identical.
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        target = fixture / "framework" / "probe.md"
        with target.open("ab") as fh:
            fh.write(b"\xff")
        poisoned = target.read_bytes()
        result = _run(fixture)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("FAILED", result.stderr)
        self.assertEqual(target.read_bytes(), poisoned)

    def test_write_failure_leaves_target_untouched(self):
        """Atomic write (#821 review): a failed rename must not touch the target.

        Shadow `mv` with a failing shim: the converter succeeds, the write
        stage fails. Rename semantics mean the original is still intact —
        the hook must refuse loudly (nonzero exit) with the target
        byte-identical (a write-through `cat` could not promise this).
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        target = fixture / "framework" / "probe.md"
        before = target.read_bytes()
        shimdir = fixture / "bin"
        shimdir.mkdir()
        shim = shimdir / "mv"
        shim.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
        shim.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        result = _run(fixture, env)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("FAILED", result.stderr)
        self.assertEqual(target.read_bytes(), before)

    def test_sync_is_idempotent(self):
        """A second consecutive run replaces nothing (no 'replaced' lines)."""
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        first = _run(fixture)
        self.assertEqual(first.returncode, 0, first.stderr)
        second = _run(fixture)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn("replaced", second.stdout)


if __name__ == "__main__":
    unittest.main()
