---
name: doc-adr-fixer
description: Apply fixes to an ADR from the latest doc-adr-audit report - structure, links, element IDs, content, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-5-artifact
    - quality-assurance
  custom_fields:
    layer: 5
    artifact_type: ADR
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD]
    downstream_artifacts: [SPEC, TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.10.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-adr-fixer

## Purpose

Read the latest audit report and apply fixes to an ADR, bridging
`../doc-adr-audit/SKILL.md` and a passing ADR so the audit↔fix cycle can
converge.

**Layer**: 5 (ADR quality improvement).
**Upstream**: the ADR document + `ADR-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed ADR + `ADR-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-adr-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
ADR (use `../doc-adr/SKILL.md` / `../doc-adr-autopilot/SKILL.md`).

## Input Contract

Consume the latest `ADR-NN.A_audit_report_vNNN.md`. Back up the ADR before
editing (`tmp/backup/ADR-NN_<ts>/`); on error, restore. Element-ID standards
come from `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | nested-folder rule | move ADR into `docs/05_ADR/ADR-NN_{slug}/`; rename folder to match ID; fix relative links after the move |
| 1 — Missing files | referenced-but-absent | create glossary / index / reference placeholders from templates |
| 2 — Links | broken/abs paths | recompute relative paths; convert absolute → relative |
| 3 — Element IDs | legacy/invalid IDs | re-derive `ADR.NN.SS.xxxx` (section number + content hash); drop legacy `ADR.NN.xxxx`, numeric type-codes, `DEC-XXX`/`ALT-XXX`/`CON-XXX` prefixes; keep document refs in dash form `ADR-NN` |
| 4 — Content | placeholders, missing subsections | fill template dates; default missing status to `Proposed`; normalize subsection headings in place; flag `[TODO]`/`[TBD]` for manual completion |
| 5 — References | traceability | add missing cumulative tags `@brd @prd @ears @bdd`; add the `@adr: ADR-NN` self-tag and `@depends:` cross-links; update the ADR index |
| 6 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`/`status`; apply tiered drift merge against changed upstream (BRD/PRD/EARS/BDD) |
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized Context / Decision / Consequences sections at the next natural boundary, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**Element ID re-derivation:** `key = "{doc_id}:{section_id}:{title}:{description}"`;
ID = `ADR.{doc_id}.{section_id}.<first 4 hex of SHA256(key)>` (extend to 8 on
collision). The element kind is conveyed by its section, not by a type-code.
Document-level refs (`ADR-NN`, `SPEC-NN`, `IPLAN-NN`) stay in dash form.

**Tiered upstream drift:** <5% change → Tier 1 auto-merge (patch bump); 5–15% →
Tier 2 auto-merge + detailed changelog (minor bump); >15% → Tier 3 archive
current + regenerate via autopilot (major bump). Never delete superseded
decisions — mark `[SUPERSEDED]` and retain for traceability. Record results in
`.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, header normalize, ID conversion) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded tables/subsections) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, decision rationale) |

## Content-Preservation Rules

- Never delete existing decision, context, or alternatives content; insert
  template blocks only where a section is missing or below minimum structure.
- Never alter the recorded decision or its rationale to make a check pass.
- Normalize equivalent headings in place rather than duplicating sections.
- Renumber only within the same section file; flag if a cross-reference anchor
  would break.

## Fix Report Format

Write `ADR-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified) · **Fixes Applied** (code, issue, fix,
file, confidence) · **Manual-Review Queue** · **Validation After Fix**
(score/errors/warnings before→after) · **Cleanup Summary** (delete superseded
fix reports) · **Next Steps** (re-run `doc-adr-audit`). Loop until score ≥
threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-adr-audit/SKILL.md` · Create: `../doc-adr/SKILL.md`
- Orchestration: `../doc-adr-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/05_ADR/ADR-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
