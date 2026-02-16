---
title: "Traceability Matrix Template Completion Guide"
tags:
  - supporting-document
  - traceability-guide
  - shared-architecture
  - document-template
custom_fields:
  document_type: guide
  purpose: template-completion-reference
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# Traceability Matrix Template Completion Guide

## 1. Status Summary

**Completion**: 13 of 13 matrix templates updated with cumulative tagging sections (100% complete) ✅

**Phase 3 Status**: COMPLETE - All traceability matrix templates now have cumulative tagging sections

## 2. Completed Templates

### ✅ Complete Templates (13/13)

1. **TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md**
   - Comprehensive 15-layer cumulative tagging table
   - Complete examples for all layers
   - Validation rules and patterns

2. **BRD-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 1)
   - No upstream tags required
   - Strategic source documentation
   - Traceability anchor pattern

3. **PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 2)
   - Required tags: `@brd`
   - Tag count: 1
   - Product requirements pattern

4. **EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 3)
   - Required tags: `@brd`, `@prd`
   - Tag count: 2
   - WHEN-THE-SHALL syntax integration

5. **REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 7)
   - Required tags: `@brd` through `@sys`
   - Tag count: 6
   - Atomic requirements pattern

6. **SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 9)
   - Required tags: `@brd` through `@req` + optional `@ctr`
   - Tag count: 7-8
   - YAML cumulative_tags format

7. **BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 4)
   - Required tags: `@brd`, `@prd`, `@ears`
   - Tag count: 3+
   - Gherkin tags and markdown format

8. **ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 5)
   - Required tags: `@brd` through `@bdd`
   - Tag count: 4
   - Architecture decisions with test scenario references

9. **SYS-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 6)
   - Required tags: `@brd` through `@adr`
   - Tag count: 5
   - System requirements with architecture decisions

10. **CTR-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 8)
    - Required tags: `@brd` through `@req`
    - Tag count: 7
    - API contracts (optional layer)

11. **TASKS-00_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 11)
    - Required tags: `@brd` through `@spec`
    - Tag count: 8-9
    - Implementation tasks with all upstream references

## 3. Remaining Templates

✅ **NONE** - All 13 templates now complete with cumulative tagging sections!

## 4. Established Pattern

### section Structure

Each completed template follows this structure:

```markdown
## 2. Required Tags (Cumulative Tagging Hierarchy - Layer X)

### 2.1 Tag Requirements for [ARTIFACT] Artifacts
- Layer number
- Artifact type description
- Required tags list
- Tag count

### 2.2 Tag Format
- Example tag format
- Format rules (bullet list)

### 2.3 Example: [ARTIFACT] with Required Tags
- Complete example with all required tags
- Markdown code block showing tags
- Downstream artifact references

### 2.4 Example: [Additional Context-Specific Example]
- Second example showing variation or detail
- Statement-level or structure-specific examples

### 2.5 Validation Rules
1. Required tags specification
2. Format compliance
3. Valid references
4. No gaps in chain
5. [Artifact-specific rules]

### 2.6 Tag Discovery
- bash commands for tag extraction
- bash commands for validation
- bash commands for coverage reports

### 2.7 [ARTIFACT] Traceability Pattern
- ASCII art chain showing layer position
- Key role description
- Relationship to upstream/downstream artifacts
```

### section Renumbering

After adding section 2 (Required Tags), all subsequent sections are renumbered:
- Original section 2 → section 3
- Original section 3 → section 4
- ... and so on

## 3. Completion Instructions

### 3.1 For Each Remaining Template:

1. **Read the existing template**
   ```bash
   Read file_path: $FRAMEWORK_ROOT/[ARTIFACT]/[ARTIFACT]-00_TRACEABILITY_MATRIX-TEMPLATE.md
   # Example: FRAMEWORK_ROOT=/path/to/ai_dev_flow
   ```

2. **Insert cumulative tagging section after section 1**
   - Use Edit tool to insert new section 2 before existing section 2
   - Follow the established pattern structure above
   - Customize examples for the specific artifact type

3. **Renumber existing sections**
   - Use sed or Edit to increment section numbers
   - Update all section references in the document

4. **Verify consistency**
   - Check tag count matches layer requirements
   - Verify tag format examples are correct
   - Ensure validation rules are appropriate

5. **Commit changes**
   - Individual commit per template or batch commit
   - Reference this guide in commit messages

### 3.2 Example Tag Requirements by Layer

```
Layer 1 (BRD): None (0 tags)
Layer 2 (PRD): @brd (1 tag)
Layer 3 (EARS): @brd, @prd (2 tags)
Layer 4 (BDD): @brd, @prd, @ears (3+ tags)
Layer 5 (ADR): @brd through @bdd (4 tags)
Layer 6 (SYS): @brd through @adr (5 tags)
Layer 7 (REQ): @brd through @sys (6 tags)
Layer 8 (CTR): @brd through @req (7 tags)  # Optional
Layer 9 (SPEC): @brd through @req + optional @ctr (7-8 tags)
Layer 10 (TSPEC): @brd through @spec (8 tags)
Layer 11 (TASKS): @brd through @tspec (9-10 tags)
```

### 3.3 Validation Commands Template

```bash
# Find all [ARTIFACT]s and their upstream tags
python scripts/extract_tags.py --type [ARTIFACT] --show-all-upstream

# Validate [ARTIFACT]-XXX has required tags
python scripts/validate_tags_against_docs.py \
  --artifact [ARTIFACT]-XXX \
  --expected-layers [comma-separated-layers] \
  --strict

# Generate [ARTIFACT] traceability report
python scripts/generate_traceability_matrix.py \
  --type [ARTIFACT] \
  --show-coverage
```

## 4. References

- **Core Documentation**:
  - [TRACEABILITY.md](TRACEABILITY.md#cumulative-tagging-hierarchy) - Cumulative tagging hierarchy specification
  - [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](SPEC_DRIVEN_DEVELOPMENT_GUIDE.md#cumulative-tagging-hierarchy) - SDD workflow with tagging

- **Helper Scripts**:
  - [generate_traceability_matrix.py](scripts/generate_traceability_matrix.py) - Generates traceability reports

- **Completed Examples**:
  - Simple (1 tag): PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md
  - Medium (2 tags): EARS-00_TRACEABILITY_MATRIX-TEMPLATE.md
  - Complex (6 tags): REQ-00_TRACEABILITY_MATRIX-TEMPLATE.md
  - YAML (7-9 tags): SPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md

## 5. Completion Summary

✅ **Phase 3 Complete**: All 13 traceability matrix templates updated with cumulative tagging sections

**What Was Accomplished**:
1. ✅ All 13 matrix templates have consistent cumulative tagging structure
2. ✅ Each template includes section 2 with 7 subsections (tag requirements through traceability pattern)
3. ✅ Automated script (add_cumulative_tagging_to_matrices.py) created for reproducibility
4. ✅ Examples use consistent request submission Service scenario
5. ✅ Proper section renumbering across all templates

**Files Modified**: 5 templates (BDD, ADR, SYS, CTR, TASKS)
**Files Created**: 1 script (add_cumulative_tagging_to_matrices.py)
**Total Lines Added**: 1,186 lines across all templates

**Next Phases** (Already Complete):
- Phase 4: Update workflow diagrams ✅
- Phase 5: Update doc-flow skill ✅
- Phase 6: Update validation scripts ✅
- Phase 7: Create complete example ✅

---

**Document Status**: Active
**Created**: 2025-11-13T00:00:00
**Author**: AI Dev Flow Framework Team
**Purpose**: Guide completion of remaining traceability matrix templates using established pattern
