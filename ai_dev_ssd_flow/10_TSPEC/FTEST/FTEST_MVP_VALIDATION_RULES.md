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

## Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL FTEST documents MUST be in nested folders.

**Required Structure**: `docs/10_TSPEC/FTEST/FTEST-NN_{slug}/FTEST-NN_{slug}.md`

**Validation**:
1. Check document is inside a nested folder
2. Verify folder name matches FTEST ID pattern
3. Verify file name matches folder name
4. Parent path must be: `docs/10_TSPEC/FTEST/`

**This check is BLOCKING** - FTEST must pass folder structure validation before other checks proceed.

---

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

### FTEST-Specific Tags

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

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
