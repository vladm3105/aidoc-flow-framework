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

1. **First**: complete BRD-RT-002 live verification (~$10 for the two cheap
   checks) — without it, both follow-ups risk building on a broken pattern.
2. **Then PRD-RT-001** — propagates the pattern to the next layer at low
   marginal cost. Forces the BRD-RT pattern to prove it generalises.
   Validates the "Reusable from BRD-RT-002" claim before committing to
   EARS/BDD/ADR/SPEC/TDD/IPLAN.
3. **Then caching** — once 2 layers are proven on the Task-fan-out path,
   the caching optimisation is a transparent perf improvement behind the
   same contract. Saves real money when the full cascade starts running
   regularly.

Reverse order is also viable (caching first, then PRD-RT) — that would
mean PRD-RT-001 immediately inherits the cached runner. But it ships an
unproven 2-layer wiring on top of a new dispatch mechanism, which is
harder to debug if either breaks. Recommend PRD-RT-001 first.

## Cross-references

- BRD-RT-001 plan: `plans/BRD-REVIEW-TEAM-PLAN.md`
- BRD-RT-002 plan: `plans/BRD-RT-002-VERDICT-CHAIN-PLAN.md`
- PROFILE-DELTA-001 plan: `plans/PROFILE-DELTA-OVERRIDE-PLAN.md`
- Framework review-team contract: `framework/governance/REVIEW_TEAM.md`
- Per-layer crews + weights: `framework/governance/REVIEW_CREWS.yaml`
- Adaptation surface (knob registry): `framework/governance/ADAPTATION_SURFACE.yaml`
- Decision register entries: D-0024, D-0025, D-0026 in `plans/DECISIONS.md`
