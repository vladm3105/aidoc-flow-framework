# PRD Workflow Standard — Layer 02

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.91.0 |
| Authority | Decision GD-60 (framework/governance/DECISIONS.md) |

---

## 1. Overview & Architectural Scope

This specification establishes the **normative standard** for modeling Layer 02 (PRD — Product Requirements Document) product feature decomposition, multi-container architectural partitioning, feature prioritization, acceptance threshold validation, and requirement invalidation compensation sagas using the **CNCF Serverless Workflow DSL v0.8 (YAML)** (`specVersion: "0.8"`).

In the 10-layer SDD framework:
```text
BRD (01) → PRD (02) → EARS (03) → BDD (04) → ADR (05) → SPEC (06) → TDD (07) → IPLAN (08) → Code → CHG (09) → EVAL (10)
           ^^^^^^^^^
           This Layer
```

PRD occupies the **Container level** in the SDD C4 architecture model. It translates high-level business goals (BRD) into product features, functional blocks, user personas, and container service boundaries.

While single-container product initiatives can be modeled using static declarative templates, complex enterprise systems feature multi-container topologies with distributed service responsibilities, concurrent feature decomposition trees, quantitative SLA/capacity thresholds (`@threshold:`), and cross-feature prioritization matrices. This standard provides an engine-agnostic, declarative execution workflow for validating and ratifying product requirements.

---

## 2. Primitive Mapping: PRD to CNCF Serverless Workflow

The table below defines the formal mapping of PRD product feature decomposition primitives to CNCF Serverless Workflow states:

| PRD Product Primitive | CNCF State Type | Purpose & Operational Semantics |
|---|---|---|
| **Initiative Ingestion** | `operation` / `inject` | Parses product initiative backlog, extracts executive summary, and maps upstream BRD references (`@brd:`). |
| **Container Decomposition** | `parallel` | Fan-out decomposing features concurrently across distinct C4 container boundaries (e.g. Ingress Gateway, Core Services, Persistence Stores). |
| **Feature Prioritization** | `operation` | Computes weighted utility scores (e.g., RICE scoring across Reach, Impact, Confidence, Effort) to establish implementation order. |
| **Acceptance Threshold Validation** | `operation` | Validates quantitative SLA, latency, and capacity bounds (`@threshold:` definitions) against business targets. |
| **BRD Strategic Alignment Gate** | `switch` | Evaluates upstream traceability, minimum viability criteria, and budget/timeline compliance to route to ratification, negotiation, or rejection. |
| **Stakeholder Scope Negotiation** | `callback` | Emits scope/budget adjustment notices and suspends execution awaiting correlated `ProductScopeAdjustmentEvent` (with timeout). |
| **Product Contract Ratification** | `operation` | Emits canonical SHA-256 hash IDs (`PRD.{doc_id}.{section_id}.{hash}`) and publishes approved features to downstream EARS. |
| **Requirement Invalidation Saga** | `operation` (`usedForCompensation: true`) | Compensating transaction triggered on rejection or cancellation, invalidating downstream draft artifacts across EARS, BDD, ADR, and SPEC. |

---

## 3. Dual-Template Architecture & Selection Matrix

Layer 02 provides two canonical authoring templates. Authors and autonomous AI agents MUST select the template matching the structural complexity of the product initiative:

```text
                              ┌───────────────────────────────────┐
                              │  Does the product initiative span │
                              │  multiple C4 containers, feature  │
                              │  DAGs, or require RICE scoring?   │
                              └─────────────────┬─────────────────┘
                                                │
                                ┌───────────────┴───────────────┐
                                │                               │
                                ▼ YES                           ▼ NO
                ┌──────────────────────────────┐ ┌──────────────────────────────┐
                │   PRD-SWF-TEMPLATE.yaml      │ │       PRD-TEMPLATE.yaml      │
                │   (Hybrid Envelope Subtype)  │ │      (Standard Declarative)  │
                │                              │ │                              │
                │  - Embedded CNCF v0.8 Graph  │ │  - Declarative YAML tables   │
                │  - Parallel Container Decomp │ │  - Standard feature backlog  │
                │  - Automated RICE Scoring    │ │  - Single-container systems │
                │  - Threshold Validation Gate │ │  - Monolithic initiatives    │
                │  - Invalidation Compensation │ │                              │
                └──────────────────────────────┘ └──────────────────────────────┘
```

### Selection Rules:
1. **Use `PRD-TEMPLATE.yaml`** when the initiative targets a single container, isolated component, or monolithic service with direct, linear requirements.
2. **Use `PRD-SWF-TEMPLATE.yaml`** when the initiative spans multiple independently deployable containers, establishes cross-container dependencies, requires multi-criteria feature prioritization (RICE), or enforces automated acceptance threshold validation.

---

## 4. Graph Integrity Invariants

All PRD workflow definitions (whether embedded in `PRD-SWF-TEMPLATE.yaml` or standalone under `framework/governance/workflows/`) MUST satisfy five structural invariants:

### Invariant P-WF01: Container Boundary Isolation
- Parallel decomposition branches MUST map to distinct C4 container boundaries (e.g. gateway, domain service, datastore).
- Cross-container coupling within a single parallel branch is strictly forbidden.

### Invariant P-WF02: Quantitative Acceptance Thresholds
- Every threshold bound (`@threshold:`) defined within PRD acceptance criteria MUST specify a concrete numeric value and unit (e.g. `p95 < 50ms`, `availability >= 99.99%`).
- Vague adjectives (`"high performance"`, `"scalable"`, `"real-time"`) are non-conformant and MUST fail threshold validation.

### Invariant P-WF03: Upstream BRD Traceability Parity
- Every functional feature declared in a PRD workflow MUST trace to at least one valid upstream BRD requirement ID (`@brd: BRD.NN.07.xxxx` or `@brd: BRD.NN.08.xxxx`).
- Unanchored features lacking BRD traceability MUST be rejected during the strategic alignment gate.

### Invariant P-WF04: Objective Prioritization Model
- Feature prioritization states MUST compute deterministic, quantifiable rankings using standard models (e.g., RICE = $(Reach \times Impact \times Confidence) / Effort$ or MoSCoW tiers).
- Unranked or arbitrarily ordered feature sets are non-conformant.

### Invariant P-WF05: Downstream Invalidation Compensation
- Any state machine validating product initiatives MUST bind rejection states to an automated compensation action (`compensatedBy: InvalidateDownstreamArtifacts`).
- The compensation action MUST revoke provisional downstream EARS requirements, BDD scenarios, ADRs, or SPEC interactions derived from the rejected features.

---

## 5. Zero-Runtime LangGraph Execution Model

In strict accordance with **Principle D-0013 (Spec Engine-Agnostic Purity)**, `framework/` ships pure declarative specifications without bundling Python runtime packages, workflow interpreters, or vendor SDKs.

### Agentic Execution Mapping
When an autonomous AI agent or execution harness executes a PRD workflow via LangGraph:
1. **Workflow Ingestion**: The agent parses `prd-feature-decomposition.sw.yaml` into state nodes.
2. **State Translation**:
   - `operation` states map to deterministic LLM/tool execution nodes (e.g., backlog parsers, RICE calculators).
   - `parallel` states execute independent container decomposition branches concurrently using async tasks.
   - `switch` states evaluate JSONPath/CEL expressions against accumulated product metadata.
   - `callback` states pause the LangGraph thread using checkpointers until stakeholder scope adjustment events are posted.
   - `compensatedBy` states execute rollback handlers when execution paths terminate in rejection.
