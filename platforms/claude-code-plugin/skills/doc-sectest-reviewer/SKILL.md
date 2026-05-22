---
name: doc-sectest-reviewer
description: Review security-focused TDD (Layer 7) test cases for content quality, threat/control coverage, and safety compliance
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
    downstream_artifacts: []
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-sectest-reviewer

## Purpose

Perform semantic quality review for security-focused **TDD (Layer 7)** test
cases beyond structural validation.

This skill is a **TDD (Layer 7) specialization** focused on the security-test
content of TDD. It does **not** define a separate artifact, template, or
element-code; the canonical artifact contract is
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`). Security tests
are the `security` `type` of TDD test cases.

**Layer**: 7 (TDD — security-test focus)

**Upstream**: TDD (from `doc-sectest-autopilot`)

**Downstream**: None (final QA gate before IPLAN generation)

---

## Review Scope

1. SPEC and ADR alignment for security requirements (`@spec`, `@adr`)
2. Category completeness (AuthN, AuthZ, Input, Crypto, Config, Session)
3. Threat scenario realism and security control completeness
4. Compliance mapping completeness (for example OWASP/CWE/NIST where documented)
5. Safety constraint presence and unsafe-guidance exclusion
6. Traceability completeness and consistency (`@brd`..`@spec` plus `@tdd`)

---

## Safety Policy

- Security tests must run in isolated environments only.
- Never run security tests against production systems.
- Any guidance enabling operational misuse, production-targeted testing, or
  exploit execution steps is `manual_required` or `blocked`.

---

## Output Contract

Reviewer-native output:
- `TDD-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-sectest-audit` may emit `TDD-NN.A_audit_report_vNNN.md` as preferred
  fixer input.

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

- `doc-sectest-validator`
- `doc-sectest-fixer`
- `doc-sectest-audit`
- `doc-sectest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a security-test-focused TDD reviewer referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate SECTEST/TSPEC artifact or numeric code; `type: security` cases). Report contract retargeted to `TDD-NN.A_/.R_`. Safety policy and threshold-based pass gate preserved. |
| 1.0 | 2026-02-27 | Initial security-test reviewer (pre-migration legacy layer). |

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as valid source mode and verify intent
  preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as
  blocking issues requiring clarification.
