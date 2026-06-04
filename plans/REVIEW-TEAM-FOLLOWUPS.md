# REVIEW-TEAM-FOLLOWUPS — TODO

| Field      | Value                                      |
|------------|--------------------------------------------|
| Source     | BRD-RT-001 (D-0024), PROFILE-DELTA-001 (D-0025), BRD-RT-002 (D-0026) — all merged |
| Status     | TRACKING — 2026-06-04T15:30:32Z            |
| Feeds      | future PRs (one per item)                  |

## Context

The review-team architecture has landed at the BRD layer via three sequenced PRs:

- **BRD-RT-001** (D-0024, plugin v0.4.1): wired Claude Code `Task`-tool subagent
  fan-out into `doc-brd-audit`, `doc-brd-fixer`, and `doc-brd-autopilot`. The
  framework's spec-defined `independent` review mode now actually runs at the
  BRD gate with a per-artifact blackboard at `.aidoc/review/01_BRD/<BRD-id>/`.
- **PROFILE-DELTA-001** (D-0025, plugin v0.4.2, framework spec 0.11.3):
  refactored `.aidoc/profile.yaml` from a verbatim copy of the framework
  default into a true override-only delta. New `framework/governance/PROFILE-TEMPLATE.yaml`
  ships as the bootstrap skeleton.
- **BRD-RT-002** (D-0026, plugin v0.4.3): closed five gaps from BRD-RT-001's
  live verification runs. Synthesizer now writes a structured `verdict.json`
  companion; every verdict consumer (audit-skill stdout, driver script,
  autopilot revise loop, fixer) reads JSON instead of scraping Markdown.
  Per-layer cap raised 900s → 1800s; new `AUDIT_TIMEOUT=1200s` via name-match.

The items below are the **explicitly deferred** follow-ups identified across
those three PRs' "Out of scope" sections plus the cost-optimization plan
sketched in PR #69's caching-analysis discussion.

## Follow-up items

### TODO-RT0 — BRD-RT-003: operational fixes from BRD-RT-002 live verification

- **Status:** PENDING — 2026-06-04T12:30:00Z
- **Source:** BRD-RT-002 live verification (Run #1 team mode + Run #2
  single_pass) on 2026-06-04. Verification confirmed verdict-chain
  consistency end-to-end (the architectural contract works) but
  surfaced three operational gaps in the BRD layer that don't impact
  the contract but cause failures under realistic team-mode timing.
- **Scope:** three small fixes that together unblock per-layer team
  mode for routine use:
  - **G11 — Autopilot timeout too short.** `doc-brd-autopilot` hit
    the default 600s `SKILL_TIMEOUT` (exit 124) in team mode because
    the autopilot now internally orchestrates a sub-team (drafter →
    audit → fixer loop). BRD-RT-002's `AUDIT_TIMEOUT=1200` name-match
    only covered `*-audit`. Fix: extend the name-match in
    `tests/scripts/test-acceptance.sh:_pick_timeout_for` to also
    catch `*-autopilot`, OR introduce a separate
    `AUTOPILOT_TIMEOUT=1800`.
  - **G12 — Per-layer cap exceeded.** Run #1's BRD layer ran 2569s
    > 1800s cap. Breakdown: autopilot timeout (600s wasted) + first
    audit (~580s) + fixer (487s) + re-audit (~900s) = ~2569s.
    Resolution may follow from fixing G11 (autopilot succeeds in
    one shot, no driver-level duplicate audit). If 1800s still
    tight after G11, raise to 3600s.
  - **G13 — Fixer team-mode lens-validation unverified.** Run #1's
    fixer ran (487s, outcome PASS) but produced no
    `<persona>.fix_<N>.json` slots. The 1 P1 finding spanned
    architect + business_analyst lenses; possibly the fixer skipped
    lens validation when no single lens "owned" the finding, or the
    BRD-RT-001 SKILL text describing the team-mode patch-validation
    loop is under-specified. Investigate: read
    `doc-brd-fixer/SKILL.md` Remediate Mode §4 (Validate
    non-regression), trace what actually happened in the live run,
    add explicit dispatch-decision rules for multi-lens findings if
    needed.
- **Estimated effort:** ~1-2 hours of script + skill edits; one live
  re-verification (~$5-7, ~15-20 min) to confirm Run #1's pass
  criteria reach 6/6 instead of 4/6.
- **Plugin version:** plugin v0.4.3 → v0.4.4 (small patch). Could
  also ride along in PRD-RT-001 (TODO-RT1 below) if scheduling
  aligns — same script + same fixer-SKILL touchpoints.
- **DECISIONS.md entry:** D-0027 — "Autopilot timeout extends to
  match audit (`*-autopilot` in the name-match); multi-lens fixer
  findings dispatch all responsible lenses for validation."
- **Verification artifacts to inspect** (already on disk from
  2026-06-04 live runs but not committed):
  - `examples/url-shortener/.aidoc/review/01_BRD/BRD-01/verdict.json`
    (from Run #1) — confirms verdict.json schema is correct
  - `examples/url-shortener/logs/2026-06-04T113650/elements/doc-brd-fixer.log`
    — fixer reported outcome PASS but no slot dispatch
  - `examples/url-shortener/logs/2026-06-04T122110/.aidoc/audit/01_BRD-audit.md`
    (Run #2) — confirms single_pass advisory note works
- **Sequencing note:** BRD-RT-003 should land **before** PRD-RT-001
  if PRD-RT-001 wants its first live verification to reach 6/6
  cleanly. Otherwise PRD-RT-001 will inherit the same G11/G12/G13
  gaps and produce the same "4/6 pass" pattern.

### TODO-RT1 — PRD-RT-001: propagate BRD-RT pattern to the PRD layer

- **Status:** PENDING — 2026-06-04T15:30:32Z
- **Scope:** Apply the BRD-RT-002 pattern verbatim to four PRD-layer skills
  (`doc-prd`, `doc-prd-audit`, `doc-prd-fixer`, `doc-prd-autopilot`):
  - `doc-prd-audit/SKILL.md` team-mode branch with the PRD crew from
    `REVIEW_CREWS.yaml` (`{product_owner: 30, architect: 25, tech_lead: 20,
    adversary: 15, auditor: 10}`) + Output Contract subsection mirroring
    `verdict.json`.
  - `doc-prd-autopilot/SKILL.md` create→review→revise loop reading
    `verdict.combined_status` for gate decisions.
  - `doc-prd-fixer/SKILL.md` Input Contract preferring `verdict.json`.
  - Always-on `single_pass` advisory note in `doc-prd-audit` Combined Report.
  - All four skills declare `review_mode` in `adapts:` frontmatter.
  - `<PRD-id>` codified as short artifact ID (`PRD-01`), not nested folder name.
- **Prerequisite:** BRD-RT-002 live verification (Verification step 4 of PR
  #73) must pass cleanly first — confirms the pattern actually works
  end-to-end before propagating. **Live cost:** ~$5-7, ~15-20 min.
- **Out of scope:** PRD-layer prompt content changes beyond the team-mode
  wiring. The PRD crew composition and weights come from `REVIEW_CREWS.yaml`
  and are not modified.
- **Reusable from BRD-RT-002:** the entire fix-shape pattern (Output Contract
  subsection, verdict.json read, autopilot revise loop, fixer slot
  preference, single_pass advisory) is generic — only the layer name and
  crew composition substitute.
- **Estimated effort:** ~3 hours of skill text edits + plugin version bump
  (0.4.3 → 0.4.4) + plan PR + impl PR + live verification (~$5-7).
- **Plugin version:** plugin v0.4.3 → v0.4.4. Framework spec unchanged.
  No GATE-SPEC.
- **Decision register:** new D-0027 — "PRD-RT-001 inherits BRD-RT-002
  verdict-chain pattern; per-layer follow-ups for EARS-RT, BDD-RT,
  ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT chain through the same pattern."
- **Next steps:** open plan PR `plans/PRD-RT-001-PLAN.md` covering the
  per-layer translation; verify against the BRD-RT-002 verification
  template; land impl PR.

### TODO-RT2 — REVIEW-TEAM-RUNNER-CACHING-001: prompt caching for team-mode (v0.4.4 or later)

- **Status:** PENDING — 2026-06-04T15:30:32Z
- **Scope:** Reduce team-mode audit cost from ~3.3× single-pass per gate to
  ~1.3× via Anthropic prompt caching. Concretely:
  - Build a new `tests/scripts/review_team_runner.py` (or
    `platforms/claude-code-plugin/scripts/`) — a Python orchestrator that
    calls the Anthropic SDK directly with `cache_control` markers on the
    shared prefix (framework reference docs + the artifact under review).
  - Dispatch the 4 review lens calls in parallel via `asyncio.gather` so the
    4× cached-input savings actually materialise.
  - Replace the synthesizer LLM call with a **deterministic Python reduce**
    of the per-persona slot JSONs (the reduce is spec'd as deterministic
    per `REVIEW_TEAM.md` §"Synthesis = reduce + narrative" — the only
    stochastic part is the optional narrative pass).
  - Optionally use Haiku for the narrative-only pass (~3-4× cheaper than
    Sonnet for structured aggregation).
  - Update `doc-*-audit/SKILL.md` team-mode branch to invoke the runner
    instead of fanning out via `Task`. Same lens contract, same blackboard
    layout — drop-in replacement.
  - Add a `caching: enabled | disabled` knob in `.aidoc/profile.yaml` (new
    knob in the closed adaptation surface — requires framework spec bump
    0.11.3 → 0.11.4) so projects can opt back into the `Task`-fan-out path
    if the runner is unavailable (no SDK installed, no API key).
- **Why not in BRD-RT-002:** Claude Code's `Task` tool does not expose
  `cache_control` markers to skill authors. Caching requires bypassing the
  Task mechanism with a direct-SDK runner. Architectural shape change
  warranting its own PR.
- **Cost math** (per audit, at Sonnet rates):
  - Current (BRD-RT-002 team mode): ~$0.62 (3.3× single-pass baseline)
  - With caching: ~$0.25 (1.3× baseline) — **60% reduction**
  - Across a full team-mode cascade: ~$80 → ~$30
- **Dependencies:** BRD-RT-002 live verification must pass first (confirms
  the slot/verdict.json contract works as designed before we change the
  dispatch mechanism behind it).
- **Risks:**
  - Bypasses Claude Code's `Task` mechanism — divergence from the
    "Claude Code-native" plugin design. Mitigation: keep the Task-fan-out
    path as the fallback when the Python runner is unavailable.
  - Adds Python dependency (Anthropic SDK) to the plugin's runtime path.
  - Auth context — the runner needs `ANTHROPIC_API_KEY`; today the plugin
    uses `claude -p` interactive login. Mitigation: detect both, prefer
    runner when SDK + API key are present, fall back to Task fan-out.
- **Estimated effort:** ~2-3 days. Touches a new Python script,
  `doc-*-audit/SKILL.md` (all 8 layers' team-mode branches), plugin
  version bump, plan + impl PRs, framework spec bump for the new
  `caching` knob.
- **Plugin version:** plugin v0.4.4 → v0.4.5 (after PRD-RT-001), OR
  v0.4.3 → v0.4.4 if it lands before PRD-RT-001. Sequencing decision
  deferred until both plans are drafted.
- **Framework spec:** 0.11.3 → 0.11.4 (additive — new `caching` knob in
  `ADAPTATION_SURFACE.yaml`).
- **Next steps:** open plan PR `plans/REVIEW-TEAM-RUNNER-CACHING-001-PLAN.md`
  detailing the runner architecture, SDK integration, fallback logic, and
  verification ladder.

## Sequencing recommendation

Updated 2026-06-04 after BRD-RT-002 live verification (Run #1 + Run #2):

1. **First — BRD-RT-003** (TODO-RT0): close G11/G12/G13 operational
   gaps from Run #1. Without these, every per-layer team-mode run
   will repeat the same 4/6 pass-criteria pattern (verdict-chain
   works, but autopilot timeout + per-layer cap + fixer slot
   dispatch all fail). Small PR (~1-2 hours + ~$7 re-verification).
2. **Then PRD-RT-001** (TODO-RT1): propagates the BRD-RT pattern to
   the PRD layer at low marginal cost once BRD-RT-003's fixes make
   the pattern actually robust. Forces the pattern to prove it
   generalises. Validates the "Reusable from BRD-RT-002" claim
   before committing to EARS/BDD/ADR/SPEC/TDD/IPLAN.
3. **Then caching** (TODO-RT2): once ≥2 layers are proven on the
   Task-fan-out path, the caching optimisation is a transparent
   perf improvement behind the same contract. Saves real money when
   the full cascade starts running regularly.

Reverse order is also viable (caching first, then PRD-RT) — that would
mean PRD-RT-001 immediately inherits the cached runner. But it ships an
unproven 2-layer wiring on top of a new dispatch mechanism, which is
harder to debug if either breaks. Recommend BRD-RT-003 → PRD-RT-001 →
caching.

## BRD-RT-002 verification snapshot (2026-06-04)

Two live runs against `examples/url-shortener` BRD layer:

| | Run #1 (team mode) | Run #2 (single_pass) |
|---|---|---|
| Outcome | FAIL (7/1/1/9) | PASS (7/0/8/15) |
| Wall-clock | 2569s (cap exceeded) | 764s (within cap) |
| Pass criteria met | 4/6 | 5/5 |
| Verdict-chain consistency | ✅ verified end-to-end | ✅ override-respect + advisory verified |

Run #1 outcome FAIL is from `doc-brd-autopilot` timeout, not from
verdict-chain drift. The architectural contract (synthesizer writes
verdict.json, all consumers read it consistently) is **verified**;
the operational issues are routine timeout tuning captured as
TODO-RT0.

## Cross-references

- BRD-RT-001 plan: `plans/BRD-REVIEW-TEAM-PLAN.md`
- BRD-RT-002 plan: `plans/BRD-RT-002-VERDICT-CHAIN-PLAN.md`
- PROFILE-DELTA-001 plan: `plans/PROFILE-DELTA-OVERRIDE-PLAN.md`
- Framework review-team contract: `framework/governance/REVIEW_TEAM.md`
- Per-layer crews + weights: `framework/governance/REVIEW_CREWS.yaml`
- Adaptation surface (knob registry): `framework/governance/ADAPTATION_SURFACE.yaml`
- Decision register entries: D-0024, D-0025, D-0026 in `plans/DECISIONS.md`
