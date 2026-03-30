---
title: "FTEST MVP Creation Rules"
tags:
  - ftest-rules
  - mvp-guidance
  - layer-10-artifact
  - ai-guidance
custom_fields:
  document_type: creation-rules
  artifact_type: FTEST
  layer: 10
  test_type_code: 43
  development_status: active
---

# FTEST MVP Creation Rules

## Purpose

AI guidance for creating functional test specifications that validate system quality attributes.

## Pre-Creation Checklist

Before creating an FTEST document:

- [ ] SYS documents exist for system requirements
- [ ] Threshold definitions are established
- [ ] Quality attributes identified
- [ ] Test environment available
- [ ] Measurement tools configured

## Document Naming and Location

**Nested Folder Rule**: ALL FTEST documents MUST be in nested folders.

**Structure**: `docs/10_TSPEC/FTEST/FTEST-NN_{slug}/FTEST-NN_{slug}.md`

**Examples**:
```
docs/10_TSPEC/FTEST/
├── FTEST-01_api_performance/
│   └── FTEST-01_api_performance.md
├── FTEST-02_system_reliability/
│   └── FTEST-02_system_reliability.md
└── FTEST-03_security_validation/
    └── FTEST-03_security_validation.md
```

## Element ID Format

**Format**: `TSPEC.NN.43.SS`

| Component | Description |
|-----------|-------------|
| `TSPEC` | Artifact type |
| `NN` | Document number (matches filename) |
| `43` | Functional test type code |
| `SS` | Sequential test case number (01-99) |

## Required Sections

| Section | Required | Content |
|---------|----------|---------|
| 1. Document Control | Yes | Status, version, scores |
| 2. Test Scope | Yes | System, quality attributes, thresholds |
| 3. Test Case Index | Yes | ID, attribute, SYS coverage |
| 4. Test Case Details | Yes | Threshold validation, workflows |
| 5. SYS Coverage Matrix | Yes | SYS → Test mapping |
| 6. Traceability | Yes | @sys, @threshold tags |

## Quality Attributes

Target these quality attributes:

| Attribute | Focus | Examples |
|-----------|-------|----------|
| Performance | Response time, throughput | P95 latency, RPS |
| Reliability | Availability, durability | Uptime, MTBF |
| Security | Authentication, authorization | Auth failures, vulnerabilities |
| Scalability | Load handling, growth | Concurrent users, resource usage |

## Traceability Rules

### Cumulative Tags (Layer 10 - 8-9 Required)

| Tag | Reference Format | Required |
|-----|------------------|----------|
| `@brd` | BRD.NN.TT.SS | Yes |
| `@prd` | PRD.NN.TT.SS | Yes |
| `@ears` | EARS.NN.25.SS | Yes |
| `@bdd` | BDD.NN.14.SS | Yes |
| `@adr` | ADR-NN | Yes |
| `@sys` | SYS.NN.26.SS | Yes |
| `@req` | REQ.NN.27.SS | Yes |
| `@spec` | SPEC-NN | Yes |
| `@ctr` | CTR-NN | If exists |

### FTEST-Specific Required Tags

| Tag | Requirement |
|-----|-------------|
| `@sys` | Every test MUST trace to SYS requirement |
| `@threshold` | Every test MUST reference threshold |

### Tag Format

```markdown
@sys: SYS.NN.01.01
@threshold: TH-PERF-001 (<200ms P95)
```

## Threshold Validation Table

Every test MUST include threshold validation:

```markdown
| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| [Metric name] | [Target value] | [How measured] |
```

## Workflow Steps

Every test MUST include workflow steps:

```markdown
| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | [Action] | [Expected] |
```

## Measurement Methodology

Tests MUST include executable measurement code:

```python
# Measurement example
results = run_test()
assert results.metric < threshold
```

## Coverage Requirements

| Metric | Target |
|--------|--------|
| SYS coverage | ≥85% |
| Threshold refs | 100% |
| Workflow steps | 1 per test |
| Measurement code | 1 per test |

## Quality Gate Scoring

| Component | Weight | Criteria |
|-----------|--------|----------|
| SYS Coverage | 30% | Quality attributes have tests |
| Threshold Refs | 25% | All metrics use @threshold |
| Workflow Steps | 25% | End-to-end flows documented |
| Measurement | 20% | Metrics collection defined |

**Pass threshold**: ≥85%

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Missing @threshold | Reference threshold definition |
| No measurement code | Add executable validation |
| Vague thresholds | Use specific numeric values |
| Missing workflow | Add step-by-step process |

## Validation Command

```bash
# Validate single FTEST (nested folder structure)
python scripts/validate_ftest.py docs/10_TSPEC/FTEST/FTEST-01_api_performance/FTEST-01_api_performance.md

# Validate all FTEST documents
python scripts/validate_ftest.py docs/10_TSPEC/FTEST/
```

## See Also

- [FTEST-MVP-TEMPLATE.md](FTEST-MVP-TEMPLATE.md)
- [FTEST_MVP_VALIDATION_RULES.md](FTEST_MVP_VALIDATION_RULES.md)
- [FTEST_MVP_QUALITY_GATES.md](FTEST_MVP_QUALITY_GATES.md)

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
