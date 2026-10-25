# BRD Workflow Standard — Layer 01

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.96.15 |
| Authority | Decision GD-61 (framework/governance/DECISIONS.md) |

---

## 1. Overview & Architectural Scope

This specification establishes the **normative standard** for modeling Layer 01 (BRD — Business Requirements Document) business requirements validation, value stream mapping, strategic ROI alignment, stakeholder consensus orchestration, and strategic initiative invalidation compensation sagas using the **CNCF Serverless Workflow DSL v0.8 (YAML)** (`specVersion: "0.8"`).

In the 10-layer SDD framework:
```text
BRD (01) → PRD (02) → EARS (03) → BDD (04) → ADR (05) → SPEC (06) → TDD (07) → IPLAN (08) → Code → CHG (09) → EVAL (10)
^^^^^^^^
This Layer
```

BRD occupies the **Context level** in the SDD C4 architecture model. It formalizes enterprise vision, customer actors, external market drivers, core business objectives, and organizational boundaries.

While single-capability business initiatives can be modeled using static declarative templates, complex enterprise initiatives feature multi-stream value flows with cross-departmental stakeholders, quantitative ROI and financial feasibility thresholds, regulatory compliance gates, and executive steering committee consensus cycles. This standard provides an engine-agnostic, declarative execution workflow for validating and ratifying business requirements before product decomposition in Layer 02 (PRD).

---

## 2. Primitive Mapping: BRD to CNCF Serverless Workflow

The table below defines the formal mapping of BRD business requirement primitives to CNCF Serverless Workflow states:

| BRD Business Primitive | CNCF State Type | Purpose & Operational Semantics |
|---|---|---|
| **Strategic Theme Ingestion** | `operation` / `inject` | Ingests strategic theme, parses market context, business drivers, problem statement, and executive intent. |
| **Value Stream Decomposition** | `parallel` | Fan-out analyzing concurrent operational value streams (e.g. Customer Journey, Core Operations, Financial & Regulatory Governance). |
| **ROI & Feasibility Analysis** | `operation` | Computes quantitative economic metrics (ROI, Net Present Value, payback period, capital allocation bounds). |
| **Strategic Alignment Gate** | `switch` | Evaluates business objective fit, ROI viability, and budget allocation to branch to ratification, steering review, or rejection. |
| **Steering Committee Review** | `callback` | Emits review request and pauses execution awaiting correlated `ExecutiveSteeringApprovalEvent` (with timeout). |
| **Business Initiative Ratification** | `operation` | Emits canonical SHA-256 hash IDs (`BRD.{doc_id}.{section_id}.{hash}`) and publishes approved baseline to downstream PRD. |
| **Strategic Invalidation Saga** | `operation` (`usedForCompensation: true`) | Compensating transaction triggered on cancellation or rejection, revoking downstream PRD draft allocations and resource commitments. |

---

## 3. Two-Graph & Dual-Template Architecture Selection Matrix

Layer 01 employs the framework's **Two-Graph Dual-Plane Architecture**, pairing an executable process workflow with an atomic content graph to generate and ratify business requirements:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 01 BRD TWO-GRAPH ARCHITECTURE                                │
├────────────────────────────────────────────────────────┬────────────────────────────────────┤
│          GRAPH 1: PROCESS DAG (CONTROL PLANE)          │   GRAPH 2: CONTENT GRAPH (DATA)    │
│       BRD-SWF-TEMPLATE.yaml (Hybrid Envelope)          │       (BRD-GRAPH-TEMPLATE.yaml)    │
├────────────────────────────────────────────────────────┼────────────────────────────────────┤
│ • CNCF Serverless Workflow v0.8 state machine DAG      │ • SDD-GRAPH v2.0 Property Graph    │
│ • Flow of HOW to create, evaluate & ratify the BRD     │ • Content of WHAT entities exist   │
│ • Value stream mapping (Customer, Ops, Financial)      │ • Business drivers & objectives    │
│ • Automated quantitative ROI & feasibility gating      │ • Operational capabilities         │
│ • Executive steering committee review callbacks        │ • Relational links (realizes, etc) │
│ • Strategic invalidation saga (compensatedBy)          │ • Validated via BTV engine         │
└───────────────────────────┬────────────────────────────┴─────────────────┬──────────────────┘
                            │                                              │
                            ▼                                              ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │               DOCUMENT GENERATION & PROJECTION               │
                    ├──────────────────────────────────────────────────────────────┤
                    │ • Process DAG orchestrates authoring & verification steps    │
                    │ • Agent actions populate and mutate atomic nodes in Data     │
                    │ • BTV verifies topological closure & acyclicity              │
                    │ • Observability Adapter projects graph into BRD-TEMPLATE.yaml│
                    └──────────────────────────────────────────────────────────────┘
```

### Dual-Template Selection Rules:
Authors and autonomous AI agents select the template matching the structural complexity of the business initiative:
1. **Use Two-Graph Generation (`BRD-SWF-TEMPLATE.yaml` [Hybrid Envelope Subtype] + `BRD-GRAPH-TEMPLATE.yaml` [Property Graph])** when the initiative spans multiple operational value streams, requires formal financial feasibility/ROI verification, involves multi-party executive steering reviews, or mandates automated invalidation rollbacks. The Process DAG guides authoring, populates the Content Graph, executes BTV verification, and projects the final BRD specification.
2. **Use Companion Declarative (`BRD-TEMPLATE.yaml`)** directly when the business initiative is focused on a single capability, direct business workflow, or minor enhancement with straightforward stakeholder alignment where state machine orchestration is not needed.

---

## 4. Graph Integrity Invariants

All BRD workflow definitions (whether embedded in `BRD-SWF-TEMPLATE.yaml` or standalone under `framework/governance/workflows/`) MUST satisfy five structural invariants:

### Invariant B-WF01: SMART Business Objectives
- Every business objective evaluated in a BRD workflow MUST conform to SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound).
- Each objective MUST define a concrete KPI and targeted measurable improvement.

### Invariant B-WF02: Quantified Economic Viability
- Economic evaluation states MUST compute deterministic, quantifiable financial metrics (e.g., ROI %, Net Present Value, or payback duration).
- Unquantified statements of benefit without economic verification MUST fail feasibility evaluation.

### Invariant B-WF03: Multi-Stakeholder Consensus
- Strategic alignment gates MUST verify sign-off across all required governance roles (Executive Sponsor, Business Lead, Enterprise Architect).
- Missing stakeholder approvals MUST route to an explicit `callback` state rather than automatic acceptance.

### Invariant B-WF04: Operational Value Stream Coverage
- Parallel value stream mapping states MUST span both external customer-facing journeys and internal operational/regulatory processes.
- Unbalanced initiatives omitting operational support capabilities are non-conformant.

### Invariant B-WF05: Strategic Invalidation Compensation
- Any state machine validating business initiatives MUST bind rejection or cancellation states to an automated compensation action (`compensatedBy: InvalidateStrategicInitiatives`).
- The compensation action MUST revoke provisional downstream PRD draft allocations, reserved capacity, and portfolio slots.

### Invariant B-WF06: Strategic Architecture Topic Framing
- Section 8 (`adr_topics`) must frame required decisions as business capabilities rather than prematurely hardcoding specific technology vendors, while recording candidate baselines that prioritize options from the approved enterprise technology stack ([`TECHNOLOGY_STACK_USAGE_GUIDE.md`](../../governance/TECHNOLOGY_STACK_USAGE_GUIDE.md)) for downstream Layer 05 ADR evaluation.

---

## 5. Zero-Runtime LangGraph Execution Model

In strict accordance with **Principle D-0013 (Spec Engine-Agnostic Purity)**, `framework/` ships pure declarative specifications without bundling Python runtime packages, workflow interpreters, or vendor SDKs.

### Agentic Execution Mapping
When an autonomous AI agent or execution harness executes a BRD workflow via LangGraph:
1. **Workflow Ingestion**: The agent parses `brd-business-validation.sw.yaml` into state nodes.
2. **State Translation**:
   - `operation` states map to deterministic LLM/tool execution nodes (e.g., strategic theme parsers, ROI calculators).
   - `parallel` states execute independent value stream analysis branches concurrently using async workers.
   - `switch` states evaluate JSONPath/CEL expressions against accumulated business metrics.
   - `callback` states pause the LangGraph thread using checkpointers until executive steering approval events are posted.
   - `compensatedBy` states execute rollback handlers when execution paths terminate in rejection.
3. **Dual-Graph Pipeline Coordination**:
   - **Step 1 (Process DAG Orchestration)**: LangGraph drives the authoring agent through the state machine.
   - **Step 2 (Content Graph Mutation)**: As operations complete, the agent instantiates and updates nodes (`business_driver`, `strategic_objective`, `operational_capability`) and edges (`realizes`, `verifies`) in `BRD-GRAPH-TEMPLATE.yaml`.
   - **Step 3 (Binary Topological Validation - BTV)**: The state machine executes BTV asserting DAG integrity, trace closure, and schema conformance.
   - **Step 4 (Document Generation / Read Projection)**: The Observability Adapter compiles the validated property graph into the canonical human-readable document (`BRD-TEMPLATE.yaml` structure).

---

## 6. Closed Dual-Flow Quality Loop: Authoring & Review Saga Binding (CHG-111, GD-98)

To eliminate the decoupling between artifact authoring and review crew evaluation, Layer 01 adheres to the closed dual-flow loop:

1. **Explicit Author Rubric Binding**:
   - The document envelope `metadata:` block declares `author_persona: "business_analyst"` and `author_playbook: "framework/playbooks/01_BRD/business_analyst.md"`.
   - Autonomous drafting agents derive their authoring constraints and strategic themes directly from this rubric prior to drafting.

2. **Mandatory Review Saga Invalidation & Gating**:
   - Prior to final ratification (`RatifyBusinessSpecification`), the authoring workflow executes `InvokeReviewSagaGate` via the `invokeReviewSaga` custom function, invoking the designated review saga subflow (`brd-review-remediation-flow`).
   - The review saga coordinates multi-agent review crew evaluation across persona playbooks, enforcing the quality gate condition:
     `${ .blocking_findings == 0 and .gate_passed == true }`.
   - If findings or defects are uncovered, the saga executes an automated remediation loop, halting ratification until all P0/P1 blockers are resolved.

---

## 7. 5-Step Closed Layer Lifecycle and CloudEvent Handoff (CHG-112, GD-99)

Layer 01 BRD implements the standardized 5-step closed lifecycle:
1. **Stage 1 (Authoring)**: Business analyst authors strategic theme, value stream decomposition, and quantitative ROI analysis.
2. **Stage 2 (Review & Remediation)**: Review saga executes multi-persona review. Unresolved blockers trigger author remediation (`RemediateLayerDraft`, author: `business_analyst`) before re-entering `InvokeReviewSagaGate` (Circuit Breaker CB-1: max 2 remediation passes / 3 review cycles).
3. **Stage 3 (Layer Boundary Gate Verification)**: `VerifyLayerCloseoutGate` verifies `GATE-01` exit criteria (`GATE-01_BUSINESS_PRODUCT.md`).
4. **Stage 4 (Baseline Sealing & SDD Graph Lineage)**: `SealLayerDocumentBaseline` seals frontmatter status to `Baselined` with SHA-256 checksum; `RegisterSddGraphBaselineNode` registers `BrdNode` in SDD graph and locks incoming edges.
5. **Stage 5 (Downstream Handoff CloudEvent Emission)**: `EmitLayerHandoffEvent` publishes `BrdClosedAndBaselinedEvent` (`org.aidoc.sdd.layer01.brd.closed`) with payload `initiativeId`, `brd_tags`, authorizing Layer 02 (PRD) start.
