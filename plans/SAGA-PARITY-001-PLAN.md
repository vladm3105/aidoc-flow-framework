# SAGA-PARITY-001 — Lifecycle-Behavior Parity Between Plugin and Hermes via a Framework Saga Contract

| Field      | Value                                                     |
|------------|-----------------------------------------------------------|
| Task       | SAGA-PARITY-001                                           |
| Depends on | BRD-RT-001..004 (D-0024-D-0028, merged); CHAOS-SEC-SPLIT-001 (D-0030, merged); live BRD verification on 2026-06-05 |
| Status     | PLANNED — 2026-06-05T11:45:00Z                            |
| Feeds      | All per-layer team-mode follow-ups (PRD-RT-001 onward) — they inherit the saga contract |
| Scope flag | **Framework-spec change** — CHG-gated; framework spec 0.12.0 → 0.13.0. Multi-phase plan covering framework + plugin + Hermes. |

## Objective

Move the review-team lifecycle (create→review→revise loop with per-branch
state machine, journal, compensation events, and break-circuit) from a
**platform implementation detail** to a **framework-spec contract** that both
platforms implement. Achieve **lifecycle-behavior parity** in place of the
current implicit **output-shape parity** — both platforms then expose the
same observable saga lifecycle, journal schema, and break-circuit policy
while keeping their own runtime mechanisms (Python saga runtime for Hermes;
markdown SKILL + JSON + Bash subprocesses for the plugin).

Supersede **D-0005** (the 2026-05-26 "no saga in plugin" decision) with
**D-0031**, citing the new evidence (live BRD outer-loop timeout observed
during CHAOS-SEC-SPLIT-001 verification on 2026-06-05) and the project-level
parity goal that D-0005 did not contemplate.

## Background

### What's currently true

- **Hermes implements a full saga**: explicit state machine in
  `platforms/hermes/src/mcp_server/review/saga_models.py`
  (`_ALLOWED_TRANSITIONS`), a per-run journal via `saga_journal.py`, branch
  states (`SagaBranchState`), compensation events, deterministic IDs, and
  resumable runs across process boundaries.
- **The plugin has no equivalent**: `doc-<layer>-autopilot` runs the entire
  create→review→revise loop inside one `claude -p` session bounded by a
  single `ORCHESTRATOR_TIMEOUT=1800s`. The shared blackboard
  (`.aidoc/review/<NN>_<LAYER>/<id>/<lens>.json`) captures crew slot state
  but not outer-loop phase state.
- **Functional parity today is output-shape only**:
  `tests/conformance/test_review_report_parity.py` validates committed
  sample fixtures from both runners against a single
  `review_report.schema.json`. That is *terminal-state* parity, not
  *lifecycle* parity.

### The new evidence (2026-06-05 BRD live verification)

The CHAOS-SEC-SPLIT-001 verification run produced a live BRD cascade on the
new 5-lens crew. Results:

- The standalone audit + fixer + re-audit dual-dispatch path **succeeded**:
  audit (87) → fixer → re-audit (92, PASS). Total runtime 3535s.
- The monolithic `doc-brd-autopilot` invocation **timed out at 1800s** (exit
  124). The autopilot started the draft + review + revise iteration but
  could not complete the multi-lens fixer validation + re-audit within
  `ORCHESTRATOR_TIMEOUT`.
- The blackboard captured all 5 lens slots + verdict.json + two fix-validation
  slots (`chaos_engineer.fix_1.json`, `business_analyst.fix_1.json`). The
  partial-crew state is durably journaled — but the **autopilot's outer-loop
  phase state is not**. There is no way for an outside observer (or a
  subsequent autopilot invocation) to know which phases completed and which
  did not without inspecting timestamps and inferring.

### Why D-0005 needs to be reopened

D-0005's reasoning rested on two premises:

1. *"The saga exists to coordinate Hermes' external LLM-API fan-out, which
   can fail/timeout mid-flight and needs durable orchestration +
   compensation. The plugin's agents are Claude Code `Task` subagents whose
   lifecycle the harness manages — there is nothing to journal or
   compensate."*
2. *"The blackboard already gives the durable-slot/resume property and
   coverage/quorum gives graceful degradation."*

Both premises are correct for **partial-crew state** (one lens out of N
fails inside an otherwise-completing run). The blackboard handles this
cleanly: re-dispatch the missing lens, coverage records the partial state,
the gate degrades to low-confidence if quorum is missed.

What D-0005 did **not** contemplate is **partial-outer-loop state**: the
autopilot completes only some of its create→review→revise phases before the
process is killed. The harness sees only "the `claude -p` invocation timed
out"; it has no journal of WHICH phases ran, what iteration the loop was on,
or what would constitute a sensible resume point.

The 2026-06-05 live run is the existence proof. D-0005's "nothing to journal"
assertion is now factually incorrect — there *is* something to journal at
the outer-loop level, even though there isn't at the per-branch level.

### Why this is also a parity requirement

Even setting aside the timeout evidence: docs/PARITY.md as of merge of #80
documents an explicit *intentional* runtime divergence between the platforms
("Plugin: blackboard, no saga, per D-0005 | Hermes: saga retries /
compensation"). Every per-layer plan that follows (PRD-RT-001 onward)
inherits that divergence — and every reader of those plans has to context-
switch between the two platform mental models when reasoning about
resilience. That cost compounds as the cascade builds out across all 8
layers.

Promoting the saga lifecycle into the framework spec changes the parity
contract from **output-shape parity** to **lifecycle-behavior parity**:
both platforms expose the same observable states, transitions, and journal
shape. They keep distinct runtime mechanisms (Python saga vs SKILL+JSON+Bash),
but the observed lifecycle is identical. Conformance tests verify the
journal schema across both platforms.

## Scope

### In (entire plan, across 4 phases)

#### Phase 1 — Spec design + D-0031 supersession

- `framework/governance/REVIEW_SAGA.md` (new) — engine-agnostic saga
  lifecycle contract (state machine, transitions, journal schema,
  compensation events, break-circuit policy).
- `framework/governance/REVIEW_TEAM.md` — cross-reference REVIEW_SAGA.md
  from §Operations and §Resilience.
- `framework/governance/saga.schema.json` (new) — JSON schema for the
  per-run journal file that conformance can validate.
- `framework/VERSION` — 0.12.0 → 0.13.0 (CHG-gated spec bump).
- `plans/DECISIONS.md` — **D-0031** superseding D-0005's scope-narrowing
  premise; preserves D-0005's reasoning history.
- `docs/PARITY.md` — reframe from "output-shape parity" language to
  "lifecycle-behavior parity"; update the Review-team comparison table to
  cite REVIEW_SAGA.md; rewrite §"Parity proof" to add the new lifecycle
  conformance test alongside the existing report-shape test.
- Plugin + Hermes both bump `FRAMEWORK_SPEC_VERSION` to `0.13.0` (no
  implementation change yet — declares intent to conform).
- `platforms/claude-code-plugin/CHANGELOG.md` and project `CHANGELOG.md`
  entries.

#### Phase 2 — Plugin BRD-layer proof of concept

- `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md` —
  refactor to:
  - Maintain `saga.json` at `.aidoc/review/01_BRD/<BRD-id>/saga.json`.
  - Dispatch each phase (draft, review, fixer, re-review) via `Bash` →
    `claude -p /aidoc-flow:doc-brd-{audit,fixer}` subprocesses (each gets a
    fresh OS-level timeout, matching the existing ORCHESTRATOR_TIMEOUT
    via `_pick_timeout_for`).
  - Implement the break-circuit soft-deadline policy (check elapsed before
    each phase; if past soft deadline, write PARTIAL_TIMEOUT to saga.json
    and exit 0 cleanly).
  - Validate transitions using the JSON schema (or a tiny Python helper
    script if practical) before writing — the LLM enforces transitions by
    reading `_ALLOWED_TRANSITIONS` from the spec.
- `platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md` — append
  break-circuit policy + transition updates to saga.json.
- `platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md` — same.
- `platforms/claude-code-plugin/skills/review-team/SKILL.md` — describe the
  saga.json shape + transition responsibilities (it's the dispatcher that
  updates branch states).
- Plugin `VERSION` 0.5.x → 0.6.0 (breaking — adds a new contract).
- Live BRD verification: same shape as CHAOS-SEC-SPLIT-001's verification,
  with new pass criteria covering saga.json schema conformance.

#### Phase 3 — Hermes alignment + cross-platform conformance

- Audit Hermes' existing implementation against the new spec. State names
  (`PREPARED`, `FANOUT_STARTED`, `BRANCH_RUNNING`, `BRANCH_COMPLETED`,
  `BRANCH_FAILED`, `BRANCH_COMPENSATING`, `FANIN_REDUCED`, `SYNTHESIZED`,
  `ESCALATED`, `CLOSED`) and transitions in
  `saga_models.py:_ALLOWED_TRANSITIONS` already exist and are the source
  the spec adopts. Verify byte-for-byte.
- Add `PARTIAL_TIMEOUT` state to Hermes (the only new state the spec
  introduces; maps Hermes' SIGTERM-during-branch case to the same observable
  status the plugin reports via break-circuit).
- Update Hermes' saga schema export (if any) to match
  `framework/governance/saga.schema.json` exactly.
- New conformance test
  `tests/conformance/test_saga_lifecycle_parity.py` — validates that:
  - Both platforms' saga journals match `saga.schema.json`.
  - The state machine + transition table in REVIEW_SAGA.md exactly matches
    Hermes' `_ALLOWED_TRANSITIONS`.
  - Every plugin orchestrator SKILL.md
    (`doc-*-{audit,autopilot,fixer}`, 28 skills per BRD-RT-004's
    name-match) contains the `## Break-circuit policy` section
    (greppable invariant).
- Hermes `VERSION` patch bump (no functional behavior change beyond the
  PARTIAL_TIMEOUT addition).
- `platforms/hermes/docs/architecture/REVIEW_TEAM_CONFORMANCE.md` updated
  to cite REVIEW_SAGA.md.

#### Phase 4 — Plugin propagation (PRD..IPLAN)

- Apply Phase 2's pattern to the other 7 layer-autopilots
  (`doc-prd-autopilot`, `doc-ears-autopilot`, …, `doc-iplan-autopilot`)
  plus their `-audit` and `-fixer` companions.
- These are mechanical given the BRD reference implementation; each layer
  can be its own PR. PRD-RT-001 (already-drafted plan, currently on todo)
  is folded into this phase — its impl PR adopts the saga contract from
  the start instead of being retrofitted.
- Conformance test from Phase 3 expands its sweep to all 8 layers.

### Out (genuinely deferred)

- **Removing `doc-review` / `trace-check` stub skills** — deprecation
  target was pushed to v0.6.0 by CHAOS-SEC-SPLIT-001; the plugin reaching
  v0.6.0 in Phase 2 *could* land this, but it's tangential to the saga
  work and should be its own clean-up PR.
- **Full Hermes saga refactor / runtime change** — Phase 3 only requires
  the PARTIAL_TIMEOUT addition + schema conformance verification. Any
  larger restructure of Hermes' saga runtime is its own project.
- **REVIEW-TEAM-RUNNER-CACHING-001** (TODO-RT2) — orthogonal cost
  optimization; not in this plan.
- **Per-layer team-mode wirings that pre-date this work** (BRD-RT-001..004
  already merged) — they consume the new contract once Phase 2 lands; they
  do not need to be retroactively re-planned.

## Approach

### The saga lifecycle contract (the heart of the plan)

The contract is **the framework spec section REVIEW_SAGA.md**. The state
machine, transition table, journal schema, and break-circuit policy live
there. Both platforms implement the contract via their own runtime
mechanisms; conformance tests verify the observable behavior.

#### State machine (adopt Hermes' existing names verbatim)

```text
States:
  PREPARED              — saga created, no phase started
  FANOUT_STARTED        — dispatcher began fanning out crew
  BRANCH_RUNNING        — a branch (= one persona dispatch) is in flight
  BRANCH_COMPLETED      — branch returned a persona-output record
  BRANCH_FAILED         — branch returned error or non-conformant output
  BRANCH_COMPENSATING   — branch failed; compensation in progress (retry,
                          alternative dispatch, or graceful skip)
  FANIN_REDUCED         — synthesizer produced the deterministic reduce
  SYNTHESIZED           — narrative (advisory) layer produced
  ESCALATED             — terminal: escalated to human review
  CLOSED                — terminal: run completed cleanly
  PARTIAL_TIMEOUT       — NEW: terminal-this-process state. Break-circuit
                          or OS timeout fired; saga.json is durably
                          journaled and a future run can read this state
                          and decide to resume or escalate.

Transitions (engine-agnostic; promoted from Hermes' _ALLOWED_TRANSITIONS
verbatim, plus PARTIAL_TIMEOUT additions):
  PREPARED              → {FANOUT_STARTED, PARTIAL_TIMEOUT}
  FANOUT_STARTED        → {BRANCH_RUNNING, PARTIAL_TIMEOUT}
  BRANCH_RUNNING        → {BRANCH_COMPLETED, BRANCH_FAILED, PARTIAL_TIMEOUT}
  BRANCH_FAILED         → {BRANCH_COMPENSATING, ESCALATED, BRANCH_COMPLETED}
  BRANCH_COMPENSATING   → {BRANCH_RUNNING, ESCALATED}
  BRANCH_COMPLETED      → {FANIN_REDUCED, PARTIAL_TIMEOUT}
  FANIN_REDUCED         → {SYNTHESIZED, PARTIAL_TIMEOUT}
  SYNTHESIZED           → {CLOSED}
  ESCALATED             → {}     (terminal)
  CLOSED                → {}     (terminal)
  PARTIAL_TIMEOUT       → {}     (terminal-this-process; resume by new run
                                  reading the journal)
```

The asymmetry: PARTIAL_TIMEOUT can fire from most non-terminal states (the
break-circuit can trip during any phase). It cannot fire after
`SYNTHESIZED` because that's effectively done.

#### Journal schema (saga.schema.json)

```json
{
  "review_run_id":         "16-char deterministic hash (per Hermes' deterministic_review_run_id)",
  "artifact_id":           "BRD-01, PRD-02, etc. (short form)",
  "layer":                 "01_BRD | 02_PRD | ... | 08_IPLAN",
  "document_fingerprint":  "sha256 of the artifact at run start",
  "personas_requested":    ["architect", "business_analyst", ...],
  "status":                "<state from the state machine>",
  "iteration":             "create→review→revise iteration count (1-N)",
  "current_phase":         "draft | review | fixer | re-review | reduce | synthesize",
  "retry_count":           "integer",
  "created_at":            "ISO 8601 UTC",
  "updated_at":            "ISO 8601 UTC",
  "branches": {
    "<persona_name>": {
      "branch_id":         "12-char hash",
      "status":            "<branch state>",
      "attempt":           "integer",
      "started_at":        "ISO 8601 UTC | null",
      "ended_at":          "ISO 8601 UTC | null",
      "error_code":        "string | null"
    }
  },
  "transitions": [
    {"ts": "ISO 8601 UTC",
     "from": "<state>",
     "to": "<state>",
     "scope": "run | branch:<persona_name>"}
  ],
  "compensation_actions": [
    {"ts": "ISO 8601 UTC",
     "branch": "<persona_name>",
     "reason": "<error_code or human-readable>",
     "action": "retry | skip | escalate"}
  ]
}
```

This is the minimal schema that captures every observable state needed for
lifecycle parity. Hermes' existing `SagaRunState` is structurally identical
(its `compensation_actions` field already matches the schema). The plugin
will write this exact JSON shape.

#### Break-circuit policy contract

Every orchestrator SKILL (`doc-*-{audit,autopilot,fixer}`, 28 skills) MUST
include a `## Break-circuit policy` section with this behavioral contract:

```text
At skill start, record the start epoch:
  Bash: date +%s > <saga_dir>/.skill-start

Before each phase boundary (between Task subagent dispatches or before
each `claude -p` subprocess invocation), check elapsed time:
  Bash: echo $(( $(date +%s) - $(cat <saga_dir>/.skill-start) ))

If elapsed exceeds the platform's SOFT_DEADLINE (≤ OS timeout − 300s buffer):
  1. Do NOT dispatch the next phase.
  2. Append a transition entry to saga.json: from <current_state> → PARTIAL_TIMEOUT.
  3. Update saga.json status to PARTIAL_TIMEOUT with `current_phase` set
     to where the break-circuit fired.
  4. Exit 0 cleanly. The caller's next invocation can read saga.json
     and decide to resume, retry, or escalate.

If the LLM ignores the break-circuit and the OS sends SIGTERM, the
subprocess exits 124 and saga.json reflects the last successful checkpoint.
The journal is best-effort durable; the OS timeout is the hard floor.
```

The spec does NOT prescribe specific deadline values — platforms pick
numbers appropriate to their runtime. Plugin's ORCHESTRATOR_TIMEOUT=1800s
implies SOFT_DEADLINE ≈ 1500s; Hermes' per-branch timeouts come from
`persona_mappings.yaml` and have their own buffer.

#### Enforcement asymmetry (honest caveat in the spec)

The spec acknowledges:

- **Hermes** enforces transitions via Python code (`can_transition` raises
  on invalid transitions, append_compensation_event writes structured
  entries, runtime owns the state machine).
- **Plugin** enforces transitions cooperatively (SKILL.md tells the LLM
  to validate against the transition table before writing; the LLM follows
  the contract).

Same observable lifecycle, different enforcement. Conformance tests check
the observable artifact (the saga.json file), not the enforcement
mechanism. Worth a one-paragraph note in REVIEW_SAGA.md so future readers
don't get confused.

### D-0031 supersession reasoning

D-0031 is **not** a reversal of D-0005; it is an extension of D-0005's
scope. The structure:

1. **Preserve D-0005's core finding**: blackboard + coverage/quorum is
   sufficient for *partial-crew state*. Re-dispatching a single missing
   lens does not need saga compensation events. That part of D-0005 stays
   correct.
2. **Acknowledge D-0005's blind spot**: it pre-committed to "no saga at all"
   based on the premise that "there is nothing to journal." The
   2026-06-05 live BRD run is empirical evidence that there is something
   to journal at the *outer-loop* level — phase progression, iteration
   count, transitions between phases.
3. **Add the missing layer**: a minimal saga contract for outer-loop state
   that complements (does not replace) the blackboard.
4. **Acknowledge the parity dimension** D-0005 did not weigh: the project
   has since adopted lifecycle-behavior parity as an explicit goal (per
   user direction 2026-06-05); the divergence D-0005 accepted is now an
   architectural cost the project chooses to close.

D-0031 cites D-0005 explicitly, marks D-0005 as **superseded in scope**
(not deprecated outright — its blackboard-for-crew-state reasoning is still
the contract), and points forward to REVIEW_SAGA.md as the new authority
for outer-loop lifecycle.

## Phase-by-phase step sequence

### Phase 1 — Spec design + D-0031 (CHG-gated)

1. Draft `framework/governance/REVIEW_SAGA.md` with the state machine,
   transition table (adopted verbatim from `saga_models.py:_ALLOWED_TRANSITIONS`
   plus the PARTIAL_TIMEOUT additions), journal schema description, and
   break-circuit policy contract.
2. Draft `framework/governance/saga.schema.json` formally.
3. Update `framework/governance/REVIEW_TEAM.md` to cross-reference
   REVIEW_SAGA.md from §Operations §Create (the loop that consumes the
   saga) and §Resilience (partial-crew vs partial-loop distinction).
4. Bump `framework/VERSION` 0.12.0 → 0.13.0.
5. Add D-0031 entry to `plans/DECISIONS.md`, preserving D-0005's text
   unchanged (just adding the supersession note pointing to D-0031).
6. Update `docs/PARITY.md`:
   - Replace "output-shape parity" language with **lifecycle-behavior parity**.
   - Update §"Review team" intro to cite REVIEW_SAGA.md as the contract.
   - Update the comparison table to add a "Saga lifecycle" row showing
     both platforms now conform to the same state machine.
   - Update §"Parity proof" — keep the report-shape schema check, ADD the
     new lifecycle/saga-schema check (will be implemented in Phase 3).
   - Add a one-paragraph **Enforcement asymmetry** note (LLM cooperative
     vs Python preemptive).
7. Bump both platforms' `FRAMEWORK_SPEC_VERSION` to 0.13.0 (Phase 1's spec
   is the new contract; platforms declare intent to conform; full
   implementation arrives in Phases 2 and 3).
8. Project-level `CHANGELOG.md` and `platforms/claude-code-plugin/CHANGELOG.md`
   entries documenting the spec change.
9. Pass GATE-SPEC (CHG-D1) — verified by the spec-change CI workflow.

### Phase 2 — Plugin BRD-layer proof of concept

1. `doc-brd-autopilot/SKILL.md` — full refactor:
   - Replace the in-session create→review→revise loop with a saga-driven
     orchestration: read saga.json (or initialize), check current state,
     dispatch the next phase via Bash → `claude -p /aidoc-flow:doc-brd-{audit,fixer}`,
     update saga.json on return, loop.
   - Embed the state machine transition table inline (or as a referenced
     section); the LLM validates transitions before writing.
   - Embed the `## Break-circuit policy` section.
2. `doc-brd-audit/SKILL.md` — append:
   - A "Saga interaction" section saying: at start, transition the
     responsible branch(es) from `BRANCH_RUNNING` to either
     `BRANCH_COMPLETED` or `BRANCH_FAILED`. Append transition entry.
   - The `## Break-circuit policy` section (in case audit is invoked
     directly outside autopilot).
3. `doc-brd-fixer/SKILL.md` — append same saga + break-circuit content.
4. `review-team/SKILL.md` — describe the saga.json layout next to the
   blackboard layout; the orchestrator-mediated hub now writes a saga
   journal too.
5. Bump plugin `VERSION` 0.5.x → 0.6.0 (new contract introduced).
6. 9-place fanout for 0.6.0 (per CHAOS-SEC-SPLIT-001 pattern: plugin.json,
   marketplace.json, READMEs, docs, 52 skills' frontmatter version).
7. Plugin CHANGELOG entry.
8. Live BRD verification (next).

### Phase 3 — Hermes alignment + cross-platform conformance

1. Audit `platforms/hermes/src/mcp_server/review/saga_models.py` against
   the new spec; confirm every state name + transition matches. If any
   drift exists, decide spec-side adjustment or Hermes-side rename; pick
   one and apply it.
2. Add `PARTIAL_TIMEOUT` to Hermes' `_ALLOWED_TRANSITIONS` and to
   `SagaRunState` (it's a valid status string).
3. Verify `saga_journal.py` produces JSON matching
   `framework/governance/saga.schema.json` exactly; adjust field names if
   needed.
4. `platforms/hermes/docs/architecture/REVIEW_TEAM_CONFORMANCE.md` —
   update to cite REVIEW_SAGA.md as the source of truth for the
   lifecycle; remove or update any text that previously described the
   Hermes implementation as the canonical source.
5. New conformance test `tests/conformance/test_saga_lifecycle_parity.py`:
   - Parse `framework/governance/saga.schema.json`.
   - Validate sample fixtures from both platforms (`fixtures/saga/{hermes,plugin}_BRD-01_saga.json`)
     against the schema.
   - Assert state machine + transitions in REVIEW_SAGA.md
     match Hermes' `_ALLOWED_TRANSITIONS` exactly.
   - Grep-assert that every `doc-*-{audit,autopilot,fixer}` SKILL.md
     contains the `## Break-circuit policy` section (28 skills).
6. Hermes `VERSION` patch bump.
7. Hermes platform CHANGELOG (if maintained).

### Phase 4 — Plugin propagation (PRD..IPLAN)

1. Apply Phase 2's refactor pattern to the remaining 7 layer-autopilots
   and their audit/fixer companions. Each layer can be its own PR.
2. Conformance test from Phase 3 expands to cover all 8 layers.
3. PRD-RT-001 (currently on todo) is implemented as part of Phase 4 PRD
   work, adopting the saga contract from the start.
4. Per-layer live verifications (BRD has already happened in Phase 2; PRD,
   EARS, BDD, ADR, SPEC, TDD, IPLAN each get their own).

## Verification

### Phase 1 verification (free; lint + spec gates)

- `pre-commit run --files <changed-files>` — green.
- `python tests/chg/spec_gate.py` (GATE-SPEC) — green (CHANGELOG updated;
  framework/VERSION bumped).
- Manual schema review of `saga.schema.json` for completeness.
- `python3 -m unittest discover -s tests/conformance` — current suite still
  green (no behavior change yet; just spec docs).

### Phase 2 verification (live; ~$3-5)

- Static lint + conformance — green.
- `bash tests/scripts/test-acceptance.sh url-shortener --no-live` — green
  (mock-mode regression check).
- Live BRD cascade — `bash tests/scripts/test-acceptance.sh url-shortener
  --live --phase=cascade --from-layer=brd --to-layer=brd --force`.
- **Pass criteria (8/8 mirroring BRD-RT-004 + new saga checks):**
  - `saga.json` present at `.aidoc/review/01_BRD/<BRD-id>/saga.json`,
    schema-conformant.
  - Final `status: CLOSED`, `iteration` ≤ 3, all transitions logged.
  - All 5 lens slots + verdict.json present (CHAOS-SEC-SPLIT-001 pass
    criteria still pass).
  - Driver-vs-synthesizer score agreement.
  - **Autopilot completes within budget this time** — because each phase is
    a fresh subprocess, the cumulative wall-clock can exceed 1800s
    without any single subprocess timing out.
  - If autopilot's outer process *does* time out (e.g., extended fix
    cycles), saga.json has `status: PARTIAL_TIMEOUT` (not the previous
    behavior of `error: claude -p exit 124` with no journal).
  - Re-invoking autopilot reads the PARTIAL_TIMEOUT saga.json and resumes
    from the documented `current_phase`.

### Phase 3 verification

- New conformance test `test_saga_lifecycle_parity.py` passes (cross-
  platform schema + transition + break-circuit greppable invariants).
- Hermes unit tests stay green (411/411 from CHAOS-SEC-SPLIT-001
  baseline).
- Manual: pick one BRD artifact, run through both platforms, confirm both
  produce schema-conformant saga.json with identical final state.

### Phase 4 verification

- Per-layer live verification (each layer's autopilot completes against
  the saga contract; pass criteria match BRD's).
- Full cascade verification — `--from-layer=brd --to-layer=iplan` —
  remains a separate cost decision; the saga contract should make it
  more reliable than today's monolithic-autopilot baseline.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | LLM ignores the break-circuit (cooperative enforcement fails) | OS-level `timeout 1800` SIGTERM remains the hard floor. PARTIAL_TIMEOUT is best-effort; the journal still reflects the last successful checkpoint up to SIGTERM. Verified by Phase 2's live run. |
| R2 | Adopting Hermes' state names locks the framework spec into Hermes-influenced vocabulary | The names (`PREPARED`, `BRANCH_RUNNING`, etc.) are general — they describe saga patterns in distributed-systems literature broadly. Not Hermes-coined. The alternative (rename) costs Hermes refactor with no semantic gain. Accepted. |
| R3 | Plugin SKILL prompts ballooning in size when each carries the saga + break-circuit content | The transition table + break-circuit policy can be a SHORT cross-reference to REVIEW_SAGA.md (e.g., 5-10 lines), not a full inline copy. The LLM reads the referenced spec. Skill files stay manageable. |
| R4 | saga.json schema drift between platforms over time | Cross-platform conformance test in Phase 3 (`test_saga_lifecycle_parity.py`) is the load-bearing check. Asserts schema + transition-table equality. Any drift breaks CI. |
| R5 | Bash + nested `claude -p` subprocesses introduce new failure modes (e.g., env not inherited correctly) | Test-acceptance.sh already does exactly this (it spawns `claude -p` to run skills with `--plugin-dir`). The pattern is proven. Phase 2's live BRD run is the existence proof for autopilot's use of it. |
| R6 | Phase 4's 7-layer propagation is mechanical but invites copy-paste errors | Conformance test (greppable break-circuit invariant) catches missing sections. Each per-layer PR runs its own static + mock checks. Live verification per layer is optional but recommended. |
| R7 | PRD-RT-001 (already drafted as todo) needs to be reworked to use the saga contract | PRD-RT-001 plan is uncommitted in working tree — natural to rebase its content onto SAGA-PARITY-001's Phase 4. The work is additive: PRD-RT-001 gets the saga.json contract baked in from day one. |
| R8 | Hermes' saga has fields beyond what saga.schema.json requires (Hermes-specific extras like `document_fingerprint`) | Schema is "minimum required"; platforms may add extension fields. saga.schema.json declares `additionalProperties: true` (or per-field allowlist) explicitly. Hermes keeps its extras. |
| R9 | Spec change blocks all per-layer work until Phase 1 lands | Phase 1 is plan-only PR + impl PR; impl PR is mostly markdown + JSON schema; turnaround is fast. Other unrelated work (e.g., the deprecated stub removal at v0.6.0) can proceed in parallel. |
| R10 | The framework spec previously did not own saga state; adding it now might conflict with downstream consumers | The two known consumers (Hermes, plugin) are both in this repo; no external consumers known. If any emerge later, the spec is well-versioned (0.12.0 → 0.13.0; consumers pin to a version). |

## Review log

### Pass 1 — 2026-06-05T11:45:00Z

Initial draft. Findings folded in:

- Adopted Hermes' state names + transitions verbatim from `saga_models.py`
  (verified earlier via direct read). Adds `PARTIAL_TIMEOUT` as the only
  new state (covers the break-circuit case the plugin needs and Hermes can
  use to represent SIGTERM-during-branch).
- D-0031 framed as supersession in *scope* (not reversal) — preserves
  D-0005's blackboard-for-crew-state finding, extends the contract to
  cover outer-loop state.
- 4-phase structure: spec design first (Phase 1 unblocks 2 + 3), then BRD
  proof (Phase 2), then Hermes alignment (Phase 3), then plugin
  propagation (Phase 4).
- PARITY.md reframing built into Phase 1.

### Pass 2 — 2026-06-05T11:45:00Z (self-review)

Re-read. Findings:

- **G1 — Phase 1 spec bump (0.12.0 → 0.13.0) is CHG-gated.** Verified by
  reference to D-0028's prior CHG flow. Same shape; no new gate
  machinery needed.
- **G2 — Plugin VERSION bump 0.5.x → 0.6.0.** This is the same major
  shift the deprecation timeline used (CHAOS-SEC-SPLIT-001 pushed
  `doc-review`/`trace-check` removal to v0.6.0). Phase 2 lands at
  0.6.0; the deprecated stubs are then optionally removable in a
  separate clean-up PR (out of scope for SAGA-PARITY-001 explicitly).
- **G3 — Enforcement asymmetry note is honest and important.** Already
  surfaced in the Approach section + the spec section + R1. Keep it
  visible.
- **G4 — Hermes' saga has Run state and Branch state mixed in one
  transition table.** Verified by reading `_ALLOWED_TRANSITIONS`
  directly. The spec adopts this mixing as-is (it's how Hermes models
  it; spec follows). Conformance test asserts byte-equality.
- **G5 — `current_phase` field in saga.json is plugin-flavored.**
  Hermes might not naturally have a `current_phase` concept (it has
  `status`). Decision: `current_phase` is plugin-only enrichment;
  saga.schema.json marks it as optional. Phase 3 verifies the
  required field set conforms across both.
- **G6 — Plan touches 30+ files in Phase 1 alone.** Manageable but
  worth flagging. Most are simple version bumps + CHANGELOG.

### Pass 3 — 2026-06-05T11:45:00Z (gap-review against codebase)

Cross-checked critical assumptions.

- **G7 — Hermes already has compensation_actions field**: confirmed in
  `SagaRunState.compensation_actions: list[dict]` — schema can use this
  shape directly. Good alignment.
- **G8 — Hermes' deterministic IDs**: `deterministic_review_run_id`,
  `deterministic_branch_id` — these are Hermes-specific implementation
  details. The spec should mention "implementations SHOULD use
  deterministic IDs for replayability" but not mandate a specific
  algorithm. Plugin can adopt the same algorithm or use UUIDs;
  conformance only cares about format (16-char/12-char strings).
- **G9 — `_resolve_review_branch_runtime` in saga_orchestrator.py reads
  timeout from `persona_mappings.yaml`**: Hermes-specific per-persona
  timeout config. Spec should mention "platforms MAY support per-branch
  timeouts; the OS-level enforcement is platform's responsibility" —
  Hermes already does, plugin uses OS `timeout` per subprocess. Both
  conform.
- **G10 — `test_review_report_parity.py` already enforces output-shape
  parity**. Phase 3's new `test_saga_lifecycle_parity.py` is additive,
  not a replacement. The two tests together enforce both layers of
  parity (lifecycle + output).
- **G11 — `tools/sync-plugin-framework.sh` syncs the plugin's bundled
  framework/ from canonical**. Phase 1's REVIEW_SAGA.md addition will
  need to re-run sync. Standard step.
- **G12 — Phase 2's live verification needs new pass criteria covering
  saga.json**. Added explicitly in §Verification: "saga.json present
  and schema-conformant", "Final status: CLOSED", "resume after
  PARTIAL_TIMEOUT works."
- **G13 — Per-layer plans for EARS-RT-001..IPLAN-RT-001 don't yet
  exist**. Phase 4 covers them inline OR they become per-layer plans
  inheriting from SAGA-PARITY-001's contract. Plan leaves this open;
  Phase 4 is mechanical and can be one PR per layer.
- **G14 — D-0005 has TWO entries in DECISIONS.md** (verified by grep —
  one at line 394 for "no saga", one at line 884 for "framework ships
  per-layer index templates"). D-0031 explicitly supersedes the
  *first* (line 394, "No saga for the plugin review runner"). The
  D-0031 entry text needs to call out the line/date to disambiguate
  from the duplicate D-0005 numbering.

Plan ready for implementation. Phase 1 (plan-only-then-impl) is the
starting line; Phases 2, 3, 4 follow.

## Cross-references

### Predecessor decisions

- **D-0005 (2026-05-26)** — "No saga for the plugin review runner":
  `plans/DECISIONS.md:394`. **Superseded in scope** by D-0031 (this plan).
  D-0005's blackboard-for-crew-state reasoning remains the contract.
- **D-0005 (2026-05-18)** — "framework ships per-layer index templates"
  `plans/DECISIONS.md:884` (separate entry with same number — D-0031
  text explicitly disambiguates).
- **D-0024..D-0028** — BRD-RT chain (review-team wiring, verdict-chain,
  ops fixes, orchestrator timeout). Foundation that SAGA-PARITY-001
  builds on.
- **D-0030 (CHAOS-SEC-SPLIT-001)** — lens partition. Live verification
  evidence is what triggered SAGA-PARITY-001.

### Existing artifacts referenced by this plan

- **`framework/governance/REVIEW_TEAM.md`** — current spec for
  review-team behavior. Phase 1 updates to cross-reference REVIEW_SAGA.md.
- **`framework/governance/REVIEW_CREWS.yaml`** — per-layer crews;
  unchanged by this plan.
- **`platforms/hermes/src/mcp_server/review/saga_models.py`** — current
  Hermes state machine. The spec adopts these names verbatim.
- **`platforms/hermes/src/mcp_server/review/saga_journal.py`** — current
  Hermes journal implementation. Phase 3 verifies schema conformance.
- **`tests/conformance/test_review_report_parity.py`** — existing
  output-shape parity test. Phase 3 adds a sibling lifecycle test.
- **`docs/PARITY.md`** — existing parity comparison doc. Phase 1
  reframes it for lifecycle-behavior parity.

### Forward references (created by this plan)

- **`framework/governance/REVIEW_SAGA.md`** (Phase 1) — the new spec
  section.
- **`framework/governance/saga.schema.json`** (Phase 1) — the new
  schema.
- **`tests/conformance/test_saga_lifecycle_parity.py`** (Phase 3) —
  the new conformance test.
- **`D-0031`** (Phase 1, in `plans/DECISIONS.md`) — the supersession
  decision.

### Project policy references

- `docs/PROJECT.md` §2 — independent version streams (framework,
  plugin, Hermes each version separately).
- `docs/PROJECT.md` §6 — CHG process (post-cutover governance for
  framework spec changes).
- `docs/TAGGING.md` — git tag namespace (framework/v0.13.0,
  claude-code-plugin/v0.6.0, hermes/vX.Y.Z).
