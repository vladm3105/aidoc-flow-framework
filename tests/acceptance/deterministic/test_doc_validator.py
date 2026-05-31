"""Deterministic acceptance: doc-validator runs sdd_doc_lint over a broken fixture
and surfaces structural findings.

doc-validator is a prompt-driven SKILL.md whose deterministic counterpart is
sdd_doc_lint. broken_chain by itself only carries an HTML-comment cascade
marker that the linter ignores by design, so the most reliable broken fixture
to demonstrate doc-validator's "find structural breakage" surface is the
canonical layer-1 broken fixture (BRD-01_missing_section.md, STRUCT01).
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
        """Sanity: broken_chain's only diff from golden is an HTML-comment cascade
        marker that sdd_doc_lint ignores by design. Both lint to no structural
        findings; cross-artifact validation is out of scope."""
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
