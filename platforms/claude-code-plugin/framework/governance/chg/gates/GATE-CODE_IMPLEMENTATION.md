---
title: "GATE-CODE: Implementation Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: "CODE"
  layer_range: "Code"
  layer_names: ["Code"]
---

# GATE-CODE: Implementation Gate

> **Position**: Before Code (source code implementation)
> **Change Sources**: Implementation, Feedback (defects), Cascade from GATE-08
> **Purpose**: Validate implementation changes and ensure proper root cause analysis

## 1. Purpose & Scope

GATE-CODE validates changes to source code. It is the final gate before deployment. All code changes must pass TDD test suites, maintain code quality standards, and demonstrate that fixes address root causes rather than symptoms. IPLAN (L8) is the immediate upstream documentation layer.

### 1.1 Layer Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| Code | Source Code | Source code implementation — C4-L4 level |

### 1.2 Immediate Upstream

IPLAN (L8) provides the execution plan: file manifest, creation order, session handoff protocol, and audit trail. Code changes that diverge from IPLAN must update IPLAN first.

### 1.3 Typical Change Sources

- **Implementation**: Code development per IPLAN
- **Feedback**: Production incidents, user-reported defects, performance issues
- **Cascade**: Implementation of upstream changes (GATE-01/03/06/08 passed)

## 2. Entry Criteria

Before entering GATE-CODE, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Root cause analysis completed | Yes | Documented in CHG or ticket |
| Fix at correct layer determined | Yes | Layer assignment justification |
| Regression scope identified | Yes | Affected test areas listed |
| IPLAN updated (if file manifest changes) | Conditional | IPLAN reflects current file list |
| TDD test suite defined | Yes | Test cases exist for changed code |
| If cascade: upstream gates passed | Conditional | GATE-01/03/06/08 approval |
| If feedback: incident documented | Conditional | Incident reference |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Root cause analysis documented
- [ ] Fix layer determined (not symptom masking)
- [ ] Regression test scope identified
- [ ] IPLAN updated if file manifest changed
- [ ] TDD test cases cover the change
- [ ] If defect: linked to issue tracker
- [ ] If cascade: upstream gates confirmed
- [ ] If hotfix: emergency flag set
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-CODE-E001 | Root cause analysis must be completed | ERROR | RCA section present |
| GATE-CODE-E002 | Fix must be at correct layer (not symptom masking) | ERROR | Layer justification |
| GATE-CODE-E003 | Code must pass TDD test suite | ERROR | Test suite green |
| GATE-CODE-E004 | Code review required for C2/C3 changes | ERROR | Review approval |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-CODE-W001 | Performance regression without baseline | WARNING | Benchmark before and after |
| GATE-CODE-W002 | Build warning introduced | WARNING | Fix or document rationale |
| GATE-CODE-W003 | Technical debt documented with tracking ticket | WARNING | Create follow-up issue |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **C1** | Self + Peer Review | Immediate |
| **C2** | Technical Lead + QA Lead | 2 business days |
| **C3** | TL + Architect | 3 business days |

### 4.2 Code Review Requirements

| Change Type | Reviewers Required | Coverage |
|-------------|-------------------|----------|
| C1 Bug fix | 1 peer reviewer | Changed files |
| C2 Feature | 2 reviewers (1 senior) | Changed files + integration |
| C3 Architecture | 3 reviewers + architect | Full module |

### 4.3 Escalation Path

```
C1 (Self + Peer Review)
      
       (if test failure persists)
C2 (TL + QA)
      
       (if root cause is upstream)
Bubble Up to GATE-08/06/03/01
```

## 5. Exit Criteria

To pass GATE-CODE, the change must satisfy:

| Criterion | C1 | C2 | C3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| Root cause documented | Yes | Yes | Yes |
| TDD test suite passes | Yes | Yes | Yes |
| Code review approved | Peer | TL | Architect |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-CODE-E* checks all pass
- [ ] GATE-CODE-W* checks reviewed
- [ ] Root cause analysis documented
- [ ] Fix implemented at correct layer
- [ ] TDD test suite passing
- [ ] Code review approved
- [ ] IPLAN audit trail updated
- [ ] Ready for merge
```

## 6. Routing Rules

After passing GATE-CODE:

| Scenario | Next Step |
|----------|-----------|
| Standard fix | Merge to main branch |
| C3 change | Post-deployment validation |
| Root cause requires upstream fix | Bubble up to GATE-08/06/03/01 |
| Emergency hotfix | Fast-track with post-mortem |

### 6.1 Root Cause Layer Detection

```
Test Failure Analysis:
      
      
  Where is the actual problem?
      
      
  Code bug?               → Fix Code → GATE-CODE
  IPLAN wrong order?      → Fix IPLAN → GATE-08
  TDD missing test?       → Fix TDD → GATE-06
  SPEC interface wrong?   → Fix SPEC → GATE-06
  ADR decision wrong?     → Fix ADR → GATE-03
  BDD scenario missing?   → Fix BDD → GATE-03
  EARS requirement wrong? → Fix EARS → GATE-03
  PRD feature wrong?      → Fix PRD → GATE-01
  BRD objective wrong?    → Fix BRD → GATE-01
```

### 6.2 Bubble-Up Process

When root cause is upstream:

1. Document finding in current CHG
2. Create a new CHG for the upstream fix, with its own
   [`GATE_APPROVAL_FORM`](../templates/GATE_APPROVAL_FORM.md) — do **not** record
   the upstream gates on the current change's form
3. Route to appropriate gate
4. Current change becomes dependent on upstream CHG

## 7. Error Catalog

### 7.1 GATE-CODE Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-CODE-E001 | Analysis | Missing root cause analysis | Add RCA section with 5-Whys or fishbone |
| GATE-CODE-E002 | Layer | Symptom masking detected | Trace to actual problem layer |
| GATE-CODE-E003 | Testing | TDD test suite failing | Fix code to pass TDD test cases |
| GATE-CODE-E004 | Review | Code review not approved | Complete review process |
| GATE-CODE-W001 | Performance | Regression without baseline | Benchmark before and after |
| GATE-CODE-W002 | Quality | Build warning introduced | Fix or document rationale |
| GATE-CODE-W003 | Debt | Technical debt without tracking | Create follow-up issue |

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
- [ ] TDD test cases cover the scenario
```

## 8. Special Considerations

### 8.1 Defect vs. Design Decision

| Indicator | Classification | Action |
|-----------|---------------|--------|
| Code doesn't match SPEC | Defect (C1) | Fix code |
| SPEC doesn't match ADR/BDD | Design issue (C2) | GATE-06 |
| BDD doesn't match EARS | Requirements issue | GATE-03 |
| Business rule is wrong | Business issue | GATE-01 |
| IPLAN order is wrong | Execution issue | GATE-08 |

### 8.2 Performance Fix Checklist

```markdown
- [ ] Baseline performance documented
- [ ] Bottleneck identified with profiling
- [ ] Fix benchmarked against baseline
- [ ] TDD test cases updated with performance thresholds
- [ ] No regression in other areas
```

### 8.3 Security Fix Checklist

```markdown
- [ ] Vulnerability classified (CVSS)
- [ ] Fix addresses root cause
- [ ] Security review completed
- [ ] Security test added to TDD
- [ ] Disclosure timeline followed
```

---

**Related Documents**:
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../templates/GATE_APPROVAL_FORM.md](../templates/GATE_APPROVAL_FORM.md)
