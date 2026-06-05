# SAGA-PARITY-001 Phase 1 — Spec design + D-0031 supersession

| Field      | Value                                                     |
|------------|-----------------------------------------------------------|
| Task       | SAGA-PARITY-001-PHASE-1                                   |
| Parent     | SAGA-PARITY-001 (`plans/SAGA-PARITY-001-PLAN.md`, merged via PR #81 + Pass-4 amendments PR #82) |
| Depends on | CHAOS-SEC-SPLIT-001 (D-0030, merged); D-0005 (2026-05-26, to be superseded in scope by D-0031) |
| Status     | PLANNED — 2026-06-05T13:00:00Z                            |
| Feeds      | Phase 2 (plugin BRD impl), Phase 3 (Hermes alignment), Phase 4 (per-layer propagation) — all blocked until Phase 1 lands |
| Scope flag | **Framework-spec change** — CHG-gated; framework `0.12.0 → 0.13.0` |

## Objective

Implement Phase 1 of SAGA-PARITY-001: extract the engine-agnostic
review-saga lifecycle contract from Hermes' existing `saga_models.py` into
the framework spec, formalize the journal schema, supersede D-0005's
"no-saga-in-plugin" scope with D-0031, and reframe `docs/PARITY.md` to
state lifecycle-behavior parity as the project's parity contract.

This is **plan-only-then-impl**: this plan PR captures the concrete
design choices; the follow-up impl PR creates the files per the design.
After Phase 1 lands, both platforms declare conformance intent to spec
`0.13.0`, but neither has yet implemented the contract — that work
happens in Phase 2 (plugin) and Phase 3 (Hermes), gated on Phase 1.

## Scope

### In

1. **New file** `framework/governance/REVIEW_SAGA.md` — engine-agnostic
   saga lifecycle contract (state machine narrative + transition table +
   journal schema description + break-circuit policy contract +
   FRAMEWORK_SPEC_VERSION semantics + enforcement-asymmetry caveat).
2. **New file** `framework/governance/saga.schema.json` — formal JSON
   Schema for the per-run saga journal file, with required vs optional
   field declarations per the parent plan's §"Field requirement matrix"
   (G24).
3. **Edit** `framework/governance/REVIEW_TEAM.md` — add a single
   one-line `> See also` cross-reference to REVIEW_SAGA.md from
   §Operations §Create and §Resilience. No content duplication (G23).
4. **Edit** `framework/VERSION` — `0.12.0 → 0.13.0` (CHG-gated bump).
5. **Edit** `plans/DECISIONS.md` — add D-0031 entry (text below);
   preserve D-0005 verbatim (just appended with a supersession-pointer
   line at the bottom of D-0005's entry).
6. **Edit** `docs/PARITY.md` — fill in the previously-deferred "Saga
   lifecycle" comparison row + the second parity-proof bullet (the new
   `test_saga_lifecycle_parity.py` reference) + the
   enforcement-asymmetry caveat paragraph. (Most reframing landed in
   PR #81; this finishes the parts that depended on REVIEW_SAGA.md
   existing.)
7. **Edit** `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` —
   `0.11.3` (current local snapshot) is already `0.12.0`; set to
   `0.13.0`.
8. **Edit** `platforms/hermes/FRAMEWORK_SPEC_VERSION` — `0.12.0 → 0.13.0`.
9. **Edit** project `CHANGELOG.md` — entry under `[Unreleased]`
   documenting framework `0.13.0` and the lifecycle-parity goal.
10. **Edit** `platforms/claude-code-plugin/CHANGELOG.md` — short
    entry noting `FRAMEWORK_SPEC_VERSION` bump and intent to conform.
11. **Edit** `docs/TAGGING.md` — add a `framework/v0.13.0` release row.
12. **Run** `tools/sync-plugin-framework.sh` — re-sync the plugin's
    bundled `framework/` copy to include REVIEW_SAGA.md + saga.schema.json.

### Out (deferred to later phases)

- **Plugin implementation of saga.json + Bash subprocess + break-circuit
  policy** — Phase 2.
- **Hermes `transitions: list[dict]` field + `PARTIAL_TIMEOUT` state +
  downstream consumer updates** — Phase 3.
- **Cross-platform conformance test** `test_saga_lifecycle_parity.py` —
  Phase 3 (Phase 1 declares the contract; the test is added once Hermes
  has implemented + plugin's BRD proof has fixtures).
- **Per-layer plugin propagation** (PRD..IPLAN) — Phase 4.
- **Any plugin own-VERSION bump** (`platforms/claude-code-plugin/VERSION`
  stays at 0.5.x; Phase 2 bumps it).
- **Any Hermes own-VERSION bump** (`platforms/hermes/VERSION` stays at
  0.1.1; Phase 3 patch-bumps it).

## Approach — concrete content designs

### Design 1 — `framework/governance/REVIEW_SAGA.md`

Proposed full content (impl-ready; the impl PR can paste this directly):

````markdown
# Review Saga — lifecycle contract for the review-team's create→review→revise loop

`REVIEW_TEAM.md` defines *what* the review team is (crew of personas, blackboard,
synthesizer, scoring/gate, partial-crew resilience). This document defines the
**lifecycle saga**: the state machine, transition table, journal schema, and
break-circuit policy that govern the durable progression of a review run from
PREPARED to CLOSED (or to one of the terminal failure states). It is a **light
contract** — engine-agnostic — and is the framework's authority on observable
lifecycle behavior. Each platform binds the contract to its own runtime.

The contract was extracted from Hermes' existing `saga_models.py` and
`saga_journal.py` implementations (which predated this spec section) and
generalized so the Claude Code plugin and any future engine can implement it
via different mechanisms while exposing the same observable lifecycle. The
project's parity goal is **lifecycle-behavior parity** (per `docs/PARITY.md`);
this document is its load-bearing definition.

## States

The saga's run-level and branch-level states share one state machine. Each
state-typed value belongs to either the **run** (the overall review run) or to
a **branch** (one persona's dispatch within the run). State names are
unambiguous about which scope they apply to.

| State | Scope | Meaning |
|---|---|---|
| `PREPARED` | run | Saga created; no phase started; personas requested are recorded. |
| `FANOUT_STARTED` | run | Dispatcher began fanning out the crew; per-branch states are now meaningful. |
| `BRANCH_RUNNING` | branch | A persona dispatch is in flight (Task subagent or saga branch executor). |
| `BRANCH_COMPLETED` | branch | The branch returned a conforming persona-output record to its slot. |
| `BRANCH_FAILED` | branch | The branch returned an error or non-conformant output. |
| `BRANCH_COMPENSATING` | branch | The branch failed and compensation is in progress (retry, alternative dispatch, or graceful skip). |
| `FANIN_REDUCED` | run | The synthesizer's deterministic reduce produced the unified-report core (findings + score + coverage). |
| `SYNTHESIZED` | run | The synthesizer's narrative (advisory) layer is produced. |
| `ESCALATED` | run | Terminal. The run could not complete; human review is required. |
| `CLOSED` | run | Terminal. The run completed cleanly. |
| `PARTIAL_TIMEOUT` | run | Terminal-this-process. The break-circuit (or OS timeout) fired; the journal is durably written and a future invocation may resume from this checkpoint. |

## Transition table

Engine-agnostic. Adopted verbatim from Hermes' `saga_models.py:_ALLOWED_TRANSITIONS`,
extended with `PARTIAL_TIMEOUT` transitions per SAGA-PARITY-001 (D-0031).

| From | Allowed next states |
|---|---|
| `PREPARED` | `FANOUT_STARTED`, `PARTIAL_TIMEOUT` |
| `FANOUT_STARTED` | `BRANCH_RUNNING`, `PARTIAL_TIMEOUT` |
| `BRANCH_RUNNING` | `BRANCH_COMPLETED`, `BRANCH_FAILED`, `PARTIAL_TIMEOUT` |
| `BRANCH_FAILED` | `BRANCH_COMPENSATING`, `ESCALATED`, `BRANCH_COMPLETED` |
| `BRANCH_COMPENSATING` | `BRANCH_RUNNING`, `ESCALATED` |
| `BRANCH_COMPLETED` | `FANIN_REDUCED`, `PARTIAL_TIMEOUT` |
| `FANIN_REDUCED` | `SYNTHESIZED`, `PARTIAL_TIMEOUT` |
| `SYNTHESIZED` | `CLOSED` |
| `ESCALATED` | (terminal) |
| `CLOSED` | (terminal) |
| `PARTIAL_TIMEOUT` | (terminal-this-process; future invocations resume from this journal state by re-entering one of the allowed source states) |

## Journal schema

Each run produces a durable journal file. The journal is the authoritative
record of the saga's progression and the basis of lifecycle conformance
verification. Both platforms must produce a journal matching
`saga.schema.json` (this file's companion).

### Required fields

| Field | Type | Description |
|---|---|---|
| `review_run_id` | string | 16-char-or-longer deterministic ID per run (Hermes uses `deterministic_review_run_id`; platforms MAY use deterministic IDs or UUIDs). |
| `artifact_id` | string | Short ID of the artifact under review (`BRD-01`, `PRD-02`, …). |
| `layer` | string | One of the 8 framework layers (`01_BRD`..`08_IPLAN`). |
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
| `document_fingerprint` | string | Hermes populates as a content hash; plugin optional. |
| `document_path` | string | Hermes populates as an absolute path; plugin optional. |
| `current_phase` | string | Plugin enrichment: `draft` / `review` / `fixer` / `re-review` / `reduce` / `synthesize`. Helps resumability after `PARTIAL_TIMEOUT`. |
| `retry_count` | integer | Defaults to 0; useful for resumable retries. |

Platforms MAY add additional extension fields beyond these. The schema
declares `additionalProperties: true`.

### `branches[<persona>]` sub-object

Required: `branch_id` (string), `status` (one of the branch-scoped states),
`attempt` (integer, 0-based).
Optional: `started_at`, `ended_at` (ISO 8601 UTC), `error_code` (string).

### `transitions[]` entry

Required: `ts` (ISO 8601 UTC), `from` (state string or null on initial entry),
`to` (state string), `scope` (string: `"run"` or `"branch:<persona>"`).

### `compensation_actions[]` entry

Required: `ts` (ISO 8601 UTC), `branch` (persona name), `reason` (string —
the `error_code` or a human-readable cause), `action` (one of `retry`,
`skip`, `escalate`).

## Break-circuit policy

Cooperative graceful-exit mechanism: every orchestrator skill / runtime that
participates in the saga MUST monitor its own wall-clock against a
platform-defined SOFT_DEADLINE that sits **below** the platform's hard
timeout (OS SIGTERM or runtime kill signal), with a minimum buffer of 300s.
At checkpoint boundaries (per-skill-type table below), the orchestrator
checks elapsed time and exits cleanly with status `PARTIAL_TIMEOUT` if the
soft deadline has been crossed.

### Checkpoint boundaries by skill type

| Orchestrator skill / runtime | Checkpoint boundaries |
|---|---|
| `doc-*-autopilot` (plugin) | Between the create / review / fixer / re-review phases of the outer loop. |
| `doc-*-audit` (plugin) | After all lens dispatches return; before invoking the synthesizer. |
| `doc-*-fixer` (plugin) | Between multi-lens validation dispatches (each blocking finding's per-lens validation is one boundary). |
| `review-team` (plugin) | After each crew fan-out completes; before the reduce step. |
| Hermes' `saga_orchestrator` | Per-branch via `_resolve_review_branch_runtime` timeout from `persona_mappings.yaml`; SIGTERM-during-branch maps to PARTIAL_TIMEOUT. |

### Behavior at checkpoint

```text
1. Read elapsed wall-clock since skill / run start.
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

The spec does not prescribe specific numbers — platforms pick values
appropriate to their runtime:

- **Plugin**: SOFT_DEADLINE ≈ 1500s (with the OS `timeout 1800` providing
  the hard floor; 300s buffer).
- **Hermes**: per-branch timeouts come from `persona_mappings.yaml`; the
  buffer is configured per branch.

## FRAMEWORK_SPEC_VERSION semantics

Each platform carries two version files with distinct meanings:

| File | Meaning |
|---|---|
| `platforms/<name>/VERSION` | The platform's own SemVer (independent stream). |
| `platforms/<name>/FRAMEWORK_SPEC_VERSION` | The framework spec version the platform **declares intent to conform to** — NOT necessarily the version it has fully implemented mid-delivery. |

The conformance test `test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION`
enforces only string equality between `framework/VERSION` and each
platform's `FRAMEWORK_SPEC_VERSION`. Implementation completeness against the
spec is verified by behavior-specific tests (e.g.,
`test_saga_lifecycle_parity.py`).

This declaration-vs-implementation distinction allows a multi-phase delivery
where the spec changes in Phase N and platforms implement in Phases N+1,
N+2 — both platforms declare matching `FRAMEWORK_SPEC_VERSION` from Phase N
while their actual implementations land later.

## Enforcement asymmetry — honest caveat

The two platforms enforce this contract via different mechanisms:

- **Hermes**: preemptive enforcement in Python. `saga_models.py:can_transition`
  raises `ValueError` on invalid transitions; the runtime owns the journal
  and serializes state changes through `update_run_status` and
  `set_branch_state`.
- **Plugin**: cooperative enforcement via SKILL prompts. The orchestrator
  SKILL.md tells the LLM to validate transitions against this document's
  table before writing `saga.json`; OS-level `timeout` is the hard floor.

Same observable lifecycle, different enforcement. Conformance tests check
the observable artifact (the journal file's schema + state machine
adherence + greppable break-circuit invariant), not the enforcement
mechanism. This asymmetry is a known platform difference, not a parity
violation.

## Cross-references

- `REVIEW_TEAM.md` — the operational semantics (create / review / remediate)
  this saga lifecycle wraps. The loop's WHAT lives there; the loop's HOW
  (states, transitions, journal) lives here.
- `REVIEW_CREWS.yaml` — the per-layer crew compositions referenced via
  `personas_requested`.
- `REVIEW_REMEDIATION_FLOW.md` — the trigger points (`on_author`,
  `pre_promotion`, `pre_merge`, `on_gate_fail`) that fire the loop the
  saga records.
- `SECURITY_REVIEW.md` — untrusted-input handling for content in the
  blackboard (separate concern from saga state).
- `saga.schema.json` — formal JSON Schema for the journal.
- `plans/DECISIONS.md` D-0031 — the supersession decision that brought
  this contract into the framework spec.
- `plans/DECISIONS.md` D-0005 — the prior "no saga in plugin" decision,
  superseded in scope (its blackboard-for-crew-state reasoning remains
  authoritative).
````

### Design 2 — `framework/governance/saga.schema.json`

Proposed full content (impl-ready):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://aidoc-flow/framework/governance/saga.schema.json",
  "title": "Review Saga Journal",
  "description": "Engine-agnostic schema for the per-run review saga journal. Spec authority: framework/governance/REVIEW_SAGA.md.",
  "type": "object",
  "additionalProperties": true,
  "required": [
    "review_run_id",
    "artifact_id",
    "layer",
    "personas_requested",
    "status",
    "iteration",
    "created_at",
    "updated_at",
    "branches",
    "transitions",
    "compensation_actions"
  ],
  "properties": {
    "review_run_id": {
      "type": "string",
      "minLength": 12,
      "description": "Deterministic or UUID run identifier."
    },
    "artifact_id": {
      "type": "string",
      "pattern": "^[A-Z]+-[0-9]{2}$",
      "description": "Short artifact ID like BRD-01, PRD-02."
    },
    "layer": {
      "type": "string",
      "enum": [
        "01_BRD", "02_PRD", "03_EARS", "04_BDD",
        "05_ADR", "06_SPEC", "07_TDD", "08_IPLAN"
      ]
    },
    "personas_requested": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1
    },
    "status": {
      "type": "string",
      "enum": [
        "PREPARED", "FANOUT_STARTED",
        "BRANCH_RUNNING", "BRANCH_COMPLETED", "BRANCH_FAILED", "BRANCH_COMPENSATING",
        "FANIN_REDUCED", "SYNTHESIZED",
        "ESCALATED", "CLOSED", "PARTIAL_TIMEOUT"
      ]
    },
    "iteration": {
      "type": "integer",
      "minimum": 1
    },
    "created_at": {"type": "string", "format": "date-time"},
    "updated_at": {"type": "string", "format": "date-time"},
    "branches": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "additionalProperties": true,
        "required": ["branch_id", "status", "attempt"],
        "properties": {
          "branch_id": {"type": "string", "minLength": 8},
          "status": {
            "type": "string",
            "enum": [
              "BRANCH_RUNNING", "BRANCH_COMPLETED",
              "BRANCH_FAILED", "BRANCH_COMPENSATING"
            ]
          },
          "attempt": {"type": "integer", "minimum": 0},
          "started_at": {"type": ["string", "null"], "format": "date-time"},
          "ended_at": {"type": ["string", "null"], "format": "date-time"},
          "error_code": {"type": ["string", "null"]}
        }
      }
    },
    "transitions": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["ts", "to", "scope"],
        "properties": {
          "ts": {"type": "string", "format": "date-time"},
          "from": {"type": ["string", "null"]},
          "to": {"type": "string"},
          "scope": {
            "type": "string",
            "pattern": "^(run|branch:[a-z_]+)$"
          }
        }
      }
    },
    "compensation_actions": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": true,
        "required": ["ts", "branch", "reason", "action"],
        "properties": {
          "ts": {"type": "string", "format": "date-time"},
          "branch": {"type": "string"},
          "reason": {"type": "string"},
          "action": {
            "type": "string",
            "enum": ["retry", "skip", "escalate"]
          }
        }
      }
    },
    "document_fingerprint": {"type": "string"},
    "document_path": {"type": "string"},
    "current_phase": {
      "type": "string",
      "enum": ["draft", "review", "fixer", "re-review", "reduce", "synthesize"]
    },
    "retry_count": {"type": "integer", "minimum": 0}
  }
}
```

### Design 3 — D-0031 entry text

Proposed `plans/DECISIONS.md` insertion (newest-first; goes right after the
existing D-0030 entry):

```markdown
## D-0031 — Promote the review-saga lifecycle into the framework spec (supersedes D-0005's scope)

- **Date:** 2026-06-05T13:00:00Z
- **Decision:** Promote the review-team saga lifecycle (state machine,
  transitions, journal schema, compensation events, break-circuit policy)
  from a Hermes-internal implementation detail to an engine-agnostic
  framework-spec contract at `framework/governance/REVIEW_SAGA.md` +
  `framework/governance/saga.schema.json`. Both platforms (Hermes Python
  runtime and Claude Code plugin via SKILL prompts + saga.json + Bash
  subprocesses) implement the same observable lifecycle. Framework spec
  bumps `0.12.0 → 0.13.0` (CHG-gated).
- **Why:** Two converging pressures:
  1. **New failure-class evidence.** D-0005 (2026-05-26) decided "no saga
     in plugin" on the premise that "there is nothing to journal" — the
     plugin's Task subagents are harness-managed and the blackboard +
     coverage/quorum handles partial-crew state. The 2026-06-05 live BRD
     verification (CHAOS-SEC-SPLIT-001, D-0030) revealed a failure class
     D-0005 did not contemplate: **partial outer-loop state** when
     `doc-brd-autopilot` times out mid-iteration with a 5-lens crew +
     multi-lens fixer validation. There IS something to journal at the
     outer-loop level — phase progression, iteration count, transitions
     between phases. D-0005's "nothing to journal" assertion is now
     factually incomplete.
  2. **Lifecycle-behavior parity requirement.** The project's parity goal
     is now lifecycle-behavior parity (per `docs/PARITY.md`), not just
     output-shape parity. Achieving it requires both platforms to expose
     the same observable saga lifecycle. The framework spec is the only
     durable place to define that lifecycle without locking platforms
     into a single implementation.
- **Supersession scope:** D-0031 **supersedes D-0005's scope-narrowing
  premise** ("the plugin needs no saga"), NOT D-0005's reasoning about
  partial-crew state. The blackboard remains the durable medium for
  per-lens slot state; D-0031 adds a parallel saga.json journal for
  outer-loop phase state. D-0005's text is preserved verbatim with a
  trailing pointer to D-0031.
- **Notes:** Adopts Hermes' existing state names + transitions verbatim
  (PREPARED, FANOUT_STARTED, BRANCH_RUNNING, etc.) as the spec source —
  cheaper than renaming a working implementation; the names are general,
  not Hermes-coined. Adds `PARTIAL_TIMEOUT` as the only new state
  (covers break-circuit + SIGTERM cases on both platforms). Adds a
  top-level `transitions: list[dict]` field that Hermes does not have
  today; Phase 3 of SAGA-PARITY-001 adds it to Hermes' `SagaRunState`.
  The plugin implementation is cooperative (LLM honors the contract);
  Hermes' is preemptive (Python runtime enforces). Same observable
  lifecycle, different enforcement — documented as a known platform
  asymmetry in REVIEW_SAGA.md.
- **Implementation:** SAGA-PARITY-001 plan (`plans/SAGA-PARITY-001-PLAN.md`)
  organizes 4 phases. This decision lands in Phase 1 (this PR's parent).
  Phases 2-4 implement the contract on each platform.
```

### Design 4 — D-0005 amendment (preserve text, add trailing pointer)

Edit `plans/DECISIONS.md` D-0005 entry (the 2026-05-26 one, line 394 —
the duplicate D-0005 at line 884 is a separate decision and stays
untouched). Append at the end of the existing entry:

```markdown
- **Superseded in scope** by **D-0031** (2026-06-05). D-0005's
  blackboard-for-crew-state reasoning remains authoritative; D-0031
  extends the contract with an outer-loop saga.json journal to cover
  partial outer-loop state. See REVIEW_SAGA.md for the lifecycle
  contract.
```

(Do NOT modify D-0005's existing text.)

### Design 5 — `docs/PARITY.md` finalization

The PR #81 commit already reframed PARITY.md to lifecycle-behavior parity
language and added the saga-lifecycle comparison row + parity-proof
bullets. Phase 1's PARITY.md edits are minimal — fill in the remaining
forward-references now that REVIEW_SAGA.md exists:

- Verify the link `framework/governance/REVIEW_SAGA.md` in the parity
  contract paragraph resolves (no broken link in CI markdown-link
  check, if any).
- Confirm the Saga lifecycle row in the comparison table references
  `REVIEW_SAGA.md` (already does per PR #81).
- Update the status line at the top:

```diff
- > Status: as of project `v1.1.0` / `hermes/v0.1.1` /
- > `claude-code-plugin/v0.5.0` (framework spec `0.12.0`; ...
+ > Status: as of project `v1.1.0` / `hermes/v0.1.1` /
+ > `claude-code-plugin/v0.5.0` (framework spec `0.13.0`; ...
```

### Design 6 — `framework/governance/REVIEW_TEAM.md` one-liner cross-reference

Add to §"Operations §Create" (just before the `## Scoring, conflicts & the gate` heading):

```markdown
> See also `REVIEW_SAGA.md` for the saga state machine and journal contract
> that governs the durable progression of this loop.
```

Add to `## Resilience & security`:

```markdown
> Note: `REVIEW_SAGA.md` defines the partial-loop state contract
> (`PARTIAL_TIMEOUT`, break-circuit policy) that complements the
> partial-crew resilience described here.
```

That's it. REVIEW_TEAM.md does not duplicate REVIEW_SAGA.md content.

### Design 7 — Project + plugin CHANGELOG entries

Project `CHANGELOG.md` `[Unreleased]` block (before the
"### Framework Spec 0.11.3 → 0.12.0" entry CHAOS-SEC-SPLIT-001 added):

```markdown
### Changed — Framework Spec 0.12.0 → 0.13.0 (CHG-gated)

- **Review-saga lifecycle promoted to framework spec
  (SAGA-PARITY-001-PHASE-1, D-0031; PR #<this>).**
  - New: `framework/governance/REVIEW_SAGA.md` — engine-agnostic saga
    lifecycle contract (state machine, transitions, journal schema,
    break-circuit policy, FRAMEWORK_SPEC_VERSION semantics,
    enforcement-asymmetry caveat).
  - New: `framework/governance/saga.schema.json` — formal JSON Schema
    for the per-run saga journal.
  - Edit: `REVIEW_TEAM.md` adds two one-line `> See also`
    cross-references to REVIEW_SAGA.md (no content duplication).
  - D-0031 supersedes D-0005's scope-narrowing premise. D-0005's
    blackboard-for-crew-state reasoning remains authoritative.
  - `framework/VERSION`: `0.12.0 → 0.13.0`.
  - Both platforms declare `FRAMEWORK_SPEC_VERSION = 0.13.0` (intent
    to conform; implementation arrives in Phases 2 and 3 of
    SAGA-PARITY-001).
```

Plugin `CHANGELOG.md` `[Unreleased]` block:

```markdown
### Changed

- **`FRAMEWORK_SPEC_VERSION` bumped `0.12.0 → 0.13.0`
  (SAGA-PARITY-001 Phase 1, D-0031).** Plugin declares intent to
  conform to the new review-saga lifecycle contract introduced by the
  framework spec; full implementation (saga.json + Bash subprocess
  refactor + break-circuit policy in BRD-layer SKILLs) arrives in
  Phase 2 of SAGA-PARITY-001 with plugin v0.6.0. No plugin behavior
  change in this version.
```

### Design 8 — `docs/TAGGING.md` framework release row

Insert after the existing `framework/v0.12.0` entry (or create the
row if absent):

```markdown
| `framework/v0.13.0` | SAGA-PARITY-001-PHASE-1 close | Framework spec — review-saga lifecycle promoted to spec (REVIEW_SAGA.md + saga.schema.json); D-0031 supersedes D-0005's scope; both platforms declare intent to conform with full impl in Phases 2 and 3 |
```

## Step sequence

Concrete file-by-file edit list. Each step is small and independently
verifiable.

1. **Create** `framework/governance/REVIEW_SAGA.md` with the content
   from Design 1.
2. **Create** `framework/governance/saga.schema.json` with the schema
   from Design 2.
3. **Edit** `plans/DECISIONS.md`:
   - Insert D-0031 entry from Design 3 above D-0030.
   - Append the supersession-pointer line from Design 4 to the existing
     D-0005 entry (line 394).
4. **Edit** `framework/governance/REVIEW_TEAM.md` per Design 6 (two
   one-line cross-references).
5. **Edit** `framework/VERSION`: `0.12.0` → `0.13.0`.
6. **Edit** `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION`:
   `0.12.0` → `0.13.0`.
7. **Edit** `platforms/hermes/FRAMEWORK_SPEC_VERSION`: `0.12.0` →
   `0.13.0`.
8. **Edit** `docs/PARITY.md` per Design 5 (status line spec version,
   link verification).
9. **Edit** project `CHANGELOG.md` `[Unreleased]` block with Design 7
   project-side entry.
10. **Edit** `platforms/claude-code-plugin/CHANGELOG.md` `[Unreleased]`
    block with Design 7 plugin-side entry.
11. **Edit** `docs/TAGGING.md` with Design 8 release row.
12. **Run** `tools/sync-plugin-framework.sh` — re-syncs the plugin's
    `framework/` bundle so REVIEW_SAGA.md + saga.schema.json + updated
    REVIEW_TEAM.md are byte-identical with the canonical framework copy.
    Commits the resulting bundle changes.
13. **Verify** GATE-SPEC locally: `python3 tests/chg/spec_gate.py`
    should report green (`framework/VERSION` + `CHANGELOG.md` both
    updated).

## Verification

All Phase 1 verification is **free** (no live LLM calls; spec change
only).

### Step A — Static lint

```sh
env -u LD_LIBRARY_PATH pre-commit run --files \
  framework/governance/REVIEW_SAGA.md \
  framework/governance/saga.schema.json \
  framework/governance/REVIEW_TEAM.md \
  framework/VERSION \
  platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION \
  platforms/hermes/FRAMEWORK_SPEC_VERSION \
  docs/PARITY.md \
  CHANGELOG.md \
  platforms/claude-code-plugin/CHANGELOG.md \
  docs/TAGGING.md \
  plans/DECISIONS.md
```

Pass criteria: all hooks green (markdownlint, yaml-check, JSON syntax
check via `check-json`, etc.).

### Step B — Full conformance suite

```sh
env -u LD_LIBRARY_PATH python3 -m unittest discover -s tests/conformance
```

Pass criteria: 101/101 tests still pass. No new tests added in this
phase (the new lifecycle-parity test arrives in Phase 3).

Key tests this phase exercises:

- `test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION` — both
  platforms now declare `0.13.0`, matching `framework/VERSION`. Passes
  via the declaration-vs-implementation semantic.
- `test_plugin_framework_bundle.test_bundle_is_byte_identical` —
  the post-step-12 sync ensures byte equality.
- `test_review_team.*` — REVIEW_TEAM.md changes are additive
  one-liners; existing tests pass unchanged.

### Step C — GATE-SPEC (CHG-D1)

```sh
env -u LD_LIBRARY_PATH python3 tests/chg/spec_gate.py
```

Pass criteria: output `GATE-SPEC: framework/ change vs origin/main — VERSION + CHANGELOG updated, OK.`

### Step D — JSON Schema self-validation

```sh
python3 -c "
import json
schema = json.loads(open('framework/governance/saga.schema.json').read())
assert schema['\$schema'] == 'http://json-schema.org/draft-07/schema#'
assert 'review_run_id' in schema['required']
print('saga.schema.json: schema-self-validation OK')
"
```

Pass criteria: schema parses + has expected required fields.

### Step E — Plugin bundle byte-equality

```sh
diff -r framework/ platforms/claude-code-plugin/framework/ | head -5
```

Pass criteria: zero output (the bundle equals canonical post-sync).

### Step F — Inspection invariants

```sh
# No broken cross-references
grep -E 'REVIEW_SAGA|saga.schema.json' docs/PARITY.md framework/governance/REVIEW_TEAM.md plans/DECISIONS.md
# D-0031 entry present and references D-0005 supersession
grep -A3 '^## D-0031' plans/DECISIONS.md
# D-0005 has supersession pointer
grep -A1 'Superseded in scope' plans/DECISIONS.md | head -5
```

Pass criteria: cross-references resolve; D-0031 entry includes
"Superseded in scope" wording.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | The proposed REVIEW_SAGA.md content has design errors discoverable only when Phase 2 / 3 implementations try to conform | Phase 1 is plan-only-then-impl. The plan-PR (this PR) is the design-review checkpoint. The 3-pass inline review below is the load-bearing check; if it surfaces an issue, fix here before impl PR opens. |
| R2 | Both platforms declare `FRAMEWORK_SPEC_VERSION = 0.13.0` before any implementation lands; consumers might assume conformance | The declaration-vs-implementation semantic is **explicitly documented in REVIEW_SAGA.md** (see Design 1 §"FRAMEWORK_SPEC_VERSION semantics"). PARITY.md status line and CHANGELOG entries both note that implementation arrives in Phases 2 and 3. |
| R3 | GATE-SPEC (CHG-D1) might require additional formalities beyond CHANGELOG + VERSION bump | Verified pattern: CHAOS-SEC-SPLIT-001's framework-spec change (PR #79) used the same CHG-gated shape. The gate scripts `tests/chg/spec_gate.py` codify the requirements. |
| R4 | The plugin bundle sync (step 12) might surface drift in other framework/ subtrees that touched recently | The sync script (`tools/sync-plugin-framework.sh`) re-copies the entire bundle from canonical. Any pre-existing drift gets corrected as a side effect. Verified by the byte-equality test (Step E). |
| R5 | `saga.schema.json`'s `"format": "date-time"` requires a JSON Schema validator that understands the format keyword — the project's conformance test might not | Phase 1's schema-self-validation (Step D) is a structural check. Strict format validation happens in Phase 3's `test_saga_lifecycle_parity.py`. Phase 1 verifies syntax; deep validation comes later. |
| R6 | D-0005's text-preservation requirement might conflict with a markdownlint check on the appended pointer line | Pre-commit lint runs against the final state; if a check fails (e.g., trailing whitespace, blank-line spacing), fix the pointer formatting without changing D-0005's original text. |
| R7 | Other plans on todo (PRD-RT-001) reference D-0005 directly — superseding it might invalidate those plan documents | D-0031 is a **scope** supersession, not a content rewrite. D-0005's text stays verbatim. References to D-0005 elsewhere remain valid. The supersession pointer just adds context for future readers. |
| R8 | The proposed REVIEW_SAGA.md is long (~250 lines as a markdown file) and might mention concepts not yet in the rest of the spec | All concepts (states, transitions, blackboard, persona-output contract) trace back to either REVIEW_TEAM.md (which already exists) or Hermes' existing implementation. No novel framework concepts introduced. |

## Review log

### Pass 1 — 2026-06-05T13:00:00Z (initial draft)

- Adopted the parent plan's design decisions verbatim (state machine
  from Hermes, PARTIAL_TIMEOUT addition, field-requirement matrix,
  per-skill-type break-circuit boundaries, FRAMEWORK_SPEC_VERSION
  semantics).
- Pre-drafted the actual content of REVIEW_SAGA.md (Design 1) and
  saga.schema.json (Design 2) so the impl PR is mechanical paste.
- D-0031 entry wording uses "Superseded in scope" not "Deprecated" or
  "Replaced" — D-0005's blackboard reasoning still holds.
- File count: 11 edits + 2 new files = **13 file changes** in Phase 1.

### Pass 2 — 2026-06-05T13:00:00Z (self-review)

- **G-P1 — D-0005 line number**: text refers to "line 394" of
  DECISIONS.md. Verified earlier via grep; if a future edit shifts the
  number, the impl PR re-greps to find it. Step 3 says "the 2026-05-26
  one" which disambiguates from the duplicate D-0005 at line 884
  regardless of line shifts.
- **G-P2 — saga.schema.json format keyword**: JSON Schema's
  `"format": "date-time"` is informational in draft-07; strict
  validation depends on the validator. Risks table R5 acknowledges
  this. The schema's `enum` constraints on `status` and `action` are
  the load-bearing checks.
- **G-P3 — JSON `additionalProperties: true` at the top level**:
  intentional. Platforms add extension fields (Hermes:
  `document_fingerprint`, `document_path`; plugin: `current_phase`).
  Required fields are the minimum-viable contract.
- **G-P4 — REVIEW_SAGA.md links REVIEW_TEAM.md**: bidirectional
  cross-references (REVIEW_SAGA.md → REVIEW_TEAM.md for semantics,
  REVIEW_TEAM.md → REVIEW_SAGA.md for state machine). Both updates
  ship in the same impl PR (atomic).
- **G-P5 — The schema does NOT specify the saga.json file PATH**;
  paths are platform-specific (plugin: `.aidoc/review/<NN>_<LAYER>/<id>/saga.json`;
  Hermes: its own output dir). The schema describes JSON structure
  only. Correct.

### Pass 3 — 2026-06-05T13:00:00Z (codebase cross-check)

- **G-P6 — Verify `tests/chg/spec_gate.py` exists and works**: yes,
  used in PR #79 verified flow (`GATE-SPEC: framework/ change vs
  origin/main — VERSION + CHANGELOG updated, OK.`). Same gate fires
  here.
- **G-P7 — Verify `tools/sync-plugin-framework.sh` exists**: yes,
  used in PR #79 + #80. Same sync script.
- **G-P8 — Verify `framework/governance/` exists**: yes, contains
  REVIEW_TEAM.md, REVIEW_CREWS.yaml, REVIEW_REMEDIATION_FLOW.md,
  SECURITY_REVIEW.md, etc. REVIEW_SAGA.md slots in here.
- **G-P9 — Verify `platforms/claude-code-plugin/CHANGELOG.md` has
  `[Unreleased]` block**: yes, the recent CHAOS-SEC-SPLIT-001 entries
  are there.
- **G-P10 — Verify project `CHANGELOG.md` has `[Unreleased]` block**:
  yes, with prior CHAOS-SEC-SPLIT-001 entry "Framework Spec 0.11.3 →
  0.12.0 (CHG-gated)". New entry "Framework Spec 0.12.0 → 0.13.0"
  goes above it (chronological "newest first" by virtue of being
  later spec).
- **G-P11 — Verify `docs/TAGGING.md` has a framework row section**:
  yes, format is `| \`framework/vX.Y.Z\` | <event> | <description> |`.
  Pattern is consistent with prior entries.
- **G-P12 — Verify the plugin's bundle includes
  `platforms/claude-code-plugin/framework/governance/`**: yes (from
  earlier sync after CHAOS-SEC-SPLIT-001). The sync script handles
  new files automatically.
- **G-P13 — Schema field `compensation_actions` matches Hermes' field
  name (`SagaRunState.compensation_actions`)**: verified earlier.
  Plugin will populate the same field name. Phase 3 verifies
  byte-equality between Hermes' serialized output and the schema.
- **G-P14 — Hermes uses `personas_requested` field too** (verified
  via `SagaRunState.personas_requested: list[str]`). Schema requires
  exactly this field name. ✓

Plan ready for impl.

## Cross-references

### Within this plan family

- **Parent plan**: `plans/SAGA-PARITY-001-PLAN.md` (the 4-phase
  organizing plan; this Phase 1 plan supplies impl-ready content).
- **Sibling phases (gated on this)**: Phase 2 plugin BRD impl, Phase 3
  Hermes alignment, Phase 4 plugin propagation. Each will get its own
  plan PR when this Phase 1 lands.

### Predecessor decisions

- **D-0005 (2026-05-26)** — `plans/DECISIONS.md:394` ("No saga for the
  plugin review runner"). To be superseded in scope by D-0031.
- **D-0024..D-0028** — BRD-RT chain (foundation that surfaced the
  outer-loop timeout evidence).
- **D-0030** — CHAOS-SEC-SPLIT-001 (the verification run that revealed
  the saga gap).

### Spec authorities cited

- `framework/governance/REVIEW_TEAM.md` — operational semantics.
- `framework/governance/REVIEW_CREWS.yaml` — per-layer crews.
- Hermes' `platforms/hermes/src/mcp_server/review/saga_models.py` —
  source of the adopted state machine + transitions.
- `docs/PROJECT.md` §2 — independent version streams (the basis for
  the declaration-vs-implementation semantic).
- `docs/PROJECT.md` §6 — CHG process (post-cutover governance).

### Forward (created by this plan)

- `framework/governance/REVIEW_SAGA.md`
- `framework/governance/saga.schema.json`
- `plans/DECISIONS.md` D-0031 (+ D-0005 supersession pointer)
