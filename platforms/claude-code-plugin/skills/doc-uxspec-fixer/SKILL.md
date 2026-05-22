---
name: doc-uxspec-fixer
description: Reads review reports and applies fixes to UX-focused SPEC (Layer 6) documents - handles structure issues and iterative improvement
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: ux
    deliverable_type: ux
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SPEC, Review Report]
    downstream_artifacts: [Fixed SPEC, Fix Report]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-uxspec-fixer

## Purpose

Automated **fix skill** that reads the latest review report and applies fixes to
UX-focused SPEC documents (Layer 6). This is the UX/interface-design specialization of
the SPEC layer — it repairs SPEC documents whose `spec_focus` is `ux`.

**Layer**: 6 (SPEC — UX-focused quality improvement)

---

## Fixable Issue Types

### Automatic Fixes
- Missing `document_type` → Add `document_type: spec-document`
- Missing `spec_focus` → Add `spec_focus: ux`
- Broken internal links → Update to correct paths
- Missing traceability tags → Add required upstream tags (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`)

### Manual Review Required
- Visual design decisions
- Interaction pattern choices
- Accessibility violations

---

## Output Files

| File | Purpose |
|------|---------|
| Updated SPEC YAML | Fixed document |
| `SPEC-NN.F_fix_report_vNNN.md` | Fix report |

---

## Fix Procedure

The framework ships no runtime fix scripts — **this skill is the fixer**. Read the
review report, apply the automatic fixes above, flag manual-review items, and emit
the fix report. Never introduce legacy `@sys`/`@req`/`@ctr` tags or 3-segment
element IDs.

## References

- Parent SPEC skill: `../doc-spec/SKILL.md`
- Reviewer: `../doc-uxspec-reviewer/SKILL.md`
- Template (single source of truth): `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer contract: `framework/layers/06_SPEC/README.md`
- ID rules: `framework/governance/ID_NAMING_STANDARDS.md`
