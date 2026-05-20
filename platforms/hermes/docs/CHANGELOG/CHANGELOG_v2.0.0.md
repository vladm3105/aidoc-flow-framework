# Changelog v2.0.0

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

## Release Date

2026-05-02

## Overview

UCX Hermes v2.0.0 promotes `ucx_hermes/` to the **sole active MCP runtime** and deprecates `mcp_ucx/` (frozen at v1.22.0). This is a governance-hardening release, not a feature release. The core capability set remains identical; the changes are architectural safety boundaries.

---

## Breaking Changes

### 1. AI Executor Delegation Removed

**What changed**: The `executor` parameter no longer triggers AI agent execution in document-critical tools. Instead, the tools return structured text (reports, prompts, fix instructions) for human or Hermes review.

**Affected tools**:
- `sdd_validate` (fix path; `executor` parameter)
- `sdd_create_build`
- `sdd_review`
- `sdd_remediate` (all 3 remediation modes)

**Before**: Passing `executor` to these tools spawned a stateless CLI or API AI agent that rewrote documents without context of the conversation or human approval.

**After**: The same tools return deterministic findings + human-readable instructions. The caller (Hermes or human) decides whether and how to apply changes.

**Migration**: No code migration needed. If your workflow depended on silent auto-rewrite, switch to:
1. Call tool without `executor`
2. Receive prompt/report text
3. Feed text to Hermes with explicit instruction to edit
4. Review diff before saving

See `docs/HERMES_INTEGRATION.md` for detailed safe workflow.

---

## New Components

### 2. Hermes Bridge Skill

**Path**: `skills/hermes/ucx-sdd-bridge/SKILL.md`

**Purpose**: Codifies the safe UCX-Hermes integration contract for the agent.

**Contents**:
- Tool safety classification (18 safe deterministic vs 4 human-gated)
- Standard 6-phase workflow (init → validate → review → remediate → score → advance)
- Dangerous patterns to refuse
- Memory conventions for cross-session project state
- Configuration notes for `.mcp.json`

**Installation**:
```bash
cp -r /opt/data/ucx_framework/ucx_hermes/skills/hermes/ucx-sdd-bridge ~/.hermes/skills/
hermes skills enable ucx-sdd-bridge
```

### 3. Hermes Integration Documentation

**Path**: `docs/HERMES_INTEGRATION.md`

**Purpose**: Complete reference for integrating UCX with Hermes Agent.

**Contents**:
- Architecture diagram (Hermes + UCX)
- Safe vs unsafe tool reference table
- Configuration steps (MCP config, skill install, project setup)
- Standard workflow example (6 phases)
- Troubleshooting guide
- Migration from pre-patched UCX

### 4. Migration Guide

**Path**: `docs/migration/MIGRATION_FROM_MCP_UCX.md`

**Purpose**: Step-by-step guide for moving from `mcp_ucx/` to `ucx_hermes/`.

**Contents**:
- Path mapping (old → new)
- MCP configuration changes
- What was patched and why
- Verification checklist
- Rollback instructions

---

## Documentation Updates

### 5. Canonical Documentation Moved

All canonical docs now maintained under `ucx_hermes/docs/`:
- `README.md` — primary entry point, declares v2.0.0 canonical status
- `ROADMAP.md` — version updated to 2.0.0
- Architecture, specs, policies, plans, changelogs — all migrated

`mcp_ucx/docs/` is **frozen**. A deprecation banner was added to `mcp_ucx/docs/README.md`.

### 6. Template References Updated

All YAML templates in `ucx_hermes/templates/` updated to reference `ucx_hermes` instead of `mcp_ucx`:
- `BRD-TEMPLATE.yaml`
- `PRD-TEMPLATE.yaml`
- `EARS-TEMPLATE.yaml`
- `BDD-TEMPLATE.yaml`
- `ADR-TEMPLATE.yaml`
- `SPEC-TEMPLATE.yaml`
- Archive templates (SYS, REQ, CTR, TSPEC, TASKS)

### 6a. Template v3 Layer Alignment

All active templates were re-sourced from `ucx_flow_v3/` (canonical v3.2 layer definitions) to remove stale references to cut layers:

| Before (v2 layers in templates) | After (v3.2 only) |
|---|---|
| BRD downstream referenced SYS, REQ, CTR, TSPEC, TASKS | BRD downstream: PRD only |
| PRD downstream referenced REQ, CTR, SYS, TSPEC, TASKS | PRD downstream: EARS only |
| SPEC downstream referenced TSPEC → TASKS → Code | SPEC downstream: TDD → IPLAN → Code |
| Layer numbers misaligned (SPEC as Layer 9 in some headers) | SPEC = Layer 6, TDD = Layer 7, IPLAN = Layer 8 |
| C4 mapping used v2 4-layer map with SYS/REQ/CTR | C4 mapping: BRD→PRD→SPEC→Code |

Cut layers moved to `templates/archive/`:
- `SYS-TEMPLATE.yaml` → archive (ADR replaces architecture decisions)
- `REQ-TEMPLATE.yaml` → archive (EARS replaces formal requirements)
- `CTR-TEMPLATE.yaml` → archive (SPEC inline contracts)
- `TSPEC-TEMPLATE.yaml` → archive (TDD Section 4 embeds test cases)
- `TASKS-TEMPLATE.yaml` → archive (IPLAN replaces execution planning)

**Rule enforced**: Active templates must reference only the 8 v3.2 layers. Archive templates are historical artifacts.

### 7. Root README Updated

The framework-level `README.md` at `/opt/data/ucx_framework/README.md` now:
- Lists `ucx_hermes/` as primary
- Marks `mcp_ucx/` as deprecated
- References `ucx_hermes` version 2.0.0
- Points quick-start and validation examples to `ucx_hermes`

### 8. Runtime Environment Document Updated

`HERMES_UCX_RUNTIME_ENVIRONMENT.md` updated to reference `ucx_hermes` lifecycle engine path.

### 9. MCP Configuration Updated

`.mcp.json` at framework root updated:
- `cwd` changed from `/opt/data/ucx_framework/mcp_ucx/src` to `/opt/data/ucx_framework/ucx_hermes/src`

---

## Code Reference Updates

### 10. Logger Naming

`src/mcp_server/logging_config.py`:
- Logger name changed from `mcp_ucx` to `ucx_hermes`
- Log file name changed from `mcp_ucx.log` to `ucx_hermes.log`
- Module docstring updated

### 11. pyproject.toml

- `name`: `mcp-ucx-server` → `ucx-hermes-server`
- `version`: `0.1.0` → `2.0.0`
- `description`: Updated to mention Hermes

### 12. Inline Comments

`src/mcp_server/utils/source_files.py`:
- Comment updated to reference `ucx_hermes`

`src/mcp_server/executor/api_runner.py`:
- Error message updated to `pip install 'ucx_hermes[api]'`

---

## Deprecated / Removed

| Component | Status | Replacement |
|-----------|--------|-------------|
| `mcp_ucx/` directory | Frozen at v1.22.0, deprecated | `ucx_hermes/` v2.0.0+ |
| AI executor in `sdd_validate` fix path | Removed | Returns `fix_report` text only |
| AI executor in `sdd_create_build` | Removed | Returns creation prompt + metadata |
| AI executor in `sdd_review` | Removed | Returns assembled `prompt_text` |
| AI executor in `sdd_remediate` | Removed | Returns fix instructions only |

---

## Verification

- [x] `python3 -m py_compile src/mcp_server/tool_registry.py` → SYNTAX OK
- [x] `python3 -m py_compile src/mcp_server/logging_config.py` → SYNTAX OK
- [x] `python3 -m py_compile src/mcp_server/executor/api_runner.py` → SYNTAX OK
- [x] `python3 -m py_compile src/mcp_server/utils/source_files.py` → SYNTAX OK
- [x] `python3 -m py_compile src/mcp_server/server.py` → SYNTAX OK
- [x] All template `mcp_ucx` references replaced with `ucx_hermes`
- [x] Root README, pre-commit config, MCP config updated
- [x] Migration guide and integration doc created

---

## References

- `docs/HERMES_INTEGRATION.md` — Hermes integration architecture
- `skills/hermes/ucx-sdd-bridge/SKILL.md` — Bridge skill
- `docs/migration/MIGRATION_FROM_MCP_UCX.md` — Migration guide
- `docs/ROADMAP.md` — Forward roadmap
