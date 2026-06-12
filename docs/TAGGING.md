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
| `claude-code-plugin/v0.8.0` | Plugin release `0.8.0` close (EARS-RT-001, MINOR) | Claude Code plugin — EARS layer team-mode + playbook injection. `doc-ears-audit/SKILL.md` (267 → 498 lines) gains `## Review Mode` (team mode default at gates) + `## Saga interaction` + `## Break-circuit policy` plus playbook injection (step 3a + augmented step 4); `doc-ears-fixer/SKILL.md` (113 → 298 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy` (mirrors PRD-RT-001 fixer pattern). 5 EARS playbook files: `requirements_specialist` 35 / `tech_lead` 25 / `qa_lead` 20 / `chaos_engineer` 12 / `security_engineer` 8 = 100 (chaos-heavy split per REVIEW_CREWS.yaml — failure-mode ACs dominate over abuse-case ACs at EARS). Lens→agent map: `requirements-analyst` / `solutions-architect` / `test-architect` / `chaos-engineer` / `security-engineer`. 5 audit SKILLs (BDD/ADR/SPEC/TDD/IPLAN) deferred to per-layer follow-up PRs. |
| `claude-code-plugin/v0.9.0` | Plugin release `0.9.0` close (BDD-RT-001, MINOR) | Claude Code plugin — BDD layer team-mode + playbook injection. `doc-bdd-audit/SKILL.md` (268 → 500 lines) gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` + playbook injection (step 3a + augmented step 4); `doc-bdd-fixer/SKILL.md` (118 → 304 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy` (mirrors EARS-RT-001 fixer pattern). 6 BDD playbook files: `qa_lead` 35 / `tech_lead` 25 / `chaos_engineer` 14 / `security_engineer` 6 / `operator` 10 / `auditor` 10 = 100. Chaos-HEAVY split (14 > 6, highest chaos weight of any layer per REVIEW_CREWS.yaml) reflects BDD failure-scenario emphasis. operator lens first appears at BDD — maps to `devops-release-engineer` plugin agent. Framework spec `0.14.1` → `0.14.2` (PATCH: BDD playbooks within existing §Playbooks artifact class). 4 audit SKILLs (ADR/SPEC/TDD/IPLAN) deferred to per-layer follow-up PRs. |
| `claude-code-plugin/v0.10.0` | Plugin release `0.10.0` close (ADR-RT-001, MINOR) | Claude Code plugin — ADR layer team-mode + playbook injection. `doc-adr-audit/SKILL.md` (268 → 500 lines) gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` + playbook injection (step 3a + augmented step 4); `doc-adr-fixer/SKILL.md` (113 → 299 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy` (mirrors BDD-RT-001 fixer pattern). 6 ADR playbook files: `architect` 35 / `tech_lead` 25 / `security_engineer` 12 / `operator` 10 / `auditor` 10 / `chaos_engineer` 8 = 100. Security-HEAVY split (12 > 8, first layer where security dominates over chaos per REVIEW_CREWS.yaml) reflects ADR encoding trust boundaries, authn/authz choices, and crypto decisions. Lens→agent map: `solutions-architect` (architect + tech_lead) / `security-engineer` / `devops-release-engineer` / `traceability-auditor` / `chaos-engineer`. Framework spec `0.14.2` → `0.14.3` (PATCH: ADR playbooks within existing §Playbooks artifact class). 3 audit SKILLs (SPEC/TDD/IPLAN) deferred to per-layer follow-up PRs. |
| `claude-code-plugin/v0.11.0` | Plugin release `0.11.0` close (SPEC-RT-001, MINOR) | Claude Code plugin — SPEC layer team-mode + playbook injection. `doc-spec-audit/SKILL.md` (267 → 502 lines) gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` + playbook injection (step 3a + augmented step 4); `doc-spec-fixer/SKILL.md` (115 → 305 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy` (mirrors ADR-RT-001 fixer pattern). 5 SPEC playbook files: `architect` 30 / `tech_lead` 30 / `integration_lead` 20 / `chaos_engineer` 10 / `security_engineer` 10 = 100. Equal chaos/security split (10/10) per REVIEW_CREWS.yaml — SPEC specifies both performance/resilience and security controls at equal weight. **Smallest crew of any layer** (5 lenses; no operator + no auditor at SPEC altitude). `integration_lead` first appears at SPEC — binds to `solutions-architect` (third lens sharing this agent alongside architect + tech_lead; brief specifies the lens at Task dispatch time). Framework spec `0.14.3` → `0.14.4` (PATCH: SPEC playbooks within existing §Playbooks artifact class). 2 audit SKILLs (TDD/IPLAN) deferred to per-layer follow-up PRs. |
| `claude-code-plugin/v0.12.0` | Plugin release `0.12.0` close (NECESSARY-UPSTREAM-001, MINOR) | Claude Code plugin — 15 SKILLs aligned with the necessary-upstream contract: 7 layer-author SKILLs (`doc-prd`/`doc-ears`/`doc-bdd`/`doc-adr`/`doc-spec`/`doc-tdd`/`doc-iplan`) drop "cumulative upstream tags" instructions, with frontmatter `upstream_artifacts:` shrunk to the necessary set per layer (EARS [PRD], BDD [EARS], ADR [EARS, BDD], SPEC [EARS, BDD, ADR], TDD [EARS, BDD, ADR, SPEC], IPLAN [SPEC, TDD]; PRD [BRD] unchanged). 8 layer audit/fixer SKILLs reword cumulative-tag references (fixer remediation tables now instruct adding tags missing from the layer's `required_tags`). Acceptance harness `tests/scripts/test-acceptance.sh` validator probe (line 1523) drops "cumulative" from its prompt; expected-count threshold reduced 20 → 10. Framework spec `0.15.2` → `0.16.0` (MINOR — necessary-upstream contract change in `LAYER_REGISTRY.yaml` + §7 templates + governance docs). `doc-tdd-audit` and `doc-tdd-fixer` deferred to TDD-RT-001 rebase (they live on `feat/tdd-rt-001`). |
| `framework/v0.16.0` | NECESSARY-UPSTREAM-001 close | Framework spec — replaces the cumulative-trace dependency contract (every downstream layer redeclares every upstream layer in `required_tags`) with **necessary upstream + transitive reachability**: each layer declares only what its own evaluation reads; lineage to layers further upstream is discoverable transitively through the @-tag chain (one hop per layer) and via the new `tools/trace_walk.py` for one-shot DAG-closure queries. `LAYER_REGISTRY.yaml` `required_tags` shrunk per layer; 7 layer templates' §7 Traceability blocks aligned with the new contract; ADR auditor C1 rewording; new `REVIEW_TEAM.md` §"Necessary upstream + transitive trace" section + `ADAPTATION_SURFACE.yaml` `cascade_rule` baseline restatement. New `sdd_doc_lint` rule `TRACE-RES-001` (corpus-level) provides deterministic structural-floor enforcement: every emitted `@<layer>: <ID>` tag must resolve on disk (host doc exists + element id declared in host); index docs excluded; runs at every layer regardless of crew shape. Existing conformance test `test_required_tags_are_cumulative` renamed → `test_required_tags_match_necessary_upstream_table`; new conformance file `test_layer_registry_necessary_upstream.py` adds template §7 block-shape assertions. Origin: TDD-RT-001 live cascade (2026-06-09) produced TDD-01 with `@prd: PRD.01.13.7760` referencing a non-existent `docs/02_PRD/PRD-01.md` — saga ended at PARTIAL_TIMEOUT with no convergence path because the cumulative contract forced trace fabrication when an upstream layer was genuinely absent. |
| `claude-code-plugin/v0.13.0` | Plugin release `0.13.0` close (TDD-RT-001, MINOR) | Claude Code plugin — TDD layer team-mode + playbook injection. `doc-tdd-audit/SKILL.md` (268 → ~500 lines) gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` + playbook injection (step 3a + augmented step 4); `doc-tdd-fixer/SKILL.md` (112 → ~298 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy` (mirrors SPEC-RT-001 fixer pattern). 6 TDD playbook files: `qa_lead` 35 / `tech_lead` 25 / `chaos_engineer` 10 / `security_engineer` 10 / `operator` 10 / `auditor` 10 = 100. Equal chaos/security split (10/10) per REVIEW_CREWS.yaml — `security_engineer` co-owns SECTEST (per its agent brief); failure-test cases balance security-test cases at executable-proof altitude. Six-lens crew (largest TDD-altitude crew shape) — `operator` verifies SLO emission + smoke/canary/rollback, `auditor` verifies BDD→TDD trace forward-completeness. Lens→agent map: `test-architect` (qa_lead) / `solutions-architect` (tech_lead) / `chaos-engineer` / `security-engineer` / `devops-release-engineer` (operator) / `traceability-auditor` (auditor). Framework spec `0.16.0` → `0.16.1` (PATCH: TDD playbooks within existing §Playbooks artifact class). Authored on top of NECESSARY-UPSTREAM-001 (framework 0.16.0) — playbooks land under the new necessary-upstream contract from the start; `doc-tdd-audit`/`doc-tdd-fixer` have no cumulative-tag prose to scrub (predicted clean by Pass 2 of NECESSARY-UPSTREAM-001, confirmed on rebase). 1 audit SKILL (IPLAN) deferred to per-layer follow-up PR. |
| `framework/v0.16.1` | TDD-RT-001 close (PATCH) | Framework spec — 6 TDD playbooks (`framework/playbooks/07_TDD/`: qa_lead, tech_lead, chaos_engineer, security_engineer, operator, auditor) added within the existing §Playbooks artifact class. Crew weights match `REVIEW_CREWS.yaml` TDD entry. Playbook frontmatter declares `framework_spec_version: "0.16.1"`. |
| `framework/v0.17.0` | FRAMEWORK-FEEDBACK-LOG-001 close (MINOR) | Framework spec — new governance Principle 9 in `DOC_GOVERNANCE_CORE.md` (example-driven / project-driven framework improvement); new dedicated doc `framework/governance/FRAMEWORK_FEEDBACK_LOG.md` codifying the two-tier feedback pipeline (Tier 1: consumer-project `framework-feedback-log.md`; Tier 2: framework-side `plans/FRAMEWORK-TODO.md`); new consumer-project scaffold `framework/templates/framework-feedback-log.template.md` (first entry in the `framework/templates/` directory). Origin: project-side observation that friction discovered across many cascades + multiple per-layer rollouts was evaporating between sessions; same issues kept resurfacing in new work. The two-tier pipeline converts example-driven and project-driven discovery into durable framework improvement. |
| `claude-code-plugin/v0.13.1` | TRACE-RES-FIXUP-001 close (PATCH) | Claude Code plugin — TRACE-RES-001 lint rule now correctly skips downstream tags (e.g. SPEC-01 emitting `@tdd: TDD-01` before the cascade has generated TDD-01); downstream pointers are informational forward references, not upstream lineage. Self-tags resolve naturally via `doc_index`; sibling references still resolve against `doc_index`. Synced to both vendored copies. `examples/url-shortener/docs/` regenerated end-to-end (PRD→TDD, 5h 1m wall clock): PRD 92 / EARS 94 / BDD 91 / ADR 96 / SPEC 97 / TDD 90 (all PASS). Temporary `SDD_LINT_SKIP_TRACE_RES=1` env-var bypass removed. New `plans/FRAMEWORK-TODO.md` seeded as Tier 2 of the FRAMEWORK-FEEDBACK-LOG-001 pipeline (8 framework-improvement items captured from the NECESSARY-UPSTREAM-001 → TDD-RT-001 → this work sequence). |
| `framework/v0.17.1` | IPLAN-RT-001 close (PATCH) | Framework spec — 6 IPLAN playbooks (`framework/playbooks/08_IPLAN/`: tech_lead, architect, operator, integration_lead, auditor, chaos_engineer) added within the existing §Playbooks artifact class. Crew weights match `REVIEW_CREWS.yaml` IPLAN entry (sum 100; no security_engineer per IPLAN crew comment — threat-model upstream in ADR/SPEC; new integration_lead lens unique to IPLAN). Playbook frontmatter declares `framework_spec_version: "0.17.1"`. With this PATCH, LAYER-PLAYBOOKS-001 reaches 45 of 45 playbooks across all 8 layers (BRD 5 + PRD 6 + EARS 5 + BDD 6 + ADR 6 + SPEC 5 + TDD 6 + IPLAN 6). |
| `claude-code-plugin/v0.14.0` | IPLAN-RT-001 close (MINOR) | Claude Code plugin — final 8/8 layer rollout: IPLAN layer team-mode + playbook injection. `doc-iplan-audit/SKILL.md` (270 → 551 lines) gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` + playbook injection (step 3a + augmented step 4); `doc-iplan-fixer/SKILL.md` (112 → 310 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy` (mirrors TDD-RT-001 pattern). Lens→agent map: tech_lead + architect + integration_lead → `solutions-architect` (three lens-roles dispatched as three Task subagent invocations with lens-specific playbook briefs); `operator` → `devops-release-engineer`; `auditor` → `traceability-auditor`; `chaos_engineer` → `chaos-engineer`. Six-lens crew (largest at any layer). `@unittest.skip` removed from `tests/conformance/test_playbook_coverage.py:35` (task #258 closing cleanup) — conformance suite gains its 121st active test (`test_every_crew_lens_has_a_playbook_file` now enforces all 45 playbooks). `docs/PARITY.md` Layer Playbooks row title corrected from stale `(BRD/PRD/EARS)` to `(all 8 layers)`. Closes the LAYER-PLAYBOOKS-001 workstream. |
| `claude-code-plugin/v0.14.1` | CLEANUP-PR-A close (PATCH) | Claude Code plugin — first child PR of FRAMEWORK-CLEANUP-001 (master PR #128). Closes `plans/FRAMEWORK-TODO.md` items #1-4 (harness + lint workflow hygiene). New `--skip-lint-smoke` flag in `tests/scripts/test-acceptance.sh` (item 1, replaces deprecated `SDD_LINT_SKIP_TRACE_RES=1` env-var pattern). New "Cleanup-then-cascade pattern" subsection in `tests/ACCEPTANCE.md` documenting the `rm -rf <layer>` → `--force` sequence (item 2). DO-NOT-EDIT banners on canonical vendored Python modules (`tools/sdd_doc_lint/__init__.py`, `tools/saga_driver.py`) + new `platforms/claude-code-plugin/framework/_VENDORED.md` README (item 3 — clarifies the byte-identity contract for vendored copies). 18 audit + fixer SKILL prompts gain a `### Table-pipe escape (MD056)` subsection instructing the LLM author to escape `\|` inside code spans within markdown table cells (item 4 — root-cause fix for the MD056 cascade output issue surfaced in IPLAN-RT-001 PR #127). No framework spec change. |
| `framework/v0.18.0` | CLEANUP-PR-C close (MINOR) | Framework spec — second child PR of FRAMEWORK-CLEANUP-001 (master PR #128). Closes `plans/FRAMEWORK-TODO.md` items #11-14 (spec/registry/template hygiene). Item 11: `REVIEW_REMEDIATION_FLOW.md` §The quality loop gains a new "Iteration cap" subsection elevating the previously-impl-bound `MAX_ITERATIONS=3` to spec; new `ADAPTATION_SURFACE.yaml` knob `quality_loop_max_iterations` (range 1-10, default 3) makes the cap project-tunable. Item 12: new `id_patterns.threshold` in `LAYER_REGISTRY.yaml` (`TYPE.NN.<lowercase_category>.<lowercase_key>`) distinguishes threshold keys from 4-segment hex-hash element IDs; `sdd_doc_lint` TH01 check upgraded to use the strict regex. Item 13: new "Element-ID exemptions" subsection in `ID_NAMING_STANDARDS.md` formalizing that SPEC §5 rules + IPLAN §4 contracts MAY but are not required to carry layer-local element IDs. Item 14: new "Optional downstream slots" subsection in `REVIEW_TEAM.md` + new `optional_downstream_slots:` per-layer field in `LAYER_REGISTRY.yaml` (only EARS opts in, with slots toward BDD) formalizing the existing-but-undeclared EARS `@bdd:` slot pattern. |
| `claude-code-plugin/v0.15.0` | CLEANUP-PR-C close (MINOR) | Claude Code plugin — companions framework/v0.18.0. `tools/saga_driver.py` gains `_resolve_max_iterations(profile_path)` helper that loads `.aidoc/profile.yaml` and reads the new `quality_loop_max_iterations` knob; falls back to default 3 for missing-file / malformed-yaml / missing-field / out-of-range (1-10). `tools/sdd_doc_lint/__init__.py` TH01 check upgraded to use the strict threshold regex (rejects mixed-case categories). Both vendored mirrors re-synced via `sync-vendored.sh`. |
| `framework/v0.19.0` | CLEANUP-PR-B close (MINOR) | Framework spec — third child PR of FRAMEWORK-CLEANUP-001 (master PR #128). Closes `plans/FRAMEWORK-TODO.md` items #5-10 — review-quality calibration (the heart). `REVIEW_TEAM.md` §Operations gains 3 new subsections: "Strip author self-claim before lens fan-out" (item 9 — anchor-effect fix), "No-findings rationale" (item 8 — convergence-theater fix; cap at 95 when 100/0 lacks rationale), "Fixer-introduced regressions" (item 10 — `fixer_introduced: true` field + `## Regressions` report section). 13 playbook files (6 × auditor + 7 × tech_lead) gain `## No-findings rationale` section. `framework/playbooks/07_TDD/auditor.md` C4 + Reasoning frame + C1 updated from cumulative-trace pre-0.16.0 wording to necessary-upstream contract (item 7). |
| `claude-code-plugin/v0.16.0` | CLEANUP-PR-B close (MINOR) | Claude Code plugin — companions framework/v0.19.0. 9 audit SKILLs (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN/CHG) gain `### Strip author self-claim before lens dispatch` subsection (item 9) + `### Regressions` subsection in Combined Report Format (item 10). `agents/synthesizer.md` extended with: no-findings-rationale check that caps `lens_score` at 95 when missing rationale on 100/0 outputs (item 8); fixer-introduced regression detection comparing iter-N finding locations to iter-(N-1) Fixes Applied entries (item 10). `CLAUDE.md` §Development workflow item 2 gains Corpus cross-check + Empirical pass-count baseline paragraphs (items 5 + 6). |
| `framework/v0.19.1` | CLEANUP-PR-E close (PATCH) | Framework spec — fourth child PR of FRAMEWORK-CLEANUP-001 (master PR #128). Closes `plans/FRAMEWORK-TODO.md` item #17 — IPLAN sub-types. `IPLAN-TEMPLATE.yaml` gains `subtype: code_build \| deploy \| combined` field (default combined for backward compat) + `_required_when_subtype:` markers on 4 existing sections + 5 new deploy-only sections (rollback_procedure, smoke_tests, canary_metrics, observability_hooks, runbook_reference). Backward compat preserved: existing IPLANs without subtype default to combined. |
| `claude-code-plugin/v0.16.1` | CLEANUP-PR-E close (PATCH) | Claude Code plugin — companions framework/v0.19.1. `doc-iplan/SKILL.md` Creation Process gains "Select subtype" step (4). `doc-iplan-audit/SKILL.md` Structural Checklist gains subtype-aware section dispatch (reads `document_control.subtype`; defaults to `combined`). IPLAN playbooks (operator, chaos_engineer, integration_lead) gain `### Subtype awareness` subsection — at `code_build` subtype, deploy concerns are explicit out of scope; lens MAY return 100/0 with rationale `"subtype: code_build — deploy concerns out of scope"` (composes with CLEANUP-PR-B item 8 no-findings-rationale rule). |
| `framework/v0.20.0` | CLEANUP-PR-D close (MINOR) | Framework spec — fifth child PR of FRAMEWORK-CLEANUP-001 (master PR #128). Closes items #15-16 and opens item #19 (Option B future). PRD-TEMPLATE.yaml gains OPTIONAL `component_decomposition` section (§7b) with components + named thresholds (`full_id: PRD.NN.<cat>.<key>`). REVIEW_TEAM.md §Operations gains 'Threshold-resolution gate' subsection. DECISION-GATE-D resolved as Option A (subsection in PRD); Option B (new `02b_DECOMP` layer) deferred. |
| `claude-code-plugin/v0.17.0` | CLEANUP-PR-D close (MINOR) | Claude Code plugin — companions framework/v0.20.0. New `sdd_doc_lint` corpus-level rule TH-RES-001 (`tools/sdd_doc_lint/__init__.py`) validates every downstream `@threshold:` citation resolves to a `full_id:` entry in host PRD's `component_decomposition` section. Citation-driven: PRDs with no downstream threshold cites pass automatically. P2 (host PRD missing section) + P1 (section present, key not declared) severities. New `tests/unit/test_threshold_resolution.py` covers 4 cases. |
| `framework/v0.20.1` | CLEANUP-PR-F close (PATCH) | Framework spec — single-item follow-up closing `plans/FRAMEWORK-TODO.md` item #18 (doc-number independence across layers). New §"Cross-layer cardinality" subsection in `ID_NAMING_STANDARDS.md` documents per-layer independent doc numbering + one-to-many + many-to-one cross-layer relationships + that the url-shortener example's 1:1 alignment is coincidence. 6 auditor playbooks gain orphan-vs-sibling notes; `TRACEABILITY.md` cross-references the new subsection. |
| `claude-code-plugin/v0.17.1` | CLEANUP-PR-F close (PATCH) | Claude Code plugin — companions framework/v0.20.1. 8 doc-<layer> author SKILLs gain one-line clarification in the Reserve ID step pointing to the new ID_NAMING_STANDARDS §Cross-layer cardinality subsection. |
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
