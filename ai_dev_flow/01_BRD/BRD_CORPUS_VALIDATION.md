# BRD Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | BRD_CORPUS_VALIDATION |
| Version | 1.1 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete BRD corpus |
| Trigger | Run after ALL BRDs are complete |
| Scope | Entire BRD corpus validation |
| Layer | Layer 1 → Layer 2 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all BRD files are created but BEFORE PRD creation begins. These rules validate the entire BRD corpus as a cohesive set, checking for cross-document consistency, reference integrity, and quality standards that cannot be verified at the individual file level.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual BRD Validation** | After each BRD creation | Single file | `BRD_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL BRDs complete | Entire BRD set | This document |

### Workflow Position

```
Individual BRD Creation → BRD_VALIDATION_RULES.md (per-file)
        ↓
All BRDs Complete
        ↓
BRD_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin PRD Creation (Layer 2)
FAIL → Fix issues, re-run corpus validation
```

---

## 0. Errors Found During BRD Creation

This section tracks common errors discovered during corpus validation. Populate during actual validation runs.

### 0.1 Critical Errors (MUST FIX)

| # | Error Type | BRDs Affected | Description | Fix Required |
|---|------------|---------------|-------------|--------------|
| E01 | **Premature Downstream References** | (Template) | Downstream artifacts (PRD, ADR, SPEC) referenced without "(pending)" status | Add "(pending)" suffix or use generic references |
| E02 | **Placeholder for Existing Document** | (Template) | BRD marked "(future BRD)" but file already exists | Replace placeholder with hyperlink reference |
| E03 | **Index Out of Sync** | (Template) | Index shows "Planned" but BRD file exists | Update index status to "Complete" |

### 0.2 Warnings (SHOULD FIX)

| # | Warning Type | BRDs Affected | Description | Recommendation |
|---|--------------|---------------|-------------|----------------|
| W01 | **Count Mismatch** | (Template) | Document claims "N items" but has different count | Reconcile claimed count with actual items |
| W02 | **Exact Cost Value** | (Template) | Cost specified without range | Use range format (e.g., $100-$150) |
| W03 | **Terminology Inconsistency** | (Template) | Same term used differently across documents | Standardize to single term variation |

### 0.3 Issues Fixed (Reference)

| # | Issue | Location | Fix Applied |
|---|-------|----------|-------------|
| (Template) | - | - | - |

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking PRD creation)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future BRD)` | BRD-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

**Validation Logic**:
```bash
# Check 1: Find placeholder text for existing documents
for placeholder in $(grep -rohE "BRD-[0-9]+ \(future" "$BRD_DIR"); do
  brd_num=$(echo "$placeholder" | grep -oE "BRD-[0-9]+")
  if ls "$BRD_DIR/${brd_num}_"*.md 2>/dev/null; then
    echo "ERROR: $brd_num exists but marked as future"
  fi
done

# Check 2: Find other placeholder patterns
grep -rniE "\(when created\)|\(to be defined\)|\(TBD\)" "$BRD_DIR"
```

**Fix**: Replace placeholder with actual hyperlink reference:
```markdown
# Before
See BRD-07 (future BRD) for AI Gateway details.

# After
See [BRD-07: AI Gateway Architecture](./BRD-07_ai_gateway_architecture.md) for details.
```

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 2+ artifacts

**Severity**: Error (blocking)

**Rationale**: BRD is Layer 1. It should NOT reference specific numbered PRD, ADR, SPEC, or other downstream documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `PRD-NN` | 2 | PRDs don't exist during BRD creation |
| `ADR-NN` | 5 | ADRs don't exist during BRD creation |
| `SPEC-NN` | 10 | SPECs don't exist during BRD creation |
| `TASKS-NN` | 11 | TASKS don't exist during BRD creation |
| `IPLAN-NN` | 12 | **DEPRECATED** - IPLAN merged into TASKS (2026-01-15) |

**Allowed Patterns** (generic references):
- "This will inform PRD development"
- "Downstream PRD artifacts will..."
- "See future ADR for architectural decisions"

**Validation Logic**:
```bash
# Check 3: Flag specific numbered references to downstream artifacts
grep -rnE "(PRD|ADR|SPEC|TASKS|IPLAN)-[0-9]{2,}" "$BRD_DIR" | \
  grep -v "Layer [0-9]" | \
  grep -v "SDD workflow"
# Expected: No output (all downstream refs should be generic)
```

**Fix**: Use generic names or topic descriptions:
```markdown
# Before (ERROR)
See PRD-03 for detailed feature specifications.

# After (CORRECT)
This requirement will be detailed in the PRD layer.
```

> **Layer 1 Traceability Note**: BRD is Layer 1 (entry point) in the SDD workflow. No upstream traceability tags are required.
>
> | Layer | Tag Format | Required |
> |-------|------------|----------|
> | 0 (Strategy) | External context | N/A (not SDD artifact) |
> | 1 (BRD) | Entry point | **NO upstream tags** |
> | 2+ (PRD, EARS, etc.) | `@brd:`, `@prd:`, etc. | YES (cumulative) |
>
> BRD documents MAY reference external strategy documents but these are informational, not traceability requirements.

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "7-state lifecycle" | 8 states listed | Count mismatch |
| "5 key features" | 6 features enumerated | Count mismatch |
| "3 integration points" | 4 integrations described | Count mismatch |

**Validation Logic**:
```bash
# Check 4: Extract claimed counts and compare with actual items
# Example: "7-state" should have exactly 7 state definitions
grep -nE "[0-9]+-state|[0-9]+ states" "$file" | while read claim; do
  count=$(echo "$claim" | grep -oE "[0-9]+")
  # Count actual state definitions in document
  actual=$(grep -cE "^#{2,3}.*State|^\*\*State" "$file")
  if [ "$count" -ne "$actual" ]; then
    echo "WARNING: Claimed $count states but found $actual"
  fi
done

# Check 5: Find "N key" or "N features" claims
grep -nE "[0-9]+ (key|features|steps|components|integrations)" "$BRD_DIR"/*.md
```

**Fix**: Reconcile counts with actual items:
```markdown
# Before (WARNING)
The system uses a 7-state position lifecycle:
1. Pending, 2. Open, 3. Partial, 4. Filled, 5. Closing, 6. Closed, 7. Cancelled, 8. Expired

# After (CORRECT)
The system uses an 8-state position lifecycle:
1. Pending, 2. Open, 3. Partial, 4. Filled, 5. Closing, 6. Closed, 7. Cancelled, 8. Expired
```

**MVP BRD Thresholds** (different from full BRD):
- Target: 200-400 lines
- Warning: 500 lines (consider if truly MVP scope)
- Error: 600 lines (likely not MVP - use full BRD template)

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify BRD index file reflects actual file states

**Severity**: Error

**Index File Pattern**: `BRD-*_index.md` (e.g., `BRD-00_index.md`, `BRD-000_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing BRD files listed in index |
| Version currency | Version numbers match file headers |
| Status accuracy | Status matches actual file content |

**Validation Logic**:
```bash
# Setup: Find index file using glob pattern
for f in "$BRD_DIR"/BRD-*_index.md; do
  if [[ -f "$f" ]]; then
    index_file="$f"
    break
  fi
done

# Check 6: Files marked "Planned" that exist
grep -E "\| Planned \|" "$index_file" | while read line; do
  brd=$(echo "$line" | grep -oE "BRD-[0-9]+")
  if ls "$BRD_DIR/${brd}_"*.md 2>/dev/null; then
    echo "ERROR: $brd exists but marked Planned in index"
  fi
done

# Check 7: Existing files not in index
for f in "$BRD_DIR"/BRD-[0-9]*_*.md; do
  brd=$(basename "$f" | grep -oE "BRD-[0-9]+")
  if ! grep -q "$brd" "$index_file"; then
    echo "ERROR: $brd exists but not in index"
  fi
done
```

**Fix**: Update index to match reality:
```markdown
# Before (ERROR in index)
| BRD-07 | AI Gateway | Planned | - |

# After (CORRECT - file exists)
| BRD-07 | AI Gateway Architecture | Complete | 1.0 |
```

---

### CORPUS-05: Inter-BRD Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Purpose**: ~~Ensure navigation links between related BRDs~~

**Reason for Deprecation**: Per SDD traceability rules, document name references (e.g., `BRD-01`, `BRD-07`) are valid and sufficient for traceability. Hyperlinks are optional enhancements, not requirements.

**Valid Reference Formats**:
```markdown
# All of these are valid per traceability rules:

# Document name reference (sufficient)
See BRD-07 for routing details.
This integrates with BRD-15 data architecture.

# Optional: with hyperlink (enhanced navigation)
See [BRD-07: AI Gateway](./BRD-07_ai_gateway_architecture.md) for routing details.
```

**Traceability Rule**: Document IDs (`BRD-NN`) provide sufficient traceability. Hyperlinks are optional convenience features and should not trigger validation warnings.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex concepts

**Severity**: Info

**Recommended Diagrams by BRD Type**:
| BRD Type | Recommended Diagrams |
|----------|---------------------|
| Architecture | Component diagram, deployment diagram |
| Data | Data flow diagram, ERD |
| Integration | Sequence diagram, integration map |
| Workflow | State diagram, flowchart |
| Agent | Agent hierarchy, communication flow |

**Validation Logic**:
```bash
# Check 8: Find files without Mermaid diagrams
for f in "$BRD_DIR"/BRD-[0-9]*_*.md; do
  diagram_count=$(grep -c '```mermaid' "$f" || echo 0)
  if [ "$diagram_count" -eq 0 ]; then
    echo "INFO: $(basename $f) has no Mermaid diagrams"
  fi
done

# Check 9: Count diagrams per file
echo "=== Diagram Coverage ==="
for f in "$BRD_DIR"/BRD-[0-9]*_*.md; do
  count=$(grep -c '```mermaid' "$f" 2>/dev/null || echo 0)
  echo "$(basename $f): $count diagrams"
done
```

**Recommendation**: Add diagrams for:
- Architecture decisions (flowchart or C4)
- Data flows (sequence or flowchart)
- State machines (stateDiagram-v2)
- Agent hierarchies (graph TD)

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all BRDs

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Term consistency | Same term used same way across docs |
| Acronym expansion | Acronyms expanded on first use per doc |
| No conflicting definitions | Same concept not defined differently |
| Central glossary reference | Complex terms reference glossary |

**Common Inconsistencies**:
| Inconsistency | Example |
|---------------|---------|
| Hyphenation | "real-time" vs "realtime" vs "real time" |
| E-mail variants | "e-mail" vs "email" vs "E-mail" |
| Infrastructure terms | "on-premise" vs "on-premises" vs "onprem" |
| Capitalization | "Agent" vs "agent" |

**Validation Logic**:
```bash
# Check 10: Find term variations using associative array
declare -A term_variations
term_variations["real-time"]="realtime|real time"
term_variations["e-mail"]="email|E-mail"
term_variations["on-premise"]="on-premises|onprem"

for term in "${!term_variations[@]}"; do
  variations="${term_variations[$term]}"
  primary_count=$(grep -rciE "\b$term\b" "$BRD_DIR" | grep -v ":0" | wc -l)
  var_count=$(grep -rciE "\b($variations)\b" "$BRD_DIR" | grep -v ":0" | wc -l)
  if [[ "$primary_count" -gt 0 && "$var_count" -gt 0 ]]; then
    echo "WARNING: '$term' in $primary_count files, variations in $var_count files"
  fi
done

# Check 11: Quick scan for common inconsistencies
echo "=== Quick Terminology Scan ==="
grep -rci "real-time\|realtime" "$BRD_DIR" | grep -v ":0"
```

**Fix**: Standardize terminology and reference central glossary:
```markdown
# Before (inconsistent)
Doc A: "The system handles real-time data..."
Doc B: "The system handles realtime data..."

# After (consistent)
Doc A: "The system handles real-time data..."
Doc B: "The system handles real-time data..."
```

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the BRD corpus

**Severity**: Error

**Element ID Format**: `BRD.NN.TT.SS`
- NN = Document number
- TT = Element type code
- SS = Sequence number

**Validation Logic**:
```bash
# Check 12: Extract all element IDs and find duplicates
grep -rohE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" "$BRD_DIR" | \
  sort | uniq -d | while read dup; do
    echo "ERROR: Duplicate element ID: $dup"
    grep -rn "$dup" "$BRD_DIR"
  done

# Check 13: Count element IDs per document
echo "=== Element ID Distribution ==="
for f in "$BRD_DIR"/BRD-[0-9]*_*.md; do
  count=$(grep -coE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" "$f" 2>/dev/null || echo 0)
  echo "$(basename $f): $count element IDs"
done
```

**Allowed Duplicates** (same ID referenced, not defined):
- Cross-references using `@brd:` tags
- Traceability sections listing upstream sources

**Fix**: Renumber duplicate IDs:
```markdown
# Before (ERROR - same ID in two files)
BRD-07: BRD.07.01.15 - Gateway routing requirement
BRD-15: BRD.07.01.15 - Data validation requirement  # DUPLICATE!

# After (CORRECT)
BRD-07: BRD.07.01.15 - Gateway routing requirement
BRD-15: BRD.15.01.15 - Data validation requirement
```

---

### CORPUS-09: Cost Estimate Format

**Purpose**: Validate cost estimates use ranges for flexibility

**Severity**: Warning

**Pattern**: Exact dollar amounts without ranges

**Good Formats**:
| Format | Example | Status |
|--------|---------|--------|
| Range | $100-$150/month | Correct |
| Approximate | ~$125/month | Correct |
| Range with qualifier | $100-$200 depending on usage | Correct |

**Bad Formats**:
| Format | Example | Issue |
|--------|---------|-------|
| Exact | $125/month | Too precise |
| No unit | $500 | Missing time unit |

**Validation Logic**:
```bash
# Check 14: Find exact dollar amounts without range indicators
grep -rnE "\\\$[0-9,]+(\.[0-9]+)?[^-~0-9]" "$BRD_DIR" | \
  grep -v "range" | \
  grep -v "approximately" | \
  grep -v "~"

# Check 15: Count cost-related patterns
echo "=== Cost Format Analysis ==="
echo "Exact values: $(grep -rcoE '\$[0-9]+' "$BRD_DIR" | grep -v ":0" | wc -l)"
echo "Ranges (~): $(grep -rcoE '~\$[0-9]+' "$BRD_DIR" | grep -v ":0" | wc -l)"
echo "Ranges (-): $(grep -rcoE '\$[0-9]+-\$[0-9]+' "$BRD_DIR" | grep -v ":0" | wc -l)"
```

**Fix**: Use ranges or approximations:
```markdown
# Before (WARNING)
Monthly cost: $175

# After (CORRECT)
Monthly cost: $150-$200 (varies by usage)
# OR
Monthly cost: ~$175
```

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

**General Thresholds**:
| Metric | Warning | Error | Rationale |
|--------|---------|-------|-----------|
| Lines | 600 | 1,200 | Readability |
| Tokens | 50,000 | 100,000 | Tool limits |
| File size | 200KB | 400KB | Processing limits |

**Type-Specific Limits** (enhanced from BDD patterns):
| File Type | Warning | Error | Max Items |
|-----------|---------|-------|-----------|
| BRD index file (`BRD-NN.0_*.md`) | 300 lines | 500 lines | N/A |
| BRD section file (`BRD-NN.N_*.md`) | 400 lines | 600 lines | N/A |
| BRD single file (`BRD-NN_*.md`) | 600 lines | 1,200 lines | N/A |
| Elements per section | 15 | 25 | 25 max |
| MVP BRD files | 400 lines | 600 lines | Use full template if exceeded |

**Validation Logic**:
```bash
# Check 1: General line count check
for f in "$BRD_DIR"/BRD-[0-9]*_*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 1200 ]; then
    echo "ERROR: $(basename $f) exceeds 1200 lines ($lines)"
  elif [ "$lines" -gt 600 ]; then
    echo "WARNING: $(basename $f) exceeds 600 lines ($lines)"
  fi
done

# Check 2: Type-specific validation
for f in "$BRD_DIR"/BRD-*_*/*0_*.md; do
  lines=$(wc -l < "$f" 2>/dev/null)
  if [ "$lines" -gt 500 ]; then
    echo "ERROR: Index file $(basename $f) exceeds 500 lines ($lines)"
  elif [ "$lines" -gt 300 ]; then
    echo "WARNING: Index file $(basename $f) exceeds 300 lines ($lines)"
  fi
done

# Check 3: Section file validation
for f in "$BRD_DIR"/BRD-*_*/BRD-*.[1-9]*.md; do
  lines=$(wc -l < "$f" 2>/dev/null)
  if [ "$lines" -gt 600 ]; then
    echo "ERROR: Section file $(basename $f) exceeds 600 lines ($lines)"
  elif [ "$lines" -gt 400 ]; then
    echo "WARNING: Section file $(basename $f) exceeds 400 lines ($lines)"
  fi
done
```

**Fix**: Split into section-based files:
```
docs/01_BRD/BRD-07_ai_gateway/
├── BRD-07.0_index.md
├── BRD-07.1_executive_summary.md
├── BRD-07.2_architecture.md
└── BRD-07.3_integration.md
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 2+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate element ID across corpus | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| ~~CORPUS-W002~~ | ~~Missing inter-BRD hyperlinks~~ | ~~CORPUS-05~~ (deprecated) |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Exact cost without range | CORPUS-09 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |
| CORPUS-I002 | Consider adding data flow diagram | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_brd_corpus.sh docs/BRD

# With verbose output
./scripts/validate_brd_corpus.sh docs/BRD --verbose

# Check specific category
./scripts/validate_brd_corpus.sh docs/BRD --check=placeholders
./scripts/validate_brd_corpus.sh docs/BRD --check=index
./scripts/validate_brd_corpus.sh docs/BRD --check=crosslinks
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Errors found (blocking) |
| 2 | Warnings found (non-blocking) |
| 3 | Script error |

### 3.1 Complete Validation Script

Save as `scripts/validate_brd_corpus.sh`:

```bash
#!/bin/bash
# BRD Corpus Validation Script
# Usage: ./scripts/validate_brd_corpus.sh [BRD_DIR]
# Validates entire BRD corpus for CORPUS-01 through CORPUS-10 checks

BRD_DIR="${1:-docs/BRD}"
ERRORS=0
WARNINGS=0

echo "=== BRD Corpus Validation ==="
echo "Directory: $BRD_DIR"
echo ""

# CORPUS-01: Placeholder Text for Existing Documents
echo "Checking CORPUS-01: Placeholder text for existing documents..."
for placeholder in $(grep -rohE "BRD-[0-9]+ \(future" "$BRD_DIR" 2>/dev/null); do
  brd_num=$(echo "$placeholder" | grep -oE "BRD-[0-9]+")
  if ls "$BRD_DIR/${brd_num}_"*.md 2>/dev/null >/dev/null; then
    echo "  ERROR: $brd_num exists but marked as future"
    ERRORS=$((ERRORS + 1))
  fi
done
[ $ERRORS -eq 0 ] && echo "  PASS"

# CORPUS-02: Premature Downstream References
echo "Checking CORPUS-02: Premature downstream references..."
DOWNSTREAM=$(grep -rnE "(PRD|ADR|SPEC|TASKS|IPLAN)-[0-9]{2,}" "$BRD_DIR" 2>/dev/null | grep -v "Layer [0-9]" | grep -v "SDD workflow" | wc -l)
if [ $DOWNSTREAM -gt 0 ]; then
  echo "  ERROR: $DOWNSTREAM premature downstream references found"
  ERRORS=$((ERRORS + 1))
else
  echo "  PASS"
fi

# CORPUS-04: Index Synchronization
echo "Checking CORPUS-04: Index synchronization..."
for f in "$BRD_DIR"/BRD-*_index.md "$BRD_DIR"/BRD-000_index.md 2>/dev/null; do
  if [[ -f "$f" ]]; then
    index_file="$f"
    break
  fi
done
if [[ -n "$index_file" ]]; then
  # Check for files marked "Planned" that exist
  grep -E "\| Planned \|" "$index_file" 2>/dev/null | while read line; do
    brd=$(echo "$line" | grep -oE "BRD-[0-9]+")
    if ls "$BRD_DIR/${brd}_"*.md 2>/dev/null >/dev/null; then
      echo "  ERROR: $brd exists but marked Planned in index"
      ERRORS=$((ERRORS + 1))
    fi
  done
  echo "  PASS (if no errors above)"
else
  echo "  SKIP: No index file found"
fi

# CORPUS-07: Glossary Consistency (sample check)
echo "Checking CORPUS-07: Terminology consistency..."
real_time=$(grep -rci "real-time" "$BRD_DIR" 2>/dev/null | grep -v ":0" | wc -l)
realtime=$(grep -rci "realtime" "$BRD_DIR" 2>/dev/null | grep -v ":0" | wc -l)
if [[ "$real_time" -gt 0 && "$realtime" -gt 0 ]]; then
  echo "  WARNING: Mixed 'real-time' ($real_time) and 'realtime' ($realtime) usage"
  WARNINGS=$((WARNINGS + 1))
else
  echo "  PASS"
fi

# CORPUS-08: Element ID Uniqueness
echo "Checking CORPUS-08: Element ID uniqueness..."
DUPLICATES=$(grep -rohE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" "$BRD_DIR" 2>/dev/null | sort | uniq -d | wc -l)
if [ $DUPLICATES -gt 0 ]; then
  echo "  ERROR: $DUPLICATES duplicate element IDs found"
  grep -rohE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" "$BRD_DIR" | sort | uniq -d
  ERRORS=$((ERRORS + 1))
else
  echo "  PASS"
fi

# CORPUS-09: Cost Estimate Format
echo "Checking CORPUS-09: Cost estimate format..."
EXACT_COSTS=$(grep -rnE "\\\$[0-9,]+(\.[0-9]+)?[^-~0-9]" "$BRD_DIR" 2>/dev/null | grep -v "range" | grep -v "approximately" | grep -v "~" | wc -l)
if [ $EXACT_COSTS -gt 5 ]; then
  echo "  WARNING: $EXACT_COSTS exact cost values without ranges"
  WARNINGS=$((WARNINGS + 1))
else
  echo "  PASS"
fi

# CORPUS-10: File Size Compliance
echo "Checking CORPUS-10: File size compliance..."
for f in "$BRD_DIR"/BRD-[0-9]*_*.md; do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f")
    if [ "$lines" -gt 1200 ]; then
      echo "  ERROR: $(basename $f) exceeds 1200 lines ($lines)"
      ERRORS=$((ERRORS + 1))
    elif [ "$lines" -gt 600 ]; then
      echo "  WARNING: $(basename $f) exceeds 600 lines ($lines)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
done
echo "  PASS (if no errors above)"

# Summary
echo ""
echo "=== Validation Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
  echo "FAILED: Fix errors before PRD creation"
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo "PASSED with warnings: Review before PRD creation"
  exit 2
else
  echo "PASSED: BRD corpus ready for PRD creation"
  exit 0
fi
```

---

## 4. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-brd-corpus.yml
name: BRD Corpus Validation

on:
  push:
    paths:
      - 'docs/01_BRD/**/*.md'
  pull_request:
    paths:
      - 'docs/01_BRD/**/*.md'

jobs:
  validate-brd-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate BRD Corpus
        run: |
          chmod +x ./scripts/validate_brd_corpus.sh
          ./scripts/validate_brd_corpus.sh docs/BRD
        continue-on-error: false  # Block on errors

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: brd-validation-report
          path: tmp/brd_validation_*.log
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (BRD validation)

# Check if BRD files are staged
if git diff --cached --name-only | grep -q "^docs/01_BRD/"; then
  echo "Running BRD corpus validation..."
  ./scripts/validate_brd_corpus.sh docs/BRD --errors-only
  if [[ $? -ne 0 ]]; then
    echo "BRD validation failed. Fix errors before committing."
    exit 1
  fi
fi
```

### Makefile Integration

```makefile
# Makefile
.PHONY: validate-brd

validate-brd:
	@./scripts/validate_brd_corpus.sh docs/BRD

validate-all: validate-brd validate-prd validate-ears
	@echo "All corpus validations complete"
```

---

## 5. Remediation Guide

### Priority Order

1. **CORPUS-E*** (Errors)**: Fix immediately - block PRD creation
2. **CORPUS-W*** (Warnings)**: Fix before PRD creation if possible
3. **CORPUS-I*** (Info)**: Consider for quality improvement

### Quick Fix Commands

```bash
# Find all placeholder text
grep -rniE "\(future (BRD|PRD|ADR)\)|\(when created\)|\(to be defined\)|\(pending\)" docs/BRD

# Find premature downstream references
grep -rnE "(PRD|ADR|SPEC|TASKS|IPLAN)-[0-9]{2,}" docs/BRD

# Find missing hyperlinks
grep -rnE "BRD-[0-9]+" docs/BRD | grep -v "\[BRD-"

# Find duplicate element IDs
grep -rohE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" docs/BRD | sort | uniq -d

# Check file sizes
wc -l docs/01_BRD/BRD-[0-9]*_*.md | sort -n
```

### Common Remediation Patterns

#### Placeholder → Hyperlink
```bash
# Pattern
sed -i 's/BRD-07 (future BRD)/[BRD-07: AI Gateway](\.\/BRD-07_ai_gateway.md)/g' "$file"
```

#### Downstream Reference → Generic
```bash
# Pattern
sed -i 's/See PRD-03 for details/This will be detailed in the PRD layer/g' "$file"
```

#### Index Status Update
```bash
# Manual update required - verify file exists, then update index
ls docs/01_BRD/BRD-07_*.md && \
  sed -i 's/| BRD-07 .* Planned |/| BRD-07 | AI Gateway | Complete | 1.0 |/' docs/01_BRD/BRD-000_index.md
```

---

## 5. Validation Checklist

### Pre-PRD Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-BRD cross-links present~~ (deprecated - document IDs are sufficient)
- [ ] **CORPUS-06**: Diagrams present for complex concepts
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Cost estimates use ranges
- [ ] **CORPUS-10**: All files under size limits

### Sign-off

| Check | Status | Date | Reviewer |
|-------|--------|------|----------|
| Errors (E001-E005) | ☐ Pass | | |
| Warnings (W001-W005) | ☐ Reviewed | | |
| Info (I001-I002) | ☐ Acknowledged | | |

### 5.3 BRD Corpus Baseline Metrics

This section captures verified counts from corpus validation runs. Update after each validation.

| BRD | Sections | Elements | Lines | Last Verified |
|-----|----------|----------|-------|---------------|
| (Template) | - | - | - | YYYY-MM-DD |
| **TOTAL** | **-** | **-** | **-** | |

**Validation Command**:
```bash
# Generate corpus metrics
for f in docs/01_BRD/BRD-[0-9]*_*.md; do
  lines=$(wc -l < "$f")
  elements=$(grep -cE "BRD\.[0-9]+\.[0-9]+\.[0-9]+" "$f" 2>/dev/null || echo 0)
  echo "$(basename $f): $lines lines, $elements elements"
done
```

---

## 6. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2026-01-04 | - | Added type-specific file limits (CORPUS-10); added Errors Found section; added Baseline Metrics section; added Complete Validation Script; added Layer 1 traceability note; reorganized bash checks |
| 1.0 | 2026-01-04 | - | Initial corpus validation rules |

---

## References

- [BRD_VALIDATION_RULES.md](./BRD_VALIDATION_RULES.md) - Individual file validation
- [BRD-TEMPLATE.md](./BRD-TEMPLATE.md) - BRD document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
