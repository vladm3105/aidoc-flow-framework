# IPLAN Distributed Multi-Agent Execution, Cryptographic Attribution & Step Evidence Plan

## Goal Description

Bridge Layer 08 (IPLAN) of `aidoc-flow-framework` natively to the `iplanic` distributed execution architecture (`aidoc-flow-iplanic` and `aidoc-flow-iplan-standard`). In distributed multi-agent execution environments where distinct workers (subagents or remote runners like `iplan-runner`) execute partitioned work orders of an implementation plan, self-reported completion (`status: Completed`) is vulnerable to phantom execution, cross-worker state drift, lack of attribution, hung/looping runners, and accidental step skipping.

This enhancement introduces:

1. **Dual-Identity Agent Attribution**: Distinguishing human-readable agent personas (`protocol_agent_id`, e.g. `agent:tech_lead`) from cryptographic signing identities (`executor_id`, e.g. `exec:m7k3...` bound to an Ed25519 public key).
2. **Step-Level Digital Signatures**: Embedding an `attestation` envelope inside steps (`IPLAN-TEMPLATE.yaml`) and graph action nodes (`IPLAN-GRAPH-TEMPLATE.yaml`) carrying an Ed25519 or HMAC-SHA256 signature over execution facts (command exit code, stdout digest, and output Git tree SHA), with schema-valid `_UNSIGNED` fallback for local developers.
3. **Pre-Flight Handover Verification**: Defining downstream worker pre-flight assertion contracts in `IPLAN_WORKFLOW_STANDARD.md` and `IPLAN-SWF-TEMPLATE.yaml`, where downstream workers assert upstream digital signatures and Git tree hashes before executing subsequent tasks, transitioning immediately to `ExecutionBlockedTerminal` on state drift.
4. **Step-Execution Completeness Gate & Skip Auditing**: Enforcing a strict step-coverage invariant where every step in `plan.steps` must be accounted for (`Completed` with non-empty evidence or explicitly `Skipped` with a mandatory `skip_audit` block), eliminating silent step omission and false progression.
5. **Execution Timeouts & Loop Protection**: Integrating native CNCF Serverless Workflow state and action timeouts (`stateExecTimeout: "PT15M"`, `actionExecTimeout: "PT5M"`) into mutating states, aligning with framework adaptation knobs (`exec_wall_clock_budget_s`, `exec_test_timeout_s`) to prevent runaway worker loops and hung subprocesses.
6. **Dual-Anchor Evidence TTL**: Binding step attestations and detached receipts to both temporal freshness (`valid_until` / TTL) and state invariants (`output_tree_sha`), rejecting stale, expired, or replayed execution proofs.
7. **Layer 10 (EVAL) Post-Validation Integration**: Formatting Layer 08 execution evidence receipts for native consumption by Layer 10 (EVAL) post-validation suites (`EVAL-SWF-TEMPLATE.yaml` and `EVAL-REPORT-TEMPLATE.yaml`), embedding `iplan_receipt_ref` and `receipt_seal_hash` in `iplan_context`.
8. **Iplanic-Native Handoffs**: Supporting optional `intake_control.provenance` for L1 Assurance plan import and aligning Section 9 detached receipts with `iplan-evidence-bundle.schema.json`.

---

## User Review Required

> [!NOTE]
> All new template fields (`intake_control`, `attestation`, `skip_audit`, and `timeouts`) carry `_required: false` or are declared as optional extensions. This ensures 100% backward compatibility for existing IPLAN documents and preserves clean passes in `tests/acceptance/deterministic/test_layer_iplan.py`.

Separate considerations:

> [!IMPORTANT]
> The signature block supports an unsigned fallback (`_UNSIGNED: { key_id: null, algorithm: "hmac-sha256", value: null }`), mirroring Iplanic's production standard. Local developers and agents without keystores execute unimpeded while enterprise multi-agent clusters enforce full Ed25519 verification.

---

## Open Questions

None. The design natively maps to existing conventions proven in `aidoc-flow-iplanic`, `aidoc-flow-iplan-standard`, and `ADAPTATION_SURFACE.yaml`.

---

## Proposed Changes

### Component 1: Layer 08 Workflow Governance Standard

#### [MODIFY] [IPLAN_WORKFLOW_STANDARD.md](../framework/governance/IPLAN_WORKFLOW_STANDARD.md)

- Update §9 (`Execution Evidence Receipts Specification`) to align receipt properties with `iplan-evidence-bundle.schema.json` (`plan_ref`, `execution_evidence`, `assurance`, `seal.canonical_hash`, `seal.signature`), include `valid_until` / `evidence_ttl_s`, and define downstream Layer 10 (EVAL) post-validation ingestion.
- Add §10 (`Cryptographic Agent Attribution & Step Digital Signatures`):
  - Formally specify the dual-identity model (`executor_id` vs `protocol_agent_id`).
  - Define the step `attestation` schema, RFC 8785 canonical JSON serialization, and Ed25519/HMAC-SHA256 signature verification.
  - Define the `_UNSIGNED` schema-valid fallback contract (`{ key_id: null, algorithm: "hmac-sha256", value: null }`).
  - Define Dual-Anchor Freshness (wall-clock TTL + Git tree SHA binding).
- Add §11 (`Distributed Worker Handover, Timeouts & Completeness`):
  - §11.1: Pre-flight verification contract for multi-worker DAG execution with canonical `verifies` relation.
  - §11.2: Step-Execution Completeness Gate (`VerifyStepExecutionCompleteness`) and mandatory `skip_audit` format (`justification`, `authorized_by`, `approved_at`) for skipped steps.
  - §11.3: State execution ceilings and action timeouts (`stateExecTimeout`, `actionExecTimeout`).
  - §11.4: Distributed task lease lifecycle and stale-worker reaper semantics.
- Renumber existing `## 10. Review Log` to `## 12. Review Log` and record CHG-121 pass.

---

### Component 2: Layer 08 & Layer 10 Templates and Schemas

#### [MODIFY] [IPLAN-TEMPLATE.yaml](../framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml)

- Add optional root-level `intake_control:` block (`_required: false`) supporting `provenance` (`initiator_key_id`, `algorithm`, `signed_at`, `value`) for L1 Assurance intake by Iplanic.
- Enrich `work_orders.orders[]` with optional `attestation:` block (`executor_id`, `protocol_agent_id`, `occurred_at`, `valid_until`, `evidence_summary`, `signature`) and `skip_audit:` structure.

#### [MODIFY] [IPLAN-GRAPH-TEMPLATE.yaml](../framework/layers/08_IPLAN/IPLAN-GRAPH-TEMPLATE.yaml)

- Add `attestation` and `timeouts` properties (`executor_id`, `protocol_agent_id`, `signature_algorithm`, `output_tree_sha`, `state_timeout_s`) to `task_action` properties.
- Add downstream-to-upstream pre-flight verification edges using the canonical `verifies` relation (`relation: "verifies"`) with `properties.verification_type: "preflight_attestation"` (satisfying `sdd-graph.schema.json` enum restrictions).

#### [MODIFY] [EVAL-REPORT-TEMPLATE.yaml](../framework/layers/10_EVAL/EVAL-REPORT-TEMPLATE.yaml)

- Enrich Section 2 `iplan_context:` with `iplan_receipt_ref:` and `receipt_seal_hash:` to formalize post-validation evidence anchoring.

---

### Component 3: CNCF Serverless Workflow & Governance State Machine

#### [MODIFY] [IPLAN-SWF-TEMPLATE.yaml](../framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml) and [iplan-execution.sw.yaml](../framework/governance/workflows/iplan-execution.sw.yaml)

- Declare `verifyAttestationReceipt` and `verifyStepCompleteness` under workflow `functions:` (`operation: "urn:aidoc:governance:attestation#verify"`, `type: custom`).
- Add state and action timeouts (`timeouts: { stateExecTimeout: "PT15M", actionExecTimeout: "PT5M" }`) to mutating operation states (`Step3_ImplementTestsFirst`, `Step4_ImplementSourceCode`, `Step5_VerifyImplementationSuite`).
- Update `Step1_PreFlightCheck` to include `verifyUpstreamAttestation` checking upstream receipts, TTL, and tree hashes.
- Add `EvaluatePreFlightGate` switch state branching on `${ .preflight.verified == true }` $\to$ `Step2_SnapshotOriginals`, else `transition: ExecutionBlockedTerminal`.
- Add `VerifyStepExecutionCompleteness` operation state prior to `Step6_CommitAndSignoff` verifying that no steps were silently skipped.
- Add `AttestStepCompletion` action under mutating states to generate step attestation facts.

---

### Component 4: Conformance Tests & Spec Gate

#### [MODIFY] [test_iplan_workflow.py](../tests/conformance/test_iplan_workflow.py)

- Add `test_distributed_attestation_and_iplanic_compatibility`:
  - Assert that `IPLAN-TEMPLATE.yaml` defines `intake_control` with `_required: false`.
  - Assert that `work_orders` carries attestation guidance and `valid_until` TTL.
  - Assert that `IPLAN_WORKFLOW_STANDARD.md` defines §10, §11, and §12.
  - Assert that `IPLAN-SWF-TEMPLATE.yaml` declares timeouts and completeness verification.
  - Test Ed25519 signature structure and `_UNSIGNED` schema validity against Iplanic schema expectations.

#### [MODIFY] [VERSION](../framework/VERSION) & [sync-version-refs.sh](../hooks/sync-version-refs.sh)

- Bump version `0.96.7` $\to$ `0.96.8`.
- Append `0.96.7` to `OLD_VERSIONS` in `hooks/sync-version-refs.sh` and run sweep.

---

## Verification Plan

### Automated Tests

- Run plan linter:

  ```bash
  python3 .agents/skills/verified-planning/check_plan.py plans/IPLAN-DISTRIBUTED-EXECUTION-ATTESTATION-PLAN.md
  ```

- Run Layer 08 acceptance tests:

  ```bash
  python3 -m unittest tests/acceptance/deterministic/test_layer_iplan.py -v
  ```

- Run Layer 08 conformance tests:

  ```bash
  python3 -m unittest tests/conformance/test_iplan_workflow.py -v
  ```

- Run SWF linter:

  ```bash
  python3 -m sdd_doc_lint.swf_lint framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml framework/governance/workflows/iplan-execution.sw.yaml
  ```

- Run pre-push checks and spec gate:

  ```bash
  python3 tests/chg/spec_gate.py --base origin/dev
  bash hooks/pre_push_check.sh
  ```

### Manual Verification

- Verify that `IPLAN-TEMPLATE.yaml` and `IPLAN-SWF-TEMPLATE.yaml` parse cleanly with PyYAML.
- Verify that `tests/acceptance/deterministic/test_layer_iplan.py` remains 100% green without modifying frozen golden fixtures.

---

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | `IPLAN_WORKFLOW_STANDARD.md` declares Section 9 `Execution Evidence Receipts Specification` | `## 9. Execution Evidence Receipts Specification (CHG-120, CHG-121)` | framework/governance/IPLAN_WORKFLOW_STANDARD.md:387 |
| 2 | Section 9 receipt declares `document_type: "iplan-execution-receipt"` | `document_type: "iplan-execution-receipt"` | framework/governance/IPLAN_WORKFLOW_STANDARD.md:393 |
| 3 | Section 8 defines the four orthogonal status planes table | `\| Plane \| Scope \| Permitted Values \| Mutation Authority \|` | framework/governance/IPLAN_WORKFLOW_STANDARD.md:373 |
| 4 | `IPLAN-TEMPLATE.yaml` defines `work_orders:` in Section 3 | `work_orders:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:389 |
| 5 | `IPLAN-TEMPLATE.yaml` defines Section 3b `failure_handling:` with `_required: false` | `failure_handling:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:432 |
| 6 | `IPLAN-GRAPH-TEMPLATE.yaml` defines `properties:` under task action node `TASK.08.01.xxxx` | `properties:` | framework/layers/08_IPLAN/IPLAN-GRAPH-TEMPLATE.yaml:39 |
| 7 | `IPLAN-SWF-TEMPLATE.yaml` defines `InitializeExecutionContext` inject state | `- name: InitializeExecutionContext` | framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml:159 |
| 8 | `IPLAN-SWF-TEMPLATE.yaml` defines `Step1_PreFlightCheck` operation state | `- name: Step1_PreFlightCheck` | framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml:167 |
| 9 | `iplan-execution.sw.yaml` defines `InitializeExecutionContext` inject state | `- name: InitializeExecutionContext` | framework/governance/workflows/iplan-execution.sw.yaml:64 |
| 10 | `test_layer_iplan.py` runs acceptance verification against IPLAN golden template | `self.assert_golden_passes_lint` | tests/acceptance/deterministic/test_layer_iplan.py:27 |
| 11 | `test_iplan_workflow.py` tests Layer 08 execution resilience and status taxonomy | `def test_execution_resilience_and_status_taxonomy_conformance` | tests/conformance/test_iplan_workflow.py:169 |
| 12 | `framework/VERSION` is bumped to `0.96.8` | `0.96.8` | framework/VERSION:1 |
| 13 | `hooks/sync-version-refs.sh` tracks version history in `OLD_VERSIONS` | `OLD_VERSIONS` | hooks/sync-version-refs.sh:128 |
| 14 | `ADAPTATION_SURFACE.yaml` defines `exec_test_timeout_s` ceiling knob | `- name: exec_test_timeout_s` | framework/governance/ADAPTATION_SURFACE.yaml:138 |
| 15 | `ADAPTATION_SURFACE.yaml` defines `exec_wall_clock_budget_s` ceiling knob | `- name: exec_wall_clock_budget_s` | framework/governance/ADAPTATION_SURFACE.yaml:172 |
| 16 | `EVAL-REPORT-TEMPLATE.yaml` defines `iplan_context` Section 2 snapshot | `iplan_context:` | framework/layers/10_EVAL/EVAL-REPORT-TEMPLATE.yaml:54 |

---

## Review log

### Pass 1 - 2026-10-19

- Dispatched independent adversarial subagent review (conversation `8cc40b88-136b-4144-a4bb-2018ea11d24c`).
- *Finding 1 (Load-Bearing)*: `sdd-graph.schema.json` strictly restricts `relation` to 9 enum values; `verifies_preflight_of` would fail `test_sdd_graph_schema.py`.
  - *Fix*: Standardized on canonical `verifies` relation with `properties.verification_type: "preflight_attestation"`.
- *Finding 2 (Load-Bearing)*: CNCF SWF `Step1_PreFlightCheck` (operation state) cannot conditionally branch to `ExecutionBlockedTerminal` without a switch state or `onErrors`, and `verifyAttestationReceipt` must be declared in `functions:`.
  - *Fix*: Added `EvaluatePreFlightGate` switch state and declared `verifyAttestationReceipt` under workflow `functions:`.
- *Finding 3 (Load-Bearing)*: `## 10. Review Log` already exists at line 421 of `IPLAN_WORKFLOW_STANDARD.md`.
  - *Fix*: Specified renumbering of existing `Review Log` to `## 12. Review Log` upon adding sections 10 and 11.
- *Finding 4 (Non-Load-Bearing)*: Claim 11 citation pinned to line 169 (method definition).
  - *Fix*: Updated Claim 11 to line 169 with symbol `def test_execution_resilience_and_status_taxonomy_conformance`.

### Pass 2 - 2026-10-19 - independent

- Folded all 3 load-bearing findings from Pass 1.
- Validated that `tests/acceptance/deterministic/test_layer_iplan.py` golden fixtures are protected via `_required: false`.
- Confirmed CNCF Serverless Workflow state machine transitions and functions are fully well-formed.
- Folded user requirements for Evidence TTL, state execution timeouts (`stateExecTimeout`, `actionExecTimeout`), and Step-Execution Completeness Gate auditing against accidental omission.
- Added Claims 14 and 15 citing adaptation surface execution bounds.
- Folded Layer 10 (EVAL) post-validation bridge: enriched `EVAL-REPORT-TEMPLATE.yaml` Section 2 `iplan_context` with receipt reference and seal hash, and added Claim 16.

### Pass 3 - 2026-10-19 - independent

- Dispatched fresh independent adversarial reviewer (conversation `b17c753e-cece-469f-b070-a6dd8ae1a779`).
- Verified all 16 citations in Claim Ledger against source files and lines.
- Simulated `swf_lint` on proposed state machine transitions, timeouts, and function declarations (clean, 0 findings).
- Confirmed Draft-07 validation of `IPLAN-GRAPH-TEMPLATE.yaml` against `sdd-graph.schema.json` with canonical `verifies` relation.
- Confirmed golden fixture protection in `test_layer_iplan.py` and Layer 10 EVAL compatibility.
- **Result:** ready — no further findings.
