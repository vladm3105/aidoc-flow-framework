# CHG to Governance Phase Bridge

## Overview

This document bridges SDD's 4-Gate Change Management (CHG) system with governance phase-gated deployment.

---

## When to Use CHG

| SDD Depth | Change Management Method |
|-----------|-------------------------|
| **SDD-Lite** | PR-based only |
| **SDD-Standard** | PR-based + review gates |
| **SDD-Full** | 4-Gate CHG system (formal) |

CHG documents are **required** for SDD-Full projects and **optional** for others.

---

## Gate-to-Phase Mapping

| SDD Gate | Layers Affected | Governance Equivalent | Approval Required |
|----------|-----------------|----------------------|-------------------|
| GATE-01 | L1-L4 (BRD->BDD) | Phase requirement review | Business Owner |
| GATE-05 | L5-L8 (ADR->CTR) | Architecture review | Architect |
| GATE-09 | L9-L11 (SPEC->TASKS) | Sprint planning approval | Tech Lead |
| GATE-12 | L12-L14 (IMPL->Validation) | PR merge + phase deployment | Reviewer |

---

## Integration Points

### CHG Document Triggers Governance Actions

| CHG Status | Governance Action |
|------------|-------------------|
| CHG created | Issue labeled `chg:pending` |
| CHG approved | Label changed to `chg:approved`, proceed with implementation |
| CHG rejected | Label changed to `chg:rejected`, rework required |
| GATE-12 passed | `deploy-dev.yml` triggered on phase completion |

### Governance Events Trigger CHG Updates

| Governance Event | CHG Impact |
|------------------|------------|
| Sprint retrospective | Review open CHGs, close completed |
| Phase deployment | Update CHG status to reflect deployment |
| Production incident | May trigger emergency CHG bypass |

---

## Emergency Bypass Conditions

CHG gates can be bypassed for:
- P1 production incidents
- Critical security vulnerabilities (CVSS >= 9.0)
- Regulatory compliance deadlines

Document bypass in CHG with:
- `bypass_reason: <description>`
- `bypass_approver: <name>`
- `bypass_date: <YYYY-MM-DD>`

---

## CHG Labels

| Label | Color | Description |
|-------|-------|-------------|
| `chg:pending` | Yellow (#F9A825) | CHG document awaiting approval |
| `chg:approved` | Green (#43A047) | CHG document approved |
| `chg:rejected` | Red (#D32F2F) | CHG document rejected |

---

## CHG Workflow Diagram

```
BRD/PRD Changes Proposed
        |
        v
+------------------+
|   CHG Created    |
|  Label: pending  |
+------------------+
        |
        v
+------------------+
|  GATE-01 Review  |  (Business Owner)
|    L1-L4 scope   |
+------------------+
        |
   +---------+
   |  Pass?  |
   +---------+
   Yes |    | No
       v    v
  Proceed  Rework
       |
       v
+------------------+
|  GATE-05 Review  |  (Architect)
|    L5-L8 scope   |
+------------------+
        |
       ...
        |
        v
+------------------+
|  GATE-12 Review  |  (Reviewer)
|    L12-L14 impl  |
+------------------+
        |
        v
+------------------+
|   CHG Approved   |
| Label: approved  |
+------------------+
        |
        v
  deploy-dev.yml
```

---

## Reference Documents

| Document | Location |
|----------|----------|
| CHG Template | `ai_dev_ssd_flow/CHG/CHG-TEMPLATE.yaml` |
| Change Management Guide | `ai_dev_ssd_flow/CHG/CHG-00_index.md` |
| 4-Gate Definitions | `ai_dev_ssd_flow/CHG/gates/` |
