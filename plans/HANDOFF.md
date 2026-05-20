# Session Handoff

Continuity record across ephemeral sessions. Read this first each session;
refresh it at milestones and **before any context compaction**.
Timestamps are ISO 8601 UTC (`YYYY-MM-DDThh:mm:ssZ`).

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Last updated  | 2026-05-20T18:35:00Z                       |
| Working branch| `claude/multi-platform-migration-AamWB`    |
| Current phase | Phase 3 — Platform B: Claude Code plugin (P3-T0 done) |
| Next task     | P3-T1 — design (resolve the 6 open questions from P3-T0 audit: manifest schema, non-doc-skill scope, save-plan in/out, root-files scope, plugin name, copy strategy) |

## Progress

- Phase 0 (Planning & Scaffolding) — complete.
- Phase 1 Step 0 (P1-T0, legacy isolation) — complete.
- P1-T1 (audit of `legacy/ucx_flow_v3/`) — complete; see
  `plans/P1-AUDIT-ucx_flow_v3.md`.
- P1-T2 (layer extraction) — complete; `framework/layers/` holds 24 files;
  see `plans/P1-T2-PLAN.md`.
- P1-T3 (registry extraction) — complete; `framework/registry/` holds
  `LAYER_REGISTRY.yaml` + `README.md`; see `plans/P1-T3-PLAN.md`.
- P1-T4 (governance + CHG extraction) — complete; `framework/governance/`
  holds 18 files; see `plans/P1-T4-PLAN.md`.
- P1-T5 (shared conformance suite) — complete; `tests/conformance/` holds the
  helper + 4 test modules (22 tests, all green); see `plans/P1-T5-PLAN.md`.
  The engine-agnostic `framework/README.md` was written here (pulled forward
  from P1-T7).
- P1-T6 (`framework/VERSION` + tag convention) — complete; `framework/VERSION`
  at `0.1.0`, tag namespaces in `docs/PROJECT.md` §3, suite at 24 tests; see
  `plans/P1-T6-PLAN.md`. The `framework/v0.1.0` git tag is deferred to Phase 1
  close (D-0009, tracked as P1-T8).
- P1-T7 (framework root assembly) — complete; the 4 methodology docs extracted
  into `framework/`; suite at 25 tests; see `plans/P1-T7-PLAN.md`.
  **`framework/` is now fully assembled.**
- P1-T8 (Phase 1 close) — **complete.** Changelog cut into `[0.1.0]` /
  `[0.2.0]`, ROADMAP marked, and the three annotated tags (`v0.1.0`,
  `framework/v0.1.0`, `v0.2.0`) published to the remote (pushed from a local
  clone after the in-container tag push was blocked by the git proxy). See
  `plans/P1-T8-PLAN.md`. **Phase 1 complete.**
- P2-T0 (Phase 2 audit & task breakdown) — **complete.** Paper-only audit
  resolved that `mcp_ucx` is the deprecated predecessor of `ucx_hermes` and
  is out of Phase 2 scope; Phase 2 input is 280 files. Mapped 4 code-level +
  prose-level framework-coupling sites; defined the audit-confirmed P2-T1…T6
  breakdown. See `plans/P2-T0-PLAN.md` / `plans/P2-AUDIT-hermes.md`.
- P2-T1 (Hermes design) — **complete.** Five design choices resolved
  (`plans/P2-T1-DESIGN.md`): keep `mcp_server` import path with
  `hermes-server` distribution (Q1 — Platform B is JS/MD, no Python
  collision); two plain-text VERSION files for spec declaration (Q2);
  **drop platform `templates/` — consume `framework/layers/`** (Q3, D-0013);
  `hermes-mcp` script entry (Q4); mirror legacy layout minus dropped
  paths (Q5). D-0013 logs the templates-source-of-truth decision.
- P2-T2 (port-verbatim) — **complete.** 64 files copied byte-identical
  from `legacy/ucx_hermes/` to `platforms/hermes/`: `examples/` (1),
  `prompts/` (46), `skills/layer_aliases/` (1), `skills/personas/` (15),
  `skills/persona_mappings.yaml` (1). All seven verify gates green —
  `diff -r` identical on every path, no `ucx_flow` references in the
  copied targets, expected-absent paths still absent, conformance suite
  25/25. → `plans/P2-T2-PLAN.md`.

## Achievements

- 2026-05-18 — Isolated the pre-migration project into `legacy/` (frozen);
  disabled legacy CI; rewrote root `README.md`; repointed `.mcp.json`.
- 2026-05-18 — Added `plans/` workspace, root `CLAUDE.md`, `DECISIONS.md`,
  and `PreCompact` / `SessionStart` continuity hooks.
- 2026-05-18 — Audited `legacy/ucx_flow_v3/` (49 files); resolved P1 open
  questions (D-0005 index templates, D-0006 `framework/` v0.1.0).
- 2026-05-18 — Added the two-pass plan-review gate (D-0007): `CLAUDE.md`
  rule, `plans/PLAN-TEMPLATE.md`, `PreToolUse(git commit)` warning hook.
- 2026-05-18 — Extracted the 8 SDD layers into `framework/layers/`
  (templates, READMEs, index templates — engine-neutral).
- 2026-05-18 — Extracted `LAYER_REGISTRY.yaml` into `framework/registry/`
  as the authoritative machine-readable layer model.
- 2026-05-18 — Extracted governance docs + CHG overlay into
  `framework/governance/` (18 files, engine-neutral; CHG spec-only).
- 2026-05-18 — Built the shared conformance suite (`tests/conformance/`,
  22 tests) and wrote the engine-agnostic `framework/README.md`.
- 2026-05-19 — Created `framework/VERSION` (`0.1.0`) and the tag-namespace
  convention (D-0009); conformance suite at 24 tests.
- 2026-05-19 — Extracted the 4 methodology docs into `framework/`;
  `framework/` fully assembled; conformance suite at 25 tests.
- 2026-05-19 — Closed Phase 1: changelog cut + ROADMAP marked; release tags
  `v0.1.0`, `framework/v0.1.0`, `v0.2.0` published to the remote.
- 2026-05-19 — Added `docs/TAGGING.md` tagging policy (release + bookmark
  tags, D-0011).
- 2026-05-19 — Defined the framework's purpose: the IPLAN is the terminal
  product; code/deploy out of scope; v1 = software/devops; domain profiles
  post-v1.0 (D-0012, `ROADMAP.md`).
- 2026-05-19 — Completed P2-T0 (Phase 2 audit & task breakdown):
  `legacy/mcp_ucx/` confirmed out of scope; Phase 2 input is 280 files;
  coupling sites mapped; P2-T1…T6 defined.
- 2026-05-19 — Completed P2-T1 (Hermes design): five design choices
  resolved; D-0013 records the templates-single-source-of-truth rule
  (platforms consume `framework/layers/`, never duplicate).
- 2026-05-20 — Completed P2-T2 (port-verbatim): 64 files copied
  byte-identical into `platforms/hermes/`; verify gates all green.
- 2026-05-20 — Completed P2-T7 (port `hermes_agent_skills/` from main):
  181 files (was 187; 6 D-0013-obsolete sync files deleted) at
  `platforms/hermes/agent-skills/spec-driven-development/`; zero
  `ucx_flow|UCX_FLOW` hits; audit §5b updated; two plan deviations
  documented as Pass 3 retro (G11 deletion vs deprecation, G13 `/opt/data`
  verify softening).
- 2026-05-20 — Completed P2-T3 (port-with-repoint): 200 files +
  VERSION/FRAMEWORK_SPEC_VERSION ported; pyproject migrated to
  `hermes-server` / `0.1.0` / `hermes-mcp` (P2-T1 Q1+Q4); path-map
  rewrote all current-behavior `ucx_flow_v3` references in 18 files;
  11 historical docs preserved verbatim per G13; audit §3a/§3c
  refreshed; .mcp.json repointed. Conformance 25/25; Hermes' own
  suite 397/447 (50 failures from D-0013 scaffold-runtime gap →
  deferred to new P2-T9 task).
- 2026-05-20 — Completed P2-T8 (drop skill's templates duplication):
  deleted 8 drifted layer YAMLs at `agent-skills/.../sdd-orchestrator/
  templates/`; rewired 25 references in `SKILL.md` +
  `sdd-workflow-quickstart.md` to `framework/layers/0N_TYPE/
  TYPE-TEMPLATE.yaml`; rewrote line-692 `skill_view` example to a
  direct-read instruction. Content-equivalence check confirmed deltas
  were engine-hardcode + phrasing — no substantive content lost.
  D-0013 conformance for the skill package complete. Pass 3 retro
  records G17 (verify gate V6 was too coarse — corrected to scope
  the grep to `skill_view.*templates/`).
- 2026-05-20 — Completed P2-T9 (rewire MCP scaffold + validation
  runtime to `framework/layers/`): removed the `templates/` row from
  `CANONICAL_SCAFFOLD_MAPPINGS`; rewrote `_default_ssd_root` to
  `framework/layers`; fixed `_default_repo_root` parents count
  (`[4]→[5]` — layout shifted in P2-T3); rewrote
  `validation/runner.py:_resolve_canonical_template_root` as a
  3-stage precedence chain (override → scaffold output → canonical);
  cleaned up test fixtures. **Hermes test suite 397/447 → 447/447;
  conformance 25/25.** Pass 3 retro records G16 (parents-count audit
  lesson) + G17 (cross-module path-computer audit lesson). The 50
  P2-T3-deferred failures are all closed; D-0013 conformance for
  the MCP server complete.
- 2026-05-20 — Completed P2-T5 (Phase 2 verify): ran 14 consolidated
  gates — conformance 25/25, Hermes 447/447, zero coupling in
  current-behavior content, docs whitelist exact-match (11 files),
  VERSION files match `framework/VERSION`, smoke test scaffolds 71
  files end-to-end. Audit math reconciled (440 = 439 + 1 P0-scaffolded
  README). Verify record landed at `plans/P2-T5-VERIFY.md`. Phase 2
  is structurally complete; P2-T6 may cut the changelog and tags.
- 2026-05-20 — Completed P2-T6 (Phase 2 close): `CHANGELOG.md` cut to
  `[0.3.0] — 2026-05-20` (full Phase 2 cycle: Added / Changed /
  Removed, folding the 4 pre-existing `[Unreleased]` items);
  `ROADMAP.md` status `Phase 2 complete (v0.3.0) — Phase 3 next`;
  Phase 2 section ends with `Status: complete (v0.3.0,
  hermes/v0.1.0)`; `docs/TAGGING.md` table appended with the 2 new
  tag rows. Close commit `20c061d` pushed to the working branch.
  Annotated tags `v0.3.0` + `hermes/v0.1.0` created locally on
  `20c061d`; tag push 403'd as expected (P1-T8 pattern). Tag
  publication requires the user to run the local-clone workaround
  documented in `plans/P2-T6-PLAN.md` Implementation note. **Phase 2
  is structurally closed.**
- 2026-05-20T17:25:00Z — User published the two Phase 2 tags via the
  local-clone workaround. `git ls-remote --tags origin` now returns
  all 5 tags; `v0.3.0` and `hermes/v0.1.0` both dereference to the
  close commit `20c061d`. **Phase 2 is formally closed.** Next: Phase 3
  (Platform B — Claude Code plugin).
- 2026-05-20T18:35:00Z — Completed P3-T0 (Phase 3 audit + task
  breakdown). `plans/P3-AUDIT-claude-code-plugin.md` inventories
  `.claude/` (191 files), resolves the **copy-with-divergence**
  relationship (root stays in dev-time service until Phase 5), maps
  framework coupling to a single uniform rewire (`ai_dev_flow` →
  `framework` across 30 files), and classifies every top-level path.
  Phase 3 shape is 5 sub-tasks (T1–T5) — simpler than P2's 9 because
  coupling is small, no predecessor noise (no `mcp_ucx`-style tree),
  and the artifact is declarative (no Python package or test suite).
  6 open questions for P3-T1 design; see `plans/P3-T0-PLAN.md` for
  the full breakdown.

## Next steps

1. **P3-T1 — Design.** Resolve the 6 open questions surfaced by the
   P3-T0 audit (`plans/P3-AUDIT-claude-code-plugin.md` §6): plugin
   manifest schema; the 6 borderline non-doc skills (`code-review`,
   `refactor-flow`, `test-automation`, `security-audit`,
   `contract-tester`, `analytics-flow`, `devops-flow`, `ai-pr-review`);
   `save-plan` command in/out; the 22 root files under
   `.claude/skills/`; plugin name in the manifest; copy strategy;
   optional plugin lifecycle hooks. Output:
   `plans/P3-T1-DESIGN.md` per the P2-T1 pattern.
2. Then P3-T2 (port content with `ai_dev_flow → framework` rewire),
   P3-T3 (plugin scaffold + manifest + VERSION files), P3-T4 (verify),
   P3-T5 (Phase 3 close → `v0.4.0`, `claude-code-plugin/v0.1.0`).

## Open questions

- None outstanding.

## Log

- 2026-05-18T00:00:00Z — Handoff record created.
- 2026-05-18T17:27:00Z — Added decision log + continuity hooks.
- 2026-05-18T17:45:00Z — Completed P1-T1 audit of `legacy/ucx_flow_v3/`.
- 2026-05-18T18:45:00Z — Added two-pass plan-review gate (D-0007).
- 2026-05-18T19:05:00Z — Completed P1-T2 layer extraction.
- 2026-05-18T19:40:00Z — Completed P1-T3 registry extraction.
- 2026-05-18T20:30:00Z — Completed P1-T4 governance + CHG extraction.
- 2026-05-18T21:25:00Z — Completed P1-T5 conformance suite; wrote
  `framework/README.md`.
- 2026-05-19T09:20:00Z — Completed P1-T6 `framework/VERSION` + tag convention.
- 2026-05-19T10:00:00Z — Completed P1-T7 root assembly; `framework/` fully
  assembled.
- 2026-05-19T10:45:00Z — P1-T8 Phase 1 close commit; release tags created
  locally.
- 2026-05-19T11:35:00Z — Tag push blocked (HTTP 403, `refs/tags/*`); added
  `docs/TAGGING.md`; corrected records — P1-T8/P0-T5 reopened.
- 2026-05-19T12:45:00Z — Recorded framework purpose + domain-profile
  direction (D-0012); project name set to `aidoc-flow`.
- 2026-05-19T13:10:00Z — Added D-0012 refinements R1 (IPLAN planned/executed
  states; criticality-scaled audit) and R2 (curated corpus as the unit of
  value; library/composition/freshness as post-v1.0 destination).
- 2026-05-19T13:50:00Z — Release tags `v0.1.0`, `framework/v0.1.0`, `v0.2.0`
  published from a local clone; Phase 1 closed; P0-T5 and P1-T8 done.
- 2026-05-19T14:25:00Z — Completed P2-T0 audit; mcp_ucx out of scope; P2-T1…T6
  defined and queued in `MIGRATION_TODO.md`.
- 2026-05-19T14:55:00Z — Completed P2-T1 design; D-0013 records the
  templates-single-source-of-truth rule.
- 2026-05-20T09:10:00Z — Completed P2-T2 port-verbatim copy (64 files,
  all verify gates green).
- 2026-05-20T09:25:00Z — P2-T0 audit scope-completeness correction (§5b):
  3 legacy-root Hermes files added to P2-T3 scope (`HERMES_UCX_RUNTIME_ENVIRONMENT.md`,
  `MULTI_PROJECT_QUICK_REFERENCE.md`, `MULTI_PROJECT_SETUP_GUIDE.md`);
  4 others classified drop / out-of-scope; Pass 4 retro recorded.
- 2026-05-20T10:15:00Z — Completed P2-T7: ported `hermes_agent_skills/`
  (181 files) into `platforms/hermes/agent-skills/`; §5b updated so the
  3 root-docs files are sourced via P2-T7, not double-ported via P2-T3;
  P2-T7 Pass 3 retro records implementation-time deviations.
- 2026-05-20T10:45:00Z — Remaining-tasks review: P2-T4 (spec-version
  declaration) folded into P2-T3; added P2-T8 (drop skill's template
  duplication, rewire to `framework/layers/`) to close D-0013 fully for
  the skill package. New order: T3 → T8 → T5 → T6.
- 2026-05-20T11:50:00Z — Drafted `plans/P2-T3-PLAN.md` (two review passes
  done). Plan recon surfaced an audit gap: 3 test files + 17 docs files
  carry `ucx_flow_v3` references that §3a/§3b missed. P2-T3 absorbs the
  scope (§3a-extension for tests; new §3c for docs, classified historical
  vs current-behavior per the P2-T7 G13 lesson) and lands the audit-doc
  correction inside its own step sequence. Awaiting approval to implement.
- 2026-05-20T12:50:00Z — Completed P2-T3 port-with-repoint: 200 files
  ported + 2 VERSION files; path-map applied across 18 edit-list files;
  11 historical docs preserved verbatim; pyproject + .mcp.json updated;
  audit §3a renamed and new §3c added. Conformance 25/25; Hermes tests
  397/447. Pass 3 retrospective records G18: plan's "no logic edits"
  Out-clause contradicted P2-T1 Q3 downstream which had pre-flagged
  required logic work. **Added P2-T9** to queue: rewire MCP scaffold
  runtime (`CANONICAL_SCAFFOLD_MAPPINGS`) to consume `framework/layers/`
  instead of the dropped `platforms/hermes/templates/`. Symmetric with
  P2-T8's skill-package rewire — could be merged.
