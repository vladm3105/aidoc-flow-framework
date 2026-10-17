# Plan: Wire Playbook Authoring & Review Saga Subflows into Layer SWF Templates (CHG-111, GD-98)

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Ready |
| Last Updated | 2026-10-16 |
| Author | Framework Maintainer |
| Framework Version | 0.93.0 |
| Target Framework Version | 0.94.0 (C2 Minor Spec & Tooling Release) |
| Authority | Decision GD-98 (`DEC-CHG-111`), [Decision D-0013 / GD-13](../framework/governance/DECISIONS.md), [`REVIEW_CREWS.yaml`](../framework/governance/REVIEW_CREWS.yaml), [`REVIEW_WORKFLOW_STANDARD.md`](../framework/governance/REVIEW_WORKFLOW_STANDARD.md), Issue #996 |

---

## 1. Problem Statement & Motivation

### 1.1 The Decoupled Authoring & Review Gap

In the current SDD architecture across Layers `01_BRD` through `10_EVAL`:

1. **Decoupled Workflow State Machines**:
   - Each layer provides a Process DAG template (`*-SWF-TEMPLATE.yaml`) embedding CNCF Serverless Workflow DSL v0.8 to orchestrate the creation of layer artifacts.
   - Each layer also has an independent, fully-developed Review Saga (`framework/governance/workflows/review/<layer>-review-remediation.sw.yaml`) orchestrating multi-agent review crew fan-out across persona playbooks (`framework/playbooks/<layer>/*.md`).
   - However, in `*-SWF-TEMPLATE.yaml`, the evaluation gates (e.g. `EvaluateStrategicAlignmentGate` in BRD) transition **directly** to `RatifyBusinessSpecification` without invoking the layer's review saga! The authoring flow and the multi-lens review loop exist as unlinked, isolated state machines.

2. **Unspecified Author Rubric in Workflow Definitions**:
   - While [`REVIEW_CREWS.yaml`](../framework/governance/REVIEW_CREWS.yaml) specifies the designated `author` role for each layer (e.g. `business_analyst` for BRD, `product_owner` for PRD, `requirements_specialist` for EARS, etc.), the `*-SWF-TEMPLATE.yaml` files do not declare `author_persona` or `author_playbook` in their metadata. Autonomous agents authoring an artifact have no explicit workflow binding pointing them to their authoring rubric prior to drafting.

3. **Missing Automated Workflow Verification (`SWF-L008`)**:
   - The structural workflow linter (`sdd_doc_lint.swf_lint`) enforces schema compliance (`SWF-L001` through `SWF-L007`), but lacks a rule validating that layer authoring workflows declare canonical author playbooks and invoke their designated review sagas.

---

## 2. Architectural Design: The Closed Dual-Flow Loop

To resolve this decoupling, **CHG-111** integrates the Authoring Flow with the Review Saga into a closed-loop quality lifecycle:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 LAYER AUTHORING PROCESS DAG (*-SWF-TEMPLATE.yaml)            │
│  • Bound to Author Persona & Playbook (e.g. business_analyst.md)            │
│  • Ingest Context → Decompose Streams → Construct Content Graph             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼ (At Quality Gate)
┌─────────────────────────────────────────────────────────────────────────────┐
│                 REVIEW SAGA SUBFLOW (*-review-remediation.sw.yaml)          │
│  • Parallel Fan-Out: Architect, Auditor, Chaos, Security, Specialist        │
│  • Evaluates 58 Persona Playbooks against SDD Content Graph (Kùzu / Cypher)  │
│  • Computes Weighted Score (Gate Floor >= 90) + SAGA Remediation Loop        │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 │ Gate Passed (>=90, 0 P0/P1)               │ Gate Failed (Iter Cap)
                 ▼                                           ▼
┌─────────────────────────────────┐        ┌──────────────────────────────────┐
│   Ratify Layer Specification    │        │ Steering Committee Escalation    │
│   (Unlock Downstream Handoff)   │        │ (Compensate & Rollback Alloc)    │
└─────────────────────────────────┘        └──────────────────────────────────┘
```

### 2.1 Author Playbook Binding (`*-SWF-TEMPLATE.yaml`)

Each layer's `*-SWF-TEMPLATE.yaml` metadata will declare:

```yaml
metadata:
  author_persona: "<role>"
  author_playbook: "framework/playbooks/<layer>/<role>.md"
```

Mappings per [`REVIEW_CREWS.yaml`](../framework/governance/REVIEW_CREWS.yaml):

- **01_BRD**: `business_analyst` $\to$ `framework/playbooks/01_BRD/business_analyst.md`
- **02_PRD**: `product_owner` $\to$ `framework/playbooks/02_PRD/product_owner.md`
- **03_EARS**: `requirements_specialist` $\to$ `framework/playbooks/03_EARS/requirements_specialist.md`
- **04_BDD**: `qa_lead` $\to$ `framework/playbooks/04_BDD/qa_lead.md`
- **05_ADR**: `architect` $\to$ `framework/playbooks/05_ADR/architect.md`
- **06_SPEC**: `architect` $\to$ `framework/playbooks/06_SPEC/architect.md`
- **07_TDD**: `qa_lead` $\to$ `framework/playbooks/07_TDD/qa_lead.md`
- **08_IPLAN**: `tech_lead` $\to$ `framework/playbooks/08_IPLAN/tech_lead.md`
- **09_CHG**: `integration_lead` $\to$ `framework/playbooks/09_CHG/integration_lead.md`
- **10_EVAL**: `evaluator` $\to$ `framework/playbooks/10_IPVERIFY/evaluator.md`

### 2.2 Review Saga Subflow Invocation

In each `*-SWF-TEMPLATE.yaml`, the evaluation state triggers the review saga subflow:

```yaml
    functions:
      - name: invokeReviewSaga
        operation: "urn:aidoc:workflows:review-saga#invoke"
        type: custom

    states:
      - name: InvokeReviewSagaGate
        type: operation
        actions:
          - name: runLayerReviewSagaAction
            functionRef:
              refName: invokeReviewSaga
              arguments:
                workflowId: "<layer>-review-remediation-flow"
                artifactId: "${ .artifactId }"
        transition: EvaluateReviewSagaResult

      - name: EvaluateReviewSagaResult
        type: switch
        dataConditions:
          - name: ReviewGateApproved
            condition: "${ .reviewScore >= 90 and .blockingFindings == 0 }"
            transition: RatifySpecification
          - name: ReviewRequiresSteering
            condition: "${ .requiresEscalation == true }"
            transition: AwaitSteeringCommitteeCallback
        defaultCondition:
          transition: RejectInitiative
```

### 2.3 Structural Linter Rule `SWF-L008`

Add rule `SWF-L008` to `sdd_doc_lint.swf_lint`:

- Asserts that all layer workflow templates (`*-SWF-TEMPLATE.yaml`) carry valid `author_persona` and `author_playbook` metadata pointing to existing files.
- Asserts that the template contains an invocation state targeting `<layer>-review-remediation-flow`.

---

## 3. Implementation Phasing

### Phase 1: Governance Artifacts (CHG-111 & IPLAN-111)

- Author `framework/archive/CHG-111/CHG-111.yaml` and `IPLAN-111.yaml`.
- Validate via `python3 sdd_doc_lint/chg_lint.py`.

### Phase 2: Layer SWF Templates & Standards Harmonization

- Update all 10 `*-SWF-TEMPLATE.yaml` files with author playbook metadata and review saga subflow invocations.
- Update all 10 layer workflow standards (`framework/layers/<NN>_<LAYER>/<LAYER>_WORKFLOW_STANDARD.md`) documenting the closed dual-flow loop.

### Phase 3: Linter Extension (`SWF-L008`) & Test Coverage

- Implement `SWF-L008` in `sdd_doc_lint/swf_lint.py`.
- Add test coverage in `tests/unit/test_swf_lint.py` asserting `SWF-L008` catches missing review saga bindings and valid templates pass.

### Phase 4: CI Verification & Promotion

- Run full test suites (`python3 -m unittest discover tests/unit`, conformance, pre-push checks).
- Open PR `feature/chg-111-layer-swf-playbook-integration` $\to$ `dev`.
- Verify CI passes and merge to `dev`.

---

## 4. Invariants & Guardrails

1. **Engine Neutrality (Decision D-0013)**: Declarative specifications remain runtime-pure; subflow references use canonical CNCF Serverless Workflow v0.8 schemas.
2. **Canonical 10-Layer Registry Preservation**: The 10 layers in `LAYER_REGISTRY.yaml` remain immutable.
3. **Zero Breaking Changes to Standalone Review Sagas**: Existing review workflows in `framework/governance/workflows/review/` remain backwards-compatible and unchanged in their core logic.

---

## 5. Out of Scope

- Automated compilation of markdown playbooks into executable Cypher queries (deferred to future feature release).
- Modifying scoring weight allocations in `REVIEW_CREWS.yaml`.

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Crews mapping declares layer author personas and review crew allocations | `crews:` | framework/governance/REVIEW_CREWS.yaml:55 |
| 2 | Layer 01 BRD authoring workflow template declares CNCF state machine | `IngestStrategicInitiative` | framework/layers/01_BRD/BRD-SWF-TEMPLATE.yaml:452 |
| 3 | Layer 01 BRD review remediation workflow fans out multi-agent crew | `DispatchReviewCrew` | framework/governance/workflows/review/brd-review-remediation.sw.yaml:46 |
| 4 | Layer 01 business analyst playbook serves as primary author lens | `business_analyst` | framework/playbooks/01_BRD/business_analyst.md:3 |
| 5 | Structural workflow linter implements CNCF DSL verification rules | `lint_file` | sdd_doc_lint/swf_lint.py:405 |
| 6 | Conformance registry enforces exactly ten canonical SDD layers | `test_exactly_ten_layers` | tests/conformance/test_registry.py:32 |

---

## Review log

### Pass 1: 2026-10-16 — Framework Architect & Workflow Specialist

- **Findings**:
  1. *Subflow Semantics*: CNCF Serverless Workflow v0.8 supports both `subFlowRef` and custom function operations (`type: custom`). We must ensure `swf_lint.py` validates the subflow reference without rejecting custom function wrappers used by specific orchestration engines.
  2. *Layer 10 Specialization*: Layer 10 (EVAL) is not crew-scored via `REVIEW_CREWS.yaml` but verdict-graded via `10_IPVERIFY` playbooks (`eval-verification-flow.sw.yaml`). Its authoring template must point to `evaluator.md` rather than a generic reviewer.
- **Resolution**:
  - Clarified in Section 2.2 that `invokeReviewSaga` can be represented as an operation or `subFlowRef`, validated by `SWF-L008`.
  - Bound Layer 10 explicitly to `evaluator` and `framework/playbooks/10_IPVERIFY/evaluator.md` in Section 2.1.

### Pass 2: 2026-10-16 — Independent QA Lead & Governance Auditor

- **Findings**:
  1. *Author Playbook Path Validation*: `SWF-L008` must verify that the cited `author_playbook` file actually exists on disk, preventing broken links or typos during authoring.
  2. *Backwards Compatibility of Declarative Templates*: Standard declarative companion templates (`*-TEMPLATE.yaml`) must remain purely declarative and unaffected by SWF subflow requirements.
- **Resolution**:
  - Specified file-existence validation for `author_playbook` in `SWF-L008` (Section 2.3).
  - Explicitly scoped changes to `*-SWF-TEMPLATE.yaml` (Workflow Subtypes), leaving static companion templates untouched.
- **Result:** Ready — zero remaining findings.
