# Specification-Driven Development Guide

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.96.17 |


## Overview

SDD is a streamlined 10-layer documentation-to-code framework. Each layer produces one YAML document type, with end-to-end traceability from business requirements to execution planning. The layer order follows a logical dependency flow: specify what to build first (SPEC), then define how to test it (TDD), then plan the execution (IPLAN).

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
                                                                                           ↑
                                                                             CHG (L9, overlay) → EVAL (L10)
```

## Layer Descriptions

| Layer | Artifact | Purpose | Upstream | Downstream |
|-------|----------|---------|----------|------------|
| L1 | BRD | Business requirements, objectives, scope | — | PRD |
| L2 | PRD | Product features, user stories, ADR topics | BRD | EARS |
| L3 | EARS | Formal requirements (WHEN-THE-SHALL-WITHIN) | PRD | BDD |
| L4 | BDD | Executable acceptance scenarios (Given-When-Then) with spec_trace | EARS | ADR |
| L5 | ADR | Architecture & technology selection gate (Context-Decision-Consequences) | EARS, BDD | SPEC |
| L6 | SPEC | Component interfaces, data models, behavior contracts | EARS, BDD, ADR | TDD |
| L7 | TDD | Test case definitions, BDD-to-test mapping, quality thresholds | EARS, BDD, ADR, SPEC | IPLAN |
| L8 | IPLAN | Execution plan: file manifest, bash commands, session handoff | SPEC, TDD | Code |
| L9 | CHG | Change management overlay — gates, versioning, audit trail | Any | — |
| L10 | EVAL | Evaluation & QA governance — test strategy, coverage matrices | EARS, BDD, TDD, IPLAN | CI/CD |

> **Technology Selection Gate ([`governance/TECHNOLOGY_STACK_USAGE_GUIDE.md`](governance/TECHNOLOGY_STACK_USAGE_GUIDE.md)):**  
> SDD enforces clean architectural separation: Layers 01–04 (**Problem Space**) remain technology-agnostic. Layer 05 (**ADR**) serves as the formal selection gate, evaluating options from `vladm3105/technology-stack` against EARS timing constraints and BDD failure scenarios via Multi-Criteria Decision Analysis (MCDA). Layers 06–10 (**Solution Space**) author concrete technology contracts, testcontainers, and implementations.

The forward chain above is the **SDD2C greenfield** (F1) flow. Subsequent changes do not all repeat it: behavior changes
restart the chain from the lowest affected layer (**SEED2C** brownfield / F3, SDD-first), defects in completed work repair
through the scoped bugfix vehicle (**CODE2C** / F4, parent immutable), backward reconciliation maps existing code (**CODE2S** / Type-R),
emergency production fixes route via **HOTFIX** (Emergency), and small direct requests skip the SDD cascade
(**DIR2C** / F2). Which flow a change takes is routed by
[`governance/CHG_REQUEST_FLOWS.md`](governance/CHG_REQUEST_FLOWS.md) (ratified 0.57.0, CHG-06).

## Necessary-upstream traceability

Each layer cites only its **necessary upstream** (`required_tags` in
`LAYER_REGISTRY.yaml`), not the cumulative closure of every upstream layer.
Deeper lineage is transitive (one hop per layer, or a trace-walk query over the
`@`-tag graph — no such script ships in this repo; the traversal is the
normative capability, outside the spec):

```
BRD:   —
PRD:   @brd
EARS:  @prd
BDD:   @ears  # structured ears: list per scenario — emits no @-tag (04_BDD exception)
ADR:   @ears @bdd
SPEC:  @ears @bdd @adr
TDD:   @ears @bdd @adr @spec
IPLAN: @spec @tdd
EVAL:  @ears @bdd @tdd @iplan
```

`required_tags` is the minimum trace-resolution set; a layer MAY carry extra
provenance tags (e.g. a platform ADR's `@brd`/`@prd`) but is not required to.

## Layer Gate Flow: Binary Topological Validation (BTV)

Per CHG-97, layer gates evaluate deterministically via Binary Topological Validation (BTV) rather than legacy numeric score thresholds (>=90/100). Each layer must achieve deterministic BTV PASS (structural completeness, upstream trace satisfaction, DAG validity) before transitioning to the downstream layer:

```
BRD → PRD-Ready (BTV PASS) → PRD → EARS-Ready (BTV PASS) → EARS → BDD-Ready (BTV PASS)
→ BDD → ADR-Ready (BTV PASS) → ADR → SPEC-Ready (BTV PASS) → SPEC → TDD-Ready (BTV PASS)
→ TDD → IPLAN-Ready (BTV PASS) → IPLAN → EXEC-Ready (BTV PASS) → Code
```

## Three-Tier Architecture & Dual-Template Selection Matrix (Tier 1 SWF, Tier 2 GRAPH, Tier 3 MD, and Declarative Alternative)

To support both lightweight specification drafting and complex autonomous agent orchestration, SDD implements the **Three-Tier Layer Architecture** alongside the dual-template selection matrix across all layers (ratified across Decisions GD-51 through GD-61, and GD-99 through GD-113):

1. **Tier 1: Declarative Execution Flow (`*-SWF-TEMPLATE.yaml`)**:
   - Implements the **Hybrid Envelope Architecture** (`subtype: workflow`), preserving full structural schema compliance (`STRUCT01-10`) with `sdd_doc_lint` while housing an embedded, vendor-neutral **CNCF Serverless Workflow v0.8 YAML** state machine (`workflow_definition`).
   - Drives the **5-step closed layer lifecycle**:
     - **Stage 1: Authoring** — Playbook-guided drafting of requirements, contracts, or architecture.
     - **Stage 2: Multi-Persona Review Saga & Remediation** — Adversarial review loop with in-situ author remediation (`RemediateLayerDraft`) before escalation.
     - **Stage 3: Boundary Gate Verification** — Deterministic validation enforcing layer gates (`VerifyLayerCloseoutGate`).
     - **Stage 4: Document Baseline Sealing** — Freezing the document baseline (`SealLayerDocumentBaseline`) and registering the SDD graph node (`RegisterSddGraphBaselineNode`).
     - **Stage 5: Event-Driven Handoff** — Emitting trace-contextualized CloudEvents (`EmitLayerHandoffEvent` / `produceEvents`) to trigger downstream lifecycle workflows.
   - Normative mapping rules for each layer are documented in `layers/0X_TYPE/TYPE_WORKFLOW_STANDARD.md` and `governance/GOVERNANCE_WORKFLOW_STANDARD.md`.

2. **Tier 2: Canonical Data Plane Property Graph (`*-GRAPH-TEMPLATE.yaml`)**:
   - Represents the layer's formal knowledge graph in **SDD-GRAPH v2.0** format.
   - Provides strongly-typed typed entities (nodes) and explicit relational dependencies (edges) for sub-millisecond graph slicing, blast-radius queries via Kùzu/openCypher, and deterministic DAG validation (`BTV PASS`).

3. **Tier 3: Compiled Presentation Projection (`*.md`)**:
   - Clean, human-readable GitHub-Flavored Markdown projection compiled from Tier 1 and Tier 2 definitions for human review, PR summaries, and documentation publication.

4. **Standard Declarative Alternative (`*-TEMPLATE.yaml`)**:
   - Purely declarative YAML defining requirements, acceptance scenarios, architecture decisions, interfaces, test suites, or execution plans.
   - Recommended for straightforward, linear, or atomic development tasks where workflow orchestration is unnecessary.

## Layer Responsibilities

| Area | Owner | Implementation Rule |
|-----|-------------|---------------------|
| Business intent & problem space | BRD (L1) | Business rationale, market problem, success metrics, constraints |
| Product requirements & user stories | PRD (L2) | Features, user personas, functional scope, acceptance boundaries |
| Requirement formalization | EARS (L3) + BDD (L4) | Formal clauses + executable scenarios with `spec_trace` |
| Architecture decisions | ADR (L5) | Context-Decision-Consequences with downstream SPEC readiness |
| Interface and behavior contracts | SPEC (L6) | Component-level interfaces, data models, behavior contracts |
| Test definitions | TDD (L7) | Embedded test cases, thresholds, and BDD mapping |
| Execution planning | IPLAN (L8) | File manifest, commands, session handoff |
| Governance workflow | CHG overlay (L9) | Project-level control outside the sequential lifecycle (operational namespace 09) |
| Evaluation & verification | EVAL (L10) | Evaluation reports, QA governance, acceptance validation, coverage matrices |

## Development vs Deployment Separation

SDD enforces a strict boundary between development and deployment concerns. Development plans (IPLAN L8) produce artifacts. Deployment plans consume and apply them.

| Concern | Plan Type | Owns | Done When |
|---------|-----------|------|-----------|
| **Development** | IPLAN (L8) | Source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything authored, committed, shipped via `git push` | Code + IaC + scripts authored, committed, green; tests pass |
| **Deployment** | Separate deployment plan | Operator execution: `terraform apply`, `atlas migrate apply`, image build + deploy, environment activation, acceptance/soak runs | Artifacts applied to target environment; acceptance gates green |

**Rule.** An IPLAN flips to `Completed` once source code + Terraform modules + CI/CD scripts are authored, committed, and green. It does NOT wait for deployment. A deployment-stuck IPLAN (e.g., "ready for `terraform apply`") is still complete from the development side.

**Cross-plan handoff.** When closing a development IPLAN whose artifacts depend on a deployment step, register the obligation in `IPLAN-00_index.yaml` §deferred_items before flipping status. The IPLAN status reflects authoring-completion; the registry entry tracks the deploy-side handoff.
