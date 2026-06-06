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

These five fixes are part of the same v0.6.1 release; no separate
amendment PR.

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
