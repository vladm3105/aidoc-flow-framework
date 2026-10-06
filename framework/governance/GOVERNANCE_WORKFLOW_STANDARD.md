# Governance Workflow Standard: CNCF Serverless Workflow DSL & Executable Graphs

## Document Control

| Field | Value |
|---|---|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.88.2 |

Establishes the open, vendor-neutral CNCF Serverless Workflow (YAML) specification
as the official framework standard for modeling, validating, and executing governance
flows and multi-agent lifecycle state machines.

---

## 1. Purpose & Architectural Context

The SDD framework governs complex, multi-agent development lifecycles (Change Requests,
Review Sagas, Worktree Isolations, Seed Decompositions, Evaluation Runs, Decision Ratifications, and QA Acceptance Runs).
Historically, these rules were documented solely as human-readable prose across dozens of markdown files.

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
   Govern multi-agent repository lifecycles (Change Requests, Worktrees, PR Watches, Review Sagas, Evaluation Runners, Decision Ratification, QA Staging Acceptance Runs, Automated TDD Execution, Distributed Component Choreography, Architectural Trade-off Analysis).
   Governed exclusively by this standard.
2. **Implementation Workflows (`framework/layers/08_IPLAN/IPLAN-SWF-TEMPLATE.yaml`)**:
   Govern codebase mutation, test file creation, and execution-time saga compensation.
   Governed by [`IPLAN_WORKFLOW_STANDARD.md`](IPLAN_WORKFLOW_STANDARD.md).
3. **Behavioral Acceptance Workflows (`framework/layers/04_BDD/BDD-SWF-TEMPLATE.yaml`)**:
   Govern complex, multi-step stateful user journeys and scenario-level saga rollback.
   Governed by [`framework/layers/04_BDD/BDD_WORKFLOW_STANDARD.md`](../layers/04_BDD/BDD_WORKFLOW_STANDARD.md).
4. **Test-Driven Workflows (`framework/layers/07_TDD/TDD-SWF-TEMPLATE.yaml`)**:
   Govern multi-tier test execution, fixture provisioning, and teardown compensation sagas.
   Governed by [`framework/layers/07_TDD/TDD_WORKFLOW_STANDARD.md`](../layers/07_TDD/TDD_WORKFLOW_STANDARD.md).
5. **Technical Specification Workflows (`framework/layers/06_SPEC/SPEC-SWF-TEMPLATE.yaml`)**:
   Govern distributed component interactions, event choreography, asynchronous callbacks, and distributed transaction saga compensations.
   Governed by [`framework/layers/06_SPEC/SPEC_WORKFLOW_STANDARD.md`](../layers/06_SPEC/SPEC_WORKFLOW_STANDARD.md).
6. **Architectural Decision Workflows (`framework/layers/05_ADR/ADR-SWF-TEMPLATE.yaml`)**:
   Govern multi-candidate trade-off analysis, MCDA utility scoring, stakeholder RFC review loops, and rejection archival sagas.
   Governed by [`framework/layers/05_ADR/ADR_WORKFLOW_STANDARD.md`](../layers/05_ADR/ADR_WORKFLOW_STANDARD.md).
7. **Requirements Validation Workflows (`framework/layers/03_EARS/EARS-SWF-TEMPLATE.yaml`)**:
   Govern requirement dependency DAG resolution, syntax verification, cross-requirement conflict detection, BDD-readiness gating, and invalidation compensation sagas.
   Governed by [`framework/layers/03_EARS/EARS_WORKFLOW_STANDARD.md`](../layers/03_EARS/EARS_WORKFLOW_STANDARD.md).
8. **Product Requirements Decomposition Workflows (`framework/layers/02_PRD/PRD-SWF-TEMPLATE.yaml`)**:
   Govern multi-container feature decomposition, RICE prioritization, acceptance threshold validation, and requirement invalidation compensation sagas.
   Governed by [`framework/layers/02_PRD/PRD_WORKFLOW_STANDARD.md`](../layers/02_PRD/PRD_WORKFLOW_STANDARD.md).
9. **Business Requirements Validation Workflows (`framework/layers/01_BRD/BRD-SWF-TEMPLATE.yaml`)**:
   Govern strategic theme ingestion, value stream mapping, quantitative ROI evaluation, executive steering committee reviews, and strategic invalidation compensation sagas.
   Governed by [`framework/layers/01_BRD/BRD_WORKFLOW_STANDARD.md`](../layers/01_BRD/BRD_WORKFLOW_STANDARD.md).

## 2. Directory Structure & File Conventions

All declarative workflow definitions reside in `framework/governance/workflows/`:

```
framework/governance/
├── workflows/
│   ├── chg-request-flow.sw.yaml              # Change classification, gates & landing
│   ├── seed-to-module-decomposition.sw.yaml  # 5-step seed to C4-L2 module flow
│   ├── worktree-pr-lifecycle.sw.yaml         # Worktree isolation, PR watch & cleanup
│   ├── eval-verification-run.sw.yaml         # Layer 10 multi-tier test execution & verification
│   ├── review-remediation-flow.sw.yaml       # Multi-agent quality loop & 3-strike remediation saga
│   ├── decision-ratification-flow.sw.yaml    # Decision proposal, review, founder sign-off & lock
│   ├── bdd-acceptance-run.sw.yaml            # Layer 04 QA staging BDD acceptance test suite execution
│   ├── tdd-test-execution.sw.yaml            # Layer 07 automated test suite execution & fixture rollback
│   ├── spec-choreography-contract.sw.yaml    # Layer 06 distributed component interaction & choreography contract
│   ├── adr-decision-analysis.sw.yaml         # Layer 05 architectural trade-off analysis & multi-criteria evaluation
│   ├── ears-requirements-validation.sw.yaml  # Layer 03 requirements syntax validation, dependency DAG resolution & BDD-readiness gating
│   ├── prd-feature-decomposition.sw.yaml     # Layer 02 product feature decomposition, RICE prioritization & threshold gating
│   └── brd-business-validation.sw.yaml       # Layer 01 business requirements validation, value stream mapping & ROI gating
│
├── GOVERNANCE_WORKFLOW_STANDARD.md           # This normative standard
├── CHG_REQUEST_FLOWS.md                      # Prose guide embedding chg-request-flow graph
├── SEED_TO_MODULE_DECOMPOSITION.md           # Prose guide embedding decomposition graph
├── WORKTREE_FLOW.md                          # Prose guide embedding worktree graph
├── REVIEW_REMEDIATION_FLOW.md                # Prose guide embedding review-remediation graph
├── REVIEW_SAGA.md                            # Review saga lifecycle contract
└── DECISION_WORKFLOW.md                      # Decision workflow embedding ratification graph
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

Unconditional loops without terminating edge conditions or retry limits are prohibited.

### Rule 3: Discrete Gate Verification (`type: switch`)
All quality gates and transition approvals must be represented as discrete `switch` states
evaluating unambiguous boolean conditions (e.g., `"${ .eval_verdict == 'PASS' }"`).
Conditional branches must explicitly define a `defaultCondition` preventing deadlocks.

### Rule 4: Parallelism for Independent Reviews (`type: parallel`)
Multi-agent reviews (e.g., simultaneous checks by Architect, Security, and Auditor) must be
modeled as `parallel` states with `completionType: allOf` to minimize latency while guaranteeing
full consensus.

### Rule 5: Human-in-the-Loop Callback Gates (`type: callback`)
States requiring explicit human confirmation (e.g. founder approval for releases per `AGENTS.md`,
or destructive worktree cleanup approvals) must use the `callback` state pattern. Execution
suspends until a correlated external authorization event (`kind: consumed`) is received or an
`eventTimeout` expires:

```yaml
- name: AwaitFounderReleaseApproval
  type: callback
  action:
    name: NotifyFounderReleasePending
    functionRef:
      refName: sendReleaseApprovalRequest
  eventRef: FounderApprovalEvent
  timeouts:
    eventTimeout: "PT24H"
  transition: ProcessFounderDecision
```

### Rule 6: Rollback and Remediation Sagas (`compensatedBy`)
Destructive operations, task branch allocations, or worktree creation steps that fail downstream
validation must declare a compensating state using the `compensatedBy` attribute. This guarantees
clean environment restoration without orphaned branches or dirty state:

```yaml
- name: ProvisionWorktree
  type: operation
  compensatedBy: CleanupWorktreeSaga
  actions:
    - name: RunGitWorktreeAdd
      functionRef:
        refName: executeWorktreeAdd
  transition: RunFeatureImplementation
```

---

## 5. Execution Integration: LangGraph & Agent Runtimes

While the framework specification is runtime-neutral ([D-0013](DECISIONS.md)), any downstream
agent harness consuming this framework can convert `.sw.yaml` files into executable graphs:

```python
import yaml
from langgraph.graph import StateGraph, END

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

---

## 6. Multi-Tier Circuit Breakers (Anti-Infinite Loop System)

To guarantee that autonomous execution never enters an uncontrolled loop, exhausts compute, or cascades errors, any conforming multi-agent engine enforces six non-negotiable circuit breakers:

| Breaker | Threshold | Trigger Condition | System Action | Governing Framework Standard |
| :--- | :--- | :--- | :--- | :--- |
| **CB-1: Review-Fix Iteration Breaker** | Max 2 remediation passes | Pass 2 judge returns `REVISE` or `BLOCK` twice consecutively on the same step | **HALT.** Escalate to human founder with exact dissenting findings and proposed alternatives. | `REVIEW_REMEDIATION_FLOW.md`, `CI_AUTONOMOUS_PR_STANDARD.md` Invariant 4 |
| **CB-2: CI Polling Deadline** | 15 minutes (60 cycles @ 15s) | Required status checks remain pending, queued, or running after 15 minutes | **HALT.** Abort polling, diagnose stuck workflow run via platform API, and alert human founder. | `CI_AUTONOMOUS_PR_STANDARD.md` Invariant 3, `AGENTS.md` §Watching your PR |
| **CB-3: CI Failure Remediation Cap** | Exactly 1 retry attempt | Required CI status checks fail on pull request | **REMEDIATE ONCE.** Pull run logs, apply targeted fix on feature branch, re-verify locally, push commit. If checks fail a second time, **HALT** immediately. | `AGENTS.md` §Non-negotiables, `CI_AUTONOMOUS_PR_STANDARD.md` Invariant 4 |
| **CB-4: Monotonic Phase State Invariant** | 0 regressions allowed | Attempt to modify a `Completed` step or regress CHG/IPLAN status | **FATAL REJECT.** Completed steps are immutable. Post-implementation defects must be addressed via new follow-up issue/CHG. | `DOC_GOVERNANCE_CORE.md` §3.3 (CHG-L017), `CHG_REQUEST_FLOWS.md` |
| **CB-5: Git Divergence & Conflict Lock** | 0 force-pushes allowed | Remote integration branch diverges during feature work (`DIRTY` / `CONFLICTING`) | Merge cleanly from updated `origin/dev`. Autonomous resolution authorized for Class 1 (Deterministic/Additive) conflicts. If Class 2 (Semantic/Architectural) conflicts occur, abort merge and **HALT** immediately. | `CI_AUTONOMOUS_PR_STANDARD.md` Invariant 5 |
| **CB-6: Scope Boundary Escort** | Out-of-manifest file edit | Implementation requires touching files not listed in IPLAN `file_manifest` | **HALT.** Do not write to unauthorized files. Update IPLAN or submit feedback issue. | `DOC_GOVERNANCE_CORE.md` §3.13 (IPLAN Gate), `WORKTREE_FLOW.md` |

---

## 7. Layer 10 Terminal Lifecycle Gate Contract

Change Requests and Implementation Plans conclude deterministically through the Layer 10 Evaluation gate:
1. **Deployable Changes (Code, Schemas, Configurations, Runtime Touches):**
   - **IPLAN Transition (`Completed` → `Verified`):** Permitted only upon the generation and commit of an authentic Layer 10 Terminal Evaluation Report (`docs/sdd/10_EVAL/EVAL-{NN}/reports/EVAL-{NN}-RPT-001.yaml` or equivalent) with `verdict: PASS` and zero failed test cases.
   - **CHG Transition (`Implemented` → `Completed`):** Permitted only when the terminal evaluation report is committed and merged into the integration branch (`dev`).
2. **Non-Deployable Changes (Documentation, SDD-Only, Governance, Tooling Scripts):**
   - Non-deployable changes bypass live deployment and evaluation reports (`CHG_REQUEST_FLOWS.md` §3.3 rule 10).
   - Closes directly via a clean governance sync pull request advancing status to `Completed` once static linting (`chg_lint`, pre-commit) and dual independent review passes succeed.

---

## 8. Tripartite Engineering Architecture & Separation of Concerns

Conforming multi-agent project implementations separate software delivery responsibilities across three autonomous, non-overlapping engineering roles:

| Engineering Role | Primary Mandate | Allowed File Mutations | Prohibited Actions |
|---|---|---|---|
| **DEV (Developer / Author)** | Implements features, refactors architecture, fixes code defects | Production codebase, internal unit test fixtures, authorized IPLAN `file_manifest` targets | Approving own changes, self-merging without green status checks, modifying QA acceptance suites |
| **SDET (Software Development Engineer in Test)** | Authors automated test harnesses, mock fixtures, synthetic test runners, and performance benchmarks | Test suites (`tests/*`), test scaffolding, CI testing scripts, benchmark harnesses | Directly mutating production application logic to force tests to pass |
| **QA (Quality Assurance & Acceptance Verifier)** | Executes independent user-journey acceptance tests, end-to-end browser scenarios, compliance audits | Verification reports, test run logs, QA issue comments, failure reproduction artifacts | **HARD BLOCK: Zero production or test code mutations** (QA observes, tests, and reports; never writes fixes) |

### 8.1 Strict Non-Code-Modifying Invariant (HARD BLOCK for QA)

To prevent conflict of interest, test dilution, and cosmetic patching:
1. **Observation & Verification Only:** QA personas and acceptance runners operate in a read-only capacity with respect to production codebases and test harness implementation.
2. **Zero In-Place Fixes:** When an acceptance test fails, QA agents MUST NOT modify code or adjust assertions to mask the defect.
3. **Defect Ticket & Repro Generation:** QA agents capture structured reproduction evidence (logs, DOM snapshots, network traces, failing payloads), formulate an actionable defect finding, and surface it back to the DEV persona or open a governed issue.

### 8.2 Mandatory Post-Merge Issue Closure & Implementation Report Contract

When a pull request merges into the target integration branch (`dev`), the delivering agent MUST close the loop by posting an explicit Implementation and Verification Report on the associated tracking issue before closing it:

1. **Deterministic Close Reference:** PR descriptions must carry explicit `Closes #N` or `Fixes #N` keywords for each resolved issue.
2. **Post-Merge Closing Comment:** The delivering agent must post a closing comment to the issue documenting:
   - **Delivered Scope:** Concrete summary of implemented features or bug fixes.
   - **Verification Evidence:** Green CI run links or IDs, test execution summary, and merge commit SHA on `origin/dev`.
   - **Artifact Links:** Clickable links to updated SDD artifacts (SPEC, IPLAN, EVAL report).
3. **Safe Publishing Mechanics:** Agents must author comment bodies via files (`gh issue comment <N> --body-file <file>`), verifying that the comment published with non-zero length.

## 9. Review Log

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
- **2026-10-05 — Pass 3 (Step 3 Quality Loops & Decision Ratification)**:
  - *Gap found*: Quality loop (`REVIEW_REMEDIATION_FLOW.md`) and decision lifecycle (`DECISION_WORKFLOW.md`) lacked registered CNCF state machine models.
  - *Fix*: Registered `review-remediation-flow.sw.yaml` and `decision-ratification-flow.sw.yaml` in Section 2 and updated Rule 5/6 references.
- **2026-10-05 — Pass 4 (Step 4 BDD Acceptance Execution Runner)**:
  - *Gap found*: QA staging BDD acceptance execution runner lacked registration in governance workflow standard.
  - *Fix*: Registered `bdd-acceptance-run.sw.yaml` in Section 2 and added domain separation pointer to `BDD_WORKFLOW_STANDARD.md`.
- **2026-10-05 — Pass 5 (Step 6 SPEC Distributed Choreography Standard)**:
  - *Gap found*: Distributed service interaction sequencing, event choreography, and saga rollback compensation lacked registration in governance workflow catalog.
  - *Fix*: Registered `spec-choreography-contract.sw.yaml` in Section 2, added Layer 06 SPEC workflow domain separation entry in Section 1, and documented Pass 5 in Review Log.
- **2026-10-05 — Pass 6 (Step 7 ADR Decision Analysis & MCDA Scoring Standard)**:
  - *Gap found*: Architectural candidate trade-off evaluation, multi-criteria decision analysis (MCDA), stakeholder RFC review loops, and rejection archival sagas lacked formal CNCF Serverless Workflow modeling.
  - *Fix*: Registered `adr-decision-analysis.sw.yaml` in Section 2, added Layer 05 ADR workflow domain separation entry in Section 1, and documented Pass 6 in Review Log.
- **2026-10-05 — Pass 7 (Step 8 EARS Requirements Validation & Dependency DAG Standard)**:
  - *Gap found*: Requirements syntax verification, dependency DAG resolution, conflict detection, and BDD-readiness gating lacked formal CNCF Serverless Workflow modeling.
  - *Fix*: Registered `ears-requirements-validation.sw.yaml` in Section 2, added Layer 03 EARS workflow domain separation entry in Section 1, and documented Pass 7 in Review Log.
- **2026-10-05 — Pass 9 (Step 10 BRD Business Validation & Value Stream Standard)**:
  - *Gap found*: Strategic theme ingestion, value stream mapping, quantitative ROI evaluation, and executive steering committee review callbacks lacked formal CNCF Serverless Workflow modeling.
  - *Fix*: Registered `brd-business-validation.sw.yaml` in Section 2, added Layer 01 BRD workflow domain separation entry in Section 1, and documented Pass 9 in Review Log.
- **2026-10-05 — Pass 8 (Step 9 PRD Product Decomposition & Feature Prioritization Standard)**:
  - *Gap found*: Multi-container feature decomposition, RICE prioritization, and quantitative acceptance threshold validation lacked formal CNCF Serverless Workflow modeling.
  - *Fix*: Registered `prd-feature-decomposition.sw.yaml` in Section 2, added Layer 02 PRD workflow domain separation entry in Section 1, and documented Pass 8 in Review Log.
- **2026-10-06 — Pass 10 (Autonomous Circuit Breakers & Terminal EVAL Gate)**:
  - *Gap found*: Circuit breaker thresholds (review-fix caps, CI polling timeouts, CI failure retries, git conflict classes, monotonic step locks) were dispersed across multiple documents without a unified operational matrix.
  - *Fix*: Codified Section 6 Multi-Tier Circuit Breakers Matrix (CB-1 through CB-6) and formalized Section 7 Layer 10 Terminal Lifecycle Gate Contract.
- **2026-10-06 — Pass 11 (Tripartite Separation of Concerns & Issue Closure Contract)**:
  - *Gap found*: Lack of clear boundaries between DEV, SDET, and QA personas, creating risks of QA modifying production code during acceptance test runs. Missing formal contract for post-merge issue closure reports.
  - *Fix*: Codified Section 8 Tripartite Engineering Architecture with strict non-code-modifying invariant for QA, and formalized Section 8.2 Mandatory Post-Merge Issue Closure & Implementation Report Contract.
