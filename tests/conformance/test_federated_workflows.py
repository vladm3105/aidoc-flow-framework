"""Conformance tests for Federated Multi-Project CNCF Serverless Workflows.

Validates that:
1. MULTI_PROJECT_FEDERATED_STANDARD.md establishes normative multi-project contracts.
2. All 5 federated workflow state machines exist under framework/governance/workflows/:
   - multi-repo-contract-sync.sw.yaml
   - cross-project-ci-dispatch.sw.yaml
   - context-slicing-generation.sw.yaml
   - stack-policy-validation.sw.yaml
   - support-ticket-escalation.sw.yaml
3. All workflows comply with CNCF Serverless Workflow DSL v0.8.
4. All workflows pass sdd_doc_lint.swf_lint with 0 errors.
"""

import subprocess
import sys
import unittest
from pathlib import Path

import yaml
from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"
WORKFLOWS = GOVERNANCE / "workflows"

FEDERATED_WORKFLOWS = [
    "multi-repo-contract-sync.sw.yaml",
    "cross-project-ci-dispatch.sw.yaml",
    "context-slicing-generation.sw.yaml",
    "stack-policy-validation.sw.yaml",
    "support-ticket-escalation.sw.yaml",
]

VALID_STATE_TYPES = frozenset(
    {
        "operation",
        "switch",
        "parallel",
        "callback",
        "event",
        "sleep",
        "inject",
        "foreach",
    }
)


class FederatedWorkflowsConformanceTest(unittest.TestCase):
    def test_multi_project_federated_standard_document_present(self):
        doc = GOVERNANCE / "MULTI_PROJECT_FEDERATED_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing MULTI_PROJECT_FEDERATED_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertIn("Quad-Pillar Corporate Ecosystem", content)
        self.assertIn("Multi-Repo Isolation & Distribution Model", content)
        self.assertIn("aidoc-contracts", content)
        self.assertIn("aidoc-tools", content)
        self.assertIn("contracts-registry.yaml", content)
        self.assertIn("iplan.proto", content)
        self.assertIn("change_event.proto", content)
        self.assertIn("test_oracle.proto", content)
        self.assertIn("support_ticket.proto", content)
        self.assertIn("stack_policy.proto", content)
        self.assertIn("Context Slicing Engine Specification", content)

    def test_all_five_federated_workflows_exist(self):
        for wf_name in FEDERATED_WORKFLOWS:
            wf_path = WORKFLOWS / wf_name
            self.assertTrue(wf_path.is_file(), f"Missing federated workflow file: {wf_name}")

    def test_federated_workflows_cncf_spec_compliance(self):
        for wf_name in FEDERATED_WORKFLOWS:
            wf_path = WORKFLOWS / wf_name
            with wf_path.open(encoding="utf-8") as f:
                wf = yaml.safe_load(f)

            self.assertIsInstance(wf, dict, f"{wf_name} must parse as a YAML mapping")
            self.assertEqual(wf.get("specVersion"), "0.8", f"{wf_name} specVersion must be 0.8")
            self.assertTrue(wf.get("id"), f"{wf_name} must have a non-empty id")
            self.assertTrue(wf.get("name"), f"{wf_name} must have a non-empty name")
            self.assertTrue(wf.get("version"), f"{wf_name} must have a non-empty version")

            start_state = wf.get("start")
            self.assertTrue(start_state, f"{wf_name} must declare a start state")

            states = wf.get("states", [])
            self.assertIsInstance(states, list, f"{wf_name} states must be a list")
            self.assertGreater(len(states), 0, f"{wf_name} must define at least one state")

            state_names = {s.get("name") for s in states if isinstance(s, dict)}
            self.assertIn(start_state, state_names, f"{wf_name} start state '{start_state}' not in states")

            has_terminal_state = False
            for s in states:
                s_name = s.get("name")
                s_type = s.get("type")
                self.assertIn(s_type, VALID_STATE_TYPES, f"{wf_name}:{s_name} invalid state type '{s_type}'")

                # Check terminal state
                end_clause = s.get("end")
                if end_clause is True or (isinstance(end_clause, dict) and end_clause.get("terminate") is True):
                    has_terminal_state = True

                # Check transition targets
                trans = s.get("transition")
                if trans:
                    self.assertIn(trans, state_names, f"{wf_name}:{s_name} transition target '{trans}' not found")

                # Check switch condition targets
                for cond in s.get("dataConditions", []):
                    c_trans = cond.get("transition")
                    if c_trans:
                        self.assertIn(c_trans, state_names, f"{wf_name}:{s_name} condition target '{c_trans}' not found")
                def_cond = s.get("defaultCondition", {})
                if isinstance(def_cond, dict) and def_cond.get("transition"):
                    d_trans = def_cond["transition"]
                    self.assertIn(d_trans, state_names, f"{wf_name}:{s_name} defaultCondition target '{d_trans}' not found")

                # Check SAGA compensation target
                comp = s.get("compensatedBy")
                if comp:
                    self.assertIn(comp, state_names, f"{wf_name}:{s_name} compensatedBy target '{comp}' not found")

            self.assertTrue(has_terminal_state, f"{wf_name} must declare at least one terminal state")

    def test_swf_lint_clean_pass(self):
        cmd = [sys.executable, "-m", "sdd_doc_lint.swf_lint"] + [str(WORKFLOWS / wf) for wf in FEDERATED_WORKFLOWS]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(
            result.returncode,
            0,
            f"swf_lint failed on federated workflows:\n{result.stdout}\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
