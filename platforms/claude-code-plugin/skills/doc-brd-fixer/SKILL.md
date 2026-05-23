---
name: doc-brd-fixer
description: Apply fixes to a BRD from the latest doc-brd-audit report - structure, links, element IDs, content, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-1-artifact
    - quality-assurance
  custom_fields:
    layer: 1
    artifact_type: BRD
    skill_category: quality-assurance
    upstream_artifacts: []
    downstream_artifacts: [PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.3.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-brd-fixer

## Purpose

Read the latest audit report and apply fixes to a BRD, bridging
`../doc-brd-audit/SKILL.md` and a passing BRD so the audit↔fix cycle can
converge.

**Layer**: 1 (BRD quality improvement).
**Upstream**: the BRD document + `BRD-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed BRD + `BRD-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-brd-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
BRD (use `../doc-brd/SKILL.md` / `../doc-brd-autopilot/SKILL.md`).

## Input Contract

Consume the latest `BRD-NN.A_audit_report_vNNN.md`. Back up the BRD before
editing (`tmp/backup/BRD-NN_<ts>/`); on error, restore. Element-ID standards
come from `framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`framework/layers/01_BRD/BRD-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | nested-folder rule | move BRD into `docs/01_BRD/BRD-NN_{slug}/`; rename folder to match ID; fix relative links after the move |
| 1 — Missing files | referenced-but-absent | create glossary / GAP / reference placeholders from templates |
| 2 — Links | broken/abs paths | recompute relative paths; convert absolute → relative |
| 3 — Element IDs | legacy/invalid IDs | re-derive `BRD.NN.SS.xxxx` (section number + content hash); drop legacy `BRD.NN.xxxx`, numeric type-codes, `FR-XXX`/`BO-XXX` prefixes |
| 4 — Content | placeholders, missing subsections | fill template dates; normalize MVP subsection headings in place; safe sibling renumbering; flag `[TODO]`/`[TBD]` for manual completion |
| 5 — References | traceability | add missing `@ref:` tags; fix cross-BRD paths; update the traceability matrix |
| 6 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`/`upstream_mode`; when `upstream_mode: "ref"`, apply tiered drift merge (below) |

**Element ID re-derivation:** `key = "{doc_id}:{section_id}:{title}:{description}"`;
ID = `BRD.{doc_id}.{section_id}.<first 4 hex of SHA256(key)>` (extend to 8 on
collision). Document-level refs (`SPEC-NN`, `ADR-NN`, `IPLAN-NN`) stay in dash
form.

**Tiered upstream drift** (only when `upstream_mode: "ref"`): <5% change →
Tier 1 auto-merge (patch bump); 5–15% → Tier 2 auto-merge + detailed changelog
(minor bump); >15% → Tier 3 archive current + regenerate via autopilot (major
bump). Never delete upstream-removed content — mark `[DEPRECATED]` and retain
for traceability. Record results in `.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, header normalize, ID conversion) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded tables/subsections) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, strategy rationale) |

## Content-Preservation Rules

- Never delete existing business content; insert template blocks only where a
  section is missing or below minimum structure.
- Normalize equivalent headings in place rather than duplicating sections.
- Renumber only within the same section file; flag if a cross-reference anchor
  would break.

## Fix Report Format

Write `BRD-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified) · **Fixes Applied** (code, issue, fix,
file, confidence) · **Manual-Review Queue** · **Validation After Fix**
(score/errors/warnings before→after) · **Cleanup Summary** (delete superseded
fix reports) · **Next Steps** (re-run `doc-brd-audit`). Loop until score ≥
threshold or max iterations reached.


## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-brd-audit/SKILL.md` · Create: `../doc-brd/SKILL.md`
- Orchestration: `../doc-brd-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `framework/governance/ID_NAMING_STANDARDS.md`
