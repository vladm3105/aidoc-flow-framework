# CHANGELOG v0.17.0

**Release Date**: 2026-04-02
**Type**: Minor (UCX Root Relocation)

## Summary

mcp_ucx v1.10.0: Relocates UCX from `docs/UCX/` to project root `UCX/`. Separates operational tooling from SDD documentation. Backward-compatible fallback + auto-migration.

## Changes

### mcp_ucx Server (v1.10.0)

- `resolve_ucx_root()`: centralized resolver with `UCX/` → `docs/UCX/` fallback
- `sdd_init`: auto-migrates `docs/UCX/` to `UCX/` on invocation
- 22 files updated (~100 path references)
- Logging: `UCX/logs/mcp_ucx.log`

### Projects Migrated

- ucx_framework: `docs/UCX/` → `UCX/`
- b-local-docs: `docs/UCX/` → `UCX/`

## References

- [PLAN-020](mcp_ucx/docs/plans/PLAN-020_ucx_root_relocation.md)
- [mcp_ucx CHANGELOG v1.10.0](mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.10.0.md)
