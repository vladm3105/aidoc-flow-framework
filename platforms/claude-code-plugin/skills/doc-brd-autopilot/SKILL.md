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
    version: "0.4.0"
    framework_spec_version: "0.10.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary]
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

1. **Input analysis** — classify the input (REF / prompt / IPLAN), locate
   reference material, and decide generate vs review-and-fix.
2. **Type & scope** — Platform vs Feature; for a Feature BRD, verify the
   referenced Platform BRD exists; reserve the next `BRD-NN`.
3. **Generation** — produce the BRD per `../doc-brd/SKILL.md`: Document Control
   (Section 1) first, §3–§15 required sections (toggle §2 Executive Summary per
   `section_toggles`), diagrams registry, appendix, §8 across the 7 categories,
   element IDs `BRD.NN.SS.xxxx`, diagram tags via `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-brd-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-brd-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/01_BRD/BRD-00_index.md`; on exhausting iterations, flag for manual
   review.

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
