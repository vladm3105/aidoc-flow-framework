---
name: doc-tdd-autopilot
description: Generate TDDs end-to-end from a SPEC, a prompt, or an IPLAN - detect input, plan the test pyramid, generate test cases, validate, and run the audit/fix cycle. Use to create or batch-create TDDs.
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - automation-workflow
  custom_fields:
    layer: 7
    artifact_type: TDD
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN]
    version: "0.23.2"
    framework_spec_version: "0.35.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary, review_mode]
---

# doc-tdd-autopilot

## Purpose

Automated **TDD generation pipeline**. From a SPEC component contract
(`docs/06_SPEC/`), a user prompt, or an implementation plan (`IPLAN-*`), it
analyzes the source, plans the test pyramid, generates a complete TDD (BDD→test
mapping, test-case definitions, thresholds, execution order), validates
readiness, maintains `TDD-00_index.md`, and drives the audit↔fix cycle to a
passing score — for one TDD or a batch.

**Layer**: 7. **Upstream**: SPEC (primary) + BDD (behavior source), drawing on
BRD/PRD/EARS/ADR. **Downstream**: a validated TDD + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-tdd/SKILL.md` | TDD structure and authoring rules (generation) |
| `../doc-tdd-audit/SKILL.md` | quality gate (scoring + findings) |
| `../doc-tdd-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | element-ID standards |

## Input Contract

Accepts: a target TDD id/path; a SPEC path/`SPEC-NN`; a free-text prompt; or an
IPLAN path. Optional: score threshold (default 90), max fix iterations
(default 3), batch list. With no explicit input, treat the request as a prompt.
The **primary source is SPEC** (the component contract); **BDD is the source of
truth for behavior** — never invent missing upstream artifacts.

## Smart Document Detection

For each target, check whether the TDD already exists
(`docs/07_TDD/TDD-NN_{component_slug}.yaml`):

- **Missing** → *generate* mode (one TDD per SPEC component).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

Determine the covered SPEC component and confirm `deliverable_type: code` from
the source content.

## Model precheck

Advisory, best-effort. Surfaces the model you recommended for this layer; it
cannot switch the session model. Before invoking the driver:

1. If `.claude/aidoc-flow.config.yaml` is absent, or has no `model.*` keys, skip
   this section entirely (no output).
2. Resolve the recommended model: `model.per_layer.TDD` if set, else
   `model.default`.
3. Act on `model.precheck` (`warn` | `silent` | `block`):
   - `warn` (default) — print one line, then continue to the driver:
     `ℹ TDD recommends model '<rec>'. If you're not on it, run /model <rec> (or set model.precheck: silent to hide this).`
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
  --layer 07_TDD \
  --threshold 90
```

Use a generous timeout (≥1800s). Do not pre-analyze the input. Do not
read the upstream. Do not classify type/scope. The driver and its
dispatched subprocesses (`/aidoc-flow:doc-tdd` for draft,
`/aidoc-flow:doc-tdd-audit` for review, `/aidoc-flow:doc-tdd-fixer`
for fixer) handle all of that. The driver enforces the state machine
preemptively per
`${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_SAGA.md`; this
SKILL's job is to invoke it and report.

**Step 2 — After the driver returns, report.** Read
`.aidoc/review/07_TDD/${ARTIFACT_ID}/saga.json`. Final status MUST be
one of `CLOSED` (PASS), `ESCALATED` (terminal FAIL), or
`PARTIAL_TIMEOUT` (soft-deadline; resumable). Print the status, the
final score from `verdict.json` if present, and a 1-line summary.

**Step 3 — Index update (only on `CLOSED`).** Add a row to
`docs/07_TDD/TDD-00_index.md` referencing the new TDD; update the upstream artifact's
downstream entry.

That is the entire workflow in `team` mode. If you find yourself
doing anything else here — drafting prose, dispatching Task subagents,
invoking other slash commands — STOP, recognize that you are
bypassing the driver, and invoke the Bash command above instead.

### Linear Pipeline (`review_mode: single_pass`)

Unchanged legacy behaviour — used when the profile says so, when `Task`
subagent dispatch is unavailable, or at write-time (`on_author`) where
cost is the primary concern. The 5-step in-session pattern below
produces the TDD without saga.json; the harness's saga-journal
check will then fail the layer, so this mode is only appropriate for
manual dry-runs.

1. **Input analysis** — classify the input (SPEC / prompt / IPLAN), locate the
   SPEC contract and the BDD scenarios it covers, and decide generate vs
   review-and-fix.
2. **Type & scope** — confirm the parent SPEC exists and is IPLAN-ready; map one
   TDD per SPEC component; reserve the next `TDD-NN`.
3. **Generation** — produce the TDD per `../doc-tdd/SKILL.md`: Document Control
   first, all 7 sections, test pyramid set, each BDD scenario mapped to test
   types/files, test-case IDs `TDD.NN.04.xxxx`, thresholds, Red→Green→Refactor
   order, cumulative tags @brd…@spec + @tdd self-tag; diagram tags via
   `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-tdd-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-tdd-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/07_TDD/TDD-00_index.md`; on exhausting iterations, flag for manual
   review.

## Execution Modes

- **Single** — one TDD (generate or review-and-fix).
- **Batch** — multiple TDDs, processed in **chunks of 3** to bound context;
  generate a TDD only after its parent SPEC component exists.
- **Dry-run** — report the planned actions (covered SPEC, test pyramid, IDs)
  without writing files.

## Quality Gates

- Generation does not complete until the audit passes (IPLAN-Ready ≥ threshold,
  0 Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The TDD index is updated only after a TDD passes.
- Test files are declared before implementation (TDD order); fresh audit every
  cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Parent SPEC missing or below IPLAN-Ready threshold | stop; report the upstream dependency |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the TDD |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-tdd/SKILL.md` · Audit: `../doc-tdd-audit/SKILL.md` · Fix:
  `../doc-tdd-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-00_index.TEMPLATE.md`
