# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BDD-TEMPLATE.feature
# - Authority: BDD-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from BDD_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to BDD-TEMPLATE.feature
# =============================================================================
---
title: "BDD Validation Rules Reference"
tags:
  - validation-rules
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

> **📋 Document Role**: VALIDATION CHECKLIST for BDD documents (DERIVATIVE).
> - **Authority**: Validates compliance with `BDD-TEMPLATE.feature` (PRIMARY STANDARD)
> - **Purpose**: Post-creation quality gate checks
> - **Scope**: Use for quality gates before committing BDD changes
> - **Conflict Resolution**: If this conflicts with Template, update this document

# BDD Validation Rules Reference

**Version**: 1.1
**Date**: 2025-11-19
**Last Updated**: 2025-12-26
**Purpose**: Complete validation rules for BDD feature files
**Script**: `scripts/validate_bdd_template.sh`
**Primary Template**: `BDD-TEMPLATE.feature`
**Framework**: doc_flow SDD (100% compliant)
**Changes**: Added split-file structure validation (v1.1). Previous: ADR-ready scoring validation system (v1.0)

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
   2.1. [Split-File Structure Validation (CHECK 9)](#check-9-split-file-structure-validation)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The BDD validation script ensures feature files meet quality standards for ADR progression and automated test execution.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (BDD-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `BDD-000_*.md` or `BDD-000_*.feature`

**Document Types**:
- Index documents (`BDD-000_index.md`)
- Traceability matrix templates (`BDD-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `BDD-000_*` pattern.

---

## Validation Checks

### CHECK 1: Required Document Control Fields

**Type**: Error (blocking)

**Required Fields**:
- Project Name, Document Version, Date, Document Owner, Prepared By, Status, ADR-Ready Score

### CHECK 2: Gherkin Syntax Compliance

**Type**: Error (blocking)

**Requirements**:
- Feature declaration with As a/I want/So that
- Background keyword where applicable
- Valid Given/When/Then structure
- Proper tag format (@scenario_name)

### CHECK 3: ADR-Ready Score Validation ⭐ NEW

**Purpose**: Validate ADR-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: ADR-Ready Score with ✅ emoji and percentage`

### CHECK 4: Upstream Traceability Tags

**Purpose**: Verify complete tag chain per BDD-TEMPLATE.feature
**Type**: Error (blocking)

**Required Tags** (ALL MANDATORY):
```gherkin
@brd: BRD.NN.EE.SS    # REQUIRED - business requirements
@prd: PRD.NN.EE.SS    # REQUIRED - product requirements
@ears: EARS.NN.EE.SS  # REQUIRED - engineering requirements
```

**Format**: Extended format with requirement ID suffix (`:NN`) is REQUIRED.

### CHECK 4.1: Tag Placement Validation ⭐ NEW

**Purpose**: Verify tags are Gherkin-native, not in comments
**Type**: Error (blocking)

**Validation Rule**: Tags MUST appear as Gherkin-native tags on separate lines before `Feature:` keyword, NOT inside comment blocks.

**❌ INVALID** (comment-based tags - frameworks cannot parse):
```gherkin
# @brd: BRD.01.01.01
# @prd: PRD.01.01.01
Feature: My Feature
```

**✅ VALID** (Gherkin-native tags):
```gherkin
@brd:BRD.01.01.01
@prd:PRD.01.01.01
@ears:EARS.01.24.01
Feature: My Feature
```

**Detection Pattern**:
```bash
# Detect comment-based tags (invalid)
grep -n "^#.*@brd:" docs/BDD/*.feature
grep -n "^#.*@prd:" docs/BDD/*.feature
grep -n "^#.*@ears:" docs/BDD/*.feature
```

**Error Message**: `❌ INVALID: Tags found in comments. Move to Gherkin-native format before Feature: keyword`

### CHECK 5: Scenario Coverage Completeness

**Purpose**: Ensure comprehensive test coverage
**Type**: Warning

**Requirements**:
- Primary success scenarios present
- Error conditions covered
- Edge cases included
- Quality attribute scenarios specified

### CHECK 6: BDD Syntax Validation

**Purpose**: Verify Gherkin best practices
**Type**: Warning

**Requirements**:
- Active voice in step definitions
- Observable outcomes in Then steps
- No subjective language (fast, reliable, etc.)
- Data-driven Examples tables for parametric testing

### CHECK 7: ADR Readiness Assessment

**Purpose**: Verify architectural requirements clarity
**Type**: Warning

**Requirements**:
- Performance targets quantifiable
- security scenarios included
- Integration points specified
- Scalability requirements defined

---

### CHECK 8: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `BDD.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `TS-XXX` | ❌ Fail - use BDD.NN.14.SS |
| Removed pattern | `Scenario-XXX` | ❌ Fail - use BDD.NN.14.SS |
| Removed pattern | `STEP-XXX` | ❌ Fail - use BDD.NN.15.SS |

**Regex**: `^###?\s+BDD\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for BDD**:
| Element Type | Code | Example |
|--------------|------|---------|
| Test Scenario | 14 | BDD.02.14.01 |
| Step | 15 | BDD.02.15.01 |

**Fix**: Replace `Scenario: TS-01` with `Scenario: BDD.02.14.01`

**Reference**: BDD_CREATION_RULES.md Section 4.1, ID_NAMING_STANDARDS.md lines 783-793

---

### CHECK 9: Section-Based Structure Validation ⭐ UPDATED

**Purpose**: Validate section-based BDD structure compliance (MANDATORY format)
**Type**: Error (blocking)
**Scope**: ALL BDD .feature files (no backward compatibility with legacy formats)

#### 9.1 File Naming Pattern Validation

**Requirement**: ALL .feature files MUST match one of three valid section-based patterns

**Three Valid Patterns** (ONLY):

1. **Section-Only Format** (Primary)
   - Pattern: `^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$`
   - Example: `BDD-02.14_query_result_filtering.feature`
   - Use When: Standard section file (≤500 lines, ≤12 scenarios)

2. **Subsection Format** (When Section >500 Lines)
   - Pattern: `^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$`
   - Example: `BDD-02.24.01_quality_performance.feature`
   - Use When: Section requires splitting (each subsection ≤500 lines)

3. **Aggregator Format** (Optional Redirect Stub)
   - Pattern: `^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$`
   - Example: `BDD-02.12.00_query_graph_traversal.feature`
   - Use When: Organizing multiple subsections under one section
   - **Special Requirements**: MUST have `@redirect` tag, MUST have 0 scenarios

**Validation Commands**:
```bash
# Check if file matches any valid pattern
filename="BDD-02.14_query.feature"

# Test section-only pattern
echo "$filename" | grep -qE "^BDD-[0-9]{2,}\.[0-9]+_[a-z0-9_]+\.feature$" && echo "✅ Section-only"

# Test subsection pattern
echo "$filename" | grep -qE "^BDD-[0-9]{2,}\.[0-9]+\.[0-9]{2}_[a-z0-9_]+\.feature$" && echo "✅ Subsection"

# Test aggregator pattern
echo "$filename" | grep -qE "^BDD-[0-9]{2,}\.[0-9]+\.00_[a-z0-9_]+\.feature$" && echo "✅ Aggregator"
```

**Error Messages**:
- `❌ INVALID: File does not match any valid section-based pattern`
- `❌ INVALID: Use BDD-NN.SS_{slug}.feature, BDD-NN.SS.mm_{slug}.feature, or BDD-NN.SS.00_{slug}.feature`

#### 9.2 Prohibited Pattern Detection

**Requirement**: Legacy formats MUST NOT be used (no backward compatibility)

**Prohibited Patterns** (ERROR on match):

1. **_partN Suffix** (Legacy splitting convention)
   - Pattern: `^BDD-\d{2,}_[a-z0-9_]+_part\d+\.feature$`
   - Example: `BDD-02_query_part1.feature` ❌
   - Fix: Use subsection format `BDD-02.SS.01_query.feature`

2. **Single-File Format** (Legacy)
   - Pattern: `^BDD-\d{2,}_[a-z0-9_]+\.feature$` (without dot notation)
   - Example: `BDD-02_knowledge_engine.feature` ❌
   - Fix: Use section format `BDD-02.SS_{slug}.feature`

3. **Directory-Based Structure** (Legacy)
   - Pattern: `BDD-NN_{slug}/features/` subdirectory
   - Example: `BDD-02_knowledge_engine/features/` ❌
   - Fix: Flatten to BDD/ root level with section-based naming

**Validation Commands**:
```bash
# Detect _partN suffix (prohibited)
find docs/BDD -name "*.feature" | grep -E "BDD-[0-9]{2,}_.*_part[0-9]+" && echo "❌ Prohibited _partN suffix found"

# Detect single-file format (prohibited)
find docs/BDD -name "*.feature" | grep -vE "\.[0-9]+" && echo "❌ Prohibited single-file format found"

# Detect directory-based structure (prohibited)
find docs/BDD -type d -name "BDD-*" | grep -E "BDD-[0-9]{2,}_" && echo "❌ Prohibited directory structure found"

# Detect features/ subdirectory (prohibited)
find docs/BDD -type d -name "features" && echo "❌ Prohibited features/ subdirectory found"
```

**Error Messages**:
- `❌ PROHIBITED: _partN suffix detected. Use subsection format: BDD-NN.SS.01_{}, BDD-NN.SS.02_{}, etc.`
- `❌ PROHIBITED: Single-file format detected. Use section-based format: BDD-NN.SS_{}.feature`
- `❌ PROHIBITED: Directory-based structure detected. Migrate to section-based format at BDD/ root level`
- `❌ PROHIBITED: features/ subdirectory detected. All .feature files must be at BDD/ root level`

#### 9.3 Aggregator Validation

**Requirement**: Aggregator files (.00) MUST meet redirect stub requirements

**Aggregator Requirements** (ALL MANDATORY):
1. **Pattern**: `^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$`
2. **@redirect Tag**: MUST be present (Gherkin-native tag)
3. **0 Scenarios**: MUST NOT contain any `Scenario:` or `Scenario Outline:` entries
4. **Documentation**: SHOULD list all subsections in Feature description

**Valid Aggregator Example**:
```gherkin
# File: BDD-02.12.00_query_graph_traversal.feature
@redirect
@section: 2.12.00
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.12: Query Graph Traversal (Aggregator)

  This is a redirect stub. Test scenarios are in subsections:
  - BDD-02.12.01_depth_first.feature - Depth-first traversal tests
  - BDD-02.12.02_breadth_first.feature - Breadth-first traversal tests
  - BDD-02.12.03_bidirectional.feature - Bidirectional traversal tests

Background:
  Given the system timezone is "America/New_York"
  # No scenarios in aggregator - redirect only
```

**Validation Commands**:
```bash
# Check for @redirect tag
grep -q "^@redirect" BDD-02.12.00_query.feature || echo "❌ Missing @redirect tag"

# Check for 0 scenarios
scenario_count=$(grep -c "^\s*Scenario" BDD-02.12.00_query.feature)
[ "$scenario_count" -eq 0 ] || echo "❌ Aggregator contains $scenario_count scenarios (must be 0)"

# Check for subsection .00 pattern
echo "BDD-02.12.00_query.feature" | grep -qE "\.00_" && echo "✅ Valid aggregator pattern"
```

**Error Messages**:
- `❌ ERROR: Aggregator file (.00) missing required @redirect tag`
- `❌ ERROR: Aggregator file (.00) must have 0 scenarios (redirect stub only)`
- `⚠️  WARNING: Aggregator missing subsection list in Feature description`

#### 9.4 File Size Limits

**Requirement**: Individual .feature files MUST stay under size limits

**Hard Limits**:
- **Maximum lines per .feature file**: 500 lines (soft limit: 400 lines)
- **Maximum scenarios per Feature block**: 12 scenarios

**Rationale**: Keep files executable, maintainable, and within test framework limits

**Validation Commands**:
```bash
# Check line count for each .feature file at BDD/ root
find docs/BDD -maxdepth 1 -name "*.feature" -exec wc -l {} \; | awk '$1 > 500 {print "❌ " $2 ": " $1 " lines (max 500)"}'

# Check scenario count per Feature block
for f in docs/BDD/*.feature; do
  count=$(grep -c "^\s*Scenario" "$f")
  if [ $count -gt 12 ]; then
    echo "❌ $f: $count scenarios (max 12)"
  fi
done
```

**Error Messages**:
- `❌ ERROR: File exceeds 500 line limit (current: NNN lines)`
- `⚠️  WARNING: File exceeds soft limit of 400 lines (current: NNN lines)`
- `❌ ERROR: Feature block contains NN scenarios (max 12 per block)`

**Fix**: Split into subsections using `BDD-NN.SS.mm_{slug}.feature` format

#### 9.5 Section Metadata Tags Validation

**Requirement**: ALL .feature files MUST have section metadata tags

**Required Tags** (ALL MANDATORY):
1. `@section: N.S` or `@section: N.S.m` - Section/subsection number
2. `@parent_doc: BDD-NN` - Parent BDD suite
3. `@index: BDD-NN.0_index.md` - Index file reference

**For Subsections** (ADDITIONAL):
4. `@parent_section: N.S` - Parent section number

**Valid Tag Examples**:
```gherkin
# Section-only file (BDD-02.14_query.feature)
@section: 2.14
@parent_doc: BDD-02
@index: BDD-02.0_index.md
@brd:BRD.02.03.14
@prd:PRD.02.05.14
@ears:EARS.02.14.01

# Subsection file (BDD-02.24.01_performance.feature)
@section: 2.24.01
@parent_section: 2.24
@parent_doc: BDD-02
@index: BDD-02.0_index.md
@brd:BRD.02.03.24
@prd:PRD.02.05.24
@ears:EARS.02.24.01

# Aggregator file (BDD-02.12.00_query.feature)
@redirect
@section: 2.12.00
@parent_doc: BDD-02
@index: BDD-02.0_index.md
```

**Validation Commands**:
```bash
# Check for @section tag
grep -q "^@section:" BDD-02.14_query.feature || echo "❌ Missing @section tag"

# Check for @parent_doc tag
grep -q "^@parent_doc:" BDD-02.14_query.feature || echo "❌ Missing @parent_doc tag"

# Check for @index tag
grep -q "^@index:" BDD-02.14_query.feature || echo "❌ Missing @index tag"

# For subsections, check @parent_section tag
filename="BDD-02.24.01_performance.feature"
if echo "$filename" | grep -qE "\.[0-9]{2}_"; then
  grep -q "^@parent_section:" "$filename" || echo "❌ Missing @parent_section tag (required for subsections)"
fi
```

**Error Messages**:
- `❌ ERROR: Missing required @section: N.S metadata tag`
- `❌ ERROR: Missing required @parent_doc: BDD-NN metadata tag`
- `❌ ERROR: Missing required @index: BDD-NN.0_index.md metadata tag`
- `❌ ERROR: Missing required @parent_section: N.S tag (subsections only)`

#### 9.6 Index File Existence

**Requirement**: Each BDD suite MUST have an index file (BDD-NN.0_index.md)

**Index File Pattern**: `^BDD-\d{2,}\.0_index\.md$`

**Example**: `BDD-02.0_index.md`

**Index File Purpose**:
- Suite overview and testing scope
- File map table (section, file, scenarios, lines, status)
- Traceability matrix (upstream/downstream)
- Execution strategy and order
- Quality gates (pre/post execution)

**Validation Commands**:
```bash
# Extract unique suite numbers from .feature files
suite_nums=$(find docs/BDD -maxdepth 1 -name "BDD-*.*.*.feature" -o -name "BDD-*.*.feature" | \
  sed -E 's/.*BDD-([0-9]{2,})\..*/\1/' | sort -u)

# Check for index file for each suite
for num in $suite_nums; do
  index_file="docs/BDD/BDD-${num}.0_index.md"
  [ -f "$index_file" ] || echo "❌ Missing index file: BDD-${num}.0_index.md"
done
```

**Error Messages**:
- `❌ ERROR: Missing required index file: BDD-NN.0_index.md`
- `⚠️  WARNING: Index file exists but is empty`

#### 9.7 Non-Gherkin Content Validation

**Requirement**: .feature files MUST NOT contain non-Gherkin Markdown content

**Invalid Content Types**:
- Markdown tables in .feature files
- Prose paragraphs in .feature files
- Architectural diagrams in .feature files

**Valid Locations for Non-Gherkin Content**:
- BDD-NN.0_index.md (overview, file map, documentation)
- BDD-NN_README.md (optional companion doc)
- BDD-NN_TRACEABILITY.md (optional traceability matrix)
- BDD-NN_GLOSSARY.md (optional terminology)

**Validation Commands**:
```bash
# Detect Markdown tables in .feature files (invalid)
grep -n "^|.*|.*|$" docs/BDD/*.feature && echo "❌ Markdown table found in .feature file"

# Detect Markdown headers in .feature files (invalid - Gherkin uses ##)
grep -n "^# [^@]" docs/BDD/*.feature && echo "❌ Non-Gherkin Markdown header found"
```

**Error Messages**:
- `❌ INVALID: Markdown table found in .feature file (move to BDD-NN.0_index.md or BDD-NN_README.md)`
- `❌ INVALID: Non-Gherkin Markdown content in .feature file`

#### 9.8 Quality Gate Pre-Commit Checklist

**File Naming** (ALL REQUIRED):
- ✅ Matches one of 3 valid patterns (section-only, subsection, aggregator)
- ✅ NO prohibited patterns (_partN, single-file, directory-based)
- ✅ NO features/ subdirectory

**File Structure** (ALL REQUIRED):
- ✅ ALL .feature files at docs/BDD/ root level (flat structure)
- ✅ Index file exists for each suite: BDD-NN.0_index.md
- ✅ Optional companion docs at BDD/ root: BDD-NN_README.md, BDD-NN_TRACEABILITY.md

**Feature File Quality** (ALL REQUIRED):
- ✅ No .feature exceeds 500 lines
- ✅ No Feature block exceeds 12 scenarios
- ✅ No non-Gherkin Markdown in .feature files
- ✅ All quantitative values use `@threshold:` keys
- ✅ Times have seconds; timezone is `America/New_York` or approved IANA zone

**Section Metadata** (ALL REQUIRED):
- ✅ @section tag present (N.S or N.S.m format)
- ✅ @parent_doc tag present (BDD-NN format)
- ✅ @index tag present (BDD-NN.0_index.md format)
- ✅ @parent_section tag present (subsections only)

**Aggregator Requirements** (IF APPLICABLE):
- ✅ Has @redirect tag
- ✅ Has 0 executable scenarios
- ✅ Lists subsections in Feature description
- ✅ Has .00 subsection number

#### 9.9 Validation Script Integration

**Command**:
```bash
# Validate section-based structure for all BDD files
python ai_dev_flow/scripts/validate_bdd_suite.py --root docs/BDD --prd-root docs/PRD

# Validate specific suite
python ai_dev_flow/scripts/validate_bdd_suite.py --root docs/BDD --prd-root docs/PRD | grep "BDD-02"
```

**Expected Output**:
```
✓ BDD validation passed (no violations)
```

**Error Output Example**:
```
ERROR: BDD-02_query.feature:1: Prohibited single-file format detected. Use section-based format: BDD-NN.SS_{}.feature
ERROR: BDD-02.14_query.feature:1: Missing required @section: N.S metadata tag
ERROR: docs/BDD:1: Missing required index file: BDD-02.0_index.md
ERROR: BDD-02.12.00_query.feature:15: Aggregator file (.00) must have 0 scenarios (redirect stub only)

❌ Validation failed: 4 error(s), 0 warning(s)
```

**Exit Codes**:
- `0`: All validation checks passed
- `1`: Blocking errors found (must fix before commit)

**Reference**: `BDD_CREATION_RULES.md` Section 1.2, `validate_bdd_suite.py`

---

### CHECK 10: Section Numbering Sequence Validation ⭐ NEW

**Purpose**: Validate section numbering is sequential with no gaps
**Type**: Warning (recommended to fix)
**Scope**: ALL BDD suites

**Requirement**: Section numbers within a suite SHOULD be sequential without gaps

**Valid Sequence**:
```
BDD-02.0_index.md
BDD-02.1_ingest.feature
BDD-02.2_query.feature
BDD-02.3_learning.feature
```

**Invalid Sequence** (gap at section 2):
```
BDD-02.0_index.md
BDD-02.1_ingest.feature
BDD-02.3_learning.feature  # ❌ Missing section 2
BDD-02.4_processing.feature
```

**Validation Commands**:
```bash
# Extract section numbers for suite BDD-02
sections=$(find docs/BDD -name "BDD-02.*.feature" | sed -E 's/.*BDD-02\.([0-9]+).*/\1/' | sort -n)

# Check for gaps
prev=0
for num in $sections; do
  if [ $((num - prev)) -gt 1 ]; then
    echo "⚠️  WARNING: Gap in section numbering between $prev and $num"
  fi
  prev=$num
done
```

**Error Messages**:
- `⚠️  WARNING: Section numbering gap detected between N.S1 and N.S2`
- `⚠️  WARNING: Duplicate section number N.S detected`
- `⚠️  WARNING: Section numbers not sequential (found: 1, 3, 5)`

**Fix**: Renumber sections to be sequential (1, 2, 3, 4...) or document intentional gaps in index file

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing Document Control fields |
| **CHECK 2** | Fix Gherkin syntax (Given/When/Then structure) |
| **CHECK 3** | Add properly formatted ADR-Ready Score |
| **CHECK 4** | Complete traceability tag chain |
| **CHECK 8** | Replace legacy element IDs (TS-XXX, Scenario-XXX) with unified format `BDD.NN.TT.SS` |
| **CHECK 9.1** | Create missing companion files (README.md, TRACEABILITY.md, GLOSSARY.md) |
| **CHECK 9.2** | Move .feature files from suite root to features/ subdirectory |
| **CHECK 9.3** | Create redirect stub with @redirect/@meta tag and 0 scenarios |
| **CHECK 9.4** | Split files exceeding 500 lines into smaller domain-focused files |
| **CHECK 9.5** | Add required sections to companion files |
| **CHECK 9.6** | Move Markdown tables/content from .feature to companion files |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single BDD feature file
./scripts/validate_bdd_template.sh docs/BDD/BDD-01_feature_scenarios.feature

# Validate all BDD files
find docs/BDD -name "BDD-*.feature" -exec ./scripts/validate_bdd_template.sh {} \;
```

### ADR-Ready Scoring Criteria ⭐ NEW

**Scenario Completeness (35%)**:
- All EARS statements translated to BDD: 15%
- Comprehensive coverage (success/error/edge): 15%
- Observable verifications specified: 5%

**Testability (30%)**:
- Scenarios are automatable: 15%
- Data-driven Examples tables used: 10%
- Performance benchmarks quantifiable: 5%

**Architecture Requirements (25%)**:
- Performance/security/scalability quality attributes: 15%
- Integration points defined: 10%

**Business Validation (10%)**:
- Business acceptance criteria: 5%
- Measurable success outcomes: 5%

### Validation Tiers Summary

| Tier | Type | Checks | Action |
|------|------|--------|--------|
| **Tier 1** | Error | 1-4 | Must fix before commit |
| **Tier 2** | Warning | 5-7 | Recommended to fix |
| **Tier 3** | Info | - | No action required |

---

## Common Mistakes

### Mistake #1: Incomplete Traceability Tags (ALL THREE ARE REQUIRED)
```
❌ @brd: BRD-01           (missing element ID suffix)
✅ @brd: BRD.01.01.30       (correct 4-segment element ID format)
❌ Missing @brd tag        (ALL three tags are MANDATORY)
✅ @brd: BRD.01.01.30
   @prd: PRD.01.01.02
   @ears: EARS.01.24.03
```

### Mistake #2: Subjective Language
```
❌ Given the system is running fast
✅ Given response time is under 500ms
```

### Mistake #3: ADR-Ready Score Format
```
❌ ADR-Ready Score: 95%
✅ ADR-Ready Score: ✅ 95% (Target: ≥90%)
```

### Mistake #4: Missing Scenario Types
```
❌ Only success scenarios included
✅ Include @negative @edge_case @quality_attribute scenarios
```

### Mistake #5: Incorrect Split-File Structure
```
❌ .feature files at suite root level
docs/BDD/BDD-06_level0_system_agents/
├── BDD-06_health_monitor.feature     (WRONG - at suite root)
├── BDD-06_data_guardian.feature      (WRONG - at suite root)
└── features/                          (EMPTY)

✅ .feature files in features/ subdirectory
docs/BDD/BDD-06_level0_system_agents/
├── README.md
├── TRACEABILITY.md
├── GLOSSARY.md
└── features/
    ├── BDD-06_health_monitor.feature  (CORRECT - in features/)
    ├── BDD-06_data_guardian.feature   (CORRECT - in features/)
    └── BDD-06_integration.feature     (CORRECT - in features/)

❌ Missing redirect stub
docs/BDD/BDD-06_level0_system_agents.feature  (MISSING)

✅ Redirect stub at docs/BDD/ root level
docs/BDD/BDD-06_level0_system_agents.feature  (redirect stub with 0 scenarios)

❌ File exceeds 500 lines
BDD-06_health_monitor.feature: 625 lines (SPLIT NEEDED)

✅ Files within size limits
BDD-06_health_monitor.feature: 450 lines (GOOD)
```

---

**Maintained By**: QA Team, Engineering Team
**Review Frequency**: Updated with BDD template enhancements
