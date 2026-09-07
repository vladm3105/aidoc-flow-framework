# IDCOORD-SECOND-HASH-IMPL Plan — one hash implementation in the repo

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | IDCOORD-SECOND-HASH-IMPL                                     |
| Type           | test-harness                                                 |
| Status         | ✅ SHIPPED — 2026-07-26                                      |
| Depends on     | D-0062 (PROVISIONAL-IDS-002 Phase 1), D-0067 / GD-09         |
| Closes         | [#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351) |
| Version impact | **None.** No `framework/` change, no platform change, no `VERSION` bump — `tests/` only |
| Gate           | Not GATE-SPEC (nothing under `framework/` is touched)        |

## Objective

`tests/acceptance/_id_coordinator.py:17-19` is a **second, independent
implementation** of the element-ID hash that skips the normalization transform
D-0062 made normative. Its smoke test asserts determinism and shape but never
parity with the canonical `compute_element_hash()`, so a wrong algorithm is
indistinguishable from a right one.

This plan makes `_id_coordinator` **delegate** to the canonical implementation,
adds the parity test that makes silent re-divergence impossible, and resolves two
further defects the same investigation surfaced.

## The issue's premise is wrong, and correcting it is the plan's main finding

**#351 states that `element_id()` feeds `write_registry()`, "so committed fixture
IDs derive from the wrong algorithm," and that fixing it "will churn committed
goldens" — which is why it was filed separately from
ELEMENT-ID-LAYER-CONTRACT-001 rather than folded in.**

**That is false, and it was verified false, not assumed:**

| Claim in #351 | Reality |
| --- | --- |
| `element_id()` feeds `write_registry()` | `write_registry()` has **zero callers**. `grep -rn "write_registry\|extract_elements" --include=*.py --include=*.sh --include=*.yml` outside the module itself returns nothing |
| committed fixture IDs derive from it | `tests/acceptance/fixtures/fullpath/ID_REGISTRY.yaml` is **`{}` — 3 bytes**, unchanged since its creation commit `f0d08f54` |
| goldens carry IDs it minted | `grep -o "PRD\.01\.[a-z_]*\.[0-9a-f]\{4\}"` over `fullpath/golden_chain/02_PRD/PRD-01_golden.md` returns **nothing**. `extract_elements()` *computes* IDs from golden content at call time; it does not read stored ones, and nothing persists what it computes |
| fixing it churns goldens | **Zero churn.** No committed artifact carries an ID produced by this code |

`plans/PLUGIN-TEST-SUITE-REVIEW.md:32` already recorded half of this as finding
**F2** — *"`_id_coordinator.py` committed but never imported. Empty
`ID_REGISTRY.yaml`."* — and its suggested disposition was *"wire it into a real
closure test, or remove both files."* That finding was never actioned and #351
was filed without reference to it.

**Consequence for scope.** The reason this was deferred out of
ELEMENT-ID-LAYER-CONTRACT-001 (golden-churn risk in a documentation plan) does
not exist. The work is a small, self-contained, zero-risk test-harness change.
The founder should know the deferral rationale has evaporated; the plan is
written either way, since the fix still needs to be specified before it is made.

## Scope

**In:**

- **A — delegate the hash.** `element_hash()` calls `compute_element_hash()` from
  the canonical `sdd_doc_lint` module instead of re-deriving it, so there is one
  algorithm in the repo.
- **B — the parity test.** A test asserting
  `element_hash(...) == compute_element_hash(...)[:4]` over a table of inputs
  chosen to exercise every step of the transform (uppercase, punctuation,
  non-NFC composition, collapsed whitespace, >100-char truncation). Without it,
  A can silently regress exactly as it silently diverged.
- **C — the string `section_id`.** `element_id()` accepts a string
  (`"project_scope"`) and emits `BRD.01.project_scope.<hash>`, which the
  registry pattern `^[A-Z]+\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}$`
  (`framework/registry/LAYER_REGISTRY.yaml:216`) rejects and `ELEM_FORM` would
  not accept. See **D3** — this is the one design decision in the plan.
- **D — the multi-document YAML crash.** `extract_elements()` calls
  `yaml.safe_load()`, which raises `ComposerError` on any golden containing a
  second `---`. **Three committed goldens do**
  (`fullpath/golden_chain/{06_SPEC,07_TDD,08_IPLAN}/*-01_golden.yaml`). No test
  reaches them, so the crash is latent — see **D4**.
- **E — the AS11 docstring.** `tools/sdd_doc_lint/__init__.py:1131-1132`
  describes the element hash as a prefix of
  `{doc_id}:{section_id}:{title}:{description}` with no mention of the
  transform. Zero behavioural effect (the implementation 200 lines above is
  correct) but it is the same wrong statement in the same file. Folded in per
  #351's "Secondary" section. **Touching it re-vendors the two byte-identical
  copies** under `platforms/*/sdd_doc_lint/`, so the bundle sync must run.

**Out of scope:**

- **Deleting `_id_coordinator.py` outright.** It is a live option — PLUGIN-TEST-SUITE-REVIEW
  F2 offers it as the alternative — but it is a *product* decision about whether
  cross-layer ID-closure testing is still wanted, not a defect fix. See **D1**.
- **Wiring `write_registry()` into a real closure test.** The other half of F2.
  It needs the goldens to carry reproducible upstream IDs, which they do not
  (the smoke test's own docstring says downstream goldens "reference placeholder
  upstream IDs that don't reproduce the upstream's actual element hashes"). That
  is a fixture-authoring project, not this.
- **The 19 platform authoring surfaces** — #342.
- **Any `framework/` change.** This plan touches `tests/` and, for E, the
  vendored linter docstring. Nothing under `framework/`, so no GATE-SPEC and no
  `VERSION` bump.

## Approach / Design

### D1 — Fix it rather than delete it, but say why the question is open

F2 offered "wire it into a real closure test, **or remove both files**." Removal
is defensible: the module has no consumer, its registry is empty, and its smoke
test only proves the module does not crash on inputs no product code sends it.

**Fix, not delete, for this plan** — on the narrow ground that deleting it is a
decision about the *test strategy* (does the suite still want cross-layer ID
closure?) which nobody has taken, while a second wrong implementation of a
normative algorithm is a defect regardless of that decision. A defect fix should
not smuggle in a strategy change.

**But the plan states the cost of that choice plainly:** after this work the repo
still carries a module with no product consumer, now correct. If the founder
decides closure testing is not coming, deleting `_id_coordinator.py`,
`test_id_coordinator.py` and `ID_REGISTRY.yaml` supersedes this entire plan and
is strictly cheaper. **That question should be answered before the work starts,
not after.**

### D2 — Delegate, do not re-implement

`element_hash()` becomes a thin wrapper:

```python
from sdd_doc_lint import compute_element_hash

def element_hash(doc_id: str, section_id: str, title: str, description: str) -> str:
    return compute_element_hash(doc_id, section_id, title, description)[:4]
```

The module already imports from the canonical module (`_normalise_heading`,
line 30), so it is not isolated by design — it simply never adopted
`compute_element_hash`. The `[:4]` slice is retained rather than pushed into the
canonical function because `compute_element_hash()` owns the 4→8 collision
extension, and a fixture helper has no collision context to make that decision in.

**The import must move to module scope.** Today the `sys.path` insert for
`tools/` happens *inside* `extract_elements()` (line 29), so a caller invoking
`element_hash()` alone never runs it. A module-level import needs the path insert
at module level too — otherwise A introduces an `ImportError` on the exact call
path the parity test exercises.

### D3 — `section_id`: widen the format, do not silently break callers

`element_id()` takes a string `section_id` and its own test asserts the result
matches `^BRD\.01\.project_scope\.[0-9a-f]{4}$`
(`test_id_coordinator.py:29-31`) — i.e. the string form is *deliberate*, not
accidental. But `LAYER_REGISTRY.yaml:216` requires two-digit numerics, so no ID
this function produces could ever be valid.

Three options:

| # | Option | Assessment |
| --- | --- | --- |
| a | Require a 2-digit numeric `section_id`; update the test | Correct against the registry. Breaks `extract_elements()`, which derives `section_id` from a **normalised heading string** (`_normalise_heading`, line 45) and has no numeric to supply |
| b | Map heading → section number inside `extract_elements()` | Correct and complete, but requires a heading→ordinal mapping per layer that does not exist anywhere in the repo. That is a new contract — the same overreach GD-09 declined for TDD field extraction |
| c | Leave the string form, and **document** that these IDs are fixture-local identifiers, not spec-conformant element IDs | Honest, zero-risk, and matches what the module actually is |

**(c), with a caveat comment and an assertion.** The module is a fixture helper
with no product consumer; pretending its output is registry-valid would be worse
than saying it is not. The docstring states the limitation, and the parity test
covers the **hash**, which is the part that must match the spec. A follow-up TODO
entry records that (b) is the real fix if closure testing is ever wired up.

Choosing (a) or (b) here would be scope creep into the fixture-authoring project
that D1 already put out of scope.

### D4 — The multi-document YAML crash is in scope because A makes it reachable

`extract_elements()` uses `yaml.safe_load()`, which raises on a second `---`.
Verified: it raises `ComposerError` on
`fullpath/golden_chain/06_SPEC/SPEC-01_golden.yaml`.

It is latent today because the only test that calls `extract_elements()` over
goldens uses `fixtures_for(idx, "valid")` → `layer_NN_<name>/valid/`
(`_harness.py:17-21`), which never reaches `fullpath/`. Six `fullpath` YAML
goldens exist; the three under `golden_chain/` carry two `---` markers each and
crash.

Fix: `yaml.safe_load_all()`, merging the documents, so the helper handles the
front-matter-plus-body shape the repo's own goldens use. **Include a regression
test that calls `extract_elements()` over the `fullpath/` goldens** — otherwise
the fix is unverified and the gap that hid it stays open.

### D5 — Version impact: none

Nothing under `framework/` changes, so GATE-SPEC does not apply and
`framework/VERSION` does not move. E edits `tools/sdd_doc_lint/__init__.py`, a
repo-root tool, and requires `tools/sync-plugin-framework.sh` to re-vendor the
two byte-identical platform copies — a bundle refresh, not a platform product
change, so neither platform `VERSION` moves either (the D5 precedent in
ELEMENT-ID-LAYER-CONTRACT-001).

## File structure

### Modified

| File | Change |
| --- | --- |
| `tests/acceptance/_id_coordinator.py` | A (delegate + module-scope import), C (docstring caveat), D (`safe_load_all`) |
| `tests/acceptance/deterministic/test_id_coordinator.py` | B (parity table), D (fullpath regression) |
| `tools/sdd_doc_lint/__init__.py` | E — AS11 docstring only, no behaviour |
| `platforms/{hermes,claude-code-plugin}/sdd_doc_lint/__init__.py` | E — re-vendored by the sync script, never hand-edited |
| `plans/FRAMEWORK-TODO.md` | `IDCOORD-SECOND-HASH-IMPL` → Closed; one new entry for the deferred D3 option (b) |
| `CHANGELOG.md` | `[Unreleased]` entry |

No new files.

## Implementation sequence

1. **Answer D1's open question first** — if closure testing is being dropped,
   delete the three files and close #351 as superseded. Everything below assumes
   the answer is "keep."
2. **Test first (B).** Write the parity test against the *current* implementation
   and confirm it is **red**, with inputs covering each transform step. A parity
   test that passes before the fix would mean the transform never applies to the
   chosen inputs, which would make it worthless.
3. **A** — module-scope `sys.path` insert + `compute_element_hash` delegation.
   Parity test → green.
4. **D** — `safe_load_all`; add the `fullpath/` regression test; confirm it is red
   before the fix and green after.
5. **C** — docstring caveat naming the registry pattern the string form does not
   satisfy, plus the deferred-option TODO entry.
6. **E** — AS11 docstring, then `bash tools/sync-plugin-framework.sh`; verify the
   three copies are byte-identical again (`md5sum`).
7. **Verify** — the table below.
8. **Docs of record** — `CHANGELOG.md`, `plans/FRAMEWORK-TODO.md`, `plans/HANDOFF.md`.
9. **Comment on #351 correcting its premise** before closing it, so the record
   does not preserve the wrong claim about fixture churn.

## Verification

| Check | Command | Expected |
| --- | --- | --- |
| Parity | `python3 -m pytest tests/acceptance/deterministic/test_id_coordinator.py` | green (red at step 2) |
| Acceptance tier | `python3 -m unittest discover -s tests/acceptance/deterministic -q` | no regressions |
| Conformance | `python3 -m pytest tests/conformance/` | 243+ pass |
| Hermes | `python3 -m pytest platforms/hermes/tests/` | 570 pass |
| Vendoring intact | `md5sum tools/sdd_doc_lint/__init__.py platforms/*/sdd_doc_lint/__init__.py` | three identical sums |
| Bundle | `git add -A && bash tools/sync-plugin-framework.sh && git diff --name-only` | empty |
| **No golden churn** | `git diff --stat tests/acceptance/fixtures/` | **empty** — this is the plan's central claim; a non-empty result means the premise correction was wrong and the work stops |
| No spec change | `git diff --stat framework/` | empty |

## Risks

| # | Risk | Mitigation |
| --- | --- | --- |
| 1 | D1's question is answered "delete" *after* the work lands | Step 1 forces the question first. The work is small enough that the loss is bounded either way |
| 2 | The module-scope import breaks under a different `sys.path` (e.g. pytest rootdir) | Step 3 runs the suite from both `tests/` and repo root; the existing `parents[2] / "tools"` idiom is preserved, only hoisted |
| 3 | `safe_load_all` merge picks the wrong document when keys collide | Merge is last-wins over a dict update, and the regression test asserts the extracted element count per golden, so a wrong merge shows up as a count change |
| 4 | E's docstring edit is mistaken for a behaviour change at review | The PR body states it is documentation inside code, with the correct implementation cited 200 lines above |

## Claim ledger

| #   | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | `element_hash` re-derives the hash with no normalization | `def element_hash` | tests/acceptance/_id_coordinator.py:17 |
| 2 | The canonical implementation applies the transform to both text fields | `_normalize_hash_field(title)` | `tools/sdd_doc_lint/__init__.py`:933 |
| 3 | The module already imports from the canonical module, so delegation is not a new coupling | `from sdd_doc_lint import _normalise_heading` | tests/acceptance/_id_coordinator.py:30 |
| 4 | That import sits inside `extract_elements`, so `element_hash` alone never runs the path insert | `sys.path.insert` | tests/acceptance/_id_coordinator.py:29 |
| 5 | The smoke test checks determinism and shape, never parity | `def test_element_hash_is_deterministic` | tests/acceptance/deterministic/test_id_coordinator.py:22 |
| 6 | The string `section_id` form is deliberate — its own test asserts it | `project_scope` | tests/acceptance/deterministic/test_id_coordinator.py:31 |
| 7 | The registry element pattern requires two-digit numerics | `element: "^[A-Z]+` | framework/registry/LAYER_REGISTRY.yaml:216 |
| 8 | `extract_elements` uses single-document loading | `yaml.safe_load(text)` | tests/acceptance/_id_coordinator.py:68 |
| 9 | The golden-walking test uses `layer_NN/valid`, never `fullpath/` | `fixtures_for(idx, "valid")` | tests/acceptance/deterministic/test_id_coordinator.py:47 |
| 10 | `fixtures_for` resolves to `layer_NN_<name>/<kind>` | `folder = f"layer_{layer_index:02d}_{layer_name}"` | tests/acceptance/_harness.py:20 |
| 11 | The AS11 docstring states the raw input with no mention of the transform | ``{doc_id}:{section_id}:{title}:{description}`` | `tools/sdd_doc_lint/__init__.py`:1132 |
| 12 | F2 already recorded the never-imported module + empty registry | `committed but never imported` | plans/PLUGIN-TEST-SUITE-REVIEW.md:32 |
| 13 | The registry is empty | `{}` | tests/acceptance/fixtures/fullpath/ID_REGISTRY.yaml:1 |

## Docs to update

`CHANGELOG.md` · `plans/FRAMEWORK-TODO.md` (entry → Closed; one new entry for the
deferred D3 option (b)) · `plans/HANDOFF.md`. **No** `framework/`, **no**
`ROADMAP.md` (not a user-visible capability), **no** `VERSION`.

## Review log

### Pass 1 — 2026-07-26 — self-review against source

Five findings, each reproduced before folding.

1. **The issue's fixture-churn premise is false.** Checked rather than accepted:
   `write_registry` has no callers, `ID_REGISTRY.yaml` is `{}` at 3 bytes and
   unchanged since `f0d08f54`, and the goldens carry no `TYPE.NN.SS.xxxx` IDs
   for `extract_elements` to have minted. **Folded** — promoted to its own
   section at the top of the plan, because it changes the work's risk profile
   and the founder's deferral was made on the wrong premise.
2. **PLUGIN-TEST-SUITE-REVIEW F2 already covers half of this** and was not cited
   by #351. **Folded** into the premise section and D1; F2's "or remove both
   files" became D1's open question rather than being silently ignored.
3. **A latent crash, unreported anywhere.** `extract_elements` raises
   `ComposerError` on three committed `golden_chain` YAML goldens. **Folded** as
   scope item D + design D4, with the reason it is invisible (the walking test
   uses a different fixture tree) stated so the fix includes a test that would
   have caught it.
4. **The delegation has an import trap.** The `tools/` path insert lives inside
   `extract_elements`, so a naive module-scope `from sdd_doc_lint import
   compute_element_hash` would `ImportError` on the parity test's own call path.
   **Folded** into D2 as an explicit instruction.
5. **First draft "fixed" the string `section_id` to a numeric.** That would have
   broken `extract_elements`, whose `section_id` comes from a normalised heading
   with no numeric available, and required inventing a heading→ordinal mapping —
   precisely the new-contract overreach GD-09 declined for TDD. **Folded** as
   D3, resolved to option (c) with the real fix recorded as a deferred TODO.

### Pass 2 — 2026-07-26 — re-review of the Pass-1 patches

Four findings, all from the Pass-1 edits themselves.

1. **Pass 1 made the plan argue for deletion without proposing it.** The premise
   section established the module has no consumer; D1 then said "fix, not
   delete" but the *reason* was thin. **Patched** — D1 now separates the two
   questions (a defect is a defect regardless of strategy) and states the cost
   of the choice, with step 1 forcing the strategy question before any work.
2. **The D4 fix was specified without a test that reaches it.** Changing
   `safe_load` → `safe_load_all` while the only caller-test still walks
   `layer_NN/valid` would leave the fix unverified and the coverage gap intact.
   **Patched** — D4 and step 4 now require a `fullpath/` regression test, red
   before and green after.
3. **The verification table lacked the one check that proves the premise.**
   "No golden churn" was asserted in prose but not verified in the table.
   **Patched** — `git diff --stat tests/acceptance/fixtures/` added, with an
   explicit stop condition: a non-empty result falsifies the premise and halts
   the work.
4. **E's blast radius was understated.** The first draft said "docstring only,"
   omitting that `tools/sdd_doc_lint/` is vendored into both platforms, so the
   edit changes three files and needs the bundle sync. **Patched** — file table,
   step 6, and the `md5sum` verification row now say so.

### Pass 3 — 2026-07-26 — re-review of the Pass-2 patches

No new substantive gaps. Two wording corrections only: the version-impact row
now says "no `VERSION` bump" explicitly rather than implying it via "not
GATE-SPEC" (E touches `tools/`, which a reader could reasonably think is a
platform surface), and Risk 2 names the concrete failure mode (pytest rootdir)
rather than "path issues." Converged.

## Implementation notes — 2026-07-26

Step 1 was put to the founder before any code was written; the answer was
**keep + fix**, so A–E executed as specified. Three corrections to the plan that
only surfaced against the source:

1. **Step 6 named the wrong sync script.** `tools/sync-plugin-framework.sh`
   vendors `framework/` subtrees plus three named `tools/` files
   (`saga_driver.py`, `finding_filter.py`, `playbook_loader.py`) — **not**
   `sdd_doc_lint`. The script that re-vendors the linter is
   `tools/sdd_doc_lint/sync-vendored.sh`, which
   `tests/conformance/platforms/test_doc_lint_vendoring.py:13` names as the fix
   command. Used that; the three `md5sum`s match.
2. **"Frontmatter-bearing" is not the same as "multi-document."** A *leading*
   `---` is only a document-start marker; what `safe_load` rejects is a second
   document, i.e. a *closing* fence. All six `fullpath` YAML goldens open with
   `---`, but only the three under `golden_chain/` carry two markers and crash.
   The regression test counts parsed documents rather than inspecting the first
   line.
3. **The parity table needed guards of its own.** A parity case whose raw and
   normalized forms happen to coincide would pass under the wrong implementation
   too — the same "passes under any hash function" flaw that let the original
   divergence hide. `test_parity_cases_actually_exercise_the_transform` asserts
   every case differs pre/post transform. It is a property of the *table*, not of
   `element_hash` — it is green on `HEAD` too, by design; the 8 subtests that go
   red before the fix and green after are
   `test_element_hash_matches_canonical_prefix`'s.

   Self-review then found the table had a hole the guard could not see. A
   per-step mutation matrix (drop one transform step, see which rows catch it)
   showed **exactly one row covers NFC** — and only while its text stays
   decomposed. A formatter that precomposed the literal would drop NFC coverage
   to zero with every test still green, since that row's casefold difference
   alone satisfies the exercise-check. Fixed by writing the row as `é`
   escapes plus `test_nfc_case_is_decomposed`. Final matrix: nfc←1 row,
   truncate←1, collapse←3, strip←4, casefold←7. Every step covered.

4. **The same trap caught the YAML fix, twice.** Review found the merge should
   take the last dict document rather than union the key sets (a union promotes
   frontmatter keys into the section namespace, diverging from
   `_harness.headings()`). The `fullpath/` regression test was then asserted to
   catch that — it does not: mutating the fix back to `data.update(document)`
   left all tests green, because today's frontmatter is `doc_id` (scalar) and
   `metadata` (filtered by name). The first replacement test *also* failed to
   discriminate: `reuse:` (TRACEABILITY.md:141), the one first-class frontmatter
   block the spec defines, is a flat dict of scalars and mints nothing either
   way. Only a frontmatter key mapping to a **mapping-of-mappings** — the
   extractor's own criterion for a walkable section — separates the two
   implementations, so `test_frontmatter_keys_are_not_walked_as_sections`
   synthesises exactly that, verified red under the mutation and green after.
   **Every "this test would catch it" claim in this PR was checked by mutation;
   two of them were false.**

**Verification at ship** — parity + fullpath tests red before, green after;
acceptance deterministic tier 62 tests with the **same 3 pre-existing failures**
as `HEAD`; conformance **253 passed / 688 subtests**; Hermes **570 passed**;
`git diff --stat tests/acceptance/fixtures/` **empty** (the plan's central claim,
confirmed); `git diff --stat framework/` empty; both sync scripts idempotent.

**Those 3 pre-existing failures turned out to be untracked**, contrary to a first
draft of this note that attributed them to `CORPUS-REFGRAN-RECASCADE`. That entry
is `[example-corpus]`, covers `examples/url-shortener/docs/`, and touches the
acceptance suite only in one clause about `SPEC-01_golden` REFGRAN01 — it does not
cover ACC01 (present in 2 of the 3) or the COV02 findings on these fixtures. Filed
as `ACCEPTANCE-TIER-DRIFT-UNTRACKED` +
[#365](https://github.com/vladm3105/aidoc-flow-framework/issues/365), together
with the reason it went unnoticed: **no CI workflow runs the acceptance tier.**
