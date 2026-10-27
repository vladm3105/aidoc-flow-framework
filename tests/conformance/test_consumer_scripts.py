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
  * CHG-50: no GNU ``sed -i`` (BSD-safe tmpfile fill, proven under a shim
    that rejects ``-i``), ``--canon-sha`` pin verified post-clone,
    install pre-validates before ``--force`` delete, upgrade swaps via
    backup rename with a pre-swap smoke assert, AUTHOR newlines refused.
"""

from __future__ import annotations

import os
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
    for layer in (
        "01_BRD",
        "02_PRD",
        "03_EARS",
        "04_BDD",
        "05_ADR",
        "06_SPEC",
        "07_TDD",
        "08_IPLAN",
        "09_CHG",
        "10_EVAL",
    ):
        prefix = layer.split("_")[1]
        tmpl_src = FRAMEWORK / "layers" / layer / f"{prefix}-00_index.TEMPLATE.yaml"
        if tmpl_src.exists():
            ldir = canon / "framework" / "layers" / layer
            ldir.mkdir(parents=True, exist_ok=True)
            shutil.copy(tmpl_src, ldir / f"{prefix}-00_index.TEMPLATE.yaml")
    tmpl_dir = canon / "framework" / "templates"
    tmpl_dir.mkdir(parents=True)
    shutil.copy(
        FRAMEWORK / "templates" / "AGENTS-TEMPLATE.md",
        tmpl_dir / "AGENTS-TEMPLATE.md",
    )
    for tmpl_name in (
        "STACK-POLICY-TEMPLATE.yaml",
        "TASKFILE-TEMPLATE.yml",
        "ENGINE-CONFIG-TEMPLATE.yaml",
        "CONSUMER-PRECOMMIT-TEMPLATE.yaml",
    ):
        src = FRAMEWORK / "templates" / tmpl_name
        if src.exists():
            shutil.copy(src, tmpl_dir / tmpl_name)
    # Governance blueprint sources tapped by install.sh blueprints (CHG-136).
    for tmpl_name in (
        "AIDOC-CHG-EXECUTION-FLOW-TEMPLATE.md",
        "AIDOC-CI-SMART-ROUTING-TEMPLATE.md",
        "AIDOC-CONFLICT-RESOLUTION-TEMPLATE.md",
        "AIDOC-SELF-REVIEW-LOOP-TEMPLATE.md",
        "AIDOC-QA-PROTOCOL-TEMPLATE.md",
        "AIDOC-BROWSER-TESTING-TEMPLATE.md",
    ):
        src = FRAMEWORK / "governance" / "aidoc" / tmpl_name
        if src.exists():
            shutil.copy(src, aidoc / tmpl_name)
    for std_name in ("DURABLE_EXECUTION_STANDARD.md", "REVIEW_WORKFLOW_STANDARD.md"):
        src = FRAMEWORK / "governance" / std_name
        if src.exists():
            shutil.copy(src, gov / std_name)
    (canon / "framework" / "archive").mkdir(parents=True)
    (canon / "framework" / "archive" / "FROZEN").write_text("canon-dev history\n", encoding="utf-8")
    for d in ("docs", "hooks", "sdd_doc_lint", "tests"):
        (canon / d).mkdir(parents=True)
        (canon / d / "MARKER").write_text(marker + "\n", encoding="utf-8")
    # The scaffolded pre-commit gate references the real hook by path: ship
    # it so the wiring test proves executability, not just text (CHG-136).
    hook_src = REPO_ROOT / "hooks" / "ch-gate-check.sh"
    if hook_src.is_file():
        shutil.copy(hook_src, canon / "hooks" / "ch-gate-check.sh")
    return canon


def _run(script: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(script), *args],
        capture_output=True,
        text=True,
        timeout=120,
        stdin=subprocess.DEVNULL,
        env=env or dict(os.environ),
    )


def _git_init(path: Path) -> str:
    """Turn a fixture canon into a git checkout; return HEAD SHA."""
    env = {
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    subprocess.run(["git", "init", "-q"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "canon"],
        cwd=path,
        check=True,
        capture_output=True,
        env={**dict(os.environ), **env},
    )
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, check=True, capture_output=True, text=True
    )
    return out.stdout.strip()


def _bsd_sed_shim(shimdir: Path) -> None:
    """A sed that dies on GNU -i (BSD/macOS behavior), else execs real sed."""
    real_sed = shutil.which("sed")
    shimdir.mkdir(parents=True, exist_ok=True)
    shim = shimdir / "sed"
    shim.write_text(
        "#!/bin/sh\n"
        'for a in "$@"; do\n'
        '  case "$a" in -i|-i*) echo "sed: -i needs backup suffix (BSD)" >&2; exit 1 ;; esac\n'
        "done\n"
        f'exec "{real_sed}" "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)


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

    def test_scaffolds_adr_index_and_agents_working_agreement(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        adr_index = self.project / "docs" / "sdd" / "05_ADR" / "ADR-00_index.yaml"
        self.assertTrue(adr_index.is_file())
        adr_content = adr_index.read_text(encoding="utf-8")
        self.assertIn("9.9.9", adr_content)
        self.assertNotIn("[X.Y.Z]", adr_content)
        agents = self.project / "AGENTS.md"
        self.assertTrue(agents.is_file())
        agents_content = agents.read_text(encoding="utf-8")
        self.assertIn("proj", agents_content)
        self.assertIn("Where state lives", agents_content)

    def test_no_adr_and_no_agents_flags_skip_scaffolding(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--no-adr",
            "--no-agents",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.project / "docs" / "sdd" / "05_ADR").exists())
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_scaffolds_all_layer_indices_with_flag(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--all-indices",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for layer in (
            "01_BRD",
            "02_PRD",
            "03_EARS",
            "04_BDD",
            "05_ADR",
            "06_SPEC",
            "07_TDD",
            "08_IPLAN",
            "09_CHG",
            "10_EVAL",
        ):
            prefix = layer.split("_")[1]
            idx = self.project / "docs" / "sdd" / layer / f"{prefix}-00_index.yaml"
            self.assertTrue(idx.is_file(), f"missing index for {layer}")
            content = idx.read_text(encoding="utf-8")
            self.assertIn("9.9.9", content, f"missing version in {idx}")
            self.assertNotIn("[X.Y.Z]", content, f"unresolved placeholder in {idx}")

    def test_all_indices_respects_no_adr_flag(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--all-indices",
            "--no-adr",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        brd_idx = self.project / "docs" / "sdd" / "01_BRD" / "BRD-00_index.yaml"
        self.assertTrue(brd_idx.is_file())
        self.assertFalse((self.project / "docs" / "sdd" / "05_ADR").exists())

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

    def test_force_with_incomplete_canon_refuses_before_deleting(self):
        # #880: --force must validate the canon BEFORE deleting .aidoc.
        first = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(first.returncode, 0, first.stderr)
        bad = _make_canon(self.tmp, "9.9.12", "canon-incomplete")
        (bad / "framework" / "governance" / "PROFILE-TEMPLATE.yaml").unlink()
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(bad), "--force", "--yes")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("canon template missing", proc.stderr)
        # The original tree is intact — nothing was deleted.
        profile = (self.project / ".aidoc" / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.9"', profile)

    def test_author_newline_refused(self):
        # #884: a newline in AUTHOR would break the sed fill program.
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon), "--author", "a\nb")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("newline", proc.stderr)
        self.assertFalse((self.project / ".aidoc").exists())

    def test_canon_sha_accept_and_reject(self):
        # #879: --canon-sha pins the canon HEAD; mismatch dies, non-git refuses.
        sha = _git_init(self.canon)
        good = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon), "--canon-sha", sha)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("SHA verified", good.stdout)
        bad_sha = "0" * 40 if not sha.startswith("0") else "1" * 40
        proj2 = self.tmp / "proj2"
        proj2.mkdir()
        mismatch = _run(INSTALL, str(proj2), "--canon-dir", str(self.canon), "--canon-sha", bad_sha)
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn("!=", mismatch.stderr)
        malformed = _run(INSTALL, str(proj2), "--canon-dir", str(self.canon), "--canon-sha", "xyz")
        self.assertEqual(malformed.returncode, 2)
        self.assertIn("40-hex", malformed.stderr)
        plain = _make_canon(self.tmp, "9.9.13", "canon-plain")
        proj3 = self.tmp / "proj3"
        proj3.mkdir()
        non_git = _run(INSTALL, str(proj3), "--canon-dir", str(plain), "--canon-sha", sha)
        self.assertEqual(non_git.returncode, 2)
        self.assertIn("needs a git canon tree", non_git.stderr)

    def test_install_completes_under_bsd_sed(self):
        # #878: no GNU -i anywhere — the full install runs under a BSD-mimic
        # sed that dies on -i. (Fails on the pre-CHG-50 scripts.)
        shimdir = self.tmp / "bin"
        _bsd_sed_shim(shimdir)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon), env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        profile = (self.project / ".aidoc" / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.9"', profile)

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

    def test_pin_install_sets_project_name_and_passes_profile_lint(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        profile_path = self.project / ".aidoc" / "profile.yaml"
        profile_text = profile_path.read_text(encoding="utf-8")
        self.assertIn('project_name: "proj"', profile_text)
        from sdd_doc_lint.profile_lint import validate_profile

        is_valid, errors = validate_profile(profile_path)
        self.assertTrue(is_valid, f"profile_lint failed: {errors}")

    def test_scaffolds_stack_policy_and_linter_runner(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        policy = self.project / "stack-policy.yaml"
        self.assertTrue(policy.is_file())
        self.assertIn('tenant_id: "proj"', policy.read_text(encoding="utf-8"))
        runner = self.project / ".aidoc" / "bin" / "sdd-lint"
        self.assertTrue(runner.is_file())
        self.assertTrue(os.access(runner, os.X_OK))
        taskfile = self.project / ".aidoc" / "Taskfile.yml"
        self.assertTrue(taskfile.is_file())
        taskfile_text = taskfile.read_text(encoding="utf-8")
        self.assertIn("lint:", taskfile_text)
        self.assertIn("chg-lint:", taskfile_text)
        self.assertIn("swf-lint:", taskfile_text)
        self.assertIn("profile-lint:", taskfile_text)
        engine_cfg = self.project / ".aidoc" / "engine" / "engine.yaml"
        self.assertTrue(engine_cfg.is_file())
        self.assertIn("aidoc-flow-langgraph", engine_cfg.read_text(encoding="utf-8"))

    def test_no_stack_policy_flag_skips_scaffolding(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--no-stack-policy",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.project / "stack-policy.yaml").exists())

    def test_scaffolds_governance_blueprints_by_default(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        gov = self.project / ".aidoc" / "project" / "governance"
        for name in (
            "CHG_EXECUTION_FLOW.md",
            "CI_SMART_ROUTING.md",
            "CONFLICT_RESOLUTION.md",
            "SELF_REVIEW_LOOP.md",
            "QA_PROTOCOL.md",
            "BROWSER_TESTING.md",
            "DURABLE_EXECUTION.md",
            "REVIEW_WORKFLOWS.md",
        ):
            self.assertTrue((gov / name).is_file(), f"blueprint missing: {name}")

    def test_no_blueprints_flag_skips_scaffolding(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--no-blueprints",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        gov = self.project / ".aidoc" / "project" / "governance"
        self.assertFalse(
            any(gov.glob("*.md")) if gov.is_dir() else False,
            "blueprints scaffolded despite --no-blueprints",
        )

    def test_scaffolds_precommit_config_by_default(self):
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        precommit = self.project / ".pre-commit-config.yaml"
        self.assertTrue(precommit.is_file())
        content = precommit.read_text(encoding="utf-8")
        self.assertIn("chg-gate-check", content)
        self.assertIn(".aidoc/framework/hooks/ch-gate-check.sh", content)
        hook = self.project / ".aidoc" / "framework" / "hooks" / "ch-gate-check.sh"
        self.assertTrue(hook.is_file(), "scaffolded gate entry has no hook behind it")
        self.assertTrue(os.access(hook, os.X_OK), "shipped hook is not executable")

    def test_no_precommit_flag_skips_scaffolding(self):
        proc = _run(
            INSTALL,
            str(self.project),
            "--canon-dir",
            str(self.canon),
            "--no-precommit",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse((self.project / ".pre-commit-config.yaml").exists())


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

    def test_upgrade_ignores_install_only_opt_outs(self):
        self._install_pin()
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            "--no-adr",
            "--no-agents",
            "--no-stack-policy",
            "--no-blueprints",
            "--no-precommit",
            "--author",
            "Probe Eng",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_pin_upgrade_replaces_and_reports_drift(self):
        self._install_pin()
        overrides = self.project / ".aidoc" / "project"
        overrides.mkdir(parents=True, exist_ok=True)
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

    def test_pin_upgrade_refuses_git_submodule_without_force(self):
        self._install_pin()
        # Simulate a git submodule: .aidoc/framework/.git file (gitlink)
        gitlink = self.project / ".aidoc" / "framework" / ".git"
        gitlink.write_text("gitdir: ../../.git/modules/.aidoc/framework\n")
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Git submodule", proc.stderr)

        # With --force, upgrade succeeds and replaces it
        proc_force = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            "--force",
        )
        self.assertEqual(proc_force.returncode, 0, proc_force.stderr)

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
        # Default installs scaffold blueprints (UNPINNED drift), so the
        # vacuous path needs an install with nothing under .aidoc/project/.
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(self.canon_a), "--no-blueprints")
        self.assertEqual(proc.returncode, 0, proc.stderr)
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

    def test_backup_swap_leaves_no_prev_on_success(self):
        # #881: the old tree is kept as backup only until the swap succeeds.
        self._install_pin()
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        fw = self.project / ".aidoc" / "framework"
        self.assertFalse(
            Path(str(fw) + ".prev").exists(), "backup must be removed after a clean swap"
        )
        marker = (fw / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-B")

    def test_stale_prev_refuses(self):
        # #881: a leftover backup means an interrupted upgrade — refuse loudly.
        self._install_pin()
        prev = self.project / ".aidoc" / "framework.prev"
        prev.mkdir()
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("stale backup", proc.stderr)
        marker = (self.project / ".aidoc" / "framework" / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-A")

    def test_incomplete_stage_refuses_swap(self):
        # #881: never trade a good tree for an incomplete stage.
        self._install_pin()
        (self.canon_b / "framework" / "governance" / "ADAPTATION_SURFACE.yaml").unlink()
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing swap", proc.stderr)
        fw = self.project / ".aidoc" / "framework"
        self.assertTrue(fw.is_dir())
        marker = (fw / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-A")

    def test_upgrade_canon_sha_accept_and_reject(self):
        # #879: upgrade honors --canon-sha like install does.
        self._install_pin()
        sha = _git_init(self.canon_b)
        good = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--canon-sha",
            sha,
            "--yes",
        )
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertIn("SHA verified", good.stdout)
        bad_sha = "0" * 40 if not sha.startswith("0") else "1" * 40
        mismatch = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--canon-sha",
            bad_sha,
            "--yes",
            "--force",
        )
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn("!=", mismatch.stderr)

    def test_failed_swap_restores_previous_tree(self):
        # #881: a failing second rename restores the backup, never strands.
        # A counting mv shim fails exactly the STAGE→FW rename (2nd mv call).
        self._install_pin()
        shimdir = self.tmp / "bin"
        shimdir.mkdir()
        real_mv = shutil.which("mv")
        count = self.tmp / "mv-count"
        shim = shimdir / "mv"
        shim.write_text(
            "#!/bin/sh\n"
            f'N=$(cat "{count}" 2>/dev/null || echo 0); N=$((N+1)); echo "$N" > "{count}"\n'
            'if [ "$N" = 2 ]; then echo "shim: refusing 2nd mv" >&2; exit 1; fi\n'
            f'exec "{real_mv}" "$@"\n',
            encoding="utf-8",
        )
        shim.chmod(0o755)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            env=env,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("previous tree restored", proc.stderr)
        fw = self.project / ".aidoc" / "framework"
        self.assertTrue(fw.is_dir())
        marker = (fw / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-A")

    def test_upgrade_completes_under_bsd_sed(self):
        # #878: the re-pin runs under a BSD-mimic sed. (Fails pre-CHG-50.)
        self._install_pin()
        shimdir = self.tmp / "bin"
        _bsd_sed_shim(shimdir)
        env = dict(os.environ)
        env["PATH"] = str(shimdir) + os.pathsep + env["PATH"]
        proc = _run(
            UPGRADE,
            str(self.project),
            "--to",
            "9.9.10",
            "--canon-dir",
            str(self.canon_b),
            "--yes",
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        profile = (self.project / ".aidoc" / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.10"', profile)

    def test_upgrade_backfills_missing_project_name(self):
        self._install_pin()
        profile_path = self.project / ".aidoc" / "profile.yaml"
        content = profile_path.read_text(encoding="utf-8")
        content = re.sub(
            r"^[ \t]*project_name:.*", '  # project_name: "<broken>"', content, flags=re.MULTILINE
        )
        profile_path.write_text(content, encoding="utf-8")
        proc = _run(
            UPGRADE, str(self.project), "--to", "9.9.10", "--canon-dir", str(self.canon_b), "--yes"
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        reloaded = profile_path.read_text(encoding="utf-8")
        self.assertIn('project_name: "proj"', reloaded)


class ScriptPortabilityPins(unittest.TestCase):
    """Static pins: no GNU-only constructs may re-enter the scripts (#878)."""

    @staticmethod
    def _code(path: Path) -> str:
        text = path.read_text(encoding="utf-8")
        return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))

    def test_no_gnu_sed_inplace(self):
        for script in (INSTALL, UPGRADE):
            with self.subTest(script=script.name):
                code = self._code(script)
                self.assertNotRegex(code, r"sed\s+-i", f"{script.name} uses GNU sed -i")
                self.assertIn("pinsub", code, f"{script.name} lost its portable fill")

    def test_scripts_carry_version_markers(self):
        for script in (INSTALL, UPGRADE):
            with self.subTest(script=script.name):
                text = script.read_text(encoding="utf-8")
                self.assertRegex(
                    text, r"(?m)^# Version: 1\.1$", f"{script.name} lost its version marker"
                )


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


class DeployScript(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="deploy-scripts-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.project = self.tmp / "proj"
        self.project.mkdir()

    def test_deploy_fresh_pin_with_flags(self):
        deploy_sh = REPO_ROOT / "deploy.sh"
        proc = subprocess.run(
            [
                "bash",
                str(deploy_sh),
                "--target",
                str(self.project),
                "--kind",
                "pin",
                "--no-stack-policy",
                "--yes",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue((self.project / ".aidoc" / "profile.yaml").exists())
        self.assertFalse((self.project / "stack-policy.yaml").exists())

    def test_deploy_default_kind_is_pin(self):
        deploy_sh = REPO_ROOT / "deploy.sh"
        proc = subprocess.run(
            [
                "bash",
                str(deploy_sh),
                "--target",
                str(self.project),
                "--yes",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        fw = self.project / ".aidoc" / "framework"
        self.assertTrue(fw.exists())
        self.assertTrue(fw.is_dir())
        self.assertFalse(fw.is_symlink())

    def test_deploy_help_exits_zero(self):
        deploy_sh = REPO_ROOT / "deploy.sh"
        proc = subprocess.run(
            ["bash", str(deploy_sh), "--help"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Usage:", proc.stdout)

    def test_deploy_missing_values_refused(self):
        deploy_sh = REPO_ROOT / "deploy.sh"
        for flag in ("--target", "--kind", "--shared"):
            proc = subprocess.run(
                ["bash", str(deploy_sh), flag],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(proc.returncode, 2, flag)
            self.assertIn("needs a value", proc.stderr)

    def test_deploy_canon_symlink_refused(self):
        deploy_sh = REPO_ROOT / "deploy.sh"
        proc = subprocess.run(
            [
                "bash",
                str(deploy_sh),
                "--target",
                str(self.project),
                "--kind",
                "symlink",
                "--canon",
                "framework/v9.9.9",
                "--yes",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--canon", proc.stderr)

    def _tag_canon(self, version):
        canon = _make_canon(self.tmp, version, f"canon-{version}")
        _git_init(canon)
        subprocess.run(
            ["git", "-C", str(canon), "tag", f"framework/v{version}"],
            check=True,
            capture_output=True,
        )
        return canon

    def test_deploy_canon_tag_fresh_install(self):
        canon = self._tag_canon("9.9.9")
        deploy_sh = REPO_ROOT / "deploy.sh"
        proc = subprocess.run(
            [
                "bash",
                str(deploy_sh),
                "--target",
                str(self.project),
                "--canon",
                "framework/v9.9.9",
                "--yes",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env={**dict(os.environ), "AIDOC_CANON_URL": str(canon)},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        profile = (self.project / ".aidoc" / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.9"', profile)

    def test_deploy_canon_tag_brownfield_upgrade(self):
        canon_a = _make_canon(self.tmp, "9.9.9", "canon-A")
        proc = _run(INSTALL, str(self.project), "--canon-dir", str(canon_a))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        canon_b = self._tag_canon("9.9.10")
        deploy_sh = REPO_ROOT / "deploy.sh"
        proc = subprocess.run(
            [
                "bash",
                str(deploy_sh),
                "--target",
                str(self.project),
                "--canon",
                "framework/v9.9.10",
                "--yes",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env={**dict(os.environ), "AIDOC_CANON_URL": str(canon_b)},
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        aidoc = self.project / ".aidoc"
        profile = (aidoc / "profile.yaml").read_text(encoding="utf-8")
        self.assertIn('framework_version: "9.9.10"', profile)
        marker = (aidoc / "framework" / "tests" / "MARKER").read_text().strip()
        self.assertEqual(marker, "canon-9.9.10")


class ChGateCheckHook(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ch-gate-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.hook = REPO_ROOT / "hooks" / "ch-gate-check.sh"

    def test_ch_gate_check_discovers_underscored_09_chg(self):
        repo = self.tmp / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        chg_dir = repo / "docs" / "sdd" / "09_CHG"
        chg_dir.mkdir(parents=True)
        (chg_dir / "CHG-01.yaml").write_text(
            "change_control:\n  status: In-Progress\n", encoding="utf-8"
        )
        (repo / "main.py").write_text("print(1)\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        proc = subprocess.run(
            [str(self.hook)], cwd=repo, capture_output=True, text=True, timeout=30
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Active CHG found", proc.stdout)


if __name__ == "__main__":
    unittest.main()
