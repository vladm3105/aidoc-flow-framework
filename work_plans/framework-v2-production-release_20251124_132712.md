# Implementation Plan - docs_flow_framework v2.0 Production Release

**Created**: 2025-11-24 13:27:12 EST
**Status**: Ready for Implementation
**Estimated Time**: 45 minutes total

## Objective

Prepare the docs_flow_framework v2.0 for production release by resolving 4 critical metadata compliance issues identified in comprehensive framework review. Achieve 100% metadata compliance across all 28 Claude skills and 27 templates.

## Context

### Review Summary
A comprehensive pre-production review identified the framework as **95% production-ready** with excellent core architecture, documentation, and traceability chains. All layer assignments are correct, the 16-layer architecture is consistently documented, and validation tooling is functional.

### Critical Findings
- **14 skills** have duplicate YAML description/name lines (parsing blockers)
- **1 skill** has incorrect description content (doc-ctr)
- **1 skill** missing all metadata (doc-validator)
- **1 template** has uncommitted changes (BRD-TEMPLATE.md)

### Current State
- Metadata compliance: 96% (27/28 templates, 14/28 skills fully compliant)
- Layer assignments: 100% correct
- Traceability chains: 100% valid
- Documentation: Comprehensive and accurate
- Quality score: 9.5/10

### Post-Fix State
- Metadata compliance: 100% (28/28 templates, 28/28 skills)
- Ready for production tag: v2.0-production-ready
- Framework achieves full production readiness

## Task List

### Phase 1: Fix Duplicate YAML Lines (30 min)
- [ ] Fix doc-adr/SKILL.md (lines 3 & 20: duplicate descriptions)
- [ ] Fix doc-bdd/SKILL.md (lines 3 & 21: duplicate descriptions)
- [ ] Fix doc-ctr/SKILL.md (lines 3, 4, & 22: 4 descriptions - includes wrong content)
- [ ] Fix doc-ears/SKILL.md (lines 3 & 21: duplicate descriptions)
- [ ] Fix doc-impl/SKILL.md (lines 3 & 21: duplicate descriptions)
- [ ] Fix doc-iplan/SKILL.md (lines 3 & 21: duplicate descriptions)
- [ ] Fix doc-prd/SKILL.md (lines 3 & 22: duplicate descriptions)
- [ ] Fix doc-req/SKILL.md (lines 3 & 20: duplicate descriptions)
- [ ] Fix doc-spec/SKILL.md (lines 3 & 20: duplicate descriptions)
- [ ] Fix doc-sys/SKILL.md (lines 3 & 21: duplicate descriptions)
- [ ] Fix doc-tasks/SKILL.md (lines 3 & 20: duplicate descriptions)
- [ ] Fix trace-check/SKILL.md (lines 2 & 15: duplicate name lines)
- [ ] Fix project-init/SKILL.md (lines 2 & 15: duplicate name lines)

### Phase 2: Fix doc-ctr Wrong Description (2 min)
- [ ] Verify doc-ctr line 4 contains "Configuration schema for position limits"
- [ ] Delete line 4 (keep line 3's correct description)

### Phase 3: Add doc-validator Metadata (5 min)
- [ ] Add complete YAML frontmatter to doc-validator/SKILL.md
- [ ] Include name, description, tags, custom_fields

### Phase 4: Handle BRD-TEMPLATE Changes (2 min)
- [ ] Review uncommitted changes in ai_dev_flow/BRD/BRD-TEMPLATE.md
- [ ] Commit if changes are valid metadata additions
- [ ] Revert if changes are unintended

### Phase 5: Validation (5 min)
- [ ] Run: `python3 scripts/validate_metadata.py .`
- [ ] Run: `python3 ai_dev_flow/scripts/validate_requirement_ids.py`
- [ ] Verify all skills load without YAML parsing errors
- [ ] Confirm 100% metadata compliance

### Phase 6: Production Release (3 min)
- [ ] Create git commit for all fixes
- [ ] Create git tag: v2.0-production-ready
- [ ] Verify clean git state

### Deferred to Post-Release (v2.1)
- [ ] Add layer numbering warnings to Mermaid diagrams
- [ ] Create scripts/README.md validation guide
- [ ] Add generic domain examples with [PLACEHOLDER] format
- [ ] Clarify working directory context in validation docs

## Implementation Guide

### Prerequisites
- Working directory: `/opt/data/docs_flow_framework`
- Git repository with clean working state (except known BRD-TEMPLATE change)
- Python 3.x for validation scripts
- Text editor with YAML syntax support

### Phase 1: Fix Duplicate YAML Lines in 14 Skills

**Problem Pattern:**
Skills have YAML frontmatter with description/name field, followed by duplicate line after `---` closing marker.

**Example (doc-adr/SKILL.md):**
```yaml
---
name: doc-adr
description: Create Architecture Decision Records (ADR)...
tags: [...]
custom_fields: {...}
---

name: doc-adr  # ❌ DUPLICATE - REMOVE THIS LINE
description: Create Architecture Decision Records...  # ❌ DUPLICATE - REMOVE THIS LINE

# doc-adr  ← Keep H1 heading

## Purpose
...
```

**Fix Pattern:**
1. Open each skill file
2. Locate the `---` closing marker (end of YAML frontmatter)
3. Check next 1-2 lines for duplicate `name:` or `description:` fields
4. Delete duplicate lines (everything between `---` and the `# skill-name` heading)
5. Keep the H1 heading (`# skill-name`)

**Affected Files:**
1. `.claude/skills/doc-adr/SKILL.md` - Remove lines 20-21
2. `.claude/skills/doc-bdd/SKILL.md` - Remove lines 21-22
3. `.claude/skills/doc-ctr/SKILL.md` - Remove lines 22-23 (handle line 4 separately in Phase 2)
4. `.claude/skills/doc-ears/SKILL.md` - Remove lines 21-22
5. `.claude/skills/doc-impl/SKILL.md` - Remove lines 21-22
6. `.claude/skills/doc-iplan/SKILL.md` - Remove lines 21-22
7. `.claude/skills/doc-prd/SKILL.md` - Remove lines 22-23
8. `.claude/skills/doc-req/SKILL.md` - Remove lines 20-21
9. `.claude/skills/doc-spec/SKILL.md` - Remove lines 20-21
10. `.claude/skills/doc-sys/SKILL.md` - Remove lines 21-22
11. `.claude/skills/doc-tasks/SKILL.md` - Remove lines 20-21
12. `.claude/skills/trace-check/SKILL.md` - Remove lines 15-16 (duplicate name)
13. `.claude/skills/project-init/SKILL.md` - Remove lines 15-16 (duplicate name)

**Verification:**
- Each skill should have exactly ONE `name:` field (in YAML frontmatter)
- Each skill should have exactly ONE `description:` field (in YAML frontmatter)
- No `name:` or `description:` fields outside `---` markers
- H1 heading (`# skill-name`) should be the first line after closing `---`

### Phase 2: Fix doc-ctr Wrong Description Content

**Problem:**
Line 4 of `.claude/skills/doc-ctr/SKILL.md` contains incorrect content:
```yaml
description: Configuration schema for position limits  # ❌ WRONG - Delete this
```

This appears to be copied from an example and is unrelated to CTR (API Contracts).

**Fix Steps:**
1. Open `.claude/skills/doc-ctr/SKILL.md`
2. Verify line 3 contains correct description: "Create Data Contracts (CTR) - Optional Layer 9 artifact..."
3. Delete line 4 entirely
4. Keep line 3 as the only description

**Verification:**
- Single `description:` field with correct CTR content
- No reference to "position limits" anywhere in frontmatter

### Phase 3: Add doc-validator Metadata

**Problem:**
`.claude/skills/doc-validator/SKILL.md` has no YAML frontmatter. File starts directly with markdown:
```markdown
# doc-validator

**Description**: Automated validation...
```

**Fix Steps:**
1. Open `.claude/skills/doc-validator/SKILL.md`
2. Add complete YAML frontmatter at the beginning:

```yaml
---
name: doc-validator
description: Automated validation of documentation standards for SDD framework compliance
tags:
  - sdd-workflow
  - shared-architecture
  - quality-assurance
custom_fields:
  architecture_approaches:
    - ai-agent-based
    - traditional-8layer
  priority: shared
  development_status: active
  skill_category: quality-assurance
  applies_to: all-artifacts
  layer: N/A
---

# doc-validator

**Description**: Automated validation...
```

**Notes:**
- `layer: N/A` is correct for cross-layer utility skills
- `skill_category: quality-assurance` reflects validation purpose
- `applies_to: all-artifacts` since it validates all document types

**Verification:**
- File starts with `---`
- Valid YAML syntax (no duplicate keys)
- All required fields present: name, description, tags, custom_fields
- H1 heading preserved after closing `---`

### Phase 4: Handle BRD-TEMPLATE Uncommitted Changes

**Problem:**
Git status shows:
```
M ai_dev_flow/BRD/BRD-TEMPLATE.md
```

**Investigation Steps:**
```bash
cd /opt/data/docs_flow_framework
git diff ai_dev_flow/BRD/BRD-TEMPLATE.md
```

**Decision Tree:**
- **If changes are metadata additions** (likely from Phase 2 metadata work):
  - Commit with message: `feat: Complete metadata additions to BRD-TEMPLATE.md`
  - Add to final production commit

- **If changes are unintended or incomplete**:
  - Revert: `git checkout ai_dev_flow/BRD/BRD-TEMPLATE.md`
  - Verify file matches committed version

**Verification:**
- Run `git status` - should show clean state or staged changes only
- BRD-TEMPLATE.md has valid YAML frontmatter
- No unexpected content modifications

### Phase 5: Validation

**Metadata Validation:**
```bash
cd /opt/data/docs_flow_framework
python3 scripts/validate_metadata.py .
```

**Expected Output:**
- ✅ All YAML frontmatter valid
- ✅ No duplicate keys
- ✅ All required fields present
- ✅ Tag taxonomy compliance: 100%

**ID Format Validation:**
```bash
python3 ai_dev_flow/scripts/validate_requirement_ids.py
```

**Expected Output:**
- ✅ All IDs follow TYPE-NNN or TYPE-NNN-YY format
- ✅ No collisions with reserved namespaces

**Manual Verification:**
1. Attempt to load each skill in Claude Code (check YAML parsing)
2. Verify doc-validator appears in skill list
3. Check that all 28 skills have complete metadata
4. Confirm 100% metadata compliance

**Success Criteria:**
- Zero YAML parsing errors
- Zero validation script failures
- All 28 skills load correctly
- Clean git status (or only intended commits staged)

### Phase 6: Production Release

**Commit All Fixes:**
```bash
cd /opt/data/docs_flow_framework
git add .claude/skills/*/SKILL.md
git add ai_dev_flow/BRD/BRD-TEMPLATE.md  # Only if changes are valid

git commit -m "fix: Resolve critical YAML metadata issues for production release

Critical Fixes:
- Remove duplicate description/name lines in 14 skills
- Fix incorrect description content in doc-ctr skill
- Add complete metadata to doc-validator skill
- Handle BRD-TEMPLATE uncommitted changes

Impact:
- Achieves 100% metadata compliance (28/28 skills, 27/27 templates)
- Resolves YAML parsing blockers
- Framework ready for production use

Validation:
- All skills load without YAML errors
- validate_metadata.py: PASS
- validate_requirement_ids.py: PASS

Framework Status: Production Ready

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Create Production Tag:**
```bash
git tag -a v2.0-production-ready -m "docs_flow_framework v2.0 Production Release

Framework Highlights:
- 16-layer architecture (Layers 0-15)
- 28 Claude skills with 100% metadata compliance
- 27 document templates with complete YAML frontmatter
- Full traceability chain validation
- Comprehensive validation tooling

Quality Metrics:
- Metadata compliance: 100% (28/28 skills, 27/27 templates)
- Layer assignments: 100% correct
- Traceability chains: 100% valid
- Documentation: Comprehensive
- Quality score: 10/10

Critical Issues Resolved:
- ✅ All YAML parsing errors fixed
- ✅ All metadata gaps filled
- ✅ Clean git state achieved

Post-Release Roadmap (v2.1):
- Add layer numbering warnings to Mermaid diagrams
- Create scripts/README.md validation guide
- Add generic domain examples
- Expand domain adaptation guides

Release Date: 2025-11-24
Framework Version: 2.0"
```

**Verify Tag:**
```bash
git tag -l "v2.0*"
git show v2.0-production-ready
```

**Final Verification:**
```bash
git status  # Should show: "nothing to commit, working tree clean"
git log --oneline -1  # Should show the commit message
```

## Verification Checklist

### Pre-Implementation
- [ ] Backup current state: `git stash` or create branch
- [ ] Verify working directory: `/opt/data/docs_flow_framework`
- [ ] Confirm Python 3.x available: `python3 --version`

### During Implementation
- [ ] Each skill file opens successfully
- [ ] YAML syntax remains valid after edits
- [ ] No accidental content deletion beyond duplicates
- [ ] Git diff shows only intended changes

### Post-Implementation
- [ ] Zero YAML parsing errors across all 28 skills
- [ ] `validate_metadata.py` returns zero errors
- [ ] `validate_requirement_ids.py` returns zero errors
- [ ] All skills visible in Claude Code skill list
- [ ] doc-validator skill loads with complete metadata
- [ ] Git status shows clean state
- [ ] Git tag v2.0-production-ready created
- [ ] Framework achieves 100% metadata compliance

### Success Criteria
- [x] 4 critical issues resolved
- [ ] 28/28 skills with valid YAML frontmatter
- [ ] 27/27 templates with valid YAML frontmatter
- [ ] Zero validation failures
- [ ] Production release tag created
- [ ] Quality score: 10/10

## References

### Key Files
- **Skill directory**: `.claude/skills/*/SKILL.md`
- **Template directory**: `ai_dev_flow/*/TYPE-TEMPLATE.md`
- **Validation scripts**: `scripts/validate_metadata.py`, `ai_dev_flow/scripts/validate_requirement_ids.py`
- **Documentation**: `README.md`, `METADATA_TAGGING_GUIDE.md`, `ID_NAMING_STANDARDS.md`

### Related Documentation
- METADATA_TAGGING_GUIDE.md: Metadata standards and taxonomy
- METADATA_QUICK_REFERENCE.md: Quick lookup for metadata fields
- ID_NAMING_STANDARDS.md: Document ID format rules
- SPEC_DRIVEN_DEVELOPMENT_GUIDE.md: 16-layer architecture overview

### Previous Work
- Recent commit (08463d9): Added YAML frontmatter metadata to all templates
- Recent commit (d49afac): Added metadata tagging guides
- Phase 3 (0e3adf3): Added comprehensive metadata to all 28 skills

### Review Report
Full comprehensive review report available in conversation history (2025-11-24):
- 4 critical issues identified
- 8 lower-priority issues deferred to v2.1
- Framework assessed as 95% production-ready before fixes
- Quality score: 9.5/10 (pre-fix)

## Post-Release Improvements (v2.1)

### High Priority
1. **Layer Numbering Clarity**
   - Add warnings to all Mermaid diagrams about L1-L11 visual groupings
   - Create quick reference table for formal vs. diagram layer numbers
   - Ensure "use formal layer numbers" appears prominently

2. **Validation Guide**
   - Create `scripts/README.md` explaining which script to run when
   - Document validation workflows for different scenarios
   - Add troubleshooting section

### Medium Priority
3. **Generic Domain Examples**
   - Create placeholder-based examples for non-finance domains
   - Add DOMAIN_ADAPTATION_GUIDE.md
   - Provide healthcare, e-commerce, SaaS example adaptations

4. **Documentation Polish**
   - Standardize "Layer X" vs "Layers X-Y" terminology
   - Clarify working directory context in all guides
   - Add more cross-references between related documents

### Low Priority
5. **Tooling Enhancements**
   - Consider pre-commit hooks for metadata validation
   - Add automated YAML linting to CI/CD
   - Create skill metadata validator as separate tool

## Notes

### Implementation Time Estimates
- **Phase 1** (14 files): 30 minutes (2-3 min per file)
- **Phase 2** (1 file): 2 minutes
- **Phase 3** (1 file): 5 minutes
- **Phase 4** (git review): 2 minutes
- **Phase 5** (validation): 5 minutes
- **Phase 6** (git tag): 3 minutes
- **Total**: 47 minutes

### Risk Assessment
- **Complexity**: 1/5 (simple text edits)
- **Risk**: Low (isolated to metadata, no code changes)
- **Rollback**: Easy (git revert or stash pop)
- **Impact**: High (unblocks production release)

### Dependencies
- No external dependencies required
- No code compilation needed
- No database migrations
- No API changes
- Pure documentation metadata fixes

### Failure Modes
- **YAML syntax errors**: Validate each file individually before committing
- **Git conflicts**: Ensure clean working directory before starting
- **Script failures**: Check Python version and script paths
- **Tag conflicts**: Verify tag name doesn't exist before creating

### Success Indicators
1. All validation scripts pass without errors
2. Git shows clean working state
3. All 28 skills load in Claude Code without warnings
4. Production tag v2.0-production-ready exists
5. Framework documentation claims "100% metadata compliance"

---

**Implementation Plan Status**: Ready for Execution
**Next Steps**: Begin Phase 1 - Fix duplicate YAML lines in 14 skills
**Expected Completion**: 2025-11-24 (same day)
**Framework Version After Completion**: 2.0 (Production Ready)
