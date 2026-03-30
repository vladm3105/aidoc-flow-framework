# Change Management (CHG) — Governance Overlay

## Overview

CHG is a **governance overlay** for managing changes to existing SDD artifacts.
It is NOT a lifecycle layer — it triggers on-demand when modifying any artifact
across the 11-layer SDD workflow.

## Change Levels

| Level | Scope | Gate | Process |
|-------|-------|------|---------|
| L1 | Typo, formatting | None | Fix → commit |
| L2 | Section update | Peer review | Assess → update → verify |
| L3 | Cross-layer change | Formal gate | Full CHG process |
| Emergency | Critical production | Post-hoc + post-mortem | Fix → deploy → document within 48h |

## Change Source Routing

| Source | Entry Gate | Direction |
|--------|-----------|-----------|
| Upstream | GATE-01 | BRD/PRD change cascading down |
| Midstream | GATE-05 | ADR/SYS change affecting neighbors |
| Downstream | GATE-09 | SPEC/TASKS change propagating up |
| External | GATE-01 | Regulatory, vendor, market |
| Feedback | GATE-12 | Production feedback, user issues |

## Files

| File/Dir | Purpose |
|----------|---------|
| `CHG-TEMPLATE.yaml` | Single template — all change levels |
| `CHG-00_index.md` | Change registry |
| `gates/` | Gate definitions (GATE-01, 05, 09, 12 + error catalog + diagram) |
| `templates/GATE_APPROVAL_FORM.md` | Companion — gate approval documentation |
| `templates/POST_MORTEM-TEMPLATE.md` | Companion — emergency post-mortem |

## NOT a Lifecycle Layer

CHG is NOT:
- Part of the BRD→TASKS workflow
- In `mcp_sdd/templates/`
- Assigned a C4 level
- Part of the readiness score chain

CHG uses gate approval instead of readiness scores.

## Archive

`CHG_v1_archive/` contains deprecated templates, source guides, workflows, and scripts.
