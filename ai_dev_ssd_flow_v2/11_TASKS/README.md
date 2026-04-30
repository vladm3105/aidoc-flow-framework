# AI Implementation Guide (TASKS) — Layer 11

## Overview

TASKS is the **AI agent's code-generation guide** — the bridge between SPEC documentation
and actual source code. Each TASKS document provides implementation plans with executable
commands, contracts, and verification criteria for one SPEC component.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

**This is the FINAL SDD layer.** TASKS downstream is source code and tests, not another layer.

## Two-Level Structure

| Document | Scope | Purpose |
|----------|-------|---------|
| `IMPLEMENTATION_PLAN_TEMPLATE.md` | Project-level | Orchestrator — orders TASKS by dependency, tracks phases |
| `TASKS-TEMPLATE.yaml` | Per-component | Implementation spec — 13 sections with execution commands |

The IMPLEMENTATION_PLAN reads ALL SPECs, performs dependency analysis, and determines
execution order. Individual TASKS documents are created in that order.

## Files

| File | Purpose |
|------|---------|
| `TASKS-TEMPLATE.yaml` | Per-task spec template (13 sections + handoff protocol) |
| `IMPLEMENTATION_PLAN_TEMPLATE.md` | Project orchestrator template |
| `IMPLEMENTATION_PLAN_TEMPLATE.yaml` | Orchestrator YAML structure |
| `IMPLEMENTATION_PLAN_README.md` | Orchestrator user guide |
| `TASKS-00_index.md` | TASKS registry |

## Template Sync Rule

```bash
cp ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.yaml mcp_sdd/templates/TASKS-TEMPLATE.yaml
```

## What Makes TASKS Unique

- **Execution Commands**: Runnable bash/shell for setup, implementation, validation
- **Implementation Contracts**: Protocol/ABC interfaces for parallel development
- **Session Handoff**: File-based state tracking for stateless MCP executor calls
- **Full Upstream Verification**: Checks all 10 layers before code generation
- **Development Plan Tracking**: Pre/post-execution gates with YAML checklists

## Element IDs

```text
Format: TASKS.{doc_id}.{section_id}.{hash}
Example: TASKS.01.03.g7k2
```

## Session Handoff Protocol

Each MCP executor call is independent. The TASKS document IS the handoff artifact:
1. Read Session Log → identify last session's state
2. Check code inventory → verify files exist
3. Find next incomplete step → continue (don't regenerate)
4. Update session log → state for next session

## MCP Tools (mcp_sdd)

Any CLI agent (Claude, Codex, Gemini, OpenCode, Copilot) can use TASKS via mcp_sdd:

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate TASKS from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | Execution-Ready score (>=90/100) |

## Archive

`TASKS_v1_archive/` contains deprecated template/rules/scripts files.
IMPLEMENTATION_PLAN templates remain active in this directory.
