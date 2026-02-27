---
name: doc-sectest-reviewer
description: Review SECTEST content quality, threat/control coverage, and safety compliance for security test specifications
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - sectest-review
  custom_fields:
    layer: 10
    artifact_type: SECTEST
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SECTEST]
    downstream_artifacts: []
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SECTEST-MVP-TEMPLATE schema_version"
---

# doc-sectest-reviewer

## Purpose

Perform semantic quality review for SECTEST artifacts beyond structural validation.

---

## Review Scope

1. SEC and SPEC alignment for security requirements
2. Category completeness (`[AuthN]`, `[AuthZ]`, `[Input]`, `[Crypto]`, `[Config]`, `[Session]`)
3. Threat scenario realism and security control completeness
4. Compliance mapping completeness (for example OWASP/CWE/NIST where documented)
5. Safety constraint presence and unsafe-guidance exclusion
6. Traceability completeness and consistency

---

## Safety Policy

- Security tests must run in isolated environments only.
- Never run security tests against production systems.
- Any guidance enabling operational misuse, production-targeted testing, or exploit execution steps is `manual_required` or `blocked`.

---

## Output Contract

Reviewer-native output:
- `SECTEST-NN.R_review_report_vNNN.md`

Audit-wrapper compatibility:
- `doc-sectest-audit` may emit `SECTEST-NN.A_audit_report_vNNN.md` as preferred fixer input.

All reports are colocated with parent SECTEST file.

---

## Score Gate

- Pass target: score `>=90`
- Manual-required findings block automated completion.

---

## Related Skills

- `doc-sectest-validator`
- `doc-sectest-fixer`
- `doc-sectest-audit`
- `doc-sectest-autopilot`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial SECTEST reviewer with audit-compatible report contract, safety policy, and threshold-based pass gate |
