# PLAN-031: API Executor (LiteLLM) and Tool Surface Cleanup

**Status**: Complete (2026-04-07)

## Context

UCX (Unified Context eXcelerator) is an AI agent orchestration platform. Its core value is assembling project-specific context for any AI agent. Two blockers prevent this from working end-to-end:

1. **API executors are a stub** — `api_runner.py` raises `NotImplementedError`. Only CLI executors work. This blocks headless/CI pipeline execution and direct API provider access (OpenRouter, Claude API, OpenAI).
2. **`sdd_remediate_fix` as a standalone tool is confusing** — agents see two remediation tools and must decide which to call. `sdd_remediate --fix` already chains into the fix step internally. The standalone tool adds surface area without adding capability.
3. **No cleanup tool** — validation, review, and remediation stages accumulate reports, derived copies, and diagnostics in document folders. With PLAN-030's versioned copies (`_remediate_v1`, `_v2`, ...) this grows fast. No way to prune obsolete artifacts while keeping the latest.

## Goals

- Implement LiteLLM-based API executor so any LLM provider can execute UCX prompts
- Absorb `sdd_remediate_fix` into `sdd_remediate` as an internal procedure
- Add `sdd_clean` tool to prune obsolete stage artifacts, keeping only the latest per document
- Net tool count: 25 → 25 (remove `sdd_remediate_fix`, add `sdd_clean`)
- Update `sdd_run_lifecycle` pipeline to reflect the merged tool
- Add OpenRouter support via LiteLLM's provider prefix routing

## Non-Goals

- CLI parity (deferred — MCP-first approach)
- Pipeline retry/loop logic (PLAN-032)
- Workflow definitions (PLAN-033)

---

## Phase 1: API Executor Implementation

### 1a. Implement `api_runner.py`

**File**: `mcp_sdd/src/mcp_server/executor/api_runner.py`

Current state: 28 lines, raises `NotImplementedError`.

Replace with LiteLLM integration:

```python
async def run_api_executor(
    config: ExecutorConfig,
    prompt: str,
    system_prompt: str | None = None,
    timeout: int | None = None,
    project_env: dict[str, str] | None = None,
) -> ExecutorResult:
```

Implementation requirements:

1. Import `litellm.acompletion` (async). Handle `ImportError` with clear install guidance.
2. Resolve API key from `config.api_key_env` using:
   - `project_env` dict (project `.env` — highest priority)
   - `os.environ` fallback
3. Call `litellm.acompletion()` with:
   - `model=config.model` (LiteLLM handles provider routing: `openrouter/`, `gemini/`, etc.)
   - `api_base=config.api_base` (if set, for custom endpoints)
   - `api_key=resolved_key`
   - `messages=[{"role": "user", "content": prompt}]` (add system_prompt as system message if provided)
   - `timeout=timeout or config.timeout`
4. Extract response text from `response.choices[0].message.content`.
5. Return `ExecutorResult(stdout=response_text, stderr="", exit_code=0, executor_name=config.name)`.
6. Handle errors:
   - `litellm.AuthenticationError` → exit_code=-4, stderr with key env var name
   - `litellm.RateLimitError` → exit_code=-5, stderr with retry guidance
   - `litellm.Timeout` → exit_code=-1, stderr matching CLI timeout format
   - `litellm.APIError` → exit_code=-6, stderr with provider error
   - `ImportError` → exit_code=-7, stderr: "pip install litellm"

### 1b. Update `dispatcher.py`

**File**: `mcp_sdd/src/mcp_server/executor/dispatcher.py`

Pass `project_env` to `run_api_executor` (currently only CLI runner receives it):

```python
elif config.executor_type == ExecutorType.API:
    result = await run_api_executor(
        config=config,
        prompt=prompt,
        timeout=timeout,
        project_env=project_env,  # ADD: for API key resolution
    )
```

### 1c. Update `registry.py` built-in API entries

**File**: `mcp_sdd/src/mcp_server/executor/registry.py`

Change status from `"stub"` to `"active"` for built-in API executors. Add OpenRouter entry:

```python
BUILTIN_API_EXECUTORS: dict[str, dict] = {  # Rename from BUILTIN_API_STUBS
    "api/gpt-4o": {
        "model": "gpt-4o",
        "api_key_env": "OPENAI_API_KEY",
    },
    "api/claude-sonnet": {
        "model": "claude-sonnet-4-20250514",
        "api_key_env": "ANTHROPIC_API_KEY",
    },
    "api/gemini-pro": {
        "model": "gemini/gemini-2.5-pro",
        "api_key_env": "GEMINI_API_KEY",
    },
    "api/openrouter": {
        "model": "openrouter/auto",
        "api_key_env": "OPENROUTER_API_KEY",
    },
}
```

Update `_build_config` default status: remove the `"stub" if executor_type == ExecutorType.API` fallback — API executors are now active.

Update `_init_builtins()` to reference renamed dict.

### 1d. Add `litellm` as optional dependency

**File**: `mcp_sdd/pyproject.toml` (or equivalent)

Add optional dependency group:

```toml
[project.optional-dependencies]
api = ["litellm>=1.40.0"]
```

API executor gracefully degrades when litellm is not installed.

---

## Phase 2: Absorb `sdd_remediate_fix` into `sdd_remediate`

### 2a. Add `remediation_report` parameter to `sdd_remediate`

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`

Add to `sdd_remediate` input schema (after existing `review_report`):

```python
"remediation_report": {
    "type": "string",
    "description": "Path to existing remediation report. When combined with fix=true, skips findings generation and applies fix from this report directly."
},
```

Behavior matrix:

| `fix` | `remediation_report` | Behavior |
|-------|---------------------|----------|
| false | omitted | Generate findings only (current default) |
| true  | omitted | Generate findings → auto-chain into fix (current `--fix`) |
| true  | provided | Skip findings → fix directly from provided report |
| false | provided | Ignored (findings-only mode doesn't use remediation report) |

### 2b. Update `sdd_remediate` handler

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`, lines 1023-1067

**Prerequisite**: PLAN-030 must be complete. `run_remediate_fix_build` already produces versioned output (`_remediate_v{N}`).

Three code paths based on arguments:

```python
if name == "sdd_remediate":
    # ... existing setup ...
    
    # Path A: Direct fix from existing report (skip findings generation)
    if arguments.get("fix") and arguments.get("remediation_report"):
        from mcp_server.remediation import run_remediate_fix_build
        fix_result = run_remediate_fix_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            remediation_report=_opt_path(arguments, "remediation_report"),
            output_dir=output_dir,
        )
        fix_det = _serialize_result(fix_result)
        return await _maybe_run_executor(
            arguments, fix_result.report_text, fix_det, working_dir=project_root,
        )
    
    # Path B: Generate findings (always)
    result = run_remediation_build(...)
    det_result = _serialize_result(result)
    remediate_response = await _maybe_run_executor(...)
    
    # Path C: Auto-chain into fix after findings (fix=true, no existing report)
    if arguments.get("fix"):
        # Uses result.report_path from Path B as remediation_report
        # run_remediate_fix_build produces _remediate_v{N} (PLAN-030)
        ...
    
    return remediate_response
```

Note: `run_remediate_fix_build` is now an internal function only — no longer exposed as a standalone MCP tool.

### 2c. Remove `sdd_remediate_fix` from TOOLS list

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`

Delete the `Tool(name="sdd_remediate_fix", ...)` entry (lines 389-406).

Delete the handler block (lines 1069-1112):
```python
if name == "sdd_remediate_fix":
    ...
```

### 2d. Update `sdd_next_action`

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`, lines 554-557

Change:
```python
elif has_remediation_report:
    current_stage = "remediation_reported"
    next_action = "remediate_fix"
    next_tool = "sdd_remediate_fix"
```

To:
```python
elif has_remediation_report:
    current_stage = "remediation_reported"
    next_action = "remediate --fix"
    next_tool = "sdd_remediate"
```

### 2e. Update `_handle_lifecycle_pipeline`

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`, lines 1113-1178

Update stage handlers map:
```python
stage_handlers = {
    "validate": "sdd_validate",
    "validate_fix": "sdd_validate",
    "review": "sdd_review",
    "remediate": "sdd_remediate",
    "remediate_fix": "sdd_remediate",  # CHANGED: route to sdd_remediate with fix=true
}
```

For `remediate_fix` stage, inject `fix=true` into stage_args:
```python
if stage == "remediate_fix":
    stage_args["fix"] = True
```

Post-fix verification (lines 1154-1169): update condition from `stage == "remediate_fix"` to check for fix result presence. Derived paths now use versioned naming (`_remediate_v{N}` from PLAN-030):

```python
# Post-fix verification when remediate produced fix output
if stage == "remediate_fix":
    # fix=true was injected — check fix_result inside stage_result
    fix_result = stage_result.get("fix_result", stage_result)
    derived_paths = fix_result.get("derived_paths", [])
    if derived_paths:
        # derived_paths[0] is now _remediate_v{N} (versioned, PLAN-030)
        verify_args = {
            k: v for k, v in stage_args.items()
            if k in ("project", "doc_type", "layer")
        }
        verify_args["document"] = derived_paths[0]
        ...
```

### 2f. Update `sdd_score_compare` tool description

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`

Update any tool descriptions that reference `sdd_remediate_fix` to say `sdd_remediate --fix` instead.

---

## Phase 3: Tests

### 3a. API executor tests

**File**: `mcp_sdd/tests/unit/test_api_runner.py` (new)

- Test `ImportError` handling when litellm not installed
- Test API key resolution from project_env vs os.environ
- Test error mapping (auth, rate limit, timeout, API error)
- Mock `litellm.acompletion` for success path

**File**: `mcp_sdd/tests/integration/test_api_executor_integration.py` (new)

- Test dispatcher routes API type correctly
- Test project `.env` API key injection
- Test built-in API executor configs are valid

### 3b. Remediate merge tests

**File**: `mcp_sdd/tests/unit/test_remediation_runner.py` (update)

- Test `sdd_remediate` with `fix=true` (existing, verify still passes)
- Test `sdd_remediate` with `fix=true, remediation_report=path` (new — direct fix mode)
- Test `sdd_remediate` with `remediation_report` but `fix=false` (findings-only, report ignored)

**File**: `mcp_sdd/tests/unit/test_server.py` (update)

- Remove `sdd_remediate_fix` from tool list assertions
- Add `sdd_clean` to tool list assertions
- Update any test that directly invokes `sdd_remediate_fix`

**File**: `mcp_sdd/tests/unit/test_yaml_parity.py` (update)

- Remove `sdd_remediate_fix` from YAML/MCP parity checks

**File**: `mcp_sdd/tests/integration/test_lifecycle_pipeline_integration.py` (update)

- Verify `remediate_fix` stage in pipeline now routes through `sdd_remediate` with `fix=true`

---

## Phase 4: Documentation Updates

### 4a. Architecture docs

| File | Change |
|------|--------|
| `mcp_sdd/docs/README.md` | Remove `sdd_remediate_fix`, add `sdd_clean`, document API executor |
| `mcp_sdd/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md` | Update canonical runtime surface, remove remediate-fix as separate command |
| `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md` | Remove `remediate-fix` command, document `remediate --fix --remediation-report` |
| `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md` | Update remediation flow to single-tool model |
| `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md` | Update remediation procedures |
| `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md` | Update executor section with API executor details |

### 4b. Specs

| File | Change |
|------|--------|
| `mcp_sdd/docs/specs/SPEC-009_mcp_remediation_and_fix_flow_contracts.md` | Update contracts: single tool, two modes |
| `mcp_sdd/docs/specs/SPEC-007_mcp_review_remediation_operational_contracts.md` | Remove standalone fix tool contracts |

### 4c. Framework docs

| File | Change |
|------|--------|
| `README.md` (root) | Update tool list (swap `sdd_remediate_fix` for `sdd_clean`) |
| `ai_dev_ssd_flow/REPORT_NAMING_STANDARDS.md` | Update stage codes table (remove standalone `remediate_fix` stage, note it's now `remediate` with `fix=true`) |

### 4d. Roadmap

**File**: `mcp_sdd/docs/ROADMAP.md`

Add v1.21.0 release entry:

```markdown
### v1.21.0 - API Executor and Tool Surface Cleanup (PLAN-031)

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | Implement LiteLLM API executor, absorb sdd_remediate_fix into sdd_remediate |

Planned scope:

- Implement API executor via LiteLLM (100+ LLM providers including OpenRouter)
- Absorb sdd_remediate_fix into sdd_remediate as fix=true mode
- Add sdd_clean tool for stage artifact pruning
- Add built-in OpenRouter executor entry
- Update lifecycle pipeline for merged remediation tool and optional pre-clean
```

---

## Phase 5: `sdd_clean` — Stage Artifact Cleanup Tool

### 5a. Problem

Each lifecycle stage writes artifacts into the document folder:

| Stage | Files Created | Accumulation Pattern |
|-------|--------------|---------------------|
| validate | `{DOC-ID}.ucx.validate.json`, `.txt`, `_validate_copy.*` | Overwritten per run |
| review | `{DOC-ID}.ucx.review.md`, inspection/sidecar files | Overwritten per run |
| remediate | `{DOC-ID}.ucx.remediate.json`, `.txt` | Overwritten per run |
| remediate --fix | `{stem}_remediate_v1.*`, `_v2.*`, `_v3.*` ... | **Accumulates** (PLAN-030) |
| validate (with --keep-history) | `{DOC-ID}.ucx.validate.v001.json`, `.v002.json` ... | **Accumulates** |
| creation | prompt bundles, sidecar metadata | Per run |

After several iterations a document folder contains dozens of obsolete reports, old versioned copies, and diagnostic files. No tool exists to prune them.

### 5b. Tool Definition

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`

Add to TOOLS list:

```python
Tool(
    name="sdd_clean",
    description="Remove obsolete stage artifacts from document folder, keeping only the latest report and derived copy per stage.",
    inputSchema={
        "type": "object",
        "properties": {
            "project": {
                "type": "string",
                "description": "Project root path. Resolved from session/config default when omitted.",
            },
            "document": {
                "type": "string",
                "description": "Path to document file or directory to clean.",
            },
            "stages": {
                "type": "array",
                "items": {"type": "string", "enum": ["validate", "review", "remediate", "creation", "all"]},
                "description": "Stages to clean. Default: ['all'].",
                "default": ["all"],
            },
            "keep": {
                "type": "integer",
                "description": "Number of latest versions to keep per artifact type. Default: 1.",
                "default": 1,
                "minimum": 0,
            },
            "dry_run": {
                "type": "boolean",
                "description": "List files that would be deleted without deleting. Default: true.",
                "default": True,
            },
        },
        "required": ["document"],
    },
),
```

**Key design decisions:**
- `dry_run=True` by default — safe first invocation, agent must explicitly set `false` to delete
- `keep=1` — retain the latest version by default (not zero)
- `keep=0` — remove ALL stage artifacts (full clean for re-run from scratch)
- Stages are selectable — clean only remediation versions, or everything

### 5c. Cleanup Engine

**File**: `mcp_sdd/src/mcp_server/cleanup/runner.py` (new module)

```python
def run_clean(
    document_path: Path,
    stages: list[str],
    keep: int = 1,
    dry_run: bool = True,
) -> CleanResult:
```

**Artifact classification** (reuse patterns from `source_files.py`):

| Category | Pattern | Sort Key | Keep Rule |
|----------|---------|----------|-----------|
| Validation reports | `REPORT_PATTERN` with `.validate.` | Version number or mtime | Keep latest `keep` |
| Validation copies | `_validate_copy` or `_validated` | mtime | Keep latest `keep` |
| Review reports | `REPORT_PATTERN` with `.review.` | Version number or mtime | Keep latest `keep` |
| Remediation reports | `REPORT_PATTERN` with `.remediate.` | Version number or mtime | Keep latest `keep` |
| Remediation copies | `_remediate_v{N}` pattern | Version number (N) | Keep latest `keep` |
| Legacy remediation copies | `_remediate_copy` | mtime | Delete if versioned copies exist |
| Creation artifacts | Prompt bundles, sidecars in `.ucx/creation/` | mtime | Keep latest `keep` |
| Versioned reports | `.v{NNN}.json` / `.v{NNN}.txt` | Version number | Keep latest `keep` |

**Version sorting for remediation copies:**
- Parse `_remediate_v{N}` → sort by N descending → keep top `keep` → delete rest
- Example with `keep=1`: `_v1`, `_v2`, `_v3` → keep `_v3`, delete `_v1` and `_v2`

**Return value:**
```python
@dataclass
class CleanResult:
    deleted: list[str]      # Paths deleted (or would delete if dry_run)
    kept: list[str]         # Paths retained
    dry_run: bool
    total_bytes_freed: int  # 0 if dry_run
```

### 5d. Handler in tool_registry.py

```python
if name == "sdd_clean":
    from mcp_server.cleanup.runner import run_clean
    document_path = _path(arguments, "document")
    stages = arguments.get("stages", ["all"])
    keep = arguments.get("keep", 1)
    dry_run = arguments.get("dry_run", True)
    result = run_clean(
        document_path=document_path,
        stages=stages,
        keep=keep,
        dry_run=dry_run,
    )
    return {
        "dry_run": result.dry_run,
        "deleted": result.deleted,
        "deleted_count": len(result.deleted),
        "kept": result.kept,
        "kept_count": len(result.kept),
        "bytes_freed": result.total_bytes_freed,
    }
```

### 5e. Integration with `sdd_run_lifecycle`

Add optional `clean_before` parameter to `sdd_run_lifecycle`:

```python
"clean_before": {
    "type": "boolean",
    "description": "Run sdd_clean before starting pipeline. Default: false.",
    "default": False,
}
```

When `clean_before=true`, the pipeline runs `sdd_clean(document, stages=["all"], keep=0, dry_run=false)` before the first stage — starting from a clean slate.

### 5f. Tests

**File**: `mcp_sdd/tests/unit/test_cleanup_runner.py` (new)

1. **Versioned remediation cleanup**: Create `_v1`, `_v2`, `_v3` → clean with `keep=1` → only `_v3` remains
2. **Report cleanup**: Create `.validate.json`, `.validate.v001.json`, `.validate.v002.json` → clean → only latest remains
3. **Dry run**: Same setup → `dry_run=true` → files still exist, `deleted` list populated
4. **Stage filtering**: Create validate + remediation artifacts → clean `stages=["remediate"]` → only remediation cleaned
5. **keep=0**: All stage artifacts removed
6. **Legacy compat**: `_remediate_copy` cleaned when versioned copies exist
7. **Source protection**: Source documents (`TYPE-NN_slug.yaml`) never deleted regardless of settings

---

## Execution Checklist

- [ ] Phase 1a: Implement `api_runner.py` with LiteLLM
- [ ] Phase 1b: Update `dispatcher.py` — pass `project_env` to API runner
- [ ] Phase 1c: Update `registry.py` — rename stubs, add OpenRouter, change default status
- [ ] Phase 1d: Add `litellm` optional dependency
- [ ] Phase 2a: Add `remediation_report` param to `sdd_remediate` schema
- [ ] Phase 2b: Update `sdd_remediate` handler for direct-fix mode
- [ ] Phase 2c: Remove `sdd_remediate_fix` tool definition and handler
- [ ] Phase 2d: Update `sdd_next_action` references
- [ ] Phase 2e: Update `_handle_lifecycle_pipeline` stage routing
- [ ] Phase 2f: Update tool descriptions referencing `sdd_remediate_fix`
- [ ] Phase 3a: API executor unit + integration tests
- [ ] Phase 3b: Remediation merge tests (update existing + new)
- [ ] Phase 4a: Architecture docs update
- [ ] Phase 4b: Spec contracts update
- [ ] Phase 4c: Framework docs update
- [ ] Phase 4d: Roadmap entry
- [ ] Phase 5a-5c: Implement `sdd_clean` cleanup engine and runner
- [ ] Phase 5d: Add handler in tool_registry.py
- [ ] Phase 5e: Add `clean_before` to `sdd_run_lifecycle`
- [ ] Phase 5f: Cleanup runner tests

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| LiteLLM dependency adds weight | Optional dependency — API executor degrades gracefully with clear error |
| Removing `sdd_remediate_fix` breaks existing agent workflows | `sdd_remediate --fix` already works; pipeline `remediate_fix` stage still accepted (routed internally) |
| API key exposure in logs | Existing `env_manager.py` never logs values; API runner must follow same contract |
| LiteLLM version drift | Pin minimum version (`>=1.40.0`), test against latest in CI |

## Dependencies

- **PLAN-030 (versioned remediation copies)**: Must be completed before PLAN-031 Phase 2. PLAN-030 adds versioned naming (`_remediate_v{N}`) to `run_remediate_fix_build` output. PLAN-031 then absorbs that function into `sdd_remediate` as the `fix=true` mode.
- PLAN-030 Phase 5 (`--fix` auto-chain) was deferred to this plan — PLAN-031 Phase 2 is the canonical implementation of `--fix` behavior including the `remediation_report` direct-fix mode.
- After PLAN-030: `sdd_remediate_fix` standalone tool still exists but outputs versioned files. After PLAN-031: `sdd_remediate_fix` is removed, and `sdd_remediate --fix` produces versioned files via the same internal `run_remediate_fix_build` function.

### Execution Order

```
PLAN-030 Phases 1-4  →  versioned naming in run_remediate_fix_build
PLAN-030 Phase 6     →  tests for versioned naming
PLAN-030 Phase 7     →  doc updates for versioned naming
PLAN-031 Phase 1     →  API executor (independent, can parallel with PLAN-030)
PLAN-031 Phase 2     →  absorb sdd_remediate_fix + --fix chain + remediation_report param
PLAN-031 Phase 3     →  tests (including --fix chain test deferred from PLAN-030)
PLAN-031 Phase 4     →  doc updates
PLAN-031 Phase 5     →  sdd_clean tool (independent, can parallel with Phase 2)
```
