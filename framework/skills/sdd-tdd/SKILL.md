---
name: sdd-tdd
description: >-
  Author TDD cases (Layer 07): test definitions with assertions and verification criteria that the EVAL layer executes — no unasserted behavior ships.
---

# SDD TDD Author

> Framework skill — routes to `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
> and `TDD_WORKFLOW_STANDARD.md` (entry gate GATE-06).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: `sdd-spec` interfaces are the test surface.

## 1. Assert the contract, arrange the fixtures

Each test case names its target (component + interface), arranges fixtures
explicitly, asserts observable behavior, and states verification criteria.
A case without an assertion is a note, not a test — promote it or delete it.

## 2. Cover the SPEC, exactly

Every SPEC interface gets cases; every case traces to one interface. Like
BDD: uncovered surface is risk, double-covered surface is a future
contradiction. New sections stay inside existing mappings (`test_strategy`)
so the deterministic layer fixtures keep passing.

## 3. Seal and hand off

Gate: GATE-06. Cases here are what `sdd-eval` executes — write them so
that a FAIL verdict names the broken contract, not the test. Next:
`sdd-iplan` (then code, then `sdd-eval`).
