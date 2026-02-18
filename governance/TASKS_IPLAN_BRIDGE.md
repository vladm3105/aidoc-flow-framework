# TASKS to IPLAN Bridge

## Overview

This document bridges SDD Layer 11 (TASKS) artifacts with governance IPLAN documents, clarifying when and how each is used.

---

## Artifact Comparison

| Aspect | TASKS (SDD Layer 11) | IPLAN (Governance) |
|--------|---------------------|-------------------|
| **Created** | During SDD specification | Before implementing each issue |
| **Format** | YAML with traceability | Markdown with checklist |
| **Scope** | Full feature breakdown | Single issue execution |
| **Purpose** | Work decomposition from SPEC | Execution plan with corrections |
| **Contains** | Tasks, dependencies, acceptance criteria | Steps, risks, findings |

---

## Workflow Integration

### When Using SDD + Governance

```
SPEC-NN (Layer 9)
    |
TASKS-NN generated (Layer 11)
    |
tasks_to_github.py creates issues
    |
Issue #X created with source:sdd label
    |
AI agent picks up issue (ai:ready)
    |
Agent creates IPLAN-X_{slug}.md BEFORE coding
    |
Implementation proceeds per IPLAN
    |
PR created, IPLAN marked complete
```

### Traceability Chain

```
BRD -> PRD -> EARS -> ADR -> SYS -> REQ -> SPEC -> TASKS -> Issue -> IPLAN -> Code
```

Each IPLAN includes:
- `@tasks: TASKS-NN.MM.PP` reference (links to source task)
- Full upstream traceability (inherited from TASKS)
- Issue-specific execution details

---

## When to Use Which

| Scenario | Use TASKS | Use IPLAN |
|----------|-----------|-----------|
| SDD-generated feature | Yes - Generated from SPEC | Yes - Created per issue |
| Manual issue (no SDD) | No - Not applicable | Yes - Required before coding |
| Bug fix | No - Not applicable | Yes - Required (simplified) |
| Hotfix | No - Not applicable | No - Code-only, 72h retroactive docs |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.md` | TASKS format specification |
| `ai_dev_ssd_flow/11_TASKS/IMPLEMENTATION_PLAN_TEMPLATE.md` | SDD implementation tracking |
| `governance/plans/IPLAN-TEMPLATE.md` | Governance IPLAN format |
| `governance/GOVERNANCE_RULES.md` Section 3 | Issue processing workflow |

---

## Implementation Plan Templates Clarification

Multiple implementation plan templates exist for different purposes:

| Template | Location | Purpose |
|----------|----------|---------|
| **IPLAN-TEMPLATE.md** | `governance/plans/` | Per-issue execution plan (governance) |
| **IMPLEMENTATION_PLAN_TEMPLATE.md** | `ai_dev_ssd_flow/11_TASKS/` | TASKS execution tracking (SDD) |
| **IMPLEMENTATION_PLAN_TEMPLATE.yaml** | `ai_dev_ssd_flow/11_TASKS/` | Machine-readable version |

**Key Difference**:
- **IPLAN**: Governance artifact, created per GitHub issue, focuses on execution steps and corrections
- **IMPLEMENTATION_PLAN**: SDD artifact, tracks overall TASKS completion across multiple issues
