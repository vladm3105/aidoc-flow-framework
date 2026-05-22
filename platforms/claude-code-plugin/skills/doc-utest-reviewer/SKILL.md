---
name: doc-utest-reviewer
description: Review unit-focused TDD (Layer 7) test cases for coverage rigor and unit category completeness
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-unit-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: unit
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-utest-reviewer

## Purpose

Perform semantic quality review for unit-focused **TDD (Layer 7)** test cases
beyond structural validation.

This skill is a **TDD (Layer 7) specialization** for the unit-test focus of TDD.
It reviews against the single canonical artifact contract
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, see `../doc-tdd/`) and does **not**
define a separate artifact, template, or element-code.

**Layer**: 7 (TDD — unit-test focus)

---

## Review Scope

1. Unit category completeness (logic, state, validation, edge)
2. SPEC-to-test traceability completeness and consistency
3. Unit coverage quality and gate compliance (`>=90%`)
4. Input/expected-output clarity for each unit case
5. Edge-case adequacy for complex unit logic

---

## Unit-Test Gate Policy

- IPLAN-Ready target: `>=90`.
- Unit coverage target: `>=90%`.
- Missing category coverage or missing inputs/outputs is `manual_required`.
- Missing edge cases for complex logic is `manual_required`.

---

## Output Contract

Reviewer-native output:
- `TDD-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-utest-audit` may emit `TDD-NN.A_audit_report_vNNN.md` as the preferred
  fixer input.

All reports are colocated with the parent TDD document.

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
- `../doc-tdd/` (parent TDD authoring skill)

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as a valid source mode and verify intent
  preservation from implementation plan scope/objectives.
- Validate the upstream autopilot precedence assumption:
  `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as
  blocking issues requiring clarification.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Reviews unit-focused TDD test cases (no UTEST/TSPEC artifact or numeric code); SPEC traceability and 4-segment IDs (`TDD.NN.04.xxxx`, `type: unit`); audit-compatible report contract retained. |
| 1.0 | 2026-02-27 | Initial unit-test reviewer (pre-migration legacy layer). |
