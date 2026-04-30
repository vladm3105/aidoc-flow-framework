# Change Management (CHG) — Governance Overlay (v3.2)

## Overview

CHG is a **governance overlay** for managing changes to existing SDD artifacts.
It is NOT a lifecycle layer — it triggers on-demand when modifying any artifact
across the 8-layer SDD v3.2 workflow.

## Change Levels

| Level | Scope | Gate | Process |
|-------|-------|------|---------|
| C1 | Typo, formatting | None | Fix → commit |
| C2 | Section update | Peer review | Assess → update → verify |
| C3 | Cross-layer change | Formal gate | Full CHG process |
| Emergency | Critical production | Post-hoc + post-mortem | Fix → deploy → document within 48h |

## Change Source Routing

| Source | Entry Gate | Direction |
|--------|-----------|-----------|
| Upstream | GATE-01 | BRD/PRD change cascading down |
| Midstream | GATE-03 | EARS/BDD/ADR change affecting neighbors |
| Design | GATE-06 | SPEC/TDD change |
| Execution | GATE-08 | IPLAN change |
| External | GATE-01 | Regulatory, vendor, market |
| Feedback | GATE-CODE | Production feedback, user issues |

## Cascade Chain

```
BRD(L1) → PRD(L2) → EARS(L3) → BDD(L4) → ADR(L5) → SPEC(L6) → TDD(L7) → IPLAN(L8) → Code
```

## Files

| File/Dir | Purpose |
|----------|---------|
| `CHG-TEMPLATE.yaml` | Single template — all change levels |
| `CHG-00_index.md` | Change registry |
| `gates/` | Gate definitions (GATE-01, 03, 06, 08, CODE + error catalog + diagram) |
| `templates/GATE_APPROVAL_FORM.md` | Companion — gate approval documentation |
| `templates/POST_MORTEM-TEMPLATE.md` | Companion — emergency post-mortem |

## NOT a Lifecycle Layer

CHG is NOT:
- Part of the BRD→IPLAN→Code workflow
- In the YAML template chain
- Assigned a C4 level
- Part of the readiness score chain

CHG uses gate approval instead of readiness scores.
