# BRD Workflow Standard — Layer 01

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.91.1 |
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

## 3. Dual-Template Architecture & Selection Matrix

Layer 01 provides two canonical authoring templates. Authors and autonomous AI agents MUST select the template matching the structural complexity of the business initiative:

```text
                              ┌───────────────────────────────────┐
                              │  Does the business initiative     │
                              │  span multiple value streams,     │
                              │  ROI models, or executive gates?  │
                              └─────────────────┬─────────────────┘
                                                │
                                ┌───────────────┴───────────────┐
                                │                               │
                                ▼ YES                           ▼ NO
                ┌──────────────────────────────┐ ┌──────────────────────────────┐
                │   BRD-SWF-TEMPLATE.yaml      │ │       BRD-TEMPLATE.yaml      │
                │   (Hybrid Envelope Subtype)  │ │      (Standard Declarative)  │
                │                              │ │                              │
                │  - Embedded CNCF v0.8 Graph  │ │  - Declarative YAML tables   │
                │  - Parallel Value Streams    │ │  - Standard objective table  │
                │  - Automated ROI Calculation │ │  - Single-capability apps   │
                │  - Steering Review Callback  │ │  - Small/focused initiatives │
                │  - Invalidation Compensation │ │                              │
                └──────────────────────────────┘ └──────────────────────────────┘
```

### Selection Rules:
1. **Use `BRD-TEMPLATE.yaml`** when the business initiative is focused on a single capability, direct business workflow, or minor enhancement with straightforward stakeholder alignment.
2. **Use `BRD-SWF-TEMPLATE.yaml`** when the initiative spans multiple operational value streams, requires formal financial feasibility/ROI verification, involves multi-party executive steering reviews, or mandates automated invalidation rollbacks.

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
