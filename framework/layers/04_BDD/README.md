# Behavior-Driven Development (BDD) — Layer 4

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.94.0 |


## Overview

BDD defines executable acceptance scenarios as structured Given-When-Then YAML,
translating EARS formal requirements into testable behaviors with spec_trace links to
SPEC sections for req-to-implementation traceability.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified

## Behavioral Graphs & Structured YAML vs Legacy Gherkin

The framework uses **executable behavioral state graphs** ([CNCF Serverless Workflow v0.8 YAML](./BDD_WORKFLOW_STANDARD.md)) and **structured YAML scenarios**, not legacy Gherkin `.feature` narrative files or conversational examples.
This is a deliberate architectural choice:

- **Executable state graphs**: Complex asynchronous interactions, multi-step flows, and rollback sagas are represented as formal state machine graphs (`states: [inject, operation, switch, callback]`), which autonomous AI agents and execution engines execute deterministically.
- **Element-level traceability**: YAML scenarios and workflow graphs carry per-scenario EARS element-level traceability (the `ears:` list on each scenario or state), which legacy Gherkin comments cannot encode formally.
- **Content-hash ID integration**: Behavioral graphs and YAML scenarios integrate natively with the framework's element-ID and `@`-tag system (content-hash IDs `BDD.NN.SS.xxxx`, upstream/downstream cross-references).
- **Machine-parsable schemas**: Structured YAML and CNCF workflow graphs are directly machine-parsable by the `sdd_doc_lint` validator, `swf_lint`, and downstream TDD mapping (Layer 07), avoiding brittle regex-based `.feature` parsing.
- **Visual diagrams over text examples**: For human-readable reviews, behavioral paths are visualized using standard Mermaid diagrams (`@diagram: state-*` or `@diagram: flow-*`) rather than Gherkin narrative text. The authoritative per-layer value is `extensions` in [`../../registry/LAYER_REGISTRY.yaml`](../../registry/LAYER_REGISTRY.yaml) (GD-17).


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
| `BDD-SWF-TEMPLATE.yaml` | **Workflow subtype** — Hybrid Envelope housing a CNCF Serverless Workflow (v0.8) state machine for complex, stateful user journeys and saga rollback. |
| `BDD_WORKFLOW_STANDARD.md` | Normative standard specifying Given/When/Then mapping to CNCF Serverless Workflow state primitives. |
| `BDD-00_index.TEMPLATE.yaml` | BDD registry template — tracks planned and active BDD documents and scenario suites per project in canonical 5-Quadrant YAML |

## Scenario Formats: Standard vs. Stateful Workflow

The framework provides two complementary approaches to BDD authoring:

1. **Standard Atomic Scenarios (`BDD-TEMPLATE.yaml`)**:
   Designed for single-turn, atomic Given-When-Then checks.
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

2. **Stateful Behavioral Workflows (`BDD-SWF-TEMPLATE.yaml`)**:
   Designed for multi-step user journeys, distributed transactions, asynchronous callbacks, and failure compensation. Utilizes the **Hybrid Envelope Architecture**: the outer envelope preserves SDD metadata and traceability, while an embedded `workflow:` block houses a valid CNCF Serverless Workflow v0.8 state machine (`subtype: workflow`). See [`BDD_WORKFLOW_STANDARD.md`](BDD_WORKFLOW_STANDARD.md) and [`framework/governance/workflows/bdd-acceptance-run.sw.yaml`](../../governance/workflows/bdd-acceptance-run.sw.yaml).

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

TDD (L7) maps each BDD scenario to a concrete test case via its §3 mapping table or §4 test case metadata.
Every BDD scenario MUST be accounted for in TDD (`ACC01`).
