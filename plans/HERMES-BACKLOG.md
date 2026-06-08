# Hermes Backlog — deferred work pending plugin completion

| Field | Value |
|-------|-------|
| Status     | **DEFERRED** — pending completion of plugin-side work |
| Owner      | vladm3105 |
| Last update | 2026-06-06 |
| Policy     | **Plugin-first development.** Hermes work is deferred until the corresponding plugin functionality is complete and verified end-to-end. This is the single source of truth for "what Hermes still needs to catch up on." |

## Why this exists

The aidoc-flow project ships two independent platforms — the Claude Code
plugin and Hermes (MCP server) — against the same engine-agnostic
framework spec. Plugin-side iteration is currently faster (it has
working acceptance suites, smaller surface area, and the recent
SAGA-PARITY-001 work has paid off there). Rather than splitting effort
across both platforms in parallel, the project sequences:

1. **Develop and verify on the plugin side first.** Each feature
   ships, gets exercised in the url-shortener acceptance cascade,
   and any bugs surface against real artifacts.
2. **Apply the verified lessons to Hermes in a batch** once the
   plugin reaches a natural completion point (e.g., after Phase 4
   propagates the saga driver to PRD..IPLAN).

Plugin-first is not a permanent asymmetry — it's a sequencing
choice. Hermes still ships against every framework-spec change
(GATE-SPEC), but the Hermes-side implementations of features that
the plugin has been the testbed for are batched here.

## Hermes-deferred items

### H-1 — SAGA-PARITY-001 Phase 3: G-R1 invariant alignment

**Source:** [`docs/PARITY.md`](../docs/PARITY.md) §Enforcement parity;
plugin commits `802d9b72` (Amendment 1 merge), `558ef6c8`
(REVIEW-CALIBRATION-001 plan), `d3692d9f` (REVIEW-CALIBRATION-001 impl).

**Original placeholder:** earlier session drafted a
`plans/SAGA-PARITY-001-PHASE-3-PLAN.md` on a `plan/saga-parity-001-phase-3`
local branch. That draft predates Amendment 1's bug-hunt
(B1-B7) and the BRANCH_COMPENSATING spec-gap finding from
REVIEW-CALIBRATION-001 verification. The draft is stale and should
be refreshed when work resumes — do NOT just open it as a plan
PR.

**Substantive work for Hermes:**

- Bring Hermes' `saga_orchestrator.py` / `saga_models.py` /
  `saga_journal.py` PARTIAL_TIMEOUT handling into alignment with
  the plugin's `tools/saga_driver.py`:
  - Ensure G-R1 holds — never write `from: PARTIAL_TIMEOUT`; walk
    `transitions[]` backward to find the resume point. The plugin
    `saga_driver.py:resume_from_partial_timeout()` is the
    reference implementation.
  - Iteration-stop on PARTIAL_TIMEOUT (the plugin's while-loop exit
    condition is `{CLOSED, ESCALATED, PARTIAL_TIMEOUT}` after the
    Amendment 1 B7 fix).
  - PARTIAL_TIMEOUT used for subprocess-failure paths instead of
    direct ESCALATED (per the spec's narrow `BRANCH_FAILED →
    ESCALATED` rule — `BRANCH_COMPLETED`/`PREPARED` can't reach
    ESCALATED legally).
- Add Hermes-side conformance equivalent to
  `tests/conformance/test_saga_driver_invariants.py` (10 tests
  asserting the state machine matches the spec).
- Live verification: run Hermes through the same url-shortener BRD
  cascade scenario and verify the resulting saga.json is
  schema-conformant with no `from: PARTIAL_TIMEOUT` transitions.

**Spec gap to consider during this work:** the audit/fixer SKILLs
emit transitions `BRANCH_COMPLETED → BRANCH_COMPENSATING`,
`BRANCH_COMPENSATING → BRANCH_COMPLETED`, and `BRANCH_COMPLETED →
FANOUT_STARTED` during the fixer cycle. Those aren't in
`_ALLOWED_TRANSITIONS` per the current spec. Hermes' state machine
is the authoritative test — does it reject them? If so, the spec is
right and the SKILLs need slimming (Phase 4 work); if not, the
spec needs amendment to model the fixer-revisit transitions.

**Dependency:** plugin Phase 4 (PRD..IPLAN saga driver propagation)
should land first — Phase 4 may further refine the state machine
based on per-layer differences, and Hermes should align to the
final shape, not an intermediate one.

### H-2 — REVIEW-CALIBRATION-001 lens sub-checks for Hermes review

**Source:** plugin PR #95 (plan) + #96 (impl);
[`platforms/claude-code-plugin/skills/doc-*-audit/SKILL.md`](../platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md).

**Plugin status:** 5 content sub-checks (A1 cell-actionability + A2
assumption-capture + A3 cross-section pointer-validity + BA1
AC-testability + SE1 deferred-decision safety) added to all 8 plugin
audit SKILLs. v0.6.1 → v0.6.2 PATCH.

**Substantive work for Hermes:**

- Add equivalent sub-checks to Hermes' review prompts (whatever
  Hermes uses to render lens persona instructions for the auditor,
  business_analyst, and security_engineer roles).
- The plugin's `## Content Sub-Checks` block in
  `doc-brd-audit/SKILL.md` is the reference; the wording uses
  section *concepts* not § numbers so it transfers verbatim.
- Live verification: run Hermes' audit against the saved BRD-01
  artifact (
  [`examples/url-shortener/.aidoc/before-after/BRD-01-before-fix.md`](../examples/url-shortener/.aidoc/before-after/BRD-01-before-fix.md)
  ) and confirm all 5 missed-issue categories surface ≥1 finding.

**Dependency:** none specific — could run in parallel with H-1.
Recommended to batch with H-1 to minimize Hermes-touching PRs.

### H-3 — REVIEW-CALIBRATION-002 backlog (if any items survive plugin-side experience)

**Source:** plan PR #95's "Out of scope" section.

The REVIEW-CALIBRATION-001 plan deferred 6 speculative items as a
one-line backlog enumeration. None has design work in
REVIEW-CALIBRATION-002 yet — they're a watch-list:

- New outward-facing `consumer_simulator` lens
- `min(lens_scores) ≥ 85` per-lens-minimum PASS gate
- Iteration-stop-on-stability (replace score-only PASS gate)
- Author-isolation for drafter-as-reviewer
- `sdd_doc_lint` cross-section pointer rule
- Hermes-side application of the v0.6.2 sub-checks (this is H-2 above)

**Trigger:** revisit only if future verification surfaces that the
v0.6.2 sub-checks miss something the deferred items would catch.
Until then, no design work.

### H-4. Layer Playbook Injection in Hermes Team-Mode (LAYER-PLAYBOOKS-001)

**Source:** PR LAYER-PLAYBOOKS-001 (plugin) shipped per-layer per-lens
playbooks at `framework/playbooks/<NN>_<LAYER>/<lens>.md` (BRD + PRD
to start; other 6 layers ship per-layer in follow-up PRs). Hermes
does not yet consume them.

**Scope:** When Hermes implements team-mode lens fan-out, the lens
prompts must inline the (layer, lens) playbook content per the
framework spec contract in REVIEW_TEAM.md §Playbooks. Synthesizer
parity: enforce `findings[].check` citation; emit
`verdict.playbook_coverage`.

**Dependency:** Hermes team-mode (currently not implemented).

## What's NOT in this backlog

- **Anything plugin-side.** Plugin TODOs live in normal places —
  `plans/` for active plans, the project ROADMAP for sequencing,
  `platforms/claude-code-plugin/CHANGELOG.md` for the per-release
  record.
- **Framework spec changes.** Those go through GATE-SPEC; this file
  is platform-specific.
- **CHG governance.** Has its own track.

## How to read this file

When the plugin reaches a natural completion point (after Phase 4,
or when a user explicitly says "now let's catch up Hermes"):

1. Re-read each H-N item above. Some may have been overtaken by
   spec evolution and need refresh, not direct implementation.
2. For each item, **draft a new plan** (REVIEW-CALIBRATION-002-PLAN,
   SAGA-PARITY-001-PHASE-3-PLAN, etc.) using the current state of
   the plugin and the framework spec as the reference target.
3. Run the standard two-cycle plan review before opening the plan PR.
4. Apply the minimal-and-realistic plans rule — each Hermes plan
   should be sized to its specific objective, not "catch Hermes up
   on everything at once."

When new items emerge (i.e., a plugin feature lands and we want to
note that Hermes will need to catch up later):

1. Add a new H-N entry above with the same shape (Source / Plugin
   status / Substantive work / Dependency).
2. Update the "Last update" date in the header.

## Linked artifacts

- [`docs/PARITY.md`](../docs/PARITY.md) — current parity contract +
  what each platform implements today
- [`ROADMAP.md`](../ROADMAP.md) — overall project sequencing
- Plugin CHANGELOG: [`platforms/claude-code-plugin/CHANGELOG.md`](../platforms/claude-code-plugin/CHANGELOG.md)
- Hermes CHANGELOG: [`platforms/hermes/CHANGELOG.md`](../platforms/hermes/CHANGELOG.md)
- `framework/governance/REVIEW_SAGA.md` — the spec contract both
  platforms align to
