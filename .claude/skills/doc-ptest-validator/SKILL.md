---
name: doc-ptest-validator
description: Validate Performance Test Specifications (PTEST) against Layer 10 PTEST MVP schema and structure contracts
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - ptest
  custom_fields:
    layer: 10
    artifact_type: PTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [PTEST]
    downstream_artifacts: [Audit, Fix]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks PTEST_MVP_SCHEMA schema_version"
---

# doc-ptest-validator

## Purpose

Validate PTEST documents for subtype-specific schema, structure, traceability, and performance-threshold requirements.

---

## Validation Schema Reference

- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/PTEST/PTEST_MVP_VALIDATION_RULES.md`

---

## Validation Checklist

1. Nested folder rule (`PTEST-NN_{slug}/PTEST-NN_{slug}.md`)
2. Six required sections present and ordered
3. PTEST element IDs use `TSPEC.NN.44.SS`
4. Required cumulative tags present (`@brd`..`@spec`, optional `@ctr`)
5. Required subtype tags present (`@sys`, `@spec`)
6. Required categories represented (`[Load]`, `[Stress]`, `[Endurance]`, `[Spike]`)
7. Load scenario tables and measurable thresholds are present
8. TASKS-Ready score claim present and threshold-aligned

---

## Commands

```bash
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_ptest.py docs/10_TSPEC/PTEST/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/PTEST/PTEST-NN_slug/PTEST-NN_slug.md --auto-fix
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact PTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Integration

- Invoked by: `doc-ptest`, `doc-ptest-autopilot`, `doc-ptest-audit`
- Feeds into: `doc-ptest-audit`, `doc-ptest-fixer`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial PTEST validator with schema/structure/tag/performance checks and canonical script references |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

