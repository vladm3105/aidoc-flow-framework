# Plan: Codify Full Layer Closeout and Downstream Handoff Cycles across Layer SWF Templates (CHG-112, GD-99)

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Ready |
| Last Updated | 2026-10-17 |
| Author | Framework Maintainer |
| Framework Version | 0.94.0 |
| Target Framework Version | 0.95.0 (C2 Minor Spec & Tooling Release) |
| Authority | Decision GD-99 (`DEC-CHG-112`), [Decision D-0013 / GD-13](../framework/governance/DECISIONS.md), [`REVIEW_REMEDIATION_FLOW.md`](../framework/governance/REVIEW_REMEDIATION_FLOW.md), [`GOVERNANCE_WORKFLOW_STANDARD.md`](../framework/governance/GOVERNANCE_WORKFLOW_STANDARD.md), [`GATE_INTERACTION_DIAGRAM.md`](../framework/layers/09_CHG/gates/GATE_INTERACTION_DIAGRAM.md), [`MULTI_PROJECT_FEDERATED_STANDARD.md`](../framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md), Issue #999 |

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | BRD SWF template terminates on bare element ID emission | `RatifyBusinessSpecification` | framework/layers/01_BRD/BRD-SWF-TEMPLATE.yaml:560 |
| 2 | PRD SWF template terminates abruptly after ID emission | `RatifyProductContract` | framework/layers/02_PRD/PRD-SWF-TEMPLATE.yaml:393 |
| 3 | EARS SWF template terminates without layer gate closeout | `RatifyEarsRequirements` | framework/layers/03_EARS/EARS-SWF-TEMPLATE.yaml:362 |
| 4 | BDD SWF template terminates immediately on scenario success | `CompleteScenarioSuccess` | framework/layers/04_BDD/BDD-SWF-TEMPLATE.yaml:208 |
| 5 | ADR SWF template seals decision without downstream handoff event | `RatifyDecision` | framework/layers/05_ADR/ADR-SWF-TEMPLATE.yaml:345 |
| 6 | SPEC SWF template emits success receipt without layer gate verification | `EmitSuccessReceipt` | framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml:347 |
| 7 | TDD SWF template terminates on raw test success inject | `TestRunSucceeded` | framework/layers/07_TDD/TDD-SWF-TEMPLATE.yaml:262 |
| 8 | IPLAN SWF template completes on commit without closeout verification | `Step6_CommitAndSignoff` | framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml:218 |
| 9 | EVAL SWF template writes receipt without formal SDD graph closeout | `EmitPassingReceipt` | framework/layers/10_EVAL/EVAL-SWF-TEMPLATE.yaml:272 |
| 10 | GATE-01 specifies mandatory blocking error checks between L1 and L2 | `GATE-01-E001` | framework/layers/09_CHG/gates/GATE-01_BUSINESS_PRODUCT.md:79 |
| 11 | GATE-03 specifies mandatory blocking checks for L3-L5 requirements & ADRs | `GATE-03-E001` | framework/layers/09_CHG/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md:83 |
| 12 | GATE-06 requires SPEC interfaces to synchronize with TDD test contracts | `GATE-06-E001` | framework/layers/09_CHG/gates/GATE-06_DESIGN_TEST.md:77 |
| 13 | GATE-08 enforces complete file manifests and acyclic task ordering | `GATE-08-E001` | framework/layers/09_CHG/gates/GATE-08_IPLAN.md:79 |
| 14 | GATE-CODE validates test suite passage and layer placement | `GATE-CODE-E001` | framework/layers/09_CHG/gates/GATE-CODE_IMPLEMENTATION.md:90 |
| 15 | Phase-3 closeout mandates authentic EVAL report for deployable scope | `Phase-3 closeout bifurcates on deployability.` | framework/governance/DOC_GOVERNANCE_CORE.md:287 |
| 16 | Framework formally proscribes legacy Gherkin in favor of behavioral graphs | `Behavioral State Graphs Prohibit Legacy Gherkin` | framework/governance/MULTI_PROJECT_FEDERATED_STANDARD.md:195 |
| 17 | Quality loop requires gate floor passage before downstream transition | `gate floor passed` | framework/governance/REVIEW_REMEDIATION_FLOW.md:50 |
| 18 | Circuit breaker CB-1 limits review-remediation cycles to 3 | `CB-1: Review-Fix Iteration Breaker` | framework/governance/GOVERNANCE_WORKFLOW_STANDARD.md:305 |
| 19 | SWF linter validates author playbook citation on disk | `SWF-L008` | sdd_doc_lint/swf_lint.py:470 |

---

## 1. Problem Statement & Motivation

### 1.1 The Incomplete Terminal Closeout Phase

While **CHG-111** successfully wired `author_persona`, `author_playbook`, and the multi-persona review saga invocation (`InvokeReviewSagaGate`) into all 10 layer Serverless Workflow (SWF) templates, the terminal sequence of every template remains an incomplete stub:

1. **Premature Termination without Layer Boundary Gates**:
   - In `BRD-SWF-TEMPLATE.yaml` and `PRD-SWF-TEMPLATE.yaml`, passing the review saga immediately executes a rudimentary `Ratify...` state that emits element IDs and terminates (`end: true`).
   - The formal layer boundary gates defined in `framework/layers/09_CHG/gates/` (`GATE-01` through `GATE-CODE`) are never evaluated as declarative states in the template.

2. **Abrupt Abort instead of Closed Remediation Loop**:
   - If `EvaluateReviewSagaResult` encounters blocking findings, the current templates transition directly to terminal rejection states (`RejectBusinessInitiative`, `RecordAssertionFailure`, `CompensateDistributedSaga`, `QuarantineDefect`).
   - The primary layer workflow does not model the author's remediation cycle or re-evaluation in the state machine, leaving the loop unclosed at the layer orchestrator level.

3. **Missing Baseline Sealing & SDD Graph Lineage**:
   - Documents are not sealed with an immutable frontmatter status update (`status: Approved` or `status: Baselined`), timestamp, cryptographic content hash (SHA-256), or author/approver signature.
   - The local `SddGraph` knowledge store is not updated to register the node's `Baselined` state before unlocking downstream work.

4. **Missing Downstream Handoff CloudEvents ("Starting the Next Layer")**:
   - In CNCF Serverless Workflow DSL v0.8, inter-service and inter-workflow coordination occurs via CloudEvents (`events:`, `produceEvents:`).
   - Currently, no layer template emits a formal layer completion event (e.g. `BrdClosedAndBaselinedEvent`, `PrdClosedAndBaselinedEvent`), nor do downstream layers define event triggers (`eventRef`) to consume upstream baselines. As a result, autonomous pipelines cannot chain layers together deterministically.

5. **Proscribed Gherkin Scenarios in Downstream Contracts**:
   - Earlier draft specifications referenced legacy `gherkin_scenarios` for Layer 04 (BDD) handoffs.
   - Per **CHG-96** and `MULTI_PROJECT_FEDERATED_STANDARD.md` §4, legacy conversational Gherkin is formally proscribed in favor of **declarative behavioral state graphs** and structured YAML scenarios carrying per-state `ears:` element traceability.

---

## 2. Architectural Design: The 5-Step Closed Layer Lifecycle

To guarantee that each layer is 100% audited, remediated, verified, and sealed before the subsequent layer begins, all 10 layer SWF templates will implement a standardized **5-step closed lifecycle**:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STAGE 1: AUTHORING & DECOMPOSITION                     │
│  • Primary Author Persona (playbook-guided drafting)                        │
│  • Domain validation, AST parsing, topological sorting                      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  STAGE 2: MULTI-PERSONA REVIEW & REMEDIATION                │
│  • State: InvokeReviewSagaGate (calls <layer>-review-remediation-flow)       │
│  • State: EvaluateReviewSagaResult                                          │
│      ├─ Blockers > 0 & Iteration < 3 ──► State: RemediateLayerDraft         │
│      │                                     (Author applies fixes)           │
│      │                                     └─► Re-Invoke Review Saga        │
│      ├─ Iteration >= 3 ──► EscalateToGovernance (Circuit Breaker CB-1)      │
│      └─ Review Score >= 90 & Blockers == 0 ──► (Advance to Stage 3)         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STAGE 3: LAYER BOUNDARY GATE VERIFICATION                 │
│  • State: VerifyLayerCloseoutGate                                           │
│  • Executes formal GATE-01 / GATE-03 / GATE-06 / GATE-08 / GATE-CODE checks  │
│  • Validates structural lint (sdd_doc_lint), schema conformance, and tags   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 STAGE 4: BASELINE SEALING & SDD GRAPH LINEAGE                │
│  • State: SealLayerDocumentBaseline                                         │
│      - Advances document frontmatter status to "Approved" / "Baselined"     │
│      - Generates content checksum (SHA-256) & approval metadata             │
│  • State: RegisterSddGraphBaselineNode                                      │
│      - Updates SddGraph node status to "Baselined", locking incoming edges  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               STAGE 5: DOWNSTREAM HANDOFF CLOUDEVENT EMISSION                │
│  • State: EmitLayerHandoffEvent                                             │
│  • Publishes canonical CloudEvent with ratified catalog payload              │
│  • Authorizes & triggers downstream Layer N+1 workflow start event          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Standardized Event Emission & Trigger Matrix

Every layer publishes a typed CloudEvent upon completion and declares the consumption trigger for downstream orchestration:

| Layer | Emitted CloudEvent (`produceEvents`) | Output Handoff Payload | Downstream Triggered Layer | Consuming Event Ref |
|---|---|---|---|---|
| **01_BRD** | `BrdClosedAndBaselinedEvent` | `initiativeId`, `brd_tags`, `roi_metrics` | **02_PRD** | `BrdBaselinedTriggerEvent` |
| **02_PRD** | `PrdClosedAndBaselinedEvent` | `documentId`, `features`, `@threshold:` | **03_EARS** | `PrdBaselinedTriggerEvent` |
| **03_EARS** | `EarsClosedAndBaselinedEvent` | `documentId`, `requirements_dag` | **04_BDD** & **05_ADR** *(Parallel)* | `EarsBaselinedTriggerEvent` |
| **04_BDD** | `BddScenariosClosedEvent` | `documentId`, `behavioral_state_graphs`, `scenarios_dag` | **06_SPEC** *(Join)* | `BddClosedTriggerEvent` |
| **05_ADR** | `AdrDecisionsClosedEvent` | `documentId`, `decisions`, `tech_registry` | **06_SPEC** *(Join)* | `AdrClosedTriggerEvent` |
| **06_SPEC** | `SpecContractsClosedEvent` | `documentId`, `contracts`, `api_schemas` | **07_TDD** | `SpecClosedTriggerEvent` |
| **07_TDD** | `TddSuitesClosedEvent` | `documentId`, `test_suites`, `coverage_target` | **08_IPLAN** | `TddClosedTriggerEvent` |
| **08_IPLAN** | `IplanApprovedEvent` | `iplan_id`, `file_manifest`, `tasks` | **[Code]** | `IplanApprovedTriggerEvent` |
| **09_CHG** | `ChgCloseoutEvent` | `chg_id`, `audit_trail`, `verdict` | **10_EVAL** | `ChgCloseoutTriggerEvent` |
| **10_EVAL** | `EvalVerificationClosedEvent` | `eval_id`, `receipt_path`, `verdict: PASS` | **SDD Chain** | `SddChainCompleteEvent` |

### 2.2 Parallel Fork & Join Architecture (L3 $\to$ L4/L5 $\to$ L6)

In Spec-Driven Development, Layer 03 (EARS) completion authorizes two concurrent engineering tracks that join at Layer 06 (SPEC):

1. **Parallel Fork (`ForkLayer04And05`)**:
   - `ExecuteLayer04BDD`: QA Lead converts requirements DAG into executable behavioral state graphs.
   - `ExecuteLayer05ADR`: Architect evaluates architectural trade-offs (MCDA scoring) and ratifies technology selections against enterprise tech stack policy.
2. **Synchronized Join (`ExecuteLayer06SPEC`)**:
   - Layer 06 (SPEC) requires **both** `BddScenariosClosedEvent` and `AdrDecisionsClosedEvent` before interface choreography, state machines, and API schemas can be finalized.

### 2.3 Two-Tier Remediation Architecture (Micro vs. Macro)

To maintain clean separation between automated linter fixes and fundamental design changes:

1. **Tier 1: Saga Micro-Remediation (Automated / In-Saga)**:
   - Executed internally within `<layer>-review-remediation-flow`.
   - Handles localized syntax errors, missing traceability tags, and structural linter warnings across up to 3 cycles.
2. **Tier 2: Orchestrator Macro-Remediation (Domain Re-drafting / Steering)**:
   - Executed by the layer template state machine (`RemediateLayerDraft`) when review findings demand domain model redesign or external stakeholder feedback (e.g. `AwaitSteeringCommitteeCallback` in BRD, `AwaitScopeAdjustmentCallback` in PRD, `SolicitClarificationCallback` in EARS).
   - If iteration limits are exhausted (Circuit Breaker `CB-1`), the workflow transitions to `EscalateToGovernance`.

### 2.4 Layer-to-Gate Checkpoint Mapping Table

Each layer workflow verifies its specific gate exit criteria in `VerifyLayerCloseoutGate` before document sealing:

| Layer | Exit Gate Checkpoint | Governing Specification | Mandatory Blocking Criteria |
|---|---|---|---|
| **01_BRD** | `GATE-01` (L1 Phase) | `GATE-01_BUSINESS_PRODUCT.md` | Business justification present (`GATE-01-E001`), ROI positive, sponsor identified |
| **02_PRD** | `GATE-01` (L2 Phase) | `GATE-01_BUSINESS_PRODUCT.md` | PRD features linked to `@brd:` (`GATE-01-E002`), container boundaries defined |
| **03_EARS** | `GATE-03` (L3 Phase) | `GATE-03_REQUIREMENTS_ARCHITECTURE.md` | Syntax compliant, DAG acyclic, `@prd:` trace complete (`GATE-03-E001`) |
| **04_BDD** | `GATE-03` (L4 Phase) | `GATE-03_REQUIREMENTS_ARCHITECTURE.md` | All `@ears:` mapped to behavioral graphs, zero uncompensated state failures |
| **05_ADR** | `GATE-03` (L5 Phase) | `GATE-03_REQUIREMENTS_ARCHITECTURE.md` | Technology stack policy compliant, MCDA utility matrix scored, index synchronized |
| **06_SPEC** | `GATE-06` (L6 Phase) | `GATE-06_DESIGN_TEST.md` | OpenAPI/AsyncAPI valid, choreography contracts sealed (`GATE-06-E001`) |
| **07_TDD** | `GATE-06` (L7 Phase) | `GATE-06_DESIGN_TEST.md` | Test suite 100% green, unit/integration split verified, anti-mock clean |
| **08_IPLAN** | `GATE-08` | `GATE-08_IPLAN.md` | Manifest explicit, step graph acyclic, authorizing CHG linked (`GATE-08-E001`) |
| **[Code]** | `GATE-CODE` | `GATE-CODE_IMPLEMENTATION.md` | Regression suites green, zero out-of-manifest file edits, pre-push clean |
| **10_EVAL** | `EVAL Closeout` | `DOC_GOVERNANCE_CORE.md` §3.3 | Authentic EVAL report `PASS`, 0 open P0/P1 defects |

### 2.5 Standardized FunctionRef Signatures (Decision D-0013)

To ensure portable compilation across runtime orchestrators without platform lock-in:

```yaml
# Document Baseline Sealing Operation
functionRef:
  refName: sealDocumentBaseline
  arguments:
    documentId: "${ .documentId }"
    layer: "01_BRD"
    targetStatus: "Baselined"
    checksumAlgorithm: "SHA-256"

# SDD Knowledge Graph Registration Operation
functionRef:
  refName: registerGraphBaselineNode
  arguments:
    nodeType: "BrdNode"
    nodeId: "${ .documentId }"
    status: "Baselined"
    lockIncomingEdges: true
```

### 2.6 Behavioral Layer Lifecycle Specialization (BDD & TDD)

For behavioral layers modeling executable test journeys:

- **04_BDD**: Upon scenario execution success (`CompleteScenarioSuccess`), the workflow transitions to `VerifyLayerCloseoutGate` (verifying scenario coverage and tag completeness), calls `SealLayerDocumentBaseline`, and emits `BddScenariosClosedEvent`.
- **07_TDD**: Upon test execution success (`TestRunSucceeded`), the workflow transitions to `VerifyLayerCloseoutGate` (verifying test contracts against SPEC interfaces), calls `SealLayerDocumentBaseline`, and emits `TddSuitesClosedEvent`.

---

## 3. Implementation Phases & Work Breakdown

### Phase 1: Formal Governance Records & Worktree Setup

- Author formal Change Request `CHG-112.yaml` (Decision GD-99) and `IPLAN-112.yaml`.
- Create isolated task worktree `.worktrees/aidoc-chg-112-impl` on branch `feature/chg-112-layer-closeout-cycle`.
- Open tracking GitHub issue with full blast radius and verification criteria.

### Phase 2: Layer SWF Template Upgrades (All 10 Templates)

Update all 10 templates (`01_BRD` through `10_EVAL`) to incorporate Stages 2 through 5:

1. Embed the `RemediateLayerDraft` state in the review switch to enable in-situ author remediation before escalation.
2. Add `VerifyLayerCloseoutGate` executing gate checklist criteria (`GATE-01` through `GATE-CODE`).
3. Add `SealLayerDocumentBaseline` and `RegisterSddGraphBaselineNode` operations.
4. Add `EmitLayerHandoffEvent` with CNCF CloudEvent declarations in `events:` block.

### Phase 3: Standalone Governance Workflows & Master Pipeline

1. Update all 10 workflows in `framework/governance/workflows/` in lockstep.
2. Author the Master End-to-End Orchestrator:
   - `framework/governance/workflows/sdd-layer-orchestration.sw.yaml`: Chained state machine orchestrating all 10 layers sequentially with parallel fork (L4/L5) and join (L6) using event correlation.
3. Update `framework/governance/GOVERNANCE_WORKFLOW_STANDARD.md` and all 10 `*_WORKFLOW_STANDARD.md` documents.

### Phase 4: Structural Linter Rule `SWF-L009` & Unit Testing

1. Implement rule `SWF-L009` in `sdd_doc_lint/swf_lint.py`:
   - Validates that both embedded templates and standalone layer execution workflows define:
     - Remediation loop state (`RemediateLayerDraft` or equivalent).
     - Layer gate closeout state (`VerifyLayerCloseoutGate`).
     - Document sealing state (`SealLayerDocumentBaseline`).
     - Handoff event emission (`produceEvents` / `EmitLayerHandoffEvent`).
2. Add comprehensive unit test suite in `sdd_doc_lint/tests/test_swf_lint.py`.
3. Update `framework/governance/LINT_RULES.md` and `tests/conformance/test_lint_catalog.py` (range 1 to 9).

### Phase 5: Version Fanout & State Finalization

- Bump `framework/VERSION` to `0.95.0`.
- Run `bash hooks/sync-version-refs.sh`.
- Finalize `CHG-112.yaml` and `IPLAN-112.yaml`.
- Execute full test battery (unit, conformance, linter, pre-push check).
- Open PR to `dev`, watch CI, enable auto-merge, and clean up worktree.

---

## 4. Master SDD Layer Orchestration State Machine

To provide an out-of-the-box executable orchestration of all 10 layers, `sdd-layer-orchestration.sw.yaml` declares the event-driven choreography with parallel fork/join:

```yaml
id: sdd-layer-orchestration-flow
name: SDD 10-Layer Master Orchestration Pipeline
version: "1.0.0"
specVersion: "0.8"
description: >-
  Master pipeline orchestrating the sequential execution and handoff of all
  10 SDD layers (01_BRD through 10_EVAL) using event correlation and parallel fork/join.

events:
  - name: BrdClosedAndBaselinedEvent
    type: org.aidoc.sdd.layer01.brd.closed
    source: /layers/01_brd
  - name: PrdClosedAndBaselinedEvent
    type: org.aidoc.sdd.layer02.prd.closed
    source: /layers/02_prd
  - name: EarsClosedAndBaselinedEvent
    type: org.aidoc.sdd.layer03.ears.closed
    source: /layers/03_ears
  - name: BddScenariosClosedEvent
    type: org.aidoc.sdd.layer04.bdd.closed
    source: /layers/04_bdd
  - name: AdrDecisionsClosedEvent
    type: org.aidoc.sdd.layer05.adr.closed
    source: /layers/05_adr
  - name: SpecContractsClosedEvent
    type: org.aidoc.sdd.layer06.spec.closed
    source: /layers/06_spec
  - name: TddSuitesClosedEvent
    type: org.aidoc.sdd.layer07.tdd.closed
    source: /layers/07_tdd
  - name: IplanApprovedEvent
    type: org.aidoc.sdd.layer08.iplan.approved
    source: /layers/08_iplan
  - name: ChgCloseoutEvent
    type: org.aidoc.sdd.layer09.chg.closed
    source: /layers/09_chg
  - name: EvalVerificationClosedEvent
    type: org.aidoc.sdd.layer10.eval.closed
    source: /layers/10_eval

start: ExecuteLayer01BRD

states:
  - name: ExecuteLayer01BRD
    type: callback
    action:
      name: startBrdExecutionAction
      functionRef:
        refName: triggerWorkflow
        arguments:
          workflowId: "brd-business-validation-flow"
    eventRef: BrdClosedAndBaselinedEvent
    transition: ExecuteLayer02PRD

  - name: ExecuteLayer02PRD
    type: callback
    action:
      name: startPrdExecutionAction
      functionRef:
        refName: triggerWorkflow
        arguments:
          workflowId: "prd-feature-decomposition-flow"
          upstreamBrd: "${ .eventData.initiativeId }"
    eventRef: PrdClosedAndBaselinedEvent
    transition: ExecuteLayer03EARS

  - name: ExecuteLayer03EARS
    type: callback
    action:
      name: startEarsExecutionAction
      functionRef:
        refName: triggerWorkflow
        arguments:
          workflowId: "ears-requirements-validation-flow"
          upstreamPrd: "${ .eventData.documentId }"
    eventRef: EarsClosedAndBaselinedEvent
    transition: ForkLayer04And05

  - name: ForkLayer04And05
    type: parallel
    completionType: allOf
    branches:
      - name: ExecuteLayer04BDDBranch
        actions:
          - name: startBddExecutionAction
            functionRef:
              refName: triggerWorkflow
              arguments:
                workflowId: "bdd-acceptance-run-flow"
                upstreamEars: "${ .eventData.documentId }"
      - name: ExecuteLayer05ADRBranch
        actions:
          - name: startAdrExecutionAction
            functionRef:
              refName: triggerWorkflow
              arguments:
                workflowId: "adr-decision-analysis-flow"
                upstreamEars: "${ .eventData.documentId }"
    transition: ExecuteLayer06SPEC

  # ... Sequential progression through Layer 06 SPEC, Layer 07 TDD, Layer 08 IPLAN, Code, and Layer 10 EVAL ...
```

---

## 5. Structural Linter Rule SWF-L009 Specification

### 5.1 Rule Definition

| Field | Specification |
|---|---|
| **Rule ID** | `SWF-L009` |
| **Name** | Layer Workflow Closeout & Handoff Compliance |
| **Severity** | `ERROR` |
| **Scope** | All `*-SWF-TEMPLATE.yaml` files and standalone layer workflows in `framework/governance/workflows/` (excluding `REVIEW-SWF-TEMPLATE.yaml` and `archive/`) |
| **Requirement** | Workflow must define: (1) In-situ remediation loop, (2) Gate closeout verification state, (3) Document sealing action, (4) Downstream handoff event emission. |

### 5.2 Failure Codes & Remediation

- `SWF-L009: Missing remediation loop state`: The review evaluation switch must have a path transitioning to an author remediation state before final rejection.
- `SWF-L009: Missing layer closeout gate verification state`: The template must include an operation state verifying the layer's formal boundary gate (e.g. `VerifyLayerCloseoutGate`).
- `SWF-L009: Missing document baseline sealing action`: The template must execute an action that sets `status: Approved` / `Baselined` and records verification metadata.
- `SWF-L009: Missing downstream handoff event emission`: The terminal state must declare `produceEvents` emitting the layer's completion CloudEvent.

---

## 6. Test & Verification Plan

1. **Unit Testing (`sdd_doc_lint/tests/test_swf_lint.py`)**:
   - Verify `SWF-L009` triggers on templates missing gate verification, sealing, remediation loops, or event emission.
   - Verify clean pass when all 4 closeout criteria are satisfied.
2. **Catalog Conformance (`tests/conformance/test_lint_catalog.py`)**:
   - Verify `SWF-L001` through `SWF-L009` are registered in catalog tests (`range(1, 10)`).
3. **Template Validation Battery**:
   - `python3 -m sdd_doc_lint.swf_lint framework/layers/ framework/governance/`: 0 errors.
4. **Governance Validation**:
   - `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-112/CHG-112.yaml`: 0 errors.
5. **Full Regression Suites**:
   - Conformance: 612 tests green.
   - Unit tests: 252+ tests green.
   - `bash hooks/pre_push_check.sh`: clean pass with `OPS-0065` audit-trail phrase.

---

## 7. Risk Assessment & Mitigations

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| **Template Schema Bloat** | Low readability | Medium | Keep closeout states concise; modularize detailed check actions into named functionRefs (`verifyLayerBoundaryGate`, `sealDocumentBaseline`, `emitCloudEvent`). |
| **Backward Compatibility for Consumer Workflows** | High breakage | Low | `SWF-L009` targets framework layer templates (`*-SWF-TEMPLATE.yaml`), not ad-hoc user scripts. Old templates in `archive/` are explicitly exempt. |
| **Event Engine Portability** | Lock-in | Low | CloudEvent schemas follow the standard CNCF Serverless Workflow DSL v0.8 specification, executable across LangGraph, Temporal, or purely static prompt engines. |

---

## Review log

### Pass 1: 2026-10-17 — Initial Author Review

- **Findings**:
  1. *Behavioral Layer Closeout*: BDD and TDD templates model test scenarios rather than document authoring flows; closeout requirements must fit their behavioral lifecycle.
  2. *Event Emission Standard*: Event emission syntax varies between CNCF SWF DSL versions.
- **Resolution**:
  - Codified in Section 2.1 that BDD/TDD closeout gates verify scenario coverage and seal test suites without clobbering scenario execution steps.
  - Standardized on v0.8 `produceEvents: [{ eventRef: <EventName> }]` across all states.

### Pass 2: 2026-10-17 — Independent Multi-Perspective Audit

- **Reviewers**: FrameworkArchitect, WorkflowSpecialist, QALead
- **Findings**:
  1. *Master Orchestration Correlation*: Master orchestrator pipeline needed to demonstrate how the emitted CloudEvents are consumed by downstream layers.
  2. *Circuit Breaker Safety*: Need circuit breaker guarantee for the in-situ remediation loop.
- **Resolution**:
  - Added Section 4 detailing `sdd-layer-orchestration.sw.yaml` with callback event states.
  - Explicitly bounded remediation loop to `iteration < max_iterations` (default 3 cycles / 2 remediation passes per `CB-1`).

### Pass 3: 2026-10-17 — Gap Remediation & Graph Standardization Review

- **Reviewers**: FrameworkArchitect, WorkflowSpecialist, QA Lead, Governance Auditor
- **Findings**:
  1. *Retired Gherkin Terminology*: Section 2.1 referenced legacy `gherkin_scenarios` for Layer 04 (BDD) handoffs, violating CHG-96 and `MULTI_PROJECT_FEDERATED_STANDARD.md` §4.
  2. *Parallel Fork/Join at L3/L4/L5/L6*: Section 4 master orchestrator modeled a purely linear ladder, failing to reflect that Layer 03 (EARS) forks into concurrent tracks for Layer 04 (BDD) and Layer 05 (ADR) that join at Layer 06 (SPEC).
  3. *Two-Tier Remediation Clarification*: Clarified demarcation between Tier 1 internal saga micro-remediation (automated linter fixes) and Tier 2 layer orchestrator macro-remediation (domain re-drafting).
  4. *Layer-to-Gate Checkpoint Mapping*: Added formal Section 2.4 mapping table specifying exact gate exit criteria across layers (`GATE-01` through `GATE-CODE`).
  5. *Standardized FunctionRef Signatures*: Defined explicit parameter schemas for `sealDocumentBaseline` and `registerGraphBaselineNode` per Decision D-0013.
  6. *SWF-L009 Scope Extension*: Expanded `SWF-L009` to enforce closeout compliance on both embedded templates and standalone execution workflows.
  7. *Behavioral Layer Specialization*: Detailed terminal closeout state wiring for BDD scenario runners and TDD test suites.
- **Resolution**:
  - All 7 gaps codified into Sections 1, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3, 4, and 5.
  - Replaced `gherkin_scenarios` with `behavioral_state_graphs, scenarios_dag`.
  - Added parallel fork and join states to `sdd-layer-orchestration.sw.yaml`.
  - Verified 19 load-bearing citations against repository source.
- **Result:** Ready — zero remaining findings.
