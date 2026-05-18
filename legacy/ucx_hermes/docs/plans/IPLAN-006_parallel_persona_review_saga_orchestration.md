---
title: "IPLAN-006: Parallel Persona Review Saga Orchestration"
id: IPLAN-006
date_created: 2026-05-04
last_updated: 2026-05-04
status: planned
owner: ai-agent
tags:
  - implementation-plan
  - hermes
  - orchestration
  - saga
  - review
  - personas
  - contracts
custom_fields:
  document_type: iplan
  plan_id: IPLAN-006
  execution_state: not_started
  created_date: 2026-05-04
  timezone: America/New_York
---

## IPLAN-006: Parallel Persona Review Saga Orchestration

## 1. Objective

Implement a Hermes orchestration mode for multi-persona review that executes persona branches in parallel with Saga transaction controls, then merges results deterministically for downstream governance decisions.

This plan is contract-first: normative specification updates must be completed before runtime behavior changes.

## 2. Scope

### In Scope

1. Parallel fan-out/fan-in execution for persona review branches.
2. Saga journal for branch lifecycle, retries, compensation actions, and escalation status.
3. Deterministic reducer for branch finding merge, deduplication, and provenance.
4. Chairperson synthesis over reduced findings.
5. Tool and CLI contract updates for orchestration controls.
6. Reporting/lineage naming for saga artifacts.
7. Documentation and test coverage updates.

### Out of Scope

1. Changes to UCX deterministic validator rule logic.
2. Direct executor delegation from document-critical UCX tools.
3. Automatic source-document mutation without policy gates.
4. Migration to external workflow engines.

## 3. Baseline and Gap Statement

Current baseline:

1. Review runtime builds a single combined multi-persona prompt path.
2. Persona mapping `mode` values are metadata-only and not runtime-active.
3. Lifecycle pipeline executes stages sequentially.

Documented gaps this plan resolves:

1. Missing runtime fan-out/fan-in orchestration modules.
2. Contract mismatch between desired review outputs and current review prompt-only contract.
3. Missing schema parameters for saga controls.
4. Missing saga artifact naming and lineage mapping.
5. Missing canonical ID enforcement in reducer output.
6. Missing dedicated test modules for scheduler/journal/reducer behavior.

## 4. Contract Change Gate (Mandatory Before Code)

No runtime implementation starts until the following contract updates are merged.

### 4.1 Required Spec Updates

1. `docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md`
   - add parallel review operational contract
   - define review branch output and fan-in reducer output as contract variants
2. `docs/specs/SPEC-008_mcp_output_schema_contracts.md`
   - add `sdd_review` schema fields for orchestration mode, retry policy, timeouts, and saga status outputs
3. `docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md`
   - define canonical saga journal/report naming, versioning, and lineage metadata
4. `docs/specs/SPEC-002_mcp_review_scoring_handoff_identity_contracts.md`
   - enforce `finding_id` and `action_id` format and required fields for reducer outputs

### 4.2 Contract Acceptance Criteria

1. Spec text explicitly states when review operates in prompt-only mode vs saga orchestration mode.
2. Required output fields for saga mode are machine-parseable and deterministic.
3. Saga artifacts include canonical lineage metadata and timezone-normalized timestamps.
4. ID and action identity contracts are unchanged or formally version-bumped with compatibility notes.

## 5. Target Runtime Outcome

### 5.1 Functional Outcomes

1. Review runs support bounded parallel execution across persona branches.
2. Each branch uses persona-scoped section context.
3. Branch outputs merge into deterministic reduced findings.
4. Branch failures trigger compensation before escalation.
5. Pipeline merge gate can consume saga escalation status.

### 5.2 Non-Functional Outcomes

1. Deterministic reducer output for identical inputs.
2. Idempotent retries keyed by `review_run_id` and `branch_id`.
3. Source protection preserved across all retry/compensation paths.

## 6. Workstreams

### 6.1 Workstream A: Tool and CLI Contract Surface

Target modules:

1. `src/mcp_server/tool_registry.py`
2. `src/mcp_server/cli/main.py`
3. `docs/architecture/MCP_CLI_REFERENCE.md`

Deliverables:

1. New review orchestration parameters (example):
   - `review_mode`: `prompt_only | saga_parallel`
   - `max_parallel_branches`
   - `branch_timeout_seconds`
   - `max_branch_retries`
   - `retry_backoff_seconds`
   - `saga_resume`
2. Validation and defaults for new parameters.
3. Backward-compatible behavior when parameters omitted.

Acceptance criteria:

1. MCP schema validates new parameters.
2. CLI exposes equivalent options.
3. Existing prompt-only review behavior remains default and unchanged.

### 6.2 Workstream B: Saga State Machine and Journal

Target modules:

1. `src/mcp_server/review/` (new orchestration and journal modules)
2. `src/mcp_server/models/` (state and payload contracts)

Deliverables:

1. Deterministic keys: `review_run_id`, `branch_id`.
2. Journal schema and append-only writes.
3. State machine with retry-loop transitions.

Canonical states:

1. `PREPARED`
2. `FANOUT_STARTED`
3. `BRANCH_RUNNING`
4. `BRANCH_COMPLETED`
5. `BRANCH_FAILED`
6. `BRANCH_COMPENSATING`
7. `FANIN_REDUCED`
8. `SYNTHESIZED`
9. `CLOSED`
10. `ESCALATED`

Required transitions:

1. `PREPARED -> FANOUT_STARTED`
2. `FANOUT_STARTED -> BRANCH_RUNNING`
3. `BRANCH_RUNNING -> BRANCH_COMPLETED | BRANCH_FAILED`
4. `BRANCH_FAILED -> BRANCH_COMPENSATING`
5. `BRANCH_COMPENSATING -> BRANCH_RUNNING` (retry path)
6. `BRANCH_COMPENSATING -> ESCALATED` (retry exhaustion path)
7. `BRANCH_COMPLETED -> FANIN_REDUCED`
8. `FANIN_REDUCED -> SYNTHESIZED`
9. `SYNTHESIZED -> CLOSED`

Acceptance criteria:

1. Journal records transitions and attempts deterministically.
2. Resume operation does not rerun completed branches.
3. Escalation state is terminal unless a new run is started.

### 6.3 Workstream C: Parallel Branch Scheduler and Context Partitioning

Target modules:

1. `src/mcp_server/review/runner.py`
2. `src/mcp_server/prompts/context_builder.py`
3. `src/mcp_server/skills/project_ucx_loader.py`

Deliverables:

1. Bounded parallel branch scheduler.
2. Persona-scoped section filtering policy with minimum coverage floor.
3. Branch-level timeout and retry hooks to saga journal.

Acceptance criteria:

1. Branch execution concurrency honors configured limit.
2. Branch payload contains scoped sections plus required structural blocks.
3. Token warnings emitted per branch sidecar when thresholds are exceeded.

### 6.4 Workstream D: Deterministic Fan-In Reducer and Identity Compliance

Target modules:

1. `src/mcp_server/review/` (new reducer module)
2. `src/mcp_server/models/context_engineering_contracts.py`

Deliverables:

1. Canonical finding normalization and deduplication by content hash.
2. Mandatory identity fields on merged findings:
   - `finding_id`
   - `action_id`
   - `priority`
   - `persona`
   - `message`
   - `recommended_action`
   - `provenance.branch_id`
   - `provenance.persona`
   - `content_hash`
3. Deterministic ordering and fingerprint for reduced output.

Acceptance criteria:

1. Identical inputs produce identical reduced outputs and fingerprints.
2. IDs satisfy canonical format constraints.
3. Reducer collision handling is deterministic and test-backed.

### 6.5 Workstream E: Compensation, Escalation, and Governance Wiring

Target modules:

1. `src/mcp_server/review/` orchestration modules
2. `src/mcp_server/tool_registry.py`
3. `docs/architecture/MCP_OPERATIONAL_FLOWS.md`
4. `docs/HERMES_INTEGRATION.md`
5. `docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`

Deliverables:

1. Compensation matrix for timeout, schema failure, reducer conflict, synthesis failure.
2. Saga status fields in review response payload for downstream gates.
3. Merge-gate language including saga escalation blocker.

Acceptance criteria:

1. Escalation status is machine-parseable in pipeline outputs.
2. Round-based governance sequence includes saga mode behavior.
3. Existing non-saga review workflow remains valid.

### 6.6 Workstream F: Artifact Naming and Lineage

Target artifacts:

1. saga journal file family
2. optional reducer output report family
3. optional synthesis output report family

Required naming contract (to be finalized by SPEC updates):

1. Names must use canonical doc-id rooted patterns and versioning.
2. Saga artifacts must carry source artifact, stage, and generated-at metadata.
3. Timestamps must include timezone offset and follow repository policy.

Acceptance criteria:

1. Artifact names and lineage pass reporting contract checks.
2. Collision handling is bounded and deterministic.

### 6.7 Workstream G: Tests and Evidence

Target tests:

1. `tests/unit/test_review_runner.py`
2. `tests/unit/test_saga_review_orchestrator.py` (new)
3. `tests/unit/test_saga_review_reducer.py` (new)
4. `tests/unit/test_saga_review_journal.py` (new)
5. `tests/unit/test_cli_main.py`
6. `tests/integration/test_prompt_context_builder.py`
7. `tests/integration/test_lifecycle_pipeline_integration.py`
8. `tests/integration/test_migration_flows.py`
9. `tests/integration/test_saga_review_pipeline.py` (new)

Acceptance criteria:

1. Happy path, retry path, and escalation path are covered.
2. Determinism assertions pass across repeated runs.
3. Prompt-only mode regression tests pass unchanged.

## 7. Implementation Contracts

### 7.1 Protocol Interfaces

1. `PersonaBranchExecutor.execute_branch(branch_input) -> BranchResult`
2. `ReviewReducer.reduce(branch_results) -> ReducedReview`
3. `SagaJournalStore.append/load/transition(...)`

### 7.2 Exception Hierarchy

1. `SagaBranchTimeoutError`
2. `SagaBranchSchemaError`
3. `SagaReducerConflictError`
4. `SagaSynthesisError`

Required fields per exception:

1. `error_code`
2. `stage`
3. `retryable`

### 7.3 Data Models

1. `ReviewSagaRun`
2. `ReviewSagaBranch`
3. `CompensationEvent`
4. `ReducedFinding`

## 8. Validation Procedure

Command set:

1. `pytest ucx_hermes/tests/unit/test_review_runner.py`
2. `pytest ucx_hermes/tests/unit/test_saga_review_orchestrator.py`
3. `pytest ucx_hermes/tests/unit/test_saga_review_reducer.py`
4. `pytest ucx_hermes/tests/unit/test_saga_review_journal.py`
5. `pytest ucx_hermes/tests/unit/test_cli_main.py`
6. `pytest ucx_hermes/tests/integration/test_prompt_context_builder.py`
7. `pytest ucx_hermes/tests/integration/test_lifecycle_pipeline_integration.py`
8. `pytest ucx_hermes/tests/integration/test_migration_flows.py`
9. `pytest ucx_hermes/tests/integration/test_saga_review_pipeline.py`

Additional checks:

1. Determinism check for reducer fingerprint and branch ordering.
2. Documentation link validation for updated docs.

## 9. Delivery Phases

### Phase P0: Contract Alignment (Mandatory)

1. Complete required spec updates in Section 4.
2. Update architecture docs to reflect dual-mode review behavior.
3. Freeze schema fields for saga controls.

Exit criteria:

1. Specs merged and internally consistent.
2. Tool/CLI schema changes approved.

### Phase P1: Core Runtime Scaffolding

1. Implement state models and journal.
2. Add scheduler hooks and runtime flags.
3. Add reducer skeleton with identity validation.

Exit criteria:

1. Unit tests pass for scaffolding modules.
2. Prompt-only path unaffected.

### Phase P2: Compensation and Governance Integration

1. Implement compensation and escalation handlers.
2. Wire saga status into lifecycle and merge-gate outputs.
3. Add integration tests for retry and escalation.

Exit criteria:

1. End-to-end saga mode passes integration tests.
2. Escalation blocks merge gate path as specified.

### Phase P3: Hardening and Evidence Publication

1. Finalize deterministic ordering and collision handling.
2. Publish changelog and roadmap evidence entries.
3. Run full regression suite.

Exit criteria:

1. Determinism tests pass across reruns.
2. Documentation and runtime behavior remain aligned.

## 10. Risk Register

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Over-parallelization | memory pressure and scheduler thrashing | bounded pool and adaptive throttling |
| Reducer non-determinism | unstable governance outcomes | strict ordering and hash-based dedup |
| Retry amplification | latency increase | bounded retries with terminal escalation |
| Under-selected context | missed findings | minimum section coverage floor and confidence guardrails |
| Contract drift | runtime/docs mismatch | phase-gated contract-first implementation |

## 11. Completion Definition

Plan completion requires:

1. Contract updates in SPEC-002, SPEC-004, SPEC-007, and SPEC-008 are merged.
2. Parallel saga review mode is implemented and test-backed.
3. Identity, lineage, and output schema compliance is verified.
4. Governance sequence includes saga escalation gate behavior.
5. Root documentation and roadmap/changelog entries are updated with evidence.
