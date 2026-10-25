---
name: sdd-adr
description: >-
  Author ADRs (Layer 05): record architecture decisions with options, trade-offs, and a Selected reason — status Proposed until accepted, never silent.
---

# SDD ADR Author

> Framework skill — routes to `framework/layers/05_ADR/ADR-TEMPLATE.yaml`
> and `ADR_WORKFLOW_STANDARD.md` (entry gate GATE-03).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: BDD scenarios bound the behavior the architecture must support.

## 1. Decide on paper, with losers named

Each ADR names the decision, the options considered with trade-offs, and
the selection with a one-line reason. An ADR with one option is a rubber
stamp — find the real alternative or say why none exists. Status starts at
`Proposed`; only acceptance moves it to `Accepted` (later: `Deprecated`
or `Superseded`, never edited into a different past).

## 2. Keep the deterministic gates honest

`spec_ready_status` stays a binary topological verdict (PASS), not a score.
Scores rot into arguments about thresholds; PASS/FAIL rot into nothing.

## 3. Seal and hand off

Gate: GATE-03. Fast-path restriction applies (CHG-L019). Next: `sdd-spec`.
