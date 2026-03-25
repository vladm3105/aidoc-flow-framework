---
title: "RISKSPEC MVP Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - riskspec-subtype
custom_fields:
  document_type: rules
  artifact_type: RISKSPEC
  layer: 9
  subtype_code: 53
---

# RISKSPEC MVP Creation Rules

## Purpose

Guidelines for creating Risk Analysis Specification (RISKSPEC) documents - comprehensive risk assessments, impact analyses, and control measures for system components.

## When to Create RISKSPEC

Create a RISKSPEC when:
- REQ document has `deliverable_type: risk`
- Requirement involves risk assessment activities
- Component requires formal risk analysis
- Compliance mandates risk documentation

## Prerequisites

Before creating RISKSPEC:

1. **REQ Document**: Atomic requirement with `deliverable_type: risk`
2. **ADR Document**: Architecture decisions affecting risk profile
3. **SYS Document**: System design for risk context
4. **BDD Scenarios**: Test scenarios for control verification

## File Naming

```
RISKSPEC-NN_domain_name.yaml
```

- `NN`: Sequential number (01, 02, 03...)
- `domain_name`: Snake_case, descriptive name of risk domain

## Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| metadata | Yes | Document control with `deliverable_type: risk` |
| traceability | Yes | Must include REQ reference |
| section_3_risk_specification | Yes | Framework, matrix, register, controls |
| mitigations | Yes | Mitigation strategies and implementations |
| assessments | Yes | Impact assessments and residual risk |
| monitoring | Yes | KRIs and review schedules |
| verification | Yes | Audit tests and BDD references |

## Element ID Format

```
RISKSPEC.{DOC}.{TYPE}.{SEQ}
```

| Code | Type | Example |
|------|------|---------|
| 65 | risk | RISKSPEC.01.65.01 |
| 66 | control | RISKSPEC.01.66.01 |
| 67 | mitigation | RISKSPEC.01.67.01 |
| 68 | assessment | RISKSPEC.01.68.01 |

## CTR Requirement

RISKSPEC does **NOT** require CTR (Contract) reference:
- Risk specifications have no external interface
- No API contracts needed
- Focus is on internal risk assessment

## Risk Framework Selection

| Framework | Use Case |
|-----------|----------|
| ISO31000 | General enterprise risk management |
| NIST | Government/regulated environments |
| FAIR | Quantitative cyber risk analysis |
| custom | Organization-specific requirements |

## Risk Categories

| Category | Description |
|----------|-------------|
| operational | Day-to-day operations risks |
| financial | Monetary/budgetary risks |
| compliance | Regulatory/legal risks |
| security | Cybersecurity/data protection risks |
| strategic | Long-term business risks |

## Control Types

| Type | Purpose | Examples |
|------|---------|----------|
| preventive | Stop risk occurrence | Access controls, input validation |
| detective | Identify risk occurrence | Monitoring, logging, alerts |
| corrective | Respond after occurrence | Incident response, recovery |

## Mitigation Strategies

| Strategy | When to Use |
|----------|-------------|
| avoid | High impact risk, can change approach |
| transfer | Risk can be insured or contracted out |
| mitigate | Acceptable with controls in place |
| accept | Low risk, mitigation cost exceeds benefit |

## Quality Gate

**RISK-Ready Score Target**: >= 90%

| Criterion | Weight |
|-----------|--------|
| Risk Identification | 25% |
| Impact Assessment | 25% |
| Mitigation Strategies | 20% |
| Control Measures | 15% |
| Traceability | 15% |

## Validation Checklist

- [ ] `deliverable_type: risk` in metadata
- [ ] REQ reference in traceability
- [ ] Risk framework specified (ISO31000/NIST/FAIR/custom)
- [ ] At least one risk in risk_register
- [ ] Each risk has likelihood and impact scores
- [ ] At least one control defined
- [ ] Each control references valid risk_id
- [ ] Mitigation strategy for each risk
- [ ] Residual risk calculated
- [ ] KRIs defined for critical risks
- [ ] Review schedule established

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
