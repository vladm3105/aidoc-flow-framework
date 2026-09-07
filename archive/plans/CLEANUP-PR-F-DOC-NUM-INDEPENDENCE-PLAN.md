# CLEANUP-PR-F — Doc-Number Independence Across Layers

> Single-item follow-up PR. Closes `plans/FRAMEWORK-TODO.md` item #18.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | CLEANUP-PR-F                                |
| Type           | combined plan + impl (small, docs + SKILL prose) |
| Worktree       | `feat/cleanup-pr-f-doc-num-independence`    |
| Depends on     | FRAMEWORK-CLEANUP-001 (PRs #128-#134) — all merged |
| Closes         | `plans/FRAMEWORK-TODO.md` item #18 |
| Version impact | Framework PATCH `0.20.0 → 0.20.1` (new ID_NAMING_STANDARDS subsection + SKILL prompt clarifications); plugin PATCH `0.17.0 → 0.17.1` |
| Status         | DRAFT — 2026-06-11 |

## Item closed

| # | Tag | Item |
|---|---|---|
| 18 | `[governance]` | Doc-number independence across layers not codified |

## Problem

User clarification (2026-06-11): document numbers (the `NN` in
`BRD-01` / `PRD-01` / `EARS-01` / ...) are **per-layer sequential and
INDEPENDENT** across layers. One BRD MAY drive multiple downstream
PRDs (`PRD-01`, `PRD-02`, ...); one PRD MAY cite multiple BRD docs
via multiple `@brd: BRD-NN` citations.

Currently the framework has zero explicit mention of this:

- `ID_NAMING_STANDARDS.md` says *"sequential two-digit number"* — per
  layer, but doesn't say INDEPENDENT across.
- `TRACEABILITY.md` has no cross-layer cardinality discussion.
- `REVIEW_TEAM.md` + `REVIEW_REMEDIATION_FLOW.md` silent on
  cardinality.
- url-shortener example's 1:1 numbering (BRD-01 → PRD-01 → ... →
  IPLAN-01) reinforces the WRONG "numbers line up" mental model. A
  reader could reasonably conclude doc numbers are cumulative across
  layers.

## Fix shape

### Item 18a — `ID_NAMING_STANDARDS.md` "Cross-layer cardinality" subsection

Insert a new subsection between the Document-IDs table (§Document IDs)
and the §Element IDs section. ~30 lines documenting:

- Doc numbers are per-layer sequential and **independent across
  layers**
- **One-to-many supported** — one BRD MAY drive multiple PRDs
- **Many-to-one supported** — one PRD MAY cite multiple BRDs via
  multiple `@brd:` tags
- The url-shortener example's 1:1 numbering is COINCIDENCE, not
  contract

### Item 18b — 8 doc-<layer> author SKILLs Reserve ID step

Each `doc-<layer>/SKILL.md` Reserve ID step gets a one-line
clarification: *"Pick the next-free number in YOUR layer's index;
the upstream's number is NOT relevant to your choice (doc numbers
are per-layer independent — see `ID_NAMING_STANDARDS.md`
§Cross-layer cardinality)."*

### Item 18c — Auditor playbooks orphan-vs-sibling note

The 6 auditor playbooks (BRD, PRD, BDD, ADR, TDD, IPLAN — EARS and
SPEC have no auditor lens) gain a one-line beyond-checklist note:
*"Apparent-orphan downstream docs (e.g., PRD-02 with `@brd: BRD-01`
when PRD-01 also exists) MAY be valid siblings of the same upstream,
not actual orphans — doc numbers are per-layer independent per
`ID_NAMING_STANDARDS.md` §Cross-layer cardinality."*

### Item 18d — `TRACEABILITY.md` cross-reference

Add a one-line cross-reference in §Cumulative Tagging pointing to
the new ID_NAMING_STANDARDS §Cross-layer cardinality subsection.

## File structure

### Modified

| Path | Item | Change |
|---|---|---|
| `framework/governance/ID_NAMING_STANDARDS.md` | 18a | New "Cross-layer cardinality" subsection (~30 lines) between §Document IDs and §Element IDs |
| 8 × `platforms/claude-code-plugin/skills/doc-<layer>/SKILL.md` | 18b | One-line clarification in Reserve ID step |
| 6 × `framework/playbooks/<NN>_<LAYER>/auditor.md` (01_BRD, 02_PRD, 04_BDD, 05_ADR, 07_TDD, 08_IPLAN) | 18c | One-line beyond-checklist note on orphan-vs-sibling |
| `framework/governance/TRACEABILITY.md` | 18d | One-line cross-reference in §Cumulative Tagging |
| `framework/VERSION` + `platforms/claude-code-plugin/VERSION` + 2 × `FRAMEWORK_SPEC_VERSION` | — | `0.20.0 → 0.20.1` PATCH + `0.17.0 → 0.17.1` PATCH |
| CHANGELOG.md, docs/TAGGING.md (2 rows), plans/HANDOFF.md, plans/FRAMEWORK-TODO.md (item #18 Open → Closed) | — | Docs of record |

**Total: ~17 substantive file edits + sync re-propagation.**

### Out of scope

- Re-cascading url-shortener corpus to demonstrate non-1:1 numbering
  (would need a multi-PRD scenario; not part of this PR)
- Hermes mirror — plugin-first per HERMES-CATCHUP-001
- Promoting cross-layer cardinality to a runtime-validated rule (no
  rule currently exists to validate; making one would be scope creep)

## Implementation sequence

1. Plan iterative review (2 cycles)
2. ID_NAMING_STANDARDS update (item 18a)
3. 8 doc-<layer> SKILL Reserve ID updates (item 18b)
4. 6 auditor playbook notes (item 18c)
5. TRACEABILITY cross-reference (item 18d)
6. Version + sync + docs of record
7. Conformance + lint cheap checks
8. Open PR

## Verification

| # | Check | Expected |
|---|---|---|
| 1 | ID_NAMING_STANDARDS has §"Cross-layer cardinality" subsection | PASS — grep |
| 2 | 8 doc-<layer> SKILLs reference §Cross-layer cardinality | PASS — grep |
| 3 | 6 auditor playbooks have orphan-vs-sibling note | PASS — grep |
| 4 | TRACEABILITY.md cross-references the new subsection | PASS — grep |
| 5 | Conformance: 120/120 PASS | PASS |
| 6 | Unit: 47/47 PASS | PASS |
| 7 | url-shortener lint clean (no regression) | PASS |

## Review log

### Pass 0 — initial draft

- **Date:** 2026-06-11T23:55:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-12T00:00:00Z
- **Cross-checks:**
  - `ID_NAMING_STANDARDS.md` has §Document IDs at line 3, §Element IDs at line 18 — insertion site exists ✓
  - 8 doc-<layer> SKILLs all have "Reserve ID" step (verified) ✓
  - 6 auditor playbooks exist (no EARS, no SPEC — confirmed earlier in PR-B) ✓
  - `TRACEABILITY.md` has §Cumulative Tagging at line 9 — cross-reference site ✓
- **Findings (0 substantive):** plan is minimal-and-realistic; sized
  to 1 item per scope.

### Pass 2 — re-review

- **Date:** 2026-06-12T00:05:00Z
- **Findings:** 0 substantive. Self-converged.
- **Verdict:** Per FRAMEWORK-CLEANUP-001 Pass 4 lesson, user-driven
  review on the PR is the real convergence gate.
