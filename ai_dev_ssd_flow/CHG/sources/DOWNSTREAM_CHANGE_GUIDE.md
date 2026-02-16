---
title: "Downstream Change Guide (Defect Management)"
tags:
  - change-management
  - change-source
  - downstream
  - defect-management
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: CHG
  change_source: downstream
  origin_layers: [12, 13, 14]
  development_status: active
---

# Downstream Change Guide

**Change Source**: Downstream (Implementation/Defect-Driven)
**Origin Layers**: L12-L14 (Code, Tests, Validation)
**Direction**: Bottom-up (may bubble to source layer)
**Entry Gate**: GATE-12 (Implementation)

---

## Gate Entry Point

| Attribute | Value |
|-----------|-------|
| **Entry Gate** | GATE-12 |
| **Gate Layers** | L12-L14 (Code, Tests, Validation) |
| **Validation Script** | `./CHG/scripts/validate_gate12.sh` |
| **Full Workflow** | `workflows/DOWNSTREAM_WORKFLOW.md` |

**Critical**: Downstream changes require root cause analysis. If root cause is upstream:

| Root Cause Layer | Bubble Up To | Cascade Path |
|------------------|--------------|--------------|
| L12-L14 (Code/Tests) | Stay at GATE-12 | GATE-12 only |
| L9-L11 (SPEC/TSPEC) | GATE-09 | GATE-09 → GATE-12 |
| L5-L8 (REQ/CTR) | GATE-05 | GATE-05 → GATE-09 → GATE-12 |
| L1-L4 (BRD/PRD) | GATE-01 | GATE-01 → GATE-05 → GATE-09 → GATE-12 |

**Before proceeding, validate root cause:**
```bash
./CHG/scripts/validate_gate12.sh <CHG_FILE>
python CHG/scripts/validate_chg_routing.py <CHG_FILE> --validate-root-cause
```

---

## 1. Overview

Downstream changes originate from defects discovered during implementation, testing, or validation. The key is **root cause analysis** to determine where the fix should be applied.

```
┌─────────────────────────────────────────────────────────────┐
│                 DOWNSTREAM CHANGE FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              DEFECT DETECTION POINTS                │   │
│  │  • Unit test failure (L13)                          │   │
│  │  • Integration test failure (L13)                   │   │
│  │  • Smoke test failure (L13)                         │   │
│  │  • Validation failure (L14)                         │   │
│  │  • Code review finding (L12)                        │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│             ┌─────────────────────────┐                    │
│             │   ROOT CAUSE ANALYSIS   │                    │
│             │   Where is the bug?     │                    │
│             └───────────┬─────────────┘                    │
│                         │                                   │
│         ┌───────────────┼───────────────┐                  │
│         │               │               │                  │
│         ▼               ▼               ▼                  │
│   ┌──────────┐   ┌──────────┐   ┌──────────────┐          │
│   │ CODE BUG │   │SPEC ERROR│   │REQUIREMENT   │          │
│   │  (L12)   │   │ (L9-L11) │   │   GAP (L1-L7)│          │
│   └────┬─────┘   └────┬─────┘   └──────┬───────┘          │
│        │              │                │                   │
│        ▼              ▼                ▼                   │
│   ┌──────────┐   ┌──────────┐   ┌──────────────┐          │
│   │ L1: Fix  │   │ L2: Fix  │   │ L2-L3: Fix   │          │
│   │ code     │   │ spec +   │   │ requirement  │          │
│   │ only     │   │ regen    │   │ + cascade    │          │
│   └──────────┘   └──────────┘   └──────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. Root Cause Analysis

### 2.1 The Key Question

When a test fails, ask: **"Where does the truth lie?"**

| If the truth is in... | The bug is in... | Fix at... |
|-----------------------|------------------|-----------|
| The test (TSPEC) | Code implementation | L12 Code |
| The code (expected behavior) | Test specification | L10 TSPEC |
| Neither (ambiguous) | Requirement/Spec | L7-L9 |
| Business expectation | Requirement | L1-L7 |

### 2.2 Root Cause Decision Tree

```
                    ┌───────────────────────┐
                    │    Test Failed        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Does test match TSPEC?│
                    └───────────┬───────────┘
                                │
               ┌────────────────┴────────────────┐
               │ NO                              │ YES
               ▼                                 ▼
    ┌───────────────────┐           ┌───────────────────┐
    │ Test impl wrong   │           │ Does TSPEC match  │
    │ Fix: L13 Tests    │           │ SPEC?             │
    │ Level: L1         │           └─────────┬─────────┘
    └───────────────────┘                     │
                               ┌──────────────┴──────────────┐
                               │ NO                          │ YES
                               ▼                             ▼
                    ┌───────────────────┐       ┌───────────────────┐
                    │ TSPEC wrong       │       │ Does SPEC match   │
                    │ Fix: L10 TSPEC    │       │ REQ?              │
                    │ Level: L1         │       └─────────┬─────────┘
                    └───────────────────┘                 │
                                          ┌──────────────┴──────────────┐
                                          │ NO                          │ YES
                                          ▼                             ▼
                               ┌───────────────────┐       ┌───────────────────┐
                               │ SPEC wrong        │       │ Code bug          │
                               │ Fix: L9 SPEC      │       │ Fix: L12 Code     │
                               │ Level: L2         │       │ Level: L1         │
                               └───────────────────┘       └───────────────────┘
```

## 3. Defect Classification

### 3.1 By Root Cause Layer

| Root Cause | Layer | Fix Level | Regeneration Scope |
|------------|-------|-----------|-------------------|
| **Code Implementation Bug** | L12 | L1 | None |
| **Test Implementation Bug** | L13 | L1 | None |
| **TSPEC Error** | L10 | L1 | Re-run tests |
| **TASKS Error** | L11 | L1-L2 | Code regeneration |
| **SPEC Design Error** | L9 | L2 | L10-L14 |
| **CTR Contract Error** | L8 | L2-L3 | L9-L14 |
| **REQ Ambiguity** | L7 | L2 | L8-L14 |
| **Requirement Gap** | L1-L7 | L2-L3 | Full cascade |

### 3.2 By Severity

| Severity | Description | Response Time | Level |
|----------|-------------|---------------|-------|
| **Critical** | System unusable | Immediate | L1-L3 |
| **High** | Major feature broken | 24 hours | L1-L2 |
| **Medium** | Feature degraded | 1 week | L1-L2 |
| **Low** | Minor issue | Next sprint | L1 |

## 4. Fix Workflows

### 4.1 L1: Code Bug Fix

**When**: Root cause is in L12 Code only

```
┌─────────────────────────────────────────────────────────────┐
│                  CODE BUG FIX (L1)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Reproduce the bug                                       │
│     - Identify failing test                                 │
│     - Confirm TSPEC is correct                              │
│                                                             │
│  2. Fix the code                                            │
│     - Edit source file                                      │
│     - Follow SPEC design                                    │
│                                                             │
│  3. Verify fix                                              │
│     - Run failing test → Now passes                        │
│     - Run related tests → No regression                    │
│                                                             │
│  4. Commit                                                  │
│     - "fix: [description]"                                 │
│     - Reference issue/ticket if applicable                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**No CHG required.**

### 4.2 L1: Test/TSPEC Fix

**When**: Root cause is in L10 TSPEC or L13 Test implementation

```
┌─────────────────────────────────────────────────────────────┐
│               TEST/TSPEC FIX (L1)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Identify incorrect test                                 │
│     - Compare test with SPEC                                │
│     - Confirm code behavior is correct                      │
│                                                             │
│  2. Fix TSPEC (if spec wrong)                               │
│     - Update test case definition                           │
│     - Update I/O tables                                     │
│     - Update expected results                               │
│                                                             │
│  3. Fix Test implementation (if impl wrong)                 │
│     - Update test code to match TSPEC                       │
│                                                             │
│  4. Verify                                                  │
│     - Test now passes                                       │
│     - TSPEC matches SPEC                                    │
│                                                             │
│  5. Commit                                                  │
│     - "fix(test): [description]"                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**No CHG required.**

### 4.3 L2: SPEC/Design Fix

**When**: Root cause is in L9 SPEC design

```
┌─────────────────────────────────────────────────────────────┐
│                 SPEC FIX (L2)                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Create CHG document                                     │
│     - CHG-XX_spec_fix/                                     │
│     - Use CHG-MVP-TEMPLATE.md                              │
│                                                             │
│  2. Verify upstream alignment                               │
│     - Does REQ support correct behavior?                   │
│     - If not → Escalate to L7                              │
│                                                             │
│  3. Update SPEC                                             │
│     - Fix design error                                      │
│     - Increment version                                     │
│                                                             │
│  4. Update TSPEC                                            │
│     - Align test specs with fixed SPEC                     │
│                                                             │
│  5. Update TASKS                                            │
│     - Reflect implementation changes                       │
│                                                             │
│  6. Regenerate Code                                         │
│     - Implement corrected design                           │
│                                                             │
│  7. Validate                                                │
│     - All tests pass                                        │
│     - Close CHG                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 L2-L3: Requirement Gap Fix

**When**: Root cause is in L1-L7 requirements

```
┌─────────────────────────────────────────────────────────────┐
│              REQUIREMENT GAP FIX (L2-L3)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Create CHG document                                     │
│     - CHG-XX_requirement_gap/                              │
│     - Assess L2 vs L3 based on scope                       │
│                                                             │
│  2. Identify gap in requirements                            │
│     - Which layer has the ambiguity?                       │
│     - BRD? PRD? EARS? BDD? REQ?                            │
│                                                             │
│  3. Clarify requirement                                     │
│     - Work with stakeholders                               │
│     - Document correct behavior                            │
│                                                             │
│  4. Update requirement artifact                             │
│     - Add/modify requirement                               │
│     - Update traceability                                  │
│                                                             │
│  5. Cascade downstream                                      │
│     - Update all affected layers                           │
│     - SPEC → TSPEC → TASKS → Code → Tests                  │
│                                                             │
│  6. Validate                                                │
│     - All tests pass                                        │
│     - Behavior matches clarified requirement               │
│     - Close CHG                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 5. Test Failure Triage

### 5.1 Unit Test Failure (UTEST)

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Wrong output | Code logic error | L1 code fix |
| Missing edge case | Test incomplete | L1 TSPEC/test fix |
| Type error | Code or SPEC wrong | Check SPEC first |

### 5.2 Integration Test Failure (ITEST)

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Component mismatch | Contract violation | Check CTR |
| Data format error | Schema mismatch | Check CTR .yaml |
| Connection failure | Config/infra issue | L1 config fix |

### 5.3 Smoke Test Failure (STEST)

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Health check fails | Deployment issue | Check deploy config |
| Critical path broken | Major bug escaped | L1-L2 investigation |
| Timeout | Performance issue | Check SYS thresholds |

### 5.4 Functional Test Failure (FTEST)

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Threshold not met | Implementation gap | Check SYS requirements |
| Behavior mismatch | REQ/BDD ambiguity | Clarify requirements |
| Quality attr fail | Design issue | Check ADR/SYS |

## 6. Defect Documentation

### 6.1 Defect Record Template

```markdown
## Defect: [Brief Description]

**Detected By**: [Test type/method]
**Severity**: [Critical/High/Medium/Low]
**Root Cause Layer**: [L7-L14]

### Analysis
- **Symptom**: [What failed]
- **Expected**: [What should happen]
- **Actual**: [What happened]
- **Root Cause**: [Where the bug is]

### Fix
- **Layer**: [Where to fix]
- **Change Level**: [L1/L2/L3]
- **Artifacts Updated**: [List]

### Verification
- [ ] Fix implemented
- [ ] Tests pass
- [ ] No regression
```

### 6.2 Defect Traceability

Every defect fix should be traceable:

```
Defect → Root Cause Analysis → Fix Layer → CHG (if L2+) → Verification
```

## 7. Examples

### 7.1 Example: Unit Test Failure - Code Bug

**Symptom**: `test_calculate_total` fails with wrong sum

```
Root Cause Analysis:
- TSPEC says: sum(items) should return total
- SPEC says: iterate and sum all items
- Code: has off-by-one error in loop

Conclusion: Code bug (L12)
Fix Level: L1
Action: Fix loop in calculate_total()
```

### 7.2 Example: Integration Test Failure - Contract Mismatch

**Symptom**: `test_api_create_user` returns 400

```
Root Cause Analysis:
- Test sends: {"name": "John"}
- CTR .yaml requires: {"name": "str", "email": "str"}
- Code validates per CTR

Conclusion: Test doesn't match CTR (L10/L13)
Fix Level: L1
Action: Update test to include required email field
```

### 7.3 Example: Functional Test Failure - Requirement Gap

**Symptom**: `test_response_time` exceeds threshold

```
Root Cause Analysis:
- FTEST threshold: P95 < 200ms
- SYS requirement: P95 < 200ms
- Actual P95: 350ms
- SPEC algorithm: O(n²) complexity

Conclusion: SPEC design doesn't meet SYS requirement
Fix Level: L2
Action: Redesign algorithm in SPEC, regenerate downstream
```

---

**Related Documents**:
- [CHANGE_MANAGEMENT_GUIDE.md](../CHANGE_MANAGEMENT_GUIDE.md)
- [TESTING_STRATEGY_TDD.md](../../TESTING_STRATEGY_TDD.md)
- [10_TSPEC/README.md](../../10_TSPEC/README.md)
