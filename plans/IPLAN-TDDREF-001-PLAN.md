# IPLAN-TDDREF-001 Plan — a `tdd_ref` carrier on the IPLAN file manifest

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | IPLAN-TDDREF-001                                               |
| Type           | feature                                                        |
| Status         | PLANNED — 2026-08-26T00:00:00Z                                 |
| Depends on     | **`LINT-TAG-QUOTE-001` (must merge first — §D2)**; GD-15 (accepted, unbumped) |
| Feeds          | `IPLAN-COV04-002` — the coverage rule, whose matcher is written against this field |
| Version impact | framework MINOR; the `framework/VERSION` bump + `CHANGELOG.md` are **required in the shipping PR diff** (§D4) |

## Objective

Give an IPLAN file-manifest entry a **line-local `tdd_ref` field** whose value is a
`@tdd:` tag, so a TDD test case is machine-attributable to the IPLAN that builds it —
carried on the manifest entry for the file.

**The entry-level binding is authored, not enforced.** A line-local matcher proves
only that some `tdd_ref` line in this IPLAN cites the element; it cannot prove the
line sits in a `file_manifest` entry rather than a renamed block, nor say *which*
entry. Enforcing that needs a structural parse, deferred with Stage 2's `tasks[]`
(design F-3). The Objective is stated at the granularity the mechanism delivers.

This ships no linter change and no lint rule — the linter defect its carrier depends
on is `LINT-TAG-QUOTE-001`, a separate PR.

## Why this shape (supersedes IPLAN-COVMAP-001)

The predecessor proposed a new top-level `coverage_map` section. Three independent
review passes (5 → 7 → 5 load-bearing findings) established that the section was
both **insufficient** and **more expensive than necessary**:

- **Insufficient.** `coverage_map:` is a *block* marker. `ACC01`'s parse is strictly
  line-local — its predicate is `_TDD_CASE_ID.search(line) or _BDD_PAIR_FIELD.search(line)`
  (Claim 5) — and it works only because the carrier is a key whose **value is the tag**:
  `bdd_scenario: "@bdd: …"` / `bdd_ref: "@bdd: …"` (Claims 1-4). Under a section header,
  every citation sits on a different line and a line-local matcher counts nothing.
- **More expensive than necessary.** A `tdd_ref:` key **inside the existing
  `file_manifest.files[]` entries** satisfies the identical predicate, and because
  `template_sections()` iterates only top-level keys (Claim 6) it reddens **no**
  acceptance golden, needs no `_required_when_subtype` marker, and — carrying no
  `# Section N:` header — does not move the count the skill/template alignment guard
  asserts (Claim 7). It also needs no `builds:` field: the entry already *is* the file.

The `path:` key cannot serve, because its value is a path (Claim 8). The template
already mandates element-level `@tdd:` per GD-03 (Claim 17) — this plan supplies the
carrier, not the requirement.

## Scope

**In:** the `tdd_ref` field in `IPLAN-TEMPLATE.yaml` and `IPLAN-MVP-TEMPLATE.yaml`;
its authoring guidance; the layer README; one golden as the worked example the
successor's matcher is written against; the bundle mirror; the GATE-SPEC obligations
(§D4).

**Out:** the `COV04` rule, the registry `building_layers` block, any lint constant or
fixture, corpus regeneration, and R3-R12 of
`plans/IPLAN-LAYER-REVIEW-001-DESIGN.md`.

## Approach / Design

### D1 — The carrier is a key whose value is the tag, on the manifest entry

```yaml
file_manifest:
  files:
    - path: "<unit test for the component, per the @spec language>"
      order: 1
      status: NOT_STARTED
      tdd_ref: "@tdd: TDD.NN.04.xxxx | @tdd: TDD.NN.04.yyyy"
```

Directly analogous to `e2e_tests.cases[].bdd_ref` (Claim 2), the shape
`_BDD_PAIR_FIELD` matches. The successor's matcher is the sibling regex
`\btdd_ref\b`, which does **not** collide with the template's existing
`tdd_references:` key — the trailing `e` defeats the word boundary (Claim 18).

**Nesting is irrelevant to a line-local matcher, and this matters for the MVP
template.** `IPLAN-MVP-TEMPLATE.yaml`'s manifest is a **bare list**, not
`{files: [...]}` (Claim 12) — a divergence the parent design assigns to R9 / Stage 5
and which this plan does **not** reconcile. The field attaches to the bare-list entry
there. Any statement that the **matcher** requires `files[]` is wrong. (Hermes' IPLAN validator
is a different consumer and does require a `files` list, which the MVP bare list
already violates — out of scope, R9/Stage 5 owns it.)

**Element scope:** the carrier cites §4 test-case ids (`TDD.NN.04.xxxx`). The
successor rule must state whether it enumerates only those or every
`TDD.NN.SS.xxxx` in `element_host`; this plan does not decide it.

### D2 — The carrier is unusable until `LINT-TAG-QUOTE-001` merges

`TAG` captures `[^\s|]+`, so a closing `"` gloms into the value, `ELEM_FORM` fails,
and `build_edge_graph` discards the citation. Reproduced directly:
`tdd_ref: "@tdd: TDD.01.04.aaaa"` captures `TDD.01.04.aaaa"`. Only non-final tags in a
multi-tag scalar survive; the single-tag case is always corrupted.

All three candidate authoring forms were measured, and none is usable without the
linter fix:

| Form | YAML parses | Tag survives capture | Tag on the `tdd_ref` line |
| --- | --- | --- | --- |
| `tdd_ref: "@tdd: TDD.01.04.aaaa"` | yes | **no** — captured `TDD.01.04.aaaa"` | yes |
| `tdd_ref: @tdd: TDD.01.04.aaaa` | **no** — `@` is a reserved indicator | yes | yes |
| `tdd_ref: \|` + tag on the next line | yes | yes | **no** — breaks line-locality |

The quoted form is the only one that can work, and it works only with the dependency
merged. Keep this table: it is the sole record of why the block scalar was rejected,
and a later reader will otherwise re-propose it.

**That fix is `LINT-TAG-QUOTE-001`, a separate PR**, split out on this plan's Pass-2
recommendation: it touches no `framework/` path, so it carries no version bump and
none of the ~100-file fanout, and it lets this plan depend on a merged, gate-verified
fact rather than a reviewed claim. This plan does **not** re-specify it.

### D2b — The carrier is format-agnostic; there is no Markdown deferral

**A previous draft scoped this to YAML and deferred a Markdown carrier to a Stage-5
generator. That was wrong and is withdrawn.** `_BDD_PAIR_FIELD` is a bare word match
over `text.splitlines()` with no YAML dependency, and the all-Markdown example corpus
**already pairs through it today**: `TDD-01.md` carries rows of the form
`` `TDD.01.04.3c7f` bdd_ref @bdd: BDD.01.03.9b90 `` (Claim 22). Unquoted in Markdown,
there is no closing quote and no glomming.

So the successor rule is **not** YAML-scoped, and the rendered form needs no invented
marker — the field name *is* the marker. The rendered carrier arrives with the
manifest table when the corpus is regenerated: GD-15 makes a `.md` restating YAML
**generated, not authored**, and `CLAUDE.md` forbids hand-editing example artifacts
independently. Corpus regeneration is out of scope here.

### D3 — `tdd_ref` is optional per entry; coverage is judged from the TDD side

A manifest entry may legitimately realize no test case — a package `__init__`, a
config file. So the field is optional on an entry, and the successor rule asks the
converse question: *is every TDD element cited by some IPLAN document?* That keeps this
plan free of any completeness assertion it cannot enforce.

### D4 — GATE-SPEC obligations are in scope, not excluded

`tests/chg/spec_gate.py` fails **GATE-SPEC-E005** for any `framework/` file in the
diff without `framework/VERSION`, and **E008** without `CHANGELOG.md` (Claim 13). The
gate runs on `pull_request` over the whole PR diff (Claim 14), so this binds when the
PR opens, not per commit. A GD entry in `framework/governance/DECISIONS.md` is the
change record for a `framework/**` normative change.

The predecessor put the bump "out of scope", which would have produced an
unmergeable PR. Phase D's ordering is load-bearing: `framework/VERSION` →
`scripts/sync-version-refs.sh` → `tools/sync-plugin-framework.sh`.

**GD-15 is already in-tree, unbumped and un-changelogged** — verified 2026-08-26, not
inferred from the changelog alone: `git log -S 'GD-15 —' -- framework/governance/DECISIONS.md`
returns nothing and `git show HEAD:framework/governance/DECISIONS.md` contains no GD-15,
so it is an uncommitted working-tree edit. (Its presence in the plugin bundle copy is
this session's `sync-plugin-framework.sh` run, **not** evidence of a merge — a Pass-3
reviewer read it the other way.) (Claim 24) and its own
text names the `VERSION`/`CHANGELOG` bump plus both `FRAMEWORK_SPEC_VERSION` pins as
its change record. Since `spec_gate` evaluates the whole PR diff, **one bump
discharges GD-15 and GD-16 together** — but the CHANGELOG entry must then describe
both, and the plan's header dependency is resolved that way rather than by landing
GD-15 in a separate PR first.

## File structure

### Modified — authored

- `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` — `tdd_ref` on the manifest entries + guidance.
- `framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml` — the bare-list entry gains the field (D1).
- `framework/layers/08_IPLAN/README.md` — the carrier, D3's optionality, D2b's format-agnosticism.
- `tests/acceptance/fixtures/fullpath/golden_chain/08_IPLAN/IPLAN-01_golden.yaml` — the worked example.
- `tests/acceptance/expected_warnings/fullpath__golden_chain.yaml` — **re-derived**, not assumed: editing that golden puts it under the bidirectional warning-multiset contract, where a warning is as fatal as an error.
- `framework/governance/DECISIONS.md` (GD-16), `CHANGELOG.md`, `framework/VERSION`.

### Modified — generated by the fanout (NOT hand-edited)

The `VERSION` bump fans out well beyond the authored set: both
`platforms/*/FRAMEWORK_SPEC_VERSION` (pinned by conformance, Claim 23), `README.md`,
`docs/PARITY.md`, both platform READMEs, `CLAUDE.md`'s framework-spec token, the 52
SKILL frontmatters and the playbook set with its mirror. **This is a ~100-file PR, not
a five-file one** — a different review and a different governance-budget conversation.

⚠️ Do **not** hand-edit `CLAUDE.md`'s framework-spec token before running
`scripts/sync-version-refs.sh`: `fw_prev` is read from `CLAUDE.md` and gates
propagation to five further files, silently, at exit 0.

## Implementation sequence

### Phase A — Templates

Add `tdd_ref` to both templates per D1, quoted, with `_guidance` stating D3's
optionality. Add no `# Section N:` header and no new top-level key.

⚠️ **The guidance must not put the token `tdd_ref` and a `@tdd:` example on the same
line.** That is the ACC01 traceability-block loophole shape in reverse — it would make
the template's own guidance a carrier. `TDD-TEMPLATE.yaml` avoids it by construction:
its guidance names `bdd_ref` in prose and carries no `@bdd:` tag on that line.

**Ship `tests/conformance/test_iplan_carrier.py`** (Risk R2). Two asserts, and they
must **parse the YAML**, not grep — a substring check is satisfied by the unrelated
`tdd_references:` key (Claim 18):

- `IPLAN-TEMPLATE.yaml` — `file_manifest.files[]` has at least one entry carrying a
  `tdd_ref` key.
- `IPLAN-MVP-TEMPLATE.yaml` — at least one bare-list entry under `file_manifest`
  carries a `tdd_ref` key.

Both are needed: the canonical template is as unguarded as the MVP skeleton, and the
Pass-2 finding that produced this risk applies to each.

### Phase B — Worked example — **BLOCKED on `LINT-TAG-QUOTE-001`**

Running this before the dependency merges produces a manifest that is **wrong but
green**: a malformed value is *skipped*, not flagged, by both `_check_trace_resolution`
and `build_edge_graph`. Do not start it early.

Add `tdd_ref` to the `fullpath/golden_chain` IPLAN golden so that **every** element
its sibling TDD declares — `TDD.01.04.aaaa`, `bbbb`, `cccc` — is cited on some
`tdd_ref` line. *Covering* is the deliverable, not merely "real ids": the parent design
assigns this fixture the positive case, and a partial map forces the successor to
re-edit the golden and re-derive the manifest a second time. That TDD declares only §4
ids, so covering is stable under either enumeration the successor picks. Placeholder ids of the `TYPE.NN.SS.xxxx` form fail `ELEM_FORM`,
so the goldens' actual ids are required.

Then re-derive `tests/acceptance/expected_warnings/fullpath__golden_chain.yaml` by
running the tier and diffing — with `LINT-TAG-QUOTE-001` merged the new `tdd_ref` is a
real edge, so the multiset may move. This manifest is Phase B's deliverable.

Do **not** touch `layer_08_iplan/valid/IPLAN-01_golden.yaml`: its frontmatter fence is
unterminated, so it is invisible to the edge graph, and repairing it would move that
directory's expected-warnings manifest — a separate change.

### Phase C — Docs

Layer README; GD-16; `plans/DECISIONS.md`; `plans/HANDOFF.md`; move the parent design's
staging row 1a to its new state (the row already names this task, so the deliverable is
the state change, not the pointer). Then run `tools/sync-plugin-framework.sh` so the
README's bundle copy matches.

These are the plan-surface documents named in §Docs to update; Phase C owns all of
them, so none is left without a phase.

⚠️ `test_spec_hygiene` bans `plugin`, `SKILL` and `doc-<layer>` tokens anywhere under
`framework/**` outside a small allowlist (Claim 25) — the README guidance must avoid
them.

### Phase D — Version and fanout

`framework/VERSION` → `scripts/sync-version-refs.sh` → `tools/sync-plugin-framework.sh`,
in that order, plus `CHANGELOG.md` (§D4). Then `pre-commit run --all-files` twice,
clean both times.

## Verification

- `python3 -m pytest tests/conformance -q` — green. The skill/template alignment guard
  is unaffected because no `# Section N:` header is added (Claim 7).
- `python3 -m pytest tests/acceptance/deterministic -q` — green **without** golden
  section updates, because `template_sections()` reads only top-level keys (Claim 6).
  This is the measurable difference from the predecessor, which reddened two goldens.
- `python3 -m sdd_doc_lint examples/url-shortener/docs/` — **expected delta: zero.**
  The mechanism is that no new *section* is added, so `_load_section_targets` collects
  no new `_size_target` and STRUCT01 is unmoved; the corpus itself is not edited.
- `python3 -c "import yaml,sys;[yaml.safe_load(open(f)) for f in sys.argv[1:]]"` over
  both templates and the edited golden — an unquoted `@` value fails here (§D2 table).
- **The edited golden's own manifest must be re-derived, not assumed.** Editing
  `fullpath/golden_chain`'s IPLAN puts it under the bidirectional warning-multiset
  contract, where a warning is exactly as fatal as an error. With the §D2 fix the new
  `tdd_ref` becomes a real edge, so re-run and diff rather than reasoning about it.
- The `_size_target: 400` on `file_manifest` is **inert** — `_load_section_targets`
  skips sections carrying `_required_when_subtype:`. STY02 falls back to the flat
  default (target 200, blocking 300), and it applies to authored artifacts, not to
  templates, which are never linted.
- `python3 tests/chg/spec_gate.py` against the PR diff — E005/E008 clear (§D4).

## Docs to update

`framework/layers/08_IPLAN/README.md`, `framework/governance/DECISIONS.md` (GD-16),
`plans/DECISIONS.md`, `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md` (staging table) and
`plans/HANDOFF.md` — **all owned by Phase C**. `CHANGELOG.md` is owned by Phase D,
because its entry describes the version bump and must cover GD-15 and GD-16 together
(§D4).

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | `tdd_ref` is authored as a sibling comment or a nested list rather than the key's own quoted value, and the successor's line-local matcher cannot see it | High | D1 fixes the shape against Claim 2's precedent; Phase B's golden is the worked example the matcher is written against |
| R2 | Either template is skipped, so an IPLAN authored from it can never satisfy the successor rule | Medium | **Claim 15's locked precedent is BRD-only** — no gate covers IPLAN, and the canonical template is as unguarded as the MVP one. Phase A ships `tests/conformance/test_iplan_carrier.py` per the §Phase A spec; without it this risk materialises green |
| R3 | Unquoted `@` breaks `yaml.safe_load` in the harness | Medium | §D2's measured form table; the Verification parse step |
| R4 | The PR opens without the `VERSION`/`CHANGELOG` pair and GATE-SPEC blocks it | Medium | D4 puts both in scope with the load-bearing fanout order |
| R6 | The MVP template's `traceability.upstream` emits no `@tdd:` tag at all, so the design's TAG01 backstop does not hold for an MVP-authored IPLAN | Medium | Recorded for the successor; out of scope here (R9 / Stage 5 owns the MVP shape) |

<!-- markdownlint-disable MD050 -->

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | ACC01's YAML carrier is a key whose value IS the tag, which is what makes a line-local match possible | `bdd_scenario:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:123 |
| 2  | `bdd_ref` is the second such carrier and the direct structural analogue of `tdd_ref` | `bdd_ref:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:202 |
| 3  | The matcher is a bare field-name regex, so it matches only when the tag shares the field's line | `_BDD_PAIR_FIELD` | tools/sdd_doc_lint/__init__.py:2190 |
| 4  | The linter states the contract explicitly — the tag value sits ON the field line | `value sits ON the field` | tools/sdd_doc_lint/__init__.py:2185 |
| 5  | The pairing predicate is line-local and accepts either marker, so a field-name carrier is sufficient on its own | `_TDD_CASE_ID.search(line)` | tools/sdd_doc_lint/__init__.py:2457 |
| 6  | `template_sections()` iterates only top-level keys, so a key nested in a manifest entry reddens no golden and needs no subtype marker | `for key, value in data.items()` | tests/acceptance/_harness.py:222 |
| 7  | The skill/template alignment guard counts `# Section N:` headers, so a nested key does not move it | `_template_numbered_count` | tests/conformance/platforms/test_skill_template_alignment.py:83 |
| 8  | IPLAN's `file_manifest` entry key holds a path, not a tag, so `path:` cannot serve as the carrier | `- path:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:94 |
| 9  | A trace edge requires a literal `@<layer>:` token whose value terminates on whitespace or pipe, so one quoted scalar may carry several tags | `TAG` | tools/sdd_doc_lint/trace_graph.py:32 |
| 10 | `@` is a YAML reserved indicator; the template's own precedent quotes the value | `source_spec` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:65 |
| 11 | GD-15 fixes YAML as the normative artifact format and Markdown as a **generated** rendering — the basis for §D2b's regeneration route and §D4's change record | `GD-15` | framework/governance/DECISIONS.md:16 |
| 12 | The MVP skeleton carries its own `file_manifest` entry list, so the carrier must be added there too | `file_manifest:` | framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml:21 |
| 13 | Any `framework/` file in the diff fails GATE-SPEC-E005 without `framework/VERSION`, and E008 without `CHANGELOG.md` | `GATE-SPEC-E005` | tests/chg/spec_gate.py:86 |
| 14 | The gate runs on `pull_request`, so the obligation binds over the PR diff rather than per commit | `pull_request:` | .github/workflows/chg-gate.yml:14 |
| 15 | A template addition moving the MVP skeleton is a precedent locked in code | `BRD-MVP-TEMPLATE.yaml is missing` | tests/conformance/test_seed_contract.py:110 |
| 16 | Any `framework/**` edit requires the plugin bundle re-sync or the byte-identity guard fails | `test_bundle_is_byte_identical` | tests/conformance/platforms/test_plugin_framework_bundle.py:61 |
| 17 | The template already mandates element-level `@tdd:` per GD-03 — this plan supplies the carrier, not the requirement | `element-declaring` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:35 |

| 18 | `\btdd_ref\b` does not collide with the template's existing `tdd_references:` key — the trailing `e` defeats the word boundary | `tdd_references:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:203 |
| 22 | The all-Markdown corpus already pairs through a field-name carrier today, unquoted — so the carrier is format-agnostic and needs no Markdown deferral | `bdd_ref @bdd:` | examples/url-shortener/docs/07_TDD/TDD-01.md:155 |
| 23 | Conformance asserts each platform's `FRAMEWORK_SPEC_VERSION` equals `framework/VERSION`, so the bump fans out beyond the authored set | `assertEqual` | tests/conformance/platforms/test_version_declaration.py:46 |
| 24 | GD-15 is in-tree while `CHANGELOG.md`'s newest framework entry is still GD-14's `0.41.3 → 0.42.0` — so this PR's bump discharges both | `GD-14` | CHANGELOG.md:15 |
| 25 | `test_spec_hygiene` bans `plugin` / `SKILL` / `doc-<layer>` tokens under `framework/**` outside an allowlist | `\bplugin\b` | tests/conformance/test_spec_hygiene.py:31 |

<!-- markdownlint-enable MD050 -->

## Review log

### Pass 0 — 2026-08-26 — authoring (NOT a review pass)

Supersedes `IPLAN-COVMAP-001`, which reached its 3-pass review cap with five
load-bearing findings open. Carried forward from those passes: F1's rendering defect
(now D2's explicit deferral plus a stated Stage-5 obligation), F2's cheaper shape
(now D1, and the reason this plan exists), F3's skill-count breakage (dissolved by
the shape — Claim 7), F4's GATE-SPEC omission (now D4), F5's MVP gap (now Phase A).
The zero-corpus-delta rationale is restated by its real mechanism rather than
"no rule ships".

### Pass 1 — 2026-08-26 — independent (`verified-planning-reviewer`)

Six load-bearing findings. The two decisive ones were reproduced by direct execution
before folding, not accepted on the report.

- **The plan's own quoting rule broke the citation.** `TAG` captures `[^\s|]+`, so a
  closing `"` gloms into the value, `ELEM_FORM` fails and `build_edge_graph` discards
  it. Reproduced: `tdd_ref: "@tdd: TDD.01.04.aaaa"` captures `TDD.01.04.aaaa"`. The
  single-tag case — the one in the plan's own snippet — is always corrupted.
  **Folded: §D2 adds the `_THRESHOLD`-style quote exclusion, with blast radius
  measured at zero across four tiers (Claim 21); Phase A is now test-first on that
  fix.**
- **D2's YAML-only deferral was unnecessary and is withdrawn (subtractive).** The
  field-name carrier has no YAML dependency and the all-Markdown corpus already pairs
  through it (Claim 22). **Folded: §D2b replaces the deferral; the successor is not
  YAML-scoped and needs no invented Stage-5 marker.**
- **`IPLAN-MVP-TEMPLATE.yaml` has no `files[]`** — its manifest is a bare list, a
  divergence assigned to R9/Stage 5. **Folded into D1: nesting is irrelevant to a
  line-local matcher, stated explicitly so Phase B is executable.**
- **The Objective overclaimed file-level attribution.** A line marker binds a citation
  to a line, not to an entry. **Folded: narrowed to document-level, with the
  entry-level binding stated as authored-not-enforced.**
- **D4's obligations were incomplete and the diff was understated ~20×.** GD-15 is
  in-tree, unbumped and un-changelogged; the fanout touches ~100 files.
  **Folded: one bump discharges GD-15 and GD-16; File structure now separates
  authored from generated and carries the `CLAUDE.md` `fw_prev` rider.**
- **R2's mitigation cited a BRD-only precedent.** No gate covers the IPLAN MVP
  skeleton. **Folded: Phase A adds a one-assert conformance check.**

Minors folded: Claim 13's line was one early; Claim 17 was an orphan and is now cited;
the `_size_target: 400` is inert (STY02 falls back to 200/300 and applies to artifacts,
not templates); Phase C warns about `test_spec_hygiene`'s banned tokens; the staging
row already names this task, so Phase D's deliverable is the state change.

### Pass 2 — 2026-08-26 — independent (`verified-planning-reviewer`)

Six load-bearing findings; the decisive one was a **scope cut**, not a fold.

- **Split the linter fix out.** `spec_gate` fires only on `framework/` paths, so the
  `_TAG` change on its own is a six-file PR with no version bump and none of the
  ~100-file fanout — and landing it first turns "blast radius zero" from a claim
  reviewed inside a large diff into a merged, gate-verified fact. **Actioned:**
  `plans/LINT-TAG-QUOTE-001-PLAN.md`; §D2 is now a dependency statement and Phase A is
  gone.
- **"No script syncs the vendored mirrors" was false, twice.**
  `tools/sdd_doc_lint/sync-vendored.sh` copies all four linter modules to both mirrors,
  and `test_doc_lint_vendoring.py` asserts byte-identity and names that script as the
  remedy — so divergence fails the PR rather than shipping silently. Worse, the plan's
  only sync step was `sync-plugin-framework.sh`, which vendors three unrelated tools
  files and **would not have propagated the fix at all**. Verified. **Actioned:** both
  the file list and Risk R5 moved to `LINT-TAG-QUOTE-001`, which owns the propagation.
- **The probe was being used as an acceptance gate and is too weak for that.** It
  compares code/path/line and is blind to message-text changes, which is exactly what
  dropping a glommed quote does; the acceptance manifests match on a message-derived
  field. **Actioned:** the suites are the gate; the probe is supporting evidence with
  its limits stated in the row.
- **§D2b's supporting sentence named the wrong table and contradicted GD-15.** The
  File-to-contract map is not the rendered file manifest, and "a per-row edit, not a
  generator" inverts GD-15 consequence 2 and the never-hand-edit rule. **Folded:** the
  conclusion stands, the sentence is replaced by the regeneration route.
- **No phase owned `expected_warnings/fullpath__golden_chain.yaml`** even though
  Verification anticipated it moving. **Folded into Phase B as its deliverable.**
- **Claim 11 asserted a rationale the plan had abandoned.** **Folded:** restated as
  GD-15's format ruling, which §D2b and §D4 both lean on.

Minors folded: D3 still said "entry" after the Objective was narrowed to document
level; the `files[]` sentence now scopes to the matcher and notes Hermes' validator as
a separate consumer; Phase A's guidance must not put `tdd_ref` and a `@tdd:` example on
one line (the ACC01 loophole shape in reverse); R3 pointed at a rule that moved.

### Pass 3 — 2026-08-26 — independent (`verified-planning-reviewer`)

Five load-bearing findings; the review cap (3) is reached, so the loop stops here.

**Applied — subtractive or defect-preventing only:**

- **Cut residue removed.** Ledger rows 19-21 justified the `_TAG` work that left this
  plan at Pass 2. Row 21 was worse than orphaned: it still read "**Blocks Phase A**",
  and Phase A is now *Templates* — an implementer would have run a linter blast-radius
  probe as a precondition for adding a template field. Deleted; the measurement lives in
  `LINT-TAG-QUOTE-001` Claim 13.
- **D3 would have shipped the loophole into normative text.** It phrased the successor's
  question document-scoped — which the parent design explicitly rejects — and `:154`
  sends that content into `framework/layers/08_IPLAN/README.md`. Corrected to name the
  `tdd_ref` carrier line, with a note that the qualifier must survive into the README.
- **Phase B is now marked BLOCKED, not merely dependent.** Running it before the
  dependency merges yields a manifest that is *wrong but green*, because a malformed tag
  value is skipped rather than flagged.
- **Phase B's covering requirement is stated** (F3), and Claim 23 was re-cited from an
  existence assert to the actual equality pin.

**Refuted — not folded.** The reviewer suspected GD-15 had already shipped inside
`0.42.0`, which would have made §D4 attach a changelog entry to a released decision.
Checked: `git log -S` returns nothing, HEAD contains no GD-15, and it is an uncommitted
working-tree edit from this session. Its presence in the plugin bundle is this session's
own sync run, not a merge. §D4 stands, and the verification is now recorded in it so the
question is not re-litigated.

**Open — for the human, not for a fourth fold:**

- **Does this plan ship standalone at all?** The reviewer's answer is *no — land it with
  COV04*, and the strongest reason is measured: `LINT_RULES.md` is a `framework/` path,
  so COV04 will force a **second** identical MINOR + ~100-file fanout. Two such PRs for
  one capability, to ship a field that no rule, audit or harness reads until the second
  one lands.
- **Residual specification gaps** if it does ship standalone: R2's MVP conformance assert
  names no host module and nothing would lock the key in the canonical template either;
  two references to a "§D2 table" the cut removed; a Pass-2 minor logged as folded that
  did not land in Phase A; `HANDOFF.md` and the vendored template mirrors own no phase.

**Result of Pass 3:** not ready — escalated.

### Pass 3a — 2026-08-26 — authoring gap-closure (NOT a review pass)

The scope question was answered by the founder: **keep the plans separate.** With that
settled, Pass 3's residual gaps were worth closing and are now closed:

- The measured **form table is restored** in §D2, resolving the two dangling "§D2 table"
  references and preserving the only record of why the block scalar was rejected.
- **R2's conformance check is specified concretely** as `tests/conformance/test_iplan_carrier.py`
  with two YAML-parsing asserts — and widened, because the canonical template was as
  unguarded as the MVP skeleton.
- **Phase A carries the guidance constraint** that Pass 2 logged as folded but which had
  not landed in the body.
- **The file lists are corrected:** the three vendored template/README copies are driven
  by the template edit rather than the version fanout, so they move to Phases A/C; Phase C
  now explicitly owns every plan-surface document including `HANDOFF.md`, and Phase D owns
  `CHANGELOG.md`.

**Result:** **implementation-ready with one stated caveat** — three independent passes
were run and the third's load-bearing items were either applied, refuted with evidence
(GD-15), or resolved by the founder's scope decision. No fourth pass was dispatched, per
the cap. A reader who wants a clean final pass should dispatch one before the PR opens;
nothing in the plan is known-open.

### Implementation — 2026-08-26

Implemented and verified, except the version bump (below).

- `tdd_ref` added to `IPLAN-TEMPLATE.yaml` (two of three entries — the third is left
  without it as the worked example of D3's optionality) and to the MVP skeleton's
  bare-list entry. Both parse; the guidance carries no `@tdd:` on a `tdd_ref` line, per
  the Phase A constraint.
- `tests/conformance/test_iplan_carrier.py` guards **both** templates. Mutation-tested:
  deleting the MVP carrier fails it, restoring it passes.
- `fullpath/golden_chain`'s IPLAN cites all three elements its sibling TDD declares —
  *covering*, per the parent design. The expected-warnings manifest was **re-derived by
  running the tier, not assumed**: it did not move.
- GD-16 recorded; layer README documents the three carrier rules; bundle mirror synced.
- Conformance 374 passed / 796 subtests; acceptance 64 passed; corpus lint delta zero.

**Withheld: the `framework/VERSION` bump, `CHANGELOG.md`, and the ~100-file fanout**
(§D4). The founder's standing instruction is not to bump, and `CLAUDE.md` requires
per-bump founder OK for the plugin fanout. Consequence to be explicit about: with
`framework/**` edited and no bump in the diff, **GATE-SPEC-E005 and E008 will fail this
PR**. The change is complete and verified locally; it is not mergeable until the bump
lands in the same diff.

Filed as issue #543 (the coverage gap this carrier serves).
