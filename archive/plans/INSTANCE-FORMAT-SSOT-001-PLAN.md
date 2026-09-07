# INSTANCE-FORMAT-SSOT-001 — instance format gets one normative source, and a guard that keeps it there

| Field | Value |
| --- | --- |
| Plan state | **In Progress** — 2026-08-28. Three independent passes recorded (9/6/7 findings, all folded); founder accepted the plan as folded at the OPS-0066 cap rather than authorising a fourth. |
| Owner | framework |
| Issues | **#566** (census), **#558** (release provenance). Enablement, not this plan: **#564**, **#565** |
| Version impact | framework **MINOR** `0.43.0 → 0.44.0` |
| Change level | **C2** (GATE-SPEC) |
| Supersedes | `plans/GD15-CARRIER-LINT-001-PLAN.md` (ABANDONED — see its Review log) |
| Unblocks | the first framework tag since `v0.41.3` |

## Objective

GD-15 (spec `0.43.0`) made YAML the mandatory **instance** format and, in the same entry,
declined to adopt the frontmatter contract that makes an instance legible to any rule
(Claim 1). Measured: a conformant YAML BRD produces 17 `STRUCT01` errors and a vacuous `COV01`
pass (Claim 2). The spec mandates a format its own gate rejects, so no release can honestly be
tagged.

Two prior designs failed. This one applies the pattern **this repo already ratified for exactly
this defect class** — GD-09, *"Single source, enforced by deletion"* (Claim 3):

> Re-specifying per layer is what allowed the drift; updating the … stale copies would only
> reset the drift clock.

## Scope

**In scope:**

1. **One normative source, cross-referenced — not deleted.** `LAYER_REGISTRY.yaml` `extensions`
   is the sole **authority** for instance format. Each carrier keeps an in-layer statement of
   the *value* and cross-references the registry, per **GD-09 rule 2** (Claim 18):
   *"Every mandating layer states its contract in-layer."* `01_BRD/README.md:146` is the shipped
   model — it states the shape, names the single source, and says "Do not re-specify it here."
   (`NEW@pass1` — the first draft proposed deleting the in-layer statements, which cites GD-09
   against itself: GD-09 deleted a re-specified *algorithm*, never the layer's own contract.)
2. **`GD-17`** — the erratum, whose effective condition is **outcome-based, not a component
   list** (D6, `NEW@pass3`). Every enumerated version of this condition has been under-counted:
   `doc_id` alone (Pass 2 F4), then `doc_id` + a carrier-aware structural check (Pass 3 F3).
3. **Two filename claims, repaired differently** (Claims 6 and 16, `NEW@pass1`):
   - `layers/01_BRD/README.md:119` — `BRD-NN_*.md` → `.yaml`. It contradicts `:125` six lines
     later; `.yaml` is correct and consistent.
   - `04_BDD/BDD-TEMPLATE.yaml:148` — **the extension claim is removed, not substituted.** The
     sentence describes a ```yaml **fence**, and `_YAML_FENCE` is the sole in-force extraction
     path for `_extract_bdd_scenarios`, `BDD-SCHEMA-001` and the seed stripper (Claim 19). It is
     therefore an accurate description of the **current** carrier, not a defect — and under
     GD-17 the mandate is not yet effective, so "correcting" it to `.yaml` would assert a form
     the gate rejects. The repair is *"the produced BDD document"*: no extension claim, still
     accurate about the fence, and invisible to the guard. Rewriting the carrier itself stays
     #564 work.
4. **A conformance guard** — every `<TYPE>-NN…` instance filename *mentioned in file content*
   under `framework/**` uses an extension in that layer's `extensions`, with **two** exemptions
   (`NEW@pass1`): (a) **mention-level** index exemption — a `<TYPE>-00_*index*` token is exempt
   **wherever it appears**, not merely inside an index file; (b) `governance/DECISIONS.md`, a
   ratified historical record (Claim 21).
5. `VERSION` bump, fanout, `CHANGELOG` `0.44.0` entry with the #558 narration.
6. Re-point `TEMPLATE-COMPLETENESS-001` to `0.45.0` and `GD-17`→`GD-18` (Claims 8, 9).

**Out of scope — the enablement, sequenced behind `OKF-CONFORMANCE-001` D1, one line each:**

- The frontmatter/`doc_id` contract itself (#564; D1 is `Draft`, Claim 5).
- The four carrier-aware linter primitives, the BRD §7 `band`/`realized_by` keys, and the
  acceptance re-baseline (#564).
- `FMT01` / `extensions` enforcement (#565) — enforcing a mandate this PR gives a later
  effective date would be self-contradicting.
- `governance/DECISIONS.md:31`'s `IPLAN-01.md`: descriptive of a real corpus artifact inside a
  ratified record, not a format assertion. Not rewritten.

## Approach / Design

### D0 — The carrier list, written out (`NEW@pass1`)

Two prior designs died on an unenumerated count, so it is a list, not a figure:

| # | Carrier | Citation | Disposition |
| --- | --- | --- | --- |
| C1 | `DOC_GOVERNANCE_CORE.md` Principle 2 | `:6` (Claim 4) | keeps its two carve-outs; defers to the registry for per-layer values |
| C2 | `DOC_GOVERNANCE_CORE.md` §Template Policy | `:43-44` | defers |
| C3 | `LAYER_REGISTRY.yaml` `extensions` + header | `:18`, `:23-27` (Claim 7) | **the authority** |
| C4 | GD-15 Decision text | `DECISIONS.md:90-100` | ratified record — **not rewritten**; GD-17 amends it |
| C5 | `layers/01_BRD/README.md` §Document Formats | `:125` | states `.yaml` + cross-references C3 |
| C6 | `governance/ID_NAMING_STANDARDS.md` File-Naming table | `:277` (Claim 24) | **carrier** — asserts `.yaml` twice, normatively; states the value + cross-references C3 (`NEW@pass2`) |
| C7 | `layers/04_BDD/BDD-00_index.TEMPLATE.md` §File Format | `:43-45` (Claim 25) | **carrier, and guard-blind** — prose with no filename token, so it can drift to `.md` and V2 stays 0 forever; states the value + cross-references C3 (`NEW@pass2`) |

**Arithmetic:** **seven** carriers — C3 is the authority, C1/C2/C5/C6/C7 defer, C4 is a ratified
record that GD-17 amends rather than edits. (`NEW@pass2` — the first draft said five and its
prose said "the other four defer", which only balanced by miscounting C4 as a deferrer.)

⚠️ **C6's earlier exclusion rationale was false** (`NEW@pass2`). It claimed `:277` "uses a generic
`{TYPE}-NN` placeholder … so the guard cannot see it". The line asserts `.yaml` **twice** and its
Example cell carries a literal `BRD-01_kyc_onboarding.yaml` that the guard *does* see — it passes
only because `.yaml` is conformant. T3 was already editing it, so the table and the task set had
not reconciled.

**Bounded scan for C7's shape** (`NEW@pass2`): `grep -rnE '^#+ *(File Format|Document Formats)'`
over `framework/` returns **exactly two** — C5 and C7. Every other layer states the value only
through *filename patterns*, which the guard sees, so they need no cross-reference. The list is
**+2, not +7**.

**Out of the list, deliberately:** `framework/docs/AIDOC.md:105`
(`docs/<NN>_<LAYER>/<TYPE>-01.md`) is a **Platform-B capability table**, covered by the spec-only
caveat in D5.

**Restored exclusion (`NEW@pass1`):** `BRD-TEMPLATE.yaml:582-583` makes the *authored Markdown
form* of §7 NORMATIVE, ratified into GD-14 (`DECISIONS.md:168`). The first draft dropped this
exclusion when it inherited the abandoned plan's Out-of-scope list. It is **#564 work** and
touching it re-opens GD-14's counting rule.

### D1 — Cross-reference, not reconciliation

**Seven** surfaces assert the mandate (D0; `NEW@pass3` — the first draft said five). Editing all
seven to agree leaves seven places able to drift; GD-09 measured that outcome and rejected it.
Instead **C3 is the authority, five defer (C1/C2/C5/C6/C7), and C4 is a ratified record GD-17
amends rather than edits**. This also makes the erratum tractable: the effective condition is
written **once**, in GD-17 (D6).

### D2 — The guard must exempt index docs, or it flags correct files

`LAYER_REGISTRY.yaml:23-27` sanctions `.md` index docs for layers 01-07 (Claim 7). A naive
"every `<TYPE>-NN` filename matches `extensions`" rule flags **9** correct index references
(`NEW@pass2`; the first draft said 7). The distinction is the exemption's **unit**: 7 of those 9
sit *inside* an index file — the number a **file-level** exemption catches — while 2 sit in
non-index files (`BRD-TEMPLATE.yaml:137`, `ID_NAMING_STANDARDS.md:275`). Only a **mention-level**
exemption catches all 9. The exemption already exists in code as `_is_index_doc` (Claim 10) and
the guard reuses that notion rather than inventing one.

⚠️ This is why the census in #566 was first reported as "18 surfaces, 6 self-contradictory". With
the exemption applied the true figures are **7 carriers and 2 filename claims** (D0; Claims 6 and
16). `NEW@pass3` — an earlier fold said "5 carriers and 2 defects"; the count moved again at
Pass 2 (C6, C7) and "defects" was wrong because the BDD claim is an accurate description of the
in-force carrier, not a defect. The guard is written against the corrected measurement.

### D3 — `0.44.0` here; `TEMPLATE-COMPLETENESS-001` to `0.45.0`

The blocker relief must precede the first tag. Eleven lines in that plan mention `0.44.0`
(Claim 8); **three are historical** — `:253`, `:364`, `:370`, the last two inside one dated
amendment block — and are annotated, not edited. Two of the eight forward-looking lines also
carry the *from* version, so they become `0.44.0 → 0.45.0`, not `0.43.0 → 0.45.0`.
Its four `GD-17` references become `GD-18` (Claim 9).

### D4 — #558 narration

Founder decision (Claim 29 — recorded on the issue 2026-08-28, verifiable by probe): tag neither `0.42.0` nor `0.43.0`; the
`0.44.0` entry states that `0.42.0` was never a value of `framework/VERSION`, that `0.43.0`
shipped untagged, and that `framework/v0.44.0` is the first tag since `v0.41.3`. **Edit no
published entry.**

## File structure

### Modified

| Path | Change |
| --- | --- |
| `framework/registry/LAYER_REGISTRY.yaml` | header: sole-normative-source statement + the effective condition |
| `framework/governance/DOC_GOVERNANCE_CORE.md` | Principle 2 + §Template Policy defer to the registry and carry the condition |
| `framework/governance/DECISIONS.md` | `GD-17` |
| `framework/layers/01_BRD/README.md` | `:119` `.md` → `.yaml`; `:125` states the value + cross-references C3 |
| `framework/governance/ID_NAMING_STANDARDS.md` | `:277` cross-references C3 (`NEW@pass2`, C6) |
| `framework/layers/04_BDD/BDD-00_index.TEMPLATE.md` | `:43-45` §File Format cross-references C3 (`NEW@pass2`, C7) |
| `CLAUDE.md`, `ROADMAP.md` | current-state token / shipped-work bullet (`NEW@pass2`) |
| `framework/layers/04_BDD/BDD-TEMPLATE.yaml` | `:148` — **drop the extension claim** (`BDD-NN.md` → "the produced BDD document"). ⚠️ **Do NOT substitute `.yaml`** (`NEW@pass2`; the first draft's table said `→ BDD-NN.yaml`, contradicting Scope 3 and T2 — and `.yaml` is registry-conformant, so no V-row would have caught it) |
| `framework/VERSION` | `0.43.0` → `0.44.0` |
| `CHANGELOG.md` | `0.44.0` entry + #558 narration |
| `plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | 8 forward-looking version refs + 4 `GD-17`→`GD-18`; 3 historical annotated |
| `plans/DECISIONS.md`, `plans/HANDOFF.md` | record the #558 decision; clear "needs a founder call" |

### Added

| Path | Purpose |
| --- | --- |
| `tests/conformance/test_instance_format_ssot.py` | the guard (D2) |

## Implementation sequence

### T1 — the guard, first

⚠️ **State the match pattern** (`NEW@pass3`, Pass 3 F6). It is the eight registry artifact names,
a hyphen, then **two digits or the literal `NN`**, an optional slug, then the extension:
`\b(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)-(NN|\d{2})([_A-Za-z0-9{}*-]*)\.(md|yaml)\b`.
A loose form such as `(BRD|…|IPLAN)-[^\s]*\.md` picks up ~14 non-instance hits under the spec
tree — `IPLAN-ECOSYSTEM.md`, `IPLAN-STANDARD.md`, `IPLAN-DEFINITIONS.md`, `IPLAN-ASSURANCE.md`,
`IPLAN-TDDREF-001-PLAN.md` — and V1 would read far from 2 with no way to tell whether the guard
or the measurement is wrong.

⚠️ **Scan root is `REPO_ROOT / "framework"`, not a `framework/**` glob** (`NEW@pass2`, Claim 27).
`platforms/claude-code-plugin/framework/` is a vendored mirror; a repo-root glob doubles every
figure (V1=4, V3=22) and — since T2 fixes only the spec copies while T6 re-vendors much later —
**V2 would be non-zero at the point the plan runs it**, breaking the T2 → V2 → T6 sequencing.

Write `tests/conformance/test_instance_format_ssot.py` **before** the fixes, and confirm it
**fails** on the two defects (Claims 6, 16) and **passes** the **9** index references. A guard written
after its fixes inherits their misconception.

**Mutation check:** remove the mention-level index exemption and confirm the test reports
**11** total (9 index false positives + the 2 real defects) — see V3. (`NEW@pass2`; the first
draft said "7 false positives", which is unsatisfiable and would read as the guard being wrong.)

### T2 — the two filename claims (Claim 6). T1 goes green.

`01_BRD/README.md:119` → `.yaml`. `04_BDD/BDD-TEMPLATE.yaml:148` → drop the extension
(*"the produced BDD document"*), **do not** substitute `.yaml` — Scope item 3 and Claim 19.

### T3 — single source (D1)

Registry header states the authority. **All five deferrers** cross-reference it: Principle 2 (C1),
§Template Policy (C2), `01_BRD/README.md:125` (C5), `ID_NAMING_STANDARDS.md:277` (C6) **and
`04_BDD/BDD-00_index.TEMPLATE.md:43-45` (C7)** (`NEW@pass3` — C7 was in D0 and the Modified table
but in no task, leaving open the guard-blind vector Pass 2 added it to close).

⚠️ **None of these restates the effective condition** (`NEW@pass3`, D6). They cross-reference
GD-17. Restating it in three normative surfaces re-creates the drift D1 exists to prevent.

⚠️ **Preserve Principle 2's carve-outs** (`NEW@pass1`, Claim 20). It exempts repository prose
(`README`, `CHANGELOG`, governance surfaces) *and* index templates. The registry header carries
only the **index** half; drop the prose half and every `framework/**` governance `.md` — including
the files the guard scans — reads as non-conformant.

⚠️ **Break the citation cycle** (`NEW@pass1`). `LAYER_REGISTRY.yaml:19` currently cites Principle 2
as *its* authority. Inverting the direction without removing that back-reference leaves the two
pointing at each other with the mandate stated in neither.

### T4 — `GD-17` (D1, Claim 5)

**Do NOT write a `doc_id`-only condition** (`NEW@pass3`; the first draft said "Name `doc_id`",
which Pass 2 F4 and Pass 3 F3 both showed is insufficient). Write the **outcome-based** condition
from D6. State the SemVer pair `0.43.0 → 0.44.0` explicitly —
GD-15 and GD-16 both omit theirs. Record the `GATE-SPEC-W003` security assessment in the
GD-05/GD-08 form (Claim 11).

### T5 — CHANGELOG `0.44.0` + #558 narration (D4)

### T6 — bump and fanout

⚠️ Order (`CLAUDE.md` § Durable traps — **not** Claim 12, which supports the bump gate only; `NEW@pass3`): `framework/VERSION` → `scripts/sync-version-refs.sh` → **then**
`tools/sync-plugin-framework.sh`.
⚠️ Do **not** hand-edit the framework token in `docs/PARITY.md` first (Claim 13) — it is both the
detector's source and a target, so editing it strands the fanout silently at exit 0.
The fanout mechanically rewrites `tests/conformance/platforms/test_plugin_release_metadata.py`
(Claim 14) and re-vendors the plugin bundle, so "no test changes" would be false.

### T7 — re-point `TEMPLATE-COMPLETENESS-001` (D3). The dated note names **only** `0.45.0` and `GD-18`.

### T8 — record the #558 decision in `plans/DECISIONS.md`; clear `plans/HANDOFF.md:18-34`.

### T9 — file the platform-surface follow-up issue (D5, Claim 22) — **done: #567**

## Verification

| # | Command | Expected | Task |
| --- | --- | --- | --- |
| V1 | new guard, run before T2 | **fails with exactly 2** — `01_BRD/README.md:119`, `04_BDD/BDD-TEMPLATE.yaml:148`. **Measured on the prototype**, not asserted | T1 |
| V2 | new guard, run after T2 | passes — **0** violations | T2 |
| V3 | guard with the **mention-level** index exemption removed | **11** violations — proves the exemption is mention-level, not file-level. **Measured** (`NEW@pass1`; the first draft asserted 7 and Pass 1 asserted 16 — both wrong) | T1 |
| V3b | guard with the `DECISIONS.md` exemption removed | **3** — the 2 above plus `DECISIONS.md:31`. **Measured** (`NEW@pass1`, Claim 21) | T1 |
| V4 | `python3 -m pytest tests/conformance -q` | green, incl. the new module | T1-T6 |
| V5 | `python3 -m pytest tests/acceptance/deterministic -q` | green — 64 passed / 56 subtests, unchanged | T1-T6 |
| V6 | `PYTHONPATH=tools python3 -m pytest tools/sdd_doc_lint/tests -q` | green — 6 passed, unchanged | T1-T6 |
| V7 | `python3 -m sdd_doc_lint examples/url-shortener/docs/` | unchanged from `main` | T3 |
| V8 | `cat framework/VERSION platforms/*/FRAMEWORK_SPEC_VERSION` | all three `0.44.0` | T6 |
| V9 | `git diff main -- CHANGELOG.md \| grep -c '^-[^-]'` | `0`. ⚠️ **not** `grep '^-'` — the diff header `--- a/CHANGELOG.md` matches that every run (measured) | T5 |
| V10 | `git diff -U0 main -- CHANGELOG.md \| grep '^@@'` | one hunk, all `+`, starting between `## [Unreleased]` and the current topmost `###` | T5 |
| V11 | `grep -c '0\.44\.0' plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | **`5`** (`NEW@pass1`; the first draft said `3`) — 3 historical (the claim-ledger row, and the two sentences inside the dated `Amendment — 2026-08-28` block — cited by name, since the re-point note shifted their line numbers) **plus** `:10` and `:120`, which D3 rewrites to `0.44.0 → 0.45.0` and which therefore still contain `0.44.0` | T7 |
| V12 | `grep -c 'GD-17' plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | `0` — the dated note names only `GD-18` | T7 |
| V13 | `grep -c '0\.43\.0' plans/TEMPLATE-COMPLETENESS-001-PLAN.md` | `2` — the two forward-looking `from` refs become `0.44.0 →`, leaving the historical pair | T7 |
| V14 | `pre-commit run --all-files` twice consecutively | clean both times | all |

V5-V7 must be **unchanged**, not merely green: no linter code changes here, so movement means
the edits touched behaviour they should not have.

## Docs to update

- [ ] `CHANGELOG.md` — `0.44.0` + #558 narration
- [ ] `framework/governance/DECISIONS.md` — GD-17
- [ ] `plans/DECISIONS.md` — the #558 founder decision
- [ ] `CLAUDE.md` — framework current-state token (does **not** self-heal; Claim 13)
- [ ] `plans/HANDOFF.md` — regenerate; clear the #558 "needs a founder call" section
- [ ] `ROADMAP.md` — shipped-work bullet (`NEW@pass3`)

### D6 — The effective condition is an outcome, written once (`NEW@pass3`)

**Enumerating components has failed three times.** Measured (Claim 28): with a `doc_id`
frontmatter present, a YAML BRD is admitted to the edge graph — and `scan_fr_elements` **still
returns 0**, so `COV01` stays vacuous. Pass 3 confirmed two more that no enumeration named:
`BDD-SCHEMA-001` and the EARS→BDD edges go silently vacuous (fence matcher), and `SEED01` is
silently skipped.

So GD-17 states a **testable outcome**, which cannot be under-enumerated:

> The instance-format mandate takes normative effect when, for every layer, a reference instance
> authored in the layer's `extensions` format (a) lints with **zero** findings, and (b) yields
> the **same element and coverage results** as the equivalent Markdown form — i.e. carrier
> parity, not merely absence of errors. Clause (b) is what catches a vacuous pass; clause (a)
> alone would be satisfied by a linter that sees nothing.

Operationally that is #564's completion **in full** — all four carrier-aware primitives — and it
is directly checkable by a carrier-parity test rather than by reading a checklist.

**The condition is written ONCE, in GD-17** (`NEW@pass3`, Pass 3 F5). C1, C2, C3, C5, C6 and C7
**cross-reference GD-17**; none restates it. The draft had it in four places against a rationale
demanding one.

### D5 — Spec-only scope, stated (`NEW@pass1`)

This plan governs `framework/**`. **Platform authoring surfaces are out of scope and still
instruct `.md`** — e.g. `platforms/claude-code-plugin/skills/doc-prd/SKILL.md:135-136` prescribes
`PRD-NN_{slug}.md` (Claim 22). GD-09 recorded exactly this caveat for its own guard
(`DECISIONS.md:546-548`: *"Its scope is the spec only … platform authoring surfaces … must add
their own lock"*). T6's `sync-plugin-framework.sh` run vendors the corrected framework docs into
a plugin that still says `.md`, so without this caveat the Objective over-reaches. **A follow-up
issue is filed in T9.**

## Risks

| Risk | Mitigation |
| --- | --- |
| Guard flags correct index docs | D2; V3 proves the exemption is live |
| Guard written after its fixes inherits their misconception | T1 orders it first; V1 requires a red run |
| Erratum reads as walking GD-15 back | GD-17 keeps the mandate with an effective condition |
| Rewriting published history | V9 + V10 |
| Falsifying TC-001's founder-decision record | D3; V11 pins the three historical mentions |
| Fanout stranded silently | T6 ⚠️ ordering + `docs/PARITY.md` trap |
| `GATE-SPEC-W003` fires (agent-facing governance change) | warning-only; record the assessment in GD-17 (Claim 11) |
| Governance-PR surface budget exceeded | the unsplittable-bump exemption (Claim 15). ⚠️ `plans/HANDOFF.md:104` says **"Not standing"** — it is per-bump, and requires a **per-bump founder OK** recorded in the commit message (`NEW@pass1`; the first draft called it "standing", which the cited line contradicts verbatim) |

<!-- markdownlint-disable MD050 -->
<!-- MD050 rewrites `__init__.py` to `**init**.py`, silently breaking citations and failing the
     gate with the misleading `path '.py' does not exist`. Workaround per issue #408. -->

## Claim ledger

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | GD-15 mandates the instance format and declines the frontmatter contract in one entry | `frontmatter contract` | framework/governance/DECISIONS.md:101 |
| 2 | Nine rules and the trace graph gate on a frontmatter `doc_id` that no template declares | `build_edge_graph` | tools/sdd_doc_lint/__init__.py:1762 |
| 3 | GD-09 ratified "single source, enforced by deletion" for this defect class | `Single source, enforced by deletion` | framework/governance/DECISIONS.md:520 |
| 4 | Principle 2 asserts the instance mandate unconditionally and is GD-15's named authority | `YAML is the mandatory format` | framework/governance/DOC_GOVERNANCE_CORE.md:6 |
| 5 | The frontmatter contract is owned by a `Draft` design that never names `doc_id` | `D1` | plans/OKF-CONFORMANCE-001-DESIGN.md:110 |
| 6 | `01_BRD/README.md:119` says `BRD-NN_*.md` six lines before `:125` says YAML | `BRD-NN_*.md` | framework/layers/01_BRD/README.md:119 |
| 7 | The registry sanctions `.md` index docs for layers 01-07 | `Index templates` | framework/registry/LAYER_REGISTRY.yaml:23 |
| 8 | `TEMPLATE-COMPLETENESS-001` mentions `0.44.0` on eleven lines, three historical | `founder` | plans/TEMPLATE-COMPLETENESS-001-PLAN.md:364 |
| 9 | That plan already claims the `GD-17` identifier | `GD-17` | plans/TEMPLATE-COMPLETENESS-001-PLAN.md:183 |
| 10 | An index-doc exemption already exists in code and is used by `STRUCT01` | `_is_index_doc` | tools/sdd_doc_lint/__init__.py:1438 |
| 11 | `GATE-SPEC-W003` fires on an agent-facing governance change with no security assessment | `GATE-SPEC-W003` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:105 |
| 12 | A framework `VERSION` bump is gated and requires the fanout | `GATE-SPEC-E005` | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:89 |
| 13 | `fw_prev` is detected from `docs/PARITY.md`, which is also a fanout target | `fw_prev` | scripts/sync-version-refs.sh:296 |
| 14 | The fanout rewrites a conformance test, so "no test changes" is false | `test_plugin_release_metadata` | scripts/sync-version-refs.sh:352 |
| 15 | A framework bump is unsplittable and needs a per-bump founder OK | `unsplittable` | plans/HANDOFF.md:101 |
| 16 | `04_BDD/BDD-TEMPLATE.yaml:148` names the produced instance `BDD-NN.md` | `BDD-NN.md` | framework/layers/04_BDD/BDD-TEMPLATE.yaml:148 |
| 17 | `framework/VERSION` currently reads `0.43.0` | `0.43.0` | framework/VERSION:1 |
| 18 | GD-09 rule 2 requires every mandating layer to state its contract **in-layer** (`NEW@pass1`) | `states its contract in-layer` | framework/governance/DECISIONS.md:526 |
| 19 | The BDD sentence describes a ```yaml **fence**, the sole in-force extraction path (`NEW@pass1`) | `_YAML_FENCE` | tools/sdd_doc_lint/__init__.py:1622 |
| 20 | Principle 2 carries a repository-prose carve-out the registry header does not (`NEW@pass1`) | `does not govern repository prose` | framework/governance/DOC_GOVERNANCE_CORE.md:6 |
| 21 | `DECISIONS.md:31` names `IPLAN-01.md` descriptively inside a ratified record (`NEW@pass1`) | `IPLAN-01.md` | framework/governance/DECISIONS.md:31 |
| 22 | A plugin authoring skill still prescribes `.md` PRDs (`NEW@pass1`) | `PRD-NN_{slug}.md` | platforms/claude-code-plugin/skills/doc-prd/SKILL.md:135 |
| 23 | GD-09 recorded a spec-only scope caveat for its own guard (`NEW@pass1`) | `platform authoring surfaces` | framework/governance/DECISIONS.md:547 |
| 24 | `ID_NAMING_STANDARDS.md:277` asserts `.yaml` normatively — it is a carrier, not an exclusion (`NEW@pass2`) | `{TYPE}-NN.yaml` | framework/governance/ID_NAMING_STANDARDS.md:277 |
| 25 | `BDD-00_index.TEMPLATE.md` §File Format states the value in prose, so the guard is blind to it (`NEW@pass2`) | `File Format` | framework/layers/04_BDD/BDD-00_index.TEMPLATE.md:43 |
| 26 | `STRUCT01` resolves sections from `##` headings and never reads frontmatter, so a `doc_id` contract cannot relieve it (`NEW@pass2`) | `_section_word_counts(body)` | tools/sdd_doc_lint/__init__.py:1480 |
| 27 | A vendored plugin mirror of the spec tree exists, so the guard's scan root must be the spec tree (`NEW@pass2`) | `SUBTREES` | tools/sync-plugin-framework.sh:24 |
| 28 | With a `doc_id` frontmatter present a YAML BRD enters the edge graph, yet `COV01` still discovers 0 FRs — so no component enumeration can be sufficient; **blocks T4**, whose condition D6 rewrites (`NEW@pass3`) | `scan_fr_elements` | PROBE: `PYTHONPATH=tools python3 -c "import sdd_doc_lint as L; L.scan_fr_elements(open(<yaml-brd>).read())"` → `0`, while `build_edge_graph` admits the doc |
| 29 | The #558 founder decision is recorded on the issue, not merely asserted; **blocks T5**, which writes it into published release history (`NEW@pass3`) | `#558` | PROBE: `gh issue view 558 --json comments --jq '.comments[-1].body'` → the 2026-08-28 option-3 decision |

**Expected gate warnings — do not "fix" them.** Rows 2, 13, 14 cite a precise line *inside* a
multi-occurrence symbol, so the gate resolves the symbol elsewhere and reports drift. The cited
lines are the accurate ones; `--fix` would replace them with less precise ones.

<!-- markdownlint-enable MD050 -->

## Review log

### Pass 1 — 2026-08-28 — independent

Nine load-bearing findings, all confirmed. **Unlike the abandoned plan's Passes 1 and 3, none
refutes the premise** — single source + effective condition + guard survives intact. Seven are
corrections, two improve the design. Folded; additions carry `NEW@pass1`.

**F4 (best finding) — GD-09 was cited for half its rule, and the omitted half forbids what T3
did.** GD-09 ratified three rules; rule 2 is *"Every mandating layer states its contract
in-layer"* (Claim 18). It deleted a re-specified **algorithm**, never the layer's own contract —
`01_BRD/README.md:146` is the shipped model, stating the shape *and* naming the single source
*and* saying "Do not re-specify it here." The draft's T3 removed `01_BRD/README.md:125`, the only
in-layer statement a BRD author reads. **Design corrected: state in-layer, cross-reference for
authority.**

**F7 (second-best) — and it produced a better repair than the finding proposed.** The BDD
sentence describes a ```yaml **fence**, and `_YAML_FENCE` is the sole in-force extraction path
(Claim 19). Substituting `.yaml` yields "a```yaml fence in the produced `BDD-NN.yaml`" —
incoherent, and asserting a form the gate rejects. But the deeper point is that the sentence is
**not a defect**: it accurately describes the *current* carrier, and under GD-17 the mandate is
not yet effective. First fold cut it to #564; second fold found the right repair — **remove the
extension claim** (*"the produced BDD document"*), which is accurate, safe, and invisible to the
guard.

**F1 + F9 — the guard's exemption unit was never stated, and V1/V2/V3 were unsatisfiable as
written.** The reviewer read it as file-level (reusing `_is_index_doc`, which tests the document
being linted) and correctly showed that yields 9 false positives in non-index files. The
prototype had implemented it **mention-level** all along. Folded: the unit is now stated, plus a
second exemption for `governance/DECISIONS.md` (Claim 21 — `:31` names `IPLAN-01.md`
descriptively inside a ratified record).

**All four V-row figures are now measured rather than asserted, and every previous figure was
wrong:** V1 = **2** (draft said 1), V3 = **11** (draft said 7; Pass 1 said 16), V3b = **3**.

**F5 — V11 should be `5`, not `3`.** `:10` and `:120` are rewritten to `0.44.0 → 0.45.0`, which
still contains `0.44.0`. Pass 3 of the abandoned plan found the same class of error; the *from*-
version correction was carried into the design and not into the count.

**F2 + F3 — the carrier count was a figure, not a list.** Folded as **D0**, an explicit table of
five with dispositions, plus two written-out exclusions (`ID_NAMING_STANDARDS.md:277`, added to
the deferral set since its generic `{TYPE}-NN` placeholder is invisible to the guard; and
`docs/AIDOC.md:105`, a Platform-B table covered by D5). The `_authored_form` exclusion, dropped
when the draft inherited the abandoned plan's list, is restored.

**F6 — deferring Principle 2 would drop its repository-prose carve-out**, which is what keeps
every `framework/**` governance `.md` from reading as non-conformant; the registry header carries
only the index half. Also folded: `LAYER_REGISTRY.yaml:19` cites Principle 2 as *its* authority,
so inverting without removing the back-reference leaves a citation cycle.

**F8 — no spec-only caveat.** Folded as **D5** + task T9, mirroring GD-09's own caveat
(Claim 23). A plugin skill still prescribes `.md` PRDs (Claim 22).

**F10 (minor, folded) — Claim 15 said "standing"; `HANDOFF.md:104` says "Not standing".**

**Clean, recorded:** V9's `'^-[^-]'` form; V10's hunk range; Claims 5, 7, 8, 9 exact; no
conformance test asserts on the prose of the edited surfaces.

**Result:** folded; dispatching Pass 2.

### Pass 2 — 2026-08-28 — independent

Six load-bearing findings, all confirmed, all folded (`NEW@pass2`). Pass 1 was 9, so the loop is
converging and no finding refutes the premise. **Notably, the reviewer independently re-derived
the guard figures and confirmed them** — V1=2, V2=0, V3=11, V3b=3. First time a count in this
effort has survived independent re-derivation.

**F4 (decisive) — the erratum's condition was insufficient, and would have auto-restored the
defect.** GD-17 named only a `doc_id` frontmatter contract. But the Objective cites **two**
independent failures, and only one is `doc_id`-caused: `STRUCT01` resolves sections through
`_section_word_counts`, which enumerates `##` headings and **never reads frontmatter**
(Claim 26). So a `doc_id` contract relieves the vacuous `COV01` pass and leaves **all 17
`STRUCT01` errors**. Had #564 shipped its frontmatter contract ahead of the carrier-aware
primitives, GD-17 would have flipped the mandate to effective and restored the exact state this
plan exists to relieve. **Condition now names #564's completion — both halves.**

**F3 — the carrier list was short by two, and one exclusion rationale was false.** `C6`
(`ID_NAMING_STANDARDS.md:277`) asserts `.yaml` **twice** normatively and its Example cell carries
a literal filename the guard *does* see — the draft excluded it on a rationale that was wrong in
both halves, while T3 was already editing it, so the table and the task set had not reconciled.
`C7` (`04_BDD/BDD-00_index.TEMPLATE.md:43-45` §File Format) is a **guard-blind** prose carrier: no
filename token, so it can drift to `.md` and V2 stays 0 forever — exactly the vector D1 exists to
close. A bounded scan (`grep -rnE '^#+ *(File Format|Document Formats)'`) returns **exactly
two** of this shape, so the list is **+2, not +7**. Carrier count is now **seven**, written out
with dispositions; the draft's "five … the other four defer" only balanced by miscounting the
ratified GD-15 record as a deferrer.

**F1 — the F7 fold half-landed.** The File-structure table still said `BDD-NN.md → BDD-NN.yaml`,
contradicting the folded Scope 3 and T2. Worst property: `.yaml` is registry-conformant, so **no
V-row would have caught it** — the one place the wrong repair is invisible to every check is
exactly where the stale instruction survived.

**F2 — `7` was the file-level figure.** A naive rule flags **9** index references, not 7; the 7
are those *inside* an index file. T1's mutation check ("expect 7 false positives") was therefore
unsatisfiable and would have read as the guard being broken. Corrected to 11 total. The Pass 1
log's own evidence sentence was wrong in the same direction and is corrected here.

**F5 — the `FMTX01` row was unowned and in the wrong catalog.** No design item, no task, no
verification, and `LINT_RULES.md` is the catalog of codes *a platform linter emits* — a
one-directional conformance test means it would not go red, so it would silently instruct a
second platform to emit a code nothing emits. That is the #565 enforcement this plan explicitly
defers. **Row dropped.**

**F6 — the guard's scan root was unstated.** `platforms/claude-code-plugin/framework/` is a
vendored mirror (Claim 27); a repo-root glob gives V1=4, V3=22, and since T2 fixes only the spec
copies while T6 re-vendors later, **V2 would be non-zero when the plan runs it**. Root is now
stated as `REPO_ROOT / "framework"`.

**Minors folded:** Claim 19's symbol was misnamed (`_extract_bdd_scenarios` → `_bdd_yaml_scenarios`,
`:1622`); `CLAUDE.md` and `ROADMAP.md` added to the Modified table.

**Confirmed sound:** the BDD repair reasoning; every `C`/`D`/`T`/`V` token resolves; ledger IDs
unique; D3/V11/V12/V13 re-derived exactly (V11=5, V12=0, V13=2); nineteen claims verified
semantically; no conformance test asserts on the prose of any edited surface.

**Result:** folded; dispatching Pass 3.

### Pass 3 — 2026-08-28 — independent (OPS-0066 cap)

Seven load-bearing findings, all confirmed, all folded (`NEW@pass3`). **Pass 1 = 9, Pass 2 = 6,
Pass 3 = 7.** Under the fold discipline that is not converging, so **no fourth pass was
dispatched** and the state is surfaced to the founder.

**But the composition changed, and that matters more than the count.** Three of the seven (F1,
F2, F4) are **this plan's own folds half-landing** — a correction that reached one surface and
not another — not design defects. One (F3) the author had already found by measurement while the
pass ran. And the finding that killed both prior designs came back **clean**:

> **Priority 2 — the carrier list: C1-C7 is complete. … No eighth carrier exists in
> `framework/**`. The count is correct at seven.**

The reviewer derived that independently with a shape-independent re-scan (not the plan's own
bounded `grep`), specifically noting that C6's heading is `## File Naming`, which the bounded
scan does *not* match — so the list survives a method the plan did not use. The guard figures
were also re-derived a third time and hold: V1=2, V2=0, V3=11, V3b=3.

**F3 (substantive) — the condition was still insufficient, one layer deeper.** Pass 2 corrected
`doc_id`-only to `doc_id` + carrier-aware STRUCT01. Still short: `scan_fr_elements` is a third
primitive, and `BDD-SCHEMA-001` + the EARS→BDD edges (fence matcher) and `SEED01` (silently
skipped) are a fourth and fifth. Author's own measurement agrees (Claim 28): with `doc_id`
present the doc **enters** the edge graph and `COV01` **still** discovers 0 FRs.
**Resolved by D6:** the condition is now an **outcome** — carrier parity, testable — not a
component list. Three enumerations were under-counted; an outcome cannot be.

**F1, F2, F4 — fold hygiene.** D1/D2 still said "five carriers"; T4 still said "Name `doc_id`",
the instruction that actually authors GD-17; T3 omitted C7, the guard-blind carrier Pass 2 added
precisely to close that vector. In every case the stale copy sat where no verification row reads
it — the same invisibility property Pass 2's F1 identified.

**Countermeasure added (author, `NEW@pass3`):** a mechanical self-consistency sweep over the plan
body for each superseded figure and instruction. Run after this fold it found **5** hits, of
which **2 were genuine misses** my targeted replacements had not matched (D1's "five surfaces",
D2's "5 carriers and 2 defects") and 3 were deliberate quotes inside correction notes. Both
genuine misses are repaired and the sweep is now clean. This class had half-landed on three
consecutive folds; grepping for the old string is what catches it.

**F5 — the condition lived in four places** against a rationale demanding one. D6 settles it:
written once in GD-17; C1/C2/C3/C5/C6/C7 cross-reference.

**F6 — the guard's match pattern was unstated.** A loose form picks up ~14 non-instance hits
(`IPLAN-ECOSYSTEM.md`, `IPLAN-STANDARD.md`, …). The regex is now written into T1.

**F7 — D4's founder decision had no ledger row.** T5 turns it into permanent CHANGELOG text and
T8 clears the handoff on its strength. Added as Claim 29 with a `PROBE`, matching the sibling
plan's treatment of the same class.

**Minors folded:** `ROADMAP.md` added to Docs-to-update; T6's ordering warning no longer miscites
Claim 12; Scope 3 now cites Claims 6 **and** 16.

**Result: NOT ready — cap reached. Escalated.** All seven are folded and the plan is
self-consistent, but **no review has seen the folded text**, and OPS-0066 forbids a fourth
dispatch. The open item is a founder decision: accept the plan as folded and proceed to
implementation, or authorise a fourth pass.
