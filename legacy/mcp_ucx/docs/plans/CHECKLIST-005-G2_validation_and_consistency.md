---
title: "CHECKLIST-005-G2: Validation and Consistency"
id: CHECKLIST-005-G2
date_created: 2026-03-27
last_updated: 2026-03-27
status: completed
owner: ai-agent
tags:
  - checklist
  - mcp
  - gap-closure
  - phase-g2
custom_fields:
  document_type: checklist
  parent_plan: IPLAN-005
  phase: G2
  timezone: America/New_York
---

## CHECKLIST-005-G2: Validation and Consistency

## 1. Phase Objective

Deliver validation parity closure for EARS and target layers, and implement a lightweight consistency command for lineage and stage-chain checks.

## 2. Execution Checklist

### 2.1 EARS Parity Implementation (GAP-01)

- [x] Implement EARS validation rules and quality gate checks.
- [x] Add EARS fixtures for positive and negative scenarios.
- [x] Add unit tests for rule outcomes and gate ordering.
- [x] Add integration tests for folder and single-document execution paths.

### 2.2 Consistency Command (GAP-02)

- [x] Implement consistency command in CLI.
- [x] Implement lineage and stage-chain checks without full validation rerun.
- [x] Add text and json output contracts.
- [x] Add command tests for pass, fail, and runtime-error cases.

### 2.3 SPEC TASKS CTR Parity Closure (GAP-06)

- [x] Complete parity audit for SPEC, TASKS, and CTR.
- [x] Implement missing checks or record formal deferrals.
- [x] Update fixtures and tests for each closed check.

### 2.4 Documentation and Release Artifacts

- [x] Update architecture and spec documents for G2 command and validator behavior.
- [x] Update roadmap with G2 completion state and delivered scope.
- [x] Add changelog entry for validation and consistency delivery.

## 3. Exit Gates

- [x] GAP-01, GAP-02, and GAP-06 are closed or formally deferred.
- [x] New command and validator behavior are test-backed.
- [x] Documentation, roadmap, and changelog updates are merged.

## 4. Evidence Log

| Item | Evidence Path | Status | Owner | Date |
| --- | --- | --- | --- | --- |
| EARS and parity-depth test evidence | mcp_ucx/tests/unit/test_validation_runner.py; mcp_ucx/tests/integration/test_migration_flows.py | Completed | ai-agent | 2026-03-27 |
| Consistency command tests | mcp_ucx/tests/unit/test_cli_main.py | Completed | ai-agent | 2026-03-27 |
| Parity audit update | mcp_ucx/docs/plans/GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md | Completed | ai-agent | 2026-03-27 |
| Roadmap update | mcp_ucx/docs/ROADMAP.md | Completed | ai-agent | 2026-03-27 |
| Changelog update | mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.0.0.md | Completed | ai-agent | 2026-03-27 |
