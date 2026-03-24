# PLAN-001: UCX v2 — MCP-First Clean Slate Architecture

| Field | Value |
| --- | --- |
| **Plan ID** | PLAN-001 |
| **Title** | UCX v2 — MCP-First Clean Slate Architecture |
| **Status** | Approved |
| **Author** | UCX Team |
| **Date** | 2026-03-23 |
| **Target Version** | UCX v2.0.0 |
| **Supersedes** | PLAN-016 (archived as v1 history) |

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
| Single monolithic agent | Orchestrator + one layer agent per SDD layer |

### 2.2 No Backward Compatibility

UCX v2 does not maintain CLI compatibility. Users migrating from v1:

- Replace `ucx validate brd <path>` -> `brd_validate(brd_path=<path>)` (MCP tool call)
- Replace `ucx review prd <path>` -> `prd_review(validation_prd_path=<path>)` (MCP tool call)
- Replace shell automation -> agentic workflow via `agents/orchestrator.py`

Migration reference: `UCX/docs/MIGRATION_FROM_V1.md`.

### 2.3 Multi-Agent Architecture

UCX v2 uses a **multi-agent model**: one Orchestrator coordinates one specialized agent per SDD layer.

```text
External AI Assistant
        │
        ▼  MCP tool calls
  ┌─────────────┐
  │ Orchestrator │   ucx_orchestrate(), ucx_status()
  └──────┬──────┘
         │  AgentRequest / AgentResponse
    ┌────┴────────────────────────────┐
    ▼                                 ▼
┌─────────┐                    ┌─────────┐
│ PRDAgent│  ...               │ BRDAgent│  ...
└────┬────┘                    └────┬────┘
     │  validators/layers/prd.py    │  validators/layers/brd.py
     ▼                              ▼
ValidationResult                ValidationResult
```

**Phased rollout:**

| Phase | Agents Active | Plan |
| --- | --- | --- |
| Phase 1 | Orchestrator + PRD agent | PLAN-002 |
| Phase 2 | + BRD agent | PLAN-003 |
| Phase 3 | + EARS agent, ADR agent | PLAN-004 |
| Phase 4 | + SYS, REQ, CTR agents | PLAN-005 |

The Orchestrator is the only MCP-facing component. Layer agents are internal implementation units called via `AgentRequest` / `AgentResponse` contracts. Layer agents do not call each other and have no direct MCP exposure.

---

## 3. UCX v2 Directory Structure

```text
UCX/                                  # UCX v2.0.0 — MCP-first
├── pyproject.toml                    # v2.0.0, fastmcp-first, no click
├── README.md                         # v2 overview and quickstart
├── ucx/                              # Python package
│   ├── __init__.py
│   ├── version.py                    # "2.0.0"
│   ├── exceptions.py                 # Exception hierarchy
│   │
│   ├── mcp/                          # PRIMARY interface (FastMCP)
│   │   ├── __init__.py
│   │   ├── server.py                 # FastMCP server entry
│   │   └── tools/                    # Per-layer tool namespaces
│   │       ├── __init__.py
│   │       ├── registry.py           # Tool registration
│   │       ├── brd.py                # brd_* tools (Layer 1)
│   │       ├── prd.py                # prd_* tools (Layer 2)
│   │       ├── ears.py               # ears_* tools (Layer 3)
│   │       ├── adr.py                # adr_* tools (Layer 5)
│   │       ├── sys.py                # sys_* tools (Layer 6)
│   │       ├── req.py                # req_* tools (Layer 7)
│   │       └── ctr.py                # ctr_* tools (Layer 8)
│   │
│   ├── validators/                   # Pure validation logic (no CLI coupling)
│   │   ├── __init__.py
│   │   ├── base.py                   # Validator protocol
│   │   ├── result.py                 # ValidationResult, Finding, Severity
│   │   └── layers/                   # Per-layer validator implementations
│   │       ├── __init__.py
│   │       ├── brd.py
│   │       ├── prd.py
│   │       ├── ears.py
│   │       ├── adr.py
│   │       ├── sys.py
│   │       ├── req.py
│   │       └── ctr.py
│   │
│   ├── agents/                       # Multi-agent orchestration layer
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # UCX Orchestrator — routes to layer agents
│   │   ├── base.py                   # LayerAgent protocol / ABC
│   │   ├── contract.py               # AgentRequest, AgentResponse models
│   │   ├── workflow.py               # Stage machine
│   │   ├── stages.py                 # Stage enum and transitions
│   │   └── layers/                   # Per-SDD-layer agent implementations
│   │       ├── __init__.py
│   │       ├── prd.py                # PRD agent (Phase 1)
│   │       ├── brd.py                # BRD agent (Phase 2)
│   │       ├── ears.py               # EARS agent (Phase 3)
│   │       ├── adr.py                # ADR agent (Phase 3)
│   │       ├── sys.py                # SYS agent (Phase 4)
│   │       ├── req.py                # REQ agent (Phase 4)
│   │       └── ctr.py                # CTR agent (Phase 4)
│   │
│   ├── models/                       # Pydantic data models
│   │   ├── __init__.py
│   │   └── document.py               # DocumentLayer, LayerInfo, ArtifactClass
│   │
│   └── config/                       # Configuration
│       ├── __init__.py
│       └── settings.py               # UCXSettings (pydantic-settings)
│
├── docs/                             # v2 documentation
│   ├── ROADMAP.md                    # v2 roadmap
│   ├── MIGRATION_FROM_V1.md          # Migration reference
│   └── plans/                        # v2 plan documents
│
└── tests/                            # Test suite
    ├── __init__.py
    ├── mcp/
    ├── unit/
    ├── smoke/
    └── regression/
```

---

## 4. Design Principles

### 4.1 Layer Isolation

Each SDD document layer has its own agent (`agents/layers/{layer}.py`) and its own MCP tool namespace module (`mcp/tools/{layer}.py`). The Orchestrator routes requests to the correct layer agent. Layer agents do not call each other. No cross-layer coupling anywhere in the call graph.

### 4.2 Pure Validators

`ucx/validators/` modules return `ValidationResult` objects. They contain no terminal output formatting, no click decorators, no file-writing side effects. Side effects belong only in MCP tool handlers.

### 4.3 Structured Returns

All MCP tools return `dict`. Keys:

- `status`: `"ok"` | `"error"` | `"warning"`
- `path`: absolute path of the document acted upon
- `findings`: list of finding dicts (when applicable)
- `next_step`: recommended next action for the agent
- `data`: tool-specific payload

### 4.4 Orchestrator Routes, Layer Agents Execute

The Orchestrator (`agents/orchestrator.py`) receives requests from an external AI assistant via MCP and routes each request to the appropriate layer agent using an `AgentRequest` contract. Each layer agent owns the full stage machine (validate → review → remediate → apply) for its layer. The stage transitions are defined in `agents/workflow.py` and `agents/stages.py`, shared across all layer agents.

### 4.5 No Global State

No module-level singletons. `UCXSettings` is injected into tool classes at construction time. This enables testability without monkeypatching.

### 4.6 Async-First

All MCP tool methods are `async`. Validators expose both sync and async APIs. IO operations use `asyncio`.

### 4.7 Agent Request/Response Contract

All Orchestrator-to-layer-agent calls use a shared typed contract (`agents/contract.py`):

| Model | Fields |
| --- | --- |
| `AgentRequest` | `stage`, `layer`, `document_path`, `context`, `policy_flags`, `trace_id` |
| `AgentResponse` | `status`, `stage`, `layer`, `findings`, `artifact_outputs`, `next_step`, `trace_id` |

Rules:
- No agent returns unstructured text.
- Layer agents must not raise uncaught exceptions. Errors are captured as `AgentResponse(status="error")` with `findings` populated.
- `trace_id` is set by the Orchestrator and threaded through to the layer agent response for end-to-end observability.

---

## 5. MCP Tool Inventory (v2.0.0 Scope)

### 5.1 Tool Naming Convention

`{layer_prefix}_{action}` where:

- `{layer_prefix}` = `brd` | `prd` | `ears` | `adr` | `sys` | `req` | `ctr`
- `{action}` = `validate` | `validate_fix` | `review` | `remediate` | `remediate_apply` | `status` | `artifacts`

### 5.2 Tool Matrix (Phase 1)

Layer tools remain the external MCP interface. Internally, the Orchestrator dispatches each call to the appropriate layer agent.

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

### 5.3 Orchestrator Tools

Two additional MCP tools are exposed by the Orchestrator for cross-layer workflows:

| Tool | Description |
| --- | --- |
| `ucx_orchestrate` | Run a cross-layer workflow for a project path (validate → review → remediate across selected layers) |
| `ucx_status` | Report stage completion across all active layer agents for a project path |

---

## 6. Archive Strategy

### 6.1 Archive Location

```text
/opt/data/docs_flow_framework/
├── UCX/               # v2.0.0 (new, MCP-first)
└── UCX_v1_archive/    # v1.x preserved (git mv)
```

### 6.2 What v1 Archive Contains

The entire UCX v1 codebase with all plans (PLAN-001 through PLAN-016), documentation, tests, validators, CLI code, and MCP prototype. It is read-only reference material.

### 6.3 Referencing v1

When porting validation logic from v1 to v2, reference the v1 archive:

```python
# Reference: UCX_v1_archive/ucx/validators/brd/quality_gate.py
```

Validators in v2 are rewrites, not copies. They must not import from `UCX_v1_archive/`.

---

## 7. v2 Plan Sequence

PLAN-001 is the baseline architecture plan. Follow-on v2 plans:

| Plan | Scope |
| --- | --- |
| PLAN-001 | UCX v2 architecture baseline — Orchestrator + per-layer agent model |
| PLAN-002 | UCX v2 Orchestrator + PRD agent (Phase 1): `AgentRequest/Response` contracts, `PrdAgent`, `ucx_orchestrate`, `ucx_status` |
| PLAN-003 | UCX v2 BRD agent (Phase 2): `BrdAgent` and `brd_*` tools wired through Orchestrator |
| PLAN-004 | UCX v2 EARS and ADR agents (Phase 3) |
| PLAN-005 | UCX v2 SYS, REQ, CTR agents (Phase 4) |
| PLAN-006 | UCX v2 agent contract hardening: observability, failure policy, retry semantics, `trace_id` threading |

---

## 8. Acceptance Criteria

- [x] `UCX_v1_archive/` exists and contains full v1 source under git tracking
- [x] `UCX/` contains v2 skeleton with `ucx/version.py` reporting `2.0.0`
- [x] `ucx/mcp/server.py` starts a FastMCP server without errors
- [x] All tool class stubs (`brd.py`, `prd.py`, etc.) are present with `raise NotImplementedError` bodies
- [x] `ucx/validators/result.py` defines `ValidationResult`, `Finding`, `Severity`
- [x] `ucx/validators/base.py` defines `Validator` Protocol
- [x] `pyproject.toml` has `version = "2.0.0"` and no `click` dependency
- [x] `docs/ROADMAP.md` reflects v2 plan sequence
- [x] No imports from `UCX_v1_archive/` in any v2 source file
