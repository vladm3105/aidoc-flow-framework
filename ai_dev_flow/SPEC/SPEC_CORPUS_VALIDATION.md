# SPEC Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | SPEC_CORPUS_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete SPEC corpus |
| Trigger | Run after ALL SPEC files are complete |
| Scope | Entire SPEC corpus validation |
| Layer | Layer 10 → Layer 11 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all SPEC (Technical Specifications) files are created but BEFORE TASKS creation begins. SPEC documents use YAML format for machine-readable implementation specifications.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual SPEC Validation** | After each SPEC creation | Single file | `SPEC_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL SPEC complete | Entire SPEC set | This document |

### Workflow Position

```
Individual SPEC Creation → SPEC_VALIDATION_RULES.md (per-file)
        ↓
All SPEC Complete
        ↓
SPEC_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin TASKS Creation (Layer 11)
FAIL → Fix issues, re-run corpus validation
```

### SPEC Format

SPEC documents use YAML format for machine-readable specifications:
```
docs/SPEC/
├── SPEC-NN_{name}.yaml    # Technical specification
└── SPEC-000_index.md      # Registry/index file
```

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future SPEC)` | SPEC-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 11+ artifacts

**Severity**: Error (blocking)

**Rationale**: SPEC is Layer 10. It should NOT reference specific numbered TASKS or IPLAN documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `TASKS-NN` | 11 | TASKS don't exist during SPEC creation |
| `IPLAN-NN` | 12 | IPLANs don't exist during SPEC creation |

**Allowed Patterns** (generic references):
- "This will inform TASKS development"
- "Downstream implementation will..."
- "See future IPLAN for execution"

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 parameters" | 6 parameters listed | Count mismatch |
| "3 endpoints" | 4 defined | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify SPEC index file reflects actual file states

**Severity**: Warning

**Index File Pattern**: `SPEC-000_index.md` or `SPEC-*_index.md`

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing SPEC files listed in index |

---

### CORPUS-05: Inter-SPEC Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex specifications

**Severity**: Info

**Recommended Diagrams**:
| SPEC Type | Recommended Diagrams |
|-----------|---------------------|
| API specification | Sequence diagram |
| State machine | State transition diagram |
| Data flow | Data flow diagram |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all SPEC files

**Severity**: Warning

---

### CORPUS-08: Specification ID Uniqueness

**Purpose**: No duplicate SPEC IDs across the corpus

**Severity**: Error

**SPEC ID Format**: `SPEC-NN` (document-level)

---

### CORPUS-09: Parameter Type Format

**Purpose**: Validate parameter type specifications are consistent

**Severity**: Warning

**Valid Type Formats**:
| Format | Example |
|--------|---------|
| Primitive | `string`, `integer`, `boolean`, `float` |
| Complex | `List[string]`, `Dict[string, any]`, `Optional[int]` |
| Custom | `UserID`, `OrderStatus`, `Timestamp` |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

---

### CORPUS-11: YAML Syntax Validation

**Purpose**: Verify all SPEC files have valid YAML syntax

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| Valid YAML | File parses without errors |
| Proper indentation | Consistent 2-space indentation |
| No syntax errors | No malformed keys/values |

**Validation Logic**:
```bash
# Validate YAML syntax
for yaml_file in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
  if ! python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
    echo "ERROR: $(basename $yaml_file) has invalid YAML syntax"
  fi
done
```

---

### CORPUS-12: Parameter Type Consistency

**Purpose**: Verify parameter types are consistent across related specifications

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Type naming | Same concept uses same type name |
| Type definitions | Custom types defined consistently |
| Input/output matching | Function inputs match expected outputs |

---

### CORPUS-13: REQ Coverage

**Purpose**: Verify all requirements have corresponding specifications

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| REQ references | Each SPEC references implemented REQs |
| Coverage gaps | No orphaned REQs without SPEC |
| Traceability matrix | All REQs accounted for |

**Validation Logic**:
```bash
# Check for REQ references in SPEC files
for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
  req_refs=$(grep -coE "REQ-[0-9]+" "$f" 2>/dev/null || echo 0)
  if [[ $req_refs -eq 0 ]]; then
    echo "WARNING: $(basename $f) has no REQ references"
  fi
done
```

---

### CORPUS-14: Required YAML Fields

**Purpose**: Verify all SPEC files contain required fields

**Severity**: Error

**Required Fields**:
| Field | Description |
|-------|-------------|
| `spec_id` | Unique specification identifier |
| `version` | Specification version |
| `title` | Human-readable title |
| `description` | Brief description |
| `upstream_refs` | Traceability references |

---

### CORPUS-15: Cumulative Traceability Compliance

**Purpose**: Verify SPEC includes cumulative upstream tags

**Severity**: Error

**Required Upstream Tags** (7 cumulative):
| Tag | Layer | Description |
|-----|-------|-------------|
| `@brd` | 1 | Business Requirements |
| `@prd` | 2 | Product Requirements |
| `@ears` | 3 | EARS Requirements |
| `@bdd` | 4 | BDD Scenarios |
| `@adr` | 5 | Architecture Decisions |
| `@sys` | 6 | System Requirements |
| `@req` | 7 | Atomic Requirements |

**Note**: Optional layers (IMPL@8, CTR@9) included if present

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference | CORPUS-02 |
| CORPUS-E004 | Duplicate SPEC ID | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Invalid YAML syntax | CORPUS-11 |
| CORPUS-E013 | REQ without SPEC coverage | CORPUS-13 |
| CORPUS-E014 | Missing required YAML field | CORPUS-14 |
| CORPUS-E015 | Missing cumulative traceability | CORPUS-15 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Index out of sync | CORPUS-04 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W009 | Parameter type format inconsistency | CORPUS-09 |
| CORPUS-W012 | Parameter type inconsistency | CORPUS-12 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_spec_corpus.sh docs/SPEC

# With verbose output
./scripts/validate_spec_corpus.sh docs/SPEC --verbose
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

### Pre-TASKS Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-SPEC cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex specifications
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate SPEC IDs
- [ ] **CORPUS-09**: Parameter type formats consistent
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All YAML files syntactically valid
- [ ] **CORPUS-12**: Parameter types consistent across specs
- [ ] **CORPUS-13**: All REQs have SPEC coverage
- [ ] **CORPUS-14**: All SPEC have required YAML fields
- [ ] **CORPUS-15**: Cumulative traceability complete (7 tags)

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-spec-corpus.yml
name: SPEC Corpus Validation

on:
  push:
    paths:
      - 'docs/SPEC/**/*.yaml'
      - 'docs/SPEC/**/*.yml'
      - 'docs/SPEC/**/*.md'
  pull_request:
    paths:
      - 'docs/SPEC/**/*.yaml'
      - 'docs/SPEC/**/*.yml'
      - 'docs/SPEC/**/*.md'

jobs:
  validate-spec-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate SPEC Corpus
        run: |
          chmod +x ./scripts/validate_spec_corpus.sh
          ./scripts/validate_spec_corpus.sh docs/SPEC
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: spec-validation-report
          path: tmp/spec_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# SPEC corpus validation on staged SPEC files
if git diff --cached --name-only | grep -qE "^docs/SPEC/.*\.(yaml|yml|md)$"; then
  echo "Running SPEC corpus validation..."
  ./scripts/validate_spec_corpus.sh docs/SPEC --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ SPEC corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ SPEC corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-spec:
	@echo "Validating SPEC corpus..."
	@./scripts/validate_spec_corpus.sh docs/SPEC

validate-spec-verbose:
	@./scripts/validate_spec_corpus.sh docs/SPEC --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req validate-spec validate-tasks validate-iplan
	@echo "All corpus validations complete"
```

### Integration with TASKS Layer Gate

SPEC corpus validation should pass before creating TASKS documents:

```bash
# Pre-TASKS gate check
./scripts/validate_spec_corpus.sh docs/SPEC
if [ $? -eq 0 ]; then
  echo "✓ SPEC corpus valid - ready for TASKS layer creation"
else
  echo "❌ Fix SPEC corpus errors before proceeding to TASKS layer"
  exit 1
fi
```

---

## References

- [SPEC_VALIDATION_RULES.md](./SPEC_VALIDATION_RULES.md) - Individual file validation
- [SPEC-TEMPLATE.yaml](./SPEC-TEMPLATE.yaml) - SPEC document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
