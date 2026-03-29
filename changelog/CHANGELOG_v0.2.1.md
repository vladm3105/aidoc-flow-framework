# CHANGELOG v0.2.1

**Release Date**: 2026-03-29
**Type**: Patch (MCP SDD Template Naming Migration)

## Summary

Updated the mcp_sdd server to support the unified template naming convention (`{ARTIFACT}-TEMPLATE.yaml`) introduced in v0.2.0. Adds backward-compatible fallback to legacy naming (`{ARTIFACT}-MVP-TEMPLATE.*`). BRD is the first layer migrated; other layers continue using legacy naming until individually refactored.

## Changes

### New: Resolution Helper (`mcp_sdd/src/mcp_server/utils/template_naming.py`)

- `resolve_template_path()`: Tries unified name first, falls back to MVP name for file path resolution
- `load_tuned_template()`: Tries `.yaml` → `.md` → `-MVP-.md` for template content loading
- New `utils/` package with `__init__.py`

### Modified: 5 Source Files (10 occurrences)

| File | Change |
|------|--------|
| `validation/runner.py` | Uses `resolve_template_path()` instead of hardcoded `-MVP-TEMPLATE.yaml` suffix |
| `skills/scaffold.py` | Broadened filter: `"-TEMPLATE"` matches both unified and legacy naming |
| `skills/project_ucx_loader.py` | Broadened filter: same approach as scaffold.py |
| `prompts/context_builder.py` | 6 occurrences updated: instructional strings, docstring, comment, and template loading via `load_tuned_template()` |
| `review/runner.py` | Broadened filter + renamed `mvp_template_name` → `template_name` |

### New: Template Copy

- Copied `BRD-TEMPLATE.yaml` to `mcp_sdd/templates/` alongside existing `BRD-MVP-TEMPLATE.md`

### Modified: Test Files

- `tests/unit/test_cli_main.py`: Updated assertion for validation test (template change affects validation outcome)
- `tests/unit/test_validation_runner.py`: Added 4 migration tests for template naming resolution

### Modified: Documentation

- `docs/architecture/MCP_OPERATIONAL_FLOWS.md` (v1.3 → v1.4): Updated scaffold and create-build descriptions to reflect both naming conventions

### Plan

- `work_plans/PLAN-002_mcp_sdd_template_naming_migration.md`: Implementation plan
- `work_plans/PLAN-002_checklist.md`: Execution checklist

## Backward Compatibility

Fully backward compatible:

- Legacy naming (`*-MVP-TEMPLATE.*`) continues to work via fallback resolution
- Non-BRD layers (PRD, EARS, ADR, SYS, REQ, etc.) unchanged — still use legacy naming
- `_MVP_SCHEMA.yaml` filter unchanged — schema files optional per layer
- Existing test suite: 173 passed (+4 new), 1 pre-existing failure

## Validation Evidence

- Baseline: 169 passed, 1 pre-existing failure
- Final: 173 passed, 1 pre-existing failure (0 regressions, +4 migration tests)
- Source grep: zero `MVP-TEMPLATE` references in source files (excluding resolution helper fallback logic and deprecation notes)
