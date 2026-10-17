# EARS Workflow Standard — Layer 03

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.96.1 |
| Authority | Decision GD-59 (framework/governance/DECISIONS.md) |

---

## 1. Overview & Architectural Scope

This specification establishes the **normative standard** for modeling Layer 03 (EARS — Easy Approach to Requirements Syntax) requirements analysis, dependency resolution, cross-requirement conflict detection, BDD-readiness gating, and invalidation compensation sagas using the **CNCF Serverless Workflow DSL v0.8 (YAML)** (`specVersion: "0.8"`).

In the 10-layer SDD framework:
```text
BRD (01) → PRD (02) → EARS (03) → BDD (04) → ADR (05) → SPEC (06) → TDD (07) → IPLAN (08) → Code → CHG (09) → EVAL (10)
                      ^^^^^^^^^
                      This Layer
```

EARS translates business goals (BRD) and product features (PRD) into atomic, testable, unambiguous logic statements using five core syntax patterns:
1. **Event-Driven (WHEN)**: Triggered by external/system events.
2. **State-Driven (WHILE)**: Active during continuous states.
3. **Optional Feature (WHERE)**: Active when feature or configuration is enabled.
4. **Unwanted Behavior (IF)**: Handles error conditions, recovery, and fallback.
5. **Ubiquitous (THE-SHALL)**: Universal system invariants.

While single-system requirements can be expressed in linear tabular format, complex enterprise systems feature multi-system requirement topologies with inter-requirement dependency DAGs, conflicting pre-conditions, and strict BDD-readiness criteria. This standard provides an engine-agnostic, declarative execution workflow for validating and ratifying requirement graphs.

---

## 2. Primitive Mapping: EARS to CNCF Serverless Workflow

The table below defines the formal mapping of EARS requirements analysis primitives to CNCF Serverless Workflow states:

| EARS Requirement Primitive | CNCF State Type | Purpose & Operational Semantics |
|---|---|---|
| **Requirements Ingestion** | `operation` / `inject` | Parses raw requirement text, extracts metadata, and maps upstream PRD references (`@prd:`). |
| **Syntax Pattern Verification** | `operation` | Validates compliance with the 5 EARS patterns, verifies the actor response clause (`THE [component] SHALL`), and checks timing quantifiers (`WITHIN`). |
| **Dependency DAG Resolution** | `parallel` | Evaluates requirement clusters concurrently and validates that `@depends:` forms an acyclic directed graph (DAG). |
| **Conflict & Consistency Check** | `operation` | Checks for mutually exclusive states, overlapping triggers, or contradictory behavioral requirements across components. |
| **BDD-Readiness Evaluation** | `switch` | Evaluates BDD-readiness via Binary Topological Validation (BTV PASS per CHG-97 across structural validity, trace satisfaction, and zero conflicts) and routes to ratification, clarification, or rejection. |
| **Stakeholder Clarification** | `callback` | Emits a clarification request to PRD authors and pauses execution until a correlated `RequirementClarificationEvent` is received (with timeout). |
| **Contract Ratification** | `operation` | Generates canonical SHA-256 hash IDs (`EARS.{doc_id}.{section_id}.{hash}`) and emits the ratified requirement set to downstream BDD. |
| **Requirement Invalidation Saga** | `operation` (`usedForCompensation: true`) | Compensating transaction triggered when requirements are rejected, invalidating downstream draft artifacts and alerting stakeholders. |

---

## 3. Two-Graph & Dual-Template Architecture Selection Matrix

Layer 03 employs the framework's **Two-Graph Dual-Plane Architecture**, pairing an executable process workflow with an atomic content graph to generate and ratify functional requirements:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 03 EARS TWO-GRAPH ARCHITECTURE                               │
├────────────────────────────────────────────────────────┬────────────────────────────────────┤
│          GRAPH 1: PROCESS DAG (CONTROL PLANE)          │   GRAPH 2: CONTENT GRAPH (DATA)    │
│       EARS-SWF-TEMPLATE.yaml (Hybrid Envelope)         │      (EARS-GRAPH-TEMPLATE.yaml)    │
├────────────────────────────────────────────────────────┼────────────────────────────────────┤
│ • CNCF Serverless Workflow v0.8 state machine DAG      │ • SDD-GRAPH v2.0 Property Graph    │
│ • Flow of HOW to parse, validate & ratify requirements │ • Content of WHAT requirements exist│
│ • Syntax verification & parallel DAG dependency checks │ • Atomic EARS requirement statements│
│ • Automated BDD-Readiness scoring gate (BTV PASS)      │ • Upstream PRD & downstream BDD links│
│ • Stakeholder clarification callbacks                  │ • Relational links (realizes, etc) │
│ • Rejection invalidation saga (compensatedBy)          │ • Validated via BTV engine         │
└───────────────────────────┬────────────────────────────┴─────────────────┬──────────────────┘
                            │                                              │
                            ▼                                              ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │               DOCUMENT GENERATION & PROJECTION               │
                    ├──────────────────────────────────────────────────────────────┤
                    │ • Process DAG orchestrates requirements validation & gating  │
                    │ • Agent actions populate and mutate atomic nodes in Data     │
                    │ • BTV verifies topological closure & DAG acyclicity          │
                    │ • Observability Adapter projects graph into EARS-TEMPLATE.yaml│
                    └──────────────────────────────────────────────────────────────┘
```

### Dual-Template Selection Rules:
Authors and autonomous AI agents select the template matching the structural complexity of the requirements:
1. **Use Two-Graph Generation (`EARS-SWF-TEMPLATE.yaml` [Hybrid Envelope Subtype] + `EARS-GRAPH-TEMPLATE.yaml` [Property Graph])** when requirements span multiple subsystems, declare inter-requirement prerequisites (`@depends:`), require automated DAG acyclicity checks, or feed automated BDD generation pipelines. The Process DAG guides validation, populates the Content Graph, executes BTV verification, and projects the final EARS specification.
2. **Use Companion Declarative (`EARS-TEMPLATE.yaml`)** directly when requirements represent a single component or linear feature set with isolated, independent behaviors without branching or automated compensations.

---

## 4. Graph Integrity Invariants

All EARS workflow definitions (whether embedded in `EARS-SWF-TEMPLATE.yaml` or standalone under `framework/governance/workflows/`) MUST satisfy five structural invariants:

### Invariant E-WF01: Directed Acyclic Graph (DAG) Integrity
- Inter-requirement dependencies declared via `@depends:` MUST form a directed acyclic graph.
- Circular dependencies (`EARS.01 -> EARS.02 -> EARS.01`) are strictly forbidden and MUST fail the dependency resolution state.

### Invariant E-WF02: Actor Clause Mandate
- Every requirement pattern statement MUST contain the canonical EARS actor response clause: `THE [system/component] SHALL [response action]`.
- Connectives such as `THEN` or passive phrases (`"it should"`, `"must be done"`) are non-conformant.

### Invariant E-WF03: Quantifiable Timing & Bounds
- Every latency-sensitive requirement MUST quantify response time using percentile bounds (`p50`, `p95`, `p99`) via the `WITHIN` clause.
- Non-latency bounds (e.g. retry counts, batch sizes, cache cycles) MUST specify explicit numeric values and units (e.g., `WITHIN 3 cycles`, `@threshold: ADR.01.retry.count`).
- Subjective adjectives (`"real-time"`, `"immediately"`, `"fast"`, `"robust"`) are strictly forbidden.

### Invariant E-WF04: Upstream Traceability Parity
- Every requirement statement MUST map to at least one valid upstream PRD functional requirement ID (`@prd: PRD.NN.09.xxxx`).
- Unanchored requirements with missing or broken PRD links MUST be flagged during the BDD-readiness gate.

### Invariant E-WF05: Rejection Invalidation Compensation
- Any state machine evaluating requirement validity MUST bind rejection states to an automated compensation action (`compensatedBy: InvalidateDownstreamArtifacts`).
- The compensation action MUST flag or revoke any provisional downstream BDD, ADR, or SPEC artifacts derived from the rejected requirements.

### Invariant E-WF06: Technology Selection Criteria Feed
- Quality attributes, SLA bounds, and throughput constraints quantified in Section 4 (`quality_attributes`) must be formulated to feed directly as evaluation criteria and weighting parameters into Layer 05 ADR multi-criteria decision analysis (MCDA) across approved platform technology candidates ([`TECHNOLOGY_STACK_USAGE_GUIDE.md`](../../governance/TECHNOLOGY_STACK_USAGE_GUIDE.md)).

---

## 5. Zero-Runtime LangGraph Execution Model

In strict accordance with **Principle D-0013 (Spec Engine-Agnostic Purity)**, `framework/` ships pure declarative specifications without bundling Python runtime packages, workflow interpreters, or vendor SDKs.

### Agentic Execution Mapping
When an autonomous AI agent or execution harness executes an EARS workflow via LangGraph:
1. **Workflow Ingestion**: The agent parses `ears-requirements-validation.sw.yaml` into state nodes.
2. **State Translation**:
   - `operation` states map to deterministic LLM/tool execution nodes (e.g., regex pattern parsers, AST linters).
   - `parallel` states execute independent requirement branch analyses concurrently using async tasks.
   - `switch` states evaluate JSONPath/CEL expressions against accumulated requirement metadata.
   - `callback` states pause the LangGraph thread using checkpointers (`MemorySaver` / database saver) until stakeholder events are posted.
   - `compensatedBy` states execute rollback handlers when execution paths terminate in rejection.
3. **Dual-Graph Pipeline Coordination**:
   - **Step 1 (Process DAG Orchestration)**: LangGraph drives the authoring agent through the requirement validation workflow.
   - **Step 2 (Content Graph Mutation)**: As operations complete, the agent instantiates and updates nodes (`requirement`, `quality_attribute`, `timing_bound`) and edges (`realizes`, `verifies`, `depends_on`) in `EARS-GRAPH-TEMPLATE.yaml`.
   - **Step 3 (Binary Topological Validation - BTV)**: The state machine executes BTV asserting DAG acyclicity, upstream PRD closure, and zero requirement conflicts.
   - **Step 4 (Document Generation / Read Projection)**: The Observability Adapter compiles the validated property graph into the canonical human-readable document (`EARS-TEMPLATE.yaml` structure).

---

## 6. Closed Dual-Flow Quality Loop: Authoring & Review Saga Binding (CHG-111, GD-98)

To eliminate the decoupling between artifact authoring and review crew evaluation, Layer 03 adheres to the closed dual-flow loop:

1. **Explicit Author Rubric Binding**:
   - The document envelope `metadata:` block declares `author_persona: "requirements_specialist"` and `author_playbook: "framework/playbooks/03_EARS/requirements_specialist.md"`.
   - Autonomous drafting agents derive their authoring constraints and EARS syntactic structures directly from this rubric prior to drafting.

2. **Mandatory Review Saga Invalidation & Gating**:
   - Prior to final ratification (`RatifyEarsRequirements`), the authoring workflow executes `InvokeReviewSagaGate` via the `invokeReviewSaga` custom function, invoking the designated review saga subflow (`ears-review-remediation-flow`).
   - The review saga coordinates multi-agent review crew evaluation across persona playbooks, enforcing the quality gate condition:
     `${ .review_score >= 90 and .blocking_findings == 0 and .gate_passed == true }`.
   - If findings or defects are uncovered, the saga executes an automated remediation loop, halting ratification until all P0/P1 blockers are resolved.

---

## 7. 5-Step Closed Layer Lifecycle and CloudEvent Handoff (CHG-112, GD-99)

Layer 03 EARS implements the standardized 5-step closed lifecycle:
1. **Stage 1 (Authoring)**: Requirements specialist authors syntax-constrained EARS statements, system event triggers, and response boundaries.
2. **Stage 2 (Review & Remediation)**: Review saga executes multi-persona review. Unresolved blockers trigger author remediation (`RemediateLayerDraft`, author: `requirements_specialist`) before re-entering `InvokeReviewSagaGate` (Circuit Breaker CB-1: max 2 remediation passes / 3 review cycles).
3. **Stage 3 (Layer Boundary Gate Verification)**: `VerifyLayerCloseoutGate` verifies `GATE-03` exit criteria (`GATE-03_EARS_BDD_ADR.md`).
4. **Stage 4 (Baseline Sealing & SDD Graph Lineage)**: `SealLayerDocumentBaseline` seals frontmatter status to `Baselined` with SHA-256 checksum; `RegisterSddGraphBaselineNode` registers `EarsNode` in SDD graph and locks incoming edges.
5. **Stage 5 (Downstream Handoff CloudEvent Emission)**: `EmitLayerHandoffEvent` publishes `EarsClosedAndBaselinedEvent` (`org.aidoc.sdd.layer03.ears.closed`) with payload `requirements_count`, `graph_node_ref`, `ears_checksum`, authorizing downstream Layer 04 (BDD) and Layer 05 (ADR) execution.
