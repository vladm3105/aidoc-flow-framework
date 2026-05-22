---
name: doc-dspec-audit
description: Unified data-spec SPEC (Layer 6) quality gate - validates structure, detects issues, computes TDD-Ready score, and produces a report for the fixer
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: data-design
    deliverable_type: document
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [Audit Report]
    version: "1.0"
    last_updated: "2026-05-22"
---

# doc-dspec-audit

## Purpose

Unified **data-spec SPEC quality gate** that combines structural validation,
content review, and TDD-Ready scoring into a single comprehensive audit. This
is a plugin-only authoring helper — a data-design specialization of SPEC
(Layer 6) — that audits against the single framework SPEC template.

**Layer**: 6 (SPEC — data-design quality gate)

**Parent**: `../doc-spec/`

---

## TDD-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Data-Model Coverage | 25% | All data structures defined with typed fields |
| Interface Completeness | 20% | Public exports and signatures complete |
| Behavior Specification | 20% | Validation rules and state transitions sourced |
| Implementation Notes | 15% | Constraints and patterns documented |
| Downstream TDD Contract | 10% | TDD document referenced |
| Traceability | 10% | All upstream tags present |

**Thresholds**:
- **PASS**: ≥85%
- **CONDITIONAL**: 75-84%
- **FAIL**: <75%

---

## Output Files

| File | Purpose |
|------|---------|
| `SPEC-NN.A_audit_report_vNNN.md` | Comprehensive audit report |

---

## References

- Parent skill: `../doc-spec/`
- Template: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- Layer guide: `framework/layers/06_SPEC/README.md`
- ID standards: `framework/governance/ID_NAMING_STANDARDS.md`
