# DOC-CHECK Plan — flow review/remediation loop (spec) + automated triggers

| Field      | Value                          |
|------------|--------------------------------|
| Task       | DOC-CHECK                      |
| Depends on | framework spec `0.6.0`; the per-layer `-audit`/`-fixer` skills + Hermes validation runtime (both exist) |
| Status     | IN PROGRESS — Phase 0 merged (PR #17, spec `0.7.0`); Phases 1–4 (linter/hook/CI/parity) implemented on `claude/doc-check-triggers` |
| Feeds      | an engine-agnostic review→remediation→gate loop in the spec, with write-time (#1) + PR-time (#2) triggers, both platforms |

## Objective

The flow today models only *creation* — BRD→…→IPLAN with a readiness gate (≥90)
between layers. **Review** and **remediation** exist only as *platform*
capabilities (`doc-<layer>-audit`/`-fixer`, Hermes `UCR_*`/`UCRem_*`); they are
not concepts in the spec, and nothing fires them automatically. This task (a)
models the **review→remediation→gate loop and its trigger points** in the
framework spec as an engine-agnostic **light contract**, then (b) implements two
of those trigger points — **`on_author`** (write-time, #1) and **`pre_merge`**
(PR-time, #2) — in the platforms, backed by a deterministic structural check.

> **Decisions (from discussion):** spec model = **light contract** (name the loop
>
> + trigger points + what platforms must surface; leave the *how* to platforms).
> Automation = **spec + plugin hook + CI** (build #1 and #2 now, accepting a
> deterministic check behind them). Framework-first, not tooling-first.

## Background — what exists vs. what's missing

| Capability | Plugin | Hermes | Framework spec |
|------------|--------|--------|----------------|
| Review (semantic) | `doc-<layer>-audit` | `UCR_*` + `sdd-review-personas` | — (only the ≥90 gate threshold) |
| Remediation | `doc-<layer>-fixer` | `UCRem_*` | — |
| Gate | `gate-check` (CHG) | CHG runtime | readiness ≥90; CHG gates |
| Deterministic doc check | **none** | `src/mcp_server/validation/*` + scoring CLI | registry + templates (rules' source of truth) |
| Loop / trigger-point **model** | — | — | **none** ← this task adds it |
| Write-time trigger (#1) | **none** (no hooks) | MCP validate/score tool | — |
| PR-time trigger (#2) | **none** | **none** | `spec_gate.py` gates the *framework*, not instance docs |

Two facts shape implementation:

1. **Consumer-facing.** This repo ships the framework + platforms; it holds **no
   SDD instance documents**. The hook + CI fire in a *consuming project*; here
   they're developed + tested against **fixtures**.
2. **Deterministic vs LLM.** Hooks (shell) and CI (Actions) are deterministic;
   the `-audit` skills are LLM reasoning. So the automated triggers enforce a
   **structural** check and *nudge/defer to* the LLM audit for the semantic score.

## Scope

**In:**

+ **Phase 0 — spec light contract** (`framework/`): a new engine-agnostic doc
  modeling the per-artifact loop + named trigger points + the light conformance
  contract (what a platform surfaces at each point). GATE-SPEC change ⇒ version
  bump + CHANGELOG + both FSV + 54-skill ripple.
+ **Phase 1 — deterministic check** (`tools/sdd_doc_lint/`): a shared,
  engine-agnostic, stdlib structural linter that *implements* the trigger-point
  check (the registry/template-driven structural subset). Not the centerpiece —
  the platform-tier implementation of the spec's contract.
+ **Phase 2 — `on_author` (#1):** a plugin Claude Code **PostToolUse** hook on
  `docs/<NN>_<X>/**` → run the check, print findings, nudge `doc-<layer>-audit`.
  **Advisory** (never blocks the edit).
+ **Phase 3 — `pre_merge` (#2):** a reusable **`doc-review.yml`** running the
  check over changed `docs/**` on PRs; **blocking** on structural violations.
  Self-tested here against fixtures; shipped as a consumer template.
+ **Phase 4 — Hermes mapping + parity:** document Hermes' existing capabilities
  against the spec's trigger points (its server validator already covers the
  `on_author` analog); add CI parity via the same `doc-review.yml`.
+ Fixtures: valid + intentionally-broken sample docs to test linter, hook, CI.

**Out (deferred / not in scope):**

+ Re-implementing the **semantic ≥90 readiness score** deterministically — stays
  the LLM `-audit` skill. The check is structural only.
+ Running the LLM audit *inside* CI (needs an API key + cost + nondeterminism).
+ **Mandating check semantics/severities in the spec** — the light contract names
  the points + what to surface, not *how* to check (per the prescriptiveness
  decision). A heavier "check catalog" is a possible later spec increment.
+ Converging Hermes' `mcp_server/validation` onto the shared linter (larger
  refactor; later option).
+ Auto-applying `-fixer` from a hook (remediation stays a deliberate step).

## The spec model (Phase 0 detail)

New `framework/governance/REVIEW_REMEDIATION_FLOW.md` (engine-agnostic):

+ **Loop:** `Draft → Review (findings + readiness score) → Remediate (fix →
  re-review) → Gate (≥ threshold) → Approved → downstream`. Ties to the existing
  `status` enums + the ≥90 readiness gate (this names the review/remediate
  *stages*; it does not change the gate thresholds or the CHG gates).
+ **Trigger points (engine-agnostic names):**
  + `on_author` — artifact created/edited → review (findings + score).
  + `on_gate_fail` — score < threshold → remediation, then re-review.
  + `pre_promotion` — before generating the downstream layer → gate must pass.
  + `pre_merge` — artifact enters shared history (PR/integration) → review gate.
+ **Light conformance contract:** at each trigger point a platform supports, it
  MUST surface (a) findings, (b) the readiness score vs the gate, (c) the
  remediation path. *How* (deterministic vs LLM, hook vs CI vs tool) is the
  platform's choice. Platforms document their trigger-point → capability mapping.
+ A non-normative mapping table (plugin / Hermes) so the contract is concrete.

Conformance: add the file to `test_governance.py` `EXPECTED_FILES`; confirm
`test_spec_hygiene` (engine-agnostic). Optional light guard: the doc names the
four trigger points (low cost, prevents silent omission).

## Step sequence

1. **Phase 0** — write the spec doc; register in governance README +
   `EXPECTED_FILES`; bump `0.6.0 → 0.7.0` (VERSION + 2 FSV + 54 skills) +
   CHANGELOG; conformance + `spec_gate` green. *(Its own PR — a clean GATE-SPEC
   change.)*
2. **Phase 1** — `tools/sdd_doc_lint/` + fixtures + unit test.
3. **Phase 2** — plugin `on_author` hook + manifest + docs (advisory).
4. **Phase 3** — `doc-review.yml` `pre_merge` gate + fixture self-test (blocking).
5. **Phase 4** — Hermes trigger-point mapping doc + CI parity; `docs/PARITY.md`
   pointer.
6. **Verify**; **land** per phase; update CHANGELOG / platform changelogs.

> Sequencing note: Phase 0 is a framework-spec (GATE-SPEC) change and lands on
> its own; Phases 1–4 are platform/tooling and can follow in a second PR (they
> reference the spec contract Phase 0 establishes).

## Verification

+ Phase 0: conformance green (governance file-set + hygiene); `spec_gate` green
  vs origin/main; versions aligned at `0.7.0`.
+ Phase 1: `python -m sdd_doc_lint <fixtures>/valid` exits 0; `/broken` exits
  non-zero with expected codes; unit test green.
+ Phase 2: writing a fixture doc in a scratch session surfaces the advisory
  (documented manual test — hooks need a live session).
+ Phase 3: `doc-review.yml` passes on valid fixtures, fails on broken.
+ `pre-commit run --all-files` clean; linter has no engine tokens / no
  Hermes-server dependency; spec doc passes hygiene.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Spec contract drifts toward over-prescription | Light contract only (names points + what to surface); check semantics/severity explicitly out (Scope-Out); a catalog is a separate later increment. |
| R2 | Over-engineering the deterministic check into an audit re-implementation | Structural subset only; the LLM `-audit` keeps the semantic score; phase-gated. |
| R3 | Plugin-Hermes coupling | The deterministic check is engine-agnostic stdlib in `tools/`; the plugin hook shells to it, never to the Hermes server. |
| R4 | Hook too aggressive / annoying | Advisory only, path-scoped to `docs/<NN>_<X>/**`, fast/deterministic, user-disable-able. CI is the blocking layer. |
| R5 | No `docs/` in this repo → triggers look untested | Fixtures + a self-test CI job exercise the linter + workflow in-repo. |
| R6 | GATE-SPEC self-gate (Phase 0) | Phase 0 bumps VERSION + CHANGELOG by construction; FSV match; suite green. |
| R7 | Plugin manifest hook schema correctness | Verify the Claude Code plugin `hooks` (PostToolUse) schema against current docs before wiring; POSIX-portable script. |
| R8 | Duplication with Hermes' validator | Bounded (both read the same registry/templates); convergence is a later option. |

## Review log

> ≥2 passes before implementation (CLAUDE.md).

### Pass 1 — 2026-05-25 (post-redirect rewrite)

+ **Reframed tooling-first → framework-first.** The prior draft led with the
  linter; per the redirect, Phase 0 now models the loop + trigger points in the
  spec (light contract), and the linter is repositioned as the *platform-tier
  implementation* of a trigger-point check, not the centerpiece.
+ **Honored the light-contract decision.** Spec names points + what to surface,
  leaves the *how* to platforms; check semantics/severity kept out of the spec
  (Scope-Out, R1) to avoid over-prescription.
+ **Kept the "build #1 + #2 now" decision.** Phases 2–3 implement `on_author`
  (advisory hook) + `pre_merge` (blocking CI), backed by the Phase 1 check.
+ **Split the PRs.** Phase 0 (framework/GATE-SPEC) lands separately from the
  platform/tooling phases so the spec bump is a clean, reviewable change.

### Pass 2 — 2026-05-25

+ **Trigger-point naming sanity.** `on_author` / `on_gate_fail` / `pre_promotion`
  / `pre_merge` cover the lifecycle without overlap; #1 = `on_author`, #2 =
  `pre_merge`; the other two map to existing capabilities (gate-check /
  fixer) so the contract isn't inventing unimplemented points.
+ **Semver.** Phase 0 is additive (new governance doc, no change to existing
  gates/thresholds) ⇒ **minor** `0.6.0 → 0.7.0`. No change.
+ **Conformance footprint.** New governance file ⇒ `EXPECTED_FILES` + hygiene
  (same pattern as `SECURITY_REVIEW.md` in PR #12); optional trigger-point-name
  guard noted as low-cost. No change.
+ No further findings — implementable.

## Implementation log

### Phase 0 — merged (PR #17, 2026-05-25)

`framework/governance/REVIEW_REMEDIATION_FLOW.md` (light contract: loop + four
trigger points), spec `0.6.0 → 0.7.0`, registered in governance README +
`test_governance` `EXPECTED_FILES`.

### Phases 1–4 — 2026-05-25 (branch `claude/doc-check-triggers`)

+ **Phase 1** — `tools/sdd_doc_lint/` stdlib linter (PyYAML to read the registry):
  trace-tag/ID forms, required cumulative tags, `@threshold:` format, EARS
  `THE…SHALL` grammar, placeholder leakage. Valid + broken fixtures; 3-test
  unit suite. Fixed a false-positive (threshold keys vs element IDs). Fixtures
  excluded from markdownlint.
+ **Phase 2** — plugin `on_author` hook: `hooks/hooks.json` (PostToolUse
  Write|Edit) + `hooks/sdd-doc-review.sh` (advisory nudge to `doc-<layer>-audit`,
  best-effort `sdd_doc_lint` findings, always exit 0). Verified across non-SDD /
  no-linter / linter-present cases. Hook schema confirmed via the
  `claude-code-guide` agent (`hooks/hooks.json`, `${CLAUDE_PLUGIN_ROOT}`,
  `tool_input.file_path`, `hookSpecificOutput.additionalContext`).
+ **Phase 3** — `.github/workflows/doc-review.yml` (`pre_merge`): unit-tests the
  linter, smoke-passes valid fixtures, asserts broken fixtures fail the gate,
  lints `docs/` (none here → no-op). All steps simulated green locally.
+ **Phase 4** — `docs/PARITY.md` per-trigger mapping table; plugin + Hermes
  READMEs document their trigger-point bindings; Hermes adopts the shared
  `doc-review.yml` for `pre_merge` parity.
+ **Design note (consumer runtime):** the deterministic linter runs cleanly in
  **CI** (repo checked out) — that is the reliable `pre_merge` gate. The
  **write-time hook is advisory** (nudge always works; linter findings are
  best-effort when importable) because reliably running a deterministic linter
  inside an arbitrary consumer's live session would need bundling/duplication.
  This matches D3 (hook advisory, CI blocking). Bundling the linter into the
  plugin / a consumer-install story is a possible follow-up.
+ **Verification:** conformance still **49/49** (platform/tooling changes don't
  touch `framework/`); no spec bump; `pre-commit` clean on changed files.
