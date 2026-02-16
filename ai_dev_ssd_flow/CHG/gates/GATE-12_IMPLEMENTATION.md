---
title: "GATE-12: Implementation Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: 12
  layer_range: "L12-L14"
  layer_names: ["Code", "Tests", "Validation"]
  development_status: active
---

# GATE-12: Implementation Gate (L12-L14)

> **Position**: Before Layers 12-14 (Code, Tests, Validation)
> **Change Sources**: Downstream, Feedback (defects)
> **Purpose**: Validate implementation changes and ensure proper root cause analysis

## 1. Purpose & Scope

GATE-12 validates changes originating from code, test implementations, and validation processes. It ensures that defect fixes address root causes rather than symptoms and maintains code quality standards.

### 1.1 Layers Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| L12 | Code | Source code implementation |
| L13 | Tests | Test implementations |
| L14 | Validation | Production readiness validation |

### 1.2 Typical Change Sources

- **Downstream**: Bug fixes, code refactoring, test fixes
- **Feedback**: Production incidents, user-reported defects, performance issues
- **Cascade**: Implementation of upstream changes (GATE-01/05/09 passed)

## 2. Entry Criteria

Before entering GATE-12, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Root cause analysis completed | Yes | Documented in CHG or ticket |
| Fix at correct layer determined | Yes | Layer assignment justification |
| Regression scope identified | Yes | Affected test areas listed |
| If cascade: upstream gates passed | Conditional | GATE-01/05/09 approval |
| If feedback: incident documented | Conditional | Incident reference |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Root cause analysis documented
- [ ] Fix layer determined (not symptom masking)
- [ ] Regression test scope identified
- [ ] If defect: linked to issue tracker
- [ ] If cascade: upstream gates confirmed
- [ ] If hotfix: emergency flag set
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-12-E001 | Root cause analysis must be completed | ERROR | RCA section present |
| GATE-12-E002 | Fix must be at correct layer (not symptom masking) | ERROR | Layer justification |
| GATE-12-E003 | Regression tests must be included | ERROR | Test files present |
| GATE-12-E004 | Code review required for L2/L3 changes | ERROR | Review approval |
| GATE-12-E005 | Build must pass before merge | ERROR | CI pipeline green |
| GATE-12-E006 | Test coverage must not decrease | ERROR | Coverage delta check |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-12-W001 | Code fix without corresponding TSPEC update | WARNING | Update TSPEC for TDD compliance |
| GATE-12-W002 | Large code change classified as L1 | WARNING | Consider L2 classification |
| GATE-12-W003 | Performance-critical code without benchmark | WARNING | Add performance test |
| GATE-12-W004 | Security-sensitive code without security review | WARNING | Request security review |
| GATE-12-W005 | Dead code detected | WARNING | Remove unused code |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **L1** | Self (author) | Immediate |
| **L2** | Technical Lead + QA Lead | 2 business days |
| **L3** | TL + Architect | 3 business days |

### 4.2 Code Review Requirements

| Change Type | Reviewers Required | Coverage |
|-------------|-------------------|----------|
| L1 Bug fix | 1 peer reviewer | Changed files |
| L2 Feature | 2 reviewers (1 senior) | Changed files + integration |
| L3 Architecture | 3 reviewers + architect | Full module |

### 4.3 Escalation Path

```
L1 (Self + Peer Review)
     │
     ▼ (if test failure persists)
L2 (TL + QA)
     │
     ▼ (if root cause is upstream)
Bubble Up to GATE-09/05/01
```

## 5. Exit Criteria

To pass GATE-12, the change must satisfy:

| Criterion | L1 | L2 | L3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| Root cause documented | Yes | Yes | Yes |
| Regression tests pass | Yes | Yes | Yes |
| Code review approved | Peer | TL | Architect |
| Coverage maintained | Yes | Yes | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-12-E* checks all pass
- [ ] GATE-12-W* checks reviewed
- [ ] Root cause analysis documented
- [ ] Fix implemented at correct layer
- [ ] Regression tests included and passing
- [ ] Code review approved
- [ ] CI/CD pipeline green
- [ ] Coverage maintained or improved
```

## 6. Routing Rules

After passing GATE-12:

| Scenario | Next Step |
|----------|-----------|
| Standard fix | Merge to main branch |
| L3 change | Post-deployment validation |
| Root cause requires upstream fix | Bubble up to GATE-09/05/01 |
| Emergency hotfix | Fast-track with post-mortem |

### 6.1 Root Cause Layer Detection

```
Test Failure Analysis:
     │
     ▼
┌───────────────────────────────────────┐
│ Where is the actual problem?          │
├───────────────────────────────────────┤
│                                       │
│ Code bug (L12)?          → Fix L12    │
│                                       │
│ Test spec wrong (L10)?   → Fix TSPEC  │
│                          → GATE-09    │
│                                       │
│ SPEC ambiguous (L9)?     → Fix SPEC   │
│                          → GATE-09    │
│                                       │
│ Contract mismatch (L8)?  → Fix CTR    │
│                          → GATE-05    │
│                                       │
│ Requirement unclear (L7)?→ Fix REQ    │
│                          → GATE-05    │
│                                       │
│ Business rule wrong?     → GATE-01    │
│                                       │
└───────────────────────────────────────┘
```

### 6.2 Bubble-Up Process

When root cause is upstream:

1. Document finding in current CHG
2. Create new CHG for upstream fix
3. Route to appropriate gate
4. Current change becomes dependent on upstream CHG

## 7. Error Catalog

### 7.1 GATE-12 Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-12-E001 | Analysis | Missing root cause analysis | Add RCA section with 5-Whys or fishbone |
| GATE-12-E002 | Layer | Symptom masking detected | Trace to actual problem layer |
| GATE-12-E003 | Testing | Regression tests missing | Add tests covering the fix |
| GATE-12-E004 | Review | Code review not approved | Complete review process |
| GATE-12-E005 | Build | CI pipeline failing | Fix build errors |
| GATE-12-E006 | Coverage | Test coverage decreased | Add tests to maintain coverage |
| GATE-12-W001 | TDD | TSPEC not updated | Update test specifications |
| GATE-12-W002 | Classification | Large change as L1 | Consider L2 classification |
| GATE-12-W003 | Performance | Missing benchmark | Add performance test |
| GATE-12-W004 | Security | Security review needed | Request security review |
| GATE-12-W005 | Quality | Dead code present | Remove unused code |

### 7.2 Root Cause Analysis Template

```markdown
## Root Cause Analysis

### Problem Statement
[What was the observed problem?]

### 5-Whys Analysis
1. Why? [First-level cause]
2. Why? [Second-level cause]
3. Why? [Third-level cause]
4. Why? [Fourth-level cause]
5. Why? [Root cause]

### Root Cause Layer
**Layer**: L[N] - [Layer Name]
**Justification**: [Why this is the correct layer to fix]

### Fix Verification
- [ ] Fix addresses root cause (not symptom)
- [ ] Similar issues prevented by this fix
- [ ] Regression tests cover the scenario
```

## 8. Special Considerations

### 8.1 Defect vs. Design Decision

| Indicator | Classification | Action |
|-----------|---------------|--------|
| Code doesn't match SPEC | Defect (L1) | Fix code |
| SPEC doesn't match requirement | Design issue (L2) | GATE-09 |
| Requirement is unclear | Requirements issue | GATE-05 |
| Business rule is wrong | Business issue | GATE-01 |

### 8.2 Performance Fix Checklist

For performance-related fixes:

```markdown
- [ ] Baseline performance documented
- [ ] Bottleneck identified with profiling
- [ ] Fix benchmarked against baseline
- [ ] Performance test added to TSPEC
- [ ] No regression in other areas
```

### 8.3 Security Fix Checklist

For security-related fixes:

```markdown
- [ ] Vulnerability classified (CVSS)
- [ ] Fix addresses root cause
- [ ] Security review completed
- [ ] Security test added
- [ ] Disclosure timeline followed
```

## 9. Validation Script

Validation is performed by `scripts/validate_gate12.sh`:

```bash
# Usage
./CHG/scripts/validate_gate12.sh <CHG_FILE> [--verbose]

# Exit Codes
# 0 = Pass (no errors, no warnings)
# 1 = Pass with warnings (non-blocking)
# 2 = Fail (blocking errors)
```

---

**Related Documents**:
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../workflows/DOWNSTREAM_WORKFLOW.md](../workflows/DOWNSTREAM_WORKFLOW.md)
- [../workflows/EMERGENCY_WORKFLOW.md](../workflows/EMERGENCY_WORKFLOW.md)
