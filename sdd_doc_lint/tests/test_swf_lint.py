"""Unit tests for sdd_doc_lint/swf_lint.py (CNCF Serverless Workflow linter)."""

from __future__ import annotations

import unittest
from pathlib import Path

from sdd_doc_lint.swf_lint import (
    EXIT_CLEAN,
    lint_workflow_dict,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class SwfLintRulesTest(unittest.TestCase):
    def test_valid_minimal_workflow(self):
        wf = {
            "id": "test-flow",
            "name": "Test Flow",
            "version": "1.0",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "transition": "StateB",
                },
                {
                    "name": "StateB",
                    "type": "operation",
                    "end": True,
                },
            ],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        errors = [f for f in findings if f.severity == "ERROR"]
        self.assertEqual(errors, [])

    def test_swf_l001_missing_required_fields(self):
        wf = {
            "id": "test-flow",
            "specVersion": "0.7",  # wrong version
            "states": [],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        rules = [f.rule for f in findings]
        self.assertIn("SWF-L001", rules)
        messages = " ".join(f.message for f in findings)
        self.assertIn("name", messages)
        self.assertIn("start", messages)
        self.assertIn("0.8", messages)

    def test_swf_l002_invalid_state_type(self):
        wf = {
            "id": "test-flow",
            "name": "Test Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "unsupported_type",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        rules = [f.rule for f in findings]
        self.assertIn("SWF-L002", rules)

    def test_swf_l003_missing_terminal_state(self):
        wf = {
            "id": "test-flow",
            "name": "Test Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "transition": "StateA",
                }
            ],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        rules = [f.rule for f in findings]
        self.assertIn("SWF-L003", rules)

    def test_swf_l004_undefined_transition_target(self):
        wf = {
            "id": "test-flow",
            "name": "Test Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "transition": "NonExistentState",
                },
                {
                    "name": "StateB",
                    "type": "operation",
                    "end": True,
                },
            ],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        rules = [f.rule for f in findings]
        self.assertIn("SWF-L004", rules)

    def test_swf_l005_invalid_compensation_target(self):
        wf = {
            "id": "test-flow",
            "name": "Test Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "compensatedBy": "MissingCompensationState",
                    "transition": "StateB",
                },
                {
                    "name": "StateB",
                    "type": "operation",
                    "end": True,
                },
            ],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        rules = [f.rule for f in findings]
        self.assertIn("SWF-L005", rules)

    def test_swf_l006_parallel_branch_completeness(self):
        wf = {
            "id": "test-flow",
            "name": "Test Flow",
            "specVersion": "0.8",
            "start": "ParallelState",
            "states": [
                {
                    "name": "ParallelState",
                    "type": "parallel",
                    "branches": [
                        {"name": "BranchA", "actions": []},  # empty actions
                    ],
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "test.sw.yaml")
        rules = [f.rule for f in findings]
        self.assertIn("SWF-L006", rules)

    def test_swf_l007_review_crew_parity(self):
        review_crews = {
            "BRD": {
                "review": {
                    "architect": 30,
                    "business_analyst": 30,
                    "auditor": 20,
                    "chaos_engineer": 12,
                    "security_engineer": 8,
                }
            }
        }
        # Only dispatches architect and auditor; missing 3 personas
        wf = {
            "id": "brd-review-flow",
            "name": "BRD Review Flow",
            "specVersion": "0.8",
            "governed_layer": "01_BRD",
            "start": "DispatchCrew",
            "states": [
                {
                    "name": "DispatchCrew",
                    "type": "parallel",
                    "branches": [
                        {
                            "name": "ArchitectBranch",
                            "actions": [
                                {
                                    "name": "ExecArch",
                                    "functionRef": {"arguments": {"persona": "architect"}},
                                }
                            ],
                        },
                        {
                            "name": "AuditorBranch",
                            "actions": [
                                {
                                    "name": "ExecAuditor",
                                    "functionRef": {"arguments": {"persona": "auditor"}},
                                }
                            ],
                        },
                    ],
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "brd-review.sw.yaml", review_crews=review_crews)
        warnings = [f for f in findings if f.rule == "SWF-L007"]
        self.assertEqual(len(warnings), 1)
        self.assertIn("missing declared personas", warnings[0].message)

    def test_swf_l008_valid_template_passes(self):
        wf = {
            "id": "brd-flow",
            "name": "BRD Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "metadata": {
                "author_persona": "business_analyst",
                "author_playbook": "framework/playbooks/01_BRD/business_analyst.md",
            },
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "transition": "InvokeReviewSagaGate",
                },
                {
                    "name": "InvokeReviewSagaGate",
                    "type": "operation",
                    "actions": [
                        {
                            "name": "invokeSaga",
                            "functionRef": {
                                "refName": "invokeReviewSaga",
                                "arguments": {
                                    "workflowId": "brd-review-remediation-flow",
                                },
                            },
                        }
                    ],
                    "end": True,
                },
            ],
        }
        findings = lint_workflow_dict(wf, "BRD-SWF-TEMPLATE.yaml", repo_root=REPO_ROOT)
        l008_findings = [f for f in findings if f.rule == "SWF-L008"]
        self.assertEqual(l008_findings, [])

    def test_swf_l008_missing_persona_or_playbook(self):
        wf = {
            "id": "brd-flow",
            "name": "BRD Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "metadata": {},
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "BRD-SWF-TEMPLATE.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L008"]
        self.assertTrue(any("author_persona" in f.message for f in errors))
        self.assertTrue(any("author_playbook" in f.message for f in errors))

    def test_swf_l008_nonexistent_playbook_path(self):
        wf = {
            "id": "brd-flow",
            "name": "BRD Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "metadata": {
                "author_persona": "business_analyst",
                "author_playbook": "framework/playbooks/fake/does_not_exist.md",
            },
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "BRD-SWF-TEMPLATE.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L008"]
        self.assertTrue(any("not found on disk" in f.message for f in errors))

    def test_swf_l008_missing_review_saga_invocation(self):
        wf = {
            "id": "brd-flow",
            "name": "BRD Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "metadata": {
                "author_persona": "business_analyst",
                "author_playbook": "framework/playbooks/01_BRD/business_analyst.md",
            },
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "BRD-SWF-TEMPLATE.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L008"]
        self.assertTrue(any("review saga invocation state" in f.message for f in errors))

    def test_swf_l008_non_template_workflow_exempt(self):
        wf = {
            "id": "brd-validation",
            "name": "BRD Validation",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "brd-business-validation.sw.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L008"]
        self.assertEqual(errors, [])

    def test_swf_l009_valid_closeout_passes(self):
        wf = {
            "id": "brd-flow",
            "name": "BRD Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "metadata": {
                "author_persona": "business_analyst",
                "author_playbook": "framework/playbooks/01_BRD/business_analyst.md",
            },
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "transition": "InvokeReviewSagaGate",
                },
                {
                    "name": "InvokeReviewSagaGate",
                    "type": "operation",
                    "actions": [
                        {
                            "name": "invokeSaga",
                            "functionRef": {
                                "refName": "invokeReviewSaga",
                                "arguments": {
                                    "workflowId": "brd-review-remediation-flow",
                                },
                            },
                        }
                    ],
                    "transition": "RemediateLayerDraft",
                },
                {
                    "name": "RemediateLayerDraft",
                    "type": "operation",
                    "actions": [
                        {
                            "name": "remediate",
                            "functionRef": {
                                "refName": "remediateLayerFindings",
                            },
                        }
                    ],
                    "transition": "VerifyLayerCloseoutGate",
                },
                {
                    "name": "VerifyLayerCloseoutGate",
                    "type": "operation",
                    "actions": [
                        {
                            "name": "verifyGate",
                            "functionRef": {
                                "refName": "verifyLayerBoundaryGate",
                            },
                        }
                    ],
                    "transition": "SealLayerDocumentBaseline",
                },
                {
                    "name": "SealLayerDocumentBaseline",
                    "type": "operation",
                    "actions": [
                        {
                            "name": "sealDoc",
                            "functionRef": {
                                "refName": "sealDocumentBaseline",
                            },
                        }
                    ],
                    "transition": "EmitLayerHandoffEvent",
                },
                {
                    "name": "EmitLayerHandoffEvent",
                    "type": "operation",
                    "produceEvents": [
                        {"eventRef": "BrdClosedAndBaselinedEvent"}
                    ],
                    "end": True,
                },
            ],
        }
        findings = lint_workflow_dict(wf, "BRD-SWF-TEMPLATE.yaml", repo_root=REPO_ROOT)
        l009_errors = [f for f in findings if f.rule == "SWF-L009"]
        self.assertEqual(l009_errors, [])

    def test_swf_l009_missing_closeout_elements(self):
        # Missing all 4 closeout elements
        wf = {
            "id": "brd-flow",
            "name": "BRD Flow",
            "specVersion": "0.8",
            "start": "StateA",
            "metadata": {
                "author_persona": "business_analyst",
                "author_playbook": "framework/playbooks/01_BRD/business_analyst.md",
            },
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "transition": "InvokeReviewSagaGate",
                },
                {
                    "name": "InvokeReviewSagaGate",
                    "type": "operation",
                    "actions": [
                        {
                            "name": "invokeSaga",
                            "functionRef": {
                                "refName": "invokeReviewSaga",
                                "arguments": {
                                    "workflowId": "brd-review-remediation-flow",
                                },
                            },
                        }
                    ],
                    "end": True,
                },
            ],
        }
        findings = lint_workflow_dict(wf, "BRD-SWF-TEMPLATE.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L009"]
        self.assertEqual(len(errors), 4)
        messages = " ".join(f.message for f in errors)
        self.assertIn("in-situ remediation loop state", messages)
        self.assertIn("layer closeout gate verification state", messages)
        self.assertIn("document baseline sealing state", messages)
        self.assertIn("downstream handoff event emission", messages)

    def test_swf_l009_standalone_workflow_enforced(self):
        wf = {
            "id": "brd-validation",
            "name": "BRD Validation",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "brd-business-validation.sw.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L009"]
        self.assertEqual(len(errors), 4)

    def test_swf_l009_non_layer_workflow_exempt(self):
        wf = {
            "id": "toolchain-event-broker",
            "name": "Toolchain Event Broker",
            "specVersion": "0.8",
            "start": "StateA",
            "states": [
                {
                    "name": "StateA",
                    "type": "operation",
                    "end": True,
                }
            ],
        }
        findings = lint_workflow_dict(wf, "toolchain-event-broker.sw.yaml", repo_root=REPO_ROOT)
        errors = [f for f in findings if f.rule == "SWF-L009"]
        self.assertEqual(errors, [])


class SwfLintLiveWorkflowsTest(unittest.TestCase):
    def test_all_governance_workflows_pass_clean(self):
        wf_dir = REPO_ROOT / "framework" / "governance" / "workflows"
        self.assertTrue(wf_dir.is_dir())
        rc = main([str(wf_dir)])
        self.assertEqual(rc, EXIT_CLEAN, "All governance workflows must lint clean")

    def test_all_layer_templates_pass_clean(self):
        layers_dir = REPO_ROOT / "framework" / "layers"
        self.assertTrue(layers_dir.is_dir())
        rc = main([str(layers_dir)])
        self.assertEqual(rc, EXIT_CLEAN, "All layer templates with workflows must lint clean")


if __name__ == "__main__":
    unittest.main()
