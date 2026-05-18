# PLAN-001: MCP Protocol Transport Layer for SDD CLI

| Field | Value |
| --- | --- |
| Status | Implemented |
| Commit | 4ecd8bc |
| Release | v0.1.0 (2026-03-28) |
| Type | Feature — New MCP Server |
| Priority | High |
| Date | 2026-03-28 |
| Scope | Add MCP protocol transport to existing SDD CLI runtime |
| Server Name | sdd-lifecycle |

---

## 1. Context

The SDD framework at `mcp/src/mcp_server/` has 15 runner functions exposed via an argparse CLI. To enable multi-agent orchestration (Claude, Codex, Gemini, OpenCode, Copilot CLI), we need to expose these as native MCP tools over stdio transport. The key innovation is **per-call executor selection** — each LLM-dependent tool accepts an `executor` parameter so the orchestrator can mix agents across the lifecycle (e.g., Claude for creation, Codex for fixing).

### 1.1 Directory Rename (Pre-Implementation Step)

Rename `mcp/` → `mcp_ucx/` to avoid confusion with the MCP protocol itself and other MCP servers in the project.

```bash
git mv mcp mcp_ucx
```

**Scope of rename**:
- All source paths: `mcp_ucx/src/mcp_server/` (internal package name `mcp_server` stays unchanged)
- All test paths: `mcp_ucx/tests/`
- All doc paths: `mcp_ucx/docs/`
- Templates and skills: `mcp_ucx/templates/`, `mcp_ucx/skills/`, `mcp_ucx/prompts/`
- Packaging: `mcp_ucx/pyproject.toml`
- MCP registration `cwd`: updated to `/opt/data/ucx_framework/mcp_ucx/src`

**What does NOT change**:
- Python package name remains `mcp_server` (internal imports unchanged)
- Tool names remain `sdd_*` prefix
- Server name remains `sdd-lifecycle`

All paths in sections below use the new `mcp_ucx/` root.

---

## 2. Multi-MCP Ecosystem

This server (`sdd-lifecycle`) is one of several planned MCP servers that an orchestrator composes:

```
AI Agent (Orchestrator)
  │
  ├── MCP 1: sdd-lifecycle      ← THIS PLAN — document create/validate/review/remediate
  ├── MCP 2: project-governance  (future) — GitHub Projects tasks, IPLANs, governance rules
  ├── MCP 3: project-knowledge   (future) — RAG/graph KB for docs, templates, source refs
  └── MCP N: additional servers as needed
```

**Boundary rule**: Each MCP server is independently usable. No cross-server tool dependencies. The orchestrator composes them — e.g., query KB for context, create document, create governance task.

**Interaction patterns** (orchestrator-level, not built into this server):
- `project-knowledge` → `sdd-lifecycle`: KB provides templates/context, sdd-lifecycle creates docs
- `sdd-lifecycle` → `project-governance`: After review passes, governance creates tracking tasks
- `project-knowledge` → `project-governance`: KB indexes governance artifacts for search

---

## 3. Architecture (This Server)

```
AI Agent (Orchestrator)
  │  MCP Protocol (JSON-RPC / stdio)
  ▼
MCP Server: sdd-lifecycle (mcp_ucx/src/mcp_server/server.py)
  ├── Deterministic tools → execute runner functions directly
  └── LLM-dependent tools → spawn CLI AI Agent (executor) as subprocess
                              └── claude / codex / gemini / opencode / copilot-cli
```

---

## 4. Files to Create (9 new files, 0 existing files modified)

### 4.1 `mcp_ucx/src/mcp_server/executor/__init__.py`
Empty package init.

### 4.2 `mcp_ucx/src/mcp_server/executor/registry.py` (~120 lines)
Open executor registry — ships with built-in executors, accepts new ones at runtime via MCP tool call or config file.

**Design principle**: The `executor` parameter on LLM-dependent tools is a free-form string, not a hardcoded enum. Any registered executor name is valid. New CLI AI agents can be added without code changes.

**Built-in executors** (shipped with the server):

```python
BUILTIN_EXECUTORS = {
    "claude": {"command": "claude", "args": ["-p", "--output-format", "json", "--verbose"], "prompt_mode": "file"},
    "codex": {"command": "codex", "args": ["exec"], "prompt_mode": "positional"},
    "gemini": {"command": "gemini", "args": [], "prompt_mode": "positional"},
    "opencode": {"command": "opencode", "args": ["run"], "prompt_mode": "positional"},
    "copilot-cli": {"command": "gh", "args": ["copilot"], "prompt_mode": "positional", "status": "experimental"},
}
```

**Executor type system** — two executor types sharing a common interface:

```python
class ExecutorType(str, Enum):
    CLI = "cli"    # subprocess-based CLI AI agents
    API = "api"    # LLM API calls via LiteLLM or direct SDK

@dataclass
class ExecutorConfig:
    name: str               # unique identifier (e.g., "claude", "aider", "litellm/gpt-4o")
    executor_type: ExecutorType  # cli or api
    # CLI fields
    command: str = ""       # binary name or path (e.g., "claude", "/usr/local/bin/aider")
    args: list[str] = field(default_factory=list)  # base arguments before prompt
    prompt_mode: str = ""   # "file" (stdin pipe) | "positional" (append as last arg)
    # API fields
    model: str = ""         # LiteLLM model string (e.g., "gpt-4o", "claude-sonnet-4-20250514", "gemini/gemini-2.5-pro")
    api_base: str = ""      # optional custom API base URL
    api_key_env: str = ""   # env var name holding the API key (e.g., "OPENAI_API_KEY")
    # Common fields
    status: str = "active"  # "active" | "experimental" | "stub"
    timeout: int = 300      # default timeout in seconds
    env: dict[str, str] | None = None  # additional environment variables
```

**API executor architecture** (stub for v0.1.0, implementation in future version):

```python
# executor/api_runner.py — stub

async def run_api_executor(
    config: ExecutorConfig,
    prompt: str,
    system_prompt: str | None = None,
    timeout: int = 300,
) -> ExecutorResult:
    """Execute prompt via LLM API. Requires litellm package.

    Uses LiteLLM as a universal gateway supporting 100+ LLM providers:
    OpenAI, Anthropic, Google, Azure, Bedrock, Ollama, local models, etc.

    Not implemented in v0.1.0. Returns stub response.
    """
    raise NotImplementedError(
        f"API executor '{config.name}' requires litellm. "
        "Install with: pip install litellm. "
        "Implementation planned for v0.2.0."
    )
```

**Built-in API executor stubs** (registered but raise NotImplementedError until v0.2.0):

```python
API_EXECUTOR_STUBS = {
    "api/gpt-4o": {"model": "gpt-4o", "api_key_env": "OPENAI_API_KEY"},
    "api/claude-sonnet": {"model": "claude-sonnet-4-20250514", "api_key_env": "ANTHROPIC_API_KEY"},
    "api/gemini-pro": {"model": "gemini/gemini-2.5-pro", "api_key_env": "GEMINI_API_KEY"},
}
```

The `executor/runner.py` dispatcher routes by `executor_type`:

```python
async def run_executor(name: str, prompt: str, ...) -> ExecutorResult:
    config = get_executor(name)
    if config.executor_type == ExecutorType.CLI:
        return await run_cli_executor(config, prompt, ...)
    elif config.executor_type == ExecutorType.API:
        return await run_api_executor(config, prompt, ...)
```

**Registry API**:

- `get_executor(name: str) -> ExecutorConfig` — raises KeyError if not registered
- `list_executors() -> list[ExecutorConfig]` — all registered executors with status
- `register_executor(config: ExecutorConfig) -> None` — add or replace an executor at runtime
- `remove_executor(name: str) -> None` — unregister an executor

**MCP tools for executor management**:

- `sdd_list_executors` — returns all registered executors with type, status, and capabilities
- `sdd_register_executor` — registers a new CLI or API executor at runtime:

  CLI example:

  ```json
  {
    "name": "aider",
    "executor_type": "cli",
    "command": "aider",
    "args": ["--message"],
    "prompt_mode": "positional"
  }
  ```

  API example:

  ```json
  {
    "name": "api/mistral-large",
    "executor_type": "api",
    "model": "mistral/mistral-large-latest",
    "api_key_env": "MISTRAL_API_KEY"
  }
  ```

**Optional config file** (`mcp_ucx/executors.json`): Loaded at server startup. Supports both CLI and API executors:

```json
[
    {"name": "aider", "executor_type": "cli", "command": "aider", "args": ["--message"], "prompt_mode": "positional"},
    {"name": "cline", "executor_type": "cli", "command": "cline", "args": ["--prompt"], "prompt_mode": "positional"},
    {"name": "api/deepseek", "executor_type": "api", "model": "deepseek/deepseek-chat", "api_key_env": "DEEPSEEK_API_KEY"},
    {"name": "api/ollama-llama", "executor_type": "api", "model": "ollama/llama3", "api_base": "http://localhost:11434"}
]
```

**Naming convention**: API executors use `api/` prefix (e.g., `api/gpt-4o`, `api/ollama-llama`). CLI executors use plain names (e.g., `claude`, `codex`). This makes executor type visible in tool calls without inspecting the registry.

**Notes**:
- **File-based prompt delivery**: Prompts >4KB written to temp file, piped via stdin or passed as path (see Section 10.2)
- **Copilot CLI**: Marked experimental — invocation pattern to be confirmed as `gh copilot` agent capabilities evolve
- **No hardcoded enum**: The `executor` parameter on tools is a free string validated against the registry at call time, not at schema definition time

### 4.3 `mcp_ucx/src/mcp_server/executor/cli_runner.py` (~100 lines)
Async subprocess runner for CLI agents.

```python
async def run_executor(
    executor_name: str,
    prompt: str,
    working_dir: Path | None = None,
    timeout: int = 300,
) -> ExecutorResult:
```

- Resolves executor config from registry
- Spawns `asyncio.create_subprocess_exec` with prompt via arg or stdin
- Captures stdout/stderr
- Returns `ExecutorResult(stdout, stderr, exit_code, executor_name)`
- Timeout with `asyncio.wait_for`

### 4.4 `mcp_ucx/src/mcp_server/executor/api_runner.py` (~40 lines)
Stub for API-based LLM execution via LiteLLM. Raises `NotImplementedError` in v0.1.0.

- `run_api_executor(config, prompt, system_prompt?, timeout) -> ExecutorResult`
- When implemented (v0.2.0): uses `litellm.acompletion()` as universal gateway
- Supports 100+ providers: OpenAI, Anthropic, Google, Azure, Bedrock, Ollama, local models

### 4.5 `mcp_ucx/src/mcp_server/executor/dispatcher.py` (~30 lines)
Routes executor calls by type:

```python
async def run_executor(name: str, prompt: str, ...) -> ExecutorResult:
    config = get_executor(name)
    if config.executor_type == ExecutorType.CLI:
        return await run_cli_executor(config, prompt, ...)
    elif config.executor_type == ExecutorType.API:
        return await run_api_executor(config, prompt, ...)
```

### 4.6 `mcp_ucx/src/mcp_server/tool_registry.py` (~450 lines)
All 15 MCP Tool definitions + handler dispatch.

**Deterministic tools (11)** — execute directly, return JSON (always available for granular control):

| Tool Name | Runner Function | Key Params |
|-----------|----------------|------------|
| `sdd_init` | `scaffold_project_ucx` | project |
| `sdd_validate` | `run_project_validation_build` | project, doc_type, layer, document |
| `sdd_consistency` | `run_consistency_check` | target |
| `sdd_preflight` | `run_preflight` | project, context |
| `sdd_prescreen` | `run_prescreen` | document |
| `sdd_scan` | `run_scan` | report_file |
| `sdd_score_show` | `show_score` | report_file |
| `sdd_score_validate` | `validate_score` | report_file, threshold |
| `sdd_score_compare` | `compare_scores` | baseline_report_file, candidate_report_file |
| `sdd_list_executors` | `list_executors` | (none) |
| `sdd_register_executor` | `register_executor` | name, command, args, prompt_mode |

**Orchestration tools (2)** — high-level lifecycle automation:

| Tool Name | Purpose | Key Params |
|-----------|---------|------------|
| `sdd_run_lifecycle` | Run multiple lifecycle stages in sequence on a document | project, doc_type, layer, document, stages, executor?, persona?, template? |
| `sdd_next_action` | Inspect document folder and recommend next lifecycle stage | document |

`sdd_run_lifecycle` accepts a `stages` array (subset of `["create", "validate", "validate_fix", "review", "remediate", "remediate_fix"]`). Runs each stage in order, feeding output from one stage as input to the next. Returns a combined report with per-stage results. If any stage fails, stops and reports which stage failed and why. Example:

```json
{
    "project": "/path/to/project",
    "doc_type": "brd",
    "layer": "01_BRD",
    "document": "/path/to/docs/01_BRD/BRD-01_platform/",
    "stages": ["validate", "validate_fix", "review"],
    "executor": "claude",
    "persona": "architect",
    "template": "UCR_PROMPT_BRD_PROJECT.md"
}
```

`sdd_next_action` inspects the artifact folder for existing stage outputs and returns:

```json
{
    "document": "/path/to/docs/01_BRD/BRD-01_platform/",
    "current_stage": "validated",
    "existing_artifacts": ["BRD-01_platform.md", "validation_report.json", "BRD-01_platform_validation.md"],
    "next_action": "review",
    "next_tool": "sdd_review",
    "next_params": {"project": "...", "doc_type": "brd", "layer": "01_BRD", "document": "..."}
}
```

**Both tools are optional conveniences.** All individual stage tools remain fully available for debugging, manual execution, re-running a single stage, or custom workflows.

**LLM-dependent tools (6)** — accept optional `executor` param, callable individually:

| Tool Name | Runner Function | Executor Behavior |
|-----------|----------------|-------------------|
| `sdd_create_build` | `run_project_creation_build` | If executor: spawn agent with assembled prompt. If omitted: return prompt text |
| `sdd_create` | `run_project_creation_artifact` | If executor: spawn agent to generate content, write artifact. If omitted: write template artifact |
| `sdd_review` | `run_project_review_build` | If executor: spawn agent with review prompt. If omitted: return prompt text |
| `sdd_validate_fix` | `run_validate_fix_build` | If executor: spawn agent to apply fixes. If omitted: return fix report |
| `sdd_remediate` | `run_remediation_build` | If executor: spawn agent with remediation prompt. If omitted: return findings |
| `sdd_remediate_fix` | `run_remediate_fix_build` | If executor: spawn agent to apply fixes. If omitted: return fix report |

**Common `executor` parameter** (on all LLM-dependent tools):
```json
{
  "executor": {
    "type": "string",
    "description": "CLI AI agent name from executor registry. Omit to return prompt text for orchestrator to handle. Use sdd_list_executors to see available executors.",
    "type": "string"
  }
}
```

**Handler pattern**:
```python
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    # 1. Convert string paths to Path objects
    # 2. Call runner function (deterministic part)
    # 3. If executor specified: spawn CLI agent with prompt
    # 4. Serialize result to JSON
    # 5. Return TextContent
```

**SourceSection reconstruction**: For tools accepting `sections` (create-build, review), the input schema accepts a JSON array of `{section_id, title, content, included?}` objects, converted to `SourceSection` instances internally.

### 4.7 `mcp_ucx/src/mcp_server/server.py` (~50 lines)
Thin MCP server entry point. Follows exact pattern from `ucx_knowledge/mcp/server.py`:

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent
from mcp_server.tool_registry import TOOLS, handle_tool

server = Server("sdd-lifecycle")

@server.list_tools()
async def list_tools(): return TOOLS

@server.call_tool()
async def call_tool(name, arguments):
    return await handle_tool(name, arguments)

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

def main_sync():
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
```

### 4.8 `mcp_ucx/pyproject.toml` (~30 lines)
Package definition:

```toml
[project]
name = "mcp-sdd-server"
version = "0.1.0"
description = "MCP server for Specification-Driven Development lifecycle"
requires-python = ">=3.12"
dependencies = [
    "mcp[cli]>=1.0.0",
    "pydantic>=2.0",
]

[project.scripts]
mcp-sdd = "mcp_server.server:main_sync"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mcp_server"]
```

### 4.9 `mcp_ucx/tests/unit/test_server.py` (~200 lines)
Tests for the MCP transport layer:

- Tool registry completeness (19 tools: 11 deterministic + 2 orchestration + 6 LLM-dependent)
- Tool name uniqueness
- Input schema validity (all required fields present)
- Deterministic tool handler: mock runner, verify JSON result
- LLM-dependent tool handler without executor: verify prompt returned
- LLM-dependent tool handler with executor: mock subprocess, verify spawn
- Executor registry: known executors resolve, unknown raises KeyError
- Executor registry: register/remove custom executors at runtime
- Path argument conversion: string to Path
- Error handling: runner exception mapped to error JSON response
- `sdd_next_action`: mock folder contents, verify correct next stage recommendation
- `sdd_run_lifecycle`: mock runners, verify stage chaining and combined report
- `sdd_run_lifecycle`: verify early stop on stage failure

---

## 5. Registration

Add to project `.mcp.json` (or create one at `mcp_ucx/.mcp.json`):

```json
{
  "mcpServers": {
    "sdd-lifecycle": {
      "command": "/opt/data/ucx_framework/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/opt/data/ucx_framework/mcp_ucx/src"
    }
  }
}
```

---

## 6. Implementation Order

0. **Rename `mcp/` → `mcp_ucx/`** — `git mv mcp mcp_ucx`, verify existing tests pass
1. **Create `roadmap/ROADMAP.md`** — initial roadmap with v0.1.0 planned
2. `executor/__init__.py` + `executor/registry.py` — zero dependencies
3. `executor/runner.py` — depends on registry
4. `tool_registry.py` — depends on executor + all runners
5. `server.py` — depends on tool_registry
6. `pyproject.toml` — packaging
7. `tests/unit/test_server.py` — validates everything
8. MCP registration — `.mcp.json` entry
9. **Create `changelog/CHANGELOG_v0.1.0.md`** — release record after implementation complete

---

## 7. Verification

1. **Unit tests**: `pytest mcp_ucx/tests/unit/test_server.py -v`
2. **Existing tests still pass**: `pytest mcp_ucx/tests/ -v` (no existing files modified)
3. **Manual MCP test**: Start server and call a deterministic tool:
   ```bash
   cd /opt/data/ucx_framework/mcp_ucx/src
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python -m mcp_server.server
   ```
4. **Claude Code integration**: Add to `.mcp.json`, restart Claude Code, verify `sdd_*` tools appear in tool list
5. **End-to-end with executor**: Call `sdd_validate` (deterministic) then `sdd_review` with `executor: "claude"` (LLM-dependent)

---

## 8. Roadmap and Changelog

### 8.1 Changelog Policy

- **Location**: `changelog/CHANGELOG_vX.Y.Z.md` (one file per release)
- **When to create**: After each version-tagged commit or logical release milestone
- **NOT on every commit** — group related commits into releases using semver:
  - **Patch** (0.0.x): bug fixes, minor corrections
  - **Minor** (0.x.0): new features, new tools, new commands
  - **Major** (x.0.0): breaking changes, architectural shifts

**Changelog entry format** (follows UCX_v1 convention):
```markdown
# CHANGELOG vX.Y.Z

**Release Date**: YYYY-MM-DD
**Type**: Major/Minor/Patch (summary)

## Summary
One paragraph describing the release.

## Changes
### Feature/Fix Group Name
- Bullet list of changes with file paths

## Backward Compatibility
State whether changes are backward compatible.

## Validation Evidence
- Test results, verification steps performed
```

### 8.2 Roadmap

- **Location**: `roadmap/ROADMAP.md` (single file, updated in place)
- **When to update**: When planning new releases, completing milestones, or shifting priorities
- **Scope**: This repo only (`ucx_framework`). Project-specific roadmaps live in their own repos.

**Roadmap format** (follows UCX_v1 convention):
```markdown
# ucx_framework Roadmap

| Field | Value |
| --- | --- |
| Current Version | X.Y.Z |
| Next Minor | description |
| Next Major | description |

## Version Timeline
(ASCII diagram)

## Planned Releases
### vX.Y.Z - Title
| Field | Value |
| Status | Planned/In Progress/Implemented |
| Type | Major/Minor/Patch |
| Scope | description |

## Completed Releases
(moved here after implementation)
```

### 8.3 Initial Files to Create

1. **`roadmap/ROADMAP.md`** — Initial roadmap with v0.1.0 (MCP transport layer) as first planned release
2. **`changelog/CHANGELOG_v0.1.0.md`** — Created after PLAN-001 implementation completes

### 8.4 Scope Boundary Rule

Each repository maintains its own changelog and roadmap. Do not mix:
- `ucx_framework` changelog/roadmap — SDD framework, MCP servers, skills, templates
- Project-specific repos (ibmcp, b_local, trading) — their own changelogs in their own repos
- `mcp_ucx/docs/CHANGELOG/` — internal MCP-SDD subsystem changelog (already exists, continues independently)

---

## 9. Reference Files

| File | Purpose |
|------|---------|
| `mcp_ucx/src/mcp_server/cli/main.py` | Existing CLI — all argument patterns and runner imports |
| `ucx_knowledge/mcp/server.py` | Reference MCP server implementation to follow |
| `dev_tools/mcp/pyproject.toml` | Reference packaging pattern |
| `mcp_ucx/src/mcp_server/review/runner.py` | Runner signatures: review, creation |
| `mcp_ucx/src/mcp_server/validation/runner.py` | Runner signature: validation |
| `mcp_ucx/src/mcp_server/remediation/runner.py` | Runner signatures: remediation, fix flows |
| `mcp_ucx/src/mcp_server/scoring/runner.py` | Runner signatures: scoring |
| `mcp_ucx/src/mcp_server/consistency/runner.py` | Runner signature: consistency |
| `mcp_ucx/src/mcp_server/preflight/runner.py` | Runner signature: preflight |
| `mcp_ucx/src/mcp_server/prescreening/runner.py` | Runner signature: prescreen |
| `mcp_ucx/src/mcp_server/scan/runner.py` | Runner signature: scan |
| `mcp_ucx/src/mcp_server/skills/scaffold.py` | Runner signature: init |

---

## 10. Gap Analysis and Resolutions

Gap review performed 2026-03-28. All Critical/High items resolved below.

### 10.1 Executor CLI Invocations (Critical/High — RESOLVED)

The original registry had incorrect CLI flags. Corrected invocations:

```python
EXECUTORS = {
    "claude": {
        "command": "claude",
        "args": ["-p", "--output-format", "json", "--verbose"],
        "prompt_mode": "file",  # write prompt to temp file, pass via stdin pipe
        "notes": "Uses --print mode. For agent-mode tasks needing file access, caller must add --allowedTools or --dangerously-skip-permissions.",
    },
    "codex": {
        "command": "codex",
        "args": ["exec"],
        "prompt_mode": "positional",  # codex exec "prompt"
    },
    "gemini": {
        "command": "gemini",
        "args": [],
        "prompt_mode": "positional",  # gemini "prompt"
    },
    "opencode": {
        "command": "opencode",
        "args": ["run"],
        "prompt_mode": "positional",  # opencode run "prompt"
    },
}
```

**Copilot CLI** retained as `experimental` — current `gh copilot suggest` is command-suggestion only, but `gh copilot` agent capabilities are evolving. Invocation pattern marked for confirmation. Registry validates executor `status` field and warns on experimental executors.

### 10.2 Prompt Delivery — File-Based (High — RESOLVED)

All executors use **file-based prompt delivery** to avoid shell escaping and ARG_MAX issues:

1. Write assembled prompt to temp file (`tempfile.NamedTemporaryFile`, suffix=`.md`)
2. Pass temp file path or pipe content via stdin depending on executor
3. Clean up temp file after executor completes

This handles prompts of any size safely. The `prompt_mode` field in executor config controls delivery:
- `"file"` — pipe file content via stdin
- `"positional"` — pass as positional argument (for short prompts) or fall back to file-stdin for prompts >4KB

### 10.3 Working Directory and Environment (High — RESOLVED)

- **Working directory**: Defaults to the `project` path from the MCP tool call. The tool handler extracts `project` and passes it as `working_dir` to `run_executor`.
- **Environment**: Subprocess inherits `os.environ` from the MCP server process. Document requirement: the MCP server must be launched in an environment that has API keys for all configured executors (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`).

### 10.4 Executor Output Handling (High — RESOLVED)

Strategy: **pass-through with metadata wrapper**.

```python
@dataclass(frozen=True)
class ExecutorResult:
    stdout: str
    stderr: str
    exit_code: int
    executor_name: str
    prompt_file: str  # path to temp prompt file (for debugging)
```

MCP tool response when executor is used:
```json
{
    "executor": "claude",
    "exit_code": 0,
    "output": "<raw stdout from executor>",
    "stderr": "<stderr if non-empty>",
    "deterministic_result": { /* runner function output (reports, paths) */ }
}
```

The orchestrator decides how to interpret executor output. The MCP server does not parse it — different executors have different formats and the orchestrator knows which executor it chose.

**Non-zero exit code**: Returned as a successful MCP tool response with `exit_code` field set. The orchestrator inspects exit code and decides whether to retry with a different executor.

### 10.5 Input Schema Completeness (High — RESOLVED)

Full parameter lists for all tools (matching CLI and runner signatures):

**sdd_validate** — add: `tier1_only` (boolean), `strict` (boolean), `format` (enum: text/json), `out` (string, optional)

**sdd_review** — add: `unified` (boolean), `one_turn` (boolean), `no_resume` (boolean), `session_ttl` (integer), `clean_memory` (boolean), `clean_reports` (boolean), `keep_versions` (integer), `out` (string, optional)

**sdd_create** — add: `target` (string, REQUIRED), `overwrite` (boolean), `sections` (array, optional), `out` (string, optional)

**sdd_create_build** — add: `sections` (array, optional), `out` (string, optional)

**sdd_validate_fix** — add: `validation_report` (string, optional), `out` (string, optional)

**sdd_remediate** — add: `review_report` (string, optional), `out` (string, optional)

**sdd_remediate_fix** — add: `remediation_report` (string, optional), `out` (string, optional)

**sdd_preflight** — add: `document` (string, optional), `format` (enum: text/json), `out` (string, optional)

**sdd_consistency** — add: `format` (enum: text/json), `out` (string, optional)

**sdd_prescreen** — add: `out` (string, optional)

**sdd_scan** — add: `out` (string, optional)

All tools: `out` parameter defaults to stage-specific `.ucx/<stage>` directory when omitted.

### 10.6 pyproject.toml — main_sync (Critical — RESOLVED)

Add sync wrapper to `server.py`:

```python
def main_sync():
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
```

### 10.7 Rename Documentation Impact (High — DEFERRED)

The `git mv mcp mcp_ucx` will leave stale `mcp/` path references in ~20 documentation files inside `mcp_ucx/docs/`. Resolution:
- Run global find-and-replace `mcp/src` → `mcp_ucx/src`, `mcp/tests` → `mcp_ucx/tests`, `mcp/docs` → `mcp_ucx/docs` across all `.md` files in `mcp_ucx/docs/`
- Verify with `grep -r "mcp/" mcp_ucx/docs/ | grep -v mcp_ucx` to catch remaining stale refs
- This is a mechanical step executed immediately after `git mv`

### 10.8 MCP Progress Notifications (Medium — DEFERRED to v0.2.0)

Long-running executor calls (2-5 min) have no progress reporting. The MCP protocol supports `notifications/progress` but implementing it requires streaming subprocess output. Deferred to v0.2.0.

### 10.9 Timeout Configurability (Low — RESOLVED)

Add optional `timeout` parameter (integer, seconds) to all LLM-dependent tools. Default: 300. Max: 900.

### 10.10 Error Handling — Executor Not Installed (Medium — RESOLVED)

`FileNotFoundError` from `create_subprocess_exec` caught and returned as:
```json
{"error": "Executor 'codex' not found. Ensure 'codex' is installed and in PATH.", "executor": "codex"}
```
