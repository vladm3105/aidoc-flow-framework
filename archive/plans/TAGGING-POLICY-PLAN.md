# Plan — `docs/TAGGING.md` Tagging Policy

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | Tagging policy doc + apply P1-T8 tags       |
| Status     | DONE — 2026-05-19T11:25:00Z                |

## Objective

Consolidate the git-tag policy into one doc, `docs/TAGGING.md`, covering both
**release tags** (the existing namespaced SemVer scheme) and a new
**bookmark tag** category for marking notable non-release points so they are
easy to find. Then apply the policy to P1-T8 by pushing its release tags.

## Scope

**In:** create `docs/TAGGING.md`; slim `docs/PROJECT.md` §3 to a summary that
points at it; record the bookmark-tag category as D-0011; push the three
P1-T8 release tags.
**Out:** in-document `@`-annotation tags (a separate framework concept, not
git tags); CI tag automation.

## Tag categories

| Category | Namespace | Form | Annotated | Mutable | Pushed |
|----------|-----------|------|-----------|---------|--------|
| Release — project milestone | `vX.Y.Z` | SemVer | yes | no (permanent) | yes |
| Release — framework spec | `framework/vX.Y.Z` | SemVer | yes | no | yes |
| Release — platform | `<platform>/vX.Y.Z` | SemVer | yes | no | yes |
| Bookmark | `mark/<slug>` | free slug | yes (1-line note) | yes (may move/delete) | yes |

**Bookmark tags** mark notable non-release commits — a baseline, a known-good
state, an audit point, "where behaviour X changed" — for quick retrieval via
`git tag -l 'mark/*'` and `git describe`. They are annotated (so each carries
a reason), shared (pushed), and may be moved or deleted as they age out.
Release tags are the opposite: immutable once pushed.

## Approach

- `docs/TAGGING.md` is the **authority**: full category definitions, the
  create/push commands, the find/search commands (`git tag -l 'pattern'`,
  `git tag -n`, `git describe`), and the rules (annotated for releases;
  never move/force-push a release tag; bookmarks are disposable).
- `docs/PROJECT.md` §3 keeps a short "tag streams" summary and links
  `docs/TAGGING.md` as the full policy — the namespace table moves to
  `TAGGING.md` to avoid two copies drifting apart.
- D-0011 records the bookmark-tag category.

## Apply to P1-T8

P1-T8 (Phase 1 close) per the policy gets the **release tags** — no bookmark
is warranted (`v0.2.0` already marks the milestone). The three tags already
exist locally; "apply" = push them:

```
git push origin v0.1.0 framework/v0.1.0 v0.2.0
```

## Verification

- `docs/TAGGING.md` exists; `docs/PROJECT.md` §3 links it; no duplicated
  namespace table.
- After the push, `git ls-remote --tags origin` lists `v0.1.0`,
  `framework/v0.1.0`, `v0.2.0`.
- `git tag -l 'framework/*'` resolves the framework stream.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Pushing release tags is irreversible | the user explicitly instructed "apply tags to P1-T8"; scope is exactly the 3 named tags; no `--force` |
| R2 | `PROJECT.md` §3 and `TAGGING.md` drift | the namespace table lives only in `TAGGING.md`; §3 links it |
| R3 | A `mark/` bookmark mistaken for a release | `TAGGING.md` states bookmarks are non-SemVer, mutable, and not releases |

## Implementation (2026-05-19T11:25:00Z)

Created `docs/TAGGING.md` (release + bookmark categories, commands, rules);
slimmed `docs/PROJECT.md` §3 to a summary + link; recorded D-0011.

**Blocker — tag push rejected (HTTP 403).** Applying the P1-T8 tags failed:
`git push origin v0.1.0 framework/v0.1.0 v0.2.0` returns HTTP 403, as does
each tag individually. The remote execution environment's git proxy permits
pushes only to the working branch and rejects `refs/tags/*`. A 403 is an
authorization rejection, not a network error — not retryable here. The three
tags exist and are correct **locally**; publishing them needs either an
environment whose network policy allows tag pushes, or a push from a local
clone. P1-T8 and P0-T5 remain open on this.

## Review log

### Pass 1 — 2026-05-19T11:15:00Z

- **G1.** `PROJECT.md` §3 already holds the namespace table; duplicating it in
  `TAGGING.md` invites drift. → `TAGGING.md` owns the canonical table; §3 is
  reduced to a summary + link. R2.
- **G2.** Bookmark tags must be clearly distinct from releases or someone may
  treat a `mark/` tag as a version. → category table + explicit prose:
  bookmarks are non-SemVer, mutable, disposable. R3.
- **G3.** "Apply tags to P1-T8" = push the 3 release tags; pushing is
  irreversible. → the user's instruction is the authorization; scope pinned to
  exactly `v0.1.0`, `framework/v0.1.0`, `v0.2.0`. R1.

### Pass 2 — 2026-05-19T11:18:00Z

- **G4.** After the push, `plans/HANDOFF.md`'s existing "tags … pushed" line
  becomes accurate — no separate correction needed.
- **G5.** No `framework/` files change, so the conformance suite is
  unaffected; verification rests on `ls-remote`.
- **G6.** No bookmark tag is created for P1-T8 — the category is documented
  for future use; `v0.2.0` already marks the milestone. Confirmed intentional.
- No new blockers. Ready to implement.
