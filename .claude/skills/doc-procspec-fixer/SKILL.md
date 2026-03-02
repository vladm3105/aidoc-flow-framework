---
name: doc-procspec-fixer
description: Automated fix skill that reads review reports and applies fixes to PROCSPEC documents - handles structure issues and iterative improvement
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - procspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 54
    artifact_type: PROCSPEC
    deliverable_type: process
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [REQ, PROCSPEC, Review Report]
    downstream_artifacts: [Fixed PROCSPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-procspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to PROCSPEC (Process Specification) documents.

**Layer**: 9.54 (PROCSPEC Quality Improvement)

---

## Fixable Issue Types

### Automatic Fixes
- Missing `document_type` → Add `document_type: procspec-document`
- Missing `subtype_code` → Add `subtype_code: 54`
- Broken internal links → Update to correct paths
- Missing traceability tags → Add required cumulative tags

### Manual Review Required
- Process flow decisions
- Role assignment choices
- Error handling strategies

---

## Output Files

| File | Purpose |
|------|---------|
| Updated PROCSPEC YAML | Fixed document |
| `PROCSPEC-NN.F_fix_report_vNNN.md` | Fix report |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/PROCSPEC/PROCSPEC_MVP_SCHEMA.yaml`
