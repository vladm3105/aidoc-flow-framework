---
name: doc-stest-audit
description: Unified smoke-focused TDD (Layer 7) audit wrapper that runs validator then reviewer and emits a combined report for fixer workflows
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
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-stest-audit

## Purpose

Run a single audit workflow for **smoke-focused TDD (Layer 7)** test cases:

1. `doc-stest-validator`
2. `doc-stest-reviewer`

Then emit a combined fixer-ready report.

This skill is a **TDD (Layer 7) specialization**. It audits TDD documents whose
test cases carry a smoke / deployment critical-path focus; it does **not**
define a separate artifact, template, or element-code. The canonical artifact
contract is `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

**Layer**: 7 (TDD — smoke focus)

---

## Output Contract

Primary output:
- `TDD-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-stest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score = 100 AND no blocking/manual-required issues
- FAIL: validator FAIL OR reviewer score < 100 OR blocking/manual-required issues present

Deployment-gate policy:
- Timeout budget violations, missing rollback procedures, missing 100%-gate markers, or non-binary pass/fail criteria are `manual_required` or `blocked` and cannot auto-pass.

---

## Combined Report Sections

1. Summary
2. Score Calculation
3. Validator Findings
4. Reviewer Findings
5. Coverage Findings
6. Deployment Gate Findings
7. Fix Queue (`auto_fixable`, `manual_required`, `blocked`)
8. Recommended Next Step

---

## Handoff Rule

If remediation needed:
- Run `doc-stest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-stest-audit docs/07_TDD/TDD-01_deploy_smoke.yaml
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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) smoke-focus audit wrapper over `TDD-NN` documents; dropped the legacy smoke-test subtype identity, legacy layer framing, and legacy flow paths. References `framework/layers/07_TDD/TDD-TEMPLATE.yaml`. |
| 1.0 | 2026-02-27 | Initial smoke-test audit wrapper (pre-migration). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback reference paths.
