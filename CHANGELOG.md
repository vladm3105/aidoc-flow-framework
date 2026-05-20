# Changelog

All notable changes to the AI Doc Flow Framework (multi-platform project) are
documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this is the **project-level** changelog tracking the multi-platform
> migration. Once scaffolded, each platform keeps its own changelog at
> `platforms/<name>/CHANGELOG.md`, and `framework/` versions independently.

## [Unreleased]

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
  + 13 SDD-adjacent non-doc), 19 skill-root files (quickrefs +
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
