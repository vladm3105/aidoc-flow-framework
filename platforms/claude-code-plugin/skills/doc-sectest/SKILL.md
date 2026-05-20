---
name: doc-sectest
description: Create Security Test Specifications (SECTEST) as Layer 10 subtype artifacts for security control and threat validation
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - sectest
    - shared-architecture
  custom_fields:
    layer: 10
    artifact_type: SECTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: core-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
    downstream_artifacts: [TASKS, Code]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SECTEST-MVP-TEMPLATE schema_version"
---

# doc-sectest

## Purpose

Create **Security Test Specifications (SECTEST)** for security control and threat validation across AuthN, AuthZ, Input, Crypto, Config, and Session categories as a Layer 10 TSPEC subtype.

**Layer**: 10  
**Subtype Code**: 45 (`TSPEC.NN.45.SS`)

---

## Canonical References

Before authoring SECTEST, read:

1. `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
2. `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.yaml`
3. `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
4. `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml`
5. `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml`

---

## When to Use

Use `doc-sectest` when:
- You are creating or editing **SECTEST-only** artifacts.
- `@sec` and `@spec` constraints are primary.
- Threat scenarios and security control validation are the core objective.

Use `doc-tspec` instead when:
- Multi-subtype orchestration is required (UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).
- Cross-subtype normalization or batch TSPEC work is primary.

---

## SECTEST Contract (MVP)

### Required Structure

SECTEST follows a 6-section contract:
1. Document Control
2. Test Scope
3. Test Case Index
4. Test Case Details
5. Security Coverage Matrix
6. Traceability

### Required Tags

- Cumulative Layer-10 tags: `@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@sys`, `@req`, `@spec` (+ `@ctr` if exists)
- Type-specific required tags: `@sec`, `@spec`

### Test Categories and Coverage

- Required categories: `[AuthN]`, `[AuthZ]`, `[Input]`, `[Crypto]`, `[Config]`, `[Session]`
- TASKS-Ready threshold: `>=90%`
- Security coverage target: template-aligned (`>=90%` baseline)

### Folder Rule

Use nested folder structure:
- `docs/10_TSPEC/SECTEST/SECTEST-NN_{slug}/SECTEST-NN_{slug}.md`

### Safety Rule

- Security tests must run in **isolated environments only**.
- Never run security tests against production systems.

---

## Validation Commands

```bash
# SECTEST subtype validation
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_sectest.py docs/10_TSPEC/SECTEST/

# Layer-wide TSPEC validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/

# Quality score validation
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/

# Cross-document validation
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/SECTEST/SECTEST-NN_slug/SECTEST-NN_slug.md --auto-fix

# Cumulative tag validation
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact SECTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Output Quality Gate

- No schema/structure blockers.
- All required SECTEST sections present.
- `@sec` and `@spec` mappings are explicit.
- Threat scenarios and security controls are represented.
- Traceability includes required cumulative tags.
- Safety warnings are present and explicit.
- Report references use versioned naming where applicable.

---

## Related Skills

- `doc-sectest-autopilot`
- `doc-sectest-validator`
- `doc-sectest-reviewer`
- `doc-sectest-fixer`
- `doc-sectest-audit`
- `doc-tspec` (multi-subtype fallback path)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial SECTEST authoring skill aligned to canonical SECTEST MVP template/rules/schema with safety constraints and TSPEC coexistence routing |
