# EARS Requirements — Layer 3

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.87.0 |

## Overview

EARS (Easy Approach to Requirements Syntax) formalizes business and product
requirements into precise, testable statements using WHEN-THE-SHALL-WITHIN syntax.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified

## C4 Model Position

EARS is a **refinement step** that formalizes the transition from Context (BRD) to
Container (PRD). It does not have its own C4 level — it translates requirements
into atomic, testable logic for downstream BDD scenarios.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition              ← this layer
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions validating SPEC contracts
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files & Templates

| File | Purpose |
|------|---------|
| `EARS-TEMPLATE.yaml` | **Default Declarative** — full template with embedded authoring guidance for single-system requirements. Self-documenting for AI agents. |
| `EARS-SWF-TEMPLATE.yaml` | **Workflow Subtype** — Hybrid Envelope Architecture housing an embedded CNCF Serverless Workflow state machine for complex, multi-system requirement topologies, dependency DAGs, and BDD-readiness verification. |
| `EARS_WORKFLOW_STANDARD.md` | **Normative Standard** — formal specification defining EARS primitive to CNCF state mappings, DAG integrity rules, and invalidation compensation. |
| `EARS-00_index.TEMPLATE.md` | EARS registry template — tracks planned and active EARS documents per project. |

## Workflow Integration & CNCF Serverless Workflow Standard

Layer 03 adopts the **CNCF Serverless Workflow DSL v0.8 (YAML)** (Decision **GD-59**)
to orchestrate requirement verification graphs:
- **Dependency DAGs**: Parallel resolution of inter-requirement dependencies (`@depends:`).
- **Syntax Parsing**: Automated verification of the 5 EARS patterns (WHEN, WHILE, WHERE, IF, Ubiquitous) and mandatory response clauses (`THE [system] SHALL ... WITHIN ...`).
- **Conflict Analysis**: Deterministic scanning for mutually exclusive states and conflicting operational triggers.
- **BDD-Readiness Gating**: Formal evaluation against the >=90/100 readiness criteria before transition to Layer 04 (BDD).
- **Invalidation Sagas**: Automated compensation (`compensatedBy: InvalidateDownstreamArtifacts`) revoking downstream draft artifacts when requirements are rejected.

See `EARS_WORKFLOW_STANDARD.md` for complete specification rules and graph invariants.

## EARS Syntax Patterns

| Pattern | Trigger | Format |
|---------|---------|--------|
| Event-Driven | External event | WHEN [trigger], THE [component] SHALL [action] WITHIN [timing] |
| State-Driven | System state | WHILE [state], THE [component] SHALL [behavior] WITHIN [context] |
| Optional | Feature/config present | WHERE [feature enabled], THE [component] SHALL [behavior] |
| Unwanted | Error condition | IF [error], THE [component] SHALL [recovery] WITHIN [timing] |
| Ubiquitous | Always applies | THE [component] SHALL [behavior] for [scope] |

Every pattern uses the canonical EARS response clause `THE [component] SHALL …`
— never a `THEN` connective. `WITHIN [timing]` is a framework extension (not
stock EARS) supporting quantifiability. A genuinely multi-condition requirement
*composes* these patterns (e.g. `WHILE [state], WHEN [event], THE … SHALL …`) —
that is composition, not a sixth pattern.

## Pattern decision tree

When the pattern is not obvious, walk this tree top-down — first match wins:

```text
Is this a normal operating state?
  → YES → WHILE (state-driven)
  → NO → Is this triggered by a specific event?
    → YES → WHEN (event-driven)
    → NO → Is this an error/failure condition?
      → YES → IF (unwanted behavior)
      → NO → Is this a universal invariant?
        → YES → THE-SHALL (ubiquitous)
        → NO → Is this feature-gated?
          → YES → WHERE (optional)
```

Common traps: a liveness check ("the service is healthy") is a normal state →
`WHILE`, not `IF`; an unreachable dependency is an error → `IF`, not `WHILE`;
a universal invariant ("all traffic flows through the gateway") → `THE-SHALL`,
not `WHEN`.

## Element IDs

Hash-based, content-derived IDs scoped to EARS content:
> The SHA-256 form is the **canonicalization target**: engines emit stable opaque strings that *should* match it. `rehash --check` verification is shipped for BRD §7 only (PROVISIONAL-IDS-002 Phase 1); extraction for this layer is Phase 2+. See `ID_NAMING_STANDARDS.md`.

```text
Format: EARS.{doc_id}.{section_id}.{hash}
Example: EARS.01.03.c4d8
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{norm(title)}:{norm(description)}"`, first 4 hex chars (the canonicalization target; not verified until `rehash --check`). `norm()` is the normalization transform, and `governance/ID_NAMING_STANDARDS.md` is its **single source** — along with the byte-exact input assembly. Do not re-specify it here.
See template `metadata.id_standard` for details.

## Upstream Traceability

Each EARS links to its source PRD via its necessary-upstream tag (BRD is reached transitively through the PRD):

```text
@prd: PRD.NN.09.xxxx    (required — links to PRD functional requirement)
```
