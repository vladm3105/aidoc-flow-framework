# D54-F13 Phase-Leak Plan — COV03: advisory when a deferred (`Future`-banded) FR is realized downstream

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | D54-F13 (phase-leak leg only; the missing-downstream leg shipped as COV01) |
| Type           | feat (new advisory lint rule)               |
| Status         | READY — 2026-07-06 (Pass 2 independent fresh-context; Pass 3 self) |
| Depends on     | none (COV01/COV02 coverage engine already shipped) |
| Feeds          | authors get an early signal that a next-cycle item is being pulled into the current build |
| Version impact | framework spec **MINOR** (`0.33.1 → 0.34.0`) — a new normative lint rule documented in `framework/governance/`. Both `FRAMEWORK_SPEC_VERSION` pointers auto-re-match; plugin + Hermes **product** versions unchanged. Lint code lives in `tools/` (vendored), so the `framework/**` change that triggers GATE-SPEC is the TRACEABILITY.md doc + the BRD band note. |

## Objective

D54-F13's **missing-downstream** leg shipped as `COV01` (an in-scope FR with no
SPEC/IPLAN blocks). Its **phase-leak** leg — "an out-of-phase item leaked into an
in-phase plan" — is the one genuinely-open piece (deferred in the COV01 docstring as
"DD-6 row 4").

Grounding showed the framework **already carries both phase axes**, so no new tag is
warranted (MINIMAL-ADVISORY scope, ratified 2026-07-06):

- **Within-cycle phase = the FR band.** `priority_definitions` defines `Future` = "Next
  MVP cycle enhancements" — the machine-readable next-phase signal. `covered_state_of`
  already classifies a `Future` band as `CoveredState.DEFERRED`, and COV01 **escapes** it
  (`!= AUTHORED → continue`).
- **Cross-cycle phase = the BRD-00 roadmap `Cycle` column.** Later-cycle BRDs are
  `Planned`/`Sketch` = **trace-inert** (not authored, not in the `@`-tag graph), so an IPLAN
  structurally cannot realize a future-cycle element — that leak is already prevented.

The only genuinely-missing piece is the **inverse of COV01's escape skip**: COV01 blocks an
`AUTHORED` FR that is *not* realized; nothing flags a `DEFERRED` FR that *is* realized. That
FR is a possible phase-leak — something marked next-cycle is being pulled into the current
build. This plan adds **`COV03`**, an **advisory** (never blocks) that surfaces exactly that,
reusing the existing band + coverage graph. No new tag, field, artifact, or template
structure.

## Scope

**In:**

- **New rule `COV03` in the canonical linter** (`tools/sdd_doc_lint/__init__.py`): a
  `_check_phase_leak(corpus, mode)` that, for each BRD FR whose `covered_state_of` is
  `CoveredState.DEFERRED` (a `Future` band, no `realized_by:`), checks whether the FR
  element is picked up by its realizing layer (`_element_realizing_citers(graph,
  fr.elem_id, REALIZING_LAYERS["BRD"])`, the same element-level helper COV01 uses). If it
  is, emit `Finding(..., "COV03", …, severity="warning")`. **Advisory in both `build` and
  `gate-code`** (never an error — scope pull-forward is legitimate; the fix is usually to
  re-band the FR `P1`/`P2` or confirm the deferral). Dispatched inside the existing
  `if not skip_coverage:` block (so `--skip-coverage-gate` suppresses it, consistent with
  the coverage family) alongside COV01/COV02. Skips `reuse: referenced` docs (like COV01).
- **Propagate to the vendored mirrors** via `tools/sdd_doc_lint/sync-vendored.sh` (both
  `platforms/*/sdd_doc_lint/` are byte-identical mirrors; the drift guard
  `tests/conformance/platforms/test_doc_lint_vendoring.py` enforces equality).
- **Document COV03 as normative** in `framework/governance/TRACEABILITY.md`, beside
  COV01/COV02 (this is the `framework/**` change that trips GATE-SPEC), plus a one-line note
  in the BRD `_authored_form` band guidance (`BRD-TEMPLATE.yaml`) that a `Future` FR realized
  downstream draws a COV03 advisory.
- **Test** in `tests/conformance/test_coverage_engine.py`: a `DEFERRED` FR that is realized
  downstream → `[("COV03", "warning")]`; a `DEFERRED` FR with no realizing citer → `[]`; a
  `realized_by:` FR is **never** COV03 (it's a positive coverage claim, not a leak); an
  `AUTHORED` FR is COV01's domain, never COV03.
- Bump `framework/VERSION` `0.33.1 → 0.34.0` (staged) + `CHANGELOG.md` entry (GATE-SPEC
  E005+E008) + re-vendor the plugin framework bundle (`sync-plugin-framework.sh`) so the
  TRACEABILITY.md + BRD-template doc changes propagate. `plans/DECISIONS.md` (D-0055),
  `plans/FRAMEWORK-TODO.md` (close D54-F13), `plans/HANDOFF.md`.

**Out of scope (deferred — with rationale):**

- **A first-class phase tag on capability elements** — redundant with the existing band
  (`P1`/`P2`/`Future`) + the BRD-00 `Cycle` roadmap; adding one would duplicate a
  single-sourced signal. (This is the over-engineering the MINIMAL-ADVISORY decision
  rejected.)
- **A cross-cycle IPLAN→Cycle binding + a *blocking* out-of-phase gate** — cross-cycle
  leaks are already structurally prevented (future-cycle BRDs are trace-inert); a blocking
  gate would fight legitimate scope pull-forward. Advisory is the right severity.
- **Deep IPLAN-level phase-leak (vs. element-level PRD realization)** — the element-level
  realizing-citer check catches the leak at its earliest downstream point (mirrors COV01);
  a deeper SPEC/IPLAN walk adds noise for no earlier catch. Revive only if the PRD-level
  signal proves too coarse in practice.

## Approach / Design (D-0055)

**COV03 is the exact inverse of COV01's escape.** COV01 iterates BRD FRs and, for each
`AUTHORED` FR, blocks if it does NOT reach a realizing layer; it `continue`s (escapes) on
any non-`AUTHORED` state. COV03 iterates the same FRs and, for each `DEFERRED` FR, warns if
it DOES reach its realizing layer. Same corpus, same `build_edge_graph`, same
`_element_realizing_citers` helper, same `reuse: referenced` skip — a ~25-line sibling
function.

```
def _check_phase_leak(corpus, mode="build"):   # mode kept only for sibling-signature symmetry; severity is always warning
  graph = build_edge_graph(corpus)
  for each BRD doc (not reuse:referenced):
    for fr in scan_fr_elements(text):
      if covered_state_of(fr) != CoveredState.DEFERRED:   # only Future-banded, no realized_by
          continue
      citers = _element_realizing_citers(graph, fr.elem_id, REALIZING_LAYERS.get("BRD", ()))
      if citers:
          emit COV03 warning: "deferred FR '<id>' (band Future) is realized downstream by
          <citers> — a possible phase-leak; re-band it P1/P2 for the current cycle or
          confirm the deferral is intentional"
```

**Do NOT copy COV01's `{SPEC, IPLAN} ⊆ layers` early-return guard** (Pass-2 finding).
`_check_forward_coverage` returns `[]` when the corpus has no SPEC or no IPLAN doc (it needs
the full chain to assert reach); COV03 needs only **PRD** realization, so it must run on a
BRD+PRD-only corpus — precisely the early-stage cascade where a phase-leak is most likely.
COV03 gates on the element-level realizing-citer alone; it has no such precondition. Use
`REALIZING_LAYERS.get("BRD", ())` (COV01's defensive form), not `[...]`.

**Why `DEFERRED` only, not `REALIZED_BY`.** `covered_state_of` returns `REALIZED_BY` when
the band carries `realized_by: <LAYER>` — a *positive* coverage declaration, not a leak.
COV03 keys strictly on `CoveredState.DEFERRED` (a bare `Future` band), so a `realized_by:`
FR is never flagged.

**Advisory, both modes.** Unlike COV01 (which escalates to error at `gate-code`), COV03 is
`warning` in both `build` and `gate-code`: building a deferred item early is not a
correctness defect (scope changes), so it must never block a gate — it prompts the author to
reconcile the band. This matches the REUSE01-style advisory precedent.

**Versioning.** A new normative lint rule is an additive spec feature → **MINOR** (matching
the COV01 `0.24.0` / COV02 `0.25.0` / REFGRAN01 `0.27.0` precedent — each a MINOR bump for a
new rule), so `0.33.1 → 0.34.0`. The lint code is in `tools/` (not `framework/`), so the
GATE-SPEC-triggering `framework/**` change is the TRACEABILITY.md normative doc + the BRD
band note.

**Backward-compatibility.** Purely additive + advisory: no existing finding changes, no gate
newly blocks, every current corpus stays green (a new warning is not a failure). The only
behavior change is a new advisory line when a `Future` FR is realized downstream.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `tools/sdd_doc_lint/__init__.py` | add `_check_phase_leak` (COV03); dispatch in the `if not skip_coverage:` block |
| `platforms/hermes/sdd_doc_lint/__init__.py`, `platforms/claude-code-plugin/sdd_doc_lint/__init__.py` | regenerated by `tools/sdd_doc_lint/sync-vendored.sh` (byte-identical; not hand-edited) |
| `framework/governance/TRACEABILITY.md` | document COV03 beside COV01/COV02 (the `framework/**` GATE-SPEC change) |
| `framework/layers/01_BRD/BRD-TEMPLATE.yaml` | one-line note in the `_authored_form` band guidance re: COV03 |
| `tests/conformance/test_coverage_engine.py` | COV03 cases (realized-deferred → warning; unrealized-deferred → none; realized_by → none) |
| `framework/VERSION` (→ `0.34.0`) + `CHANGELOG.md` | version + entry (GATE-SPEC E005+E008) |
| `platforms/claude-code-plugin/framework/**` | re-vendored by `sync-plugin-framework.sh` (TRACEABILITY.md + BRD template) |
| `plans/DECISIONS.md` (D-0055) / `plans/FRAMEWORK-TODO.md` (close D54-F13) / `plans/HANDOFF.md` | docs |

## Implementation sequence

### Task 1: COV03 in the canonical linter

- Add `_check_phase_leak(corpus, mode="build")` next to `_check_forward_coverage`; dispatch
  `findings.extend(_check_phase_leak(corpus, mode))` in the `if not skip_coverage:` block.
- Run `tools/sdd_doc_lint/sync-vendored.sh`; verify both mirrors byte-identical.

### Task 2: Tests

- Add the COV03 cases to `tests/conformance/test_coverage_engine.py` (reuse the existing
  fixture-corpus builders).

### Task 3: Framework docs (the GATE-SPEC change)

- `TRACEABILITY.md` COV03 paragraph; `BRD-TEMPLATE.yaml` band-guidance one-liner.

### Task 4: Version + propagation + docs of record

- `framework/VERSION → 0.34.0` (staged); `sync-plugin-framework.sh` re-vendor;
  `CHANGELOG.md`; D-0055; close D54-F13; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | unit: a `Future`-banded FR realized by a PRD → `_check_phase_leak` returns `[("COV03","warning")]` | present | COV03 core |
| V2 | unit: a `Future`-banded FR with NO realizing citer → `[]`; a `realized_by:` FR → `[]`; an `AUTHORED` FR → `[]` (no COV03) | correct exclusions | Design (DEFERRED-only) |
| V3 | COV03 is `warning` in BOTH `build` and `gate-code` (never `error`) | non-blocking | advisory severity |
| V4 | `python -m pytest tests/conformance -q` | green (incl. coverage-engine + vendoring drift guard) | propagation |
| V5 | `diff` canonical vs both `platforms/*/sdd_doc_lint/__init__.py` | byte-identical (sync-vendored ran) | Task 1 |
| V6 | run the linter over `examples/*/docs/` | **zero unexpected COV03** (the example corpus has no realized-yet-deferred FR); if any appear, they are real leaks — report, don't suppress | corpus cross-check (mandatory) |
| V7 | `python tests/chg/spec_gate.py` | OK — VERSION + CHANGELOG present (E005+E008) | Task 4 |
| V8 | `grep -rn '0.33.1' framework/VERSION platforms/*/FRAMEWORK_SPEC_VERSION` | none (all moved to 0.34.0) | version propagation |

## Docs to update

- [ ] `CHANGELOG.md` — MINOR `0.33.1 → 0.34.0`, COV03
- [ ] `plans/DECISIONS.md` — D-0055 (COV03 advisory; minimal scope; no new phase tag)
- [ ] `plans/FRAMEWORK-TODO.md` — close `D54-F13`
- [ ] `plans/HANDOFF.md` — progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | COV03 is noisy (fires on legitimate deferred-but-referenced FRs) | med | element-level realizing-citer only (a PRD `@brd:` cite = realization in the necessary-upstream model, not a mere mention); advisory (never blocks); V6 corpus cross-check confirms zero unexpected findings |
| R2 | Editing a vendored mirror instead of canonical → drift-guard CI fail | low | edit `tools/sdd_doc_lint/__init__.py` only; Task 1 runs `sync-vendored.sh`; V5 + V4 (drift guard) verify |
| R3 | MINOR vs PATCH mis-call | low | new normative rule = additive feature = MINOR, per COV01/COV02/REFGRAN01 precedent |
| R4 | `framework/VERSION` unstaged → hook skipped → stale pointers + GATE-SPEC fail | low | Task 4 stages VERSION; V7 (gate) + V8 (no stale 0.33.1) |
| R5 | Advisory over-realization contradicts REALIZED_BY semantics | low | COV03 keys strictly on `CoveredState.DEFERRED`; `realized_by:` → `REALIZED_BY`, never flagged (V2) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `Future` band = "Next MVP cycle" (the next-phase signal) | `Future: "Next MVP cycle enhancements based on user feedback"` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:538 |
| 2  | The band is the machine-readable phase signal | `machine-readable phase signal` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:561 |
| 3  | `CoveredState.DEFERRED` is the classification COV03 keys on | `DEFERRED = "deferred"` | tools/sdd_doc_lint/**init**.py:813 |
| 4  | `covered_state_of` maps a `Future` band → `DEFERRED` | `def covered_state_of` | tools/sdd_doc_lint/**init**.py:842 |
| 5  | COV01 escapes non-AUTHORED FRs (COV03 is the inverse) | `if covered_state_of(fr) != CoveredState.AUTHORED:` | tools/sdd_doc_lint/**init**.py:1626 |
| 6  | `_element_realizing_citers` — the element-level realizing-citer helper COV03 reuses | `def _element_realizing_citers` | tools/sdd_doc_lint/**init**.py:1691 |
| 7  | `REALIZING_LAYERS` — the BRD→realizing-layer map | `REALIZING_LAYERS: dict[str, tuple[str, ...]] =` | tools/sdd_doc_lint/**init**.py:1684 |
| 8  | Coverage checks are dispatched behind `skip_coverage` (COV03 joins here) | `if not skip_coverage:` | tools/sdd_doc_lint/**init**.py:2011 |
| 9  | Existing forward gate to add COV03 beside | `_check_forward_coverage(corpus, mode)` | tools/sdd_doc_lint/**init**.py:2012 |
| 10 | Canonical linter source (edit here; mirrors are vendored) | `CANONICAL SOURCE: tools/sdd_doc_lint/__init__.py` | platforms/hermes/sdd_doc_lint/**init**.py:3 |
| 11 | The vendor sync script copies canonical → each mirror | `cp "$canonical/__init__.py" "$dest/__init__.py"` | tools/sdd_doc_lint/sync-vendored.sh:16 |
| 12 | The vendoring drift guard (CI enforces byte-identity) | `class DocLintVendoring` | tests/conformance/platforms/test_doc_lint_vendoring.py:27 |
| 13 | Coverage-engine test structure (COV01 finding-tuple assertion pattern) | `_check_forward_coverage` | tests/conformance/test_coverage_engine.py:24 |
| 14 | COV01/COV02 are documented as normative in TRACEABILITY.md (append COV03) | `COV01` | framework/governance/TRACEABILITY.md:98 |
| 15 | Current framework spec version 0.33.1 (MINOR target 0.34.0) | `0.33.1` | framework/VERSION:1 |
| 16 | GATE-SPEC-E005 requires VERSION bump on any framework/** change | `GATE-SPEC-E005` | tests/chg/spec_gate.py:86 |
| 17 | GATE-SPEC-E008 requires CHANGELOG in the same diff | `CHANGELOG.md` | tests/chg/spec_gate.py:87 |

## Review log

### Pass 1 — 2026-07-06 — self-review

Draft after grounding the phase model. Key decision (ratified MINIMAL-ADVISORY): the "first-
class phase tag" the TODO proposed is redundant — `Future` band = within-cycle next-phase,
BRD-00 `Cycle` roadmap + trace-inert future BRDs = cross-cycle, both already single-sourced.
COV03 is the exact inverse of COV01's `!= AUTHORED` escape, reusing the same graph + helper;
advisory (never blocks) because scope pull-forward is legitimate. Canonical edit in
`tools/`, vendored to both mirrors; the `framework/**` GATE-SPEC change is the TRACEABILITY.md
doc. Pending: independent Pass 2.

### Pass 2 — 2026-07-06 — independent (fresh-context adversarial)

A fresh-context reviewer verified all 17 citations exact (symbol + line) and confirmed the
design premise against source: (a) a bare `Future` band → `DEFERRED`; (b) `realized_by:` →
`REALIZED_BY` (precedence over band), so COV03 never flags it; (c) COV01 `continue`s on
non-AUTHORED, and `CoveredState.DEFERRED` has **no other consumer** in the linter → COV03 is
genuinely non-redundant. Helper reuse matches COV01 exactly (`_element_realizing_citers(graph,
fr.elem_id, REALIZING_LAYERS.get("BRD", ()))` → `("PRD",)`). GATE-SPEC reasoning correct
(`spec_gate.py` keys on `framework/`; `tools/` is outside it; the TRACEABILITY.md +
`framework/VERSION` change trips E005/E008; `sync-version-refs.sh` auto-re-matches the
`FRAMEWORK_SPEC_VERSION` pointers). MINOR consistent with COV01/COV02/REFGRAN01. **One MINOR
folded:** COV03 must NOT clone COV01's `{SPEC,IPLAN} ⊆ layers` early-return — it gates on PRD
realization alone and must run on BRD+PRD-only corpora (where phase-leaks are likeliest);
added an explicit "do not copy the guard" note + reflected it in the pseudocode. Two NITs
folded (dead `mode` param commented for sibling-symmetry; `.get("BRD", ())` defensive form).
Row-13 line-off is harmless (symbol authoritative). 0 load-bearing.

### Pass 3 — 2026-07-06 — self-review (re-validate the Pass-2 fold)

Re-checked the fold: the pseudocode now shows `_check_phase_leak` with the `.get` form + the
mode-symmetry comment, and the "do NOT copy the SPEC/IPLAN guard" note makes the pre-SPEC-corpus
requirement explicit (so V6's example-corpus run + V1/V2 unit tests exercise the BRD+PRD path
correctly). Scope unchanged (no new tag; advisory only). Internal consistency: version-impact,
Scope, File-structure, V1-V8, and the ledger all agree; D-0055 is the next free decision number
(D-0054 = IPLAN-LANG-001). No new gaps.

**Result:** ready
