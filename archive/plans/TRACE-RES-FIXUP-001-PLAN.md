# TRACE-RES-FIXUP-001 Implementation Plan

> Follow-up to NECESSARY-UPSTREAM-001 + TDD-RT-001 — closes two bug classes
> (lint-rule downstream/self-tag handling + url-shortener corpus orphan-tag
> residue) and removes the temporary `SDD_LINT_SKIP_TRACE_RES=1` bypass that
> let TDD-RT-001 land.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | TRACE-RES-FIXUP-001                         |
| Type           | bugfix (lint-rule semantics + example-corpus regen + bypass removal) |
| Status         | READY-FOR-PR — converged at Pass 5 (Pass 1 patched 15:00; Pass 2 15:30; Pass 3 15:50; Pass 4 16:10; Pass 5 16:30) |
| Depends on     | NECESSARY-UPSTREAM-001 (merged PR #121); TDD-RT-001 (merged PR #122) |
| Blocks         | Future per-layer cascades against the url-shortener corpus running without bypass; IPLAN-RT-001 verification |
| Worktree       | `feat/trace-res-fixup-001` at `/opt/data/aidoc-flow/framework-trace-res-fixup-001/` |
| Version impact | Plugin PATCH `0.13.0 → 0.13.1` (lint-rule semantic fix in `sdd_doc_lint/__init__.py`). No `framework/` change — the example corpus regeneration replaces artifacts but does not change spec/registry/templates, so no GATE-SPEC trigger. |

## Problem statement

The TDD-RT-001 cascade aborted at Phase 0 lint-smoke with 107 `TRACE-RES-001`
errors. Diagnosis surfaced **two bug classes** (lint-rule semantics and
corpus state) that this plan ships fixes for, plus removes the temporary
bypass that let TDD-RT-001 land:

### Bug 1 — TRACE-RES-001 fires on downstream tags (lint rule bug)

The TRACE-RES-001 rule (NECESSARY-UPSTREAM-001 Task 4b) checks every emitted
`@<layer>: <ID>` tag for on-disk resolution. But the necessary-upstream
contract is about **upstream** lineage; downstream pointers like
`@tdd: TDD-01` emitted from SPEC-01 are informational forward references
that:

- May not exist yet during cascade (TDD-01 is generated AFTER SPEC-01)
- Are not part of the "necessary upstream" contract being enforced
- Are tooling pointers, not trace-lineage citations

Example (from the failed TDD-RT-001 cascade output):

```
examples/url-shortener/docs/06_SPEC/SPEC-01.md:295:
  [ERROR TRACE-RES-001] trace tag '@tdd: TDD-01' references unknown document
  (no corpus member has doc_id 'TDD-01')
```

SPEC-01 line 295 reads: `TDD document: @tdd: TDD-01` — explicitly a
downstream pointer. SPEC's `required_tags=[ears, bdd, adr]` does NOT include
TDD; the tag is informational, and the cascade is about to generate TDD-01.
The rule should not block here.

### Bug 2 — Pre-NECESSARY-UPSTREAM-001 corpora carry orphan @prd cumulative-trace tags

Existing url-shortener artifacts (BRD-01, EARS-01, BDD-01, ADR-01, SPEC-01)
were generated under the OLD cumulative-trace contract. They emit `@prd:`
tags (cumulative lineage) pointing at element IDs in a PRD-01.md that
never existed in the example corpus (the example was generated with the
PRD layer skipped or with no PRD layer authored).

Under the OLD lint, presence-only TAG01 didn't catch the orphan. Under the
NEW TRACE-RES-001 rule, every emitted upstream tag must resolve — these
orphan @prd tags fire.

Example (from cascade output):

```
examples/url-shortener/docs/05_ADR/ADR-01.md:321:
  [ERROR TRACE-RES-001] trace tag '@prd: PRD.01.13.7760' unresolvable
  (host document missing; expected host 'PRD-01')
```

ADR-01 line 321 is a cumulative-trace header line citing 6 `@prd:` element
IDs, all in a PRD-01.md that doesn't exist. Same pattern repeats across
BRD-01, EARS-01, BDD-01, SPEC-01.

This is corpus drift — the example pre-dates the new contract — and it's
**correctly diagnosed** by TRACE-RES-001 (the rule is doing its job).
The fix is to regenerate the corpus, not weaken the rule.

The NECESSARY-UPSTREAM-001 PR's "backwards compatibility" claim
(*"existing url-shortener artifacts remain valid under the new contract
(their declared tags still resolve)"*) was **wrong** for this corpus —
NECESSARY-UPSTREAM-001's Pass 4 cross-check verified the new rule against
`tools/sdd_doc_lint/fixtures/` but not against `examples/url-shortener/docs/`.
The check should have been extended to the example corpus during that
plan's Pass 4.

## Temporary bypass already in place

To unblock TDD-RT-001 cascade verification:

- `SDD_LINT_SKIP_TRACE_RES=1` env var added to `_check_trace_resolution` —
  disables the rule entirely when set. Used by the TDD-RT-001 cascade run
  to allow the cascade to proceed past Phase 0 lint-smoke and surface
  any **other** errors in the TDD-layer generation.
- Documented inline in the function's docstring with a back-reference to
  this plan.
- NOT to be relied on in production CI — purely a migration bridge until
  this plan ships.

## Fixes

### Fix 1 — Downstream-tag skip in TRACE-RES-001 (lint rule)

Modify `_check_trace_resolution` so that for each artifact being linted:

1. Derive the artifact's own layer-number from frontmatter `artifact_type`
   (fallback to `doc_id` prefix if `artifact_type` is missing).
2. Derive the artifact's own `doc_id` from frontmatter (e.g. `SPEC-01`).
3. For each emitted `@<layer>: <ID>` tag, derive the tag's layer-number
   from the layer prefix (e.g., `@tdd` → 7) and resolve the tag's host
   `doc_id` (already done by existing element-id derivation logic).
4. **Skip** the resolution check when:
   - `tag_layer_number > artifact_layer_number` (downstream pointer), OR
   - `tag_host_doc_id == artifact's own doc_id` (self-tag — exact doc match,
     not merely same-layer).
5. **Do not skip** when `tag_layer_number == artifact_layer_number` but the
   doc_id differs (sibling reference, e.g. SPEC-02 → `@spec: SPEC-01`).
   Sibling references are real upstream lineage within a layer and must
   resolve.
6. Keep all existing checks for upstream tags.

Test additions (`tests/unit/test_sdd_doc_lint_trace_resolution.py`):

- **Downstream-skip:** SPEC-01 emits `@tdd: TDD-01` (forward pointer)
  where TDD-01 doesn't exist in corpus → no TRACE-RES-001 finding.
- **Self-tag skip (exact doc_id):** SPEC-01 emits `@spec: SPEC-01`
  (its own doc id) → no finding.
- **Sibling reference NOT skipped:** SPEC-02 emits `@spec: SPEC-01`
  but SPEC-01 doesn't exist → TRACE-RES-001 fires (sibling reference is
  real upstream lineage within a layer; resolution still required).
- Existing cases (missing-doc, unknown-element, index-doc-skip) continue
  to pass.

### Fix 2 — Regenerate url-shortener example corpus

The url-shortener corpus has 5 downstream artifacts (BRD-01, EARS-01,
BDD-01, ADR-01, SPEC-01) that each emit orphan `@prd:` tags from the old
cumulative contract. No PRD-01.md exists. Strategy:

1. **One-shot bypass for the regen run only:** set
   `SDD_LINT_SKIP_TRACE_RES=1` for this single cascade invocation so
   Phase 0 lint-smoke passes against the legacy corpus and the cascade
   can run. Bypass is NOT committed; it's a one-time env-var setting on
   the invocation line.
2. **Cascade range:** `bash tests/scripts/test-acceptance.sh url-shortener
   --live --phase=cascade --from-layer=prd --to-layer=tdd` (default
   path (a) from Step 5 — extends regen through TDD for end-to-end
   consistency in one PR). This:
   - Reads existing BRD-01.md as upstream (BRD is NOT regenerated).
   - Generates a new PRD-01.md (currently missing from the corpus).
   - Regenerates EARS-01.md / BDD-01.md / ADR-01.md / SPEC-01.md / TDD-01.md
     under the new necessary-upstream contract (the
     post-NECESSARY-UPSTREAM-001 author SKILLs no longer emit cumulative
     `@brd:`/`@prd:` decoration above the per-layer required set).
   - Element IDs in the regenerated layers will differ from the
     pre-regen artifacts (content-hash-based), but every emitted tag
     will resolve within the regenerated corpus because the new SKILLs
     emit only what `required_tags` declares.
   - Wall-clock budget: up to 6 layers × 90 min per `SAGA-BUDGET-001`
     = ~9 hours worst case; typical per-layer cascade in this codebase
     converges in 60-80 min, so realistic ≈ 6-8 hours.
3. **Verify post-regen:** with bypass NOT set,
   `python3 -m sdd_doc_lint examples/url-shortener/docs/` returns 0
   `TRACE-RES-001` findings. Then run the harness in bootstrap-only mode
   (`bash tests/scripts/test-acceptance.sh url-shortener --bootstrap-only`)
   to confirm Phase 0 lint-smoke passes end-to-end without bypass.
4. **Commit the regenerated artifacts** as `examples/url-shortener/docs/`
   updates in this PR — they are framework-generated, not hand-edited,
   so they satisfy `[[feedback_never_hand_edit_example_artifacts]]`. The
   pre-regen artifacts are replaced; git history preserves their content
   for reference.
5. **Downstream consumers:** TDD-01.md (generated under TDD-RT-001) is
   left in place. Its `@bdd:` / `@ears:` / `@adr:` / `@spec:` references
   currently cite the pre-regen element IDs and will become orphan after
   the regen lands. Two options:
   - (a) Regenerate TDD-01 too — run
     `--from-layer=prd --to-layer=tdd` to extend the regen through TDD.
   - (b) Delete TDD-01.md and let IPLAN-RT-001 (the next task) re-author
     it under the regenerated upstream.
   Pick (a) for end-to-end consistency in one PR; pick (b) only if (a)
   shows convergence issues during impl. **Default: (a).**

### Fix 3 — Remove the temporary bypass

Once Fix 1 + Fix 2 land:

1. Delete the `SDD_LINT_SKIP_TRACE_RES` early-return from
   `_check_trace_resolution` in `tools/sdd_doc_lint/__init__.py`.
2. Update the docstring to drop the bypass mention.
3. Run `tools/sdd_doc_lint/sync-vendored.sh` so both vendored copies
   (`platforms/claude-code-plugin/sdd_doc_lint/` +
   `platforms/hermes/sdd_doc_lint/`) lose the bypass too.
4. Verify the harness `tests/scripts/test-acceptance.sh` does NOT have
   any `SDD_LINT_SKIP_TRACE_RES=1` invocation (sanity check — the
   bypass was only invoked at the cascade command line in this session,
   never embedded in the harness).

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `tools/sdd_doc_lint/__init__.py` | Add downstream-tag + self-tag skip to `_check_trace_resolution` (Fix 1); remove `SDD_LINT_SKIP_TRACE_RES` early-return (Fix 3) |
| `platforms/claude-code-plugin/sdd_doc_lint/__init__.py` | Vendored mirror — re-synced via `tools/sdd_doc_lint/sync-vendored.sh` |
| `platforms/hermes/sdd_doc_lint/__init__.py` | Same |
| `tests/unit/test_sdd_doc_lint_trace_resolution.py` | Add 3 cases: downstream-skip, self-tag skip, sibling-reference NOT skipped |
| `examples/url-shortener/docs/02_PRD/PRD-01.md` | **Created** by Fix 2 cascade regen |
| `examples/url-shortener/docs/03_EARS/EARS-01.md` | Regenerated |
| `examples/url-shortener/docs/04_BDD/BDD-01.md` | Regenerated |
| `examples/url-shortener/docs/05_ADR/ADR-01.md` | Regenerated |
| `examples/url-shortener/docs/06_SPEC/SPEC-01.md` | Regenerated |
| `examples/url-shortener/docs/07_TDD/TDD-01.md` | Regenerated (default path (a) — extends regen through TDD for end-to-end consistency) |
| `platforms/claude-code-plugin/VERSION` | `0.13.0 → 0.13.1` (PATCH — lint-rule semantic fix) |
| `CHANGELOG.md` | `[Unreleased]` entry: TRACE-RES-FIXUP-001 — describes Fix 1/2/3 |
| `docs/TAGGING.md` | New row `claude-code-plugin/v0.13.1` |
| `plans/HANDOFF.md` | Dated narrative — TRACE-RES-FIXUP-001 ships; IPLAN-RT-001 unblocked |

No `framework/**` change. The example corpus regeneration is data, not
spec. No GATE-SPEC trigger.

## Implementation sequence

### Task 1: Plan iterative review (≥ 2 cycles, mandatory, before PR)

- Pass 1 self-review against the codebase. Patch in place.
- Pass 2 re-review. Continue passes until one surfaces zero substantive
  gaps (MAJOR + MEDIUM). Past plans in this repo have typically taken
  4 cycles to converge; this plan needed 5 (the corpus-regen cleanup
  path required Pass 4 to catch the bogus `.aidoc/saga/` reference).

### Task 2: Implement Fix 1 (lint rule downstream/self-tag skip)

- Test-first: add the 3 new test cases to `tests/unit/test_sdd_doc_lint_trace_resolution.py`.
- Confirm the 2 new positive cases (downstream-skip + self-tag) FAIL and the
  1 sibling-NOT-skipped case still PASSES.
- Modify `_check_trace_resolution` per Fix 1 algorithm.
- Sync vendored copies via `tools/sdd_doc_lint/sync-vendored.sh`.
- Confirm all 3 new cases PASS + existing cases unchanged + conformance
  byte-identity holds.

### Task 3: Implement Fix 2 (regen url-shortener corpus)

- **Pre-cascade cleanup** (makes regen deterministic):

  ```sh
  rm -rf examples/url-shortener/docs/02_PRD/   # didn't exist; cleanup is a no-op
  rm -rf examples/url-shortener/docs/03_EARS/  # will be regenerated
  rm -rf examples/url-shortener/docs/04_BDD/   # will be regenerated
  rm -rf examples/url-shortener/docs/05_ADR/   # will be regenerated
  rm -rf examples/url-shortener/docs/06_SPEC/  # will be regenerated
  rm -rf examples/url-shortener/docs/07_TDD/   # will be regenerated
  rm -rf examples/url-shortener/.aidoc/review/ # per-layer saga + lens slots + verdicts
  rm -rf examples/url-shortener/.aidoc/audit/  # per-layer audit reports
  ```

  BRD-01.md is preserved (read-only as upstream). The saga state lives
  inside `.aidoc/review/<NN_LAYER>/<DOC_ID>/saga.json` (no separate
  `.aidoc/saga/` directory — confirmed by this plan's Pass 4 inspection);
  nuking `.aidoc/review/` wipes all saga + per-layer review state in
  one move.
  `.aidoc/audit/` holds the per-layer audit report markdown files;
  also cleared. `.aidoc/remediation/` is left in place (it holds
  per-document remediation history not affected by the regen).

  The cascade harness' overwrite semantics for existing target-layer
  docs is not explicitly documented (the saga driver simply invokes the
  autopilot, which may or may not refuse on pre-existing artifacts) —
  pre-cleaning sidesteps any uncertainty.
- One-shot env var: `SDD_LINT_SKIP_TRACE_RES=1 bash tests/scripts/test-acceptance.sh
  url-shortener --live --phase=cascade --from-layer=prd --to-layer=tdd`.
- Wait for cascade completion. 6 layers × `SAGA-BUDGET-001` 90 min/layer
  = ~9 hours worst case; typical convergence 60-80 min/layer = realistic
  6-8 hours.
- Verify regenerated artifacts: spot-check each layer's frontmatter +
  `@<layer>:` citations resolve in the regenerated corpus.

### Task 4: Implement Fix 3 (remove bypass)

- Delete the `SDD_LINT_SKIP_TRACE_RES` early-return from
  `tools/sdd_doc_lint/__init__.py`.
- Update docstring (remove bypass mention).
- Re-sync vendored copies.
- Verify with bypass NOT set: `python3 -m sdd_doc_lint examples/url-shortener/docs/`
  returns 0 findings.

### Task 5: Version + docs of record

- `platforms/claude-code-plugin/VERSION` `0.13.0 → 0.13.1`.
- Sync hook propagates plugin version. (No framework version bump.)
- `CHANGELOG.md`: prepend `[Unreleased]` entry describing all 3 fixes.
- `docs/TAGGING.md`: new row for `claude-code-plugin/v0.13.1`.
- `plans/HANDOFF.md`: dated narrative.

### Task 6: Conformance + lint + sanity cascade

- `python3 -m unittest discover -s tests/conformance` — 120/120 PASS.
- `python3 -m unittest discover -s tests/unit` — 40+ PASS (including 3 new).
- `python3 -m sdd_doc_lint examples/url-shortener/docs/` — 0 findings.
- `bash tests/scripts/test-acceptance.sh url-shortener --bootstrap-only`
  — Phase 0 lint-smoke passes with NO bypass set.

### Task 7: Open PR (only after Tasks 1-6 all green)

## Out of scope

- AUTO-REMEDIATE-001 extension to handle TRACE-RES-001 — speculative;
  Fix 1 + Fix 2 + cascade-driven regen should be sufficient.
- Adding a `--skip-lint-smoke` flag to the harness — speculative; once
  Fix 2 lands, the corpus passes lint-smoke and the bypass is unneeded.
- Full Hermes parity catch-up — plugin-first; tracked in `plans/HERMES-BACKLOG.md`.
  (Note: this PR does sync the vendored `platforms/hermes/sdd_doc_lint/`
  copy as part of Fix 3 — that's byte-identity vendoring, not feature
  parity work.)

## Verification

| #  | Check | Expected |
| -- | ----- | -------- |
| 1 | Unit `test_sdd_doc_lint_trace_resolution.py` (extended from 4 → 7 cases) | PASS — 3 new cases (downstream-skip, self-tag skip, sibling-not-skipped) added alongside existing 4 cases (clean corpus, missing doc, unknown element, index-doc skip) |
| 2 | Unit `test_lint.py` valid fixtures | PASS — no regression |
| 3 | Conformance `test_layer_registry_necessary_upstream` | PASS — registry shape unchanged |
| 4 | `python3 -m sdd_doc_lint examples/url-shortener/docs/` (post-regen, NO bypass) | 0 findings — corpus self-consistent under the new contract |
| 5 | `bash tests/scripts/test-acceptance.sh url-shortener --bootstrap-only` (NO bypass) | Phase 0 lint-smoke passes end-to-end |
| 6 | Conformance suite | 120/120 PASS (1 skipped) |
| 7 | `tools/sdd_doc_lint/__init__.py` grep `SDD_LINT_SKIP_TRACE_RES` | 0 hits (bypass removed) |

## Risks & rollback

| Risk | Mitigation |
| ---- | ---------- |
| Cascade regen takes 3-4 hours and the saga may not converge on every layer | Per the SAGA-BUDGET-001 contract each per-layer cascade has a 5400s budget; even with PARTIAL_TIMEOUT the regenerated artifact replaces the old one. If a layer fails to converge (`combined_status: FAIL`), commit it anyway as "best-effort regen" and queue cleanup in `IPLAN-RT-001` or a follow-up. Lint resolution is the gating criterion here, not the per-layer audit score. |
| Element-ID drift breaks downstream references in TDD-01 (if regen stops at SPEC, TDD-01's existing `@adr:`/`@spec:`/`@bdd:` ids become orphan) | Default to path (a) in Fix 2 — extend regen through `--to-layer=tdd`. If that proves too long/fragile, fall back to path (b) (delete TDD-01.md; let IPLAN-RT-001 author it under the regenerated upstream). |
| Pre-regen artifacts had useful test-fixture content that the regen may not reproduce | The corpus is a synthetic walkthrough, not a canonical content store. Regenerated artifacts under the new contract are MORE useful as fixtures (they exercise the contract that's now active). |

**Rollback:** Single PR. `git revert <merge-sha>` restores both the lint
rule + the corpus. The temporary `SDD_LINT_SKIP_TRACE_RES=1` bypass on
main is unaffected by a revert and remains as the emergency scaffold.

## Notes

- The bypass `SDD_LINT_SKIP_TRACE_RES=1` is a temporary scaffold. CI must
  never set it on protected branches; the in-code docstring already warns
  against this. No separate CONTRIBUTING.md note needed — once this PR
  lands, the bypass is gone and the constraint becomes moot.
- Pass 1 narrowed the original scope: there's no "Bug 3" (stray
  `@brd:` in TDD-01) — the cascade-produced TDD-01.md §1 line 30 reads
  `@ears | @bdd | @adr | @spec` with no `@brd:`/`@prd:`, so the
  necessary-upstream contract is correctly followed at the author side.
  The auditor's "C4 cumulative-tag header" P2 finding from the TDD
  cascade was about inter-section consistency, not orphan tags.
- This plan ships Fixes 1 + 2 + 3 atomically. Splitting would leave the
  corpus in a half-migrated state for an indeterminate window.

## Review log

> Per CLAUDE.md §"Development workflow" item 2: ≥ 2 review cycles BEFORE
> PR. Each = *review → patch → re-review*. Continue until a pass surfaces
> zero substantive gaps.

### Pass 0 — initial draft

- **Date:** 2026-06-10T13:30:00Z
- **Drafted under:** TDD-RT-001 cascade work (filed alongside the
  failed cascade output as a quick follow-up plan).
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-10T15:00:00Z
- **Method:** cross-check every claim against post-NECESSARY-UPSTREAM-001 +
  post-TDD-RT-001 main (commit `1d2f0938`). Verify each of the 7 author
  SKILLs is clean of cumulative-tag instructions; inspect cascade-produced
  TDD-01.md to verify Bug 3's evidence; inspect cascade harness behavior
  for `--from-layer` semantics.
- **Findings (12 gaps — 3 MAJOR / 5 MEDIUM / 4 MINOR):**
  - **G1 (MAJOR):** Bug 3 claim (TDD-01 emits stray `@brd:`) is WRONG.
    Cross-check showed TDD-01 §1 line 30 reads `@ears | @bdd | @adr |
    @spec` — necessary-upstream contract correctly followed. The
    auditor C4 finding I cited was about inter-section consistency, not
    orphan tags. *Patch:* Bug 3 dropped from the plan; Notes section
    explains the false alarm.
  - **G2 (MAJOR):** Fix 1 algorithm wrongly skipped ALL same-layer tags
    (including sibling references like SPEC-02 → @spec: SPEC-01).
    *Patch:* Refined — skip only when `tag_host_doc_id == artifact's
    own doc_id` (exact match), not by layer-equality. Sibling references
    still resolve. New test case "sibling-NOT-skipped" added.
  - **G3 (MAJOR):** Fix 2 cascade strategy was underspecified.
    Element-IDs are content-hash-based so regenerating PRD doesn't
    preserve the orphan IDs cited in existing artifacts. *Patch:* Spec
    expanded — full regen `--from-layer=prd --to-layer=tdd` replaces
    EARS/BDD/ADR/SPEC/TDD entirely under the new contract; one-shot
    env-var bypass for the regen invocation only (not committed); two
    alternate paths (a)/(b) for TDD-01 with default (a).
  - **G4 (MEDIUM):** Version impact "TBD". *Patch:* Plugin PATCH
    `0.13.0 → 0.13.1`; no framework change.
  - **G5 (MEDIUM):** Blocks/Depends-on field stale (TDD-RT-001 already
    shipped). *Patch:* Reworded — depends on merged PRs; blocks future
    cascades + IPLAN-RT-001.
  - **G6 (MEDIUM):** No File structure section. *Patch:* Added —
    lint module + 3 vendored copies + tests + 6 regenerated example
    artifacts + 1 new PRD-01.md + VERSION + CHANGELOG/TAGGING/HANDOFF.
  - **G7 (MEDIUM):** No Implementation sequence (Tasks). *Patch:* Added
    7-task sequence with two-cycle review as Task 1.
  - **G8 (MEDIUM):** No Review log. *Patch:* Added.
  - **G9 (MINOR):** Header blurb said "two fixes". *Patch:* Reworded
    to "two bug classes + bypass removal".
  - **G10 (MINOR):** Verification row 5 referenced TDD-RT-001 cascade
    re-run. *Patch:* Reworded to fresh harness bootstrap check (NO
    bypass) + sdd_doc_lint scan returning 0.
  - **G11 (MINOR):** CONTRIBUTING.md update mentioned in Notes but not
    actionable. *Patch:* Note rewritten — once bypass is removed, the
    constraint is moot; no CONTRIBUTING.md change needed.
  - **G12 (MINOR):** Type field needs update. *Patch:* "bugfix (lint-rule
    semantics + example-corpus regen + bypass removal)".
- **Worktree:** moved from a quick filing under `feat/tdd-rt-001` to a
  dedicated worktree `feat/trace-res-fixup-001` (added to metadata).
- **Net structural change:** scope unchanged (still 3 fixes); ~80 lines of
  new sections (File structure + Tasks + Risks + Review log).
- **Status:** SUPERSEDED by Pass 2.

### Pass 2 — re-review

- **Date:** 2026-06-10T15:30:00Z
- **Method:** re-read patched plan top-to-bottom; cross-check Pass 1
  patches for self-consistency + against codebase realities (SAGA-BUDGET-001
  per-layer budget, harness verification modes, scope of vendored sync).
- **Findings (6 substantive gaps — 2 MAJOR, 2 MEDIUM, 2 MINOR):**
  - **P2-1 (MAJOR):** Fix 2 Step 2 said `--from-layer=prd --to-layer=spec`
    while Step 5 default + Task 3 said `--to-layer=tdd`. Self-inconsistency
    introduced by Pass 1 G3 patch.
    *Patch:* Step 2 now explicitly uses `--to-layer=tdd` (default path (a))
    and cross-references Step 5.
  - **P2-2 (MAJOR):** Modified table listed
    `examples/url-shortener/docs/01_BRD/BRD-01.md` as "Regenerated", but
    Fix 2 Step 2 explicitly says BRD-01 is read as upstream (NOT
    regenerated — cascade starts at PRD).
    *Patch:* BRD-01 row removed from Modified.
  - **P2-3 (MEDIUM):** Cascade runtime estimate "~3-4 hours" inconsistent
    with `SAGA-BUDGET-001` (5400s = 90 min/layer × 6 layers = 9 hours
    worst case).
    *Patch:* Reworded to "up to 9 hours worst case; typical 6-8 hours"
    in both Fix 2 Step 2 and Task 3.
  - **P2-4 (MEDIUM):** Two different verification approaches for
    "lint-smoke passes without bypass" — Fix 2 Step 3 used a per-layer
    cascade probe; Task 6 used `--bootstrap-only`. The bootstrap-only
    mode is faster, lower-cost, and sufficient.
    *Patch:* Fix 2 Step 3 aligned to use `--bootstrap-only` like Task 6.
  - **P2-5 (MINOR):** "3 new test cases" wording unclear about
    relationship to existing tests.
    *Patch:* Verification row 1 now clarifies "extended from 4 → 7 cases"
    with both old and new cases named.
  - **P2-6 (MINOR):** Out-of-scope said "Hermes mirror catch-up" but
    Fix 3 does sync the vendored Hermes lint copy. Confusing.
    *Patch:* Clarified — full Hermes parity is deferred; byte-identity
    vendor sync of the lint module IS in scope (part of Fix 3).
- **Net structural change:** zero new tasks, zero new file deltas. Six
  in-place clarifications.
- **Status:** SUPERSEDED by Pass 3.

### Pass 3 — re-review

- **Date:** 2026-06-10T15:50:00Z
- **Method:** re-read patched plan; cross-check (a) test file path on
  current main, (b) current conformance counts, (c) cascade harness
  overwrite semantics for re-running over existing target-layer artifacts.
- **Findings (3 substantive — 0 MAJOR, 1 MEDIUM, 2 MINOR):**
  - **P3-1 (MEDIUM):** Cascade overwrite behavior for existing
    target-layer artifacts not explicitly documented in the harness; the
    saga driver delegates to the autopilot which may or may not refuse on
    pre-existing files. Pass 2 spec assumed clean overwrite.
    *Patch:* Task 3 now starts with an explicit pre-cascade cleanup step
    (`rm -rf` the to-be-regenerated layer dirs + `.aidoc/saga/` +
    `.aidoc/review/`). Makes the regen deterministic and matches the
    pattern already used in this codebase before re-running cascades.
    BRD-01.md is preserved (read-only as upstream).
  - **P3-2 (MINOR):** Status field stamped only Pass 1; missing Pass 2 +
    Pass 3 stamps.
    *Patch:* Now reads "(Pass 1 patched 15:00; Pass 2 patched 15:30;
    Pass 3 patched 15:50)".
  - **P3-3 (MINOR):** Problem statement intro said "two distinct bugs"
    while the blockquote header (Pass 1 patch) had been updated to
    "two bug classes + bypass removal". Mild self-inconsistency.
    *Patch:* Intro reworded to "two bug classes ... plus removes the
    temporary bypass".
- **Cross-checks that came back clean (no patches needed):**
  - `tests/unit/test_sdd_doc_lint_trace_resolution.py` exists on main ✓
  - Current conformance: 120/120 + 40/40 (1 skip each) ✓ matches plan claim
  - Test count math: existing 4 + 3 new = 7 ✓ matches Pass 2 verification row 1
  - `examples/url-shortener/.aidoc/profile.yaml` `active_layers` commented
    out — all 8 layers active by default ✓
- **Net structural change:** Task 3 gained a pre-cascade cleanup step
  (~10 lines of shell). No new tasks, no new file deltas in the Modified
  table. Status + Problem-statement intro tightened.
- **Status:** SUPERSEDED by Pass 4.

### Pass 4 — re-review

- **Date:** 2026-06-10T16:10:00Z
- **Method:** verify Pass 3 cleanup-step paths against actual `.aidoc/`
  layout; resolve any remaining ambiguous cross-references.
- **Findings (2 — 1 MAJOR, 1 MINOR):**
  - **P4-1 (MAJOR):** Pass 3 cleanup step referenced
    `examples/url-shortener/.aidoc/saga/` — that directory does NOT
    exist. The saga state actually lives inside
    `.aidoc/review/<NN_LAYER>/<DOC_ID>/saga.json` per the per-document
    blackboard contract from REVIEW_TEAM.md.
    *Patch:* Cleanup commands corrected — drop the bogus
    `rm -rf .aidoc/saga/`; nuking `.aidoc/review/` covers all per-layer
    saga + lens slots + verdicts. Also added explicit
    `rm -rf .aidoc/audit/` (per-layer audit reports). `.aidoc/remediation/`
    left in place (per-document remediation history; not affected).
  - **P4-2 (MINOR):** "Pass 4 cross-check" in Problem statement was
    ambiguous — could refer to this plan's Pass 4 OR
    NECESSARY-UPSTREAM-001's Pass 4 (which actually missed the example
    corpus).
    *Patch:* Disambiguated to "NECESSARY-UPSTREAM-001's Pass 4".
- **Cross-checks that came back clean:**
  - 6 cleanup dir paths verified: `02_PRD` absent (cleanup is no-op);
    `03_EARS / 04_BDD / 05_ADR / 06_SPEC / 07_TDD` all exist (cleanup
    is meaningful).
  - No remaining `TBD` / `TODO` / `FIXME` placeholders (the one
    "TBD" hit at line 381 is in a Pass 1 review-log entry quoting the
    original gap text — historical, expected).
  - Internal Pass-N cross-references are now consistent across the
    review log.
- **Net structural change:** corrected ~12 lines of cleanup shell;
  disambiguated 1 paragraph in Problem statement.
- **Status:** SUPERSEDED by Pass 5.

### Pass 5 — convergence pass

- **Date:** 2026-06-10T16:30:00Z
- **Method:** verify Pass 4 cleanup-path patches against actual layout;
  scan for any remaining stale self-references; confirm task structure
  is coherent end-to-end.
- **Findings (2 MINOR/cosmetic — 0 MAJOR, 0 MEDIUM):**
  - **P5-1 (MINOR):** Task 1 title said "Plan two-cycle review" — but the
    plan has actually taken 5 cycles to converge. The "two-cycle" minimum
    from CLAUDE.md is a floor, not the realized count.
    *Patch:* Title reworded to "Plan iterative review (≥ 2 cycles)";
    body adds that past plans typically take 4 cycles and this one took
    5 (Pass 4 caught the `.aidoc/saga/` bug).
  - **P5-2 (MINOR):** Task 3 cleanup commentary referenced "Pass 4
    inspection" without specifying which plan's Pass 4 (this plan's vs
    NECESSARY-UPSTREAM-001's).
    *Patch:* Disambiguated to "this plan's Pass 4 inspection".
- **Cross-checks that came back clean:**
  - All 6 docs/ cleanup paths verified against actual filesystem.
  - All 2 .aidoc/ cleanup paths verified (`review/` + `audit/` both exist;
    `remediation/` left in place).
  - Modified table aligns with cleanup list (BRD-01.md NOT regenerated;
    PRD-01.md created; EARS/BDD/ADR/SPEC/TDD regenerated; matches the
    cleanup scope).
  - Test file path `tests/unit/test_sdd_doc_lint_trace_resolution.py`
    confirmed on main; test execution pattern uses `PYTHONPATH=
    plugin_bundle_root()` per existing test convention.
  - No remaining placeholder strings (`TBD`/`TODO`/`FIXME`/`XXX`); the
    sole "TBD" hit at line 381 is historical text inside a Pass 1
    review-log entry quoting the original gap (expected, not a defect).
  - Internal Pass-N cross-references are all consistent.
  - Bug-Fix-Task numbering coherent: Bug 1 → Fix 1 → Task 2; Bug 2 → Fix 2
    → Task 3; Fix 3 → Task 4 (bypass removal); Tasks 5/6/7 = version +
    verification + PR.
- **Net structural change:** 2 line-level cosmetic edits; status field
  promoted to `READY-FOR-PR`.
- **Verdict: CONVERGENCE.** Zero MAJOR or MEDIUM gaps remain. Plan is
  ready for impl PR per CLAUDE.md §"Development workflow" item 2.

### Pass 6 — sanity check (optional)

Not required under the convergence rule (≥ 2 cycles + zero substantive
gaps). Pass 5 may have introduced inconsistencies in its two MINOR edits;
a Pass 6 sanity pass over those specific changes would close the loop
formally but is unlikely to surface anything actionable.
