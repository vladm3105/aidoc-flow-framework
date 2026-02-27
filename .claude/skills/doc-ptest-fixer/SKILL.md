---
name: doc-ptest-fixer
description: Apply automated and guided fixes for PTEST findings from audit/review reports
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ptest-fix
  custom_fields:
    layer: 10
    artifact_type: PTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [PTEST, Audit Report, Review Report]
    downstream_artifacts: [Fixed PTEST, Fix Report]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks PTEST-MVP-TEMPLATE schema_version"
---

# doc-ptest-fixer

## Purpose

Apply fixes for PTEST issues identified by validator/reviewer workflows, with deterministic source-report precedence.

---

## Input Contract

Preferred:
- `PTEST-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `PTEST-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required sections (6-section contract)
- Missing/invalid subtype tags (`@sys`, `@spec`)
- Missing performance categories or load scenario tables
- Non-measurable threshold definitions
- Incomplete execution profile for complex scenarios
- Traceability and cross-reference consistency
- Naming/path corrections for nested-folder compliance

---

## Outputs

- Fixed PTEST document(s)
- `PTEST-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-ptest-fixer PTEST-01
/doc-ptest-fixer PTEST-01 --review-report PTEST-01.A_audit_report_v001.md
/doc-ptest-fixer PTEST-01 --review-report PTEST-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-ptest-audit`
- Re-run `doc-ptest-audit` after fixes to verify closure

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial PTEST fixer with deterministic `.A_` preferred / `.R_` legacy precedence and versioned fix report contract |
