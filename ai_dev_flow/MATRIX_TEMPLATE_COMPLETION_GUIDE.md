# Traceability Matrix Template Completion Guide

## Status Summary

**Completion**: 6 of 13 matrix templates updated with cumulative tagging sections (46% complete)

**Phase 3 Status**: Pattern established across key layers

## Completed Templates

### ✅ Complete Templates (6)

1. **TRACEABILITY_MATRIX_COMPLETE-TEMPLATE.md**
   - Comprehensive 16-layer cumulative tagging table
   - Complete examples for all layers
   - Validation rules and patterns

2. **BRD-000_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 1)
   - No upstream tags required
   - Strategic source documentation
   - Traceability anchor pattern

3. **PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 2)
   - Required tags: `@brd`
   - Tag count: 1
   - Product requirements pattern

4. **EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 3)
   - Required tags: `@brd`, `@prd`
   - Tag count: 2
   - WHEN-THE-SHALL syntax integration

5. **REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 7)
   - Required tags: `@brd` through `@sys`
   - Tag count: 6
   - Atomic requirements pattern

6. **SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md** (Layer 10)
   - Required tags: `@brd` through `@req` + optional `@impl`, `@ctr`
   - Tag count: 7-9
   - YAML cumulative_tags format

## Remaining Templates (7)

### Layer 4: BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd`, `@prd`, `@ears`
- **Tag Count**: 3+
- **Format**: Gherkin tags format
- **Pattern**: Test scenarios with cumulative upstream tags

### Layer 5: ADR-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd`, `@prd`, `@ears`, `@bdd`
- **Tag Count**: 4
- **Format**: Markdown tags
- **Pattern**: Architecture decisions with test scenario references

### Layer 6: SYS-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd` through `@adr`
- **Tag Count**: 5
- **Format**: Markdown tags
- **Pattern**: System requirements with architecture decisions

### Layer 8: IMPL-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd` through `@req`
- **Tag Count**: 7
- **Format**: Markdown tags
- **Pattern**: Implementation plans (optional layer)
- **Note**: Optional layer - include only if exists in chain

### Layer 9: CTR-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd` through `@impl`
- **Tag Count**: 8
- **Format**: Markdown + YAML (contract files)
- **Pattern**: API contracts (optional layer)
- **Note**: Optional layer - include only if exists in chain

### Layer 11: TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd` through `@spec`
- **Tag Count**: 8-10
- **Format**: Markdown tags
- **Pattern**: Implementation tasks with all upstream references

### Layer 12: TASKS_PLANS-000_TRACEABILITY_MATRIX-TEMPLATE.md
- **Required Tags**: `@brd` through `@tasks`
- **Tag Count**: 9-11
- **Format**: Markdown tags
- **Pattern**: Session-specific implementation plans

## Established Pattern

### Section Structure

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

### Section Renumbering

After adding Section 2 (Required Tags), all subsequent sections are renumbered:
- Original Section 2 → Section 3
- Original Section 3 → Section 4
- ... and so on

## Completion Instructions

### For Each Remaining Template:

1. **Read the existing template**
   ```bash
   Read file_path: /opt/data/docs_flow_framework/ai_dev_flow/[ARTIFACT]/[ARTIFACT]-000_TRACEABILITY_MATRIX-TEMPLATE.md
   ```

2. **Insert cumulative tagging section after Section 1**
   - Use Edit tool to insert new Section 2 before existing Section 2
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

### Example Tag Requirements by Layer

```
Layer 1 (BRD): None (0 tags)
Layer 2 (PRD): @brd (1 tag)
Layer 3 (EARS): @brd, @prd (2 tags)
Layer 4 (BDD): @brd, @prd, @ears (3+ tags)
Layer 5 (ADR): @brd through @bdd (4 tags)
Layer 6 (SYS): @brd through @adr (5 tags)
Layer 7 (REQ): @brd through @sys (6 tags)
Layer 8 (IMPL): @brd through @req (7 tags)  # Optional
Layer 9 (CTR): @brd through @impl (8 tags)  # Optional
Layer 10 (SPEC): @brd through @req + optional @impl, @ctr (7-9 tags)
Layer 11 (TASKS): @brd through @spec (8-10 tags)
Layer 12 (task_plans): @brd through @tasks (9-11 tags)
```

### Validation Commands Template

```bash
# Find all [ARTIFACT]s and their upstream tags
python scripts/extract_tags.py --type [ARTIFACT] --show-all-upstream

# Validate [ARTIFACT]-XXX has required tags
python scripts/validate_tags_against_docs.py \
  --artifact [ARTIFACT]-XXX \
  --expected-layers [comma-separated-layers] \
  --strict

# Generate [ARTIFACT] traceability report
python scripts/generate_traceability_matrices.py \
  --type [ARTIFACT] \
  --show-coverage
```

## References

- **Core Documentation**:
  - [TRACEABILITY.md](TRACEABILITY.md#cumulative-tagging-hierarchy) - Cumulative tagging hierarchy specification
  - [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](SPEC_DRIVEN_DEVELOPMENT_GUIDE.md#cumulative-tagging-hierarchy) - SDD workflow with tagging

- **Helper Scripts**:
  - [batch_update_matrix_templates.py](scripts/batch_update_matrix_templates.py) - Generates tag sections for all layers

- **Completed Examples**:
  - Simple (1 tag): PRD-000_TRACEABILITY_MATRIX-TEMPLATE.md
  - Medium (2 tags): EARS-000_TRACEABILITY_MATRIX-TEMPLATE.md
  - Complex (6 tags): REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md
  - YAML (7-9 tags): SPEC-000_TRACEABILITY_MATRIX-TEMPLATE.md

## Next Steps

1. Complete remaining 7 matrix templates following the established pattern
2. Verify all templates have consistent structure and naming
3. Run validation scripts on all completed templates
4. Update work plan with Phase 3 completion status
5. Proceed to Phase 4: Update workflow diagrams

---

**Document Status**: Active
**Created**: 2025-11-13
**Author**: AI Dev Flow Framework Team
**Purpose**: Guide completion of remaining traceability matrix templates using established pattern
