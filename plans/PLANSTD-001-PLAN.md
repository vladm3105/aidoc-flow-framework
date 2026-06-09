# PLANSTD-001 Implementation Plan — Unified AI-agent plan template + IPLAN-layer plan standard

| Field          | Value                                            |
|----------------|--------------------------------------------------|
| Task           | PLANSTD-001                                       |
| Type           | feature (spec + repo template)                    |
| Status         | PLANNED — 2026-06-09T00:00:00Z                   |
| Depends on     | none (clean base from `main`, framework `0.14.3`) |
| Feeds          | every future plan in `plans/` (and downstream repos that adopt the standard) |
| Version impact | `framework/VERSION` MINOR (additive spec doc); both `FRAMEWORK_SPEC_VERSION` conformance pointers re-matched to it; plugin & Hermes **product** versions unchanged (independent streams — see D-PLANSTD-5, resolved). Exact framework number resolved at impl time against then-current `main` |

## Objective

Replace the thin, migration-flavored `plans/PLAN-TEMPLATE.md` with a single
**unified plan template** that scales from a one-commit bugfix to a multi-phase
feature, is engine-agnostic and repo-agnostic, and lets an execution agent keep
only the chapters that apply to the work type (e.g. a documentation plan drops
the TDD/test chapters). Anchor that template to a normative **plan standard**
document in the IPLAN layer of the framework spec, so the structure, the
section-applicability rules, and the two-pass review discipline are specified
once and reused everywhere.

## Scope

**In:**

- Rewrite `plans/PLAN-TEMPLATE.md` to the approved unified template (metadata
  table with `Type`/`Version impact`; `[REQUIRED]`/`[CODE]`/`[IF APPLICABLE]`
  section tags; an APPLICABILITY MATRIX header that maps work type → sections
  to keep; explicit "delete non-applicable chapters" instruction; File
  structure, Out of scope, Implementation sequence as `### Task N`, Verification
  table, Docs-to-update checklist, Risks, Review log).
- Create one normative standard doc in `framework/layers/08_IPLAN/` describing
  that template: purpose, section catalog with applicability semantics, the
  work-type matrix, and the review discipline. Engine-agnostic.
- Re-vendor the plugin framework bundle (`tools/sync-plugin-framework.sh`) so
  the new spec doc is mirrored byte-identically (D-0022).
- Bump `framework/VERSION` + both `platforms/*/FRAMEWORK_SPEC_VERSION`; let the
  mechanical doc-sync hook propagate version strings.
- Update docs of record (CHANGELOG, ROADMAP, HANDOFF, PARITY current-state row).

## Out of scope (deferred)

- Migrating existing `plans/*.md` to the new structure — they are already
  instantiated; the template governs *new* plans only.
- A separate lightweight DESIGN template — DESIGN docs use the same unified
  template with `Type: design` and unused chapters deleted; revisit only if a
  real DESIGN doc proves the unified form too heavy.
- Conformance *enforcement* of the standard (a test that lints `plans/*.md`
  against the standard) — no named issue requires it yet; backlog one-liner.
- Rolling the template out to sibling repos (`ibmcp`, `b_local`, `trading`) —
  done by copying `plans/PLAN-TEMPLATE.md` per repo once this lands.

## Approach / Design

Two artifacts, one source of truth:

1. **`framework/layers/08_IPLAN/PLAN_STANDARD.md`** (normative spec) —
   defines the unified plan structure and the applicability rules. Engine- and
   repo-agnostic so it can be vendored into the plugin and adopted by any repo.
2. **`plans/PLAN-TEMPLATE.md`** (working instance) — this repo's copy-paste
   starting point, conforming to the standard.

**Design decisions (record in `plans/DECISIONS.md` at land):**

- **D-PLANSTD-1 — placement.** The standard lives in `framework/layers/08_IPLAN/`
  per the request. It governs *general development / work plans* (feature,
  bugfix, docs, refactor, chore) authored as markdown in repo `plans/` dirs. It
  is a **third, orthogonal concept**, explicitly distinct from BOTH formal IPLAN
  YAML artifacts the layer already defines: (a) the Permanent per-SPEC-component
  `IPLAN-TEMPLATE.yaml` (file manifest + session handoff), and (b) the Temporary
  `tmp/TMP-IPLAN-*.yaml` bugfix artifacts. Neither YAML artifact changes. The
  standard doc opens with an explicit scope boundary, and the IPLAN `README.md`
  cross-link (Task 3) must state plainly that the new doc governs markdown
  `plans/*.md`, NOT the README's existing YAML Permanent/Temporary slots — this
  cross-link is load-bearing for the layer's conceptual coherence (R1).
- **D-PLANSTD-2 — flexibility mechanism.** Section applicability is expressed by
  inline tags (`[REQUIRED]` always; `[CODE]` only when executable code/tests
  change; `[IF APPLICABLE]` only when it has real content) plus a single
  APPLICABILITY MATRIX in the template header. The agent reads the matrix for
  its work type, keeps the listed sections, and **deletes** the rest — no empty
  headings or "N/A" stubs survive into a real plan. TDD is a single `[CODE]`
  line inside Implementation, deleted for documentation/chore work. The
  confirmed work-type set (2026-06-09) is **`feature` / `bugfix` /
  `documentation` / `refactor` / `chore`**.
- **D-PLANSTD-3 — engine-agnostic content.** The standard doc must satisfy
  `test_spec_hygiene.py`, which scans every file under `framework/`. Explicit
  forbidden patterns (all case-insensitive): `hermes`, `ucx_`, `.claude/`,
  bare-word `\bmcp\b` (the word "mcp" anywhere trips it), `mermaid-gen`,
  `charts-flow`, the SDD-verb regex `sdd_(validate|create|score_validate|
  consistency|preflight|next_action|review|remediate)`, the literal substring
  `framework_version`, and `SDD v3` (except on a `derived_from:` line). So the
  doc describes the metadata table's version field WITHOUT writing the literal
  `framework_version` and WITHOUT quoting any version string.
- **D-PLANSTD-4 — verification is REQUIRED for all work types**, but its *kind*
  differs: code plans verify with runnable commands; documentation plans verify
  with lint/link-check/render/review-pass. A docs plan may drop TDD but never
  drops Verification.
- **D-PLANSTD-5 — version streams (RESOLVED 2026-06-09).** `docs/PROJECT.md` §2
  defines four independent SemVer streams; `framework/VERSION` is the
  framework's *own* spec-release number, independent from per-template
  `metadata.schema_version` (all pinned `"1.0"` while `framework/VERSION` reached
  `0.14.3`), document-instance versions, and the platform **product** streams.
  Decision: adding the doc bumps **`framework/VERSION` (MINOR)** — forced by
  GATE-SPEC-E005, which fires on any `framework/**` change with no path
  exclusion. Both `FRAMEWORK_SPEC_VERSION` files are **conformance pointers**
  (not product versions) and are re-matched to `framework/VERSION` by
  conformance. The plugin's own product version (`platforms/claude-code-plugin/VERSION`
  = `0.10.0`) and `platforms/hermes/VERSION` **do NOT bump** — a vendored spec
  doc the skills never invoke is not a platform product release; precedent is
  the framework `0.11.1/.2/.3` spec re-syncs that left the plugin product
  version untouched. The standard doc carries **no internal version field**
  (matches existing governance markdown).
- **D-PLANSTD-6 — markdown-lint clean (asymmetric enforcement).** `.pre-commit-config.yaml`
  globally excludes `^framework/` (and the vendored plugin bundle) from ALL
  hooks. Consequence: `plans/PLAN-TEMPLATE.md` IS auto-linted by the
  `markdownlint`/`end-of-file-fixer`/`trailing-whitespace` hooks, but
  `framework/layers/08_IPLAN/PLAN_STANDARD.md` is NOT — its markdown
  style is unenforced by hooks. To keep the spec doc clean, run `markdownlint`
  on it directly (not via the `pre-commit` wrapper, which will skip it). The
  conformance gate still applies to the spec doc (it is `always_run`, not
  file-filtered).

## File structure

### Created

- `framework/layers/08_IPLAN/PLAN_STANDARD.md` — normative standard for
  the unified plan template (spec layer; engine-agnostic).
- `platforms/claude-code-plugin/framework/layers/08_IPLAN/PLAN_STANDARD.md`
  — vendored mirror (generated by `tools/sync-plugin-framework.sh`, not
  hand-authored).

### Modified

- `plans/PLAN-TEMPLATE.md` — replaced with the unified template.
- `framework/layers/08_IPLAN/README.md` — add a cross-link + scope note
  distinguishing the formal IPLAN YAML artifact from the unified plan standard.
- `framework/VERSION` — MINOR bump.
- `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION`,
  `platforms/hermes/FRAMEWORK_SPEC_VERSION` — match `framework/VERSION`.
- Version-quoting docs touched by `scripts/sync-version-refs.sh` (auto, on the
  VERSION commit): `plugin.json`, `marketplace.json`, SKILL.md frontmatter,
  `README.md`, `docs/PARITY.md` current-state row, etc.
- `CHANGELOG.md`, `ROADMAP.md`, `plans/HANDOFF.md`, `plans/DECISIONS.md` —
  doc-of-record updates (human-authored).

## Implementation sequence

### Task 1: Author the standard doc

- Create `framework/layers/08_IPLAN/PLAN_STANDARD.md`: scope boundary
  vs formal IPLAN YAML; section catalog with `[REQUIRED]`/`[CODE]`/
  `[IF APPLICABLE]` semantics; APPLICABILITY MATRIX (feature / bugfix /
  documentation / refactor / chore); two-pass Review-log discipline.
- Keep it engine-agnostic (D-PLANSTD-3); no hardcoded version string.

### Task 2: Rewrite the repo template

- Replace `plans/PLAN-TEMPLATE.md` with the approved unified template; ensure it
  conforms to the standard authored in Task 1 (same section names + tags).

### Task 3: Cross-link the IPLAN README

- Add a short scope note + link in `framework/layers/08_IPLAN/README.md` stating
  the new standard governs markdown `plans/*.md` dev/work plans, distinct from
  BOTH the YAML Permanent IPLAN and the YAML `tmp/` Temporary IPLAN (D-PLANSTD-1).
  This cross-link is load-bearing for the layer's coherence.

### Task 4: Bump versions, then re-vendor

- Bump `framework/VERSION` (MINOR) and re-match both `FRAMEWORK_SPEC_VERSION`
  pointers to it. Leave `platforms/claude-code-plugin/VERSION` and
  `platforms/hermes/VERSION` (product streams) **unchanged** per D-PLANSTD-5.
  Do this *before* the vendor re-sync and the commit (not before authoring) so
  the mechanical hook propagates version strings first.
- Run `bash tools/sync-plugin-framework.sh` to mirror the new doc into the
  plugin bundle byte-identically.

### Task 5: Update docs of record

- CHANGELOG entry, ROADMAP bullet, HANDOFF narrative, DECISIONS entries
  (D-PLANSTD-1..4), PARITY current-state row (handled by the version hook).

### Task 6: Verify and land

- Run Verification (below); all checks green.
- Commit (conventional prefixes; one logical change per commit); open the impl
  PR only after Verification passes.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
|----|-------------------------------|-----------------|---------|
| V1 | `python3 -m unittest discover -s tests/conformance -v` | all green — esp. `test_plugin_framework_bundle`, `test_spec_hygiene`, `test_layers` | spec stays coherent; no engine tokens; layer triad intact |
| V2 | `diff -rq framework/layers platforms/claude-code-plugin/framework/layers` | no output (vendor synced) | D-0022 byte-identical bundle |
| V3 | Manual walk-through: instantiate the template as `Type: documentation` AND `Type: bugfix` | TDD/`[CODE]` lines cleanly deletable for docs; matrix sections resolve for both; no orphan headings | D-PLANSTD-2 flexibility |
| V4 | `git commit` of the VERSION change | `scripts/sync-version-refs.sh` runs, re-stages, idempotent; `FRAMEWORK_SPEC_VERSION` files == `framework/VERSION` | version streams consistent |
| V5 | Inspect CHANGELOG/ROADMAP/HANDOFF | each reflects PLANSTD-001 | docs-of-record discipline |
| V6 | `markdownlint framework/layers/08_IPLAN/PLAN_STANDARD.md` (direct) AND `pre-commit run markdownlint --files plans/PLAN-TEMPLATE.md` | both pass | D-PLANSTD-6 markdown-lint clean (spec doc linted directly; `plans/` template via hook) |
| V7 | `python tests/chg/spec_gate.py` with base `origin/main` | pass — GATE-SPEC-E005 (`framework/VERSION` in diff) + E008 (`CHANGELOG.md` in diff) satisfied | R7 / merge-blocking CI gate |

> **Safety net:** the conformance suite (V1) runs as an `always_run` pre-commit
> hook (`.pre-commit-config.yaml:96`), so a drifted vendor bundle blocks the
> commit locally — not only CI. GATE-SPEC (V7) is a separate CI workflow
> (`.github/workflows/chg-gate.yml`); run `spec_gate.py` locally before pushing.
> Note: the `^framework/` hook exclude means the spec doc is NOT auto-linted by
> the markdownlint hook (V6 lints it directly).

## Docs & artifacts to update

- [ ] `CHANGELOG.md` — PLANSTD-001 entry
- [ ] `ROADMAP.md` — bullet
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — D-PLANSTD-1..4
- [ ] `docs/PARITY.md` current-state row — via version hook (auto)
- [ ] `framework/VERSION` + both `FRAMEWORK_SPEC_VERSION` — bumped UPFRONT (Task 4)

## Risks

| #  | Risk | Likelihood | Mitigation |
|----|------|-----------|------------|
| R1 | Placing a general dev-plan standard in the SDD `08_IPLAN` layer blurs that layer's identity (formal IPLAN = per-SPEC YAML execution bridge) | med | Standard doc opens with an explicit scope boundary; README cross-link; `IPLAN-TEMPLATE.yaml` semantics untouched (D-PLANSTD-1) |
| R2 | Adding to `framework/` without re-vendoring fails `test_plugin_framework_bundle` | high if skipped | Task 4 runs `tools/sync-plugin-framework.sh`; V1+V2 catch drift |
| R3 | Engine tokens / version strings in the standard doc fail `test_spec_hygiene` | med | D-PLANSTD-3 keeps it engine-agnostic & version-free; V1 catches |
| R4 | Version-stream collision — `main` advances (SPEC-RT-001 / PRD-RT-001 in flight) before merge | med | Bump from then-current `main` at impl time; rebase before opening impl PR |
| R5 | Existing in-flight plans break when `PLAN-TEMPLATE.md` changes | low | Template change does not touch already-instantiated plans; out of scope |
| R6 | `plans/PLAN-TEMPLATE.md` fails `markdownlint` pre-commit hook (line length, heading levels, list style), blocking the commit | med | Author to repo markdown conventions; V6 runs the linter before commit (D-PLANSTD-6) |
| R7 | GATE-SPEC CI gate (`tests/chg/spec_gate.py`) blocks the merge if `framework/VERSION` or `CHANGELOG.md` is absent from the PR diff (E005/E008) — a recurring trip-up (ADR-RT-001 PR #108) | high if forgotten | Task 4 bumps VERSION, Task 5 updates CHANGELOG, both in the same PR; V7 runs the gate locally before push |

## Claim ledger

| #  | Claim | Symbol | Citation |
|----|-------|--------|----------|
| 1  | `plans/PLAN-TEMPLATE.md` exists and is the current (thin, migration-flavored) plan template | — | plans/PLAN-TEMPLATE.md:1 |
| 2  | The IPLAN layer dir holds README + YAML template + YAML index (the conformance triad); no general markdown plan standard yet | `## Template` | framework/layers/08_IPLAN/README.md:55 |
| 3  | The formal IPLAN artifact is a per-SPEC-component YAML (file manifest, session handoff), not a general dev plan | `iplan-document` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:14 |
| 4  | IPLAN README already splits Permanent (YAML/per-SPEC) vs Temporary (bugfix/disposable) plans | `Permanent vs Temporary` | framework/layers/08_IPLAN/README.md:11 |
| 5  | `test_layers.py` checks only that the triad is *present* — it has no "no unexpected files" assertion, so adding a doc to a layer dir is safe | `class LayerFiles` | tests/conformance/test_layers.py:11 |
| 6  | `test_governance.py`'s `test_no_unexpected_files` (and the stricter `test_no_orphan_governance_files`, :107) are both scoped to `framework/governance/`, not `framework/layers/` | `test_no_unexpected_files` | tests/conformance/test_governance.py:64 |
| 7  | The plugin vendors `framework/{layers,governance,registry,playbooks}` + one root doc, and conformance fails on any fileset/byte drift (D-0022) | `test_bundle_fileset_matches_canonical` | tests/conformance/platforms/test_plugin_framework_bundle.py:45 |
| 8  | Re-sync after editing canonical spec is `bash tools/sync-plugin-framework.sh` | `sync-plugin-framework.sh` | tests/conformance/platforms/test_plugin_framework_bundle.py:11 |
| 9  | `tools/sync-plugin-framework.sh` mirrors the `layers` subtree, so a new 08_IPLAN doc propagates to the plugin bundle | `SUBTREES=(layers` | tools/sync-plugin-framework.sh:24 |
| 10 | `framework/VERSION` is `0.14.3` on `main` (the branch base) | `0.14.3` | framework/VERSION:1 |
| 11 | Both platforms declare spec version `0.14.3`, which must match `framework/VERSION` | `0.14.3` | platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION:1 |
| 12 | Spec hygiene forbids engine tokens (`hermes`, `ucx_`, `.claude/`, `mcp`, …) and stale version strings under `framework/` | `test_spec_hygiene.py` | tests/conformance/README.md:40 |
| 13 | Conformance is run with `python3 -m unittest discover -s tests/conformance -v` | `unittest discover` | tests/conformance/README.md:22 |
| 14 | A mechanical pre-commit hook propagates version strings on a VERSION change | `Mechanical doc-sync` | scripts/sync-version-refs.sh:2 |
| 15 | A semantic pre-commit hook warns when code/spec changes but no doc-of-record is touched | `Warning hook` | scripts/check-docs-updated.sh:2 |
| 16 | Real plans in this repo carry File-structure / Implementation-sequence(`### Task N`) / Out-of-scope / Review-log sections the current template lacks | `## File structure` | plans/ADR-RT-001-PLAN.md:36 |
| 17 | The conformance suite runs as a pre-commit hook, so a drifted vendor bundle blocks the commit locally (not only CI) | `id: conformance` | .pre-commit-config.yaml:96 |
| 18 | `markdownlint` runs as a pre-commit hook, so the new markdown files must be lint-clean to commit | `id: markdownlint` | .pre-commit-config.yaml:55 |
| 19 | `sync-version-refs.sh` + `check-docs-updated.sh` are wired as pre-commit hooks | `id: sync-version-refs` | .pre-commit-config.yaml:108 |
| 20 | The plugin's own SemVer is `0.10.0`, tracked separately from `FRAMEWORK_SPEC_VERSION` | `0.10.0` | platforms/claude-code-plugin/VERSION:1 |
| 21 | GATE-SPEC CI enforces E005 (`framework/VERSION` in diff) + E008 (`CHANGELOG.md` in diff) for any `framework/**` change; run via the chg-gate workflow | `framework/VERSION` | tests/chg/spec_gate.py:85 |
| 22 | `.pre-commit-config.yaml` globally excludes `^framework/` (and the vendored bundle) from ALL hooks, so the spec doc is not auto-linted by the markdownlint hook | `exclude:` | .pre-commit-config.yaml:14 |

## Review log

> A plan needs **at least two** passes before it is presented or implemented
> (CLAUDE.md § Development workflow), and ≥1 pass must be an **independent
> fresh-context review** (verified-planning). Each pass: re-read the whole plan,
> list findings, fold fixes back into the sections above; the next pass
> re-validates the prior pass's edits. Stop when a pass surfaces zero
> load-bearing findings. Each pass also cross-checks Verification against
> Objective + Scope, and the Claim ledger for `UNVERIFIED` rows.

### Pass 1 — 2026-06-09 — self-review

- **Hook installation confirmed (was an unverified V4 assumption).** Hooks run
  via the `pre-commit` framework (`.pre-commit-config.yaml`). Verified that
  `conformance`, `markdownlint`, `sync-version-refs`, and `check-docs-updated`
  are all wired. → Claims 17–19 added; Verification "Safety net" note added.
- **Missing constraint: markdownlint.** The two authored markdown files must be
  lint-clean to commit. → Added D-PLANSTD-6, V6, R6, Claim 18.
- **Plugin-own-version ambiguity.** A vendor-only doc addition's effect on
  `platforms/claude-code-plugin/VERSION` (0.10.0) vs `FRAMEWORK_SPEC_VERSION`
  was conflated in the metadata table. → Split into D-PLANSTD-5; metadata
  `Version impact` corrected; Claim 20 added.
- **"UPFRONT" wording** in Task 4 was ambiguous (before authoring vs before
  commit). → Clarified: bump before vendor-sync/commit, after authoring.
- **Standard-doc name** `PLAN_STANDARD.md` is provisional pending user
  confirmation; noted in Approach.

### Pass 2 — 2026-06-09 — independent (fresh-context subagent)

Adversarial fresh-context review against real source. Two load-bearing findings,
both folded in; several citation-accuracy nits fixed.

- **L1 — missing GATE-SPEC gate in Verification.** A spec-touching PR runs
  `tests/chg/spec_gate.py` (CI: `.github/workflows/chg-gate.yml`) enforcing
  E005 (`framework/VERSION` in diff) + E008 (`CHANGELOG.md` in diff). The plan
  satisfied both via Tasks 4–5 but never listed the gate. Verified at
  `tests/chg/spec_gate.py:85` + `.github/workflows/chg-gate.yml`. → Added V7,
  R7, Claim 21.
- **L2 — Claim 6 citation wrong + missed stricter guard.** Cited line 8 (a
  constant) instead of the test at :64, and omitted `test_no_orphan_governance_files`
  (:107). Conclusion (governance-scoped, layers unaffected) still holds. →
  Citation fixed; orphan guard noted.
- **M (verification accuracy) — `^framework/` hook exclude.** `.pre-commit-config.yaml:14`
  excludes `framework/` from ALL hooks, so markdownlint via the pre-commit
  wrapper SKIPS the spec doc. → D-PLANSTD-6 corrected (asymmetric enforcement);
  V6 now lints the spec doc directly.
- **M — spec-hygiene token list** was under-enumerated. → D-PLANSTD-3 now lists
  the exact patterns incl. bare-word `\bmcp\b` and literal `framework_version`.
- **M — D-PLANSTD-1 coherence.** The new standard is a *third* concept (markdown
  `plans/*.md`), not the README's YAML `tmp/` Temporary slot; the README
  cross-link is load-bearing. → D-PLANSTD-1 + Task 3 sharpened.
- **Minor citation nits** (Claim 5 line) fixed. All other claims (1–4, 7–20)
  verified by the reviewer as resolving and supported. Framework MINOR confirmed
  defensible against `GATE-SPEC_FRAMEWORK.md` + CHANGELOG precedent.

### Pass 3 — 2026-06-09 — self re-validation of Pass 2 patches

- Independently confirmed L1 (`tests/chg/spec_gate.py:85-88` appends E005/E008
  on missing `framework/VERSION`/`CHANGELOG.md`; `.github/workflows/chg-gate.yml`
  runs it) and the `^framework/` exclude (`.pre-commit-config.yaml:14`) before
  folding — not taken on the subagent's word.
- Re-read the patched sections: no new inconsistency introduced. V7 maps to R7;
  V6 split matches the exclude reality; D-PLANSTD-3/6 align with the verified
  hygiene + hook behavior.

### Pass 4 — 2026-06-09 — independent (fresh-context subagent, final)

- Second fresh-context adversarial pass swept the full `tests/conformance/`
  tree, every `.github/workflows/*.yml`, and re-verified all 22 Claim-ledger
  rows. Confirmed each triggered CI workflow is covered: `chg-gate.yml`
  (V7/R7), `conformance.yml` (V1), `pre-commit.yml` (V1/V6); and that
  `plugin.yml` (skill-count==52, forbidden-token grep), `hermes.yml`,
  `codeql.yml`, `doc-review.yml` are unaffected by a vendored doc-only addition.
- Only two non-load-bearing nits: Claim 12/13 citation lines off by 2–3 within
  the correct block. → Both corrected to README.md:40 and :22.
- **Result:** ready — independent pass returned zero load-bearing findings.

### Pass 5 — 2026-06-09 — decision resolution (D-PLANSTD-5)

- User clarified the versioning model: `framework/VERSION` is the framework's
  own spec-release stream, independent from per-template `metadata.schema_version`
  (verified pinned `"1.0"` across all layer templates), document-instance
  versions, and the platform **product** streams. Cross-checked against
  `docs/PROJECT.md` §2 (four independent streams) and `tests/chg/spec_gate.py`
  (E005 fires on any `framework/**` change, no exclusion).
- **D-PLANSTD-5 resolved:** bump `framework/VERSION` only; re-match the two
  `FRAMEWORK_SPEC_VERSION` pointers; leave plugin & Hermes product versions at
  current values; standard doc carries no internal version field. → Metadata
  `Version impact`, D-PLANSTD-5, and Task 4 updated. No load-bearing impact.
- **Result:** ready — no new findings; decision-only edit, all 22 citations
  still resolve.

### Pass 6 — 2026-06-09 — final decisions locked

- **Standard-doc filename locked:** `framework/layers/08_IPLAN/PLAN_STANDARD.md`
  (was provisional `UNIFIED_PLAN_STANDARD.md`); all 7 references updated.
- **Work-type set confirmed:** `feature` / `bugfix` / `documentation` /
  `refactor` / `chore` (D-PLANSTD-2).
- No open questions remain. **Result:** ready — no new findings; naming/decision
  edits only, all 22 citations still resolve.
