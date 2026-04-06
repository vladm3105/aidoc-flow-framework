# CHANGELOG — UCX v1.17.0

**Release Date**: 2026-04-06
**Plan**: PLAN-027 (Project environment management)

## Summary

Auto-load project `.env` files for executor subprocesses with mtime-based caching, system variable blocklist, and secure inspection tools. Add `sdd_env_show` MCP tool and `env-show` CLI command. Enhance preflight to report env key inventory. Thread `project_env` through the executor dispatch chain.

## New

### Environment Manager Module

**New file**: `mcp_sdd/src/mcp_server/env_manager.py`

| Function | Purpose |
|----------|---------|
| `load_project_env(project_root)` | Load `.env` with mtime cache, blocklist, BOM handling |
| `show_project_env(project_root)` | Inspect `.env` keys without exposing values |
| `_invalidate_env_cache(project_root)` | Clear cache entry (testing) |

Uses `dotenv_values()` (never `load_dotenv()`) — does not mutate `os.environ`.

### `sdd_env_show` MCP Tool + `env-show` CLI Command

| MCP Tool | CLI Command | Purpose |
|----------|-------------|---------|
| `sdd_env_show` | `env-show` | Show .env keys, key count, blocked system vars |

CLI usage:

```bash
mcp env-show --project /path [--format text|json]
```

Returns `env_keys`, `env_key_count`, `blocked_vars`, `env_file_exists`. Values are never exposed.

### Security Protections

| Protection | Implementation |
|------------|---------------|
| System variable blocklist | `BLOCKED_ENV_VARS` frozenset: PATH, HOME, PYTHONPATH, LD_LIBRARY_PATH, LD_PRELOAD, SHELL, USER, IFS |
| None value filtering | Bare `KEY` lines (no `=value`) filtered before return |
| File permission warning | Warns if `.env` is group/world-readable (`mode & 0o077`) |
| UTF-8 BOM handling | Strips `\ufeff` prefix from first key |
| Parse error resilience | Malformed `.env` returns `{}` with logged warning |

### Dependency

`python-dotenv>=1.0.0` added to `pyproject.toml`.

## Changed

### Executor Env Merge Chain

**Files**: `executor/cli_runner.py`, `executor/dispatcher.py`

New `project_env: dict[str, str] | None = None` parameter added to `run_cli_executor()` and `run_executor()`. Merge order:

1. `os.environ` (base)
2. `config.env` (executor static config)
3. `project_env` (.env file — wins, except blocked vars)

All new parameters default to `None` — fully backward compatible.

### Tool Dispatch: Auto-Load Project Env

**File**: `tool_registry.py` — `_maybe_run_executor()`

When an executor is specified, loads `project_env` from the `--project` argument's `.env` file before spawning the subprocess.

### Enhanced Preflight `.env` Check

**File**: `preflight/runner.py`

| Check | Before | After |
|-------|--------|-------|
| `.env` detection | Existence only (`provider_token_present`) | Existence + key inventory |
| Key reporting | Not reported | `env_key_count`, `env_keys` (keys only) |
| Blocked vars | Not detected | `env_blocked_vars` list + warning |
| Parse errors | Not handled | `env_parse_error` warning |

## Files Changed

| File | Change |
|------|--------|
| `mcp_sdd/src/mcp_server/env_manager.py` | **New** — env loading, caching, security |
| `mcp_sdd/src/mcp_server/executor/cli_runner.py` | Add `project_env` param, update env merge |
| `mcp_sdd/src/mcp_server/executor/dispatcher.py` | Add `project_env` param, forward to CLI runner |
| `mcp_sdd/src/mcp_server/tool_registry.py` | `sdd_env_show` tool def + dispatch, env load in `_maybe_run_executor` |
| `mcp_sdd/src/mcp_server/preflight/runner.py` | Enhanced `.env` check with key inventory |
| `mcp_sdd/src/mcp_server/cli/main.py` | `env-show` subcommand |
| `mcp_sdd/pyproject.toml` | Add `python-dotenv>=1.0.0` |
| `mcp_sdd/tests/unit/test_env_manager.py` | **New** — 12 unit tests |
| `mcp_sdd/tests/integration/test_executor_env.py` | **New** — 3 integration tests |
| `mcp_sdd/tests/unit/test_server.py` | Tool count 22→23 |
| `mcp_sdd/tests/unit/test_preflight_runner.py` | +2 env check tests |

## Backward Compatibility

- All new parameters default to `None` — existing callers unaffected
- `executor/__init__.py` re-exports unchanged
- Missing `.env` returns empty dict — executor uses parent env as before
- Preflight `provider_token_present` check unchanged (existence-based)

## Test Coverage

314 tests pass. New tests: 12 (env_manager) + 3 (executor_env integration) + 2 (preflight env) + tool count update.
