---
title: "SECTEST MVP Validation Rules"
tags:
  - sectest-rules
  - validation-rules
  - layer-10-artifact
custom_fields:
  document_type: validation-rules
  artifact_type: SECTEST
  layer: 10
  test_type_code: 45
  development_status: active
---

# SECTEST MVP Validation Rules

## Purpose

Validation criteria for security test specification documents. Used by `validate_sectest.py` script.

## Structural Validation

### Required Sections

| Section | Validation Rule |
|---------|-----------------|
| 1. Document Control | Must contain status, version, TASKS-Ready score |
| 2. Test Scope | Must define component, threats, scenarios |
| 3. Test Case Index | Must list all test cases with IDs |
| 4. Test Case Details | Must have threat scenarios and security controls |
| 5. Security Coverage Matrix | Must map all SEC/CTR reqs to tests |
| 6. Traceability | Must contain @sec, @ctr, @sys, @spec tags |

### YAML Frontmatter

Required fields:

```yaml
title: "SECTEST-NN: [Title]"
tags:
  - sectest-document
  - layer-10-artifact
custom_fields:
  artifact_type: SECTEST
  test_type_code: 45
```

## Element ID Validation

### Format

```
TSPEC.NN.45.SS
```

### Rules

| Rule | Validation |
|------|------------|
| Prefix | Must be `TSPEC` |
| Doc number | Must match document filename |
| Type code | Must be `45` for security tests |
| Sequence | Must be unique within document |

### Regex Pattern

```regex
^TSPEC\.\d{2,}\.45\.\d{2,}$
```

## Traceability Validation

### Required Tags

| Tag | Pattern | Required |
|-----|---------|----------|
| `@sec` | `SEC\.\d{2,}\.\d{2}` | Yes |
| `@ctr` | `CTR-\d{2,}` | Recommended |
| `@sys` | `SYS\.\d{2,}\.\d{2}` | Recommended |
| `@spec` | `SPEC-\d{2,}` | Yes |

### Tag Location

- `@sec` must appear in Test Case Details section
- `@spec` must appear in Document Control or Test Scope

### Coverage Rule

Every test case MUST have at least one `@sec` reference.

## Content Validation

### Threat Scenarios

**Required format**:

```markdown
| Element | Description |
|---------|-------------|
| Threat Actor | [description] |
| Attack Vector | [description] |
| Prerequisites | [description] |
| Impact | [description] |
```

**Validation rules**:
- Must have Threat Actor
- Must have Attack Vector
- Must have Prerequisites
- Must have Impact

### Security Controls

**Required format**:

```markdown
| Control | Expected Behavior | Validation Method |
|---------|-------------------|-------------------|
```

**Validation rules**:
- Must have header row
- Must have at least 1 control
- Expected Behavior must be specific
- Validation Method must be actionable

### Execution Profile

**Required fields**:
- `primary_interface`: one of mcp | http | cli | library | other
- `skip_policy`: must include safety rationale
- Environment isolation requirement documented

**Validation**: At least one execution_profile per document with safety constraints

### Compliance Mapping

**Recommended elements**:
- OWASP Top 10 reference
- CWE identifier
- Framework mapping

## Coverage Validation

### Security Coverage Matrix

| Validation | Criteria |
|------------|----------|
| Completeness | All referenced SEC reqs must appear in matrix |
| Mapping | Each SEC req must map to ≥1 test ID |
| CTR Mapping | CTR references should be mapped |
| Coverage % | Must calculate and display percentage |

### Minimum Coverage

| Metric | Threshold |
|--------|-----------|
| SEC coverage | ≥90% |
| CTR coverage | ≥85% |
| Category coverage | 4/6 categories used |

## Quality Score Calculation

### Weights

| Component | Weight | Measurement |
|-----------|--------|-------------|
| Security Requirements | 30% | (Covered SEC reqs / Total SEC reqs) × 100 |
| Threat Scenarios | 25% | (Tests with scenarios / Total tests) × 100 |
| Security Controls | 20% | (Tests with controls / Total tests) × 100 |
| Execution Profile | 15% | (Docs with safety profile / Total docs) × 100 |
| Compliance Mapping | 10% | (Tests with compliance / Total tests) × 100 |

### Formula

```
Score = (SEC × 0.30) + (Threat × 0.25) + (Control × 0.20) + (Profile × 0.15) + (Compliance × 0.10)
```

### Pass/Fail

| Score | Status |
|-------|--------|
| ≥90% | PASS |
| 80-89% | WARN |
| <80% | FAIL |

## Validation Output

### Pass Output

```
✅ SECTEST-01_authentication.md: PASS (95%)
  - SEC Coverage: 100% (10/10)
  - Threat Scenarios: 100% (8/8)
  - Security Controls: 100% (8/8)
  - Execution Profile: 100% (1/1)
  - Compliance Mapping: 75% (6/8)
```

### Fail Output

```
❌ SECTEST-01_authentication.md: FAIL (82%)
  - SEC Coverage: 90% (9/10)
    Missing: SEC.01.05
  - Threat Scenarios: 100% (8/8)
  - Security Controls: 75% (6/8)
    Missing controls: TSPEC.01.45.03, TSPEC.01.45.07
  - Execution Profile: 100% (1/1)
  - Compliance Mapping: 50% (4/8)
```

## Automated Checks

The validator script performs:

1. YAML frontmatter parsing
2. Section presence check
3. Element ID format validation
4. Traceability tag extraction
5. Threat scenario validation
6. Security control validation
7. Execution profile safety check
8. Coverage matrix analysis
9. Quality score calculation

## See Also

- [SECTEST-MVP-TEMPLATE.md](SECTEST-MVP-TEMPLATE.md)
- [SECTEST_MVP_QUALITY_GATES.md](SECTEST_MVP_QUALITY_GATES.md)
- [SECTEST_MVP_CREATION_RULES.md](SECTEST_MVP_CREATION_RULES.md)
- [../scripts/validate_sectest.py](../scripts/validate_sectest.py)
