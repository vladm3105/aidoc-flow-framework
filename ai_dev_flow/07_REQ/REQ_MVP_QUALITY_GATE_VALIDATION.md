---
title: "REQ Quality Gate Validation"
tags:
  - quality-gate-validation
  - layer-7-artifact
  - shared-architecture
custom_fields:
  document_type: quality-gate-validation
  artifact_type: REQ
  layer: 7
  priority: shared
  development_status: active
---

# REQ Quality Gate Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | REQ_QUALITY_GATE_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete REQ corpus |
| Trigger | Run after ALL REQ files are complete |
| Scope | Entire REQ Quality Gate validation |
| Layer | Layer 7 → Layer 8/9 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all REQ (Atomic Requirements) files are created but BEFORE CTR or SPEC creation begins. These rules validate the entire REQ corpus as a cohesive set, checking for cross-document consistency, domain coverage, and quality standards that cannot be verified at the individual file level.

**Consistency Note**: All MVP artifacts (creation rules, validation rules, quality gates, schema) MUST stay consistent with `REQ-MVP-TEMPLATE.md` and `REQ-MVP-TEMPLATE.yaml`; keep changes synchronized.

### Cross-Linking Tags

REQ documents may include same-layer cross-links for clarity and AI ranking:
- `@depends: REQ-NN` — prerequisite REQs that must be satisfied first.
- `@discoverability: REQ-NN (short rationale); REQ-NN (short rationale)` — related REQs with brief reasons to aid search.

Legacy "See also …" strings are deprecated. Corpus validation may report presence of these tags for visibility (informational only).

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual REQ Validation** | After each REQ creation | Single file | `REQ_MVP_VALIDATION_RULES.md` |
| **Quality Gate Validation** | After ALL REQ complete | Entire REQ set | This document |

### Workflow Position

```
Individual REQ Creation → REQ_MVP_VALIDATION_RULES.md (per-file)
        ↓
All REQ Complete
        ↓
REQ_MVP_QUALITY_GATE_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin CTR (Layer 8) or SPEC (Layer 9)
FAIL → Fix issues, re-run Quality Gate validation
```

### REQ Directory Structure

REQ uses domain-based subdirectories:
```
docs/07_REQ/
├── REQ-000_index.md
├── api/
│   └── REQ-01_api_authentication.md
├── auth/
├── core/
├── data/
├── risk/
├── trading/
├── collection/
├── compliance/
└── ml/
```

---

## 1. Quality Gate Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking SPEC creation)

**Important**: The validation script uses `grep -F` (fixed string matching) to match these patterns LITERALLY. Parentheses and brackets are matched as actual characters, not regex operators.

**Patterns to Detect** (matched LITERALLY):
| Pattern | Description |
|---------|-------------|
| `(future REQ)` | REQ-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |
| `[TBD]` | Generic placeholder in brackets |
| `[TODO]` | Task marker that should be resolved |

**What This Check Does NOT Flag** (expected patterns):

| Pattern | Location | Why It's Valid |
|---------|----------|----------------|
| `TBD` (unbracketed) | Downstream reference tables | SPEC/TASKS don't exist during REQ phase |
| `\| SPEC-NN \| TBD \|` | Traceability tables | Downstream artifacts are created later |
| `\| TASKS-NN \| TBD \|` | Traceability tables | Layer 10 doesn't exist at Layer 7 |

**Rationale**: REQ documents (Layer 7) legitimately contain "TBD" in downstream reference tables because SPEC (Layer 9) and TASKS (Layer 10) documents don't exist yet during REQ creation. The validation only flags bracketed placeholders like `(TBD)` or `[TBD]` which indicate incomplete content within the current document.

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 8+ artifacts

**Severity**: Error (blocking)

**Rationale**: REQ is Layer 7. It should NOT reference specific numbered CTR, SPEC, or TASKS documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `CTR-NN` | 8 | CTR don't exist during REQ creation |
| `SPEC-NN` | 9 | SPECs don't exist during REQ creation |
| `TASKS-NN` | 10 | TASKS don't exist during REQ creation |

**Allowed Patterns** (generic references):
- "This will inform SPEC development"
- "Downstream implementation will..."
- "See future TASKS for details"

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 acceptance criteria" | 6 listed | Count mismatch |
| "3 dependencies" | 4 enumerated | Count mismatch |
| "7 verification methods" | 8 described | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify REQ index file reflects actual file states

**Severity**: Error

**Index File Pattern**: `REQ-*_index.md` (e.g., `REQ-000_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing REQ files listed in index |
| Domain accuracy | Subdirectory matches domain classification |
| Version currency | Version numbers match file headers |

---

### CORPUS-05: Unit Tests Coverage ⭐ NEW

**Purpose**: Verify all REQ files contain Section 8.1 Unit Tests tables

**Severity**: Warning

**Rationale**: Unit Tests drive SPEC interface design. REQs without TDD tables may produce incomplete SPECs.

**Checks**:
| Check | Description |
|-------|-------------|
| Section 8.1 exists | Must be titled "Unit Tests" |
| Minimum 3 entries | At least 3 test cases per REQ |
| Category prefixes | `[Logic]`, `[State]`, `[Validation]`, `[Edge]` |

**Aggregate Metrics**:
- Target: 100% of REQ files have Section 8.1
- Warning: <90% coverage
- Error: <70% coverage

**Reference**: TESTING_STRATEGY_TDD.md (Unit Tests Phase)

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex requirements

**Severity**: Info

**Recommended Diagrams by REQ Type**:
| REQ Type | Recommended Diagrams |
|----------|---------------------|
| Data flow requirements | Data flow diagram |
| State requirements | State machine diagram |
| Integration requirements | Sequence diagram |
| Algorithm requirements | Flowchart |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all REQ files

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Term consistency | Same term used same way across docs |
| Acronym expansion | Acronyms expanded on first use per doc |
| No conflicting definitions | Same concept not defined differently |

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the REQ corpus

**Severity**: Error

**Element ID Format**: `REQ.NN.TT.SS`
- NN = Document number
- TT = Element type code
- SS = Sequence number

**Note**: REQ files are distributed across subdirectories but share a global ID namespace.

**Validation Logic**:
```bash
# Check for duplicate element IDs across all subdirectories
find "$REQ_DIR" -name "REQ-*.md" -exec grep -ohE "REQ\.[0-9]+\.[0-9]+\.[0-9]+" {} \; | \
  sort | uniq -d
```

---

### CORPUS-09: Priority Distribution

**Purpose**: Validate priority distribution across requirements

**Severity**: Warning

**Expected Distribution**:
| Priority | Expected Range |
|----------|----------------|
| MUST | 60-80% |
| SHOULD | 15-30% |
| MAY | 5-15% |

**Anti-patterns**:
- 100% MUST (over-prioritization)
- No MUST requirements (under-prioritization)
- No MAY requirements (missing optional features)

---

### CORPUS-10: File Size Compliance (Universal Splitting Rule)

**Purpose**: Enforce Nested Directory Pattern when triggers are met.

**Severity**: **Error (blocking)** at 20,000 tokens

**Triggers**:
1. **Size**: File > 20,000 tokens.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `07_REQ/REQ-{PRD_ID}_{Slug}/` folder.

**Error Message**: `❌ ERROR: REQ-NN triggers nested folder rule (>20,000 tokens or >1 file). Move to 07_REQ/REQ-NN_{Slug}/`

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 500 | 1,000 |
| Tokens | 50,000 | — |

---

### CORPUS-11: Cumulative Traceability (@brd + @prd + @ears + @bdd + @adr + @sys)

**Purpose**: Verify all REQ have cumulative upstream traceability

**Severity**: Error

**Required Tags**: Each REQ must include all six:
- `@brd:` tag linking to source BRD element
- `@prd:` tag linking to source PRD element
- `@ears:` tag linking to source EARS element
- `@bdd:` tag linking to source BDD element
- `@adr:` tag linking to source ADR document
- `@sys:` tag linking to source SYS element

**Validation Logic**:
```bash
# Check each REQ has cumulative traceability
find "$REQ_DIR" -name "REQ-[0-9]*_*.md" | while read f; do
  if [[ "$(basename $f)" =~ _index ]]; then continue; fi

  diagram_count=$(grep -c '```mermaid' "$f" 2>/dev/null || true)
  has_brd=$(grep -c "@brd:" "$f" 2>/dev/null || true)
  has_prd=$(grep -c "@prd:" "$f" 2>/dev/null || true)
  has_ears=$(grep -c "@ears:" "$f" 2>/dev/null || true)
  has_bdd=$(grep -c "@bdd:" "$f" 2>/dev/null || true)
  has_adr=$(grep -c "@adr:" "$f" 2>/dev/null || true)
  has_sys=$(grep -c "@sys:" "$f" 2>/dev/null || true)

  if [[ $has_brd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @brd traceability tag"
  fi
  # ... repeat for other tags
done
```

---

### CORPUS-12: MVP 11-Section Format Compliance

**Purpose**: Verify all REQ follow the MVP 11-section format (no Change History)

**Severity**: Error

**Required Sections (MVP)**:
| # | Section | Required |
|---|---------|----------|
| 1 | Document Control | Yes |
| 2 | Requirement Description | Yes |
| 3 | Functional Specification | Yes |
| 4 | Interface Definition | Yes |
| 5 | Error Handling | Yes |
| 6 | Quality Attributes | Yes |
| 7 | Configuration | Yes |
| 8 | Testing Requirements | Yes |
| 9 | Acceptance Criteria | Yes |
| 10 | Traceability | Yes |
| 11 | Implementation Notes | Yes |

**Validation Logic**:
```bash
# Check for required sections (MVP 11-section format)
required_sections=("Document Control" "Requirement Description" "Functional Specification" "Interface Definition"
                   "Error Handling" "Quality Attributes" "Configuration" "Testing Requirements"
                   "Acceptance Criteria" "Traceability" "Implementation Notes")
for f in $(find "$REQ_DIR" -name "REQ-[0-9]*_*.md"); do
  for section in "${required_sections[@]}"; do
    if ! grep -qE "^#+.*$section" "$f"; then
      echo "ERROR: $(basename $f) missing '$section' section"
    fi
  done
done
```

---

### CORPUS-13: Domain Subdirectory Classification

**Purpose**: Verify REQ files are in correct domain subdirectories

**Severity**: Warning

**Valid Domains**:
| Domain | Description |
|--------|-------------|
| api | API and endpoint requirements |
| auth | Authentication and authorization |
| core | Core business logic |
| data | Data management and persistence |
| risk | Risk management and controls |
| trading | Trading operations |
| collection | Data collection and ingestion |
| compliance | Regulatory compliance |
| ml | Machine learning and AI |

**Checks**:
| Check | Description |
|-------|-------------|
| Valid subdirectory | File is in recognized domain folder |
| Domain consistency | File content matches subdirectory domain |
| No orphaned files | All REQ files are in subdirectories |

---

### CORPUS-14: SPEC-Readiness Scoring

**Purpose**: Verify SPEC-Ready scores are present and meet threshold

**Severity**: Warning

**Threshold**: All REQ files should have SPEC-Ready Score ≥90%

**Validation Logic**:
```bash
# Check SPEC-Ready scores
find "$REQ_DIR" -name "REQ-[0-9]*_*.md" | while read f; do
  if [[ "$(basename $f)" =~ _index ]]; then continue; fi
  score=$(grep -oE "SPEC-Ready Score[^0-9]*[0-9]+" "$f" | grep -oE "[0-9]+" | head -1)
  if [[ -z "$score" ]]; then
    echo "WARNING: $(basename $f) missing SPEC-Ready Score"
  elif [[ $score -lt 90 ]]; then
    echo "WARNING: $(basename $f) has SPEC-Ready Score $score% (target: ≥90%)"
  fi
done
```

---

### CORPUS-15: CTR-Readiness Scoring

**Purpose**: Verify CTR-Ready scores are present for interface-relevant requirements

**Severity**: Info

**Threshold**: CTR-Ready Score ≥85% recommended

---

### CORPUS-16: Acceptance Criteria Coverage

**Purpose**: Verify all REQ have adequate acceptance criteria

**Severity**: Warning

**Minimum Requirements**:
| Priority | Minimum AC Count |
|----------|------------------|
| MUST | 3 acceptance criteria |
| SHOULD | 2 acceptance criteria |
| MAY | 1 acceptance criteria |

---

### CORPUS-17: YAML Frontmatter Compliance

**Purpose**: Verify required custom_fields are present in YAML frontmatter

**Severity**: Error

**Required Fields**:
| Field | Value | Required |
|-------|-------|----------|
| `artifact_type` | `REQ` | Yes |
| `layer` | `7` | Yes |
| `upstream_sys` | `SYS-NN` | Yes |
| `spec_ready_score` | `NN%` | Yes |
| `ctr_ready_score` | `NN%` | No |

**Validation Logic**:
```bash
find "$REQ_DIR" -name "REQ-[0-9]*_*.md" | while read f; do
  ! grep -q "artifact_type: REQ" "$f" && echo "ERROR: Missing artifact_type: $f"
  ! grep -q "layer: 7" "$f" && echo "ERROR: Missing layer: $f"
  ! grep -q "upstream_sys:" "$f" && echo "ERROR: Missing upstream_sys: $f"
done
```

---

### CORPUS-18: Tag Notation Consistency

**Purpose**: Validate correct notation (dot vs dash) for traceability tags

**Severity**: Error

**Tag Notation Rules**:
| Tag Type | Required Notation | Example | Rationale |
|----------|-------------------|---------|-----------|
| `@brd` | Dot (element-level) | `BRD.07.01.01` | References specific element |
| `@prd` | Dot (element-level) | `PRD.03.02.01` | References specific element |
| `@ears` | Dot (element-level) | `EARS.05.01.01` | References specific element |
| `@bdd` | Dot (element-level) | `BDD.02.01.01` | References specific element |
| `@sys` | Dot (element-level) | `SYS.07.01.01` | References specific element |
| `@req` | Dot (element-level) | `REQ.01.01.01` | References specific element |
| `@adr` | Dash (document-level) | `ADR-33` | References whole document |
| `@spec` | Dash (document-level) | `SPEC-07` | References whole document |

**Validation Logic**:
```bash
grep -rn "@brd:" "$REQ_DIR"/*.md | grep "BRD-" && echo "ERROR: @brd should use dot notation"
grep -rn "@adr:" "$REQ_DIR"/*.md | grep "ADR\." && echo "ERROR: @adr should use dash notation"
```

---

### CORPUS-19: Date Format Consistency

**Purpose**: Verify all dates use ISO 8601 format

**Severity**: Error

**Required Format**: `YYYY-MM-DD` (e.g., `2026-01-05`)

**Invalid Formats**:
| Pattern | Example | Issue |
|---------|---------|-------|
| `MM/DD/YYYY` | `01/05/2026` | US format ambiguous |
| `DD/MM/YYYY` | `05/01/2026` | EU format ambiguous |
| `Month D, YYYY` | `January 5, 2026` | Verbose, inconsistent |

**Validation Logic**:
```bash
grep -rE "[0-9]{2}/[0-9]{2}/[0-9]{4}" "$REQ_DIR"/*.md && echo "ERROR: Invalid date format"
```

---

### CORPUS-20: ASCII Art Detection

**Purpose**: Detect box drawing characters in non-index files

**Severity**: Warning

**Exempt Files**: `*_index.md` (directory structure visualization allowed)

**Characters to Detect**: `┌┐└┘─│├┤┬┴┼`

**Validation Logic**:
```bash
find "$REQ_DIR" -name "REQ-[0-9]*_*.md" ! -name "*_index.md" | while read f; do
  if grep -qE "┌|┐|└|┘|─|│|├|┤|┬|┴|┼" "$f"; then
    echo "WARNING: $(basename $f) contains box drawing characters"
  fi
done
```

---

### CORPUS-21: custom_fields Key Naming Consistency

**Purpose**: Enforce consistent key naming in custom_fields YAML section

**Severity**: Error

**Key Naming Rules**:
| Correct Key | Incorrect Key | Description |
|-------------|---------------|-------------|
| `upstream_sys` | `sys_source` | Source SYS document |
| `spec_ready_score` | `specReadyScore` | Use snake_case |
| `impl_ready_score` | `implReadyScore` | Use snake_case |

**Validation Logic**:
```bash
find "$REQ_DIR" -name "REQ-[0-9]*_*.md" | while read f; do
  grep -q "sys_source:" "$f" && echo "ERROR: $f uses 'sys_source' instead of 'upstream_sys'"
done
```

---

### CORPUS-22: Upstream TBD References

**Purpose**: Detect TBD placeholders in upstream traceability references

**Severity**: Error (blocking SPEC creation)

**Rationale**: Upstream documents (BRD, PRD, EARS, BDD, ADR, SYS) from Layers 1-6 must exist BEFORE REQ (Layer 7) creation. TBD is not acceptable for upstream references.

**Important**: This is different from **downstream** TBD references (SPEC, TASKS) which ARE expected because those documents are created AFTER REQ.

**Upstream vs Downstream TBD**:
| Direction | Documents | TBD Allowed? | Reason |
|-----------|-----------|--------------|--------|
| **Upstream** | BRD, PRD, EARS, BDD, ADR, SYS | ✗ No | Must exist before REQ |
| **Downstream** | SPEC, TASKS, CTR | ✓ Yes | Created after REQ |

**Patterns Flagged**:
| Pattern | Error |
|---------|-------|
| `@brd: TBD` | Upstream BRD reference is TBD |
| `@prd: TBD` | Upstream PRD reference is TBD |
| `@ears: TBD` | Upstream EARS reference is TBD |
| `@bdd: TBD` | Upstream BDD reference is TBD |
| `@adr: TBD` | Upstream ADR reference is TBD |
| `@sys: TBD` | Upstream SYS reference is TBD |

**Validation Logic**:
```bash
# Check for TBD in upstream traceability tags
for tag in "@brd:" "@prd:" "@ears:" "@bdd:" "@adr:" "@sys:"; do
  grep -rE "${tag}\s*(TBD|\(TBD\)|\[TBD\])" "$REQ_DIR"/*.md
done
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 8+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate element ID across corpus | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing @brd traceability tag | CORPUS-11 |
| CORPUS-E012 | Missing @prd traceability tag | CORPUS-11 |
| CORPUS-E013 | Missing @ears traceability tag | CORPUS-11 |
| CORPUS-E014 | Missing @bdd traceability tag | CORPUS-11 |
| CORPUS-E015 | Missing @adr traceability tag | CORPUS-11 |
| CORPUS-E016 | Missing @sys traceability tag | CORPUS-11 |
| CORPUS-E017 | Missing required section (MVP 11-section format) | CORPUS-12 |
| CORPUS-E018 | Missing required YAML frontmatter field | CORPUS-17 |
| CORPUS-E019 | Wrong tag notation (dot vs dash) | CORPUS-18 |
| CORPUS-E020 | Invalid date format | CORPUS-19 |
| CORPUS-E021 | Invalid custom_fields key name | CORPUS-21 |
| CORPUS-E022 | TBD in upstream traceability reference | CORPUS-22 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W009 | Priority distribution imbalance | CORPUS-09 |
| CORPUS-W013 | Invalid domain subdirectory | CORPUS-13 |
| CORPUS-W014 | SPEC-Ready Score below 90% | CORPUS-14 |
| CORPUS-W016 | Insufficient acceptance criteria | CORPUS-16 |
| CORPUS-W017 | ASCII art in non-index file | CORPUS-20 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |
| CORPUS-I015 | CTR-Ready Score below 85% | CORPUS-15 |

---

## 3. Automated Script Usage

### Running Quality Gate Validation

```bash
# Full Quality Gate validation
./scripts/validate_req_corpus.sh docs/REQ

# With verbose output
./scripts/validate_req_corpus.sh docs/REQ --verbose

# Check specific category
./scripts/validate_req_corpus.sh docs/REQ --check=traceability
```

### Script Implementation Notes

**CORPUS-01 Pattern Matching**: The validation script uses `grep -F` (fixed string matching) instead of regex to prevent false positives. This ensures:

- `(TBD)` matches only the literal string `(TBD)`, not just `TBD`
- `[TODO]` matches only the literal string `[TODO]`, not a character class
- Parentheses and brackets are not interpreted as regex operators

**Why This Matters**: Without `-F`, patterns like `(pending)` would match any occurrence of "pending" because parentheses are regex grouping operators. The fixed string matching ensures accurate detection of actual placeholder markers.

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | Errors found (blocking) |
| 2 | Warnings found (non-blocking) |
| 3 | Script error |

---

## 4. Validation Checklist

### Pre-SPEC Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-REQ cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex requirements
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Priority distribution is balanced
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All REQ have cumulative traceability (6 tags)
- [ ] **CORPUS-12**: All REQ follow MVP 11-section format (no Change History)
- [ ] **CORPUS-13**: All REQ in valid domain subdirectories
- [ ] **CORPUS-14**: All REQ have SPEC-Ready Score ≥90%
- [ ] **CORPUS-15**: CTR-Ready scores present
- [ ] **CORPUS-16**: Adequate acceptance criteria coverage
- [ ] **CORPUS-17**: Required YAML frontmatter fields present
- [ ] **CORPUS-18**: Tag notation consistent (dot vs dash)
- [ ] **CORPUS-19**: All dates use ISO 8601 format
- [ ] **CORPUS-20**: No ASCII art in non-index files
- [ ] **CORPUS-21**: custom_fields keys use correct naming
- [ ] **CORPUS-22**: No TBD in upstream traceability references

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-req-corpus.yml
name: REQ Quality Gate Validation

on:
  push:
    paths:
      - 'docs/07_REQ/**/*.md'
  pull_request:
    paths:
      - 'docs/07_REQ/**/*.md'

jobs:
  validate-req-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate REQ Corpus
        run: |
          chmod +x ./scripts/validate_req_corpus.sh
          ./scripts/validate_req_corpus.sh docs/REQ
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: req-validation-report
          path: tmp/req_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# REQ Quality Gate validation on staged REQ files
if git diff --cached --name-only | grep -q "^docs/07_REQ/"; then
  echo "Running REQ Quality Gate validation..."
  ./scripts/validate_req_corpus.sh docs/REQ --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ REQ Quality Gate validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ REQ Quality Gate validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-req:
	@echo "Validating REQ corpus..."
	@./scripts/validate_req_corpus.sh docs/REQ

validate-req-verbose:
	@./scripts/validate_req_corpus.sh docs/REQ --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req validate-spec validate-tasks
	@echo "All Quality Gate validations complete"
```

### Integration with SPEC Layer Gate

REQ Quality Gate validation should pass before creating SPEC documents:

```bash
# Pre-SPEC gate check
./scripts/validate_req_corpus.sh docs/REQ
if [ $? -eq 0 ]; then
  echo "✓ REQ corpus valid - ready for SPEC layer creation"
else
  echo "❌ Fix REQ corpus errors before proceeding to SPEC layer"
  exit 1
fi
```

---

## 6. Fix Priority Classification

### Priority 1: Blocking (Must Fix Before Layer Transition)

- Placeholder text for existing documents (CORPUS-01)
- Premature downstream references (CORPUS-02)
- Index synchronization errors (CORPUS-04)
- Duplicate element IDs (CORPUS-08)
- Missing cumulative traceability tags (CORPUS-11)
- Missing required sections (CORPUS-12)
- YAML frontmatter issues (CORPUS-17)
- Tag notation errors (CORPUS-18)
- Invalid date formats (CORPUS-19)
- custom_fields key naming (CORPUS-21)
- Upstream TBD references (CORPUS-22)

### Priority 2: Quality (Recommended Before Approval)

- Internal count mismatches (CORPUS-03)
- Missing diagrams (CORPUS-06)
- Terminology inconsistencies (CORPUS-07)
- Priority distribution imbalance (CORPUS-09)
- File size warnings (CORPUS-10)
- Invalid domain subdirectory (CORPUS-13)
- Acceptance criteria coverage (CORPUS-16)
- ASCII art in non-index files (CORPUS-20)

### Priority 3: Continuous (Address During Maintenance)

- SPEC-Ready Score below 90% (CORPUS-14)
- CTR-Ready Score below 85% (CORPUS-15)

---


## References

- [REQ_MVP_VALIDATION_RULES.md](./REQ_MVP_VALIDATION_RULES.md) - Individual file validation
- [REQ-MVP-TEMPLATE.md](./REQ-MVP-TEMPLATE.md) - REQ document template (full template archived)
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
