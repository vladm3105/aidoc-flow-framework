# Implementation Plan - Fix Framework Format Issues

**Created**: 2025-12-10 17:13:36 EST
**Status**: Ready for Implementation

## Objective

Fix 4 critical format/consistency issues identified in the SDD framework documentation review:
1. "conregulatoryutive" typo (should be "consecutive") - 17 occurrences
2. Broken REQ-TEMPLATE-V3.md references - 10 occurrences
3. NFR terminology (should be "quality attributes") - 2 files
4. Missing YAML frontmatter in example files - 5 files

## Context

A comprehensive review of the `ai_dev_flow/` directory was conducted on 2025-12-10. The framework has 193 files across 12 documentation layers. Most patterns are correct, but 4 issues require fixes.

**Review Report Location**: `tmp/framework_review_report_2025-12-10.md`

**Verified Correct**:
- No deprecated TASKS_PLANS references
- No old ib-async/ib-insync library names
- Layer numbering (1-12) consistent
- Traceability tag formats correct
- @threshold format correct
- ID naming standards compliant

## Task List

### Completed
- [x] Search for deprecated NFR terminology (should be QA)
- [x] Check for old format patterns in templates
- [x] Verify layer numbering consistency
- [x] Check traceability tag formats (@brd, @prd, etc.)
- [x] Verify YAML frontmatter consistency
- [x] Check for deprecated TASKS_PLANS references
- [x] Verify threshold format consistency (X.X format)
- [x] Check ID naming standards compliance
- [x] Review cross-document references
- [x] Generate summary report of findings

### Pending
- [ ] Fix "conregulatoryutive" typo across all files
- [ ] Fix REQ-TEMPLATE-V3.md references to REQ-TEMPLATE.md
- [ ] Replace NFR with "quality attributes" in active files
- [ ] Add YAML frontmatter to example files (optional)
- [ ] Commit changes with descriptive message

### Notes
- Archived files (`REQ/archived/`) contain NFR references intentionally - do not modify
- The `TRACEABILITY.md:473` NFR reference is a deprecation note - keep as documentation

## Implementation Guide

### Prerequisites
- Working directory: `/opt/data/docs_flow_framework`
- Backup recommended before bulk changes

### Execution Steps

**Step 1: Fix "conregulatoryutive" typo (HIGH PRIORITY)**
```bash
cd /opt/data/docs_flow_framework
find ai_dev_flow -name "*.md" -exec sed -i 's/conregulatoryutive/consecutive/g' {} \;
```

Affected files:
- `REQ/README.md` (lines 193, 365)
- `REQ/REQ-TEMPLATE.md` (lines 1012, 1013)
- `REQ/archived/REQ-TEMPLATE-V2-ARCHIVED.md` (lines 742, 743)
- `REQ/examples/TRACEABILITY_MATRIX_REQ_EXAMPLE.md` (line 39)
- `REQ/examples/api/REQ-001_api_integration_example.md` (7 occurrences)
- `CTR/CTR-TEMPLATE.md` (lines 240, 300, 448)
- `scripts/README.md` (line 184)

**Step 2: Fix REQ-TEMPLATE-V3.md references (HIGH PRIORITY)**
```bash
cd /opt/data/docs_flow_framework
sed -i 's/REQ-TEMPLATE-V3\.md/REQ-TEMPLATE.md/g' ai_dev_flow/REQ/REQ_VALIDATION_RULES.md
sed -i 's/REQ-TEMPLATE-V3\.md/REQ-TEMPLATE.md/g' ai_dev_flow/REQ/REQ-TEMPLATE.md
```

**Step 3: Fix NFR terminology (MEDIUM PRIORITY)**
```bash
cd /opt/data/docs_flow_framework
sed -i 's/other NFRs/other quality attributes/g' ai_dev_flow/EARS/README.md
sed -i 's/, NFRs,/, quality attributes,/g' ai_dev_flow/TRACEABILITY.md
```

**Step 4: Add YAML frontmatter to example files (LOW PRIORITY - OPTIONAL)**
Files needing frontmatter:
- `ai_dev_flow/REQ/examples/auth/REQ-003_access_control_example.md`
- `ai_dev_flow/REQ/examples/data/REQ-002_data_validation_example.md`
- `ai_dev_flow/SCHEMA_TEMPLATE_GUIDE.md`
- `ai_dev_flow/index.md`
- `ai_dev_flow/BRD/prompt.md`

### Verification

After each step, verify changes:
```bash
# Verify typo fix
grep -rn "conregulatoryutive" ai_dev_flow/ --include="*.md"
# Should return empty

# Verify REQ-TEMPLATE-V3 fix
grep -rn "REQ-TEMPLATE-V3" ai_dev_flow/ --include="*.md"
# Should return empty

# Verify NFR fix (excluding archived and deprecation notes)
grep -rn "NFR" ai_dev_flow/ --include="*.md" | grep -v "archived/" | grep -v "NFR tag deprecated"
# Should return empty or only acceptable references
```

### Commit Changes
```bash
git add -A
git commit -m "fix(docs): correct typos and broken references in SDD framework

- Fix 'conregulatoryutive' typo to 'consecutive' (17 occurrences)
- Update REQ-TEMPLATE-V3.md references to REQ-TEMPLATE.md (10 refs)
- Replace NFR with 'quality attributes' terminology (2 files)

Fixes identified in framework review 2025-12-10

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## References

- **Review Report**: `tmp/framework_review_report_2025-12-10.md`
- **Framework Root**: `ai_dev_flow/`
- **Main Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **ID Standards**: `ai_dev_flow/ID_NAMING_STANDARDS.md`

## Estimated Time

- Steps 1-3: ~5 minutes (automated)
- Step 4: ~15 minutes (manual YAML additions)
- Verification: ~5 minutes
- **Total**: 10-25 minutes depending on optional step
