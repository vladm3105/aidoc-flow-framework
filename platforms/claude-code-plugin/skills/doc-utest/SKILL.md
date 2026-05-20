---
name: doc-utest
description: Create Unit Test Specifications (UTEST) as Layer 10 subtype artifacts for component-level test validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - utest
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: UTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
    downstream_artifacts: [TASKS, Code]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks UTEST-MVP-TEMPLATE schema_version"
---

# doc-utest

## Purpose

Create **Unit Test Specifications (UTEST)** for component-level validation as a Layer 10 TSPEC subtype with explicit REQ traceability and TASKS-ready quality gates.

**Layer**: 10  
**Subtype Code**: 40 (`TSPEC.NN.40.SS`)

---

## Canonical References

Before authoring UTEST, read:

1. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
2. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.yaml`
3. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
4. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml`
5. `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml`

---

## When to Use

Use `doc-utest` when:
- You are creating or editing **UTEST-only** artifacts.
- `@req` and `@spec` mappings are primary.
- Component-level logic, state, validation, and edge-case checks are the core objective.

Use `doc-tspec` instead when:
- Multi-subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
- Cross-subtype normalization or batch TSPEC work is primary.

---

## UTEST Contract (MVP)

### Required Structure

UTEST follows a 6-section contract:
1. Document Control
2. Test Scope
3. Test Case Index
4. Test Case Details
5. REQ Coverage Matrix
6. Traceability

### Required Tags

- Cumulative Layer-10 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@spec` (+ `@ctr` if exists)
- UTEST-specific required tags: `@req`, `@spec`

### Unit-Test Gate Requirements

- TASKS-Ready score target must be `>=90%`.
- REQ coverage target must be `>=90%`.
- Test categories must include `[Logic]`, `[State]`, `[Validation]`, `[Edge]`.
- Every test case must include an Input/Output table.
- Complex test logic must include pseudocode.

### Folder Rule

Use nested folder structure:
- `docs/10_TSPEC/UTEST/UTEST-NN_{slug}/UTEST-NN_{slug}.md`

---

## Validation Commands

```bash
# UTEST subtype validation
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_utest.py docs/10_TSPEC/UTEST/

# Layer-wide TSPEC validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/

# Quality score validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Cross-document validation
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/UTEST/UTEST-NN_slug/UTEST-NN_slug.md --auto-fix

# Cumulative tag validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact UTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Output Quality Gate

- No schema/structure blockers.
- All required UTEST sections present.
- `@req` and `@spec` mappings are explicit.
- REQ coverage and TASKS-ready scores meet `>=90%` target.
- `[Logic]`, `[State]`, `[Validation]`, `[Edge]` categories are represented.
- Input/Output tables and pseudocode guidance are present where required.
- Report references use versioned naming where applicable.

---

## Related Skills

- `doc-utest-autopilot`
- `doc-utest-validator`
- `doc-utest-reviewer`
- `doc-utest-fixer`
- `doc-utest-audit`
- `doc-tspec` (multi-subtype fallback path)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial UTEST authoring skill aligned to canonical UTEST MVP template/rules/schema with 90%-gate constraints and TSPEC coexistence routing |
