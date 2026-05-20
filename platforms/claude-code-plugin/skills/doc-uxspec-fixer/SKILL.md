---
name: doc-uxspec-fixer
description: Automated fix skill that reads review reports and applies fixes to UXSPEC documents - handles structure issues and iterative improvement
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
    upstream_artifacts: [REQ, UXSPEC, Review Report]
    downstream_artifacts: [Fixed UXSPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-uxspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to UXSPEC (UX Specification) documents.

**Layer**: 9.52 (UXSPEC Quality Improvement)

---

## Fixable Issue Types

### Automatic Fixes
- Missing `document_type` → Add `document_type: uxspec-document`
- Missing `subtype_code` → Add `subtype_code: 52`
- Broken internal links → Update to correct paths
- Missing traceability tags → Add required cumulative tags

### Manual Review Required
- Visual design decisions
- Interaction pattern choices
- Accessibility violations

---

## Output Files

| File | Purpose |
|------|---------|
| Updated UXSPEC YAML | Fixed document |
| `UXSPEC-NN.F_fix_report_vNNN.md` | Fix report |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/UXSPEC/UXSPEC_MVP_SCHEMA.yaml`
