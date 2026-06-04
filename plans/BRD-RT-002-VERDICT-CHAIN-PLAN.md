# BRD-RT-002 Plan — Wire the audit → autopilot verdict chain through the written reports

| Field      | Value                                       |
|------------|---------------------------------------------|
| Task       | BRD-RT-002                                  |
| Depends on | BRD-RT-001 (D-0024, merged), PROFILE-DELTA-001 (D-0025, merged) |
| Status     | PLANNED — 2026-06-03T17:53:34Z (Pass 3 amendment 2026-06-03T18:25:00Z) |
| Feeds      | PRD-RT, EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT — these per-layer follow-ups inherit the corrected verdict-chain semantics from this PR |

## Objective

Close ten gaps surfaced by the BRD-RT-001 live verification runs
(2026-06-03) so team-mode review produces **the same verdict at every
consumer** — audit-skill stdout, written audit report, driver script,
autopilot revise loop — and the per-layer runtime cap stops aborting
legitimate team-mode runs. After this PR, a team-mode audit that
computes FAIL actually triggers the fixer; the synthesizer writes a
deterministic `verdict.json` that callers parse instead of scraping
Markdown prose; a `single_pass` audit is always marked advisory; and a
full-cascade team-mode run can complete inside its wall-clock and cost
budgets.

## Scope

**In:**

- `agents/synthesizer.md` — also write a structured **`verdict.json`**
  companion next to `report.md` containing
  `{combined_status, content_score, structural_status, coverage:
  {expected, ran, quorum_met}, blocking_findings_count, lens_scores:
  {<lens>: <score>}}`. The Markdown `report.md` stays as the human
  narrative; downstream consumers parse the JSON.
- `doc-brd-audit/SKILL.md` (frontmatter line ~18 + new section after
  `### team mode` at line ~76):
  - Add `## Output Contract` subsection inside the team-mode branch
    that reads `verdict.json` and produces stdout in the structured
    shape below.
  - In Combined Report Format (line ~193), always include the
    `single_pass` advisory note whenever `review_mode: single_pass` is
    the resolved mode — not gated on "at a gate" (the audit skill
    doesn't reliably know its trigger context).
- `doc-brd-autopilot/SKILL.md` (Workflow §5 / "Revise" step at line
  ~94-103) — the create→review→revise loop reads its PASS/FAIL
  decision from `verdict.json` at
  `.aidoc/review/01_BRD/<BRD-id>/verdict.json`, with fallback to the
  written `01_BRD-audit.md` if verdict.json is absent (e.g. single_pass
  runs without a synthesizer). Never reads the audit subagent's
  stdout summary or the BRD's self-claimed PRD-Ready score.
- `doc-brd-fixer/SKILL.md` — minor confirmation that the fixer
  consumes the written report + slots. **First live exercise** of
  team-mode fixer behaviour happens in this PR's Verification step 4
  (BRD-RT-001's runs never reached the fixer because the autopilot
  mis-read the verdict as PASS).
- `tests/scripts/test-acceptance.sh`:
  - `MAX_LAYER_SEC=900` → `1800` (line 63) with comment explaining team
    mode legitimately runs 17-25 min per layer.
  - `SKILL_TIMEOUT=600` → `1200` for the audit skill specifically (or
    give `doc-brd-audit` the `REVIEW_TEAM_TIMEOUT` since it now
    orchestrates a sub-team itself). Cleanest impl: name a new
    `AUDIT_TIMEOUT=1200` and use it in `invoke_skill` when name matches
    `doc-*-audit`.
  - In `invoke_skill` (function defined around line 430), after
    capturing `audit_score` from the skill's stdout response, also read
    the synthesizer's `verdict.json` if present. If the values differ,
    log a warning and prefer `verdict.json`. Belt-and-suspenders for
    Gap A drift.
- **`<BRD-id>` path codification** — the slot directory is
  `.aidoc/review/01_BRD/<BRD-id>/` where `<BRD-id>` is the short
  artifact ID (`BRD-01`), not the nested folder name
  (`BRD-01_url_shortener`). BRD-RT-001's implementation already chose
  the short form; this plan codifies it explicitly and updates the
  BRD-RT-001 SKILL text wording retroactively in the same edits.
- Plugin version bump 0.4.2 → 0.4.3.
- Plugin CHANGELOG entry.
- `plans/DECISIONS.md` D-0026 — "Synthesizer writes a structured
  `verdict.json`; every verdict consumer (audit skill stdout, driver,
  autopilot, fixer) reads from it. Markdown `report.md` is the human
  narrative, never the parse target."

**Out:**

- Framework spec changes — none required. `REVIEW_TEAM.md` already says
  the synthesiser's reduce is deterministic and authoritative; this PR
  is the plugin's binding catching up to the spec.
- **PRD..IPLAN layer wiring** — propagation deferred until BRD-RT-002
  is verified live. **The Gap A/C/E fix pattern (Output Contract,
  read-from-verdict.json, always-on advisory) is generic and reusable
  verbatim** for `doc-<layer>-audit` and `doc-<layer>-autopilot` skills
  at PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN. Each per-layer follow-up
  PR copies the pattern with the layer's name substituted.
- A new conformance test that asserts stdout/`verdict.json` score
  match — potentially valuable but model-output behavior is hard to
  assert deterministically; defer until BRD-RT-002 + PRD-RT show
  consistent results across runs.
- `single_pass` deprecation — single_pass remains a first-class
  fallback (cost-constrained runs, no-subagent contexts). Only the
  advisory framing changes (now always shown when single_pass resolves).
- Hermes-side parity — Hermes implements its own runtime; this PR is
  plugin-only.
- Caching follow-up (`REVIEW-TEAM-RUNNER-CACHING-001`) — separate
  v0.4.4 work; orthogonal optimisation.

## Approach

### Root-cause: the audit skill's stdout ≠ the audit skill's written report

Run #1 (team mode, default profile) of the BRD-only cascade produced:

```
$LOG_DIR/elements/doc-brd-audit.log:   audit_score: 92, outcome: PASS  ← reported
.aidoc/audit/01_BRD-audit.md:          Content score: 83, Combined: FAIL  ← written
```

Same skill invocation. Two verdicts. The model running `doc-brd-audit`
in team mode followed the SKILL's instructions to dispatch the crew and
synthesizer, but then **its final stdout summary reflected the
autopilot's self-claim** (92, from the BRD's traceability-matrix health
line) rather than the synthesizer's deterministic computation (83).
Every downstream consumer (driver, autopilot revise loop) reads the
stdout, not the written report — so the FAIL never propagates.

### Why Markdown report.md is the wrong parse target

The synthesizer's `report.md` is rendered as human-narrative Markdown:

```markdown
## Gate Decision

| Item | Value |
|---|---|
| Readiness score (advisory) | **83 / 100** |
| Gate threshold | 90 |
| Verdict | **FAIL** |
```

Parseable by a model, but **fragile** — heading text, cell formatting,
or value placement can drift between runs. Asking the audit skill's
model to extract values from `report.md` to produce its stdout shifts
fragility from one place to another.

The structural fix is to have the synthesizer also write a
deterministic, schema-checkable `verdict.json` companion. Then every
consumer parses JSON, not prose.

### Fix shape per gap

**Gap A — `doc-brd-audit/SKILL.md` team-mode branch.** Add an explicit
"Output Contract" subsection inside the team-mode branch (insertion
point: immediately after the "Quorum & coverage" paragraph at line
~125, before `### single_pass mode (fallback)` at line ~131):

```
## Output Contract

After the synthesizer writes `verdict.json` (alongside `report.md`)
read it back and produce your terminal stdout response in this exact
shape, mirroring the JSON values verbatim:

  Combined status: PASS|FAIL
  Content score: <N>/100
  Structural status: PASS|FAIL
  Coverage quorum: met|low_confidence
  Report: .aidoc/audit/01_BRD-audit.md

Do NOT echo the BRD's self-claimed PRD-Ready score. The synthesizer's
`verdict.json` is the authoritative verdict; your response mirrors it
key-for-key.
```

**Gap B — driver belt-and-suspenders.** In
`tests/scripts/test-acceptance.sh`, modify the `invoke_skill` bash
function (around line 430) to read the synthesizer's `verdict.json` (if
present at `.aidoc/review/<NN>_<LAYER>/<artifact-id>/verdict.json`)
after the skill returns. Cross-check the captured `audit_score`
against `verdict.json:content_score`. If they differ, log a warning
and store the JSON value. Catches future drift without depending on
model-prompt compliance.

**Gap C — `doc-brd-autopilot/SKILL.md` Workflow §5 (revise step at line
94-103).** Make the read-source explicit and deterministic:

```
After invoking `../doc-brd-audit/SKILL.md`, decide pass/fail by reading
the synthesizer's `verdict.json` at
`.aidoc/review/01_BRD/<BRD-id>/verdict.json`:

  - verdict.combined_status == "FAIL" → invoke `../doc-brd-fixer/SKILL.md`
    (team mode), GOTO step 4 to re-audit.
  - verdict.coverage.quorum_met == false → flag manual-review, halt.
  - verdict.combined_status == "PASS" → finalize.

When `verdict.json` is absent (e.g. single_pass run with no
synthesizer), parse the written `.aidoc/audit/01_BRD-audit.md`
combined-status line instead. Never make this decision from the audit
subagent's stdout summary or from the BRD's self-claimed PRD-Ready
score. The written verdict is the gate; everything else is advisory.
```

**Gap D — per-layer cap.** Raise `MAX_LAYER_SEC=900` to `1800`
(line 63 of `tests/scripts/test-acceptance.sh`) with an updated comment
explaining the rationale.

**Gap E — single_pass advisory note, always-on.** Add to
`doc-brd-audit/SKILL.md` Combined Report Format (around line 193).
**Always include** this advisory whenever the resolved mode is
`single_pass`, regardless of the trigger context. The note is
informational; showing it harmlessly at `on_author` is preferable to
the audit skill trying to detect "am I at a gate?" — which it cannot
reliably do without a caller-passed flag.

```
When the resolved `review_mode` is `single_pass`, include this
advisory in the report Summary section:

  > **Advisory mode.** This audit ran in `single_pass` — one model
  > applying every lens in one context. Per REVIEW_TEAM.md §"Scoring,
  > conflicts & the gate", `team` mode is the canonical gate review;
  > `single_pass` is a cost-constrained fallback whose lens
  > independence is reduced. Score 0-100 here is informational; a
  > production gate run should re-audit in `team` mode.
```

### New: structured `verdict.json` schema

`agents/synthesizer.md` instructs the synthesizer subagent to write
this file alongside `report.md`:

```json
{
  "combined_status": "PASS|FAIL",
  "content_score": 83,
  "structural_status": "PASS|FAIL",
  "coverage": {
    "expected": 4,
    "ran": 4,
    "quorum_met": true
  },
  "blocking_findings_count": 2,
  "lens_scores": {
    "architect": 93,
    "business_analyst": 82,
    "auditor": 92,
    "adversary": 62
  }
}
```

Schema is intentionally flat — every consumer (audit skill, driver,
autopilot, fixer) extracts what it needs by top-level key.

### Per-skill timeout interaction (G1 resolution)

`doc-brd-audit` in team mode internally orchestrates 4 review subagents

- synthesizer. Its observed Run #1 duration was 580s — within the 600s
default `SKILL_TIMEOUT` but close to the wall. After this PR, the same
skill may also drive fixer iterations (which it didn't before), pushing
duration higher.

**Resolution**: introduce `AUDIT_TIMEOUT=1200` in `test-acceptance.sh`
(or extend the existing per-skill name-matching: skills whose name ends
in `-audit` get the longer timeout). The 1800s `REVIEW_TEAM_TIMEOUT`
remains for the `review-team` skill itself.

### Wall-clock budget for full-cascade runs (G4 resolution)

Realistic projection per layer in team mode with fix iterations:

| Component | Time |
|---|---|
| Autopilot (drafter subagent) | ~3-5 min |
| Audit (4 lens subagents + synthesizer) | ~10-15 min |
| Fixer (if triggered, with N lens validators) | ~5-8 min |
| Re-audit after fix | ~10-15 min |
| **Per-layer typical (no fix)** | **~15-20 min** |
| **Per-layer with one fix iteration** | **~30-40 min** |
| **Per-layer max (3 fix iterations)** | **~50-70 min** |

Full cascade × 8 layers:

| Scenario | Wall-clock | Cost (Sonnet pricing) |
|---|---|---|
| Optimistic (no fixes needed at any layer) | ~2 hours | ~$40-50 |
| Typical (fix at 2-3 layers, 1 iter each) | ~3 hours | ~$60-80 |
| Worst case (fix at every layer, 3 iter) | ~6-8 hours | ~$120-180 |

Existing guards:

- `MAX_TOTAL_OUTPUT_TOKENS=1_500_000` (~$22 worth of output tokens) —
  may not be sufficient for worst-case full cascade; consider raising
  to 5M (~$75) for explicit team-mode full-cascade runs.
- Per-skill timeout (600s or new 1200s for audits) — catches stuck
  subagents.
- Per-layer cap (new 1800s) — catches stuck cascades on one layer.

**Recommended operational pattern**: full team-mode cascades run via
the existing `run_in_background: true` script invocation (which the
acceptance suite already supports via the test-harness background
mode) or via overnight `nohup`. Operators get notified at completion
rather than blocking on the terminal.

## Step sequence

1. **`agents/synthesizer.md`** — instruct the synthesizer subagent to
   write `verdict.json` alongside `report.md`. Include the schema
   shown above. Ensure the lens-score map mirrors the framework's
   per-layer crew weights.

2. **`doc-brd-audit/SKILL.md` — Gap A + Gap E + path codification**:
   - Frontmatter `adapts:` line ~18 — unchanged (already has
     `review_mode` from BRD-RT-001).
   - Replace any wording about `<BRD-id>` matching the nested folder
     name with the short artifact ID (`BRD-01`).
   - Add `## Output Contract` subsection after the team-mode branch's
     "Quorum & coverage" paragraph (insertion point ~line 125-130),
     citing the verdict.json fields.
   - In Combined Report Format (around line 193), add the always-on
     `single_pass` advisory paragraph.

3. **`doc-brd-autopilot/SKILL.md` — Gap C**:
   - Workflow §5 (Revise) at line ~94-103: replace "if FAIL …" with
     the explicit verdict.json read shown in the Approach section.
   - Single_pass branch keeps existing read-from-audit-report
     behaviour (with a one-line note that verdict.json is absent in
     single_pass).
   - Update `<BRD-id>` path references to the short form.

4. **`doc-brd-fixer/SKILL.md` — clarification + confirmation**:
   - Confirm Input Contract reads `.aidoc/audit/01_BRD-audit.md` (it
     does, from BRD-RT-001).
   - Add one sentence: "When `verdict.json` is present, prefer it for
     the blocking-findings list (deterministic JSON parse vs Markdown
     extraction). Fall back to the audit report when verdict.json is
     absent."
   - Update `<BRD-id>` path references to the short form.

5. **`tests/scripts/test-acceptance.sh` — Gaps B + D + audit timeout**:
   - Line 63: `MAX_LAYER_SEC=900` → `1800` with comment.
   - Lines 67-69: add `AUDIT_TIMEOUT=1200`; use it in `invoke_skill`
     (line ~430) when the skill name matches `*-audit`.
   - In `invoke_skill` after capturing `audit_score` from stdout, also
     read `.aidoc/review/<NN>_<LAYER>/<artifact-id>/verdict.json` if
     present. If `content_score` differs from the captured value, log
     a warning and prefer the JSON value.
   - Consider raising `MAX_TOTAL_OUTPUT_TOKENS` from `1_500_000` to
     `5_000_000` to accommodate worst-case team-mode full cascades.
     Decision deferred to operator preference; keep current value as
     default.

6. **Plugin version bump** 0.4.2 → 0.4.3: standard 9-place fanout —
   VERSION + plugin.json + marketplace.json + 52 skills' frontmatter
   `version:` + plugin README + root README + docs/PARITY.md +
   docs/TAGGING.md (new tag row) + SKILL_AUTHORING.md. Use the same
   Python bulk-bump pattern from BRD-RT-001 and PROFILE-DELTA-001.

7. **Plugin CHANGELOG entry** at
   `platforms/claude-code-plugin/CHANGELOG.md` under `[Unreleased] →
   Changed`. Documents all five gaps + the new verdict.json contract +
   per-skill audit timeout + per-layer cap raise.

8. **DECISIONS.md entry D-0026** at `plans/DECISIONS.md`:
   "Synthesizer writes a structured `verdict.json`; every verdict
   consumer (audit-skill stdout, driver, autopilot, fixer) reads from
   it. Markdown `report.md` is the human narrative, never the parse
   target."

9. **Verify** (see Verification section).

10. **Land** — single PR. No `framework/**` content touched;
    GATE-SPEC not applicable.

## Verification

Cheap-to-expensive ladder. Steps 1-3 are free. Steps 4-5 spend ~$10
total (two BRD-only live runs). Step 6 (full cascade) is the eventual
end-to-end confirmation but explicitly deferred — see Wall-clock
budget above.

1. **Static lint + conformance** (free, < 30s):

   ```sh
   env -u LD_LIBRARY_PATH pre-commit run --files \
     platforms/claude-code-plugin/agents/synthesizer.md \
     platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md \
     platforms/claude-code-plugin/skills/doc-brd-autopilot/SKILL.md \
     platforms/claude-code-plugin/skills/doc-brd-fixer/SKILL.md \
     platforms/claude-code-plugin/VERSION \
     platforms/claude-code-plugin/.claude-plugin/plugin.json \
     .claude-plugin/marketplace.json \
     tests/scripts/test-acceptance.sh \
     platforms/claude-code-plugin/CHANGELOG.md \
     plans/DECISIONS.md
   python3 -m unittest discover -s tests/conformance -v
   ```

   Pass criteria: pre-commit green; 96/96 conformance tests pass.

2. **Mock-mode acceptance** (free, < 1 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --no-live
   ```

   Pass criteria: PASS (7/0/44/51) — no regression on the deterministic
   path.

3. **Skill-text + script inspection** (free):

   - `agents/synthesizer.md` contains the `verdict.json` write
     instructions and the schema.
   - `doc-brd-audit/SKILL.md` contains the new Output Contract block
     reading from `verdict.json`.
   - `doc-brd-autopilot/SKILL.md` Workflow §5 cites `verdict.json` at
     `.aidoc/review/01_BRD/<BRD-id>/verdict.json` as the gate-decision
     source.
   - All BRD skill text uses `<BRD-id>` = short artifact ID consistently.
   - `tests/scripts/test-acceptance.sh` `MAX_LAYER_SEC=1800` and
     `AUDIT_TIMEOUT=1200`; `invoke_skill` cross-checks the JSON.

4. **Live BRD-only run, team mode** (~$5-7, ~15-20 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd --force
   ```

   Pass criteria (the load-bearing checks):
   - **`verdict.json` present** at
     `.aidoc/review/01_BRD/BRD-01/verdict.json` — structured JSON
     parseable by `json.loads`, all six top-level keys present.
   - **Driver and synthesizer agree**: the driver-reported
     `audit_score` in `summary.txt` matches `verdict.json:content_score`.
   - **Autopilot iterates on FAIL** (G3 — first live exercise of
     fixer team-mode behaviour): if `verdict.combined_status == FAIL`,
     the autopilot invokes `doc-brd-fixer`. The fix log
     (`elements/doc-brd-fixer.log`) shows non-zero
     `audit_score_after_fixer`.
   - **Fixer's lens-validation slots appear**:
     `.aidoc/review/01_BRD/BRD-01/<persona>.fix_<N>.json` files exist
     after the fix iteration.
   - **No per-layer cap abort**: the BRD layer completes within the
     new 1800-second cap.
   - **Slot files still produced** at
     `.aidoc/review/01_BRD/BRD-01/{business_analyst,architect,auditor,adversary}.json`
     (same as BRD-RT-001 Run #1).

   The expected outcome on the url-shortener BRD is that the autopilot
   tries to address BA-001 (visit-count contradiction) and other P1
   findings, re-audits, and either converges to PASS or escalates to
   manual-review after 3 iterations. Either way, the verdict chain is
   end-to-end consistent.

5. **Live BRD-only run, single_pass mode** (~$2-3, ~10 min):

   ```sh
   # Edit examples/url-shortener/.aidoc/profile.yaml — set
   # review_mode: single_pass
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd --force
   ```

   Pass criteria:
   - **Audit report includes the always-on advisory note** about
     `single_pass` being informational.
   - **No slot files produced** (override-respect still works).
   - **No `verdict.json`** (synthesizer doesn't run in single_pass —
     autopilot falls back to reading the audit report directly).
   - **Driver and audit report agree on the score** (both should
     report the same single-context-computed score).
   - **No regression** vs BRD-RT-001 Run #2's 93 PASS baseline.

6. **Full cascade verification** (~$15-25, defer): only after steps 1-5
   pass cleanly. See Wall-clock budget above — recommend running via
   `--run_in_background` or `nohup` overnight rather than blocking the
   terminal for 2-4 hours. Confirms:
   - Run all 8 layers without aborting under the new 1800s per-layer
     cap.
   - Each layer's driver-reported score matches its
     `verdict.json:content_score`.
   - Layer FAIL verdicts actually trigger fixer cycles.
   - Final summary reflects real per-layer team-mode verdicts.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Model still echoes the autopilot's self-claim despite the Output Contract instructions | Two layers: (a) verdict.json is structured JSON the synthesizer writes deterministically, so the audit skill's read-and-mirror task is now JSON parsing (more reliable than Markdown extraction). (b) Driver cross-check (Gap B) catches any remaining drift |
| R2 | Synthesizer's `verdict.json` write may itself drift (model omits a field, uses wrong type) | Schema is flat (no nesting beyond `coverage`); audit-skill stdout instruction explicitly cites every field name. Driver's cross-check logs a structured warning when JSON parse fails or expected key missing. Add to future BRD-RT-003 if drift becomes a pattern: validate JSON against a JSONSchema |
| R3 | Autopilot's revise loop now triggers fixer cycles that the fixer can't actually resolve (e.g. BA-001 needs a human business decision) | The fixer's existing `manual-required` confidence tag (BRD-RT-001) handles this — it'll mark the finding manual-review and halt after max iterations. Logs a clear escalation message |
| R4 | Raising `MAX_LAYER_SEC` to 1800s lets a stuck/runaway skill burn budget for twice as long before aborting | Inner backstop unchanged: per-skill `SKILL_TIMEOUT` (default 600s, audits now 1200s, review-team 1800s, agents 600s). Outer backstop: `--cost-cap` (cumulative output tokens). Per-layer cap is the middle guard |
| R5 | Full team-mode cascade exceeds the existing `MAX_TOTAL_OUTPUT_TOKENS=1_500_000` (~$22) cap | Plan recommends raising to 5M (~$75) for explicit team-mode full-cascade runs; default stays 1.5M for partial/single-layer runs. Operator can override per invocation. Verification step 4 (BRD-only) easily fits under 1.5M |
| R6 | Full cascade wall-clock budget is 3-4 hours typical, 6-8 worst-case | Operational pattern documented in Approach: run via background/overnight. Operator notified at completion. Per-skill timeouts catch stuck runs early |
| R7 | The always-on single_pass advisory note creates confusion ("am I supposed to ignore the score?") | Note explicitly says "informational"; doesn't change PASS/FAIL outcome. Shown only in audit report, not in driver summary. Users picking `single_pass` are making a deliberate cost-vs-rigor tradeoff per `ADAPTATION_SURFACE.yaml` |
| R8 | `<BRD-id>` path change (codifying short artifact ID) breaks something that hard-coded the long form | Inspection shows BRD-RT-001's implementation already used the short form (`BRD-01`); only the SKILL text descriptions referenced the long form. No code consumers depend on either form. Slot files at the new short-form path are what BRD-RT-001 actually produced |
| R9 | Per-skill audit timeout introduces inconsistency between layers (BRD audit at 1200s vs other-layer audits at 600s) | The name-match rule (`*-audit` → 1200s) applies uniformly across all 8 layers. When PRD-RT etc. propagate, their audits inherit the longer timeout automatically |
| R10 | Verification step 4 might not produce convergence to PASS (e.g., the BA-001 contradiction is unresolvable without a business decision) | Verification's pass criterion is **verdict-chain consistency** (driver ↔ verdict.json ↔ audit report all agree), not "audit reaches PASS". Either PASS-after-fix OR manual-review-after-3-iterations is a valid demonstrative outcome — both prove the chain works |

## Review log

### Pass 1 — 2026-06-03T17:53:34Z

Initial draft. Findings folded back into the sections above:

- Five gaps (A audit-stdout-mismatch, B driver-parses-wrong-source, C
  autopilot-reads-wrong-source, D per-layer-cap-too-tight, E
  single_pass-leniency) collapse into one root cause for A/B/C: the
  audit skill's stdout response diverges from the written report. Gap
  D is a one-line script tweak. Gap E is a doc-only advisory note.
- DECISIONS.md D-0026 captures the principle.
- Verification step 4 is the load-bearing check. Step 5 tests Gap E.
  Step 6 (full cascade) is the eventual confirmation, deferred.

### Pass 2 — 2026-06-03T17:53:34Z

Re-read whole plan. Verification calibration check confirmed each
pass criterion in steps 4 and 5 maps to a specific transformation
rule. No new findings.

### Pass 3 — 2026-06-03T18:25:00Z (gap-review amendment)

Comprehensive gap review of the Pass 1+2 plan identified ten gaps
(G1-G10). All folded back into the sections above:

- **G1 — Per-skill timeout interaction**: doc-brd-audit's 580s Run #1
  duration was perilously close to the 600s `SKILL_TIMEOUT`. With fix
  iterations now possible, duration can grow. Resolution: new
  `AUDIT_TIMEOUT=1200` applied via name-match (`*-audit`) in
  `invoke_skill`. Documented in Approach and Step 5.
- **G2 — Slot-directory path inconsistency** (`<BRD-id>`
  long-vs-short form): BRD-RT-001's implementation already picked the
  short artifact ID (`BRD-01`); only the SKILL text used the long
  form. Codified the short form in Scope, Approach, and all Step
  references. R8 captures the (low) backward-compat risk.
- **G3 — Fixer team-mode behaviour unverified by any prior live
  run**: BRD-RT-001's runs never reached the fixer because the
  autopilot mis-read the verdict as PASS. Explicit Verification
  step 4 sub-criterion added: "Fixer's lens-validation slots appear
  at `<persona>.fix_<N>.json`". Step 4 description now calls out
  "first live exercise of team-mode fixer behaviour".
- **G4 — Full-cascade cost & wall-clock budget missing**: new
  "Wall-clock budget" subsection in Approach quantifies per-layer and
  full-cascade scenarios (~2-8 hours; ~$40-180). R5 and R6 add the
  cost-cap-raise and operational-pattern mitigations.
- **G5 — Markdown `report.md` is the wrong parse target**: structural
  fix is to have the synthesizer write a deterministic `verdict.json`
  companion. New file added to Scope (In):
  `platforms/claude-code-plugin/agents/synthesizer.md`. New Step 1
  added. Audit skill's Output Contract (Gap A) and autopilot's revise
  loop (Gap C) now read JSON, not Markdown. R2 captures the
  json-write-drift risk.
- **G6 — "At a gate" condition for the single_pass advisory**: skill
  cannot reliably know its trigger context. Simplified to "always
  show advisory when single_pass resolves". R7 captures the
  user-confusion risk (mitigated by explicit "informational" wording).
- **G7 — PRD..IPLAN inherit the same pattern**: explicit note added in
  Scope (Out). Per-layer follow-up PRs (PRD-RT-001, EARS-RT-001, etc.)
  copy the verdict.json + Output Contract + always-on advisory
  pattern verbatim per layer.
- **G8 — Exact line/section anchors**: Step sequence now cites the
  insertion point for each edit (line numbers + section names) so
  reviewers can find the targets without grep.
- **G9 — Reference `invoke_skill` bash function**: Gap B fix in
  Approach and Step 5 now cite `invoke_skill` (line ~430 of
  `test-acceptance.sh`) as the specific code location.
- **G10 — Prose redundancy**: kept the per-gap fix shapes consolidated
  in the Approach section. Step sequence cites the Approach
  paragraphs by gap label rather than restating the fix.

Additional consequential changes from the gap review:

- Risks table grew from 8 to 10 entries (added R5 cost-cap, R9
  per-skill timeout, R10 verification-doesn't-have-to-converge to
  replace original R8 plus new framing).
- Step sequence grew from 9 steps to 10 (new Step 1 for synthesizer
  agent; old Steps 1-9 renumbered 2-10).
- Scope (In) added `agents/synthesizer.md` and explicit
  per-skill-timeout name-match rule.
- Scope (Out) explicitly enumerates that PRD..IPLAN follow-ups reuse
  this pattern verbatim — they don't need their own plans for the
  verdict.json contract, only layer-specific applications.

No false-positives or false-negatives in the gap analysis: each
identified gap maps to a concrete fix shape in the Approach section
and a verification criterion (where verifiable).

Plan is ready for implementation. Scope grew modestly (added one file:
`agents/synthesizer.md`; one new constant: `AUDIT_TIMEOUT`); the core
architectural shape is unchanged.
