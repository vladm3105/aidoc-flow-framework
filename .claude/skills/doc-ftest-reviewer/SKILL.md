---
name: doc-ftest-reviewer
description: Review FTEST content quality, SYS alignment, and threshold validation completeness for functional test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ftest-review
  custom_fields:
    layer: 10
    artifact_type: FTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [FTEST]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks FTEST-MVP-TEMPLATE schema_version"
---

# doc-ftest-reviewer

## Purpose

Perform semantic quality review for FTEST artifacts beyond structural validation.

---

## Review Scope

1. SYS requirement alignment and quality-attribute coverage
2. Threshold definitions and measurable validation criteria
3. Test case completeness (workflow steps + measurement methodology)
4. Edge-case and failure-condition coverage
5. Traceability completeness and consistency

---

## Output Contract

Reviewer-native output:
- `FTEST-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-ftest-audit` may emit `FTEST-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with parent FTEST file.

---

## Score Gate

- Pass target: score `>=90`
- Manual-required findings block automated completion.

---

## Related Skills

- `doc-ftest-validator`
- `doc-ftest-fixer`
- `doc-ftest-audit`
- `doc-ftest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial FTEST reviewer with audit-compatible report contract and threshold-based pass gate |
