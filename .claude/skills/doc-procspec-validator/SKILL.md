---
name: doc-procspec-validator
description: Validate Process Specifications (PROCSPEC) documents against Layer 9.54 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - procspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 54
    artifact_type: PROCSPEC
    deliverable_type: process
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [PROCSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-procspec-validator

Validate Process Specifications (PROCSPEC) documents against Layer 9.54 schema standards.

## Validation Schema Reference

- Schema: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml`
- Layer: 9.54
- Artifact Type: PROCSPEC
- Deliverable Type: process

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `procspec-document` |
| `artifact_type` | Yes | `PROCSPEC` |
| `deliverable_type` | Yes | `process` |
| `subtype_code` | Yes | `54` |

### 2. Process Content Validation

- [ ] Element type specified (70-73)
- [ ] Process steps numbered
- [ ] Roles/responsibilities defined
- [ ] Decision points marked
- [ ] Verification steps included

### 3. PROC-Ready Score

**Target**: PROC-Ready ≥85%

## References

- Schema: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml`
