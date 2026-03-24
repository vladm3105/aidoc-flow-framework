# PLAN-016: UCX v2 — MCP-First Clean Slate Architecture

| Field | Value |
| --- | --- |
| **Plan ID** | PLAN-016 |
| **Title** | UCX v2 — MCP-First Clean Slate Architecture |
| **Status** | Approved |
| **Author** | UCX Team |
| **Date** | 2026-03-23 |
| **Target Version** | UCX v2.0.0 |
| **Supersedes** | PLAN-015 (version strategy) |

---

## 1. Context and Motivation

### 1.1 UCX v1 Structural Problem

UCX v1 was designed around a Click-based CLI (`ucx validate`, `ucx review`, `ucx remediate`). The MCP layer (`ucx/mcp/`) was added to v1 as an afterthought in PLAN-014, wrapping existing CLI-oriented functions.

This produced structural problems:

| Problem | Root Cause |
| --- | --- |
| Validator functions format output for terminal display | CLI formatting mixed into core logic |
| MCP tools delegate to CLI internals | No clean API boundary |
| `apply_ucx_action_fixes()` straddles CLI and MCP | Shared utility born from workaround |
| `tools_prd.py` reimplements contract checks | Redundant to `ucx/core/ucrem.py` |
| PRD `prd.py` flat-file validator vs `prd/` directory validators | Two parallel PRD subsystems |

### 1.2 Decision

**Archive UCX v1 as `UCX_v1_archive/`.** Start UCX v2 from scratch in `UCX/` with MCP as the primary — and only — user-facing interface.

No CLI entrypoint in v2. Agents drive document lifecycle via MCP tools.

---

## 2. Architecture Decision

### 2.1 Interface Model

| UCX v1 | UCX v2 |
| --- | --- |
| CLI primary (`ucx` command) | MCP primary (`ucx-mcp` server) |
| MCP wraps CLI | MCP wraps pure validators |
| Script-based automation | Agent-driven workflows |
| Click decorators on validators | FastMCP tool functions |
| Mixed output (terminal + structured) | Structured dicts only |

### 2.2 No Backward Compatibility

UCX v2 does not maintain CLI compatibility. Users migrating from v1:

- Replace `ucx validate brd <path>` → `brd_validate(brd_path=<path>)` (MCP tool call)
- Replace `ucx review prd <path>` → `prd_review(prd_path=<path>)` (MCP tool call)
- Replace shell automation → agentic workflow via `agents/workflow.py` stages

Migration reference: `UCX_v1_archive/docs/MIGRATION_v2.md` (to be created).

---

## 3. UCX v2 Directory Structure

```
UCX/                                  # UCX v2.0.0 — MCP-first
├── pyproject.toml                    # v2.0.0, fastmcp-first, no click
├── README.md                         # v2 overview and quickstart
├── ucx/                              # Python package
│   ├── __init__.py
│   ├── version.py                   # "2.0.0"
│   ├── exceptions.py                # Exception hierarchy
│   │
│   ├── mcp/                         # PRIMARY interface (FastMCP)
│   │   ├── __init__.py
│   │   ├── server.py                # FastMCP server entry
│   │   └── tools/                   # Per-layer tool namespaces
│   │       ├── __init__.py
│   │       ├── registry.py         # Tool registration
│   │       ├── brd.py              # brd_* tools (Layer 1)
│   │       ├── prd.py              # prd_* tools (Layer 2)
│   │       ├── ears.py             # ears_* tools (Layer 3)
│   │       ├── adr.py              # adr_* tools (Layer 5)
│   │       ├── sys.py              # sys_* tools (Layer 6)
│   │       ├── req.py              # req_* tools (Layer 7)
│   │       └── ctr.py              # ctr_* tools (Layer 8)
│   │
│   ├── validators/                  # Pure validation logic (no CLI coupling)
│   │   ├── __init__.py
│   │   ├── base.py                 # Validator protocol
│   │   ├── result.py               # ValidationResult, Finding, Severity
│   │   └── layers/                 # Per-layer validator implementations
│   │       ├── __init__.py
│   │       ├── brd.py
│   │       ├── prd.py
│   │       ├── ears.py
│   │       ├── adr.py
│   │       ├── sys.py
│   │       ├── req.py
│   │       └── ctr.py
│   │
│   ├── agents/                      # Agentic workflow orchestration
│   │   ├── __init__.py
│   │   ├── workflow.py             # Stage machine
│   │   └── stages.py               # Stage enum and transitions
│   │
│   ├── models/                      # Pydantic data models
│   │   ├── __init__.py
│   │   └── document.py             # DocumentType, LayerInfo, ArtifactClass
│   │
│   └── config/                      # Configuration
│       ├── __init__.py
│       └── settings.py             # UCXSettings (pydantic-settings)
│
├── docs/                            # v2 documentation
│   ├── ROADMAP.md                  # v2 roadmap
│   ├── MIGRATION_FROM_V1.md        # Migration reference
│   └── plans/                      # v2 plan documents (start at PLAN-001)
│
└── tests/                           # Test suite
    ├── __init__.py
    └── mcp/
        ├── __init__.py
        └── test_server.py
```

---

## 4. Design Principles

### 4.1 Layer Isolation

Each SDD document layer has its own tool namespace module (`brd.py`, `prd.py`, etc.). No cross-layer tool coupling.

### 4.2 Pure Validators

`ucx/validators/` modules return `ValidationResult` objects. They contain no terminal output formatting, no click decorators, no file-writing side effects. Side effects belong only in MCP tool handlers.

### 4.3 Structured Returns

All MCP tools return `dict`. Keys:
- `status`: `"ok"` | `"error"` | `"warning"`
- `path`: absolute path of the document acted upon
- `findings`: list of finding dicts (when applicable)
- `next_step`: recommended next action for the agent
- `data`: tool-specific payload

### 4.4 Agents Drive Workflow

`ucx/agents/workflow.py` defines the stage machine (validate → review → remediate → apply). MCP tools call into this layer. An agent orchestrates tool calls in sequence.

### 4.5 No Global State

No module-level singletons. `UCXSettings` is injected into tool classes at construction time. This enables testability without monkeypatching.

### 4.6 Async-First

All MCP tool methods are `async`. Validators expose both sync and async APIs. IO operations use `asyncio`.

---

## 5. MCP Tool Inventory (v2.0.0 Scope)

### 5.1 Tool Naming Convention

`{layer_prefix}_{action}` where:

- `{layer_prefix}` = `brd` | `prd` | `ears` | `adr` | `sys` | `req` | `ctr`
- `{action}` = `validate` | `validate_fix` | `review` | `remediate` | `remediate_apply` | `status` | `artifacts`

### 5.2 Tool Matrix (Phase 1)

| Tool | Layer | Action | Description |
| --- | --- | --- | --- |
| `brd_validate` | BRD | validate | Quality gate validation |
| `brd_review` | BRD | review | AI-driven review |
| `brd_remediate` | BRD | remediate | Apply AI remediations |
| `brd_status` | BRD | status | Workflow completeness |
| `prd_validate` | PRD | validate | PRD quality gate validation |
| `prd_validate_fix` | PRD | validate_fix | Fix validation issues |
| `prd_review` | PRD | review | AI-driven PRD review |
| `prd_remediate` | PRD | remediate | Generate remediation report |
| `prd_remediate_apply` | PRD | remediate_apply | Apply remediation patches |
| `prd_artifacts` | PRD | artifacts | Classify PRD artifacts in dir |
| `prd_status` | PRD | status | PRD workflow completeness |
| `ears_validate` | EARS | validate | EARS quality gate |
| `ears_review` | EARS | review | AI EARS review |
| `adr_validate` | ADR | validate | ADR quality gate |
| `adr_review` | ADR | review | AI ADR review |
| `sys_validate` | SYS | validate | SYS quality gate |
| `req_validate` | REQ | validate | REQ quality gate |
| `ctr_validate` | CTR | validate | CTR quality gate |

---

## 6. Archive Strategy

### 6.1 Archive Location

```
/opt/data/docs_flow_framework/
├── UCX/               # v2.0.0 (new, MCP-first)
└── UCX_v1_archive/    # v1.x preserved (git mv)
```

### 6.2 What v1 Archive Contains

The entire UCX v1 codebase with all plans (PLAN-001 through PLAN-016), documentation, tests, validators, CLI code, and MCP prototype. It is read-only reference material.

### 6.3 Referencing v1

When porting validation logic from v1 to v2, reference the v1 archive:

```
# Reference: UCX_v1_archive/ucx/validators/brd/quality_gate.py
```

Validators in v2 are rewrites, not copies. They must not import from `UCX_v1_archive/`.

---

## 7. Plan Numbering in v2

v2 plans start at PLAN-001 in `UCX/docs/plans/`. They are independent of v1 plans in `UCX_v1_archive/docs/plans/`.

First v2 plans:

| Plan | Scope |
| --- | --- |
| PLAN-001 | UCX v2 BRD validator and `brd_*` MCP tools |
| PLAN-002 | UCX v2 PRD workflow and `prd_*` MCP tools (port PLAN-012/014 logic) |
| PLAN-003 | UCX v2 EARS validator and `ears_*` tools |
| PLAN-004 | UCX v2 remaining layers (ADR, SYS, REQ, CTR) |
| PLAN-005 | UCX v2 agentic workflow engine (`agents/`) |

---

## 8. Acceptance Criteria

- [ ] `UCX_v1_archive/` exists and contains full v1 source under git tracking
- [ ] `UCX/` contains v2 skeleton with `ucx/version.py` reporting `2.0.0`
- [ ] `ucx/mcp/server.py` starts a FastMCP server without errors
- [ ] All tool class stubs (`brd.py`, `prd.py`, etc.) are present with `raise NotImplementedError` bodies
- [ ] `ucx/validators/result.py` defines `ValidationResult`, `Finding`, `Severity`
- [ ] `ucx/validators/base.py` defines `Validator` Protocol
- [ ] `pyproject.toml` has `version = "2.0.0"` and no `click` dependency
- [ ] `docs/ROADMAP.md` reflects v2 plan sequence
- [ ] No imports from `UCX_v1_archive/` in any v2 source file
