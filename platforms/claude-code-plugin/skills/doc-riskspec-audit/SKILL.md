---
name: doc-riskspec-audit
description: Risk-focused SPEC quality gate (Layer 6) - validates structure, detects issues, computes SPEC-Ready score for risk-analysis specifications
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-document
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    deliverable_type: risk
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [Audit Report]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-riskspec-audit

## Purpose

Quality gate for **risk-analysis SPEC documents** that combines structural
validation, content review, and SPEC-Ready scoring. This is the risk-spec
specialization of the SPEC (Layer 6) authoring helpers — see the parent skill
`../doc-spec/` and the single SPEC template at
`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`.

**Layer**: 6 (SPEC quality gate, risk-analysis focus)

---

## SPEC-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Risk Identification | 25% | All risks identified |
| Impact Analysis | 20% | Ratings justified |
| Control Mapping | 20% | Controls defined |
| Mitigation Plans | 15% | Actions specified |
| Residual Risk | 10% | Post-mitigation assessed |
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

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guidance: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
