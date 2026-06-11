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
    version: "0.13.1"
    framework_spec_version: "0.17.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary]
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

## Workflow

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
