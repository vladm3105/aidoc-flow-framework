---
name: doc-riskspec-audit
description: Unified RISKSPEC quality gate - validates structure, detects issues, computes RISK-Ready score
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - riskspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 53
    artifact_type: RISKSPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [RISKSPEC]
    downstream_artifacts: [Audit Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-riskspec-audit

## Purpose

Unified **RISKSPEC quality gate** that combines structural validation, content review, and RISK-Ready scoring.

**Layer**: 9.53 (RISKSPEC Quality Gate)

---

## RISK-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Risk Identification | 25% | All risks identified |
| Impact Analysis | 20% | Ratings justified |
| Control Mapping | 20% | Controls defined |
| Mitigation Plans | 15% | Actions specified |
| Residual Risk | 10% | Post-mitigation assessed |
| Traceability | 10% | Cumulative tags present |

**Thresholds**:
- **PASS**: ≥85%
- **CONDITIONAL**: 75-84%
- **FAIL**: <75%

---

## Output Files

| File | Purpose |
|------|---------|
| `RISKSPEC-NN.A_audit_report_vNNN.md` | Audit report |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
