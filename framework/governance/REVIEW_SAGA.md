# Review Saga — lifecycle contract for the review-team's create→review→revise loop

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-10-07 |
| Author | Framework Maintainer |
| Framework Version | 0.89.0 |

`REVIEW_TEAM.md` defines *what* the review team is (crew of personas, blackboard,
synthesizer, scoring/gate, partial-crew resilience). This document defines the
**lifecycle saga**: the state machine, transition table, journal schema, and
break-circuit policy that govern the durable progression of a review run from
PREPARED to CLOSED (or to one of the terminal failure states). It is a **light
contract** — engine-agnostic — and is the framework's authority on observable
lifecycle behavior. Each platform binds the contract to its own runtime.

The contract was generalized from a working reference implementation that
predated this spec section, then promoted into framework spec so that any
conforming engine — saga runtime, prompt-orchestration engine, or another
mechanism — can implement it while exposing the same observable lifecycle. The
project's parity goal is **lifecycle-behavior parity**;
this document is its load-bearing definition.

Executable CNCF Serverless Workflow definitions for this saga lifecycle are
formally codified in `framework/governance/REVIEW_WORKFLOW_STANDARD.md`,
`framework/governance/workflows/review-remediation-flow.sw.yaml`, and the per-layer
review workflows in `framework/governance/workflows/review/` (`REV-01-BRD` through `REV-09-CHG`).

## States

The saga's run-level and branch-level states share one state machine. Each
state-typed value belongs to either the **run** (the overall review run) or to
a **branch** (one persona's dispatch within the run). State names are
unambiguous about which scope they apply to.

| State | Scope | Meaning |
|---|---|---|
| `PREPARED` | run | Saga created; no phase started; personas requested are recorded. |
| `FANOUT_STARTED` | run | Dispatcher began fanning out the crew; per-branch states are now meaningful. |
| `BRANCH_RUNNING` | branch | A persona dispatch is in flight (sub-task or saga branch executor). |
| `BRANCH_COMPLETED` | branch | The branch returned a conforming persona-output record to its slot. |
| `BRANCH_FAILED` | branch | The branch returned an error or non-conformant output. |
| `BRANCH_COMPENSATING` | branch | The branch failed and compensation is in progress (retry, alternative dispatch, or graceful skip). |
| `FANIN_REDUCED` | run | The synthesizer's deterministic reduce produced the unified-report core (findings + score + coverage). |
| `SYNTHESIZED` | run | The synthesizer's narrative (advisory) layer is produced. |
| `ESCALATED` | run | Terminal. The run could not complete; human review is required. |
| `CLOSED` | run | Terminal. The run completed cleanly. |
| `PARTIAL_TIMEOUT` | run | Terminal-this-process. The break-circuit (or hard timeout) fired; the journal is durably written and a future invocation may resume from this checkpoint. |

## Transition table

Engine-agnostic. Engines MAY enforce transitions preemptively (runtime code)
or cooperatively (prompts that direct an LLM to validate against this table
before writing the journal).

| From | Allowed next states |
|---|---|
| `PREPARED` | `FANOUT_STARTED`, `PARTIAL_TIMEOUT` |
| `FANOUT_STARTED` | `BRANCH_RUNNING`, `PARTIAL_TIMEOUT` |
| `BRANCH_RUNNING` | `BRANCH_COMPLETED`, `BRANCH_FAILED`, `PARTIAL_TIMEOUT` |
| `BRANCH_FAILED` | `BRANCH_COMPENSATING`, `ESCALATED`, `BRANCH_COMPLETED` |
| `BRANCH_COMPENSATING` | `BRANCH_RUNNING`, `ESCALATED` |
| `BRANCH_COMPLETED` | `FANIN_REDUCED`, `PARTIAL_TIMEOUT` |
| `FANIN_REDUCED` | `SYNTHESIZED`, `PARTIAL_TIMEOUT` |
| `SYNTHESIZED` | `CLOSED`, `FANOUT_STARTED`, `ESCALATED`, `PARTIAL_TIMEOUT` |
| `ESCALATED` | (terminal) |
| `CLOSED` | (terminal) |
| `PARTIAL_TIMEOUT` | (terminal-this-process; future invocations resume from this journal state by re-entering one of the allowed source states) |

## Journal schema

Each run produces a durable journal file. The journal is the authoritative
record of the saga's progression and the basis of lifecycle conformance
verification. Every conforming implementation must produce a journal matching `saga.schema.json`
(this file's companion).

### Required fields

| Field | Type | Description |
|---|---|---|
| `review_run_id` | string | 12-char-or-longer run identifier. Implementations MAY use deterministic IDs derived from the artifact + persona set + time bucket, or UUIDs. |
| `artifact_id` | string | Short ID of the artifact under review (`BRD-01`, `PRD-02`, …). The format follows `ID_NAMING_STANDARDS.md` §"Format" and the authoritative `../registry/LAYER_REGISTRY.yaml` `id_patterns.document` pattern (`^[A-Z]+-\d{2,}$` — two-or-more digits; two-digit is the common case). |
| `layer` | string | One of the framework layers (`01_BRD`..`08_IPLAN`), the `09_CHG` change-management overlay, or `10_EVAL` — matching the `layer` enum in `saga.schema.json`. |
| `personas_requested` | array of strings | The crew dispatched, drawn from `REVIEW_CREWS.yaml` personas registry. |
| `status` | string | Current run-level state from the table above. |
| `iteration` | integer | `1`-based create→review→revise iteration counter. |
| `created_at` | string (ISO 8601 UTC) | Run creation timestamp. |
| `updated_at` | string (ISO 8601 UTC) | Last journal write timestamp. |
| `branches` | object | Map of persona name → branch sub-object (schema below). |
| `transitions` | array of objects | Append-only log of state changes (schema below). |
| `compensation_actions` | array of objects | Append-only log of compensation events (schema below). |

### Optional fields

| Field | Type | Notes |
|---|---|---|
| `document_fingerprint` | string | An implementation MAY populate as a content hash. |
| `document_path` | string | An implementation MAY populate as an absolute path. |
| `current_phase` | string | Implementation enrichment for cooperative-enforcement engines: `draft` / `review` / `fixer` / `re-review` / `reduce` / `synthesize`. Helps resumability after `PARTIAL_TIMEOUT`. |
| `retry_count` | integer | Defaults to 0; useful for resumable retries. |

Implementations MAY add additional extension fields beyond these at the **top
level** and within `branches[<persona>]` / `compensation_actions[]` entries
(the schema declares `additionalProperties: true` for those). The
`transitions[]` entries are the **load-bearing parity artifact** — the
schema declares `additionalProperties: false` for transition entries to
prevent engines from drifting on the journal's audit trail. If an engine
genuinely needs to extend transitions (e.g., to carry a saga correlation
ID across distributed branches), that extension goes through a follow-up
CHG to the schema, not a unilateral implementation addition.

### `branches[<persona>]` sub-object

Required: `branch_id` (string), `status` (one of the branch-scoped states),
`attempt` (integer, 0-based).
Optional: `started_at`, `ended_at` (ISO 8601 UTC), `error_code` (string).

### `transitions[]` entry

Required: `ts` (ISO 8601 UTC), `to` (state string), `scope` (string: `"run"` or `"branch:<persona>"`) — matching the schema's required `["ts", "to", "scope"]`.
Optional: `from` (state string, or null on the initial entry).

### `compensation_actions[]` entry

Required: `ts` (ISO 8601 UTC), `branch` (persona name), `reason` (string —
the `error_code` or a human-readable cause), `action` (one of `retry`,
`skip`, `escalate`).

## Break-circuit policy

Cooperative graceful-exit mechanism: every orchestrator that participates in
the saga MUST monitor its own wall-clock against an implementation-defined
SOFT_DEADLINE that sits **below** the implementation's hard timeout (OS
signal, runtime kill, or equivalent), with a minimum buffer of 300s. At
checkpoint boundaries (per-orchestrator-role table below), the orchestrator checks
elapsed time and exits cleanly with status `PARTIAL_TIMEOUT` if the soft
deadline has been crossed.

### Checkpoint boundaries by orchestrator role

| Orchestrator role | Checkpoint boundaries |
|---|---|
| Layer autopilot (create→review→revise loop) | Between the create / review / fixer / re-review phases of the outer loop. |
| Layer audit (multi-persona review) | After all lens dispatches return; before invoking the synthesizer. |
| Layer fixer (multi-lens validation) | Between multi-lens validation dispatches (each blocking finding's per-lens validation is one boundary). |
| Review-team dispatcher (the shared fan-out) | After each crew fan-out completes; before the reduce step. |
| Saga runtime (preemptive engines) | Per-branch via implementation-defined per-persona timeout configuration; hard-timeout-during-branch maps to `PARTIAL_TIMEOUT`. |

### Behavior at checkpoint

```text
1. Read elapsed wall-clock since orchestrator start.
2. If elapsed > SOFT_DEADLINE:
   a. Do NOT dispatch the next phase / lens / fix-validation.
   b. Append a transitions[] entry: from <current_state> → PARTIAL_TIMEOUT.
   c. Update status: PARTIAL_TIMEOUT; set current_phase if applicable.
   d. Exit cleanly (subprocess exit 0 / runtime non-error termination).
3. If elapsed ≤ SOFT_DEADLINE: proceed with the next phase normally.
```

If the orchestrator ignores the break-circuit (cooperative failure) and the
hard timeout fires, the journal records the last successful checkpoint
state — NOT `PARTIAL_TIMEOUT`. Both outcomes are valid graceful-degradation
states; conformance accepts either as evidence the journal captured useful
state.

### Soft-deadline values

The spec does not prescribe specific numbers — engines pick values
appropriate to their runtime. The contract is that SOFT_DEADLINE ≤
HARD_TIMEOUT − 300s. Per-platform numeric choices are documented in each
platform's own engineering docs (not in this engine-agnostic spec).

## Framework spec-version declaration

A consuming implementation records which framework spec version it conforms
to (the `framework/VERSION` value at the time of adoption) in its own
engineering docs — a declaration of intent, NOT a claim of complete
implementation mid-delivery. Implementation completeness against the spec is
verified by behavior-specific conformance tests (e.g., the
saga-lifecycle-parity test at
`tests/conformance/test_saga_lifecycle_parity.py`), not by version-string
equality.

This declaration-vs-implementation distinction allows a multi-phase adoption
where the spec changes in one phase and consumer implementations land later.

## Enforcement asymmetry — honest caveat

Engines MAY enforce this contract via different mechanisms:

- **Preemptive enforcement.** Runtime code validates transitions
  (`can_transition` raises on invalid transition) and serializes state
  changes through a single runtime layer that owns the journal file.
- **Cooperative enforcement.** Orchestrator prompts direct an LLM to
  validate transitions against this document's table before writing the
  journal; OS-level signals are the hard floor.

Same observable lifecycle, different enforcement. Conformance tests check
the observable artifact (the journal file's schema + state machine
adherence + greppable break-circuit invariant), not the enforcement
mechanism. Binding of these enforcement modes is documented in the
consumer's own engineering documentation, not in this engine-agnostic spec.

## Cross-references

- `REVIEW_TEAM.md` — the operational semantics (create / review / remediate)
  this saga lifecycle wraps. The loop's WHAT lives there; the loop's HOW
  (states, transitions, journal) lives here.
- `REVIEW_CREWS.yaml` — the per-layer crew compositions referenced via
  `personas_requested`.
- `REVIEW_REMEDIATION_FLOW.md` — the trigger points (`on_author`,
  `pre_promotion`, `pre_merge`, `on_gate_fail`) that fire the loop the
  saga records.
- `REVIEW_WORKFLOW_STANDARD.md` — graph-based review flow specification and traversal taxonomy.
- `workflows/review-remediation-flow.sw.yaml` — canonical CNCF Serverless Workflow state machine.
- `workflows/review/` — per-layer review & remediation workflows (`REV-01-BRD` through `REV-09-CHG`).
- `GOVERNANCE_WORKFLOW_STANDARD.md` — normative specification for CNCF Serverless Workflow adoption.
- `DIAGRAM_STANDARDS.md` — visualization standards and Mermaid syntax for governance workflows.
- `SECURITY_REVIEW.md` — untrusted-input handling for content in the
  blackboard (separate concern from saga state).
- `saga.schema.json` — formal JSON Schema for the journal.
- D-0031 (see the D-series annex in `DECISIONS.md`) — the
  supersession decision that brought this contract into the framework spec.
- D-0005 (see the D-series annex in `DECISIONS.md`) — the prior
  decision that one engine would not port the saga, superseded in scope
  (its blackboard-for-crew-state reasoning remains authoritative).
