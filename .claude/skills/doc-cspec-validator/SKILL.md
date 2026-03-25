---
name: doc-cspec-validator
description: Validate Code Specifications (CSPEC) documents against Layer 9.50 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - cspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 50
    artifact_type: CSPEC
    deliverable_type: code
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [CSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-cspec-validator

Validate Code Specifications (CSPEC) documents against Layer 9.50 schema standards.

## Activation

Invoke when user requests validation of CSPEC documents or after creating/modifying CSPEC artifacts.

## Validation Schema Reference

- Schema: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
- Layer: 9.50
- Artifact Type: CSPEC
- Deliverable Type: code

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Required Structure**:

| CSPEC Type | Required Location |
|------------|-------------------|
| YAML | `docs/09_SPEC/CSPEC/CSPEC-NN_{slug}/CSPEC-NN_{slug}.yaml` |

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `cspec-document` |
| `artifact_type` | Yes | `CSPEC` |
| `deliverable_type` | Yes | `code` |
| `subtype_code` | Yes | `50` |
| `layer` | Yes | `9` |

### 2. CTR Compliance (MANDATORY for CSPEC)

CSPEC requires CTR contract:
- [ ] CTR reference exists in traceability
- [ ] Interface definitions match CTR schema
- [ ] API contracts are implemented

### 3. Interface Definitions

- [ ] All interfaces have complete signatures
- [ ] Parameter types are specified
- [ ] Return types are specified
- [ ] Error handling is defined

### 4. Implementation Details

- [ ] Classes/modules are specified
- [ ] Methods have algorithms defined
- [ ] Dependencies are listed
- [ ] Configuration is documented

### 5. Test Mapping

- [ ] Unit test cases mapped to methods
- [ ] Integration test cases mapped to interfaces
- [ ] Coverage requirements specified

### 6. Traceability

Required cumulative tags:
- `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@ctr`

### 7. CODE-Ready Score

| Component | Weight | Minimum |
|-----------|--------|---------|
| Interface Completeness | 20% | 100% |
| CTR Compliance | 20% | 100% |
| Algorithm Specification | 15% | 90% |
| Error Handling | 15% | 90% |
| Test Mapping | 15% | 90% |
| Traceability | 15% | 100% |

**Target**: CODE-Ready ≥90%

## Validation Commands

```bash
# Validate single CSPEC
python ai_dev_ssd_flow/09_SPEC/scripts/validate_spec.py \
  --spec-file docs/09_SPEC/CSPEC/CSPEC-NN_{slug}/CSPEC-NN_{slug}.yaml \
  --subtype CSPEC

# Validate all CSPECs
python ai_dev_ssd_flow/09_SPEC/scripts/validate_spec.py \
  --directory docs/09_SPEC/CSPEC \
  --subtype CSPEC
```

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| CSPEC-E001 | Error | Missing CTR reference |
| CSPEC-E002 | Error | Incomplete interface definition |
| CSPEC-E003 | Error | Missing algorithm specification |
| CSPEC-W001 | Warning | Test mapping incomplete |
| CSPEC-W002 | Warning | CODE-Ready score below threshold |

## References

- Schema: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
