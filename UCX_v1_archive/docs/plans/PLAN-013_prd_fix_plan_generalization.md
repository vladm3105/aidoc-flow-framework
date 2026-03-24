# PLAN-013: PRD Fix Plan Generalization and Historical Preservation

**Document ID**: PLAN-013_prd_fix_plan_generalization
**Created**: 2026-03-22
**Updated**: 2026-03-22
**Status**: Completed
**Target Version**: UCX v1.21.7
**Related Plans**: PLAN-006_fixer_to_llm_handoff.md, PLAN-012_prd_derived_artifact_flow.md

---

## Objective

Generalize the PRD-01-specific fix plan into a reusable template that applies to all PRDs while preserving the PRD-01 remediation history for auditability.

This plan formalizes a reusable pattern for split remediation:
1. Deterministic script-based fixes
2. Semantic LLM-based fixes

---

## Problem Statement

The original PRD-01 fix plan contained implementation details specific to one document instance.

Observed limitations:
- PRD-specific wording reduced reuse across other PRDs
- Historical details were mixed with procedural guidance
- Deterministic versus semantic boundaries were not documented as a reusable contract

Required outcome:
- One template that can be instantiated for any PRD
- Retention of PRD-01 findings and corrections as historical evidence
- Alignment with existing handoff rules and derived-artifact workflow

---

## Scope

### In Scope

- Convert PRD fix-plan content to template form with placeholders
- Preserve PRD-01 case details in a dedicated history section
- Keep deterministic/LLM split consistent with runtime handoff logic
- Record this change as PLAN-013 for UCX history

### Out of Scope

- Changes to validator rule logic
- Changes to PRD scoring model
- Migration tooling for old fix-plan files

---

## Design Decisions

### 1. Template-First Structure

Use a reusable plan structure with `<PRD-ID>` and `<PRD_DIR>` placeholders so the same document can drive remediation for any PRD.

### 2. Explicit Fix-Class Separation

Document deterministic and semantic catalogs separately to reduce role ambiguity:
- Deterministic: script-safe structural and ID fixes
- Semantic: content-quality and notation consistency tasks requiring LLM review

### 3. Historical Preservation via Embedded Case Snapshot

Retain PRD-01 context in the template's historical section so prior corrections remain traceable without keeping a one-off active plan format.

### 4. Guardrail Documentation for Section 14

Document that Section 14 launch criteria are structural checklist content and should not generate `PRD.NN.14.xx` element IDs.

---

## Implementation Steps

1. Replace PRD-01-specific language with generic template directives.
2. Add reusable status/task tables for deterministic and LLM phases.
3. Add standard command sequence for validate/review/remediate.
4. Add a dedicated historical section preserving PRD-01 decisions and lessons.
5. Publish this PLAN-013 entry to document rationale and governance lineage.

---

## Validation Criteria

1. Template can be reused for any PRD by replacing placeholders only.
2. Deterministic and LLM sections have no overlap in ownership.
3. Historical PRD-01 context remains available in the generalized file.
4. Cross-references to PLAN-006 and PLAN-012 remain accurate.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Operators treat template as PRD-01-only | Reduced reuse | Use neutral title, generic variables, and explicit scope |
| Historical details removed during cleanup | Audit gap | Keep dedicated PRD-01 history subsection |
| Drift between template and fixer behavior | Process mismatch | Keep catalogs aligned with fixer handoff boundaries |

---

## Historical Notes

- PRD-01 remediation surfaced invalid-type-code risks when adding structural sections.
- Template guidance now captures this as a reusable rule.
- PLAN-013 records transition from one-off incident plan to reusable operational artifact.

---

## Completion Record

| Date | Status | Notes |
|------|--------|-------|
| 2026-03-22 | Completed | PRD fix plan generalized and PRD-01 history preserved |
