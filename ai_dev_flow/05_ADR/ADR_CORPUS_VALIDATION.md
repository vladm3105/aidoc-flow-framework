---
title: "ADR Corpus Validation"
tags:
  - corpus-validation
  - layer-5-artifact
  - shared-architecture
custom_fields:
  document_type: corpus-validation
  artifact_type: ADR
  layer: 5
  priority: shared
  development_status: active
---

# ADR Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | ADR_CORPUS_VALIDATION |
| Version | 1.1 |
| Created | 2026-01-04 |
| Updated | 2026-01-04 |
| Purpose | Quality gate for complete ADR corpus |
| Trigger | Run after ALL ADRs are complete |
| Scope | Entire ADR corpus validation |
| Layer | Layer 5 → Layer 6 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all ADR files are created but BEFORE SYS creation begins. These rules validate the entire ADR corpus as a cohesive set, checking for cross-document consistency, decision conflicts, and quality standards that cannot be verified at the individual file level.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual ADR Validation** | After each ADR creation | Single file | `ADR_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL ADR complete | Entire ADR set | This document |

### Workflow Position

```
Individual ADR Creation → ADR_VALIDATION_RULES.md (per-file)
        ↓
All ADRs Complete
        ↓
ADR_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin SYS Creation (Layer 6)
FAIL → Fix issues, re-run corpus validation
```

### ADR Document Categories

| Category | Pattern | Corpus Validation |
|----------|---------|-------------------|
| Standard ADR | `ADR-NN_{topic}.md` | Full validation |
| ADR-REF | `ADR-REF-NN_{slug}.md` | Reduced (no traceability) |

---

## 0. Errors Found During Validation (Template)

This section documents errors discovered during corpus validation. Copy and populate for each project.

### 0.1 Critical Errors (MUST FIX)

| # | Error Type | ADRs Affected | Description | Fix Required |
|---|------------|---------------|-------------|--------------|
| E01 | **Title Numbering Format** | - | YAML title uses 3-digit format (`ADR-001`) | Change to 2-digit format (`ADR-01`) |
| E02 | **Header Level Inconsistency** | - | Major sections use H3 (`###`) instead of H2 (`##`) | Use H2 for all major sections per template |
| E03 | **Missing Document Control** | - | No Document Control table with required metadata | Add Document Control section at top of document |
| E04 | **Missing Traceability Section** | - | No Section 16 Traceability with cumulative @tags | Add Traceability section with @brd, @prd, @ears, @bdd tags |
| E05 | **Missing SYS-Ready Score** | - | No SYS-Ready Score in Document Control | Add score in format: `SYS-Ready NN% (Target: ≥90%)` |
| E06 | **H1 Title vs H2** | - | Main title uses H2 (`## ADR-NN:`) instead of H1 | Use H1 format: `# ADR-NN: Title` |

### 0.2 Warnings (SHOULD FIX)

| # | Warning Type | ADRs Affected | Description | Recommendation |
|---|--------------|---------------|-------------|----------------|
| W01 | **ASCII Diagrams** | - | Text-based diagrams instead of Mermaid | Convert all ASCII diagrams to Mermaid per DIAGRAM_STANDARDS.md |
| W02 | **Custom Fields Inconsistency** | - | YAML custom_fields differ from template | Standardize YAML frontmatter per ADR-MVP-TEMPLATE.md (full template archived) |
| W03 | **Index Title Format** | - | Title uses `ADR-000` instead of `ADR-00` | Change to 2-digit format for consistency |

### 0.3 Issues Fixed (Reference)

| # | Issue | Location | Fix Applied |
|---|-------|----------|-------------|
| F01 | - | - | - |

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking SYS creation)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future ADR)` | ADR-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

**Validation Logic**:
```bash
# Check 1: Placeholder patterns
grep -rn "(future ADR)\|(when created)\|(to be defined)\|(pending)\|(TBD)" "$ADR_DIR"/ADR-*.md
# Expected: No output or only in legitimately incomplete documents
```

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 6+ artifacts

**Severity**: Error (blocking)

**Rationale**: ADR is Layer 5. It should NOT reference specific numbered SYS, REQ, SPEC, or TASKS documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `SYS-NN` | 6 | SYS don't exist during ADR creation |
| `REQ-NN` | 7 | REQs don't exist during ADR creation |
| `SPEC-NN` | 10 | SPECs don't exist during ADR creation |
| `TASKS-NN` | 11 | TASKS don't exist during ADR creation |

**Allowed Patterns** (generic references):
- "This will inform SYS development"
- "Downstream REQ artifacts will..."
- "See future SPEC for implementation"

**Validation Logic**:
```bash
# Check 2: Premature downstream references (Layer 6+)
grep -rn "SYS-[0-9]\|REQ-[0-9]\|SPEC-[0-9]\|TASKS-[0-9]" "$ADR_DIR"/ADR-*.md
# Expected: No output (ADR should not reference future layer documents)
```

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 alternatives" | 6 alternatives listed | Count mismatch |
| "3 consequences" | 4 enumerated | Count mismatch |
| "7 architecture decisions" | 8 described | Count mismatch |

**Validation Logic**:
```bash
# Check 3: Internal count consistency (manual review needed)
# Look for numeric claims followed by enumerated lists
grep -n "[0-9]\+ alternative\|[0-9]\+ consequence" "$ADR_DIR"/ADR-*.md
```

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify ADR index file reflects actual file states

**Severity**: Error

**Index File Pattern**: `ADR-*_index.md` (e.g., `ADR-00_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing ADR files listed in index |
| Version currency | Version numbers match file headers |
| Status accuracy | Status matches actual file content |

**Validation Logic**:
```bash
# Check 4: Index synchronization
# Count actual ADR files vs index entries
ls "$ADR_DIR"/ADR-[0-9]*_*.md 2>/dev/null | wc -l
grep -c "| ADR-[0-9]" "$ADR_DIR"/ADR-*_index.md
```

---

### CORPUS-05: Inter-ADR Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability. Hyperlinks are optional enhancements.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex architecture decisions

**Severity**: Info

**Recommended Diagrams by ADR Type**:
| ADR Type | Recommended Diagrams |
|----------|---------------------|
| Technology selection | Comparison matrix diagram |
| Architecture pattern | Component diagram |
| Integration decision | Sequence diagram |
| Data model decision | ERD or data flow |

**Validation Logic**:
```bash
# Check 5: Mermaid diagram presence
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  diagram_count=$(grep -c "^```mermaid" "$f" 2>/dev/null || true)
  if [ "$diagram_count" -eq 0 ]; then
    echo "INFO: $(basename $f) has no Mermaid diagrams"
  fi
done
```

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all ADRs

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Term consistency | Same term used same way across docs |
| Acronym expansion | Acronyms expanded on first use per doc |
| No conflicting definitions | Same concept not defined differently |

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate ADR references across the corpus

**Severity**: Error

**ADR uses document-level references**: `ADR-NN` (not dot notation)

**Validation Logic**:
```bash
# Check 6: Duplicate ADR filenames
ls "$ADR_DIR"/ADR-[0-9]*_*.md | \
  grep -oE "ADR-[0-9]+" | sort | uniq -d
# Expected: No output (no duplicate numbers)
```

---

### CORPUS-09: Decision Status Tracking

**Purpose**: Validate decision status consistency

**Severity**: Warning

**Valid Statuses**:
| Status | Description |
|--------|-------------|
| Proposed | Under consideration |
| Accepted | Approved and active |
| Deprecated | Replaced by newer decision |
| Superseded | Replaced with specific ADR reference |

**Validation Logic**:
```bash
# Check 7: Valid decision statuses
grep -rn "Status.*:\s*\(Proposed\|Accepted\|Deprecated\|Superseded\)" "$ADR_DIR"/ADR-*.md
```

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 600 | 1,200 |
| Tokens | 50,000 | 100,000 |

**Validation Logic**:
```bash
# Check 8: File size compliance
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 1200 ]; then
    echo "ERROR: $(basename $f) exceeds 1200 lines ($lines)"
  elif [ "$lines" -gt 600 ]; then
    echo "WARNING: $(basename $f) exceeds 600 lines ($lines)"
  fi
done
```

---

### CORPUS-11: Context-Decision-Consequences Structure

**Purpose**: Verify all ADRs follow ADR structure pattern

**Severity**: Error

**Required Sections**:
| Section | Description |
|---------|-------------|
| Context | Problem statement and driving forces |
| Decision | The architecture decision made |
| Consequences | Resulting context after decision |

**Validation Logic**:
```bash
# Check 9: Required ADR sections
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if ! grep -qE "^#+.*Context" "$f"; then
    echo "ERROR: $(basename $f) missing Context section"
  fi
  if ! grep -qE "^#+.*Decision" "$f"; then
    echo "ERROR: $(basename $f) missing Decision section"
  fi
  if ! grep -qE "^#+.*(Consequences|Implications)" "$f"; then
    echo "ERROR: $(basename $f) missing Consequences section"
  fi
done
```

---

### CORPUS-12: Cumulative Traceability (@brd + @prd + @ears + @bdd)

**Purpose**: Verify all standard ADRs have cumulative upstream traceability

**Severity**: Error (for standard ADRs only)

**Required Tags**: Each standard ADR must include all four:
- `@brd:` tag linking to source BRD element
- `@prd:` tag linking to source PRD element
- `@ears:` tag linking to source EARS element
- `@bdd:` tag linking to source BDD element

**Exemption**: ADR-REF documents are exempt from traceability requirements.

**Validation Logic**:
```bash
# Check 10: Cumulative traceability (skip ADR-REF)
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if [[ "$(basename $f)" =~ ADR-REF ]]; then continue; fi

  has_brd=$(grep -c "@brd:" "$f" 2>/dev/null || echo 0)
  has_prd=$(grep -c "@prd:" "$f" 2>/dev/null || echo 0)
  has_ears=$(grep -c "@ears:" "$f" 2>/dev/null || echo 0)
  has_bdd=$(grep -c "@bdd:" "$f" 2>/dev/null || echo 0)

  if [[ $has_brd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @brd traceability tag"
  fi
  if [[ $has_prd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @prd traceability tag"
  fi
  if [[ $has_ears -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @ears traceability tag"
  fi
  if [[ $has_bdd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @bdd traceability tag"
  fi
done
```

---

### CORPUS-13: Decision Conflict Detection

**Purpose**: Identify conflicting architecture decisions

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Contradicting decisions | Two ADRs making opposite choices |
| Overlapping scope | Multiple ADRs addressing same topic |
| Supersession tracking | Superseded ADRs reference replacement |

**Validation Logic**:
```bash
# Check 11: Decision topic overlaps
grep -rhE "^#+.*Decision:" "$ADR_DIR"/ADR-[0-9]*_*.md | \
  sed 's/.*Decision:\s*//' | sort | uniq -d
```

---

### CORPUS-14: SYS-Ready Score Threshold

**Purpose**: Verify ADR documents meet SYS-Ready threshold

**Severity**: Warning

**Threshold**: All standard ADRs should have SYS-Ready Score ≥90%

**Exemption**: ADR-REF documents are exempt from readiness scores.

**Validation Logic**:
```bash
# Check 12: SYS-Ready Score presence and format
grep -rn "SYS-Ready.*[0-9]\+%" "$ADR_DIR"/ADR-[0-9]*_*.md
# Verify scores are ≥90%
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 6+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate ADR reference | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing Context section | CORPUS-11 |
| CORPUS-E012 | Missing Decision section | CORPUS-11 |
| CORPUS-E013 | Missing Consequences section | CORPUS-11 |
| CORPUS-E014 | Missing @brd traceability tag | CORPUS-12 |
| CORPUS-E015 | Missing @prd traceability tag | CORPUS-12 |
| CORPUS-E016 | Missing @ears traceability tag | CORPUS-12 |
| CORPUS-E017 | Missing @bdd traceability tag | CORPUS-12 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W009 | Invalid decision status | CORPUS-09 |
| CORPUS-W013 | Potential decision conflict | CORPUS-13 |
| CORPUS-W014 | SYS-Ready Score below 90% | CORPUS-14 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. ADR Structure Requirements

### 3.1 Pattern A vs Pattern B (Historical Context)

Some projects may have legacy ADRs that don't follow current standards. Use this table to identify issues:

| Aspect | Pattern A (Legacy) | Pattern B (Current Standard) |
|--------|---------------------|------------------------------|
| Title Format | `ADR-00X` (3-digit) | `ADR-XX` (2-digit) |
| Main Header | `## ADR-XXX:` (H2) | `# ADR-XX:` (H1) |
| Section Headers | H3 (`###`) | H2 (`##`) |
| Document Control | Missing | Present |
| Diagrams | ASCII art | Mermaid |
| **Status** | **Requires full restructure** | **Template-compliant** |

### 3.2 Required Document Structure (Per Template)

| # | Section | Required |
|---|---------|----------|
| 1 | **YAML Frontmatter** | YES - title, tags, custom_fields |
| 2 | **Document Control** | YES - Project, Version, Date, Owner, Status, SYS-Ready Score |
| 3 | **Status** | YES - Current ADR status |
| 4 | **Context** | YES - Problem statement and background |
| 5 | **Decision** | YES - The architecture decision made |
| 6 | **Consequences** | YES - Positive and negative outcomes |
| 7 | **Alternatives Considered** | YES - Evaluated options |
| 8 | **Architecture Flow** | Recommended - Mermaid diagrams |
| 9 | **Implementation Details** | YES - Technical specifics |
| 10 | **Dependencies** | YES - Related systems and components |
| 11 | **Testing Strategy** | YES - Validation approach |
| 12 | **Rollback Strategy** | YES - Recovery procedures |
| 13 | **Success Metrics** | YES - Measurable criteria |
| 14 | **Timeline** | Optional - Implementation phases |
| 15 | **References** | YES - Related documents |
| 16 | **Traceability** | YES - Cumulative upstream tags |

### 3.3 SYS-Ready Score Calculation

| Category | Weight | Criteria |
|----------|--------|----------|
| **Decision Completeness** | 30% | Context/Decision/Consequences/Alternatives fully documented |
| **Architecture Clarity** | 35% | Mermaid diagrams, component responsibilities, cross-cutting concerns |
| **Implementation Readiness** | 20% | Complexity estimates, dependencies identified, rollback strategy |
| **Verification Approach** | 15% | Testing strategy, success metrics, validation criteria |

**Score Format**: `SYS-Ready 95% (Target: ≥90%)`

---

## 4. Cumulative Tagging Requirements

### 4.1 ADR Layer Position

ADR is **Layer 5** in the SDD workflow, requiring tags from all 4 upstream layers:

| Layer | Artifact | Tag Format | Required |
|-------|----------|------------|----------|
| 1 | BRD | `@brd: BRD.NN.TT.SS` | YES |
| 2 | PRD | `@prd: PRD.NN.TT.SS` | YES |
| 3 | EARS | `@ears: EARS.NN.TT.SS` | YES |
| 4 | BDD | `@bdd: BDD.NN.TT.SS` | YES |

### 4.2 Tag Format Convention

| Reference Type | Notation | Format | Example |
|----------------|----------|--------|---------|
| **Document** | Dash | `TYPE-NN` | `ADR-07` |
| **Element** | Dot | `TYPE.NN.TT.SS` | `BRD.07.01.01` |

**Rule**: ADRs are referenced by dash notation (`ADR-07`) but reference upstream elements with dot notation (`@brd: BRD.07.01.01`).

**Common Mistakes**:
| Wrong | Correct | Issue |
|-------|---------|-------|
| `@brd: BRD-07` | `@brd: BRD.07.01.01` | Dash instead of dot for element |
| `@adr: ADR.07.01.01` | `@adr: ADR-07` | Dot instead of dash for document |

---

## 5. Automated Validation Script

Save as `scripts/validate_adr_corpus.sh`:

```bash
#!/bin/bash
# ADR Corpus Validation Script
# Usage: ./scripts/validate_adr_corpus.sh [ADR_DIR] [--verbose|--errors-only]

ADR_DIR="${1:-docs/ADR}"
VERBOSE=false
ERRORS_ONLY=false

# Parse arguments
for arg in "$@"; do
  case $arg in
    --verbose) VERBOSE=true ;;
    --errors-only) ERRORS_ONLY=true ;;
  esac
done

ERRORS=0
WARNINGS=0
INFO=0

echo "=== ADR Corpus Validation ==="
echo "Directory: $ADR_DIR"
echo "Date: $(TZ=America/New_York date)"
echo ""

# CORPUS-01: Placeholder text
echo "Checking CORPUS-01: Placeholder text for existing documents..."
PLACEHOLDER=$(grep -rn "(future ADR)\|(when created)\|(to be defined)\|(pending)\|(TBD)" "$ADR_DIR"/ADR-*.md 2>/dev/null | wc -l)
if [ "$PLACEHOLDER" -gt 0 ]; then
  echo "  ERROR: Found $PLACEHOLDER placeholder references"
  $VERBOSE && grep -rn "(future ADR)\|(when created)\|(to be defined)\|(pending)\|(TBD)" "$ADR_DIR"/ADR-*.md 2>/dev/null
  ERRORS=$((ERRORS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-02: Premature downstream references
echo "Checking CORPUS-02: Premature downstream references..."
DOWNSTREAM=$(grep -rn "SYS-[0-9]\|REQ-[0-9]\|SPEC-[0-9]\|TASKS-[0-9]" "$ADR_DIR"/ADR-*.md 2>/dev/null | wc -l)
if [ "$DOWNSTREAM" -gt 0 ]; then
  echo "  ERROR: Found $DOWNSTREAM premature Layer 6+ references"
  $VERBOSE && grep -rn "SYS-[0-9]\|REQ-[0-9]\|SPEC-[0-9]\|TASKS-[0-9]" "$ADR_DIR"/ADR-*.md 2>/dev/null
  ERRORS=$((ERRORS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-04: Index synchronization
echo "Checking CORPUS-04: Index synchronization..."
INDEX_FILE=$(ls "$ADR_DIR"/ADR-*_index.md 2>/dev/null | head -1)
if [ -n "$INDEX_FILE" ]; then
  FILE_COUNT=$(ls "$ADR_DIR"/ADR-[0-9]*_*.md 2>/dev/null | grep -v index | wc -l)
  INDEX_COUNT=$(grep -c "| ADR-[0-9]" "$INDEX_FILE" 2>/dev/null || echo 0)
  if [ "$FILE_COUNT" -ne "$INDEX_COUNT" ]; then
    echo "  WARNING: Index has $INDEX_COUNT entries but $FILE_COUNT files exist"
    WARNINGS=$((WARNINGS + 1))
  else
    $ERRORS_ONLY || echo "  PASS (${FILE_COUNT} files, ${INDEX_COUNT} entries)"
  fi
else
  echo "  INFO: No index file found"
  INFO=$((INFO + 1))
fi

# CORPUS-06: Mermaid diagrams
echo "Checking CORPUS-06: Visualization coverage..."
NO_DIAGRAMS=0
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if [ -f "$f" ]; then
    count=$(grep -c "^\`\`\`mermaid" "$f" 2>/dev/null || echo 0)
    if [ "$count" -eq 0 ]; then
      NO_DIAGRAMS=$((NO_DIAGRAMS + 1))
      $VERBOSE && echo "  INFO: $(basename $f) has no Mermaid diagrams"
    fi
  fi
done
if [ "$NO_DIAGRAMS" -gt 0 ]; then
  echo "  INFO: $NO_DIAGRAMS ADRs without Mermaid diagrams"
  INFO=$((INFO + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-08: Duplicate ADR numbers
echo "Checking CORPUS-08: Element ID uniqueness..."
DUPLICATES=$(ls "$ADR_DIR"/ADR-[0-9]*_*.md 2>/dev/null | grep -oE "ADR-[0-9]+" | sort | uniq -d | wc -l)
if [ "$DUPLICATES" -gt 0 ]; then
  echo "  ERROR: Found $DUPLICATES duplicate ADR numbers"
  $VERBOSE && ls "$ADR_DIR"/ADR-[0-9]*_*.md | grep -oE "ADR-[0-9]+" | sort | uniq -d
  ERRORS=$((ERRORS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-10: File size
echo "Checking CORPUS-10: File size compliance..."
SIZE_ERRORS=0
SIZE_WARNINGS=0
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f")
    if [ "$lines" -gt 1200 ]; then
      echo "  ERROR: $(basename $f) exceeds 1200 lines ($lines)"
      SIZE_ERRORS=$((SIZE_ERRORS + 1))
    elif [ "$lines" -gt 600 ]; then
      $VERBOSE && echo "  WARNING: $(basename $f) exceeds 600 lines ($lines)"
      SIZE_WARNINGS=$((SIZE_WARNINGS + 1))
    fi
  fi
done
if [ "$SIZE_ERRORS" -gt 0 ]; then
  ERRORS=$((ERRORS + SIZE_ERRORS))
elif [ "$SIZE_WARNINGS" -gt 0 ]; then
  echo "  WARNING: $SIZE_WARNINGS files exceed 600 lines"
  WARNINGS=$((WARNINGS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-11: Context-Decision-Consequences structure
echo "Checking CORPUS-11: Context-Decision-Consequences structure..."
STRUCT_ERRORS=0
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if [ -f "$f" ] && [[ ! "$(basename $f)" =~ _index ]]; then
    missing=""
    if ! grep -qE "^#+.*Context" "$f"; then missing="Context "; fi
    if ! grep -qE "^#+.*Decision" "$f"; then missing="${missing}Decision "; fi
    if ! grep -qE "^#+.*(Consequences|Implications)" "$f"; then missing="${missing}Consequences"; fi
    if [ -n "$missing" ]; then
      echo "  ERROR: $(basename $f) missing: $missing"
      STRUCT_ERRORS=$((STRUCT_ERRORS + 1))
    fi
  fi
done
if [ "$STRUCT_ERRORS" -gt 0 ]; then
  ERRORS=$((ERRORS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-12: Cumulative traceability
echo "Checking CORPUS-12: Cumulative traceability..."
TRACE_ERRORS=0
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if [ -f "$f" ] && [[ ! "$(basename $f)" =~ ADR-REF ]] && [[ ! "$(basename $f)" =~ _index ]]; then
    missing=""
    if ! grep -q "@brd:" "$f" 2>/dev/null; then missing="@brd "; fi
    if ! grep -q "@prd:" "$f" 2>/dev/null; then missing="${missing}@prd "; fi
    if ! grep -q "@ears:" "$f" 2>/dev/null; then missing="${missing}@ears "; fi
    if ! grep -q "@bdd:" "$f" 2>/dev/null; then missing="${missing}@bdd"; fi
    if [ -n "$missing" ]; then
      $VERBOSE && echo "  ERROR: $(basename $f) missing tags: $missing"
      TRACE_ERRORS=$((TRACE_ERRORS + 1))
    fi
  fi
done
if [ "$TRACE_ERRORS" -gt 0 ]; then
  echo "  ERROR: $TRACE_ERRORS ADRs missing traceability tags"
  ERRORS=$((ERRORS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# CORPUS-14: SYS-Ready Score
echo "Checking CORPUS-14: SYS-Ready Score threshold..."
NO_SCORE=0
LOW_SCORE=0
for f in "$ADR_DIR"/ADR-[0-9]*_*.md; do
  if [ -f "$f" ] && [[ ! "$(basename $f)" =~ ADR-REF ]] && [[ ! "$(basename $f)" =~ _index ]]; then
    score=$(grep -oE "SYS-Ready.*[0-9]+%" "$f" 2>/dev/null | grep -oE "[0-9]+" | head -1)
    if [ -z "$score" ]; then
      NO_SCORE=$((NO_SCORE + 1))
      $VERBOSE && echo "  WARNING: $(basename $f) missing SYS-Ready Score"
    elif [ "$score" -lt 90 ]; then
      LOW_SCORE=$((LOW_SCORE + 1))
      $VERBOSE && echo "  WARNING: $(basename $f) SYS-Ready Score ${score}% < 90%"
    fi
  fi
done
if [ "$NO_SCORE" -gt 0 ] || [ "$LOW_SCORE" -gt 0 ]; then
  echo "  WARNING: $NO_SCORE missing scores, $LOW_SCORE below 90%"
  WARNINGS=$((WARNINGS + 1))
else
  $ERRORS_ONLY || echo "  PASS"
fi

# Summary
echo ""
echo "=== Validation Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"
echo "Info: $INFO"

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo "FAILED: Fix errors before proceeding to SYS creation"
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo ""
  echo "PASSED WITH WARNINGS: Review warnings before proceeding"
  exit 2
else
  echo ""
  echo "PASSED: ADR corpus ready for SYS creation"
  exit 0
fi
```

---

## 6. Post-Validation Actions

### 6.1 For Critical Errors

| Error | Remediation Steps |
|-------|-------------------|
| **E01: Title Numbering** | 1. Open YAML frontmatter<br>2. Change `title: "ADR-001:` to `title: "ADR-01:`<br>3. Search/replace `ADR-00X` with `ADR-0X` in body |
| **E02: Header Level** | 1. Find all `### Context`, `### Decision`, etc.<br>2. Change `###` to `##` for major sections<br>3. Verify H1 for main title, H2 for sections, H3 for subsections |
| **E03: Missing Document Control** | 1. Insert after YAML frontmatter, before Section 1<br>2. Use template from ADR-MVP-TEMPLATE.md (full template archived)<br>3. Include all required fields |
| **E04: Missing Traceability** | 1. Add Section 16 before References<br>2. Include all 4 upstream tags (@brd, @prd, @ears, @bdd)<br>3. Use TYPE.NN.TT.SS format for element references |
| **E05: Missing SYS-Ready Score** | 1. Add to Document Control table<br>2. Calculate score using criteria in Section 3.3<br>3. Format: `SYS-Ready NN% (Target: ≥90%)` |
| **E06: H1 Title** | 1. Change `## ADR-NN:` to `# ADR-NN:`<br>2. Ensure only one H1 per document |

### 6.2 For Warnings

| Warning | Remediation Steps |
|---------|-------------------|
| **W01: ASCII Diagrams** | 1. Identify all ASCII art (boxes, arrows, lines)<br>2. Convert to Mermaid syntax<br>3. Use `mermaid-gen` skill for assistance<br>4. Reference: DIAGRAM_STANDARDS.md |
| **W02: Custom Fields** | 1. Compare YAML to ADR-MVP-TEMPLATE.md (full template archived)<br>2. Standardize custom_fields structure<br>3. Required: artifact_type, layer, priority |
| **W03: Index Title** | 1. Change `ADR-000` to `ADR-00` in YAML<br>2. Update header if present |

---

## 7. ADR-Specific Validation Rules

### 7.1 Reserved ID Exemption

ADR-00_*.md files (index, traceability matrix, templates) are EXEMPT from validation checks E01-E06.

### 7.2 ADR-REF Documents

ADR-REF-NN_*.md files use reduced validation:
- Document Control: Required
- SYS-Ready Score: NOT REQUIRED
- Traceability tags: NOT REQUIRED
- Full structure: NOT REQUIRED

### 7.3 Mermaid Diagram Requirements

All architecture diagrams MUST use Mermaid syntax:
- Flowcharts: `flowchart TD`
- Sequence diagrams: `sequenceDiagram`
- Class diagrams: `classDiagram`
- State diagrams: `stateDiagram-v2`

Prohibited:
- ASCII box drawings (`+----+`, `|    |`)
- Text-based arrows (`--->`, `=====>`)
- Manual spacing for alignment

---

## 8. Baseline Metrics

Use this template to track corpus validation progress:

| Metric | Initial | Current | Target |
|--------|---------|---------|--------|
| Total ADRs | - | - | - |
| Critical Errors | - | 0 | 0 |
| Warnings | - | 0 | 0 |
| Missing Traceability | - | 0 | 0 |
| Missing SYS-Ready Score | - | 0 | 0 |
| Files >600 lines | - | 0 | 0 |
| Files without Mermaid | - | 0 | - |

**Baseline Command**:
```bash
./scripts/validate_adr_corpus.sh docs/ADR --verbose 2>&1 | tee tmp/adr_baseline_$(date +%Y%m%d).log
```

---

## 9. Validation Checklist

### Pre-SYS Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-ADR cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex decisions
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate ADR references
- [ ] **CORPUS-09**: All decision statuses are valid
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All ADRs have Context-Decision-Consequences
- [ ] **CORPUS-12**: All standard ADRs have cumulative traceability
- [ ] **CORPUS-13**: No conflicting decisions detected
- [ ] **CORPUS-14**: All ADRs have SYS-Ready Score ≥90%

---

## 10. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-adr-corpus.yml
name: ADR Corpus Validation

on:
  push:
    paths:
      - 'docs/05_ADR/**/*.md'
  pull_request:
    paths:
      - 'docs/05_ADR/**/*.md'

jobs:
  validate-adr-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate ADR Corpus
        run: |
          chmod +x ./scripts/validate_adr_corpus.sh
          ./scripts/validate_adr_corpus.sh docs/ADR
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: adr-validation-report
          path: tmp/adr_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# ADR corpus validation on staged ADR files
if git diff --cached --name-only | grep -q "^docs/05_ADR/"; then
  echo "Running ADR corpus validation..."
  ./scripts/validate_adr_corpus.sh docs/ADR --errors-only
  if [ $? -ne 0 ]; then
    echo "ADR corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "ADR corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-adr:
	@echo "Validating ADR corpus..."
	@./scripts/validate_adr_corpus.sh docs/ADR

validate-adr-verbose:
	@./scripts/validate_adr_corpus.sh docs/ADR --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr
	@echo "All corpus validations complete"
```

### Integration with SYS Layer Gate

ADR corpus validation should pass before creating SYS documents:

```bash
# Pre-SYS gate check
./scripts/validate_adr_corpus.sh docs/ADR
if [ $? -eq 0 ]; then
  echo "ADR corpus valid - ready for SYS layer creation"
else
  echo "Fix ADR corpus errors before proceeding to SYS layer"
  exit 1
fi
```

---

## 11. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-04 | Claude | Initial corpus validation rules |
| 1.1 | 2026-01-04 | Claude | Added Section 0 (Errors Template), Section 3 (Structure Requirements), Section 4 (Cumulative Tagging), complete validation script, Section 6 (Post-Validation Actions), Section 7 (ADR-Specific Rules), Section 8 (Baseline Metrics), numbered check comments |

---

## References

- [ADR_VALIDATION_RULES.md](./ADR_VALIDATION_RULES.md) - Individual file validation
- [ADR-MVP-TEMPLATE.md](./ADR-MVP-TEMPLATE.md) - ADR document template (full template archived)
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
