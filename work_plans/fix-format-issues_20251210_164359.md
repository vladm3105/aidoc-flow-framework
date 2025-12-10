# Implementation Plan - Fix Format Issues

**Created**: 2025-12-10 16:43:59 EST
**Status**: Ready for Implementation

## Objective

Fix remaining format inconsistencies in the docs_flow_framework documentation, including malformed "regulatoryTION" typos, old category-coded IDs, deprecated TASKS:PHASE format, and incorrect @threshold format.

## Context

After the recent unified format migration (`TYPE.NNN.NNN`), a comprehensive review identified several remaining format inconsistencies that need to be addressed. The standard reference is `ai_dev_flow/ID_NAMING_STANDARDS.md`.

### Key Decisions
- `@icon: TASKS-NNN:ContractName` format is INTENTIONAL (colon separates doc ID from contract name)
- Template placeholders like `@adr: ADR-NNN` are expected and should remain
- Archived files should NOT be modified (historical records)

## Task List

### Completed
- [x] Scan all documents for old category-coded ID formats (REQ-ML-XXX, etc.)
- [x] Check for inconsistent traceability tag formats
- [x] Find malformed tags and typos in templates
- [x] Verify traceability matrix format consistency
- [x] Check IPLAN templates for deprecated formats
- [x] Generate comprehensive report of all issues found

### Pending
- [ ] Fix HIGH priority: "regulatoryTION" typos (10 locations)
- [ ] Fix MEDIUM priority: Old category-coded IDs (4 locations)
- [ ] Fix MEDIUM priority: Deprecated TASKS:PHASE format (4 files)
- [ ] Fix MEDIUM priority: Old @threshold format (1 file)
- [ ] Validate all fixes with grep commands
- [ ] Commit changes

## Implementation Guide

### Prerequisites
- Review full report at: `tmp/format_review_report_20251210.md`
- Reference standard: `ai_dev_flow/ID_NAMING_STANDARDS.md`

### Execution Steps

#### Step 1: Fix "regulatoryTION" Typos (HIGH Priority)

| File | Line | Current | Fix To |
|------|------|---------|--------|
| `ai_dev_flow/PRD/PRD_VALIDATION_RULES.md` | 251 | `MISSING regulatoryTION:` | `MISSING SECTION:` |
| `ai_dev_flow/PRD/PRD_VALIDATION_RULES.md` | 252 | `MISSING regulatoryTION:` | `MISSING SECTION:` |
| `ai_dev_flow/SPEC/SPEC_VALIDATION_RULES.md` | 106 | `sys: "SYS-NNN:regulatoryTION-ID"` | `sys: "SYS-NNN"` |
| `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md` | 221 | `sys: "SYS-NNN:regulatoryTION-ID"` | `sys: "SYS-NNN"` |
| `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md` | 613 | `@spec: SPEC-NNN:regulatoryTION` | `@spec: SPEC-NNN` |
| `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md` | 619 | `@ctr: CTR-NNN:regulatoryTION` | `@ctr: CTR-NNN` |
| `ai_dev_flow/IPLAN/README.md` | 140 | `@spec: SPEC-NNN:regulatoryTION` | `@spec: SPEC-NNN` |
| `ai_dev_flow/IPLAN/README.md` | 148 | `@ctr: CTR-NNN:regulatoryTION` | `@ctr: CTR-NNN` |
| `ai_dev_flow/IPLAN/README.md` | 1332 | `@spec: SPEC-___:regulatoryTION` | `@spec: SPEC-___` |
| `ai_dev_flow/IPLAN/README.md` | 1335 | `@ctr: CTR-___:regulatoryTION` | `@ctr: CTR-___` |

#### Step 2: Fix Old Category-Coded IDs (MEDIUM Priority)

| File | Line | Current | Fix To |
|------|------|---------|--------|
| `ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md` | 281 | `REQ-AUTH-001.md` | `REQ-001_authentication.md` |
| `ai_dev_flow/PROJECT_SETUP_GUIDE.md` | 743 | `REQ-MLR-032` | `REQ-032` |
| `ai_dev_flow/PROJECT_SETUP_GUIDE.md` | 763 | `REQ-MLR-032` | `REQ-032` |
| `ai_dev_flow/PROJECT_SETUP_GUIDE.md` | 773 | `REQ-MLR-046` | `REQ-046` |
| `ai_dev_flow/PROJECT_SETUP_GUIDE.md` | 746 | `@ears: EARS.MLR.001` | `@ears: EARS.001.001` |

#### Step 3: Fix Deprecated TASKS:PHASE Format (MEDIUM Priority)

| File | Line | Current | Fix To |
|------|------|---------|--------|
| `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md` | 383 | `TASKS-NNN:PHASE-X.Y` | `TASKS-NNN` |
| `ai_dev_flow/IPLAN/IPLAN_VALIDATION_RULES.md` | 270 | `TASKS-NNN:PHASE-X.Y` | `TASKS-NNN` |
| `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md` | 614 | `@tasks: TASKS-NNN:PHASE-X.Y` | `@tasks: TASKS-NNN` |
| `ai_dev_flow/IPLAN/README.md` | 141 | `@tasks: TASKS-NNN:PHASE-X.Y` | `@tasks: TASKS-NNN` |

#### Step 4: Fix Old @threshold Format (MEDIUM Priority)

| File | Line | Current | Fix To |
|------|------|---------|--------|
| `ai_dev_flow/SYS/SYS-TEMPLATE.md` | 786 | `@threshold: PRD-003` | `@threshold: PRD.003` |

### Verification

```bash
# Verify no regulatoryTION remains
grep -rn "regulatoryTION" ai_dev_flow/
# Expected: No matches

# Verify no old category-coded IDs
grep -rn "REQ-[A-Z]\{2,\}-[0-9]" ai_dev_flow/
# Expected: No matches (or only archived files)

# Verify no TASKS:PHASE format
grep -rn "TASKS-NNN:PHASE" ai_dev_flow/
# Expected: No matches

# Verify @threshold uses dots
grep -rn "@threshold: PRD-" ai_dev_flow/
# Expected: No matches
```

## References

- Full report: `tmp/format_review_report_20251210.md`
- Standard reference: `ai_dev_flow/ID_NAMING_STANDARDS.md`
- Traceability guide: `ai_dev_flow/TRACEABILITY.md`

---

**To continue implementation in a new context:**
1. Open new Claude Code session
2. Run: `cat /opt/data/docs_flow_framework/work_plans/fix-format-issues_20251210_164359.md`
3. Say: "Implement this plan"
