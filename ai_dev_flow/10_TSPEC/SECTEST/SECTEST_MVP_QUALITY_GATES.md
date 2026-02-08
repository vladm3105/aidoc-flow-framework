---
title: "SECTEST MVP Quality Gates"
tags:
  - sectest-rules
  - quality-gates
  - layer-10-artifact
custom_fields:
  document_type: quality-gates
  artifact_type: SECTEST
  layer: 10
  test_type_code: 45
  development_status: active
---

# SECTEST MVP Quality Gates

## Purpose

Define quality gate criteria for security test specifications to ensure TASKS-readiness.

## Quality Gate Summary

| Gate | Weight | Target | Description |
|------|--------|--------|-------------|
| GATE-01 | 30% | 100% | Security Requirements Coverage |
| GATE-02 | 25% | 100% | Threat Scenarios |
| GATE-03 | 20% | 100% | Security Controls |
| GATE-04 | 15% | 100% | Execution Profile |
| GATE-05 | 10% | 100% | Compliance Mapping |

**Overall Target**: ≥90%

---

## GATE-01: Security Requirements Coverage (30%)

### Criteria

Every security requirement (SEC, CTR, or SYS) must have at least one test scenario.

### Measurement

```
Coverage = (Security REQs with tests / Total Security REQs) × 100
```

### Pass Conditions

| Condition | Status |
|-----------|--------|
| 100% coverage | Full pass |
| 90-99% coverage | Conditional pass |
| <90% coverage | Fail |

### Evidence Required

- Security Coverage Matrix completed
- All SEC/CTR/SYS requirement IDs mapped to test IDs
- No orphan security requirements

### Remediation

If coverage <100%:
1. Identify missing security requirements
2. Create test scenarios for each
3. Update coverage matrix
4. Re-validate

---

## GATE-02: Threat Scenarios (25%)

### Criteria

Every test scenario must document specific threat actor and attack vector.

### Measurement

```
Score = (Tests with threat scenarios / Total tests) × 100
```

### Required Elements

| Element | Description | Example |
|---------|-------------|---------|
| Threat Actor | Who is attacking | External attacker, insider, automated bot |
| Attack Vector | How they attack | SQL injection, XSS, credential stuffing |
| Prerequisites | What they need | Network access, valid account, knowledge |

### Evidence Required

- Threat scenario table in each test section
- Specific attack descriptions
- Clear prerequisites

### Remediation

If score <100%:
1. List tests without threat scenarios
2. Define threat actors and attack vectors
3. Document prerequisites
4. Re-validate

---

## GATE-03: Security Controls (20%)

### Criteria

Every test scenario must define expected security controls and validation methods.

### Measurement

```
Score = (Tests with security controls / Total tests) × 100
```

### Required Elements

| Element | Description |
|---------|-------------|
| Control | Security mechanism (auth, encryption, validation) |
| Expected Behavior | How control should respond |
| Validation Method | How to verify control works |

### Evidence Required

- Security Controls table in each test section
- Specific expected behaviors
- Clear validation methods

### Remediation

If score <100%:
1. Identify tests without security controls
2. Document expected controls and behaviors
3. Define validation methods
4. Re-validate

---

## GATE-04: Execution Profile (15%)

### Criteria

Test scenarios must document execution environment and safety constraints.

### Required Fields

```yaml
execution_profile:
  primary_interface: "http"
  debug_interfaces_allowed: []
  required_services:
    - name: "auth_service"
      readiness_check:
        type: "http"
        value: "http://localhost:8080/health"
  required_env_vars:
    - "SECURITY_TEST_ENV"  # isolated test environment only
    - "TEST_CREDENTIALS"
  ordering:
    constraints: ["STEST-001"]  # smoke tests must pass first
  skip_policy:
    conditions: "Skip in production environments"
    rationale: "Security tests must run in isolated environment"
```

### Evidence Required

- `execution_profile` section present
- Safety constraints documented
- Isolated environment requirements specified

### Remediation

If score <100%:
1. Add execution_profile to template
2. Document safety constraints
3. Specify isolated environment requirements
4. Re-validate

---

## GATE-05: Compliance Mapping (10%)

### Criteria

Security tests should map to relevant compliance frameworks.

### Measurement

```
Score = (Tests with compliance mapping / Total tests) × 100
```

### Common Frameworks

| Framework | Focus Area |
|-----------|-----------|
| OWASP Top 10 | Web application security |
| CWE | Common Weakness Enumeration |
| NIST CSF | Cybersecurity Framework |
| ISO 27001 | Information security management |

### Evidence Required

- Compliance mapping documented
- Framework references provided

### Remediation

If score <100%:
1. Map tests to relevant frameworks
2. Add OWASP/CWE references
3. Re-validate

---

## Combined Score Calculation

### Formula

```
Total = (G1 × 0.30) + (G2 × 0.25) + (G3 × 0.20) + (G4 × 0.15) + (G5 × 0.10)
```

### Example Calculation

| Gate | Score | Weight | Contribution |
|------|-------|--------|--------------|
| GATE-01 | 100% | 0.30 | 30.0 |
| GATE-02 | 95% | 0.25 | 23.75 |
| GATE-03 | 90% | 0.20 | 18.0 |
| GATE-04 | 100% | 0.15 | 15.0 |
| GATE-05 | 80% | 0.10 | 8.0 |
| **Total** | | | **94.75%** |

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
- [ ] All security requirements covered
- [ ] Threat scenarios documented
- [ ] Security controls defined
- [ ] Execution profile includes safety constraints
- [ ] Compliance mappings provided
- [ ] Traceability tags present

## Validation Command

```bash
python scripts/validate_sectest.py docs/10_TSPEC/SECTEST/SECTEST-NN_*.md --quality-gates
```

## See Also

- [SECTEST_MVP_VALIDATION_RULES.md](SECTEST_MVP_VALIDATION_RULES.md)
- [SECTEST_MVP_CREATION_RULES.md](SECTEST_MVP_CREATION_RULES.md)
- [../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md](../TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md)
