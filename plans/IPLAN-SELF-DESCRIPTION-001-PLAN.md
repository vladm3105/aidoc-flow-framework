# IPLAN-SELF-DESCRIPTION-001 Plan — three layer templates declare no title, while every artifact they produce has one

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | IPLAN-SELF-DESCRIPTION-001                                    |
| Type           | feature                                                       |
| Status         | PLANNED — 2026-08-31                                          |
| Depends on     | Founder decisions F-1..F-3 (below), recorded 2026-08-31       |
| Feeds          | `OKF-CONFORMANCE-001` D1 (`FRONTMATTER_CONTRACT.md`)          |
| Version impact | framework **MINOR** `0.47.0 → 0.48.0`; plugin bundle re-vendored, no plugin version move |

## Objective

`SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml` and `IPLAN-TEMPLATE.yaml` declare no
document title. Every artifact those templates produce carries one anyway —
authored by hand, in a key the template never named. This plan adds the
top-level `title:` those three templates are missing, gives IPLAN's
`file_manifest` entries the one-line `description` its own stateless-executor
protocol needs, and pins the resulting class with a conformance guard.

It closes [#553](https://github.com/vladm3105/aidoc-flow-framework/issues/553),
which was cut from `TEMPLATE-COMPLETENESS-001` at Pass 2 for lack of the
placement decision that F-1 now supplies.

## Scope

**In:**

- Top-level `title:` in `SPEC-TEMPLATE.yaml`, `TDD-TEMPLATE.yaml`,
  `IPLAN-TEMPLATE.yaml`, **authored as a plain scalar string** (Claims 24-25).
- `description:` on each `file_manifest.files[]` entry in `IPLAN-TEMPLATE.yaml`
  (#553 finding 2).
- A `document_control._guidance` sentence in `IPLAN-TEMPLATE.yaml` reserving
  `session_summary` as the status-at-a-glance name and stating it is distinct
  from §5 `session_handoff` (#553 finding 3).
- `tests/conformance/test_layer_title_declared.py` — a new guard pinning that
  every full layer template declares a top-level `title:`.
- **Amending the R8 row** in `IPLAN-LAYER-REVIEW-001-DESIGN.md` and correcting the
  two other surfaces that record R8's placement as live fact (Claims 27-29).
- The framework MINOR bump, both sync fanouts, a `GD-23` entry, and the docs of
  record.

**Out of scope (deferred):**

- **Top-level `id:`.** F-2 excludes it. Filed as
  [#588](https://github.com/vladm3105/aidoc-flow-framework/issues/588) for
  `OKF-CONFORMANCE-001` D1 to settle — that contract's stated job is the required
  top-level keys (Claim 12).
- **`document_control.iplan_id` removal.** Removing it is not additive: four
  goldens author it (Claim 9). It stays.
- **Reconciling the MVP templates**, which put `title` under `document_control`
  (Claim 2). `IPLAN-LAYER-REVIEW-001-DESIGN.md` R9 owns MVP reconciliation.
- **The `.md`-vs-`.yaml` three-way format split** (`OKF-CONFORMANCE-001` F-0).
- **The `STY02` budget defect** found while baselining this plan — 11 sections
  across 3 layers are enforced at the flat 200 instead of their declared
  `_size_target`, `file_manifest` among them. Recorded as a correction on
  [#546](https://github.com/vladm3105/aidoc-flow-framework/issues/546). It changes
  no decision here: this plan adds words to a section already over budget either
  way, and fixing it needs the parked subtype decision.

## Decisions (founder, 2026-08-31)

### F-1 — `title` is a top-level key

Not `document_control.title` (#553's implied placement, and the MVP shape), and
not `metadata.title` (`IPLAN-LAYER-REVIEW-001-DESIGN.md` R8, Claim 13). Top-level
is what five of eight full templates already ship (Claim 1), what every authored
artifact carries (Claim 3), and what the seven index templates carry (Claim 4).
`metadata.title` exists in no template in the repository (Claim 14).

**R8 is superseded on placement, because R8 contradicts the authority it cites.**
It defers to "the OKF D1 contract", and D1 declares *the required **top-level**
keys* (Claim 12) — so D1 selects top-level, not `metadata:`. D2 settles the
sibling key the same way, choosing the top-level `artifact_type` the linter reads
over the nested one (Claim 15), and the same design's own Correction 4 independently establishes that
templates receive `artifact_type` **and `title`** at all (Claim 26) — it is silent
on placement, so it corroborates the pair without carrying the top-level half.
R8's `metadata:` placement is a drafting slip.

*(The contract file itself does not yet exist — `ls framework/governance/` returns
23 entries and none is `FRONTMATTER_CONTRACT.md`. That is deliberately **not** the
ground for retiring R8: D1 is a live decision this plan feeds, so an
argument-from-absence would evaporate the moment the contract is authored.)*

### F-2 — `title:` only; top-level `id:` does not ride along

The identity carriers are already three deep for IPLAN and top-level `id:` would
be a fourth with no writer and no reader (Claims 8-11).

**This deliberately ships a new shape.** All five templates carrying a top-level
`title:` carry it as an adjacent `id:` + `title:` pair (Claim 1); after this
change three templates carry `title:` with no `id:`, which is a shape no template
has today. That is accepted, not overlooked: `title:` has evidence behind it —
every artifact writes one, no template declares it — while `id:` would deepen a
split this plan did not create. `test_layer_title_declared.py` pins the `title`
half only, so whichever way #588 resolves `id:`, it does not have to move the
guard.

### F-3 — All three layers, one bump

SPEC and TDD have the same gap as IPLAN (Claim 5) and in a sharper form: neither
declares any key above `metadata:` (Claim 6), and SPEC's `document_control` carries
no identifier field either (Claim 7) — so the full template names the document
nowhere at all. Shipping
IPLAN alone costs a second framework MINOR, a second fanout and a second founder
grant for a byte-identical edit. The per-bump founder OK for `0.47.0 → 0.48.0`
was granted 2026-08-31 and is recorded in the commit message.

## Approach

The change is three template edits plus a guard. **Two independent derivations
read a layer template's top-level keys, and they do not agree on what a section
is** — so "additive" has to be true for both.

1. **`STRUCT01` / the size budget.** `_load_section_targets` admits a top-level
   key only when its value is a mapping carrying an integer `_size_target`
   (Claim 16). A scalar `title:` fails the `isinstance(body, dict)` test on that
   same line. BRD is the live proof — it has carried a top-level `title:` since
   before the pin and derives 17 (Claim 17).
2. **The acceptance harness.** `template_sections()` admits **every** top-level
   key whose value is a mapping and whose name is not `metadata` — it does *not*
   require `_size_target` (Claim 24) — and its output is asserted hard against
   each golden's headings (Claim 25).

**Therefore `title:` MUST be a plain scalar string with no sub-keys.** Authored as
a mapping — the pervasive convention in these very templates, where `_guidance:`
children are everywhere, and this plan is itself adding a `_guidance` sentence —
the conformance tier would stay **green** while the acceptance tier went **red**
with `missing template sections ['title']` on all three goldens. The two tiers
disagree, and only the weaker one would catch it.

`metadata.total_sections` does not move: it counts numbered sections, and
`title:` is not one. GD-21 pins both numbers independently (Claim 18), so both
pins in `test_required_section_sets.py` stay untouched. A third guard is already
inert by construction — `test_skill_template_alignment.py` lists `title` in
`_HEADER_KEYS`, so it classifies the key as header metadata rather than a section
(Claim 33).

The `description` half is not cosmetic. `file_manifest` is what a resumed session
reads to pick its next file (Claim 23), and the keys it finds are `path`,
`order`, `status`, `session`, `verified` and sometimes `tdd_ref` (Claim 19) — a location, a
sequence and a state, with nothing saying what the file is *for*.

## File structure

| File | Change |
| --- | --- |
| `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` | add scalar top-level `title:` above `metadata:` (Claim 6) |
| `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | add scalar top-level `title:` above `metadata:` (Claim 6) |
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | add scalar top-level `title:`; add `description:` to each `files[]` entry (Claim 19); add the `session_summary` guidance sentence (Claim 20) |
| `tests/conformance/test_layer_title_declared.py` | **new** — every full layer template declares a scalar top-level `title:`. Loops `ARTIFACTS` directly, in the per-layer `subTest` shape of the derived-count pin (Claim 35) — note that pin loops a module-local literal, so copying it verbatim would lose the "a ninth layer cannot be skipped" property. Lives in `tests/conformance/` and not `tests/unit/` because nothing runs `tests/unit/` |
| `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md` | amend the R8 row (`:340`, Claim 13) in that file's own retirement convention — the VOID/Amended form its R3 row already uses (Claim 27) |
| `plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | tombstone the three places recording R8's `metadata:` placement and the #553 gate as live (Claim 28) |
| `plans/HANDOFF.md` | `:49` names #553 as gated on R8 and goes stale on merge (Claim 29). `:43` tallies *"Eleven are blocked on a founder decision"* and then adds #553 as a twelfth outside that count — reconcile the sentence, do not merely drop the line |
| `framework/VERSION` | `0.47.0` → `0.48.0` |
| `framework/governance/DECISIONS.md` | `GD-23` |
| `plans/DECISIONS.md` | `D-00NN` recording F-1..F-3 |
| `CHANGELOG.md` | docs of record |
| *script-rewritten, never by hand* | `platforms/*/FRAMEWORK_SPEC_VERSION`, 52 SKILL frontmatters, canonical playbooks, the plugin framework bundle, `docs/PARITY.md`, `CLAUDE.md`, `README.md`, both platform READMEs, and the pinned literal in `tests/conformance/platforms/test_plugin_release_metadata.py` (Claim 31) |

## Implementation sequence

1. **Guard first.** Write `tests/conformance/test_layer_title_declared.py` and
   confirm it is **RED** on all three layers before any template edit. A guard
   that has never failed has not been shown to measure anything. Assert the key
   is a **scalar**, not merely present — that is the property Claim 24 makes
   load-bearing, and a presence-only guard would pass the mapping form that
   reddens acceptance.
2. Add the three scalar `title:` keys.
3. Add IPLAN's `files[].description` — on **all three** `files[]` entries, not
   only the two that carry `tdd_ref` (Claim 19) — and the `session_summary`
   guidance line.
4. **`bash tools/sync-plugin-framework.sh`.** Not optional and not deferrable to
   step 6: the bundle guard byte-compares every file under the four synced
   subtrees (Claim 36), so the three template edits redden it immediately, and
   the conformance suite is an `always_run` pre-commit hook (Claim 37) — so the
   template-edit **commit itself** is blocked until the bundle is re-synced. The
   script is version-independent and idempotent, so step 6 re-running it is free.

   **Stage the output in the same breath:**

   ```sh
   bash tools/sync-plugin-framework.sh && git add \
     framework/layers/06_SPEC framework/layers/07_TDD framework/layers/08_IPLAN \
     platforms/claude-code-plugin/framework platforms/claude-code-plugin/tools
   ```

   Unlike `sync-version-refs.sh`, this script performs **no `git add`** of its own
   (Claim 40). `pre-commit` reads the **staging area** and stashes unstaged changes
   to tracked files, so syncing without staging leaves the guard red against a
   stashed tree — and its failure message tells you to re-run the very script you
   just ran. **Both sides must be staged**, and for symmetric reasons: stage only
   the templates and the regenerated bundle is stashed away; stage only the bundle
   and the canonical edits are stashed, so the new bundle is compared against a
   HEAD-state `framework/`. The two destination paths above are the complete write
   set (Claim 21), and `git add <dir>` is the right form because the script
   regenerates by `rm -rf`, so deletions must be staged too.
5. Run `tests/conformance` **and** `tests/acceptance/deterministic` before the
   version bump, to isolate the template edits from the fanout. Both tiers must
   be green and both pins in `test_required_section_sets.py` unchanged. Running
   only the conformance tier here would miss the failure Claim 24 describes.
6. **Bump with `python3 tools/bump_version.py 0.48.0`** — the repo's purpose-built
   tool, not the hand sequence. It bumps the canonical playbooks itself *before*
   syncing (Claim 32), which is why its bundle-first sync order is safe and does
   **not** contradict `CLAUDE.md`'s documented order (Claim 22): that order
   governs the manual path, where `sync-version-refs.sh` is what bumps the
   playbooks. It also fixes the plugin README ahead of the pre-commit conformance
   hook. Do not mix the two paths. Its closing reminder that the
   `test_plugin_release_metadata.py` hard-pin is a manual step is **stale**
   (Claim 39) — `sync-version-refs.sh` already wrote it (Claim 31). Do not
   hand-edit that literal.
7. `GD-23` + `plans/DECISIONS.md` + `CHANGELOG.md` + `plans/HANDOFF.md`, and the
   R8 amendments from the File-structure table. **Then `bash
   tools/sync-plugin-framework.sh` one final time**: `framework/governance/` is
   inside the synced subtrees (Claim 36), so writing GD-23 after step 6's last
   sync leaves the bundled `DECISIONS.md` stale and the guard red. Stage its output
   too (Claim 40).

## Verification

- `python3 -m pytest tests/conformance -q` — baseline on this branch is
  **453 passed / 911 subtests**.
- `python3 -m pytest tests/acceptance/deterministic -q` — baseline **64 / 56**.
  Load-bearing, not routine: this is the tier Claim 24 puts at risk.
- `python3 -m pytest tests/unit -q` — baseline **196 / 231**.
- `PYTHONPATH=tools python3 -m pytest tools/sdd_doc_lint/tests -q` — baseline **6**.
- `PYTHONPATH=tools python3 -m sdd_doc_lint examples/url-shortener/docs/` — the
  corpus cross-check CLAUDE.md requires when a plan touches template shape.
  Baseline is **1 error across 1 file** plus known warnings (deferred corpus
  debt). Expect **no change** — not because the corpus already authors `title:`,
  which would confuse the template's YAML key with the artifact's `.md`
  frontmatter, but because `_load_section_targets` is the linter's **only** read
  of a layer template (Claim 30) and it consumes `_size_target` / `_required*`
  and nothing else. No other template key can move a corpus finding.
- `pre-commit run --all-files` — baseline is all 19 hooks green.
- Run `bash tools/sync-plugin-framework.sh` **twice** at the very end and confirm
  the second run leaves a clean tree — and that `git status` is clean, which is the
  half a sync alone does not give you (Claim 40). Both syncs are already clean by
  the time Verification runs, since step 7 now closes with one; the twice-run form
  is kept because it is the check that would have caught the ordering defect, not
  because a diff is expected here.

## Docs to update

`CHANGELOG.md`, `framework/governance/DECISIONS.md` (GD-23), `plans/DECISIONS.md`,
`plans/HANDOFF.md`, plus the two R8-recording plan surfaces in the File-structure
table. `docs/PARITY.md`, `CLAUDE.md` and `README.md` move by script, not by hand —
and `docs/PARITY.md` must **not** be hand-edited first, because it is the
`fw_prev` detector's own source and editing it strands the whole fanout at exit 0.

**Deliberately not changed:** `framework/layers/08_IPLAN/README.md`'s worked
manifest entry (Claim 34) already elides `session` and `verified` — it illustrates
`tdd_ref`, not the full field list — so it is not "a field short" and adding
`description` there would misrepresent it as an exhaustive shape. The same holds for
`platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:100`, which enumerates
`order`, `status`, `session`, `verified` (Claim 41): it is already a key short —
`tdd_ref` shipped under GD-16 without touching it — and `:51` names the template as
the **source of truth** (Claim 42), so it is prose about the template rather than a
second declaration of it.
Adjudicated here so a later pass does not re-raise it as an omission.

## Risks

| Risk | Mitigation |
| --- | --- |
| **`title:` authored as a mapping reddens the acceptance tier while conformance stays green** | The single highest-value risk here. Step 1's guard asserts scalar-ness; step 5 runs both tiers before the bump (Claims 24-25) |
| A top-level key silently joins `STRUCT01`'s required set | Claims 16-17 say it cannot; step 5 tests the assumption in isolation |
| The `description` key collides with an existing per-file field | The existing key vocabulary is `path`, `order`, `status`, `session`, `verified`, `tdd_ref` (Claim 19) — no collision |
| A future `session_summary` field re-creates the §5 collision #553 finding 3 warns about | The guidance sentence names it and states the distinction (Claim 20) |
| Retiring R8 strands documents that record it as live | Three surfaces identified and taken in this PR (Claims 27-29) |
| Mixing the two bump paths | Step 6 commits to `bump_version.py` and says why both orders are individually correct (Claims 22, 32) |
| A `framework/**` edit reddens the byte-identical bundle guard and blocks its own commit | Step 4 syncs the bundle before any test run; step 7 syncs again after the governance write (Claims 36-37) |
| The idempotence check reports a false defect | Verification keeps the twice-run form because it is the check that would have caught the ordering defect — not because a diff is expected, since step 7 now closes with its own sync |
| A reproduction run stages 100+ collateral files | Any sync-script reproduction runs in a throwaway clone, never the working tree |

## Claim ledger

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | Five full layer templates declare a top-level `title:`, each as an adjacent `id:` + `title:` pair | `title:` | `framework/layers/01_BRD/BRD-TEMPLATE.yaml:18` |
| 2 | All eight MVP templates put `title` under `document_control` instead | `title:` | `framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml:6` |
| 3 | The authored corpus IPLAN carries a top-level `title:` the template never declared | `title:` | `examples/url-shortener/docs/08_IPLAN/IPLAN-01.md:2` |
| 40 | NEW@pass3 — `sync-plugin-framework.sh` performs no `git add`, unlike `sync-version-refs.sh`, which re-stages precisely because *"pre-commit reads from the staging area"* | `Re-stage anything we touched` | `scripts/sync-version-refs.sh:463` |
| 41 | NEW@pass4 — the plugin IPLAN skill's manifest-key prose is already a key short: it omits `tdd_ref`, which shipped under GD-16 | `session`, `verified` | `platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:100` |
| 42 | NEW@pass4 — that same skill names the template as the source of truth, so its prose is not a second declaration | `Template (source of truth)` | `platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:51` |
| 5 | The corpus SPEC and TDD artifacts also carry a top-level `title:` | `title:` | `examples/url-shortener/docs/06_SPEC/SPEC-01.md:2` |
| 6 | SPEC and TDD templates open at `metadata:` with no key above it | `metadata:` | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:6` |
| 7 | SPEC's `document_control` carries no identifier field at all | `document_control:` | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml:70` |
| 8 | IPLAN's `document_control` carries `iplan_id` — the only full template that does | `iplan_id:` | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:71` |
| 9 | The IPLAN golden authors `iplan_id`, so removing it is not an additive edit | `iplan_id:` | `tests/acceptance/fixtures/layer_08_iplan/valid/IPLAN-01_golden.yaml:13` |
| 10 | Goldens carry `doc_id` and `metadata.artifact_id` as two further identity carriers | `doc_id:` | `tests/acceptance/fixtures/layer_06_spec/valid/SPEC-01_golden.yaml:2` |
| 11 | The linter reads `doc_id` from frontmatter; nothing reads a top-level `id` | `doc_id` | `tools/sdd_doc_lint/__init__.py:1539` |
| 12 | OKF D1 declares *the required **top-level** keys* — so D1 selects top-level, which is what R8 cites and contradicts | `top-level` | `plans/OKF-CONFORMANCE-001-DESIGN.md:121` |
| 13 | R8 places `title` in `metadata:` and cites the OKF D1 contract as its authority | `R8` | `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md:340` |
| 14 | No template declares `metadata.title` | `metadata:` | `framework/layers/01_BRD/BRD-TEMPLATE.yaml:24` |
| 15 | OKF D2 settles that the rule reads **top-level** — "the same key the linter reads" | `top-level` | `plans/OKF-CONFORMANCE-001-DESIGN.md:146` |
| 16 | `STRUCT01`'s required set is derived only from top-level keys whose value is a mapping carrying an integer `_size_target` | `_load_section_targets` | `tools/sdd_doc_lint/__init__.py:530` |
| 17 | BRD derives 17 required sections while carrying a top-level `title:` — the live proof a scalar key is skipped | `EXPECTED` | `tests/conformance/test_required_section_sets.py:52` |
| 18 | `total_sections` and the derived required count are pinned as two separate measurements | `_declared` | `tests/conformance/test_required_section_sets.py:211` |
| 19 | `file_manifest.files[]` entries carry at most six keys and none states intent — the third entry carries five, having no `tdd_ref` | `files:` | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:146` |
| 20 | `session_handoff` is a top-level IPLAN section, so a `document_control` field of that name would collide | `session_handoff:` | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:217` |
| 21 | `tools/sync-plugin-framework.sh` writes to exactly two destinations: four subtrees (`layers`, `governance`, `registry`, `playbooks`) plus a named root file into `platforms/claude-code-plugin/framework`, and three named tools files into `platforms/claude-code-plugin/tools`. It is the write side of the guard in Claim 36 | `TOOLS_FILES` | `tools/sync-plugin-framework.sh:33` |
| 22 | The manual propagation order `VERSION` → `sync-version-refs.sh` → `sync-plugin-framework.sh` is load-bearing; reversing it lands drifted playbooks | `Propagation order` | `CLAUDE.md:741` |
| 23 | The stateless-executor protocol this `description` serves reads the manifest for the next file | `file_manifest` | `platforms/claude-code-plugin/skills/doc-iplan/SKILL.md:129` |
| 24 | NEW@pass1 — the acceptance harness admits **every** top-level mapping key except `metadata` as a section, without requiring `_size_target` | `for key, value in data.items()` | `tests/acceptance/_harness.py:249` |
| 25 | NEW@pass1 — that derived set is asserted hard against each golden's headings | `assert_template_sections_present_in_golden` | `tests/acceptance/_harness.py:384` |
| 26 | NEW@pass1, reworded@pass2 — Correction 4 establishes that templates receive `artifact_type` **and `title`**. It says nothing about placement; top-level comes from D1 (Claim 12) and D2 (Claim 15) | `Correction` | `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md:321` |
| 27 | NEW@pass1 — that design's R-table has an established retirement convention: the row is retained and marked VOID | `VOID` | `plans/IPLAN-LAYER-REVIEW-001-DESIGN.md:335` |
| 28 | NEW@pass1 — `TEMPLATE-COMPLETENESS-001` records R8's `metadata:` placement and the #553 founder gate as live fact | `R8 places` | `plans/TEMPLATE-COMPLETENESS-001-PLAN.md:40` |
| 29 | NEW@pass1 — the handoff names R8 as the owner of the #553 gate | `R8 owns` | `plans/HANDOFF.md:49` |
| 30 | NEW@pass1 — `_load_section_targets` is the linter's only read of a layer template | `tpl = registry.parent.parent` | `tools/sdd_doc_lint/__init__.py:514` |
| 31 | NEW@pass1 — `sync-version-refs.sh` rewrites the pinned literal in the plugin release-metadata test | `test_plugin_release_metadata.py` | `scripts/sync-version-refs.sh:352` |
| 32 | NEW@pass1 — `bump_version.py` bumps the canonical playbooks itself, so its bundle-first sync order carries the new values | `bundle copies follow via sync` | `tools/bump_version.py:99` |
| 33 | NEW@pass1 — the skill/template alignment guard already lists `title` as header metadata, not a section | `_HEADER_KEYS` | `tests/conformance/platforms/test_skill_template_alignment.py:38` |
| 34 | NEW@pass1 — the IPLAN README's worked manifest entry already elides `session` and `verified` | `tdd_ref:` | `framework/layers/08_IPLAN/README.md:74` |
| 35 | NEW@pass1, re-pointed@pass2 — the per-layer loop the new guard should copy (the roster pin at `:194` compares sets; it does not iterate) | `test_derived_required_counts_match_the_pins` | `tests/conformance/test_required_section_sets.py:198` |
| 36 | NEW@pass2 — the bundle guard byte-compares every file under `layers`, `governance`, `registry`, `playbooks` against the plugin copy | `test_bundle_is_byte_identical` | `tests/conformance/platforms/test_plugin_framework_bundle.py:61` |
| 37 | NEW@pass2 — the conformance suite runs as an `always_run` pre-commit hook, so a red bundle guard blocks the commit itself | `always_run` | `.pre-commit-config.yaml:128` |
| 38 | NEW@pass2 — `markdownlint --fix` runs on every commit; it is what corrupts an un-backticked `__init__.py` into `**init**.py` | `--fix` | `.pre-commit-config.yaml:75` |
| 39 | NEW@pass2 — `bump_version.py`'s closing reminder still calls the release-metadata pin a manual step | `Reminder` | `tools/bump_version.py:152` |

## Review log

### Pass 1 - 2026-08-31 - independent

Dispatched `verified-planning-reviewer`, fresh context. **8 load-bearing findings,
all folded; every one re-verified against source before folding.**

1. **The safety argument covered one derivation, not two.** The acceptance
   harness derives sections from `isinstance(value, dict)` alone, so a `title:`
   authored as a mapping would redden acceptance while conformance stayed green.
   Folded as Claims 24-25, the Approach rewrite, a Scope constraint, step 1's
   scalar assertion, step 4's second tier, and the top Risks row. **This was the
   finding that justified the pass** — the original step 4 explicitly ran only the
   tier that cannot see it.
2. **Claim 15 cited a line with nothing to do with the claim** (`__init__.py:1447`
   is a `STALE01` finding about `last_audited_spec`). Re-cited to the OKF design's
   own text at `:146`.
3. **Claim 13's R8 line was stale by exactly the drift a sibling plan flagged** —
   `:328` → `:340`. `TEMPLATE-COMPLETENESS-001-PLAN.md:276` already warns the row
   moved; this plan had re-introduced the pre-shift number.
4. **Claim 12's citation did not support it, and the R8 retirement stood on the
   wrong ground.** Re-cited to D1's own "required top-level keys" at `:121`, and
   F-1 reframed from *"the contract does not exist"* — which evaporates the moment
   the contract is written, and this plan *feeds* it — to *"R8 contradicts the
   authority it cites"*. Correction 4 added as supporting Claim 26.
5. **Retiring R8 stranded three surfaces** the plan did not update. Added to
   File structure, Docs to update and Risks as Claims 27-29, using the design's
   own VOID convention.
6. **The corpus-lint expectation was right for a wrong reason** — it conflated
   the template's YAML key with the artifact's `.md` frontmatter. Restated on
   Claim 30: `_load_section_targets` is the linter's only template read.
7. **The plan claimed to ship "the shape five layers already ship" while shipping
   half of a pair that has never shipped as a half.** Claim 1 and F-2 now say so
   explicitly and record it as a deliberate new shape.
8. **The fanout radius was under-stated and the bump path unnamed.** Added
   `CLAUDE.md`, `README.md` and the release-metadata literal; step 5 now commits to
   `tools/bump_version.py`. Investigating this surfaced an apparent contradiction
   with `CLAUDE.md`'s documented order — resolved, not papered over: the tool bumps
   canonical playbooks itself first (Claim 32), so both orders are correct for
   their own path.

Also folded, non-load-bearing: the guard iterates `ARTIFACTS` (Claim 35); it lives
in `tests/conformance/` because nothing runs `tests/unit/`; and the IPLAN README's
manifest example is recorded as a **deliberate** non-change (Claim 34) rather than
left for a later pass to re-raise.

Verified clean by the pass and not re-examined: "framework MINOR, no plugin version
move"; Claims 16/17/18; that no surface errors on an unexpected top-level template
key; and that `description:` collides with nothing in Hermes, the carrier test or
the ID coordinator.

**Ledger grew 23 → 35.** Per the fold discipline that is normally a defect signal.
Here it is the reviewer's completeness brief landing as intended: 11 of the 12 new
rows are consumers the first draft never considered, and one (Claim 12) is a
re-citation. No new *design* was added — the only behavioural change is the
scalar-`title:` constraint, which narrows the plan rather than widening it.

**Result:** folded; pass 2 dispatched.

### Pass 2 - 2026-08-31 - independent

Dispatched `verified-planning-reviewer`, fresh context, briefed that rows marked
`NEW@pass1` were unreviewed surface. **4 load-bearing findings, all folded; each
re-verified against source before folding.**

The pass **confirmed the central safety argument** and swept for the third consumer
it might have missed: there is none. Hermes YAML-loads a layer template but reads
only `metadata.*` and a `sections:` list layer templates do not have; the alignment
guard excludes `title` twice over; both vendored linter mirrors are byte-identical
by their own test; and no test asserts template key ordering, so `title:` above
`metadata:` is safe. Claim 32's bump-order resolution also verified end to end, as
did `GD-23` / `0.48.0` being the right next values and the R8 census being complete.

1. **Step 4 could not have been green.** The template edits redden
   `test_bundle_is_byte_identical`, which byte-compares all four synced subtrees
   (Claim 36) — and the conformance suite is an `always_run` pre-commit hook
   (Claim 37), so the template-edit **commit itself** was blocked. A
   `sync-plugin-framework.sh` run is now step 4, ahead of the two-tier run.
2. **Step 6's GD-23 write landed after the last sync.** `framework/governance/` is
   inside the synced subtrees, so the bundled `DECISIONS.md` would go stale and the
   same guard red. Step 7 now closes with a final sync.
   This also falsified the plan's own idempotence check: as written, the re-run
   *legitimately* produced a diff, so the stated pass condition would have read as
   a defect. Restated as a twice-run sync.
3. **The plan's own `pre-commit` run would have corrupted three of its citations.**
   Rows 11, 16 and 30 carried un-backticked `tools/sdd_doc_lint/__init__.py:NNNN`,
   and `markdownlint --fix` (Claim 38) rewrites `__init__.py` → `**init**.py`,
   failing the citation gate with the misleading `path '.py' does not exist`. This
   is a documented repo trap that 10 plan files already carry; every citation in the
   ledger is now backticked.
4. **Claim 26 asserted a placement its citation does not state.** Correction 4 says
   templates receive `artifact_type` and `title`; it is **silent on placement**.
   Both the claim and F-1's sentence now say so. F-1's conclusion is unchanged — it
   stands on D1 (Claim 12) and D2 (Claim 15), not on Correction 4.
   ⚠️ **This is Pass 1 finding 4 reproduced by the fold that fixed it** — a citation
   stretched one step past what it says. Worth naming as the recurring defect of
   this plan rather than filing as a one-off.

Non-load-bearing, also folded: Claim 35 re-pointed (the roster pin compares sets,
it does not iterate); Claim 19 corrected — the third `files[]` entry carries five
keys, not six, so step 3 now says **all three** entries; `bump_version.py`'s stale
manual-step reminder recorded as Claim 39 so an implementer does not hand-edit a
literal the script already wrote; and the `plans/HANDOFF.md` row now says to
reconcile its "Eleven are blocked" tally rather than just delete the #553 line.

The pass could not re-derive the Verification baselines (no shell). They were
measured in-session on this branch before any edit: conformance **453 / 911**,
acceptance-deterministic **64 / 56**, unit **196 / 231**, `sdd_doc_lint` **6**,
corpus lint **1 error across 1 file**, `pre-commit` **19 hooks green**. The one
figure the pass could check by inspection — 19 commit-stage hooks — it confirmed.

**Ledger grew 35 → 39.** Four rows, all consumers of the commit path that the first
two drafts never modelled. No design was added; findings 1 and 2 **reordered** the
implementation rather than extending it.

**Result:** folded; pass 3 dispatched — pass 2 raised load-bearing findings, so the
loop had not converged.

### Pass 3 - 2026-08-31 - independent

Dispatched `verified-planning-reviewer`, fresh context, scoped to the second fold's
surface and told which questions prior passes had settled. **2 load-bearing
findings, both folded; both re-verified against source.** The pass explicitly
confirmed the design layer clean — no other file the plan edits lives inside a
synced subtree, `GATE-SPEC` E005/E008 are PR-diff-scoped so the intermediate commits
cannot trip them, and the new guard needs no test-module registration.

1. **The 6→7 renumber moved the sequence but not its references.** Three Risks
   mitigations and one line inside step 4 still pointed at the old numbering — including
   the mitigation for the plan's own self-declared highest-value risk, which pointed at
   a step that runs no tests. Corrected. This is the failure mode the fold discipline
   names explicitly: **subtractive folding is safer on facts and more dangerous to
   references.** Two folds produced zero surviving factual errors in the cited body and
   four broken internal pointers.
2. **Step 4's remedy was incomplete, and would have reproduced the exact symptom it
   was inserted to remove.** `tools/sync-plugin-framework.sh` performs **no `git add`**,
   unlike `scripts/sync-version-refs.sh:463`, which re-stages with the comment *"pre-commit
   reads from the staging area"* (Claim 40). An implementer who ran the sync and then
   staged only the three templates would commit against a tree where the regenerated
   bundle had been stashed back to HEAD — guard red, with a message telling them to
   re-run the script they had just run. Both sync invocations now stage their output.

Minor items also folded: Claim 35's File-structure sentence (the derived-count pin
loops a module-local literal, not `ARTIFACTS`, so copying it verbatim would lose the
property the sentence claimed); the twice-run rationale, stale once step 7 gained its
own sync; Claim 21, orphaned and understating its own source, now reworded as the
write side of Claim 36; and `doc-iplan/SKILL.md:100`'s key enumeration adjudicated as
a deliberate non-change, the same treatment Claim 34 gave the README.

**Ledger grew 39 → 40.** One row.

⚠️ **The 3-pass cap is reached and pass 3 was not clean, so the loop stops here by
rule rather than by convergence.** The trend is 8 → 4 → 2 and the character of the
findings changed completely — passes 1 and 2 invalidated reasoning, pass 3 found only
broken internal references and one shell mechanic, with the design layer explicitly
verified sound. A fourth pass scoped to this fold's own surface is the natural next
step, but that is a human call, not one this plan may make for itself.

**Result:** 2 load-bearing findings folded; cap reached, surfaced to the founder.

### Pass 4 - 2026-08-31 - independent

Founder authorized one further pass after the cap, scoped narrowly to the pass-3
fold surface and the plan's internal wiring rather than to the whole plan.

**Zero load-bearing findings.** The pass confirmed Claim 40 end to end and — the
question that mattered — established that the two staged paths are the script's
**complete** write set: `tools/sync-plugin-framework.sh:21` and `:32` are its only
destinations, `ROOT_FILES` copies *into* the first rather than to a third, and the
`case` suffix guard pins both. It also confirmed the renumber damage from pass 3 is
fully repaired: all eleven `step N` references in the body resolve, ledger IDs run
1-40 unique and ascending, and Claims 19, 26, 35, 38 and 40 carry no overreach.

Five minor items, all folded:

1. **Claim 21 under-described its own script** — it named the subtrees but not the
   three vendored tools files, so nothing in the ledger justified the second path in
   step 4's stage command. Now covers both destinations and is cited from step 4.
2. **Risks row 8 contradicted the Verification text it pointed at** — it still
   carried the pass-2 rationale ("step 7 legitimately dirties the tree") after pass 3
   gave step 7 its own closing sync. Restated.
3. **F-3 stretched Claim 7 one step.** Claim 7 is scoped to *SPEC's* `document_control`
   and is silent on TDD and on `title`; F-3 cited it for both. The underlying fact
   holds — TDD declares no `title:`/`id:`/`tdd_id:` anywhere — so only the citation was
   short. Now cites Claim 6 alongside it. **This is the plan's recurring defect
   appearing a third time**, at a row the brief had not listed; naming it in pass 2 did
   not prevent it, which is the more useful lesson than the fix.
4. **The `doc-iplan/SKILL.md` adjudication had no ledger row**, unlike the README
   adjudication it mirrors. Added as Claims 41-42, so the gate now covers those two
   line numbers instead of trusting prose.
5. **Step 4's stage command was the mirror of the defect pass 3 removed** — it staged
   the sync output but not the three template edits, so an implementer following it
   literally would have the canonical edits stashed and the new bundle compared against
   a HEAD-state `framework/`. Graded minor by the pass; folded as load-bearing here,
   because it changes the command an implementer runs. Both sides are now staged, with
   the symmetry stated.

**Ledger grew 40 → 42.** Two rows, both closing a gate gap rather than adding design.

**Result:** ready — no load-bearing findings.
