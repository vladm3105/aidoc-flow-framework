"""Conformance: the plugin's PostToolUse review hook is safe on a stranger's machine.

Locks the PLUGIN-PREPROD-001 PR 1 fixes for
`platforms/claude-code-plugin/hooks/sdd-doc-review.sh`:

* **B1** — no module the project can place gets imported by the linter. Two
  vectors, closed in two stages: a `sdd_doc_lint/` package in the user's working
  directory (`python3 -m` searches the CWD first — PR 1), and a `yaml/` package
  on an **inherited `PYTHONPATH`**, which the hook used to append to the plugin
  root (PR 2). The second one executed, silently, in a real hook run.
* **B4 (hook half)** — only lines matching the linter's finding grammar reach the
  model; a crash must not be relabelled as structural findings.
* **H1** — structural findings require a project that actually adopted the
  framework; the bundled registry otherwise makes every repo look adopted.
* **H2** — the documented `review_hook` `off | on | verbose` enum is honoured.
* **H3** — findings are framed as untrusted tool output, not as instructions.
* **M1 / P1** — the hook declares a timeout and bounds what it reads and emits.
* **L4** — the layer path test honours the configured `docs_root`.

Every scratch project is created **outside this repository and outside `$HOME`**.
Inside either, the hook's upward walk would reach a real adoption marker (this
repo's own `framework/registry/LAYER_REGISTRY.yaml`, or a user-global
`~/.aidoc/`) and the H1 assertions would pass against a build where H1 was never
implemented.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLUGIN = _REPO_ROOT / "platforms" / "claude-code-plugin"
_HOOK = _PLUGIN / "hooks" / "sdd-doc-review.sh"
_HOOKS_JSON = _PLUGIN / "hooks" / "hooks.json"
_BROKEN_BRD = (
    _REPO_ROOT / "tests" / "acceptance" / "fixtures" / "negative" / "brd-broken-sections.md"
)

# The hook exits 0 emitting nothing when jq is missing, so every behavioural
# assertion below would pass vacuously. Assert the precondition rather than
# skipping on it.
_JQ = shutil.which("jq")
_PYTHON3 = shutil.which("python3")


class HookHarness(unittest.TestCase):
    """Shared scratch-project construction and hook invocation."""

    def setUp(self):
        self.assertIsNotNone(_JQ, "jq is required: without it the hook exits 0 silently")
        self.assertIsNotNone(_PYTHON3, "python3 is required to exercise the linter path")
        self.assertTrue(_HOOK.is_file(), f"hook not found: {_HOOK}")
        self.assertTrue(_BROKEN_BRD.is_file(), f"fixture not found: {_BROKEN_BRD}")

    def make_project(self, *, review_hook=None, adopted=False, docs_root=None):
        """Create a scratch project root outside the repo and outside $HOME."""
        root = Path(tempfile.mkdtemp(prefix="aidoc-hook-conf-")).resolve()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)

        self.assertFalse(
            str(root).startswith(str(_REPO_ROOT) + os.sep),
            f"scratch root {root} is inside the repo; H1 would false-pass",
        )
        home = str(Path.home().resolve())
        self.assertFalse(
            str(root) == home or str(root).startswith(home + os.sep),
            f"scratch root {root} is inside $HOME; H1 would false-pass",
        )
        # Location is not enough: an adoption marker on any ancestor of the
        # temp dir would satisfy the walk and make every H1-negative test pass
        # for the wrong reason.
        for ancestor in root.parents:
            self.assertFalse(
                (ancestor / ".aidoc").exists()
                or (ancestor / "framework" / "registry" / "LAYER_REGISTRY.yaml").exists(),
                f"adoption marker at {ancestor}; H1 would false-pass",
            )

        if review_hook is not None or docs_root is not None:
            (root / ".claude").mkdir(parents=True, exist_ok=True)
            lines = ["schema: 1"]
            if docs_root is not None:
                lines.append(f"docs_root: {docs_root}")
            if review_hook is not None:
                lines.append(f'review_hook: "{review_hook}"')
            (root / ".claude" / "aidoc-flow.config.yaml").write_text(
                "\n".join(lines) + "\n", encoding="utf-8"
            )

        if adopted == "registry":
            # The second marker the hook accepts. Contents are deliberately a
            # stub: the hook only tests for the file's presence, and it runs the
            # linter from the plugin root so this copy is never consumed. A test
            # asserting findings still appear here is what locks that.
            reg = root / "framework" / "registry"
            reg.mkdir(parents=True, exist_ok=True)
            (reg / "LAYER_REGISTRY.yaml").write_text(
                "# planted by a test; the hook must not consume this\nlayers: []\n",
                encoding="utf-8",
            )
        elif adopted:
            # `.aidoc/` — what a project that has run the cascade carries.
            (root / ".aidoc").mkdir(exist_ok=True)

        return root

    def place_broken_brd(self, root: Path, relative: str, pad_sections: int = 0) -> Path:
        """Stage the broken-BRD fixture, optionally padded.

        The fixture on its own yields exactly one ERROR and no WARNING, which is
        why the padding exists: each appended section trips one `STY02` WARNING,
        so one section exercises the grammar's WARNING alternative and enough of
        them overflow the findings byte budget. Built here rather than borrowed
        from `examples/`, whose corpus is regenerated wholesale.
        """
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_BROKEN_BRD, target)
        if pad_sections:
            words = " ".join(f"word{i}" for i in range(400))
            with target.open("a", encoding="utf-8") as handle:
                for n in range(pad_sections):
                    handle.write(f"\n## Pad {n}\n\n{words}\n")
        return target

    def stub_python3(self, root: Path, *, rc: int, stdout: str = "", stderr: str = ""):
        """A `python3` on `PATH` that emits fixed output and exits `rc`.

        The hook's contract is written in terms of the linter's exit code, and
        every way of provoking a real non-zero from the vendored linter runs
        through a path the hardening has since closed. Stubbing the interpreter
        states the contract directly: this code, this output, this behaviour.
        """
        bindir = root / "stubbin"
        bindir.mkdir(exist_ok=True)
        stub = bindir / "python3"
        stub.write_text(
            "#!/usr/bin/env bash\n"
            f"printf '%s' {shlex.quote(stdout)}\n"
            f"printf '%s' {shlex.quote(stderr)} >&2\n"
            f"exit {int(rc)}\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)
        return dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}")

    def run_hook(self, target: Path, cwd: Path, env: dict | None = None):
        payload = json.dumps({"tool_input": {"file_path": str(target)}})
        return subprocess.run(
            ["bash", str(_HOOK)],
            input=payload,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            env=env,
            timeout=60,
        )

    def assert_clean_streams(self, proc):
        """Exit 0, and not one byte on stderr.

        The acceptance harness captures this hook with `2>&1` and asserts the
        result parses as JSON, so a stray diagnostic fails that element with the
        misleading reason "hook output invalid JSON".
        """
        self.assertEqual(proc.returncode, 0, f"hook must always exit 0; stderr={proc.stderr!r}")
        self.assertEqual(proc.stderr, "", f"hook wrote to stderr: {proc.stderr!r}")

    def context_of(self, proc) -> str:
        self.assert_clean_streams(proc)
        self.assertTrue(proc.stdout.strip(), "expected hook output, got nothing")
        payload = json.loads(proc.stdout)
        return payload["hookSpecificOutput"]["additionalContext"]


class WorkingDirectoryIsNotAnImportPath(HookHarness):
    """B1: a shadow `sdd_doc_lint/` in the user's CWD must never execute."""

    def test_shadow_package_does_not_run(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        shadow = root / "sdd_doc_lint"
        shadow.mkdir()
        (shadow / "__init__.py").write_text("", encoding="utf-8")
        (shadow / "__main__.py").write_text(
            "import pathlib, sys\n"
            "pathlib.Path(__file__).resolve().parent.parent"
            '.joinpath("SHADOW_RAN").write_text("executed\\n")\n'
            'print("SHADOW-PAYLOAD-EXECUTED", file=sys.stderr)\n'
            "sys.exit(1)\n",
            encoding="utf-8",
        )

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertFalse(
            (root / "SHADOW_RAN").exists(),
            "a sdd_doc_lint package in the working directory executed",
        )
        self.assertNotIn("SHADOW-PAYLOAD-EXECUTED", context)
        # The vendored linter ran instead: its findings are present.
        self.assertIn("STRUCT01", context)


class OnlyFindingsReachTheModel(HookHarness):
    """B4 (hook half): crash output must not be relabelled as findings."""

    def test_non_finding_lines_are_filtered_out(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("STRUCT01", context)
        # The trailing summary line is not a finding and must not be forwarded.
        self.assertNotIn("sdd-doc-lint:", context)
        for line in context.splitlines():
            if "[ERROR " in line or "[WARNING " in line:
                # The code charset must admit hyphens — TRACE-RES-001, TH-RES-001
                # and friends are real rule codes.
                self.assertRegex(line, r":[0-9]+: \[(ERROR|WARNING) [A-Z0-9-]+\] ")

    def test_warning_severity_findings_reach_the_model(self):
        """The grammar says WARNING, not WARN — a `WARN ` alternative matches nothing.

        Without this the whole WARNING branch is untested: the unpadded fixture
        emits only an ERROR, so `\\[(ERROR|WARN) ` and `\\[(ERROR|WARNING) `
        behave identically. It is also the only guard the `--warn-exit` work
        will have.
        """
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md", pad_sections=1)

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("[WARNING STY02]", context)
        self.assertIn("[ERROR STRUCT01]", context)

    def test_a_crashing_linter_yields_no_findings_block(self):
        """A traceback exits 1 — the same code as findings — and must be dropped.

        Driven by a stub `python3` on `PATH` rather than by shadowing PyYAML.
        The shadow used to work because the hook appended the inherited
        `PYTHONPATH`; it no longer does (that was a code-execution hole — see
        `PlantedModulesOnPythonpathDoNotExecute`), so the shadow can no longer
        reach the linter. It had also stopped testing this at all in the
        meantime: PLUGIN-PREPROD-001 PR 2 made an absent PyYAML exit **3**, so
        the `rc == 1` branch was never entered and all three assertions below
        passed because nothing was produced rather than because it was filtered.

        The stub is strictly better than either: it names the exit code and the
        output independently, so the test states the contract instead of
        arranging for a real crash and hoping it still lands on 1.
        """
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        env = self.stub_python3(
            root,
            rc=1,
            stderr=(
                "Traceback (most recent call last):\n"
                '  File "<frozen runpy>", line 189, in _run_module_as_main\n'
                "ImportError: cannot import name 'safe_load' from 'yaml'\n"
            ),
        )
        proc = self.run_hook(target, cwd=root, env=env)

        context = self.context_of(proc)
        self.assertIn("doc-brd-audit", context, "the nudge must survive a linter crash")
        self.assertNotIn("Traceback", context)
        self.assertNotIn("ImportError", context)
        self.assertNotIn("<untrusted-tool-output", context)


class PlantedModulesOnPythonpathDoNotExecute(HookHarness):
    """B1, second vector: an inherited `PYTHONPATH` must not reach the linter.

    PR 1 closed the working-directory vector (`python3 -m` searching the CWD).
    The hook still *appended* the inherited `PYTHONPATH` to the plugin root,
    so a `yaml/` package on any inherited entry was imported by the linter and
    ran — silently, with the hook exiting 0 and emitting a normal nudge.
    `.envrc` is repository content and direnv exports it, so this was reachable
    from a cloned repo on a developer machine with a common tool installed.
    """

    def test_planted_yaml_package_does_not_execute(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        planted = root / "envdir"
        (planted / "yaml").mkdir(parents=True)
        marker = root / "PLANTED_RAN"
        (planted / "yaml" / "__init__.py").write_text(
            "import pathlib\n"
            f'pathlib.Path({str(marker)!r}).write_text("executed\\n")\n'
            "def safe_load(*a, **k):\n"
            "    return {}\n"
            "def safe_load_all(*a, **k):\n"
            "    return iter(())\n",
            encoding="utf-8",
        )

        context = self.context_of(
            self.run_hook(target, cwd=root, env=dict(os.environ, PYTHONPATH=str(planted)))
        )

        self.assertFalse(
            marker.exists(),
            "a yaml/ package on the inherited PYTHONPATH executed inside the hook",
        )
        # The real linter ran instead — the fix must not have silenced it.
        self.assertIn("STRUCT01", context)


class AdoptionIsRequiredForFindings(HookHarness):
    """H1: the bundled registry must not make every directory look adopted."""

    def test_non_adopting_project_gets_the_nudge_without_findings(self):
        root = self.make_project(review_hook="verbose", adopted=False)
        # Basename branch only: no scaffolded docs/0N_<ARTIFACT>/ tree, no
        # project-local registry, no .aidoc/.
        target = self.place_broken_brd(root, "BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context, "the advisory nudge is not gated on adoption")
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)

    def test_the_same_document_in_an_adopted_project_does_get_findings(self):
        """The control for the test above: the gate, not the document, is why."""
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("<untrusted-tool-output", context)
        self.assertIn("STRUCT01", context)


class ReviewHookEnumIsWired(HookHarness):
    """H2: the documented off | on | verbose values control the hook."""

    def test_off_emits_nothing(self):
        root = self.make_project(review_hook="off", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        proc = self.run_hook(target, cwd=root)

        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "", "review_hook: off must emit nothing at all")

    def test_on_nudges_without_findings(self):
        root = self.make_project(review_hook="on", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context)
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)

    def test_the_default_with_no_config_file_is_on(self):
        root = self.make_project(review_hook=None, adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context)
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)

    def test_an_unrecognized_value_falls_back_to_the_default(self):
        root = self.make_project(review_hook="LOUD", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context)
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)

    def test_a_crlf_config_is_honoured(self):
        """`CONFIG.md` tells users to QUOTE these values, so CRLF hits the documented form.

        On a CRLF file the closing quote is not at end-of-line: a quote-strip
        that runs before the whitespace strip leaves `"off"` intact, the enum
        rejects it, and the hook silently stays on.
        """
        root = self.make_project(adopted=True)
        (root / ".claude").mkdir(exist_ok=True)
        (root / ".claude" / "aidoc-flow.config.yaml").write_bytes(
            b'schema: 1\r\nreview_hook: "off"\r\n'
        )
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        proc = self.run_hook(target, cwd=root)

        self.assert_clean_streams(proc)
        self.assertEqual(proc.stdout.strip(), "")

    def test_the_config_is_found_by_walking_up_from_the_edited_file(self):
        """The hook's CWD is not guaranteed to be the project root."""
        root = self.make_project(review_hook="off", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        proc = self.run_hook(target, cwd=Path(tempfile.gettempdir()))

        self.assertEqual(
            proc.stdout.strip(), "", "config must be located from the file, not the CWD"
        )


class TheUpwardWalkStopsAtHome(HookHarness):
    """H1's `$HOME` bound — untestable from a scratch root, which is never inside it.

    A user-global `~/.aidoc/profile.yaml` is documented, so a marker at or above
    `$HOME` must not count as adoption. These tests point `$HOME` at a scratch
    directory rather than the real one.
    """

    def _home_project(self):
        home = self.make_project(review_hook="verbose", adopted=False)
        (home / ".aidoc").mkdir()  # the documented user-global marker
        target = self.place_broken_brd(home, "proj/BRD-01.md")
        return home, target

    def test_a_user_global_marker_is_not_a_project_signal(self):
        home, target = self._home_project()

        env = dict(os.environ, HOME=str(home))
        context = self.context_of(self.run_hook(target, cwd=home, env=env))

        self.assertIn("doc-brd-audit", context)
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)

    def test_the_bound_survives_a_home_spelled_with_a_trailing_slash(self):
        """A raw string compare against `$HOME` never matches, so the bound vanishes."""
        home, target = self._home_project()

        env = dict(os.environ, HOME=str(home) + "/")
        context = self.context_of(self.run_hook(target, cwd=home, env=env))

        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)

    def test_a_config_at_home_is_still_read(self):
        """The bound is on the adoption marker, not on the config.

        `$HOME` may legitimately be a project root, and refusing to read its
        config is how a user ends up unable to turn an advisory hook off.
        """
        home = self.make_project(review_hook="off", adopted=True)
        target = self.place_broken_brd(home, "proj/docs/01_BRD/BRD-01.md")

        env = dict(os.environ, HOME=str(home))
        proc = self.run_hook(target, cwd=home, env=env)

        self.assert_clean_streams(proc)
        self.assertEqual(proc.stdout.strip(), "", "review_hook: off at $HOME must be honoured")


class TheProjectCannotSteerTheLinter(HookHarness):
    """The linter runs from the plugin root, not the user's working directory."""

    def test_a_project_local_registry_is_not_consumed(self):
        """It is an adoption marker only — never a source of regexes to compile.

        The linter resolves the nearest registry by walking up from its CWD and
        compiles that registry's `id_patterns` over document text. Running from
        the plugin root means a planted registry cannot supply them; findings
        still come from the bundled one.
        """
        root = self.make_project(review_hook="verbose", adopted="registry")
        target = self.place_broken_brd(root, "BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("<untrusted-tool-output", context)
        self.assertIn("STRUCT01", context)


class UntrustedContentIsFramed(HookHarness):
    """H3: file-derived text crosses into instruction context clearly labelled."""

    def test_findings_are_wrapped_in_an_untrusted_envelope(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn('<untrusted-tool-output source="sdd_doc_lint">', context)
        self.assertIn("</untrusted-tool-output>", context)
        self.assertIn("not instructions", context)

    def test_the_filename_is_framed_too(self):
        root = self.make_project(review_hook="on", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("<untrusted-filename>BRD-01.md</untrusted-filename>", context)


class TheHookIsBounded(HookHarness):
    """M1 / P1: a declared timeout, a size cap, and a bounded findings block."""

    def test_hooks_json_declares_a_timeout(self):
        manifest = json.loads(_HOOKS_JSON.read_text(encoding="utf-8"))
        entries = [
            hook
            for group in manifest["hooks"]["PostToolUse"]
            for hook in group["hooks"]
            if hook.get("type") == "command"
        ]
        self.assertTrue(entries, "no command hook declared")
        for hook in entries:
            self.assertIsInstance(
                hook.get("timeout"), int, f"no integer timeout declared on {hook.get('command')}"
            )
            self.assertGreater(hook["timeout"], 0)

    def test_the_findings_block_is_truncated_to_a_byte_budget(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        # 40 padded sections yield ~8 KB of findings against a 4 KB budget.
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md", pad_sections=40)
        self.assertLess(target.stat().st_size, 1024 * 1024, "must stay under the size cap")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("[truncated]", context)
        self.assertIn("</untrusted-tool-output>", context, "the envelope must still close")
        self.assertLess(len(context), 6000)

    def test_a_missing_file_leaves_both_streams_clean(self):
        """The file can vanish between the tool call and the hook.

        `wc -c <"$f"` on a missing file is reported by the SHELL, so redirecting
        `wc`'s own stderr does not suppress it — and one stray byte fails the
        acceptance harness's JSON assertion.
        """
        root = self.make_project(review_hook="verbose", adopted=True)
        self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")
        gone = root / "docs" / "01_BRD" / "BRD-99.md"

        proc = self.run_hook(gone, cwd=root)

        self.assert_clean_streams(proc)
        json.loads(proc.stdout)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can read anything")
    def test_an_unreadable_file_leaves_both_streams_clean(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")
        target.chmod(0o000)
        self.addCleanup(target.chmod, 0o644)

        proc = self.run_hook(target, cwd=root)

        self.assert_clean_streams(proc)
        json.loads(proc.stdout)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "no mkfifo on this platform")
    def test_a_fifo_at_the_edited_path_does_not_block(self):
        """A FIFO would block `wc` — and then the linter — until the host timeout."""
        root = self.make_project(review_hook="verbose", adopted=True)
        target = root / "docs" / "01_BRD" / "BRD-01.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        os.mkfifo(target)

        proc = self.run_hook(target, cwd=root)

        self.assert_clean_streams(proc)
        self.assertNotIn("<untrusted-tool-output", proc.stdout)

    def test_an_oversized_document_is_not_linted(self):
        root = self.make_project(review_hook="verbose", adopted=True)
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")
        with target.open("a", encoding="utf-8") as handle:
            handle.write("\n" + "<!-- padding -->\n" * 70000)
        self.assertGreater(target.stat().st_size, 1024 * 1024)

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context)
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)


class DocsRootIsHonoured(HookHarness):
    """L4: the layer path test must not hardcode `/docs/`."""

    def test_a_configured_docs_root_is_used_for_layer_detection(self):
        root = self.make_project(review_hook="verbose", docs_root="specifications/sdd/")
        # Adoption comes from the path branch alone — no registry, no .aidoc/ —
        # which is exactly what a scaffolded greenfield project looks like.
        target = self.place_broken_brd(root, "specifications/sdd/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context)
        self.assertIn("<untrusted-tool-output", context)

    def test_a_document_outside_the_configured_docs_root_is_not_adopted(self):
        root = self.make_project(review_hook="verbose", docs_root="specifications/sdd/")
        target = self.place_broken_brd(root, "docs/01_BRD/BRD-01.md")

        context = self.context_of(self.run_hook(target, cwd=root))

        self.assertIn("doc-brd-audit", context)
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("STRUCT01", context)


if __name__ == "__main__":
    unittest.main()
