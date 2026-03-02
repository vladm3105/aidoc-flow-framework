---
name: doc-uxspec-validator
description: Validate UX Specifications (UXSPEC) documents against Layer 9.52 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - uxspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 52
    artifact_type: UXSPEC
    deliverable_type: ux
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [UXSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-uxspec-validator

Validate UX Specifications (UXSPEC) documents against Layer 9.52 schema standards.

## Validation Schema Reference

- Schema: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml`
- Layer: 9.52
- Artifact Type: UXSPEC
- Deliverable Type: ux

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `uxspec-document` |
| `artifact_type` | Yes | `UXSPEC` |
| `deliverable_type` | Yes | `ux` |
| `subtype_code` | Yes | `52` |

### 2. UX Content Validation

- [ ] Element type specified (60-63)
- [ ] Layout specifications complete
- [ ] Interaction patterns defined
- [ ] Responsive breakpoints specified
- [ ] Accessibility requirements noted

### 3. DESIGN-Ready Score

**Target**: DESIGN-Ready ≥85%

## References

- Schema: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_VALIDATION_RULES.md`
