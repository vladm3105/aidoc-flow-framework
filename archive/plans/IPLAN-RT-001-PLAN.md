# IPLAN-RT-001 Implementation Plan

> Combined plan + impl PR per established per-layer rollout pattern
> (mirrors EARS-RT-001 + BDD-RT-001 + ADR-RT-001 + SPEC-RT-001 + TDD-RT-001).
> **Final per-layer rollout** — closes the 8-layer team-mode + playbook
> sequence.

**Goal:** Wire team-mode fan-out into `doc-iplan-audit` + `doc-iplan-fixer`
SKILLs, add playbook injection, author 6 IPLAN playbooks, remove the
`@unittest.skip` on `test_playbook_coverage` (the closing cleanup), and
validate via live IPLAN cascade.

**Architecture:** Mechanical replication of the TDD-RT-001 pattern for
the IPLAN layer (Layer 8). Framework spec contract from LAYER-PLAYBOOKS-001
unchanged; only IPLAN-specific configuration + content lands. All
infrastructure defects from earlier per-layer work are resolved on main,
so this is expected to be the cleanest per-layer landing yet.

**Design authority:** `framework/governance/REVIEW_TEAM.md` §Playbooks +
`platforms/claude-code-plugin/skills/doc-tdd-audit/SKILL.md` (TDD-RT-001
template — freshest reference).

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | IPLAN-RT-001                                |
| Type           | combined plan + impl (per-layer rollout)    |
| Worktree       | `feat/iplan-rt-001` at `/opt/data/aidoc-flow/framework-iplan-rt-001/` |
| Depends on     | TRACE-RES-FIXUP-001 impl (PR #125, merged `90f37002`) — regenerated url-shortener corpus is the cascade target |
| Blocks         | Nothing — this is the **8/8 closing layer rollout**. After merge: LAYER-PLAYBOOKS-001 backlog is empty; only Hermes parity catch-up (HERMES-BACKLOG H-4) remains as a follow-on workstream |
| Scope closure  | Closes session memory tasks **#268** (IPLAN-RT-001) and **#258** (remove `@unittest.skip` from `test_playbook_coverage`) in one PR |
| Version impact | Framework PATCH `0.17.0 → 0.17.1` (IPLAN playbooks under existing §Playbooks artifact class) + plugin MINOR `0.13.1 → 0.14.0` (new layer wiring) |

---

## IPLAN crew (from `framework/governance/REVIEW_CREWS.yaml`)

```yaml
IPLAN:
  author: tech_lead
  # rationale: Chaos-only (8) — IPLAN is procedural deploy/rollback; threat
  # model lives upstream in ADR/SPEC. Chaos covers rollback/recovery scenarios.
  review: {tech_lead: 30, architect: 25, operator: 15, integration_lead: 12, auditor: 10, chaos_engineer: 8}
```

Sum: 100. **6 lenses** — same headcount as TDD but a different shape:

- **No `security_engineer`** — per the file comment, threat-model is
  upstream concern (ADR/SPEC); IPLAN is procedural deploy/rollback only.
- **New `integration_lead` lens** — appears only at the IPLAN layer.
  Focus: cross-system contract compatibility, dependency rollout order,
  feature-flag gating, backward-compatible API window. Distinct from
  `operator` (smoke/canary/observability) and `architect` (topology
  invariants).
- **Reduced `chaos_engineer` weight (8)** — IPLAN's chaos surface is
  narrower than TDD's (rollback & recovery, not generic fault injection).

## Lens → plugin agent mapping

| Lens | Weight | Agent | Note |
|---|---|---|---|
| `tech_lead` | 30 | `solutions-architect` | IPLAN author + lens; deploy-sequence reversibility focus |
| `architect` | 25 | `solutions-architect` | topology invariants from ADR/SPEC |
| `operator` | 15 | `devops-release-engineer` | smoke/canary/rollback observability |
| `integration_lead` | 12 | `solutions-architect` | cross-system contract compatibility (new lens) |
| `auditor` | 10 | `traceability-auditor` | upstream-trace + IPLAN-ID conformance |
| `chaos_engineer` | 8 | `chaos-engineer` | rollback dress rehearsal |

`solutions-architect` carries three lens roles at IPLAN (tech_lead +
architect + integration_lead) — confirmed by the lens→agent table in
`platforms/claude-code-plugin/skills/review-team/SKILL.md` which already
documents `architect, tech_lead, integration_lead → solutions-architect`.
The fan-out dispatches three separate subagent invocations with distinct
playbook briefs; the agent prompt distinguishes lens by the brief, not
by the subagent_type.

---

## File structure

### Modified

| Path | Change |
|---|---|
| `platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md` (270 → ~500 lines) | Add §Review Mode (team + single_pass), §Saga interaction, §Break-circuit policy, playbook injection step 3a + augmented step 4 |
| `platforms/claude-code-plugin/skills/doc-iplan-fixer/SKILL.md` (112 → ~300 lines) | Add §Remediate Mode (team + single_pass), §Saga interaction, §Break-circuit policy |
| `tests/conformance/test_playbook_coverage.py` | **Remove `@unittest.skip` line 35** (task #258 closing cleanup — all 45 playbooks now land) |
| `CHANGELOG.md` (root) | `[Unreleased]` entry for framework `0.17.0 → 0.17.1` + plugin `0.13.1 → 0.14.0` |
| `ROADMAP.md` | Shipped bullet (per-layer rollout sequence COMPLETE) |
| `plans/HANDOFF.md` | Dated narrative — IPLAN-RT-001 closes the 8-layer sequence |
| `docs/PARITY.md` | Layer Playbooks row title fixed from stale `(BRD/PRD/EARS)` to `(all 8 layers)`. (Row went stale across 5 prior per-layer PRs that landed EARS/BDD/ADR/SPEC/TDD playbooks without updating this title.) |
| `docs/TAGGING.md` | New rows for `framework/v0.17.1` + `claude-code-plugin/v0.14.0` |
| `framework/VERSION` | `0.17.0 → 0.17.1` (PATCH — IPLAN playbooks under existing §Playbooks) |
| `platforms/claude-code-plugin/VERSION` | `0.13.1 → 0.14.0` (MINOR — new layer wiring) |
| `tests/conformance/platforms/test_plugin_release_metadata.py` | Hardcoded `"0.17.0"` → `"0.17.1"` |

### Created

| Path | Lens / Weight |
|---|---|
| `framework/playbooks/08_IPLAN/tech_lead.md` | 30 |
| `framework/playbooks/08_IPLAN/architect.md` | 25 |
| `framework/playbooks/08_IPLAN/operator.md` | 15 |
| `framework/playbooks/08_IPLAN/integration_lead.md` | 12 |
| `framework/playbooks/08_IPLAN/auditor.md` | 10 |
| `framework/playbooks/08_IPLAN/chaos_engineer.md` | 8 |

---

## Per-lens playbook content (hybrid shape per REVIEW_TEAM.md §Playbooks; ~95-110 lines each)

**tech_lead (30, solutions-architect)** — Deploy-sequence reversibility lens (IPLAN author).

- C1: Every deploy step has a documented rollback step (paired). Missing → P1 citing C1.
- C2: Cutover decision criteria are explicit (named metric + threshold), not "use judgment". Missing → P1 citing C2.
- C3: Phase boundaries declare pre-conditions + post-conditions. Missing → P2 citing C3.
- C4: Time-bound gates (smoke window, canary duration, rollback SLA) carry concrete numbers. Missing → P2 citing C4.
- C5: State transitions between deploy phases are deterministic (no branching on "operator discretion"). Missing → P3 citing C5.

**architect (25, solutions-architect)** — Topology invariants lens.

- C1: IPLAN's deployment topology matches the ADR's documented topology. Drift → P1 citing C1.
- C2: No new infrastructure introduced at IPLAN that's absent from ADR/SPEC. Drift → P1 citing C2.
- C3: Component dependencies match SPEC's deployment graph. Mismatch → P2 citing C3.
- C4: Capacity / NFR references resolve to SPEC's NFR bounds. Missing → P2 citing C4.
- C5: Migration steps preserve invariants stated in ADR. Missing → P3 citing C5.

**operator (15, devops-release-engineer)** — Smoke / canary / observability lens.

- C1: Smoke tests defined for each cutover step (named, with pass criteria). Missing → P1 citing C1.
- C2: Canary metric thresholds explicit (latency, error rate, saturation). Missing → P2 citing C2.
- C3: Rollback procedure references SPEC-named one-way decisions. Missing → P2 citing C3.
- C4: Observability hooks present (deploy-event emit, version pin, dashboard URL). Missing → P3 citing C4.
- C5: On-call playbook / runbook update referenced. Missing → P3 citing C5.

**integration_lead (12, solutions-architect)** — Cross-system compatibility lens (new at IPLAN).

- C1: Cross-service contract versions explicitly pinned per cutover step. Missing → P1 citing C1.
- C2: Integration test gates run pre-cutover at each phase boundary. Missing → P2 citing C2.
- C3: Dependency rollout order reflects SPEC's component DAG (upstream first). Wrong order → P2 citing C3.
- C4: Feature-flag default state declared per flag. Missing → P3 citing C4.
- C5: Backward-compatible API window declared (how long old + new run side-by-side). Missing → P3 citing C5.

**auditor (10, traceability-auditor)** — Upstream-trace + IPLAN-ID conformance lens.

- C1: Every `@spec: SPEC.NN…` / `@tdd: TDD.NN…` tag resolves to an existing upstream element. Broken → P1 citing C1.
- C2: IPLAN step IDs conform to `IPLAN.NN.SS.xxxx` 4-hex content-hash pattern. Non-conformant → P1 citing C2.
- C3: Each row in the deployment-step matrix has a paired body step. Orphan → P2 citing C3.
- C4: Cumulative `@spec / @tdd` header at doc level resolves cleanly (necessary-upstream contract). Missing → P2 citing C4.
- C5: Cross-IPLAN `@iplan` references use correct form (dash for doc-level, dotted for element-level). Wrong form → P3 citing C5.

**chaos_engineer (8, chaos-engineer)** — Rollback dress-rehearsal lens.

- C1: Rollback exercised in a non-prod environment with realistic conditions (not just documented). Missing → P1 citing C1.
- C2: Recovery-time assertions reference SPEC's MTTR bound. Missing → P2 citing C2.
- C3: Failure-injection step exists in pre-cutover dress rehearsal. Missing → P2 citing C3.
- C4: Blast-radius reduction step declared (canary → partial → full). Missing → P3 citing C4.
- C5: Stop-the-world abort criteria documented (what triggers immediate rollback). Missing → P3 citing C5.

---

## Implementation sequence

### Task 1: Plan iterative review (≥ 2 cycles, mandatory, before PR)

- Pass 1 self-review against the codebase. Patch in place.
- Pass 2 re-review. Continue passes until one surfaces zero substantive
  gaps (MAJOR + MEDIUM).

### Task 2: Author 6 IPLAN playbooks

`framework/playbooks/08_IPLAN/{tech_lead,architect,operator,integration_lead,auditor,chaos_engineer}.md`.
Hybrid content shape; ~95-110 lines each. Frontmatter:
`layer: 08_IPLAN`, `lens: <name>`, `weight: <N>`, `agent: <name>`,
`framework_spec_version: "0.17.1"`.

### Task 3: Refactor `doc-iplan-audit/SKILL.md` (270 → ~500 lines)

Mirror TDD-RT-001's `doc-tdd-audit/SKILL.md`:

- Add §Review Mode (team + single_pass) with persona blackboard slot
  paths.
- Add §Saga interaction (saga.json lifecycle handling).
- Add §Break-circuit policy (PARTIAL_TIMEOUT / ESCALATED fallbacks).
- Augment Execution Contract (step 3a: playbook injection from
  `framework/playbooks/08_IPLAN/`; step 4: combined report includes
  per-lens findings and synthesizer coverage).

### Task 4: Refactor `doc-iplan-fixer/SKILL.md` (112 → ~300 lines)

Mirror TDD-RT-001's `doc-tdd-fixer/SKILL.md`:

- Add §Remediate Mode (team + single_pass) with per-lens validation.
- Add §Saga interaction.
- Add §Break-circuit policy.

### Task 5: Remove `@unittest.skip` from `test_playbook_coverage.py` (task #258 cleanup)

Delete `@unittest.skip("Phase E will land 45 playbooks — skip until then")`
at `tests/conformance/test_playbook_coverage.py:35`. The conformance suite
gains its 121st test once IPLAN's 6 playbooks land — total active count
should grow by 1.

### Task 6: Version bumps + docs of record

- `framework/VERSION` `0.17.0 → 0.17.1`.
- `platforms/claude-code-plugin/VERSION` `0.13.1 → 0.14.0`.
- `platforms/hermes/FRAMEWORK_SPEC_VERSION` `0.17.0 → 0.17.1`.
- `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` `0.17.0 → 0.17.1`.
- Run `scripts/sync-version-refs.sh` (auto-propagates the new version to
  `plugin.json`, `marketplace.json`, 52 × SKILL.md frontmatter, READMEs,
  `docs/SKILL_AUTHORING.md`, `docs/PARITY.md` current-state row, AND
  the `framework_spec_version` field in **all 45 playbook frontmatter
  files** (`framework/playbooks/<NN>_<LAYER>/*.md`) — extended by
  LAYER-PLAYBOOKS-001 Phase F Task 11). Bulk diff but mechanical;
  re-stages automatically.
- Run `tools/sync-plugin-framework.sh` (re-syncs framework bundle into
  `platforms/claude-code-plugin/framework/` mirror).
- Update `CHANGELOG.md` + `docs/TAGGING.md` (2 new rows) +
  `docs/PARITY.md` (correct stale Layer Playbooks row title) +
  `ROADMAP.md` (mark per-layer rollout sequence complete) +
  `plans/HANDOFF.md`.
- Update hardcoded version refs in
  `tests/conformance/platforms/test_plugin_release_metadata.py` (line 139:
  `"0.17.0"` → `"0.17.1"`).

### Task 7: Conformance + lint (cheap checks before the long cascade)

- `python3 -m unittest discover -s tests/conformance` — expect **121/121
  PASS** (1 new test active after removing the @unittest.skip).
- `python3 -m unittest discover -s tests/unit` — 43/43 PASS.
- `PYTHONPATH=platforms/claude-code-plugin python3 -m sdd_doc_lint examples/url-shortener/docs/`
  — 0 TRACE-RES-001 findings (unchanged from TRACE-RES-FIXUP-001).

These are cheap; run them before Task 8's live cascade so any obvious
regression is caught in seconds, not after a 30-90 min cascade run.

### Task 8: Live IPLAN cascade (acceptance)

- `bash tests/scripts/test-acceptance.sh url-shortener --live --phase=cascade --from-layer=iplan --to-layer=iplan`.
- Expect IPLAN-01 to generate against the regenerated SPEC-01/TDD-01
  upstream, audit via 6-lens fan-out, fixer applies remediation, saga
  converges in ≤ 3 iterations.
- **Pass criteria:** IPLAN-01 verdict `PASS` with `combined_status: PASS`
  and `content_score >= 90`; saga `CLOSED`; all 6 persona slots present
  at `.aidoc/review/08_IPLAN/IPLAN-01/{tech_lead,architect,operator,integration_lead,auditor,chaos_engineer}.json`.

### Task 9: Open combined plan + impl PR (only after Tasks 1-8 all green)

---

## Out of scope

- Hermes mirror catch-up — plugin-first; tracked in `plans/HERMES-BACKLOG.md`.
- IPLAN ↔ iplanic integration — separate concern; tracked in
  `plans/IPLAN-IPLANIC-DEFERRED.md`.
- Creating a dedicated `integration-lead.md` agent file — the
  `solutions-architect` agent prompt is general enough to carry the
  lens; revisit if cascade evidence shows the lens needs distinct
  scaffolding.
- Speculative second-IPLAN authoring (`IPLAN-02_*.md`) — single
  IPLAN per cascade per current pattern.

---

## Verification

| #  | Check | Expected |
| -- | ----- | -------- |
| 1 | `framework/playbooks/08_IPLAN/` (6 files exist, valid frontmatter) | PASS |
| 2 | Conformance `test_playbook_coverage` (after @unittest.skip removal) | PASS — all 45 playbooks present |
| 3 | Conformance full suite | **121/121 PASS** (**0 skipped** — the `test_every_crew_lens_has_a_playbook_file` skip is the only one on main; removing it leaves the suite fully active) |
| 4 | Unit suite | 43/43 PASS |
| 5 | Lint on examples/url-shortener/docs | 0 TRACE-RES-001 findings |
| 6a | Live IPLAN cascade — **primary success** | saga `CLOSED`, verdict `PASS`, `content_score >= 90` |
| 6b | Live IPLAN cascade — **acceptable fallback** | saga `PARTIAL_TIMEOUT` after iter-3, verdict `FAIL` with `content_score >= 87` and all 6 persona slots populated. Per the `[governance]` FRAMEWORK-TODO entry, this is acceptable; the deliverable is the artifact + saga lifecycle, not a particular numeric score |
| 7 | Pre-commit hooks (sync-version-refs + check-docs-updated) | PASS |

---

## Risks & rollback

| Risk | Mitigation |
| ---- | ---------- |
| `solutions-architect` carries three lens roles (tech_lead + architect + integration_lead) at IPLAN | This mapping is already documented in `review-team/SKILL.md`'s lens→agent table; not a new design. The playbook brief is lens-specific (5 checks tied to that lens's concerns only); agent prompt distinguishes lens by brief content, not subagent_type |
| Live cascade hits PARTIAL_TIMEOUT at MAX_ITERATIONS=3 | Per the new `[governance]` FRAMEWORK-TODO entry, that's acceptable behavior — the artifact + saga lifecycle is the deliverable. Re-run with `sdd-lifecycle resume` if needed |
| Removing `@unittest.skip` exposes a test_playbook_coverage gap not caught by static checks | Step 7 reruns full conformance before commit; gap surfaces locally not on CI |

**Rollback:** Single PR. `git revert <merge-sha>` restores the prior
state. IPLAN playbooks + SKILL refactors are additive; framework spec
PATCH is reversible.

---

## Review log

> Per CLAUDE.md §"Development workflow" item 2: ≥ 2 review cycles BEFORE
> PR. Each = *review → patch → re-review*. Continue until a pass surfaces
> zero substantive gaps.

### Pass 0 — initial draft

- **Date:** 2026-06-10T18:30:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against codebase

- **Date:** 2026-06-10T18:45:00Z
- **Method:** verify every claim in the draft against current main
  (`90f37002`, post-TRACE-RES-FIXUP-001). Spot-check existing patterns
  (TDD-RT-001 plan, REVIEW_TEAM playbook artifact class, lens-to-agent
  table in `review-team/SKILL.md`, current PARITY/ROADMAP state).
- **Findings (4 substantive — 0 MAJOR, 3 MEDIUM, 1 MINOR):**
  - **P1-1 (MEDIUM):** Plan's "Blocks: None" under-described the
    closure. This PR is the **8/8 closing layer rollout** AND it folds
    in task #258 (`@unittest.skip` removal). After merge, the
    LAYER-PLAYBOOKS-001 backlog is fully drained.
    *Patch:* Field reworded to "8/8 closing layer rollout"; new
    "Scope closure" field added explicitly listing tasks #268 + #258.
  - **P1-2 (MEDIUM):** `docs/PARITY.md` line 184 currently reads
    `Layer Playbooks (BRD/PRD/EARS) | ✅ active | ⏳ deferred`. Five
    prior per-layer PRs (EARS/BDD/ADR/SPEC/TDD-RT-001) left this row
    title stale. The plan said "extended to all 8 layers" without
    flagging that the row is actually being **corrected** from a long-
    stale state.
    *Patch:* File-structure row reworded to make the staleness explicit.
  - **P1-3 (MEDIUM):** Risk table called the integration_lead lens
    mapping "no dedicated agent" — implying ambiguity. Actually
    `review-team/SKILL.md` ALREADY documents
    `architect, tech_lead, integration_lead → solutions-architect`
    as a deliberate multi-lens-per-agent mapping. Not a new design;
    not a risk.
    *Patch:* Lens→Agent narrative cites the existing table; Risk row
    reworded to describe (not as risk) the documented multi-role
    mapping.
  - **P1-4 (MINOR):** Pass 0 / Pass 1 review log placeholder dates left
    as 2026-06-10T18:30/18:45 — fine; just confirming.
- **Cross-checks that came back clean:**
  - `tests/conformance/test_playbook_coverage.py:35` confirmed
    `@unittest.skip("Phase E will land 45 playbooks — skip until then")`
    ✓
  - `tests/conformance/platforms/test_plugin_release_metadata.py:139`
    has `"0.17.0"` hardcoded ✓ — will bump to `"0.17.1"`
  - `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` exists ✓ — author
    SKILL has a template to use
  - All 4 `doc-iplan-*` skills exist on disk ✓
  - `framework/playbooks/08_IPLAN/` directory NOT yet created ✓ —
    will be created by this PR
  - ROADMAP.md line 150 shows 11 playbooks landed; per-layer PRs from
    EARS through TDD have shipped 23 more (5 EARS + 6 BDD + 6 ADR +
    5 SPEC + 6 TDD); IPLAN-RT-001 adds the final 6, totaling 45 across
    all 8 layers (matches LAYER-PLAYBOOKS-001 target)
- **Net structural change:** 4 in-place clarifications. No new tasks
  or files added.
- **Status:** Patches folded in. Awaiting Pass 2.

### Pass 2 — re-review

- **Date:** 2026-06-10T19:00:00Z
- **Method:** re-read patched plan top to bottom; cross-check Pass 1
  patches for self-consistency; verify numeric claims against this
  session's prior cascade evidence.
- **Findings (3 substantive — 1 MAJOR, 2 MEDIUM):**
  - **P2-1 (MAJOR):** Verification row 3 said "121/121 PASS (**1
    skipped**)". After removing the `@unittest.skip` decorator (Task 5),
    the only skipped test on main is the one being un-skipped. So the
    post-impl state is **121/121 PASS (0 skipped)**. The "(1 skipped)"
    wording would mean the skip is still in place, which contradicts
    Task 5.
    *Patch:* Verification row 3 reworded to "121/121 PASS (0 skipped)"
    with the rationale inline.
  - **P2-2 (MEDIUM):** Verification row 6 (live cascade) required
    `content_score >= 90` for pass — but the Risks table acknowledges
    that PARTIAL_TIMEOUT at 89 (the silent-iter-3-ceiling scenario
    captured in the `[governance]` FRAMEWORK-TODO entry) is acceptable.
    The two contradicted each other.
    *Patch:* Split row 6 into 6a (primary success: CLOSED PASS 90+)
    and 6b (acceptable fallback: PARTIAL_TIMEOUT FAIL with score >= 87
    and all 6 slots populated). Aligns with the governance reality.
  - **P2-3 (MEDIUM):** Task 6 (Version bumps + docs of record) didn't
    mention that the `sync-version-refs.sh` hook also propagates to
    **all 45 playbook frontmatter files** (the extension landed in
    LAYER-PLAYBOOKS-001 Phase F Task 11). This makes the diff much
    larger than a naive reader would expect; future contributors might
    panic at the file count.
    *Patch:* Task 6 expanded — explicitly enumerates the propagation
    targets including the 45 playbook frontmatter sync; reassures
    that it's mechanical.
- **Cross-checks that came back clean:**
  - Lens content for IPLAN — 6 playbooks × 5 checks = 30 C-checks
    total. Structure mirrors TDD-RT-001 ✓
  - Per-lens content focus distinct (no overlap between operator and
    integration_lead) ✓
  - File-structure paths all valid ✓
  - Risk/rollback framing aligned with verification rows after P2-2
    patch ✓
- **Net structural change:** 3 in-place clarifications. Verification
  table grew by 1 row (6a + 6b split). No new tasks.
- **Status:** Patches folded in. Awaiting Pass 3 to confirm Pass 2
  patches did not introduce new inconsistencies.

### Pass 3 — re-review + convergence

- **Date:** 2026-06-10T19:15:00Z
- **Method:** verify Pass 2's numeric claims against this session's
  history; re-read patched plan for any new contradictions.
- **Findings (1 MINOR — 0 MAJOR, 0 MEDIUM):**
  - **P3-1 (MINOR):** Task 7 title was "Conformance + lint + sanity
    cascade" but body had no cascade step (cascade is Task 8). Title
    misleading.
    *Patch:* Title corrected to "Conformance + lint (cheap checks
    before the long cascade)"; trailing rationale added.
- **Cross-checks that came back clean:**
  - **Pass 2 "1 skipped on main" claim CONFIRMED**: ran conformance
    on this branch (pre-impl); only skipped test is
    `test_every_crew_lens_has_a_playbook_file` with reason "Phase E
    will land 45 playbooks — skip until then". Task 5 removes exactly
    that decorator. Post-impl will be 121/121 PASS (0 skipped). ✓
  - **Pass 2 "TDD-RT-001 scored 89" claim CONFIRMED**: commit `13e7de80`
    "evidence(tdd-rt-001): live cascade — content_score 89, 0 P0/P1,
    near-converge". Fallback threshold 87 in row 6b allows a 2-point
    buffer below the TDD-RT-001 actual, which is reasonable. ✓
  - File-structure paths all verified against current main + worktree
    state.
  - Verification row count: 7 logical checks (rows 1-7 with 6a+6b as
    one logical pair). Slight numbering awkwardness (1,2,3,4,5,6a,6b,7)
    but readable; not worth restructuring.
  - Task 1-9 ordering: review (1) → playbooks (2) → audit refactor (3)
    → fixer refactor (4) → skip removal (5) → version/docs (6) →
    cheap checks (7) → live cascade (8) → PR (9). Cheap-before-expensive
    ordering preserved. ✓
- **Net structural change:** 1 line-level edit (Task 7 title +
  rationale).
- **Verdict: CONVERGENCE.** 0 MAJOR + 0 MEDIUM findings; only 1 MINOR
  cosmetic patch. Plan is READY-FOR-PR per CLAUDE.md
  §"Development workflow" item 2.

**Convergence trend:**

| Pass | Found | MAJOR | MED | MIN |
|---|---|---|---|---|
| 1 | 4 | 0 | 3 | 1 |
| 2 | 3 | **1** | 2 | 0 |
| 3 | 1 | **0** | **0** | 1 |

Pass 2 caught the most consequential finding (the verification-row /
Task-5 internal contradiction). Pass 3 surfaced only a cosmetic title
issue, confirming convergence.
