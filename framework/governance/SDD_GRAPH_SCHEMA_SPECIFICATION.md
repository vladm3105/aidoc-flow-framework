# Specification: Native SDD Graph Schema (SDD-GRAPH v2.0)

## Document Control

| Field | Value |
|---|---|
| Version | 2.0.0 |
| Status | Ratified |
| Last Updated | 2026-10-16 |
| Author | Framework Maintainer |
| Framework Version | 0.96.7 |
| Authority | Decision DEC-CHG-108 / GD-95, [`DOC_GOVERNANCE_CORE.md`](DOC_GOVERNANCE_CORE.md), [`IPLAN_WORKFLOW_STANDARD.md`](IPLAN_WORKFLOW_STANDARD.md) |

---

## 1. Purpose & Core Philosophy

The Native SDD Graph specification defines a machine-native, typed property graph representing the entire lifecycle of software requirements, architecture decisions, behavioral acceptance criteria, test proofs, and codebase implementation tasks.

### 1.1 Beyond Document-Oriented Artifacts
Traditional SDD artifacts structured specifications as human-facing documents (hierarchical YAML sections, markdown headings, and prose paragraphs). In an autonomous software delivery environment:
- **Primary Consumers & Producers**: Autonomous AI agents (Planner, Architect, SDET, Developer, Reviewer) and deterministic verification tools.
- **Single Source of Truth (SSOT)**: A typed property graph (`.graph.yaml`) storing atomic nodes and relational edges.
- **Mathematical Integrity**: Binary Topological Validation (BTV), acyclicity, and coverage are computed using pure graph algorithms (`networkx`) rather than regular expression scrapers.
- **Human Visibility**: Maintained as an on-demand, read-only projection via the Observability Adapter ([`OBSERVABILITY_ADAPTER_CONTRACT.md`](OBSERVABILITY_ADAPTER_CONTRACT.md)).

---

## 2. Graph Data Model & Root Envelope

Every graph slice is stored as a YAML document conforming to [`framework/governance/sdd-graph.schema.json`](sdd-graph.schema.json):

```yaml
schema_version: "2.0-graph"
slice_id: "INIT-01_user_authentication"
metadata:
  author: "ai-persona:architect-01"
  created_date: "2026-10-16"
  last_updated: "2026-10-16"
  status: "Active"
  framework_version: "0.96.7"
  description: "OAuth2 and JWT token verification capability"

nodes:
  # Atomic nodes defined here
  ...

edges:
  # Relational edges defined here
  ...
```

---

## 3. Node Ontology (10 Canonical SDD Types + Change Overlay)

Every node carries an immutable 4-segment content-hash ID (`TYPE.NN.SS.xxxx` or canonical entity token) and specific typed properties:

### 3.1 Tier 1: Seed Vision (`seed_intent`)
- **ID Pattern**: `SEED-<slug>`
- **Properties**: `title`, `statement` (intent / vision), `properties.environmental_constraints`, `properties.c4_level: "c4-l1"`.
- **Role**: Captures stakeholder problem space, business context, and top-level boundaries.

### 3.2 Tier 2: Subsystem Container (`system_container`)
- **ID Pattern**: `MODULE-NN` (e.g. `MODULE-01` or template `MODULE-NN`)
- **Properties**: `title`, `statement` (subsystem role), `description`, `properties.c4_level: "c4-l2"`, `properties.container_archetype` (`api_service` | `worker` | `data_store` | `spa` | `gateway` | `library`), `properties.approved_stack`, `properties.runtime_platform`, `properties.candidate_stack_status`, `properties.subsystem_invariants`, `properties.trust_boundary`, `properties.data_classification`, `properties.data_protection_matrix`, `properties.choreography` (`interactions`, `failure_branches`).
- **Role**: Defines architectural subsystem container (C4-L2), data movement boundaries, trust enclaves, and inter-module process choreography.

### 3.3 Layer 01: Business Objective (`business_objective`)
- **ID Pattern**: `BRD.NN.SS.xxxx` (or `BIZ.NN.SS.xxxx`)
- **Properties**: `title`, `statement`, `properties.priority` (`P0`–`P3`), `properties.roi_target`.
- **Role**: Defines business value drivers, market requirements, and executive goals.

### 3.4 Layer 02: Product Capability (`product_capability`)
- **ID Pattern**: `PRD.NN.SS.xxxx`
- **Properties**: `title`, `statement`, `properties.persona`, `properties.sla_threshold`.
- **Role**: Partitions business goals into buildable product feature capabilities.

### 3.5 Layer 03: Formal Requirement (`formal_requirement`)
- **ID Pattern**: `EARS.NN.SS.xxxx`
- **Properties**: `title`, `statement`, `pattern` (`ubiquitous` | `event_driven` | `state_driven` | `optional` | `unwanted`).
- **Role**: Strict EARS syntax specifying exact functional behavior.

### 3.6 Layer 04: Acceptance Scenario (`acceptance_scenario`)
- **ID Pattern**: `BDD.NN.SS.xxxx`
- **Properties**: `title`, `given`, `when`, `then`.
- **Role**: The behavioral oracle defining "what correct looks like" independently of code.

### 3.7 Layer 05: Architectural Decision (`architectural_decision`)
- **ID Pattern**: `ADR.NN.SS.xxxx`
- **Properties**: `title`, `context`, `decision`, `consequences`, `status` (`Proposed` | `Accepted` | `Deprecated`).
- **Role**: Durable record of architectural design rationale and trade-offs.

### 3.8 Layer 06: Component Contract (`component_contract`)
- **ID Pattern**: `SPEC.NN.SS.xxxx`
- **Properties**: `title`, `target_file`, `properties.protocol` (`grpc` | `http` | `cloudevents`), `properties.schema_ref`.
- **Role**: Buildable interface specification and wire contract (C4-L3).

### 3.9 Layer 07: Test Fixture (`test_fixture`)
- **ID Pattern**: `TDD.NN.SS.xxxx`
- **Properties**: `title`, `target_file`, `command` (e.g. `pytest tests/unit/test_jwt.py`), `properties.test_function`.
- **Role**: Concrete test code proving scenario satisfaction, authored test-first.

### 3.10 Layer 08: Implementation Task (`task_action`)
- **ID Pattern**: `TASK.NN.SS.xxxx` (rollback: `TASK.NN.SS.xxxx_rollback`)
- **Properties**: `title`, `action` (`apply_patch` | `create_file` | `run_script`), `target_file`, `compensation`.
- **Role**: Executable code mutation DAG with native saga rollback compensation.

### 3.11 Layer 09 Overlay: Change Request (`change_request`)
- **ID Pattern**: `CHG-NN`
- **Properties**: `title`, `status`, `authorized_by`, `properties.change_level` (`C1`–`C3`).
- **Role**: Transactional governance envelope authorizing mutations to active nodes.

### 3.12 Layer 10: Evaluation Suite (`evaluation_suite`)
- **ID Pattern**: `EVAL.NN.SS.xxxx`
- **Properties**: `title`, `statement`, `properties.eval_track`, `properties.environment`, `properties.scoring_criteria`, `properties.quality_gate`, `properties.benchmark_thresholds`.
- **Role**: Comprehensive evaluation and verification suite auditing requirements coverage, performance benchmarks, and regression gates.

---

## 4. Edge Ontology & Cardinality Invariants

Edges represent directed semantic dependencies (`from` $\longrightarrow$ `to`). The graph validator enforces strict cardinality rules:

```
[seed_intent] ──decomposes_to──► [system_container]
                                         │
[business_objective] ◄──realizes───────┤
                                         ▼
                               [product_capability]
                                         ▲
[formal_requirement] ──realizes─────────┘
         ▲  ▲
         │  └──verifies── [evaluation_suite] ──verifies──► [test_fixture] / [task_action]
         │
         └──verifies── [acceptance_scenario] ◄──proves── [test_fixture]
                                                               ▲
[architectural_decision] ──constrains──► [component_contract]  │
                                                ▲              │
                                                └──implements──┴── [task_action]
                                                                        │
                                                                   compensated_by
                                                                        ▼
                                                                 [rollback_action]
```

### 4.1 Cardinality Invariant Table

| Rule ID | Relation | From | To | Cardinality | Verification Invariant |
|---|---|---|---|---|---|
| `GRAPH-CARD-001` | `decomposes_to` | `seed_intent` | `system_container` / `product_capability` | $1 : N$ ($N \ge 1$) | Seed vision must decompose into $\ge 1$ container/capability. |
| `GRAPH-CARD-002` | `realizes` | `formal_requirement` | `product_capability` / `business_objective` | $M : N$ ($N \ge 1$) | Every requirement must trace upstream to an authorized capability. |
| `GRAPH-CARD-003` | `verifies` | `acceptance_scenario` | `formal_requirement` | $M : N$ ($N \ge 1$) | **Oracle Invariant**: Every requirement MUST have $\ge 1$ BDD scenario. |
| `GRAPH-CARD-004` | `proves` | `test_fixture` | `acceptance_scenario` | $M : N$ ($N \ge 1$) | **Test Proof Invariant**: Every scenario MUST have $\ge 1$ test fixture. |
| `GRAPH-CARD-005` | `constrains` | `architectural_decision`| `component_contract` | $M : N$ | Component interfaces must adhere to ratified ADRs. |
| `GRAPH-CARD-006` | `implements` | `task_action` | `component_contract` / `test_fixture` | $M : N$ ($N \ge 1$) | Tasks must directly target contracts or failing test fixtures. |
| `GRAPH-CARD-007` | `compensated_by` | `task_action` | `task_action` (rollback) | $1 : 1$ (Strict) | **Saga Rollback Invariant**: Every mutating task MUST have 1 rollback. |
| `GRAPH-CARD-008` | `authorized_by` | Any mutated node | `change_request` | $1 : 1$ | Mutated/superseded nodes must cite an authorizing CHG. |
| `GRAPH-CARD-009` | `supersedes` | New Node Version | Old Node Version | $1 : 1$ | Preserves immutable version lineage. |
| `GRAPH-CARD-010` | `verifies` | `evaluation_suite` | `task_action` / `test_fixture` / `formal_requirement` | $M : N$ ($N \ge 1$) | **Holistic Evaluation Invariant**: Every evaluation suite MUST verify $\ge 1$ target (task, test fixture, or formal requirement). |

---

## 5. Storage Partitioning & Git Tracking

To eliminate Git merge collisions across concurrent multi-agent branches:
1. **Initiative Slices**: `docs/sdd/graph/initiatives/<initiative_slug>.graph.yaml` contains feature-specific requirements, scenarios, tests, and task actions.
2. **Module Slices**: `docs/sdd/graph/modules/<module_slug>.graph.yaml` contains persistent container definitions, component contracts, and core interfaces.
3. **In-Memory Unification**: The graph verification engine merges all slice files into a unified DAG in memory during test and CI runs.
4. **Git Tracking Policy**: All `.graph.yaml` files are tracked directly in version control. Filesystem symlinks are strictly banned.

---

## 6. Federated Multi-Repository Contracts

Per [`MULTI_PROJECT_FEDERATED_STANDARD.md`](MULTI_PROJECT_FEDERATED_STANDARD.md):
- Nodes can reference external specifications using URI prefixes: `@<repo_slug>:<NODE_ID>`.
- Example: `to: "@auth-service:SPEC.06.01.a8b9"`.
- BTV resolves federated targets against `.aidoc/contracts-registry.yaml`. Declared external nodes are treated as validated stubs, allowing local BTV verification to pass cleanly without checking out external repositories.

---

## 7. Node Immutability Lifecycle

1. **Active Invariance**: Once committed to `dev` with `status: Active`, nodes are immutable.
2. **Mutation Mechanics**: To modify a requirement:
   - A new node is authored with a new content-hash ID: `EARS.01.03.c4d5`.
   - The new node specifies: `supersedes: "EARS.01.03.a1b2"` and `authorized_by: "CHG-108"`.
   - The old node is marked `status: Superseded`.
3. **Historical Auditability**: The graph engine maintains complete historical lineage without modifying past Git commits.
