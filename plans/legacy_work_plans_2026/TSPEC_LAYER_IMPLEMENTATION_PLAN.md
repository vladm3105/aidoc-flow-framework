# TSPEC (Test Specifications) Layer Implementation Plan

## Overview

Create Layer 10 TSPEC between SPEC (L9) and TASKS (becomes L11) to formalize test specifications for TDD workflow.

**Location**: `/opt/data/ucx_framework/ai_dev_flow/10_TSPEC/`

---

## 1. Layer Structure

### Directory Layout

```
ai_dev_flow/
├── 10_TSPEC/
│   ├── README.md                              # Layer overview
│   ├── TSPEC-00_index.md                      # Master index
│   ├── TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md
│   │
│   ├── UTEST/                                 # Unit Test Specifications
│   │   ├── UTEST-MVP-TEMPLATE.md
│   │   ├── UTEST-MVP-TEMPLATE.yaml
│   │   ├── UTEST_MVP_SCHEMA.yaml
│   │   ├── UTEST_MVP_CREATION_RULES.md
│   │   ├── UTEST_MVP_VALIDATION_RULES.md
│   │   └── UTEST_MVP_QUALITY_GATES.md
│   │
│   ├── ITEST/                                 # Integration Test Specifications
│   │   ├── ITEST-MVP-TEMPLATE.md
│   │   ├── ITEST-MVP-TEMPLATE.yaml
│   │   ├── ITEST_MVP_SCHEMA.yaml
│   │   ├── ITEST_MVP_CREATION_RULES.md
│   │   ├── ITEST_MVP_VALIDATION_RULES.md
│   │   └── ITEST_MVP_QUALITY_GATES.md
│   │
│   ├── STEST/                                 # Smoke Test Specifications
│   │   ├── STEST-MVP-TEMPLATE.md
│   │   ├── STEST-MVP-TEMPLATE.yaml
│   │   ├── STEST_MVP_SCHEMA.yaml
│   │   ├── STEST_MVP_CREATION_RULES.md
│   │   ├── STEST_MVP_VALIDATION_RULES.md
│   │   └── STEST_MVP_QUALITY_GATES.md
│   │
│   ├── FTEST/                                 # Functional Test Specifications
│   │   ├── FTEST-MVP-TEMPLATE.md
│   │   ├── FTEST-MVP-TEMPLATE.yaml
│   │   ├── FTEST_MVP_SCHEMA.yaml
│   │   ├── FTEST_MVP_CREATION_RULES.md
│   │   ├── FTEST_MVP_VALIDATION_RULES.md
│   │   └── FTEST_MVP_QUALITY_GATES.md
│   │
│   ├── scripts/
│   │   ├── README.md
│   │   ├── validate_utest.py                  # Unit test validator
│   │   ├── validate_itest.py                  # Integration test validator
│   │   ├── validate_stest.py                  # Smoke test validator
│   │   ├── validate_ftest.py                  # Functional test validator
│   │   ├── validate_tspec_quality_score.sh    # Combined score
│   │   └── validate_all_tspec.sh              # Batch all types
│   │
│   └── examples/
│       ├── README.md
│       ├── UTEST-01_auth_service.md
│       ├── ITEST-01_auth_service.md
│       ├── STEST-01_auth_service.md
│       └── FTEST-01_auth_service.md
│
└── 11_TASKS/  (renumbered from 10_TASKS)
```

---

## 2. Test Type Categories

| Code | Type | Abbreviation | Source Artifacts | Purpose |
|------|------|--------------|------------------|---------|
| 40 | Unit Test | UT | REQ (L7), SPEC (L9) | Individual function tests |
| 41 | Integration Test | IT | CTR (L8), SYS (L6), SPEC (L9) | Component interaction |
| 42 | Smoke Test | ST | EARS (L3), BDD (L4), REQ (L7) | Post-deployment health |
| 43 | Functional Test | FT | SYS (L6) | System behavior validation |
| 44-45 | Reserved | - | - | Future (performance, security) |

**Note**: Acceptance tests remain in BDD (L4), not duplicated.

---

## 3. Element ID Format

**Format**: `TSPEC.NN.TT.SS`

- `NN` = Document number
- `TT` = Test type code (40-45)
- `SS` = Sequential test case number

**Examples**:
- `TSPEC.01.40.01` = Doc 1, Unit Test #1
- `TSPEC.01.41.03` = Doc 1, Integration Test #3
- `TSPEC.01.42.01` = Doc 1, Smoke Test #1
- `TSPEC.01.43.02` = Doc 1, Functional Test #2

---

## 4. Template Sections by Test Type

### UTEST (Unit Test Specifications)

| Section | Content |
|---------|---------|
| 1. Document Control | Status, version, TASKS-Ready score |
| 2. Test Scope | Component, SPEC ref, coverage target (≥90%) |
| 3. Test Case Index | ID, name, category, REQ coverage, priority |
| 4. Test Case Details | I/O tables, pseudocode, error cases |
| 5. REQ Coverage Matrix | REQ ID → Test IDs mapping |
| 6. Traceability | `@req`, `@spec` (required) |

**Required Tags**: `@req`, `@spec`
**Categories**: `[Logic]`, `[State]`, `[Validation]`, `[Edge]`

### ITEST (Integration Test Specifications)

| Section | Content |
|---------|---------|
| 1. Document Control | Status, version, TASKS-Ready score |
| 2. Test Scope | Components involved, dependencies |
| 3. Test Case Index | ID, name, components, CTR coverage |
| 4. Test Case Details | Contract compliance, sequence diagrams |
| 5. CTR Coverage Matrix | CTR endpoint → Test IDs mapping |
| 6. Traceability | `@ctr`, `@sys`, `@spec` (required) |

**Required Tags**: `@ctr`, `@sys`, `@spec`
**Focus**: API contracts, component interactions, data flows

### STEST (Smoke Test Specifications)

| Section | Content |
|---------|---------|
| 1. Document Control | Status, version |
| 2. Test Scope | Deployment target, timeout budget (<5min) |
| 3. Critical Path Index | ID, path, timeout, rollback trigger |
| 4. Test Case Details | Pass/fail criteria, health checks |
| 5. Rollback Procedures | Failure actions per test |
| 6. Traceability | `@ears`, `@bdd`, `@req` (required) |

**Required Tags**: `@ears`, `@bdd`, `@req`
**Constraints**: Total suite <5 minutes, fail-fast

### FTEST (Functional Test Specifications)

| Section | Content |
|---------|---------|
| 1. Document Control | Status, version |
| 2. Test Scope | System workflows, quality attributes |
| 3. Test Case Index | ID, name, SYS coverage, quality attribute |
| 4. Test Case Details | Workflow steps, threshold validation |
| 5. SYS Coverage Matrix | SYS ID → Test IDs mapping |
| 6. Traceability | `@sys` (required), `@threshold` |

**Required Tags**: `@sys`, `@threshold`
**Focus**: Performance, reliability, security, scalability

---

## 5. Traceability Tags

**Required upstream tags (9 total)**:
```
@brd, @prd, @ears, @bdd, @adr, @sys, @req, @ctr, @spec
```

**Plus**: `@threshold` for quantitative values

**Downstream**:
```
@tasks: TASKS-NN
@code: tests/unit/, tests/integration/, etc.
```

---

## 6. Quality Gates by Test Type

### UTEST Quality Gates (≥90% target)

| Gate | Weight | Criteria |
|------|--------|----------|
| REQ Coverage | 30% | Every REQ has ≥1 unit test |
| I/O Tables | 25% | Every test has input/output table |
| Category Prefixes | 15% | All tests use [Logic]/[State]/[Validation]/[Edge] |
| Pseudocode | 15% | Executable pseudocode present |
| Error Cases | 15% | Error conditions documented |

### ITEST Quality Gates (≥85% target)

| Gate | Weight | Criteria |
|------|--------|----------|
| CTR Coverage | 30% | Every CTR endpoint has ≥1 test |
| Contract Compliance | 25% | Schema validation defined |
| Sequence Diagrams | 20% | Component interactions visualized |
| Side Effects | 15% | Database/state changes verified |
| Traceability | 10% | @ctr, @sys, @spec tags present |

### STEST Quality Gates (100% required)

| Gate | Weight | Criteria |
|------|--------|----------|
| Critical Paths | 30% | All P0 paths covered |
| Timeout Budget | 25% | Total suite <5 minutes |
| Rollback Defined | 25% | Every test has failure action |
| Health Checks | 20% | Connectivity, API response verified |

### FTEST Quality Gates (≥85% target)

| Gate | Weight | Criteria |
|------|--------|----------|
| SYS Coverage | 30% | Quality attributes have tests |
| Threshold Refs | 25% | All metrics use @threshold |
| Workflow Steps | 25% | End-to-end flows documented |
| Measurement | 20% | Metrics collection defined |

---

## 7. Files to Create

### Layer Root (High Priority)

| File | Description |
|------|-------------|
| `10_TSPEC/README.md` | Layer overview, test type guide |
| `10_TSPEC/TSPEC-00_index.md` | Master index all test specs |
| `10_TSPEC/TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md` | Combined matrix |

### UTEST Subdirectory (High Priority)

| File | Description |
|------|-------------|
| `UTEST/UTEST-MVP-TEMPLATE.md` | Unit test template |
| `UTEST/UTEST-MVP-TEMPLATE.yaml` | YAML version |
| `UTEST/UTEST_MVP_SCHEMA.yaml` | Validation schema |
| `UTEST/UTEST_MVP_CREATION_RULES.md` | AI guidance |
| `UTEST/UTEST_MVP_VALIDATION_RULES.md` | Validation rules |
| `UTEST/UTEST_MVP_QUALITY_GATES.md` | Quality gate criteria |

### ITEST Subdirectory (High Priority)

| File | Description |
|------|-------------|
| `ITEST/ITEST-MVP-TEMPLATE.md` | Integration test template |
| `ITEST/ITEST-MVP-TEMPLATE.yaml` | YAML version |
| `ITEST/ITEST_MVP_SCHEMA.yaml` | Validation schema |
| `ITEST/ITEST_MVP_CREATION_RULES.md` | AI guidance |
| `ITEST/ITEST_MVP_VALIDATION_RULES.md` | Validation rules |
| `ITEST/ITEST_MVP_QUALITY_GATES.md` | Quality gate criteria |

### STEST Subdirectory (High Priority)

| File | Description |
|------|-------------|
| `STEST/STEST-MVP-TEMPLATE.md` | Smoke test template |
| `STEST/STEST-MVP-TEMPLATE.yaml` | YAML version |
| `STEST/STEST_MVP_SCHEMA.yaml` | Validation schema |
| `STEST/STEST_MVP_CREATION_RULES.md` | AI guidance |
| `STEST/STEST_MVP_VALIDATION_RULES.md` | Validation rules |
| `STEST/STEST_MVP_QUALITY_GATES.md` | Quality gate criteria |

### FTEST Subdirectory (High Priority)

| File | Description |
|------|-------------|
| `FTEST/FTEST-MVP-TEMPLATE.md` | Functional test template |
| `FTEST/FTEST-MVP-TEMPLATE.yaml` | YAML version |
| `FTEST/FTEST_MVP_SCHEMA.yaml` | Validation schema |
| `FTEST/FTEST_MVP_CREATION_RULES.md` | AI guidance |
| `FTEST/FTEST_MVP_VALIDATION_RULES.md` | Validation rules |
| `FTEST/FTEST_MVP_QUALITY_GATES.md` | Quality gate criteria |

### Scripts (Medium Priority)

| File | Description |
|------|-------------|
| `scripts/README.md` | Script documentation |
| `scripts/validate_utest.py` | Unit test validator |
| `scripts/validate_itest.py` | Integration test validator |
| `scripts/validate_stest.py` | Smoke test validator |
| `scripts/validate_ftest.py` | Functional test validator |
| `scripts/validate_tspec_quality_score.sh` | Combined score |
| `scripts/validate_all_tspec.sh` | Batch all types |

### Examples (Medium Priority)

| File | Description |
|------|-------------|
| `examples/README.md` | Examples guide |
| `examples/UTEST-01_auth_service.md` | Unit test example |
| `examples/ITEST-01_auth_service.md` | Integration test example |
| `examples/STEST-01_auth_service.md` | Smoke test example |
| `examples/FTEST-01_auth_service.md` | Functional test example |

### Total Files: 38

---

## 8. Updates to Existing Files

| File | Change |
|------|--------|
| `ai_dev_flow/ID_NAMING_STANDARDS.md` | Add TSPEC section with codes 40-45 |
| `ai_dev_flow/LAYER_REGISTRY.yaml` | Add L10 TSPEC, renumber TASKS to L11 |
| `ai_dev_flow/TESTING_STRATEGY_TDD.md` | Add TSPEC references in workflow |
| `ai_dev_flow/TRACEABILITY.md` | Add TSPEC layer |
| Rename `10_TASKS/` → `11_TASKS/` | Directory rename |

---

## 9. Migration from REQ Section 8

**Current**: REQ Section 8 contains Logical TDD tables

**After**:
1. REQ Section 8 keeps summary only with reference: `See TSPEC-NN`
2. Detailed test specs move to TSPEC
3. Add `@tspec` tag to REQ documents

---

## 10. Implementation Order

### Phase 1: Directory Structure & Layer Root
1. Create `10_TSPEC/` directory with subdirectories (UTEST, ITEST, STEST, FTEST, scripts, examples)
2. Create `10_TSPEC/README.md` (layer overview)
3. Create `10_TSPEC/TSPEC-00_index.md` (master index)
4. Rename `10_TASKS/` → `11_TASKS/`

### Phase 2: UTEST (Unit Tests) - TDD Priority
5. Create `UTEST/UTEST-MVP-TEMPLATE.md`
6. Create `UTEST/UTEST_MVP_CREATION_RULES.md`
7. Create `UTEST/UTEST_MVP_VALIDATION_RULES.md`
8. Create `UTEST/UTEST_MVP_QUALITY_GATES.md`
9. Create `scripts/validate_utest.py`

### Phase 3: ITEST (Integration Tests)
10. Create `ITEST/ITEST-MVP-TEMPLATE.md`
11. Create `ITEST/ITEST_MVP_CREATION_RULES.md`
12. Create `ITEST/ITEST_MVP_VALIDATION_RULES.md`
13. Create `ITEST/ITEST_MVP_QUALITY_GATES.md`
14. Create `scripts/validate_itest.py`

### Phase 4: STEST (Smoke Tests)
15. Create `STEST/STEST-MVP-TEMPLATE.md`
16. Create `STEST/STEST_MVP_CREATION_RULES.md`
17. Create `STEST/STEST_MVP_VALIDATION_RULES.md`
18. Create `STEST/STEST_MVP_QUALITY_GATES.md`
19. Create `scripts/validate_stest.py`

### Phase 5: FTEST (Functional Tests)
20. Create `FTEST/FTEST-MVP-TEMPLATE.md`
21. Create `FTEST/FTEST_MVP_CREATION_RULES.md`
22. Create `FTEST/FTEST_MVP_VALIDATION_RULES.md`
23. Create `FTEST/FTEST_MVP_QUALITY_GATES.md`
24. Create `scripts/validate_ftest.py`

### Phase 6: Framework Updates
25. Update `ID_NAMING_STANDARDS.md` (add UTEST/ITEST/STEST/FTEST codes)
26. Update `LAYER_REGISTRY.yaml` (L10 TSPEC, L11 TASKS)
27. Update `TESTING_STRATEGY_TDD.md` (add TSPEC layer references)
28. Update `TRACEABILITY.md`

### Phase 7: Examples & Finalization
29. Create example documents (one per test type)
30. Create YAML templates and schemas
31. Create batch validation scripts
32. Create traceability matrix template

---

## 11. Verification

After implementation:
1. Run `validate_tspec.py` on example document
2. Verify layer numbering in LAYER_REGISTRY.yaml
3. Check ID format compliance in ID_NAMING_STANDARDS.md
4. Validate traceability chain works end-to-end
5. Confirm TASKS references updated to Layer 11
