---
name: doc-utest-reviewer
description: Review UTEST content quality, REQ coverage rigor, and unit-test category completeness for unit test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - utest-review
  custom_fields:
    layer: 10
    artifact_type: UTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [UTEST]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks UTEST-MVP-TEMPLATE schema_version"
---

# doc-utest-reviewer

## Purpose

Perform semantic quality review for UTEST artifacts beyond structural validation.

---

## Review Scope

1. Unit test category completeness (`[Logic]`, `[State]`, `[Validation]`, `[Edge]`)
2. REQ-to-test traceability completeness and consistency
3. REQ coverage quality and gate compliance (`>=90%`)
4. Input/Output table clarity for each test case
5. Pseudocode adequacy for complex test logic

---

## Unit-Test Gate Policy

- TASKS-Ready target: `>=90%`.
- REQ coverage target: `>=90%`.
- Missing category coverage or missing I/O table is `manual_required`.
- Missing pseudocode for complex logic is `manual_required`.

---

## Output Contract

Reviewer-native output:
- `UTEST-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-utest-audit` may emit `UTEST-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with parent UTEST file.

---

## Score Gate

- Pass target: score `>=90`
- Manual-required findings block automated completion.

---

## Related Skills

- `doc-utest-validator`
- `doc-utest-fixer`
- `doc-utest-audit`
- `doc-utest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial UTEST reviewer with audit-compatible report contract and 90%-gate REQ coverage/category quality checks |
