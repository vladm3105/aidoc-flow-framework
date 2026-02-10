---
title: "SYS Quality Gate Validation Rules"
tags:
  - quality-gate-validation
  - layer-6-artifact
  - shared-architecture
  - quality-gate
custom_fields:
  document_type: validation-rules
  artifact_type: SYS
  layer: 6
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# SYS Quality Gate Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | SYS_QUALITY_GATE_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04T00:00:00 |
| Purpose | Quality gate for complete SYS corpus |
| Trigger | Run after ALL SYS files are complete |
| Scope | Entire SYS Quality Gate validation |
| Layer | Layer 6 → Layer 7 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all SYS (System Requirements) files are created but BEFORE REQ creation begins. These rules validate the entire SYS corpus as a cohesive set, checking for cross-document consistency, quality attribute coverage, and quality standards that cannot be verified at the individual file level.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual SYS Validation** | After each SYS creation | Single file | `SYS_MVP_VALIDATION_RULES.md` |
| **Quality Gate Validation** | After ALL SYS complete | Entire SYS set | This document |

### Workflow Position

```
Individual SYS Creation → SYS_MVP_VALIDATION_RULES.md (per-file)
        ↓
All SYS Complete
        ↓
SYS_MVP_QUALITY_GATE_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin REQ Creation (Layer 7)
FAIL → Fix issues, re-run Quality Gate validation
```

---

## 1. Quality Gate Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking REQ creation)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future SYS)` | SYS-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 7+ artifacts

**Severity**: Error (blocking)

**Rationale**: SYS is Layer 6. It should NOT reference specific numbered REQ, SPEC, or TASKS documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `REQ-NN` | 7 | REQs don't exist during SYS creation |
| `SPEC-NN` | 10 | SPECs don't exist during SYS creation |
| `TASKS-NN` | 11 | TASKS don't exist during SYS creation |

**Allowed Patterns** (generic references):
- "This will inform REQ development"
- "Downstream SPEC artifacts will..."
- "See future implementation for details"

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 system requirements" | 6 requirements listed | Count mismatch |
| "3 quality attributes" | 4 enumerated | Count mismatch |
| "7 interfaces" | 8 described | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify SYS index file reflects actual file states

**Severity**: Error

**Index File Pattern**: `SYS-*_index.md` (e.g., `SYS-00_index.md`)

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing SYS files listed in index |
| Version currency | Version numbers match file headers |
| Status accuracy | Status matches actual file content |

---

### CORPUS-05: Inter-SYS Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability. Hyperlinks are optional enhancements.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex system requirements

**Severity**: Info

**Recommended Diagrams by SYS Type**:
| SYS Type | Recommended Diagrams |
|----------|---------------------|
| Interface definitions | Component diagram |
| Data flows | Data flow diagram |
| State management | State machine diagram |
| Integration points | Sequence diagram |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all SYS files

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Term consistency | Same term used same way across docs |
| Acronym expansion | Acronyms expanded on first use per doc |
| No conflicting definitions | Same concept not defined differently |

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the SYS corpus

**Severity**: Error

**Element ID Format**: `SYS.NN.TT.SS`
- NN = Document number
- TT = Element type code
- SS = Sequence number

**Validation Logic**:
```bash
# Check for duplicate element IDs
grep -rohE "SYS\.[0-9]+\.[0-9]+\.[0-9]+" "$SYS_DIR"/*.md | sort | uniq -d
```

---

### CORPUS-09: Quality Attribute Quantification

**Purpose**: Validate quality attribute specifications are measurable

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Response time | Numeric values with units (ms, seconds) |
| Throughput | Transactions per second/minute |
| Availability | Percentage (99.9%, 99.99%) |
| Scalability | Numeric limits or ranges |

**Vague Patterns to Flag**:
| Pattern | Issue |
|---------|-------|
| "fast response" | Not measurable |
| "high availability" | Not quantified |
| "scalable" | No numeric threshold |
| "performant" | Undefined metric |

---

### CORPUS-10: File Size Compliance (Universal Splitting Rule)

**Purpose**: Enforce Nested Directory Pattern when triggers are met.

**Severity**: **Error (blocking)** at 20,000 tokens

**Triggers**:
1. **Size**: File > 20,000 tokens.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `06_SYS/SYS-{PRD_ID}_{Slug}/` folder.

**Error Message**: `❌ ERROR: SYS-NN triggers nested folder rule (>20,000 tokens or >1 file). Move to 06_SYS/SYS-NN_{Slug}/`

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 500 | 1,000 |
| Tokens | 50,000 | — |

---

### CORPUS-11: Cumulative Traceability (@brd + @prd + @ears + @bdd + @adr)

**Purpose**: Verify all SYS have cumulative upstream traceability

**Severity**: Error

**Required Tags**: Each SYS must include all five:
- `@brd:` tag linking to source BRD element
- `@prd:` tag linking to source PRD element
- `@ears:` tag linking to source EARS element
- `@bdd:` tag linking to source BDD element
- `@adr:` tag linking to source ADR document

**Validation Logic**:
```bash
# Check each SYS has cumulative traceability
for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
  if [[ "$(basename $f)" =~ _index ]]; then continue; fi

  has_brd=$(grep -c "@brd:" "$f" 2>/dev/null || true)
  has_prd=$(grep -c "@prd:" "$f" 2>/dev/null || true)
  has_ears=$(grep -c "@ears:" "$f" 2>/dev/null || true)
  has_bdd=$(grep -c "@bdd:" "$f" 2>/dev/null || true)
  has_adr=$(grep -c "@adr:" "$f" 2>/dev/null || true)

  if [[ $has_brd -eq 0 ]]; then
    echo "ERROR: $(basename $f) missing @brd traceability tag"
  fi
  # ... repeat for other tags
done
```

---

### CORPUS-12: Quality Attribute Coverage

**Purpose**: Verify all standard quality attributes are addressed

**Severity**: Warning

**Standard Quality Attributes** (ISO 25010):
| Attribute | Description |
|-----------|-------------|
| Performance | Response time, throughput, resource utilization |
| Reliability | Availability, fault tolerance, recoverability |
| Security | Confidentiality, integrity, authentication |
| Maintainability | Modularity, testability, modifiability |
| Scalability | Horizontal/vertical scaling limits |

**Validation Logic**:
```bash
# Check for quality attribute coverage across corpus
qa_keywords=("performance" "reliability" "security" "maintainability" "scalability" "availability")
for qa in "${qa_keywords[@]}"; do
  count=$(grep -ril "$qa" "$SYS_DIR"/SYS-[0-9]*_*.md 2>/dev/null | wc -l)
  if [[ $count -eq 0 ]]; then
    echo "WARNING: No SYS documents address '$qa'"
  fi
done
```

---

### CORPUS-13: Non-Functional Requirement Completeness

**Purpose**: Verify NFRs cover essential categories

**Severity**: Warning

**Essential NFR Categories**:
| Category | Description |
|----------|-------------|
| Performance | Response time, throughput requirements |
| Capacity | Data volume, concurrent user limits |
| Availability | Uptime requirements, maintenance windows |
| Security | Authentication, authorization, encryption |
| Compliance | Regulatory requirements (if applicable) |
| Integration | External system interface requirements |

**Validation Logic**:
```bash
# Check NFR category coverage
nfr_categories=("Performance" "Capacity" "Availability" "Security" "Compliance" "Integration")
for nfr in "${nfr_categories[@]}"; do
  count=$(grep -rilE "^#+.*$nfr|$nfr Requirements" "$SYS_DIR"/SYS-[0-9]*_*.md 2>/dev/null | wc -l)
  if [[ $count -eq 0 ]]; then
    echo "WARNING: No SYS documents have '$nfr' section"
  fi
done
```

---

### CORPUS-14: Interface Definition Completeness

**Purpose**: Verify system interfaces are fully specified

**Severity**: Warning

**Required Interface Elements**:
| Element | Description |
|---------|-------------|
| Protocol | HTTP, gRPC, WebSocket, etc. |
| Data format | JSON, Protobuf, XML, etc. |
| Authentication | Method and requirements |
| Error handling | Error codes and responses |

---

### CORPUS-15: REQ-Ready Score Threshold

**Purpose**: Verify SYS documents meet REQ-Ready threshold

**Severity**: Warning

**Thresholds**:
| Template Profile | Threshold | Detection |
|------------------|-----------|-----------|
| MVP (default) | ≥85% | `template_profile: mvp` or no marker |
| Full | ≥90% | `template_profile: full` |

**Validation Logic**:
```bash
# Check REQ-Ready scores with profile-aware threshold
for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
  if [[ "$(basename $f)" =~ _index ]]; then continue; fi

  # Detect profile (default to mvp)
  if grep -q "template_profile: full" "$f" 2>/dev/null; then
    threshold=90
  else
    threshold=85
  fi

  score=$(grep -oE "REQ-Ready Score[^0-9]*[0-9]+" "$f" | grep -oE "[0-9]+" | head -1)
  if [[ -n "$score" && $score -lt $threshold ]]; then
    echo "WARNING: $(basename $f) has REQ-Ready Score $score% (target: ≥$threshold%)"
  fi
done
```

---

### CORPUS-16: Template Variant Declaration

**Purpose**: Verify documents using specialized templates declare template variant in metadata

**Severity**: Error

**Required for**: Documents containing template-specific sections (e.g., "MVP Scope")

**Validation Logic**:
```bash
for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
  if grep -q "MVP Scope\|Full Scope" "$f" 2>/dev/null; then
    if ! grep -q "template_variant:" "$f" 2>/dev/null; then
      echo "ERROR: $(basename $f) missing template_variant declaration"
    fi
  fi
done
```

---

### CORPUS-17: Parent-Child Document Hierarchy

**Purpose**: Verify subsystem documents reference their parent document

**Severity**: Error (for designated subsystem documents)

**Applicability**: Documents designated as subsystems (configurable per project)

**Required Tag**: `@parent-sys: SYS-NN`

**Configuration**: Define `SUBSYSTEM_START` environment variable per project

**Validation Logic**:
```bash
for f in "$SYS_DIR"/SYS-[0-9]*_*.md; do
  doc_num=$(basename "$f" | grep -oE "SYS-[0-9]+" | grep -oE "[0-9]+")
  if [[ $doc_num -ge $SUBSYSTEM_START ]]; then
    if ! grep -q "@parent-sys:" "$f" 2>/dev/null; then
      echo "ERROR: $(basename $f) is subsystem but missing @parent-sys tag"
    fi
  fi
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
| `@adr` | Dash (document-level) | `ADR-33` | References whole document |
| `@spec` | Dash (document-level) | `SPEC-07` | References whole document |
| `@parent-sys` | Dash (document-level) | `SYS-07` | References parent document |

**Validation Logic**:
```bash
grep -rn "@brd:" "$SYS_DIR"/*.md | grep "BRD-" && echo "ERROR: @brd should use dot notation"
grep -rn "@adr:" "$SYS_DIR"/*.md | grep "ADR\." && echo "ERROR: @adr should use dash notation"
```

---

### CORPUS-19: Date Format Consistency

**Purpose**: Verify all dates use ISO 8601 format

**Severity**: Error

**Required Format**: `YYYY-MM-DDTHH:MM:SS` (e.g., `2026-01-04T00:00:00`)

**Invalid Formats**:
| Pattern | Example | Issue |
|---------|---------|-------|
| `MM/DD/YYYY` | `01/04/2026` | US format ambiguous |
| `DD/MM/YYYY` | `04/01/2026` | EU format ambiguous |
| `Month D, YYYY` | `January 4, 2026` | Verbose, inconsistent |

**Validation Logic**:
```bash
grep -rE "[0-9]{2}/[0-9]{2}/[0-9]{4}" "$SYS_DIR"/*.md && echo "ERROR: Invalid date format"
```

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference (Layer 7+) | CORPUS-02 |
| CORPUS-E003 | Index out of sync with actual files | CORPUS-04 |
| CORPUS-E004 | Duplicate element ID across corpus | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing @brd traceability tag | CORPUS-11 |
| CORPUS-E012 | Missing @prd traceability tag | CORPUS-11 |
| CORPUS-E013 | Missing @ears traceability tag | CORPUS-11 |
| CORPUS-E014 | Missing @bdd traceability tag | CORPUS-11 |
| CORPUS-E015 | Missing @adr traceability tag | CORPUS-11 |
| CORPUS-E016 | Missing template_variant declaration | CORPUS-16 |
| CORPUS-E017 | Missing @parent-sys in subsystem doc | CORPUS-17 |
| CORPUS-E018 | Wrong tag notation (dot vs dash) | CORPUS-18 |
| CORPUS-E019 | Invalid date format | CORPUS-19 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Quality attribute not quantified | CORPUS-09 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W012 | Missing quality attribute coverage | CORPUS-12 |
| CORPUS-W013 | NFR category not addressed | CORPUS-13 |
| CORPUS-W014 | Interface definition incomplete | CORPUS-14 |
| CORPUS-W015 | REQ-Ready Score below threshold (MVP: 85%, Full: 90%) | CORPUS-15 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Quality Gate Validation

```bash
# Full Quality Gate validation
./scripts/validate_sys_corpus.sh docs/SYS

# With verbose output
./scripts/validate_sys_corpus.sh docs/SYS --verbose

# Check specific category
./scripts/validate_sys_corpus.sh docs/SYS --check=traceability
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

### Pre-REQ Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-SYS cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex requirements
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Quality attributes are quantified
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All SYS have cumulative traceability (5 tags)
- [ ] **CORPUS-12**: Quality attribute coverage complete
- [ ] **CORPUS-13**: NFR categories addressed
- [ ] **CORPUS-14**: Interface definitions complete
- [ ] **CORPUS-15**: All SYS meet REQ-Ready Score threshold (MVP: ≥85%, Full: ≥90%)
- [ ] **CORPUS-16**: Template variant declared for specialized templates
- [ ] **CORPUS-17**: Parent-child hierarchy tags present for subsystems
- [ ] **CORPUS-18**: Tag notation consistent (dot vs dash)
- [ ] **CORPUS-19**: All dates use ISO 8601 format

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-sys-corpus.yml
name: SYS Quality Gate Validation

on:
  push:
    paths:
      - 'docs/06_SYS/**/*.md'
  pull_request:
    paths:
      - 'docs/06_SYS/**/*.md'

jobs:
  validate-sys-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate SYS Corpus
        run: |
          chmod +x ./scripts/validate_sys_corpus.sh
          ./scripts/validate_sys_corpus.sh docs/SYS
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: sys-validation-report
          path: tmp/sys_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# SYS Quality Gate validation on staged SYS files
if git diff --cached --name-only | grep -q "^docs/06_SYS/"; then
  echo "Running SYS Quality Gate validation..."
  ./scripts/validate_sys_corpus.sh docs/SYS --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ SYS Quality Gate validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ SYS Quality Gate validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-sys:
	@echo "Validating SYS corpus..."
	@./scripts/validate_sys_corpus.sh docs/SYS

validate-sys-verbose:
	@./scripts/validate_sys_corpus.sh docs/SYS --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req validate-spec
	@echo "All Quality Gate validations complete"
```

### Integration with REQ Layer Gate

SYS Quality Gate validation should pass before creating REQ documents:

```bash
# Pre-REQ gate check
./scripts/validate_sys_corpus.sh docs/SYS
if [ $? -eq 0 ]; then
  echo "✓ SYS corpus valid - ready for REQ layer creation"
else
  echo "❌ Fix SYS corpus errors before proceeding to REQ layer"
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
- Tag notation errors (CORPUS-18)
- Invalid date formats (CORPUS-19)

### Priority 2: Quality (Recommended Before Approval)

- Internal count mismatches (CORPUS-03)
- Missing diagrams (CORPUS-06)
- Terminology inconsistencies (CORPUS-07)
- Unquantified quality attributes (CORPUS-09)
- File size warnings (CORPUS-10)
- Template variant declaration (CORPUS-16)
- Parent-child hierarchy (CORPUS-17)

### Priority 3: Continuous (Address During Maintenance)

- Quality attribute coverage gaps (CORPUS-12)
- NFR category gaps (CORPUS-13)
- Interface completeness (CORPUS-14)
- REQ-Ready score below threshold (CORPUS-15)

---

## References

- [SYS_MVP_VALIDATION_RULES.md](./SYS_MVP_VALIDATION_RULES.md) - Individual file validation
- [SYS_MVP_CREATION_RULES.md](./SYS_MVP_CREATION_RULES.md) - SYS creation guidelines

- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
