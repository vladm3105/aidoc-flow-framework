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
    version: "0.2.0"
    framework_spec_version: "0.8.1"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary]
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

## Workflow

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
