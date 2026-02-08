---
title: "PTEST MVP Quality Gates"
tags:
  - ptest-rules
  - quality-gates
  - layer-10-artifact
custom_fields:
  document_type: quality-gates
  artifact_type: PTEST
  layer: 10
  test_type_code: 44
  development_status: active
---

# PTEST MVP Quality Gates

## Purpose

Define quality gate criteria for performance test specifications to ensure TASKS-readiness.

## Quality Gate Summary

| Gate | Weight | Target | Description |
|------|--------|--------|-------------|
| GATE-01 | 25% | 100% | Performance Requirements Coverage |
| GATE-02 | 25% | 100% | Load Scenarios |
| GATE-03 | 20% | 100% | Performance Thresholds |
| GATE-04 | 15% | 100% | Execution Profile |
| GATE-05 | 15% | 100% | Measurement Strategy |

**Overall Target**: ≥85%

---

## GATE-01: Performance Requirements Coverage (25%)

### Criteria

Every performance requirement referenced in the SPEC must have at least one test scenario.

### Measurement

```
Coverage = (PERF-REQs with tests / Total PERF-REQs) × 100
```

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% coverage | Full pass |
| 85-99% coverage | Conditional pass |
| <85% coverage | Fail |

### Evidence Required

- Performance Coverage Matrix completed
- All PERF/SYS requirement IDs mapped to test IDs
- No orphan performance requirements

### Remediation

If coverage <100%:
1. Identify missing performance requirements
2. Create test scenarios for each
3. Update coverage matrix
4. Re-validate

---

## GATE-02: Load Scenarios (25%)

### Criteria

Every test scenario must define concrete load conditions.

### Measurement

```
Score = (Tests with load scenarios / Total tests) × 100
```

### Table Requirements

| Requirement | Validation |
|-------------|------------|
| Header row | `| Load Level | Concurrent Users | Duration |` |
| Minimum rows | 3 scenarios (normal, peak, stress) |
| Quantified values | No vague terms like "high load" |

### Evidence Required

- Load Scenario table in each test section
- Realistic user counts and durations
- Rationale for load levels

### Remediation

If score <100%:
1. List tests without load scenarios
2. Define normal, peak, and stress loads
3. Quantify concurrent users and duration
4. Re-validate

---

## GATE-03: Performance Thresholds (20%)

### Criteria

Every test scenario must define measurable performance thresholds.

### Measurement

```
Score = (Tests with thresholds / Total tests) × 100
```

### Required Metrics

| Metric | Unit | Example |
|--------|------|---------|
| Response Time | ms | ≤500ms (p95) |
| Throughput | req/s | ≥1000 req/s |
| Error Rate | % | ≤0.1% |
| Resource Usage | % | CPU ≤80% |

### Evidence Required

- Threshold table in each test section
- Baseline/reference values (if applicable)
- Pass/fail criteria defined

### Remediation

If score <100%:
1. Identify tests without thresholds
2. Define quantitative targets
3. Add baseline comparisons where applicable
4. Re-validate

---

## GATE-04: Execution Profile (15%)

### Criteria

Test scenarios must document execution environment and constraints.

### Required Fields

```yaml
execution_profile:
  primary_interface: "http"  # mcp | http | cli | library
  required_services:
    - name: "database"
      readiness_check:
        type: "command"
        value: "pg_isready -h localhost"
  required_env_vars:
    - "DB_HOST"
    - "LOAD_TEST_TOKEN"
  ordering:
    constraints: []
  skip_policy:
    conditions: "none"
    rationale: "Performance tests required for release"
```

### Evidence Required

- `execution_profile` section present
- Primary interface declared
- Service dependencies documented
- Environment prerequisites listed (names only, no secrets)

### Remediation

If score <100%:
1. Add execution_profile to template
2. Document primary interface
3. List required services and env vars
4. Re-validate

---

## GATE-05: Measurement Strategy (15%)

### Criteria

Every test must define how performance metrics will be collected.

### Measurement

```
Score = (Tests with measurement strategy / Total tests) × 100
```

### Required Elements

| Element | Description |
|---------|-------------|
| Tool | Load generator (e.g., Locust, k6, JMeter) |
| Metrics | What to measure (latency, throughput, errors) |
| Sampling | How metrics are sampled |
| Baseline | Reference for comparison |

### Evidence Required

- Measurement strategy documented
- Tool selection justified
- Metrics explicitly listed

### Remediation

If score <100%:
1. List tests without measurement strategy
2. Document tools and metrics
3. Define sampling approach
4. Re-validate

---

## Combined Score Calculation

### Formula

```
Total = (G1 × 0.25) + (G2 × 0.25) + (G3 × 0.20) + (G4 × 0.15) + (G5 × 0.15)
```

### Example Calculation

| Gate | Score | Weight | Contribution |
|------|-------|--------|--------------|
| GATE-01 | 95% | 0.25 | 23.75 |
| GATE-02 | 100% | 0.25 | 25.0 |
| GATE-03 | 90% | 0.20 | 18.0 |
| GATE-04 | 100% | 0.15 | 15.0 |
| GATE-05 | 80% | 0.15 | 12.0 |
| **Total** | | | **93.75%** |

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
- [ ] No GATE at <75%
- [ ] All performance requirements covered
- [ ] Load scenarios quantified
- [ ] Thresholds defined with units
- [ ] Execution profile documented
- [ ] Measurement strategy specified
- [ ] Traceability tags present

## Validation Command

```bash
python scripts/validate_ptest.py docs/10_TSPEC/PTEST/PTEST-NN_*.md --quality-gates
```

## See Also

- [PTEST_MVP_VALIDATION_RULES.md](PTEST_MVP_VALIDATION_RULES.md)
- [PTEST_MVP_CREATION_RULES.md](PTEST_MVP_CREATION_RULES.md)
- [../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md](../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md)
