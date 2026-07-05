# HERMES-REVIEW-CONTENT-DELIVERY Plan — inline the (stripped) document body into the review prompt so the LLM lens actually reads the artifact

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-REVIEW-CONTENT-DELIVERY              |
| Type           | fix (functional gap) + folds the paused single_pass strip |
| Status         | IMPLEMENTED — 2026-07-04 (Pass 2 = 3 independent agents, Pass 3 independent; all V-checks green) |
| Depends on     | none                                         |
| Supersedes     | the strip-only intent of `HERMES-SINGLE-PASS-PARITY-PLAN.md` (#242, merged) — its premise ("both paths write the artifact body into the lens prompt") was false; the strip folds into this |
| Version impact | **Hermes MINOR** (`0.6.0 → 0.7.0`). **No framework change** — `REVIEW_TEAM.md` already presupposes the body reaches the lens; Hermes catches up. No GATE-SPEC, no re-vendor. |

## Objective

An investigation (dispatched, evidence-grounded) found that **Hermes's API-path LLM
review never receives the document body** — it scores an artifact it has not read.
`assemble_project_review_prompt` (`context_builder.py:394-466`) composes `prompt_text`
from persona, optional playbook, template, actionable rules, optional layer assets,
and a **metadata-only JSON** block (`:445-457`); `section.content` (the body) feeds only
categorization/token-math/snippets, all of which land in `bundle.context` and are
**never serialized into the prompt**. The executor is a pure completion —
`run_executor`'s `working_dir` is **not** forwarded to `run_api_executor`
(`dispatcher.py:35-42`), and both review callers pass `system_prompt=None`. So the
lens sees only metadata.

Two confirmations that this is a **gap, not a design**:

+ The review templates carry a body placeholder that nothing ever fills —
  `UCR_PROMPT_BRD.md:818-820`: `## Document to Review` / `[PASTE BRD DOCUMENT CONTENT
  BELOW THIS LINE]` (6 of 11 templates have it).
+ The **creation** flow *does* inline substance (`## Authoritative Layer Assets` +
  the project template); only review omits the body. And `REVIEW_TEAM.md:78-93`
  presupposes the body reaches the lens ("the brief that goes to the lens has the
  stripped body").

Because the body never reaches the lens, the author-self-claim **strip (H-6.2, D-0049,
and the paused single_pass plan #242) is currently inert** — it mutates `section.content`,
which never reaches the LLM. This plan fixes the delivery gap **and** makes the strip
meaningful for the first time, by folding the runner-level strip in: the body is
stripped, then inlined into the prompt.

## Scope

**In:**

+ **Inline the document body into the review prompt.** In
  `assemble_project_review_prompt` (`context_builder.py:394`), inline a
  `## Document to Review` block built from **`mapping.included_sections`** (the
  per-persona-relevant set the builder already computes at `:408`), reconstructed in
  document order under a `### <section_id> <title>` header. **Reconcile the template
  placeholder (F1):** 6 of the 9 review prompt templates end with a `## Document to Review` /
  `[PASTE … CONTENT BELOW THIS LINE]` placeholder (`UCR_PROMPT_BRD.md:818-820`); the
  builder must **remove any such placeholder block from `prompt_template_text`** and
  emit exactly **one** populated `## Document to Review` block — no duplicate header,
  no dangling "paste below" instruction. This covers **all** review paths, because
  every caller (saga branches/aggregate, MCP `prompt_only`, CLI `single_pass`) routes
  through `run_project_review_build` → `assemble_project_review_prompt`.
+ **Why `included_sections`, not all sections — with an empty-guard (F2 + token
  consistency + Pass-3 Finding 1).** The builder already maps sections to each
  persona's relevant set (`map_sections_for_personas`, `:408`). For CLI/`single_pass`
  the whole artifact is one whole-file section that (for any real artifact) maps to
  `included` → the lens gets the **full body**; a per-persona saga branch gets that
  persona's relevant sections (Hermes's existing relevance design); the aggregate gets
  the **union**. Inlining `included_sections` matches what `tokens_total` **already
  counts** (`build_runtime_context`, `:254-258`), so **no new token accounting is added
  and nothing is double-counted** (see below). **Guard (Pass-3 Finding 1):**
  `categorize_section` defaults a keyword-free section to category `"metadata"`, which
  no persona maps to, so a degenerate/keyword-free document could map to an **empty**
  `included_sections` → an empty body. So inline `mapping.included_sections or
  sections` — fall back to **all** sections when the included set is empty, guaranteeing
  the lens is never handed an empty body. (The rare fallback under-counts tokens
  slightly — harmless; the count is a warning heuristic, not a gate.)
+ **Fold the runner-level strip (from #242).** Extract `_strip_author_self_claim` +
  `_SELF_CLAIM_RE` (`saga_orchestrator.py:85,91`) to a new
  `review/section_hygiene.py` (`strip_author_self_claim`); call it in
  `run_project_review_build` (`runner.py:38`) so the `sections` handed to
  `assemble_project_review_prompt` are already stripped → the inlined body carries no
  author `*_ready_score`. Remove the redundant saga `:615` pre-strip + prune the
  orphaned `replace` import (`saga_orchestrator.py:10`). This is where the strip stops
  being cosmetic.
+ **Token budget — no new accounting; the body is already counted.** `tokens_total`
  (`build_runtime_context`, `:254-258,296`) already folds `included_sections` content
  into the estimate, so the existing `inspect_prompt_bundle` warning (threshold
  `12000`, `:313-318`) — which the saga surfaces as a P1 "token budget warning"
  finding (`saga_orchestrator.py:345-348`) — **already reflects body size**. This plan
  adds **no** token accounting (adding body tokens on top of `tokens_total` would
  double-count and spuriously trip that P1 finding). Do **not** touch
  `_compute_token_warning` (it measures persona text only; its "reduce persona count"
  message does not fit a large body). **No truncation** (a truncated body re-breaks
  review); chunking for very large artifacts is a documented follow-on. The pre-existing
  `15000` vs `12000` threshold split (`:109` vs `:313`) is left as-is (not worsened).
+ Update the two existing strip tests to `section_hygiene`; add tests (additive — no
  existing prompt-shape test hard-breaks, they use substring assertions): the body is
  now in the review prompt (`test_prompt_context_builder.py`); the inlined body is
  stripped of self-claim scores; exactly one `## Document to Review` header (no
  placeholder residue).
+ **Docs:** D-0051 (records the content-blind gap + fix; supersedes #242's strip
  premise; H-6.2 strip is now meaningful, not cosmetic). Mark
  `HERMES-SINGLE-PASS-PARITY-PLAN.md` superseded. Correct H-6.2 in `HERMES-BACKLOG.md`.
  Add a backlog entry for the **plugin-side** strip gap (secondary finding). Hermes
  `0.6.0 → 0.7.0`; Hermes + root CHANGELOG; HANDOFF; `docs/PARITY.md` (Hermes review
  now delivers content).

**Out of scope (deferred — documented):**

+ **Large-artifact chunking / summarization.** Inlining the full body can exceed the
  model context for very large artifacts; this plan warns (not truncates). A
  chunk/map-reduce strategy is a separate follow-on (new backlog entry).
+ **Plugin-side strip enforcement.** The investigation flagged that the plugin lens
  reads the raw on-disk file via its path (`doc-brd-audit/SKILL.md:110`), so the
  `REVIEW_TEAM.md:82` strip MUST may be unfulfilled there too. Cross-platform concern;
  a new backlog entry, verified + planned separately.
+ **`single_pass` playbook injection** — still deferred (the #242 out-of-scope design
  questions stand).

## Approach / Design (D-0051)

### Content delivery — the core fix

`assemble_project_review_prompt` gains one part: `## Document to Review\n\n<body>`,
where `<body>` = `"\n\n".join(f"### {s.section_id} {s.title}\n{s.content.strip()}"
for s in (mapping.included_sections or sections))` — the per-persona relevant set
already computed at `:408`, with an all-sections fallback when it is empty (Pass-3
Finding 1). It is inserted **before** the two trailing metadata dumps (`:456-457`) so
the lens reads the artifact then its structural metadata. The `sections` param already
carries the parsed document (every caller builds it from the artifact file), so no new
loading is needed — the body was always available; it was simply never placed in the
prompt.

**Template placeholder reconciliation (F1).** The template part (`prompt_template_text`,
`:446`) already contains, in 6 of 11 templates, a trailing `## Document to Review` +
`[PASTE … BELOW THIS LINE]` placeholder. Appending a second populated block would
produce a **duplicate header** and a dangling paste instruction. So the builder
**strips any existing `## Document to Review … [PASTE … BELOW THIS LINE]` block from
`prompt_template_text`** before appending the single populated block — one uniform code
path, correct for all 11 templates (with or without the placeholder).

**Scope of the inlined body (F2).** `included_sections` (not all `sections`) is
deliberate: for CLI/`single_pass` the whole file maps to one included section → full
body; for a per-persona saga branch, that persona's relevant sections (the existing
relevance design); for the aggregate, the union. This bounds the per-branch token cost
using machinery the builder already runs, and keeps the inlined content identical to
what `tokens_total` counts (no self-referential under-report). A lens that needs
cross-section context is served by the aggregate + the per-persona split that the team
review is built around; matching the plugin's whole-file read for every single-persona
branch is a cost the relevance mapping deliberately avoids.

All review paths are fixed at once because `run_project_review_build` (`runner.py`) is
the single builder every caller routes through, and it delegates to
`assemble_project_review_prompt`.

### Strip — folded in, now meaningful

The runner strips `sections` (extracted `strip_author_self_claim`) **before**
`assemble_project_review_prompt` inlines them, so the `## Document to Review` block
never contains the author's `*_ready_score`. This is the point of the H-6.2/#242
strip; until the body is inlined it was inert. Extraction + the runner call + the saga
pre-strip removal + `replace` prune are exactly the (reviewed, Pass-3-clean) mechanics
of the paused #242 plan, reused here.

### Token budget — already counted, no new accounting

`tokens_total` (`build_runtime_context`, `:254-258,296`) **already folds
`included_sections` content** into its estimate — so the existing warning in
`inspect_prompt_bundle` (threshold `12000`, `:313-318`), which the saga converts into
a P1 "token budget warning" finding (`saga_orchestrator.py:345-348`), already reflects
body size. Because this plan inlines exactly `included_sections`, the inlined content
matches what is already counted: **no token accounting is added** (doing so would
double-count and spuriously raise the P1 finding on every branch), and `_compute_token_warning`
(persona-only) is left untouched. The pre-existing `15000`/`12000` threshold split
(`:109`/`:313`) is out of scope and left unchanged. No truncation (a truncated body
re-breaks review); chunking for very large artifacts is a documented follow-on.

Note the deterministic (non-LLM) branch `_branch_prompt_findings` (`saga_orchestrator.py:271`)
calls the runner but consumes only `.inspection`, so it now reconstructs a body it
never reads (F4). Harmless; a cheap guard is a possible follow-on, not required.

### Versioning

Hermes review moving from content-blind to content-aware is a **major functional
change** to observable behavior → **Hermes MINOR** `0.6.0 → 0.7.0`. No `framework/`
change (the spec already assumes the lens reads the body). No GATE-SPEC, no re-vendor.

### Backward-compatibility

Every review prompt gains a `## Document to Review` block; existing tests that assert
prompt *shape* may need updating (they previously asserted metadata-only prompts). No
return-contract change (`prompt_only` still returns raw stdout; the saga still parses
findings). The strip extraction is behavior-preserving (Pass-3-verified in #242).

## File structure

### Added

| Path | Purpose |
| ---- | ------- |
| `platforms/hermes/src/mcp_server/review/section_hygiene.py` | shared `strip_author_self_claim` + `_SELF_CLAIM_RE` |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/src/mcp_server/prompts/context_builder.py` | `assemble_project_review_prompt`: inline a `## Document to Review` body from `mapping.included_sections` before the metadata dumps (`:456`); strip the template's placeholder block first (dedupe the header). No token-accounting change |
| `platforms/hermes/src/mcp_server/review/runner.py` | strip `sections` at the top of `run_project_review_build` (`:38`) so the inlined body is clean |
| `platforms/hermes/src/mcp_server/review/saga_orchestrator.py` | remove the local strip def + `_SELF_CLAIM_RE` + the `:615` call; prune the orphaned `replace` import (`:10`) |
| `platforms/hermes/tests/…` | body-in-prompt test; stripped-body test; token-warning test; retarget the 2 strip-test imports to `section_hygiene`; update any prompt-shape test that assumed no body |
| `platforms/hermes/VERSION` (→ `0.7.0`) + Hermes CHANGELOG + root CHANGELOG | version + entries |
| `plans/DECISIONS.md` (D-0051) / `plans/HERMES-SINGLE-PASS-PARITY-PLAN.md` (superseded banner) / `plans/HERMES-BACKLOG.md` (H-6.2 correction + 2 new deferred entries) / `plans/HANDOFF.md` / `docs/PARITY.md` | docs |

## Implementation sequence

### Task 1: content delivery — [CODE]

+ In `assemble_project_review_prompt`: strip any `## Document to Review … [PASTE …
  BELOW THIS LINE]` block from `prompt_template_text`, then inline one
  `## Document to Review` block from `mapping.included_sections` before the metadata
  dumps. No token-accounting change. Tests (in `test_prompt_context_builder.py`): a
  review prompt now contains a unique body token; exactly one `## Document to Review`
  header; no `[PASTE …]` residue.

### Task 2: fold the strip (make it meaningful) — [CODE]

+ Extract `strip_author_self_claim` → `section_hygiene`; call in the runner; remove the
  saga `:615` strip + local def + prune `replace`; retarget the 2 tests. Test: the
  inlined `## Document to Review` body has no `*_ready_score` line; saga suite green.

### Task 3: version + docs

+ Hermes `0.7.0`; both CHANGELOGs; D-0051; supersede #242; correct H-6.2 backlog; add
  the two deferred backlog entries (large-artifact chunking; plugin-side strip gap);
  HANDOFF; PARITY.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | build a review prompt over an included section with body `UNIQUEBODYTOKEN` (in `test_prompt_context_builder.py`) | `prompt_text` now contains `## Document to Review` + `UNIQUEBODYTOKEN` | core fix (was the bug) |
| V2 | body with `brd_ready_score: 92` | the inlined `## Document to Review` body has no `brd_ready_score` (strip now bites) | strip meaningful |
| V3 | template WITH the placeholder (BRD) | assembled prompt has **exactly one** `## Document to Review` header and no `[PASTE … BELOW]` residue | F1 placeholder reconcile |
| V3b | a keyword-free section (categorizes as `metadata` → empty `included_sections`) | body still inlined via the all-sections fallback (never empty) | Pass-3 Finding 1 guard |
| V4 | MCP `prompt_only` + CLI `single_pass` + saga branch prompts | all contain the document body (single builder covers all) | all paths |
| V5 | `section_hygiene.strip_author_self_claim` unit (moved #242 tests) | pass | pure move |
| V6 | `ruff check platforms/hermes/src` | clean (no orphaned `replace`) | prune |
| V7 | `python -m pytest platforms/hermes/tests -q` | green — additive body block; existing prompt tests use substring assertions (no shape hard-break) | no regression |
| V8 | `python -m pytest tests/conformance -q` | green (no framework change) | no regression |

## Docs to update

+ [ ] `platforms/hermes/CHANGELOG.md` — `[0.7.0]` (review now delivers document content; strip now effective)
+ [ ] root `CHANGELOG.md` — Hermes `0.6.0 → 0.7.0`
+ [ ] `plans/DECISIONS.md` — D-0051 (content-blind gap + fix; supersedes #242 strip premise; H-6.2 now meaningful) **+ a correction note on D-0049** (its H-6.2 strip was inert until this plan; the 0.6.0 changelog described it as functional)
+ [ ] `plans/HERMES-SINGLE-PASS-PARITY-PLAN.md` — superseded banner
+ [ ] `plans/HERMES-BACKLOG.md` — correct H-6.2; add "large-artifact chunking" + "plugin-side strip enforcement" deferred entries
+ [ ] `plans/HANDOFF.md` — arc progress
+ [ ] `docs/PARITY.md` — Hermes review now delivers document content to the lens

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Existing tests assert review-prompt shape and break | low | reviewer 3 verified all review-prompt tests use substring/`>0` assertions — the body block is **additive**, no hard-break; V1/V2 are net-new in `test_prompt_context_builder.py` |
| R2 | Large artifacts blow the model context window | med | warn via the existing (already-body-aware) `tokens_total` threshold; do NOT truncate (would re-break review); chunking is a documented follow-on |
| R3 | Saga N-branch prompts each carry a body → cost | low-med | branches are **independent** API calls (a cost multiplier, not a single-context sum, so not a chunking prerequisite); inlining `included_sections` (not all) bounds each branch to its persona's relevant set |
| R4 | Strip extraction regresses the saga | low | Pass-3-clean in #242; V5 unit + V7 suite; behavior-preserving move; `document_fingerprint` uses only `len(sections)` (unchanged) |
| R5 | Reconstruction injects a synthetic `### <id> <title>` header the on-disk artifact lacks | low | for whole-file sections the title is `Source: <file>` — a cosmetic wrapper, zero content loss; the lens reviews the engine's own parse (consistent with how `sections` already drive review) |
| R6 | Over-scoping | low | core = content delivery; strip folds in because it's the mechanism that cleans the inlined body (coupled, not speculative); the reviews *simplified* the design (included_sections + no new token work); chunking + plugin-strip + deterministic-path guard explicitly deferred |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `assemble_project_review_prompt` builds `prompt_text` from these parts; no body inlined | `parts = [combined_persona_text` | platforms/hermes/src/mcp_server/prompts/context_builder.py:437 |
| 2  | The trailing parts are metadata-only JSON dumps (body goes before these) | `inspect_prompt_bundle(bundle)` | platforms/hermes/src/mcp_server/prompts/context_builder.py:456 |
| 3  | The builder is the single chokepoint every review caller routes through | `def run_project_review_build` | platforms/hermes/src/mcp_server/review/runner.py:27 |
| 4  | `run_project_review_build` delegates to `assemble_project_review_prompt` | `assemble_project_review_prompt` | platforms/hermes/src/mcp_server/review/runner.py:38 |
| 5  | `working_dir` is NOT forwarded to the API executor (lens can't read files) | `run_api_executor(` | platforms/hermes/src/mcp_server/executor/dispatcher.py:35 |
| 6  | `run_api_executor` is a pure completion (system + user prompt only) | `messages` | platforms/hermes/src/mcp_server/executor/api_runner.py:138 |
| 7  | The review template has an unfilled body placeholder | `Document to Review` | platforms/hermes/prompts/templates/review/UCR_PROMPT_BRD.md:818 |
| 8  | The strip helper + regex live locally in `saga_orchestrator` (to extract) | `_strip_author_self_claim` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:91 |
| 9  | The saga pre-strip call (to remove; runner will strip) | `_strip_author_self_claim` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:615 |
| 10 | `replace` is imported and used ONLY by the strip helper (orphaned on removal) | `dataclass, replace` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:10 |
| 11 | Two existing tests import the strip helper (retarget) | `_strip_author_self_claim` | platforms/hermes/tests/unit/test_saga_review_orchestrator.py:530 |
| 12 | Token warning threshold + helper (extend to count the body) | `TOKEN_WARNING_THRESHOLD` | platforms/hermes/src/mcp_server/prompts/context_builder.py:109 |
| 13 | `_compute_token_warning` is the token-warning path | `def _compute_token_warning` | platforms/hermes/src/mcp_server/prompts/context_builder.py:371 |
| 14 | Spec presupposes the lens receives the (stripped) body | `stripped body` | framework/governance/REVIEW_TEAM.md:93 |
| 15 | The review assembler inlines layer-asset substance but omits the document body | `Authoritative Layer Assets` | platforms/hermes/src/mcp_server/prompts/context_builder.py:455 |
| 16 | Current Hermes version is `0.6.0` (→ `0.7.0` MINOR) | `0.6.0` | platforms/hermes/VERSION:1 |
| 17 | Most recent decision is D-0050 → next free is D-0051 | `D-0050` | plans/DECISIONS.md:13 |
| 18 | The builder already computes per-persona `included_sections` (the set to inline) | `mapping = map_sections_for_personas` | platforms/hermes/src/mcp_server/prompts/context_builder.py:408 |
| 19 | `sections` are built whole-file from the artifact (so included = full body for CLI/single_pass) | `_build_review_sections_from_document` | platforms/hermes/src/mcp_server/cli/main.py:747 |
| 20 | `tokens_total` already folds included-section content in → existing warning reflects body size | `token_estimate = estimate_tokens` | platforms/hermes/src/mcp_server/prompts/context_builder.py:254 |
| 22 | `categorize_section` defaults a keyword-free section to `"metadata"` (→ empty-guard needed) | `def categorize_section` | platforms/hermes/src/mcp_server/prompts/context_builder.py:141 |
| 21 | The saga surfaces the token warning as a P1 finding (so new body-token accounting would spuriously trip it) | `token budget warning` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:345 |

## Review log

### Pass 1 — 2026-07-04 — self-review

+ **Grounded on a dispatched investigation** that confirmed Hermes review
  content-blindness three ways (no body in the prompt parts list; `working_dir` not
  forwarded to the completion executor; `system_prompt=None`) and established it as a
  gap (unfilled template placeholder; creation-vs-review asymmetry; spec presupposes
  the body reaches the lens). This plan directly fills the gap at the one builder every
  path shares.
+ **The strip is folded, not bundled speculatively:** content delivery inlines the
  body; without the strip that body would carry the author's score → re-introducing the
  exact anchor effect. They are coupled — the strip is the mechanism that cleans the
  inlined body, and this is where it stops being inert. Reuses the Pass-3-clean #242
  mechanics.
+ **Deferred with rationale:** large-artifact chunking (warn-not-truncate now) + the
  plugin-side strip gap (cross-platform, verify separately). Not bundled.
+ Citation gate: 17 rows to verify.

### Pass 2 — 2026-07-04 — independent (3-agent parallel per OPS-0067)

Three fresh-context reviewers (citations, design, regression). Core premise **fully
verified** (Hermes review is content-blind; `sections` = full parsed body; the builder
is the single chokepoint; strip fold correct + no bypass). Findings folded:

+ **[LOAD-BEARING] F1 — malformed double-header.** 6/11 templates already end with a
  `## Document to Review` / `[PASTE … BELOW]` placeholder; appending a second block
  ships a duplicate header + dangling instruction. → Builder now **strips the
  placeholder block first**, emits exactly one populated block (V3).
+ **[LOAD-BEARING] F2 + token double-count (converged).** The builder already computes
  per-persona `included_sections`, and `tokens_total` **already counts that content**.
  Inlining *all* sections would (a) ignore the relevance mapping (self-inflicting the
  N-multiplier) and (b) under-count / risk double-count. → Inline
  **`mapping.included_sections`**, which bounds cost AND matches the existing token
  count → **no new token accounting** (dropped the "extend token warning" scope; it
  would double-count and spuriously trip the saga's P1 finding). `_compute_token_warning`
  (persona-only) left untouched.
+ **[MINOR] F4** deterministic branch builds an unused body (noted, deferred). **F5/F6**
  resolved by inlining included (counted) content; pre-existing 12000/15000 split left
  as-is. **R1 overstated** — existing prompt tests use substring assertions, additive
  body block doesn't hard-break (V7). **Citation fixes:** row 14 → `:93`, row 15 →
  review-side `:455` (reworded); added rows 18-21 (the `included_sections` mapping,
  whole-file sections, existing token count, saga P1 warning). **D-0049 correction**
  added to the docs list.
+ **N-multiplier is not a chunking prerequisite** — branches are independent API calls
  (cost multiplier, not single-context sum); chunking stays a follow-on.

### Pass 3 — 2026-07-04 — independent (fresh-context code-reviewer) re-review of the reconciled design

**0 load-bearing findings.** The reviewer verified all 22 rows + the reconciled design
against source: `included_sections` is in scope at the inline point and carries the
needed fields; the placeholder block is **uniform + trailing** in all 6 templates (a
single regex strip is clean); "no new token accounting" is genuinely safe
(`tokens_total` already folds exactly the `included_sections` content — no
double-count); the strip fold routes through the single chokepoint with no un-stripped
path, and the `replace`-prune + 2-test-retarget extraction ripple is complete (`re`
correctly retained). Folded findings:

+ **Finding 1 [MINOR, impl-critical] — empty-`included` edge.** `categorize_section`
  defaults a keyword-free section to `"metadata"` (no persona maps to it), so a
  degenerate document → empty `included_sections` → empty body. → Added the
  `mapping.included_sections or sections` **fallback guard** (V3b) + a note that V1/V2
  fixtures must use category-triggering content. Ledger row 22 added.
+ **Finding 2 [MINOR] — row 20 citation** `:237`→`:254` (fixed). "6 of 11" → "6 of 9
  prompt templates" (fixed).
+ Version (MINOR), supersession, and the D-0049 correction all confirmed sound.

### Pass 4 — 2026-07-04 — self-review (re-validate the Finding-1 guard)

The `included_sections or sections` guard is internally consistent: for real artifacts
`included` is non-empty (unchanged behavior); only a keyword-free/degenerate doc hits
the fallback, which delivers the full body (the correct outcome) at a slight,
harmless token under-count. V3b exercises it. No new gaps.

**Result:** ready

## Implementation record — 2026-07-04

Implemented on `fix/hermes-review-content-delivery` after the plan PR (#243) merged.

+ **Task 1 (content delivery):** `assemble_project_review_prompt` now strips the
  template's `## Document to Review … [PASTE … BELOW]` placeholder (new
  `_DOC_REVIEW_PLACEHOLDER_RE`) and inlines one `## Document to Review` block from
  `mapping.included_sections or sections`, before the metadata dumps. Added `import re`.
+ **Task 2 (strip fold):** extracted `strip_author_self_claim` → `section_hygiene.py`;
  called in `run_project_review_build`; removed the saga `:615` pre-strip + local def +
  pruned the `replace` import; retargeted the 2 strip tests.
+ **Impl discovery (folds Pass-3 Finding 1 cleanly):** the empty-`included` case does
  **not** reach the `or sections` fallback — `build_prompt_bundle`'s existing
  `validate_prompt_bundle_or_raise` rejects an empty `included_sections` **loudly**
  (`ContractValidationError`, caught by the branch fns as a coverage finding) *before*
  body assembly. So the fallback is belt-and-suspenders; the empty-body edge is already
  prevented. Kept the `or sections` guard (harmless) + `if document_body:`.
+ **Verification (end-to-end, the check that originally exposed the gap):** a review
  build now yields `## Document to Review` + the body token in `prompt_text`, exactly
  one header (dedupe), and `brd_ready_score` stripped from the inlined body — the strip
  bites for the first time. V1/V3 in `test_prompt_context_builder.py`, V2 (strip via
  the runner) in `test_review_runner.py`. **V6** ruff clean; **V7** 511 Hermes tests
  (508 + 3); **V8** 160 conformance — all green; no existing prompt test hard-broke.
+ **Task 3 (docs):** Hermes `VERSION → 0.7.0`; both CHANGELOGs; D-0051 + D-0049
  correction; superseded banner on #242; H-6.2 corrected + H-13/H-14 added in
  HERMES-BACKLOG; HANDOFF; PARITY.
