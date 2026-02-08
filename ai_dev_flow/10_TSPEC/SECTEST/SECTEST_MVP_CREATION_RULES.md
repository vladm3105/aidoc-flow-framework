---
title: "SECTEST MVP Creation Rules"
tags:
  - sectest-rules
  - mvp-guidance
  - layer-10-artifact
  - ai-guidance
custom_fields:
  document_type: creation-rules
  artifact_type: SECTEST
  layer: 10
  test_type_code: 45
  development_status: active
---

# SECTEST MVP Creation Rules

## Purpose

AI guidance for creating security test specifications that meet security workflow requirements.

## Pre-Creation Checklist

Before creating a SECTEST document:

- [ ] Security requirements defined (SEC, CTR, SYS)
- [ ] Threat model completed
- [ ] Attack surface documented
- [ ] Isolated test environment available
- [ ] Safety constraints defined

## Document Naming

**Format**: `SECTEST-NN_[component_or_threat].md`

**Examples**:
- `SECTEST-01_authentication.md`
- `SECTEST-02_input_validation.md`
- `SECTEST-03_api_security.md`

## Element ID Format

**Format**: `TSPEC.NN.45.SS`

| Component | Description |
|-----------|-------------|
| `TSPEC` | Artifact type |
| `NN` | Document number (matches filename) |
| `45` | Security test type code |
| `SS` | Sequential test case number (01-99) |

## Required Sections

| Section | Required | Content |
|---------|----------|---------|
| 1. Document Control | Yes | Status, version, scores |
| 2. Test Scope | Yes | Component, threats, scenarios |
| 3. Test Case Index | Yes | ID, name, category, SEC coverage |
| 4. Test Case Details | Yes | Threat scenarios, controls, validation |
| 5. Security Coverage Matrix | Yes | SEC/CTR → Test mapping |
| 6. Traceability | Yes | @sec, @ctr, @sys, @spec tags |

## Test Categories

Use these category prefixes for all test cases:

| Category | Purpose | Example |
|----------|---------|---------|
| `[AuthN]` | Authentication testing | Password policies, MFA |
| `[AuthZ]` | Authorization testing | Access control, privilege escalation |
| `[Input]` | Input validation | Injection attacks, XSS |
| `[Crypto]` | Cryptographic testing | Encryption, key management |
| `[Config]` | Configuration security | Security headers, defaults |
| `[Session]` | Session management | Token handling, timeouts |

## Traceability Rules

### Required Tags

| Tag | Requirement |
|-----|-------------|
| `@sec` | Every test MUST trace to at least one SEC requirement |
| `@ctr` | Every test SHOULD trace to relevant CTR |
| `@sys` | Every test SHOULD trace to relevant SYS |
| `@spec` | Document MUST reference source SPEC |

### Tag Format

```markdown
@sec: SEC.NN.SS
@ctr: CTR-NN
@sys: SYS.NN.SS
@spec: SPEC-NN
```

## Threat Scenario Requirements

Every test case MUST include a Threat Scenario table:

```markdown
| Element | Description |
|---------|-------------|
| Threat Actor | External attacker with valid credentials |
| Attack Vector | Privilege escalation via role manipulation |
| Prerequisites | Valid low-privilege account, access to API |
| Impact | Unauthorized access to admin functions |
```

## Security Control Requirements

Every test case MUST define security controls:

```markdown
| Control | Expected Behavior | Validation Method |
|---------|-------------------|-------------------|
| RBAC | Deny access to admin endpoints | HTTP 403 response |
| Input Validation | Reject malformed role parameter | Input sanitization error |
| Audit Logging | Log access attempt | Check audit logs |
```

## Execution Profile Requirements

Security tests MUST include execution profile with safety constraints:

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
    - "SECURITY_TEST_ENV"  # must be "isolated"
  ordering:
    constraints: ["STEST-001"]  # smoke tests must pass first
  skip_policy:
    conditions: "Skip in production or shared environments"
    rationale: "Security tests must run in isolated environment only"
```

## Coverage Requirements

| Metric | Target |
|--------|--------|
| SEC coverage | ≥90% |
| CTR coverage | ≥85% |
| Test categories | At least 4 represented |
| Threat scenarios | Every test has threat actor and vector |
| Security controls | Every test has controls and validation |

## Quality Gate Scoring

| Component | Weight | Criteria |
|-----------|--------|----------|
| Security Requirements | 30% | Every SEC/CTR/SYS req has ≥1 test |
| Threat Scenarios | 25% | Every test has threat actor and vector |
| Security Controls | 20% | Controls and validation methods defined |
| Execution Profile | 15% | Safety constraints documented |
| Compliance Mapping | 10% | OWASP/CWE/framework references |

**Pass threshold**: ≥90%

## Common Mistakes

| Mistake | Correction |
|---------|------------|
| Missing @sec tag | Every test MUST trace to SEC |
| Vague threat descriptions | Be specific about actors and vectors |
| Missing safety constraints | Always document isolated environment requirement |
| No validation methods | Define how to verify each control |
| Wrong ID format | Use TSPEC.NN.45.SS format |

## Validation Command

```bash
python scripts/validate_sectest.py docs/10_TSPEC/SECTEST/SECTEST-01_*.md
```

## See Also

- [SECTEST-MVP-TEMPLATE.md](SECTEST-MVP-TEMPLATE.md)
- [SECTEST_MVP_VALIDATION_RULES.md](SECTEST_MVP_VALIDATION_RULES.md)
- [SECTEST_MVP_QUALITY_GATES.md](SECTEST_MVP_QUALITY_GATES.md)
