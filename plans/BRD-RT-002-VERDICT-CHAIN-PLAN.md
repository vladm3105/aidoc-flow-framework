# BRD-RT-002 Plan — Wire the audit → autopilot verdict chain through the written reports

| Field      | Value                                       |
|------------|---------------------------------------------|
| Task       | BRD-RT-002                                  |
| Depends on | BRD-RT-001 (D-0024, merged), PROFILE-DELTA-001 (D-0025, merged) |
| Status     | PLANNED — 2026-06-03T17:53:34Z              |
| Feeds      | PRD-RT, EARS-RT, BDD-RT, ADR-RT, SPEC-RT, TDD-RT, IPLAN-RT — these per-layer follow-ups inherit the corrected verdict-chain semantics from this PR |

## Objective

Close five gaps surfaced by the BRD-RT-001 live verification runs
(2026-06-03) so team-mode review produces **the same verdict at every
consumer** — audit-skill stdout, written audit report, driver script,
autopilot revise loop — and the per-layer runtime cap stops aborting
legitimate team-mode runs. After this PR, a team-mode audit that
computes FAIL actually triggers the fixer; a `single_pass` audit at a
gate is marked advisory; and a full-cascade team-mode run no longer
hits the 900-second cap on every layer.

## Scope

**In:**

- `doc-brd-audit/SKILL.md` — team-mode branch must instruct the model
  to mirror the synthesizer's deterministic verdict in its stdout
  response (the skill's "return value"). Today the model echoes the
  autopilot's self-claim instead.
- `doc-brd-autopilot/SKILL.md` — the create→review→revise loop must
  read its PASS/FAIL decision from the *written* audit report at
  `.aidoc/audit/01_BRD-audit.md` and the synthesizer's
  `.aidoc/review/01_BRD/<BRD-id>/report.md`, not from the audit
  subagent's verbal response.
- `doc-brd-fixer/SKILL.md` — minor confirmation that the fixer consumes
  the written report + slots (already does in the BRD-RT-001 text;
  verify and add an assertion if needed).
- `tests/scripts/test-acceptance.sh` — raise `MAX_LAYER_SEC` from 900 to
  1800 (mode-agnostic; team-mode legitimately runs ~17-25 min per
  layer). Optionally also cross-check the captured `audit_score`
  against the written report file as belt-and-suspenders.
- `doc-brd-audit/SKILL.md` Combined Report Format — when `review_mode:
  single_pass` is used at a gate (`pre_promotion`/`pre_merge`), include
  an explicit **advisory note**: result is informational only;
  `team` mode is the canonical gate per `REVIEW_TEAM.md`. (Doc-only;
  doesn't change behavior.)
- Plugin version bump 0.4.2 → 0.4.3.
- Plugin CHANGELOG entry.
- `plans/DECISIONS.md` D-0026 — "Audit skill's stdout response is its
  verdict; written report is the authoritative reference."

**Out:**

- Framework spec changes — none required. `REVIEW_TEAM.md` already says
  the synthesiser's reduce is deterministic and authoritative; this PR
  is the plugin's binding catching up to the spec.
- PRD..IPLAN layer wiring — propagation deferred until BRD-RT-002 is
  verified live (full cascade) so the corrected pattern propagates
  cleanly.
- Driver script source-of-score refactor — the simplest fix is at the
  skill side (Gap A). Driver cross-check is optional belt-and-suspenders;
  keep minimal.
- A new conformance test that asserts stdout/report score match —
  potentially valuable but model-output behavior is hard to assert
  deterministically; defer until BRD-RT-002 + PRD-RT show consistent
  results across runs.
- `single_pass` deprecation — single_pass remains a first-class fallback
  (e.g. for `on_author`, partial-quorum runs, cost-constrained
  environments). Only the *advisory framing* at gates changes.
- Hermes-side parity — Hermes implements its own runtime; this PR is
  plugin-only.
- Caching follow-up (`REVIEW-TEAM-RUNNER-CACHING-001`) — separate v0.4.4
  work; orthogonal optimisation.

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

This is the root cause of Gaps A, B, and C from the post-Run-#1
discussion. They share one fix: the audit skill's text must make the
model output the synthesizer's verdict in its terminal response.

### Fix shape per gap

**Gap A — `doc-brd-audit/SKILL.md` team-mode branch.** Add an explicit
"Output contract" subsection inside the team-mode branch:

```
After the synthesizer writes `report.md`, read it back, extract
`combined_status` / `content score` / `coverage.quorum_met`, and produce
your terminal stdout response in the exact shape:

  Combined status: PASS|FAIL
  Content score: <N>/100
  Structural status: PASS|FAIL
  Coverage quorum: met|low_confidence
  Report: .aidoc/audit/01_BRD-audit.md

Do NOT echo the BRD's self-claimed PRD-Ready score. The synthesizer's
report.md is the authoritative verdict; your response mirrors it.
```

**Gap C — `doc-brd-autopilot/SKILL.md` Workflow §5 (revise step).** Make
the read-source explicit:

```
After invoking `../doc-brd-audit/SKILL.md`, decide pass/fail by READING
the written report at `.aidoc/audit/01_BRD-audit.md`:
  - Combined status: FAIL → invoke `../doc-brd-fixer/SKILL.md`, GOTO step 4
  - Coverage quorum: low_confidence → flag manual-review, halt
  - Combined status: PASS → finalize

Do NOT make this decision from the audit subagent's stdout summary or
from the BRD's self-claimed PRD-Ready score. The written audit report
is the gate; everything else is advisory.
```

**Gap B — driver belt-and-suspenders (optional).** In
`tests/scripts/test-acceptance.sh`, after `invoke_skill "doc-brd-audit"`,
parse `Content score:` from `.aidoc/audit/01_BRD-audit.md` and overwrite
the captured `audit_score` if it differs. Logs a warning when the two
disagree. This catches future drift without forcing the model to be
perfect.

**Gap D — per-layer cap.** Raise `MAX_LAYER_SEC=900` to `MAX_LAYER_SEC=1800`
with an updated comment explaining the rationale (team mode at one
layer = 4 review subagents in parallel + synthesizer + author + fixer
loop iteration, naturally 15-25 minutes).

**Gap E — single_pass advisory note at gates.** Add to
`doc-brd-audit/SKILL.md` combined report format:

```
When `review_mode: single_pass` is used at a gate (pre_promotion /
pre_merge), include this advisory in the report summary:

  > **Advisory mode.** This audit ran in `single_pass` — one model
  > applying every lens in one context. Per REVIEW_TEAM.md §"Scoring,
  > conflicts & the gate", `team` mode is the canonical gate review;
  > `single_pass` is a cost-constrained fallback whose lens
  > independence is reduced. Score 0-100 here is informational; a
  > production gate run should re-audit in `team` mode.
```

## Step sequence

1. **`doc-brd-audit/SKILL.md` — Gap A + Gap E**:
   - Add `## Output Contract` subsection inside team-mode branch
     describing the exact terminal-stdout shape (mirrors synthesizer's
     verdict).
   - Add `single_pass` advisory note paragraph in Combined Report
     Format when the run is at a gate trigger.

2. **`doc-brd-autopilot/SKILL.md` — Gap C**:
   - Workflow §5 (revise) explicitly reads `.aidoc/audit/01_BRD-audit.md`
     for the gate decision, not the audit subagent's stdout.
   - Make the read-from-report behaviour symmetric across both team and
     single_pass modes.

3. **`doc-brd-fixer/SKILL.md` — confirmation**:
   - Verify Input Contract already says "consume the latest audit
     report from `.aidoc/audit/01_BRD-audit.md`". It does (post
     BRD-RT-001). Add a one-sentence reminder that the report is
     authoritative for fix triggering.

4. **`tests/scripts/test-acceptance.sh` — Gaps B + D**:
   - `MAX_LAYER_SEC=900` → `MAX_LAYER_SEC=1800` with comment.
   - Optional belt-and-suspenders: after capturing audit_score from the
     skill's stdout, also read the written report's "Content score"
     line. Log warning if they differ; prefer the report's value.

5. **Plugin version bump** 0.4.2 → 0.4.3: VERSION + plugin.json +
   marketplace.json + 52 skills' frontmatter `version:` + plugin README
   - root README + docs/PARITY.md + docs/TAGGING.md (new tag row) +
   SKILL_AUTHORING.md.

6. **Plugin CHANGELOG entry** at
   `platforms/claude-code-plugin/CHANGELOG.md` under
   `[Unreleased] → Changed` documenting Gaps A/B/C/D/E and the
   underlying verdict-chain consistency fix.

7. **DECISIONS.md entry D-0026** at `plans/DECISIONS.md`:
   "Audit skill's stdout response is its verdict; the written report is
   the authoritative reference, and every consumer (driver, autopilot
   revise loop, fixer) reads from the report file."

8. **Verify** (see Verification section).

9. **Land** — single PR. No framework/** content touched; GATE-SPEC not
   applicable.

## Verification

Cheap-to-expensive ladder. Steps 1-3 are free. Steps 4-5 spend ~$10
total (two BRD-only live runs).

1. **Static lint + conformance** (free, < 30s):

   ```sh
   env -u LD_LIBRARY_PATH pre-commit run --files \
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

3. **Skill-text inspection** (free):

   - `doc-brd-audit/SKILL.md` contains the new Output Contract block.
   - `doc-brd-autopilot/SKILL.md` Workflow §5 cites
     `.aidoc/audit/01_BRD-audit.md` as the gate-decision source.
   - `tests/scripts/test-acceptance.sh` `MAX_LAYER_SEC=1800`.

4. **Live BRD-only run, team mode** (~$5-7, ~15-20 min):

   ```sh
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd --force
   ```

   Pass criteria (the load-bearing checks):
   - **Driver and synthesizer agree**: the driver-reported
     `audit_score` in `summary.txt` matches the synthesizer's
     `Content score` in `.aidoc/audit/01_BRD-audit.md`.
   - **Autopilot iterates on FAIL**: if synthesizer says FAIL with P1
     findings, the autopilot invokes `doc-brd-fixer`. The fix-iteration
     log (`elements/doc-brd-fixer.log`) shows non-zero
     `audit_score_after_fixer`.
   - **No per-layer cap abort**: the BRD layer completes within the
     new 1800-second cap.
   - **`.aidoc/review/01_BRD/<BRD-id>/` slots present** (same as Run #1).

   The expected outcome on the url-shortener BRD is that the autopilot
   tries to address BA-001 (visit-count contradiction) and other P1
   findings, re-audits, and either converges to PASS or escalates to
   manual review after 3 iterations. Either way, the verdict chain is
   end-to-end consistent.

5. **Live BRD-only run, single_pass mode** (~$2-3, ~10 min):

   ```sh
   # Edit examples/url-shortener/.aidoc/profile.yaml — set review_mode: single_pass
   bash tests/scripts/test-acceptance.sh url-shortener --live \
        --phase=cascade --from-layer=brd --to-layer=brd --force
   ```

   Pass criteria:
   - **Audit report includes the new advisory note** about
     `single_pass` being informational at gates.
   - **No slot files produced** (override-respect still works).
   - **Driver and audit report agree on the score** (both should
     report the same single-context-computed score).
   - **No regression vs Run #2's 93 PASS baseline**.

6. **Full cascade verification** (~$15-25, defer): only after steps 1-5
   pass cleanly. With the new 1800-second cap and corrected verdict
   chain, a full cascade should:
   - Run all 8 layers without aborting.
   - Each layer's driver-reported score matches its written audit
     report.
   - Layer FAIL verdicts actually trigger fixer cycles (which they
     don't today on BRD).
   - Final summary reflects real per-layer team-mode verdicts.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Model still echoes the autopilot's self-claim despite the new Output Contract instructions | Belt-and-suspenders: driver cross-checks the written report's score (Gap B fix). When they disagree, log a warning and prefer the report. Catches stochastic drift without forcing the model to be perfect every time |
| R2 | Autopilot's revise loop now triggers fixer cycles that the fixer can't actually resolve (e.g. BA-001 needs a human business decision: "exact counting" vs "1% tolerance") | The fixer's existing `manual-required` confidence tag (BRD-RT-001) handles this — it'll mark the finding manual-review and halt after max iterations. Logs a clear escalation message |
| R3 | Raising `MAX_LAYER_SEC` to 1800s lets a stuck/runaway skill burn budget for twice as long before aborting | The `--cost-cap=$22` token-budget guard still fires across the run. Per-skill timeouts (600s default, 1800s review-team, 600s agents) remain as the inner backstop. Per-layer cap is the outer guard for "one layer accidentally runs forever" |
| R4 | Full cascade with team mode at every layer × 3 fix iterations × 8 layers = potentially very long run | Realistic upper bound: 8 layers × 25 min/layer = ~3.3 hours wall-clock; cost-cap halts at $22 well before that. Operator can also use `--from-layer`/`--to-layer` for partial cascades. Same `--cost-cap` and per-layer caps remain in force |
| R5 | The single_pass advisory note creates confusion about whether single_pass results are "trustworthy" | Note explicitly says "informational"; doesn't change PASS/FAIL outcome. Users picking `single_pass` are making a deliberate cost-vs-rigor tradeoff per `ADAPTATION_SURFACE.yaml` |
| R6 | Gap E (single_pass leniency) is a structural property of single-context lens simulation, not fixable by note alone | The note is a UX patch; the structural fix is "don't use single_pass at gates", which the framework already recommends. This PR doesn't try to *prevent* single_pass at gates — that's a project-policy decision |
| R7 | Per-layer cap raise to 1800s breaks any existing CI workflow that expected 900s | Search confirms no CI workflow hardcodes 900s; the cap is internal to `test-acceptance.sh`. Per-layer-cap is a runtime safety belt, not a contract |
| R8 | Verification step 4 might not produce convergence to PASS (e.g., the BA-001 contradiction is unresolvable without a business decision) | Verification's pass criterion is "verdict chain is consistent", not "audit reaches PASS". Either PASS-after-fix OR manual-review-after-3-iterations is a valid demonstrative outcome — both prove the chain works |

## Review log

### Pass 1 — 2026-06-03T17:53:34Z

Initial draft. Findings folded back into the sections above:

- The five gaps from the BRD-RT-001 live runs (A audit-stdout-mismatch,
  B driver-parses-wrong-source, C autopilot-reads-wrong-source, D
  per-layer-cap-too-tight, E single_pass-leniency) collapse into one
  root cause for A/B/C: the audit skill's stdout response diverges
  from the written report. Gap D is a one-line script tweak. Gap E is
  a doc-only advisory note. All five fit in one PR.
- Plugin version bump 0.4.2 → 0.4.3 plus standard fanout. No framework
  spec change → no GATE-SPEC ceremony.
- DECISIONS.md D-0026 captures the architectural principle: "audit
  skill's stdout response IS its verdict; written report is the
  authoritative reference; consumers read from the report".
- Verification step 4 is the load-bearing check — it tests all three
  Gap A/B/C fixes simultaneously. Step 5 tests Gap E. Step 6 (full
  cascade) is the eventual end-to-end confirmation but deferred until
  steps 1-5 pass.
- R8: verification pass-criterion is verdict-chain consistency, NOT
  reaching PASS on this specific BRD. The url-shortener BRD has real
  spec issues (BA-001) that might be unresolvable by automated fixer
  without a business decision — that's a valid outcome and still
  proves the chain works.
- Defer making single_pass advisory-mandatory at gates — that's a
  project policy decision, not a framework rule.

### Pass 2 — 2026-06-03T17:53:34Z

Re-read whole plan. No new findings.

- **Verification calibration**: each pass criterion in steps 4 and 5
  maps to a specific transformation:
  - Gap A fix (audit Output Contract) → "driver and synthesizer
    agree on score" (step 4)
  - Gap B fix (driver cross-check) → same as above (the cross-check
    is what guarantees the agreement)
  - Gap C fix (autopilot reads written report) → "autopilot iterates
    on FAIL" (step 4) — observable via fixer-loop activation
  - Gap D fix (cap raise) → "no per-layer cap abort" (step 4)
  - Gap E fix (advisory note) → "audit report includes advisory note"
    (step 5)
  No false positives (each rule's output trips a check) or false
  negatives (no rule's output is unchecked).
- **Scope check**: every "Out:" item has a clear deferral target.
  PRD..IPLAN propagation is gated on this PR's verification success.
  Single_pass deprecation is explicitly a project-policy decision.
- **Risks check**: 8 risks identified. R1 (model behavior unreliable)
  is the most material; mitigated by the driver cross-check
  belt-and-suspenders. R8 (verification might not converge to PASS)
  is real but doesn't invalidate the verification — chain consistency
  is the metric, not score outcome.
- **Backward-compat check**: no `framework/**` change; existing
  projects continue working; team-mode runs that succeeded under
  BRD-RT-001 continue to succeed. The new behaviour is purely
  additive (more accurate verdict reporting, longer per-layer cap,
  optional advisory note).
- **Cost check**: verification cost ~$10 total (steps 4 + 5).
  Full-cascade verification at step 6 is deferred and gates further
  per-layer propagation. No surprise spend.

Plan ready for implementation.
