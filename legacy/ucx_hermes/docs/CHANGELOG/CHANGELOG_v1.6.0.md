# CHANGELOG v1.6.0

**Release Date**: 2026-03-31
**Type**: Minor (3-Segment Element ID Migration)

## Summary

Migrated all templates, prompts, and skills from 4-segment `TYPE.NN.TT.hash` to 3-segment `TYPE.NN.hash` element ID format. YAML parent keys replace element type codes for semantic context.

## Changes

### Templates (11 files)

- `format:` changed from `{doc_type}.{doc_id}.{section_id}.{hash}` to `{doc_type}.{doc_id}.{hash}`
- Hash input: `{doc_id}:{yaml_key}:{title}` (replaces `{doc_id}:{section_id}:{title}:{description}`)
- All inline examples updated to 3-segment
- SPEC-TEMPLATE.yaml `element_ids:` section updated

### Prompt Templates (3 files modified)

- `UCC_PROMPT_PRD.md` — "4-segment" → "3-segment", removed type code table
- `UCRem_PROMPT_PRD.md` — format refs updated
- `UCRem_PROMPT_EARS.md` — format refs updated

### Validation Regex

- `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$` — 3-segment only, supports SPEC subtypes (CSPEC, UXSPEC, RISKSPEC, PROCSPEC)
