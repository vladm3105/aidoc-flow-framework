---
title: "GATE-06: Design & Test Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: 6
  layer_range: "L6-L7"
  layer_names: ["SPEC", "TDD"]
---

# GATE-06: Design & Test Gate (L6-L7)

> **Position**: Before Layers 6-7 (SPEC, TDD)
> **Change Sources**: Design, Midstream cascade from GATE-03, implementation feedback
> **Purpose**: Validate technical specifications and test definitions before execution planning

## 1. Purpose & Scope

GATE-06 validates changes to technical specifications (SPEC) and test case definitions (TDD). SPEC defines component contracts; TDD defines how those contracts are validated. Changes must maintain SPEC→TDD consistency. This gate ensures specification quality before IPLAN execution begins.

### 1.1 Layers Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| L6 | SPEC | Technical Specification — interfaces, data models, behavior contracts |
| L7 | TDD | Test-Driven Development Guide — test case definitions, BDD-to-test mapping, quality thresholds |

### 1.2 Typical Change Sources

- **Design**: Algorithm improvements, interface optimization, performance tuning
- **Midstream Cascade**: Changes flowing from GATE-03 (ADR/BDD/EARS)
- **Feedback (Technical)**: Implementation insights requiring spec adjustments

## 2. Entry Criteria

Before entering GATE-06, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Technical design documented | Yes | SPEC section completeness |
| TDD coverage assessed | Yes | BDD scenario mapping verified |
| Upstream gates passed (if cascade) | Conditional | GATE-01/03 approval documented |
| Performance baseline (if algorithm change) | Conditional | Current metrics documented |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] SPEC changes documented with rationale
- [ ] TDD test cases cover all changed SPEC interfaces
- [ ] BDD-to-TDD scenario mapping verified
- [ ] If cascade: upstream gates confirmed passed
- [ ] If algorithm/interface change: baseline metrics documented
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-06-E001 | SPEC must have TDD-Ready score >= 90% | ERROR | Score check |
| GATE-06-E002 | TDD must cover all BDD scenarios | ERROR | BDD-to-TDD coverage check |
| GATE-06-E003 | TDD/SPEC sync: test contracts must match SPEC interfaces | ERROR | Cross-reference validation |
| GATE-06-E004 | SPEC change must update TDD before proceeding | ERROR | TDD compliance check |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-06-W001 | Algorithm change without performance baseline | WARNING | Document current metrics |
| GATE-06-W002 | SPEC implementation complexity > 4 | WARNING | Consider decomposition |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **C1** | Self (author) | Immediate |
| **C2** | Technical Lead | 2 business days |
| **C3** | Technical Lead + Domain Expert | 3 business days |

### 4.2 SPEC-TDD Consistency Requirement

All SPEC changes MUST flow through TDD:

```
1. Update SPEC to define implementation contract
2. Update TDD to define test cases for changed interfaces
3. Verify TDD.Ready score >= 90%
4. Update IPLAN to reflect test-first implementation order
```

### 4.3 Escalation Path

```
C1 (Self-approved)
      
       (if interface change)
C2 (Technical Lead)
      
       (if architecture/performance impact)
C3 (TL + Domain Expert)
```

## 5. Exit Criteria

To pass GATE-06, the change must satisfy:

| Criterion | C1 | C2 | C3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| SPEC TDD-Ready score >= 90% | Yes | Yes | Yes |
| TDD covers all BDD scenarios | Yes | Yes | Yes |
| SPEC-TDD synchronization verified | Yes | Yes | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-06-E* checks all pass
- [ ] GATE-06-W* checks reviewed
- [ ] SPEC has >= 90% TDD-Ready score
- [ ] TDD covers all BDD scenarios with test cases
- [ ] TDD test contracts match SPEC interfaces
- [ ] SPEC change reflected in TDD
- [ ] Approvals obtained per matrix
```

## 6. Routing Rules

After passing GATE-06:

| Scenario | Next Step |
|----------|-----------|
| Standard flow | Proceed to GATE-08 (IPLAN) |
| C1 TDD-only fix | Direct to IPLAN update |
| SPEC interface change | IPLAN in test-first order |

### 6.1 Routing Flowchart

```
                    GATE-06 PASSED
                           
              Ready for execution planning
                    
                     GATE-08
                      IPLAN
                    
                         
          
            Test-first implementation
                     
                     GATE-CODE
```

## 7. Error Catalog

### 7.1 GATE-06 Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-06-E001 | Readiness | SPEC TDD-Ready score < 90% | Complete missing sections, clarify ambiguities |
| GATE-06-E002 | Coverage | TDD missing BDD scenario coverage | Add test case definitions for all BDD scenarios |
| GATE-06-E003 | Consistency | TDD/SPEC misalignment | Synchronize TDD test contracts with SPEC interfaces |
| GATE-06-E004 | Process | SPEC change without TDD update | Update TDD with test cases for changed interfaces |
| GATE-06-W001 | Performance | Algorithm change without baseline | Document current performance metrics |
| GATE-06-W002 | Complexity | High implementation complexity | Consider decomposition into smaller SPEC components |

### 7.2 Common Resolutions

```markdown
## GATE-06-E001 Resolution
Improve SPEC TDD-Ready score:

1. Complete all required sections:
   - Interface definitions with type signatures
   - Data models with validation rules
   - Behavior contracts with pre/post conditions
   - Error handling with error codes

2. Remove ambiguous language:
   - Replace "should" with "SHALL"
   - Quantify thresholds
   - Define edge cases

## GATE-06-E002 Resolution
TDD must cover every BDD scenario:

| BDD Scenario | Test Type | TDD Case |
|--------------|-----------|----------|
| SCEN-001     | Unit      | TC-001   |
| SCEN-002     | Unit      | TC-002   |
| SCEN-003     | Unit      | TC-003   |

## GATE-06-E004 Resolution
Updated SPEC flow:

1. Modify SPEC component interfaces
2. Add/modify TDD test cases for changed interfaces
3. Verify TDD.Ready score
4. Update IPLAN for test-first implementation order
```

---

**Related Documents**:
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../templates/GATE_APPROVAL_FORM.md](../templates/GATE_APPROVAL_FORM.md)
