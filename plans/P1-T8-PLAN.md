# P1-T8 Plan — Phase 1 Close: Release Tags

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T8                                      |
| Depends on | P1-T1…T7 complete; `framework/` assembled  |
| Status     | BLOCKED — 2026-05-19T11:35:00Z (tag push) |
| Closes     | Phase 1; also completes P0-T5              |

## Objective

Close Phase 1: cut the project changelog, mark the milestone, and create the
release tags — the framework spec's first independent tag (`framework/v0.1.0`)
and the Phase 1 project milestone (`v0.2.0`).

## Pre-existing state

- `v0.1.0` **already exists** — an annotated tag on `d986694`
  ("docs: plan multi-platform restructure (Phase 0 baseline)"), annotation
  "Phase 0 — planning baseline …". It is **not pushed** (`git ls-remote
  --tags origin` is empty). It is correct as-is — do not recreate or move it.
- No other tags exist locally or on the remote.

## Scope

**In:** changelog cut; ROADMAP/tracker updates; create `framework/v0.1.0` +
`v0.2.0` annotated tags; push the branch and all three tags.
**Out:** any change to `main`; a separate `framework/CHANGELOG.md` (first
release — the project changelog covers it; revisit if the spec iterates).

## Approach

### Tags (all annotated)

| Tag | Commit | Status | Message |
|-----|--------|--------|---------|
| `v0.1.0` | `d986694` | exists — push only | (unchanged) |
| `framework/v0.1.0` | Phase 1 close commit | create + push | `Framework spec v0.1.0 — first independent release` |
| `v0.2.0` | Phase 1 close commit | create + push | `Phase 1 — Framework Spec Extraction complete` |

`framework/v0.1.0` and `v0.2.0` point at the **Phase 1 close commit** (the
commit made in step 2 below), so the tagged tree includes the changelog cut.
`v0.1.0` stays on `d986694`.

### Changelog cut

In `CHANGELOG.md`, convert `## [Unreleased]` to `## [0.2.0] — 2026-05-19`
(project milestone) and open a fresh empty `## [Unreleased]` above it.

## Step sequence

1. Verify the conformance suite is green (don't tag a broken spec).
2. Commit "docs: close Phase 1 — release v0.2.0": changelog cut, ROADMAP
   status (Phase 1 done → Phase 2 next), `MIGRATION_TODO.md` (P1-T8 + P0-T5
   ticked), `HANDOFF.md`, this plan's status.
3. Push the branch.
4. Create the two annotated tags on the close commit.
5. **Confirm the exact tag set + commands with the user, then** push all
   three tags (`v0.1.0`, `framework/v0.1.0`, `v0.2.0`).
6. Verify tags landed on the remote.

## Verification

- `python3 -m unittest discover -s tests/conformance` → all 25 pass
  (pre-tag gate).
- `git ls-remote --tags origin` shows `v0.1.0`, `framework/v0.1.0`, `v0.2.0`
  after the push.
- `git tag -l 'framework/*'` lists `framework/v0.1.0` (namespace filter works).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Pushed tags are effectively irreversible / remote-visible | explicit user confirmation of the exact tag set before `git push` (step 5); annotated tags; never `--force` |
| R2 | Tagging a broken spec | suite-green gate before tagging (step 1) |
| R3 | Tag points at a commit not yet on the remote | push the branch (step 3) before pushing tags (step 5) |
| R4 | `v0.2.0` on the remote with no `v0.1.0` — incoherent sequence | push the pre-existing `v0.1.0` too (completes P0-T5) |
| R5 | Slash ref `framework/v0.1.0` mishandled | D-0009 convention; `git tag -l 'framework/*'` verified post-push |

## Implementation (2026-05-19T10:40:00Z)

**Finding F1 — changelog cut is a milestone split, not a rename.** The plan
assumed `[Unreleased]` → `[0.2.0]`. In fact `[Unreleased]` had never been cut,
so it bundled Phase 0 *and* Phase 1 content. Cutting it all to `[0.2.0]` would
mislabel the Phase 0 planning baseline. Resolved by splitting into `[0.1.0]`
(Phase 0 — planning & scaffolding) and `[0.2.0]` (Phase 1 — framework spec
extraction), partitioned per the `docs/PROJECT.md` §4 milestone table.

**Finding F2 — tag push blocked (HTTP 403). TASK NOT COMPLETE.** Steps 1–4
are done: suite verified green, the Phase 1 close commit landed and was
pushed, and all three annotated tags were created locally. Step 5 (push the
tags) fails — `git push origin <tag>` returns HTTP 403 for every tag. The
remote execution environment's git proxy allows pushes only to the working
branch and rejects `refs/tags/*`; a 403 is an authorization rejection, not a
retryable network error. The tags are created and correct locally; P1-T8
cannot close until they are published from an environment whose network
policy permits tag pushes (or from a local clone).

## Review log

### Pass 1 — 2026-05-19T10:25:00Z

- **G1.** `v0.1.0` exists locally but is unpushed; tagging `v0.2.0` alone would
  leave an incoherent remote sequence. → Push `v0.1.0` as part of P1-T8; this
  also completes P0-T5. R4; tracker ticks both.
- **G2.** Tags must point at the Phase 1 close commit (after the changelog
  cut), not raw `f131a6f`, so the tagged tree carries the `[0.2.0]` section. →
  Step order: commit first, then tag.
- **G3.** Release tags must be annotated (`-a`, dated, messaged), not
  lightweight. → Specified in the tag table.
- **G4.** A release without a changelog cut leaves `[Unreleased]` stale. →
  Cut `[Unreleased]` → `[0.2.0]`, reopen empty `[Unreleased]`.
- **G5.** Pushing tags is remote and effectively irreversible. → Explicit
  user confirmation of the exact tag set and commands before step 5; no
  `--force`. R1.

### Pass 2 — 2026-05-19T10:30:00Z

Cross-checked Verification, scope, and ordering:

- **G6.** Verification includes the suite-green pre-tag gate (R2) and a
  post-push `ls-remote` check — covers both "is the spec sound" and "did the
  push land". No false positive/negative.
- **G7.** Push ordering confirmed: branch (step 3) before tags (step 5), so
  every tagged commit already exists on the remote (R3).
- **G8.** `v0.1.0` annotation and target commit (`d986694`) were inspected and
  are correct — P1-T8 only *pushes* it, never recreates/moves it (moving an
  existing tag would be the kind of destructive rewrite to avoid).
- **G9.** `framework/CHANGELOG.md` deliberately out of scope — `0.1.0` is the
  spec's first release with nothing to diff against; the project changelog
  records it. Noted for when the spec next iterates.
- No new blockers. Ready to implement; step 5 gated on user confirmation.
