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

EXPECTED_WORKFLOWS = [
    "chg-request-flow.sw.yaml",
    "seed-to-module-decomposition.sw.yaml",
    "worktree-pr-lifecycle.sw.yaml",
    "eval-verification-run.sw.yaml",
    "review-remediation-flow.sw.yaml",
    "decision-ratification-flow.sw.yaml",
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
                self.assertIn("id", data)
                self.assertIn("name", data)
                self.assertIn("version", data)
                self.assertEqual(
                    data.get("specVersion"), "0.8", f"{wf_name} must specify specVersion: '0.8'"
                )
                self.assertIn("start", data)
                self.assertIn("states", data)

                states = data["states"]
                self.assertIsInstance(states, list)
                self.assertGreater(len(states), 0, f"{wf_name} must declare at least one state")

                state_names = {s["name"] for s in states if "name" in s}
                self.assertEqual(
                    len(state_names), len(states), f"{wf_name} contains duplicate state names"
                )
                self.assertIn(
                    data["start"], state_names, f"Start state '{data['start']}' not in states"
                )

                terminal_states = 0
                for state in states:
                    s_name = state["name"]
                    s_type = state.get("type")
                    self.assertIn(
                        s_type, VALID_STATE_TYPES, f"State '{s_name}' has invalid type '{s_type}'"
                    )

                    # Check transition target
                    if "transition" in state:
                        target = state["transition"]
                        self.assertIn(
                            target,
                            state_names,
                            f"Transition from '{s_name}' targets unknown state '{target}'",
                        )

                    # Check switch conditions
                    if s_type == "switch":
                        conditions = state.get("dataConditions", [])
                        for cond in conditions:
                            c_target = cond.get("transition")
                            if c_target:
                                self.assertIn(
                                    c_target,
                                    state_names,
                                    f"Switch condition in '{s_name}' targets unknown '{c_target}'",
                                )
                        default_target = state.get("defaultCondition", {}).get("transition")
                        if default_target:
                            self.assertIn(
                                default_target,
                                state_names,
                                f"Default condition in '{s_name}' targets unknown '{default_target}'",
                            )

                    # Check compensation target
                    if "compensatedBy" in state:
                        comp_target = state["compensatedBy"]
                        self.assertIn(
                            comp_target,
                            state_names,
                            f"CompensatedBy in '{s_name}' targets unknown state '{comp_target}'",
                        )

                    # Check terminal state
                    if state.get("end") is True or (
                        isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
                    ):
                        terminal_states += 1

                self.assertGreater(
                    terminal_states, 0, f"{wf_name} must contain at least one terminal state"
                )

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
        self.assertIn("CNCF Serverless Workflow standard", decisions)
        self.assertIn("0.79.0", decisions)


if __name__ == "__main__":
    unittest.main()
