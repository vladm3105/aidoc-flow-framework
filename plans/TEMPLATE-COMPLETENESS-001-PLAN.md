# TEMPLATE-COMPLETENESS-001 Plan — three layer-template gaps as one framework MINOR

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | TEMPLATE-COMPLETENESS-001                                     |
| Type           | feature                                                       |
| Status         | PLANNED — 2026-08-28T00:00:00Z                                |
| Depends on     | GD-15 (YAML normative), GD-16 (`tdd_ref` carrier)             |
| Feeds          | #550, #551, #532                                              |
| Version impact | framework **MINOR** `0.43.0 → 0.44.0` (additive template keys) |

## Objective

Close three verified layer-template gaps in one framework release. Each is
evidence-complete on the tracker and each independently trips **GATE-SPEC-E005**
(Claim 1), so shipping them separately costs three version bumps, three ~120-file
fanouts, three `CHANGELOG.md` serialisation points and three per-bump founder grants.
Bundling converts that into one.

## Scope

**In:**

- **#550** — replace the **ten** hardcoded Python test paths across TDD and SPEC, and
  close the companion silence in `framework/TESTING_STRATEGY_TDD.md`.
- **#551** — give SPEC and TDD a `threshold_references` carrier.
- **#532** — GD-13's title and the `0.41.3` CHANGELOG enumeration.
- The fanout both sync scripts perform, a `GD-17` decision entry, and the docs of record.

**Out of scope (deferred):**

- **#552** (diagram slots, `metadata.validation:`) — **CUT at Pass 2.** The diagram half is
  not an additive template edit: SPEC's declared tag vocabulary is two values across four
  surfaces (Claim 21) and its third mandated kind has no tag, while EARS's allowlist is
  **empty** and DG02 is error-severity (Claim 22), so a tagged EARS slot would ship a
  template that fails the framework's own linter. Reaching `tools/sdd_doc_lint`,
  `LAYER_REGISTRY.yaml`, `DIAGRAM_STANDARDS.md` and a plugin SKILL is a different change
  with a different risk profile. Its own plan.
- **#553** (IPLAN self-description) — **CUT at Pass 2.** `IPLAN-LAYER-REVIEW-001-DESIGN.md`
  R8 places `title` in `metadata:` per the OKF D1 contract and is founder-gated on
  `OKF-CONFORMANCE-001` (Claim 23). Shipping `document_control.title` now either pre-empts
  that decision or lands two `title` fields. Blocked on the placement call, not on effort.
- **#540** (BRD 5-FR cap) — all three options touch `framework/**` and would ride this bump,
  but which option is a founder call.
- **#531** — `tests/`-only, needs no bump; its own plan.
- **#554**, **#555**, **#486**, **#487** — no bump, or absorbed by the corpus regen.
- All ⏸ PARKED issues (#438, #483, #543–#548).
- **Two defects discovered during this plan's review, filed separately rather than fixed
  here:** the stale `fw_prev` trap (Claim 19/20), filed as **#556** and since **fixed**, and EARS's `glossary:` being
  admitted to STRUCT01's required set while the template numbers five sections (Claim 18),
  filed as **#557**.

## Approach / Design

### D1 — Every addition nests inside an existing top-level section

**The invariant is not `total_sections`.** That key has exactly one consumer in the tree
and it is BRD-only (Claim 15). The two mechanisms that actually gate structure are:

- **STRUCT01's required-section set**, derived from top-level keys carrying `_size_target`
  and not marked `_required: false` / `_required_when_subtype:` (Claim 16). The count is
  never read.
- **The section-count gate**, which counts `# Section N:` comment headers in the template
  against the plugin creation skill's declared structure (Claim 17).
- **The acceptance harness's own derivation**, which requires **every top-level mapping key
  except `metadata`** and ignores `_size_target` entirely (Claim 27).

So the invariant this plan must hold is: **no new top-level key at all** — the third
derivation makes `_size_target` irrelevant, so a key added without one still reddens every
golden of that layer. Both additions nest inside existing sections, so all three hold.

⚠️ **V3 and V4 are blind to the third derivation.** For the acceptance tier the tripwire is
**V6**, not V4.

| # | Addition | Host (existing section) | New `_size_target` key? | New `# Section` header? |
| --- | --- | --- | --- | --- |
| 1 | SPEC `threshold_references` | `traceability:` — Claim 8 | no | no |
| 2 | TDD `threshold_references` | `traceability:` — Claim 25 | no | no |

`total_sections` values are left untouched, which is correct and consequence-free.

### D2 — The threshold carrier copies EARS exactly, and the issue quotes it wrongly

EARS already ships the settled form, **nested inside `traceability:`**, at
`EARS-TEMPLATE.yaml:384` (Claim 7). Its child key is **`items:`**, each entry
`{tag, category, value}`.

Issue #551's fix-shape snippet writes that block with a `tags:` child and a bare `- tag:`
list. **That is not what the file says** (Claim 7). Implementing the issue body verbatim
would invent a third shape — the exact failure #551 itself cites when rejecting the
consumer's proposed `spec_threshold_references`. Copy the file, not the issue.

### D3 — #550 covers ten paths across two files, not four

Claim 2 established the four `test_file:` values in TDD §4. Three more sit in TDD §3 under
a **different key name** (`file:`, Claim 3) and three more in SPEC's `tdd_contracts`
(`path:`, Claim 4). A fix scoped to the `test_file:` marker leaves six survivors and a
verification step that reports clean over them — this plan's own first draft did exactly
that. V2 is therefore class-scoped, not marker-scoped.

The `function:` / `test_function:` values alongside them are also pytest-shaped. They are
**in scope for the same pass**: leaving them re-pins the language one field over.

### D4 — #550 replaces values and adds a pointer; it adds no field

**Do not** add `language:` / `test_framework:` to `test_cases[]` — SPEC owns `language:`
(Claim 5) and IPLAN forbids re-pinning it (Claim 6). `TDD-MVP-TEMPLATE.yaml` is already
correct (Claim 10) and is the target shape.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | D3 (7 paths); D1 row 2 |
| `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` | D3 (3 paths); D1 row 1 |
| `framework/TESTING_STRATEGY_TDD.md` | new section: test paths derive from `@spec` `language:` |
| `framework/governance/DECISIONS.md` | GD-13 title fix (#532); new GD-17 |
| `framework/VERSION` | `0.43.0` → `0.44.0` |
| `CHANGELOG.md` | `0.41.3` entry enumerates all six surfaces (#532); new `0.44.0` entry |
| `platforms/claude-code-plugin/framework/layers/**` | vendored mirrors, by script (Claim 11) |
| `ROADMAP.md`, `plans/HANDOFF.md`, `plans/DECISIONS.md` | docs of record |

## Implementation sequence

### Task 1: #550 — language genericization across TDD and SPEC

- Replace all **ten** hardcoded paths (Claims 2, 3, 4) with the placeholder form, and
  genericize the adjacent pytest-shaped `function:` / `test_function:` values (D3).
- **Target form is `TDD-MVP-TEMPLATE.yaml`'s bare angle-bracket placeholder** (Claim 10) —
  `test_file: "<unit test path, per the @spec language>"`, `test_function: "<test function name>"`.
  **Do not** use the `# example (Python):` device: that works in `IPLAN-TEMPLATE.yaml` only
  because those entries are list-of-string commands, not mapping values (Claim 6). One form,
  not two.
- Genericize the seven pytest-shaped `function:` / `test_function:` values in the same pass
  (Claim 28) — leaving them re-pins the language one field over.
- Add the do-not-re-pin sentence to `test_cases._guidance` and to
  `tdd_contracts._guidance`.
- Add a short section to `framework/TESTING_STRATEGY_TDD.md` stating that test-file
  conventions derive from the `@spec` `language:` declaration. The file is currently
  silent on the subject (Claim 12) — without it the template change points at nothing.

### Task 2: #551 — threshold carriers

- Copy `EARS-TEMPLATE.yaml:384` in shape (D2, Claim 7) into `SPEC-TEMPLATE.yaml`
  `traceability:` (Claim 8) and `TDD-TEMPLATE.yaml` `traceability:` (Claim 25), under the
  same name `threshold_references` with an `items:` child.
- Add no `_size_target` to either block (D1).
- Leave `TDD-TEMPLATE.yaml:236` `thresholds:` untouched — it holds coverage gates, a
  different concept, and the name collision is why this gap survived (Claim 9).

### Task 3: #532 — doc accuracy

- Retitle GD-13 from "Two governance documents" to "Six authoring surfaces" (Claim 13).
  Body needs no change.
- **Correct forward, do not rewrite the released entry** — founder decision 2026-08-28,
  option (b). Extending the `0.41.3` CHANGELOG entry in place would rewrite the changelog of
  a **published release**: `framework/v0.41.3` is a non-draft, non-prerelease GitHub release
  on `8dccc315`, published 2026-08-24 (Claim 24). Instead, state the correction inside the
  new `0.44.0` entry: name all six GD-13 surfaces there and say explicitly that the `0.41.3`
  entry named two of them. Leave `CHANGELOG.md:38` untouched.
  *(An earlier draft argued the in-place edit was safe because the entry sits under
  `## [Unreleased]` at `CHANGELOG.md:13`. That inference was false — `[Unreleased]` heads
  the **project** stream (`v1.x.y`), and the framework spec is independently versioned and
  independently tagged, so the heading was never evidence about the framework stream.)*
- ⚠️ **Related but out of scope: issue #558.** Spec `0.42.0` and `0.43.0` are themselves
  untagged, and `framework/VERSION` never held `0.42.0`. That is a separate founder call and
  does **not** block this plan — but do not cut a `0.44.0` tag without reading #558 first.
- The GD-13 retitle (Claim 13) proceeds unaffected.

### Task 4: version bump and fanout

- **Order is load-bearing:** `framework/VERSION` → `scripts/sync-version-refs.sh` →
  `tools/sync-plugin-framework.sh` (Claim 11). Reversing it lands drifted bundled
  playbooks and a red bundle guard.
- **Do not hand-edit the framework-spec token in `docs/PARITY.md` before running the
  sync.** `fw_prev` is detected from `docs/PARITY.md` (Claim 19) and gates propagation to
  `CLAUDE.md`, `README.md`, both platform READMEs and a conformance literal. ⚠️ Both
  *(Both `CLAUDE.md` § "Durable traps" and the script's own header comment used to name
  `CLAUDE.md` as the source. **Fixed 2026-08-28 by #556** — Claim 20. Cite the `fw_prev`
  assignment by name, not by line: correcting that header moved it.)*
- Write `GD-17` in `framework/governance/DECISIONS.md` covering the three changes.
- Record the founder's per-bump grant as an audit-trail line in the commit message.

## Verification

| # | Check (command or observable) | Expected result | Maps to |
| -- | ---- | ---- | ---- |
| V1 | `grep -c '@threshold' framework/layers/06_SPEC/SPEC-TEMPLATE.yaml framework/layers/07_TDD/TDD-TEMPLATE.yaml` | both non-zero (was `0`/`0`) | Task 2 |
| V2a | `grep -nE '(test_file\|file\|path): "tests/' framework/layers/0[67]_*/[A-Z]*-TEMPLATE.yaml` | zero matches — all ten paths (Claims 2, 3, 4) | Task 1, D3 |
| V2b | `grep -nE '(function\|test_function): "test_' framework/layers/07_TDD/TDD-TEMPLATE.yaml` | zero matches — all seven function values (Claim 28) | Task 1, D3 |
| V3 | `grep -cE '^# Section [0-9]+:' framework/layers/06_SPEC/SPEC-TEMPLATE.yaml framework/layers/07_TDD/TDD-TEMPLATE.yaml` | unchanged (8 / 7) | D1 |
| V4 | For each edited template, the set of top-level keys carrying `_size_target` is unchanged | no new required section | D1, Claim 16 |
| V5 | `python3 -m pytest tests/conformance -q` | green | all |
| V6 | `python3 -m pytest tests/acceptance/deterministic -q` | green | all |
| V7 | `PYTHONPATH=tools python3 -m pytest tools/sdd_doc_lint/tests -q` | green | all |
| V8 | `pre-commit run --all-files` | clean | Task 4 |
| V9 | `diff -r framework/layers platforms/claude-code-plugin/framework/layers` | no drift | Task 4 |
| V10 | `cat platforms/*/FRAMEWORK_SPEC_VERSION` | both read `0.44.0` | Task 4 |
| V11 | the same `grep -oE 'ID_NAMING_STANDARDS\|TRACEABILITY\|auditor\|IPLAN-TEMPLATE\|requirements-analyst' \| sort -u \| wc -l` run over the **new `0.44.0`** CHANGELOG block | `5` tokens naming **6** surfaces — the regex matches `auditor` once for both playbooks (Claim 26), so the two figures are consistent | Task 3 |
| V11b | `git diff main -- CHANGELOG.md \| grep '^-'` | no deletions inside the `0.41.3` block — the released entry is untouched (option (b)) | Task 3 |
| V12 | `grep -n '^## GD-13' framework/governance/DECISIONS.md` | title says "Six authoring surfaces" | Task 3 |

## Docs to update

- [ ] `CHANGELOG.md` — `0.44.0` entry; plus the `0.41.3` correction (Task 3)
- [ ] `ROADMAP.md` — bullet
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — the bundling decision and the two Pass-2 cuts
- [ ] `framework/governance/DECISIONS.md` — GD-17
- [ ] `CLAUDE.md`, `README.md`, `docs/PARITY.md` — by `scripts/sync-version-refs.sh`

## Risks

| # | Risk | Likelihood | Mitigation |
| -- | ---- | ---- | ---- |
| R1 | The bump PR exceeds Rule 1's 3-surface cap and is unsplittable | **Certain** | Structural; needs the per-bump founder grant recorded in the commit message |
| R2 | An addition creates a new required section and reddens every existing instance of that layer | Medium | D1 nests both additions; **V4 and V3 catch the STRUCT01 and header-count derivations, V6 catches the acceptance-harness derivation (Claim 27) that both are blind to** |
| R3 | Implementing #551 from the issue body produces a third threshold shape | Medium | D2; copy `EARS-TEMPLATE.yaml:384`, not the issue's snippet |
| R4 | The fanout runs in the wrong order and lands drifted playbooks | Medium | Task 4 fixes the order; V9 detects it |
| R5 | An implementer pre-edits `docs/PARITY.md` and silently strands the gated block | **Low since #556** | Both narrative surfaces now name `docs/PARITY.md` (Claim 20). Task 4 restates it; the failure is still silent at exit 0, so the warning stays |
| R6 | #550's fix is scoped to one marker and leaves survivors — six under other **path** keys, or seven under the **function** keys one field over | **High** | D3 counts both classes; **V2a covers paths, V2b covers functions**. This plan's first draft made the path error and its second made the function error |
| R7 | Adding template keys reddens the acceptance tier | Medium | The fixtures are linted against the **live** templates, so "templates are not instances" does not decouple them; V6 is the check and the tier matches warnings as a bidirectional multiset, so any movement is visible |

## Claim ledger

| # | Claim | Symbol | Citation |
| -- | ---- | ---- | ---- |
| 1 | A `framework/**` change requires a `framework/VERSION` bump | `GATE-SPEC-E005` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:89 |
| 2 | TDD §4 hardcodes four Python `test_file:` paths | `test_file` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:165 |
| 3 | TDD §3 hardcodes three more under the key `file:` | `file` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:127 |
| 4 | SPEC hardcodes three more under `tdd_contracts.test_files` | `path` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:192 |
| 5 | SPEC owns the `language:` declaration | `language` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:97 |
| 6 | IPLAN forbids re-pinning a language and uses `# example (Python):` | `Do NOT re-pin a language here` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:133 |
| 7 | EARS's threshold carrier nests in `traceability:` and its child key is `items:`, not `tags:` | `threshold_references` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:384 |
| 8 | SPEC has a `traceability:` section with an `upstream:` block | `traceability` | framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:202 |
| 9 | TDD `thresholds:` holds coverage gates, not `@threshold:` citations | `thresholds` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:236 |
| 10 | The TDD MVP template is already genericized | `test_file` | framework/layers/07_TDD/TDD-MVP-TEMPLATE.yaml:25 |
| 11 | Two sync scripts perform the fanout | `sync-version-refs.sh` | scripts/sync-version-refs.sh:10 |
| 12 | `TESTING_STRATEGY_TDD.md` names no language or runner — blocks Task 1 | (absence) | PROBE: `grep -in -e python -e pytest -e jest framework/TESTING_STRATEGY_TDD.md` exits 1 |
| 13 | GD-13's title says "Two governance documents" while its body says six | `GD-13` | framework/governance/DECISIONS.md:202 |
| 14 | The `0.41.3` CHANGELOG entry is the block to extend | `0.41.2 → 0.41.3` | CHANGELOG.md:46 |
| 15 | `total_sections` has exactly one consumer and it is BRD-only | `test_total_sections_bumped` | tests/conformance/test_seed_contract.py:80 |
| 16 | STRUCT01's required-section set is derived from top-level keys carrying `_size_target` | `_size_target` | `tools/sdd_doc_lint/__init__.py:531` |
| 17 | The section-count gate counts `# Section N:` comment headers | `_template_numbered_count` | tests/conformance/platforms/test_skill_template_alignment.py:78 |
| 18 | EARS's `glossary:` carries `_size_target` and no `_required: false`, so STRUCT01 requires a section the template does not number | `glossary` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:401 |
| 19 | `fw_prev` is detected from `docs/PARITY.md`, not `CLAUDE.md` — #386 is fixed | `fw_prev="$(detect_version_in docs/PARITY.md` | scripts/sync-version-refs.sh:298 |
| 20 | **RESOLVED 2026-08-28 by #556.** The script header and `CLAUDE.md` both named `CLAUDE.md` as the `fw_prev` source; both now name `docs/PARITY.md` | `Corrected per #556` | scripts/sync-version-refs.sh:62 |
| 21 | SPEC's declared diagram-tag vocabulary is two values | `diagram_tags` | framework/registry/LAYER_REGISTRY.yaml:204 |
| 22 | EARS's diagram allowlist is empty, so any EARS `@diagram:` tag is a DG02 error | `_DIAGRAM_ALLOWED` | `tools/sdd_doc_lint/__init__.py:820` |
| 23 | R8 places IPLAN `title` in `metadata:` and is founder-gated on OKF D1 — line cited as of `docs/a2-discard-d0077`, which restores two void R-rows above it | `R8` | plans/IPLAN-LAYER-REVIEW-001-DESIGN.md:340 |
| 24 | Framework spec `0.41.3` **is a published release**, so an in-place edit rewrites shipped history — blocks Task 3's CHANGELOG half (resolved 2026-08-28 → correct forward in `0.44.0`) | `framework/v0.41.3` | PROBE: `gh release view framework/v0.41.3 --json tagName,isDraft,isPrerelease` returns non-draft, non-prerelease, on `8dccc315` |
| 25 | TDD has a `traceability:` top-level section carrying `_size_target` — the host for D1 row 2 | `traceability` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:300 |
| 26 | GD-13 enumerates six surfaces across **five** bullets — one bullet names both auditor playbooks | `playbooks/05_ADR/auditor.md` | framework/governance/DECISIONS.md:223 |
| 27 | A third required-section derivation exists and ignores `_size_target`: every top-level mapping key except `metadata` | `_required_when_subtype` | tests/acceptance/_harness.py:211 |
| 28 | TDD carries seven pytest-shaped `function:` / `test_function:` values alongside the paths | `function` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:128 |

## Review log

### Pass 1 — 2026-08-28 — self-review

- Drafted against source, not the issue bodies. Surfaced **D2**: #551's fix-shape snippet
  writes `tags:` where `EARS-TEMPLATE.yaml:384` writes `items:`. Implementing the issue
  verbatim would have invented a third shape.
- Surfaced the nesting requirement and hosted all additions inside existing sections.
- Claim 12 is an absence; written as `PROBE`, blocking Task 1 only.

**Result:** not ready — awaiting independent pass.

### Pass 2 — 2026-08-28 — independent

Seven load-bearing findings, all re-derived against source before folding. **Pass 2 raised
more findings than Pass 1, so scope was cut rather than folded** (fold discipline).

- **Scope cut — #552 removed.** The diagram half reaches `tools/sdd_doc_lint`
  (`_DIAGRAM_ALLOWED`, Claim 22), `LAYER_REGISTRY.yaml` (Claim 21), `DIAGRAM_STANDARDS.md`
  and a plugin SKILL. EARS's allowlist is **empty** and DG02 is error-severity, so a tagged
  EARS diagram slot would ship a template that fails the framework's own linter; SPEC's
  third mandated diagram kind has no declared tag at all. Not an additive template edit.
- **Scope cut — #553 removed.** R8 places IPLAN `title` in `metadata:` per OKF D1 and is
  founder-gated (Claim 23). Task 4 placed it in `document_control:`. Shipping now either
  pre-empts the decision or lands two `title` fields.
- **D1's rationale was wrong and V4 was not a tripwire.** The plan had built D1, R2 and V4
  on `total_sections`, which no code reads outside one BRD-only test (Claim 15). The real
  gates are STRUCT01's `_size_target`-derived set (Claim 16) and the `# Section N:` header
  count (Claim 17). The *design* survived; its stated reason and its verification did not.
  Both rewritten; V3 added.
- **#550 under-covered by more than half.** Four paths became ten across two files
  (Claims 2, 3, 4), and V2 was marker-scoped — it would have reported clean over six
  survivors. D3 added; V2 rewritten class-scoped.
- **Claim 16 of the prior draft was false and is deleted.** EARS numbers Sections 1-5
  *including* Document Control, so the claimed counting divergence does not exist. The real
  defect one field over — `glossary:` requiring a sixth STRUCT01 section the template does
  not number (Claim 18) — is filed separately, not fixed here.
- **Task 4's fanout guardrail protected the wrong file.** `fw_prev` is detected from
  `docs/PARITY.md` (Claim 19); #386 is fixed. `CLAUDE.md`'s durable trap and the script's
  own header (Claim 20) were both stale — filed as #556 and fixed on 2026-08-28.
- **Minor, folded:** Task 3 edits a historical CHANGELOG entry in place; permissible only
  because it is still under `## [Unreleased]` (Claim 24). Now stated.
- **Confirmed, no action:** D2 is correct and #551's snippet genuinely is wrong; blast
  radius is one vendored mirror per template with no Hermes copy; the surviving three tasks
  touch disjoint files apart from `CHANGELOG.md`.

**Result:** not ready — the cut needs a re-validating pass.

### Pass 3 — 2026-08-28 — independent

Five load-bearing findings and two minor, all re-derived against source before folding.
**Findings fell 7 → 5, and every one was a wiring or evidence defect rather than a design
defect — the three surviving tasks were not challenged.** This is the OPS-0066 cap; no
fourth pass was dispatched.

- **Claim 24 was a false inference, and it blocks half of Task 3.** The prior draft argued
  that rewriting the `0.41.3` CHANGELOG entry was safe because it sits under
  `## [Unreleased]`. `framework/v0.41.3` is a **published, non-draft, non-prerelease GitHub
  release** on `8dccc315` (2026-08-24). `[Unreleased]` heads the *project* stream; the
  framework spec is independently versioned and independently tagged, so that heading was
  never evidence about it. Claim 24 now records the true fact as a `PROBE`, and Task 3's
  CHANGELOG half is marked ⛔ founder-decision with two stated options. The GD-13 retitle is
  unaffected and proceeds.
  *This one was available at session start — `plans/HANDOFF.md` states the release
  explicitly — and was inferred past anyway.*
- **V11's `5` and Task 3's `six` looked contradictory and are not.** The regex matches
  `auditor` once for both playbooks, so 5 tokens report 6 surfaces (Claim 26). V11 was also
  the one verification step delegating its command to an issue body; it is now inline and
  self-contained, and states the reconciliation.
- **D1's invariant was still incomplete.** A **third** required-section derivation exists in
  `tests/acceptance/_harness.py:211`: it requires every top-level mapping key except
  `metadata` and ignores `_size_target` entirely (Claim 27). So a top-level key added
  *without* `_size_target` passes V3 and V4 and still reddens every golden of that layer.
  D1's invariant is now "no new top-level key at all", and R2 re-points at **V6** as the
  tripwire for that derivation. *Pass 2 corrected this same class of error once already —
  a design decision defended by the wrong gate.*
- **Task 1 reproduced R6 one field over.** D3 put the pytest-shaped `function:` /
  `test_function:` values in scope, but V2 matched path keys only — a marker-scoped check
  over a class-scoped deliverable, which is the exact defect R6 exists to prevent. Split
  into **V2a** (ten paths) and **V2b** (seven function values, Claim 28); R6 raised to
  High and reworded to name both classes.
- **Task 1 also specified two incompatible target forms.** The `# example (Python):` device
  works in `IPLAN-TEMPLATE.yaml` only because those entries are list-of-string commands,
  not mapping values. Settled on one form: `TDD-MVP-TEMPLATE.yaml`'s bare angle-bracket
  placeholder (Claim 10), which D4 already named as the target shape.
- **D1 row 2 and Task 2 both cited Claim 9 for TDD's host section**, which asserts something
  else (that `thresholds:` holds coverage gates). A post-renumbering wiring defect the
  citation gate cannot catch, because Claim 9's own citation is valid. Added Claim 25 for
  the real host at `TDD-TEMPLATE.yaml:300` and re-pointed both references.
- **Minor, folded:** the two deferred defects now carry their issue numbers (#556, #557),
  discharging the capture-on-the-tracker rule.
- **Minor, not folded:** R1's "unsplittable" argument never states the real fanout count
  (`platforms/*/FRAMEWORK_SPEC_VERSION`, 52 SKILL frontmatters, `docs/SKILL_AUTHORING.md`,
  a conformance literal). V8/V9 surface these, so nothing ships broken; recorded rather
  than fixed, to avoid growing the plan at the cap.
- **Confirmed, no action:** MINOR is the correct grade (`GATE-SPEC-E002` permits minor at
  C2); R7's acceptance reasoning is correct and the fixtures do lint against live
  templates; the three-task bundle remains disjoint apart from `CHANGELOG.md`; no residue
  of #552 or #553 survives anywhere; ledger IDs are unique and every prose pointer resolves.

**Result:** not ready pending the escalated decision — see the amendment below.

### Amendment — 2026-08-28 — founder decision applied (NOT a review pass)

Pass 3 was the OPS-0066 cap, so rather than dispatch a fourth pass the one open item was
escalated. The founder resolved it as **option (b): correct forward inside the new `0.44.0`
entry; do not rewrite the released `0.41.3` entry.** Folded into Task 3, Claim 24 and V11,
with **V11b** added to prove the released entry is untouched.

Also recorded while folding: **#558** — spec `0.42.0` and `0.43.0` are themselves untagged,
and `framework/VERSION` never held `0.42.0`. That is a separate founder call. It does not
block this plan, but it means a `0.44.0` tag should not be cut without reading it.

**Honest limit on this result:** no confirming pass ran against this amendment, because the
pass cap was already reached. The amendment is subtractive — it removes an option and
narrows a task — and adds one verification step. Nothing in Tasks 1, 2 or 4 changed.

**Result:** ready for its plan PR. Ledger has 28 rows and no `UNVERIFIED`; three review
cycles ran (1 self + 2 dispatched independent); every finding is folded and the sole
escalated decision is resolved.
