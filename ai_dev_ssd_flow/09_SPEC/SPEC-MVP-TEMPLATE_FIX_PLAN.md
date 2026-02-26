# SPEC-MVP-TEMPLATE Fix Plan

**Artifact**: SPEC (Technical Specifications)
**Layer**: 9
**Status**: PLANNED
**Created**: 2026-02-26T12:00:00
**Priority**: HIGH

---

## Gap Summary

| ID | Gap | Location | Severity | Phase |
|----|-----|----------|----------|-------|
| GAP-01 | AI_CONTEXT says "7 required sections" but template has 8 sections | SPEC-MVP-TEMPLATE.md:41 | HIGH | 1 |
| GAP-02 | Duplicate `upstream_links` section in creation rules | SPEC_MVP_CREATION_RULES.md:91,100 | HIGH | 1 |
| GAP-03 | Duplicate error code line (SPEC-E025) | SPEC_MVP_VALIDATION_RULES.md:327,329 | MEDIUM | 1 |
| GAP-04 | Section count mismatch "7 major sections" in creation rules | SPEC_MVP_CREATION_RULES.md:71 | HIGH | 1 |
| GAP-05 | Wrong schema path in validator skill | doc-spec-validator/SKILL.md:31 | HIGH | 2 |
| GAP-06 | Legacy cumulative tag format in validator | doc-spec-validator/SKILL.md:189-196 | HIGH | 2 |
| GAP-07 | Wrong validation rules path in validator | doc-spec-validator/SKILL.md:316-317 | HIGH | 2 |
| GAP-08 | Wrong layer number in quick reference | doc-spec_quickref.md:4,17 | HIGH | 3 |
| GAP-09 | Wrong output path in quick reference | doc-spec_quickref.md:30 | HIGH | 3 |
| GAP-10 | Wrong template path in quick reference | doc-spec_quickref.md:88 | HIGH | 3 |
| GAP-11 | Section count mismatch (12 vs 8 MVP) in quick reference | doc-spec_quickref.md:64 | MEDIUM | 3 |
| GAP-12 | Missing nested folder rule in quick reference | doc-spec_quickref.md | MEDIUM | 3 |
| GAP-13 | Version history update needed | All affected files | LOW | 4 |
| GAP-14 | Wrong template path in autopilot skill | doc-spec-autopilot/SKILL.md:953 | HIGH | 2 |

---

## Template Format Clarification

**Important Context**: SPEC has two template formats serving different workflows:

| Format | File | Sections | Purpose |
|--------|------|----------|---------|
| Markdown | SPEC-MVP-TEMPLATE.md | 8 numbered (1-8) + 2 appendices | Human workflow, documentation |
| YAML | SPEC-MVP-TEMPLATE.yaml | 13+ top-level keys | Autopilot, code generation |

The fix plan addresses issues in **BOTH** formats. When fixing section counts, ensure the correct count for each format is used.

---

## Phase 0: Pre-Flight Verification

### 0.1 Backup Critical Files

```bash
# Create backup directory
mkdir -p /tmp/spec_fix_backup_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/tmp/spec_fix_backup_$(date +%Y%m%d_%H%M%S)"

# Backup template files
cp ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md "$BACKUP_DIR/"
cp ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md "$BACKUP_DIR/"
cp ai_dev_ssd_flow/09_SPEC/SPEC_MVP_VALIDATION_RULES.md "$BACKUP_DIR/"

# Backup skill files
cp .claude/skills/doc-spec-validator/SKILL.md "$BACKUP_DIR/"
cp .claude/skills/doc-spec_quickref.md "$BACKUP_DIR/"
```

### 0.2 Verify Current State

```bash
# Verify section counts
grep -n "required sections" ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md
grep -n "major sections" ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md

# Check for duplicates
grep -n "upstream_links:" ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md

# Verify paths in validator
grep -n "ai_dev_flow" .claude/skills/doc-spec-validator/SKILL.md
```

---

## Phase 1: Fix Template and Rules Files

### 1.1 Fix AI_CONTEXT Section Count (GAP-01)

**File**: `ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md`
**Line**: 41

**Before**:
```
- 7 required sections.
```

**After**:
```
- 8 required sections (Sections 1-8) plus 2 optional appendices.
```

### 1.2 Remove Duplicate upstream_links Section (GAP-02)

**File**: `ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md`
**Lines**: 99-106 (remove the duplicate)

**Before** (lines 91-107):
```yaml
  # Upstream links (REQUIRED) - Quick reference to source documents
  upstream_links:
    - artifact: "BRD-01"
      path: "../01_BRD/BRD-NN_{slug}.md"
      sections: ["§X Business Requirements"]
    - artifact: "PRD-01"
      path: "../02_PRD/PRD-NN_{slug}.md"
      sections: ["§Y Functional Requirements"]

  # Upstream links (REQUIRED) - Quick reference to source documents
  upstream_links:
    - artifact: "BRD-01"
      path: "../01_BRD/BRD-NN_{slug}.md"
      sections: ["§X Business Requirements"]
    - artifact: "PRD-01"
      path: "../02_PRD/PRD-NN_{slug}.md"
      sections: ["§Y Functional Requirements"]
```

**After** (lines 91-98 only):
```yaml
  # Upstream links (REQUIRED) - Quick reference to source documents
  upstream_links:
    - artifact: "BRD-01"
      path: "../01_BRD/BRD-NN_{slug}.md"
      sections: ["§X Business Requirements"]
    - artifact: "PRD-01"
      path: "../02_PRD/PRD-NN_{slug}.md"
      sections: ["§Y Functional Requirements"]
```

### 1.3 Remove Duplicate Error Code Line (GAP-03)

**File**: `ai_dev_ssd_flow/09_SPEC/SPEC_MVP_VALIDATION_RULES.md`
**Lines**: 327, 329 (line 329 is duplicate of 327)

**Before** (lines 327-329):
```
- `[FAIL] SPEC-E025: Missing interfaces.internal_apis`

- `[FAIL] SPEC-E025: Missing interfaces.internal_apis`
```

**After** (remove line 329):
```
- `[FAIL] SPEC-E025: Missing interfaces.internal_apis`
```

### 1.4 Fix Section Count in Creation Rules (GAP-04)

**File**: `ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md`
**Line**: 71

**Before**:
```
**Complete YAML structure with 7 major sections (kept in a single YAML file):**
```

**After**:
```
**Complete YAML structure with major sections (kept in a single YAML file):**
```

**Note**: Remove the specific count to avoid mismatches, or count accurately based on actual sections.

---

## Phase 2: Fix Validator Skill File

### 2.1 Fix Schema Path (GAP-05)

**File**: `.claude/skills/doc-spec-validator/SKILL.md`
**Line**: 31

**Before**:
```
Schema: `ai_dev_flow/SPEC/SPEC_SCHEMA.yaml`
```

**After**:
```
Schema: `ai_dev_ssd_flow/09_SPEC/SPEC_MVP_SCHEMA.yaml`
```

### 2.2 Fix Cumulative Tag Formats (GAP-06)

**File**: `.claude/skills/doc-spec-validator/SKILL.md`
**Lines**: 189-196

**Before**:
```markdown
**Layer 9 Cumulative Tags:**
- @brd: BRD-NNN:XXX-NNN (required)
- @prd: PRD-NNN:XXX-NNN (required)
- @ears: EARS-NNN:NNN (required)
- @bdd: BDD-NNN:scenario-name (required)
- @adr: ADR-NN (required)
- @sys: SYS-NNN:XXX-NNN (required)
- @req: REQ-NNN:feature-name (required)
- @ctr: CTR-NNN (optional)
```

**After**:
```markdown
**Layer 9 Cumulative Tags:**
- @brd: BRD.NN.EE.SS (required)
- @prd: PRD.NN.EE.SS (required)
- @ears: EARS.NN.24.SS (required)
- @bdd: BDD.NN.13.SS (required)
- @adr: ADR-NN (required)
- @sys: SYS.NN.25.SS (required)
- @req: REQ.NN.26.SS (required)
- @ctr: CTR-NN (optional)
```

### 2.3 Fix Related Resources Paths (GAP-07)

**File**: `.claude/skills/doc-spec-validator/SKILL.md`
**Lines**: 316-317

**Before**:
```markdown
- **SPEC Validation Rules**: `ai_dev_flow/09_SPEC/SPEC_VALIDATION_RULES.md`
- **SPEC Schema**: `ai_dev_flow/SPEC/SPEC_SCHEMA.yaml`
```

**After**:
```markdown
- **SPEC Validation Rules**: `ai_dev_ssd_flow/09_SPEC/SPEC_MVP_VALIDATION_RULES.md`
- **SPEC Schema**: `ai_dev_ssd_flow/09_SPEC/SPEC_MVP_SCHEMA.yaml`
```

### 2.4 Fix Autopilot Template Path (GAP-14)

**File**: `.claude/skills/doc-spec-autopilot/SKILL.md`
**Line**: 953

**Before**:
```markdown
- **SPEC Template**: `ai_dev_flow/09_SPEC/SPEC-TEMPLATE.yaml`
```

**After**:
```markdown
- **SPEC Template**: `ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.yaml`
```

---

## Phase 3: Fix Quick Reference File

### 3.1 Fix Layer Number (GAP-08)

**File**: `.claude/skills/doc-spec_quickref.md`

**Line 4 Before**:
```
**Layer:** 10 (Technical Specifications)
```

**Line 4 After**:
```
**Layer:** 9 (Technical Specifications)
```

**Line 17 Before**:
```
- "Document Layer 10 specification for validation service"
```

**Line 17 After**:
```
- "Document Layer 9 specification for validation service"
```

### 3.2 Fix Output Path (GAP-09)

**File**: `.claude/skills/doc-spec_quickref.md`
**Lines**: 29-31

**Before**:
```
## Output Location

```
ai_dev_flow/SPEC/SPEC-NNN_{slug}.yaml
```
```

**After**:
```
## Output Location (Nested Folder - MANDATORY)

```
docs/09_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
```
```

### 3.3 Fix Template Path (GAP-10)

**File**: `.claude/skills/doc-spec_quickref.md`
**Lines**: 85-89

**Before**:
```
## Template Location

```
ai_dev_flow/10_SPEC/SPEC-MVP-TEMPLATE.yaml
```
```

**After**:
```
## Template Location

```
ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md    # Human workflow
ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.yaml  # Autopilot workflow
```
```

### 3.4 Fix Required Sections (GAP-11)

**File**: `.claude/skills/doc-spec_quickref.md`
**Lines**: 64-68

**Before**:
```
## Required Sections (12)

1. metadata, 2. cumulative_tags, 3. overview, 4. architecture
5. interfaces, 6. implementation, 7. error_handling, 8. configuration
9. testing, 10. deployment, 11. monitoring, 12. traceability
```

**After**:
```
## Required Sections (MVP - 8 Numbered + 2 Appendices)

1. Document Control, 2. Traceability, 3. Component Overview, 4. Technical Design
5. Implementation Logic, 6. Configuration, 7. Non-Functional Requirements, 8. Quality Gates
Appendix A: Glossary, Appendix B: References
```

### 3.5 Add Nested Folder Rule (GAP-12)

**File**: `.claude/skills/doc-spec_quickref.md`
**Add after Quick Validation section**:

```markdown
## Nested Folder Rule (MANDATORY)

ALL SPEC documents MUST use nested folders:
```
docs/09_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml
```

Invalid: `docs/09_SPEC/SPEC-01_api.yaml` (not in nested folder)
Valid: `docs/09_SPEC/SPEC-01_api/SPEC-01_api.yaml`
```

---

## Phase 4: Update Version History

### 4.1 Update SPEC-MVP-TEMPLATE.md Version History

Add entry to version history section:

```markdown
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.1 | 2026-02-26 | Fixed AI_CONTEXT section count from 7 to 8 sections | System |
```

### 4.2 Update SPEC_MVP_CREATION_RULES.md Version History

Add entry to version history section (if exists) or update the version at the top:

```markdown
**Version**: 1.4
**Changes**: v1.4: Removed duplicate upstream_links section; fixed section count reference
```

### 4.3 Update SPEC_MVP_VALIDATION_RULES.md Version History

Add entry (if version history section exists):

```markdown
**Version**: 1.3
**Changes**: v1.3: Removed duplicate error code line (SPEC-E025)
```

### 4.4 Update doc-spec-validator/SKILL.md Version History

```markdown
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.3 | 2026-02-26 | Fixed schema path to ai_dev_ssd_flow/09_SPEC/; Updated cumulative tag formats to unified dot notation; Fixed validation rules paths | System |
```

---

## Phase 5: Verification

### 5.1 Verify Template Fixes

```bash
# Verify AI_CONTEXT section count
grep -n "8 required sections" ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md

# Count actual numbered sections in template
grep -E "^## [0-9]+\." ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE.md | wc -l
```

### 5.2 Verify Creation Rules Fixes

```bash
# Verify no duplicate upstream_links
grep -c "upstream_links:" ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md
# Expected: 1

# Verify section count fix
grep -n "major sections" ai_dev_ssd_flow/09_SPEC/SPEC_MVP_CREATION_RULES.md
```

### 5.3 Verify Validation Rules Fixes

```bash
# Verify no duplicate SPEC-E025 lines
grep -c "SPEC-E025" ai_dev_ssd_flow/09_SPEC/SPEC_MVP_VALIDATION_RULES.md
# Expected: 1
```

### 5.4 Verify Validator Skill Fixes

```bash
# Verify correct schema path
grep "ai_dev_ssd_flow/09_SPEC/SPEC_MVP_SCHEMA.yaml" .claude/skills/doc-spec-validator/SKILL.md

# Verify no old paths remain
grep -c "ai_dev_flow/SPEC" .claude/skills/doc-spec-validator/SKILL.md
# Expected: 0

# Verify cumulative tag format
grep -E "@brd: BRD\.[0-9]{2}\.[0-9]{2}\.[0-9]{2}" .claude/skills/doc-spec-validator/SKILL.md
```

### 5.5 Verify Quick Reference Fixes

```bash
# Verify layer 9
grep "Layer: 9" .claude/skills/doc-spec_quickref.md

# Verify no layer 10 references
grep -c "Layer.* 10" .claude/skills/doc-spec_quickref.md
# Expected: 0

# Verify nested folder path
grep "docs/09_SPEC/SPEC-NN_{slug}/SPEC-NN_{slug}.yaml" .claude/skills/doc-spec_quickref.md

# Verify template path
grep "ai_dev_ssd_flow/09_SPEC/SPEC-MVP-TEMPLATE" .claude/skills/doc-spec_quickref.md
```

---

## Phase 6: Post-Implementation Checks

### 6.1 Cross-Document Consistency

```bash
# Verify layer 9 is consistent across all SPEC files
grep -rn "layer.*9" ai_dev_ssd_flow/09_SPEC/*.md ai_dev_ssd_flow/09_SPEC/*.yaml
grep -rn "layer.*9" .claude/skills/doc-spec*/SKILL.md

# Verify no layer 10 references remain
grep -rn "layer.*10" ai_dev_ssd_flow/09_SPEC/ .claude/skills/doc-spec*/
# Expected: No matches
```

### 6.2 Skill File Path Consistency

```bash
# Verify all skill files use correct paths
grep -rn "ai_dev_ssd_flow/09_SPEC" .claude/skills/doc-spec*/SKILL.md
grep -rn "ai_dev_flow/.*SPEC" .claude/skills/doc-spec*/SKILL.md
# Second command should return no matches
```

---

## Execution Order

| Order | Phase | Description | Estimated Edits |
|-------|-------|-------------|-----------------|
| 1 | Phase 0 | Pre-flight verification and backups | 0 (verification only) |
| 2 | Phase 1 | Fix template and rules files (4 fixes) | 4 |
| 3 | Phase 2 | Fix validator skill file (3 fixes) | 3 |
| 4 | Phase 3 | Fix quick reference file (5 fixes) | 5 |
| 5 | Phase 4 | Update version histories (4 files) | 4 |
| 6 | Phase 5 | Verification commands | 0 (verification only) |
| 7 | Phase 6 | Post-implementation checks | 0 (verification only) |

**Total Files Modified**: 5
**Total Edits**: ~16

---

## Rollback Plan

If issues are found post-implementation:

```bash
# Restore from backup
cp "$BACKUP_DIR/SPEC-MVP-TEMPLATE.md" ai_dev_ssd_flow/09_SPEC/
cp "$BACKUP_DIR/SPEC_MVP_CREATION_RULES.md" ai_dev_ssd_flow/09_SPEC/
cp "$BACKUP_DIR/SPEC_MVP_VALIDATION_RULES.md" ai_dev_ssd_flow/09_SPEC/
cp "$BACKUP_DIR/SKILL.md" .claude/skills/doc-spec-validator/
cp "$BACKUP_DIR/doc-spec_quickref.md" .claude/skills/
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-02-26 | Initial fix plan creation | System |
