---
name: doc-dspec-fixer
description: Automated fix skill that reads review reports and applies fixes to data-spec SPEC (Layer 6) documents - handles broken links, data-model structure issues, and iterative improvement
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: data-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, Review Report]
    downstream_artifacts: [Fixed SPEC, Fix Report]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-dspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes
to data-spec SPEC (Layer 6) documents. Enables iterative improvement cycles
between review and fix phases. This is a plugin-only authoring helper — a
data-design specialization of SPEC — that operates on documents conforming to
the single framework SPEC template.

**Layer**: 6 (SPEC — data-design quality improvement)

**Parent**: `../doc-spec/`

**Upstream**: BRD, PRD, EARS, BDD, ADR, Review Report

**Downstream**: Fixed SPEC, Fix Report

---

## Fixable Issue Types

### Automatic Fixes

| Issue Type | Fix Action |
|------------|------------|
| Missing `document_type` | Add `document_type: spec-document` |
| Missing `layer` | Add `layer: 6` |
| Broken internal links | Update to correct framework paths |
| Missing traceability tags | Add required upstream tags |
| YAML syntax errors | Fix formatting issues |

### Semi-Automatic Fixes

| Issue Type | Fix Action |
|------------|------------|
| Missing data-model fields | Generate typed-field placeholders |
| Incomplete interface definition | Add template signature stubs |

### Manual Review Required

| Issue Type | Action |
|------------|--------|
| Data-model accuracy issues | Requires subject matter expert |
| Behavior/contract mismatch | Requires stakeholder input |
| Architecture-decision conflicts | May require ADR revision |

---

## Output Files

| File | Purpose |
|------|---------|
| Updated SPEC YAML | Fixed document |
| `SPEC-NN.F_fix_report_vNNN.md` | Fix report documenting changes |

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
