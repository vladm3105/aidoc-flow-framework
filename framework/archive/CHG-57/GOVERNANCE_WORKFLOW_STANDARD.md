# Governance Workflow Standard: CNCF Serverless Workflow DSL & Executable Graphs

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.2 |
| Status | Approved |
| Last Updated | 2026-10-05 |
| Author | Framework Maintainer |
| Framework Version | 0.77.0 |

Establishes the open, vendor-neutral CNCF Serverless Workflow (YAML) specification
as the official framework standard for modeling, validating, and executing governance
flows and multi-agent lifecycle state machines.

---

## 1. Purpose & Architectural Context

The SDD framework governs complex, multi-agent development lifecycles (Change Requests,
Review Sagas, Worktree Isolations, Seed Decompositions, and SDD Cascades). Historically,
these rules were documented solely as human-readable prose across dozens of markdown files.

This specification formalizes **Machine-Executable Governance**:
1. **From Prose to State Machines**: Governance flows are formally declared as Directed Acyclic
   Graphs (DAGs) and state machines using the CNCF Serverless Workflow standard.
2. **Engine-Agnostic Purity ([D-0013](DECISIONS.md))**: The framework ships pure, declarative
   YAML files (`.sw.yaml`). It does not bundle or lock into runtime engines.
3. **Execution Ready**: Agent orchestrators (e.g. LangGraph, Temporal, AutoGen, or custom agent
   harnesses) can ingest these workflow definitions on the fly to drive autonomous agents without
   procedural drift.
4. **Visual Graph Parity**: Every workflow definition serves as the single source of truth for
   rendering native Mermaid state diagrams embedded directly into human-facing documentation.

---

### Domain Separation: Governance Workflows vs. Implementation Workflows

To prevent conflation between repository governance policy and codebase mutation tasks:
1. **Governance Workflows (`framework/governance/workflows/*.sw.yaml`)**:
   Govern multi-agent repository lifecycles (Change Requests, Worktrees, PR Watches, Review Sagas).
   Governed exclusively by this standard.
2. **Implementation Workflows (`framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml`)**:
   Govern codebase mutation, test file creation, and execution-time saga compensation.
   Governed by [`IPLAN_WORKFLOW_STANDARD.md`](IPLAN_WORKFLOW_STANDARD.md).

## 2. Directory Structure & File Conventions

All declarative workflow definitions reside in `framework/governance/workflows/`:

```
framework/governance/
├── workflows/
│   ├── chg-request-flow.sw.yaml              # Change classification, gates & landing
│   ├── seed-to-module-decomposition.sw.yaml  # 5-step seed to C4-L2 module flow
│   ├── worktree-pr-lifecycle.sw.yaml         # Worktree isolation, PR watch & cleanup
│   └── review-saga-orchestration.sw.yaml     # Multi-agent review crew dispatch & fan-in
│
├── GOVERNANCE_WORKFLOW_STANDARD.md           # This normative standard
├── CHG_REQUEST_FLOWS.md                      # Prose guide embedding chg-request-flow graph
├── SEED_TO_MODULE_DECOMPOSITION.md           # Prose guide embedding decomposition graph
└── WORKTREE_FLOW.md                          # Prose guide embedding worktree graph
```

### File Naming Convention
- Canonical extension: `<domain>-<process>.sw.yaml`
- Lowercase alphanumeric slugs with hyphens (e.g., `chg-request-flow.sw.yaml`).
- Specification Version: All workflows target `specVersion: "0.8"` of the CNCF Serverless Workflow standard.

---

## 3. CNCF Serverless Workflow Mapping to SDD Governance

The framework adopts CNCF Serverless Workflow v0.8 primitives mapped directly to
governance and agentic execution concepts:

| CNCF Primitive | Governance Concept | Agentic / LangGraph Execution Mapping |
|---|---|---|
| **`start: StateName`** | Flow Entrypoint | `graph.set_entry_point(StateName)` |
| **`type: operation`** | Execution Phase | Node executing an agent persona, tool, or linter check |
| **`type: switch`** | Governance Gate Check | Conditional router (`add_conditional_edges`) evaluating gate criteria |
| **`type: parallel`** | Multi-Agent Review Crew | Concurrent fan-out to specialized reviewers (`completionType: allOf`) |
| **`type: callback` / `event`**| Human-in-the-Loop Gate | Execution pause / checkpoint awaiting human OK (founder approval) |
| **`subFlowRef`** | Sub-process Delegation | Nested invocation of child workflow (e.g. calling review saga from PR flow) |
| **`transition: NextState`**| State Progression | Deterministic graph edge (`add_edge(State, NextState)`) |
| **`end: true`** | Successful Completion | Edge terminating at `END` |
| **`end: { terminate: true }`**| Gate Rejection / Escalation| Abort / escalation terminal state |
| **`compensatedBy`** | Saga Rollback / Remediation | Compensation action restoring workspace or aborting worktree |

---

## 4. Rules for Governance Graphs

### Rule 1: Declarative Single Source of Truth
The `.sw.yaml` file is the normative authority for all state transitions, gate guards, and
allowed paths. Companion Markdown documentation (`*.md`) provides narrative context and
renders the visual graph, but must never declare transitions not permitted by the YAML.

### Rule 2: Deterministic Terminal States
Every execution path in a workflow graph must reach an unambiguous terminal state:
- **`end: true`**: Denotes successful phase completion and compliance sign-off.
- **`end: { terminate: true }`**: Denotes explicit gate failure, escalation, or rejection.
Unbounded cycles without explicit termination conditions are strictly prohibited.

### Rule 3: Gate Boundary Integrity & Switch Guards
All governance gates (GATE-01 through GATE-08, GATE-CODE, GATE-SPEC) must be represented as
explicit `switch` states. Gate transitions must carry unambiguous `dataConditions`:
```yaml
- name: EvaluateGateSpec
  type: switch
  dataConditions:
    - condition: "${ .gate_checks.all_passed == true and .gate_checks.unresolved_blockers == 0 }"
      transition: ApproveChangeRequest
  defaultCondition:
    transition: EscalateGateFailures
```

### Rule 4: Agent Persona Attribution in Actions
When an `operation` state delegates work to an AI agent, the action metadata must declare:
- The required agent role or persona (e.g., `architect`, `security_engineer`, `qa_lead`).
- The explicit input artifacts and output target.
```yaml
actions:
  - name: performSecurityAudit
    functionRef:
      refName: dispatchAgentPersona
      arguments:
        persona: "security_engineer"
        playbook: "framework/playbooks/05_ADR/security_engineer.md"
        input_artifact: "docs/sdd/05_ADR/ADR-01.yaml"
```

### Rule 5: Human-in-the-Loop & Founder OK Gates
Certain governance transitions strictly require in-session human authorization (e.g., release
promotion, unmerged branch deletion, or self-review skips). These must be modeled using
`callback` or `event` states that halt autonomous progression until an explicit event arrives:
```yaml
- name: AwaitFounderAuthorization
  type: callback
  action:
    functionRef:
      refName: promptHumanOperator
      arguments:
        prompt: "Release promotion from dev to main requires founder sign-off."
  eventRef: FounderApprovalEvent
  transition: PromoteRelease
```

### Rule 6: Saga Rollback & Compensation Actions
Workflows that perform mutating operations (worktree creation, git branching, file writes) must
declare `compensatedBy` handlers to cleanly undo side effects on failure or abort:
```yaml
- name: AllocateTaskWorktree
  type: operation
  compensatedBy: CleanupTaskWorktree
  actions:
    - name: createWorktree
      functionRef:
        refName: runGitCommand
        arguments:
          command: "git worktree add ../<name> -b feature/<slug> origin/dev"
  transition: ExecuteTaskWork
```

### Rule 7: Visual Graph Synchronization (Mermaid Parity)
Every workflow graph must maintain 1-to-1 parity with a native Mermaid `stateDiagram-v2`
embedded in its companion governance document. The graph must clearly display:
- States and transitions.
- Decision branches (choice diamonds / conditions).
- Terminal success and failure sinks.

---

## 5. LangGraph & Runtime Adapter Pattern

To preserve framework neutrality while enabling zero-effort execution in Python agent ecosystems,
runtimes compile `.sw.yaml` into LangGraph on the fly using a standard adapter:

```python
from langgraph.graph import StateGraph, START, END
import yaml

def load_governance_graph(yaml_path: str, action_bindings: dict) -> StateGraph:
    with open(yaml_path) as f:
        spec = yaml.safe_load(f)

    builder = StateGraph(dict)
    for state in spec.get("states", []):
        name = state["name"]
        stype = state.get("type", "operation")

        if stype in ("operation", "switch", "parallel"):
            fn = action_bindings.get(name, lambda s: s)
            builder.add_node(name, fn)

    for state in spec.get("states", []):
        name = state["name"]
        if "transition" in state:
            builder.add_edge(name, state["transition"])
        elif state.get("end") is True:
            builder.add_edge(name, END)
        elif state.get("type") == "switch":
            conditions = state.get("dataConditions", [])
            builder.add_conditional_edges(
                name,
                lambda s, c=conditions, d=state.get("defaultCondition", {}).get("transition"): (
                    next((x["transition"] for x in c if s.get(x["condition"])), d)
                )
            )

    builder.set_entry_point(spec["start"])
    return builder.compile()
```

---

## 6. Review Log

- **2026-10-05 — Pass 1 (Architectural Integrity & Primitives)**:
  - *Gap found*: Lack of formal human-in-the-loop primitive for founder OK gates in `AGENTS.md`.
  - *Fix*: Added Rule 5 explicitly codifying `callback` states for human authorization gates.
  - *Gap found*: Missing compensation standard for failed worktrees and branch cleanups.
  - *Fix*: Added Rule 6 codifying `compensatedBy` handlers aligning with `REVIEW_SAGA.md`.
- **2026-10-05 — Pass 2 (Schema Precision & Version Pinning)**:
  - *Gap found*: Spec version was not pinned, leading to potential schema drift between CNCF v0.8 and v1.0.
  - *Fix*: Standardized on `specVersion: "0.8"` across all workflow definitions in Section 2.
  - *Gap found*: Missing parallel state execution semantics in LangGraph adapter description.
  - *Fix*: Reconciled Section 3 and Section 5 to handle parallel fan-out nodes.
