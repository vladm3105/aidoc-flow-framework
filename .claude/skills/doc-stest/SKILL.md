---
name: doc-stest
description: Create Smoke Test Specifications (STEST) as Layer 10 subtype artifacts for deployment critical-path validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - stest
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: STEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
    downstream_artifacts: [TASKS, Code]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks STEST-MVP-TEMPLATE schema_version"
---

# doc-stest

## Purpose

Create **Smoke Test Specifications (STEST)** for deployment critical-path validation with strict fail-fast pass/fail outcomes as a Layer 10 TSPEC subtype.

**Layer**: 10  
**Subtype Code**: 42 (`TSPEC.NN.42.SS`)

---

## Canonical References

Before authoring STEST, read:

1. `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md`
2. `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.yaml`
3. `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_CREATION_RULES.md`
4. `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_VALIDATION_RULES.md`
5. `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml`

---

## When to Use

Use `doc-stest` when:
- You are creating or editing **STEST-only** artifacts.
- `@ears`, `@bdd`, and `@req` constraints are primary.
- Deployment smoke validation and critical-path rollback readiness are the core objective.

Use `doc-tspec` instead when:
- Multi-subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
- Cross-subtype normalization or batch TSPEC work is primary.

---

## STEST Contract (MVP)

### Required Structure

STEST follows a 6-section contract:
1. Document Control
2. Test Scope
3. Critical Path Index
4. Test Case Details
5. Rollback Procedures
6. Traceability

### Required Tags

- Cumulative Layer-10 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@spec` (+ `@ctr` if exists)
- Type-specific required tags: `@ears`, `@bdd`, `@req`

### Deployment Gate Requirements

- Total timeout budget must be `<=300s` (max 300s / <5 minutes)
- Quality gate target is `100% quality gate` (`Target: 100%`)
- Every test must have rollback procedure
- Pass/fail criteria must be binary and fail-fast

### Folder Rule

Use nested folder structure:
- `docs/10_TSPEC/STEST/STEST-NN_{slug}/STEST-NN_{slug}.md`

---

## Validation Commands

```bash
# STEST subtype validation
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_stest.py docs/10_TSPEC/STEST/

# Layer-wide TSPEC validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/

# Quality score validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Cross-document validation
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/STEST/STEST-NN_slug/STEST-NN_slug.md --auto-fix

# Cumulative tag validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact STEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Output Quality Gate

- No schema/structure blockers.
- All required STEST sections present.
- `@ears`, `@bdd`, and `@req` mappings are explicit.
- Timeout and rollback constraints are present.
- Binary pass/fail criteria are explicit for critical paths.
- Report references use versioned naming where applicable.

---

## Related Skills

- `doc-stest-autopilot`
- `doc-stest-validator`
- `doc-stest-reviewer`
- `doc-stest-fixer`
- `doc-stest-audit`
- `doc-tspec` (multi-subtype fallback path)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial STEST authoring skill aligned to canonical STEST MVP template/rules/schema with deployment-gate constraints and TSPEC coexistence routing |
