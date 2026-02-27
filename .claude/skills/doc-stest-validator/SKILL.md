---
name: doc-stest-validator
description: Validate Smoke Test Specifications (STEST) against Layer 10 STEST MVP schema and structure contracts
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - stest
  custom_fields:
    layer: 10
    artifact_type: STEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [STEST]
    downstream_artifacts: [Audit, Fix]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks STEST_MVP_SCHEMA schema_version"
---

# doc-stest-validator

## Purpose

Validate STEST documents for subtype-specific schema, structure, traceability, and deployment-smoke gate requirements.

---

## Validation Schema Reference

- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/STEST/STEST_MVP_VALIDATION_RULES.md`

---

## Validation Checklist

1. Nested folder rule (`STEST-NN_{slug}/STEST-NN_{slug}.md`)
2. Six required sections present and ordered
3. STEST element IDs use `TSPEC.NN.42.SS`
4. Required cumulative tags present (`@brd`..`@spec`, optional `@ctr`)
5. Required subtype tags present (`@ears`, `@bdd`, `@req`)
6. Timeout budget markers are present (`max 300s` or `<=300s`)
7. 100% gate markers are present (`Target: 100%` or `100% quality gate`)
8. Rollback procedure requirement is explicit (every test must have rollback procedure)
9. Binary pass/fail criteria are explicit for critical paths

---

## Commands

```bash
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_stest.py docs/10_TSPEC/STEST/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/STEST/STEST-NN_slug/STEST-NN_slug.md --auto-fix
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact STEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Integration

- Invoked by: `doc-stest`, `doc-stest-autopilot`, `doc-stest-audit`
- Feeds into: `doc-stest-audit`, `doc-stest-fixer`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial STEST validator with schema/structure/tag checks and strict deployment-gate validation rules |
