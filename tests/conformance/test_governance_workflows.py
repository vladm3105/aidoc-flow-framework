"""Conformance tests for Governance Workflow Standard and CNCF Serverless Workflows.

Validates that declarative workflow graphs adhere to CNCF Serverless Workflow v0.8 (YAML),
that all states and transitions are deterministic and reachable, and that governance
contracts (GOVERNANCE_WORKFLOW_STANDARD.md, DIAGRAM_STANDARDS.md, DECISIONS.md) are synchronized.
"""

import unittest

import yaml
from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"
WORKFLOWS_DIR = GOVERNANCE / "workflows"
REVIEW_WORKFLOWS_DIR = WORKFLOWS_DIR / "review"

EXPECTED_WORKFLOWS = [
    "chg-request-flow.sw.yaml",
    "seed-to-module-decomposition.sw.yaml",
    "worktree-pr-lifecycle.sw.yaml",
    "eval-verification-run.sw.yaml",
    "review-remediation-flow.sw.yaml",
    "decision-ratification-flow.sw.yaml",
    "bdd-acceptance-run.sw.yaml",
    "tdd-test-execution.sw.yaml",
    "spec-choreography-contract.sw.yaml",
    "adr-decision-analysis.sw.yaml",
    "ears-requirements-validation.sw.yaml",
    "prd-feature-decomposition.sw.yaml",
    "brd-business-validation.sw.yaml",
]

EXPECTED_REVIEW_WORKFLOWS = [
    "brd-review-remediation.sw.yaml",
    "prd-review-remediation.sw.yaml",
    "ears-review-remediation.sw.yaml",
    "bdd-review-remediation.sw.yaml",
    "adr-review-remediation.sw.yaml",
    "spec-review-remediation.sw.yaml",
    "tdd-review-remediation.sw.yaml",
    "iplan-review-remediation.sw.yaml",
    "chg-review-remediation.sw.yaml",
]

VALID_STATE_TYPES = {
    "operation",
    "switch",
    "parallel",
    "callback",
    "event",
    "sleep",
    "inject",
    "foreach",
}


class GovernanceWorkflowsTest(unittest.TestCase):
    def test_workflow_standard_document_present(self):
        doc = GOVERNANCE / "GOVERNANCE_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing GOVERNANCE_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertIn('specVersion: "0.8"', content)
        self.assertIn("LangGraph", content)
        self.assertIn("Rule 1: Declarative Single Source of Truth", content)
        self.assertIn("Rule 2: Deterministic Terminal States", content)

    def test_expected_workflows_exist(self):
        self.assertTrue(WORKFLOWS_DIR.is_dir(), "Missing governance/workflows directory")
        for wf_name in EXPECTED_WORKFLOWS:
            with self.subTest(workflow=wf_name):
                wf_path = WORKFLOWS_DIR / wf_name
                self.assertTrue(wf_path.is_file(), f"Missing workflow file: {wf_name}")

    def test_workflow_schema_and_graph_integrity(self):
        for wf_name in EXPECTED_WORKFLOWS:
            with self.subTest(workflow=wf_name):
                wf_path = WORKFLOWS_DIR / wf_name
                with wf_path.open(encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                self.assertIsInstance(data, dict, f"{wf_name} must parse as a YAML mapping")
                self.assertIn("id", data, f"{wf_name} missing 'id'")
                self.assertIn("name", data, f"{wf_name} missing 'name'")
                self.assertEqual(
                    data.get("specVersion"), "0.8", f"{wf_name} must target specVersion 0.8"
                )
                self.assertIn("start", data, f"{wf_name} missing 'start' state")
                self.assertIn("states", data, f"{wf_name} missing 'states' list")

                states = data["states"]
                self.assertIsInstance(states, list, f"{wf_name} 'states' must be a list")
                self.assertGreater(len(states), 0, f"{wf_name} must declare at least one state")

                state_names = {s["name"] for s in states if isinstance(s, dict) and "name" in s}
                self.assertIn(
                    data["start"],
                    state_names,
                    f"{wf_name} start state '{data['start']}' not found in states",
                )

                terminal_states = 0
                for state in states:
                    s_name = state.get("name", "<unnamed>")
                    s_type = state.get("type")
                    self.assertIn(
                        s_type,
                        VALID_STATE_TYPES,
                        f"{wf_name} state '{s_name}' has invalid type '{s_type}'",
                    )

                    # Check transitions exist
                    if "transition" in state:
                        target = state["transition"]
                        self.assertIn(
                            target,
                            state_names,
                            f"{wf_name} state '{s_name}' transitions to undefined state '{target}'",
                        )

                    # Check switch dataCondition transitions
                    if s_type == "switch":
                        conditions = state.get("dataConditions", [])
                        for cond in conditions:
                            if "transition" in cond:
                                self.assertIn(
                                    cond["transition"],
                                    state_names,
                                    f"{wf_name} switch condition '{cond.get('name')}' transitions to undefined state",
                                )
                        default_trans = state.get("defaultCondition", {}).get("transition")
                        if default_trans:
                            self.assertIn(
                                default_trans,
                                state_names,
                                f"{wf_name} switch defaultCondition transitions to undefined state",
                            )

                    # Check compensatedBy references
                    if "compensatedBy" in state:
                        comp_target = state["compensatedBy"]
                        self.assertIn(
                            comp_target,
                            state_names,
                            f"{wf_name} state '{s_name}' compensatedBy undefined state '{comp_target}'",
                        )

                    # Check terminal state
                    if state.get("end") is True or (
                        isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
                    ):
                        terminal_states += 1

                self.assertGreater(
                    terminal_states, 0, f"{wf_name} must contain at least one terminal state"
                )

    def test_review_workflow_standard_document_present(self):
        doc = GOVERNANCE / "REVIEW_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing REVIEW_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertIn('specVersion: "0.8"', content)
        self.assertIn("REV-PASS", content)
        self.assertIn("REV-AUTO", content)
        self.assertIn("REV-CHG", content)
        self.assertIn("REV-01-BRD", content)
        self.assertIn("REV-09-CHG", content)

    def test_expected_review_workflows_exist(self):
        self.assertTrue(
            REVIEW_WORKFLOWS_DIR.is_dir(), "Missing governance/workflows/review directory"
        )
        for wf_name in EXPECTED_REVIEW_WORKFLOWS:
            with self.subTest(review_workflow=wf_name):
                wf_path = REVIEW_WORKFLOWS_DIR / wf_name
                self.assertTrue(wf_path.is_file(), f"Missing review workflow file: {wf_name}")

    def test_review_workflow_schema_and_graph_integrity(self):
        for wf_name in EXPECTED_REVIEW_WORKFLOWS:
            with self.subTest(review_workflow=wf_name):
                wf_path = REVIEW_WORKFLOWS_DIR / wf_name
                with wf_path.open(encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                self.assertIsInstance(data, dict, f"{wf_name} must parse as a YAML mapping")
                self.assertIn("id", data, f"{wf_name} missing 'id'")
                self.assertIn("name", data, f"{wf_name} missing 'name'")
                self.assertEqual(
                    data.get("specVersion"), "0.8", f"{wf_name} must target specVersion 0.8"
                )
                self.assertIn("start", data, f"{wf_name} missing 'start' state")
                self.assertIn("states", data, f"{wf_name} missing 'states' list")

                states = data["states"]
                self.assertIsInstance(states, list, f"{wf_name} 'states' must be a list")
                self.assertGreater(len(states), 0, f"{wf_name} must declare at least one state")

                state_names = {s["name"] for s in states if isinstance(s, dict) and "name" in s}
                self.assertIn(
                    data["start"],
                    state_names,
                    f"{wf_name} start state '{data['start']}' not found in states",
                )

                terminal_states = 0
                for state in states:
                    s_name = state.get("name", "<unnamed>")
                    s_type = state.get("type")
                    self.assertIn(
                        s_type,
                        VALID_STATE_TYPES,
                        f"{wf_name} state '{s_name}' has invalid type '{s_type}'",
                    )

                    if "transition" in state:
                        target = state["transition"]
                        self.assertIn(
                            target,
                            state_names,
                            f"{wf_name} state '{s_name}' transitions to undefined state '{target}'",
                        )

                    if s_type == "switch":
                        conditions = state.get("dataConditions", [])
                        for cond in conditions:
                            if "transition" in cond:
                                self.assertIn(
                                    cond["transition"],
                                    state_names,
                                    f"{wf_name} switch condition '{cond.get('name')}' transitions to undefined state",
                                )
                        default_trans = state.get("defaultCondition", {}).get("transition")
                        if default_trans:
                            self.assertIn(
                                default_trans,
                                state_names,
                                f"{wf_name} switch defaultCondition transitions to undefined state",
                            )

                    if "compensatedBy" in state:
                        comp_target = state["compensatedBy"]
                        self.assertIn(
                            comp_target,
                            state_names,
                            f"{wf_name} state '{s_name}' compensatedBy undefined state '{comp_target}'",
                        )

                    if state.get("end") is True or (
                        isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
                    ):
                        terminal_states += 1

                self.assertGreater(
                    terminal_states, 0, f"{wf_name} must contain at least one terminal state"
                )

    def test_workflow_linter_passes_all_workflows(self):
        from sdd_doc_lint.swf_lint import lint_path

        for wf_name in EXPECTED_WORKFLOWS:
            with self.subTest(core_workflow=wf_name):
                wf_path = WORKFLOWS_DIR / wf_name
                findings = lint_path(wf_path)
                errors = [f for f in findings if f.severity == "ERROR"]
                self.assertEqual(errors, [], f"swf_lint found errors in {wf_name}: {errors}")

        for wf_name in EXPECTED_REVIEW_WORKFLOWS:
            with self.subTest(review_workflow=wf_name):
                wf_path = REVIEW_WORKFLOWS_DIR / wf_name
                findings = lint_path(wf_path)
                errors = [f for f in findings if f.severity == "ERROR"]
                self.assertEqual(errors, [], f"swf_lint found errors in {wf_name}: {errors}")

    def test_diagram_standards_synchronization(self):
        diag_standards = (GOVERNANCE / "DIAGRAM_STANDARDS.md").read_text(encoding="utf-8")
        self.assertIn(
            "Governance State Machines & Workflow Graphs (CNCF Serverless Workflow)", diag_standards
        )
        self.assertIn(".sw.yaml", diag_standards)
        self.assertIn("GOVERNANCE_WORKFLOW_STANDARD.md", diag_standards)

    def test_decisions_synchronization(self):
        decisions = (GOVERNANCE / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("GD-51", decisions)
        self.assertIn("GD-53", decisions)
        self.assertIn("GD-54", decisions)
        self.assertIn("GD-55", decisions)
        self.assertIn("GD-56", decisions)
        self.assertIn("GD-57", decisions)
        self.assertIn("GD-58", decisions)
        self.assertIn("GD-59", decisions)
        self.assertIn("GD-60", decisions)
        self.assertIn("CNCF Serverless Workflow standard", decisions)


if __name__ == "__main__":
    unittest.main()
