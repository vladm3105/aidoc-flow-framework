---
name: doc-brd-autopilot
description: Generate BRDs end-to-end from reference docs, a prompt, or an IPLAN - detect input, determine type, generate, validate, and run the audit/fix cycle. Use to create or batch-create BRDs.
metadata:
  tags:
    - sdd-workflow
    - layer-1-artifact
    - automation-workflow
  custom_fields:
    layer: 1
    artifact_type: BRD
    skill_category: automation-workflow
    upstream_artifacts: []
    downstream_artifacts: [PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.6.0"
    framework_spec_version: "0.13.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary, review_mode]
---

# doc-brd-autopilot

## Purpose

Automated **BRD generation pipeline**. From reference documents
(`docs/00_REF/`), a user prompt, or an implementation plan (`IPLAN-*`), it
analyzes the source, determines BRD type, generates a complete BRD, validates
readiness, maintains `BRD-00_index.md`, and drives the audit↔fix cycle to a
passing score — for one BRD or a batch.

**Layer**: 1. **Upstream**: optional REF/prompt/IPLAN input. **Downstream**: a
validated BRD + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-brd/SKILL.md` | BRD structure and authoring rules (generation) |
| `../doc-brd-audit/SKILL.md` | quality gate (scoring + findings) |
| `../doc-brd-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | element-ID standards |
| `../review-team/SKILL.md` | team-mode dispatcher (parallel persona subagent fan-out) |
| `../charts-flow/SKILL.md` | diagram contract tags (C4-L1, DFD-L1) |

Authoring style for the produced BRD is governed by
`${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` (inherited
via `doc-brd` and `doc-brd-audit`).

## Input Contract

Accepts: a target BRD id/path; a REF directory or file(s); a free-text prompt;
or an IPLAN path. Optional: score threshold (default 90), max fix iterations
(default 3), batch list. With no explicit input, treat the request as a prompt.

## Smart Document Detection

For each target, check whether the BRD already exists (nested folder
`docs/01_BRD/BRD-NN_{slug}/`):

- **Missing** → *generate* mode.
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

Determine `deliverable_type` (`code`/`document`/`ux`/`risk`/`process`) and BRD
type (Platform vs Feature) from the source content.

## Workflow

Resolve `review_mode` from `.aidoc/profile.yaml`; if unset, fall through
to the framework default `team` at gates per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`. Same
fallback applies to `audit_threshold`, `section_toggles`,
`active_layers`, and `glossary`.
The workflow has two shapes — the team-mode create→review→revise loop
(default at gates) and the single_pass linear pipeline (fallback).

1. **Input analysis** — classify the input (REF / prompt / IPLAN), locate
   reference material, and decide generate vs review-and-fix.
2. **Type & scope** — Platform vs Feature; for a Feature BRD, verify the
   referenced Platform BRD exists; reserve the next `BRD-NN`.

### Saga-driven generation loop (`review_mode: team`)

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`, the
plugin uses cooperative enforcement: this SKILL prompt directs the LLM
to read/write `saga.json`, validate transitions against the table in
REVIEW_SAGA.md, and dispatch each phase as a fresh `claude -p`
subprocess via the `Bash` tool. Each phase inherits its own
`ORCHESTRATOR_TIMEOUT=1800s` budget rather than sharing the autopilot's
parent budget; the saga.json journal preserves progress across
invocations, so a run that hits the soft deadline (1500s) can be
resumed by a subsequent invocation.

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §Operations
§Create: **one drafter, many reviewers** — parallel drafts do not merge
coherently.

#### 3. Saga setup (entry / resume)

Variables for the rest of this section:

- `SAGA_DIR=.aidoc/review/01_BRD/<BRD-id>/`
- `SAGA_FILE=$SAGA_DIR/saga.json`
- `START_EPOCH_FILE=$SAGA_DIR/.skill-start.autopilot`
- `SOFT_DEADLINE=1500` seconds (OS-level timeout is 1800s; 300s buffer
  per `REVIEW_SAGA.md` §"Break-circuit policy")

`<BRD-id>` is the short artifact ID (e.g. `BRD-01`), not the nested
folder name. The directory MUST exist before writing; create with
`Bash: mkdir -p $SAGA_DIR`.

**Per-skill start epoch** (per `REVIEW_SAGA.md`): every orchestrator
SKILL tracks elapsed time against its OWN epoch file. Each subprocess
that this autopilot spawns starts fresh, so it writes its own
`.skill-start.<skill>` file. The naming convention:

| Skill | Epoch file |
|---|---|
| `doc-brd-autopilot` | `$SAGA_DIR/.skill-start.autopilot` |
| `doc-brd-audit` | `$SAGA_DIR/.skill-start.audit` |
| `doc-brd-fixer` | `$SAGA_DIR/.skill-start.fixer` |

##### 3.1 Resolve the saga state

Inspect `$SAGA_FILE`. Possible cases:

- **File does not exist**: this is a fresh run. Continue to §3.2
  (initialize fresh).
- **File exists with `status` ∈ {`PREPARED`, `FANOUT_STARTED`,
  `BRANCH_RUNNING`, `BRANCH_COMPLETED`, `BRANCH_FAILED`,
  `BRANCH_COMPENSATING`, `FANIN_REDUCED`, `SYNTHESIZED`}**: prior run
  was interrupted before reaching a terminal state. Treat as resume
  (§3.4 below).
- **File exists with `status == "PARTIAL_TIMEOUT"`**: break-circuit
  fired in a prior invocation. Resume from the checkpoint marker
  (§3.4 below).
- **File exists with `status == "CLOSED"`**: saga already completed.
  Log `saga already CLOSED for <BRD-id>; iteration N complete` and
  exit cleanly (exit 0). Do NOT re-run unless the user has explicitly
  removed `$SAGA_FILE`.
- **File exists with `status == "ESCALATED"`**: prior run was
  escalated for human review. Do NOT auto-restart. Log `saga
  ESCALATED for <BRD-id>; human review required` and exit cleanly.

##### 3.2 Initialize fresh saga (when no saga.json present)

Check for **pre-Phase-2 blackboard migration** first: walk
`$SAGA_DIR/*.json`. If `<persona>.json` slot files are present (a
pre-Phase-2 run without saga.json), build a saga.json reflecting
the existing slot state:

- For each `<persona>.json` slot, add a `branches[<persona>]` entry
  with `status: "BRANCH_COMPLETED"`, `attempt: 0`,
  `started_at: <slot file mtime>`, `ended_at: <slot file mtime>`,
  and `branch_id: <12-char hash of "<run_id>|<persona>">`.
- Set saga `status: "BRANCH_COMPLETED"` (all crew slots present
  means fan-in is the next phase).
- Set `iteration: 1`, `current_phase: "re-review"` (re-audit
  defensively; we don't know if the existing slots are post-audit
  or post-fixer).
- Append a single backfill transition entry with `migration: true`
  extension field: `{"ts": "<now>", "from": null, "to":
  "BRANCH_COMPLETED", "scope": "run", "migration": true}`.

Otherwise (no slot files), initialize a clean saga:

```json
{
  "review_run_id": "<sha256-prefix-of: $artifact_path|$crew|$time_bucket>",
  "artifact_id": "<BRD-id>",
  "layer": "01_BRD",
  "personas_requested": ["business_analyst", "architect", "auditor",
                         "chaos_engineer", "security_engineer"],
  "status": "PREPARED",
  "iteration": 1,
  "current_phase": "draft",
  "created_at": "<now ISO 8601 UTC>",
  "updated_at": "<now ISO 8601 UTC>",
  "branches": {},
  "transitions": [
    {"ts": "<now>", "from": null, "to": "PREPARED", "scope": "run"}
  ],
  "compensation_actions": []
}
```

Write `$SAGA_FILE`. Then record the autopilot's start epoch:

```sh
Bash: mkdir -p $SAGA_DIR && date +%s > $START_EPOCH_FILE
```

##### 3.3 Phase dispatch loop

Until `status` reaches a terminal state (`CLOSED`, `ESCALATED`, or
`PARTIAL_TIMEOUT`):

**a. Break-circuit check** (before dispatching the next phase):

```sh
Bash: echo $(( $(date +%s) - $(cat $START_EPOCH_FILE) ))
```

If elapsed > `SOFT_DEADLINE` (1500s):

- Append transition: `{"from": "<current_status>", "to":
  "PARTIAL_TIMEOUT", "scope": "run", "ts": "<now>"}`.
- Set `status: "PARTIAL_TIMEOUT"`; preserve `current_phase` for
  resume.
- Update `updated_at`. Write `$SAGA_FILE`. Exit cleanly.

**b. Determine and dispatch next phase** based on `current_phase`:

| current_phase | Subprocess command | After subprocess exit 0 |
|---|---|---|
| `draft` | `Bash: timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p "/aidoc-flow:doc-brd Draft BRD-<id> at <path>; use BRD-TEMPLATE.yaml + the source input at <seed-path>. Write to docs/01_BRD/BRD-<id>_<slug>/."` | Transition: `PREPARED → FANOUT_STARTED`; set `current_phase: "review"` |
| `review` | `Bash: timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p "/aidoc-flow:doc-brd-audit Audit BRD-<id> at <path>. Iteration=<N>. saga.json at $SAGA_FILE."` | Read `verdict.json`; if PASS → `current_phase: "finalize"`; if FAIL → `current_phase: "fixer"` |
| `fixer` | `Bash: timeout 1800 claude --plugin-dir "$PLUGIN_DIR" -p "/aidoc-flow:doc-brd-fixer Fix BRD-<id> at <path> based on findings at <audit-report-path>. saga.json at $SAGA_FILE."` | Increment `iteration`; set `current_phase: "re-review"` |
| `re-review` | (same as `review` above) | If PASS → `current_phase: "finalize"`; if FAIL AND `iteration < 3` → `current_phase: "fixer"`; else set `status: "ESCALATED"` |
| `finalize` | Update `docs/01_BRD/BRD-00_index.md`. Append transitions: `BRANCH_COMPLETED → FANIN_REDUCED → SYNTHESIZED → CLOSED`. Set `status: "CLOSED"`. | Exit loop |

The audit and fixer subprocesses manage their own per-branch
transitions and break-circuit; they MUST update `$SAGA_FILE` on entry
and exit per their own SKILL.md `## Saga interaction` sections.

**c. Update saga.json after each subprocess returns**. Re-read
`$SAGA_FILE` to pick up any transitions the subprocess wrote. Validate
the new `status` against `REVIEW_SAGA.md`'s transition table —
invalid transitions are bugs to escalate, not to silently apply.

##### 3.4 Resume logic (G-R1: PARTIAL_TIMEOUT is checkpoint-marker only)

`PARTIAL_TIMEOUT` is terminal-this-process per `REVIEW_SAGA.md`'s
transition table — it has no allowed-next transitions. The resume
mechanism does NOT append a `from: PARTIAL_TIMEOUT` transition (which
would violate the spec). Instead:

1. Read the existing `$SAGA_FILE`.
2. Identify `current_phase` from the journal.
3. Re-record the autopilot's start epoch (`date +%s >
   $START_EPOCH_FILE`); this invocation's clock starts fresh.
4. Walk `transitions[]` backward to find the most recent transition
   whose `to` is NOT `PARTIAL_TIMEOUT`. That state is the resume
   point.
5. Set `status` to the resume point (the run can continue from
   here). Do NOT append a transition `from: PARTIAL_TIMEOUT`.
6. Continue from §3.3 phase dispatch loop. The next legal transition
   from the resume point is what gets appended.

For example, if the prior journal was:

```text
PREPARED → FANOUT_STARTED → BRANCH_RUNNING → BRANCH_COMPLETED →
PARTIAL_TIMEOUT (current_phase: fixer)
```

Resume sets `status: "BRANCH_COMPLETED"` and continues to the fixer
phase. The next transition appended would be `BRANCH_COMPLETED →
FANIN_REDUCED` (or similar) once the fixer completes.

The PARTIAL_TIMEOUT entry remains in `transitions[]` as a permanent
checkpoint record.

### Linear Pipeline (`review_mode: single_pass`)

Unchanged legacy behaviour — used when the profile says so, when `Task`
subagent dispatch is unavailable, or at write-time (`on_author`) where
cost is the primary concern.

3. **Generation** — produce the BRD per `../doc-brd/SKILL.md`: Document
   Control (Section 1) first, §3–§15 required sections (toggle §2
   Executive Summary per `section_toggles`), diagrams registry,
   appendix, §8 across the 7 categories, element IDs `BRD.NN.SS.xxxx`,
   diagram tags via `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-brd-audit/SKILL.md` from scratch in
   single_pass mode.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max:
   run `../doc-brd-fixer/SKILL.md` in single_pass mode, then re-audit.
   On pass, update `docs/01_BRD/BRD-00_index.md`; on exhausting
   iterations, flag for manual review.

## Execution Modes

- **Single** — one BRD (generate or review-and-fix).
- **Batch** — multiple BRDs, processed in **chunks of 3** to bound context;
  generate Platform BRDs before the Feature BRDs that depend on them.
- **Dry-run** — report the planned actions (type, sections, IDs) without
  writing files.

## Quality Gates

- Generation does not complete until the audit passes (score ≥ threshold, 0
  Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The BRD index is updated only after a BRD passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Referenced Platform BRD missing (Feature BRD) | stop; report the missing dependency |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the BRD |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-brd/SKILL.md` · Audit: `../doc-brd-audit/SKILL.md` · Fix:
  `../doc-brd-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-00_index.TEMPLATE.md`
