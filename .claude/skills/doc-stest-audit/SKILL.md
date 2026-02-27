---
name: doc-stest-audit
description: Unified STEST audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - stest-audit
  custom_fields:
    layer: 10
    artifact_type: STEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [STEST]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks STEST-MVP-TEMPLATE schema_version"
---

# doc-stest-audit

## Purpose

Run a single STEST audit workflow:
1. `doc-stest-validator`
2. `doc-stest-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `STEST-NN.A_audit_report_vNNN.md`

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
/doc-stest-audit docs/10_TSPEC/STEST/STEST-01_scope/STEST-01_scope.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial STEST audit wrapper with validator->reviewer orchestration and strict 100% deployment-gate pass contract |
