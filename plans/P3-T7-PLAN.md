# P3-T7 — Add new skills (CHG family, gate-check, project-adopt)

| Field      | Value |
|------------|-------|
| Task       | P3-T7 — add the missing change-management + onboarding skills |
| Status     | VERIFIED — 2026-05-23T17:07:07Z |
| Depends on | P3-T6 (canonical 46-skill set) |
| Standard   | `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md` |

## Why

The P3-T6 review found three framework-backed capabilities with **no skill**:
the CHG change-management overlay (`framework/governance/chg/`), its approval
gates, and a brownfield onboarding path (`project-init` is greenfield-only).
This task adds 6 skills (46 → 52). `doc-code`/implement was considered and
deferred (overlaps native coding).

## Scope — 6 new skills

1. **`doc-chg`** (base) — author a CHG document for an edit to existing SDD
   artifacts: classify change level (C1–C3/Emergency), route by source to the
   entry gate, assess cross-layer cascade impact, populate `CHG-TEMPLATE.yaml`,
   register in `CHG-00_index`. Emergency level uses `POST_MORTEM-TEMPLATE.md`
   (post-mortem folded in here — no separate skill).
2. **`doc-chg-autopilot`** — end-to-end CHG authoring with minimal prompts.
3. **`doc-chg-audit`** — validate a CHG doc vs template: schema, required
   fields, impact/cascade completeness, gate-routing correctness. Gate-readiness
   report (CHG uses gate approval, not a ≥90 readiness score).
4. **`doc-chg-fixer`** — fix issues found by `doc-chg-audit`.
5. **`gate-check`** (utility) — run the appropriate approval gate
   (GATE-01/03/06/08/CODE) for a change's affected layers, apply
   `GATE_ERROR_CATALOG`, prepare `GATE_APPROVAL_FORM`. **Prepares + verifies; the
   human grants approval** (never the skill).
6. **`project-adopt`** (utility, brownfield) — counterpart to `project-init`:
   detect an existing codebase, reverse-engineer BRD…SPEC-level docs from current
   code, scaffold `docs/`, then hand to `doc-flow`/`-audit` to close gaps.

## Design decisions

- **CHG is not a lifecycle layer** (`chg/README.md`): the `doc-chg` family carries
  NO numeric `layer` / `artifact_type: <layer>` and NO upstream/downstream layer
  chain. Tags: `sdd-workflow` + `change-management`. It still fits the
  base/autopilot/audit/fixer pattern (template + index + validate + fix).
- `gate-check` + `project-adopt` are utilities (`skill_category: utility`,
  no layer). `project-adopt` mirrors `project-init`'s body structure.
- No framework `registry` change (CHG/gates/utilities are not layers).

## Implementation

- Author all 6 to the canonical standard (version = plugin 0.2.0,
  `framework_spec_version` 0.1.0, no Version History, `charts-flow` not
  mermaid-gen, references limited to the canonical set).
- Wire in: `doc-flow` (mention CHG overlay + gate-check), `skill-recommender`
  catalog, plugin `README` inventory (46→52), `CHANGELOG [Unreleased]`,
  `docs/PARITY.md` count, and `plm_lint.py` `MIGRATED` (+doc-chg, gate-check,
  project-adopt).

## Verification

- 52 skill dirs / 52 SKILL.md; new skills: name==dirname, version 0.2.0,
  framework_spec_version 0.1.0, no Version History, no removed-skill refs.
- No dangling skill cross-refs or framework paths.
- Conformance suite green.

## Review log

### Implementation — 2026-05-23T17:07:07Z (VERIFIED)

- Authored the 6 skills via two parallel agents (CHG family; gate-check +
  project-adopt), each grounded in `framework/governance/chg/` + `SKILL_AUTHORING.md`.
- CHG family carries no numeric `layer` (governance overlay), `artifact_type: CHG`,
  and reports `gate_ready` rather than a ≥90 score.
- Wired in: `doc-flow` (brownfield path + a Change-management section),
  `skill-recommender` (intent rows + catalog, 46→52), plugin `README` (added a
  change-management row; utilities 14→16; total 52), `CHANGELOG [Unreleased]`
  Added entry, `docs/PARITY.md` (52 + CHG/gate-check/project-adopt), and
  `plm_lint.py` `MIGRATED` (+doc-chg, gate-check, project-adopt).
- **Verification:** 52 dirs / 52 SKILL.md; 6 new skills pass acceptance
  (name==dirname, version 0.2.0, framework_spec_version 0.1.0, no Version
  History, no removed-skill refs); no dangling skill cross-refs or framework
  paths; conformance **32 passed, 103 subtests**.
- Deferred (by user choice): `doc-code`/implement.
