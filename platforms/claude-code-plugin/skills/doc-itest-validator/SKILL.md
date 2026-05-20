---
name: doc-itest-validator
description: Validate Integration Test Specifications (ITEST) against Layer 10 ITEST MVP schema and structure contracts
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - itest
  custom_fields:
    layer: 10
    artifact_type: ITEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [ITEST]
    downstream_artifacts: [Audit, Fix]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks ITEST_MVP_SCHEMA schema_version"
---

# doc-itest-validator

## Purpose

Validate ITEST documents for subtype-specific schema, structure, traceability, contract, and interaction requirements.

---

## Validation Schema Reference

- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/ITEST/ITEST_MVP_SCHEMA.yaml`

---

## Validation Checklist

1. Nested folder rule (`ITEST-NN_{slug}/ITEST-NN_{slug}.md`)
2. Six required sections present and ordered
3. ITEST element IDs use `TSPEC.NN.41.SS`
4. Required cumulative tags present (`@brd`..`@spec`, optional `@ctr`)
5. Required subtype tags present (`@ctr`, `@sys`)
6. Contract compliance tables and interaction coverage are present
7. Sequence diagrams exist for complex interactions
8. CTR coverage matrix and TASKS-Ready claim are present

---

## Commands

```bash
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_itest.py docs/10_TSPEC/ITEST/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/ITEST/ITEST-NN_slug/ITEST-NN_slug.md --auto-fix
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact ITEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Integration

- Invoked by: `doc-itest`, `doc-itest-autopilot`, `doc-itest-audit`
- Feeds into: `doc-itest-audit`, `doc-itest-fixer`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial ITEST validator with schema/structure/tag/contract checks and canonical script references |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

