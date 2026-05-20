---
name: doc-uxspec-audit
description: Unified UXSPEC quality gate - validates structure, detects issues, computes DESIGN-Ready score
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
    downstream_artifacts: [Audit Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-uxspec-audit

## Purpose

Unified **UXSPEC quality gate** that combines structural validation, content review, and DESIGN-Ready scoring.

**Layer**: 9.52 (UXSPEC Quality Gate)

---

## DESIGN-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Layout Completeness | 20% | All screens specified |
| Interaction Spec | 20% | User interactions defined |
| Visual Consistency | 20% | Design system compliance |
| Accessibility | 15% | WCAG requirements met |
| Responsive Design | 15% | Breakpoints defined |
| Traceability | 10% | Cumulative tags present |

**Thresholds**:
- **PASS**: ≥85%
- **CONDITIONAL**: 75-84%
- **FAIL**: <75%

---

## Output Files

| File | Purpose |
|------|---------|
| `UXSPEC-NN.A_audit_report_vNNN.md` | Audit report |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml`
