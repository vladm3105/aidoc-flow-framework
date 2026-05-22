---
name: doc-itest-fixer
description: Apply automated and guided fixes for integration-focused TDD (Layer 7) findings from audit/review reports
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
    - itest-fix
  custom_fields:
    layer: 7
    artifact_type: TDD
    test_focus: integration
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [TDD, Audit Report, Review Report]
    downstream_artifacts: [Fixed TDD, Fix Report]
    version: "2.0"
    last_updated: "2026-05-22"
  versioning_policy: "tracks TDD-TEMPLATE schema_version"
---

# doc-itest-fixer

## Purpose

Apply fixes for integration-focused **TDD (Layer 7)** issues identified by the
validator/reviewer workflows, with deterministic source-report precedence.

This skill is a **TDD (Layer 7) specialization** (integration-test focus); it
operates on TDD documents authored against the single canonical artifact
contract `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

---

## Input Contract

Preferred:
- `TDD-NN.A_audit_report_vNNN.md`

Legacy-compatible:
- `TDD-NN.R_review_report_vNNN.md`

Selection precedence:
1. Newest timestamp/version.
2. If tied, prefer `.A_audit_report_vNNN.md` over `.R_review_report_vNNN.md`.

---

## Fix Categories

- Missing required sections (the 7-section TDD template)
- Missing/invalid upstream tags (`@brd` through `@spec`, plus the `@tdd` self-tag)
- Behavior-contract (`@spec: SPEC-NN`) mapping completeness
- Missing integration-case fields (`contract`, `setup`, `action`, `expected_state`, `error_paths`)
- Missing Mermaid sequence diagram for complex interactions
- Element-ID corrections to the 4-segment `TDD.NN.04.xxxx` form (`type: integration`)
- Traceability and cross-reference consistency
- Naming/path corrections for nested-folder compliance

---

## Outputs

- Fixed TDD document(s)
- `TDD-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-itest-fixer TDD-01
/doc-itest-fixer TDD-01 --review-report TDD-01.A_audit_report_v001.md
/doc-itest-fixer TDD-01 --review-report TDD-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-itest-audit`
- Re-run `doc-itest-audit` after fixes to verify closure

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) integration-focus fixer over `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; reports and fixes keyed to `TDD-NN`; element IDs corrected to 4-segment `TDD.NN.04.xxxx`. |
| 1.0 | 2026-02-27 | Initial fixer with deterministic `.A_` preferred / `.R_` legacy precedence (pre-migration legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan (IPLAN) scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
