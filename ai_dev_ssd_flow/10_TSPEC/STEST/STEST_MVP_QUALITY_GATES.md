---
title: "STEST MVP Quality Gates"
tags:
  - stest-rules
  - quality-gates
  - layer-10-artifact
custom_fields:
  document_type: quality-gates
  artifact_type: STEST
  layer: 10
  test_type_code: 42
  development_status: active
---

# STEST MVP Quality Gates

## Purpose

Define quality gate criteria for smoke test specifications. **100% compliance required** - smoke tests are critical for deployment safety.

## Quality Gate Summary

| Gate | Weight | Target | Description |
|------|--------|--------|-------------|
| GATE-01 | 30% | 100% | Critical Paths |
| GATE-02 | 25% | 100% | Timeout Budget |
| GATE-03 | 25% | 100% | Rollback Defined |
| GATE-04 | 20% | 100% | Health Checks |

**Overall Target**: 100% (mandatory)

---

## GATE-01: Critical Paths (30%)

### Criteria

All P0 critical paths must have smoke tests.

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% P0 paths covered | PASS |
| Any P0 path missing | FAIL |

### Evidence Required

- Critical Path Index shows all P0 paths
- Each path has assigned test

---

## GATE-02: Timeout Budget (25%)

### Criteria

Total suite execution must complete within 5 minutes.

### Budget Requirements

| Metric | Requirement |
|--------|-------------|
| Total suite | ≤ 300 seconds |
| Individual test | ≤ 60 seconds |
| Buffer | ≥ 30 seconds |

### Pass Conditions

| Condition | Status |
|-----------|--------|
| Total ≤ 300s with buffer | PASS |
| Total > 300s | FAIL |
| No buffer | FAIL |

---

## GATE-03: Rollback Defined (25%)

### Criteria

Every test must have explicit rollback procedure.

### Rollback Requirements

| Requirement | Validation |
|-------------|------------|
| Step-by-step procedure | Table format |
| Commands specified | Executable |
| Escalation path | Contact defined |

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% tests have rollback | PASS |
| Any test missing rollback | FAIL |

---

## GATE-04: Health Checks (20%)

### Criteria

Every test must include executable health check.

### Health Check Requirements

| Requirement | Validation |
|-------------|------------|
| Executable command | Bash/curl syntax |
| Timeout specified | `--max-time N` |
| Exit code validation | Check return |

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% tests have checks | PASS |
| Any test missing check | FAIL |

---

## Combined Score Calculation

### Formula

```
Total = (G1 × 0.30) + (G2 × 0.25) + (G3 × 0.25) + (G4 × 0.20)
```

### Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 100% | ✅ PASS | Proceed to TASKS |
| <100% | ❌ FAIL | Remediation required |

**Note**: Unlike other TSPEC types, STEST has no WARN threshold. Smoke tests must be 100% compliant.

---

## TASKS-Ready Checklist

Before proceeding to TASKS generation:

- [ ] Overall score = 100%
- [ ] All P0 paths covered
- [ ] Total timeout ≤ 300s
- [ ] All tests have rollback
- [ ] All tests have health checks
- [ ] Traceability tags present

## Validation Command

```bash
python scripts/validate_stest.py docs/10_TSPEC/STEST/STEST-NN_*.md --quality-gates
```

## See Also

- [STEST_MVP_VALIDATION_RULES.md](STEST_MVP_VALIDATION_RULES.md)
- [STEST_MVP_CREATION_RULES.md](STEST_MVP_CREATION_RULES.md)
