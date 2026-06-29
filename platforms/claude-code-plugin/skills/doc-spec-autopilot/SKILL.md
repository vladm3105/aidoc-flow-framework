---
name: doc-spec-autopilot
description: Generate SPECs end-to-end from BDD/ADR, a prompt, or an IPLAN - detect input, generate the component spec, validate, and run the audit/fix cycle. Use to create or batch-create SPECs.
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - automation-workflow
  custom_fields:
    layer: 6
    artifact_type: SPEC
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN]
    version: "0.23.0"
    framework_spec_version: "0.29.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary, review_mode]
---

# doc-spec-autopilot

## Purpose

Automated **SPEC generation pipeline**. From upstream BDD/ADR documents, a user
prompt, or an implementation plan (`IPLAN-*`), it analyzes the source, generates
a complete component SPEC, validates readiness, maintains `SPEC-00_index.md`, and
drives the audit↔fix cycle to a passing score — for one SPEC or a batch.

**Layer**: 6. **Upstream**: BDD/ADR (and the EARS/PRD/BRD chain), or a
prompt/IPLAN input. **Downstream**: a validated SPEC + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-spec/SKILL.md` | SPEC structure and authoring rules (generation) |
| `../doc-spec-audit/SKILL.md` | quality gate (scoring + findings) |
| `../doc-spec-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | ID standards (dash-form `SPEC-NN`) |

## Input Contract

Accepts: a target SPEC id/path; an upstream BDD/ADR id or path; a free-text
prompt; or an IPLAN path. Optional: score threshold (default 90), max fix
iterations (default 3), batch list. With no explicit input, treat the request as
a prompt.

## Smart Document Detection

For each target, check whether the SPEC already exists (nested folder
`docs/06_SPEC/SPEC-NN_{slug}/`):

- **Missing** → *generate* mode (from BDD/ADR, prompt, or IPLAN).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

A `SPEC-NN` input is treated as the self type (review). A `BDD-NN`/`ADR-NN`
input is the upstream source: generate the matching SPEC if missing, else review.

## Model precheck

Advisory, best-effort. Surfaces the model you recommended for this layer; it
cannot switch the session model. Before invoking the driver:

1. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys, skip
   this section entirely (no output).
2. Resolve the recommended model: `model.per_layer.SPEC` if set, else
   `model.default`.
3. Act on `model.precheck` (`warn` | `silent` | `block`):
   - `warn` (default) — print one line, then continue to the driver:
     `ℹ SPEC recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
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
  --layer 06_SPEC \
  --threshold 90
```

Use a generous timeout (≥1800s). Do not pre-analyze the input. Do not
read the upstream. Do not classify type/scope. The driver and its
dispatched subprocesses (`/aidoc-flow:doc-spec` for draft,
`/aidoc-flow:doc-spec-audit` for review, `/aidoc-flow:doc-spec-fixer`
for fixer) handle all of that. The driver enforces the state machine
preemptively per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`; this
SKILL's job is to invoke it and report.

**Step 2 — After the driver returns, report.** Read
`.aidoc/review/06_SPEC/${ARTIFACT_ID}/saga.json`. Final status MUST be
one of `CLOSED` (PASS), `ESCALATED` (terminal FAIL), or
`PARTIAL_TIMEOUT` (soft-deadline; resumable). Print the status, the
final score from `verdict.json` if present, and a 1-line summary.

**Step 3 — Index update (only on `CLOSED`).** Add a row to
`docs/06_SPEC/SPEC-00_index.md` referencing the new SPEC; update the upstream artifact's
downstream entry.

That is the entire workflow in `team` mode. If you find yourself
doing anything else here — drafting prose, dispatching Task subagents,
invoking other slash commands — STOP, recognize that you are
bypassing the driver, and invoke the Bash command above instead.

### Linear Pipeline (`review_mode: single_pass`)

Unchanged legacy behaviour — used when the profile says so, when `Task`
subagent dispatch is unavailable, or at write-time (`on_author`) where
cost is the primary concern. The 5-step in-session pattern below
produces the SPEC without saga.json; the harness's saga-journal
check will then fail the layer, so this mode is only appropriate for
manual dry-runs.

1. **Input analysis** — classify the input (BDD/ADR / prompt / IPLAN), locate
   upstream material, and decide generate vs review-and-fix.
2. **Upstream readiness** — confirm the upstream ADR/BDD exist and are ready;
   reserve the next `SPEC-NN`.
3. **Generation** — produce the SPEC per `../doc-spec/SKILL.md`: Document Control
   first, all 8 sections in YAML, interfaces/data models/behavior at C4-L3,
   cumulative tags (`@brd @prd @ears @bdd @adr`), `@threshold` references for
   numbers, downstream `@tdd: TDD-NN` contract, diagram tags via
   `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-spec-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-spec-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/06_SPEC/SPEC-00_index.md`; on exhausting iterations, flag for manual
   review.

## Execution Modes

- **Single** — one SPEC (generate or review-and-fix).
- **Batch** — multiple SPECs, processed in **chunks of 3** to bound context.
- **Dry-run** — report the planned actions (sections, IDs, upstream tags)
  without writing files.

## Quality Gates

- Generation does not complete until the audit passes (TDD-Ready score ≥
  threshold, 0 Tier-1 errors) or the iteration cap is hit (then: manual-review
  flag).
- The SPEC index is updated only after a SPEC passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Referenced upstream ADR/BDD missing | stop; report the missing dependency |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the SPEC |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-spec/SKILL.md` · Audit: `../doc-spec-audit/SKILL.md` · Fix:
  `../doc-spec-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-00_index.TEMPLATE.md`
