---
title: "STEST MVP Validation Rules"
tags:
  - stest-rules
  - validation-rules
  - layer-10-artifact
custom_fields:
  document_type: validation-rules
  artifact_type: STEST
  layer: 10
  test_type_code: 42
  development_status: active
---

# STEST MVP Validation Rules

## Purpose

Validation criteria for smoke test specification documents. Used by `validate_stest.py` script.

## Structural Validation

### Required Sections

| Section | Validation Rule |
|---------|-----------------|
| 1. Document Control | Must contain status, timeout budget |
| 2. Test Scope | Must define deployment context, timeout budget |
| 3. Critical Path Index | Must list all tests with timeouts |
| 4. Test Case Details | Must have pass/fail criteria, rollback |
| 5. Rollback Procedures | Must have global rollback matrix |
| 6. Traceability | Must contain @ears, @bdd, @req tags |

## Element ID Validation

### Format

```
TSPEC.NN.42.SS
```

### Regex Pattern

```regex
^TSPEC\.\d{2,}\.42\.\d{2,}$
```

## Traceability Validation

### Required Tags

| Tag | Pattern | Required |
|-----|---------|----------|
| `@ears` | `EARS\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@bdd` | `BDD\.\d{2,}\.\d{2}\.\d{2,}` | Yes |
| `@req` | `REQ\.\d{2,}\.\d{2}\.\d{2,}` | Yes |

## Content Validation

### Timeout Budget

**Validation rules**:
- Total timeout ≤ 300 seconds
- Individual test timeout ≤ 60 seconds
- Budget table must exist

### Pass/Fail Criteria

**Required format**:

```markdown
| Condition | Result |
|-----------|--------|
| [Success condition] | ✅ PASS |
| [Failure condition] | ❌ FAIL |
```

**Validation**: Must have at least one PASS and one FAIL condition

### Health Check

**Required**: Executable command block

```bash
curl -f https://... --max-time N
```

**Validation**: Must contain curl or equivalent health check command

### Rollback Procedure

**Required format**:

```markdown
| Step | Action | Command |
|------|--------|---------|
| 1 | [Action] | [Command] |
```

**Validation**: Every test must have rollback procedure

## Quality Score Calculation

### Weights

| Component | Weight | Measurement |
|-----------|--------|-------------|
| Critical Paths | 30% | (Covered paths / Total P0 paths) × 100 |
| Timeout Budget | 25% | (Budget compliant / 1) × 100 |
| Rollback Defined | 25% | (Tests with rollback / Total tests) × 100 |
| Health Checks | 20% | (Tests with checks / Total tests) × 100 |

### Formula

```
Score = (Paths × 0.30) + (Timeout × 0.25) + (Rollback × 0.25) + (Health × 0.20)
```

### Pass/Fail

| Score | Status |
|-------|--------|
| 100% | ✅ PASS |
| <100% | ❌ FAIL |

**Note**: STEST requires 100% compliance. No partial passes.

## Validation Output

### Pass Output

```
✅ STEST-01_production.md: PASS (100%)
  - Critical Paths: 100% (4/4)
  - Timeout Budget: 100% (165s/300s)
  - Rollback Defined: 100% (4/4)
  - Health Checks: 100% (4/4)
```

### Fail Output

```
❌ STEST-01_production.md: FAIL (85%)
  - Critical Paths: 100% (4/4)
  - Timeout Budget: 100% (165s/300s)
  - Rollback Defined: 75% (3/4)
    Missing: TSPEC.01.42.03
  - Health Checks: 75% (3/4)
    Missing: TSPEC.01.42.04
```

## See Also

- [STEST-MVP-TEMPLATE.md](STEST-MVP-TEMPLATE.md)
- [STEST_MVP_QUALITY_GATES.md](STEST_MVP_QUALITY_GATES.md)
- [STEST_MVP_CREATION_RULES.md](STEST_MVP_CREATION_RULES.md)
- [../scripts/validate_stest.py](../scripts/validate_stest.py)
