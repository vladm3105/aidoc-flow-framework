---
name: doc-iplan-fixer
description: Apply fixes to an IPLAN from the latest doc-iplan-audit report - structure, links, IDs, file manifest, session handoff, implementation contracts, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-8-artifact
    - quality-assurance
  custom_fields:
    layer: 8
    artifact_type: IPLAN
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC, TDD]
    downstream_artifacts: [CODE]
    version: "0.6.5"
    framework_spec_version: "0.14.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-iplan-fixer

## Purpose

Read the latest audit report and apply fixes to an IPLAN, bridging
`../doc-iplan-audit/SKILL.md` and a passing IPLAN so the audit↔fix cycle can
converge.

**Layer**: 8 (IPLAN quality improvement).
**Upstream**: the IPLAN document + `IPLAN-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed IPLAN + `IPLAN-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-iplan-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
IPLAN (use `../doc-iplan/SKILL.md` / `../doc-iplan-autopilot/SKILL.md`).

## Input Contract

Consume the latest `IPLAN-NN.A_audit_report_vNNN.md`. Back up the IPLAN before
editing (`tmp/backup/IPLAN-NN_<ts>/`); on error, restore. ID standards come from
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | naming/placement | move permanent IPLAN to `docs/08_IPLAN/IPLAN-NN_{slug}.yaml`; move temporary plans to `tmp/` and remove from index; rename file to match ID; fix relative links after the move |
| 1 — Missing sections | absent template sections | seed `file_manifest`, `session_handoff`, `implementation_contracts`, `code_inventory` from the template; create stub test/impl files at declared manifest paths |
| 2 — Links | broken/abs paths | recompute relative paths to SPEC/TDD; convert absolute → relative; fix malformed manifest paths |
| 3 — IDs | invalid IDs | convert hierarchical `IPLAN.NN.SS.xxxx` → document-level `IPLAN-NN`; re-number 3-digit `IPLAN-NNN` → two-digit; add 4-hex hash to `TDD.NN.SS` → `TDD.NN.SS.xxxx`; convert `SPEC.NN.SS.xxxx` → `SPEC-NN` |
| 4 — Content & manifest | placeholders, ordering | fill template dates; reorder manifest to test-first; add missing `status`/`verified` markers; flag `[TODO]`/`[TBD]` for manual completion |
| 5 — References | traceability | add missing `@spec:`/`@tdd:` upstream tags; complete the cumulative chain (`@brd @prd @ears @bdd @adr @spec @tdd`); add missing `code_inventory` entries |
| 6 — Upstream | drift | when SPEC/TDD changed since creation, apply tiered drift merge (below) |
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized session-handoff narrative at session boundaries, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**ID re-derivation:** IPLAN is document-level — always `IPLAN-NN` (dash form),
never a dotted element ID. Document-level upstreams (`SPEC-NN`, `ADR-NN`) stay
dash; hierarchical upstreams keep the dotted 4-segment form (`TDD.NN.SS.xxxx`).

**Tiered upstream drift** (SPEC/TDD changed): <5% change → Tier 1 auto-merge new
manifest entries (patch bump); 5–15% → Tier 2 auto-merge + detailed changelog
(minor bump); >15% → Tier 3 archive current + regenerate via autopilot (major
bump). Never delete manifest entries — mark `[CANCELLED]` with a reason and
retain for the audit trail. Record results in `.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, ID conversion, manifest reorder) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded sections/contracts) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, contract method bodies, Tier 3 drift) |

## Content-Preservation Rules

- Never delete existing manifest entries, contracts, or session history; insert
  template blocks only where a section is missing or below minimum structure.
- Preserve file descriptions, dependency logic, complexity values, and prior
  session entries; normalize format only.
- Mark removed-upstream manifest entries `[CANCELLED]` (keep all original
  fields) rather than deleting them.

## Fix Report Format

Write `IPLAN-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; sections created; files modified) · **Fixes Applied** (code, issue,
fix, file, confidence) · **Manual-Review Queue** · **Validation After Fix**
(score/errors/warnings before→after) · **Cleanup Summary** (delete superseded
fix reports) · **Next Steps** (re-run `doc-iplan-audit`). Loop until score ≥
threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-iplan-audit/SKILL.md` · Create: `../doc-iplan/SKILL.md`
- Orchestration: `../doc-iplan-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
