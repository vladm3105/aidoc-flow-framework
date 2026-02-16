---
title: "GATE-01: Business/Product Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: 1
  layer_range: "L1-L4"
  layer_names: ["BRD", "PRD", "EARS", "BDD"]
  development_status: active
---

# GATE-01: Business/Product Gate (L1-L4)

> **Position**: Before Layers 1-4 (BRD, PRD, EARS, BDD)
> **Change Sources**: Upstream, External (business impact)
> **Purpose**: Validate business/product changes before cascading to architecture

## 1. Purpose & Scope

GATE-01 validates changes originating from business requirements, product decisions, market feedback, or regulatory compliance. It ensures that changes to foundational layers (L1-L4) are properly justified, scoped, and have stakeholder approval before cascading downstream.

### 1.1 Layers Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| L1 | BRD | Business Requirements Document |
| L2 | PRD | Product Requirements Document |
| L3 | EARS | Easy Approach to Requirements Syntax |
| L4 | BDD | Behavior-Driven Development Scenarios |

### 1.2 Typical Change Sources

- **Upstream**: Market requirements, stakeholder requests, business strategy pivots
- **External (Business)**: Regulatory changes, compliance requirements, partner demands
- **Feedback (Strategic)**: User research insights affecting product direction

## 2. Entry Criteria

Before entering GATE-01, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Business justification documented | Yes | Written rationale with measurable impact |
| Stakeholder identified | Yes | Named sponsor for the change |
| Change source classified | Yes | One of 5 sources identified |
| Preliminary scope defined | Yes | Affected layers estimated |
| Change level proposed | Yes | L1/L2/L3 classification with justification |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Change request has business justification
- [ ] Sponsoring stakeholder identified
- [ ] Change source documented (Upstream/External/Feedback)
- [ ] Initial scope assessment completed
- [ ] Change level (L1/L2/L3) proposed
- [ ] For L3: Architecture board notified
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-01-E001 | BRD change must have business justification | ERROR | `grep -E "Business Justification|Rationale" CHG.md` |
| GATE-01-E002 | PRD change must link to BRD objective | ERROR | `@brd:` tag present and valid |
| GATE-01-E003 | EARS must follow WHEN-THE-SHALL syntax | ERROR | Syntax validation script |
| GATE-01-E004 | BDD must have Given-When-Then format | ERROR | Feature file syntax check |
| GATE-01-E005 | Breaking change missing L3 classification | ERROR | Change level validation |
| GATE-01-E006 | No stakeholder approval for L3 change | ERROR | Approval signature present |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-01-W001 | Large scope (>5 layers) without L3 | WARNING | Consider elevating to L3 |
| GATE-01-W002 | Missing stakeholder sign-off for L2 | WARNING | Obtain PO approval |
| GATE-01-W003 | Cascade affects >10 artifacts | WARNING | Create implementation plan |
| GATE-01-W004 | External trigger without CVE/compliance ref | WARNING | Add reference number |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **L1** | Self (author) | Immediate |
| **L2** | Product Owner + Technical Lead | 2 business days |
| **L3** | PO + Architect + Stakeholder | 5 business days |

### 4.2 Escalation Path

```
L1 (Self-approved)
     │
     ▼ (if scope expands)
L2 (PO + TL)
     │
     ▼ (if breaking change detected)
L3 (Full Board)
```

### 4.3 Approval Form

For L2/L3 changes, complete `templates/GATE_APPROVAL_FORM.md` with:

- Change summary
- Impact assessment
- Risk analysis
- Approver signatures

## 5. Exit Criteria

To pass GATE-01, the change must satisfy:

| Criterion | L1 | L2 | L3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| Business justification complete | No | Yes | Yes |
| Stakeholder approval obtained | No | Yes | Yes |
| Implementation scope documented | No | Yes | Yes |
| Rollback plan documented | No | No | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-01-E* checks all pass
- [ ] GATE-01-W* checks reviewed (L2/L3: documented decisions)
- [ ] CHG document created (L2/L3)
- [ ] Approvals obtained per matrix
- [ ] Cascade scope finalized
- [ ] Ready to proceed to affected layers
```

## 6. Routing Rules

After passing GATE-01:

| Scenario | Next Step |
|----------|-----------|
| Change affects L5-L8 (ADR, SYS, REQ, CTR) | Proceed to GATE-05 |
| Change affects L9-L11 only (SPEC, TSPEC, TASKS) | Proceed to GATE-09 |
| Change affects L12-L14 only (Code, Tests, Val) | Proceed to GATE-12 |
| L1 Patch (single layer fix) | Direct implementation |

### 6.1 Routing Flowchart

```
                    GATE-01 PASSED
                          │
                          ▼
            ┌─────────────────────────┐
            │ Does change affect ADR? │
            └───────────┬─────────────┘
                        │
         ┌──────────────┼──────────────┐
         │ Yes          │              │ No
         ▼              │              ▼
    ┌─────────┐         │       ┌─────────────────┐
    │ GATE-05 │         │       │ SPEC/TSPEC only?│
    └─────────┘         │       └────────┬────────┘
                        │                │
                        │     ┌──────────┼──────────┐
                        │     │ Yes      │          │ No
                        │     ▼          │          ▼
                        │ ┌─────────┐    │    ┌─────────┐
                        │ │ GATE-09 │    │    │ GATE-12 │
                        │ └─────────┘    │    └─────────┘
                        │                │
```

## 7. Error Catalog

### 7.1 GATE-01 Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-01-E001 | Documentation | Missing business justification | Add "Business Justification" section with measurable impact |
| GATE-01-E002 | Traceability | PRD missing BRD linkage | Add `@brd:` tag with valid BRD reference |
| GATE-01-E003 | Syntax | EARS syntax violation | Fix WHEN-THE-SHALL-WITHIN format |
| GATE-01-E004 | Syntax | BDD format violation | Fix Given-When-Then structure |
| GATE-01-E005 | Classification | Breaking change misclassified | Escalate change level to L3 |
| GATE-01-E006 | Approval | Missing L3 stakeholder approval | Obtain and document approval |
| GATE-01-W001 | Scope | Large cascade scope | Consider L3 upgrade or phase implementation |
| GATE-01-W002 | Approval | Missing L2 approval | Obtain PO sign-off |
| GATE-01-W003 | Planning | High artifact count | Create detailed implementation plan |
| GATE-01-W004 | Documentation | External trigger missing reference | Add CVE/compliance reference |

### 7.2 Common Resolutions

```markdown
## GATE-01-E001 Resolution
Add section to CHG document:

### Business Justification
- **Business Need**: [Specific business problem being solved]
- **Expected Outcome**: [Measurable business impact]
- **Success Metrics**: [KPIs to measure success]

## GATE-01-E002 Resolution
Add traceability tag to PRD:

@brd: BRD-XXX (Objective Y.Z)

## GATE-01-E003 Resolution
Fix EARS statement format:

WHEN [trigger condition]
THE [system/component]
SHALL [action/behavior]
WITHIN [time constraint]
```

## 8. Validation Script

Validation is performed by `scripts/validate_gate01.sh`:

```bash
# Usage
./CHG/scripts/validate_gate01.sh <CHG_FILE> [--verbose]

# Exit Codes
# 0 = Pass (no errors, no warnings)
# 1 = Pass with warnings (non-blocking)
# 2 = Fail (blocking errors)
```

---

**Related Documents**:
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../workflows/UPSTREAM_WORKFLOW.md](../workflows/UPSTREAM_WORKFLOW.md)
- [../templates/GATE_APPROVAL_FORM.md](../templates/GATE_APPROVAL_FORM.md)
