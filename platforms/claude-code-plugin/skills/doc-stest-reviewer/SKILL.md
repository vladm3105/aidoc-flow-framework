---
name: doc-stest-reviewer
description: Review smoke-focused TDD (Layer 7) content quality, timeout/rollback compliance, and critical-path pass/fail rigor
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-smoke-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: smoke
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

# doc-stest-reviewer

## Purpose

Perform semantic quality review for **smoke-focused TDD (Layer 7)** test cases
beyond structural validation.

This skill is a **TDD (Layer 7) specialization**. It reviews TDD documents whose
test cases carry a smoke / deployment critical-path focus; it does **not**
define a separate artifact, template, or element-code. The canonical artifact
contract is `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

**Layer**: 7 (TDD — smoke focus)

---

## Review Scope

1. Deployment critical-path coverage completeness
2. Smoke timeout budget realism and compliance (`<=300s` / max 300s)
3. Rollback / cleanup completeness for each critical-path test case
4. Binary pass/fail criteria clarity and fail-fast behavior
5. `@ears` / `@bdd` / `@spec` traceability completeness and consistency

---

## Deployment Gate Policy

- Critical-path target: 100% (`100% quality gate`).
- Every critical-path test case must declare a rollback procedure.
- Timeout budget markers must be explicit (`max 300s` or `<=300s`).
- Any missing critical deployment gate element is `manual_required` or `blocked`.

---

## Output Contract

Reviewer-native output:
- `TDD-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-stest-audit` may emit `TDD-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with the parent TDD document.

---

## Score Gate

- Pass target: score `=100`
- Manual-required findings block automated completion.

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Related Skills

- `doc-stest-validator`
- `doc-stest-fixer`
- `doc-stest-audit`
- `doc-stest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) smoke-focus reviewer over `TDD-NN` documents; dropped the legacy smoke-test subtype identity and legacy layer framing. References `framework/layers/07_TDD/TDD-TEMPLATE.yaml`. |
| 1.0 | 2026-02-27 | Initial smoke-test reviewer (pre-migration). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback reference paths.
