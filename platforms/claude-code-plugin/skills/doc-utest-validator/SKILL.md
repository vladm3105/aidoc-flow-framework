---
name: doc-utest-validator
description: Validate unit-focused TDD (Layer 7) test cases against the framework TDD contract
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-unit-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: unit
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: [Audit, Fix]
    version: "2.0"
    last_updated: "2026-05-22"
---

# doc-utest-validator

Validate unit-focused **TDD (Layer 7)** test cases against the framework TDD
contract.

This skill is a **TDD (Layer 7) specialization** for the unit-test focus of TDD.
It validates against the single canonical artifact contract and does **not**
define a separate artifact, template, or element-code. The plugin skill *is* the
validator — there is no external validation script.

## Activation

Invoke when the user requests validation of unit-focused TDD test cases, or
after creating/modifying such an artifact.

## Validation Contract Reference

- Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Layer: 7 (TDD — unit-test focus)
- Artifact Type: TDD

## Validation Checklist

1. Document location: `docs/07_TDD/TDD-NN_{slug}.yaml`
2. TDD template sections present and ordered
3. Unit test cases use element IDs `TDD.NN.04.xxxx` with `type: unit`
4. Required cumulative tags present (`@brd` .. `@spec`)
5. Self tag present (`@tdd: TDD-NN`)
6. IPLAN-Ready score markers present (`Target: >=90`)
7. Unit coverage markers present (`Coverage: >=90%`)
8. Unit cases cover logic, state, validation, and edge conditions
9. Inputs and expected outputs present for each unit case
10. Edge cases documented for complex unit logic

## Validation Procedure (declarative)

This skill performs validation directly — there is no external script. Walk the
checklist above against the document, then:

1. Confirm the file location and YAML parse cleanly.
2. Confirm unit cases carry `TDD.NN.04.xxxx` IDs and `type: unit`.
3. Confirm logic/state/validation/edge conditions are represented.
4. Confirm all upstream tags resolve to existing documents.
5. Compute the unit coverage and IPLAN-Ready scores; flag any below threshold.

For the authoritative rules, consult `framework/layers/07_TDD/README.md`,
`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, and `framework/governance/`.

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| TDD-E001 | Error | Missing required upstream tag |
| TDD-E002 | Error | Unit case missing inputs/expected outputs |
| TDD-E003 | Error | Missing unit category coverage (logic/state/validation/edge) |
| TDD-W001 | Warning | Edge cases for complex logic incomplete |
| TDD-W002 | Warning | Unit coverage or IPLAN-Ready score below threshold |

## Integration

- Invoked by: `doc-utest`, `doc-utest-autopilot`, `doc-utest-audit`
- Feeds into: `doc-utest-audit`, `doc-utest-fixer`

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer TDD model (Layer 7). Validates unit-focused TDD test cases against `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (no UTEST/TSPEC schema, numeric code, or external script). 4-segment IDs (`TDD.NN.04.xxxx`, `type: unit`); upstream BRD,PRD,EARS,BDD,ADR,SPEC. |
| 1.0 | 2026-02-27 | Initial unit-test validator (pre-migration legacy layer). |
