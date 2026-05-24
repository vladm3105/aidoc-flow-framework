# PLAN-016: mcp_ucx Cross-Section Validation & BRD Template Improvements

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

## Context

During BRD-04 (Data Model & Ledger) review, we found 9 friction points that stem from missing machine-enforceable validation in `mcp_ucx`. Current `sdd_validate` only checks frontmatter fields, required tags, and section presence — it has no cross-section consistency rules.

Analysis shows 3 of 7 proposed rules are **not BRD-specific** — they apply to all 11 SDD layers. This plan splits validation into two tiers: generic cross-section rules (all layers) and BRD-specific rules.

**Goal**: Add two-tier cross-section validation to `mcp_ucx` server via `sdd_validate`, update the BRD template, and establish patterns reusable across all SDD layers.

**Scope**: `mcp_ucx` server code + templates only. Claude `doc-*` skills are out of scope.

**Status**: Implemented (2026-04-01, mcp_ucx v1.7.0 / framework v0.14.0)

---

## Friction Points Addressed

| # | Friction | Root Cause | Tier |
|---|---------|-----------|------|
| 1 | ADT decisions don't propagate to Implementation/Support/Cost | No cross-section consistency rule | BRD-specific |
| 2 | Phantom quality attribute IDs in traceability matrix | No element ID existence validation | **Generic (all layers)** |
| 3 | Phase count mismatch (Scope vs Implementation) | No phase alignment check | BRD-specific |
| 4 | PRD-Ready Score self-declared at 100/100 despite issues | No plausibility check against validation findings | **Generic (all layers)** |
| 5 | Stale entity references (Sardine in exec summary, not in FRs) | No entity consistency check | BRD-specific |
| 6 | Currency scope inconsistency (UZS missing from FR-01) | No enum consistency across sections | BRD-specific |
| 7 | No diagrams section in template | Template gap | **Generic (all layers with diagram contracts)** |
| 8 | No YAML-to-MD conversion standard | No MD companion template | BRD-specific (template) |
| 9 | No diagram-to-section mapping standard | DIAGRAM_STANDARDS.md gap | BRD-specific (template) |

---

## Architecture: Two-Tier Validation

```
mcp_ucx/src/mcp_server/validation/
├── runner.py              # Existing entry point + YAML fork
├── cross_section.py       # NEW: Tier 1 — Generic rules (all layers)
├── brd_rules.py           # NEW: Tier 2 — BRD-specific rules
└── __init__.py            # Updated exports
```

**Call chain** in `run_project_validation_build()`:

```
sdd_validate(doc_type="brd", ...)
  → runner.py: YAML/MD fork
    → cross_section.py: run_cross_section_checks()     # ALL layers
    → brd_rules.py: run_brd_cross_section_checks()     # BRD only
```

Future layers get Tier 1 validation for free. Layer-specific modules (e.g., `prd_rules.py`, `spec_rules.py`) can be added following the `brd_rules.py` pattern.

---

## Deliverables

### 1. Tier 1: Generic cross-section module — `cross_section.py`

Rules that apply to **all 11 SDD layers** via `sdd_validate`. Each rule is parametric — it discovers the relevant YAML keys per layer rather than hardcoding BRD structure.

| Rule ID | Check | Severity | Layers | How It Works |
|---------|-------|----------|--------|-------------|
| SDD-XS-001 | **Traceability ID Existence** — All element IDs referenced in `traceability` section must exist as `id` values in their declared source sections. | error | All 11 | Collects all `id:` values from the full YAML (building an ID registry). Scans `traceability` for ID-shaped strings (`TYPE.NN.xxxx`). Flags any reference not in registry. |
| SDD-XS-002 | **Readiness Score Plausibility** — If any `*_ready_score` field parses as "100/100" but validation has errors/warnings, flag as implausible. | warning | All 11 | Auto-detects score field name per layer: `prd_ready_score` (BRD), `ears_ready_score` (PRD), `bdd_ready_score` (EARS), `sys_ready_score` (ADR), `req_ready_score` (SYS), `spec_ready_score` (REQ/CTR), `tasks_ready_score` (TSPEC), `execution_ready_score` (TASKS). Runs last. |
| SDD-XS-003 | **Diagram Registry Present** — YAML documents that define `diagram_standard` with required tags in metadata must have a `diagrams` section with at least 1 item. | warning | BRD, PRD, ADR, SYS, SPEC | Checks if template metadata has `diagram_standard.tags` — if so, expects `diagrams.items` to be non-empty. Layers without diagram contracts (EARS, BDD, REQ, CTR, TSPEC, TASKS) are skipped. |

**Function signature**:

```python
def run_cross_section_checks(
    *,
    yaml_data: dict[str, object],
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Generic cross-section validation for all SDD layers (YAML documents)."""
```

**MD fallback**:

```python
def run_cross_section_checks_md(
    *,
    content: str,
    doc_type: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """Cross-section checks for MD-format documents (regex-based, limited).
    
    Only SDD-XS-001 (traceability ID existence) is feasible via regex.
    Others skip with info: 'Structured validation requires YAML format'.
    """
```

**Readiness score field mapping** (used by SDD-XS-002):

```python
READINESS_SCORE_FIELDS: dict[str, str] = {
    "brd": "prd_ready_score",
    "prd": "ears_ready_score",
    "ears": "bdd_ready_score",
    "bdd": "adr_ready_score",
    "adr": "sys_ready_score",
    "sys": "req_ready_score",
    "req": "spec_ready_score",
    "ctr": "spec_ready_score",
    "spec": "task_ready_score",
    "tspec": "tasks_ready_score",
    "tasks": "execution_ready_score",
}
```

### 2. Tier 2: BRD-specific module — `brd_rules.py`

Rules that only apply when `doc_type == "brd"`.

| Rule ID | Check | Severity | Friction | Notes |
|---------|-------|----------|----------|-------|
| BRD-XS-001 | **ADT Decision Propagation** — Extract selected option name from each ADT `alternatives` list (entry where `rationale` starts with "Selected"). Check case-insensitive presence in serialized `implementation_approach` and `cost_benefit` sections. | warning | #1 | Normalized key extraction. Serializes target sections to string via `json.dumps()` for substring search. |
| BRD-XS-002 | **Phase Alignment** — Phase names/count in `project_scope.phasing.phases` must match `implementation_approach.phases.items`. Compare by `phase` key value. | error | #3 | Exact phase name match required. Reports which phases are missing/extra. |
| BRD-XS-004 | **Entity Consistency** — Extract entity names from `executive_summary.key_stakeholders[].stakeholder` and partner names from `executive_summary.business_problem`. Cross-check against serialized `functional_requirements` and `stakeholders` sections. Flag entities in exec summary that appear nowhere else. | warning | #5 | Extracts from YAML keys (not freetext NLP). For partner names in `business_problem` text, uses regex for capitalized words in parentheses like `(Bridge, Sardine)`. |
| BRD-XS-005 | **Currency Scope Consistency** — **Conditional**: only fires when `mandatory_conditions` contains `precision` key with currency-related content. Extracts currency codes (3-letter uppercase: USD, MXN, UZS, USDC, EUR) from FR acceptance criteria and `mandatory_conditions`. Flags codes in mandatory conditions not present in FR scope. | warning | #6 | Regex `r'\b[A-Z]{3,4}\b'` filtered against known currency patterns. Skips for BRDs without currency keys. |

**Function signature**:

```python
def run_brd_cross_section_checks(
    *,
    yaml_data: dict[str, object],
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """BRD-specific cross-section consistency validation (YAML BRDs only)."""
```

**MD fallback** (degraded path):

```python
def run_brd_cross_section_checks_md(
    *,
    content: str,
    errors: list[str],
    warnings: list[str],
    passes: list[str],
) -> None:
    """BRD cross-section checks for MD-format BRDs (regex-based, limited).
    
    Only BRD-XS-002 (phase count via heading matching) is feasible.
    Others skip with info: 'Structured BRD validation requires YAML format'.
    """
```

### 3. YAML/MD decision fork in validation runner

**File**: `mcp_ucx/src/mcp_server/validation/runner.py`

**Changes** (+80-100 lines):

1. Add `_collect_yaml_files(document_path: Path) -> list[Path]` — finds `.yaml` files matching `[A-Z]+-\d+_*.yaml` pattern, excludes TEMPLATE files.

2. Add decision fork in `run_project_validation_build()`:

   ```python
   yaml_files = _collect_yaml_files(document_path)
   md_files = _collect_markdown_files(document_path)

   if yaml_files:
       # YAML path: structured validation
       yaml_data = yaml.safe_load(yaml_files[0].read_text(encoding="utf-8"))
       _validate_yaml_metadata(yaml_data, template, errors, warnings, passes)
       
       # Tier 1: Generic cross-section (all layers)
       run_cross_section_checks(
           yaml_data=yaml_data, doc_type=doc_type,
           errors=errors, warnings=warnings, passes=passes,
       )
       # Tier 2: Layer-specific cross-section
       if doc_type.strip().lower() == "brd":
           run_brd_cross_section_checks(
               yaml_data=yaml_data,
               errors=errors, warnings=warnings, passes=passes,
           )
   elif md_files:
       # Existing MD path (unchanged) + degraded cross-section
       # ... existing frontmatter, tags, sections, parity checks ...
       run_cross_section_checks_md(
           content=combined_content, doc_type=doc_type,
           errors=errors, warnings=warnings, passes=passes,
       )
       if doc_type.strip().lower() == "brd":
           run_brd_cross_section_checks_md(
               content=combined_content,
               errors=errors, warnings=warnings, passes=passes,
           )
   else:
       errors.append("No markdown or YAML files found to validate")
   ```

3. New helper `_validate_yaml_metadata()` — maps YAML top-level keys to existing tag/field validation.

### 4. BRD-TEMPLATE.yaml updates

**Files** (must stay in sync):

- `mcp_ucx/templates/BRD-TEMPLATE.yaml`
- `ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml`

Add `diagrams` section and `cross_section_rules` to metadata. See plan body for YAML content.

### 5. New BRD-MD-TEMPLATE.md

**File**: `mcp_ucx/templates/BRD-MD-TEMPLATE.md` (~120 lines)

Standardized YAML-to-MD rendering template defining section headings, diagram references, table formats, and MUST/SHALL formatting rules.

### 6. DIAGRAM_STANDARDS.md update

**File**: `ucx_flow_v3/DIAGRAM_STANDARDS.md`

Add BRD-specific required diagram list (Platform: 3 minimum, Feature: 2 minimum). Fix DFD-L0 vs DFD-L1 discrepancy — standardize to `dfd-l1`.

### 7. Tests

- `mcp_ucx/tests/unit/test_cross_section.py` (~200 lines) — generic rule tests across multiple doc types
- `mcp_ucx/tests/unit/test_brd_rules.py` (~250 lines) — BRD-specific rule tests

---

## File Change Summary

| File | Action | Size Est. | Tier |
|------|--------|-----------|------|
| `mcp_ucx/src/mcp_server/validation/cross_section.py` | **Create** | ~200 lines | Generic (all layers) |
| `mcp_ucx/src/mcp_server/validation/brd_rules.py` | **Create** | ~200 lines | BRD-specific |
| `mcp_ucx/src/mcp_server/validation/runner.py` | **Modify** | +80-100 lines | Infrastructure |
| `mcp_ucx/src/mcp_server/validation/__init__.py` | **Modify** | +4 exports | Infrastructure |
| `mcp_ucx/templates/BRD-TEMPLATE.yaml` | **Modify** | +40 lines | BRD template |
| `ucx_flow_v3/01_BRD/BRD-TEMPLATE.yaml` | **Sync** | Same | BRD template |
| `mcp_ucx/templates/BRD-MD-TEMPLATE.md` | **Create** | ~120 lines | BRD template |
| `ucx_flow_v3/DIAGRAM_STANDARDS.md` | **Modify** | +25 lines | Framework standard |
| `mcp_ucx/tests/unit/test_cross_section.py` | **Create** | ~200 lines | Generic tests |
| `mcp_ucx/tests/unit/test_brd_rules.py` | **Create** | ~250 lines | BRD tests |

**Total new code**: ~1,200 lines across 10 files

---

## Implementation Order

1. Run existing test suite (baseline)
2. Create `cross_section.py` with 3 generic rules + MD fallback
3. Create `brd_rules.py` with 4 BRD-specific rules + MD fallback
4. Add YAML collection + decision fork to `validation/runner.py`
5. Wire both tiers into validation pipeline
6. Update `validation/__init__.py` exports
7. Write `test_cross_section.py`
8. Write `test_brd_rules.py`
9. Run full test suite — all must pass
10. Update `BRD-TEMPLATE.yaml` (both copies)
11. Create `BRD-MD-TEMPLATE.md`
12. Update `DIAGRAM_STANDARDS.md`
13. Smoke test against BRD-04 YAML (pre-fix and post-fix versions)
14. Smoke test against PRD YAML (verify generic rules run, BRD rules skipped)
15. Smoke test against MD-format BRD (verify degraded path)

---

## Risks

| Risk | Mitigation |
|------|-----------|
| YAML parsing adds dependency | `yaml` already imported in runner.py |
| False positives on ADT entity matching | Normalized option name, case-insensitive, serialized section search |
| Currency rule fires on non-financial BRDs | Conditional: only activates when `mandatory_conditions.precision` exists |
| Breaking existing MD validation | YAML fork is additive; MD path unchanged |
| Template changes break existing BRDs | `diagrams` and `cross_section_rules` are additive; no fields removed |
| Generic rules produce noise on sparse layers | Graceful skip when expected keys not found |

---

## Future Extensions (not in this plan)

- `prd_rules.py` — PRD-specific rules (feature vs user journey alignment)
- `spec_rules.py` — SPEC-specific rules (REQ coverage completeness)
- `sdd_consistency` tool extension — cross-document traceability
- Diagram registry validation for PRD/SYS/SPEC templates
- Auto-generation of `diagrams` section during `sdd_create`
