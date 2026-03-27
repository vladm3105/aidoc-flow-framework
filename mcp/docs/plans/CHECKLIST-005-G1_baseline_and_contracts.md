---
title: "CHECKLIST-005-G1: Baseline and Contracts"
id: CHECKLIST-005-G1
date_created: 2026-03-27
last_updated: 2026-03-27
status: completed
owner: ai-agent
tags:
  - checklist
  - mcp
  - gap-closure
  - phase-g1
custom_fields:
  document_type: checklist
  parent_plan: IPLAN-005
  phase: G1
  timezone: America/New_York
---

## CHECKLIST-005-G1: Baseline and Contracts

## 1. Phase Objective

Establish measurable baseline evidence for GAP-01 through GAP-06 and freeze command and contract definitions required for downstream implementation phases.

## 2. Execution Checklist

### 2.1 Baseline Evidence

- [x] Capture current runtime behavior for gap-relevant commands and reports.
- [x] Record baseline status for GAP-01 through GAP-06 in the matrix.
- [x] Produce baseline parity notes for EARS, SPEC, TASKS, and CTR.

### 2.2 Contract Freeze

- [x] Confirm planned command names: consistency and preflight.
- [x] Confirm command output modes: text and json where applicable.
- [x] Confirm exit-code contract: 0 pass, 1 blocking failure, 2 runtime error.
- [x] Define schema fields for new diagnostics and telemetry outputs.

### 2.3 Documentation and Release Artifacts

- [x] Update architecture docs with planned command contracts and phase sequencing.
- [x] Update roadmap with G1 planned and baseline-complete status.
- [x] Add changelog note documenting contract freeze and baseline evidence publication.

## 3. Exit Gates

- [x] Baseline evidence exists for all six gaps.
- [x] Command names and exit semantics are frozen in plan and docs.
- [x] Roadmap and changelog updates are merged.

## 4. Evidence Log

| Item | Evidence Path | Status | Owner | Date |
| --- | --- | --- | --- | --- |
| Baseline matrix update | mcp/docs/plans/GAP-CLOSURE-MATRIX-001_mcp_ucx_gap_closure.md | Completed | ai-agent | 2026-03-27 |
| Architecture contract updates | mcp/docs/architecture/MCP_CLI_REFERENCE.md | Completed | ai-agent | 2026-03-27 |
| Baseline parity notes | mcp/docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md | Completed | ai-agent | 2026-03-27 |
| Diagnostics and telemetry schema fields | mcp/docs/specs/SPEC-004_mcp_reporting_lineage_artifact_contracts.md; mcp/docs/specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md | Completed | ai-agent | 2026-03-27 |
| Roadmap update | mcp/docs/ROADMAP.md | Completed | ai-agent | 2026-03-27 |
| Changelog update | mcp/docs/CHANGELOG/CHANGELOG_v1.0.0.md | Completed | ai-agent | 2026-03-27 |
