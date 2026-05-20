---
name: doc-uxspec-reviewer
description: Comprehensive content review and quality assurance for UXSPEC documents - validates UX specification completeness, design consistency, and accessibility
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
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [UXSPEC]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-uxspec-reviewer

## Purpose

Comprehensive **content review and quality assurance** for UX Specification (UXSPEC) documents. Validates layout completeness, interaction specifications, visual consistency, and accessibility compliance.

**Layer**: 9.52 (UXSPEC Quality Assurance)

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

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml`
