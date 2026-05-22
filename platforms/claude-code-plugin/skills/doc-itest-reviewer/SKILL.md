---
name: doc-itest-reviewer
description: Review integration-focused TDD (Layer 7) content quality, contract alignment, and interaction completeness
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
    - itest-review
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: integration
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

# doc-itest-reviewer

## Purpose

Perform semantic quality review for integration-focused **TDD (Layer 7)** test
cases, beyond structural validation.

This skill is a **TDD (Layer 7) specialization** (integration-test focus); it
operates on TDD documents authored against the single canonical artifact
contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

---

## Review Scope

1. Behavior-contract (`@spec: SPEC-NN`) alignment for integration points
2. Contract-compliance completeness across integration test cases
3. Interaction-flow validation (sequence and data flow)
4. Test-case completeness and side-effect/error-path coverage
5. Traceability completeness and consistency (cumulative @brd through @spec, @tdd self-tag)

---

## Output Contract

Reviewer-native output:
- `TDD-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-itest-audit` may emit `TDD-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with the parent TDD document.

---

## Score Gate

- Pass target: score `>=90`
- Manual-required findings block automated completion.

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Related Skills

- `doc-itest-validator`
- `doc-itest-fixer`
- `doc-itest-audit`
- `doc-itest-autopilot`
- `../doc-tdd/` (parent TDD authoring skill)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) integration-focus reviewer over `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; reports keyed to `TDD-NN`; behavior-contract checks via `@spec: SPEC-NN`. |
| 1.0 | 2026-02-27 | Initial reviewer with audit-compatible report contract and threshold-based pass gate (pre-migration legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan (IPLAN) scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
