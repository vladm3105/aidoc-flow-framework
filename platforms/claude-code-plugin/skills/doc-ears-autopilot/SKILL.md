---
name: doc-ears-autopilot
description: Generate EARS documents end-to-end from a PRD, a prompt, or an IPLAN - detect input, validate readiness, generate formal statements, validate, and run the audit/fix cycle. Use to create or batch-create EARS.
metadata:
  tags:
    - sdd-workflow
    - layer-3-artifact
    - automation-workflow
  custom_fields:
    layer: 3
    artifact_type: EARS
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD]
    downstream_artifacts: [BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.25.0"
    framework_spec_version: "0.45.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary, review_mode]
---

# doc-ears-autopilot

## Purpose

Automated **EARS generation pipeline**. From an upstream PRD, a user prompt, or
an implementation plan (`IPLAN-*`), it analyzes the source, verifies upstream
readiness, generates a complete EARS document of atomic WHEN-THE-SHALL-WITHIN
statements, validates readiness, maintains `EARS-00_index.md`, and drives the
audit↔fix cycle to a passing score — for one EARS or a batch.

**Layer**: 3. **Upstream**: a PRD (and its BRD), a prompt, or an IPLAN.
**Downstream**: a validated EARS + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-ears/SKILL.md` | EARS structure, the four patterns, syntax rules |
| `../doc-ears-audit/SKILL.md` | quality gate (scoring + findings) |
| `../doc-ears-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | element-ID standards and `@threshold:` tags |

## Input Contract

Accepts: a target EARS id/path; an upstream PRD id/path; a free-text prompt; or
an IPLAN path. Optional: score threshold (default 90), max fix iterations
(default 3), batch list. With no explicit input, treat the request as a prompt.

## Smart Document Detection

For each target, check whether the EARS already exists (nested folder
`docs/03_EARS/EARS-NN_{slug}/`):

- **Missing** → *generate* mode (from the upstream PRD / prompt / IPLAN).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

Determine `deliverable_type` (`code`/`document`/`ux`/`risk`/`process`,
inherited from the upstream PRD) from the source content.

## Model precheck

Advisory, best-effort. Surfaces the model you recommended for this layer; it
cannot switch the session model. Before invoking the driver:

1. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys, skip
   this section entirely (no output).
2. Resolve the recommended model: `model.per_layer.EARS` if set, else
   `model.default`.
3. Act on `model.precheck` (`warn` | `silent` | `block`):
   - `warn` (default) — print one line, then continue to the driver:
     `ℹ EARS recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
   - `silent` — print nothing; continue.
   - `block` — print the line above plus `precheck=block: confirm you want to
     draft on the current model, or run /model <rec> first.`, then wait for the
     user to confirm before continuing.

## Workflow

### Saga-driven generation loop (`review_mode: team`)

**Step 1 — Invoke the driver. Period.** The harness sets `PREV_OUTPUT`,
`ARTIFACT_ID`, `ARTIFACT_PATH` env vars before invoking this SKILL.
Your first **orchestration** action MUST be the `Bash` tool (the Model precheck above runs first), running exactly:

```sh
python3 "${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py" \
  --layer 03_EARS \
  --allow-skip-permissions
```

`--allow-skip-permissions` lets the phases the driver dispatches write
files without a permission prompt — unattended autopilot requires it.
Drop the flag to run the same loop with Claude Code's normal prompts on.

Use a generous timeout (≥1800s). Do not pre-analyze the input. Do not
read the upstream. Do not classify type/scope. The driver and its
dispatched subprocesses (`/aidoc-flow:doc-ears` for draft,
`/aidoc-flow:doc-ears-audit` for review, `/aidoc-flow:doc-ears-fixer`
for fixer) handle all of that. The driver enforces the state machine
preemptively per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`; this
SKILL's job is to invoke it and report.

**Step 2 — After the driver returns, report.** Read
`.aidoc/review/03_EARS/${ARTIFACT_ID}/saga.json`. Final status MUST be
one of `CLOSED` (PASS), `ESCALATED` (terminal FAIL), or
`PARTIAL_TIMEOUT` (soft-deadline; resumable). Print the status, the
final score from `verdict.json` if present, and a 1-line summary.

**Step 3 — Index update (only on `CLOSED`).** Add a row to
`docs/03_EARS/EARS-00_index.md` referencing the new EARS; update the upstream artifact's
downstream entry.

That is the entire workflow in `team` mode. If you find yourself
doing anything else here — drafting prose, dispatching Task subagents,
invoking other slash commands — STOP, recognize that you are
bypassing the driver, and invoke the Bash command above instead.

### Linear Pipeline (`review_mode: single_pass`)

Unchanged legacy behaviour — used when the profile says so, when `Task`
subagent dispatch is unavailable, or at write-time (`on_author`) where
cost is the primary concern. The 5-step in-session pattern below
produces the EARS without saga.json; the harness's saga-journal
check will then fail the layer, so this mode is only appropriate for
manual dry-runs.

1. **Input analysis** — classify the input (PRD / prompt / IPLAN), locate the
   upstream PRD and its BRD, and decide generate vs review-and-fix.
2. **Readiness check** — confirm the upstream PRD exists and is EARS-Ready
   (score ≥ threshold); reserve the next `EARS-NN`. Categorize PRD requirements
   into the four EARS patterns (Event, State, Unwanted, Ubiquitous).
3. **Generation** — produce the EARS per `../doc-ears/SKILL.md`: Document
   Control first, all 5 sections, atomic WHEN-THE-SHALL-WITHIN statements,
   tabular Quality Attributes (percentile timing), element IDs `EARS.NN.SS.xxxx`,
   cumulative `@brd`/`@prd` tags, `@threshold:` references, state/sequence
   diagram tags via `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-ears-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-ears-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/03_EARS/EARS-00_index.md`; on exhausting iterations, flag for manual
   review.

## Execution Modes

- **Single** — one EARS (generate or review-and-fix).
- **Batch** — multiple EARS, processed in **chunks of 3** to bound context;
  generate each EARS only after its upstream PRD is confirmed ready.
- **Dry-run** — report the planned actions (patterns, sections, IDs) without
  writing files.

## Quality Gates

- Generation does not complete until the audit passes (BDD-Ready ≥ threshold, 0
  Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The EARS index is updated only after an EARS passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Upstream PRD missing or below EARS-Ready threshold | stop; report the missing/unready dependency |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the EARS |
| Vague/compound statement cannot be auto-resolved | flag for manual review, continue batch |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-ears/SKILL.md` · Audit: `../doc-ears-audit/SKILL.md` · Fix:
  `../doc-ears-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-00_index.TEMPLATE.md`
