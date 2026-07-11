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

_Nothing yet._

## [0.11.1] — 2026-07-11

### Fixed

- **Pre-prod readiness cleanup (audit 2026-07-11; `0.11.0 → 0.11.1`).** Three small
  robustness/observability fixes surfaced by the pre-prod audit:
  - **Corrupt review/remediation reports no longer degrade silently**
    (`remediation/runner.py`). The two report-read sites that caught
    `JSONDecodeError`/`OSError` with a bare `pass` (→ default `{}` = "no findings",
    indistinguishable from a genuinely clean report) now emit a `logger.warning` so the
    silent-clean path is traceable.
  - **Empty-choices API responses surface as a normal executor failure**
    (`executor/api_runner.py`). A provider returning zero `choices` previously raised a
    bare `IndexError` that lost the executor-context the other error paths wrap; it now
    returns an `ExecutorResult(exit_code=1, …)` with a clear message. Regression test added.
  - **Deploy note for the built-in executors' localhost LiteLLM proxy**
    (`executor/registry.py`). Documented that the default executors require the local
    proxy (or a `UCX_EXECUTOR_*` / `executors.json` override) — a connection failure
    otherwise surfaces as a non-zero `exit_code` at call time, not a crash.

  (Audit item "delete dead vendored `sdd_doc_lint/`" was **rejected on verification** —
  it is a drift-guarded vendored copy, not dead code.) The parallel-review global-lock
  latency finding (a larger change) is tracked separately for a dedicated fix.

## [0.11.0] — 2026-07-11

### Added

- **Bounded, opt-in review→remediate→re-review quality loop (HERMES-REVIEW-LOOP-001
  Phase 1; `0.10.0 → 0.11.0`).** `sdd_review` gains a `quality_loop` boolean
  (default `false`). When set on the `saga_parallel` path, a failing readiness gate
  below the profile's `quality_loop_max_iterations` cap (default 3) auto-drives the
  remediation pipeline (findings → fix prompt → executor apply) and re-reviews the
  remediated copy; the final failing pass break-circuits to `PARTIAL_TIMEOUT`. Off
  (the default) the review is a single pass, byte-identical to before.
  - **Outer wrapper, not a state-machine change** (`review/quality_loop.py`,
    `run_review_quality_loop`). Each iteration is a _fresh forward saga run_
    (`run_project_review_build_saga` gains `iteration` / `quality_loop` /
    `is_final_iteration` params), so the forward-only transition table and
    `saga.schema.json` are untouched — no `framework/VERSION` change.
  - **Per-iteration journal discriminator (LB-7).** `deterministic_review_run_id`
    appends an `iterN` discriminator for `iteration > 1` only, so a same-clock-hour
    re-review lands in a distinct journal file instead of clobbering the prior pass's
    audit trail. The `iteration == 1` (default) id stays byte-identical.
  - **Gate at FANIN_REDUCED** (`_quality_gate_passed`): PASS iff the numeric review
    score `≥ gate_threshold` and no blocking findings. **Operating constraint:** the
    score is produced only on the `saga_parallel` + branch-LLM + framework-crew path;
    off it the score is `None` → the gate passes → the loop degrades to a safe single
    pass. A `SOFT_DEADLINE_SECONDS` (3600s) wall-clock bound also caps the loop.
  - Conformance: a real multi-iteration Hermes journal (`iteration > 1`, distinct file,
    both validate against `saga.schema.json`) + the Hermes mirror of the plugin's
    `test_invalid_transition_raises` invariant
    (`tests/conformance/test_saga_lifecycle_parity.py`). New unit coverage in
    `tests/unit/test_quality_loop.py` (loop-off single pass, FAIL→remediate→PASS,
    cap→`PARTIAL_TIMEOUT`, no-derived-copy stop, iteration threading).

  Feeds HERMES-BACKLOG **H-7** (iteration cap — shipped), **H-1** (`PARTIAL_TIMEOUT`
  write-site — now written on the quality-loop path; the general break-circuit +
  cross-invocation resume / G-R1 remain Phase 2), and unblocks **H-6.3** (iter-N vs
  iter-(N-1) regression detection — now has real iterations to compare).

## [0.10.0] — 2026-07-10

### Added

- **`audit_threshold` raise-only score gate (HERMES-ADAPT-ENFORCE-001; `0.9.0 → 0.10.0`).**
  Enforces the `.aidoc/profile.yaml` `audit_threshold` knob — the Hermes-native slice
  of H-16. A profile-declared per-layer threshold RAISES the effective readiness gate
  and never lowers it (per `ADAPTATION_SURFACE.yaml` "never weakens a gate"):
  - `validate_score` gains `audit_threshold: dict | None`; a per-layer value is
    honored **only if ≥ 90** (the framework-documented default, `PROFILE-TEMPLATE.yaml`)
    and applied as `max(effective, value)` after the tdd/iplan `90` floor
    (monotonic — can only push the gate up). Malformed / below-default / bool / float
    values are skipped. A `threshold_source` (`caller` / `readiness_floor` / `profile`)
    is recorded in the payload.
  - `sdd_score_validate` gains an **optional** `project` arg; when supplied, the
    handler resolves the profile via `ProjectContext` and passes its `audit_threshold`
    map (guarded `ctx.profile if ctx else None`). The lifecycle pipeline threads
    `project` into the `score_validate` re-dispatch. Without `project` / profile /
    a matching layer key → byte-identical to before.
  - Tests include a handler-level `_dispatch` wiring test that catches a
    dead-profile-wiring regression (validated: it fails if the handler stops passing
    the profile).

  **Still deferred (HERMES-BACKLOG H-16):** structural `active_layers`/`section_toggles`
  enforcement (the `active_layers` cascade lives in the byte-identical vendored lint —
  a framework change) and `quality_loop_max_iterations` (needs the outer review loop —
  H-7). See `plans/HERMES-ADAPT-ENFORCE-001-PLAN.md` §Out.

## [0.9.0] — 2026-07-10

### Added

- **`.aidoc/profile.yaml` runtime consumption — minimum honest (HERMES-REVIEW-001
  PR-ADAPT, D-0038 adaptation surface; `0.8.0 → 0.9.0`).** Hermes never read the
  spec's declared single adaptation input at runtime (M1/M7); now it does:
  - New `mcp_server/profile.py` — `load_project_profile(project_root)` reads
    `<root>/.aidoc/profile.yaml`, parses all 6 `ADAPTATION_SURFACE.yaml` knobs, and
    applies the spec-mandated graceful fallback on missing-file / missing-field /
    malformed-value (each knob defaults independently). Wired into
    `ProjectContext.resolve` as a `profile` field alongside env / executor config.
  - **A2 — `review_mode` reconciled.** The `sdd_review` tool now accepts the spec
    vocabulary `team` / `single_pass` as aliases for `saga_parallel` / `prompt_only`
    (schema enum + normalization). When the arg is omitted, a profile that
    _explicitly_ declares `review_mode` is honored; otherwise the existing
    `prompt_only` default holds (a profile present only for e.g. a glossary does not
    silently flip the review mode).
  - **A1 — prompt-injectable authoring knobs.** The creation prompt now injects a
    `## Project Adaptation Profile` block via `context_builder` carrying `glossary`
    (terminology), the layer-scoped `section_toggles` (which optional sections to
    author / skip), and `active_layers`. Unprofiled projects are byte-identical to
    before (empty block → omitted).

  **Deferred to a follow-up (see HERMES-BACKLOG H-16):** structural _enforcement_ of
  `active_layers` (layer skipping) and `section_toggles` (template mutation), the
  `audit_threshold` gate (its raise-only semantics need reconciling with
  `profile_contracts.resolve_threshold_precedence`'s override semantics), and
  `quality_loop_max_iterations` (Hermes has no outer review→remediate loop yet — H-7).

## [0.8.0] — 2026-07-10

### Changed

- **Native BDD authoring rewritten to YAML-BDD (HERMES-REVIEW-001 PR-BDD, D-0038;
  `0.7.4 → 0.8.0`).** Hermes's private BDD prompts/persona/output-schema still taught
  Gherkin `.feature` syntax while the framework had moved to the structured
  `scenarios:` YAML form (D-0038). This was the D-0038 gap the HERMES-BACKLOG banner
  wrongly claimed was auto-satisfied (H-15). Rewritten to the flat `scenarios:` YAML
  model (per-scenario `type`/`priority`, element-level `ears:` list, no Gherkin, no
  written `@`-tags):
  - `prompts/templates/creation/UCC_PROMPT_BDD.md` — authoring model + example + checklist.
  - `prompts/templates/review/UCR_PROMPT_BDD.md` — review criteria key on scenario
    structure + element-level `ears` coverage; QA-lead lens retargeted from Gherkin
    syntax to YAML-scenario structure.
  - `prompts/templates/remediation/UCRem_PROMPT_BDD.md` — fixes edit the `scenarios:`
    YAML; retired the `@EARS.XX`/`@happy-path` tag convention.
  - `skills/personas/qa_lead.md` — "Gherkin syntax purity" lens → `scenarios:` YAML
    structural lens.
  - `prompts/templates/creation/UCC_OUTPUT_SCHEMA.md` — Layer-4 output contract
    "Gherkin `.feature` files" → the `scenarios:` YAML block.
  - Stale-tag/wording cleanups (M6/L4/L5): `UCC_PROMPT_EARS.md` `@bdd:` file-path →
    element form `BDD.NN.SS.xxxx`; `UCC_PROMPT_PRD.md` 3-segment `@brd:` example →
    4-segment; retired "cumulative" upstream wording in `UCC_OUTPUT_SCHEMA.md` /
    `UCC_PROMPT_SPEC.md` / `UCRem_PROMPT_SPEC.md`.

### Added

- **BDD-prompt drift guard (`tests/unit/test_bdd_prompt_yaml_conformance.py`).** A
  Hermes-side guard asserting the BDD surfaces reference `scenarios:` and contain no
  _structural_ Gherkin markers (```gherkin fences, `Feature:`/`Scenario:`/`Background:`
  declaration lines, standalone Gherkin scenario-tag lines). It deliberately does not
  grep the bare word "Gherkin" (a correct prompt says "NOT Gherkin" as an anti-drift
  line). Converts a previously CI-invisible drift class into a CI-visible one. Kept
  Hermes-side rather than in the shared conformance suite (it asserts a platform's
  private prompts).

## [0.7.4] — 2026-07-10

### Fixed

- **MCP server source fixes (HERMES-REVIEW-001 PR-CODE; `0.7.3 → 0.7.4`).** Six
  correctness/hygiene fixes from the 2026-07-09 Hermes review, each with a
  regression test where behavior changes:
  - **C1 (H2) — API-executor env lock.** Replaced the lazily-created module-global
    `asyncio.Lock` (`_get_env_lock()` factory) with a module-global
    `threading.Lock`. The review saga fans branches over a `ThreadPoolExecutor`
    where each worker drives its own `asyncio.run` loop; the loop-bound
    `asyncio.Lock`, cached on first use, raised `RuntimeError` ("bound to a
    different event loop") under cross-thread contention. The lock is a sync
    context manager, so the acquire site changed `async with` → `with` and the
    factory collapsed. Parallel API-executor branches now serialize on env
    injection (correctness over the non-default API-path concurrency). New
    cross-thread regression test.
  - **C2 (M2) — versioned-report TOCTOU.** `write_versioned_report_atomic` now
    allocates versions with `os.open(O_CREAT|O_EXCL)` + retry-on-`FileExistsError`
    instead of the exists()-then-`os.replace` race (mirrors
    `saga_orchestrator._write_versioned_json`). New concurrent-writer regression test.
  - **C3 (L1) — deprecated datetime.** `saga_orchestrator._time_bucket` uses
    `datetime.now(UTC)` instead of the deprecated `datetime.utcnow()`.
  - **C4 (M3) — event-loop blocking.** The synchronous `run_project_review_build_saga`
    call in the async dispatch handler is offloaded via `await asyncio.to_thread(...)`
    so it no longer blocks the MCP event loop (composes with C1).
  - **C5 (L2) — cleanup unlink safety.** Each deletion goes through a helper that
    unlinks first and records the path as deleted only on success (try/except),
    so one unreadable file can't abort the batch half-done or make the result claim
    a file it never removed. A failed unlink is surfaced on a new
    `CleanResult.failed` field and exposed as `failed`/`failed_count` in the
    `sdd_clean` (MCP + CLI) responses, so a partial cleanup is no longer reported
    as an unqualified success.
  - **C6 (L3) — dead code + intent.** Removed the dead
    `if isinstance(required, list): pass` block in `scoring/runner.py`; annotated the
    TDD/IPLAN readiness gate as intentionally fail-closed (a missing readiness score
    does not pass).

## [0.7.3] — 2026-07-10

### Documentation

- **HERMES-REVIEW-001 PR-DOCS — active-facing docs/version drift sweep.** Finalizes
  the 0.7.3 release record and reconciles stale version/path/count references
  surfaced by the 2026-07-09 Hermes review (H3/H4/H5/M4/M5/M8, L6): `pyproject.toml`
  version `0.1.0` → `0.7.3`; `README.md` conformance block + platform-info table to
  real values (`VERSION` `0.7.3`, `FRAMEWORK_SPEC_VERSION`/spec `0.36.2`, canonical
  `hermes/v*` Version cell), source-module count `18` → `20` (+`team_emulator`),
  persona count `15` → `16`, and a complete 27-tool table; `docs/HERMES_INTEGRATION.md`
  pre-migration `ucx_framework/ucx_hermes` paths rewritten to the `platforms/hermes`
  layout, the `Python 3.11+` contradiction fixed to `>=3.12`, and the retired `ucx_kb`
  KB-runtime sections repointed to engramory; `docs/README.md` `2.0.0`/`ucx_hermes`
  self-id corrected, dead `migration/MIGRATION_FROM_MCP_UCX.md` link retired,
  `SPEC-011` added to the spec list; `docs/ROADMAP.md` legacy `2.0.0` table marked
  historical. Also extends `scripts/sync-version-refs.sh` to cover the Hermes
  `pyproject.toml` + README version blocks so they no longer re-drift
  (closes FRAMEWORK-TODO `HERMES-README-VERSION-DRIFT`). Docs + tooling only; no
  runtime behavior change.

### Added

- **Review calibration: no-findings rationale cap + strip author self-claim
  (HERMES-REVIEW-CALIBRATION, H-6.1 + H-6.2, D-0049; `0.5.1 → 0.6.0`).** Two
  FRAMEWORK-CLEANUP-001 review-quality deltas, as consumer-side enforcement of
  contracts already in `REVIEW_TEAM.md` + the injected playbooks (no framework
  change). **No-findings rationale (H-6.1):** the parser now captures a lens's
  `no_findings_rationale`, and `score_review` caps a lens scoring 100 with zero
  findings and no rationale to 95, emitting a `STRUCTURE-RAT-001` advisory in the
  verdict — a calibration nudge against "convergence theater." This also fixes a
  latent parser bug where a clean `findings: []` output fell through to a `fallback`
  P1 with `lens_score=None`, silently dropping the lens from scoring. **Strip author
  self-claim (H-6.2):** self-assessment score fields (`*_ready_score` / `*_score` /
  `readiness_score` / `audit_score`) are redacted from each section body before lens
  fan-out (in-prompt only; on-disk artifact untouched) to remove the anchor effect.
  The third H-6 delta (fixer-introduced regression detection) remains deferred —
  Hermes's saga is single-pass, so there is no prior iteration to compare.

- **8-layer playbook coverage (verified) + CHG crew parity (HERMES-PARITY-PHASE-3,
  D-0047; `0.4.0 → 0.5.0`).** Phase 2's playbook injection is layer-agnostic, so all
  8 lifecycle layers (not just BRD+PRD) already inject their per-`(layer,lens)`
  playbooks — now locked in by a regression test over every `REVIEW_CREWS.yaml` crew
  lens. Added the `chg` review crew to `persona_mappings.yaml` (crew parity with the
  framework CHG crew) and removed the `HERMES_DEFERRED_LAYERS` whitelist, so the
  crew-coverage conformance test now enforces CHG like the lifecycle layers. Crew-map
  parity only — a _live/sanctioned_ CHG saga review (adding `09_CHG` to
  `saga.schema.json` + a dispatch path) is a deferred follow-on; no default flow
  dispatches a `chg` review. No framework spec change.

- **Playbook injection for BRD + PRD (HERMES-PARITY-PHASE-2, D-0046; `0.3.0 → 0.4.0`).**
  The review saga now injects the per-`(layer, lens)` playbook
  (`framework/playbooks/{01_BRD,02_PRD}/<lens>.md`) into each crew lens's branch
  prompt, enforces the framework citation floor (every finding cites `check:` — a
  `Cn` id or `beyond-checklist:<tag>`; uncited findings are discarded on the LLM
  path), and emits `verdict.playbook_coverage`. New `playbook_loader.py` (crew-lens
  resolution via `REVIEW_CREWS.yaml`, keyed on crew membership so non-crew branch
  personas `fact_checker`/`chairperson` get no playbook and are NOT failed) +
  byte-identical vendor of the plugin's `finding_filter.py` (drift-guarded).
  `check` threaded through the parser → reducer (`ReducedFinding`) → verdict.
  Scope: the saga per-branch team-review path (BRD+PRD); other 6 layers + CHG and
  the `prompt_only` mode are Phase 3 follow-ons. No framework spec change.

### Fixed

- **Review lens now receives the document body — Hermes review was content-blind
  (HERMES-REVIEW-CONTENT-DELIVERY, D-0051; `0.6.0 → 0.7.0`).** The API-path LLM review
  never received the artifact body: `assemble_project_review_prompt` built the prompt
  from persona + template + rules + metadata-only JSON, the executor is a pure
  completion (`working_dir` not forwarded), and `system_prompt` was `None` — so the
  lens scored a document it had never read. Fixed at the single builder chokepoint:
  `assemble_project_review_prompt` now inlines a `## Document to Review` block from the
  per-persona `included_sections` (deduping the template's own placeholder), so every
  review path (MCP `prompt_only`, CLI `single_pass`, saga branches/aggregate) delivers
  the body. **Consequence:** the author-self-claim strip (H-6.2, shipped in `0.6.0`)
  was **inert** — it mutated section content that never reached the LLM; folding the
  strip into the shared builder (`run_project_review_build`) so the inlined body is
  stripped makes it effective for the first time. No new token accounting (the body's
  tokens were already counted). See D-0051; corrects D-0049.
- **Real saga journals conform to `saga.schema.json` (HERMES-SAGA-JOURNAL-CONFORMANCE,
  H-12, D-0048; `0.5.0 → 0.5.1`).** The real journal (`asdict(SagaRunState)`) was
  missing 4 schema-required fields — `artifact_id`, `layer`, `iteration`,
  `transitions` — and never recorded `transitions`; the Phase-1 guard validated only
  hand-authored fixtures, masking it. `SagaRunState` gains the 4 (defaulted →
  backward-compatible); `saga_journal.py` records schema-shaped transitions on the
  run seed, each successful `update_run_status`, and each branch status change (exactly
  `{ts, from, to, scope}`); `_to_run_state` roundtrips them. The orchestrator derives
  `layer` from the **required** `doc_type` via `normalize_layer(layer or doc_type)`
  (not the optional `--layer`, default `None`), so the default invocation stays
  schema-valid. Paired framework PATCH adds `09_CHG` to the schema enum so CHG review
  journals validate. New `SagaRealJournalConformance` validates a real journal (not a
  fixture) — the guard that would have caught H-12.
- **Saga state-machine conformance (HERMES-PARITY-PHASE-1, D-0045).** Hermes's
  `saga_models._ALLOWED_TRANSITIONS` was missing the spec's `PARTIAL_TIMEOUT`
  break-circuit state (`REVIEW_SAGA.md` requires it reachable from `PREPARED`,
  `FANOUT_STARTED`, `BRANCH_RUNNING`, `BRANCH_COMPLETED`, `FANIN_REDUCED`, terminal).
  Added it so Hermes's table equals the spec and the plugin's `tools/saga_driver.py`.
  New shared conformance test `tests/conformance/test_saga_lifecycle_parity.py` now
  enforces both platforms' tables against `REVIEW_SAGA.md` and validates a sample
  journal from each runner against `saga.schema.json` (the test `docs/PARITY.md`
  previously over-claimed already existed). **No version bump** — Phase 1 makes the
  state machine _accept_ the transition (parity contract); the orchestrator does not
  yet _write_ it (break-circuit exercise + resume is Phase 1b).

### Removed

- **Orphaned hand-vendored `references/` framework-doc copies** (H-11b, D-0059;
  `0.7.2 → 0.7.3`, skill `2.1.1 → 2.1.2`). Deleted 5 dead copies from the
  `sdd-orchestrator/references/` directory — `ucx-readme.md`, `doc-governance-core.md`,
  `id-naming-standards.md`, `layer-registry.yaml`, `data-consistency-report.json`. They were
  **orphaned** (grep-verified: no loader anywhere in the repo references them; `SKILL.md`
  loads none of them) and **stale drift-sources** — e.g. `id-naming-standards.md` was titled
  "SDD v3.2", was 53 lines vs the canonical 191, and described the **retired sequential-ID
  scheme** contradicting the current model. Per [[D-0013]] Hermes reads `framework/` directly
  (no local sync), so these copies had silently drifted; deleting them (rather than
  re-syncing) removes the drift/misinformation source. No behavioral change (nothing loaded
  them); 166 conformance + 511 Hermes tests green. Closes H-11b.

- **Legacy SYS/REQ/CTR/TSPEC layers** (PLATFORM-ALIGN Part B3, `0.2.0 → 0.3.0`).
  These layers are not part of the 8-layer SDD framework (the framework absorbed
  SYS→SPEC, REQ→EARS, CTR→SPEC, TSPEC→TDD); they were retained only as a "legacy
  compatibility" surface. Removed the **operative** surface: the 12 prompt
  templates (`UC{C,R,Rem}_PROMPT_{SYS,REQ,CTR,TSPEC}.md`), the `sys/req/ctr/tspec`
  entries from `skills/registry.py` `LAYER_PREFIXES` and `skills/persona_mappings.yaml`
  (creation + review), the `ctr` structure branch in `validation/runner.py`, and
  the `skills/README.md` mention; the legacy-layer tests in `test_validation_runner.py`
  were dropped/trimmed. `tasks` (the IPLAN rename-alias) is retained.
  Also scrubbed the **descriptive** legacy-layer references from the vendored
  persona profiles (`skills/personas/*.md`): dropped the dead `SYS/REQ/CTR/TSPEC`
  scoring-weight lines, removed those tokens from each persona's `doc_types`
  list, and removed the dedicated layer rows + sections (e.g. integration_lead's
  "CTR Expertise", qa_lead's "TSPEC Quality Metrics"). _Deliberately retained:_
  the `agent-skills/` historical notes documenting the layers as "cut from
  v3"/"deprecated" (accurate history) and the threshold-rules `req`/`ctr` tokens
  (unrelated meanings — rate/Currency-Transaction-Report).

### Changed

- **sdd-orchestrator published docs reconciled to the single-path model**
  (ENG-STALE-DEPTH-DOCS; `0.7.1 → 0.7.2`, skill `2.1.0 → 2.1.1`). Completes the behavioral
  legs of H-11a: the skill's **user-facing** `root-docs/` + `governance/` docs still
  advertised the dead v3.2 **SDD-Lite / SDD-Standard / SDD-Full depth-variant** model (the
  2026-06-12 legacy cleanup fixed `sdd_config.yaml` + the repo README; D-0053 fixed the
  SKILL + 2 loaded governance files; these published surfaces were the remainder). Fixed:
  `root-docs/README.md` (the "Scalable Depth" tagline + the "SDD Depth Variants" table that
  **contradicted the same file's** already-correct single-path prose),
  `root-docs/MULTI_PROJECT_QUICK_REFERENCE.md` + `MULTI_PROJECT_SETUP_GUIDE.md` (two more
  depth-selection tables + an embedded changelog line), `governance/CHG_GOVERNANCE_BRIDGE.md`
  (a governance rule keyed on the dead tiers), and **two dead links** to a nonexistent
  `governance/SDD_DEPTH_GUIDE.md` (removed). All reconciled to the single SDD path (8 layers
  required per NECESSARY-UPSTREAM-001; MVP → PROD → NEW MVP; CHG overlay). A dead "SDD-Full"
  term in the CHG-label comments was dropped (no `create_label` value changed). Doc-accuracy
  only — no engine change, no `framework/` change. No new decision (governed by the
  2026-06-12 cleanup + D-0053). Deferred: the public-render leg + the cosmetic v3.2
  string sweep (H-11a proper).

- **sdd-orchestrator skill modernized to the weighted-crew + playbook + single-path
  model** (H11-ORCHESTRATOR-CREW-MODEL, D-0053; `0.7.0 → 0.7.1`). The
  `agent-skills/.../sdd-orchestrator` skill described the obsolete v3.2 "15 parallel
  personas + Lite/Standard/Full depth-tier" model the engine abandoned. Corrected, in
  `SKILL.md`: the persona model (frontmatter/Overview + the inert UCX→Hermes 15-persona
  mapping and the creation/review assignment tables → point at
  `framework/governance/REVIEW_CREWS.yaml` as the authority for all 9 weighted crews +
  one illustrative BRD crew + a `framework/playbooks/` / LAYER-PLAYBOOKS-001 cross-link);
  the superseded "8-category weighted-deduction" chairperson formula → the current
  **weighted-average of crew `lens_score`s, capped by unresolved P0/P1** (matching
  `review/review_scoring.py`); the wrong "All 15 required BRD sections" list → point at
  `BRD-TEMPLATE.yaml`; the "4-persona" EARS/BRD counts → the 5-lens crews; the stale
  `/opt/data/ucx_framework/.venv` MCP-config paths → the canonical `/path/to/python`
  placeholder; and dropped the "SDD v3.2" version pins. Two **loaded** governance files
  carrying the abandoned Lite/Standard/Full depth-tier model —
  `governance/GOVERNANCE_RULES.md` §7 and the primary-load
  `references/governance-load-protocol.md` — were replaced with the current single-path
  layer model (no tiers; necessary-upstream contract; MVP → PROD → NEW MVP). Skill
  `version: 2.0.0 → 2.1.0`. Doc-accuracy only — no engine/runtime change, no `framework/`
  change. _(Deferred backlog: the ~25-file cosmetic "v3.2" string residue across the
  inherited governance scaffold; the hand-vendored `references/` framework-doc copies
  (D-0013 delete-vs-resync); the element-ID SHA-256 residue, framework-gated by
  PROVISIONAL-IDS-002.)_

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
  form. _Stricter validation:_ a previously-accepted 3-segment ID now fails —
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
  reframed as _composition_ of the base patterns (the standalone `Complex` row +
  the `CX` type code removed). Doc-only; no runtime behavior change.
  _(Note: the prompts' legacy type-code element-ID scheme — `EARS.NN.<code>.<seq>`
  vs the framework's hash-based `EARS.NN.SS.xxxx` — is a separate, pre-existing
  divergence, out of scope here.)_

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
