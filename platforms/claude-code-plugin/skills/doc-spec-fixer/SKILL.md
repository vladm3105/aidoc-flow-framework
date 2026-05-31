---
name: doc-spec-fixer
description: Apply fixes to a SPEC from the latest doc-spec-audit report - structure, YAML, links, IDs, content, references, and upstream drift. Use after an audit reports issues.
metadata:
  tags:
    - sdd-workflow
    - layer-6-artifact
    - quality-assurance
  custom_fields:
    layer: 6
    artifact_type: SPEC
    skill_category: quality-assurance
    upstream_artifacts: [BRD, PRD, EARS, BDD, ADR]
    downstream_artifacts: [TDD, IPLAN]
    version: "0.2.0"
    framework_spec_version: "0.9.0"
    last_updated: "2026-05-23"
    adapts: [section_toggles]
---

# doc-spec-fixer

## Purpose

Read the latest audit report and apply fixes to a SPEC, bridging
`../doc-spec-audit/SKILL.md` and a passing SPEC so the audit↔fix cycle can
converge.

**Layer**: 6 (SPEC quality improvement).
**Upstream**: the SPEC document + `SPEC-NN.A_audit_report_vNNN.md`.
**Downstream**: the fixed SPEC + `SPEC-NN.F_fix_report_vNNN.md`.

## When to Use

After `doc-spec-audit` returns `FAIL`, as part of an Audit → Fix → Audit loop.
Do **not** use without an audit report (run the audit first) or to create a new
SPEC (use `../doc-spec/SKILL.md` / `../doc-spec-autopilot/SKILL.md`).

## Input Contract

Consume the latest `SPEC-NN.A_audit_report_vNNN.md`. Back up the SPEC before
editing (`tmp/backup/SPEC-NN_<ts>/`); on error, restore. ID standards come from
`${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`; structure rules from
`${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` and `README.md`.

## Fix Phases

Run in order; later phases assume the earlier ones succeeded.

| Phase | Scope | Representative actions |
|-------|-------|------------------------|
| 0 — Structure | nested-folder rule | move SPEC into `docs/06_SPEC/SPEC-NN_{slug}/`; rename folder to match ID; fix relative links after the move |
| 1 — YAML | malformed YAML | repair indentation/quoting, remove duplicate keys, fix types so the SPEC parses |
| 2 — Missing files | referenced-but-absent | create index / reference placeholders from templates |
| 3 — Links | broken/abs paths | recompute relative paths; convert absolute → relative |
| 4 — IDs | invalid/legacy IDs | enforce dash-form `SPEC-NN` at the document level; correct upstream element refs to `TYPE.NN.SS.xxxx`; drop legacy `STEP-XXX`/`IF-XXX`/`DM-XXX`, 3-digit `SPEC-NNN`, numeric type codes |
| 5 — Content | placeholders, thresholds | fill template dates; replace hardcoded numbers with `@threshold:` references; flag `[TODO]`/`[TBD]` for manual completion |
| 6 — References | traceability | add missing cumulative tags (`@brd @prd @ears @bdd @adr`) and the downstream `@tdd: TDD-NN`; fix upstream paths; update the traceability matrix |
| 7 — Upstream | metadata + drift | fix `deliverable_type`/`document_type`; apply tiered drift merge against upstream ADR/BDD (below) |
| 8 — Style | STY01 banned phrases, STY02/03 oversized prose, FM01 frontmatter mismatch | substitute filler; replace flagged superlatives; collapse paragraph (≥ 3 banned phrases in one section) to bullets; reconcile frontmatter ↔ Document Control rows; STY02/03 — split oversized Behavior / Interfaces sections at the next contract boundary, or mark `manual_required`. Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/AUTHORING_STYLE.md` |

**ID rules:** SPEC is referenced at the **document level** in dash form
`SPEC-NN` — never a dotted SPEC element ID. Upstream hierarchical refs use the
4-segment element form `TYPE.NN.SS.xxxx` (e.g. `BDD.01.03.8f4c`); document-level
`@adr: ADR-NN`.

**Tiered upstream drift** (against the referenced ADR/BDD): <5% change → Tier 1
auto-merge (patch bump); 5–15% → Tier 2 auto-merge + detailed changelog (minor
bump); >15% → Tier 3 archive current + regenerate via autopilot (major bump).
Never delete upstream-removed content — mark `[DEPRECATED]` and retain for
traceability. Record results in `.drift_cache.json`.

## Confidence Classification

Tag every applied fix and surface counts in the report:

| Confidence | Meaning |
|------------|---------|
| `auto-safe` | deterministic, low semantic risk (link/path, YAML reindent, ID conversion, threshold tagging) |
| `auto-assisted` | template insertion with partial assumptions (scaffolded sections/interface stubs) |
| `manual-required` | domain content cannot be inferred (interface signatures, behavior logic, unresolved TODO/TBD) |

## Content-Preservation Rules

- Never delete existing interface definitions, data-model schemas, or behavior
  logic; insert template blocks only where a section is missing or below minimum
  structure.
- Normalize equivalent YAML keys/headings in place rather than duplicating
  sections; preserve YAML comments.
- Renumber only within the same section; flag if a cross-reference anchor would
  break.

## Fix Report Format

Write `SPEC-NN.F_fix_report_vNNN.md` with: **Summary** (issues in / fixed /
remaining; files created / modified; YAML blocks repaired) · **Fixes Applied**
(code, issue, fix, file, confidence) · **Manual-Review Queue** · **Upstream
Drift Summary** · **Validation After Fix** (score/errors/warnings before→after)
· **Cleanup Summary** (delete superseded fix reports) · **Next Steps** (re-run
`doc-spec-audit`). Loop until score ≥ threshold or max iterations reached.

## Adaptation

Before applying fixes, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `section_toggles`: do not reintroduce an
**optional** section the project has toggled off. Ignore any unknown or
out-of-surface key.
Authority: `${CLAUDE_PLUGIN_ROOT}/framework/governance/ADAPTATION.md`.

## Related Resources

- Audit (input): `../doc-spec-audit/SKILL.md` · Create: `../doc-spec/SKILL.md`
- Orchestration: `../doc-spec-autopilot/SKILL.md` · IDs: `../doc-naming/SKILL.md`
- Authority: `${CLAUDE_PLUGIN_ROOT}/framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`,
  `${CLAUDE_PLUGIN_ROOT}/framework/governance/ID_NAMING_STANDARDS.md`
