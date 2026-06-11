---
name: doc-bdd-autopilot
description: Generate BDD scenarios end-to-end from EARS, a prompt, or an IPLAN - detect input, generate Gherkin scenarios, validate, and run the audit/fix cycle. Use to create or batch-create BDD suites.
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
    version: "0.17.0"
    framework_spec_version: "0.20.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary]
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
| `../doc-bdd/SKILL.md` | BDD structure, Gherkin syntax, and authoring rules (generation) |
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

## Workflow

1. **Input analysis** — classify the input (EARS / prompt / IPLAN), locate the
   upstream EARS and its BRD/PRD trace elements, and decide generate vs
   review-and-fix.
2. **Type & scope** — confirm the referenced EARS (and its PRD/BRD elements)
   exist; map EARS statements to scenario categories; reserve the next `BDD-NN`.
3. **Generation** — produce the BDD per `../doc-bdd/SKILL.md`: Document Control
   first, all 5 sections, scenarios across the five categories with executable
   Given-When-Then steps, cumulative tags `@brd @prd @ears` (Gherkin-native),
   `@scenario-id` IDs `BDD.NN.03.xxxx`, `@threshold:` references, and a
   `spec_trace` per scenario. Sequence diagrams via `../charts-flow/SKILL.md`.
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
