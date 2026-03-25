---
name: doc-riskspec-validator
description: Validate Risk Specifications (RISKSPEC) documents against Layer 9.53 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - riskspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 53
    artifact_type: RISKSPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [RISKSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-riskspec-validator

Validate Risk Specifications (RISKSPEC) documents against Layer 9.53 schema standards.

## Validation Schema Reference

- Schema: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
- Layer: 9.53
- Artifact Type: RISKSPEC
- Deliverable Type: risk

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `riskspec-document` |
| `artifact_type` | Yes | `RISKSPEC` |
| `deliverable_type` | Yes | `risk` |
| `subtype_code` | Yes | `53` |

### 2. Risk Content Validation

- [ ] Element type specified (65-68)
- [ ] Risk categories defined
- [ ] Probability scales documented
- [ ] Impact scales documented
- [ ] Risk appetite stated

### 3. RISK-Ready Score

**Target**: RISK-Ready ≥85%

## References

- Schema: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
