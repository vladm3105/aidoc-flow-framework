# CHANGELOG v0.12.0

**Release Date**: 2026-03-30
**Type**: Minor (TASKS Template Unification — ALL 11 LAYERS COMPLETE)

## Summary

Unified the TASKS (Layer 11) artifact — the FINAL SDD layer. All 11 layers now have
unified YAML templates in `mcp_sdd/templates/`. The complete SDD workflow from business
requirements (BRD) to code generation (TASKS) is unified under a single template standard.

## Changes

### TASKS Layer Unification

- **New**: `TASKS-TEMPLATE.yaml` (475 lines, 2 pre-content + 13 numbered + glossary)
- **Replaced**: 6 core files (3,204 lines) archived to `TASKS_v1_archive/`
- **Kept active**: IMPLEMENTATION_PLAN_TEMPLATE.md/.yaml + README (project orchestrator)
- **mcp_sdd**: TASKS-TEMPLATE.yaml ADDED — completes **11 unified YAML templates**

### TASKS-Unique Features

- **Session Handoff Protocol**: File-based state tracking for stateless MCP executor calls
- **Full Upstream Chain Verification**: Pre-check verifies all 10 upstream layers
- **Execution Commands**: Runnable bash/shell (unique to TASKS)
- **Implementation Contracts**: Protocol/ABC interfaces for parallel development
- **Execution-Ready Score**: >=90/100 before code generation

### All Templates in mcp_sdd

```
ADR-TEMPLATE.yaml    CTR-TEMPLATE.yaml    REQ-TEMPLATE.yaml    TASKS-TEMPLATE.yaml
BDD-TEMPLATE.yaml    EARS-TEMPLATE.yaml   SPEC-TEMPLATE.yaml   TSPEC-TEMPLATE.yaml
BRD-TEMPLATE.yaml    PRD-TEMPLATE.yaml    SYS-TEMPLATE.yaml
```

## MILESTONE: Complete SDD Workflow Unified

| Layer | C4 Position | Template | Version |
|-------|-------------|----------|---------|
| BRD (1) | Context | `BRD-TEMPLATE.yaml` | v0.2.0 |
| PRD (2) | Container | `PRD-TEMPLATE.yaml` | v0.3.0 |
| EARS (3) | Transition | `EARS-TEMPLATE.yaml` | v0.4.0 |
| BDD (4) | Transition | `BDD-TEMPLATE.yaml` | v0.5.0 |
| ADR (5) | Bridge | `ADR-TEMPLATE.yaml` | v0.6.0 |
| SYS (6) | Component | `SYS-TEMPLATE.yaml` | v0.7.0 |
| REQ (7) | Decomposition | `REQ-TEMPLATE.yaml` | v0.8.0 |
| CTR (8) | Decomposition | `CTR-TEMPLATE.yaml` | v0.9.0 |
| SPEC (9) | Code | `SPEC-TEMPLATE.yaml` | v0.10.0 |
| TSPEC (10) | Validation | `TSPEC-TEMPLATE.yaml` | v0.11.0 |
| TASKS (11) | Execution | `TASKS-TEMPLATE.yaml` | v0.12.0 |

## Validation

- mcp_sdd: 173 passed, 0 regressions
- Template resolution: verified
- 11 templates in mcp_sdd/templates/
- MCP Ops Doc: updated to "All 11 layers unified"
- BRD glossary: TASKS definition added
