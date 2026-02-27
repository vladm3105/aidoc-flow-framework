---
name: doc-itest-audit
description: Unified ITEST audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - itest-audit
  custom_fields:
    layer: 10
    artifact_type: ITEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [ITEST]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks ITEST-MVP-TEMPLATE schema_version"
---

# doc-itest-audit

## Purpose

Run a single ITEST audit workflow:
1. `doc-itest-validator`
2. `doc-itest-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `ITEST-NN.A_audit_report_vNNN.md`

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
/doc-itest-audit docs/10_TSPEC/ITEST/ITEST-01_scope/ITEST-01_scope.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial ITEST audit wrapper with validator->reviewer orchestration and `.A_` preferred fixer contract |
