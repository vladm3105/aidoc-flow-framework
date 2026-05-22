---
name: doc-itest
description: Author TDD (Layer 7) test-case definitions with an integration-test focus - component interactions, contract validation, and sequence-flow verification
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-integration-helper
    - shared-architecture
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: integration
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN, Code]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-itest

## Purpose

Author **TDD (Layer 7) test-case definitions with an integration-test focus** —
component interactions, behavior-contract compliance, sequence-flow validation,
and integration-level data-flow checks.

This skill is a **TDD (Layer 7) specialization**. It authors TDD documents whose
test cases concentrate on the `integration` test type, and it references the
single canonical artifact contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
(see `../doc-tdd/`); it does **not** define a separate artifact, template, or
element-code.

**Layer**: 7 (TDD — integration-test focus)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4),
ADR (Layer 5), SPEC (Layer 6)

**Downstream**: IPLAN (Layer 8), Code

---

## Canonical References

Before authoring integration-focused TDD test cases, read:

1. `framework/layers/07_TDD/TDD-TEMPLATE.yaml` — the single TDD artifact contract
2. `framework/layers/07_TDD/README.md` — layer overview
3. `framework/governance/ID_NAMING_STANDARDS.md` — element ID and tag formats
4. `../doc-tdd/SKILL.md` — the parent TDD authoring skill
5. `../doc-flow/SHARED_CONTENT.md` — shared standards

---

## When to Use

Use `doc-itest` when:
- You are authoring or editing TDD test cases focused on **integration**.
- Behavior-contract checks (`@spec: SPEC-NN`) and component-interaction coverage
  are the primary objective.
- Sequence/data-flow verification across components is the core focus.

Use `../doc-tdd/` directly when:
- A full TDD document spanning all test types (unit/integration/e2e/security)
  is required.
- Cross-type test-pyramid balancing is the primary objective.

---

## Integration-Focused TDD Contract

### Required Structure

The integration focus lives inside the single TDD template's 7 sections
(`framework/layers/07_TDD/TDD-TEMPLATE.yaml`):

1. Document Control
2. Test Pyramid (emphasize the integration band)
3. BDD Scenario to Test Mapping
4. Test Case Definitions (the `integration_tests` cases are primary here)
5. Test Thresholds
6. TDD Execution Order (Red → Green → Refactor)
7. Traceability

Integration test cases (Section 4 `integration_tests`) carry `contract`,
`setup`, `action`, `expected_state`, and `error_paths` fields — this is where
the legacy contract-compliance matrix and sequence-flow checks are recast as
TDD test-case content, not as a separate ITEST artifact.

### Required Tags

- Cumulative Layer-7 upstream tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`,
  `@spec` (SPEC referenced document-level as `SPEC-NN`).
- The `@tdd: TDD-NN` self-tag (document-level dash form).

### Element IDs

- Test cases use the 4-segment element ID `TDD.NN.04.xxxx` (test cases live in
  Section 4); set each case's `type: integration`.
- Do **not** use legacy `TSPEC.NN.41.SS` codes or any numeric subtype code.

### Threshold and Coverage

- IPLAN-Ready threshold: `>=90/100`.
- Integration coverage target: `>=85%` with contract validation passing
  (per the TDD template thresholds).

### Folder Rule

- `docs/07_TDD/TDD-NN_{slug}/TDD-NN_{slug}.yaml` (or flat
  `docs/07_TDD/TDD-NN_{slug}.yaml` per the TDD layer convention).

### Diagram Rule

- Include Mermaid sequence diagrams for complex interactions (text-based
  diagrams are prohibited; see the `mermaid-gen` skill).

---

## Validation

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator: apply the declarative checklist below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

- [ ] TDD document follows the 7-section template
- [ ] Integration test cases present in Section 4 (`integration_tests`)
- [ ] Each test case uses `TDD.NN.04.xxxx` and `type: integration`
- [ ] `contract`, `setup`, `action`, `expected_state`, `error_paths` populated
- [ ] Behavior-contract (`@spec: SPEC-NN`) mappings are explicit
- [ ] Sequence/data-flow checks represented where interactions are complex
- [ ] Cumulative upstream tags (@brd through @spec) plus the @tdd self-tag
- [ ] IPLAN-Ready Score `>=90/100`

---

## Output Quality Gate

- No schema/structure blockers against the TDD template.
- Integration test cases are complete (inputs, expected state, error paths).
- Behavior-contract mappings are explicit.
- Sequence/data-flow checks are represented where interactions are complex.
- Traceability includes the required cumulative tags.

---

## Related Skills

- `doc-itest-autopilot`
- `doc-itest-validator`
- `doc-itest-reviewer`
- `doc-itest-fixer`
- `doc-itest-audit`
- `../doc-tdd/` (parent TDD authoring skill — full-spectrum test cases)

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) integration-test specialization referencing the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no separate ITEST/TSPEC artifact, template, or numeric subtype code). Documents are `TDD-NN`; test cases use 4-segment `TDD.NN.04.xxxx` with `type: integration`. Upstream BRD,PRD,EARS,BDD,ADR,SPEC; downstream IPLAN,Code. Dead validation-script references removed (framework is spec-only). |
| 1.0 | 2026-02-27 | Initial integration-test authoring skill (pre-migration legacy 12-layer model). |
