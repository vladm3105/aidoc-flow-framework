---
name: doc-iplan-audit
description: Unified IPLAN audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
    - quality-assurance
    - iplan-audit
    - shared-architecture
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [IPLAN]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks IPLAN-TEMPLATE schema_version"
---

# doc-iplan-audit

## Purpose

Run a single IPLAN audit workflow:
1. `doc-iplan-validator`
2. `doc-iplan-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `IPLAN-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-iplan-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score >= 90 AND no blocking/manual-required issues
- FAIL: validator FAIL OR reviewer score < 90 OR blocking/manual-required issues present

IPLAN gate policy:
- Missing structural compliance, missing implementation-contract essentials, broken traceability, test-first ordering violations, or unresolved manual-required findings cannot auto-pass.

---

## Combined Report Sections

1. Summary
2. Score Calculation
3. Validator Findings
4. Reviewer Findings
5. Coverage Findings
6. IPLAN Gate Findings
7. Fix Queue (`auto_fixable`, `manual_required`, `blocked`)
8. Recommended Next Step

---

## Handoff Rule

If remediation needed:
- Run `doc-iplan-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-iplan-audit docs/08_IPLAN/IPLAN-01_scope/IPLAN-01_scope.yaml
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | Migrated to the 8-layer model: audits IPLAN (Layer 8) documents; orchestrates `doc-iplan-validator` -> `doc-iplan-reviewer`; combined `.A_` report contract for `doc-iplan-fixer` handoff |
| 1.0 | 2026-02-27 | Initial audit wrapper with validator->reviewer orchestration and combined `.A_` report contract for fixer handoff |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.
