---
title: "Downstream Change Workflow"
tags:
  - change-management
  - workflow
  - downstream
  - defect-management
  - shared-architecture
custom_fields:
  document_type: workflow
  artifact_type: CHG
  change_source: downstream
  entry_gate: GATE-12
  development_status: active
---

# Downstream Change Workflow

> **Entry Gate**: GATE-12 (Implementation)
> **Source Layers**: L12-L14 (Code, Tests, Validation)
> **Cascade Direction**: Bottom-up (bubble up to source layer)

## 1. Overview

This workflow handles changes originating from code bugs, test failures, and validation issues. These changes enter at GATE-12 but may require root cause analysis to bubble up to the correct layer for fixing.

### 1.1 Typical Triggers

- Code bug reports
- Test failures
- Validation failures
- Code review findings
- Static analysis issues
- Runtime errors

### 1.2 Workflow Path

```
DOWNSTREAM TRIGGER (L12-L14)
         │
         ▼
   ┌──────────────────────────────────────┐
   │         ROOT CAUSE ANALYSIS          │
   │     Where is the actual problem?     │
   └─────────────────┬────────────────────┘
                     │
     ┌───────────────┼───────────────────┬───────────────────┐
     │               │                   │                   │
     ▼               ▼                   ▼                   ▼
  Code Bug        SPEC/TSPEC         REQ/CTR            BRD/PRD
  (L12-L14)        Wrong              Wrong              Wrong
     │            (L9-L11)           (L5-L8)            (L1-L4)
     │               │                   │                   │
     ▼               ▼                   ▼                   ▼
  GATE-12        GATE-09             GATE-05            GATE-01
  Fix Here       Bubble Up           Bubble Up          Bubble Up
     │               │                   │                   │
     ▼               ▼                   ▼                   ▼
  DEPLOYED       Cascade             Cascade            Full
                 L9→L14              L5→L14             Cascade
```

## 2. Pre-Workflow Checklist

Before initiating the downstream change workflow:

```markdown
- [ ] Issue/defect documented
- [ ] Reproduction steps available
- [ ] Initial investigation completed
- [ ] Root cause hypothesis formed
- [ ] Impact scope assessed
```

## 3. Root Cause Analysis (Critical)

**The most important step in downstream workflow is finding the TRUE root cause.**

### 3.1 5-Whys Template

```markdown
## Root Cause Analysis

### Problem Statement
Test X fails with error Y

### 5-Whys Analysis
1. Why does test X fail?
   → Because function Z returns incorrect value

2. Why does function Z return incorrect value?
   → Because the algorithm doesn't handle edge case

3. Why doesn't algorithm handle edge case?
   → Because SPEC doesn't mention edge case

4. Why doesn't SPEC mention edge case?
   → Because REQ didn't specify this scenario

5. Why didn't REQ specify this scenario?
   → Because user story acceptance criteria was ambiguous

### Root Cause
**Layer**: L7 (REQ) / L4 (BDD)
**Fix Required**: Update REQ with explicit edge case, update BDD acceptance criteria
```

### 3.2 Root Cause Layer Detection

| Symptom | Investigation | Likely Root Cause Layer |
|---------|---------------|------------------------|
| Code throws exception | Check if SPEC covers scenario | L12 (code) or L9 (SPEC) |
| Test assertion fails | Check if test matches SPEC | L13 (test) or L10 (TSPEC) |
| Integration fails | Check contract alignment | L8 (CTR) or L12 (code) |
| Acceptance fails | Check requirement clarity | L4 (BDD) or L7 (REQ) |
| Performance issue | Check quality attributes | L6 (SYS) or L12 (code) |

### 3.3 Symptom vs. Root Cause

```
ANTI-PATTERN: Symptom Masking
────────────────────────────
Test fails → Add try/catch to suppress error
             ✗ This masks the symptom, not fix root cause

CORRECT: Root Cause Fix
───────────────────────
Test fails → Trace to SPEC → Trace to REQ → Fix REQ
             Cascade fix through all layers
             ✓ This fixes the actual problem
```

## 4. Step-by-Step Process

### Step 1: Issue Documentation

| Action | Details |
|--------|---------|
| Document defect | Issue tracker or CHG document |
| Reproduction steps | Clear steps to reproduce |
| Environment details | OS, versions, configurations |
| Error messages | Full stack traces |

### Step 2: Root Cause Analysis

Execute 5-Whys or fishbone analysis:

```markdown
- [ ] Problem statement documented
- [ ] 5-Whys completed
- [ ] Root cause layer identified
- [ ] Fix layer determined
- [ ] Bubble-up required? (Yes if root cause is L1-L11)
```

### Step 3: Routing Decision

Based on root cause layer:

| Root Cause Layer | Entry Gate | Process |
|------------------|------------|---------|
| L12-L14 (Code/Tests) | GATE-12 | Fix directly |
| L9-L11 (SPEC/TSPEC/TASKS) | GATE-09 | Bubble up, cascade |
| L5-L8 (ADR/SYS/REQ/CTR) | GATE-05 | Bubble up, cascade |
| L1-L4 (BRD/PRD/EARS/BDD) | GATE-01 | Bubble up, full cascade |

### Step 4a: GATE-12 Fix (L12-L14 Root Cause)

If root cause is in implementation layers:

**Validation**:
```bash
./CHG/scripts/validate_gate12.sh CHG-XX_bugfix/CHG-XX_bugfix.md
```

**Fix Process**:
```markdown
1. Write failing test (if not already failing)
2. Implement fix
3. Verify test passes
4. Run regression tests
5. Code review
6. Merge
```

### Step 4b: Bubble-Up Fix (L1-L11 Root Cause)

If root cause is upstream:

1. Create CHG for upstream fix
2. Route to appropriate gate (GATE-01/05/09)
3. Fix at root cause layer
4. Cascade changes downstream
5. Original downstream symptom should be resolved

**Example**:
```markdown
Original Issue: Test_checkout_total fails
Root Cause: REQ-07-003 missing tax calculation spec
Fix Route: GATE-05 → Update REQ → GATE-09 → Update SPEC/TSPEC → GATE-12 → Fix code
```

### Step 5: Closure

```markdown
## Closure Checklist
- [ ] Root cause identified and documented
- [ ] Fix at correct layer (not symptom masking)
- [ ] Regression tests added
- [ ] Code review approved
- [ ] Tests passing
- [ ] CHG status set to "Completed"
```

## 5. Change Level Specifics

### 5.1 L1 Patch (Downstream)

Most common for downstream changes:
- Simple bug fixes
- Test corrections
- Typo fixes in code

**Process**: Direct fix, no CHG document required

### 5.2 L2 Minor (Downstream)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-MVP-TEMPLATE.md |
| Approvals | TL + QA |
| Cascade | As determined by root cause |
| Timeline | 1-3 business days |

### 5.3 L3 Major (Downstream)

Rare for downstream; indicates significant design flaw:

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-TEMPLATE.md |
| Approvals | TL + Architect |
| Cascade | Likely full cascade after bubble-up |
| Timeline | 5-15 business days |

## 6. Common Scenarios

### Scenario 1: Simple Code Bug

```
Trigger: Null pointer exception in production
Root Cause: L12 (code doesn't check for null)
Change Level: L1

1. Write test reproducing the bug
2. Fix null check in code
3. Verify test passes
4. Commit: "fix: add null check in X function"
```

### Scenario 2: Test Spec Mismatch

```
Trigger: Test fails but code seems correct
Root Cause: L10 (TSPEC has wrong expected value)
Change Level: L1 or L2

1. Verify SPEC defines correct behavior
2. GATE-09: Update TSPEC to match SPEC
3. GATE-12: Update test implementation
4. All tests should pass
```

### Scenario 3: Missing Specification

```
Trigger: Edge case not handled
Root Cause: L9 (SPEC doesn't cover edge case)
Change Level: L2

1. Create CHG-XX_edge_case/
2. GATE-09:
   a. Update TSPEC with edge case test
   b. Update SPEC with edge case handling
3. GATE-12: Implement edge case in code
```

### Scenario 4: Requirement Ambiguity

```
Trigger: Feature works differently than expected
Root Cause: L7 (REQ is ambiguous)
Change Level: L2 or L3

1. Create CHG-XX_req_clarity/
2. GATE-05: Update REQ with clarification
3. GATE-09: Update SPEC/TSPEC
4. GATE-12: Adjust implementation if needed
```

### Scenario 5: Integration Failure

```
Trigger: Service A can't communicate with Service B
Root Cause: L8 (CTR contract mismatch)
Change Level: L2 or L3

1. Create CHG-XX_contract_fix/
2. GATE-05: Update CTR for correct contract
3. GATE-09: Update SPEC/TSPEC for both services
4. GATE-12: Fix implementation in both services
```

## 7. Regression Test Requirements

### 7.1 Required for All Downstream Fixes

```markdown
## Regression Test Checklist
- [ ] Test reproducing the bug exists
- [ ] Test passes after fix
- [ ] Related functionality regression tests run
- [ ] No test coverage decrease
```

### 7.2 Test Scope by Root Cause Layer

| Root Cause Layer | Minimum Test Scope |
|------------------|-------------------|
| L12 (Code) | Unit tests for changed functions |
| L13 (Tests) | Affected test suite |
| L10 (TSPEC) | All tests in affected TSPEC |
| L9 (SPEC) | Integration tests for feature |
| L8 (CTR) | Contract tests + integration |
| L7 (REQ) | Acceptance tests for requirement |
| L4 (BDD) | Full BDD scenario suite |

## 8. Anti-Pattern Detection

### 8.1 Symptom Masking Indicators

| Pattern | Detection | Correct Action |
|---------|-----------|----------------|
| Try/catch hiding error | Suppresses rather than handles | Fix root cause |
| Hardcoded workaround | Magic values/conditionals | Update SPEC |
| Duplicate code for fix | Copy-paste instead of abstraction | Refactor properly |
| Test disabled/skipped | `@skip` or `@ignore` annotation | Fix test or SPEC |

### 8.2 Validation

```bash
# Check for symptom masking patterns
./CHG/scripts/validate_gate12.sh --check-symptom-masking CHG-XX/

# Verify fix is at correct layer
python CHG/scripts/validate_chg_routing.py CHG-XX/ --validate-root-cause
```

## 9. Validation Script Integration

```bash
# Full workflow validation
./CHG/scripts/validate_all_gates.sh CHG-XX_bugfix/CHG-XX_bugfix.md --source=downstream

# Root cause validation
python CHG/scripts/validate_chg_routing.py CHG-XX_bugfix/ --validate-root-cause

# Individual gate validation
./CHG/scripts/validate_gate12.sh CHG-XX_bugfix/CHG-XX_bugfix.md

# If bubble-up required
./CHG/scripts/validate_gate09.sh CHG-XX_bugfix/CHG-XX_bugfix.md
./CHG/scripts/validate_gate05.sh CHG-XX_bugfix/CHG-XX_bugfix.md
./CHG/scripts/validate_gate01.sh CHG-XX_bugfix/CHG-XX_bugfix.md
```

---

**Related Documents**:
- [../gates/GATE-12_IMPLEMENTATION.md](../gates/GATE-12_IMPLEMENTATION.md)
- [../sources/DOWNSTREAM_CHANGE_GUIDE.md](../sources/DOWNSTREAM_CHANGE_GUIDE.md)
- [../sources/FEEDBACK_CHANGE_GUIDE.md](../sources/FEEDBACK_CHANGE_GUIDE.md)
- [EMERGENCY_WORKFLOW.md](./EMERGENCY_WORKFLOW.md) (for P1 incidents)
