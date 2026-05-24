# Changelog

All notable changes to the AI Doc Flow Framework (multi-platform project) are
documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this is the **project-level** changelog tracking the multi-platform
> migration. Once scaffolded, each platform keeps its own changelog at
> `platforms/<name>/CHANGELOG.md`, and `framework/` versions independently.

## [Unreleased]

### Changed

- Framework spec **0.3.2 → 0.4.0** (minor) — FRWK-REVIEW pre-production audit,
  batches 1 (correctness) + 2 (security). **Correctness:** corrected malformed
  trace-tag examples in the SPEC/TDD templates to the registry's element form
  (`TYPE.NN.SS.xxxx`, never a `TYPE-NN.SS.xxxx` hybrid) and added an `id_standard`
  note to the SPEC/TDD/IPLAN templates documenting where document-level refs are
  the intentional per-component bridge; reframed the BDD template's downstream
  guidance; closed a numbering gap in the BRD template's extra-small requirement
  IDs; renamed the PRD index status "Review" → "In Review" with a
  doc-status-vs-lifecycle note; documented the index-template extension split in
  the layer registry; retired stale "5-Gate" branding now that GATE-SPEC is the
  sixth gate, unified the emergency post-mortem SLA to 48h, and surfaced GATE-SPEC
  on the change-approval form + post-mortem template. **Security:** new
  `framework/governance/SECURITY_REVIEW.md` (engine-agnostic safety checks for
  agent-authored artifacts — secret leakage, prompt-injection, provenance,
  active-content sanitization), referenced from `DOC_GOVERNANCE_CORE.md` and the
  gates; a new blocking `GATE-03-E008` requiring external-source changes to cite a
  CVE/advisory or an explicit `no advisory applies: <reason>` escape (W001 kept as
  the softer nudge); a `DIAGRAM_STANDARDS.md` sanitization rule for mermaid click
  handlers + inline HTML; and a `GATE-SPEC-W003` security/abuse-review check for
  agent-facing spec changes. New `tests/conformance/test_framework_review_guards.py`
  locks the correctness fixes in (suite now 46 tests); `test_governance.py`
  `EXPECTED_FILES` gains `SECURITY_REVIEW.md`. Both `FRAMEWORK_SPEC_VERSION` files
  and the plugin skills' `framework_spec_version` re-synced.
- Framework spec **0.3.1 → 0.3.2** (patch) — `framework/README.md` governance
  section now documents GATE-SPEC, the project adaptation overlay
  (`ADAPTATION.md` + `ADAPTATION_SURFACE.yaml`), and `DECISIONS.md` (the
  spec-level decision register). Doc-only; both `FRAMEWORK_SPEC_VERSION` files
  and the plugin skills' `framework_spec_version` re-synced.

### Added

- **Pre-commit hooks** (`.pre-commit-config.yaml` + a `pre-commit` CI workflow,
  D-0021): hygiene (whitespace/EOF/check-yaml·json·toml/merge/large-files/
  private-key), **ruff** + ruff-format, **bandit** (gated medium+), **markdownlint**,
  **yamllint**, **detect-secrets** (baseline), **pip-audit** (manual/CI stage), and
  a local hook running the conformance suite. Pragmatic rule sets (stylistic
  noise disabled); `legacy/` + Hermes vendored/parsed content excluded. A repo-wide
  autofix + cleanup pass was applied (markdownlint/ruff over ~450 files, plus
  hand-fixed genuine findings) so `pre-commit run --all-files` is green; the stale
  `ucx_hermes` placeholder config was replaced.

## [1.1.0] — 2026-05-24

First post-cutover feature release. Tagged `v1.1.0` at the PR #2 merge; bundles
the canonical plugin skill-set revision, the project adaptation overlay (ADAPT),
and the return of change management as the GATE-SPEC framework-spec gate
(CHG-D1) plus its formal governance record (CHG-D2). Framework spec **0.1.0 →
0.3.1**.

### Changed

- **Plugin layer-model migration (PLM).** Migrated the entire Claude Code
  plugin skill corpus (125 skills) from the legacy **12-layer** SDD model to the
  framework's **8-layer** model (BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN), closing
  the layer-model gap noted under [1.0.0] and in `docs/PARITY.md` (the gap was
  far larger than that note implied — 116/142 skills carried legacy
  fingerprints). Renamed `doc-tspec*`→`doc-tdd*` and `doc-tasks*`→`doc-iplan*`;
  retired the legacy SYS/REQ/CTR families (142→125 skills); kept the SPEC- and
  test-subtype families as L6/L7 specialization helpers (decision D-0015);
  realigned every layer number, element ID (now 4-segment `TYPE.NN.SS.xxxx`),
  `framework/layers/` path, downstream/traceability chain, and skill
  cross-reference; removed dead validation-script references. Delivered in
  staged, conformance-gated batches B0–B7 (`plans/PLM-PLAN.md`).

### Added

- **Framework governance decision register (CHG-D2).** New
  `framework/governance/DECISIONS.md` — the spec's own durable home for
  decisions about the spec and its governance. Records the CHG implementation
  model (CHG-D1) as **GD-01**, engine-agnostic; lists D-0013 + D-0019 as pending
  graduation from the migration log. Recording it was itself a GATE-SPEC change
  (framework spec **0.3.0 → 0.3.1**, the first real exercise of the gate).
- **GATE-SPEC — the framework-spec change gate (CHG-D1, D-0020).** Implements
  ROADMAP CHG-D1 — change management as skills + CI/CD, both platforms. Adds the
  *meta* gate that governs changes to the `framework/` spec itself (templates,
  governance, registry, VERSION), orthogonal to the artifact-cascade gates: a new
  `GATE-SPEC_FRAMEWORK.md` definition, a `spec` `change_source` + `semver_impact`
  field, error-catalog/interaction-diagram/CHG-template/README wiring. Wired
  through the plugin CHG skills (`gate-check` runs it; `doc-chg` family routes to
  it) and the Hermes server-side validator (`validation/chg_rules.py`). The
  diff-aware checks (E005 VERSION bump, E008 CHANGELOG) ship as
  `tests/chg/spec_gate.py` + a staged CI workflow; the human-approval half is
  documented as protected-branch review. This **unblocks** `knowledge-extractor`'s
  spec-promotion path. Framework spec **0.2.0 → 0.3.0**.
- **Project adaptation overlay (ADAPT, D-0019).** `framework/governance/ADAPTATION.md`
  - machine-readable `ADAPTATION_SURFACE.yaml` (a closed 4-knob surface:
  `active_layers`, `section_toggles`, `audit_threshold` raise-only, `glossary`),
  the `adapts:` consult-clause across the 35-skill adapting set, and two new
  utility skills — `project-profile` (maintains `.aidoc/profile.yaml`) and
  `knowledge-extractor` (promotes proven local adaptations upward). Framework spec
  **0.1.0 → 0.2.0**.
- Conformance check `tests/conformance/platforms/test_plm_lint.py` (suite now
  **32** tests) — fails if any plugin skill reintroduces a legacy 12-layer
  fingerprint, locking the migration in against regression. *(Suite has since
  grown to 43 with the adaptation-surface and GATE-SPEC guards.)*

## [1.0.0] — 2026-05-21

**Phase 5 — Cutover.** The multi-platform project replaces `main`.
The migration from the pre-migration `ucx_framework` (v0.20.4) is
complete: one engine-agnostic specification (`framework/`) plus two
independent platforms (Hermes MCP server, Claude Code plugin), both
green on the shared conformance suite. The pristine pre-migration
project is preserved on the protected, read-only archive branch
`legacy-ucx-v3.2-read-only`.

> Version scope (P5-T1 Q4): `v1.0.0` is the **project-milestone**
> tag for the cutover — *not* a claim that every component is
> 1.0-stable. `framework/` stays `0.1.0` (no spec change; earns
> `1.0.0` later under the returning CHG governance). The plugin
> stays `0.1.0` (documented layer-model gap, see below). The Hermes
> api_runner fix below ships as the optional `hermes/v0.1.1` patch.

### Removed

- In-tree `legacy/` directory (2276 tracked files, ~645k lines) —
  the pre-migration `ucx_framework` working copy. **Lossless:** the
  full content is preserved byte-for-byte on the protected
  `legacy-ucx-v3.2-read-only` branch (`491e8db`) and in git history.
  (P5-T2)
- Dev-time root `.claude/` loader (240 tracked files) — the
  migration-era Claude Code skills/agents/commands/hooks used to run
  the migration itself. The shipped Claude Code delivery is now the
  **plugin** (`platforms/claude-code-plugin/`), not a root loader.
  **Lossless:** skills/agents/commands are productized in the
  plugin; the pre-migration `.claude/` is on the archive branch; the
  migration-era `.claude/` (incl. the 3 hooks) remains in git
  history. (P5-T3)

### Fixed

- `platforms/hermes/src/mcp_server/executor/api_runner.py` — the
  litellm-missing error told users to `pip install 'ucx_hermes[api]'`;
  corrected to `pip install 'hermes-server[api]'` to match the
  distribution rename in P2-T1 Q1. Resolves the carried known issue
  surfaced at P4-T5 verify. Ships as the optional `hermes/v0.1.1`
  patch (see `platforms/hermes/CHANGELOG.md`).

### Changed

- Project docs finalized for the as-built, post-migration state
  (P5-T4): `README.md` (dropped migration framing + `legacy/` from
  the structure diagram; platform matrix → release tags; added
  archive-branch + PARITY/TAGGING pointers); `docs/REPO_STRUCTURE.md`
  (PLANNED → as-built; legacy mapping reframed as history);
  `docs/PROJECT.md` (§3/§4 cutover reconciled to the archive
  branch); `CLAUDE.md` (rewritten from migration-in-progress memory
  to slim post-migration project memory; root file, survived the
  `.claude/` removal).

### Known carried issues (post-v1.0)

- **Plugin SDD layer-model gap** — the plugin reflects the legacy
  11-layer model and lacks `doc-tdd` + `doc-iplan` (`docs/PARITY.md`
  "Known parity gap"). Content depth, not a correctness issue;
  per-skill content migration tracked as post-v1.0 work. This is why
  the plugin honestly stays `0.1.0`.
- **~150 Class D stale `framework/<X>` references** in plugin skill
  content (P3-T2 G18) — same root cause as the layer-model gap.
- **CI workflows** at `plans/workflows-pending/` await user `git mv`
  into `.github/workflows/` from a local clone (in-container GitHub
  App lacks `workflows` permission).

## [0.5.0] — 2026-05-21

Phase 4 — Conformance & Independence. Platform-conformance tests
(PC1 + PC4) added to the shared suite; greenfield CI workflows
authored; per-platform CHANGELOG retrofits; expanded Hermes README;
repo-root LICENSE; parity report.

### Added

- `tests/conformance/platforms/` sub-package with PC1 (version
  declaration: VERSION + FRAMEWORK_SPEC_VERSION files exist, are
  bare SemVer, match `framework/VERSION`) and PC4 (engine isolation:
  forbidden-token scan scoped to runtime-significant directories
  per platform) test modules. Suite grows **25 → 31 tests**.
- Three greenfield GitHub Actions workflows authored, staged at
  `plans/workflows-pending/` pending user `git mv` to
  `.github/workflows/` (in-container GitHub App lacks `workflows`
  permission — see `docs/TAGGING.md` "In-container push
  restrictions"):
  - `conformance.yml` — runs the 31-test conformance suite on
    every push/PR.
  - `hermes.yml` — runs Hermes' pytest suite (Python 3.12 via
    `actions/setup-python@v5`) on push/PR touching
    `platforms/hermes/**` or `framework/**`.
  - `plugin.yml` — smoke-checks the plugin: manifest valid +
    coupling sweep + structural sanity on push/PR touching
    `platforms/claude-code-plugin/**`.
  All `ubuntu-latest`; concurrency cancel-in-progress; minimal
  `contents: read` permissions. No carry-over from
  `legacy/github-workflows-disabled/` (28 workflows, all
  self-hosted-coupled).
- `platforms/hermes/CHANGELOG.md` — Hermes `[0.1.0]` mirroring
  project `[0.3.0]` scoped content. Cross-references project-level
  CHANGELOG and `plans/P2-T*-PLAN.md` for the full audit trail.
- `platforms/claude-code-plugin/CHANGELOG.md` — plugin `[0.1.0]`
  mirroring project `[0.4.0]` scoped content, with a "Known
  limitations" section flagging the legacy-vs-new SDD layer model
  gap.
- `LICENSE` at repo root — MIT, copyright `vladm3105` (matches
  plugin manifest's `"license": "MIT"` placeholder).
- `docs/PARITY.md` — 5-section capability comparison between
  Hermes and the Claude Code plugin: capability matrix (8 SDD
  layers × 2 platforms); workflow operations; platform-specific
  extras; known parity gap (plugin reflects the legacy 11-layer
  model; lacks `doc-tdd` + `doc-iplan`); user-facing
  "choosing between" decision table.
- `docs/STARTUP_HANDOFF.md` — distills business / startup ideas
  from the migration session (IPLAN-as-product, corpus, domain
  profiles, CHG governance-as-code, etc.) for a future strategy
  session. Separate from the technical migration scope.
- Per-task plans `plans/P4-T0..T5-PLAN.md`, the design doc
  `plans/P4-T1-DESIGN.md`, the audit `plans/P4-AUDIT-conformance.md`,
  and the verify record `plans/P4-T5-VERIFY.md`.

### Changed

- `tests/conformance/_spec.py` — extended **additively** with
  platform helpers (`PLATFORMS_ROOT`, `platform_dirs`,
  `platform_version_file`, `platform_framework_spec_version_file`,
  `framework_version`). Existing helpers + imports untouched.
- `platforms/hermes/README.md` — expanded from 27-line Phase-0
  placeholder to 113-line user-facing doc. Full mirror of P3-T3's
  populated plugin README structure: inventory table, install +
  `.mcp.json` snippet, MCP tool list, framework spec conformance
  section, platform info table, relationship-to-plugin section.
- `docs/TAGGING.md` — appended "In-container push restrictions"
  section documenting the two operation classes that need the
  local-clone workaround (`refs/tags/*` — 4 occurrences after
  P4-T5; `.github/workflows/**` — 1 occurrence). Symmetric with
  the existing tag-push reference.

### Known carried issues (deferred)

- **CI workflow files** at `plans/workflows-pending/` — user
  `git mv`'s them into `.github/workflows/` from a local clone.
  Phase 4 closed without that user action; the relocation is a
  transit detail, not a content gap.
- **Plugin legacy-vs-new SDD layer model gap** (P3-T1 §Deferred
  R2 / `docs/PARITY.md` "Known parity gap"). Plugin lacks
  `doc-tdd` + `doc-iplan`; has `doc-sys` / `doc-req` / `doc-ctr` /
  `doc-tspec` / `doc-tasks` from the legacy 11-layer model.
  Hermes covers all 8 new-model layers via its generic `sdd_*`
  tools. Resolution is a per-skill content-migration task tracked
  as post-v1.0 cleanup.
- **`platforms/hermes/src/mcp_server/executor/api_runner.py:115`**
  carries a stale install instruction
  (`pip install 'ucx_hermes[api]'`); current distribution is
  `hermes-server` (P2-T1 Q1). 1-line fix; deferred to Phase 5
  housekeeping or a `hermes/v0.1.1` patch.
- **~150 Class D stale `framework/<X>` references** in plugin
  skill content (P3-T2 G18) — same root cause as the layer model
  gap; resolution post-v1.0.

## [0.4.0] — 2026-05-20

Phase 3 — Platform B: Claude Code plugin. `platforms/claude-code-plugin/`
ships the 142-skill SDD engine as a native Claude Code plugin (no MCP
backend), consumes `framework/` at `v0.1.0`, and is released as
`claude-code-plugin/v0.1.0`. The plugin uses Claude Code's
auto-discovery from `skills/`, `agents/`, `commands/` at plugin root —
no explicit registration in the manifest.

### Added

- `platforms/claude-code-plugin/` — the Claude Code plugin platform.
  171 net files (post-cleanup): 142 skill directories (129 `doc-*`
  - 13 SDD-adjacent non-doc), 19 skill-root files (quickrefs +
  set-overview READMEs + `REVIEW_DOCUMENT_STANDARDS.md`), 1 agent
  (`requirements-analyst`), 1 command (`save-plan`), plus 4 new
  top-level files (manifest + 2 VERSION files + populated README).
- `platforms/claude-code-plugin/.claude-plugin/plugin.json` —
  minimal 7-field manifest (`name`, `description`, `version`,
  `license`, `repository`, `homepage`, `keywords`). Plugin name
  `aidoc-flow`; slash-prefix `/aidoc-flow:doc-...`. Author block
  omitted (the in-container `git config user.name` returns the
  session's identity, not the repo owner; the `repository` URL
  handles ownership signaling — matches Hermes pyproject precedent).
- `platforms/claude-code-plugin/VERSION` (`0.1.0`, 6 bytes) and
  `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` (`0.1.0`,
  byte-identical to `framework/VERSION`) — declares the plugin's
  own SemVer + framework-spec conformance per D-0009 / P2-T1 Q2.
- `platforms/claude-code-plugin/README.md` — populated user-facing
  doc (82 lines, from 27-line Phase 0 placeholder): inventory table,
  install pointer, slash-prefix use examples, framework spec
  conformance with VERSION cat output, platform info table,
  Hermes-platform relationship section.
- `plans/P3-T0-PLAN.md` + `plans/P3-AUDIT-claude-code-plugin.md` —
  Phase 3 audit (191-file `.claude/` inventory; copy-with-divergence
  relationship resolved) and task breakdown.
- Per-task plans `plans/P3-T1..T5-PLAN.md`, each with the two-pass
  review log mandated by D-0007.
- `plans/P3-T1-DESIGN.md` — 7 plugin design decisions resolved
  before any content moved (manifest schema verified via the
  `claude-code-guide` agent — Claude Code auto-discovers,
  no explicit registration block; plugin name `aidoc-flow`; copy
  strategy is the 3-stage `cp -r` + `rm -rf` recipe; no lifecycle
  hooks in `v0.1.0`).
- `plans/P3-T4-VERIFY.md` — formal Phase 3 verify record covering
  22 gates (conformance 25/25, plugin structure, coupling sweep,
  manifest validity, integration checks).

### Changed

- Rewrote all `ai_dev_flow` placeholder paths in the ported skill
  content to point at `framework/` — 211 line hits across 30 files
  cleared via word-boundary regex sed (P2-T7 G12). Class B (5 layer
  dirs → `framework/layers/0X_TYPE/`) and Class C
  (`ID_NAMING_STANDARDS.md` → `framework/governance/`) sub-path
  corrections applied. 2 illustration `/opt/data/...` paths
  preserved per the P2-T7 G13 historical-vs-current rule.
- `project-mngt/SKILL.md` — the one current-behavior
  `/opt/data/ucx_framework/...` reference rewired to repo-relative
  `framework/governance/ID_NAMING_STANDARDS.md`.

### Removed

- 7 non-SDD-adjacent skill directories excluded from the plugin
  port: `code-review`, `refactor-flow`, `analytics-flow`,
  `devops-flow`, `ai-pr-review`, `google-adk`, `n8n` (P3-T1 Q2 —
  general-purpose, not coupled to any SDD artifact). Source
  `.claude/skills/` retains them; they remain available in dev-time
  use until Phase 5 cutover.
- 3 `.claude/skills/` root files excluded from the plugin port:
  `README.md` (referenced an obsolete multi-project symlink pattern
  and the legacy `ucx_framework/.claude/skills/` canonical path),
  `google-adk_quickref.md`, `n8n_quickref.md` (parent skills out).
- **47 broken symlinks** the source `.claude/skills/` carried via
  `cp -r` into the plugin — self-referencing pointers at
  `/opt/data/docs_flow_framework/.claude/skills/<name>`, leftovers
  from the old multi-project symlink consumption pattern. Removed
  in-flight during P3-T4 verify (G18 finding) via `xargs git rm`
  on the 47 symlink entries.

### Carried known issue (deferred)

- The ~150 Class D stale `framework/<X>` references in the ported
  skills point at concepts not in the current 8-layer framework
  (`framework/scripts/`, legacy 11-layer numbering,
  legacy alpha-named dirs, legacy top-level guides). Resolution is
  a per-skill content-migration task outside Phase 3 scope (P3-T1
  §Deferred R2). The plugin works as a Claude Code artifact
  regardless — the references are documentation hygiene, not
  runtime correctness.

## [0.3.0] — 2026-05-20

Phase 2 — Platform A: Hermes Re-homing. `platforms/hermes/` is fully
assembled, consumes `framework/` at `v0.1.0`, and ships its own first
release as `hermes/v0.1.0`. The MCP server's scaffold + validation
runtime now reads layer templates from `framework/layers/<NN>_<X>/`
per D-0013, closing the platform-template duplication.

### Added

- `docs/TAGGING.md` — the full git-tag policy: release tags (`vX.Y.Z`,
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`) and `mark/<slug>` bookmark tags,
  with create / push / find commands (D-0011). `docs/PROJECT.md` §3 slimmed
  to a summary that links it.
- `ROADMAP.md` "Post-v1.0 — Planned Capabilities" — the domain-profile
  mechanism for generalizing the IPLAN beyond software (D-0012).
- `platforms/hermes/` — the Hermes MCP server platform. 437 net files
  ported and rewired across four sub-tasks: 64 verbatim (P2-T2 —
  `examples/`, `prompts/`, `skills/layer_aliases/`, `skills/personas/`,
  `skills/persona_mappings.yaml`); 200 port-with-repoint (P2-T3 —
  `pyproject.toml`, `src/`, `tests/`, `docs/` less `migration/`,
  `skills/README.md`, `skills/hermes/`); 181 agent-skills from `main`
  (P2-T7 — `agent-skills/spec-driven-development/{sdd-orchestrator,
  sdd-review-personas}/`); minus 8 dropped (P2-T8 — drifted layer
  templates that D-0013 obsoleted).
- `platforms/hermes/VERSION` (`0.1.0`) and
  `platforms/hermes/FRAMEWORK_SPEC_VERSION` (`0.1.0`, matching
  `framework/VERSION`) — declares Hermes' own SemVer + the framework
  spec version it conforms to (D-0009 mechanism, P2-T1 Q2).
- `platforms/hermes/pyproject.toml` keys: `name = "hermes-server"`
  (P2-T1 Q1) at `version = "0.1.0"`; `[project.scripts]
  hermes-mcp = "mcp_server.server:main_sync"` (P2-T1 Q4). Distribution
  name distinguishes the project; the `mcp_server` import path is
  preserved (no Platform B Python collision; P2-T1 Q1 rationale).
- `plans/P2-T0-PLAN.md` + `plans/P2-AUDIT-hermes.md` — the Phase 2
  audit (280-file Hermes tree classified port-verbatim / port-with-
  repoint / drop) and the per-task breakdown (T0..T9).
- Per-task plans `plans/P2-T1..T9-PLAN.md`, each with the two-pass
  review log mandated by D-0007.
- `plans/P2-T5-VERIFY.md` — the formal Phase 2 verify record covering
  14 gates (conformance 25/25, Hermes own suite 447/447, coupling
  sweep, version files, smoke test, structure, file inventory).
- `plans/DECISIONS.md` D-0013 — single-source-of-truth for layer
  templates: platforms consume `framework/layers/`, never duplicate.

### Changed

- Recorded the framework's purpose — the IPLAN as the terminal product;
  code/deploy out of scope; v1 scope is software/devops (D-0012).
- Refined D-0012: the IPLAN has a planned and an executed state with
  criticality-scaled audit depth (R1); the curated corpus of proven IPLANs —
  with composition and freshness — is the unit of value and the post-v1.0
  strategic destination (R2).
- Rewrote all `ucx_flow_v3` runtime coupling to point at `framework/`:
  18 files in the edit set (4 code + 3 tests + 5 skills + 6 architecture/
  spec docs), with sub-path repoints to `framework/registry/` and
  `framework/layers/<NN>_<X>/` (P2-T3). 11 historical-context docs
  (CHANGELOGs, ROADMAP retrospective, completed PLAN-* checklists)
  preserved verbatim per the G13 lesson — rewriting them would falsify
  history.
- Rewired the MCP server's scaffold runtime to consume the framework's
  per-layer layout (P2-T9). Five spots across three files closed the
  D-0013 architectural gap that P2-T3 first surfaced: removed the
  `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`, rewrote
  `_default_ssd_root` to return `framework/layers`, corrected
  `_default_repo_root` parents count (`[4]→[5]` — layout shifted in
  P2-T3), and rewrote `validation/runner.py:_resolve_canonical_template_root`
  as a 3-stage precedence chain (project framework override → scaffold
  output → canonical). Hermes' own test suite went 397/447 → **447/447**.
- Rewrote the skill's template-loading prose (P2-T8): 25 references in
  `agent-skills/.../sdd-orchestrator/SKILL.md` +
  `references/sdd-workflow-quickstart.md` rewired from skill-relative
  `templates/0N_TYPE-TEMPLATE.yaml` to framework-relative
  `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`; the `skill_view` API
  example was rewritten as a direct-read instruction since templates
  now live outside the skill.
- `.mcp.json` cwd repointed from `legacy/ucx_hermes/src` to
  `platforms/hermes/src` (P2-T3).
- `plans/P2-AUDIT-hermes.md` refreshed with §3a extension (3 test
  files added to the code-level coupling list) and §3c (new section —
  "Documentation cluster — historical vs current") to record audit
  gaps discovered during P2-T3 planning.

### Removed

- The 8 drifted layer template YAMLs at `platforms/hermes/agent-skills/
  spec-driven-development/sdd-orchestrator/templates/` (P2-T8). They
  carried engine hardcodes (`server: ucx_hermes`, `tool: sdd_validate`,
  `SDD v3` labels, vendor-named agent placeholders) that D-0013
  excluded from documents. The framework `framework/layers/<NN>_<X>/
  <X>-TEMPLATE.yaml` set is the single source of truth.
- 6 D-0013-obsolete sync files from the agent-skills package (P2-T7):
  `sync-ucx-templates.sh`, `sync.py`, `.sync-backlog.json`,
  `template-sync-procedure.md`, `template-v3-alignment-checklist.md`,
  `ucx-framework-quirks.md`. There is no longer anything to sync —
  Hermes consumes `framework/layers/` directly.
- The `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS` (P2-T9) and
  the no-op `exists()` branch in `_default_ssd_root` — both dead code
  after D-0013.
- `legacy/ucx_hermes/docs/migration/MIGRATION_FROM_MCP_UCX.md` from the
  port set (P2-T3) — `mcp_ucx/` is the deprecated predecessor, archived
  in `legacy/` and slated for full removal at Phase 5 cutover.

## [0.2.0] — 2026-05-19

Phase 1 — Framework Spec Extraction. `framework/` is fully assembled and
guarded by a 25-test conformance suite. Framework spec released as
`framework/v0.1.0`.

### Added

- Plan-review gate (D-0007): plans require a `## Review log` of ≥2 passes;
  `plans/PLAN-TEMPLATE.md` added; non-blocking `PreToolUse(git commit)` hook
  warns when a staged plan file falls short.
- `plans/P1-AUDIT-ucx_flow_v3.md` — Phase 1 audit (P1-T1) classifying the
  49-file legacy SDD tree as engine-agnostic, mixed, instance, or drop, with
  the target `framework/` layout for the Phase 1 extraction steps.
- `framework/layers/` (P1-T2) — the 8 engine-agnostic SDD layer specs
  extracted from `legacy/ucx_flow_v3/`: per layer a `*-TEMPLATE.yaml`, a
  `README.md`, and a `*-00_index.TEMPLATE.*` index template (24 files). All
  Hermes/MCP- and Claude-Code-specific content removed; legacy version
  strings neutralized.
- `framework/registry/` (P1-T3) — `LAYER_REGISTRY.yaml`, the authoritative
  machine-readable layer model (layer order, traceability graph, C4 mapping,
  ID patterns), plus a `README.md`. Standalone version field and legacy
  changelog dropped; layer `folder` paths repointed under `layers/`.
- `framework/governance/` (P1-T4) — 5 governance docs (`DOC_GOVERNANCE_CORE`,
  `ID_NAMING_STANDARDS`, `TRACEABILITY`, `DIAGRAM_STANDARDS`,
  `THRESHOLD_NAMING_RULES`) and the CHG overlay (`chg/` — README, template,
  index template, 7 gates, 2 companion templates), 18 files. Engine-specific
  skill references and `MCP` mentions neutralized; CHG extracted spec-only
  (not enforced until post-Phase 5).
- `tests/conformance/` (P1-T5) — the shared conformance suite: stdlib
  `unittest` tests covering registry self-consistency, layer templates,
  governance files, the framework root, `VERSION`, and spec hygiene (no engine
  tokens in `framework/`), plus the documented platform-conformance contract
  for Phase 4. No `pytest` dependency (D-0008).
- `framework/README.md` — the engine-agnostic spec overview (8-layer flow, C4
  alignment, layout, conformance, versioning), replacing the scaffolding
  placeholder.
- `framework/VERSION` (P1-T6) — the framework spec's independent version
  stream, at `0.1.0`.
- `docs/PROJECT.md` §3 — tag-namespace convention: project milestones
  `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms `<platform>/vX.Y.Z`
  (D-0009).
- `framework/` root methodology docs (P1-T7) — `SPEC_DRIVEN_DEVELOPMENT_GUIDE`,
  `QUICK_REFERENCE`, `AI_ASSISTANT_RULES`, `TESTING_STRATEGY_TDD`, extracted
  engine-neutral (version strings neutralized, links repointed, legacy
  version-lineage content dropped per D-0010).

### Changed

- **Legacy isolation (P1-T0):** all pre-migration content moved into `legacy/`
  (frozen) — `ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`, `ai_dev_ssd_flow_v2`,
  `governance`, and supporting trees. Repo root now holds only the new
  project (`framework/`, `platforms/`, `docs/`) plus infrastructure.
- Legacy GitHub Actions workflows disabled (parked in
  `legacy/github-workflows-disabled/`).
- Root `README.md` rewritten for the multi-platform project.
- `.mcp.json` Hermes server path repointed to `legacy/ucx_hermes/`.

## [0.1.0] — 2026-05-18

Phase 0 — Planning & Scaffolding. The migration baseline.

### Added

- Planning baseline for the multi-platform restructure:
  - `ROADMAP.md` — phased delivery plan (Phase 0 → cutover v1.0.0).
  - `docs/REPO_STRUCTURE.md` — target repository layout and legacy mapping.
  - `docs/PROJECT.md` — versioning, branching, milestones, conformance, and
    interim change-management policy.
  - `platforms/hermes/` and `platforms/claude-code-plugin/` directories.
  - `framework/` directory placeholder for the shared engine-agnostic spec.
- CHG implementation decision recorded as tracked TODO (ROADMAP CHG-D1/D2,
  `docs/PROJECT.md` § CHG implementation model): CHG to be built as
  skills + CI/CD post-Phase 5.
- `CLAUDE.md` — auto-loaded project memory: development workflow
  (plan → review → harden → implement → verify → land), definition of done,
  and session-handoff practice.
- `plans/` workspace — `README.md`, `MIGRATION_TODO.md` (live task tracker),
  `HANDOFF.md` (session continuity), `DECISIONS.md` (decision log).
- `.claude/` automation hooks: `PreCompact` (auto-commit + push a WIP
  snapshot before compaction) and `SessionStart` (inject `plans/HANDOFF.md`
  into context), with scripts under `.claude/hooks/`.

### Notes

- Forked from `ucx_framework` v0.20.4 (`main`).
- The gated CHG change-management process is intentionally not applied during
  the migration; it is re-introduced post-cutover (see `docs/PROJECT.md`).

[Unreleased]: https://github.com/vladm3105/aidoc-flow-framework/tree/claude/multi-platform-migration-AamWB
[0.2.0]: https://github.com/vladm3105/aidoc-flow-framework/releases/tag/v0.2.0
[0.1.0]: https://github.com/vladm3105/aidoc-flow-framework/releases/tag/v0.1.0
