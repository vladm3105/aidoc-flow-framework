"""Conformance tests for Layer 04 (BDD) CNCF Serverless Workflow standard.

Validates that BDD-SWF-TEMPLATE.yaml adheres to the Hybrid Envelope Architecture,
that the embedded behavioral workflow graph complies with CNCF Serverless Workflow v0.8 (YAML),
that all states, transitions, and saga compensation handlers are deterministic,
and that the QA staging bdd-acceptance-run.sw.yaml execution runner is valid and synchronized.
"""

import unittest

import yaml
from _spec import FRAMEWORK

GOVERNANCE = FRAMEWORK / "governance"
LAYER_04 = FRAMEWORK / "layers" / "04_BDD"

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


class BddWorkflowTest(unittest.TestCase):
    def test_bdd_workflow_standard_document_present(self):
        doc = LAYER_04 / "BDD_WORKFLOW_STANDARD.md"
        self.assertTrue(doc.is_file(), "Missing BDD_WORKFLOW_STANDARD.md")
        content = doc.read_text(encoding="utf-8")
        self.assertTrue('specVersion: "0.8"' in content or "specVersion: '0.8'" in content)
        self.assertIn("Hybrid Envelope Architecture", content)
        self.assertIn("compensatedBy", content)
        self.assertIn("LangGraph", content)
        self.assertIn("bdd-acceptance-run.sw.yaml", content)
        self.assertIn("Dual-Template Discipline", content)

    def test_bdd_swf_template_exists_and_envelope_valid(self):
        tpl = LAYER_04 / "BDD-SWF-TEMPLATE.yaml"
        self.assertTrue(tpl.is_file(), "Missing BDD-SWF-TEMPLATE.yaml")

        with tpl.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertIsInstance(data, dict, "Template must parse as a YAML mapping")

        # Top-level SDD Envelope sections
        expected_envelope_keys = [
            "id",
            "doc_id",
            "title",
            "metadata",
            "document_control",
            "feature",
            "traceability",
            "workflow",
        ]
        for key in expected_envelope_keys:
            self.assertIn(key, data, f"Missing required envelope key '{key}'")

        meta = data.get("metadata", {})
        self.assertEqual(meta.get("schema_version"), "1.0")
        self.assertEqual(meta.get("subtype"), "workflow")
        self.assertEqual(meta.get("layer"), 4)
        self.assertEqual(meta.get("document_type"), "bdd-document")

    def test_bdd_swf_workflow_graph_integrity(self):
        tpl = LAYER_04 / "BDD-SWF-TEMPLATE.yaml"
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
                target = state["transition"]
                self.assertIn(
                    target,
                    state_names,
                    f"Transition target '{target}' from state '{s_name}' not defined",
                )

            if s_type == "switch":
                for cond in state.get("dataConditions", []):
                    self.assertIn(
                        "transition",
                        cond,
                        f"Condition in state '{s_name}' missing transition",
                    )
                    c_target = cond["transition"]
                    self.assertIn(
                        c_target,
                        state_names,
                        f"Condition target '{c_target}' from switch '{s_name}' not defined",
                    )
                if "defaultCondition" in state:
                    d_target = state["defaultCondition"].get("transition")
                    if d_target:
                        self.assertIn(
                            d_target,
                            state_names,
                            f"Default target '{d_target}' from switch '{s_name}' not defined",
                        )

        self.assertGreater(terminal_states, 0, "Workflow has no terminal state")
        self.assertGreater(len(compensation_handlers), 0, "No saga compensation declared")

        for handler in compensation_handlers:
            self.assertIn(handler, state_names, f"Compensation handler '{handler}' not defined")

    def test_bdd_acceptance_run_workflow_schema(self):
        wf_path = GOVERNANCE / "workflows" / "bdd-acceptance-run.sw.yaml"
        self.assertTrue(wf_path.is_file(), "Missing bdd-acceptance-run.sw.yaml")

        with wf_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.assertEqual(data.get("id"), "bdd-acceptance-run")
        self.assertEqual(data.get("specVersion"), "0.8")
        self.assertEqual(data.get("start"), "ProvisionStagingEnvironment")

        states = data.get("states", [])
        state_names = {s["name"] for s in states if "name" in s}
        self.assertIn("ProvisionStagingEnvironment", state_names)
        self.assertIn("DiscoverAcceptanceScenarios", state_names)
        self.assertIn("ExecuteScenarioMatrix", state_names)
        self.assertIn("EvaluateScenarioAssertions", state_names)
        self.assertIn("QuarantineFailedScenarios", state_names)
        self.assertIn("EmitAcceptanceReceipt", state_names)
        self.assertIn("TeardownStagingEnvironment", state_names)

        provision_state = next(s for s in states if s["name"] == "ProvisionStagingEnvironment")
        self.assertEqual(
            provision_state.get("compensatedBy"),
            "TeardownStagingEnvironment",
            "Provision state must compensate with Teardown",
        )

        teardown_state = next(s for s in states if s["name"] == "TeardownStagingEnvironment")
        self.assertTrue(
            teardown_state.get("end") is True,
            "Teardown state must be terminal",
        )

    def test_layer_04_readme_references_workflow(self):
        readme = LAYER_04 / "README.md"
        content = readme.read_text(encoding="utf-8")
        self.assertIn("BDD-SWF-TEMPLATE.yaml", content)
        self.assertIn("BDD_WORKFLOW_STANDARD.md", content)
        self.assertIn("bdd-acceptance-run.sw.yaml", content)


if __name__ == "__main__":
    unittest.main()
