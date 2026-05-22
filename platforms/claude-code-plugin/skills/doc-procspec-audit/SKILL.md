---
name: doc-procspec-audit
description: Unified process-spec SPEC (Layer 6) quality gate - validates structure, detects issues, computes TDD-Ready score, and produces a report for doc-procspec-fixer
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - spec-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    spec_focus: process-design
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

# doc-procspec-audit

## Purpose

Unified **process-spec SPEC quality gate** that combines structural validation,
content review, and TDD-Ready scoring into a single comprehensive audit. This
is a plugin-only authoring helper — a process/workflow-design specialization of
SPEC (Layer 6) — that audits against the single framework SPEC template
(`framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`, see `../doc-spec/`).

**Layer**: 6 (SPEC — process-design quality gate)

**Parent**: `../doc-spec/`

---

## TDD-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Step Completeness | 25% | All process steps documented with pre/post conditions |
| Role Assignment | 20% | Responsible roles defined per step |
| Decision Points | 15% | Branch logic and outcomes clear |
| Error Handling | 15% | Recovery and fallback procedures documented |
| Verification Steps | 15% | Completion criteria and quality checks defined |
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
