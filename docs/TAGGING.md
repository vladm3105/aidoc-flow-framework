# Tagging Policy

> The authoritative git-tag policy for the multi-platform project. `docs/PROJECT.md`
> §3 summarizes it; this document is the full reference.

Git tags are named pointers to specific commits. This project uses them in two
roles: **release tags** that permanently mark version milestones, and
**bookmark tags** that mark notable points for easy retrieval.

> Scope: this covers **git tags**. It is unrelated to the in-document
> `@`-annotations (`@brd`, `@diagram: c4-l1`, …) used inside `framework/`
> artifacts — those are a separate traceability mechanism.

## Tag categories

| Category | Namespace | Example | Annotated | Mutable | Pushed |
|----------|-----------|---------|-----------|---------|--------|
| Release — project milestone | `vX.Y.Z` | `v0.2.0` | yes | no — permanent | yes |
| Release — framework spec | `framework/vX.Y.Z` | `framework/v0.1.0` | yes | no — permanent | yes |
| Release — platform | `<platform>/vX.Y.Z` | `hermes/v0.3.0` | yes | no — permanent | yes |
| Bookmark | `mark/<slug>` | `mark/pre-cutover` | yes | yes — may move/delete | yes |

## 1. Release tags

Release tags mark a published version. Each of the three SemVer streams
(see `docs/PROJECT.md` §2) tags in its own namespace:

- **Project milestones** — `vX.Y.Z`. One per completed phase (`v0.1.0` …
  `v1.0.0`). Tracks the migration itself.
- **Framework spec** — `framework/vX.Y.Z`. The shared `framework/` contract.
  Version source: `framework/VERSION`.
- **Platforms** — `<platform>/vX.Y.Z` (`hermes/…`, `claude-code-plugin/…`).
  Version source: `platforms/<name>/VERSION`.

Rules:

- `VERSION` files hold the **bare** SemVer (`0.1.0`); the tag adds the `v`
  prefix and the namespace.
- Release tags are **annotated** (`git tag -a`) — they carry a tagger, date,
  and message.
- Release tags are **immutable** once pushed. Never move or force-push one;
  to correct a mistake, cut a new version.
- A release tag is created only on a commit whose conformance suite is green.

## 2. Bookmark tags

Bookmark tags mark a notable **non-release** commit so it is easy to find
later — a baseline, a known-good state, an audit reference point, the commit
where some behaviour changed, or a spot worth returning to.

- Namespace: `mark/<slug>` — a short, descriptive, lowercase-kebab slug
  (`mark/pre-cutover`, `mark/conformance-baseline`).
- Annotated, with a one-line note explaining why the commit is marked.
- **Mutable and disposable**: a bookmark may be moved to a newer commit or
  deleted once it has served its purpose. They are *not* versions and carry no
  SemVer meaning.
- Pushed, so the whole team shares them.

## Creating and pushing tags

```sh
# Release tag (annotated)
git tag -a v0.2.0 <commit> -m "Phase 1 — Framework Spec Extraction complete"
git tag -a framework/v0.1.0 <commit> -m "Framework spec v0.1.0 — first release"

# Bookmark tag (annotated)
git tag -a mark/conformance-baseline <commit> -m "First green conformance run"

# Tags do NOT travel with `git push`; push them explicitly
git push origin v0.2.0 framework/v0.1.0      # named tags

# Delete a bookmark that has aged out (local + remote)
git tag -d mark/old-bookmark
git push origin :refs/tags/mark/old-bookmark
```

Never `git push --force` a tag, and never `git push --tags` blindly — push
named tags so nothing unintended is published.

## Finding tags

```sh
git tag -l 'framework/*'     # one stream
git tag -l 'mark/*'          # all bookmarks
git tag -n                   # tags with their annotation messages
git describe --tags HEAD     # nearest tag + distance from HEAD
git log --oneline v0.1.0..v0.2.0   # commits between two tags
```

Slash-namespaced refs (`framework/v0.1.0`, `mark/<slug>`) are valid git tag
names and make `git tag -l '<prefix>/*'` an effective per-stream filter.

## Current tags

| Tag | Commit | Marks |
|-----|--------|-------|
| `v0.1.0` | Phase 0 baseline | Planning & scaffolding milestone |
| `v0.2.0` | Phase 1 close | Framework Spec Extraction milestone |
| `framework/v0.1.0` | Phase 1 close | Framework spec — first independent release |
| `v0.3.0` | Phase 2 close | Platform A: Hermes Re-homing milestone |
| `hermes/v0.1.0` | Phase 2 close | Hermes platform — first independent release |
| `v0.4.0` | Phase 3 close | Platform B: Claude Code plugin milestone |
| `claude-code-plugin/v0.1.0` | Phase 3 close | Claude Code plugin — first independent release |

> Phase 1 tags (`v0.1.0`, `v0.2.0`, `framework/v0.1.0`) are published
> on the remote. Phase 2 tags (`v0.3.0`, `hermes/v0.1.0`) and Phase 3
> tags (`v0.4.0`, `claude-code-plugin/v0.1.0`) are created locally on
> the in-container session at the respective close commits and need
> the same local-clone workaround established at P1-T8 — the
> in-container git proxy continues to refuse tag pushes with HTTP 403.
> See `plans/P2-T6-PLAN.md` §Approach.5 and `plans/P3-T5-PLAN.md`
> §Approach.5 for the exact local-clone commands.
> Verify any tag's publication via `git ls-remote --tags origin`.
