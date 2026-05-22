---
name: doc-utest-audit
description: Unified unit-focused TDD (Layer 7) audit wrapper that runs validator then reviewer and emits a combined fixer-ready report
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
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-utest-audit

## Purpose

Run a single unit-focused **TDD (Layer 7)** audit workflow:
1. `doc-utest-validator`
2. `doc-utest-reviewer`

Then emit a combined fixer-ready report.

This skill is a **TDD (Layer 7) specialization** for the unit-test focus of TDD.
It audits against the single canonical artifact contract
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, see `../doc-tdd/`) and does **not**
define a separate artifact, template, or element-code.

**Layer**: 7 (TDD — unit-test focus)

---

## Output Contract

Primary output:
- `TDD-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-utest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score >= 90 AND no blocking/manual-required
  issues
- FAIL: validator FAIL OR reviewer score < 90 OR blocking/manual-required issues
  present

Unit-test gate policy:
- Missing category coverage (logic/state/validation/edge), missing
  inputs/expected outputs, unit coverage below 90%, or missing edge cases for
  complex logic are `manual_required` or `blocked` and cannot auto-pass.

---

## Combined Report Sections

1. Summary
2. Score Calculation
3. Validator Findings
4. Reviewer Findings
5. Coverage Findings
6. Unit-Test Gate Findings
7. Fix Queue (`auto_fixable`, `manual_required`, `blocked`)
8. Recommended Next Step

---

## Handoff Rule

If remediation needed:
- Run `doc-utest-fixer` with the newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-utest-audit docs/07_TDD/TDD-01_auth_service.yaml
```

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Audits unit-focused TDD test cases (no UTEST/TSPEC artifact or numeric code); validator->reviewer orchestration retained; report contract emits `TDD-NN.A_…`. |
| 1.0 | 2026-02-27 | Initial unit-test audit wrapper (pre-migration legacy layer). |
