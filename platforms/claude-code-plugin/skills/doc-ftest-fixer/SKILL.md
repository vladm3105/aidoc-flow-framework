---
name: doc-ftest-fixer
description: Apply automated and guided fixes for functional-TDD (Layer 7) findings from audit/review reports
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

# doc-ftest-fixer

## Purpose

Apply fixes for functional-focused **TDD (Layer 7)** issues identified by
validator/reviewer workflows, with deterministic source-report precedence.

This skill is a **TDD (Layer 7) specialization** for the functional-test focus.
It fixes TDD documents against the single canonical artifact contract
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

- Missing required sections (single 7-section TDD template)
- Missing/invalid element IDs (correct to `TDD.NN.04.xxxx`)
- Missing/invalid functional-case `type` (`e2e` / `security`)
- Quality-attribute threshold and measurement-methodology completeness (Section 5)
- Traceability and cross-reference consistency (functional cases trace to EARS / BDD / SPEC; no SYS)
- Naming/path corrections for the `docs/07_TDD/` layout

---

## Outputs

- Fixed TDD document(s)
- `TDD-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-ftest-fixer TDD-01
/doc-ftest-fixer TDD-01 --review-report TDD-01.A_audit_report_v001.md
/doc-ftest-fixer TDD-01 --review-report TDD-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-ftest-audit`
- Re-run `doc-ftest-audit` after fixes to verify closure

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Fixes functional-focused TDD (Layer 7) documents against the single `framework/layers/07_TDD/TDD-TEMPLATE.yaml`; fix categories retargeted to `TDD.NN.04.xxxx` IDs and `e2e`/`security` case types; traceability traces to EARS/BDD/SPEC (no SYS); report contract retargeted to `TDD-NN.*`. |
| 1.0 | 2026-02-27 | Initial functional-test fixer (pre-migration legacy model). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as a valid source mode and verify intent preservation from implementation-plan scope/objectives.
- Validate the upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
