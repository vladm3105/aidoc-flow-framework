---
name: doc-ptest-audit
description: Unified PTEST audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ptest-audit
  custom_fields:
    layer: 10
    artifact_type: PTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [PTEST]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks PTEST-MVP-TEMPLATE schema_version"
---

# doc-ptest-audit

## Purpose

Run a single PTEST audit workflow:
1. `doc-ptest-validator`
2. `doc-ptest-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `PTEST-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-ptest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

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
- Run `doc-ptest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-ptest-audit docs/10_TSPEC/PTEST/PTEST-01_scope/PTEST-01_scope.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial PTEST audit wrapper with validator->reviewer orchestration and `.A_` preferred fixer contract |
