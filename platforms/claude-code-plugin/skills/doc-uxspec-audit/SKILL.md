---
name: doc-uxspec-audit
description: Quality gate for UX-focused SPEC (Layer 6) documents - validates structure, detects issues, computes DESIGN-Ready score
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
    downstream_artifacts: [Audit Report]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-uxspec-audit

## Purpose

Quality gate for **UX-focused SPEC documents** (Layer 6) that combines structural
validation, content review, and DESIGN-Ready scoring. This is the UX/interface-design
specialization of the SPEC layer — it audits SPEC documents whose `spec_focus` is `ux`
(wireframes, mockups, prototypes, user journeys), not a separate artifact type.

**Layer**: 6 (SPEC — UX-focused quality gate)

A UX-focused SPEC is a SPEC document. It uses the single SPEC template; this skill
adds UX-design audit criteria on top of the standard SPEC checks.

---

## DESIGN-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Layout Completeness | 20% | All screens specified |
| Interaction Spec | 20% | User interactions defined |
| Visual Consistency | 20% | Design system compliance |
| Accessibility | 15% | WCAG requirements met |
| Responsive Design | 15% | Breakpoints defined |
| Traceability | 10% | Upstream tags present |

**Thresholds**:
- **PASS**: ≥85%
- **CONDITIONAL**: 75-84%
- **FAIL**: <75%

---

## Output Files

| File | Purpose |
|------|---------|
| `SPEC-NN.A_audit_report_vNNN.md` | Audit report |

---

## Validation Procedure

The framework ships no runtime validation scripts — **this skill is the auditor**.
Apply the DESIGN-Ready criteria above declaratively against each UX-focused SPEC
document, record findings, and emit the audit report.

## References

- Parent SPEC skill: `../doc-spec/SKILL.md`
- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer contract: `framework/layers/06_SPEC/README.md`
- ID rules: `framework/governance/ID_NAMING_STANDARDS.md`
