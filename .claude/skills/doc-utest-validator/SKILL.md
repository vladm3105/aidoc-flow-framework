---
name: doc-utest-validator
description: Validate Unit Test Specifications (UTEST) against Layer 10 UTEST MVP schema and structure contracts
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - utest
  custom_fields:
    layer: 10
    artifact_type: UTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [UTEST]
    downstream_artifacts: [Audit, Fix]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks UTEST_MVP_SCHEMA schema_version"
---

# doc-utest-validator

## Purpose

Validate UTEST documents for subtype-specific schema, structure, traceability, and unit-test gate requirements.

---

## Validation Schema Reference

- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/UTEST/UTEST_MVP_VALIDATION_RULES.md`

---

## Validation Checklist

1. Nested folder rule (`UTEST-NN_{slug}/UTEST-NN_{slug}.md`)
2. Six required sections present and ordered
3. UTEST element IDs use `TSPEC.NN.40.SS`
4. Required cumulative tags present (`@brd`..`@spec`, optional `@ctr`)
5. Required subtype tags present (`@req`, `@spec`)
6. TASKS-Ready score markers are present (`Target: >=90%`)
7. REQ coverage markers are present (`Coverage: >=90%`)
8. Test categories include `[Logic]`, `[State]`, `[Validation]`, `[Edge]`
9. Input/Output table requirement is satisfied for test cases
10. Pseudocode guidance exists for complex test logic

---

## Commands

```bash
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_utest.py docs/10_TSPEC/UTEST/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/UTEST/UTEST-NN_slug/UTEST-NN_slug.md --auto-fix
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact UTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Integration

- Invoked by: `doc-utest`, `doc-utest-autopilot`, `doc-utest-audit`
- Feeds into: `doc-utest-audit`, `doc-utest-fixer`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial UTEST validator with schema/structure/tag checks and unit-test 90% gate validation rules |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

