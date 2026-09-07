# LINT-TAG-QUOTE-001 Plan — terminate a trace-tag value on a quote

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | LINT-TAG-QUOTE-001                                             |
| Type           | bugfix                                                         |
| Status         | PLANNED — 2026-08-26T00:00:00Z                                 |
| Depends on     | none                                                           |
| Feeds          | `IPLAN-TDDREF-001` (its carrier is unusable without this)      |
| Version impact | **none** — touches no `framework/` path, so GATE-SPEC does not fire (§D3) |

## Objective

Make a `@<layer>:` trace tag resolve when it ends a quoted YAML scalar. Today the
closing quote is captured into the value, the id fails validation, and the citation
is silently discarded from the trace graph.

## Scope

**In:** the value-capture character class in the two tag regexes, their vendored
mirrors, a regression test, and the one prose comment the change falsifies.

**Out:** any `framework/` edit, any new lint rule, any template or corpus change, and
the `IPLAN-TDDREF-001` carrier that motivated this.

## Approach / Design

### D1 — The defect

`TAG` captures `[^\s|]+` (Claim 1). A closing `"` is neither whitespace nor a pipe,
so on

```yaml
      tdd_ref: "@tdd: TDD.01.04.aaaa"
```

the captured value is `TDD.01.04.aaaa"`. `ELEM_FORM` and `DOC_FORM` are fully
anchored (Claim 2), so `doc_id_from_token` returns `None` and `build_edge_graph`
**discards the citation** (Claim 3). The tag is then invisible to the edge graph, to
`TRACE-RES-001` resolution checking, and to `REFGRAN01`.

Only the **final** tag of a quoted scalar is affected — earlier tags terminate on the
pipe. The single-tag case, which is the common one, is always corrupted.

**The blast radius is the framework's own contract, not one carrier field.** All
**eight** layer templates prescribe exactly the form the linter discards — 82
occurrences of `"@<layer>: …"` across `01_BRD` through `08_IPLAN` (Claim 14 cites one;
re-measure with `grep -c '"@[a-z]*:' framework/layers/*/[A-Z]*-TEMPLATE.yaml`). So any
corpus authored to template is affected, which is a stronger justification than the
`IPLAN-TDDREF-001` carrier that surfaced it.

A live in-repo instance sits inside a required context:
`IPLAN-00_index.TEMPLATE.yaml:29` carries `source_spec: "@spec: SPEC-NN"` and the index
templates are linted (Claim 15). The fix changes that finding's ID01 *message* from
`'@spec: SPEC-NN"'` to `'@spec: SPEC-NN'` — code, path and line unchanged. Benign, but
it is the worked example of why the probe is not the gate (§Verification).

### D2 — The fix, and why this exact character class

Exclude both quote characters from the capture: `[^\s|'\"]+`, in **both**
`trace_graph.TAG` and `sdd_doc_lint._TAG`.

This is not a new idea in this codebase. `_THRESHOLD` already carries the identical
exclusion for the identical bug class, with a comment naming the glomming failure
(Claim 4). `ACC01` works around the same defect rule-locally by re-extracting the
leading token (Claim 5) — evidence the defect is known, and that a local workaround
does not fix the *edge*, only that one rule's pairing.

**The exclusion cannot truncate a legitimate value — for either consumer.** The
captured value is validated on two paths, and both are fully anchored and admit
neither quote: the edge-graph path against `DOC_FORM`/`ELEM_FORM` (Claim 6), and
`ID01` against the **registry** `id_patterns` (Claim 16), which is a different source
the first draft did not cite. Excluding both quotes is strictly correct; excluding
only `"` would leave the single-quoted YAML form broken.

Two riders, so a later reader does not over-read this:

- **Strictly correct about non-truncation is not the same as complete termination.**
  ACC01's own workaround comment names a trailing **comma** as well as the quote, and
  backticked tags are common in prose surfaces. None of those are lint targets today.
  This fix closes the quote case only, deliberately.
- **There is a third tag regex and it is correctly out of scope.**
  `tests/conformance/test_framework_review_guards.py` uses a positive class that
  already terminates on a quote (Claim 17). `TAG` and `_TAG` are the only two
  instances of the defective class; `_THRESHOLD` already carries the fix.

### D3 — This PR touches no `framework/` path, so it carries no version bump

`spec_gate.evaluate()` returns `[]` unless some diffed path starts with `framework/`
(Claim 7). This change is confined to `tools/`, `platforms/*/sdd_doc_lint/` and
`tests/`, so neither **GATE-SPEC-E005** nor **E008** fires: no `framework/VERSION`
bump, no `CHANGELOG.md` requirement, and none of the ~100-file version fanout.

That separation is the point. Landing it alone converts "blast radius is zero" from a
claim reviewed inside a large diff into a merged, gate-verified fact that
`IPLAN-TDDREF-001` can depend on.

### D4 — Propagation is scripted and guarded; do not hand-copy

`tools/sdd_doc_lint/sync-vendored.sh` copies all four linter modules into **both**
platform mirrors (Claim 8), and `test_doc_lint_vendoring.py` asserts byte-identity
over the same set, naming that script as the remedy (Claim 9). So divergence fails
the PR rather than shipping silently.

⚠️ `tools/sync-plugin-framework.sh` is **not** the script for this: it vendors three
unrelated tools files and never touches `sdd_doc_lint` (Claim 10).

## File structure

### Modified

- `tools/sdd_doc_lint/trace_graph.py` — the `TAG` capture class, and the comment at
  Claim 11 which documents the old behaviour and becomes false.
- `tools/sdd_doc_lint/__init__.py` — the `_TAG` capture class.
- `platforms/claude-code-plugin/sdd_doc_lint/{trace_graph.py,__init__.py}` — mirrors.
- `platforms/hermes/sdd_doc_lint/{trace_graph.py,__init__.py}` — mirrors.

### Created

- `tests/unit/test_tag_quote_termination.py` — the regression, registered in
  `tests/conformance/test_repo_scripts.py`'s `REGISTERED` tuple, because `tests/unit/`
  is executed by no hook and no workflow (Claim 12).

## Implementation sequence

### Phase A — Test-first

Assert that a tag ending a double-quoted scalar and one ending a single-quoted scalar
both yield a value passing `ELEM_FORM`, and that `build_edge_graph` records an edge
for each. Assert the pipe behaviour is unchanged. Confirm red.

### Phase B — The fix

Apply `[^\s|'\"]+` to both regexes. Update the falsified comment (Claim 11) to name
the quote terminator alongside the pipe. Confirm green.

### Phase C — Propagate (a precondition, not a tidy-up)

The deterministic acceptance tier lints through the **plugin's vendored copy**, not
`tools/` (Claim 21). So Phase D measures the mirror: reordering C and D yields a green
run that proves nothing.

Run `bash tools/sdd_doc_lint/sync-vendored.sh`. Re-run until two consecutive
`pre-commit run --all-files` runs are clean — `ruff-format` may rewrite a file after
it is copied.

### Phase D — Prove the blast radius

Run the full suites (§Verification). The measured expectation is **no change to any
finding**, because no **lint-target** artifact uses a quoted tag form — zero matches
across `tests/acceptance/fixtures/**`, `tools/sdd_doc_lint/fixtures/**` and
`examples/url-shortener/docs/**`. The *templates* use it pervasively (§D1), but
templates are never linted; the one linted template-shaped file changes only a message.

## Verification

- `python3 -m pytest tests/conformance -q` — green, including
  `test_doc_lint_vendoring` (Claim 9).
- `python3 -m pytest tests/acceptance/deterministic -q` — green. **This is the real
  gate, not the probe:** the acceptance manifests match on a message-derived field, so
  a change that alters only a finding's *message* is invisible to a code/path/line
  comparison but can still redden this tier.
- `python3 -m sdd_doc_lint examples/url-shortener/docs/` — no change against HEAD.
- **`PYTHONPATH=tools`** `python3 -m pytest tools/sdd_doc_lint/tests -q` — green. The
  suite does not collect without it (Claim 19).
- **CI contexts this diff triggers that the first draft named none of:** `doc-review`
  fires on `tools/sdd_doc_lint/**` and runs the linter's own tests plus a negative gate
  requiring `rc == 1` exactly on the broken fixtures (Claim 20) — the most likely place
  a regex change moves; and `Hermes platform` fires on `platforms/hermes/**`. Neither is
  a required context, but both will run.
- Claim 13's probe as **supporting evidence only**, with its stated limits.
- `python3 tests/chg/spec_gate.py` over the PR diff — returns no failures, confirming
  D3.

## Docs to update

`framework/governance/LINT_RULES.md` is **not** affected — no rule is added or
changed. `plans/DECISIONS.md` records the fix and its zero-delta measurement.

**Both platform changelogs are mandatory**, and this is a convention the gate does not
enforce: `CONTRIBUTING.md`'s matrix makes `platforms/<name>/CHANGELOG.md [Unreleased]`
a same-PR requirement for any `platforms/<name>/**` change (Claim 18), and this PR
edits both vendored mirrors. GATE-SPEC-E008 not firing (§D3) says nothing about it —
D3's "no `CHANGELOG.md` requirement" is about the **root** changelog and the gate only.

⚠️ Separately and **not in this PR**: `CLAUDE.md:736` states "No script does it" about
the vendored mirrors and then names `sync-vendored.sh` two sentences later. That
durable-trap entry is self-contradictory and misled this plan's own first draft; it
needs a correction of its own.

<!-- markdownlint-disable MD050 -->

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The tag value capture is `[^\s\|]+`, which does not terminate on a quote | `TAG = re.compile` | tools/sdd_doc_lint/trace_graph.py:32 |
| 2  | `ELEM_FORM` is fully anchored, so a value carrying a trailing quote fails validation | `ELEM_FORM` | tools/sdd_doc_lint/trace_graph.py:37 |
| 3  | An unresolvable token is skipped, so the citation contributes no edge | `cited_doc is None` | tools/sdd_doc_lint/__init__.py:1763 |
| 4  | `_THRESHOLD` already excludes both quotes for this exact bug class, with a comment naming the glomming failure | `_THRESHOLD` | tools/sdd_doc_lint/__init__.py:215 |
| 5  | ACC01 re-extracts the leading token to work around the same glomming, which pairs but produces no edge | `take the leading` | tools/sdd_doc_lint/__init__.py:2464 |
| 6  | Tag values are validated against forms admitting neither quote character, so excluding both cannot truncate a legitimate value | `DOC_FORM` | tools/sdd_doc_lint/trace_graph.py:35 |
| 7  | `spec_gate` returns no failures unless a diffed path starts with `framework/` | `touched_framework = any` | tests/chg/spec_gate.py:80 |
| 8  | `sync-vendored.sh` copies the linter modules into both platform mirrors | `canonical=` | tools/sdd_doc_lint/sync-vendored.sh:10 |
| 9  | A conformance guard asserts the vendored copies are byte-identical, so divergence fails the PR | `MODULES =` | tests/conformance/platforms/test_doc_lint_vendoring.py:25 |
| 10 | `sync-plugin-framework.sh` vendors three unrelated tools files and never touches `sdd_doc_lint` | `TOOLS_FILES=` | tools/sync-plugin-framework.sh:33 |
| 11 | A prose comment documents the pipe-only termination and is falsified by this change | `terminates on a` | tools/sdd_doc_lint/trace_graph.py:29 |
| 12 | Registering in the conformance shim promotes a `tests/unit/` module into the **required** conformance context, which the linter's own suite (path-filtered, non-required `doc-review`) never reaches — that is the reason to put the regression there | `REGISTERED = (` | tests/conformance/test_repo_scripts.py:31 |
| 13 | The fix changes no finding on the corpus or three golden tiers. Supporting evidence only — it compares code/path/line as a **set**, so it is blind to message-text changes, to multiplicity (two findings sharing a triple collapse to one), and to `trace_walk`/`sdd_coverage`. **Blocks Phase D** | `TAG` | PROBE: `cd tools && python3 -c "import sys,re,pathlib;sys.path.insert(0,'.');import sdd_doc_lint as L;from sdd_doc_lint import trace_graph as TG;ts=[pathlib.Path(x) for x in ['../examples/url-shortener/docs','../tests/acceptance/fixtures/fullpath/golden_chain','../tests/acceptance/fixtures/layer_08_iplan/valid','../tests/acceptance/fixtures/layer_07_tdd/valid']];r=lambda t:sorted((f.code,f.path,f.line) for f in L.lint_path(t));b=[r(t) for t in ts];q=chr(39)+chr(34);p=re.compile(TG.TAG.pattern.replace('[^\\s','[^\\s'+q));TG.TAG=p;L._TRACE_TAG=p;L._TAG=re.compile(L._TAG.pattern.replace('[^\\s','[^\\s'+q));print(sum(len(set(x)^set(r(t))) for x,t in zip(b,ts)))"` — printed `0` on 2026-08-26 |
| 14 | Two further tools import from `trace_graph` and are unexercised by the probe, so the suites rather than the probe are the gate | `from sdd_doc_lint.trace_graph import` | tools/trace_walk.py:38 |

| 14 | The framework's own layer templates prescribe the quoted tag form the linter discards | `bdd_scenario:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:123 |
| 15 | The eight index templates are linted, so a quoted tag inside one is a live lint target | `-00_index.TEMPLATE.` | tests/conformance/test_index_template_lint.py:34 |
| 16 | `ID01` validates the captured value against the registry `id_patterns`, a second anchored source the first draft did not cite | `doc_re.match(val)` | tools/sdd_doc_lint/__init__.py:671 |
| 17 | A third tag regex exists in the review guards and already terminates on a quote — correctly out of scope | `[A-Za-z][A-Za-z0-9.` | tests/conformance/test_framework_review_guards.py:16 |
| 18 | `CONTRIBUTING.md` makes a platform changelog entry a same-PR requirement for any `platforms/<name>/**` change | `[Unreleased]` | CONTRIBUTING.md:51 |
| 19 | The linter's own suite does not collect without `PYTHONPATH=tools` | `PYTHONPATH=tools` | tools/sdd_doc_lint/tests/test_lint.py:3 |
| 20 | `doc-review` triggers on `tools/sdd_doc_lint/**` and runs the linter suite plus a negative fixture gate | `tools/sdd_doc_lint/` | .github/workflows/doc-review.yml:16 |
| 21 | The deterministic acceptance tier lints through the plugin's vendored copy, so the mirror is what Phase D measures | `plugin_bundle_root()` | tests/acceptance/_harness.py:273 |

<!-- markdownlint-enable MD050 -->

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | A finding's message text changes without its code/path/line moving, reddening the acceptance tier invisibly to the probe | Medium | Verification gates on `tests/acceptance/deterministic`, not the probe; Claim 13 states the limit |
| R2 | Only `"` is excluded, leaving single-quoted YAML broken | Medium | D2 states the literal class `[^\s\|'\"]+` |
| R3 | The mirrors are hand-copied and drift after `ruff-format` | Low | Phase C uses `sync-vendored.sh`; Claim 9's guard fails the PR if they drift |
| R4 | The falsified comment is left in place, so the next reader trusts it | Medium | It is a named deliverable of Phase B (Claim 11) |

## Review log

### Pass 0 — 2026-08-26 — authoring (NOT a review pass)

Split out of `IPLAN-TDDREF-001` on that plan's Pass-2 recommendation. The fix was
folded into the carrier plan at its Pass 1, which grew that plan to a ~100-file
version-bump diff; `spec_gate` fires only on `framework/` paths (Claim 7), so
separating the linter fix yields a PR of roughly ten files — six source, the regression, the shim registration, and two platform changelogs — with no bump and no fanout, and
lets the carrier plan depend on a merged fact rather than a reviewed claim.

### Pass 1 — 2026-08-26 — independent (`verified-planning-reviewer`)

Five load-bearing findings. All verified against source before folding.

- **The zero-delta reason was false and the defect is bigger than stated.** "No artifact
  uses a quoted tag form" is wrong: **all eight** layer templates prescribe it (82
  occurrences), and one linted index template carries it. **Folded:** §D1 now frames the
  blast radius as the framework's own contract — a stronger justification — and Phase D
  narrows the claim to *lint-target* artifacts. The zero-delta conclusion survives.
- **Both platform changelogs are mandatory and were unlisted.** `CONTRIBUTING.md`'s
  matrix requires them for any `platforms/**` change; E008 not firing says nothing about
  it. **Folded into Docs to update, with the gate-vs-convention distinction stated.**
- **A Verification command could not run** — the linter suite needs `PYTHONPATH=tools`.
  **Folded.**
- **No CI context was named**, and the diff triggers `doc-review` (which runs the
  linter suite and a negative gate requiring `rc == 1`) and `Hermes platform`.
  **Folded.**
- **D2 proved its non-truncation property for only one of two consumers.** `ID01`
  validates against the registry `id_patterns`, not `DOC_FORM`/`ELEM_FORM`. Conclusion
  survives; **the missing citation is now Claim 16.**

Minors folded: Phase C is a precondition because the acceptance tier lints the
**mirror**, not `tools/` — reordering yields a green run proving nothing; Claim 12's
reason was inverted (registration promotes the test into a *required* context, which is
the argument *for* `tests/unit/`); Claim 13 gains multiplicity blindness; the fix closes
the quote case only, not the trailing comma or backtick; the third tag regex is named as
deliberately out of scope; "six files" corrected to ~ten.

### Pass 2 — 2026-08-26 — dispatched, stopped before returning

An independent pass was dispatched and the founder stopped it. **It contributed no
findings and is not counted.** The plan therefore stands at **one** completed
independent pass, whose five load-bearing findings are all folded above.

**Result:** **not ready by the verified-planning bar**, which requires two dispatched
passes with the last returning clean. Nothing is known-open: every Pass-1 finding was
verified against source and folded, and the citation gate passes all 21 citations. The
outstanding item is procedural — dispatch one more pass before the PR opens.

### Implementation — 2026-08-26

Implemented and verified. Phase A's regression went red on 8 assertions and green after
the fix; the unquoted control passed throughout. The measured blast radius held at
**zero** across the corpus and all three golden tiers, and the acceptance tier — the
real gate, since the probe is blind to message-text changes — stayed green.

- `tests/unit/test_tag_quote_termination.py`, registered in the conformance shim so it
  rides a required context. It asserts the character class itself carries both quotes,
  not merely that one worked example resolves: a caller-side strip (ACC01's workaround)
  would satisfy every other assertion while leaving the edge graph broken.
- Both regexes patched; the falsified comment in `trace_graph.py` rewritten.
- Propagated with `tools/sdd_doc_lint/sync-vendored.sh`; `test_doc_lint_vendoring`
  green. Two consecutive `pre-commit run --all-files` runs clean.
- `spec_gate.evaluate()` over the linter-only file set returns **no failures**, so §D3
  holds: no version bump.

Filed as issue #542.
