# PLAN-020: YAML Document Parity and API Consistency

## Context

Full tool testing of all 20 mcp_sdd tools against BRD-03 (YAML format) revealed 4 issues where tools assume `.md` input or have inconsistent APIs. These tools work correctly for MD documents but fail or produce incorrect results for YAML-format SDD artifacts.

**Goal**: Ensure all mcp_sdd tools handle YAML documents on par with MD documents, and normalize result class APIs.

**Status**: Planned

**Scope**: `mcp_sdd` server code only

---

## Issues Found

### Issue 1: `sdd_consistency` expects `.md` source artifacts

**Tool**: `sdd_consistency` (`consistency/runner.py`)
**Symptom**: Reports `missing_source_artifact` and `BLOCKED` for YAML-only BRD directories.
**Root cause**: `_find_source_artifact()` searches for `[A-Z]+-\d+_.+\.md` pattern. YAML files (`*.yaml`) are not recognized as source artifacts.
**Impact**: Consistency check is unusable for YAML documents — blocks the lifecycle pipeline.

**Fix**: Add `.yaml`/`.yml` glob alongside `.md` in source artifact detection. Apply same `_validation`/`_remediated` exclusion filter used in validation runner.

### Issue 2: `sdd_next_action` doesn't detect YAML artifacts

**Tool**: `sdd_next_action` (`tool_registry.py:_inspect_document_folder()`)
**Symptom**: After full remediation pipeline on YAML BRD, reports stage as "reviewed" instead of "remediated". Recommends `sdd_remediate` when remediation is already complete.
**Root cause**: `_inspect_document_folder()` only searches for `.md` files:
  - `source_pattern = re.compile(r"^[A-Z]+-\d+_.+\.md$")` — misses `.yaml`
  - `has_validation_copy = any("_validation" in f.stem for f in md_files)` — only checks `.md`
  - `has_remediated_copy = any("_remediated" in f.stem for f in md_files)` — only checks `.md`
**Impact**: Pipeline orchestration gives wrong recommendations for YAML documents.

**Fix**: Include `.yaml` files in artifact detection alongside `.md`. Check both extensions for source, validation, and remediated copies.

### Issue 3: Scoring formula weights cross-section errors same as structural errors

**Tool**: `sdd_score_show` / `sdd_score_validate` (`scoring/runner.py`)
**Symptom**: 9 cross-section warnings (SDD-XS-001 phantom IDs) scored as 9 × 20 = 180 deductions → score 0. These are content-level issues, not structural failures.
**Root cause**: Generic scoring formula `score = max(0, 100 - (errors * 20) - (warnings * 5))` doesn't distinguish error categories. A single SDD-XS-001 error (phantom traceability ID) costs the same as a missing required section.
**Impact**: Score is misleading — a BRD with 5+ cross-section issues always scores 0, masking the actual document quality.

**Fix**: Introduce error weight categories:
  - `structural_error`: 20 points (missing section, missing frontmatter) — current weight
  - `cross_section_error`: 10 points (SDD-XS, BRD-XS rules) — reduced weight
  - `warning`: 5 points (current weight, unchanged)

Implementation: Add `error_category` field to validation report errors (e.g., prefix-based: `SDD-XS-*` and `BRD-XS-*` are cross-section). Scoring runner checks prefix to determine weight.

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

**Fix**: Add a uniform `report` property alias to all result classes that currently use `payload`. This is non-breaking — existing `payload` attribute stays, `report` is added as an alias. Also add `is_valid` alias where `passed` is used.

```python
@property
def report(self) -> dict[str, object]:
    return self.payload

@property
def is_valid(self) -> bool:
    return self.passed
```

---

## File Changes

| File | Action | Issue | Est. Lines |
|------|--------|-------|-----------|
| `consistency/runner.py` | Add YAML source detection | #1 | +15 |
| `tool_registry.py` | Add YAML to `_inspect_document_folder()` | #2 | +10 |
| `scoring/runner.py` | Category-weighted scoring | #3 | +20 |
| `validation/runner.py` | Add error category prefix to cross-section errors | #3 | +5 |
| `validation/cross_section.py` | Tag errors with `[cross-section]` category | #3 | +5 |
| `validation/brd_rules.py` | Tag errors with `[cross-section]` category | #3 | +5 |
| `consistency/runner.py` | Add `report` + `is_valid` aliases | #4 | +8 |
| `link_validation/runner.py` | Add `report` + `is_valid` aliases | #4 | +8 |
| `preflight/runner.py` | Add `report` + `is_ready` aliases | #4 | +8 |
| `scoring/runner.py` | Add `report` alias to ScoreShowResult | #4 | +5 |
| `remediation/runner.py` | YAML structure validation | #5 | +40 |
| `utils/source_files.py` | Create shared source file collector | #6 | ~50 |
| `validation/runner.py` | Use shared collector | #6 | -20 (remove duplication) |
| `remediation/runner.py` | Use shared collector | #6 | -10 (remove duplication) |
| Tests (new/updated) | Cover YAML parity + scoring weights + structure | All | ~200 |

### Issue 5: YAML structure validation in remediation (absorbed from PLAN-019)

**Tool**: `sdd_remediate` (`remediation/runner.py`)
**Symptom**: `run_remediation_build()` only checks frontmatter + placeholders — both irrelevant for YAML. No structural validation of YAML documents.
**Root cause**: Remediation was built for MD-only workflow.
**Impact**: Remediation report is near-empty for YAML documents.

**Fix**: Add YAML structure validation when document is `.yaml/.yml`:
- **Required top-level keys**: Verify expected keys exist per doc_type (BRD: `metadata`, `document_control`, `executive_summary`, `functional_requirements`, `traceability`)
- **Element ID format**: Verify `id:` values match `TYPE.NN.hash` pattern
- **Empty section detection**: Flag sections that exist but have no content

### Issue 6: Shared source file collection utility

**Tools**: validation, consistency, remediation runners
**Symptom**: Three runners independently implement YAML/MD file collection with `_validation`/`_remediated` exclusion. Pattern duplicated across files.
**Root cause**: YAML support added incrementally (PLAN-016 added to validation only).

**Fix**: Create shared `mcp_sdd/src/mcp_server/utils/source_files.py` with:
```python
def collect_source_files(document_path: Path, extensions: tuple[str, ...] = (".md", ".yaml", ".yml")) -> list[Path]:
    """Collect source document files, excluding templates and derived copies."""
```
Replace `_collect_markdown_files` and `_collect_yaml_files` in all runners with this shared utility.

---

**Total**: ~350 lines across 12+ files

---

## Implementation Order

1. Create shared `utils/source_files.py` (Issue #6)
2. Fix `sdd_consistency` YAML source detection (Issue #1)
3. Fix `sdd_next_action` YAML artifact detection (Issue #2)
4. Add YAML structure validation to `sdd_remediate` (Issue #5)
5. Add error category prefix to cross-section validation errors (Issue #3)
6. Update scoring formula for category-weighted errors (Issue #3)
7. Add result class API aliases (Issue #4)
8. Wire shared source file collector into all runners
9. Write tests
10. Run full test suite
11. Re-test all 20 tools against BRD-03

---

## Verification

1. `python -m pytest mcp_sdd/tests/unit/ -v` — all pass
2. `sdd_consistency` on YAML BRD → detects source artifact, no BLOCKED
3. `sdd_next_action` on YAML BRD after remediation → stage "remediated", next "review" or "complete"
4. `sdd_score_show` on 9 cross-section errors → score > 0 (not zero)
5. All result classes accessible via both `report` and `payload` (where applicable)
6. All result classes accessible via both `is_valid` and `passed` (where applicable)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| API aliases break existing callers | Additive only — `payload`/`passed` stay, `report`/`is_valid` added |
| Scoring weight change affects existing quality gates | Cross-section errors are new (PLAN-016) — no existing gates use them |
| YAML parity in consistency may miss MD-specific checks | YAML path skips frontmatter/section checks (appropriate) |

---

## Dependencies

- PLAN-016 (cross-section validation) — done, introduced the errors that exposed Issues 1-3
- PLAN-019 (remediation enhancement) — YAML structure validation absorbed into this plan; PLAN-019 retains review report parsing only
- Implement BEFORE PLAN-019 (review parsing depends on YAML-aware remediation)
