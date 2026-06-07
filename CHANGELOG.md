# Changelog

All notable changes to the AI Doc Flow Framework (multi-platform project) are
documented here. Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope: this is the **project-level** changelog tracking the multi-platform
> migration. Once scaffolded, each platform keeps its own changelog at
> `platforms/<name>/CHANGELOG.md`, and `framework/` versions independently.
>
> This file logs both project releases (`v1.x.y`) and framework-spec releases (`Framework Spec 0.x.y`). Per-stream details for the Claude Code plugin live in [`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md).

## [Unreleased]

### Changed — Claude Code plugin (plugin-only; no spec change)

Plugin-side post-spec-0.13.0 work. The framework spec stays at `0.13.0`;
the entries below describe how the plugin implements (and iterates on
the implementation of) the saga-lifecycle contract codified in
SAGA-PARITY-001 Phase 1. See
[`platforms/claude-code-plugin/CHANGELOG.md`](platforms/claude-code-plugin/CHANGELOG.md)
for the per-release plugin detail.

- **Plugin v0.6.0 — BRD-layer saga via cooperative enforcement
  (SAGA-PARITY-001 Phase 2).** First plugin implementation of the
  framework saga lifecycle; SKILL-prompt-driven cooperative
  enforcement of state-machine transitions. Empirically failed
  end-to-end verification (invalid transitions, non-terminal final
  status, no actual subprocess dispatch); fixed in Amendment 1
  (below).
- **Plugin v0.6.1 — preemptive saga driver
  (SAGA-PARITY-001 Phase 2 Amendment 1).** New `tools/saga_driver.py`
  (Python stdlib-only) replaces cooperative enforcement with
  deterministic script-driven enforcement; vendored alongside the
  framework bundle. 7 in-flight bugs (B1-B7) fixed on the same branch
  per the submit-only-finalized-work principle. Verified end-to-end on
  the 4th live BRD cascade: `status: CLOSED`, score 96/100, 10/10
  pass criteria. PRD..IPLAN saga driver propagation deferred to
  Phase 4.
- **Plugin v0.6.2 — 5 content sub-checks across 8 audit SKILLs
  (REVIEW-CALIBRATION-001).** Adds A1 cell-actionability + A2
  assumption-capture + A3 cross-section pointer-validity (auditor
  lens), BA1 acceptance-criterion testability (business_analyst
  lens), SE1 deferred-decision safety (security_engineer lens) —
  uniformly applied across all 8 layer audit SKILLs. Catches 5
  substantive content-quality issues that v0.6.1's review missed
  (visit-count AC untestable; sync-response content unspecified;
  qualitative budget non-actionable; assumption-shaped prose buried
  in FRs; Med/High risks with deferred mitigation). Verified
  before/after on the saved BRD-01: all 5 issues remediated. No
  spec touch, no new lens, no weight changes.

### Added — Project-level conventions

- **"Submit only finalized work" durable convention**
  (CLAUDE.md, [#90](https://github.com/vladm3105/aidoc-flow-framework/pull/90)) —
  every PR (plan or impl) must already have completed its
  review-and-fix cycles locally; post-merge amendment PRs to recently-
  merged work are forbidden.
- **"Minimal-and-realistic plans" durable convention**
  (CLAUDE.md, [#93](https://github.com/vladm3105/aidoc-flow-framework/pull/93)) —
  a plan should be sized to the problem it addresses, not "a perfect
  plan to do everything"; speculative scope gets parked as one-line
  backlog enumeration, not drafted.
- **Two-cycle plan review (mandatory)**
  (CLAUDE.md, [#86](https://github.com/vladm3105/aidoc-flow-framework/pull/86) + [#90](https://github.com/vladm3105/aidoc-flow-framework/pull/90)) —
  every plan must complete ≥2 full review→patch→re-review cycles
  BEFORE the plan PR opens.
- **Plugin-first development sequencing**
  (ROADMAP.md, [#97](https://github.com/vladm3105/aidoc-flow-framework/pull/97)) —
  features land on the plugin first; Hermes follow-on batches per
  `plans/HERMES-BACKLOG.md`.

### Changed — Framework Spec 0.12.0 → 0.13.0 (CHG-gated)

- **Review-saga lifecycle promoted to framework spec
  (SAGA-PARITY-001-PHASE-1, D-0031).**
  - New: `framework/governance/REVIEW_SAGA.md` — engine-agnostic saga
    lifecycle contract (state machine, transitions, journal schema,
    break-circuit policy, FRAMEWORK_SPEC_VERSION semantics,
    enforcement-asymmetry caveat).
  - New: `framework/governance/saga.schema.json` — formal JSON Schema
    for the per-run saga journal.
  - Edit: `REVIEW_TEAM.md` adds two one-line `> See also`
    cross-references to REVIEW_SAGA.md (no content duplication).
  - D-0031 supersedes D-0005's scope-narrowing premise. D-0005's
    blackboard-for-crew-state reasoning remains authoritative.
  - `framework/VERSION`: `0.12.0 → 0.13.0`.
  - Both platforms declare `FRAMEWORK_SPEC_VERSION = 0.13.0` (intent
    to conform; implementation arrives in Phases 2 and 3 of
    SAGA-PARITY-001).

### Changed — Framework Spec 0.11.3 → 0.12.0 (CHG-gated)

- **Adversary review-lens partitioned into `chaos_engineer` + `security_engineer`
  (CHAOS-SEC-SPLIT-001, D-0030; plan in #78, impl in #79).**
  - `framework/governance/REVIEW_CREWS.yaml`: removed `adversary` from the
    personas registry; added `chaos_engineer` (internal stability) and
    `security_engineer` (external threats). All 8 crews rewritten with new
    per-layer weights (all sums = 100) and `# rationale:` comments per crew.
    Bias: BRD/EARS chaos-heavy (12:8), BDD chaos-heavy (14:6), ADR
    security-heavy (8:12), PRD/SPEC/TDD equal split, IPLAN chaos-only.
  - `framework/governance/REVIEW_TEAM.md`: prose mention of `adversary`
    updated to reference both new lenses; new `## Weight allocation rules`
    subsection codifies the four-category allocation protocol
    (chaos-heavy / security-heavy / equal / chaos-only).
  - `framework/VERSION`: 0.11.3 → 0.12.0.
  - Per-platform impact: Claude Code plugin bumped to v0.5.0 (BREAKING —
    blackboard slot filenames change: `adversary.json` →
    `chaos_engineer.json` + new `security_engineer.json`). Hermes
    FRAMEWORK_SPEC_VERSION bumped to 0.12.0; Hermes' runtime persona was
    already `chaos_engineer` so the migration was minimal (translation
    layer removed, new persona file added). Per-platform changelogs
    document the breaking-surface details.

### Fixed

- Closed a confabulation hole in the Claude Code plugin's read-time/audit
  skills: `doc-flow` and every `doc-<layer>-audit` skill now explicitly require
  the auditor to load the corresponding `*-TEMPLATE.yaml` and enumerate the
  required sections from it before running the structural check, with a
  written ban on rationalising drift as a "compact" / "walkthrough" / "lint-
  pinned" variant. The audit Structure cells now defer to that enumeration
  instead of hard-coding "all N template sections", which was a brittle parallel
  source of truth. Also realigned three creation skills with their templates:
  `doc-brd` (replaced an 18-section list containing phantom sections — User
  Stories, Implementation Approach, Support & Maintenance, Cost-Benefit, Quality
  Assurance — with the template's actual 15 numbered sections plus the diagrams
  registry and appendix backmatter; remapped `§7.2 ADR Requirements` → `§8
  adr_topics` everywhere it was cross-referenced; dropped stale `§3.6/§3.7`
  Platform-vs-Feature cross-refs that never existed in the template), `doc-ears`
  and `doc-adr` (renumbered to count `document_control` as Section 1, matching
  the template's own `# Section N:` numbering and the PRD-style convention).
  New conformance test `tests/conformance/platforms/test_skill_template_alignment.py`
  prevents the drift class from recurring: audit skills must carry the explicit
  enumeration block and no hard-coded count; creation skills' `Required structure
  (N sections)` heading must match the template's numbered count; and creation
  skill section lists must use only template-derived vocabulary (no phantoms).
  Template is the single source of truth (D-0013).
- Purged the pre-migration legacy taxonomy from the Hermes prompt templates so
  the creation/review/remediation agents follow the v3.2 source-of-truth naming
  convention (`ucx_flow_v3`). Removed the 10/12-layer `SYS / REQ / CTR / TSPEC /
  TASKS` model (the framework is the 8 layers BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN)
  from `UCC_OUTPUT_SCHEMA.md`, `UCC_PERSONAS.md`, and the `UCC_/UCR_/UCRem_`
  prompts; corrected `SPEC` from Layer 9 → 6 and the upstream/downstream chains;
  and converted legacy element-ID forms to the canonical 4-segment
  `{TYPE}.{doc}.{section}.{hash}` (`TYPE.NN.SS.xxxx`) — dropping the type-code +
  sequence variant (`NN.TT.SS`) and 3-segment forms (`ADR.{doc}.{seq}`). Renamed
  PRD's legacy `SYS-Ready` score to `SPEC-Ready`. Platform-only; no framework
  spec change.

### Changed

- Framework spec **0.11.2 → 0.11.3** (patch, additive) — new
  `framework/governance/PROFILE-TEMPLATE.yaml` skeleton ships as the
  bootstrap source for project profiles. Operationalises the precedence
  chain (`framework defaults < user-global seed < project profile`)
  documented in `framework/governance/ADAPTATION.md` since v0.11.0:
  bootstrapped `.aidoc/profile.yaml` now carries no hardcoded overrides
  — every adaptation knob is commented out, falling through to
  framework defaults. Frees the framework to evolve crew/persona
  defaults without breaking existing projects (which was foreclosed by
  the previous bootstrap-as-byte-copy behaviour). No schema or rule
  change; no existing key removed; every existing profile continues to
  parse. Plugin v0.4.1 → v0.4.2 binds the new mechanism. New
  conformance test
  `tests/conformance/platforms/test_profile_schema.py` validates the
  closed-surface contract for project profiles. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 52 plugin
  skills' `framework_spec_version` re-synced to 0.11.3. See
  `plans/PROFILE-DELTA-OVERRIDE-PLAN.md` and DECISIONS.md D-0025.
- **Acceptance suite: `--dry-run` and `--no-live` consolidated into a
  single behaviour.** The two modes overlapped on Phase 0 preflight
  (manifest validate, profile check, fixtures presence) — running
  both back-to-back wasted a Phase 0 pass. `--no-live` now prints the
  planned-execution summary (phases, cost cap, timeouts, live status)
  at the top of every run, *then* continues into the full
  deterministic suite (negative fixtures + hook). `--dry-run` is kept
  as a clean alias of `--no-live` (the conventional name is widely
  expected). One mode is now sufficient for both "preview before
  spending" and "verify deterministic infrastructure" — strictly more
  coverage than the old `--dry-run` (which exited after Phase 0).
- **Acceptance methodology consolidated into permanent docs.** The
  example-scoped `examples/url-shortener/ACCEPTANCE_TEST_PLAN.md`
  (733 lines) was split into framework-wide permanent locations so
  future examples (`payment-gateway`, etc.) reuse a single source of
  methodology truth: [`tests/ACCEPTANCE.md`](tests/ACCEPTANCE.md) —
  the engine-agnostic methodology (driver, log layout, schema,
  `--promote` algorithm, phase definitions, design decisions, cost
  ballpark, CI integration); [`plans/ACCEPTANCE-SUITE-HISTORY.md`](plans/ACCEPTANCE-SUITE-HISTORY.md)
  — per-PR implementation timeline + v1→v4 plan evolution + lessons
  learned; and a thin
  [`examples/url-shortener/README.md`](examples/url-shortener/README.md)
  (~120 lines) covering only what is unique about that seed. Adding a
  sibling example is now just `seed/` + `chg/` + a ~50-line README
  pointing at the methodology — no duplication of phase definitions,
  schema docs, or design decisions. Framework spec **0.11.1 → 0.11.2**
  (patch) covers the engine-agnostic doc-link relocations (see
  immediately below).
- Framework spec **0.11.1 → 0.11.2** (patch) — doc-only refs in
  `framework/README.md` and `framework/docs/AIDOC.md` updated to
  point at `tests/ACCEPTANCE.md` (relocated from
  `framework/docs/ACCEPTANCE_TESTING.md` so the framework spec stays
  engine-agnostic). No schema or rule change. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 52 plugin
  skills' `framework_spec_version` re-synced to 0.11.2.
- Framework spec **0.11.0 → 0.11.1** (patch) — doc-only addition of
  `framework/docs/AIDOC.md` formalising the `.aidoc/` provenance tier
  as part of the engine-agnostic spec. No schema or rule change. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 52 plugin
  skills' `framework_spec_version` re-synced to 0.11.1.
- **Test runners co-located under `tests/scripts/`.** Moved `test-plugin.sh`,
  `test-layer.sh`, and `test-fullpath.sh` from the parent repo's `scripts/`
  into `framework/tests/scripts/`. The framework is now fully self-testable
  with no parent-repo dependency; `tests/` becomes the single boundary for
  everything related to verifying the spec. Run-log layout reorganised into
  per-run directories keyed by ISO timestamp:
  - Example-driven default suite (Phase 3 `sdd_doc_lint` + Phase 4 live
    probe target a specific example) → `examples/<NAME>/logs/<TS>/`
    (`plugin-test.log` + `probe-doc-flow.txt`).
  - Fixture-driven suites (unit / layer / fullpath / pre-deploy / packaging /
    release / smoke / review — none touch `examples/`) →
    `tests/logs/<TS>/plugin-test.log`.

  `.gitignore` updated to cover both. Default-suite Phase 3 now SKIPs cleanly
  when the targeted example's `docs/` is missing or empty (post-demo-reset
  state) instead of silently passing on zero files. Internal doc references
  (`tests/README.md`, `tests/HOWTO.md`, `tests/TROUBLESHOOTING.md`,
  `tests/smoke/COMMANDS.md`, `examples/url-shortener/README.md`) updated to
  the new path. Companion parent-repo PR drops the obsolete copies and
  updates `release.yml` to call `framework/tests/scripts/test-plugin.sh`.
- Framework spec **0.9.1 → 0.10.0** (minor) — AUTHORING-STYLE follow-up
  AS2: every section in every layer template (8 × ~10 sections = 76
  sections) gains a `_size_target` key with an explicit per-section word
  count drawn from AUTHORING_STYLE.md tiers (100 / 200 / 300 / 500 / 800
  per section purpose). `sdd_doc_lint` STY02 now reads this per-section
  target via heading-to-key normalisation (with `_BLOCKING_FACTOR = 1.5`
  applied) instead of the flat 200-word default; behaviour identical for
  sections without a `_size_target` key. Both `FRAMEWORK_SPEC_VERSION`
  files (Hermes + plugin) and the 50 plugin skills' `framework_spec_version`
  re-synced to 0.10.0.
- Framework spec **0.9.0 → 0.9.1** (patch) — AUTHORING-STYLE follow-up AS6:
  PRD-TEMPLATE.yaml `_guidance` blocks normalised to imperative voice
  ("Specify" replaces "Elaborate" in three places). No spec semantics
  change. Both `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 50
  plugin skills' `framework_spec_version` re-synced to 0.9.1.
- Framework spec **0.8.1 → 0.9.0** (minor) — additive governance change:
  adds principle 7 ("token-efficient authoring") to `DOC_GOVERNANCE_CORE.md`
  and the new `AUTHORING_STYLE.md` governance doc. Both
  `FRAMEWORK_SPEC_VERSION` files (Hermes + plugin) and the 50 plugin skills'
  `framework_spec_version` re-synced to 0.9.0.
- Framework spec **0.8.0 → 0.8.1** (patch) — AUDIT-FIXUPS WS-A: the ADR (L5)
  template now **requires** a decision/interaction `sequenceDiagram` (carrying its
  intent header + `@diagram: sequence-*` tag), with `flowchart` demoted to an
  optional supplement — matching `DIAGRAM_STANDARDS.md` ("Required decision
  sequence"). Previously `ADR-TEMPLATE.yaml` offered sequence/flowchart as equals
  and never required the sequence. Both `FRAMEWORK_SPEC_VERSION` files + the 54
  plugin skills' `framework_spec_version` re-synced to 0.8.1.
- Platform agents now apply the framework's **C4 + DFD + sequence** diagram model
  (`framework/governance/DIAGRAM_STANDARDS.md`) in review and creation.
  Hermes review personas (`architect`, `integration_lead`, `auditor`) gained
  per-layer diagram-review lenses (injected into every crew); the SPEC review
  prompt now verifies the C4-L3/DFD-L3 diagram contract; the orchestrator's
  `references/diagram-standards.md` was de-contaminated of plugin-only tokens
  (`mermaid-gen`, `.claude/skills/…`) and now points to the framework as
  authority. Plugin agents (`solutions-architect`, `traceability-auditor`,
  `code-reviewer`) make the C4/DFD/sequence + `@diagram:` tag + C4-L4 ownership
  checks explicit. Also corrected a residual legacy layer number (SPEC
  **L9 → L6**) in the `tech_lead`/`integration_lead` personas and the SPEC
  review/remediation prompts. Platform-only — no framework spec change.
- Framework spec **0.7.1 → 0.8.0** (minor) — AGENT-TEAM Phase 0: the
  engine-agnostic **review-team** model. New `framework/governance/REVIEW_TEAM.md`
  (multi-persona crews + a hub blackboard + the persona-output contract + a
  deterministic weighted/capped scoring & conflict policy with the structural gate
  as the reproducible floor + create/review/remediate shapes + resilience/security)
  and `framework/governance/REVIEW_CREWS.yaml` (per-layer crews + scoring weights +
  default mode). Adds a `review_mode` (`team`|`single_pass`) knob to
  `ADAPTATION_SURFACE.yaml`. New `tests/conformance/test_review_team.py` validates
  the crews (layers ⊆ 8, personas ⊆ the closed set, weights sum to 100); both new
  governance files registered in the README + `test_governance` (suite now 54).
  Engine-agnostic — each platform binds the personas to its own agent runtime
  (Phase 1 Hermes conform, Phase 2 plugin build). Both `FRAMEWORK_SPEC_VERSION`
  files + the 54 plugin skills' `framework_spec_version` re-synced.
- Framework spec **0.7.0 → 0.7.1** (patch) — documentation consistency pass
  (post-EARS-changes review). Corrected three 3-segment element-ID examples in
  `EARS-TEMPLATE.yaml` to the canonical 4-segment form (`TYPE.NN.SS.xxxx`): the
  `id_standard` example (`EARS.01.c4d8` → `EARS.01.03.c4d8`, which had contradicted
  its own stated format) and two `_antipatterns` (`PRD.01.1dbc`/`BRD.02.f1de` →
  4-segment, so each shows only its named flaw). Added `SECURITY_REVIEW.md` and
  `REVIEW_REMEDIATION_FLOW.md` to the `QUICK_REFERENCE.md` Key Files table (they
  were missing since their introduction). Both `FRAMEWORK_SPEC_VERSION` files and
  the plugin skills' `framework_spec_version` re-synced. No schema/rule change.

- Framework spec **0.6.0 → 0.7.0** (minor) — DOC-CHECK Phase 0: model the
  **review→remediation→gate quality loop** and its **trigger points** in the spec
  (new `framework/governance/REVIEW_REMEDIATION_FLOW.md`). Previously review and
  remediation existed only as platform capabilities; the spec now names the loop
  (`Draft → Review → Remediate → Gate → Approved`) and four engine-agnostic
  trigger points — `on_author`, `on_gate_fail`, `pre_promotion`, `pre_merge` —
  with a **light conformance contract**: at each point an engine supports, it
  surfaces findings, the readiness score vs the gate, and the remediation path;
  *how* (deterministic vs LLM, hook vs CI) is the engine's choice, and each engine
  documents its own trigger-point → capability mapping. Does not change the
  readiness-gate threshold or the CHG gates. Additive/backward-compatible.
  Registered in the governance README + `test_governance` `EXPECTED_FILES`; both
  `FRAMEWORK_SPEC_VERSION` files and the 54 plugin skills' `framework_spec_version`
  re-synced. *(Platform triggers — the write-time hook (#1) and PR-time CI (#2) —
  follow as a separate platform/tooling change.)*
- Framework spec **0.5.0 → 0.6.0** (minor) — FRWK-REVIEW finding **#4b**: EARS
  statement-model reconciliation. The EARS layer described its own model four
  different ways (template/README: 4 patterns in `THE…SHALL` form; index: 5 types
  in a non-EARS `…THEN…` form; plugin `requirements-analyst`: 5 patterns dropping
  Unwanted; Hermes personas: 6). Standardized on **canonical EARS** (decision
  D1=A): the five patterns **Ubiquitous, Event-driven (WHEN), State-driven
  (WHILE), Optional (WHERE), Unwanted (IF)**, all using the canonical response
  clause `THE [component] SHALL …` — the non-EARS `THEN` connective is removed.
  Added the missing **Optional / `WHERE`** pattern (guidance + structured
  `optional_feature` block) to `EARS-TEMPLATE.yaml`; added the Optional row to the
  README and corrected the index table to the `SHALL` form; documented "complex"
  as *composition* of the base patterns (not a sixth type) and `WITHIN` as a
  framework timing extension. Aligned the first-class plugin docs (`doc-ears`,
  `requirements-analyst`). New `tests/conformance/test_ears_model.py` locks the
  five-pattern set + `SHALL` grammar so the files can't re-diverge (suite now 49).
  Backward-compatible (existing documents stay valid). Both `FRAMEWORK_SPEC_VERSION`
  files and the plugin skills' `framework_spec_version` re-synced. *Deferred:*
  aligning the Hermes vendored `agent-skills`/`prompts` EARS tables (platform
  follow-up, not a framework-spec change).
- Framework spec **0.4.0 → 0.5.0** (minor) — FRWK-REVIEW pre-production audit,
  batch 3 (THRESHOLD de-bloat, #12). Trimmed `framework/governance/THRESHOLD_NAMING_RULES.md`
  to its engine-agnostic naming/tag/boundary core: **genericized** the
  domain-specific financial examples (KYC verification tiers, B2B/B2C scaling,
  AML/CTR/SAR abbreviations, USD framing) to neutral `quota`/tier placeholders in
  place, and **removed** the runtime/operational machinery that is out-of-charter
  for a spec that ships no runtime — the §8 *Environment Override Rules*
  (override permission matrix, prod override workflow, environment scaling), the
  §12 governance *configuration-propagation* SLAs ("within 60 seconds") and the
  *approver-role* matrix. Condensed the duplicated per-layer usage examples (§1.3.3
  now points to §6). Replaced the stale "UCX Flow Team" / 2025-12-16 document
  history with a neutral provenance note. No programmatic consumer parses the
  file (verified across both platforms); references to it are documentation
  links, which still resolve.

  > **Deprecation note.** Threshold *runtime/override/operational* policy is no
  > longer specified by the framework. A consuming project that relied on the
  > removed §8/§12 operational guidance should define environment-override and
  > rollout policy in its own configuration governance; the framework standard
  > now covers only naming, `@threshold:` referencing, and boundary semantics.

- Framework spec **0.3.2 → 0.4.0** (minor) — FRWK-REVIEW pre-production audit,
  batches 1 (correctness) + 2 (security). **Correctness:** corrected malformed
  trace-tag examples in the SPEC/TDD templates to the registry's element form
  (`TYPE.NN.SS.xxxx`, never a `TYPE-NN.SS.xxxx` hybrid) and added an `id_standard`
  note to the SPEC/TDD/IPLAN templates documenting where document-level refs are
  the intentional per-component bridge; reframed the BDD template's downstream
  guidance; closed a numbering gap in the BRD template's extra-small requirement
  IDs; renamed the PRD index status "Review" → "In Review" with a
  doc-status-vs-lifecycle note; documented the index-template extension split in
  the layer registry; retired stale "5-Gate" branding now that GATE-SPEC is the
  sixth gate, unified the emergency post-mortem SLA to 48h, and surfaced GATE-SPEC
  on the change-approval form + post-mortem template. **Security:** new
  `framework/governance/SECURITY_REVIEW.md` (engine-agnostic safety checks for
  agent-authored artifacts — secret leakage, prompt-injection, provenance,
  active-content sanitization), referenced from `DOC_GOVERNANCE_CORE.md` and the
  gates; a new blocking `GATE-03-E008` requiring external-source changes to cite a
  CVE/advisory or an explicit `no advisory applies: <reason>` escape (W001 kept as
  the softer nudge); a `DIAGRAM_STANDARDS.md` sanitization rule for mermaid click
  handlers + inline HTML; and a `GATE-SPEC-W003` security/abuse-review check for
  agent-facing spec changes. New `tests/conformance/test_framework_review_guards.py`
  locks the correctness fixes in (suite now 46 tests); `test_governance.py`
  `EXPECTED_FILES` gains `SECURITY_REVIEW.md`. Both `FRAMEWORK_SPEC_VERSION` files
  and the plugin skills' `framework_spec_version` re-synced.
- Framework spec **0.3.1 → 0.3.2** (patch) — `framework/README.md` governance
  section now documents GATE-SPEC, the project adaptation overlay
  (`ADAPTATION.md` + `ADAPTATION_SURFACE.yaml`), and `DECISIONS.md` (the
  spec-level decision register). Doc-only; both `FRAMEWORK_SPEC_VERSION` files
  and the plugin skills' `framework_spec_version` re-synced.

### Added

- **Acceptance suite: resume + partial-execution support.** The driver
  (`tests/scripts/test-acceptance.sh`) now survives long-running
  interruptions and supports targeted re-runs without re-spending the
  full $15–25 of a cascade. **Resume** (R1–R6): SIGINT/TERM trap saves
  an incremental `summary.json` and marks in-flight elements
  `INTERRUPTED`; `RUNNING` stubs distinguish in-progress from
  PASS/FAIL/SKIP; `--skip-completed=<path>` resumes against a prior
  run's summary, replaying only `FAIL` / `INTERRUPTED` / `RUNNING`
  elements; schema bumped v1.1 → v1.2 to add the `RUNNING` and
  `INTERRUPTED` outcomes. **Partial execution** (P1–P5): `--element=<name>`
  runs a single named element (skill, agent, command, or hook);
  `--from-layer=<N>` / `--to-layer=<N>` constrain the cascade range
  (e.g. *"generate only the PRD against the existing BRD"*); `--dry-run`
  previews which elements would invoke without spending tokens;
  `--cost-cap=<USD>` halts the run when the running token estimate
  reaches the cap. The companion `summary.json` is the single source of
  truth — `_should_invoke()` consults it before every skill call, so a
  resumed or partial run re-uses prior-PASS outputs as upstream inputs
  for downstream layers.
- **`.aidoc/` — third committed documentation tier formalized.** Per
  every project, four tiers now: inputs (`seed/`, `chg/`, committed),
  outputs (`docs/`, committed), provenance (`.aidoc/`, committed),
  tool internals (`logs/<TS>/`, gitignored). `.aidoc/` holds the audit
  reports, review consensus, remediation logs, validation reports,
  security reviews, and quality suggestions that AI personas produced
  while authoring the project's chain — answering "how did the AI
  arrive at the output in `docs/`?" without needing to re-run the
  suite. New `framework/docs/AIDOC.md` is the canonical reference.
  Acceptance suite (`tests/scripts/test-acceptance.sh`) restructured
  to route skill outputs accordingly: `doc-<layer>-autopilot` → `docs/`,
  `doc-<layer>-audit` → `.aidoc/audit/`, `doc-<layer>-fixer` →
  `.aidoc/remediation/`, `review-team` → `.aidoc/review/`,
  `doc-validator`/`doc-ref`/`gate-check` → `.aidoc/validation/`,
  `security-audit` → `.aidoc/security/`, `quality-advisor` →
  `.aidoc/quality/`. Log layout flattened into single
  `logs/<TS>/elements/<name>.log` per element with YAML front-matter
  plus raw stdout. `.gitignore` rule for `.aidoc/review/` split: only
  `.aidoc/review/.blackboard/` (per-persona scratch) stays ignored;
  consensus reports under `.aidoc/review/<layer>-consensus.md` are
  committed. Acceptance suite includes per-skill timeout (`B4`),
  fixer `tmp/backup/` cleanup (`B5`), token estimation + cost cap
  (`B6` + `A8`), `--skip-completed` (`A6`), `--from-layer=<N>`
  resume (`A7`), retry-on-transient-HTTP-error (`A9`), and per-layer
  runtime cap (`B2`). Schema bumped to v1.1
  (`tests/scripts/test-acceptance.schema.json`).

- **Pre-deployment acceptance test suite** — new
  `tests/scripts/test-acceptance.sh` (~1500 lines) drives every active
  plugin surface element (50 skills + 11 agents + 1 command + 1 hook =
  63 total) against a named example's seed; the produced chain is the
  release-gate evidence that the plugin works end-to-end.

  Driver structure (per
  [`examples/url-shortener/ACCEPTANCE_TEST_PLAN.md`](examples/url-shortener/ACCEPTANCE_TEST_PLAN.md)):
  Phase 0 (bootstrap + preflight: manifest validate, lint smoke, state
  detection, API auth) → Phase 1.1 (happy-path BRD→IPLAN cascade with
  autopilot + audit + optional fixer + lint per layer) → Phase 1.2
  (6-fixture negative validation at
  `tests/acceptance/fixtures/negative/`) → Phase 2 (CHG cycle driven by
  per-example `chg/test-change.md`) → Phase 3 (14 utility probes with
  minimum-coverage thresholds preventing empty-output false-PASS) →
  Phase 4 (11 agents + `/aidoc-flow:save-plan` command + deterministic
  `hooks/sdd-doc-review.sh` test).

  Per-run log layout under `examples/<NAME>/logs/<TS>/` with
  human-readable `summary.txt`, machine-readable `summary.json`
  validating against
  `tests/scripts/test-acceptance.schema.json` (v1.0), and per-element
  `.log` + `.meta.json` under `bootstrap/`, `skills/`, `agents/`,
  `command/`, `hook/`, `cascade/`, `negative/`, `sandbox/`.

  `--mock=<run-dir>` replays a prior recorded run without LLM cost for
  script-development iteration. `--promote` archives the previous
  `examples/<NAME>/docs/` to `docs-archive/v<X.Y.Z>/` and replaces it
  with the freshly-produced cascade output; `--push` pushes the promote
  commit. 45-minute hard wall-clock cap. Token cost per `--live` run:
  ~$11–20.

  First example: `examples/url-shortener/` with seed at
  `seed/initial-requirements.md` and CHG change-set at
  `chg/test-change.md` (visit-rate analytics dashboard).

  Six shared negative fixtures at `tests/acceptance/fixtures/negative/`
  exercise structural-defect detection: missing required sections
  (STRUCT01), malformed trace-tags (ID01), non-existent upstream refs,
  low audit-score content, missing required diagrams, broken chain
  traces. 4 of 6 verifiable deterministically; 2 require live LLM.

  Companion parent-repo PR wires `release.yml` to invoke the acceptance
  suite on tag push with `actions/upload-artifact@v4` and raises the
  `T4L` token-ledger ceiling from 500K to 1M.

- **Token-efficient authoring governance** — new
  `framework/governance/AUTHORING_STYLE.md` canonicalises the writing voice
  the SDD corpus expects: elimination list (benefit statements, efficiency
  claims, ease-of-use claims, future-oriented promises, superlatives, filler
  phrases, verbose introductions, redundant restatement), form enforcement
  (imperative verbs for procedures, conditional statements for error
  handling, tables for parameter specs, bullets for options, one-sentence
  element descriptions, ≤ 3-sentence rationale, `@threshold:` keys for
  quantitative values, precise data types), form-preference order
  (table → bullet → diagram → prose), per-section size defaults (≤ 200 words
  or one table/diagram; ≤ 3 000 words for BRD/PRD bodies; ≤ 1 500 for the
  other layers + CHG), and an audit hook (Tier 2 advisory by default,
  promoted to Tier 1 blocking when ≥ 3 banned phrases occur in one section
  or the document exceeds its size target by > 50%). Promoted to canonical
  governance via `DOC_GOVERNANCE_CORE.md` principle 7. Wired into every
  `doc-<layer>` (creation) and `doc-<layer>-audit` skill as an authority
  reference, and into the audit Structural Checklist as the new
  Authoring-style check block. New conformance test
  `tests/conformance/platforms/test_authoring_style_referenced.py` (5
  checks) guarantees the rule cannot be forgotten when new skills land.
  Follow-up TODOs (linter, CHG-family extension, per-section
  `_size_target`, `_guidance` tightening, fixer auto-fix, skill-body
  retrofit) are tracked in `plans/AUTHORING-STYLE-FOLLOWUP.md`.
- **gitleaks** secret-scanning wired into `.pre-commit-config.yaml` (with
  `.gitleaks.toml` allowlisting the `.secrets.baseline`) — a git-aware scan
  alongside the existing `detect-secrets` baseline check. Added a project
  `.yamllint.yaml` config (line-length 120 as a *warning*; tolerate missing
  document-start and non-bool truthy keys common in our templates) and pointed
  the yamllint hook at it (dropping `--strict` so the configured warnings stay
  non-blocking). Tooling-only; no framework spec change.
- **Pre-commit hooks** (`.pre-commit-config.yaml` + a `pre-commit` CI workflow,
  D-0021): hygiene (whitespace/EOF/check-yaml·json·toml/merge/large-files/
  private-key), **ruff** + ruff-format, **bandit** (gated medium+), **markdownlint**,
  **yamllint**, **detect-secrets** (baseline), **pip-audit** (manual/CI stage), and
  a local hook running the conformance suite. Pragmatic rule sets (stylistic
  noise disabled); `legacy/` + Hermes vendored/parsed content excluded. A repo-wide
  autofix + cleanup pass was applied (markdownlint/ruff over ~450 files, plus
  hand-fixed genuine findings) so `pre-commit run --all-files` is green; the stale
  `ucx_hermes` placeholder config was replaced.

## [0.11.0] — Framework Spec — 2026-05-31

### Added

- Tiered test suite for the plugin (`tests/unit`, `tests/acceptance`,
  `tests/packaging`, `tests/release`, `tests/smoke`, `tests/review`).
- `STRUCT01` lint check (missing required template section).
- `sdd_doc_lint --format=json` structured output mode.
- Per-layer + full-path test runners (`scripts/test-layer.sh`, `scripts/test-fullpath.sh`).
- GitHub Actions: PR gate, release gate, nightly live tier, post-deploy smoke.
- Suite documentation: `tests/README.md`, `SCENARIOS.md`, `HOWTO.md`,
  `ENVIRONMENT.md`, `TROUBLESHOOTING.md`, `CONTRIBUTING.md`, per-tier READMEs.
- `tools/bump_version.py` portable VERSION bumper.

### Changed

- 5 stale skills bumped to align with framework spec.
- Plugin (`claude-code-plugin/v0.4.0`) ships a consolidated canonical skill set: **52 skills = 50 active + 2 deprecated stubs**. Hard-deleted 3 redundant skills (`context-analyzer`, `skill-recommender`, `workflow-optimizer`) — folded into `doc-flow`. Deprecated 2 skills (`doc-review`, `trace-check`) — retained as redirect stubs until v0.5.0, folded into `doc-validator`.
- Plugin marketplace + manifest metadata updated for pre-1.0 preview posture (see `platforms/claude-code-plugin/CHANGELOG.md`).
- IPLAN ↔ iplanic integration explicitly deferred — see [`plans/IPLAN-IPLANIC-DEFERRED.md`](plans/IPLAN-IPLANIC-DEFERRED.md).

## [1.1.0] — 2026-05-24

First post-cutover feature release. Tagged `v1.1.0` at the PR #2 merge; bundles
the canonical plugin skill-set revision, the project adaptation overlay (ADAPT),
and the return of change management as the GATE-SPEC framework-spec gate
(CHG-D1) plus its formal governance record (CHG-D2). Framework spec **0.1.0 →
0.3.1**.

### Changed

- **Plugin layer-model migration (PLM).** Migrated the entire Claude Code
  plugin skill corpus (125 skills) from the legacy **12-layer** SDD model to the
  framework's **8-layer** model (BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN), closing
  the layer-model gap noted under [1.0.0] and in `docs/PARITY.md` (the gap was
  far larger than that note implied — 116/142 skills carried legacy
  fingerprints). Renamed `doc-tspec*`→`doc-tdd*` and `doc-tasks*`→`doc-iplan*`;
  retired the legacy SYS/REQ/CTR families (142→125 skills); kept the SPEC- and
  test-subtype families as L6/L7 specialization helpers (decision D-0015);
  realigned every layer number, element ID (now 4-segment `TYPE.NN.SS.xxxx`),
  `framework/layers/` path, downstream/traceability chain, and skill
  cross-reference; removed dead validation-script references. Delivered in
  staged, conformance-gated batches B0–B7 (`plans/PLM-PLAN.md`).

### Added

- **Framework governance decision register (CHG-D2).** New
  `framework/governance/DECISIONS.md` — the spec's own durable home for
  decisions about the spec and its governance. Records the CHG implementation
  model (CHG-D1) as **GD-01**, engine-agnostic; lists D-0013 + D-0019 as pending
  graduation from the migration log. Recording it was itself a GATE-SPEC change
  (framework spec **0.3.0 → 0.3.1**, the first real exercise of the gate).
- **GATE-SPEC — the framework-spec change gate (CHG-D1, D-0020).** Implements
  ROADMAP CHG-D1 — change management as skills + CI/CD, both platforms. Adds the
  *meta* gate that governs changes to the `framework/` spec itself (templates,
  governance, registry, VERSION), orthogonal to the artifact-cascade gates: a new
  `GATE-SPEC_FRAMEWORK.md` definition, a `spec` `change_source` + `semver_impact`
  field, error-catalog/interaction-diagram/CHG-template/README wiring. Wired
  through the plugin CHG skills (`gate-check` runs it; `doc-chg` family routes to
  it) and the Hermes server-side validator (`validation/chg_rules.py`). The
  diff-aware checks (E005 VERSION bump, E008 CHANGELOG) ship as
  `tests/chg/spec_gate.py` + a staged CI workflow; the human-approval half is
  documented as protected-branch review. This **unblocks** `knowledge-extractor`'s
  spec-promotion path. Framework spec **0.2.0 → 0.3.0**.
- **Project adaptation overlay (ADAPT, D-0019).** `framework/governance/ADAPTATION.md`
  - machine-readable `ADAPTATION_SURFACE.yaml` (a closed 4-knob surface:
  `active_layers`, `section_toggles`, `audit_threshold` raise-only, `glossary`),
  the `adapts:` consult-clause across the 35-skill adapting set, and two new
  utility skills — `project-profile` (maintains `.aidoc/profile.yaml`) and
  `knowledge-extractor` (promotes proven local adaptations upward). Framework spec
  **0.1.0 → 0.2.0**.
- Conformance check `tests/conformance/platforms/test_plm_lint.py` (suite now
  **32** tests) — fails if any plugin skill reintroduces a legacy 12-layer
  fingerprint, locking the migration in against regression. *(Suite has since
  grown to 43 with the adaptation-surface and GATE-SPEC guards.)*

## [1.0.0] — 2026-05-21

**Phase 5 — Cutover.** The multi-platform project replaces `main`.
The migration from the pre-migration `ucx_framework` (v0.20.4) is
complete: one engine-agnostic specification (`framework/`) plus two
independent platforms (Hermes MCP server, Claude Code plugin), both
green on the shared conformance suite. The pristine pre-migration
project is preserved on the protected, read-only archive branch
`legacy-ucx-v3.2-read-only`.

> Version scope (P5-T1 Q4): `v1.0.0` is the **project-milestone**
> tag for the cutover — *not* a claim that every component is
> 1.0-stable. `framework/` stays `0.1.0` (no spec change; earns
> `1.0.0` later under the returning CHG governance). The plugin
> stays `0.1.0` (documented layer-model gap, see below). The Hermes
> api_runner fix below ships as the optional `hermes/v0.1.1` patch.

### Removed

- In-tree `legacy/` directory (2276 tracked files, ~645k lines) —
  the pre-migration `ucx_framework` working copy. **Lossless:** the
  full content is preserved byte-for-byte on the protected
  `legacy-ucx-v3.2-read-only` branch (`491e8db`) and in git history.
  (P5-T2)
- Dev-time root `.claude/` loader (240 tracked files) — the
  migration-era Claude Code skills/agents/commands/hooks used to run
  the migration itself. The shipped Claude Code delivery is now the
  **plugin** (`platforms/claude-code-plugin/`), not a root loader.
  **Lossless:** skills/agents/commands are productized in the
  plugin; the pre-migration `.claude/` is on the archive branch; the
  migration-era `.claude/` (incl. the 3 hooks) remains in git
  history. (P5-T3)

### Fixed

- `platforms/hermes/src/mcp_server/executor/api_runner.py` — the
  litellm-missing error told users to `pip install 'ucx_hermes[api]'`;
  corrected to `pip install 'hermes-server[api]'` to match the
  distribution rename in P2-T1 Q1. Resolves the carried known issue
  surfaced at P4-T5 verify. Ships as the optional `hermes/v0.1.1`
  patch (see `platforms/hermes/CHANGELOG.md`).

### Changed

- Project docs finalized for the as-built, post-migration state
  (P5-T4): `README.md` (dropped migration framing + `legacy/` from
  the structure diagram; platform matrix → release tags; added
  archive-branch + PARITY/TAGGING pointers); `docs/REPO_STRUCTURE.md`
  (PLANNED → as-built; legacy mapping reframed as history);
  `docs/PROJECT.md` (§3/§4 cutover reconciled to the archive
  branch); `CLAUDE.md` (rewritten from migration-in-progress memory
  to slim post-migration project memory; root file, survived the
  `.claude/` removal).

### Known carried issues (post-v1.0)

- **Plugin SDD layer-model gap** — the plugin reflects the legacy
  11-layer model and lacks `doc-tdd` + `doc-iplan` (`docs/PARITY.md`
  "Known parity gap"). Content depth, not a correctness issue;
  per-skill content migration tracked as post-v1.0 work. This is why
  the plugin honestly stays `0.1.0`.
- **~150 Class D stale `framework/<X>` references** in plugin skill
  content (P3-T2 G18) — same root cause as the layer-model gap.
- **CI workflows** at `plans/workflows-pending/` await user `git mv`
  into `.github/workflows/` from a local clone (in-container GitHub
  App lacks `workflows` permission).

## [0.5.0] — 2026-05-21

Phase 4 — Conformance & Independence. Platform-conformance tests
(PC1 + PC4) added to the shared suite; greenfield CI workflows
authored; per-platform CHANGELOG retrofits; expanded Hermes README;
repo-root LICENSE; parity report.

### Added

- `tests/conformance/platforms/` sub-package with PC1 (version
  declaration: VERSION + FRAMEWORK_SPEC_VERSION files exist, are
  bare SemVer, match `framework/VERSION`) and PC4 (engine isolation:
  forbidden-token scan scoped to runtime-significant directories
  per platform) test modules. Suite grows **25 → 31 tests**.
- Three greenfield GitHub Actions workflows authored, staged at
  `plans/workflows-pending/` pending user `git mv` to
  `.github/workflows/` (in-container GitHub App lacks `workflows`
  permission — see `docs/TAGGING.md` "In-container push
  restrictions"):
  - `conformance.yml` — runs the 31-test conformance suite on
    every push/PR.
  - `hermes.yml` — runs Hermes' pytest suite (Python 3.12 via
    `actions/setup-python@v5`) on push/PR touching
    `platforms/hermes/**` or `framework/**`.
  - `plugin.yml` — smoke-checks the plugin: manifest valid +
    coupling sweep + structural sanity on push/PR touching
    `platforms/claude-code-plugin/**`.
  All `ubuntu-latest`; concurrency cancel-in-progress; minimal
  `contents: read` permissions. No carry-over from
  `legacy/github-workflows-disabled/` (28 workflows, all
  self-hosted-coupled).
- `platforms/hermes/CHANGELOG.md` — Hermes `[0.1.0]` mirroring
  project `[0.3.0]` scoped content. Cross-references project-level
  CHANGELOG and `plans/P2-T*-PLAN.md` for the full audit trail.
- `platforms/claude-code-plugin/CHANGELOG.md` — plugin `[0.1.0]`
  mirroring project `[0.4.0]` scoped content, with a "Known
  limitations" section flagging the legacy-vs-new SDD layer model
  gap.
- `LICENSE` at repo root — MIT, copyright `vladm3105` (matches
  plugin manifest's `"license": "MIT"` placeholder).
- `docs/PARITY.md` — 5-section capability comparison between
  Hermes and the Claude Code plugin: capability matrix (8 SDD
  layers × 2 platforms); workflow operations; platform-specific
  extras; known parity gap (plugin reflects the legacy 11-layer
  model; lacks `doc-tdd` + `doc-iplan`); user-facing
  "choosing between" decision table.
- `docs/STARTUP_HANDOFF.md` — distills business / startup ideas
  from the migration session (IPLAN-as-product, corpus, domain
  profiles, CHG governance-as-code, etc.) for a future strategy
  session. Separate from the technical migration scope.
- Per-task plans `plans/P4-T0..T5-PLAN.md`, the design doc
  `plans/P4-T1-DESIGN.md`, the audit `plans/P4-AUDIT-conformance.md`,
  and the verify record `plans/P4-T5-VERIFY.md`.

### Changed

- `tests/conformance/_spec.py` — extended **additively** with
  platform helpers (`PLATFORMS_ROOT`, `platform_dirs`,
  `platform_version_file`, `platform_framework_spec_version_file`,
  `framework_version`). Existing helpers + imports untouched.
- `platforms/hermes/README.md` — expanded from 27-line Phase-0
  placeholder to 113-line user-facing doc. Full mirror of P3-T3's
  populated plugin README structure: inventory table, install +
  `.mcp.json` snippet, MCP tool list, framework spec conformance
  section, platform info table, relationship-to-plugin section.
- `docs/TAGGING.md` — appended "In-container push restrictions"
  section documenting the two operation classes that need the
  local-clone workaround (`refs/tags/*` — 4 occurrences after
  P4-T5; `.github/workflows/**` — 1 occurrence). Symmetric with
  the existing tag-push reference.

### Known carried issues (deferred)

- **CI workflow files** at `plans/workflows-pending/` — user
  `git mv`'s them into `.github/workflows/` from a local clone.
  Phase 4 closed without that user action; the relocation is a
  transit detail, not a content gap.
- **Plugin legacy-vs-new SDD layer model gap** (P3-T1 §Deferred
  R2 / `docs/PARITY.md` "Known parity gap"). Plugin lacks
  `doc-tdd` + `doc-iplan`; has `doc-sys` / `doc-req` / `doc-ctr` /
  `doc-tspec` / `doc-tasks` from the legacy 11-layer model.
  Hermes covers all 8 new-model layers via its generic `sdd_*`
  tools. Resolution is a per-skill content-migration task tracked
  as post-v1.0 cleanup.
- **`platforms/hermes/src/mcp_server/executor/api_runner.py:115`**
  carries a stale install instruction
  (`pip install 'ucx_hermes[api]'`); current distribution is
  `hermes-server` (P2-T1 Q1). 1-line fix; deferred to Phase 5
  housekeeping or a `hermes/v0.1.1` patch.
- **~150 Class D stale `framework/<X>` references** in plugin
  skill content (P3-T2 G18) — same root cause as the layer model
  gap; resolution post-v1.0.

## [0.4.0] — 2026-05-20

Phase 3 — Platform B: Claude Code plugin. `platforms/claude-code-plugin/`
ships the 142-skill SDD engine as a native Claude Code plugin (no MCP
backend), consumes `framework/` at `v0.1.0`, and is released as
`claude-code-plugin/v0.1.0`. The plugin uses Claude Code's
auto-discovery from `skills/`, `agents/`, `commands/` at plugin root —
no explicit registration in the manifest.

### Added

- `platforms/claude-code-plugin/` — the Claude Code plugin platform.
  171 net files (post-cleanup): 142 skill directories (129 `doc-*`
  - 13 SDD-adjacent non-doc), 19 skill-root files (quickrefs +
  set-overview READMEs + `REVIEW_DOCUMENT_STANDARDS.md`), 1 agent
  (`requirements-analyst`), 1 command (`save-plan`), plus 4 new
  top-level files (manifest + 2 VERSION files + populated README).
- `platforms/claude-code-plugin/.claude-plugin/plugin.json` —
  minimal 7-field manifest (`name`, `description`, `version`,
  `license`, `repository`, `homepage`, `keywords`). Plugin name
  `aidoc-flow`; slash-prefix `/aidoc-flow:doc-...`. Author block
  omitted (the in-container `git config user.name` returns the
  session's identity, not the repo owner; the `repository` URL
  handles ownership signaling — matches Hermes pyproject precedent).
- `platforms/claude-code-plugin/VERSION` (`0.1.0`, 6 bytes) and
  `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` (`0.1.0`,
  byte-identical to `framework/VERSION`) — declares the plugin's
  own SemVer + framework-spec conformance per D-0009 / P2-T1 Q2.
- `platforms/claude-code-plugin/README.md` — populated user-facing
  doc (82 lines, from 27-line Phase 0 placeholder): inventory table,
  install pointer, slash-prefix use examples, framework spec
  conformance with VERSION cat output, platform info table,
  Hermes-platform relationship section.
- `plans/P3-T0-PLAN.md` + `plans/P3-AUDIT-claude-code-plugin.md` —
  Phase 3 audit (191-file `.claude/` inventory; copy-with-divergence
  relationship resolved) and task breakdown.
- Per-task plans `plans/P3-T1..T5-PLAN.md`, each with the two-pass
  review log mandated by D-0007.
- `plans/P3-T1-DESIGN.md` — 7 plugin design decisions resolved
  before any content moved (manifest schema verified via the
  `claude-code-guide` agent — Claude Code auto-discovers,
  no explicit registration block; plugin name `aidoc-flow`; copy
  strategy is the 3-stage `cp -r` + `rm -rf` recipe; no lifecycle
  hooks in `v0.1.0`).
- `plans/P3-T4-VERIFY.md` — formal Phase 3 verify record covering
  22 gates (conformance 25/25, plugin structure, coupling sweep,
  manifest validity, integration checks).

### Changed

- Rewrote all `ai_dev_flow` placeholder paths in the ported skill
  content to point at `framework/` — 211 line hits across 30 files
  cleared via word-boundary regex sed (P2-T7 G12). Class B (5 layer
  dirs → `framework/layers/0X_TYPE/`) and Class C
  (`ID_NAMING_STANDARDS.md` → `framework/governance/`) sub-path
  corrections applied. 2 illustration `/opt/data/...` paths
  preserved per the P2-T7 G13 historical-vs-current rule.
- `project-mngt/SKILL.md` — the one current-behavior
  `/opt/data/ucx_framework/...` reference rewired to repo-relative
  `framework/governance/ID_NAMING_STANDARDS.md`.

### Removed

- 7 non-SDD-adjacent skill directories excluded from the plugin
  port: `code-review`, `refactor-flow`, `analytics-flow`,
  `devops-flow`, `ai-pr-review`, `google-adk`, `n8n` (P3-T1 Q2 —
  general-purpose, not coupled to any SDD artifact). Source
  `.claude/skills/` retains them; they remain available in dev-time
  use until Phase 5 cutover.
- 3 `.claude/skills/` root files excluded from the plugin port:
  `README.md` (referenced an obsolete multi-project symlink pattern
  and the legacy `ucx_framework/.claude/skills/` canonical path),
  `google-adk_quickref.md`, `n8n_quickref.md` (parent skills out).
- **47 broken symlinks** the source `.claude/skills/` carried via
  `cp -r` into the plugin — self-referencing pointers at
  `/opt/data/docs_flow_framework/.claude/skills/<name>`, leftovers
  from the old multi-project symlink consumption pattern. Removed
  in-flight during P3-T4 verify (G18 finding) via `xargs git rm`
  on the 47 symlink entries.

### Carried known issue (deferred)

- The ~150 Class D stale `framework/<X>` references in the ported
  skills point at concepts not in the current 8-layer framework
  (`framework/scripts/`, legacy 11-layer numbering,
  legacy alpha-named dirs, legacy top-level guides). Resolution is
  a per-skill content-migration task outside Phase 3 scope (P3-T1
  §Deferred R2). The plugin works as a Claude Code artifact
  regardless — the references are documentation hygiene, not
  runtime correctness.

## [0.3.0] — 2026-05-20

Phase 2 — Platform A: Hermes Re-homing. `platforms/hermes/` is fully
assembled, consumes `framework/` at `v0.1.0`, and ships its own first
release as `hermes/v0.1.0`. The MCP server's scaffold + validation
runtime now reads layer templates from `framework/layers/<NN>_<X>/`
per D-0013, closing the platform-template duplication.

### Added

- `docs/TAGGING.md` — the full git-tag policy: release tags (`vX.Y.Z`,
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`) and `mark/<slug>` bookmark tags,
  with create / push / find commands (D-0011). `docs/PROJECT.md` §3 slimmed
  to a summary that links it.
- `ROADMAP.md` "Post-v1.0 — Planned Capabilities" — the domain-profile
  mechanism for generalizing the IPLAN beyond software (D-0012).
- `platforms/hermes/` — the Hermes MCP server platform. 437 net files
  ported and rewired across four sub-tasks: 64 verbatim (P2-T2 —
  `examples/`, `prompts/`, `skills/layer_aliases/`, `skills/personas/`,
  `skills/persona_mappings.yaml`); 200 port-with-repoint (P2-T3 —
  `pyproject.toml`, `src/`, `tests/`, `docs/` less `migration/`,
  `skills/README.md`, `skills/hermes/`); 181 agent-skills from `main`
  (P2-T7 — `agent-skills/spec-driven-development/{sdd-orchestrator,
  sdd-review-personas}/`); minus 8 dropped (P2-T8 — drifted layer
  templates that D-0013 obsoleted).
- `platforms/hermes/VERSION` (`0.1.0`) and
  `platforms/hermes/FRAMEWORK_SPEC_VERSION` (`0.1.0`, matching
  `framework/VERSION`) — declares Hermes' own SemVer + the framework
  spec version it conforms to (D-0009 mechanism, P2-T1 Q2).
- `platforms/hermes/pyproject.toml` keys: `name = "hermes-server"`
  (P2-T1 Q1) at `version = "0.1.0"`; `[project.scripts]
  hermes-mcp = "mcp_server.server:main_sync"` (P2-T1 Q4). Distribution
  name distinguishes the project; the `mcp_server` import path is
  preserved (no Platform B Python collision; P2-T1 Q1 rationale).
- `plans/P2-T0-PLAN.md` + `plans/P2-AUDIT-hermes.md` — the Phase 2
  audit (280-file Hermes tree classified port-verbatim / port-with-
  repoint / drop) and the per-task breakdown (T0..T9).
- Per-task plans `plans/P2-T1..T9-PLAN.md`, each with the two-pass
  review log mandated by D-0007.
- `plans/P2-T5-VERIFY.md` — the formal Phase 2 verify record covering
  14 gates (conformance 25/25, Hermes own suite 447/447, coupling
  sweep, version files, smoke test, structure, file inventory).
- `plans/DECISIONS.md` D-0013 — single-source-of-truth for layer
  templates: platforms consume `framework/layers/`, never duplicate.

### Changed

- Recorded the framework's purpose — the IPLAN as the terminal product;
  code/deploy out of scope; v1 scope is software/devops (D-0012).
- Refined D-0012: the IPLAN has a planned and an executed state with
  criticality-scaled audit depth (R1); the curated corpus of proven IPLANs —
  with composition and freshness — is the unit of value and the post-v1.0
  strategic destination (R2).
- Rewrote all `ucx_flow_v3` runtime coupling to point at `framework/`:
  18 files in the edit set (4 code + 3 tests + 5 skills + 6 architecture/
  spec docs), with sub-path repoints to `framework/registry/` and
  `framework/layers/<NN>_<X>/` (P2-T3). 11 historical-context docs
  (CHANGELOGs, ROADMAP retrospective, completed PLAN-* checklists)
  preserved verbatim per the G13 lesson — rewriting them would falsify
  history.
- Rewired the MCP server's scaffold runtime to consume the framework's
  per-layer layout (P2-T9). Five spots across three files closed the
  D-0013 architectural gap that P2-T3 first surfaced: removed the
  `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`, rewrote
  `_default_ssd_root` to return `framework/layers`, corrected
  `_default_repo_root` parents count (`[4]→[5]` — layout shifted in
  P2-T3), and rewrote `validation/runner.py:_resolve_canonical_template_root`
  as a 3-stage precedence chain (project framework override → scaffold
  output → canonical). Hermes' own test suite went 397/447 → **447/447**.
- Rewrote the skill's template-loading prose (P2-T8): 25 references in
  `agent-skills/.../sdd-orchestrator/SKILL.md` +
  `references/sdd-workflow-quickstart.md` rewired from skill-relative
  `templates/0N_TYPE-TEMPLATE.yaml` to framework-relative
  `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`; the `skill_view` API
  example was rewritten as a direct-read instruction since templates
  now live outside the skill.
- `.mcp.json` cwd repointed from `legacy/ucx_hermes/src` to
  `platforms/hermes/src` (P2-T3).
- `plans/P2-AUDIT-hermes.md` refreshed with §3a extension (3 test
  files added to the code-level coupling list) and §3c (new section —
  "Documentation cluster — historical vs current") to record audit
  gaps discovered during P2-T3 planning.

### Removed

- The 8 drifted layer template YAMLs at `platforms/hermes/agent-skills/
  spec-driven-development/sdd-orchestrator/templates/` (P2-T8). They
  carried engine hardcodes (`server: ucx_hermes`, `tool: sdd_validate`,
  `SDD v3` labels, vendor-named agent placeholders) that D-0013
  excluded from documents. The framework `framework/layers/<NN>_<X>/
  <X>-TEMPLATE.yaml` set is the single source of truth.
- 6 D-0013-obsolete sync files from the agent-skills package (P2-T7):
  `sync-ucx-templates.sh`, `sync.py`, `.sync-backlog.json`,
  `template-sync-procedure.md`, `template-v3-alignment-checklist.md`,
  `ucx-framework-quirks.md`. There is no longer anything to sync —
  Hermes consumes `framework/layers/` directly.
- The `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS` (P2-T9) and
  the no-op `exists()` branch in `_default_ssd_root` — both dead code
  after D-0013.
- `legacy/ucx_hermes/docs/migration/MIGRATION_FROM_MCP_UCX.md` from the
  port set (P2-T3) — `mcp_ucx/` is the deprecated predecessor, archived
  in `legacy/` and slated for full removal at Phase 5 cutover.

## [0.2.0] — 2026-05-19

Phase 1 — Framework Spec Extraction. `framework/` is fully assembled and
guarded by a 25-test conformance suite. Framework spec released as
`framework/v0.1.0`.

### Added

- Plan-review gate (D-0007): plans require a `## Review log` of ≥2 passes;
  `plans/PLAN-TEMPLATE.md` added; non-blocking `PreToolUse(git commit)` hook
  warns when a staged plan file falls short.
- `plans/P1-AUDIT-ucx_flow_v3.md` — Phase 1 audit (P1-T1) classifying the
  49-file legacy SDD tree as engine-agnostic, mixed, instance, or drop, with
  the target `framework/` layout for the Phase 1 extraction steps.
- `framework/layers/` (P1-T2) — the 8 engine-agnostic SDD layer specs
  extracted from `legacy/ucx_flow_v3/`: per layer a `*-TEMPLATE.yaml`, a
  `README.md`, and a `*-00_index.TEMPLATE.*` index template (24 files). All
  Hermes/MCP- and Claude-Code-specific content removed; legacy version
  strings neutralized.
- `framework/registry/` (P1-T3) — `LAYER_REGISTRY.yaml`, the authoritative
  machine-readable layer model (layer order, traceability graph, C4 mapping,
  ID patterns), plus a `README.md`. Standalone version field and legacy
  changelog dropped; layer `folder` paths repointed under `layers/`.
- `framework/governance/` (P1-T4) — 5 governance docs (`DOC_GOVERNANCE_CORE`,
  `ID_NAMING_STANDARDS`, `TRACEABILITY`, `DIAGRAM_STANDARDS`,
  `THRESHOLD_NAMING_RULES`) and the CHG overlay (`chg/` — README, template,
  index template, 7 gates, 2 companion templates), 18 files. Engine-specific
  skill references and `MCP` mentions neutralized; CHG extracted spec-only
  (not enforced until post-Phase 5).
- `tests/conformance/` (P1-T5) — the shared conformance suite: stdlib
  `unittest` tests covering registry self-consistency, layer templates,
  governance files, the framework root, `VERSION`, and spec hygiene (no engine
  tokens in `framework/`), plus the documented platform-conformance contract
  for Phase 4. No `pytest` dependency (D-0008).
- `framework/README.md` — the engine-agnostic spec overview (8-layer flow, C4
  alignment, layout, conformance, versioning), replacing the scaffolding
  placeholder.
- `framework/VERSION` (P1-T6) — the framework spec's independent version
  stream, at `0.1.0`.
- `docs/PROJECT.md` §3 — tag-namespace convention: project milestones
  `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms `<platform>/vX.Y.Z`
  (D-0009).
- `framework/` root methodology docs (P1-T7) — `SPEC_DRIVEN_DEVELOPMENT_GUIDE`,
  `QUICK_REFERENCE`, `AI_ASSISTANT_RULES`, `TESTING_STRATEGY_TDD`, extracted
  engine-neutral (version strings neutralized, links repointed, legacy
  version-lineage content dropped per D-0010).

### Changed

- **Legacy isolation (P1-T0):** all pre-migration content moved into `legacy/`
  (frozen) — `ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`, `ai_dev_ssd_flow_v2`,
  `governance`, and supporting trees. Repo root now holds only the new
  project (`framework/`, `platforms/`, `docs/`) plus infrastructure.
- Legacy GitHub Actions workflows disabled (parked in
  `legacy/github-workflows-disabled/`).
- Root `README.md` rewritten for the multi-platform project.
- `.mcp.json` Hermes server path repointed to `legacy/ucx_hermes/`.

## [0.1.0] — 2026-05-18

Phase 0 — Planning & Scaffolding. The migration baseline.

### Added

- Planning baseline for the multi-platform restructure:
  - `ROADMAP.md` — phased delivery plan (Phase 0 → cutover v1.0.0).
  - `docs/REPO_STRUCTURE.md` — target repository layout and legacy mapping.
  - `docs/PROJECT.md` — versioning, branching, milestones, conformance, and
    interim change-management policy.
  - `platforms/hermes/` and `platforms/claude-code-plugin/` directories.
  - `framework/` directory placeholder for the shared engine-agnostic spec.
- CHG implementation decision recorded as tracked TODO (ROADMAP CHG-D1/D2,
  `docs/PROJECT.md` § CHG implementation model): CHG to be built as
  skills + CI/CD post-Phase 5.
- `CLAUDE.md` — auto-loaded project memory: development workflow
  (plan → review → harden → implement → verify → land), definition of done,
  and session-handoff practice.
- `plans/` workspace — `README.md`, `MIGRATION_TODO.md` (live task tracker),
  `HANDOFF.md` (session continuity), `DECISIONS.md` (decision log).
- `.claude/` automation hooks: `PreCompact` (auto-commit + push a WIP
  snapshot before compaction) and `SessionStart` (inject `plans/HANDOFF.md`
  into context), with scripts under `.claude/hooks/`.

### Notes

- Forked from `ucx_framework` v0.20.4 (`main`).
- The gated CHG change-management process is intentionally not applied during
  the migration; it is re-introduced post-cutover (see `docs/PROJECT.md`).

[Unreleased]: https://github.com/vladm3105/aidoc-flow-framework/tree/claude/multi-platform-migration-AamWB
[0.2.0]: https://github.com/vladm3105/aidoc-flow-framework/releases/tag/v0.2.0
[0.1.0]: https://github.com/vladm3105/aidoc-flow-framework/releases/tag/v0.1.0
