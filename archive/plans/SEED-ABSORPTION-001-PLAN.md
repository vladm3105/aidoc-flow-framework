# SEED-ABSORPTION-001 Plan — seed→SDD absorption contract, BDD acceptance pairing, produced-artifact ID hygiene

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | SEED-ABSORPTION-001                                          |
| Type           | feature                                                      |
| Status         | PLANNED — 2026-07-24T00:00:00Z                               |
| Depends on     | FRWK-REVIEW-003 T3 if that plan lands first (see R3)         |
| Feeds          | corpus regeneration; `plans/FRAMEWORK-TODO.md` residuals     |
| Version impact | framework **MINOR** (additive); GATE-SPEC C2. Absolute numbers deliberately not pinned, per `PLAN_STANDARD.md` |

## Objective

Close three gaps in the `framework/` spec surfaced by founder review on
2026-07-24. **(A)** The spec names a `seed/` input tier but defines no contract
over it: nothing requires the SDD chain to account for what the seed says, and
nothing forbids "fixing" the seed when an audit finds a gap. This plan makes the
seed **frozen historical input** and requires every seed claim to be **absorbed
into the chain or explicitly rejected/deferred inside it**, with the disposition
recorded in the BRD. **(B)** Templated placeholder element IDs
(`BDD.01.03.xxxx`) are legitimate in the layer templates and README snippets —
they are the *shape* of a future ID — but must never survive into a **produced
document artifact**, where a real hex ID (`BDD.01.03.d7a2`) is required. That
prevention already exists and blocks (`ID03`/`ID01`, both error-severity); what
is missing is a regression fixture pinning it, so it cannot silently rot.
**(C)** BDD is specified as "executable
acceptance scenarios" that nothing is required to execute: `COV02` accepts a
scenario realized by **SPEC or TDD**, so a scenario can satisfy coverage with
zero tests — and the canonical corpus ships **16 of 31 scenarios realized by
nothing**, a state conformance currently *pins* as expected.

## Scope

**In:**

- A normative seed→SDD contract (`framework/governance/SEED_CONTRACT.md`),
  its BRD carrier section, and the BRD playbook checks that enforce it.
- A `SEED01` structural lint rule + the audit-side completeness check, with the
  deterministic/semantic split stated explicitly.
- A regression fixture + test locking the existing guarantee that a **produced
  artifact** carrying a templated placeholder ID (`TYPE.NN.SS.xxxx`,
  `TYPE.01.03.xxxx`) is rejected by `ID03`/`ID01`; plus one documenting sentence
  in `LINT_RULES.md` / `ID_NAMING_STANDARDS.md` making the guarantee
  discoverable. **Templates and READMEs are not changed.**
- A normative BDD→acceptance-test pairing contract and an `ACC01` lint rule that
  is **case-scoped**, not document-scoped (see Part C — the document-scoped form
  is provably vacuous against the current corpus).
- Remediation attempt for the 16 orphaned corpus scenarios **through framework
  skills only** (`doc-tdd-audit` → `doc-tdd-fixer`), never by hand-editing
  artifacts; with the realistic expectation that the blocker is upstream.

**Out of scope (deferred):**

- Changing `COV02` / `realizing_layers` semantics. `ACC01` is additive;
  mutating the existing OR-map would silently re-grade every consumer corpus.
- A machine parser for seed prose (claim extraction). Ledger *completeness*
  stays an audit-lens judgement; only ledger *structure* is linted.
- Promoting `ACC01` to `error` in `build` mode. It lands `warning`/`error`
  matching `COV02`'s mode split; escalation is a later call once corpora are clean.
- Making `seed_disposition:` a *required* BRD section. It ships
  `_required: false` (see Part A); requiring it is a separate, breaking change.
- **Any change to the layer templates or README placeholder examples.** Per
  founder direction (2026-07-24) the templated `xxxx` form is correct there — it
  is an example of a future ID. Only produced artifacts are constrained.
- Extending the seed contract to `chg/` (the second human-input tier).
- A `.feature` Gherkin emitter for BDD scenarios.
- Authoring the SPEC coverage the 16 orphan scenarios lack (Task 7 finding).

## Approach / Design

### Part A — the seed contract

The spec mentions the seed three times, all descriptively
(`framework/README.md:122` inputs row; `framework/docs/AIDOC.md:17` tier
diagram; `framework/docs/AIDOC.md:25` tier table).
`framework/layers/01_BRD/README.md` — the document governing the layer the seed
feeds — never mentions it, and BRD carries `required_tags: []`
(`framework/registry/LAYER_REGISTRY.yaml:25`), so the layer has no declared
upstream of any kind. The result: seed content that never reaches the chain is
invisible, and the cheapest way to "resolve" an audit finding is to edit the
seed until the gap disappears.

New `framework/governance/SEED_CONTRACT.md` states three rules:

1. **Frozen input.** `<project>/seed/` is historical input. Once the first BRD
   of a cycle is authored, seed files are not edited to resolve findings. A
   finding of the form "the seed says X, the chain does not" is resolved **in
   the BRD**, never by amending the seed. New human input arrives through
   `<project>/chg/`, which already has a gate.
2. **Total disposition.** Every claim in the seed has exactly one disposition in
   the BRD set of that cycle: `absorbed` (names ≥1 BRD element ID),
   `rejected` (rationale), or `deferred` (rationale + target cycle).
3. **BRD is the absorption point.** A seed claim first appearing at PRD or
   later, with no BRD row, is a gap — not a shortcut.

**Carrier + backward compatibility.** A new `seed_disposition:` section in
`BRD-TEMPLATE.yaml`, declared **`_required: false`**. This is load-bearing, not
a detail: two independent enforcers derive "required sections" from the template
body — STRUCT01 at `tools/sdd_doc_lint/__init__.py:1365` over
`_load_section_targets` (`:441`), and the stricter acceptance harness at
`tests/acceptance/_harness.py:43`, which requires every top-level dict section
except `metadata`. Without the marker, the section's mere existence makes every
already-authored BRD — including `examples/url-shortener/docs/01_BRD/BRD-01.md`
— emit a STRUCT01 **error** and breaks the BRD golden acceptance test. Both
enforcers honour `_required: false` (`__init__.py:449`, `_harness.py:46`), the
precedent being PRD's `component_decomposition`. The section is additive for
existing corpora and authored going forward.

**Placement.** Appended as a new trailing section **§16**, after §15 Glossary
(`framework/layers/01_BRD/BRD-TEMPLATE.yaml:978`), with `total_sections`
(`:29`) moved 15 → 16. It is deliberately *not* placed next to `project_scope:`
(`:385`): section numbers are ordinal in this template and the `section_id` is a
**hash input** for element IDs (`framework/governance/ID_NAMING_STANDARDS.md:71`),
so inserting at §5/§6 would renumber §7–§15 and invalidate the section segment
of every `BRD.NN.07.*` element ID and every downstream `@brd:` citation. BRD §7
is separately load-bearing in the linter's FR scanner and `rehash --check`
extraction boundary. `out_of_scope:` (`:408`) stays a scope declaration; a
deferred seed claim SHOULD also appear there, and the ledger row is what makes
that deferral traceable to its input.

**Enforcement split** (stated inside the contract, so the gate is not read as
stronger than it is):

| Question | Enforcer |
| --- | --- |
| Is every ledger row well-formed; does each `absorbed` row's target element resolve? | `SEED01`, deterministic lint |
| Did the ledger *miss* a claim the seed makes? | BRD auditor lens (new C8) — requires reading prose, not machine-checkable |

### Part B — prevent templated IDs in produced artifacts

The `xxxx` token has two jobs, and the founder's direction (2026-07-24) fixes
which one is in scope:

- **In templates and README snippets it is correct.** `TYPE.NN.SS.xxxx`
  (`framework/governance/ID_NAMING_STANDARDS.md:203`,
  `framework/governance/TAG_SYNTAX.md:23`) and a skeleton `id: BDD.01.03.xxxx`
  are the *shape* of a future ID. These are **not touched.**
- **In a produced document artifact it is a defect** — a real artifact must
  carry a real hex ID (`BDD.01.03.d7a2`), never the templated form.

The prevention already exists and blocks. `ID03` (error,
`tools/sdd_doc_lint/__init__.py:642`) rejects any element-id-shaped token that
fails `id_patterns.element` (`framework/registry/LAYER_REGISTRY.yaml:216`,
which requires 4–8 lowercase hex) — verified against a probe artifact carrying
`BDD.01.03.xxxx` (fully templated hash), `BDD.NN.03.xxxx` (templated doc number
too), in an `id:` declaration, in free prose, and in a table cell: **all three
positions flagged.** The `@`-tag citation form `@bdd: BDD.01.03.xxxx` is caught
by `ID01` (error, `tools/sdd_doc_lint/__init__.py:594`). `PH01` deliberately
stays silent on `.`-preceded hash runs (`(?<!\.)\bx{3,}\b`,
`tools/sdd_doc_lint/__init__.py:157`) and leaves them to `ID03` — so the two
rules do not double-report, and `ID03`/`ID01` fully own this.

So item 3 needs **no template change and no new rule** — it is already enforced.
The gap is that the guarantee is not **pinned**: the acceptance suite has a
negative-fixtures pass (`tests/ACCEPTANCE.md:305`), but its nearest fixture
`brd-broken-tags.md:26` exercises a *different* malformed shape (3-segment
`BRD.01.aaaa`), not the templated `TYPE.NN.SS.xxxx`. A refactor of the id
scanner could silently stop catching the templated form and no test would fail.

Fix (deliberately minimal — the "N fixes for N issues" rule, `CLAUDE.md`
§Durable conventions):

1. A negative fixture under `tests/acceptance/fixtures/negative/` carrying a
   templated placeholder ID in all three positions (declaration, `@`-tag
   citation, prose), with the expected `ID03`/`ID01` codes documented in the
   fixture header the way the sibling fixtures already are.
2. A conformance assertion that running the linter over that fixture emits
   `ID03` **and** `ID01` and does not pass.
3. One sentence in `framework/governance/ID_NAMING_STANDARDS.md` and the
   `ID03` row's contract note in `LINT_RULES.md`: *a produced artifact must
   carry real element IDs; the templated `TYPE.NN.SS.xxxx` placeholder is valid
   only in templates and illustrative snippets, and `ID03`/`ID01` reject it in
   any authored document.*

The templated-ID counts in the templates (`.xxxx` × BRD 28, PRD 20, EARS 18,
ADR 14, SPEC 11, TDD 10, BDD 7, IPLAN 3) and the README snippets are recorded
here only as a **non-regression baseline** — V6 asserts they are unchanged.

### Part C — acceptance pairing

`framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:18` calls BDD "executable acceptance
scenarios"; `framework/layers/04_BDD/README.md:26` then says QA-staging-only, do
not run in CI; `framework/TESTING_STRATEGY_TDD.md:63` delegates execution to TDD
("TDD does NOT create new test scenarios… maps existing BDD scenarios"). Nothing
closes the loop: `COV02` treats BDD's realizing set as `("SPEC", "TDD")` and
passes an element cited by **either** (`tools/sdd_doc_lint/__init__.py:2208`,
map at `:2008`, normative source `framework/registry/LAYER_REGISTRY.yaml:231`).
A scenario designed-for but never tested is coverage-clean.

The live corpus shows the cost: `python -m sdd_doc_lint
examples/url-shortener/docs/` emits **16 `COV02` warnings**, and
`tests/conformance/test_coverage_engine.py:103` *asserts* that count with a
docstring deferring remediation to "a separate corpus/skill follow-up".

**`ACC01` must be case-scoped.** The cheap implementation — reusing
`_element_realizing_citers(graph, elem, ("TDD",))`
(`tools/sdd_doc_lint/__init__.py:2015`) — returns **citer documents**, so it
would mean "some TDD document mentions this scenario anywhere". The corpus
already contains the loophole in finished form:
`examples/url-shortener/docs/07_TDD/TDD-01.md:206` is a single §4 traceability
line citing all 15 scenarios at once. Under a document-scoped rule, appending
the 16 orphan IDs to that one line would drive `COV02` and `ACC01` to zero with
**no test case authored** — precisely the vacuous pass the directive exists to
close. So `ACC01` reads the TDD carrier fields instead:

- `test_mapping.scenarios[].bdd_scenario` (`TDD-TEMPLATE.yaml:86`), and
- `e2e_tests.cases[].bdd_ref` (`:165`).

A BDD scenario is *paired* when ≥1 TDD **test case or mapping entry** names it
through one of those fields. Citations appearing only in the §4 traceability
block do not pair. This is **new parsing over the rendered TDD document**, not a
reuse of the existing realization primitive — the plan states the added cost
rather than claiming "an enforcement contract over an existing shape". Mode
split, `_BACKWARD_ORACLE_LAYERS` gating, and the `reuse: referenced` exemption
(`__init__.py:2205`) mirror `COV02`.

Other design points:

- **Registry.** New `acceptance_layers: {BDD: [TDD]}` block, sibling to
  `realizing_layers`, which is **not** touched — changing it would break the
  pinned assertion at `tests/conformance/test_coverage_engine.py:103` and
  re-grade consumer corpora. The additive block trips neither existing guard:
  `tests/conformance/platforms/test_realizing_layers_registry.py:21` reads only
  `realizing_layers`, and `tests/conformance/test_registry.py:28` uses `assertIn`
  for top-level keys.
- **Naming.** "Acceptance" is already taken in this repo — `tests/ACCEPTANCE.md`
  is the plugin's pre-deployment methodology (`framework/README.md:129`) and
  `tests/acceptance/` is the release-gate suite. `LINT_RULES.md` and the registry
  comment each carry one disambiguating sentence: `ACC01` / `acceptance_layers`
  govern BDD-scenario→TDD-case pairing inside a *project's* chain, not the
  framework's own acceptance harness.
- **Expected finding delta.** Under the document-scoped reading the delta would
  be zero (the 15 covered scenarios are cited by both SPEC and TDD, the 16
  uncovered by neither). Under the case-scoped rule the delta is **not**
  knowable from the current measurement — some of the 15 may be cited only in
  the §4 block. T6 measures it before asserting anything, and the conformance
  fixture (V4) is what proves the loophole is closed.

### Governance

All three parts edit `framework/**` → GATE-SPEC
(`framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:48`). Additive ⇒ SemVer
**minor**, change level **C2** (`:60`, `:94`). Entry obligations:
`framework/VERSION` bump (E005, `:89`), `CHANGELOG.md` (E008, `:92`), both
platforms' `FRAMEWORK_SPEC_VERSION` re-declared + conformance green (E006/E007).
W003 applies — Parts A and C change agent-facing authoring guidance, so the
`SECURITY_REVIEW.md` checklist is carried. Recorded as **GD-08**
(`framework/governance/DECISIONS.md:16` shows GD-07 as the highest existing).

**Two sync surfaces, not one.** Beyond the vendored linter
(`tools/sdd_doc_lint/sync-vendored.sh:14`, four `.py` files), the plugin bundles
a byte-identical copy of `framework/`'s `layers`, `governance`, `registry` and
`playbooks` subtrees, asserted at
`tests/conformance/platforms/test_plugin_framework_bundle.py:61` and re-synced by
`tools/sync-plugin-framework.sh`. Every edit to `framework/governance/**` (Parts
A, B doc-note, C) lands inside those subtrees, so `sync-plugin-framework.sh` runs
in each PR that touches them. Part B's fixture + test are under `tests/`, outside
the bundle.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `framework/governance/SEED_CONTRACT.md` | The normative seed tier: frozen input, total disposition, BRD as absorption point |
| `tests/conformance/test_seed_contract.py` | Guards the contract doc + the BRD template carrier section |
| `tests/acceptance/fixtures/negative/brd-templated-ids.md` | Part B fixture — a produced artifact carrying `TYPE.NN.SS.xxxx` in declaration / `@`-tag / prose |
| `tests/conformance/test_templated_id_rejected.py` | Part B — asserts the linter emits `ID03` + `ID01` over that fixture |
| `tests/conformance/test_acceptance_pairing.py` | Guards `ACC01` + `acceptance_layers` registry/linter sync |

### Modified

| Path | Change |
| ---- | ------ |
| `framework/governance/DECISIONS.md` | GD-08 — seed is frozen historical input; absorption is total |
| `framework/governance/README.md` | Index row for `SEED_CONTRACT.md` |
| `tests/conformance/test_governance.py` | `EXPECTED_FILES` gains `SEED_CONTRACT.md` — the set is asserted **exactly** (`:70`), so omitting this turns V1 red |
| `framework/governance/LINT_RULES.md` | `SEED01`, `ACC01` (+ naming-disambiguation sentence); `ID03`/`ID01` contract note on templated-ID rejection |
| `framework/governance/ID_NAMING_STANDARDS.md` | One sentence: templated `TYPE.NN.SS.xxxx` is valid only in templates/snippets; `ID03`/`ID01` reject it in a produced artifact |
| `framework/layers/01_BRD/BRD-TEMPLATE.yaml` | `seed_disposition:` §16 (`_required: false`); `total_sections` 15→16. **No placeholder edits** |
| `framework/layers/01_BRD/BRD-MVP-TEMPLATE.yaml` | Skeleton row for `seed_disposition:` |
| `framework/layers/01_BRD/README.md` | "Seed input" section pointing at the contract |
| `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | Acceptance-criteria guidance on the BDD map |
| `framework/layers/04_BDD/README.md` | Acceptance-pairing note (Part C); no placeholder/ID edits |
| `framework/layers/07_TDD/README.md` + `framework/TESTING_STRATEGY_TDD.md` | Pairing contract is normative, not advisory |
| `framework/registry/LAYER_REGISTRY.yaml` | New `acceptance_layers` block |
| `framework/playbooks/01_BRD/business_analyst.md` | C8 — author the seed-disposition ledger |
| `framework/playbooks/01_BRD/auditor.md` | C8 — ledger completeness against the seed |
| `framework/playbooks/07_TDD/qa_lead.md` | Check: every BDD scenario paired to a test case |
| `tools/sdd_doc_lint/__init__.py` (+ 2 vendored copies) | `SEED01`, `ACC01` |
| `platforms/claude-code-plugin/framework/**` | Re-synced via `tools/sync-plugin-framework.sh` (byte-identity guard) |
| `tests/conformance/test_coverage_engine.py` | Docstring at `:103` names `ACC01` as owner of the pairing half |
| `framework/VERSION`, `CHANGELOG.md`, `ROADMAP.md`, both `FRAMEWORK_SPEC_VERSION` | MINOR bump + records |

## Implementation sequence

Sequential PRs. Governance PRs keep to ≤3 doc surfaces (`CLAUDE.md`
§"Governance PR discipline" Rule 1); each carries the mandatory pre-push
adversarial agent dispatch (Rule 2). Every PR touching
`framework/{layers,governance,registry,playbooks}` ends with
`bash tools/sync-plugin-framework.sh`.

### Task 1 (T1): Seed contract + GD-08 — governance PR

- Author `framework/governance/SEED_CONTRACT.md` (3 rules + the enforcer table).
- `framework/governance/DECISIONS.md` GD-08; `governance/README.md` index row;
  **`tests/conformance/test_governance.py` `EXPECTED_FILES`**.
- **Test-first:** `tests/conformance/test_seed_contract.py` asserting the
  contract exists, is indexed, and names all three rules — failing first.

### Task 2 (T2): BRD carrier — `seed_disposition:` §16

- Append `seed_disposition:` after §15 Glossary with `_required: false`,
  `_guidance`, `_example` (real hex IDs), `_antipatterns`; `total_sections` →16.
- **Test-first:** extend `test_seed_contract.py` to assert the section exists,
  carries `_required: false`, and that `_example` rows use only the three legal
  dispositions. Then run `python -m unittest discover tests/acceptance` — the
  BRD golden (`tests/acceptance/deterministic/test_layer_brd.py:23`) must stay
  green, which is the machine-checkable proof the section is non-breaking.
- `framework/layers/01_BRD/README.md` gains a "Seed input" section.

### Task 3 (T3): `SEED01` + BRD playbook checks

- **Test-first:** linter fixtures for a malformed row and an `absorbed` row
  whose target element does not resolve.
- Implement `SEED01`; `sync-vendored.sh`; `LINT_RULES.md` row.
- `business_analyst.md` C8 (author the ledger) + `auditor.md` C8 (completeness
  against the seed — explicitly a reading judgement).

### Task 4 (T4): Freeze the example seed

- `examples/url-shortener/seed/initial-requirements.md:24` — replace the stale
  "cleared pending regeneration" note with the freeze marker. This is the
  **only** seed edit this plan makes, and it changes no claim.

### Task 5 (T5): Lock the templated-ID prevention (Part B)

- **Test-first:** author `tests/acceptance/fixtures/negative/brd-templated-ids.md`
  — a produced artifact carrying `BDD.01.03.xxxx` in an `id:` declaration, in an
  `@bdd:` citation, and in prose; header documents the expected `ID03`/`ID01`
  codes (mirroring `brd-broken-tags.md`). Add
  `tests/conformance/test_templated_id_rejected.py` asserting the linter emits
  both codes and does not pass. It must be red only if the prevention is ever
  removed — today it passes, proving the guarantee already holds.
- Add the discoverability sentence to `ID_NAMING_STANDARDS.md` and the `ID03`
  contract note to `LINT_RULES.md`. **No template or README edit.**
- `sync-plugin-framework.sh` (the two governance docs are in the bundle).

### Task 6 (T6): Acceptance pairing contract + `ACC01`

- **Test-first:** `tests/conformance/test_acceptance_pairing.py` — a scenario
  named only in a §4 traceability block yields `ACC01`; one named by a
  `bdd_scenario`/`bdd_ref` field does not. This fixture is the proof the
  vacuous-pass loophole is closed.
- Registry `acceptance_layers` + disambiguation comment; implement the
  case-scoped `ACC01`; `sync-vendored.sh`; `LINT_RULES.md` row.
- **Measure** the corpus delta and record it in the PR body before touching any
  assertion.
- Normative pairing wording in `04_BDD/README.md`, `07_TDD/README.md`,
  `TESTING_STRATEGY_TDD.md`, `TDD-TEMPLATE.yaml`; `07_TDD/qa_lead.md` check.

### Task 7 (T7): Corpus remediation attempt — expected to surface a SPEC gap

The 16 orphans are un-**designed**, not merely un-tested:
`examples/url-shortener/docs/07_TDD/TDD-01.md:66` scopes itself to "the **15**
Mapping-Store BDD scenarios (SPEC-01 §8)", the corpus has exactly one SPEC, and
TDD's declared upstream includes `spec`. So dispatching the TDD skills asks them
to author tests for scenarios no SPEC specifies.

- Dispatch `doc-tdd-audit` then `doc-tdd-fixer`
  (`platforms/claude-code-plugin/skills/doc-tdd-{audit,fixer}/SKILL.md`) against
  `examples/url-shortener/docs/07_TDD/`.
- **Expected outcome:** a SPEC-coverage finding, not 16 new test cases. In that
  case file the gap in `plans/FRAMEWORK-TODO.md`, leave
  `test_coverage_engine.py:103` at 16, and stop. **No hand-edits**
  (`CLAUDE.md:93`).
- Reconcile with `CLAUDE.md:19` (the corpus is regenerated wholesale after
  framework changes, so corpus-remediation findings are deferred to that regen):
  T7 is a *probe* that produces the finding, not a substitute for the regen.
- Amend the pinned count only if the skills actually produced the pairing.

### Task 8 (T8): Version, records, platforms

- `framework/VERSION` MINOR bump; both `FRAMEWORK_SPEC_VERSION`;
  `CHANGELOG.md`; `ROADMAP.md`; `plans/HANDOFF.md`; `plans/DECISIONS.md`.
- Carry `SECURITY_REVIEW.md` (GATE-SPEC W003) for T1/T2/T6 agent-facing wording.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python -m unittest discover tests/conformance` | green, including the 4 new/edited guards and `test_governance.py`'s exact-set assertion | all parts |
| V2 | `python -m unittest discover tests/acceptance` | green — proves `seed_disposition:` did not break the BRD golden. **Not covered by V1** | T2 |
| V3 | `PYTHONPATH=tools python3 -m sdd_doc_lint examples/url-shortener/docs/` | vs. baseline **16 COV02 / 6 STY02 / 5 REFGRAN01 / 1 TH-RES-001 error**: no new STRUCT01; `ACC01` count recorded, not predicted. After T7: COV02/ACC01 ↓; **STY02 may rise** if TDD-01 grows — the response is a TDD split, never a budget weakening | Parts A+C, corpus cross-check (`CLAUDE.md:150`) |
| V4 | `test_acceptance_pairing.py` fixture: scenario named only in a §4 traceability block | `ACC01` fires (`warning` in build, `error` in gate-code) | Part C loophole closed |
| V5 | `test_templated_id_rejected.py` over the new negative fixture | `ID03` **and** `ID01` fire; the fixture does not pass — the prevention holds | Part B |
| V6 | `git diff --stat framework/layers/` | **no template or layer-README change** — Part B touches only `tests/` + two governance docs; the `.xxxx` counts (BRD 28/PRD 20/EARS 18/ADR 14/SPEC 11/TDD 10/BDD 7/IPLAN 3) are unchanged | Part B non-regression |
| V7 | After staging: `bash tools/sdd_doc_lint/sync-vendored.sh && git diff --exit-code` | re-running the sync produces **no further** diff (the in-PR diff is expected; this checks convergence) | T3, T6 |
| V8 | After staging: `bash tools/sync-plugin-framework.sh && git diff --exit-code` | same, for the plugin's bundled `framework/` | all PRs touching layers/governance/registry/playbooks |
| V9 | `python ~/.claude/skills/verified-planning/check_plan.py plans/SEED-ABSORPTION-001-PLAN.md` | `ok` | plan gate |
| V10 | GATE-SPEC pre-gate checklist (`GATE-SPEC_FRAMEWORK.md:65`) | E001–E008 pass; W003 addressed | governance |

## Docs to update

- [ ] `CHANGELOG.md` — MINOR entry (seed contract, `SEED01`, templated-ID lock, `ACC01`)
- [ ] `ROADMAP.md` — recently-shipped bullet
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — Part B is a regression-lock, not a template change
      (founder direction); the decision not to mutate `realizing_layers`; the
      case-scoped `ACC01`
- [ ] `framework/governance/DECISIONS.md` — GD-08
- [ ] `framework/VERSION`, `platforms/*/FRAMEWORK_SPEC_VERSION`
- [ ] `plans/FRAMEWORK-TODO.md` — the T7 SPEC-coverage gap; close any superseded item

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | `ACC01` fires broadly on consumer corpora that legitimately design-without-testing | med | Ships `warning` in `build` (only `error` in `gate-code`), same split as `COV02`; escalation deferred |
| R2 | Item 3 is read as "rewrite the template placeholders" (my original draft), touching ~10 template + README files for no functional gain | med | Founder direction (2026-07-24): templates are correct. Part B changes only `tests/` + two governance docs; V6 asserts no `framework/layers/` change |
| R3 | Collides with in-flight `plans/FRWK-REVIEW-003-PLAN.md` — its T3 edits `LAYER_REGISTRY.yaml:230`, the very comment block `acceptance_layers` appends to | med | Part B no longer touches templates/READMEs, so the only overlap is the registry comment block (T6 vs FRWK-REVIEW-003 T3); land after it if it proceeds. That plan is still `PLANNED` (`:7`) and untracked, so if it is dropped this plan is independent — merge-order only |
| R4 | `SEED01` is read as proving seed completeness, which it cannot do | med | The contract carries the enforcer table; auditor C8 owns completeness |
| R5 | T7's skills cannot pair the orphans; pressure to hand-edit the corpus | high | T7 *expects* a SPEC-coverage finding; stops and files the gap; `CLAUDE.md:93` forbids the hand-edit |
| R6 | Freezing the seed blocks a genuinely-wrong input from ever being corrected | low | `chg/` is the gated channel for new human input; the contract names it |
| R7 | The case-scoped `ACC01` needs new TDD-document parsing, larger than reusing the realization primitive | med | Confined to two named carrier fields; V4's fixture defines the contract before implementation |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The spec names `seed/` only as an inputs row | `<project>/seed/` | framework/README.md:122 |
| 2  | Seed is a committed human-input tier alongside `chg/` | `seed/, chg/` | framework/docs/AIDOC.md:17 |
| 2b | …and again in the tier table (third and last mention) | `human-authored seeds + change requests` | framework/docs/AIDOC.md:25 |
| 3  | BRD declares no required upstream tags | `required_tags: []` | framework/registry/LAYER_REGISTRY.yaml:25 |
| 4  | BRD template has a `project_scope:` section (rejected insertion point) | `project_scope:` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:385 |
| 5  | `out_of_scope` is a scope declaration, not seed provenance | `out_of_scope:` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:408 |
| 5b | §15 Glossary is the last numbered section — §16 is the safe append point | `# Section 15: Glossary` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:978 |
| 5c | `total_sections` must move 15 → 16 | `total_sections: 15` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:29 |
| 5d | `section_id` is a hash input, so renumbering invalidates element IDs | `"{doc_id}:{section_id}:{title}:{description}"` | framework/governance/ID_NAMING_STANDARDS.md:71 |
| 6  | Element ID pattern requires 4–8 lowercase hex (so `aaaa` would pass, `yyyy` would not) | `element:` | framework/registry/LAYER_REGISTRY.yaml:216 |
| 7  | `realizing_layers` is the normative backward-coverage map | `realizing_layers:` | framework/registry/LAYER_REGISTRY.yaml:231 |
| 8  | BDD's realizing set is SPEC **or** TDD | `BDD: [SPEC, TDD]` | framework/registry/LAYER_REGISTRY.yaml:234 |
| 9  | The linter mirrors that map as a curated constant | `REALIZING_LAYERS` | `tools/sdd_doc_lint/__init__.py:2008` |
| 10 | COV02 passes an element cited by any layer in its realizing set (OR semantics) | `_element_realizing_citers` | `tools/sdd_doc_lint/__init__.py:2208` |
| 11 | The realization primitive is document-scoped — it returns citer docs, not test cases | `citers \|= graph.citers_in_layer(token, layer)` | `tools/sdd_doc_lint/__init__.py:2021` |
| 12 | COV02 is `warning` in build, `error` in gate-code | `severity` | `tools/sdd_doc_lint/__init__.py:2191` |
| 13 | COV02 exempts `reuse: referenced` host docs | `reuse.get(host, ("authored", ""))[0]` | `tools/sdd_doc_lint/__init__.py:2205` |
| 14 | Conformance pins the corpus at 16 orphan BDD scenarios and defers remediation | `test_example_corpus_cov02_surfaces_16_orphan_scenarios` | tests/conformance/test_coverage_engine.py:103 |
| 14b | A single §4 traceability line already cites 15 scenarios at once — the vacuous-pass vector | `@bdd: BDD.01.03.9b90` | examples/url-shortener/docs/07_TDD/TDD-01.md:206 |
| 14c | TDD-01 scopes itself to the 15 SPEC-01-designed scenarios — the orphans are un-designed | `Mapping-Store BDD scenarios` | examples/url-shortener/docs/07_TDD/TDD-01.md:66 |
| 15 | PH01's lowercase placeholder pattern excludes `.`-preceded hash segments, leaving them to ID03 | `(?<!\.)\bx{3,}\b` | `tools/sdd_doc_lint/__init__.py:157` |
| 15b | ID03 emits on any element-id token that fails the hex pattern — the prevention that already blocks templated IDs in a produced artifact | `Finding(rel, i, "ID03", f"malformed element id '{tok}'")` | `tools/sdd_doc_lint/__init__.py:642` |
| 15c | ID01 emits on a templated `@`-tag citation — the citation-form half of the same prevention | `Finding(rel, i, "ID01", f"malformed trace-tag id` | `tools/sdd_doc_lint/__init__.py:594` |
| 16 | PH01 catalogued as a warning-level placeholder rule | `PH01` | framework/governance/LINT_RULES.md:23 |
| 17 | ID03 is the malformed-element-id error (blocking) | `ID03` | framework/governance/LINT_RULES.md:31 |
| 17b | ID01 is the malformed-trace-tag error (blocking) | `ID01` | framework/governance/LINT_RULES.md:29 |
| 18 | The acceptance suite already runs a negative-fixtures validation pass | `brd-broken-tags.md` | tests/ACCEPTANCE.md:305 |
| 18b | …but its nearest fixture exercises a 3-segment malformed form, NOT the templated `TYPE.NN.SS.xxxx` | `@brd: BRD.01.aaaa` | tests/acceptance/fixtures/negative/brd-broken-tags.md:26 |
| 19 | The catalog guard is one-directional (emitted ⊆ catalogued) | `test_every_emitted_rule_is_catalogued` | tests/conformance/platforms/test_lint_rules_catalog.py:55 |
| 19b | STRUCT01 derives required sections from `_size_target` and honours `_required: false` | `if body.get("_required") is False:` | `tools/sdd_doc_lint/__init__.py:449` |
| 19c | STRUCT01 is error-severity | `STRUCT01` | framework/governance/LINT_RULES.md:19 |
| 19d | The acceptance harness is stricter — every top-level dict section but `metadata` — and also honours `_required: false` | `if value.get("_required") is False:` | tests/acceptance/_harness.py:46 |
| 19e | The governance file set is asserted **exactly**, so a new doc must be registered | `self.assertEqual(found, set(EXPECTED_FILES))` | tests/conformance/test_governance.py:70 |
| 19f | The plugin bundles a byte-identical copy of framework/ subtrees | `test_bundle_is_byte_identical` | tests/conformance/platforms/test_plugin_framework_bundle.py:61 |
| 19g | …covering layers, governance, registry, playbooks | `SUBTREES = ("layers", "governance", "registry", "playbooks")` | tests/conformance/platforms/test_plugin_framework_bundle.py:23 |
| 19h | The registry sync guard reads only `realizing_layers`, so `acceptance_layers` is safe | `realizing_layers` | tests/conformance/platforms/test_realizing_layers_registry.py:21 |
| 29 | `TYPE.NN.SS.xxxx` is legitimate pattern notation in the tag table — templates are correct as-is (Part B changes none) | `@bdd: BDD.NN.SS.xxxx` | framework/governance/ID_NAMING_STANDARDS.md:203 |
| 30 | …and in the tag-syntax granularity table | ``**element** `TYPE.NN.SS.xxxx``` | framework/governance/TAG_SYNTAX.md:23 |
| 30b | A skeleton `id: BDD.01.03.xxxx` in a README snippet is the shape of a future ID — left unchanged per founder direction | `id: BDD.01.03.xxxx` | framework/layers/04_BDD/README.md:60 |
| 30c | …the same file shows the concrete form alongside it, so both are intended | `BDD.01.03.d7a2` | framework/layers/04_BDD/README.md:80 |
| 31 | TDD template carries a per-scenario BDD mapping field — an `ACC01` carrier | `bdd_scenario:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:86 |
| 32 | …and an e2e case-level BDD reference — the second carrier | `bdd_ref:` | framework/layers/07_TDD/TDD-TEMPLATE.yaml:165 |
| 33 | BDD is specified as executable acceptance scenarios | `Executable acceptance scenarios` | framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:18 |
| 34 | …yet the layer forbids CI execution | `QA STAGING ONLY` | framework/layers/04_BDD/README.md:26 |
| 35 | TDD maps existing BDD scenarios and creates none | `BDD as Source of Truth` | framework/TESTING_STRATEGY_TDD.md:63 |
| 35b | "Acceptance" already names the plugin's release-gate methodology | `acceptance-test methodology` | framework/README.md:129 |
| 36 | A `framework/**` edit routes to GATE-SPEC by target | `routed to GATE-SPEC by its **target**` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:48 |
| 37 | A spec change is never C1; `major ⇒ C3` only | `Change level proposed` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:60 |
| 38 | VERSION must bump when `framework/**` changes | `GATE-SPEC-E005` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:89 |
| 39 | CHANGELOG must be updated | `GATE-SPEC-E008` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:92 |
| 40 | Agent-facing spec changes carry a SECURITY_REVIEW assessment | `GATE-SPEC-W003` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:105 |
| 41 | GD-07 is the highest existing governance decision → GD-08 is next | `## GD-07` | framework/governance/DECISIONS.md:16 |
| 43 | The vendored linter sync covers four `.py` files into two platforms | `"$repo_root/platforms/hermes/sdd_doc_lint"; do` | tools/sdd_doc_lint/sync-vendored.sh:14 |
| 44 | Example artifacts are never hand-edited | `Never hand-edit example artifacts.` | CLAUDE.md:93 |
| 44b | The corpus is regenerated wholesale after framework changes | `regenerated wholesale after framework changes` | CLAUDE.md:19 |
| 45 | A plan changing a lint rule must run the corpus lint in a review pass | `Corpus cross-check` | CLAUDE.md:150 |
| 46b | FRWK-REVIEW-003 T3 edits the registry comment block `acceptance_layers` appends near — the one remaining overlap | `Task 3 (T3): Registry + layer-README truth-up` | plans/FRWK-REVIEW-003-PLAN.md:296 |
| 46c | …and it is still `PLANNED`, so this plan cannot assume its version numbers | `Status         \| PLANNED` | plans/FRWK-REVIEW-003-PLAN.md:7 |
| 47 | BRD auditor lens has 7 checks; C8 is the next | `**C7 — Version history present if status is Review or Approved.**` | framework/playbooks/01_BRD/auditor.md:81 |
| 48 | BRD business_analyst lens has 7 checks; C8 is the next | `**C7 — Document Control section complete.**` | framework/playbooks/01_BRD/business_analyst.md:76 |
| 49 | The example seed carries a stale "cleared pending regeneration" note | `has been cleared pending regeneration` | examples/url-shortener/seed/initial-requirements.md:24 |
| 50 | The plan template requires a Claim ledger + Review log | `## Claim ledger — [IF APPLICABLE]` | plans/PLAN-TEMPLATE.md:97 |

## Review log

### Pass 1 — 2026-07-24 — self-review

- **Part B contradicted itself.** The draft said "examples should carry real IDs"
  and then proposed real IDs in *fill-in skeletons* too — which would make a
  copied placeholder pass `ID03` silently, strictly worse than today. Split the
  surface three ways (pattern prose / `_example` / skeleton) and recorded the
  deviation-with-reason, with `BDD-00_index.TEMPLATE.md:95` as precedent.
- **`ACC01` was described as if it would find new problems.** Measured the
  corpus: the 15 covered scenarios are cited by both SPEC and TDD, the 16
  uncovered by neither, so a document-scoped `ACC01` flags exactly `COV02`'s 16.
- **`SEED01` was over-claimed.** A deterministic rule cannot know whether the
  ledger missed a claim the seed prose makes. Added the enforcer table and moved
  completeness to auditor C8.
- **Mutating `realizing_layers` would have broken a pinned conformance
  assertion** (`test_coverage_engine.py:103`). Replaced with additive
  `acceptance_layers`.
- **Missing baseline.** Ran the corpus lint and recorded 16/6/5/1.
- **Missing dependency** on FRWK-REVIEW-003.

### Pass 2 — 2026-07-24 — independent (fresh-context)

Fourteen findings, all folded. The four with the largest design impact:

- **`ACC01` as designed was vacuous.** Reusing `_element_realizing_citers`
  yields citer *documents*, and `examples/url-shortener/docs/07_TDD/TDD-01.md:206`
  is already a single §4 traceability line citing 15 scenarios at once — so
  appending 16 IDs to it would zero both COV02 and ACC01 with no test authored.
  Rule redesigned as **case-scoped** over `bdd_scenario` / `bdd_ref`, with the
  added parsing cost stated and V4 as the proof fixture. The finding-delta claim
  was downgraded from "zero today" to "measured in T7, not predicted".
- **The BRD carrier was an error-level breaking change.** STRUCT01
  (`__init__.py:449`) and the stricter acceptance harness (`_harness.py:46`)
  both derive required sections from the template, so adding the section would
  have turned every authored BRD red and broken the BRD golden. Now ships
  `_required: false`, and V2 runs `tests/acceptance` — which V1 does not cover.
- **Placement would have renumbered §7–§15**, and `section_id` is a hash input
  (`ID_NAMING_STANDARDS.md:71`), invalidating every `BRD.NN.07.*` element ID.
  Moved to a trailing §16.
- **Two sync surfaces, not one, and a third registration.** The plugin bundles
  byte-identical `framework/` subtrees
  (`test_plugin_framework_bundle.py:61,23`) — every part of this plan lands
  inside them — and `test_governance.py:70` asserts the governance file set
  *exactly*, so `SEED_CONTRACT.md` must be registered or V1 goes red. Added
  `tools/sync-plugin-framework.sh` (V8), the `EXPECTED_FILES` edit, and fixed V7,
  which as written could never pass inside its own PR.

Also folded: Part B expanded from 4 blocks to every element-declaring template +
layer README (the file-scoped guard could not otherwise go green); the
placeholder alphabet pinned to non-hex `g`–`z` (`aaaa`/`bbbb` are valid hex and
would reintroduce R2); T8 reframed — the orphans are un-*designed*
(`TDD-01.md:66`), so the expected outcome is a SPEC-coverage gap and the pinned
16 most likely stays; V3 now states an expected direction per rule instead of
predicting STY02 would hold while TDD-01 doubles; absolute version numbers
dropped and R3 widened to FRWK-REVIEW-003 T3's registry + README overlap; the
`04_BDD/README.md:64,94` `ears:` lines added to T6; "mentions the seed exactly
twice" corrected to three; and a disambiguation sentence added because
"acceptance" already names the plugin's release-gate suite.

Two items the reviewer explicitly confirmed as **correct** and not to be
re-litigated: the PH01 regex genuinely cannot match a `.`-preceded hash segment
(row 15), and the additive `acceptance_layers` block trips neither the registry
sync guard nor `test_registry.py`.

### Pass 3 — 2026-07-24 — self-review of the Pass 2 fold

- Re-ran the citation gate after the fold: all ledger symbols resolve.
- Checked that no Pass 2 fix contradicts a Pass 1 fix. The one interaction is
  Part C: Pass 1 established "delta is zero today", Pass 2 invalidated it by
  changing the rule's granularity. Pass 1's wording was removed, not layered
  over — the plan now states the delta is measured in T7.
- Confirmed the `_required: false` fix does not defeat Part A's purpose: the
  contract is normative for *new* BRDs via playbook C8, while the lint stays
  silent on pre-existing ones. Requiring the section is named in Out-of-scope as
  the follow-on breaking change.

### Pass 4 — 2026-07-24 — founder scope correction (Part B)

Founder direction: the templated `xxxx` form is **correct** in the layer
templates and README snippets — it is the shape of a future ID. The real
requirement is preventing a templated ID from surviving into a **produced
artifact**. Re-verified empirically against three probe artifacts: `ID03`
(`__init__.py:642`) already rejects `BDD.01.03.xxxx` / `BDD.NN.03.xxxx` in an
`id:` declaration, in free prose, and in a table cell; `ID01` (`:594`) rejects
the `@`-tag citation form; both are error-severity and blocking. So the
prevention already exists.

Part B therefore **inverts** from the Pass-1/2 design: instead of rewriting
placeholders across ~10 template + README files (which the Pass-2 fold had
*expanded*), it now changes nothing under `framework/layers/`. The only gap is
that the guarantee is not pinned by a test — the nearest negative fixture
(`brd-broken-tags.md:26`) exercises a different malformed shape — so Part B
adds one negative fixture + a conformance assertion + one discoverability
sentence. This is strictly smaller and lower-risk than the prior Part B.

Cascaded edits: removed `test_template_example_ids.py`, the template/README
"Modified" rows, and the non-hex-alphabet design; new T5 is the regression lock;
tasks renumbered (old T7→T6 acceptance, T8→T7 corpus, T9→T8 version); V5/V6
rewritten (V5 = fixture rejected; V6 = no `framework/layers/` change); R2 and R3
rescoped; ledger rows 20–28 (template/README duplicate-placeholder premises)
removed as no-longer-defects, rows 15b/15c/17b/18/18b added for the
already-existing prevention. Parts A and C are unchanged from the Pass-2
independent review, so that review still stands for them.

Part B is a scope *reduction* the founder directed and I verified against
source; Parts A and C carry their prior independent review unchanged.

### Pass 5 — 2026-07-24 — author-side ai-review (stands in for CI ai-review)

The CI `ai-review` check fail-closed on a 401 (the `codex` reviewer has no
OpenAI key on this public repo — infrastructure error, not a verdict), so an
author-side adversarial review was run on the committed diff. It returned
`CHANGES_REQUESTED` with four internal-consistency findings, all leftovers from
the Pass-4 renumbering that were not fully propagated — folded:

- Scope bullet said "Task 8 finding" for the SPEC-coverage gap → **Task 7**.
- Part C prose said "T7 measures it" → **T6**; and "fixture (V3)" → **V4**.
- File-structure Modified table was missing the `04_BDD/README.md` row that
  T6 edits → added.
- `Depends on` cited FRWK-REVIEW-003 "T2/T3" but only T3 is substantiated (Part
  B no longer touches the template family) → narrowed to **T3**.

All text-only; no design change. The reviewer confirmed scope discipline and
ledger self-consistency were sound.

**Result:** ready — four consistency fixes folded; re-running the citation gate
and markdownlint after this fold.
