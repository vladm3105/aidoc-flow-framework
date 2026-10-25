---
name: sdd-prd
description: >-
  Author the PRD (Layer 02): expand BRD segments into actionable personas and feature scopes with acceptance criteria the EARS layer can formalize.
---

# SDD PRD Author

> Framework skill — routes to `framework/layers/02_PRD/PRD-TEMPLATE.yaml`
> and `PRD_WORKFLOW_STANDARD.md` (entry gate GATE-01).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: `sdd-brd` must stand — a PRD without a BRD has no objectives to satisfy.

## 1. Expand, don't invent

Translate each BRD objective into features; translate each `target_users`
segment into a `primary_persona` with characteristics, pain points, and
success criteria. A feature with no parent objective is scope creep — cut
it or send it back to the BRD.

## 2. Write acceptance criteria EARS can consume

Each feature scope closes with acceptance criteria precise enough to become
WHEN-THE-SHALL statements downstream. Vague criteria ("fast", "intuitive",
"robust") fail here, not in EARS — quantify now.

## 3. Seal and hand off

Trace every feature to its BRD objective (`decomposes_to` / `satisfies`
edges in the layer graph). Gate: GATE-01. Next: `sdd-ears`.
