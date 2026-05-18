# PLAN-018: YAML Document Parity and API Consistency

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

## Context

Full tool testing of all 20 mcp_ucx tools against BRD-03 (YAML format) revealed 6 issues where tools assume `.md` input or have inconsistent APIs. These tools work correctly for MD documents but fail or produce incorrect results for YAML-format SDD artifacts.

**Goal**: Ensure all mcp_ucx tools handle YAML documents on par with MD documents, and normalize result class APIs.

**Status**: Implemented (2026-04-02, mcp_ucx v1.8.0 / framework v0.15.0)

**Scope**: `mcp_ucx` server code only. `sdd_create` / `sdd_create_build` testing is out of scope (separate plan).

---

## Issues Found

### Issue 1: `sdd_consistency` expects `.md` source and derived artifacts

**Tool**: `sdd_consistency` (`consistency/runner.py`)
**Symptom**: Reports `missing_source_artifact` and `BLOCKED` for YAML-only BRD directories.
**Root cause**: Multiple hardcoded `.md` assumptions:
  - `_resolve_source()` (line 56): `folder.glob("*.md")` — misses `.yaml` source artifacts
  - Derived artifact detection (lines 85-87): constructs `_validation.md` and `_remediated.md` paths — misses `.yaml` variants
  - Validation report lookup (line 85): looks for `{doc_id}_validation_report.md` — but we write `.json`
**Impact**: Consistency check is unusable for YAML documents — blocks the lifecycle pipeline.

**Fix**:
  - `_resolve_source()`: Search both `*.md` and `*.yaml` with `_validation`/`_remediated` exclusion
  - Derived artifact detection: Check for both `.md` and `.yaml` validation/remediated copies
  - Validation report: Check `.json` in addition to `.md`
  - Use shared `collect_source_files()` utility (Issue #6)

### Issue 2: `sdd_next_action` doesn't detect YAML artifacts

**Tool**: `sdd_next_action` (`tool_registry.py:_inspect_document_folder()`)
**Symptom**: After full remediation pipeline on YAML BRD, reports stage as "reviewed" instead of "remediated". YAML files not included in `existing_artifacts` list.
**Root cause**: Three `.md`-only assumptions:
  - `md_files = sorted(document_dir.glob("*.md"))` — YAML not collected
  - `all_names` built from `md_files + json_files` only — YAML invisible
  - `source_pattern = re.compile(r"^[A-Z]+-\d+_.+\.md$")` — misses `.yaml`
  - `has_validation_copy`, `has_remediated_copy` check only `md_files`
**Impact**: Pipeline orchestration gives wrong recommendations and incomplete artifact lists for YAML documents.

**Fix**:
  - Add `yaml_files = sorted(document_dir.glob("*.yaml"))` 
  - Include in `all_names`
  - Expand `source_pattern` to match `.yaml`
  - Check both `md_files` and `yaml_files` for validation/remediated copies

### Issue 3: Scoring formula weights cross-section errors same as structural errors

**Tool**: `sdd_score_show` / `sdd_score_validate` (`scoring/runner.py`)
**Symptom**: 9 cross-section errors (SDD-XS-001 phantom IDs) scored as 9 x 20 = 180 deductions → score 0. These are content-level issues, not structural failures.
**Root cause**: `_derive_score()` reads flat `summary.errors` count. No distinction between error categories. Formula: `score = max(0, 100 - (errors * 20) - (warnings * 5))`.
**Impact**: Score is misleading — a BRD with 5+ cross-section issues always scores 0, masking the actual document quality.

**Fix** (two-part):

**Part A — Validation runner emits categorized counts**: Add `structural_errors` and `cross_section_errors` to the report `summary` dict. The validation runner already knows the category when appending errors (cross-section rules are called in a separate block). Count errors before and after cross-section checks to derive the split.

```python
# In runner.py report summary:
"summary": {
    "errors": len(errors),                    # total (backward compat)
    "structural_errors": structural_count,    # new
    "cross_section_errors": xs_count,         # new
    "warnings": len(warnings),
    "passes": len(passes),
    "is_valid": is_valid,
}
```

**Part B — Scoring runner uses categorized weights**: Update `_derive_score()`:

```python
structural = int(summary.get("structural_errors", summary.get("errors", 0)))
cross_section = int(summary.get("cross_section_errors", 0))
warnings = int(summary.get("warnings", 0))

# If categorized counts available, use weighted formula
if "structural_errors" in summary:
    score = max(0, 100 - (structural * 20) - (cross_section * 10) - (warnings * 5))
else:
    # Backward compat: old reports without categories
    score = max(0, 100 - (structural * 20) - (warnings * 5))
```

Weights:
  - `structural_error`: 20 points (missing section, missing frontmatter)
  - `cross_section_error`: 10 points (SDD-XS, BRD-XS rules)
  - `warning`: 5 points (unchanged)

### Issue 4: Result class API inconsistency

**Tools**: All runners
**Symptom**: Some result classes use `report` (validation), others use `payload` (preflight, consistency, link_validation), and field names vary (`is_valid` vs `passed` vs `status`).
**Impact**: Callers must know per-tool attribute names. Makes generic tool handling in pipeline orchestration harder.

**Current state**:

| Runner | Result class | Data field | Status field |
|--------|-------------|-----------|-------------|
| validation | `ValidationRunResult` | `report` | `is_valid` |
| consistency | `ConsistencyRunResult` | `payload` | `passed` |
| link_validation | `LinkValidationRunResult` | `payload` | `passed` |
| preflight | `PreflightRunResult` | `payload` | `status` (str) |
| scoring (show) | `ScoreShowResult` | `payload` | — |
| scoring (validate) | `ScoreValidateResult` | — | `passed` |
| scan | `ScanRunResult` | `report` | — |
| remediation | `RemediationRunResult` | `report` | — |
| validate_fix | `ValidateFixRunResult` | `report` | — |
| remediate_fix | `RemediateFixRunResult` | `report` | — |

**Fix**: Add `@property` aliases to frozen dataclasses. Non-breaking — existing attributes stay, aliases added. Properties work on `@dataclass(frozen=True)` since they don't set instance attributes.

```python
@property
def report(self) -> dict[str, object]:
    return self.payload

@property
def is_valid(self) -> bool:
    return self.passed
```

### Issue 5: YAML structure validation in remediation (absorbed from PLAN-019)

**Tool**: `sdd_remediate` (`remediation/runner.py`)
**Symptom**: `run_remediation_build()` only checks frontmatter + placeholders — both irrelevant for YAML. No structural validation of YAML documents.
**Root cause**: Remediation was built for MD-only workflow.
**Impact**: Remediation report is near-empty for YAML documents.

**Fix**: Add YAML structure validation when document is `.yaml/.yml`:
- **Required top-level keys**: Load from the layer template (`BRD-TEMPLATE.yaml` sections list) via `_load_layer_yaml_template()` — not hardcoded per doc_type. Extract section names from template and verify they exist as top-level keys in the document YAML.
- **Element ID format**: Verify `id:` values match `TYPE.NN.hash` pattern (`^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`)
- **Empty section detection**: Flag sections that are `null`, empty dict `{}`, or empty list `[]`

### Issue 6: Shared source file collection utility

**Tools**: validation, consistency, remediation runners
**Symptom**: Three runners independently implement YAML/MD file collection with `_validation`/`_remediated` exclusion. Pattern duplicated across files.
**Root cause**: YAML support added incrementally (PLAN-016 added to validation only).

**Fix**: Create shared `mcp_ucx/src/mcp_server/utils/source_files.py`:

```python
def collect_source_files(
    document_path: Path,
    extensions: tuple[str, ...] = (".md", ".yaml", ".yml"),
) -> list[Path]:
    """Collect source document files, excluding templates and derived copies.
    
    Handles both file and directory inputs. Excludes:
    - *_validation.* (derived validation copies)
    - *_remediated.* (derived remediated copies)
    - *TEMPLATE* (template files)
    - *REVIEW*, *REPORT* (review/audit artifacts)
    """
```

Wire into each runner as it's fixed (not as a separate step).

---

## File Changes

| File | Action | Issue | Est. Lines |
|------|--------|-------|-----------|
| `utils/source_files.py` | **Create** shared collector | #6 | ~60 |
| `consistency/runner.py` | YAML source + derived detection, use shared collector, add `report`/`is_valid` aliases | #1, #4, #6 | +30 |
| `tool_registry.py` | YAML in `_inspect_document_folder()` — all_names, source, validation, remediated | #2 | +15 |
| `scoring/runner.py` | Category-weighted scoring, add `report` alias | #3, #4 | +25 |
| `validation/runner.py` | Emit `structural_errors`/`cross_section_errors` in summary, use shared collector | #3, #6 | +15 |
| `link_validation/runner.py` | Add `report`/`is_valid` aliases | #4 | +8 |
| `preflight/runner.py` | Add `report`/`is_ready` aliases | #4 | +8 |
| `remediation/runner.py` | YAML structure validation, use shared collector | #5, #6 | +50 |
| `tests/unit/test_source_files.py` | **Create** — shared collector tests | #6 | ~80 |
| `tests/unit/test_yaml_parity.py` | **Create** — consistency, next_action, scoring YAML tests | #1-3 | ~120 |
| `tests/unit/test_api_aliases.py` | **Create** — result class alias tests | #4 | ~60 |

### Documentation Updates

| File | Action |
|------|--------|
| `mcp_ucx/docs/README.md` | Update tool descriptions to note YAML support; add CHANGELOG v1.8.0 link |
| `mcp_ucx/docs/ROADMAP.md` | Add v1.8.0 planned release section |
| `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.8.0.md` | **Create** — YAML parity, categorized scoring, API aliases, shared collector |
| `mcp_ucx/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md` | Update artifact lifecycle diagram to show YAML path alongside MD |
| `mcp_ucx/docs/architecture/MCP_CLI_REFERENCE.md` | Note YAML document support in validate/consistency/remediate tool docs |
| `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md` | Add YAML troubleshooting section (common issues: frontmatter false positive, derived copy detection) |
| `roadmap/ROADMAP.md` | Add v0.15.0 planned release (maps to mcp_ucx v1.8.0) |
| `changelog/CHANGELOG_v0.15.0.md` | **Create** — framework-level changelog for YAML parity |
| `ucx_flow_v3/01_BRD/README.md` | Note that BRDs can be authored in YAML or MD; both validated by sdd_validate |

**Total**: ~530 lines across 20 files (11 code + 9 docs)

---

## Implementation Order

1. Create `utils/source_files.py` shared collector (Issue #6)
2. Fix `sdd_consistency` — YAML source + derived detection, use shared collector, add aliases (Issues #1, #4, #6)
3. Fix `sdd_next_action` — YAML artifacts in `_inspect_document_folder()` (Issue #2)
4. Add YAML structure validation to `sdd_remediate`, use shared collector (Issues #5, #6)
5. Emit categorized error counts in `validation/runner.py` (Issue #3 Part A)
6. Update `_derive_score()` in `scoring/runner.py` for category weights (Issue #3 Part B)
7. Add `report`/`is_valid` aliases to remaining result classes (Issue #4)
8. Wire shared collector into `validation/runner.py` replacing `_collect_markdown_files` + `_collect_yaml_files` (Issue #6)
9. Write tests for all changes
10. Run full test suite (existing 163 + new)
11. Re-test all 20 tools against BRD-03 YAML
12. Test `sdd_run_lifecycle` pipeline end-to-end on YAML BRD
13. Create `mcp_ucx/docs/CHANGELOG/CHANGELOG_v1.8.0.md`
14. Update `mcp_ucx/docs/ROADMAP.md` — add v1.8.0 release
15. Update `mcp_ucx/docs/README.md` — tool descriptions + changelog link
16. Update mcp_ucx architecture docs (runtime, CLI reference, runbook)
17. Create `changelog/CHANGELOG_v0.15.0.md` (framework-level)
18. Update `roadmap/ROADMAP.md` — add v0.15.0 release
19. Update `ucx_flow_v3/01_BRD/README.md` — note YAML authoring support

---

## Verification

1. `python -m pytest mcp_ucx/tests/unit/ -v` — all existing + new tests pass
2. `sdd_consistency` on YAML BRD → detects source artifact and derived copies, no BLOCKED
3. `sdd_next_action` on YAML BRD after remediation → stage "remediated", YAML files in artifacts list
4. `sdd_score_show` on 9 cross-section errors → score > 0 (not zero), categorized counts in output
5. `sdd_score_validate` with threshold=85 → uses weighted formula
6. `sdd_remediate` on YAML BRD → reports missing keys, invalid IDs, empty sections (not just "review linked")
7. All result classes accessible via both `report` and `payload` (where applicable)
8. All result classes accessible via both `is_valid` and `passed` (where applicable)
9. `sdd_run_lifecycle` pipeline (validate → validate_fix → review) completes on YAML BRD
10. Shared `collect_source_files()` used in validation, consistency, and remediation runners

---

## Risks

| Risk | Mitigation |
|------|-----------|
| API aliases break existing callers | Additive only — `payload`/`passed` stay, `report`/`is_valid` added |
| Scoring weight change affects existing gates | Backward compat: old reports without categories use original formula |
| YAML parity in consistency may miss MD checks | YAML path skips frontmatter/section checks (appropriate for structured data) |
| Template loading for YAML structure validation | Reuse existing `_load_layer_yaml_template()` — already tested |
| Shared collector breaks existing file selection | Keep existing private functions as deprecated wrappers calling shared utility |

---

## Out of Scope

- `sdd_create` / `sdd_create_build` testing — separate plan, not YAML parity related
- Review report parsing for remediation — PLAN-019 (depends on this plan)
- UCX relocation — PLAN-020 (independent)

---

## Dependencies

- PLAN-016 (cross-section validation) — done, introduced the errors that exposed Issues 1-3
- PLAN-019 (remediation enhancement) — YAML structure validation absorbed into this plan; PLAN-019 retains review report parsing only
- Implement BEFORE PLAN-019 (review parsing depends on YAML-aware remediation)
