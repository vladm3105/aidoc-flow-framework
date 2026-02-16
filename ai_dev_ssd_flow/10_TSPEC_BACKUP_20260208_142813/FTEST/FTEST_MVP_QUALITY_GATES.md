---
title: "FTEST MVP Quality Gates"
tags:
  - ftest-rules
  - quality-gates
  - layer-10-artifact
custom_fields:
  document_type: quality-gates
  artifact_type: FTEST
  layer: 10
  test_type_code: 43
  development_status: active
---

# FTEST MVP Quality Gates

## Purpose

Define quality gate criteria for functional test specifications to ensure TASKS-readiness.

## Quality Gate Summary

| Gate | Weight | Target | Description |
|------|--------|--------|-------------|
| GATE-01 | 30% | 100% | SYS Coverage |
| GATE-02 | 25% | 100% | Threshold Refs |
| GATE-03 | 25% | 100% | Workflow Steps |
| GATE-04 | 20% | 100% | Measurement |

**Overall Target**: ≥85%

---

## GATE-01: SYS Coverage (30%)

### Criteria

All SYS quality attributes must have functional tests.

### Quality Attributes

| Attribute | SYS Pattern |
|-----------|-------------|
| Performance | SYS.NN.01.XX |
| Reliability | SYS.NN.02.XX |
| Security | SYS.NN.03.XX |
| Scalability | SYS.NN.04.XX |

### Measurement

```
Coverage = (SYS with tests / Total SYS) × 100
```

---

## GATE-02: Threshold Refs (25%)

### Criteria

Every test must reference defined thresholds.

### Threshold Format

```
@threshold: TH-[ATTR]-NNN
```

### Measurement

```
Score = (Tests with @threshold / Total tests) × 100
```

---

## GATE-03: Workflow Steps (25%)

### Criteria

Every test must have documented workflow steps.

### Requirements

- Minimum 3 steps per test
- Step-Action-Result format
- Clear progression

### Measurement

```
Score = (Tests with workflows / Total tests) × 100
```

---

## GATE-04: Measurement (20%)

### Criteria

Every test must include measurement methodology.

### Requirements

- Executable code block
- Assertion/comparison
- Clear metric calculation

### Measurement

```
Score = (Tests with measurement / Total tests) × 100
```

---

## Combined Score Calculation

### Formula

```
Total = (G1 × 0.30) + (G2 × 0.25) + (G3 × 0.25) + (G4 × 0.20)
```

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| ≥85% | ✅ PASS | Proceed to TASKS |
| 75-84% | ⚠️ WARN | Review and improve |
| <75% | ❌ FAIL | Remediation required |

---

## TASKS-Ready Checklist

- [ ] Overall score ≥85%
- [ ] All SYS attributes covered
- [ ] All thresholds referenced
- [ ] Workflows documented
- [ ] Measurement code present
- [ ] Traceability tags present

## Validation Command

```bash
python scripts/validate_ftest.py docs/10_TSPEC/FTEST/FTEST-NN_*.md --quality-gates
```
