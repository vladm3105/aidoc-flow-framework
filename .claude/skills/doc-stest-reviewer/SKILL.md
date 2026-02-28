---
name: doc-stest-reviewer
description: Review STEST content quality, timeout/rollback compliance, and critical-path pass/fail rigor for smoke test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - stest-review
  custom_fields:
    layer: 10
    artifact_type: STEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [STEST]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks STEST-MVP-TEMPLATE schema_version"
---

# doc-stest-reviewer

## Purpose

Perform semantic quality review for STEST artifacts beyond structural validation.

---

## Review Scope

1. Deployment critical-path coverage completeness
2. Timeout budget realism and compliance (`<=300s` / max 300s)
3. Rollback procedure completeness for each test case
4. Binary pass/fail criteria clarity and fail-fast behavior
5. EARS/BDD/REQ traceability completeness and consistency

---

## Deployment Gate Policy

- Target: 100% (`100% quality gate`).
- Every test must have rollback procedure.
- Timeout budget markers must be explicit (`max 300s` or `<=300s`).
- Any missing critical deployment gate element is `manual_required` or `blocked`.

---

## Output Contract

Reviewer-native output:
- `STEST-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-stest-audit` may emit `STEST-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with parent STEST file.

---

## Score Gate

- Pass target: score `=100`
- Manual-required findings block automated completion.

---

## Related Skills

- `doc-stest-validator`
- `doc-stest-fixer`
- `doc-stest-audit`
- `doc-stest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial STEST reviewer with audit-compatible report contract and strict 100% deployment-gate pass rule |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

