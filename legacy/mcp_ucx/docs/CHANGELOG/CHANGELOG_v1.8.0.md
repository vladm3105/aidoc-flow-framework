# CHANGELOG v1.8.0

**Release Date**: 2026-04-02
**Type**: Minor (YAML Parity and API Consistency)
**Plan**: [PLAN-018](../plans/PLAN-018_yaml_parity_and_api_consistency.md)

## Summary

Ensures all mcp_ucx tools handle YAML documents on par with MD documents. Introduces categorized scoring weights, result class API aliases, YAML structure validation in remediation, and a shared source file collector.

## Changes

### YAML Parity

| Tool | Before | After |
|------|--------|-------|
| `sdd_consistency` | BLOCKED on YAML-only directories | Detects YAML source + derived copies |
| `sdd_next_action` | Missed YAML files in artifact list and stage detection | Full YAML lifecycle tracking |
| `sdd_remediate` | 0 findings for YAML documents | Validates structure, required keys, element IDs |

### Categorized Scoring

Formula: `score = 100 - (structural × 20) - (cross_section × 10) - (warnings × 5)`

Validation reports now include `structural_errors` and `cross_section_errors` counts in summary. Scoring runner uses category weights when available, falls back to original formula for old reports.

### Result Class API Aliases

All result classes now support uniform `.report` and `.is_valid` properties:

| Class | New Properties |
|-------|---------------|
| `ConsistencyRunResult` | `.report`, `.is_valid` |
| `LinkValidationRunResult` | `.report`, `.is_valid` |
| `PreflightRunResult` | `.report`, `.is_ready` |
| `ScoreShowResult` | `.report` |
| `ScoreValidateResult` | `.report`, `.is_valid` |
| `ScoreCompareResult` | `.report` |

Existing `payload`/`passed` attributes unchanged (non-breaking).

### Shared Source File Collector

New `mcp_server.utils.source_files` module:
- `collect_source_files()` — handles both MD and YAML, excludes derived copies and templates
- `is_yaml_document()` — extension check utility
- Used by validation runner; consistency and remediation runners use updated internal logic

### Tests

24 new tests (187 total):
- `test_source_files.py` (7): shared collector
- `test_yaml_parity.py` (9): consistency, next_action, scoring YAML support
- `test_api_aliases.py` (8): result class property aliases

## Backward Compatibility

- Scoring: old reports without `structural_errors` use original formula
- API aliases: existing `payload`/`passed` attributes unchanged
- All 163 existing tests pass without modification
