---
name: doc-sectest-fixer
description: Apply automated and guided fixes to security-focused TDD (Layer 7) test cases from audit/review reports
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
    upstream_artifacts: [TDD, Audit Report, Review Report]
    downstream_artifacts: [Fixed TDD, Fix Report]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-sectest-fixer

## Purpose

Apply fixes to security-focused **TDD (Layer 7)** test cases identified by the
validator/reviewer workflows, with deterministic source-report precedence.

This skill is a **TDD (Layer 7) specialization** operating on the security-test
focus of TDD. It does **not** define a separate artifact, template, or
element-code; the canonical artifact contract is
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`). Security tests
are the `security` `type` of TDD test cases.

**Layer**: 7 (TDD — security-test focus)

**Upstream**: TDD document, Audit Report (`TDD-NN.A_audit_report_vNNN.md`),
Review Report (`TDD-NN.R_review_report_vNNN.md`)

**Downstream**: Fixed TDD, Fix Report (`TDD-NN.F_fix_report_vNNN.md`)

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

- Missing required template sections (7-section TDD contract)
- Missing/invalid security test-case attributes (`type: security`, `threat`,
  `expected_result`)
- Missing security categories, threat scenarios, or controls
- Missing/weak safety constraints or production-targeting language
- Missing/invalid element IDs (`TDD.NN.04.xxxx`)
- Traceability and cross-reference consistency (`@brd`..`@spec`, `@tdd`)
- Naming/path corrections for TDD-document compliance

---

## Outputs

- Fixed TDD document(s)
- `TDD-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-sectest-fixer TDD-01
/doc-sectest-fixer TDD-01 --review-report TDD-01.A_audit_report_v001.md
/doc-sectest-fixer TDD-01 --review-report TDD-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-sectest-audit`
- Re-run `doc-sectest-audit` after fixes to verify closure

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a security-test-focused TDD fixer referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate SECTEST/TSPEC artifact or numeric code; `type: security` cases). Report contract retargeted to `TDD-NN.A_/.R_/.F_`. Safety remediation checks preserved. |
| 1.0 | 2026-02-27 | Initial security-test fixer (pre-migration legacy layer). |

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as valid source mode and verify intent
  preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as
  blocking issues requiring clarification.
