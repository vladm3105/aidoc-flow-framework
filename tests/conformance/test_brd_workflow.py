"""Conformance tests for Layer 01 (BRD) CNCF Serverless Workflow standard.

Validates that:
1. BRD_WORKFLOW_STANDARD.md is present and defines normative mapping, value stream analysis, and rules.
2. BRD-SWF-TEMPLATE.yaml adheres to Hybrid Envelope Architecture and CNCF v0.8 DSL with all 17 required sections.
3. brd-business-validation.sw.yaml is a valid, deterministic, compensable CNCF state machine.
4. Layer 01 documentation reflects the dual-template architecture.
"""

import unittest

import yaml
from _spec import FRAMEWORK

LAYER_01 = FRAMEWORK / "layers" / "01_BRD"
GOVERNANCE = FRAMEWORK / "governance"
WORKFLOWS_DIR = GOVERNANCE / "workflows"

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


class BrdWorkflowTest(unittest.TestCase):
    def test_brd_workflow_standard_document_present(self):
        doc = LAYER_01 / "BRD_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing BRD_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertTrue('specVersion: "0.8"' in content or "specVersion: '0.8'" in content)
        self.assertIn("Hybrid Envelope", content)
        self.assertIn("compensatedBy", content)
        self.assertIn("Context", content)
        self.assertIn("Value Stream", content)
        self.assertIn("ROI", content)
        self.assertIn("LangGraph", content)
        self.assertIn("brd-business-validation.sw.yaml", content)
        self.assertIn("Dual-Template", content)

    def test_brd_swf_template_exists_and_envelope_valid(self):
        tpl_path = LAYER_01 / "BRD-SWF-TEMPLATE.yaml"
        self.assertTrue(tpl_path.is_file(), "Missing BRD-SWF-TEMPLATE.yaml")
        with tpl_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Template must parse as a YAML mapping")
        self.assertIn("doc_id", data)
        self.assertIn("title", data)
        self.assertIn("metadata", data)
        self.assertIn("document_control", data)
        self.assertIn("executive_summary", data)
        self.assertIn("introduction", data)
        self.assertIn("business_objectives", data)
        self.assertIn("project_scope", data)
        self.assertIn("stakeholders", data)
        self.assertIn("functional_requirements", data)
        self.assertIn("quality_expectations", data)
        self.assertIn("acceptance_criteria", data)
        self.assertIn("constraints_and_assumptions", data)
        self.assertIn("risk_management", data)
        self.assertIn("adr_topics", data)
        self.assertIn("traceability", data)
        self.assertIn("diagrams", data)
        self.assertIn("approval", data)
        self.assertIn("glossary", data)
        self.assertIn("appendix", data)

        meta = data.get("metadata", {})
        self.assertEqual(meta.get("schema_version"), "1.0")
        self.assertEqual(meta.get("framework_version"), "[X.Y.Z]")
        self.assertEqual(meta.get("subtype"), "workflow")

        # Check embedded workflow definition
        vsm = data.get("value_stream_mapping", {})
        wf = vsm.get("workflow_definition")
        self.assertIsNotNone(wf, "Missing workflow_definition in value_stream_mapping")
        self.assertEqual(wf.get("specVersion"), "0.8")
        self.assertIn("states", wf)
        self.assertGreaterEqual(len(wf["states"]), 5)

    def test_brd_business_validation_workflow_valid_cncf(self):
        wf_path = WORKFLOWS_DIR / "brd-business-validation.sw.yaml"
        self.assertTrue(wf_path.is_file(), "Missing brd-business-validation.sw.yaml")
        with wf_path.open(encoding="utf-8") as f:
            wf = yaml.safe_load(f)

        self.assertEqual(wf.get("id"), "brd-business-validation")
        self.assertEqual(wf.get("specVersion"), "0.8")
        self.assertIn("start", wf)
        self.assertIn("states", wf)

        states = {s["name"]: s for s in wf["states"]}
        self.assertIn(wf["start"], states, "Start state must exist")

        # Validate state types and transitions
        for s_name, s_data in states.items():
            s_type = s_data.get("type")
            self.assertIn(s_type, VALID_STATE_TYPES, f"Invalid state type in {s_name}: {s_type}")
            if "transition" in s_data:
                target = s_data["transition"]
                self.assertIn(target, states, f"Invalid transition target {target} from {s_name}")
            if s_type == "switch" and "dataConditions" in s_data:
                for cond in s_data["dataConditions"]:
                    if "transition" in cond:
                        self.assertIn(
                            cond["transition"],
                            states,
                            f"Invalid switch condition transition in {s_name}",
                        )
            if "compensatedBy" in s_data:
                comp = s_data["compensatedBy"]
                self.assertIn(
                    comp,
                    states,
                    f"Compensation state {comp} not found for {s_name}",
                )

        # Reachability test from start state
        visited = set()
        queue = [wf["start"]]
        while queue:
            curr = queue.pop(0)
            if curr in visited or curr not in states:
                continue
            visited.add(curr)
            s_data = states[curr]
            if "transition" in s_data:
                queue.append(s_data["transition"])
            if s_data.get("type") == "switch" and "dataConditions" in s_data:
                for cond in s_data["dataConditions"]:
                    if "transition" in cond:
                        queue.append(cond["transition"])
                if "defaultCondition" in s_data and "transition" in s_data["defaultCondition"]:
                    queue.append(s_data["defaultCondition"]["transition"])
            if "compensatedBy" in s_data:
                queue.append(s_data["compensatedBy"])

        self.assertEqual(
            len(visited),
            len(states),
            f"Unreachable states detected: {set(states) - visited}",
        )

    def test_brd_readme_references_workflow_template(self):
        readme = LAYER_01 / "README.md"
        self.assertTrue(readme.is_file(), "Missing 01_BRD/README.md")
        content = readme.read_text(encoding="utf-8")
        self.assertIn("BRD-SWF-TEMPLATE.yaml", content)
        self.assertIn("BRD_WORKFLOW_STANDARD.md", content)
        self.assertIn("Dual-Template", content)
        self.assertIn("GD-61", content)
