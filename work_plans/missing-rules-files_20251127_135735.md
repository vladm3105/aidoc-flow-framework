# Implementation Plan - Create Missing CREATION_RULES and VALIDATION_RULES Files

**Created**: 2025-11-27 13:57:35 EST
**Updated**: 2025-11-27 (Corrected after detailed exploration)
**Status**: Ready for Implementation

## Objective

Create 9 missing CREATION_RULES and VALIDATION_RULES files plus 5 validation scripts for document types in the ai_dev_flow framework. Also fix one naming inconsistency.

## Context

Review of all 13 document types in `/opt/data/docs_flow_framework/ai_dev_flow/` revealed gaps in supporting documentation. Each document type should have:

- TEMPLATE file (all have this)
- CREATION_RULES.md
- VALIDATION_RULES.md

---

## Corrected Gap Analysis

### Previous Analysis vs Actual State

| Document Type | Original Analysis | Actual State | Correction |
|---------------|-------------------|--------------|------------|
| ADR | Complete | Complete | ✓ |
| BDD | Complete | Complete | ✓ |
| BRD | Complete | Complete | ✓ |
| CTR | Missing both | Missing both | ✓ |
| EARS | Complete | Complete | ✓ |
| **ICON** | **Missing both** | **Has CREATION, missing VALIDATION** | **Corrected** |
| IMPL | Missing both | Missing both | ✓ |
| IPLAN | Missing both | Missing both | ✓ |
| PRD | Complete | Complete | ✓ |
| REQ | Complete | Complete (naming issue) | Note below |
| SPEC | Complete | Complete | ✓ |
| SYS | Complete | Complete | ✓ |
| TASKS | Missing both | Missing both | ✓ |

### Naming Inconsistency Found

- `REQ-VALIDATION-RULES.md` uses hyphens
- All other validation rules use underscores: `*_VALIDATION_RULES.md`
- **Decision**: Rename to `REQ_VALIDATION_RULES.md` for consistency

### Complete Document Types (9/13)

- ADR, BDD, BRD, EARS, ICON (creation only), PRD, REQ, SPEC, SYS

### Incomplete Document Types (4/13 missing both, 1/13 missing validation only)

| Type | Layer | Missing Files |
|------|-------|---------------|
| CTR | 9 | CTR_CREATION_RULES.md, CTR_VALIDATION_RULES.md |
| ICON | 11 | ICON_VALIDATION_RULES.md (has CREATION_RULES) |
| IMPL | 8 | IMPL_CREATION_RULES.md, IMPL_VALIDATION_RULES.md |
| IPLAN | 12 | IPLAN_CREATION_RULES.md, IPLAN_VALIDATION_RULES.md |
| TASKS | 11 | TASKS_CREATION_RULES.md, TASKS_VALIDATION_RULES.md |

---

## Task List (15 total)

### Pre-Implementation: Naming Fix

- [ ] Rename `REQ-VALIDATION-RULES.md` → `REQ_VALIDATION_RULES.md`
- [ ] Update any internal references to the old filename

### Phase 1: High Priority Rules Files (5 files)

- [ ] Create CTR_CREATION_RULES.md (Layer 9 - API Contracts)
- [ ] Create CTR_VALIDATION_RULES.md
- [ ] Create TASKS_CREATION_RULES.md (Layer 11 - Code Generation Plans)
- [ ] Create TASKS_VALIDATION_RULES.md
- [ ] Create ICON_VALIDATION_RULES.md (Layer 11 - Implementation Contracts)

### Phase 2: Medium-High Priority Rules Files (2 files)

- [ ] Create IMPL_CREATION_RULES.md (Layer 8 - Project Management)
- [ ] Create IMPL_VALIDATION_RULES.md

### Phase 3: Medium Priority Rules Files (2 files)

- [ ] Create IPLAN_CREATION_RULES.md (Layer 12 - Session Execution Plans)
- [ ] Create IPLAN_VALIDATION_RULES.md

### Phase 4: Validation Scripts (5 scripts)

- [ ] Create scripts/validate_ctr.sh
- [ ] Create scripts/validate_icon.sh
- [ ] Create scripts/validate_impl.sh
- [ ] Create scripts/validate_iplan.sh
- [ ] Create scripts/validate_tasks.sh

---

## Implementation Guide

### Prerequisites

Reference files to read before creating each file:

1. The corresponding TEMPLATE file for that document type
2. The README.md in that directory
3. Pattern examples:
   - `REQ/REQ_CREATION_RULES.md`
   - `REQ/REQ_VALIDATION_RULES.md` (after rename)
   - `ICON/ICON_CREATION_RULES.md`
   - `SPEC/SPEC_VALIDATION_RULES.md`

### File Locations

All rules files go in: `/opt/data/docs_flow_framework/ai_dev_flow/{TYPE}/`

```text
ai_dev_flow/CTR/CTR_CREATION_RULES.md
ai_dev_flow/CTR/CTR_VALIDATION_RULES.md
ai_dev_flow/ICON/ICON_VALIDATION_RULES.md
ai_dev_flow/IMPL/IMPL_CREATION_RULES.md
ai_dev_flow/IMPL/IMPL_VALIDATION_RULES.md
ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md
ai_dev_flow/IPLAN/IPLAN_VALIDATION_RULES.md
ai_dev_flow/TASKS/TASKS_CREATION_RULES.md
ai_dev_flow/TASKS/TASKS_VALIDATION_RULES.md
```

All scripts go in: `/opt/data/docs_flow_framework/ai_dev_flow/scripts/`

```text
ai_dev_flow/scripts/validate_ctr.sh
ai_dev_flow/scripts/validate_icon.sh
ai_dev_flow/scripts/validate_impl.sh
ai_dev_flow/scripts/validate_iplan.sh
ai_dev_flow/scripts/validate_tasks.sh
```

### Standard Structure for CREATION_RULES

Each CREATION_RULES.md should contain (10-12 sections):

1. YAML frontmatter with metadata tags
2. File Organization and Directory Structure
3. Document Structure (X Required sections)
4. Document Control Requirements
5. ID and Naming Standards
6. Artifact-Specific Principles
7. Traceability Requirements
8. Quality Gates
9. Business Rules and Validation
10. Quick Reference with validation commands

### Standard Structure for VALIDATION_RULES

Each VALIDATION_RULES.md should contain (5 major sections):

1. Overview and Validation Tiers table
2. Validation Checks (numbered CHECK 1, CHECK 2, etc.)
3. Error Fix Guide
4. Quick Reference
5. Common Mistakes

### Validation Check Format

````markdown
### CHECK N: [Check Name]

**Purpose**: [One-sentence description]
**Type**: Error | Warning | Info

**Requirements**: [Specific rules]

**Error Message**:

```text
❌ [Error text]
```

**Fix**:

1. [Step-by-step fix]
````

---

## Detailed File Specifications

### CTR (Layer 9 - API Contracts)

#### CTR_CREATION_RULES.md (~2,500 tokens)

- Dual-file structure (.md + .yaml)
- Synchronization rules between files
- Endpoint/function definition requirements
- Error code to HTTP status mapping

#### CTR_VALIDATION_RULES.md (~3,000 tokens)

- CHECK: Both files exist (.md AND .yaml)
- CHECK: ID consistency across files
- CHECK: YAML schema validity
- CHECK: Endpoint definitions complete
- CHECK: Error handling documented

### ICON (Layer 11 - Implementation Contracts)

#### ICON_VALIDATION_RULES.md (~2,000 tokens)

- CHECK: Bidirectional traceability (TASKS ↔ ICON)
- CHECK: Provider/consumer validation
- CHECK: mypy --strict compliance
- CHECK: Orphan detection (ICON with 0 references)
- CHECK: @icon-role tag validation

### IMPL (Layer 8 - Project Management)

#### IMPL_CREATION_RULES.md (~2,200 tokens)

- WHO-WHEN-WHAT focus (not HOW)
- Phase structure requirements
- Deliverable traceability
- Risk register format

#### IMPL_VALIDATION_RULES.md (~2,500 tokens)

- CHECK: No technical implementation details (scope guard)
- CHECK: Phase structure completeness
- CHECK: Deliverable traceability to CTR/SPEC/TASKS
- CHECK: Sign-off section validation

### IPLAN (Layer 12 - Session Execution)

#### IPLAN_CREATION_RULES.md (~2,200 tokens)

- Bash command block format
- Verification checkpoint format
- Parent TASKS reference
- BDD scenario mapping

#### IPLAN_VALIDATION_RULES.md (~2,500 tokens)

- CHECK: Bash command syntax validity
- CHECK: Verification checkpoints after each phase
- CHECK: Parent TASKS reference valid
- CHECK: BDD scenario mapping complete

### TASKS (Layer 11 - Code Generation)

#### TASKS_CREATION_RULES.md (~2,500 tokens)

- Traceability header format (@brd through @spec)
- Implementation Contracts section (8.1/8.2)
- Phase 0-4 structure
- Acceptance criteria requirements

#### TASKS_VALIDATION_RULES.md (~3,000 tokens)

- CHECK: Cumulative tags completeness (11 tags)
- CHECK: SPEC reference valid
- CHECK: Section 8.x contract validation (if N ≥ 3 dependencies)
- CHECK: Acceptance criteria count (≥15)
- CHECK: BDD scenario mapping with line numbers

---

## Validation Script Structure

Each script should follow this pattern:

```bash
#!/bin/bash
# validate_{type}.sh - Validates {TYPE} documents
# Usage: ./scripts/validate_{type}.sh <filename.md>

set -e

FILE="$1"
ERRORS=0
WARNINGS=0

# Tier 1: Errors (exit 1)
# Tier 2: Warnings (exit 0)
# Tier 3: Info (exit 0)

# CHECK 1: File exists and is readable
if [[ ! -f "$FILE" ]]; then
    echo "❌ CHECK 1: File not found: $FILE"
    exit 1
fi

# CHECK 2: YAML frontmatter valid
# CHECK 3: Required sections present
# ... type-specific checks

# Summary
if [[ $ERRORS -gt 0 ]]; then
    echo "❌ FAILED: $ERRORS error(s), $WARNINGS warning(s)"
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo "⚠️  PASSED WITH WARNINGS: $WARNINGS warning(s)"
    exit 0
else
    echo "✅ PASSED: All validation checks passed"
    exit 0
fi
```

### Script Reference Files

- `/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_brd_template.sh`

---

## Verification

After creating each file:

```bash
# Verify file exists
ls -la /opt/data/docs_flow_framework/ai_dev_flow/{TYPE}/{TYPE}_*RULES.md

# Check YAML frontmatter is valid
head -20 /opt/data/docs_flow_framework/ai_dev_flow/{TYPE}/{TYPE}_*RULES.md
```

After all files created:

```bash
# Verify all document types now have complete rules
for type in ADR BDD BRD CTR EARS ICON IMPL IPLAN PRD REQ SPEC SYS TASKS; do
  echo "=== $type ==="
  ls /opt/data/docs_flow_framework/ai_dev_flow/$type/*TEMPLATE* 2>/dev/null || echo "Missing TEMPLATE"
  ls /opt/data/docs_flow_framework/ai_dev_flow/$type/*CREATION_RULES* 2>/dev/null || echo "Missing CREATION_RULES"
  ls /opt/data/docs_flow_framework/ai_dev_flow/$type/*VALIDATION_RULES* 2>/dev/null || echo "Missing VALIDATION_RULES"
done

# Verify all scripts exist
ls -la /opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_*.sh
```

---

## References

- Pattern files:
  - `/opt/data/docs_flow_framework/ai_dev_flow/REQ/REQ_CREATION_RULES.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/REQ/REQ_VALIDATION_RULES.md` (after rename)
  - `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON_CREATION_RULES.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/SPEC/SPEC_VALIDATION_RULES.md`
- Plan file: `/home/ya/.claude/plans/toasty-forging-lemur.md`
- Framework guide: `/opt/data/docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
