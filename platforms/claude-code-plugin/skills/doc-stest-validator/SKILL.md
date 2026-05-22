---
name: doc-stest-validator
description: Validate smoke-focused TDD (Layer 7) test cases against the framework TDD contract and deployment smoke-gate requirements
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - tdd-smoke-helper
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: smoke
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

# doc-stest-validator

## Purpose

Validate **smoke-focused TDD (Layer 7)** test cases for structure,
traceability, and deployment-smoke gate requirements.

This skill is a **TDD (Layer 7) specialization**. It validates against the
single canonical artifact contract and does **not** define a separate artifact,
template, or element-code. The plugin skill *is* the validator — there is no
external validation script.

**Layer**: 7 (TDD — smoke focus)

---

## Validation Contract Reference

- Canonical artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Parent TDD skill: `../doc-tdd/`

---

## Validation Checklist

1. File rule (`docs/07_TDD/TDD-NN_{slug}.yaml`); YAML parses cleanly
2. The 7 TDD template sections present and ordered
3. Smoke test-case element IDs use `TDD.NN.04.xxxx` with a `type`
   (`integration` / `e2e`)
4. Required cumulative tags present (`@brd`..`@spec`) plus the `@tdd` self-tag
5. Critical-path traceability present (`@ears`, `@bdd`, `@spec`)
6. Smoke timeout budget markers present (`max 300s` or `<=300s`)
7. 100%-gate markers present (`Target: 100%` or `100% quality gate`)
8. Rollback / cleanup requirement explicit for every critical-path case
9. Binary pass/fail criteria explicit for critical paths

---

## Validation Procedure (declarative)

The framework is spec-only — there are no scripts to run. Walk the checklist
above against the document, then confirm metadata (`document_type: tdd-document`,
`artifact_type: TDD`, `layer: 7`), structure, traceability, and the smoke-gate
constraints. For the authoritative rules, consult
`framework/layers/07_TDD/README.md`,
`framework/layers/07_TDD/TDD-TEMPLATE.yaml`, and `framework/governance/`.

---

## Integration

- Invoked by: `doc-stest`, `doc-stest-autopilot`, `doc-stest-audit`
- Feeds into: `doc-stest-audit`, `doc-stest-fixer`

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) smoke-focus validator over `TDD-NN` documents with `TDD.NN.04.xxxx` element IDs; dropped the legacy smoke-test subtype element codes, legacy layer framing, legacy flow paths, dead validation scripts, and the retired cumulative tags. References `framework/layers/07_TDD/TDD-TEMPLATE.yaml`. |
| 1.0 | 2026-02-27 | Initial smoke-test validator (pre-migration). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback reference paths.
