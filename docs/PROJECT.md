# Project Management — AI Doc Flow Framework (Multi-Platform)

> **History record (CHG-08 #670):** this document managed the archived
> multi-platform migration project (Hermes + Claude Code plugin, cutover
> `v1.0.0`). Values, branches, and pins inside are frozen at the 0.53.x era —
> read them as history, not live instruction. Live project state: repo
> `README.md` + `CHANGELOG.md`; live spec: `framework/`; live process:
> `AGENTS.md`.
>
> Created 2026-05-18. Companion to `docs/REPO_STRUCTURE.md` (`ROADMAP.md` was
> retired; the historical companion reference is kept as history).

## 1. Overview

The project restructures the document-flow framework into one engine-agnostic
specification with two independent platforms:

| Platform | Engine | Source of truth |
|----------|--------|-----------------|
| A — Hermes AI | MCP server (`ucx_hermes`) | retired with the 2026-09-07 archive; code removed |
| B — Claude Code plugin | Native Claude Code (skills/agents/commands/hooks) | retired with the 2026-09-07 archive; code removed |

Both implemented the same `framework/` spec; they shared no runtime code. No
live platform code remains — the framework is the whole product.

## 2. Versioning

Semantic Versioning ([semver.org](https://semver.org)). Four independent streams:

| Stream | File | Purpose |
|--------|------|---------|
| Project (migration) | `CHANGELOG.md` (`ROADMAP.md` retired) | Tracks migration milestones only |
| Framework spec | `framework/VERSION` | The shared contract |
| Hermes AI | retired | Platform stream frozen at the 2026-09-07 archive |
| Claude Code plugin | retired | Platform stream frozen at the 2026-09-07 archive |

Each consumer declares the spec version it conforms to. A MAJOR
bump of the framework spec signals a potentially breaking contract change for
all consumers.

The migration project starts a fresh `0.x` line (it is a separate, independent
project from legacy `ucx_framework` v0.20.4). Cutover ships `v1.0.0`.

## 3. Branching & Tagging

> **Superseded (CHG-24 #802):** the live branching model is `AGENTS.md`
> (`feature/*` → `dev` → `main`). Everything below is the frozen
> migration-era record — read as history, not instruction.

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
- Platforms tagged their own releases independently (frozen at the 2026-09-07 archive).

### Tag namespaces

Git tags use two live release namespaces — project milestones `vX.Y.Z` and
framework spec `framework/vX.Y.Z` — plus a `mark/<slug>` namespace for
non-release bookmarks (the `<platform>/vX.Y.Z` namespace is frozen history).
`VERSION` files hold the bare SemVer; the tag adds the `v` prefix and the namespace.

**See [`docs/TAGGING.md`](TAGGING.md) for the full tagging policy** — category
definitions, create / push / find commands, and the rules (annotated release
tags, never move a release tag, disposable bookmarks).

## 4. Milestones

| Milestone | Phase | Tag | Definition of Done |
|-----------|-------|-----|--------------------|
| Planning baseline | 0 | `v0.1.0` | Roadmap, changelog, structure, platform dirs in place |
| Framework spec | 1 | `v0.2.0` | `framework/` populated; conformance suite defined |
| Hermes re-homed | 2 | `v0.3.0` | Hermes under `archive/platforms/`; passes conformance |
| Plugin built | 3 | `v0.4.0` | Plugin built, Hermes-free; passes conformance |
| Independence | 4 | `v0.5.0` | Both platforms green; independent changelogs + CI |
| Cutover | 5 | `v1.0.0` | New project replaces `main`; legacy archived as the `legacy-ucx-v3.2-read-only` branch |

## 5. Conformance Model

The `framework/` spec is the contract. A shared suite under
`tests/conformance/` validates that a platform correctly implements the
10-layer SDD flow (BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN→Code→EVAL→Verified), schemas,
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
   downstream consumers and real breaking-change risk; that is exactly the
   cross-layer, formal-gate scenario CHG exists for.
2. **Feature** — the CHG overlay ships inside `framework/governance/` as a
   capability consumers expose to their end users.

Consumer-internal development continues under ordinary SemVer + changelog; PR review applies, the gated process is not.

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

**Historical: the plugin's vendored bundle.** The Claude Code plugin used to ship
a byte-identical copy of `framework/{layers,governance,registry}` (+ the
SDD guide) so it installed self-contained (D-0022), and a spec change carried
one more obligation: regenerating `archive/platforms/claude-code-plugin/framework/`
via `archive/tools/sync-plugin-framework.sh` in the same change, backstopped by
the `test_plugin_framework_bundle.py` drift-guard. That bundle, script, and guard
were retired with the 2026-09-07 platform archive — no re-sync obligation remains.

## 7. Project Integration — Consuming the Framework

Projects consume the framework by cloning it into their `.aidoc/framework/` directory. This section defines the integration contract.

### 7.1 Consumer copy (allowlist)

A new project ships a *pinned copy* of exactly the directories below —
nothing else. Clone the canon to scratch, copy the allowlist out, then prune
the frozen history inside the copy. Never clone the canon tree whole into the
project, and never maintain the set as a post-clone denylist (`rm` after a
full clone): a denylist rots on every new top-level directory, which is how
`.agents/`, `.aidoc/`, `plans/`, and 4.2 MB of `framework/archive/` leaked
into consumer trees (#834).

```bash
# Clone the canon to scratch (never into the project tree)
git clone --depth 1 https://github.com/vladm3105/aidoc-flow-framework.git /tmp/aidoc-framework

# Copy ONLY the consumer allowlist into the fresh project tree
# (new adoption; refreshes go through UPGRADE-RUNBOOK.md, which removes first)
mkdir -p .aidoc/framework
cp -r /tmp/aidoc-framework/{framework,docs,hooks,sdd_doc_lint,tests} .aidoc/framework/

# Prune canon-dev history inside the copy (frozen CHG archive)
rm -rf .aidoc/framework/framework/archive
```

**Shipped directories (the allowlist):**

| Directory | Purpose |
|-----------|---------|
| `framework/` | Core spec — governance, layers, playbooks, registry, skills, orientation guides, `VERSION`, `CHANGELOG.md` (minus `archive/`, pruned above) |
| `docs/` | Framework documentation (including this contract and the adaptation guide) |
| `hooks/` | Advisory hooks (`PostToolUse` + `PreCommit` — see `hooks/README.md`) |
| `sdd_doc_lint/` | Structural linter (296+ checks) |
| `tests/` | Shared suites (conformance, acceptance, unit) — re-pass on upgrade |

**Deliberately NOT shipped (stays in canon):** `.agents/` (repo skills),
`.aidoc/` (canon's own learning log), `.github/` (canon CI), `plans/`
(working plans), root dev docs (`AGENTS.md`, `CONTRIBUTING.md`,
`GOVERNANCE.md`, `README.md`, `SECURITY.md`, `CHANGELOG.md`, `LICENSE`),
tooling dotfiles (`.pre-commit-config.yaml`, `.gitleaks.toml`, linter
configs), and the canon `.git` history. Refresh a pinned copy by repeating
the copy above per `framework/governance/aidoc/UPGRADE-RUNBOOK.md` — never by
pulling inside `.aidoc/framework/`.

### 7.2 Directory structure contract

Projects maintain a `.aidoc/` directory with this structure:

```
.aidoc/
├── profile.yaml             # Project adaptation knobs
├── framework/               # Pinned allowlist copy (§7.1, version-pinned)
│   ├── framework/           # Core spec (WITHOUT archive/ — pruned, §7.1)
│   │   ├── governance/
│   │   ├── layers/
│   │   ├── playbooks/
│   │   ├── registry/
│   │   ├── skills/
│   │   ├── *.md guides      # orientation docs, ship with the copy
│   │   ├── CHANGELOG.md     # upgrade input (per-version migration notes)
│   │   └── VERSION          # pinned-version source of truth
│   ├── docs/
│   ├── hooks/
│   ├── sdd_doc_lint/
│   └── tests/
├── project/                 # Project-specific overrides
│   ├── governance/          # Rule overrides
│   ├── layers/              # Template overrides
│   ├── playbooks/           # Playbook overrides
│   ├── scripts/             # Script overrides
│   ├── templates/           # Template overrides
│   └── registry/            # Registry overrides
└── README.md
```

### 7.3 Discovery rule

When reading a template, rule, or playbook:

1. Check `.aidoc/project/{same-path}` first (project override)
2. If the file exists there, use it
3. If not, fall back to `.aidoc/framework/framework/{same-path}` (shared framework)

### 7.4 Version pinning

The project's `.aidoc/profile.yaml` records the pinned framework version:

```yaml
metadata:
  framework_source: "https://github.com/vladm3105/aidoc-flow-framework"
  framework_path: ".aidoc/framework"
  framework_spec_path: ".aidoc/framework/framework"
  framework_version: "0.53.1"  # Frozen 0.53.x-era pin (see banner); live version: framework/VERSION
```

### 7.5 Updating the framework

```bash
cd .aidoc/framework && git pull origin main
```

After pulling, verify `framework/VERSION` matches the pin in `.aidoc/profile.yaml`. If a newer version has breaking changes, update project overrides in `.aidoc/project/` before adopting.

### 7.6 No symlinks

> **Superseded (CHG-24 #801):** the binding rule is
> `framework/governance/ADAPTATION.md` § "Symlink convention" —
> `.aidoc/framework/` is a symlink to the shared framework directory
> (canonical). The MUST-NOT below is the frozen 0.53.x-era rule, kept as
> history; see `docs/ADAPTATION-GUIDE.md` §2 for the live convention.

Projects MUST NOT use symlinks to external framework directories. The framework must be a real cloned copy to support version pinning, local patches, and clean updates.
