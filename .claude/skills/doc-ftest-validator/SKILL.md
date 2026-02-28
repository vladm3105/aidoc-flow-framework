---
name: doc-ftest-validator
description: Validate Functional Test Specifications (FTEST) against Layer 10 FTEST MVP schema and structure contracts
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ftest
  custom_fields:
    layer: 10
    artifact_type: FTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [FTEST]
    downstream_artifacts: [Audit, Fix]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks FTEST_MVP_SCHEMA schema_version"
---

# doc-ftest-validator

## Purpose

Validate FTEST documents for subtype-specific schema, structure, traceability, and threshold-quality constraints.

---

## Validation Schema Reference

- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/FTEST/FTEST_MVP_VALIDATION_RULES.md`

---

## Validation Checklist

1. Nested folder rule (`FTEST-NN_{slug}/FTEST-NN_{slug}.md`)
2. Six required sections present and ordered
3. FTEST element IDs use `TSPEC.NN.43.SS`
4. Required cumulative tags present (`@brd`..`@spec`, optional `@ctr`)
5. Required subtype tags present (`@sys`, `@threshold`)
6. SYS coverage matrix and threshold references are present
7. TASKS-Ready score claim present and threshold-aligned

---

## Commands

```bash
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_ftest.py docs/10_TSPEC/FTEST/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/FTEST/FTEST-NN_slug/FTEST-NN_slug.md --auto-fix
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact FTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Integration

- Invoked by: `doc-ftest`, `doc-ftest-autopilot`, `doc-ftest-audit`
- Feeds into: `doc-ftest-audit`, `doc-ftest-fixer`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial FTEST validator with schema/structure/tag/threshold checks and canonical script references |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

