---
name: doc-cspec-autopilot
description: Automated CSPEC (Code Specification) generation from REQ/CTR - generates implementation-ready YAML specifications for source code deliverables
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - cspec-artifact
    - automation-workflow
  custom_fields:
    layer: 9
    subtype_code: 50
    artifact_type: CSPEC
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [REQ, CTR]
    downstream_artifacts: [TSPEC, TASKS]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-cspec-autopilot

## Purpose

Automated **Code Specification (CSPEC)** generation pipeline that processes REQ documents (with mandatory CTR) to generate implementation-ready YAML specifications for source code deliverables.

**Layer**: 9.50 (CSPEC - Code Specifications)

**Upstream**: REQ (Layer 7), CTR (Layer 8 - required for CSPEC)

**Downstream**: TSPEC (Layer 10), TASKS (Layer 11)

---

## When to Use

Use `doc-cspec-autopilot` when:
- REQ documents have `deliverable_type: code` (or unspecified, as code is default)
- CTR contracts exist for API/interface definitions
- Generating specifications for source code implementation
- Creating YAML specs for services, libraries, modules

---

## Document Type Contract (MANDATORY)

When generating CSPEC document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "cspec-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: cspec-document    # NOT "template"
     artifact_type: CSPEC
     deliverable_type: code
     layer: 9
     subtype_code: 50
   ```

3. **Validation**: Generated documents MUST have `document_type: cspec-document`

---

## Skill Dependencies

| Skill | Purpose | Phase |
|-------|---------|-------|
| `doc-naming` | Element ID format (CSPEC.NN.xxxx, codes 50-54) | All Phases |
| `doc-req-validator` | Validate REQ SPEC-Ready score | Phase 2 |
| `doc-ctr-validator` | Validate CTR contracts (required for CSPEC) | Phase 2 |
| `doc-cspec-validator` | Validation with CODE-Ready scoring | Phase 4 |
| `doc-cspec-reviewer` | Content review, quality scoring | Phase 5 |

---

## Execution Phases

### Phase 1: Input Analysis
- Identify REQ documents with `deliverable_type: code`
- Locate corresponding CTR contracts (required)
- Extract interface definitions from CTR

### Phase 2: Readiness Validation
- Verify REQ SPEC-Ready score ≥90%
- Verify CTR contracts are complete
- Check all dependencies are satisfied

### Phase 3: CSPEC Generation
- Create CSPEC YAML from template
- Map REQ requirements to specification elements
- Include CTR interface definitions
- Add implementation details (classes, methods, algorithms)

### Phase 4: Validation
- Run `doc-cspec-validator`
- Check CODE-Ready score ≥90%
- Verify CTR compliance

### Phase 5: Review
- Run `doc-cspec-reviewer`
- Generate audit report
- Apply fixes if needed via `doc-cspec-fixer`

---

## Output Structure

```
09_SPEC/CSPEC/CSPEC-NN_{slug}/
├── CSPEC-NN_{slug}.yaml        # Primary CSPEC document
├── CSPEC-NN.0_index.md         # Index (if split needed)
└── CSPEC-NN.A_audit_report.md  # Audit report
```

---

## CODE-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Interface Completeness | 20% | 100% |
| CTR Compliance | 20% | 100% |
| Algorithm Specification | 15% | ≥90% |
| Error Handling | 15% | ≥90% |
| Test Mapping | 15% | ≥90% |
| Traceability | 15% | 100% |

**Target**: CODE-Ready ≥90%

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
- Creation Rules: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.md`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
