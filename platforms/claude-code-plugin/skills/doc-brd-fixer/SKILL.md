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
    version: "0.4.2"
    framework_spec_version: "0.11.3"
    last_updated: "2026-05-23"
    adapts: [section_toggles, review_mode]
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

Consume the latest audit report from `.aidoc/audit/01_BRD-audit.md` (the
`.aidoc/` provenance tier). Back up the BRD before editing
(`tmp/backup/BRD-NN_<ts>/`); on error, restore. Element-ID standards come
from `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`;
structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml` and
`README.md`.

## Remediate Mode

Resolve `review_mode` from `.aidoc/profile.yaml`; if unset, fall through
to the framework default `team` per the precedence chain in
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`. Same
fallback applies to other adaptation knobs (`section_toggles`).

### team mode (per REVIEW_TEAM.md §Operations §Remediate)

1. **Read the audit report** at `.aidoc/audit/01_BRD-audit.md` AND, when
   present, the per-persona slots at
   `.aidoc/review/01_BRD/<BRD-id>/<persona>.json`. The slots carry
   structured findings with stable ids, priorities, and locations the
   fixer needs. **Slots are optional** — fixer must work from the audit
   report alone if slots are missing (e.g. single_pass run produced no
   slots).
2. **Group blocking findings** (P0 + P1) by responsible lens via the
   lens → agent mapping in `../review-team/SKILL.md`. P2/P3 are
   advisory — apply deterministically without lens validation.
3. **Propose and apply a patch** per blocking finding. Fix Phases 0–7
   below describe the patch shapes; the catalogue is the same in both
   modes. Back up first per the existing Input Contract.
4. **Validate non-regression.** Dispatch the responsible lens as a
   `Task` subagent in patch-validation mode: subagent_type=<mapped
   agent>; brief = the patched region + the original finding + the
   patch diff; output = a fresh persona-output record (lens_score for
   that region + any new findings). Persist as
   `.aidoc/review/01_BRD/<BRD-id>/<persona>.fix_<N>.json`.
5. **Revert regressions.** If any lens returns new P0/P1 on the patch,
   revert that patch and flag `manual_required` for the original
   finding. **Never silently keep a regressing fix.**
6. **Dispatch the synthesizer once**, after all patches are validated,
   to emit the unified fix report. Persist
   `.aidoc/remediation/01_BRD-fix.md` with both the Fixes Applied table
   AND a Validation Slots index.

### single_pass mode (fallback)

Apply Phase 0–7 directly, single-handed, no lens validation. Unchanged
legacy behaviour — required when the profile says so, when `Task` subagent
dispatch is unavailable, or when no slots are present.

In both modes, P2/P3 advisory findings are applied without lens
validation; only blocking findings (P0/P1) go through the
patch-validation loop in team mode.

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
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler (`in order to` → `to`; drop `the fact that`, `it should be noted`, `please note`, `as a matter of fact`); replace flagged superlatives (`amazing`, `seamless`, `cutting-edge`, `state-of-the-art`); collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control ↔ revision-history rows (mirror frontmatter as the source of truth); STY02/03 — auto-split sections > 300 words at the first natural subheading, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

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
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-brd-audit/SKILL.md` · Create: `../doc-brd/SKILL.md`
- Orchestration: `../doc-brd-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/01_BRD/BRD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
