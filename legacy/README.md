# legacy/ — Frozen Pre-Migration Project

> Status: FROZEN. Do not develop here.

This directory holds the entire pre-migration project (`ucx_framework`
v0.20.4) as it existed before the multi-platform restructure began.

## Why it exists

The new project (`framework/` + `platforms/`) is built from scratch to avoid
overlap and confusion with the old tree. The old tree is retained here, intact,
because Phases 1–3 of the migration **extract and port content from it**
(layer definitions, governance rules, the Hermes engine, the `doc-*` skills).

See `../ROADMAP.md` and `../docs/REPO_STRUCTURE.md` for the legacy → target
mapping.

## Rules

- **Frozen.** No new development happens in `legacy/`.
- **Copy, don't move.** When the new project needs legacy content, copy it
  out and adapt it — leave the legacy copy untouched.
- **CI disabled.** The former GitHub Actions workflows are parked, inert, in
  `legacy/github-workflows-disabled/`.
- **Removal.** `legacy/` is deleted at or shortly after the Phase 5 cutover,
  once nothing in the new project depends on it.
