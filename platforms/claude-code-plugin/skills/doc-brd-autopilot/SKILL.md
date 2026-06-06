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
    version: "0.6.1"
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

This SKILL is a **thin entry point** over the bundled
`${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py`, which drives the
create-review-revise loop **deterministically** under preemptive
enforcement per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`. The driver
script is the orchestration mechanism; this SKILL invokes it and
reports the result.

This SUPERSEDES the cooperative-enforcement loop that Phase 2 originally
embedded in this SKILL prompt, which empirically failed
(2026-06-05 verification: invalid transitions, non-terminal final
status, no subprocess dispatch). Per SAGA-PARITY-001 Phase 2
Amendment 1, all state-machine validation, transition enforcement,
break-circuit handling, and subprocess dispatch are now in
`saga_driver.py`.

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §Operations
§Create: **one drafter, many reviewers** — the driver enforces this
single-drafter contract on the dispatch sequence.

#### 3. Dispatch the saga driver

The harness sets `PREV_OUTPUT`, `ARTIFACT_ID`, `ARTIFACT_PATH` env
vars before invoking this SKILL (per Pass-4 A5/A6: deterministic
env-var contract, no LLM-cooperative prompt parsing). The driver
reads them; this SKILL only invokes it:

```sh
Bash: python3 "${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py" \
  --layer 01_BRD \
  --threshold 90
```

The driver writes `saga.json` to
`.aidoc/review/01_BRD/<ARTIFACT_ID>/saga.json` and prints one
`dispatch: <phase> ...` line per subprocess dispatched. Each phase
(`draft`, `review`, `fixer`, `re-review`) runs as a separate
`claude -p /aidoc-flow:doc-brd[-audit|-fixer]` subprocess with its
own `ORCHESTRATOR_TIMEOUT=1800s` budget. The driver enforces
`SOFT_DEADLINE=1500s` against its own wall clock and writes
`PARTIAL_TIMEOUT` if exceeded — that exit is resumable by a
subsequent invocation.

After the driver returns, post the final saga status (`CLOSED`,
`ESCALATED`, or `PARTIAL_TIMEOUT`) as the autopilot's outcome. On
`CLOSED`, also update `docs/01_BRD/BRD-00_index.md`.

#### 3.1 Driver contracts (reference)

The driver implements (see `${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py`
for the canonical version):

- **Entry / resume**: fresh saga.json init if absent;
  pre-Phase-2 blackboard migration if slot files exist;
  CLOSED/ESCALATED → exit; PARTIAL_TIMEOUT or in-flight → resume
  from the journaled `current_phase`.
- **Per-phase dispatch**: `draft` → `/aidoc-flow:doc-brd`;
  `review`/`re-review` → `/aidoc-flow:doc-brd-audit`;
  `fixer` → `/aidoc-flow:doc-brd-fixer`. Each runs as a separate
  `claude -p` subprocess with `timeout 1800`.
- **Transition validation**: every `from → to` is checked against
  the `_ALLOWED_TRANSITIONS` table (mirror of
  `framework/governance/REVIEW_SAGA.md`'s table). Invalid transitions
  raise; the driver does not silently apply them.
- **Break-circuit**: `SOFT_DEADLINE = 1500s` against the driver's own
  wall clock; exceeding it writes `PARTIAL_TIMEOUT` and exits cleanly.
- **Resume (G-R1)**: walks `transitions[]` backward to find the
  pre-PARTIAL_TIMEOUT state. Does NOT append a `from: PARTIAL_TIMEOUT`
  transition.
- **Verdict reading (A9)**: after each audit subprocess, reads
  `.aidoc/review/01_BRD/<id>/verdict.json`. Missing file →
  `ESCALATED` (audit failure), not `FAIL → fixer`.
- **Branch validation (A8)**: after each audit, repairs missing
  `branches[<persona>]` fields from slot file mtimes.
- **Iteration cap**: `MAX_ITERATIONS = 3`; if audit still FAIL after
  three fix cycles, escalate.

For the full state machine and journal schema see
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md` and
`saga.schema.json`.

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
