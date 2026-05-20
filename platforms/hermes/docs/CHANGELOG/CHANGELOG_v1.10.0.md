# CHANGELOG v1.10.0

**Release Date**: 2026-04-02
**Type**: Minor (UCX Root Relocation)
**Plan**: [PLAN-020](../plans/PLAN-020_ucx_root_relocation.md)

## Summary

Relocates UCX operational infrastructure from `{project}/docs/UCX/` to `{project}/UCX/`. Separates tooling (personas, prompts, templates, logs) from SDD documentation artifacts. Includes backward-compatible fallback and auto-migration.

## Changes

### Path Relocation

All UCX paths changed from `docs/UCX/` to `UCX/`:
- `UCX/skills/personas/` — persona files
- `UCX/prompts/templates/` — creation, review, remediation templates
- `UCX/templates/` — document templates and layer assets
- `UCX/logs/` — structured logging output

### Centralized Resolver

New `resolve_ucx_root(project_root)` function checks `UCX/` first, falls back to `docs/UCX/` for backward compatibility. All modules use this resolver — no hardcoded paths.

### Auto-Migration

`sdd_init` automatically detects `docs/UCX/` and moves it to `UCX/` when the new location doesn't exist. Preserves all files including custom modifications.

### Scope

- 8 source files updated (~40 path references)
- 6 unit test files updated (~30 references)
- 3 integration test files updated (~29 references)
- 8 documentation files updated (~20 references)
- 2 projects migrated (ucx_framework, b-local-docs)

### Tests

All 205 unit tests + 51 integration tests pass. Zero regressions.

## Backward Compatibility

- `resolve_ucx_root()` checks both locations — existing projects with `docs/UCX/` continue to work
- `sdd_init` auto-migrates on next invocation
- Logging falls back to `docs/UCX/logs/` if `UCX/` parent doesn't exist
