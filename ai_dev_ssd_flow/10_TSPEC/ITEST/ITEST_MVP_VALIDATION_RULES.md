---
title: "ITEST MVP Validation Rules"
tags:
  - itest-rules
  - validation-rules
  - layer-10-artifact
custom_fields:
  document_type: validation-rules
  artifact_type: ITEST
  layer: 10
  test_type_code: 41
  development_status: active
---

# ITEST MVP Validation Rules

## Purpose

Validation criteria for integration test specification documents. Used by `validate_itest.py` script.

## Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL ITEST documents MUST be in nested folders.

**Required Structure**: `docs/10_TSPEC/ITEST/ITEST-NN_{slug}/ITEST-NN_{slug}.md`

**Validation**:
1. Check document is inside a nested folder
2. Verify folder name matches ITEST ID pattern
3. Verify file name matches folder name
4. Parent path must be: `docs/10_TSPEC/ITEST/`

**This check is BLOCKING** - ITEST must pass folder structure validation before other checks proceed.

---

## Structural Validation

### Required Sections

| Section | Validation Rule |
|---------|-----------------|
| 1. Document Control | Must contain status, version, TASKS-Ready score |
| 2. Test Scope | Must define components, integration points |
| 3. Test Case Index | Must list all test cases with IDs |
| 4. Test Case Details | Must have contract tables and sequences |
| 5. CTR Coverage Matrix | Must map all CTR endpoints to tests |
| 6. Traceability | Must contain @ctr, @sys, @spec tags |

### YAML Frontmatter

Required fields:

```yaml
title: "ITEST-NN: [Title]"
tags:
  - itest-document
  - layer-10-artifact
custom_fields:
  artifact_type: ITEST
  test_type_code: 41
```

## Element ID Validation

### Format

```
TSPEC.NN.41.SS
```

### Rules

| Rule | Validation |
|------|------------|
| Prefix | Must be `TSPEC` |
| Doc number | Must match document filename |
| Type code | Must be `41` for integration tests |
| Sequence | Must be unique within document |

### Regex Pattern

```regex
^TSPEC\.\d{2,}\.\d{2}\.\d{2,}$
```

## Traceability Validation

### Cumulative Tags (Layer 10 - 8-9 Required)

| Tag | Pattern | Required |
|-----|---------|----------|
| `@brd` | `BRD\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@prd` | `PRD\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@ears` | `EARS\.\d{2,}\.25\.\d{2,}` | Yes |
| `@bdd` | `BDD\.\d{2,}\.14\.\d{2,}` | Yes |
| `@adr` | `ADR-\d{2,}` | Yes |
| `@sys` | `SYS\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@req` | `REQ\.\d{2,}\.27\.\d{2,}` | Yes |
| `@spec` | `SPEC-\d{2,}` | Yes |
| `@ctr` | `CTR-\d{2,}` | If exists |

### ITEST-Specific Tags

| Tag | Pattern | Required |
|-----|---------|----------|
| `@ctr` | `CTR-\d{2,}` | Yes |
| `@sys` | `SYS\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@spec` | `SPEC-\d{2,}` | Yes |

### Tag Location

- `@ctr` must appear in Test Case Details section
- `@sys` must appear in Test Scope or Test Case Details
- `@spec` must appear in Document Control

## Content Validation

### Contract Compliance Tables

**Required format**:

```markdown
| Aspect | Expected | Validation |
|--------|----------|------------|
```

**Validation rules**:
- Must have header row
- Must include Request Schema, Response Schema, Status Code
- Expected column cannot be empty

### Sequence Diagrams

**Required format**:

```markdown
```mermaid
sequenceDiagram
    ...
```
```

**Validation rules**:
- Must use Mermaid sequenceDiagram syntax
- Must include all components mentioned in test
- Required for tests involving >2 components

### Side Effects

**Required format**:

```markdown
| Effect | Verification |
|--------|--------------|
```

**Validation**: At least 1 side effect documented per test

## Coverage Validation

### CTR Coverage Matrix

| Validation | Criteria |
|------------|----------|
| Completeness | All CTR endpoints must appear in matrix |
| Mapping | Each endpoint must map to ≥1 test ID |
| Coverage % | Must calculate and display percentage |

### Minimum Coverage

| Metric | Threshold |
|--------|-----------|
| CTR coverage | ≥85% |
| Sequence diagrams | ≥1 for complex flows |

## Quality Score Calculation

### Weights

| Component | Weight | Measurement |
|-----------|--------|-------------|
| CTR Coverage | 30% | (Covered endpoints / Total endpoints) × 100 |
| Contract Compliance | 25% | (Tests with tables / Total tests) × 100 |
| Sequence Diagrams | 20% | (Tests with diagrams / Multi-component tests) × 100 |
| Side Effects | 15% | (Tests with effects / Total tests) × 100 |
| Traceability | 10% | (Required tags present) × 100 |

### Formula

```
Score = (CTR × 0.30) + (Contract × 0.25) + (Seq × 0.20) + (Effects × 0.15) + (Trace × 0.10)
```

### Pass/Fail

| Score | Status |
|-------|--------|
| ≥85% | PASS |
| 75-84% | WARN |
| <75% | FAIL |

## Validation Output

### Pass Output

```
[PASS] ITEST-01_auth_service.md: PASS (88%)
  - CTR Coverage: 90% (9/10)
  - Contract Tables: 100% (8/8)
  - Sequence Diagrams: 80% (4/5)
  - Side Effects: 88% (7/8)
  - Traceability: 100% (3/3)
```

### Fail Output

```
[FAIL] ITEST-01_auth_service.md: FAIL (72%)
  - CTR Coverage: 70% (7/10)
    Missing: /api/v1/logout, /api/v1/refresh
  - Contract Tables: 75% (6/8)
    Missing: TSPEC.01.41.03, TSPEC.01.41.07
  - Sequence Diagrams: 60% (3/5)
  - Side Effects: 75% (6/8)
  - Traceability: 67% (2/3)
```

## See Also

- [ITEST-MVP-TEMPLATE.md](ITEST-MVP-TEMPLATE.md)
- [ITEST_MVP_QUALITY_GATES.md](ITEST_MVP_QUALITY_GATES.md)
- [ITEST_MVP_CREATION_RULES.md](ITEST_MVP_CREATION_RULES.md)
- [../scripts/validate_itest.py](../scripts/validate_itest.py)

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
