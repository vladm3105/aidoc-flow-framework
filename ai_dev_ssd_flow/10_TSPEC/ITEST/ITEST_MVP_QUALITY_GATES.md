---
title: "ITEST MVP Quality Gates"
tags:
  - itest-rules
  - quality-gates
  - layer-10-artifact
custom_fields:
  document_type: quality-gates
  artifact_type: ITEST
  layer: 10
  test_type_code: 41
  development_status: active
---

# ITEST MVP Quality Gates

## Purpose

Define quality gate criteria for integration test specifications to ensure TASKS-readiness.

## Quality Gate Summary

| Gate | Weight | Target | Description |
|------|--------|--------|-------------|
| GATE-01 | 30% | 100% | CTR Coverage |
| GATE-02 | 25% | 100% | Contract Compliance |
| GATE-03 | 20% | 100% | Sequence Diagrams |
| GATE-04 | 15% | 100% | Side Effects |
| GATE-05 | 10% | 100% | Traceability |

**Overall Target**: ≥85%

---

## GATE-01: CTR Coverage (30%)

### Criteria

Every CTR endpoint must have at least one integration test.

### Measurement

```
Coverage = (Endpoints with tests / Total CTR endpoints) × 100
```

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% coverage | Full pass |
| 85-99% coverage | Conditional pass |
| <85% coverage | Fail |

### Evidence Required

- CTR Coverage Matrix completed
- All endpoints mapped to test IDs
- No orphan endpoints

---

## GATE-02: Contract Compliance (25%)

### Criteria

Every test case must include a contract compliance table.

### Table Requirements

| Required Aspect | Description |
|-----------------|-------------|
| Request Schema | JSON schema or example |
| Response Schema | JSON schema or example |
| Status Codes | All possible codes listed |
| Headers | Content-Type, Authorization |

### Measurement

```
Score = (Tests with contract table / Total tests) × 100
```

---

## GATE-03: Sequence Diagrams (20%)

### Criteria

Multi-component interactions must include sequence diagrams.

### Applicability

| Test Type | Diagram Required |
|-----------|------------------|
| Single component | Optional |
| 2 components | Recommended |
| 3+ components | Required |

### Measurement

```
Score = (Multi-component tests with diagrams / Multi-component tests) × 100
```

### Diagram Requirements

- Valid Mermaid syntax
- All participants named
- Request/response arrows correct
- Alt/opt blocks for conditions

---

## GATE-04: Side Effects (15%)

### Criteria

Every test must document observable side effects.

### Side Effect Categories

| Category | Examples |
|----------|----------|
| Database | Records created, updated, deleted |
| Cache | Keys set, invalidated |
| Queue | Messages published |
| External | API calls made |
| Logs | Entries created |

### Measurement

```
Score = (Tests with side effects documented / Total tests) × 100
```

---

## GATE-05: Traceability (10%)

### Criteria

Required traceability tags must be present.

### Required Tags

| Tag | Location |
|-----|----------|
| `@ctr` | Test Case Details |
| `@sys` | Test Scope or Details |
| `@spec` | Document Control |

### Measurement

```
Score = (Required tags present / Total required) × 100
```

---

## Combined Score Calculation

### Formula

```
Total = (G1 × 0.30) + (G2 × 0.25) + (G3 × 0.20) + (G4 × 0.15) + (G5 × 0.10)
```

### Example Calculation

| Gate | Score | Weight | Contribution |
|------|-------|--------|--------------|
| GATE-01 | 90% | 0.30 | 27.0 |
| GATE-02 | 100% | 0.25 | 25.0 |
| GATE-03 | 80% | 0.20 | 16.0 |
| GATE-04 | 85% | 0.15 | 12.75 |
| GATE-05 | 100% | 0.10 | 10.0 |
| **Total** | | | **90.75%** |

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥85% | ✅ PASS | Proceed to TASKS |
| 75-84% | ⚠️ WARN | Review and improve |
| <75% | ❌ FAIL | Remediation required |

---

## TASKS-Ready Checklist

Before proceeding to TASKS generation:

- [ ] Overall score ≥85%
- [ ] No GATE at <70%
- [ ] All CTR endpoints covered
- [ ] Contract tables complete
- [ ] Sequence diagrams for complex flows
- [ ] Side effects documented
- [ ] Traceability tags present

## Validation Command

```bash
python scripts/validate_itest.py docs/10_TSPEC/ITEST/ITEST-NN_*.md --quality-gates
```

## See Also

- [ITEST_MVP_VALIDATION_RULES.md](ITEST_MVP_VALIDATION_RULES.md)
- [ITEST_MVP_CREATION_RULES.md](ITEST_MVP_CREATION_RULES.md)
- [../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md](../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md)
