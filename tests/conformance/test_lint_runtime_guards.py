"""Conformance: the linter diagnoses its own missing prerequisites, and warning
findings can reach a caller.

Locks the PLUGIN-PREPROD-001 PR 2 fixes for ``tools/sdd_doc_lint/``:

* **B4 (linter half)** — PyYAML is an unguarded module-level import. Absent, the
  linter dies with a traceback whose top line names ``yaml`` and whose exit code
  (1) is indistinguishable from "this document has error findings". It must exit
  **3** with a one-line diagnostic naming PyYAML.
* **The interpreter floor is diagnosed, not tripped over.** ``enum.StrEnum``
  landed in Python 3.11 and stock macOS still ships 3.9 as ``/usr/bin/python3``.
  The check has to run *before* the import it protects, or the user gets an
  ``ImportError`` traceback about a name they have never heard of.
* **Exit 3 is distinct.** Exit 2 already carries two meanings — argparse usage
  error, and "registry unavailable" from the ``OSError`` handler. A third would
  defeat the point of the fix, so the other two are asserted to still be 2.
* **L5** — warning-severity findings are unreachable today: ``__main__`` returns
  0 unless a finding is ``error``, so the plugin's review hook (which speaks only
  when the linter exits 1) can never surface one despite ``verbose`` mode
  claiming to. ``--warn-exit`` makes them reachable **and the hook must pass it**
  — the flag closes nothing on its own.

The PyYAML-absent case is exercised by blocking the import in a subprocess
(a ``sitecustomize.py`` on a scratch ``PYTHONPATH`` that raises
``ModuleNotFoundError`` from a meta-path finder), which is a genuine absence
rather than a stubbed module. The interpreter floor cannot be exercised on the
running interpreter at all, so it is split into a pure helper that is called with
a fake ``version_info`` plus a source-order assertion that the helper runs before
the import it guards.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLS = _REPO_ROOT / "tools"
_LINT_INIT = _TOOLS / "sdd_doc_lint" / "__init__.py"
_HOOK = _REPO_ROOT / "platforms" / "claude-code-plugin" / "hooks" / "sdd-doc-review.sh"
_VALID_BRD = (
    _REPO_ROOT / "tests" / "acceptance" / "fixtures" / "layer_01_brd" / "valid" / "BRD-01_golden.md"
)
_BROKEN_BRD = (
    _REPO_ROOT / "tests" / "acceptance" / "fixtures" / "negative" / "brd-broken-sections.md"
)

#: A single section this long trips one `STY02` WARNING and nothing else, which
#: is what a "warnings only" document has to be to distinguish exit 0 from 1.
_PAD_SECTION = "\n## Pad 0\n\n" + " ".join(f"word{i}" for i in range(400)) + "\n"

_EXIT_PREREQUISITE = 3


def _scratch(case: unittest.TestCase) -> Path:
    root = Path(tempfile.mkdtemp(prefix="aidoc-lint-guard-")).resolve()
    case.addCleanup(shutil.rmtree, root, ignore_errors=True)
    return root


def _run_lint(*args: str, env: dict | None = None, cwd: Path | None = None):
    """Invoke the canonical linter exactly as a consumer does."""
    environ = dict(os.environ)
    environ["PYTHONPATH"] = str(_TOOLS)
    if env:
        for key, value in env.items():
            if value is None:
                environ.pop(key, None)
            else:
                environ[key] = value
    return subprocess.run(
        [sys.executable, "-m", "sdd_doc_lint", *args],
        capture_output=True,
        text=True,
        env=environ,
        cwd=str(cwd) if cwd else str(_REPO_ROOT),
        timeout=120,
    )


class LintGuardHarness(unittest.TestCase):
    def setUp(self):
        self.assertTrue(_VALID_BRD.is_file(), f"fixture not found: {_VALID_BRD}")
        self.assertTrue(_BROKEN_BRD.is_file(), f"fixture not found: {_BROKEN_BRD}")

    def warnings_only_doc(self, root: Path, relative: str = "BRD-01.md") -> Path:
        """A document whose only finding is a WARNING.

        Asserted here rather than assumed: if the fixture ever gains an ERROR,
        every `--warn-exit` test below would pass for the wrong reason.
        """
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_VALID_BRD.read_text(encoding="utf-8") + _PAD_SECTION, encoding="utf-8")
        proc = _run_lint("--format", "json", str(target))
        findings = json.loads(proc.stdout)
        self.assertTrue(findings, "expected at least one finding")
        self.assertEqual(
            [f["severity"] for f in findings],
            ["warning"] * len(findings),
            f"fixture is not warnings-only: {findings}",
        )
        return target

    def block_pyyaml(self, root: Path) -> Path:
        """A scratch directory that makes ``import yaml`` genuinely fail.

        A meta-path finder rather than a stub module: a stub would have to guess
        which exception a real absence raises, and the guard's whole job is to
        catch the real one.
        """
        blocker = root / "no-pyyaml"
        blocker.mkdir(parents=True, exist_ok=True)
        (blocker / "sitecustomize.py").write_text(
            "import sys\n"
            "\n"
            "\n"
            "class _NoYaml:\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            '        if fullname == "yaml" or fullname.startswith("yaml."):\n'
            '            raise ModuleNotFoundError(f"No module named {fullname!r}", '
            "name=fullname)\n"
            "        return None\n"
            "\n"
            "\n"
            "sys.meta_path.insert(0, _NoYaml())\n",
            encoding="utf-8",
        )
        # Proven, not assumed: if `sitecustomize` were not picked up (site
        # disabled, name shadowed), every assertion below would test a linter
        # that still has PyYAML.
        probe = subprocess.run(
            [sys.executable, "-c", "import yaml"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(blocker)},
            timeout=60,
        )
        self.assertNotEqual(probe.returncode, 0, "the PyYAML blocker did not take effect")
        # Positive control. Without it, a host that simply has no PyYAML would
        # let these tests pass with the blocker doing nothing at all — the
        # blocker would be untested scaffolding and the guard unproven.
        control = subprocess.run(
            [sys.executable, "-c", "import yaml"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            control.returncode, 0, "PyYAML is absent on this host; the blocker proves nothing"
        )
        return blocker

    def break_pyyaml(self, root: Path) -> Path:
        """A scratch directory where PyYAML is *present but broken*.

        The guard catches ``ImportError``, not just ``ModuleNotFoundError``, and
        says so in a comment. This is the fixture that holds it to that: a
        module that imports and then fails is the shape a half-installed C
        extension takes, and narrowing the guard to ``ModuleNotFoundError``
        silently reverts that case to a traceback at exit 1.
        """
        broken = root / "broken-pyyaml"
        broken.mkdir(parents=True, exist_ok=True)
        # Multi-line and long on purpose. A real broken C extension reports the
        # absolute path of the site-packages that failed, over several lines —
        # which both breaks the one-line contract and publishes host layout into
        # a CI log, so the message has to be bounded and not merely caught.
        (broken / "yaml.py").write_text(
            "raise ImportError(\n"
            '    "cannot load /home/someuser/.venv/lib/python3.12/site-packages/"\n'
            '    "_yaml.cpython-312-x86_64-linux-gnu.so: undefined symbol\\n"\n'
            '    "referenced from libyaml.so.2\\n" + "padding " * 100\n'
            ")\n",
            encoding="utf-8",
        )
        return broken


class MissingPyYAMLIsDiagnosed(LintGuardHarness):
    """B4 (linter half): an absent PyYAML is named, not tracebacked."""

    def test_exit_code_and_diagnostic(self):
        root = _scratch(self)
        blocker = self.block_pyyaml(root)
        target = root / "BRD-01.md"
        target.write_text(_VALID_BRD.read_text(encoding="utf-8"), encoding="utf-8")

        proc = _run_lint(str(target), env={"PYTHONPATH": f"{blocker}{os.pathsep}{_TOOLS}"})

        self.assertEqual(
            proc.returncode,
            _EXIT_PREREQUISITE,
            f"expected exit {_EXIT_PREREQUISITE}; stderr={proc.stderr!r}",
        )
        self.assertIn("PyYAML", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(proc.stdout, "", f"nothing belongs on stdout: {proc.stdout!r}")

    def test_a_broken_install_is_diagnosed_too(self):
        """Present-but-broken PyYAML raises ``ImportError``, not its subclass.

        Narrowing the guard to ``ModuleNotFoundError`` passes every other test
        in this module — the blocker above raises the subclass — while sending
        this case back to a traceback at exit 1.
        """
        root = _scratch(self)
        broken = self.break_pyyaml(root)
        target = root / "BRD-01.md"
        target.write_text(_VALID_BRD.read_text(encoding="utf-8"), encoding="utf-8")

        proc = _run_lint(str(target), env={"PYTHONPATH": f"{broken}{os.pathsep}{_TOOLS}"})

        self.assertEqual(
            proc.returncode,
            _EXIT_PREREQUISITE,
            f"expected exit {_EXIT_PREREQUISITE}; stderr={proc.stderr!r}",
        )
        self.assertIn("PyYAML", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(len(proc.stderr.strip().splitlines()), 1, proc.stderr)
        self.assertLess(len(proc.stderr), 400, "the interpolated cause is unbounded")
        self.assertNotIn("referenced from", proc.stderr, "only the first line belongs here")

    def test_diagnostic_is_one_line(self):
        """The plugin hook forwards nothing on exit 3, but the pre-commit and CI
        callers show stderr verbatim — a multi-line dump there buries the cause.
        """
        root = _scratch(self)
        blocker = self.block_pyyaml(root)
        target = root / "BRD-01.md"
        target.write_text(_VALID_BRD.read_text(encoding="utf-8"), encoding="utf-8")

        proc = _run_lint(str(target), env={"PYTHONPATH": f"{blocker}{os.pathsep}{_TOOLS}"})

        self.assertEqual(len(proc.stderr.strip().splitlines()), 1, proc.stderr)


class ExitThreeIsDistinct(LintGuardHarness):
    """Exit 2 keeps its two existing meanings; the new condition gets its own."""

    def test_usage_error_is_still_two(self):
        proc = _run_lint()  # no paths — argparse
        self.assertEqual(proc.returncode, 2, proc.stderr)

    def test_registry_unavailable_is_still_two(self):
        root = _scratch(self)
        target = root / "BRD-01.md"
        target.write_text(_VALID_BRD.read_text(encoding="utf-8"), encoding="utf-8")

        proc = _run_lint(str(target), env={"SDD_REGISTRY": str(root / "nope.yaml")})

        self.assertEqual(proc.returncode, 2, f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertIn("registry unavailable", proc.stderr)


class InterpreterFloorIsDiagnosed(LintGuardHarness):
    """The Python floor is stated and checked before the import that needs it."""

    def _module(self):
        sys.path.insert(0, str(_TOOLS))
        self.addCleanup(lambda: sys.path.remove(str(_TOOLS)))
        import sdd_doc_lint

        return sdd_doc_lint

    def test_floor_helper_rejects_old_interpreters(self):
        mod = self._module()
        self.assertEqual(mod.MIN_PYTHON, (3, 11))
        message = mod.python_floor_error((3, 9, 6))
        self.assertIsNotNone(message, "3.9 must be rejected")
        # The ORDERED clause, not two substrings. Swapping the two format
        # arguments produces "needs Python 3.9 or newer (running 3.11)" — which
        # contains both and is actively misleading to the one user it is for.
        self.assertIn("needs Python 3.11 or newer (running 3.9)", message)

    def test_floor_helper_accepts_the_running_interpreter(self):
        mod = self._module()
        self.assertIsNone(mod.python_floor_error(tuple(sys.version_info)))
        self.assertIsNone(mod.python_floor_error((3, 11, 0)))

    def test_floor_check_precedes_the_import_it_guards(self):
        """Source order, because a guard that runs after ``from enum import
        StrEnum`` produces the traceback it exists to replace.
        """
        source = _LINT_INIT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        floor_line = None
        strenum_line = None
        for node in ast.walk(tree):
            if (
                floor_line is None
                and isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "python_floor_error"
            ):
                floor_line = node.lineno
            if (
                strenum_line is None
                and isinstance(node, ast.ImportFrom)
                and node.module == "enum"
                and any(alias.name == "StrEnum" for alias in node.names)
            ):
                strenum_line = node.lineno
        self.assertIsNotNone(floor_line, "the floor check is never called at import time")
        self.assertIsNotNone(strenum_line, "`from enum import StrEnum` not found")
        self.assertLess(floor_line, strenum_line)

    def test_module_parses_on_the_floor_it_names(self):
        """A guard in a file that will not compile on 3.9 never runs.

        ``feature_version`` is best-effort, but it does reject the syntax most
        likely to creep in (``match``, and 3.10+ grammar), which is enough to
        catch the mistake that would silently disarm the diagnostic.
        """
        source = _LINT_INIT.read_text(encoding="utf-8")
        try:
            ast.parse(source, feature_version=(3, 9))
        except SyntaxError as exc:  # pragma: no cover - the failure is the point
            self.fail(f"{_LINT_INIT.name} does not parse under Python 3.9 syntax: {exc}")

    def test_postponed_annotations_keep_the_guard_evaluable(self):
        """Parsing is not enough — the guard's own code must *evaluate* on 3.9.

        ``python_floor_error`` is annotated ``tuple[int, ...] | None``, which is
        inert only because of ``from __future__ import annotations``. Drop that
        line — a plausible cleanup, since ruff targets py311 — and on 3.9 the
        ``def`` evaluates its annotations, ``TypeError`` is raised at import, and
        the user gets a traceback at exit 1: exactly the failure this guard
        replaces, in exactly the population it serves. The mutant still parses
        under 3.9 grammar, so the test above does not catch it.
        """
        tree = ast.parse(_LINT_INIT.read_text(encoding="utf-8"))
        future_line = None
        helper_line = None
        for node in ast.walk(tree):
            if (
                future_line is None
                and isinstance(node, ast.ImportFrom)
                and node.module == "__future__"
                and any(alias.name == "annotations" for alias in node.names)
            ):
                future_line = node.lineno
            if (
                helper_line is None
                and isinstance(node, ast.FunctionDef)
                and node.name == "python_floor_error"
            ):
                helper_line = node.lineno
        self.assertIsNotNone(
            future_line,
            "`from __future__ import annotations` is gone: the floor guard's own "
            "annotations would now be evaluated at import time on the very "
            "interpreters it exists to diagnose",
        )
        self.assertIsNotNone(helper_line, "`python_floor_error` not found")
        self.assertLess(future_line, helper_line)

    def test_guard_fires_end_to_end_on_an_old_interpreter(self):
        """The guard's real path, not a proxy for it.

        ``sys.version_info`` is assignable, so a ``sitecustomize`` on the
        subprocess's path can present the running interpreter as 3.9 and the
        import-time branch executes for real — diagnostic, exit code and all.
        Kept alongside the source-order checks rather than replacing them: on a
        3.12 host this passes even against the annotation mutant above.
        """
        root = _scratch(self)
        fake = root / "old-python"
        fake.mkdir()
        (fake / "sitecustomize.py").write_text(
            'import sys\n\nsys.version_info = (3, 9, 6, "final", 0)\n', encoding="utf-8"
        )
        target = root / "BRD-01.md"
        target.write_text(_VALID_BRD.read_text(encoding="utf-8"), encoding="utf-8")

        proc = _run_lint(str(target), env={"PYTHONPATH": f"{fake}{os.pathsep}{_TOOLS}"})

        self.assertEqual(
            proc.returncode,
            _EXIT_PREREQUISITE,
            f"expected exit {_EXIT_PREREQUISITE}; stderr={proc.stderr!r}",
        )
        self.assertIn("needs Python 3.11 or newer (running 3.9)", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(len(proc.stderr.strip().splitlines()), 1, proc.stderr)


class WarningFindingsAreReachable(LintGuardHarness):
    """L5: ``--warn-exit`` makes warning-severity findings observable."""

    def test_warnings_only_document_exits_zero_by_default(self):
        """The default contract is unchanged — CI depends on it."""
        root = _scratch(self)
        target = self.warnings_only_doc(root)
        self.assertEqual(_run_lint(str(target)).returncode, 0)

    def test_warnings_only_document_exits_one_under_warn_exit(self):
        root = _scratch(self)
        target = self.warnings_only_doc(root)
        proc = _run_lint("--warn-exit", str(target))
        self.assertEqual(proc.returncode, 1, f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
        self.assertIn("STY02", proc.stdout)

    def test_clean_document_still_exits_zero_under_warn_exit(self):
        root = _scratch(self)
        target = root / "BRD-01.md"
        target.write_text(_VALID_BRD.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(_run_lint("--warn-exit", str(target)).returncode, 0)

    def test_error_document_exits_one_either_way(self):
        root = _scratch(self)
        target = root / "BRD-01.md"
        target.write_text(_BROKEN_BRD.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertEqual(_run_lint(str(target)).returncode, 1)
        self.assertEqual(_run_lint("--warn-exit", str(target)).returncode, 1)


class TheHookPassesWarnExit(LintGuardHarness):
    """L5 closes only if the hook actually passes the flag.

    The scratch project is built outside the repo and outside ``$HOME`` for the
    reason ``test_plugin_hook_safety`` documents: the hook's upward walk would
    otherwise reach a real adoption marker.
    """

    def setUp(self):
        super().setUp()
        self.assertIsNotNone(
            shutil.which("jq"), "jq is required: without it the hook exits 0 silently"
        )
        self.assertTrue(_HOOK.is_file(), f"hook not found: {_HOOK}")

    def adopted_verbose_project(self) -> Path:
        root = _scratch(self)
        home = str(Path.home().resolve())
        self.assertFalse(
            str(root).startswith(str(_REPO_ROOT) + os.sep) or str(root).startswith(home + os.sep),
            f"scratch root {root} would make the adoption walk false-pass",
        )
        (root / ".aidoc").mkdir()
        (root / ".claude").mkdir()
        (root / ".claude" / "aidoc-flow.config.yaml").write_text(
            'schema: 1\nreview_hook: "verbose"\n', encoding="utf-8"
        )
        return root

    def run_hook(self, target: Path, cwd: Path, env: dict | None = None):
        return subprocess.run(
            ["bash", str(_HOOK)],
            input=json.dumps({"tool_input": {"file_path": str(target)}}),
            capture_output=True,
            text=True,
            cwd=str(cwd),
            env=env,
            timeout=120,
        )

    def test_exit_three_leaves_the_hook_silent_but_still_nudging(self):
        """The hook's own contract for the code this PR introduced.

        Covered only by accident before: the sibling crash test used to provoke
        exit 3 by shadowing PyYAML, so repairing *that* test (it had stopped
        exercising the crash path) would have left exit 3 asserted nowhere. A
        stub interpreter states the contract without depending on how the code
        is provoked.
        """
        root = self.adopted_verbose_project()
        target = self.warnings_only_doc(root, "docs/01_BRD/BRD-01.md")

        bindir = root / "stubbin"
        bindir.mkdir()
        stub = bindir / "python3"
        stub.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' 'sdd-doc-lint: PyYAML is required but could not be imported"
            " (No module named yaml); install it with `python3 -m pip install pyyaml`.' >&2\n"
            # Finding-SHAPED, and still must not be forwarded: exit 3 means the
            # linter declined to run, so its output describes nothing. Without
            # this line the grammar filter alone would carry the assertions and
            # the rc test could be widened to `-ne 0` unnoticed.
            "printf '%s\\n' '/tmp/x/BRD-01.md:1: [ERROR STRUCT01] fabricated by a stub' >&2\n"
            f"exit {_EXIT_PREREQUISITE}\n",
            encoding="utf-8",
        )
        stub.chmod(0o755)

        proc = self.run_hook(
            target,
            cwd=root,
            env=dict(os.environ, PATH=f"{bindir}{os.pathsep}{os.environ.get('PATH', '')}"),
        )

        self.assertEqual(proc.returncode, 0, f"stderr={proc.stderr!r}")
        self.assertEqual(proc.stderr, "", f"hook wrote to stderr: {proc.stderr!r}")
        context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("doc-brd-audit", context, "the nudge must survive a missing prerequisite")
        self.assertNotIn("<untrusted-tool-output", context)
        self.assertNotIn("PyYAML", context, "a setup diagnostic is not a structural finding")
        self.assertNotIn("STRUCT01", context, "exit 3 means the linter never looked at the file")

    def test_warning_only_findings_reach_the_model(self):
        root = self.adopted_verbose_project()
        target = self.warnings_only_doc(root, "docs/01_BRD/BRD-01.md")

        proc = self.run_hook(target, cwd=root)

        self.assertEqual(proc.returncode, 0, f"stderr={proc.stderr!r}")
        self.assertEqual(proc.stderr, "", f"hook wrote to stderr: {proc.stderr!r}")
        context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("STY02", context)
        self.assertIn("WARNING", context)


if __name__ == "__main__":
    unittest.main()
