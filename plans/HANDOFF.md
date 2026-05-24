# Session Handoff

> **✅ MERGED TO MAIN — PR #2 (2026-05-24).** The whole post-v1.0.0 line landed
> on `main` (merge commit `3974daa`): canonical 54-skill plugin set, ADAPT
> overlay, **CHG-D1 / GATE-SPEC**, **CHG-D2 / GD-01**. All four PR checks were
> green pre-merge — including the **Framework-spec change gate**, GATE-SPEC's
> first real enforcement (E005 VERSION + E008 CHANGELOG + E006/E007 conformance)
> on a live PR. `main` is the integration line; `claude/skill-revision` is merged
> (safe to delete). Framework spec **0.3.1**; conformance 43; the `workflows`
> permission is now granted (so `.github/workflows/**` is pushable in-container).
>
> **Remaining (user-only):**
>
> - **Branch protection on `framework/**`** (repo → Settings → Branches) — the
>   human-approval half of GATE-SPEC. The automated half now enforces via the
>   `chg-gate.yml` workflow; the human sign-off exists only once this rule is set.
> - **Release tags** — annotated; tag pushes still 403 in-container (separate
>   from the workflows scope, see `docs/TAGGING.md`), so push from a local clone:
>
>   ```sh
>   git tag -a framework/v0.2.0 f22fe6a -m "Framework spec v0.2.0 — adaptation overlay (ADAPT, D-0019)"
>   git tag -a framework/v0.3.0 f8e8bf5 -m "Framework spec v0.3.0 — GATE-SPEC framework-spec change gate (CHG-D1, D-0020)"
>   git tag -a framework/v0.3.1 3753de2 -m "Framework spec v0.3.1 — governance decision register (CHG-D2, GD-01)"
>   git push origin framework/v0.2.0 framework/v0.3.0 framework/v0.3.1
>   ```
>
>   Optional project milestone tag: `git tag -a v1.1.0 3974daa -m "Post-cutover feature release — adaptation overlay + CHG GATE-SPEC" && git push origin v1.1.0`.
> - Delete the merged `claude/skill-revision` branch.

> **✅ CHG-D2 COMPLETE — framework governance decision register (2026-05-23).**
> Established `framework/governance/DECISIONS.md` — the spec's own durable home
> for decisions about the spec + its governance — and recorded the CHG
> implementation model (CHG-D1) there as **GD-01** (engine-agnostic). The
> migration log's spec-affecting decisions now graduate here; D-0013 + D-0019 are
> listed pending. Recording it was itself a GATE-SPEC change — the **first real
> exercise of the gate** (framework spec **0.3.0 → 0.3.1**; + both FSV + 54
> skills). Conformance **43** (DECISIONS.md folded into the existing governance
> file-set checks; its content passes the engine-token hygiene scan);
> `plm_lint` clean; `spec_gate` passes vs origin/main. ROADMAP CHG-D1 **and**
> CHG-D2 are now done. **Branch: `claude/skill-revision`** (PR #2 → `main`,
> clean fast-forward). **Workflows now active** — the user granted the GitHub App
> the `workflows` permission, so `.github/workflows/**` is pushable from the
> container. Fixed the stale **Plugin smoke-checks** guard in place (skill count
> `-lt 100`/~142 → `-lt 40`/~54) and **activated `chg-gate.yml`** (the GATE-SPEC
> CI workflow, `pull_request`-scoped); `plans/workflows-pending/` is drained.
> **Remaining user-only:** branch protection / required reviewers on
> `framework/**` (the human-approval half of GATE-SPEC); push the 0.3.x tags from
> a local clone.

> **✅ CHG-D1 COMPLETE — GATE-SPEC, the framework-spec change gate (2026-05-23).**
> ROADMAP CHG-D1 done (D-0020, plan `plans/CHG-D1-PLAN.md`): change management as
> **skills + CI/CD, both platforms**. Added **GATE-SPEC** — the *meta* gate
> governing changes to the `framework/` spec itself (templates/governance/
> registry/VERSION), orthogonal to the artifact-cascade gates. Five increments:
> (1) shared spec — `GATE-SPEC_FRAMEWORK.md` + `spec` change_source +
> `semver_impact` + error-catalog/diagram/CHG-template/README wiring + a
> conformance guard; (2) plugin skills — `gate-check` runs it, `doc-chg` family
> routes to it, `knowledge-extractor` **unblocked** (spec promotion now routes to
> a real CHG record + GATE-SPEC); (3) CI — `tests/chg/spec_gate.py` (diff-aware
> E005/E008) + staged `plans/workflows-pending/chg-gate.yml`; (4) Hermes
> server-side — `validation/chg_rules.py` + 5 unit tests; (5) close. Three-way
> enforcer split: record validator (E001–E004) · CI (E005–E008) · protected-branch
> review (human E004); **a skill never self-approves**. Framework spec **0.2.0 →
> 0.3.0** (+ both FSV + 54 skills). Conformance **38 → 43**; Hermes CHG 8/8 (full
> validation suite green bar pre-existing `mcp`-SDK-missing collection errors);
> `plm_lint` clean. **Branch: `claude/skill-revision`.** **Follow-up: CHG-D2**
> (record CHG-D1 as a formal `framework/governance/` decision — now actionable).
> **User-only:** relocate `chg-gate.yml` → `.github/workflows/`; set branch
> protection on `framework/**` (the human-approval half); push the 0.3.0 tags.

> **✅ ADAPT COMPLETE — adaptation surface + knowledge extractor (2026-05-23).** New feature:
> project adaptation overlay + knowledge extractor (plan `plans/ADAPT-PLAN.md`,
> hardened Pass 1–4; design recorded D-0019). **Increment 1 (this commit):** the
> engine-agnostic surface spec `framework/governance/ADAPTATION.md` + the
> machine-readable `ADAPTATION_SURFACE.yaml` (closed 4-knob registry —
> `active_layers`, `section_toggles`, `audit_threshold` raise-only, `glossary`;
> `id_format` deferred; skippable layers `[BDD, ADR]` + cascade rule). Registered
> in `governance/README.md` + the governance conformance contract (+1 test).
> Conformance **33/33**. **Increment 2 done:** `adapts:` frontmatter +
> `## Adaptation` consult-clause wired into the **35-skill adapting set** (layer
> base/autopilot/audit/fixer ×8 + `trace-check` + `project-init`/`-adopt`) via
> `/tmp/wire_adapts.py`; new `tests/conformance/platforms/test_adaptation.py`
> asserts `adapts ⊆ surface` + authority-ref + ≥35 wired. Conformance **36/36**,
> `plm_lint --all` clean. **Increments 3+4 done:** new **`project-profile`**
> utility skill (creates/maintains `.aidoc/profile.yaml`, materializes the
> user-global seed, validates against the surface); registered everywhere —
> plugin README (52→**53**, utilities 16→17), `SKILL_AUTHORING` §1 (corrected
> stale 46→53, added the change-mgmt family + project-adopt/gate-check it had
> omitted), `skill-recommender` intent map + catalog, `doc-flow` utility list.
> Conformance **36/36**, `plm_lint` clean, skill count **53**. **ADAPT-B done
> (functional):** added the **learnings-log** convention to `ADAPTATION.md` (§7,
> entry shape + best-effort capture + owner-routing) and the **`knowledge-extractor`**
> skill (manual: read profile+learnings → judge generalizability → classify owner
> → draft; spec target → CHG draft stamped *blocked on the unbuilt spec-gate*,
> guidance target → PR-ready description; never applies/approves). Registered
> everywhere (README 53→**54**, utilities 17→18; `SKILL_AUTHORING`;
> `skill-recommender` intent+catalog); `project-profile` link restored.
> **✅ ADAPT COMPLETE — version bumped (feature close):** `framework/VERSION` +
> both platform `FRAMEWORK_SPEC_VERSION` `0.1.0 → **0.2.0**`, and all 54 plugin
> skills' `framework_spec_version` (user decision = bump everything). Conformance
> **37/37** (+leakage guard), `plm_lint` clean, skill count **54**. **Branch:
> `claude/skill-revision`** (user-confirmed). **Deferred follow-up:** the CHG
> spec-change gate (CHG-D1) — spec→CHG promotions are drafted but ungated until
> built. **Pending user-only (carry-overs):** push the 0.2.0 spec/release tags
> from a local clone (in-container `refs/tags/*` 403); decide whether to roll
> these commits into a plugin release (CHANGELOG `[Unreleased]` not yet cut).

> **✅ NEW SKILLS ADDED — 46 → 52 (2026-05-23, P3-T7).** A post-revision review
> found framework-backed capabilities with no skill; added 6 (skipping
> `doc-code`/implement by user choice): the **`doc-chg` family** (base +
> `-autopilot`/`-audit`/`-fixer`) for the CHG change-management overlay
> (`framework/governance/chg/`) — change-level classification (C1–C3/Emergency),
> source→gate routing, cascade impact, `gate_ready` instead of a ≥90 score;
> **`gate-check`** — runs the CHG approval gates (GATE-01/03/06/08/CODE) and
> prepares `GATE_APPROVAL_FORM` (human approves, never the skill); and
> **`project-adopt`** — brownfield counterpart to `project-init`. Wired into
> `doc-flow`, `skill-recommender`, plugin `README` (52), `CHANGELOG`,
> `docs/PARITY.md`, and `plm_lint` `MIGRATED`. Conformance **32/32**. Record:
> `plans/P3-T7-PLAN.md`.

> **✅ SKILL SET REVISED — canonical 46 (2026-05-23, P3-T6).** Pruned the plugin
> skill corpus **124 → 46** and recreated every survivor to one standard
> (`platforms/claude-code-plugin/docs/SKILL_AUTHORING.md`): the 8 layer families
> `doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}` × {base, `-autopilot`, `-audit`,
> `-fixer`} = 32, plus 14 utilities. Removed (reversing D-0015): 25 SPEC-subtype
>
> - 36 test-type families (folded into SPEC L6 / TDD L7), 14 deprecated
> `-reviewer`/`-validator` (merged into `-audit`), 3 legacy utils
> (contract-tester/test-automation/mermaid-gen), 16 loose `.md`, and the orphaned
> `doc-flow/SHARED_CONTENT.md` (D-0013). Each skill `version` now defaults to the
> plugin version (0.2.0) + `framework_spec_version`; Version-History footers
> dropped; `mermaid-gen`→`charts-flow`; `agents/README` + `doc-validator` +
> `doc-review` repointed to `-audit`. Conformance **32/32**. Record:
> `plans/P3-T6-PLAN.md`. **Open:** (1) confirm push branch — working tree is on
> `claude/skill-revision`, task setup named `claude/multi-platform-migration-AamWB`;
> (2) consider bumping plugin 0.2.0→0.3.0 given the scope (skills track the
> plugin version, so they'd follow); (3) the "new skills" idea is still pending.

> **🚀 PLUGIN v0.2.0 RELEASE PREPPED (2026-05-23) — launch-wise, in-container half.**
> Cut the Claude Code plugin's first post-migration release: `VERSION` +
> `plugin.json` bumped `0.1.0 → 0.2.0`; CHANGELOG `[Unreleased]` → `[0.2.0] —
> 2026-05-23`; added the repo-root **plugin marketplace** manifest
> (`.claude-plugin/marketplace.json`, marketplace `aidoc-flow-framework` →
> plugin `aidoc-flow`, subdir source) so it installs via `/plugin marketplace
> add vladm3105/aidoc-flow-framework` + `/plugin install
> aidoc-flow@aidoc-flow-framework`; install command added to root + plugin
> READMEs; `docs/TAGGING.md` Current-tags table extended (`v1.0.0`,
> `claude-code-plugin/v0.2.0`). Conformance 32/32. The annotated tag
> `claude-code-plugin/v0.2.0` is created locally on the release commit (push
> 403s in-container — same pattern as every prior tag). **Remaining = user-only:
> (1) merge this branch into `main`; (2) push the tag from a local clone;
> (3) relocate CI workflows from `plans/workflows-pending/` → `.github/workflows/`.**
> See "Independent pending user actions" below for exact commands.

> **✅ MIGRATION COMPLETE (2026-05-21).** All five phases done; the
> Phase 5 cutover is closed at project `v1.0.0` (in-container half).
> The working branch holds the finished multi-platform project. The
> only remaining steps are **user-side local-clone actions** — tag
> pushes + the `main` force-replace + CI-workflow relocation
> (commands in `plans/MIGRATION_TODO.md` P5-T6). Pre-migration
> history is on the protected `legacy-ucx-v3.2-read-only` branch.
>
> **✅ PLM COMPLETE (2026-05-22) — Plugin layer-model migration.** The Claude
> Code plugin's entire **125-skill** corpus is migrated from the legacy
> 12-layer SDD model to the framework's **8-layer** model — all batches B0–B7
> landed. Sequence: B1 renamed tspec→tdd & tasks→iplan + retired sys/req/ctr
> (142→125); B2 brd/prd/ears; B3 bdd/adr + adr-roadmap; B4 spec (L9→L6) + 5
> SPEC-subtypes (L6 helpers); B5 6 test-subtypes (L7 helpers); B6 12
> helper/orchestrator skills (incl. doc-naming, element-code system deleted);
> B7 promoted the gate to conformance + deleted the PARITY gap + CHANGELOG
> close-out. Both platforms now implement the 8-layer model. `plm_lint --all`
> is clean and enforced by conformance (`tests/conformance/platforms/test_plm_lint.py`;
> suite **32/32**). Records: `plans/PLM-PLAN.md`, `DECISIONS.md` D-0015.
>
> **Post-migration gap audit (2026-05-22, D-0016):** verified the framework
> correctly absorbs SYS/REQ/CTR (SYS→SPEC, CTR→SPEC, REQ→EARS) against the v3.2
> source; fixed deprecated-layer residue the gate had missed in the plugin
> surface — `agents/requirements-analyst.md` (REQ→EARS), the trace-check example,
> and a broken `doc-validator` ref — and hardened `plm_lint` (now scans
> `agents/`+`commands/`; adds dash-ref / layer-dir / context-aware 3-segment
> patterns). project-mngt keeps generic REQ-NN (excepted).

Continuity record across ephemeral sessions. Read this first each session;
refresh it at milestones and **before any context compaction**.
Timestamps are ISO 8601 UTC (`YYYY-MM-DDThh:mm:ssZ`).

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Last updated  | 2026-05-24T00:00:00Z                       |
| Working branch| `main` (PR #2 merged; `claude/skill-revision` merged, safe to delete) |
| Current phase | Post-cutover features all landed on `main` (merge `3974daa`): **ADAPT** (D-0019), **CHG-D1 / GATE-SPEC** (D-0020), **CHG-D2 / GD-01**. Framework spec **0.3.1**; 54 skills; conformance **43**; GATE-SPEC CI enforcing on PRs. |
| Next task     | **None pending in-container.** **User-only:** branch protection on `framework/**`; push the framework `v0.2.0/v0.3.0/v0.3.1` tags (+ optional `v1.1.0`) from a local clone (see top blockquote). |

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
- 2026-05-20T19:10:00Z — Completed P3-T1 (design, paper-only).
  7 questions resolved in `plans/P3-T1-DESIGN.md`. Manifest is
  minimal (auto-discovery handles registration; confirmed via
  claude-code-guide agent — no published `$schema` URL,
  `name`/`description`/`version`/`author` are the recommended core
  fields). Plugin skill set finalised: **142 skills** (129 doc-* +
  13 non-doc); plugin name `aidoc-flow`; copy strategy a 3-stage
  `cp -r` + `rm -rf` recipe; no lifecycle hooks in v0.1.0.
  Pass 2 caught a Pass 1 skill-count miscount (144 → 142) and
  softened the manifest author block (populated from
  `git config user.name` at P3-T3, not hardcoded).
- 2026-05-20T20:20:00Z — Completed P3-T2 (port content). 3-stage
  `cp -r` + `rm -rf` recipe landed 142 skills + 19 root files + 1
  agent + 1 command at `platforms/claude-code-plugin/` (168 total
  files). Basic sed cleared 211 line hits of `ai_dev_flow` across
  30 source files; Class B (5 layer dirs) + Class C
  (ID_NAMING_STANDARDS) + project-mngt `/opt/data` rewrite applied.
  G13 illustration paths preserved. All 11 verify gates green;
  conformance unchanged at 25/25. Pass 3 retro records G17 (sed
  delimiter collision — `|` clash with regex alternation, corrected
  to `#` mid-flight) and G18 (Class D stale-reference set sized:
  ~150 line hits across 30 stale segments; top item
  `framework/scripts/` with 60 refs; resolution deferred to a
  content-migration task per P3-T1 §Deferred R2).
- 2026-05-20T21:10:00Z — Completed P3-T3 (plugin scaffold).
  `.claude-plugin/plugin.json` (7 fields, minimal manifest);
  `VERSION` + `FRAMEWORK_SPEC_VERSION` both `0.1.0`; `README.md`
  expanded from 27-line placeholder to 82-line user-facing doc.
  Two implementation findings recorded: **Finding 1** (omit author
  block — in-container `git config user.name` returns `Claude`, not
  the repo owner; manifest's `repository` URL handles ownership
  signaling); **Finding 2** (no platform `CHANGELOG.md` — following
  Hermes precedent for symmetry; retrofit deferred). All 11 verify
  gates green; conformance 25/25 unaffected.
- 2026-05-20T21:55:00Z — Completed P3-T4 (Phase 3 verify). 22 gates
  ran across conformance, structure, content + coupling sweep,
  manifest validity, and integration-level checks. Mid-flight cleanup
  surfaced and removed **47 broken symlinks** the source `.claude/`
  carried (self-referencing pointers at `/opt/data/docs_flow_framework/
  .claude/skills/<name>` — leftovers from the old multi-project
  symlink consumption pattern). Post-cleanup file count is 171 =
  git = disk; audit math reconciles cleanly. All 22 gates green.
  Verify record at `plans/P3-T4-VERIFY.md`. Lesson for future port
  plans: add `find -type l` to the audit recon to surface symlinks
  upfront (P3-T0 + P2-T0/T2 audits missed this).
- 2026-05-20T22:40:00Z — Completed P3-T5 (Phase 3 close).
  `CHANGELOG.md` cut to `[0.4.0] — 2026-05-20` (full Phase 3 cycle
  — Added / Changed / Removed, plus a carried-known-issue note for
  the ~150 Class D stale refs); `ROADMAP.md` status `Phase 3 complete
  (v0.4.0) — Phase 4 next`; Phase 3 section ends with `Status:
  complete (v0.4.0, claude-code-plugin/v0.1.0)`; `docs/TAGGING.md`
  table appended (7 rows total). Close commit `087f7d5` pushed to the
  working branch. Annotated tags `v0.4.0` + `claude-code-plugin/v0.1.0`
  created locally on `087f7d5`; tag push 403'd as expected (third
  occurrence of the in-container 403 — P1-T8, P2-T6, P3-T5). Tag
  publication requires the user to run the local-clone workaround
  documented in `plans/P3-T5-PLAN.md` Implementation note. **Phase 3
  is structurally closed.**
- 2026-05-20T22:55:00Z — User published the two Phase 3 tags via the
  local-clone workaround. `git ls-remote --tags origin` now returns
  all 7 tags; `v0.4.0` and `claude-code-plugin/v0.1.0` both
  dereference to the close commit `087f7d5`. **Phase 3 is formally
  closed.** Next: Phase 4 (Conformance & Independence).
- 2026-05-20T23:45:00Z — Completed P4-T0 (Phase 4 audit + task
  breakdown). `plans/P4-AUDIT-conformance.md` assesses the platform-
  conformance contract (4 bullets: PC1+PC4 statically testable
  today, PC2+PC3 deferred to runtime exercise), the CI gap (no
  `.github/workflows/`; 3 greenfield workflows planned —
  conformance, Hermes, plugin), and the CHANGELOG/README/LICENSE
  gaps (both platforms lack `CHANGELOG.md`, Hermes README still
  Phase-0 placeholder, no repo-root `LICENSE`). 9 deferred items
  from P1/P2/P3 rolled up: 5 in-scope for Phase 4, 4 deferred
  further (content-design / already-done). Phase 4 shape is 5
  sub-tasks (T1 design → T2 conformance tests → T3 CI → T4
  retrofits+parity → T5 verify+close). 6 open questions for P4-T1.
  See `plans/P4-T0-PLAN.md` for the full breakdown.
- 2026-05-20 — Added `docs/STARTUP_HANDOFF.md` — distills business /
  startup ideas from the architectural decisions of the multi-platform
  migration: IPLAN-as-product, IPLAN corpus (D-0012 R2), engine-
  agnostic spec, domain profiles (post-v1.0), CHG governance-as-code
  (CHG-D1), ephemeral-session workflow tooling, migration as case
  study. Does not affect the migration's technical scope; ideas
  surfaced organically and are filed for a future strategy session.
- 2026-05-21T00:35:00Z — Completed P4-T1 (design, paper-only).
  6 questions resolved in `plans/P4-T1-DESIGN.md`. New conformance
  sub-package `tests/conformance/platforms/` with two modules
  (`test_version_declaration.py` + `test_engine_isolation.py`);
  suite grows 25 → 28-30. PC4 scope: runtime-significant
  directories only (`src/`, `pyproject.toml`, `.claude-plugin/`,
  `commands/`, `agents/`); documentary references in
  READMEs/docs/skills allowed. CI runner: `ubuntu-latest`;
  Python 3.12 via `actions/setup-python@v5`. CHANGELOG retrofit:
  minimal-honest (each platform's `[0.1.0]` mirrors the
  corresponding project release scoped to that platform). Hermes
  README: full mirror of P3-T3 plugin README. LICENSE: MIT (matches
  plugin manifest placeholder); copyright `vladm3105`. Q7
  confirmed no framework tag bump.
- 2026-05-21T01:20:00Z — Completed P4-T2 (platform conformance
  tests). New sub-package `tests/conformance/platforms/` with 6
  test methods across 2 modules: `test_version_declaration.py`
  (4 tests — PC1) + `test_engine_isolation.py` (2 tests — PC4
  with case-insensitive forbidden-token scan, scoped to runtime-
  significant directories per P4-T1 Q2). `_spec.py` extended
  additively. **Conformance suite: 25 → 31 tests, all green.**
  One implementation-time correction: initial `_spec.py` Edit
  failed silently (file not Read first) — caught by the ImportError
  in suite output; re-Read + re-Edit landed cleanly. Lesson: silent
  Edit failures are real; treat unexpected ImportErrors after
  "successful" Edits as suspect.
- 2026-05-21T02:15:00Z — Completed P4-T3 (CI workflows authored).
  Three greenfield workflows (`conformance.yml`, `hermes.yml`,
  `plugin.yml`) — all `ubuntu-latest`, Python 3.12 via
  setup-python@v5, concurrency cancel-in-progress, minimal
  `contents: read`. No carry-over from legacy. All 8 verify gates
  green; local smoke confirms commands work.
  **Implementation-time discovery — fifth in-container
  restriction:** the GitHub App credentials lack the `workflows`
  permission, so the in-container push of `.github/workflows/*.yml`
  is rejected. Workflow files staged at `plans/workflows-pending/`
  for the user to `git mv` into `.github/workflows/` from a local
  clone — exact commands in `plans/P4-T3-PLAN.md` Implementation
  note. (`docs/TAGGING.md` was extended in P4-T4 to document this
  restriction symmetrically with the tag-push restriction.)
- 2026-05-21T04:15:00Z — Completed P4-T5 (Phase 4 verify + close,
  combined per P4-T0 design). 13 gates ran green; one carried-
  known-issue surfaced (`api_runner.py:115` stale install
  instruction `pip install 'ucx_hermes[api]'`; correct is
  `hermes-server[api]` — 1-line fix deferred to Phase 5
  housekeeping per R5 scope). Close commit `954d8da` shipped;
  `CHANGELOG.md [0.5.0]` cut; ROADMAP marked; `docs/TAGGING.md`
  table grew to 8 rows. Annotated tag `v0.5.0` created locally;
  in-container tag push 403'd as expected (4th occurrence —
  P1-T8, P2-T6, P3-T5, P4-T5). Verify record at
  `plans/P4-T5-VERIFY.md`. **Phase 4 structurally closed.**
- 2026-05-21T04:30:00Z — User published `v0.5.0` from a local
  clone (initial push didn't land; the local tag existed and
  `git push origin v0.5.0` transmitted it). `git ls-remote --tags
  origin` now returns 8 tags; `v0.5.0^{}` dereferences to the
  close commit `954d8da`. **Phase 4 formally closed.** Project
  moves into Phase 5 (Cutover). Workflow relocation from P4-T3
  remains an independent pending user action.
- 2026-05-21T05:35:00Z — Completed P5-T0 (cutover audit + task
  breakdown). `plans/P5-AUDIT-cutover.md` inventories the two
  destructive removal targets (`legacy/` 28M/2275 files; root
  `.claude/` loader) and confirms **no runtime dependency** from
  the surviving tree on either. Classifies every cutover operation
  by reversibility × authority — the `main` replacement and all
  tag pushes are **user-only** (main is locked per docs/PROJECT.md
  §3; tags hit the 5th refs/tags/* 403). Recommends shipping
  `v1.0.0` with the documented plugin layer-model gap (content
  migration → post-v1.0). 6-task breakdown with confirmation gates
  on the destructive removals; root `.claude/` removal sequenced
  late (it disables the session's own hooks). 6 open questions for
  P5-T1. **The destructive steps and the main replacement will each
  be surfaced for explicit confirmation when reached.**
- 2026-05-21T04:45:00Z — Closed one of the two pending items:
  fixed `api_runner.py:115` stale install string
  (`ucx_hermes[api]` → `hermes-server[api]`; commit `23ae664`);
  Hermes suite 447/447, conformance 31/31; recorded in CHANGELOG
  `[Unreleased] Fixed`. The **workflow relocation remains
  user-only** — the in-container GitHub App lacks the `workflows`
  permission, so `.github/workflows/**` pushes are rejected; the
  files stay staged at `plans/workflows-pending/` until the user
  `git mv`'s them from a local clone (commands in
  `plans/P4-T3-PLAN.md`). The larger carried issues (plugin
  legacy-vs-new layer model; ~150 stale `framework/<X>` refs)
  are post-v1.0 content migrations, not quick completions —
  scoped into Phase 5 / post-v1.0.
- 2026-05-21T03:10:00Z — Completed P4-T4 (retrofits + parity
  report). Six artifacts landed:
  - `platforms/hermes/CHANGELOG.md` — Hermes `[0.1.0]` mirroring
    project `[0.3.0]` scoped content.
  - `platforms/claude-code-plugin/CHANGELOG.md` — plugin `[0.1.0]`
    mirroring project `[0.4.0]` scoped content.
  - `platforms/hermes/README.md` — expanded from 27-line
    placeholder to **113 lines** (mirrors P3-T3 plugin README
    structure: what's inside, install, MCP tool list, framework
    spec conformance section, platform info table, relationship-
    to-plugin section).
  - `LICENSE` at repo root — MIT, copyright `vladm3105` (matches
    plugin manifest `"license": "MIT"`).
  - `docs/PARITY.md` — 5-section capability comparison (matrix /
    operations / extras / known parity gap / choosing between).
    Honest about the **legacy-vs-new layer model gap**: plugin
    lacks `doc-tdd` + `doc-iplan`; has `doc-sys` / `doc-req` /
    `doc-ctr` / `doc-tspec` / `doc-tasks` from the legacy
    11-layer model. Hermes covers all 8 new-model layers via
    its generic `sdd_*` tools. Resolution deferred post-v1.0
    per P3-T1 §Deferred R2.
  - `docs/TAGGING.md` extended with an "In-container push
    restrictions" section documenting the tag + workflow
    restrictions symmetrically (per P4-T3 G15 recommendation).
  All 9 verify gates green; conformance still 31/31.

## Next steps

1. **P5-T2 — Remove `legacy/`** (`git rm -r legacy/`). **Destructive
   — confirm at execution.** Archive precondition met
   (`legacy-ucx-v3.2-read-only` protected). Then P5-T4 (finalize docs
   incl. CLAUDE.md rewrite + legacy-removal→archive-branch
   reconciliation), P5-T3 (remove root `.claude/` — **destructive +
   session-affecting, gated, LATE**), P5-T5 (verify), P5-T6 (close +
   cutover → `v1.0.0`).
2. **P5-T6 cutover is user-authorized:** `main` replacement =
   **force-replace** `main` with the working-branch tip (P5-T1 Q1 —
   FF impossible; lossless via the archive branch; lift main's branch
   protection, force-push, re-enable). Tags via user local-clone.

**Archive branch (done + protected):** `legacy-ucx-v3.2-read-only`
created off `main` (`491e8db`), read-only — preserves the pristine
pre-migration `ucx_framework` project. This is the precondition that
makes the P5-T2/T3 working-branch removals safe (verified: all 7
legacy trees + root `.claude/` present in the archive; caveat — the
archive's `.claude/` is the pre-migration one, the migration-era
hooks survive only in working-branch git history).

**Independent pending user actions** (carry-overs, do anytime):

- Relocate workflows: `git mv plans/workflows-pending/*.yml
  .github/workflows/` from a local clone (P4-T3; in-container
  can't push `.github/workflows/`).

**Plugin v0.2.0 launch — remaining user-only steps** (2026-05-23):

1. **Merge into `main`** — the migrated plugin (8-layer corpus, 9-agent
   roster, marketplace) lives only on `claude/multi-platform-migration-AamWB`,
   13+ commits ahead of `origin/main` (which is at the `v1.0.0` cutover). Until
   merged, `/plugin install` from the repo serves the **pre-migration** plugin.
2. **Push the release tag** from a local clone (in-container 403):

   ```sh
   git tag -a claude-code-plugin/v0.2.0 <release-commit> \
     -m "Claude Code plugin v0.2.0 — full 8-layer SDD model + marketplace install"
   git push origin claude-code-plugin/v0.2.0
   ```

3. **Relocate CI** (item above) so the plugin/conformance workflows actually run.
Verify the tag with `git ls-remote --tags origin`.

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
