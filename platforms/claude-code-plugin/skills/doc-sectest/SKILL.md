---
name: doc-sectest
description: Author TDD (Layer 7) test cases with a security-test focus - threat scenarios, security controls, and vulnerability tests traced to SPEC/ADR
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-security-helper
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: security
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-sectest

## Purpose

Author **TDD (Layer 7)** test-case definitions with a **security-test focus** —
threat scenarios, security control validation, and vulnerability checks across
AuthN, AuthZ, Input, Crypto, Config, and Session concerns, traced to SPEC
component contracts and ADR security decisions. Co-owned with the
security-engineer agent.

This skill is a **TDD (Layer 7) specialization**. It authors TDD documents with
a security-test focus and references the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code. Security tests are the
`security` `type` of TDD test cases, not a distinct layer or numeric code.

**Layer**: 7 (TDD — security-test focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Canonical References

Before authoring security-focused TDD test cases, read:

1. Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
2. Layer overview: `framework/layers/07_TDD/README.md`
3. Parent TDD skill: `../doc-tdd/`
4. Governance / ID & naming standards: `framework/governance/`

---

## When to Use

Use `doc-sectest` when:
- You are authoring TDD test cases focused on **security** validation.
- `@spec` and `@adr` (security decisions) mappings are primary.
- Threat scenarios and security control validation are the core objective.

Use `../doc-tdd/` directly when:
- You need the full TDD document spanning all test types (unit, integration,
  e2e, security) rather than a security-focused authoring pass.

---

## Security-Test Focus Contract

### Required Structure

Security-focused work lives inside the single TDD document
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, 7 sections). For security cases,
emphasize:

1. Document Control (Section 1)
2. Test Pyramid — security slice (Section 2)
3. BDD Scenario to Test Mapping — `type: security` entries (Section 3)
4. Test Case Definitions — `type: security` cases (Section 4 `security_tests`)
5. Test Thresholds — security coverage gate (Section 5)
6. Traceability (Section 7)

### Element IDs

Security test cases use the 4-segment element ID `TDD.NN.04.xxxx` (test cases
live in Section 4) with a `type: security` attribute — NOT a separate numeric
code. Each case carries a `threat` reference (OWASP category / threat model)
and an `expected_result` (rejection / sanitization / error).

### Required Tags

- Cumulative Layer-7 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@spec`
  (elements use `TYPE.NN.SS.xxxx`; SPEC uses document-level `SPEC-NN`)
- Self tag: `@tdd: TDD-NN`

### Security-Test Categories and Coverage

- Recommended threat categories: AuthN, AuthZ, Input, Crypto, Config, Session.
- IPLAN-Ready score target must be `>=90`.
- Security coverage target: all authentication/authorization paths; no OWASP
  Top 10 vulnerabilities detected.

### Folder Rule

Security cases live in the parent TDD document:
- `docs/07_TDD/TDD-NN_{component_slug}.yaml`

### Safety Rule

- Security tests must run in **isolated environments only**.
- Never run security tests against production systems.

---

## Validation

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator. Apply the declarative checklist below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

- [ ] Security cases authored inside the TDD document (`TDD-NN_{slug}.yaml`)
- [ ] Each security case has a `TDD.NN.04.xxxx` ID and `type: security`
- [ ] Each security case carries a `threat` reference and `expected_result`
- [ ] Threat scenarios and security controls represented (AuthN/AuthZ/Input/
      Crypto/Config/Session)
- [ ] Security coverage threshold set (auth/authz paths; no OWASP Top 10)
- [ ] Safety constraints present (isolated environments only; never production)
- [ ] Cumulative tags `@brd` through `@spec` present, plus `@tdd` self-tag
- [ ] IPLAN-Ready score `>=90`

---

## Output Quality Gate

- No schema/structure blockers against `TDD-TEMPLATE.yaml`.
- Security-focused TDD sections present.
- `@spec` and `@adr` (and upstream) mappings are explicit.
- Threat scenarios and security controls are represented.
- Security coverage and IPLAN-Ready scores meet `>=90`/target.
- Safety warnings are present and explicit.

---

## Related Skills

- `doc-sectest-autopilot`
- `doc-sectest-validator`
- `doc-sectest-reviewer`
- `doc-sectest-fixer`
- `doc-sectest-audit`
- `../doc-tdd/` (parent TDD authoring skill — full document, all test types)

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a security-test-focused TDD specialization referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate SECTEST/TSPEC artifact, template, or numeric code). Security tests are now the `security` `type` of TDD test cases. 4-segment element IDs (`TDD.NN.04.xxxx`, `type: security`); upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN. Dead validation scripts removed in favor of this skill's declarative checklist. Safety constraints preserved. |
| 1.0 | 2026-02-27 | Initial security-test authoring skill (pre-migration legacy layer). |
