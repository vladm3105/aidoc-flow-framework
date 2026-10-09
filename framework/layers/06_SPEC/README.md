# 06_SPEC — Technical Specification

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.91.2 |


## C4 Model Position

SPEC is the **C4-L3 (Component)** level in the C4 architecture model. Content describes component interfaces, data models, and behavior contracts — not architecture decisions (ADR) or code implementation (Code).

Required diagram tags: `@diagram: c4-l3`, `@diagram: dfd-l3`.

```text
Context (BRD)    — business environment, actors, boundaries       C4-L1
Container (PRD)  — product features, functional blocks            C4-L2
  └─ EARS/BDD    — formalize Context→Container transition
  └─ ADR         — decision bridge (no C4 level)
Component (SPEC) — interfaces, data models, behavior contracts   C4-L3 ← this layer
  └─ TDD/IPLAN   — implementation bridge (no C4 level)
Code             — source code                                    C4-L4
```

## Purpose

Implementation-ready technical specification for a single software component. Defines interfaces, data models, and behavior contracts before downstream TDD test cases are written.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified

## Design Decisions

- **Unified metadata model** — same structure as all other layers
- **Positioned at L6** — after ADR (architecture decisions) and before TDD (test definitions). Logical flow: decide architecture → specify components → define tests → implement.
- **Dual-template architecture** — `SPEC-TEMPLATE.yaml` (default, standard atomic components) and `SPEC-SWF-TEMPLATE.yaml` (workflow subtype, CNCF Serverless Workflow v0.8 for distributed interaction choreography, asynchronous callbacks, and saga rollback compensation).
- **Test contract references** — links to TDD layer (Layer 7) for test case definitions
- **Unified v1.0 metadata model** — same structure as all other layers

## Specification Baseline

| Area | SPEC Standard |
|--------------------|-------------------|
| Metadata model | `schema_version: 1.0` unified model |
| Traceability | Flat upstream tags |
| Template model | Dual-template (Standard vs Workflow) |
| Upstream | EARS + BDD + ADR |
| Downstream | TDD → IPLAN → Code |
| Document shape | 8 core sections |
| Readiness gate | TDD-Ready score >= 90% (GATE-06) |

## Element IDs

SPEC content **MAY** carry `SPEC.NN.SS.xxxx` element IDs but is not required to
(exemption: `governance/ID_NAMING_STANDARDS.md` §"Element-ID exemptions").
Lineage for §3 Protocol method specifications and §5 fail-closed rules comes
from upstream `@ears` / `@bdd` / `@adr` citations plus the declared method
names — do not over-assign layer-local IDs.

## Upstream Traceability

SPEC cites its necessary upstream (Layer 6 `required_tags`) — `@ears` + `@bdd` + `@adr`:

```text
@ears: EARS.NN.03.xxxx   (formal requirements the component realizes)
@bdd: BDD.NN.03.xxxx     (acceptance scenarios the component must satisfy)
@adr: ADR.NN.03.xxxx     (architecture decisions constraining the design)
```

## Specification Formats: Standard vs. Distributed Choreography Workflow

The framework provides two complementary approaches to SPEC authoring:

1. **Standard In-Process Specifications (`SPEC-TEMPLATE.yaml`)**:
   Designed for monolithic libraries, pure algorithms, and synchronous function exports:
   ```yaml
   interfaces:
     exports:
       - name: "TokenValidator"
         type: "class"
         signature: "def validate_token(token: str) -> Claims:"
         description: "Validates JWT signature and returns claims"
   ```

2. **Distributed Choreography Workflows (`SPEC-SWF-TEMPLATE.yaml`)**:
   Designed for distributed microservices, event-driven interactions, asynchronous callbacks, and distributed transaction saga compensations. Utilizes the **Hybrid Envelope Architecture**: the outer envelope preserves SDD metadata and traceability, while an embedded `workflow:` block houses a valid CNCF Serverless Workflow v0.8 state machine (`subtype: workflow`). See [`SPEC_WORKFLOW_STANDARD.md`](SPEC_WORKFLOW_STANDARD.md) and [`framework/governance/workflows/spec-choreography-contract.sw.yaml`](../../governance/workflows/spec-choreography-contract.sw.yaml).

## Templates & Reference Documents

| File | Purpose |
|------|---------|
| `SPEC-TEMPLATE.yaml` | **Default** — full template with embedded authoring guidance. Self-documenting for AI agents. |
| `SPEC-SWF-TEMPLATE.yaml` | **Workflow Subtype** — Hybrid Envelope housing CNCF Serverless Workflow (v0.8) for distributed component choreography and saga compensation. |
| `SPEC_WORKFLOW_STANDARD.md` | Normative standard specifying interface/event mapping to CNCF Serverless Workflow state primitives. |
| `SPEC-MVP-TEMPLATE.yaml` | Minimal template for rapid prototyping. |
| `SPEC-00_index.TEMPLATE.md` | SPEC registry template — tracks planned and active SPECs per project |
