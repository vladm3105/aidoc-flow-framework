# EARS Workflow Standard — Layer 03

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.84.0 |
| Authority | Decision GD-59 (framework/governance/DECISIONS.md) |

---

## 1. Overview & Architectural Scope

This specification establishes the **normative standard** for modeling Layer 03 (EARS — Easy Approach to Requirements Syntax) requirements analysis, dependency resolution, cross-requirement conflict detection, BDD-readiness gating, and invalidation compensation sagas using the **CNCF Serverless Workflow DSL v0.8 (YAML)** (`specVersion: "0.8"`).

In the 10-layer SDD framework:
```text
BRD (01) → PRD (02) → EARS (03) → BDD (04) → ADR (05) → SPEC (06) → TDD (07) → IPLAN (08) → Code (09) → EVAL (10)
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
| **BDD-Readiness Evaluation** | `switch` | Evaluates BDD-ready score (threshold >=90/100 across clarity, testability, quality attributes, and strategic alignment) and routes to ratification, clarification, or rejection. |
| **Stakeholder Clarification** | `callback` | Emits a clarification request to PRD authors and pauses execution until a correlated `RequirementClarificationEvent` is received (with timeout). |
| **Contract Ratification** | `operation` | Generates canonical SHA-256 hash IDs (`EARS.{doc_id}.{section_id}.{hash}`) and emits the ratified requirement set to downstream BDD. |
| **Requirement Invalidation Saga** | `operation` (`usedForCompensation: true`) | Compensating transaction triggered when requirements are rejected, invalidating downstream draft artifacts and alerting stakeholders. |

---

## 3. Dual-Template Architecture & Selection Matrix

Layer 03 provides two canonical authoring templates. Authors and autonomous AI agents MUST select the template matching the structural complexity of the requirements:

```text
                              ┌───────────────────────────────────┐
                              │  Are requirements multi-system,   │
                              │  feature inter-dependent DAGs,    │
                              │  or require automated BDD gating? │
                              └─────────────────┬─────────────────┘
                                                │
                                ┌───────────────┴───────────────┐
                                │                               │
                                ▼ YES                           ▼ NO
                ┌──────────────────────────────┐ ┌──────────────────────────────┐
                │   EARS-SWF-TEMPLATE.yaml     │ │      EARS-TEMPLATE.yaml      │
                │   (Hybrid Envelope Subtype)  │ │      (Standard Declarative)  │
                │                              │ │                              │
                │  - Embedded CNCF v0.8 Graph  │ │  - Declarative YAML tables   │
                │  - Parallel DAG Resolution   │ │  - Atomic EARS statements    │
                │  - BDD-Ready Scoring Gate    │ │  - Standard single-system    │
                │  - Invalidation Compensation │ │    requirements              │
                └──────────────────────────────┘ └──────────────────────────────┘
```

### Selection Rules:
1. **Use `EARS-TEMPLATE.yaml`** when requirements represent a single component or linear feature set with isolated, independent behaviors.
2. **Use `EARS-SWF-TEMPLATE.yaml`** when requirements span multiple subsystems, declare inter-requirement prerequisites (`@depends:`), require automated DAG acyclicity checks, or feed automated BDD generation pipelines.

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
