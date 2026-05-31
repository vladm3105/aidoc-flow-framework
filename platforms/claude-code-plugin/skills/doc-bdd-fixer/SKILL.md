---
name: doc-bdd-fixer
description: Apply fixes to a BDD suite from the latest doc-bdd-audit report - structure, links, element IDs, Gherkin content, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-4-artifact
    - quality-assurance
  custom_fields:
    layer: 4
    artifact_type: BDD
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS]
    downstream_artifacts: [ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.9.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-bdd-fixer

## Purpose

Read the latest audit report and apply fixes to a BDD suite, bridging
`../doc-bdd-audit/SKILL.md` and a passing BDD so the audit↔fix cycle can
converge.

**Layer**: 4 (BDD quality improvement).
**Upstream**: the BDD document + `BDD-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed BDD + `BDD-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-bdd-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
BDD (use `../doc-bdd/SKILL.md` / `../doc-bdd-autopilot/SKILL.md`).

## Input Contract

Consume the latest `BDD-NN.A_audit_report_vNNN.md`. Back up the BDD before
editing (`tmp/backup/BDD-NN_<ts>/`); on error, restore. Element-ID standards
come from `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure and Gherkin
rules from `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | folder/index rule | move BDD into `docs/04_BDD/BDD-NN_{slug}/`; rename folder to match ID; ensure index present; fix relative links after the move |
| 1 — Missing files | referenced-but-absent | create glossary / index / `.feature` placeholders from templates |
| 2 — Links | broken/abs paths | recompute relative paths; convert absolute → relative |
| 3 — Element IDs | legacy/invalid IDs | re-derive `BDD.NN.SS.xxxx` (section + content hash); drop legacy `BDD.NN.xxxx`, numeric type-codes, `SCEN-XXX`/`STEP-XXX` prefixes |
| 4 — Content | placeholders, tags, thresholds | fill template dates; move comment tags to Gherkin-native; add `@scenario-type`/priority/`WITHIN` thresholds; flag `[TODO]`/`[TBD]` and missing Given-When-Then for manual completion |
| 5 — References | traceability | add missing cumulative `@brd @prd @ears` tags; fix cross-doc paths; add/repair `spec_trace`; update the traceability matrix |
| 6 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`/`upstream_mode`; when upstream EARS drifts, apply tiered drift merge (below) |

**Element ID re-derivation:** `key = "{doc_id}:{section_id}:{title}:{description}"`;
ID = `BDD.{doc_id}.{section_id}.<first 4 hex of SHA256(key)>` (extend to 8 on
collision). Document-level refs (`SPEC-NN`, `ADR-NN`, `IPLAN-NN`) stay in dash
form; scenarios live in section `03`.

**Content-preservation in Gherkin:** never modify step text (Given/When/Then) or
Examples-table data; only add missing tags/metadata and replace hardcoded values
with `@threshold:` references. Missing keywords/structure are flagged, not
invented.

**Tiered upstream drift** (EARS changed since BDD): <5% change → Tier 1
auto-merge new scenarios (patch bump); 5–15% → Tier 2 auto-merge + detailed
changelog, mark modified-source scenarios for review (minor bump); >15% → Tier 3
archive current + regenerate via autopilot (major bump). Never delete
upstream-removed scenarios — mark `@deprecated` and retain for traceability.
Record results in `.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, tag relocation, ID conversion, threshold substitution) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded scenarios/sections, default priority tags) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, missing Given-When-Then, step semantics) |

## Content-Preservation Rules

- Never delete existing scenario content; insert template blocks only where a
  section or scenario is missing or below minimum structure.
- Move equivalent tags to their Gherkin-native position rather than duplicating.
- Renumber/restructure only within the same document; flag if a cross-reference
  anchor would break.

## Fix Report Format

Write `BDD-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified) · **Fixes Applied** (code, issue, fix,
file, confidence) · **Manual-Review Queue** · **Validation After Fix**
(score/errors/warnings before→after) · **Cleanup Summary** (delete superseded
fix reports) · **Next Steps** (re-run `doc-bdd-audit`). Loop until score ≥
threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-bdd-audit/SKILL.md` · Create: `../doc-bdd/SKILL.md`
- Orchestration: `../doc-bdd-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/04_BDD/BDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
