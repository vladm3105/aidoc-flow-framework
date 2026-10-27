---
name: sdd-bdd
description: >-
  Author BDD scenarios (Layer 04): translate EARS requirements into executable Given-When-Then scenarios mapped to state-machine primitives.
---

# SDD BDD Author

> Framework skill — routes to `framework/layers/04_BDD/BDD-TEMPLATE.yaml`
> and `BDD_WORKFLOW_STANDARD.md` (entry gate GATE-03).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: `sdd-ears` statements are the input.

## 1. Scenarios, not scripts

Write standard linear Given/When/Then scenarios for atomic or monolithic
features; reach for feature files only where the template's criteria call
for them. Map each step to state-machine primitives
(inject/operation/event/switch) so scenarios execute instead of merely
reading well.

## 2. Cover the requirements, exactly

Every EARS statement gets at least one scenario; every scenario traces to
exactly one EARS statement. A scenario covering nothing is theater; a
requirement covered twice is a future contradiction — reconcile, don't
duplicate.

## 3. Seal and hand off

Gate: GATE-03. Same fast-path restriction as EARS (CHG-L019). Next: `sdd-adr`.
