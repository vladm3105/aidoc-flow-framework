---
name: doc-tdd-fixer
description: Apply fixes to a TDD from the latest doc-tdd-audit report - structure, links, element IDs, test-case content, references, and upstream SPEC drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-7-artifact
    - quality-assurance
  custom_fields:
    layer: 7
    artifact_type: TDD
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SPEC]
    downstream_artifacts: [IPLAN]
    version: "0.4.3"
    framework_spec_version: "0.11.3"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-tdd-fixer

## Purpose

Read the latest audit report and apply fixes to a TDD, bridging
`../doc-tdd-audit/SKILL.md` and a passing TDD so the audit↔fix cycle can
converge.

**Layer**: 7 (TDD quality improvement).
**Upstream**: the TDD document + `TDD-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed TDD + `TDD-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-tdd-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
TDD (use `../doc-tdd/SKILL.md` / `../doc-tdd-autopilot/SKILL.md`).

## Input Contract

Consume the latest `TDD-NN.A_audit_report_vNNN.md`. Back up the TDD before
editing (`tmp/backup/TDD-NN_<ts>/`); on error, restore. Element-ID standards
come from `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | location/filename | move TDD into `docs/07_TDD/`; rename to `TDD-NN_{slug}.yaml`; align slug with the parent SPEC component; fix relative links after the move |
| 1 — Missing files | referenced-but-absent | create index / fixture / reference placeholders from templates |
| 2 — Links | broken/abs paths | recompute relative paths; convert absolute → relative |
| 3 — Element IDs | legacy/invalid IDs | re-derive `TDD.NN.04.xxxx` (Section 4 + content hash); drop legacy 3-segment `TDD.NN.xxxx` and `TC-XXX`/`UT-XXX`/`IT-XXX`/`ST-XXX`/`FT-XXX` (set the `type` attribute instead) |
| 4 — Content | placeholders, malformed cases | fill template dates; add missing inputs/expected output/edge cases; set a `type` attribute; repair the BDD→test mapping; flag `[TODO]`/`[TBD]` for manual completion |
| 5 — References | traceability | add missing `@spec:`/`@bdd:` tags; fix cross-doc paths; update Section 7 traceability and the coverage table |
| 6 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`; when the parent SPEC has changed, apply tiered drift merge (below) |
| 7 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized Test Case sections at type/category boundaries, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**Element ID re-derivation:** `ID = TDD.{doc_id}.04.<first 4 hex of
SHA256(case content)>` (extend to 8 on collision). Test type stays a `type`
attribute, never an ID code. Document-level refs (`SPEC-NN`, `ADR-NN`,
`IPLAN-NN`) stay in dash form.

**Tiered upstream drift** (when the parent SPEC changed): <5% change → Tier 1
auto-merge new test-case stubs (patch bump); 5–15% → Tier 2 auto-merge + flag
affected cases for review + changelog (minor bump); >15% → Tier 3 archive
current + regenerate via autopilot (major bump). Never delete tests — mark
`[DEPRECATED]` and retain for traceability. Record results in
`.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, ID conversion, date fill) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded test-case fields, coverage rows) |
| `manual-required` | domain content cannot be inferred (unresolved TODO/TBD, test logic, assertions) |

## Content-Preservation Rules

- Never delete existing test logic, assertions, test data, or fixtures; insert
  template blocks only where a case or section is missing required structure.
- Normalize equivalent headings/cases in place rather than duplicating them.
- Deprecated tests are marked, not removed; recalculate coverage after fixes.

## Fix Report Format

Write `TDD-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified; test cases repaired) · **Fixes Applied**
(code, issue, fix, file, confidence) · **Manual-Review Queue** · **Validation
After Fix** (score/errors/warnings before→after) · **Cleanup Summary** (delete
superseded fix reports) · **Next Steps** (re-run `doc-tdd-audit`). Loop until
score ≥ threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-tdd-audit/SKILL.md` · Create: `../doc-tdd/SKILL.md`
- Orchestration: `../doc-tdd-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/07_TDD/TDD-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
