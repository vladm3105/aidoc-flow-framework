---
name: doc-dspec-autopilot
description: Automated DSPEC (Documentation Specification) generation from REQ - generates specifications for user guides, API docs, and compliance documentation
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - dspec-artifact
    - automation-workflow
  custom_fields:
    layer: 9
    subtype_code: 51
    artifact_type: DSPEC
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [REQ]
    downstream_artifacts: [TSPEC, TASKS]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-dspec-autopilot

## Purpose

Automated **Documentation Specification (DSPEC)** generation pipeline that processes REQ documents to generate specifications for documentation deliverables including user guides, API documentation, training materials, and compliance documents.

**Layer**: 9.51 (DSPEC - Documentation Specifications)

**Upstream**: REQ (Layer 7)

**Downstream**: TSPEC (Layer 10), TASKS (Layer 11)

---

## When to Use

Use `doc-dspec-autopilot` when:
- REQ documents have `deliverable_type: document`
- Creating specifications for user documentation
- Generating API documentation specs
- Creating training material specifications
- Generating compliance documentation specs

---

## Document Type Contract (MANDATORY)

When generating DSPEC document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "dspec-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: dspec-document    # NOT "template"
     artifact_type: DSPEC
     deliverable_type: document
     layer: 9
     subtype_code: 51
   ```

3. **Validation**: Generated documents MUST have `document_type: dspec-document`

---

## Documentation Types

| Doc Type | Code | Description | Examples |
|----------|------|-------------|----------|
| User Guide | 55 | End-user documentation | Getting started, tutorials |
| API Documentation | 56 | Technical API reference | Endpoints, parameters, examples |
| Compliance Document | 57 | Regulatory compliance | Audit reports, certifications |
| Training Material | 58 | Learning resources | Courses, workshops, assessments |

---

## Skill Dependencies

| Skill | Purpose | Phase |
|-------|---------|-------|
| `doc-naming` | Element ID format (DSPEC.NN.TT.SS, codes 55-58) | All Phases |
| `doc-req-validator` | Validate REQ SPEC-Ready score | Phase 2 |
| `doc-dspec-validator` | Validation with DOC-Ready scoring | Phase 4 |
| `doc-dspec-reviewer` | Content review, quality scoring | Phase 5 |

---

## Execution Phases

### Phase 1: Input Analysis
- Identify REQ documents with `deliverable_type: document`
- Determine documentation type (user guide, API docs, etc.)
- Extract content requirements from REQ

### Phase 2: Readiness Validation
- Verify REQ SPEC-Ready score ≥90%
- Check all dependencies are satisfied
- Validate audience analysis complete

### Phase 3: DSPEC Generation
- Create DSPEC YAML from template
- Map REQ requirements to documentation sections
- Define content structure and outline
- Specify style guide compliance

### Phase 4: Validation
- Run `doc-dspec-validator`
- Check DOC-Ready score ≥85%
- Verify content coverage

### Phase 5: Review
- Run `doc-dspec-reviewer`
- Generate audit report
- Apply fixes if needed via `doc-dspec-fixer`

---

## Output Structure

```
09_SPEC/DSPEC/DSPEC-NN_{slug}/
├── DSPEC-NN_{slug}.yaml        # Primary DSPEC document
├── DSPEC-NN.0_index.md         # Index (if split needed)
└── DSPEC-NN.A_audit_report.md  # Audit report
```

---

## DOC-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Content Coverage | 25% | 100% |
| Audience Alignment | 20% | ≥90% |
| Structure Completeness | 20% | ≥90% |
| Style Compliance | 15% | ≥85% |
| Accessibility | 10% | ≥85% |
| Traceability | 10% | 100% |

**Target**: DOC-Ready ≥85%

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
- Creation Rules: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_CREATION_RULES.md`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_VALIDATION_RULES.md`
