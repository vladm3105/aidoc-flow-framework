# BRD-RT-001 Plan — Wire Review-Team Subagent Fan-Out into BRD-Layer Skills

| Field      | Value                                       |
|------------|---------------------------------------------|
| Task       | BRD-RT-001                                  |
| Depends on | D-0020 (GATE-SPEC), `review-team/SKILL.md`  |
| Status     | PLANNED — 2026-06-03T03:54:28Z              |
| Feeds      | PRD-RT, EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT (per-layer follow-ups) |

## Objective

Align the four BRD-layer skills (`doc-brd`, `doc-brd-audit`, `doc-brd-fixer`,
`doc-brd-autopilot`) and the `requirements-analyst` agent with the framework
spec's multi-persona review-team model so the team-mode `independent`
review actually runs at the BRD gate — using Claude Code's `Task` tool to
fan out per-persona subagents over the per-artifact blackboard at
`.aidoc/review/01_BRD/<BRD-id>/`. The single-pass legacy path stays
unchanged as the fallback. No `framework/**` content is touched.

## Scope

**In:**

- 4 skills under `platforms/claude-code-plugin/skills/doc-brd*/SKILL.md`
- 1 agent at `platforms/claude-code-plugin/agents/requirements-analyst.md`
- Plugin version bump 0.4.0 → 0.4.1 (`platforms/claude-code-plugin/VERSION`
  - `platforms/claude-code-plugin/.claude-plugin/plugin.json` `version`)
- Plugin CHANGELOG entry at `platforms/claude-code-plugin/CHANGELOG.md`
- A new `DECISIONS.md` entry: D-0030 — BRD-layer team-mode dispatcher
  placement (rationale for wiring at `doc-*-audit`, not at the orchestrator)

**Out:**

- PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN — same refactor applies but lands as
  per-layer follow-up PRs (PRD-RT, EARS-RT, …) once the BRD pattern
  validates end-to-end on a live cascade
- `review-team/SKILL.md` itself — already correctly designed per spec
- Hermes-side parity — Hermes already implements this canonically
  (`sdd-orchestrator` + `sdd-review-personas` + 15-persona library)
- `requirements-analyst` full Hermes-parity refactor (EARS-first
  classification, FR/QA/IR bucket removal, output-protocol unification) —
  deferred to a separate larger refactor; this PR only fixes the 5 legacy
  bugs
- Removing the cascade's standalone `doc-brd` "reference call"
  (`test-acceptance.sh:906`) — clean-up, tracked separately as G1 of the
  audit findings
- Phase 4.1 `requirements-analyst` invocation timing (currently post-hoc,
  could be at-gate) — tracked separately as G2 of the audit findings
- The `BRD-REF` documents exception (free-format references exempt from
  scores) — niche feature, no current invocation, defer until used
- Framework `CLAUDE.md` stale spec-version reference (says 0.11.0, actual
  0.11.2) — separate housekeeping commit, not in this plan
- `tests/scripts/test-acceptance.sh` verification harness changes — the
  existing per-persona name grep in `review-team.log` (lines 1238-1276) is
  insufficient for proper team-mode verification, but tightening it is a
  separate concern; this plan adds explicit verification commands instead

## Approach

### Architectural decision (D-0030 candidate)

The dispatcher of the persona crew lives in `doc-<layer>-audit` (and
`doc-<layer>-autopilot` for the create loop), **not** at a higher
orchestrator. Rationale:

- `review-team/SKILL.md:108` already says "`pm-orchestrator` (or the
  invoking `doc-<layer>-audit`) is the dispatcher." This codifies that.
- Per-layer dispatch at the gate matches `REVIEW_REMEDIATION_FLOW.md`
  trigger points (`on_gate_fail`, `pre_promotion`, `pre_merge`); a
  chain-wide review can't catch errors at the per-layer gate they
  originated at.
- The Phase 3 chain-wide `review-team` invocation in
  `test-acceptance.sh:1239` continues to exist for cross-cutting review;
  the two are complementary, not duplicative.

### BRD crew (verified, `framework/governance/REVIEW_CREWS.yaml`)

```yaml
BRD:
  author: business_analyst
  review: {architect: 30, business_analyst: 30, auditor: 20, adversary: 20}
```

Weights sum to 100. Note: Hermes' `brd-review-inline-pattern.md` uses
`chaos-engineer` for the same role; the framework canonicalized to
`adversary` for the closed cross-engine persona set. Plugin mapping per
`platforms/claude-code-plugin/skills/review-team/SKILL.md` lens→agent
table:

| Lens | Agent (`subagent_type`) | Source-of-truth path |
|---|---|---|
| `business_analyst` | `requirements-analyst` | `agents/requirements-analyst.md` |
| `architect` | `solutions-architect` | `agents/solutions-architect.md` |
| `auditor` | `traceability-auditor` (+ `security-engineer` when security/compliance findings) | `agents/{traceability-auditor,security-engineer}.md` |
| `adversary` | `adversary` | `agents/adversary.md` |
| `synthesizer` | `synthesizer` | `agents/synthesizer.md` |

### Mode resolution (consistent across the four skills)

Read `.aidoc/profile.yaml` `review_mode`. Default `team`. Fall back to
`single_pass` when (a) profile says so, (b) `Task` subagent dispatch
unavailable, or (c) crew quorum cannot be met. **Structural gate floor
runs deterministically in every mode** — `team` adds parallel content
review **above** it, never below it (per `REVIEW_TEAM.md`:82-86).

In single_pass mode, quorum is not applicable (one model applies all
lenses sequentially in one context).

### Per-artifact blackboard path

```
.aidoc/review/01_BRD/<BRD-id>/
  business_analyst.json   # persona-output record per lens
  architect.json
  auditor.json
  adversary.json
  <persona>.fix_<N>.json  # patch-validation records during remediate
  report.md               # synthesizer's reduced report
```

`<BRD-id>` matches the BRD's nested folder name (e.g. `BRD-01_url_shortener`)
so multiple BRDs per project don't collide. The audit's team-mode branch
must `mkdir -p` this directory before dispatching subagents.

### Audit-report output path (resolves audit finding C3)

Update `doc-brd-audit/SKILL.md` to write to
`.aidoc/audit/01_BRD-audit.md` per `framework/docs/AIDOC.md` (which is the
canonical contract). The legacy `BRD-NN.A_audit_report_vNNN.md` shape
content is preserved — just relocated. Acceptance suite already routes
output there (already verified in the BRD-only live run).

## Step sequence

1. **`requirements-analyst.md` agent — 5 legacy fixes** (smallest, most
   isolated; ship first):
   - Layer chain line 26: extend to `BRD → PRD → EARS → BDD → ADR → SPEC →
     TDD → IPLAN`.
   - Coverage Threshold Guidelines (lines 366-371): add `TDD → IPLAN` and
     `IPLAN → Code` rows.
   - Add a new `## Review-Team Lens Role` section after line 21 declaring
     the three-lens binding (`business_analyst` for BRD,
     `requirements_specialist` for EARS, `product_owner` for PRD) per
     `review-team/SKILL.md` mapping table.
   - Line 254 `@adr: ADR-NN` (dash form) — add a one-line note that this
     is by design (document-level refs are dash form per
     `ID_NAMING_STANDARDS.md`).
   - Add a single-sentence aside near the FR/QA/IR classification table
     clarifying that these are *category labels*, not the removed `FR-XXX`
     *element ID prefix* pattern.

2. **`doc-brd/SKILL.md` — minor**:
   - Frontmatter `adapts:` → append `review_mode`.
   - Validation section (lines 150-167): add a single paragraph clarifying
     the mode-aware validator framing (structural checks always run here;
     content quality runs in `doc-brd-audit` in either mode).

3. **`doc-brd-audit/SKILL.md` — the meaty contract change**:
   - Frontmatter `adapts:` → append `review_mode`.
   - Insert new `## Review Mode` section between Execution Contract and
     Structural Checklist with the pseudo-text below.
   - Combined Report Format: add `Persona Slot Index` block (paths to
     per-lens slots) and a `Coverage` line surfacing `coverage.quorum_met`
     for consumers.
   - Update output-path declaration from
     `docs/01_BRD/BRD-NN_*/BRD-NN.A_audit_report_vNNN.md` to
     `.aidoc/audit/01_BRD-audit.md` (align with AIDOC.md).
   - Mention that `mkdir -p .aidoc/review/01_BRD/<BRD-id>/` happens before
     fan-out.

   Pseudo-text for the new section:

   ```
   ## Review Mode

   Resolve `review_mode` from `.aidoc/profile.yaml`. Default `team`.

   **team mode (preferred):**
   1. mkdir -p .aidoc/review/01_BRD/<BRD-id>/
   2. Read BRD crew from REVIEW_CREWS.yaml:
      {architect:30, business_analyst:30, auditor:20, adversary:20}.
   3. Map each lens to its plugin agent via review-team/SKILL.md.
   4. Fan out: dispatch one Task subagent per lens with
      subagent_type=<agent>; each receives BRD path, lens name, weight,
      slot path .aidoc/review/01_BRD/<BRD-id>/<lens>.json. The
      structural checklist is included as untrusted context.
   5. Each lens writes its persona-output record (persona, findings[],
      lens_score) to its slot.
   6. After all slots written (or marked failed on no-return), dispatch
      the synthesizer subagent against the slot dir. It deterministically
      dedups findings, computes weighted/capped score per REVIEW_TEAM.md,
      records coverage, writes report.md.
   7. Compose the combined audit report: (a) structural findings (always)
      + (b) synthesizer's report.md content findings. Preserve the
      existing audit-report shape.

   **single_pass mode (fallback):**
   Run single-pass content review by this model directly, applying every
   lens in one context (no quorum applies). Same combined-report shape.

   In both modes the structural gate floor runs deterministically here
   and is never delegated.
   ```

4. **`doc-brd-fixer/SKILL.md` — remediate-loop integration**:
   - Frontmatter `adapts: [section_toggles]` → `[section_toggles, review_mode]`.
   - Insert new `## Remediate Mode` section between Input Contract and
     Fix Phases with the pseudo-text below.
   - Fix Phases table: keep verbatim.

   Pseudo-text:

   ```
   ## Remediate Mode

   Resolve review_mode from .aidoc/profile.yaml. Default team.

   **team mode (per REVIEW_TEAM.md §Operations §Remediate):**
   1. Read BRD-NN.A_audit_report_vNNN.md AND, when present, the per-persona
      slots at .aidoc/review/01_BRD/<BRD-id>/<persona>.json. Slots are
      optional — fixer must work from the audit report alone if slots are
      missing (e.g. single_pass run produced no slots).
   2. Group blocking findings (P0+P1) by responsible lens via the lens→agent
      table. P2/P3 are advisory — apply deterministically without lens
      validation.
   3. For each blocking finding propose a patch (Fix Phases 0–7 below
      describe the patch shapes) and apply it (back up first per Input
      Contract).
   4. Validate non-regression: dispatch the responsible lens as a Task
      subagent in patch-validation mode. Persist as
      <persona>.fix_<N>.json in the same blackboard.
   5. If any lens returns new P0/P1 on the patch, revert that patch and
      flag manual_required. Never silently keep a regressing fix.
   6. After all patches validated, dispatch synthesizer once to emit the
      unified fix report. Persist BRD-NN.F_fix_report_vNNN.md with both
      Fixes Applied table AND a Validation Slots index.

   **single_pass mode:** apply Phase 0–7 directly, single-handed, no lens
   validation. Unchanged legacy behaviour.
   ```

5. **`doc-brd-autopilot/SKILL.md` — outer loop refactor**:
   - Frontmatter `adapts:` → append `review_mode`. Keep `glossary` (passes
     through to `doc-brd`).
   - Skill Dependencies table: add `../review-team/SKILL.md` (role: "team-mode
     dispatcher") and `../charts-flow/SKILL.md` (already referenced in
     Workflow §3, missing from the table).
   - Add reference to `framework/governance/AUTHORING_STYLE.md` somewhere
     in the body (currently only inherited via doc-brd / doc-brd-audit).
   - Replace Workflow §4-5 with the create→review→revise loop.

   Pseudo-text:

   ```
   ## Generation Loop (review_mode: team)

   When review_mode is team, generation is a create→review→revise loop
   per REVIEW_TEAM.md §Operations §Create:
   1. Draft — dispatch ONE Task subagent: subagent_type=requirements-analyst
      (BRD author = business_analyst lens). Brief: BRD-TEMPLATE.yaml,
      source input, doc-brd/SKILL.md as authoring rules. ONE author —
      never parallel drafts.
   2. Review — invoke doc-brd-audit (default pass-through mode); the
      audit fans out the BRD crew.
   3. Revise — if FAIL and iterations < 3, invoke doc-brd-fixer in team
      mode (consumes slot index, dispatches lens validators per blocking
      finding). GOTO step 2.
   4. Converge or escalate — on PASS update BRD-00_index.md; on max
      iterations with FAIL write manual-review flag.

   (single_pass mode): run legacy Workflow §1-§5 unchanged.
   ```

6. **Plugin version bump**:
   - `platforms/claude-code-plugin/VERSION`: `0.4.0` → `0.4.1`.
   - `platforms/claude-code-plugin/.claude-plugin/plugin.json` `version`
     field: `0.4.0` → `0.4.1`.

7. **Plugin CHANGELOG entry** at
   `platforms/claude-code-plugin/CHANGELOG.md`:
   - New `[0.4.1]` section under `[Unreleased]` or as a dated release row.
   - Categories: `Changed` (the 4 BRD skill refactors + agent fixes).
   - Note: framework spec unchanged (still 0.11.2); only plugin behaviour
     changes.

8. **DECISIONS.md entry** at `plans/DECISIONS.md`:
   - Add **D-0030**: BRD-layer team-mode dispatcher placement. Records that
     the persona crew is dispatched from `doc-<layer>-audit` (and
     `doc-<layer>-autopilot` for create), not from a higher orchestrator.
     ISO-stamped per CLAUDE.md convention. Cite `REVIEW_TEAM.md:108` and
     `review-team/SKILL.md:108` as the canonical anchors.

9. **Verify** (see Verification section below).

10. **Land**:
    - Single PR `feat(plugin): wire review-team subagent fan-out into BRD-layer skills`.
    - Update plugin CHANGELOG under `[Unreleased] → Changed`.
    - Update `plans/MIGRATION_TODO.md` only if it tracks BRD-RT (it does
      not currently — no update needed).
    - Project-level `CHANGELOG.md` / `ROADMAP.md` — no update needed
      (project-level tracks framework spec + project releases; this is a
      plugin-only change).

## Verification

Cheap-to-expensive ladder. Steps 1-3 are non-LLM; step 4 spends ~$5-8.

1. **Static lint + conformance** (free, < 30s):

   ```sh
   env -u LD_LIBRARY_PATH pre-commit run --files \
     platforms/claude-code-plugin/skills/doc-brd/SKILL.md \
     platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md \
     platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md \
     platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md \
     platforms/claude-code-plugin/agents/requirements-analyst.md \
     platforms/claude-code-plugin/VERSION \
     platforms/claude-code-plugin/.claude-plugin/plugin.json \
     platforms/claude-code-plugin/CHANGELOG.md \
     plans/DECISIONS.md
   python3 -m unittest discover -s tests/conformance -v
   ```

   Pass criteria: pre-commit green (whitespace, markdownlint, secrets, the
   `framework/platform conformance suite` hook); `tests/conformance/test_review_team.py`
   still confirms BRD crew weights sum to 100 and lens→agent table covers
   all referenced personas.

2. **`adapts:` declaration check** (free):

   ```sh
   grep -E "^\s*adapts:" platforms/claude-code-plugin/skills/doc-brd*/SKILL.md
   ```

   Pass criteria: all 4 skill frontmatters show `review_mode` in `adapts:`.

3. **Mock-mode acceptance run** (free, < 1 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --no-live
   ```

   Pass criteria: 7 PASS / 0 FAIL / 44 SKIP / 51 total (matches the
   pre-refactor baseline). Confirms no regression on the deterministic path.

4. **Single-layer team-mode live run** (~$2-3, ~10 min):

   ```sh
   # Ensure profile says team mode (already default per REVIEW_CREWS.yaml)
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd
   ```

   Pass criteria (all four required):
   - **Slot files present**: `ls .aidoc/review/01_BRD/BRD-01_*/` shows
     `business_analyst.json`, `architect.json`, `auditor.json`,
     `adversary.json` — each non-empty and parsing as the persona-output
     contract (`persona`, `findings[]`, `lens_score`).
   - **Synthesizer report**: `.aidoc/review/01_BRD/BRD-01_*/report.md`
     present with a coverage line and weighted-capped score.
   - **Combined audit report**: `.aidoc/audit/01_BRD-audit.md` contains a
     `Persona Slot Index` block listing the 4 slot paths.
   - **Audit score**: ≥ 90 (or fixer-loop converges within 3 iterations).

   Note: the existing harness check
   (`tests/scripts/test-acceptance.sh:1238-1276`) only verifies persona
   names appear in `review-team.log` — that's necessary but not
   sufficient. The four pass criteria above are checked **manually** for
   this PR's verification.

5. **Remediate-loop verification** (~$2, ~5 min) — optional but
   recommended:

   Inject a deliberate P1 finding (drop §8's "Infrastructure" ADR-topic
   category from the produced BRD), re-run step 4. Pass criteria: fixer
   dispatches `auditor` + `architect` lens validators, writes
   `<persona>.fix_<N>.json` slots, second-pass audit converges to PASS.

6. **Single-pass regression** (~$2, ~10 min):

   ```sh
   # Set review_mode: single_pass in examples/url-shortener/.aidoc/profile.yaml
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd
   ```

   Pass criteria: identical PASS to the historical 96/100; **no**
   `.aidoc/review/` slot files produced; combined audit report has no
   `Persona Slot Index` block (no slots to index).

7. **Full cascade** (~$15-25, 60-120 min) — defer to a follow-up after
   steps 1-6 all pass. Validates the BRD pattern doesn't break downstream
   layers (PRD..IPLAN still single-pass at this point).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Regressing the url-shortener 96/100 single-pass PASS | `single_pass` stays unchanged code path; verification step 6 explicitly tests parity |
| R2 | Partial-crew quorum below threshold | REVIEW_TEAM.md §Resilience requires "below quorum → low-confidence → human review, never silent pass." Audit's Combined Report surfaces `coverage.quorum_met=false` and autopilot treats that as FAIL even if numeric score ≥ threshold |
| R3 | `requirements-analyst` agent overloaded with 3 lens roles | Mapping already binds these 3 lenses to this agent in `review-team/SKILL.md`; we only make it explicit, not new |
| R4 | Cost regression from N concurrent Task subagents per layer | `--cost-cap` guard in test-acceptance.sh halts at $22; per-layer costs measured in verification step 4 before extending pattern beyond BRD |
| R5 | Phase 3 chain-wide `review-team` invocation now redundant with per-layer team-mode audits | Plan deliberately keeps both (cross-cutting vs gate-level review). Re-evaluate after full cascade lands; could remove Phase 3 invocation in a follow-up |
| R6 | Audit-report path change (legacy `docs/.../BRD-NN.A_audit_report_vNNN.md` → `.aidoc/audit/01_BRD-audit.md`) breaks anything reading the legacy path | Audit suite already writes to the `.aidoc/` path; no other consumer found. doc-brd-fixer's input contract still reads "the latest audit report" — updated to read from new path |
| R7 | Task tool dispatch unavailable at runtime (e.g. nested skill invocation context) | `single_pass` fallback handles this; mode resolution explicitly tests for dispatch availability before fan-out |

## Review log

### Pass 1 — 2026-06-03T03:54:28Z

Findings folded back into the sections above:

- Initial plan (at `~/.claude/plans/gleaming-humming-deer.md`) deviated
  from `plans/PLAN-TEMPLATE.md` structure. Rewrote with metadata table,
  Objective/Scope/Approach/Step sequence/Verification/Risks ordering, and
  this Review log section per D-0007.
- Audit-report output-path inconsistency was acknowledged but not
  resolved. Took position (a) — align with `framework/docs/AIDOC.md`
  canonical path `.aidoc/audit/01_BRD-audit.md`. Added explicit step in
  the audit skill change list. Added R6 to track migration risk.
- Plugin version bump and CHANGELOG entry were missing. Added as Step 6
  and Step 7. Plugin is independent SemVer stream — needed for any
  behavioural change.
- D-0030 `DECISIONS.md` entry was missing per the project's
  "Record non-obvious choices in plans/DECISIONS.md" rule. Added as
  Step 8.
- Implementation order within the single PR was unspecified. Step
  sequence now lists files in dependency order (agent first → doc-brd
  → audit → fixer → autopilot).
- Several audit findings (B2, B3, B4, E2, E3, G1, G2) had unclear
  status. Added explicit "Out:" bullets enumerating which are deferred
  and to where.
- Hermes uses `chaos-engineer` for what the framework spec calls
  `adversary`. Added a note in the BRD crew section so readers familiar
  with Hermes don't get confused.
- Per-artifact blackboard dir creation (`mkdir -p`) was implicit. Added
  explicitly to Step 3's pseudo-text.
- Single_pass mode and quorum concept relationship was unclear. Added
  explicit "no quorum in single_pass" clarifier in the Mode resolution
  paragraph.
- Verification step 4's claim about the existing harness was
  over-stated. Read the actual code at
  `tests/scripts/test-acceptance.sh:1238-1276` — it only grep's persona
  names in `review-team.log`, which is necessary-but-insufficient for
  verifying real Task fan-out. Reworded verification to spell out four
  explicit pass criteria (slot files, synthesizer report, combined-audit
  index block, audit score) that are checked manually for this PR.
- Risk R5 (Phase 3 redundancy) and R7 (Task tool dispatch unavailable)
  were not in the original draft. Added.

### Pass 2 — 2026-06-03T03:54:28Z

Re-read whole plan. No new findings.

- **Verification calibration check**: each pass criterion in Verification
  step 4 maps to a specific transformation rule in Step sequence — the
  rules' intended outputs trip the checks (no false positives), and no
  check misses outputs the rules produce (no false negatives). The four
  pass criteria correspond directly to:
  - mkdir + per-lens fan-out (rule §3.team mode steps 1-4) → "Slot files
    present"
  - Synthesizer dispatch (rule §3.team mode step 6) → "Synthesizer report"
  - Combined report composition (rule §3.team mode step 7) → "Combined
    audit report contains Persona Slot Index"
  - audit_threshold ≥ 90 + fixer convergence → "Audit score ≥ 90"
- **Scope check**: every "Out:" item has a clear deferral target or
  out-of-scope rationale.
- **Risks check**: 7 risks identified; each has a concrete mitigation
  tied to a specific verification step or design choice in the plan
  body.
- **PR-readiness check**: the implementation order in Step sequence
  produces a clean diff per file, and inter-skill contracts (audit's
  slot schema consumed by fixer and autopilot) land atomically in the
  same PR — no broken intermediate states possible.

### Pass 3 — 2026-06-03T03:59:33Z

Reviewed `/opt/data/ucx_framework/mcp_ucx` — the pre-Hermes deprecated
predecessor — as an additional historical reference point. Findings
**confirm the plan's direction**; no substantive changes required:

- **mcp_ucx is the "what NOT to do" reference.**
  `mcp_ucx/prompts/templates/review/UCR_PROMPT_BRD.md` line 5 says
  "Apply all personas sequentially, maintaining full context throughout."
  This is the sequential single-context AI Expert Board pattern. Hermes
  `sdd-orchestrator/SKILL.md` line 19 explicitly migrated away from it
  ("Unlike the legacy UCX system that concatenated all persona texts
  into a single prompt, you dispatch personas as parallel subagents").
  The plugin's current `single_pass` mode is literally the mcp_ucx
  pattern — which is fine to retain as the documented fallback.

- **Persona-set evolution confirmed** (mcp_ucx → Hermes → framework
  spec): mcp_ucx BRD review crew was 6 personas
  `[architect, auditor, business_analyst, chaos_engineer, fact_checker, chairperson]`
  with `mode: sequential`. The framework spec canonicalized to a 4-persona
  BRD review crew + synthesizer:
  - `chaos_engineer` → `adversary` (semantic rename in the closed
    persona set per `REVIEW_CREWS.yaml`)
  - `fact_checker` → folded into the synthesizer's deterministic reduce
    (per `REVIEW_TEAM.md` §"Synthesis = reduce + narrative")
  - `chairperson` → `synthesizer` (renamed; same role)
  The plan correctly uses the canonical 4-persona framework crew.

- **mcp_ucx's `persona_mappings.yaml`** carried `mode: sequential`
  everywhere with a comment: "Future: parallel persona orchestration."
  Hermes delivered that future. The plugin's `review-team/SKILL.md`
  documents that future. The plan's job is to *wire* that future at
  the BRD-layer dispatchers — confirmed as the correct scope.

- **mcp_ucx referenced legacy 12-layer SDD model** (`sys`, `req`, `ctr`,
  `tspec` in `persona_mappings.yaml` lines 32-52). The framework retired
  these to the canonical 8 layers. Not relevant to the current plan
  except as confirmation that the plugin's already-completed PLM
  migration (CHANGELOG `[1.1.0]` "Plugin layer-model migration") is the
  right precedent — this plan is doing similar work for review-team
  semantics at the BRD layer.

- **mcp_ucx's "pre-validation vs content findings" separation**
  (`UCR_PROMPT_BRD.md` lines 43-53): a useful principle that's already
  captured by the framework spec via the structural-gate-floor (always
  deterministic) vs content-review (persona crew, advisory enrichment
  above the floor) split — `REVIEW_TEAM.md` §"Scoring, conflicts & the
  gate" line 82-86. The plan's §"Mode resolution" reflects this
  correctly.

Plan is ready for implementation. Three passes complete, last pass found
no actionable changes.
