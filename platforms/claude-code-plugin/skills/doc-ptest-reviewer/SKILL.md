---
name: doc-ptest-reviewer
description: Review performance-focused TDD (Layer 7) content quality, threshold coverage, and performance scenario completeness
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-performance-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: performance
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-ptest-reviewer

## Purpose

Perform semantic quality review for performance-focused **TDD (Layer 7)** test
cases beyond structural validation.

This skill is a **TDD (Layer 7) specialization** for the performance-test
focus. It reviews TDD documents against the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code.

---

## Review Scope

1. SPEC and ADR alignment for performance requirements
2. Performance scenario completeness (Load / Stress / Endurance / Spike)
3. Load scenario realism and threshold measurability
4. `execution_profile` completeness for complex scenarios
5. Traceability completeness and consistency (cumulative `@brd`..`@spec` + `@tdd`)

---

## Output Contract

Reviewer-native output:
- `TDD-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-ptest-audit` may emit `TDD-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with the parent TDD document.

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
- `../doc-tdd/` (parent TDD authoring skill)

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`
- Parent TDD skill: `../doc-tdd/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) performance-test reviewer over the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; review scope recast to SPEC/ADR alignment and performance scenarios; report contract `TDD-NN.R_…`. |
| 1.0 | 2026-02-27 | Initial PTEST reviewer (pre-migration, legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
