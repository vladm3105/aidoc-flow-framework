---
title: "Autopilot Integration Review: CHG, TSPEC, and TDD"
tags:
  - framework-review
  - autopilot
  - change-management
  - tspec
  - tdd
custom_fields:
  document_type: review
  artifact_type: REF
  priority: recommended-approach
  development_status: active
  version: "1.0"
  date_created: "2026-02-06T00:00:00"
---

# Autopilot Integration Review: CHG, TSPEC, and TDD

## Executive Summary

This document reviews the current MVP Autopilot (v5.0) and identifies integration gaps for:
- **CHG (Change Management)** - 4-Gate change validation system
- **TSPEC (Test Specification)** - Layer 10 test specifications
- **TDD (Test-Driven Development)** - Test-first workflow integration

**Current State**: Autopilot covers L1-L10 (BRD→TASKS) but skips TSPEC layer and has no CHG integration.

**Proposed State**: Extend autopilot to cover L1-L11 with TSPEC, optional CHG workflows, and TDD-first pipeline.

---

## 1. Current State Analysis

### 1.1 MVP Autopilot v5.0 Layer Coverage

| Layer | Artifact | Current Autopilot | Directory |
|-------|----------|-------------------|-----------|
| L1 | BRD | ✅ Included | `01_BRD/` |
| L2 | PRD | ✅ Included | `02_PRD/` |
| L3 | EARS | ✅ Included | `03_EARS/` |
| L4 | BDD | ✅ Included | `04_BDD/` |
| L5 | ADR | ✅ Included | `05_ADR/` |
| L6 | SYS | ✅ Included | `06_SYS/` |
| L7 | REQ | ✅ Included | `07_REQ/` |
| L8 | CTR | ✅ Included | `08_CTR/` |
| L9 | SPEC | ✅ Included | `09_SPEC/` |
| **L10** | **TSPEC** | ❌ **MISSING** | `10_TSPEC/` |
| L11 | TASKS | ✅ Included (as L10) | `11_TASKS/` |
| - | CHG | ❌ **MISSING** | `CHG/` |

### 1.2 Layer Numbering Inconsistency

The MVP_AUTOPILOT.md document shows TASKS as "Layer 10", but:
- Directory structure: `10_TSPEC/` and `11_TASKS/`
- CHANGE_MANAGEMENT_GUIDE.md: TSPEC is L10, TASKS is L11

**Issue**: Layer numbering mismatch between autopilot documentation and actual directory structure.

### 1.3 Existing Infrastructure (Not Integrated)

#### TSPEC Layer (10_TSPEC/)
```
10_TSPEC/
├── UTEST/          # Unit Test Specifications
├── ITEST/          # Integration Test Specifications
├── STEST/          # Smoke Test Specifications
├── FTEST/          # Functional Test Specifications
├── scripts/        # Validation scripts
│   ├── validate_utest.py
│   ├── validate_itest.py
│   ├── validate_stest.py
│   ├── validate_ftest.py
│   └── validate_tspec_quality_score.sh
└── test_registry.yaml
```

#### Change Management (CHG/)
```
CHG/
├── CHANGE_MANAGEMENT_GUIDE.md   # 4-Gate system
├── CHG-MVP-TEMPLATE.md          # L2 Minor changes
├── CHG-TEMPLATE.md              # L3 Major changes
├── CHG_MVP_SCHEMA.yaml
├── sources/                     # Change source guides
├── scripts/                     # Gate validation scripts
│   ├── validate_chg_routing.py
│   ├── validate_gate01.sh
│   ├── validate_gate05.sh
│   ├── validate_gate09.sh
│   └── validate_gate12.sh
└── templates/
```

#### TDD Strategy (TESTING_STRATEGY_TDD.md)
- Comprehensive TDD integration guide exists
- Autopilot section present but not bidirectionally linked

---

## 2. Gap Analysis

### 2.1 TSPEC Layer Gap

| Gap | Impact | Priority |
|-----|--------|----------|
| No TSPEC generation in pipeline | Tests not specified before code | P1 - Critical |
| No TSPEC validation step | Quality gate missing for tests | P1 - Critical |
| Layer numbering mismatch | Documentation confusion | P2 - High |
| No traceability from SPEC→TSPEC→TASKS | Incomplete traceability chain | P1 - Critical |

### 2.2 Change Management Gap

| Gap | Impact | Priority |
|-----|--------|----------|
| No CHG workflow in autopilot | Changes not tracked/validated | P2 - High |
| No gate validation automation | Manual gate checking required | P2 - High |
| No change level determination | Incorrect process selection | P3 - Medium |
| No integration with resume mode | Brownfield changes untracked | P2 - High |

### 2.3 TDD Integration Gap

| Gap | Impact | Priority |
|-----|--------|----------|
| No test-first generation mode | Tests follow code (not TDD) | P1 - Critical |
| TESTING_STRATEGY_TDD.md not linked | Workflow disconnection | P3 - Medium |
| No failing test validation step | TDD cycle incomplete | P2 - High |
| No PENDING→FILLED tag update | Traceability incomplete | P2 - High |

---

## 3. Proposed Changes

### 3.1 Updated Layer Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    UPDATED 12-LAYER MODEL                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  L1  BRD ──┐                                                    │
│  L2  PRD ──┼── GATE-01 (Business)                              │
│  L3  EARS ─┤                                                    │
│  L4  BDD ──┘                                                    │
│            ↓                                                    │
│  L5  ADR ──┐                                                    │
│  L6  SYS ──┼── GATE-05 (Architecture)                          │
│  L7  REQ ──┤                                                    │
│  L8  CTR ──┘                                                    │
│            ↓                                                    │
│  L9  SPEC ─┐                                                    │
│  L10 TSPEC ┼── GATE-09 (Design/Test) ← NEW: TSPEC INTEGRATION  │
│  L11 TASKS ┘                                                    │
│            ↓                                                    │
│  L12+ Code/Tests/Deploy ── GATE-12 (Implementation)            │
│                                                                 │
│  CHG: Cross-cutting for L2+ changes                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 MVP_AUTOPILOT.md Updates Required

#### 3.2.1 Section: Layer-by-Layer Behavior

**Add TSPEC section** (insert between SPEC and TASKS):

```markdown
### TSPEC (Layer 10)
**Directory**: `10_TSPEC/`

**Generation** (4 test type specifications):
- UTEST: Unit test specifications from REQ (L7) + SPEC (L9)
- ITEST: Integration test specifications from CTR (L8) + SYS (L6)
- STEST: Smoke test specifications from EARS (L3) + BDD (L4)
- FTEST: Functional test specifications from SYS (L6)

**Validation**:
- Script: `10_TSPEC/scripts/validate_tspec_quality_score.sh`
- Minimum Score: 90% (UTEST), 85% (ITEST), 100% (STEST), 85% (FTEST)

**TDD Requirement**:
- Unit tests must be generated with `@code: PENDING` tag
- Tags updated after code generation
```

#### 3.2.2 Section: Traceability Rules

**Update cumulative tagging hierarchy**:

| Layer | Required Tags |
|-------|---------------|
| ... | ... |
| **SPEC** (L9) | `@brd` through `@ctr` |
| **TSPEC** (L10) | `@brd` through `@spec` ← NEW |
| **TASKS** (L11) | `@brd` through `@tspec` ← UPDATED |

#### 3.2.3 Section: Execution Flow

**Update flow diagram**:

```
Configuration → Pre-Checks → Generation (L1-L9)
                                ↓
                            TSPEC Generation (L10) ← NEW
                                ↓
                            TDD Unit Test Validation ← NEW
                                ↓
                            TASKS Generation (L11)
                                ↓
                            Validation → Post-Checks → Report
```

### 3.3 TDD Workflow Integration

#### 3.3.1 New Autopilot Flag: `--tdd-mode`

```bash
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --intent "My MVP" \
  --slug my_mvp \
  --tdd-mode \        # NEW: Enable TDD workflow
  --auto-fix \
  --report markdown
```

**TDD Mode Behavior**:
1. Generate L1-L9 artifacts
2. Generate TSPEC (L10) with test specifications
3. Generate unit test files with `@code: PENDING` tags
4. Validate tests fail (no implementation)
5. Generate TASKS (L11) referencing TSPEC
6. Continue to code generation (if `--up-to CODE`)
7. Validate tests pass
8. Update `@code: PENDING` → actual file paths

#### 3.3.2 TDD Workflow Configuration

**Add to `config/default.yaml`**:

```yaml
tdd:
  enabled: false          # Enable via --tdd-mode flag
  generate_tests: true    # Generate test files from TSPEC
  validate_failing: true  # Validate tests fail before code
  validate_passing: true  # Validate tests pass after code
  update_tags: true       # Update PENDING tags to actual paths
  test_framework: pytest
  coverage_threshold: 90
```

### 3.4 Change Management Integration

#### 3.4.1 New Autopilot Mode: `--chg-mode`

```bash
# For modifying existing artifacts
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --chg-mode \              # NEW: Enable CHG workflow
  --chg-level L2 \          # Change level (L1/L2/L3)
  --chg-source midstream \  # Change source
  --auto-fix \
  --report markdown
```

**CHG Mode Behavior**:
1. Analyze affected layers from change
2. Determine entry gate (GATE-01/05/09/12)
3. Create CHG document from template
4. Validate gate requirements
5. Process affected layers
6. Update traceability
7. Validate all gates passed
8. Complete CHG document

#### 3.4.2 CHG Workflow Configuration

**Add to `config/default.yaml`**:

```yaml
change_management:
  enabled: false              # Enable via --chg-mode flag
  auto_classify: true         # Auto-determine L1/L2/L3
  create_chg_doc: true        # Auto-create CHG document
  validate_gates: true        # Run gate validation scripts
  archive_obsolete: true      # Archive replaced artifacts (L3)
  template_l2: CHG-MVP-TEMPLATE.md
  template_l3: CHG-TEMPLATE.md
```

### 3.5 Updated Command Reference

| Flag | Short | Description |
|------|-------|-------------|
| `--tdd-mode` | `-T` | Enable TDD workflow with TSPEC generation |
| `--chg-mode` | `-C` | Enable CHG workflow for existing artifacts |
| `--chg-level` | | Change level: L1, L2, or L3 |
| `--chg-source` | | Change source: upstream, midstream, downstream, external, feedback |
| `--skip-tspec` | | Skip TSPEC generation (legacy mode) |
| `--validate-gates` | | Run CHG gate validation only |

---

## 4. Implementation Plan

### Phase 1: Documentation Updates (Priority: P1)

| Task | File | Effort |
|------|------|--------|
| Fix layer numbering | MVP_AUTOPILOT.md | Low |
| Add TSPEC section | MVP_AUTOPILOT.md | Medium |
| Update traceability hierarchy | MVP_AUTOPILOT.md | Low |
| Update execution flow diagram | MVP_AUTOPILOT.md | Low |
| Add cross-references to TESTING_STRATEGY_TDD.md | MVP_AUTOPILOT.md | Low |

### Phase 2: TSPEC Integration (Priority: P1)

| Task | File | Effort |
|------|------|--------|
| Add TSPEC generation logic | mvp_autopilot.py | High |
| Add TSPEC validation calls | mvp_autopilot.py | Medium |
| Update config schema | config/default.yaml | Low |
| Add TSPEC layer config | config/layers.yaml | Low |
| Update quality gates config | config/quality_gates.yaml | Low |

### Phase 3: TDD Workflow (Priority: P2)

| Task | File | Effort |
|------|------|--------|
| Implement --tdd-mode flag | mvp_autopilot.py | Medium |
| Add test generation logic | mvp_autopilot.py | High |
| Add PENDING tag management | mvp_autopilot.py | Medium |
| Add failing test validation | mvp_autopilot.py | Medium |
| Update CI/CD workflows | .github/workflows/*.yml | Medium |

### Phase 4: CHG Integration (Priority: P3)

| Task | File | Effort |
|------|------|--------|
| Implement --chg-mode flag | mvp_autopilot.py | Medium |
| Add CHG document generation | mvp_autopilot.py | Medium |
| Integrate gate validation | mvp_autopilot.py | Medium |
| Add change level auto-detection | mvp_autopilot.py | High |
| Add archive logic for L3 | mvp_autopilot.py | Medium |

---

## 5. Updated Workflow Diagrams

### 5.1 Standard Workflow (with TSPEC)

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTOPILOT STANDARD WORKFLOW                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Configuration Loading                                          │
│         ↓                                                       │
│  Pre-Checks                                                     │
│         ↓                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │            Documentation Generation                   │      │
│  │  BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR    │      │
│  │         ↓                                             │      │
│  │       SPEC                                            │      │
│  │         ↓                                             │      │
│  │       TSPEC (Unit/Integration/Smoke/Functional)  ← NEW│      │
│  │         ↓                                             │      │
│  │       TASKS                                           │      │
│  └──────────────────────────────────────────────────────┘      │
│         ↓                                                       │
│  Validation (All Layers)                                        │
│         ↓                                                       │
│  Post-Checks                                                    │
│         ↓                                                       │
│  Report Generation                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 TDD Workflow Mode

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTOPILOT TDD WORKFLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Documentation Generation (L1-L9)                               │
│         ↓                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                TDD CYCLE                              │      │
│  │                                                       │      │
│  │  TSPEC Generation (L10)                              │      │
│  │         ↓                                             │      │
│  │  Test File Generation (@code: PENDING)               │      │
│  │         ↓                                             │      │
│  │  Validate Tests FAIL (Red State) ✓                   │      │
│  │         ↓                                             │      │
│  │  TASKS Generation (L11)                              │      │
│  │         ↓                                             │      │
│  │  Code Generation (L12)                               │      │
│  │         ↓                                             │      │
│  │  Validate Tests PASS (Green State) ✓                 │      │
│  │         ↓                                             │      │
│  │  Update @code Tags (PENDING → path)                  │      │
│  └──────────────────────────────────────────────────────┘      │
│         ↓                                                       │
│  Report with TDD Metrics                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 CHG Workflow Mode

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTOPILOT CHG WORKFLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Change Request                                                 │
│         ↓                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │            CHANGE CLASSIFICATION                      │      │
│  │                                                       │      │
│  │  Analyze affected layers                             │      │
│  │         ↓                                             │      │
│  │  Determine change level (L1/L2/L3)                   │      │
│  │         ↓                                             │      │
│  │  Determine entry gate (GATE-01/05/09/12)             │      │
│  └──────────────────────────────────────────────────────┘      │
│         ↓                                                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │            GATE VALIDATION                            │      │
│  │                                                       │      │
│  │  Run gate validation scripts                         │      │
│  │         ↓                                             │      │
│  │  Create CHG document                                 │      │
│  │         ↓                                             │      │
│  │  Archive obsolete artifacts (L3 only)                │      │
│  └──────────────────────────────────────────────────────┘      │
│         ↓                                                       │
│  Process Affected Layers (downstream cascade)                   │
│         ↓                                                       │
│  Update Traceability                                            │
│         ↓                                                       │
│  Complete CHG Document                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Configuration Updates Required

### 6.1 config/default.yaml

```yaml
# Add after existing configuration

# TSPEC Layer Configuration (NEW)
tspec:
  enabled: true
  directory: "10_TSPEC"
  test_types:
    - type: UTEST
      directory: UTEST
      sources: [REQ, SPEC]
      min_score: 90
    - type: ITEST
      directory: ITEST
      sources: [CTR, SYS, SPEC]
      min_score: 85
    - type: STEST
      directory: STEST
      sources: [EARS, BDD, REQ]
      min_score: 100
    - type: FTEST
      directory: FTEST
      sources: [SYS]
      min_score: 85
  validator: "10_TSPEC/scripts/validate_tspec_quality_score.sh"

# TDD Configuration (NEW)
tdd:
  enabled: false
  generate_tests: true
  validate_failing: true
  validate_passing: true
  update_tags: true
  test_framework: pytest
  coverage_threshold: 90
  test_output_dir: "tests"

# Change Management Configuration (NEW)
change_management:
  enabled: false
  auto_classify: true
  create_chg_doc: true
  validate_gates: true
  archive_obsolete: true
  chg_directory: "docs/CHG"
  templates:
    l2: "CHG/CHG-MVP-TEMPLATE.md"
    l3: "CHG/CHG-TEMPLATE.md"
  gates:
    gate01: "CHG/scripts/validate_gate01.sh"
    gate05: "CHG/scripts/validate_gate05.sh"
    gate09: "CHG/scripts/validate_gate09.sh"
    gate12: "CHG/scripts/validate_gate12.sh"
```

### 6.2 config/quality_gates.yaml

```yaml
# Add TSPEC quality gates

tspec_quality_gates:
  utest:
    min_score: 90
    required_sections:
      - purpose
      - test_cases
      - io_tables
      - traceability
  itest:
    min_score: 85
    required_sections:
      - purpose
      - component_interactions
      - sequence_diagrams
      - traceability
  stest:
    min_score: 100
    required_sections:
      - critical_paths
      - timeout_budget
      - rollback_procedure
      - traceability
  ftest:
    min_score: 85
    required_sections:
      - sys_requirements
      - threshold_validation
      - traceability
```

---

## 7. Testing the Integration

### 7.1 Verification Checklist

**TSPEC Integration**:
- [ ] TSPEC layer generates after SPEC
- [ ] All 4 test types (UTEST/ITEST/STEST/FTEST) generate correctly
- [ ] TSPEC validators run and report scores
- [ ] TASKS references TSPEC with correct tags
- [ ] Traceability chain complete: SPEC → TSPEC → TASKS

**TDD Integration**:
- [ ] `--tdd-mode` flag recognized
- [ ] Test files generate with `@code: PENDING` tags
- [ ] Test failure validation works (Red state)
- [ ] Test pass validation works (Green state)
- [ ] PENDING tags update to actual paths

**CHG Integration**:
- [ ] `--chg-mode` flag recognized
- [ ] CHG document created from template
- [ ] Gate validation scripts execute
- [ ] Archive logic works for L3 changes
- [ ] Traceability updates correctly

### 7.2 Test Commands

```bash
# Standard workflow with TSPEC
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --intent "Test TSPEC Integration" \
  --slug test_tspec \
  --auto-fix \
  --report markdown

# TDD workflow
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --intent "Test TDD Integration" \
  --slug test_tdd \
  --tdd-mode \
  --auto-fix \
  --report markdown

# CHG workflow
python3 ai_dev_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root ai_dev_flow \
  --chg-mode \
  --chg-level L2 \
  --chg-source midstream \
  --auto-fix \
  --report markdown
```

---

## 8. Related Documentation

| Document | Path | Relationship |
|----------|------|--------------|
| MVP Autopilot (current) | `AUTOPILOT/MVP_AUTOPILOT.md` | Primary update target |
| TSPEC README | `10_TSPEC/README.md` | TSPEC layer details |
| Change Management Guide | `CHG/CHANGE_MANAGEMENT_GUIDE.md` | CHG integration source |
| Testing Strategy TDD | `TESTING_STRATEGY_TDD.md` | TDD workflow source |
| Traceability Guide | `TRACEABILITY.md` | Tag requirements |

---

## 9. Summary

### 9.1 Key Changes Required

1. **Fix layer numbering** (TSPEC=L10, TASKS=L11)
2. **Add TSPEC generation** to autopilot pipeline
3. **Add TSPEC validation** to quality gates
4. **Implement TDD mode** with test-first workflow
5. **Implement CHG mode** for change management
6. **Update configuration** files with new options
7. **Update documentation** with new workflows

### 9.2 Benefits

| Integration | Benefit |
|-------------|---------|
| TSPEC | Complete test specification before implementation |
| TDD | Enforce test-first development practices |
| CHG | Formal change tracking and gate validation |
| All | End-to-end traceability from BRD to tests |

### 9.3 Implementation Priority

| Phase | Components | Priority |
|-------|------------|----------|
| 1 | Documentation fixes + TSPEC | P1 - Critical |
| 2 | TDD workflow | P2 - High |
| 3 | CHG workflow | P3 - Medium |

---

**Document Control**

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Date Created | 2026-02-06T00:00:00 |
| Status | Draft |
| Author | AI Dev Flow Framework |
| Review Required | Yes |
