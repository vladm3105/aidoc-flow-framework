---
title: "Document-Type Validation Template Guide"
tags:
  - framework-guide
  - template
  - scaling-pattern
custom_fields:
  document_type: implementation-guide
  artifact_type: framework-support
  priority: high
  version: "1.0"
  scope: all-document-types
---

# Document-Type Validation Template Guide

**Purpose:** Step-by-step guide to create validation guides for any document type using the established REQ template pattern.

**Template Base:** REQ validation guides are the complete reference implementation. Copy and adapt for other types.

---

## Quick Summary of Pattern

Every document type (BRD, PRD, REQ, SPEC, etc.) needs:

```
{LAYER}/{TYPE_FOLDER}/
├── {TYPE}_VALIDATION_STRATEGY.md          [Quick reference: gates, architecture]
├── {TYPE}_VALIDATION_COMMANDS.md          [CLI commands specific to type]
├── {TYPE}_AI_VALIDATION_DECISION_GUIDE.md [Decision patterns, edge cases]
├── scripts/
│   ├── README.md                          [Quick start for tools]
│   ├── validate_all.sh                    [Master orchestrator]
│   ├── validate_{type}_quality_score.sh   [Quality gates validator]
│   ├── validate_{type}_spec_readiness.py  [Readiness scorer]
│   ├── validate_{type}_template.sh        [Template compliance]
│   └── validate_{type}_ids.py             [ID format validator]
└── [existing templates, examples, etc.]
```

---

## File Templates

### 1. {TYPE}_VALIDATION_STRATEGY.md

**Copy template from:** `07_REQ/REQ_VALIDATION_STRATEGY.md`

**Adapt by:**

```markdown
1. Replace {TYPE} prefix in title
2. Update gate table (e.g., BRD gates vs REQ gates)
3. Update validator references ({TYPE}_quality_score.sh instead of req_quality_score.sh)
4. Adjust gate descriptions for document type
5. Update cross-references to framework docs
6. Customize usage patterns (BRD workflow ≠ REQ workflow)
```

**Example for BRD:**

```markdown
# BRD Validation Strategy (Quick Reference)

**Purpose:** Quick reference for BRD validation architecture, gates, and patterns.

...

## {TYPE} Quality Gates

| Gate | Type | Name | Brief |
|------|------|------|-------|
| 01 | ERROR | Placeholder Detection | Remove TBD, TODO, FIXME |
| 02 | ERROR | Epic Structure | 8-12 epics required |
...
```

---

### 2. {TYPE}_VALIDATION_COMMANDS.md

**Copy template from:** `07_REQ/REQ_VALIDATION_COMMANDS.md`

**Adapt by:**

```markdown
1. Replace {TYPE} prefix in title
2. Update master orchestrator reference
3. List type-specific validators
4. Update command examples (e.g., BRD-specific scoring)
5. Adjust workflows to match type (BRD workflow ≠ REQ workflow)
6. Update CLI flags relevant to type
```

**Example for BRD:**

```markdown
# BRD Validation Commands

**Purpose:** Quick reference for BRD-specific validation commands.

...

## Master Orchestrator

bash scripts/validate_all.sh --file <brd-file.md>
bash scripts/validate_all.sh --directory <folder>

## Individual Validators

### Quality Gate Validator (BRD-specific gates)
bash scripts/validate_brd_quality_score.sh <directory>

### SPEC-Readiness Scorer
python3 scripts/validate_brd_spec_readiness.py --brd-file <file>
```

---

### 3. {TYPE}_AI_VALIDATION_DECISION_GUIDE.md

**Copy template from:** `07_REQ/REQ_AI_VALIDATION_DECISION_GUIDE.md`

**Adapt by:**

```markdown
1. Replace REQ with {TYPE} throughout
2. Add type-specific GATE patterns
3. Update decision matrices to match type gates
4. Add type-specific edge cases
5. Document type-specific workarounds
6. Include type-specific troubleshooting
```

**Example sections for BRD:**

```markdown
## Common BRD Validation Issues

### Issue: "Epic count out of range (5 required, 3-12 expected)"

**Error:** GATE-02
**Causes:** Too few epics defined
**Resolution:** Add 2-7 more epics or validate that 3 truly covers all customer needs

### Issue: "Story acceptance criteria incomplete"

**Error:** GATE-08
**Causes:** User stories lack measurable acceptance criteria
**Resolution:** Add 3-5 acceptance criteria per story
```

---

### 4. scripts/README.md

**Copy template from:** `07_REQ/scripts/README.md`

**Adapt by:**

```markdown
1. Replace REQ references with {TYPE}
2. Update tool descriptions for type-specific validators
3. Adjust examples to match type workflows
4. Update cross-references to {TYPE}_VALIDATION_*.md docs
5. Customize troubleshooting for type-specific issues
```

---

## Validator Script Templates

### Master Orchestrator: validate_all.sh

**Copy template from:** `07_REQ/scripts/validate_all.sh`

**Key sections to customize:**

```bash
# 1. Script header - update documentation
# 2. VALIDATORS array - list type-specific validators
# 3. Validation modes - file vs directory handling
# 4. Output formatting - type-specific success/failure messages
# 5. Exit codes - match type-specific severities
```

**Pseudo-code adaptation:**

```bash
#!/bin/bash

# BRD-Specific Master Orchestrator
MODE="$1"
TARGET="$2"

case "$MODE" in
  --file)
    validate_brd_template.sh "$TARGET"
    python3 validate_brd_spec_readiness.py --brd-file "$TARGET"
    python3 validate_brd_ids.py --brd-file "$TARGET"
    ;;
  --directory)
    validate_brd_quality_score.sh "$TARGET"
    python3 validate_brd_spec_readiness.py --directory "$TARGET"
    python3 validate_brd_ids.py --directory "$TARGET"
    ;;
esac
```

---

### Type-Specific Validators

Each validator should follow this pattern:

**validate_{type}_quality_score.sh:**
```bash
# Purpose: Run N gates on directory (corpus-level)
# Inputs: directory path
# Output: Gate results, color-coded
# Exit code: 0 (pass) or 2 (error) or 1 (warning)
```

**validate_{type}_template.sh:**
```bash
# Purpose: Check document structure (file-level)
# Inputs: file path
# Output: Section validation results
# Exit code: 0 (pass) or 2 (error)
```

**validate_{type}_spec_readiness.py:**
```bash
# Purpose: Score readiness 0-100%
# Inputs: file or directory + threshold (default 90)
# Output: Score + detailed breakdown
# Exit code: 0 (pass) or 1 (fail threshold)
```

**validate_{type}_ids.py:**
```bash
# Purpose: Validate ID format and uniqueness
# Inputs: file or directory
# Output: ID validation results
# Exit code: 0 (pass) or 2 (error)
```

---

## Implementation Checklist

Use this checklist to implement validation guides for a new document type:

### Phase 1: Documentation (3 files)

- [ ] Create `{TYPE}_VALIDATION_STRATEGY.md`
  - [ ] Copy structure from REQ version
  - [ ] Update gate table with type-specific gates
  - [ ] Update architecture description
  - [ ] Customize workflows

- [ ] Create `{TYPE}_VALIDATION_COMMANDS.md`
  - [ ] List type-specific validators
  - [ ] Provide CLI examples
  - [ ] Update troubleshooting

- [ ] Create `{TYPE}_AI_VALIDATION_DECISION_GUIDE.md`
  - [ ] Document type-specific decision patterns
  - [ ] Add edge cases
  - [ ] Include workarounds

### Phase 2: Scripts (Master Orchestrator)

- [ ] Create `scripts/validate_all.sh`
  - [ ] File mode delegation
  - [ ] Directory mode delegation
  - [ ] Error handling
  - [ ] Output formatting

- [ ] Create `scripts/README.md`
  - [ ] Installation instructions
  - [ ] Quick start examples
  - [ ] Troubleshooting

### Phase 3: Individual Validators (5 scripts)

- [ ] Create `scripts/validate_{type}_quality_score.sh`
  - [ ] Implement N gates (type-specific count)
  - [ ] Color-coded output
  - [ ] Exit codes

- [ ] Create `scripts/validate_{type}_template.sh`
  - [ ] Check required sections
  - [ ] Validate structure
  - [ ] Metadata validation

- [ ] Create `scripts/validate_{type}_spec_readiness.py`
  - [ ] Scoring logic (0-100%)
  - [ ] Factor weighting
  - [ ] Threshold comparison

- [ ] Create `scripts/validate_{type}_ids.py`
  - [ ] ID format validation
  - [ ] Uniqueness check
  - [ ] Hierarchy validation

- [ ] Create `scripts/add_crosslinks_{type}.py` (if needed)
  - [ ] Cross-link generation
  - [ ] @depends/@discoverability tags
  - [ ] Pre-validation helper

### Phase 4: Testing & Documentation

- [ ] Test all scripts with sample documents
- [ ] Verify exit codes
- [ ] Check error messages
- [ ] Create example workflows
- [ ] Update framework index (VALIDATION_GUIDES_INDEX.md)

---

## Gate Count by Document Type

Recommended number of validation gates per type:

| Type | Gates | Complexity | Focus |
|------|-------|-----------|-------|
| BRD | 10-12 | Medium | Epic/story structure, acceptance criteria |
| PRD | 12-14 | Medium-High | Feature completeness, API contracts |
| EARS | 8-10 | Low-Medium | Event structure, action completeness |
| BDD | 10-12 | Medium | Scenario structure, step definitions |
| ADR | 6-8 | Low | Decision rationale, alternatives |
| SYS | 12-14 | High | System architecture, component definition |
| REQ | 14-16 | High | Traceability, SPEC-readiness, domains |
| CTR | 8-10 | Medium | Contract structure, type safety |
| SPEC | 14-16 | High | Code generation, schema validation |
| TASKS | 6-8 | Low-Medium | Closure criteria, priority, dependencies |

---

## Example: Scaling from REQ to BRD

### Step 1: Copy REQ files

```bash
cd ai_dev_flow/01_BRD

# Copy REQ guides and adapt
cp ../07_REQ/REQ_VALIDATION_STRATEGY.md BRD_VALIDATION_STRATEGY.md
cp ../07_REQ/REQ_VALIDATION_COMMANDS.md BRD_VALIDATION_COMMANDS.md
cp ../07_REQ/REQ_AI_VALIDATION_DECISION_GUIDE.md BRD_AI_VALIDATION_DECISION_GUIDE.md

# Copy scripts and adapt
cp -r ../07_REQ/scripts/* scripts/
```

### Step 2: Adapt documentation

```markdown
# Find & replace:
- REQ → BRD
- req → brd
- requirement → epic/story
- REQ-NN.MM → BRD-NN.MM (or BRD-NN depending on structure)
- 11 sections → X sections (BRD-specific)
- 14 gates → Y gates (BRD-specific)
```

### Step 3: Adapt validators

```bash
# Update validate_all.sh to call BRD validators
# Update quality_score script for BRD gates
# Update template script for BRD structure
# Update ID validator for BRD naming
```

### Step 4: Test

```bash
# Run against sample BRD documents
bash scripts/validate_all.sh --file sample_brd.md
bash scripts/validate_all.sh --directory sample_brd_folder
```

---

## Framework Integration

After creating {TYPE} guides:

1. **Update VALIDATION_GUIDES_INDEX.md**
   - Add row to document-type table
   - Update status indicator

2. **Update VALIDATION_COMMANDS.md**
   - Add section for new type
   - Reference type-specific commands

3. **Update VALIDATION_STRATEGY_GUIDE.md**
   - Add type-specific architecture note
   - Link to type-specific strategy

4. **Update README at framework level**
   - Add new type to supported list
   - Link to guides

---

## Scalability Principles

1. **DRY (Don't Repeat Yourself)**
   - Universal rules stay in framework docs
   - Type-specific rules in type docs

2. **Clear Separation**
   - Framework = rules for all types
   - Type-specific = rules for one type

3. **Consistent Naming**
   - Framework: `VALIDATION_*.md`
   - Type-specific: `{TYPE}_VALIDATION_*.md`

4. **Modular Validators**
   - Each validator does one thing
   - Master orchestrator coordinates
   - Easy to update individual gates

5. **Documentation Mirrors Code**
   - Documents match validator structure
   - Examples match actual commands
   - Troubleshooting matches real errors

---

## Maintenance & Evolution

As validators improve:

1. Update validator script
2. Update corresponding guide section
3. Add example to AI_VALIDATION_DECISION_GUIDE.md
4. Test with sample documents
5. Update framework index with date

---

**Last Updated:** 2026-01-24T00:00:00  
**Status:** Template guide for scaling validation framework  
**Audience:** Framework architects, document-type implementers  
**Scope:** Implementation guide for new document types
