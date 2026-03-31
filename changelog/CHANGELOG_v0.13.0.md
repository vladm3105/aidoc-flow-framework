# CHANGELOG v0.13.0

**Release Date**: 2026-03-31
**Type**: Minor (3-Segment Element ID Migration)

## Summary

Migrated element IDs from 4-segment `TYPE.NN.TT.hash` to 3-segment `TYPE.NN.hash` format across the entire SDD framework. The element type code segment (TT) is removed because YAML parent keys provide type context. All project documents (b-local etc.) will be re-created with the new format.

## Changes

### Element ID Format

| Aspect | Before | After |
|--------|--------|-------|
| Format | `TYPE.NN.TT.hash` (4 segments) | `TYPE.NN.hash` (3 segments) |
| Example | `BRD.02.01.8cf7` | `BRD.02.8cf7` |
| Hash input | `{doc_id}:{section_id}:{title}:{desc}` | `{doc_id}:{yaml_key}:{title}` |
| Regex | `^[A-Z]{2,5}\.\d{2,}\.\d{2,}\.\d{2,}$` | `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$` |

### Standards Updated (Phase 1)

- `ID_NAMING_STANDARDS.md` — format spec, regex, examples, deprecated type code table
- `VALIDATION_STANDARDS.md` — IDPAT-E002/E003/W001, deprecated ELEM codes
- `LAYER_REGISTRY.yaml` — `id_patterns.element` regex

### Templates Updated (Phase 2)

- 11 primary templates in `mcp_sdd/templates/` — format, guidance, all inline examples
- 11 mirror templates synced to `ai_dev_ssd_flow/{NN}_{TYPE}/`
- 11 layer READMEs updated
- SPEC-TEMPLATE.yaml `element_ids:` section updated

### SPEC Subtypes (Phase 3)

- 10 schema + template files (CSPEC, DSPEC, UXSPEC, RISKSPEC, PROCSPEC)
- 6 index + creation rules files

### Prompt Templates (Phase 4)

- `UCC_PROMPT_PRD.md` — removed "4-segment" instruction
- `UCRem_PROMPT_PRD.md`, `UCRem_PROMPT_EARS.md` — format refs updated

### Framework Documentation (Phase 5, ~25 files)

All framework docs updated: README, TRACEABILITY, SPEC_DRIVEN_DEVELOPMENT_GUIDE, AI_ASSISTANT_RULES, QUICK_REFERENCE, METADATA guides, TESTING_STRATEGY, PROJECT_MODEL, FINANCIAL_DOMAIN_CONFIG, and others.

### Claude Code Skills (Phase 6, ~57 files)

All `doc-*` and `doc-*-autopilot` skills updated. `doc-naming/SKILL.md` (primary ID authority) fully migrated.

### Archived

- `ai_dev_ssd_flow/AUTOPILOT/` → `archived/AUTOPILOT_v1_archive/` (deprecated, 14 files with hardcoded ID parsing)

### Deprecated

- Element type code table (01-99) — retained as historical reference only
- BRD Section-to-Element-Code Mapping — YAML key validation replaces it
- ELEM-E001/W001 validation codes — no longer applicable

## Validation

- mcp_sdd tests: all passing
- YAML template validation: all 11 valid
- No backward compatibility — clean break, all project docs re-created
