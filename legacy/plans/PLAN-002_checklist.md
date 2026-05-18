# PLAN-002 Implementation Checklist

**Plan**: PLAN-002_mcp_ucx_template_naming_migration.md
**Status**: Complete
**Date**: 2026-03-29

---

## Pre-Flight

- [ ] Run baseline tests — confirm current pass count
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ -v --tb=short 2>&1 | tail -5
  ```
- [ ] Record baseline: `___` passed, `___` failed

---

## Phase 1: Resolution Helper

- [ ] Create `src/mcp_server/utils/__init__.py` (empty file)
- [ ] Create `src/mcp_server/utils/template_naming.py` with:
  - [ ] `resolve_template_path(layer_dir, artifact, suffix)` — tries `{ARTIFACT}-TEMPLATE{suffix}` then `{ARTIFACT}-MVP-TEMPLATE{suffix}`
  - [ ] `load_tuned_template(doc_type, loader_fn, **kwargs)` — tries `.yaml`, `.md`, `-MVP-.md` in order
- [ ] Verify import works:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -c "from mcp_server.utils.template_naming import resolve_template_path, load_tuned_template; print('OK')"
  ```

---

## Phase 2: Source File Changes

### 2.1 validation/runner.py

- [ ] Add import: `from mcp_server.utils.template_naming import resolve_template_path`
- [ ] Line 91: Replace `template_path = template_root / layer / f"{artifact}-MVP-TEMPLATE.yaml"` with:
  ```python
  template_path = resolve_template_path(template_root / layer, artifact, ".yaml")
  ```
- [ ] Line 92: Update `if not template_path.exists():` to `if template_path is None:`
- [ ] Run: `python -m pytest tests/unit/test_validation_runner.py -v --tb=short`

### 2.2 skills/scaffold.py

- [ ] Line 77: Change `"-MVP-TEMPLATE" not in` to `"-TEMPLATE" not in`
- [ ] Run: `python -m pytest tests/unit/test_scaffold_init.py -v --tb=short`

### 2.3 skills/project_ucx_loader.py

- [ ] Line 88: Change `"-MVP-TEMPLATE" in` to `"-TEMPLATE" in`
- [ ] Run: `python -m pytest tests/unit/test_project_ucx_loader.py -v --tb=short`

### 2.4 prompts/context_builder.py

- [ ] Add import: `from mcp_server.utils.template_naming import load_tuned_template`
- [ ] Line 91: `*-MVP-TEMPLATE.*` → `*-TEMPLATE.*`
- [ ] Line 100: `*-MVP-TEMPLATE.*` → `*-TEMPLATE.*`
- [ ] Line 364 (docstring): `*-MVP-TEMPLATE.*` → `*-TEMPLATE.*`
- [ ] Line 409 (comment): `(MVP template + schema)` → `(template + schema)`
- [ ] Lines 414-421: Replace entire try/except block with:
  ```python
  document_template_text = load_tuned_template(
      doc_type=doc_type,
      loader_fn=load_project_document_template,
      project_root=project_root,
  )
  ```
- [ ] Run: `python -m pytest tests/integration/test_creation_prompt_builder.py tests/integration/test_prompt_context_builder.py -v --tb=short`

### 2.5 review/runner.py

- [ ] Line 176: Rename `mvp_template_name` → `template_name`
- [ ] Line 177: Change `"-MVP-TEMPLATE" in name` → `"-TEMPLATE" in name`
- [ ] Line 180: Update variable to `template_name`
- [ ] Line 181: Update error message: `"No layer template asset found for final artifact creation"`
- [ ] Lines 182-183: Update `mvp_template_name` → `template_name`
- [ ] Run: `python -m pytest tests/unit/test_review_runner.py -v --tb=short`

### Phase 2 Gate

- [ ] All 5 source files modified
- [ ] No remaining `-MVP-TEMPLATE` in source files (verify):
  ```bash
  grep -rn 'MVP-TEMPLATE' src/mcp_server/ | grep -v __pycache__ | grep -v '_MVP_SCHEMA' | grep -v 'CREATION_RULES\|VALIDATION_RULES'
  ```
  Expected: 0 matches (only `_MVP_CREATION_RULES` and `_MVP_VALIDATION_RULES` deprecation notes survive)

---

## Phase 3: Template Copies

- [ ] Copy unified BRD template:
  ```bash
  cp /opt/data/ucx_framework/ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml /opt/data/ucx_framework/mcp_ucx/templates/BRD-TEMPLATE.yaml
  ```
- [ ] Verify old template still exists (backward compat):
  ```bash
  ls /opt/data/ucx_framework/mcp_ucx/templates/BRD-MVP-TEMPLATE.md
  ```
- [ ] Verify non-BRD templates unchanged:
  ```bash
  ls /opt/data/ucx_framework/mcp_ucx/templates/PRD-MVP-TEMPLATE.md
  ```

---

## Phase 4: Test Fixture Updates

For each test file: update BRD-specific fixtures only. Leave non-BRD fixtures unchanged.

- [ ] `tests/unit/test_validation_runner.py` — BRD template fixture names
- [ ] `tests/unit/test_scaffold_init.py` — BRD template fixture names
- [ ] `tests/unit/test_project_ucx_loader.py` — BRD asset filter assertions
- [ ] `tests/unit/test_review_runner.py` — BRD template fixture names
- [ ] `tests/unit/test_cli_main.py` — BRD fixture names
- [ ] `tests/integration/test_creation_prompt_builder.py` — BRD fixture names and assertions
- [ ] `tests/integration/test_prompt_context_builder.py` — BRD fixture and assertion
- [ ] `tests/integration/test_migration_flows.py` — schema reference

### Phase 4 Gate

- [ ] Run full test suite:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ -v --tb=short
  ```
- [ ] Compare pass count to baseline: `___` passed (should be >= baseline)

---

## Phase 5: Migration Tests

Add 4 new tests to `tests/unit/test_validation_runner.py`:

- [ ] Test: new name only (`BRD-TEMPLATE.yaml` exists) → found
- [ ] Test: old name only (`BRD-MVP-TEMPLATE.yaml` exists) → found
- [ ] Test: both exist → new name takes precedence
- [ ] Test: non-BRD layer (`PRD-MVP-TEMPLATE.yaml`) → still works

### Phase 5 Gate

- [ ] Run migration tests:
  ```bash
  python -m pytest tests/unit/test_validation_runner.py -k "template_naming" -v
  ```
- [ ] All 4 new tests pass

---

## Phase 6: Documentation

- [ ] Update `docs/architecture/MCP_OPERATIONAL_FLOWS.md`:
  - [ ] Replace `*-MVP-TEMPLATE.*` references with `*-TEMPLATE.*`
  - [ ] Add note about backward compatibility with old naming

---

## Final Validation

- [ ] Full test suite passes:
  ```bash
  cd /opt/data/ucx_framework/mcp_ucx && python -m pytest tests/ -v --tb=short
  ```
- [ ] Final count: `___` passed, `___` failed
- [ ] No regressions (final >= baseline)
- [ ] No `"-MVP-TEMPLATE"` in source files:
  ```bash
  grep -rn 'MVP-TEMPLATE' src/mcp_server/ | grep -v __pycache__ | grep -v '_MVP_SCHEMA'
  ```
  Expected: only `_MVP_CREATION_RULES` and `_MVP_VALIDATION_RULES` deprecation notes (lines 94, 104 in context_builder.py)
- [ ] BRD template resolves correctly:
  ```bash
  python -c "
  from pathlib import Path
  from mcp_server.utils.template_naming import resolve_template_path
  p = resolve_template_path(Path('ai_dev_ssd_flow/01_BRD'), 'BRD', '.yaml')
  print(f'Resolved: {p}')
  assert p is not None and 'BRD-TEMPLATE.yaml' in str(p)
  print('PASS')
  "
  ```

---

## Post-Implementation

- [ ] Update changelog if needed
- [ ] Mark PLAN-002 status as Complete
- [ ] Delete this checklist (temporary execution checklist)
