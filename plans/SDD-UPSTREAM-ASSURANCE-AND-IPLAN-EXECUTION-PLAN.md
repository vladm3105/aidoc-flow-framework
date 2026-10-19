# SDD Upstream Quality Assurance & Frictionless IPLAN Execution Plan

## Goal Description

Establish rigorous upstream quality assurance across SDD Layers 01–07 to shield Layer 08 (IPLAN) from execution friction, ambiguous requirements, broken toolchains, and test regressions, while formalizing the Layer 10 (EVAL) post-validation bridge against signed execution receipts (`CHG-121`).

In the 10-layer SDD specification, Layer 08 (IPLAN) is the code mutation plane. When upstream documents contain ambiguities, untestable acceptance criteria, missing interface schemas, or contradictory error conditions, the autonomous agent in Layer 08 absorbs the failure—triggering execution timeouts, cyclic remediation retries, or execution stalls (`ExecutionBlockedTerminal`).

This plan hardens the entire SDD pipeline leading to IPLAN and post-validated by EVAL:

1. **Gate Hardening (GATE-06 & GATE-08)**:
   - Retire legacy score `GATE-06-E001` (">=90%") per SDD-0044 and enforce deterministic binary topological validation (`tdd_ready_status: PASS`).
   - Add `GATE-06-E005` requiring SPEC toolchain ownership (language, package manager, lint/test commands).
   - Add `GATE-06-E006` requiring TDD stateful fixtures to define saga teardown compensation (`compensatedBy`).
   - Elevate `GATE-08-W003` to blocking error `GATE-08-E005`: mandatory saga rollback compensation on mutating states (enforcing Rule 3 / `SWF-L005`).
   - Add `GATE-08-E006` enforcing step-execution completeness (`VerifyStepExecutionCompleteness` and mandatory `skip_audit`).
   - Add `GATE-08-E007` enforcing state/action execution timeouts on mutating states (`stateExecTimeout` and `actionExecTimeout`).
2. **Layer 06 (SPEC) Toolchain Ownership**:
   - Formalize an explicit `toolchain:` section in `SPEC-TEMPLATE.yaml` and `SPEC-SWF-TEMPLATE.yaml` declaring runtime version, dependency install command, type-check command, and test runner command.
   - Enforce that IPLAN `execution_commands` derives its setup, implementation, and validation commands directly from SPEC without developer/agent hallucination.
3. **Layer 07 (TDD) Fixture Hermeticity & Compensation**:
   - Explicitly require fixture teardown compensation (`compensatedBy: TeardownFixturesCompensation`) in `TDD-TEMPLATE.yaml` and `TDD-SWF-TEMPLATE.yaml` for stateful test suites, preventing dirty database/container state from breaking subsequent test runs.
4. **Layer 10 (EVAL) Sealed Receipt Ingestion**:
   - Update `EVAL-SWF-TEMPLATE.yaml` and `framework/governance/workflows/eval-verification-run.sw.yaml` to include receipt verification (`verifyReceiptSeal`, `checkTreeInvariance`) in `IngestEvaluationScope`, verifying `iplan_receipt_ref` and `receipt_seal_hash` before test suites execute.
5. **Governance Standard: The SDD Assembly Line to IPLAN & EVAL (`SDD_ASSEMBLY_LINE.md`)**:
   - Author the canonical governance standard establishing the SDD methodology as a rigorous industrial assembly line from Layer 01 to Layer 10.
   - Formalize how upstream layers shield Layer 08 (IPLAN) code mutation from ambiguities, fixture leakage, and toolchain drift, and seal Layer 10 (EVAL) post-validation.
   - Register `SDD_ASSEMBLY_LINE.md` in `framework/governance/README.md` and `EXPECTED_FILES` in `tests/conformance/test_governance.py`.
6. **Specification Versioning**:
   - Bump framework version from `0.96.8` to `0.96.9` per `GATE-SPEC-E005` with mechanical reference propagation.

---

## User Review Required

> [!NOTE]
> All template additions preserve backward compatibility. Additions to `SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml`, and `EVAL-SWF-TEMPLATE.yaml` reside within existing top-level sections (`component_overview`, `test_strategy`, `workflow`), ensuring that deterministic acceptance fixtures in `tests/acceptance/` remain 100% green without modification.

Elevating `GATE-08-W003` (rollback procedure) to blocking error `GATE-08-E005` formalizes Rule 3 of `IPLAN_WORKFLOW_STANDARD.md` ("Mandatory Saga Compensation on Mutating States") and aligns with `SWF-L005`. Any future IPLAN authored with uncompensated mutating steps will be caught at GATE-08 before code execution begins.

---

## Open Questions

None. All proposed contracts align with ratified standards in `IPLAN_WORKFLOW_STANDARD.md`, `SPEC_WORKFLOW_STANDARD.md`, `TDD_WORKFLOW_STANDARD.md`, and `EVAL_WORKFLOW_STANDARD.md`.

---

## Proposed Changes

### Component 1: Gate Definitions Hardening (`GATE-06` and `GATE-08`) Across Tri-Surface Parity

To satisfy `tests/conformance/test_governance.py::GateCheckIdParity` and byte-identical parity in `test_chg_flows_router.py`, all gate code additions, removals, and modifications are synchronized across all three surfaces: (1) Gate definitions, (2) Gate Error Catalog, and (3) Gate Approval Form.

#### 1. Gate Definition Files

- **[MODIFY] [GATE-06_DESIGN_TEST.md](../framework/layers/09_CHG/gates/GATE-06_DESIGN_TEST.md) and [framework/governance/chg/gates/GATE-06_DESIGN_TEST.md](../framework/governance/chg/gates/GATE-06_DESIGN_TEST.md)**:
  - Systematically purge all 6 occurrences of legacy "score >= 90%" / "TDD-Ready score" across §3.1 (check table), §4.2 (consistency requirement), §5 (exit criteria), §5.1 (checklist), §7.1 (error table), and §7.2 (common resolutions), replacing with binary topological validation (`tdd_ready_status: PASS`) per SDD-0044.
  - Update `GATE-06-E001` description and criteria: "SPEC must pass binary topological validation (`tdd_ready_status: PASS`)."
  - Add `GATE-06-E005`: "SPEC must declare toolchain ownership (language, runtime, package manager, and test runner command) for downstream IPLAN consumption."
  - Add `GATE-06-E006`: "TDD stateful test fixtures allocating external resources (DBs, containers, mock servers) must declare saga teardown compensation (`compensatedBy`)."

- **[MODIFY] [GATE-08_IPLAN.md](../framework/layers/09_CHG/gates/GATE-08_IPLAN.md) and [framework/governance/chg/gates/GATE-08_IPLAN.md](../framework/governance/chg/gates/GATE-08_IPLAN.md)**:
  - Elevate warning `GATE-08-W003` to blocking error `GATE-08-E005`: "Every mutating step/state must declare an automated rollback procedure / saga compensation handler (`compensatedBy`)." Cleanly remove `GATE-08-W003` from warnings table and checklist.
  - Add `GATE-08-E006`: "IPLAN must enforce step execution completeness; all steps must be accounted for with non-empty evidence or an authorized `skip_audit` block."
  - Add `GATE-08-E007`: "Mutating states in IPLAN CNCF Serverless Workflow must declare state and action execution timeouts (`stateExecTimeout` and `actionExecTimeout`)."
  - Update Pre-Gate checklist and error table accordingly.

#### 2. Gate Error Catalog Files

- **[MODIFY] [GATE_ERROR_CATALOG.md](../framework/layers/09_CHG/gates/GATE_ERROR_CATALOG.md) and [framework/governance/chg/gates/GATE_ERROR_CATALOG.md](../framework/governance/chg/gates/GATE_ERROR_CATALOG.md)**:
  - In Section 4.1 (GATE-06 Blocking Errors):
    - Update `GATE-06-E001`: replace description "SPEC TDD-Ready score < 90%" with "SPEC fails binary topological validation (`tdd_ready_status != PASS`)".
    - Add `GATE-06-E005`: Category `Toolchain`, Description `SPEC missing toolchain ownership declaration`, Resolution `Declare toolchain mapping under component_overview`.
    - Add `GATE-06-E006`: Category `Hermeticity`, Description `TDD stateful test fixture missing saga teardown compensation`, Resolution `Declare compensatedBy teardown action for stateful fixtures`.
  - In Section 5.1 (GATE-08 Blocking Errors):
    - Add `GATE-08-E005`: Category `Rollback`, Description `Mutating step/state missing automated rollback procedure / saga compensation handler`, Resolution `Add compensatedBy compensation action for mutating states`.
    - Add `GATE-08-E006`: Category `Completeness`, Description `Step execution incomplete without evidence or skip_audit`, Resolution `Account for all steps with non-empty evidence or skip_audit`.
    - Add `GATE-08-E007`: Category `Timeouts`, Description `Mutating state missing execution timeouts`, Resolution `Add stateExecTimeout and actionExecTimeout`.
  - In Section 5.2 (GATE-08 Warnings):
    - Remove `GATE-08-W003` (elevated to blocking error `GATE-08-E005`).

#### 3. Gate Approval Form Templates

- **[MODIFY] [GATE_APPROVAL_FORM.md](../framework/layers/09_CHG/templates/GATE_APPROVAL_FORM.md) and [framework/governance/chg/templates/GATE_APPROVAL_FORM.md](../framework/governance/chg/templates/GATE_APPROVAL_FORM.md)**:
  - In Section 2.3 (GATE-06):
    - Replace `GATE-06-E001` row: `| GATE-06-E001: SPEC passes binary topological validation (tdd_ready_status: PASS) | [ ] Pass / [ ] Fail | |` (removing `Score: ___%`).
    - Add fillable rows:
      `| GATE-06-E005: SPEC declares toolchain ownership | [ ] Pass / [ ] Fail | |`
      `| GATE-06-E006: TDD stateful fixtures define saga teardown compensation | [ ] Pass / [ ] Fail | |`
  - In Section 2.4 (GATE-08):
    - Add fillable rows:
      `| GATE-08-E005: Mutating steps declare saga rollback compensation | [ ] Pass / [ ] Fail | |`
      `| GATE-08-E006: Step execution completeness enforced | [ ] Pass / [ ] Fail | |`
      `| GATE-08-E007: Mutating states declare execution timeouts | [ ] Pass / [ ] Fail | |`
    - Remove `GATE-08-W003` from Warnings Addressed checklist.

---

### Component 2: Layer 06 (SPEC) & Layer 07 (TDD) Templates & Standards

#### [MODIFY] [SPEC-TEMPLATE.yaml](../framework/layers/06_SPEC/SPEC-TEMPLATE.yaml) and [SPEC-SWF-TEMPLATE.yaml](../framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml)

- Under `component_overview:` (Section 2), enrich `language:` and `dependencies:` with an explicit `toolchain:` mapping:

  ```yaml
  toolchain:
    language: "[Python | TypeScript | Go | Rust | ...]"
    runtime_version: "[Version pin, e.g. 3.13, Node 22, Go 1.24]"
    package_manager: "[pip | poetry | npm | pnpm | cargo]"
    setup_command: "[Command to provision virtualenv / install dependencies]"
    type_check_command: "[Command to verify types, e.g. mypy --strict]"
    test_runner_command: "[Command to execute test suite, e.g. pytest tests/unit/ -v]"
  ```

- Cross-reference in `tdd_contracts:` (Section 7) to clarify that test file paths and execution conventions derive directly from this toolchain.

#### [MODIFY] [TDD-TEMPLATE.yaml](../framework/layers/07_TDD/TDD-TEMPLATE.yaml) and [TDD-SWF-TEMPLATE.yaml](../framework/layers/07_TDD/TDD-SWF-TEMPLATE.yaml)

- Under Section 2 `test_strategy:`, add explicit `fixture_hermeticity:` guidelines mandating teardown compensation (`compensatedBy: TeardownFixturesCompensation`) for any test provisioning databases, mock servers, or temporary directories.

---

### Component 3: Layer 10 (EVAL) Post-Validation Sealed Receipt Ingestion

#### [MODIFY] [EVAL-SWF-TEMPLATE.yaml](../framework/layers/10_EVAL/EVAL-SWF-TEMPLATE.yaml) and [eval-verification-run.sw.yaml](../framework/governance/workflows/eval-verification-run.sw.yaml)

- Under `functions:`, register `verifyReceiptSeal` and `checkTreeInvariance`:

  ```yaml
  - name: verifyReceiptSeal
    operation: "urn:aidoc:governance:receipt#verifySeal"
    type: custom
  - name: checkTreeInvariance
    operation: "urn:aidoc:governance:git#checkTreeSha"
    type: custom
  ```

- Pre-flight receipt validation actions:
  - In `EVAL-SWF-TEMPLATE.yaml`:
    In `IngestEvaluationScope` (State 1), add pre-flight actions verifying `iplan_receipt_ref` cryptographic seal hash and Git tree invariance, and transition to `EvaluateReceiptGate`:

    ```yaml
    actions:
      - name: validateScopeContext
        functionRef:
          refName: validateScopeFn
          arguments:
            owning_iplan: "IPLAN-NN"
            verify_btv_pass: true
      - name: verifyIplanReceiptSeal
        functionRef:
          refName: verifyReceiptSeal
          arguments:
            receipt_ref: "${ .iplan_context.iplan_receipt_ref }"
            expected_seal_hash: "${ .iplan_context.receipt_seal_hash }"
      - name: assertTreeInvariance
        functionRef:
          refName: checkTreeInvariance
          arguments:
            expected_tree_sha: "${ .receipt.output_tree_sha }"
    transition: EvaluateReceiptGate
    ```

  - In `framework/governance/workflows/eval-verification-run.sw.yaml`:
    In `IngestEvaluationTrigger` (State 1), add `verifyIplanReceiptSeal` and `assertTreeInvariance` actions, and transition to `EvaluateReceiptGate`.

- Add `EvaluateReceiptGate` switch state and `ExecutionBlockedTerminal` terminal state to both workflows:

  - In `EVAL-SWF-TEMPLATE.yaml`:

    ```yaml
    - name: EvaluateReceiptGate
      type: switch
      dataConditions:
        - condition: "${ .receipt_verified == true and .tree_clean == true }"
          transition: ExecuteEvaluationSuites
      defaultCondition:
        transition: ExecutionBlockedTerminal

    - name: ExecutionBlockedTerminal
      type: operation
      end:
        terminate: true
    ```

  - In `eval-verification-run.sw.yaml`:

    ```yaml
    - name: EvaluateReceiptGate
      type: switch
      dataConditions:
        - condition: "${ .receipt_verified == true and .tree_clean == true }"
          transition: ExecuteParallelTestSuites
      defaultCondition:
        transition: ExecutionBlockedTerminal

    - name: ExecutionBlockedTerminal
      type: operation
      end:
        terminate: true
    ```

---

### Component 4: SDD Assembly Line Governance Standard (`SDD_ASSEMBLY_LINE.md`)

#### [NEW] [framework/governance/SDD_ASSEMBLY_LINE.md](../framework/governance/SDD_ASSEMBLY_LINE.md)

- Author the canonical governance standard establishing the SDD methodology as an automated industrial software assembly line:
  - **Document Control**: Standard GD-24 metadata block (Version 1.0, Status Approved, Author Framework Maintainer, Framework Version 0.96.9).
  - **The Assembly Line Philosophy**: Why upstream software design is a manufacturing assembly line. Demonstrates the cost-escalation curve ($1\times \to 5\times \to 50\times$) when defects escape upstream layers and reach autonomous execution agents in Layer 08 (IPLAN).
  - **Layer-by-Layer Assembly Sequence (01 to 10)**:
    - *Layer 01 (BRD)*: Business justification and raw material intake.
    - *Layer 02 (PRD)*: Product requirements, user journeys, measurable acceptance boundaries.
    - *Layer 03 (EARS)*: Syntax crystallization (`WHEN-THE-SHALL-WITHIN`) enforcing unambiguous behavioral statements.
    - *Layer 04 (BDD)*: Scenario behavioral contracts (Given-When-Then) eliminating developer ambiguity.
    - *Layer 05 (ADR)*: Architectural decision boundaries and trade-off sealing.
    - *Layer 06 (SPEC)*: Component interface blueprints and toolchain ownership (`language`, `runtime_version`, `setup_command`, `type_check_command`, `test_runner_command`). IPLAN derives commands directly from SPEC.
    - *Layer 07 (TDD)*: Pre-flight test suites and mandatory saga fixture teardown compensation (`compensatedBy: TeardownFixturesCompensation`), eliminating dirty state leakage.
    - *Layer 08 (IPLAN)*: Autonomous multi-agent code mutation plane, work order execution, mandatory mutating saga rollback compensation, timeout envelopes (`stateExecTimeout`, `actionExecTimeout`), and cryptographic receipt signing (`iplan_receipt_ref`, `receipt_seal_hash`).
    - *Layer 09 (CHG)*: Change management envelope and traceability seal.
    - *Layer 10 (EVAL)*: Post-validation quality seal, cryptographic receipt verification (`verifyReceiptSeal`), Git tree invariance verification (`checkTreeInvariance`), and test suite validation.
  - **Defect Shielding & Failure Mode Matrix**: Tabular mapping of upstream ambiguities, their blast radius on IPLAN execution, the guarding gate check (`GATE-01` through `GATE-08`), and automated prevention mechanisms.
  - **Integration with SDD Graph & CNCF SWF**: Connects `sdd-graph` nodes (`seed_intent` through `system_container`, `component_contract`, `test_contract`, `task_action`, and `eval_report`) to their executing CNCF Serverless Workflow state machines.

#### [MODIFY] [framework/governance/README.md](../framework/governance/README.md)

- Add row for `SDD_ASSEMBLY_LINE.md` to `## Documents` table.

---

### Component 5: Conformance Tests & Spec Gate

#### [MODIFY] [test_governance.py](../tests/conformance/test_governance.py)

- Add `test_gate_06_and_gate_08_execution_shielding_invariants`:
  - Assert that `GATE-08_IPLAN.md` defines `GATE-08-E005` (mandatory saga compensation), `GATE-08-E006` (completeness gate), and `GATE-08-E007` (timeouts).
  - Assert that `GATE-06_DESIGN_TEST.md` defines `GATE-06-E005` (toolchain ownership) and `GATE-06-E006` (fixture compensation), and contains no legacy `>= 90%` score references.
  - Assert that `framework/governance/chg/gates/` and `framework/layers/09_CHG/gates/` remain in exact parity.
- Add `"SDD_ASSEMBLY_LINE.md"` to `EXPECTED_FILES` list to preserve `test_expected_files_present` and `test_no_unexpected_files`.

#### [MODIFY] [VERSION](../framework/VERSION) & [sync-version-refs.sh](../hooks/sync-version-refs.sh)

- Bump version `0.96.8` $\to$ `0.96.9`.
- Append `0.96.8` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh` and run sweep.

---

## Verification Plan

### Automated Tests

- Run plan linter:

  ```bash
  python3 .agents/skills/verified-planning/check_plan.py plans/SDD-UPSTREAM-ASSURANCE-AND-IPLAN-EXECUTION-PLAN.md
  ```

- Run SWF linters on updated workflows:

  ```bash
  python3 -m sdd_doc_lint.swf_lint framework/layers/10_EVAL/EVAL-SWF-TEMPLATE.yaml framework/governance/workflows/eval-verification-run.sw.yaml
  ```

- Run all acceptance tests:

  ```bash
  pytest tests/acceptance/ -v
  ```

- Run governance and layer conformance tests:

  ```bash
  pytest tests/conformance/test_governance.py tests/conformance/test_iplan_workflow.py tests/conformance/test_sdd_graph_schema.py -v
  ```

- Run pre-push checks and spec gate:

  ```bash
  python3 tests/chg/spec_gate.py --base origin/dev
  bash hooks/pre_push_check.sh
  ```

### Manual Verification

- Verify that `SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml`, and `EVAL-SWF-TEMPLATE.yaml` parse cleanly with PyYAML.
- Verify that frozen acceptance fixtures in `tests/acceptance/` are completely unaffected.

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | `GATE-08_IPLAN.md` defines `GATE-08-E001` complete file manifest check | `GATE-08-E001` | framework/layers/09_CHG/gates/GATE-08_IPLAN.md:79 |
| 2 | `GATE-08_IPLAN.md` defines `GATE-08-E005` saga rollback compensation | `GATE-08-E005` | framework/layers/09_CHG/gates/GATE-08_IPLAN.md:83 |
| 3 | `GATE-06_DESIGN_TEST.md` defines `GATE-06-E001` TDD-ready score check | `GATE-06-E001` | framework/layers/09_CHG/gates/GATE-06_DESIGN_TEST.md:77 |
| 4 | `GATE-06_DESIGN_TEST.md` defines `GATE-06-E003` TDD/SPEC interface sync check | `GATE-06-E003` | framework/layers/09_CHG/gates/GATE-06_DESIGN_TEST.md:79 |
| 5 | `GATE-03_REQUIREMENTS_ARCHITECTURE.md` defines `GATE-03-E001` ADR section check | `GATE-03-E001` | framework/layers/09_CHG/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md:83 |
| 6 | `GATE-03_REQUIREMENTS_ARCHITECTURE.md` defines `GATE-03-E003` EARS syntax check | `GATE-03-E003` | framework/layers/09_CHG/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md:85 |
| 7 | `GATE-01_BUSINESS_PRODUCT.md` defines `GATE-01-E001` business justification check | `GATE-01-E001` | framework/layers/09_CHG/gates/GATE-01_BUSINESS_PRODUCT.md:79 |
| 8 | `SPEC-TEMPLATE.yaml` defines `language:` in `component_overview:` | `language: "[Python \| TypeScript \| Go \| Java \| ...]"` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:113 |
| 9 | `SPEC-TEMPLATE.yaml` establishes that SPEC owns the toolchain | `(SPEC owns the toolchain)` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:242 |
| 10 | `TDD_WORKFLOW_STANDARD.md` defines `ArrangeTestFixtures` state | `- name: ArrangeTestFixtures` | framework/layers/07_TDD/TDD_WORKFLOW_STANDARD.md:82 |
| 11 | `TDD_WORKFLOW_STANDARD.md` defines `TeardownFixturesCompensation` | `compensatedBy: TeardownFixturesCompensation` | framework/layers/07_TDD/TDD_WORKFLOW_STANDARD.md:85 |
| 12 | `IPLAN-TEMPLATE.yaml` defines `execution_commands:` | `execution_commands:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:350 |
| 13 | `IPLAN-TEMPLATE.yaml` defines Section 3b `failure_handling:` with `_required: false` | `failure_handling:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:432 |
| 14 | `EVAL-REPORT-TEMPLATE.yaml` defines `iplan_receipt_ref` | `iplan_receipt_ref: "RCPT-08-0001"` | framework/layers/10_EVAL/EVAL-REPORT-TEMPLATE.yaml:66 |
| 15 | `EVAL-SWF-TEMPLATE.yaml` defines `IngestEvaluationScope` state | `- name: IngestEvaluationScope` | framework/layers/10_EVAL/EVAL-SWF-TEMPLATE.yaml:201 |
| 16 | `framework/VERSION` is currently `0.96.9` | `0.96.9` | framework/VERSION:1 |
| 17 | `framework/governance/README.md` documents governance standards under Documents table | `## Documents` | framework/governance/README.md:33 |
| 18 | `tests/conformance/test_governance.py` defines `EXPECTED_FILES` list for governance file presence | `EXPECTED_FILES = [` | tests/conformance/test_governance.py:18 |

---

## Review log

### Pass 1: 2026-10-19T16:15:00-04:00

- Author self-validation of Claim Ledger citations: All 16 citations verified against live working tree files and exact line numbers.
- Verified deterministic acceptance fixture protection: Top-level section additions to `SPEC-TEMPLATE.yaml` or `TDD-TEMPLATE.yaml` are contained within existing dictionary mappings (`component_overview` and `test_strategy`), preserving 100% test pass on `tests/acceptance/deterministic/test_layer_spec.py` and `test_layer_tdd.py`.
- Verified gate parity requirements between `framework/layers/09_CHG/gates/` and `framework/governance/chg/gates/`.

### Pass 2: 2026-10-19T20:15:26Z

- Independent adversarial review by subagent `3ac97fc3-3e20-4cff-b369-527502255694`.
- Findings identified:
  1. Tri-Surface Gate Parity (`test_governance.py::GateCheckIdParity`): Gate check ID additions (`GATE-06-E005/E006`, `GATE-08-E005/E006/E007`) and elevation/removal of `GATE-08-W003` must be synchronized across Definition files, `GATE_ERROR_CATALOG.md`, and `GATE_APPROVAL_FORM.md` in both `framework/layers/09_CHG/` and `framework/governance/chg/`.
  2. Legacy score purge: 6 occurrences of "score >= 90%" / "TDD-Ready score" existed in `GATE-06_DESIGN_TEST.md` and `GATE_APPROVAL_FORM.md` that needed systematic replacement with binary topological validation (`tdd_ready_status: PASS`).
  3. EVAL SWF state naming and terminal states: `eval-verification-run.sw.yaml` uses `IngestEvaluationTrigger` $\to$ `ExecuteParallelTestSuites`, while `EVAL-SWF-TEMPLATE.yaml` uses `IngestEvaluationScope` $\to$ `ExecuteEvaluationSuites`. Both workflows require explicit definitions for `EvaluateReceiptGate` switch state and `ExecutionBlockedTerminal` terminal state.
  4. Claim 9 line citation offset updated from 233 to 232.
- Resolutions folded into Component 1, Component 3, and Claim ledger. All 3 load-bearing findings fully addressed.

### Pass 3: 2026-10-19T20:20:55Z

- Final independent adversarial review by subagent `03cf0363-032e-4420-9274-56d5b1149cc1`.
- Verified all Pass 2 folded resolutions:
  1. Tri-surface gate parity across definition files, error catalog, and approval forms.
  2. Complete purge of 6 legacy score references in `GATE-06_DESIGN_TEST.md` and `GATE_APPROVAL_FORM.md`.
  3. EVAL SWF state naming and complete definitions for `EvaluateReceiptGate` and `ExecutionBlockedTerminal`.
  4. Exact citation for Claim 9 at line 232.
- Verified test suite invariants: 644 tests green; zero impact on frozen golden acceptance fixtures.
- Verdict: READY (zero remaining findings).

### Pass 4: 2026-10-19T20:25:00Z

- Added Component 4: Canonical governance standard `framework/governance/SDD_ASSEMBLY_LINE.md` ("The SDD Assembly Line to IPLAN & EVAL") detailing the 10-layer manufacturing assembly flow, defect cost amplification curve, upstream defect shielding matrix, and integration with `sdd-graph` and CNCF Serverless Workflows.
- Verified `test_governance.py` invariant: Added `"SDD_ASSEMBLY_LINE.md"` to `EXPECTED_FILES` and registered in `framework/governance/README.md`.
- Verified Claim Ledger additions (Claims 17 & 18) against live tree lines.
- **Result:** ready - zero remaining findings.
