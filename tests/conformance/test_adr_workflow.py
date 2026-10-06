"""Conformance tests for Layer 05 (ADR) CNCF Serverless Workflow standard.

Validates that:
1. ADR_WORKFLOW_STANDARD.md is present and defines normative mapping, MCDA, and rules.
2. ADR-SWF-TEMPLATE.yaml adheres to Hybrid Envelope Architecture and CNCF v0.8 DSL.
3. adr-decision-analysis.sw.yaml is a valid, deterministic, compensable CNCF state machine.
4. Layer 05 documentation and registries reflect the dual-template architecture.
"""

import unittest

import yaml
from _spec import FRAMEWORK

LAYER_05 = FRAMEWORK / "layers" / "05_ADR"
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


class AdrWorkflowTest(unittest.TestCase):
    def test_adr_workflow_standard_document_present(self):
        doc = LAYER_05 / "ADR_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing ADR_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertTrue('specVersion: "0.8"' in content or "specVersion: '0.8'" in content)
        self.assertIn("Hybrid Envelope Architecture", content)
        self.assertIn("compensatedBy", content)
        self.assertIn("MCDA", content)
        self.assertIn("LangGraph", content)
        self.assertIn("adr-decision-analysis.sw.yaml", content)
        self.assertIn("Dual-Template", content)

    def test_adr_swf_template_exists_and_envelope_valid(self):
        tpl_path = LAYER_05 / "ADR-SWF-TEMPLATE.yaml"
        self.assertTrue(tpl_path.is_file(), "Missing ADR-SWF-TEMPLATE.yaml")
        with tpl_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Template must parse as a YAML mapping")
        self.assertIn("doc_id", data)
        self.assertIn("title", data)
        self.assertIn("metadata", data)
        self.assertIn("document_control", data)
        self.assertIn("context", data)
        self.assertIn("decision", data)
        self.assertIn("alternatives", data)
        self.assertIn("consequences", data)
        self.assertIn("architecture_flow", data)
        self.assertIn("implementation_assessment", data)
        self.assertIn("verification", data)
        self.assertIn("traceability", data)
        self.assertIn("related_decisions", data)
        self.assertIn("glossary", data)
        self.assertIn("appendix", data)

        meta = data["metadata"]
        self.assertEqual(meta.get("schema_version"), "1.0")
        self.assertEqual(meta.get("framework_version"), "[X.Y.Z]")
        self.assertEqual(meta.get("layer"), 5)
        self.assertEqual(meta.get("subtype"), "workflow")

        # Validate embedded CNCF workflow in architecture_flow
        arch_flow = data["architecture_flow"]
        self.assertIn("decision_workflow", arch_flow)
        wf = arch_flow["decision_workflow"]
        self.assertIsInstance(wf, dict)
        self.assertIn("id", wf)
        self.assertIn("name", wf)
        self.assertEqual(wf.get("specVersion"), "0.8")
        self.assertIn("start", wf)
        self.assertIn("states", wf)

        states = wf["states"]
        self.assertIsInstance(states, list)
        state_names = {s["name"] for s in states if "name" in s}
        self.assertIn(wf["start"], state_names)

        terminal_count = 0
        for state in states:
            s_type = state.get("type")
            self.assertIn(s_type, VALID_STATE_TYPES)

            if "transition" in state:
                self.assertIn(state["transition"], state_names)

            if "compensatedBy" in state:
                self.assertIn(state["compensatedBy"], state_names)

            if s_type == "switch":
                for cond in state.get("dataConditions", []):
                    if "transition" in cond:
                        self.assertIn(cond["transition"], state_names)
                default_target = state.get("defaultCondition", {}).get("transition")
                if default_target:
                    self.assertIn(default_target, state_names)

            if state.get("end") is True or (
                isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
            ):
                terminal_count += 1

        self.assertGreater(terminal_count, 0, "Embedded workflow must have terminal states")

    def test_adr_decision_analysis_workflow_valid(self):
        wf_path = WORKFLOWS_DIR / "adr-decision-analysis.sw.yaml"
        self.assertTrue(wf_path.is_file(), "Missing adr-decision-analysis.sw.yaml")
        with wf_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data.get("id"), "adr-decision-analysis")
        self.assertEqual(data.get("specVersion"), "0.8")
        self.assertIn("start", data)
        self.assertIn("states", data)

        states = data["states"]
        state_names = {s["name"] for s in states if "name" in s}
        self.assertIn(data["start"], state_names)

        has_parallel = False
        has_callback = False
        has_compensation = False
        terminal_count = 0

        for state in states:
            s_type = state.get("type")
            if s_type == "parallel":
                has_parallel = True
                self.assertIn("branches", state)
                self.assertGreaterEqual(len(state["branches"]), 2)
            if s_type == "callback":
                has_callback = True
            if "compensatedBy" in state:
                has_compensation = True
                self.assertIn(state["compensatedBy"], state_names)
            if "transition" in state:
                self.assertIn(state["transition"], state_names)
            if s_type == "switch":
                for cond in state.get("dataConditions", []):
                    if "transition" in cond:
                        self.assertIn(cond["transition"], state_names)
                default_target = state.get("defaultCondition", {}).get("transition")
                if default_target:
                    self.assertIn(default_target, state_names)
            if state.get("end") is True or (
                isinstance(state.get("end"), dict) and state["end"].get("terminate") is True
            ):
                terminal_count += 1

        self.assertTrue(has_parallel, "Workflow should have parallel candidate assessment")
        self.assertTrue(has_callback, "Workflow should have stakeholder RFC callback handling")
        self.assertTrue(has_compensation, "Workflow should declare compensation state")
        self.assertGreater(terminal_count, 0, "Workflow must declare terminal states")

    def test_layer_05_readme_synchronization(self):
        readme_path = LAYER_05 / "README.md"
        self.assertTrue(readme_path.is_file(), "Missing 05_ADR/README.md")
        content = readme_path.read_text(encoding="utf-8")
        self.assertIn("ADR-SWF-TEMPLATE.yaml", content)
        self.assertIn("ADR_WORKFLOW_STANDARD.md", content)
        self.assertIn("Dual-Template", content)


if __name__ == "__main__":
    unittest.main()
