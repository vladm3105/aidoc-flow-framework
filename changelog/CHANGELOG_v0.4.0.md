# CHANGELOG v0.4.0

**Release Date**: 2026-03-29
**Type**: Minor (EARS Template Unification)

## Summary

Unified the EARS (Layer 3) artifact into a single YAML template, following the same approach as BRD (v0.2.0) and PRD (v0.3.0). Incorporated PRD EARS appendix content (timing profiles, boundary values, state transitions) into the template.

## Changes

### EARS Layer Unification

**New**: `ai_dev_ssd_flow/03_EARS/EARS-TEMPLATE.yaml` (387 lines, schema v1.0)

**Replaced** (6 files, 2,988 lines → 387 lines):

| File | Lines | Disposition |
|------|-------|-------------|
| `EARS-MVP-TEMPLATE.md` | 264 | Archived |
| `EARS-MVP-TEMPLATE.yaml` | 292 | Archived |
| `EARS_MVP_SCHEMA.yaml` | 350 | Archived |
| `EARS_MVP_CREATION_RULES.md` | 706 | Guidance embedded as `_guidance` fields |
| `EARS_MVP_VALIDATION_RULES.md` | 690 | Validation via mcp_sdd tools |
| `EARS_MVP_QUALITY_GATE_VALIDATION.md` | 686 | Quality gates via mcp_sdd tools |

**Archived**: 16+ files + scripts/ + examples/ + backup → `EARS_v1_archive/`

### Section Structure (6 → 5 + glossary)

| Old | New | Change |
|-----|-----|--------|
| Section 2 (Workflow) | Merged into Section 2 `_guidance` | Workflow is template-level info |
| Section 6 (References) | Merged into Section 5 (Traceability) | Consolidation |

### PRD EARS Appendix Incorporated

Content preserved from PRD v0.3.0 migration (`tmp/EARS_APPENDIX_FROM_PRD.md`) now embedded:
- Timing Profile Matrix (p50/p95/p99) → `quality_attributes._guidance`
- Boundary Value Matrix → `requirements._guidance`
- State Transition Diagram template → `requirements._guidance`
- Fallback Path Documentation → `requirements._guidance`
- EARS-Ready Checklist → `requirements._guidance`
- Timing vocabulary replacements → `quality_attributes._guidance`

### Hash-Based Element IDs

Old type codes (25=EARS statement, 02=performance, 03=security, 04=reliability)
replaced by section-based hash IDs: `EARS.{doc_id}.{section_id}.{hash}`

### BRD Downstream Split

BRD `downstream_expected` entry `"EARS/BDD"` (layer "3/4") split into:
- EARS (layer 3): "Formal WHEN-THE-SHALL-WITHIN requirements"
- BDD (layer 4): "Given-When-Then test scenarios"

### C4 Model Position

EARS documented as refinement step (not a C4 level) that formalizes the Context→Container transition between BRD and PRD.

### mcp_sdd Updates

- Copied `EARS-TEMPLATE.yaml` to `mcp_sdd/templates/`
- Removed `mcp_sdd/templates/EARS-MVP-TEMPLATE.md`
- Updated `UCRem_PROMPT_EARS.md`: element IDs (pattern codes → hash-based), quality checklist
- No source code changes (PLAN-002 naming migration already in place)

### Other Fixes

- EARS acronym corrected in `EARS-00_index.md`: "Event-Action-Response-State" → "Easy Approach to Requirements Syntax"

## Backward Compatibility

- mcp_sdd test suite: 173 passed, 1 pre-existing failure, 0 regressions
- EARS parity validation (trigger + actor clause check) unchanged and verified

## Validation Evidence

- YAML syntax: `yaml.safe_load()` passes
- Template resolution: `resolve_template_path()` finds `EARS-TEMPLATE.yaml`
- EARS parity tests: 4 passed
- mcp_sdd full suite: 173 passed, 0 regressions
