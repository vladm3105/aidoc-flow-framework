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

## [0.22.0] — 2026-06-22

### Added

- **MODEL-PRECHECK-ROLLOUT — the 8 layer autopilots now surface the per-layer
  model recommendation.** Each `doc-<layer>-autopilot` gains a `## Model
  precheck` section (before `## Workflow`) that reads `model.per_layer` /
  `model.default` / `model.precheck` from `.claude/aidoc-flow.config.yaml` and
  **prints** the recommendation + the `/model <rec>` switch command before
  invoking the driver. It does **not** compare against the session model (a
  skill can't read its own model id) — it surfaces the recommendation and lets
  the user decide. `precheck` modes: `warn` (print + proceed, default) ·
  `silent` (nothing) · `block` (print + wait for confirmation). Closes the
  documented-but-unimplemented `precheck` behavior described in
  `commands/model.md`.
- `tests/conformance/platforms/test_model_precheck.py` — asserts all 8
  autopilots carry the section, reference the config keys, and place it before
  the saga-driver invocation.

### Changed

- Each autopilot's Step-1 saga directive reworded from "VERY FIRST tool call"
  to "first **orchestration** action MUST be Bash", so the precheck notice may
  run before the driver without being read as bypassing it.

### Notes

- Scope is **autopilots-only**. Base/audit/fixer skills run headless under the
  saga driver in the normal flow (where a notice is pointless and `block` can't
  ask), so they're deferred. Advisory only — the plugin cannot switch the
  session model.

## [0.21.0] — 2026-06-22

### Changed

- **SAGA-PARITY-001 Phase 4 — the 6 remaining layer autopilots now drive the
  saga driver.** `doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot` previously
  described only a legacy in-session generation loop, while only `brd`/`prd`
  invoked `tools/saga_driver.py`. The acceptance harness masked this — it
  shells the driver directly per layer, *not* through the autopilot SKILL — so
  a human running `/aidoc-flow:doc-bdd-autopilot` got an untested path that
  diverged from the one the suite proves. Each of the 6 `## Workflow` sections
  is now the proven two-subsection shape: a `### Saga-driven generation loop`
  (`review_mode: team`, the default) that invokes
  `saga_driver.py --layer <NN_TYPE>`, plus the existing steps retained verbatim
  under `### Linear Pipeline` (`review_mode: single_pass`). All 8 layer
  autopilots now behave identically.
- **`review_mode` added to `adapts:` frontmatter** of the 6 migrated SKILLs and
  reconciled into `doc-prd-autopilot` (it branched on `review_mode` without
  declaring it; `doc-brd-autopilot` already declared it).

### Added

- `tests/conformance/platforms/test_autopilot_saga_parity.py` — asserts all 8
  layer autopilots carry the saga block with the correct `--layer <NN_TYPE>`,
  retain the `single_pass` fallback, and declare `review_mode` in `adapts:`.

## [0.20.1] — 2026-06-14

### Fixed

- **`README.md` Platform info table — `Version` cell drift.** The cell had
  been stuck at `0.6.3` since plugin v0.7.0 (~14 version bumps ago)
  because `scripts/sync-version-refs.sh` only awk'd bare `^X.Y.Z$` lines
  in this README (for the `$ cat VERSION` example block), missing the
  inline table cell. This release canonicalizes the cell to the tag form
  `claude-code-plugin/v0.20.1`.
- **`scripts/sync-version-refs.sh` extended** to also propagate
  `claude-code-plugin/v<X.Y.Z>` references in
  `platforms/claude-code-plugin/README.md` and `hermes/v<X.Y.Z>` in
  `platforms/hermes/README.md`. Closes the recurrence class — by
  canonicalizing the Platform info cell to the tag form (which the
  sync script already covered for root README.md / PARITY.md), future
  bumps update the platform README automatically.

### Surfaced (out of scope for this PATCH)

- `platforms/hermes/README.md:107-108` carries the same drift bug
  (`hermes/v0.1.0` vs actual `0.3.0`; `framework spec 0.1.0` vs actual
  `0.21.1`). Tracked as `HERMES-README-VERSION-DRIFT` in
  `plans/FRAMEWORK-TODO.md`. The extended sync script will auto-fix the
  tag form at Hermes's next VERSION bump per the plugin-first rule.
  The framework-spec cell needs a separate sync pattern (not added here).

## [0.20.0] — 2026-06-14

### Changed

- **`/aidoc-flow:bug-report` and `/aidoc-flow:feedback` now accept a
  user prompt argument and draft a full GitHub issue from it.** The LLM
  composes a concise title and a structured body using the user's
  one-line input, the current conversation context (recent commands,
  errors, files referenced), and the environment / version stamp. The
  resulting title and body are URL-encoded into `?title=&body=` so the
  GitHub `issues/new` form opens with both fields prefilled. The user
  reviews on github.com and clicks Submit; the plugin never auto-submits.
- **Preview step.** Both commands now print the drafted title + body in
  chat before the URL, so the user can sanity-check the LLM's draft
  before clicking through. Anything wrong gets edited on github.com.
- **Refined GitHub issue templates** (`.github/ISSUE_TEMPLATE/bug_report.md`,
  `.github/ISSUE_TEMPLATE/feedback.md`) — section structure aligned with
  what the LLM drafts, so direct-on-GitHub fillers also benefit and the
  prefilled body reads naturally inside the template.
- **Secret-redaction guardrail.** Both commands explicitly do not include
  log content, file contents, or paths that look like secrets (anything
  matching `(token|secret|key|password|api[_-]?key)`); such fragments are
  replaced with `(redacted)` in the drafted body.

### Supersedes

The unreleased `[0.19.1]` PATCH (URL-prefill of a static env block via
`&body=`) is superseded by this MINOR release — same `&body=` machinery,
but the body content is now LLM-drafted from the user's prompt, not a
static four-line env stamp. Argument-accepting commands are new behaviour;
hence MINOR rather than PATCH.

## [0.19.0] — 2026-06-14

### Added — PLUGIN-USER-COMMANDS

- **11 user-facing commands** under `commands/`, all namespaced `/aidoc-flow:<name>`:
  - Meta: `about`, `help`, `bug-report`, `contact-us`, `feedback`
  - Workflow: `status`, `next`
  - Lifecycle: `uninstall`
  - Config: `configure`, `budget`, `model`
- **Optional project-local config file** `.claude/aidoc-flow.config.yaml` —
  read/written by `/configure`, `/budget`, `/model`; ignored by every other
  skill. Schema, defaults, and enums documented in `docs/CONFIG.md`.
- **`.github/ISSUE_TEMPLATE/feedback.md`** — backend for `/aidoc-flow:feedback`
  (separate from the existing `bug_report.md`).
- **Conformance test** `tests/conformance/platforms/test_plugin_config_schema.py`
  — fails CI if `docs/CONFIG.md` and the three config command files drift on
  schema keys, defaults, or enum values.

### Honest caveats baked into the commands

- `/aidoc-flow:budget` is a **behavior knob** (skips optional passes, terser
  output), not a token-budget cap. The plugin has no token-meter hook.
- `/aidoc-flow:model` is **advisory**. The plugin cannot switch the Claude
  Code session model; the command records the per-layer recommendation and
  prints copy-paste native `/model <id>` commands.
- `/aidoc-flow:uninstall` is a **guided exit**. The native
  `/plugin uninstall aidoc-flow@aidoc-flow-framework` does the actual removal.

### Out of scope (tracked, deferred)

- Per-skill model/budget preflight rollout — config keys are introduced;
  wiring the preflight line into every `doc-*` SKILL is a follow-on
  (`plans/FRAMEWORK-TODO.md` — `MODEL-PRECHECK-ROLLOUT`).
- Cross-platform parity in Hermes (plugin-first; tracked in
  `plans/HERMES-BACKLOG.md`).
- GitHub Discussions backend for `/feedback` (Issues + template is v1).

## [0.18.0] — 2026-06-12

### Added

- **CHG layer team-mode + playbook injection (CHG-RT-001).** `doc-chg-audit/SKILL.md` (200 → 693 lines) gains `## Review Mode` + `## Saga interaction` + `## Break-circuit policy` + `## Content Sub-Checks` (A1/A2/A3/BA1/SE1) + playbook injection. `doc-chg-fixer/SKILL.md` (125 → 344 lines) gains `## Remediate Mode` + `## Saga interaction` + `## Break-circuit policy`. `doc-chg-autopilot/SKILL.md` (116 → 191 lines) gains saga-driven generation loop invoking `python3 saga_driver.py --layer 09_CHG`.
- `tools/saga_driver.py` `_LAYER_CREWS` gains `"09_CHG"` entry with the 6 personas matching `REVIEW_CREWS.yaml` CHG crew.
- CHG-RT-001 live cascade against url-shortener: PASS @ iter 3 score 95, 0 blocking findings; `examples/url-shortener/docs/09_CHG/CHG-01.md` is the first end-to-end CHG cascade output in framework history.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.20.1` → `0.21.0` (consumes new CHG crew + 6 new playbooks under `framework/playbooks/09_CHG/`).

## [0.17.1] — 2026-06-12

### Changed

- **Doc-number independence clarification (CLEANUP-PR-F).** 8 `doc-<layer>` author SKILLs gain a one-line clarification in the Reserve ID step pointing to the new `ID_NAMING_STANDARDS.md` §"Cross-layer cardinality" subsection — doc numbers are per-layer sequential and INDEPENDENT across layers; one-to-many + many-to-one cross-layer relationships both supported.
- `FRAMEWORK_SPEC_VERSION` `0.20.0` → `0.20.1`.

### Fixed

- **PR-E STRUCT01 regression** caused by IPLAN sub-types' `_required_when_subtype:` markers — `tools/sdd_doc_lint/__init__.py` `_load_section_targets()` now honors the marker (skips conditionally-required sections; defers subtype-aware check to the layer's audit SKILL).

## [0.17.0] — 2026-06-11

### Added

- **Threshold-resolution gate TH-RES-001 (CLEANUP-PR-D).** New `sdd_doc_lint` corpus-level rule (`tools/sdd_doc_lint/__init__.py`) — validates every downstream `@threshold: PRD.NN.<cat>.<key>` citation resolves to a `full_id:` entry in the host PRD's `component_decomposition` section. Citation-driven: PRDs with no downstream threshold cites pass automatically. P2 (host PRD missing section) + P1 (section present, key not declared).
- `tests/unit/test_threshold_resolution.py` — 4 unit tests.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.19.1` → `0.20.0` (new optional `component_decomposition` section in PRD template).

## [0.16.1] — 2026-06-11

### Added

- **IPLAN sub-types (CLEANUP-PR-E).** `doc-iplan/SKILL.md` Creation Process gains "Select subtype" step — `code_build` / `deploy` / `combined`. `doc-iplan-audit/SKILL.md` Structural Checklist gains subtype-aware section dispatch (reads `document_control.subtype`; defaults to `combined`).
- IPLAN playbooks (operator, chaos_engineer, integration_lead) gain `### Subtype awareness` subsection — at `code_build` subtype, deploy concerns are explicit out of scope.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.19.0` → `0.19.1` (template `subtype` field + 5 new deploy-only sections).

## [0.16.0] — 2026-06-11

### Added

- **Review-quality calibration (CLEANUP-PR-B — heart of FRAMEWORK-CLEANUP-001).** 9 audit SKILLs (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN/CHG) gain `### Strip author self-claim before lens dispatch` subsection (anchor-effect fix) + `### Regressions` subsection in Combined Report Format.
- `agents/synthesizer.md` extended with:
  - **No-findings-rationale check** — caps `lens_score` at 95 when 100/0 output lacks `no_findings_rationale` field; emits `STRUCTURE-RAT-001` advisory.
  - **Fixer-introduced regression detection** — compares iter-N finding locations to iter-(N-1) "Fixes Applied" entries; sets `fixer_introduced: true`; caps affected lens score at iter-(N-1) value.
- `CLAUDE.md` §Development workflow gains Corpus cross-check + Empirical pass-count baseline paragraphs.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.18.0` → `0.19.0` (new REVIEW_TEAM.md §Operations subsections + 13 playbook content additions + TDD auditor C4/C1/Reasoning frame aligned with necessary-upstream contract).

## [0.15.0] — 2026-06-11

### Added

- **Spec / registry / template hygiene (CLEANUP-PR-C).** `tools/saga_driver.py` gains `_resolve_max_iterations(profile_path)` helper — loads `.aidoc/profile.yaml`, reads the new `quality_loop_max_iterations` knob (range 1-10, default 3); falls back to default for missing-file / malformed-yaml / missing-field / out-of-range.
- `tools/sdd_doc_lint/__init__.py` TH01 check upgraded to use a strict threshold regex (rejects mixed-case categories).

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.17.1` → `0.18.0`.

## [0.14.1] — 2026-06-11

### Added

- **Harness + lint workflow hygiene (CLEANUP-PR-A).** New `--skip-lint-smoke` flag in `tests/scripts/test-acceptance.sh` (replaces deprecated `SDD_LINT_SKIP_TRACE_RES=1` env-var pattern).
- "Cleanup-then-cascade pattern" subsection in `tests/ACCEPTANCE.md` (`rm -rf <layer>` → `--force` sequence).
- DO-NOT-EDIT banners on canonical vendored Python modules + new `framework/_VENDORED.md` README clarifying the byte-identity contract.
- 18 audit + fixer SKILL prompts gain `### Table-pipe escape (MD056)` subsection (root-cause fix for cascade-output MD056 issue).

## [0.14.0] — 2026-06-11

### Added

- **IPLAN layer team-mode + playbook injection (IPLAN-RT-001).** Final 8/8 layer rollout closing the LAYER-PLAYBOOKS-001 workstream. `doc-iplan-audit/SKILL.md` (270 → 551 lines) + `doc-iplan-fixer/SKILL.md` (112 → 310 lines) gain the team-mode + saga + playbook injection shape.
- 6 IPLAN playbook files: tech_lead 30 / architect 25 / operator 15 / integration_lead 12 / auditor 10 / chaos_engineer 8 = 100 (no security_engineer per IPLAN crew — threat model upstream in ADR/SPEC).

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.17.0` → `0.17.1` (final IPLAN playbooks land within existing §Playbooks artifact class).
- `@unittest.skip` removed from `tests/conformance/test_playbook_coverage.py` — conformance now actively enforces all 45 playbooks.

## [0.13.1] — 2026-06-10

### Fixed

- **TRACE-RES-001 downstream-skip (TRACE-RES-FIXUP-001).** Lint rule now correctly skips downstream tags (e.g., SPEC-01 emitting `@tdd: TDD-01` before TDD-01 has been generated); downstream pointers are informational forward references, not upstream lineage.

### Changed

- `examples/url-shortener/docs/` regenerated end-to-end (PRD→TDD, 5h 1m wall clock): PRD 92 / EARS 94 / BDD 91 / ADR 96 / SPEC 97 / TDD 90 (all PASS).
- Temporary `SDD_LINT_SKIP_TRACE_RES=1` env-var bypass removed.

## [0.13.0] — 2026-06-10

### Added

- **TDD layer team-mode + playbook injection (TDD-RT-001).** `doc-tdd-audit/SKILL.md` (268 → ~500 lines) + `doc-tdd-fixer/SKILL.md` (112 → ~298 lines) gain the team-mode shape.
- 6 TDD playbook files: qa_lead 35 / tech_lead 25 / chaos_engineer 10 / security_engineer 10 / operator 10 / auditor 10 = 100. Equal chaos/security split — security_engineer co-owns SECTEST.
- Authored on top of NECESSARY-UPSTREAM-001; playbooks land under the new necessary-upstream contract from the start.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.16.0` → `0.16.1`.

## [0.12.0] — 2026-06-09

### Changed

- **Necessary-upstream contract alignment (NECESSARY-UPSTREAM-001).** 15 SKILLs aligned with the new contract: 7 layer-author SKILLs drop "cumulative upstream tags" instructions; `upstream_artifacts:` frontmatter shrunk to the necessary set per layer (EARS [PRD], BDD [EARS], ADR [EARS, BDD], SPEC [EARS, BDD, ADR], TDD [EARS, BDD, ADR, SPEC], IPLAN [SPEC, TDD]; PRD [BRD] unchanged).
- 8 layer audit/fixer SKILLs reword cumulative-tag references; fixer remediation tables now instruct adding tags missing from `required_tags`.
- Acceptance harness validator probe drops "cumulative" from prompt; expected-count threshold reduced 20 → 10.
- `FRAMEWORK_SPEC_VERSION` `0.15.2` → `0.16.0` (MINOR — necessary-upstream contract change in `LAYER_REGISTRY.yaml` + §7 templates + governance docs).

## [0.11.0] — 2026-06-09

### Added

- **SPEC layer team-mode + playbook injection (SPEC-RT-001).** `doc-spec-audit/SKILL.md` (267 → 502 lines) + `doc-spec-fixer/SKILL.md` (115 → 305 lines) gain the team-mode shape.
- 5 SPEC playbook files: architect 30 / tech_lead 30 / integration_lead 20 / chaos_engineer 10 / security_engineer 10 = 100. Equal chaos/security split. **Smallest crew of any layer** (5 lenses; no operator + no auditor at SPEC altitude).
- `integration_lead` first appears at SPEC — binds to `solutions-architect` (third lens sharing this agent alongside architect + tech_lead).

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.14.3` → `0.14.4`.

## [0.10.0] — 2026-06-08

### Added

- **ADR layer team-mode + playbook injection (ADR-RT-001).** `doc-adr-audit/SKILL.md` (268 → 500 lines) + `doc-adr-fixer/SKILL.md` (113 → 299 lines) gain the team-mode shape.
- 6 ADR playbook files: architect 35 / tech_lead 25 / security_engineer 12 / operator 10 / auditor 10 / chaos_engineer 8 = 100. **Security-heavy** split (first layer where security dominates over chaos) — ADRs encode trust boundaries, authn/authz choices, crypto decisions.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.14.2` → `0.14.3`.

## [0.9.0] — 2026-06-08

### Added

- **BDD layer team-mode + playbook injection (BDD-RT-001).** `doc-bdd-audit/SKILL.md` (268 → 500 lines) + `doc-bdd-fixer/SKILL.md` (118 → 304 lines) gain the team-mode shape.
- 6 BDD playbook files: qa_lead 35 / tech_lead 25 / chaos_engineer 14 / security_engineer 6 / operator 10 / auditor 10 = 100. **Chaos-heavy** split (14 > 6, highest chaos weight of any layer) — reflects BDD failure-scenario emphasis.
- `operator` lens first appears at BDD — maps to `devops-release-engineer` plugin agent.

### Changed

- `FRAMEWORK_SPEC_VERSION` `0.14.1` → `0.14.2`.

## [0.8.0] — 2026-06-08

### Added

- Playbook injection wired into doc-ears-audit + doc-ears-fixer SKILLs.
  doc-ears-audit (267 → 498 lines): `## Review Mode` (team mode default
  at gates) + `## Saga interaction` + `## Break-circuit policy` + step
  3a playbook load + augmented step 4 brief composition with
  `## Layer-specific playbook` section.
  doc-ears-fixer (113 → 298 lines): `## Remediate Mode` + `## Saga
  interaction` + `## Break-circuit policy` (mirrors PRD-RT-001 fixer).
- 5 EARS playbook files at framework/playbooks/03_EARS/: requirements_
  specialist (35), tech_lead (25), qa_lead (20), chaos_engineer (12),
  security_engineer (8). Each ~95-110 lines with hybrid content shape
  (reasoning frame + Cn checks + beyond-checklist + scoring rubric).

### Changed

- `FRAMEWORK_SPEC_VERSION` 0.14.0 (unchanged — consumes existing
  Playbooks spec from LAYER-PLAYBOOKS-001).

### Verified

- Live EARS cascade ran 5 iterations end-to-end: draft → audit
  (iter-1) → fixer (iter-1) → re-audit (iter-2) → fixer (iter-2) →
  re-audit (iter-3 with SE-001 P1) → hand-fix #1 (abuse-case pair) →
  iter-4 re-audit (SE-001 resolved, STRUCT-001 P1 surfaced) →
  hand-fix #2 (ID format) → iter-5 re-audit (terminal at MAX_ITERATIONS;
  score 84/100, blocking=0, all P1s resolved). security_engineer
  perfect 100/100. playbook_coverage populated for first time:
  `{C1:2, C2:4, C3:1, C4:2, C5:6, beyond_checklist:1}`.

### Deferred

- 5 audit SKILLs (doc-{bdd,adr,spec,tdd,iplan}-audit) lack team-mode
  wiring; per-layer follow-up PRs (BDD-RT-001 through IPLAN-RT-001)
  will land team-mode + playbooks together.

## [0.7.0] — 2026-06-07

### Added

- Playbook injection in doc-brd-audit + doc-prd-audit SKILLs. Each
  audit SKILL's team-mode flow now loads
  `framework/playbooks/<NN>_<LAYER>/<lens>.md` and inlines the content
  into each lens subagent's Task brief.
- `tools/playbook_loader.py` — stdlib helper for path resolution +
  missing-file handling.
- `tools/finding_filter.py` — synthesizer's check-citation filter +
  coverage-emission helper.
- `agents/synthesizer.md` — schema-enforcement (`findings[].check`
  required; discards uncited) + `verdict.playbook_coverage` emission
  - `### Discarded findings` subsection in report.md.

### Changed — Plugin 0.7.0

- `FRAMEWORK_SPEC_VERSION` 0.13.1 → 0.14.0 (consumes new framework
  spec containing §Playbooks contract).

### Deferred

- 6 audit SKILLs (EARS/BDD/ADR/SPEC/TDD/IPLAN) lack team-mode
  wiring; playbook injection for those layers ships per-layer in
  follow-up PRs.

### Changed — Plugin v0.6.4 → v0.6.5

> **SemVer classification**: PATCH bump — harness change only;
> no SKILL surface changes, no framework spec touch. The autopilot
> SKILL is unmodified; only `tests/scripts/test-acceptance.sh` changes.

#### Why

The 2026-06-07 PRD-RT-001 verification (PR #101) surfaced an
LLM-stochasticity issue in the harness's driver-invocation path. The
autopilot SKILL has been the harness's entry point since v0.6.1
(Amendment 1): the harness invokes `claude -p
/aidoc-flow:doc-<layer>-autopilot ...`, the autopilot LLM then runs
`Bash: python3 saga_driver.py ...`. Same SKILL prompt produced
different LLM behavior across runs — BRD v0.6.1 worked, PRD v0.6.4
failed (LLM chose `run_in_background=true` and exited before driver
completed, relying on a notification that doesn't fire in `claude
-p` mode).

This is the same class of issue as B1 (cooperative-enforcement is
non-deterministic at the protocol-contract granularity required by
REVIEW_SAGA.md). Same fix shape: take the LLM out of the contract-
enforcement path.

#### What changed

`tests/scripts/test-acceptance.sh` cascade dispatcher invokes
`python3 saga_driver.py --layer NN_LAYER --threshold 90` DIRECTLY
with the same env-var setup (`PREV_OUTPUT`, `ARTIFACT_ID`,
`ARTIFACT_PATH`, `CLAUDE_PLUGIN_ROOT`). The autopilot LLM is no
longer in the harness's driver-invocation path. The harness:

- Tracks the driver subprocess as the `doc-<layer>-autopilot`
  element in the run summary (for output continuity).
- Records the subprocess stdout to
  `logs/<TS>/elements/doc-<layer>-autopilot.stdout`.
- Treats `timeout` (rc=124) as FAIL with an explicit "driver
  timeout" note.
- Honors `$ORCHESTRATOR_TIMEOUT` (currently 3600s) as the outer
  wall-clock cap; the driver's own `SOFT_DEADLINE=3300s` is the
  inner soft cap.

#### What stays the same

- The autopilot SKILL (`doc-<layer>-autopilot/SKILL.md`) is
  unchanged — it remains the user-facing entry point for
  `/aidoc-flow:doc-<layer>-autopilot` interactive invocation in a
  Claude Code session. Users get the same behavior they had before.
- The driver itself (`tools/saga_driver.py`) is unchanged.
- Every other harness flow (mock mode, dry-run, single-element,
  CHG cascade, utilities, agents) is unaffected.

#### Why this is safe

The driver is layer-agnostic: its `_LAYER_CREWS` covers all 8 layers
(verified by `test_layer_crews_match_yaml`). The driver IS the saga-
lifecycle implementation per `framework/governance/REVIEW_SAGA.md` —
invoking it directly is invoking the same authoritative
implementation that the autopilot SKILL used to invoke.

#### Unblocks

Live verification for EARS-RT-001 / BDD-RT-001 / ADR-RT-001 /
SPEC-RT-001 / TDD-RT-001 / IPLAN-RT-001 propagation. Each per-layer
RT PR can now run an end-to-end cascade without the
LLM-stochasticity risk in the dispatch path.

#### Verification

- Pre-commit + conformance suite green.
- Live BRD re-verification (regression check): pending.
- Live PRD re-verification (the failure that motivated this change):
  pending.

### Changed — Plugin v0.6.3 → v0.6.4

> **SemVer classification**: PATCH bump — wires team-mode dispatch into the
> PRD layer's audit + fixer SKILLs (PRD-RT-001), grafting the same
> structure BRD got under BRD-RT-001 with PRD-specific lens crew
> (`product_owner / architect / tech_lead / chaos_engineer /
> security_engineer / auditor`). Second of the per-layer Phase 4 PRs.

#### Why

The v0.6.3 PRD increment wired the saga driver to `doc-prd-autopilot`
but the live verification surfaced that `doc-prd-audit` (and
`doc-prd-fixer`) had never received the team-mode fan-out wiring
that BRD's audit/fixer got under BRD-RT-001. The audit ran in legacy
single-pass mode → no `verdict.json`, no lens slots → driver hit the
B7-followon PARTIAL_TIMEOUT escape. This release closes that gap.

#### What changed

- **`doc-prd-audit/SKILL.md`** — added three new top-level sections
  (`## Review Mode` + `## Saga interaction` + `## Break-circuit
  policy`) grafted from `doc-brd-audit/SKILL.md` with PRD-specific
  substitutions:
  - Blackboard path: `.aidoc/review/02_PRD/<PRD-id>/`
  - PRD crew weights: `product_owner: 30, architect: 25, tech_lead:
    20, chaos_engineer: 8, security_engineer: 7, auditor: 10`
  - Lens → agent map: `product_owner → requirements-analyst`,
    `tech_lead → solutions-architect`, others identical to BRD.
  - Rationale text: "chaos / security split 8 / 7 — PRD carries
    both reliability and security NFRs; neither dominates" (per
    CHAOS-SEC-SPLIT-001).
- **`doc-prd-fixer/SKILL.md`** — added `## Remediate Mode` +
  `## Saga interaction` + `## Break-circuit policy` grafted from
  `doc-brd-fixer/SKILL.md` with the same PRD-specific
  substitutions.
- Plugin VERSION 0.6.3 → 0.6.4 (mechanical sync hook propagates).

#### Scope: PRD audit + fixer only

EARS..IPLAN audit + fixer SKILLs still lack team-mode wiring (will
get it via EARS-RT-001, BDD-RT-001, ADR-RT-001, SPEC-RT-001,
TDD-RT-001, IPLAN-RT-001 in subsequent incremental PRs, after each
layer's autopilot has been wired to the saga driver via Phase 4 per
the verify-one-layer-before-propagating rule).

#### Verification

- Pre-commit + conformance suite green.
- Live PRD cascade against the merged BRD-01 — expected to close
  cleanly now (saga driver invoked, audit fans out 6 lens subagents,
  verdict.json + lens slots materialize, fixer dispatched if needed,
  status: CLOSED). Pending.

### Changed — Plugin v0.6.2 → v0.6.3

> **SemVer classification**: PATCH bump — wires the saga driver to the
> PRD autopilot using the same mechanical pattern Amendment 1 brought
> to the BRD autopilot in v0.6.1. No new code paths; the driver
> (`tools/saga_driver.py`) already supported layer `02_PRD` (its
> `_LAYER_CREWS` knew all 8 layers from v0.6.1). First of 7
> incremental PRs propagating the saga driver to PRD..IPLAN per
> SAGA-PARITY-001 Phase 4.

#### Why

PRD's autopilot was the older v0.5.x in-session 5-step pattern — it
generated a PRD without `saga.json`, which the v0.6.1 cascade
dispatcher (B2 harness assertion) FAILs as a missing-journal layer.
Wiring the saga driver to PRD aligns it with BRD's v0.6.1 behavior:
preemptive enforcement, schema-conformant `saga.json`, valid
transitions, no `from: PARTIAL_TIMEOUT`.

#### What changed

- `platforms/claude-code-plugin/skills/doc-prd-autopilot/SKILL.md` —
  same mechanical edit as v0.6.1 for BRD:
  - Added `### Saga-driven generation loop (review_mode: team)`
    section as the first sub-section of `## Workflow`. Three-step
    imperative: invoke the driver, read saga.json, update PRD-00
    index on CLOSED.
  - Layer code: `--layer 02_PRD`.
  - Existing 5-step in-session pattern preserved as
    `### Linear Pipeline (review_mode: single_pass)` for `Task`-
    subagent-unavailable scenarios.
- Plugin VERSION 0.6.2 → 0.6.3.
- 52 SKILL.md frontmatter version bump (auto-applied by
  `scripts/sync-version-refs.sh` per CLAUDE.md §"Update docs of
  record per PR").
- `scripts/sync-version-refs.sh` extended to handle the bare
  `^X.Y.Z$` line in `platforms/claude-code-plugin/README.md`'s
  `$ cat VERSION` example block (was previously a manual edit;
  now mechanical).
- `docs/TAGGING.md` gains the `claude-code-plugin/v0.6.3` release row.

#### Scope: PRD layer only

This release wires the saga driver for the PRD layer only.
`doc-{ears,bdd,adr,spec,tdd,iplan}-autopilot` still use the v0.5.x
in-session pattern. Each will get the same mechanical edit in a
follow-up incremental PR after PRD verification confirms the pattern
works for PRD-shape content + PRD's specific lens crew
(`product_owner: 30, architect: 25, tech_lead: 20, chaos_engineer:
8, security_engineer: 7, auditor: 10`).

#### B7-class follow-on fix (driver MISSING-verdict path)

The 2026-06-07 live PRD cascade surfaced an extension of B7
(Amendment 1's "driver crashes on illegal ESCALATED transition")
that the original fix missed. When the audit subprocess returns
without writing `verdict.json` — which happens when the audit SKILL
is not yet team-mode-wired for the layer — `_advance_after_phase`
tried `append_transition(from=saga.status, to=ESCALATED)`. From
`FANOUT_STARTED` (the state after a non-fan-out audit), ESCALATED
is illegal per spec; the driver crashed with ValueError and saga
stayed at FANOUT_STARTED.

Fix: use PARTIAL_TIMEOUT (universally reachable) for the MISSING-
verdict path, with a compensation_actions entry naming the likely
cause ("audit SKILL may not be team-mode-wired for layer"). Same
class as the v0.6.1 B7 fix; same resolution. All ESCALATED-from-
arbitrary-state sites in the driver are now PARTIAL_TIMEOUT.

#### Known limitation — PRD audit/fixer SKILLs not team-mode-wired

The 2026-06-07 PRD cascade verified the saga driver propagation
works (driver invoked correctly, saga.json materialized, draft
subprocess produced a 18.5KB PRD-01.md). **But the PRD audit ran in
legacy single-pass mode** — it produced a single
`PRD-01.A_audit_report_v001.md` (94/100, well-structured) but did
NOT fan out 5 lens subagents and did NOT write `verdict.json` or
lens slot files. Root cause: `doc-prd-audit/SKILL.md` lacks the
`## Saga interaction` + `## Review Mode` + `## Break-circuit policy`
sections that `doc-brd-audit/SKILL.md` got under BRD-RT-001. Same
for `doc-prd-fixer`.

Phase 4 per-layer work is therefore **3 SKILL edits, not 1**:

1. Autopilot — wire saga driver (this release, ✓ done for PRD).
2. Audit — wire team-mode fan-out (PRD-RT-001 follow-on PR).
3. Fixer — wire team-mode remediation (PRD-RT-001 follow-on PR).

EARS..IPLAN will follow the same 3-edit pattern. The next PR
(PRD-RT-001) does the audit + fixer wiring for PRD and runs the
PRD cascade again to verify end-to-end.

#### Verification

- Pre-commit + conformance suite green.
- Live PRD cascade (2026-06-07): driver invocation + saga.json
  init + draft dispatch + state-machine advance ALL ✓. Audit
  subprocess ran but didn't team-mode-fan-out → PARTIAL_TIMEOUT
  with compensation_actions entry. **The Phase 4 mechanical edit
  is verified working; the team-mode wiring is the next PR.**

### Changed — Plugin v0.6.1 → v0.6.2

> **SemVer classification**: PATCH bump (0.6.1 → 0.6.2) — content
> sub-checks added to existing audit lens prompts. No public-surface
> change (slash-command names unchanged, SKILL frontmatter unchanged,
> generated artifact shape unchanged). Per REVIEW-CALIBRATION-001
> (plan PR #95).

#### Why

A fresh re-read of the merged BRD-01 (the SAGA-PARITY-001 Phase 2
Amendment 1 verification artifact) found 5 substantive issues that
the v0.6.1 5-lens review passed at 94/100:

- Visit-count AC `BRD.01.07.2ee0` — "best-effort / eventually
  consistent" with no tolerance bound → not testable.
- Sync-response AC `BRD.01.07.c1b6` — "Synchronous response on
  submit" doesn't say what comes back → PRD must guess.
- §10 budget cell `BRD.01.10.0b8f` — qualitative; referenced by
  7 §8 cells as if quantitative → vacuous cross-reference.
- "Short codes do not expire this cycle" — buried in FR prose, no
  §10 assumption ID → lost downstream.
- Open-redirect risk `BRD.01.12.40e7` — Med/High severity with
  mitigation "deferred to ADR" + referenced ADR is `Pending` →
  unmitigated abuse vector ships to launch.

The 5-lens crew (`business_analyst`, `architect`, `auditor`,
`chaos_engineer`, `security_engineer`) covers the right perspectives;
three lens prompts simply lacked concrete sub-checks for the failure
mode "non-empty cell / existing AC / named risk = accepted as
adequate." This release adds those sub-checks.

#### What changed

Five content sub-checks added to all 8 layer audit SKILLs
(`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}-audit/SKILL.md`), under
a new top-level section titled `## Content Sub-Checks` inserted
between the existing structural-checks block and the
scoring/output-format section. Same wording for every layer
(section references use concept names like "the constraints
section" / "the launch-gate section" / "the decision-topics
section" / "the functional-requirements section" / "the
assumptions table" — not § numbers — so the same wording works
across all 8 layer templates).

- **A1 — Cell actionability** (auditor lens). Every table cell must
  commit to an ACTIONABLE claim, not just be non-empty. Raises on
  quantitative columns with prose instead of a number; status/content
  column mismatches; cross-references quoting commitments the target
  section doesn't make. P2 default; P1 on launch-gate path.
- **A2 — Assumption-capture discipline** (auditor lens). Every
  assumption-like statement that downstream layers may rely on must
  be captured as a row in the assumptions table with an ID.
  Assumption-shaped prose buried elsewhere is a finding. P2.
- **A3 — Cross-section pointer validity** (auditor lens). For every
  cross-reference (section pointer, artifact ID, `@threshold:` /
  `@diagram:` / `@brd:` etc. tag): target exists AND referenced
  content matches the citing claim's shape. Intentionally overlaps
  A1 on broken cross-references — defense-in-depth. P2 default; P1
  on launch-gate path.
- **BA1 — Acceptance criterion testability** (business_analyst lens).
  Every AC must be testable as written: numeric threshold, binary
  outcome with a single observable definition, fully enumerated
  outcome set, or tolerance bound on a soft semantic. P2 default;
  P1 if the AC is the only criterion for a P1 functional
  requirement.
- **SE1 — Deferred-decision safety** (security_engineer lens). For
  every risk with Likelihood ≥ Medium AND Impact ≥ High: if
  mitigation points to a Pending decision topic AND the launch-gate
  section doesn't name a control category, raise P1 (the artifact
  is committing to ship an unmitigated high-severity risk).

The sub-checks explicitly exclude "downstream-owned by design"
content — phrases like "owned by PRD", "deferred to the next layer",
"specified in EARS" mark legitimate deferrals that must not fire
the checks.

#### Scope

- All 8 layer audit SKILLs uniformly. No layer-specific variants.
- Lens-prompt additions only. No new lens, no new persona, no
  weight changes in `REVIEW_CREWS.yaml`, no spec change.
- Plugin VERSION fanout across the standard 9 places (VERSION,
  plugin.json, marketplace.json, repo + plugin READMEs,
  SKILL_AUTHORING.md, PARITY.md, TAGGING.md, 52 × SKILL.md
  frontmatter).

#### Why this is PATCH not MINOR

- No public surface changes: same slash commands, same SKILL
  frontmatter, same lens-output JSON schema (findings still have
  `id` / `priority` / `location` / `message` / `personas` /
  `recommendation`), same `verdict.json` shape.
- Lens prompts grow internally; behaviour is strictly additive
  (existing structural checks still run; sub-checks add findings).
- An audit run against the merged BRD-01 produces ≥5 findings the
  v0.6.1 audit missed; downstream fixer addresses them via the
  normal iter loop.

#### Out of scope (REVIEW-CALIBRATION-002 backlog)

Speculative items considered for this plan and deferred (no design
work; revisit only if future verification surfaces a need):

- New outward-facing `consumer_simulator` lens.
- `min(lens_scores) ≥ 85` per-lens-minimum PASS gate.
- Iteration-stop-on-stability (replace score-only gate).
- Author-isolation for `business_analyst` drafter-as-reviewer.
- `sdd_doc_lint` cross-section pointer rule.
- Hermes-side application of the same sub-checks.

#### Files changed

- 8 × `platforms/claude-code-plugin/skills/doc-*-audit/SKILL.md` —
  new `## Content Sub-Checks` section.
- `platforms/claude-code-plugin/VERSION` — 0.6.1 → 0.6.2.
- 52 × `platforms/claude-code-plugin/skills/*/SKILL.md` — frontmatter
  `version` 0.6.1 → 0.6.2.
- `platforms/claude-code-plugin/.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, repo + plugin READMEs,
  `docs/SKILL_AUTHORING.md` — version references.
- `docs/PARITY.md` — current-state declaration v0.6.2.
- `docs/TAGGING.md` — new `claude-code-plugin/v0.6.2` row.

### Changed — Plugin v0.6.0 → v0.6.1

> **SemVer classification**: PATCH bump (0.6.0 → 0.6.1) — saga-driven
> loop in the BRD layer's `doc-brd-autopilot` SKILL is fixed without
> changing any public surface (slash-command names, frontmatter
> contract, generated artifact shape). Phase 2's empirical failure
> (2026-06-05 live BRD verification) is the bug being patched.

#### Why

Phase 2 wired up the cooperative-enforcement design from
`framework/governance/REVIEW_SAGA.md` via prompt text embedded in
`doc-brd-autopilot/SKILL.md` (~300 lines of state-machine rules,
transition tables, subprocess dispatch instructions). The 2026-06-05
url-shortener live BRD cascade demonstrated empirically that
**cooperative enforcement is unreliable**: the autopilot synthesized
an invalid `saga.json` (7 illegal transitions, final status
`BRANCH_COMPLETED` not `CLOSED`, no actual subprocess dispatch, layer
runtime 3656s > 3600s cap) instead of executing the
create-review-revise loop subprocess-by-subprocess. The LLM's compliance
with prompt-embedded protocol contracts is non-deterministic at the
state-machine granularity required by REVIEW_SAGA.md.

#### What changed

- **New: `tools/saga_driver.py`** (vendored into the plugin bundle as
  `platforms/claude-code-plugin/tools/saga_driver.py`). ~400 lines of
  stdlib-only Python implementing **preemptive enforcement**: the
  driver script reads/writes `saga.json`, validates every transition
  against an embedded `_ALLOWED_TRANSITIONS` table (mirror of
  REVIEW_SAGA.md), dispatches each phase (`draft`, `review`, `fixer`,
  `re-review`) as a separate `claude -p /aidoc-flow:doc-<layer>[-...]`
  subprocess with `timeout 1800s`, enforces the `SOFT_DEADLINE=1500s`
  break-circuit against its own wall clock, and resumes from
  `PARTIAL_TIMEOUT` per G-R1 (walks `transitions[]` backward to find
  the pre-PARTIAL_TIMEOUT state; never writes `from: PARTIAL_TIMEOUT`).
- **Slimmed `doc-brd-autopilot/SKILL.md`** — the ~180-line
  cooperative-enforcement section becomes a ~30-line thin entry point
  that invokes `${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py` with the
  layer code; all state-machine knowledge moves to the driver. The
  `single_pass` mode and the SKILL's outer responsibilities
  (input-classification, type-and-scope, index-update) are unchanged.
- **`tools/sync-plugin-framework.sh` extended** to vendor `tools/`
  alongside `framework/`, so the driver script ships inside the plugin
  bundle (`${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py`) and is
  callable from an installed plugin session.
- **`tests/scripts/test-acceptance.sh` cascade dispatcher** — the
  per-layer block dispatches only the autopilot (which internally
  drives audit + fixer + re-audit via subprocess). The harness sets
  `PREV_OUTPUT`, `ARTIFACT_ID`, `ARTIFACT_PATH` env vars before
  invocation so the driver reads them deterministically (no
  LLM-cooperative prompt parsing — Pass-4 A5/A6).
- **`tests/conformance/test_saga_driver_invariants.py`** (new, 10
  tests) — asserts the driver's state-machine table contains all 11
  spec states, PARTIAL_TIMEOUT/CLOSED/ESCALATED are terminal, invalid
  transitions raise, resume logic walks backward correctly, and
  `_LAYER_CREWS` matches `REVIEW_CREWS.yaml` (Pass-4 A7 drift defence).

#### Why this is PATCH not MINOR

- No public surface changes: same slash commands, same SKILL
  frontmatter, same `saga.json` schema, same generated BRD shape.
- Existing user prompts and workflows continue to work unchanged.
- The substitution is purely internal: cooperative LLM-driven loop
  becomes deterministic Python-driven loop, with the same observable
  contract (CLOSED on PASS, ESCALATED on terminal FAIL,
  PARTIAL_TIMEOUT on soft-deadline crossing).
- Pre-Phase-2 blackboard migration path retained: if a directory has
  slot files but no `saga.json`, the driver scaffolds one from the
  slot mtimes.

#### Scope: BRD layer only

This release wires the saga driver for the **BRD layer only**. The
remaining 7 layers (PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN) still use
the (now-failing) cooperative-enforcement prompt pattern from Phase 2
and will be migrated in a follow-up plan once BRD-layer verification
demonstrates the preemptive pattern works end-to-end. Per
SAGA-PARITY-001 Phase 4. Until then, those layers' autopilot skills
remain at v0.6.1 but functionally unchanged from v0.6.0.

#### In-flight bug fixes (2026-06-05 live verification)

The first live verification of v0.6.1 surfaced three bugs in the
initial impl that were fixed on the same branch before this release
opens (per the submit-only-finalized-work principle):

- **B1 — autopilot bypassed the driver.** The initial slim SKILL
  text still had room for the LLM to dispatch Task subagents
  cooperatively and produce the BRD in-session, without invoking
  the saga driver. saga.json was never written. Fix: rewrote the
  `team`-mode section with imperative one-shot direction —
  "your FIRST tool call MUST be Bash python3
  ${CLAUDE_PLUGIN_ROOT}/tools/saga_driver.py ..." — and removed
  the verbose "Driver contracts" reference block that gave the
  LLM enough emulation context to skip the dispatch.
- **B2 — harness silently no-op'd on missing saga.json.** The
  cascade dispatcher's saga-journal inspection used
  `if [[ -f "$saga_file" ]]; then ... fi` and didn't fail when the
  file was absent. The autopilot subprocess returned exit 0 (it
  did produce a BRD in-session), so the harness reported PASS
  despite the driver never running. Fix: hard-fail when
  saga.json is missing or status is ESCALATED / PARTIAL_TIMEOUT /
  any other non-CLOSED terminal.
- **B3 — autopilot stdout was clobbered.** `invoke_skill` already
  calls `write_element_log` internally on PASS, which merges the
  staging stdout into the .log file and deletes the staging copy.
  The cascade dispatcher then called `write_element_log` a second
  time, which read an already-deleted file and re-wrote the .log
  with an empty body. Fix: removed the redundant cascade-side
  call.

**B5 — driver SOFT_DEADLINE too tight for fixer cycles.** Initial
budget of 1500s (25 min) covered draft+audit happy path but always
fired break-circuit during the fixer + re-audit cycle. Bumped to
3300s (55 min); harness `ORCHESTRATOR_TIMEOUT` aligned 1800s -> 3600s.

**B6 — driver overwrote subprocess writes to saga.json.** The driver
loaded saga.json once at startup, kept it in memory, and
`write_saga()` after each phase. The audit subprocess writes its own
per-branch transitions and advances run-scope status directly to
saga.json on disk; the driver's stale in-memory copy then overwrote
those writes (transitions list dropped from 13 to 2 in the live
run). Fix: re-load saga.json from disk after `dispatch_phase`
returns and before `_advance_after_phase` modifies it.

**B6 follow-on — PASS path non-idempotent.** Because the audit
synthesizer typically advances saga.status to FANIN_REDUCED before
the driver picks back up, the driver's old PASS path
(`append_transition(from=saga.status, to=FANIN_REDUCED)`) would emit
a no-op transition that fails `_ALLOWED_TRANSITIONS`. Walk the
terminal chain FANIN_REDUCED -> SYNTHESIZED -> CLOSED skipping
states the saga is already at.

**B7 — driver crashed on subprocess failure.** Per spec
`_ALLOWED_TRANSITIONS`, `ESCALATED` is reachable only from
`BRANCH_FAILED` or `BRANCH_COMPENSATING`. The driver's failure-
handling code (subprocess exit != 0, max iterations exhausted) tried
to `append_transition(from=saga.status, to=ESCALATED)` regardless of
current state, which raised `ValueError` for the common cases
(saga.status at `PREPARED` / `FANOUT_STARTED` / `BRANCH_COMPLETED` /
`FANIN_REDUCED`). When a claude API session limit hit during the
draft subprocess (live verification, 2026-06-05), the driver
crashed with the ValueError and saga.json never recorded the
failure. Fix: use `PARTIAL_TIMEOUT` (universally reachable from
non-terminal states) for both subprocess-failure and max-iter-
exhausted paths. `PARTIAL_TIMEOUT` connotes "non-CLOSED terminal,
resumable on next invocation" — the right semantics for both
cases. Harness treats `PARTIAL_TIMEOUT` and `ESCALATED` identically
(both → layer FAIL). The driver's `while` loop also now exits on
`PARTIAL_TIMEOUT` (previously only `CLOSED` / `ESCALATED`).

These six fixes are part of the same v0.6.1 release; no separate
amendment PR.

#### Verification result (2026-06-06 fourth live cascade)

Final live BRD cascade against `examples/url-shortener` (commit
`3cf15ca4` with all B1-B7 fixes) reached **`saga.status: CLOSED`**
in **2559s (42.6 min)** with score 94/100 PASS, quorum met, iter=2
(one fixer cycle), all 5 lens slots populated, BRD-01.md lint
clean, no `from: PARTIAL_TIMEOUT` transitions (G-R1 invariant
holds). 10/10 load-bearing pass criteria met.

#### Known limitation — fixer-cycle transitions are spec-non-conforming

The audit/fixer SKILLs (cooperative-enforcement code path inherited
from v0.6.0) emit run/branch-scope transitions during the fixer
cycle that aren't in the spec's `_ALLOWED_TRANSITIONS` table:

- `BRANCH_COMPLETED -> BRANCH_COMPENSATING` (fixer entry per branch)
- `BRANCH_COMPENSATING -> BRANCH_COMPLETED` (fixer validation per
  branch + once at run-scope)
- `BRANCH_COMPLETED -> FANOUT_STARTED` (re-audit re-entry at
  run-scope)

These are semantically correct (a fixer-then-revisit IS the right
shape for the loop) but the framework spec's transition table
doesn't model them. The driver itself only writes spec-compliant
transitions (run-scope entries around the cycle). The cooperative
SKILL writes are the source of the non-conformance.

Phase 4 will either:

1. **Amend the framework spec** to add fixer-revisit transitions
   (`BRANCH_COMPLETED -> BRANCH_COMPENSATING`, etc.), OR
2. **Slim the audit/fixer SKILLs** so they don't write run/branch-
   scope transitions to saga.json at all — the driver owns ALL
   journal writes.

Option 2 aligns with the SKILL prompt drift carry-forward (below)
and is the cleaner architectural fix. Marked for the Phase 4 plan.

#### Known limitation — doc-brd SKILL prompt drift (Phase 4 follow-up)

The doc-brd SKILL's prompt body still contains the v0.6.0
cooperative-enforcement saga-interaction text (instructions telling the
LLM to write to `saga.json` itself). The 2026-06-05 draft-only smoke
test demonstrated the SKILL correctly **inferred** the new architecture
from the driver-supplied brief and deliberately did NOT write to
`saga.json` — preserving the driver's authoritative-writer position.
This is the right architectural behaviour, but it relies on LLM
inference rather than explicit prompt direction; the same class of
non-determinism that motivated the cooperative → preemptive pivot
applies. Phase 4 will slim doc-brd (and the PRD..IPLAN base SKILLs)
to remove the cooperative-enforcement saga prose entirely, so the
deferral becomes deterministic.

#### Hermes parity

Hermes already implements the same preemptive saga model
(`saga_orchestrator.py`). This release brings the plugin to functional
parity for the BRD layer; Hermes's behaviour is unchanged.
SAGA-PARITY-001 Phase 3 will tighten the Hermes side's
`PARTIAL_TIMEOUT` invariants (G-R1) so both implementations enforce
the same `from: PARTIAL_TIMEOUT` ban.

#### Files changed

- `platforms/claude-code-plugin/VERSION`: `0.6.0` → `0.6.1`.
- 52 × `platforms/claude-code-plugin/skills/<name>/SKILL.md`:
  `version: "0.6.0"` → `"0.6.1"`.
- `platforms/claude-code-plugin/.claude-plugin/plugin.json`: version
  bump.
- `platforms/claude-code-plugin/README.md`,
  `platforms/claude-code-plugin/docs/SKILL_AUTHORING.md`: version
  references updated; deprecated-stub removal milestone pushed
  v0.6.0 → v0.7.0 (those stubs survived the 0.6.0 release
  unchanged).
- `platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md`:
  slimmed cooperative-enforcement section to a thin driver-invocation
  entry point.
- `platforms/claude-code-plugin/skills/doc-review/SKILL.md`,
  `platforms/claude-code-plugin/skills/trace-check/SKILL.md`:
  deprecation removal milestone updated.
- `tools/saga_driver.py`: NEW (source of truth for the bundled
  copy).
- `tools/sync-plugin-framework.sh`: extended to vendor `tools/`.
- `platforms/claude-code-plugin/tools/saga_driver.py`: NEW (vendored,
  byte-identical to source).
- `tests/scripts/test-acceptance.sh`: cascade dispatcher refactored to
  autopilot-only per layer; env-var injection added.
- `tests/conformance/test_saga_driver_invariants.py`: NEW.

### Changed — Plugin v0.5.0 → v0.6.0

> **SemVer classification rationale**: this release is labelled as a
> MINOR bump (0.5.0 → 0.6.0) rather than BREAKING. The primary surface
> change — adding `saga.json` to `.aidoc/review/<NN>_<LAYER>/<id>/` —
> is purely **additive**: no existing files (blackboard slots,
> verdict.json, report.md) change shape, and no existing CLI / skill
> invocation breaks. Consumers that strictly enumerate the contents of
> `.aidoc/review/` may see a new file, but the shape of every other
> file is preserved. Under pre-1.0 SemVer the project uses MINOR for
> additive changes.

- **BRD-layer saga implementation (SAGA-PARITY-001 Phase 2, D-0031).**
  The plugin's BRD-layer orchestrator skills (`doc-brd-autopilot`,
  `doc-brd-audit`, `doc-brd-fixer`, plus the supporting `doc-brd` +
  shared `review-team`) now maintain a saga journal at
  `.aidoc/review/01_BRD/<BRD-id>/saga.json` per the framework
  saga lifecycle contract (`framework/governance/REVIEW_SAGA.md`).
  - **Autopilot refactor**: the create→review→revise loop now
    dispatches each phase (draft, review, fixer, re-review) via
    `Bash → claude -p` subprocesses. Each phase gets its own fresh
    `ORCHESTRATOR_TIMEOUT=1800s` budget. The autopilot's outer loop
    reads/writes saga.json between phases, validates transitions
    against the spec table, and exits cleanly with status
    `PARTIAL_TIMEOUT` if its `SOFT_DEADLINE=1500s` is crossed.
  - **Resumable runs**: an autopilot invocation that returns with
    `status: PARTIAL_TIMEOUT` can be re-invoked; the resumed
    session reads saga.json, identifies `current_phase`, and
    continues from the recorded checkpoint. The CHAOS-SEC-SPLIT-001
    verification scenario (5-lens BRD with multi-lens fixer hitting
    1802s in a single autopilot invocation) becomes recoverable
    instead of fatal.
  - **Break-circuit policy** with per-skill checkpoint boundaries:
    autopilot fires between phases; audit before synthesizer; fixer
    between multi-lens validations; each skill tracks its own
    elapsed time via per-skill `.skill-start.<skill>` epoch files.
  - **Pre-Phase-2 blackboard migration**: if `.aidoc/review/01_BRD/
    <BRD-id>/` has slot files but no saga.json (a pre-Phase-2 run),
    the autopilot scaffolds a saga.json reflecting the existing
    state instead of treating it as fresh.
  - **Standalone audit/fixer behavior**: when invoked directly
    outside the autopilot loop without a pre-existing saga.json,
    the audit/fixer skip saga.json writes entirely (backward
    compatible with direct skill invocation).
  - **`doc-brd` gains a `## Draft mode (saga-driven)` section**:
    when invoked via the autopilot subprocess pattern with `Draft`
    in the brief, `doc-brd` dispatches `requirements-analyst` as a
    Task subagent with the `business_analyst` lens (preserves the
    persona binding lost in the move from in-session Task dispatch
    to subprocess invocation).
  - **`review-team` SKILL gains a `## The saga journal` section**
    describing the saga.json layout alongside the existing
    blackboard description.
  - PRD..IPLAN propagation arrives in SAGA-PARITY-001 Phase 4.
  - Hermes-side alignment (PARTIAL_TIMEOUT, `transitions[]` field)
    arrives in Phase 3.
  - **Net file changes**: 4 BRD SKILLs + doc-brd + review-team + 52
    skills' frontmatter `version` bump + plugin VERSION + 9-place
    fanout. No framework spec changes (Phase 1's 0.13.0 holds).

### Changed — Framework Spec 0.12.0 → 0.13.0 (CHG-gated, declaration only)

- **`FRAMEWORK_SPEC_VERSION` bumped `0.12.0 → 0.13.0`
  (SAGA-PARITY-001 Phase 1, D-0031).** Plugin declares intent to
  conform to the new review-saga lifecycle contract introduced by the
  framework spec; full implementation (saga.json + Bash subprocess
  refactor + break-circuit policy in BRD-layer SKILLs) arrives in
  Phase 2 of SAGA-PARITY-001 with plugin v0.6.0. No plugin behavior
  change in this version.

### Changed (BREAKING)

- **Adversary lens partitioned into `chaos_engineer` + `security_engineer`
  (CHAOS-SEC-SPLIT-001, D-0030).** The single `adversary` review lens —
  which conflated *internal stability* concerns (failure modes, edge
  cases, race conditions, resource exhaustion) with *external threat*
  concerns (trust boundaries, abuse cases, controls) — is partitioned
  into two narrowly-scoped lenses aligned with intent. `agents/adversary.md`
  is renamed to `agents/chaos-engineer.md` (color `orange` →
  `cyan`); the existing `agents/security-engineer.md` is promoted from
  a transitive `auditor` sub-role to a first-class crew lens (color
  unchanged `red`). The framework spec bumps `0.11.3 → 0.12.0`
  (CHG-gated).

  **Per-layer weight redistribution** (all sums still = 100;
  authoritative in `REVIEW_CREWS.yaml`):
  - **BRD**: chaos 12 / security 8 — chaos-heavy (reliability NFRs >
    threat-modeling at business-requirements level).
  - **PRD**: chaos 8 / security 7 — equal split (both NFRs matter).
  - **EARS**: chaos 12 / security 8 — chaos-heavy (failure-mode ACs >
    abuse-case ACs).
  - **BDD**: chaos 14 / security 6 — chaos-heavy (failure scenarios
    dominate Gherkin).
  - **ADR**: chaos 8 / security 12 — **security-heavy** (trust
    boundaries, authn/authz, crypto choices).
  - **SPEC**: chaos 10 / security 10 — equal split (perf + controls).
  - **TDD**: chaos 10 / security 10 — equal split (`security_engineer`
    co-owns SECTEST).
  - **IPLAN**: chaos 8 / (no security) — **chaos-only** (security
    lives upstream in ADR/SPEC; chaos covers rollback/recovery).

  **Breaking surface** (consumers parsing the blackboard or
  `verdict.json` must migrate):
  - Slot filenames change: `adversary.json` → `chaos_engineer.json` and
    `security_engineer.json` (new).
  - `verdict.json:lens_scores` keys change: `"adversary"` →
    `"chaos_engineer"` + `"security_engineer"`.
  - `personas` arrays in `findings[].personas` may now contain both
    new lens names (overlap zone for rate-limits, TOCTOU, resource-DoS
    — synthesizer dedupes by `(location, id)`).
  - Personas registry in `REVIEW_CREWS.yaml`: `adversary` removed;
    `chaos_engineer` + `security_engineer` added.

  **Migration**: regenerate `.aidoc/review/` on first run — `rm -rf
  .aidoc/review/` is the one-step migration. No backward-compat shim is
  planned (per project policy "no backwards-compatibility hacks").

  Plugin v0.4.5 → v0.5.0 (SemVer-major because slot filenames are part
  of the public contract). FRAMEWORK_SPEC_VERSION `0.11.3 → 0.12.0`.
  Deprecation timeline for `doc-review` and `trace-check` redirect
  stubs pushed from v0.5.0 → v0.6.0 (those stubs are tangential to
  this lens partition).

### Changed

- **Generalised orchestrator timeout policy (BRD-RT-004, D-0028).**
  Collapses the previously-separate `AUDIT_TIMEOUT` (BRD-RT-002),
  `AUTOPILOT_TIMEOUT` (BRD-RT-003), and `REVIEW_TEAM_TIMEOUT` into a
  single **`ORCHESTRATOR_TIMEOUT=1800s`** applied to every skill that
  internally dispatches a sub-team in team mode. Name-match in
  `tests/scripts/test-acceptance.sh:_pick_timeout_for` covers
  `review-team`, `*-audit`, `*-autopilot`, and now also **`*-fixer`** —
  closing **G15**: live re-verification on 2026-06-04 (after
  BRD-RT-003) showed `doc-brd-fixer` hit the default 600s
  `SKILL_TIMEOUT` (exit 124) mid-dispatch of its multi-lens validators
  for the BA-001 finding (`[architect, business_analyst]`).
  Generalising the budget closes the gap and prevents the same shape
  from recurring at PRD..IPLAN's fixers. Leaf skills (no sub-team
  dispatch) keep the 600s `SKILL_TIMEOUT`; Phase 4.1 agents keep the
  600s `AGENT_TIMEOUT`. Plan banner display tightened to show one
  orchestrator budget instead of three separate values. Plugin v0.4.4
  → v0.5.0. Framework spec unchanged (0.11.3). No GATE-SPEC. The
  consolidation also makes per-layer follow-ups (PRD-RT-001 etc.)
  inherit the corrected ops uniformly via the same name-match.

- **Operational fixes from BRD-RT-002 live verification (BRD-RT-003, D-0027).**
  Closes three operational gaps surfaced by the 2026-06-04 BRD-RT-002 live
  verification (Run #1 team mode hit 4/6 pass criteria; the 2 FAILs were
  operational, not architectural). Fixes:
  - **G11 — Autopilot timeout extended.** `doc-*-autopilot` in team mode
    runs the entire `create→review→revise` loop (drafter, audit, fixer,
    re-audit) inside one outer claude process. Run #1's
    `doc-brd-autopilot` hit the default 600s SKILL_TIMEOUT (exit 124).
    `tests/scripts/test-acceptance.sh` introduces `AUTOPILOT_TIMEOUT=1800`
    applied via name-match (`*-autopilot`) in `_pick_timeout_for`. Plan
    summary banner updated.
  - **G12 — Per-layer cap raised 1800s → 3600s.** Even with the autopilot
    timeout fixed, a multi-iteration fix cycle (3 iterations × ~25 min)
    pushes layer wall-clock past 60 minutes. Lineage: 900s (BRD-RT-001) →
    1800s (BRD-RT-002) → 3600s (BRD-RT-003). Existing inner backstops
    (per-skill timeouts, `--cost-cap`, the framework's
    `MAX_TOTAL_OUTPUT_TOKENS`) remain.
  - **G13 — Fixer multi-lens dispatch made explicit.** Run #1's fixer ran
    487s and produced no `<persona>.fix_<N>.json` slots because the
    BRD-RT-001 SKILL text said "dispatch *the* responsible lens" — but
    the single P1 finding spanned `architect + business_analyst`. The
    model bailed on lens validation. `doc-brd-fixer/SKILL.md` Remediate
    Mode §2 now codifies dispatch-decision rules: single-lens → dispatch
    that one; multi-lens → dispatch **all** in parallel; orphan finding
    → dispatch the layer's author lens as default. §4 updates the slot
    naming and persistence guarantees per dispatched lens.
  - **Synthesizer schema clarification.** `agents/synthesizer.md`
    documents the `findings[].personas` field (consumed by `doc-*-fixer`
    for multi-lens dispatch) — Run #1's data already had this; the
    SKILL spec catches up.

  Plugin v0.4.3 → v0.4.4. Framework spec unchanged (0.11.3). No
  GATE-SPEC. See `plans/REVIEW-TEAM-FOLLOWUPS.md` TODO-RT0 for the gap
  history. Live re-verification (~$7, ~25-30 min) should reach 6/6 pass
  criteria on the BRD layer; the same name-match + cap apply to PRD..IPLAN
  once propagated.

- **Verdict-chain consistency wired through written reports (BRD-RT-002, D-0026).**
  Closes five gaps surfaced by the BRD-RT-001 live verification runs.
  The synthesizer agent (`agents/synthesizer.md`) now writes a
  deterministic **`verdict.json`** companion next to `report.md` —
  flat schema with `combined_status`, `content_score`,
  `structural_status`, `coverage.*`, `blocking_findings_count`, and
  `lens_scores`. Every downstream consumer (audit-skill stdout,
  driver script's `parse_audit_score`, autopilot's revise loop,
  fixer's blocking-findings list) reads from `verdict.json` instead
  of scraping Markdown prose or echoing the BRD's self-claimed
  PRD-Ready score. `doc-brd-audit/SKILL.md` adds an explicit Output
  Contract subsection mirroring the JSON values; `doc-brd-autopilot/SKILL.md`
  Workflow §5 reads `verdict.combined_status` for the gate decision;
  `doc-brd-fixer/SKILL.md` prefers `verdict.json` for blocking-finding
  counts and slot paths. `tests/scripts/test-acceptance.sh` raises
  `MAX_LAYER_SEC` 900 → 1800 (team-mode legitimately runs 17-25
  min/layer); introduces `AUDIT_TIMEOUT=1200` applied via name-match
  to any `doc-*-audit` skill (uniform across all 8 layers); and
  `parse_audit_score` now prefers `verdict.json:content_score` over
  the audit skill's stdout, logging a warning on drift.
  `<BRD-id>` codified as the short artifact ID (`BRD-01`), not the
  nested folder name. Always-on `single_pass` advisory note included
  in the audit report whenever single_pass is the resolved mode
  (the skill cannot reliably know its trigger context). Plugin v0.4.2
  → v0.4.3. See `plans/BRD-RT-002-VERDICT-CHAIN-PLAN.md` for the full
  design (10 gaps, 3 review passes).

- **Project profile is an override-only delta (PROFILE-DELTA-001, D-0025).**
  The acceptance suite's profile bootstrap source moved from
  `framework/governance/REVIEW_CREWS.yaml` to a new dedicated
  `framework/governance/PROFILE-TEMPLATE.yaml` skeleton. A bootstrapped
  `.aidoc/profile.yaml` now carries no hardcoded overrides — every
  adaptation knob is commented out, falling through to framework
  defaults via the `framework defaults < user-global seed < project
  profile` precedence chain documented in
  `framework/governance/ADAPTATION.md`. Persona-list extraction in the
  acceptance suite (`tests/scripts/test-acceptance.sh:1244-1280`) gains
  a fallback chain that reads from
  `framework/governance/REVIEW_CREWS.yaml` when the project profile
  declares no crews/personas. The four BRD-layer skills'
  mode-resolution prompts explicitly cite the fallback to the framework
  default. Result: the framework can safely evolve crew/persona
  defaults without breaking existing projects, and profile readers see
  only what the project chose to override. Plugin v0.4.1 → v0.4.2;
  framework spec **0.11.2 → 0.11.3** (additive — new template file). New
  conformance test `tests/conformance/platforms/test_profile_schema.py`
  validates that committed project profiles use only top-level keys
  defined in the closed `ADAPTATION_SURFACE.yaml` (out-of-surface keys
  would be silently ignored by a conforming engine, so flagging them
  is an authoring-mistake guard). See
  `plans/PROFILE-DELTA-OVERRIDE-PLAN.md` for the full design.

- **BRD-layer review-team subagent fan-out wired (BRD-RT-001).** The four
  BRD-layer skills (`doc-brd`, `doc-brd-audit`, `doc-brd-fixer`,
  `doc-brd-autopilot`) and the `requirements-analyst` agent now follow
  the framework spec's multi-persona review-team model
  (`framework/governance/REVIEW_TEAM.md`, `REVIEW_CREWS.yaml`). The audit
  and autopilot get a `## Review Mode` branch: in **team mode** (default
  at gates per `REVIEW_CREWS.yaml` `default_mode: independent`) they
  dispatch the BRD crew
  (`{architect: 30, business_analyst: 30, auditor: 20, adversary: 20}`)
  as parallel `Task` subagents over the per-artifact blackboard at
  `.aidoc/review/01_BRD/<BRD-id>/`, then run the `synthesizer` for the
  deterministic reduce + narrative; **single_pass mode** stays as the
  unchanged legacy fallback. The autopilot's audit↔fix cycle becomes the
  framework spec's create→review→revise loop. The audit-report output
  path moves from `docs/01_BRD/.../BRD-NN.A_audit_report_vNNN.md` to
  `.aidoc/audit/01_BRD-audit.md` per `framework/docs/AIDOC.md`. The
  `requirements-analyst` agent gains an explicit `## Review-Team Lens
  Role` section declaring its `business_analyst`/`requirements_specialist`/
  `product_owner` lens bindings per the lens→agent table in
  `review-team/SKILL.md`. Five legacy bugs in `requirements-analyst.md`
  fixed: layer chain extended to include TDD/IPLAN, coverage threshold
  table gains `TDD → IPLAN` + `IPLAN → Code` rows, `@adr` dash-vs-dot
  notation clarified, FR/QA/IR classification labels distinguished from
  the removed `FR-XXX` element-ID prefix pattern. Framework spec
  unchanged; this is a plugin-only behaviour change. See
  `plans/BRD-REVIEW-TEAM-PLAN.md` for the full design + verification
  ladder. Cost characteristic: team mode is ~3.3× single-pass per audit
  (intentional architectural cost for true lens independence); the
  follow-up `REVIEW-TEAM-RUNNER-CACHING-001` (v0.4.2) brings that to
  ~1.3× via prompt caching.

- **Demo corpus cleared.** `examples/url-shortener/docs/` (8 layer artifacts:
  BRD-01 through IPLAN-01) removed. The corpus predated the `STRUCT01` lint
  and the v0.4.0 skill consolidation and was emitting 43 structural findings.
  The `seed/initial-requirements.md` is retained as the regeneration input.
  The new demo chain will be authored from a Claude Code session by driving
  the seed through `doc-{layer}-autopilot` skills against current templates
  and committed under `docs/` once it passes `sdd_doc_lint` + each layer's
  `-audit` gate. The test-suite live tier exercises the same path for
  regression validation but produces test-instrumented output unsuitable as
  production demo content.
- Updated `examples/url-shortener/README.md`, the seed file, and the plugin
  `README.md` Quickstart to point at the seed-based regeneration walkthrough
  (was: "complete, gate-clean example chain").
- **`doc-flow` — bundled-path resolution guidance.** Added a "Reading bundled
  files" note clarifying that `${CLAUDE_PLUGIN_ROOT}` is an environment variable
  (it does not auto-expand in skill prose) and how to resolve a
  `${CLAUDE_PLUGIN_ROOT}/framework/…` reference — read it via the shell (where the
  variable expands) or relative to the plugin root. Proactively de-risks the P2
  live-run / install smoke test (plan risk R2).
- Manifest metadata polished for pre-1.0 preview (PR #44). Plugin description and marketplace description prefixed "Pre-1.0 preview." with explicit "APIs and surfaces may change before 1.0" note.
- Plugin manifest `homepage` repointed from placeholder `https://aidoc-flow.com/claude-code` to the working install-section anchor at `https://github.com/vladm3105/aidoc-flow-framework#install-the-claude-code-plugin`.
- Plugin manifest `author` cleaned up: dropped non-resolving `aidoc-flow.com` email + url; left `name` and added GitHub repo URL.
- Framework spec dependency bumped to `0.11.0` (was `0.10.0`).

### Documentation

- IPLAN ↔ iplanic integration explicitly deferred — see framework `plans/IPLAN-IPLANIC-DEFERRED.md`.
- Plugin README opens with a substantive description block under the H1
  (8-layer flow visualization + "What you get" + "Use it when") — framework
  PR #46.

## [0.4.0] — 2026-05-27

### Changed

- **Skill set consolidated 55 → 50 active (+ 2 deprecated stubs = 52 total, redundancy audit).** Folded five
  overlapping utilities into two homes, carrying their procedural detail:
  - `skill-recommender` + `workflow-optimizer` + `context-analyzer` → **`doc-flow`**,
    which now carries the intent-keyword → skill map, the `where am I` position
    scan (status taxonomy + progress %), `what's next` P0/P1/P2 prioritization over
    the critical path with parallel-work detection, and the context scan
    (upstream-candidate ranking + vocabulary). It is **adaptation-aware**
    (`adapts: [active_layers]`): the critical path, progress denominator, and
    next-step recommendations honor a project's disabled skippable layers.
    `skill-recommender` also duplicated Claude Code's native skill dispatch.
  - `trace-check` + `doc-review` → **`doc-validator`**, which now covers full
    bidirectional traceability with `auto_fix` repair (backup / rollback /
    no-placeholder safety) and the four-class prose review (DATA/REF/TYPO/TERM,
    severity by `strictness`). It is **adaptation-aware**
    (`adapts: [active_layers, glossary]`): traceability honors a project's
    disabled-layer profile instead of false-failing it, and the prose pass uses
    the project `glossary` to suppress domain-term false positives.
  Utilities 19 → 14. All cross-references across skills, agents, README, and
  `docs/SKILL_AUTHORING.md` were repointed; `plm_lint`'s enforced set updated.
  `doc-naming` stays the ID-format authority; the per-layer 4-variant skills are
  unchanged.

## [0.3.0] — 2026-05-27

### Added

- **Self-contained framework bundle (PLUGIN-MARKETPLACE P1)** — the plugin now
  ships a **vendored, byte-identical copy** of the framework spec it consumes
  (`framework/{layers,governance,registry}` + the SDD guide) at the plugin root,
  generated by `../../tools/sync-plugin-framework.sh`. Every reference across
  skills/agents/commands/docs (380 across 66 files) was repointed from the
  monorepo-relative `framework/…` (which resolved nowhere once Claude Code copies
  only the plugin dir to its cache) to `${CLAUDE_PLUGIN_ROOT}/framework/…`, the
  install-time anchor. The plugin is now **installable self-contained**; the
  monorepo `../../framework/` stays the single source of truth (decision
  **D-0022**), with a conformance **drift-guard** asserting byte-identity.
- **Deterministic validation gate** — `../../tests/conformance/platforms/`
  `test_plugin_manifest.py` (manifest required/recommended fields, every skill
  has a description, every agent has name+description, `hooks.json` shape, and
  **bundled-reference resolution**: every `${CLAUDE_PLUGIN_ROOT}/framework/…` ref
  resolves to a real bundled file/dir — the check that catches a broken ref) and
  `test_plugin_framework_bundle.py` (the drift-guard). Conformance 57 → 65.
- **`plugin.json` metadata** — added `$schema`
  (`json.schemastore.org/claude-code-plugin-manifest.json`); set `author` to the
  `aidoc-flow.com` identity and `homepage` to `https://aidoc-flow.com/claude-code`
  (**D-0023** — one brand, path-based per-integration pages). Publish-time URL +
  mailbox verification is the P2 gate.

  > Note: in `v0.4.0` the homepage was repointed to <https://github.com/vladm3105/aidoc-flow-framework#install-the-claude-code-plugin> until the aidoc-flow.com identity is live.
- **Review-team mode (AGENT-TEAM Phase 2)** — a shared `review-team` skill plus
  two review-lens agents (`adversary`, `synthesizer`): the plugin's binding of the
  engine-agnostic `framework/governance/REVIEW_TEAM.md` model. The crew fans out as
  `Task` subagents that deposit findings to a **git-ignored `.aidoc/review/`
  blackboard**; the `synthesizer` reduces the slots (dedup by `location`+`id`, max
  severity, weighted/capped score from `REVIEW_CREWS.yaml`, coverage/quorum) into one
  report. Per `../../plans/DECISIONS.md` **D-0005** the plugin uses the blackboard +
  coverage (durable per-persona slots), **not** a saga. The gate stays the
  deterministic structural floor + "no unresolved P0/P1"; the score is advisory.
  **Behavior:** the `doc-*-audit`/`-fixer`/`-autopilot` skills gain a *team* mode
  (dispatched by `pm-orchestrator` via `review-team`) at gates
  (`pre_promotion`/`pre_merge`); `single_pass` — today's single-pass audit — stays
  the advisory `on_author` default and the no-subagent fallback, selected by the
  `review_mode` knob.
- **CHG change-management skills + onboarding/gate utilities (task P3-T7)** —
  six new skills, bringing the set to **52**:
  - `doc-chg` family (base + `-autopilot` + `-audit` + `-fixer`) — author and
    validate change records against the framework CHG overlay
    (`framework/governance/chg/`): change-level classification (C1–C3/Emergency),
    source→gate routing, and cross-layer cascade impact. CHG uses gate approval,
    not a ≥90 readiness score.
  - `gate-check` — run the CHG approval gate (GATE-01/03/06/08/CODE) for a
    change's affected layers and prepare `GATE_APPROVAL_FORM`; the skill prepares
    and verifies, a human approves.
  - `project-adopt` — adopt SDD into an existing (brownfield) codebase, the
    counterpart to the greenfield `project-init`.
  Wired into `doc-flow`, `skill-recommender`, the plugin README inventory, and
  the conformance lint's enforced scope.

### Changed

- **README rewritten to lead with install + quickstart** and document the
  self-contained framework bundle; component counts refreshed to the as-built
  totals (55 skills, 11 agents). Spec-change checklist (`../../docs/PROJECT.md`
  §6) now records the bundle re-sync obligation; `tests/chg/spec_gate.py` prints
  a re-sync reminder on a framework change.
- **Skill set revised to the canonical 46** and recreated to a single standard
  (`docs/SKILL_AUTHORING.md`), task `../../plans/P3-T6-PLAN.md`. The set is now
  the 8 layer families (`doc-{brd,prd,ears,bdd,adr,spec,tdd,iplan}`) each in 4
  variants — base, `-autopilot`, `-audit`, `-fixer` — plus 14 utilities. Every
  retained `SKILL.md` was regenerated lean and consistent: `version` now
  defaults to the plugin version (`0.2.0`) with `framework_spec_version`
  recorded; `## Version History` footers dropped (history lives here + in git);
  `mermaid-gen` references repointed to `charts-flow`; cross-references limited
  to the canonical set. `agents/README.md`, `doc-validator`, and `doc-review`
  repointed their `-reviewer`/`-validator` references to the unified `-audit`.

### Removed

- Stale skill families not in the 8-layer contract (`framework/registry/LAYER_REGISTRY.yaml`),
  reversing the D-0015 retention: SPEC-subtype (`doc-cspec/dspec/uxspec/riskspec/procspec`,
  25) — subsumed by SPEC (L6); test-type (`doc-utest/itest/ftest/ptest/stest/sectest`,
  36) — folded into TDD (L7); deprecated `-reviewer`/`-validator` variants (14) —
  merged into `-audit`; legacy utilities `contract-tester`, `test-automation`,
  `mermaid-gen` (3); 16 loose `*.md` helper files at the `skills/` root; and the
  orphaned `doc-flow/SHARED_CONTENT.md` (a plugin-local standards copy superseded
  by `framework/`, per D-0013). Plugin skill count 124 → 46.

## [0.2.0] — 2026-05-23

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
- `project-mngt` skill parked to `legacy/claude-code-plugin/` (marked
  legacy, pending review): a generic MVP/MMP/MMR planning methodology,
  not SDD-layer-specific, so it no longer ships with the plugin. All
  inbound references (`README` counts, `skill-recommender` routing,
  `adr-roadmap`/`doc-flow`/`trace-check`/`mermaid-gen`/`workflow-optimizer`
  cross-links, `pm-orchestrator` + agents roster) neutralized. Plugin
  skill count 125 → 124. See `../../plans/DECISIONS.md` D-0017. README
  skill counts also corrected to the as-built totals (the migration's
  142 → 125 reduction had not been reflected there).

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
