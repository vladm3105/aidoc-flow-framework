# PLAN-030: Versioned Remediation Copies (`_remediate_v{N}`)

**Status**: Complete (2026-04-07)

## Context

The remediation fix pipeline currently creates `{stem}_remediate_copy.{ext}` — overwriting on each run. This prevents iterative remediation where each pass builds on the previous. The fix introduces versioned naming: `_remediate_v1`, `_remediate_v2`, etc., preserving all iterations. Previous versions are never overwritten.

> **Coordination with PLAN-031**: This plan covers versioned naming only. The `--fix` auto-chain and `sdd_remediate_fix` tool absorption into `sdd_remediate` are handled by PLAN-031. Execute PLAN-030 first, then PLAN-031.

## Naming Convention

```
First run:   BRD-05_multi_agent_ai_system_remediate_v1.yaml
Second run:  BRD-05_multi_agent_ai_system_remediate_v2.yaml  (source: v1)
Third run:   BRD-05_multi_agent_ai_system_remediate_v3.yaml  (source: v2)
```

## Implementation Phases

### Phase 1: Core Engine — `mcp_ucx/src/mcp_server/remediation/runner.py`

**1a. Add helpers** (insert after `_canonical_stem`, ~line 779):
- `_REMEDIATE_VERSION_RE = re.compile(r"_remediate_v(\d+)")`
- `_next_remediate_version(canonical_stem, output_dir)` — scan output_dir for highest `_remediate_v{N}`, return N+1
  - IMPORTANT: Match with `path.stem.startswith(canonical_stem + "_remediate_v")` to avoid false matches on shared prefixes (e.g., `BRD-01_test` vs `BRD-01_test_extended`)

**1b. Update `_canonical_stem`** (~lines 773-779):
- Add regex strip for `_remediate_v\d+` suffix before the postfix loop
- Keep legacy `_remediate_copy` in the postfix loop for backward compat

**1c. Update `run_remediate_fix_build`** (~lines 976-979):
- Before `_apply_copy`, compute: `canon = _canonical_stem(effective_document_path)` for files, or `effective_document_path.name` for directories
- Compute `next_ver = _next_remediate_version(canon, output_dir)`
- Change suffix from `"remediate_copy"` to `f"remediate_v{next_ver}"`
- Add `"remediate_version": next_ver` to the report dict

**1d. Update filters** (~lines 121, 867):
- Add `and not _REMEDIATE_VERSION_RE.search(path.stem)` alongside existing `"_remediate_copy"` check

### Phase 2: Filter Updates — 4 secondary files

**`mcp_ucx/src/mcp_server/utils/source_files.py`**:
- Line ~27: `DERIVED_COPY_PATTERN` regex — add `remediate_v\d+` alternative
- Line ~31: `_DERIVED_STEMS` — ADD `"_remediate_v"` (substring match covers all vN), KEEP `"_remediate_copy"` for backward compat

**`mcp_ucx/src/mcp_server/validation/runner.py`**:
- Lines ~41, 64, 88, 98: Add `and not re.search(r"_remediate_v\d+", path.stem)` to each filter

**`mcp_ucx/src/mcp_server/tool_registry.py`**:
- Line ~529: Source file filter — add `_remediate_v\d+` exclusion
- Lines ~545-547: `has_remediated_copy` — also check for `_remediate_v\d+`

**`mcp_ucx/src/mcp_server/cli/main.py`**:
- Line ~320: Filter — add `_remediate_v\d+` exclusion

### Phase 3: Consistency Runner — `mcp_ucx/src/mcp_server/consistency/runner.py`

- Line ~77: Filter — add `_remediate_v\d+` exclusion
- Lines ~127-129: Replace hardcoded `_remediate_copy` path lookup with version-aware resolution:
  - Glob for `{stem}_remediate_v*{ext}`, sort by version number, pick highest
  - Fallback to legacy `_remediate_copy` if no versioned files exist

### Phase 4: `verify_remediation_quality` Fix — `tool_registry.py` lines ~1070-1083

When iterating (v1→v2), the quality check currently compares `original_path=document_path` (the base document) vs the new derived copy. For iterative runs where `document_path` is itself a `_remediate_v1` file, the comparison should be v1 vs v2, not original vs v2. The handler already passes `document_path` which in the iterative case IS the vN-1 file — verify this works correctly and add a test.

### ~~Phase 5~~ → Deferred to PLAN-031

> **Deferred**: The `--fix` auto-chain and full absorption of `sdd_remediate_fix` into `sdd_remediate` (including the new `remediation_report` parameter for direct-fix mode) are handled by PLAN-031 Phase 2. This avoids modifying the tool surface twice.
>
> PLAN-030 keeps `sdd_remediate_fix` as-is (standalone tool) but with versioned output. PLAN-031 then absorbs it into `sdd_remediate` with `fix=true`.

### Phase 6: Tests — 6 test files + new tests

**Update existing assertions:**

| File | Changes |
|------|---------|
| `tests/unit/test_remediation_runner.py` | Update `_remediate_copy` assertions to `_remediate_v1` |
| `tests/unit/test_source_files.py` | Add test for `_remediate_v1` exclusion (keep existing `_remediate_copy` test for backward compat) |
| `tests/unit/test_yaml_parity.py` | Update fixture filename to `_remediate_v1` |
| `tests/unit/test_server.py` | Update fixture filename to `_remediate_v1` |
| `tests/unit/test_cli_main.py` | Update fixture filename to `_remediate_v1` |
| `tests/integration/test_migration_flows.py` | Update assertion filename to `_remediate_v1` |

**New tests to add** (in `test_remediation_runner.py`):
1. **Version incrementing**: Run `run_remediate_fix_build` twice → verify both `_v1` and `_v2` exist, v1 not overwritten
2. **Iterative flow**: Pass `_remediate_v1` file as `document` to `run_remediate_fix_build` → produces `_v2` (canonical stem properly stripped)
3. **Directory-based versioning**: Run `run_remediate_fix_build` on directory twice → verify both `_remediate_v1/` and `_remediate_v2/` dirs exist
4. **Backward compat**: Pre-create `_remediate_copy` file → still excluded from source discovery, and `run_remediate_fix_build` creates `_v1` (not `_v2`)
5. **Prefix safety**: Two documents with shared prefix (`BRD-01_test`, `BRD-01_test_extended`) → version numbers independent

> **Note**: The `--fix` chain test (sdd_remediate with fix=true) is deferred to PLAN-031 Phase 3b.

### Phase 7: Documentation Updates

**Update (not historical changelogs):**
- `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md` (~line 270) — update `_remediate_copy` reference to `_remediate_v{N}`
- `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md` (~line 305) — update naming description

**Do NOT modify** (historical records):
- `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.11.0.md` — historical, leave as-is

**Add new CHANGELOG entry** for this feature (version TBD after implementation).

## Backward Compatibility

- All filters match BOTH `_remediate_copy` (legacy) AND `_remediate_v\d+` (new)
- `_canonical_stem` strips both patterns
- `_DERIVED_STEMS` contains both `"_remediate_copy"` and `"_remediate_v"`
- Consistency runner falls back to `_remediate_copy` when no versioned files exist
- Existing `_remediate_copy` files in user projects continue to be excluded from source discovery

## Known Limitations

- **Race condition**: If two concurrent `remediate_fix` calls target the same document, both could compute the same next version. Unlikely in CLI usage.
- **`_build_remediate_fix_prompt`** says "source is protected" — on iterative runs the "source" is the previous version, not the original document. Acceptable wording since the vN-1 file IS protected from mutation.

## Verification

1. Run existing tests: `cd mcp_ucx && python -m pytest tests/ -x -q`
2. Run `run_remediate_fix_build` twice on same document → verify both `_v1` and `_v2` exist
3. Verify `_canonical_stem("BRD-05_test_remediate_v3")` returns `"BRD-05_test"`
4. Verify legacy `_remediate_copy` files still excluded by filters
5. Verify prefix safety: `_next_remediate_version("BRD-01_test", dir)` does not count `BRD-01_test_extended_remediate_v1`

> **`--fix` chain verification** deferred to PLAN-031.

## Completion Evidence

- All 360 tests pass (`python -m pytest tests/ -x -q`)
- Phase 1: `_REMEDIATE_VERSION_RE`, `_next_remediate_version`, `_canonical_stem`, `run_remediate_fix_build` — all in `remediation/runner.py`
- Phase 2: Filters updated in `source_files.py`, `validation/runner.py`, `tool_registry.py`, `cli/main.py`
- Phase 3: Consistency runner version-aware resolution in `consistency/runner.py` lines 128-137
- Phase 4: `verify_remediation_quality` uses `document_path` (which is vN-1 in iterative runs)
- Phase 6: 5 new tests + 6 existing test files updated with `_remediate_v1` assertions
- Phase 7: Architecture docs (`MCP_OPERATOR_RUNBOOK.md`, `MCP_OPERATIONAL_FLOWS.md`) updated; `REPORT_NAMING_STANDARDS.md` updated with versioned naming and detection patterns
- Pre-existing test bug fixed: `test_truncate_long_action` updated for `max_len=2000` (PLAN-029)
