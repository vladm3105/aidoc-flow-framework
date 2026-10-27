---
name: sdd-ears
description: >-
  Author EARS requirements (Layer 03): convert PRD features into formal WHEN-THE-SHALL statements that are atomic, testable, and syntactically invariant.
---

# SDD EARS Author

> Framework skill — routes to `framework/layers/03_EARS/EARS-TEMPLATE.yaml`
> and `EARS_WORKFLOW_STANDARD.md` (entry gate GATE-03).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: `sdd-prd` features are the input; no PRD, no EARS.

## 1. Enforce the syntactic invariant

Every statement requires a trigger clause (WHEN | IF | WHILE) and an actor
clause (THE SYSTEM SHALL), in WHEN-THE-SHALL-WITHIN form. A requirement that
cannot be cast into this shape is not a requirement yet — push it back to
the PRD for clarification instead of weakening the syntax.

## 2. Keep statements atomic and testable

One behavior per statement, one verifiable outcome. Compound statements
split; untestable adjectives get thresholds or leave. Each statement traces
to its PRD feature; each PRD acceptance criterion is covered by at least
one statement.

## 3. Seal and hand off

Gate: GATE-03. Fast-path flows (HOTFIX, CODE2C, DIR2C) may not touch this
layer without an SDD lifecycle step (CHG-L019). Next: `sdd-bdd`.
