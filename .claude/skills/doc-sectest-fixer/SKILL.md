---
name: doc-sectest-fixer
description: Apply automated and guided fixes for SECTEST findings from audit/review reports
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - sectest-fix
  custom_fields:
    layer: 10
    artifact_type: SECTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SECTEST, Audit Report, Review Report]
    downstream_artifacts: [Fixed SECTEST, Fix Report]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SECTEST-MVP-TEMPLATE schema_version"
---

# doc-sectest-fixer

## Purpose

Apply fixes for SECTEST issues identified by validator/reviewer workflows, with deterministic source-report precedence.

---

## Input Contract

Preferred:
- `SECTEST-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `SECTEST-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required sections (6-section contract)
- Missing/invalid subtype tags (`@sec`, `@spec`)
- Missing security categories, threat scenarios, or controls
- Missing/weak safety constraints or production-targeting language
- Traceability and cross-reference consistency
- Naming/path corrections for nested-folder compliance

---

## Outputs

- Fixed SECTEST document(s)
- `SECTEST-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-sectest-fixer SECTEST-01
/doc-sectest-fixer SECTEST-01 --review-report SECTEST-01.A_audit_report_v001.md
/doc-sectest-fixer SECTEST-01 --review-report SECTEST-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-sectest-audit`
- Re-run `doc-sectest-audit` after fixes to verify closure

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial SECTEST fixer with deterministic `.A_` preferred / `.R_` legacy precedence, safety remediation checks, and versioned fix report contract |
