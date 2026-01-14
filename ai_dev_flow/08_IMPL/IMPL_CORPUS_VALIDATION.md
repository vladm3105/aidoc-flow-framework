# IMPL Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | IMPL_CORPUS_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete IMPL corpus |
| Trigger | Run after ALL IMPL files are complete |
| Scope | Entire IMPL corpus validation |
| Layer | Layer 8 (Optional) → Layer 9/10 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all IMPL (Implementation Approach) files are created but BEFORE CTR or SPEC creation begins. IMPL is an **optional layer** that documents WHO-WHEN-WHAT implementation strategies.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual IMPL Validation** | After each IMPL creation | Single file | `IMPL_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL IMPL complete | Entire IMPL set | This document |

### Workflow Position

```
Individual IMPL Creation → IMPL_VALIDATION_RULES.md (per-file)
        ↓
All IMPL Complete (Optional Layer)
        ↓
IMPL_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin CTR (Layer 9) or SPEC (Layer 10)
FAIL → Fix issues, re-run corpus validation
```

### IMPL Layer Status

| Status | Description |
|--------|-------------|
| Optional | IMPL layer can be skipped per `.project_config.yaml` |
| Required When | Complex implementation requires team coordination |
| Skip When | Single developer, straightforward implementation |

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future IMPL)` | IMPL-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 9+ artifacts

**Severity**: Error (blocking)

**Rationale**: IMPL is Layer 8. It should NOT reference specific numbered CTR, SPEC, TASKS, or IPLAN documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `CTR-NN` | 9 | CTR don't exist during IMPL creation |
| `SPEC-NN` | 10 | SPECs don't exist during IMPL creation |
| `TASKS-NN` | 11 | TASKS don't exist during IMPL creation |
| `IPLAN-NN` | 12 | IPLANs don't exist during IMPL creation |

**Allowed Patterns** (generic references):
- "This will inform SPEC development"
- "Downstream TASKS will..."
- "See future implementation details"

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 implementation phases" | 6 phases listed | Count mismatch |
| "3 team members" | 4 listed | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify IMPL index file reflects actual file states

**Severity**: Warning

**Index File Pattern**: `IMPL-*_index.md`

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing IMPL files listed in index |

---

### CORPUS-05: Inter-IMPL Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for implementation approaches

**Severity**: Info

**Recommended Diagrams**:
| IMPL Type | Recommended Diagrams |
|-----------|---------------------|
| Phased rollout | Gantt chart (Mermaid) |
| Team structure | Organization diagram |
| Dependencies | Dependency graph |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all IMPL files

**Severity**: Warning

---

### CORPUS-08: Element ID Uniqueness

**Purpose**: No duplicate element IDs across the IMPL corpus

**Severity**: Error

**Element ID Format**: `IMPL.NN.TT.SS`

---

### CORPUS-09: Resource Specification

**Purpose**: Validate resource allocations are specified

**Severity**: Warning

**Required Elements**:
| Element | Description |
|---------|-------------|
| WHO | Team member/role assignment |
| WHEN | Timeline/phase specification |
| WHAT | Deliverable description |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

---

### CORPUS-11: WHO-WHEN-WHAT Structure Compliance

**Purpose**: Verify all IMPL follow the WHO-WHEN-WHAT pattern

**Severity**: Error

**Required Sections**:
| Section | Description |
|---------|-------------|
| WHO | Responsible parties (roles/teams) |
| WHEN | Timeline and milestones |
| WHAT | Deliverables and outcomes |

**Validation Logic**:
```bash
# Check for WHO-WHEN-WHAT structure
for f in "$IMPL_DIR"/IMPL-[0-9]*_*.md; do
  if ! grep -qiE "^#+.*(WHO|Responsible|Team|Owner)" "$f"; then
    echo "ERROR: $(basename $f) missing WHO section"
  fi
  if ! grep -qiE "^#+.*(WHEN|Timeline|Schedule|Phase)" "$f"; then
    echo "ERROR: $(basename $f) missing WHEN section"
  fi
  if ! grep -qiE "^#+.*(WHAT|Deliverable|Output|Outcome)" "$f"; then
    echo "ERROR: $(basename $f) missing WHAT section"
  fi
done
```

---

### CORPUS-12: REQ Coverage

**Purpose**: Verify implementation approach covers all requirements

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| REQ references | Each IMPL references covered REQs |
| Coverage gaps | No orphaned REQs without IMPL |

---

### CORPUS-13: Dependency Tracking

**Purpose**: Verify implementation dependencies are documented

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| External dependencies | Third-party libraries/services listed |
| Internal dependencies | Cross-team dependencies documented |
| Blocking items | Blockers identified and tracked |

---

### CORPUS-14: SPEC-Ready Score Threshold

**Purpose**: Verify IMPL documents meet SPEC-Ready threshold

**Severity**: Warning

**Threshold**: All IMPL files should have SPEC-Ready Score ≥85%

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference | CORPUS-02 |
| CORPUS-E004 | Duplicate element ID | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Missing WHO section | CORPUS-11 |
| CORPUS-E012 | Missing WHEN section | CORPUS-11 |
| CORPUS-E013 | Missing WHAT section | CORPUS-11 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Index out of sync | CORPUS-04 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W009 | Resource specification incomplete | CORPUS-09 |
| CORPUS-W012 | REQ coverage gap | CORPUS-12 |
| CORPUS-W013 | Missing dependency documentation | CORPUS-13 |
| CORPUS-W014 | SPEC-Ready Score below 85% | CORPUS-14 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_impl_corpus.sh docs/IMPL

# With verbose output
./scripts/validate_impl_corpus.sh docs/IMPL --verbose
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
- [x] **CORPUS-05**: ~~Inter-IMPL cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex approaches
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate element IDs
- [ ] **CORPUS-09**: Resource specifications complete
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All IMPL follow WHO-WHEN-WHAT structure
- [ ] **CORPUS-12**: REQ coverage complete
- [ ] **CORPUS-13**: Dependencies documented
- [ ] **CORPUS-14**: All IMPL have SPEC-Ready Score ≥85%

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-impl-corpus.yml
name: IMPL Corpus Validation

on:
  push:
    paths:
      - 'docs/08_IMPL/**/*.md'
  pull_request:
    paths:
      - 'docs/08_IMPL/**/*.md'

jobs:
  validate-impl-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate IMPL Corpus
        run: |
          chmod +x ./scripts/validate_impl_corpus.sh
          ./scripts/validate_impl_corpus.sh docs/IMPL
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: impl-validation-report
          path: tmp/impl_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# IMPL corpus validation on staged IMPL files
if git diff --cached --name-only | grep -q "^docs/08_IMPL/"; then
  echo "Running IMPL corpus validation..."
  ./scripts/validate_impl_corpus.sh docs/IMPL --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ IMPL corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ IMPL corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-impl:
	@echo "Validating IMPL corpus..."
	@./scripts/validate_impl_corpus.sh docs/IMPL

validate-impl-verbose:
	@./scripts/validate_impl_corpus.sh docs/IMPL --verbose

# Include in combined validation target (optional layer)
validate-all-with-optional: validate-all validate-impl validate-ctr
	@echo "All corpus validations including optional layers complete"
```

### Integration with SPEC Layer Gate

IMPL corpus validation should pass before creating SPEC documents (when IMPL layer is enabled):

```bash
# Pre-SPEC gate check (optional layer)
if [ -d "docs/IMPL" ] && [ "$(ls -A docs/IMPL 2>/dev/null)" ]; then
  ./scripts/validate_impl_corpus.sh docs/IMPL
  if [ $? -eq 0 ]; then
    echo "✓ IMPL corpus valid - ready for SPEC layer creation"
  else
    echo "❌ Fix IMPL corpus errors before proceeding to SPEC layer"
    exit 1
  fi
fi
```

---

## References

- [IMPL_VALIDATION_RULES.md](./IMPL_VALIDATION_RULES.md) - Individual file validation
- [IMPL-TEMPLATE.md](./IMPL-TEMPLATE.md) - IMPL document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
