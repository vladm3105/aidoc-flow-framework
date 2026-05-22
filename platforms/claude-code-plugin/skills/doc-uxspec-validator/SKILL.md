---
name: doc-uxspec-validator
description: Validate UX-focused SPEC (Layer 6) documents against the SPEC template and UX-design standards
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: ux
    deliverable_type: ux
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-uxspec-validator

Validate UX-focused SPEC documents against the SPEC template (Layer 6) and
UX-design standards. This is the UX/interface-design specialization of the SPEC
layer — it validates SPEC documents whose `spec_focus` is `ux`. A UX-focused SPEC
is a SPEC document; it uses the single SPEC template and adds UX-design checks.

## Validation Schema Reference

- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Standards: `framework/governance/ID_NAMING_STANDARDS.md`, `framework/layers/06_SPEC/README.md`
- Layer: 6
- Artifact Type: SPEC (`spec_focus: ux`)
- Deliverable Type: ux

## Validation Checklist

### 1. Metadata Validation

| Field | Required | Valid Values |
|-------|----------|--------------|
| `document_type` | Yes | `spec-document` |
| `artifact_type` | Yes | `SPEC` |
| `deliverable_type` | Yes | `ux` |
| `spec_focus` | Yes | `ux` |

### 2. UX Content Validation

- [ ] UX content category captured (wireframe / mockup / prototype / user journey)
- [ ] Layout specifications complete
- [ ] Interaction patterns defined
- [ ] Responsive breakpoints specified
- [ ] Accessibility requirements noted

### 3. Traceability Validation

Upstream tags (4-segment element IDs `TYPE.NN.SS.xxxx`; ADR uses document-level `ADR-NN`):
- @brd: BRD.NN.SS.xxxx
- @prd: PRD.NN.SS.xxxx
- @ears: EARS.NN.SS.xxxx
- @bdd: BDD.NN.SS.xxxx
- @adr: ADR-NN

Document reference: `@spec: SPEC-NN`. No `@sys`/`@req`/`@ctr` tags — the 8-layer
model has no SYS/REQ/CTR layers.

**Legacy forms REJECTED**: 3-segment element IDs `TYPE.NN.xxxx`, numeric type-code
IDs, document IDs with extra leading zero `SPEC-NNN`, and any SYS/REQ/CTR upstream.

### 4. DESIGN-Ready Score

**Target**: DESIGN-Ready ≥85%

## Validation Procedure

The framework ships no runtime validation scripts — **this skill is the validator**.
Apply the checklist above declaratively against each UX-focused SPEC document,
record each finding with its severity, and emit a validation report.

## References

- Parent SPEC skill: `../doc-spec/SKILL.md`
- SPEC validator: `../doc-spec-validator/SKILL.md`
- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer contract: `framework/layers/06_SPEC/README.md`
- ID rules: `framework/governance/ID_NAMING_STANDARDS.md`
