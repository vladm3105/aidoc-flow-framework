---
name: doc-ftest-validator
description: Validate functional-focused TDD (Layer 7) test cases against the framework TDD contract - structure, traceability, and quality-attribute thresholds
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-functional-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    tdd_focus: functional
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

# doc-ftest-validator

## Purpose

Validate functional-focused **TDD (Layer 7)** test cases for structure,
traceability, and quality-attribute threshold constraints.

This skill is a **TDD (Layer 7) specialization** for the functional-test focus.
It validates against the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`) and does **not**
define a separate artifact, template, or element-code. The plugin skill *is* the
validator — there is no external validation script.

---

## Validation Contract Reference

- Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- ID & naming standards: `framework/governance/ID_NAMING_STANDARDS.md`

---

## Validation Checklist

1. File location rule (`docs/07_TDD/TDD-NN_{slug}.yaml`)
2. The single 7-section TDD template is present and ordered
3. Functional test-case element IDs use `TDD.NN.04.xxxx` (4-segment)
4. Each functional case carries a valid `type` (`e2e` / `security`)
5. Required cumulative upstream tags present (`@brd`..`@spec`; no SYS)
6. Functional cases trace to EARS / BDD / SPEC; quality-attribute thresholds present (Section 5)
7. IPLAN-Ready score claim present and threshold-aligned (>=90/100)

---

## Validation Procedure (declarative)

This skill performs validation directly — there is no external script. Walk the
checklist above against the document, then:

1. Confirm the file location and YAML parse cleanly.
2. Confirm all 7 template sections are present and ordered.
3. Confirm functional cases (Section 4) carry `TDD.NN.04.xxxx` IDs and a valid `type`.
4. Confirm quality-attribute thresholds are set in Section 5.
5. Confirm all upstream tags resolve to existing documents (no SYS).
6. Confirm the IPLAN-Ready score meets the target.

For the authoritative rules, consult `framework/layers/07_TDD/README.md`,
`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, and `framework/governance/`.

---

## Integration

- Invoked by: `doc-ftest`, `doc-ftest-autopilot`, `doc-ftest-audit`
- Feeds into: `doc-ftest-audit`, `doc-ftest-fixer`

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Validates functional-focused TDD (Layer 7) documents against the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; checklist retargeted to `TDD.NN.04.xxxx` IDs, `e2e`/`security` case types, EARS/BDD/SPEC traceability (no SYS coverage), Section 5 thresholds; removed dead validation-script references — this skill is now the declarative validator (framework is spec-only). |
| 1.0 | 2026-02-27 | Initial functional-test validator (pre-migration legacy model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
