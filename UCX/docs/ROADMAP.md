# UCX v2 Roadmap

## Version: 2.0.0 (Current — MCP-First Architecture)

UCX v2 is a clean-slate rewrite. The CLI-based v1 is archived in `UCX_v1_archive/`.

---

## Release Timeline

| Version | Status | Scope |
| --- | --- | --- |
| **2.0.0** | In Progress | MCP server skeleton, all layer tool stubs |
| 2.1.0 | Planned | BRD validator + `brd_*` tools implemented (PLAN-002) |
| 2.2.0 | Planned | PRD workflow + `prd_*` tools implemented (PLAN-003) |
| 2.3.0 | Planned | EARS tools implemented (PLAN-004) |
| 2.4.0 | Planned | ADR, SYS, REQ, CTR tools implemented (PLAN-005) |
| 2.5.0 | Planned | Agentic workflow engine hardening (PLAN-006) |
| 3.0.0 | Future | Multi-agent orchestration, parallel layer processing |

---

## v2.0.0 Scope (Current)

**Goal**: Working MCP server with all layer namespaces registered.
Tools raise `NotImplementedError` with PLAN references — server starts and lists tools.

**Deliverables**:

- `ucx/mcp/server.py` — FastMCP server entry
- `ucx/mcp/tools/` — 7 layer namespaces (brd, prd, ears, adr, sys, req, ctr)
- `ucx/validators/base.py` + `result.py` — validation contracts
- `ucx/agents/stages.py` + `workflow.py` — stage machine
- `ucx/models/document.py` — document layer registry
- `ucx/config/settings.py` — environment-based configuration

---

## Plan Index

| Plan | Scope | Status |
| --- | --- | --- |
| PLAN-001 | UCX v2 architecture baseline and MCP-first structure | Approved |
| PLAN-002 | BRD validator and `brd_*` MCP tools | Planned |
| PLAN-003 | PRD workflow and `prd_*` MCP tools | Planned |
| PLAN-004 | EARS validator and `ears_*` tools | Planned |
| PLAN-005 | ADR, SYS, REQ, CTR layers | Planned |
| PLAN-006 | Agentic workflow engine hardening | Planned |

---

## Design Principles

1. **MCP-first** — The MCP server is the only user-facing interface
2. **Layer isolation** — Each SDD layer has its own tool namespace
3. **Pure validators** — No side effects, no terminal output in validator logic
4. **Async-first** — All MCP tool methods are `async`
5. **Structured returns** — All tools return `dict` with `status`, `next_step`
6. **No global state** — Settings injected at construction, not module-level singletons

---

## Reference

- [v1 Archive](../../UCX_v1_archive/) — v1 source for porting validator logic
- [PLAN-001 Architecture](plans/PLAN-001_ucx_v2_mcp_first_architecture.md) — v2 baseline architecture plan
