# Hermes Platform Changelog

All notable changes to the **Hermes MCP server** platform are documented
here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this platform adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this changelog tracks the Hermes platform at
> `platforms/hermes/`. For framework spec changes see
> [`../../framework/`](../../framework/); for project-level migration
> history see [`../../CHANGELOG.md`](../../CHANGELOG.md).
>
> Tag namespace: `hermes/vX.Y.Z` (per
> [`../../docs/TAGGING.md`](../../docs/TAGGING.md) D-0011).

## [Unreleased]

### Changed

- **Element-ID alignment to the framework 4-segment hash form** (PLATFORM-ALIGN
  Part B, `0.1.0 → 0.2.0`). The runtime element-ID validators in
  `validation/cross_section.py` (`_ELEMENT_ID_RE`, `_ELEMENT_ID_INLINE_RE`) and
  `remediation/runner.py` (`_ID_PATTERN`) accepted the **3-segment** form
  `TYPE.NN.xxxx`; they now require the framework's canonical **4-segment** form
  `TYPE.NN.SS.xxxx` (adding the section segment), matching
  `LAYER_REGISTRY.yaml` `id_patterns.element`. Tests updated accordingly. The
  8-layer EARS/BDD prompt templates' element-ID examples + the `UCC_PROMPT_EARS`
  ID-convention legend were migrated off the legacy type-code scheme
  (`EARS.NN.<CODE>.<seq>`, `PRD.NN.US.NN`, 3-segment refs) to the 4-segment hash
  form. *Stricter validation:* a previously-accepted 3-segment ID now fails —
  intended (the 3-segment form was the legacy variant the framework retired).

- **EARS pattern alignment** — brought the Hermes vendored EARS pattern tables
  into line with the framework's canonical statement model (framework spec
  `0.6.0`, FRWK-REVIEW #4b). The persona docs (`skills/personas/requirements_specialist.md`,
  `agent-skills/.../sdd-review-personas/SKILL.md`) and the EARS prompt templates
  (`prompts/templates/{creation/UCC_PROMPT_EARS,creation/UCC_OUTPUT_SCHEMA,
  review/UCR_PROMPT_EARS,remediation/UCRem_PROMPT_EARS}.md`) had drifted to a
  6-pattern model with a mixed `IF…THEN` connective. Now: the five canonical
  patterns (Ubiquitous, Event/`WHEN`, State/`WHILE`, Optional/`WHERE`,
  Unwanted/`IF`) in the uniform `the [system] shall …` form (no `THEN`); "complex"
  reframed as *composition* of the base patterns (the standalone `Complex` row +
  the `CX` type code removed). Doc-only; no runtime behavior change.
  *(Note: the prompts' legacy type-code element-ID scheme — `EARS.NN.<code>.<seq>`
  vs the framework's hash-based `EARS.NN.SS.xxxx` — is a separate, pre-existing
  divergence, out of scope here.)*

## [0.1.1] — 2026-05-21

Patch — corrects a stale install instruction. Conforms to framework
spec `v0.1.0` (unchanged). Coincides with the project `v1.0.0`
cutover but versions independently (`docs/PROJECT.md` §3).

### Fixed

- `src/mcp_server/executor/api_runner.py` — the litellm-missing
  error string told users to `pip install 'ucx_hermes[api]'`;
  corrected to `pip install 'hermes-server[api]'`, matching the
  distribution name set in P2-T1 Q1. Surfaced at P4-T5 verify,
  fixed in P5.

## [0.1.0] — 2026-05-20

First independent release of the Hermes MCP server platform on the
multi-platform `aidoc-flow-framework` repository. Conforms to framework
spec `v0.1.0`.

### Added

- Hermes MCP server platform at `platforms/hermes/` — `src/mcp_server/`
  with 18 sub-modules (`cleanup`, `cli`, `consistency`, `core`,
  `creation`, `executor`, `link_validation`, `models`, `preflight`,
  `prescreening`, `prompts`, `remediation`, `reporting`, `review`,
  `scan`, `scoring`, `skills`, `utils`, `validation`).
- 447-test pytest suite at `tests/` (unit + integration + contract).
- `pyproject.toml` — `[project] name = "hermes-server"`,
  `[project.scripts] hermes-mcp = "mcp_server.server:main_sync"`.
  Distribution name distinguishes the project; `mcp_server` import
  path preserved.
- `VERSION` (`0.1.0`) and `FRAMEWORK_SPEC_VERSION` (`0.1.0`, matching
  `framework/VERSION`) — declares Hermes' own SemVer + the framework
  spec version it conforms to per D-0009.
- `prompts/` — 46 MCP prompt files (port-verbatim from legacy).
- `skills/` — `hermes/` (5 platform-specific skills), `personas/` (15
  files), `layer_aliases/`, `persona_mappings.yaml`.
- `agent-skills/spec-driven-development/` — `sdd-orchestrator` (180
  files) and `sdd-review-personas` (1 file) ported from the user's
  branch.
- `docs/` — `CHANGELOG/`, `architecture/`, `plans/`, `policies/`,
  `specs/` (80 files; `docs/migration/` dropped per audit).

### Changed

- Rewired the MCP server's scaffold + validation runtime to consume
  the framework's per-layer layout (`framework/layers/<NN>_<X>/`) per
  D-0013, closing the platform-template duplication: removed the
  `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`; rewrote
  `_default_ssd_root` to return `framework/layers`; corrected
  `_default_repo_root` parents count; rewrote
  `validation/runner.py:_resolve_canonical_template_root` as a
  3-stage precedence chain.
- Rewrote all `ucx_flow_v3` runtime coupling to point at `framework/`
  — 18 files in the edit set (4 code + 3 tests + 5 skills + 6
  architecture/spec docs), with sub-path repoints to `framework/registry/`
  and `framework/layers/<NN>_<X>/`. 11 historical-context docs
  preserved verbatim per the G13 rule (CHANGELOGs, ROADMAP retrospective,
  completed PLAN-* checklists).
- `.mcp.json` cwd repointed from `legacy/ucx_hermes/src` to
  `platforms/hermes/src`.
- Skill content rewired to `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`
  references; `skill_view` API example in `sdd-orchestrator/SKILL.md`
  rewritten as a direct-read instruction since templates now live
  outside the skill.

### Removed

- The 8 drifted layer template YAMLs at `agent-skills/spec-driven-
  development/sdd-orchestrator/templates/` per D-0013 — the framework's
  `framework/layers/<NN>_<X>/<X>-TEMPLATE.yaml` set is the single
  source of truth.
- 6 D-0013-obsolete sync files from the agent-skills package
  (`sync-ucx-templates.sh`, `sync.py`, `.sync-backlog.json`,
  `template-sync-procedure.md`, `template-v3-alignment-checklist.md`,
  `ucx-framework-quirks.md`).
- Legacy `templates/` directory at the platform root (dropped per
  D-0013; never ported from `legacy/ucx_hermes/`).
- `docs/migration/MIGRATION_FROM_MCP_UCX.md` from the port set —
  `mcp_ucx/` is the deprecated predecessor, archived in `legacy/`
  and slated for full removal at Phase 5 cutover.

> Full migration audit trail: project-level
> [`CHANGELOG.md [0.3.0]`](../../CHANGELOG.md) and
> [`plans/P2-T0-PLAN.md`](../../plans/P2-T0-PLAN.md) through P2-T9.
