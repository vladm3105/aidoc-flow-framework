---
title: "PTEST MVP Creation Rules"
tags:
  - ptest-rules
  - mvp-guidance
  - layer-10-artifact
  - ai-guidance
custom_fields:
  document_type: creation-rules
  artifact_type: PTEST
  layer: 10
  test_type_code: 44
  development_status: active
---

# PTEST MVP Creation Rules

## Purpose

AI guidance for creating performance test specifications that meet TDD workflow requirements.

## Pre-Creation Checklist

Before creating a PTEST document:

- [ ] SPEC document exists and defines performance requirements
- [ ] SYS document includes performance thresholds
- [ ] Baseline performance data available (if applicable)
- [ ] Test environment constraints defined

## Document Naming

**Format**: `PTEST-NN_[component_or_scenario].md`

**Examples**:
- `PTEST-01_api_response_time.md`
- `PTEST-02_database_throughput.md`
- `PTEST-03_concurrent_user_load.md`

## Element ID Format

**Format**: `TSPEC.NN.44.SS`

| Component | Description |
|-----------|-------------|
| `TSPEC` | Artifact type |
| `NN` | Document number (matches filename) |
| `44` | Performance test type code |
| `SS` | Sequential test case number (01-99) |

## Required Sections

| Section | Required | Content |
|---------|----------|---------|
| 1. Document Control | Yes | Status, version, scores |
| 2. Test Scope | Yes | Component, dependencies, scenarios |
| 3. Test Case Index | Yes | ID, name, category, SYS coverage |
| 4. Test Case Details | Yes | Load scenarios, thresholds, measurements |
| 5. Performance Coverage Matrix | Yes | SYS → Test mapping |
| 6. Traceability | Yes | @sys, @spec tags |

## Test Categories

Use these category prefixes for all test cases:

| Category | Purpose | Example |
|----------|---------|---------|
| `[Load]` | Load testing under various conditions | Normal, peak, stress |
| `[Stress]` | Breaking point identification | Maximum capacity |
| `[Endurance]` | Long-duration stability | Memory leaks, degradation |
| `[Spike]` | Sudden load changes | Traffic spikes |

## Traceability Rules

### Required Tags

| Tag | Requirement |
|-----|-------------|
| `@sys` | Every test MUST trace to at least one SYS requirement |
| `@spec` | Document MUST reference source SPEC |

### Tag Format

```markdown
@sys: SYS.NN.SS
@spec: SPEC-NN
```

## Load Scenario Requirements

Every test case MUST include a Load Scenario table:

```markdown
| Load Level | Concurrent Users | Duration | Target Throughput |
|------------|------------------|----------|-------------------|
| Normal | 100 | 10 min | 500 req/s |
| Peak | 500 | 5 min | 1000 req/s |
| Stress | 1000 | 2 min | 1500 req/s |
```

**Minimum rows**: 3 (normal, peak, stress)

## Performance Threshold Requirements

Every test case MUST define thresholds:

```markdown
| Metric | Target | Maximum | Unit |
|--------|--------|---------|------|
| Response Time (p95) | ≤200 | ≤500 | ms |
| Error Rate | ≤0.1 | ≤1.0 | % |
| CPU Usage | ≤60 | ≤80 | % |
```

## Execution Profile Requirements

Complex tests MUST include execution profile:

```yaml
execution_profile:
  primary_interface: "http"
  debug_interfaces_allowed: ["cli"]
  required_services:
    - name: "api_server"
      readiness_check:
        type: "http"
        value: "http://localhost:8080/health"
  required_env_vars:
    - "LOAD_TEST_ENDPOINT"
    - "LOAD_TEST_TOKEN"
  ordering:
    constraints: []
  skip_policy:
    conditions: "CI-only skip for load tests"
    rationale: "Resource-intensive tests run on schedule"
```

## Coverage Requirements

| Metric | Target |
|--------|--------|
| SYS coverage | ≥85% |
| Test categories | All 4 represented |
| Load scenarios | ≥3 per test |
| Thresholds | All key metrics covered |

## Quality Gate Scoring

| Component | Weight | Criteria |
|-----------|--------|----------|
| Performance Requirements | 25% | Every SYS/performance req has ≥1 test |
| Load Scenarios | 25% | Every test has defined load conditions |
| Performance Thresholds | 20% | Quantified targets with units |
| Execution Profile | 15% | Environment and dependencies documented |
| Measurement Strategy | 15% | Tools and metrics specified |

**Pass threshold**: ≥85%

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Missing @sys tag | Every test MUST trace to SYS |
| Vague load descriptions | Use specific numbers (users, duration) |
| Missing units | Always specify ms, req/s, %, etc. |
| No baseline reference | Include baseline for comparison |
| Wrong ID format | Use TSPEC.NN.44.SS format |

## Validation Command

```bash
python scripts/validate_ptest.py docs/10_TSPEC/PTEST/PTEST-01_*.md
```

## See Also

- [PTEST-MVP-TEMPLATE.md](PTEST-MVP-TEMPLATE.md)
- [PTEST_MVP_VALIDATION_RULES.md](PTEST_MVP_VALIDATION_RULES.md)
- [PTEST_MVP_QUALITY_GATES.md](PTEST_MVP_QUALITY_GATES.md)
