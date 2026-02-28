---
name: doc-utest-audit
description: Unified UTEST audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - utest-audit
  custom_fields:
    layer: 10
    artifact_type: UTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [UTEST]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks UTEST-MVP-TEMPLATE schema_version"
---

# doc-utest-audit

## Purpose

Run a single UTEST audit workflow:
1. `doc-utest-validator`
2. `doc-utest-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `UTEST-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-utest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score >= 90 AND no blocking/manual-required issues
- FAIL: validator FAIL OR reviewer score < 90 OR blocking/manual-required issues present

Unit-test gate policy:
- Missing category coverage, missing Input/Output tables, REQ coverage below 90%, or missing pseudocode for complex logic are `manual_required` or `blocked` and cannot auto-pass.

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
- Run `doc-utest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-utest-audit docs/10_TSPEC/UTEST/UTEST-01_scope/UTEST-01_scope.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial UTEST audit wrapper with validator->reviewer orchestration and 90%-gate unit-test pass contract |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

