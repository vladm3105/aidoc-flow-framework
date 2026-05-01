# PLAN-002: MCP SDD Template Naming Migration

**Status**: Complete
**Created**: 2026-03-29
**Scope**: Update mcp_ucx server to support unified `{ARTIFACT}-TEMPLATE.yaml` naming
**Trigger**: BRD layer refactored from dual-file to single YAML template (v0.2.0)
**Risk**: Low — substring broadening is mechanically safe; fallback preserves backward compat

---

## Problem

The mcp_ucx server hardcodes `"-MVP-TEMPLATE"` suffix in 5 source files (10 occurrences). BRD was migrated to `BRD-TEMPLATE.yaml` (no "-MVP-" prefix). Other layers (PRD, EARS, ADR, etc.) still use old naming. The fix must support both conventions with new-name-first resolution.

## Design Decision

**Approach**: Broaden substring matching from `"-MVP-TEMPLATE"` to `"-TEMPLATE"`.

`"-TEMPLATE"` is a substring of `"-MVP-TEMPLATE"`, so the broadened check matches both old and new filenames without extra logic. For path construction (where a specific file is built, not filtered), use try-new-then-fallback-old pattern.

No other files in layer directories contain `"-TEMPLATE"` outside of template files, so this is safe.

**Schema handling**: BRD no longer has a separate `_MVP_SCHEMA.yaml`. The `_MVP_SCHEMA.yaml` filter in scaffold.py and project_ucx_loader.py remains unchanged — when no schema file exists for a layer, fewer assets are loaded, which is correct behavior. Schema is optional at Layer 1.

---

## Phase 1: Resolution Helper

Create new package `src/mcp_server/utils/`:

```
src/mcp_server/utils/__init__.py          # empty
src/mcp_server/utils/template_naming.py   # resolution helper
```

```python
# template_naming.py
from pathlib import Path

def resolve_template_path(layer_dir: Path, artifact: str, suffix: str) -> Path | None:
    """Try unified name first, fall back to MVP name."""
    for pattern in (f"{artifact}-TEMPLATE{suffix}", f"{artifact}-MVP-TEMPLATE{suffix}"):
        path = layer_dir / pattern
        if path.exists():
            return path
    return None

def load_tuned_template(doc_type: str, loader_fn, **loader_kwargs) -> str | None:
    """Try unified template name first, fall back to MVP name.

    Searches in order: .yaml (unified), .md (unified), .md (MVP legacy).

    Args:
        doc_type: Document type (e.g., "brd")
        loader_fn: Function that loads template by name (raises FileNotFoundError if missing)
        **loader_kwargs: Additional kwargs passed to loader_fn
    Returns:
        Template content string, or None if neither name exists.
    """
    for suffix in ("-TEMPLATE.yaml", "-TEMPLATE.md", "-MVP-TEMPLATE.md"):
        name = f"{doc_type.upper()}{suffix}"
        try:
            return loader_fn(template_name=name, **loader_kwargs)
        except FileNotFoundError:
            continue
    return None
```

---

## Phase 2: Fix 5 Source Files (10 occurrences)

### 2.1 validation/runner.py — line 91

**Current**: `template_path = template_root / layer / f"{artifact}-MVP-TEMPLATE.yaml"`

**Fix**: Use `resolve_template_path(template_root / layer, artifact, ".yaml")`.
Handle `None` return with existing error message.

### 2.2 skills/scaffold.py — line 77

**Current**: `if "-MVP-TEMPLATE" not in source_file.name and not source_file.name.endswith("_MVP_SCHEMA.yaml")`

**Fix**: Change to `if "-TEMPLATE" not in source_file.name and not source_file.name.endswith("_MVP_SCHEMA.yaml")`.

`"-TEMPLATE"` matches both `BRD-TEMPLATE.yaml` and `PRD-MVP-TEMPLATE.md`.
`_MVP_SCHEMA.yaml` filter unchanged — schema files are optional per layer.

### 2.3 skills/project_ucx_loader.py — line 88

**Current**: `if "-MVP-TEMPLATE" in file_path.name or file_path.name.endswith("_MVP_SCHEMA.yaml")`

**Fix**: Change to `if "-TEMPLATE" in file_path.name or file_path.name.endswith("_MVP_SCHEMA.yaml")`.

### 2.4 prompts/context_builder.py — 6 occurrences

**Line 91** (instructional string):
  Current: `*-MVP-TEMPLATE.*`
  Fix: `*-TEMPLATE.*`

**Line 92** (instructional string):
  `*_MVP_SCHEMA.yaml` — unchanged (schema still uses this name for layers that have it)

**Line 100** (instructional string):
  Current: `*-MVP-TEMPLATE.*`
  Fix: `*-TEMPLATE.*`

**Line 101** (instructional string):
  `*_MVP_SCHEMA.yaml` — unchanged

**Line 364** (docstring):
  Current: `Layer assets (*-MVP-TEMPLATE.* and *_MVP_SCHEMA.yaml files)`
  Fix: `Layer assets (*-TEMPLATE.* and *_MVP_SCHEMA.yaml files)`

**Line 409** (comment):
  Current: `# Authoritative SSD layer assets (MVP template + schema) copied during scaffold`
  Fix: `# Authoritative SSD layer assets (template + schema) copied during scaffold`

**Line 414** (path construction):
  Current: `tuned_template_name = f"{doc_type.upper()}-MVP-TEMPLATE.md"`
  Fix: Use `load_tuned_template()` helper with the existing `load_project_document_template` function:
  ```python
  document_template_text = load_tuned_template(
      doc_type=doc_type,
      loader_fn=load_project_document_template,
      project_root=project_root,
  )
  ```
  This replaces lines 414-421 (the try/except block).

### 2.5 review/runner.py — lines 176-183

**Current**:
```python
mvp_template_name = next(
    (name for name in creation_result.layer_asset_names if "-MVP-TEMPLATE" in name),
    None,
)
if mvp_template_name is None:
    raise ValueError("No layer MVP template asset found for final artifact creation")
final_content = creation_result.layer_assets[mvp_template_name]
template_source = f"layer_asset:{mvp_template_name}"
```

**Fix**:
- Line 177: Change filter to `"-TEMPLATE" in name`
- Line 176: Rename variable `mvp_template_name` → `template_name`
- Line 180-181: Update variable name and error message: `"No layer template asset found..."`
- Lines 182-183: Update variable references

Note: The dict lookup on line 182 works correctly because `load_project_layer_assets()`
stores assets by actual filename — the broadened filter in project_ucx_loader.py (2.3)
ensures the correct filename key is used regardless of naming convention.

---

## Phase 3: Update Template Copies

Directory: `/opt/data/ucx_framework/mcp_ucx/templates/`

- Copy `ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml` to `mcp_ucx/templates/BRD-TEMPLATE.yaml`
- Keep `mcp_ucx/templates/BRD-MVP-TEMPLATE.md` temporarily (scaffold may reference it for projects not yet migrated)
- Leave other layer templates (`PRD-MVP-TEMPLATE.md`, etc.) unchanged

---

## Phase 4: Fix Test Files

For BRD-specific test fixtures, update filenames from `BRD-MVP-TEMPLATE.yaml` to `BRD-TEMPLATE.yaml`. Leave non-BRD fixtures unchanged.

| Test File | BRD Fixtures to Update |
|-----------|----------------------|
| `tests/unit/test_validation_runner.py` | BRD template/schema fixture names |
| `tests/unit/test_scaffold_init.py` | BRD template fixture names |
| `tests/unit/test_project_ucx_loader.py` | BRD asset filter assertions |
| `tests/unit/test_review_runner.py` | BRD template fixture names |
| `tests/unit/test_cli_main.py` | BRD fixture names |
| `tests/integration/test_creation_prompt_builder.py` | BRD fixture names and assertions |
| `tests/integration/test_prompt_context_builder.py` | BRD fixture and assertion |
| `tests/integration/test_migration_flows.py` | Schema reference |

---

## Phase 5: Migration Tests

Add to `tests/unit/test_validation_runner.py`:

1. **New name only**: `BRD-TEMPLATE.yaml` exists → found
2. **Old name only**: `BRD-MVP-TEMPLATE.yaml` exists → found (backward compat)
3. **Both exist**: new name takes precedence
4. **Non-BRD layer**: `PRD-MVP-TEMPLATE.yaml` → still works

---

## Phase 6: Documentation

Update `/opt/data/ucx_framework/mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md` to reflect both naming conventions.

---

## Instance Format Clarification

The **template** is YAML (`BRD-TEMPLATE.yaml`). BRD **instances** generated from this
template can be either `.yaml` or `.md` depending on project convention.

The validation runner's file discovery pattern (`r"^[A-Z]+-\d+_.+\.md$"` in runner.py
line 31) only matches `.md` files. This is unchanged in this plan — BRD instances remain
`.md` for now. If projects adopt YAML instances, the discovery pattern needs updating
in a separate change.

---

## Future Concerns (not in scope)

- `prompts/templates/creation/UCC_PROMPT_PRD.md` hardcodes `PRD-MVP-TEMPLATE.md` (lines 25, 342, 362). Will break when PRD migrates to unified naming. Address when PRD layer is refactored.
- `_MVP_SCHEMA.yaml` suffix remains unchanged. When layers drop separate schema files (as BRD did), the filter harmlessly finds nothing.
- File discovery pattern for YAML instances (runner.py line 31) — address when projects adopt YAML BRD instances.

---

## Validation

```bash
cd /opt/data/ucx_framework/mcp_ucx
python -m pytest tests/ -v
```

All 169+ existing tests must pass. New migration tests must pass.

---

## Files Changed

| File | Change Type |
|------|-------------|
| `src/mcp_server/utils/__init__.py` | NEW — empty package init |
| `src/mcp_server/utils/template_naming.py` | NEW — resolution helpers |
| `src/mcp_server/validation/runner.py` | MODIFY — use helper (1 line) |
| `src/mcp_server/skills/scaffold.py` | MODIFY — broaden filter (1 line) |
| `src/mcp_server/skills/project_ucx_loader.py` | MODIFY — broaden filter (1 line) |
| `src/mcp_server/prompts/context_builder.py` | MODIFY — 6 occurrences + fallback logic |
| `src/mcp_server/review/runner.py` | MODIFY — broaden filter (1 line) |
| `templates/BRD-TEMPLATE.yaml` | NEW — unified template copy |
| 8 test files | MODIFY — BRD fixture names |
| `docs/architecture/MCP_OPERATIONAL_FLOWS.md` | MODIFY — naming docs |

**Total**: 2 new files, 7 modified source files, 8 modified test files, 1 doc file.

---

## Rollback

Revert the 5 source file changes. The resolution helper's fallback guarantees old naming still works, so partial rollback is safe.
