---
title: "BDD MVP Validation Rules"
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

# =============================================================================
#  Document Role: This is a DERIVATIVE of BDD-MVP-TEMPLATE.feature
# - Authority: BDD-MVP-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from BDD_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to BDD-MVP-TEMPLATE.feature
# =============================================================================

> ** Document Role**: VALIDATION CHECKLIST for BDD documents (DERIVATIVE).
> - **Authority**: Validates compliance with `BDD-MVP-TEMPLATE.feature` (PRIMARY STANDARD)
> - **Purpose**: Post-creation quality gate checks
> - **Scope**: Use for quality gates before committing BDD changes
> - **Conflict Resolution**: If this conflicts with Template, update this document

# BDD Validation Rules Reference

## MVP Validation Profile (DEFAULT)

**MVP validation is the framework default.** Full validation is applied only when explicitly triggered or when using enterprise profile.

### MVP Detection

| Detection Method | Pattern | Result |
|------------------|---------|--------|
| Filename | `*-MVP-*.feature` | MVP profile |
| Frontmatter | `template_profile: mvp` | MVP profile |
| Default (no markers) | — | MVP profile |
| Frontmatter | `template_profile: full` or `enterprise` | Full profile |

### Validation Differences

| Check Category | MVP Profile | Full Profile |
|----------------|-------------|--------------|
| Gherkin syntax | Error | Error |
| Traceability tags (@brd, @prd, @ears) | Error | Error |
| Feature metadata | Error | Error |
| Scenario count limits | **Warning** | Error |
| ADR-Ready Score threshold | 70/100 | 90/100 |
| Background steps | **Skip** | Required |

### Usage

```bash
# MVP validation (default)
python3 ai_dev_flow/04_BDD/scripts/validate_bdd.py ai_dev_flow/04_BDD --profile mvp

# Full validation (explicit)
python3 ai_dev_flow/04_BDD/scripts/validate_bdd.py ai_dev_flow/04_BDD --profile full
```

### Cross-Linking Tags (AI-Friendly)

Use same-layer cross-links to document BDD relationships:
- `@depends: BDD-NN` — hard prerequisite BDD suite(s) that must be satisfied first.
- `@discoverability: BDD-NN (short rationale)` — related BDD suites with brief reasons to aid AI search and ranking.

Validation handling: Info-level (non-blocking). Reported for visibility only. Tags may be added to feature file headers or companion `BDD-NN_README.md` files.

---

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

**Version**: 1.1
**Date**: 2025-11-19T00:00:00
**Last Updated**: 2025-12-26T00:00:00
**Purpose**: Complete validation rules for BDD feature files
**Script**: `python 04_BDD/scripts/validate_bdd.py`
**Primary Template**: `BDD-MVP-TEMPLATE.feature`
**Framework**: AI Dev Flow SDD (100% compliant)
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

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

The BDD validation script ensures feature files meet quality standards for ADR progression and automated test execution.

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

### Reserved ID Exemption (BDD-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `BDD-00_*.md` or `BDD-00_*.feature`

**Document Types**:
- Index documents (`BDD-00_index.md`)
- Traceability matrix templates (`BDD-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `BDD-00_*` pattern.

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

### CHECK 3: ADR-Ready Score Validation  NEW

**Purpose**: Validate ADR-ready score format and threshold
**Type**: Error (blocking)

**Valid Examples**: `[PASS] 95% (Target: ≥90%)`

**Error Message**: `[FAIL] MISSING: ADR-Ready Score with [PASS] emoji and percentage`

### CHECK 4: Upstream Traceability Tags

**Purpose**: Verify complete tag chain per BDD-MVP-TEMPLATE.feature
**Type**: Error (blocking)

**Required Tags** (ALL MANDATORY):
```gherkin
@brd: BRD.NN.EE.SS    # REQUIRED - business requirements
@prd: PRD.NN.EE.SS    # REQUIRED - product requirements
@ears: EARS.NN.EE.SS  # REQUIRED - engineering requirements
```

**Format**: Extended format with requirement ID suffix (`:NN`) is REQUIRED.

### CHECK 4.1: Tag Placement Validation  NEW

**Purpose**: Verify tags are Gherkin-native, not in comments
**Type**: Error (blocking)

**Validation Rule**: Tags MUST appear as Gherkin-native tags on separate lines before `Feature:` keyword, NOT inside comment blocks.

**[FAIL] INVALID** (comment-based tags - frameworks cannot parse):
```gherkin
# @brd: BRD.01.01.01
# @prd: PRD.01.01.01
Feature: My Feature
```

**[PASS] VALID** (Gherkin-native tags):
```gherkin
@brd:BRD.01.01.01
@prd:PRD.01.01.01
@ears:EARS.01.24.01
Feature: My Feature
```

**Detection Pattern**:
```bash
# Detect comment-based tags (invalid)
grep -n "^#.*@brd:" docs/04_BDD/BDD-*/BDD-*.feature
grep -n "^#.*@prd:" docs/04_BDD/BDD-*/BDD-*.feature
grep -n "^#.*@ears:" docs/04_BDD/BDD-*/BDD-*.feature
```

**Error Message**: `[FAIL] INVALID: Tags found in comments. Move to Gherkin-native format before Feature: keyword`

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

### CHECK 8: Element ID Format Compliance  NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `BDD.NN.TT.SS:` | [PASS] Pass |
| Removed pattern | `TS-XXX` | [FAIL] Fail - use BDD.NN.14.SS |
| Removed pattern | `Scenario-XXX` | [FAIL] Fail - use BDD.NN.14.SS |
| Removed pattern | `STEP-XXX` | [FAIL] Fail - use BDD.NN.15.SS |

**Regex**: `^###?\s+BDD\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for BDD**:
| Element Type | Code | Example |
|--------------|------|---------|
| Test Scenario | 14 | BDD.02.14.01 |
| Step | 15 | BDD.02.15.01 |

**Fix**: Replace `Scenario: TS-01` with `Scenario: BDD.02.14.01`

**Reference**: BDD_CREATION_RULES.md Section 4.1, [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

### CHECK 9: Section-Based Structure Validation  UPDATED

**Purpose**: Validate section-based BDD structure compliance (MANDATORY format)
**Type**: Error (blocking)
**Scope**: ALL BDD .feature files (no backward compatibility with legacy formats)

#### 9.1 File Naming Pattern Validation

**Requirement**: ALL .feature files MUST match one of three valid section-based patterns

**Three Valid Patterns** (ONLY):

1. **Section-Only Format** (Primary)
   - Pattern: `^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$`
   - Example: `BDD-02.14_query_result_filtering.feature`
   - Use When: Standard section file (≤800 lines, ≤12 scenarios)

2. **Subsection Format** (When Section >800 Lines)
   - Pattern: `^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$`
   - Example: `BDD-02.24.01_quality_performance.feature`
   - Use When: Section requires splitting (each subsection ≤800 lines)

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
echo "$filename" | grep -qE "^BDD-[0-9]{2,}\.[0-9]+_[a-z0-9_]+\.feature$" && echo "[PASS] Section-only"

# Test subsection pattern
echo "$filename" | grep -qE "^BDD-[0-9]{2,}\.[0-9]+\.[0-9]{2}_[a-z0-9_]+\.feature$" && echo "[PASS] Subsection"

# Test aggregator pattern
echo "$filename" | grep -qE "^BDD-[0-9]{2,}\.[0-9]+\.00_[a-z0-9_]+\.feature$" && echo "[PASS] Aggregator"
```

**Error Messages**:
- `[FAIL] INVALID: File does not match any valid section-based pattern`
- `[FAIL] INVALID: Use BDD-NN.SS_{slug}.feature, BDD-NN.SS.mm_{slug}.feature, or BDD-NN.SS.00_{slug}.feature`

#### 9.2 Prohibited Pattern Detection

**Requirement**: Legacy formats MUST NOT be used (no backward compatibility)

**Prohibited Patterns** (ERROR on match):

1. **_partN Suffix** (Legacy splitting convention)
   - Pattern: `^BDD-\d{2,}_[a-z0-9_]+_part\d+\.feature$`
   - Example: `BDD-02_query_part1.feature` [FAIL]
   - Fix: Use subsection format `BDD-02.SS.01_query.feature`

2. **Single-File Format** (Legacy)
   - Pattern: `^BDD-\d{2,}_[a-z0-9_]+\.feature$` (without dot notation)
   - Example: `BDD-02_knowledge_engine.feature` [FAIL]
   - Fix: Use section format `BDD-02.SS_{slug}.feature`

3. **Directory-Based Structure** (Legacy)
   - Pattern: `BDD-NN_{slug}/features/` subdirectory
   - Example: `BDD-02_knowledge_engine/features/` [FAIL]
   - Fix: Move `.feature` files to the suite folder root: `docs/04_BDD/BDD-NN_{slug}/BDD-NN.SS_{slug}.feature`

**Validation Commands**:
```bash
# Detect _partN suffix (prohibited)
find docs/BDD -name "*.feature" | grep -E "BDD-[0-9]{2,}_.*_part[0-9]+" && echo "[FAIL] Prohibited _partN suffix found"

# Detect single-file format (prohibited)
find docs/BDD -name "*.feature" | grep -vE "\.[0-9]+" && echo "[FAIL] Prohibited single-file format found"

# Detect features/ subdirectory (prohibited)
find docs/BDD -type d -name "features" && echo "[FAIL] Prohibited features/ subdirectory found"
```

**Error Messages**:
- `[FAIL] PROHIBITED: _partN suffix detected. Use subsection format: BDD-NN.SS.01_{}, BDD-NN.SS.02_{}, etc.`
- `[FAIL] PROHIBITED: Single-file format detected. Use section-based format: BDD-NN.SS_{}.feature`
- `[FAIL] PROHIBITED: Legacy directory structure detected. Use nested suite folder with section-based files`
- `[FAIL] PROHIBITED: features/ subdirectory detected. Use nested suite folder; no features/ subfolder`

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
grep -q "^@redirect" BDD-02.12.00_query.feature || echo "[FAIL] Missing @redirect tag"

# Check for 0 scenarios
scenario_count=$(grep -c "^\s*Scenario" BDD-02.12.00_query.feature)
[ "$scenario_count" -eq 0 ] || echo "[FAIL] Aggregator contains $scenario_count scenarios (must be 0)"

# Check for subsection .00 pattern
echo "BDD-02.12.00_query.feature" | grep -qE "\.00_" && echo "[PASS] Valid aggregator pattern"
```

**Error Messages**:
- `[FAIL] ERROR: Aggregator file (.00) missing required @redirect tag`
- `[FAIL] ERROR: Aggregator file (.00) must have 0 scenarios (redirect stub only)`
- `[WARN]  WARNING: Aggregator missing subsection list in Feature description`

#### 9.4 File Size Limits

**Requirement**: Individual .feature files MUST stay under size limits

**Hard Limits**:
- **Maximum tokens per .feature file**: 20,000 tokens (warning: 15,000 tokens)
- **Maximum scenarios per Feature block**: 12 scenarios

**Rationale**: Keep files executable, maintainable, and within test framework limits

**Validation Commands**:
```bash
# Check token count using the validator script
python3 04_BDD/scripts/validate_bdd.py docs/04_BDD --profile mvp

# Check scenario count per Feature block
for f in docs/04_BDD/BDD-*/BDD-*.feature; do
  count=$(grep -c "^\s*Scenario" "$f")
  if [ $count -gt 12 ]; then
    echo "[FAIL] $f: $count scenarios (max 12)"
  fi
done
```

**Error Messages**:
- `[FAIL] ERROR: File exceeds 20,000 token limit (current: NNN tokens)`
- `[WARN]  WARNING: File exceeds soft limit of 15,000 tokens (current: NNN tokens)`
- `[FAIL] ERROR: Feature block contains NN scenarios (max 12 per block)`

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
grep -q "^@section:" BDD-02.14_query.feature || echo "[FAIL] Missing @section tag"

# Check for @parent_doc tag
grep -q "^@parent_doc:" BDD-02.14_query.feature || echo "[FAIL] Missing @parent_doc tag"

# Check for @index tag
grep -q "^@index:" BDD-02.14_query.feature || echo "[FAIL] Missing @index tag"

# For subsections, check @parent_section tag
filename="BDD-02.24.01_performance.feature"
if echo "$filename" | grep -qE "\.[0-9]{2}_"; then
  grep -q "^@parent_section:" "$filename" || echo "[FAIL] Missing @parent_section tag (required for subsections)"
fi
```

**Error Messages**:
- `[FAIL] ERROR: Missing required @section: N.S metadata tag`
- `[FAIL] ERROR: Missing required @parent_doc: BDD-NN metadata tag`
- `[FAIL] ERROR: Missing required @index: BDD-NN.0_index.md metadata tag`
- `[FAIL] ERROR: Missing required @parent_section: N.S tag (subsections only)`

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
  index_file="docs/04_BDD/BDD-${num}.0_index.md"
  [ -f "$index_file" ] || echo "[FAIL] Missing index file: BDD-${num}.0_index.md"
done
```

**Error Messages**:
- `[FAIL] ERROR: Missing required index file: BDD-NN.0_index.md`
- `[WARN]  WARNING: Index file exists but is empty`

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
grep -n "^|.*|.*|$" docs/04_BDD/BDD-*/BDD-*.feature && echo "[FAIL] Markdown table found in .feature file"

# Detect Markdown headers in .feature files (invalid - Gherkin uses ##)
grep -n "^# [^@]" docs/04_BDD/BDD-*/BDD-*.feature && echo "[FAIL] Non-Gherkin Markdown header found"
```

**Error Messages**:
- `[FAIL] INVALID: Markdown table found in .feature file (move to BDD-NN.0_index.md or BDD-NN_README.md)`
- `[FAIL] INVALID: Non-Gherkin Markdown content in .feature file`

#### 9.8 Quality Gate Pre-Commit Checklist

**File Naming** (ALL REQUIRED):
- [PASS] Matches one of 3 valid patterns (section-only, subsection, aggregator)
- [PASS] NO prohibited patterns (_partN, single-file, directory-based)
- [PASS] NO features/ subdirectory

**File Structure** (ALL REQUIRED):
- [PASS] ALL .feature files live inside suite folders: docs/04_BDD/BDD-NN_{slug}/
- [PASS] Index file exists for each suite: BDD-NN.0_index.md (inside the suite folder)
- [PASS] Optional companion docs live with the suite: BDD-NN_README.md, BDD-NN_TRACEABILITY.md

**Feature File Quality** (ALL REQUIRED):
- [PASS] No .feature exceeds 800 lines
- [PASS] No Feature block exceeds 12 scenarios
- [PASS] No non-Gherkin Markdown in .feature files
- [PASS] All quantitative values use `@threshold:` keys
- [PASS] Times have seconds; timezone is `America/New_York` or approved IANA zone

**Section Metadata** (ALL REQUIRED):
- [PASS] @section tag present (N.S or N.S.m format)
- [PASS] @parent_doc tag present (BDD-NN format)
- [PASS] @index tag present (BDD-NN.0_index.md format)
- [PASS] @parent_section tag present (subsections only)

**Aggregator Requirements** (IF APPLICABLE):
- [PASS] Has @redirect tag
- [PASS] Has 0 executable scenarios
- [PASS] Lists subsections in Feature description
- [PASS] Has .00 subsection number

#### 9.9 Validation Script Integration

**Command**:
```bash
# Validate section-based structure for all BDD files
python3 04_BDD/scripts/validate_bdd_suite.py --root BDD --prd-root PRD

# Validate specific suite
python3 04_BDD/scripts/validate_bdd_suite.py --root BDD --prd-root PRD | grep "BDD-02"
```

**Expected Output**:
```
 BDD validation passed (no violations)
```

**Error Output Example**:
```
ERROR: BDD-02_query.feature:1: Prohibited single-file format detected. Use section-based format: BDD-NN.SS_{}.feature
ERROR: BDD-02.14_query.feature:1: Missing required @section: N.S metadata tag
ERROR: docs/BDD:1: Missing required index file: BDD-02.0_index.md
ERROR: BDD-02.12.00_query.feature:15: Aggregator file (.00) must have 0 scenarios (redirect stub only)

[FAIL] Validation failed: 4 error(s), 0 warning(s)
```

**Exit Codes**:
- `0`: All validation checks passed
- `1`: Blocking errors found (must fix before commit)

**Reference**: `BDD_CREATION_RULES.md` Section 1.2, `validate_bdd_suite.py`

---

### CHECK 10: Section Numbering Sequence Validation  NEW

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
BDD-02.3_learning.feature  # [FAIL] Missing section 2
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
    echo "[WARN]  WARNING: Gap in section numbering between $prev and $num"
  fi
  prev=$num
done
```

**Error Messages**:
- `[WARN]  WARNING: Section numbering gap detected between N.S1 and N.S2`
- `[WARN]  WARNING: Duplicate section number N.S detected`
- `[WARN]  WARNING: Section numbers not sequential (found: 1, 3, 5)`

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
| **CHECK 9.4** | Split files exceeding 800 lines into smaller domain-focused files |
| **CHECK 9.5** | Add required sections to companion files |
| **CHECK 9.6** | Move Markdown tables/content from .feature to companion files |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single BDD feature file
python 04_BDD/scripts/validate_bdd.py docs/04_BDD/BDD-01_feature_scenarios/BDD-01.1_feature_scenarios.feature

# Validate all BDD files
find docs/BDD -name "BDD-*.feature" -exec python 04_BDD/scripts/validate_bdd.py {} \;
```

### ADR-Ready Scoring Criteria  NEW

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
[FAIL] @brd: BRD-01           (missing element ID suffix)
[PASS] @brd: BRD.01.01.30       (correct 4-segment element ID format)
[FAIL] Missing @brd tag        (ALL three tags are MANDATORY)
[PASS] @brd: BRD.01.01.30
   @prd: PRD.01.01.02
   @ears: EARS.01.24.03
```

### Mistake #2: Subjective Language
```
[FAIL] Given the system is running fast
[PASS] Given response time is under 500ms
```

### Mistake #3: ADR-Ready Score Format
```
[FAIL] ADR-Ready Score: 95%
[PASS] ADR-Ready Score: [PASS] 95% (Target: ≥90%)
```

### Mistake #4: Missing Scenario Types
```
[FAIL] Only success scenarios included
[PASS] Include @negative @edge_case @quality_attribute scenarios
```

### Mistake #5: Incorrect Split-File Structure
```
[PASS] .feature files at suite folder root (no features/ subdirectory)
docs/04_BDD/BDD-06_level0_system_agents/
 BDD-06.0_index.md
 BDD-06.1_health_monitor.feature     (CORRECT - at suite root)
 BDD-06.2_data_guardian.feature      (CORRECT - at suite root)
 BDD-06.3.00_integration.feature     (CORRECT - aggregator)
 BDD-06_README.md

[FAIL] features/ subdirectory present (legacy)
docs/04_BDD/BDD-06_level0_system_agents/
 README.md
 TRACEABILITY.md
 GLOSSARY.md
 features/
     BDD-06_health_monitor.feature  (WRONG - move to suite root)
     BDD-06_data_guardian.feature   (WRONG - move to suite root)
     BDD-06_integration.feature     (WRONG - move to suite root)

[FAIL] Missing aggregator stub when 5+ subsections
docs/04_BDD/BDD-06_level0_system_agents/BDD-06.3.00_integration.feature  (MISSING)

[PASS] Redirect/aggregator stub inside suite folder
docs/04_BDD/BDD-06_level0_system_agents/BDD-06.3.00_integration.feature  (redirect stub with 0 scenarios)

[FAIL] File exceeds 800 lines
BDD-06.1_health_monitor.feature: 625 lines (SPLIT NEEDED)

[PASS] Files within size limits
BDD-06_health_monitor.feature: 450 lines (GOOD)
```

---

**Maintained By**: QA Team, Engineering Team
**Review Frequency**: Updated with BDD template enhancements
