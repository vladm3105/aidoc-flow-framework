---
title: "SPEC Quality Gate Validation"
tags:
  - quality-gate-validation
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: quality-gate-validation
  artifact_type: SPEC
  layer: 9
  priority: shared
  development_status: active
---

# SPEC Quality Gate Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | SPEC_QUALITY_GATE_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete SPEC corpus |
| Trigger | Run after ALL SPEC files are complete |
| Scope | Entire SPEC Quality Gate validation |
| Layer | Layer 9 → Layer 10 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all SPEC (Technical Specifications) files are created but BEFORE TASKS creation begins. SPEC documents use YAML format for machine-readable implementation specifications.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual SPEC Validation** | After each SPEC creation | Single file | `SPEC_MVP_VALIDATION_RULES.md` |
| **Quality Gate Validation** | After ALL SPEC complete | Entire SPEC set | This document |

### Workflow Position

```
Individual SPEC Creation → SPEC_MVP_VALIDATION_RULES.md (per-file)
        ↓
All SPEC Complete
        ↓
SPEC_MVP_QUALITY_GATE_VALIDATION.md CORPUS-01 to CORPUS-15 (automated)
        ↓
CORPUS-FINAL: Holistic AI Review (manual) ← FINAL GATE
        ↓
Fix ALL inconsistencies
        ↓
PASS → Begin TASKS Creation (Layer 10)
FAIL → Fix issues, re-run Quality Gate validation
```

### SPEC Format

SPEC documents use YAML format for machine-readable specifications:
```
docs/09_SPEC/
├── SPEC-NN_{name}.yaml    # Technical specification
└── SPEC-000_index.md      # Registry/index file
```

---

## 1. Quality Gate Validation Checks

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

**Purpose**: Detect references to non-existent Layer 10+ artifacts

**Severity**: Error (blocking)

**Rationale**: SPEC is Layer 9. It should NOT reference specific numbered TASKS documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `TASKS-NN` | 10 | TASKS don't exist during SPEC creation |

**Allowed Patterns** (generic references):
- "This will inform TASKS development"
- "Downstream implementation will..."
- "See future TASKS for execution"

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

### CORPUS-10: File Size Compliance (Universal Splitting Rule)

**Purpose**: Enforce Nested Directory Pattern when triggers are met.

**Severity**: **Error (blocking)** at 20,000 tokens

**Triggers**:
1. **Size**: File > 20,000 tokens.
2. **Cardinality**: More than 1 file for this ID.

**Action**: Move to `09_SPEC/SPEC-{PRD_ID}_{Slug}/` folder.

**Error Message**: `❌ ERROR: SPEC-NN triggers nested folder rule (>20,000 tokens or >1 file). Move to 09_SPEC/SPEC-NN_{Slug}/`

**File Format**: YAML (.yaml, .yml)

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
  req_refs=$(grep -coE "REQ-[0-9]+" "$f" 2>/dev/null || true)
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

**Note**: Optional layer (CTR@8) included if present

---

### CORPUS-16: Required Subsection Coverage ⭐ NEW

**Purpose**: Verify all SPEC files contain the 6 required subsections

**Severity**: Error (blocking)

**Required Subsections**:
| Section | Subsection | Purpose |
|---------|------------|---------|
| `traceability` | `upstream_links` | Quick reference to source documents |
| `architecture` | `overview` | High-level component description |
| `architecture` | `component_structure` | Logical component breakdown |
| `architecture` | `element_ids` | Unique element identifiers |
| `interfaces` | `external_apis` | HTTP endpoints |
| `interfaces` | `internal_apis` | Internal method signatures |

**Validation Logic**:
```bash
# Check for required subsections in SPEC files
for f in "$SPEC_DIR"/SPEC-[0-9]*_*.yaml; do
  for subsection in "upstream_links" "overview" "component_structure" "element_ids" "external_apis" "internal_apis"; do
    if ! grep -q "$subsection:" "$f" 2>/dev/null; then
      echo "ERROR: $(basename $f) missing required subsection: $subsection"
    fi
  done
done
```

**Error Message**: `❌ CORPUS-E016: Missing required subsection {subsection} in {filename}`

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
| CORPUS-E016 | Missing required subsection | CORPUS-16 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Index out of sync | CORPUS-04 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W006 | Naming convention violation (PascalCase classes, snake_case methods - dunder methods allowed) | - |
| CORPUS-W008 | ID formatting issue | - |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Quality Gate Validation

```bash
# Full Quality Gate validation
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
- [ ] **CORPUS-16**: All required subsections present (upstream_links, overview, component_structure, element_ids, external_apis, internal_apis)

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-spec-corpus.yml
name: SPEC Quality Gate Validation

on:
  push:
    paths:
      - 'docs/09_SPEC/**/*.yaml'
      - 'docs/09_SPEC/**/*.yml'
      - 'docs/09_SPEC/**/*.md'
  pull_request:
    paths:
      - 'docs/09_SPEC/**/*.yaml'
      - 'docs/09_SPEC/**/*.yml'
      - 'docs/09_SPEC/**/*.md'

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

# SPEC Quality Gate validation on staged SPEC files
if git diff --cached --name-only | grep -qE "^docs/09_SPEC/.*\.(yaml|yml|md)$"; then
  echo "Running SPEC Quality Gate validation..."
  ./scripts/validate_spec_corpus.sh docs/SPEC --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ SPEC Quality Gate validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ SPEC Quality Gate validation passed"
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
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req validate-spec validate-tasks
	@echo "All Quality Gate validations complete"
```

### Integration with TASKS Layer Gate

SPEC Quality Gate validation should pass before creating TASKS documents:

```bash
# Pre-TASKS gate check
./scripts/validate_spec_corpus.sh docs/SPEC
if [ $? -eq 0 ]; then
  echo "✓ SPEC corpus valid - ready for TASKS layer creation (Layer 10)"
else
  echo "❌ Fix SPEC corpus errors before proceeding to TASKS layer"
  exit 1
fi
```

---

## 3. CORPUS-FINAL: Holistic Project-Level Review (MANDATORY)

> **⚠️ CRITICAL**: This is the FINAL validation step before TASKS creation. All errors and inconsistencies MUST be fixed.

### Purpose

Perform a comprehensive, manual AI-assisted review of ALL SPEC files as a cohesive code generation skeleton. This is NOT automated validation—it requires intelligent analysis of the entire SPEC corpus as a project.

### When to Run

- After ALL automated quality gate checks pass (CORPUS-01 through CORPUS-15)
- Before creating ANY TASKS documents
- Must be performed by AI assistant, not scripts

### Review Scope

| Category | What to Check |
|----------|--------------|
| **Cross-SPEC Consistency** | Same concepts use same values across files |
| **Dependency Coherence** | All internal dependencies reference valid SPECs |
| **Interface Contracts** | APIs match between provider and consumer SPECs |
| **Technology Alignment** | All SPECs use approved ADR-00 stack |
| **Parameter Consistency** | Same parameters have same types/formats |
| **Link Validity** | All upstream links point to existing documents |
| **Threshold References** | Use @threshold instead of hardcoded values |
| **Naming Conventions** | Consistent YAML formatting and quoting |

### Required Analysis Steps

1. **Inventory all SPEC files**: Count and list all YAML files
2. **Extract cross-SPEC patterns**: 
   - `auth:` values across all files
   - `latency_target:` values  
   - `rate_limit:` values
   - `language:` values
   - `domain:` values
3. **Identify inconsistencies**: Flag format variations
4. **Verify dependency graph**: Ensure no circular or missing dependencies
5. **Check REQ coverage**: Confirm all REQs mapped with no duplicates
6. **Technology stack alignment**: Verify against ADR-00

### Output Requirements

Generate a **SPEC Skeleton Review Report** with:

| Section | Content |
|---------|---------|
| Executive Summary | File count, critical/minor issues, overall status |
| Structure Consistency | Required fields, section ordering |
| Cross-SPEC Inconsistencies | List all format/value inconsistencies |
| Dependency Coherence | Internal/external dependency validation |
| Interface Contract Coherence | API consistency |
| REQ Traceability | Coverage and duplicate check |
| Technology Stack Alignment | ADR-00 compliance |
| Recommendations | Must-fix and should-fix items |
| Verdict | READY or NOT READY for TASKS |

### Pass/Fail Criteria

| Severity | Impact |
|----------|--------|
| **Critical Issues** | MUST fix before TASKS - blocks code generation |
| **Consistency Issues** | MUST fix - affects code consistency |
| **Minor Issues** | SHOULD fix - cosmetic but recommended |

**To PASS**: 0 critical issues, 0 consistency issues (minor issues acceptable)

### Fixing Inconsistencies

All inconsistencies identified MUST be fixed before proceeding to TASKS:

```bash
# Example fixes for common inconsistencies

# 1. Auth format - standardize to quoted strings
auth: "JWT Bearer"  # Not: auth: JWT Bearer

# 2. Latency - use threshold references
latency_target: "@threshold:perf.api.p95_latency"  # Not: latency_target: "50ms"

# 3. Domain - consistent naming
domain: "foundation"  # Not: domain: "d1_foundation"

# 4. Language - include version
language: "Python 3.12+"  # Not: language: "python"
```

### Workflow Integration

```
All SPECS Complete
        ↓
CORPUS-01 through CORPUS-15 (automated) ← Pass required
        ↓
CORPUS-FINAL: Holistic AI Review (manual) ← THIS STEP
        ↓
Fix ALL inconsistencies
        ↓
Re-run holistic review
        ↓
PASS → SPEC Skeleton READY
        ↓
Begin SPEC Dependency Analysis (TASKS_MVP_CREATION_RULES Section 0)
        ↓
Create TASKS documents
```

---

## References

- [SPEC_MVP_VALIDATION_RULES.md](./SPEC_MVP_VALIDATION_RULES.md) - Individual file validation
- [SPEC-MVP-TEMPLATE.yaml](./SPEC-MVP-TEMPLATE.yaml) - SPEC document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
