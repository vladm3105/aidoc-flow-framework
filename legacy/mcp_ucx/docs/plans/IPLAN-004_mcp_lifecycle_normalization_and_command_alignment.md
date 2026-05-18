---
title: "IPLAN-004: MCP Lifecycle Normalization and Command Alignment"
id: IPLAN-004
date_created: 2026-03-27
last_updated: 2026-03-27
status: completed
owner: ai-agent
tags:
  - implementation-plan
  - mcp
  - history
  - documentation
  - lifecycle
custom_fields:
  document_type: iplan
  plan_id: IPLAN-004
  status: completed
  created_date: 2026-03-27
  timezone: America/New_York
---

## IPLAN-004: MCP Lifecycle Normalization and Command Alignment

## 1. Objective

Record the completed MCP updates that normalized the document lifecycle flow across all SSD layers, aligned active command naming from `validate-build` to `validate`, and documented the project-initialization path required before document creation.

## 2. Scope

### In Scope

1. Generalize the source-protected derived-artifact flow to all supported document layers.
2. Normalize active CLI naming from `validate-build` to `validate`.
3. Document the `init` -> `create-build` -> `create` project initialization and document creation flow.
4. Update roadmap and changelog artifacts to preserve release history.

### Out of Scope

1. New autopilot orchestration behavior.
2. New diagnostics command families beyond already implemented runtime capabilities.
3. Changes to archived historical records that intentionally preserve older command names.

## 3. Implemented Changes

### 3.1 Runtime and CLI

1. Renamed the active validation command from `validate-build` to `validate` in the MCP CLI.
2. Preserved the six-stage lifecycle contract:
   - `create`
   - `validate`
   - `validate-fix`
   - `review`
   - `remediate`
   - `remediate-fix`
3. Generalized folder-based artifact resolution rules:
   - `validate`, `validate-fix`, and `remediate` resolve the canonical source artifact from a document folder.
   - `remediate-fix` resolves the `_validation` derived artifact from a document folder.
4. Normalized remediated artifact naming to canonical base-stem output:
   - `{slug}_remediated.md`
   - not `{slug}_validation_remediated.md`

### 3.2 Documentation

1. Expanded `MCP_OPERATIONAL_FLOWS.md` to include:
   - project initialization flow (`init` and `create-build`)
   - end-to-end six-stage lifecycle flow
   - artifact lineage and source-resolution rules
2. Expanded `MCP_CLI_REFERENCE.md` to include:
   - updated `validate` command contract
   - derived-artifact lineage rules
   - project initialization examples
3. Updated active runtime-facing documentation and runbook references to use `validate` as the canonical command name.

## 4. Affected Artifacts

### 4.1 Runtime and Tests

1. `mcp_ucx/src/mcp_server/cli/main.py`
2. `mcp_ucx/src/mcp_server/remediation/runner.py`
3. `mcp_ucx/tests/unit/test_cli_main.py`
4. `mcp_ucx/tests/unit/test_validation_runner.py`
5. `mcp_ucx/tests/unit/test_remediation_runner.py`
6. `mcp_ucx/tests/integration/test_migration_flows.py`

### 4.2 Active Documentation

1. `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
2. `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md`
3. `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
4. `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md`
5. `mcp_ucx/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`
6. `mcp_ucx/docs/specs/SPEC-008_mcp_output_schema_contracts.md`
7. `mcp_ucx/docs/ROADMAP.md`
8. `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.0.0.md`

## 5. Acceptance Evidence

### 5.1 Runtime Validation

1. Full MCP test suite passed after command rename and lifecycle normalization.
2. Result snapshot:
   - `107 passed, 2 warnings`

### 5.2 Documentation Alignment

1. Active operational and CLI docs now use `validate` as the canonical command name.
2. Active docs describe the project initialization flow and the six-stage lifecycle using MCP-native naming.
3. Historical artifacts remain unchanged where they are intended to preserve earlier release terminology.

## 6. Release Impact

1. MCP active runtime naming is now consistent with the documented lifecycle.
2. Derived-artifact flow is documented as a cross-layer contract instead of a PRD-specific exception.
3. Project-local scaffold generation is explicitly documented as a prerequisite for creation flows.

## 7. Completion Record

| Date | Status | Notes |
| --- | --- | --- |
| 2026-03-27 | Completed | Lifecycle flow generalized across layers, `validate` naming normalized, roadmap/changelog updated |