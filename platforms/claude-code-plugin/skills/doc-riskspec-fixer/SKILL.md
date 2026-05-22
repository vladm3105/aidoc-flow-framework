---
name: doc-riskspec-fixer
description: Automated fix skill that reads review reports and applies fixes to risk-analysis SPEC (Layer 6) documents - handles structure issues and iterative improvement
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
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, Review Report]
    downstream_artifacts: [Fixed SPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-riskspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes
to risk-analysis SPEC documents. This is the risk-spec specialization of the
SPEC (Layer 6) authoring helpers — see the parent skill `../doc-spec/` and the
single SPEC template at `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`.

**Layer**: 6 (SPEC quality improvement, risk-analysis focus)

---

## Fixable Issue Types

### Automatic Fixes
- Missing `document_type` → Add `document_type: spec-document`
- Missing `artifact_type` → Add `artifact_type: SPEC`
- Broken internal links → Update to correct paths
- Missing traceability tags → Add required upstream tags

### Manual Review Required
- Risk rating decisions
- Control effectiveness assessments
- Mitigation strategy choices

---

## Output Files

| File | Purpose |
|------|---------|
| Updated SPEC YAML | Fixed document |
| `SPEC-NN.F_fix_report_vNNN.md` | Fix report |

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guidance: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
