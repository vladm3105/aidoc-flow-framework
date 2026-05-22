---
name: doc-sectest-validator
description: Validate security-focused TDD (Layer 7) test cases against the framework TDD contract - structure, traceability, threat/control coverage, and safety
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-security-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: security
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: [Audit, Fix]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-sectest-validator

## Purpose

Validate security-focused **TDD (Layer 7)** test cases against the framework TDD
contract — structure, traceability, threat/control coverage, and safety
requirements.

This skill is a **TDD (Layer 7) specialization** for the security-test focus of
TDD. It validates against the single canonical artifact contract and does
**not** define a separate artifact, template, or element-code. Security tests
are the `security` `type` of TDD test cases. The plugin skill *is* the
validator — there is no external validation script.

**Layer**: 7 (TDD — security-test focus)

**Upstream**: TDD document (security focus)

**Downstream**: Audit, Fix

---

## Validation Contract Reference

- Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Validation Checklist

1. Security cases authored inside the parent TDD document
   (`docs/07_TDD/TDD-NN_{component_slug}.yaml`)
2. The 7 template sections present and ordered
3. Security test-case element IDs use `TDD.NN.04.xxxx` with `type: security`
4. Required cumulative tags present (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`,
   `@spec`; elements use `TYPE.NN.SS.xxxx`, SPEC uses `SPEC-NN`)
5. Self tag present (`@tdd: TDD-NN`)
6. Recommended threat categories represented (AuthN, AuthZ, Input, Crypto,
   Config, Session)
7. Threat scenario and security-control content present (each case has a
   `threat` reference and an `expected_result`)
8. IPLAN-Ready score claim present and threshold-aligned (`>=90`)
9. Safety warning statements present and explicit (isolated environments only;
   never production)

---

## Validation Procedure (declarative)

This skill performs validation directly — there is no external script. Walk the
checklist above against the document, then:

1. Confirm the folder structure and YAML parse cleanly.
2. Confirm each security case has a `TDD.NN.04.xxxx` ID with `type: security`.
3. Confirm threat references, expected results, and security controls present.
4. Confirm all upstream tags resolve to existing documents.
5. Confirm safety constraints are present and explicit.

For the authoritative rules, consult `framework/layers/07_TDD/README.md`,
`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, and `framework/governance/`.

---

## Integration

- Invoked by: `doc-sectest`, `doc-sectest-autopilot`, `doc-sectest-audit`
- Feeds into: `doc-sectest-audit`, `doc-sectest-fixer`

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a security-test-focused TDD validator referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate SECTEST/TSPEC schema or numeric code; `type: security` cases). 4-segment element IDs (`TDD.NN.04.xxxx`); cumulative tags `@brd`..`@spec` plus `@tdd`. Dead validation scripts removed in favor of this skill's declarative checklist. Safety constraints preserved. |
| 1.0 | 2026-02-27 | Initial security-test validator (pre-migration legacy layer). |
