---
name: doc-riskspec-validator
description: Validate risk-analysis SPEC (Layer 6) documents against the unified SPEC template and governance standards
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-document
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-riskspec-validator

Validate risk-analysis SPEC documents against the unified SPEC (Layer 6)
template and governance standards. This is the risk-spec specialization of the
SPEC authoring helpers — see the parent skill `../doc-spec/` and the single
SPEC template at `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`.

## Validation Reference

- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer: 6 (SPEC, risk-analysis focus)
- Artifact Type: SPEC
- Deliverable Type: risk

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `spec-document` |
| `artifact_type` | Yes | `SPEC` |
| `deliverable_type` | Yes | `risk` |
| `layer` | Yes | `6` |

### 2. Risk Content Validation

- [ ] Risk categories defined
- [ ] Probability scales documented
- [ ] Impact scales documented
- [ ] Risk appetite stated
- [ ] Controls and mitigation plans present

### 3. Traceability Validation

- [ ] Document-level tag present (`@spec: SPEC-NN`)
- [ ] Upstream tags use 4-segment element IDs (`@ears: EARS.NN.SS.xxxx`,
      `@bdd: BDD.NN.SS.xxxx`) or document refs (`@adr: ADR-NN`)

### 4. SPEC-Ready Score

**Target**: SPEC-Ready ≥85%

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guidance: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
