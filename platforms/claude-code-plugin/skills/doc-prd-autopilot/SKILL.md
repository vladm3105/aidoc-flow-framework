---
name: doc-prd-autopilot
description: Generate PRDs end-to-end from a BRD, a prompt, or an IPLAN - detect input, derive scope, generate, validate, and run the audit/fix cycle. Use to create or batch-create PRDs.
metadata:
  tags:
    - sdd-workflow
    - layer-2-artifact
    - automation-workflow
  custom_fields:
    layer: 2
    artifact_type: PRD
    skill_category: automation-workflow
    upstream_artifacts: [BRD]
    downstream_artifacts: [EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.9.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary]
---

# doc-prd-autopilot

## Purpose

Automated **PRD generation pipeline**. From an upstream BRD, a user prompt, or
an implementation plan (`IPLAN-*`), it analyzes the source, derives product
scope, generates a complete PRD, validates EARS-readiness, maintains
`PRD-00_index.md`, and drives the audit↔fix cycle to a passing score — for one
PRD or a batch.

**Layer**: 2. **Upstream**: a BRD (or prompt/IPLAN input). **Downstream**: a
validated PRD + index entry.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-prd/SKILL.md` | PRD structure and authoring rules (generation) |
| `../doc-brd-audit/SKILL.md` | upstream BRD quality gate (PRD-Ready) |
| `../doc-prd-audit/SKILL.md` | quality gate (scoring + findings) |
| `../doc-prd-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | element-ID standards |

## Input Contract

Accepts: a target PRD id/path; a source BRD id/path; a free-text prompt; or an
IPLAN path. Optional: score threshold (default 90), max fix iterations (default
3), batch list. With no explicit input, treat the request as a prompt.
Precedence when multiple are given: IPLAN > BRD/REF > prompt; conflicting
objective/scope is blocking and requires user clarification.

## Smart Document Detection

For each target, check whether the PRD already exists (nested folder
`docs/02_PRD/PRD-NN_{slug}/`):

- **Missing** → *generate* mode (from the source BRD/prompt/IPLAN).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

A `BRD-NN` input maps to the corresponding PRD: generate if missing, review if
it already exists. Determine `deliverable_type`
(`code`/`document`/`ux`/`risk`/`process`) inherited from the source BRD.

## Workflow

1. **Input analysis** — classify the input (BRD / prompt / IPLAN), locate the
   source material, and decide generate vs review-and-fix.
2. **BRD readiness** — when generating from a BRD, confirm it passes
   `../doc-brd-audit/SKILL.md` (PRD-Ready ≥ threshold); read all BRD section
   files as one document; reserve the next `PRD-NN`.
3. **Generation** — produce the PRD per `../doc-prd/SKILL.md`: Document Control
   first (with `@brd:` reference + EARS-Ready score), all 15 sections, §10 in
   ≥3 categories, §14 ADR-topic elaboration (no ADR numbers), element IDs
   `PRD.NN.SS.xxxx`, cumulative `@brd:` tags, diagram tags via
   `../charts-flow/SKILL.md` (`c4-l2`/`dfd-l2`/`sequence-sync` with `alt/else`).
4. **Validation** — run `../doc-prd-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-prd-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/02_PRD/PRD-00_index.md` and the parent BRD's downstream entry; on
   exhausting iterations, flag for manual review.

## Execution Modes

- **Single** — one PRD (generate or review-and-fix).
- **Batch** — multiple PRDs, processed in **chunks of 3** to bound context;
  generate each PRD only after its source BRD is ready.
- **Dry-run** — report the planned actions (source, sections, IDs) without
  writing files.

## Quality Gates

- Generation does not complete until the audit passes (EARS-Ready ≥ threshold,
  0 Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The PRD index and parent-BRD downstream entry are updated only after a PRD
  passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Source BRD missing or below PRD-Ready | stop; report the unmet dependency |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the PRD |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-prd/SKILL.md` · Audit: `../doc-prd-audit/SKILL.md` · Fix:
  `../doc-prd-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/02_PRD/PRD-00_index.TEMPLATE.md`
