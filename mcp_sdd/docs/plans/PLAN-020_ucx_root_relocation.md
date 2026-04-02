# PLAN-020: Relocate UCX from docs/UCX to project root UCX/

## Context

UCX (Unified Context) contains operational infrastructure — personas, prompt templates, layer templates, logs. It is not an SDD documentation artifact. Having it under `docs/` mixes tooling with deliverables (BRD, PRD, EARS, etc.).

**Goal**: Move `{project}/docs/UCX/` → `{project}/UCX/` across mcp_sdd codebase and all scaffolded projects.

**Status**: Implemented (2026-04-02, mcp_sdd v1.10.0 / framework v0.17.0)

**Type**: Breaking change — required migration of existing scaffolded projects.

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

## Scope: Full Reference Audit

Grep of `docs/UCX` across the entire mcp_sdd codebase: **~100 references across 22 files**.

### Source files (8 files, ~40 references)

| File | Refs | Change |
|------|------|--------|
| `skills/project_ucx_loader.py` | 8 | Central path constants + all path functions → use `_resolve_ucx_root()` |
| `skills/scaffold.py` | 7 | Scaffold destination paths → use `_resolve_ucx_root()` |
| `logging_config.py` | 2 | `_LOG_SUBDIR` → use `_resolve_ucx_root()` from loader |
| `preflight/runner.py` | 1 | Hardcoded `project_root / "docs/UCX"` → use `_resolve_ucx_root()` |
| `prompts/context_builder.py` | 2 | Docstring path references |
| `cli/main.py` | 12 | Help text strings (`--project` descriptions) |
| `tool_registry.py` | 2 | Tool description strings |
| **Total source** | **34** | |

### Unit test files (6 files, ~30 references)

| File | Refs |
|------|------|
| `tests/unit/test_project_ucx_loader.py` | 10 |
| `tests/unit/test_scaffold_init.py` | 6 |
| `tests/unit/test_review_runner.py` | 8 |
| `tests/unit/test_cli_main.py` | 3 |
| `tests/unit/test_validation_runner.py` | 3 |
| **Total unit tests** | **30** |

### Integration test files (3 files, ~25 references)

| File | Refs |
|------|------|
| `tests/integration/test_prompt_context_builder.py` | 15 |
| `tests/integration/test_migration_flows.py` | 2 |
| `tests/integration/test_creation_prompt_builder.py` | 12 |
| **Total integration tests** | **29** |

### Documentation files (7+ files, ~10 references)

| File | Change |
|------|--------|
| `docs/architecture/MCP_RUNTIME_ARCHITECTURE.md` | Path references |
| `docs/architecture/MCP_CLI_REFERENCE.md` | Path references |
| `docs/architecture/MCP_OPERATOR_RUNBOOK.md` | Path references |
| `docs/architecture/MCP_OPERATIONAL_FLOWS.md` | Path references |
| `docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md` | Path references |
| `docs/architecture/MCP_PERSONA_DESIGN_GUIDE.md` | Path references |
| `docs/specs/SPEC-006_mcp_creation_flow_operational_contracts.md` | Path references |
| `docs/plans/PLAN-017_executor_output_and_logging.md` | Path references |
| `docs/README.md` | Path references |

---

## Backward Compatibility

### Centralized path resolver

Add `_resolve_ucx_root()` to `project_ucx_loader.py`. **All modules** must use this function — no hardcoded `docs/UCX` paths anywhere:

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

Modules that currently hardcode paths:
- `project_ucx_loader.py` — all path functions (persona, template, layer assets)
- `scaffold.py` — scaffold destination
- `logging_config.py` — log directory
- `preflight/runner.py` — UCX existence check
- `_REQUIRED_PATHS` constant in loader — validation paths

### Auto-migration in `sdd_init`

Add migration logic to `scaffold.py`:

```python
def _migrate_legacy_ucx(project_root: Path) -> bool:
    """If docs/UCX exists and UCX/ doesn't, move it. Returns True if migrated."""
    legacy = project_root / "docs" / "UCX"
    new = project_root / "UCX"
    if legacy.exists() and not new.exists():
        shutil.move(str(legacy), str(new))
        return True
    return False
```

Called at the start of `scaffold_project_ucx()` before creating new files.

---

## Implementation Order

1. Add `_resolve_ucx_root()` to `project_ucx_loader.py`
2. Refactor all path functions in `project_ucx_loader.py` to use resolver
3. Update `_REQUIRED_PATHS` constant to be dynamic (computed from resolver)
4. Update `scaffold.py` — destination paths + auto-migration
5. Update `logging_config.py` — use resolver instead of hardcoded `_LOG_SUBDIR`
6. Update `preflight/runner.py` — use resolver
7. Update `prompts/context_builder.py` — docstrings
8. Update `cli/main.py` — help text strings
9. Update `tool_registry.py` — tool description strings
10. Run unit tests — fix all 6 unit test files (30 path references)
11. Run integration tests — fix all 3 integration test files (29 path references)
12. Run full test suite — all must pass
13. Update 9 documentation files
14. Add `.gitignore` entries for `UCX/logs/` in project templates
15. Migrate existing projects:
    - `/opt/data/docs_flow_framework/`: `mv docs/UCX UCX`
    - `/opt/data/b-local/b-local-docs/`: `mv docs/UCX UCX`
16. Smoke test: `sdd_init` on fresh project → creates `UCX/` at root
17. Smoke test: `sdd_init` on project with `docs/UCX/` → auto-migrates to `UCX/`
18. Smoke test: `sdd_validate`, `sdd_review`, `sdd_remediate` against migrated project
19. Create mcp_sdd CHANGELOG v1.10.0 and ROADMAP entry
20. Create framework CHANGELOG v0.17.0 and ROADMAP entry
21. Update READMEs

---

## Verification

1. `python -m pytest mcp_sdd/tests/unit/ -v` — all pass
2. `python -m pytest mcp_sdd/tests/integration/ -v` — all pass
3. `grep -r "docs/UCX" mcp_sdd/src/` returns 0 results (no hardcoded paths)
4. `grep -r "docs/UCX" mcp_sdd/tests/` returns 0 results
5. `sdd_init` on fresh project → creates `UCX/` at root (not `docs/UCX/`)
6. `sdd_init` on project with `docs/UCX/` → auto-migrates, logs migration
7. Logging writes to `UCX/logs/mcp_sdd.log`
8. Existing projects with `docs/UCX/` still work via fallback resolver (before migration)
9. After migration, all tools work against `UCX/`
10. Full pipeline (`validate → validate_fix → review → remediate → remediate_fix`) works on migrated project

---

## Risks

| Risk | Mitigation |
|------|-----------|
| Breaking existing projects | Fallback resolver checks both locations; auto-migration on `sdd_init` |
| ~100 references across 22 files | Systematic grep + replace; test coverage verifies each path |
| Integration tests with hardcoded paths | Fix all 29 references; run integration suite |
| Auto-migration race condition | Check `not new.exists()` before move; `shutil.move` is atomic on same filesystem |
| `.gitignore` stale entries | Add new entries alongside old (both `UCX/logs/` and `docs/UCX/logs/`) during transition |
| Third-party tools expecting docs/UCX | None known; UCX is internal to mcp_sdd |

---

## Out of Scope

- Claude `doc-*` skills path updates — separate scope
- Other projects beyond docs_flow_framework and b-local-docs
