---
name: doc-utest-fixer
description: Apply automated and guided fixes for UTEST findings from audit/review reports
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - utest-fix
  custom_fields:
    layer: 10
    artifact_type: UTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [UTEST, Audit Report, Review Report]
    downstream_artifacts: [Fixed UTEST, Fix Report]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks UTEST-MVP-TEMPLATE schema_version"
---

# doc-utest-fixer

## Purpose

Apply fixes for UTEST issues identified by validator/reviewer workflows, with deterministic source-report precedence.

---

## Input Contract

Preferred:
- `UTEST-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `UTEST-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required sections (6-section contract)
- Missing/invalid subtype tags (`@req`, `@spec`)
- Missing category coverage (`[Logic]`, `[State]`, `[Validation]`, `[Edge]`)
- Missing Input/Output tables for test cases
- Missing pseudocode for complex logic
- REQ coverage below `>=90%` target
- Traceability and cross-reference consistency
- Naming/path corrections for nested-folder compliance

---

## Outputs

- Fixed UTEST document(s)
- `UTEST-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-utest-fixer UTEST-01
/doc-utest-fixer UTEST-01 --review-report UTEST-01.A_audit_report_v001.md
/doc-utest-fixer UTEST-01 --review-report UTEST-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-utest-audit`
- Re-run `doc-utest-audit` after fixes to verify closure

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial UTEST fixer with deterministic `.A_` preferred / `.R_` legacy precedence and UTEST 90%-gate remediation checks |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

