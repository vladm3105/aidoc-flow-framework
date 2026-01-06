# Framework Format Issues Report

**Generated**: 2025-12-10
**Status**: Issues identified for remediation

---

## Summary

| Category | Files Affected | Severity | Action |
|----------|----------------|----------|--------|
| ADR-REF format | 3 | MEDIUM | Fix references |
| EARS internal ID format | 5 | LOW | Update template examples |
| Document-level tags (missing sub-ID) | 4 | MEDIUM | Add sub-IDs to examples |

---

## Issue 1: ADR-REF Format (OLD)

**Standard**: `@adr: ADR-NNN` (e.g., `@adr: ADR-033`)
**Issue**: Using `ADR-REF-NNN` pattern instead of `ADR-NNN`

### Files Requiring Fixes

| File | Lines | Current | Correct |
|------|-------|---------|---------|
| `ai_dev_flow/METADATA_TAGGING_GUIDE.md` | 391, 411, 432, 433, 529, 851, 889 | `ADR-REF-002`, `ADR-REF-001` | `ADR-033`, `ADR-034` |
| `ai_dev_flow/METADATA_QUICK_REFERENCE.md` | 45, 75, 478 | `ADR-REF-002`, `ADR-REF-001` | `ADR-033`, `ADR-034` |
| `ai_dev_flow/AI_ASSISTANT_RULES.md` | 1036, 1047 | `ADR-REF-002`, `ADR-REF-001` | `ADR-033`, `ADR-034` |

---

## Issue 2: EARS Internal ID Format (OLD)

**Standard**: Internal statements use `EARS.NNN.NNN` format for traceability tags
**Issue**: EARS template shows old hyphenated format `EARS-NNN-NNN` in examples

### Files Requiring Updates

| File | Lines | Current | Note |
|------|-------|---------|------|
| `ai_dev_flow/EARS/EARS-TEMPLATE.md` | 212-215 | `EARS-001-001`, `EARS-001-101` | Template example table |
| `ai_dev_flow/EARS/EARS_CREATION_RULES.md` | 111, 161 | `EARS-006-001`, `EARS-001-001` | Example patterns |
| `ai_dev_flow/EARS/EARS_VALIDATION_RULES.md` | 267, 268, 327, 329, 334, 336, 476 | `EARS-006-001`, `EARS-002-001` | Validation examples |
| `ai_dev_flow/METADATA_VS_TRACEABILITY.md` | 121 | `EARS-002-003` | Inline example |
| `ai_dev_flow/scripts/validate_ears.py` | 74 | `EARS-030-001` | Regex comment |

**Note**: For @ears traceability TAGS, the format is `EARS.NNN.NNN` (dots). The hyphenated format may still be valid for internal section IDs in EARS documents. Needs clarification.

---

## Issue 3: Document-Level Tags Missing Sub-IDs

**Standard**:
- BRD: `@brd: BRD.NNN.NNN`
- PRD: `@prd: PRD.NNN.NNN`
- EARS: `@ears: EARS.NNN.NNN`

**Issue**: Examples show document-level references without sub-IDs

### Files Requiring Updates

| File | Lines | Current | Should Be |
|------|-------|---------|-----------|
| `ai_dev_flow/METADATA_VS_TRACEABILITY.md` | 110, 115, 120, 125, 253, 255 | `@brd: BRD-001`, `@prd: PRD-003`, `@ears: EARS-002` | `@brd: BRD.001.XXX`, `@prd: PRD.003.XXX`, `@ears: EARS.002.XXX` |
| `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | 279-284 | `@brd: BRD-001`, `@prd: PRD-003` | `@brd: BRD.001.XXX`, `@prd: PRD.003.XXX` |
| `ai_dev_flow/METADATA_TAGGING_GUIDE.md` | 893 | `@brd: BRD-022` | `@brd: BRD.022.XXX` |

---

## Issue 4: Deprecated Format Documentation (KEEP - Correctly Marked)

These files contain OLD formats but are **correctly marked as deprecated** with ❌ symbols. **NO ACTION REQUIRED**.

| File | Purpose |
|------|---------|
| `README.md:340` | Shows deprecated `@brd: BRD-001:030` with ❌ |
| `.claude/skills/doc-*.md` | All show `@brd: BRD-017:001 ❌` as deprecated example |
| `ai_dev_flow/ID_NAMING_STANDARDS.md:389` | Documents old format as deprecated |

---

## Issue 5: Work Plans & Archive (IGNORE)

The following directories contain historical work plans and archived documents. These should NOT be modified as they represent point-in-time records:

- `work_plans/` - Historical planning documents
- `archive/` - Deprecated documentation

---

## Correct Format Reference (from TRACEABILITY.md)

| Tag | Format | Example |
|-----|--------|---------|
| `@brd` | `@brd: BRD.NNN.NNN` | `@brd: BRD.001.030` |
| `@prd` | `@prd: PRD.NNN.NNN` | `@prd: PRD.003.002` |
| `@ears` | `@ears: EARS.NNN.NNN` | `@ears: EARS.001.003` |
| `@bdd` | `@bdd: BDD.NNN.NNN` | `@bdd: BDD.003.007` |
| `@adr` | `@adr: ADR-NNN` | `@adr: ADR-033` |
| `@sys` | `@sys: SYS.NNN.NNN` | `@sys: SYS.008.001` |
| `@req` | `@req: REQ.NNN.NNN` | `@req: REQ.003.001` |
| `@impl` | `@impl: IMPL.NNN.NNN` | `@impl: IMPL.001.001` |
| `@ctr` | `@ctr: CTR-NNN` | `@ctr: CTR-001` |
| `@spec` | `@spec: SPEC-NNN` | `@spec: SPEC-003` |
| `@tasks` | `@tasks: TASKS.NNN.NNN` | `@tasks: TASKS.001.003` |
| `@iplan` | `@iplan: IPLAN-NNN` | `@iplan: IPLAN-001` |

---

## Recommended Actions

### Priority 1: ADR-REF → ADR-NNN (3 files)
```bash
# Files to update:
# - ai_dev_flow/METADATA_TAGGING_GUIDE.md
# - ai_dev_flow/METADATA_QUICK_REFERENCE.md
# - ai_dev_flow/AI_ASSISTANT_RULES.md
```

### Priority 2: Document-level tags → Add sub-IDs (4 files)
```bash
# Files to update:
# - ai_dev_flow/METADATA_VS_TRACEABILITY.md
# - ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
# - ai_dev_flow/METADATA_TAGGING_GUIDE.md (line 893)
```

### Priority 3: EARS template examples (5 files)
```bash
# Review if EARS internal ID format should be hyphenated or dotted
# Update templates if changing to dot format
```
