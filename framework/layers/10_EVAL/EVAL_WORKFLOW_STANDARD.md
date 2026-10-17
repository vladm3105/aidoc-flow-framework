# EVAL Workflow Specification Standard: CNCF Serverless Workflow for Layer 10

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-14 |
| Author | Framework Maintainer |
| Framework Version | 0.94.0 |

Establishes the normative standard for modeling, validating, and executing Layer 10 (Evaluation & Quality Verification / EVAL) execution plans, test suite runners, and quality gate receipts using the CNCF Serverless Workflow v0.8 specification in YAML format within the SDD Hybrid Envelope Architecture.

---

## 1. Purpose & Architectural Context

In the 10-layer SDD specification (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified), Layer 10 governs evaluation strategy, execution verification, and quality gate reporting.

Each IPLAN owns exactly one EVAL document (1:1 coupling). The EVAL documents specific test suites, acceptance scenarios, and performance/security benchmarks required to prove that the implemented code satisfies all upstream contracts.

Historically, EVAL strategy documents were authored as static checklist documents ([`EVAL-TEMPLATE.yaml`](./EVAL-TEMPLATE.yaml)). While adequate for manual inspection, static files present clear operational deficiencies in automated cloud-native environments:

1. **Multi-Tier Execution Coordination**: Comprehensive evaluation spans multiple concurrent test tiers (unit, integration, acceptance, conformance, security SAST), each requiring distinct environment configurations, timeouts, and prerequisites.
2. **Deterministic Teardown & Quarantine Compensation (`compensatedBy`)**: Integration fixtures, mock containers, and staging data provisioned during evaluation require reliable saga cleanup to prevent dirty state contamination across test runs.
3. **Automated Quality Gate Evaluation**: Gating decisions must deterministically assess code coverage targets, pass rates, and blocker counts against PRD quality thresholds.
4. **Autonomous Remediation Dispatch**: When evaluation fails, autonomous agents require declarative failure routing to dispatch targeted bugfix vehicles (C1 CHG + scoped IPLAN) per [`REVIEW_REMEDIATION_FLOW.md`](../../governance/REVIEW_REMEDIATION_FLOW.md).

---

## 2. Hybrid Envelope Architecture

To maintain complete backward compatibility with structural linters (`sdd_doc_lint`, `STRUCT01`, `TAG01`), all CNCF-compliant EVAL documents adopt the **Hybrid Envelope Architecture**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Layer 10 EVAL Document Envelope (EVAL-SWF-TEMPLATE.yaml)              │
├────────────────────────────────────────────────────────────────────────┤
│  • doc_id, metadata (schema_version: "1.0", layer: 10)                 │
│  • document_control (subtype: workflow, owning_iplan: "IPLAN-NN")      │
│  • evaluation_scope (owning_iplan, upstream_sources, target_env)       │
│  • test_design (declarative EVAL.NN.SS.xxxx test case definitions)     │
│  • coverage_matrix (bidirectional traceability matrix)                 │
│  • quality_thresholds (p0_critical, p1_high, coverage thresholds)      │
│  • execution_plan (triggers: initial_eval, bug_fix_verification, etc)   │
├────────────────────────────────────────────────────────────────────────┤
│  workflow: (CNCF Serverless Workflow v0.8 YAML)                        │
│   ├── id, name, version, specVersion: "0.8"                             │
│   ├── start: IngestEvaluationScope                                     │
│   └── states:                                                          │
│       ├── [Ingest]    operation (load strategy, set thresholds)        │
│       ├── [Execute]   parallel (unit, acceptance, conformance, SAST)   │
│       ├── [Evaluate]  operation (compute scorecard metrics)            │
│       ├── [Decide]    switch (AllPassed vs HasFailures)                │
│       ├── [Teardown]  operation (cleanup fixtures compensation)        │
│       └── [Terminal]  operation (EmitReceipt / TriggerRemediation)     │
├────────────────────────────────────────────────────────────────────────┤
│  • traceability (@ears, @bdd, @tdd, @iplan references)                 │
└────────────────────────────────────────────────────────────────────────┘
```

The outer envelope preserves standard SDD metadata and section sets, while the inner `workflow:` mapping houses the executable CNCF Serverless Workflow state machine.

---

## 3. Evaluation-Verification State Machine Primitives

The evaluation and quality gate verification lifecycle maps cleanly to CNCF Serverless Workflow state types:

| Phase | Purpose | CNCF State Type | Workflow Construct |
|---|---|---|---|
| **Ingest** | Ingest trigger context and test plan | `operation` or `inject` | Validates trigger (`initial_eval`, `bug_fix_verification`) and loads thresholds |
| **Execute** | Parallel execution across test tiers | `parallel` (`allOf`) | Dispatches unit, acceptance, conformance, and security SAST suites |
| **Evaluate** | Calculate aggregated score and gate metrics | `operation` | Weighs coverage, traceability, and pass rates against thresholds |
| **Decide** | Branch on quality gate compliance | `switch` | Assesses `score >= 90 and blocker_count == 0` |
| **Receipt** | Emit immutable EVAL-REPORT receipt | `operation` (`end: true`) | Generates `EVAL-{NN}-RPT-{NNN}.yaml` and marks IPLAN Verified |
| **Remediate** | Handle defects and trigger bugfix vehicle | `operation` (`terminate: true`) | Compensates test fixtures and dispatches C1 CHG + scoped IPLAN |

---

## 4. Saga Teardown & Fixture Compensation (`compensatedBy`)

Evaluation runs that allocate external test containers, databases, or mock infrastructure MUST declare a compensating teardown state:

```yaml
- name: ExecuteEvaluationSuites
  type: parallel
  completionType: allOf
  compensatedBy: CleanupEvaluationArtifacts
  branches:
    - name: UnitSuiteBranch
      actions: [...]
    - name: AcceptanceSuiteBranch
      actions: [...]
  transition: EvaluateQualityGates
```

When unexpected harness failures or assertion errors occur, the orchestrator triggers `CleanupEvaluationArtifacts` to ensure no dirty state or orphaned resources linger in CI/staging environments.

---

## 5. Two-Graph Architecture & Dual-Template Selection Discipline

Layer 10 employs the framework's **Two-Graph Dual-Plane Architecture**, pairing an executable verification orchestration workflow with an atomic evaluation content graph:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 10 EVAL TWO-GRAPH ARCHITECTURE                               │
├────────────────────────────────────────────────────────┬────────────────────────────────────┤
│          GRAPH 1: PROCESS DAG (CONTROL PLANE)          │   GRAPH 2: CONTENT GRAPH (DATA)    │
│       EVAL-SWF-TEMPLATE.yaml (Hybrid Envelope)         │      (EVAL-GRAPH-TEMPLATE.yaml)    │
├────────────────────────────────────────────────────────┼────────────────────────────────────┤
│ • CNCF Serverless Workflow v0.8 state machine DAG      │ • SDD-GRAPH v2.0 Property Graph    │
│ • Flow of HOW to coordinate, verify & gate quality     │ • Content of WHAT tests exist      │
│ • Multi-tier parallel test execution & quality gates   │ • Test suites, benchmarks, scopes  │
│ • Gating switch states & automated receipt emission    │ • Quality thresholds & coverage    │
│ • Fixture teardown & quarantine saga compensation      │ • Relational links (evaluates etc) │
│ • Validated via LangGraph / Temporal state machine     │ • Validated via BTV engine         │
└───────────────────────────┬────────────────────────────┴─────────────────┬──────────────────┘
                            │                                              │
                            ▼                                              ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │               DOCUMENT GENERATION & PROJECTION               │
                    ├──────────────────────────────────────────────────────────────┤
                    │ • Process DAG orchestrates test execution & gate evaluation  │
                    │ • Agent actions populate and mutate atomic nodes in Data     │
                    │ • BTV verifies topological closure & test case coverage      │
                    │ • Observability Adapter projects graph into EVAL-TEMPLATE    │
                    └──────────────────────────────────────────────────────────────┘
```

Authors select between authoring configurations based on orchestration complexity:

| Criteria | Standard Companion [`EVAL-TEMPLATE.yaml`](./EVAL-TEMPLATE.yaml) | Two-Graph [`EVAL-SWF-TEMPLATE.yaml`](./EVAL-SWF-TEMPLATE.yaml) + [`EVAL-GRAPH-TEMPLATE.yaml`](./EVAL-GRAPH-TEMPLATE.yaml) |
|---|---|---|
| **Execution Complexity** | Static test checklists, atomic unit smoke runs | Multi-tier parallel test execution, conditional quality gates |
| **Fixture Lifecycle** | Stateless, in-process mocks | Multi-container fixtures, first-class saga compensation |
| **Subtype Declaration** | Standard / omitted | `subtype: workflow` in `document_control` |
| **Automated Remediation** | Manual bug reporting | Automated bugfix dispatch via `REVIEW_REMEDIATION_FLOW.md` |
| **Target Orchestrator** | Manual review, standard test runners | Autonomous coding agents, LangGraph DAG engines, CI pipelines |

---

## 6. Review & Remediation Saga (`REV-10-EVAL`)

Review and remediation of Layer 10 strategy and report artifacts is governed by [`eval-review-remediation.sw.yaml`](../../governance/workflows/review/eval-review-remediation.sw.yaml).

Per [`REVIEW_CREWS.yaml`](../../governance/REVIEW_CREWS.yaml) and the `10_IPVERIFY` playbooks, the review crew evaluates artifacts across 5 specialized perspectives:
- **`evaluator`** (weight 35%): Assesses test coverage, case design completeness, and assertion rigor.
- **`validator`** (weight 25%): Validates element ID hashes (`EVAL.NN.SS.xxxx`), pass criteria, and drift.
- **`verifier`** (weight 20%): Verifies owning IPLAN lifecycle status alignment and threshold compliance.
- **`report_generator`** (weight 10%): Verifies report receipt formatting and immutability.
- **`auditor`** (weight 10%): Checks traceability tags and compliance rules.

Author remediation is assigned to the `qa_lead` persona, bounded by a maximum of 3 iterations before escalation.

### 6.1 Closed Dual-Flow Quality Loop: Authoring & Review Saga Binding (CHG-111, GD-98)

To eliminate the decoupling between evaluation execution and review crew evaluation:

1. **Explicit Author Rubric Binding**:
   - The document envelope `metadata:` block declares `author_persona: "evaluator"` and `author_playbook: "framework/playbooks/10_IPVERIFY/evaluator.md"`.
   - Autonomous evaluation agents derive suite coverage requirements, threshold metrics, and receipt criteria directly from this rubric prior to authoring.

2. **Mandatory Review Saga Invalidation & Gating**:
   - Prior to final receipt emission (`EmitPassingReceipt` in templates or `EmitPassingReportReceipt` in runner workflows), the workflow executes `InvokeReviewSagaGate` via the `invokeReviewSaga` custom function, invoking the designated review saga subflow (`eval-review-remediation-flow`).
   - The review saga coordinates multi-agent review crew evaluation across persona playbooks, enforcing the quality gate condition:
     `${ .review_score >= 90 and .blocking_findings == 0 and .gate_passed == true }`.
   - If findings or defective test receipts are uncovered, the saga executes an automated remediation loop, halting receipt verification until all P0/P1 blockers are resolved.

---

## 7. Review Log

- **2026-10-14 — Pass 1 (Initial Ratification)**:
  - Codified Layer 10 CNCF Serverless Workflow standard, Hybrid Envelope Architecture, Arrange-Execute-Evaluate-Receipt state machine mapping, and dual-template selection discipline.
- **2026-10-14 — Pass 2 (Review Remediation & Parity)**:
  - *Gap found*: Layer 10 lacked a companion review remediation workflow (`eval-review-remediation.sw.yaml`) and conformance test coverage.
  - *Fix*: Integrated `REV-10-EVAL` specification, codified `10_IPVERIFY` review crew weights, and linked to `test_eval_workflow.py`.
