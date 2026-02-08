---
title: "UTEST MVP Validation Rules"
tags:
  - utest-rules
  - validation-rules
  - layer-10-artifact
custom_fields:
  document_type: validation-rules
  artifact_type: UTEST
  layer: 10
  test_type_code: 40
  development_status: active
---

# UTEST MVP Validation Rules

## Purpose

Validation criteria for unit test specification documents. Used by `validate_utest.py` script.

## Structural Validation

### Required Sections

| Section | Validation Rule |
|---------|-----------------|
| 1. Document Control | Must contain status, version, TASKS-Ready score |
| 2. Test Scope | Must define component, SPEC ref, coverage target |
| 3. Test Case Index | Must list all test cases with IDs |
| 4. Test Case Details | Must have I/O tables and pseudocode |
| 5. REQ Coverage Matrix | Must map all REQs to tests |
| 6. Traceability | Must contain @req and @spec tags |

### YAML Frontmatter

Required fields:

```yaml
title: "UTEST-NN: [Title]"
tags:
  - utest-document
  - layer-10-artifact
custom_fields:
  artifact_type: UTEST
  test_type_code: 40
```

## Element ID Validation

### Format

```
TSPEC.NN.40.SS
```

### Rules

| Rule | Validation |
|------|------------|
| Prefix | Must be `TSPEC` |
| Doc number | Must match document filename |
| Type code | Must be `40` for unit tests |
| Sequence | Must be unique within document |

### Regex Pattern

```regex
^TSPEC\.\d{2,}\.\d{2}\.\d{2,}$
```

## Traceability Validation

### Required Tags

| Tag | Pattern | Required |
|-----|---------|----------|
| `@req` | `REQ\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@spec` | `SPEC-\d{2,}` | Yes |

### Tag Location

- `@req` must appear in Test Case Details section
- `@spec` must appear in Document Control or Test Scope

### Coverage Rule

Every test case MUST have at least one `@req` reference.

## Content Validation

### I/O Tables

**Required format**:

```markdown
| Input | Expected Output | Notes |
|-------|-----------------|-------|
```

**Validation rules**:
- Must have header row
- Must have at least 3 data rows
- Input column cannot be empty
- Expected Output column cannot be empty

### Pseudocode

**Required keywords**:
- `GIVEN` (precondition)
- `WHEN` (action)
- `THEN` (assertion)

**Validation**: At least one Given-When-Then block per test case

### Error Cases

**Required format**:

```markdown
| Error Condition | Expected Behavior |
|-----------------|-------------------|
```

**Validation**: At least 1 error case per test

### Category Prefixes

**Valid categories**:
- `[Logic]`
- `[State]`
- `[Validation]`
- `[Edge]`

**Validation**: Every test case name must include one category prefix

## Coverage Validation

### REQ Coverage Matrix

| Validation | Criteria |
|------------|----------|
| Completeness | All referenced REQs must appear in matrix |
| Mapping | Each REQ must map to ≥1 test ID |
| Coverage % | Must calculate and display percentage |

### Minimum Coverage

| Metric | Threshold |
|--------|-----------|
| REQ coverage | ≥90% |
| Category coverage | 4/4 categories used |

## Quality Score Calculation

### Weights

| Component | Weight | Measurement |
|-----------|--------|-------------|
| REQ Coverage | 30% | (Covered REQs / Total REQs) × 100 |
| I/O Tables | 25% | (Tests with tables / Total tests) × 100 |
| Category Prefixes | 15% | (Tests with prefix / Total tests) × 100 |
| Pseudocode | 15% | (Tests with pseudocode / Total tests) × 100 |
| Error Cases | 15% | (Tests with errors / Total tests) × 100 |

### Formula

```
Score = (REQ × 0.30) + (IO × 0.25) + (Cat × 0.15) + (Pseudo × 0.15) + (Err × 0.15)
```

### Pass/Fail

| Score | Status |
|-------|--------|
| ≥90% | PASS |
| 80-89% | WARN |
| <80% | FAIL |

## Validation Output

### Pass Output

```
✅ UTEST-01_auth_service.md: PASS (92%)
  - REQ Coverage: 95% (30/30)
  - I/O Tables: 100% (25/25)
  - Categories: 100% (25/25)
  - Pseudocode: 80% (20/25)
  - Error Cases: 88% (22/25)
```

### Fail Output

```
❌ UTEST-01_auth_service.md: FAIL (78%)
  - REQ Coverage: 70% (21/30)
    Missing: REQ.01.10.05, REQ.01.10.08
  - I/O Tables: 80% (20/25)
    Missing: TSPEC.01.40.03, TSPEC.01.40.07
  - Categories: 100% (25/25)
  - Pseudocode: 60% (15/25)
  - Error Cases: 72% (18/25)
```

## Automated Checks

The validator script performs:

1. YAML frontmatter parsing
2. Section presence check
3. Element ID format validation
4. Traceability tag extraction
5. I/O table detection
6. Pseudocode keyword search
7. Coverage matrix analysis
8. Quality score calculation

## See Also

- [UTEST-MVP-TEMPLATE.md](UTEST-MVP-TEMPLATE.md)
- [UTEST_MVP_QUALITY_GATES.md](UTEST_MVP_QUALITY_GATES.md)
- [UTEST_MVP_CREATION_RULES.md](UTEST_MVP_CREATION_RULES.md)
- [../scripts/validate_utest.py](../scripts/validate_utest.py)
