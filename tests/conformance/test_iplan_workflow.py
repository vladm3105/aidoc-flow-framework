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

    def test_execution_resilience_and_status_taxonomy_conformance(self):
        """Asserts CHG-120 execution resilience, non-destructive states, and status taxonomy."""
        tpl_path = LAYER_08 / "IPLAN-SWF-TEMPLATE.yaml"
        with tpl_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 1. Plane 3: File manifest must use NOT_STARTED, never PENDING
        files = data.get("file_manifest", {}).get("files", [])
        self.assertGreater(len(files), 0)
        for entry in files:
            self.assertEqual(
                entry.get("status"),
                "NOT_STARTED",
                f"File manifest entry {entry.get('path')} must use NOT_STARTED",
            )

        # 2. Execution states presence
        states = {s["name"]: s for s in data.get("workflow", {}).get("states", [])}
        self.assertIn("InitializeExecutionContext", states)
        self.assertEqual(states["InitializeExecutionContext"].get("type"), "inject")

        self.assertIn("RemediateImplementationFixes", states)
        self.assertEqual(
            states["RemediateImplementationFixes"].get("compensatedBy"),
            "RollbackSourceFiles",
            "RemediateImplementationFixes must declare compensatedBy saga handler (Rule 3)",
        )

        self.assertIn("ExecutionBlockedTerminal", states)
        blocked_end = states["ExecutionBlockedTerminal"].get("end")
        self.assertTrue(
            blocked_end is True
            or (isinstance(blocked_end, dict) and blocked_end.get("terminate") is True)
        )

        # 3. Absence of legacy review_score >= 90 (SDD-0044)
        raw_text = tpl_path.read_text(encoding="utf-8")
        self.assertNotIn("review_score", raw_text)

        std_text = (GOVERNANCE / "IPLAN_WORKFLOW_STANDARD.md").read_text(encoding="utf-8")
        self.assertNotIn("${ .review_score", std_text)

    def test_distributed_attestation_and_iplanic_compatibility(self):
        """Validates CHG-121 distributed multi-agent attestation, timeouts, and EVAL bridge."""
        # 1. IPLAN-TEMPLATE.yaml has intake_control with _required: false and work_orders attestation
        iplan_yaml = (LAYER_08 / "IPLAN-TEMPLATE.yaml").read_text(encoding="utf-8")
        iplan_data = yaml.safe_load(iplan_yaml)
        self.assertIn("intake_control", iplan_data)
        self.assertFalse(iplan_data["intake_control"].get("_required", True))
        self.assertIn("provenance", iplan_data["intake_control"])

        self.assertIn("work_orders", iplan_data.get("execution_commands", {}))
        self.assertIn("attestation:", iplan_yaml)
        self.assertIn("executor_id:", iplan_yaml)
        self.assertIn("protocol_agent_id:", iplan_yaml)
        self.assertIn("skip_audit:", iplan_yaml)
        self.assertIn("valid_until:", iplan_yaml)

        # 2. IPLAN-GRAPH-TEMPLATE.yaml has verifies relation for preflight attestation
        graph_text = (LAYER_08 / "IPLAN-GRAPH-TEMPLATE.yaml").read_text(encoding="utf-8")
        self.assertIn("preflight_attestation", graph_text)
        self.assertIn("TASK.08.02.xxxx", graph_text)
        self.assertIn('relation: "verifies"', graph_text)

        # 3. IPLAN-SWF-TEMPLATE.yaml & iplan-execution.sw.yaml have attestation functions & states
        for path in [
            LAYER_08 / "IPLAN-SWF-TEMPLATE.yaml",
            GOVERNANCE / "workflows" / "iplan-execution.sw.yaml",
        ]:
            swf_data = yaml.safe_load(path.read_text(encoding="utf-8"))
            func_names = (
                [f["name"] for f in swf_data["workflow"]["functions"] if "name" in f]
                if "workflow" in swf_data
                else [f["name"] for f in swf_data["functions"]]
            )
            self.assertIn("verifyAttestationReceipt", func_names)
            self.assertIn("verifyStepCompleteness", func_names)

            states = (
                swf_data["workflow"]["states"] if "workflow" in swf_data else swf_data["states"]
            )
            state_names = [s["name"] for s in states]
            self.assertIn("EvaluatePreFlightGate", state_names)
            self.assertIn("VerifyStepExecutionCompleteness", state_names)

            step3 = next(s for s in states if s["name"] == "Step3_ImplementTestsFirst")
            self.assertIn("timeouts", step3)
            self.assertEqual(step3["timeouts"]["stateExecTimeout"], "PT15M")
            self.assertEqual(step3["timeouts"]["actionExecTimeout"], "PT5M")

        # 4. EVAL-REPORT-TEMPLATE.yaml has receipt ref and seal hash
        eval_path = FRAMEWORK / "layers" / "10_EVAL" / "EVAL-REPORT-TEMPLATE.yaml"
        eval_data = yaml.safe_load(eval_path.read_text(encoding="utf-8"))
        self.assertIn("iplan_context", eval_data)
        self.assertIn("iplan_receipt_ref", eval_data["iplan_context"])
        self.assertIn("receipt_seal_hash", eval_data["iplan_context"])

        # 5. IPLAN_WORKFLOW_STANDARD.md contains normative §10 and §11
        std_text = (GOVERNANCE / "IPLAN_WORKFLOW_STANDARD.md").read_text(encoding="utf-8")
        self.assertIn(
            "## 10. Cryptographic Agent Attribution & Step Digital Signatures (CHG-121)", std_text
        )
        self.assertIn(
            "## 11. Distributed Worker Handover, Timeouts & Completeness (CHG-121)", std_text
        )
        self.assertIn("valid_until", std_text)
        self.assertIn("canonical_hash", std_text)


if __name__ == "__main__":
    unittest.main()
