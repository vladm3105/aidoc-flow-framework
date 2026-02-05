---
title: "Design Change Workflow"
tags:
  - change-management
  - workflow
  - design-optimization
  - shared-architecture
custom_fields:
  document_type: workflow
  artifact_type: CHG
  change_source: design-optimization
  entry_gate: GATE-09
  development_status: active
---

# Design Change Workflow

> **Entry Gate**: GATE-09 (Design/Test)
> **Source Layers**: L9-L11 (SPEC, TSPEC, TASKS)
> **Cascade Direction**: Downstream to L14, with TDD compliance

## 1. Overview

This workflow handles changes originating from design optimizations, test specification updates, and task breakdown refinements. These changes enter at GATE-09 and focus on maintaining TDD compliance while cascading to implementation.

### 1.1 Typical Triggers

- Algorithm optimization discoveries
- TSPEC coverage improvements
- SPEC clarification needs
- TASKS decomposition refinements
- Performance baseline updates
- Edge case handling additions

### 1.2 Workflow Path

```
DESIGN TRIGGER (L9-L11)
         │
         ▼
   ┌──────────────────────────────────────┐
   │ Does change affect L5-L8?            │
   │ (Architecture/Contract/Requirements) │
   └─────────────────┬────────────────────┘
                     │
         ┌───────────┼───────────┐
         │ Yes       │           │ No
         ▼           │           ▼
     GATE-05         │       GATE-09
     (Bubble Up)     │       (Entry)
         │           │           │
         ▼           │           │
     Update L5-L8    │           │
         │           │           │
         ▼           │           │
     GATE-09 ◄───────┘           │
         │                       │
         └───────────────────────┘
                     │
                     ▼
              ┌──────────────┐
              │  TDD ORDER:  │
              │  1. TSPEC    │
              │  2. SPEC     │
              │  3. TASKS    │
              └──────┬───────┘
                     │
                     ▼
                 GATE-12
                     │
                     ▼
                 DEPLOYED
```

## 2. Pre-Workflow Checklist

Before initiating the design change workflow:

```markdown
- [ ] Design rationale documented
- [ ] Upstream impact assessed (does this affect L5-L8?)
- [ ] TDD order planned (TSPEC first)
- [ ] Performance baseline documented (if algorithm change)
- [ ] Change level proposed (L1/L2/L3)
- [ ] SPEC implementation readiness score reviewed
```

## 3. TDD Compliance Requirements

**Critical Rule**: All design changes MUST follow TDD order:

```
┌─────────────────────────────────────────────────────┐
│              TDD ORDER FOR DESIGN CHANGES           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. TSPEC (L10) ◄── Update test specifications FIRST│
│      │                                              │
│      ▼                                              │
│  2. SPEC (L9)  ◄── Then update implementation spec │
│      │                                              │
│      ▼                                              │
│  3. TASKS (L11) ◄── Finally update task breakdown  │
│      │                                              │
│      ▼                                              │
│  4. Code (L12) ◄── Implement to pass tests         │
│      │                                              │
│      ▼                                              │
│  5. Tests (L13) ◄── Run tests (should pass now)   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3.1 TDD Compliance Violations

| Violation | Error Code | Resolution |
|-----------|------------|------------|
| SPEC changed without TSPEC | GATE-09-E005 | Update TSPEC first |
| TASKS created without SPEC link | GATE-09-E003 | Add @spec tag |
| Code written before TSPEC | GATE-12-W001 | Retroactive TSPEC update |

## 4. Step-by-Step Process

### Step 1: Change Request Initialization

| Action | Details |
|--------|---------|
| Create CHG directory | `docs/CHG/CHG-XX_short_name/` |
| Use template | L1: commit only, L2: `CHG-MVP-TEMPLATE.md`, L3: `CHG-TEMPLATE.md` |
| Set change source | `design-optimization` |
| Identify entry layer | Layer 9-11 where change originates |

```yaml
# CHG frontmatter
custom_fields:
  change_source: design-optimization
  entry_gate: GATE-09
  tdd_compliance: true
```

### Step 2: Bubble-Up Assessment

Check if change affects L5-L8:

| Layer Impact | Decision |
|--------------|----------|
| Affects REQ (L7) | Bubble up to GATE-05 |
| Affects CTR (L8) | Bubble up to GATE-05 |
| Affects SYS (L6) | Bubble up to GATE-05 |
| Affects ADR (L5) | Bubble up to GATE-05 |
| L9-L11 only | Proceed with GATE-09 |

### Step 3: GATE-09 Entry

**Validation Requirements**:

| Check | L1 | L2 | L3 |
|-------|----|----|---|
| SPEC readiness score >= 90% | Yes | Yes | Yes |
| TSPEC interface coverage | Yes | Yes | Yes |
| TDD order compliance | Yes | Yes | Yes |
| Performance baseline (if algo) | - | Yes | Yes |

**Run validation**:
```bash
./CHG/scripts/validate_gate09.sh CHG-XX_change/CHG-XX_change.md
```

### Step 4: Update Design Layers (TDD Order)

#### 4.1 Update TSPEC First (L10)

```markdown
## TSPEC Updates
- [ ] New interface test cases added
- [ ] Edge case coverage expanded
- [ ] Negative test cases included
- [ ] Performance test baseline updated (if applicable)
- [ ] Test types coverage verified:
  - [ ] UTEST-40: Unit tests
  - [ ] ITEST-41: Integration tests
  - [ ] STEST-42: Smoke tests
  - [ ] FTEST-43: Functional tests
```

#### 4.2 Update SPEC Second (L9)

```markdown
## SPEC Updates
- [ ] Algorithm/logic documented
- [ ] Interface definitions updated
- [ ] Error handling specified
- [ ] Constraints documented
- [ ] Implementation readiness score calculated
```

#### 4.3 Update TASKS Third (L11)

```markdown
## TASKS Updates
- [ ] Tasks linked to SPEC (@spec:)
- [ ] Tasks linked to TSPEC (@tspec:)
- [ ] Dependencies mapped
- [ ] Effort estimates updated
- [ ] No circular dependencies
```

### Step 5: GATE-12 Implementation

**Validation**:
```bash
./CHG/scripts/validate_gate12.sh CHG-XX_change/CHG-XX_change.md
```

**Implementation Order**:

| Step | Action | Validation |
|------|--------|------------|
| 1 | Write code | Implement SPEC |
| 2 | Run tests | TSPEC tests should pass |
| 3 | Validate | L14 validation checklist |

### Step 6: Closure

```markdown
## Closure Checklist
- [ ] GATE-09 passed
- [ ] GATE-12 passed
- [ ] TDD order followed
- [ ] All tests passing
- [ ] Traceability updated
- [ ] CHG status set to "Completed"
```

## 5. Change Level Specifics

### 5.1 L1 Patch (Design)

Common for:
- TSPEC typo corrections
- SPEC clarification (no behavior change)
- TASKS estimate adjustments

**Process**: Direct edit, no CHG document required
**TDD Compliance**: Still required for SPEC changes

### 5.2 L2 Minor (Design)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-MVP-TEMPLATE.md |
| Approvals | Technical Lead |
| Cascade | L9-L14 |
| Timeline | 1-3 business days |

### 5.3 L3 Major (Design)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-TEMPLATE.md |
| Approvals | TL + Domain Expert |
| Cascade | May include L5-L8 via bubble-up |
| Archive Required | Yes |
| Timeline | 3-10 business days |

## 6. Common Scenarios

### Scenario 1: Algorithm Optimization

```
Trigger: Better sorting algorithm discovered
Change Level: L2 (performance improvement)

1. Create CHG-XX_algo_optimization/
2. Document current performance baseline
3. GATE-09 (TDD Order):
   a. Update TSPEC with performance test
   b. Update SPEC with new algorithm
   c. Update TASKS with implementation work
4. GATE-12: Implement and verify
```

### Scenario 2: Edge Case Coverage

```
Trigger: QA found uncovered edge case
Change Level: L1 or L2 (depends on impact)

1. If L1: Direct TSPEC update
2. If L2: Create CHG-XX_edge_case/
3. GATE-09:
   a. Add edge case to TSPEC
   b. Update SPEC if behavior unclear
   c. Update TASKS if new work needed
4. GATE-12: Implement edge case handling
```

### Scenario 3: SPEC Clarification

```
Trigger: Implementer needs clarity on interface
Change Level: L1 (clarification only)

1. Direct edit to SPEC (no behavior change)
2. Verify TSPEC still aligned
3. No GATE-09 formal process needed
4. Commit with clarification note
```

### Scenario 4: Test Coverage Improvement

```
Trigger: Coverage analysis shows gaps
Change Level: L2 (test enhancement)

1. Create CHG-XX_test_coverage/
2. GATE-09:
   a. Update TSPEC with new test cases
   b. Verify SPEC alignment
   c. No TASKS change typically
3. GATE-12: Implement new tests
```

## 7. Performance Change Protocol

For algorithm or performance-related changes:

### 7.1 Pre-Change Baseline

```markdown
## Performance Baseline (Required for algorithm changes)
- Current metric: [e.g., 150ms average response time]
- Measurement method: [e.g., pytest-benchmark]
- Sample size: [e.g., 1000 iterations]
- Environment: [e.g., CI/CD runner specs]
```

### 7.2 Post-Change Validation

```markdown
## Performance Validation
- New metric: [e.g., 75ms average response time]
- Improvement: [e.g., 50% reduction]
- Regression check: [e.g., no other metrics degraded]
- TSPEC performance test: [e.g., test_performance_baseline]
```

## 8. Validation Script Integration

```bash
# Full workflow validation
./CHG/scripts/validate_all_gates.sh CHG-XX_change/CHG-XX_change.md --source=design-optimization

# TDD compliance check
./CHG/scripts/validate_gate09.sh CHG-XX_change/CHG-XX_change.md --check-tdd-order

# SPEC readiness score
python CHG/scripts/validate_chg_routing.py CHG-XX_change/CHG-XX_change.md --spec-readiness

# Individual gate validation
./CHG/scripts/validate_gate09.sh CHG-XX_change/CHG-XX_change.md
./CHG/scripts/validate_gate12.sh CHG-XX_change/CHG-XX_change.md
```

---

**Related Documents**:
- [../gates/GATE-09_DESIGN_TEST.md](../gates/GATE-09_DESIGN_TEST.md)
- [MIDSTREAM_WORKFLOW.md](./MIDSTREAM_WORKFLOW.md) (for bubble-up cases)
- [../CHG-MVP-TEMPLATE.md](../CHG-MVP-TEMPLATE.md)
