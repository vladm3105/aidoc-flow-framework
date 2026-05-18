# BDD-MVP-TEMPLATE Fix Plan

**Created**: 2026-02-26
**Status**: Complete ✓
**Completed**: 2026-02-26
**Version**: 1.1 (Added gaps #14-20: doc-bdd and doc-bdd-autopilot skill path fixes)
**Target Files**:
- `BDD-MVP-TEMPLATE.feature` (primary)
- `BDD_MVP_VALIDATION_RULES.md`
- `BDD_MVP_SCHEMA.yaml`
- `BDD_MVP_CREATION_RULES.md`
- `README.md`

## Overview

Fix identified gaps in `/opt/data/docs_flow_framework/ucx_flow_v3/04_BDD/` documents and align template, validation rules, schema, and skills to a consistent MVP structure.

## Target Files

| File | Type | Priority |
|------|------|----------|
| `BDD-MVP-TEMPLATE.feature` | Feature Template (primary authority) | P1 |
| `BDD_MVP_VALIDATION_RULES.md` | Validation Rules | P1 |
| `BDD_MVP_SCHEMA.yaml` | Schema Definition | P1 |
| `BDD_MVP_CREATION_RULES.md` | Creation Rules | P1 |
| `README.md` | Layer Documentation | P2 |
| `doc-bdd*/SKILL.md` | Skills (5 files) | P2 |
| `doc-bdd_quickref.md` | Quick Reference | P2 |

## Reference Files

- `EARS-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference - example format)
- `PRD-MVP-TEMPLATE_FIX_PLAN.md` (for alignment reference)
- `ID_NAMING_STANDARDS.md` (for element ID format)

---

## Gap Summary

| # | Gap | Severity | Location | Phase |
|---|-----|----------|----------|-------|
| 1 | Duplicate YAML frontmatter in creation rules | Critical | BDD_MVP_CREATION_RULES.md lines 1-13, 21-33 | 1 |
| 2 | Duplicate YAML frontmatter in validation rules | Critical | BDD_MVP_VALIDATION_RULES.md lines 1-13, 22-34 | 1 |
| 3 | Schema default profile is `full` instead of `mvp` | High | BDD_MVP_SCHEMA.yaml line 36 | 2 |
| 4 | Schema `last_updated` is outdated (2026-01-20) | Medium | BDD_MVP_SCHEMA.yaml line 23 | 2 |
| 5 | Template references wrong creation rules file | High | BDD-MVP-TEMPLATE.feature line 20 | 2 |
| 6 | Template references wrong validation rules file | High | BDD-MVP-TEMPLATE.feature line 21 | 2 |
| 7 | doc-bdd-validator schema path incorrect | High | doc-bdd-validator/SKILL.md line 31 | 3 |
| 8 | doc-bdd_quickref output location uses old format | Medium | doc-bdd_quickref.md line 30 | 3 |
| 9 | doc-bdd_quickref template location path wrong | Medium | doc-bdd_quickref.md line 68 | 3 |
| 10 | README file size limits inconsistent | Medium | README.md lines 559-562 | 4 |
| 11 | Schema references old creation rules filename | Medium | BDD_MVP_SCHEMA.yaml line 28 | 2 |
| 12 | Schema references old validation rules filename | Medium | BDD_MVP_SCHEMA.yaml line 29 | 2 |
| 13 | Missing `schema_version` and `total_sections` in schema metadata | Low | BDD_MVP_SCHEMA.yaml | 2 |
| 14 | doc-bdd/SKILL.md path prefix wrong (ucx_flow_v3 vs ucx_flow_v3) | High | doc-bdd/SKILL.md lines 53-56 | 3 |
| 15 | doc-bdd/SKILL.md Related Resources old paths and filenames | High | doc-bdd/SKILL.md lines 606-612 | 3 |
| 16 | doc-bdd/SKILL.md references non-existent BDD_SPLITTING_RULES.md | Medium | doc-bdd/SKILL.md lines 56, 612 | 3 |
| 17 | doc-bdd-autopilot/SKILL.md Templates/Rules section old paths | High | doc-bdd-autopilot/SKILL.md lines 1673-1680 | 3 |
| 18 | doc-bdd-autopilot/SKILL.md references BDD_SCHEMA.yaml (non-MVP name) | High | doc-bdd-autopilot/SKILL.md line 1677 | 3 |
| 19 | doc-bdd-autopilot/SKILL.md references non-existent BDD_SPLITTING_RULES.md | Medium | doc-bdd-autopilot/SKILL.md line 1680 | 3 |
| 20 | doc-bdd/SKILL.md command examples use old paths | Medium | doc-bdd/SKILL.md lines 434, 446 | 3 |

---

## Phase 0: Pre-Implementation

### 0.1 Backup All Files

```bash
# Create backup directory
mkdir -p /opt/data/docs_flow_framework/ucx_flow_v3/04_BDD/.backup_2026-02-26

# Backup templates and rules
cp BDD-MVP-TEMPLATE.feature .backup_2026-02-26/
cp BDD_MVP_VALIDATION_RULES.md .backup_2026-02-26/
cp BDD_MVP_CREATION_RULES.md .backup_2026-02-26/
cp BDD_MVP_SCHEMA.yaml .backup_2026-02-26/
cp README.md .backup_2026-02-26/

# Backup skills
cp -r /opt/data/docs_flow_framework/.claude/skills/doc-bdd* .backup_2026-02-26/
```

### 0.2 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Existing BDD features reference old paths | Medium | Medium | Document migration guide |
| Skills produce invalid output | Medium | Medium | Update all skills in Phase 3 |
| Validation rules mismatch | Low | Medium | Verify CHECK numbers align |
| Cross-document links break | Low | Low | Update references in Phase 4 |

### 0.3 Rollback Plan

**If issues occur during implementation:**

1. **Immediate Rollback**:
   ```bash
   # Restore all files
   cp .backup_2026-02-26/BDD-MVP-TEMPLATE.feature ./
   cp .backup_2026-02-26/BDD_MVP_VALIDATION_RULES.md ./
   cp .backup_2026-02-26/BDD_MVP_CREATION_RULES.md ./
   cp .backup_2026-02-26/BDD_MVP_SCHEMA.yaml ./
   cp .backup_2026-02-26/README.md ./

   # Restore skills
   cp -r .backup_2026-02-26/doc-bdd* /opt/data/docs_flow_framework/.claude/skills/
   ```

2. **Partial Rollback**: Revert only affected files from backup

3. **Post-Rollback**: Re-run validators to confirm restored state

### 0.4 Downstream Impact Analysis

| Downstream Artifact | Impact | Action Required |
|--------------------|--------|-----------------|
| Existing BDD documents | Path references may need update | Add migration note to plan |
| ADR templates | Reference BDD sections | Verify ADR-MVP-TEMPLATE references |
| Validation scripts | CHECK numbers reference sections | Verify BDD_MVP_VALIDATION_RULES.md |
| doc-bdd-reviewer | Check section completeness | Verify section-based checks |
| doc-bdd-fixer | Fix phases reference sections | Verify section creation logic |

---

## Phase 1: Critical Structural Fixes

### 1.1 Remove Duplicate YAML Frontmatter in Creation Rules

**File**: `BDD_MVP_CREATION_RULES.md`

**Current State**:
- Lines 1-13: First YAML frontmatter (valid)
- Lines 21-33: Second YAML frontmatter (duplicate)

**Action**: Delete lines 21-33 (second frontmatter block)

**Keep**: Lines 1-13 (first frontmatter) and lines 14-20 (document role comment)

### 1.2 Remove Duplicate YAML Frontmatter in Validation Rules

**File**: `BDD_MVP_VALIDATION_RULES.md`

**Current State**:
- Lines 1-13: First YAML frontmatter (valid)
- Lines 22-34: Second YAML frontmatter (duplicate)

**Action**: Delete lines 22-34 (second frontmatter block)

---

## Phase 2: Schema and Template Fixes

### 2.1 Update Schema Default Profile

**File**: `BDD_MVP_SCHEMA.yaml`

**Current State** (line 36):
```yaml
profiles:
  default: full
```

**Action**: Change to:
```yaml
profiles:
  default: mvp
```

### 2.2 Update Schema Metadata

**File**: `BDD_MVP_SCHEMA.yaml`

**Current State** (line 23):
```yaml
last_updated: "2026-01-20"
```

**Action**: Update to current date and add missing fields:
```yaml
schema_version: "1.1"
artifact_type: BDD
layer: 4
last_updated: "2026-02-26"
```

### 2.3 Update Schema References

**File**: `BDD_MVP_SCHEMA.yaml`

**Current State** (lines 28-29):
```yaml
references:
  md_template: "BDD-MVP-TEMPLATE.feature"
  yaml_template: "N/A (BDD is .feature-only, no YAML version)"
  creation_rules: "BDD_CREATION_RULES.md"
  validation_rules: "BDD_VALIDATION_RULES.md"
```

**Action**: Update to use MVP filenames:
```yaml
references:
  md_template: "BDD-MVP-TEMPLATE.feature"
  yaml_template: "N/A (BDD is .feature-only, no YAML version)"
  creation_rules: "BDD_MVP_CREATION_RULES.md"
  validation_rules: "BDD_MVP_VALIDATION_RULES.md"
```

### 2.4 Update Template References

**File**: `BDD-MVP-TEMPLATE.feature`

**Current State** (lines 20-21):
```
# CREATION_RULES: BDD_CREATION_RULES.md
# VALIDATION_RULES: BDD_VALIDATION_RULES.md
```

**Action**: Update to use MVP filenames:
```
# CREATION_RULES: BDD_MVP_CREATION_RULES.md
# VALIDATION_RULES: BDD_MVP_VALIDATION_RULES.md
```

---

## Phase 3: Update doc-bdd* Skills

### 3.1 Target Skill Files

| Skill | File Path | Update Scope |
|-------|-----------|--------------|
| doc-bdd-validator | `.claude/skills/doc-bdd-validator/SKILL.md` | Fix schema path reference |
| doc-bdd | `.claude/skills/doc-bdd/SKILL.md` | **CRITICAL**: Fix multiple path refs (lines 53-56, 434, 446, 606-612) |
| doc-bdd-autopilot | `.claude/skills/doc-bdd-autopilot/SKILL.md` | **CRITICAL**: Fix Templates/Rules section (lines 1673-1680) |
| doc-bdd-reviewer | `.claude/skills/doc-bdd-reviewer/SKILL.md` | Verify path references |
| doc-bdd-fixer | `.claude/skills/doc-bdd-fixer/SKILL.md` | Verify path references |
| doc-bdd_quickref | `.claude/skills/doc-bdd_quickref.md` | Fix output location and template path |

### 3.2 doc-bdd-validator/SKILL.md Fixes

**Line 31**: Change schema path from:
```markdown
Schema: `ucx_flow_v3/BDD/BDD_SCHEMA.yaml`
```

To:
```markdown
Schema: `ucx_flow_v3/04_BDD/BDD_MVP_SCHEMA.yaml`
```

### 3.3 doc-bdd/SKILL.md Fixes (CRITICAL - Multiple Locations)

**Lines 53-56** (Pre-requisite References): Change from:
```markdown
3. **Template**: `ucx_flow_v3/04_BDD/BDD-SECTION-TEMPLATE.feature`
4. **Creation Rules**: `ucx_flow_v3/04_BDD/BDD_CREATION_RULES.md`
5. **Validation Rules**: `ucx_flow_v3/04_BDD/BDD_VALIDATION_RULES.md`
6. **Splitting Rules**: `ucx_flow_v3/04_BDD/BDD_SPLITTING_RULES.md`
```

To:
```markdown
3. **Template**: `ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature`
4. **Creation Rules**: `ucx_flow_v3/04_BDD/BDD_MVP_CREATION_RULES.md`
5. **Validation Rules**: `ucx_flow_v3/04_BDD/BDD_MVP_VALIDATION_RULES.md`
```

> **Note**: Remove `BDD_SPLITTING_RULES.md` reference - file does not exist. Splitting rules are in `BDD_MVP_CREATION_RULES.md` Section 1.2.

**Lines 606-612** (Related Resources): Change from:
```markdown
- **Template**: `ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature`
- **Index Template**: `ucx_flow_v3/04_BDD/BDD-SECTION-0-TEMPLATE.md`
- **Subsection Template**: `ucx_flow_v3/04_BDD/BDD-SUBSECTION-TEMPLATE.feature`
- **Aggregator Template**: `ucx_flow_v3/04_BDD/BDD-AGGREGATOR-TEMPLATE.feature`
- **Creation Rules**: `ucx_flow_v3/04_BDD/BDD_CREATION_RULES.md`
- **Validation Rules**: `ucx_flow_v3/04_BDD/BDD_VALIDATION_RULES.md`
- **Splitting Rules**: `ucx_flow_v3/04_BDD/BDD_SPLITTING_RULES.md`
```

To:
```markdown
- **Template**: `ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature`
- **Index Template**: `ucx_flow_v3/04_BDD/BDD-SECTION-0-TEMPLATE.md`
- **Aggregator Template**: `ucx_flow_v3/04_BDD/BDD-AGGREGATOR-TEMPLATE.feature`
- **Schema**: `ucx_flow_v3/04_BDD/BDD_MVP_SCHEMA.yaml`
- **Creation Rules**: `ucx_flow_v3/04_BDD/BDD_MVP_CREATION_RULES.md`
- **Validation Rules**: `ucx_flow_v3/04_BDD/BDD_MVP_VALIDATION_RULES.md`
```

**Lines 434, 446** (Command Examples): Update path prefix from `ucx_flow_v3/` to `ucx_flow_v3/`.

### 3.4 doc-bdd-autopilot/SKILL.md Fixes (CRITICAL)

**Lines 1673-1680** (Templates and Rules): Change from:
```markdown
- **BDD Template**: `ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature`
- **Section Template**: `ucx_flow_v3/04_BDD/BDD-SECTION-TEMPLATE.feature`
- **Index Template**: `ucx_flow_v3/04_BDD/BDD-SECTION-0-TEMPLATE.md`
- **Aggregator Template**: `ucx_flow_v3/04_BDD/BDD-AGGREGATOR-TEMPLATE.feature`
- **BDD Schema**: `ucx_flow_v3/04_BDD/BDD_SCHEMA.yaml`
- **BDD Creation Rules**: `ucx_flow_v3/04_BDD/BDD_CREATION_RULES.md`
- **BDD Validation Rules**: `ucx_flow_v3/04_BDD/BDD_VALIDATION_RULES.md`
- **BDD Splitting Rules**: `ucx_flow_v3/04_BDD/BDD_SPLITTING_RULES.md`
```

To:
```markdown
- **BDD Template**: `ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature`
- **Index Template**: `ucx_flow_v3/04_BDD/BDD-SECTION-0-TEMPLATE.md`
- **Aggregator Template**: `ucx_flow_v3/04_BDD/BDD-AGGREGATOR-TEMPLATE.feature`
- **BDD Schema**: `ucx_flow_v3/04_BDD/BDD_MVP_SCHEMA.yaml`
- **BDD Creation Rules**: `ucx_flow_v3/04_BDD/BDD_MVP_CREATION_RULES.md`
- **BDD Validation Rules**: `ucx_flow_v3/04_BDD/BDD_MVP_VALIDATION_RULES.md`
```

> **Note**: Remove `BDD_SPLITTING_RULES.md` and `BDD-SECTION-TEMPLATE.feature` references - files don't exist. Use `BDD-MVP-TEMPLATE.feature` as primary template.

### 3.5 doc-bdd_quickref.md Fixes

**Line 30**: Change output location from:
```text
docs/BDD/BDD-NNN_{feature_name}.feature
```

To:
```text
docs/04_BDD/BDD-NN_{slug}/BDD-NN.SS_{section_slug}.feature
```

**Line 68**: Change template location from:
```text
ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature
```

To:
```text
ucx_flow_v3/04_BDD/BDD-MVP-TEMPLATE.feature
```

---

## Phase 4: README and Documentation Fixes

### 4.1 Fix File Size Limits Inconsistency

**File**: `README.md`

**Current State** (lines 559-562):
```markdown
## File Size Limits

- **Target**: 800 lines per `.feature` file
- **Maximum**: 1200 lines per `.feature` file (absolute)
```

**Action**: Align with schema and creation rules:
```markdown
## File Size Limits

- **Target**: 800 lines per `.feature` file
- **Maximum**: 1200 lines per `.feature` file (absolute)
- **Scenarios**: Maximum 12 scenarios per Feature block
```

**Rationale**: Schema (line 261-264) and creation rules (Section 1.2.6) both specify:
- Maximum 1200 lines (absolute)
- Target 800 lines
- Maximum 12 scenarios per Feature

---

## Phase 5: Testing & Validation

### 5.1 Syntax Validation

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| YAML syntax | Validate YAML files | No syntax errors |
| Frontmatter check | Search for duplicate frontmatter | Single block only |
| Schema validation | Load schema file | Valid YAML |

### 5.2 Validation Commands

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('BDD_MVP_SCHEMA.yaml').read())"

# Check for duplicate frontmatter in creation rules
head -50 BDD_MVP_CREATION_RULES.md | grep -c "^---"
# Expected: 2 (opening and closing)

# Check for duplicate frontmatter in validation rules
head -50 BDD_MVP_VALIDATION_RULES.md | grep -c "^---"
# Expected: 2 (opening and closing)

# Verify schema default profile
grep "default:" BDD_MVP_SCHEMA.yaml
# Expected: "default: mvp"
```

### 5.3 Skill Testing

| Skill | Test Action | Expected Result |
|-------|-------------|-----------------|
| doc-bdd | Verify path references | Correct ucx_flow_v3 paths |
| doc-bdd-validator | Validate test BDD | Pass all checks |

---

## Execution Order

| Step | Phase | Action | Dependencies |
|------|-------|--------|--------------|
| 1 | 0 | Create backups | None |
| 2 | 1 | Fix duplicate YAML in creation rules | Backup complete |
| 3 | 1 | Fix duplicate YAML in validation rules | Step 2 |
| 4 | 2 | Update schema default profile | Step 3 |
| 5 | 2 | Update schema metadata and references | Step 4 |
| 6 | 2 | Update template references | Step 5 |
| 7 | 3 | Update doc-bdd-validator schema path | Step 6 |
| 8 | 3 | Update doc-bdd/SKILL.md prerequisite refs (lines 53-56) | Step 7 |
| 9 | 3 | Update doc-bdd/SKILL.md Related Resources (lines 606-612) | Step 8 |
| 10 | 3 | Update doc-bdd/SKILL.md command examples (lines 434, 446) | Step 9 |
| 11 | 3 | Update doc-bdd-autopilot/SKILL.md Templates/Rules (lines 1673-1680) | Step 10 |
| 12 | 3 | Update doc-bdd_quickref paths | Step 11 |
| 13 | 4 | Fix README file size limits | Step 12 |
| 14 | 5 | Run all validation tests | Step 13 |

---

## Verification Checklist

### Creation Rules Verification
- [ ] Single YAML frontmatter block (duplicate removed)
- [ ] No duplicate frontmatter blocks

### Validation Rules Verification
- [ ] Single YAML frontmatter block
- [ ] No duplicate frontmatter blocks

### Schema Verification
- [ ] `profiles.default: mvp` (changed from `full`)
- [ ] `last_updated: "2026-02-26"` (updated)
- [ ] References point to MVP filenames
- [ ] Valid YAML syntax

### Template Verification
- [ ] References BDD_MVP_CREATION_RULES.md
- [ ] References BDD_MVP_VALIDATION_RULES.md

### Skill Files Verification
- [ ] doc-bdd-validator/SKILL.md has correct schema path (`ucx_flow_v3/04_BDD/BDD_MVP_SCHEMA.yaml`)
- [ ] doc-bdd/SKILL.md prerequisite refs use `ucx_flow_v3/` path prefix (lines 53-56)
- [ ] doc-bdd/SKILL.md Related Resources use MVP filenames (lines 606-612)
- [ ] doc-bdd/SKILL.md command examples use correct paths (lines 434, 446)
- [ ] doc-bdd/SKILL.md no reference to non-existent BDD_SPLITTING_RULES.md
- [ ] doc-bdd-autopilot/SKILL.md Templates/Rules use correct paths (lines 1673-1680)
- [ ] doc-bdd-autopilot/SKILL.md no reference to non-existent files
- [ ] doc-bdd_quickref.md has correct output location
- [ ] doc-bdd_quickref.md has correct template location

### README Verification
- [ ] File size limits aligned with schema (1200 max, 800 target)
- [ ] Scenario limit documented (12 per Feature)

---

## Estimated Changes

| Metric | Count |
|--------|-------|
| Creation Rules lines removed | ~12 |
| Validation Rules lines removed | ~12 |
| Schema lines modified | ~6 |
| Template lines modified | ~2 |
| README lines modified | ~4 |
| doc-bdd/SKILL.md lines modified | ~20 |
| doc-bdd-autopilot/SKILL.md lines modified | ~10 |
| doc-bdd-validator/SKILL.md lines modified | ~2 |
| doc-bdd_quickref.md lines modified | ~4 |
| Skill files to update | 4 |

---

## Migration Guide for Existing BDD Features

If existing BDD documents need updating:

1. **Verify folder structure**: Ensure all `.feature` files are in nested folders `docs/04_BDD/BDD-NN_{slug}/`
2. **Update file references**: Change any references to old paths
3. **Validate**: Run validator on updated documents

---

## Related Files to Update (Post-Implementation)

After fixing the template and skills, verify these files:

| File | Update Needed | Priority |
|------|---------------|----------|
| `ADR-MVP-TEMPLATE.md` | BDD section references | P3 |
| `SYS-MVP-TEMPLATE.md` | BDD section references | P3 |
| Existing BDD documents | Path verification | P3 |

---

**End of Plan**
