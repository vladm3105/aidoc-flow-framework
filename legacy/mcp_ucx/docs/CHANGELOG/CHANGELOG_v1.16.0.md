# CHANGELOG — UCX v1.16.0

**Release Date**: 2026-04-05
**Plan**: PLAN-026 (Persona management tools)

## Summary

Add persona management MCP tools and CLI commands for inspecting and modifying project-specific persona-to-layer mappings. Add `--update` mode to `sdd_init` for syncing stale project UCX files. Demote `executive_summary` to optional in BRD template. Rewrite BRD-XS-004 validation rule to use authoritative sections.

## New

### Persona Management Tools (3 MCP tools + 3 CLI commands)

| MCP Tool | CLI Command | Purpose |
|----------|-------------|---------|
| `sdd_personas_show` | `personas-show` | Display persona assignments per phase/doctype |
| `sdd_personas_set` | `personas-set` | Update persona list for a phase+doctype with validation |
| `sdd_personas_diff` | `personas-diff` | Compare project mappings against framework defaults |

**New file**: `mcp_ucx/src/mcp_server/skills/persona_manager.py`

CLI usage:

```bash
mcp personas-show --project /path [--phase creation] [--doc-type brd] [--format text|json]
mcp personas-set --project /path --phase creation --doc-type brd --personas architect auditor
mcp personas-diff --project /path [--format text|json]
```

### Scaffold Update Mode

`sdd_init` now supports `--update` to sync stale project UCX files with framework source:

| Flag | Behavior |
|------|----------|
| (none) | Create missing files only (existing behavior) |
| `--update` | Overwrite stale templates/prompts. Protects `persona_mappings.yaml` |
| `--update --update-mappings` | Also reset `persona_mappings.yaml` to framework defaults |

MCP tool equivalents: `sdd_init(update=true)`, `sdd_init(update=true, update_mappings=true)`

**Protected files**: `persona_mappings.yaml` is project-owned after init. The `PROTECTED_PROJECT_FILES` set in `scaffold.py` prevents accidental overwrites during `--update`. Result now reports `protected_paths` alongside `created_paths`, `skipped_paths`, `updated_paths`.

### Preflight Persona Health Check

`sdd_preflight` now checks persona mapping integrity when `context` includes review/remediate:
- Verifies all referenced persona `.md` files exist
- Reports missing doctypes compared to framework defaults
- Returns `persona_mapping_health` key in checks: `ok` | `warning` | `error`

## Changed

### BRD Template: `executive_summary` Demoted to Optional

**File**: `ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml`

`executive_summary` is now `required: false`. It is a derived section that can be generated on demand from authoritative sections (`business_objectives`, `stakeholders`, `project_scope`). Not consumed by downstream prompts or validation rules.

### BRD-XS-004: Entity Consistency Rule Rewritten

**File**: `mcp_ucx/src/mcp_server/validation/brd_rules.py`

| Aspect | Before | After |
|--------|--------|-------|
| Entity source | `executive_summary.key_stakeholders`, `executive_summary.business_problem` | Top-level `stakeholders` (partner roles only), `business_objectives.problem_statement.current_workarounds` |
| Search corpus | `functional_requirements`, `stakeholders`, `introduction` | `functional_requirements`, `introduction`, `project_scope` |
| Filtering | All names extracted | Only organizational entities (partner/vendor roles); excludes individual person names |

### Remediation Runner: `executive_summary` Removed from Required Keys

**File**: `mcp_ucx/src/mcp_server/remediation/runner.py`

BRD required top-level keys changed from `["document_control", "executive_summary", "functional_requirements"]` to `["document_control", "functional_requirements"]`.

## Files Changed

| File | Change |
|------|--------|
| `mcp_ucx/src/mcp_server/skills/persona_manager.py` | **New** — show, set, diff, health check |
| `mcp_ucx/src/mcp_server/skills/scaffold.py` | Add `--update` / `--update-mappings` modes, `PROTECTED_PROJECT_FILES` |
| `mcp_ucx/src/mcp_server/skills/__init__.py` | Export 4 persona_manager functions |
| `mcp_ucx/src/mcp_server/tool_registry.py` | 3 new Tool defs + dispatch blocks (22 tools total) |
| `mcp_ucx/src/mcp_server/preflight/runner.py` | Persona mapping health check integration |
| `mcp_ucx/src/mcp_server/cli/main.py` | 3 subcommands + init flags + formatting helpers |
| `mcp_ucx/src/mcp_server/validation/brd_rules.py` | BRD-XS-004 rewritten |
| `mcp_ucx/src/mcp_server/remediation/runner.py` | Remove executive_summary from BRD required keys |
| `ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml` | executive_summary: required: false |
| `mcp_ucx/tests/unit/test_persona_manager.py` | **New** — 14 tests |
| `mcp_ucx/tests/unit/test_scaffold_init.py` | +3 tests (update, protected, update-mappings) |
| `mcp_ucx/tests/unit/test_brd_rules.py` | Updated entity consistency tests |
| `mcp_ucx/tests/unit/test_preflight_runner.py` | +1 health check test |
| `mcp_ucx/tests/unit/test_server.py` | Tool count 19→22 |

## Fixed (Post-Review)

### `show_persona_mappings` cache safety

`show_persona_mappings` returned shallow copies of cached mapping dicts. A caller mutating the return value could corrupt the mtime-based cache. Fixed: `copy.deepcopy()` on returned phase/entry data.

### `diff_persona_mappings` mode comparison

`diff_persona_mappings` only compared `personas` lists, ignoring `mode` changes (e.g., `sequential` → `parallel`). Fixed: diff now compares `mode` field and includes `project_mode`/`default_mode` in changed entries when they differ.

## Backward Compatibility

- `sdd_init` without flags behaves identically to before
- BRD documents with `executive_summary` continue to validate (field is optional, not removed)
- Existing `persona_mappings.yaml` files are not affected; new tools are additive
- BRD-XS-004 may produce different results for documents that previously relied on `executive_summary` for entity extraction

## Test Coverage

295 tests pass. New tests: 14 (persona_manager) + 3 (scaffold update) + 1 (preflight health) + 3 (BRD rules).
