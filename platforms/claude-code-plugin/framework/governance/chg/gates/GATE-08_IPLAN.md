---
title: "GATE-08: IPLAN Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: 8
  layer_range: "L8"
  layer_names: ["IPLAN"]
---

# GATE-08: IPLAN Gate (L8)

> **Position**: Before Layer 8 (IPLAN)
> **Change Sources**: Design cascade from GATE-06, execution adjustment
> **Purpose**: Validate implementation plans before code generation — the last documentation gate before source code

## 1. Purpose & Scope

GATE-08 validates changes to Implementation Plans (IPLAN). IPLAN is the execution bridge between TDD test definitions and source code — its file manifest, command sequence, session handoff, and audit trail must be correct and complete. Errors in IPLAN result in incorrect or incomplete code generation.

### 1.1 Layer Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| L8 | IPLAN | Implementation Plan — file manifest, bash commands, session handoff, code audit trail |

### 1.2 Typical Change Sources

- **Design Cascade**: SPEC/TDD changes flowing from GATE-06
- **Execution Adjustment**: Reordering implementation steps, adding files, updating commands
- **Feedback**: Session handoff improvements from implementation experience

## 2. Entry Criteria

Before entering GATE-08, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Upstream gates passed | Yes | GATE-01/03/06 approval documented |
| TDD test cases defined | Yes | TDD document exists with test cases |
| File manifest defined | Yes | Complete list of files to create/modify |
| Test-first order enforced | Yes | Test files listed before implementation files |
| Session handoff documented | Yes | State variables described |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Upstream gates (GATE-01/03/06) confirmed passed
- [ ] TDD document exists with test case definitions
- [ ] File manifest is complete (no missing files)
- [ ] Test files listed before implementation files
- [ ] Bash commands are exact and executable
- [ ] Session handoff protocol described
- [ ] Temporary plan location (IPLAN/tmp/) for bugfixes
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-08-E001 | IPLAN must have complete file manifest | ERROR | File list matches SPEC component scope |
| GATE-08-E002 | Test-first order: test files before implementation files | ERROR | Parse file manifest order |
| GATE-08-E003 | IPLAN must reference upstream SPEC and TDD | ERROR | `@spec:` and `@tdd:` tags present |
| GATE-08-E004 | Session handoff protocol documented | ERROR | State variable section present |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-08-W001 | File manifest exceeds 20 files | WARNING | Consider splitting into multiple IPLANS |
| GATE-08-W002 | Missing implementation contract for shared interface | WARNING | Define contract for multi-session work |
| GATE-08-W003 | No rollback procedure defined | WARNING | Add revert steps for failed implementation |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **C1** | Self (author) | Immediate |
| **C2** | Technical Lead | 1 business day |
| **C3** | Technical Lead + Domain Expert | 2 business days |

### 4.2 IPLAN Execution Readiness

Before code generation begins, IPLAN must demonstrate:

```
1. File manifest complete with creation order
2. Test files listed before implementation files
3. Bash commands are exact and reproducible
4. Session handoff protocol describes all state
5. Temporary plans isolated to IPLAN/tmp/
6. Each file references its owning SPEC component
```

### 4.3 Escalation Path

```
C1 (Self-approved)
      
       (if execution order change)
C2 (Technical Lead)
      
       (if session handoff protocol change)
C3 (TL + Domain Expert)
```

## 5. Exit Criteria

To pass GATE-08, the change must satisfy:

| Criterion | C1 | C2 | C3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| File manifest complete | Yes | Yes | Yes |
| Test-first order verified | Yes | Yes | Yes |
| Session handoff documented | Yes | Yes | Yes |
| Upstream traceability tags present | Yes | Yes | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-08-E* checks all pass
- [ ] GATE-08-W* checks reviewed
- [ ] File manifest is complete and ordered
- [ ] Test files precede implementation files
- [ ] @spec and @tdd tags present
- [ ] Session handoff protocol documented
- [ ] Approvals obtained per matrix
- [ ] Ready for code generation
```

## 6. Routing Rules

After passing GATE-08:

| Scenario | Next Step |
|----------|-----------|
| Standard flow | Proceed to GATE-CODE for implementation |
| IPLAN-only fix (C1) | Direct to code generation |
| File manifest update | Regenerate affected code files |

### 6.1 Routing Flowchart

```
                    GATE-08 PASSED
                           
              Ready for code generation
                    
                     GATE-CODE
              Implementation + Review
                    
                         
          
     Code        Build Pass   Merge
     
```

### 6.2 Bubble-Up Trigger

When implementation reveals IPLAN issues:

```
Code generation failure
      
      
      
  Where is the gap?
      
      
  Missing file           Wrong order
  → Add to IPLAN         → Reorder IPLAN
  → GATE-08              → GATE-08
  
  Wrong interface         Wrong command
  → Fix SPEC             → Fix IPLAN
  → GATE-06              → GATE-08
```

## 7. Error Catalog

### 7.1 GATE-08 Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-08-E001 | Completeness | File manifest incomplete | Add missing files to manifest |
| GATE-08-E002 | Order | Test files not before implementation files | Reorder manifest: tests first |
| GATE-08-E003 | Traceability | Missing @spec/@tdd tags | Add upstream traceability tags |
| GATE-08-E004 | Handoff | Session handoff protocol missing | Document state variables and resume protocol |
| GATE-08-W001 | Size | File manifest too large | Split into multiple IPLANS per sub-component |
| GATE-08-W002 | Contracts | Shared interface without contract | Define implementation contract |
| GATE-08-W003 | Rollback | No rollback procedure | Add revert steps |

### 7.2 Common Resolutions

```markdown
## GATE-08-E001 Resolution
Complete the file manifest with all required files:

| Order | File | Type | Purpose |
|-------|------|------|---------|
| 1 | test_component.py | Test | Unit tests for Component |
| 2 | component.py | Impl | Component implementation |
| 3 | __init__.py | Module | Package init |

## GATE-08-E002 Resolution
Ensure test-first ordering:

1. Test files must appear before implementation files
2. Test stubs should be created first
3. Implementation files fill in the stubs

## GATE-08-E003 Resolution
Add the necessary upstream traceability tags. IPLAN requires only @spec + @tdd
(per LAYER_REGISTRY.yaml required_tags); BRD/PRD/EARS/BDD/ADR are reached
transitively through the chain, not cited locally:

@spec: SPEC-XX (Component Definition)
@tdd: TDD-XX (Test Cases)
```

---

**Related Documents**:
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../templates/GATE_APPROVAL_FORM.md](../templates/GATE_APPROVAL_FORM.md)
- [../../../layers/08_IPLAN/](../../../layers/08_IPLAN/)
