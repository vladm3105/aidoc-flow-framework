---
title: "PRD Corpus Validation"
tags:
  - corpus-validation
  - layer-2-artifact
  - shared-architecture
custom_fields:
  document_type: corpus-validation
  artifact_type: PRD
  layer: 2
  priority: shared
  development_status: active
---

# PRD Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | PRD_CORPUS_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete PRD corpus |
| Trigger | Run after ALL PRDs are complete |
| Scope | Entire PRD corpus validation |
| Layer | Layer 2 → Layer 3 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all PRD files are created but BEFORE EARS creation begins. These rules validate the entire PRD corpus as a cohesive set, checking for cross-document consistency, reference integrity, and quality standards that cannot be verified at the individual file level.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual PRD Validation** | After each PRD creation | Single file | `PRD_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL PRDs complete | Entire PRD set | This document |

### Workflow Position

```
Individual PRD Creation → PRD_VALIDATION_RULES.md (per-file)
        ↓
All PRDs Complete
        ↓
PRD_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin EARS Creation (Layer 3)
FAIL → Fix issues, re-run corpus validation
```

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text and Prohibited Content

**Purpose**: Detect placeholder text that references documents which already exist, plus incomplete markers

**Severity**: Error (blocking EARS creation)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future PRD)` | PRD-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |
| `[TBD]` | Bracketed placeholder |
| `[TODO]` | Todo marker in final document |
| `XXX` | Development marker |
| `FIXME` | Bug marker in documentation |
| `HACK` | Temporary workaround marker |
| `WIP` | Work in progress marker |
| `[PLACEHOLDER]` | Explicit placeholder |
| `???` | Uncertainty marker |
| `<<<` | Merge conflict marker |

**Validation Logic**:
```bash
# For each PRD reference in placeholder format, check if file exists
for placeholder in $(grep -rohE "PRD-[0-9]+ \(future" "$PRD_DIR"); do
  prd_num=$(echo "$placeholder" | grep -oE "PRD-[0-9]+")
  if ls "$PRD_DIR/${prd_num}_"*.md 2>/dev/null; then
    echo "ERROR: $prd_num exists but marked as future"
  fi
done
```

**Fix**: Replace placeholder with actual hyperlink reference:
```markdown
# Before
See PRD-07 (future PRD) for AI Gateway product details.

# After
See [PRD-07: AI Gateway Product](./PRD-07_ai_gateway_product.md) for details.
```

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 3+ artifacts

**Severity**: Error (blocking)

**Rationale**: PRD is Layer 2. It should NOT reference specific numbered ADR, SPEC, or other downstream documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `ADR-NN` | 5 | ADRs don't exist during PRD creation |
| `SYS-NN` | 6 | SYS don't exist during PRD creation |
| `REQ-NN` | 7 | REQs don't exist during PRD creation |
| `SPEC-NN` | 10 | SPECs don't exist during PRD creation |
| `TASKS-NN` | 11 | TASKS don't exist during PRD creation |

**Allowed Patterns** (generic references):
- "This will inform EARS development"
- "Downstream ADR artifacts will..."
- "See future SPEC for technical details"

**Validation Logic**:
```bash
# Flag specific numbered references to downstream artifacts
grep -rnE "(ADR|SYS|REQ|SPEC|TASKS)-[0-9]{2,}" "$PRD_DIR" | \
  grep -v "Layer [0-9]" | \
  grep -v "SDD workflow"
```

**Fix**: Use generic names or topic descriptions:
```markdown
# Before (ERROR)
See ADR-03 for detailed architecture decisions.

# After (CORRECT)
Architecture decisions will be documented in the ADR layer.
```

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 user stories" | 6 stories listed | Count mismatch |
| "3 key features" | 4 features enumerated | Count mismatch |
| "7 success metrics" | 8 metrics described | Count mismatch |

**Validation Logic**:
```bash
# Extract claimed counts and compare with actual items
grep -nE "[0-9]+ user stor|[0-9]+ feature|[0-9]+ metric" "$file" | while read claim; do
  count=$(echo "$claim" | grep -oE "[0-9]+")
  # Count actual items in document
  # Manual verification recommended
done
```

**Fix**: Reconcile counts with actual items.

---

### CORPUS-04: Bidirectional Index Completeness

**Purpose**: Verify PRD index file reflects actual file states (bidirectional check)

**Severity**: Error

**Index File Pattern**: `PRD-*_index.md` (e.g., `PRD-00_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing PRD files listed in index |
| No dead references | All index entries have corresponding files |
| Version currency | Version numbers match file headers |
| Status accuracy | Status matches actual file content |

**Validation Logic**:
```bash
# Find index file using glob pattern
for f in "$PRD_DIR"/PRD-*_index.md; do
  if [[ -f "$f" ]]; then
    index_file="$f"
    break
  fi
done

# Direction 1: Check for files marked "Planned" that exist
grep -E "\| Planned \|" "$index_file" | while read line; do
  prd=$(echo "$line" | grep -oE "PRD-[0-9]+")
  if ls "$PRD_DIR/${prd}_"*.md 2>/dev/null; then
    echo "ERROR: $prd exists but marked Planned in index"
  fi
done

# Direction 2: Check for orphan files not in index
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  prd=$(basename "$f" | grep -oE "PRD-[0-9]+")
  if ! grep -q "$prd" "$index_file" 2>/dev/null; then
    echo "ERROR: $(basename $f) not listed in index"
  fi
done

# Direction 3: Check for dead references in index
grep -oE "PRD-[0-9]+" "$index_file" | sort -u | while read prd; do
  if ! ls "$PRD_DIR/${prd}_"*.md 2>/dev/null >/dev/null; then
    if ! ls "$PRD_DIR/${prd}/"*.md 2>/dev/null >/dev/null; then
      echo "ERROR: $prd in index but file not found"
    fi
  fi
done
```

**Fix**: Update index to match reality or create missing files.

---

### CORPUS-05: Inter-PRD Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Purpose**: ~~Ensure navigation links between related PRDs~~

**Reason for Deprecation**: Per SDD traceability rules, document name references (e.g., `PRD-01`, `PRD-07`) are valid and sufficient for traceability. Hyperlinks are optional enhancements, not requirements.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex concepts

**Severity**: Info

**Recommended Diagrams by PRD Type**:
| PRD Type | Recommended Diagrams |
|----------|---------------------|
| Product Overview | User journey, feature map |
| Feature Set | Feature interaction diagram |
| User Stories | User flow diagram |
| Metrics | Dashboard mockup, KPI hierarchy |

**Validation Logic**:
```bash
# Check for Mermaid code blocks
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  diagram_count=$(grep -c '```mermaid' "$f" || true)
  if [ "$diagram_count" -eq 0 ]; then
    echo "INFO: $(basename $f) has no Mermaid diagrams"
  fi
done
```

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all PRDs

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Term consistency | Same term used same way across docs |
| Acronym expansion | Acronyms expanded on first use per doc |
| No conflicting definitions | Same concept not defined differently |

**Common Inconsistencies**:
| Inconsistency | Example |
|---------------|---------|
| Hyphenation | "real-time" vs "realtime" |
| Capitalization | "User Story" vs "user story" |
| Abbreviations | "MVP" vs "minimum viable product" |

**Validation Logic**:
```bash
# Check for term variations
declare -A term_variations
term_variations["real-time"]="realtime|real time"
term_variations["user-story"]="user story|userstory"

for term in "${!term_variations[@]}"; do
  # Check for inconsistent usage
done
```

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the PRD corpus

**Severity**: Error

**Element ID Format**: `PRD.NN.TT.SS`
- NN = Document number
- TT = Element type code
- SS = Sequence number

**Validation Logic**:
```bash
# Extract all element IDs and find duplicates
grep -rohE "PRD\.[0-9]+\.[0-9]+\.[0-9]+" "$PRD_DIR" | \
  sort | uniq -d | while read dup; do
    echo "ERROR: Duplicate element ID: $dup"
  done
```

---

### CORPUS-09: Cost Estimate Format

**Purpose**: Validate cost estimates use ranges for flexibility

**Severity**: Warning

**Good Formats**:
| Format | Example | Status |
|--------|---------|--------|
| Range | $100-$150/month | Correct |
| Approximate | ~$125/month | Correct |

**Bad Formats**:
| Format | Example | Issue |
|--------|---------|-------|
| Exact | $125/month | Too precise |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 600 | 1,200 |
| Tokens | 50,000 | 100,000 |

**MVP PRD Thresholds**:
- Target: 300-500 lines
- Warning: 500 lines
- Error: 800 lines (exceeds MVP scope)

---

### CORPUS-11: BRD Traceability Completeness (4-Segment Format)

**Purpose**: Verify all PRDs have upstream BRD references using correct element-level format

**Severity**: Error

**Required Tags**: Each PRD must include `@brd:` tags linking to source BRD elements

**Format Requirement**: BRD tags MUST use 4-segment dot notation: `BRD.NN.TT.SS`
- NN = Document number
- TT = Element type code
- SS = Sequence number

**Valid vs Invalid Formats**:
| Format | Example | Status |
|--------|---------|--------|
| 4-segment dot | `@brd: BRD.07.01.01` | ✓ Correct |
| 3-segment dot | `@brd: BRD.07.01` | ✗ Invalid (missing sequence) |
| Dash notation | `@brd: BRD-07` | ✗ Invalid (document-level only) |
| No dots | `@brd: BRD07` | ✗ Invalid (missing separators) |

**Validation Logic**:
```bash
# Check each PRD has @brd tags
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  if ! grep -q "@brd:" "$f"; then
    echo "ERROR: $(basename $f) missing @brd traceability tags"
  else
    # Check for incorrect BRD tag format (not 4-segment)
    bad_tags=$(grep -oP '@brd:\s*\KBRD[.-][0-9]+(\.[0-9]+)*' "$f" 2>/dev/null | \
      grep -vE '^BRD\.[0-9]+\.[0-9]+\.[0-9]+$' || true)
    if [[ -n "$bad_tags" ]]; then
      echo "ERROR: $(basename $f) has invalid @brd format: $bad_tags (must be BRD.NN.TT.SS)"
    fi
  fi
done
```

**Fix**: Add BRD traceability tags with correct 4-segment format:
```markdown
## Traceability

### Upstream Sources
# WRONG: @brd: BRD-07
# WRONG: @brd: BRD.07
# CORRECT:
- @brd: BRD.01.23.01 - Business objective for user authentication
- @brd: BRD.01.01.05 - Functional requirement for login flow
- @brd: BRD.07.32.01 - AI Gateway architecture topic
```

---

### CORPUS-12: User Story Coverage

**Purpose**: Verify BRD business objectives have corresponding PRD user stories

**Severity**: Warning

**Validation Logic**:
```bash
# Compare BRD business objectives with PRD user stories
# Manual verification recommended for completeness
```

---

### CORPUS-13: Template Structure Compliance

**Purpose**: Validate PRD files have all required sections from PRD-MVP-TEMPLATE.md

**Severity**: Error

**Template Variants**:

| Template | Sections | Score Threshold | Use Case |
|----------|----------|-----------------|----------|
| **MVP** | 17 (1-17) | ≥85% | Rapid prototyping, hypothesis validation |
| 9 | Functional Requirements | Yes |
| 10 | Customer-Facing Content & Messaging | Yes |
| 11 | Acceptance Criteria | Yes |
| 12 | Constraints & Assumptions | Yes |
| 13 | Risk Assessment | Yes |
| 14 | Success Definition | Yes |
| 15 | Stakeholders & Communication | Yes |
| 16 | Implementation Approach | Yes |
| 17 | Budget & Resources | Yes |
| 18 | Traceability | Yes |
| 19 | References | Yes |
| 20 | EARS Enhancement Appendix | Yes |
| 21 | Quality Assurance & Testing Strategy | Yes |

**MVP Template Required Sections** (17 sections):
| # | Section | Required |
|---|---------|----------|
| 1 | Document Control | Yes |
| 2 | Executive Summary | Yes |
| 3 | Problem Statement | Yes |
| 4 | Target Users | Yes |
| 5 | Success Metrics (KPIs) | Yes |
| 6 | Scope | Yes |
| 7 | User Stories (High-Level) | Yes |
| 8 | Functional Requirements (Essential) | Yes |
| 9 | Quality Attributes (Baseline) | Yes |
| 10 | Architecture Decision Requirements | Yes |
| 11 | Constraints & Assumptions | Yes |
| 12 | Risk Assessment (Top 5) | Yes |
| 13 | Implementation Approach | Yes |
| 14 | MVP Acceptance Criteria | Yes |
| 15 | Cost Estimate (Simplified) | Yes |
| 16 | Traceability | Yes |
| 17 | Glossary (MVP-Specific) | Yes |

**Validation Logic**:
```bash
# Standard template sections (21)
STANDARD_SECTIONS=(
  "Document Control" "Executive Summary" "Problem Statement"
  "Target Audience" "Success Metrics" "Goals & Objectives"
  "Scope & Requirements" "User Stories" "Functional Requirements"
  "Customer-Facing Content" "Acceptance Criteria" "Constraints"
  "Risk Assessment" "Success Definition" "Stakeholders"
  "Implementation Approach" "Budget & Resources" "Traceability"
  "References" "EARS Enhancement" "Quality Assurance"
)

# MVP template sections (17)
MVP_SECTIONS=(
  "Document Control" "Executive Summary" "Problem Statement"
  "Target Users" "Success Metrics" "Scope"
  "User Stories" "Functional Requirements" "Quality Attributes"
  "Architecture Decision" "Constraints" "Risk Assessment"
  "Implementation Approach" "MVP Acceptance" "Cost Estimate"
  "Traceability" "Glossary"
)

for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -qi "## .*$section\|# .*$section" "$f" 2>/dev/null; then
      echo "ERROR: $(basename $f) missing section: $section"
    fi
  done
done
```

---

### CORPUS-14: SYS-Ready Score Validation

**Purpose**: Validate each PRD includes SYS-Ready score for downstream layer readiness

**Severity**: Error (if score below template threshold)

**Score Thresholds**:
| Status | Score Range | Template | Allowed to Proceed |
|--------|-------------|----------|-------------------|
| Ready | >= 90 | Standard | Yes (to EARS) |
| MVP-Ready | >= 85 | MVP | Yes (to EARS) |
| Draft | 70-89 | Standard | No (refinement needed) |
| Draft | 70-84 | MVP | No (refinement needed) |
| Incomplete | < 70 | Any | No (major gaps) |

**Template Detection**:
- **MVP Template**: Check for `PRD-MVP-TEMPLATE` in document or `template_variant: MVP` in YAML
- **Standard Template**: Default if not MVP

**Validation Logic**:
```bash
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  score=$(grep -oP 'sys_ready_score:\s*\K[0-9]+' "$f" 2>/dev/null || echo "0")
  is_mvp=$(grep -qiE 'template_variant.*MVP|MVP.*template' "$f" && echo "true" || echo "false")

  if [[ "$is_mvp" == "true" ]]; then
    threshold=85
    template_type="MVP"
  else
    threshold=90
    template_type="Standard"
  fi

  if [[ $score -lt $threshold ]]; then
    echo "ERROR: $(basename $f) SYS-Ready score $score < $threshold ($template_type threshold)"
  fi
done
```

**Score Calculation**:
| Criterion | Weight | Max Points |
|-----------|--------|-----------|
| All sections complete | 20% | 20 |
| BRD traceability present | 15% | 15 |
| User stories defined | 20% | 20 |
| Acceptance criteria specific | 15% | 15 |
| Success metrics measurable | 15% | 15 |
| Risks documented | 15% | 15 |
| **Total** | **100%** | **100** |

---

### CORPUS-15: MVP Hypothesis Format

**Purpose**: Validate MVP hypothesis uses proper testable format

**Severity**: Warning

**Required Format**: "We believe that [feature] will [outcome] if we [measurement]"

**Validation Logic**:
```bash
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  if ! grep -qiE 'We believe that.*will.*if we' "$f" 2>/dev/null; then
    echo "WARNING: $(basename $f) may lack properly formatted MVP hypothesis"
  fi
done
```

**Good Examples**:
```markdown
We believe that implementing real-time price alerts will increase user engagement
if we see a 25% increase in daily active users within 30 days of launch.

We believe that the AI-powered trade suggestions will reduce analysis time
if we measure an average 40% reduction in time-to-decision metrics.
```

---

### CORPUS-16: Glossary Path Standardization

**Purpose**: Validate glossary references use standardized paths

**Severity**: Warning

**Standard Path**: `docs/glossary.md` or project-specific glossary in Document Control

**Validation Logic**:
```bash
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  # Check for glossary reference in Document Control table
  if grep -q "Glossary" "$f" 2>/dev/null; then
    if ! grep -qE 'glossary\.md|Glossary.*\|' "$f" 2>/dev/null; then
      echo "WARNING: $(basename $f) glossary path may not be standardized"
    fi
  fi
done
```

---

### CORPUS-17: Token Count Compliance

**Purpose**: Estimate token count to prevent AI tool processing limits

**Severity**: Warning at 40K tokens, Error at 80K tokens

**Estimation Formula**: `tokens ≈ words × 1.3`

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Words | ~31,000 | ~62,000 |
| Tokens | 40,000 | 80,000 |

**Validation Logic**:
```bash
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  words=$(wc -w < "$f")
  tokens=$((words * 13 / 10))

  if [[ $tokens -gt 80000 ]]; then
    echo "ERROR: $(basename $f) exceeds 80K tokens (~$tokens)"
  elif [[ $tokens -gt 40000 ]]; then
    echo "WARNING: $(basename $f) exceeds 40K tokens (~$tokens)"
  fi
done
```

---

### CORPUS-18: YAML Frontmatter Validation

**Purpose**: Validate required YAML frontmatter fields for metadata consistency

**Severity**: Warning

**Required Fields**:
| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Document title |
| `status` | Yes | Draft/Review/Approved |
| `version` | Yes | Semantic version |
| `created` | Yes | ISO date (YYYY-MM-DD) |
| `modified` | Yes | ISO date (YYYY-MM-DD) |
| `brd_refs` | Yes | Array of BRD references |
| `sys_ready_score` | Yes | Numeric 0-100 |

**Validation Logic**:
```bash
REQUIRED_FIELDS=("title" "status" "version" "created" "modified" "brd_refs" "sys_ready_score")

for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  # Check if file has YAML frontmatter
  if head -1 "$f" | grep -q "^---"; then
    for field in "${REQUIRED_FIELDS[@]}"; do
      if ! grep -q "^$field:" "$f" 2>/dev/null; then
        echo "WARNING: $(basename $f) missing YAML field: $field"
      fi
    done
  fi
done
```

---

### CORPUS-19: ISO Date Format Compliance

**Purpose**: Ensure all dates use ISO 8601 format (YYYY-MM-DD)

**Severity**: Warning

**Valid Format**: `2026-01-04`, `2026-12-31`

**Invalid Formats**:
| Format | Example | Issue |
|--------|---------|-------|
| US format | `01/04/2026` | Ambiguous |
| Written | `Jan 4, 2026` | Non-standard |
| European | `04/01/2026` | Ambiguous |
| Reversed | `04-01-2026` | Wrong order |

**Validation Logic**:
```bash
for f in "$PRD_DIR"/PRD-[0-9]*_*.md; do
  # Detect non-ISO date formats
  bad_dates=$(grep -oE '[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}|[A-Za-z]{3} [0-9]{1,2},? [0-9]{4}' "$f" 2>/dev/null | head -5)
  if [[ -n "$bad_dates" ]]; then
    echo "WARNING: $(basename $f) contains non-ISO dates: $bad_dates"
  fi
done
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text or prohibited content | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 3+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate element ID across corpus | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing BRD traceability tags | CORPUS-11 |
| CORPUS-E011a | Invalid @brd format (not 4-segment) | CORPUS-11 |
| CORPUS-E013 | Missing required template section | CORPUS-13 |
| CORPUS-E014 | SYS-Ready score < 85 (MVP threshold) | CORPUS-14 |
| CORPUS-E017 | Token count exceeds 80K | CORPUS-17 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Exact cost without range | CORPUS-09 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W012 | BRD objective without PRD user story | CORPUS-12 |
| CORPUS-W015 | MVP hypothesis format incorrect | CORPUS-15 |
| CORPUS-W016 | Glossary path not standardized | CORPUS-16 |
| CORPUS-W017 | Token count exceeds 40K | CORPUS-17 |
| CORPUS-W018 | Missing YAML frontmatter field | CORPUS-18 |
| CORPUS-W019 | Non-ISO date format detected | CORPUS-19 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

### Error Reference: Remediation

| Code | Remediation |
|------|-------------|
| CORPUS-E001 | Remove placeholder text or replace with actual content/links |
| CORPUS-E002 | Replace numbered downstream refs with generic descriptions |
| CORPUS-E003 | Run `./scripts/sync_prd_index.sh` or update index manually |
| CORPUS-E004 | Rename duplicate IDs to unique values |
| CORPUS-E011 | Add @brd tags in Traceability section |
| CORPUS-E011a | Change `@brd: BRD-07` to `@brd: BRD.07.TT.SS` format |
| CORPUS-E013 | Add missing section from PRD-MVP-TEMPLATE.md |
| CORPUS-E014 | Improve PRD quality until sys_ready_score >= 85 |
| CORPUS-W015 | Add hypothesis: "We believe that [X] will [Y] if we [Z]" |
| CORPUS-W018 | Add YAML frontmatter with required fields |
| CORPUS-W019 | Convert dates to YYYY-MM-DD format |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_prd_corpus.sh docs/PRD

# With verbose output
./scripts/validate_prd_corpus.sh docs/PRD --verbose

# Check specific category
./scripts/validate_prd_corpus.sh docs/PRD --check=traceability
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Errors found (blocking) |
| 2 | Warnings found (non-blocking) |
| 3 | Script error |

---

## 4. Validation Checklist

### Pre-EARS Gate Checklist

- [ ] **CORPUS-01**: No placeholder text or prohibited content
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Bidirectional index completeness verified
- [x] **CORPUS-05**: ~~Inter-PRD cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex concepts
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Cost estimates use ranges
- [ ] **CORPUS-10**: All files under size limits (lines)
- [ ] **CORPUS-11**: All PRDs have @brd tags (4-segment format)
- [ ] **CORPUS-12**: BRD objectives have PRD user stories
- [ ] **CORPUS-13**: Required template sections present (21 Standard / 17 MVP)
- [ ] **CORPUS-14**: SYS-Ready score meets template threshold (≥90% Standard / ≥85% MVP)
- [ ] **CORPUS-15**: MVP hypothesis format validated
- [ ] **CORPUS-16**: Glossary paths standardized
- [ ] **CORPUS-17**: Token count within limits
- [ ] **CORPUS-18**: YAML frontmatter fields present
- [ ] **CORPUS-19**: ISO date format compliance

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-prd-corpus.yml
name: PRD Corpus Validation

on:
  push:
    paths:
      - 'docs/02_PRD/**/*.md'
  pull_request:
    paths:
      - 'docs/02_PRD/**/*.md'
  workflow_dispatch:  # Manual trigger

jobs:
  validate-prd:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Make validation script executable
        run: chmod +x ./scripts/validate_prd_corpus.sh

      - name: Run PRD Corpus Validation
        id: validation
        run: |
          ./scripts/validate_prd_corpus.sh docs/PRD --verbose 2>&1 | tee validation_output.txt
          exit_code=${PIPESTATUS[0]}
          echo "exit_code=$exit_code" >> $GITHUB_OUTPUT
        continue-on-error: true

      - name: Upload Validation Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: prd-validation-report
          path: validation_output.txt

      - name: Comment on PR
        if: github.event_name == 'pull_request' && steps.validation.outputs.exit_code != '0'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('validation_output.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## PRD Corpus Validation Failed\n\n```\n' + output.substring(0, 60000) + '\n```'
            });

      - name: Fail if validation errors
        if: steps.validation.outputs.exit_code == '1'
        run: exit 1
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run PRD corpus validation if PRD files changed
if git diff --cached --name-only | grep -q "docs/02_PRD/"; then
  echo "PRD files changed, running corpus validation..."
  ./scripts/validate_prd_corpus.sh docs/PRD

  if [ $? -ne 0 ]; then
    echo "PRD corpus validation failed. Fix errors before committing."
    exit 1
  fi
fi
```

---

## References

- [PRD_VALIDATION_RULES.md](./PRD_VALIDATION_RULES.md) - Individual file validation
- [PRD-MVP-TEMPLATE.md](./PRD-MVP-TEMPLATE.md) - PRD document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
