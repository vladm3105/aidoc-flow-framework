---
name: doc-ptest-reviewer
description: Review PTEST content quality, threshold coverage, and performance scenario completeness for performance test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ptest-review
  custom_fields:
    layer: 10
    artifact_type: PTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [PTEST]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks PTEST-MVP-TEMPLATE schema_version"
---

# doc-ptest-reviewer

## Purpose

Perform semantic quality review for PTEST artifacts beyond structural validation.

---

## Review Scope

1. SYS and SPEC alignment for performance requirements
2. Category completeness (`[Load]`, `[Stress]`, `[Endurance]`, `[Spike]`)
3. Load scenario realism and threshold measurability
4. Execution profile completeness for complex scenarios
5. Traceability completeness and consistency

---

## Output Contract

Reviewer-native output:
- `PTEST-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-ptest-audit` may emit `PTEST-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with parent PTEST file.

---

## Score Gate

- Pass target: score `>=90`
- Manual-required findings block automated completion.

---

## Related Skills

- `doc-ptest-validator`
- `doc-ptest-fixer`
- `doc-ptest-audit`
- `doc-ptest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial PTEST reviewer with audit-compatible report contract and threshold-based pass gate |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

