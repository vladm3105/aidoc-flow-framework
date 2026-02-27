---
name: doc-itest
description: Create Integration Test Specifications (ITEST) as Layer 10 subtype artifacts for component interaction and contract validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - itest
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: ITEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
    downstream_artifacts: [TASKS, Code]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks ITEST-MVP-TEMPLATE schema_version"
---

# doc-itest

## Purpose

Create **Integration Test Specifications (ITEST)** for component interactions, API contract compliance, sequence flow validation, and integration-level data flow checks.

**Layer**: 10  
**Subtype Code**: 41 (`TSPEC.NN.41.SS`)

---

## Canonical References

Before authoring ITEST, read:

1. `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
2. `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.yaml`
3. `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_CREATION_RULES.md`
4. `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_VALIDATION_RULES.md`
5. `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml`

---

## When to Use

Use `doc-itest` when:
- You are creating or editing **ITEST-only** artifacts.
- API contract checks (`@ctr`) and integration requirement checks (`@sys`) are primary.
- Sequence/data flow verification across components is the core objective.

Use `doc-tspec` instead when:
- Multi-subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
- Cross-subtype normalization or batch TSPEC work is primary.

---

## ITEST Contract (MVP)

### Required Structure

ITEST follows a 6-section contract:
1. Document Control
2. Test Scope
3. Test Case Index
4. Test Case Details
5. CTR Coverage Matrix
6. Traceability

### Required Tags

- Cumulative Layer-10 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@spec` (+ `@ctr` if exists)
- Type-specific required tags: `@ctr`, `@sys`

### Threshold and Coverage

- TASKS-Ready threshold: `>=90%`
- CTR coverage target: template-aligned (`>=85%` baseline)

### Folder Rule

Use nested folder structure:
- `docs/10_TSPEC/ITEST/ITEST-NN_{slug}/ITEST-NN_{slug}.md`

### Diagram Rule

- Include sequence diagrams for complex interactions.

---

## Validation Commands

```bash
# ITEST subtype validation
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_itest.py docs/10_TSPEC/ITEST/

# Layer-wide TSPEC validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/

# Quality score validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Cross-document validation
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/ITEST/ITEST-NN_slug/ITEST-NN_slug.md --auto-fix

# Cumulative tag validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact ITEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Output Quality Gate

- No schema/structure blockers.
- All required ITEST sections present.
- `@ctr` and `@sys` mappings are explicit.
- Sequence/data flow checks are represented where interactions are complex.
- Traceability includes required cumulative tags.
- Report references use versioned naming where applicable.

---

## Related Skills

- `doc-itest-autopilot`
- `doc-itest-validator`
- `doc-itest-reviewer`
- `doc-itest-fixer`
- `doc-itest-audit`
- `doc-tspec` (multi-subtype fallback path)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial ITEST authoring skill aligned to canonical ITEST MVP template/rules/schema with TSPEC coexistence routing and canonical validation command set |
