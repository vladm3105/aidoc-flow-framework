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

- Full-depth programs require all CHG gates.
- Lite/Standard may use subset gates by policy.
- Emergency bypass must be documented with reason, approver, and follow-up action.

## References

- `ai_dev_flow_v3/CHG/CHG-TEMPLATE.yaml`
- `ai_dev_flow_v3/CHG/gates/`
