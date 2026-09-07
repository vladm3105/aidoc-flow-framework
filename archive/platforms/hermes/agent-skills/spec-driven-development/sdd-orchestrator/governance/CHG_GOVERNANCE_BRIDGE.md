# CHG to Governance Bridge (v3)

## Overview

Maps v3 CHG gate overlay to governance execution phases.

## CHG Gate Mapping

| Gate | Scope | Governance Equivalent |
|---|---|---|
| GATE-01 | Business/Product intent | Intake validation |
| GATE-03 | Requirements/Architecture | Design approval |
| GATE-06 | Specification/Test design | Pre-execution quality gate |
| GATE-08 | Execution plan (IPLAN) | Implementation readiness |
| GATE-CODE | Code/release decision | Merge/deploy authorization |

## Integration Rules

- CHG is an orthogonal governance overlay on changes; its gates apply to every change that
  crosses a gate boundary (there are no depth tiers to key a subset off).
- Emergency bypass must be documented with reason, approver, and follow-up action.

## References

- `framework/governance/chg/CHG-TEMPLATE.yaml`
- `framework/governance/chg/gates/`
