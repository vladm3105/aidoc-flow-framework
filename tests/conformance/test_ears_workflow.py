"""Conformance tests for Layer 03 (EARS) CNCF Serverless Workflow standard.

Validates that:
1. EARS_WORKFLOW_STANDARD.md is present and defines normative mapping, DAG invariants, and rules.
2. EARS-SWF-TEMPLATE.yaml adheres to Hybrid Envelope Architecture and CNCF v0.8 DSL with all 6 required sections.
3. ears-requirements-validation.sw.yaml is a valid, deterministic, compensable CNCF state machine.
4. Layer 03 documentation reflects the dual-template architecture.
"""

import unittest

import yaml
from _spec import FRAMEWORK

LAYER_03 = FRAMEWORK / "layers" / "03_EARS"
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


class EarsWorkflowTest(unittest.TestCase):
    def test_ears_workflow_standard_document_present(self):
        doc = LAYER_03 / "EARS_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing EARS_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertTrue('specVersion: "0.8"' in content or "specVersion: '0.8'" in content)
        self.assertIn("Hybrid Envelope", content)
        self.assertIn("compensatedBy", content)
        self.assertIn("DAG", content)
        self.assertIn("BDD-Readiness", content)
        self.assertIn("LangGraph", content)
        self.assertIn("ears-requirements-validation.sw.yaml", content)
        self.assertIn("Dual-Template", content)

    def test_ears_swf_template_exists_and_envelope_valid(self):
        tpl_path = LAYER_03 / "EARS-SWF-TEMPLATE.yaml"
        self.assertTrue(tpl_path.is_file(), "Missing EARS-SWF-TEMPLATE.yaml")
        with tpl_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Template must parse as a YAML mapping")
        self.assertIn("doc_id", data)
        self.assertIn("title", data)
        self.assertIn("metadata", data)
        self.assertIn("document_control", data)
        self.assertIn("purpose_and_context", data)
        self.assertIn("requirements", data)
        self.assertIn("quality_attributes", data)
        self.assertIn("traceability", data)
        self.assertIn("glossary", data)

        meta = data["metadata"]
        self.assertEqual(meta.get("schema_version"), "1.0")
        self.assertEqual(meta.get("framework_version"), "[X.Y.Z]")
        self.assertEqual(meta.get("layer"), 3)
        self.assertEqual(meta.get("subtype"), "workflow")

        # Validate embedded CNCF workflow in requirements
        reqs = data["requirements"]
        self.assertIn("workflow_definition", reqs)
        wf = reqs["workflow_definition"]
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

    def test_ears_requirements_validation_workflow_valid(self):
        wf_path = WORKFLOWS_DIR / "ears-requirements-validation.sw.yaml"
        self.assertTrue(wf_path.is_file(), "Missing ears-requirements-validation.sw.yaml")
        with wf_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data.get("id"), "ears-requirements-validation")
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

        self.assertTrue(has_parallel, "Workflow should have parallel dependency resolution")
        self.assertTrue(has_callback, "Workflow should have clarification callback handling")
        self.assertTrue(has_compensation, "Workflow should declare compensation state")
        self.assertGreater(terminal_count, 0, "Workflow must declare terminal states")

    def test_layer_03_readme_synchronization(self):
        readme_path = LAYER_03 / "README.md"
        self.assertTrue(readme_path.is_file(), "Missing 03_EARS/README.md")
        content = readme_path.read_text(encoding="utf-8")
        self.assertIn("EARS-SWF-TEMPLATE.yaml", content)
        self.assertIn("EARS_WORKFLOW_STANDARD.md", content)
        self.assertIn("CNCF Serverless Workflow", content)


if __name__ == "__main__":
    unittest.main()
