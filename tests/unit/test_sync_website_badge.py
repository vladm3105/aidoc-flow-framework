"""Unit: the web-site badge sync self-heals and reports its one silent state (#423).

WHY THIS TEST IS SHAPED LIKE THIS. `scripts/sync-version-refs.sh` writes a badge
into `../web-site/`, an **independent sibling repository**. The defect #423 records
is that the write was a *silent* no-op: it matched the exact string
``Pre-release v<plugin_prev>``, and ``replace_in_file`` returns success on a miss
with no log line — so once one bump was missed, every later run grepped for a
version the site no longer carried and reported nothing. The public badge sat at
``v0.20.1`` against plugin ``0.25.0``, and a second page
(``claude-plugin/index.astro``) was never in the sweep at all, at ``v0.18.0``.

**The prescribed test method could not see it.** `CLAUDE.md` requires a sync-script
reproduction to run in a throwaway clone, because a real run stages 100+ files — and
a clone has no sibling `../web-site/`, so the only write that leaves the repo is
structurally invisible to it. This test supplies a **synthetic** sibling instead: a
temp directory laid out as `<tmp>/framework` + `<tmp>/web-site`, which exercises the
cross-repo path without touching the developer's real sibling checkout.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "sync-version-refs.sh"


def _git_free_env() -> dict[str, str]:
    """The ambient environment with every ``GIT_*`` variable removed.

    THIS IS NOT OPTIONAL, and it is not defensive programming. When this suite
    runs from the `conformance` pre-commit hook during an actual ``git commit``,
    git exports ``GIT_DIR`` and ``GIT_INDEX_FILE`` to the hook. A subprocess
    inheriting them ignores its own ``cwd``: the sandbox's ``git init`` re-inits
    the REAL repository (it set ``core.bare = true`` on this submodule once,
    breaking the worktree), and the script's ``git rev-parse --show-toplevel``
    then returns the real root — so ``../web-site`` resolves to the developer's
    actual sibling checkout and the test writes outside its temp dir.

    Note ``pre-commit run --all-files`` sets only ``GIT_EDITOR``, so the bug is
    invisible there and appears only at real commit time.
    """
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


#: A synthetic plugin version for the sandbox. Deliberately NOT the real tree's
#: value: reading that would make both sides agree by construction, so a script
#: that hardcoded a version would still pass.
SANDBOX_VERSION = "9.9.9"

BADGE_FILES = (
    "src/pages/index.astro",
    "src/pages/claude-plugin/index.astro",
)


class WebsiteBadgeSelfHeal(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        if not SCRIPT.is_file():
            self.skipTest("sync-version-refs.sh not present")
        if shutil.which("git") is None:
            self.skipTest("git not available")
        self.plugin_ver = SANDBOX_VERSION
        self.tmp = Path(tempfile.mkdtemp(prefix="sync-badge-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

        self.repo = self.tmp / "framework"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "platforms" / "claude-code-plugin").mkdir(parents=True)
        shutil.copy2(SCRIPT, self.repo / "scripts" / "sync-version-refs.sh")
        (self.repo / "platforms" / "claude-code-plugin" / "VERSION").write_text(
            f"{self.plugin_ver}\n", encoding="utf-8"
        )
        # The script ends in `git add -u`; give it a repo so that path is exercised
        # rather than silently skipped.
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True, env=_git_free_env())

        self.site = self.tmp / "web-site"
        for rel in BADGE_FILES:
            (self.site / rel).parent.mkdir(parents=True, exist_ok=True)

    def _write_badge(self, rel: str, body: str) -> Path:
        path = self.site / rel
        path.write_text(body, encoding="utf-8")
        return path

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        # `--verbose` is the script's real switch (`$1`); an earlier draft passed a
        # SYNC_VERBOSE env var that nothing reads, which silently suppressed every
        # log line and left the block's only success signal asserted by nothing.
        return subprocess.run(
            ["bash", "scripts/sync-version-refs.sh", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
            env=_git_free_env(),
            check=False,
        )

    def test_a_stale_badge_heals_without_a_version_bump(self):
        """The heart of #423: drift must heal on the next run, not seal itself.

        No VERSION changes here. The old code only wrote inside the
        prev-detection guard, so with nothing bumped it did nothing at all — which
        is exactly how a missed bump became permanent.
        """
        home = self._write_badge(BADGE_FILES[0], '<span class="badge">Pre-release v0.20.1</span>\n')
        sub = self._write_badge(BADGE_FILES[1], '<span class="badge">Pre-release v0.18.0</span>\n')
        result = self._run()  # NO --verbose: the pre-commit `entry:` passes none
        self.assertIn(
            "(self-healing",
            result.stderr,
            "no self-healing log line — the write is silent again, which is the "
            "property #423 was filed about",
        )
        for path in (home, sub):
            with self.subTest(file=str(path.relative_to(self.site))):
                self.assertIn(
                    f"Pre-release v{self.plugin_ver}",
                    path.read_text(encoding="utf-8"),
                    "a stale badge did not heal — the sync is exact-string again (#423)",
                )

    def test_the_second_page_is_swept_too(self):
        """`claude-plugin/index.astro` was never in the sweep and sat 7 minors behind."""
        sub = self._write_badge(BADGE_FILES[1], '<span class="badge">Pre-release v0.18.0</span>\n')
        self._run()
        self.assertIn(f"Pre-release v{self.plugin_ver}", sub.read_text(encoding="utf-8"))

    def test_an_already_current_badge_is_not_rewritten(self):
        """This block runs on every invocation; it must not dirty a sibling repo."""
        home = self._write_badge(
            BADGE_FILES[0], f'<span class="badge">Pre-release v{self.plugin_ver}</span>\n'
        )
        before = home.stat().st_mtime_ns
        self._run()
        self.assertEqual(
            before,
            home.stat().st_mtime_ns,
            "an already-current badge was rewritten — every commit touching a VERSION "
            "file would dirty the sibling repository's working tree",
        )

    def test_a_file_carrying_both_a_current_and_a_stale_badge_fully_heals(self):
        """Checking only for the current value would skip the stale one beside it."""
        home = self._write_badge(
            BADGE_FILES[0],
            # Both on ONE line, deliberately: `sed` without `/g` still substitutes
            # once PER LINE, so a two-line fixture passes with the flag removed.
            f"a Pre-release v{self.plugin_ver} and b Pre-release v0.19.0\n",
        )
        self._run()
        text = home.read_text(encoding="utf-8")
        self.assertEqual(
            text.count(f"Pre-release v{self.plugin_ver}"),
            2,
            "a stale badge survived beside a current one",
        )

    def test_a_present_file_with_no_badge_warns(self):
        """The one state worth hearing about — and the one the old code hid."""
        self._write_badge(BADGE_FILES[0], "<p>no badge here</p>\n")
        result = self._run()
        self.assertIn(
            "carries no 'Pre-release v<x.y.z>' badge",
            result.stderr,
            "a present-but-badgeless sibling file produced no warning — this is the "
            "silence #423 was filed about",
        )

    def test_a_suffixed_badge_heals_whole_rather_than_welding(self):
        """Matching the bare X.Y.Z prefix corrupts a public page, stably.

        "Pre-release v0.26.0-rc1" would become "Pre-release v0.25.0-rc1" — the old
        suffix welded onto the new version — and the next run would then see a
        current-looking badge and leave it there.
        """
        home = self._write_badge(BADGE_FILES[0], "x Pre-release v0.26.0-rc1\n")
        self._run()
        self.assertIn(f"Pre-release v{self.plugin_ver}\n", home.read_text(encoding="utf-8"))
        self.assertNotIn("-rc1", home.read_text(encoding="utf-8"))

    def test_a_symlinked_badge_file_is_refused_not_replaced(self):
        """`sed -i` unlinks and renames, so it would swap the link for a regular
        file and leave the real target stale — a silent half-fix."""
        target = self.site / "real.astro"
        target.write_text("real Pre-release v0.19.0\n", encoding="utf-8")
        link = self.site / BADGE_FILES[0]
        if link.exists():
            link.unlink()
        link.symlink_to(Path("../../real.astro"))
        result = self._run()
        self.assertIn("is a symlink", result.stderr)
        self.assertTrue(link.is_symlink(), "the symlink was replaced by a regular file")
        self.assertIn("v0.19.0", target.read_text(encoding="utf-8"))

    def test_an_unreadable_file_is_not_reported_as_missing_a_badge(self):
        """grep exit 2 is an error, not "no match" — naming the wrong cause is how
        #423 stayed invisible for five minors."""
        home = self._write_badge(BADGE_FILES[0], "x Pre-release v0.19.0\n")
        home.chmod(0o000)
        self.addCleanup(home.chmod, 0o644)
        if os.access(home, os.R_OK):  # running as root — the mode is not enforced
            self.skipTest("cannot make a file unreadable (running as root)")
        result = self._run()
        self.assertIn("cannot read", result.stderr)
        self.assertNotIn("carries no", result.stderr)

    def test_the_write_is_announced_without_the_verbose_flag(self):
        """The production invocation passes no `--verbose`, so `log` is suppressed.

        `.pre-commit-config.yaml`'s `entry:` is a bare `bash scripts/sync-version-refs.sh`,
        and its `verbose: true` is pre-commit's *display* flag, not the script's.
        An earlier revision of this block used `log`, so it rewrote a file in
        another git repository with zero output and rc=0 — the silence #423 was
        filed about, relocated. Every other test here would have passed.
        """
        self._write_badge(BADGE_FILES[0], "x Pre-release v0.19.0\n")
        result = self._run()
        self.assertIn(
            "self-healing",
            result.stderr,
            "a cross-repo write produced no output in the non-verbose invocation "
            "that production actually uses",
        )

    def test_a_malformed_plugin_version_touches_nothing(self):
        """Without the `[[ -n "$plugin_ver" ]]` guard this publishes `Pre-release v`."""
        (self.repo / "platforms" / "claude-code-plugin" / "VERSION").write_text(
            "not-a-version\n", encoding="utf-8"
        )
        home = self._write_badge(BADGE_FILES[0], "x Pre-release v0.19.0\n")
        self._run()
        self.assertIn(
            "Pre-release v0.19.0",
            home.read_text(encoding="utf-8"),
            "a malformed VERSION reached the badge — an empty version would be "
            "published to a public page",
        )

    def test_no_cross_repo_write_outside_a_git_repository(self):
        """The `git rev-parse` gate is this change's own safety control.

        `repo_root` falls back to `pwd`, and the sibling paths are relative to it,
        so outside a repository `../web-site` could resolve somewhere unintended.
        """
        shutil.rmtree(self.repo / ".git")
        home = self._write_badge(BADGE_FILES[0], "x Pre-release v0.19.0\n")
        self._run()
        self.assertIn(
            "Pre-release v0.19.0",
            home.read_text(encoding="utf-8"),
            "the sibling was written from outside a git repository — the rev-parse gate is gone",
        )

    def test_an_inherited_git_dir_cannot_redirect_the_write(self):
        """The sandbox must stay a sandbox when git exports GIT_DIR to a hook.

        Measured mechanism: inside a temp repo with ``GIT_DIR`` inherited,
        ``git rev-parse --show-toplevel`` returns the REAL repository root, so the
        script's ``cd "$repo_root"`` lands there and ``../web-site`` resolves to
        the developer's actual sibling checkout. Before the scrub, running this
        suite from the pre-commit hook during a real ``git commit`` re-inited the
        real module directory (setting ``core.bare = true``) and pointed the
        cross-repo write at the real sibling. `pre-commit run --all-files` sets
        only ``GIT_EDITOR``, so nothing catches this except a test that sets the
        variable deliberately.
        """
        home = self._write_badge(BADGE_FILES[0], "x Pre-release v0.19.0\n")
        real_git_dir = REPO_ROOT / ".git"
        with unittest.mock.patch.dict(
            os.environ,
            {"GIT_DIR": str(real_git_dir), "GIT_INDEX_FILE": str(real_git_dir / "index")},
        ):
            self._run()
        self.assertIn(
            f"Pre-release v{self.plugin_ver}",
            home.read_text(encoding="utf-8"),
            "the sandbox badge did not heal under an inherited GIT_DIR — the run was "
            "redirected at the real repository, and the cross-repo write with it",
        )

    def test_an_absent_sibling_is_silent(self):
        """Normal for a standalone clone and for CI; must not warn."""
        shutil.rmtree(self.site)
        result = self._run()
        self.assertNotIn("web-site", result.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
