---
name: doc-procspec-fixer
description: Automated fix skill that reads review reports and applies fixes to process-spec SPEC (Layer 6) documents - handles structure issues and iterative improvement
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: process-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC, Review Report]
    downstream_artifacts: [Fixed SPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-procspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to
process-spec SPEC documents. This is a plugin-only authoring helper — a
process/workflow-design specialization of SPEC (Layer 6) — operating against the
single framework SPEC template (`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`,
see `../doc-spec/`).

**Layer**: 6 (SPEC — process-design quality improvement)

**Parent**: `../doc-spec/`

**Upstream**: SPEC, Review Report

**Downstream**: Fixed SPEC, Fix Report

---

## Fixable Issue Types

### Automatic Fixes
- Missing `document_type` → Add `document_type: spec-document`
- Missing `spec_focus` → Add `spec_focus: process-design`
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
| Updated SPEC YAML | Fixed document |
| `SPEC-NN.F_fix_report_vNNN.md` | Fix report |

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
