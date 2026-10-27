"""Unit tests: IPLAN _required_when_subtype structural enforcement (CHG-140, issue #1046)."""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

_LINT_ROOT = str(Path(__file__).resolve().parents[2])


class IplanSubtypeLintTests(unittest.TestCase):
    def _run_lint_with_name(self, body: str, filename: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / filename
            f.write_text(body, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "sdd_doc_lint", td, "--format=json"],
                cwd=td,
                env={"PYTHONPATH": _LINT_ROOT, "PATH": "/usr/bin:/bin"},
                capture_output=True,
                text=True,
                check=False,
            )
            return json.loads(result.stdout or "[]")

    def test_iplan_code_build_requires_file_manifest(self):
        """code_build requires file_manifest, execution_commands, implementation_contracts, session_handoff."""
        body = textwrap.dedent("""
            doc_id: IPLAN-01
            title: "Test Implementation Plan"
            document_control:
              subtype: code_build
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
            execution_commands:
              commands: []
            implementation_contracts:
              contracts: []
            session_handoff:
              notes: "done"
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-01_test.yaml")
        struct01_sections = {f["section"] for f in findings if f["code"] == "STRUCT01"}
        self.assertIn(
            "file_manifest",
            struct01_sections,
            f"code_build must require file_manifest; got {findings}",
        )
        self.assertNotIn(
            "rollback_procedure",
            struct01_sections,
            "code_build must not require rollback_procedure",
        )

    def test_iplan_code_build_passes_with_all_code_sections(self):
        body = textwrap.dedent("""
            doc_id: IPLAN-01
            title: "Test Implementation Plan"
            document_control:
              subtype: code_build
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
            file_manifest:
              files: []
            execution_commands:
              commands: []
            implementation_contracts:
              contracts: []
            session_handoff:
              notes: "done"
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-01_test.yaml")
        struct01 = [f for f in findings if f["code"] == "STRUCT01"]
        self.assertEqual(struct01, [], f"expected no STRUCT01 findings, got {struct01}")

    def test_iplan_deploy_requires_rollback_procedure(self):
        """deploy requires rollback_procedure, smoke_tests, canary_metrics, observability_hooks, runbook_reference."""
        body = textwrap.dedent("""
            doc_id: IPLAN-02
            title: "Test Deploy Plan"
            document_control:
              subtype: deploy
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
            smoke_tests:
              tests: []
            canary_metrics:
              metrics: []
            observability_hooks:
              hooks: []
            runbook_reference:
              runbook: "doc"
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-02_test.yaml")
        struct01_sections = {f["section"] for f in findings if f["code"] == "STRUCT01"}
        self.assertIn(
            "rollback_procedure",
            struct01_sections,
            f"deploy must require rollback_procedure; got {findings}",
        )
        self.assertNotIn(
            "file_manifest",
            struct01_sections,
            "deploy must not require file_manifest",
        )

    def test_iplan_deploy_passes_with_all_deploy_sections(self):
        body = textwrap.dedent("""
            doc_id: IPLAN-02
            title: "Test Deploy Plan"
            document_control:
              subtype: deploy
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
            rollback_procedure:
              steps: []
            smoke_tests:
              tests: []
            canary_metrics:
              metrics: []
            observability_hooks:
              hooks: []
            runbook_reference:
              runbook: "doc"
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-02_test.yaml")
        struct01 = [f for f in findings if f["code"] == "STRUCT01"]
        self.assertEqual(struct01, [], f"expected no STRUCT01 findings, got {struct01}")

    def test_iplan_unrecognized_subtype_emits_struct01(self):
        body = textwrap.dedent("""
            doc_id: IPLAN-03
            title: "Test Unknown Subtype Plan"
            document_control:
              subtype: arbitrary_unknown_subtype
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-03_test.yaml")
        unrec = [
            f
            for f in findings
            if f["code"] == "STRUCT01" and "unrecognized IPLAN subtype" in f["message"]
        ]
        self.assertTrue(
            len(unrec) >= 1,
            f"expected unrecognized IPLAN subtype error, got {findings}",
        )
        self.assertEqual(unrec[0]["section"], "document_control")

    def test_iplan_without_subtype_preserves_backward_compatibility(self):
        """When document_control has no subtype, only unconditional sections are required."""
        body = textwrap.dedent("""
            doc_id: IPLAN-04
            title: "Legacy IPLAN without subtype"
            document_control:
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-04_test.yaml")
        struct01 = [f for f in findings if f["code"] == "STRUCT01"]
        self.assertEqual(
            struct01,
            [],
            f"legacy IPLAN without subtype should not fail conditional checks, got {struct01}",
        )

    def test_iplan_combined_requires_both_code_and_deploy_sections(self):
        body = textwrap.dedent("""
            doc_id: IPLAN-05
            title: "Combined Plan"
            document_control:
              subtype: combined
              status: In-Progress
            tdd_consistency:
              status: verified
            traceability:
              upstream: []
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-05_test.yaml")
        struct01_sections = {f["section"] for f in findings if f["code"] == "STRUCT01"}
        self.assertIn("file_manifest", struct01_sections)
        self.assertIn("execution_commands", struct01_sections)
        self.assertIn("implementation_contracts", struct01_sections)
        self.assertIn("session_handoff", struct01_sections)
        self.assertIn("rollback_procedure", struct01_sections)
        self.assertIn("smoke_tests", struct01_sections)
        self.assertIn("canary_metrics", struct01_sections)
        self.assertIn("observability_hooks", struct01_sections)
        self.assertIn("runbook_reference", struct01_sections)

    def test_iplan_docs_subtype_sections(self):
        body = textwrap.dedent("""
            doc_id: IPLAN-06
            title: "Docs Plan"
            document_control:
              subtype: docs
              status: In-Progress
            tdd_consistency:
              status: not-applicable
            traceability:
              upstream: []
            file_manifest:
              files: []
            implementation_contracts:
              contracts: []
            session_handoff:
              notes: "done"
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-06_test.yaml")
        struct01 = [f for f in findings if f["code"] == "STRUCT01"]
        self.assertEqual(struct01, [], f"expected no STRUCT01 for valid docs IPLAN, got {struct01}")

    def test_iplan_markdown_carrier_enforces_subtype(self):
        body = textwrap.dedent("""
            ---
            artifact_id: IPLAN-07
            layer: 8
            document_control:
              subtype: code_build
              status: In-Progress
            ---
            # IPLAN-07
            ## Document Control
            ## TDD Consistency
            ## Traceability
        """).strip()
        findings = self._run_lint_with_name(body, "IPLAN-07_test.md")
        struct01_sections = {f["section"] for f in findings if f["code"] == "STRUCT01"}
        self.assertIn(
            "file_manifest",
            struct01_sections,
            f"Markdown carrier must enforce subtype sections; got {findings}",
        )


if __name__ == "__main__":
    unittest.main()
