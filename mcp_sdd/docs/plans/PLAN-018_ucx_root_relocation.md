# PLAN-018: Relocate UCX from docs/UCX to project root UCX/

## Context

UCX (Unified Context) contains operational infrastructure — personas, prompt templates, layer templates, logs. It is not an SDD documentation artifact. Having it under `docs/` mixes tooling with deliverables (BRD, PRD, EARS, etc.).

**Goal**: Move `{project}/docs/UCX/` → `{project}/UCX/` across mcp_sdd codebase and all scaffolded projects.

**Status**: Planned (implement after mcp_sdd testing complete)

**Type**: Breaking change — requires migration of existing scaffolded projects.

---

## Rationale

| Factor | `docs/UCX/` (current) | `UCX/` (proposed) |
|--------|----------------------|-------------------|
| Semantic clarity | Mixed with SDD artifacts | Clear separation: tooling vs docs |
| Path simplicity | `docs/UCX/logs/mcp_sdd.log` | `UCX/logs/mcp_sdd.log` |
| .gitignore | Nested ignore rules | Simple root-level ignores |
| Convention alignment | Diverges from `.claude/`, `.mcp.json` | Matches root-level config pattern |
| Discovery | Hidden in docs tree | Visible at project root |

---

## Scope

### mcp_sdd code changes

| File | Change | Lines Est. |
|------|--------|-----------|
| `mcp_sdd/src/mcp_server/skills/project_ucx_loader.py` | Change `docs/UCX/` → `UCX/` in all path constants | ~10 |
| `mcp_sdd/src/mcp_server/skills/scaffold.py` | Update scaffold target directory | ~5 |
| `mcp_sdd/src/mcp_server/logging_config.py` | Change `_LOG_SUBDIR = "docs/UCX/logs"` → `"UCX/logs"` | 1 |
| `mcp_sdd/src/mcp_server/cli/main.py` | Update any hardcoded `docs/UCX` references | ~3 |
| `mcp_sdd/src/mcp_server/tool_registry.py` | Verify no hardcoded paths (uses loader) | 0 |

### Test changes

| File | Change |
|------|--------|
| `mcp_sdd/tests/unit/test_server.py` | Update scaffold assertions if any reference `docs/UCX` |
| Any test with `docs/UCX` fixtures | Update paths |

### Documentation changes

| File | Change |
|------|--------|
| `mcp_sdd/docs/README.md` | Update UCX path references |
| `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md` | Update path references |
| `mcp_sdd/docs/architecture/MCP_OPERATOR_RUNBOOK.md` | Update path references |
| `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md` | Update path references |

### Existing project migration

For each scaffolded project:

```bash
# Migration command per project
mv {project}/docs/UCX {project}/UCX
```

Known projects to migrate:
- `/opt/data/docs_flow_framework/` (framework itself)
- `/opt/data/b-local/b-local-docs/` (b-local)

### Backward compatibility

Add a fallback check in `project_ucx_loader.py`:

```python
def _resolve_ucx_root(project_root: Path) -> Path:
    """Resolve UCX directory, supporting both new and legacy locations."""
    new_path = project_root / "UCX"
    if new_path.exists():
        return new_path
    legacy_path = project_root / "docs" / "UCX"
    if legacy_path.exists():
        return legacy_path
    return new_path  # default to new location for scaffolding
```

This allows existing projects to work during transition without immediate migration.

---

## Implementation Order

1. Add `_resolve_ucx_root()` fallback to `project_ucx_loader.py`
2. Update `scaffold.py` to create `UCX/` at project root
3. Update `logging_config.py` log subdirectory
4. Update `cli/main.py` references
5. Run tests — verify all pass
6. Update mcp_sdd documentation
7. Migrate existing projects (`mv docs/UCX UCX`)
8. Smoke test against migrated projects

---

## Verification

1. `python -m pytest mcp_sdd/tests/unit/ -v` — all pass
2. `sdd_init` creates `UCX/` at root (not `docs/UCX/`)
3. Logging writes to `UCX/logs/mcp_sdd.log`
4. Existing projects with `docs/UCX/` still work (fallback)
5. After migration, projects use `UCX/` exclusively

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Breaking existing projects | Fallback resolver checks both locations |
| Docs referencing old paths | grep + update in implementation |
| Third-party tools expecting docs/UCX | None known; UCX is internal to mcp_sdd |
