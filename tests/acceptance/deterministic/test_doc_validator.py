"""Deterministic acceptance: doc-validator runs on broken chain via sdd_doc_lint."""

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
    def test_lint_runs_on_broken_chain(self):
        broken = FIXTURES_ROOT / "fullpath" / "broken_chain"
        self.assertTrue(broken.is_dir(), "broken_chain fixture missing")
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
        self.assertTrue(findings, "broken_chain expected to produce findings; got none")
