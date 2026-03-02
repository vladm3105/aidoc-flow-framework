---
name: doc-uxspec-autopilot
description: Automated UXSPEC (UX Specification) generation from REQ - generates specifications for wireframes, mockups, and user experience artifacts
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - uxspec-artifact
    - automation-workflow
  custom_fields:
    layer: 9
    subtype_code: 52
    artifact_type: UXSPEC
    deliverable_type: ux
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [REQ]
    downstream_artifacts: [TSPEC, TASKS]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-uxspec-autopilot

## Purpose

Automated **UX Specification (UXSPEC)** generation pipeline that processes REQ documents to generate specifications for user experience deliverables including wireframes, mockups, prototypes, and user journeys.

**Layer**: 9.52 (UXSPEC - UX Specifications)

**Upstream**: REQ (Layer 7)

**Downstream**: TSPEC (Layer 10), TASKS (Layer 11)

---

## When to Use

Use `doc-uxspec-autopilot` when:
- REQ documents have `deliverable_type: ux`
- Creating specifications for wireframes
- Generating mockup specifications
- Creating prototype requirements
- Specifying user journey designs

---

## Document Type Contract (MANDATORY)

When generating UXSPEC document instances, the autopilot MUST:

1. **Read** `instance_document_type` from template:
   - Source: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml`
   - Field: `metadata.instance_document_type: "uxspec-document"`

2. **Set** `document_type` in generated document frontmatter:
   ```yaml
   custom_fields:
     document_type: uxspec-document
     artifact_type: UXSPEC
     deliverable_type: ux
     layer: 9
     subtype_code: 52
   ```

---

## UX Element Types

| Element Type | Code | Description |
|--------------|------|-------------|
| Wireframe | 60 | Low-fidelity layout |
| Mockup | 61 | High-fidelity visual design |
| Prototype | 62 | Interactive prototype |
| User Journey | 63 | User flow visualization |

---

## DESIGN-Ready Score Components

| Component | Weight | Target |
|-----------|--------|--------|
| Layout Completeness | 20% | 100% |
| Interaction Spec | 20% | ≥90% |
| Visual Consistency | 20% | ≥90% |
| Accessibility | 15% | ≥85% |
| Responsive Design | 15% | ≥85% |
| Traceability | 10% | 100% |

**Target**: DESIGN-Ready ≥85%

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml`
