# Migration TODO — Multi-Platform Restructure

Live task tracker for the migration. Phases mirror `ROADMAP.md`.
Status legend: `[ ]` open · `[~]` in progress · `[x]` done (committed + pushed).

| Field           | Value                                      |
|------------------|--------------------------------------------|
| Working branch   | `claude/multi-platform-migration-AamWB`    |
| Current phase    | Phase 2 — Platform A: Hermes re-homing     |
| Last updated     | 2026-05-20T16:20:00Z                       |

---

## Phase 0 — Planning & Scaffolding → `v0.1.0`

- [x] P0-T1 — Create working branch.
- [x] P0-T2 — Author `ROADMAP.md`, `CHANGELOG.md`, `docs/PROJECT.md`, `docs/REPO_STRUCTURE.md`.
- [x] P0-T3 — Establish `platforms/` directories.
- [x] P0-T4 — Create `plans/` workspace.
- [x] P0-T6 — Add `CLAUDE.md` project memory, development workflow, and
  continuity automation (`PreCompact` / `SessionStart` hooks).
- [x] P0-T5 — Tag planning baseline `v0.1.0` (published from a local clone at Phase 1 close).

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
- [x] P1-T8 — Phase 1 close: changelog cut, milestone tags `v0.1.0` /
  `framework/v0.1.0` / `v0.2.0` published. → `plans/P1-T8-PLAN.md`

## Phase 2 — Platform A: Hermes Re-homing → `v0.3.0`

- [x] P2-T0 — Phase 2 audit & task breakdown. Resolved that `mcp_ucx` is a
  deprecated predecessor (out of scope); Phase 2 input is the 280 files of
  `legacy/ucx_hermes/`. → `plans/P2-T0-PLAN.md` · `plans/P2-AUDIT-hermes.md`
- [x] P2-T1 — Design: five choices resolved; templates-single-source-of-truth
  (D-0013), `mcp_server` import kept with `hermes-server` distribution,
  two plain-text VERSION files, `hermes-mcp` script, mirror-legacy layout.
  → `plans/P2-T1-DESIGN.md`
- [x] P2-T2 — Port-verbatim: 64 files copied byte-identical into
  `platforms/hermes/` (`examples/`, `prompts/`, `skills/layer_aliases/`,
  `skills/personas/`, `skills/persona_mappings.yaml`). All seven verify
  gates green. → `plans/P2-T2-PLAN.md`
- [x] P2-T3 — Port-with-repoint: copied `pyproject.toml`, `src/` (63),
  `tests/` (47), `docs/` less `migration/` (80), `skills/README.md`,
  `skills/hermes/` (8); 200 files ported + 2 VERSION files. Path-map
  applied across 18 edit-list files (4 code + 3 test + 5 skills +
  6 current-behavior docs); 11 historical docs preserved verbatim
  per G13. `pyproject.toml` carries `hermes-server` / `0.1.0` /
  `hermes-mcp` per P2-T1 Q1+Q4. `VERSION` + `FRAMEWORK_SPEC_VERSION`
  both `0.1.0`. `.mcp.json` cwd repointed. Audit §3a renamed
  "Code-level + tests"; new §3c documentation cluster added.
  Conformance 25/25; Hermes tests 397/447 (50 D-0013 scaffold-gap
  failures deferred to P2-T9). DONE 2026-05-20T12:50:00Z.
- [x] P2-T8 — Dropped 8 layer YAMLs at `agent-skills/.../sdd-orchestrator/templates/`
  (skill drift: engine hardcodes like `server: ucx_hermes`, `SDD v3` labels);
  rewired 25 references (17 in `SKILL.md`, 8 in `sdd-workflow-quickstart.md`)
  from skill-relative `templates/0N_TYPE-TEMPLATE.yaml` to framework-relative
  `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`; rewrote `SKILL.md:692`'s
  `skill_view` API example to a direct-read instruction (templates now live
  outside the skill). Content-equivalence check confirmed all deltas were
  engine-hardcode-removal + phrasing; no substantive content lost.
  Conformance 25/25; D-0013 conformance for skill package complete.
  DONE 2026-05-20T13:55:00Z.
- [x] P2-T9 — Rewired MCP scaffold + validation runtime to consume
  `framework/layers/<NN>_<X>/`. Five edits across 3 files: removed the
  `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`; rewrote
  `_default_ssd_root` to return `framework/layers`; fixed
  `_default_repo_root` parents count (`[4]→[5]`, layout shifted post-
  P2-T3); rewrote `validation/runner.py:_resolve_canonical_template_root`
  as a 3-stage precedence chain (project-framework-override → scaffold
  output → canonical); updated `test_scaffold_init.py` fixtures. Hermes
  test suite 397/447 → **447/447**; conformance 25/25. Pass 3 retro
  records G16 (parents-count audit lesson) + G17 (cross-module path-
  computer audit lesson). DONE 2026-05-20T15:30:00Z.
- [x] P2-T5 — Phase 2 verify: ran 14 consolidated gates across
  conformance (25/25), Hermes own suite (447/447), coupling sweep
  (0 in current-behavior; whitelist matches exactly 11 historical),
  structure / VERSION files / smoke test / file inventory. **All gates
  green.** Verify record at `plans/P2-T5-VERIFY.md`. Phase 2
  structurally complete. DONE 2026-05-20T16:20:00Z.
- [ ] P2-T6 — Phase 2 close: `CHANGELOG.md [0.3.0]`; ROADMAP marked;
  milestone tag `v0.3.0`; platform tag `hermes/v0.1.0` (per
  `docs/TAGGING.md`). Anticipate same HTTP 403 on tag pushes (P1-T8
  pattern); bake local-clone push commands into the plan.
- [x] P2-T7 — Port `hermes_agent_skills/spec-driven-development/` from
  `origin/main` to `platforms/hermes/agent-skills/spec-driven-development/`
  (sdd-orchestrator + sdd-review-personas). 181 files (was 187; 6 D-0013-
  obsolete sync files deleted). Zero `ucx_flow|UCX_FLOW` hits. Audit §5b
  updated; conformance 25/25. → `plans/P2-T7-PLAN.md`

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
