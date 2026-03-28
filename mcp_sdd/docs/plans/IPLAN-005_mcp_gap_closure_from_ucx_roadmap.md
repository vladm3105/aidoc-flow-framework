---
title: "IPLAN-005: MCP Gap Closure from UCX Roadmap"
id: IPLAN-005
date_created: 2026-03-27
last_updated: 2026-03-27
status: completed
owner: ai-agent
tags:
  - implementation-plan
  - mcp
  - roadmap
  - validation
  - diagnostics
  - governance
custom_fields:
  document_type: iplan
  plan_id: IPLAN-005
  status: completed
  execution_state: completed
  created_date: 2026-03-27
  timezone: America/New_York
---

## IPLAN-005: MCP Gap Closure from UCX Roadmap

## 1. Objective

Close the remaining MCP capability gaps identified from the UCX_v1 roadmap comparison, including validation parity, operational preflight diagnostics, artifact consistency controls, remediation safety telemetry, and stable finding and action identity.

## 2. Scope

### In Scope

1. Implement EARS validation parity and quality gate coverage under the MCP validation pipeline.
2. Implement a lightweight artifact consistency command for lineage and stage-chain checks without rerunning full validation.
3. Implement AI preflight diagnostics for provider and runtime readiness checks before review and remediation stages.
4. Implement remediation safety telemetry for source restoration and mutation-guard visibility.
5. Implement stable hash-based finding and action IDs for deterministic tracking.
6. Audit and strengthen SPEC, TASKS, and CTR validation parity where gaps are confirmed.
7. Update architecture and operator documentation for all delivered capabilities.
8. Update release history artifacts (roadmap and changelog) for each completed phase.

### Out of Scope

1. Real-time review streaming.
2. Interactive fix application UI.
3. VS Code extension packaging.

## 3. Gap Inventory and Target Outcomes

| Gap ID | Gap | Current MCP State | Target Outcome |
| --- | --- | --- | --- |
| GAP-01 | EARS validation parity | Layer registry exists; parity-level validators are not complete | EARS validation module and quality gates aligned to BRD and PRD contract depth |
| GAP-02 | Artifact consistency checks | Lineage rules exist in reporting contracts; no dedicated lightweight command | Dedicated command checks artifact availability, stage consistency, and lineage integrity |
| GAP-03 | AI preflight diagnostics | No explicit preflight command in current CLI | Deterministic preflight command with machine-readable output and exit semantics |
| GAP-04 | Remediation safety telemetry | Source-protected flow exists; telemetry is limited | Explicit telemetry fields and operator-visible report sections for source restore events |
| GAP-05 | Hash-based finding and action IDs | Hash utilities exist for contracts; findings and actions still need deterministic ID policy | Stable content-addressable IDs for findings and actions with backward-compatible parsing |
| GAP-06 | SPEC, TASKS, CTR parity depth | Generic layer support exists; parity depth is not baseline-audited in this cycle | Gap-audited and closed validation profile coverage for SPEC, TASKS, CTR |

## 4. Implementation Contracts and Constraints

### 4.1 Complexity and Resource Profile

| Workstream | Complexity (1-5) | CPU/Memory Impact | Storage Impact | Risk Level |
| --- | --- | --- | --- | --- |
| EARS parity validators | 4 | Validation runtime increases with rule count | Additional reports only | Medium |
| Artifact consistency command | 2 | Minimal | Minimal | Low |
| AI preflight diagnostics | 3 | Provider probe calls and parse overhead | Minimal | Medium |
| Remediation telemetry | 2 | Minimal | Report payload growth | Low |
| Hash-based IDs | 3 | Minimal hash computation overhead | Minimal | Medium |
| SPEC/TASKS/CTR parity audit and closure | 4 | Validation runtime increases with added rules | Additional fixtures and reports | Medium |

### 4.2 Failure Modes and Mitigations

1. False-positive validation failures due to strict parity rules.
   - Mitigation: introduce rule-level fixture coverage and threshold-controlled rollout.
2. Provider preflight instability due to non-deterministic responses.
   - Mitigation: parse fallback strategy and explicit degraded-state statuses.
3. Report consumer breakage from ID format transition.
   - Mitigation: dual-format compatibility window and parser-level normalization.
4. Overlapping checks between full validation and consistency command.
   - Mitigation: define strict non-overlap contract for consistency checks.

## 5. Workstreams

### 5.1 Workstream A: EARS Validation Parity

Target modules:

1. mcp_sdd/src/mcp_server/validation
2. mcp_sdd/src/mcp_server/creation/profile_contracts.py
3. mcp_sdd/tests/unit
4. mcp_sdd/tests/integration

Deliverables:

1. EARS-specific validator rules and quality gate enforcement.
2. EARS profile fixture set aligned to current contract schema.
3. Unit and integration coverage for pass and fail paths.

Acceptance criteria:

1. EARS layer validates with deterministic rule outputs.
2. Gate ordering and boundary checks match profile contract behavior.
3. Test suite includes positive and negative parity fixtures.

### 5.2 Workstream B: Artifact Consistency Command

Target modules:

1. mcp_sdd/src/mcp_server/cli/main.py
2. mcp_sdd/src/mcp_server/reporting/contracts.py
3. mcp_sdd/src/mcp_server/core
4. mcp_sdd/tests/unit/test_cli_main.py

Deliverables:

1. New command for lineage and stage artifact consistency checks.
2. JSON and text output schemas with stable exit semantics.
3. CI-safe execution contract that avoids full validation reruns.

Acceptance criteria:

1. Command detects missing or conflicting source, validation, and remediated artifacts.
2. Command validates upstream linkage integrity.
3. Exit behavior supports CI gating.

### 5.3 Workstream C: AI Preflight Diagnostics

Target modules:

1. mcp_sdd/src/mcp_server/cli/main.py
2. mcp_sdd/src/mcp_server/review
3. mcp_sdd/src/mcp_server/remediation
4. mcp_sdd/tests/unit
5. mcp_sdd/tests/integration

Deliverables:

1. New preflight command with provider availability and response-shape checks.
2. Optional runtime preflight hook before review and remediation invocation.
3. Machine-parseable diagnostics output.

Acceptance criteria:

1. Preflight reports explicit ready, degraded, or blocked statuses.
2. Preflight supports deterministic fallback parsing.
3. Runtime path can run with required preflight gating.

### 5.4 Workstream D: Remediation Safety Telemetry

Target modules:

1. mcp_sdd/src/mcp_server/remediation/runner.py
2. mcp_sdd/src/mcp_server/reporting/contracts.py
3. mcp_sdd/tests/unit/test_remediation_runner.py

Deliverables:

1. Structured telemetry fields for source protection and restore actions.
2. Report section for restoration summary and mutation guard outcomes.
3. Deterministic emission policy under protected mode.

Acceptance criteria:

1. Reports include restoration event counts and source paths.
2. Telemetry is emitted only when relevant conditions occur.
3. Protected-mode integrity behavior remains unchanged.

### 5.5 Workstream E: Hash-Based Finding and Action IDs

Target modules:

1. mcp_sdd/src/mcp_server/reporting
2. mcp_sdd/src/mcp_server/remediation
3. mcp_sdd/src/mcp_server/review
4. mcp_sdd/tests/unit
5. mcp_sdd/tests/integration

Deliverables:

1. Deterministic content-addressable ID generation for findings and actions.
2. Backward-compatible parser support for legacy sequential IDs.
3. Contract updates for ID shape and collision handling.

Acceptance criteria:

1. Identical content produces identical IDs across reruns.
2. Report consumers accept both old and new ID formats during transition.
3. Collision policy and hash source fields are documented and tested.

### 5.6 Workstream F: SPEC, TASKS, CTR Parity Audit and Closure

Target modules:

1. mcp_sdd/src/mcp_server/validation
2. mcp_sdd/src/mcp_server/creation/profile_contracts.py
3. mcp_sdd/tests/unit
4. mcp_sdd/tests/integration

Deliverables:

1. Baseline parity audit report for SPEC, TASKS, and CTR layers.
2. Missing rule implementation and fixture updates.
3. Coverage matrix updates with pass and fail evidence.

Acceptance criteria:

1. Each target layer has an explicit parity checklist.
2. Missing checks identified by audit are implemented or formally deferred.
3. Final validation matrix records closure status for all checklist items.

## 6. Documentation and Release-History Update Plan

### 6.1 Documentation Updates (Mandatory)

Update these active documents as each workstream completes:

1. mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md
2. mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md
3. mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md
4. mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md
5. mcp_sdd/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md
6. mcp_sdd/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md
7. mcp_sdd/docs/specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md
8. mcp_sdd/docs/specs/SPEC-010_mcp_prescreen_scan_scoring_contracts.md

Documentation acceptance checks:

1. Runtime command names and examples match implementation.
2. Lifecycle and artifact lineage sections reflect new command behavior.
3. Link validation passes for updated docs.

### 6.2 Changelog Updates (Mandatory)

1. Append a new dated entry to mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.0.0.md after each completed phase.
2. Record command additions, contract changes, and compatibility notes.
3. Include explicit migration notes for ID format transition.

### 6.3 Roadmap Updates (Mandatory)

1. Update mcp_sdd/docs/ROADMAP.md at phase boundaries.
2. Add planned and implemented milestones for gap-closure phases.
3. Move completed workstreams from planned to implemented sections with objective evidence.

## 7. Phase Schedule

### Phase G1: Baseline and Contracts

1. Create baseline gap-audit evidence for GAP-01 through GAP-06.
2. Freeze command contracts for consistency and preflight additions.
3. Publish spec-level contract deltas for validation and reporting.

Exit criteria:

1. Gap inventory has a measurable baseline status.
2. Contract deltas approved in docs/specs.
3. Roadmap updated with G1 completion status.

### Phase G2: Validation and Consistency Closure

1. Deliver Workstream A (EARS parity).
2. Deliver Workstream B (artifact consistency command).
3. Deliver Workstream F (SPEC/TASKS/CTR parity closure).

Exit criteria:

1. Validation parity gaps are closed or documented as deferred with rationale.
2. Consistency command is test-backed and CI-usable.
3. Documentation, changelog, and roadmap updates are merged.

### Phase G3: Diagnostics and Safety Hardening

1. Deliver Workstream C (AI preflight diagnostics).
2. Deliver Workstream D (remediation safety telemetry).

Exit criteria:

1. Preflight command and gating behavior are test-backed.
2. Safety telemetry appears in remediation outputs with deterministic schema.
3. Documentation, changelog, and roadmap updates are merged.

### Phase G4: Identity and Release Closure

1. Deliver Workstream E (hash-based IDs).
2. Complete compatibility window documentation and parser verification.
3. Publish final closure report for GAP-01 through GAP-06.

Exit criteria:

1. Hash-based ID policy is implemented with compatibility validation.
2. All gaps are marked closed or deferred with signed rationale.
3. Final changelog and roadmap entries published.

## 8. Validation and Evidence

Required validation commands:

1. Targeted unit and integration suites for each workstream.
2. Full MCP test suite after each phase merge.
3. Documentation link checks for mcp/docs updates.

Required evidence artifacts:

1. Phase-level test evidence logs.
2. Gap closure matrix with status per gap ID.
3. Release readiness note linked to roadmap and changelog updates.

## 9. Completion Definition

The plan is complete when all in-scope gaps are either:

1. Implemented with tests and active documentation updates.
2. Formally deferred with objective rationale, risk statement, and roadmap placement.

Mandatory completion deliverables:

1. Updated architecture and spec documents.
2. Updated changelog entries.
3. Updated roadmap milestones.
4. Final closure report under mcp_sdd/docs/plans.

## 10. Plan Review Findings and Corrections

### 10.1 Gaps Identified During Plan Review

1. New command naming for GAP-02 and GAP-03 was not frozen.
2. Exit-code contract was not explicit for consistency and preflight commands.
3. Phase-level evidence ownership and artifact naming were not standardized.
4. Deferral decision format was not defined for unresolved parity checks.

### 10.2 Corrections Applied

1. Freeze planned command names:
   - consistency
   - preflight
2. Freeze initial exit-code contract for both commands:
   - 0: success or pass
   - 1: blocking failures detected
   - 2: runtime or processing error
3. Standardize phase evidence artifacts:
   - CHECKLIST-005-G1_baseline_and_contracts.md
   - CHECKLIST-005-G2_validation_and_consistency.md
   - CHECKLIST-005-G3_diagnostics_and_safety.md
   - CHECKLIST-005-G4_identity_and_release.md
4. Standardize gap status and evidence tracking in:
   - GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md

## 11. Execution Artifacts and Ownership

### 11.1 Phase Checklist Artifacts

1. G1 checklist: mcp_sdd/docs/plans/CHECKLIST-005-G1_baseline_and_contracts.md
2. G2 checklist: mcp_sdd/docs/plans/CHECKLIST-005-G2_validation_and_consistency.md
3. G3 checklist: mcp_sdd/docs/plans/CHECKLIST-005-G3_diagnostics_and_safety.md
4. G4 checklist: mcp_sdd/docs/plans/CHECKLIST-005-G4_identity_and_release.md

### 11.2 Matrix Artifact

1. Gap closure matrix: mcp_sdd/docs/plans/GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md

### 11.3 Deferral Format

When a gap item cannot be closed in the current phase, record the following fields in the matrix:

1. Deferral reason
2. Risk impact
3. Target phase or roadmap version
4. Approver
5. Review date
