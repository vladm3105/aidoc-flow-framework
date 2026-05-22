---
name: doc-uxspec-autopilot
description: Automated generation of UX-focused SPEC (Layer 6) documents - specifications for wireframes, mockups, and user experience artifacts
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - automation-workflow
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: ux
    deliverable_type: ux
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-uxspec-autopilot

## Purpose

Automated **UX-focused SPEC** generation pipeline that processes upstream artifacts
to produce SPEC documents for user-experience deliverables — wireframes, mockups,
prototypes, and user journeys. This is the UX/interface-design specialization of the
SPEC layer; it authors standard SPEC documents with `spec_focus: ux`, not a separate
artifact type.

**Layer**: 6 (SPEC — UX-focused authoring)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5)

**Downstream**: TDD (Layer 7), IPLAN (Layer 8), Code

---

## When to Use

Use `doc-uxspec-autopilot` when:
- Upstream PRD/BDD describe user-experience deliverables
- Creating SPEC documents for wireframes
- Generating mockup specifications
- Creating prototype requirements
- Specifying user journey designs

---

## Document Type Contract (MANDATORY)

When generating UX-focused SPEC document instances, the autopilot MUST:

1. **Read** the SPEC template (single source of truth):
   - Source: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
   - The document is a SPEC; the UX focus is a content specialization, not a new schema.

2. **Set** the standard SPEC frontmatter, marking the UX focus:
   ```yaml
   custom_fields:
     document_type: spec-document
     artifact_type: SPEC
     spec_focus: ux
     deliverable_type: ux
     layer: 6
   ```

---

## UX Content Categories

These describe the UX content captured inside the SPEC document — they are SPEC
section content, not ID type-codes.

| Category | Description |
|--------------|-------------|
| Wireframe | Low-fidelity layout |
| Mockup | High-fidelity visual design |
| Prototype | Interactive prototype |
| User Journey | User flow visualization |

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

## Traceability

A UX-focused SPEC carries the standard SPEC upstream tags (4-segment element IDs
`TYPE.NN.SS.xxxx`; ADR uses document-level `ADR-NN`):
`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`. The document itself is referenced as
`@spec: SPEC-NN`. No `@sys`/`@req`/`@ctr` tags — the 8-layer model has no SYS/REQ/CTR.

## References

- Parent SPEC skill: `../doc-spec/SKILL.md`
- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer contract: `framework/layers/06_SPEC/README.md`
- ID rules: `framework/governance/ID_NAMING_STANDARDS.md`
