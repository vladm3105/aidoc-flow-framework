---
title: "RISKSPEC MVP Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - riskspec-subtype
custom_fields:
  document_type: rules
  artifact_type: RISKSPEC
  layer: 9
  subtype_code: 53
---

# RISKSPEC MVP Validation Rules

## Purpose

Validation checklist for Risk Analysis Specification (RISKSPEC) documents after creation.

## Validation Checklist

### Structure Validation

- [ ] File is valid YAML
- [ ] File name matches `RISKSPEC-NN_name.yaml` format
- [ ] All required sections present
- [ ] `instance_document_type: riskspec-document`
- [ ] `deliverable_type: risk`

### Metadata Validation

- [ ] Version is semantic version format (X.Y.Z)
- [ ] Status is valid (draft, review, approved, implemented)
- [ ] Dates are YYYY-MM-DD format
- [ ] At least one author specified
- [ ] `ctr_required: false`

### Traceability Validation

- [ ] REQ reference present (required)
- [ ] All cumulative tags complete (BRD through REQ)
- [ ] Downstream artifacts defined (TASKS, policies, controls)
- [ ] Element IDs use RISKSPEC.NN.TT.SS format

### Risk Specification Validation

- [ ] risk_framework specified (ISO31000, NIST, FAIR, or custom)
- [ ] assessment_type specified (qualitative, quantitative, hybrid)
- [ ] risk_matrix defined with likelihood and impact scales
- [ ] risk_tolerance specified (low, medium, high)
- [ ] At least one risk in risk_register

### Risk Register Validation

- [ ] Each risk has unique ID (RISKSPEC.NN.65.SS)
- [ ] Each risk has category (operational, financial, compliance, security, strategic)
- [ ] Each risk has description
- [ ] Each risk has likelihood score (1-5)
- [ ] Each risk has impact score (1-5)
- [ ] Each risk has calculated risk_score
- [ ] Each risk has mitigation_strategy (avoid, transfer, mitigate, accept)

### Controls Validation

- [ ] At least one control defined
- [ ] Each control has unique ID (RISKSPEC.NN.66.SS)
- [ ] Each control references valid risk_id
- [ ] Each control has control_type (preventive, detective, corrective)
- [ ] Each control has description
- [ ] Each control has owner
- [ ] Each control has status (planned, implemented, verified)

### Mitigations Validation

- [ ] Each mitigation has unique ID (RISKSPEC.NN.67.SS)
- [ ] Each mitigation references valid risk_id
- [ ] Each mitigation has strategy (avoid, transfer, mitigate, accept)
- [ ] Each mitigation has implementation details
- [ ] Each mitigation has timeline
- [ ] Each mitigation has cost estimate

### Assessments Validation

- [ ] Impact assessments defined for significant risks
- [ ] Each assessment has unique ID (RISKSPEC.NN.68.SS)
- [ ] Each assessment references valid risk_id
- [ ] Each assessment has impact_area
- [ ] Residual risk calculated for each risk
- [ ] Residual score <= inherent score
- [ ] within_tolerance determination made

### Monitoring Validation

- [ ] Key Risk Indicators (KRIs) defined for critical risks
- [ ] Each KRI has threshold values
- [ ] Each KRI has monitoring frequency
- [ ] Each KRI has owner
- [ ] Review schedule established
- [ ] Next review dates specified

### Verification Validation

- [ ] At least one BDD scenario or audit test referenced
- [ ] Control testing coverage targets specified
- [ ] Audit paths defined

## RISK-Ready Score Calculation

| Criterion | Weight | Check |
|-----------|--------|-------|
| Risk Identification | 25% | All risks identified with categories and scores |
| Impact Assessment | 25% | Likelihood, impact, and residual risk calculated |
| Mitigation Strategies | 20% | Strategy assigned for each risk |
| Control Measures | 15% | Controls defined with owners and types |
| Traceability | 15% | All upstream/downstream links complete |

**Target**: >= 90%

## Error Codes

| Code | Severity | Message |
|------|----------|---------|
| RISKSPEC-E001 | Error | File is not valid YAML |
| RISKSPEC-E002 | Error | Missing required field |
| RISKSPEC-E003 | Error | deliverable_type must be 'risk' |
| RISKSPEC-E004 | Error | Missing risk_framework |
| RISKSPEC-E005 | Error | Missing REQ reference |
| RISKSPEC-E006 | Error | No risks in risk_register |
| RISKSPEC-E007 | Error | No controls defined |
| RISKSPEC-E008 | Error | Risk missing likelihood or impact |
| RISKSPEC-E009 | Error | Control references invalid risk_id |
| RISKSPEC-E010 | Error | Mitigation references invalid risk_id |
| RISKSPEC-W001 | Warning | Risk category not from standard list |
| RISKSPEC-W002 | Warning | Control missing owner |
| RISKSPEC-W003 | Warning | Missing BDD references |
| RISKSPEC-W004 | Warning | Residual risk exceeds inherent risk |

## Validation Commands

```bash
# YAML syntax validation
yamllint RISKSPEC-NN_name.yaml

# Schema validation
validate-spec --schema RISKSPEC_MVP_SCHEMA.yaml RISKSPEC-NN_name.yaml

# RISK-Ready score calculation
calc-readiness --type RISK-Ready RISKSPEC-NN_name.yaml
```

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
