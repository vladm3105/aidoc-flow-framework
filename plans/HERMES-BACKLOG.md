# Hermes Backlog — deferred work pending plugin completion

| Field | Value |
|-------|-------|
| Status     | **ARC UNDERWAY** — Phase 1 shipped (saga conformance); playbook injection is the load-bearing next gap |
| Owner      | vladm3105 |
| Last update | 2026-07-02 |
| Policy     | **Plugin-first development.** Hermes work is deferred until the corresponding plugin functionality is complete and verified end-to-end. This is the single source of truth for "what Hermes still needs to catch up on." |

> **⚠️ CORRECTED ASSESSMENT (2026-07-02, D-0045) — read before implementing any
> H-item below.** An evidence-backed re-assessment found this backlog's central
> premise **wrong**: **Hermes already has team-mode** (a working saga orchestrator
> with parallel per-persona fan-out — `saga_orchestrator.py:526`; crews reconciled to
> `REVIEW_CREWS.yaml` — `review_scoring.py:54`; MCP-wired `sdd_review` `saga_parallel`
> mode). H-4's "team-mode not implemented" is **FALSE**. And the **entire 0.32.x arc
> (D-0038…D-0044) is AUTO-SATISFIED** for Hermes via its byte-identical vendored
> `sdd_doc_lint` + shared `framework/layers/` templates — none needs Hermes-native
> code. The **real gap is older engine debt: playbook injection + saga completeness.**
> Re-sequenced (see `plans/HERMES-PARITY-PHASE-1-PLAN.md`):
>
> | Phase | Scope | Status |
> |-------|-------|--------|
> | 1 | saga state-machine conformance (`PARTIAL_TIMEOUT`) + enforced `test_saga_lifecycle_parity.py` | **✅ shipped** — partial H-1 (table); no Hermes bump |
> | 1b | orchestrator break-circuit *exercise* + resume (rest of H-1); `quality_loop_max_iterations` (H-7 knob) | pending |
> | 2 | **playbook injection** for BRD+PRD (H-4) — the load-bearing gap | **✅ shipped** (`hermes/v0.4.0`, D-0046) — H-4 CLOSED for BRD+PRD; H-2/H-6 fold into Phase 3 |
> | 3 | 8-layer coverage (H-5, already delivered by Phase 2 — verified) + CHG crew (H-10) | **✅ shipped** (`hermes/v0.5.0`, D-0047) — H-5 CLOSED (all 8 lifecycle layers); H-10 crew-map parity CLOSED; live CHG saga = follow-on |
> | 3b | real saga-journal conformance + `09_CHG` schema enum + live CHG (H-12) | **✅ shipped** (`hermes/v0.5.1` + framework `0.32.7`, D-0048) — H-12 CLOSED; real journals conform; live CHG sanctioned |
> | 4 (opt) | `sdd-orchestrator` agent-skill v3.2 modernization (H-11) | pending |
>
> **Auto-satisfied (no action):** H-3 (dormant), H-7 lint rows / H-8 / H-9 lint+template
> rows, and all of D-0038…D-0044 — Hermes gets these via vendored lint + shared
> templates. The H-N entries below are retained as historical detail; the phase table
> above is the live sequencing.

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

### H-12 — Hermes real saga journals don't conform to `saga.schema.json` (fixtures mask it) — ✅ CLOSED (2026-07-03, D-0048, framework 0.32.7 + hermes 0.5.1)

**Status:** CLOSED. `SagaRunState` gained the 4 defaulted fields; `saga_journal.py`
records schema-shaped transitions (run seed + each successful status/branch change);
the orchestrator derives `layer` from the required `doc_type` via
`normalize_layer(layer or doc_type)` (F1 — not the optional `--layer`); `09_CHG`
added to the schema enum; new `SagaRealJournalConformance` validates a **real**
journal (lifecycle + `--layer`-omitted + CHG). This also closed the "live CHG saga"
follow-on (a real CHG journal now validates). See D-0048.

**Source:** discovered 2026-07-03 while grounding the "live CHG saga" follow-on
after HERMES-PARITY-PHASE-3 (#234).

**Finding (evidence-backed):** a **real** Hermes saga journal (serialized from
`SagaRunState`, `platforms/hermes/src/mcp_server/review/saga_models.py`) is
**missing 4 `saga.schema.json`-required fields**: `artifact_id`, `layer`,
`iteration`, `transitions`. Verified by running `run_project_review_build_saga`
end-to-end and dumping `journal_path` — keys were
`{review_run_id, document_path, document_fingerprint, personas_requested, status,
created_at, updated_at, retry_count, branches, compensation_actions}`. The
`tests/conformance/test_saga_lifecycle_parity.py` guard (HERMES-PARITY-PHASE-1)
only validates **hand-authored fixtures** (`fixtures/saga/hermes_BRD-01_saga.json`,
which were written *with* those fields) — so the "both platforms' saga journals
conform to the shared schema" parity claim is **aspirational for Hermes**, not
enforced against real output.

**Fix shape:** add `artifact_id` / `layer` / `iteration` to `SagaRunState` (populate
from the saga call's `layer` + extracted doc id) and serialize the accumulated
`transitions` into the journal; add a conformance/integration test that validates a
**real** Hermes journal (not a fixture) against `saga.schema.json`. This also
naturally sanctions CHG (a real CHG journal would carry `layer: "09_CHG"`, which
then needs `09_CHG` added to the schema enum — a `framework/` change). Moderate
(Hermes engine + a framework schema addition).

**Related — "live CHG saga" is a NEAR-NO-OP:** CHG review already runs end-to-end
today (verified: `saga_status=CLOSED`, uncited findings discarded, `playbook_coverage
{C1:1}`) because the injection path is layer-agnostic (Phase 2) and CHG crew parity
landed in Phase 3 (#234). The only thing "live CHG" adds beyond H-12 is documenting
`sdd_review doc_type=chg` as a sanctioned target. Fold into H-12.

**Dependency:** none. Independent of the other H-items. Higher value than the
originally-planned "live CHG saga" (which grounding showed unnecessary).

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

### H-6 — FRAMEWORK-CLEANUP-001 calibration deltas (PR-B heart) — ⏳ PARTIAL (6.1+6.2 CLOSED 2026-07-04, D-0049, hermes 0.6.0; 6.3 blocked)

**Status:** H-6.1 (no-findings rationale cap) + H-6.2 (strip author self-claim)
**CLOSED** via HERMES-REVIEW-CALIBRATION (D-0049, `hermes/v0.6.0`) — consumer-side
enforcement, no framework change. H-6.3 (fixer-introduced regression detection)
**remains BLOCKED**: it needs an iter-N vs iter-(N-1) comparison and Hermes's saga is
single-pass (`iteration=1`); it belongs to a future Hermes multi-iteration
review-loop initiative, not this arc.

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

### H-11 — sdd-orchestrator agent-skill v3.2-era modernization (legacy-sdd-depth cleanup origin)

**Source:** legacy-sdd-depth cleanup PR (2026-06-12) — user-surfaced
legacy bug: the v3.2-era `sdd_depth: lite | standard | full` tiers had
survived in `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/`
after the framework moved to the single-path adaptive-loop model
(MVP → PROD → New MVP → Updated PROD). The legacy-sdd-depth PR removed
the `sdd_depth` references from `sdd_config.yaml` + `root-docs/README.md`

- added this entry. The orchestrator's broader v3.2-era worldview is
deeper than this cleanup touched.

**Substantive work for Hermes** (beyond the depth removal):

- Modernize the orchestrator's persona model — the skill still
  references "15 specialized review personas dispatched as parallel
  subagents" from the v3.2 era. The current framework uses the closed
  persona set in `REVIEW_CREWS.yaml` with per-layer crews of 5-6
  lenses + per-lens playbooks at `framework/playbooks/<NN>_<LAYER>/`.
- Cross-link the LAYER-PLAYBOOKS-001 contract.
- Replace `sdd-review-personas` related-skill reference with the
  current crew + playbook contract.
- Update governance docs under the orchestrator's `governance/` for
  the same v3.2-era anachronisms.
- Live verification — confirm a Hermes user invoking
  `sdd-orchestrator` against url-shortener follows the current 8-layer
  path.

**Dependency:** none specific. Independent of H-1..H-10. Can land
incrementally.

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
