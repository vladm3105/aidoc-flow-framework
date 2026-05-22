---
name: doc-riskspec-autopilot
description: Automated risk-analysis SPEC (Layer 6) generation - generates specifications for risk matrices, impact assessments, and mitigation plans
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-document
    - automation-workflow
  custom_fields:
    layer: 6
    artifact_type: SPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-riskspec-autopilot

## Purpose

Automated **risk-analysis SPEC** generation pipeline that processes upstream
artifacts (BRD, PRD, EARS, BDD, ADR) to generate SPEC documents for risk
management deliverables including risk matrices, impact assessments, control
measures, and mitigation plans. This is the risk-spec specialization of the
SPEC (Layer 6) authoring helpers — see the parent skill `../doc-spec/` and the
single SPEC template at `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`.

**Layer**: 6 (SPEC, risk-analysis focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

**Downstream**: TDD (Layer 7), IPLAN (Layer 8)

---

## When to Use

Use `doc-riskspec-autopilot` when:
- Upstream artifacts have `deliverable_type: risk`
- Creating risk matrix specifications
- Generating impact assessment specs
- Creating control measure documentation
- Specifying mitigation plan requirements

---

## Document Type Contract (MANDATORY)

When generating risk-analysis SPEC document instances, the autopilot MUST:

1. **Read** `document_type` from the single SPEC template:
   - Source: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
   - Field: `metadata.document_type: "spec-document"`

2. **Set** the metadata in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: spec-document
     artifact_type: SPEC
     deliverable_type: risk
     layer: 6
   ```

---

## Risk Content Areas

| Content Area | Description |
|--------------|-------------|
| Risk Matrix | Probability × Impact grid |
| Impact Assessment | Consequence analysis |
| Control Measure | Risk mitigation controls |
| Mitigation Plan | Action plan for risks |

These are expressed inside the standard SPEC sections (behavior, data models,
implementation notes) — not as separate ID type codes.

---

## Supported Frameworks

- ISO 31000 - Risk Management
- NIST Cybersecurity Framework
- FAIR - Factor Analysis of Information Risk
- Custom enterprise frameworks

---

## SPEC-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Risk Identification | 25% | 100% |
| Impact Analysis | 20% | ≥90% |
| Control Mapping | 20% | ≥90% |
| Mitigation Plans | 15% | ≥85% |
| Residual Risk | 10% | ≥85% |
| Traceability | 10% | 100% |

**Target**: SPEC-Ready ≥85%

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guidance: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
