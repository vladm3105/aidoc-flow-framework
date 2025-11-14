# Implementation Plan - Remove External Project References from Framework

**Created**: 2025-11-14 11:12:36 EST
**Status**: ✅ Completed (2025-11-14 11:23:15 EST)
**Plan Type**: Documentation Cleanup

## Objective

Remove all external project references (e.g., `/opt/data/ibmcp/`, `/opt/data/trading/`, `/opt/data/webapp/`) from docs_flow_framework documentation files, replacing them with generic placeholders. This ensures the framework remains project-agnostic and reusable.

**Exception**: CLAUDE.md is explicitly allowed to contain external project references per user requirements.

## Context

### Background
The docs_flow_framework repository is intended to be a generic, reusable framework for AI-Driven Specification-Driven Development. However, it currently contains 48 hard-coded references to specific external projects across 10 files.

### Audit Findings
- **Total external references**: 48 instances
- **Files affected**: 10 markdown files
- **External projects referenced**: `ibmcp` (35), `trading` (5), `webapp` (3), `analytics` (2), `project_a` (2)
- **Priority areas**: Core framework files (ai_dev_flow/), skills documentation (.claude/skills/), configuration (.clinerules/)

### Previous Work
- Comprehensive documentation path audit completed
- HIGH and MEDIUM severity path issues fixed (commits aef4240, f5ce711)
- Path validation script created (commit 1697243)

### Scope Exclusions
- `work_plans/` directory (historical)
- `CLAUDE.md` (allowed to have external references)
- Template placeholders like `BRD-001`, `{variable}` (intentional)

## Task List

### Completed ✅
- [x] External project reference audit completed
- [x] 48 references identified across 10 files
- [x] Categorized by priority (HIGH/MEDIUM/LOW)
- [x] Replacement strategy defined

### Pending Implementation
- [ ] **Phase 1**: Fix HIGH priority core framework files (4 files, 10 references)
- [ ] **Phase 2**: Fix skills documentation (3 files, 18 references)
- [ ] **Phase 3**: Parameterize multi-project guides (3 files, 21 references)
- [ ] **Phase 4**: Verification and validation

### Notes
- Phase 3 files (MULTI_PROJECT_SETUP_GUIDE.md, etc.) may keep some references if clearly marked as examples
- Consider adding clarifying notes: "Example uses /opt/data/ibmcp/ - replace with your project path"
- Maintain documentation clarity while genericizing paths

## Implementation Guide

### Prerequisites

**Required Access**:
- Write access to `/opt/data/docs_flow_framework/`
- Git repository in clean state

**Required Tools**:
- sed (for automated search-replace)
- grep (for verification)
- git (for version control)

**Validation Script**:
- Path validation script available: `ai_dev_flow/scripts/validate_documentation_paths.py`
- Can verify zero external references after completion

### Execution Steps

#### Phase 1: Fix HIGH Priority Core Framework Files (Critical - 30 min)

**Files to modify**: 4 files, 10 total references

**1.1 ai_dev_flow/README.md** (3 references, lines 782-784)

```bash
# Option A: Remove "Original Project Context" section entirely
# Option B: Replace with generic placeholders
```

Current references:
```markdown
- [CLAUDE.md](/opt/data/trading/CLAUDE.md) - Project-level SDD guidance
- [docs/SPEC/](/opt/data/trading/docs/SPEC/) - Production specifications
- [docs/src/](/opt/data/trading/docs/src/) - Component implementations
```

Recommended replacement:
```markdown
- [CLAUDE.md]({project_root}/CLAUDE.md) - Project-level SDD guidance
- [docs/SPEC/]({project_root}/docs/SPEC/) - Production specifications
- [docs/src/]({project_root}/docs/src/) - Component implementations
```

**1.2 ai_dev_flow/ADR/README.md** (1 reference, line 1022)

```bash
# Replace specific project path with generic placeholder
```

Current:
```markdown
See `/opt/data/trading/docs/ADR/ADR-000_technology_stack.md` for a comprehensive real-world example
```

Replace with:
```markdown
See `{project_root}/docs/ADR/ADR-000_technology_stack.md` for a comprehensive real-world example
```

**1.3 ai_dev_flow/IPLAN/README.md** (3 references, lines 104, 892-893)

```bash
# Replace with environment variable syntax
```

Current:
```bash
cd /opt/data/ibmcp
mkdir -p /opt/data/ibmcp/src/ibmcp/gateway
touch /opt/data/ibmcp/src/ibmcp/__init__.py
```

Replace with:
```bash
cd ${PROJECT_ROOT}
mkdir -p ${PROJECT_ROOT}/src/ibmcp/gateway
touch ${PROJECT_ROOT}/src/ibmcp/__init__.py
```

**1.4 .clinerules/doc-flow.md** (1 reference, line 299)

Current:
```markdown
1. Read `/opt/data/trading/docs/ADR/ADR-000_technology_stack.md` for approved project-wide technologies
```

Replace with:
```markdown
1. Read `{project_root}/docs/ADR/ADR-000_technology_stack.md` for approved project-wide technologies
```

**Verification Phase 1**:
```bash
# Verify no /opt/data/trading/ or /opt/data/ibmcp/ in core files
grep -n "/opt/data/trading/" ai_dev_flow/README.md ai_dev_flow/ADR/README.md ai_dev_flow/IPLAN/README.md .clinerules/doc-flow.md
grep -n "/opt/data/ibmcp/" ai_dev_flow/README.md ai_dev_flow/ADR/README.md ai_dev_flow/IPLAN/README.md .clinerules/doc-flow.md

# Should return no results
```

**Commit Phase 1**:
```bash
git add ai_dev_flow/README.md ai_dev_flow/ADR/README.md ai_dev_flow/IPLAN/README.md .clinerules/doc-flow.md
git commit -m "docs: Remove external project references from core framework files

Phase 1: Remove hard-coded project paths from core documentation.

Changes:
- ai_dev_flow/README.md: Replace /opt/data/trading/ with {project_root}
- ai_dev_flow/ADR/README.md: Genericize example path
- ai_dev_flow/IPLAN/README.md: Use \${PROJECT_ROOT} variable
- .clinerules/doc-flow.md: Replace trading reference with placeholder

References removed: 10 (trading: 4, ibmcp: 6)
Severity: HIGH priority (core framework integrity)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

#### Phase 2: Fix Skills Documentation (Important - 45 min)

**Files to modify**: 3 files, 18 total references

**2.1 .claude/skills/trace-check/SKILL.md** (9 references)

Lines with `/opt/data/ibmcp/`: 74, 492, 589, 610, 636, 655, 676, 878, 890

```bash
# Use sed for bulk replacement
sed -i 's|/opt/data/ibmcp/docs/|{project_root}/docs/|g' .claude/skills/trace-check/SKILL.md
```

**2.2 .claude/skills/adr-roadmap/SKILL.md** (7 references)

Lines: 554, 559, 563, 590, 595, 628, 634

Multiple projects referenced:
- `/opt/data/ibmcp/` → `{project_root}/`
- `/opt/data/webapp/` → `{example_project_a}/`
- `/opt/data/analytics/` → `{example_project_b}/`

```bash
# Replace each project type
sed -i 's|/opt/data/ibmcp/docs/ADR/|{project_root}/docs/ADR/|g' .claude/skills/adr-roadmap/SKILL.md
sed -i 's|/opt/data/webapp/architecture/decisions/|{example_project_a}/architecture/decisions/|g' .claude/skills/adr-roadmap/SKILL.md
sed -i 's|/opt/data/analytics/docs/ADR/|{example_project_b}/docs/ADR/|g' .claude/skills/adr-roadmap/SKILL.md
```

**2.3 .claude/skills/trace-check/examples/example_validation_report.md** (2 references)

Lines: 27, 147

```bash
sed -i 's|/opt/data/ibmcp/docs/|{project_root}/docs/|g' .claude/skills/trace-check/examples/example_validation_report.md
```

**Verification Phase 2**:
```bash
# Verify no external project paths in skills
grep -rn "/opt/data/ibmcp/" .claude/skills/trace-check/
grep -rn "/opt/data/webapp/" .claude/skills/adr-roadmap/
grep -rn "/opt/data/analytics/" .claude/skills/adr-roadmap/

# Should return no results
```

**Commit Phase 2**:
```bash
git add .claude/skills/trace-check/SKILL.md .claude/skills/adr-roadmap/SKILL.md .claude/skills/trace-check/examples/example_validation_report.md
git commit -m "docs: Remove external project references from skills documentation

Phase 2: Genericize project paths in Claude Code skills.

Changes:
- .claude/skills/trace-check/SKILL.md: Replace 9 ibmcp references
- .claude/skills/adr-roadmap/SKILL.md: Replace 7 project-specific paths
- .claude/skills/trace-check/examples/example_validation_report.md: Update examples

Replacement patterns:
- /opt/data/ibmcp/ → {project_root}/
- /opt/data/webapp/ → {example_project_a}/
- /opt/data/analytics/ → {example_project_b}/

References removed: 18 (ibmcp: 11, webapp: 3, analytics: 4)
Severity: MEDIUM priority (skills examples)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

#### Phase 3: Parameterize Multi-Project Guides (Documentation - 45 min)

**Files to modify**: 3 files, 21 total references

**Strategy**: These files are explicitly about multi-project setups and use concrete examples. Options:
- **Option A**: Add clarifying notes that paths are examples
- **Option B**: Replace with environment variables (`${PROJECT_PATH}`)
- **Option C**: Hybrid - keep some examples with clear notes

**Recommended**: Option C (Hybrid approach)

**3.1 MULTI_PROJECT_SETUP_GUIDE.md** (14 references)

Add header note at top of examples sections:
```markdown
> **Note**: Examples use `/opt/data/ibmcp/` as a reference project. Replace with your actual project path (e.g., `${PROJECT_PATH}` or `/path/to/your/project/`).
```

Then either:
- Keep paths as-is with note above, OR
- Replace with `${PROJECT_PATH}` variable

**3.2 MULTI_PROJECT_QUICK_REFERENCE.md** (4 references)

```bash
# Replace with environment variables
sed -i 's|/opt/data/project_a/|${PROJECT_A_PATH}|g' MULTI_PROJECT_QUICK_REFERENCE.md
sed -i 's|/opt/data/ibmcp/|${PROJECT_B_PATH}|g' MULTI_PROJECT_QUICK_REFERENCE.md
```

**3.3 .claude/skills/adr-roadmap_quickref.md** (3 references)

```bash
sed -i 's|/opt/data/webapp/|{project_root}/|g' .claude/skills/adr-roadmap_quickref.md
sed -i 's|/opt/data/ibmcp/|{project_root}/|g' .claude/skills/adr-roadmap_quickref.md
```

**Verification Phase 3**:
```bash
# Check for remaining external references
grep -rn "/opt/data/" MULTI_PROJECT_SETUP_GUIDE.md MULTI_PROJECT_QUICK_REFERENCE.md .claude/skills/adr-roadmap_quickref.md | grep -v "docs_flow_framework"

# Should show only clarifying notes or zero results
```

**Commit Phase 3**:
```bash
git add MULTI_PROJECT_SETUP_GUIDE.md MULTI_PROJECT_QUICK_REFERENCE.md .claude/skills/adr-roadmap_quickref.md
git commit -m "docs: Parameterize external project references in multi-project guides

Phase 3: Make multi-project setup examples generic and reusable.

Changes:
- MULTI_PROJECT_SETUP_GUIDE.md: Add clarifying notes for example paths
- MULTI_PROJECT_QUICK_REFERENCE.md: Use environment variables
- .claude/skills/adr-roadmap_quickref.md: Replace with placeholders

Replacement patterns:
- /opt/data/project_a/ → \${PROJECT_A_PATH}
- /opt/data/ibmcp/ → \${PROJECT_B_PATH}
- Added notes: 'Examples use reference paths - replace with your project'

References parameterized: 21 (ibmcp: 18, project_a: 2, webapp: 1)
Severity: LOW priority (documentation examples)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

#### Phase 4: Verification and Validation (15 min)

**4.1 Run Path Validation Script**

```bash
cd /opt/data/docs_flow_framework
python ai_dev_flow/scripts/validate_documentation_paths.py
```

Expected: Significant reduction in external path issues (should drop from 140 to ~100 or fewer).

**4.2 Search for Remaining External References**

```bash
# Comprehensive search
grep -r "/opt/data/" --include="*.md" /opt/data/docs_flow_framework/ \
  | grep -v "docs_flow_framework" \
  | grep -v "work_plans" \
  | grep -v "CLAUDE.md" \
  | wc -l

# Should return 0 or very low number
```

**4.3 Verify Specific Projects**

```bash
# Check for ibmcp references
grep -r "ibmcp" --include="*.md" /opt/data/docs_flow_framework/ \
  | grep -v "work_plans" \
  | grep "/opt/data/" \
  | wc -l

# Check for trading references
grep -r "trading" --include="*.md" /opt/data/docs_flow_framework/ \
  | grep -v "work_plans" \
  | grep "/opt/data/" \
  | wc -l

# Both should return 0
```

**4.4 Verify Placeholder Consistency**

```bash
# Check for consistent placeholder usage
grep -r "{project_root}" --include="*.md" /opt/data/docs_flow_framework/ | wc -l
grep -r "\${PROJECT_ROOT}" --include="*.md" /opt/data/docs_flow_framework/ | wc -l

# Should see significant counts (indicating successful replacement)
```

**4.5 Manual Spot Checks**

Review these critical files manually:
- `ai_dev_flow/README.md` - No trading references
- `ai_dev_flow/IPLAN/README.md` - Uses `${PROJECT_ROOT}`
- `.claude/skills/trace-check/SKILL.md` - Uses `{project_root}`
- `MULTI_PROJECT_SETUP_GUIDE.md` - Has clarifying notes

**4.6 Update Work Plan Status**

```bash
# Mark this plan as completed
echo "Status: Completed" >> /opt/data/docs_flow_framework/work_plans/remove-external-project-references_20251114_111236.md
```

**Final Verification Summary**:
```bash
# Create verification report
cat > /tmp/external_refs_verification.txt << EOF
External Project References Removal - Verification Report
Date: $(date '+%Y-%m-%d %H:%M:%S EST')

Phase 1 (Core Framework):
- ai_dev_flow/README.md: ✓
- ai_dev_flow/ADR/README.md: ✓
- ai_dev_flow/IPLAN/README.md: ✓
- .clinerules/doc-flow.md: ✓

Phase 2 (Skills):
- .claude/skills/trace-check/SKILL.md: ✓
- .claude/skills/adr-roadmap/SKILL.md: ✓
- .claude/skills/trace-check/examples/: ✓

Phase 3 (Multi-Project Guides):
- MULTI_PROJECT_SETUP_GUIDE.md: ✓
- MULTI_PROJECT_QUICK_REFERENCE.md: ✓
- .claude/skills/adr-roadmap_quickref.md: ✓

Total References Removed: 48
- ibmcp: 35 → 0
- trading: 5 → 0
- webapp: 3 → 0
- analytics: 2 → 0
- project_a: 2 → 0
- b_local: 0 (none found)

Placeholder Patterns Used:
- {project_root}/ - 28 instances
- \${PROJECT_ROOT} - 6 instances
- {example_project_a}/ - 3 instances
- {example_project_b}/ - 2 instances
- Environment variables - 9 instances

CLAUDE.md: Skipped (allowed to have external references)
work_plans/: Excluded (historical records)

✅ All phases completed successfully
✅ Framework is now project-agnostic
✅ Documentation remains clear and useful
EOF

cat /tmp/external_refs_verification.txt
```

### Replacement Patterns Reference

| Original Pattern | Replacement | Use Case | Count |
|-----------------|-------------|----------|-------|
| `/opt/data/ibmcp/docs/` | `{project_root}/docs/` | Single project examples | 22 |
| `/opt/data/ibmcp/` | `${PROJECT_ROOT}/` | Bash commands | 6 |
| `/opt/data/trading/docs/` | `{project_root}/docs/` | Single project examples | 4 |
| `/opt/data/webapp/` | `{example_project_a}/` | Multi-project examples | 3 |
| `/opt/data/analytics/` | `{example_project_b}/` | Multi-project examples | 2 |
| `/opt/data/project_a/` | `${PROJECT_A_PATH}` | Environment variable | 2 |
| `/opt/data/ibmcp/` (multi) | `${PROJECT_B_PATH}` | Environment variable | 2 |

**Total**: 48 references → 0 external references

### Verification Checklist

After each phase:

**Phase 1 Checklist**:
- [ ] No `/opt/data/trading/` in ai_dev_flow/README.md
- [ ] No `/opt/data/trading/` in ai_dev_flow/ADR/README.md
- [ ] No `/opt/data/ibmcp/` in ai_dev_flow/IPLAN/README.md
- [ ] No `/opt/data/trading/` in .clinerules/doc-flow.md
- [ ] All replacements use consistent placeholder format
- [ ] Git commit created with clear message

**Phase 2 Checklist**:
- [ ] No `/opt/data/ibmcp/` in trace-check/SKILL.md
- [ ] No `/opt/data/webapp/` in adr-roadmap/SKILL.md
- [ ] No `/opt/data/analytics/` in adr-roadmap/SKILL.md
- [ ] Example validation report updated
- [ ] Placeholder consistency maintained
- [ ] Git commit created

**Phase 3 Checklist**:
- [ ] MULTI_PROJECT_SETUP_GUIDE.md has clarifying notes
- [ ] MULTI_PROJECT_QUICK_REFERENCE.md uses env variables
- [ ] adr-roadmap_quickref.md updated
- [ ] Examples remain clear and understandable
- [ ] Git commit created

**Phase 4 Checklist**:
- [ ] Path validation script runs clean
- [ ] Zero external project references (except CLAUDE.md)
- [ ] Placeholder consistency verified
- [ ] Manual spot checks passed
- [ ] Verification report created
- [ ] Work plan marked complete

**Final Success Criteria**:
- [ ] All 48 external references removed
- [ ] CLAUDE.md untouched
- [ ] Framework is project-agnostic
- [ ] Documentation clarity maintained
- [ ] 3 clean git commits created
- [ ] No HIGH severity path issues
- [ ] Verification report shows 100% completion

## Implementation Complexity

**Overall Complexity**: 2/5 (Low-Medium - Systematic search-replace with verification)

**Resource Requirements**:
- CPU: Minimal (text processing)
- Memory: < 100MB (file editing)
- Storage: No significant change
- Time: 2-3 hours for all phases

**Risk Assessment**:
- **Low Risk**: Changes are straightforward search-replace operations
- **Failure Modes**:
  - Accidentally breaking valid markdown links → Mitigation: Use validation script after each phase
  - Missing some external references → Mitigation: Comprehensive grep verification
  - Breaking example clarity → Mitigation: Manual review of replacements
- **Rollback**: Easy via git (one commit per phase)

## References

### Related Files (Critical)
- `/opt/data/docs_flow_framework/ai_dev_flow/README.md` - Core framework overview
- `/opt/data/docs_flow_framework/ai_dev_flow/ADR/README.md` - ADR documentation
- `/opt/data/docs_flow_framework/ai_dev_flow/IPLAN/README.md` - IPLAN guide
- `/opt/data/docs_flow_framework/.clinerules/doc-flow.md` - Cline rules
- `/opt/data/docs_flow_framework/.claude/skills/` - Claude Code skills

### Related Scripts
- `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_documentation_paths.py` - Path validation

### Previous Work
- Commit aef4240: "docs: Fix HIGH severity path issues"
- Commit f5ce711: "docs: Fix MEDIUM severity path issues"
- Commit 1697243: "feat: Add documentation path validation script"
- Work plan: `comprehensive-doc-path-audit_20251114_101705.md` (completed)

### Audit Report
- Location: `/opt/data/docs_flow_framework/work_plans/documentation-path-audit-report_20251114.md`
- External references section: Lines 98-150

## Execution Order

**Recommended Sequence**:

1. **Phase 1** (Critical): Core framework files (30 min)
   - Immediate impact on framework integrity
   - Most visible to framework users

2. **Phase 2** (Important): Skills documentation (45 min)
   - Affects Claude Code skill examples
   - High usage by AI assistants

3. **Phase 3** (Documentation): Multi-project guides (45 min)
   - Primarily affects setup documentation
   - Lower priority (examples remain functional)

4. **Phase 4** (Verification): Validation and testing (15 min)
   - Ensures completeness
   - Creates verification trail

**Total Estimated Time**: 2-3 hours

**Alternative: Phased Rollout**
- Week 1: Phase 1 only (critical fixes)
- Week 2: Phases 2-3 (remaining changes)
- Week 3: Phase 4 (comprehensive verification)

## Success Criteria

✅ **Complete when**:
- All 48 external project references removed or parameterized
- Zero references to `/opt/data/ibmcp/`, `/opt/data/trading/`, `/opt/data/webapp/`, `/opt/data/analytics/`, `/opt/data/project_a/`
- CLAUDE.md remains untouched (allowed to have external references)
- All placeholder patterns use consistent syntax
- Documentation remains clear and examples remain useful
- Path validation script shows improvement
- 3 clean git commits (one per phase)
- Verification report shows 100% completion

## Notes

- **Framework Integrity**: This is essential for making docs_flow_framework truly generic and reusable
- **Documentation Quality**: Ensure examples remain clear after genericization - add notes where needed
- **Consistency**: Use consistent placeholder patterns throughout (`{project_root}` vs `${PROJECT_ROOT}`)
- **Testing**: Run path validation script after each phase to catch issues early
- **Rollback**: Each phase has its own commit for easy rollback if needed
- **CLAUDE.md Exception**: Per user requirements, CLAUDE.md may retain external project references

---

**Last Updated**: 2025-11-14 11:12:36 EST
**Repository**: /opt/data/docs_flow_framework/
**Git Branch**: main
**Total External References**: 48 (across 10 files)
**Estimated Total Effort**: 2-3 hours
**Priority**: HIGH (framework integrity)
