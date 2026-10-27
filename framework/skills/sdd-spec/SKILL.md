---
name: sdd-spec
description: >-
  Author the SPEC (Layer 06): component interfaces, wire contracts, and data schemas with the toolchain pinned in the document's own language field.
---

# SDD SPEC Author

> Framework skill — routes to `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
> and `SPEC_WORKFLOW_STANDARD.md` (entry gate GATE-06).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream: `sdd-adr` decisions constrain the components; the SPEC does not
> re-litigate them.

## 1. Contracts, not descriptions

Define `component_overview` with interfaces, wire contracts, and data
schemas per component. SPEC owns the toolchain: pin it in the document's
own `language:` field so generators and linters read one source of truth.

## 2. Stay inside the ADDs

Every component traces to its authorizing ADR and the BDD scenarios it
implements. New top-level sections stay inside existing mappings (e.g.
`component_overview`) so deterministic acceptance fixtures keep passing —
a section that breaks the fixture is a section in the wrong place.

## 3. Seal and hand off

Gate: GATE-06. Fast-path restriction applies (CHG-L019). Next: `sdd-tdd`.
