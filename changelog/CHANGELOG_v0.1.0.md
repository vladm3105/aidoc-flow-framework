# CHANGELOG v0.1.0

**Release Date**: 2026-03-28
**Type**: Minor (MCP Protocol Transport Layer)

## Summary

First release of the `sdd-lifecycle` MCP server exposing the SDD document lifecycle as 19 native MCP tools over stdio transport. Introduces open executor registry supporting per-call selection of CLI AI agents and API LLM providers.

## Changes

### Directory Rename

- Renamed `mcp/` to `mcp_ucx/` to avoid confusion with MCP protocol
- Updated all internal documentation path references (38 files)
- Python package name `mcp_server` unchanged — zero import changes

### MCP Server (`mcp_ucx/src/mcp_server/server.py`)

- Thin entry point using `mcp.server.Server` + `stdio_server` over stdio transport
- Server name: `sdd-lifecycle`
- Loads optional `executors.json` at startup for pre-configured executors

### Executor Package (`mcp_ucx/src/mcp_server/executor/`)

- `registry.py`: Open executor registry with `ExecutorConfig` dataclass, `ExecutorType` enum (CLI/API), 5 built-in CLI executors (claude, codex, gemini, opencode, copilot-cli), 3 API stubs (api/gpt-4o, api/claude-sonnet, api/gemini-pro)
- `cli_runner.py`: Async subprocess runner with file-based prompt delivery for large prompts, timeout handling, not-installed detection
- `api_runner.py`: Stub for LiteLLM API gateway (raises NotImplementedError, planned for v0.2.0)
- `dispatcher.py`: Routes executor calls by type (CLI or API)

### Tool Registry (`mcp_ucx/src/mcp_server/tool_registry.py`)

19 MCP tools in three tiers:

**Deterministic tools (11)**: `sdd_init`, `sdd_validate`, `sdd_consistency`, `sdd_preflight`, `sdd_prescreen`, `sdd_scan`, `sdd_score_show`, `sdd_score_validate`, `sdd_score_compare`, `sdd_list_executors`, `sdd_register_executor`

**Orchestration tools (2)**: `sdd_run_lifecycle` (multi-stage pipeline), `sdd_next_action` (lifecycle advisor)

**LLM-dependent tools (6)**: `sdd_create_build`, `sdd_create`, `sdd_review`, `sdd_validate_fix`, `sdd_remediate`, `sdd_remediate_fix`

### Packaging

- `mcp_ucx/pyproject.toml`: Package `mcp-sdd-server` v0.1.0 with `mcp-sdd` console script
- `.mcp.json`: MCP server registration for Claude Code auto-discovery

### Roadmap and Changelog

- `roadmap/ROADMAP.md`: Initial roadmap with v0.1.0, v0.2.0, v1.0.0 milestones
- `changelog/CHANGELOG_v0.1.0.md`: This file

### Plan

- `plans/PLAN-001_mcp_protocol_transport_layer.md`: Full implementation plan with gap analysis

## Backward Compatibility

Fully backward compatible:

- Existing CLI (`mcp_ucx/src/mcp_server/cli/main.py`) unchanged
- Existing tests unchanged (169 passed, 1 pre-existing integration failure)
- No existing files modified — all changes are new files

## Validation Evidence

- New MCP server tests: 33 passed (mcp_ucx/tests/unit/test_server.py)
- Full test suite: 169 passed, 1 pre-existing failure (test_validate_to_fix_to_remediate_flow)
- MCP server initialization: responds to JSON-RPC initialize with protocol version 2024-11-05
- Tool count verified: 19 tools registered
- Executor count verified: 8 executors registered (5 CLI active, 3 API stub)

### End-to-End Validation (b-local project)

Tested against `/opt/data/b-local/b-local-docs` (74 existing BRDs):

| Tool | Test | Result |
|------|------|--------|
| `sdd_preflight` | Environment readiness | status=ready, all checks passed |
| `sdd_create` | BRD-75 from MVP template | Template artifact created (39KB) + creation prompt (114KB) |
| `sdd_validate` | Structural validation | Passed: 0 errors, 0 warnings |
| `sdd_next_action` | Lifecycle stage advisor | Correctly identified stage=validated, next=validate_fix |
| `sdd_list_executors` | Registry query | 8 executors (5 CLI, 3 API stub) |
| `sdd_run_lifecycle` | Pipeline: validate + validate_fix | Both stages completed, source protection confirmed |
