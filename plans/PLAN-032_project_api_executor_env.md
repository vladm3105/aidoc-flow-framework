# PLAN-032: Project-Specific API Executor Environment

**Status**: Done
**Target version**: 1.22.0

## Context

PLAN-031 delivered the LiteLLM-based API executor (`api_runner.py`). It resolves API keys from project `.env` via `project_env` dict. However, two gaps remain:

1. **Only `api_key` is extracted from project_env** — LiteLLM reads many settings from `os.environ` (e.g., `OPENAI_API_BASE`, `AZURE_API_VERSION`, `LITELLM_LOG`, `OPENAI_ORG_ID`). Project `.env` values stay in the dict and never reach LiteLLM's environment reader.

2. **No project-level executor config override** — `executors.json` is server-global. A project needing a custom model (`gpt-4o-mini`), api_base (Azure, proxy), or timeout cannot configure this without modifying the shared server config.

3. **Project env is loaded ad-hoc, only for executors** — `load_project_env` is called inside `_maybe_run_executor` only when an executor is specified. Deterministic tools, preflight, and prompt assembly have no access to project env. The `project_root` path is resolved independently 12+ times across `_dispatch` via `_path(arguments, "project")`.

The CLI executor (`cli_runner.py`) already handles env correctly: it merges `os.environ + config.env + project_env` into the subprocess environment (line 38-39). The API executor must reach parity, and the project environment should be centrally available.

## Goals

- Centralize project resolution and env loading into a `ProjectContext` resolved once per tool call
- Forward project `.env` vars to LiteLLM during API calls (temporary env injection, concurrency-safe)
- Support project-level executor config overrides via `{project}/UCX/executors.json`
- Add `UCX_EXECUTOR_*` env-var convention for project-wide executor defaults from `.env`
- Fix `system_prompt` passthrough from dispatcher to API executor
- Merge `config.env` into API executor env injection (parity with CLI runner)
- Extend `sdd_env_show` and `sdd_preflight` to report API executor readiness
- No change to existing env security model (BLOCKED_ENV_VARS, mtime cache, no value exposure)

## Non-Goals

- Custom LiteLLM proxy deployment
- Per-tool executor routing (use `--executor` argument already supported)
- Token counting or cost tracking (separate concern)
- Changing runner function signatures to accept `ProjectContext` (downstream runners keep receiving `project_root: Path`)

---

## Phase 0: Centralized `ProjectContext`

### Problem

`_dispatch` in `tool_registry.py` calls `_path(arguments, "project")` 12+ times independently. Each handler resolves project_root, then some load env, some load executor config, some do neither. This leads to:

- `project_env` only available inside `_maybe_run_executor` (executor-only)
- `project_executor_overrides` loaded per-executor-call (Phase 3), duplicated
- No single place to add project-wide settings (e.g., `UCX_STRICT_MODE`, `UCX_KEEP_VERSIONS`)
- Repeated `Path(project_arg).expanduser().resolve()` across handlers

### Solution

Introduce a lightweight `ProjectContext` dataclass resolved once at the top of `_dispatch`, available to all handlers.

### 0a. Add `ProjectContext` to existing `project_context.py`

**File**: `mcp_ucx/src/mcp_server/project_context.py`

Add `ProjectContext` to the existing module rather than creating a new file. `project_context.py` already owns project resolution (session/config defaults) — the per-call snapshot belongs in the same domain. This avoids a confusing split between `project_context.py` (resolution) and a separate `project_env.py` (snapshot).

Append after the existing `resolve_project` function:

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ProjectContext:
    """Immutable snapshot of project-specific configuration for a single tool call."""

    project_root: Path
    project_env: dict[str, str] = field(default_factory=dict)
    executor_overrides: dict = field(default_factory=dict)
    # executor_overrides typed as dict (not dict[str, ExecutorConfig]) to avoid
    # circular import — registry.py imports are deferred to resolve().

    @staticmethod
    def resolve(project_arg: str | None) -> ProjectContext | None:
        """Build context from a project argument. Returns None if no project.

        Handles both None and "" as no-project (returns None).
        """
        if not project_arg:
            return None
        project_root = Path(project_arg).expanduser().resolve()

        from mcp_server.env_manager import load_project_env
        from mcp_server.executor.registry import load_project_executor_config

        return ProjectContext(
            project_root=project_root,
            project_env=load_project_env(project_root),
            executor_overrides=load_project_executor_config(project_root),
        )
```

Key properties:
- **Frozen dataclass**: immutable after creation, safe for concurrent access
- **Lazy but cached**: `load_project_env` and `load_project_executor_config` both use mtime-based caching internally, so repeated calls for the same project are cheap
- **Optional**: `resolve()` returns `None` for tools that have no project argument, and for empty string (covers `sdd_set_project` clearing with `""`)
- **Deferred imports**: `load_project_env` and `load_project_executor_config` are imported inside `resolve()` to avoid circular imports and to allow Phase 3a to be implemented first
- **No signature changes to runners**: downstream runners still receive `project_root: Path`; the context just eliminates repeated resolution and makes env/overrides available at the handler level

### 0b. Integration in `_dispatch`

**File**: `mcp_ucx/src/mcp_server/tool_registry.py`

At the top of `_dispatch`, resolve context once:

```python
async def _dispatch(name: str, arguments: dict) -> dict:
    from mcp_server.project_context import ProjectContext
    ctx = ProjectContext.resolve(arguments.get("project"))

    # Handlers use ctx.project_root instead of _path(arguments, "project")
    # Handlers pass ctx to _maybe_run_executor for env/overrides
    ...
```

**Session management tools** (`sdd_set_project`, `sdd_get_project`) run before ctx is used and have their own early-return logic. `sdd_set_project` accepts `""` to clear the session — `ProjectContext.resolve("")` returns `None`, which is correct since these tools manage the resolution chain itself, not the resolved state.

```python
    # sdd_set_project: still uses arguments directly (manages resolution, not resolved state)
    if name == "sdd_set_project":
        project_val = arguments.get("project", "")
        if not project_val:
            clear_session_project()
            return {"cleared": True, "session_project": None}
        # Use _path here, not ctx — sdd_set_project validates the raw path
        project_root = _path(arguments, "project")
        return set_session_project(project_root)
```

**Lifecycle pipeline** (`sdd_run_lifecycle`) calls `_dispatch` recursively for each stage. Each sub-call re-resolves `ProjectContext` — this is intentional and correct because both `load_project_env` and `load_project_executor_config` use mtime-based caching, so repeated resolution for the same project is near-free.

Replace `_path(arguments, "project")` calls with `ctx.project_root` where a project argument exists. Handlers that don't need project (e.g., `sdd_consistency`, `sdd_validate_links`) continue using `_path(arguments, "target")` unchanged.

Example handler migration — `sdd_validate`:

```python
    # BEFORE:
    project_root = _path(arguments, "project")
    ...
    # project_env loaded separately inside _maybe_run_executor

    # AFTER:
    project_root = ctx.project_root
    ...
    # ctx passed to _maybe_run_executor for env/overrides
```

### 0c. Update `_maybe_run_executor` to accept `ProjectContext`

The final combined signature includes both `system_prompt` (Phase 1b) and `ctx` (this phase):

```python
async def _maybe_run_executor(
    arguments: dict,
    prompt_text: str,
    deterministic_result: dict,
    working_dir: Path | None = None,
    system_prompt: str | None = None,   # Added in Phase 1b
    ctx: ProjectContext | None = None,   # Added in Phase 0c — replaces internal env/override loading
) -> dict:
    executor_name = arguments.get("executor")
    if not executor_name:
        return {
            **deterministic_result,
            "prompt_text": prompt_text,
            "executor": None,
        }

    # Default working_dir to document folder
    if working_dir is None:
        doc_arg = arguments.get("document")
        if doc_arg:
            doc_path = Path(doc_arg).expanduser().resolve()
            working_dir = doc_path if doc_path.is_dir() else doc_path.parent

    # Use context instead of loading env/overrides independently
    project_env = ctx.project_env if ctx else None
    project_overrides = ctx.executor_overrides if ctx else None

    timeout = arguments.get("timeout", 300)
    exec_result = await run_executor(
        name=executor_name,
        prompt=prompt_text,
        working_dir=working_dir,
        timeout=timeout,
        project_env=project_env or None,
        system_prompt=system_prompt,
        project_overrides=project_overrides or None,
    )
    ...
```

This eliminates the duplicate `load_project_env` and `load_project_executor_config` calls that were previously inside `_maybe_run_executor`.

### 0d. Future extensibility

With `ProjectContext` in place, future features can add fields without touching handler signatures:

| Future Field | Use Case |
|---|---|
| `ucx_root: Path` | Cached UCX root resolution (currently re-resolved per loader call) |
| `strict_mode: bool` | Read from `UCX_STRICT_MODE` in `.env` |
| `keep_versions: int` | Read from `UCX_KEEP_VERSIONS` in `.env` for cleanup defaults |
| `log_level: str` | Per-project log verbosity |

These are **not in scope** for this plan — listed to show the extension points.

### 0e. Tests

- Test `ProjectContext.resolve(None)` returns `None`
- Test `ProjectContext.resolve("")` returns `None` (empty string = no project)
- Test `ProjectContext.resolve("/some/path")` returns context with resolved root, env, and overrides
- Test context is frozen (immutable after creation)
- Test context with missing `.env` has empty `project_env`
- Test context with missing `UCX/executors.json` has empty `executor_overrides`
- Test `_maybe_run_executor` uses `ctx.project_env` instead of calling `load_project_env`
- Test `_maybe_run_executor` uses `ctx.executor_overrides` instead of calling `load_project_executor_config`
- Test `sdd_set_project` with `""` still works (early return before ctx used)

### 0f. Migration scope

The following handlers in `_dispatch` will use `ctx.project_root` instead of `_path(arguments, "project")`:

| Handler | Currently | After |
|---------|-----------|-------|
| `sdd_init` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_validate` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_preflight` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_personas_show` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_personas_set` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_personas_diff` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_env_show` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_create_build` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_create` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_review` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_remediate` | `_path(arguments, "project")` | `ctx.project_root` |
| `sdd_set_project` | `_path(arguments, "project")` | `ctx.project_root` |

Handlers without a `project` argument are unchanged: `sdd_consistency`, `sdd_validate_links`, `sdd_prescreen`, `sdd_scan`, `sdd_score_*`, `sdd_next_action`, `sdd_clean`.

---

## Phase 1: Env Injection and Executor Fixes

### 1a. Concurrency-safe env injection — `api_runner.py`

**File**: `mcp_ucx/src/mcp_server/executor/api_runner.py`

The MCP server is async (single event loop). Multiple concurrent tool calls may `await acompletion` with different projects, causing env var interleaving. Use an `asyncio.Lock` to serialize the inject-call-restore cycle.

Additionally, merge `config.env` (from `ExecutorConfig.env` field set via `executors.json`) into the injection — the CLI runner already does this (line 38-39) but the API runner ignores it.

```python
import asyncio
import contextlib

_api_env_lock = asyncio.Lock()

@contextlib.contextmanager
def _inject_env(
    config_env: dict[str, str] | None,
    project_env: dict[str, str] | None,
):
    """Temporarily set config + project env vars in os.environ for LiteLLM.

    Merge order: os.environ (base) < config.env < project_env.
    Restores original values on exit. Respects BLOCKED_ENV_VARS.
    """
    merged = {**(config_env or {}), **(project_env or {})}
    if not merged:
        yield
        return

    from mcp_server.env_manager import BLOCKED_ENV_VARS
    saved: dict[str, str | None] = {}
    for key, val in merged.items():
        if key in BLOCKED_ENV_VARS:
            continue
        saved[key] = os.environ.get(key)  # None if absent
        os.environ[key] = val
    try:
        yield
    finally:
        for key, prev in saved.items():
            if prev is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prev
```

Wrap the acompletion call with lock + injection:

```python
    async with _api_env_lock:
        with _inject_env(config.env, project_env):
            try:
                response = await litellm.acompletion(**kwargs)
                ...
            except litellm.AuthenticationError as exc:
                ...
```

The lock ensures no two API calls interleave their env mutations. The `with` block inside the `async with` keeps the critical section minimal.

**Explicit kwargs vs. env-var boundary**: Values that `api_runner` already passes as explicit kwargs to `acompletion` (`api_key`, `api_base`, `model`, `timeout`) always take precedence over env vars — LiteLLM kwargs win over its own env reader. The env injection covers LiteLLM-native settings that have no kwarg equivalent (e.g., `AZURE_API_VERSION`, `LITELLM_LOG`, `OPENAI_ORG_ID`, `LITELLM_PROXY_BASE_URL`).

### 1b. Fix `system_prompt` passthrough — `dispatcher.py`

**File**: `mcp_ucx/src/mcp_server/executor/dispatcher.py`

`api_runner.run_api_executor` accepts `system_prompt` but the dispatcher never passes it. Add `system_prompt` to the dispatcher signature and forward it to the API runner. CLI executors receive the system prompt embedded in the prompt text (already handled), so no CLI change needed.

```python
async def run_executor(
    name: str,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int | None = None,
    project_env: dict[str, str] | None = None,
    system_prompt: str | None = None,  # NEW
) -> ExecutorResult:
    ...
    elif config.executor_type == ExecutorType.API:
        result = await run_api_executor(
            config=config,
            prompt=prompt,
            system_prompt=system_prompt,  # NEW
            timeout=timeout,
            project_env=project_env,
        )
```

`_maybe_run_executor` already receives `system_prompt` in its combined signature (see Phase 0c). It forwards the value to `run_executor` → `run_api_executor`.

Callers of `_maybe_run_executor` that produce a system prompt (review, remediate) should pass it through. Callers without a system prompt (create, validate) pass `None` (default).

### 1c. Tests

- Test that merged env (config.env + project_env) appears in `os.environ` during the call and is restored after
- Test merge order: project_env wins over config.env for same key
- Test that BLOCKED_ENV_VARS from both sources are excluded
- Test that pre-existing env vars are restored to original values
- Test that absent vars are cleaned up after the call
- Test concurrency: two concurrent calls with different project_env don't interleave (mock asyncio.Lock or verify sequential execution)
- Test system_prompt reaches acompletion messages list
- Test system_prompt=None omits system message

---

## Phase 2: `UCX_EXECUTOR_*` Env-Var Overrides

**File**: `mcp_ucx/src/mcp_server/executor/api_runner.py`

Allow project `.env` to set project-wide executor defaults. These are **not executor-specific** — they apply to whichever executor is selected for the call. For per-executor overrides, use `UCX/executors.json` (Phase 3).

| Env Var | Overrides | Example |
|---------|-----------|---------|
| `UCX_EXECUTOR_MODEL` | `config.model` | `gpt-4o-mini`, `claude-haiku-4-5-20251001` |
| `UCX_EXECUTOR_API_BASE` | `config.api_base` | `https://my-azure.openai.azure.com/` |
| `UCX_EXECUTOR_TIMEOUT` | `config.timeout` | `600` |
| `UCX_EXECUTOR_API_KEY_ENV` | `config.api_key_env` | `MY_CUSTOM_KEY` (redirects key lookup) |

**Design note**: These are project-wide defaults, not per-executor. A project typically uses one primary API executor. If a project needs different models for different executors, use `UCX/executors.json` (Phase 3) which supports per-name overrides. This keeps the `.env` interface simple.

### 2a. Resolution function

Insert in `api_runner.py`:

```python
def _resolve_overrides(
    config: ExecutorConfig,
    project_env: dict[str, str] | None,
) -> tuple[str, str, int, str]:
    """Return (model, api_base, timeout, api_key_env) with project overrides applied.

    Precedence: UCX_EXECUTOR_* env vars > config fields.
    """
    env = project_env or {}
    model = env.get("UCX_EXECUTOR_MODEL", "") or config.model
    api_base = env.get("UCX_EXECUTOR_API_BASE", "") or config.api_base

    # Validate api_key_env redirect against BLOCKED_ENV_VARS
    raw_key_env = env.get("UCX_EXECUTOR_API_KEY_ENV", "")
    if raw_key_env:
        from mcp_server.env_manager import BLOCKED_ENV_VARS
        if raw_key_env in BLOCKED_ENV_VARS:
            logger.warning(
                "UCX_EXECUTOR_API_KEY_ENV='%s' is a blocked system variable — ignoring",
                raw_key_env,
            )
            api_key_env = config.api_key_env
        else:
            api_key_env = raw_key_env
    else:
        api_key_env = config.api_key_env

    timeout_str = env.get("UCX_EXECUTOR_TIMEOUT", "")
    try:
        timeout = int(timeout_str) if timeout_str else config.timeout
    except ValueError:
        logger.warning("Invalid UCX_EXECUTOR_TIMEOUT='%s', using default %d", timeout_str, config.timeout)
        timeout = config.timeout

    return model, api_base, timeout, api_key_env
```

### 2b. Apply overrides in `run_api_executor`

Replace hardcoded `config.model`, `config.api_base`, `config.timeout`, `config.api_key_env` with resolved values from `_resolve_overrides`. The resolved values feed into the explicit kwargs passed to `acompletion`, which always win over env vars injected in Phase 1.

### 2c. Tests

- Test model override from project_env
- Test api_base override from project_env
- Test timeout override (valid int, invalid string falls back)
- Test api_key_env redirect to a custom var
- Test api_key_env redirect to a BLOCKED var is rejected (falls back to config)
- Test empty override values fall through to config defaults

---

## Phase 3: Project-Level `executors.json`

**File**: `mcp_ucx/src/mcp_server/executor/registry.py`

### 3a. Scoped project executor overlay

The global `_registry` must not be polluted by project-specific configs. Introduce a project-scoped overlay that is loaded per-call and discarded after.

```python
def load_project_executor_config(project_root: Path) -> dict[str, ExecutorConfig]:
    """Load project-specific executor overrides from {project}/UCX/executors.json.

    Returns a dict of executor configs (does NOT modify global registry).
    Returns empty dict if file missing or invalid.
    """
    project_config = project_root / "UCX" / "executors.json"
    if not project_config.is_file():
        return {}

    try:
        data = json.loads(project_config.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Invalid project executors.json at %s: %s", project_config, exc)
        return {}

    # Accept same formats as server config
    if isinstance(data, list):
        executors = data
    elif isinstance(data, dict):
        executors = data.get("executors", [])
    else:
        logger.warning(
            "Project executors.json at %s: expected object or array, got %s",
            project_config, type(data).__name__,
        )
        return {}

    if not isinstance(executors, list):
        logger.warning("Project executors.json at %s: 'executors' must be an array", project_config)
        return {}

    result: dict[str, ExecutorConfig] = {}
    for entry in executors:
        if not isinstance(entry, dict) or "name" not in entry:
            continue
        name = entry["name"]
        exec_type = ExecutorType(entry.get("executor_type", "cli"))
        result[name] = _build_config(name, entry, exec_type)
        logger.info("Loaded project executor override: %s (%s)", name, exec_type.value)
    return result
```

### 3b. Add `get_executor` with project overlay

```python
def get_executor(name: str, project_overrides: dict[str, ExecutorConfig] | None = None) -> ExecutorConfig:
    """Get executor config by name. Project overrides take precedence over global."""
    if project_overrides and name in project_overrides:
        return project_overrides[name]
    if name not in _registry:
        available = ", ".join(sorted(_registry.keys()))
        raise KeyError(f"Unknown executor '{name}'. Available: {available}")
    return _registry[name]
```

### 3c. Thread project overrides through dispatcher

**File**: `mcp_ucx/src/mcp_server/executor/dispatcher.py`

```python
async def run_executor(
    name: str,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int | None = None,
    project_env: dict[str, str] | None = None,
    system_prompt: str | None = None,
    project_overrides: dict[str, ExecutorConfig] | None = None,  # NEW
) -> ExecutorResult:
    config = get_executor(name, project_overrides=project_overrides)
    ...
```

**File**: `mcp_ucx/src/mcp_server/tool_registry.py` — `_maybe_run_executor` receives `ctx: ProjectContext | None` (Phase 0c) and extracts `ctx.executor_overrides` from there. No separate `load_project_executor_config` call needed — it was already loaded when `ProjectContext.resolve()` ran at the top of `_dispatch`.

This way project executor configs are loaded once per tool call via `ProjectContext`, never touch the global registry, and different projects in concurrent calls get their own overlays.

### 3d. Schema validation and error reporting

`load_project_executor_config` already handles:
- Missing file → empty dict (no-op)
- JSON parse errors → warning + empty dict
- Wrong top-level type → warning + empty dict
- Missing `name` in entries → skipped

Add preflight validation (Phase 4) to surface these warnings to the user.

### 3e. Scaffold support

**File**: `mcp_ucx/src/mcp_server/skills/scaffold.py`

Add `UCX/executors.json` as a documented optional path. Do NOT scaffold it by default (most projects don't need it). Do NOT add to `PROTECTED_PROJECT_FILES`. Add a comment in scaffold.py noting it as a recognized path:

```python
# Optional project files (not scaffolded, but recognized at runtime):
# - UCX/executors.json — project-specific executor config overrides
```

### 3f. Tests

- Test project overrides dict returned correctly from valid file
- Test project override takes precedence over global in get_executor
- Test global registry unchanged after loading project config
- Test missing file returns empty dict (no-op)
- Test malformed JSON returns empty dict with warning
- Test two different project roots return independent overrides

---

## Phase 4: Preflight and Env Show Enhancements

### 4a. `sdd_env_show` — API readiness section

**File**: `mcp_ucx/src/mcp_server/env_manager.py`

Add to `show_project_env` return dict:

```python
    # API executor readiness: check if expected API key vars are present
    api_key_vars = {"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY"}
    ucx_overrides = {k: "(set)" for k in safe_keys if k.startswith("UCX_EXECUTOR_")}
    api_keys_present = sorted(api_key_vars & set(safe_keys))

    return {
        ...existing fields...,
        "api_keys_present": api_keys_present,
        "ucx_executor_overrides": ucx_overrides,
    }
```

### 4b. CLI text formatter update

**File**: `mcp_ucx/src/mcp_server/cli/main.py`

Update the `env-show` text output handler to display the new fields:

```python
    if result.get("api_keys_present"):
        print(f"API keys present: {', '.join(result['api_keys_present'])}")
    if result.get("ucx_executor_overrides"):
        print(f"UCX executor overrides: {', '.join(result['ucx_executor_overrides'].keys())}")
```

### 4c. `sdd_preflight` — executor environment check

**File**: `mcp_ucx/src/mcp_server/preflight/runner.py`

Preflight already receives `project_root`. With Phase 0, the calling handler has `ctx` available and can pass `ctx.executor_overrides` to avoid redundant loading. But preflight also needs to validate the file independently (it's a diagnostic tool). Add after the existing env checks:

```python
    # API executor env readiness
    checks["api_keys_present"] = env_info.get("api_keys_present", [])
    checks["ucx_executor_overrides"] = env_info.get("ucx_executor_overrides", {})

    # Project executors.json validation
    project_executors_path = project_root / "UCX" / "executors.json"
    checks["project_executors_json"] = project_executors_path.is_file()
    if project_executors_path.is_file():
        from mcp_server.executor.registry import load_project_executor_config
        project_execs = load_project_executor_config(project_root)
        checks["project_executor_count"] = len(project_execs)
        if not project_execs:
            warnings.append("project_executors_json_invalid")
```

### 4d. `sdd_list_executors` — project overlay visibility

**File**: `mcp_ucx/src/mcp_server/tool_registry.py`

Currently `sdd_list_executors` has no `project` parameter and only shows global registry entries. Add optional `project` so agents can see effective executors including project overrides:

```python
    Tool(
        name="sdd_list_executors",
        ...
        inputSchema={
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Optional project root. When provided, includes project-specific executor overrides.",
                },
            },
            "required": [],
        },
    ),
```

Handler update:

```python
    if name == "sdd_list_executors":
        executors = list_executors()
        exec_list = [...]  # existing serialization

        # Merge project overrides if project provided
        if ctx and ctx.executor_overrides:
            project_names = set()
            for e in ctx.executor_overrides.values():
                project_names.add(e.name)
                exec_list.append({
                    "name": e.name,
                    ...
                    "source": "project",
                })
            # Mark global entries that are overridden
            for item in exec_list:
                if item.get("source") != "project" and item["name"] in project_names:
                    item["overridden_by_project"] = True

        return {"executors": exec_list}
```

Each entry gets a `"source": "global"` or `"source": "project"` field. Global entries overridden by project entries are flagged with `"overridden_by_project": true`.

### 4e. Tests

- Test env_show reports api_keys_present
- Test env_show reports UCX_EXECUTOR_* overrides
- Test env_show text format includes new fields
- Test preflight reports project_executors_json existence
- Test preflight warns on invalid project executors.json
- Test preflight reports project_executor_count
- Test list_executors without project returns global only (source: "global")
- Test list_executors with project includes project overrides (source: "project")
- Test list_executors flags overridden global entries

---

## Phase 5: Documentation Updates

### 5a. `mcp_ucx/docs/README.md`

Add to Section 3 (Skills and Project Isolation Model) under Environment Management:

**Project-Wide Executor Defaults** (via `.env`):

| Env Var | Purpose | Scope |
|---------|---------|-------|
| `UCX_EXECUTOR_MODEL` | Override executor model | Applies to selected executor |
| `UCX_EXECUTOR_API_BASE` | Override API endpoint URL | Applies to selected executor |
| `UCX_EXECUTOR_TIMEOUT` | Override timeout (seconds) | Applies to selected executor |
| `UCX_EXECUTOR_API_KEY_ENV` | Redirect API key lookup to a different env var | Validated against BLOCKED_ENV_VARS |

For per-executor overrides (different models for different executors), use `{project}/UCX/executors.json`.

Document `{project}/UCX/executors.json` as an optional override file with same format as server `executors.json`.

### 5b. `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`

Update executor integration section to document:

1. `ProjectContext` — resolved once per tool call, provides `project_root`, `project_env`, `executor_overrides` to all handlers

2. Env merge order for API executors:
   ```
   os.environ (base) < config.env (from executors.json) < project .env (temporary injection)
   ```

3. Explicit kwargs vs env boundary:
   ```
   Explicit kwargs to acompletion (always win): model, api_key, api_base, timeout
   Env injection (for LiteLLM-native settings): AZURE_API_VERSION, LITELLM_LOG, OPENAI_ORG_ID, etc.
   ```

4. Concurrency model: asyncio.Lock serializes env injection for API calls

### 5c. `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md`

Add troubleshooting section for API executor env issues:
- Missing API keys: check `sdd_env_show` for `api_keys_present`
- Wrong model: check `UCX_EXECUTOR_MODEL` in `.env` or `UCX/executors.json`
- Azure endpoints: set `AZURE_API_VERSION` and `UCX_EXECUTOR_API_BASE` in `.env`

### 5d. `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md`

Document `UCX_EXECUTOR_*` env vars in the environment section. Document `env-show` text output changes.

### 5e. Changelog

Create `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.22.0.md`.

---

## Precedence Summary

Final merge order for API executor settings (highest wins):

| Priority | Source | Scope | Mechanism |
|----------|--------|-------|-----------|
| 1 (lowest) | Builtin registry | Global | `BUILTIN_API_EXECUTORS["api/gpt-4o"]` |
| 2 | Server `executors.json` | Global | `load_config_file()` at startup |
| 3 | Project `UCX/executors.json` | Project | `load_project_executor_config()` per-call overlay |
| 4 | `UCX_EXECUTOR_*` in project `.env` | Project (all executors) | `_resolve_overrides()` in api_runner |
| 5 (highest) | `--executor` tool argument | Per-call | Selects executor by name |

**Explicit kwargs vs env injection boundary**:

| Passed as kwarg (always wins) | Left to LiteLLM env reader |
|-------------------------------|---------------------------|
| `model` | `AZURE_API_VERSION` |
| `api_key` | `LITELLM_LOG` |
| `api_base` | `OPENAI_ORG_ID` |
| `timeout` | `LITELLM_PROXY_BASE_URL` |
| | `AWS_REGION_NAME` |
| | Any other LiteLLM-native env var |

Values passed as explicit kwargs to `acompletion` always take precedence over env vars — even if the same env var is injected by Phase 1. This avoids dual-path ambiguity.

For API key resolution specifically:

| Priority | Source |
|----------|--------|
| 1 (lowest) | `os.environ` (direct) |
| 2 | Project `.env` key matching `config.api_key_env` |
| 3 (highest) | `UCX_EXECUTOR_API_KEY_ENV` redirect (looks up named var in project_env, then os.environ; rejects BLOCKED vars) |

---

## Implementation Order

Phases have dependencies that dictate execution order:

```
Phase 3a (load_project_executor_config function only)
  └─► Phase 0 (ProjectContext — imports load_project_executor_config)
        └─► Phase 1 (env injection, system_prompt, lock)
              └─► Phase 2 (UCX_EXECUTOR_* overrides)
                    └─► Phase 3b-f (get_executor overlay, dispatcher threading, scaffold, tests)
                          └─► Phase 4 (preflight, env_show, list_executors)
                                └─► Phase 5 (docs, changelog)
```

**Why this order**:
- Phase 0 imports `load_project_executor_config` → must exist first (Phase 3a)
- Phase 1 modifies `_maybe_run_executor` which Phase 0c also modifies → implement together
- Phase 2 (`_resolve_overrides`) is called inside the Phase 1 lock scope → Phase 1 must be in place
- Phase 3b-f threads overrides through dispatcher using `ctx` from Phase 0 → Phase 0 must be in place
- Phase 4 reports on state created by Phases 0-3 → all must be in place
- Phase 5 documents everything → last

---

## Concurrency Model

The MCP server runs on a single asyncio event loop. Multiple concurrent tool calls may await `acompletion` with different projects.

**Problem**: `os.environ` is process-global. Without protection, two concurrent API calls would interleave their env mutations.

**Solution**: `_api_env_lock = asyncio.Lock()` serializes the inject → call → restore cycle. This means API calls are sequential (not parallel), which is acceptable because:
- LiteLLM calls are I/O-bound (network wait), not CPU-bound
- The lock scope is minimal (only around `acompletion`, not prompt assembly)
- CLI executors are unaffected (they spawn subprocesses with their own env)
- True parallelism would require `os.environ` copy-on-write, which Python doesn't support

---

## Validation Checklist

- [ ] Phase 3a: `load_project_executor_config` exists and returns isolated dict
- [ ] Phase 0: `ProjectContext.resolve(None)` returns `None`
- [ ] Phase 0: `ProjectContext.resolve("")` returns `None`
- [ ] Phase 0: `ProjectContext.resolve(path)` loads env and executor overrides
- [ ] Phase 0: Context is frozen (immutable)
- [ ] Phase 0: `_dispatch` resolves context once; handlers use `ctx.project_root`
- [ ] Phase 0: `_maybe_run_executor` receives `ctx` and uses its env/overrides
- [ ] Phase 0: All 12 project-tool handlers migrated from `_path(arguments, "project")` to `ctx.project_root`
- [ ] Phase 0: `sdd_set_project` with `""` still works (early return before ctx)
- [ ] Phase 0: Lifecycle pipeline sub-calls re-resolve ctx (intentional, cached)
- [ ] Phase 1: `os.environ` temporarily includes config.env + project_env during acompletion; restored after
- [ ] Phase 1: BLOCKED_ENV_VARS are never injected (from either source)
- [ ] Phase 1: asyncio.Lock prevents concurrent env interleaving
- [ ] Phase 1: system_prompt flows from tool_registry → dispatcher → api_runner → acompletion messages
- [ ] Phase 2: `UCX_EXECUTOR_MODEL` overrides config.model
- [ ] Phase 2: Invalid `UCX_EXECUTOR_TIMEOUT` falls back to config default
- [ ] Phase 2: `UCX_EXECUTOR_API_KEY_ENV` pointing to a BLOCKED var is rejected
- [ ] Phase 3b-f: Project overlay takes precedence in `get_executor`
- [ ] Phase 3b-f: Malformed project executors.json returns empty dict with warning
- [ ] Phase 3b-f: Two different projects get independent overlays
- [ ] Phase 3b-f: Global registry unchanged after loading project config
- [ ] Phase 4: `sdd_env_show` reports api_keys_present and UCX overrides (JSON + text)
- [ ] Phase 4: `sdd_preflight` reports project_executors_json and warns on invalid
- [ ] Phase 4: `sdd_list_executors` with project shows overrides with source field
- [ ] Phase 5: All architecture docs updated (including ProjectContext in runtime arch)
- [ ] All existing tests still pass
- [ ] New tests for all phases
