---
name: doc-riskspec-autopilot
description: Automated RISKSPEC (Risk Specification) generation from REQ - generates specifications for risk matrices, impact assessments, and mitigation plans
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - riskspec-artifact
    - automation-workflow
  custom_fields:
    layer: 9
    subtype_code: 53
    artifact_type: RISKSPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [REQ]
    downstream_artifacts: [TSPEC, TASKS]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-riskspec-autopilot

## Purpose

Automated **Risk Specification (RISKSPEC)** generation pipeline that processes REQ documents to generate specifications for risk management deliverables including risk matrices, impact assessments, control measures, and mitigation plans.

**Layer**: 9.53 (RISKSPEC - Risk Specifications)

**Upstream**: REQ (Layer 7)

**Downstream**: TSPEC (Layer 10), TASKS (Layer 11)

---

## When to Use

Use `doc-riskspec-autopilot` when:
- REQ documents have `deliverable_type: risk`
- Creating risk matrix specifications
- Generating impact assessment specs
- Creating control measure documentation
- Specifying mitigation plan requirements

---

## Document Type Contract (MANDATORY)

When generating RISKSPEC document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "riskspec-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: riskspec-document
     artifact_type: RISKSPEC
     deliverable_type: risk
     layer: 9
     subtype_code: 53
   ```

---

## Risk Element Types

| Element Type | Code | Description |
|--------------|------|-------------|
| Risk Matrix | 65 | Probability × Impact grid |
| Impact Assessment | 66 | Consequence analysis |
| Control Measure | 67 | Risk mitigation controls |
| Mitigation Plan | 68 | Action plan for risks |

---

## Supported Frameworks

- ISO 31000 - Risk Management
- NIST Cybersecurity Framework
- FAIR - Factor Analysis of Information Risk
- Custom enterprise frameworks

---

## RISK-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Risk Identification | 25% | 100% |
| Impact Analysis | 20% | ≥90% |
| Control Mapping | 20% | ≥90% |
| Mitigation Plans | 15% | ≥85% |
| Residual Risk | 10% | ≥85% |
| Traceability | 10% | 100% |

**Target**: RISK-Ready ≥85%

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
