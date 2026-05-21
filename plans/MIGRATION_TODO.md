# Migration TODO — Multi-Platform Restructure

Live task tracker for the migration. Phases mirror `ROADMAP.md`.
Status legend: `[ ]` open · `[~]` in progress · `[x]` done (committed + pushed).

| Field           | Value                                      |
|------------------|--------------------------------------------|
| Working branch   | `claude/multi-platform-migration-AamWB`    |
| Current phase    | Phase 2 — Platform A: Hermes re-homing     |
| Last updated     | 2026-05-21T06:30:00Z                       |

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
- [x] P2-T6 — Phase 2 close: `CHANGELOG.md [0.3.0]` (Phase 2 cycle —
  Added / Changed / Removed); `ROADMAP.md` line 6 + Phase 2 section
  marked complete; `docs/TAGGING.md` table appended. Annotated tags
  `v0.3.0` (milestone) and `hermes/v0.1.0` (platform) created locally
  on close commit `20c061d` and **published on the remote via the
  local-clone workaround** (P1-T8 pattern). All 5 tags now on origin.
  **Phase 2 formally closed.** DONE 2026-05-20T17:25:00Z.
- [x] P2-T7 — Port `hermes_agent_skills/spec-driven-development/` from
  `origin/main` to `platforms/hermes/agent-skills/spec-driven-development/`
  (sdd-orchestrator + sdd-review-personas). 181 files (was 187; 6 D-0013-
  obsolete sync files deleted). Zero `ucx_flow|UCX_FLOW` hits. Audit §5b
  updated; conformance 25/25. → `plans/P2-T7-PLAN.md`

## Phase 3 — Platform B: Claude Code Plugin → `v0.4.0`

- [x] P3-T0 — Phase 3 audit + task breakdown: inventoried `.claude/`
  (191 files; 149 skills = 129 `doc-*` + 20 non-doc; 1 agent;
  1 command; 3 dropped hooks). Coupling sweep: zero
  `ucx_flow|UCX_FLOW|ucx_hermes`; 30 files carry `ai_dev_flow`
  placeholder paths to rewire to `framework/`; 2 illustration paths
  preserved per G13. Relationship resolved: **copy-with-divergence**
  (root `.claude/` stays in dev-time service until Phase 5 cutover).
  Phase 3 shape: 5 sub-tasks (T1 design → T2 port → T3 scaffold →
  T4 verify → T5 close). 6 open questions for P3-T1 design.
  See `plans/P3-T0-PLAN.md` + `plans/P3-AUDIT-claude-code-plugin.md`.
  DONE 2026-05-20T18:35:00Z.
- [x] P3-T1 — Design (paper-only): 7 questions resolved in
  `plans/P3-T1-DESIGN.md`. Plugin manifest = minimal (auto-discovery
  handles skills/agents/commands; verified via claude-code-guide
  agent). Non-doc skill scope: 13 IN (10 clearly + 3 borderline:
  `test-automation`, `security-audit`, `contract-tester`); 7 OUT
  (2 clearly + 5 borderline general-purpose). `save-plan` command:
  IN (generic plan-save utility, not migration-specific). 22 root
  files under `.claude/skills/`: 19 IN, 3 OUT (`README.md` plus
  `google-adk`/`n8n` quickrefs). Plugin name: **`aidoc-flow`**.
  Copy strategy: `cp -r` per top-level path + explicit `rm -rf` of
  OUT entries (3-stage recipe). No lifecycle hooks in v0.1.0.
  **Plugin skill total: 142.** Pass 2 caught a Pass 1 counting error
  (corrected from 144 to 142). DONE 2026-05-20T19:10:00Z.
- [x] P3-T2 — Port content: 3-stage `cp -r` recipe copied 142 skills
  + 19 root files + 1 agent + 1 command from `.claude/` to
  `platforms/claude-code-plugin/` (162 total + 6 nested skill files =
  168 total). 7 OUT skill dirs + 3 OUT root files dropped. Basic sed
  cleared 211 line hits of `ai_dev_flow` across 30 source files.
  Class B sub-path correction (5 layer dirs → `framework/layers/`)
  landed 6 refs across 3 files. Class C (ID_NAMING_STANDARDS) landed
  13 refs in `framework/governance/`. `/opt/data/ucx_framework`
  targeted edit cleared 1 ref. G13 illustration paths preserved.
  All 11 verify gates green; conformance 25/25 unaffected. Pass 3
  retro records G17 (sed delimiter collision — corrected mid-flight
  from `|` to `#`) and G18 (Class D stale-reference set sized: ~150
  line hits across 30 stale segments; top item `framework/scripts/`
  with 60 refs; resolution deferred to a content-migration task per
  P3-T1 §Deferred R2). DONE 2026-05-20T20:20:00Z.
- [x] P3-T3 — Plugin scaffold: `.claude-plugin/plugin.json` (minimal
  manifest — 7 fields: `name`, `description`, `version`, `license`,
  `repository`, `homepage`, `keywords`; **author block omitted**
  because in-container `git config user.name` returned `Claude`, not
  the repo owner — recorded as Finding 1 / G10 lesson). `VERSION`
  (`0.1.0`, 6 bytes) + `FRAMEWORK_SPEC_VERSION` (`0.1.0`, identical
  to `framework/VERSION`). `README.md` expanded from 27-line
  placeholder to 82-line user-facing doc (skills table, install,
  use, spec conformance, info table, Hermes-relationship section).
  **No `CHANGELOG.md`** — followed Hermes precedent (Finding 2);
  symmetric retrofit deferred. All 11 verify gates green.
  DONE 2026-05-20T21:10:00Z.
- [x] P3-T4 — Phase 3 verify: ran 22 consolidated gates across
  conformance (25/25), structure, content + coupling (zero Hermes
  refs, zero `ai_dev_flow`, sub-path corrections landed, G13
  illustration paths preserved), manifest validity + name + versions,
  integration checks (file inventory, content equivalence,
  auto-discovery sanity, source-unchanged, Hermes unaffected). Mid-
  flight cleanup removed **47 broken symlinks** the source `.claude/`
  carried (G18 finding); post-cleanup plugin file count is 171 =
  git = disk. **All gates green.** Verify record at
  `plans/P3-T4-VERIFY.md`. DONE 2026-05-20T21:55:00Z.
- [x] P3-T5 — Phase 3 close: `CHANGELOG.md [0.4.0]` (Phase 3 cycle
  — Added / Changed / Removed; carried known-issue note for ~150
  Class D stale refs); `ROADMAP.md` line 6 + Phase 3 section marked
  complete; `docs/TAGGING.md` table appended (7 rows). Annotated
  tags `v0.4.0` (milestone) and `claude-code-plugin/v0.1.0` (platform)
  created locally on close commit `087f7d5` and **published on the
  remote via the local-clone workaround** (third occurrence — P1-T8,
  P2-T6, P3-T5). All 7 tags now on origin. **Phase 3 formally
  closed.** DONE 2026-05-20T22:55:00Z.

## Phase 4 — Conformance & Independence → `v0.5.0`

- [x] P4-T0 — Phase 4 audit + task breakdown: assessed platform-
  conformance contract (4 bullets — PC1+PC4 statically testable
  today, PC2+PC3 deferred to runtime exercise); CI gap (no
  `.github/workflows/`; 3 greenfield workflows planned);
  CHANGELOG/README/LICENSE gaps (both platforms lack CHANGELOG,
  Hermes README still placeholder, no repo-root LICENSE); parity
  report scope (layers × operations matrix). Rolled up 9 deferred
  items from P1/P2/P3 — **5 in-scope** (per-platform CHANGELOG ×2,
  LICENSE, Hermes README, conformance-suite extension), **4
  deferred** (content-design / already-done). Phase 4 shape: 5
  sub-tasks (T1 design → T2 conformance tests → T3 CI → T4
  retrofits+parity → T5 verify+close). 6 open questions. See
  `plans/P4-T0-PLAN.md` + `plans/P4-AUDIT-conformance.md`.
  DONE 2026-05-20T23:45:00Z.
- [x] P4-T1 — Design (paper-only): 6 questions resolved in
  `plans/P4-T1-DESIGN.md`. Test-module placement: new sub-package
  `tests/conformance/platforms/` (`test_version_declaration.py`
  + `test_engine_isolation.py`); suite grows 25 → 28-30. PC4
  scope: **runtime-significant directories** (`src/`,
  `pyproject.toml`, `.claude-plugin/`, `commands/`, `agents/`);
  prose / READMEs / `skills/<X>/SKILL.md` documentary references
  allowed. Forbidden-token tables specified bidirectionally
  (case-insensitive). CI runner: `ubuntu-latest`; Python 3.12 via
  `actions/setup-python@v5`; no carry-over from legacy. CHANGELOG
  retrofit: **minimal-honest** (each platform's `[0.1.0]` mirrors
  the corresponding project release scoped to that platform).
  Hermes README: **full mirror** of P3-T3 plugin README. LICENSE:
  **MIT** (matches plugin manifest placeholder); copyright holder
  `vladm3105` (matches GitHub repo owner). Q7 confirmed no
  framework tag bump (spec unchanged). DONE 2026-05-21T00:35:00Z.
- [x] P4-T2 — Platform conformance tests: new sub-package
  `tests/conformance/platforms/` with `__init__.py`,
  `test_version_declaration.py` (4 tests: PC1 declaration —
  VERSION file exists, FRAMEWORK_SPEC_VERSION file exists, both are
  bare SemVer, declared version matches `framework/VERSION`), and
  `test_engine_isolation.py` (2 tests: PC4 — Hermes runtime
  surface no plugin-engine tokens, plugin runtime surface no
  Hermes-engine tokens; case-insensitive forbidden-token scan
  scoped to runtime-significant directories per P4-T1 Q2).
  `_spec.py` extended additively with platform helpers. Suite:
  **25 → 31 tests**, all green on first run after fixing one
  implementation-time silent-Edit failure. DONE 2026-05-21T01:20:00Z.
- [x] P4-T3 — CI workflows authored (greenfield, ubuntu-latest,
  Python 3.12 via setup-python@v5, concurrency cancel-in-progress,
  minimal `contents: read`): `conformance.yml` (31-test suite on
  every push/PR), `hermes.yml` (pytest on platforms/hermes/** or
  framework/**), `plugin.yml` (manifest valid + coupling sweep +
  structural sanity on platforms/claude-code-plugin/**). All 8
  verify gates green (YAML valid; local smoke OK). **In-container
  push rejected** ("refusing to allow GitHub App to create workflow
  without workflows permission" — fifth in-container restriction).
  Workflows staged at `plans/workflows-pending/` for user to
  `git mv` into `.github/workflows/` from a local clone (see
  `plans/P4-T3-PLAN.md` Implementation note for exact commands).
  DONE 2026-05-21T02:15:00Z (pending workflow file relocation by user).
- [x] P4-T4 — Retrofits + parity report: 6 artifacts landed —
  `platforms/hermes/CHANGELOG.md` + `platforms/claude-code-plugin/CHANGELOG.md`
  (each a per-platform `[0.1.0]` mirroring the corresponding
  project release scoped to that platform, per P4-T1 Q4 minimal-
  honest posture); `platforms/hermes/README.md` expanded 27 → 113
  lines (full mirror of P3-T3 plugin README structure per Q5);
  repo-root `LICENSE` (MIT, copyright `vladm3105` per Q6, matches
  plugin manifest placeholder); `docs/PARITY.md` (5-section
  capability comparison with known-parity-gap call-out on the
  legacy-vs-new layer model); `docs/TAGGING.md` extended with an
  "In-container push restrictions" section documenting the tags
  + workflows restriction symmetrically. All 9 verify gates green;
  conformance still 31/31. DONE 2026-05-21T03:10:00Z.
- [x] P4-T5 — Phase 4 verify + close (combined): 13 verify gates
  ran green (conformance 31/31, deliverables present, cross-platform
  sanity, scope discipline). Carried-known-issue surfaced:
  `api_runner.py:115` has stale install instruction
  (`pip install 'ucx_hermes[api]'`; correct is
  `hermes-server[api]`) — 1-line fix deferred to Phase 5
  housekeeping or `hermes/v0.1.1` patch per R5 scope. Close
  commit `954d8da` shipped; `CHANGELOG.md [0.5.0]` cut covering
  the full Phase 4 cycle (Added / Changed / Known carried issues);
  ROADMAP Phase 4 marked complete; `docs/TAGGING.md` table grew
  to 8 rows. Annotated tag `v0.5.0` created locally on the close
  commit; in-container tag push 403'd as expected (4th occurrence
  — P1-T8, P2-T6, P3-T5, P4-T5). Verify record at
  `plans/P4-T5-VERIFY.md`. **Phase 4 formally closed** —
  `v0.5.0` published on the remote (8 tags total; `v0.5.0^{}` →
  `954d8da`). DONE 2026-05-21T04:30:00Z.

## Phase 5 — Cutover → `v1.0.0`

- [x] P5-T0 — Cutover audit + task breakdown: inventoried the two
  destructive removal targets (`legacy/` 28M/2275 files; root
  `.claude/` dev-time loader) and confirmed **no runtime dependency**
  from the surviving tree on either (framework/ + tests/ + .mcp.json
  clean; the few hits are documentary or already-known stale refs).
  Classified every cutover operation by reversibility × authority —
  `main` replacement + all tag pushes are **user-only**. Carried-
  issue disposition: ship `v1.0.0` with the documented plugin
  layer-model gap (post-v1.0 content fix); `api_runner.py` already
  fixed. 6-task breakdown (T1 design → T2 remove legacy → T4
  finalize docs → T3 remove .claude/ → T5 verify → T6 close+cutover);
  destructive tasks carry confirmation gates. 6 open questions for
  P5-T1. See `plans/P5-T0-PLAN.md` + `plans/P5-AUDIT-cutover.md`.
  DONE 2026-05-21T05:35:00Z.
- [x] P5-T1 — Design (paper-only): 6 decisions in `plans/P5-T1-DESIGN.md`.
  **Q1 main-replacement: force-replace** (histories diverged — FF
  impossible; old main is the protected archive branch, so lossless;
  user-authorized). **Q2 framework: stays `0.1.0`** (no spec change;
  earns 1.0.0 later under post-cutover CHG). **Q3 plugin gap: not a
  blocker** — ship v1.0.0 with the documented gap. **Q4 tags: project
  `v1.0.0` only**; components independent (optional `hermes/v0.1.1`
  for the api_runner fix; plugin stays `0.1.0`; framework `0.1.0`) —
  flagged as the most-likely-override (vs a unified-1.0 launch).
  **Q5 plans/: keep in-tree** (audit trail). **Q6 CLAUDE.md: rewrite**
  to post-migration memory (root file; survives the `.claude/`
  removal). DONE 2026-05-21T06:30:00Z.
- [ ] P5-T2 — Remove `legacy/` (**restored**, D-0014 archive-then-clean):
  `git rm -r legacy/`. Destructive — confirmation gate at execution;
  precondition (archive branch `legacy-ucx-v3.2-read-only` exists +
  protected) **met**. Verify no runtime dependency; conformance 31/31.
- [ ] P5-T3 — Remove root `.claude/` (**restored**, D-0014): `git rm -r
  .claude/`. Destructive + session-affecting — confirmation gate;
  sequenced LATE (disables this session's hooks). Migration-era
  `.claude/` survives in git history; archive holds pre-migration
  `.claude/`. CLAUDE.md (root file) survives + is rewritten in P5-T4.
- [ ] P5-T4 — Finalize project docs (README, REPO_STRUCTURE, PROJECT,
  ROADMAP, CLAUDE.md) — incl. reconciling the legacy-removal language
  to name the `legacy-ucx-v3.2-read-only` archive branch.
- [ ] P5-T5 — Verify (consolidated final gate; `plans/P5-T5-VERIFY.md`).
- [ ] P5-T6 — Close + cutover: `CHANGELOG.md [1.0.0]`; tags `v1.0.0`
  + platform stables (user local-clone); **`main` replacement
  (user-authorized)**.

---

## Deferred / Post-Migration

- [ ] CHG-D1 — Re-introduce change management as skills + CI/CD (see `ROADMAP.md`).
- [ ] CHG-D2 — Record CHG decision formally in `framework/governance/`.
- [ ] INFRA-1 — Refresh stale `.github/` metadata (CODEOWNERS, dependabot, labeler) for the new layout.
