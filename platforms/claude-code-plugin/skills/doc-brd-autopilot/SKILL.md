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
    version: "0.20.1"
    framework_spec_version: "0.23.0"
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

> **MANDATORY — DO THIS FIRST.** Your first and only action when
> `review_mode: team` (the framework default) is to invoke the saga
> driver via the `Bash` tool. **You MUST NOT** dispatch `Task` subagents
> directly, **MUST NOT** call `doc-brd`/`doc-brd-audit`/`doc-brd-fixer`
> directly via `SlashCommand` or otherwise, and **MUST NOT** generate
> the BRD in-session. The driver is the sole orchestration mechanism for
> the create-review-revise loop. Bypassing it produces a BRD without
> a saga.json journal — this empirically failed the 2026-06-05 BRD
> verification and is the *exact* bug this SKILL slim-down fixes.

### Saga-driven generation loop (`review_mode: team`)

**Step 1 — Invoke the driver. Period.** The harness sets `PREV_OUTPUT`,
`ARTIFACT_ID`, `ARTIFACT_PATH` env vars before invoking this SKILL.
Your VERY FIRST tool call MUST be the `Bash` tool, running exactly:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py" \
  --layer 01_BRD \
  --threshold 90
```

Use a generous timeout (≥1800s). Do not pre-analyze the input. Do not
read the seed. Do not classify type/scope. The driver and its
dispatched subprocesses (`/aidoc-flow:doc-brd` for draft,
`/aidoc-flow:doc-brd-audit` for review, `/aidoc-flow:doc-brd-fixer`
for fixer) handle all of that. The driver enforces the state machine
preemptively per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`; this
SKILL's job is to invoke it and report.

**Step 2 — After the driver returns, report.** Read
`.aidoc/review/01_BRD/${ARTIFACT_ID}/saga.json`. Final status MUST be
one of `CLOSED` (PASS), `ESCALATED` (terminal FAIL), or
`PARTIAL_TIMEOUT` (soft-deadline; resumable). Print the status, the
final score from `verdict.json` if present, and a 1-line summary.

**Step 3 — Index update (only on `CLOSED`).** Add a row to
`docs/01_BRD/BRD-00_index.md` referencing the new BRD.

That is the entire workflow in `team` mode. If you find yourself
doing anything else here — drafting prose, dispatching Task subagents,
invoking other slash commands — STOP, recognize that you are
bypassing the driver, and invoke the Bash command above instead.

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
