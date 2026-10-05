"""Conformance tests for Layer 08 (IPLAN) CNCF Serverless Workflow standard.

Validates that IPLAN-SWF-TEMPLATE.yaml adheres to the Hybrid Envelope Architecture,
that the embedded workflow graph complies with CNCF Serverless Workflow v0.8 (YAML),
that all states, transitions, and saga compensation handlers are deterministic,
and that governance contracts are properly synchronized.
"""

import unittest
import yaml

from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"
LAYER_08 = FRAMEWORK / "layers" / "08_IPLAN"

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


class IPlanWorkflowTest(unittest.TestCase):
    def test_iplan_workflow_standard_document_present(self):
        doc = GOVERNANCE / "IPLAN_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing IPLAN_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertIn('specVersion: "0.8"', content)
        self.assertIn("Hybrid Envelope Architecture", content)
        self.assertIn("compensatedBy", content)
        self.assertIn("LangGraph", content)
        self.assertIn("Rule 1: Static Inventory Parity", content)
        self.assertIn("Rule 3: Mandatory Saga Compensation on Mutating States", content)

    def test_iplan_swf_template_exists_and_envelope_valid(self):
        tpl = LAYER_08 / "IPLAN-SWF-TEMPLATE.yaml"
        self.assertTrue(tpl.is_file(), "Missing IPLAN-SWF-TEMPLATE.yaml")

        with tpl.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Template must parse as a YAML mapping")

        # Top-level SDD Envelope sections
        expected_envelope_keys = [
            "doc_id",
            "title",
            "metadata",
            "document_control",
            "file_manifest",
            "tdd_consistency",
            "workflow",
            "implementation_contracts",
            "session_handoff",
            "traceability",
        ]
        for key in expected_envelope_keys:
            self.assertIn(key, data, f"Missing required envelope key '{key}'")

        self.assertEqual(data.get("document_control", {}).get("subtype"), "workflow")
        self.assertEqual(
            data.get("metadata", {}).get("workflow_standard"),
            "CNCF-Serverless-Workflow-0.8",
        )

    def test_iplan_workflow_graph_integrity(self):
        tpl = LAYER_08 / "IPLAN-SWF-TEMPLATE.yaml"
        with tpl.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        wf = data.get("workflow", {})
        self.assertIn("id", wf)
        self.assertIn("name", wf)
        self.assertIn("version", wf)
        self.assertEqual(wf.get("specVersion"), "0.8")
        self.assertIn("start", wf)
        self.assertIn("states", wf)

        states = wf["states"]
        self.assertIsInstance(states, list)
        self.assertGreater(len(states), 0)

        state_names = {s["name"] for s in states if "name" in s}
        self.assertEqual(len(state_names), len(states), "Duplicate state names in workflow")
        self.assertIn(wf["start"], state_names, f"Start state '{wf['start']}' not in states")

        terminal_states = 0
        compensation_handlers = set()

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

            # Check compensation targets
            if "compensatedBy" in state:
                comp_target = state["compensatedBy"]
                self.assertIn(
                    comp_target,
                    state_names,
                    f"CompensatedBy in '{s_name}' targets unknown state '{comp_target}'",
                )
                compensation_handlers.add(comp_target)

            # Check terminal state
            if state.get("end") is True or (
                isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
            ):
                terminal_states += 1

        self.assertGreater(terminal_states, 0, "Workflow must contain at least one terminal state")
        self.assertGreater(
            len(compensation_handlers),
            0,
            "Workflow must declare at least one compensatedBy saga handler",
        )

    def test_governance_synchronization(self):
        gov_doc = (GOVERNANCE / "GOVERNANCE_WORKFLOW_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn("IPLAN_WORKFLOW_STANDARD.md", gov_doc)

        diag_doc = (GOVERNANCE / "DIAGRAM_STANDARDS.md").read_text(encoding="utf-8")
        self.assertIn("IPLAN", diag_doc)

        decisions = (GOVERNANCE / "DECISIONS.md").read_text(encoding="utf-8")
        self.assertIn("GD-52", decisions)
        self.assertIn("0.77.0", decisions)

        plan_std = (LAYER_08 / "PLAN_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn("workflow", plan_std)
        self.assertIn("IPLAN-SWF-TEMPLATE.yaml", plan_std)


if __name__ == "__main__":
    unittest.main()
