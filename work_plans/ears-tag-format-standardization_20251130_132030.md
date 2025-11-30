# Implementation Plan - EARS Traceability Tag Format Standardization

**Created**: 2025-11-30 13:20:30 EST
**Completed**: 2025-11-30 EST
**Status**: COMPLETED

## Objective

Standardize EARS traceability tag format from mixed prefixed formats (`@ears: EARS-012:STATE-001`, `@ears: EARS-012:EVENT-002`) to simple numeric format (`@ears: EARS-012:001`) across all framework documentation.

## Context

### Problem
EARS traceability tag format is inconsistent across the codebase:
- Current (mixed): `@ears: EARS-012:STATE-001`, `@ears: EARS-012:EVENT-002`
- Correct format: `@ears: EARS-012:001` (simple numeric suffix per TRACEABILITY.md line 305)

### Key Decisions
- **User confirmed**: Simple numeric format (`@ears: EARS-012:001`)
- **Canonical source**: TRACEABILITY.md line 305 defines the correct format
- **Pattern**: `@ears: EARS-NNN:NNN` (document ID + 3-digit numeric requirement ID)

## Task List

### Completed
- [x] Step 1: Update Schema files (validation patterns)
  - BDD/BDD_SCHEMA.yaml
  - SYS/SYS_SCHEMA.yaml
  - ADR/ADR_SCHEMA.yaml
  - REQ/REQ_SCHEMA.yaml
  - CTR/CTR_SCHEMA.yaml
  - TASKS/TASKS_SCHEMA.yaml
  - IPLAN/IPLAN_SCHEMA.yaml
  - SPEC/SPEC_SCHEMA.yaml
- [x] Step 2: Update Template files (*-TEMPLATE.*)
  - BDD/BDD-TEMPLATE.feature
  - SYS/SYS-TEMPLATE.md
  - ADR/ADR-TEMPLATE.md
  - CTR/CTR-TEMPLATE.md
  - REQ/REQ-TEMPLATE.md
  - TASKS/TASKS-TEMPLATE.md
  - IPLAN/IPLAN-TEMPLATE.md
  - IMPL/IMPL-TEMPLATE.md
  - SPEC/SPEC-TEMPLATE.yaml
  - REQ/archived/REQ-TEMPLATE-V2-ARCHIVED.md
- [x] Step 3: Update Creation/Validation Rules
  - All *_CREATION_RULES.md files
  - All *_VALIDATION_RULES.md files
- [x] Step 4: Update Traceability Matrix Templates
  - All *-000_TRACEABILITY_MATRIX-TEMPLATE.md files
  - TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md
- [x] Step 5: Update Reference Documents
  - COMPLETE_TAGGING_EXAMPLE.md
  - SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
  - README.md
  - TRACEABILITY.md
  - IPLAN/README.md
- [x] Step 6: Verification - grep for remaining prefixed formats (PASSED)

## Implementation Guide

### Prerequisites
- Read current ai_dev_flow/ files before editing
- Understand YAML schema structure for regex patterns

### Execution Steps

1. **Schema Pattern Updates**
   Change regex patterns from:
   ```yaml
   pattern: "@ears:\\s*EARS-\\d{3}:[A-Z]+-\\d{3}"
   ```
   To:
   ```yaml
   pattern: "@ears:\\s*EARS-\\d{3}:\\d{3}"
   ```

2. **Template Example Updates**
   Change examples from:
   ```markdown
   @ears: EARS-001:EVENT-003
   @ears: EARS-012:STATE-001
   ```
   To:
   ```markdown
   @ears: EARS-001:003
   @ears: EARS-012:001
   ```

3. **Placeholder Updates**
   Change template placeholders from:
   ```markdown
   @ears: EARS-NNN:STATEMENT-ID
   ```
   To:
   ```markdown
   @ears: EARS-NNN:NNN
   ```

### Verification
```bash
# Should find NO matches with prefixed format (EVENT-, STATE-, STATEMENT-, REQ-)
grep -rE "EARS-[0-9]{3}:[A-Z]+-[0-9]{3}" ai_dev_flow/

# Should find matches with numeric format only
grep -rE "@ears:.*EARS-[0-9]{3}:[0-9]{3}" ai_dev_flow/
```

## References

- **Files**:
  - `ai_dev_flow/TRACEABILITY.md` (line 305 - canonical format)
  - `ai_dev_flow/BDD/BDD_SCHEMA.yaml` (pattern definition)
  - All *-TEMPLATE.* files in ai_dev_flow/
- **Related Work**: BDD consistency fix completed earlier (bdd-consistency-fix_20251130_130901.md)
