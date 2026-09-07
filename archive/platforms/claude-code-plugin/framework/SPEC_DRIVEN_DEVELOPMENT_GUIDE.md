# Specification-Driven Development Guide

## Overview

SDD is a streamlined 8-layer documentation-to-code framework. Each layer produces one YAML document type, with end-to-end traceability from business requirements to execution planning. The layer order follows a logical dependency flow: specify what to build first (SPEC), then define how to test it (TDD), then plan the execution (IPLAN).

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

## Layer Descriptions

| Layer | Artifact | Purpose | Upstream | Downstream |
|-------|----------|---------|----------|------------|
| L1 | BRD | Business requirements, objectives, scope | — | PRD |
| L2 | PRD | Product features, user stories, ADR topics | BRD | EARS |
| L3 | EARS | Formal requirements (WHEN-THE-SHALL-WITHIN) | PRD | BDD |
| L4 | BDD | Executable acceptance scenarios (Given-When-Then) with spec_trace | EARS | ADR |
| L5 | ADR | Architecture decisions (Context-Decision-Consequences) | EARS, BDD | SPEC |
| L6 | SPEC | Component interfaces, data models, behavior contracts | EARS, BDD, ADR | TDD |
| L7 | TDD | Test case definitions, BDD-to-test mapping, quality thresholds | EARS, BDD, ADR, SPEC | IPLAN |
| L8 | IPLAN | Execution plan: file manifest, bash commands, session handoff | SPEC, TDD | Code |

## Necessary-upstream traceability

Each layer cites only its **necessary upstream** (`required_tags` in
`LAYER_REGISTRY.yaml`), not the cumulative closure of every upstream layer.
Deeper lineage is transitive (one hop per layer, or a trace-walk query — the
reference implementation ships `tools/trace_walk.py`, outside the spec):

```
BRD:   —
PRD:   @brd
EARS:  @prd
BDD:   @ears
ADR:   @ears @bdd
SPEC:  @ears @bdd @adr
TDD:   @ears @bdd @adr @spec
IPLAN: @spec @tdd
```

`required_tags` is the minimum trace-resolution set; a layer MAY carry extra
provenance tags (e.g. a platform ADR's `@brd`/`@prd`) but is not required to.

## Readiness Score Flow

Each layer must achieve >=90/100 readiness score before generating the next layer:

```
BRD → PRD-Ready (>=90) → PRD → EARS-Ready (>=90) → EARS → BDD-Ready (>=90)
→ BDD → ADR-Ready (>=90) → ADR → SPEC-Ready (>=90) → SPEC → TDD-Ready (>=90)
→ TDD → IPLAN-Ready (>=90) → IPLAN → EXEC-Ready (>=90) → Code
```

## Layer Responsibilities

| Area | Owner | Implementation Rule |
|-----|-------------|---------------------|
| Architecture decisions | ADR (L5) | Context-Decision-Consequences with downstream SPEC readiness |
| Requirement formalization | EARS (L3) + BDD (L4) | Formal clauses + executable scenarios with `spec_trace` |
| Interface and behavior contracts | SPEC (L6) | Component-level interfaces, data models, behavior contracts |
| Test definitions | TDD (L7) | Embedded test cases, thresholds, and BDD mapping |
| Execution planning | IPLAN (L8) | File manifest, commands, session handoff |
| Governance workflow | CHG overlay | Project-level control outside layer numbering |

## Development vs Deployment Separation

SDD enforces a strict boundary between development and deployment concerns. Development plans (IPLAN L8) produce artifacts. Deployment plans consume and apply them.

| Concern | Plan Type | Owns | Done When |
|---------|-----------|------|-----------|
| **Development** | IPLAN (L8) | Source code, Terraform modules, Helm charts, CI/CD workflow files, schema DDL, scripts — anything authored, committed, shipped via `git push` | Code + IaC + scripts authored, committed, green; tests pass |
| **Deployment** | Separate deployment plan | Operator execution: `terraform apply`, `atlas migrate apply`, image build + deploy, environment activation, acceptance/soak runs | Artifacts applied to target environment; acceptance gates green |

**Rule.** An IPLAN flips to `Completed` once source code + Terraform modules + CI/CD scripts are authored, committed, and green. It does NOT wait for deployment. A deployment-stuck IPLAN (e.g., "ready for `terraform apply`") is still complete from the development side.

**Cross-plan handoff.** When closing a development IPLAN whose artifacts depend on a deployment step, register the obligation in `IPLAN-00_index.yaml` §deferred_items before flipping status. The IPLAN status reflects authoring-completion; the registry entry tracks the deploy-side handoff.
