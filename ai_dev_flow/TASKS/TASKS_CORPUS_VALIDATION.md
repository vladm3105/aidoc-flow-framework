# TASKS Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | TASKS_CORPUS_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete TASKS corpus |
| Trigger | Run after ALL TASKS files are complete |
| Scope | Entire TASKS corpus validation |
| Layer | Layer 11 → Layer 12 transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all TASKS (Task Breakdown) files are created but BEFORE IPLAN creation begins. TASKS documents decompose SPEC into AI-structured TODO tasks with dependency tracking.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual TASKS Validation** | After each TASKS creation | Single file | `TASKS_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL TASKS complete | Entire TASKS set | This document |

### Workflow Position

```
Individual TASKS Creation → TASKS_VALIDATION_RULES.md (per-file)
        ↓
All TASKS Complete
        ↓
TASKS_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin IPLAN Creation (Layer 12)
FAIL → Fix issues, re-run corpus validation
```

### TASKS Format

TASKS documents use Markdown format with structured task entries:
```
docs/TASKS/
├── TASKS-NN_{name}.md     # Task breakdown document
└── TASKS-000_index.md     # Registry/index file
```

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future TASKS)` | TASKS-NN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

---

### CORPUS-02: Premature Downstream References

**Purpose**: Detect references to non-existent Layer 12+ artifacts

**Severity**: Error (blocking)

**Rationale**: TASKS is Layer 11. It should NOT reference specific numbered IPLAN documents that don't exist yet.

**Patterns to Flag**:
| Pattern | Layer | Issue |
|---------|-------|-------|
| `IPLAN-NN` | 12 | IPLANs don't exist during TASKS creation |

**Allowed Patterns** (generic references):
- "This will inform IPLAN development"
- "Downstream execution will..."
- "See future implementation plan"

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 tasks" | 6 tasks listed | Count mismatch |
| "3 dependencies" | 4 defined | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify TASKS index file reflects actual file states

**Severity**: Warning

**Index File Pattern**: `TASKS-000_index.md` or `TASKS-*_index.md`

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing TASKS files listed in index |

---

### CORPUS-05: Inter-TASKS Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for task dependencies

**Severity**: Info

**Recommended Diagrams**:
| TASKS Type | Recommended Diagrams |
|------------|---------------------|
| Sequential tasks | Flowchart |
| Parallel tasks | Gantt chart |
| Dependencies | Dependency graph |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all TASKS files

**Severity**: Warning

---

### CORPUS-08: Task ID Uniqueness

**Purpose**: No duplicate task IDs across the TASKS corpus

**Severity**: Error

**Task ID Format**: `TASKS.NN.TT.SS` (dot notation for elements)

---

### CORPUS-09: Priority Format Consistency

**Purpose**: Validate task priority specifications are consistent

**Severity**: Warning

**Valid Priority Formats**:
| Format | Values |
|--------|--------|
| P-number | `P0`, `P1`, `P2`, `P3` |
| Text | `Critical`, `High`, `Medium`, `Low` |
| Numeric | `1`, `2`, `3`, `4` |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

---

### CORPUS-11: Task Dependency DAG Validation

**Purpose**: Verify task dependencies form a valid DAG (no cycles)

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| No circular dependencies | Task A → B → C → A is invalid |
| Valid dependency references | All referenced tasks exist |
| Reachable start | At least one task has no dependencies |

**Validation Logic**:
```bash
# Extract dependency relationships
# Check for cycles using topological sort
# Flag any circular dependency chains
```

---

### CORPUS-12: SPEC Coverage

**Purpose**: Verify all specifications have corresponding tasks

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| SPEC references | Each TASKS references implemented SPECs |
| Coverage gaps | No orphaned SPECs without TASKS |
| Traceability matrix | All SPECs accounted for |

**Validation Logic**:
```bash
# Check for SPEC references in TASKS files
for f in "$TASKS_DIR"/TASKS-[0-9]*_*.md; do
  spec_refs=$(grep -coE "SPEC-[0-9]+" "$f" 2>/dev/null || echo 0)
  if [[ $spec_refs -eq 0 ]]; then
    echo "WARNING: $(basename $f) has no SPEC references"
  fi
done
```

---

### CORPUS-13: Implementation Contract References

**Purpose**: Verify implementation contracts are properly referenced

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| `@icon` tags | Implementation contracts referenced |
| Contract definitions | Contracts defined in Implementation Contracts section |
| Provider/consumer roles | `@icon-role` specified where applicable |

**Contract Types**:
| Type | Description |
|------|-------------|
| Protocol Interface | `typing.Protocol` signatures |
| Exception Hierarchy | Typed exception classes |
| State Machine | Enum states with transitions |
| Data Model | Pydantic/TypedDict schemas |
| DI Interface | ABC classes for dependency injection |

---

### CORPUS-14: Task Status Tracking

**Purpose**: Verify task status fields are properly defined

**Severity**: Warning

**Valid Status Values**:
| Status | Description |
|--------|-------------|
| `pending` | Task not started |
| `in_progress` | Currently being worked |
| `blocked` | Waiting on dependency |
| `completed` | Task finished |
| `cancelled` | Task no longer needed |

---

### CORPUS-15: Cumulative Traceability Compliance

**Purpose**: Verify TASKS includes cumulative upstream tags

**Severity**: Error

**Required Upstream Tags** (8 cumulative):
| Tag | Layer | Description |
|-----|-------|-------------|
| `@brd` | 1 | Business Requirements |
| `@prd` | 2 | Product Requirements |
| `@ears` | 3 | EARS Requirements |
| `@bdd` | 4 | BDD Scenarios |
| `@adr` | 5 | Architecture Decisions |
| `@sys` | 6 | System Requirements |
| `@req` | 7 | Atomic Requirements |
| `@spec` | 10 | Technical Specifications |

**Note**: Optional layers (IMPL@8, CTR@9) included if present

---

### CORPUS-16: Effort Estimation Presence

**Purpose**: Verify tasks include effort estimates

**Severity**: Warning

**Valid Estimation Formats**:
| Format | Example |
|--------|---------|
| Story points | `SP: 3`, `Story Points: 5` |
| T-shirt size | `Size: M`, `Effort: L` |
| Complexity | `Complexity: 3/5` |

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E002 | Premature downstream reference | CORPUS-02 |
| CORPUS-E004 | Duplicate task ID | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | Circular dependency detected | CORPUS-11 |
| CORPUS-E012 | SPEC without TASKS coverage | CORPUS-12 |
| CORPUS-E015 | Missing cumulative traceability | CORPUS-15 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Index out of sync | CORPUS-04 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W009 | Priority format inconsistency | CORPUS-09 |
| CORPUS-W013 | Missing implementation contract | CORPUS-13 |
| CORPUS-W014 | Missing task status | CORPUS-14 |
| CORPUS-W016 | Missing effort estimate | CORPUS-16 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_tasks_corpus.sh docs/TASKS

# With verbose output
./scripts/validate_tasks_corpus.sh docs/TASKS --verbose
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

### Pre-IPLAN Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [ ] **CORPUS-02**: No premature downstream references
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-TASKS cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex dependencies
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate task IDs
- [ ] **CORPUS-09**: Priority formats consistent
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: No circular dependencies (valid DAG)
- [ ] **CORPUS-12**: All SPECs have TASKS coverage
- [ ] **CORPUS-13**: Implementation contracts referenced
- [ ] **CORPUS-14**: Task status fields present
- [ ] **CORPUS-15**: Cumulative traceability complete (8 tags)
- [ ] **CORPUS-16**: Effort estimates present

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-tasks-corpus.yml
name: TASKS Corpus Validation

on:
  push:
    paths:
      - 'docs/TASKS/**/*.md'
  pull_request:
    paths:
      - 'docs/TASKS/**/*.md'

jobs:
  validate-tasks-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate TASKS Corpus
        run: |
          chmod +x ./scripts/validate_tasks_corpus.sh
          ./scripts/validate_tasks_corpus.sh docs/TASKS
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: tasks-validation-report
          path: tmp/tasks_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# TASKS corpus validation on staged TASKS files
if git diff --cached --name-only | grep -q "^docs/TASKS/"; then
  echo "Running TASKS corpus validation..."
  ./scripts/validate_tasks_corpus.sh docs/TASKS --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ TASKS corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ TASKS corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-tasks:
	@echo "Validating TASKS corpus..."
	@./scripts/validate_tasks_corpus.sh docs/TASKS

validate-tasks-verbose:
	@./scripts/validate_tasks_corpus.sh docs/TASKS --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req validate-spec validate-tasks validate-iplan
	@echo "All corpus validations complete"
```

### Integration with IPLAN Layer Gate

TASKS corpus validation should pass before creating IPLAN documents:

```bash
# Pre-IPLAN gate check
./scripts/validate_tasks_corpus.sh docs/TASKS
if [ $? -eq 0 ]; then
  echo "✓ TASKS corpus valid - ready for IPLAN layer creation"
else
  echo "❌ Fix TASKS corpus errors before proceeding to IPLAN layer"
  exit 1
fi
```

---

## References

- [TASKS_VALIDATION_RULES.md](./TASKS_VALIDATION_RULES.md) - Individual file validation
- [TASKS-TEMPLATE.md](./TASKS-TEMPLATE.md) - TASKS document template
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](./IMPLEMENTATION_CONTRACTS_GUIDE.md) - Contract patterns
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
