# CHANGELOG — UCX v1.13.0

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

**Release Date**: 2026-04-02
**Plan**: PLAN-023 (Merge sdd_validate_fix into sdd_validate)

## Summary

Merge `sdd_validate_fix` into `sdd_validate` so a single tool runs structural validation and produces fix artifacts when errors are found. Rename validation artifacts for consistency. Tool count reduced from 20 to 19.

## Changed

- `sdd_validate` now produces derived copy (`_validated`) and fix report (`validate_fix_report.*`) automatically when validation errors are found
- `sdd_validate_fix` retained as deprecated alias — routes to `sdd_validate` with deprecation warning
- `sdd_next_action`: "validated" state transitions directly to "review" (no intermediate "validate_fix" step)
- Pipeline flow simplified from 6 stages to 5: create → validate → review → remediate → remediate-fix
- New response fields on `sdd_validate`: `is_valid` (bool), `fix_generated` (bool), `passed` always True (for pipeline compatibility)
- Artifact naming:
  - `{id}.ucx.validate.json/.txt` — initial validation report (unchanged per PLAN-021)
  - `*_validate_copy.*` → `*_validated.*` (derived copy suffix)
  - `{id}.ucx.validate_fix.json/.txt` — unchanged (fix metadata and instructions)

## Removed

- `sdd_validate_fix` as a standalone tool in the TOOLS registry (retained as deprecated alias)
- Tool count: 20 → 19 (12 deterministic, 1 orchestration, 6 LLM-dependent)

## Backward Compatibility

`sdd_validate_fix` continues to work as a deprecated alias. Callers receive a deprecation warning and are routed to `sdd_validate`. Output artifacts are identical. Callers should migrate to `sdd_validate` directly.

Consumers matching `*_validate_copy.*` must update to `*_validated.*`. Validation report naming `*.ucx.validate.json` is unchanged per PLAN-021.

## Files Changed

- `mcp_ucx/src/mcp_server/tool_registry.py` — removed `sdd_validate_fix` tool definition
- `mcp_ucx/src/mcp_server/server.py` — merged validate_fix logic into validate handler, added deprecated alias routing
- `mcp_ucx/src/mcp_server/validation/runner.py` — updated output filenames (`validate`, `_validated`)
- `mcp_ucx/src/mcp_server/validation/fix_runner.py` — integrated into validation runner
- `mcp_ucx/src/mcp_server/cli/main.py` — removed `validate-fix` subcommand, updated validate output handling
- `mcp_ucx/src/mcp_server/next_action.py` — "validated" → "review" transition (removed "validate_fix" intermediate)
- `mcp_ucx/src/mcp_server/consistency/runner.py` — updated artifact name patterns
- `mcp_ucx/src/mcp_server/utils/source_files.py` — updated `_validated` suffix exclusion
- `mcp_ucx/docs/README.md` — updated report naming example, version, changelog list
- `mcp_ucx/docs/ROADMAP.md` — added v1.13.0 entry
- `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md` — updated artifact names, pipeline stages, lineage chain
- `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md` — updated validate and validate-fix sections
- `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md` — updated validate-fix deprecation, artifact lineage, examples
