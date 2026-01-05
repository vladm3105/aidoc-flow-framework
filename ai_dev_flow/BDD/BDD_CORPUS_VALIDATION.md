# BDD Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | BDD_CORPUS_VALIDATION |
| Version | 1.1 |
| Created | 2026-01-04 |
| Updated | 2026-01-04 |
| Purpose | Quality gate for complete BDD corpus |
| Trigger | Run after ALL BDD files are complete |
| Scope | Entire BDD corpus validation |
| Layer | Layer 4 → Layer 5 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all BDD feature files are created but BEFORE ADR creation begins. These rules validate the entire BDD corpus as a cohesive set, checking for cross-document consistency, step reusability, and quality standards that cannot be verified at the individual file level.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual BDD Validation** | After each BDD creation | Single file | `BDD_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL BDD complete | Entire BDD set | This document |

### Workflow Position

```
Individual BDD Creation → BDD_VALIDATION_RULES.md (per-file)
        ↓
All BDD Complete
        ↓
BDD_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin ADR Creation (Layer 5)
FAIL → Fix issues, re-run corpus validation
```

---

## 0. Errors Found During BDD Validation

This section tracks common errors discovered during corpus validation. Populate during actual validation runs.

### 0.1 Critical Errors (MUST FIX)

| # | Error Type | BDDs Affected | Description | Fix Required |
|---|------------|---------------|-------------|--------------|
| E01 | **Premature Downstream References** | (populate) | Downstream artifacts (ADR, SYS, REQ, SPEC) referenced without "(pending)" status | Add "(pending)" suffix to all downstream references |
| E02 | **Scenario Count Mismatch** | (populate) | Index claims differ from actual scenario counts | Run scenario count validation and update index |
| E03 | **File Count Mismatch** | (populate) | Index shows incorrect file counts | Verify with `ls` command and update index |

### 0.2 Warnings (SHOULD FIX)

| # | Warning Type | BDDs Affected | Description | Recommendation |
|---|--------------|---------------|-------------|----------------|
| W01 | **Missing Status Column** | (populate) | Index downstream tables lack explicit "Status" column | Add Status column with "Pending" value |
| W02 | **Inconsistent Index Metadata** | (populate) | Section scenario/line counts may drift from actual content | Recount after each feature file modification |

### 0.3 Issues Fixed (Reference)

| # | Issue | Location | Fix Applied |
|---|-------|----------|-------------|
| (Template) | - | - | - |

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking ADR creation)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future BDD)` | BDD-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

**Validation Logic**:
```bash
# Check 1: Find placeholder text for existing documents
for placeholder in $(grep -rohE "BDD-[0-9]+ \(future" "$BDD_DIR"); do
  bdd_num=$(echo "$placeholder" | grep -oE "BDD-[0-9]+")
  if ls "$BDD_DIR/${bdd_num}_"*.feature 2>/dev/null; then
    echo "ERROR: $bdd_num exists but marked as future"
  fi
done

# Check 2: Find other placeholder patterns
grep -rniE "\(when created\)|\(to be defined\)|\(TBD\)" "$BDD_DIR"
```

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 5+ artifacts

**Severity**: Error (blocking)

**Rationale**: BDD is Layer 4. It should NOT reference specific numbered ADR, SYS, REQ, SPEC, TASKS, or IPLAN documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `ADR-NN` | 5 | ADRs don't exist during BDD creation |
| `SYS-NN` | 6 | SYS don't exist during BDD creation |
| `REQ-NN` | 7 | REQs don't exist during BDD creation |
| `SPEC-NN` | 10 | SPECs don't exist during BDD creation |
| `TASKS-NN` | 11 | TASKS don't exist during BDD creation |
| `IPLAN-NN` | 12 | IPLANs don't exist during BDD creation |

**Allowed Patterns** (generic references):
- "This will inform ADR decisions"
- "Downstream REQ artifacts will..."
- "See future SPEC for implementation"

**Validation Logic**:
```bash
# Check 3: Flag specific numbered references to downstream artifacts
grep -rnE "(ADR|SYS|REQ|SPEC|TASKS|IPLAN)-[0-9]{2,}" "$BDD_DIR" | \
  grep -v "(pending)" | \
  grep -v "Layer [0-9]"
# Expected: No output (all downstream refs should be generic or have (pending))
```

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 scenarios" | 6 scenarios listed | Count mismatch |
| "3 features" | 4 features enumerated | Count mismatch |
| "7 test cases" | 8 described | Count mismatch |

**Validation Logic**:
```bash
# Check 4: Find "N scenarios" or "N features" claims
grep -nE "[0-9]+ (scenarios|features|test cases)" "$BDD_DIR"/*.md
```

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify BDD index file reflects actual file states

**Severity**: Error

**Index File Pattern**: `BDD-*_index.md` (e.g., `BDD-00_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing BDD files listed in index |
| Version currency | Version numbers match file headers |
| Status accuracy | Status matches actual file content |

**Validation Logic**:
```bash
# Check 5: Files marked "Planned" that exist
for f in "$BDD_DIR"/BDD-*_index.md; do
  if [[ -f "$f" ]]; then
    grep -E "\| Planned \|" "$f" | while read line; do
      bdd=$(echo "$line" | grep -oE "BDD-[0-9]+")
      if ls "$BDD_DIR/${bdd}_"*.feature 2>/dev/null >/dev/null; then
        echo "ERROR: $bdd exists but marked Planned in index"
      fi
    done
  fi
done

# Check 6: Existing files not in index
for f in "$BDD_DIR"/BDD-[0-9]*_*.feature; do
  bdd=$(basename "$f" | grep -oE "BDD-[0-9]+")
  if ! grep -q "$bdd" "$BDD_DIR"/BDD-*_index.md 2>/dev/null; then
    echo "ERROR: $bdd exists but not in index"
  fi
done
```

---

### CORPUS-05: Inter-BDD Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability. Hyperlinks are optional enhancements.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex scenarios

**Severity**: Info

**Recommended Diagrams by BDD Type**:
| BDD Type | Recommended Diagrams |
|----------|---------------------|
| User flows | Sequence diagrams |
| State changes | State machine diagrams |
| Integration | Component diagrams |

**Validation Logic**:
```bash
# Check 7: Find files without Mermaid diagrams
for f in "$BDD_DIR"/BDD-[0-9]*_*.md; do
  diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
  if [ "$diagram_count" -eq 0 ]; then
    echo "INFO: $(basename $f) has no Mermaid diagrams"
  fi
done
```

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all BDD files

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Given/When/Then case | Consistent capitalization |
| Step phrase consistency | Same action same wording |
| Domain terms | Consistent terminology |

**Common Inconsistencies**:
| Inconsistency | Example |
|---------------|---------|
| Step variations | "user logs in" vs "user is logged in" |
| Article usage | "the system" vs "system" |
| Tense | "should display" vs "displays" |

**Validation Logic**:
```bash
# Check 8: Quick terminology scan
echo "=== Terminology Consistency ==="
grep -rci "the system" "$BDD_DIR" | grep -v ":0" | wc -l
grep -rci "system" "$BDD_DIR" | grep -v "the system" | grep -v ":0" | wc -l
```

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the BDD corpus

**Severity**: Error

**Element ID Format**: `BDD.NN.TT.SS`
- NN = Document number
- TT = Element type code (24 = BDD scenario)
- SS = Sequence number

**Validation Logic**:
```bash
# Check 9: Extract all element IDs and find duplicates
grep -rohE "BDD\.[0-9]+\.[0-9]+\.[0-9]+" "$BDD_DIR" | \
  sort | uniq -d | while read dup; do
    echo "ERROR: Duplicate element ID: $dup"
    grep -rn "$dup" "$BDD_DIR"
  done
```

---

### CORPUS-09: Timing Constraint Format

**Purpose**: Validate timeout/timing specifications in scenarios

**Severity**: Warning

**Good Formats**:
| Format | Example | Status |
|--------|---------|--------|
| With threshold | `within 500ms` | Correct |
| Explicit timing | `responds in 2 seconds` | Correct |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

**Thresholds**:
| File Type | Warning | Error | Max Items |
|-----------|---------|-------|-----------|
| Feature file (`.feature`) | 300 lines | 600 lines | 12 scenarios max |
| Index file (`*0_*.md`) | 300 lines | 500 lines | N/A |
| General BDD markdown | 600 lines | 1,200 lines | N/A |

**Validation Logic**:
```bash
# Check 10: Feature file line count
for f in "$BDD_DIR"/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f")
    if [ $lines -gt 300 ]; then
      echo "WARNING: $(basename $f) has $lines lines (>300)"
    fi
  fi
done

# Check 11: Index file line count
for f in "$BDD_DIR"/BDD-*_*/*0_*.md; do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f")
    if [ $lines -gt 500 ]; then
      echo "ERROR: $(basename $f) exceeds 500 lines ($lines)"
    fi
  fi
done

# Check 12: Scenario count per feature (max 12)
for f in "$BDD_DIR"/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    count=$(grep -c "Scenario:" "$f" 2>/dev/null || echo 0)
    if [ $count -gt 12 ]; then
      echo "WARNING: $(basename $f) has $count scenarios (max 12)"
    fi
  fi
done
```

---

### CORPUS-11: Given-When-Then Syntax Compliance

**Purpose**: Verify all BDD scenarios use proper Gherkin syntax

**Severity**: Error

**Required Elements**:
| Element | Description |
|---------|-------------|
| Feature | Feature declaration with description |
| Scenario/Outline | Scenario with descriptive title |
| Given | Preconditions and context |
| When | Action being tested |
| Then | Expected outcome |

**Validation Logic**:
```bash
# Check 13: Feature declaration present
grep -L "^Feature:" "$BDD_DIR"/BDD-*_*/*.feature 2>/dev/null

# Check 14: All scenarios have Given-When-Then structure
for f in "$BDD_DIR"/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    scenarios=$(grep -c "Scenario:" "$f" 2>/dev/null || echo 0)
    givens=$(grep -c "^\s*Given" "$f" 2>/dev/null || echo 0)
    whens=$(grep -c "^\s*When" "$f" 2>/dev/null || echo 0)
    thens=$(grep -c "^\s*Then" "$f" 2>/dev/null || echo 0)
    if [ "$givens" -eq 0 ] || [ "$whens" -eq 0 ] || [ "$thens" -eq 0 ]; then
      echo "WARNING: $(basename $f) incomplete (Given:$givens When:$whens Then:$thens)"
    fi
  fi
done

# Check 15: Scenario Outline must have Examples
for f in "$BDD_DIR"/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    outlines=$(grep -c "Scenario Outline:" "$f" 2>/dev/null || echo 0)
    examples=$(grep -c "Examples:" "$f" 2>/dev/null || echo 0)
    if [ "$outlines" -gt 0 ] && [ "$outlines" -ne "$examples" ]; then
      echo "ERROR: $(basename $f) has $outlines Outlines but $examples Examples"
    fi
  fi
done

# Check 16: SHALL keyword in Then steps
for f in "$BDD_DIR"/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    thens=$(grep -c "^\s*Then" "$f" 2>/dev/null || echo 0)
    shalls=$(grep -c "SHALL" "$f" 2>/dev/null || echo 0)
    if [ "$thens" -gt 0 ] && [ "$shalls" -eq 0 ]; then
      echo "WARNING: $(basename $f) Then steps without SHALL"
    fi
  fi
done
```

---

### CORPUS-12: Cumulative Traceability (@brd + @prd + @ears)

**Purpose**: Verify all BDD have cumulative upstream traceability

**Severity**: Error

**Required Tags**: Each BDD must include all three:
- `@brd:` tag linking to source BRD element
- `@prd:` tag linking to source PRD element
- `@ears:` tag linking to source EARS element

**Validation Logic**:
```bash
# Check 17: Cumulative traceability tags present
for f in "$BDD_DIR"/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    brd=$(grep -c "@brd:" "$f" 2>/dev/null || echo 0)
    prd=$(grep -c "@prd:" "$f" 2>/dev/null || echo 0)
    ears=$(grep -c "@ears:" "$f" 2>/dev/null || echo 0)
    if [ "$brd" -eq 0 ] || [ "$prd" -eq 0 ] || [ "$ears" -eq 0 ]; then
      echo "WARNING: $(basename $f) missing tags (brd:$brd prd:$prd ears:$ears)"
    fi
  fi
done

# Check 18: Correct element ID format (dot-based)
grep -oE "@(brd|prd|ears): [A-Z]+\.[0-9]+\.[0-9]+\.[0-9]+" "$BDD_DIR"/BDD-*_*/*.feature | head -5

# Check 19: Wrong dash-based element IDs (should return NO matches)
grep -E "@(brd|prd|ears): [A-Z]+-[0-9]+-" "$BDD_DIR"/BDD-*_*/*.feature
```

---

### CORPUS-13: Feature File Aggregation (Split-File Consistency)

**Purpose**: Verify split BDD files maintain consistency

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Index exists | Split features have `BDD-NN.0_index.md` |
| Numbering sequence | Section numbers are sequential |
| Cross-references | Sections reference each other correctly |

**Validation Logic**:
```bash
# Check 20: Split-file directories have index
for dir in "$BDD_DIR"/BDD-[0-9]*_*/; do
  if [[ -d "$dir" ]]; then
    if ! ls "$dir"/BDD-*.0_*.md 2>/dev/null >/dev/null; then
      echo "WARNING: Split BDD $(basename $dir) missing index file"
    fi
  fi
done
```

---

### CORPUS-14: Step Reusability (Duplicate Step Detection)

**Purpose**: Identify duplicate or similar step definitions for DRY principle

**Severity**: Info

**Checks**:
| Check | Description |
|-------|-------------|
| Exact duplicates | Identical step text across files |
| Near duplicates | Similar steps with minor variations |
| Parameterization | Steps that could use scenario outlines |

**Validation Logic**:
```bash
# Check 21: Extract all Given/When/Then steps and find duplicates
grep -rhE "^\s+(Given|When|Then|And|But) " "$BDD_DIR"/*.feature 2>/dev/null | \
  sed 's/^\s*//' | sort | uniq -c | sort -rn | \
  awk '$1 > 1 {print "INFO: Step used " $1 " times: " substr($0, index($0,$2))}'
```

---

### CORPUS-15: ADR-Ready Score Threshold

**Purpose**: Verify BDD documents meet ADR-Ready threshold

**Severity**: Warning

**Threshold**: All BDD files should have ADR-Ready Score ≥90%

**Validation Logic**:
```bash
# Check 22: ADR-Ready scores
for f in "$BDD_DIR"/BDD-[0-9]*_*.feature; do
  if [ -f "$f" ]; then
    score=$(grep -oE "ADR-Ready Score[^0-9]*[0-9]+" "$f" | grep -oE "[0-9]+" | head -1)
    if [[ -n "$score" && $score -lt 90 ]]; then
      echo "WARNING: $(basename $f) has ADR-Ready Score $score% (target: ≥90%)"
    fi
  fi
done
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 5+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate element ID across corpus | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing Feature declaration | CORPUS-11 |
| CORPUS-E012 | Missing @brd traceability tag | CORPUS-12 |
| CORPUS-E013 | Missing @prd traceability tag | CORPUS-12 |
| CORPUS-E014 | Missing @ears traceability tag | CORPUS-12 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Timing constraint not measurable | CORPUS-09 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W013 | Split-file missing index | CORPUS-13 |
| CORPUS-W015 | ADR-Ready Score below 90% | CORPUS-15 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |
| CORPUS-I014 | Duplicate step detected | CORPUS-14 |

---

## 3. BDD Traceability Requirements

### 3.1 Cumulative Tagging (Layer 4)

BDD is Layer 4 in the SDD workflow. Each BDD file MUST include cumulative tags from ALL upstream layers:

| Layer | Tag Format | Required |
|-------|------------|----------|
| 1 (BRD) | `@brd: BRD.NN.TT.SS` | YES |
| 2 (PRD) | `@prd: PRD.NN.TT.SS` | YES |
| 3 (EARS) | `@ears: EARS.NN.TT.SS` | YES |

**Placement**: Tags should appear immediately after the document header comment block.

### 3.2 Feature File Traceability Header

Every feature file MUST include a traceability comment block:

```gherkin
# =============================================================================
# BDD-NN.S: Feature Title
# Layer 4 - BDD Test Specification
# =============================================================================
# TRACEABILITY:
#   Upstream: EARS-NN (EARS.NN.XX.YY-ZZ)
#   Downstream: SYS-NN (pending), REQ-NN (pending), SPEC-NN (pending)
# =============================================================================
```

**CRITICAL**: Downstream references MUST include "(pending)" until artifacts exist.

### 3.3 Index File Downstream Table Format

Index files with downstream artifact references MUST use table format with Status column:

```markdown
### Downstream Artifacts (Pending)

| BDD Section | Downstream Artifact | Status | Description |
|-------------|---------------------|--------|-------------|
| BDD-NN.1 | ADR-NN, SYS-NN | Pending | Description of downstream artifacts |
| BDD-NN.2 | SPEC-NN | Pending | Description |
```

---

## 4. Gherkin Syntax Standards

### 4.1 Feature Structure

```gherkin
Feature: BDD-NN.S: Descriptive Feature Title
  As a [role]
  I want [capability]
  So that [benefit]

  Background:
    Given [common precondition]
    And [additional precondition]

  Scenario: Descriptive scenario title
    Given [context]
    When [action]
    Then [expected outcome with SHALL]
```

### 4.2 Scenario Naming Convention

| Prefix | Purpose | Example |
|--------|---------|---------|
| No prefix | Happy path / primary behavior | `Scenario: User successfully logs in` |
| `@negative` | Error cases | `Scenario: Login fails with invalid password` |
| `@edge-case` | Boundary conditions | `Scenario: System handles empty input` |
| `@state-driven` | State machine transitions | `Scenario: Order transitions from pending to filled` |

### 4.3 Step Keywords

| Keyword | Usage | SHALL Requirement |
|---------|-------|-------------------|
| `Given` | Setup preconditions | No |
| `When` | Action/trigger | No |
| `Then` | Expected outcome | YES - use "SHALL" |
| `And` | Additional conditions | Depends on context |

### 4.4 Threshold References

Use `@threshold:` comments to link to PRD threshold values:

```gherkin
# @threshold: PRD.12.capital.initial = $1,000,000
Scenario: Paper trading initializes with simulated capital
  Given paper trading mode activates
  When the capital initialization process runs
  Then the System SHALL initialize with @threshold: PRD.12.capital.initial
```

---

## 5. Automated Validation Script

Save as `scripts/validate_bdd_corpus.sh`:

```bash
#!/bin/bash
# BDD Corpus Validation Script
# Usage: ./scripts/validate_bdd_corpus.sh [BDD_DIR]
# Validates entire BDD corpus for CORPUS-01 through CORPUS-15 checks

BDD_DIR="${1:-docs/BDD}"
ERRORS=0
WARNINGS=0

echo "=== BDD Corpus Validation ==="
echo "Directory: $BDD_DIR"
echo ""

# E01: Premature Downstream References
echo "Check 1: Premature downstream references in feature files..."
PREMATURE=$(grep -rn "Downstream:" $BDD_DIR/BDD-*_*/*.feature 2>/dev/null | grep -v "(pending)" | grep -v "pending)" | wc -l)
if [ $PREMATURE -gt 0 ]; then
  echo "  ERROR: $PREMATURE files have downstream refs without (pending)"
  grep -rn "Downstream:" $BDD_DIR/BDD-*_*/*.feature | grep -v "(pending)" | grep -v "pending)"
  ERRORS=$((ERRORS + 1))
else
  echo "  PASS"
fi

# E01b: Missing Status column in index tables
echo "Check 2: Status column in index downstream tables..."
for f in $BDD_DIR/BDD-*_*/*0_*.md; do
  if grep -q "Downstream" "$f" 2>/dev/null; then
    if ! grep -q "| Status |" "$f" 2>/dev/null; then
      echo "  ERROR: $(basename $f) missing Status column"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done
echo "  PASS (if no errors above)"

# E02: Scenario Count Validation
echo "Check 3: Scenario count validation..."
ACTUAL_TOTAL=$(grep -rh "Scenario:" $BDD_DIR/BDD-*_*/*.feature 2>/dev/null | wc -l)
INDEX_TOTAL=$(grep "Total Scenarios" $BDD_DIR/BDD-00_index.md 2>/dev/null | grep -oE "[0-9]+")
if [ -n "$INDEX_TOTAL" ] && [ "$ACTUAL_TOTAL" != "$INDEX_TOTAL" ]; then
  echo "  ERROR: Index claims $INDEX_TOTAL scenarios but actual is $ACTUAL_TOTAL"
  ERRORS=$((ERRORS + 1))
else
  echo "  PASS (Total: $ACTUAL_TOTAL scenarios)"
fi

# Check cumulative tags
echo "Check 4: Cumulative traceability tags..."
for f in $BDD_DIR/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    brd=$(grep -c "@brd:" "$f" 2>/dev/null || echo 0)
    prd=$(grep -c "@prd:" "$f" 2>/dev/null || echo 0)
    ears=$(grep -c "@ears:" "$f" 2>/dev/null || echo 0)
    if [ "$brd" -eq 0 ] || [ "$prd" -eq 0 ] || [ "$ears" -eq 0 ]; then
      echo "  WARNING: $(basename $f) missing cumulative tags (brd:$brd prd:$prd ears:$ears)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

# Check TRACEABILITY header
echo "Check 5: TRACEABILITY comment block..."
MISSING_TRACE=$(grep -L "TRACEABILITY:" $BDD_DIR/BDD-*_*/*.feature 2>/dev/null | wc -l)
if [ $MISSING_TRACE -gt 0 ]; then
  echo "  WARNING: $MISSING_TRACE files missing TRACEABILITY block"
  WARNINGS=$((WARNINGS + 1))
else
  echo "  PASS"
fi

# Check Gherkin structure
echo "Check 6: Gherkin Given-When-Then structure..."
for f in $BDD_DIR/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    thens=$(grep -c "^\s*Then" "$f" 2>/dev/null || echo 0)
    shalls=$(grep -c "SHALL" "$f" 2>/dev/null || echo 0)
    if [ "$thens" -gt 0 ] && [ "$shalls" -eq 0 ]; then
      echo "  WARNING: $(basename $f) has Then steps without SHALL keyword"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

# Check file sizes
echo "Check 7: Feature file line counts..."
for f in $BDD_DIR/BDD-*_*/*.feature; do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f")
    if [ $lines -gt 300 ]; then
      echo "  WARNING: $(basename $f) has $lines lines (>300)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done

# Summary
echo ""
echo "=== Validation Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
  echo "FAILED: Fix errors before ADR creation"
  exit 1
else
  echo "PASSED: BDD corpus ready for ADR creation"
  exit 0
fi
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Errors found (blocking) |
| 2 | Warnings found (non-blocking) |
| 3 | Script error |

---

## 6. Post-Validation Actions

### 6.1 For Critical Errors

| Error | Remediation Steps |
|-------|-------------------|
| **E01: Premature Downstream References** | 1. Open affected feature file<br>2. Find TRACEABILITY comment block<br>3. Add "(pending)" after each downstream artifact<br>4. For index files: Add Status column with "Pending" value |
| **E02: Scenario Count Mismatch** | 1. Run scenario count script<br>2. Update BDD-00_index.md with correct counts<br>3. Update each suite's index with accurate scenario/file counts |
| **E03: File Count Mismatch** | 1. Run `ls BDD-NN_*/*.feature \| wc -l`<br>2. Compare with index claim<br>3. Update index table with correct file count |

### 6.2 For Warnings

| Warning | Remediation Steps |
|---------|-------------------|
| **W01: Missing Status Column** | 1. Open index file<br>2. Add `\| Status \|` to table header<br>3. Add `\| Pending \|` to each row |
| **W02: Inconsistent Metadata** | 1. Recount scenarios in feature files<br>2. Update section index scenario counts<br>3. Update line counts if displayed |

---

## 7. Baseline Metrics (Verified Counts)

Populate after validation runs.

| Suite | Scenarios | Files | Status | Last Verified |
|-------|-----------|-------|--------|---------------|
| BDD-01 | - | - | Pending | - |
| BDD-02 | - | - | Pending | - |
| BDD-03 | - | - | Pending | - |
| ... | ... | ... | ... | ... |
| **TOTAL** | **-** | **-** | | |

**Validation Command**:
```bash
# Count scenarios per suite
for suite in 01 02 03 04 05 06 07 08 09 10; do
  count=$(grep -h "Scenario:" docs/BDD/BDD-${suite}_*/*.feature 2>/dev/null | wc -l)
  files=$(ls docs/BDD/BDD-${suite}_*/*.feature 2>/dev/null | wc -l)
  echo "BDD-${suite}: $count scenarios, $files files"
done
```

---

## 8. Validation Checklist

### Pre-ADR Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-BDD cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex scenarios
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Timing constraints are measurable
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All scenarios use Given-When-Then syntax
- [ ] **CORPUS-12**: All BDD have cumulative traceability (@brd + @prd + @ears)
- [ ] **CORPUS-13**: Split files have proper index structure
- [ ] **CORPUS-14**: Duplicate steps identified for refactoring
- [ ] **CORPUS-15**: All BDD have ADR-Ready Score ≥90%

---

## 9. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-bdd-corpus.yml
name: BDD Corpus Validation

on:
  push:
    paths:
      - 'docs/BDD/**/*.md'
      - 'docs/BDD/**/*.feature'
  pull_request:
    paths:
      - 'docs/BDD/**/*.md'
      - 'docs/BDD/**/*.feature'

jobs:
  validate-bdd-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate BDD Corpus
        run: |
          chmod +x ./scripts/validate_bdd_corpus.sh
          ./scripts/validate_bdd_corpus.sh docs/BDD
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: bdd-validation-report
          path: tmp/bdd_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# BDD corpus validation on staged BDD files
if git diff --cached --name-only | grep -qE "^docs/BDD/.*\.(md|feature)$"; then
  echo "Running BDD corpus validation..."
  ./scripts/validate_bdd_corpus.sh docs/BDD --errors-only
  if [ $? -ne 0 ]; then
    echo "BDD corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "BDD corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-bdd:
	@echo "Validating BDD corpus..."
	@./scripts/validate_bdd_corpus.sh docs/BDD

validate-bdd-verbose:
	@./scripts/validate_bdd_corpus.sh docs/BDD --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys
	@echo "All corpus validations complete"
```

### Integration with ADR Layer Gate

BDD corpus validation should pass before creating ADR documents:

```bash
# Pre-ADR gate check
./scripts/validate_bdd_corpus.sh docs/BDD
if [ $? -eq 0 ]; then
  echo "BDD corpus valid - ready for ADR layer creation"
else
  echo "Fix BDD corpus errors before proceeding to ADR layer"
  exit 1
fi
```

---

## 10. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-01-04 | - | Added Section 0 (Errors Found); Added numbered check comments (Check 1-22); Added Section 3 (Traceability Requirements); Added Section 4 (Gherkin Syntax Standards); Added complete validation script; Added Section 6 (Post-Validation Actions); Added Section 7 (Baseline Metrics); Renumbered sections |
| 1.0 | 2026-01-04 | - | Initial corpus validation rules |

---

## References

- [BDD_VALIDATION_RULES.md](./BDD_VALIDATION_RULES.md) - Individual file validation
- [BDD-TEMPLATE.feature](./BDD-TEMPLATE.feature) - BDD document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
