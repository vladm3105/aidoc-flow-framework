# framework/ — Shared Engine-Agnostic Specification

The **engine-agnostic specification** of the document-flow framework: the
single contract that every platform implements. It contains **no runtime
code** — only the layer definitions, registry, governance rules, templates,
and review playbooks that platforms consume.

## What it specifies

Specification-Driven Development (SDD) is an **8-layer documentation-to-code
flow** that produces implementation-ready technical specifications from
business requirements. Each layer is a single document type with cumulative
traceability:

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
```

| Layer | Artifact | Purpose |
|-------|----------|---------|
| 1 | BRD | Business requirements and objectives |
| 2 | PRD | Product features and user stories |
| 3 | EARS | Formal requirements (WHEN-THE-SHALL-WITHIN) |
| 4 | BDD | Acceptance scenarios (Given-When-Then) |
| 5 | ADR | Architecture decisions (Context-Decision-Consequences) |
| 6 | SPEC | Technical specification — interfaces, data models, contracts |
| 7 | TDD | Test case definitions and quality thresholds |
| 8 | IPLAN | Implementation plan — file manifest, execution bridge |

Each layer N may reference only the layers before it; `downstream` and
`required_tags` in the registry encode the full traceability graph.

## C4 alignment

The layers align with the C4 architecture model at four zoom levels, with two
bridge groups connecting them:

| C4 level | Layers | Artifacts |
|----------|--------|-----------|
| L1 Context | 1 | BRD |
| L2 Container | 2 | PRD |
| Decision bridge | 3–5 | EARS, BDD, ADR |
| L3 Component | 6 | SPEC |
| Implementation bridge | 7–8 | TDD, IPLAN |
| L4 Code | — | Source code |

Bridge groups are SDD-specific refinements that translate and validate the
transitions between C4 levels; they have no C4 zoom level of their own.

## Layout

```
framework/
  README.md              This file.
  VERSION                Framework spec version (SemVer).
  SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  End-to-end SDD authoring guide (the one
                         root doc platforms vendor alongside the spec subtrees).
  QUICK_REFERENCE.md     Condensed layer / tag / ID cheat-sheet.
  TESTING_STRATEGY_TDD.md  Test-strategy guidance feeding the TDD layer.
  AI_ASSISTANT_RULES.md  Authoring rules for AI agents that consume the spec.
  layers/                The 8 layer definitions — one folder per layer, each
                         with a template, a README, and an index template
                         (08_IPLAN also carries PLAN_STANDARD.md).
  playbooks/             Per-layer review playbooks — the lens-by-lens audit
                         checklists the review-team crews apply, one folder per
                         layer. A vendored artifact class.
  registry/
    LAYER_REGISTRY.yaml   Authoritative machine-readable layer model: order,
                          traceability graph, C4 mapping, ID patterns.
    README.md
  governance/            Governance rules; the CHG change-management overlay
                         (gates incl. GATE-SPEC, the framework-spec change gate;
                         templates); the project adaptation surface
                         (ADAPTATION.md + ADAPTATION_SURFACE.yaml); and
                         DECISIONS.md, the spec-level decision register.
                         See governance/README.md.
  docs/
    AIDOC.md              Canonical reference for the .aidoc/ provenance tier.
```

## Conformance

The contract is enforced by the shared conformance suite in
[`../tests/conformance/`](../tests/conformance/). It verifies that this spec is
internally consistent — the registry agrees with itself and with the files on
disk, templates match the registry, and no engine-specific content has leaked
in — and defines the contract that platform implementations are tested against.

Run it from the repository root:

```sh
python3 -m unittest discover -s tests/conformance -v
```

## How platforms consume it

Each platform is an **independent engine** that implements this specification;
the platforms share `framework/` and nothing else. A platform declares the
`framework/VERSION` it conforms to, generates artifacts that validate against
the layer templates and the registry's ID patterns, and enforces the
traceability rules the registry encodes. See [`../README.md`](../README.md) for
the platforms and the overall project layout.

## Versioning

`framework/VERSION` carries the spec version as SemVer. A breaking change to a
layer schema, the registry model, or a governance rule is a major bump;
backward-compatible additions are minor; clarifications are patch. Platforms
pin the spec version they implement.

## Project layout — four tiers

Every project that uses the framework structures its outputs into four
explicit tiers:

| Tier | Where | Committed? |
|---|---|:---:|
| Inputs | `<project>/seed/`, `<project>/chg/` | ✅ |
| AI outputs (chain) | `<project>/docs/` | ✅ |
| AI provenance | `<project>/.aidoc/` — audit, review, remediation, validation, security, quality reports | ✅ |
| Tool internals | `<project>/logs/<TS>/` — execution metadata, raw stdout | ❌ |

`.aidoc/` answers *"how did the AI arrive at the output?"* without
requiring a re-run. See [`docs/AIDOC.md`](docs/AIDOC.md) for the
canonical reference. The pre-deployment acceptance-test methodology
that populates these tiers lives at
[`../tests/ACCEPTANCE.md`](../tests/ACCEPTANCE.md) (test-suite
documentation; outside the engine-agnostic spec).
