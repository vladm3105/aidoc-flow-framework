---
name: doc-ptest
description: Create Performance Test Specifications (PTEST) as Layer 10 subtype artifacts for load, stress, endurance, and spike validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - ptest
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: PTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
    downstream_artifacts: [TASKS, Code]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks PTEST-MVP-TEMPLATE schema_version"
---

# doc-ptest

## Purpose

Create **Performance Test Specifications (PTEST)** for system performance validation across Load, Stress, Endurance, and Spike categories as a Layer 10 TSPEC subtype.

**Layer**: 10  
**Subtype Code**: 44 (`TSPEC.NN.44.SS`)

---

## Canonical References

Before authoring PTEST, read:

1. `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md`
2. `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.yaml`
3. `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md`
4. `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml`
5. `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml`

---

## When to Use

Use `doc-ptest` when:
- You are creating or editing **PTEST-only** artifacts.
- `@sys` and `@spec` constraints are primary.
- Performance thresholds and load-profile behavior are the core objective.

Use `doc-tspec` instead when:
- Multi-subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
- Cross-subtype normalization or batch TSPEC work is primary.

---

## PTEST Contract (MVP)

### Required Structure

PTEST follows a 6-section contract:
1. Document Control
2. Test Scope
3. Test Case Index
4. Test Case Details
5. SYS Coverage Matrix
6. Traceability

### Required Tags

- Cumulative Layer-10 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@spec` (+ `@ctr` if exists)
- Type-specific required tags: `@sys`, `@spec`

### Test Categories and Coverage

- Required categories: `[Load]`, `[Stress]`, `[Endurance]`, `[Spike]`
- TASKS-Ready threshold: `>=90%`
- SYS coverage target: template-aligned (`>=85%` baseline)

### Folder Rule

Use nested folder structure:
- `docs/10_TSPEC/PTEST/PTEST-NN_{slug}/PTEST-NN_{slug}.md`

### Performance Rule

- Use **Load Scenario** tables for all test cases.
- Include `execution_profile` for complex scenarios.

---

## Validation Commands

```bash
# PTEST subtype validation
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_ptest.py docs/10_TSPEC/PTEST/

# Layer-wide TSPEC validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/

# Quality score validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Cross-document validation
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/PTEST/PTEST-NN_slug/PTEST-NN_slug.md --auto-fix

# Cumulative tag validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact PTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Output Quality Gate

- No schema/structure blockers.
- All required PTEST sections present.
- `@sys` and `@spec` mappings are explicit.
- Load scenarios and measurable thresholds are present.
- Traceability includes required cumulative tags.
- Report references use versioned naming where applicable.

---

## Related Skills

- `doc-ptest-autopilot`
- `doc-ptest-validator`
- `doc-ptest-reviewer`
- `doc-ptest-fixer`
- `doc-ptest-audit`
- `doc-tspec` (multi-subtype fallback path)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial PTEST authoring skill aligned to canonical PTEST MVP template/rules/schema with TSPEC coexistence routing and canonical validation command set |
