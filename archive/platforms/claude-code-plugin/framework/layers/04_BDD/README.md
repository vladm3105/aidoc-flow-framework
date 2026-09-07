# Behavior-Driven Development (BDD) — Layer 4

## Overview

BDD defines executable acceptance scenarios as structured Given-When-Then YAML,
translating EARS formal requirements into testable behaviors with spec_trace links to
SPEC sections for req-to-implementation traceability.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

## YAML vs Gherkin

The framework uses **YAML-structured scenarios**, not Gherkin `.feature` files.
This is a deliberate design choice:

- YAML scenarios carry per-scenario EARS element-level traceability (the `ears:`
  list on each scenario), which Gherkin comments cannot encode formally.
- YAML scenarios integrate with the framework's element-ID and `@`-tag system
  (content-hash IDs, upstream/downstream cross-references).
- YAML is directly machine-parsable by both the `sdd_doc_lint` validator and the
  TDD mapping step (layer 7), avoiding brittle regex-based `.feature` parsing.
- Gherkin is still supported as an **output format** for human-readable
  summaries, but the authoritative representation is YAML. The authoritative
  per-layer value is `extensions` in
  [`../../registry/LAYER_REGISTRY.yaml`](../../registry/LAYER_REGISTRY.yaml) — the
  single normative source (GD-17). This states the value; it does not re-specify it.


**Execution**: QA STAGING ONLY — do NOT run in CI pipeline. Use TDD (L7) unit/integration tests for CI.

**Acceptance pairing (normative — GD-08).** Because BDD scenarios are not
executed here, "executable acceptance scenario" is only true once TDD (L7) pairs
each scenario to a concrete test case. Every scenario declared in this layer MUST
be named by a TDD **test case or §3 mapping entry**; a scenario that reaches only
the TDD §7 traceability block is not paired. `ACC01`
(`../../governance/LINT_RULES.md`; `../../governance/SEED_CONTRACT.md`) enforces
this — `warning` in `build`, `error` in `gate-code` — and is stricter than
`COV02`, which a SPEC-only citation already satisfies.

## C4 Model Position

BDD is a **refinement step** alongside EARS that formalizes the transition from
Context (BRD) to Container (PRD). BDD translates EARS requirements into executable
Given-When-Then scenarios, which TDD (L7) maps to concrete test cases.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition              ← this layer
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions from SPEC + BDD scenarios
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files

| File | Purpose |
|------|---------|
| `BDD-TEMPLATE.yaml` | **Default** — full template with embedded `scenarios:` YAML guidance in `_example` fields. Self-documenting for AI agents. |
| `BDD-MVP-TEMPLATE.yaml` | Skeleton — stripped-down structural form. Not standalone. See [BRD README](../01_BRD/README.md) for the template selection rule. |
| `BDD-00_index.TEMPLATE.md` | BDD registry template — tracks planned and active BDD documents per project |

## Scenario YAML Quick Reference

BDD scenarios are authored as **structured YAML** (a `scenarios:` list), not
Gherkin `@`-tags. `id`/`type`/`priority` are fields; the upstream trace is an
element-level `ears:` list; `given`/`when`/`then` are phase lists.

```yaml
scenarios:
  - id: BDD.01.03.xxxx
    name: User logs in with valid credentials
    type: success
    priority: p0-critical
    ears: [EARS.01.03.xxxx]
    given: ["a registered user with valid credentials"]
    when: ["the user submits a login request"]
    then:
      - "the system authenticates the user"
      - "a session token is returned WITHIN @threshold:PRD.01.perf.auth.p95"
    spec_trace: ["SPEC Section 5 (Behavior)"]
```

## Element IDs

Hash-based, content-derived IDs scoped to BDD content:
> The SHA-256 form is the **canonicalization target**: engines emit stable opaque strings that *should* match it. `rehash --check` verification is shipped for BRD §7 only (PROVISIONAL-IDS-002 Phase 1); extraction for this layer is Phase 2+. See `ID_NAMING_STANDARDS.md`.

```text
Format: BDD.{doc_id}.{section_id}.{hash}
Example: BDD.01.03.d7a2
```

## Upstream Traceability

BDD is the **exception** to the `@`-tag convention (see `TAG_SYNTAX.md`): a BDD
document carries its required upstream trace to **EARS (Layer 3)** as a
structured, element-level `ears:` list **per scenario** — not as an `@ears`
tag. PRD/BRD lineage is reached transitively through the EARS document's own
`@`-tag chain; a BDD document emits no `@ears`/`@prd`/`@brd` tags of its own.

```yaml
scenarios:
  - id: BDD.01.03.xxxx
    ears: [EARS.01.03.xxxx]   # element-level; one space after the colon in any @-tag elsewhere
```

## Downstream Traceability

Each BDD scenario includes a `spec_trace` field linking to SPEC sections:

```text
spec_trace:
  - "SPEC Section 3 (Interfaces)"
  - "SPEC Section 5 (Behavior)"
```
