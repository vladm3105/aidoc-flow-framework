# REFGRAN-GUARD-001 Plan — lock the document-level-permitted set to {SPEC, IPLAN}

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | REFGRAN-GUARD-001                                            |
| Type           | bugfix                                                       |
| Status         | READY — 2026-08-28T00:00:00Z (4 review passes; see Review log) |
| Depends on     | GD-03, GD-13 (#530)                                          |
| Feeds          | #531                                                         |
| Version impact | **none** — `tests/**` plus two lint-exclude lines; no `framework/**` edit, so GATE-SPEC-E005 does not fire and no `framework/VERSION` bump is needed |

## Objective

GD-03 ratified that a trace citation to an element-declaring layer must be
element-level, leaving `{SPEC, IPLAN}` as the only document-level-permitted
targets. That proposition is stated in four places and measured in none.
Between 2026-06-27 and 2026-08-23 two of the statements said the opposite and
nothing noticed (#531). This plan makes the four surfaces agree by test.

## Scope

**In:**

- A conformance guard asserting the document-level-permitted set is exactly
  `{SPEC, IPLAN}` on all four authority surfaces: the linter constant,
  `ID_NAMING_STANDARDS.md`, `TAG_SYNTAX.md`, `TRACEABILITY.md`.
- Committed fixtures carrying the real pre-#530 drifted text, plus the lint
  exclusions that keep them byte-faithful.
- The scope limits stated in the guard's own docstring: which four surfaces are
  covered, that coverage is **per anchored region and not per file**, and that
  GD-13's successor language overclaims what this guard reaches
  (§"Alternatives considered", item 3).

**Out of scope (deferred):**

- **The #563 remediation.** Cut from this plan at Pass 2 and moved to its own,
  because independent review showed it is eleven per-surface judgements rather
  than one edit applied eleven times: five of the surfaces this plan originally
  proposed to "correct" are **not** defects (downstream forward-pointers, which
  GD-03 exempts and `build_edge_graph` drops before `REFGRAN01` runs), and the
  census grew by five surfaces in three roots that were structurally outside it.
  Corrected on #563; that issue now owns the work.
- **A class-wide scan over authoring surfaces.** Rejected on measurement — see
  §"Alternatives considered", item 2.
- The `#486` corpus re-cascade, which `plans/CORPUS-REGEN-RUNBOOK.md` owns and
  #563 blocks.
- Any `framework/**` edit. The three governance surfaces are already correct;
  this plan only locks them. This also defers **correcting** GD-13's
  "would have caught all six" sentence at
  `framework/governance/DECISIONS.md:243` — amending it is a `framework/**` edit
  with the GATE-SPEC-E005 cost of alternative 1. The guard's docstring records
  the true figure; the GD sentence needs its own issue.

## Approach / Design

### D1 — compare the document-level-permitted set, not the element-declaring set

The two are complements, so comparing either would seem equivalent. They are
not, because the surfaces state them at different completeness.
`TRACEABILITY.md:58` names EARS, BDD, ADR and TDD on the element-declaring side
and omits BRD and PRD — so an element-declaring comparison reports a 4-of-6
mismatch **on a correct file**. Every surface states the document-level side
completely. Direction chosen accordingly; this also matches #531's own framing.

### D2 — an unparseable surface is a distinct hard failure, never an empty set

The first prototype's `TRACEABILITY` extractor "caught" the pre-#530 drift by
returning the empty set from a failed match, not by reading a wrong set. That is
a pass for the wrong reason, and its inverse is worse: a benign rewording of a
*correct* sentence also yields the empty set, reddening CI with a set-mismatch
message that names layers rather than saying the parse broke.

Each extractor therefore raises `Unparseable` with the reason, and the test
reports that distinctly from a set mismatch. **The rule binds the fixture test
too** — it asserts the exact set extracted from each fixture *and* that
`Unparseable` was not raised, so a broken parse can never be mistaken for a
detected regression. Without that second assertion the fixture files stand as
evidence of a detection that never happened.

### D3 — classify bullets by an explicit permit phrase, which outranks a forbid marker

`ID_NAMING_STANDARDS.md` states the rule as six bullets under one heading. A
bullet is read only if it carries an explicit permitting phrase —
`document-level permitted`, `are **document-level**`, `is **document-level**` —
and is not the self-tag/forward-pointer exemption bullet. **A permit phrase
outranks a forbid marker in the same bullet**, and names are then taken from the
bullet's bolded subject, which is what the permit attaches to.

That precedence is the whole design, and getting it backwards costs the guard
its most likely future catch. `:233` carries *both*: it permits
(`is **document-level permitted**`) and it forbids (`Citing an
**element-declaring** layer … remains element-level`). Under a forbid-first rule
`:233` is skipped — and `:233` is the bullet that **actually drifted** before
the GD-13 correction landed. Its fixture form carries no forbid clause, so the
historical regression is still detected either way; but a *re-drift* that adds `ADR / TDD` back to the
bolded subject while leaving today's "remains element-level" sentence intact
would be skipped and the guard would go green. Measured: that mutant survives
under forbid-first and is killed under permit-first.

Reading the **bolded subject** rather than the bullet body is load-bearing for
the same bullet in the other direction — `:233`'s body names TDD and ADR in its
counter-example ("a concrete test case in TDD, a decision in ADR"), so a
body-wide read yields `{SPEC, IPLAN, TDD, ADR}` on correct text.

Measured classification, both sources, six bullets each:

| Bullet | current `main` | pre-#530 fixture |
| --- | --- | --- |
| `:232` Oracle layers | no-permit skip | no-permit skip |
| `:233` Design & realization | **permit** → `{SPEC, IPLAN}` | **permit** → `{ADR, SPEC, TDD, IPLAN}` |
| `:235` trace citation | no-permit skip | no-permit skip |
| `:244` BDD carrier | no-permit skip (contains no `document-level` at all) | no-permit skip |
| `:251` `@spec:`/`@iplan:` | **permit** → `{SPEC, IPLAN}` | **permit** → `{SPEC, IPLAN}` |
| `:254` Self-tags | exemption skip | exemption skip |

The test asserts the **shape** of that parse — six bullets, exactly two
permitting — not only its result, so a seventh bullet forces a decision instead
of silently joining a class. Bullets are joined across continuation lines before
classification; `:231`'s `**Derivable Principle:**` lead-in and the blank line at
`:234` split the section into two blocks, so a naive per-block split does not
yield six.

### D4 — read layer names from a permitting bullet's bolded subject, not only from `@tag` tokens

The first prototype killed three synthetic mutants and then **missed the actual
historical drift**, because the drifted bullet named its layers in a bolded
subject —
`- **Design & realization layers (ADR / SPEC / TDD / IPLAN):** …` — with no
`@adr:`/`@tdd:` token anywhere. A token-only extractor reads it as clean.

This is the failure mode recorded as "your own test can enshrine the defect you
just introduced": a mutant written beside the extractor inherits the extractor's
assumption about *how the rule is phrased*, so mutant and extractor agree and
the mutant dies for the wrong reason. The authority on how the drift reads is
the drift itself, which is why D5 exists.

### D5 — regression-test against the real pre-#530 text, and make the discarded prototype the control

Three fixtures are committed from `8dccc315^`. The guard must extract
`{ADR, SPEC, TDD, IPLAN}` from the `ID_NAMING_STANDARDS.md` and `TRACEABILITY.md`
fixtures and `{SPEC, IPLAN}` from the `TAG_SYNTAX.md` one, which was already
correct and is the negative control.

The **positive control is the discarded token-only prototype**, not a stub. A
stub raising `NotImplementedError` fails for a reason unrelated to detection —
a green-baseline assertion with no information content, and a perfect kill rate
against a control you built is a symptom rather than a result. Running the
regression fixtures against the token-only prototype and confirming it misses
the `ID_NAMING_STANDARDS.md` one turns D4 from a narrated claim into a measured
one at zero cost.

### D6 — the fixtures must be excluded from the autofixing hooks

`.pre-commit-config.yaml:16` excludes `framework/` from every hook; `tests/` is
not excluded. So a fixture under `tests/conformance/fixtures/` is subject to
`markdownlint --fix` (`:57`), `trailing-whitespace` and `end-of-file-fixer`
(`:23-24`) — and the originals have never been style-linted, so findings are
likely and `--fix` rewrites them silently. MD049/MD050 emphasis normalization
rewrites `**document-level permitted**`-class spans across a whole file, which is
exactly the text the fixture exists to preserve. Worse, a `pre-commit
run --all-files` check would then be green *because* the corruption ran.

`tools/sdd_doc_lint/fixtures` is already excluded at `.pre-commit-config.yaml:67`
for verbatim this reason ("deliberately-malformed sample docs"), and
`.github/workflows/markdown-lint.yml:74` carries the matching CI glob.

**That precedent is not sufficient to copy, and this is the trap.** The `:67`
exclude is scoped to the markdownlint hook alone, while three *other* hooks
rewrite files unconditionally — `trailing-whitespace` (`:23`),
`end-of-file-fixer` (`:24`) and `mixed-line-ending --fix=lf` (`:33`), none of
which carries an exclude. Adding `tests/conformance/fixtures` at `:67` would
leave all three live, and the `tools/sdd_doc_lint/fixtures` precedent has the
same hole, so its existence is not evidence the single line works. The exclusion
therefore goes in the **global** `exclude:` at `.pre-commit-config.yaml:16`,
alongside `framework/`, plus the CI glob at
`.github/workflows/markdown-lint.yml:74`.

### D7 — import the linter constant; do not regex the Python source

`tests/conformance/platforms/test_realizing_layers_registry.py:15` and
`tests/conformance/test_acceptance_pairing.py:17` both `sys.path.insert` and
import the constant directly. An import has no `Unparseable` failure mode,
survives a `ruff-format` reflow of the tuple, and survives a type annotation on
the assignment. That removes one of the four extractors and shrinks the surface
D2 has to defend from four to three.

Two riders. The 8-layer set comes from `tests/conformance/_spec.py:19`
(`ARTIFACTS`), never a fresh literal — otherwise the guard introduces a *fifth*
unguarded statement of a layer list. And the complement is asserted explicitly
(`declaring | permitted == set(ARTIFACTS)` and `declaring & permitted == set()`)
rather than encoded in a `-`, so a layer added to one set and not the other
fails here instead of vanishing.

### The three prose extractors

| Surface | Anchor | Scoping rule |
| --- | --- | --- |
| `TAG_SYNTAX.md:21` | the `\| Target layer \| Form \| Why \|` table | read the **Form cell only**. The element row's Why cell contains the word "document" ("functionality is defined in the element, not the document"), so a row-level test yields all eight layers. |
| `ID_NAMING_STANDARDS.md:223` | bullets under `### Reference granularity`, classified per D3 | names from a permitting bullet's bolded subject and its `@tag` tokens |
| `TRACEABILITY.md:58` | the permit clause `citing <subject> (<layers>) at document-level` | the parenthesised list immediately preceding `at document-level`. **Not** the literal `element-ID-exempt layers (` — that phrase is absent from the drifted text (Pass 4), so the regression fixture would report `Unparseable` rather than a wrong set, which D2 forbids counting as a detection. `at document-level` occurs exactly once in each of the two versions, and it is the permit clause specifically: the same physical line also carries "a document-level ID" (a forbid counter-example) and "are document-level and exempt" (the carve-out), neither of which this anchor matches |

## Alternatives considered

1. **State the set once in `LAYER_REGISTRY.yaml`**, as `realizing_layers` (`:240`)
   and `acceptance_layers` (`:262`) already do, and check the prose against the
   registry rather than against each other. This is the better design and is
   rejected only on cost: it is a `framework/**` edit, so it trips
   GATE-SPEC-E005, forces a `framework/VERSION` bump with its ~120-file fanout
   and a per-bump founder grant, and needs a GD entry. Recorded here as the
   successor rather than silently not-chosen.
2. **A class-wide scan over authoring surfaces** (playbooks, layer templates,
   plugin skills/agents/docs, Hermes prompts and `agent-skills`). Rejected on
   measurement. The census is recorded as its command, not as a number in
   prose — `tmp/` is gitignored, so a script reference there would dangle:

   ```sh
   grep -rEn --include='*.md' --include='*.yaml' --include='*.yml' \
     '@(brd|prd|ears|bdd|adr|tdd): *`?(BRD|PRD|EARS|BDD|ADR|TDD)-(NN|[0-9]+)' \
     framework/playbooks framework/layers framework/governance \
     platforms/claude-code-plugin/{agents,skills,docs} \
     platforms/hermes/{prompts,skills,agent-skills}
   # -> 51 hits across 29 files
   ```

   The result is overwhelmingly
   exempt: self-tags, downstream forward-pointers, `FAIL:`/`WRONG:`
   counter-examples, and the layer templates' own self-tag declarations
   (`- "@brd: BRD-NN"` and its five siblings). An exemption model at that ratio
   is a heuristic, and it fails in one of two directions that are both worse
   than no check: it false-positives on correct text and blocks CI, or it
   under-covers and reads as complete —
   `tests/conformance/platforms/test_no_inprompt_hashing.py` being the in-repo
   cautionary instance that #531 itself names. A token scan also cannot see
   `doc-tdd/SKILL.md:124`, which states the rule in prose with no dash token.
   Those surfaces are not unguarded in consequence, only unguarded *here*:
   `REFGRAN01` flags the artifacts they generate, which is how #486 was found —
   a downstream detector with regen latency, recorded as a real limit.
3. **Inheriting GD-13's framing unexamined.** `framework/governance/DECISIONS.md:243`
   says a guard over these four surfaces "would have caught all six". It would
   not: two of the six were `playbooks/{05_ADR,07_TDD}/auditor.md`, a third was
   `layers/08_IPLAN/IPLAN-TEMPLATE.yaml` and a fourth was
   `agents/requirements-analyst.md` — none of which this guard reads. It would
   have caught **two**. The four-surface scope is still right, for the reason in
   item 2; the inherited claim about its reach is not, and the guard's docstring
   says so.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/test_ref_granularity_parity.py` | the guard, its fixture regression, and the scope-limit docstring |
| `tests/conformance/fixtures/refgran/README.md` | the source SHA and the exact `git show` command; states the fixtures are immutable evidence |
| `tests/conformance/fixtures/refgran/pre530_ID_NAMING_STANDARDS.md` | real drifted text at `8dccc315^` |
| `tests/conformance/fixtures/refgran/pre530_TRACEABILITY.md` | real drifted text at `8dccc315^` |
| `tests/conformance/fixtures/refgran/pre530_TAG_SYNTAX.md` | already-correct negative control at `8dccc315^` |

### Modified

| Path | Change |
| ---- | ------ |
| `.pre-commit-config.yaml` | add `tests/conformance/fixtures` to the markdownlint exclude at `:67` |
| `.github/workflows/markdown-lint.yml` | add the matching `!tests/conformance/fixtures` glob at `:74` |
| `CHANGELOG.md` | `[Unreleased]` entry |
| `plans/DECISIONS.md` | D2, D5, D6, D7 and alternative 1 are non-obvious and measured |
| `plans/HANDOFF.md` | regenerate |

## Implementation sequence

### Task 1: fixtures and their lint exemption

- Add the exclude lines **first**, in their own commit, and confirm with a
  scratch file that `pre-commit run --all-files` leaves it byte-identical. The
  scratch file must be **deliberately dirty** — trailing whitespace, no final
  newline, a CRLF line — or the check passes vacuously against the three hygiene
  hooks it exists to test (V8). Landing the fixtures before the exclusions is
  the failure D6 describes.
- Extract the three fixtures from `8dccc315^` and write the provenance README.

### Task 2: the guard

- **Test-first:** land `test_guard_detects_the_pre_530_drift` against the
  fixtures before the extractors exist, with the discarded token-only prototype
  as the control (D5).
- Add `tests/conformance/test_ref_granularity_parity.py`: `Unparseable`, the
  linter import (D7), three prose extractors, and three test methods — live
  parity, fixture regression, and the D3 shape assertion.
- Keep it standalone at `tests/conformance/` top level.
  `test_governance.py:1` scopes itself to "`framework/governance/` files are
  present and parseable" and imports only `ARTIFACTS, FRAMEWORK`; reaching into
  `tools/sdd_doc_lint/` would give it a cross-boundary dependency it has
  avoided. `test_review_report_parity.py`,
  `test_layer_registry_necessary_upstream.py` and `test_acceptance_pairing.py`
  are the standalone-parity-module precedent. It does **not** belong under
  `tests/conformance/platforms/` — nothing in it is platform-specific.
- No registration is needed. `tests/conformance/test_repo_scripts.py:16-21`
  scopes its `REGISTERED` tuple to `tests.unit.*`, and
  `.pre-commit-config.yaml:107` discovers `tests/conformance` by pattern. Stated
  because the rule for `tests/unit/**` is the opposite and the two are easy to
  conflate.
- Adopt `GateCheckIdParity`'s docstring convention (`test_governance.py:175-194`):
  name the four surfaces covered, the playbook/template/skill classes not
  covered with the alternative-2 measurement, and mark each limit as established
  by mutation rather than assumed. State one more limit explicitly: coverage is
  **per anchored region, not per file** — a contradicting sentence added
  elsewhere in a guarded file passes, which is exactly how GD-13 describes the
  original defect ("contradicting the bullet immediately below it in the same
  file", `framework/governance/DECISIONS.md:219`). And record the true reach of
  the guard, two of GD-13's six surfaces, not the six its own successor sentence
  claims.

### Task 3: mutation-test the guard

- Reintroduce each of the **two** real drifted statements individually and
  confirm a distinct failure naming its surface. Two, not three: GD-13
  (`framework/governance/DECISIONS.md:218-222`) names only
  `ID_NAMING_STANDARDS.md` and `TRACEABILITY.md`; `TAG_SYNTAX.md` was already
  correct and the linter constant was never drifted.
- Negative control: the `## Carve-outs — NOT trace citations` section of
  `TAG_SYNTAX.md:45-53` states that document-level *is* correct for
  `@bdd: BDD-01` and `@tdd: TDD-01`. Real adjacent text that must not be read;
  if the extractor ever widens past the table it fails loudly. Stronger than a
  synthetic trailing paragraph, which a table-anchored extractor cannot see by
  construction.
- **The permit-over-forbid mutant (V7):** add `ADR / TDD` back to `:233`'s
  bolded subject and leave today's "remains element-level" sentence in place.
  This is the likeliest shape of a future re-drift and it survives under a
  forbid-first classifier, so it is the mutation that justifies D3 rather than
  merely illustrating it.
- Confirm an unparseable surface reports as unparseable and names no layer set —
  delete the `### Reference granularity` heading and read the message.

### Task 4: docs of record

- Root `CHANGELOG.md` `[Unreleased]`.
- `plans/DECISIONS.md` — **start at D-0078**: D-0077 is claimed by the unmerged
  PR #559 (branch `docs/a2-discard-d0077`), so `main`'s highest is D-0076 and
  two branches would otherwise collide on one number.
- `plans/HANDOFF.md` regenerate.

## Verification

> The conformance suite runs on the **standard library `unittest`**, not pytest:
> `.pre-commit-config.yaml:107` and `.github/workflows/conformance.yml:45` both
> invoke `unittest discover`, and `tests/conformance/requirements.txt` lists only
> PyYAML and jsonschema. A pytest-shaped module (bare `test_*` functions, no
> `TestCase`) would be collected by neither gate — a guard that exists and never
> runs, which is the failure class this plan is about. V2 is the row that catches
> it, so it uses the gating runner verbatim.

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python3 -m unittest tests.conformance.test_ref_granularity_parity -v` | all cases pass | Task 2 |
| V2 | `python3 -m unittest discover -s tests/conformance -v 2>&1 \| grep -c ref_granularity` | non-zero — the module is collected by the runner both gates use | Task 2 |
| V3 | each of the two real drifted statements reintroduced individually | two distinct failures, each naming its surface | Task 3 |
| V4 | `### Reference granularity` heading deleted | failure says the surface is unparseable, and names no layer set | D2, Task 3 |
| V5 | `ADR` and `TDD` injected into `TAG_SYNTAX.md:45-53`'s carve-outs section | still passes, extracted set unchanged — the extractor does not read past its table anchor | D3, Task 3 |
| V6 | the fixture regression run against the discarded token-only prototype | it misses the `ID_NAMING_STANDARDS.md` fixture | D4, D5 |
| V7 | `ADR / TDD` added to `ID_NAMING_STANDARDS.md:233`'s bolded subject, forbid sentence left intact | fails — the permit-over-forbid precedence of D3 | D3, Task 3 |
| V8 | a deliberately dirty scratch file (trailing space, no final newline, CRLF) under `tests/conformance/fixtures/`, then `pre-commit run --all-files` | left byte-identical | D6, Task 1 |
| V9 | `pre-commit run --all-files`, then `git diff --exit-code tests/conformance/fixtures/` | green **and** the fixtures byte-identical | D6, Task 1 |
| V10 | `diff <(git show 8dccc315^:framework/governance/ID_NAMING_STANDARDS.md) tests/conformance/fixtures/refgran/pre530_ID_NAMING_STANDARDS.md` | empty, for each of the three | Task 1 |

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | The prose extractors are regexes; a legitimate rewrite of a governance surface reddens CI | med | Lower than it looks: `.markdownlint.json:3` disables MD013 and `.markdownlintignore:13` excludes `framework/`, so no tool reflows these files and the one-physical-line `TRACEABILITY.md:58` anchor is stable. Where a rewrite does break an anchor, D2 makes it report `Unparseable` with the reason, so the author is told the parse broke rather than shown a layer-set diff. |
| R2 | The guard covers 4 surfaces; a green run reads as "the rule is locked everywhere" | high | Stated in the test's own docstring with alternative 2's measurement, as `GateCheckIdParity` does for its two limits, and reconciled against GD-13's overclaim in alternative 3. |
| R3 | The fixtures get "fixed" by a future contributor whose extractor rewrite fails the control | med | The provenance README records the SHA and command; the guard's docstring states they are immutable evidence; V8 re-derives them from git on demand. |
| R4 | markdownlint autofix corrupts a citation in this plan (`__init__.py` → `` **init**.py ``, `#NNN` at line start → H1) | med | Both are recorded traps; backtick every underscored path, never start a line with `#NNN`, re-run the citation gate after any autofix. |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The authority is a 6-layer tuple of element-declaring layers | `_REFGRAN_ELEMENT_DECLARING` | `tools/sdd_doc_lint/__init__.py:2668` |
| 2  | REFGRAN01 is a warning in `build` and an error in `gate-code` | `Severity mirrors the coverage gates' run-mode` | `tools/sdd_doc_lint/__init__.py:2690` |
| 3  | It skips non-element-declaring targets, so `@spec`/`@iplan` are exempt | `# @spec / @iplan target — exempt (no canonical elements)` | `tools/sdd_doc_lint/__init__.py:2709` |
| 4  | `build_edge_graph` drops self-tags and downstream forward-pointers before REFGRAN01 runs — why alternative 2's census is mostly exempt | `excludes self-tags + downstream forward-pointers` | `tools/sdd_doc_lint/__init__.py:2684` |
| 5  | `TAG_SYNTAX.md` states the set as a two-row table | `\| Target layer \| Form \| Why \|` | `framework/governance/TAG_SYNTAX.md:21` |
| 6  | Its element row's Why cell contains "document", so the parse must be Form-cell-scoped | `not the document (GD-03)` | `framework/governance/TAG_SYNTAX.md:23` |
| 7  | Its carve-outs section states document-level is correct for self-tags and forward-pointers — the D3 negative control | `## Carve-outs — NOT trace citations (document-level is correct)` | `framework/governance/TAG_SYNTAX.md:45` |
| 8  | `TAG_SYNTAX.md` delegates granularity ownership to `ID_NAMING_STANDARDS.md`, so its table is a derived surface | `- **Granularity** (element-level vs document-level) — owned by` | `framework/governance/TAG_SYNTAX.md:7` |
| 9  | `ID_NAMING_STANDARDS.md` states it under a `### Reference granularity (GD-03)` heading | `### Reference granularity (GD-03)` | `framework/governance/ID_NAMING_STANDARDS.md:223` |
| 10 | Its "Oracle layers" bullet carries a document-level counter-example, hence the forbid skip | `- **Oracle layers (EARS requirement or BDD scenario):**` | `framework/governance/ID_NAMING_STANDARDS.md:232` |
| 11 | Its "BDD carrier" bullet carries `@ears`/`@bdd` tokens and no forbid marker, hence the permit whitelist | `- **BDD carrier (YAML-BDD-SCHEMA, D-0038):**` | `framework/governance/ID_NAMING_STANDARDS.md:244` |
| 12 | Its one permitting bullet names `@spec:` and `@iplan:` | `citations are **document-level** — those layers are` | `framework/governance/ID_NAMING_STANDARDS.md:251` |
| 13 | Its exemption bullet covers self-tags and downstream forward-pointers | `- **Self-tags**` | `framework/governance/ID_NAMING_STANDARDS.md:254` |
| 14 | `TRACEABILITY.md` states the rule under `## Coverage gates`, not a `###` heading | `- **Reference Granularity Principle (GD-03 / #502):**` | `framework/governance/TRACEABILITY.md:58` |
| 15 | That same physical line carries two other `document-level` phrases, so the anchor must be the permit clause specifically | `Self-tags and downstream forward-pointers are document-level and exempt` | `framework/governance/TRACEABILITY.md:58` |
| 39 | The drifted form of that clause names a different subject, so a subject-anchored parse is `Unparseable` on it — the Pass-4 finding | `citing design/decision units (ADR, SPEC, TDD, IPLAN) at document-level` | `8dccc315^:framework/governance/TRACEABILITY.md:58` |
| 16 | `GateCheckIdParity` is the set-equality-across-surfaces precedent | `class GateCheckIdParity` | `tests/conformance/test_governance.py:143` |
| 17 | Its docstring states two scope limits and marks them mutation-established | `**Two limits, both established by mutation rather than assumed.**` | `tests/conformance/test_governance.py:175` |
| 18 | `test_governance.py` scopes itself to `framework/governance/`, so the guard does not belong there | `Conformance: ``framework/governance/`` files are present and parseable.` | `tests/conformance/test_governance.py:1` |
| 19 | Importing the linter constant is the established pattern, not regexing the source | `from sdd_doc_lint import REALIZING_LAYERS` | `tests/conformance/platforms/test_realizing_layers_registry.py:16` |
| 20 | A second instance of that pattern | `from sdd_doc_lint import ACCEPTANCE_LAYERS, _check_acceptance_pairing` | `tests/conformance/test_acceptance_pairing.py:17` |
| 21 | The 8-layer set already exists as a literal in the suite's helper | `ARTIFACTS = ["BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN"]` | `tests/conformance/_spec.py:19` |
| 22 | `_spec.py` exposes `REPO_ROOT`, so the guard can reach `tools/` | `REPO_ROOT` | `tests/conformance/_spec.py:14` |
| 23 | `test_repo_scripts.py`'s registration shim is scoped to `tests/unit`, so conformance needs none | `REGISTERED` | `tests/conformance/test_repo_scripts.py:31` |
| 24 | The conformance workflow checks out shallow, so a test cannot read `8dccc315^` | `- uses: actions/checkout@v7` | `.github/workflows/conformance.yml:34` |
| 25 | Only `chg-gate.yml` sets full history, confirming the shallow default is not overridden | `fetch-depth: 0` | `.github/workflows/chg-gate.yml:30` |
| 26 | The global pre-commit exclude covers `framework/` but not `tests/` | `exclude: '^(legacy/\|framework/\|platforms/claude-code-plugin/framework/` | `.pre-commit-config.yaml:16` |
| 27 | markdownlint runs with `--fix`, so an unexcluded fixture is rewritten | `args: [--fix]` | `.pre-commit-config.yaml:58` |
| 28 | `tools/sdd_doc_lint/fixtures` is already excluded for verbatim this reason | `sdd_doc_lint fixtures are` | `.pre-commit-config.yaml:62` |
| 29 | The CI markdown-lint caller carries the matching glob and needs the same addition | `!tools/sdd_doc_lint/fixtures` | `.github/workflows/markdown-lint.yml:74` |
| 30 | MD013 is disabled, so no tool reflows the one-line TRACEABILITY anchor | `"MD013": false` | `.markdownlint.json:3` |
| 31 | GD-13's successor language claims this guard "would have caught all six" | `such a guard would have caught all six` | `framework/governance/DECISIONS.md:243` |
| 32 | GD-13 names only two prose surfaces as drifted; the other four are outside this guard | `Six authoring surfaces had never been reconciled to it and went on telling authors` | `framework/governance/DECISIONS.md:216` |
| 33 | `LAYER_REGISTRY.yaml` already carries normative sets of this kind — alternative 1's basis | `realizing_layers` | `framework/registry/LAYER_REGISTRY.yaml:240` |
| 34 | The registry is at `framework/registry/`, not `framework/layers/` | `REGISTRY_PATH` | `tests/conformance/_spec.py:16` |
| 35 | The three hygiene hooks carry no exclude of their own, so the markdownlint-scoped one at `:67` would not protect the fixtures | `- id: mixed-line-ending` | `.pre-commit-config.yaml:33` |
| 36 | Both gates run `unittest discover`, so a pytest-shaped module is collected by neither | `entry: python3 -m unittest discover -s tests/conformance` | `.pre-commit-config.yaml:107` |
| 37 | The CI job runs the same, and the suite declares no pytest dependency | `run: python -m unittest discover -s tests/conformance -v` | `.github/workflows/conformance.yml:45` |
| 38 | The as-built module passes `main`, detects the fixture drift, and kills the permit-over-forbid mutant — **blocks V1** | — | PROBE: python3 -m unittest tests.conformance.test_ref_granularity_parity -v |

## Review log

### Pass 1 — 2026-08-28 — self-review

- Draft written after the scoping measurement recorded on #531 and #563.
- Design direction reversed against the comment posted on #531, which had
  recommended a class-wide authoring-surface scan. The exemption-rate
  measurement was taken after that recommendation and refutes it.
- The first extractor prototype was discarded: it killed three synthetic mutants
  and missed the real pre-#530 drift (D4).

### Pass 2 — 2026-08-28 — independent (dispatched, two reviewers)

- **Scope cut.** Pass 2 raised roughly three times Pass 1's load-bearing
  findings, and most traced to the bundled #563 remediation rather than to the
  guard. Per the fold rule, the remediation was cut to its own plan instead of
  folded a second time.
- **The remediation was also wrong, not merely large.** Five surfaces this plan
  proposed to correct are downstream forward-pointers, which GD-03 exempts and
  `build_edge_graph` drops (claim 4); `ADR-NN` is a legitimate document form for
  ADR's self-tag and `@depends:`, so "drop `ADR-NN` from the validator's
  enforced set" would have made it flag exempt constructs. #563 corrected.
- **Both reviewers independently derived a false positive from the plan's own
  description of the bullet classifier** — the BDD-carrier bullet. The
  implemented prototype does not have it, because it also requires a permitting
  phrase; the plan described only the forbid filter. The description was the
  defect, and D3 now states the whitelist, the measured per-bullet
  classification, and a shape assertion.
- Regexing the linter source replaced by an import, with two in-repo precedents
  (claims 19, 20) — one fewer extractor and one fewer `Unparseable` surface.
- The fixture path was unguarded twice over: nothing excluded it from
  `markdownlint --fix` (D6), and the fixture test as described could pass by
  raising `Unparseable`, which is the exact confusion D2 forbids. Both closed.
- Control replaced: the discarded token-only prototype, not a stub (D5).
- The census was not reproducible and its roots omitted
  `platforms/hermes/agent-skills` and `platforms/claude-code-plugin/docs`.
  Re-derived with a recorded command; the conclusion survives, the number did
  not. The two roots are not equivalent, and Pass 3 caught the sloppy
  conflation: `agent-skills` yields five token hits including two real
  instances, while `docs/` yields **zero** — its real instance
  (`SKILL_AUTHORING.md:68-71`) states the rule generically as `TYPE-NN` and is
  invisible to the token grammar entirely. That is evidence *for* alternative 2,
  not against it.
- V3 said "three drifted statements"; there are two (claim 32). V5 was vacuous
  by construction and was replaced with real adjacent text.
- GD-13's "would have caught all six" is inherited and wrong — it would have
  caught two (alternative 3).

### Pass 3 — 2026-08-28 — independent (dispatched)

- **The forbid-skip landed on the one bullet that actually drifted.** `:233`
  carries a permit phrase *and* a forbid marker; under forbid-first it was
  skipped. The historical fixture is detected either way — its `:233` has no
  forbid clause, measured — but a re-drift adding `ADR / TDD` to the bolded
  subject while keeping today's "remains element-level" sentence would have gone
  green. D3 now gives permit precedence over forbid, both classifications are
  recorded as measured tables, and the mutant is V7. Verified: it survives under
  the old rule and is killed under the new one.
- **V1/V2 verified with a runner neither gate uses.** The suite runs
  `unittest discover` (claims 36, 37) and declares no pytest dependency, so a
  pytest-shaped module would be collected by neither the hook nor the required
  context. V1 rewritten; V2 is now a collection assertion against the gating
  runner.
- **D6's prescription covered one of four rewriting hooks.** The `:67` exclude is
  markdownlint-scoped; `trailing-whitespace`, `end-of-file-fixer` and
  `mixed-line-ending` carry none (claim 35). Moved to the global `exclude:` at
  `:16`. The Task-1 scratch check was also vacuous unless the scratch file is
  deliberately dirty — now stated, and V8.
- V5 was still unable to fail (real text, but unmutated); it now injects `ADR`
  and `TDD` into the carve-outs section.
- Scope items that had no task were retargeted: the guard's docstring owns the
  limits, and correcting GD-13's sentence is deferred as a `framework/**` edit
  needing its own issue.
- Coverage is **per anchored region, not per file** — a contradicting sentence
  elsewhere in a guarded file passes. Added to the docstring requirement, since
  that is verbatim how GD-13 describes the original defect.
- Census riders corrected: five self-tag declarations, not seven; and
  `platforms/claude-code-plugin/docs` yields zero token hits, which is evidence
  for alternative 2 rather than the incidental detail Pass 2 recorded.

**Result:** not ready — the three-pass fold cap is reached with load-bearing
findings folded but unvalidated. Per OPS-0066 the open items go to the founder
rather than into a fourth dispatch; every Pass-3 fold above is measured rather
than argued, and the plan is otherwise ready to open.

### Pass 4 — 2026-08-28 — validation (implementation probe, not a fold cycle)

Per OPS-0066 the three fold cycles are spent. This pass validated the Pass-3
folds by building the module rather than by re-reviewing the prose, which is
what Pass 3's own "folded but unvalidated" result asked for. One load-bearing
finding, and it is a defect in the **design as written**, not in the folds:

- **The `TRACEABILITY.md` anchor could not parse the fixture it exists to
  detect.** The extractor table specified the literal `element-ID-exempt
  layers (`. That phrase entered the file *in the GD-13 correction itself* — the
  drifted text at `8dccc315^` reads `citing design/decision units (ADR, SPEC,
  TDD, IPLAN) at document-level` and contains the anchor **zero** times
  (measured). So the regression fixture would have raised `Unparseable`, and D2
  is explicit that a failed parse is never a detection: the fixture would have
  stood as evidence of a catch that never happened — verbatim the failure D2 was
  written to prevent, reaching the one surface D2 did not re-examine.

  Anchor replaced with the **permit clause** `citing <subject> (<layers>) at
  document-level`, which occurs exactly once in each version and yields
  `{SPEC, IPLAN}` on `main` and `{ADR, SPEC, TDD, IPLAN}` on the fixture. It is
  also the same permit-first principle D3 established for
  `ID_NAMING_STANDARDS.md`, so the three extractors now share one rule instead of
  two — the inconsistency is what hid the defect.

  This is the D4 lesson recurring one surface over: the authority on how drift
  reads is the drift itself, and the anchor had been derived from the corrected
  text alone.

**Result:** ready to open. The remaining Pass-3 folds are validated by V1–V10
passing against the as-built module.
