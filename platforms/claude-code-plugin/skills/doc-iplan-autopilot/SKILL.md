---
name: doc-iplan-autopilot
description: Generate IPLANs end-to-end from a SPEC/TDD, a prompt, or an existing IPLAN - detect input, plan a test-first file manifest, generate, validate, and run the audit/fix cycle. Use to create or batch-create IPLANs.
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
    - automation-workflow
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    skill_category: automation-workflow
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD]
    downstream_artifacts: [CODE]
    version: "0.4.4"
    framework_spec_version: "0.11.3"
    last_updated: "2026-05-23"
    adapts: [section_toggles, active_layers, audit_threshold, glossary]
---

# doc-iplan-autopilot

## Purpose

Automated **IPLAN generation pipeline**. From a SPEC/TDD component, a user
prompt, or an existing IPLAN, it analyzes the source, plans a test-first file
manifest, generates a complete IPLAN, validates CODE-readiness, maintains
`IPLAN-00_index.yaml`, and drives the audit↔fix cycle to a passing score — for
one IPLAN or a batch.

**Layer**: 8 (final doc layer; downstream is Code). **Upstream**: SPEC/TDD,
prompt, or existing IPLAN input. **Downstream**: a validated IPLAN + index entry.

This autopilot generates **permanent** IPLANs only (one per SPEC/TDD component).
Temporary bugfix plans are authored manually via `../doc-iplan/SKILL.md` and are
not registered in the index.

## Skill Dependencies

| Skill | Role |
|-------|------|
| `../doc-iplan/SKILL.md` | IPLAN structure and authoring rules (generation) |
| `../doc-iplan-audit/SKILL.md` | quality gate (CODE-Ready scoring + findings) |
| `../doc-iplan-fixer/SKILL.md` | applies fixes from the audit report |
| `../doc-naming/SKILL.md` | document/element-ID standards |

## Input Contract

Accepts: a target IPLAN id/path; a SPEC or TDD id/path; a free-text prompt; or an
existing IPLAN path. Precedence: explicit IPLAN > SPEC/TDD upstream > prompt.
Optional: score threshold (default 90), max fix iterations (default 3), batch
list. With no explicit input, treat the request as a prompt.

## Smart Document Detection

For each target, check whether the IPLAN already exists
(`docs/08_IPLAN/IPLAN-NN_*.yaml`):

- **Missing** → *generate* mode (from the SPEC/TDD component).
- **Exists** → *review & fix* mode (audit, then fix if below threshold).

A SPEC-NN or TDD-NN input maps to its IPLAN-NN; generate if missing, otherwise
review. Determine plan type (permanent vs temporary) from the source — this
autopilot proceeds only for permanent plans.

## Workflow

1. **Input analysis** — classify the input (SPEC/TDD / prompt / existing IPLAN),
   locate the upstream component, and decide generate vs review-and-fix.
2. **Manifest planning** — verify the source TDD/SPEC is IPLAN-Ready ≥ threshold;
   plan the test-first file order and identify file dependencies; reserve the
   next `IPLAN-NN`.
3. **Generation** — produce the IPLAN per `../doc-iplan/SKILL.md`: Document
   Control first, all 6 sections, test-first file manifest, execution commands,
   implementation contracts when 3+ files share interfaces, seeded session
   handoff, cumulative tags (`@brd @prd @ears @bdd @adr @spec @tdd`), and an
   empty `code_inventory`. Diagrams via `../charts-flow/SKILL.md`.
4. **Validation** — run `../doc-iplan-audit/SKILL.md` from scratch.
5. **Audit ↔ fix cycle** — while score < threshold and iterations < max: run
   `../doc-iplan-fixer/SKILL.md`, then re-audit. On pass, update
   `docs/08_IPLAN/IPLAN-00_index.yaml`; on exhausting iterations, flag for manual
   review.

## Execution Modes

- **Single** — one IPLAN (generate or review-and-fix).
- **Batch** — multiple IPLANs, processed in **chunks of 3** to bound context;
  generate plans for upstream components before dependent ones.
- **Dry-run** — report the planned actions (type, file manifest, IDs) without
  writing files.

## Quality Gates

- Generation does not complete until the audit passes (CODE-Ready ≥ threshold, 0
  Tier-1 errors) or the iteration cap is hit (then: manual-review flag).
- The IPLAN index is updated only after a plan passes.
- Fresh audit every cycle — no cached scores.

## Error Handling

| Situation | Action |
|-----------|--------|
| Source SPEC/TDD below IPLAN-Ready threshold | stop; report the upstream gap (fix upstream first) |
| Max iterations reached below threshold | write reports, flag for manual review, continue batch |
| Source input ambiguous | fall back to prompt mode; record assumptions in the IPLAN |
| Write/permission error | log, skip the item, continue the batch |

## Adaptation

Before applying defaults, read the project adaptation profile
(`.aidoc/profile.yaml`) and apply it in both the generation and the internal
audit/fix phases. Honor `section_toggles`, `active_layers`, `audit_threshold`
(raise-only — stricter only), and `glossary`. Ignore any unknown or
out-of-surface key; absent a profile, use framework defaults.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Create: `../doc-iplan/SKILL.md` · Audit: `../doc-iplan-audit/SKILL.md` · Fix:
  `../doc-iplan-fixer/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/README.md`,
  `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml`
