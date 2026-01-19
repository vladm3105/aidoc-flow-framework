---
title: "CTR Quality Gate Validation"
tags:
  - quality-gate-validation
  - layer-8-artifact
  - shared-architecture
custom_fields:
  document_type: quality-gate-validation
  artifact_type: CTR
  layer: 8
  priority: shared
  development_status: active
---

# CTR Quality Gate Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | CTR_QUALITY_GATE_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete CTR corpus |
| Trigger | Run after ALL CTR files are complete |
| Scope | Entire CTR Quality Gate validation |
| Layer | Layer 8 (Optional) → Layer 9 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all CTR (Data Contracts) files are created but BEFORE SPEC creation begins. CTR is an **optional layer** that documents API/data contracts using a dual-file format (.md + .yaml).

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual CTR Validation** | After each CTR creation | Single file | `CTR_MVP_VALIDATION_RULES.md` |
| **Quality Gate Validation** | After ALL CTR complete | Entire CTR set | This document |

### Workflow Position

```
Individual CTR Creation → CTR_MVP_VALIDATION_RULES.md (per-file)
        ↓
All CTR Complete (Optional Layer)
        ↓
CTR_QUALITY_GATE_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin SPEC Creation (Layer 9)
FAIL → Fix issues, re-run Quality Gate validation
```

### CTR Layer Status

| Status | Description |
|--------|-------------|
| Optional | CTR layer can be skipped per `.project_config.yaml` |
| Required When | External APIs, microservices, data exchange contracts |
| Skip When | Monolithic application, internal-only interfaces |

### CTR Dual-File Format

Each contract requires two files:
```
docs/08_CTR/{subdomain}/
├── CTR-NN_{name}.md      # Human-readable contract documentation
└── CTR-NN_{name}.yaml    # Machine-readable schema
```

---

## 1. Quality Gate Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future CTR)` | CTR-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 9+ artifacts

**Severity**: Error (blocking)

**Rationale**: CTR is Layer 8. It should NOT reference specific numbered SPEC or TASKS documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `SPEC-NN` | 9 | SPECs don't exist during CTR creation |
| `TASKS-NN` | 10 | TASKS don't exist during CTR creation |

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 endpoints" | 6 endpoints listed | Count mismatch |
| "3 schemas" | 4 defined | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify CTR index file reflects actual file states

**Severity**: Warning

**Index File Pattern**: `CTR-*_index.md`

---

### CORPUS-05: Inter-CTR Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex contracts

**Severity**: Info

**Recommended Diagrams**:
| CTR Type | Recommended Diagrams |
|----------|---------------------|
| REST API | Sequence diagram |
| Event-driven | Event flow diagram |
| Data schema | ERD diagram |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all CTR files

**Severity**: Warning

---

### CORPUS-08: Contract ID Uniqueness

**Purpose**: No duplicate contract IDs across the CTR corpus

**Severity**: Error

**Contract ID Format**: `CTR-NN` (document-level, not dot notation)

---

### CORPUS-09: Version Format Consistency

**Purpose**: Validate version specifications are consistent

**Severity**: Warning

**Valid Formats**:
| Format | Example |
|--------|---------|
| Semantic | `1.0.0`, `2.1.3` |
| Date-based | `2026-01-04` |

---

### CORPUS-10: File Size Compliance (Universal Splitting Rule)

**Purpose**: Enforce Nested Directory Pattern when triggers are met.

**Severity**: **Error (blocking)** at 1000 lines

**Triggers**:
1. **Size**: File > 1000 lines.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `08_CTR/CTR-{PRD_ID}_{Slug}/` folder.

**Error Message**: `❌ ERROR: CTR-NN triggers nested folder rule (>1000 lines or >1 file). Move to 08_CTR/CTR-NN_{Slug}/`

**Thresholds**:
| Metric | Warning | Error |
|--------|---------|-------|
| Lines | 500 | 1,000 |

---

### CORPUS-11: Dual-File Consistency

**Purpose**: Verify .md and .yaml files match and are synchronized

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| Both files exist | Each CTR has both .md and .yaml |
| Version match | Version in .md matches .yaml |
| Endpoint match | Endpoints in .md match .yaml definitions |
| Schema match | Schemas documented in .md exist in .yaml |

**Validation Logic**:
```bash
# Check for dual-file pairs
for md_file in "$CTR_DIR"/*/CTR-[0-9]*_*.md; do
  yaml_file="${md_file%.md}.yaml"
  if [[ ! -f "$yaml_file" ]]; then
    echo "ERROR: $(basename $md_file) missing paired .yaml file"
  fi
done

for yaml_file in "$CTR_DIR"/*/CTR-[0-9]*_*.yaml; do
  md_file="${yaml_file%.yaml}.md"
  if [[ ! -f "$md_file" ]]; then
    echo "ERROR: $(basename $yaml_file) missing paired .md file"
  fi
done
```

---

### CORPUS-12: YAML Schema Validation

**Purpose**: Verify YAML files are syntactically valid

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| Valid YAML syntax | File parses without errors |
| Required fields | Essential schema fields present |
| Type consistency | Data types properly specified |

**Validation Logic**:
```bash
# Validate YAML syntax
for yaml_file in "$CTR_DIR"/*/CTR-[0-9]*_*.yaml; do
  if ! python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
    echo "ERROR: $(basename $yaml_file) has invalid YAML syntax"
  fi
done
```

---

### CORPUS-13: Version Compatibility Tracking

**Purpose**: Verify breaking changes are documented

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Major version | Breaking changes documented |
| Deprecations | Deprecated fields/endpoints listed |
| Migration guide | Upgrade path documented |

---

### CORPUS-14: Subdomain Classification

**Purpose**: Verify CTR files are in correct subdirectories

**Severity**: Warning

**Valid Subdomains**:
| Subdomain | Description |
|-----------|-------------|
| rest | REST API contracts |
| events | Event schemas and contracts |
| schemas | Shared data schemas |

---

### CORPUS-15: SPEC-Ready Score Threshold

**Purpose**: Verify CTR documents meet SPEC-Ready threshold

**Severity**: Warning

**Threshold**: All CTR files should have SPEC-Ready Score ≥90%

---


### CORPUS-17: Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.

**Severity**: Error

**Check**: `^###\s+CTR\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`


---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference | CORPUS-02 |
| CORPUS-E004 | Duplicate contract ID | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing paired .yaml file | CORPUS-11 |
| CORPUS-E012 | Missing paired .md file | CORPUS-11 |
| CORPUS-E013 | Version mismatch between files | CORPUS-11 |
| CORPUS-E014 | Invalid YAML syntax | CORPUS-12 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Index out of sync | CORPUS-04 |
| CORPUS-W005 | File exceeds 800 lines | CORPUS-10 |
| CORPUS-W009 | Version format inconsistency | CORPUS-09 |
| CORPUS-W013 | Breaking change not documented | CORPUS-13 |
| CORPUS-W014 | Invalid subdomain | CORPUS-14 |
| CORPUS-W015 | SPEC-Ready Score below 90% | CORPUS-15 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Quality Gate Validation

```bash
# Full Quality Gate validation
./scripts/validate_ctr_corpus.sh docs/CTR

# With verbose output
./scripts/validate_ctr_corpus.sh docs/CTR --verbose
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

### Pre-SPEC Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-CTR cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex contracts
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate contract IDs
- [ ] **CORPUS-09**: Version formats consistent
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All CTR have matching .md/.yaml pairs
- [ ] **CORPUS-12**: All YAML files are valid
- [ ] **CORPUS-13**: Breaking changes documented
- [ ] **CORPUS-14**: All CTR in valid subdirectories
- [ ] **CORPUS-15**: All CTR have SPEC-Ready Score ≥90%

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-ctr-corpus.yml
name: CTR Quality Gate Validation

on:
  push:
    paths:
      - 'docs/08_CTR/**/*.md'
      - 'docs/08_CTR/**/*.yaml'
      - 'docs/08_CTR/**/*.yml'
  pull_request:
    paths:
      - 'docs/08_CTR/**/*.md'
      - 'docs/08_CTR/**/*.yaml'
      - 'docs/08_CTR/**/*.yml'

jobs:
  validate-ctr-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate CTR Corpus
        run: |
          chmod +x ./scripts/validate_ctr_corpus.sh
          ./scripts/validate_ctr_corpus.sh docs/CTR
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: ctr-validation-report
          path: tmp/ctr_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# CTR Quality Gate validation on staged CTR files
if git diff --cached --name-only | grep -qE "^docs/08_CTR/.*\.(md|yaml|yml)$"; then
  echo "Running CTR Quality Gate validation..."
  ./scripts/validate_ctr_corpus.sh docs/CTR --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ CTR Quality Gate validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ CTR Quality Gate validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-ctr:
	@echo "Validating CTR corpus..."
	@./scripts/validate_ctr_corpus.sh docs/CTR

validate-ctr-verbose:
	@./scripts/validate_ctr_corpus.sh docs/CTR --verbose

# Include in combined validation target (optional layer)
validate-all-with-optional: validate-all validate-impl validate-ctr
	@echo "All Quality Gate validations including optional layers complete"
```

### Integration with SPEC Layer Gate

CTR Quality Gate validation should pass before creating SPEC documents (when CTR layer is enabled):

```bash
# Pre-SPEC gate check (optional layer)
if [ -d "docs/CTR" ] && [ "$(ls -A docs/CTR 2>/dev/null)" ]; then
  ./scripts/validate_ctr_corpus.sh docs/CTR
  if [ $? -eq 0 ]; then
    echo "✓ CTR corpus valid - ready for SPEC layer creation"
  else
    echo "❌ Fix CTR corpus errors before proceeding to SPEC layer"
    exit 1
  fi
fi
```

---

## References

- [CTR_MVP_VALIDATION_RULES.md](./CTR_MVP_VALIDATION_RULES.md) - Individual file validation
- [CTR-MVP-TEMPLATE.md](./CTR-MVP-TEMPLATE.md) - CTR document template (primary standard)
- [CTR_SCHEMA.yaml](./CTR_SCHEMA.yaml) - Validation schema (OpenAPI 3.x format)
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
