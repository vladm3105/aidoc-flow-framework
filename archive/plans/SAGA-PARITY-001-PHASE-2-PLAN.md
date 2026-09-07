# SAGA-PARITY-001 Phase 2 — Plugin BRD-layer impl (saga.json + Bash subprocess + break-circuit)

| Field      | Value                                                     |
|------------|-----------------------------------------------------------|
| Task       | SAGA-PARITY-001-PHASE-2                                   |
| Parent     | SAGA-PARITY-001 (`plans/SAGA-PARITY-001-PLAN.md`, merged) |
| Depends on | Phase 1 (D-0031; merged via PR #84) — REVIEW_SAGA.md + saga.schema.json are the contract this phase implements |
| Status     | PLANNED — 2026-06-05T14:30:00Z                            |
| Feeds      | Phase 3 (Hermes alignment; will compare against plugin's saga.json fixtures), Phase 4 (PRD..IPLAN propagation; reuses this BRD reference impl) |
| Scope flag | **Plugin minor bump** — plugin VERSION 0.5.0 → 0.6.0; MINOR (not BREAKING) per Pass-4 G-R8: `saga.json` is a purely additive artifact, no existing file shapes change. The 0.6 vs 0.5.1 bump signals "meaningful new capability". |

## Objective

Implement the **cooperative-enforcement** binding of the framework saga
lifecycle contract (`framework/governance/REVIEW_SAGA.md`) on the
Claude Code plugin for the BRD layer. Specifically: every BRD-layer
orchestrator skill (`doc-brd-autopilot`, `doc-brd-audit`, `doc-brd-fixer`)
maintains a `saga.json` journal at
`.aidoc/review/01_BRD/<BRD-id>/saga.json`, dispatches each create→review→
revise phase via `Bash → claude -p` subprocesses (each gets a fresh
`ORCHESTRATOR_TIMEOUT=1800s` budget via the existing
`tests/scripts/test-acceptance.sh:_pick_timeout_for` name-match), and
implements the **break-circuit policy** with a `SOFT_DEADLINE=1500s`
(300s buffer below OS timeout) at the per-skill checkpoint boundaries
defined in REVIEW_SAGA.md.

After Phase 2 lands, the plugin's BRD layer produces a saga.json that
conforms to `saga.schema.json` on every run, complementary to the
existing blackboard slot files. The autopilot's outer-loop budget
problem (BRD-RT-004 + CHAOS-SEC-SPLIT-001 verification) is solved by
**resumability**: an autopilot invocation that hits PARTIAL_TIMEOUT
exits cleanly with the journal preserved; a subsequent invocation
reads the saga.json and resumes from the recorded `current_phase`.

This is the **reference implementation** for the cooperative-enforcement
mode. Phase 4 propagates the same pattern verbatim to PRD..IPLAN.

## Scope

### In

1. **Edit** `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`
   — full refactor per Design 1 (saga.json read/initialize, per-phase
   subprocess dispatch via `Bash`, break-circuit checkpoint, resume
   logic, transition validation).
1a. **Edit** `platforms/claude-code-plugin/skills/doc-brd/SKILL.md`
   — append §"Draft mode (saga-driven)" section per Design 1 §3a
   (G-R2). The draft subprocess invokes `doc-brd`, which dispatches
   `requirements-analyst` as a Task subagent with the
   `business_analyst` lens brief. Preserves the persona binding lost
   in the move from in-session Task dispatch to subprocess
   invocation.
2. **Edit** `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md`
   — append §"Saga interaction" + §"Break-circuit policy" sections
   (Design 2). When invoked standalone OR via autopilot, the audit
   transitions its branches and respects the break-circuit.
3. **Edit** `platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md`
   — append same saga interaction + break-circuit sections (Design 3),
   adapted for the multi-lens validation-dispatch boundaries.
4. **Edit** `platforms/claude-code-plugin/skills/review-team/SKILL.md`
   — append a §"Saga journal" subsection (Design 4) describing the
   saga.json layout next to the existing blackboard layout
   description. The review-team dispatcher updates branch states.
5. **Bump plugin VERSION** 0.5.0 → 0.6.0 (MINOR per Pass-4 G-R8;
   `saga.json` is a purely additive artifact, no existing file shapes
   change; the 0.6 bump signals "meaningful new capability" without
   the BREAKING flag).
6. **9-place version fanout** for 0.6.0 (per CHAOS-SEC-SPLIT-001
   pattern; full enumeration in Step 6 of Step Sequence).
7. **Edit** `platforms/claude-code-plugin/CHANGELOG.md` with the
   Design 5 entry.
8. **Edit** `docs/PARITY.md` — set status-line plugin version to
   `claude-code-plugin/v0.6.0`; update §"Review team" comparison
   table's "Saga lifecycle" row to note plugin now implements the
   contract for BRD (PRD..IPLAN deferred to Phase 4).
9. **Edit** `docs/TAGGING.md` — add `claude-code-plugin/v0.6.0`
   release row.
10. **Live BRD verification** (~$3, ~30-60 min) per Design 6 with
    the 8 pass criteria.

### Out (deferred to later phases)

- **Hermes-side changes** (`PARTIAL_TIMEOUT` addition,
  `transitions[]` field on `SagaRunState`) — Phase 3.
- **Cross-platform conformance test** `test_saga_lifecycle_parity.py`
  — Phase 3 (it needs Hermes' Phase-3 changes to validate both
  platforms).
- **PRD..IPLAN propagation** — Phase 4.
- **Harness-side changes** to `tests/scripts/test-acceptance.sh` for
  PARTIAL_TIMEOUT resume — covered in Step 9 below as **conditional**
  (only if the live verification surfaces a need).
- **Plugin own VERSION beyond 0.6.0** — Phase 4 patch-bumps per-layer
  as it propagates.
- **`framework/VERSION` or `FRAMEWORK_SPEC_VERSION`** changes — the
  spec is unchanged in Phase 2 (Phase 1's `0.13.0` declaration remains).

## Approach — concrete content designs

### Design 1 — `doc-brd-autopilot/SKILL.md` refactor

The autopilot becomes a **saga-driven coordinator** that dispatches
each phase as a fresh `claude -p` subprocess via the `Bash` tool. Its
own session is light — no in-session LLM work between phases beyond
reading files, checking elapsed time, and making gate decisions.

#### Frontmatter

Unchanged from current state except `adapts` gains `saga`-aware
fields if needed. The skill `version` bumps to `0.6.0` and
`framework_spec_version` stays at `0.13.0` (Phase 1's declaration).

#### Replace the Workflow section with a saga-driven loop

Replace the existing "Generation Loop (review_mode: team)" section
(lines 81-118 of the current SKILL.md, approximately) with:

````markdown
## Saga-driven generation loop (`review_mode: team`)

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`, the
plugin uses cooperative enforcement: this SKILL prompt directs the LLM
to read/write `saga.json`, validate transitions against the table in
REVIEW_SAGA.md, and dispatch each phase as a fresh `claude -p`
subprocess via the `Bash` tool (so each phase inherits its own
`ORCHESTRATOR_TIMEOUT=1800s` budget rather than sharing the
autopilot's parent budget).

### 1. Saga setup (entry / resume)

`SAGA_DIR=.aidoc/review/01_BRD/<BRD-id>/`
`SAGA_FILE=$SAGA_DIR/saga.json`
`START_EPOCH_FILE=$SAGA_DIR/.skill-start.autopilot`
`SOFT_DEADLINE=1500`  # seconds; OS-level timeout = 1800s; 300s buffer

**Per-skill start epoch (G-R3)**. Each subprocess invoked from
autopilot's loop starts with its own fresh OS-level timeout (1800s).
Each skill therefore tracks elapsed time against its OWN start epoch,
not autopilot's. The naming convention:

| Skill | Start epoch file |
|---|---|
| `doc-brd-autopilot` | `$SAGA_DIR/.skill-start.autopilot` |
| `doc-brd-audit` | `$SAGA_DIR/.skill-start.audit` |
| `doc-brd-fixer` | `$SAGA_DIR/.skill-start.fixer` |
| `review-team` | `$SAGA_DIR/.skill-start.review-team` |

Each skill writes its own file at entry and reads its own file at
break-circuit checks. Files are gitignored as part of `.aidoc/`
runtime state.

If `$SAGA_FILE` exists and `status` is not `CLOSED` or `ESCALATED`,
this invocation is a **resume**. Read the existing saga and continue
from `current_phase`. Otherwise initialize a fresh saga:

```json
{
  "review_run_id": "<sha256-prefix-of: $artifact_path|$crew|$time_bucket>",
  "artifact_id": "<BRD-id>",
  "layer": "01_BRD",
  "personas_requested": ["business_analyst","architect","auditor","chaos_engineer","security_engineer"],
  "status": "PREPARED",
  "iteration": 1,
  "current_phase": "draft",
  "created_at": "<now ISO 8601 UTC>",
  "updated_at": "<now ISO 8601 UTC>",
  "branches": {},
  "transitions": [{"ts": "<now>", "from": null, "to": "PREPARED", "scope": "run"}],
  "compensation_actions": []
}
```

Then write start epoch:
`Bash: date +%s > $START_EPOCH_FILE`

### 1a. Pre-Phase-2 blackboard migration (G-R6)

If `$SAGA_DIR` exists with **slot files but no saga.json**
(`.aidoc/review/01_BRD/<BRD-id>/<persona>.json` files present from a
pre-Phase-2 run, no `saga.json`), autopilot detects this and
scaffolds a saga.json reflecting the existing state instead of
treating it as fresh:

  - Walk `$SAGA_DIR/*.json`. For each `<persona>.json` slot file:
    - Add a `branches[<persona>]` entry with
      `status: BRANCH_COMPLETED`, `attempt: 0`,
      `started_at: <slot file mtime>`, `ended_at: <slot file mtime>`.
  - Set saga `status: BRANCH_COMPLETED` (all crew slots present
    means fan-in is the next phase).
  - Set `iteration: 1`, `current_phase: re-review` (we don't know
    if the existing slots are post-audit or post-fixer, so we
    re-audit defensively).
  - Append a single backfill transition entry:
    `null → BRANCH_COMPLETED, scope: "run", reason: "pre-saga
    migration backfill"` (this is a non-standard transition;
    document with a `migration: true` extension field in that
    entry).
  - Continue from §2 phase dispatch loop.

This preserves work-in-progress from pre-Phase-2 sessions. If a user
prefers a clean re-run, they can `rm $SAGA_DIR/*.json` before
invoking autopilot.

### 2. Phase dispatch loop

Until `status ∈ {CLOSED, ESCALATED, PARTIAL_TIMEOUT}`:

  **a. Break-circuit check.** Before dispatching the next phase:
  ```
  Bash: echo $(( $(date +%s) - $(cat $START_EPOCH_FILE) ))
  ```
  If elapsed > `SOFT_DEADLINE`:
    - Append transition: `<current_status> → PARTIAL_TIMEOUT` (scope: run).
    - Set status to PARTIAL_TIMEOUT; preserve `current_phase`.
    - Write $SAGA_FILE and exit cleanly (no further dispatch).

  **b. Determine and dispatch next phase** based on `current_phase`:

  | current_phase | Subprocess command (via Bash) | Pre-transition | Post-transition (on subprocess exit 0) |
  |---|---|---|---|
  | `draft` | `claude -p /aidoc-flow:doc-brd <draft brief>` — see §3a | `PREPARED → FANOUT_STARTED` | `FANOUT_STARTED → BRANCH_RUNNING` (drafter as a single-branch); after draft completes: `BRANCH_RUNNING → BRANCH_COMPLETED` for the drafter; set `current_phase: review` |
  | `review` | `claude -p /aidoc-flow:doc-brd-audit <audit brief>` — see §3b | (none — audit invocation begins its own branch transitions) | After audit subprocess exits: read its `verdict.json`; if PASS → `current_phase: finalize`; if FAIL → `current_phase: fixer` |
  | `fixer` | `claude -p /aidoc-flow:doc-brd-fixer <fixer brief>` | (none — fixer manages its own transitions) | After fixer exits: increment `iteration`; `current_phase: re-review` |
  | `re-review` | `claude -p /aidoc-flow:doc-brd-audit <re-audit brief>` | (none) | After re-audit: if PASS → `current_phase: finalize`; if FAIL AND `iteration < 3` → `current_phase: fixer`; else escalate (status: ESCALATED) |
  | `finalize` | Update `docs/01_BRD/BRD-00_index.md`; transition through `FANIN_REDUCED → SYNTHESIZED → CLOSED` | `<prior> → FANIN_REDUCED → SYNTHESIZED → CLOSED` | exit loop |

  **c. Update saga.json after each subprocess returns.** Append a
  transition entry per the table. Write `$SAGA_FILE`. Update
  `updated_at`. The transition table from REVIEW_SAGA.md MUST be
  respected — invalid transitions (e.g., `PREPARED → CLOSED`) are
  bugs.

  **d. Loop.**

### 3. Phase briefs (subprocess inputs)

#### 3a. Drafter (G-R2)

The current autopilot dispatches `requirements-analyst` as a `Task`
subagent for the draft phase (with `business_analyst` lens brief per
the lens→agent mapping). The Phase 2 refactor moves this dispatch
into a **subprocess** via `Bash → claude -p /aidoc-flow:doc-brd ...`.
A subprocess invocation cannot pass `subagent_type` directly (that's
a Task-tool parameter, not a CLI argument), so the persona binding
must move INTO the `doc-brd/SKILL.md` prompt itself.

**Plan scope addition (G-R2)**: `platforms/claude-code-plugin/skills/doc-brd/SKILL.md`
gains a `## Draft mode (saga-driven)` section telling the LLM:

> When invoked via `claude -p /aidoc-flow:doc-brd Draft BRD-<id> ...`
> (the subprocess pattern from the autopilot saga loop), dispatch ONE
> `Task` subagent with `subagent_type=requirements-analyst` and the
> `business_analyst` lens brief per the BRD crew. The subagent
> authors the BRD; this skill's role is to brief it and write the
> result to `docs/01_BRD/BRD-<id>_<slug>/`.

The subprocess command remains:

```sh
timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p \
  "/aidoc-flow:doc-brd Draft BRD-<id> at <path>; use BRD-TEMPLATE.yaml + the source input at <seed-path>. Write to docs/01_BRD/BRD-<id>_<slug>/."
```

The child claude session reads doc-brd/SKILL.md's new `## Draft mode
(saga-driven)` section and dispatches the Task subagent. The
persona binding is preserved via the SKILL prompt's instruction, not
via a CLI parameter.

Updated **scope** (add to §"In" item list): doc-brd/SKILL.md edit.

#### 3b. Audit (review and re-review phases)

```sh
timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p \
  "/aidoc-flow:doc-brd-audit Audit BRD-<id> at <path>. Update saga.json at <saga-path> (read current state, transition branches, write back). Write audit report to <audit-report-path>. Iteration=<N>."
```

The audit invocation reads the saga.json, transitions its branches as
it dispatches lenses, and updates the saga.json before exit. The
audit also writes the existing `verdict.json` per BRD-RT-002.

#### 3c. Fixer

```sh
timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p \
  "/aidoc-flow:doc-brd-fixer Fix BRD-<id> at <path> based on audit findings at <audit-report-path>. Update saga.json (multi-lens validation dispatches transition branches BRANCH_COMPENSATING)."
```

### 4. Resume logic (G-R1)

PARTIAL_TIMEOUT is terminal-this-process per
`framework/governance/REVIEW_SAGA.md`'s transition table — it has no
allowed-next transitions. The resume mechanism is therefore NOT a
direct `PARTIAL_TIMEOUT → X` transition. Instead, a resumed run
treats the PARTIAL_TIMEOUT entry in `transitions[]` as a **checkpoint
marker** and appends **the next legal transition from the state that
was active immediately before PARTIAL_TIMEOUT fired**.

Concretely:

  1. Read the existing saga.json.
  2. Identify `current_phase` from the journal.
  3. Re-record start epoch (this invocation's clock starts fresh; see
     §"Per-skill start epoch" below for the file naming).
  4. **Identify the pre-PARTIAL_TIMEOUT state**: walk backward through
     `transitions[]` to find the most recent transition whose `to`
     is NOT `PARTIAL_TIMEOUT`. That state is the resume point.
  5. **Append the next legal transition** from that state per the
     REVIEW_SAGA.md transition table. For example:
     - If the pre-PARTIAL_TIMEOUT state was `BRANCH_COMPLETED` (all
       branches done but synthesizer didn't get to dispatch),
       append `BRANCH_COMPLETED → FANIN_REDUCED` once synthesizer
       runs.
     - If it was `BRANCH_RUNNING` (some branches were mid-flight),
       continue running those branches (their per-branch state
       transitions resume independently).
     - If it was `FANOUT_STARTED` (fan-out had begun but no branch
       completed), pick up dispatching remaining lenses.
  6. Continue from §2 phase dispatch loop.

Do NOT write a transition with `from: PARTIAL_TIMEOUT` — that would
violate the spec's transition table and the conformance suite (when
the cross-platform parity test arrives in Phase 3) would flag it.
The PARTIAL_TIMEOUT entry remains in `transitions[]` as a permanent
record that this run was checkpointed and resumed; subsequent
transitions continue the lifecycle from where the checkpoint was
laid down.

### 4a. Edge cases on entry (G-R4)

- **`status == CLOSED`** on entry: the saga already completed
  successfully. Log "saga already CLOSED for BRD-<id>; iteration N
  complete" and exit cleanly (exit code 0). Do NOT re-run unless
  the user explicitly requests a fresh iteration (e.g., by removing
  saga.json or invoking with a `--force-fresh` flag — out of scope
  for Phase 2; treat CLOSED as terminal).
- **`status == ESCALATED`** on entry: the prior run was escalated
  for human review. Do NOT auto-restart. Log "saga ESCALATED for
  BRD-<id>; human review required" and exit cleanly. Only a manual
  saga.json deletion + fresh autopilot invocation should bypass
  ESCALATED.
- **`status == PARTIAL_TIMEOUT`**: resume per §4 above.
- **All other in-flight states** (`PREPARED`, `FANOUT_STARTED`,
  `BRANCH_RUNNING`, etc.): the prior run was interrupted before
  reaching a terminal state but did NOT fire the break-circuit
  (e.g., the parent process was SIGKILLed externally). Treat as
  resume: read saga.json, continue from `current_phase`. Append
  the next legal transition based on the prior state. Do NOT
  re-initialize (that would lose work).

### 5. Single_pass fallback

For `review_mode: single_pass`, skip the saga entirely (the legacy
linear pipeline; see §"Linear Pipeline" below). Saga.json is a
team-mode artifact; single_pass invocations do not produce one.
````

#### Workflow steps that stay

The current single_pass linear pipeline (Workflow steps 1-5 of the
existing SKILL.md) stays as a fallback. Insert a top-line conditional:

```markdown
## Workflow

The workflow has two shapes — the team-mode **saga-driven generation
loop** (default at gates) and the single_pass linear pipeline
(fallback).

[saga-driven loop above]

[unchanged single_pass linear pipeline]
```

### Design 2 — `doc-brd-audit/SKILL.md` saga interaction + break-circuit

Append two new sections after the existing §"Review Mode" section.

#### §"Saga interaction"

````markdown
## Saga interaction

When invoked by `doc-brd-autopilot` (or directly), this skill reads
and updates the saga journal at
`.aidoc/review/01_BRD/<BRD-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The audit
acts as the **fan-out + fan-in stage** of the saga.

### On entry

If saga.json exists, read it. Otherwise initialize per the autopilot's
§1 setup. Validate that current saga `status` is one of:
`FANOUT_STARTED`, `BRANCH_COMPLETED` (for re-audit). If not, log a
warning and proceed (the audit is structural enough to be invoked
outside the saga; the journal-write becomes advisory in that case).

### During lens fan-out (team mode)

For each lens dispatched as a `Task` subagent:
  1. Before dispatch: append a `branches[<lens>]` entry with
     `branch_id: <hash>`, `status: BRANCH_RUNNING`, `attempt: 0`,
     `started_at: <now>`. Append transition: `FANOUT_STARTED →
     BRANCH_RUNNING` (scope: `branch:<lens>`).
  2. After dispatch returns: update `branches[<lens>].status` to
     `BRANCH_COMPLETED` or `BRANCH_FAILED` per the lens's persona-output
     record. Set `ended_at`. Append transition entry.

### Before synthesizer dispatch

This is the break-circuit checkpoint (per REVIEW_SAGA.md's
"Layer audit" checkpoint boundary). At skill entry the audit writes
its own start epoch:

```
Bash: date +%s > $SAGA_DIR/.skill-start.audit
```

At checkpoint:

```
Bash: echo $(( $(date +%s) - $(cat $SAGA_DIR/.skill-start.audit) ))
```

If elapsed > `SOFT_DEADLINE` (1500s):
  - Append transition: `BRANCH_COMPLETED → PARTIAL_TIMEOUT`.
  - Set saga status to PARTIAL_TIMEOUT; preserve any reduced
    findings up to this point.
  - Exit cleanly. The caller (autopilot or harness) can re-invoke.

### After synthesizer reduce

  - Append transition: `BRANCH_COMPLETED → FANIN_REDUCED`.
  - Update saga `status: FANIN_REDUCED`.
  - Synthesizer also writes `verdict.json` (per BRD-RT-002, unchanged).
  - This skill's exit returns control to the caller (autopilot or
    the user); the caller decides next phase based on the verdict.

### When invoked standalone (no saga.json on entry) — G-R5

If saga.json does NOT exist (e.g., the audit is invoked outside the
autopilot's lifecycle, by a user running `/aidoc-flow:doc-brd-audit`
directly), do NOT initialize the full saga schema. The audit is not
the lifecycle owner; initializing a saga would write inconsistent
state. Instead:

  - Log "saga.json not present; running audit without saga journal
    (standalone mode)."
  - Run the audit's lens fan-out + synthesizer as normal.
  - Write blackboard slot files + verdict.json + audit report as
    usual.
  - Skip all saga.json transitions.

This preserves backward compatibility with direct skill invocation
and keeps the audit's standalone use case unchanged. Only autopilot-
driven runs produce saga.json.

### When invoked standalone in single_pass mode

If `review_mode: single_pass` is active, the audit does not produce
saga.json (same as standalone above — saga is a team-mode artifact).
Existing behavior preserved.
````

#### §"Break-circuit policy"

Add as a separate `##` section near the bottom:

````markdown
## Break-circuit policy

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`
§"Break-circuit policy", this skill checks elapsed wall-clock at one
checkpoint boundary: **after all lens dispatches return; before
invoking the synthesizer**. The SOFT_DEADLINE is 1500s (OS timeout
1800s minus 300s buffer).

If the soft deadline has been crossed, exit cleanly with
`status: PARTIAL_TIMEOUT` (per §"Saga interaction" above). If the
LLM ignores the check and the OS sends SIGTERM, saga.json reflects
the last successful checkpoint state (NOT PARTIAL_TIMEOUT). Both
outcomes are valid graceful-degradation states.
````

### Design 3 — `doc-brd-fixer/SKILL.md` saga interaction + break-circuit

Same shape as Design 2 with these differences:

- The fixer transitions branches into `BRANCH_COMPENSATING` while
  validating each patch. After validation: either back to
  `BRANCH_COMPLETED` (patch validated) or `BRANCH_FAILED` (patch
  regresses).
- The break-circuit checkpoint is **between multi-lens validation
  dispatches** (each blocking finding's per-lens validation is one
  boundary). The fixer may complete some validations and then
  PARTIAL_TIMEOUT before others, leaving `fix_N.json` slots for the
  ones it got to and a PARTIAL_TIMEOUT saga status. Re-invocation
  picks up the remaining validations.
- The transition shape: `BRANCH_COMPLETED → BRANCH_COMPENSATING →
  BRANCH_COMPLETED` (per finding) or `→ BRANCH_FAILED` (per finding).

### Design 4 — `review-team/SKILL.md` saga.json layout

Append a `## The saga journal` subsection right after the existing
`## The blackboard` section:

````markdown
## The saga journal

Alongside the blackboard, the orchestrator maintains a **saga journal**
at `.aidoc/review/<artifact-id>/saga.json` per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The saga
journal records:

- run-level **state machine** progression (PREPARED → FANOUT_STARTED
  → BRANCH_RUNNING → BRANCH_COMPLETED → FANIN_REDUCED → SYNTHESIZED →
  CLOSED, with `PARTIAL_TIMEOUT` and `ESCALATED` failure paths)
- per-branch **status** (one entry per persona dispatched)
- a **transitions[]** append-only log (every state change)
- a **compensation_actions[]** append-only log (compensation events)

The blackboard (slot files) captures **persona findings**; the saga
journal captures **lifecycle progression**. The two artifacts
complement each other:

```text
.aidoc/review/<artifact-id>/
  <persona>.json        # blackboard slot — persona-output record
  saga.json             # saga journal — lifecycle state + transitions
  report.md             # synthesizer's unified report
  verdict.json          # synthesizer's combined-status companion
```

The dispatcher (this skill) is responsible for transitioning the
saga `status` and per-branch states as it fans out and reduces. The
schema lives at `${CLAUDE_PLUGIN_ROOT}/framework/governance/saga.schema.json`;
conformance tests validate runtime saga.json files against it.
````

### Design 5 — Plugin CHANGELOG entry

Append under `[Unreleased]`:

````markdown
### Changed — Plugin v0.5.0 → v0.6.0

> **SemVer classification rationale (G-R8)**: this release is
> labelled as a MINOR bump (0.5.0 → 0.6.0) rather than BREAKING. The
> primary surface change — adding `saga.json` to
> `.aidoc/review/<NN>_<LAYER>/<id>/` — is purely **additive**: no
> existing files (blackboard slots, verdict.json, report.md) change
> shape, and no existing CLI / skill invocation breaks. Consumers
> that strictly enumerate the contents of `.aidoc/review/` may see a
> new file, but the shape of every other file is preserved. Under
> pre-1.0 SemVer the project uses MINOR for additive changes; the
> 0.6 bump (vs a patch 0.5.1) signals "meaningful new capability"
> while avoiding the ⛔ BREAKING flag.

- **BRD-layer saga implementation (SAGA-PARITY-001 Phase 2, D-0031).**
  The plugin's BRD-layer orchestrator skills (`doc-brd-autopilot`,
  `doc-brd-audit`, `doc-brd-fixer`, plus shared `review-team`) now
  maintain a saga journal at
  `.aidoc/review/01_BRD/<BRD-id>/saga.json` per the framework
  saga lifecycle contract (`framework/governance/REVIEW_SAGA.md`).
  - **Autopilot refactor**: the create→review→revise loop now
    dispatches each phase via `Bash → claude -p` subprocesses
    (each gets its own `ORCHESTRATOR_TIMEOUT=1800s` budget). The
    autopilot's outer loop wakes the next phase, updates saga.json
    after each subprocess returns, and validates state transitions
    against the table in REVIEW_SAGA.md. The autopilot's session
    no longer runs the entire loop in-process — phases live in
    subprocesses for budget isolation.
  - **Break-circuit policy**: SOFT_DEADLINE=1500s (300s buffer
    below ORCHESTRATOR_TIMEOUT). At per-skill checkpoint boundaries
    (autopilot: between phases; audit: before synthesizer; fixer:
    between multi-lens validations; review-team: between fan-out
    and reduce), the orchestrator checks elapsed time and exits
    cleanly with `status: PARTIAL_TIMEOUT` if the soft deadline
    has been crossed.
  - **Resumable runs**: an autopilot invocation that returns with
    `status: PARTIAL_TIMEOUT` can be re-invoked; the resumed
    session reads saga.json and continues from
    `current_phase`. The CHAOS-SEC-SPLIT-001 verification scenario
    (5-lens BRD with multi-lens fixer hitting 1802s in a single
    autopilot invocation) becomes recoverable instead of fatal.
  - PRD..IPLAN propagation arrives in SAGA-PARITY-001 Phase 4.
  - Hermes-side alignment (PARTIAL_TIMEOUT, transitions[] field)
    arrives in Phase 3.
  - **Breaking surface**: `.aidoc/review/01_BRD/<BRD-id>/saga.json`
    is a new public artifact. Consumers parsing `.aidoc/review/`
    contents should expect this file. The blackboard slot files
    (`<persona>.json`, `verdict.json`, `report.md`) are unchanged.

  Plugin `VERSION`: `0.5.0 → 0.6.0`. `FRAMEWORK_SPEC_VERSION`
  unchanged at `0.13.0` (Phase 1's declaration; Phase 2 implements
  what Phase 1 declared).
````

### Design 6 — Live BRD verification pass criteria

Run:

```sh
bash tests/scripts/test-acceptance.sh url-shortener --live \
     --phase=cascade --from-layer=brd --to-layer=brd --force
```

Pass criteria (8/8, expanding BRD-RT-004 + CHAOS-SEC-SPLIT verification
with the new saga checks):

1. **saga.json present** at `.aidoc/review/01_BRD/<BRD-id>/saga.json`
   and schema-conformant (validates against `saga.schema.json`).
2. **5 lens slot files** present including `chaos_engineer.json` and
   `security_engineer.json` (CHAOS-SEC-SPLIT-001 invariant carries
   forward).
3. **Final saga `status`** is one of: `CLOSED` (happy path), or
   `PARTIAL_TIMEOUT` (graceful-degradation path; harness re-invokes
   for completion).
4. **`transitions[]`** has entries showing the full lifecycle (at
   minimum: PREPARED → FANOUT_STARTED → BRANCH_RUNNING for each lens
   → BRANCH_COMPLETED for each lens → FANIN_REDUCED → SYNTHESIZED →
   CLOSED). If PARTIAL_TIMEOUT, the path stops at the appropriate
   checkpoint.
5. **`verdict.json:lens_scores`** map contains both
   `chaos_engineer` and `security_engineer` keys (CHAOS-SEC-SPLIT-001
   invariant).
6. **Per-phase subprocess invocation visible in logs**: the
   acceptance script's element logs show `doc-brd-autopilot`
   invoking `claude -p /aidoc-flow:doc-brd-audit` and
   `/aidoc-flow:doc-brd-fixer` as child processes.
7. **Break-circuit fires cleanly OR loop completes within budget**.
   Two scenarios both acceptable:
   - **Scenario A (happy path)**: total runtime ≤ MAX_LAYER_SEC
     (3600s); final status CLOSED; no PARTIAL_TIMEOUT in
     `transitions[]`.
   - **Scenario B (resume path)**: autopilot's outer session hits
     SOFT_DEADLINE, exits with status PARTIAL_TIMEOUT and exit
     code 0; harness OR a re-invocation reads saga.json and
     resumes from `current_phase`; subsequent invocation
     completes (status CLOSED).
8. **No SIGTERM-leaked saga.json** (i.e., no `exit 124` with a
   missing or last-checkpoint-only saga.json). If the LLM ignores
   the break-circuit and SIGTERM fires, that's a cooperative
   failure — saga.json should still have the last successful
   checkpoint state, which is acceptable per the spec, but the
   verification flags it as a quality issue for the SKILL prompt.

## Step sequence

1. **Edit** `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`
   per Design 1.
2. **Edit** `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md`
   per Design 2 (append §"Saga interaction" + §"Break-circuit policy").
3. **Edit** `platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md`
   per Design 3 (similar to Design 2, adapted for multi-lens validation
   boundaries).
4. **Edit** `platforms/claude-code-plugin/skills/review-team/SKILL.md`
   per Design 4 (append `## The saga journal` subsection).
5. **Bump plugin VERSION** `0.5.0 → 0.6.0` at `platforms/claude-code-plugin/VERSION`.
6. **9-place version fanout** (enumerated):
   - `platforms/claude-code-plugin/VERSION`
   - `platforms/claude-code-plugin/.claude-plugin/plugin.json`
     (`"version"` field)
   - `.claude-plugin/marketplace.json` (the plugin's `"version"` field)
   - `platforms/claude-code-plugin/README.md` (version references)
   - root `README.md` (if it cites the plugin version)
   - `docs/PARITY.md` (status line)
   - `docs/TAGGING.md` (new `claude-code-plugin/v0.6.0` row)
   - `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md` (version
     references in example frontmatter)
   - **52 skills' frontmatter** via sed:

     ```sh
     grep -rl '^    version: "0.5.0"' platforms/claude-code-plugin/skills/ \
       | xargs sed -i 's/^    version: "0.5.0"/    version: "0.6.0"/'
     ```

     Verify with `grep -rc '^    version: "0.6.0"' platforms/claude-code-plugin/skills/`
     showing 52 matches.
7. **Edit** `platforms/claude-code-plugin/CHANGELOG.md` per Design 5
   (insert above existing `[Unreleased]` entries; newest-first).
8. **Edit** `docs/PARITY.md`:
   - Status line: bump `claude-code-plugin/v0.5.0 → v0.6.0`.
   - "Saga lifecycle" row: note plugin now implements the contract
     for BRD (PRD..IPLAN deferred to Phase 4).
9. **Edit** `docs/TAGGING.md`: add `claude-code-plugin/v0.6.0`
   release row.
10. **Conditional harness change** to
    `tests/scripts/test-acceptance.sh` (G-R7). Concrete spec (apply
    only if Scenario B is observed in live verification):

    Insert a saga-aware resume loop after the existing
    `invoke_skill "doc-$layer-autopilot"` call in the cascade loop
    (search for `invoking /aidoc-flow:doc-$layer-autopilot` to
    locate; near line ~950 of test-acceptance.sh). Diff sketch:

    ```diff
       invoke_skill "doc-$layer-autopilot" "$autopilot_prompt" ...
    +
    +  # Saga resume loop (SAGA-PARITY-001 Phase 2, G-R7). If the
    +  # autopilot exited cleanly but saga.json shows PARTIAL_TIMEOUT,
    +  # re-invoke up to MAX_RESUMES=2 times to drive it to a terminal
    +  # state (CLOSED or ESCALATED).
    +  local saga_file=".aidoc/review/01_BRD/BRD-01/saga.json"
    +  local resume_count=0
    +  while [[ -f "$saga_file" ]] && [[ $resume_count -lt 2 ]]; do
    +    local status
    +    status=$(python3 -c "import json; print(json.loads(open('$saga_file').read()).get('status',''))")
    +    [[ "$status" == "PARTIAL_TIMEOUT" ]] || break
    +    log_info "  saga PARTIAL_TIMEOUT — resuming autopilot (attempt $((resume_count+1)))"
    +    invoke_skill "doc-$layer-autopilot" "Resume autopilot for $layer; saga.json exists at $saga_file" "skill" "cascade"
    +    resume_count=$((resume_count+1))
    +  done
    ```

    `MAX_RESUMES=2` bounds the resume loop (prevents infinite
    re-invocation if the saga somehow stays at PARTIAL_TIMEOUT).
    Phase 2 verification Step F covers this case; if it fails after
    2 resumes, the run is marked degraded but not blocking.

    **Decision rule**: apply Step 10 only if Step D's live verification
    observes Scenario B (autopilot exits with status PARTIAL_TIMEOUT
    on first invocation). Otherwise the harness stays unchanged and
    autopilot's first invocation reaches CLOSED in one go.
11. **Pre-commit lint** on all changed files.
12. **Full conformance suite** — 101/101 still pass; saga.json is
    not validated by an existing test in Phase 2 (the cross-platform
    test arrives in Phase 3), so this run is a regression-only
    check.
13. **Live BRD verification** per Design 6.
14. **Update SAGA-PARITY-001 plan** `Plan ready for impl.` line to
    note Phase 2 landed; add forward pointer to Phase 3.

## Verification

### Step A — Static lint

```sh
env -u LD_LIBRARY_PATH pre-commit run --files \
  platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md \
  platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md \
  platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md \
  platforms/claude-code-plugin/skills/review-team/SKILL.md \
  platforms/claude-code-plugin/VERSION \
  platforms/claude-code-plugin/CHANGELOG.md \
  platforms/claude-code-plugin/.claude-plugin/plugin.json \
  .claude-plugin/marketplace.json \
  platforms/claude-code-plugin/README.md \
  docs/PARITY.md \
  docs/TAGGING.md
```

Pass: green.

### Step B — Conformance suite

```sh
env -u LD_LIBRARY_PATH python3 -m unittest discover -s tests/conformance
```

Pass: 101/101. Specific tests this phase touches:

- `test_plugin_release_metadata` — plugin VERSION matches references.
- `test_skill_metadata_versions_match_plugin_declarations` — all 52
  skills declare `version: "0.6.0"`.
- `test_plugin_framework_bundle.test_bundle_is_byte_identical` — no
  drift between canonical and bundle (no framework/ changes in this
  phase, so the bundle stays in sync without re-sync).

### Step C — Mock-mode acceptance

```sh
bash tests/scripts/test-acceptance.sh url-shortener --no-live
```

Pass: PASS outcome; no regression. Mock mode does not exercise the
saga refactor's subprocess logic (subprocess invocations don't run
in mock mode), so this only catches structural regressions.

### Step D — Live BRD cascade

Per Design 6. Two scenarios, both acceptable. ~$3-5 cost. ~30-90 min
wall-clock (Scenario A: ~50 min; Scenario B: two invocations totaling
~60 min).

### Step E — saga.json inspection (G-R9)

After live run, validate `.aidoc/review/01_BRD/<BRD-id>/saga.json`
against the schema. Reuse Phase 1's smoke-test pattern (Phase 1 plan
Step D2) with live-run-specific assertions:

```python
import json
from pathlib import Path

saga = json.loads(Path(".aidoc/review/01_BRD/BRD-01/saga.json").read_text())
schema = json.loads(Path("framework/governance/saga.schema.json").read_text())

# All required fields present
for key in schema["required"]:
    assert key in saga, f"saga.json missing required field: {key}"

# Status in valid enum
assert saga["status"] in schema["properties"]["status"]["enum"]

# All 5 BRD-crew personas have branch entries
expected_personas = {"business_analyst", "architect", "auditor",
                     "chaos_engineer", "security_engineer"}
got = set(saga["branches"].keys())
assert got >= expected_personas, f"missing branches: {expected_personas - got}"

# transitions[] non-empty and ordered
assert len(saga["transitions"]) >= 5, "transitions[] too short"

# Final status is terminal
assert saga["status"] in {"CLOSED", "PARTIAL_TIMEOUT", "ESCALATED"}, \
    f"non-terminal final status: {saga['status']}"

# G-R1 invariant: no `from: PARTIAL_TIMEOUT` transitions
for t in saga["transitions"]:
    assert t.get("from") != "PARTIAL_TIMEOUT", \
        f"invalid transition from PARTIAL_TIMEOUT detected: {t}"

print("saga.json: live-run validation OK")
```

Pass criteria: all assertions pass.

### Step F — Resume verification (if Scenario B observed)

If the first invocation hits PARTIAL_TIMEOUT, re-invoke the autopilot
manually:

```sh
claude --plugin-dir <plugin-dir> -p \
  "/aidoc-flow:doc-brd-autopilot Resume BRD-<id> at <path>."
```

Pass: resumed invocation reads saga.json, completes the remaining
phases, final saga `status: CLOSED`.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Nested `claude -p` subprocesses fail in some environments (e.g., no `--plugin-dir` access) | Test-acceptance.sh already does exactly this (its dispatch loop spawns `claude -p` for each skill). Existing pattern; same env requirements. Phase 2's live verification IS the existence proof. |
| R2 | LLM cooperative enforcement fails — autopilot ignores the break-circuit and SIGTERM fires | OS-level `timeout 1800` is the hard floor. Saga.json reflects last successful checkpoint; both outcomes are valid graceful-degradation states per Phase 1 spec. Verification accepts either. |
| R3 | Resume logic is fragile — autopilot might mis-parse saga.json or transition incorrectly on resume | The transition table in REVIEW_SAGA.md is the contract. Phase 2's SKILL prompt embeds the transitions tabularly. Resume is best-effort; if it fails, the user can manually delete saga.json to force fresh start. Document this in the CHANGELOG. |
| R4 | autopilot's parent session budget (1800s) is too tight to complete even one phase + saga update + dispatch the next | Plain dispatch overhead is ~5-10s per phase boundary. The autopilot's clock is dominated by SUBPROCESS wait time. With 4 phases × ~600s wait avg = ~2400s, parent autopilot exhausts budget before completing all 4 phases — that's where the PARTIAL_TIMEOUT / resume pattern kicks in. Expected behavior; not a bug. |
| R5 | Harness (`test-acceptance.sh`) doesn't know to resume PARTIAL_TIMEOUT | Step 10 is optional harness change; Scenario A may pass without it. If Scenario B is observed, add the re-invocation logic in Step 10. |
| R6 | Plugin v0.6.0 breaks downstream consumers expecting the prior `.aidoc/review/` shape | `saga.json` is additive (a new file); existing slot files, verdict.json, report.md are unchanged. Migration note in CHANGELOG. The "breaking" classification is conservative — actual breakage is limited to consumers that strictly enumerate files in the directory (rare). |
| R7 | SKILL prompts grow significantly larger; LLM context budget concerns | Saga interaction sections are ~50-80 lines per skill. Manageable. The transition table is embedded once per SKILL; could be cross-referenced to REVIEW_SAGA.md if size becomes an issue (Phase 4 retrospective). |
| R8 | Live verification cost ~$3-5 is wasted if a bug is found mid-run | The plan front-loads static + conformance verification (Steps A-C, all free). Live verification (Step D) runs only after the cheap checks pass. Cost is bounded by `--cost-cap=$22` in test-acceptance.sh. |
| R9 | The current `doc-brd-autopilot` SKILL's existing single_pass linear pipeline interferes with the new saga-driven loop | The saga loop is gated on `review_mode: team`; single_pass falls through to the existing linear pipeline unchanged. Both code paths coexist. |
| R10 | Resume logic creates a hard-to-test edge case (PARTIAL_TIMEOUT → resume → CLOSED) | Live verification Step F covers this when applicable. The deterministic mock mode does not exercise it. A unit-test-style fixture for the resume case may be a follow-up. |
| R11 | Run-vs-branch state ambiguity in REVIEW_SAGA.md transition table (G-R10) — the transitions table mixes per-run states (PREPARED, FANOUT_STARTED, FANIN_REDUCED, SYNTHESIZED, CLOSED) with per-branch states (BRANCH_RUNNING, BRANCH_COMPLETED, etc.). The actual transition from run-level FANOUT_STARTED to run-level FANIN_REDUCED isn't explicit; it's mediated by per-branch transitions. | Phase 2 implements the ambiguity verbatim (transitions[] entries carry `scope: "run"` or `"branch:<persona>"`, disambiguating at the journal level). Phase 3's cross-platform conformance test may surface the ambiguity as a parity issue between the two platforms' interpretations; the resolution is a follow-up amendment to REVIEW_SAGA.md (e.g., add explicit run-level transitions BRANCH_COMPLETED → FANIN_REDUCED only when all per-branch entries are BRANCH_COMPLETED). Flagged for Phase 3 review; not blocking Phase 2 impl. |

## Review log

### Pass 1 — 2026-06-05T14:30:00Z (initial draft)

- The autopilot refactor centers on a saga-driven loop: read saga.json,
  determine next phase, dispatch via `Bash → claude -p` subprocess,
  update saga, check break-circuit, loop. Each phase gets its own fresh
  ORCHESTRATOR_TIMEOUT via the subprocess.
- Resumability via PARTIAL_TIMEOUT solves the autopilot's parent-budget
  problem: the parent session may not complete all 4 phases in one
  invocation, but the journal preserves state and re-invocation
  resumes.
- Each BRD-layer orchestrator skill gets its own break-circuit
  checkpoint boundary per REVIEW_SAGA.md's table.
- Plugin VERSION 0.5.0 → 0.6.0 (SemVer-major; saga.json is a new
  public artifact). 9-place fanout with sed bump for 52 skills.

### Pass 2 — 2026-06-05T14:30:00Z (self-review)

- **G-Q1 — saga.json file path stability across iterations**. Each
  iteration of the create→review→revise loop reuses the SAME
  saga.json file (not per-iteration). The `iteration` field is
  incremented; the `transitions[]` log records each iteration's
  phases. Verified against the design.
- **G-Q2 — autopilot's parent budget vs subprocess budgets**. The
  parent autopilot session has ORCHESTRATOR_TIMEOUT=1800s. Each
  subprocess it spawns has its OWN 1800s timeout. But the parent
  WAITS for each subprocess, so parent wall-clock ≈ sum of subprocess
  wall-clocks. For 4 phases × ~10-15min = 40-60 min, parent
  ORCHESTRATOR_TIMEOUT (30 min) is insufficient. R4 + resume pattern
  is the answer.
- **G-Q3 — `current_phase` field is plugin-specific enrichment per
  the Phase 1 schema (G24 matrix)**. It's optional in saga.schema.json
  but the autopilot REQUIRES it for resume logic. This is fine — the
  schema marks it optional (other engines may omit it); the plugin
  populates it. Documented in REVIEW_SAGA.md §"Optional fields".
- **G-Q4 — Break-circuit checkpoint granularity per skill**.
  Autopilot fires between phases. Audit fires before synthesizer.
  Fixer fires between multi-lens validation dispatches. Review-team
  fires between fan-out and reduce. All four boundaries are codified
  in REVIEW_SAGA.md per Phase 1's Design 1 §"Break-circuit policy
  contract".
- **G-Q5 — How does the autopilot subprocess invocation pass
  saga.json context to the child claude -p**? The child `claude -p`
  doesn't inherit the parent's tool state. But the child can `Read`
  the saga.json file from disk; the path is conventional
  (`.aidoc/review/01_BRD/<BRD-id>/saga.json`). The audit/fixer
  SKILLs' new §"Saga interaction" instructs the child to read/update
  saga.json. The path is passed in the invocation's brief.
- **G-Q6 — Pre-commit / markdownlint constraints on long SKILL
  files**. Phase 1's SKILL files were already large; Phase 2's
  additions are ~80 lines per file. Should still lint clean.

### Pass 3 — 2026-06-05T14:30:00Z (codebase cross-check)

- **G-Q7 — Verify the existing `doc-brd-autopilot/SKILL.md` is open
  to the saga refactor**: yes, the §"Generation Loop (review_mode:
  team)" section is the replacement target. The §"Linear Pipeline
  (review_mode: single_pass)" stays unchanged.
- **G-Q8 — Verify `BRD-id` resolution**: per BRD-RT-002, the short
  artifact ID (`BRD-01`) is the source; the nested folder name
  (`BRD-01_kyc_onboarding`) is NOT. saga.json path uses BRD-id.
- **G-Q9 — Verify the existing `_pick_timeout_for` in
  `tests/scripts/test-acceptance.sh` covers nested `claude -p`
  invocations**: yes, when autopilot Bashes `timeout 1800 claude -p
  /aidoc-flow:doc-brd-audit ...`, the outer `timeout` is from the
  autopilot's own SKILL prompt (it uses `timeout 1800` literally as
  in the design). The nested claude process has its own 1800s
  budget. (Note: the parent autopilot is wrapped by
  test-acceptance.sh's `timeout 1800 claude -p
  /aidoc-flow:doc-brd-autopilot`; the inner subprocess wrappers
  spawn another `timeout 1800 claude -p ...` ⇒ two separate timer
  trees, OS handles it via separate child PIDs.)
- **G-Q10 — Existing skill `frontmatter framework_spec_version`**:
  all 52 skills currently declare `0.13.0` (Phase 1's bump). Phase 2
  does NOT change this — only the plugin VERSION (which is a
  separate field) bumps. The sed in Step 6 targets
  `^    version: "0.5.0"` (the plugin-own version), not
  framework_spec_version.
- **G-Q11 — review-team/SKILL.md already cites D-0005 + D-0031**
  per Phase 1 step 12. Design 4 adds the saga journal subsection
  underneath; doesn't conflict with the citation.
- **G-Q12 — Live verification cost estimate**: BRD-RT-004's live
  run was 3535s × ~$0.001/s ≈ $3.5. Adding nested-subprocess
  overhead (each subprocess loads context fresh) may slightly
  increase cost; bound at $5 max per Scenario A. Scenario B is
  TWO sessions, so ~$6-8 total.
- **G-Q13 — Verify the schema validates a plugin-shaped
  saga.json**: design's example in §1 has all 11 required fields
  per saga.schema.json's `required: [...]` array. Verified by
  Phase 1's smoke test pattern.
- **G-Q14 — Resume logic and the formal transition table**.
  REVIEW_SAGA.md's transition table doesn't have explicit
  `PARTIAL_TIMEOUT → X` arrows. The autopilot's §4 resume logic
  treats PARTIAL_TIMEOUT as a checkpoint fence — the resume
  appends a fresh transition from PARTIAL_TIMEOUT to the
  re-entry state (e.g., FANOUT_STARTED, BRANCH_COMPLETED). This is
  consistent with the spec's "terminal-this-process; future
  invocations resume by re-entering one of the allowed source
  states" wording. If Phase 3's conformance test catches this as
  schema violation, the spec's transition table may need a
  Pass-X amendment to add explicit PARTIAL_TIMEOUT → allowed-set
  arrows. Flag for review.

Plan ready for impl.

### Pass 4 — 2026-06-05T15:30:00Z (post-merge gap-review, per CLAUDE.md two-cycle rule)

After PR #85 merged, applied the freshly-merged
`CLAUDE.md §"Development workflow" item 2` two-cycle plan review rule
to this plan: read it with fresh eyes against the codebase. Surfaced
**10 gaps** that the inline Pass 1-3 missed. The Pass 3 G-Q14
self-flag about PARTIAL_TIMEOUT transitions was technically known
but inadequately resolved; this pass folds the resolution in
concretely. All 10 gaps folded in place via this amendment commit.

**Critical (4):**

- **G-R1 — Resume transition logic violates the spec.** Pass 3's
  G-Q14 noted the issue; Pass 4 resolves it: PARTIAL_TIMEOUT is
  terminal-this-process per `framework/governance/REVIEW_SAGA.md`'s
  transition table. The resume mechanism does NOT append a
  `from: PARTIAL_TIMEOUT` transition (which would be illegal).
  Instead, the resumed run walks backward through `transitions[]`
  to find the pre-PARTIAL_TIMEOUT state and appends the next legal
  transition from THAT state. The PARTIAL_TIMEOUT entry remains in
  `transitions[]` as a checkpoint marker only. Design 1 §4 rewritten
  to reflect this; Step E (saga.json inspection) gains an explicit
  invariant check (no `from: PARTIAL_TIMEOUT` allowed).
- **G-R2 — Draft phase loses persona binding under subprocess
  invocation.** Subprocess pattern (`claude -p /aidoc-flow:doc-brd`)
  has no `subagent_type` CLI parameter, so the requirements-analyst
  binding moves INTO `doc-brd/SKILL.md`. Added new scope item 1a:
  edit `doc-brd/SKILL.md` to add a `## Draft mode (saga-driven)`
  section that dispatches `requirements-analyst` as a Task subagent
  for draft invocations.
- **G-R3 — Per-skill start epoch, not shared.** Each subprocess
  gets its own fresh 1800s timeout; checking elapsed against
  autopilot's start epoch would mis-fire. Renamed
  `$SAGA_DIR/.skill-start` to a per-skill convention:
  `.skill-start.autopilot`, `.skill-start.audit`, `.skill-start.fixer`,
  `.skill-start.review-team`. Updated Design 1 §1 (with table) and
  Design 2 break-circuit invocations.
- **G-R4 — Edge cases on entry undefined.** Plan now explicitly
  handles `status == CLOSED` (exit cleanly, "already done"),
  `status == ESCALATED` (do NOT auto-restart), and other in-flight
  states (treat as resume). Added §"4a. Edge cases on entry" to
  Design 1.

**Medium (3):**

- **G-R5 — Standalone audit/fixer behavior without saga.json**.
  Plan now specifies: standalone invocation (no saga.json present)
  SKIPS saga.json writes entirely (the audit/fixer is not the
  lifecycle owner; initializing one standalone would write
  inconsistent state). Existing blackboard slots + verdict.json +
  audit report behavior unchanged. Documented in Design 2.
- **G-R6 — Pre-Phase-2 leftover blackboard.** Added §"1a. Pre-Phase-2
  blackboard migration" to Design 1: if `$SAGA_DIR` has slot files
  but no saga.json (a pre-Phase-2 run), autopilot scaffolds a
  saga.json reflecting the existing slot state instead of treating
  as fresh.
- **G-R7 — Optional harness change concrete spec.** Replaced
  Step 10's vague "add re-invocation logic" with a concrete
  bash diff sketch: a `while [[ -f $saga_file ]] && status ==
  PARTIAL_TIMEOUT && resume_count < 2 ]]; do ... done` loop after
  the autopilot invoke in test-acceptance.sh's cascade dispatcher.

**Cosmetic / clarification (3):**

- **G-R8 — SemVer classification rewording.** Plan and CHANGELOG
  draft now classify v0.5.0 → v0.6.0 as **MINOR** (not BREAKING).
  Rationale: `saga.json` is purely additive; no existing file
  shapes change. Pre-1.0 SemVer MINOR is appropriate for "meaningful
  new capability" additions. Header metadata "Scope flag" updated;
  Design 5 CHANGELOG draft now begins with a rationale paragraph.
- **G-R9 — Verification Step E references Phase 1's smoke test
  pattern.** Step E replaced vague "inspect" with a concrete
  Python validation script (~20 lines) using the same shape as
  Phase 1's smoke test, plus live-run-specific assertions
  (5 BRD personas present in `branches`, no `from: PARTIAL_TIMEOUT`
  transitions per G-R1).
- **G-R10 — Run-vs-branch state ambiguity** in REVIEW_SAGA.md's
  transition table noted as R11 (new risk) and flagged for Phase 3
  review. Not blocking Phase 2 impl; the journal's `scope` field
  disambiguates at runtime.

**Net plan delta:**

- Scope items: 10 → 11 entries (added 1a for doc-brd/SKILL.md).
- Design 1: §1 gains per-skill start epoch table; §1a (pre-Phase-2
  migration); §3a (draft persona binding); §4 (resume logic
  rewritten); §4a (edge cases).
- Design 2: §"Before synthesizer dispatch" uses own start epoch;
  §"When invoked standalone" clarified.
- Design 5 (CHANGELOG): SemVer rationale prepended; classification
  is now MINOR.
- Step 10 (conditional harness): vague description replaced with
  concrete bash diff.
- Step E (verification): Python script with G-R1 invariant check.
- Risks: 10 → 11 entries (added R11 for run-vs-branch ambiguity).

No new spec-level changes needed for Phase 2 impl. The run-vs-branch
ambiguity (G-R10/R11) is flagged for potential Phase 3 spec
amendment but doesn't block Phase 2.

Plan ready for impl (Pass-4 amendments folded in).

### Pass 5 — 2026-06-05T15:45:00Z (re-review of patched plan, per CLAUDE.md two-cycle rule)

The new `CLAUDE.md §"Development workflow" item 2` requires a
second cycle: re-review the patched plan after Pass 4's gap fixes to
verify the patches didn't introduce new inconsistencies. This is the
mandated re-validation.

**P5-A — Scope item 5 was inconsistent with G-R8's new MINOR
classification.** The header metadata Scope flag + Design 5 CHANGELOG
were updated to MINOR in Pass 4, but the Scope-list item 5 (line 64)
still said "SemVer-major". Patched in this Pass 5 to read "MINOR per
Pass-4 G-R8" with a one-line rationale. Pass-1 review log entry on
line 870 also references "SemVer-major" — that's historical narrative
(documents what was believed at draft time) and is intentionally not
edited (would erase history).

**Other Pass-5 sanity checks** (all green):

- Scope item numbering convention (1, 1a, 2, 3, ...) is consistent —
  `1a` explicitly marks a sub-step of 1 (the doc-brd/SKILL.md edit
  added in Pass 4). Same pattern as prior plans.
- Per-skill start epoch files are correctly referenced throughout —
  `$START_EPOCH_FILE` is only used inside Design 1 (autopilot
  context), where it correctly resolves to `.skill-start.autopilot`.
  Designs 2 + 3 use their own per-skill epoch files directly.
- No remaining `from: PARTIAL_TIMEOUT` transition references in the
  plan (G-R1 fully addressed).
- All Pass-4 risk additions (R11) cross-reference cleanly to spec
  follow-ups; no orphaned references.

Pass 5 surfaced 1 cosmetic issue (P5-A), no new structural concerns.
The two-cycle rule's purpose ("verify cycle N's patches didn't
introduce new inconsistencies") is satisfied — only the single MINOR-
classification straggler in Scope item 5 was found, and it's now
fixed. The plan is ready for impl.

## Cross-references

### Within this plan family

- **Parent plan**: `plans/SAGA-PARITY-001-PLAN.md`
- **Phase 1**: `plans/SAGA-PARITY-001-PHASE-1-PLAN.md` (merged via
  #83 + #84 impl)
- **Phase 3** (next): Hermes alignment — pending plan
- **Phase 4** (after Phase 3): plugin propagation to PRD..IPLAN

### Predecessor decisions

- **D-0031** — promotes the saga lifecycle to spec
  (`plans/DECISIONS.md`).
- **D-0005** — original "no saga in plugin" (superseded in scope by
  D-0031).
- **D-0028** — ORCHESTRATOR_TIMEOUT (1800s) unified across orchestrator
  skills (the budget the per-phase subprocesses inherit).
- **D-0026** — verdict.json companion (the audit's output that
  coexists with saga.json).
- **D-0024** — BRD-layer team-mode dispatcher placement (the
  multi-lens fan-out pattern that the saga records).

### Spec authorities

- `framework/governance/REVIEW_SAGA.md` — the contract.
- `framework/governance/saga.schema.json` — the schema.
- `framework/governance/REVIEW_TEAM.md` — the operational semantics
  the saga records.
- `framework/governance/REVIEW_CREWS.yaml` — the per-layer crew the
  saga's `personas_requested` references.

### Forward (created or substantially edited by this plan)

- `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`
  (substantial refactor)
- `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md`
  (append saga interaction + break-circuit)
- `platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md`
  (append saga interaction + break-circuit)
- `platforms/claude-code-plugin/skills/review-team/SKILL.md`
  (append saga journal subsection)
- `.aidoc/review/01_BRD/<BRD-id>/saga.json` (the new runtime
  artifact)
- `platforms/claude-code-plugin/CHANGELOG.md` (BREAKING entry for
  v0.6.0)
