# CHANGELOG — UCX v1.18.0

**Release Date**: 2026-04-06
**Plan**: PLAN-027 Phase 2 (Default project resolution)

## Summary

Add session-level and config-level default project resolution to eliminate repeated `--project` arguments. Add `sdd_set_project` and `sdd_get_project` MCP tools. Migrate `executors.json` to object format with backward-compatible array shim. Add `SDD_DEFAULT_PROJECT` env var fallback for CLI.

## New

### Default Project Resolution

Resolution order: explicit `--project` argument > session override > `SDD_DEFAULT_PROJECT` env var > `executors.json` config default.

| MCP Tool | CLI Command | Purpose |
|----------|-------------|---------|
| `sdd_set_project` | (MCP only) | Set session default project. Pass empty string to clear. |
| `sdd_get_project` | `get-project` | Show resolved default project and source |

**New file**: `mcp_sdd/src/mcp_server/project_context.py`

### `_PROJECT_TOOLS` Injection

`handle_tool()` injects the resolved default project into `arguments["project"]` before `configure_logging` and dispatch. Only tools with `project` in their schema receive injection. Non-project tools are not affected.

### CLI `SDD_DEFAULT_PROJECT` Env Var

All CLI subcommands with `--project` now accept `SDD_DEFAULT_PROJECT` as a fallback. When set, `--project` becomes optional.

```bash
export SDD_DEFAULT_PROJECT=/opt/data/b-local/b-local-docs
mcp preflight --context any       # uses env var
mcp env-show                      # uses env var
mcp preflight --project /other    # explicit overrides
```

### `executors.json` Object Format

Config file accepts both formats:

```json
// New object format (with default_project)
{
    "default_project": "/opt/data/b-local/b-local-docs",
    "executors": [{"name": "claude", "executor_type": "cli", "command": "claude"}]
}

// Old array format (backward-compatible, no default_project)
[{"name": "claude", "executor_type": "cli", "command": "claude"}]
```

## Changed

### Tool Descriptions Updated

All 14 project-dependent tools now include "Resolved from session/config default when omitted." in the `project` property description. `project` remains in `required` arrays to prevent LLMs from silently dropping the field.

## Files Changed

| File | Change |
|------|--------|
| `mcp_sdd/src/mcp_server/project_context.py` | **New** — session state, config default, resolve chain |
| `mcp_sdd/src/mcp_server/tool_registry.py` | 2 tool defs, dispatch, `_PROJECT_TOOLS`, injection in `handle_tool`, descriptions |
| `mcp_sdd/src/mcp_server/executor/registry.py` | Config format migration with backward-compat shim |
| `mcp_sdd/src/mcp_server/cli/main.py` | Env var fallback for `--project`, `get-project` subcommand |
| `mcp_sdd/src/mcp_server/server.py` | Docstring tool count update |
| `mcp_sdd/tests/unit/test_project_context.py` | **New** — 12 tests |
| `mcp_sdd/tests/unit/test_tool_injection.py` | **New** — 5 tests |
| `mcp_sdd/tests/unit/test_server.py` | Tool count 23->25, 3 config format tests |

## Backward Compatibility

- `executors.json` old array format still works (no default_project)
- `--project` explicit argument always overrides any default
- `project` remains in `required` arrays — schema contract unchanged for LLMs
- All existing tests pass without modification

## Test Coverage

337 tests pass. New tests: 12 (project_context) + 5 (tool_injection) + 3 (config format) + tool count update.

## Token Efficiency

| Scenario (15 calls/session) | Before | After | Savings |
|------------------------------|--------|-------|---------|
| Config default set | ~750 tokens | 0 | ~750 |
| Session override | ~750 tokens | ~100 tokens | ~650 |
| No default configured | ~750 tokens | ~750 tokens | 0 |
