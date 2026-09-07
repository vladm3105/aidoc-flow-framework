# HERMES-REVIEW-CALIBRATION Plan (H-6.1 + H-6.2) — no-findings rationale cap + strip author self-claim

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-REVIEW-CALIBRATION (H-6.1 + H-6.2)   |
| Type           | feature (reviewer-calibration parity)       |
| Status         | IMPLEMENTED — 2026-07-04 (3 review passes, 1 independent; all V-checks green) |
| Depends on     | none (Phase-2 review-team plumbing already shipped) |
| Feeds          | Hermes review-quality parity with the plugin (FRAMEWORK-CLEANUP-001 PR-B heart) |
| Version impact | **Hermes MINOR** (`0.5.1 → 0.6.0`). **No framework change** — both contracts already exist in `REVIEW_TEAM.md` + the injected playbooks; this is pure consumer-side enforcement. No GATE-SPEC, no re-vendor. |

## Objective

Two of the three FRAMEWORK-CLEANUP-001 "PR-B heart" review-calibration deltas
(H-6) are consumer-side gaps in Hermes's team-mode review path — the framework
spec contract (`REVIEW_TEAM.md`) and the injected playbooks already carry them,
but Hermes doesn't enforce them:

1. **No-findings rationale (H-6.1).** A lens returning `lens_score: 100` with
   `findings: []` MUST supply a `no_findings_rationale`; the synthesizer caps the
   lens at 95 (advisory `STRUCTURE-RAT-001`) when it's absent — a nudge against
   "convergence theater." Hermes's parser doesn't capture the field and its scorer
   never caps. **Additionally, Hermes's parser currently mishandles a clean
   zero-findings response** — a valid `findings: []` payload falls through the
   `if findings:` guard to the `fallback` path, which returns `lens_score=None`. The
   fan-in then *drops* that lens from `lens_scores` (the `isinstance(..., (int,float))`
   guard skips `None`), so a legitimate 100/0 lens becomes a **missing** persona that
   lowers coverage — and the cap is unreachable because the lens never has a score to
   cap. (In crew/playbook mode the spurious fallback P1 is itself discarded by the
   citation floor as uncited, so the damage is the dropped score, not a polluted
   findings list.) This plan fixes the parser to preserve `lens_score` on a clean
   empty result, making no-findings enforcement reachable.
2. **Strip author self-claim (H-6.2).** Self-assessment fields (`*_ready_score`,
   `*_score`, `readiness_score`, `audit_score`) in the artifact body anchor the lens
   score. Engines MUST strip them from the body before each lens sees it. Hermes
   passes the raw `sections` to every branch untouched.

The third H-6 item (**fixer-introduced regression detection**) is **out of scope**:
it requires an iter-N vs iter-(N-1) comparison, and Hermes's saga is **single-pass**
(`iteration` is hardcoded to 1) — there is no prior iteration to compare against. It
is blocked on a separate "Hermes multi-iteration quality loop" initiative.

## Scope

**In:**

- **Parser (`persona_output_parser.py`):**
  - Extract a top-level `no_findings_rationale` (string) from the persona payload,
    like `_coerce_lens_score` does for `lens_score`.
  - Add `no_findings_rationale: str | None = None` to `PersonaParseResult`.
  - **Fix the empty-findings→fallback bug:** when a candidate parses as valid JSON
    carrying a `findings` key that coerces to an **empty** list (and a `lens_score`
    is present), return a *successful* empty `PersonaParseResult`
    (`findings=[]`, the real `parse_status`, `lens_score`, `no_findings_rationale`)
    instead of continuing to the `fallback` P1 path. The fallback stays for genuinely
    unparseable output (no JSON / no `findings` key).
- **Branch result (`saga_orchestrator.py` `_branch_llm_findings`, `:476`):** add
  `"no_findings_rationale": parsed.no_findings_rationale` to the returned dict.
- **Fan-out collection (`saga_orchestrator.py`, `:644`/`:717-726`):** track two new
  per-persona maps — `personas_with_findings: set[str]` (branch contributed ≥1
  post-filter finding) and `no_findings_rationales: dict[str, str | None]` — and pass
  them to the score computation.
- **Scoring (`review_scoring.py` `score_review`):** two new optional params
  `lens_findings_count: dict[str, int] | None` and
  `no_findings_rationale: dict[str, str | None] | None` (persona-keyed, canonicalized
  inside). For each ran lens with `lens_score == 100`, zero findings, and no/empty
  rationale, **cap that lens to 95** before the weighted average and record the
  persona in a new `ReviewScore.rationale_capped: list[str]`. `_compute_review_score`
  surfaces `rationale_capped` as `STRUCTURE-RAT-001` advisories in the verdict dict.
- **Self-claim strip (`saga_orchestrator.py`):** a helper
  `_strip_author_self_claim(sections)` redacts the canonical field patterns
  (`REVIEW_TEAM.md:86-89`) from each `SourceSection.content`; call it **once** on
  `sections` at the top of `run_project_review_build_saga` before the fan-out loop,
  so every branch (LLM + prompt mode) sees the stripped body. On-disk artifact is
  untouched (in-prompt only).
- Hermes `0.5.1 → 0.6.0`; Hermes CHANGELOG; root CHANGELOG (Hermes entry); D-0049;
  H-6 partial-close in `HERMES-BACKLOG.md` (6.1+6.2 done, 6.3 blocked); HANDOFF.

**Out of scope (deferred):**

- **H-6.3 (fixer-introduced regression detection).** Blocked — Hermes saga is
  single-pass (`saga_orchestrator.py:614` `iteration=1`); no iter-(N-1) findings or
  "Fixes Applied" state exists to compare. Belongs to a future Hermes
  multi-iteration review-loop initiative, not this plan.
- **H-2 (REVIEW-CALIBRATION-001 sub-checks A1/A2/A3/BA1/SE1).** These live **only**
  in the plugin's `doc-*-audit/SKILL.md`, NOT the shared `framework/playbooks/`, so
  they cannot reach Hermes via playbook injection. Porting them into the shared
  playbooks is a **framework-spec** change (review-team calibration decision across
  many playbook files) with zero Hermes code — a separate plan, not bundled here.
- **H-7 spec/registry deltas** (`quality_loop_max_iterations`, `@threshold:` lint).

## Approach / Design (D-0049)

### H-6.1 — no-findings rationale (parser + scorer)

Three coupled edits:

1. **Parser captures the field + represents clean-empty.** Add
   `_coerce_no_findings_rationale(payload)` (mirrors `_coerce_lens_score`, `:79`).
   In `parse_persona_output`, when a candidate parsed as a **valid dict with a
   `lens_score` present and zero coerced findings** (whether via an explicit
   `findings: []` or no `findings` key at all), return
   `PersonaParseResult(findings=[], parse_status=<status>, lens_score=lens_score,
   no_findings_rationale=<rationale>)` — a successful empty result that **preserves
   the score**. This is what makes the cap reachable (today such a lens becomes a
   `fallback` with `lens_score=None`, dropping it from `lens_scores`). Keying on
   "valid dict + `lens_score` present + zero findings" (rather than strictly "had a
   `findings` key") also handles the `{"lens_score": 100}` shape. Genuinely-broken
   output (no parseable JSON, or a dict with no `lens_score` AND no findings) still
   yields the diagnostic `fallback` P1.
2. **Scorer caps at 95.** `score_review` gains `lens_findings_count` +
   `no_findings_rationale`. Inside, over the `ran` lenses: if
   `canonical_scores[p] == 100` and `lens_findings_count.get(p, 0) == 0` and not
   `no_findings_rationale.get(p)`, set `canonical_scores[p] = 95.0` and append `p`
   to `rationale_capped`. The cap happens **before** `raw_weighted` is computed, so
   the lens contributes 95 to the weighted average. `ReviewScore` gains
   `rationale_capped: list[str]` (default empty).
3. **Verdict surfaces the advisory.** `_compute_review_score` maps each capped
   persona to a `STRUCTURE-RAT-001` advisory entry in its returned dict (new
   `advisories` / `rationale_capped` key), consistent with the "advisory in the
   verdict" wording of `REVIEW_TEAM.md:102`.

Per the spec (`REVIEW_TEAM.md:107-108`): **filing any finding (P3 included) bypasses
the requirement** — so a lens with ≥1 finding is never capped regardless of score.
The `lens_findings_count == 0` guard delivers exactly that.

**Where "zero findings" is measured:** at fan-out collection, a persona is in
`personas_with_findings` iff its branch returned ≥1 finding *after* the citation
floor (`filter_findings`) already ran inside `_branch_llm_findings` (`:474`). A lens
whose findings were all discarded as uncited contributes zero — treated as
no-findings for the cap, which is the correct "unsubstantiated 100" case.

### H-6.2 — strip author self-claim before fan-out

`_strip_author_self_claim(sections: list[SourceSection]) -> list[SourceSection]`
returns new frozen `SourceSection`s with `content` redacted of lines assigning the
canonical self-claim fields. Patterns (from `REVIEW_TEAM.md:86-89`): any key ending
`_ready_score` or `_score`, plus literal `readiness_score` / `audit_score`. Match
YAML/markdown-ish `^\s*<key>\s*[:=].*$` lines (case-insensitive) and drop the value
(replace the line, or elide it). Applied once to `sections` at the top of
`run_project_review_build_saga` (before the `while` fan-out loop, `:646`), so both
`_branch_llm_findings` (`:682`) and `_branch_prompt_findings` (`:699`) receive the
stripped list. The change is **in-prompt only** — the on-disk artifact keeps the
fields (`REVIEW_TEAM.md:91-92`).

The canonical `*_score` pattern (`REVIEW_TEAM.md:87`) matches any body key ending
`_score` — including domain fields a real artifact might carry (`risk_score: 3`,
`credit_score: …`). Those would be redacted in the lens brief too. This is
**spec-mandated and in-prompt-only** (the on-disk artifact keeps them), matching the
plugin's behavior, so it's acceptable — but the strip is deliberately broad, not a
narrow all/deny list. `lens_score` itself is a review-*output* field, never present
in a source body, so there's no self-referential loop. Section `content` is the
artifact body (frontmatter included — sections are built from the whole file), so
the redaction reaches YAML self-claim frontmatter as intended.

### Versioning

Hermes-only; no `framework/` file changes (the contracts already exist in
`REVIEW_TEAM.md` + playbooks). New observable behavior (a lens can now be capped at
95; stripped bodies reach lenses; `STRUCTURE-RAT-001` advisories appear) → **Hermes
MINOR** `0.5.1 → 0.6.0`. No GATE-SPEC (no framework change), no plugin re-vendor.

### Backward-compatibility

All new params are optional/defaulted; `ReviewScore.rationale_capped` defaults empty;
`PersonaParseResult.no_findings_rationale` defaults `None`. Existing callers and
tests that don't pass the new score_review params get identical scores (no lens is
capped when the maps are absent). The parser's clean-empty path only changes the
outcome for payloads that previously became a `fallback` P1 — a strict improvement.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/src/mcp_server/review/persona_output_parser.py` | capture `no_findings_rationale`; add it to `PersonaParseResult`; return clean-empty result instead of fallback on empty `findings` |
| `platforms/hermes/src/mcp_server/review/review_scoring.py` | `score_review` gains `lens_findings_count` + `no_findings_rationale` params + the 95-cap; `ReviewScore.rationale_capped` |
| `platforms/hermes/src/mcp_server/review/saga_orchestrator.py` | `_branch_llm_findings` returns rationale; fan-out tracks `personas_with_findings` + `no_findings_rationales`; `_compute_review_score` applies/surfaces the cap; `_strip_author_self_claim` helper called once before fan-out |
| `platforms/hermes/tests/…` | unit tests: parser clean-empty + rationale; score_review 95-cap; strip helper; an integration assertion |
| `platforms/hermes/VERSION` (→ `0.6.0`) + Hermes CHANGELOG + root CHANGELOG | version + entries |
| `plans/DECISIONS.md` (D-0049) / `plans/HERMES-BACKLOG.md` (H-6 partial) / `plans/HANDOFF.md` | docs |

## Implementation sequence

### Task 1: parser — capture rationale + fix clean-empty — [CODE]

- Add `_coerce_no_findings_rationale`; thread `no_findings_rationale` into
  `PersonaParseResult`; return a successful empty result when the payload had a
  `findings` key coercing to `[]`. Unit tests: (a) 100/0 + rationale → empty
  findings, rationale captured, no fallback; (b) 100/0 without rationale → empty,
  rationale `None`; (c) unparseable → still `fallback` P1.

### Task 2: scorer — 95 cap + advisory — [CODE]

- `score_review` new params + cap + `rationale_capped`. Unit tests: lens 100/0/no
  rationale → capped 95 + listed; lens 100/0/with rationale → not capped; lens 100
  with ≥1 finding → not capped; absent maps → unchanged (back-compat).

### Task 3: orchestrator wiring + strip — [CODE]

- Return rationale from `_branch_llm_findings`; collect `personas_with_findings` +
  `no_findings_rationales`; pass to `_compute_review_score`; surface
  `STRUCTURE-RAT-001` advisories. Add `_strip_author_self_claim` + call once before
  fan-out. Unit test the strip helper (fields gone from content, other content
  intact, frontmatter-agnostic).

### Task 4: version + docs

- Hermes `0.6.0`; Hermes + root CHANGELOG; D-0049; HERMES-BACKLOG H-6 partial-close;
  HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | parser: 100/0 + rationale | empty findings, `no_findings_rationale` captured, **`lens_score == 100` preserved**, `parse_status` != `fallback` | H-6.1 parse |
| V2 | parser: 100/0 without rationale | empty findings, rationale `None`, **`lens_score == 100` preserved**, not `fallback` | H-6.1 parse |
| V3 | parser: unparseable output | still emits the `fallback` P1 finding | no regression |
| V4 | `score_review`: lens 100 / 0 findings / no rationale | that lens capped to 95; persona in `rationale_capped` | H-6.1 cap |
| V5 | `score_review`: lens 100 / 0 findings / with rationale | not capped (stays 100) | H-6.1 bypass |
| V6 | `score_review`: lens 100 / ≥1 finding | not capped (findings bypass rationale) | H-6.1 bypass |
| V7 | `score_review`: new params omitted | identical score to pre-change | back-compat |
| V7b | `score_review`: a `chairperson` (→`synthesizer`) lens 100/0/no-rationale, maps keyed by Hermes name | capped 95 — the new maps are canonicalized via `canonical_persona`, so the alias lens is not silently missed | H-6.1 key-mapping |
| V8 | `_strip_author_self_claim` on a body with `brd_ready_score: 92` + `audit_score: 88` | both lines gone from `content`; unrelated content intact | H-6.2 |
| V9 | `python -m pytest platforms/hermes/tests -q` | green (new + existing) | no regression |
| V10 | `python -m pytest tests/conformance -q` | green (no framework change; nothing should shift) | no regression |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[0.6.0]`
- [ ] root `CHANGELOG.md` — Hermes `0.5.1 → 0.6.0` calibration entry
- [ ] `plans/DECISIONS.md` — D-0049
- [ ] `plans/HERMES-BACKLOG.md` — H-6 partial (6.1 + 6.2 done; 6.3 blocked)
- [ ] `plans/HANDOFF.md` — arc progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The clean-empty parser change regresses a test asserting a fallback finding on empty input | med | V3 preserves fallback for genuinely-unparseable output; the change only affects payloads with a real `findings: []` key — grep the Hermes tests for existing empty-findings assertions and update if any |
| R2 | Capping in `score_review` changes an existing test's expected score | med | V7: the cap only triggers with the new maps populated AND a 100/0/no-rationale lens; existing callers omit the maps → no cap. Audit `_compute_review_score` callers |
| R3 | `_strip_author_self_claim` redacts a legitimate domain field ending `_score` (`risk_score`) or a prose line mentioning "score" | low | match only assignment lines `^\s*<key>\s*[:=]` (not prose substrings); the `*_score`-domain-field case is spec-mandated + in-prompt-only (on-disk artifact unchanged) so it's parity-correct, not a defect; V8 asserts unrelated prose content survives |
| R4 | `personas_with_findings` measured post-citation-floor: a lens that filed only *uncited* findings is capped, a **literal divergence** from the spec's "filing any finding (P3 included) bypasses" (`REVIEW_TEAM.md:106-107`) | low | **deliberate**: an all-discarded lens contributed no *substantiated* finding → its 100 is unsubstantiated → cap matches the "convergence theater" intent (`REVIEW_TEAM.md:104-108`). The independent review endorsed this as a legitimate design call. Documented here so it's a known, intentional divergence, not a silent one |
| R5 | Hermes MINOR vs PATCH mis-call | low | new observable behavior (capped scores, stripped bodies, advisories) → MINOR is correct per `docs/PROJECT.md` §2 |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `PersonaParseResult` carries only `findings`/`parse_status`/`lens_score` (no rationale) | `PersonaParseResult` | platforms/hermes/src/mcp_server/review/persona_output_parser.py:94 |
| 2  | A clean empty `findings` list falls through the `if findings:` guard to the `fallback` P1 path | `parse_persona_output` | platforms/hermes/src/mcp_server/review/persona_output_parser.py:101 |
| 3  | `_coerce_lens_score` is the top-level-scalar extractor pattern to mirror for the rationale | `_coerce_lens_score` | platforms/hermes/src/mcp_server/review/persona_output_parser.py:79 |
| 4  | The fallback path emits a P1 `parser` finding when nothing parses | `fallback_message` | platforms/hermes/src/mcp_server/review/persona_output_parser.py:154 |
| 5  | The branch result dict is assembled here (add `no_findings_rationale`) | `"lens_score": parsed.lens_score` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:479 |
| 6  | The citation floor already ran (findings are post-filter) before the branch returns | `filter_findings` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:474 |
| 7  | `lens_scores` is collected per-persona at fan-in (where to also collect rationale + finding-presence) | `lens_scores[persona]` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:724 |
| 8  | `lens_scores` + `findings` accumulators are initialised before the fan-out loop | `lens_scores: dict[str, float] = {}` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:644 |
| 9  | `sections` is passed untouched to each LLM branch (the strip point) | `sections=sections` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:682 |
| 10 | `sections` is also passed to the prompt-mode branch (strip must precede both) | `sections=sections` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:699 |
| 11 | `_compute_review_score` calls `score_review` and strips persona from findings (needs per-lens counts threaded separately) | `_compute_review_score` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:506 |
| 12 | `score_review` computes the weighted average from `canonical_scores` (the cap must precede this) | `raw_weighted` | platforms/hermes/src/mcp_server/review/review_scoring.py:153 |
| 13 | `ReviewScore` is the returned dataclass (add `rationale_capped`) | `class ReviewScore` | platforms/hermes/src/mcp_server/review/review_scoring.py:96 |
| 14 | `canonical_persona` maps Hermes → framework names (for keying the new maps) | `canonical_persona` | platforms/hermes/src/mcp_server/review/review_scoring.py:49 |
| 15 | Reduced findings carry `personas` (attribution survives reduce, if needed) | `personas` | platforms/hermes/src/mcp_server/review/saga_reducer.py:13 |
| 16 | Spec: strip `*_ready_score`/`*_score`/`readiness_score`/`audit_score` before lens fan-out (in-prompt only) | `_ready_score` | framework/governance/REVIEW_TEAM.md:86 |
| 17 | Spec: 100/0 lens missing rationale → cap 95 + `STRUCTURE-RAT-001`; any finding bypasses | `STRUCTURE-RAT-001` | framework/governance/REVIEW_TEAM.md:103 |
| 18 | The injected playbook already prompts the lens to emit `no_findings_rationale` | `## No-findings rationale` | framework/playbooks/01_BRD/auditor.md:102 |
| 19 | `SourceSection` is a frozen dataclass with a `content` field (the strip target) | `class SourceSection` | platforms/hermes/src/mcp_server/prompts/context_builder.py:37 |
| 20 | Hermes saga is single-pass (`iteration=1`) → H-6.3 not applicable | `iteration=1` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:614 |
| 21 | Current Hermes version is `0.5.1` (→ `0.6.0` MINOR) | `0.5.1` | platforms/hermes/VERSION:1 |
| 22 | Most recent decision is D-0048 → next free is D-0049 | `D-0048` | plans/DECISIONS.md:12 |

## Review log

### Pass 1 — 2026-07-04 — self-review

- **Grounded on an evidence-based assessment** (dispatched subagent) that read the
  full Hermes review path: H-6.1 PARTIAL (playbook prompts the field; parser doesn't
  capture, scorer doesn't cap), H-6.2 ABSENT, H-6.3 BLOCKED (single-pass), H-2 not
  auto-satisfied (sub-checks only in plugin SKILLs, not shared playbooks). Scope cut
  to the two spec-ready consumer-side items; 6.3 + H-2 parked with rationale.
- **Non-obvious defect folded in:** Hermes's parser turns a clean `findings: []`
  into a `fallback` P1 (the `if findings:` guard), so the no-findings case is
  currently unrepresentable — the cap is unreachable without also fixing this. Added
  as an explicit Task-1 sub-item + V1-V3.
- **Cap placement:** chose `score_review` (the module that owns REVIEW_TEAM.md
  scoring policy) over the orchestrator, for unit-testability + plugin parity; new
  params are optional so existing callers are unaffected (V7).
- Citation gate: 22 rows to verify.

### Pass 2 — 2026-07-04 — independent (fresh-context code-reviewer)

An adversarial fresh-context reviewer verified all 22 ledger rows against source,
**reproduced the central premise empirically** (`{"findings":[],"lens_score":100}` →
`parse_status=fallback`, `lens_score=None`, one spurious P1), traced the
`score_review` caller graph + section-construction path, and ran the parser/scoring
test baseline (17 green). **Verdict: 0 load-bearing findings.** The premise is
confirmed (the underlying bug is real), the cap composition is safe (no
double-jeopardy with the P0/P1 caps — they act on the aggregate `score`, not
`canonical_scores`), the single-pass claim holds (H-6.3 genuinely inapplicable), the
strip is meaningful (sections are built from the whole file incl. frontmatter —
`cli/main.py:751`), and Hermes-MINOR/no-framework-change is defensible. 5 minors
folded:

- **M1 — bug framing + V1/V2 under-specified (folded).** The real damage isn't a
  polluted findings list (the fallback P1 is discarded by the citation floor as
  uncited) — it's that the fallback returns `lens_score=None`, dropping the 100/0
  lens from `lens_scores` and lowering coverage. Rewrote the Objective; V1/V2 now
  assert `lens_score == 100` is **preserved** (the property that makes the cap
  reachable).
- **M2 — clean-empty condition too narrow (folded).** `{"lens_score":100}` with no
  `findings` key also fell to fallback. Broadened the condition to "valid dict +
  `lens_score` present + zero coerced findings."
- **M3 — post-citation-floor cap diverges from spec's literal "any finding bypasses"
  (folded into R4).** Reviewer endorsed it as a legitimate design call; R4 now marks
  it a deliberate, documented divergence.
- **M4 — strip `*_score` breadth (folded).** It also matches domain fields
  (`risk_score`); reworded the design note + R3 to acknowledge this is spec-mandated,
  in-prompt-only, parity-correct — not a defect.
- **M5 — persona-key canonicalization (folded).** The new maps must route through
  `canonical_persona` or the `chairperson`→`synthesizer` lens never caps; added V7b.
- Ledger citations all resolve (a few immaterial off-by-one on `@dataclass`/`class`
  lines; `--fix` re-pointed).

### Pass 3 — 2026-07-04 — self-review (re-validate Pass-2 folds)

Re-validated the folded changes for internal consistency: the broadened clean-empty
condition (M2) and the `lens_score`-preserved assertions (M1) are mutually
consistent (both hinge on "valid dict + `lens_score` present + zero findings"); V7b
(M5) aligns with the "canonicalized inside" scope bullet; the R3/R4 rewordings
(M3/M4) don't contradict the design sections. No new gaps. Central premise + cap
composition already empirically confirmed by Pass 2.

**Result:** ready

## Implementation record — 2026-07-04

Implemented on `fix/hermes-review-calibration` after the plan PR (#238) merged. All
V-checks green.

- **Task 1 (parser):** added `_coerce_no_findings_rationale`;
  `PersonaParseResult.no_findings_rationale`; a clean-empty branch (valid dict +
  `lens_score` present + zero findings → successful empty result preserving the
  score). V1-V3 + the no-`findings`-key case (M2) added to
  `test_persona_output_parser.py`.
- **Task 2 (scorer):** `score_review` gained `lens_findings_count` +
  `no_findings_rationale` params + the 95-cap (keys canonicalized) +
  `ReviewScore.rationale_capped`. **Back-compat guard (found during impl):** the cap
  requires `cname in counts` — an absent map (existing callers) or an unrecorded lens
  is never capped. Without this guard the pre-existing `test_compute_review_score_helper`
  failed (all lenses capped when maps omitted) — V7 now enforces it. V4-V7b added to
  `test_review_scoring.py`.
- **Task 3 (orchestrator):** `_branch_llm_findings` returns the rationale; fan-out
  tracks `lens_findings_count` + `no_findings_rationales` per persona;
  `_compute_review_score` threads them + surfaces `STRUCTURE-RAT-001` advisories;
  `_strip_author_self_claim` (regex over `SourceSection.content`) called once before
  fan-out. V8 (strip + no-op identity) added to `test_saga_review_orchestrator.py`.
- **V7b correction:** `synthesizer` is the unscored reduce role (never a crew lens),
  so `chairperson`→`synthesizer` has no live scored case; V7b asserts the defensive
  behavior (alias canonicalized + ignored, real crew lenses still cap).
- **Task 4 (docs):** Hermes `VERSION → 0.6.0`; Hermes + root CHANGELOG; D-0049;
  HERMES-BACKLOG H-6 partial-close; HANDOFF.
- **Verification:** V9 = 508 Hermes tests green; V10 = 160 conformance + 644 subtests
  green. No framework change → no GATE-SPEC, no re-vendor.
