# Product Requirements Documents (PRD) — Layer 2

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.88.1 |

## Overview

PRDs define product features, user personas, container service boundaries, and
acceptance criteria as the second step in the SDD workflow. Each PRD corresponds
to one BRD iteration cycle.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code → EVAL → Verified

## C4 Model Mapping

PRD is the **Container** level in the C4 architecture model. Content describes
product features, functional blocks, and container boundaries — not business
environment (Context), component details (Component), or implementation details (Code).

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition
Container (PRD)  — product features, functional blocks                 ← this layer
  └─ ADR         — decisions that shape Component architecture
Component (SPEC) — component interfaces, data models, behavior contracts
  └─ TDD         — test case definitions validating SPEC contracts
  └─ IPLAN       — execution plan bridging TDD to Code
```

## Files & Templates

| File | Purpose |
|------|---------|
| `PRD-TEMPLATE.yaml` | **Default Declarative** — full template with embedded authoring guidance for single-container product features. Self-documenting for AI agents. |
| `PRD-SWF-TEMPLATE.yaml` | **Workflow Subtype** — Hybrid Envelope Architecture housing an embedded CNCF Serverless Workflow state machine for multi-container product decomposition, RICE prioritization, and threshold validation. |
| `PRD_WORKFLOW_STANDARD.md` | **Normative Standard** — formal specification defining PRD primitive to CNCF state mappings, container isolation rules, and invalidation compensation. |
| `PRD-00_index.TEMPLATE.md` | PRD registry template — tracks planned and active PRDs per project. |

## Workflow Integration & CNCF Serverless Workflow Standard

Layer 02 adopts the **CNCF Serverless Workflow DSL v0.8 (YAML)** (Decision **GD-60**)
to orchestrate product feature decomposition and threshold verification:
- **Container Decomposition**: Parallel fan-out decomposing initiatives across distinct C4 container boundaries.
- **RICE Feature Prioritization**: Automated utility scoring across Reach, Impact, Confidence, and Effort.
- **Acceptance Thresholds**: Formal validation of quantitative SLA and capacity bounds (`@threshold:` definitions).
- **BRD Alignment Gating**: Strategic business alignment checks verifying upstream `@brd:` traceability.
- **Invalidation Sagas**: Automated compensation (`compensatedBy: InvalidateDownstreamArtifacts`) revoking downstream draft artifacts across EARS, BDD, ADR, and SPEC when initiatives are rejected.

See `PRD_WORKFLOW_STANDARD.md` for complete specification rules and graph invariants.

## Element IDs

Hash-based, content-derived IDs scoped to PRD content (not BRD):
> The SHA-256 form is the **canonicalization target**: engines emit stable opaque strings that *should* match it. `rehash --check` verification is shipped for BRD §7 only (PROVISIONAL-IDS-002 Phase 1); extraction for this layer is Phase 2+. See `ID_NAMING_STANDARDS.md`.

```text
Format: PRD.{doc_id}.{section_id}.{hash}
Example: PRD.01.09.b3f2
```

Algorithm: SHA256 of `"{doc_id}:{section_id}:{norm(title)}:{norm(description)}"`, first 4 hex chars (the canonicalization target; not verified until `rehash --check`). `norm()` is the normalization transform, and `governance/ID_NAMING_STANDARDS.md` is its **single source** — along with the byte-exact input assembly. Do not re-specify it here.
See template `metadata.id_standard` for details.

## Upstream Traceability

Each PRD links to its source BRD via `@brd:` tags using BRD hash-based IDs:

```text
@brd: BRD.NN.07.xxxx    (links to BRD functional requirement)
@brd: BRD.NN.08.xxxx    (links to BRD ADR topic)
```
