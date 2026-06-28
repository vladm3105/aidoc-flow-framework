---
name: doc-adr-autopilot
description: Generate ADRs end-to-end from an upstream artifact (BRD/PRD/EARS/BDD), a prompt, or an IPLAN - detect input, scope the decision, generate, validate, and run the audit/fix cycle. Use to create or batch-create ADRs.
metadata:
  tags:
    - sdd-workflow
    - layer-5-artifact
    - automation-workflow
  custom_fields:
    layer: 5
    artifact_type: ADR
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD]
    downstream_artifacts: [SPEC, TDD, IPLAN]
    version: "0.22.0"
    framework_spec_version: "0.29.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary, review_mode]
---

# doc-adr-autopilot

## Purpose

Automated **ADR generation pipeline**. From an upstream artifact
(BRD §8 / PRD §14 / EARS / BDD), a user prompt, or an implementation plan
(`IPLAN-*`), it analyzes the source, scopes the decision, generates a complete
Context-Decision-Consequences record, validates readiness, maintains
`ADR-00_index.md`, and drives the audit↔fix cycle to a passing score — for one
ADR or a batch.

**Layer**: 5. **Upstream**: BRD → PRD → EARS → BDD (or a prompt/IPLAN).
**Downstream**: a validated ADR + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-adr/SKILL.md` | ADR structure and authoring rules (generation) |
| `../doc-adr-audit/SKILL.md` | quality gate (scoring + findings) |
| `../doc-adr-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | element-ID standards |
| `../adr-roadmap/SKILL.md` | plans the set of ADRs a project needs |

## Input Contract

Accepts: a target ADR id/path; an upstream id (`BRD-NN`/`PRD-NN`/`EARS-NN`/
`BDD-NN`) or topic element id; a free-text prompt; or an IPLAN path. Optional:
score threshold (default 90), max fix iterations (default 3), batch list. With
no explicit input, treat the request as a prompt.

## Smart Document Detection

For each target, check whether the ADR already exists (nested folder
`docs/05_ADR/ADR-NN_{slug}/`):

- **Missing** → *generate* mode (synthesize the decision from the upstream).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

Determine `deliverable_type` (`code`/`document`/`ux`/`risk`/`process`,
inherited from upstream) and the originating topic (PRD §14, tracing back to
BRD §8) from the source content. One ADR records **one** decision.

## Model precheck

Advisory, best-effort. Surfaces the model you recommended for this layer; it
cannot switch the session model. Before invoking the driver:

1. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys, skip
   this section entirely (no output).
2. Resolve the recommended model: `model.per_layer.ADR` if set, else
   `model.default`.
3. Act on `model.precheck` (`warn` | `silent` | `block`):
   - `warn` (default) — print one line, then continue to the driver:
     `ℹ ADR recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
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
  --layer 05_ADR \
  --threshold 90
```

Use a generous timeout (≥1800s). Do not pre-analyze the input. Do not
read the upstream. Do not classify type/scope. The driver and its
dispatched subprocesses (`/aidoc-flow:doc-adr` for draft,
`/aidoc-flow:doc-adr-audit` for review, `/aidoc-flow:doc-adr-fixer`
for fixer) handle all of that. The driver enforces the state machine
preemptively per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`; this
SKILL's job is to invoke it and report.

**Step 2 — After the driver returns, report.** Read
`.aidoc/review/05_ADR/${ARTIFACT_ID}/saga.json`. Final status MUST be
one of `CLOSED` (PASS), `ESCALATED` (terminal FAIL), or
`PARTIAL_TIMEOUT` (soft-deadline; resumable). Print the status, the
final score from `verdict.json` if present, and a 1-line summary.

**Step 3 — Index update (only on `CLOSED`).** Add a row to
`docs/05_ADR/ADR-00_index.md` referencing the new ADR; update the upstream artifact's
downstream entry.

That is the entire workflow in `team` mode. If you find yourself
doing anything else here — drafting prose, dispatching Task subagents,
invoking other slash commands — STOP, recognize that you are
bypassing the driver, and invoke the Bash command above instead.

### Linear Pipeline (`review_mode: single_pass`)

Unchanged legacy behaviour — used when the profile says so, when `Task`
subagent dispatch is unavailable, or at write-time (`on_author`) where
cost is the primary concern. The 5-step in-session pattern below
produces the ADR without saga.json; the harness's saga-journal
check will then fail the layer, so this mode is only appropriate for
manual dry-runs.

1. **Input analysis** — classify the input (upstream id / prompt / IPLAN),
   locate the originating topic (PRD §14 → BRD §8), and decide generate vs
   review-and-fix.
2. **Decision scope** — confirm exactly one decision; reserve the next
   `ADR-NN`; verify the cited upstream artifacts exist.
3. **Generation** — produce the ADR per `../doc-adr/SKILL.md`: Document Control
   first (status `Proposed`/`Accepted`), §2–§10 + glossary + appendix, 2–3 alternatives with
   cost/fit, internal element IDs `ADR.NN.SS.xxxx`, cumulative tags
   `@brd @prd @ears @bdd`, the `@adr: ADR-NN` self-tag, architecture-flow
   diagram via `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-adr-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-adr-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/05_ADR/ADR-00_index.md`; on exhausting iterations, flag for manual
   review.

## Execution Modes

- **Single** — one ADR (generate or review-and-fix).
- **Batch** — multiple ADRs, processed in **chunks of 3** to bound context;
  generate ADRs that others depend on (`@depends: ADR-NN`) first.
- **Dry-run** — report the planned actions (decision scope, sections, IDs)
  without writing files.

## Quality Gates

- Generation does not complete until the audit passes (SPEC-Ready ≥ threshold,
  0 Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The ADR index is updated only after an ADR passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Cited upstream artifact missing (BRD/PRD/EARS/BDD) | stop; report the missing dependency |
| Source describes more than one decision | split into separate ADRs (one decision each) |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the ADR |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-adr/SKILL.md` · Audit: `../doc-adr-audit/SKILL.md` · Fix:
  `../doc-adr-fixer/SKILL.md`
- Decision planning: `../adr-roadmap/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-00_index.TEMPLATE.md`
