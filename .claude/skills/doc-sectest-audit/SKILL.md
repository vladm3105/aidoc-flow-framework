---
name: doc-sectest-audit
description: Unified SECTEST audit wrapper that runs validator then reviewer and emits combined report for fixer workflows
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - sectest-audit
  custom_fields:
    layer: 10
    artifact_type: SECTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SECTEST]
    downstream_artifacts: [Audit Report, Fix Cycle]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SECTEST-MVP-TEMPLATE schema_version"
---

# doc-sectest-audit

## Purpose

Run a single SECTEST audit workflow:
1. `doc-sectest-validator`
2. `doc-sectest-reviewer`

Then emit a combined fixer-ready report.

---

## Output Contract

Primary output:
- `SECTEST-NN.A_audit_report_vNNN.md`

Fixer compatibility:
- `doc-sectest-fixer` accepts `.A_` (preferred) and `.R_` (legacy-compatible).

---

## Combined Status Rules

- PASS: validator PASS AND reviewer score >= threshold AND no blocking/manual-required issues
- FAIL: validator FAIL OR reviewer score below threshold OR blocking/manual-required issues present

Unsafe-guidance policy:
- Any guidance that enables operational misuse, production-targeted testing, or exploit execution steps is classified as `manual_required` or `blocked` and cannot auto-pass.

---

## Combined Report Sections

1. Summary
2. Score Calculation
3. Validator Findings
4. Reviewer Findings
5. Coverage Findings
6. Safety Findings
7. Fix Queue (`auto_fixable`, `manual_required`, `blocked`)
8. Recommended Next Step

---

## Handoff Rule

If remediation needed:
- Run `doc-sectest-fixer` with newest report.
- On timestamp/version tie, prefer `.A_` over `.R_`.

---

## Example

```bash
/doc-sectest-audit docs/10_TSPEC/SECTEST/SECTEST-01_scope/SECTEST-01_scope.md
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial SECTEST audit wrapper with validator->reviewer orchestration, unsafe-guidance blocking policy, and `.A_` preferred fixer contract |
