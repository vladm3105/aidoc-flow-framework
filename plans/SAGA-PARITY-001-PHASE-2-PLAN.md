# SAGA-PARITY-001 Phase 2 — Plugin BRD-layer impl (saga.json + Bash subprocess + break-circuit)

| Field      | Value                                                     |
|------------|-----------------------------------------------------------|
| Task       | SAGA-PARITY-001-PHASE-2                                   |
| Parent     | SAGA-PARITY-001 (`plans/SAGA-PARITY-001-PLAN.md`, merged) |
| Depends on | Phase 1 (D-0031; merged via PR #84) — REVIEW_SAGA.md + saga.schema.json are the contract this phase implements |
| Status     | PLANNED — 2026-06-05T14:30:00Z                            |
| Feeds      | Phase 3 (Hermes alignment; will compare against plugin's saga.json fixtures), Phase 4 (PRD..IPLAN propagation; reuses this BRD reference impl) |
| Scope flag | **Plugin breaking change** — plugin VERSION 0.5.0 → 0.6.0; SemVer-major because saga.json is a new public artifact in `.aidoc/review/<NN>_<LAYER>/<id>/` and consumers downstream may have come to expect the current shape |

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
5. **Bump plugin VERSION** 0.5.0 → 0.6.0 (SemVer-major; saga.json is a
   new public artifact, downstream consumers may have come to expect
   the prior shape).
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
`START_EPOCH_FILE=$SAGA_DIR/.skill-start`
`SOFT_DEADLINE=1500`  # seconds; OS-level timeout = 1800s; 300s buffer

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

#### 3a. Drafter

Dispatch via `Bash`:

```sh
timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p \
  "/aidoc-flow:doc-brd Draft BRD-<id> at <path>; use BRD-TEMPLATE.yaml + the source input at <seed-path> + doc-brd/SKILL.md as authoring rules. Write to docs/01_BRD/BRD-<id>_<slug>/."
```

The drafter is `requirements-analyst` invoked indirectly via the
`/aidoc-flow:doc-brd` slash — the SKILL prompt handles dispatch to
the appropriate author agent for the BRD layer (`business_analyst` lens
per `framework/governance/REVIEW_CREWS.yaml`).

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

### 4. Resume logic

If on entry `status == PARTIAL_TIMEOUT`, do NOT initialize fresh. Instead:

  1. Read the existing saga.json.
  2. Identify `current_phase` from the journal.
  3. Re-record start epoch (this invocation's clock starts fresh).
  4. Append transition: `PARTIAL_TIMEOUT → <last-current_phase's natural state>`
     (e.g., if current_phase was `fixer` and the prior run hit
     PARTIAL_TIMEOUT in BRANCH_COMPLETED, transition back to
     BRANCH_COMPLETED to resume from there).
  5. Continue from §2 phase dispatch loop.

The transition table in REVIEW_SAGA.md doesn't have an explicit
`PARTIAL_TIMEOUT → X` arrow — the spec says PARTIAL_TIMEOUT is
"terminal-this-process; future invocations resume by re-entering one
of the allowed source states." This SKILL implements that re-entry
by appending a fresh transition from PARTIAL_TIMEOUT to the resume
state, treating PARTIAL_TIMEOUT as a checkpointing fence.

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
"Layer audit" checkpoint boundary). Run:
```
Bash: echo $(( $(date +%s) - $(cat $START_EPOCH_FILE) ))
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

### When invoked standalone (single_pass mode)

If `review_mode: single_pass` is active, the audit does not produce
saga.json. Existing behavior preserved.
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
### Changed (BREAKING) — Plugin v0.5.0 → v0.6.0

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
10. **Optional harness change** to
    `tests/scripts/test-acceptance.sh`: if Scenario B (resume path)
    is needed to drive the live verification to CLOSED, add a
    conditional re-invocation when autopilot returns with saga
    status PARTIAL_TIMEOUT. Decision deferred to live verification:
    if Scenario A passes, no harness change needed; if Scenario B
    is observed, add the re-invocation logic.
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

### Step E — saga.json inspection

After live run, inspect `.aidoc/review/01_BRD/<BRD-id>/saga.json`:

- File exists, schema-conformant.
- `transitions[]` shows the lifecycle path.
- `branches{}` contains entries for each of the 5 BRD-crew personas.
- Final `status` is CLOSED or PARTIAL_TIMEOUT.

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
