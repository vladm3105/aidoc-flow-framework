# ACTIVE-LAYERS-CASCADE-001 Plan — implement the `active_layers` cascade in the canonical lint (framework H-16 remainder)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | ACTIVE-LAYERS-CASCADE-001                   |
| Type           | feature (framework-spec-behavior)           |
| Status         | READY FOR PR — 2026-07-10 (3 review passes, 2 independent; gate green). **Implementation blocked on founder ratification of the §Governance A-vs-B decision.** |
| Depends on     | HERMES-ADAPT-ENFORCE-001 (`hermes/v0.10.0`) — the Hermes-side profile plumbing; this is the framework-level remainder of H-16 the Hermes plan deferred |
| Feeds          | HERMES-BACKLOG **H-16** (adaptation-surface enforcement, framework tier); both platforms via the vendored lint |
| Version impact | **OPEN GOVERNANCE QUESTION (see §Governance)** — recommended framework MINOR (`0.36.2 → 0.37.0`) + GATE-SPEC C2; both platforms re-declare `FRAMEWORK_SPEC_VERSION`. No platform-runtime change beyond the re-vendored lint. |

## Objective

The `.aidoc/profile.yaml` `active_layers` knob lets a project disable a **skippable**
layer (BDD or ADR). The spec's `cascade_rule` (`ADAPTATION_SURFACE.yaml:96`) already
requires that when a skippable layer is disabled, the **traceability + audit
consumers must stop demanding a reference to, and stop flagging the absence of, that
layer** across every downstream layer that would otherwise read it. That rule is
**specified but unimplemented** — the canonical `sdd_doc_lint` is profile-blind
(zero `active_layers`/`.aidoc` awareness), so a project that legitimately skips BDD
still gets TAG01 "requires upstream tag `@bdd:`" failures on ADR/SPEC/TDD.

This plan implements the cascade in the **canonical lint** (`tools/sdd_doc_lint/`),
which both platforms vendor byte-identically. It is the framework-tier remainder of
H-16 that HERMES-ADAPT-ENFORCE-001 correctly deferred (a Hermes-only edit would break
the vendor byte-identity guard).

## Scope

**In:**

- **Read `active_layers`** from `.aidoc/profile.yaml` in the canonical lint's CLI
  entry (`__main__.py`), auto-discovered by walking up from the target path (mirrors
  the existing `find_registry` upward search), with an explicit `--active-layers`
  override for testing. No profile / knob absent → **all layers active → behavior
  byte-identical to today** (the safety default).
- **Thread a computed `disabled_skippable` set** into `lint_path` and apply it at the
  **single load-bearing cascade site — TAG01** (the independent review established that
  TAG01 is the *only* place a reference is *demanded*; `can_reference` has **zero
  usages** in the lint, and COV02/TRACE-RES-001/REFGRAN01 do **not** fire on the normal
  disabled-layer path — see §Verified-no-change):
  - **TAG01** (`__init__.py:600`) — the only change. Build an **effective** per-layer
    `required_tags` as a `.copy()` of the registry view **minus** the disabled layers
    (never an in-place mutation of the module global) and use it in the "requires
    upstream tag" check, so a disabled skippable layer is not demanded on ADR/SPEC/TDD.
    The disabled set is **case-normalized to the registry's lowercase tags** (`bdd`,
    `adr`) — `skippable` is spelled `[BDD, ADR]` but `required_tags` are lowercase.
- **Re-vendor** the canonical lint to the 2 byte-identical copies
  (`tools/sdd_doc_lint/sync-vendored.sh`); keep `test_doc_lint_vendoring.py` green.
- **Conformance tests** — a new positive cascade test (disable BDD → no TAG01/COV02/
  TRACE-RES-001 on ADR/SPEC/TDD for the missing `@bdd:`; mandatory-layer disable is
  rejected/ignored; no-profile unchanged), extending `test_adaptation.py` / a new
  `test_active_layers_cascade.py`. Keep `test_realizing_layers_registry.py` +
  `test_layer_registry_necessary_upstream.py` green.
- **Governance artifacts** per the ratified decision (§Governance): framework
  `VERSION` + CHANGELOG + both `FRAMEWORK_SPEC_VERSION` if bumped.

**Out:**

- **`section_toggles` structural enforcement** — CONFIRMED no-op today: optional
  (`_required: false`) sections are already excluded from STRUCT01
  (`__init__.py:376`), so a toggle changes no gate. Bundling it adds surface with no
  enforcement value.
- **`quality_loop_max_iterations`** — needs the outer review loop (H-7).
- **Changing the spec text** (`ADAPTATION_SURFACE.yaml` `cascade_rule` /
  `LAYER_REGISTRY.yaml`) — the cascade is computed by **set-subtraction from existing
  registry data**; no new registry keys or surface text are required. (If review
  finds a spec clarification IS needed, it moves the plugin-framework-bundle re-sync
  into scope — see Risks.)
- **Platform-runtime enforcement beyond the lint** — no plugin/Hermes runtime code
  *structurally enforces* `active_layers`. (Hermes DOES *consume* it — `profile.py`
  parses it and `context_builder.py:529` injects it into the creation prompt as
  advisory context; the plugin saga driver reads only `quality_loop_max_iterations`,
  `saga_driver.py:142`.) Structural enforcement is realized entirely by the vendored
  lint. Hermes's native `validation/cross_section.py` (SDD-XS-001..004) is **not** a
  demand site — it checks internal consistency, skips readiness when absent, and only
  upper-bounds cumulative tags — so it needs no cascade change (discharged).

### Verified needs NO cascade change (independent review)

The only demand site is TAG01. These were each verified NOT to fire on the normal
disabled-layer path, so they are deliberately untouched (avoiding speculative,
minimal-and-realistic scope):

- **`can_reference`** — zero usages in the canonical lint; not enforced anywhere.
- **COV02 backward-coverage** (`__init__.py:2134`) — a no-op: disabling BDD means no
  BDD elements exist to check, and EARS elements stay realized by SPEC/TDD; ADR is
  neither a key nor a value in `REALIZING_LAYERS`. (So the static constant + its
  registry-parity guard `test_realizing_layers_registry.py` stay untouched.)
- **TRACE-RES-001** (`_check_trace_resolution`, `:1605`) — only fires on an *emitted*
  `@bdd:` tag; a disabled-BDD corpus emits none, so it can only catch a stale
  hand-authored ref. Defensive-only; not implemented unless a stale-ref case surfaces.
- **REFGRAN01** (`_REFGRAN_ELEMENT_DECLARING`, `:2154`) — a *form* check on an
  already-emitted citation; layer-agnostic, never demands existence.
- **STRUCT01** / **COV01** / **COV03** / **CSC01** — keyed on sections / the
  BRD→PRD→SPEC→IPLAN chain / phase-leak, none on a disabled skippable layer.

## Governance (OPEN — needs founder / GATE-SPEC ratification before implementation)

The change edits `tools/sdd_doc_lint/` (outside `framework/`) but changes the
framework's **observable conformance behavior** (the lint now honors `active_layers`).
Two defensible positions:

- **(A) Framework MINOR + GATE-SPEC C2.** Bump `framework/VERSION` `0.36.2 → 0.37.0`,
  re-declare both platforms' `FRAMEWORK_SPEC_VERSION`, CHANGELOG. The sound rationale is
  **not** `ADAPTATION.md` §6 — that section (`:167-168`) ties a bump specifically to
  *changing the surface* (adding/renaming/removing a knob, or changing the
  mandatory/skippable split), which this change does **not** do. The rationale is the
  independent one: **a new enforced behavior under a *fixed* framework version is a
  silent behavior change for pinned consumers**, so a version signal + a GATE-SPEC
  audit record is the conservative, auditable choice.
- **(B) Tooling implementation of an existing spec (no VERSION bump).** The
  `cascade_rule` text and the surface are unchanged; we only make the reference lint
  conform to an already-ratified rule, and `ADAPTATION.md` §6 does not mandate a bump
  for a no-surface-change. GATE-SPEC's scope is `framework/` (`GATE-SPEC_FRAMEWORK.md`
  §1.1), which a `tools/sdd_doc_lint/`-only change does not touch.

**This plan leans (A)** on the silent-behavior-change rationale, but the founder
decides — and **implementation must not begin until A or B is ratified** (the
implementing PR does not unilaterally set framework-version policy). If B, the impl is
a `tools/` + re-vendor change with no framework/VERSION move.

## Approach

Keep IO (profile read) out of the pure lint logic:

1. **CLI (`__main__.py`)** — discover `.aidoc/profile.yaml` (upward from the target,
   like `find_registry`), parse `active_layers`, and compute
   `disabled_skippable = {bdd, adr} − {a.lower() for a in active_layers}` — **case-fold
   the profile input** as well as the skippable set (the documented spelling is
   uppercase `[BDD, ADR]`, but folding the input defends against a non-conforming
   lowercase profile entry that would otherwise silently under-enforce). Empty when the
   knob is absent or all-active; a request to disable a *mandatory* layer is ignored per
   the spec constraint. Add `--active-layers <CSV>` to override for tests. Pass the set
   into `lint_path`.
2. **`lint_path` (`__init__.py:2213`)** — add keyword `disabled_skippable:
   frozenset[str] = frozenset()` (lowercase tags, e.g. `{"bdd"}`). At **TAG01 only**,
   compute the effective `required_tags` as `list(registry_tags)` **minus** the
   disabled set (a fresh copy — never mutate the shared registry dict / module global,
   which would corrupt the `REALIZING_LAYERS` registry-parity guard). No
   `can_reference` view (it is never read) and no `REALIZING_LAYERS` mutation (COV02 is
   a verified no-op).
3. **No other rule-site edits.** COV02 / TRACE-RES-001 / REFGRAN01 / STRUCT01 / COV01
   are verified to not fire on the normal disabled-layer path (§Verified-no-change).
4. **Re-vendor** via `sync-vendored.sh`; run both byte-identity guards.
5. **Tests + governance artifacts** per Scope.

## Verification

- `python3 -m unittest discover -s tests/conformance` — green, including
  `test_doc_lint_vendoring.py` (byte-identity), `test_realizing_layers_registry.py`,
  `test_layer_registry_necessary_upstream.py`, and the new cascade test.
- Both platforms' `pytest` green.
- Manual: a corpus with BDD disabled (`.aidoc/profile.yaml active_layers` omitting
  BDD) lints clean where an ADR/SPEC/TDD cites no `@bdd:`; with BDD active the same
  corpus flags TAG01. A no-profile run is byte-identical to today's output.

## Risks

| Risk | Mitigation |
|------|------------|
| Governance mis-call (bump vs no-bump) | Surfaced as an explicit founder/GATE-SPEC prerequisite (§Governance); implementation gated on ratification. |
| In-place mutation of the shared registry dict / `REALIZING_LAYERS` global → corrupts `test_realizing_layers_registry.py` | The effective `required_tags` is a fresh `.copy()` minus disabled; the module global + static constant are never mutated (Approach step 2). |
| Case mismatch — `skippable` is `[BDD, ADR]` but `required_tags` are lowercase | Normalize the disabled set to lowercase before subtraction; test with a lowercase corpus. |
| Re-vendor drift (2 linter copies) | `sync-vendored.sh` + `test_doc_lint_vendoring.py` byte-identity guard; run both in Verification. |
| A spec clarification turns out necessary → plugin framework bundle also needs re-sync | If review finds `ADAPTATION_SURFACE`/`LAYER_REGISTRY` must change, add `sync-plugin-framework.sh` + `test_plugin_framework_bundle.py` to scope; currently out (cascade is computed, not stored). |

## Docs to update

- `framework/VERSION` + root `CHANGELOG.md` + both `platforms/*/FRAMEWORK_SPEC_VERSION`
  (if decision A), `plans/HERMES-BACKLOG.md` (H-16 framework-tier progress),
  `docs/PARITY.md` if the enforced-capability row changes.

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | ----- | ------ | -------- |
| 1 | the canonical lint's TAG01 reads per-layer `required_tags` and demands each as an upstream tag | `required = layers[artifact].get("required_tags", [])` | tools/sdd_doc_lint/**init**.py:600 |
| 2 | `lint_path` is the top-level entry the cascade input threads through | `def lint_path(` | tools/sdd_doc_lint/**init**.py:2213 |
| 3 | COV02 backward-coverage reads the `REALIZING_LAYERS` realizing set per layer | `realizing = REALIZING_LAYERS.get(layer, ())` | tools/sdd_doc_lint/**init**.py:2134 |
| 4 | TRACE-RES-001 upstream-tag on-disk resolution (fires only on an EMITTED tag → defensive-only for the disabled path) | `def _check_trace_resolution` | tools/sdd_doc_lint/**init**.py:1605 |
| 5 | REFGRAN01's element-declaring layer list includes BDD/ADR (a form check, assess for cascade) | `_REFGRAN_ELEMENT_DECLARING` | tools/sdd_doc_lint/**init**.py:2154 |
| 6 | the canonical lint has an upward-search registry finder to mirror for profile discovery | `def find_registry` | tools/sdd_doc_lint/**init**.py:46 |
| 7 | the CLI entry parses args and calls `lint_path` (where profile discovery is added) | `def main(argv` | tools/sdd_doc_lint/**main**.py:21 |
| 8 | the spec's `cascade_rule` specifies the required behavior (already ratified text) | `cascade_rule:` | framework/governance/ADAPTATION_SURFACE.yaml:96 |
| 9 | the skippable layers are exactly BDD + ADR | `skippable: [BDD, ADR]` | framework/governance/ADAPTATION_SURFACE.yaml:94 |
| 10 | the mandatory layers cannot be disabled | `mandatory: [BRD, PRD, EARS, SPEC, TDD, IPLAN]` | framework/governance/ADAPTATION_SURFACE.yaml:93 |
| 11 | changing the adaptation surface is tied to framework/VERSION (governance basis for decision A) | `framework/VERSION` | framework/governance/ADAPTATION.md:168 |
| 12 | downstream layers ADR/SPEC/TDD list `bdd` in required_tags (the disable-BDD blast radius) | `required_tags: [ears, bdd]` | framework/registry/LAYER_REGISTRY.yaml:84 |
| 13 | SPEC lists `bdd`+`adr` in required_tags (disable-BDD and disable-ADR both hit SPEC) | `required_tags: [ears, bdd, adr]` | framework/registry/LAYER_REGISTRY.yaml:97 |
| 14 | EARS declares `optional_downstream_slots: [BDD]` (already non-canonical forward slot) | `optional_downstream_slots` | framework/registry/LAYER_REGISTRY.yaml:64 |
| 15 | the lint is vendored byte-identically to 2 platform copies, guarded by a conformance test over 4 modules | `MODULES = ("__init__.py", "__main__.py", "trace_graph.py", "rehash.py")` | tests/conformance/platforms/test_doc_lint_vendoring.py:25 |
| 16 | the vendor sync script copies the canonical modules to the platform copies | `cp "$canonical/__init__.py" "$dest/__init__.py"` | tools/sdd_doc_lint/sync-vendored.sh:16 |
| 17 | the registry-parity guard asserts the lint's REALIZING_LAYERS constant matches the registry (must stay green) | `realizing_layers` | tests/conformance/platforms/test_realizing_layers_registry.py:1 |
| 18 | optional sections are already excluded from STRUCT01 (section_toggles enforcement is a no-op → out of scope) | `_required` | tools/sdd_doc_lint/**init**.py:376 |
| 19 | GATE-SPEC governs framework/ spec changes (the gate decision A would run through) | `GATE-SPEC` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:1 |
| 20 | the plugin saga driver reads `quality_loop_max_iterations` from the profile; it does not *enforce* active_layers (no plugin-side structural enforcement to add) | `quality_loop_max_iterations` | platforms/claude-code-plugin/tools/saga_driver.py:142 |
| 21 | current framework spec version (the bump baseline for decision A) | `0.36.2` | framework/VERSION:1 |
| 22 | `can_reference` is NOT enforced anywhere in the canonical lint — TAG01 (`required_tags`) is the sole demand site (so the cascade is TAG01-only) | `can_reference:` | framework/registry/LAYER_REGISTRY.yaml:85 |
| 23 | ADAPTATION.md §6 ties a VERSION bump to *changing the surface* (not to implementing existing enforcement) — the F1 governance correction | `Changing the surface (adding, renaming, or` | framework/governance/ADAPTATION.md:166 |
| 24 | Hermes DOES consume `active_layers` (injects it as prompt context) — so the correct out-of-scope claim is "no runtime *enforces* it", not "consumes" (F2) | `if profile.active_layers is not None:` | platforms/hermes/src/mcp_server/prompts/context_builder.py:529 |
| 25 | Hermes `cross_section` readiness check (SDD-XS-002) is not a demand site → discharged | `def _check_readiness_score_plausibility` | platforms/hermes/src/mcp_server/validation/cross_section.py:137 |

## Review log

### Pass 1 — 2026-07-10 — self-review (draft)

- Scoped to `active_layers` cascade in the **canonical lint** only, after the surface
  map confirmed: `section_toggles` enforcement is a no-op (optional sections already
  excluded from STRUCT01), `quality_loop` is H-7, and the cascade is computable by
  set-subtraction from existing registry data (no spec-text/registry-key change → the
  plugin framework-bundle re-sync stays out).
- Surfaced the real governance fork (framework-VERSION bump vs. tooling-only) as an
  explicit founder/GATE-SPEC **prerequisite**, rather than letting the impl PR decide.
- Kept IO (profile discovery) out of the pure lint logic; the cascade is a
  runtime-computed *effective view*, so the static `REALIZING_LAYERS` constant (and
  its registry-parity guard) is untouched.
- Open questions for the independent pass: (a) is TRACE-RES-001 the only place a
  dangling `@<disabled>:` citation is flagged, or do other checks (COV/REFGRAN/
  can_reference enforcement) also need the skip? (b) does any check enforce
  `can_reference` (vs only `required_tags`), i.e. is there a second demand site beyond
  TAG01? (c) is REFGRAN01 genuinely form-only (no cascade change needed)? (d) is the
  governance recommendation (A) correct, or is there precedent for tooling-behavior
  changes shipping without a framework bump?

### Pass 2 — 2026-07-10 — independent (fresh-context subagent) + fold

Independent reviewer verified **all 21 (then) ledger rows** against source and
confirmed the core mechanics sound (TAG01 + a runtime effective-view keeps every named
conformance test green; the canonical-lint-only scoping is correct). It **shrank and
corrected** the plan via findings folded here:

- **Pass-1 (a)/(b) resolved → the cascade is TAG01-ONLY.** `can_reference` has **zero
  usages** in the lint; TAG01 (`:600`) is the sole *demand* site. **Folded:** Scope /
  Approach now change only TAG01 (dropped the `can_reference` effective view — dead
  work); added ledger row 22.
- **F3/F4 — COV02 and TRACE-RES-001 are no-ops/defensive-only** on the normal
  disabled-layer path (COV02: no BDD elements exist to check, EARS still realized by
  SPEC/TDD; TRACE-RES-001 fires only on an *emitted* tag). **Folded:** both dropped from
  the implementation into a new **§Verified-no-change** list (with COV01/COV03/CSC01/
  STRUCT01/REFGRAN01), per minimal-and-realistic.
- **(c) REFGRAN01 confirmed form-only** — no change. In §Verified-no-change.
- **(d)/F1 — governance rationale corrected.** `ADAPTATION.md` §6 ties a bump to
  *changing the surface*, which this does NOT do → §6 actually supports **B**. **Folded:**
  the §Governance A-rationale re-based on the *silent-behavior-change* argument only;
  ledger row 23 added; the plan now "leans A" rather than "recommends A on §6".
- **F2 — "no runtime consumes active_layers" was false** (Hermes injects it as prompt
  context, `context_builder.py:529`). **Folded:** Scope §Out reworded to "no runtime
  *structurally enforces* it"; ledger rows 20/24 corrected.
- **F5 — `cross_section.py` discharged** (SDD-XS-001..004 are not demand sites).
  **Folded:** explicit discharge line + ledger row 25.
- **Impl caveats folded:** effective `required_tags` must be a `.copy()` (never mutate
  the module global) + case-normalize the disabled set to lowercase; both now in
  Approach step 2 + Risks. Citation nits fixed (rows 4→:1605, 20→:142, §Gov →:166-168).

**Open for Pass 3:** does the TAG01-only + §Verified-no-change reframing hold with no
new inconsistency, and are the added rows (22-25) accurate? (Governance A-vs-B stays a
founder decision, not a plan-review item.)

### Pass 3 — 2026-07-10 — independent confirmation (fresh-context subagent)

A second fresh-context reviewer confirmed the Pass-2 fold is **clean and complete with
zero load-bearing findings**, verified from source:

- **TAG01-only thesis holds** — `grep` confirms `can_reference` has zero usages in the
  lint; `required_tags` is read only at `:600` (finding at `:607`); COV02
  (`_check_backward_coverage`) provably produces no spurious finding when BDD/ADR is
  disabled (BDD has no `element_host` entries to check; EARS stays realized by the
  mandatory SPEC/TDD via the union `_element_realizing_citers`; ADR is neither key nor
  value in `REALIZING_LAYERS`). The threading path `lint_path → lint_file → lint_text`
  (TAG01 in `lint_text`) reaches `:600`.
- **Rows 22-25 + fixed rows 4/20 all resolve at their cited symbols; F1/F2/F5 corrections
  are accurate at source** (ADAPTATION.md §6 ties a bump to a *surface* change only;
  Hermes injects `active_layers` at `context_builder.py:529` + `profile.py:15` names the
  deferral; `cross_section` SDD-XS-001/002/004 are not demand sites).
- **Internally consistent** — §Verified-no-change, Scope §In (TAG01-only), and Approach
  agree; the `.copy()`-not-mutate + case-normalization caveats appear consistently; the
  conformance-test bullet asserting "no COV02/TRACE-RES on the missing `@bdd:`" is a
  *regression assertion* of the no-op claim, not a scope contradiction.

Folded the one substantive nicety (case-fold the `active_layers` *input*, not just the
skippable set — Approach step 1). Two cosmetic citation nits (row 19 GATE-SPEC anchor;
§6 `:166`/`:167-168`) left — the symbols resolve and the claims are correct.

**Result:** ready. Claim ledger has zero UNVERIFIED rows and the gate passes; three
review passes (two independent, fresh-context) drove the load-bearing count to zero.
The one remaining gate is **founder ratification of the governance decision (A vs B)**,
which the plan holds as an explicit prerequisite to implementation — not a plan-review
blocker. Sized to a single TAG01 change + re-vendor + tests (minimal-and-realistic).
