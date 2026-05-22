# Claude Code Plugin Changelog

All notable changes to the **Claude Code plugin** platform are
documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this platform adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this changelog tracks the Claude Code plugin at
> `platforms/claude-code-plugin/`. For framework spec changes see
> [`../../framework/`](../../framework/); for project-level migration
> history see [`../../CHANGELOG.md`](../../CHANGELOG.md).
>
> Tag namespace: `claude-code-plugin/vX.Y.Z` (per
> [`../../docs/TAGGING.md`](../../docs/TAGGING.md) D-0011).

## [Unreleased]

### Added
- AI Team specialist agent roster — 8 new subagents under `agents/`
  (`pm-orchestrator`, `solutions-architect`, `test-architect`,
  `software-engineer`, `devops-release-engineer`, `code-reviewer`,
  `security-engineer`, `traceability-auditor`), joining the existing
  `requirements-analyst`, plus an `agents/README.md` roster overview.
  Mirrors the SDD lifecycle (spec lane → execution lane → read-only
  quality gates) with model tiers and human-in-the-loop approval.
  Imported from the `aidoc-flow-business` design and adapted to the
  plugin: engine-coupling references removed so the agents stay
  engine-isolated (PC4), skill references corrected to skills the
  plugin actually ships, and layer numbering reconciled to the
  canonical 8-layer model (legacy SYS/REQ/CTR/TSPEC labelled as
  legacy auxiliaries). Conformance suite stays green (31/31).

### Changed
- **Whole skill corpus migrated to the framework's 8-layer SDD model**
  (BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN), replacing the legacy 12-layer
  authoring model the skills were built on (task PLM,
  `../../plans/PLM-PLAN.md`). `doc-tspec*`→`doc-tdd*` (Layer 7),
  `doc-tasks*`→`doc-iplan*` (Layer 8); SPEC renumbered 9→6; element IDs
  now 4-segment `TYPE.NN.SS.xxxx`; all `framework/layers/` paths,
  downstream/traceability chains, and skill cross-references realigned;
  dead validation-script references replaced with declarative checks.
  The SPEC-subtype (`doc-cspec/dspec/uxspec/riskspec/procspec`) and
  test-subtype (`doc-utest/itest/stest/ftest/ptest/sectest`) families
  are retained as SPEC-L6 / TDD-L7 specialization helpers (D-0015).

### Removed
- Legacy `doc-sys*`, `doc-req*`, `doc-ctr*` skill families — the SYS,
  REQ, and CTR layers do not exist in the 8-layer model. Plugin skill
  count 142 → 125.

## [0.1.0] — 2026-05-20

First independent release of the Claude Code plugin platform on the
multi-platform `aidoc-flow-framework` repository. Conforms to
framework spec `v0.1.0`. Ships the SDD engine as a **native Claude
Code plugin** — no MCP backend.

### Added
- Claude Code plugin platform at `platforms/claude-code-plugin/`.
  171 net files: 142 skill directories (129 `doc-*` + 13 SDD-adjacent
  non-doc), 19 skill-root files (quickrefs + set-overview READMEs +
  `REVIEW_DOCUMENT_STANDARDS.md`), 1 agent (`requirements-analyst`),
  1 command (`save-plan`), plus 4 top-level files (manifest + 2
  VERSION files + populated README).
- `.claude-plugin/plugin.json` — minimal 7-field manifest (`name`,
  `description`, `version`, `license`, `repository`, `homepage`,
  `keywords`). Plugin name: `aidoc-flow`; slash-prefix
  `/aidoc-flow:doc-...`. No author block (the in-container
  `git config user.name` returned the session's identity, not the
  repo owner; the `repository` URL handles ownership signaling —
  matches Hermes pyproject precedent).
- `VERSION` (`0.1.0`, 6 bytes) and `FRAMEWORK_SPEC_VERSION` (`0.1.0`,
  byte-identical to `framework/VERSION`) — declares the plugin's own
  SemVer + framework-spec conformance per D-0009.
- `README.md` — 82-line user-facing doc: inventory table, install
  pointer, slash-prefix use examples, framework spec conformance
  with VERSION snippet, platform info table, Hermes-platform
  relationship section.
- Auto-discovery: Claude Code finds `skills/<name>/SKILL.md`,
  `agents/*.md`, `commands/*.md` without an explicit registration
  block in the manifest (verified via the `claude-code-guide`
  agent's documentation lookup).

### Changed
- Rewrote all `ai_dev_flow` placeholder paths in the ported skill
  content to point at `framework/` — 211 line hits across 30 files
  cleared via word-boundary regex sed.
- Class B sub-path corrections (5 layer dirs → `framework/layers/`)
  landed in 3 files.
- Class C sub-path corrections (`framework/governance/
  ID_NAMING_STANDARDS.md`) landed in 13 references.
- `project-mngt/SKILL.md` — the one current-behavior
  `/opt/data/ucx_framework/...` reference rewired to repo-relative
  `framework/governance/ID_NAMING_STANDARDS.md`.
- 2 illustration `/opt/data/...` paths preserved verbatim per the
  G13 historical-vs-current rule (Trading Nexus tutorial reference;
  `/opt/data/my_project` placeholder).

### Removed
- 7 non-SDD-adjacent skill directories excluded from the port:
  `code-review`, `refactor-flow`, `analytics-flow`, `devops-flow`,
  `ai-pr-review`, `google-adk`, `n8n` (general-purpose, not coupled
  to any SDD artifact per the P3-T1 scope decision).
- 3 `.claude/skills/` root files excluded from the port:
  `README.md` (referenced an obsolete multi-project symlink pattern
  and the legacy `ucx_framework/.claude/skills/` canonical path),
  `google-adk_quickref.md`, `n8n_quickref.md` (parent skills out).
- 47 broken symlinks the source `.claude/skills/` carried via
  `cp -r` — self-referencing pointers at
  `/opt/data/docs_flow_framework/.claude/skills/<name>`, leftovers
  from the old multi-project symlink consumption pattern. Removed
  in-flight during P3-T4 verify.

### Known limitations
- ~150 documentary references in skill content point at concepts
  that don't exist in the current 8-layer framework (legacy 11-layer
  numbering, legacy alpha-named dirs, legacy top-level guides).
  Resolution is a per-skill content-migration task tracked as
  post-v1.0 cleanup. The plugin works as a Claude Code artifact
  regardless — the references are documentation hygiene, not
  runtime correctness.
- The plugin reflects the **legacy 11-layer SDD model** in its
  skill set; `doc-tdd` and `doc-iplan` (new-model layers 7-8) are
  absent. See [`../../docs/PARITY.md`](../../docs/PARITY.md)
  "Known parity gap" for details.

> Full migration audit trail: project-level
> [`CHANGELOG.md [0.4.0]`](../../CHANGELOG.md) and
> [`plans/P3-T0-PLAN.md`](../../plans/P3-T0-PLAN.md) through P3-T5.
