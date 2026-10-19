# Architecture Decision Records (ADR) — Layer 5

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.96.7 |

## Overview

ADRs document architecture decisions using the Context-Decision-Consequences
pattern. Each ADR addresses ONE decision, synthesizing inputs from EARS and BDD (which transitively carry PRD context).

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified

## C4 Model Position

ADR is the **decision bridge** between Container (PRD) and Component (SPEC) — it does not have its own C4 level. ADR records architectural decisions that shape the Component-level design and serves as the **formal technology selection gate** immediately after BDD (governed by [`TECHNOLOGY_STACK_USAGE_GUIDE.md`](../../governance/TECHNOLOGY_STACK_USAGE_GUIDE.md)).

```text
Problem Space (Technology-Agnostic):
  Context (BRD)    — business environment, actors, boundaries
    └─ PRD         — product features, functional blocks, ADR topics
    └─ EARS        — timing constraints, latency budgets, throughput SLAs
    └─ BDD         — executable acceptance scenarios & failure modes
Technology Selection Gate:
  ADR (Layer 5)    — selects ONE architecture & stack choice via MCDA     ← this layer
Solution Space (Technology-Bound):
  Component (SPEC) — component interfaces, data models, behavior contracts
    └─ TDD         — test case definitions validating SPEC contracts
    └─ IPLAN       — execution plan bridging TDD to Code
```

## Files & Templates

| File | Purpose |
|---|---|
| `ADR-TEMPLATE.yaml` | **Standard** — static template with embedded authoring guidance for atomic architectural decisions. |
| `ADR-GRAPH-TEMPLATE.yaml` | **Canonical Data Plane (Tier 2)** — SDD-GRAPH v2.0 property graph slice encoding architecture decisions, trade-offs, and driver links. Source of truth in git. |
| `ADR-SWF-TEMPLATE.yaml` | **Workflow (Tier 1)** — Hybrid Envelope Architecture housing an executable CNCF Serverless Workflow state machine for multi-candidate trade-off analysis. |
| `ADR_WORKFLOW_STANDARD.md` | **Normative Standard** — formal mapping of architecture decision evaluation primitives to CNCF Serverless Workflow state machines. |
| `ADR-00_index.TEMPLATE.yaml` | ADR & Project Technology Stack Registry template — tracks planned/active ADRs and houses the canonical agent-readable technology inventory for security monitoring and automated updates. |

## Three-Tier Architecture & Dual-Template Selection Matrix

Layer 05 supports three complementary representations per the SDD Three-Tier Model and Dual-Template selection based on decision complexity (GD-57):

| Decision Profile | Primary Artifact | Secondary Artifact | Operational Rationale |
|---|---|---|---|
| Single-candidate, localized design choice | `ADR-TEMPLATE.yaml` | — | Declarative, lightweight, lowest overhead. |
| Graph-first repository, AI agent slicing | `ADR-GRAPH-TEMPLATE.yaml` | Compiled `.md` | Discrete property graph nodes and edges optimized for Kùzu / openCypher context slicing. |
| High-stakes multi-candidate trade-offs (MCDA), RFC reviews, or invalidation sagas | `ADR-SWF-TEMPLATE.yaml` | `ADR-GRAPH-TEMPLATE.yaml` | Embedded CNCF v0.8 workflow orchestrating candidate evaluation and score weighting. |

### Template Implementations

1. **Standard Template (`ADR-TEMPLATE.yaml`)**:
   - Best for straightforward, single-candidate decisions or localized design choices.
   - Evaluates alternatives via lightweight prose comparison tables.
   - Pure structural YAML validated directly by `sdd_doc_lint`.

2. **CNCF Workflow Template (`ADR-SWF-TEMPLATE.yaml`)**:
   - Required for complex, high-stakes decisions with $\ge 2$ competing candidates, distributed impact, or multi-criteria quality attribute trade-offs (MCDA).
   - Embeds an executable CNCF Serverless Workflow (`specVersion: "0.8"`) state machine under `architecture_flow.decision_workflow`.
   - Automates parallel candidate evaluation, weighted utility scoring, stakeholder RFC review callbacks, and rejection archive compensation.
   - Fully compliant with the 12 required sections asserted by `sdd_doc_lint`.

## ADR Status Lifecycle

ADR uses a **different status lifecycle** from other layers:

```text
Proposed → Accepted → Deprecated → Superseded
```

(NOT Draft/In Review/Approved)

| Status | Gating Criteria | Meaning |
|---|---|---|
| Proposed | Draft / Under Review | Decision under evaluation |
| Accepted | Binary Topological Pass | Decision approved, 100% DAG completeness, ready for SPEC |
| Deprecated | — | Decision no longer relevant |
| Superseded | — | Replaced by newer ADR |

## Element IDs

Hash-based, content-derived IDs scoped to ADR content:
> The SHA-256 form is the **canonicalization target**: engines emit stable opaque strings that *should* match it. `rehash --check` verification is shipped for BRD §7 only (PROVISIONAL-IDS-002 Phase 1); extraction for this layer is Phase 2+. See `ID_NAMING_STANDARDS.md`.

```text
Format: ADR.{doc_id}.{section_id}.{hash}
Example: ADR.01.03.e5b1
```

## Upstream Traceability

ADR requires its necessary-upstream tags — @ears + @bdd (Layer 5 `required_tags`):

```text
@ears: EARS.NN.03.xxxx   (timing constraints informing decision)
@bdd: BDD.NN.03.xxxx     (integration/failure scenarios)
```
