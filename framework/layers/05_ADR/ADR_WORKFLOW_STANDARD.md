# ADR Workflow Specification Standard: CNCF Serverless Workflow for Layer 05

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.88.2 |

Establishes the normative standard for modeling, specifying, and orchestrating Layer 05 (Architecture Decision Records / ADR) architectural trade-off evaluations, multi-criteria decision analysis (MCDA), stakeholder RFC review callbacks, and decision ratification using the CNCF Serverless Workflow v0.8 specification in YAML format within the SDD Hybrid Envelope Architecture.

---

## 1. Purpose & Architectural Context

In the 10-layer SDD specification, Layer 05 (ADR) serves as the architectural decision bridge between container-level product requirements (Layer 02 PRD, Layer 03 EARS, Layer 04 BDD) and component-level technical specifications (Layer 06 SPEC). ADR records evaluate competing candidate architectures, technology stacks, and structural designs to establish the foundational technical contracts for the system.

Historically, ADR documents were authored exclusively as static YAML contracts in [`ADR-TEMPLATE.yaml`](./ADR-TEMPLATE.yaml). While effective for straightforward decisions, static documentation encounters severe challenges in complex, distributed systems:

1. **Lack of Executable Multi-Criteria Decision Analysis (MCDA)**: Complex architectural choices involve competing quality attributes (e.g., latency vs. cost, consistency vs. availability). Static tables cannot formally execute or verify weighted utility scoring across candidate architectures.
2. **Missing Stakeholder Review Callbacks & RFC Loops**: Architecture decisions require consensus across diverse personas (architect, security, tech lead, operator). Without machine-readable event callbacks, the RFC collection cycle remains ad-hoc and unverified.
3. **Absence of Systematic Rejection Archival & Compensation**: When a proposed architecture fails viability thresholds or stakeholder consensus, the reasons and discarded candidate evaluations must be archived deterministically without contaminating active system models.
4. **Agent Decision Drift in Autonomous SDD Lifecycles**: Autonomous AI coding agents evaluating architecture choices often skip alternative analysis, fail to compute quantitative trade-off metrics, or declare decisions without structured review gates.
5. **Canonical Governance Runner**: The framework provides `framework/governance/workflows/adr-decision-analysis.sw.yaml` as the canonical CNCF Serverless Workflow state machine for executing multi-candidate trade-off analysis, MCDA utility scoring, and stakeholder RFC review loops.

---

## 2. Hybrid Envelope Architecture

To maintain complete backward compatibility with structural linters (`STRUCT01`, `TAG01`, and `sdd_doc_lint`), all CNCF-compliant ADR documents adopt the **Hybrid Envelope Architecture**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Layer 05 ADR Document Envelope (ADR-SWF-TEMPLATE.yaml)                │
├────────────────────────────────────────────────────────────────────────┤
│  • doc_id, metadata (schema_version: "1.0", layer: 5, c4_level: none)  │
│  • document_control (subtype: workflow, status: Proposed|Accepted)     │
│  • context (problem_statement, business_driver, key_constraints)       │
│  • decision (chosen_solution, key_components, implementation_approach) │
│  • alternatives (considered candidate options, seed citations)         │
│  • consequences (positive_outcomes, tradeoffs_and_risks, cost_estimate)│
├────────────────────────────────────────────────────────────────────────┤
│  architecture_flow:                                                    │
│   ├── decision_sequence (@diagram: sequence-sync, sequenceDiagram)     │
│   └── decision_workflow: (CNCF Serverless Workflow v0.8 YAML)          │
│       ├── id, name, version, specVersion: "0.8"                        │
│       ├── events: [StakeholderFeedbackEvent, RFCPublishedEvent]        │
│       ├── start: IngestDecisionContext                                 │
│       └── states:                                                      │
│           ├── [Ingest]       operation (ingest drivers & constraints)  │
│           ├── [Candidates]   parallel (evaluate candidate options)     │
│           ├── [MCDA Scoring] operation (compute weighted utility matrix)│
│           ├── [Viability]    switch (validate threshold compliance)    │
│           ├── [RFC Callback] callback (await stakeholder consensus)    │
│           ├── [Ratify]       operation (seal accepted ADR element IDs) │
│           └── [Compensate]   operation (archive rejected proposal)     │
├────────────────────────────────────────────────────────────────────────┤
│  • implementation_assessment (mvp_phases, rollback_plan, monitoring)  │
│  • verification (success_criteria, bdd_scenario_refs)                  │
│  • traceability (@adr, @bdd, @ears, @spec downstream expectation)      │
│  • related_decisions (dependencies, supersedes)                        │
│  • glossary (project-specific architectural terms)                      │
│  • appendix (MVP lifecycle rules)                                      │
└────────────────────────────────────────────────────────────────────────┘
```

The outer envelope preserves all 12 required sections asserted by `tests/conformance/test_required_section_sets.py`, while `architecture_flow.decision_workflow` houses the executable CNCF Serverless Workflow state machine.

---

## 3. Architecture Decision Mapping to CNCF State Machine Primitives

The core phases of architectural decision analysis map directly onto CNCF Serverless Workflow state primitives:

| ADR Phase | Purpose | CNCF State Type | Workflow Semantic Construct |
|---|---|---|---|
| **Context & Driver Ingestion** | Load constraints, timing SLAs, and requirements | `inject` or `operation` | Initializes candidate evaluation context from upstream `@ears` and `@bdd` |
| **Candidate Evaluation** | Evaluate candidate options against quality attributes | `parallel` | Concurrent evaluation across Candidate A, B, and C with `completionType: allOf` |
| **MCDA Utility Scoring** | Compute weighted multi-criteria scores | `operation` | Executes quantitative matrix calculation (Pugh matrix / utility tree) |
| **Viability Threshold Check** | Filter out non-viable or vetoed candidates | `switch` | Verifies candidate score $\ge$ threshold and veto count $== 0$ |
| **Stakeholder RFC Review** | Solicit feedback from review crew | `callback` | Emits RFC event and suspends awaiting correlated `StakeholderFeedbackEvent` |
| **Feedback Consensus Check** | Evaluate review approval signals | `switch` | Evaluates whether feedback status is `APPROVED` with zero blocking objections |
| **Decision Ratification** | Seal decision with immutable IDs | `operation` | Generates canonical ADR IDs (`ADR.NN.03.xxxx`) and marks status `Accepted` |
| **Rejection Archival & Cleanup** | Record rejected options and purge context | `operation` (`compensatedBy`) | Archives proposal as rejected and invokes compensating context cleanup |

---

## 4. Multi-Criteria Decision Analysis (MCDA) Scoring

In workflow-driven ADR evaluations, candidate alternatives must be scored quantitatively using a weighted Multi-Criteria Decision Analysis (MCDA) function before a selection is ratified:

$$\text{Utility}(C_i) = \sum_{k=1}^M w_k \cdot S(C_i, Q_k)$$

Where:
- $C_i$ is candidate alternative $i$.
- $Q_k$ is quality attribute $k$ (e.g., latency, throughput, cost, security, resilience).
- $w_k$ is the normalized weight of quality attribute $k$ ($\sum w_k = 1.0$).
- $S(C_i, Q_k)$ is the normalized score of candidate $i$ on attribute $k$ ($0.0 \le S \le 100.0$).

The `switch` condition enforces strict threshold gating:

```yaml
- name: EvaluateDecisionViability
  type: switch
  dataConditions:
    - name: ViableCandidateSelected
      condition: "${ .selected_candidate.utility_score >= 80.0 and .selected_candidate.veto_count == 0 }"
      transition: SolicitStakeholderRFC
  defaultCondition:
    transition: RejectAndArchiveProposal
```

---

## 5. Stakeholder RFC Review Loops & Callback Correlation

When a viable candidate is identified, the state machine enters a `callback` state, dispatching a Request-for-Comment (RFC) to human architects, tech leads, or review subagents. Execution suspends until a correlated CloudEvent is received:

```yaml
- name: SolicitStakeholderRFC
  type: callback
  action:
    name: PublishProposalRFC
    functionRef:
      refName: publishDecisionRFC
      arguments:
        proposalId: "${ .adr_id }"
        selected_candidate: "${ .selected_candidate }"
  eventRef: StakeholderFeedbackEvent
  timeouts:
    eventTimeout: "PT48H"
  transition: EvaluateStakeholderFeedback
```

Correlation is established via the `proposalId` CloudEvents attribute, ensuring that multi-party review feedback maps deterministically to the active decision record.

---

## 6. Rejection Compensation & Archival Sagas

When a proposed architecture decision is rejected—either due to failing quantitative viability thresholds or receiving blocking stakeholder objections—the state machine transitions to a rejected terminal state and triggers saga rollback compensation:

```yaml
- name: RejectAndArchiveProposal
  type: operation
  compensatedBy: ArchiveRejectedDecision
  actions:
    - name: RecordProposalRejection
      functionRef:
        refName: archiveRejectedProposal
        arguments:
          adr_id: "${ .adr_id }"
          status: "Rejected"
  end: true

- name: ArchiveRejectedDecision
  type: operation
  usedForCompensation: true
  actions:
    - name: PurgeTemporaryContext
      functionRef:
        refName: cleanupEvaluationContext
        arguments:
          adr_id: "${ .adr_id }"
          archive_mode: "PERMANENT_RECORD"
```

This guarantees that discarded alternatives are permanently recorded in the ADR's `alternatives.considered` history without leaving dangling reservations or unsealed artifacts in downstream layers.

---

## 7. Dual-Template Selection Rules

Authors must select between the static template and the workflow template according to the following decision matrix:

| Architectural Criteria | Use `ADR-TEMPLATE.yaml` | Use `ADR-SWF-TEMPLATE.yaml` |
|---|---|---|
| **Candidate Count** | Single obvious candidate or minor library choice | $\ge 2$ competing candidate options requiring formal trade-offs |
| **Trade-off Complexity** | Qualitative pros/cons sufficient | Quantitative MCDA / utility tree scoring required |
| **Review Scope** | Local author or single tech lead sign-off | Formal RFC review crew with asynchronous callback events |
| **Blast Radius** | In-process, isolated component | Distributed microservices, shared databases, or cross-cutting security |
| **Reversibility** | Easily reversible with trivial cost | High switching cost requiring formal rollback and compensation plans |

---

## 8. Graph Invariants for Layer 05 ADR Workflows

All CNCF Serverless Workflow state machines authored for Layer 05 ADR must satisfy 5 structural invariants:

1. **INV-ADR-01 (Single Entrypoint)**: The workflow must declare a unique `start` state initiating context ingestion.
2. **INV-ADR-02 (Deterministic Alternative Fan-out)**: If $\ge 2$ candidates are considered, candidate assessment must execute via a `parallel` state evaluating all candidates under identical quality attribute constraints.
3. **INV-ADR-03 (Quantitative Viability Gate)**: Selection of a candidate must pass through a `switch` state validating score thresholds before advancing to RFC review.
4. **INV-ADR-04 (Correlated RFC Callback)**: The RFC feedback loop must declare a `callback` state correlated on `proposalId` with an explicit ISO 8601 timeout.
5. **INV-ADR-05 (Rejection Compensation Binding)**: Every rejection path must declare a compensating state via `compensatedBy` that cleanly archives evaluation records and purges temporary contexts.

---

## 9. Engine-Agnostic Translation & Zero-Runtime Integration

Per Decision **D-0013**, the framework specification ships pure, vendor-neutral CNCF YAML workflows with **zero bundled runtime code**. Downstream execution engines (such as LangGraph, Temporal, or AWS Step Functions) ingest these declarative definitions via direct mapping:

```python
# Conceptual translation of ADR workflow to LangGraph
from langgraph.graph import StateGraph, START, END

builder = StateGraph(ADRState)
builder.add_node("IngestDecisionContext", ingest_context)
builder.add_node("EvaluateCandidatesConcurrently", evaluate_candidates_parallel)
builder.add_node("ComputeUtilityScores", compute_mcda)
builder.add_node("SolicitStakeholderRFC", await_rfc_feedback)
builder.add_node("RatifyArchitectureDecision", seal_adr)
builder.add_node("RejectAndArchiveProposal", archive_rejection)

builder.add_edge(START, "IngestDecisionContext")
builder.add_edge("IngestDecisionContext", "EvaluateCandidatesConcurrently")
builder.add_edge("EvaluateCandidatesConcurrently", "ComputeUtilityScores")
builder.add_conditional_edges(
    "ComputeUtilityScores",
    check_viability,
    {"viable": "SolicitStakeholderRFC", "rejected": "RejectAndArchiveProposal"}
)
builder.add_conditional_edges(
    "SolicitStakeholderRFC",
    check_rfc_consensus,
    {"approved": "RatifyArchitectureDecision", "rejected": "RejectAndArchiveProposal"}
)
builder.add_edge("RatifyArchitectureDecision", END)
builder.add_edge("RejectAndArchiveProposal", END)
```
