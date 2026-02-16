---
title: "UTEST MVP Quality Gates"
tags:
  - utest-rules
  - quality-gates
  - layer-10-artifact
custom_fields:
  document_type: quality-gates
  artifact_type: UTEST
  layer: 10
  test_type_code: 40
  development_status: active
---

# UTEST MVP Quality Gates

## Purpose

Define quality gate criteria for unit test specifications to ensure TASKS-readiness.

## Quality Gate Summary

| Gate | Weight | Target | Description |
|------|--------|--------|-------------|
| GATE-01 | 30% | 100% | REQ Coverage |
| GATE-02 | 25% | 100% | I/O Tables |
| GATE-03 | 15% | 100% | Category Prefixes |
| GATE-04 | 15% | 100% | Pseudocode |
| GATE-05 | 15% | 100% | Error Cases |

**Overall Target**: ≥90%

---

## GATE-01: REQ Coverage (30%)

### Criteria

Every REQ referenced in the SPEC must have at least one unit test.

### Measurement

```
Coverage = (REQs with tests / Total REQs) × 100
```

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% coverage | Full pass |
| 90-99% coverage | Conditional pass |
| <90% coverage | Fail |

### Evidence Required

- REQ Coverage Matrix completed
- All REQ IDs mapped to test IDs
- No orphan REQs

### Remediation

If coverage <100%:
1. Identify missing REQs
2. Create test cases for each
3. Update coverage matrix
4. Re-validate

---

## GATE-02: I/O Tables (25%)

### Criteria

Every test case must include an Input/Output table.

### Measurement

```
Score = (Tests with I/O table / Total tests) × 100
```

### Table Requirements

| Requirement | Validation |
|-------------|------------|
| Header row | `| Input | Expected Output | Notes |` |
| Minimum rows | 3 data rows |
| No empty cells | Input and Output columns filled |

### Evidence Required

- Each test case section contains I/O table
- Tables follow standard format
- Happy path, error, and edge cases included

### Remediation

If score <100%:
1. List tests without tables
2. Add I/O table to each
3. Ensure minimum 3 rows
4. Re-validate

---

## GATE-03: Category Prefixes (15%)

### Criteria

Every test case name must include a category prefix.

### Valid Categories

| Category | Code | Use Case |
|----------|------|----------|
| `[Logic]` | L | Business logic, calculations |
| `[State]` | S | State transitions, lifecycle |
| `[Validation]` | V | Input validation, schema |
| `[Edge]` | E | Boundaries, limits |

### Measurement

```
Score = (Tests with prefix / Total tests) × 100
```

### Evidence Required

- Test Case Index shows categories
- Test Case Details headers include prefix
- All 4 categories used (recommended)

### Remediation

If score <100%:
1. Review test case names
2. Classify each by function
3. Add appropriate prefix
4. Re-validate

---

## GATE-04: Pseudocode (15%)

### Criteria

Complex test logic must include executable pseudocode.

### Required Keywords

```
GIVEN - Precondition setup
WHEN - Action execution
THEN - Assertion/verification
AND - Additional assertions (optional)
```

### Measurement

```
Score = (Tests with pseudocode / Total tests) × 100
```

### Minimum Standard

Each test case should have:
- At least one GIVEN clause
- Exactly one WHEN clause
- At least one THEN clause

### Evidence Required

- Pseudocode block present in Test Case Details
- Keywords properly formatted
- Logic matches I/O table

### Remediation

If score <100%:
1. Identify tests without pseudocode
2. Write Given-When-Then blocks
3. Ensure consistency with I/O tables
4. Re-validate

---

## GATE-05: Error Cases (15%)

### Criteria

Every test case must document error handling.

### Measurement

```
Score = (Tests with error cases / Total tests) × 100
```

### Table Requirements

| Requirement | Validation |
|-------------|------------|
| Header | `| Error Condition | Expected Behavior |` |
| Minimum rows | 1 error case |
| Specific behaviors | Exception type or error message |

### Evidence Required

- Error Cases table in each test section
- Specific error conditions named
- Expected behaviors defined

### Remediation

If score <100%:
1. List tests without error tables
2. Identify potential errors
3. Document expected behaviors
4. Re-validate

---

## Combined Score Calculation

### Formula

```
Total = (G1 × 0.30) + (G2 × 0.25) + (G3 × 0.15) + (G4 × 0.15) + (G5 × 0.15)
```

### Example Calculation

| Gate | Score | Weight | Contribution |
|------|-------|--------|--------------|
| GATE-01 | 95% | 0.30 | 28.5 |
| GATE-02 | 100% | 0.25 | 25.0 |
| GATE-03 | 100% | 0.15 | 15.0 |
| GATE-04 | 80% | 0.15 | 12.0 |
| GATE-05 | 90% | 0.15 | 13.5 |
| **Total** | | | **94.0%** |

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥90% | ✅ PASS | Proceed to TASKS |
| 80-89% | ⚠️ WARN | Review and improve |
| <80% | ❌ FAIL | Remediation required |

---

## TASKS-Ready Checklist

Before proceeding to TASKS generation:

- [ ] Overall score ≥90%
- [ ] No GATE at <80%
- [ ] All REQs covered
- [ ] I/O tables complete
- [ ] Pseudocode reviewed
- [ ] Error cases documented
- [ ] Traceability tags present

## Validation Command

```bash
python scripts/validate_utest.py docs/10_TSPEC/UTEST/UTEST-NN_*.md --quality-gates
```

## See Also

- [UTEST_MVP_VALIDATION_RULES.md](UTEST_MVP_VALIDATION_RULES.md)
- [UTEST_MVP_CREATION_RULES.md](UTEST_MVP_CREATION_RULES.md)
- [../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md](../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md)
