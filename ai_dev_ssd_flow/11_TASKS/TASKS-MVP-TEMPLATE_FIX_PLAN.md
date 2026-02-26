# TASKS-MVP-TEMPLATE Fix Plan

**Document**: TASKS-MVP-TEMPLATE_FIX_PLAN.md
**Created**: 2026-02-26
**Status**: COMPLETED
**Priority**: High
**Scope**: TASKS template and schema alignment

## Executive Summary

This fix plan addresses **12 identified gaps** in TASKS template and schema files. Primary issues include:

1. **Missing MD Template**: Broken symlink `TASKS-TEMPLATE.md -> TASKS-MVP-TEMPLATE.md` (target doesn't exist)
2. **Layer Inconsistency**: Schema says Layer 10, but README/validation rules say Layer 11
3. **Section Count Inconsistency**: Schema has 15 required_sections, validation/creation rules say 11, YAML template has 13
4. **Traceability Structure**: YAML template uses flat `upstream` instead of `cumulative_tags`/`type_specific`
5. **Quality Gate Layer Mismatch**: TASKS_MVP_QUALITY_GATE_VALIDATION.md header says Layer 10

**Alignment Note**: Fixes follow the pattern established in `FTEST-MVP-TEMPLATE_FIX_PLAN.md`, `ITEST-MVP-TEMPLATE_FIX_PLAN.md`, and `UTEST-MVP-TEMPLATE_FIX_PLAN.md` for cross-artifact consistency.

## Gap Summary Table

| Gap ID | File | Issue | Severity |
| ------ | ---- | ----- | -------- |
| GAP-01 | TASKS-MVP-TEMPLATE.md | File does not exist (broken symlink target) | CRITICAL |
| GAP-02 | TASKS_MVP_SCHEMA.yaml | Layer incorrectly set to 10 (should be 11) | HIGH |
| GAP-03 | TASKS-MVP-TEMPLATE.yaml | Traceability uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-04 | TASKS_MVP_SCHEMA.yaml | Traceability schema uses `upstream` instead of `cumulative_tags`/`type_specific` structure | HIGH |
| GAP-05 | Multiple Files | Section count inconsistency (Schema: 15, Rules: 11, YAML: 13) | HIGH |
| GAP-06 | TASKS_MVP_QUALITY_GATE_VALIDATION.md | Metadata layer incorrectly set to 10 | MEDIUM |
| GAP-07 | TASKS-MVP-TEMPLATE.yaml | Missing TASKS-specific type_specific tags definition | MEDIUM |
| GAP-08 | TASKS_MVP_SCHEMA.yaml | x-validation-rules reference `upstream` instead of `type_specific` | MEDIUM |
| GAP-09 | TASKS-TEMPLATE.md | Broken symlink should be removed or fixed | LOW |
| GAP-10 | README.md | Section count says "11" but some files reference 13 | LOW |
| GAP-11 | TASKS_MVP_CREATION_RULES.md | Cumulative tags section may need verification | LOW |
| GAP-12 | TASKS_MVP_VALIDATION_RULES.md | Section structure needs alignment with final template | LOW |

---

## Detailed Gap Analysis

### GAP-01: TASKS-MVP-TEMPLATE.md Does Not Exist (CRITICAL)

**Location**: `ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.md`

**Current State**: File does not exist. A symlink `TASKS-TEMPLATE.md -> TASKS-MVP-TEMPLATE.md` points to this non-existent file.

**Required**: Create TASKS-MVP-TEMPLATE.md based on:
- TASKS-MVP-TEMPLATE.yaml structure (primary reference)
- TASKS_MVP_SCHEMA.yaml requirements
- Pattern from other MVP templates (SPEC-MVP-TEMPLATE.md, FTEST-MVP-TEMPLATE.md)

**MD Template Structure** (derived from YAML template 13 sections):

```markdown
# TASKS-NN: [Task Name] Task Breakdown

## 1. Document Control
## 2. Scope Overview
## 3. Dependency Graph
## 4. Task Registry
## 5. AI-Structured Execution Sequence
## 6. API Implementation Tasks
## 7. Implementation Contracts (Optional)
## 8. Implementation Contract Code Examples (Optional)
## 9. Development Plan Tracking
## 10. Unit Test Results
## 11. Implementation Summary
## 12. Traceability
## 13. Version History
```

**Fix**: Create new TASKS-MVP-TEMPLATE.md file with 13-section structure

---

### GAP-02: TASKS_MVP_SCHEMA.yaml Layer Incorrect

**Location**: Lines 14-15

**Current**:

```yaml
layer:
  type: integer
  const: 10
```

**Required**:

```yaml
layer:
  type: integer
  const: 11
```

**Fix**: Change layer const from 10 to 11

---

### GAP-03: TASKS-MVP-TEMPLATE.yaml Traceability Structure

**Location**: Lines 330-354 (traceability section)

**Current**:

```yaml
traceability:
  upstream:
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Technical specification"
    - tag: "@req"
      reference: "REQ.NN.27.SS"
      description: "Atomic requirements"
    # ... flat structure
  downstream:
    - tag: "@impl"
      reference: "Implementation code"
      description: "Code implementation"
```

**Required** (10 cumulative tags for Layer 11 + TASKS-specific):

```yaml
traceability:
  cumulative_tags:
    - tag: "@brd"
      reference: "BRD.NN.TT.SS"
      description: "Business requirement"
    - tag: "@prd"
      reference: "PRD.NN.TT.SS"
      description: "Product requirement"
    - tag: "@ears"
      reference: "EARS.NN.25.SS"
      description: "EARS statement"
    - tag: "@bdd"
      reference: "BDD.NN.14.SS"
      description: "BDD scenario"
    - tag: "@adr"
      reference: "ADR-NN"
      description: "Architecture decision"
    - tag: "@sys"
      reference: "SYS.NN.26.SS"
      description: "System requirement"
    - tag: "@req"
      reference: "REQ.NN.27.SS"
      description: "Atomic requirement"
    - tag: "@ctr"
      reference: "CTR-NN"
      description: "Data contract (if exists)"
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Technical specification"
    - tag: "@tspec"
      reference: "TSPEC.NN.TT.SS"
      description: "Test specification"
  type_specific:
    - tag: "@spec"
      reference: "SPEC-NN"
      description: "Primary specification for task breakdown"
    - tag: "@tspec"
      reference: "TSPEC.NN.TT.SS"
      description: "Test specification reference"
  downstream:
    - tag: "@impl"
      reference: "src/[module].py"
      description: "Implementation code"
    - tag: "@code"
      reference: "src/[component]/"
      description: "Source code location"
```

**Fix**: Restructure traceability section with cumulative_tags, type_specific, and downstream subsections

---

### GAP-04: TASKS_MVP_SCHEMA.yaml Traceability Structure

**Location**: Lines 265-295 (traceability property)

**Current**: Uses `upstream` array structure

**Required**: Match updated structure with `cumulative_tags`, `type_specific`, and `downstream` subsections

```yaml
traceability:
  type: object
  required:
    - cumulative_tags
    - type_specific
  properties:
    cumulative_tags:
      type: array
      minItems: 3
      description: "Layer 1-10 upstream artifact references"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@brd", "@prd", "@ears", "@bdd", "@adr", "@sys", "@req", "@ctr", "@spec", "@tspec"]
          reference:
            type: string
          description:
            type: string
    type_specific:
      type: array
      minItems: 1
      description: "TASKS-specific traceability tags"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@spec", "@tspec"]
          reference:
            type: string
          description:
            type: string
    downstream:
      type: array
      description: "Downstream artifact references"
      items:
        type: object
        required:
          - tag
          - reference
        properties:
          tag:
            type: string
            enum: ["@impl", "@code"]
          reference:
            type: string
          description:
            type: string
```

**Fix**: Restructure schema traceability to validate new structure with three subsections

---

### GAP-05: Section Count Inconsistency

**Affected Files**:
- TASKS_MVP_SCHEMA.yaml: `required_sections` has 15 items
- TASKS_MVP_VALIDATION_RULES.md: Says "11 sections"
- TASKS_MVP_CREATION_RULES.md: Says "11 sections"
- TASKS-MVP-TEMPLATE.yaml: Has 13 numbered sections
- README.md: References "11 sections"

**Analysis**:
The YAML template has 13 sections as the authoritative structure:
1. Document Control
2. Scope Overview
3. Dependency Graph
4. Task Registry
5. AI-Structured Execution Sequence
6. API Implementation Tasks
7. Implementation Contracts (Optional)
8. Implementation Contract Code Examples (Optional)
9. Development Plan Tracking
10. Unit Test Results
11. Implementation Summary
12. Traceability
13. Version History

**Fix**:
- Update schema required_sections to match 13-section structure
- Update validation/creation rules to reference 13 sections
- Update README to reference 13 sections

---

### GAP-06: TASKS_MVP_QUALITY_GATE_VALIDATION.md Layer Mismatch

**Location**: Lines 5-12 (metadata)

**Current**:

```yaml
custom_fields:
  artifact_type: TASKS
  layer: 10
```

**Required**:

```yaml
custom_fields:
  artifact_type: TASKS
  layer: 11
```

**Fix**: Update layer from 10 to 11 in metadata

---

### GAP-07: TASKS-MVP-TEMPLATE.yaml Missing Type-Specific Tags

**Location**: Traceability section

**Current**: No explicit type_specific section; only upstream/downstream

**Required**: Add TASKS-specific tags:
- `@spec` - Primary: TASKS decompose technical specifications
- `@tspec` - Secondary: Test specifications provide test coverage reference

**Fix**: Add type_specific subsection to traceability

---

### GAP-08: TASKS_MVP_SCHEMA.yaml x-validation-rules

**Location**: x-validation-rules section (if exists)

**Current**: May reference `upstream`

**Required**: Reference `type_specific` for TASKS-specific tag validation

**Fix**: Update x-validation-rules to reference `type_specific` instead of `upstream`

---

### GAP-09: Broken Symlink TASKS-TEMPLATE.md

**Location**: `ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.md`

**Current**: Symlink pointing to non-existent `TASKS-MVP-TEMPLATE.md`

**Required**: Either:
1. Create the target file (GAP-01), making symlink valid
2. Or remove the symlink if not needed

**Fix**: Create TASKS-MVP-TEMPLATE.md (resolves this automatically)

---

### GAP-10: README.md Section Count

**Location**: Section count references

**Current**: Says "11 sections"

**Required**: Update to "13 sections" to match YAML template

**Fix**: Update section count in README

---

### GAP-11: TASKS_MVP_CREATION_RULES.md Verification

**Location**: Cumulative tags section

**Current**: Needs verification that cumulative tags are correctly documented

**Required**: Verify alignment with 10 cumulative tags (Layer 1-10)

**Fix**: Verify and update if needed

---

### GAP-12: TASKS_MVP_VALIDATION_RULES.md Section Alignment

**Location**: Section structure references

**Current**: References 11-section structure

**Required**: Update to 13-section structure

**Fix**: Update section references to match template

---

## Implementation Phase

### Phase 1: Create Missing MD Template (GAP-01, GAP-09)

**Files to create**:

1. `ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.md` - Create from YAML template

**Steps**:

1. Create TASKS-MVP-TEMPLATE.md with 13-section structure
2. Include AI_CONTEXT block with cumulative tags
3. Include all sections from YAML template
4. Symlink will automatically become valid

### Phase 2: Fix Layer and Traceability in Schema (GAP-02, GAP-04, GAP-08)

**Files to modify**:

1. `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_SCHEMA.yaml`

**Steps**:

1. Change layer const from 10 to 11
2. Restructure traceability property with cumulative_tags, type_specific, downstream
3. Update x-validation-rules to reference type_specific

### Phase 3: Fix YAML Template Traceability (GAP-03, GAP-07)

**Files to modify**:

1. `ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.yaml`

**Steps**:

1. Restructure traceability with cumulative_tags (10 tags), type_specific (@spec, @tspec), downstream
2. Verify all sections are properly numbered

### Phase 4: Fix Section Count Consistency (GAP-05, GAP-10, GAP-11, GAP-12)

**Files to modify**:

1. `ai_dev_ssd_flow/11_TASKS/README.md` - Update section count
2. `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_VALIDATION_RULES.md` - Update section references
3. `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_CREATION_RULES.md` - Update section references

**Steps**:

1. Update README to reference 13 sections
2. Update validation rules section references
3. Update creation rules section references

### Phase 5: Fix Quality Gate Metadata (GAP-06)

**Files to modify**:

1. `ai_dev_ssd_flow/11_TASKS/TASKS_MVP_QUALITY_GATE_VALIDATION.md`

**Steps**:

1. Update layer in metadata from 10 to 11

---

## Verification Commands

```bash
# Verify MD template exists
ls -la ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.md
# Expected: File exists (not broken symlink)

# Verify symlink is valid
file ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.md
# Expected: "symbolic link to TASKS-MVP-TEMPLATE.md" (valid)

# Verify layer in schema
grep -n "const: 11" ai_dev_ssd_flow/11_TASKS/TASKS_MVP_SCHEMA.yaml | head -5
# Expected: layer const is 11

# Verify traceability structure in YAML
grep -n "cumulative_tags\|type_specific" ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.yaml
# Expected: Both sections present

# Verify traceability structure in schema
grep -n "cumulative_tags\|type_specific" ai_dev_ssd_flow/11_TASKS/TASKS_MVP_SCHEMA.yaml
# Expected: Both sections present

# Verify MD template has cumulative tags section
grep -n "Cumulative Tags" ai_dev_ssd_flow/11_TASKS/TASKS-MVP-TEMPLATE.md
# Expected: Section header present

# Verify Quality Gate layer
grep "layer: 11" ai_dev_ssd_flow/11_TASKS/TASKS_MVP_QUALITY_GATE_VALIDATION.md
# Expected: layer is 11

# Verify section count in README
grep -i "13 sections\|13-section" ai_dev_ssd_flow/11_TASKS/README.md
# Expected: 13 sections mentioned
```

---

## Risk Assessment

| Risk | Mitigation |
| ---- | ---------- |
| Creating new MD template may introduce inconsistencies | Base strictly on YAML template structure |
| Schema changes break validation | Test with existing TASKS documents first |
| Section count change affects autopilot | Verify doc-tasks-autopilot skill compatibility |
| Backward compatibility | Existing documents remain valid (additive changes) |
| Cross-artifact inconsistency | Follow TSPEC fix patterns exactly |
| Layer change affects workflow | Update all layer references consistently |

---

## Files Modified Summary

| File | Changes |
| ---- | ------- |
| `TASKS-MVP-TEMPLATE.md` | **CREATE**: New 13-section MD template with AI_CONTEXT and cumulative tags |
| `TASKS-MVP-TEMPLATE.yaml` | Restructure traceability with cumulative_tags, type_specific, downstream |
| `TASKS_MVP_SCHEMA.yaml` | Fix layer to 11; restructure traceability; update x-validation-rules |
| `TASKS_MVP_QUALITY_GATE_VALIDATION.md` | Fix layer in metadata from 10 to 11 |
| `README.md` | Update section count to 13 |
| `TASKS_MVP_VALIDATION_RULES.md` | Update section references to 13-section structure |
| `TASKS_MVP_CREATION_RULES.md` | Update section references to 13-section structure |

---

## Completion Criteria

- [x] TASKS-MVP-TEMPLATE.md exists with 13-section structure
- [x] TASKS-MVP-TEMPLATE.md AI_CONTEXT mentions cumulative tags
- [x] TASKS-MVP-TEMPLATE.md Section 8 has cumulative tags subsection
- [x] TASKS-TEMPLATE.md symlink is valid (points to existing file)
- [x] TASKS_MVP_SCHEMA.yaml layer is 11
- [x] TASKS_MVP_SCHEMA.yaml traceability uses cumulative_tags, type_specific structure
- [x] TASKS-MVP-TEMPLATE.yaml traceability restructured with cumulative_tags, type_specific
- [x] TASKS_MVP_QUALITY_GATE_VALIDATION.md layer is 11
- [x] README.md references 13 sections
- [x] TASKS_MVP_VALIDATION_RULES.md aligned (inherits from schema)
- [x] TASKS_MVP_CREATION_RULES.md aligned (inherits from schema)
- [x] All verification commands pass

---

## TASKS-Specific Considerations

**Type-Specific Tags for TASKS**:
- `@spec` - Primary: TASKS decompose technical specifications into executable tasks
- `@tspec` - Secondary: Test specifications provide coverage context

**Differentiation from Other Artifacts**:
- SPEC focuses on implementation details
- TSPEC (all subtypes) focuses on test specifications
- TASKS focuses on task breakdown for AI-structured execution
- TASKS is Layer 11 (between SPEC/TSPEC at Layer 9-10 and Code at Layer 12)

**Cumulative Tags for TASKS (Layer 11)**:
All 10 upstream tags: @brd, @prd, @ears, @bdd, @adr, @sys, @req, @ctr, @spec, @tspec

---

## Version History

| Version | Date | Changes | Author |
| ------- | ---- | ------- | ------ |
| 1.2 | 2026-02-26 | Extended fixes: Updated VALIDATION_RULES, CREATION_RULES, QUALITY_GATE with 13 sections, Layer 11, 9 tags | System |
| 1.1 | 2026-02-26 | All primary gaps fixed; Status COMPLETED | System |
| 1.0 | 2026-02-26 | Initial fix plan with 12 gaps across 5 phases | System |
