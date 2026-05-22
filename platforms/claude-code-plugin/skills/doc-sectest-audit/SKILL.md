---
name: doc-sectest-audit
description: Quality gate for security-focused TDD (Layer 7) test cases - runs validator then reviewer and emits a combined fixer-ready report
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-security-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: security
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-sectest-audit

## Purpose

Quality gate for **security-focused TDD** test cases — the security-test
specialization of TDD (Layer 7). Runs a single audit workflow:

1. `doc-sectest-validator`
2. `doc-sectest-reviewer`

Then emits a combined fixer-ready report.

This skill is a **TDD (Layer 7) specialization**. It audits TDD test cases
authored with a security focus; it does **not** define a separate artifact,
template, or element-code. The canonical artifact contract is
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

**Layer**: 7 (TDD — security-test focus)

**Upstream**: TDD document (security focus)

**Downstream**: Audit Report (`TDD-NN.A_audit_report_vNNN.md`)

---

## Output Contract

Primary output:
- `TDD-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-sectest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score >= threshold AND no blocking/manual-required issues
- FAIL: validator FAIL OR reviewer score below threshold OR blocking/manual-required issues present

Unsafe-guidance policy:
- Any guidance that enables operational misuse, production-targeted testing, or
  exploit execution steps is classified as `manual_required` or `blocked` and
  cannot auto-pass.

---

## Combined Report Sections

1. Summary
2. Score Calculation
3. Validator Findings
4. Reviewer Findings
5. Coverage Findings
6. Safety Findings
7. Fix Queue (`auto_fixable`, `manual_required`, `blocked`)
8. Recommended Next Step

---

## Handoff Rule

If remediation needed:
- Run `doc-sectest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-sectest-audit docs/07_TDD/TDD-01_auth_service.yaml
```

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a security-test-focused TDD audit wrapper over the validator->reviewer chain; references `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate SECTEST/TSPEC artifact or numeric code). Report contract retargeted to `TDD-NN.A_/.R_`. Unsafe-guidance blocking policy preserved. |
| 1.0 | 2026-02-27 | Initial security-test audit wrapper (pre-migration legacy layer). |

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as valid source mode and verify intent
  preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as
  blocking issues requiring clarification.
