---
name: doc-ftest
description: Create Functional Test Specifications (FTEST) as Layer 10 subtype artifacts focused on quality-attribute validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - ftest
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: FTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
    downstream_artifacts: [TASKS, Code]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks FTEST-MVP-TEMPLATE schema_version"
---

# doc-ftest

## Purpose

Create **Functional Test Specifications (FTEST)** for system-level quality attribute validation (Performance, Reliability, Security, Scalability) as a Layer 10 TSPEC subtype.

**Layer**: 10  
**Subtype Code**: 43 (`TSPEC.NN.43.SS`)

---

## Canonical References

Before authoring FTEST, read:

1. `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md`
2. `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.yaml`
3. `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_CREATION_RULES.md`
4. `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_VALIDATION_RULES.md`
5. `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml`

---

## When to Use

Use `doc-ftest` when:
- You are creating or editing **FTEST-only** artifacts.
- `@sys` and `@threshold` constraints are primary.
- Quality-attribute threshold validation is the core objective.

Use `doc-tspec` instead when:
- Multi-subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
- Cross-subtype normalization or batch TSPEC work is primary.

---

## FTEST Contract (MVP)

### Required Structure

FTEST follows a 6-section contract:
1. Document Control
2. Test Scope
3. Test Case Index
4. Test Case Details
5. SYS Coverage Matrix
6. Traceability

### Required Tags

- Cumulative Layer-10 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@spec` (+ `@ctr` if exists)
- Type-specific required tags: `@sys`, `@threshold`

### Threshold and Coverage

- TASKS-Ready threshold: `>=90%`
- SYS coverage target: template-aligned (`>=85%` baseline)

### Folder Rule

Use nested folder structure:
- `docs/10_TSPEC/FTEST/FTEST-NN_{slug}/FTEST-NN_{slug}.md`

---

## Validation Commands

```bash
# FTEST subtype validation
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_ftest.py docs/10_TSPEC/FTEST/

# Layer-wide TSPEC validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/

# Quality score validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Cross-document validation
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/FTEST/FTEST-NN_slug/FTEST-NN_slug.md --auto-fix

# Cumulative tag validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact FTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Output Quality Gate

- No schema/structure blockers.
- All required FTEST sections present.
- `@threshold` mappings are explicit for measurable criteria.
- Traceability includes required cumulative tags.
- Report references use versioned naming where applicable.

---

## Related Skills

- `doc-ftest-autopilot`
- `doc-ftest-validator`
- `doc-ftest-reviewer`
- `doc-ftest-fixer`
- `doc-ftest-audit`
- `doc-tspec` (multi-subtype fallback path)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial FTEST authoring skill; aligned to canonical FTEST MVP template/rules/schema; added TSPEC coexistence routing and canonical validation command set |
