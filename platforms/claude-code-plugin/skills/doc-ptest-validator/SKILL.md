---
name: doc-ptest-validator
description: Validate performance-focused TDD (Layer 7) test cases against the framework TDD contract and performance-threshold requirements
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-performance-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: performance
    deliverable_type: code
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

# doc-ptest-validator

## Purpose

Validate performance-focused **TDD (Layer 7)** test cases for structure,
traceability, and performance-threshold requirements.

This skill is a **TDD (Layer 7) specialization** for the performance-test
focus. It validates against the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`) and does **not**
define a separate artifact, template, or element-code. The plugin skill *is*
the validator — there is no external validation script.

---

## Validation Contract Reference

- Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`
- Layer: 7 (TDD — performance focus)
- Artifact Type: TDD
- Deliverable Type: code

---

## Validation Checklist

1. File follows TDD naming (`TDD-NN_{slug}.yaml`) and YAML parses
2. All 7 TDD template sections present and ordered
3. Performance test cases use the 4-segment element ID `TDD.NN.04.xxxx`
4. Required cumulative tags present (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@spec`) + `@tdd` self-tag
5. SPEC/ADR performance constraints referenced (`@spec`, `@adr`)
6. Performance scenario categories represented (Load / Stress / Endurance / Spike)
7. Load scenario tables present; thresholds measurable and `@threshold:`-tagged
8. IPLAN-Ready Score claim present and threshold-aligned (`>=90/100`)

---

## Validation Procedure (declarative)

This skill performs validation directly — there is no external script. Walk the
checklist above against the document, then:

1. Confirm the filename and YAML parse cleanly.
2. Confirm all 7 template sections are present and ordered.
3. Confirm performance test-case IDs and scenario labels are valid.
4. Confirm load scenarios and `@threshold:`-tagged measurable targets are present.
5. Confirm all upstream tags resolve to existing documents.

For the authoritative rules, consult `framework/layers/07_TDD/README.md`,
`framework/layers/07_TDD/TDD-TEMPLATE.yaml`,
`framework/governance/THRESHOLD_NAMING_RULES.md`, and `framework/governance/`.

---

## Integration

- Invoked by: `doc-ptest`, `doc-ptest-autopilot`, `doc-ptest-audit`
- Feeds into: `doc-ptest-audit`, `doc-ptest-fixer`

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`
- Governance / ID & naming standards: `framework/governance/`
- Parent TDD skill: `../doc-tdd/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) performance-test validator over the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; checklist recast to 4-segment IDs, performance scenarios, and `@threshold:` tags; external validation scripts removed (framework is spec-only — this skill is the validator). |
| 1.0 | 2026-02-27 | Initial PTEST validator (pre-migration, legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
