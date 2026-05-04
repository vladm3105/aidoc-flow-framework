# PLAN-017: Executor Output Routing and mcp_ucx Logging

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

## Context

During BRD-03 review pipeline testing, two infrastructure gaps were identified:

1. **Executor output not routed to document folder** — the executor writes files to its working directory but mcp_ucx doesn't enforce that output goes to the document's folder. Each tool should default `output_dir` to the document's parent folder.

2. **No mcp_ucx logging** — no structured logging of executor invocations, exit codes, timing, or pipeline stages. Logs should be written to the project's `UCX/logs/` directory.

**Goal**: Route all executor output to document folders by default, and add structured logging to the project UCX directory.

**Scope**: `mcp_ucx` server code only.

---

## Deliverables

### 1. Executor output routing

**File**: `mcp_ucx/src/mcp_server/tool_registry.py`

For all tools that accept `document` + `out` parameters, derive `working_dir` from the document path when no explicit `out` is provided:

- `sdd_validate` → output to document folder
- `sdd_validate_fix` → output to document folder
- `sdd_review` → output to document folder
- `sdd_remediate` → output to document folder
- `sdd_remediate_fix` → output to document folder
- `sdd_create` → output to document folder

The executor `working_dir` should also be set to the document folder so any files the executor writes (via Claude Code's Write/Edit tools) land in the correct location.

### 2. Structured logging

**File**: New `mcp_ucx/src/mcp_server/logging_config.py`

Log file location: `{project_root}/UCX/logs/mcp_ucx.log`

Log entries for:
- Tool invocations (tool name, arguments, timestamp)
- Executor launches (executor name, prompt length, working_dir, timeout)
- Executor completions (exit code, stdout length, duration)
- Validation results (errors, warnings, passes counts)
- Pipeline stage transitions

Format: JSON lines (one JSON object per log entry) for machine parsing.

---

## Implementation Order

1. Add logging module
2. Wire logging into tool_registry dispatch
3. Wire logging into executor dispatcher
4. Update executor working_dir derivation in tool_registry
5. Test
6. Commit
