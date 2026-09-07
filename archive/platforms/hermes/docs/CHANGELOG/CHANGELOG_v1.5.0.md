# CHANGELOG v1.5.0

**Release Date**: 2026-03-30
**Type**: Minor (Link Validation Tool + Executor Write Fixes)

## Summary

Added `sdd_validate_links` as the 20th MCP tool (12th deterministic). Fixed CLI executor configs for Claude Code and Codex CLI to enable non-interactive file writes in automated pipelines.

## Changes

### New Tool: sdd_validate_links

- Validates markdown links in documentation files
- Checks relative file links exist and anchor references (#heading) resolve
- Reports broken links with source file, line number, target path, and reason
- Supports single file or directory scanning
- Optional workspace_root for absolute link resolution
- Output: structured JSON + human-readable text reports
- CLI subcommand: `validate-links --target <path>`
- Module: `mcp_server/link_validation/runner.py`

### Executor Config Fixes

| Executor | Flag Added | Effect |
|----------|-----------|--------|
| Claude Code | `--dangerously-skip-permissions` | Non-interactive file writes in pipeline mode |
| Codex CLI | `--full-auto` | Workspace-write sandbox + auto-approve |

### Tool Registry

- Tool count: 19 → 20
- Deterministic tools: 11 → 12
- Docstrings updated in `server.py` and `tool_registry.py`

## Validation

- 18 new unit tests for link validation runner
- 33 server tests updated (tool count assertion, deterministic set)
- 186 total tests passing, 0 regressions
- Dry-run verified all 20 tools: 16 passed, 4 skipped (need LLM executor)
- End-to-end file write verified: Claude Code and Codex CLI
