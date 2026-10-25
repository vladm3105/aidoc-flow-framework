---
name: sdd-brd
description: >-
  Author the BRD (Layer 01): business objectives, ROI, and scope that everything downstream traces to — strategy first, features never.
---

# SDD BRD Author

> Framework skill — routes to `framework/layers/01_BRD/BRD-TEMPLATE.yaml`
> and `BRD_WORKFLOW_STANDARD.md` (entry gate GATE-01).
> Paths below use `<skills-root>` = this `framework/skills/` directory.

## 1. When this layer runs

New product or initiative with no prior implementation (SDD2C), or a
SEED2C change that re-opens business scope. Never for a DIR2C request —
a BRD appearing in a docs/tooling change is a CHG-L019-class scope error.

## 2. Author from objectives, not features

Build `business_objectives`, `stakeholders`, and `project_scope` first;
personas stay high-level `target_users` here (detailed personas belong to
`sdd-prd`). Run the ROI feasibility evaluation the workflow standard
requires — quantitative cost-benefit gates, not narrative justification.

## 3. Seal the chain of custody

Every downstream layer traces here: PRD features decompose objectives,
EARS formalizes them, EVAL verifies them. Leave no objective without an
owner and no scope line without a boundary. Gate: GATE-01. Next: `sdd-prd`.
