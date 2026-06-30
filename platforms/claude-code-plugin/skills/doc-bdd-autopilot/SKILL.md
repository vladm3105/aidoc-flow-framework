---
name: doc-bdd-autopilot
description: Generate BDD scenarios end-to-end from EARS, a prompt, or an IPLAN - detect input, generate YAML scenarios, validate, and run the audit/fix cycle. Use to create or batch-create BDD suites.
metadata:
  tags:
    - sdd-workflow
    - layer-4-artifact
    - automation-workflow
  custom_fields:
    layer: 4
    artifact_type: BDD
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS]
    downstream_artifacts: [ADR, SPEC, TDD, IPLAN]
    version: "0.23.0"
    framework_spec_version: "0.32.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary, review_mode]
---

# doc-bdd-autopilot

## Purpose

Automated **BDD generation pipeline**. From upstream EARS (`docs/03_EARS/`), a
user prompt, or an implementation plan (`IPLAN-*`), it analyzes the source,
generates a complete BDD suite of Given-When-Then scenarios, validates
readiness, maintains `BDD-00_index.md`, and drives the audit↔fix cycle to a
passing ADR-Ready score — for one BDD or a batch.

**Layer**: 4. **Upstream**: EARS (with BRD/PRD trace) / prompt / IPLAN input.
**Downstream**: a validated BDD + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-bdd/SKILL.md` | BDD structure, YAML scenario schema, and authoring rules (generation) |
| `../doc-bdd-audit/SKILL.md` | quality gate (ADR-Ready scoring + findings) |
| `../doc-bdd-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | element-ID standards |

## Input Contract

Accepts: a target BDD id/path; an upstream EARS id/path; a free-text prompt; or
an IPLAN path. Optional: score threshold (default 90), max fix iterations
(default 3), batch list. With no explicit input, treat the request as a prompt.

## Smart Document Detection

For each target, check whether the BDD already exists (nested folder
`docs/04_BDD/BDD-NN_{slug}/`):

- **Missing** → *generate* mode (from EARS / prompt / IPLAN).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

Determine `deliverable_type` (`code`/`document`/`ux`/`risk`/`process`) from the
inherited PRD/BRD chain. Verify the upstream EARS exists before generating.

## Model precheck

Advisory, best-effort. Surfaces the model you recommended for this layer; it
cannot switch the session model. Before invoking the driver:

1. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys, skip
   this section entirely (no output).
2. Resolve the recommended model: `model.per_layer.BDD` if set, else
   `model.default`.
3. Act on `model.precheck` (`warn` | `silent` | `block`):
   - `warn` (default) — print one line, then continue to the driver:
     `ℹ BDD recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
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
  --layer 04_BDD \
  --threshold 90
```

Use a generous timeout (≥1800s). Do not pre-analyze the input. Do not
read the upstream. Do not classify type/scope. The driver and its
dispatched subprocesses (`/aidoc-flow:doc-bdd` for draft,
`/aidoc-flow:doc-bdd-audit` for review, `/aidoc-flow:doc-bdd-fixer`
for fixer) handle all of that. The driver enforces the state machine
preemptively per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`; this
SKILL's job is to invoke it and report.

**Step 2 — After the driver returns, report.** Read
`.aidoc/review/04_BDD/${ARTIFACT_ID}/saga.json`. Final status MUST be
one of `CLOSED` (PASS), `ESCALATED` (terminal FAIL), or
`PARTIAL_TIMEOUT` (soft-deadline; resumable). Print the status, the
final score from `verdict.json` if present, and a 1-line summary.

**Step 3 — Index update (only on `CLOSED`).** Add a row to
`docs/04_BDD/BDD-00_index.md` referencing the new BDD; update the upstream artifact's
downstream entry.

That is the entire workflow in `team` mode. If you find yourself
doing anything else here — drafting prose, dispatching Task subagents,
invoking other slash commands — STOP, recognize that you are
bypassing the driver, and invoke the Bash command above instead.

### Linear Pipeline (`review_mode: single_pass`)

Unchanged legacy behaviour — used when the profile says so, when `Task`
subagent dispatch is unavailable, or at write-time (`on_author`) where
cost is the primary concern. The 5-step in-session pattern below
produces the BDD without saga.json; the harness's saga-journal
check will then fail the layer, so this mode is only appropriate for
manual dry-runs.

1. **Input analysis** — classify the input (EARS / prompt / IPLAN), locate the
   upstream EARS and its BRD/PRD trace elements, and decide generate vs
   review-and-fix.
2. **Type & scope** — confirm the referenced EARS (and its PRD/BRD elements)
   exist; map EARS statements to scenario categories; reserve the next `BDD-NN`.
3. **Generation** — produce the BDD per `../doc-bdd/SKILL.md`: Document Control
   first, all 5 sections, a `feature:` block, and a `scenarios:` YAML list across
   the five categories — each scenario a mapping with `given`/`when`/`then` phase
   lists, an element-level `ears:` list, `id` `BDD.NN.03.xxxx`, `type`/`priority`,
   inline `@threshold:` references, and a `spec_trace`. Sequence diagrams via
   `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-bdd-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-bdd-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/04_BDD/BDD-00_index.md`; on exhausting iterations, flag for manual
   review.

## Execution Modes

- **Single** — one BDD (generate or review-and-fix).
- **Batch** — multiple BDDs, processed in **chunks of 3** to bound context;
  generate in upstream EARS order.
- **Dry-run** — report the planned actions (scenarios, categories, IDs) without
  writing files.

## Quality Gates

- Generation does not complete until the audit passes (ADR-Ready ≥ threshold, 0
  Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The BDD index is updated only after a BDD passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Referenced upstream EARS/PRD/BRD missing | stop; report the missing dependency |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the BDD |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-bdd/SKILL.md` · Audit: `../doc-bdd-audit/SKILL.md` · Fix:
  `../doc-bdd-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-00_index.TEMPLATE.md`
