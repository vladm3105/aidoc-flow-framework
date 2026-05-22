---
name: doc-itest-validator
description: Validate integration-focused TDD (Layer 7) test cases against the TDD template structure, traceability, and contract requirements
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
    - itest
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: integration
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD]
    downstream_artifacts: [Audit, Fix]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-itest-validator

## Purpose

Validate integration-focused **TDD (Layer 7)** test cases for structure,
traceability, behavior-contract, and interaction requirements.

This skill is a **TDD (Layer 7) specialization** (integration-test focus); it
operates on TDD documents authored against the single canonical artifact
contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

---

## Validation Reference

- `framework/layers/07_TDD/TDD-TEMPLATE.yaml` — the single TDD artifact contract
- `framework/layers/07_TDD/README.md` — layer overview
- `framework/governance/ID_NAMING_STANDARDS.md` — element ID and tag formats

---

## Validation Checklist

The framework is spec-only — there are no validation scripts to run. This skill
*is* the validator: apply the declarative checks below, with
`framework/layers/07_TDD/README.md` and `framework/governance/` as authority.

1. TDD document follows the 7-section template, in order
2. Integration test cases present in Section 4 (`integration_tests`)
3. Test-case element IDs use the 4-segment `TDD.NN.04.xxxx` form
4. Each integration case carries `type: integration`
5. Required cumulative upstream tags present (`@brd` through `@spec`)
6. The `@tdd: TDD-NN` self-tag present (document-level dash form)
7. Integration-case fields populated (`contract`, `setup`, `action`, `expected_state`, `error_paths`)
8. Behavior-contract (`@spec: SPEC-NN`) mappings present
9. Mermaid sequence diagrams exist for complex interactions
10. IPLAN-Ready claim present and `>=90/100`

---

## Integration

- Invoked by: `doc-itest`, `doc-itest-autopilot`, `doc-itest-audit`
- Feeds into: `doc-itest-audit`, `doc-itest-fixer`

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) integration-focus validator over `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; element IDs are 4-segment `TDD.NN.04.xxxx` with `type: integration`; behavior-contract checks via `@spec: SPEC-NN`. Dead validation-script references removed (framework is spec-only). |
| 1.0 | 2026-02-27 | Initial validator with schema/structure/tag/contract checks (pre-migration legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan (IPLAN) scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
