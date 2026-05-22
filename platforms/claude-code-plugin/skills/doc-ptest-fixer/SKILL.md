---
name: doc-ptest-fixer
description: Apply automated and guided fixes for performance-focused TDD (Layer 7) findings from audit/review reports
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

# doc-ptest-fixer

## Purpose

Apply fixes for performance-focused **TDD (Layer 7)** issues identified by
validator/reviewer workflows, with deterministic source-report precedence.

This skill is a **TDD (Layer 7) specialization** for the performance-test
focus. It fixes TDD documents against the single canonical artifact contract
`framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`); it does **not**
define a separate artifact, template, or element-code.

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

- Missing required template sections (7-section TDD contract)
- Missing/invalid upstream tags (`@spec`, `@adr` performance constraints)
- Missing performance scenario categories (Load/Stress/Endurance/Spike) or load scenario tables
- Non-measurable threshold definitions; missing `@threshold:` tags
- Incomplete `execution_profile` for complex scenarios
- Invalid element IDs (must be `TDD.NN.04.xxxx`)
- Traceability and cross-reference consistency

---

## Outputs

- Fixed TDD document(s)
- `TDD-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-ptest-fixer TDD-01
/doc-ptest-fixer TDD-01 --review-report TDD-01.A_audit_report_v001.md
/doc-ptest-fixer TDD-01 --review-report TDD-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-ptest-audit`
- Re-run `doc-ptest-audit` after fixes to verify closure

---

## References

- Canonical TDD artifact contract: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- Layer overview: `framework/layers/07_TDD/README.md`
- Performance threshold rules: `framework/governance/THRESHOLD_NAMING_RULES.md`
- Parent TDD skill: `../doc-tdd/`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model. Repositioned as a TDD (Layer 7) performance-test fixer over the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; fix categories recast to TDD/performance content and 4-segment IDs; report contract `TDD-NN.F_…`. |
| 1.0 | 2026-02-27 | Initial PTEST fixer (pre-migration, legacy 12-layer model). |

## Implementation Plan Consistency (IPLAN)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths.
