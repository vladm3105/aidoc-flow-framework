# Architecture Decision Records (ADR) — Layer 5

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.90.2 |


## Overview

ADRs document architecture decisions using the Context-Decision-Consequences
pattern. Each ADR addresses ONE decision, synthesizing inputs from EARS and BDD (which transitively carry PRD context).

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified

## C4 Model Position

ADR is the **decision bridge** between Container (PRD) and Component (SPEC) — it does not have its own C4 level. ADR records architectural decisions that shape the Component-level design.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture        ← this layer
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions validating SPEC contracts
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files

| File | Purpose |
|---|---|
| `ADR-TEMPLATE.yaml` | **Standard** — static template with embedded authoring guidance for atomic architectural decisions. |
| `ADR-SWF-TEMPLATE.yaml` | **Workflow** — Hybrid Envelope Architecture housing an executable CNCF Serverless Workflow state machine for multi-candidate trade-off analysis. |
| `ADR_WORKFLOW_STANDARD.md` | **Normative Standard** — formal mapping of architecture decision evaluation primitives to CNCF Serverless Workflow state machines. |
| `ADR-00_index.TEMPLATE.md` | ADR registry template — tracks planned and active ADRs per project. |

## Dual-Template Architecture

Layer 05 supports two complementary authoring templates depending on decision complexity:

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

| Status | SPEC-Ready Score | Meaning |
|---|---|---|
| Proposed | 70-89% | Decision under evaluation |
| Accepted | >=90% | Decision approved, ready for SPEC |
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
