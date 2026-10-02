"""Conformance: consumer install/upgrade scripts (CHG-45, issue #870).

Pins the machine-readable contract behind ``framework/scripts/``:

  * ``allowlist.txt`` is identical to the ``docs/PROJECT.md`` §7.1 consumer
    copy set (brace set + prune path) — the copy set is derived from one
    source, never a second hardcoded list (#741, #834).
  * ``install.sh`` performs BOOTSTRAP.md steps 1–5 on a fixture canon for
    both consumer kinds (pinned copy + symlink), refuses to overwrite
    without ``--force``, and mutates nothing under ``--dry-run``.
  * ``upgrade.sh`` performs the runbook step-2 re-point for both kinds
    (stage-then-rename for pinned copies — never half-copied), re-pins
    ``framework_version``, and reports override drift (DRIFT:/OK:/UNPINNED:)
    before the confirm gate.
  * Destructive ops need ``--yes`` or a TTY confirm; usage and refusal
    errors exit 2, operational failures exit 1.
  * Both scripts are ``shellcheck``-clean when the tool is available.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from _spec import FRAMEWORK, REPO_ROOT

SCRIPTS = FRAMEWORK / "scripts"
INSTALL = SCRIPTS / "install.sh"
UPGRADE = SCRIPTS / "upgrade.sh"
ALLOWLIST = SCRIPTS / "allowlist.txt"
PROJECT_DOC = REPO_ROOT / "docs" / "PROJECT.md"


def _allowlist_entries() -> tuple[set[str], set[str]]:
    """Return (copy-dirs, prune-paths) from allowlist.txt, slashes stripped."""
    copies, prunes = set(), set()
    for raw in ALLOWLIST.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            prunes.add(line[1:].rstrip("/"))
        else:
            copies.add(line.rstrip("/"))
    return copies, prunes


def _make_canon(parent: Path, version: str, marker: str) -> Path:
    """Build a minimal fixture canon tree (real templates, fake VERSION)."""
    canon = parent / f"canon-{version}"
    gov = canon / "framework" / "governance"
    aidoc = gov / "aidoc"
    aidoc.mkdir(parents=True)
    (canon / "framework" / "VERSION").write_text(version + "\n", encoding="utf-8")
    for src, dst in (
        (
            FRAMEWORK / "governance" / "aidoc" / "AIDOC-SCAFFOLD-TEMPLATE.md",
            aidoc / "AIDOC-SCAFFOLD-TEMPLATE.md",
        ),
        (FRAMEWORK / "governance" / "PROFILE-TEMPLATE.yaml", gov / "PROFILE-TEMPLATE.yaml"),
        (FRAMEWORK / "governance" / "ADAPTATION_SURFACE.yaml", gov / "ADAPTATION_SURFACE.yaml"),
    ):
        shutil.copy(src, dst)
    (canon / "framework" / "archive").mkdir(parents=True)
    (canon / "framework" / "archive" / "FROZEN").write_text("canon-dev history\n", encoding="utf-8")
    for d in ("docs", "hooks", "sdd_doc_lint", "tests"):
        (canon / d).mkdir(parents=True)
        (canon / d / "MARKER").write_text(marker + "\n", encoding="utf-8")
    return canon


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([str(script), *args], capture_output=True, text=True, timeout=120)


class AllowlistParity(unittest.TestCase):
    """allowlist.txt ≡ the §7.1 prose allowlist (single source, §7.1)."""

    def test_copy_set_matches_section_71_brace_set(self):
        doc = PROJECT_DOC.read_text(encoding="utf-8")
        section = doc.split("### 7.1", 1)[1].split("### 7.2", 1)[0]
        cp_line = next(
            line for line in section.splitlines() if "cp -r /tmp/aidoc-framework/" in line
        )
        brace = re.search(r"\{([^{}]*)\}", cp_line)
        self.assertIsNotNone(brace, "§7.1 copy line lost its brace set")
        doc_set = {d.strip() for d in brace.group(1).split(",")}
        copies, _ = _allowlist_entries()
        self.assertEqual(copies, doc_set)

    def test_prune_matches_section_71_rm_line(self):
        doc = PROJECT_DOC.read_text(encoding="utf-8")
        section = doc.split("### 7.1", 1)[1].split("### 7.2", 1)[0]
        rm_line = next(
            line
            for line in section.splitlines()
            if line.strip().startswith("rm -rf .aidoc/framework/")
        )
        pruned = rm_line.strip().rsplit(".aidoc/framework/", 1)[1]
        _, prunes = _allowlist_entries()
        self.assertEqual(prunes, {pruned})

    def test_every_copy_entry_exists_in_canon(self):
        copies, _ = _allowlist_entries()
        for entry in copies:
            self.assertTrue(
                (REPO_ROOT / entry).is_dir(), f"allowlist entry missing from canon: {entry}"
            )


class InstallScript(unittest.TestCase):
    """install.sh — BOOTSTRAP steps 1–5 on a fixture canon."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="consumer-scripts-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.canon = _make_canon(self.tmp, "9.9.9", "canon-A")
        self.project = self.tmp / "proj"
        self.project.mkdir()

    def test_pin_install_fills_and_verifies(self):
        proc = _run(
            INSTALL, str(self.project), "--canon-dir", str(self.canon), "--author", "Test Eng"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        aidoc = self.project / ".aidoc"
        readme = (aidoc / "README.md").read_text(encoding="utf-8")
        for placeholder in ("YYYY-MM-DD", "<your name>", "X.Y.Z"):
            self.assertNotIn(placeholder, readme)
        self.assertIn("9.9.9", readme)
        profile = (aidoc / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.9"', profile)
        fw = aidoc / "framework"
        self.assertTrue(fw.is_dir())
        self.assertFalse(fw.is_symlink())
        for d in ("framework", "docs", "hooks", "sdd_doc_lint", "tests"):
            self.assertTrue((fw / d).is_dir(), f"allowlist dir missing: {d}")
        self.assertFalse(
            (fw / "framework" / "archive").exists(),
            "framework/archive/ must be pruned inside the copy",
        )
        self.assertEqual((fw / "tests" / "MARKER").read_text().strip(), "canon-A")

    def test_refuses_overwrite_without_force(self):
        first = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(first.returncode, 0, first.stderr)
        second = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(second.returncode, 2)
        self.assertIn("already exists", second.stderr)
        forced = _run(
            INSTALL, str(self.project), "--canon-dir", str(self.canon), "--force", "--yes"
        )
        self.assertEqual(forced.returncode, 0, forced.stderr)

    def test_force_requires_yes_when_noninteractive(self):
        first = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(first.returncode, 0, first.stderr)
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon), "--force")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("pass --yes", proc.stderr)
        # Refused before mutating: the original tree is intact.
        self.assertTrue((self.project / ".aidoc" / "profile.yaml").is_file())

    def test_dry_run_mutates_nothing(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon), "--dry-run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.project / ".aidoc").exists())

    def test_symlink_kind_links_and_pins(self):
        proc = _run(INSTALL, str(self.project), "--kind", "symlink", "--shared", str(self.canon))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        fw = self.project / ".aidoc" / "framework"
        self.assertTrue(fw.is_symlink())
        self.assertEqual(fw.resolve(), self.canon.resolve())
        profile = (self.project / ".aidoc" / "profile.yaml").read_text()
        self.assertIn('framework_version: "9.9.9"', profile)

    def test_refuses_missing_project_dir(self):
        proc = _run(INSTALL, str(self.tmp / "nope"), "--canon-dir", str(self.canon))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("must exist", proc.stderr)

    def test_symlink_kind_requires_shared(self):
        proc = _run(INSTALL, str(self.project), "--kind", "symlink")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--shared", proc.stderr)

    def test_symlink_kind_refuses_canon_dir(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--kind",
            "symlink",
            "--shared",
            str(self.canon),
            "--canon-dir",
            str(self.canon),
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("pin", proc.stderr)

    def test_tag_mismatch_exits_1(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--canon",
            "framework/v0.0.0",
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("!=", proc.stderr)

    def test_smoke_rejects_unknown_profile_keys(self):
        bad = _make_canon(self.tmp, "9.9.11", "canon-bad")
        tpl = bad / "framework" / "governance" / "PROFILE-TEMPLATE.yaml"
        with tpl.open("a", encoding="utf-8") as fh:
            fh.write("\nbogus_key_for_smoke_test: 1\n")
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(bad))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("unknown keys", proc.stderr)

    def test_install_usage_errors(self):
        proc = _run(INSTALL, "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Usage:", proc.stdout)
        proc = _run(INSTALL, str(self.project), "--bogus")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown flag", proc.stderr)
        proc = _run(
            INSTALL, str(self.project), "--kind", "sideways", "--canon-dir", str(self.canon)
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--kind must be", proc.stderr)
        proc = _run(INSTALL, str(self.project), "--canon")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("needs a value", proc.stderr)


class UpgradeScript(unittest.TestCase):
    """upgrade.sh — runbook step-2 re-point + drift report, both kinds."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="consumer-scripts-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.canon_a = _make_canon(self.tmp, "9.9.9", "canon-A")
        self.canon_b = _make_canon(self.tmp, "9.9.10", "canon-B")
        self.project = self.tmp / "proj"
        self.project.mkdir()

    def _install_pin(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon_a))
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_pin_upgrade_replaces_and_reports_drift(self):
        self._install_pin()
        overrides = self.project / ".aidoc" / "project"
        overrides.mkdir(parents=True)
        (overrides / "old.yaml").write_text('framework_version: "9.9.8"\nfoo: 1\n')
        (overrides / "current.yaml").write_text('framework_version: "9.9.10"\nfoo: 2\n')
        (overrides / "loose.md").write_text("# no pin here\n")
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        aidoc = self.project / ".aidoc"
        profile = (aidoc / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.10"', profile)
        # Remove-before-replace: canon-A content is gone, canon-B is in.
        marker = (aidoc / "framework" / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-B")
        self.assertIn("DRIFT: project/old.yaml (authored against 9.9.8", proc.stdout)
        self.assertIn("OK: project/current.yaml (at 9.9.10)", proc.stdout)
        self.assertIn("UNPINNED: project/loose.md", proc.stdout)

    def test_pin_upgrade_refuses_same_version_without_force(self):
        self._install_pin()
        proc = _run(UPGRADE, str(self.project), "--to", "9.9.9", "--canon-dir", str(self.canon_a))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("already at 9.9.9", proc.stderr)

    def test_upgrade_requires_yes_when_noninteractive(self):
        self._install_pin()
        proc = _run(UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("pass --yes", proc.stderr)
        profile = (self.project / ".aidoc" / "profile.yaml").read_text()
        self.assertIn('framework_version: "9.9.9"', profile)

    def test_symlink_upgrade_retargets(self):
        proc = _run(INSTALL, str(self.project), "--kind", "symlink", "--shared", str(self.canon_a))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--shared", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        fw = self.project / ".aidoc" / "framework"
        self.assertEqual(fw.resolve(), self.canon_b.resolve())
        profile = (self.project / ".aidoc" / "profile.yaml").read_text()
        self.assertIn('framework_version: "9.9.10"', profile)

    def test_conformance_cmd_green_and_red(self):
        self._install_pin()
        green = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            "--conformance-cmd",
            "true",
        )
        self.assertEqual(green.returncode, 0, green.stderr)
        self.assertIn("conformance green", green.stdout)
        red = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            "--force",
            "--conformance-cmd",
            "false",
        )
        self.assertEqual(red.returncode, 1)
        self.assertIn("conformance failed", red.stderr)
        # A non-1 conformance exit still surfaces as script exit 1 (never 2).
        other = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            "--force",
            "--conformance-cmd",
            "exit 3",
        )
        self.assertEqual(other.returncode, 1)
        self.assertIn("conformance failed", other.stderr)

    def test_upgrade_dry_run_mutates_nothing(self):
        self._install_pin()
        before = (self.project / ".aidoc" / "profile.yaml").read_text()
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--dry-run",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("done (dry-run)", proc.stdout)
        after = (self.project / ".aidoc" / "profile.yaml").read_text()
        self.assertEqual(before, after)
        marker = (self.project / ".aidoc" / "framework" / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-A")

    def test_upgrade_tag_mismatch_exits_1(self):
        self._install_pin()
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "framework/v0.0.0",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("!=", proc.stderr)

    def test_namespaced_to_tag_accepted(self):
        self._install_pin()
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "framework/v9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_upgrade_without_overrides_is_vacuous(self):
        self._install_pin()
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("vacuous", proc.stdout)

    def test_upgrade_usage_errors(self):
        proc = _run(UPGRADE, "--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Usage:", proc.stdout)
        proc = _run(UPGRADE, str(self.project), "--bogus")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown flag", proc.stderr)
        self._install_pin()
        proc = _run(UPGRADE, str(self.project), "--yes")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("need --to", proc.stderr)

    def test_pin_kind_on_symlink_is_an_error(self):
        inst = _run(INSTALL, str(self.project), "--kind", "symlink", "--shared", str(self.canon_a))
        self.assertEqual(inst.returncode, 0, inst.stderr)
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.9",
            "--kind",
            "pin",
            "--canon-dir",
            str(self.canon_a),
            "--yes",
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("is a link", proc.stderr)

    def test_kind_mismatch_is_an_error(self):
        self._install_pin()
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--kind",
            "symlink",
            "--shared",
            str(self.canon_b),
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("not a link", proc.stderr)


class ScriptsAreShellcheckClean(unittest.TestCase):
    """Both scripts pass shellcheck when the tool is installed."""

    @unittest.skipUnless(shutil.which("shellcheck"), "shellcheck not installed")
    def test_shellcheck(self):
        for script in (INSTALL, UPGRADE):
            with self.subTest(script=script.name):
                proc = subprocess.run(
                    ["shellcheck", str(script)], capture_output=True, text=True, timeout=120
                )
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
