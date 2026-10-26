---
name: sdd-module
description: >-
  Decompose Seed into Modules (Tier 2): Triple-Lens subsystems (C4-L2, DFD-L2, sequence choreography) in standard layout, with lifecycle entries that satisfy CHG-L014/L015.
---

# SDD Module Author

> Framework skill — routes to
> `framework/governance/SEED_TO_MODULE_DECOMPOSITION.md` (Triple-Lens
> standard) and `framework/governance/MODULE_LAYOUT.md` (directory
> structure + rules).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: the seed (`sdd-seed`) must stand — modules decompose it, never
> invent beyond it.

## 1. Model through all three lenses

Every module in `docs/modules/MODULE-NN_*` is an architectural subsystem
(a C4-L2 container): deployable services, datastores, and dependencies
mapped to approved archetypes. Lens two traces DFD-L2 data movement —
trust boundaries and sensitivity (PII/secrets). Lens three choreographs the
sequence/process flow. A module missing a lens is a sketch, not a module.

## 2. Use the standard layout

Register in `MODULE-00_index.md`. Directory form for multi-file modules
(`README.md` overview, `architecture.svg`, `decisions.md` with seed
references, `constraints.md` invariants); flat single-file form otherwise.
Decisions cite the seed claims they resolve — untraced design is the exact
drift the seed contract exists to catch.

## 3. Cover the lifecycle

Module touches on a lifecycle-carrying CHG need a `module_lifecycle` entry
(archive → sync → version, affected modules only), each carrying
`author` + `chg_ref` — CHG-L014/L015 are errors, not advice. Next:
`sdd-brd` per module, then the SDD cascade.
