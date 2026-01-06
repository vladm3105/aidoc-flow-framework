# Framework Format Review Report

**Date**: 2025-12-10
**Scope**: `/opt/data/docs_flow_framework/ai_dev_flow/` and `.claude/skills/`
**Standard Reference**: `ai_dev_flow/ID_NAMING_STANDARDS.md`

---

## Executive Summary

| Category | Issues Found | Severity |
|----------|-------------|----------|
| Malformed Tags (typos) | 10 | HIGH |
| Old Category-Coded IDs | 4 | MEDIUM |
| Deprecated Format References | 12 | MEDIUM |
| Inconsistent Tag Formats | 8 | LOW |
| Archived Files (expected) | 5 | INFO |

---

## HIGH Priority Issues

### 1. Malformed "regulatoryTION" Typos

**Description**: Corrupted text "regulatoryTION" appears in multiple files where "SECTION" or nothing was intended.

| File | Line | Current | Fix |
|------|------|---------|-----|
| `PRD/PRD_VALIDATION_RULES.md` | 251 | `MISSING regulatoryTION: ## 6.` | `MISSING SECTION: ## 6.` |
| `PRD/PRD_VALIDATION_RULES.md` | 252 | `MISSING regulatoryTION: ## 8.` | `MISSING SECTION: ## 8.` |
| `SPEC/SPEC_VALIDATION_RULES.md` | 106 | `sys: "SYS-NNN:regulatoryTION-ID"` | `sys: "SYS-NNN"` |
| `SPEC/SPEC_CREATION_RULES.md` | 221 | `sys: "SYS-NNN:regulatoryTION-ID"` | `sys: "SYS-NNN"` |
| `IPLAN/IPLAN-TEMPLATE.md` | 613 | `@spec: SPEC-NNN:regulatoryTION` | `@spec: SPEC-NNN` |
| `IPLAN/IPLAN-TEMPLATE.md` | 619 | `@ctr: CTR-NNN:regulatoryTION` | `@ctr: CTR-NNN` |
| `IPLAN/README.md` | 140 | `@spec: SPEC-NNN:regulatoryTION` | `@spec: SPEC-NNN` |
| `IPLAN/README.md` | 148 | `@ctr: CTR-NNN:regulatoryTION` | `@ctr: CTR-NNN` |
| `IPLAN/README.md` | 1332 | `@spec: SPEC-___:regulatoryTION` | `@spec: SPEC-___` |
| `IPLAN/README.md` | 1335 | `@ctr: CTR-___:regulatoryTION` | `@ctr: CTR-___` |

---

## MEDIUM Priority Issues

### 2. Old Category-Coded ID Formats (DEPRECATED)

**Standard**: Use `REQ-NNN` not `REQ-{CATEGORY}-NNN`

| File | Line | Current Format | Correct Format |
|------|------|----------------|----------------|
| `TOOL_OPTIMIZATION_GUIDE.md` | 281 | `REQ-AUTH-001.md` | `REQ-001_authentication.md` |
| `PROJECT_SETUP_GUIDE.md` | 743 | `REQ-MLR-032` | `REQ-032` |
| `PROJECT_SETUP_GUIDE.md` | 763 | `REQ-MLR-032` | `REQ-032` |
| `PROJECT_SETUP_GUIDE.md` | 773 | `REQ-MLR-046` | `REQ-046` |

### 3. Old Category-Coded Feature ID in Tags

**Standard**: Use `EARS.NNN.NNN` not `EARS.{CATEGORY}.NNN`

| File | Line | Current Format | Correct Format |
|------|------|----------------|----------------|
| `PROJECT_SETUP_GUIDE.md` | 746 | `@ears: EARS.MLR.001` | `@ears: EARS.001.001` |

### 4. Deprecated TASKS Phase Format

**Standard**: Use `@tasks: TASKS-NNN` or `@tasks: TASKS.NNN.NNN`, NOT `TASKS-NNN:PHASE-X.Y`

| File | Line | Current Format | Correct Format |
|------|------|----------------|----------------|
| `IPLAN/IPLAN_CREATION_RULES.md` | 383 | `TASKS-NNN:PHASE-X.Y` | `TASKS-NNN` or `TASKS.NNN.NNN` |
| `IPLAN/IPLAN_VALIDATION_RULES.md` | 270 | `TASKS-NNN:PHASE-X.Y` | `TASKS-NNN` or `TASKS.NNN.NNN` |
| `IPLAN/IPLAN-TEMPLATE.md` | 614 | `@tasks: TASKS-NNN:PHASE-X.Y` | `@tasks: TASKS-NNN` |
| `IPLAN/README.md` | 141 | `@tasks: TASKS-NNN:PHASE-X.Y` | `@tasks: TASKS-NNN` |

### 5. Old @threshold Format

**Standard**: Use `@threshold: PRD.NNN.category.key` (dot separator)

| File | Line | Current Format | Correct Format |
|------|------|----------------|----------------|
| `SYS/SYS-TEMPLATE.md` | 786 | `@threshold: PRD-003` | `@threshold: PRD.003.category.key` |

---

## LOW Priority Issues

### 6. @icon Tag Format (Intentionally Uses Colon)

**Note**: The `@icon` tag format `@icon: TASKS-NNN:ContractName` is **intentional** per `ID_NAMING_STANDARDS.md` line 182. The colon separates the document ID from the contract name. This is NOT an error.

**Files using correct format**:
- `TASKS/TASKS-TEMPLATE.md:1286`
- `TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md` (multiple lines)
- `TRACEABILITY.md` (multiple lines)
- `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (multiple lines)
- `.claude/skills/doc-flow/SHARED_CONTENT.md:191`

### 7. Template Placeholders (Expected - Not Errors)

The following are template placeholders and should remain as-is:

- `@adr: ADR-NNN` (in template files - placeholder for user to fill)
- `@spec: SPEC-NNN` (in template files - placeholder for user to fill)
- `@ctr: CTR-NNN` (in template files - placeholder for user to fill)

---

## INFO: Archived Files

The following files contain deprecated formats but are intentionally archived:

| File | Status |
|------|--------|
| `REQ/archived/REQ-TEMPLATE-V1-ARCHIVED.md` | Archived - Layer 4 designation (should be Layer 7) |
| `REQ/archived/REQ-TEMPLATE-V2-ARCHIVED.md` | Archived - Uses `TYPE-NNN:NNN` format (deprecated 2025-11-19) |

These files serve as historical reference and should NOT be modified.

---

## Format Standards Summary

### Unified Feature ID Format (MANDATORY)

```
TYPE.NNN.NNN
```

**Examples**:
- `@brd: BRD.017.001`
- `@req: REQ.003.015`
- `@tasks: TASKS.001.003`

### Document ID Format

```
TYPE-NNN_{descriptive_slug}.md
```

**Examples**:
- `REQ-001_data_validation.md`
- `ADR-033_caching_strategy.md`

### Tag Formats by Type

| Tag | Simple Format | Feature-Level Format |
|-----|---------------|---------------------|
| `@brd` | `@brd: BRD-001` | `@brd: BRD.001.030` |
| `@prd` | `@prd: PRD-003` | `@prd: PRD.003.002` |
| `@ears` | `@ears: EARS-001` | `@ears: EARS.001.003` |
| `@bdd` | `@bdd: BDD-015` | `@bdd: BDD.015.001` |
| `@adr` | `@adr: ADR-033` | N/A (document-level only) |
| `@sys` | `@sys: SYS-001` | `@sys: SYS.001.012` |
| `@req` | `@req: REQ-045` | `@req: REQ.045.001` |
| `@spec` | `@spec: SPEC-003` | N/A (document-level only) |
| `@tasks` | `@tasks: TASKS-001` | `@tasks: TASKS.001.003` |
| `@iplan` | `@iplan: IPLAN-001` | N/A (document-level only) |
| `@ctr` | `@ctr: CTR-001` | N/A (document-level only) |
| `@icon` | `@icon: TASKS-001:ContractName` | N/A (special format) |
| `@threshold` | `@threshold: PRD.NNN.category.key` | N/A (registry reference) |

### Invalid Formats (DO NOT USE)

- `@brd: BRD-017:001` (colon separator between document and feature)
- `REQ-ML-XXX`, `REQ-API-XXX`, `REQ-AUTH-XXX` (category-coded IDs)
- `@nfr:`, `@fr:`, `@contract:`, `@tests:` (deprecated tags)
- `EARS.MLR.001` (category in feature ID)
- `TASKS-NNN:PHASE-X.Y` (phase notation in tasks)

---

## Validation Commands

```bash
# Check for regulatoryTION
grep -rn "regulatoryTION" ai_dev_flow/

# Check for old category-coded IDs
grep -rn "REQ-[A-Z]\{2,\}-[0-9]" ai_dev_flow/

# Check for deprecated tag formats
grep -rn "@nfr:" ai_dev_flow/
grep -rn "TASKS-NNN:PHASE" ai_dev_flow/
```

---

**Report Generated**: 2025-12-10
**Next Action**: Fix HIGH priority issues first, then MEDIUM priority
