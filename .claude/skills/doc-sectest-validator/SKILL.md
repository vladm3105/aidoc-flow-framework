---
name: doc-sectest-validator
description: Validate Security Test Specifications (SECTEST) against Layer 10 SECTEST MVP schema and structure contracts
metadata:
  tags:
    - sdd-workflow
    - layer-10-artifact
    - quality-assurance
    - sectest
  custom_fields:
    layer: 10
    artifact_type: SECTEST
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [SECTEST]
    downstream_artifacts: [Audit, Fix]
    version: "1.0"
    last_updated: "2026-02-27"
  versioning_policy: "tracks SECTEST_MVP_SCHEMA schema_version"
---

# doc-sectest-validator

## Purpose

Validate SECTEST documents for subtype-specific schema, structure, traceability, security-control, and safety requirements.

---

## Validation Schema Reference

- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_SCHEMA.yaml`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST-MVP-TEMPLATE.md`
- `ai_dev_ssd_flow/10_TSPEC/SECTEST/SECTEST_MVP_VALIDATION_RULES.md`

---

## Validation Checklist

1. Nested folder rule (`SECTEST-NN_{slug}/SECTEST-NN_{slug}.md`)
2. Six required sections present and ordered
3. SECTEST element IDs use `TSPEC.NN.45.SS`
4. Required cumulative tags present (`@brd`..`@spec`, optional `@ctr`)
5. Required subtype tags present (`@sec`, `@spec`)
6. Required categories represented (`[AuthN]`, `[AuthZ]`, `[Input]`, `[Crypto]`, `[Config]`, `[Session]`)
7. Threat scenario and security controls tables are present
8. TASKS-Ready score claim present and threshold-aligned
9. Safety warning statements are present and explicit

---

## Commands

```bash
python ai_dev_ssd_flow/10_TSPEC/scripts/validate_sectest.py docs/10_TSPEC/SECTEST/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_all_tspec.sh docs/10_TSPEC/
bash ai_dev_ssd_flow/10_TSPEC/scripts/validate_tspec_quality_score.sh docs/10_TSPEC/
python ai_dev_ssd_flow/scripts/validate_cross_document.py --document docs/10_TSPEC/SECTEST/SECTEST-NN_slug/SECTEST-NN_slug.md --auto-fix
python ai_dev_ssd_flow/scripts/validate_tags_against_docs.py --artifact SECTEST-NN --expected-layers brd,prd,ears,bdd,adr,sys,req,spec --strict
```

---

## Integration

- Invoked by: `doc-sectest`, `doc-sectest-autopilot`, `doc-sectest-audit`
- Feeds into: `doc-sectest-audit`, `doc-sectest-fixer`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-27 | Initial SECTEST validator with schema/structure/tag/security checks, safety constraints, and canonical script references |
