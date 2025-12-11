# Implementation Plan - Fix Framework Format Issues

**Created**: 2025-12-10 19:19:53 EST
**Status**: Ready for Implementation
**Scope**: `/opt/data/docs_flow_framework/ai_dev_flow/`

## Objective

Identify and fix 31 actionable format inconsistencies across SDD framework README, TEMPLATE, INDEX, and SCHEMA files to ensure documentation consistency and validation reliability.

## Context

### Analysis Results
- **CRITICAL**: 4 issues (missing BRD schema, broken path, section numbering, missing schema refs)
- **HIGH**: 5 issues (tag format, title casing, markdown links)
- **MEDIUM**: 13 issues (terminology, hardcoded examples, error code namespacing)
- **LOW**: 9 issues (placeholder style, reference formatting)

### User Decisions
- PRD section numbering: Standardize to start at Section 1 (not 0)
- ADR/README.md path: Fix to `../ADR/` relative path
- Priority classification: Keep both systems (architecture vs implementation) - by design

### Not Issues (Verified)
- Priority classification difference (architecture vs implementation priority) - intentional
- IPLAN section numbering - verified correct (sections 1, 2, 3 at lines 40, 68, 93)

## Task List

### Pending - Batch 1: Critical Fixes
- [ ] Create `BRD/BRD_SCHEMA.yaml` using PRD_SCHEMA.yaml as template
- [ ] Fix `ADR/README.md` broken path reference (line 33): `../../../docs/ADR/` → `../ADR/`
- [ ] Renumber `PRD/PRD-TEMPLATE.md` sections (0→1, 1→2, etc.)
- [ ] Add schema_reference to `SPEC/SPEC-TEMPLATE.md`
- [ ] Add schema_reference to `SPEC/SPEC-TEMPLATE.yaml`

### Pending - Batch 2: High Priority Fixes
- [ ] Fix BDD tag spacing in `BDD/BDD-TEMPLATE.feature` (`@tag:value` → `@tag: value`)
- [ ] Add schema_reference to `CTR/CTR-TEMPLATE.yaml`
- [ ] Fix SPEC_DRIVEN_DEVELOPMENT_GUIDE links in all 12 README files
- [ ] Replace hardcoded examples in `CTR/CTR-TEMPLATE.md` with placeholders

### Pending - Batch 3: Medium Priority Fixes
- [ ] Standardize YAML title format across templates to Title Case
- [ ] Namespace error codes in *_SCHEMA.yaml files (ADR-E001, BDD-E001, etc.)
- [ ] Add cumulative_tags section to `EARS/EARS_SCHEMA.yaml`
- [ ] Update `BDD/BDD-000_index.md` with clear example labeling
- [ ] Standardize H1 header naming to `# {Full Name} ({ACRONYM})`
- [ ] Standardize terminology: "Architecture Decision Requirements"
- [ ] Fix capitalization: "Security" as Quality Attribute
- [ ] Add section numbers to `SPEC/SPEC-TEMPLATE.md`
- [ ] Standardize tag notation (dots vs dashes)
- [ ] Standardize status field case to Title Case

### Pending - Batch 4: Low Priority Fixes
- [ ] Standardize placeholder format
- [ ] Use markdown links consistently for template references
- [ ] Align BDD schema version or document reason
- [ ] Remove/convert line number anchors in references
- [ ] Document quick reference section policy
- [ ] Standardize related documents section naming
- [ ] Document maximum section depth policy
- [ ] Add proper master index table to `REQ/REQ-000_index.md`

### Pending - Batch 5: Validation
- [ ] Run validation scripts to verify fixes
- [ ] Check all relative paths resolve correctly

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/`
- Reference `PRD/PRD_SCHEMA.yaml` for BRD schema creation

### Execution Steps

#### Step 1: Create Missing BRD_SCHEMA.yaml
```bash
# Copy PRD_SCHEMA.yaml as base, modify for BRD
cp ai_dev_flow/PRD/PRD_SCHEMA.yaml ai_dev_flow/BRD/BRD_SCHEMA.yaml
# Edit to change PRD references to BRD, layer 2 to layer 1
```

#### Step 2: Fix ADR/README.md Path
- File: `ai_dev_flow/ADR/README.md` line 33
- Change: `../../../docs/ADR/ADR-000_technology_stack.md` → `../ADR/ADR-000_technology_stack.md`

#### Step 3: Renumber PRD-TEMPLATE.md Sections
- File: `ai_dev_flow/PRD/PRD-TEMPLATE.md`
- Change all section numbers: 0→1, 1→2, 2→3, etc.

#### Step 4: Add Schema References
Files to update:
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.md` - add to YAML frontmatter
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml` - add field
- `ai_dev_flow/CTR/CTR-TEMPLATE.yaml` - add field

#### Step 5: Fix BDD Tag Spacing
- File: `ai_dev_flow/BDD/BDD-TEMPLATE.feature`
- Change: `@tag:value` → `@tag: value` (add space after colon)

#### Step 6: Fix README Links
All 12 README files need SPEC_DRIVEN_DEVELOPMENT_GUIDE link fixed:
```
ai_dev_flow/ADR/README.md
ai_dev_flow/BDD/README.md
ai_dev_flow/BRD/README.md
ai_dev_flow/CTR/README.md
ai_dev_flow/EARS/README.md
ai_dev_flow/IMPL/README.md
ai_dev_flow/IPLAN/README.md
ai_dev_flow/PRD/README.md
ai_dev_flow/REQ/README.md
ai_dev_flow/SPEC/README.md
ai_dev_flow/SYS/README.md
ai_dev_flow/TASKS/README.md
```

#### Step 7: Replace Hardcoded Examples in CTR-TEMPLATE.md
- File: `ai_dev_flow/CTR/CTR-TEMPLATE.md`
- Lines 140, 160: Replace "Risk Validation Service", "REQ-003, SYS-004, ADR-008" with placeholders

### Verification
1. Run validation scripts:
   ```bash
   ./scripts/validate_req_template.sh
   ./scripts/validate_brd_template.sh
   python scripts/validate_tags_against_docs.py
   ```
2. Verify YAML frontmatter parses without errors
3. Check all relative paths resolve correctly
4. Grep for tag format consistency

## References

### Key Files to Modify
- `ai_dev_flow/BRD/BRD_SCHEMA.yaml` - CREATE
- `ai_dev_flow/PRD/PRD-TEMPLATE.md` - Renumber sections
- `ai_dev_flow/ADR/README.md` - Fix path
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.md` - Add schema_reference
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml` - Add schema_reference
- `ai_dev_flow/CTR/CTR-TEMPLATE.yaml` - Add schema_reference
- `ai_dev_flow/BDD/BDD-TEMPLATE.feature` - Fix tag spacing
- `ai_dev_flow/CTR/CTR-TEMPLATE.md` - Replace hardcoded examples
- All 12 README files - Fix markdown links

### Reference Documents
- Schema pattern: `ai_dev_flow/PRD/PRD_SCHEMA.yaml`
- Template pattern: `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md` (correct format)
- Validation scripts: `ai_dev_flow/scripts/`

### Scope
- **Files to modify**: ~25-30 files
- **New files to create**: 1 (BRD_SCHEMA.yaml)
- **Complexity**: Medium (mostly find-and-replace with structural changes)
