---
name: doc-tspec-autopilot
description: Automated TSPEC generation from SPEC - generates test specifications for UTEST, ITEST, STEST, FTEST with TASKS-Ready scoring
tags:
  - sdd-workflow
  - layer-10-artifact
  - automation-workflow
  - shared-architecture
custom_fields:
  layer: 10
  artifact_type: TSPEC
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: automation-workflow
  upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
  downstream_artifacts: [TASKS]
  version: "2.1"
  last_updated: "2026-02-09"
---

# doc-tspec-autopilot

## Purpose

Automated **Test Specifications (TSPEC)** generation pipeline that processes SPEC documents to generate comprehensive test specifications for UTEST, ITEST, STEST, and FTEST with TASKS-Ready scoring.

**Layer**: 10

**Upstream**: SPEC (Layer 9)

**Downstream**: TASKS (Layer 11)

---

## Skill Dependencies

| Skill | Purpose | Phase |
|-------|---------|-------|
| `doc-naming` | Element ID format (TSPEC.NN.TT.SS, codes 40-43) | All Phases |
| `doc-spec-validator` | Validate SPEC TASKS-Ready score | Phase 2 |
| `doc-tspec` | TSPEC creation rules, test type structure | Phase 3 |
| `quality-advisor` | Real-time quality feedback | Phase 3 |
| `doc-tspec-validator` | Validation with TASKS-Ready scoring | Phase 4 |

---

## Workflow Overview

```mermaid
flowchart TD
    subgraph Phase1["Phase 1: SPEC Analysis"]
        A[Start] --> B[Read SPEC Documents]
        B --> C[Extract Methods]
        C --> D[Extract Interfaces]
        D --> E[Extract Data Models]
        E --> F[Catalog Test Targets]
    end

    subgraph Phase2["Phase 2: Test Coverage Planning"]
        F --> G[Check SPEC TASKS-Ready Score]
        G --> H{Score >= 90%?}
        H -->|No| I[Flag SPEC Issues]
        I --> J{Auto-Fixable?}
        J -->|Yes| K[Fix SPEC Issues]
        K --> G
        J -->|No| L[Abort - Manual Fix Required]
        H -->|Yes| M[Plan Test Coverage]
        M --> N[Allocate Test Types]
    end

    subgraph Phase3["Phase 3: TSPEC Generation"]
        N --> O[Generate UTEST Specs]
        O --> P[Generate ITEST Specs]
        P --> Q[Generate STEST Specs]
        Q --> R[Generate FTEST Specs]
        R --> S[quality-advisor: Real-time Feedback]
        S --> T[Build Coverage Matrix]
        T --> U[Add Traceability Tags]
        U --> V[Write TSPEC Files]
    end

    subgraph Phase4["Phase 4: TSPEC Validation"]
        V --> W[Run doc-tspec-validator]
        W --> X{TASKS-Ready >= 90%?}
        X -->|No| Y[Auto-Fix TSPEC Issues]
        Y --> Z[Re-validate TSPEC]
        Z --> X
        X -->|Yes| AA[Mark TSPEC Validated]
    end

    subgraph Phase5["Phase 5: Final Review"]
        AA --> AB[Verify Coverage Matrix]
        AB --> AC[Check All Types Present]
        AC --> AD[Update Traceability Matrix]
        AD --> AE[Generate Summary Report]
    end

    AE --> AF[Complete]
    L --> AG[Exit with Error]
```

---

## Test Types

| Type | Code | Purpose | Target |
|------|------|---------|--------|
| **UTEST** | 40 | Unit tests | Individual functions/methods |
| **ITEST** | 41 | Integration tests | Component interactions |
| **STEST** | 42 | Smoke tests | Critical path verification |
| **FTEST** | 43 | Functional tests | End-to-end workflows |

---

## TSPEC Structure

```
docs/10_TSPEC/
├── TSPEC-01_authentication/
│   ├── TSPEC-01.0_index.md
│   ├── TSPEC-01.1_utest.md      # Unit tests
│   ├── TSPEC-01.2_itest.md      # Integration tests
│   ├── TSPEC-01.3_stest.md      # Smoke tests
│   └── TSPEC-01.4_ftest.md      # Functional tests
└── TSPEC-01_authentication.md    # Redirect stub
```

---

## Coverage Matrix Format

| SPEC Element | UTEST | ITEST | STEST | FTEST | Coverage |
|--------------|-------|-------|-------|-------|----------|
| SPEC.01.28.01 | TSPEC.01.40.01 | TSPEC.01.41.01 | TSPEC.01.42.01 | - | 75% |
| SPEC.01.28.02 | TSPEC.01.40.02 | TSPEC.01.41.02 | - | TSPEC.01.43.01 | 75% |

---

## Element ID Format

| Test Type | Code | Pattern | Example |
|-----------|------|---------|---------|
| UTEST | 40 | TSPEC.NN.40.SS | TSPEC.01.40.01 |
| ITEST | 41 | TSPEC.NN.41.SS | TSPEC.01.41.01 |
| STEST | 42 | TSPEC.NN.42.SS | TSPEC.01.42.01 |
| FTEST | 43 | TSPEC.NN.43.SS | TSPEC.01.43.01 |

---

## Cumulative Tags (8 Required)

```markdown
@brd: BRD.NN.TT.SS
@prd: PRD.NN.TT.SS
@ears: EARS.NN.TT.SS
@bdd: BDD.NN.TT.SS
@adr: ADR-NN
@sys: SYS.NN.TT.SS
@req: REQ.NN.TT.SS
@spec: SPEC.NN.TT.SS
@ctr: CTR.NN.TT.SS  # Optional
```

---

## Configuration

### Default Configuration

```yaml
tspec_autopilot:
  version: "1.0"

  scoring:
    tasks_ready_min: 90
    strict_mode: false

  execution:
    max_parallel: 3        # HARD LIMIT - do not exceed
    chunk_size: 3          # Documents per chunk
    pause_between_chunks: true
    auto_fix: true
    continue_on_error: false
    timeout_per_spec: 180  # seconds

  output:
    structure: sectioned  # 4 test type files per TSPEC
    report_format: markdown

  validation:
    skip_validation: false
    fix_iterations_max: 3

  test_types:
    utest: true
    itest: true
    stest: true
    ftest: true
```

---

## Execution Modes

### Mode 1: Generate Mode (Default)

Standard TSPEC generation from SPEC documents (see Workflow Overview above).

### Mode 2: Review Mode (v2.1)

Validate existing TSPEC documents without modification. Generates quality report with actionable recommendations.

**Command**:
```bash
# Review single TSPEC
/doc-tspec-autopilot TSPEC-01 --review

# Review all TSPEC in directory
/doc-tspec-autopilot docs/10_TSPEC/ --review --all

# Review with detailed report
/doc-tspec-autopilot TSPEC-01 --review --verbose
```

**Review Process**:

```mermaid
flowchart TD
    A[Input: TSPEC Document] --> B[Load TSPEC Content]
    B --> C[Validate Test Structure]
    C --> D[Check TASKS-Ready Score]
    D --> E[Verify All 4 Test Types]
    E --> F[Validate Coverage Matrix]
    F --> G[Check Element IDs]
    G --> H[Verify Cumulative Tags]
    H --> I[Generate Review Report]
    I --> J{Issues Found?}
    J -->|Yes| K[Categorize Issues]
    K --> L[Generate Fix Recommendations]
    L --> M[Output Review Report]
    J -->|No| M
```

**Review Report Template**:

```markdown
# TSPEC Review Report: TSPEC-NN_{slug}

## Summary
- **TASKS-Ready Score**: NN% (✅/🟡/❌)
- **Total Issues**: N (E errors, W warnings)
- **Auto-Fixable**: N issues
- **Manual Review**: N issues

## Test Type Coverage
| Type | File | Tests | Coverage | Status |
|------|------|-------|----------|--------|
| UTEST | TSPEC-NN.1_utest.md | N | NN% | ✅/🟡/❌ |
| ITEST | TSPEC-NN.2_itest.md | N | NN% | ✅/🟡/❌ |
| STEST | TSPEC-NN.3_stest.md | N | NN% | ✅/🟡/❌ |
| FTEST | TSPEC-NN.4_ftest.md | N | NN% | ✅/🟡/❌ |

## Score Breakdown
| Category | Score | Max | Status |
|----------|-------|-----|--------|
| Test Type Completeness | NN | 25 | ✅/🟡/❌ |
| Coverage Matrix | NN | 20 | ✅/🟡/❌ |
| SPEC Alignment | NN | 20 | ✅/🟡/❌ |
| Element ID Format | NN | 15 | ✅/🟡/❌ |
| Traceability Tags | NN | 10 | ✅/🟡/❌ |
| Test Assertions | NN | 10 | ✅/🟡/❌ |

## Issues by Category

### Auto-Fixable Issues
| Issue | Location | Fix Action |
|-------|----------|------------|
| Legacy ID pattern | Line 45 | Convert UT-001 → TSPEC.01.40.01 |
| Missing cumulative tag | Traceability | Add @req: REQ.01.01.01 |

### Manual Review Required
| Issue | Location | Recommendation |
|-------|----------|----------------|
| Missing STEST file | TSPEC-01.3 | Create smoke test specifications |
| Low coverage | SPEC.01.28.05 | Add unit tests for method |
```

**Score Indicators**:
- ✅ Green (>=90%): TASKS-Ready
- 🟡 Yellow (70-89%): Needs improvement
- ❌ Red (<70%): Significant issues

**Review Configuration**:

```yaml
review_mode:
  enabled: true
  checks:
    - test_structure      # All 4 test type files present
    - coverage_matrix     # Coverage >= target per SPEC element
    - spec_alignment      # Tests trace to SPEC methods
    - element_ids         # TSPEC.NN.40-43.SS format
    - cumulative_tags     # 8 required tags present
    - test_assertions     # Each test has clear assertions
  output:
    format: markdown      # markdown, json, html
    include_recommendations: true
    include_fix_commands: true
  coverage_targets:
    utest: 95            # Unit test coverage target %
    itest: 85            # Integration test coverage target %
    stest: 100           # Smoke test must cover critical path
    ftest: 75            # Functional test coverage target %
```

### Mode 3: Fix Mode (v2.1)

Auto-repair existing TSPEC documents with backup and content preservation.

**Command**:
```bash
# Fix single TSPEC
/doc-tspec-autopilot TSPEC-01 --fix

# Fix with backup
/doc-tspec-autopilot TSPEC-01 --fix --backup

# Fix all TSPEC
/doc-tspec-autopilot docs/10_TSPEC/ --fix --all

# Fix specific categories only
/doc-tspec-autopilot TSPEC-01 --fix --only element_ids,tags

# Dry-run fix (preview changes)
/doc-tspec-autopilot TSPEC-01 --fix --dry-run
```

**Fix Process**:

```mermaid
flowchart TD
    A[Input: TSPEC Document] --> B[Create Backup]
    B --> C[Load TSPEC Content]
    C --> D[Run Review Analysis]
    D --> E{Auto-Fixable Issues?}
    E -->|No| F[Report: No Fixes Needed]
    E -->|Yes| G[Apply Fixes by Category]

    subgraph FixCategories["Fix Categories"]
        G --> H[Fix Element IDs]
        H --> I[Fix Test Type Structure]
        I --> J[Regenerate Coverage Matrix]
        J --> K[Add Missing Tags]
        K --> L[Fix Section Structure]
        L --> M[Add Missing Test Stubs]
    end

    M --> N[Validate Fixed Document]
    N --> O{Validation Passed?}
    O -->|No| P[Rollback to Backup]
    P --> Q[Report: Fix Failed]
    O -->|Yes| R[Save Fixed Document]
    R --> S[Generate Fix Report]
```

**TSPEC-Specific Fix Categories**:

| Category | Description | Auto-Fix Actions |
|----------|-------------|------------------|
| `element_ids` | Element ID format | Convert legacy patterns to TSPEC.NN.TT.SS |
| `test_types` | Test type files | Create missing UTEST/ITEST/STEST/FTEST files |
| `coverage_matrix` | Coverage tracking | Regenerate matrix from test specifications |
| `cumulative_tags` | Traceability tags | Add missing 8 upstream tags |
| `sections` | Section structure | Add missing sections per test type template |
| `test_stubs` | Missing tests | Generate test stubs for uncovered SPEC elements |
| `assertions` | Test assertions | Flag tests without assertions (manual fix) |

**Element ID Migration** (Layer 10):

| Legacy Pattern | New Format | Example |
|----------------|------------|---------|
| UT-NNN | TSPEC.NN.40.SS | UT-001 → TSPEC.01.40.01 |
| IT-NNN | TSPEC.NN.41.SS | IT-001 → TSPEC.01.41.01 |
| ST-NNN | TSPEC.NN.42.SS | ST-001 → TSPEC.01.42.01 |
| FT-NNN | TSPEC.NN.43.SS | FT-001 → TSPEC.01.43.01 |
| TC-NNN | TSPEC.NN.40.SS | TC-001 → TSPEC.01.40.01 (assume UTEST) |
| TEST-NNN | TSPEC.NN.43.SS | TEST-001 → TSPEC.01.43.01 (assume FTEST) |

**Content Preservation Rules**:

| Content Type | Preservation Rule |
|--------------|-------------------|
| Custom test descriptions | Never delete, only enhance metadata |
| Test assertions | Preserve all test logic |
| Test data/fixtures | Preserve all test data definitions |
| SPEC references | Validate and update format only |
| Coverage percentages | Recalculate after fixes |
| Test prerequisites | Preserve setup/teardown logic |

**Fix Configuration**:

```yaml
fix_mode:
  enabled: true
  backup:
    enabled: true
    location: "tmp/backups/"
    timestamp: true
  fix_categories:
    element_ids: true       # Convert legacy ID patterns
    test_types: true        # Create missing test type files
    coverage_matrix: true   # Regenerate coverage tracking
    cumulative_tags: true   # Add 8 required tags
    sections: true          # Add missing sections
    test_stubs: true        # Generate stubs for uncovered SPEC
    assertions: false       # Manual only (flag but don't auto-fix)
  validation:
    post_fix: true          # Validate after fixes
    rollback_on_fail: true  # Restore backup if validation fails
  preserve:
    test_descriptions: true
    test_assertions: true
    test_data: true
    spec_references: true
```

**Fix Report Template**:

```markdown
# TSPEC Fix Report: TSPEC-NN_{slug}

## Summary
- **Backup Created**: tmp/backups/TSPEC-NN_{slug}_20260209_143022/
- **Issues Fixed**: N of M auto-fixable issues
- **Manual Review**: N issues flagged

## Fixes Applied

### Element ID Migration
| Original | Fixed | File | Location |
|----------|-------|------|----------|
| UT-001 | TSPEC.01.40.01 | TSPEC-01.1_utest.md | Line 45 |
| IT-001 | TSPEC.01.41.01 | TSPEC-01.2_itest.md | Line 23 |
| ST-001 | TSPEC.01.42.01 | TSPEC-01.3_stest.md | Line 12 |

### Test Type Files Created
| File | Tests Generated | Status |
|------|-----------------|--------|
| TSPEC-01.3_stest.md | 5 smoke tests | Created from template |

### Coverage Matrix Regenerated
| SPEC Element | Before | After |
|--------------|--------|-------|
| SPEC.01.28.01 | 50% | 75% |
| SPEC.01.28.02 | 25% | 75% |
| Overall | 45% | 78% |

### Cumulative Tags Added
- @ears: EARS.01.25.001 (added)
- @sys: SYS.01.01.01 (added)
- @req: REQ.01.01.01 (added)

## Test Stubs Generated
| SPEC Element | Test Type | Stub ID |
|--------------|-----------|---------|
| SPEC.01.28.05 | UTEST | TSPEC.01.40.12 |
| SPEC.01.28.05 | ITEST | TSPEC.01.41.08 |

## Manual Review Required

### Tests Without Assertions
| Test ID | File | Issue |
|---------|------|-------|
| TSPEC.01.40.03 | TSPEC-01.1_utest.md | No assert statements |
| TSPEC.01.41.02 | TSPEC-01.2_itest.md | Missing expected outcome |

### Low Coverage Areas
| SPEC Element | Current | Target | Action Needed |
|--------------|---------|--------|---------------|
| SPEC.01.28.07 | 25% | 75% | Add 3+ UTEST, 1+ ITEST |

## Validation Results
- **TASKS-Ready Score**: Before: 68% → After: 92%
- **Validation Errors**: Before: 12 → After: 0
- **Status**: ✅ All auto-fixes validated
```

**Command Line Options** (Review/Fix Modes):

| Option | Default | Description |
|--------|---------|-------------|
| `--review` | false | Run review mode only |
| `--fix` | false | Run fix mode |
| `--backup` | true | Create backup before fixing |
| `--dry-run` | false | Preview fixes without applying |
| `--only` | all | Comma-separated fix categories |
| `--verbose` | false | Detailed output |
| `--all` | false | Process all TSPEC in directory |
| `--output-format` | markdown | Report format (markdown, json) |
| `--generate-stubs` | true | Generate test stubs for uncovered SPEC |
| `--test-types` | all | Comma-separated test types to fix |

---

## Context Management

### Chunked Parallel Execution (MANDATORY)

**CRITICAL**: To prevent conversation context overflow errors ("Prompt is too long", "Conversation too long"), all autopilot operations MUST follow chunked execution rules:

**Chunk Size Limit**: Maximum 3 documents per chunk

**Chunking Rules**:

1. **Chunk Formation**: Group SPEC-derived TSPEC documents into chunks of maximum 3 at a time
2. **Sequential Chunk Processing**: Process one chunk at a time, completing all documents in a chunk before starting the next
3. **Context Pause**: After completing each chunk, provide a summary and pause for user acknowledgment
4. **Progress Tracking**: Display chunk progress (e.g., "Chunk 2/4: Processing TSPEC-04, TSPEC-05, TSPEC-06...")

**Why Chunking is Required**:

- Prevents "Conversation too long" errors during batch processing
- Allows context compaction between chunks
- Enables recovery from failures without losing all progress
- Provides natural checkpoints for user review

**Chunk Completion Template**:

```markdown
## Chunk N/M Complete

Generated:
- TSPEC-XX: TASKS-Ready Score 94% (UTEST + ITEST + STEST + FTEST)
- TSPEC-YY: TASKS-Ready Score 92% (UTEST + ITEST + STEST + FTEST)
- TSPEC-ZZ: TASKS-Ready Score 95% (UTEST + ITEST + STEST + FTEST)

Proceeding to next chunk...
```

---

## Related Resources

- **TSPEC Skill**: `.claude/skills/doc-tspec/SKILL.md`
- **TSPEC Validator**: `.claude/skills/doc-tspec-validator/SKILL.md`
- **Naming Standards**: `.claude/skills/doc-naming/SKILL.md`
- **Quality Advisor**: `.claude/skills/quality-advisor/SKILL.md`
- **TSPEC Template**: `ai_dev_flow/10_TSPEC/TSPEC-TEMPLATE.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2026-02-09 | Added Mode 2: Review Mode for validation-only analysis with visual score indicators and coverage targets; Added Mode 3: Fix Mode for auto-repair with backup, content preservation, and test stub generation; Element ID migration (UT-NNN→TSPEC.NN.40.SS, IT-NNN→TSPEC.NN.41.SS, ST-NNN→TSPEC.NN.42.SS, FT-NNN→TSPEC.NN.43.SS) |
| 1.0 | 2026-02-08 | Initial skill creation with 5-phase workflow; Integrated doc-naming, doc-tspec, quality-advisor, doc-tspec-validator; Support for all 4 test types |
