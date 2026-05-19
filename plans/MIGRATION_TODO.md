# Migration TODO — Multi-Platform Restructure

Live task tracker for the migration. Phases mirror `ROADMAP.md`.
Status legend: `[ ]` open · `[~]` in progress · `[x]` done (committed + pushed).

| Field           | Value                                      |
|------------------|--------------------------------------------|
| Working branch   | `claude/multi-platform-migration-AamWB`    |
| Current phase    | Phase 1 — Framework Spec Extraction        |
| Last updated     | 2026-05-19T10:45:00Z                       |

---

## Phase 0 — Planning & Scaffolding → `v0.1.0`

- [x] P0-T1 — Create working branch.
- [x] P0-T2 — Author `ROADMAP.md`, `CHANGELOG.md`, `docs/PROJECT.md`, `docs/REPO_STRUCTURE.md`.
- [x] P0-T3 — Establish `platforms/` directories.
- [x] P0-T4 — Create `plans/` workspace.
- [x] P0-T6 — Add `CLAUDE.md` project memory, development workflow, and
  continuity automation (`PreCompact` / `SessionStart` hooks).
- [x] P0-T5 — Tag planning baseline `v0.1.0` (pushed at Phase 1 close, P1-T8).

## Phase 1 — Framework Spec Extraction → `v0.2.0`

- [x] P1-T0 — Legacy isolation: move pre-migration content into `legacy/`; disable legacy CI.
- [x] P1-T1 — Audit `legacy/ucx_flow_v3/` — list engine-agnostic vs. engine-specific content. → `plans/P1-AUDIT-ucx_flow_v3.md`
- [x] P1-T2 — Extract the 8 SDD layers into `framework/layers/` (templates,
  READMEs, index templates — 24 files). → `plans/P1-T2-PLAN.md`
- [x] P1-T3 — Extract `LAYER_REGISTRY.yaml` into `framework/registry/`. → `plans/P1-T3-PLAN.md`
- [x] P1-T4 — Extract governance + CHG overlay into `framework/governance/`
  (18 files). → `plans/P1-T4-PLAN.md`
- [x] P1-T5 — Define the shared conformance suite under `tests/conformance/`
  (22 tests, framework self-consistency). → `plans/P1-T5-PLAN.md`
- [x] P1-T6 — Create `framework/VERSION` (`0.1.0`) + the tag-namespace
  convention (`docs/PROJECT.md` §3, D-0009). → `plans/P1-T6-PLAN.md`
- [x] P1-T7 — Framework root assembly: the 4 methodology docs
  (`SPEC_DRIVEN_DEVELOPMENT_GUIDE`, `QUICK_REFERENCE`, `AI_ASSISTANT_RULES`,
  `TESTING_STRATEGY_TDD`) extracted into `framework/`. → `plans/P1-T7-PLAN.md`
- [x] P1-T8 — Phase 1 close: changelog cut, milestone tags `framework/v0.1.0`
  + `v0.2.0`, `v0.1.0` pushed. → `plans/P1-T8-PLAN.md`

## Phase 2 — Platform A: Hermes Re-homing → `v0.3.0`

- [ ] P2-T1 — Copy `legacy/ucx_hermes/` + `legacy/mcp_ucx/` into `platforms/hermes/`.
- [ ] P2-T2 — Repoint Hermes at `framework/`; declare `framework_spec_version`.
- [ ] P2-T3 — Update `.mcp.json` to the new Hermes path.
- [ ] P2-T4 — Hermes passes the conformance suite.

## Phase 3 — Platform B: Claude Code Plugin → `v0.4.0`

- [ ] P3-T1 — Scaffold `.claude-plugin/plugin.json`.
- [ ] P3-T2 — Port the `doc-*` skill set into the plugin.
- [ ] P3-T3 — Port commands and agents into the plugin.
- [ ] P3-T4 — Remove all Hermes/MCP dependency from the plugin path.
- [ ] P3-T5 — Plugin passes the conformance suite.

## Phase 4 — Conformance & Independence → `v0.5.0`

- [ ] P4-T1 — Both platforms green on the shared conformance suite.
- [ ] P4-T2 — Per-platform `CHANGELOG.md` and CI.
- [ ] P4-T3 — Parity report: feature gaps between platforms.

## Phase 5 — Cutover → `v1.0.0`

- [ ] P5-T1 — New project replaces `main`.
- [ ] P5-T2 — Remove `legacy/` (or archive per final decision).
- [ ] P5-T3 — Tag `v1.0.0`; platforms tag first stable releases.

---

## Deferred / Post-Migration

- [ ] CHG-D1 — Re-introduce change management as skills + CI/CD (see `ROADMAP.md`).
- [ ] CHG-D2 — Record CHG decision formally in `framework/governance/`.
- [ ] INFRA-1 — Refresh stale `.github/` metadata (CODEOWNERS, dependabot, labeler) for the new layout.
