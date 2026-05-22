---
name: doc-utest
description: Author TDD (Layer 7) test cases with a unit-test focus - component-level logic, state, validation, and edge-case tests traced to SPEC
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-unit-helper
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: unit
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-utest

## Purpose

Author **TDD (Layer 7)** test-case definitions with a **unit-test focus** —
component-level logic, state, validation, and edge-case checks traced to SPEC
component contracts.

This skill is a **TDD (Layer 7) specialization**. It authors TDD documents with
a unit-test focus and references the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code. Unit tests are the `unit`
`type` of TDD test cases, not a distinct layer or numeric code.

**Layer**: 7 (TDD — unit-test focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Canonical References

Before authoring unit-focused TDD test cases, read:

1. Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
2. Layer overview: `framework/layers/07_TDD/README.md`
3. Parent TDD skill: `../doc-tdd/`
4. Governance / ID & naming standards: `framework/governance/`

---

## When to Use

Use `doc-utest` when:
- You are authoring TDD test cases focused on **unit-level** validation.
- `@spec` (and upstream `@ears`/`@bdd`) mappings are primary.
- Component-level logic, state, validation, and edge-case checks are the core
  objective.

Use `../doc-tdd/` directly when:
- You need the full TDD document spanning all test types (unit, integration,
  e2e, security) rather than a unit-focused authoring pass.

---

## Unit-Test Focus Contract

### Required Structure

Unit-focused work lives inside the single TDD document
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, 7 sections). For unit cases,
emphasize:

1. Document Control (Section 1)
2. Test Pyramid — unit slice (Section 2)
3. BDD Scenario to Test Mapping — `type: unit` entries (Section 3)
4. Test Case Definitions — `type: unit` cases (Section 4)
5. Test Thresholds — unit coverage gate (Section 5)
6. Traceability (Section 7)

### Element IDs

Unit test cases use the 4-segment element ID `TDD.NN.04.xxxx` (test cases live
in Section 4) with a `type: unit` attribute — NOT a separate numeric code.

### Required Tags

- Cumulative Layer-7 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@spec`
  (elements use `TYPE.NN.SS.xxxx`; SPEC uses document-level `SPEC-NN`)
- Self tag: `@tdd: TDD-NN`

### Unit-Test Gate Requirements

- IPLAN-Ready score target must be `>=90`.
- Unit coverage target must be `>=90%`.
- Unit cases must cover logic, state, validation, and edge conditions.
- Every test case must include concrete inputs and expected outputs.
- Complex test logic must document edge cases.

### Folder Rule

Unit cases live in the parent TDD document:
- `docs/07_TDD/TDD-NN_{component_slug}.yaml`

---

## Validation

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator. Apply the declarative checklist below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

- [ ] Unit cases authored inside the TDD document (`TDD-NN_{slug}.yaml`)
- [ ] Each unit case has a `TDD.NN.04.xxxx` ID and `type: unit`
- [ ] Inputs and expected outputs present for every unit case
- [ ] Edge cases documented for complex logic
- [ ] Logic / state / validation / edge conditions all represented
- [ ] Unit coverage threshold set (`>=90%`)
- [ ] Cumulative tags `@brd` through `@spec` present, plus `@tdd` self-tag
- [ ] IPLAN-Ready score `>=90`

---

## Output Quality Gate

- No schema/structure blockers against `TDD-TEMPLATE.yaml`.
- Unit-focused TDD sections present.
- `@spec` and upstream mappings are explicit.
- Unit coverage and IPLAN-Ready scores meet `>=90`/`>=90%` targets.
- Logic, state, validation, and edge conditions are represented.
- Inputs/expected outputs documented for each unit case.

---

## Related Skills

- `doc-utest-autopilot`
- `doc-utest-validator`
- `doc-utest-reviewer`
- `doc-utest-fixer`
- `doc-utest-audit`
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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Repositioned as a unit-test-focused TDD specialization referencing `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate UTEST/TSPEC artifact, template, or numeric code). 4-segment element IDs (`TDD.NN.04.xxxx`, `type: unit`); upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN. Dead validation scripts removed in favor of this skill's declarative checklist. |
| 1.0 | 2026-02-27 | Initial unit-test authoring skill (pre-migration legacy layer). |
