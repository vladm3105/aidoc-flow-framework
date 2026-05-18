# CHG Migration Plan — v2 to v3

## Overview

CHG (Change Management) is a **governance overlay** — not a lifecycle layer. It triggers on-demand when modifying any SDD artifact across all layers. The v2 CHG system is a 4-gate, 14-layer-aware system with 12 existing files and 23 references to unmaterialized content (workflows, source guides, scripts).

This plan maps the 14-layer CHG system to the 8-layer v3 framework, addresses naming collisions, strips references to cut layers, and drops all never-implemented scaffolding.

---

## 1. Critical: Change Level Naming Collision

**Problem**: CHG v2 uses `L1/L2/L3` for change levels (C1=trivial, C2=minor, C3=major). In v3, `L1=BRD, L2=PRD, L3=EARS`. The statement "L2 change to PRD" is ambiguous — is it a minor change (L2) to the PRD layer, or a change at Layer 2?

**Resolution**: Rename change levels to `C1/C2/C3` across ALL CHG files:

| Old (v2) | New (v3) | Scope | Gate Required |
|----------|----------|-------|---------------|
| L1 | **C1** | Trivial: typos, formatting, clarifications | None |
| L2 | **C2** | Minor: section update, requirement refinement | Peer review |
| L3 | **C3** | Major: cross-layer change, new requirements | Formal gate |
| Emergency | **Emergency** | Critical production issue | Post-hoc + post-mortem |

Layer numbers (`L1-L8`) now unambiguously refer to SDD layers only.

---

## 2. Gate Re-Mapping to v3 Layers

### New 4-Gate Structure

| Gate | v2 Range | v3 Range | v3 Artifacts | Rename |
|------|----------|----------|-------------|--------|
| GATE-01 | L1-L4 | **L1-L2** | BRD, PRD | Keep (starts at L1) |
| GATE-05 | L5-L8 | **L3-L5** | EARS, BDD, ADR | Rename: GATE-03 |
| GATE-09 | L9-L11 | **L6-L7** | TDD, SPEC | Rename: GATE-06 |
| GATE-12 | L12-L14 | **Code** | Source code | Rename: GATE-CODE |

### Rationale for Gate Numbering Change

v2 gate numbers (01, 05, 09, 12) were named after the first layer in each range. v3 layer numbers shifted:
- Old L5 (ADR) → new L5 (ADR) — coincidence
- Old L9 (SPEC) → new L7 (SPEC) — shifted
- Old L12 (Code) → no layer number (Code is unnumbered)

New names use v3 first-layer numbers: GATE-01 (L1), GATE-03 (L3), GATE-06 (L6), GATE-CODE.

---

## 3. Per-Gate Change Summary

### GATE-01: Business/Product Gate (L1-L2)

**Changes needed: MINIMAL**

- `layer_range: "L1-L4"` → `"L1-L2"`
- `layer_names: ["BRD", "PRD", "EARS", "BDD"]` → `["BRD", "PRD"]`
- Remove EARS/BDD from Section 1.1 layers covered table
- Drop Section 3.1 error checks for EARS syntax (GATE-01-E003) and BDD format (GATE-01-E004) — these move to GATE-03
- `L1/L2/L3` change levels → `C1/C2/C3`
- Keep: business justification, stakeholder approval, change source classification
- File stays: `GATE-01_BUSINESS_PRODUCT.md`

### GATE-03 (was GATE-05): Requirements & Architecture Gate (L3-L5)

**Changes needed: MAJOR REWRITE**

Original GATE-05 covered ADR, SYS, REQ, CTR. In v3:
- **ADR survives** (L5)
- **SYS cut** — delete all SYS quality attribute checks
- **REQ cut** — delete all REQ traceability checks (GATE-05-E003)
- **CTR cut** — delete all CTR schema validation (GATE-05-E004)
- **EARS added** (L3) from old GATE-01
- **BDD added** (L4) from old GATE-01

New layer coverage: `["EARS", "BDD", "ADR"]`

| What changes | Action |
|-------------|--------|
| Title | `Architecture/Contract Gate` → `Requirements & Architecture Gate` |
| `layer_range` | `"L5-L8"` → `"L3-L5"` |
| `layer_names` | `["ADR","SYS","REQ","CTR"]` → `["EARS","BDD","ADR"]` |
| `gate_number` | Remove or change to 3 |
| File name | `GATE-05_ARCHITECTURE_CONTRACT.md` → `GATE-03_REQUIREMENTS_ARCHITECTURE.md` |
| GATE-05-E001 (ADR structure) | Keep, renumber to GATE-03-E001 |
| GATE-05-E002 (SYS quality) | **DELETE** — SYS layer cut |
| GATE-05-E003 (REQ 6 tags) | **DELETE** — REQ layer cut |
| GATE-05-E004 (CTR schema) | **DELETE** — CTR layer cut |
| GATE-05-E005 (breaking API) | **DELETE** — CTR layer cut |
| GATE-05-E006 (security review) | Keep as GATE-03-E002 |
| **NEW** GATE-03-E003 | EARS must follow WHEN-THE-SHALL syntax (moved from old GATE-01) |
| **NEW** GATE-03-E004 | BDD must have Given-When-Then format (moved from old GATE-01) |
| **NEW** GATE-03-E005 | EARS upstream tags: @brd @prd (2 tags, not 6) |
| GATE-05-W003 (ADR alternatives) | Keep |
| Upstream traceability count | `6 tags` → `4 tags` (@brd, @prd, @ears, @bdd for ADR) |
| Section 8 (Contract Deprecation) | **DELETE** — CTR cut |

Error catalog net change: 6E+4W → 7E+4W (dropped 4 SYS/REQ/CTR errors; added 5 errors: 2 from GATE-01 + 2 tag checks + CVE warning ported)

### GATE-06 (was GATE-09): Design & Test Gate (L6-L7)

**Changes needed: MAJOR REWRITE**

Original GATE-09 covered SPEC, TSPEC, TASKS. In v3:
- **SPEC survives** (L7)
- **TSPEC cut** — replaced by TDD (L6)
- **TASKS cut** — AI generates from SPEC on-the-fly

New layer coverage: `["TDD", "SPEC"]`

| What changes | Action |
|-------------|--------|
| Title | `Design/Test Gate` → `Design & Test Gate` |
| `layer_range` | `"L9-L11"` → `"L6-L7"` |
| `layer_names` | `["SPEC","TSPEC","TASKS"]` → `["TDD","SPEC"]` |
| File name | `GATE-09_DESIGN_TEST.md` → `GATE-06_DESIGN_TEST.md` |
| GATE-09-E001 (SPEC readiness >=90%) | Keep, renumber |
| GATE-09-E002 (TSPEC interface coverage) | **REPLACE**: TDD must cover all BDD scenarios |
| GATE-09-E003 (TASKS traceability) | **DELETE** — TASKS cut |
| GATE-09-E004 (TSPEC/SPEC sync) | **REPLACE**: TDD/SPEC sync — SPEC test_contracts must match TDD mappings |
| GATE-09-E005 (SPEC change without TSPEC) | **KEEP** but reword: SPEC change must update TDD first |
| GATE-09-E006 (TASKS dependency cycle) | **DELETE** — TASKS cut |
| GATE-09-W003 (implementation complexity) | Keep |
| Section 8 (TDD Integration with U/I/S/F test types) | **SIMPLIFY**: Replace 4 test type table with TDD document reference |
| UTEST-40/ITEST-41/STEST-42/FTEST-43 codes | **DELETE** — no TSPEC subtype codes in v3 |
| TASKS dependency references throughout | **DELETE** |
| Entry gate routing (Midstream cascade) | Update: GATE-05 → GATE-03 |

Error catalog net change: 6E+5W → 5E+2W (added IPLAN-Ready check)

### GATE-CODE (was GATE-12): Implementation Gate

**Changes needed: MODERATE**

Original GATE-12 covered Code, Tests, Validation (L12-L14). In v3:
- **Code survives** (unnumbered, after L7)
- **Tests (L13) cut** from documentation layers — test files are code, managed by TDD layer
- **Validation (L14) cut** — readiness scores embedded in each layer

| What changes | Action |
|-------------|--------|
| Title | `Implementation Gate` (unchanged) |
| `layer_range` | `"L12-L14"` → `"Code"` |
| `layer_names` | `["Code","Tests","Validation"]` → `["Code"]` |
| File name | `GATE-12_IMPLEMENTATION.md` → `GATE-CODE_IMPLEMENTATION.md` |
| Section 1.1 layers table | Remove Tests (L13), Validation (L14) rows |
| GATE-12-E005 (test coverage) | **REPLACE**: Code changes must pass TDD test suite |
| GATE-12-E006 (validation signoff) | **DELETE** |
| Bubble-up layer references | L13→L12/L10/L9/L8/L7 → Code→SPEC(L7)/TDD(L6)/ADR(L5)/BDD(L4)/EARS(L3) |
| Root cause analysis layers | Update all L-NN refs to v3 layer numbers |

Error catalog net change: 6E+5W → 4E+3W

---

## 4. CHG-TEMPLATE.yaml Changes

### Metadata block
- `change_level.value: L2` → `C2`
- `change_level` guidance table: all L1/L2/L3 → C1/C2/C3

### Change source routing
Replace the `change_source._guidance` table:

```
Current (v2, 14-layer cascade):
Upstream:   PRD→EARS→BDD→ADR→SYS→REQ→CTR→SPEC→TSPEC→TASKS
Midstream:  ADR↔SYS↔REQ, CTR↔SPEC
Downstream: SPEC→REQ→SYS

New (v3, 8-layer cascade):
Upstream:   BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN→Code
Midstream:  ADR→TDD→IPLAN→Code
Downstream: IPLAN→TDD→ADR (bubble-up)
```

### Impact assessment antipatterns
```
Old: "FAIL: changing SPEC without checking upstream REQ/SYS impact"
New: "FAIL: changing SPEC without checking upstream TDD/ADR impact"

Old: "FAIL: changing BRD without cascading to PRD/EARS/BDD"
New: "FAIL: changing BRD without cascading to PRD→EARS→BDD→ADR→TDD→SPEC→Code"
```

### Glossary
```
Old: L1 = Trivial change, L2 = Minor change, L3 = Major change
New: C1 = Trivial change, C2 = Minor change, C3 = Major change
```

---

## 5. Gate Interaction Diagram: Complete Rewrite

The v2 diagram has **8 ASCII-art sections** all referencing L1-L14 ranges. Every diagram needs redrawing. Key changes:

| Diagram | What Changes |
|---------|-------------|
| System Overview | `15-Layer SDD` → `8-Layer SDD`. Gate labels: GATE-01(L1-L4)→(L1-L2), GATE-05(L5-L8)→GATE-03(L3-L5), GATE-09(L9-L11)→GATE-06(L6-L7), GATE-08(L12)→(L8), GATE-12(L12-L14)→GATE-CODE(Code) |
| Gate-to-Layer Mapping | 14 rows → 8 rows + Code |
| Change Source Routing | All `L-NN` ranges remapped |
| Cascade Patterns | 4 patterns → 2 patterns (Full Cascade: GATE-01→03→06→CODE; Midstream: GATE-03→06→CODE with IPLAN) |
| Bubble-Up Pattern | L13→L12/L10/L9/L8/L7 → Code→IPLAN/TDD/SPEC/ADR/BDD/EARS |
| Approval Matrix | Gate column names updated. Approvers per gate unchanged (approval is by gate, not by layer) |
| Quick Reference | Gate selection table updated with new names and ranges |

---

## 6. File Manifest: What's Copied, Modified, or Dropped

### Copied and Modified (10 files)

| Source | Destination | Work |
|--------|-------------|------|
| `CHG-TEMPLATE.yaml` | `CHG/CHG-TEMPLATE.yaml` | Rename L→C; update change_source cascade; update antipatterns; update glossary |
| `CHG-00_index.md` | `CHG/CHG-00_index.md` | Strip 20 unwritten refs (workflows, sources, scripts); update gate descriptions |
| `README.md` | `CHG/README.md` | Update layer count; update gate names; update change level refs |
| `gates/GATE-01_BUSINESS_PRODUCT.md` | `CHG/gates/GATE-01_BUSINESS_PRODUCT.md` | Shrink layer_range L4→L2; remove EARS/BDD error checks |
| `gates/GATE-05_ARCHITECTURE_CONTRACT.md` | `CHG/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md` | Complete rewrite: new artifacts, new error codes |
| `gates/GATE-09_DESIGN_TEST.md` | `CHG/gates/GATE-06_DESIGN_TEST.md` | Rewrite: TDD replaces TSPEC+TASKS |
| `gates/GATE-12_IMPLEMENTATION.md` | `CHG/gates/GATE-CODE_IMPLEMENTATION.md` | Shrink to Code-only; update bubble-up refs |
| `gates/GATE_INTERACTION_DIAGRAM.md` | `CHG/gates/GATE_INTERACTION_DIAGRAM.md` | Complete redraw of 8 diagrams |
| `gates/GATE_ERROR_CATALOG.md` | `CHG/gates/GATE_ERROR_CATALOG.md` | Strip ~15 error codes; add new ones for EARS/BDD/TDD |
| `templates/GATE_APPROVAL_FORM.md` | `CHG/templates/GATE_APPROVAL_FORM.md` | Update gate names; update approver labels |
| `templates/POST_MORTEM-TEMPLATE.md` | `CHG/templates/POST_MORTEM-TEMPLATE.md` | Copy as-is (no layer-specific content) |

### Dropped (23 entries)

| What | Why |
|------|-----|
| `workflows/UPSTREAM_WORKFLOW.md` | Never written — cascade logic embedded in gate docs |
| `workflows/MIDSTREAM_WORKFLOW.md` | Never written |
| `workflows/DESIGN_WORKFLOW.md` | Never written |
| `workflows/DOWNSTREAM_WORKFLOW.md` | Never written |
| `workflows/EMERGENCY_WORKFLOW.md` | Never written |
| `sources/UPSTREAM_CHANGE_GUIDE.md` | Never written |
| `sources/MIDSTREAM_CHANGE_GUIDE.md` | Never written |
| `sources/DOWNSTREAM_CHANGE_GUIDE.md` | Never written |
| `sources/EXTERNAL_CHANGE_GUIDE.md` | Never written |
| `sources/FEEDBACK_CHANGE_GUIDE.md` | Never written |
| `templates/CHG-EMERGENCY-TEMPLATE.md` | Never written — emergency section in main template handles this |
| `scripts/validate_gate01.sh` | Never written — validation is MCP-based in v3 |
| `scripts/validate_gate05.sh` | Never written |
| `scripts/validate_gate09.sh` | Never written |
| `scripts/validate_gate12.sh` | Never written |
| `scripts/validate_chg_routing.py` | Never written |
| `scripts/validate_emergency_bypass.sh` | Never written |
| `scripts/validate_all_gates.sh` | Never written |

---

## 7. Error Code Migration Map

### GATE-01 (Business) — 4E + 3W

| Old Code | New Code | Description |
|----------|----------|-------------|
| GATE-01-E001 | GATE-01-E001 | Business justification documented |
| GATE-01-E002 | GATE-01-E002 | Stakeholder identified |
| GATE-01-E003 | **→ GATE-03-E003** | EARS must follow WHEN-THE-SHALL syntax |
| GATE-01-E004 | **→ GATE-03-E004** | BDD must have Given-When-Then format |
| GATE-01-E005 | GATE-01-E003 | Change source correctly classified |
| GATE-01-E006 | GATE-01-E004 | C3 requires formal stakeholder approval |
| GATE-01-W001-W004 | GATE-01-W001-W003 | Minor renumber |

### GATE-03 (Requirements & Architecture) — 7E + 4W

| Old Code | New Code | Description |
|----------|----------|-------------|
| GATE-05-E001 | GATE-03-E001 | ADR must have Context-Decision-Consequences |
| GATE-05-E002 | **DELETED** | SYS quality attributes — SYS cut |
| GATE-05-E003 | **DELETED** | REQ 6 upstream tags — REQ cut |
| GATE-05-E004 | **DELETED** | CTR schema validation — CTR cut |
| GATE-05-E005 | **DELETED** | Breaking API classification — CTR cut |
| GATE-05-E006 | GATE-03-E002 | Security review for external changes |
| (from GATE-01) | GATE-03-E003 | EARS WHEN-THE-SHALL syntax compliance |
| (from GATE-01) | GATE-03-E004 | BDD Given-When-Then format |
| **NEW** | GATE-03-E005 | EARS upstream tags: @brd @prd (2 tags) |
| **NEW** | GATE-03-E006 | BDD upstream tags: @brd @prd @ears (3 tags) |
| **NEW** | GATE-03-E007 | ADR upstream tags: @brd @prd @ears @bdd (4 tags) |
| GATE-05-W001 | GATE-03-W001 | External security change missing CVE reference |
| GATE-05-W003 | GATE-03-W002 | ADR alternatives documented |
| **NEW** | GATE-03-W003 | BDD edge case coverage |
| **NEW** | GATE-03-W004 | EARS boundary value coverage |

### GATE-06 (Design & Test) — 4E + 2W

| Old Code | New Code | Description |
|----------|----------|-------------|
| GATE-09-E001 | GATE-06-E001 | SPEC CODE-Ready score >=90% |
| GATE-09-E002 | GATE-06-E002 | TDD must cover all BDD scenarios |
| **NEW** | GATE-06-E005 | IPLAN must have executable commands and file manifest |
| GATE-09-E003 | **DELETED** | TASKS traceability — TASKS cut |
| GATE-09-E004 | GATE-06-E003 | TDD/SPEC sync: test_contracts match TDD mappings |
| GATE-09-E005 | GATE-06-E004 | SPEC change must update TDD first |
| GATE-09-E006 | **DELETED** | TASKS dependency cycle — TASKS cut |
| GATE-09-W001 | GATE-06-W001 | Algorithm change without performance baseline |
| GATE-09-W003 | GATE-06-W002 | High implementation complexity |

GATE-09-W002 (edge case coverage) and GATE-09-W005 (missing negative tests) are absorbed
into GATE-06-E002 (TDD must cover all BDD scenarios) — edge cases and negative paths are
BDD scenario variants, validated by the TDD layer's BDD-to-test mapping.

### GATE-CODE (Implementation) — 4E + 3W

| Old Code | New Code | Description |
|----------|----------|-------------|
| GATE-12-E001 | GATE-CODE-E001 | Root cause analysis documented |
| GATE-12-E002 | GATE-CODE-E002 | Fix at correct v3 layer |
| GATE-12-E003 | GATE-CODE-E003 | Regression tests pass |
| GATE-12-E004 | GATE-CODE-E004 | Code review completed |
| GATE-12-E005 | **REPLACED** | Code passes TDD test suite |
| GATE-12-E006 | **DELETED** | Validation sign-off — cut |
| GATE-12-W001 | GATE-CODE-W001 | Performance regression without baseline |
| GATE-12-W005 | GATE-CODE-W002 | Build warning introduced |
| **NEW** | GATE-CODE-W003 | Technical debt documented with tracking ticket |
(GATE-12-W002 edge cases, W003 vague tech debt, W004 no integration coverage —
all absorbed by TDD test suite enforcement in GATE-06-E002 / GATE-CODE-E003)

---

## 8. v3 CHG Directory Structure

```
ucx_flow_v3/CHG/
├── README.md
├── CHG-00_index.md
├── CHG-TEMPLATE.yaml
├── gates/
│   ├── GATE-01_BUSINESS_PRODUCT.md
│   ├── GATE-03_REQUIREMENTS_ARCHITECTURE.md    (was GATE-05)
│   ├── GATE-06_DESIGN_TEST.md                   (was GATE-09)
│   ├── GATE-CODE_IMPLEMENTATION.md              (was GATE-12)
│   ├── GATE_INTERACTION_DIAGRAM.md
│   └── GATE_ERROR_CATALOG.md
└── templates/
    ├── GATE_APPROVAL_FORM.md
    └── POST_MORTEM-TEMPLATE.md
```

**10 files** (down from 35 referenced entries in v2 index). All files are materialized — no placeholder references to unwritten content.

---

## 9. Verification Checklist

- [ ] No `L1/L2/L3` change level references remain — all should be `C1/C2/C3`
- [ ] No v2 layer artifacts referenced: SYS, REQ, CTR, TSPEC (as artifact), TASKS
- [ ] No v2 layer numbers referenced: L6, L7, L8, L9, L10, L11, L12, L13, L14
- [ ] Gate numbers match v3 layer ranges: 01(L1-L2), 03(L3-L5), 06(L6-L7), 08(L8), CODE
- [ ] Error codes reference v3 artifacts only
- [ ] Cascade patterns use v3 chain: BRD→PRD→EARS→BDD→ADR→TDD→SPEC→Code
- [ ] Traceability tag counts match v3 cumulative tags (max 6, not 14)
- [ ] Bubble-up references use v3 layer numbers
- [ ] No references to workflows/, sources/, or scripts/ directories
- [ ] No references to archived/CHG_v1_archive/
- [ ] **CHG-00_index gate descriptions match gate files** (v2 index had wrong descriptions: GATE-05 was listed as "Layers 5,9" instead of L5-L8; GATE-09 as "Layers 3-4,8" instead of L9-L11; GATE-12 as "Layers 10-12" instead of L12-L14)
