# HERMES-ADAPT-ENFORCE-001 Plan — enforce the `audit_threshold` adaptation knob (the Hermes-side slice of H-16)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-ADAPT-ENFORCE-001                    |
| Type           | feature                                     |
| Status         | READY FOR PR — 2026-07-10 (3 review passes, 2 independent; verified-planning gate green) |
| Depends on     | HERMES-REVIEW-001 PR-ADAPT (#294, `hermes/v0.9.0`) — profile loader + `ProjectContext.profile` already shipped; this plan consumes them |
| Feeds          | HERMES-BACKLOG **H-16** (adaptation-surface enforcement); the Hermes-parity arc |
| Version impact | Hermes stream only: MINOR (new gate behavior + optional tool arg). No `framework/VERSION` change. |

## Objective

PR-ADAPT (H-16, partial) made Hermes **read** `.aidoc/profile.yaml` and honor two
knobs (`review_mode` alias + `glossary`/`section_toggles`/`active_layers` as
creation-prompt context). It deferred **enforcement** of the remaining knobs. This
plan closes the one deferred slice that is genuinely Hermes-native and unblocked:
**`audit_threshold` as a raise-only score gate** — a profile-declared per-layer
threshold RAISES the effective readiness gate for that layer and never lowers it
("never weakens a gate", per `ADAPTATION_SURFACE.yaml`). The framework's documented
per-layer default is **90** (`PROFILE-TEMPLATE.yaml:42`), so a profile value is
honored only when it is ≥ 90 (raise-only against the default); a lower value is out
of surface and ignored.

The other three deferred items are **not** in this plan because investigation shows
they are framework-level or low-value (see Scope §Out). This plan's second
deliverable is to *record why*, so no future session re-attempts a Hermes-only
`active_layers` cascade (which would break the byte-identical vendored lint's
conformance guard).

## Scope

**In (Hermes-native, unblocked):**

- **`audit_threshold` raise-only gate** wired into the scoring path. Semantics
  (spec-accurate against the documented default of 90):
  - a profile `audit_threshold[layer]` value is honored **only if ≥ 90** (the
    framework default per `PROFILE-TEMPLATE.yaml:42`); a value < 90 is ignored
    (out of surface — never weakens);
  - `effective_threshold = max(existing_effective_threshold, honored_profile_value)`,
    applied AFTER the existing tdd/iplan `max(threshold, 90)` floor — monotonic
    non-decreasing, so a profile value can only push the gate UP.
- **Reach the profile** — `sdd_score_validate` currently has no `project` arg, so
  `ctx` is `None` there today (F1). Add an **optional** `project` string arg to the
  `sdd_score_validate` schema; when supplied, resolve `ProjectContext` and read
  `ctx.profile.audit_threshold` (guarded `ctx.profile if ctx else None`). The layer
  key is derived from the report payload's `doc_type`/`layer` (both emitted by
  `validation/runner.py:506-507`) and normalized to the `ADAPTATION_SURFACE`
  vocabulary. With no `project` (or no profile / no matching layer key / a
  non-int value) → `profile_threshold` is `None` → behavior byte-identical to today.
- **Pipeline stage** — thread `project` into `_handle_lifecycle_pipeline`'s
  `score_validate` `score_args` (it currently strips everything but `report_file` +
  `threshold`, so the re-dispatch re-resolves `ctx=None` unless `project` is added).
- **A `threshold_source` trace** in the `sdd_score_validate` payload
  (`caller` / `readiness_floor` / `profile`) so a raised gate is observable.
- **Malformed-value guard** (F4) — `profile.audit_threshold` inner values are not
  type-checked by the loader (`_coerce_str_map` validates only the outer dict); the
  resolver must int-coerce/skip a non-int value rather than `TypeError` in `max()`.
- **Tests** — a handler/dispatch-level test (`_dispatch("sdd_score_validate", …)`
  against a fixture project with a real `.aidoc/profile.yaml`) that asserts the gate
  actually rises (F2 — a `validate_score`-only unit test would pass even if the
  wiring were dead), plus `validate_score` unit tests for raise-applies /
  below-90-ignored / no-profile-unchanged / malformed-value-skipped / the
  interaction with the tdd/iplan `90` floor.

**Out (framework prerequisites / low-value / already tracked — enumerated, NOT
designed here):**

- **Reconciling the documented default (90 for every layer) with the code's real
  base gates.** `PROFILE-TEMPLATE.yaml:42` documents a uniform 90 default, but the
  code applies a 90 floor ONLY to the tdd/iplan readiness gate
  (`scoring/runner.py:145`); every other layer's base gate is caller-supplied / `80`
  (pipeline). This plan enforces the profile *raise* against the documented 90, but
  does **not** change the base gate for non-tdd/iplan layers (that would alter
  existing gate behavior for all layers — a separate, riskier change). The
  doc-vs-code default mismatch is an observation, not fixed here.
- **`active_layers` cascade enforcement.** The cascade_rule
  (`ADAPTATION_SURFACE.yaml:96-108`) must relax `required_tags` / `can_reference` /
  coverage for a disabled skippable layer (BDD/ADR) across the traceability + audit
  consumers — which are the **vendored `sdd_doc_lint`** (TAG01 etc.), asserted
  **byte-identical** to the canonical `tools/sdd_doc_lint/` by
  `tests/conformance/platforms/test_doc_lint_vendoring.py`. A Hermes-only edit would
  break that guard, so cascade enforcement is a **framework change** (both
  platforms), not a Hermes-platform plan. Deferred to a framework initiative.
- **`section_toggles` structural omission.** Optional template sections are already
  never *required* (`validation/runner.py:224` + lint skip of `_required: false`), so
  disabling one changes no gate; structurally *omitting* it from template assembly is
  fragile (template-text surgery) and low-value. The current PR-ADAPT advisory prompt
  injection already honors it at the authoring altitude. Deferred unless a concrete
  need surfaces.
- **`quality_loop_max_iterations`.** Needs an outer review→remediate loop Hermes
  does not have (`iteration=1` hardcoded); tracked as **H-7**. Untouched.

## Approach

One PR (Hermes MINOR). The `project` arg is **optional**, so existing
report_file+threshold callers are unaffected:

1. **Schema** — add an optional `"project"` string property to the
   `sdd_score_validate` tool schema (`tool_registry.py:323`). Not added to
   `required`.
2. **Handler** (`tool_registry.py:1308`) — when `project` is supplied, the dispatch
   already computes `ctx = ProjectContext.resolve(arguments.get("project"))`
   (`tool_registry.py:1010`); read `profile = ctx.profile if ctx else None`, resolve
   the per-layer `profile_threshold` (int-coerced, ≥90 gate applied at the resolver
   or in `validate_score`), and pass it into `validate_score`.
3. **`validate_score`** (`scoring/runner.py:132`) — add keyword-only
   `profile_threshold: int | None = None`; honor it only if `>= 90`; compute
   `effective_threshold = max(effective_threshold, profile_threshold)` after the
   tdd/iplan floor; record `threshold_source`.
4. **Layer derivation** — from `report_payload["doc_type"]` (already read by
   `_extract_readiness_gate`, `scoring/runner.py:86`) or the report's `layer` field,
   normalized to the `ADAPTATION_SURFACE` layer key (reuse the normalization idiom
   from `profile.py`/`context_builder._normalize_layer_key`).
5. **Pipeline** — add `project` to the `score_validate` `score_args`
   (`tool_registry.py:1892`) so the re-dispatch resolves the profile.
6. **Tests** per Scope §In — including the handler-level test that would catch a
   dead wiring (F2).

## Verification

- `cd platforms/hermes && python3 -m pytest -q` — green (adds raise-only unit tests
  - the handler-level wiring test).
- `python3 -m unittest discover -s tests/conformance` — green (no vendored-lint
  change → `test_doc_lint_vendoring.py` byte-identity guard stays green; this is the
  invariant an `active_layers` cascade would have violated).
- Manual: a fixture project whose `.aidoc/profile.yaml` sets `audit_threshold: {TDD: 95}`
  → `_dispatch("sdd_score_validate", {report_file, threshold: 80, project})` raises
  the effective gate to 95; `{TDD: 70}` is ignored (< 90 default); no `project` /
  no profile → unchanged. Also verify a **non-floored** layer (isolates the profile
  raise from the tdd/iplan floor): a BRD report with caller `threshold: 80` and
  `audit_threshold: {BRD: 95}` → effective gate 95; `{BRD: 85}` → ignored (< 90).

## Risks

| Risk | Mitigation |
|------|------------|
| **Dead wiring** — profile unreachable if `project` isn't threaded (F1) | Own the optional `project` schema arg + pipeline `score_args` threading; a **handler-level** test (`_dispatch`) asserts the gate actually rises — a `validate_score`-only test would false-pass (F2). |
| Layer-derivation from `doc_type` wrong / absent | Real validation reports emit both `doc_type` and `layer` (`validation/runner.py:506-507`); any miss → `profile_threshold=None` → today's behavior (never weakens). Test the missing-`doc_type` path. |
| Malformed `audit_threshold` value (`{TDD: "high"}`) — loader doesn't type-check inner values (F4) | The resolver int-coerces/skips non-int values before `max()`; test a malformed value. |
| Adding `project` breaks existing callers | It is **optional** (not in `required`); absent → unchanged. |
| `max()` misread as full spec semantics | The gate is raise-only against the documented 90 default; the base-gate doc-vs-code mismatch is explicitly Scope §Out. |
| Someone later adds `active_layers` cascade to the Hermes lint | `test_doc_lint_vendoring.py` byte-identity guard mechanically blocks it; the plan records that cascade is a framework change. |

## Docs to update

- `platforms/hermes/CHANGELOG.md` + `platforms/hermes/VERSION` (MINOR), root
  `CHANGELOG.md` `[Unreleased]`, `plans/HERMES-BACKLOG.md` (H-16 progress; keep the
  framework-prerequisite items open with the "why" from Scope §Out).

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | ----- | ------ | -------- |
| 1 | `validate_score` takes only `report_file` + `threshold` (no profile/ctx/layer) | `def validate_score(*, report_file: Path, threshold: int)` | platforms/hermes/src/mcp_server/scoring/runner.py:132 |
| 2 | the effective threshold + tdd/iplan `max(threshold, 90)` floor live here | `effective_threshold = max(threshold, 90)` | platforms/hermes/src/mcp_server/scoring/runner.py:145 |
| 3 | the readiness gate is fail-closed (missing readiness → not passed) | `readiness_gate["gate_passed"] is False` | platforms/hermes/src/mcp_server/scoring/runner.py:154 |
| 4 | the layer/doc_type is recoverable from the report payload's `doc_type` | `report_payload.get("doc_type")` | platforms/hermes/src/mcp_server/scoring/runner.py:86 |
| 5 | `_extract_readiness_gate` only recognizes tdd/iplan | `if doc_type not in {"tdd", "iplan"}` | platforms/hermes/src/mcp_server/scoring/runner.py:90 |
| 6 | the `sdd_score_validate` handler passes only report_file+threshold, no ctx/profile | `threshold=int(arguments["threshold"]),` | platforms/hermes/src/mcp_server/tool_registry.py:1313 |
| 7 | the dispatch computes `ctx` once via `ProjectContext.resolve(arguments.get("project"))` | `ctx = ProjectContext.resolve(` | platforms/hermes/src/mcp_server/tool_registry.py:1010 |
| 7a | but `ProjectContext.resolve` returns `None` when no `project` arg is given — and `sdd_score_validate` has no `project` arg, so `ctx` is always `None` there (the F1 gap) | `if not project_arg:` | platforms/hermes/src/mcp_server/project_context.py:118 |
| 7b | the established pattern reads the profile guarded (`ctx.profile if ctx else None`) because `ctx` is routinely `None` | `profile=ctx.profile if ctx else None` | platforms/hermes/src/mcp_server/tool_registry.py:1468 |
| 8 | the score_validate tool schema has only report_file + threshold (no layer/project) | `name="sdd_score_validate"` | platforms/hermes/src/mcp_server/tool_registry.py:323 |
| 9 | the lifecycle pipeline score stage builds `score_args` (stripping `project`) and defaults `threshold` to 80 | `"threshold": stage_args.get("threshold", 80)` | platforms/hermes/src/mcp_server/tool_registry.py:1894 |
| 10 | `ProjectContext` exposes the loaded profile (from PR-ADAPT) | `profile: ProjectProfile` | platforms/hermes/src/mcp_server/project_context.py:110 |
| 11 | the profile carries `audit_threshold` as a `map[layer, int]` | `audit_threshold: dict` | platforms/hermes/src/mcp_server/profile.py:49 |
| 11a | the loader does NOT type-check `audit_threshold` inner values (only the outer dict) — a malformed value reaches the resolver (F4) | `def _coerce_str_map` | platforms/hermes/src/mcp_server/profile.py:95 |
| 12 | `resolve_threshold_precedence` is OVERRIDE precedence (explicit>profile>registry>default), the inverse of raise-only — so this plan rolls its own `max()` rather than reuse it | `elif profile_threshold is not None:` | platforms/hermes/src/mcp_server/creation/profile_contracts.py:175 |
| 13 | the spec declares audit_threshold raise-only (value must be ≥ the framework default; lower ignored) | `Raise-only` | framework/governance/ADAPTATION_SURFACE.yaml:56 |
| 14 | the framework per-layer default IS documented — 90 per layer (so raise-only is implementable now; corrects the earlier "no default exists" framing) | `Framework default: 90 per layer.` | framework/governance/PROFILE-TEMPLATE.yaml:42 |
| 15 | `LAYER_REGISTRY.yaml` has NO per-layer numeric audit/score threshold field (its only `threshold` key is an ID-pattern regex) — the default lives in the profile-template doc, not the registry/scoring code | `id_patterns` | framework/registry/LAYER_REGISTRY.yaml:214 |
| 16 | the `active_layers` cascade_rule relaxes required_tags/can_reference for a disabled layer across traceability+audit | `cascade_rule` | framework/governance/ADAPTATION_SURFACE.yaml:96 |
| 17 | the primary check that would false-positive on a disabled BDD/ADR is the lint's TAG01 required-upstream-tag check (no active_layers awareness) | `required = layers[artifact].get("required_tags", [])` | platforms/hermes/sdd_doc_lint/**init**.py:600 |
| 18 | that vendored lint is asserted byte-identical to the canonical copy by a conformance guard — a Hermes-only cascade edit would break it | `test_vendored_copies_are_byte_identical` | tests/conformance/platforms/test_doc_lint_vendoring.py:29 |
| 19 | optional sections are already not required (validation runner skips `required: false`) | `if item.get("required", True) is False:` | platforms/hermes/src/mcp_server/validation/runner.py:224 |
| 20 | `section_toggles`/`active_layers` are consumed today only as advisory creation-prompt text | `_format_adaptation_profile_block` | platforms/hermes/src/mcp_server/prompts/context_builder.py:498 |
| 21 | `quality_loop_max_iterations` needs an outer loop Hermes lacks (iteration hardcoded 1) | `iteration=1` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:637 |
| 22 | the tdd-readiness-gate scoring test is the pattern to follow for the raise-only tests | `test_scoring_validate_enforces_tdd_readiness_gate` | platforms/hermes/tests/unit/test_scoring_cli.py:89 |
| 23 | real validation reports emit both `doc_type` and `layer` in the JSON payload, so layer derivation is reliable when the profile is reachable | `"layer": layer,` | platforms/hermes/src/mcp_server/validation/runner.py:507 |

## Review log

### Pass 1 — 2026-07-10 — self-review (draft)

- Scoped to the ONE Hermes-native slice (`audit_threshold`) after the surface map
  showed the other three deferred items are framework-level (`active_layers`
  cascade = byte-identical vendored lint), low-value (`section_toggles` structural
  omission), or already tracked (`quality_loop` = H-7).
- Open question left for the independent pass: is the profile reachable in the
  `sdd_score_validate` path, and is layer-derivation-from-`doc_type` reliable?

### Pass 2 — 2026-07-10 — independent (fresh-context subagent) + fold

Independent reviewer verified all 22 (then) ledger rows against source and confirmed
the **scoping thesis is sound and well-evidenced** (audit_threshold is the only
unblocked Hermes-native knob; the `active_layers`/`section_toggles`/`quality_loop`
exclusions each check out — notably the vendored-lint byte-identity guard
`test_doc_lint_vendoring.py:29` confirms the cascade is a framework change). But it
found the plan's **implementation mechanism broken** and folded 4 findings:

- **F1 (critical) — the profile was unreachable.** `sdd_score_validate` has no
  `project` arg, so `ctx = ProjectContext.resolve(None)` is always `None`
  (`project_context.py:118`) → the Pass-1 design (`ctx.profile` "already resolved")
  would ship the gate **inert** (tests-green, feature-dead). **Folded:** the plan now
  owns an **optional** `project` schema arg + pipeline `score_args` threading + the
  `ctx.profile if ctx else None` guard, and Scope §In / Approach / the version-impact
  line drop the "no schema change" claim. New ledger rows 7a/7b.
- **F2 (high) — the test strategy couldn't catch F1.** A `validate_score`-only unit
  test passes even with dead wiring. **Folded:** Scope §In + Approach now require a
  handler-level `_dispatch("sdd_score_validate", …)` test against a fixture project.
- **F3 (medium) — the "no per-layer default exists" framing was wrong.**
  `PROFILE-TEMPLATE.yaml:42` documents "Framework default: 90 per layer." **Folded:**
  the exact raise-only-vs-90 semantics moved INTO scope (honor a profile value only
  if ≥ 90); the old §Out "blocked" item became the (narrower, true) doc-vs-code
  base-gate mismatch observation. Ledger row 14 corrected to cite the template.
- **F4 (low) — malformed `audit_threshold` values are unchecked** by the loader
  (`_coerce_str_map` validates only the outer dict). **Folded:** an int-coerce/skip
  guard + test; new ledger row 11a; new Risks row.

Confirmed sound (no change): raise-only monotonicity (`max()` after the 90 floor
never weakens), the `resolve_threshold_precedence`-is-override-so-don't-reuse-it
call, and the layer-from-`doc_type` derivation itself (row 23 — reports emit
`doc_type`+`layer`).

**Open for Pass 3:** does owning the `project` schema arg + pipeline threading fully
close F1 with no remaining dead-wiring path (e.g. does any OTHER caller of
`sdd_score_validate` still strip `project`), and is the ≥90 raise-only rule
consistent everywhere it's described in the revised plan?

### Pass 3 — 2026-07-10 — independent confirmation (fresh-context subagent)

A second fresh-context reviewer confirmed the F1–F4 fold is **clean and complete**
with **zero load-bearing findings**, verified from source:

- **F1 fully closed** — grep enumerated exactly two `sdd_score_validate` callers (the
  direct handler `tool_registry.py:1308` + the pipeline re-dispatch `:1897`); **no
  third caller strips `project`**. `sdd_run_lifecycle` already declares `project`
  required, so it flows to `stage_args` and can be threaded into `score_args`. No
  residual dead-wiring path.
- All new/changed ledger rows (7a/7b/11a/23) + rows 14/18 re-verified at their cited
  symbols; the ≥90 raise-only rule is mutually consistent across Objective / Scope /
  Approach / Verification / Risks; no surviving "no schema change" or "no default
  exists" claim; the `_normalize_layer_key` idiom (`context_builder.py:493`) the
  resolver reuses exists and already reconciles lowercase `doc_type` against uppercase
  profile keys.

Only two **cosmetic, non-load-bearing** notes were raised and both folded: a
non-floored-layer (BRD) verification example (added), and a coarse row-15 anchor
(left — the `id_patterns` symbol resolves and the claim is correct). No source-claim
or structural change.

**Result:** ready. Claim ledger has zero UNVERIFIED rows and the gate passes; three
review passes (two independent, fresh-context) drove the load-bearing count to zero;
the final fold was cosmetic with no new source claims. The plan is sized to one
Hermes-native slice (`audit_threshold` raise-only) with the framework-level /
deferred items enumerated, not designed — minimal-and-realistic.
