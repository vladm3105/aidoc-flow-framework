# IPLAN Corpus Validation Rules

## Document Control

| Field | Value |
|-------|-------|
| Document ID | IPLAN_CORPUS_VALIDATION |
| Version | 1.0 |
| Created | 2026-01-04 |
| Purpose | Quality gate for complete IPLAN corpus |
| Trigger | Run after ALL IPLAN files are complete |
| Scope | Entire IPLAN corpus validation |
| Layer | Layer 12 → Code Implementation transition gate |

## Overview

This document defines **corpus-level validation rules** that run AFTER all IPLAN (Implementation Plans) files are created but BEFORE code implementation begins. IPLAN documents provide session-based bash command execution plans derived from TASKS.

### Validation Hierarchy

| Validation Type | When It Runs | Scope | File |
|-----------------|--------------|-------|------|
| **Individual IPLAN Validation** | After each IPLAN creation | Single file | `IPLAN_VALIDATION_RULES.md` |
| **Corpus Validation** | After ALL IPLAN complete | Entire IPLAN set | This document |

### Workflow Position

```
Individual IPLAN Creation → IPLAN_VALIDATION_RULES.md (per-file)
        ↓
All IPLAN Complete
        ↓
IPLAN_CORPUS_VALIDATION.md (corpus-level) ← Quality Gate
        ↓
PASS → Begin Code Implementation
FAIL → Fix issues, re-run corpus validation
```

### IPLAN Format

IPLAN documents use Markdown format with bash command blocks:
```
docs/IPLAN/
├── IPLAN-NNN_{name}.md    # Implementation plan
└── IPLAN-000_index.md     # Registry/index file
```

---

## 1. Corpus Validation Checks

### CORPUS-01: Placeholder Text for Existing Documents

**Purpose**: Detect placeholder text that references documents which already exist

**Severity**: Error (blocking)

**Patterns to Detect**:
| Pattern | Description |
|---------|-------------|
| `(future IPLAN)` | IPLAN-NNN exists but still marked as future |
| `(when created)` | Document exists but reference not updated |
| `(to be defined)` | Item has been defined elsewhere |
| `(pending)` | Work completed but placeholder remains |
| `(TBD)` | Generic placeholder for defined content |

---

### CORPUS-02: Premature Downstream References

**Purpose**: IPLAN is Layer 12 (final documentation layer)

**Severity**: Info

**Note**: IPLAN is the final SDD documentation layer. There are no downstream documentation artifacts to reference prematurely. Code implementation follows IPLAN.

---

### CORPUS-03: Internal Document Consistency

**Purpose**: Detect numerical count mismatches within documents

**Severity**: Warning

**Common Patterns**:
| Claim | Reality | Error |
|-------|---------|-------|
| "5 sessions" | 6 sessions listed | Count mismatch |
| "3 commands" | 4 defined | Count mismatch |

---

### CORPUS-04: Index Synchronization

**Purpose**: Verify IPLAN index file reflects actual file states

**Severity**: Warning

**Index File Pattern**: `IPLAN-000_index.md` or `IPLAN-*_index.md`

**Checks**:
| Check | Description |
|-------|-------------|
| No stale "Planned" status | Files marked "Planned" that actually exist |
| Complete coverage | All existing IPLAN files listed in index |

---

### CORPUS-05: Inter-IPLAN Cross-Linking (DEPRECATED)

**Status**: Deprecated

**Reason for Deprecation**: Per SDD traceability rules, document name references are valid and sufficient for traceability.

---

### CORPUS-06: Visualization Coverage

**Purpose**: Verify diagrams exist for complex execution flows

**Severity**: Info

**Recommended Diagrams**:
| IPLAN Type | Recommended Diagrams |
|------------|---------------------|
| Multi-session | Session flow diagram |
| Dependencies | Execution sequence diagram |
| State management | State transition diagram |

---

### CORPUS-07: Glossary Consistency

**Purpose**: Ensure consistent terminology across all IPLAN files

**Severity**: Warning

---

### CORPUS-08: IPLAN ID Uniqueness

**Purpose**: No duplicate IPLAN IDs across the corpus

**Severity**: Error

**IPLAN ID Format**: `IPLAN-NNN` (document-level, dash notation)

---

### CORPUS-09: Session Numbering Consistency

**Purpose**: Validate session numbering is consistent

**Severity**: Warning

**Valid Session Formats**:
| Format | Example |
|--------|---------|
| Session N | `Session 1`, `Session 2` |
| Phase N | `Phase 1`, `Phase 2` |
| Step N | `Step 1`, `Step 2` |

---

### CORPUS-10: File Size Compliance

**Purpose**: Ensure documents don't exceed token limits

**Severity**: Warning at 600 lines, Error at 1200 lines

---

### CORPUS-11: Bash Command Syntax Validation

**Purpose**: Verify bash commands are syntactically valid

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| Code blocks present | `bash` fenced code blocks exist |
| Basic syntax | Commands don't have obvious syntax errors |
| No dangerous commands | No `rm -rf /` or similar |

**Validation Logic**:
```bash
# Check for bash code blocks
for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
  bash_blocks=$(grep -c '```bash' "$f" 2>/dev/null || echo 0)
  if [[ $bash_blocks -eq 0 ]]; then
    echo "WARNING: $(basename $f) has no bash code blocks"
  fi
done
```

---

### CORPUS-12: TASKS Coverage

**Purpose**: Verify all tasks have corresponding implementation plans

**Severity**: Error

**Checks**:
| Check | Description |
|-------|-------------|
| TASKS references | Each IPLAN references implemented TASKS |
| Coverage gaps | No orphaned TASKS without IPLAN |
| Traceability matrix | All TASKS accounted for |

**Validation Logic**:
```bash
# Check for TASKS references in IPLAN files
for f in "$IPLAN_DIR"/IPLAN-[0-9]*_*.md; do
  tasks_refs=$(grep -coE "TASKS-[0-9]+" "$f" 2>/dev/null || echo 0)
  if [[ $tasks_refs -eq 0 ]]; then
    echo "WARNING: $(basename $f) has no TASKS references"
  fi
done
```

---

### CORPUS-13: Session State Management

**Purpose**: Verify session state is properly documented

**Severity**: Warning

**Required Elements**:
| Element | Description |
|---------|-------------|
| Prerequisites | What must exist before session |
| Inputs | Required inputs/data for session |
| Outputs | Expected outputs after session |
| Success criteria | How to verify session success |

---

### CORPUS-14: Rollback Procedure Specification

**Purpose**: Verify rollback procedures are documented

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Rollback section | Section documenting rollback steps |
| Recovery commands | Commands to undo changes |
| Checkpoint markers | Points where rollback is possible |

---

### CORPUS-15: Cumulative Traceability Compliance

**Purpose**: Verify IPLAN includes cumulative upstream tags

**Severity**: Error

**Required Upstream Tags** (9 cumulative):
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
| `@tasks` | 11 | Task Breakdown |

**Note**: Optional layers (IMPL@8, CTR@9) included if present

---

### CORPUS-16: Environment Variable Documentation

**Purpose**: Verify environment variables are documented

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Env var listing | Environment variables listed |
| Default values | Defaults specified where applicable |
| Required vs optional | Clearly marked |

---

### CORPUS-17: Dependency Installation Commands

**Purpose**: Verify dependency installation is documented

**Severity**: Warning

**Checks**:
| Check | Description |
|-------|-------------|
| Package managers | pip, npm, apt, etc. commands present |
| Version pinning | Versions specified |
| Virtual environment | venv/conda setup documented |

---

## 2. Error Codes

### Error Codes (Blocking)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-E001 | Placeholder text for existing document | CORPUS-01 |
| CORPUS-E004 | Duplicate IPLAN ID | CORPUS-08 |
| CORPUS-E005 | File exceeds 1,200 lines | CORPUS-10 |
| CORPUS-E011 | No bash command blocks | CORPUS-11 |
| CORPUS-E012 | TASKS without IPLAN coverage | CORPUS-12 |
| CORPUS-E015 | Missing cumulative traceability | CORPUS-15 |

### Warning Codes (Recommended)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-W001 | Internal count mismatch | CORPUS-03 |
| CORPUS-W003 | Glossary term inconsistency | CORPUS-07 |
| CORPUS-W004 | Index out of sync | CORPUS-04 |
| CORPUS-W005 | File exceeds 600 lines | CORPUS-10 |
| CORPUS-W009 | Session numbering inconsistency | CORPUS-09 |
| CORPUS-W013 | Missing session state documentation | CORPUS-13 |
| CORPUS-W014 | Missing rollback procedures | CORPUS-14 |
| CORPUS-W016 | Missing environment variable docs | CORPUS-16 |
| CORPUS-W017 | Missing dependency installation | CORPUS-17 |

### Info Codes (Advisory)

| Code | Description | Check |
|------|-------------|-------|
| CORPUS-I001 | No Mermaid diagrams found | CORPUS-06 |
| CORPUS-I002 | Final documentation layer | CORPUS-02 |

---

## 3. Automated Script Usage

### Running Corpus Validation

```bash
# Full corpus validation
./scripts/validate_iplan_corpus.sh docs/IPLAN

# With verbose output
./scripts/validate_iplan_corpus.sh docs/IPLAN --verbose
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

### Pre-Implementation Gate Checklist

- [ ] **CORPUS-01**: No placeholder text for existing documents
- [x] **CORPUS-02**: ~~No premature downstream references~~ (N/A - final layer)
- [ ] **CORPUS-03**: Internal counts match actual items
- [ ] **CORPUS-04**: Index synchronized with actual files
- [x] **CORPUS-05**: ~~Inter-IPLAN cross-links present~~ (deprecated)
- [ ] **CORPUS-06**: Diagrams present for complex execution flows
- [ ] **CORPUS-07**: Terminology consistent across corpus
- [ ] **CORPUS-08**: No duplicate IPLAN IDs
- [ ] **CORPUS-09**: Session numbering consistent
- [ ] **CORPUS-10**: All files under size limits
- [ ] **CORPUS-11**: All files have bash command blocks
- [ ] **CORPUS-12**: All TASKS have IPLAN coverage
- [ ] **CORPUS-13**: Session state properly documented
- [ ] **CORPUS-14**: Rollback procedures specified
- [ ] **CORPUS-15**: Cumulative traceability complete (9 tags)
- [ ] **CORPUS-16**: Environment variables documented
- [ ] **CORPUS-17**: Dependency installation documented

---

## 5. CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-iplan-corpus.yml
name: IPLAN Corpus Validation

on:
  push:
    paths:
      - 'docs/IPLAN/**/*.md'
  pull_request:
    paths:
      - 'docs/IPLAN/**/*.md'

jobs:
  validate-iplan-corpus:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate IPLAN Corpus
        run: |
          chmod +x ./scripts/validate_iplan_corpus.sh
          ./scripts/validate_iplan_corpus.sh docs/IPLAN
        continue-on-error: false

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: iplan-validation-report
          path: tmp/iplan_validation_*.log
          retention-days: 7
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit (add to existing hook)

# IPLAN corpus validation on staged IPLAN files
if git diff --cached --name-only | grep -q "^docs/IPLAN/"; then
  echo "Running IPLAN corpus validation..."
  ./scripts/validate_iplan_corpus.sh docs/IPLAN --errors-only
  if [ $? -ne 0 ]; then
    echo "❌ IPLAN corpus validation failed. Fix errors before committing."
    exit 1
  fi
  echo "✓ IPLAN corpus validation passed"
fi
```

### Makefile Integration

```makefile
# Add to project Makefile

validate-iplan:
	@echo "Validating IPLAN corpus..."
	@./scripts/validate_iplan_corpus.sh docs/IPLAN

validate-iplan-verbose:
	@./scripts/validate_iplan_corpus.sh docs/IPLAN --verbose

# Include in combined validation target
validate-all: validate-brd validate-prd validate-ears validate-bdd validate-adr validate-sys validate-req validate-spec validate-tasks validate-iplan
	@echo "All corpus validations complete"
```

### Integration with Implementation Gate

IPLAN corpus validation should pass before starting implementation:

```bash
# Pre-Implementation gate check
./scripts/validate_iplan_corpus.sh docs/IPLAN
if [ $? -eq 0 ]; then
  echo "✓ IPLAN corpus valid - ready for implementation"
else
  echo "❌ Fix IPLAN corpus errors before starting implementation"
  exit 1
fi
```

---

## References

- [IPLAN_VALIDATION_RULES.md](./IPLAN_VALIDATION_RULES.md) - Individual file validation
- [IPLAN-TEMPLATE.md](./IPLAN-TEMPLATE.md) - IPLAN document template
- [ID_NAMING_STANDARDS.md](../ID_NAMING_STANDARDS.md) - Element ID format
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
