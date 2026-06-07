---
name: doc-ears-fixer
description: Apply fixes to an EARS document from the latest doc-ears-audit report - structure, links, element IDs, EARS syntax, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-3-artifact
    - quality-assurance
  custom_fields:
    layer: 3
    artifact_type: EARS
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD]
    downstream_artifacts: [BDD, ADR, SPEC, TDD, IPLAN]
    version: "0.6.5"
    framework_spec_version: "0.14.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-ears-fixer

## Purpose

Read the latest audit report and apply fixes to an EARS document, bridging
`../doc-ears-audit/SKILL.md` and a passing EARS so the audit↔fix cycle can
converge.

**Layer**: 3 (EARS quality improvement).
**Upstream**: the EARS document + `EARS-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed EARS + `EARS-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-ears-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
EARS (use `../doc-ears/SKILL.md` / `../doc-ears-autopilot/SKILL.md`).

## Input Contract

Consume the latest `EARS-NN.A_audit_report_vNNN.md`. Back up the EARS before
editing (`tmp/backup/EARS-NN_<ts>/`); on error, restore. Element-ID standards
come from `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure and syntax
rules from `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | nested-folder rule | move EARS into `docs/03_EARS/EARS-NN_{slug}/`; rename folder to match ID; fix relative links after the move |
| 1 — Missing files | referenced-but-absent | create glossary / reference placeholders from templates |
| 2 — Links | broken/abs paths | recompute relative paths; convert absolute → relative; fix upstream BRD/PRD links |
| 3 — Element IDs | legacy/invalid IDs | re-derive `EARS.NN.SS.xxxx` (section number + content hash); drop legacy `EARS.NN.xxxx`, numeric type-codes (`.25`/`.26`), `Event-XXX`/`State-XXX`/`UB-XXX`/`REQ-XXX` prefixes |
| 4 — Content | placeholders, syntax | fill template dates; normalize headings in place; flag missing SHALL keyword, broken WHEN-THE-SHALL structure, missing trigger, vague timing, compound (non-atomic) statements for manual review; flag `[TODO]`/`[TBD]` |
| 5 — References | traceability | add missing cumulative `@brd`/`@prd` tags; fix `@threshold:` format; convert comma separators → pipes; update the traceability matrix |
| 6 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`; when `upstream_mode: "ref"`, apply tiered drift merge (below) |
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split sections > 300 words at the next requirement boundary, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**Element ID re-derivation:** `key = "{doc_id}:{section_id}:{title}:{description}"`;
ID = `EARS.{doc_id}.{section_id}.<first 4 hex of SHA256(key)>` (extend to 8 on
collision). The section conveys element kind (statement vs. quality attribute) —
never reuse a legacy sequence number as the final segment. Document-level refs
(`SPEC-NN`, `ADR-NN`, `IPLAN-NN`) stay in dash form.

**Tiered upstream drift** (only when `upstream_mode: "ref"`): <5% change →
Tier 1 auto-merge (patch bump); 5–15% → Tier 2 auto-merge + detailed changelog
(minor bump); >15% → Tier 3 archive current + regenerate via autopilot (major
bump). Never delete upstream-removed requirements — mark `[DEPRECATED]` and
retain for traceability. Record results in `.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, header normalize, ID conversion, comma→pipe) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded tables/sections, threshold placeholders) |
| `manual-required` | domain content cannot be inferred (missing SHALL, non-atomic split, vague-term quantification, unresolved TODO/TBD) |

## Content-Preservation Rules

- Never delete existing requirement content; insert template blocks only where a
  section is missing or below minimum structure.
- Normalize equivalent headings in place rather than duplicating sections.
- Preserve threshold values when reformatting; renumber only within the same
  section file; flag if a cross-reference anchor would break.

## Fix Report Format

Write `EARS-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified) · **Fixes Applied** (code, issue, fix,
file, confidence) · **Manual-Review Queue** (e.g. syntax, atomicity) ·
**Validation After Fix** (score/errors/warnings before→after) · **Cleanup
Summary** (delete superseded fix reports) · **Next Steps** (re-run
`doc-ears-audit`). Loop until score ≥ threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-ears-audit/SKILL.md` · Create: `../doc-ears/SKILL.md`
- Orchestration: `../doc-ears-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/03_EARS/EARS-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
