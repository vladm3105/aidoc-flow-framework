---
name: doc-itest-audit
description: Unified integration-focused TDD audit wrapper that runs validator then reviewer and emits a combined fixer-ready report
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
    - itest-audit
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: integration
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

# doc-itest-audit

## Purpose

Run a single audit workflow over an integration-focused **TDD (Layer 7)**
document:
1. `doc-itest-validator`
2. `doc-itest-reviewer`

Then emit a combined fixer-ready report.

This skill is a **TDD (Layer 7) specialization** (integration-test focus); it
operates on TDD documents authored against the single canonical artifact
contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

---

## Output Contract

Primary output:
- `TDD-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-itest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score >= threshold AND no blocking/manual-required issues
- FAIL: validator FAIL OR reviewer score below threshold OR blocking/manual-required issues present

---

## Combined Report Sections

1. Summary
2. Score Calculation
3. Validator Findings
4. Reviewer Findings
5. Coverage Findings
6. Fix Queue (`auto_fixable`, `manual_required`, `blocked`)
7. Recommended Next Step

---

## Handoff Rule

If remediation needed:
- Run `doc-itest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-itest-audit docs/07_TDD/TDD-01_scope/TDD-01_scope.yaml
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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) integration-focus audit wrapper over `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; reports keyed to `TDD-NN`. |
| 1.0 | 2026-02-27 | Initial audit wrapper with validator->reviewer orchestration and `.A_` preferred fixer contract (pre-migration legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan (IPLAN) scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
