---
title: "EARS Corpus Validation"
tags:
  - corpus-validation
  - layer-3-artifact
  - shared-architecture
custom_fields:
  document_type: corpus-validation
  artifact_type: EARS
  layer: 3
  priority: shared
  development_status: active
---

# EARS Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | EARS_CORPUS_VALIDATION |
| Version | 1.1 |
| Created | 2026-01-04 |
| Last Updated | 2026-01-04 |
| Purpose | Quality gate for complete EARS corpus |
| Trigger | Run after ALL EARS are complete |
| Scope | Entire EARS corpus validation |
| Layer | Layer 3 → Layer 4 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all EARS files are created but BEFORE BDD creation begins. These rules validate the entire EARS corpus as a cohesive set, checking for cross-document consistency, reference integrity, and quality standards that cannot be verified at the individual file level.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual EARS Validation** | After each EARS creation | Single file | `EARS_MVP_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL EARS complete | Entire EARS set | This document |

### Workflow Position

```
Individual EARS Creation → EARS_MVP_VALIDATION_RULES.md (per-file)
        ↓
All EARS Complete
        ↓
EARS_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin BDD Creation (Layer 4)
FAIL → Fix issues, re-run corpus validation
```

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking BDD creation)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future EARS)` | EARS-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

**Validation Logic**:
```bash
# For each EARS reference in placeholder format, check if file exists
for placeholder in $(grep -rohE "EARS-[0-9]+ \(future" "$EARS_DIR"); do
  ears_num=$(echo "$placeholder" | grep -oE "EARS-[0-9]+")
  if ls "$EARS_DIR/${ears_num}_"*.md 2>/dev/null; then
    echo "ERROR: $ears_num exists but marked as future"
  fi
done
```

**Fix**: Replace placeholder with actual hyperlink reference:
```markdown
# Before
See EARS-03 (future EARS) for authentication requirements.

# After
See [EARS-03: Authentication](./EARS-03_authentication.md) for details.
```

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 4+ artifacts

**Severity**: Error (blocking)

**Rationale**: EARS is Layer 3. It should NOT reference specific numbered BDD, ADR, SYS, REQ, SPEC, or TASKS documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `BDD-NN` | 4 | BDD don't exist during EARS creation |
| `ADR-NN` | 5 | ADRs don't exist during EARS creation |
| `SYS-NN` | 6 | SYS don't exist during EARS creation |
| `REQ-NN` | 7 | REQs don't exist during EARS creation |
| `SPEC-NN` | 10 | SPECs don't exist during EARS creation |
| `TASKS-NN` | 11 | TASKS don't exist during EARS creation |

**Allowed Patterns** (generic references):
- "This will inform BDD development"
- "Downstream ADR artifacts will..."
- "See future SPEC for technical details"

**Validation Logic**:
```bash
# Flag specific numbered references to downstream artifacts
grep -rnE "(BDD|ADR|SYS|REQ|SPEC|TASKS)-[0-9]{2,}" "$EARS_DIR" | \
  grep -v "Layer [0-9]" | \
  grep -v "SDD workflow"
```

**Fix**: Use generic names or topic descriptions:
```markdown
# Before (ERROR)
See BDD-03 for detailed test scenarios.

# After (CORRECT)
Test scenarios will be documented in the BDD layer.
```

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 EARS requirements" | 6 requirements listed | Count mismatch |
| "3 event-driven requirements" | 4 enumerated | Count mismatch |
| "7 state-driven requirements" | 8 described | Count mismatch |

**Validation Logic**:
```bash
# Extract claimed counts and compare with actual items
grep -nE "[0-9]+ requirement|[0-9]+ EARS" "$file" | while read claim; do
  count=$(echo "$claim" | grep -oE "[0-9]+")
  # Count actual items in document
  # Manual verification recommended
done
```

**Fix**: Reconcile counts with actual items.

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify EARS index file reflects actual file states

**Severity**: Error

**Index File Pattern**: `EARS-*_index.md` (e.g., `EARS-00_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing EARS files listed in index |
| Version currency | Version numbers match file headers |
| Status accuracy | Status matches actual file content |

**Validation Logic**:
```bash
# Find index file using glob pattern
for f in "$EARS_DIR"/EARS-*_index.md; do
  if [[ -f "$f" ]]; then
    index_file="$f"
    break
  fi
done

# Check for files marked "Planned" that exist
grep -E "\| Planned \|" "$index_file" | while read line; do
  ears=$(echo "$line" | grep -oE "EARS-[0-9]+")
  if ls "$EARS_DIR/${ears}_"*.md 2>/dev/null; then
    echo "ERROR: $ears exists but marked Planned in index"
  fi
done
```

**Fix**: Update index to match reality.

---

### CORPUS-05: Inter-EARS Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Purpose**: ~~Ensure navigation links between related EARS~~

**Reason for Deprecation**: Per SDD traceability rules, document name references (e.g., `EARS-01`, `EARS-03`) are valid and sufficient for traceability. Hyperlinks are optional enhancements, not requirements.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex requirements

**Severity**: Info

**Recommended Diagrams by EARS Type**:
| EARS Type | Recommended Diagrams |
|----------|---------------------|
| Event-Driven | State diagram, event flow |
| State-Driven | State machine diagram |
| Constraint-Based | Constraint visualization |
| Optional Features | Feature toggle diagram |

**Validation Logic**:
```bash
# Check for Mermaid code blocks
for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
  diagram_count=$(grep -c '```mermaid' "$f" || true)
  if [ "$diagram_count" -eq 0 ]; then
    echo "INFO: $(basename $f) has no Mermaid diagrams"
  fi
done
```

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all EARS

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
| SHALL variants | "SHALL" vs "shall" vs "MUST" |
| WHEN/WITHIN | "WHEN" vs "When" |
| System naming | "the system" vs "System" |

**Validation Logic**:
```bash
# Check for term variations
declare -A term_variations
term_variations["SHALL"]="shall|MUST|must"
term_variations["WHEN"]="when|WHENEVER"

for term in "${!term_variations[@]}"; do
  # Check for inconsistent usage
done
```

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the EARS corpus

**Severity**: Error

**Element ID Format**: `EARS.NN.TT.SS`
- NN = Document number
- TT = Element type code (25 = EARS statement)
- SS = Sequence number

**Validation Logic**:
```bash
# Extract all element IDs and find duplicates
grep -rohE "EARS\.[0-9]+\.[0-9]+\.[0-9]+" "$EARS_DIR" | \
  sort | uniq -d | while read dup; do
    echo "ERROR: Duplicate element ID: $dup"
  done
```

---

### CORPUS-09: Timing Constraint Format

**Purpose**: Validate WITHIN clauses have measurable timing constraints

**Severity**: Warning

**Good Formats**:
| Format | Example | Status |
|--------|---------|--------|
| With threshold ref | `WITHIN 500ms (@threshold: PRD.035.api.response)` | Correct |
| Explicit timing | `WITHIN 2 seconds` | Correct |
| Range format | `WITHIN 100-200ms` | Correct |

**Bad Formats**:
| Format | Example | Issue |
|--------|---------|-------|
| Vague | `WITHIN a reasonable time` | Not measurable |
| Missing | No WITHIN clause | Incomplete |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 600 | 1,200 |
| Tokens | 50,000 | 100,000 |

---

### CORPUS-11: WHEN-THE-SHALL-WITHIN Syntax Compliance

**Purpose**: Verify all EARS requirements use proper EARS syntax patterns

**Severity**: Error

**Required Patterns**:
| Pattern | Required Elements |
|---------|-------------------|
| Event-Driven | WHEN, THE, SHALL, WITHIN |
| State-Driven | WHILE, THE, SHALL |
| Ubiquitous | THE, SHALL (always true) |
| Optional Feature | WHERE, THE, SHALL |
| Unwanted Behavior | IF, THEN, SHALL NOT |

**Validation Logic**:
```bash
# Check for EARS syntax patterns
for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
  # Count requirements with proper syntax
  shall_count=$(grep -cE "SHALL " "$f" || echo 0)
  when_count=$(grep -cE "^WHEN |WHEN \[" "$f" || echo 0)

  if [[ $shall_count -eq 0 ]]; then
    echo "ERROR: $(basename $f) has no SHALL statements"
  fi
done
```

**Fix**: Ensure all requirements use EARS syntax:
```markdown
# Before (ERROR)
The system must validate user input and respond quickly.

# After (CORRECT)
WHEN the user submits input,
THE system SHALL validate all fields
WITHIN 200ms (@threshold: PRD.035.validation.time).
```

---

### CORPUS-12: Cumulative Traceability (@brd + @prd)

**Purpose**: Verify all EARS have cumulative upstream traceability

**Severity**: Error

**Required Tags**: Each EARS must include both:
- `@brd:` tag linking to source BRD element
- `@prd:` tag linking to source PRD element

**Validation Logic**:
```bash
# Check each EARS has cumulative traceability
for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
  if [[ "$(basename $f)" =~ _index ]]; then continue; fi

  has_brd=$(grep -c "@brd:" "$f" 2>/dev/null || echo 0)
  has_prd=$(grep -c "@prd:" "$f" 2>/dev/null || echo 0)

  if [[ $has_brd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @brd traceability tag"
  fi
  if [[ $has_prd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @prd traceability tag"
  fi
done
```

**Fix**: Add cumulative traceability tags:
```markdown
## Traceability

### Upstream Sources
- @brd: BRD.01.23.01 - Business objective for user authentication
- @prd: PRD.01.19.01 - Product requirement for login flow
```

---

### CORPUS-13: BDD Translateability Readiness

**Purpose**: Verify EARS requirements are ready for BDD translation

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| BDD-Ready Score | Each document has BDD-Ready Score ≥90% |
| Atomic requirements | No compound requirements with multiple ANDs |
| Clear triggers | WHEN clauses are specific and testable |
| Measurable outcomes | SHALL clauses define observable behavior |

**Validation Logic**:
```bash
# Check BDD-Ready scores
for f in "$EARS_DIR"/EARS-[0-9]*_*.md; do
  score=$(grep -oE "BDD-Ready Score.*[0-9]+%" "$f" | grep -oE "[0-9]+" | head -1)
  if [[ -n "$score" && $score -lt 90 ]]; then
    echo "WARNING: $(basename $f) has BDD-Ready Score $score% (target: ≥90%)"
  fi
done

# Check for compound requirements
grep -nE "SHALL.*and.*and.*and" "$EARS_DIR"/EARS-[0-9]*_*.md | while read line; do
  echo "WARNING: Compound requirement detected - consider splitting"
done
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 4+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate element ID across corpus | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing SHALL statements | CORPUS-11 |
| CORPUS-E012 | Missing @brd traceability tag | CORPUS-12 |
| CORPUS-E013 | Missing @prd traceability tag | CORPUS-12 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Timing constraint not measurable | CORPUS-09 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W013 | BDD-Ready Score below 90% | CORPUS-13 |
| CORPUS-W014 | Compound requirement detected | CORPUS-13 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_ears_corpus.sh docs/EARS

# With verbose output
./scripts/validate_ears_corpus.sh docs/EARS --verbose

# Check specific category
./scripts/validate_ears_corpus.sh docs/EARS --check=traceability
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

### Pre-BDD Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-EARS cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex requirements
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Timing constraints are measurable
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All requirements use EARS syntax (WHEN-THE-SHALL-WITHIN)
- [ ] **CORPUS-12**: All EARS have cumulative traceability (@brd + @prd)
- [ ] **CORPUS-13**: All EARS have BDD-Ready Score ≥90%

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-ears-corpus.yml
name: EARS Corpus Validation

on:
  push:
    paths:
      - 'docs/03_EARS/**/*.md'
  pull_request:
    paths:
      - 'docs/03_EARS/**/*.md'

jobs:
  validate-ears-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate EARS Corpus
        run: |
          chmod +x ./scripts/validate_ears_corpus.sh
          ./scripts/validate_ears_corpus.sh docs/EARS
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: ears-validation-report
          path: tmp/ears_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# EARS corpus validation on staged EARS files
if git diff --cached --name-only | grep -q "^docs/03_EARS/"; then
  echo "Running EARS corpus validation..."
  ./scripts/validate_ears_corpus.sh docs/EARS --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ EARS corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ EARS corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-ears:
	@echo "Validating EARS corpus..."
	@./scripts/validate_ears_corpus.sh docs/EARS

validate-ears-verbose:
	@./scripts/validate_ears_corpus.sh docs/EARS --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req
	@echo "All corpus validations complete"
```

### Integration with BDD Layer Gate

EARS corpus validation should pass before creating BDD documents:

```bash
# Pre-BDD gate check
./scripts/validate_ears_corpus.sh docs/EARS
if [ $? -eq 0 ]; then
  echo "✓ EARS corpus valid - ready for BDD layer creation"
else
  echo "❌ Fix EARS corpus errors before proceeding to BDD layer"
  exit 1
fi
```

---

## 6. Post-Validation Remediation

### Error Remediation Steps

| Error Code | Error | Remediation Steps |
|------------|-------|-------------------|
| **CORPUS-E001** | Placeholder text for existing document | 1. Locate placeholder (e.g., `EARS-03 (future EARS)`)<br>2. Replace with hyperlink: `[EARS-00_index](./EARS-00_index.md)`<br>3. Re-run validation |
| **CORPUS-E002** | Premature downstream reference | 1. Find specific downstream reference (e.g., `BDD-03`, `ADR-05`)<br>2. Replace with generic: "Test scenarios will be documented in the BDD layer"<br>3. Remove numbered references to non-existent Layer 4+ artifacts |
| **CORPUS-E003** | Index out of sync with files | 1. Open index file (e.g., `EARS-00_index.md`)<br>2. Update status from "Planned" to "Draft" or "Complete"<br>3. Add missing file entries<br>4. Remove entries for deleted files |
| **CORPUS-E004** | Duplicate element ID | 1. Search corpus for duplicate ID<br>2. Renumber one instance (increment sequence number)<br>3. Update all references to renamed ID |
| **CORPUS-E005** | File exceeds 1,200 lines | 1. Split into section-based files<br>2. Create index file (`EARS-NN.0_index.md`)<br>3. Move sections to `EARS-NN.1_name.md`, `EARS-NN.2_name.md`<br>4. Update cross-references |
| **CORPUS-E011** | Missing SHALL statements | 1. Review requirements lacking EARS syntax<br>2. Rewrite using WHEN-THE-SHALL-WITHIN pattern<br>3. Ensure each requirement has explicit SHALL |
| **CORPUS-E012** | Missing @brd traceability | 1. Add `@brd: BRD.NN.TT.SS` tag to Traceability section<br>2. Link to originating BRD element<br>3. Verify BRD element exists |
| **CORPUS-E013** | Missing @prd traceability | 1. Add `@prd: PRD.NN.TT.SS` tag to Traceability section<br>2. Link to originating PRD element<br>3. Verify PRD element exists |

### Warning Remediation Steps

| Warning Code | Warning | Remediation Steps |
|--------------|---------|-------------------|
| **CORPUS-W001** | Internal count mismatch | 1. Count actual items in document<br>2. Update claimed count to match<br>3. Reconcile summary sections |
| **CORPUS-W003** | Glossary inconsistency | 1. Choose canonical term (e.g., SHALL not "shall" or "MUST")<br>2. Apply consistently across corpus<br>3. Document in project glossary |
| **CORPUS-W004** | Timing not measurable | 1. Replace vague timing ("reasonable time")<br>2. Add specific threshold: `WITHIN 500ms`<br>3. Add threshold reference: `(@threshold: PRD.NN.name)` |
| **CORPUS-W005** | File exceeds 600 lines | 1. Consider splitting at logical section boundaries<br>2. Monitor for growth toward 1,200 line limit<br>3. Document decision if keeping as single file |
| **CORPUS-W013** | BDD-Ready Score <90% | 1. Review requirements for testability gaps<br>2. Add WITHIN timing clauses<br>3. Ensure clear actor identification<br>4. Add measurable thresholds |
| **CORPUS-W014** | Compound requirement | 1. Split into atomic requirements<br>2. Each requirement = one SHALL<br>3. Link related requirements via traceability |

---

## 7. Accepted Deviations Template

Projects may document intentional framework deviations. Use this template:

### Deviation Documentation Format

```markdown
## Accepted Deviations

### [DEVIATION-ID]: [Short Name]

| Aspect | Framework Standard | Project Implementation |
|--------|-------------------|------------------------|
| **[Aspect 1]** | [Standard behavior] | [Project behavior] |
| **[Aspect 2]** | [Standard behavior] | [Project behavior] |

**Rationale**: [Why this deviation is acceptable for this project]

**Validation Impact**: [How this affects validation - what passes/fails differently]

**Scope**: [Which documents/elements this applies to]
```

### Common Acceptable Deviations

| Deviation | When Acceptable | Documentation Required |
|-----------|-----------------|------------------------|
| Simplified numbering (2-digit vs 3-digit) | <100 requirements per pattern type | Pattern differentiation method |
| Missing diagrams | Simple requirements with clear text | Complexity assessment |
| Single-file structure | <300 lines total | Line count verification |

---

## References

- [EARS_MVP_VALIDATION_RULES.md](./EARS_MVP_VALIDATION_RULES.md) - Individual file validation
- [EARS-MVP-TEMPLATE.md](./EARS-MVP-TEMPLATE.md) - EARS document template (full template archived)
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
