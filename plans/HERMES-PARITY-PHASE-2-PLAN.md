# HERMES-PARITY-PHASE-2 Plan — playbook injection for BRD+PRD (the load-bearing gap)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-PARITY-PHASE-2                        |
| Type           | feature                                     |
| Status         | PLANNED — 2026-07-03T19:30:28-04:00         |
| Depends on     | HERMES-PARITY-PHASE-1 (D-0045, merged #230) |
| Feeds          | Phase 3 (playbook fan-out to the other 6 layers + CHG) |
| Version impact | **Hermes MINOR** (`hermes` `0.3.0 → 0.4.0`) — a structurally different review capability; **no framework spec bump** (no `framework/**` change — GATE-SPEC no-op) |

## Objective

Close the **load-bearing** Hermes-parity gap: Hermes's review lenses receive
generic **persona files** but not the per-`(layer,lens)` **playbooks**
(`framework/playbooks/<NN>_<LAYER>/<lens>.md`) — a layer-specific reasoning frame
plus a numbered evidence checklist (`C1`..`Cn`) — that the framework playbook
contract (`REVIEW_TEAM.md:210-264`) requires. Without them a lens reasons about
every layer identically and misses layer-specific gaps; and Hermes cannot enforce
the contract's citation floor (every finding cites `check:`; the synthesizer
discards uncited findings) or emit `verdict.playbook_coverage`. This phase wires
all three for **BRD + PRD** (the H-4 scope; the plugin already does this). Phase 3
fans out to the other 6 layers + CHG. The playbook files already exist for both
layers — this is **pure wiring, no content authoring**.

## Scope

**In (BRD + PRD only):**

- **Playbook loading** — a new `platforms/hermes/src/mcp_server/review/playbook_loader.py`:
  resolve `framework/playbooks/<NN>_<LAYER>/<lens>.md` via the established
  `parents[5]` framework-root idiom; return its content + the parsed valid check
  ids (`C1`..`Cn` from the `## Required evidence checks` rows matching `^\*\*C\d+`).
  Resolve a playbook **only for framework review-crew lenses** (`REVIEW_CREWS.yaml`,
  after `canonical_persona`); non-crew branch personas (`fact_checker`,
  `chairperson`) get no playbook + no floor. A missing file **for a crew lens** →
  `BRANCH_FAILED` (`reason: "playbook missing: <path>"`), never a silent
  playbook-less prompt (plugin contract).
- **Injection** — in `prompts/context_builder.py:assemble_project_review_prompt`,
  inline the resolved playbook as a `## Layer-specific playbook` element of the
  `parts` list (after `combined_persona_text`, `:425-429`); extend the
  `MCP_REVIEW_ACTIONABLE_RULES` constant (`:121-127`) with the binding "every
  finding MUST cite `check: \"C1\"` or `check: \"beyond-checklist:<tag>\"`"
  instruction.
- **Citation floor** — thread a `check` field through the finding model
  (`persona_output_parser._coerce_findings`; `saga_reducer._normalize_record`);
  **discard uncited / unknown-check findings** (byte-identical vendor of the
  plugin's stdlib `finding_filter.py` — `filter_findings` + `emit_coverage`),
  applied on the **LLM path** after `parse_persona_output`.
- **Coverage emission** — add `verdict.playbook_coverage`
  (`{<check_id>: <count>, …, "beyond_checklist": <n>}`) to the `synthesis_summary`
  (`saga_orchestrator.py:876-885`) + `SagaReviewResult`.
- Hermes MINOR bump `0.3.0 → 0.4.0`; Hermes CHANGELOG; `docs/PARITY.md` Layer-Playbooks
  row (BRD+PRD active); update the 4 affected Hermes tests; D-0046.

**Out of scope (deferred):**

- **The other 6 layers (EARS/BDD/ADR/SPEC/TDD/IPLAN) + CHG** — Phase 3 (H-5/H-10).
  The mechanism is identical; only the (layer,lens) fan-out differs.
- **The calibration deltas (H-6)** — no-findings rationale / author-self-claim
  stripping / fixer-regression. Related synthesizer work; folds into a later phase
  to keep this one focused on the injection mechanism.
- **The deterministic-fallback path** (`_branch_prompt_findings`, `:246`) — it runs
  no LLM (derives findings from prompt-inspection), so the citation-discard is a
  no-op there; playbook injection + the floor apply to the **LLM path**
  (`_branch_llm_findings`, `:364`) only. Explicit decision — see Approach.

## Approach / Design (D-0046)

### Reference: how the plugin does it

`doc-brd-audit/SKILL.md:100-117` resolves `framework/playbooks/01_BRD/<lens>.md`,
**inlines it literally** under `## Layer-specific playbook`, and instructs the lens
to cite `check:` in every finding (missing file → `BRANCH_FAILED`). The
synthesizer (`agents/synthesizer.md:104-122`) parses valid `Cn` ids from the
`## Required evidence checks` rows (`^\*\*C\d+`), discards uncited/fabricated-check
findings, and emits `verdict.playbook_coverage`. `tools/finding_filter.py`
(stdlib, 61 lines: `filter_findings(findings, valid_ids) → (kept, discarded)` +
`emit_coverage(findings)`) is the portable reference. Hermes mirrors this in code.

### Injection site + plumbing (explicit)

`assemble_project_review_prompt` (`context_builder.py:383-447`) is shared: the two
**saga-branch** callers pass a single persona, but three other callers pass
**multiple** personas — the aggregate/synthesis build (`saga_orchestrator.py:848`),
the `prompt_only` MCP review mode (`tool_registry.py:1624`, LLM-executed at `:1648`),
and the CLI (`cli/main.py:1005`). A multi-persona call has no single `<lens>.md` to
inline. **Decision:** thread an explicit optional `playbook_text` parameter from the
**per-branch** orchestrator call through `runner.py:run_project_review_build` into
`assemble_project_review_prompt`; only the single-persona saga-branch caller resolves

- passes it, so the `(layer,lens)` pair is unambiguous there. The three multi-persona
callers pass `playbook_text=None` → their prompt is unchanged. **Phase 2 scope is the
saga per-branch team-review path only;** the `prompt_only` mode + the aggregate build
are **not** playbook-injected in Phase 2 (a documented follow-on — `prompt_only` is a
distinct single-shot review entry point, tracked for a later phase).

### The three real complications (design decisions)

1. **No `check` field in Hermes's finding model — threads through 3 surfaces.**
   Today `_coerce_findings` (`persona_output_parser.py:24-51`) emits 7 keys, none
   `check`. Add `check` (optional) preserved parser → orchestrator → reducer →
   verdict (synthesizer.md:227 "check preservation is a hard contract"). **This is
   NOT just `_normalize_record`:** the reduced record is a **frozen `ReducedFinding`
   dataclass** (`saga_reducer.py:7-18`) with no `check` field, built field-by-field
   at `saga_reducer.py:124-144` — so the dataclass **and** its construction must gain
   the field, else `check` never reaches the verdict. The dedup `_identity_hash`
   (`saga_reducer.py:38-46`) stays on `message+target_layer+action` — do **not** add
   `check` (a genuine dup keeps the first branch's citation). **Coverage counting
   decision:** compute `playbook_coverage` from the **kept, pre-reduce** findings
   (per-branch, before dedup) — post-dedup would under-report (dedup keeps only one
   branch's `check`).
2. **Persona-name ↔ playbook-lens mapping (the subtle one).** Branch personas come
   from **`persona_mappings.yaml`** (`saga_orchestrator.py:551`), which is a
   **superset** of the framework review crew (`REVIEW_CREWS.yaml`). The BRD branch
   list (`persona_mappings.yaml:44`) is `[architect, auditor, business_analyst,
   chaos_engineer, security_engineer, fact_checker, chairperson]` — **two of these
   are NOT crew lenses and have no playbook**: `chairperson` (→ `synthesizer`, the
   reducer) and `fact_checker` (no alias, no `01_BRD/fact_checker.md`). **Decision:**
   the rule is keyed on crew membership, not file presence — **a branch persona that
   is NOT a framework review-crew lens (per `REVIEW_CREWS.yaml`, after
   `canonical_persona` aliasing) gets NO playbook + NO citation floor, and is NOT
   `BRANCH_FAILED`** (it runs as today). `BRANCH_FAILED` fires ONLY when a persona
   that IS a crew lens has an unexpectedly-absent playbook file. This avoids turning
   the working `fact_checker`/`chairperson` BRD branches into hard failures. (PRD is
   clean — `persona_mappings.yaml:47` is exactly the 6 PRD-playbook lenses — so a
   PRD-only smoke test would miss this; V5 tests the BRD `fact_checker` path.)
3. **Deterministic vs LLM path.** The playbook rides the **shared** prompt builder
   (`assemble_project_review_prompt`), so it lands in *both* paths' `prompt_text` —
   harmless for the deterministic path (it inspects the prompt, doesn't reason). But
   the **citation floor (discard) + coverage** apply to the **LLM path only**
   (`_branch_llm_findings`): the deterministic-fallback path emits inspection-derived
   findings with no `check`, so discarding them would empty every deterministic
   review. **Decision:** inject in the shared builder; gate the discard+coverage on
   the LLM path. Note in code + V6.

### Coverage shape

`verdict.playbook_coverage = {<check_id>: <count>, …, "beyond_checklist": <n>}`
computed from the kept (check-carrying) findings around the reduce step
(`saga_orchestrator.py:842`), added to `synthesis_summary` (`:876-885`). The >30%
beyond-checklist "drift signal" is advisory (not gated) per REVIEW_TEAM.md:261.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `platforms/hermes/src/mcp_server/review/playbook_loader.py` | resolve + read `<NN>_<LAYER>/<lens>.md`; parse valid `Cn` ids; missing→fail semantics |
| `platforms/hermes/src/mcp_server/review/finding_filter.py` | **byte-identical vendor** of the plugin's `finding_filter.py` (it is fully engine-agnostic, stdlib) + a drift-guard test asserting byte-identity — NOT a divergent port (avoids two sources of truth for the citation-filter contract) |
| `platforms/hermes/tests/unit/test_playbook_injection.py` | loader + injection + filter + coverage |

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/src/mcp_server/prompts/context_builder.py` | add an optional `playbook_text` param; inline it as `## Layer-specific playbook` in `assemble_project_review_prompt` parts (`:425-429`); extend `MCP_REVIEW_ACTIONABLE_RULES` (`:121-127`) with the `check:` instruction |
| `platforms/hermes/src/mcp_server/review/runner.py` | thread the `playbook_text` param through `run_project_review_build` (`:27-44`) — the intermediary every builder caller uses |
| `platforms/hermes/src/mcp_server/review/persona_output_parser.py` | preserve `check` in `_coerce_findings` (`:24-51`) |
| `platforms/hermes/src/mcp_server/review/saga_reducer.py` | carry `check` through `_normalize_record` (`:25-35`) **AND add the `check` field to the frozen `ReducedFinding` dataclass (`:7-18`) + its construction (`:124-144`)** |
| `platforms/hermes/src/mcp_server/review/saga_orchestrator.py` | resolve+pass playbook per branch; discard uncited on the LLM path (`:443-457`); add `playbook_coverage` to `synthesis_summary` (`:876-885`) |
| `platforms/hermes/tests/{integration/test_prompt_context_builder.py, unit/test_persona_output_parser.py, unit/test_saga_review_orchestrator.py}` | assert the playbook part, `check` survival, discard + coverage |
| `platforms/hermes/VERSION` + `CHANGELOG.md` | `0.3.0 → 0.4.0`; entry |
| `docs/PARITY.md` | Layer-Playbooks row → Hermes BRD+PRD active (Phase 3 = rest) |
| `plans/DECISIONS.md` / `HERMES-BACKLOG.md` / `HANDOFF.md` | D-0046; Phase-2 shipped; H-4 closed |

## Implementation sequence

### Task 1: playbook loader + finding_filter (test-first) — [CODE]

- Write `test_playbook_injection.py`; `playbook_loader.load_playbook(layer, lens)`
  (resolve, parse `Cn`, missing→signal) + **vendor `finding_filter.py` byte-identical
  from the plugin** + a drift-guard test asserting byte-identity. Confirm the BRD +
  PRD real playbooks load and their `Cn` ids parse.

### Task 2: injection + `check` threading — [CODE]

- Inline the playbook in `context_builder`; extend `MCP_REVIEW_ACTIONABLE_RULES`;
  add `check` to the parser + reducer. Update the prompt-content + parser tests.

### Task 3: discard + coverage — [CODE]

- In `saga_orchestrator` LLM path: map persona→lens (`canonical_persona`), resolve
  playbook (synthesizer → skip; real-lens-missing → BRANCH_FAILED), filter uncited,
  compute + attach `playbook_coverage`. Update orchestrator tests (uncited fixtures
  now discarded).

### Task 4: version + docs

- Hermes `0.4.0`; CHANGELOG; PARITY row; D-0046; backlog/HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | `test_playbook_injection.py` | all 5 BRD + 6 PRD playbooks load; `Cn` ids parse; missing→fail | loader |
| V2 | prompt-content test: a BRD branch's `prompt_text` contains `## Layer-specific playbook` + the lens's C-checks | present | injection |
| V3 | `check` survives parser→reducer→verdict on the LLM path (byte-identical) | preserved | citation floor |
| V4 | an LLM finding with no `check` (or unknown id) is discarded; a cited one kept; `playbook_coverage` counts match | correct | floor + coverage |
| V5 | the BRD `fact_checker` AND `chairperson` branches (non-crew) → no playbook, no discard, NOT BRANCH_FAILED; a crew lens with a deleted playbook → BRANCH_FAILED | correct | complication 2 (R2) |
| V6 | deterministic-path branch unaffected (no discard); `prompt_only`/aggregate builds get `playbook_text=None` (unchanged) | correct | complication 3 + injection scope |
| V7 | `python -m pytest platforms/hermes/tests -q` | green (updated fixtures) | no regression |
| V8 | `python -m pytest tests/conformance -q` | green | no cross-platform regression |
| V9 | no `framework/**` diff; Hermes `FRAMEWORK_SPEC_VERSION` `0.32.6` unchanged | GATE-SPEC no-op | version scope |
| V10 | `diff` Hermes `finding_filter.py` vs the plugin's | byte-identical (drift guard) | vendor parity |
| V11 | the added `check` / `playbook_coverage` keys survive the JSON sidecar write + `SagaReviewResult` re-export; no strict validator rejects them | green | additive-shape safety |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[0.4.0]`
- [ ] `docs/PARITY.md` — Layer-Playbooks row (Hermes BRD+PRD)
- [ ] `plans/DECISIONS.md` — D-0046
- [ ] `plans/HERMES-BACKLOG.md` — Phase 2 shipped; H-4 closed
- [ ] `plans/HANDOFF.md` — arc progress
- [ ] `CHANGELOG.md` (root) — Hermes 0.4.0 (playbook injection BRD+PRD)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Threading `check` breaks dedup / an existing test's finding shape | med | `check` is optional + NOT in `_identity_hash`; V3/V7 cover; update the 4 named tests |
| R2 | Persona→lens mapping wrongly BRANCH_FAILs a non-crew branch persona — **`fact_checker` + `chairperson` are real BRD branches with no playbook** (`persona_mappings.yaml:44`) | **high** | rule is keyed on `REVIEW_CREWS.yaml` crew membership, NOT file presence (complication 2); V5 asserts the BRD `fact_checker` branch runs normally with no playbook/floor |
| R3 | Discard-uncited nukes all findings if the LLM ignores the citation instruction | med | discard applies to LLM path only; the instruction is inlined + in `MCP_REVIEW_ACTIONABLE_RULES`; a lens that cites nothing yields 0 findings + a `playbook_coverage` of all-`beyond_checklist:0` — a visible signal, not a crash |
| R4 | `parents[5]` framework-root walk is fragile when Hermes is installed elsewhere | low | identical to the already-accepted `review_scoring` crews-path idiom; reuse it, don't invent a second mechanism |
| R5 | `prompt_only` MCP review mode (`tool_registry.py:1624`, LLM at `:1648`) is a second review path left without playbooks/floor | med | explicitly scoped out of Phase 2 (Approach §Injection); documented follow-on — Phase 2 covers the saga per-branch team-review path (the primary one) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The playbook contract: inject per-(layer,lens) playbook; every finding cites `check:`; synthesizer discards uncited + emits `verdict.playbook_coverage` | `## Playbooks` | framework/governance/REVIEW_TEAM.md:210 |
| 2  | Hermes has **zero** playbook injection today (persona files only) | `Layer Playbooks` | docs/PARITY.md:184 |
| 3  | The branch prompt is assembled as a `parts` list; persona text is one element — the injection site | `assemble_project_review_prompt` | platforms/hermes/src/mcp_server/prompts/context_builder.py:383 |
| 4  | The finding-format rules are a code constant (where the `check:` instruction goes) | `MCP_REVIEW_ACTIONABLE_RULES` | platforms/hermes/src/mcp_server/prompts/context_builder.py:121 |
| 5  | The finding model (7 keys) has NO `check` field today (`_coerce_findings`) | `_coerce_findings` | platforms/hermes/src/mcp_server/review/persona_output_parser.py:24 |
| 6  | The reduced record is a **frozen `ReducedFinding` dataclass** (no `check`) — `check` must be added to it + its construction, not just `_normalize_record` | `ReducedFinding` | platforms/hermes/src/mcp_server/review/saga_reducer.py:7 |
| 7  | Dedup identity is `message+target_layer+action` (adding `check` won't change it) | `_identity_hash` | platforms/hermes/src/mcp_server/review/saga_reducer.py:38 |
| 8  | The LLM review path (where injection matters) vs the deterministic path | `_branch_llm_findings` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:364 |
| 9  | The verdict/summary object where `playbook_coverage` is added | `synthesis_summary` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:876 |
| 10 | Hermes locates repo `framework/` at runtime via the `parents[5]` idiom (playbooks reachable the same way) | `parents[5]` | platforms/hermes/src/mcp_server/review/review_scoring.py:57 |
| 11 | `canonical_persona` already aliases persona names (reused for persona→lens) | `canonical_persona` | platforms/hermes/src/mcp_server/review/review_scoring.py:49 |
| 11b| Branch personas come from `persona_mappings.yaml` (a SUPERSET of the crew); the BRD list includes `fact_checker` + `chairperson` which have no playbook | `fact_checker` | platforms/hermes/skills/persona_mappings.yaml:44 |
| 11c| The shared builder has multi-persona callers incl. the LLM `prompt_only` mode | `run_executor` | platforms/hermes/src/mcp_server/tool_registry.py:1648 |
| 11d| `run_project_review_build` (`runner.py`) is the intermediary every builder caller uses (must thread `playbook_text`) | `run_project_review_build` | platforms/hermes/src/mcp_server/review/runner.py:27 |
| 12 | Plugin reference: playbook inlined literally + `check:` instruction; missing→BRANCH_FAILED | `Layer-specific playbook` | platforms/claude-code-plugin/skills/doc-brd-audit/SKILL.md:113 |
| 13 | Plugin portable filter: `filter_findings` + `emit_coverage` (stdlib) | `filter_findings` | platforms/claude-code-plugin/tools/finding_filter.py:19 |
| 14 | BRD (5) + PRD (6) playbook files exist — no content authoring | `lens: business_analyst` | framework/playbooks/01_BRD/business_analyst.md:3 |
| 15 | Most recent decision is D-0045 → next free is D-0046 | `D-0045` | plans/DECISIONS.md:12 |

## Review log

### Pass 1 — 2026-07-03T19:30:28-04:00 — self-review

- **F1 (vendor, don't port `finding_filter`).** Read the plugin's
  `finding_filter.py` — it is fully engine-agnostic (stdlib; operates on `dict`
  findings with a `check` field). So the parity-right choice is a **byte-identical
  vendor + drift-guard test**, not a divergent port (which would fork the
  citation-filter contract). Updated Scope, Created-table, Task 1, added V10.
- **F2 (injection-path precision).** The playbook rides the *shared* prompt builder,
  so it lands in both the deterministic and LLM paths' `prompt_text`; only the
  discard+coverage are LLM-path-gated. Refined complication 3 + V6 to say exactly
  that (avoids implying injection is LLM-only).
- **Version:** Phase 2 ships an *exercised* capability (review behavior changes), so
  it correctly bumps Hermes MINOR `0.3.0 → 0.4.0` — unlike Phase 1's latent no-bump.
- Citation gate: 15 rows resolve (row 14 → in-file symbol; row 13 → drift-corrected).

### Pass 2 — 2026-07-03T20:05:00-04:00 — independent (fresh-context)

Fresh `code-reviewer` verified all 15 citations resolve and confirmed the vendor
decision, the version bump (0.3.0→0.4.0 MINOR correct for an exercised capability),
and complication-3 (deterministic-path exemption). **3 load-bearing findings, all
folded:**

- **F-LB1 — `fact_checker` BRANCH_FAILED bug (the important one).** Branch personas
  come from `persona_mappings.yaml:44` (a superset of the crew); the BRD list
  includes `fact_checker` (no alias, no playbook) + `chairperson`. My "missing
  playbook → BRANCH_FAILED" rule would have hard-failed the working `fact_checker`
  branch on **every BRD review**. Rekeyed complication 2 + the loader rule + R2 on
  **crew membership** (`REVIEW_CREWS.yaml`), not file presence: non-crew branch
  personas get no playbook + no floor, not a failure. V5 now tests the BRD
  `fact_checker` path (PRD-only testing would miss it). Added Claim 11b.
- **F-LB2 — "single injection site" false.** The builder has 3 multi-persona callers
  incl. the LLM `prompt_only` mode (`tool_registry.py:1648`). Added explicit
  plumbing (an optional `playbook_text` param threaded orchestrator → `runner.py` →
  builder; only the single-persona branch passes it, others pass `None`) and scoped
  Phase 2 to the saga per-branch path — `prompt_only`/aggregate injection is a
  documented follow-on (R5). Added Claims 11c/11d + `runner.py` to the file table.
- **F-LB3 — `check`-threading under-scoped.** `runner.py` (intermediary) and the
  frozen `ReducedFinding` dataclass (`saga_reducer.py:7-18`, no `check` slot) were
  missing — `check` would never reach the verdict. Added both to scope + complication
  1; pinned `playbook_coverage` to **pre-reduce** counting (dedup keeps one branch's
  citation → post-reduce under-reports). Corrected count to 7 code + 4 test files.
- Minor citation drifts fixed (row 5 7-keys, 6→`ReducedFinding`, 11→:49, 15→:12);
  added V11 (additive-shape safety).

**Result:** ready
