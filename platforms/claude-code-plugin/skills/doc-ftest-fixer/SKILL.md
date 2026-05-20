---
name: doc-ftest-fixer
description: Apply automated and guided fixes for FTEST findings from audit/review reports
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ftest-fix
  custom_fields:
    layer: 10
    artifact_type: FTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [FTEST, Audit Report, Review Report]
    downstream_artifacts: [Fixed FTEST, Fix Report]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks FTEST-MVP-TEMPLATE schema_version"
---

# doc-ftest-fixer

## Purpose

Apply fixes for FTEST issues identified by validator/reviewer workflows, with deterministic source-report precedence.

---

## Input Contract

Preferred:
- `FTEST-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `FTEST-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required sections (6-section contract)
- Missing/invalid subtype tags (`@sys`, `@threshold`)
- Threshold-table and measurement-methodology completeness
- Traceability and cross-reference consistency
- Naming/path corrections for nested-folder compliance

---

## Outputs

- Fixed FTEST document(s)
- `FTEST-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-ftest-fixer FTEST-01
/doc-ftest-fixer FTEST-01 --review-report FTEST-01.A_audit_report_v001.md
/doc-ftest-fixer FTEST-01 --review-report FTEST-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-ftest-audit`
- Re-run `doc-ftest-audit` after fixes to verify closure

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial FTEST fixer with deterministic `.A_` preferred / `.R_` legacy precedence and versioned fix report contract |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

