"""Deterministic acceptance: doc-validator runs sdd_doc_lint over a broken fixture
and surfaces structural findings.

doc-validator is a prompt-driven SKILL.md whose deterministic counterpart is
sdd_doc_lint. broken_chain's breakage is a broken *cascade* — an HTML-comment
marker the linter ignores by design, plus upstream elements its downstreams
still cite — so what it yields is TRACE-RES-001, not structural findings. The
canonical layer-1 broken fixture (BRD-01_missing_section.md, STRUCT01) is
therefore the one that demonstrates doc-validator's "find structural breakage"
surface.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import plugin_bundle_root


class DocValidatorTests(unittest.TestCase):
    def test_lint_emits_struct01_on_layer_1_broken_fixture(self):
        broken = FIXTURES_ROOT / "layer_01_brd" / "broken"
        self.assertTrue(broken.is_dir(), "layer_01_brd/broken fixture missing")
        result = subprocess.run(
            [sys.executable, "-m", "sdd_doc_lint", str(broken), "--format=json"],
            env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertIn(
            result.returncode, (0, 1), f"sdd_doc_lint exit {result.returncode}\n{result.stderr}"
        )
        try:
            findings = json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            self.fail(f"sdd_doc_lint did not emit valid JSON:\n{result.stdout}")
        codes = {f["code"] for f in findings}
        self.assertIn(
            "STRUCT01",
            codes,
            f"doc-validator should surface STRUCT01 on broken fixture; got {codes}",
        )

    def test_lint_runs_cleanly_on_broken_chain(self):
        """Sanity: broken_chain lints to parseable output. NOT to a clean run.

        Measured 2026-09-04: rc=1, 37 findings, every one a `TRACE-RES-001`
        *error*. They are the point of the fixture — its cascade is deliberately
        broken — but "runs cleanly" in this method's name means "produces
        parseable JSON", not "is quiet". Cross-artifact validation is out of
        scope, which is the only thing asserted below.

        **`golden_chain` and `broken_chain` differ in five files, and always
        have** — an earlier revision of this docstring claimed one HTML-comment
        cascade marker was the whole difference, and it was never true. The
        marker (`02_PRD/PRD-01_golden.md`) is only the flag; the breakage is that
        broken_chain omits the BRD functional requirement and the PRD feature its
        downstreams cite, and its three `.yaml` downstreams carry a bare
        document-start `---` with no `doc_id` (plus IPLAN's `subtype` and three
        `tdd_ref` fields). Measured at `5037a253^`, before either recent repair:
        the same five files already differed.

        Attribution, since the earlier revision got this wrong too: `golden_chain`
        received its `doc_id` and closing fences in `f128af41`, NOT in PR #580 —
        that PR (issue #478) repaired the three per-layer copies and touched no
        `golden_chain` file. PR #579 (issue #577) re-authored §7 on the golden
        side only. Repairing broken_chain's three fences is tracked on #636;
        update this docstring when it lands.
        """
        broken_chain = FIXTURES_ROOT / "fullpath" / "broken_chain"
        if not broken_chain.is_dir():
            self.skipTest("broken_chain fixture not present")
        result = subprocess.run(
            [sys.executable, "-m", "sdd_doc_lint", str(broken_chain), "--format=json"],
            env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
            capture_output=True,
            text=True,
            check=False,
        )
        # Should run successfully and produce parseable JSON.
        self.assertIn(result.returncode, (0, 1))
        json.loads(result.stdout or "[]")  # must parse
