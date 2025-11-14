# Implementation Plan - Fix Documentation Inconsistencies

**Created**: 2025-11-14 12:35:00 EST
**Status**: Ready for Implementation
**Complexity**: 2/5 (Simple find-replace with validation)
**Estimated Time**: 3-4 hours implementation + 1-2 hours validation

---

## Objective

Fix inconsistencies and wrong references identified in comprehensive documentation review of the docs_flow_framework. Focus on critical layer numbering issues, deprecated notation, and terminology standardization across templates, skills, and guides.

---

## Context

### Review Scope

- Analyzed 98+ markdown files across entire framework
- Reviewed 28 templates (12 artifact types + traceability matrices)
- Checked 17 skills in `.claude/skills/`
- Validated against ID_NAMING_STANDARDS.md
- Scanned for broken references, external project references, and terminology inconsistencies

### Key Findings Summary

- **No broken internal references** - All links valid ✅
- **ID naming standards** - 100% compliant ✅
- **Template coverage** - Complete ✅
- **Issues Found**: 6 total (2 critical, 2 important, 2 minor)

### Critical Issues Identified

1. **Layer numbering inconsistency** - Confusing terminology in doc-flow/SKILL.md and project-init/SKILL.md
2. **Deprecated notation** - Using "XXX" instead of "NNN" in doc-flow/SKILL.md
3. **Terminology variations** - "16-layer" vs "12-layer" vs "13-layer" across multiple files
4. **External project references** - Hardcoded paths need parameterization (already in git status)

### Previous Work

- Recent commit (b08b616): "docs: Fix documentation references and inconsistencies"
- trace-check/SKILL.md already updated to v2.0.1 (2025-11-13) with correct terminology
- External reference cleanup work plan marked as completed

---

## Task List

### Analysis Tasks (Completed)

- [x] Map documentation structure and identify all templates
- [x] Check for broken internal references across all docs
- [x] Verify template consistency and naming conventions
- [x] Validate ID naming standards compliance
- [x] Check for external project references
- [x] Generate comprehensive findings report

### Implementation Tasks (Pending)

#### Phase 1: Critical Fixes (PRIORITY 1)

- [ ] Fix layer numbering in `.claude/skills/doc-flow/SKILL.md` (lines 360-377)
- [ ] Fix deprecated notation "XXX" to "NNN" in `.claude/skills/doc-flow/SKILL.md` (lines 218-221)
- [ ] Fix layer numbering in `.claude/skills/project-init/SKILL.md` (lines 37, 146, 468)
- [ ] Fix layer reference in `ai_dev_flow/IMPL/IMPL_IMPLEMENTATION_PLAN.md` (line 54)

#### Phase 2: Standardization (PRIORITY 2)

- [ ] Standardize to "16-layer architecture (Layers 0-15)" across all files
- [ ] Remove deprecated "12-layer" references (grep search)
- [ ] Remove deprecated "13-layer" references (grep search)
- [ ] Verify consistent "cumulative tags" terminology

#### Phase 3: Polish (PRIORITY 3)

- [ ] Review README.md files for consistency
- [ ] Spot-check 2-3 traceability matrix templates
- [ ] Verify all notation uses "NNN/YY" format

#### Phase 4: Validation

- [ ] Run grep for deprecated terms: "12-layer", "13-layer", "XXX notation"
- [ ] Cross-reference fixes against ID_NAMING_STANDARDS.md
- [ ] Generate validation report
- [ ] Run git diff to review all changes

---

## Detailed Issue Breakdown

### Issue 1: Layer Numbering in doc-flow/SKILL.md

**File**: `.claude/skills/doc-flow/SKILL.md`
**Lines**: 360-377
**Current Problem**: Table header says "16-layer hierarchy" but uses confusing "Layer 0-15" labeling
**Fix**: Change header to: "**Cumulative Tagging Table** (16 layers: Layer 0 through Layer 15):"
**Risk**: Low - documentation only
**Validation**: Visual inspection + AI assistant test query

### Issue 2: Deprecated Notation in doc-flow/SKILL.md

**File**: `.claude/skills/doc-flow/SKILL.md`
**Lines**: 218-221
**Current Problem**: Uses "XXX" and "YY" notation inconsistently
**Fix**: Update all instances to "NNN" and "YY" per ID_NAMING_STANDARDS.md
**Risk**: Low - terminology alignment
**Validation**: Cross-reference with ID_NAMING_STANDARDS.md

### Issue 3: Layer Numbering in project-init/SKILL.md

**File**: `.claude/skills/project-init/SKILL.md`
**Lines**: 37, 146, 468, 480
**Current Problem**: Says "13 documentation artifacts + 3 execution layers" but should be "14 documentation artifacts + 2 execution layers" (or clarify Layer 0 and Layer 15)
**Fix**: Update description to accurately reflect 16-layer architecture
**Risk**: Low - documentation clarity
**Validation**: Count artifact types and verify against TRACEABILITY.md

### Issue 4: Layer Reference in IMPL Plan

**File**: `ai_dev_flow/IMPL/IMPL_IMPLEMENTATION_PLAN.md`
**Line**: 54
**Current Problem**: References "12-layer artifact model"
**Fix**: Update to "16-layer architecture (Layers 0-15)"
**Risk**: Low - single reference update
**Validation**: Grep for remaining "12-layer" references

### Issue 5: Terminology Standardization

**Files**: Multiple
**Current Problem**: Mix of "16-layer", "12-layer", "13-layer" terminology
**Fix**: Standardize on "16-layer architecture (Layers 0-15)" everywhere
**Risk**: Low - find-replace with verification
**Validation**: Grep searches for all variants

### Issue 6: External Project References

**Files**: doc-flow/SKILL.md, project-init/SKILL.md, MULTI_PROJECT_SETUP_GUIDE.md
**Status**: Already identified in git status (modified files)
**Action**: Parameterize or add notes that paths are examples
**Risk**: Medium - affects example accuracy
**Validation**: Check parameterization strategy in DOMAIN_CONFIG files

---

## Implementation Guide

### Prerequisites

- Working directory: `/opt/data/docs_flow_framework/`
- Git status clean (commit current work first if needed)
- Backup recommendation: Create git branch for fixes
- Reference files:
  - `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md`

### Execution Steps

#### Step 1: Create Git Branch (Recommended)

```bash
cd /opt/data/docs_flow_framework
git checkout -b fix/documentation-inconsistencies
git status
```

#### Step 2: Fix Critical Issues - doc-flow/SKILL.md

```bash
# Read current file to understand context
cat .claude/skills/doc-flow/SKILL.md | head -400

# Edit lines 360-377 (layer numbering table header)
# Change: "**Cumulative Tagging Table** (16-layer hierarchy):"
# To: "**Cumulative Tagging Table** (16 layers: Layer 0 through Layer 15):"

# Edit lines 218-221 (notation consistency)
# Change all "XXX" to "NNN"
# Verify "YY" notation is consistent
```

#### Step 3: Fix Critical Issues - project-init/SKILL.md

```bash
# Read current file
cat .claude/skills/project-init/SKILL.md | head -500

# Edit lines 37, 146, 468 (layer count description)
# Verify layer count: Should be 16 layers (0-15)
# Update "13 documentation artifacts + 3 execution layers" to accurate count
```

#### Step 4: Fix IMPL Plan Layer Reference

```bash
# Edit line 54 in IMPL_IMPLEMENTATION_PLAN.md
# Change: "12-layer artifact model"
# To: "16-layer architecture (Layers 0-15)"
```

#### Step 5: Search and Replace Deprecated Terms

```bash
# Search for all instances of deprecated terms
grep -r "12-layer" /opt/data/docs_flow_framework/ --include="*.md"
grep -r "13-layer" /opt/data/docs_flow_framework/ --include="*.md"
grep -r "XXX notation" /opt/data/docs_flow_framework/ --include="*.md"

# Replace each instance with correct terminology
# Verify context before replacing
```

#### Step 6: Validation

```bash
# Check for remaining deprecated terms
grep -r "12-layer\|13-layer" /opt/data/docs_flow_framework/ --include="*.md"

# Verify NNN notation is used consistently
grep -r "XXX" /opt/data/docs_flow_framework/.claude/skills/ --include="*.md"

# Review all changes
git diff

# Check specific files
git diff .claude/skills/doc-flow/SKILL.md
git diff .claude/skills/project-init/SKILL.md
git diff ai_dev_flow/IMPL/IMPL_IMPLEMENTATION_PLAN.md
```

#### Step 7: Spot-Check Templates

```bash
# Verify 2-3 traceability matrix templates use correct notation
cat ai_dev_flow/BRD/BRD-TEMPLATE.md | grep -A 10 "Layer"
cat ai_dev_flow/IMPL/IMPL-TEMPLATE.md | grep -A 10 "Layer"
cat ai_dev_flow/TASKS/TASKS-TEMPLATE.md | grep -A 10 "Layer"
```

#### Step 8: Review README Files

```bash
# Check README consistency
cat ai_dev_flow/IMPL/README.md
cat ai_dev_flow/BDD/README.md

# Verify terminology is consistent
```

#### Step 9: Commit Changes

```bash
# Stage all changes
git add .

# Create descriptive commit
git commit -m "docs: Fix layer numbering and terminology inconsistencies

Fixes:
- Layer numbering in doc-flow/SKILL.md (lines 360-377)
- Deprecated 'XXX' notation to 'NNN' in doc-flow/SKILL.md (lines 218-221)
- Layer count in project-init/SKILL.md (lines 37, 146, 468)
- Layer reference in IMPL_IMPLEMENTATION_PLAN.md (line 54)
- Standardized to '16-layer architecture (Layers 0-15)' terminology

Validation:
- All deprecated '12-layer' and '13-layer' references removed
- ID notation consistent with ID_NAMING_STANDARDS.md
- No broken references introduced
- Templates verified for consistency

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push branch (optional)
git push origin fix/documentation-inconsistencies
```

### Verification Checklist

**Critical Fixes**:

- [ ] doc-flow/SKILL.md lines 360-377: Layer numbering table header updated
- [ ] doc-flow/SKILL.md lines 218-221: All "XXX" changed to "NNN"
- [ ] project-init/SKILL.md: Layer count description accurate
- [ ] IMPL_IMPLEMENTATION_PLAN.md: No "12-layer" reference

**Standardization**:

- [ ] No "12-layer" references remain (grep search returns empty)
- [ ] No "13-layer" references remain (grep search returns empty)
- [ ] All files use "16-layer architecture (Layers 0-15)" consistently
- [ ] All notation uses "NNN/YY" format (no "XXX")

**Template Verification**:

- [ ] BRD-TEMPLATE.md: Layer references correct
- [ ] IMPL-TEMPLATE.md: Layer references correct
- [ ] TASKS-TEMPLATE.md: Layer references correct
- [ ] Traceability sections consistent across templates

**README Verification**:

- [ ] README files follow consistent structure
- [ ] No deprecated terminology in README files
- [ ] References to layer counts are accurate

**Final Validation**:

- [ ] Git diff reviewed - all changes intentional
- [ ] No new issues introduced
- [ ] Cross-referenced against ID_NAMING_STANDARDS.md
- [ ] Test AI assistant query: "What is the layer structure of the framework?"

---

## Expected Outcomes

### Success Criteria

1. **Zero deprecated terms**: No "12-layer", "13-layer", or "XXX notation" references
2. **Consistent terminology**: All files use "16-layer architecture (Layers 0-15)"
3. **Accurate layer counts**: All descriptions match actual 16-layer structure
4. **Notation compliance**: All examples use "NNN/YY" format per ID_NAMING_STANDARDS.md
5. **No broken references**: All internal links remain valid
6. **Git history clean**: Descriptive commit message with validation notes

### Validation Report Format

```markdown
# Documentation Fix Validation Report

**Date**: YYYY-MM-DD
**Branch**: fix/documentation-inconsistencies

## Changes Summary
- Files modified: [count]
- Lines changed: [count]
- Deprecated terms removed: [count]

## Verification Results
- [x] Zero "12-layer" references
- [x] Zero "13-layer" references
- [x] Zero "XXX" notation references
- [x] All templates use "16-layer" terminology
- [x] All skills use correct layer numbering
- [x] No broken references introduced

## AI Assistant Test
Query: "What is the layer structure of the framework?"
Response: [Should correctly describe 16 layers (Layer 0-15)]

## Issues Found During Fix
- [None expected, or list any discovered issues]

## Recommendations
- [Any follow-up improvements identified]
```

---

## References

### Key Files Modified

1. `.claude/skills/doc-flow/SKILL.md` (lines 218-221, 360-377)
2. `.claude/skills/project-init/SKILL.md` (lines 37, 146, 468)
3. `ai_dev_flow/IMPL/IMPL_IMPLEMENTATION_PLAN.md` (line 54)
4. Various README.md files (terminology updates)

### Reference Documentation

- **Authoritative Standards**: `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
- **Traceability Reference**: `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md`
- **Complete Example**: `/opt/data/docs_flow_framework/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md`
- **Updated Skill**: `/opt/data/docs_flow_framework/.claude/skills/trace-check/SKILL.md` (v2.0.1)

### Related Work

- Previous commit: b08b616 "docs: Fix documentation references and inconsistencies"
- Git status shows: Modified doc-flow/SKILL.md, project-init/SKILL.md, IMPL plan
- External reference cleanup: Already addressed in separate work plan

### Analysis Artifacts

Two comprehensive reports saved to framework root:

1. `DIRECTORY_STRUCTURE_MAP.md` - Complete framework structure map
2. `REFERENCE_PATTERNS_ANALYSIS.md` - Reference pattern inventory

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking references | Very Low | Medium | All changes are terminology only, no path/link changes |
| Introducing typos | Low | Low | Git diff review before commit, validation grep searches |
| Missing deprecated terms | Low | Low | Comprehensive grep searches in validation phase |
| Inconsistent updates | Very Low | Low | Following checklist ensures all instances updated |

**Overall Risk**: LOW - Documentation-only changes with comprehensive validation

---

## Notes

### Files Requiring NO Changes ✅

- `/opt/data/docs_flow_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` - Authoritative reference
- `/opt/data/docs_flow_framework/ai_dev_flow/TRACEABILITY.md` - Already correct
- `/opt/data/docs_flow_framework/ai_dev_flow/COMPLETE_TAGGING_EXAMPLE.md` - Reference implementation
- `/opt/data/docs_flow_framework/.claude/skills/trace-check/SKILL.md` - Recently updated (v2.0.1)

### External Project References (Issue #4)

Already identified in git status. These are INTENTIONAL setup examples in:

- `MULTI_PROJECT_SETUP_GUIDE.md`
- `MULTI_PROJECT_QUICK_REFERENCE.md`
- `ai_dev_flow/IPLAN/README.md`

Action: Add parameterization notes or clarify these are examples (separate task if needed)

### Template Completeness

All 12 artifact types have templates:

- ADR, BDD, BRD, CTR, EARS, IMPL, IPLAN, PRD, REQ, SPEC, SYS, TASKS ✅
- Traceability matrix templates exist for all types ✅
- README files in all artifact directories ✅

### Framework Status

**Production-ready** with only minor inconsistencies requiring fixes. Core architecture is sound:

- No broken references
- 100% ID naming compliance
- Complete template coverage
- Working traceability system

---

## Implementation Commands Summary

```bash
# 1. Setup
cd /opt/data/docs_flow_framework
git checkout -b fix/documentation-inconsistencies

# 2. Fix doc-flow/SKILL.md
# Edit lines 360-377 (table header)
# Edit lines 218-221 (XXX to NNN)

# 3. Fix project-init/SKILL.md
# Edit lines 37, 146, 468 (layer count)

# 4. Fix IMPL plan
# Edit line 54 (12-layer to 16-layer)

# 5. Validate
grep -r "12-layer\|13-layer" . --include="*.md"
grep -r "XXX" .claude/skills/ --include="*.md"

# 6. Review and commit
git diff
git add .
git commit -m "docs: Fix layer numbering and terminology inconsistencies"

# 7. Optional: Push branch
git push origin fix/documentation-inconsistencies
```

---

**END OF IMPLEMENTATION PLAN**

To continue in new context:

1. Open new Claude Code session
2. Run: `cat /opt/data/docs_flow_framework/work_plans/fix-documentation-inconsistencies_20251114_123500.md`
3. Say: "Implement this plan"
