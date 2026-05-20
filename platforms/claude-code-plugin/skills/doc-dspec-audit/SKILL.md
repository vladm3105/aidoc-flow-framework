---
name: doc-dspec-audit
description: Unified DSPEC quality gate - validates structure, detects issues, computes DOC-Ready score, and produces report for fixer
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - dspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 51
    artifact_type: DSPEC
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [DSPEC]
    downstream_artifacts: [Audit Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-dspec-audit

## Purpose

Unified **DSPEC quality gate** that combines structural validation, content review, and DOC-Ready scoring into a single comprehensive audit.

**Layer**: 9.51 (DSPEC Quality Gate)

---

## DOC-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Content Coverage | 25% | All REQ topics addressed |
| Audience Alignment | 20% | Audience analysis complete |
| Structure Completeness | 20% | Content outline complete |
| Style Compliance | 15% | Style guide referenced |
| Accessibility | 10% | Accessibility requirements met |
| Traceability | 10% | All cumulative tags present |

**Thresholds**:
- **PASS**: ≥85%
- **CONDITIONAL**: 75-84%
- **FAIL**: <75%

---

## Output Files

| File | Purpose |
|------|---------|
| `DSPEC-NN.A_audit_report_vNNN.md` | Comprehensive audit report |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
