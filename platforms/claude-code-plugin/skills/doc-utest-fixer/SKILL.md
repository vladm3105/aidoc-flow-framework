---
name: doc-utest-fixer
description: Apply automated and guided fixes for unit-focused TDD (Layer 7) findings from audit/review reports
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
    upstream_artifacts: [TDD, Audit Report, Review Report]
    downstream_artifacts: [Fixed TDD, Fix Report]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-utest-fixer

## Purpose

Apply fixes for unit-focused **TDD (Layer 7)** test-case issues identified by
validator/reviewer workflows, with deterministic source-report precedence.

This skill is a **TDD (Layer 7) specialization** for the unit-test focus of TDD.
It remediates against the single canonical artifact contract
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, see `../doc-tdd/`) and does **not**
define a separate artifact, template, or element-code.

**Layer**: 7 (TDD — unit-test focus)

---

## Input Contract

Preferred:
- `TDD-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `TDD-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required TDD sections
- Missing/invalid tags (`@spec`, cumulative `@brd`..`@spec`, `@tdd` self-tag)
- Missing unit category coverage (logic, state, validation, edge)
- Missing inputs/expected outputs for unit cases
- Missing edge cases for complex logic
- Unit coverage below `>=90%` target
- Traceability and cross-reference consistency
- Element-ID corrections to `TDD.NN.04.xxxx` with `type: unit`

---

## Outputs

- Fixed TDD document(s)
- `TDD-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-utest-fixer TDD-01
/doc-utest-fixer TDD-01 --review-report TDD-01.A_audit_report_v001.md
/doc-utest-fixer TDD-01 --review-report TDD-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-utest-audit`
- Re-run `doc-utest-audit` after fixes to verify closure

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Remediates unit-focused TDD test cases (no UTEST/TSPEC artifact or numeric code); 4-segment IDs (`TDD.NN.04.xxxx`, `type: unit`); `.A_` preferred / `.R_` legacy precedence retained. |
| 1.0 | 2026-02-27 | Initial unit-test fixer (pre-migration legacy layer). |
