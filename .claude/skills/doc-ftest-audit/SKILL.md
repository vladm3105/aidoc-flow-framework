---
name: doc-ftest-audit
description: Unified FTEST audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ftest-audit
  custom_fields:
    layer: 10
    artifact_type: FTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [FTEST]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks FTEST-MVP-TEMPLATE schema_version"
---

# doc-ftest-audit

## Purpose

Run a single FTEST audit workflow:
1. `doc-ftest-validator`
2. `doc-ftest-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `FTEST-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-ftest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

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
- Run `doc-ftest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-ftest-audit docs/10_TSPEC/FTEST/FTEST-01_scope/FTEST-01_scope.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial FTEST audit wrapper with validator->reviewer orchestration and `.A_` preferred fixer contract |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

