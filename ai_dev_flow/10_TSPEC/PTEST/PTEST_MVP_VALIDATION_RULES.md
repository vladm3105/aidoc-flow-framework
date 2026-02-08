---
title: "PTEST MVP Validation Rules"
tags:
  - ptest-rules
  - validation-rules
  - layer-10-artifact
custom_fields:
  document_type: validation-rules
  artifact_type: PTEST
  layer: 10
  test_type_code: 44
  development_status: active
---

# PTEST MVP Validation Rules

## Purpose

Validation criteria for performance test specification documents. Used by `validate_ptest.py` script.

## Structural Validation

### Required Sections

| Section | Validation Rule |
|---------|-----------------|
| 1. Document Control | Must contain status, version, TASKS-Ready score |
| 2. Test Scope | Must define component, SPEC ref, scenarios |
| 3. Test Case Index | Must list all test cases with IDs |
| 4. Test Case Details | Must have load scenarios and thresholds |
| 5. Performance Coverage Matrix | Must map all SYS reqs to tests |
| 6. Traceability | Must contain @sys and @spec tags |

### YAML Frontmatter

Required fields:

```yaml
title: "PTEST-NN: [Title]"
tags:
  - ptest-document
  - layer-10-artifact
custom_fields:
  artifact_type: PTEST
  test_type_code: 44
```

## Element ID Validation

### Format

```
TSPEC.NN.44.SS
```

### Rules

| Rule | Validation |
|------|------------|
| Prefix | Must be `TSPEC` |
| Doc number | Must match document filename |
| Type code | Must be `44` for performance tests |
| Sequence | Must be unique within document |

### Regex Pattern

```regex
^TSPEC\.\d{2,}\.44\.\d{2,}$
```

## Traceability Validation

### Required Tags

| Tag | Pattern | Required |
|-----|---------|----------|
| `@sys` | `SYS\.\d{2,}\.\d{2}` | Yes |
| `@spec` | `SPEC-\d{2,}` | Yes |

### Tag Location

- `@sys` must appear in Test Case Details section
- `@spec` must appear in Document Control or Test Scope

### Coverage Rule

Every test case MUST have at least one `@sys` reference.

## Content Validation

### Load Scenarios

**Required format**:

```markdown
| Load Level | Concurrent Users | Duration | Target Throughput |
|------------|------------------|----------|-------------------|
```

**Validation rules**:
- Must have header row
- Must have at least 3 scenarios (normal, peak, stress)
- Must use quantified values (no vague terms)

### Performance Thresholds

**Required format**:

```markdown
| Metric | Target | Maximum | Unit |
|--------|--------|---------|------|
```

**Validation rules**:
- Must have header row
- Must include Response Time, Throughput, Error Rate
- Must specify units (ms, req/s, %)

### Execution Profile

**Required fields**:
- `primary_interface`: one of mcp | http | cli | library | other
- `required_services`: array with name and readiness_check
- `required_env_vars`: array of env var names (no values)

**Validation**: At least one execution_profile per document (can be at document level)

### Measurement Strategy

**Required elements**:
- Tool selection (e.g., Locust, k6, JMeter)
- Metrics to collect (latency, throughput, errors)
- Sampling method

## Coverage Validation

### Performance Coverage Matrix

| Validation | Criteria |
|------------|----------|
| Completeness | All referenced SYS reqs must appear in matrix |
| Mapping | Each SYS req must map to ≥1 test ID |
| Coverage % | Must calculate and display percentage |

### Minimum Coverage

| Metric | Threshold |
|--------|-----------|
| SYS coverage | ≥85% |
| Category coverage | 4/4 categories used |

## Quality Score Calculation

### Weights

| Component | Weight | Measurement |
|-----------|--------|-------------|
| Performance Requirements | 25% | (Covered SYS reqs / Total SYS reqs) × 100 |
| Load Scenarios | 25% | (Tests with scenarios / Total tests) × 100 |
| Performance Thresholds | 20% | (Tests with thresholds / Total tests) × 100 |
| Execution Profile | 15% | (Docs with profile / Total docs) × 100 |
| Measurement Strategy | 15% | (Tests with strategy / Total tests) × 100 |

### Formula

```
Score = (SYS × 0.25) + (Load × 0.25) + (Thresh × 0.20) + (Profile × 0.15) + (Measure × 0.15)
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
✅ PTEST-01_api_response_time.md: PASS (92%)
  - SYS Coverage: 95% (20/20)
  - Load Scenarios: 100% (15/15)
  - Performance Thresholds: 90% (15/15)
  - Execution Profile: 100% (1/1)
  - Measurement Strategy: 88% (14/15)
```

### Fail Output

```
❌ PTEST-01_api_response_time.md: FAIL (78%)
  - SYS Coverage: 80% (16/20)
    Missing: SYS.01.05, SYS.01.08
  - Load Scenarios: 90% (14/15)
    Missing: TSPEC.01.44.03
  - Performance Thresholds: 75% (12/15)
  - Execution Profile: 100% (1/1)
  - Measurement Strategy: 60% (9/15)
```

## Automated Checks

The validator script performs:

1. YAML frontmatter parsing
2. Section presence check
3. Element ID format validation
4. Traceability tag extraction
5. Load scenario table detection
6. Performance threshold validation
7. Execution profile validation
8. Coverage matrix analysis
9. Quality score calculation

## See Also

- [PTEST-MVP-TEMPLATE.md](PTEST-MVP-TEMPLATE.md)
- [PTEST_MVP_QUALITY_GATES.md](PTEST_MVP_QUALITY_GATES.md)
- [PTEST_MVP_CREATION_RULES.md](PTEST_MVP_CREATION_RULES.md)
- [../scripts/validate_ptest.py](../scripts/validate_ptest.py)
