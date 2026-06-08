"""Unit: STRUCT01 fires when a required template section is missing."""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import plugin_bundle_root


class Struct01Tests(unittest.TestCase):
    def _run_lint(self, body: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "BRD-01_test.md"
            f.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "sdd_doc_lint", td, "--format=json"],
                env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
                capture_output=True,
                text=True,
                check=False,
            )
            return json.loads(result.stdout or "[]")

    def _run_lint_with_name(self, body: str, filename: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / filename
            f.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "sdd_doc_lint", td, "--format=json"],
                env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
                capture_output=True,
                text=True,
                check=False,
            )
            return json.loads(result.stdout or "[]")

    def test_struct01_fires_when_required_section_missing(self):
        body = textwrap.dedent("""
            ---
            artifact_id: BRD-01
            layer: 1
            ---
            # BRD-01
            ## Document Control
            ## Introduction
            ## Business Objectives
        """).strip()
        findings = self._run_lint(body)
        codes = {f["code"] for f in findings}
        self.assertIn("STRUCT01", codes, f"expected STRUCT01, got {codes}")

    def test_struct01_skipped_for_brd_index(self):
        """BRD-00_index.md (artifact_type: BRD-INDEX) has its own template
        (BRD-00_index.TEMPLATE.md); applying the standard BRD-TEMPLATE.yaml
        sections to it produces spurious STRUCT01 findings. Regression for
        task #239."""
        body = textwrap.dedent("""
            ---
            artifact_type: BRD-INDEX
            doc_id: BRD-00
            layer: 1
            ---
            # BRD-00: Business Requirements Document Index

            Master index of all BRDs for the project.

            ## Position in Document Workflow

            (intentionally lacks the 15 required BRD sections — this is an
            index doc, not a BRD instance)
        """).strip()
        findings = self._run_lint_with_name(body, "BRD-00_index.md")
        struct01 = [f for f in findings if f["code"] == "STRUCT01"]
        self.assertEqual(
            struct01,
            [],
            f"STRUCT01 should not fire on artifact_type: BRD-INDEX; got {struct01}",
        )


if __name__ == "__main__":
    unittest.main()
