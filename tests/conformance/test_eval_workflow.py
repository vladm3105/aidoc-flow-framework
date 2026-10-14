"""Conformance tests for Layer 10 (EVAL) CNCF Serverless Workflow standard.

Validates that:
1. EVAL_WORKFLOW_STANDARD.md establishes normative CNCF Serverless Workflow rules.
2. EVAL-SWF-TEMPLATE.yaml adheres to Hybrid Envelope Architecture and CNCF v0.8 DSL.
3. eval-review-remediation.sw.yaml complies with review-saga specifications.
4. Governance references in README.md and REVIEW_WORKFLOW_STANDARD.md are synchronized.
"""

import unittest
from pathlib import Path

import yaml
from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"
LAYER_10 = FRAMEWORK / "layers" / "10_EVAL"
REVIEW_WORKFLOWS = GOVERNANCE / "workflows" / "review"

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


class EvalWorkflowTest(unittest.TestCase):
    def test_eval_workflow_standard_document_present(self):
        doc = LAYER_10 / "EVAL_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing EVAL_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertIn('specVersion: "0.8"', content)
        self.assertIn("Hybrid Envelope Architecture", content)
        self.assertIn("compensatedBy", content)
        self.assertIn("REV-10-EVAL", content)
        self.assertIn("Dual-Template Selection Discipline", content)

    def test_eval_swf_template_exists_and_envelope_valid(self):
        tpl = LAYER_10 / "EVAL-SWF-TEMPLATE.yaml"
        self.assertTrue(tpl.is_file(), "Missing EVAL-SWF-TEMPLATE.yaml")

        with tpl.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Template must parse as a YAML mapping")

        expected_envelope_keys = [
            "doc_id",
            "title",
            "metadata",
            "document_control",
            "evaluation_scope",
            "test_design",
            "coverage_matrix",
            "quality_thresholds",
            "execution_plan",
            "workflow",
            "traceability",
        ]
        for key in expected_envelope_keys:
            self.assertIn(key, data, f"Missing required envelope key '{key}'")

        self.assertEqual(data.get("document_control", {}).get("subtype"), "workflow")
        self.assertEqual(
            data.get("metadata", {}).get("workflow_standard"),
            "CNCF-Serverless-Workflow-0.8",
        )
        self.assertEqual(data.get("metadata", {}).get("layer"), 10)

    def test_eval_workflow_graph_integrity(self):
        tpl = LAYER_10 / "EVAL-SWF-TEMPLATE.yaml"
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

            if state.get("end") is True or (
                isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
            ):
                terminal_states += 1

            if "compensatedBy" in state:
                compensation_handlers.add(state["compensatedBy"])

            if "transition" in state:
                trans = state["transition"]
                self.assertIn(
                    trans,
                    state_names,
                    f"State '{s_name}' transitions to undeclared state '{trans}'",
                )

            if s_type == "switch" and "dataConditions" in state:
                for cond in state["dataConditions"]:
                    if "transition" in cond:
                        self.assertIn(
                            cond["transition"],
                            state_names,
                            f"Condition '{cond.get('name')}' transitions to undeclared state '{cond['transition']}'",
                        )
                if "defaultCondition" in state and "transition" in state["defaultCondition"]:
                    self.assertIn(
                        state["defaultCondition"]["transition"],
                        state_names,
                        f"Default condition in '{s_name}' transitions to undeclared state",
                    )

        self.assertGreater(terminal_states, 0, "No terminal state found in workflow")
        for handler in compensation_handlers:
            self.assertIn(
                handler,
                state_names,
                f"Compensating state '{handler}' is not a declared state",
            )

    def test_eval_review_remediation_workflow_integrity(self):
        wf_path = REVIEW_WORKFLOWS / "eval-review-remediation.sw.yaml"
        self.assertTrue(wf_path.is_file(), "Missing eval-review-remediation.sw.yaml")

        with wf_path.open(encoding="utf-8") as f:
            wf = yaml.safe_load(f)

        self.assertIsInstance(wf, dict)
        self.assertEqual(wf.get("specVersion"), "0.8")
        self.assertEqual(wf.get("metadata", {}).get("governed_layer"), "10_EVAL")
        self.assertEqual(wf.get("metadata", {}).get("flow_code"), "REV-10-EVAL")
        self.assertIn("start", wf)
        self.assertIn("states", wf)

        states = wf["states"]
        state_names = {s["name"] for s in states if "name" in s}
        self.assertIn("PrepareReviewCrew", state_names)
        self.assertIn("DispatchReviewCrew", state_names)
        self.assertIn("EvaluateQualityGate", state_names)
        self.assertIn("EnterRemediationCycle", state_names)
        self.assertIn("RollbackRemediationPatch", state_names)

        # Check parallel review dispatch
        dispatch = next(s for s in states if s["name"] == "DispatchReviewCrew")
        self.assertEqual(dispatch.get("type"), "parallel")
        branches = dispatch.get("branches", [])
        self.assertGreaterEqual(len(branches), 4, "Must have at least 4 verification lens branches")

    def test_eval_readme_references_workflow_and_standard(self):
        readme = LAYER_10 / "README.md"
        content = readme.read_text(encoding="utf-8")
        self.assertIn("EVAL-SWF-TEMPLATE.yaml", content)
        self.assertIn("EVAL_WORKFLOW_STANDARD.md", content)
        self.assertIn("eval-review-remediation.sw.yaml", content)

    def test_review_workflow_standard_references_eval(self):
        doc = GOVERNANCE / "REVIEW_WORKFLOW_STANDARD.md"
        content = doc.read_text(encoding="utf-8")
        self.assertIn("REV-10-EVAL", content)
        self.assertIn("eval-review-remediation.sw.yaml", content)


if __name__ == "__main__":
    unittest.main()
