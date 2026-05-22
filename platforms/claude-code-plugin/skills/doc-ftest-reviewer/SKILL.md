---
name: doc-ftest-reviewer
description: Review functional-TDD (Layer 7) content quality, behavior alignment, and quality-attribute threshold completeness
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-functional-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    tdd_focus: functional
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

# doc-ftest-reviewer

## Purpose

Perform semantic quality review for functional-focused **TDD (Layer 7)** test
cases, beyond structural validation.

This skill is a **TDD (Layer 7) specialization** for the functional-test focus.
It reviews TDD documents against the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code.

---

## Review Scope

1. Behavior alignment and quality-attribute coverage (functional cases trace to EARS / BDD / SPEC)
2. Quality-attribute threshold definitions and measurable validation criteria (Section 5)
3. Test case completeness (end-to-end workflow steps + measurement methodology)
4. Edge-case and failure-condition coverage
5. Traceability completeness and consistency (cumulative `@brd`..`@spec`, no SYS)

---

## Output Contract

Reviewer-native output:
- `TDD-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-ftest-audit` may emit `TDD-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with the parent TDD document.

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
- `../doc-tdd/` (parent TDD authoring skill)

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Reviews functional-focused TDD (Layer 7) documents against the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; review scope retargeted to EARS/BDD/SPEC behavior alignment and Section 5 quality-attribute thresholds (no SYS); report contract retargeted to `TDD-NN.*`. |
| 1.0 | 2026-02-27 | Initial functional-test reviewer (pre-migration legacy model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
