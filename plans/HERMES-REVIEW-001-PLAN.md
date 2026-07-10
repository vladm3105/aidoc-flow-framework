# HERMES-REVIEW-001 Plan — fix the 2026-07-09 Hermes platform review findings

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-REVIEW-001                           |
| Type           | bugfix                                      |
| Status         | PLANNED — 2026-07-09                        |
| Depends on     | 2026-07-09 four-agent Hermes review (working copy `tmp/REVIEW-2026-07-09_hermes.md`; this plan is self-contained) |
| Feeds          | Hermes at genuine spec-`0.36.2` parity on the authoring/runtime surfaces (not just the lint); the Hermes-parity arc (`plans/HERMES-BACKLOG.md`) |
| Version impact | Hermes stream only (independent of framework/plugin): PATCH ×2 (PR-DOCS, PR-CODE); MINOR (PR-BDD — new authoring form + conformance guard); MINOR (PR-ADAPT); PR-BL none. No `framework/VERSION` change. |

## Objective

Resolve the 19 findings (5 high / 8 medium / 6 low) from the 2026-07-09 Hermes
review. The through-line: the `FRAMEWORK_SPEC_VERSION = 0.36.2` pin is
string-honest (vendored lint byte-identical) but **overstates real conformance**
— Hermes's native prompt templates and adaptation-knob handling lag the spec,
and no conformance test exercises MCP prompt content, so the drift is invisible.
Fixes land as Hermes-stream PRs; the backlog is corrected first so the work is
tracked.

## Scope

**In:** all 19 findings, grouped into PR-BL / PR-DOCS / PR-CODE / PR-BDD /
PR-ADAPT below. Everything is under `platforms/hermes/` (+ the
`plans/HERMES-BACKLOG.md` correction and one new Hermes-side `platforms/hermes/tests/` guard).

**Out of scope (deferred):**

- The **architectural saga gate H-1** (G-R1 invariant) and other pre-existing
  DEFERRED backlog items — untouched; this plan fixes review findings, not the
  parity backlog's own long-poles.
- **Full re-architecture of the adaptation surface.** PR-ADAPT does the
  *minimum honest* consumption (read `.aidoc/profile.yaml`; honor the knobs
  that are prompt-injectable + reconcile `review_mode`); a complete
  per-knob-per-tool implementation, if larger, splits to its own follow-up.
- Historical migration docs (`docs/plans/*`, `docs/CHANGELOG/CHANGELOG_v1.*`) —
  their `ucx_hermes`/`mcp_ucx` paths are expected legacy; only *active-facing*
  docs are fixed.
- The framework/ spec and the plugin — this is a Platform-A-only initiative.

## Approach

Five PRs. **PR-BL first** (correct the backlog's wrong "D-0038 auto-satisfied"
claim so the rest is tracked), then the cheap high-visibility sweeps (PR-DOCS,
PR-CODE), then the large authoring rewrite (PR-BDD) and the design item
(PR-ADAPT). Hermes versions independently, so each code/doc PR bumps
`platforms/hermes/VERSION` + `platforms/hermes/CHANGELOG.md`. Hermes tests
(`pytest`, 511 baseline) + the shared conformance suite must stay green.

### PR-BL — backlog corrections (plans/HERMES-BACKLOG.md; no version bump)

| # | Fix | Finding |
|---|-----|---------|
| BL1 | Delete/qualify the "D-0038…D-0044 AUTO-SATISFIED via vendored lint + shared templates — none needs Hermes-native code" banner: it holds for the lint + the shared layer template, **not** for Hermes's native BDD prompts. | H1 root cause |
| BL2 | Add a **HIGH** H-item: "Hermes native BDD prompts/persona/output-schema still teach Gherkin — rewrite to YAML-BDD (D-0038)" → PR-BDD. | H1 |
| BL3 | Add an H-item: "`.aidoc/profile.yaml` / adaptation surface unread at runtime — honor the 6 knobs beyond `quality_loop_max_iterations`" → PR-ADAPT. | M1 |
| BL4 | Correct the H-4/H-5 framing (playbook injection is IMPLEMENTED, not open) if still mis-stated. | at-parity note |

### PR-DOCS — docs / version sweep (Hermes PATCH)

| # | Fix | Finding |
|---|-----|---------|
| D1 | `pyproject.toml:3` `version = "0.1.0"` → `0.7.3`. Reconcile with the `HERMES-README-VERSION-DRIFT` FRAMEWORK-TODO entry (the sync hook was meant to cover the Hermes README — verify it does after this). | H3 |
| D2 | `README.md:73-82` conformance block: real values (`VERSION` 0.7.3, `FRAMEWORK_SPEC_VERSION` 0.36.2); `:80` "conformance to framework spec `0.1.0`" → `0.36.2`; `:107-108` table. | H3 |
| D3 | `docs/HERMES_INTEGRATION.md` — rewrite all `/opt/data/ucx_framework/ucx_hermes/src` cwd/PYTHONPATH/venv paths to the real `platforms/hermes/src` layout (`:87-94,101-102,144-158,219-224,240-243`); fix the Python `3.11+`→`>=3.12` contradiction (`:532` vs `:193`); drop/repoint the `ucx_kb` KB smoke-test section (`:119-136,206-256` — superseded by engramory, not in this runtime). | H4, M8, L6 |
| D4 | `docs/README.md:289-298` — remove/repoint the dead `migration/MIGRATION_FROM_MCP_UCX.md` §7; fix the "Version 2.0.0"/`ucx_hermes/` self-id (`:4,33`); persona count 15→16 (`:195`); add `SPEC-011` to the SPEC list (`:269-280`). | H5, M4, L6 |
| D5 | `docs/ROADMAP.md:16-20` — mark the "2.0.0" version table historical (it has the banner; the table doesn't). | M4 |
| D6 | `CHANGELOG.md` — cut a released `## [0.7.3]` section (currently everything 0.2.0→0.7.3 is inline under `[Unreleased]`). | M5 |
| D7 | `README.md:13` "Source modules 18" → 20 (add `scoring`, `team_emulator`); `:47-64` tool table complete the registered set (27 tools; add `sdd_remediate`, `sdd_run_lifecycle`, `sdd_team_plan`, `sdd_set_project`/`sdd_get_project`). | M8 |

### PR-CODE — MCP server source fixes (Hermes PATCH; each with a regression test)

| # | Fix | Finding |
|---|-----|---------|
| C1 | `executor/api_runner.py:19-27` (lazy `_get_env_lock()` factory) + acquire site `:171` — `_api_env_lock` is a lazily-created `asyncio.Lock`. The factory docstring claims it "avoids binding to the wrong event loop" but does NOT: it caches one loop-bound lock reused across every later `asyncio.run` loop, so under LLM-branch `ThreadPoolExecutor` contention it `RuntimeError`s/hangs. **Fix:** replace with a module-global `threading.Lock`, **collapse the `_get_env_lock()` factory** (it is failed scaffolding), and change the acquire site `async with _get_env_lock():` → `with _get_env_lock():` (`threading.Lock` is NOT an async context manager — this is not a drop-in). **Consequence to note:** the lock is held across the awaited `litellm.acompletion` (`:171-174`), so with a threading.Lock parallel API-executor branches serialize — concurrency becomes moot for the API path (acceptable: correctness beats the current error). Add a parallel-thread regression test. | H2 |
| C2 | `reporting/contracts.py:317-351` `write_versioned_report_atomic` — replace the existence-check-then-`os.replace` TOCTOU with `open(..., "x")` (`O_CREAT\|O_EXCL`) + retry-on-`FileExistsError` (mirror `saga_orchestrator.py:119``_write_versioned_json`). | M2 |
| C3 | `review/saga_orchestrator.py:63` `datetime.utcnow()` → `datetime.now(UTC)` (the only deprecated-datetime call in production src; `saga_models.py:10` already does it right). | L1 |
| C4 | `tool_registry.py:1542` — wrap the blocking sync `run_project_review_build_saga(...)` in `await asyncio.to_thread(...)` so the review doesn't block the event loop (also unblocks keepalive/cancellation; composes with C1). | M3 |
| C5 | `cleanup/runner.py:139-152` — wrap each `unlink()` in try/except and append to `deleted` only after a successful unlink (currently records-then-deletes, aborts half-done on error). | L2 |
| C6 | `scoring/runner.py:94-98` — remove the dead `if isinstance(required, list): pass`; confirm/annotate the `:145-156` tdd/iplan silent-validation-fail intent. | L3 |

### PR-BDD — rewrite Hermes native BDD authoring to YAML-BDD (Hermes MINOR) + prompt-drift guard

| # | Fix | Finding |
|---|-----|---------|
| B1 | Rewrite `prompts/templates/creation/UCC_PROMPT_BDD.md` to the structured `scenarios:` YAML model (flat list, `type:`/`priority:`, per-scenario element-level `ears:` list, no Gherkin, no written `@ears`/`@prd`/`@brd` tags). Reference: `framework/layers/04_BDD/BDD-TEMPLATE.yaml` §scenarios (`:188-252`). | H1 |
| B2 | Rewrite `prompts/templates/review/UCR_PROMPT_BDD.md`: review criteria → YAML-scenario structure + element-level `ears:` coverage, not Gherkin syntax. (The false-flag consequence materializes when the review prompt is **dispatched to an LLM** — `prompt_only` external run or the LLM-saga branch; the deterministic default `_branch_prompt_findings` does structural/coverage analysis and never scores Gherkin. The rewrite is correct regardless.) | H1 |
| B3 | Rewrite `prompts/templates/remediation/UCRem_PROMPT_BDD.md` fix reference + examples to `scenarios:` YAML; drop the retired `@EARS.XX`/`@happy-path` tag convention (`:205-211`). | H1 |
| B4 | `skills/personas/qa_lead.md:38-46,70` — replace "Gherkin syntax purity" lens with the YAML-scenario structural lens. | H1 |
| B5 | `prompts/templates/creation/UCC_OUTPUT_SCHEMA.md:150-165` — Layer-4 output contract "Gherkin `.feature` files" → the `scenarios:` YAML block. | H1 |
| B6 | `prompts/templates/creation/UCC_PROMPT_EARS.md:116` `@bdd: BDD-01/login.feature` → `@bdd: BDD.NN.SS.xxxx`; `UCC_PROMPT_PRD.md:199` 3-segment `@brd: BRD.01.92d8` → 4-segment; the stale "cumulative" wording in `UCC_OUTPUT_SCHEMA.md:210,252,288` + `UCC_PROMPT_SPEC.md:154` + `UCRem_PROMPT_SPEC.md:24`. | M6, L4, L5 |
| B7 | **New Hermes-side conformance guard** (`platforms/hermes/tests/` — a Hermes-internal-prompt assertion should NOT couple the shared `tests/conformance/` to one platform's private files): assert the Hermes BDD prompts reference `scenarios:` and contain no **structural** Gherkin markers — `^\s*Feature:`, `^\s*Scenario:`, `Given/When/Then` inside a gherkin fence, and `@`-tag-on-BDD. **Do NOT grep the bare word "Gherkin"**: a correct YAML-BDD prompt legitimately says "author `scenarios:` YAML, NOT Gherkin" as an anti-drift instruction, which a bare-token grep would false-positive on. So this drift class becomes CI-visible (it currently isn't). | H1 (prevent recurrence) |

### PR-ADAPT — adaptation-surface consumption (Hermes MINOR; may split)

| # | Fix | Finding |
|---|-----|---------|
| A1 | Read `.aidoc/profile.yaml` at runtime (the spec's declared single input) in the creation/review paths; honor the prompt-injectable knobs (`active_layers`, `section_toggles`, `audit_threshold`, `glossary`) via the existing `context_builder` injection. **Wire the disk-read into the existing-but-unwired plumbing** — `creation/profile_contracts.py` already defines `resolve_threshold_precedence` (`profile_threshold` → `audit_threshold`) and `bind_registry_profile` with no caller; feed them rather than reimplement precedence. | M1 |
| A2 | Reconcile `review_mode`: the tool enum is `prompt_only\|saga_parallel`(`tool_registry.py:650-654`); the spec knob is`team\|single_pass`. Accept/alias the spec values (`team`→saga_parallel,`single_pass`→prompt_only) so a profile-declared`review_mode` is consumable by name. | M1, M7 |
| A3 | `quality_loop_max_iterations` — wire the knob (already tracked H-7 Phase-1b) if in cheap reach; otherwise leave to H-7 and note it. | M1 |

## Implementation sequence

1. **PR-BL** (backlog first — tracks the rest).
2. **PR-DOCS** → **PR-CODE** (cheap, high-visibility; independent; each Hermes PATCH + green pytest/conformance).
3. **PR-BDD** (largest; MINOR). B7 guard lands with it.
4. **PR-ADAPT** (design; MINOR; split if it grows).

Each Hermes PR: edit → `pytest` (511+ green) → shared `tests/conformance` green
→ Hermes `VERSION` bump + `CHANGELOG.md` → PR. Author-side review per
OPS-0065/0067 before push (the Hermes review prompts changed in PR-BDD are the
system-under-test — dispatch an adversarial reviewer on the YAML-BDD rewrite).

## Verification

- `cd platforms/hermes && python3 -m pytest -q` — 511+ green (PR-CODE adds
  regression tests for C1/C2; PR-BDD adds the B7 Hermes-side BDD-prompt guard,
  which runs under this pytest, not the shared suite).
- `python3 -m unittest discover -s tests/conformance` — green (shared suite;
  unaffected — the B7 guard is Hermes-side, not here).
- PR-BDD: grep the 3 BDD prompts + qa_lead + output schema for **structural**
  Gherkin markers (`^\s*Feature:`, `^\s*Scenario:`, Given/When/Then in a gherkin
  fence, `@`-tag-on-BDD) → 0, and for `scenarios:` → present. (Do NOT grep the
  bare word "Gherkin" — the correct rewrite keeps an explicit "NOT Gherkin"
  anti-drift line.) The B7 guard enforces this.
- PR-DOCS: grep active-facing docs for `0.1.0`/`2.0.0` current-state claims and
  `ucx_framework/ucx_hermes` paths → 0; `pyproject.toml` version = 0.7.3.
- PR-CODE C1: a test that spins 2+ threads each `asyncio.run`-ing an executor
  call contending on the env lock completes without `RuntimeError`/hang.

## Docs to update

- `platforms/hermes/CHANGELOG.md` (per PR), `platforms/hermes/VERSION` (PATCH/MINOR
  per PR), root `CHANGELOG.md` `[Unreleased]` (Hermes-stream entries),
  `plans/HERMES-BACKLOG.md` (PR-BL + close the added H-items as they ship),
  `plans/HANDOFF.md`. `docs/PARITY.md` Hermes row if a capability changes
  (PR-BDD authoring form; PR-ADAPT knobs).

## Risks

| Risk | Mitigation |
|------|------------|
| PR-BDD rewrite changes review behavior for existing BDD fixtures/examples | The example corpus is regenerated wholesale after framework/authoring changes; run the corpus lint + a sample BDD create/review to confirm the YAML prompts produce lint-clean output. The B7 guard prevents silent re-drift. |
| C1 `threading.Lock` fix under-tested (the bug is on a not-yet-default path) | Add the explicit parallel-thread regression test. NOT a drop-in: `threading.Lock` is a sync context manager, so the acquire site changes `async with` → `with` and the `_get_env_lock()` factory collapses (see C1). Default path (`_branch_prompt_findings`) is unaffected — the bug is LLM-branch-flag-only (verified). |
| PR-ADAPT balloons into a full per-knob implementation | Scoped to profile-read + prompt-injectable knobs + review_mode aliasing; anything larger splits to a follow-up (noted in Out-of-scope). |
| Doc version sweep re-drifts (pyproject not sync-wired) | D1 reconciles with the existing `HERMES-README-VERSION-DRIFT` sync-hook TODO; if pyproject isn't covered, add it to `sync-version-refs.sh` (mirrors the SYNC-CLAUDE-PLUGIN-VERSION-GAP fix). |

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | ----- | ------ | -------- |
| 1 | Hermes BDD creation prompt teaches Gherkin | `Gherkin syntax` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_BDD.md:3 |
| 2 | its example puts written `@ears`/`@prd` tags on a BDD artifact with no space after the colon | `@ears:EARS.01.03.c4d8 @prd:PRD.01.09.910c` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_BDD.md:84 |
| 3 | the BDD review prompt scores Gherkin syntax (the unmitigated false-flag path) | `Gherkin` | platforms/hermes/prompts/templates/review/UCR_PROMPT_BDD.md:5 |
| 4 | the qa_lead persona is a Gherkin purist (feeds creation + review) | `Gherkin` | platforms/hermes/skills/personas/qa_lead.md:38 |
| 5 | the Layer-4 output schema requires Gherkin `.feature` files | `Gherkin` | platforms/hermes/prompts/templates/creation/UCC_OUTPUT_SCHEMA.md:150 |
| 6 | the spec's BDD template is now a flat YAML `scenarios:` list (the rewrite target) | `scenarios:` | framework/layers/04_BDD/BDD-TEMPLATE.yaml:215 |
| 7 | HERMES-BACKLOG declares D-0038 auto-satisfied "via vendored lint + shared templates" (the wrong claim) | `AUTO-SATISFIED` | plans/HERMES-BACKLOG.md:16 |
| 8 | `_api_env_lock` is a lazily-created asyncio.Lock (via `_get_env_lock()`), acquired `async with` at :171 — the factory's "avoids wrong loop" docstring is a failed mitigation | `_api_env_lock: asyncio.Lock \| None = None` | platforms/hermes/src/mcp_server/executor/api_runner.py:19 |
| 9 | the saga fans branches over a ThreadPoolExecutor (each thread a fresh event loop) | `ThreadPoolExecutor(max_workers=max_workers)` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:677 |
| 10 | the env lock is awaited inside the per-thread executor call | `asyncio.run` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:439 |
| 11 | `write_versioned_report_atomic` does existence-check-then-os.replace (TOCTOU) | `if candidate_path.exists():` | platforms/hermes/src/mcp_server/reporting/contracts.py:344 |
| 12 | the correct O_CREAT\|O_EXCL pattern exists to mirror | `_write_versioned_json` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:119 |
| 13 | saga_orchestrator uses deprecated datetime.utcnow() | `datetime.utcnow()` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:63 |
| 14 | the blocking sync saga call sits in the async dispatch handler | `run_project_review_build_saga` | platforms/hermes/src/mcp_server/tool_registry.py:1542 |
| 15 | cleanup records a file deleted before unlinking, unguarded | `result.deleted.append` | platforms/hermes/src/mcp_server/cleanup/runner.py:139 |
| 16 | scoring has dead code | `if isinstance(required, list):` | platforms/hermes/src/mcp_server/scoring/runner.py:94 |
| 17 | pyproject version is frozen at 0.1.0 | `version = "0.1.0"` | platforms/hermes/pyproject.toml:3 |
| 18 | the README conformance block declares spec 0.1.0 (stale; real 0.36.2) | `0.1.0` | platforms/hermes/README.md:80 |
| 19 | HERMES_INTEGRATION uses the pre-migration ucx_framework path | `/opt/data/ucx_framework/ucx_hermes/src` | platforms/hermes/docs/HERMES_INTEGRATION.md:91 |
| 20 | the tool review_mode enum is prompt_only\|saga_parallel (collides with the spec team\|single_pass knob) | `["prompt_only", "saga_parallel"]` | platforms/hermes/src/mcp_server/tool_registry.py:652 |
| 21 | Hermes VERSION is 0.7.3 (the value docs/pyproject should carry) | `0.7.3` | platforms/hermes/VERSION:1 |
| 22 | the EARS creation prompt uses the retired @bdd file-path form | `@bdd: BDD-01/login.feature` | platforms/hermes/prompts/templates/creation/UCC_PROMPT_EARS.md:116 |

## Review log

### Pass 1 — 2026-07-09 — self-review (draft)

- Grouped 19 findings into 5 PRs; put backlog corrections (PR-BL) first so the
  rest is tracked (the review's #1 recommendation).
- Scoped PR-ADAPT to the *minimum honest* adaptation-surface consumption
  (profile-read + prompt-injectable knobs + review_mode aliasing), deferring a
  full per-knob build to a follow-up — minimal-and-realistic.
- Kept the architectural H-1 saga gate + pre-existing DEFERRED backlog long-poles
  out of scope (this plan fixes review findings, not the parity backlog).
- Added B7 (a BDD-prompt conformance guard) because the review's meta-finding is
  that prompt drift is CI-invisible — the guard converts the fix into a durable
  one.
- Open question for the independent pass: is the C1 concurrency bug reachable on
  any DEFAULT path, or strictly the LLM-branch flag path? The review says
  flag-only; the reviewer should confirm `_branch_prompt_findings` (deterministic
  default) truly never touches the executor lock, else C1's severity rises.

### Pass 2 — 2026-07-09 — independent (fresh-context subagent) + fold

All 22 ledger rows verified against source. **2 load-bearing findings, both
localized spec corrections (no scope change); the plan's structure, severity
framing, review_mode alias, and creation-path reasoning confirmed sound.** My
Pass-1 open question was resolved in the plan's favor: `_branch_prompt_findings`
(the `branch_llm_enabled=False` default) never calls `asyncio.run`/the executor
lock — so **C1 is genuinely flag-path-only; the DEFAULT path is safe** and the
H2 severity framing is honest.

Folded:

- **LB1** — the C1 fix was mis-specified: `api_runner.py:19` is a *lazy*
  `_get_env_lock()` factory (a failed mitigation whose docstring wrongly claims
  it dodges the wrong-loop bug), acquired `async with` at `:171`. `threading.Lock`
  is NOT an async context manager, so the fix is **not a drop-in** — it collapses
  the factory and changes `async with` → `with`. Corrected C1, row 8, and the
  Risks "drop-in" line; noted the API-path-serialization consequence.
- **LB2** — the B7 guard as drafted would false-positive on its own correct
  output (a good YAML-BDD prompt says "NOT Gherkin" as an anti-drift line, which
  a bare-`Gherkin` grep trips). Re-specified B7 + the Verification bullet to key
  on **structural** markers (`^Feature:`/`^Scenario:`/gherkin-fenced GWT/
  `@`-tag-on-BDD), not the bare token; moved the guard to a Hermes-side test.
- Minors folded: A1 now wires the disk-read into the existing-but-unwired
  `resolve_threshold_precedence`/`bind_registry_profile` plumbing rather than
  reimplementing; B2 states the precise false-flag trigger (LLM-dispatched only).
- Confirmed sound (no change): A2 alias mapping (`team`→saga_parallel,
  `single_pass`→prompt_only) matches REVIEW_TEAM.md + Hermes internal terms; no
  creation-path contradiction left behind (creation injects the YAML template,
  B1 closes the prompt side; no Gherkin `.feature` template exists); PR-BDD MINOR
  is correct (pre-1.0 output-form change).

### Pass 3 — 2026-07-09 — independent confirmation (fresh-context subagent)

A second fresh-context reviewer confirmed the LB1/LB2 folds are correct against
source and introduce no new inconsistencies (see verdict below).
It confirmed **LB1 fully folded** and found **one remaining inconsistency from
the LB2 fold**: B7's Hermes-side placement wasn't propagated to Scope + the
Verification bullet (both still routed the guard through the shared
`tests/conformance/`). **Folded:** Scope and Verification now consistently place
the B7 guard Hermes-side (`platforms/hermes/tests/`, run under `pytest`) — a
pure single-axis consistency fix, no source-claim or structural change. All
other checks (C1/row-8/Risks/A1/B2 consistency; ledger rows 8-12 resolve to real
symbols) passed.

**Result:** ready. Ledger has zero UNVERIFIED rows; three independent
fresh-context passes drove the load-bearing count to zero; the final fold was a
placement-consistency correction with no new source claims.
