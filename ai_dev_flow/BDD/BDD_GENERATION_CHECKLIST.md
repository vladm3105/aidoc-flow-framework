---
title: "BDD Suite Generation Checklist"
tags:
  - checklist
  - layer-4-artifact
  - bdd-workflow
custom_fields:
  document_type: checklist
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

# BDD Suite Generation Checklist (Section-Based Format)

**Version**: 2.0
**Date**: 2025-12-27
**Purpose**: Step-by-step checklist for creating section-based BDD suites
**Framework**: AI Dev Flow SDD methodology

**IMPORTANT**: This checklist enforces section-based format ONLY. Legacy formats (single-file, directory-based) are prohibited.

---

## Pre-Generation Requirements

### Upstream Artifacts Required

- [ ] **BRD** exists and is approved
- [ ] **PRD** exists with threshold registry section
- [ ] **EARS** exists with formal requirements

### Planning Decisions

- [ ] Suite number assigned (NN)
- [ ] Suite title defined ("Human Readable Title")
- [ ] Section split strategy identified (3-8 sections recommended)
- [ ] Section slugs determined (descriptive_names for each section)
- [ ] IANA timezone selected (default: `America/New_York`)
- [ ] Threshold keys identified from PRD

**Section Planning Example**:
```
BDD-02: Knowledge Engine Test Suite
├── Section 1: Ingest and Analysis
├── Section 2: Query Processing
├── Section 3: Learning and Adaptation
└── Section 4: Performance Monitoring
```

---

## Phase 1: Create Index File

### Index File Creation

- [ ] Create `docs/BDD/BDD-NN.0_index.md` from `BDD-SECTION-0-TEMPLATE.md`
- [ ] Update YAML frontmatter:
  - [ ] Set `title` to actual suite title
  - [ ] Update `parent_doc` reference (if applicable)
  - [ ] Update `upstream_artifacts` with BRD/PRD/EARS IDs
- [ ] Update Document Control table:
  - [ ] Set document ID: `BDD-NN.0`
  - [ ] Set current date (created, last updated)
  - [ ] Set document owner/team
- [ ] Update Suite Overview:
  - [ ] Define purpose (what this suite tests)
  - [ ] Define scope (in scope / out of scope)
- [ ] Create Section File Map table stub (will complete in Phase 3)
- [ ] Create Traceability Matrix stub (will complete in Phase 4)

**Template Source**: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-SECTION-0-TEMPLATE.md`

---

## Phase 2: Plan Section Split

### Section Split Strategy

Choose split criteria (in priority order):

1. **Domain/Module Boundaries** (Preferred)
   - Example: Ingest, Query, Learning, Monitoring
   - Aligns with architectural components

2. **Lifecycle/Phase Management**
   - Example: Setup, Operation, Teardown, Recovery
   - Aligns with temporal workflow

3. **Quality Attributes** (Cross-cutting)
   - Example: Performance, Security, Reliability
   - Aligns with non-functional requirements

4. **Requirement Groups** (EARS/PRD Alignment)
   - Example: EARS sections map 1:1 to BDD sections
   - Maintains traceability

### Section Planning Checklist

- [ ] Identify 3-8 logical sections (not too many, not too few)
- [ ] Estimate scenarios per section (target: 6-12 scenarios)
- [ ] Estimate lines per section (target: 300-400 lines, max 500)
- [ ] Map EARS requirements to sections
- [ ] Assign section numbers sequentially (1, 2, 3, 4...)
- [ ] Define section slugs (lowercase, underscores)

**Decision Matrix**:
| Section | Focus Area | EARS Range | Est. Scenarios | Est. Lines |
|---------|------------|------------|----------------|------------|
| BDD-02.1 | Ingest | EARS.02.01-05 | 8 | 350 |
| BDD-02.2 | Query | EARS.02.06-12 | 10 | 420 |
| BDD-02.3 | Learning | EARS.02.13-18 | 7 | 280 |

---

## Phase 3: Create Section Files

### For Each Section

- [ ] Create section file: `docs/BDD/BDD-NN.SS_{slug}.feature`
- [ ] Copy from `BDD-SECTION-TEMPLATE.feature`
- [ ] Update file-level traceability tags:
  ```gherkin
  @section: N.S
  @parent_doc: BDD-NN
  @index: BDD-NN.0_index.md
  @brd:BRD.NN.EE.SS
  @prd:PRD.NN.EE.SS
  @ears:EARS.NN.SS.RR
  ```
- [ ] Update Feature declaration:
  - [ ] Title: `Feature: BDD-NN.SS: [Section Name]`
  - [ ] As a/I want/So that statement
- [ ] Update Background with timezone and preconditions
- [ ] Author scenarios (see Section File Requirements below)

**Template Source**: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-SECTION-TEMPLATE.feature`

### Section File Requirements

For each section file:

- [ ] ≤500 lines (soft limit: 400)
- [ ] ≤12 scenarios per Feature block
- [ ] Use `America/New_York` or ET with HH:MM:SS times
- [ ] Replace all numeric durations/retries with `@threshold:` keys
- [ ] Use canonical step wording for reusability
- [ ] Normalize Examples tables (separate columns, no composite fields)
- [ ] Quote error codes in steps, unquote in tables
- [ ] Map scenarios to EARS requirements with @scenario_id tags

### Scenario Coverage Per Section

- [ ] **Primary success paths** (@primary tag)
- [ ] **Error handling** (@negative tag)
- [ ] **Edge cases** (@edge_case, @boundary tags)
- [ ] **Quality attributes** (@quality_attribute tag)
- [ ] **Data-driven tests** (Scenario Outline with Examples)

---

## Phase 4: Handle Oversized Sections (If Needed)

### When Section Exceeds 500 Lines

If a section file exceeds 500 lines or 12 scenarios:

**Option A: Create Subsections**

- [ ] Split section into subsections: `BDD-NN.SS.01_{slug}.feature`, `BDD-NN.SS.02_{slug}.feature`
- [ ] Copy from `BDD-SUBSECTION-TEMPLATE.feature`
- [ ] Update subsection traceability tags:
  ```gherkin
  @section: N.S.m
  @parent_section: N.S
  @parent_doc: BDD-NN
  @index: BDD-NN.0_index.md
  ```
- [ ] Each subsection ≤500 lines, ≤12 scenarios

**Option B: Create Aggregator (5+ Subsections)**

- [ ] Create aggregator: `BDD-NN.SS.00_{slug}.feature`
- [ ] Copy from `BDD-AGGREGATOR-TEMPLATE.feature`
- [ ] Add `@redirect` tag (MANDATORY)
- [ ] List all subsections in Feature description
- [ ] 0 scenarios (redirect stub only)
- [ ] Create numbered subsections: `.01`, `.02`, `.03`, etc.

**Template Sources**:
- Subsection: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-SUBSECTION-TEMPLATE.feature`
- Aggregator: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD-AGGREGATOR-TEMPLATE.feature`

---

## Phase 5: Threshold Registry Integration

### PRD Threshold Registry

- [ ] Identify all quantitative assertions in scenarios
- [ ] Add missing threshold keys to PRD registry:
  - [ ] `PRD.NN.timeout.*` keys
  - [ ] `PRD.NN.perf.*` keys
  - [ ] `PRD.NN.thresholds.*` keys
  - [ ] `PRD.NN.quality.*` keys
- [ ] Replace raw numbers in feature files with `@threshold:` references
- [ ] Verify all referenced keys exist in registry

### Threshold Validation

```bash
# Check for raw numeric values (should return 0 matches)
rg -n "WITHIN\s+[0-9]+\s+(seconds?|minutes?)" docs/BDD/BDD-NN.*.feature
rg -n "after\s+[0-9]+\s+(attempts?|retries?)" docs/BDD/BDD-NN.*.feature
```

---

## Phase 6: Update Index File

### Complete Index File

- [ ] Update Section File Map table with actual sections:
  ```markdown
  | Section | File | Scenarios | Lines | Status | Description |
  |---------|------|-----------|-------|--------|-------------|
  | 02.1 | BDD-02.1_ingest.feature | 8 | 350 | Active | Ingest and analysis tests |
  | 02.2 | BDD-02.2_query.feature | 10 | 420 | Active | Query processing tests |
  ```
- [ ] Update Traceability Matrix with upstream dependencies:
  ```markdown
  | BDD Section | Upstream Source | Description |
  |-------------|----------------|-------------|
  | BDD-02.1 | EARS.02.01-05 | Ingest requirements |
  | BDD-02.2 | EARS.02.06-12 | Query requirements |
  ```
- [ ] Update Execution Strategy (if needed)
- [ ] Update Quality Gates (if needed)

---

## Phase 7: Validation & Quality Gates

### Automated Validation

```bash
# Run section-based validation suite
python ai_dev_flow/scripts/validate_bdd_suite.py \
  --root docs/BDD \
  --prd-root docs/PRD
```

### Manual Validation Checklist

**File Organization**:
- [ ] All `.feature` files at `docs/BDD/` root level (no subdirectories)
- [ ] Index file exists: `BDD-NN.0_index.md`
- [ ] Section files follow pattern: `BDD-NN.SS_{slug}.feature`
- [ ] Subsections (if any) follow pattern: `BDD-NN.SS.mm_{slug}.feature`
- [ ] Aggregators (if any) follow pattern: `BDD-NN.SS.00_{slug}.feature`
- [ ] NO `features/` subdirectory
- [ ] NO `BDD-NN_{slug}/` directory structure

**Section File Quality**:
- [ ] No `.feature` exceeds 500 lines
- [ ] No Feature block exceeds 12 scenarios
- [ ] No non-Gherkin Markdown in `.feature` files
- [ ] All quantitative values use `@threshold:` keys
- [ ] Times have seconds; timezone is `America/New_York` or ET
- [ ] No ambiguous timezone abbreviations (EST, EDT, PST, PDT)

**Section Metadata Tags**:
- [ ] All files have `@section: N.S` or `@section: N.S.m` tag
- [ ] All files have `@parent_doc: BDD-NN` tag
- [ ] All files have `@index: BDD-NN.0_index.md` tag
- [ ] Subsections have `@parent_section: N.S` tag

**Aggregator Requirements** (if applicable):
- [ ] Aggregators have `@redirect` tag
- [ ] Aggregators have 0 scenarios
- [ ] Aggregators list all subsections in Feature description
- [ ] Aggregator subsection is `.00`

**Prohibited Patterns** (must be absent):
- [ ] NO `_partN` suffix in filenames
- [ ] NO single-file format: `BDD-NN_slug.feature`
- [ ] NO directory-based structure: `BDD-NN_{slug}/features/`

### Validation Output Expected

```
✓ BDD validation passed (no violations)
```

---

## Phase 8: Archive Original (if migrating)

If migrating from legacy format:

**From Single-File** (`BDD-NN_slug.feature`):
- [ ] Create `docs/BDD/archive/` subdirectory
- [ ] Move original to `archive/BDD-NN_slug.feature.txt`
- [ ] Rename with `.txt` extension to prevent execution

**From Directory-Based** (`BDD-NN_{slug}/`):
- [ ] Create `docs/BDD/archive/` subdirectory
- [ ] Move entire directory to `archive/BDD-NN_{slug}/`
- [ ] Add migration note in index file

---

## Phase 9: Documentation & Review

### Documentation Updates

- [ ] Update `BDD-000_index.md` with new suite entry
- [ ] Add suite to project documentation index
- [ ] Document section split rationale in index file

### Peer Review

- [ ] Code review of section files
- [ ] Validation of EARS requirement coverage
- [ ] Threshold key consistency check
- [ ] Step definition reusability review
- [ ] Section split logic review

---

## Phase 10: Commit & Integration

### Pre-Commit Checklist

- [ ] All validation checks pass (exit code 0)
- [ ] Index file complete and accurate
- [ ] Traceability tags verified
- [ ] No TODO/FIXME comments in feature files
- [ ] Section numbering sequential (no gaps)

### Git Commit

```bash
git add docs/BDD/BDD-NN.0_index.md
git add docs/BDD/BDD-NN.*.feature
git commit -m "feat(bdd): add BDD-NN [Suite Title] section-based suite

- Created section-based structure with [N] sections
- Index file: BDD-NN.0_index.md
- Section files: BDD-NN.1 through BDD-NN.[N]
- Implemented threshold registry integration
- All validation checks passed (500-line limit, 12-scenario limit)
- EARS coverage: [X] requirements across [Y] scenarios

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Common Issues & Troubleshooting

### Issue: Validation fails with "Prohibited single-file format detected"

**Symptom**: File named `BDD-NN_slug.feature` (no dot notation)

**Fix**: Rename to section-based format `BDD-NN.SS_{slug}.feature`

### Issue: Validation fails with "Prohibited directory structure"

**Symptom**: `BDD-NN_{slug}/` directory exists

**Fix**: Flatten to BDD root with section-based naming, archive legacy directory

### Issue: Validation fails with "Missing required index file"

**Symptom**: No `BDD-NN.0_index.md` file

**Fix**: Create index file from `BDD-SECTION-0-TEMPLATE.md`

### Issue: "Section file exceeds 500 lines"

**Fix**: Split into subsections using `BDD-NN.SS.mm_{slug}.feature` format

### Issue: "Raw duration found" errors

**Fix**: Replace numeric values with `@threshold:PRD.NN.timeout.<key>` references

### Issue: "Ambiguous timezone abbreviation"

**Fix**: Replace EST/EDT/etc. with `America/New_York` or ET

### Issue: "Aggregator file missing @redirect tag"

**Fix**: Add `@redirect` tag to aggregator file (`.00` suffix)

### Issue: "Aggregator contains scenarios"

**Fix**: Remove all scenarios from aggregator (redirect stubs have 0 scenarios)

---

## References

- **BDD_SPLITTING_RULES.md** — Split-suite structure standards
- **BDD_VALIDATION_RULES.md** — Validation rules (CHECK 9)
- **BDD_CREATION_RULES.md** — General BDD creation guidelines
- **ID_NAMING_STANDARDS.md** — Element ID format (BDD.NN.TT.SS)
- **Scaffold Script**: `ai_dev_flow/scripts/scaffold_split_suite.sh`
- **Validation Script**: `ai_dev_flow/scripts/validate_bdd_suite.py`

---

**Document Path**: `/opt/data/docs_flow_framework/ai_dev_flow/BDD/BDD_GENERATION_CHECKLIST.md`
**Framework**: AI Dev Flow SDD
**Last Updated**: 2025-12-27
