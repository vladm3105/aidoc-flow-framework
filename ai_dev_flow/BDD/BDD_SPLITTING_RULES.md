---
title: "BDD Section-Based File Organization"
tags:
  - framework-rules
  - layer-4-artifact
  - shared-architecture
  - mandatory-standard
custom_fields:
  document_type: splitting-rules
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
  version: "2.0"
---

# BDD Section-Based File Organization

**Purpose**: Define mandatory section-based structure for all BDD files, eliminating legacy single-file and directory-based formats.

**Version**: 2.0 (Section-Based ONLY)
**Last Updated**: 2025-12-27
**Status**: MANDATORY for all new and existing BDD files

---

## Goals

- Unify BDD naming with PRD/BRD section-based standards
- Keep feature files executable and maintainable (≤500 lines, ≤12 scenarios)
- Enforce nested suite structure under docs/BDD/BDD-NN_{slug}/
- Standardize section numbering and index files
- Eliminate backward compatibility with legacy formats

---

## Section-Based File Organization (MANDATORY)

All BDD files use section-based numbering (dot notation) aligned with PRD/BRD standards.

### Three Valid Patterns

#### 1. Section-Only Format (Primary)

**Pattern**: `^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$`
**Example**: `BDD-02.14_query_result_filtering.feature`
**Use When**: Standard section file (≤500 lines, ≤12 scenarios)

```gherkin
# File: BDD-02.14_query_result_filtering.feature
@section: 2.14
@parent_doc: BDD-02
@index: BDD-02.0_index.md
@brd:BRD.02.03.14
@prd:PRD.02.05.14
@ears:EARS.02.14.01

Feature: BDD-02.14: Query Result Filtering
  As a user querying the knowledge graph
  I want to filter results by multiple criteria
  So that I can find precisely relevant information
```

#### 2. Subsection Format (When Section >500 Lines)

**Pattern**: `^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$`
**Example**: `BDD-02.24.01_quality_performance.feature`
**Use When**: Section requires splitting (each subsection ≤500 lines)

```gherkin
# File: BDD-02.24.01_quality_performance.feature
@section: 2.24.01
@parent_section: 2.24
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.24.01: Performance Quality Attributes
  Performance scenarios for knowledge engine operations
```

#### 3. Aggregator Format (Optional Redirect Stub)

**Pattern**: `^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$`
**Example**: `BDD-02.12.00_query_graph_traversal.feature`
**Use When**: Organizing multiple subsections under one section

**Requirements**:
- `@redirect` tag MUST be present
- 0 scenarios (no executable tests)
- References to subsections in comments

```gherkin
# File: BDD-02.12.00_query_graph_traversal.feature
@redirect
@section: 2.12.00
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.12: Query Graph Traversal (Aggregator)

  This is a redirect stub. Test scenarios are in subsections:
  - BDD-02.12.01_basic_traversal.feature
  - BDD-02.12.02_path_finding.feature
  - BDD-02.12.03_relationship_queries.feature

Background:
  Given the system timezone is "America/New_York"
  # No scenarios - redirect only
```

---

## Numbering Scheme

### Index Files (.0 suffix)

**Format**: `BDD-NN.0_index.md`
**Example**: `BDD-02.0_index.md`
**Status**: MANDATORY for each BDD suite

```markdown
# BDD-02.0: Knowledge Engine Test Suite Index

## Sections

| Section | File | Scenarios | Lines | Status |
|---------|------|-----------|-------|--------|
| 2.1 | BDD-02.1_ingest.feature | 42 | 387 | Active |
| 2.2 | BDD-02.2_query.feature | 38 | 421 | Active |
| 2.3 | BDD-02.3_learning.feature | 35 | 358 | Active |
```

### Content Sections (.1, .2, .3, ...)

**Format**: `BDD-NN.SS_{slug}.feature`
**Numbering**: Sequential from 1 (no gaps)
**Example**: `BDD-02.1_ingest.feature`, `BDD-02.2_query.feature`

### Subsections (.SS.01, .SS.02, ...)

**Format**: `BDD-NN.SS.mm_{slug}.feature`
**Numbering**: Sequential from 01 within each section
**Example**: `BDD-02.3.01_learning_path.feature`, `BDD-02.3.02_bias_detection.feature`

### Aggregators (.SS.00)

**Format**: `BDD-NN.SS.00_{slug}.feature`
**Fixed Subsection**: Always .00
**Example**: `BDD-02.2.00_query.feature`

---

## File Organization

### Structure: Nested (per suite folder)

```
docs/BDD/BDD-02_knowledge_engine/
├── BDD-02.0_index.md                          # Index file (MANDATORY)
├── BDD-02.1_ingest.feature                    # Section 1
├── BDD-02.2_query.feature                     # Section 2
├── BDD-02.3.00_learning.feature               # Section 3 aggregator
├── BDD-02.3.01_learning_path.feature          # Section 3, subsection 01
├── BDD-02.3.02_bias_detection.feature         # Section 3, subsection 02
├── BDD-02_README.md                           # Optional companion doc
└── BDD-02_TRACEABILITY.md                     # Optional companion doc
```

### Suite Subdirectories Only

- ❌ **PROHIBITED**: `BDD-NN_{slug}/features/` (legacy nested features/)
- ❌ **PROHIBITED**: Additional subdirectories inside suite folder (beyond files shown)
- ✅ **REQUIRED**: All `.feature` files live inside the suite folder `BDD/BDD-NN_{slug}/`

### Optional Companion Documents

- `BDD-NN_README.md` - Suite overview
- `BDD-NN_TRACEABILITY.md` - Upstream/downstream mapping
- `BDD-NN_GLOSSARY.md` - Domain terms and thresholds

---

## Split Strategy (Prioritized)

When creating or splitting BDD suites, use these criteria in order:

### 1. Domain Modules (Preferred)

Group by functional domain or lifecycle phase:
- Ingest and Analysis
- Query and Search
- Learning and Adaptation
- State Management
- Validation and Safeguards
- Governance and Compliance

**Example**:
```
BDD-02.1_ingest_analysis.feature        # Ingest domain
BDD-02.2_query_semantic_search.feature  # Query domain
BDD-02.3_learning_adaptation.feature    # Learning domain
```

### 2. Requirement Groups (EARS/PRD Alignment)

Align with upstream EARS or PRD sections:
- Group contiguous EARS sections (2-3 per BDD section)
- Map to PRD feature areas

**Example**:
```
# EARS sections 01-05 → BDD section 1
BDD-02.1_data_ingestion.feature

# EARS sections 06-12 → BDD section 2
BDD-02.2_query_processing.feature
```

### 3. Quality Attributes (Cross-Cutting)

When scenarios span all domains:
- Performance testing
- Security scenarios
- Reliability testing
- Operational scenarios

**Example**:
```
BDD-02.24_quality_performance.feature
BDD-02.25_quality_security.feature
BDD-02.26_quality_reliability.feature
```

---

## Hard Limits and Guidance

### File Size Limits

- **Target**: 300–500 lines per `.feature` file
- **Maximum**: 600 lines (absolute)
- **Action**: If section exceeds 600 lines or approaches upper target → Split into subsections (`.SS.mm` format)

### Scenario Limits

- **Maximum**: 12 scenarios per Feature block
- **Recommendation**: 6-10 scenarios per Feature
- **Action**: If Feature exceeds 12 scenarios → Split into multiple Feature blocks or subsections

### Splitting Decision Tree

```
Is section >500 lines?
├─ NO  → Keep as section-only format (BDD-NN.SS_{slug}.feature)
└─ YES → Create subsections
    ├─ 2-4 subsections?
    │  └─ Create: BDD-NN.SS.01_{slug}.feature, BDD-NN.SS.02_{slug}.feature, ...
    └─ 5+ subsections?
       ├─ Create: BDD-NN.SS.00_{slug}.feature (aggregator)
       └─ Create: BDD-NN.SS.01_{slug}.feature, BDD-NN.SS.02_{slug}.feature, ...
```

---

## Prohibited Patterns (Cause Validation ERROR)

### 1. _partN Suffix

❌ **Bad**: `BDD-02_query_part1.feature`, `BDD-02_query_part2.feature`
✅ **Good**: `BDD-02.2.01_query_semantic.feature`, `BDD-02.2.02_query_graph.feature`

### 2. Single-File Format (Legacy)

❌ **Bad**: `BDD-02_knowledge_engine.feature` (single-file, no sections)
✅ **Good**: `BDD-02.1_ingest.feature`, `BDD-02.2_query.feature` (section-based)

### 3. Directory-Based Structure (Legacy)

❌ **Bad**:
```
BDD-02_knowledge_engine/
├── features/
│   ├── BDD-02_ingest.feature
│   └── BDD-02_query.feature
```

✅ **Good**:
```
BDD/
├── BDD-02.0_index.md
├── BDD-02.1_ingest.feature
└── BDD-02.2_query.feature
```

---

## Section Metadata Requirements

All `.feature` files MUST include section metadata tags:

```gherkin
@section: NN.SS              # Section number (e.g., 2.1, 2.14)
@parent_doc: BDD-NN          # Parent BDD suite (e.g., BDD-02)
@index: BDD-NN.0_index.md    # Index file reference
@brd:BRD.NN.EE.SS            # Upstream BRD element
@prd:PRD.NN.EE.SS            # Upstream PRD element
@ears:EARS.NN.SS.RR          # Upstream EARS requirement
```

**Feature Title Format**:
```gherkin
Feature: BDD-NN.SS: Domain Description
```

**Example**:
```gherkin
@section: 2.14
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.14: Query Result Filtering
```

---

## Migration from Legacy Formats

### From Single-File BDD

1. Identify logical domain splits (target: 3-6 sections)
2. Create `BDD-NN.0_index.md` from template
3. Split scenarios into section files (e.g., `BDD-03.1_registration.feature`)
4. Add section metadata tags to each `.feature` file
5. Archive original single-file as `BDD-NN_slug.feature.txt`
6. Validate with `python validate_bdd_suite.py --root docs/BDD`

### From Directory-Based BDD

1. Create `BDD-NN.0_index.md` from template
2. Rename feature files: `features/BDD-NN_domain.feature` → `BDD-NN.S_domain.feature`
3. Move to BDD root (no subdirectories)
4. Add section metadata tags to `.feature` files
5. Archive directory: `BDD-NN_{slug}/` → `archive/BDD-NN_{slug}/`
6. Validate with `python validate_bdd_suite.py --root docs/BDD`

---

## Canonical Step Phrases (Examples)

Use consistent step wording for reusability:

### Time and Timezone
```gherkin
Given the current time is "14:30:00" in "America/New_York"
And the system timezone is "America/New_York"
```

### State and Phase
```gherkin
Given the system is in "active" state
Given the system is in "pre_market" phase
```

### Transitions
```gherkin
When the system attempts to transition to "shutdown" state
```

### Validation Results
```gherkin
Then the validation result SHALL be "success"
And error code "VAL_001" SHALL be returned
```

### Threshold Assertions
```gherkin
Then it SHALL complete WITHIN @threshold:PRD.02.timeout.query_response
And memory usage SHALL NOT exceed @threshold:PRD.02.perf.max_memory
```

---

## Quality Gates (Pre-Commit)

Before committing BDD files:

- [ ] All `.feature` files live inside suite folder: docs/BDD/BDD-NN_{slug}/
- [ ] Index file exists: `BDD-NN.0_index.md`
- [ ] No `.feature` file exceeds 500 lines
- [ ] No Feature block exceeds 12 scenarios
- [ ] All quantitative values use `@threshold:` keys
- [ ] Times include seconds (HH:MM:SS) with IANA timezone
- [ ] No prohibited patterns (_partN, single-file, directory-based)
- [ ] Section metadata tags present in all `.feature` files
- [ ] Validation passes: `python validate_bdd_suite.py --root docs/BDD`

---

## References

- **ID_NAMING_STANDARDS.md** - BDD section-based naming patterns
- **BDD_SCHEMA.yaml** - Machine-readable validation rules
- **BDD-SECTION-0-TEMPLATE.md** - Index file template
- **BDD-SECTION-TEMPLATE.feature** - Content section template
- **BDD-SUBSECTION-TEMPLATE.feature** - Subsection template
- **BDD-AGGREGATOR-TEMPLATE.feature** - Redirect stub template
- **validate_bdd_suite.py** - Validation script

---

**Document Path**: `BDD/BDD_SPLITTING_RULES.md`
**Framework**: AI Dev Flow SDD
**Version**: 2.0 (Section-Based ONLY)
**Last Updated**: 2025-12-27
