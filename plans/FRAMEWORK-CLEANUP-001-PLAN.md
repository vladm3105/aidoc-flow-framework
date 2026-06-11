# FRAMEWORK-CLEANUP-001 — Orchestration Plan

> Multi-PR cleanup workstream draining `plans/FRAMEWORK-TODO.md` (17 open
> items as of 2026-06-11). This is an **orchestration plan**: the catalogue
> of issues, the grouping into PRs, the dependency sequence, and the
> per-cluster done criteria. Each child PR will get its own
> `plans/<NAME>-PLAN.md` with implementation details when it begins.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | FRAMEWORK-CLEANUP-001                       |
| Type           | orchestration (no impl in this PR)          |
| Worktree       | `feat/framework-cleanup-001` at `/opt/data/aidoc-flow/framework-cleanup-001/` |
| Depends on     | LAYER-PLAYBOOKS-001 closure (PR #127 `c56c386f`); FRAMEWORK-FEEDBACK-LOG-001 (PR #124) Tier-2 pipeline |
| Blocks         | Nothing — this is itself the drain workstream |
| Scope          | 17 open items in `plans/FRAMEWORK-TODO.md` grouped into 5 child PRs (PR-A through PR-E) |
| Status         | DRAFT — 2026-06-11 |

## Why this plan exists

After the LAYER-PLAYBOOKS-001 closure (8/8 layers, 45 playbooks), an
example-driven review of `examples/url-shortener/docs/` surfaced 9 new
framework-improvement items beyond the 8 already on `plans/FRAMEWORK-TODO.md`.
17 total open items now form a substantial backlog. Without an orchestration
plan, the items risk being either (a) picked off ad hoc and losing
dependency order, or (b) bundled into one over-scoped mega-PR.

This plan **triages, clusters, sequences**. It is the index for the
sub-plans, not the design for them.

## Triage — all 17 open items

Tag legend:

- `[harness]` — `tests/scripts/test-acceptance.sh` / cascade flow
- `[lint]` — `sdd_doc_lint` rule
- `[skill]` — a plugin SKILL contradicts spec or has a bug
- `[playbook]` — `framework/playbooks/<layer>/<lens>.md` calibration
- `[template]` — `framework/layers/<NN>_<X>/*-TEMPLATE.yaml` shape
- `[registry]` — `framework/registry/LAYER_REGISTRY.yaml`
- `[gate]` — new validation gate between layers
- `[saga]` — `framework/governance/REVIEW_SAGA.md` lifecycle
- `[plan-review]` — verified-planning skill
- `[governance]` — `framework/governance/DOC_GOVERNANCE_CORE.md` principles

| # | Tag | Title (short) | Priority | Cluster |
|---|---|---|---|---|
| 1 | `[harness]` | `--skip-lint-smoke` flag missing | MED | PR-A |
| 2 | `[harness]` | Tree-safety + pre-cleanup needs `--force` | LOW (doc only) | PR-A |
| 3 | `[lint]` | `sync-vendored.sh` vs `sync-plugin-framework.sh` confusion | MED | PR-A |
| 4 | `[skill]` | Auditor + fixer SKILLs emit unescaped `\|` in code spans (MD056) | MED | PR-A |
| 5 | `[plan-review]` | Plan reviews must cross-check example corpus | MED | PR-B |
| 6 | `[plan-review]` | Codify minimum-pass count by plan-type | LOW (advisory) | PR-B |
| 7 | `[skill]` | doc-tdd auditor C4 inter-section consistency | LOW (investigate) | PR-B |
| 8 | `[playbook]` | Auditor + tech_lead lens calibration (convergence theater) | **HIGH** | PR-B |
| 9 | `[skill]` | doc-*-audit strip self-claimed scores | MED | PR-B |
| 10 | `[saga]` | `fixer_introduced_finding` tag | MED | PR-B |
| 11 | `[governance]` | Iteration cap impl-bound, not spec-bound | LOW (spec doc) | PR-C |
| 12 | `[registry]` | `@threshold:` 3-segment pattern not in registry | MED | PR-C |
| 13 | `[template]` | SPEC + IPLAN element IDs codify or exempt | LOW (doc) | PR-C |
| 14 | `[template]` | EARS `@bdd:` downstream slots cleanup | MED | PR-C |
| 15 | `[gate]` | Component-decomposition gate PRD↔ADR | **HIGH** (new gate) | PR-D |
| 16 | `[gate]` | Threshold-binding gate before BDD/TDD PASS | **HIGH** (new gate) | PR-D |
| 17 | `[template]` | IPLAN sub-types (code-build vs deploy) | MED | PR-E |

## Cluster design — 5 child PRs

### PR-A — Harness + lint workflow hygiene (4 items, smallest, ships first)

**Theme:** plumbing fixes; no spec change.

**Items:** #1, #2, #3, #4.

**Scope:**

- Add `--skip-lint-smoke` flag to `tests/scripts/test-acceptance.sh` (closes item 1, retires the `SDD_LINT_SKIP_TRACE_RES=1` pattern).
- Document the cleanup-then-`--force` pattern in `tests/ACCEPTANCE.md` or surface in the harness output when tree-safety FAILs after `rm -rf` (closes item 2).
- Consolidate `sync-vendored.sh` + `sync-plugin-framework.sh` into one sync-direction-aware script; or add `DO NOT EDIT — synced from canonical` banner to each vendored module (closes item 3).
- Patch audit + fixer SKILL prompts to escape `|` inside code spans within markdown table cells; or move shell-pipe content out of cells (closes item 4 — currently masked by `examples/<*>/.aidoc/` markdownlint exclude).

**Touches:** `tests/scripts/test-acceptance.sh`, `tests/ACCEPTANCE.md`, `tools/sync-*.sh`, vendored modules' top-of-file comments, audit/fixer SKILL prompts.

**Version impact (floor):** plugin PATCH minimum (`0.14.0 → 0.14.1`); no framework change expected (harness + SKILL prompts only). Exact arithmetic finalized in child plan.

**Verification:** existing cascade re-runs cleanly; conformance unchanged.

**Done criteria:** all 4 items move to Closed with merge SHA.

---

### PR-B — Review-quality calibration (6 items, the heart of the cleanup)

**Theme:** audit honesty + saga lifecycle. **Highest-impact PR** in this workstream.

**Items:** #5, #6, #7, #8, #9, #10.

**Scope:**

- **Playbook recalibration** (item 8 — HIGH priority): refresh `framework/playbooks/<layer>/auditor.md` (8 files) and `tech_lead.md` (where applicable) with falsifiable checks that prevent 100/0-findings rubber-stamping. Principle: a lens returning `lens_score: 100` with `findings: []` must accompany the persona-output record with a `no_findings_rationale` field naming at least one section where the lens *did* examine and explicitly cleared (e.g. "§5 fail-closed rule type-completeness verified against SPEC §3 Protocol"). Synthesizer treats a missing rationale as a structural error and caps the lens at 95. Threshold N (lines-per-finding) deferred to child plan — surveyed across the 7-layer cascade history.
- **doc-tdd C4 investigation** (item 7): focused diagnostic on TDD-01's §1 line 30 finding from PR #122; decide whether C4 is the right gate or whether the auditor needs tighter section-consistency checking. Outcome may close as wontfix or update doc-tdd-audit.
- **Strip self-claimed scores from artifact** (item 9): `doc-*-audit/SKILL.md` step prepares lens brief; strip fields like `*_ready_score`, `prd_score`, etc. from the artifact text before lens fan-out. Document stripped-field list in `REVIEW_TEAM.md` §Operations.
- **Plan-review cross-check example corpus** (item 5): update verified-planning skill so plans changing lint rules / @-tag semantics / playbook content require a `python3 -m sdd_doc_lint examples/<NAME>/docs/` Pass-N smoke run before merge. Codify as a checklist step.
- **Minimum-pass-count-by-plan-type guidance** (item 6): note in verified-planning skill that framework-level / cross-cutting plans typically need 4-5 cycles; per-layer rollout plans converge in 2. Advisory only.
- **`fixer_introduced_finding` saga tag** (item 10): extend `REVIEW_SAGA.md` schema + `saga.schema.json` with a tag on iter-N findings whose location matches a iter-(N-1) Fixes Applied row. Surface in audit report `## Regressions` (new section in audit report format). Coordinate with plugin auditor/fixer SKILLs.

**Touches:** `framework/playbooks/<layer>/auditor.md` + `tech_lead.md` (up to 16 files), `framework/governance/REVIEW_SAGA.md`, `framework/governance/saga.schema.json`, `framework/governance/REVIEW_TEAM.md`, plugin `doc-*-audit/SKILL.md` (8 files), `tests/conformance/` (regression tests for the new schema + scoring).

**Version impact (floor):** framework MINOR minimum (`0.17.1 → 0.18.0` if new saga schema field; PATCH if only playbook content refresh); plugin MINOR (`0.14.1 → 0.15.0` for SKILL spec-strip changes). Exact arithmetic finalized in child plan.

**Verification:** re-run url-shortener cascade end-to-end with the recalibrated playbooks; expect score distribution to shift away from 100s on auditor/tech_lead lenses; expect any fixer-introduced regression to surface in audit `## Regressions`. Conformance + unit suites green.

**Done criteria:** all 6 items move to Closed with merge SHA; the cascade re-run shows non-100 scores on auditor/tech_lead for at least 4 of 7 layers (proving the calibration bites).

**Risks:** the recalibration may push some layers into PARTIAL_TIMEOUT at iter-3 (because more findings now block iter-2 convergence). Mitigation: accept PARTIAL_TIMEOUT as a valid outcome per the governance entry; the artifact + saga is still the deliverable.

---

### PR-C — Spec/registry/template hygiene (4 items)

**Theme:** spec-doc clarifications + registry pattern + small template tweaks.

**Items:** #11, #12, #13, #14.

**Scope:**

- **Iteration cap to spec** (item 11): elevate `MAX_ITERATIONS=3` from `tools/saga_driver.py:125` to `framework/governance/REVIEW_REMEDIATION_FLOW.md` §The quality loop. Add a `quality_loop.max_iterations` knob in `framework/governance/ADAPTATION_SURFACE.yaml`. Default 3; document override path. Plugin's `saga_driver.py` reads the knob.
- **Threshold ID pattern in registry** (item 12): add `threshold` ID pattern to `LAYER_REGISTRY.yaml` `id_patterns:` (3-segment `TYPE.NN.<category>`). Extend `sdd_doc_lint` to validate the namespace separately from element IDs. Coordinates with PR-D's threshold-binding gate.
- **SPEC + IPLAN element IDs codify** (item 13): decide whether SPEC §5 rules + IPLAN §4 contracts must carry `SPEC.NN.SS.xxxx` / `IPLAN.NN.SS.xxxx` IDs. Either (a) require via template + auditor, or (b) document deliberate exemption in `ID_NAMING_STANDARDS.md`. Recommend (b) — exempt + document, since the upstream-trace flow already binds SPEC/IPLAN to upstream IDs.
- **EARS `@bdd:` downstream slot cleanup** (item 14): drop per-line `@bdd: BDD-01` slots from `EARS-TEMPLATE.yaml`; rely on BDD's reverse `@ears:` tags for the trace. Updates EARS author SKILL + auditor to stop generating/expecting the slot.

**Touches:** `framework/governance/REVIEW_REMEDIATION_FLOW.md`, `framework/governance/ADAPTATION_SURFACE.yaml`, `framework/registry/LAYER_REGISTRY.yaml`, `framework/governance/ID_NAMING_STANDARDS.md`, `framework/layers/03_EARS/EARS-TEMPLATE.yaml`, `tools/sdd_doc_lint/__init__.py` (threshold pattern), `tools/saga_driver.py` (read iteration knob), `platforms/{hermes,claude-code-plugin}/skills/doc-ears-*`.

**Version impact (floor):** framework MINOR minimum (registry shape change + new governance principle); plugin MINOR. Exact arithmetic finalized in child plan; the version arithmetic depends on whether PR-B or PR-C ships first.

**Verification:** conformance suite extended with threshold-pattern regex tests + iteration-cap-override tests. Live EARS cascade re-run shows no `@bdd:` slot emission.

**Done criteria:** all 4 items move to Closed.

---

### PR-D — Component-decomposition + threshold-binding gates (2 items, big design)

**Theme:** two new validation gates between layers. **Substantial design work** — possibly warrants its own brainstorming session before plan.

**Items:** #15, #16.

**Scope:**

- **Component-decomposition gate** (item 15): **default approach** — extend `PRD-TEMPLATE.yaml` with a required `§ scope_this_cycle` subsection declaring which containers from PRD §9 get ADRs this cycle (which deferred to future cycles, with rationale). MINOR framework change; no new layer. ADR-author SKILL reads the section; ADR-auditor verifies scope matches. **Alternative considered**: a new artifact class `framework/layers/02b_DECOMP/` (9-layer flow) — but that's a MAJOR spec change touching 45 playbooks + conformance tests + ID_NAMING_STANDARDS + REPO_STRUCTURE. **Recommend the subsection approach** for this PR; bookmark the 02b layer idea for a future MAJOR if subsection ergonomics prove insufficient.
- **Threshold-binding gate** (item 16): extend `sdd_doc_lint` with `THRESHOLD-RES-001` rule (mirror of TRACE-RES-001 for threshold keys). Every `@threshold:KEY` citation must resolve to a numeric-bound value in the host doc; unbound thresholds fire P1 at BDD/TDD audit. Coordinates with PR-C's threshold ID pattern (PR-C must merge first).

**Touches:** `framework/layers/02_PRD/PRD-TEMPLATE.yaml` (subsection), `framework/registry/LAYER_REGISTRY.yaml`, `tools/sdd_doc_lint/__init__.py` (THRESHOLD-RES-001 rule), 4 layer auditor SKILLs (BDD/TDD enforce threshold-bind; ADR enforces decomp-scope), `REVIEW_TEAM.md` §Operations.

**Version impact:** framework MINOR (default subsection approach); plugin MINOR. Design-dependent — finalized in child plan.

**Verification:** url-shortener corpus re-cascade: PRD-01 must declare scope; ADR-01 must pass scope check; BDD/TDD must fail audit on unbound thresholds (7 of 11 thresholds in current corpus).

**Done criteria:** both items move to Closed; the url-shortener corpus exposes its scope-cliff explicitly + 7 unbound-threshold placeholders surface as findings.

**Risks:**

- Default (PRD subsection) is MINOR but the §scope_this_cycle field becomes a mandatory part of every future PRD; existing PRDs need backfill. Mitigation: ADR auditor only checks the field if it exists (graceful fallback for legacy PRDs); url-shortener PRD gets backfill in PR-D itself.
- THRESHOLD-RES-001 rule may surface many findings in legacy corpora (7 unbound in url-shortener already). Mitigation: same env-var bypass pattern used by TRACE-RES-001 (`SDD_LINT_SKIP_THRESHOLD_RES=1`) during migration; remove after corpora regen.
- Alternative 02b_DECOMP layer needs user approval and a precursor design-doc PR before plan-drafting. **Do NOT default to this**; needs explicit user opt-in.

**Recommendation:** brainstorm subsection-shape with the user BEFORE drafting the impl plan; confirm subsection approach is acceptable; if user prefers the 02b layer, escalate to a precursor design PR.

---

### PR-E — IPLAN sub-types (code-build vs deploy) (1 item)

**Theme:** IPLAN template variant + auditor section-set dispatch.

**Items:** #17.

**Scope:**

- Extend `IPLAN-TEMPLATE.yaml` with `subtype: code_build | deploy | combined`.
- Deploy IPLANs gate on rollback/smoke/canary/observability sections; code-build IPLANs exempt.
- `doc-iplan-audit/SKILL.md` selects audit section set by subtype.
- Update `IPLAN-RT-001` playbooks (`framework/playbooks/08_IPLAN/operator.md` + `chaos_engineer.md`) to dispatch checks conditional on subtype.

**Touches:** `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`, `framework/playbooks/08_IPLAN/{operator,chaos_engineer,integration_lead}.md`, `platforms/claude-code-plugin/skills/doc-iplan-audit/SKILL.md`.

**Version impact (floor):** framework PATCH minimum (template subtype field is additive) or MINOR if subtype changes IPLAN's required-section set; plugin PATCH. Exact arithmetic finalized in child plan.

**Verification:** new test in `tests/conformance/` covers the three subtype variants. Live IPLAN cascade with `subtype: deploy` exposes the deploy-only gates.

**Done criteria:** item 17 moves to Closed; url-shortener's IPLAN-01 explicitly marked `subtype: code_build` (which is what it is); a hypothetical deploy-IPLAN would be gated on the new section set.

---

## PR sequence + dependencies

```
PR-A (harness/lint hygiene)         ← independent; ships first
PR-C (spec/registry hygiene)        ← independent; ships parallel with PR-A
PR-B (review-quality calibration)   ← independent of A+C; ships after either
PR-D (decomp + threshold gates)     ← REQUIRES PR-C (threshold ID pattern)
PR-E (IPLAN subtypes)               ← independent; ships any time (weak benefit from PR-B's recalibrated playbooks but no hard dependency)
```

**Recommended order:** PR-A → PR-C → PR-B → PR-D → PR-E. Each PR is independently testable + revertible; the master plan ensures dependency-correct sequencing.

## Child PR naming convention

Branch names: `feat/cleanup-pr-{a|b|c|d|e}-<theme-slug>`. Concrete branches:

- `feat/cleanup-pr-a-harness-lint-hygiene`
- `feat/cleanup-pr-b-review-calibration`
- `feat/cleanup-pr-c-spec-registry-hygiene`
- `feat/cleanup-pr-d-decomp-threshold-gates`
- `feat/cleanup-pr-e-iplan-subtypes`

Each child plan: `plans/CLEANUP-PR-{A..E}-<slug>-PLAN.md`. Each gets its own 2-cycle review per CLAUDE.md.

## Out of scope

- Hermes parity catch-up — tracked in `plans/HERMES-BACKLOG.md` (H-4).
- New layer additions beyond IPLAN subtypes (item 17).
- Sub-framework registry changes (UCX/gov/kb per CLAUDE.md user-global) — separate concern.
- The `[skill]` doc-tdd C4 investigation (item 7) may close as wontfix during PR-B if the diagnostic shows no real issue.

## Per-PR done criteria summary

| PR | Items | Verification gate |
|----|-------|-------------------|
| PR-A | 1-4 | Cascade re-runs cleanly; existing conformance unchanged |
| PR-B | 5-10 | Live cascade re-run; auditor/tech_lead scores non-100 on ≥4 of 7 layers; `## Regressions` surfaces in any layer where fixer-introduced finding occurs |
| PR-C | 11-14 | Conformance extended; EARS cascade emits no `@bdd:` slots |
| PR-D | 15-16 | Decomp artifact authored; threshold-bind P1s surface on url-shortener |
| PR-E | 17 | IPLAN subtype dispatch works; conformance covers 3 variants |

## Overall workstream gate

FRAMEWORK-CLEANUP-001 is **complete** when:

1. All 17 items in `plans/FRAMEWORK-TODO.md` are in **Closed** with merge SHAs.
2. A fresh url-shortener cascade end-to-end produces:
   - Audit reports with non-100 scores on auditor + tech_lead lenses for ≥ 4 layers (proves PR-B calibration bites).
   - Decomp artifact present at PRD↔ADR boundary (proves PR-D shipped).
   - Threshold-bound numerics across all 11 keys (proves PR-D threshold gate bites).
   - IPLAN-01 explicitly declares `subtype` (proves PR-E shipped).
3. Conformance + unit suites green.
4. `plans/HANDOFF.md` updated to reflect "LAYER-PLAYBOOKS-001 + FRAMEWORK-CLEANUP-001 closed; next: Hermes parity catch-up".

## Notes on size + minimal-and-realistic

This orchestration plan is **deliberately the only orchestration document for the 17-item drain**. Each child PR (A through E) will get its own focused plan when its branch opens — sized to that PR's items only, not duplicating this index. Per CLAUDE.md "minimal-and-realistic": this plan is the catalog + sequence, not pre-design for each cluster.

Some items (#2, #6, #7, #11, #13) are LOW-priority and could close as wontfix-with-rationale during their cluster's plan-draft phase. The triage column above marks them so the cluster owner knows.

## Review log

> Per CLAUDE.md §"Development workflow" item 2: ≥ 2 review cycles BEFORE PR.

### Pass 0 — initial draft

- **Date:** 2026-06-11T<HH:MM>:00Z
- **Status:** SUPERSEDED by Pass 1.

### Pass 1 — self-review against TODO state + dependencies

- **Date:** 2026-06-11T19:30:00Z
- **Method:** verify the 17-item count against actual `plans/FRAMEWORK-TODO.md`
  state (post-rebuild); verify cluster→item mapping is exhaustive; verify
  dependency chain (PR-D depends on PR-C) holds; cross-check version-impact
  arithmetic against current main (framework 0.17.1 / plugin 0.14.0).
- **Findings (5 substantive — 0 MAJOR, 4 MEDIUM, 1 MINOR):**
  - **P1-1 (MEDIUM):** Initial draft had a workflow bug — appending the 9
    new entries via `cat >>` placed them BELOW `## Closed` section. Fixed
    by rebuilding the TODO file with sed slicing + manual re-insertion of
    MD056 entry (which the slice dropped).
    *Patch:* TODO file now correctly shows 17 Open + 1 Closed. Plan
    counts unchanged (the 17 figure was correct in intent; the file
    state needed catching up).
  - **P1-2 (MEDIUM):** Version-impact arithmetic was speculative — chained
    bumps from 0.17.1 → 0.18.0 → 0.19.0 across PRs assumes each PR
    triggers MINOR. But PR-A is harness/lint hygiene with no spec change
    (plugin PATCH); PR-C's iteration-cap-to-spec IS a MINOR but PR-B's
    playbook content refresh could be PATCH if no new schema. Concrete
    arithmetic depends on per-PR design.
    *Patch:* Version impact column in each PR section now flagged with
    "design-dependent — finalized in child plan"; only the floors are
    stated.
  - **P1-3 (MEDIUM):** PR-D's "potentially new framework/layers/02b_DECOMP/
    directory" introduces a 9-layer flow which would be a MAJOR framework
    spec change AND breaks the 8-layer assumption baked into 45 playbooks,
    conformance tests, ID_NAMING_STANDARDS, REPO_STRUCTURE. That's a much
    bigger change than the cluster description suggests.
    *Patch:* PR-D rephrased to recommend the PRD-§9-subsection approach
    as default (MINOR change), with the 02b_DECOMP layer as an explicit
    alternative requiring user approval before plan-drafting. Risk
    section expanded.
  - **P1-4 (MEDIUM):** PR-D depends on PR-C (threshold ID pattern) but
    the sequence section says PR-D ships after PR-B. Need explicit
    arrow PR-C → PR-D in the dependency graph. Also PR-E says "depends
    on PR-B (uses recalibrated playbooks)" — but PR-E is just IPLAN
    template subtype, not playbook content; the dependency is weak.
    *Patch:* Dependency graph updated. PR-E now says "may benefit from
    PR-B's recalibrated playbooks but ships independently".
  - **P1-5 (MINOR):** Plan has no commit/branch convention for the child
    PRs. Future readers wouldn't know whether to use `feat/framework-cleanup-pr-a`
    vs `feat/cleanup-a-harness` etc.
    *Patch:* Added a "Child PR naming" section: `feat/cleanup-pr-{a..e}-<theme-slug>`.
- **Cross-checks clean:**
  - 17 + 1 = 18 entries; matches the 9 prior + 9 new accounting ✓
  - Cluster → item mapping: every Open item is assigned to exactly one
    PR (no duplicates, no omissions) ✓
  - PR-A's 4 items + PR-B's 6 items + PR-C's 4 items + PR-D's 2 items
    - PR-E's 1 item = 17. ✓
  - LAYER-PLAYBOOKS-001 closure is real (PR #127 merged `c56c386f`) ✓
- **Net structural change:** 5 in-place clarifications.
- **Status:** Patches folded in. Awaiting Pass 2.

### Pass 2 — re-review of Pass 1 patches

- **Date:** 2026-06-11T19:45:00Z
- **Method:** re-read the patched plan; verify every cluster section
  honors Pass 1 patches (version arithmetic, dependency graph,
  child-PR naming); look for new contradictions introduced by Pass 1
  text edits.
- **Findings (2 MEDIUM — 0 MAJOR):**
  - **P2-1 (MEDIUM):** Pass 1's P1-2 patch only touched PR-D's
    version-impact line. PR-A / PR-B / PR-C / PR-E still had
    hardcoded version arithmetic ("0.14.0 → 0.14.1", "0.17.1 → 0.18.0",
    etc.) — contradicting the Pass 1 statement that "exact arithmetic
    finalized in child plan, only floors stated".
    *Patch:* All 4 PR sections' Version impact lines now say
    "Version impact (floor): … minimum. Exact arithmetic finalized
    in child plan."
  - **P2-2 (MEDIUM):** PR-B's playbook recalibration scope item said
    "lens must produce ≥ 1 finding per ≥ N lines of artifact" — N was
    undefined. A heuristic with undefined parameter is not actionable.
    *Patch:* Reframed the principle as "lens returning 100/0-findings
    must produce a `no_findings_rationale` field naming at least one
    section examined; missing rationale caps lens at 95." The
    N-lines-per-finding heuristic deferred to the child plan, with a
    note that the threshold should be surveyed across the 7-layer
    cascade history (concrete data, not a guess).
- **Cross-checks clean:**
  - Pass 1's dependency graph patch (PR-C → PR-D REQUIRES) honored ✓
  - Pass 1's child PR naming section added + branch names listed ✓
  - Pass 1's PR-D subsection-vs-02b-layer trade-off documented + risks ✓
  - 17 Open + 1 Closed items in TODO file ✓ (verified by `grep -cE`)
  - Cluster → item mapping totals 17 ✓
- **Net structural change:** 4 version-arithmetic line edits + 1
  PR-B scope-item reframe.
- **Status:** Patches folded in. Pass 3 needed only if I missed
  another inconsistency.

### Pass 3 — convergence check

- **Date:** 2026-06-11T19:55:00Z
- **Method:** read the whole plan top-to-bottom one final time.
- **Findings:** 0 substantive. The plan is internally consistent;
  the 5-PR cluster design holds; dependencies are explicit; risks
  are documented per-PR; the workstream gate criteria are concrete.
- **Verdict: CONVERGENCE.** Plan READY-FOR-PR.

**Convergence trend:**

| Pass | Found | MAJOR | MED | MIN |
|---|---|---|---|---|
| 1 | 5 | 0 | 4 | 1 |
| 2 | 2 | 0 | 2 | 0 |
| 3 | 0 | 0 | 0 | 0 |
