# framework/ — Shared Engine-Agnostic Specification

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.53.0 |


The **engine-agnostic specification** of the document-flow framework: the
single contract that every platform implements. It contains **no runtime
code** — only the layer definitions, registry, governance rules, templates,
and review playbooks that platforms consume.

## What it specifies

Specification-Driven Development (SDD) is a **10-layer documentation-to-code
flow** that produces implementation-ready technical specifications from
business requirements. Each layer is a single document type with end-to-end
traceability:

```
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
                                                        ↑
                                          CHG (L9, overlay) → EVAL (L10)
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
| 9 | CHG | Change management overlay — gates, versioning, audit trail |
| 10 | EVAL | Evaluation & QA governance — test strategy, coverage matrices |

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
  CHANGELOG.md           Version history — document-of-record for spec changes (E008).
  SPEC_DRIVEN_DEVELOPMENT_GUIDE.md  End-to-end SDD authoring guide (the one
                         root doc platforms vendor alongside the spec subtrees).
  QUICK_REFERENCE.md     Condensed layer / tag / ID cheat-sheet.
  TESTING_STRATEGY_TDD.md  Test-strategy guidance feeding the TDD layer.
  AI_ASSISTANT_RULES.md  Authoring rules for AI agents that consume the spec.
  layers/                The 10 layer definitions — one folder per layer, each
                         with a template, a README, and an index template
                         (08_IPLAN also carries PLAN_STANDARD.md and
                         IPLAN-ECOSYSTEM.md).
  playbooks/             Per-layer review playbooks — the lens-by-lens audit
                         checklists the review-team crews apply. 10 folders: one
                         per layer (01_BRD through 09_CHG) plus 10_IPLAN_VERIFY.
                         A vendored artifact class.
  templates/             Doc templates that aren't layer artifacts (e.g.
                         framework-feedback-log.template.md).
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
  archive/               Archived originals from CHG-modified documents.
                         Structure: archive/{CHG-ID}/{category}/.
  governance/aidoc/      .aidoc/ contract: AIDOC.md, scaffold template.
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

## Change Management

All changes to the framework specification — templates, governance rules,
registry, and version — follow the **CHG (Change Record) governance overlay**
defined in [`layers/09_CHG/`](layers/09_CHG/). This is the single entry point
for modifying any framework artifact.

### How it works

```
Any change to framework/  →  Classify (C1/C2/C3/Emergency)
                            →  Route to entry gate (GATE-SPEC for spec changes)
                            →  Assess impact across affected layers
                            →  Archive superseded versions
                            →  Update artifacts
                            →  Verify against gate criteria
                            →  Record in CHG document
```

### Change levels

| Level | Scope | Gate | Process |
|-------|-------|------|---------|
| C1 | Typo, formatting | None | Direct commit |
| **C2** | Section update, new governance rule | Peer review | Full CHG process |
| **C3** | Cross-layer, breaking changes | Formal gate (GATE-SPEC) | Full CHG + both-platform approval |
| Emergency | Critical production fix | Post-hoc + post-mortem within 48h | Fix first, document after |

Framework-spec changes (edits to `framework/` itself) route through
**GATE-SPEC** — the meta gate orthogonal to the artifact cascade. GATE-SPEC
enforces: provenance justification, SemVer classification (≥ C2, never C1),
`framework/VERSION` bump, both-platform `FRAMEWORK_SPEC_VERSION` re-declaration,
conformance suite green, and `CHANGELOG.md` update. See
[`layers/09_CHG/gates/GATE-SPEC_FRAMEWORK.md`](layers/09_CHG/gates/GATE-SPEC_FRAMEWORK.md)
for the full gate definition.

### Document lifecycle tracking

Every framework document carries a **Document Control** block tracking:

| Field | Purpose |
|-------|---------|
| Version | Document version (bumped on each rewrite) |
| Status | Draft / Approved / Deprecated |
| Last Updated | ISO 8601 date of last modification |
| Author | Who last modified the document |
| Framework Version | `framework/VERSION` at time of creation/update |

SDD layer templates use `document_control:` in YAML. Governance docs, gate
definitions, and reference docs use a `## Document Control` Markdown table.
YAML data files carry `last_updated` and `framework_version` in their
`metadata:` block. This convention was introduced in GD-24 (CHG-01, v0.53.0).

### Archive convention

Superseded versions are archived to `archive/CHG-01/` (framework-level) or
`docs/sdd/09-CHG/archive/{CHG-ID}/{layer}/` (project-level). The current
directory always reflects the latest truth — never append, never mix versions.

## Project layout — four tiers

Every project that uses the framework structures its outputs into four
explicit tiers:

| Tier | Where | Committed? |
|---|---|:---:|
| Inputs | `<project>/seed/`, `<project>/chg/` | ✅ |
| AI outputs (chain) | `<project>/docs/` | ✅ |
| Project overrides | `<project>/.aidoc/` — profile, project-specific templates/rules/playbooks | ✅ |
| Tool internals | `<project>/logs/<TS>/` — execution metadata, raw stdout | ❌ |

`.aidoc/` answers *"what is different about this project?"* — the profile
(adaptation knobs) and any project-specific template/rule/playbook
overrides that take precedence over the framework defaults. See
[`governance/aidoc/AIDOC.md`](governance/aidoc/AIDOC.md) for the canonical reference.
