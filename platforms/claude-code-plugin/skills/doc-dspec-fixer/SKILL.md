---
name: doc-dspec-fixer
description: Automated fix skill that reads review reports and applies fixes to DSPEC documents - handles broken links, content structure issues, and iterative improvement
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
    upstream_artifacts: [REQ, DSPEC, Review Report]
    downstream_artifacts: [Fixed DSPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-dspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to DSPEC (Documentation Specification) documents. Enables iterative improvement cycles between review and fix phases.

**Layer**: 9.51 (DSPEC Quality Improvement)

**Upstream**: REQ, DSPEC, Review Report

**Downstream**: Fixed DSPEC, Fix Report

---

## Fixable Issue Types

### Automatic Fixes

| Issue Type | Fix Action |
|------------|------------|
| Missing `document_type` | Add `document_type: dspec-document` |
| Missing `subtype_code` | Add `subtype_code: 51` |
| Broken internal links | Update to correct paths |
| Missing traceability tags | Add required cumulative tags |
| YAML syntax errors | Fix formatting issues |

### Semi-Automatic Fixes

| Issue Type | Fix Action |
|------------|------------|
| Missing content outline sections | Generate placeholders |
| Incomplete audience definition | Add template sections |

### Manual Review Required

| Issue Type | Action |
|------------|--------|
| Content accuracy issues | Requires subject matter expert |
| Audience mismatch | Requires stakeholder input |
| Style guide violations | May require editorial review |

---

## Output Files

| File | Purpose |
|------|---------|
| Updated DSPEC YAML | Fixed document |
| `DSPEC-NN.F_fix_report_vNNN.md` | Fix report documenting changes |

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/DSPEC/DSPEC_MVP_SCHEMA.yaml`
