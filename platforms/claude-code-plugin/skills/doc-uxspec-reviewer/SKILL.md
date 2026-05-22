---
name: doc-uxspec-reviewer
description: Content review and quality assurance for UX-focused SPEC (Layer 6) documents - validates UX specification completeness, design consistency, and accessibility
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
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC]
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-uxspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for UX-focused SPEC documents
(Layer 6). Validates layout completeness, interaction specifications, visual
consistency, and accessibility compliance. This is the UX/interface-design
specialization of the SPEC layer — it reviews SPEC documents whose `spec_focus` is `ux`.

**Layer**: 6 (SPEC — UX-focused quality assurance)

---

## Review Checklist

### 1. Layout Review
- [ ] All screens/views specified
- [ ] Component hierarchy clear
- [ ] Spacing/grid system defined

### 2. Interaction Review
- [ ] User interactions specified
- [ ] State transitions defined
- [ ] Micro-interactions documented

### 3. Visual Consistency
- [ ] Design tokens referenced
- [ ] Color palette compliant
- [ ] Typography consistent

### 4. Accessibility Review
- [ ] WCAG compliance checked
- [ ] Keyboard navigation specified
- [ ] Screen reader considerations

### 5. Responsive Design
- [ ] Breakpoints defined
- [ ] Mobile-first approach
- [ ] Touch targets appropriate

### 6. Traceability Review
- [ ] Upstream tags present (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`)
- [ ] Element IDs use 4-segment `TYPE.NN.SS.xxxx`; ADR uses `ADR-NN`
- [ ] Document referenced as `@spec: SPEC-NN`

---

## Review Procedure

The framework ships no runtime review scripts — **this skill is the reviewer**.
Walk the checklist above declaratively against each UX-focused SPEC document and
emit a review report for `doc-uxspec-fixer` to consume.

## References

- Parent SPEC skill: `../doc-spec/SKILL.md`
- Fixer: `../doc-uxspec-fixer/SKILL.md`
- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer contract: `framework/layers/06_SPEC/README.md`
- ID rules: `framework/governance/ID_NAMING_STANDARDS.md`
