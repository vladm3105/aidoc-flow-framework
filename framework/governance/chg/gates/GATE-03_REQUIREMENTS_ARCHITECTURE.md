---
title: "GATE-03: Requirements & Architecture Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: 3
  layer_range: "L3-L5"
  layer_names: ["EARS", "BDD", "ADR"]
---

# GATE-03: Requirements & Architecture Gate (L3-L5)

> **Position**: Before Layers 3-5 (EARS, BDD, ADR)
> **Change Sources**: Midstream, External (technical), Upstream cascade from GATE-01
> **Purpose**: Validate formal requirements, acceptance scenarios, and architecture decisions before cascading to design

## 1. Purpose & Scope

GATE-03 validates changes to formal requirements (EARS), behavior-driven scenarios (BDD), and architecture decisions (ADR). These changes form the decision bridge between product requirements and component design. Incorrect or incomplete changes at this level propagate errors through all downstream layers.

### 1.1 Layers Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| L3 | EARS | Formal requirements using WHEN-THE-SHALL-WITHIN syntax |
| L4 | BDD | Behavior-Driven Development acceptance scenarios |
| L5 | ADR | Architecture Decision Records |

### 1.2 Typical Change Sources

- **Midstream**: Formal requirement refinement, acceptance scenario additions, architecture pivots
- **External**: Security vulnerabilities, dependency updates, third-party API changes
- **Upstream (Cascaded)**: Business/product requirements flowing from GATE-01

## 2. Entry Criteria

Before entering GATE-03, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Technical rationale documented | Yes | Context-Decision-Consequences format for ADR |
| Impact on downstream layers assessed | Yes | SPEC/TDD/IPLAN impact analysis |
| Security review (if external) | Conditional | CVE reference or security assessment |
| GATE-01 passed (if upstream cascade) | Conditional | GATE-01 approval documented |
| EARS syntax compliance | Yes | WHEN-THE-SHALL-WITHIN format |
| BDD scenario format | Yes | Given-When-Then format |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Formal requirements use WHEN-THE-SHALL-WITHIN syntax
- [ ] BDD scenarios follow Given-When-Then format
- [ ] ADR has Context-Decision-Consequences sections
- [ ] Downstream impact analysis completed (SPEC/TDD/IPLAN)
- [ ] If external security: CVE/advisory referenced
- [ ] If from GATE-01: upstream approval confirmed
- [ ] For C3: Architecture board notified
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-03-E001 | ADR must document context, decision, consequences | ERROR | Section presence check |
| GATE-03-E002 | Security review for external changes | ERROR | Security assessment present |
| GATE-03-E003 | EARS must follow WHEN-THE-SHALL syntax | ERROR | Syntax validation |
| GATE-03-E004 | BDD must have Given-When-Then format | ERROR | Scenario structure check |
| GATE-03-E005 | EARS upstream tags: @brd @prd (2 tags) | ERROR | Traceability tag count |
| GATE-03-E006 | BDD upstream tags: @brd @prd @ears (3 tags) | ERROR | Traceability tag count |
| GATE-03-E007 | ADR upstream tags: @brd @prd @ears @bdd (4 tags) | ERROR | Traceability tag count |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-03-W001 | External security change without CVE reference | WARNING | Add CVE-YYYY-NNNN reference |
| GATE-03-W002 | ADR alternatives section missing | WARNING | Document considered alternatives |
| GATE-03-W003 | BDD missing edge case coverage | WARNING | Add boundary condition scenarios |
| GATE-03-W004 | EARS missing boundary value coverage | WARNING | Add boundary condition specifications |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **C1** | Self (author) | Immediate |
| **C2** | Technical Lead + Domain Expert | 3 business days |
| **C3** | Architect + Security (if external) | 5 business days |

### 4.2 Special Approval Requirements

| Change Type | Additional Approvers |
|-------------|---------------------|
| Security vulnerability fix | Security team |
| Architecture pivot (ADR change) | Architecture board |
| External requirement change | Legal/Compliance (if regulatory) |

### 4.3 Escalation Path

```
C1 (Self-approved)
      
       (if requirement/architecture change)
C2 (TL + Domain)
      
       (if security or architecture pivot)
C3 (Architect + Security)
```

## 5. Exit Criteria

To pass GATE-03, the change must satisfy:

| Criterion | C1 | C2 | C3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| Technical rationale documented | Yes | Yes | Yes |
| Security review complete | N/A | If external | Yes |
| Migration plan documented | No | No | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-03-E* checks all pass
- [ ] GATE-03-W* checks reviewed
- [ ] ADR has Context-Decision-Consequences
- [ ] EARS uses WHEN-THE-SHALL-WITHIN syntax
- [ ] BDD has Given-When-Then format
- [ ] All traceability tags present and valid
- [ ] Security review complete (if external)
- [ ] Approvals obtained per matrix
```

## 6. Routing Rules

After passing GATE-03:

| Scenario | Next Step |
|----------|-----------|
| Change affects L6-L7 (SPEC, TDD) | Proceed to GATE-06 |
| Change affects L8 (IPLAN) | Proceed to GATE-08 |
| C1 Patch (single layer fix) | Direct implementation |
| Architecture change requiring full cascade | GATE-06 → GATE-08 → GATE-CODE |

### 6.1 Routing Flowchart

```
                    GATE-03 PASSED
                           
             Does change affect SPEC?
             
          
           Yes                         No
                                      
                     
      GATE-06                   IPLAN-only change?
                     
                                         
                              
                               Yes                 No
                                                  
                           GATE-08           Direct fix
                                                  (C1 only)
```

## 7. Error Catalog

### 7.1 GATE-03 Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-03-E001 | Structure | ADR missing required sections | Add Context, Decision, Consequences sections |
| GATE-03-E002 | Security | External change missing security review | Complete security assessment |
| GATE-03-E003 | Syntax | EARS syntax violation | Fix WHEN-THE-SHALL-WITHIN format |
| GATE-03-E004 | Syntax | BDD format violation | Fix Given-When-Then structure |
| GATE-03-E005 | Traceability | EARS missing upstream tags | Add @brd and @prd tags |
| GATE-03-E006 | Traceability | BDD missing upstream tags | Add @brd, @prd, @ears tags |
| GATE-03-E007 | Traceability | ADR missing upstream tags | Add @brd, @prd, @ears, @bdd tags |
| GATE-03-W001 | Documentation | CVE reference missing | Add CVE-YYYY-NNNN to change document |
| GATE-03-W002 | Completeness | ADR alternatives not documented | Add "Considered Alternatives" section |
| GATE-03-W003 | Coverage | BDD edge cases missing | Add boundary condition scenarios |
| GATE-03-W004 | Coverage | EARS boundary values missing | Add boundary condition specifications |

### 7.2 Common Resolutions

```markdown
## GATE-03-E001 Resolution
ADR must contain:

## Context
[What is the issue motivating this decision?]

## Decision
[What is the proposed change?]

## Consequences
[What becomes easier or more difficult because of this change?]

## GATE-03-E003 Resolution
Fix EARS statement format:

WHEN [trigger condition]
THE [system/component]
SHALL [action/behavior]
WITHIN [time constraint]

## GATE-03-E004 Resolution
Fix BDD scenario format:

Given [precondition]
When [action]
Then [expected outcome]

## GATE-03-E007 Resolution
ADR must have all 4 upstream tags:

@brd: BRD-XXX
@prd: PRD-XXX
@ears: EARS-XXX
@bdd: BDD-XXX
```

## 8. Special Considerations

### 8.1 Security Vulnerability Response

For external security changes:

| CVSS Score | Response Time | Gate Process |
|------------|---------------|--------------|
| Critical (9.0-10.0) | 24 hours | Emergency Bypass |
| High (7.0-8.9) | 72 hours | Expedited GATE-03 |
| Medium (4.0-6.9) | 7 days | Standard GATE-03 |
| Low (0.1-3.9) | 30 days | Standard GATE-03 |

---

**Related Documents**:

- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../templates/GATE_APPROVAL_FORM.md](../templates/GATE_APPROVAL_FORM.md)
