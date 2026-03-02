---
name: doc-riskspec-fixer
description: Automated fix skill that reads review reports and applies fixes to RISKSPEC documents - handles structure issues and iterative improvement
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
    upstream_artifacts: [REQ, RISKSPEC, Review Report]
    downstream_artifacts: [Fixed RISKSPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-riskspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to RISKSPEC (Risk Specification) documents.

**Layer**: 9.53 (RISKSPEC Quality Improvement)

---

## Fixable Issue Types

### Automatic Fixes
- Missing `document_type` → Add `document_type: riskspec-document`
- Missing `subtype_code` → Add `subtype_code: 53`
- Broken internal links → Update to correct paths
- Missing traceability tags → Add required cumulative tags

### Manual Review Required
- Risk rating decisions
- Control effectiveness assessments
- Mitigation strategy choices

---

## Output Files

| File | Purpose |
|------|---------|
| Updated RISKSPEC YAML | Fixed document |
| `RISKSPEC-NN.F_fix_report_vNNN.md` | Fix report |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/RISKSPEC/RISKSPEC_MVP_SCHEMA.yaml`
