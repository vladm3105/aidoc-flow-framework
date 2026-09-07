# Architecture Decision Records (ADR) — Layer 5

## Overview

ADRs document architecture decisions using the Context-Decision-Consequences
pattern. Each ADR addresses ONE decision, synthesizing inputs from PRD, EARS, and BDD.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

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
|------|---------|
| `ADR-TEMPLATE.yaml` | **Default** — full template with embedded authoring guidance. Self-documenting for AI agents. |
| `ADR-MVP-TEMPLATE.yaml` | Skeleton — stripped-down structural form. Not standalone. See [BRD README](../01_BRD/README.md) for the template selection rule. |
| `ADR-00_index.TEMPLATE.md` | ADR registry template — tracks planned and active ADRs per project |

## ADR Status Lifecycle

ADR uses a **different status lifecycle** from other layers:

```text
Proposed → Accepted → Deprecated → Superseded
```

(NOT Draft/In Review/Approved)

| Status | SPEC-Ready Score | Meaning |
|--------|-----------------|---------|
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
