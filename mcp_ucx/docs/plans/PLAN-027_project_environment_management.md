# Plan: Project Environment Management (PLAN-027)

## Context

mcp_ucx (UCX) works with multiple projects per session — each tool call specifies `--project`. Project `.env` files contain API keys and provider credentials needed by executors (claude, codex, etc.), but the server never loads them. Executors only get `os.environ` + static `config.env`. If the parent shell doesn't have the keys exported, executor calls fail silently.

This plan adds automatic `.env` loading with mtime-based caching, project switching, security protections, and secure inspection tools.

## Architecture

```
Tool Call (--project /path/A)
  → load_project_env(/path/A)  [cached by mtime]
  → _maybe_run_executor(project_env={KEY1: val1, ...})
  → run_executor(project_env=...)
  → run_cli_executor: env = os.environ + config.env + project_env
  → subprocess gets all vars

Next call (--project /path/B)
  → load_project_env(/path/B)  [different cache entry]
  → executor gets /path/B's env vars
```

Merge order: `os.environ` (base) < `config.env` (executor static) < `project_env` (.env file wins, except blocked vars)

## Implementation Steps

### Step 1: Add dependency + create `env_manager.py`

**`pyproject.toml`**: Add `"python-dotenv>=1.0.0"` to dependencies.

**`mcp_ucx/src/mcp_server/env_manager.py`** (new):

```python
load_project_env(project_root: Path) -> dict[str, str]
show_project_env(project_root: Path) -> dict[str, Any]
_invalidate_env_cache(project_root: Path) -> None
```

- Uses `dotenv_values(env_path, encoding="utf-8")` — parses `.env` without modifying `os.environ`
- Mtime-based cache keyed by `str(project_root)` (same pattern as `project_ucx_loader.py:162-178`)
- Missing `.env` returns `{}` (not an error)
- `show_project_env` returns keys only, never values
- Wraps `dotenv_values()` in try/except — malformed `.env` returns `{}` + logs warning

**Security protections** (from deep review):

A) **None value filtering**: `dotenv_values()` returns `OrderedDict[str, Optional[str]]`. Keys without values (bare `KEY` lines) return `None`. Filter before returning:
```python
env = {k: v for k, v in raw.items() if v is not None}
```

B) **System variable blocklist**: Prevent `.env` from overriding `PATH`, `HOME`, `PYTHONPATH`, `LD_LIBRARY_PATH`, `LD_PRELOAD`, `SHELL`, `USER`. Log warning when blocked vars are found:
```python
BLOCKED_ENV_VARS: frozenset[str] = frozenset({
    "PATH", "HOME", "PYTHONPATH", "LD_LIBRARY_PATH",
    "LD_PRELOAD", "SHELL", "USER", "IFS",
})
```

C) **File permission warning**: Warn (not error) if `.env` is group/world-readable (`mode & 0o077`).

D) **UTF-8 BOM handling**: Use `encoding="utf-8"` explicitly. Strip BOM prefix (`\ufeff`) from first key if present.

### Step 2: Thread `project_env` through executor chain

**`executor/cli_runner.py`** (line 22): Add `project_env: dict[str, str] | None = None` param. All new params have `None` default — backward compatible; `executor/__init__.py` re-exports are unaffected.

Replace env merge (lines 36-39):
```python
# Before:
env = None
if config.env:
    import os
    env = {**os.environ, **config.env}

# After:
import os
if config.env or project_env:
    env = {**os.environ, **(config.env or {}), **(project_env or {})}
else:
    env = None
```

**`executor/dispatcher.py`** (line 13): Add `project_env: dict[str, str] | None = None` param to `run_executor()`. Forward to `run_cli_executor()` at line 30. API runner (`run_api_executor`) is a stub — does not need `project_env` now but will when implemented (v0.2.0 — uses `config.api_key_env` to resolve keys from env).

### Step 3: Load env in tool dispatch + add `sdd_env_show`

**`tool_registry.py`**:

A) In `_maybe_run_executor()` (line 424): Load project env before the `run_executor()` call at line 451:
```python
from mcp_server.env_manager import load_project_env
project_env = None
project_arg = arguments.get("project")
if project_arg:
    project_env = load_project_env(Path(project_arg).expanduser().resolve()) or None
```
Pass `project_env=project_env` to `run_executor()` at line 451.

All 6 callers of `_maybe_run_executor` always pass `arguments` with `"project"` (verified: sdd_validate, sdd_create_build, sdd_create, sdd_review, sdd_remediate, sdd_remediate_fix).

B) Add `sdd_env_show` Tool definition **after `sdd_personas_diff` (line 151), before `sdd_prescreen` (line 152)**. `project` required.

C) Add `sdd_env_show` dispatch block **after `sdd_personas_diff` dispatch (line 755), before `sdd_prescreen` dispatch (line 757)**: call `show_project_env(project_root)`.

### Step 4: Enhance preflight `.env` check

**`preflight/runner.py`** (lines 200-203): Replace existence-only check with:
- Load env via `load_project_env()`
- Report `env_key_count` and `env_keys` (keys only) in checks
- Report `env_blocked_vars` if any system vars were in `.env`
- Wrap in try/except for graceful degradation

### Step 5: Add CLI `env-show` subcommand

**`cli/main.py`**:

Parser: Add `env-show --project PATH [--format text|json]` with `dest="output_format"` **after `personas-diff` parser (line 213), before `prescreen` parser (line 215)**.

Handler: Add dispatch block **after `personas-diff` handler (line 866), before `preflight` handler (line 868)**.

### Step 6: Tests

**`tests/unit/test_env_manager.py`** (new, ~12 tests):
- Load valid .env, missing .env, malformed .env
- Mtime cache hit/miss
- Multi-project isolation
- Show returns keys not values
- Cache invalidation
- None value filtering (bare keys)
- System variable blocklist (PATH, HOME blocked)
- File permission warning
- UTF-8 BOM handling

**`tests/unit/test_server.py`**: Update tool count 22→23.

**`tests/unit/test_preflight_runner.py`**: Add env_key_count check test.

**`tests/integration/test_executor_env.py`** (new, ~3 tests):
- Verify project_env threads through to `run_cli_executor`
- Verify project_env overrides config.env
- Verify missing project_env is backward compatible

### Step 7: Update documentation

**`mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.17.0.md`** (new):
- Summary: project environment management
- New: `sdd_env_show` tool, `env-show` CLI command, auto-loading in executors
- Changed: preflight enhanced .env check, executor env merge chain
- Security: system variable blocklist, file permission warning, None filtering

**`mcp_ucx/docs/README.md`**:
- Version 1.16.0 → 1.17.0
- Add env management section after Persona Management (Section 3)
- Add changelog link

**`mcp_ucx/docs/ROADMAP.md`**:
- Version 1.16.0 → 1.17.0
- Add v1.17.0 release section

**`mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md`**:
- Add `env-show` to commands table
- Add examples for `env-show`

**`mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md`**:
- Add env loading to init flow description
- Document merge order in executor flow

**`mcp_ucx/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`**:
- Add Section 4.4 (or similar) for project environment isolation model
- Document `.env` loading, caching, blocklist

## Implementation Order

1. `pyproject.toml` + `env_manager.py` + `test_env_manager.py`
2. `cli_runner.py` + `dispatcher.py` (thread project_env)
3. `tool_registry.py` (env loading + sdd_env_show)
4. `preflight/runner.py` (enhanced check)
5. `cli/main.py` (env-show subcommand)
6. `test_executor_env.py` (integration tests)
7. Run full test suite + CLI smoke tests
8. Documentation updates (changelog, readme, roadmap, architecture docs)

## Critical Files

| File | Action |
|------|--------|
| `mcp_ucx/pyproject.toml` | Edit — add python-dotenv |
| `mcp_ucx/src/mcp_server/env_manager.py` | **Create** |
| `mcp_ucx/src/mcp_server/executor/cli_runner.py` | Edit — add project_env param, fix merge (lines 36-39) |
| `mcp_ucx/src/mcp_server/executor/dispatcher.py` | Edit — add project_env param, forward (line 30) |
| `mcp_ucx/src/mcp_server/tool_registry.py` | Edit — env load in _maybe_run_executor (line 451), Tool def (line 152) + dispatch (line 756) |
| `mcp_ucx/src/mcp_server/preflight/runner.py` | Edit — enhanced .env check (lines 200-203) |
| `mcp_ucx/src/mcp_server/cli/main.py` | Edit — env-show subcommand |
| `mcp_ucx/tests/unit/test_env_manager.py` | **Create** — 12 tests |
| `mcp_ucx/tests/integration/test_executor_env.py` | **Create** — 3 tests |
| `mcp_ucx/tests/unit/test_server.py` | Edit — tool count 22→23 |
| `mcp_ucx/tests/unit/test_preflight_runner.py` | Edit — env check test |
| `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.17.0.md` | **Create** |
| `mcp_ucx/docs/README.md` | Edit — version bump, env section |
| `mcp_ucx/docs/ROADMAP.md` | Edit — version bump, v1.17.0 section |
| `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md` | Edit — env-show command |
| `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md` | Edit — env loading flow |
| `mcp_ucx/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md` | Edit — env isolation model |

## Verification

```bash
# Install new dependency
pip install python-dotenv>=1.0.0

# Unit tests
PYTHONPATH=mcp_ucx/src python -m pytest mcp_ucx/tests/ -x -q

# CLI smoke test
PYTHONPATH=mcp_ucx/src python -m mcp_server.cli.main env-show --project /opt/data/b-local/b-local-docs
PYTHONPATH=mcp_ucx/src python -m mcp_server.cli.main env-show --project /opt/data/b-local/b-local-docs --format json

# Preflight should now report env keys
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.preflight.runner import run_preflight
from pathlib import Path
r = run_preflight(project_root=Path('/opt/data/b-local/b-local-docs'), context='review')
print('env_key_count:', r.payload['checks'].get('env_key_count'))
print('env_keys:', r.payload['checks'].get('env_keys'))
"

# Security: verify blocklist works
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.env_manager import load_project_env
from pathlib import Path
import tempfile, os
d = tempfile.mkdtemp()
with open(os.path.join(d, '.env'), 'w') as f:
    f.write('PATH=/evil\nAPI_KEY=safe_value\n')
env = load_project_env(Path(d))
assert 'PATH' not in env, 'PATH should be blocked'
assert env.get('API_KEY') == 'safe_value'
print('Blocklist working correctly')
"
```

---

## Phase 2: Default Project Resolution

### Problem

14 of 25 MCP tools require `--project` on every call. In a typical session all calls target the same project, so the repeated argument wastes ~50 tokens per call (~750 tokens across a 15-call session). The LLM must also remember and reproduce the path each time.

### Resolution Strategy

Two layers that stack — config provides the persistent default, a session tool provides the override:

| Layer | Source | Persistence | Token cost |
| --- | --- | --- | --- |
| Config default | `SDD_DEFAULT_PROJECT` env var or `executors.json` field | Across sessions | 0 per call |
| Session override | `sdd_set_project` tool call | Current session only | ~100 tokens once |

Resolution order: `arguments["project"]` (explicit) > session override > config default > error.

### Architecture

```text
Tool call (--project omitted)
  → handle_tool()
  → _inject_default_project(name, arguments)
    → check arguments["project"] present?
    → NO → name in _PROJECT_TOOLS?
      → YES → resolve_project(None)
        → _session_project set? → use it
        → SDD_DEFAULT_PROJECT env var? → use it
        → _config_default_project set? → use it
        → raise ValueError
      → NO → skip injection
  → configure_logging(project_root)
  → _dispatch(name, arguments)
```

### Phase 2 Implementation Steps

#### Step 1: Add `project_context.py` module

**`mcp_ucx/src/mcp_server/project_context.py`** (new):

```python
_session_project: Path | None = None
_config_default_project: Path | None = None

def set_config_default(project_root: Path) -> None:
    """Called once at server startup from executors.json. Not user-facing."""

def set_session_project(project_root: Path) -> dict[str, Any]:
    """Set session-level default project. Returns confirmation.

    Pass empty string or None to clear session project.
    Validates path is a directory (does not require UCX/ — sdd_init creates that).
    """

def get_session_project() -> Path | None:
    """Return current session project or None."""

def clear_session_project() -> None:
    """Clear session project (revert to config default)."""

def resolve_project(explicit: str | None) -> Path:
    """Resolve project from explicit arg > session > config > error.

    Raises ValueError when no project can be resolved.
    Logs warning if resolved directory no longer exists.
    """
```

Resolution chain:

1. `explicit` argument (from tool call `arguments["project"]`)
2. `_session_project` (from `sdd_set_project`)
3. `os.environ.get("SDD_DEFAULT_PROJECT")`
4. `_config_default_project` (from `executors.json`)
5. Raise `ValueError("No project specified and no default configured")`

#### Step 2: Migrate `executors.json` to object format

**`executor/registry.py`**: `load_config_file()` currently expects a JSON array. Migrate to object format with backward-compat shim:

```python
def load_config_file(path: Path) -> int:
    """Load executors and optional default_project from config file."""
    if not path.is_file():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))

    # Backward-compat: plain array → treat as executors-only
    if isinstance(data, list):
        executors = data
        default_project = None
    elif isinstance(data, dict):
        executors = data.get("executors", [])
        default_project = data.get("default_project")
    else:
        logger.warning("executors.json: expected object or array, got %s", type(data).__name__)
        return 0

    if default_project:
        from mcp_server.project_context import set_config_default
        set_config_default(Path(default_project).expanduser().resolve())

    count = 0
    for entry in executors:
        if not isinstance(entry, dict) or "name" not in entry:
            continue
        name = entry["name"]
        exec_type = ExecutorType(entry.get("executor_type", "cli"))
        _registry[name] = _build_config(name, entry, exec_type)
        count += 1
    return count
```

New object format:

```json
{
    "default_project": "/opt/data/b-local/b-local-docs",
    "executors": [
        {"name": "claude", "executor_type": "cli", "command": "claude", "args": ["-p"]}
    ]
}
```

Old array format still works (treated as executors-only, no default project).

#### Step 3: Add `sdd_set_project` and `sdd_get_project` tools

**`tool_registry.py`**: Add two tools (25 total).

```python
Tool(
    name="sdd_set_project",
    description=(
        "Set default project for this session. "
        "Subsequent tool calls can omit project. "
        "Pass empty string to clear session default."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "project": {
                "type": "string",
                "description": "Project root path, or empty string to clear",
            },
        },
        "required": ["project"],
    },
),
Tool(
    name="sdd_get_project",
    description="Show current default project (session override, config default, or none).",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": [],
    },
),
```

Dispatch blocks:

```python
if name == "sdd_set_project":
    from mcp_server.project_context import set_session_project, clear_session_project
    project_val = arguments.get("project", "")
    if not project_val:
        clear_session_project()
        return {"cleared": True, "session_project": None}
    project_root = _path(arguments, "project")
    return set_session_project(project_root)

if name == "sdd_get_project":
    from mcp_server.project_context import get_session_project, resolve_project
    session = get_session_project()
    try:
        resolved = resolve_project(None)
        source = "session" if session else "config"
    except ValueError:
        resolved = None
        source = "none"
    return {
        "session_project": str(session) if session else None,
        "resolved_project": str(resolved) if resolved else None,
        "source": source,
    }
```

#### Step 4: Build `_PROJECT_TOOLS` set and inject resolved project

**`tool_registry.py`**: Build a frozenset of tool names that accept `project` at module load:

```python
_PROJECT_TOOLS: frozenset[str] = frozenset(
    tool.name
    for tool in TOOLS
    if "project" in (tool.inputSchema.get("properties") or {})
)
```

Rewrite `handle_tool()` to inject project **before** `configure_logging`:

```python
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    # Inject resolved project if not explicitly provided (before logging)
    if name in _PROJECT_TOOLS and not arguments.get("project"):
        from mcp_server.project_context import resolve_project
        try:
            resolved = resolve_project(None)
            arguments["project"] = str(resolved)
        except ValueError:
            pass  # Let individual tool handlers raise on missing project

    # Configure logging with project root (now available from injection)
    project_arg = arguments.get("project")
    if project_arg:
        configure_logging(Path(project_arg).expanduser().resolve())

    start = log_tool_call(
        tool=name,
        arguments=arguments,
        project_root=Path(project_arg) if project_arg else None,
    )
    # ... rest unchanged
```

This addresses three review findings:

- **#2**: Only injects for tools that have `project` in schema (no pollution of non-project tools)
- **#3**: Injection runs before `configure_logging` (logging uses resolved project)
- **#8**: `_maybe_run_executor` reads from the same `arguments` dict (already injected)

#### Step 5: Keep `project` required in tool schemas — update descriptions

Do **not** remove `"project"` from `"required"` arrays. Instead, update the description for all 14 project-dependent tools:

```python
"project": {
    "type": "string",
    "description": "Project root path. Resolved from session/config default when omitted.",
},
```

The `"required"` array still lists `"project"` — this prevents LLMs from silently dropping the field when no default is configured. The server-side injection handles the case where the LLM omits it despite the schema.

MCP protocol note: MCP servers may receive calls with missing required fields. The injection in `handle_tool` fills the gap before dispatch. If injection fails (no default configured), the tool handler's `_path(arguments, "project")` raises `KeyError` which surfaces as an error response.

#### Step 6: CLI `--project` env var fallback

**`cli/main.py`**: No `set-project`/`get-project` CLI subcommands (CLI is stateless per invocation).

Instead, make `--project` fall back to `SDD_DEFAULT_PROJECT` env var. For each subparser that has `--project`:

```python
_default_project = os.environ.get("SDD_DEFAULT_PROJECT")

init_parser.add_argument(
    "--project",
    required=_default_project is None,
    default=_default_project,
    help="Project root (default: $SDD_DEFAULT_PROJECT)" if _default_project else "Project root",
)
```

This makes `--project` optional when the env var is set, required otherwise. No session state in CLI.

Add a `get-project` subcommand (read-only, for diagnostics):

```python
get_project_parser = subparsers.add_parser(
    "get-project",
    help="Show resolved default project from environment",
)
```

Handler:

```python
if args.command == "get-project":
    default = os.environ.get("SDD_DEFAULT_PROJECT")
    if default:
        print(f"SDD_DEFAULT_PROJECT={default}")
    else:
        print("No default project configured. Set SDD_DEFAULT_PROJECT or pass --project.")
    return 0
```

#### Step 7: Tests

**`tests/unit/test_project_context.py`** (new, ~12 tests):

- `resolve_project` with explicit arg returns it
- `resolve_project` with session override returns it
- `resolve_project` with `SDD_DEFAULT_PROJECT` env var returns it
- `resolve_project` with config default returns it
- `resolve_project` with nothing raises `ValueError`
- Precedence: explicit > session > env var > config
- `set_session_project` validates path is a directory
- `set_session_project` rejects file path
- `set_session_project` does not require UCX/ subdirectory
- `clear_session_project` reverts to config
- `set_session_project("")` clears session
- `get_session_project` returns None when not set
- Stale directory warning in `resolve_project`

**`tests/unit/test_server.py`**: Update tool count 23→25.

**`tests/unit/test_executor_registry.py`** (or existing test file):

- `load_config_file` with old array format still works
- `load_config_file` with new object format loads `default_project`
- `load_config_file` with new object format loads executors from `"executors"` key

**`tests/unit/test_tool_injection.py`** (new, ~5 tests):

- `handle_tool` injects project for project-dependent tool when omitted
- `handle_tool` does not inject project for non-project tool
- `handle_tool` does not override explicit project argument
- `configure_logging` receives injected project
- `_PROJECT_TOOLS` set matches expected tools

### Phase 2 Implementation Order

1. `project_context.py` + `test_project_context.py`
2. `executor/registry.py` — config format migration + backward-compat shim + tests
3. `tool_registry.py` — `_PROJECT_TOOLS`, injection in `handle_tool`, 2 tool defs + dispatch, update descriptions
4. `cli/main.py` — env var fallback for `--project`, `get-project` subcommand
5. `server.py` — update docstring tool count
6. `test_tool_injection.py`, `test_server.py` tool count update
7. Run full test suite + CLI smoke tests
8. Documentation updates: changelog, README, roadmap, CLI reference, operational flows, UCF doc

### Token Efficiency Analysis

| Scenario | Before (15 calls) | After (15 calls) | Savings |
| --- | --- | --- | --- |
| Config default set | 15 x ~50 = ~750 tokens | 0 | ~750 tokens |
| Session override | 15 x ~50 = ~750 tokens | 1 x ~100 = ~100 tokens | ~650 tokens |
| Mixed (switch mid-session) | 15 x ~50 = ~750 tokens | 2 x ~100 = ~200 tokens | ~550 tokens |
| No default configured | 15 x ~50 = ~750 tokens | 15 x ~50 = ~750 tokens | 0 (no change) |

### Phase 2 Critical Files

| File | Action |
| --- | --- |
| `mcp_ucx/src/mcp_server/project_context.py` | **Create** — session state, config default, resolve chain |
| `mcp_ucx/src/mcp_server/tool_registry.py` | Edit — `_PROJECT_TOOLS`, injection, 2 tool defs + dispatch, descriptions |
| `mcp_ucx/src/mcp_server/executor/registry.py` | Edit — config format migration with backward-compat shim |
| `mcp_ucx/src/mcp_server/cli/main.py` | Edit — env var fallback for `--project`, `get-project` subcommand |
| `mcp_ucx/src/mcp_server/server.py` | Edit — update docstring tool count |
| `mcp_ucx/tests/unit/test_project_context.py` | **Create** — ~12 tests |
| `mcp_ucx/tests/unit/test_tool_injection.py` | **Create** — ~5 tests |
| `mcp_ucx/tests/unit/test_server.py` | Edit — tool count 23→25 |

### Phase 2 Verification

```bash
# Config default via env var
SDD_DEFAULT_PROJECT=/opt/data/b-local/b-local-docs \
  PYTHONPATH=mcp_ucx/src python -m mcp_server.cli.main preflight --context any

# CLI get-project
SDD_DEFAULT_PROJECT=/opt/data/b-local/b-local-docs \
  PYTHONPATH=mcp_ucx/src python -m mcp_server.cli.main get-project

# Explicit still overrides
PYTHONPATH=mcp_ucx/src python -m mcp_server.cli.main preflight \
  --project /opt/data/trading --context any

# Config file object format
echo '{"default_project": "/opt/data/b-local/b-local-docs", "executors": []}' > /tmp/test_exec.json
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.executor.registry import load_config_file
from mcp_server.project_context import resolve_project
from pathlib import Path
load_config_file(Path('/tmp/test_exec.json'))
print('Resolved:', resolve_project(None))
"

# Backward compat: old array format
echo '[{"name":"echo","executor_type":"cli","command":"echo"}]' > /tmp/test_old.json
PYTHONPATH=mcp_ucx/src python -c "
from mcp_server.executor.registry import load_config_file
from pathlib import Path
n = load_config_file(Path('/tmp/test_old.json'))
print(f'Loaded {n} executor(s) from old array format')
"
```

### Design Decisions (Phase 2)

- **Session state is module-level variable**: No persistence needed — MCP server process = one session. Process restart clears it.
- **`resolve_project` raises `ValueError`**: Callers must handle missing project explicitly. Silent `None` would cause confusing errors downstream.
- **Injection in `handle_tool` before `configure_logging`**: Resolved project available to logging and all dispatch logic. Individual handlers remain unchanged.
- **`_PROJECT_TOOLS` frozenset guards injection**: Only tools with `project` in schema receive injection. Non-project tools (`sdd_scan`, `sdd_consistency`) are not polluted.
- **CLI uses env var, not session tools**: CLI is stateless between invocations. `SDD_DEFAULT_PROJECT` env var is the CLI-side default mechanism.
- **`project` stays in `required` arrays**: Prevents LLMs from silently dropping the field. Server-side injection fills the gap when default is configured.
- **Config format migration with shim**: `executors.json` accepts both old array format and new object format. Plain array = executors-only. Object = executors + `default_project`.
- **`set_session_project("")` clears**: No separate `sdd_clear_project` tool. Empty string convention documented.
- **`set_session_project` validates directory exists, not UCX/**: User may call `sdd_set_project` before `sdd_init`. UCX subdirectory created later by `sdd_init`.
- **`_dispatch` is private**: Pipeline calls `_dispatch` directly but receives the already-injected `arguments` dict from `handle_tool`. No separate injection needed.

---

## Design Decisions (Phase 1)

- **`dotenv_values()` not `load_dotenv()`**: Never mutates `os.environ` — safe for multi-project
- **Values never exposed**: `show_project_env` and preflight report keys only
- **No `sdd_env_set`**: Out of scope — MCP server is read-only for project config
- **Missing `.env` is not an error**: Returns empty dict, executor uses parent env
- **All new params default to `None`**: Fully backward compatible
- **CLI `env-show` uses `dest="output_format"`**: Matches `personas-show`/`personas-diff` pattern
- **Only `.env` loaded**: Multi-file support (`.env.local`, `.env.production`) deferred to v0.2.0
- **System var blocklist is a frozenset**: Extensible, same pattern as `PROTECTED_PROJECT_FILES` in scaffold.py

## Deep Review Findings (Phase 1)

| # | Finding | Severity | Resolution |
| --- | --- | --- | --- |
| 1 | All 6 `_maybe_run_executor` callers pass `"project"` in arguments | None | Safe — no race condition |
| 2 | No non-executor tool needs env vars | None | Correct — deterministic tools are pure functions |
| 3 | `dotenv_values()` returns `Optional[str]` — None values cause TypeError in env merge | **Critical** | Filter None values before returning |
| 4 | No file permission check for world-readable `.env` | Medium | Warn on insecure permissions (mode & 0o077) |
| 5 | No blocklist — `.env` with `PATH=/evil` poisons executor | **Critical** | `BLOCKED_ENV_VARS` frozenset with PATH, HOME, PYTHONPATH, etc. |
| 6 | No integration test for full tool→executor→subprocess chain | Medium | Add `test_executor_env.py` with 3 integration tests |
| 7 | UTF-8 BOM corrupts first key name | Medium | Explicit `encoding="utf-8"`, strip BOM from first key |
| 8 | Only `.env` supported, not `.env.local` etc. | Low | Document as v0.1.0 limitation |
| 9 | `show_project_env` triggers same log as real env load | Low | Use different log messages for load vs inspect |
