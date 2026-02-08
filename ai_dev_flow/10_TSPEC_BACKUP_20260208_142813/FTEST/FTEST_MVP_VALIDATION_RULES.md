---
title: "FTEST MVP Validation Rules"
tags:
  - ftest-rules
  - validation-rules
  - layer-10-artifact
custom_fields:
  document_type: validation-rules
  artifact_type: FTEST
  layer: 10
  test_type_code: 43
  development_status: active
---

# FTEST MVP Validation Rules

## Purpose

Validation criteria for functional test specification documents. Used by `validate_ftest.py` script.

## Structural Validation

### Required Sections

| Section | Validation Rule |
|---------|-----------------|
| 1. Document Control | Must contain status, version, TASKS-Ready score |
| 2. Test Scope | Must define system, quality attributes, thresholds |
| 3. Test Case Index | Must list all test cases with IDs |
| 4. Test Case Details | Must have threshold tables, workflows |
| 5. SYS Coverage Matrix | Must map all SYS requirements to tests |
| 6. Traceability | Must contain @sys, @threshold tags |

## Element ID Validation

### Format

```
TSPEC.NN.43.SS
```

### Regex Pattern

```regex
^TSPEC\.\d{2,}\.43\.\d{2,}$
```

## Traceability Validation

### Required Tags

| Tag | Pattern | Required |
|-----|---------|----------|
| `@sys` | `SYS\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@threshold` | `TH-[A-Z]+-\d{3}` | Yes |

## Content Validation

### Threshold Validation Tables

**Required format**:

```markdown
| Metric | Threshold | Measurement |
|--------|-----------|-------------|
```

**Validation rules**:
- Must have header row
- Threshold column must have numeric values
- Measurement column describes methodology

### Workflow Steps

**Required format**:

```markdown
| Step | Action | Expected Result |
|------|--------|-----------------|
```

**Validation**: At least 3 workflow steps per test

### Measurement Methodology

**Required**: Code block with measurement logic

**Validation**: Must contain assertion or comparison

## Quality Score Calculation

### Weights

| Component | Weight | Measurement |
|-----------|--------|-------------|
| SYS Coverage | 30% | (Covered SYS / Total SYS) × 100 |
| Threshold Refs | 25% | (Tests with threshold / Total tests) × 100 |
| Workflow Steps | 25% | (Tests with workflows / Total tests) × 100 |
| Measurement | 20% | (Tests with code / Total tests) × 100 |

### Formula

```
Score = (SYS × 0.30) + (Threshold × 0.25) + (Workflow × 0.25) + (Measurement × 0.20)
```

### Pass/Fail

| Score | Status |
|-------|--------|
| ≥85% | PASS |
| 75-84% | WARN |
| <75% | FAIL |

## See Also

- [FTEST-MVP-TEMPLATE.md](FTEST-MVP-TEMPLATE.md)
- [FTEST_MVP_QUALITY_GATES.md](FTEST_MVP_QUALITY_GATES.md)
- [FTEST_MVP_CREATION_RULES.md](FTEST_MVP_CREATION_RULES.md)
- [../scripts/validate_ftest.py](../scripts/validate_ftest.py)
