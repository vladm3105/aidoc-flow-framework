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
    version: "0.5.0"
    framework_spec_version: "0.12.0"
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

### Generation Loop (`review_mode: team`)

Per `${CLAUDE_PLUGIN_ROOT}/framework/governance/REVIEW_TEAM.md` §Operations
§Create: **one drafter, many reviewers** — parallel drafts do not merge
coherently.

3. **Draft** — dispatch ONE `Task` subagent (`subagent_type=requirements-analyst`,
   acting as the `business_analyst` lens / BRD author per the
   lens → agent mapping in `../review-team/SKILL.md`). Brief:
   `BRD-TEMPLATE.yaml`, the source input (REF/prompt/IPLAN),
   `../doc-brd/SKILL.md` as authoring rules. The author writes the BRD
   to its nested folder `docs/01_BRD/BRD-NN_{slug}/`.
4. **Review** — invoke `../doc-brd-audit/SKILL.md` (default pass-through
   `review_mode`); the audit fans out the BRD crew
   (`architect`/`business_analyst`/`auditor`/`chaos_engineer`/`security_engineer`) via `Task`
   subagents and synthesizes a combined report at
   `.aidoc/audit/01_BRD-audit.md`.
5. **Revise** — decide pass/fail by **reading the synthesizer's
   `verdict.json`** at `.aidoc/review/01_BRD/<BRD-id>/verdict.json`
   (where `<BRD-id>` is the short artifact ID, e.g. `BRD-01`):

   - `verdict.combined_status == "FAIL"` AND iterations < max →
     invoke `../doc-brd-fixer/SKILL.md` in team mode (it consumes the
     slot index, dispatches lens validators per blocking finding,
     persists patch-validation records). Then **GOTO step 4** for a
     fresh audit. Max iterations is 3 by default.
   - `verdict.coverage.quorum_met == false` → flag manual-review,
     halt (low-confidence outcome per `REVIEW_TEAM.md` §Resilience).
   - `verdict.combined_status == "PASS"` → finalize (go to step 6).

   When `verdict.json` is absent (e.g. single_pass run — synthesizer
   doesn't run in that mode), fall back to parsing the
   **Combined status** line in `.aidoc/audit/01_BRD-audit.md`. Never
   make this decision from the audit subagent's stdout summary or
   from the BRD's self-claimed PRD-Ready score. The written verdict
   is the gate; everything else is advisory.
6. **Converge or escalate** — on PASS update
   `docs/01_BRD/BRD-00_index.md` and finish; on max iterations with
   FAIL or quorum failure, write the manual-review flag and stop the
   batch item (continue with other items if any).

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
