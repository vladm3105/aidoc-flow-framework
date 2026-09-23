# TYPE-R Plan — code-to-doc reconciliation flow + MINOR bump 0.54.0 → 0.55.0

| Field | Value |
|-------|-------|
| Task | TYPE-R-RECONCILIATION |
| Type | feature (governance, engine-agnostic) |
| Status | DRAFT — 2026-09-21T00:00:00Z (Pass 0; needs two review cycles before plan PR) |
| Base | `feat/type-r-reconciliation-flow` @ `dev` (framework `0.54.0`) |
| Feeds | `0.55.0` release |
| Version impact | **MINOR `0.54.0 → 0.55.0`** — new `change_source` enum value + governance prose; no instance-format break (GD-17 untouched); change-level **C2** per GATE-SPEC |

## Objective

Formalize the **Type-R (Reconciliation) change flow**: when a verified working codebase temporarily precedes its specifications (empirical integration discovery, browser-authored test suites, critical flakiness remediation, emergency operational fixes handled outside the Emergency path), the change propagates **backward** Code → IPLAN (reverse-authored from ground truth) → upstream SDD layers, instead of fabricating a fictional design-first chronology. The framework today defines only the forward flow plus `Emergency: fix → deploy → document in 48h`; `Feedback/GATE-CODE` bubble-up covers production defects but not code-leads-docs reconciliation. This plan lands the Type-R kernel generalized from PR #654's project-donor text (no donor literals: no Privy/Bridge, Playwright, `go test`/`npm` commands, `USER_JOURNEYS.md`, `*-00` ledgers, `docs/sdd/` paths, `chg_lint.py` script names).

## Scope

**In (one concept, six surfaces):**

| # | Change | Target path(s) | Class |
|---|--------|----------------|-------|
| 1 | §3.1.2 Type-R section: trigger conditions, 5-phase flow (freeze+manifest → reverse IPLAN → upstream reconciliation → doc sync → bi-directional verification), 3 guardrails | `framework/governance/DOC_GOVERNANCE_CORE.md` (after §3.1.1, before IPLAN Gate) | prose |
| 2 | Change Source Routing row + Dual Lifecycle section (Forward design-first vs Backward reconciliation-first) | `framework/governance/chg/README.md` + `framework/layers/09_CHG/README.md` (twins kept identical for these hunks) | prose |
| 3 | `change_source: reconciliation` enum value + guidance row (entry GATE-CODE; cascade Code→IPLAN→TDD→SPEC→BDD→EARS; upstream fix as dependent CHG) | `framework/governance/chg/CHG-TEMPLATE.yaml` + `framework/layers/09_CHG/CHG-TEMPLATE.yaml` (both `value:` comment lines + `_guidance` table) | template |
| 4 | Typical-change-source + routing note for reconciliation bubble-up | `framework/governance/chg/gates/GATE-CODE_IMPLEMENTATION.md` + `framework/layers/09_CHG/gates/GATE-CODE_IMPLEMENTATION.md` (§1.3 list + §6.2 pointer) | prose |
| 5 | GD-30 decision entry | `framework/governance/DECISIONS.md` | prose |
| 6 | MINOR bump + fanout | `framework/VERSION` `0.54.0→0.55.0`, `CHANGELOG.md`, `framework/CHANGELOG.md` (mechanical pin sweep via `hooks/sync-version-refs.sh`) | release |

**Out (explicitly not in this change):**

- `GOVERNANCE_RULES.md` as a framework file — rejected; project manual, violates engine-agnostic spec + `EXPECTED_FILES` pin in `test_governance.py`.
- New lint rules or `chg_lint.py` checks — `change_source` is not enum-validated by the linter today; docs + template only. A follow-up may add an advisory check.
- `GATE_ERROR_CATALOG.md` new codes — no new blocking checks, so no catalog entries.
- Project-only donor material (§1 infra, §8 wire contracts, `docs/sdd/` paths, verify commands, P0-Card gate) — stays donor-local.
- Twin-drift repair beyond these hunks (the `validation:` block and archive-layer-list deltas between the CHG-TEMPLATE/README twins predate this change) — noted, not fixed here.

## Approach / Design

- **Decision A — one value, `reconciliation`.** Donor proposed `reconciliation` (or `backward_propagation`). One canonical value keeps the enum closed and the conformance assertion (`test_governance.py:105` checks `spec` presence; additive-safe) green.
- **Decision B — bounded exception, not second default.** Type-R text states preconditions (verification gates green BEFORE doc propagation; freeze; no new unverified code mid-reconciliation) and frames itself as the honest alternative to backdating design-first history. SDD-first (§3.1.1) stays the default; Emergency stays the production-hotfix path. Disambiguation is normative: a critical production issue uses Emergency + post-mortem, never Type-R — Type-R must not become a post-mortem dodge. Type-R covers non-emergency empirical work where the codebase is green and stable enough to serve as ground truth.
- **Decision C — feedback-row language reuse.** The new routing/template rows mirror the existing `Feedback` bubble-up phrasing (dependent upstream CHG, gates reached upstream), so readers and the GATE-CODE §6.2 process need no new mental model.
- **Decision D — twins move together.** Every hunk lands byte-identical in `governance/chg/` and `layers/09_CHG/` except where the twins already differ (untouched).
- **Decision E — CHG-04 + IPLAN-04 per GATE-SPEC.** Framework self-change: `framework/archive/CHG-04/` holds `CHG-04.yaml` (C2, `change_source: spec`, `semver_impact: minor`) + `IPLAN-04.yaml` (authorizing, `In Progress` during implementation) + archived originals. Rollback = revert branch before merge.

## Verification

- `python sdd_doc_lint/chg_lint.py framework/archive/CHG-04/CHG-04.yaml` → exit 0 (pre-commit, pre-implementation, pre-merge).
- `python -m unittest discover -s tests/conformance` → green (esp. `test_governance.py`: `EXPECTED_FILES` unchanged, template parses, SPEC-gate wiring intact).
- `python -m unittest discover -s tests/acceptance/deterministic` → green, no golden churn.
- `pre-commit run --all-files` → green (after conflict-free edit; no rebase seams expected).
- Corpus cross-check (per CLAUDE.md plan rule): `python3 -m sdd_doc_lint examples/*/docs/` → zero unexpected findings (template enum addition is additive; no `@`-tag semantics touched).

## Review log

### Pass 1 — 2026-09-21T00:00:00Z (self-review vs codebase)

Gaps found:

1. Emergency vs Type-R disambiguation missing — donor lists "emergency operational bugfixes" as a Type-R trigger, which overlaps the framework's Emergency level and could route hotfixes around the post-mortem. Patched Decision B: Emergency-qualifying work must use Emergency; Type-R is non-emergency empirical work only. Spec text must carry this.
2. Sync script path wrong (`scripts/` vs `hooks/sync-version-refs.sh`, verified by `ls hooks/`). Patched row 6.

### Pass 2 — 2026-09-21T00:00:00Z (re-review of patched plan)

- Re-checked twin edit points: `chg/README.md` vs `layers/09_CHG/README.md` differ only in the archive-layer-list line (verified `diff`); routing-table + new-section hunks apply to both. `CHG-TEMPLATE.yaml` twins differ only by `layer: 9` line and the governance copy's extra `validation:` §7 block; `change_source` hunks (guidance table + both `value:` comments) apply to both. `GATE-CODE_IMPLEMENTATION.md` twins identical.
- `test_governance.py:105` asserts only `spec` presence — additive enum value is conformance-safe. `EXPECTED_FILES` pin means no new files: plan adds none.
- Linter (`sdd_doc_lint/chg_lint.py`) has no `change_source` enum validation — docs + template scope is sufficient, no tooling change.
- GD-29 newest (`grep ^## GD-`), so GD-30 is next. No `scripts/` dir at root — hooks path confirmed.
- Corpus cross-check runs at implementation (template change is additive; no tag semantics touched).
  Result 2026-09-21: N/A — this repo ships no `examples/` corpus (framework-only layout
  post-CLEANUP-001); acceptance deterministic (64 OK) covers goldens.
- No new substantive gaps. Plan ready for implementation on this branch (plan PR opens with impl per single-initiative flow; no stacked-plan amendment).

### Implementation review (OPS-0065 3-agent parallel, single fold cycle) — 2026-09-21

- Templates/gates reviewer: success, no findings (enum in all 4 lines, twins identical, YAML parses).
- Release-mechanics reviewer: success + 1 flag: stray untracked `.mimocode/learning/` file — left untracked, never staged (explicit file-list commits only); no fixer noise in tree (19 pre-commit reformats reverted, 107 sweep-only files kept).
- Spec-prose reviewer: success + 2 SHOULD-FIX, both folded into §3.1.2: (1) §3.13 carve-out — new guardrail 4 states the reverse-authored In-Progress IPLAN authorizes all post-freeze writes and GOV-013 stays a forward-flow check; (2) Emergency-exclusion rationale now required in the Type-R CHG description, trigger reworded off "critical".
- Pre-existing failures documented as out of scope: `check-yaml` (`.github/labeler.yml` duplicate key), `yamllint` (acceptance fixtures), `markdownlint` (`plans/CLEANUP-001-PLAN.md`), `ruff (legacy alias)` env issue — all in files outside this change set, all present on dev baseline.
- Incidental finding promoted: `hooks/sync-version-refs.sh` was stale (no 0.54.0 literals — every future bump would silently no-op) and rewrote frozen `framework/archive/` originals; fixed with 0.54.0 literals + archive exclusion (order 12, CHG-04 SYNC-SCRIPT entry).
- Verification: chg_lint 0 errors (1 pre-existing advisory warning, same as CHG-03); conformance 355 OK skipped=1; acceptance 64 OK; corpus N/A (no `examples/` in this repo).
