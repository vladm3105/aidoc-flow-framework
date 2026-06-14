# Decision Log

Non-obvious decisions made during the migration, with rationale, so the "why"
survives across ephemeral sessions. Newest first. Timestamps are ISO 8601 UTC.

Decisions that affect the **shared spec** graduate into the spec's own register,
`framework/governance/DECISIONS.md` (established by CHG-D2). D-0020 (CHG-D1) is
graduated there as **GD-01**; D-0013 and D-0019 are listed there as pending
graduation.

---

## D-0033 — Claude Code plugin user-facing commands: shape, channels, and honesty boundaries (PLUGIN-USER-COMMANDS)

- **Date:** 2026-06-14T00:00:00Z
- **Plan:** `plans/PLUGIN-USER-COMMANDS-PLAN.md` (merged via PR #142, plan-only;
  this PR delivers the implementation).
- **SemVer impact:** Plugin MINOR `0.18.0 → 0.19.0`.

Three sub-decisions, captured here so future contributors do not relitigate
them when extending the command surface.

### D-0033a — `/feedback` lands in GitHub Issues, not Discussions

Issues + a dedicated `.github/ISSUE_TEMPLATE/feedback.md` template covers the
v1 need (separate triage from bug reports, single backend that the maintainer
already monitors). Discussions adds setup overhead and a second moderation
surface for a channel that is empty today. Migration path: switching `/feedback`
to Discussions later is a one-URL change in `commands/feedback.md`; deferred
backlog only, no design debt.

### D-0033b — Split `/budget` and `/model` rather than ship a single `/performance`

A single command would collapse two orthogonal axes into one slider:
*cognitive depth* (which model the user runs against) and *effort the skill
spends* (how many passes, how verbose). Users genuinely want the four
combinations (Opus + min for high-stakes terse work; Haiku + max for
stress-tests; etc.). The split also makes each command's caveat sharper —
budget is a behavior knob, model is advisory — versus a single command that
would have to hedge both.

### D-0033c — Advisory-not-enforcing posture for `/model` and `/budget`

The plugin layer **cannot**:

- switch the Claude Code session model (only the native `/model <id>` does),
- enforce a hard token cap (no token-meter hook is available to plugins),
- remove itself (only the native `/plugin uninstall` does).

Rather than hide these limits or imply enforcement that doesn't exist, the
command prose names them explicitly. `/aidoc-flow:model` prints copy-paste
native `/model <id>` commands; `/aidoc-flow:budget` documents the empirical
40–60% token reduction `min` profile delivers via skipped passes; `/aidoc-flow:uninstall`
prints the exact native uninstall command and never claims to run it. The
honesty is verified by conformance test V5 (`grep -F "advisory" commands/model.md`).

---

## D-0032 — Unified development/work plan standard in the IPLAN layer (PLANSTD-001)

- **Date:** 2026-06-09T00:00:00Z
- **Decision:** Anchor a single, flexible development/work plan template to a
  normative spec doc at `framework/layers/08_IPLAN/PLAN_STANDARD.md`, and
  rewrite `plans/PLAN-TEMPLATE.md` to conform. The standard:
  - **(placement, D-PLANSTD-1)** lives in `08_IPLAN` as a **third, orthogonal**
    concept governing markdown `plans/*.md` dev/work plans — explicitly distinct
    from BOTH the Permanent per-SPEC `IPLAN-NN_{slug}.yaml` and the Temporary
    `tmp/TMP-IPLAN-*.yaml`. Neither YAML artifact changes; the IPLAN `README.md`
    cross-link is load-bearing for the layer's conceptual coherence.
  - **(flexibility, D-PLANSTD-2)** expresses section applicability via inline
    `[REQUIRED]` / `[CODE]` / `[IF APPLICABLE]` tags plus an applicability
    matrix over the confirmed work-type set `feature` / `bugfix` /
    `documentation` / `refactor` / `chore`; the agent keeps applicable chapters
    and deletes the rest (no `N/A` stubs).
  - **(engine-agnostic, D-PLANSTD-3)** carries no engine tokens and no literal
    version string (passes `test_spec_hygiene.py`).
  - **(verification, D-PLANSTD-4)** is `[REQUIRED]` for every work type; only
    the kind varies (runnable commands for code; lint/link/render/review for
    documentation).
  - **(versioning, D-PLANSTD-5)** bumps `framework/VERSION` MINOR
    (`0.14.3 → 0.15.0`, forced by GATE-SPEC-E005); re-matches both
    `FRAMEWORK_SPEC_VERSION` pointers; leaves plugin + Hermes **product**
    versions unchanged (independent streams, `docs/PROJECT.md` §2).
- **Why:** The prior `plans/PLAN-TEMPLATE.md` was thin and migration-flavored;
  real plans in this repo had outgrown it (File-structure / `### Task N` /
  Claim-ledger / Review-log sections absent from the template). One standard,
  reused across repos, replaces ad-hoc plan shapes. Full design, claim ledger,
  and 6-pass review trail in `plans/PLANSTD-001-PLAN.md` (PR #114).

## D-0031 — Promote the review-saga lifecycle into the framework spec (supersedes D-0005's scope)

- **Date:** 2026-06-05T13:00:00Z
- **Decision:** Promote the review-team saga lifecycle (state machine,
  transitions, journal schema, compensation events, break-circuit policy)
  from a Hermes-internal implementation detail to an engine-agnostic
  framework-spec contract at `framework/governance/REVIEW_SAGA.md` +
  `framework/governance/saga.schema.json`. Both platforms (Hermes Python
  runtime and Claude Code plugin via SKILL prompts + saga.json + Bash
  subprocesses) implement the same observable lifecycle. Framework spec
  bumps `0.12.0 → 0.13.0` (CHG-gated).
- **Why:** Two converging pressures:
  1. **New failure-class evidence.** D-0005 (2026-05-26) decided "no saga
     in plugin" on the premise that "there is nothing to journal" — the
     plugin's Task subagents are harness-managed and the blackboard +
     coverage/quorum handles partial-crew state. The 2026-06-05 live BRD
     verification (CHAOS-SEC-SPLIT-001, D-0030) revealed a failure class
     D-0005 did not contemplate: **partial outer-loop state** when
     `doc-brd-autopilot` times out mid-iteration with a 5-lens crew +
     multi-lens fixer validation. Concrete evidence:
     `examples/url-shortener/logs/2026-06-05T103311/elements/doc-brd-autopilot.log`
     shows `outcome: FAIL`, `duration_sec: 1802.0`, `error: claude -p exit
     124`, and no saga journal produced. The dual-dispatch path
     (acceptance script's standalone audit → fixer → re-audit) succeeded
     at total runtime 3535s — proof that the create→review→revise loop
     *did* have intermediate state worth preserving across phase
     boundaries, but the plugin had no place to durably record it.
     D-0005's "nothing to journal" assertion is factually incomplete: at
     the outer-loop level (phase progression, iteration count,
     transitions between phases) there *is* something to journal. The
     blackboard captured per-lens slot state correctly; what was missing
     was per-phase state.
  2. **Lifecycle-behavior parity requirement.** The project's parity goal
     is now lifecycle-behavior parity (per `docs/PARITY.md`), not just
     output-shape parity. Achieving it requires both platforms to expose
     the same observable saga lifecycle. The framework spec is the only
     durable place to define that lifecycle without locking platforms
     into a single implementation.
- **Supersession scope:** D-0031 **supersedes D-0005's scope-narrowing
  premise** ("the plugin needs no saga"), NOT D-0005's reasoning about
  partial-crew state. The blackboard remains the durable medium for
  per-lens slot state; D-0031 adds a parallel saga.json journal for
  outer-loop phase state. D-0005's text is preserved verbatim with a
  trailing pointer to D-0031.
- **Notes:** Adopts Hermes' existing state names + transitions verbatim
  (PREPARED, FANOUT_STARTED, BRANCH_RUNNING, etc.) as the spec source —
  cheaper than renaming a working implementation; the names are general,
  not Hermes-coined. Adds `PARTIAL_TIMEOUT` as the only new state
  (covers break-circuit + SIGTERM cases on both platforms). Adds a
  top-level `transitions: list[dict]` field that Hermes does not have
  today; Phase 3 of SAGA-PARITY-001 adds it to Hermes' `SagaRunState`.
  The plugin implementation is cooperative (LLM honors the contract);
  Hermes' is preemptive (Python runtime enforces). Same observable
  lifecycle, different enforcement — documented as a known platform
  asymmetry in REVIEW_SAGA.md.
- **Implementation:** SAGA-PARITY-001 plan (`plans/SAGA-PARITY-001-PLAN.md`)
  organizes 4 phases. This decision lands in Phase 1
  (`plans/SAGA-PARITY-001-PHASE-1-PLAN.md`). Phases 2-4 implement the
  contract on each platform.

---

## D-0030 — Partition `adversary` lens into `chaos_engineer` + `security_engineer`

- **Date:** 2026-06-05T10:00:00Z
- **PR:** CHAOS-SEC-SPLIT-001 (plan: `plans/CHAOS-SEC-SPLIT-001-PLAN.md`,
  merged PR #78; impl: this PR).
- **Decision:** Split the single `adversary` review-lens into two
  narrowly-scoped lenses aligned with intent — `chaos_engineer` (internal
  stability: failure paths, edge cases, race conditions, resource
  exhaustion, recovery) and `security_engineer` (external threats: trust
  boundaries, abuse cases, missing authn/authz/integrity controls,
  attack surface). Promote `agents/security-engineer.md` from transitive
  auditor sub-role to first-class crew lens; rename
  `agents/adversary.md` → `agents/chaos-engineer.md`. Per-layer crew
  weights redistributed in `REVIEW_CREWS.yaml` across 8 crews (all sums
  still 100). Plugin SemVer-major 0.4.5 → 0.5.0 (BREAKING — slot
  filenames change).
- **Why:** The single `adversary` lens conflated two structurally
  different review intents — what breaks the system *by accident*
  (chaos engineering) vs what an actor exploits *on purpose* (external
  threat modeling). Even the agent's own description called itself
  "devil's-advocate / chaos lens" while explicitly deferring half its
  scope ("deep security") to the `security_engineer` agent — which
  itself existed but wasn't a crew lens. Splitting gives: (a)
  traceable findings (verdict.json's `lens_scores` exposes which axis
  is failing), (b) targeted fixer dispatch (chaos validates with stress
  scenarios; security validates with threat models), (c) focused
  persona prompts instead of the 5-bucket grab-bag that deferred half
  its own scope.
- **Weight allocation method** (codified in `REVIEW_TEAM.md` §"Weight
  allocation rules"): chaos-heavy at BRD/EARS/BDD (reliability NFRs +
  failure scenarios dominate); security-heavy at ADR (architectural
  decisions encode trust boundaries); equal split at PRD/SPEC/TDD;
  chaos-only at IPLAN (security lives upstream in ADR/SPEC). Author and
  auditor weights untouched (auditor's "+security" sub-role moves out
  to the dedicated security_engineer lens).
- **Rationale propagation** — five places (REVIEW_CREWS.yaml comments,
  REVIEW_TEAM.md §Weight allocation rules, agent briefs' per-layer
  tables, audit-skill pseudo-text, CHANGELOG). Single source of truth
  is REVIEW_CREWS.yaml; conformance test enforces drift detection.
- **Hermes platform** (separate PR) already uses `chaos_engineer` as
  its internal runtime persona name with a translation layer back to
  framework's `adversary`. This spec change removes the translation;
  Hermes' migration is dropping the translation + adding the new
  `security_engineer` lens.

---

## D-0028 — One ORCHESTRATOR_TIMEOUT for every sub-team-dispatching skill

- **Date:** 2026-06-04T21:50:00Z
- **Context:** Three separate live re-verifications across BRD-RT-001 →
  002 → 003 revealed the same operational gap iteratively: any skill
  that internally dispatches a sub-team in team mode needs more than
  the default 600s `SKILL_TIMEOUT`. Each PR fixed one skill type at a
  time:
  - BRD-RT-002 (D-0026): `AUDIT_TIMEOUT=1200` for `doc-*-audit`
  - BRD-RT-003 (D-0027): `AUTOPILOT_TIMEOUT=1800` for `doc-*-autopilot`
  - BRD-RT-003 live re-verify exposed **G15**: `doc-*-fixer` also
    times out — same pattern, third skill class. Adding
    `FIXER_TIMEOUT` would have continued the per-skill-type
    proliferation.
- **Decision:** Generalise the three separate timeout variables into
  a single **`ORCHESTRATOR_TIMEOUT=1800s`** applied uniformly to every
  skill that dispatches a sub-team in team mode. Identified by name
  pattern in `tests/scripts/test-acceptance.sh:_pick_timeout_for`:
    `review-team` ∨ `doc-*-audit` ∨ `doc-*-autopilot` ∨ `doc-*-fixer`
  The globs are **anchored to the `doc-*-` prefix** (not bare
  `*-audit` etc.) so non-orchestrator utility skills with similar
  suffixes — notably `security-audit`, a single-pass leaf skill —
  keep the default `SKILL_TIMEOUT`. Inspection-confirmed: the
  intended set is exactly the 9 layer + CHG skills per pattern
  (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN/CHG × 3 operations + 1
  `review-team` = 28 orchestrator skills total).
  Leaf skills (no sub-team dispatch) keep the 600s `SKILL_TIMEOUT`.
  Phase 4.1 agents keep `AGENT_TIMEOUT=600s`. The per-layer outer cap
  (`MAX_LAYER_SEC=3600s`, from BRD-RT-003) remains as the wall-clock
  guard for cascades.
- **Why:**
  - **One concept, one knob.** All three orchestrator skills do the
    same kind of work (Task fan-out + synthesizer). They deserve the
    same budget. Live evidence: audit ~580-900s, autopilot ~1200-1500s,
    fixer ~500-700s. 1800s comfortably covers each.
  - **Pattern matches the architecture.** REVIEW_TEAM.md frames these
    as "operations on the blackboard" (Review, Create, Remediate).
    The plugin's binding has three skill types implementing those
    operations; they share orchestration shape, they should share
    timeout policy.
  - **Future-proofs PRD..IPLAN.** When PRD-RT-001 etc. propagate, the
    name-match catches their `doc-prd-audit` / `doc-prd-fixer` /
    `doc-prd-autopilot` automatically. No per-layer config changes
    needed.
  - **Closes G15** without adding another per-type variable. The
    iterative timeout-extension pattern (BRD-RT-002 → 003 → 004)
    stops here.
- **Scope:** Plugin v0.4.4 → v0.4.5. Framework spec unchanged. Three
  env vars removed (`AUDIT_TIMEOUT`, `AUTOPILOT_TIMEOUT`,
  `REVIEW_TEAM_TIMEOUT`); one introduced (`ORCHESTRATOR_TIMEOUT`).
  The change is backward-compat at the script's command-line surface:
  no flags or args change, only internal variable names. Operators
  who set these env vars externally need to migrate; live grep
  confirms no CI config references them.
- **Notes:** This is the architectural endpoint of the
  audit→autopilot→fixer timeout sequence. After BRD-RT-004,
  per-layer follow-ups land without inheriting any timeout-shape
  gaps — they only need the same name-pattern in their layer's
  SKILL.md text. The next BRD-RT verification run is expected to
  reach 6/6 pass criteria.

## D-0027 — Autopilot timeout matches its sub-team orchestration; multi-lens fixer findings dispatch all responsible lenses

- **Date:** 2026-06-04T13:30:00Z
- **Context:** BRD-RT-002's live verification (2026-06-04) produced 4 of
  6 pass criteria on the team-mode run. The 2 FAILs were operational —
  the architectural contract (verdict.json + cross-consumer consistency)
  verified end-to-end. Three gaps:
  - **G11**: `doc-brd-autopilot` in team mode now orchestrates a full
    `create → review → revise` loop inside one outer `claude -p`
    process. The default 600s `SKILL_TIMEOUT` killed it mid-iteration
    (exit 124). BRD-RT-002's `AUDIT_TIMEOUT=1200` name-match only
    covered `*-audit`.
  - **G12**: even with G11 fixed, a multi-iteration fix cycle (3 ×
    ~25 min) pushes a single layer's wall-clock past the 1800s
    per-layer cap.
  - **G13**: BRD-RT-001's fixer SKILL text said "dispatch *the*
    responsible lens" (singular). When a finding's `personas` array
    listed 2+ lenses (e.g. `[architect, business_analyst]`), the
    model bailed on lens validation instead of dispatching both.
    Result: fixer ran but wrote no `<persona>.fix_<N>.json` slots,
    leaving the team-mode patch-validation loop unverified.
- **Decision:**
  - Extend `_pick_timeout_for` in `tests/scripts/test-acceptance.sh` to
    match `*-autopilot` skills → new `AUTOPILOT_TIMEOUT=1800` (30 min).
  - Raise `MAX_LAYER_SEC` from 1800s to 3600s. Existing inner
    backstops (per-skill timeouts, `--cost-cap`, framework's
    `MAX_TOTAL_OUTPUT_TOKENS`) remain.
  - Codify `doc-brd-fixer/SKILL.md` Remediate Mode dispatch rules:
    single-lens finding → that lens; multi-lens finding → **all**
    listed lenses in parallel; orphan finding → layer's author lens
    as fallback.
  - Document `findings[].personas` field in `agents/synthesizer.md`
    schema (the synthesizer already writes it; the SKILL catches up).
- **Why:**
  - **G11/G12 are arithmetic.** The autopilot's nested loop has more
    work to do than a single audit, so it needs a longer timeout.
    Per-layer cap matches the worst-case ceiling (3 fix iterations at
    ~20 min each).
  - **G13 is prompt-correctness.** Singular "the responsible lens" is
    ambiguous when 2+ lenses co-own a finding. Explicit branching
    rules let the model dispatch correctly without inferring intent.
  - **Fallback-to-author** keeps every blocking finding validated
    even when synthesizer doesn't populate `personas` — avoiding
    silent skips while preserving lens-independence properties.
- **Scope:** Plugin v0.4.3 → v0.4.4. Framework spec unchanged. The
  fixer pattern + autopilot-timeout name-match are reusable verbatim
  for PRD-RT, EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT —
  per-layer follow-ups inherit the corrected ops.
- **Notes:** Live re-verification (~$7, 25-30 min) is expected to take
  Run #1's pass-criteria from 4/6 to 6/6 on the BRD layer. The
  url-shortener BRD's BA-001 finding (visit-count contradiction, P1
  with `[architect, business_analyst]` personas) is now the live test
  case for multi-lens dispatch.

## D-0026 — Synthesizer writes a structured `verdict.json`; consumers parse JSON, not Markdown

- **Date:** 2026-06-03T18:25:00Z
- **Context:** BRD-RT-001's live verification runs surfaced a critical
  consistency bug: the doc-brd-audit skill's stdout response
  (audit_score: 92, PASS) diverged from the .aidoc/audit/01_BRD-audit.md
  it wrote to disk (Content score: 83, FAIL). Same invocation, two
  verdicts. Every downstream consumer (driver script, autopilot's revise
  loop) read stdout, not the written report — so team-mode FAIL
  verdicts never triggered fixer cycles. The autopilot's create→review→
  revise loop was structurally broken by the wrong source-of-truth
  read.
- **Decision:** The synthesizer subagent writes a flat, deterministic
  `verdict.json` companion alongside `report.md` at
  `.aidoc/review/<NN>_<LAYER>/<artifact-id>/verdict.json`. Every
  downstream verdict consumer — `doc-*-audit` SKILL's stdout response,
  `tests/scripts/test-acceptance.sh:parse_audit_score`, the
  autopilot's revise loop, `doc-*-fixer`'s blocking-findings list —
  reads from this JSON. Markdown `report.md` remains the human
  narrative; it is **never the machine parse target**. When the two
  files disagree, the JSON wins (it is what consumers parse).
- **Why:**
  - **Markdown is fragile.** Heading text, table format, value
    placement can drift between runs. Asking a model to extract values
    from prose shifts fragility from one place to another.
  - **JSON is deterministic.** Schema-checkable, parseable by
    `json.loads()`, and the synthesizer's reduce already produces the
    underlying values per `REVIEW_TEAM.md` §"Synthesis = reduce +
    narrative".
  - **Verdict-chain consistency at every consumer.** With one
    authoritative source (verdict.json), the driver, audit skill,
    autopilot, and fixer cannot disagree about gate state. The
    audit's stdout response mirrors the JSON key-for-key.
  - **Belt-and-suspenders.** Driver script's `parse_audit_score`
    cross-checks stdout against verdict.json; logs a warning and
    prefers JSON on drift. Catches future model-output divergence
    without depending on perfect prompt compliance.
- **Scope:** Plugin v0.4.2 → v0.4.3 binds the new mechanism at the BRD
  layer (BRD-RT-002). Per-layer follow-ups (PRD-RT, EARS-RT, etc.)
  copy the pattern verbatim. No framework spec change — `REVIEW_TEAM.md`
  already specifies the synthesizer's deterministic reduce; this is
  the plugin's binding catching up to the spec.
- **Notes:** The `<BRD-id>` path segment is codified as the **short
  artifact ID** (`BRD-01`), not the nested folder name
  (`BRD-01_url_shortener`) — BRD-RT-001's implementation already chose
  the short form. The `MAX_LAYER_SEC` cap rose 900s → 1800s to fit
  team-mode runs; a new `AUDIT_TIMEOUT=1200s` applies via name-match
  to any `doc-*-audit` skill. The always-on `single_pass` advisory
  note in audit reports is informational; it doesn't change PASS/FAIL
  outcome — projects making the cost-vs-rigor tradeoff via
  `ADAPTATION_SURFACE.yaml` are honored.

## D-0025 — Project profile is a delta, not a snapshot

- **Date:** 2026-06-03T14:14:42Z
- **Context:** In BRD-RT-001 (D-0024), the acceptance suite's profile
  bootstrap copied `framework/governance/REVIEW_CREWS.yaml` byte-for-byte
  into `.aidoc/profile.yaml`. That produced a 60-line file where every
  line was potentially an override or a stale default, with no way to
  distinguish them. Two problems followed: the framework couldn't evolve
  crew/persona defaults without breaking older projects (frozen
  snapshots), and profile readers couldn't tell what was customised.
- **Decision:** Project profiles are **override-only deltas**.
  `framework/governance/PROFILE-TEMPLATE.yaml` is the new bootstrap
  skeleton — a metadata-only file with every adaptation knob commented
  out. Unset keys fall through to framework defaults via the precedence
  chain `framework defaults < user-global seed < project profile`
  documented in `framework/governance/ADAPTATION.md` since v0.11.0.
- **Why:**
  - **Safe framework evolution.** If `REVIEW_CREWS.yaml` re-weights a
    crew in v0.12, existing projects pick up the change automatically —
    no migration required.
  - **Readable profiles.** A reader of `.aidoc/profile.yaml` sees only
    what the project chose to override; framework defaults stay where
    they belong.
  - **Operationalises the spec.** `ADAPTATION.md` already documents the
    precedence chain since the ADAPT work (D-0019); this decision wires
    it into the engine.
  - **Closed-surface conformance.** Out-of-surface keys in a profile
    would be silently ignored by a conforming engine — flagging them as
    a conformance violation is an authoring-mistake guard. New test
    `tests/conformance/platforms/test_profile_schema.py`.
- **Scope:** Plugin v0.4.1 → v0.4.2 binds the new mechanism. Framework
  spec **0.11.2 → 0.11.3** (additive — new template file). No existing
  key removed; every existing profile continues to parse. Backward-compat
  for projects with populated profiles: any present key is honored as an
  override; fallback only kicks in for absent keys.
- **Notes:** A full layered config-merge engine with a user-global seed
  file (the ADAPTATION.md "middle" precedence layer) is deferred until
  the override-only delta proves insufficient — YAGNI for current scale.
  Per-layer review-team wiring beyond BRD will consume the resolved
  profile transparently in PRD-RT-001 etc. The crews/persona definitions
  themselves remain framework-level only (not in the closed adaptation
  surface), so projects can't override the crew composition — they can
  only choose `team` vs `single_pass` and tune thresholds/toggles.

## D-0024 — BRD-layer team-mode dispatcher placement: at `doc-*-audit`, not at a higher orchestrator

- **Date:** 2026-06-03T13:30:51Z
- **Context:** The framework spec
  (`framework/governance/REVIEW_TEAM.md`,
  `framework/governance/REVIEW_CREWS.yaml`) endorses `independent`
  parallel-subagent review as the default mode at gates. The plugin's
  `platforms/claude-code-plugin/skills/review-team/SKILL.md` correctly
  describes Claude Code `Task`-tool fan-out as the mechanism, but the
  per-layer `doc-*-audit` skills did not invoke it — they ran
  single-pass content reviews in one model context. BRD-RT-001 (see
  `plans/BRD-REVIEW-TEAM-PLAN.md`) wires the fan-out at the BRD layer
  as a proof-of-concept; a design decision is needed on **which skill
  owns the dispatcher**.
- **Decision:** The dispatcher of the persona crew lives in
  `doc-<layer>-audit` (for review/gate) and `doc-<layer>-autopilot`
  (for the create→review→revise loop). **Not** in a higher orchestrator
  skill, **not** in `pm-orchestrator`, **not** as a separate
  pre-cascade phase in the acceptance suite.
- **Why:**
  - `review-team/SKILL.md:108` already designates this:
    "`pm-orchestrator` (or the invoking `doc-<layer>-audit`) is the
    dispatcher." This codifies that the audit skill is one valid owner;
    we pick it as **the** owner for per-layer gate-time review.
  - Per-layer dispatch at the gate matches `REVIEW_REMEDIATION_FLOW.md`
    trigger points (`on_gate_fail`, `pre_promotion`, `pre_merge`). A
    chain-wide orchestrator can't catch errors at the per-layer gate
    they originated at — the create→review→revise loop only converges
    when the review happens at the layer being authored.
  - The Phase 3 chain-wide `review-team` invocation in
    `tests/scripts/test-acceptance.sh:1239` continues to exist for
    cross-cutting review across the produced 8-layer chain. The two are
    complementary, not duplicative.
  - Keeping the dispatcher local to the audit skill preserves the
    "structured slots, never peer-to-peer" rule from `REVIEW_TEAM.md`
    §Blackboard — every contract between skills is the slot path +
    persona-output schema, not skill-internal logic.
- **Scope:** This decision is the rule for **every layer**'s team-mode
  wiring. BRD-RT-001 implements it for BRD; PRD-RT, EARS-RT, BDD-RT,
  ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT will copy the pattern verbatim.
- **Notes:** This is a plugin-platform decision; it does not change the
  framework spec. The plugin-spec contract (consume `framework/`
  templates + governance, no platform names in `framework/**`) is
  preserved. Plugin v0.4.0 → v0.4.1.

## D-0023 — Domain & product identity: one brand, path-based per-integration pages

- **Date:** 2026-05-27T00:00:00Z
- **Context:** Three registered domains (`aidoc-flow.com`, `.ai`, `.io`) and an
  open question of how to host the Claude Code plugin's "home" — plus the
  realization that the plugin is **one of a family** of integrations (a Claude
  Code plugin, possibly a Codex plugin, a VS Code extension, …) all consuming the
  one engine-agnostic framework spec, alongside Hermes (the MCP surface).
- **Decision:**
  1. **One canonical brand domain — `aidoc-flow.com`** (company + product +
     marketing). The other TLDs are defensive assets: `aidoc-flow.io` and a
     non-canonical `.ai` **301-redirect** to it.
  2. **Integrations are a category, addressed path-based** — `aidoc-flow.com/claude-code`,
     `/codex`, `/vscode`, `/hermes` (framework docs + install guides under
     `docs.aidoc-flow.com`). **No dedicated domain or top-level subdomain per
     integration** (`claude.`/`plugin.` were rejected — engine-coupling + the
     "Claude" trademark, and there will be several integrations). A subdomain is
     promoted for a single integration only if it grows into a standalone property.
  3. **`aidoc-flow.ai` is reserved for the agents / A2A-protocol / cloud-hosting
     product** — not spent on a dev-tool plugin (mismatched fit + brand
     fragmentation).
  4. **Plugin identity** (applied to `platforms/claude-code-plugin/.claude-plugin/plugin.json`):
     `author = { name: "AI Doc Flow", email: plugins@aidoc-flow.com, url:
     https://aidoc-flow.com }`; `homepage = https://aidoc-flow.com/claude-code`;
     `repository` stays the GitHub monorepo (source ≠ product page). Replaces the
     P1 neutral placeholder.
- **Why:** Consolidating brand/SEO/trust + cross-property auth on one registrable
  domain beats fragmenting across three TLDs or minting a subdomain per surface;
  path-based integration pages scale to N integrations with zero new DNS/TLS and
  one SEO surface. Distribution channels still differ (Claude Code marketplace /
  VS Code Marketplace / Codex), but the *website* is unified and an
  `/integrations` hub links out to each.
- **Notes / P2 publish gate:** the site and the `plugins@aidoc-flow.com` mailbox
  are **not yet live** — before marketplace **submission** (P2), verify `homepage`
  resolves and the role mailbox receives mail. The public mirror's
  `marketplace.json` `owner` uses this company/role identity; the monorepo-root
  `.claude-plugin/marketplace.json` owner is left as the personal dev identity
  until the mirror is created.

---

## D-0022 — Vendor the framework spec into the plugin (shippability exception to D-0013)

- **Date:** 2026-05-27T00:00:00Z
- **Context:** The Claude Code plugin references **47 distinct `framework/…`
  paths across 64 files**, but Claude Code copies **only the plugin directory**
  to its cache on install — so every literal `framework/<path>` reference (which
  only ever resolved from the monorepo root) breaks for every installed user.
  The plugin is therefore not installable as shipped. Full design + 3 review
  passes in `plans/PLUGIN-MARKETPLACE-PLAN.md`.
- **Decision:** The plugin **vendors** the spec subtrees it consumes —
  `framework/{layers,governance,registry}` → `platforms/claude-code-plugin/framework/{…}`,
  **byte-identical, generated** by a sync script that extends the existing
  `tools/sdd_doc_lint/sync-vendored.sh` pattern. Plugin references are repointed
  to `${CLAUDE_PLUGIN_ROOT}/framework/…` (the documented runtime anchor for a
  plugin's own cached files). This is the sanctioned **shippability exception**
  to D-0013: the monorepo `framework/` stays the **single source of truth**; the
  plugin's bundled `framework/` is **generated and never hand-edited**.
- **Why:** Identical rationale to the already-vendored `sdd_doc_lint` — a plugin
  must be self-contained to install/run from a marketplace cache, but the spec
  must stay singly-owned to avoid the dual-ownership drift D-0013 was written to
  prevent. A **drift guard** (a conformance test mirroring
  `test_doc_lint_vendoring.py`) asserts the vendored bundle is byte-identical to
  canonical, so the copy can never silently diverge; a future `framework/` edit
  re-syncs the bundle (wired into the GATE-SPEC / spec-change checklist) and the
  drift guard is the backstop. The bundle is a snapshot pinned to the plugin's
  `FRAMEWORK_SPEC_VERSION`.
- **Notes:** Vendored docs' *own* internal cross-references stay
  monorepo-relative (repointing them would break byte-identity) and are treated
  as **advisory** — the resolution gate enforces only the *plugin's* refs
  (skills/agents/commands/docs/README), not the links inside vendored docs. A
  bundled doc that *hard-depends* on a framework file outside
  `{layers,governance,registry}` adds that file to the vendored set rather than
  repointing it. Repo-root `framework/` and the dev tooling that reads it are
  unaffected.

---

## D-0005 — No saga for the plugin review runner

- **Date:** 2026-05-26T00:00:00Z
- **Decision:** The Claude Code plugin's review-team runner will **not** port
  Hermes' saga (journal / compensation / retry state-machine). It instead relies on
  the git-ignored `.aidoc/review/<artifact>/<persona>.json` blackboard for durable
  per-persona slots (resume = re-dispatch only the missing lenses) and the
  `coverage`/`quorum` policy for partial-crew degradation
  (→ low-confidence / human-review).
- **Why:** The saga exists to coordinate Hermes' *external* LLM-API fan-out, which
  can fail/timeout mid-flight and needs durable orchestration + compensation. The
  plugin's agents are Claude Code `Task` subagents whose lifecycle the harness
  manages — there is nothing to journal or compensate. The blackboard already gives
  the durable-slot/resume property and coverage/quorum gives graceful degradation,
  so a saga would be over-engineering and would fight the runtime.
- **Notes:** Consistent with the engine-agnostic spec (shared contract, per-engine
  "how") and AGENT-TEAM plan **D9**. Locks the Phase 2 direction
  (blackboard-with-coverage, not a saga port).
- **Superseded in scope** by **D-0031** (2026-06-05). D-0005's
  blackboard-for-crew-state reasoning remains authoritative; D-0031
  extends the contract with an outer-loop saga.json journal to cover
  partial outer-loop state. See `framework/governance/REVIEW_SAGA.md`
  for the lifecycle contract.

---

## D-0021 — pre-commit hooks (lint / format / security / pip-audit) + repo cleanup

- **Date:** 2026-05-24
- **Context:** Adopt automated pre-commit checks across the repo (linter errors,
  security, dependency audit) per best practices.
- **Decisions:**
  1. **Tooling:** the `pre-commit` framework. Hooks: hygiene (pre-commit-hooks),
     **ruff** + ruff-format (Python = `platforms/hermes` + `tests` only), **bandit**
     SAST (gated **medium+** — all current findings are low), **markdownlint**,
     **yamllint**, **detect-secrets** (baseline), **pip-audit** (`manual` stage —
     heavy/network, runs in CI not every commit), and a **local conformance** hook.
  2. **Pragmatic rule sets, not raw defaults** (best practice for a doc-heavy
     brownfield repo): markdownlint disables stylistic rules (MD013 line-length,
     MD060 table-style, …); ruff selects E/F/W/I/UP; yamllint lenient.
  3. **Scope:** `legacy/` + **Hermes vendored/parsed content** (`agent-skills/`,
     `prompts/`, `skills/`) excluded from markdownlint — restructuring
     code-parsed prompt headers is risky and out of scope.
  4. **Full cleanup applied** (user choice): markdownlint `--fix` (321 files) +
     ruff safe-fix/format (127), then hand-fixed the residual — incl. the genuine
     pre-existing Hermes findings (F821 missing TYPE_CHECKING import, F823
     redundant local `import os`, UP042 `str,Enum`→`StrEnum` — behavior verified),
     malformed tables, hard tabs, a double-H1, and blockquote/blank-line edges.
     `pre-commit run --all-files` is green; conformance + 383 testable Hermes
     tests pass (the 2 failures are the standing `mcp`-SDK-missing collection
     errors). Replaced the stale `ucx_hermes`-era `repos: []` placeholder.
  5. **CI:** `.github/workflows/pre-commit.yml` runs all hooks + `pip-audit`.
- **Status — DONE (2026-05-24):** branch `claude/precommit-hooks`. Contributors
  enable locally with `pip install pre-commit && pre-commit install`; pin refresh
  via `pre-commit autoupdate`.

## D-0020 — GATE-SPEC: the framework-spec change gate (CHG-D1)

- **Date:** 2026-05-23T00:00:00Z
- **Context:** ROADMAP CHG-D1 — re-introduce change management as **skills +
  CI/CD**, both platforms. The five existing gates (GATE-01/03/06/08/CODE) all
  govern a project's **artifact instances** along the BRD→Code chain; none
  governed a change to the **`framework/` spec itself**. That gap was what
  `knowledge-extractor`'s spec→CHG drafts were stamped *blocked* on (D-0019,
  ADAPT-0). Full design + 2 review passes in `plans/CHG-D1-PLAN.md`.
- **Decisions:**
  1. **GATE-SPEC is a *meta* gate, orthogonal to the artifact cascade.** It
     governs the shared contract that defines the layers (templates, governance,
     registry, VERSION) — the `docs/PROJECT.md` §6 "Process" role. It has no
     GATE-03/06/08 successor; a passed spec change instead obliges every platform
     to re-declare `FRAMEWORK_SPEC_VERSION` and re-pass conformance. Selected by
     **target** (the change edits `framework/`), not by artifact layer.
  2. **Three-way enforcer split** (the ROADMAP CHG-D1 model). Record-level
     E001–E004 (provenance, `semver_impact`+major⇒C3, never-C1, C3-approval) →
     the platform's record validator (plugin `gate-check`/`doc-chg`, Hermes
     `chg_rules.py`). Diff-aware E005 (VERSION bump) + E008 (CHANGELOG) → CI
     (`tests/chg/spec_gate.py`). Static E006 (spec-version match) + E007 (suite
     green) → the shared conformance suite. The **human** approval (E004) is
     protected-branch review — **a skill never self-approves**.
  3. **`major`⇒C3 is one-directional.** A breaking spec change must be C3;
     `minor`/`patch` may be C2. An additive change (a new optional knob, a new
     gate) reaches both platforms yet is not breaking — so it is not forced to
     C3. (GATE-SPEC's own introduction is `minor`/C2.)
  4. **New `change_source: spec` + `semver_impact` field** added to
     CHG-TEMPLATE (additive, backward-compatible; Hermes validation is
     `.get`-based, no strict key-schema to violate).
  5. **CI tooling is engine-agnostic and lives under `tests/`**, not
     `framework/` (the spec ships no runtime). The workflow stages at
     `plans/workflows-pending/chg-gate.yml` — the in-container app can't push
     `.github/workflows/**` (the standing `workflows`-permission restriction).
  6. **GATE-SPEC's introduction lands under interim PR-review controls** — a gate
     cannot gate its own introduction (mirrors how D-0019's spec doc landed).
- **Status — DONE (2026-05-23):** landed across 5 commits on
  `claude/skill-revision`. Framework spec **0.2.0 → 0.3.0** (minor; + both
  `FRAMEWORK_SPEC_VERSION` + all 54 skills' `framework_spec_version`).
  Conformance **38 → 43**; Hermes CHG unit tests 8/8 (full validation suite
  green bar the pre-existing `mcp`-SDK-missing collection errors); `plm_lint`
  clean. **Follow-up: CHG-D2** — record this as a formal `framework/governance/`
  decision (now actionable). **User-only:** relocate `plans/workflows-pending/
  chg-gate.yml` → `.github/workflows/`; configure branch protection on
  `framework/**` (the human-approval half).

## D-0019 — Project adaptation overlay + knowledge extractor (ADAPT)

- **Date:** 2026-05-23T17:50:00Z
- **Context:** Give a consuming project a bounded way to adapt the SDD flow
  without forking, plus a manual path to promote proven adaptations upward.
  Full design + review (Pass 1–4) in `plans/ADAPT-PLAN.md`.
- **Decisions:**
  1. **Promotion routes by governance owner** (corrects the original draft). Per
     `docs/PROJECT.md` §6: `framework/` spec changes are CHG-governed; platform
     (skill/tool) changes are ordinary PRs, *not* CHG. The knowledge-extractor
     classifies each candidate and routes spec→CHG / tool→PR.
  2. **ADAPT-0 — defer the spec→CHG path (option b).** The spec-change CHG gate
     is unbuilt (ROADMAP CHG-D1). v1 ships the tool-PR promotion path
     (plugin-only reach); spec-level candidates are drafted but flagged
     "blocked — needs CHG-D1". Building CHG-D1 is an out-of-scope follow-up.
  3. **Surface is closed + declarative** (`framework/governance/ADAPTATION.md`
     - machine-readable `ADAPTATION_SURFACE.yaml`). **v1 = 4 knobs**
     (`active_layers`, `section_toggles`, `audit_threshold`, `glossary`);
     **`id_format` deferred** pending an `ID_NAMING_STANDARDS.md` review to
     enumerate genuinely-selectable conventions (narrow-surface principle —
     don't invent options).
  4. **`audit_threshold` is raise-only** — a project may only make a layer's
     quality gate stricter, never lower it (preserves CLAUDE.md "never weaken a
     check"). The Tier-1 score (default 90) is the real model; the CHG
     gate-approval model has no score and is untouched.
  5. **Skippable layers = `[BDD, ADR]`** (the two non-C4 bridge layers);
     `[BRD, PRD, EARS, SPEC, TDD, IPLAN]` mandatory. A **cascade rule** removes a
     disabled layer from downstream `required_tags`/`can_reference` so
     traceability stays consistent. Conservative + reviewable; lives in the
     adaptation surface, not the core `LAYER_REGISTRY.yaml` (`optional` there is
     a separate default-flow concern).
  6. **User-global profile is an authoring-time seed, not a runtime input**
     (reproducibility). Runtime (incl. audits) reads the version-controlled
     project profile `.aidoc/profile.yaml` only; `~/.aidoc/profile.yaml` is
     merged into it at authoring time. Same precedence semantics, merge moved
     earlier so CI audits identically.
  7. **The adapting set is wider than the base skills** — `-audit`/`-autopilot`
     must honor the profile or they false-fail adapted docs; `trace-check`,
     `project-init`, `project-adopt` consult `active_layers`. (Implemented in a
     later ADAPT-A increment.)
- **Status — ADAPT complete (2026-05-23):** landed across 7 commits on
  `claude/skill-revision`. ADAPT-A: `framework/governance/ADAPTATION.md` +
  `ADAPTATION_SURFACE.yaml` (4-knob closed surface); `adapts:` + consult-clause
  wired into the 35-skill adapting set; `project-profile` skill; full doc
  registration. ADAPT-B: `ADAPTATION.md` §7 learnings-log convention +
  `knowledge-extractor` skill (owner-routing; spec→CHG draft stamped blocked on
  the unbuilt CHG-D1 gate; guidance→PR). **Single feature-close version bump**
  (sequencing refinement vs the plan's per-step bump): `framework/VERSION` +
  both platform `FRAMEWORK_SPEC_VERSION` `0.1.0 → 0.2.0`, and all 54 plugin
  skills' `framework_spec_version` (user decision: bump everything). Conformance
  **33 → 37** (governance surface well-formedness, `adapts ⊆ surface` +
  authority-ref + ≥35-wired, framework leakage guard); `plm_lint` clean.
  **Deferred (CHG-D1):** the spec→CHG promotion gate — until built, spec-level
  promotions are drafted but cannot be gated.

## D-0018 — Cut Claude Code plugin `v0.2.0`; add a repo-root plugin marketplace

- **Date:** 2026-05-23T00:00:00Z
- **Context:** The plugin's last tag (`claude-code-plugin/v0.1.0`) predates the
  8-layer migration; everything since (124-skill 8-layer corpus, 9-agent roster,
  `project-mngt` parking) sat in CHANGELOG `[Unreleased]`. There was also no way
  to *install* the plugin — only a per-plugin `plugin.json`, no marketplace
  manifest.
- **Decisions:**
  1. **Version `0.2.0` (minor), not `1.0.0`.** The 8-layer migration is a large
     feature jump but the skill/command surface may still move; staying pre-1.0
     signals that. Bumped `platforms/claude-code-plugin/VERSION` + `plugin.json`
     `version`. `FRAMEWORK_SPEC_VERSION` stays `0.1.0` (independent streams,
     `docs/PROJECT.md` §2; the conformance test checks `FRAMEWORK_SPEC_VERSION`
     against `framework/VERSION`, not the platform version — verified green).
  2. **Repo-root `.claude-plugin/marketplace.json`** (schema confirmed against
     code.claude.com/docs): marketplace `name: aidoc-flow-framework` (matches the
     repo; reads as `aidoc-flow@aidoc-flow-framework` on install) → plugin
     `aidoc-flow` via relative subdir `source: ./platforms/claude-code-plugin`.
     `version`/`description` set on the entry (optional, not inherited). Install
     command added to root + plugin READMEs.
  3. **Tag deferred to the user.** Annotated `claude-code-plugin/v0.2.0` is cut
     locally on the release commit; the in-container push 403s (5th occurrence
     of the `refs/tags/*` restriction), so the user pushes it from a local clone
     — alongside merging this branch into `main` and relocating CI.
- **Conformance:** 32/32. Recorded in plugin CHANGELOG `[0.2.0]`,
  `docs/TAGGING.md`, and `plans/HANDOFF.md`.

## D-0017 — Park `project-mngt` as legacy (pending review); pull it from the shipped plugin

- **Date:** 2026-05-22T00:00:00Z
- **Context:** `project-mngt` is a generic MVP/MMP/MMR planning *methodology*
  skill (frontmatter `layer: null`, domain-generic `REQ-NN` requirement IDs) —
  it teaches HOW to plan, not an SDD-layer artifact. It does not cleanly fit the
  8-layer engine and needs re-evaluation for fit/placement, so it should not
  ship with the plugin in the meantime.
- **Decision / actions:**
  1. **Parked**, not deleted: moved `platforms/claude-code-plugin/skills/project-mngt/`
     → `legacy/claude-code-plugin/project-mngt/` (Claude Code auto-discovers
     everything under `skills/`, so leaving `skills/` is the only reliable way to
     stop shipping it). Frontmatter `development_status: active → legacy`; park
     rationale + un-park procedure in `legacy/claude-code-plugin/README.md`.
  2. **Neutralized all inbound references** in the shipped surface: `README`
     skill table + prose; `skill-recommender` intent-map + catalog rows;
     `adr-roadmap` (SKILL + quickref) "use instead"/"combine"/related-skills;
     `doc-flow`, `trace-check`, `mermaid-gen`, `workflow-optimizer` cross-links;
     `pm-orchestrator` + `agents/README` rosters. Where a recommendation pointed
     at it for requirement planning, repointed to the requirements layers
     (`doc-brd`/`doc-prd`/`doc-ears`).
  3. **Dropped** the now-dead `("legacy-doc-ref", "project-mngt")` `plm_lint`
     exception (the skill no longer lives under any scanned scope).
  4. **Corrected** the plugin `README` skill counts to the as-built totals
     (112 `doc-*` + 12 non-doc = 124). The migration's documented 142 → 125
     reduction (plugin CHANGELOG `[Unreleased]`) had never been reflected in the
     README; parking `project-mngt` then took 125 → 124.
- **Skill count:** 125 → 124. Conformance unaffected (no count assertion; the
  parked tree is outside `skills/`, `agents/`, `commands/`).
- **Follow-up (review later):** decide whether `project-mngt` is reworked into
  an IPLAN-layer (Layer 8) helper, kept as an out-of-band methodology doc, or
  retired. Tracked in `plans/MIGRATION_TODO.md`.
- **Resolution — RETIRED (2026-05-27):** removed `legacy/claude-code-plugin/project-mngt/`.
  Rationale: it is a generic **MVP/MMP/MMR product/release-planning methodology**
  (`layer: null`), not an SDD-layer artifact; its phased-roadmap function overlaps
  `adr-roadmap` and its execution-planning overlaps the terminal `doc-iplan`, so the
  in-scope slices are already covered; reviving it as-is would reintroduce the banned
  sequential `PLAN-NNN`/`REQ-NN`/`TASK-NNN` IDs; and release-staging is out of v1's
  software/devops scope (D-0012). The methodology is a candidate for a **post-v1.0
  domain/methodology profile** (ROADMAP "Domain profiles") and remains recoverable
  from git history + the `legacy-ucx-v3.2-read-only` branch if revived. No shipped
  surface referenced it (its inbound refs were neutralized when parked), so
  conformance is unaffected.

## D-0016 — Post-migration gap audit: fix plugin-surface residue + harden the gate (not bare-token/prose patterns)

- **Date:** 2026-05-22T03:10:00Z
- **Context:** A post-completion review (cross-checked against the v3.2 source
  on `legacy-ucx-v3.2-read-only`) confirmed the **framework** 8-layer model
  correctly absorbs the deprecated SYS/REQ/CTR layers (SYS→SPEC C4-Component,
  CTR→SPEC interfaces, REQ→EARS atomic-testable). But `plm_lint`'s blind spots
  (it scanned only `skills/`, and its element-code pattern needs a trailing
  `.digit`) let deprecated-layer residue survive in the **plugin surface**:
  `agents/requirements-analyst.md` still modeled REQ as a live layer
  (`BRD→PRD→EARS→REQ→SPEC`, `docs/REQ/`, `REQ-NNN`, 3-segment IDs);
  `skills/trace-check/examples/example_validation_report.md` traced to
  `SYS-002`/`REQ-001`; `doc-validator` linked a non-existent
  `../doc-brd-validator/`.
- **Decision / actions:**
  1. **Fixed** all three: requirements-analyst's lane now terminates at EARS
     (atomic-testable requirements = EARS, per v3.2 REQ→EARS mapping), 4-segment
     IDs, `docs/03_EARS/`; the trace-check example rewritten to 8-layer
     traceability + 2-digit doc refs; the doc-validator BRD row points at the
     existing `../doc-brd-audit/` (doc-brd ships no validator).
  2. **Hardened `plm_lint`:** scan scope extended to `agents/` + `commands/`
     (always enforced); added `legacy-doc-ref` (dash refs `SYS-002`…),
     `legacy-layer-dir` (`06_SYS`/`10_TSPEC`…), and a **context-aware**
     `legacy-3seg-id` pattern (skips lines marked ❌/legacy/→/reject so
     validators' "wrong-format" teaching examples don't false-fail). Already
     wired into conformance via `test_plm_lint.py` (suite stays 32).
- **Deliberately NOT added:** bare-token (`SYS`/`REQ`/`TSPEC`) and N-layer prose
  (`12-layer`) patterns — these occur legitimately in Version-History changelog
  rows across migrated skills; flagging them would force per-file exceptions or
  false failures. The 3-seg line-context heuristic is the safe middle ground.
- **`project-mngt` kept as-is:** it uses domain-generic `REQ-NN` requirement IDs
  (a general MVP/MMP/MMR methodology skill, not SDD-layer-specific); excepted
  from `legacy-doc-ref` in the checker. `doc-naming` is excepted from
  `legacy-3seg-id` (it is the ID-format teaching authority).

## D-0015 — Plugin SPEC-/test-subtype skill families: migrate & keep as helpers (PLM-B4/B5)

- **Date:** 2026-05-22T01:30:00Z
- **Decision:** The plugin's SPEC-subtype families
  (`doc-cspec/dspec/uxspec/riskspec/procspec`) and test-subtype families
  (`doc-utest/itest/stest/ftest/ptest/sectest`) are **kept as plugin-only
  authoring helpers** under SPEC (Layer 6) and TDD (Layer 7) respectively,
  and their bodies are **migrated to the 8-layer model** (paths, IDs,
  chains) like every other family — they are NOT retired and NOT folded
  into `doc-spec`/`doc-tdd`.
- **Why:** The framework defines SPEC and TDD as single unified templates
  with no subtypes, but the *plugin* is free to ship finer-grained
  authoring skills as a value-add (its per-operation granularity is a
  documented Plugin advantage in `docs/PARITY.md`). Retiring them would be
  a real capability loss; folding them into two skills would lose the
  per-subtype slash-commands users rely on. Keeping them as helpers under
  the canonical layers preserves capability while staying spec-conformant
  (they reference, not redefine, the L6/L7 contracts).
- **Consequence:** PLM-B4 migrates `doc-spec` + the 5 SPEC-subtype
  families; PLM-B5 migrates the 6 test-subtype families. Each subtype skill
  must position itself as a specialization of its parent layer (SPEC L6 /
  TDD L7) and reference the single framework template, not a legacy subtype
  template or element-code.

- **Date:** 2026-05-21T05:50:00Z (revised same day — see Note)
- **Decision:** Preserve the pristine pre-migration `ucx_framework`
  project (original root layout) as the **protected, read-only branch
  `legacy-ucx-v3.2-read-only`** (created off `main` at commit `491e8db`,
  byte-identical; branch protection enabled). **Then**, at the Phase 5
  cutover, remove `legacy/` and root `.claude/` from the working branch
  (→ new `main`) so the shipped project is clean. The archive branch +
  git history are the durable record.
- **Why:** User directive — preserve everything ("do not remove legacy
  files"; ensure root `.claude/` is captured too), **then** clean up the
  working branch ("keeping legacy files in [a] separated archived branch
  for future reference then clean up current branch"). A protected branch
  is a more discoverable, enforceably-immutable archive than relying on
  post-deletion git history; with it in place the working-branch removals
  lose nothing substantive.
- **Safety (verified before restoring the removals):** the archive branch
  contains all 7 legacy trees (`ucx_flow_v3`, `ucx_hermes`, `mcp_ucx`,
  `ai_dev_ssd_flow_v2`, `ucx_kb`, `ucx_knowledge`, `hermes_agent_skills`)
  and root `.claude/`. **Caveat:** the archive holds the *pre-migration*
  `.claude/` (236 files, no hooks); the working branch's *migration-era*
  `.claude/` (240 files, incl. the 3 migration hooks) survives removal
  only in the working branch's git history — acceptable, as those hooks
  are obsolete migration scaffolding and the skills were productized into
  `platforms/claude-code-plugin/`.
- **Aligns with** the original cutover policy ("`legacy/` removed /
  archived at the Phase 5 cutover" — `docs/REPO_STRUCTURE.md`,
  `docs/PROJECT.md` §4, `ROADMAP.md` Phase 5, `CLAUDE.md`) — now realised
  via the archive branch rather than history-only deletion. P5-T4
  reconciles those docs to name the `legacy-ucx-v3.2-read-only` branch as
  the archive.
- **Consequence:** Phase 5 keeps its two removal tasks **restored**
  (P5-T2 remove `legacy/`, P5-T3 remove root `.claude/`), each gated on
  the archive branch existing (it does) + explicit confirmation at
  execution; root `.claude/` removal is sequenced **late** (it disables
  the session's own hooks). `CLAUDE.md` is **rewritten** to post-migration
  memory in P5-T4 (it's a root file, not under `.claude/`, so it survives
  the `.claude/` removal).
- **Note (revision):** an interim reading of the user's directives
  (recorded briefly the same day) had this as "retain `legacy/` + root
  `.claude/` in-tree, no removals." Once the protected archive branch was
  created and confirmed, the user restored the original archive-then-clean
  intent; this entry reflects the final decision.

## D-0013 — Framework templates are the single source of truth; platforms consume, not duplicate

- **Date:** 2026-05-19T14:50:00Z
- **Decision:** The 8 layer document templates
  (`<X>-TEMPLATE.yaml` for BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN) live
  exclusively in `framework/layers/<NN>_<X>/`. Platforms do **not** ship
  their own copies. Hermes' legacy `templates/` directory is dropped at the
  port (P2-T1 Q3); the platform's runtime template-loader reads from
  `framework/layers/`. Any platform-specific runtime data the legacy
  templates carried (e.g. `server: ucx_hermes`, `tool: sdd_validate`) moves
  to platform-side config — never into the engine-agnostic templates.
- **Why:** The framework is engine-agnostic by D-0006 and the conformance
  spec-hygiene tests. Embedding engine names in shared templates violates
  that contract. The legacy duplicate had already drifted from the framework
  by exactly that engine-named block (audit §3b), proving the maintenance
  burden of dual ownership. Single source of truth + clear runtime/document
  separation. Generalises: future platforms (Claude Code plugin and beyond)
  follow the same rule.
- **Notes:** Resolves the audit's §3b prose-coupling in `templates/*.yaml`
  automatically — those files are not copied to `platforms/hermes/`. The
  lone `BRD-MD-TEMPLATE.md` (no framework equivalent) is investigated at
  P2-T3 and ported-or-dropped based on call-site usage.

## D-0012 — Framework purpose: the IPLAN is the product; v1 scope is software/devops

- **Date:** 2026-05-19T12:45:00Z
- **Decision:**
  - aidoc-flow's purpose is to transform business intent into a
    fully-traceable, gate-approved **IPLAN** — the framework's *terminal
    artifact*. Source-code generation and deployment are **out of scope**:
    they are downstream, agent-agnostic steps performed by any capable AI
    agent, not by the framework.
  - The **IPLAN is the product**: a machine-readable, auditable handoff
    contract bundling reasoning (BRD/PRD), states (EARS), behavior (BDD),
    infrastructure decisions (ADR), testing procedures (TDD/TSPEC), and
    specifications — self-contained enough that any agent can execute it
    without further clarification.
  - **v1 scope is software + devops domains only.** The current SDD layers
    (EARS, BDD, ADR, TDD) are software-native. Non-technical task domains are
    deferred to a post-v1.0 **domain-profile** mechanism (see `ROADMAP.md`,
    "Post-v1.0 — Planned Capabilities").
  - Promise framing is **"rigorous, auditable, gap-surfacing"** — *not*
    "bullet-proof". The framework enforces structure and blocks on unresolved
    open questions, but cannot manufacture requirements a human never supplied.
- **Why:** Code generation and deployment are commoditized across AI agents;
  the scarce, defensible value is auditable reasoning with end-to-end
  traceability. Terminating scope at the IPLAN keeps the name `aidoc-flow`
  accurate — the framework *is* the document flow. Limiting v1 to
  software/devops keeps the existing layers fit-for-purpose; chasing
  universality early would dilute the framework into being vague at everything.
- **Notes:** The conformance suite gains a job — verifying IPLAN
  *agent-readiness* (no TBDs, full upstream traceability, bundled test specs,
  explicit stack/runtime constraints). Domain generalization is an
  architectural goal (a generic flow engine + per-domain profiles), sketched
  in `ROADMAP.md` as post-v1.0.

### Refinements

- **R1 — 2026-05-19T13:10:00Z — the IPLAN has a *planned* and an *executed*
  state.** The IPLAN is one artifact in two states: *planned* (YAML
  instructions with confirmations pending) and *executed* (each confirmation
  satisfied with evidence — what ran, results, actual vs expected). The
  *executed* IPLAN is the auditable trail behind a result; in practice humans
  scrutinise the result, not the forward plan, and often accept the planned
  IPLAN blindly. **Criticality scales audit depth:** low-criticality work
  (e.g. a throwaway MVP cloud deploy) — the IPLAN is internal quality control,
  nobody audits; high-criticality work — the executed IPLAN's evidence *is*
  the deliverable. Audit depth is a dial set by criticality, not all-or-nothing.

- **R2 — 2026-05-19T13:10:00Z — the unit of value is the curated corpus, not a
  single IPLAN.** A single IPLAN is reproducible and low-value. A curated,
  maintained library of *proven* IPLANs is codified, executable institutional
  knowledge — the customer's IP. An IPLAN earns library membership by being
  executed and audited (R1). The library — plus **composition** (IPLAN
  templates vs instances; IPLANs composing IPLANs) and **freshness**
  (re-validation, versioning, staleness flags) — is the post-v1.0 strategic
  destination: the framework as a system of record for an organisation's
  executable process knowledge. Sketched in `ROADMAP.md`.

## D-0011 — Bookmark tags alongside release tags

- **Date:** 2026-05-19T11:20:00Z
- **Decision:** Git tags serve two roles. **Release tags** (`vX.Y.Z`,
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`) are annotated, immutable, and
  permanent. **Bookmark tags** (`mark/<slug>`) are annotated, mutable, and
  disposable — they mark notable non-release commits (baselines, known-good
  states, audit points) for easy retrieval via `git tag -l 'mark/*'`. The full
  policy lives in `docs/TAGGING.md`; `docs/PROJECT.md` §3 links it.
- **Why:** Tags are a cheap, searchable way to mark history. Restricting them
  to releases wastes that. A separate, clearly non-SemVer namespace keeps
  bookmarks from being mistaken for versions.
- **Notes:** `docs/TAGGING.md` is the single authority; the tag-namespace
  table was moved there from `docs/PROJECT.md` §3 to avoid two copies drifting.

## D-0010 — Framework docs drop legacy version-lineage content

- **Date:** 2026-05-19T10:00:00Z
- **Decision:** When extracting docs into `framework/`, drop content that only
  documents the legacy SDD version lineage — the `## v3.2 Changes from v3.0`
  sections (P1-T7, in the guide and the testing-strategy doc) and the
  `CHG_MIGRATION_PLAN.md` (v2→v3) reference in `QUICK_REFERENCE.md`.
- **Why:** `framework/` is a fresh `0.1.0` version stream (D-0006); it does not
  continue the legacy `v3.x` numbering, so "changes from v3.0" history is both
  inaccurate framing and carries `v3.x` tokens the conformance hygiene check
  bans. The current layer order/rationale those sections explained is already
  stated as present-tense fact elsewhere in each doc.
- **Notes:** Removal is limited to version-lineage framing; all genuinely
  engine-agnostic methodology content is copied verbatim.

## D-0009 — Namespaced version tags; framework tag at Phase 1 close

- **Date:** 2026-05-19T09:15:00Z
- **Decision:** Each SemVer stream tags in its own namespace — project
  milestones `vX.Y.Z`, framework spec `framework/vX.Y.Z`, platforms
  `<platform>/vX.Y.Z`. `VERSION` files hold the bare SemVer; the tag adds the
  `v` and namespace. The `framework/v0.1.0` tag is created at Phase 1 close
  (after P1-T7), not at P1-T6 — so it marks a fully assembled spec — alongside
  the `v0.2.0` project milestone.
- **Why:** `docs/PROJECT.md` defined only bare milestone tags; the independent
  framework/platform streams need distinct, collision-free tag names.
  Slash-namespaced refs let `git tag -l 'framework/*'` filter one stream.
  Tagging an incomplete spec would burn a version on a partial assembly.
- **Notes:** Convention recorded in `docs/PROJECT.md` §3 (extended, not a new
  doc). P1-T6 delivers `framework/VERSION` + the convention; the deferred tag
  is tracked as the Phase 1 close task (P1-T8).

## D-0008 — Conformance suite is stdlib-only (`unittest`)

- **Date:** 2026-05-18T21:20:00Z
- **Decision:** Build `tests/conformance/` on the Python 3.11 standard library
  (`unittest`) plus `PyYAML`. No `pytest` dependency.
- **Why:** The conformance suite is the shared, engine-agnostic contract; it
  must be runnable by any platform with zero install friction. `pytest` is not
  installed in the environment, and `python -m unittest discover` runs the
  suite anywhere. `unittest.TestCase` classes remain `pytest`-discoverable for
  platforms that prefer that runner.
- **Notes:** Discovery uses a flat package-less layout (`tests/conformance/`
  with no `__init__.py`) so test modules can `import _spec` directly under
  `unittest discover`. The plan listed an `__init__.py`; it was dropped during
  implementation for clean discovery.

## D-0007 — Plan review is a two-pass, recorded gate

- **Date:** 2026-05-18T18:45:00Z
- **Decision:** Every plan file carries a `## Review log` with **≥2**
  ISO-stamped passes; a plan may not be presented, handed off, or implemented
  until it does. New plans start from `plans/PLAN-TEMPLATE.md`. A non-blocking
  `PreToolUse(git commit)` hook warns when a staged plan file falls short.
- **Why:** The review/harden step was prose-only, so a skipped second pass was
  invisible — it happened once on the P1-T2 plan. Making each pass a named,
  checkable artifact turns a silent omission into a visible gap.
- **Notes:** The hook enforces that a pass is *recorded*, not that it is
  thoughtful — review quality stays a manual judgment step.

## D-0006 — First `framework/` spec version is `0.1.0`

- **Date:** 2026-05-18T18:00:00Z
- **Decision:** The extracted `framework/` spec starts its independent version
  stream at `0.1.0`, carrying a `derived_from: "SDD v3.2"` metadata field.
  `1.0.0` is reserved for when both platforms pass the shared conformance suite.
- **Why:** The content is mature, but as a freshly re-packaged engine-agnostic
  artifact it is not yet conformance-proven and no platform is wired to it.
  `0.x` is the honest signal; the lineage field preserves provenance.

## D-0005 — `framework/` ships per-layer index templates

- **Date:** 2026-05-18T18:00:00Z
- **Decision:** Each `framework/layers/` directory ships a
  `{TYPE}-00_index.TEMPLATE.{md,yaml}` skeleton. Legacy `*-00_index.*` instance
  files are dropped (project data, not spec).
- **Why:** The index/registry *format* is a conformance concern — both
  platforms must produce and validate index files identically. Pinning the
  format in the spec prevents platform divergence.

## D-0004 — Compaction/continuity automation via hooks

- **Date:** 2026-05-18T17:27:00Z
- **Decision:** Add a `PreCompact` hook that auto-commits and pushes a WIP
  snapshot, and a `SessionStart` hook that injects `plans/HANDOFF.md` into
  context. Scripts live in `.claude/hooks/`.
- **Why:** Containers are ephemeral; only pushed work survives. The PreCompact
  hook guarantees a durable snapshot before any memory-reduction event; the
  SessionStart hook restores continuity automatically.
- **Notes:** Hooks run shell commands, not Claude reasoning — they cannot
  *write* the handoff narrative. `plans/HANDOFF.md` is refreshed manually as a
  workflow step; the hook only snapshots whatever is on disk. The PreCompact
  hook no-ops off the working branch as a safety guard.

## D-0003 — Project memory + development workflow in `CLAUDE.md`

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Maintain a root `CLAUDE.md` as auto-loaded project memory, and
  codify the change flow (plan → review → harden → implement → verify → land).
- **Why:** Each session starts cold in a fresh container. Persistent memory
  prevents re-discovery; an explicit flow keeps quality consistent.

## D-0002 — `plans/` workspace for migration tracking

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Create a fresh root `plans/` (distinct from the frozen
  `legacy/plans/`) holding `MIGRATION_TODO.md` (live tracker), `HANDOFF.md`,
  `DECISIONS.md`, and ad hoc working notes.
- **Why:** Separates volatile working state from the stable published
  `ROADMAP.md`.

## D-0001 — Isolate the pre-migration project into `legacy/`

- **Date:** 2026-05-18T00:00:00Z
- **Decision:** Move the entire pre-migration project into `legacy/` via git
  renames; freeze it (copy-don't-move); disable legacy CI.
- **Why:** A clean root for the new multi-platform structure with zero path
  overlap, while preserving the old project for content extraction in
  Phases 1–3 and full git history.
