# Tagging Policy

> The authoritative git-tag policy for the multi-platform project. `docs/PROJECT.md`
> §3 summarizes it; this document is the full reference.

Git tags are named pointers to specific commits. This project uses them in two
roles: **release tags** that permanently mark version milestones, and
**bookmark tags** that mark notable points for easy retrieval.

> Scope: this covers **git tags**. It is unrelated to the in-document
> `@`-annotations (`@brd`, `@diagram: c4-l1`, …) used inside `framework/`
> artifacts — those are a separate traceability mechanism.

## Tag categories

| Category | Namespace | Example | Annotated | Mutable | Pushed |
|----------|-----------|---------|-----------|---------|--------|
| Release — project milestone | `vX.Y.Z` | `v0.2.0` | yes | no — permanent | yes |
| Release — framework spec | `framework/vX.Y.Z` | `framework/v0.1.0` | yes | no — permanent | yes |
| Release — platform | `<platform>/vX.Y.Z` | `hermes/v0.3.0` | yes | no — permanent | yes |
| Bookmark | `mark/<slug>` | `mark/pre-cutover` | yes | yes — may move/delete | yes |

## 1. Release tags

Release tags mark a published version. Each of the three SemVer streams
(see `docs/PROJECT.md` §2) tags in its own namespace:

- **Project milestones** — `vX.Y.Z`. One per completed phase (`v0.1.0` …
  `v1.0.0`). Tracks the migration itself.
- **Framework spec** — `framework/vX.Y.Z`. The shared `framework/` contract.
  Version source: `framework/VERSION`.
- **Platforms** — `<platform>/vX.Y.Z` (`hermes/…`, `claude-code-plugin/…`).
  Version source: `platforms/<name>/VERSION`.

Rules:

- `VERSION` files hold the **bare** SemVer (`0.1.0`); the tag adds the `v`
  prefix and the namespace.
- Release tags are **annotated** (`git tag -a`) — they carry a tagger, date,
  and message.
- Release tags are **immutable** once pushed. Never move or force-push one;
  to correct a mistake, cut a new version.
- A release tag is created only on a commit whose conformance suite is green.

## 2. Bookmark tags

Bookmark tags mark a notable **non-release** commit so it is easy to find
later — a baseline, a known-good state, an audit reference point, the commit
where some behaviour changed, or a spot worth returning to.

- Namespace: `mark/<slug>` — a short, descriptive, lowercase-kebab slug
  (`mark/pre-cutover`, `mark/conformance-baseline`).
- Annotated, with a one-line note explaining why the commit is marked.
- **Mutable and disposable**: a bookmark may be moved to a newer commit or
  deleted once it has served its purpose. They are *not* versions and carry no
  SemVer meaning.
- Pushed, so the whole team shares them.

## Creating and pushing tags

```sh
# Release tag (annotated)
git tag -a v0.2.0 <commit> -m "Phase 1 — Framework Spec Extraction complete"
git tag -a framework/v0.1.0 <commit> -m "Framework spec v0.1.0 — first release"

# Bookmark tag (annotated)
git tag -a mark/conformance-baseline <commit> -m "First green conformance run"

# Tags do NOT travel with `git push`; push them explicitly
git push origin v0.2.0 framework/v0.1.0      # named tags

# Delete a bookmark that has aged out (local + remote)
git tag -d mark/old-bookmark
git push origin :refs/tags/mark/old-bookmark
```

Never `git push --force` a tag, and never `git push --tags` blindly — push
named tags so nothing unintended is published.

## Finding tags

```sh
git tag -l 'framework/*'     # one stream
git tag -l 'mark/*'          # all bookmarks
git tag -n                   # tags with their annotation messages
git describe --tags HEAD     # nearest tag + distance from HEAD
git log --oneline v0.1.0..v0.2.0   # commits between two tags
```

Slash-namespaced refs (`framework/v0.1.0`, `mark/<slug>`) are valid git tag
names and make `git tag -l '<prefix>/*'` an effective per-stream filter.

## Current tags

| Tag | Commit | Marks |
|-----|--------|-------|
| `v0.1.0` | Phase 0 baseline | Planning & scaffolding milestone |
| `v0.2.0` | Phase 1 close | Framework Spec Extraction milestone |
| `framework/v0.1.0` | Phase 1 close | Framework spec — first independent release |
| `v0.3.0` | Phase 2 close | Platform A: Hermes Re-homing milestone |
| `hermes/v0.1.0` | Phase 2 close | Hermes platform — first independent release |
| `v0.4.0` | Phase 3 close | Platform B: Claude Code plugin milestone |
| `claude-code-plugin/v0.1.0` | Phase 3 close | Claude Code plugin — first independent release |
| `v0.5.0` | Phase 4 close | Conformance & Independence milestone |
| `v1.0.0` | Phase 5 close | Cutover milestone — multi-platform project complete |
| `claude-code-plugin/v0.2.0` | Plugin 8-layer migration close | Claude Code plugin — full 8-layer SDD model (46 skills, 9-agent roster) + marketplace install |
| `claude-code-plugin/v0.4.0` | Plugin release `0.4.0` close | Claude Code plugin — canonical 52 (50 active + 2 deprecated) skills, framework spec `0.11.0`, marketplace metadata aligned |
| `claude-code-plugin/v0.4.1` | Plugin release `0.4.1` close | Claude Code plugin — BRD-layer review-team subagent fan-out wired (BRD-RT-001, D-0024); framework spec `0.11.2` |
| `claude-code-plugin/v0.4.2` | Plugin release `0.4.2` close | Claude Code plugin — project profile as override-only delta (PROFILE-DELTA-001, D-0025); framework spec `0.11.3` |
| `claude-code-plugin/v0.4.3` | Plugin release `0.4.3` close | Claude Code plugin — verdict-chain consistency (BRD-RT-002, D-0026): synthesizer writes `verdict.json` companion; audit/autopilot/fixer read from it; per-layer cap 1800s; per-audit-skill timeout 1200s |
| `claude-code-plugin/v0.4.4` | Plugin release `0.4.4` close | Claude Code plugin — operational fixes from BRD-RT-002 live verification (BRD-RT-003, D-0027): AUTOPILOT_TIMEOUT=1800s for doc-*-autopilot; per-layer cap 3600s; doc-*-fixer explicit multi-lens dispatch rules |
| `claude-code-plugin/v0.4.5` | Plugin release `0.4.5` close | Claude Code plugin — generalised orchestrator timeout (BRD-RT-004, D-0028): collapsed `AUDIT_TIMEOUT` / `AUTOPILOT_TIMEOUT` / `REVIEW_TEAM_TIMEOUT` into single `ORCHESTRATOR_TIMEOUT=1800s`; closes G15 (`doc-*-fixer` 600s timeout) by extending name-match to `*-fixer` |
| `claude-code-plugin/v0.6.0` | Plugin release `0.6.0` close (SAGA-PARITY-001 Phase 2, MINOR) | Claude Code plugin — BRD-layer saga implementation: autopilot refactored to dispatch each create→review→revise phase via Bash → claude -p subprocesses; maintains saga.json at `.aidoc/review/01_BRD/<BRD-id>/saga.json` per framework saga lifecycle contract (REVIEW_SAGA.md, D-0031); break-circuit policy with per-skill checkpoint boundaries; resumable runs (PARTIAL_TIMEOUT preserved across invocations). PRD..IPLAN propagation deferred to Phase 4; Hermes alignment to Phase 3. |
| `claude-code-plugin/v0.6.1` | Plugin release `0.6.1` close (SAGA-PARITY-001 Phase 2 Amendment 1, PATCH) | Claude Code plugin — BRD-layer saga driver: new `tools/saga_driver.py` (Python stdlib-only) replaces cooperative-enforcement SKILL-prompt loop with preemptive script-driven enforcement; `doc-brd-autopilot/SKILL.md` slimmed to thin entry point invoking the driver; `tools/sync-plugin-framework.sh` extended to vendor `tools/` into plugin bundle; harness cascade dispatcher autopilot-only with env-var contract (PREV_OUTPUT, ARTIFACT_ID, ARTIFACT_PATH); new conformance test `test_saga_driver_invariants.py` (10 tests including layer-crew drift defence). Fixes empirical failure surfaced in 2026-06-05 url-shortener live verification under v0.6.0. PRD..IPLAN still cooperative; migration in Phase 4. |
| `claude-code-plugin/v0.6.2` | Plugin release `0.6.2` close (REVIEW-CALIBRATION-001, PATCH) | Claude Code plugin — 5 content sub-checks added to all 8 layer audit SKILLs (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md`): A1 cell-actionability + A2 assumption-capture + A3 cross-section pointer-validity (auditor lens); BA1 acceptance-criterion testability (business_analyst lens); SE1 deferred-decision safety (security_engineer lens). Section references use concept names (not § numbers) so wording works uniformly across layer templates. Addresses 5 substantive issues that the v0.6.1 review missed in url-shortener BRD-01 (visit-count AC untestable; sync-response content unspecified; §10 budget non-actionable + cross-referenced as quantitative; TTL assumption buried in FR prose; open-redirect Med/High risk + deferred mitigation). No new lens, no spec change. |
| `claude-code-plugin/v0.6.3` | Plugin release `0.6.3` close (SAGA-PARITY-001 Phase 4 PRD increment, PATCH) | Claude Code plugin — PRD layer wired to the saga driver (`tools/saga_driver.py --layer 02_PRD`). `doc-prd-autopilot/SKILL.md` gains the slim `### Saga-driven generation loop` section that BRD got in v0.6.1 Amendment 1; legacy in-session 5-step pattern preserved as the `### Linear Pipeline` `single_pass` mode. Same mechanical change pattern as BRD; no new code paths in the driver itself (it already knew layer `02_PRD`). First of 7 incremental PRs propagating the saga driver to PRD..IPLAN. |
| `claude-code-plugin/v0.6.4` | Plugin release `0.6.4` close (PRD-RT-001, PATCH) | Claude Code plugin — PRD audit + fixer wired to team-mode dispatch. `doc-prd-audit/SKILL.md` gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` sections (grafted from `doc-brd-audit/SKILL.md` under BRD-RT-001 with PRD-specific lens crew); same shape for `doc-prd-fixer/SKILL.md`. PRD crew: `product_owner: 30, architect: 25, tech_lead: 20, chaos_engineer: 8, security_engineer: 7, auditor: 10` (chaos / security split 8 / 7 per CHAOS-SEC-SPLIT-001). Second of the per-layer Phase 4 PRs (autopilot wiring + audit/fixer team-mode wiring are split per the verify-one-layer-before-propagating rule). |
| `claude-code-plugin/v0.6.5` | Plugin release `0.6.5` close (harness direct-driver invocation, PATCH) | Claude Code plugin — `tests/scripts/test-acceptance.sh` cascade dispatcher invokes `python3 saga_driver.py` DIRECTLY rather than routing through the `doc-<layer>-autopilot` SKILL. Eliminates LLM-stochasticity from the harness's driver-invocation path (surfaced by PR #101 PRD-RT-001 verification: same SKILL prompt produced different LLM behavior across runs; affected all 8 layers including merged BRD). The autopilot SKILL remains the user-facing entry point for interactive use (`/aidoc-flow:doc-<layer>-autopilot`); only the harness path changes. Driver is layer-agnostic (its `_LAYER_CREWS` covers all 8 layers from v0.6.1); harness passes `--layer NN_LAYER` per layer. Deterministic. Unblocks live verification for EARS-RT-001..IPLAN-RT-001 propagation. |
| `claude-code-plugin/v0.7.0` | Plugin release `0.7.0` close (LAYER-PLAYBOOKS-001, MINOR) | Claude Code plugin — playbook injection in doc-brd-audit + doc-prd-audit SKILLs (BRD + PRD scope). New `tools/playbook_loader.py` + `tools/finding_filter.py` stdlib helpers; `agents/synthesizer.md` enforces `findings[].check` citation and emits `verdict.playbook_coverage`. Framework spec `0.13.1` → `0.14.0` (CHG-gated: new §Playbooks contract in REVIEW_TEAM.md). 11 playbook files (5 BRD + 6 PRD lenses). Live BRD acceptance: PASS @ 93/100 with 71% findings citing playbook checks. 6 audit SKILLs (EARS/BDD/ADR/SPEC/TDD/IPLAN) deferred to per-layer follow-up PRs. |
| `claude-code-plugin/v0.5.0` | Plugin release `0.5.0` close (BREAKING) | Claude Code plugin — adversary lens partitioned into `chaos_engineer` + `security_engineer` (CHAOS-SEC-SPLIT-001, D-0030); per-layer crew weights redistributed in `REVIEW_CREWS.yaml`; agent `adversary.md` renamed to `chaos-engineer.md`; `security-engineer.md` promoted to first-class crew lens; framework spec `0.11.3` → `0.12.0` (CHG-gated); slot filename change `adversary.json` → `chaos_engineer.json` + new `security_engineer.json` (BREAKING) |
| `framework/v0.13.0` | SAGA-PARITY-001-PHASE-1 close | Framework spec — review-saga lifecycle promoted to spec (`REVIEW_SAGA.md` + `saga.schema.json`); D-0031 supersedes D-0005's scope; both platforms declare intent to conform with full impl in Phases 2 and 3 |
| `framework/v0.12.0` | CHAOS-SEC-SPLIT-001 close | Framework spec — `adversary` lens partitioned into `chaos_engineer` + `security_engineer` (D-0030); per-layer crew weights redistributed in `REVIEW_CREWS.yaml`; new `## Weight allocation rules` subsection in `REVIEW_TEAM.md` |
| `framework/v0.11.3` | PROFILE-DELTA-001 close | Framework spec — new `PROFILE-TEMPLATE.yaml` skeleton + project profile delta semantics |
| `framework/v0.2.0` | ADAPT close (`f22fe6a`) | Framework spec — project adaptation overlay (ADAPTATION surface, D-0019) |
| `framework/v0.3.0` | CHG-D1 close (`f8e8bf5`) | Framework spec — GATE-SPEC framework-spec change gate (D-0020) |
| `framework/v0.3.1` | CHG-D2 (`3753de2`) | Framework spec — governance decision register, GD-01 |
| `v1.1.0` | PR #2 merge (`3974daa`) | Post-cutover feature release — skill-set revision + adaptation overlay + CHG GATE-SPEC |

> Phase 1 tags (`v0.1.0`, `v0.2.0`, `framework/v0.1.0`) are published
> on the remote. Phase 2 tags (`v0.3.0`, `hermes/v0.1.0`), Phase 3
> tags (`v0.4.0`, `claude-code-plugin/v0.1.0`), and Phase 4 tag
> (`v0.5.0`) are created locally on the in-container session at the
> respective close commits and need the local-clone workaround
> established at P1-T8 — the in-container git proxy continues to
> refuse tag pushes with HTTP 403. See `plans/P2-T6-PLAN.md`
> §Approach.5, `plans/P3-T5-PLAN.md` §Approach.5, and
> `plans/P4-T5-PLAN.md` §Approach.6 for the exact local-clone
> commands. Verify any tag's publication via
> `git ls-remote --tags origin`.
>
> The post-cutover tags (`framework/v0.2.0`, `framework/v0.3.0`,
> `framework/v0.3.1`, and the project milestone `v1.1.0`) are **published** on
> the remote, created from a local clone at the PR #2 merge.

## In-container push restrictions

The remote-execution-environment GitHub App credentials are scoped
narrower than a normal user push, so two operation classes must be
performed from a local clone with normal credentials:

| Operation class | Symptom in-container | Workaround |
|-----------------|----------------------|------------|
| `refs/tags/*` pushes | `HTTP 403` on `git push origin <tag>` | Re-create the annotated tag locally on the same target commit; `git push origin <tag>` from the local clone. Occurrences: P1-T8, P2-T6, P3-T5. See `docs/TAGGING.md` (this file) and the per-phase close-task plans. |
| `.github/workflows/**` file additions / edits | `refusing to allow a GitHub App to create or update workflow ... without 'workflows' permission` on the branch push | Stage workflow files at a non-`.github/workflows/` path (e.g. `plans/workflows-pending/`); `git mv` them into `.github/workflows/` from a local clone and push. Occurrence: P4-T3. See `plans/P4-T3-PLAN.md` §Implementation note for exact commands. |

Future plans touching either class should bake the local-clone
workaround in upfront so the user can act on the workaround without
waiting for the failure.
