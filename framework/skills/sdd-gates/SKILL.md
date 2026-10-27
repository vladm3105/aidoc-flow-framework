---
name: sdd-gates
description: >-
  Run the CHG gate battery (GATE-01 through GATE-CODE) for the touched layers, dispose every finding via the error catalog, and never merge while red.
---

# SDD Gate Runner

> Framework skill — routes to `framework/layers/09_CHG/gates/` (GATE-01,
> GATE-03, GATE-06, GATE-08, GATE-CODE, GATE-SPEC), `GATE_ERROR_CATALOG.md`,
> and `GATE_INTERACTION_DIAGRAM.md`.
> Paths below use `<skills-root>` = this `framework/skills/` directory.

## 1. Select gates by touch

Run the gates for the layers the change touches, not the whole battery by
default: GATE-01 for business/product surface, GATE-03 for requirements and
architecture, GATE-06 for design and test, GATE-08 for the IPLAN itself,
GATE-CODE for any code or implementation artifact, GATE-SPEC for normative
`framework/` edits. A skill-only change still runs the structural and
conformance gates on its PR — "docs-only" is a scope statement, not a
verification waiver.

## 2. Dispose every finding

Every finding resolves through `GATE_ERROR_CATALOG.md`: fix the cause in
the worktree and re-run to green. Additive findings (index rows, registry
entries, pins) resolve directly; semantic findings (logic, policy,
contradicted contracts) mean stop and escalate — never route around a red
gate with a skip flag or an admin override.

## 3. Merge only on green

When a required check fails, fix every error from the failed logs, push,
and re-watch from the new head — a previous run's green is not this
commit's. Stop and report to the human when the same check fails twice
after a fix attempt, or when the fix reaches beyond the PR's scope.
