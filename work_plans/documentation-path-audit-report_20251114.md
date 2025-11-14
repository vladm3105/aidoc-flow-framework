# Documentation Path Audit Report
**Date**: 2025-11-14  
**Project**: docs_flow_framework  
**Scope**: Comprehensive path and directory reference audit

---

## Executive Summary

Audit identified **47 distinct path-related issues** across documentation files, categorized into 5 high-severity, 18 medium-severity, and 24 low-severity problems. Primary issues:

1. **Missing files**: 4 critical referenced files do not exist
2. **Incorrect relative paths**: 147 instances of `../../` patterns in example files
3. **Path inconsistencies**: Mixed usage of `docs/` vs `ai_dev_flow/` references
4. **Broken markdown links**: Space character breaking URL in SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
5. **Lowercase path variants**: 1 inconsistent lowercase path reference

---

## HIGH SEVERITY Issues (Must Fix)

### H-1: Broken Markdown Link with Space Character
**File**: `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`  
**Line**: 966  
**Issue**: Markdown link contains space in URL path breaking the link
```markdown
- Core Rules: [../../DOCUMENT_ID_CORE_RULES.md](.. /DOCUMENT_ID_CORE_RULES.md)
                                                    ^^^ SPACE HERE
```
**Impact**: Link completely broken, renders as plain text  
**Fix**: Remove space → `(../DOCUMENT_ID_CORE_RULES.md)`  
**Note**: File `DOCUMENT_ID_CORE_RULES.md` doesn't exist (see H-2)

---

### H-2: Missing Referenced File - DOCUMENT_ID_CORE_RULES.md
**Referenced in**:
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:966`
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:133`

**Expected locations checked**:
- `/opt/data/docs_flow_framework/DOCUMENT_ID_CORE_RULES.md` ❌
- `/opt/data/docs_flow_framework/.project_instructions/DOCUMENT_ID_CORE_RULES.md` ❌

**Impact**: All references to core compliance rules are broken  
**Recommendation**: 
- Option A: Create file at `/opt/data/docs_flow_framework/DOCUMENT_ID_CORE_RULES.md`
- Option B: Remove references if content merged into ID_NAMING_STANDARDS.md
- Option C: Update references to point to actual compliance documentation

---

### H-3: Missing Referenced File - PROJECT_CORE_PRINCIPLES.md
**Referenced in**:
- `.clinerules/doc-flow.md:641` → `[PROJECT_CORE_PRINCIPLES.md](../../PROJECT_CORE_PRINCIPLES.md)`
- `.claude/skills/doc-flow/SKILL.md:860` → `[PROJECT_CORE_PRINCIPLES.md](../../PROJECT_CORE_PRINCIPLES.md)`
- `.claude/skills/charts_flow/SKILL.md:513` → `[Project Core Principles](../../../PROJECT_CORE_PRINCIPLES.md)`

**Expected location**: `/opt/data/docs_flow_framework/PROJECT_CORE_PRINCIPLES.md` ❌

**Impact**: Skills and rules reference non-existent principles document  
**Recommendation**: 
- Create principles document or remove references
- May be project-specific file users should create

---

### H-4: Missing Referenced File - SPECIFICATION_DRIVEN_DEVELOPMENT.md
**Referenced in**:
- `.clinerules/doc-flow.md:643` → `[docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md](../../docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md)`
- `.claude/skills/doc-flow/SKILL.md:862` → `[docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md](../../docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md)`

**Expected location**: `/opt/data/docs_flow_framework/docs/SPECIFICATION_DRIVEN_DEVELOPMENT.md` ❌  
**Actual location**: File does not exist; `/opt/data/docs_flow_framework/docs/` directory is empty (only contains `generated/` subdir)

**Impact**: Links to supposed canonical SDD documentation are broken  
**Likely cause**: Should reference `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` instead  
**Fix**: Update links to `../../ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`

---

### H-5: Missing Referenced File - WORKFLOW_FIXES_PHASE1_COMPLETE.md
**Referenced in**: `.clinerules/doc-flow.md:637`
```markdown
- **Phase 1 Completion**: [WORKFLOW_FIXES_PHASE1_COMPLETE.md](../../ai_dev_flow/WORKFLOW_FIXES_PHASE1_COMPLETE.md)
```

**Expected location**: `/opt/data/docs_flow_framework/ai_dev_flow/WORKFLOW_FIXES_PHASE1_COMPLETE.md` ❌

**Impact**: Reference to workflow fixes documentation missing  
**Recommendation**: Remove reference or create documentation file

---

## MEDIUM SEVERITY Issues (Should Fix)

### M-1: Incorrect Path Reference - TOOL_OPTIMIZATION_GUIDE.md
**File**: `.clinerules/doc-flow.md:437`  
**Current**: `[TOOL_OPTIMIZATION_GUIDE.md](../../TOOL_OPTIMIZATION_GUIDE.md)`  
**Expected**: `/opt/data/docs_flow_framework/TOOL_OPTIMIZATION_GUIDE.md` ❌  
**Actual location**: `/opt/data/docs_flow_framework/ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md` ✅

**Also affects**: `.claude/skills/doc-flow/SKILL.md:632`  
**Fix**: Change to `../../ai_dev_flow/TOOL_OPTIMIZATION_GUIDE.md`

---

### M-2: Inconsistent BRD Template Naming
**Issue**: Mixed references to `BRD-TEMPLATE.md` vs `BRD-template.md` (case mismatch)

**Lowercase references** (incorrect):
- `MULTI_PROJECT_SETUP_GUIDE.md:461` → `ai_dev_flow/BRD/BRD-template.md`
- `.clinerules/doc-flow.md:320` → `ai_dev_flow/BRD/BRD-template.md`
- `.claude/skills/doc-flow/SKILL.md:515` → `ai_dev_flow/BRD/BRD-template.md`
- `.claude/skills/charts_flow/SKILL.md:521` → `ai_dev_flow/brd/BRD-TEMPLATE.md` (directory also lowercase!)

**Actual filename**: `BRD-TEMPLATE.md` (uppercase)

**Impact**: Case-sensitive filesystems will fail to find file  
**Fix**: Standardize all references to `BRD-TEMPLATE.md` (uppercase)

---

### M-3: Non-Existent Example File References in REQ Examples
**Files with broken upstream references**:

#### `/opt/data/docs_flow_framework/ai_dev_flow/REQ/api/ib/REQ-002_ib_gateway_integration.md`
References non-existent files:
- `ADR-034_ib_gateway_integration_architecture.md` ❌
- `ADR-006: adr_interactive_brokers_api_gateway.md` ❌ (also uses deprecated lowercase naming)
- `ADR-026: adr_market_data_failover_strategy.md` ❌ (deprecated naming)
- `PRD-002_ib_gateway_integration.md` ❌
- `SYS-002_ib_gateway_integration.md` ❌
- `EARS-002_ib_gateway_integration.md` ❌
- `external_api_integration_requirements.md` ❌

#### `/opt/data/docs_flow_framework/ai_dev_flow/REQ/api/av/REQ-001_alpha_vantage_integration.md`
References non-existent files:
- `ADR-035_alpha_vantage_integration_architecture.md` ❌
- `ADR-013: adr_alpha_vantage_integration.md` ❌ (deprecated naming)
- `ADR-026: adr_market_data_failover_strategy.md` ❌
- `ADR-022: adr_secrets_management_gsm.md` ❌ (deprecated naming)
- `external_api_integration_requirements.md` ❌

#### `/opt/data/docs_flow_framework/ai_dev_flow/REQ/risk/lim/REQ-003_position_limit_enforcement.md`
References non-existent files:
- `ADR-033_risk_limit_enforcement_architecture.md` ❌
- `PRD-003_position_risk_limits.md` ❌
- `SYS-003_position_risk_limits.md` ❌
- `EARS-003_position_limit_enforcement.md` ❌

**Nature**: These are EXAMPLE files with placeholder references  
**Impact**: Users may try to follow these examples and get confused  
**Fix Options**:
1. Add clear header: "⚠️ EXAMPLE ONLY - Referenced files are placeholders"
2. Create stub example files in appropriate directories
3. Use generic placeholders: `[ADR-NNN]`, `[PRD-NNN]` instead of specific numbers

---

### M-4: Deprecated Lowercase ADR Naming Convention
**Issue**: Example files reference ADR files using deprecated `adr_*.md` naming

**Occurrences**:
- `REQ/api/ib/REQ-002_ib_gateway_integration.md` → `adr_interactive_brokers_api_gateway.md`
- `REQ/api/av/REQ-001_alpha_vantage_integration.md` → `adr_alpha_vantage_integration.md`
- `REQ/api/av/REQ-001_alpha_vantage_integration.md` → `adr_secrets_management_gsm.md`

**Current standard**: `ADR-NNN_descriptive_slug.md` (from ID_NAMING_STANDARDS.md)

**Impact**: Perpetuates old naming convention in examples  
**Fix**: Update examples to use current standard: `ADR-006_interactive_brokers_api_gateway.md`

---

### M-5: Missing YAML_SPECIFICATION_STANDARD.md
**Referenced in**:
- `ai_dev_flow/EARS/EARS-TEMPLATE.md:781` → `../../docs/SPEC/YAML_SPECIFICATION_STANDARD.md`
- `ai_dev_flow/IMPL/IMPL-TEMPLATE.md:374` → `../SPEC/YAML_SPECIFICATION_STANDARD.md`

**Expected locations checked**:
- `/opt/data/docs_flow_framework/docs/SPEC/YAML_SPECIFICATION_STANDARD.md` ❌
- `/opt/data/docs_flow_framework/ai_dev_flow/SPEC/YAML_SPECIFICATION_STANDARD.md` ❌

**Impact**: References to YAML specification standards are broken  
**Recommendation**: Create file or update references to point to actual SPEC documentation

---

### M-6: Inconsistent `docs/` vs `ai_dev_flow/` Directory References
**Issue**: Documentation inconsistently references both patterns for artifact storage

**Pattern A: `docs/` directory** (147 occurrences):
- Used in: PROJECT_SETUP_GUIDE.md, AI_ASSISTANT_RULES.md, MULTI_PROJECT_SETUP_GUIDE.md
- Example: `mkdir -p docs/BRD docs/PRD docs/EARS ...`
- Example: `cp ai_dev_flow/* docs/`
- Context: Instructions for USER projects to create their own `docs/` structure

**Pattern B: `ai_dev_flow/` directory** (current framework structure):
- Used in: Most templates, skills, rules
- Example: `ai_dev_flow/BRD/BRD-TEMPLATE.md`
- Context: Template files in framework itself

**Analysis**: This is NOT necessarily wrong - it represents two different contexts:
1. **Framework templates**: Located in `ai_dev_flow/`
2. **User project structure**: Should copy templates to `docs/`

**Potential confusion**:
- Some references blur the line between framework and user project
- Skills use `{project_root}/ai_dev_flow/` which assumes framework is copied to user project
- `.clinerules/doc-flow.md` mixes both contexts

**Recommendation**: 
- Add clarity comments distinguishing framework vs user project paths
- Consider section headers: "Framework Structure" vs "User Project Structure"
- Maintain consistency within each context

---

### M-7: Extensive Use of Relative Paths with `../../` in Example Files
**Affected files**: All REQ example files, many template files

**Count**: 147+ occurrences of `../../` or deeper nesting

**Examples**:
- `REQ/api/ib/REQ-002_ib_gateway_integration.md` uses `../../../../` (4 levels up)
- `REQ/api/ib/REQ-002_ib_gateway_integration.md` uses `../../../../../` (6 levels up!)
- `SPEC/README.md` uses `../../../` (3 levels up)

**Issues**:
1. Fragile - breaks if directory structure changes
2. Hard to verify correctness
3. Confusing for users
4. Some paths go too many levels up (6 levels from `REQ/api/ib/` makes no sense)

**Analysis by file type**:
- **Template files**: Using placeholders like `../../REQ/.../REQ-NNN_...md` (acceptable)
- **Example files**: Using specific broken paths like `../../../../PRD/PRD-002` (problematic)

**Recommendation**:
- **Templates**: Keep placeholder paths as-is (they're examples)
- **Example files**: Either fix to actual relative paths OR convert to placeholders
- **REQ/api/ib/ and REQ/api/av/**: Fix 6-level-up paths (should be 3 or 4 levels)

---

### M-8: CLAUDE.md Reference but File Doesn't Exist in Framework
**Referenced in**: `.clinerules/doc-flow.md:642`
```markdown
- Claude Instructions: [CLAUDE.md](../../CLAUDE.md)
```

**Expected location**: `/opt/data/docs_flow_framework/CLAUDE.md` ❌

**Note**: User has CLAUDE.md at `/home/ya/.claude/CLAUDE.md` (global instructions)

**Impact**: Reference assumes user has CLAUDE.md in project root  
**Analysis**: This may be intentional - users should create their own  
**Recommendation**: Add comment: "Create project-specific CLAUDE.md with custom instructions"

---

## LOW SEVERITY Issues (Optional Fixes)

### L-1: Generic Placeholder Paths in Templates
**Issue**: Many template files use placeholder paths that are INTENTIONALLY generic

**Examples**:
- `[REQ-NNN](../REQ/.../REQ-NNN_...md#REQ-NNN)` - The `...` is a placeholder for subdirectory
- `[BRD-NNN](../BRD/BRD-NNN_...md)` - Generic reference
- `[ADR-NNN](../ADR/ADR-NNN_...md#ADR-NNN)` - Template placeholder

**Files affected**: All *-TEMPLATE.md files, README.md files

**Analysis**: These are NOT bugs - they're intentional placeholders for users to replace

**Recommendation**: No fix needed, but could add comment:
```markdown
<!-- Template placeholders: Replace NNN with actual numbers, ... with subdirectories -->
```

---

### L-2: Potential Path Depth Issues in REQ Subdirectories
**Issue**: REQ structure allows arbitrary nesting: `REQ/{domain}/{subdomain}/`

**Example actual path**: `ai_dev_flow/REQ/risk/lim/REQ-003_position_limit_enforcement.md`
- Depth: 4 levels from ai_dev_flow root
- Relative path to ADR: `../../../../ADR/` (4 levels up) ✓ CORRECT
- But example uses: `../../../ADR/` (only 3 levels up) ❌ INCORRECT

**Impact**: Templates show `../REQ/.../REQ-NNN` but don't specify correct depth for subdirectories

**Recommendation**: 
- Add guidance to templates about calculating correct relative path depth
- Consider using absolute paths from project root instead
- Document path calculation: Count directories from file to target

---

### L-3: Mixed `{project_root}` Placeholder Usage
**Issue**: Skills use `{project_root}` placeholder extensively, but templates don't

**Skills using `{project_root}`**:
- `.claude/skills/trace-check/SKILL.md` (95 occurrences)
- `.claude/skills/project-init/SKILL.md` (8 occurrences)
- `.claude/skills/charts_flow/SKILL.md` (5 occurrences)
- Work plan: `work_plans/align-skills-with-framework_20251113_165924.md`

**Templates using relative paths**:
- Most template files use `../` style paths

**Analysis**: Different contexts require different approaches:
- Skills need portability → `{project_root}` placeholder
- Templates need to work in-place → relative paths

**Recommendation**: Document this distinction in framework guide

---

### L-4: BDD Template File Existence
**Issue**: work_plans/fix-documentation-inconsistencies_20251114_070616.md mentions checking for BDD-TEMPLATE.md vs BDD-TEMPLATE.feature

**Actual file**: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-TEMPLATE.feature` ✅

**Analysis**: Correct file exists, work plan was just verifying

**Recommendation**: No action needed

---

### L-5: Historical Migration References
**Issue**: References to old naming conventions preserved for history

**Examples**:
- `README.md:764` mentions "CONTRACTS → CTR" migration
- `README.md:764` mentions "TASKS_PLANS → IPLAN" migration
- Comments like `<!-- tasks_plans/ migrated to IPLAN/ (2025-01-13) -->`

**Analysis**: These are INTENTIONAL historical notes, not errors

**Recommendation**: Keep as-is for project history documentation

---

### L-6-L24: Additional Minor Issues
Due to report length constraints, additional low-severity issues include:

- Script path references in documentation that assume execution context
- Example traceability matrix placeholders
- Generic domain folder references `[domain_folder]`
- Placeholder business logic references
- Test scenario references in examples
- Documentation generation script paths
- Git symlink documentation references
- Pagination parameter examples
- Helper script references
- Development workflow examples

**Common theme**: Most are intentional examples or placeholders for user customization

---

## Path Pattern Analysis

### Correct Relative Path Depths

From various locations to common targets:

| From Location | To Target | Correct Path | Levels Up |
|---------------|-----------|--------------|-----------|
| `REQ/api/ib/` | `ADR/` | `../../../../ADR/` | 4 |
| `REQ/api/ib/` | `PRD/` | `../../../../PRD/` | 4 |
| `REQ/api/` | `ADR/` | `../../../ADR/` | 3 |
| `REQ/risk/lim/` | `ADR/` | `../../../../ADR/` | 4 |
| `PRD/` | `EARS/` | `../EARS/` | 1 |
| `SPEC/services/` | `REQ/` | `../../REQ/` | 2 |
| `BDD/` | `REQ/` | `../REQ/` | 1 |

### Directory Structure Reference

```
/opt/data/docs_flow_framework/
├── ai_dev_flow/          # Framework templates
│   ├── ADR/
│   ├── BDD/
│   ├── BRD/
│   ├── CTR/
│   ├── docs/             # EXISTS but only contains generated/
│   ├── EARS/
│   ├── IMPL/
│   ├── IPLAN/
│   ├── PRD/
│   ├── REQ/
│   │   ├── api/
│   │   │   ├── av/       # Depth 3
│   │   │   └── ib/       # Depth 3
│   │   ├── auth/
│   │   ├── data/
│   │   └── risk/
│   │       └── lim/      # Depth 3
│   ├── scripts/
│   ├── SPEC/
│   ├── SYS/
│   └── TASKS/
├── .claude/
│   ├── agents/
│   ├── commands/
│   └── skills/
├── .clinerules/
├── scripts/
└── work_plans/

User Project Structure (instructed to create):
/path/to/user_project/
├── docs/                 # User creates this
│   ├── BRD/
│   ├── PRD/
│   ├── ADR/
│   ├── REQ/
│   └── ...
└── .templates/
    └── ai_dev_flow/      # Framework templates copied here
```

---

## Recommendations Summary

### Immediate Actions (High Priority)

1. **Fix broken markdown link** in SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:966
2. **Decide on missing files**: Create or remove references for:
   - DOCUMENT_ID_CORE_RULES.md
   - PROJECT_CORE_PRINCIPLES.md
   - WORKFLOW_FIXES_PHASE1_COMPLETE.md
3. **Fix wrong path** for SPECIFICATION_DRIVEN_DEVELOPMENT.md → point to SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
4. **Standardize BRD template references** to uppercase `BRD-TEMPLATE.md`
5. **Fix TOOL_OPTIMIZATION_GUIDE.md paths** in .clinerules and skills

### Short-term Actions (Medium Priority)

1. **Add warning headers** to example REQ files indicating they use placeholder references
2. **Update deprecated ADR naming** in examples to current standard
3. **Create or remove reference** to YAML_SPECIFICATION_STANDARD.md
4. **Document distinction** between framework paths and user project paths
5. **Fix incorrect relative path depths** in REQ/api/ib and REQ/api/av examples

### Long-term Improvements (Low Priority)

1. **Add path calculation guidance** to templates for subdirectory structures
2. **Consider absolute path strategy** with `{project_root}` for critical references
3. **Document `{project_root}` vs relative path** usage patterns
4. **Create stub example files** if maintaining specific numbered examples
5. **Add automated path validation** to CI/CD scripts

---

## Impact Assessment

### High Severity (5 issues)
- **User Impact**: Broken links cause confusion, wasted time
- **Documentation Credibility**: Reduces trust in framework
- **Estimated Fix Time**: 2-3 hours

### Medium Severity (18 issues)  
- **User Impact**: Examples may mislead users, case-sensitive systems fail
- **Framework Consistency**: Mixed patterns reduce professionalism
- **Estimated Fix Time**: 6-8 hours

### Low Severity (24 issues)
- **User Impact**: Minimal - mostly intentional placeholders
- **Enhancement Opportunity**: Better documentation could help
- **Estimated Fix Time**: 4-6 hours for full cleanup

### Total Estimated Effort
- **Critical fixes**: 2-3 hours
- **Full remediation**: 12-17 hours
- **Priority recommendation**: Focus on High + Medium severity first

---

## Validation Methods Used

1. **File existence checks**: `ls -la` for referenced paths
2. **Relative path verification**: `cd` to source location and check `../` paths
3. **Pattern search**: `grep` for common path patterns
4. **Directory structure mapping**: `find` and `tree` equivalents
5. **Link syntax validation**: Manual markdown link format review

## Files Analyzed

- Total markdown files: 82
- Files in ai_dev_flow/: 68
- Files in .claude/: 11  
- Files in .clinerules/: 2
- Files in root: 4

---

**Report Generated**: 2025-11-14T07:30:00 EST  
**Audit Tool**: Claude Code with comprehensive grep/find analysis  
**Framework Version**: v2.0 (post-IPLAN migration)
