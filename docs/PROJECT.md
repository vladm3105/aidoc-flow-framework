# Project Management — AI Doc Flow Framework (Multi-Platform)

> Created 2026-05-18. Companion to `ROADMAP.md` and `docs/REPO_STRUCTURE.md`.

## 1. Overview

The project restructures the document-flow framework into one engine-agnostic
specification with two independent platforms:

| Platform | Engine | Source of truth |
|----------|--------|-----------------|
| A — Hermes AI | MCP server (`ucx_hermes`) | `platforms/hermes/` |
| B — Claude Code plugin | Native Claude Code (skills/agents/commands/hooks) | `platforms/claude-code-plugin/` |

Both implement the same `framework/` spec; they share no runtime code.

## 2. Versioning

Semantic Versioning ([semver.org](https://semver.org)). Four independent streams:

| Stream | File | Purpose |
|--------|------|---------|
| Project (migration) | `CHANGELOG.md` / `ROADMAP.md` | Tracks migration milestones only |
| Framework spec | `framework/VERSION` | The shared contract |
| Hermes AI | `platforms/hermes/VERSION` | Platform A releases |
| Claude Code plugin | `platforms/claude-code-plugin/VERSION` | Platform B releases |

Each platform declares the `framework_spec_version` it conforms to. A MAJOR
bump of the framework spec signals a potentially breaking contract change for
both platforms.

The migration project starts a fresh `0.x` line (it is a separate, independent
project from legacy `ucx_framework` v0.20.4). Cutover ships `v1.0.0`.

## 3. Branching & Tagging

- **Working branch:** `claude/multi-platform-migration-AamWB`. All migration
  work lands here.
- **Milestone tags:** each completed phase is tagged (`v0.1.0` … `v0.5.0`,
  then `v1.0.0` at cutover).
- **Cutover:** at Phase 5 the new project replaces `main`. Until then `main`
  remains the legacy `ucx_framework`.
- **`main` is protected (locked / read-only) for the duration of the
  migration.** No changes land on `main` until the Phase 5 cutover; all
  migration work happens on `claude/multi-platform-migration-AamWB`.
- Platforms tag their own releases independently once scaffolded.

### Tag namespaces

Each version stream (§2) tags independently, in its own namespace:

| Stream | Tag form | Example | Version source |
|--------|----------|---------|----------------|
| Project milestone | `vX.Y.Z` | `v0.2.0` | `ROADMAP.md` milestone table |
| Framework spec | `framework/vX.Y.Z` | `framework/v0.1.0` | `framework/VERSION` |
| Platform release | `<platform>/vX.Y.Z` | `hermes/v0.3.0` | `platforms/<name>/VERSION` |

`VERSION` files hold the bare SemVer (e.g. `0.1.0`); the tag adds the `v`
prefix and the stream namespace. Slash-namespaced refs let
`git tag -l 'framework/*'` filter a single stream and keep stream tags
visually distinct from project milestones.

The framework spec's first release tag (`framework/v0.1.0`) is created when
Phase 1 completes — i.e. once `framework/` is fully assembled — alongside the
`v0.2.0` project milestone tag.

## 4. Milestones

| Milestone | Phase | Tag | Definition of Done |
|-----------|-------|-----|--------------------|
| Planning baseline | 0 | `v0.1.0` | Roadmap, changelog, structure, platform dirs in place |
| Framework spec | 1 | `v0.2.0` | `framework/` populated; conformance suite defined |
| Hermes re-homed | 2 | `v0.3.0` | Hermes under `platforms/`; passes conformance |
| Plugin built | 3 | `v0.4.0` | Plugin built, Hermes-free; passes conformance |
| Independence | 4 | `v0.5.0` | Both platforms green; independent changelogs + CI |
| Cutover | 5 | `v1.0.0` | New project replaces `main`; legacy archived |

## 5. Conformance Model

The `framework/` spec is the contract. A shared suite under
`tests/conformance/` validates that a platform correctly implements the
8-layer SDD flow (BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN→Code), schemas,
templates, and traceability rules. Both platforms run the **same** suite —
this is what keeps two independent engines behaviourally equivalent.

## 6. Change Management

### During migration (Phases 0–5) — lightweight
The gated CHG process is **not** applied to migration work. Interim controls:

- Pull-request review on the working branch.
- Conventional commit messages.
- `CHANGELOG.md` updated per change.
- Significant decisions recorded as markdown ADRs in `docs/architecture/`.

### After cutover — CHG re-introduced
Post-migration, the gated CHG process returns in two roles:

1. **Process** — governing changes to the `framework/` spec. A spec change has
   two downstream consumers and real breaking-change risk; that is exactly the
   cross-layer, formal-gate scenario CHG exists for.
2. **Feature** — the CHG overlay ships inside `framework/governance/` as a
   capability both platforms expose to their end users.

Per-platform internal development continues under ordinary SemVer + changelog
+ PR review — the gated process is not applied to a platform's own commits.

### CHG implementation model (TODO — tracked as ROADMAP CHG-D1)

> Not built during migration. Recorded here to revisit post-Phase 5.

CHG is implemented as **skills + CI/CD**, split by responsibility:

- **Skills** — authoring (CHG document, impact assessment, cascading layer
  edits) and the *automatable* gate checks (schema validity, upstream tags,
  traceability, `GATE_APPROVAL_FORM` preparation, pass/fail gate report).
- **CI/CD** — runs the gate-validator skill on every PR as a required status
  check; blocks merge on failure.
- **Repo settings** — the *human* gate (e.g. C3 board sign-off) is enforced by
  GitHub branch protection / required reviewers. A skill prepares and verifies
  the approval form but is never the authority that grants approval.

Implemented twice against the same `framework/` spec — skills + CI workflow in
the Claude Code plugin, server-side in Hermes — validated by the shared
conformance suite.
