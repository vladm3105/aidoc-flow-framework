# CHANGELOG — UCX v1.14.0

**Release Date**: 2026-04-03
**Plan**: N/A (executor simplification + PLAN-021 naming compliance fix)

## Summary

Simplify CLI executor prompt delivery to a single positional-argument path for all executors. Fix validation report naming to comply with PLAN-021 standard (`validate_review` → `validate`).

## Changed

### Executor Simplification

- `cli_runner.py`: All CLI executors now receive the prompt as a positional argument — no size-based branching, no stdin fallback, no temp file creation
- `prompt_mode` field in `ExecutorConfig` is deprecated and ignored at runtime (retained in dataclass for `executors.json` backward compatibility)
- Removed `prompt_file` field from `ExecutorResult` dataclass
- Removed `PROMPT_SIZE_THRESHOLD` constant (was 4096 bytes)
- Removed `tempfile` import from `cli_runner.py`
- `_maybe_run_executor` response: `prompt_file` field now always `None`
- Claude executor config: removed `prompt_mode: "file"` — now uses positional like all others
- Codex, Gemini, OpenCode, Copilot-CLI: removed explicit `prompt_mode: "positional"` (positional is now the only path)

### Report Naming Fix (PLAN-021 Compliance)

- `{id}.ucx.validate_review.json/.txt` → `{id}.ucx.validate.json/.txt`
- Aligns with PLAN-021 stage code table: validate stage produces `{id}.ucx.validate.{ext}`
- The `validate_review` name was introduced in v1.13.0 (PLAN-023) but contradicted PLAN-021
- Updated `REPORT_PATTERN` regex in `source_files.py` — removed `validate_review` alternative
- Updated `_inspect_document_folder` detection: `.validate_review.` → `.validate.`
- Updated `consistency/runner.py` report path lookup

## Removed

- `PROMPT_SIZE_THRESHOLD` constant from `cli_runner.py`
- `prompt_file` field from `ExecutorResult`
- `tempfile` import from `cli_runner.py`
- `validate_review` from `REPORT_PATTERN` regex
- `prompt_mode` values from all builtin executor configs

## Backward Compatibility

- `prompt_mode` field remains in `ExecutorConfig` dataclass — external `executors.json` files that set it will not break, but the field is ignored
- Existing `*.ucx.validate_review.json` files on disk are not auto-renamed — re-run `sdd_validate` to produce files with the corrected name
- `consistency/runner.py` looks up `{id}.ucx.validate.json` first, then falls back to legacy `{id}_validation_report.json`

## Files Changed

- `mcp_sdd/src/mcp_server/executor/cli_runner.py` — simplified to single positional-argument delivery
- `mcp_sdd/src/mcp_server/executor/registry.py` — removed `prompt_mode` from all builtin configs
- `mcp_sdd/src/mcp_server/tool_registry.py` — `prompt_file: None`, updated validate detection pattern
- `mcp_sdd/src/mcp_server/validation/runner.py` — `validate_review` → `validate` in report filenames
- `mcp_sdd/src/mcp_server/consistency/runner.py` — updated report path lookup
- `mcp_sdd/src/mcp_server/utils/source_files.py` — removed `validate_review` from `REPORT_PATTERN`
- `mcp_sdd/tests/unit/test_server.py` — updated report filename assertions, removed `prompt_file`
- `mcp_sdd/tests/unit/test_yaml_parity.py` — updated report filename
- `mcp_sdd/tests/unit/test_remediation_runner.py` — updated report filename
- `mcp_sdd/tests/unit/test_cli_main.py` — updated report filenames
- `mcp_sdd/tests/integration/test_migration_flows.py` — updated report glob pattern
- `mcp_sdd/docs/architecture/MCP_CLI_REFERENCE.md` — updated artifact lineage
- `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md` — updated artifact names
- `mcp_sdd/docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md` — updated executor section
- `mcp_sdd/docs/CHANGELOG/CHANGELOG_v1.13.0.md` — corrected naming claims
- `mcp_sdd/docs/ROADMAP.md` — corrected v1.13.0 naming, added v1.14.0
- `mcp_sdd/docs/README.md` — updated version, report naming example, changelog list

## Validation

- 214 unit tests passed
- 57 integration tests passed
- Zero remaining references to `validate_review` in codebase
