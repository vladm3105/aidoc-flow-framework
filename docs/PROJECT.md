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

- **Development:** `main` is the multi-platform project (since the `v1.0.0`
  cutover). Work lands via short-lived `claude/*` feature branches → PR → `main`;
  the migration branch `claude/multi-platform-migration-AamWB` has been merged
  and deleted.
- **Milestone tags:** each migration phase was tagged (`v0.1.0` … `v0.5.0`,
  then `v1.0.0` at cutover); post-v1.0 releases tag from `main` (e.g. `v1.1.0`,
  `framework/v0.3.1`).
- **Cutover (done):** at Phase 5 the new project replaced `main`. The
  pre-migration `main` (legacy `ucx_framework`) is preserved on the protected,
  read-only branch **`legacy-ucx-v3.2-read-only`**, so the replacement was
  lossless.
- **Branch protection:** changes to `framework/**` require code-owner review
  plus the `Framework-spec change gate` status check — the human half of
  GATE-SPEC (§6).
- Platforms tag their own releases independently.

### Tag namespaces

Git tags use three release namespaces — project milestones `vX.Y.Z`,
framework spec `framework/vX.Y.Z`, and platforms `<platform>/vX.Y.Z` — plus a
`mark/<slug>` namespace for non-release bookmarks. `VERSION` files hold the
bare SemVer; the tag adds the `v` prefix and the namespace.

**See [`docs/TAGGING.md`](TAGGING.md) for the full tagging policy** — category
definitions, create / push / find commands, and the rules (annotated release
tags, never move a release tag, disposable bookmarks).

## 4. Milestones

| Milestone | Phase | Tag | Definition of Done |
|-----------|-------|-----|--------------------|
| Planning baseline | 0 | `v0.1.0` | Roadmap, changelog, structure, platform dirs in place |
| Framework spec | 1 | `v0.2.0` | `framework/` populated; conformance suite defined |
| Hermes re-homed | 2 | `v0.3.0` | Hermes under `platforms/`; passes conformance |
| Plugin built | 3 | `v0.4.0` | Plugin built, Hermes-free; passes conformance |
| Independence | 4 | `v0.5.0` | Both platforms green; independent changelogs + CI |
| Cutover | 5 | `v1.0.0` | New project replaces `main`; legacy archived as the `legacy-ucx-v3.2-read-only` branch |

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
- Significant decisions recorded in the decision log `plans/DECISIONS.md`;
  spec-affecting ones graduate to `framework/governance/DECISIONS.md`.

### After cutover — CHG re-introduced

Post-migration, the gated CHG process returns in two roles:

1. **Process** — governing changes to the `framework/` spec. A spec change has
   two downstream consumers and real breaking-change risk; that is exactly the
   cross-layer, formal-gate scenario CHG exists for.
2. **Feature** — the CHG overlay ships inside `framework/governance/` as a
   capability both platforms expose to their end users.

Per-platform internal development continues under ordinary SemVer + changelog

- PR review — the gated process is not applied to a platform's own commits.

### CHG implementation model (implemented — CHG-D1, D-0020)

CHG is implemented as **skills + CI/CD**, split by responsibility. The
spec-governance half landed first: **GATE-SPEC**, the *meta* gate governing
changes to the `framework/` spec itself (orthogonal to the artifact-cascade
gates) — see `framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md`.

- **Skills** — authoring (CHG document, impact assessment, cascading layer
  edits) and the *automatable* record-level checks. For GATE-SPEC: `gate-check`
  runs E001–E004 (provenance, `semver_impact` + major⇒C3, never-C1, C3 approval
  prep) and the `doc-chg` family routes `change_source: spec` to it.
- **CI/CD** — runs the automatable checks on every PR as a required status
  check. For GATE-SPEC: `tests/chg/spec_gate.py` enforces the diff-aware E005
  (VERSION bump) + E008 (CHANGELOG), and the conformance suite enforces E006
  (spec-version match) + E007 (suite green).
- **Repo settings** — the *human* gate (e.g. C3 board sign-off) is enforced by
  branch protection / required reviewers on `framework/**`. A skill prepares and
  verifies the approval form but is never the authority that grants approval.

Implemented twice against the same `framework/` spec — the Claude Code plugin
(skills + CI workflow) and Hermes (server-side `validation/chg_rules.py`) —
validated by the shared conformance suite. **CHG-D2** is done: the model is
recorded as **GD-01** in `framework/governance/DECISIONS.md`.

**Spec change → re-sync the plugin's vendored bundle.** The Claude Code plugin
ships a byte-identical copy of `framework/{layers,governance,registry}` (+ the
SDD guide) so it installs self-contained (D-0022). A spec change therefore has
one more obligation: run `bash tools/sync-plugin-framework.sh` to regenerate
`platforms/claude-code-plugin/framework/` and commit it in the same change. The
conformance drift-guard (`test_plugin_framework_bundle.py`) fails CI if the
bundle drifts from canonical — it is the backstop, not a surprise; the bundle is
a snapshot pinned to the plugin's `FRAMEWORK_SPEC_VERSION`.
