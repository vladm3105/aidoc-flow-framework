# docs_flow_framework Roadmap

| Field | Value |
| --- | --- |
| Current Version | 0.1.0 |
| Latest Release | 0.1.0 (MCP protocol transport layer for SDD lifecycle) |
| Next Minor | 0.2.0 (API executors via LiteLLM, MCP progress notifications) |
| Next Major | 1.0.0 (full multi-MCP ecosystem with governance and knowledge base) |
| Timezone | America/New_York |

---

## Version Timeline

```text
v0.1.0 (Current) ──► v0.2.0 ──► v1.0.0
  │                     │           │
  │                     │           └─► Multi-MCP ecosystem (governance + own KB)
  │                     └─► API executors via LiteLLM, MCP progress notifications
  └─► MCP transport layer: 19 tools, CLI executor registry, pipeline orchestration
```

---

## Planned Releases

### v0.1.0 - MCP Protocol Transport Layer

| Field | Value |
| --- | --- |
| Status | Implemented |
| Type | Minor |
| Release Date | 2026-03-28 |
| Scope | Expose SDD lifecycle as MCP tools with per-call executor selection |
| Plan | plans/PLAN-001_mcp_protocol_transport_layer.md |
| Changelog | changelog/CHANGELOG_v0.1.0.md |

Delivered scope:

- MCP server (`sdd-lifecycle`) exposing 19 tools over stdio transport
- Open executor registry: 5 CLI agents (claude, codex, gemini, opencode, copilot-cli) + 3 API stubs
- Executor type system: CLI (subprocess) and API (LiteLLM stub for v0.2.0)
- Deterministic tools (11): init, validate, consistency, preflight, prescreen, scan, scoring (show/validate/compare), list_executors, register_executor
- LLM-dependent tools (6): create_build, create, review, validate_fix, remediate, remediate_fix
- Orchestration tools (2): sdd_run_lifecycle (pipeline), sdd_next_action (advisor)
- Runtime-configurable executors: executors.json config file + sdd_register_executor tool
- Directory rename: mcp/ to mcp_sdd/
- Validated against b-local project: preflight, create, validate, next_action, run_lifecycle all passing

---

### v0.2.0 - API Executors and Progress Notifications

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | LiteLLM API executor implementation and MCP progress reporting |

Planned scope:

- Implement api_runner.py with litellm.acompletion() as universal gateway
- Support 100+ LLM providers: OpenAI, Anthropic, Google, Azure, Bedrock, Ollama, local models
- MCP progress notifications for long-running executor calls
- Configurable timeout per tool call

---

### v1.0.0 - Multi-MCP Ecosystem

| Field | Value |
| --- | --- |
| Status | Future |
| Type | Major |
| Scope | Full ecosystem with governance and knowledge base MCP servers |

Planned scope:

- MCP server: project-governance (GitHub Projects tasks, IPLANs, governance rules)
- MCP server: project-knowledge — own implementation using SQLite FTS5 + semantic search + frontmatter-aware indexing, built on existing `project_knowledge/mcp/server.py` foundation (concept inspired by markdown-vault-mcp, dependency rejected due to project maturity risk)
- Cross-server orchestration patterns
- Hard contract enforcement and quality gates

---

## Completed Releases

### v0.1.0 (2026-03-28)

MCP protocol transport layer. See changelog/CHANGELOG_v0.1.0.md for details.

---

## Constraints

- This roadmap covers the docs_flow_framework repository only
- Project-specific roadmaps (ibmcp, b_local, trading) live in their own repos
- Release sequencing can change based on implementation outcomes
