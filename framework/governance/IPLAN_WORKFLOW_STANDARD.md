# Implementation Plan Workflow Standard: CNCF Serverless Workflow for Layer 08 (IPLAN)

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.80.0 |

Establishes the normative standard for modeling, validating, and executing Layer 08
(Implementation Plan / IPLAN) task graphs using the CNCF Serverless Workflow v0.8 specification
in YAML format within the SDD Hybrid Envelope Architecture.

---

## 1. Purpose & Architectural Context

In the 10-layer SDD specification, Layer 08 (IPLAN) serves as the **mandatory execution bridge
from SPEC (Layer 06) and TDD (Layer 07) to source code implementation**.

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
   or custom agent harnesses.
5. **Clear Domain Boundary**:
   - Governance workflows (`framework/governance/workflows/*.sw.yaml` governed by `GOVERNANCE_WORKFLOW_STANDARD.md`)
     model *meta-development and governance lifecycles* (Change Requests, Worktrees, PR Watches).
   - Implementation workflows (`framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml` governed by this standard)
     model *codebase mutation and test verification execution*.
   This separation prevents mixing governance policy with codebase implementation steps.

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
  framework_version: "0.80.0"
  document_type: "iplan-document"
  layer: 8
  workflow_standard: "CNCF-Serverless-Workflow-0.8"
  tags: [iplan-document, layer-8-artifact, shared-architecture, cncf-workflow]

document_control:
  iplan_id: "IPLAN-NN"
  subtype: workflow  # Declares the CNCF workflow subtype
  source_spec: "@spec: SPEC-NN"
  status: Draft
  version: "1.0"
  author: "[Engineer / Persona]"

file_manifest:
  files:
    - path: "src/component.py"
      description: "Source implementation"
      order: 1
      status: PENDING

tdd_consistency:
  status: complete
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

### Rule 2: TDD-First State Order
In accordance with framework testing strategy, implementation workflows must order test file
creation and execution before or in tandem with source code implementation:
1. Create/amend unit test files.
2. Implement source code fulfilling test assertions.
3. Execute verification gate evaluating test results.

### Rule 3: Mandatory Saga Compensation on Mutating States
Every `operation` state that creates files, modifies source code, or alters git state must declare
a `compensatedBy` handler that reverts its specific mutations if subsequent verification gates fail.

### Rule 4: Action Traceability Metadata
To maintain element-level traceability across the SDD layers, actions within operation states
must carry upstream citations within their `metadata` dictionary:
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

---

## 5. LangGraph & Runtime Adapter Pattern

Autonomous agent runners compile the `workflow:` block of an IPLAN into LangGraph on the fly:

```python
from langgraph.graph import StateGraph, START, END
import yaml

def compile_iplan_workflow(iplan_path: str, action_handlers: dict) -> StateGraph:
    with open(iplan_path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)

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

## 6. Review Log

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
