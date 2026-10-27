# PRD Workflow Standard — Layer 02

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.96.21 |
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

## 3. Two-Graph & Dual-Template Architecture Selection Matrix

Layer 02 employs the framework's **Two-Graph Dual-Plane Architecture**, pairing an executable process workflow with an atomic content graph to generate and ratify product specifications:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 02 PRD TWO-GRAPH ARCHITECTURE                                │
├────────────────────────────────────────────────────────┬────────────────────────────────────┤
│          GRAPH 1: PROCESS DAG (CONTROL PLANE)          │   GRAPH 2: CONTENT GRAPH (DATA)    │
│       PRD-SWF-TEMPLATE.yaml (Hybrid Envelope)          │       (PRD-GRAPH-TEMPLATE.yaml)    │
├────────────────────────────────────────────────────────┼────────────────────────────────────┤
│ • CNCF Serverless Workflow v0.8 state machine DAG      │ • SDD-GRAPH v2.0 Property Graph    │
│ • Flow of HOW to decompose, prioritize & ratify PRD    │ • Content of WHAT features exist   │
│ • Parallel container decomposition (C4 Level 2)        │ • Product features & user stories  │
│ • Automated RICE scoring & threshold validation        │ • Quality thresholds (@threshold:) │
│ • Stakeholder scope negotiation review callbacks       │ • Relational links (realizes, etc) │
│ • Requirement invalidation saga (compensatedBy)        │ • Validated via BTV engine         │
└───────────────────────────┬────────────────────────────┴─────────────────┬──────────────────┘
                            │                                              │
                            ▼                                              ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │               DOCUMENT GENERATION & PROJECTION               │
                    ├──────────────────────────────────────────────────────────────┤
                    │ • Process DAG orchestrates feature decomposition & scoring   │
                    │ • Agent actions populate and mutate atomic nodes in Data     │
                    │ • BTV verifies topological closure & container boundaries    │
                    │ • Observability Adapter projects graph into PRD-TEMPLATE.yaml│
                    └──────────────────────────────────────────────────────────────┘
```

### Dual-Template Selection Rules:
Authors and autonomous AI agents select the template matching the structural complexity of the product initiative:
1. **Use Two-Graph Generation (`PRD-SWF-TEMPLATE.yaml` [Hybrid Envelope Subtype] + `PRD-GRAPH-TEMPLATE.yaml` [Property Graph])** when the initiative spans multiple independently deployable containers, establishes cross-container dependencies, requires multi-criteria feature prioritization (RICE), or enforces automated acceptance threshold validation. The Process DAG guides decomposition, populates the Content Graph, executes BTV verification, and projects the final PRD specification.
2. **Use Companion Declarative (`PRD-TEMPLATE.yaml`)** directly when the initiative targets a single container, isolated component, or monolithic service with direct, linear requirements without branching or automated compensations.

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

### Invariant P-WF06: Approved Stack Candidate Elaboration
- In Section 12/14 (`adr_topic_elaboration`), technical options proposed for evaluation must map to approved platform technology stack categories ([`TECHNOLOGY_STACK_USAGE_GUIDE.md`](../../governance/TECHNOLOGY_STACK_USAGE_GUIDE.md)), preparing concrete candidate inputs for Layer 05 ADR selection.

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
3. **Dual-Graph Pipeline Coordination**:
   - **Step 1 (Process DAG Orchestration)**: LangGraph drives the authoring agent through the feature decomposition workflow.
   - **Step 2 (Content Graph Mutation)**: As operations complete, the agent instantiates and updates nodes (`product_feature`, `user_story`, `quality_threshold`) and edges (`realizes`, `verifies`, `depends_on`) in `PRD-GRAPH-TEMPLATE.yaml`.
   - **Step 3 (Binary Topological Validation - BTV)**: The state machine executes BTV asserting container acyclicity, trace closure, and threshold validity.
   - **Step 4 (Document Generation / Read Projection)**: The Observability Adapter compiles the validated property graph into the canonical human-readable document (`PRD-TEMPLATE.yaml` structure).

---

## 6. Closed Dual-Flow Quality Loop: Authoring & Review Saga Binding (CHG-111, GD-98)

To eliminate the decoupling between artifact authoring and review crew evaluation, Layer 02 adheres to the closed dual-flow loop:

1. **Explicit Author Rubric Binding**:
   - The document envelope `metadata:` block declares `author_persona: "product_owner"` and `author_playbook: "framework/playbooks/02_PRD/product_owner.md"`.
   - Autonomous drafting agents derive their authoring constraints and product decomposition priorities directly from this rubric prior to drafting.

2. **Mandatory Review Saga Invalidation & Gating**:
   - Prior to final ratification (`RatifyProductSpecification`), the authoring workflow executes `InvokeReviewSagaGate` via the `invokeReviewSaga` custom function, invoking the designated review saga subflow (`prd-review-remediation-flow`).
   - The review saga coordinates multi-agent review crew evaluation across persona playbooks, enforcing the quality gate condition:
     `${ .blocking_findings == 0 and .gate_passed == true }`.
   - If findings or defects are uncovered, the saga executes an automated remediation loop, halting ratification until all P0/P1 blockers are resolved.

---

## 7. 5-Step Closed Layer Lifecycle and CloudEvent Handoff (CHG-112, GD-99)

Layer 02 PRD implements the standardized 5-step closed lifecycle:
1. **Stage 1 (Authoring)**: Product owner authors feature decomposition, user stories, and performance thresholds.
2. **Stage 2 (Review & Remediation)**: Review saga executes multi-persona review. Unresolved blockers trigger author remediation (`RemediateLayerDraft`, author: `product_manager`) before re-entering `InvokeReviewSagaGate` (Circuit Breaker CB-1: max 2 remediation passes / 3 review cycles).
3. **Stage 3 (Layer Boundary Gate Verification)**: `VerifyLayerCloseoutGate` verifies `GATE-01` exit criteria (`GATE-01_BUSINESS_PRODUCT.md`).
4. **Stage 4 (Baseline Sealing & SDD Graph Lineage)**: `SealLayerDocumentBaseline` seals frontmatter status to `Baselined` with SHA-256 checksum; `RegisterSddGraphBaselineNode` registers `PrdNode` in SDD graph and locks incoming edges.
5. **Stage 5 (Downstream Handoff CloudEvent Emission)**: `EmitLayerHandoffEvent` publishes `PrdClosedAndBaselinedEvent` (`org.aidoc.sdd.layer02.prd.closed`) with payload `documentId`, `features`, `@threshold:`, authorizing Layer 03 (EARS) start.
