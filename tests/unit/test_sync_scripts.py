"""Unit: hooks/sync-version-refs.sh propagates pins and is idempotent (#688).

The hook rewrites version strings across the tree and re-stages (scoped to
the touched paths, #830), so running it against the real checkout is refused
on a dirty tree — and any agent session dirties the tree by construction.
These tests instead run a COPY of the script against a fixture tree (VERSION
+ doc-control row + metadata pin + playbook frontmatter probe, each carrying
one swept form), which exercises the real counted-replacement machinery
without touching the working tree and without any skip.
"""

import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
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
    metadata pin + one playbook frontmatter pin, all stale."""
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
    (tmp / "framework" / "playbooks").mkdir()
    (tmp / "framework" / "playbooks" / "probe.md").write_text(
        f'---\nframework_spec_version: "{stale}"\n---\n# Probe playbook\n',
        encoding="utf-8",
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
        (fixture / "framework" / "probe.md").chmod(0o640)
        result = _run(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        md = (fixture / "framework" / "probe.md").read_text(encoding="utf-8")
        yaml_text = (fixture / "framework" / "governance" / "probe.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"| Framework Version | {current} |", md)
        self.assertIn(f'framework_version: "{current}"', yaml_text)
        # Rename-based write must preserve the target mode (mktemp is 600).
        # The probe carries a non-default mode so the assertion holds under
        # any umask (#831): it pins preservation, not an absolute 0o644.
        probe = fixture / "framework" / "probe.md"
        self.assertEqual(oct(probe.stat().st_mode & 0o777), "0o640")

    def test_playbook_frontmatter_swept(self):
        """The framework_spec_version loop has direct coverage (#831).

        Previously exercised only incidentally; a regression there was
        caught only by the conformance pin test, not the unit file that
        owns the hook contract.
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        result = _run(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        pb = (fixture / "framework" / "playbooks" / "probe.md").read_text(encoding="utf-8")
        self.assertIn(f'framework_spec_version: "{current}"', pb)
        self.assertNotIn(stale, pb)

    @unittest.skipUnless(shutil.which("git"), "git not available")
    def test_restage_scoped_to_touched(self):
        """The re-stage covers exactly the rewritten paths (#830).

        Pre-fix `git add -u` staged every unstaged tracked modification
        repo-wide; an unrelated dirty file must stay unstaged while the
        swept probes are staged.
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        unrelated = fixture / "framework" / "unrelated.md"
        unrelated.write_text("# Unrelated\n", encoding="utf-8")

        def git(*args):
            return subprocess.run(
                ["git", *args],
                cwd=fixture,
                capture_output=True,
                text=True,
                check=True,
            )

        git("init")
        git("add", "-A")
        git("-c", "user.name=sync-test", "-c", "user.email=t@example.com", "commit", "-qm", "init")
        unrelated.write_text("# Unrelated\n# dirty hunk\n", encoding="utf-8")
        result = _run(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        staged = git("--no-pager", "diff", "--cached", "--name-only").stdout.split()
        self.assertIn("framework/probe.md", staged)
        self.assertIn("framework/governance/probe.yaml", staged)
        self.assertIn("framework/playbooks/probe.md", staged)
        self.assertNotIn("framework/unrelated.md", staged)
        status = git("status", "--porcelain").stdout
        self.assertIn(" M framework/unrelated.md", status)

    @unittest.skipUnless(shutil.which("grep"), "grep not available")
    def test_discovery_portable_ere(self):
        """Metadata discovery works without GNU BRE alternation (#830).

        A BSD-mimic grep shim rejects the GNU-only `\\|` join (BSD grep
        matches zero files without `-E`); the hook must still sweep via
        portable `grep -rlE` with `|` alternation.
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        real_grep = shutil.which("grep")
        shimdir = fixture / "bin"
        shimdir.mkdir()
        shim = shimdir / "grep"
        shim.write_text(
            "#!/bin/sh\n"
            "# BSD mimic: GNU BRE \\| alternation matches nothing without -E.\n"
            "hasE=0\ngnu=0\n"
            'for a in "$@"; do\n'
            '  case "$a" in\n'
            '    -*) case "$a" in *E*) hasE=1 ;; esac ;;\n'
            "    *) case \"$a\" in *'\\|'*) gnu=1 ;; esac ;;\n"
            "  esac\n"
            "done\n"
            'if [ "$gnu" = 1 ] && [ "$hasE" = 0 ]; then exit 1; fi\n'
            f'exec "{real_grep}" "$@"\n',
            encoding="utf-8",
        )
        shim.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        result = _run(fixture, env)
        self.assertEqual(result.returncode, 0, result.stderr)
        md = (fixture / "framework" / "probe.md").read_text(encoding="utf-8")
        yaml_text = (fixture / "framework" / "governance" / "probe.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"| Framework Version | {current} |", md)
        self.assertIn(f'framework_version: "{current}"', yaml_text)

    def test_discovery_pattern_has_no_empty_alternative(self):
        # #886: the metadata grep pattern must be a clean alternation — the
        # old `||` join held empty alternatives that matched every file
        # (sweep's literal re-match hid it). A recording grep shim captures
        # the real pattern the script builds; pins still sweep.
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        real_grep = shutil.which("grep")
        shimdir = fixture / "bin"
        shimdir.mkdir()
        log = fixture / "patterns.log"
        shim = shimdir / "grep"
        shim.write_text(
            "#!/bin/sh\n"
            f'for a in "$@"; do case "$a" in -*) ;; *) printf "%s\\n" "$a" >> "{log}" ;; esac; done\n'
            f'exec "{real_grep}" "$@"\n',
            encoding="utf-8",
        )
        shim.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        result = _run(fixture, env)
        self.assertEqual(result.returncode, 0, result.stderr)
        patterns = log.read_text(encoding="utf-8").splitlines()
        self.assertTrue(patterns, "recording shim captured no grep pattern")
        for pat in patterns:
            with self.subTest(pattern=pat[:60]):
                self.assertNotIn("||", pat, "empty ERE alternative in discovery pattern")
        md = (fixture / "framework" / "probe.md").read_text(encoding="utf-8")
        yaml_text = (fixture / "framework" / "governance" / "probe.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"| Framework Version | {current} |", md)
        self.assertIn(f'framework_version: "{current}"', yaml_text)

    def test_restage_failure_warns_loudly(self):
        # #886: a failed re-stage must warn, never `|| true` into silence.
        text = SYNC.read_text(encoding="utf-8")
        code = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
        self.assertIn(
            "WARNING: re-stage failed",
            code,
            "sync-version-refs.sh swallows re-stage errors silently",
        )

    def test_newline_filename_swept(self):
        """A newline in a filename must not desync discovery (#830).

        Pre-fix newline-delimited `read` split one path into bogus `$rel`
        values hitting the `skip (absent)` branch; NUL-delimited reads
        sweep the real file.
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        weird = fixture / "framework" / "weird\nname.md"
        weird.write_text(f"| Framework Version | {stale} |\n", encoding="utf-8")
        result = _run(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f"| Framework Version | {current} |",
            weird.read_text(encoding="utf-8"),
        )

    def test_no_temp_litter_after_kill(self):
        """A killed run leaves no `.sync-*` temps behind (#830).

        The converter is shimmed with a stall; SIGTERM lands mid-conversion
        and the EXIT trap must remove the same-dir temp.
        """
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
        stale = next(v for v in reversed(_old_versions()) if v != current)
        fixture = _fixture(current, stale)
        shimdir = fixture / "bin"
        shimdir.mkdir()
        shim = shimdir / "python3"
        shim.write_text("#!/bin/sh\nsleep 30\n", encoding="utf-8")
        shim.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        proc = subprocess.Popen(
            ["bash", str(fixture / "hooks" / "sync-version-refs.sh")],
            cwd=fixture,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            start_new_session=True,
        )
        try:
            deadline = time.time() + 20
            while time.time() < deadline:
                litter = [p for p in fixture.rglob(".sync-*") if p.is_file()]
                if litter:
                    break
                time.sleep(0.2)
            else:
                self.fail("converter stall never produced a .sync-* temp")
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                self.fail("script did not exit after SIGTERM")
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
            proc.communicate()
        self.assertEqual([p for p in fixture.rglob(".sync-*") if p.is_file()], [])

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
