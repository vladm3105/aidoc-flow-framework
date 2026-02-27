---
name: doc-itest-reviewer
description: Review ITEST content quality, contract alignment, and interaction completeness for integration test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - itest-review
  custom_fields:
    layer: 10
    artifact_type: ITEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [ITEST]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks ITEST-MVP-TEMPLATE schema_version"
---

# doc-itest-reviewer

## Purpose

Perform semantic quality review for ITEST artifacts beyond structural validation.

---

## Review Scope

1. CTR and SYS alignment for integration points
2. Contract compliance completeness (schema/status/headers, where applicable)
3. Interaction flow validation (sequence and data flow)
4. Test case completeness and side-effect/error-path coverage
5. Traceability completeness and consistency

---

## Output Contract

Reviewer-native output:
- `ITEST-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-itest-audit` may emit `ITEST-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with parent ITEST file.

---

## Score Gate

- Pass target: score `>=90`
- Manual-required findings block automated completion.

---

## Related Skills

- `doc-itest-validator`
- `doc-itest-fixer`
- `doc-itest-audit`
- `doc-itest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial ITEST reviewer with audit-compatible report contract and threshold-based pass gate |
