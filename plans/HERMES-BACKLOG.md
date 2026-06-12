# Hermes Backlog — deferred work pending plugin completion

| Field | Value |
|-------|-------|
| Status     | **DEFERRED** — pending completion of plugin-side work |
| Owner      | vladm3105 |
| Last update | 2026-06-11 |
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

### H-5 — LAYER-PLAYBOOKS-001 closing 6 layers (EARS/BDD/ADR/SPEC/TDD/IPLAN)

**Source:** plugin PRs EARS-RT-001 / BDD-RT-001 / ADR-RT-001 /
SPEC-RT-001 / TDD-RT-001 / IPLAN-RT-001 (plugin `0.8.0 → 0.14.0`).

H-4 above only covered BRD+PRD. After plugin landed playbook injection
across the remaining 6 layers (45 of 45 playbooks total, per the
LAYER-PLAYBOOKS-001 design), Hermes still has zero playbook injection
across any layer. Hermes catch-up here is per-layer + cumulative — and
requires the H-4 review-team plumbing to land first.

**Dependency:** H-4 (Hermes team-mode dispatch). H-5 is the per-layer
fan-out once H-4 is in place.

### H-6 — FRAMEWORK-CLEANUP-001 calibration deltas (PR-B heart)

**Source:** plugin PR #131 (CLEANUP-PR-B, framework `0.19.0` + plugin
`0.16.0`).

The "heart" of FRAMEWORK-CLEANUP-001 — review-quality calibration.
Three orthogonal items the Hermes review path must mirror:

- **No-findings rationale** — a lens returning `lens_score: 100`
  with `findings: []` MUST emit a `no_findings_rationale` field;
  synthesizer caps the lens at 95 on missing rationale
  (`STRUCTURE-RAT-001` advisory). Documented in REVIEW_TEAM.md
  §Operations.
- **Strip author self-claim before lens fan-out** — engines strip
  `*_ready_score` / `*_score` / `readiness_score` / `audit_score`
  from the artifact body before passing to each lens (anchor-effect
  fix).
- **Fixer-introduced regression detection** — synthesizer compares
  iter-N finding locations to iter-(N-1) Fixes Applied entries;
  sets `fixer_introduced: true`; caps affected lens at iter-(N-1)
  value; renders findings in a `## Regressions` audit-report section.

13 playbook files (6 × auditor + 7 × tech_lead) ship the
"No-findings rationale" section on the framework side already (spec
0.19.0); Hermes catches up by aligning its synthesizer + lens
dispatch.

**Dependency:** Hermes review-team plumbing (H-4).

### H-7 — FRAMEWORK-CLEANUP-001 spec/registry deltas (PR-C + PR-D)

**Source:** plugin PRs #130 (CLEANUP-PR-C, framework `0.18.0`) + #133
(CLEANUP-PR-D, framework `0.20.0`).

Spec changes the Hermes lint surface must mirror:

- **Iteration cap** — `quality_loop_max_iterations` knob in
  `ADAPTATION_SURFACE.yaml` (default 3, range 1-10);
  REVIEW_REMEDIATION_FLOW.md §Iteration cap. Plugin's saga driver
  reads it; Hermes's saga implementation must too.
- **`@threshold:` ID pattern** — `LAYER_REGISTRY.yaml`
  `id_patterns.threshold` regex
  (`^[A-Z]+\.\d{2,}\.[a-z_]+(?:\.[a-z0-9_]+)+$`). Plugin's
  `sdd_doc_lint` TH01 enforces it; Hermes's structural-lint floor
  must too.
- **TH-RES-001 (threshold-resolution gate)** — corpus-level lint
  rule that resolves every downstream `@threshold:` citation to a
  `full_id:` entry in the host PRD's `component_decomposition`
  section (PR-D item 16). Citation-driven: P2 on missing section,
  P1 on missing key.
- **`optional_downstream_slots`** — per-layer LAYER_REGISTRY field
  formalizing EARS's `@bdd:` slots as optional non-canonical
  navigation (PR-C item 14).
- **Element-ID exemption** — SPEC §5 + IPLAN §4 layer-local IDs
  formalized as MAY-not-MUST in ID_NAMING_STANDARDS.md (PR-C
  item 13).

**Dependency:** none (all spec; Hermes lint must align).

### H-8 — IPLAN sub-types (PR-E)

**Source:** plugin PR #132 (CLEANUP-PR-E, framework `0.19.1` + plugin
`0.16.1`).

`IPLAN-TEMPLATE.yaml` gains `subtype: code_build | deploy | combined`
field (default `combined`). 9 sections gain `_required_when_subtype:`
markers (4 code-build + 5 new deploy sections). `doc-iplan-audit`
SKILL gains subtype-aware Structural Checklist dispatch; 3 IPLAN
playbooks (operator / chaos_engineer / integration_lead) gain
`### Subtype awareness` subsection. Hermes must mirror the
subtype-aware section dispatch + the same playbook awareness.

**Dependency:** none (additive template field + backward-compat
default `combined`).

### H-9 — Harness + governance hygiene (PR-A + CLAUDE.md updates)

**Source:** plugin PR #129 (CLEANUP-PR-A, plugin `0.14.1`) + PR-B's
CLAUDE.md additions (PR #131).

- **Vendored DO-NOT-EDIT banners** — Hermes's vendored `sdd_doc_lint`
  - `saga_driver` mirrors should carry the same banners + `_VENDORED.md`
  README pattern that the plugin uses.
- **MD056 SKILL prompt fix** — `### Table-pipe escape` subsections
  in audit/fixer SKILL prompts; Hermes equivalents should ship the
  same prose addition.
- **`_required: false` honored by STRUCT01** — sdd_doc_lint exempts
  template sections marked `_required: false` from the
  required-section check (lands in PR-D); Hermes lint mirror must
  match.

**Dependency:** none (per-platform polish; safely additive).

### H-10 — CHG layer team-mode + playbook injection (CHG-RT-001)

**Source:** plugin PR #137 (CHG-RT-001, framework `0.20.1 → 0.21.0` +
plugin `0.17.1 → 0.18.0`).

CHG overlay brought to per-layer parity with the 8 SDD layers on the
plugin side: 6 new playbooks at `framework/playbooks/09_CHG/`; 3 CHG
SKILLs rewritten with team-mode + saga + Break-circuit + Content
Sub-Checks; saga driver `_LAYER_CREWS` gains `"09_CHG"`. Live cascade
against url-shortener converged to PASS @ iter 3 score 95.

**Substantive work for Hermes:**

- Add `chg` entry to `platforms/hermes/skills/persona_mappings.yaml`
  `review:` map covering the 6 CHG lenses (integration_lead / architect
  / chaos_engineer / operator / auditor / security_engineer)
- Run the Hermes equivalent of doc-chg-audit team-mode dispatch (the
  test `test_hermes_review_crews_cover_framework_crews` currently
  skips `CHG` per the `HERMES_DEFERRED_LAYERS` whitelist — when CHG is
  added to Hermes, remove `CHG` from that whitelist)
- Live verification: run Hermes against the same url-shortener
  `chg/test-change.md` seed; confirm CHG-01 propagation report
  enumerates the same expected downstream impacts as plugin-side

**Dependency:** none specific — Hermes catch-up can land independently
once H-4 (team-mode) + H-5 (playbook injection) prerequisites are in
place.

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
