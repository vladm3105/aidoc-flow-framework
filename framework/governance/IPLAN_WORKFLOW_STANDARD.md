# Implementation Plan Workflow Standard: CNCF Serverless Workflow for Layer 08 (IPLAN)

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.2 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.96.7 |

Establishes the normative standard for modeling, validating, and executing Layer 08
(Implementation Plan / IPLAN) task graphs using the CNCF Serverless Workflow v0.8 specification
in YAML format within the SDD Hybrid Envelope Architecture across all 6 framework traversal-path graph flows.

---

## 1. Purpose & Architectural Context

In the 10-layer SDD specification, Layer 08 (IPLAN) serves as the **mandatory execution engine
for mutating codebase changes**. Rather than being restricted to a monolithic forward bridge
from SPEC (Layer 06) and TDD (Layer 07) to source code, Layer 08 executes across **all 6 canonical
graph traversal paths** ratified in Decisions GD-65 and GD-66:

1. **`sdd_to_code` (`SDD2C`)**: Full forward SDD cascade for greenfield capabilities (BRD $\to$ PRD $\to$ EARS $\to$ BDD $\to$ ADR $\to$ SPEC $\to$ TDD $\to$ IPLAN $\to$ Code).
2. **`iplan_to_code` (`DIR2C`)**: Fast-lane direct execution for C1 documentation, tooling, script, and non-behavioral changes (`sdd_lifecycle: []`), bypassing upstream SPEC/TDD.
3. **`code_to_code` (`CODE2C`)**: Closed-IPLAN defect repair (`IPLAN-{NEW}_bugfix_{FIXED}_{slug}.yaml`) executing defect reproduction first, patch implementation, and regression suite verification.
4. **`code_to_sdd` (`CODE2S`)**: Backward code-to-doc reconciliation (Type-R §3.1.2) where a frozen, verified codebase coordinates reverse-engineering into upstream SDD specifications.
5. **`seed_to_code` (`SEED2C`)**: Brownfield / contract changes executing multi-tier macro-decomposition from Tier 1 Seed Vision and Tier 2 Module containers down through SDD layers to Code.
6. **`hotfix` (`HOTFIX`)**: Production emergency remediation with expedited rollback/patch DAG followed by retrospective CHG and post-mortem within 48 hours.

Historically, IPLAN documents functioned as static checklists:
1. `file_manifest`: A passive inventory of files to create or modify.
2. `execution_commands`: Sequential CLI commands without conditional logic or dependency DAGs.
3. `rollback_procedure`: Passive prose instructions rather than executable compensation routines.

While human-readable, static checklists force autonomous AI coding agents (and multi-agent orchestrators)
to guess transition boundaries, step dependencies, and failure-handling procedures.

This standard establishes **Machine-Executable Implementation Plans**:
1. **From Prose to Executable DAG**: Implementation tasks are formally declared as Directed Acyclic
   Graphs (DAGs) and state machines using the CNCF Serverless Workflow v0.8 specification.
2. **Hybrid Envelope Architecture**: Preserves the outer SDD document envelope (`metadata`,
   `document_control`, `file_manifest`, `tdd_consistency`, `traceability`) to maintain complete
   backward compatibility with structural linters (`STRUCT01`, `TAG01`, and `sdd_doc_lint`), while
   housing the executable workflow graph under the dedicated `workflow:` block.
3. **Native Saga Compensation (`compensatedBy`)**: Rollback procedures are declared as first-class
   compensation states that automatically trigger when verification tests fail, preventing corrupted
   worktrees and half-implemented commits.
4. **Engine Agnosticism ([D-0013](DECISIONS.md))**: The framework ships pure declarative YAML without
   bundling proprietary orchestrator runtimes. Workflows compile on the fly into LangGraph, Temporal,
   Rust Rig (`rig-core`), or custom agent harnesses.
5. **Clear Domain Boundary**:
   - Governance workflows (`framework/governance/workflows/*.sw.yaml` governed by `GOVERNANCE_WORKFLOW_STANDARD.md`)
     model *meta-development and governance lifecycles* (Change Requests, Worktrees, PR Watches).
   - Implementation workflows (`framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml` governed by this standard)
     model *codebase mutation and test verification execution*.
   This separation prevents mixing governance policy with codebase implementation steps.

---

### The Two-Graph Architecture in Layer 08 IPLAN

Layer 08 employs the framework's **Two-Graph Dual-Plane Architecture**, pairing an executable implementation process DAG with an atomic task content graph:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                          LAYER 08 IPLAN TWO-GRAPH ARCHITECTURE                              │
├────────────────────────────────────────────────────────┬────────────────────────────────────┤
│          GRAPH 1: PROCESS DAG (CONTROL PLANE)          │   GRAPH 2: CONTENT GRAPH (DATA)    │
│       IPLAN-SWF-TEMPLATE.yaml (Hybrid Envelope)        │      (IPLAN-GRAPH-TEMPLATE.yaml)   │
├────────────────────────────────────────────────────────┼────────────────────────────────────┤
│ • CNCF Serverless Workflow v0.8 state machine DAG      │ • SDD-GRAPH v2.0 Property Graph    │
│ • Flow of HOW to execute, verify & rollback mutations  │ • Content of WHAT tasks exist      │
│ • Sequential/parallel code mutation steps              │ • Implementation tasks & contracts │
│ • Automated test execution & regression verification   │ • File manifests & touchpoints     │
│ • First-class saga rollback compensation               │ • Relational links (implements etc)│
│ • Compiled to LangGraph / Temporal / runner engine     │ • Validated via BTV engine         │
└───────────────────────────┬────────────────────────────┴─────────────────┬──────────────────┘
                            │                                              │
                            ▼                                              ▼
                    ┌──────────────────────────────────────────────────────────────┐
                    │               DOCUMENT GENERATION & PROJECTION               │
                    ├──────────────────────────────────────────────────────────────┤
                    │ • Process DAG orchestrates code mutation & verification      │
                    │ • Agent actions populate and mutate atomic nodes in Data     │
                    │ • BTV verifies topological closure & task dependencies       │
                    │ • Observability Adapter projects graph into IPLAN-TEMPLATE   │
                    └──────────────────────────────────────────────────────────────┘
```

Both graphs work together: the Process DAG drives execution, populates the Content Graph, verifies topological integrity via BTV, and projects the validated plan into the canonical human-readable document (`IPLAN-TEMPLATE.yaml` view).

---

## 2. Hybrid Envelope Architecture

To maintain compatibility with `sdd_doc_lint` while providing an executable workflow DAG, all
CNCF-compliant IPLAN artifacts adopt the **Hybrid Envelope Architecture**:

```yaml
doc_id: IPLAN-NN
title: "[Component Implementation Plan]"

# --- Top-Level SDD Envelope (Preserved for STRUCT01 / TAG01) ---
metadata:
  schema_version: "2.0"
  framework_version: "0.96.7"
  document_type: "iplan-document"
  layer: 8
  workflow_standard: "CNCF-Serverless-Workflow-0.8"
  tags: [iplan-document, layer-8-artifact, shared-architecture, cncf-workflow]

document_control:
  iplan_id: "IPLAN-NN"
  flow: "sdd_to_code"      # hotfix | code_to_sdd | code_to_code | seed_to_code | iplan_to_code | sdd_to_code
  flow_code: "SDD2C"       # HOTFIX | CODE2S | CODE2C | SEED2C | DIR2C | SDD2C
  subtype: workflow        # code_build | deploy | combined | workflow | audit_fix | bugfix | docs
  source_spec: "@spec: SPEC-NN"  # Required for SDD2C/SEED2C; optional for DIR2C (iplan_to_code)
  status: Draft
  version: "1.0"
  author: "[Engineer / Persona]"

file_manifest:
  files:
    - path: "src/component.py"
      description: "Source implementation"
      order: 1
      status: NOT_STARTED

tdd_consistency:
  status: complete  # complete | partial | not-applicable (DIR2C)
  tdd_ref: "@tdd: TDD.NN.01.0001"

# --- Section 3: CNCF Serverless Workflow Graph ---
workflow:
  id: iplan-nn-workflow
  name: "Component Execution Workflow"
  version: "1.0"
  specVersion: "0.8"
  start: InitialState
  states:
    # State machine definition ...

# --- Backmatter & Traceability Envelope ---
implementation_contracts:
  invariants: [...]

session_handoff:
  current_phase: "Ready for Execution"

traceability:
  upstream: ["@spec: SPEC-NN", "@tdd: TDD.NN.01.0001"]
  downstream: ["@code: src/component.py"]
```

---

## 3. CNCF Serverless Workflow Primitives in IPLAN

Layer 08 maps CNCF Serverless Workflow v0.8 primitives to concrete implementation concepts:

| CNCF Primitive | IPLAN Implementation Concept | Execution Behavior |
|---|---|---|
| **`start: StateName`** | Initial Execution Step | Sets the first task node in the execution graph |
| **`type: operation`** | Mutating Implementation Step | Executes file edits, snapshot creation, or command runs |
| **`type: switch`** | Test / Verification Gate Check | Evaluates test suite exit codes (`pytest`, `ruff`, `cargo`) |
| **`type: parallel`** | Concurrent File Generation | Parallel dispatch of independent module file writes |
| **`compensatedBy`** | Executable Saga Rollback | Target state invoked when verification gates fail |
| **`end: true`** | Clean Implementation Sign-off | Successful verification, staging, and commit completion |
| **`end: { terminate: true }`**| Aborted Execution Sink | Terminal sink after rollback compensation finishes |

---

## 4. Normative Rules for IPLAN Workflows

### Rule 1: Static Inventory Parity
Every file modified or created within an `operation` state's actions must be declared in the
top-level `file_manifest.files` list. Undocumented file modifications are strictly prohibited.

### Rule 2: Flow-Aware Test Ordering
In accordance with framework testing strategy, task ordering is bound to the declared traversal path:
1. **`sdd_to_code` (`SDD2C`) & `seed_to_code` (`SEED2C`)**: Implementation workflows must order test file
   creation and execution before or in tandem with source code implementation.
2. **`code_to_code` (`CODE2C`)**: Workflows must author a failing regression reproduction test before
   modifying source code, verifying that the fix specifically resolves the reported defect.
3. **`iplan_to_code` (`DIR2C`) Carve-out**: Direct documentation, tooling, script, or chore changes are
   exempt from test-first ordering (`tdd_consistency.status: not-applicable`); they require covering
   linter, formatter, or build dry-run checks before commit.

### Rule 3: Mandatory Saga Compensation on Mutating States
Every `operation` state that creates files, modifies source code, or alters git state must declare
a `compensatedBy` handler that reverts its specific mutations if subsequent verification gates fail.

### Rule 4: Action Traceability Metadata
To maintain element-level traceability across the SDD layers, actions within operation states
must carry upstream citations within their `metadata` dictionary:
- **`SDD2C`**: Must carry `@spec` and `@tdd` (plus optional `@req` / `@brd`).
- **`SEED2C`**: Must carry `@seed`, `@module`, `@spec`, and `@tdd`.
- **`CODE2C`**: Must carry `@chg` and `@tdd` (or parent IPLAN element citation).
- **`DIR2C`**: Must carry `@task` or `@chg` (exempt from `@spec` / `@tdd` requirements).
- **`CODE2S`**: Must carry `@code` source file citations pointing to verified ground truth.

```yaml
actions:
  - name: implementTokenMinting
    metadata:
      "@spec": "SPEC-02"
      "@tdd": "TDD.02.01.0001"
      "@req": "PRD-02.FR-03"
    functionRef:
      refName: editFileContent
      arguments:
        target_file: "src/auth/tokens.py"
```

### Rule 5: Deterministic Gate Sinks
Every `switch` state evaluating verification results must define:
1. `dataConditions`: Routing to the next progression step upon passing test results.
2. `defaultCondition`: Routing to an explicit saga rollback compensation sequence.
Never leave gate failures unhandled or falling through to subsequent implementation steps.

### Rule 6: Visual Graph Parity
Every IPLAN workflow must maintain 1-to-1 parity with an embedded Mermaid `stateDiagram-v2`
diagram in its companion documentation or planning record.

### Rule 7: Approved Technology Stack Invariant Enforcement
Every IPLAN workflow mutating production, test, or service code must enforce the approved
technology stack contracts ratified in Layer 05 ADR and specified in SPEC/TDD. Code mutations
must conform to target engine idioms (e.g., PostgreSQL 18 with UUIDv7 and Bytebase declarative
migrations, NATS JetStream subjects, Temporal workflow activities with saga rollbacks, LiteLLM
proxy clients) per [`TECHNOLOGY_STACK_USAGE_GUIDE.md`](TECHNOLOGY_STACK_USAGE_GUIDE.md).

---

## 4.1 Traversal-Path State Machine Topologies

Layer 08 compiles into 4 distinct execution topologies depending on the declared `flow`. Each topology incorporates bounded self-remediation (`max_attempts: 3`), non-destructive blocker handling (`ExecutionBlockedTerminal`), and saga compensation (`TriggerSagaRollback`):

### 1. Greenfield Forward Topology (`sdd_to_code` / `SDD2C`)
```
PreFlightCheck → SnapshotOriginals → ImplementTestsFirst → ImplementSourceCode → EvaluateVerificationGate → CommitAndSignoff
                                                                                       ↓ (fails & attempt < max_attempts)
                                                                                  RemediateImplementationFixes ──┘ (retry)
                                                                                       ↓ (fails & attempt >= max_attempts & blocker)
                                                                                  ExecutionBlockedTerminal
                                                                                       ↓ (fails & attempt >= max_attempts & regression)
                                                                                  TriggerSagaRollback
```

### 2. Defect Repair Topology (`code_to_code` / `CODE2C`)
```
PreFlightCheck → SnapshotOriginals → AuthorReproductionTest → ApplyPatchFix → EvaluateRegressionGate → CommitAndSignoff
                                                                                     ↓ (fails & attempt < max_attempts)
                                                                                RemediateImplementationFixes ──┘ (retry)
                                                                                     ↓ (fails & attempt >= max_attempts & blocker)
                                                                                ExecutionBlockedTerminal
                                                                                     ↓ (fails & attempt >= max_attempts & regression)
                                                                                TriggerSagaRollback
```

### 3. Direct Fast-Lane Topology (`iplan_to_code` / `DIR2C`)
```
PreFlightCheck → SnapshotOriginals → ApplyFileEdits → EvaluateLintsAndChecks → CommitAndSignoff
                                                              ↓ (fails & attempt < max_attempts)
                                                         RemediateImplementationFixes ──┘ (retry)
                                                              ↓ (fails & attempt >= max_attempts & blocker)
                                                         ExecutionBlockedTerminal
                                                              ↓ (fails & attempt >= max_attempts & regression)
                                                         TriggerSagaRollback
```

### 4. Backward Reconciliation Topology (`code_to_sdd` / `CODE2S`)
```
PreFlightCheck → FreezeCodebase → InspectCodeContracts → ReverseAuthorSDD → EvaluateDocLintGate → CommitAndSignoff
                                                                                  ↓ (fails & attempt < max_attempts)
                                                                             RemediateImplementationFixes ──┘ (retry)
                                                                                  ↓ (fails & attempt >= max_attempts & blocker)
                                                                             ExecutionBlockedTerminal
                                                                                  ↓ (fails & attempt >= max_attempts & regression)
                                                                             TriggerSagaRollback
```

---

## 5. LangGraph & Runtime Adapter Pattern

Autonomous agent runners compile the `workflow:` block of an IPLAN into LangGraph on the fly,
validating node transitions against the declared `flow`:

```python
from langgraph.graph import StateGraph, START, END
import yaml

def compile_iplan_workflow(iplan_path: str, action_handlers: dict) -> StateGraph:
    with open(iplan_path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    # Validate flow declaration
    control = doc.get("document_control", {})
    flow = control.get("flow", "sdd_to_code")
    flow_code = control.get("flow_code", "SDD2C")

    # Extract the CNCF workflow block from the Hybrid Envelope
    spec = doc.get("workflow", {})
    builder = StateGraph(dict)

    # Register nodes
    for state in spec.get("states", []):
        s_name = state["name"]
        s_type = state.get("type", "operation")

        if s_type == "operation":
            handler = action_handlers.get(s_name, lambda s: s)
            builder.add_node(s_name, handler)
        elif s_type == "switch":
            builder.add_node(s_name, lambda s: s)

    # Register edges & conditional branches
    for state in spec.get("states", []):
        s_name = state["name"]
        if "transition" in state:
            builder.add_edge(s_name, state["transition"])
        elif state.get("end") is True:
            builder.add_edge(s_name, END)
        elif state.get("type") == "switch":
            conditions = state.get("dataConditions", [])
            builder.add_conditional_edges(
                s_name,
                lambda s, c=conditions, d=state.get("defaultCondition", {}).get("transition"): (
                    next((x["transition"] for x in c if s.get(x["condition"])), d)
                )
            )

    builder.set_entry_point(spec["start"])
    return builder.compile()
```

---

## 6. Closed Dual-Flow Quality Loop: Authoring & Review Saga Binding (CHG-111, GD-98)

To eliminate the decoupling between implementation plan execution and review crew evaluation:

1. **Explicit Author Rubric Binding**:
   - The document envelope `metadata:` block declares `author_persona: "tech_lead"` and `author_playbook: "framework/playbooks/08_IPLAN/tech_lead.md"`.
   - Autonomous implementation agents derive cutover sequences, reversibility guarantees, and smoke gate definitions directly from this rubric prior to authoring.

2. **Mandatory Review Saga Invalidation & Gating**:
   - Prior to final commit and sign-off (`Step6_CommitAndSignoff`), the workflow executes `InvokeReviewSagaGate` via the `invokeReviewSaga` custom function, invoking the designated review saga subflow (`iplan-review-remediation-flow`).
   - The review saga coordinates multi-agent review crew evaluation across persona playbooks, enforcing the quality gate condition:
     `${ .blocking_findings == 0 and .gate_passed == true }`.
   - If findings or reversibility gaps are uncovered, the saga triggers an automated remediation loop, halting code commit until all P0/P1 blockers are resolved.

---

## 7. 5-Step Closed Layer Lifecycle and CloudEvent Handoff (CHG-112, GD-99)

Layer 08 IPLAN implements the standardized 5-step closed lifecycle:
1. **Stage 1 (Authoring)**: Tech lead authors implementation file manifest, mutation tasks, and saga rollback compensation states.
2. **Stage 2 (Review & Remediation)**: Review saga executes multi-persona review. Unresolved blockers trigger author remediation (`RemediateLayerDraft`, author: `tech_lead`) before re-entering `InvokeReviewSagaGate` (Circuit Breaker CB-1: max 2 remediation passes / 3 review cycles).
3. **Stage 3 (Layer Boundary Gate Verification)**: `VerifyLayerCloseoutGate` verifies `GATE-08` exit criteria (`GATE-08_IPLAN_IMPLEMENTATION.md`).
4. **Stage 4 (Baseline Sealing & SDD Graph Lineage)**: `SealLayerDocumentBaseline` seals frontmatter status to `Approved` with SHA-256 checksum; `RegisterSddGraphBaselineNode` registers `IplanNode` in SDD graph and locks incoming edges.
5. **Stage 5 (Downstream Handoff CloudEvent Emission)**: `EmitLayerHandoffEvent` publishes `IplanApprovedEvent` (`org.aidoc.sdd.layer08.iplan.approved`) with payload `file_manifest`, `tasks`, `iplan_checksum`, authorizing code execution and subsequent Layer 10 (EVAL) verification.

---

## 8. The Four Orthogonal Status Planes (CHG-120)

To prevent status pollution, loss of immutability, and state-projection ambiguity during autonomous execution, Layer 08 establishes four distinct, orthogonal status families (harmonized with `aidoc-flow-iplan-standard`):

| Plane | Scope | Permitted Values | Mutation Authority |
|---|---|---|---|
| **Plane 1: Document / Management** | `document_control.status` | `Draft`, `Approved`, `In Progress`, `Completed`, `Verified` | Governance Gate / Tech Lead / EVAL |
| **Plane 2: Step / Work Order** | Step execution state | `Not Started`, `Queued`, `Running`, `Blocked`, `Completed`, `Failed`, `Cancelled` | Execution Orchestrator |
| **Plane 3: File Manifest** | `file_manifest.files[].status` | `NOT_STARTED`, `IN_PROGRESS`, `PARTIAL`, `DONE`, `SKIPPED` | Autonomous Worker / File Mutator |
| **Plane 4: Runtime Event** | Signed execution events | `accepted`, `running`, `blocked`, `succeeded`, `failed`, `cancelled` | Worker / Tool Harness |

### Status Projection Invariants
1. **Separation of Document vs Execution**: A document in `In Progress` status contains steps transitioning through `Queued` → `Running` → `Completed`. A failed step does not mutate `document_control.status` to `Failed` — it marks the step `Failed` or `Blocked`, triggering remediation or compensation.
2. **File Manifest vs Verification**: `status: DONE` asserts that the file has been authored and exists on disk. `verified: true` asserts that unit tests have executed against the file and passed cleanly. A file may be `DONE` while `verified: false`.
3. **Non-Destructive Blocker Projection**: An agent receiving `on_blocker` or `on_ambiguity` emits a `blocked` runtime event projecting the step status to `Blocked` and halting at `ExecutionBlockedTerminal` without triggering file deletion or rollback.

---

## 9. Execution Evidence Receipts Specification (CHG-120)

Upon completing Step 5 (`Step5_VerifyImplementationSuite`) and sign-off, the Layer 08 execution engine generates a detached, tamper-evident execution receipt bridging Layer 08 codebase mutations to downstream Layer 10 (EVAL) evaluation:

```yaml
schema_version: "1.0"
document_type: "iplan-execution-receipt"
receipt_id: "RCPT-08-0001"
iplan_ref:
  iplan_id: "IPLAN-01"
  plan_version: "1.0"
  plan_digest: "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069" # RFC-8785 canonical hash
execution_context:
  git_commit_sha: "5bf2034e02a2b1387a3399550a323d1eccec5ce3"
  branch: "feature/chg-120-iplan-execution"
  executor_id: "agent:autonomous_coder"
  started_at: "2026-10-19T13:30:00Z"
  completed_at: "2026-10-19T13:35:00Z"
verification_summary:
  total_attempts: 1
  max_attempts: 3
  test_suites_passed: true
  linters_clean: true
  gate_outcome: "PASSED"
  artifacts_manifest:
    - path: "src/order_gateway/handler.py"
      status: "DONE"
      verified: true
      sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```
Downstream Layer 10 (EVAL) ingests this receipt to verify compliance against upstream specification contracts without re-running long implementation harnesses.

---

## 10. Review Log

- **2026-10-05 — Pass 1 (Envelope Preservation & Lint Integrity)**:
  - *Gap found*: Naive conversion of IPLAN to pure CNCF root broke `sdd_doc_lint`'s `STRUCT01` check.
  - *Fix*: Designed the Hybrid Envelope Architecture, retaining top-level `metadata`, `document_control`, `file_manifest`, and `traceability` keys while housing the state machine in `workflow:`.
  - *Gap found*: Passive prose rollback in Section 8 disconnected from execution logic.
  - *Fix*: Replaced passive prose with native CNCF `compensatedBy` saga rollback states.
- **2026-10-05 — Pass 2 (Traceability & Domain Boundaries)**:
  - *Gap found*: Ambiguity between governance workflows and implementation workflows.
  - *Fix*: Formalized clear separation in Section 1 (governance flows govern repo policy; IPLAN flows govern code mutation).
  - *Gap found*: Lack of tag extraction rules in workflow actions.
  - *Fix*: Codified Rule 4 mandating `@spec` and `@tdd` in action `metadata` dictionaries for seamless AST extraction.
- **2026-10-06 — Pass 3 (Dual-Layer Graph Flow & Multi-Topology Execution)**:
  - *Gap found*: Monolithic forward-flow assumption broke `DIR2C` (iplan_to_code), `CODE2C` (bugfix), and `CODE2S` (reconciliation).
  - *Fix*: Re-architected Section 1 to govern all 6 graph traversal paths; added `flow` and `flow_code` to the Hybrid Envelope; relaxed Rule 2 and Rule 4 for `DIR2C`; codified 4 standard DAG topologies in Section 4.1.
- **2026-10-19 — Pass 4 (Execution Resilience, Non-Destructive Blocked State, and 4-Plane Status Taxonomy — CHG-120)**:
  - *Gap found*: Immediate destructive saga rollback on first verification failure prevented autonomous agent remediation.
  - *Fix*: Introduced bounded inner remediation loop (`RemediateImplementationFixes`, `max_attempts: 3`) and non-destructive `ExecutionBlockedTerminal`.
  - *Gap found*: Internal vocabulary drift (`status: PENDING` in file manifest) and residual `.review_score >= 90` condition in Section 6.
  - *Fix*: Standardized file manifest on `NOT_STARTED`; retired residual `.review_score >= 90` in favor of zero blocking findings gate; codified the 4 orthogonal status planes in Section 8 and evidence receipts in Section 9.

