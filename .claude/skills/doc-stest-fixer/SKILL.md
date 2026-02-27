---
name: doc-stest-fixer
description: Apply automated and guided fixes for STEST findings from audit/review reports
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - stest-fix
  custom_fields:
    layer: 10
    artifact_type: STEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [STEST, Audit Report, Review Report]
    downstream_artifacts: [Fixed STEST, Fix Report]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks STEST-MVP-TEMPLATE schema_version"
---

# doc-stest-fixer

## Purpose

Apply fixes for STEST issues identified by validator/reviewer workflows, with deterministic source-report precedence.

---

## Input Contract

Preferred:
- `STEST-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `STEST-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required sections (6-section contract)
- Missing/invalid subtype tags (`@ears`, `@bdd`, `@req`)
- Missing timeout or 100%-gate constraints
- Missing rollback procedure requirements
- Non-binary pass/fail criteria in critical-path checks
- Traceability and cross-reference consistency
- Naming/path corrections for nested-folder compliance

---

## Outputs

- Fixed STEST document(s)
- `STEST-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-stest-fixer STEST-01
/doc-stest-fixer STEST-01 --review-report STEST-01.A_audit_report_v001.md
/doc-stest-fixer STEST-01 --review-report STEST-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-stest-audit`
- Re-run `doc-stest-audit` after fixes to verify closure

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial STEST fixer with deterministic `.A_` preferred / `.R_` legacy precedence and strict deployment-gate remediation checks |
