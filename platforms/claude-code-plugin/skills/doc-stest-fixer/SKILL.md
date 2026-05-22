---
name: doc-stest-fixer
description: Apply automated and guided fixes for smoke-focused TDD (Layer 7) findings from audit/review reports
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

# doc-stest-fixer

## Purpose

Apply fixes for **smoke-focused TDD (Layer 7)** issues identified by
validator/reviewer workflows, with deterministic source-report precedence.

This skill is a **TDD (Layer 7) specialization**. It remediates TDD documents
whose test cases carry a smoke / deployment critical-path focus; it does **not**
define a separate artifact, template, or element-code. The canonical artifact
contract is `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (see `../doc-tdd/`).

**Layer**: 7 (TDD — smoke focus)

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

- Missing required sections (7-section TDD template)
- Missing/invalid cumulative tags (`@brd`..`@spec`) or `@tdd` self-tag
- Missing critical-path traceability (`@ears`, `@bdd`, `@spec`)
- Missing smoke timeout or 100%-gate constraints
- Missing rollback / cleanup requirements
- Non-binary pass/fail criteria in critical-path checks
- Invalid element IDs (correct to `TDD.NN.04.xxxx`)
- Traceability and cross-reference consistency
- Naming/path corrections (`docs/07_TDD/TDD-NN_{slug}.yaml`)

---

## Outputs

- Fixed TDD document(s)
- `TDD-NN.F_fix_report_vNNN.md`

---

## Commands

```bash
/doc-stest-fixer TDD-01
/doc-stest-fixer TDD-01 --review-report TDD-01.A_audit_report_v001.md
/doc-stest-fixer TDD-01 --review-report TDD-01.R_review_report_v001.md
```

---

## Integration

- Typically invoked after `doc-stest-audit`
- Re-run `doc-stest-audit` after fixes to verify closure

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
| 2.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (D-0015). Repositioned as a TDD (Layer 7) smoke-focus fixer over `TDD-NN` documents with `TDD.NN.04.xxxx` element IDs; dropped the legacy smoke-test subtype identity, legacy layer framing, and legacy flow paths. References `framework/layers/07_TDD/TDD-TEMPLATE.yaml`. |
| 1.0 | 2026-02-27 | Initial smoke-test fixer (pre-migration). |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback reference paths.
