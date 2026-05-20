---
name: doc-dspec-validator
description: Validate Documentation Specifications (DSPEC) documents against Layer 9.51 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - dspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 51
    artifact_type: DSPEC
    deliverable_type: document
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [DSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-dspec-validator

Validate Documentation Specifications (DSPEC) documents against Layer 9.51 schema standards.

## Activation

Invoke when user requests validation of DSPEC documents or after creating/modifying DSPEC artifacts.

## Validation Schema Reference

- Schema: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
- Layer: 9.51
- Artifact Type: DSPEC
- Deliverable Type: document

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `dspec-document` |
| `artifact_type` | Yes | `DSPEC` |
| `deliverable_type` | Yes | `document` |
| `subtype_code` | Yes | `51` |
| `layer` | Yes | `9` |

### 2. Content Structure

- [ ] Document type specified (55-58)
- [ ] Target audience defined
- [ ] Content outline complete
- [ ] Style guide referenced

### 3. Audience Analysis

- [ ] Primary audience identified
- [ ] Secondary audiences listed
- [ ] Technical level specified
- [ ] Prerequisites documented

### 4. Content Coverage

- [ ] All REQ topics covered
- [ ] Examples included
- [ ] Diagrams/visuals specified
- [ ] Glossary terms defined

### 5. Accessibility

- [ ] Alt text requirements noted
- [ ] Reading level specified
- [ ] Translation requirements documented
- [ ] Format accessibility considered

### 6. Traceability

Required cumulative tags:
- `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`

### 7. DOC-Ready Score

| Component | Weight | Minimum |
|-----------|--------|---------|
| Content Coverage | 25% | 100% |
| Audience Alignment | 20% | 90% |
| Structure Completeness | 20% | 90% |
| Style Compliance | 15% | 85% |
| Accessibility | 10% | 85% |
| Traceability | 10% | 100% |

**Target**: DOC-Ready ≥85%

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| DSPEC-E001 | Error | Missing audience definition |
| DSPEC-E002 | Error | Incomplete content outline |
| DSPEC-E003 | Error | Missing document type |
| DSPEC-W001 | Warning | Style guide not referenced |
| DSPEC-W002 | Warning | DOC-Ready score below threshold |

## References

- Schema: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
