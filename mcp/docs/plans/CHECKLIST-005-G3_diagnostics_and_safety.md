---
title: "CHECKLIST-005-G3: Diagnostics and Safety"
id: CHECKLIST-005-G3
date_created: 2026-03-27
last_updated: 2026-03-27
status: completed
owner: ai-agent
tags:
  - checklist
  - mcp
  - gap-closure
  - phase-g3
custom_fields:
  document_type: checklist
  parent_plan: IPLAN-005
  phase: G3
  timezone: America/New_York
---

## CHECKLIST-005-G3: Diagnostics and Safety

## 1. Phase Objective

Implement preflight diagnostics and remediation safety telemetry with deterministic output contracts and phase-level operator visibility.

## 2. Execution Checklist

### 2.1 Preflight Diagnostics (GAP-03)

- [x] Implement preflight command in CLI.
- [x] Add provider and runtime readiness checks.
- [x] Add deterministic fallback parsing for unstable provider output cases.
- [x] Add text and json output schema coverage.
- [x] Add pass, degraded, blocked, and runtime-error test scenarios.

### 2.2 Remediation Safety Telemetry (GAP-04)

- [x] Add source restoration telemetry fields to remediation reports.
- [x] Add report section describing restoration and mutation-guard outcomes.
- [x] Ensure telemetry emits only under applicable conditions.
- [x] Add tests for telemetry present and telemetry-absent branches.

### 2.3 Documentation and Release Artifacts

- [x] Update runbook and architecture docs with preflight and telemetry workflows.
- [x] Update roadmap with G3 completion state.
- [x] Add changelog entry for diagnostics and safety hardening.

## 3. Exit Gates

- [x] GAP-03 and GAP-04 are closed or formally deferred.
- [x] Preflight and telemetry outputs are schema-tested.
- [x] Documentation, roadmap, and changelog updates are merged.

## 4. Evidence Log

| Item | Evidence Path | Status | Owner | Date |
| --- | --- | --- | --- | --- |
| Preflight command tests | mcp/tests/unit/test_cli_main.py; mcp/tests/unit/test_preflight_runner.py | Completed | ai-agent | 2026-03-27 |
| Telemetry output tests | mcp/tests/unit/test_remediation_runner.py | Completed | ai-agent | 2026-03-27 |
| Operator workflow updates | mcp/docs/architecture/MCP_OPERATOR_RUNBOOK.md | Completed | ai-agent | 2026-03-27 |
| Roadmap update | mcp/docs/ROADMAP.md | Completed | ai-agent | 2026-03-27 |
| Changelog update | mcp/docs/CHANGELOG/CHANGELOG_v1.0.0.md | Completed | ai-agent | 2026-03-27 |
