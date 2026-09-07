# ENG-BRD-SKETCH-ROADMAP Plan — project-init roadmap in the BRD-00 index + the "sketch" sub-form

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | ENG-BRD-SKETCH-ROADMAP                       |
| Type           | documentation                               |
| Status         | PLANNED — 2026-06-30T08:43:53-04:00         |
| Depends on     | **STRUCT01-INDEX-EXEMPTION (D-0043, merged #224)** — the BRD-00 index is now free of STRUCT01 errors, so it is a viable roadmap home; Engramory #1 |
| Feeds          | wholesale corpus regen; a future Sketch-file MINOR (deferred) |
| Version impact | framework spec **PATCH** (`0.32.4 → 0.32.5`); plugin/Hermes product versions unchanged |

## Objective

Authoring only `BRD-01` in full plus index one-liners leaves whole-project scope
under-specified before cycle 1 (Engramory #1). There is a "Planned BRDs" table in
the BRD-00 index and `@depends:` chaining exists, but no documented project-init
step that enumerates the MVP cycles, and no scope-only "sketch" form. This change
makes the BRD-00 index "Planned BRDs" table the **roadmap home** (extended with
cycle / target-PROD / `@depends:` / status columns) and documents the
project-initiation enumeration step + the **trace-inert "sketch"** concept (a
planned row, not yet in the trace graph). **Docs-only; standalone Sketch-*file*
lint support is explicitly deferred** (it would need a linter behavior change — see
Approach).

## Scope

**In:**

- `framework/layers/01_BRD/BRD-00_index.TEMPLATE.md` — extend the "Planned BRDs"
  table columns to carry cycle, target PROD, `@depends:`, and a status
  (`Planned | Sketch`).
- `framework/layers/01_BRD/README.md` — add a "Project initiation: enumerate the
  roadmap" subsection under the existing Lifecycle section; define **Sketch** as a
  trace-inert planned row.
- `framework/layers/01_BRD/BRD-TEMPLATE.yaml` — a one-line `_guidance` note on the
  `status:` field cross-referencing the Sketch concept (planned-row status; the
  standalone Sketch-file form is deferred).
- Framework-spec PATCH bump (`0.32.4 → 0.32.5`) + CHANGELOG + D-0044; close the
  TODO entry; HANDOFF banner.

**Out of scope (deferred — one-liners, not designed here):**

- **A standalone scope-only `status: Sketch` BRD *file*.** An instance BRD (not an
  index) with only `document_control`/`introduction`/`project_scope` still fails
  **STRUCT01** (required-section check) — STRUCT01-INDEX-EXEMPTION exempts only
  `<TYPE>-00_index` docs, not instance BRDs. Making the standalone Sketch form
  lint-pass needs a STRUCT01 under-authoring exemption AND the `SKETCH-001`
  over-authoring guard (author (d) — "only if over-authoring drift shows up").
  Deferred to a future MINOR; until then a sketch lives as a Planned-BRDs **row**.
  Logged in `FRAMEWORK-TODO.md`.
- `BL-STATUS-SCOPE` per-context `status` enum (separate P3 item) — `Sketch` is a
  planned-row status here, not added to the BRD-TEMPLATE document `status` enum, so
  the two do not collide.
- A top-level `ROADMAP.md` product-strategy file in consumer projects — the author
  chose the BRD-00 index home to avoid colliding with that (the location is
  *recommended*, not mandated).
- **Pre-existing BRD-00 index template ID02/PH01 findings** — independent of this
  plan, the template emits ID02 on a `PRD-Ready` column header and a `BRD-TEMPLATE`
  quick-link (both match the `<TYPE>-<word>` `_DOC_ID` shape) plus a `TBD` PH01
  placeholder. The roadmap rows introduce none of these; STRUCT01 (the only
  differentiator vs. a standalone Sketch instance file) is clean. The `_DOC_ID`
  header/filename false-positive class is a separate linter concern, logged in
  `FRAMEWORK-TODO.md` — not fixed here.

## Approach / Design (D-0044)

### Why the index table, not a standalone Sketch file

The author's resolution "collapses back toward the `BRD-00_index` home (the
original 'stub the rest' practice)." The BRD-00 **index is now free of STRUCT01
errors** — STRUCT01-INDEX-EXEMPTION (D-0043, merged #224) made `_is_index_doc`
recognize `<TYPE>-00_index` docs by filename, so the index roadmap home is a solid
foundation (this plan's earlier blocker; see Review log Pass 2 → resolved). (The
template still emits a few **pre-existing, orthogonal** ID02/PH01 findings — a
`PRD-Ready` column header and a `BRD-TEMPLATE` quick-link match the `_DOC_ID`
shape, plus a `TBD` placeholder — that this plan does not touch; see Out of scope.)
A standalone
scope-only Sketch *file* (e.g. `BRD-05_future.md` — an **instance** BRD, not an
index) remains non-viable docs-only: **STRUCT01** still enforces the full
required-section set on a regular BRD (`_check_required_template_sections`), and the
index detector does not (and must not) exempt instance BRDs. So the roadmap lives in
the BRD-00 index, and the standalone Sketch-file form (with a STRUCT01
under-authoring exemption + the `SKETCH-001` over-authoring guard) is deferred. The
change is docs-only and trap-free — no `status` value is introduced that the linter
would then reject.

### 1. Extend the "Planned BRDs" table

Current columns: `ID | Title | Priority | Target Date | Notes`. New:

```
| ID | Title | Cycle | Priority | Target PROD | @depends | Status | Notes |
```

- **Cycle** — the MVP iteration this BRD set belongs to (e.g. `MVP-1`).
- **Target PROD** — the production milestone the cycle targets (replaces the vaguer
  "Target Date"; a roadmap is PROD-anchored).
- **@depends** — sequencing (`@depends: BRD-01`), the existing chain mechanism.
- **Status** — `Planned | Sketch` for future rows (`Sketch` = scope hypothesis
  captured; `Planned` = enumerated, not yet sketched). Active BRDs continue to use
  the Document Registry table above with their document `status`.

### 2. Document the project-initiation step + Sketch concept

Add to `01_BRD/README.md` under "Lifecycle: MVP → PROD → NEW MVP" a subsection:

- At project init, enumerate **all** planned MVP cycles as **Planned BRDs** rows
  (cycle + target PROD + `@depends:`), author only the current cycle's BRD set in
  full, and leave the rest as planned/sketch rows. Recommend (do NOT mandate) the
  BRD-layer location.
- **A Sketch is trace-inert:** a Planned-BRDs row carries only its document-level
  `BRD-NN` id + `@depends:` for sequencing — **no element IDs, not in the `@`-tag
  graph, invisible to forward coverage (`COV01`/ENG-FWD-COVERAGE)** because forward
  coverage only scans authored BRD FR elements (`scan_fr_elements` reads a doc's
  `## … Functional Requirements` section, which a planned row has none of).
  Crucially, **`@depends:` is not a trace tag** — the trace-graph `TAG` regex only
  matches the eight `KNOWN_LAYERS` (`@brd…@iplan`), so an active BRD's `@depends:
  BRD-05` pointing at a not-yet-authored planned row **never triggers
  `TRACE-RES-001`**. On **graduation** to a full BRD, it gains element IDs and
  enters the graph.

### 3. Cross-reference from the template

A sentence in `BRD-TEMPLATE.yaml`'s existing `document_control._guidance` block
(not a new `_note` on the flat `status:` scalar — a sibling `_note` there would be
ambiguous, same reasoning as item-2's score fields): a scope-only future-cycle BRD
is captured as a **Sketch row** in the BRD-00 index "Planned BRDs" table (not a
standalone file yet — that form is deferred). No change to the document `status`
enum (`Draft | In Review | Approved`).

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/layers/01_BRD/BRD-00_index.TEMPLATE.md` | extend "Planned BRDs" table columns (cycle/PROD/@depends/status) + an explanatory line |
| `framework/layers/01_BRD/README.md` | new "Project initiation: enumerate the roadmap" subsection + Sketch (trace-inert) definition |
| `framework/layers/01_BRD/BRD-TEMPLATE.yaml` | one sentence in the existing `document_control._guidance` block cross-referencing Sketch (no new key on the `status:` scalar) |
| `framework/VERSION` | `0.32.4 → 0.32.5` (via `bump_version.py 0.32.5` — re-vendors bundle + fans refs) |
| `CHANGELOG.md` | `[Unreleased]` entry (GATE-SPEC-E008) |
| `plans/DECISIONS.md` | D-0044 |
| `plans/FRAMEWORK-TODO.md` | `ENG-BRD-SKETCH-ROADMAP` → Closed; add the deferred standalone-Sketch-file follow-on |
| `plans/HANDOFF.md` | banner update |

## Implementation sequence

### Task 1: docs

- Extend the BRD-00 index "Planned BRDs" table; add the README subsection +
  Sketch definition; add the BRD-TEMPLATE `_guidance` note.

### Task 2: framework-spec PATCH bump

- `python tools/bump_version.py 0.32.5` (re-vendors bundle, fans refs); CHANGELOG
  `[Unreleased]` entry.

### Task 3: docs of record

- D-0044; close the TODO entry (+ log the deferred standalone-Sketch-file
  follow-on); HANDOFF banner.

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python -m pytest tests/conformance -q` | green (template-parse + version + spec-hygiene checks unaffected) | scope |
| V2 | `python tests/chg/spec_gate.py --base main` | pass — VERSION + CHANGELOG present | GATE-SPEC |
| V3 | `python -m sdd_doc_lint examples/url-shortener/docs/` | unchanged vs baseline (16 COV02 / 5 REFGRAN01 / 6 STY02 / 1 TH-RES-001; corpus byte-untouched) | no corpus regression |
| V4 | render/inspect the extended "Planned BRDs" table | valid GFM table; new columns present; `Sketch`/`Planned` documented | scope item 1 |
| V5 | `grep -n "Sketch" framework/layers/01_BRD/{README.md,BRD-TEMPLATE.yaml,BRD-00_index.TEMPLATE.md}` | Sketch documented as trace-inert planned row in all three | scope items 2–3 |
| V6 | bundle drift guard (`test_plugin_framework_bundle.py`) | green — re-vendored byte-identical | re-vendor |

## Docs to update

- [ ] `CHANGELOG.md` — `[Unreleased]` `### … 0.32.4 → 0.32.5` entry
- [ ] `plans/DECISIONS.md` — D-0044
- [ ] `plans/FRAMEWORK-TODO.md` — close `ENG-BRD-SKETCH-ROADMAP`; log deferred standalone-Sketch-file follow-on
- [ ] `plans/HANDOFF.md` — banner
- [ ] `ROADMAP.md` — not applicable

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Adding `status: Sketch` somewhere the linter then rejects a doc | low | by design `Sketch` is a Planned-table-**row** status in the BRD-00 index (STRUCT01-exempt per D-0043; AS8 never validates a table cell); the document `status` enum is untouched; no standalone Sketch file is introduced |
| R2 | The widened 8-column table reads awkwardly / GFM-malformed | low | `framework/` is markdownlint-ignored and `MD013` is off, so no automated gate — keep the header concise and visually verify the GFM table renders (V4) |
| R3 | "Recommended not mandated" location read as a hard rule | low | explicit wording ("recommend … do not mandate"); mirrors author intent |
| R4 | Bump straggler / drift | med | V2 + V6; `bump_version.py` auto-re-vendors (proven in BL-READY-SCORE-ADVISORY) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | BRD-00 index has a "Planned BRDs" table (`ID \| Title \| Priority \| Target Date \| Notes`) | `Planned BRDs` | framework/layers/01_BRD/BRD-00_index.TEMPLATE.md:58 |
| 2  | The BRD document `status` enum is `Draft \| In Review \| Approved` (left unchanged) | `status` | framework/layers/01_BRD/BRD-TEMPLATE.yaml:180 |
| 3  | STRUCT01 now exempts `<TYPE>-00_index` docs via `_is_index_doc` (filename-based, D-0043) — the BRD-00 index is free of STRUCT01 — but still enforces required sections on a regular (instance) BRD, so a standalone Sketch *file* would fail | `_is_index_doc` | `tools/sdd_doc_lint/__init__.py:1061` |
| 4  | Forward coverage scans a doc's `## … Functional Requirements` section for FR elements — a planned index row has none, so it is trace-inert | `scan_fr_elements` | `tools/sdd_doc_lint/__init__.py:744` |
| 5  | `01_BRD/README.md` has a "Lifecycle: MVP → PROD → NEW MVP" section (the home for the new subsection) | `Lifecycle:` | framework/layers/01_BRD/README.md:34 |
| 6  | BRD set / cycle wording already reconciled (BL-BRD-SET-WORDING) — the new subsection extends it, no contradiction | `BRD *set*` | framework/layers/01_BRD/README.md:36 |
| 7  | GATE-SPEC requires `framework/VERSION` (E005) + `CHANGELOG.md` (E008) on any `framework/**` change | `evaluate` | tests/chg/spec_gate.py:79 |
| 8  | Current framework spec version is `0.32.4` (→ `0.32.5` PATCH) | `0.32.4` | framework/VERSION:1 |
| 9  | Most recent decision is D-0043 → next free is D-0044 | `D-0043` | plans/DECISIONS.md:13 |
| 10 | `@depends:` chaining is the existing cross-BRD sequencing mechanism (cited in README lifecycle) | `@depends:` | framework/layers/01_BRD/README.md:50 |
| 11 | `@depends:` is NOT a trace tag — the trace-graph `TAG` regex matches only the 8 `KNOWN_LAYERS` (`@brd…@iplan`), so a planned BRD-NN referenced via `@depends:` never triggers TRACE-RES-001 | `TAG` | tools/sdd_doc_lint/trace_graph.py:32 |

## Review log

### Pass 1 — 2026-06-30T08:43:53-04:00 — self-review

- **F1 (trace-inert proof hardened).** Verified `@depends:` is not a trace tag —
  the trace-graph `TAG` regex (`trace_graph.py:32`) matches only the 8
  `KNOWN_LAYERS`, so an active BRD's `@depends: BRD-05` at a not-yet-authored
  planned row never trips TRACE-RES-001. Added to §2 + Claim 11; this closes the
  one real failure mode of referencing planned rows.
- **F2 (guidance placement).** The Sketch cross-reference goes in
  `BRD-TEMPLATE.yaml`'s existing `document_control._guidance` block, NOT a new
  `_note` on the flat `status:` scalar (a sibling `_note` in the flat map would be
  ambiguous — same lesson as item-2's score fields). Updated §3 + File-structure.
- **F3 (column rename).** "Target Date" → "Target PROD": a roadmap is PROD-anchored;
  the new column subsumes the old. Noted in §1.
- Citation gate: all 11 ledger rows resolve (`check_plan.py` — only the expected
  pending-final-pass failure remains).

### Pass 2 — 2026-06-30T09:05:00-04:00 — independent (fresh-context)

Dispatched a fresh-context `code-reviewer` against the real source. It verified
all 11 ledger citations literally true (incl. the `@depends:`-not-a-trace-tag
proof empirically — `grep depends tools/sdd_doc_lint/` → zero matches) **and
surfaced one load-bearing finding that breaks the plan's central premise:**

- **F-LB1 (premise false).** STRUCT01's `*-INDEX` exemption reads **top-level**
  `artifact_type` (`__init__.py:1080` `fm.get("artifact_type")`), but every index
  template nests `artifact_type` under `custom_fields:` (`BRD-00_index.TEMPLATE.md:9`),
  and the values are inconsistent (only BRD-00 = `BRD-INDEX`; PRD-00…TDD-00 = bare
  `PRD`/`EARS`/…). So the exemption **never fires** for a template-faithful consumer
  index → linting BRD-00 + PRD-00 templates directly yields **32 STRUCT01 errors**.
  The plan ships green only because nothing it touches is linted (no example-corpus
  index exists; `framework/` templates aren't lint targets). The "trap-free because
  `*-INDEX`-exempt" rationale (Approach §"Why the index table…"), R1's mitigation,
  and V3's parenthetical all rest on an exemption that does not work for real
  consumer docs. **This is a pre-existing framework bug, orthogonal to the roadmap
  docs, affecting all 8 index templates** — captured as a new TODO item
  `STRUCT01-INDEX-EXEMPTION-NESTED`.
- **F-min2 / F-min3 (minor).** R2/V1 markdownlint mitigation is unsound
  (`.markdownlintignore:13` excludes `framework/`; `MD013:false`; `pytest` doesn't
  invoke markdownlint), and V3's "corpus BRD-00 index is `*-INDEX`-exempt"
  parenthetical references a corpus index that does not exist. Both harmless to the
  result; to be reworded.

**Result (Pass 2):** NOT READY — the index-as-roadmap-home premise depended on a
broken exemption. Per founder direction, the prerequisite bug was fixed first.

### Pass 3 — 2026-06-30T09:50:00-04:00 — re-scope onto the fixed foundation

- **Pass-2 blocker RESOLVED.** STRUCT01-INDEX-EXEMPTION (D-0043) shipped (plan #223
  - impl #224): `_is_index_doc` now recognizes `<TYPE>-00_index` docs by filename,
  so the BRD-00 index lints clean (verified 0 STRUCT01 on `main`). The "trap-free"
  premise is now *true*, not assumed. Revised: Approach §"Why the index table"
  (cites the fix, not the false `*-INDEX`-exempt claim); Out-of-scope (a standalone
  Sketch *instance* file still fails STRUCT01 — correctly NOT exempted by the index
  detector); R1; V3 (concrete baseline, the non-existent-corpus-index parenthetical
  removed); Claim 3 (→ `_is_index_doc`); decision renumbered D-0043 → **D-0044**
  (D-0043 is now the bugfix); Depends-on records the prerequisite.
- **F-min2 (markdownlint) folded:** the widened "Planned BRDs" table is in
  `framework/` which markdownlint ignores and `MD013` is off — R2/V1 reworded
  accordingly (no markdownlint dependency claimed).
- Re-scope is otherwise unchanged: docs-only, framework PATCH 0.32.4 → 0.32.5.

### Pass 4 — 2026-06-30T10:05:00-04:00 — independent (fresh-context, on the re-scoped plan)

Fresh `code-reviewer` confirmed the Pass-2 blocker is genuinely resolved (BRD-00
index → 0 STRUCT01 on `main`; `_is_index_doc` at `:1061` used in the exemption),
all 11 ledger rows literally true, the status-enum has no validation trap (AS8
checks only frontmatter↔DC `status`, never a table cell), and the planned-row
pattern introduces zero new ID02/TAG/coverage findings. **2 load-bearing findings,
both folded:**

- **F-LB1 — "lints clean" overstated.** The index is **0 STRUCT01** (all the design
  needs), but the template still emits pre-existing, orthogonal ID02 (`PRD-Ready`
  header, `BRD-TEMPLATE` quick-link) + PH01 (`TBD`) findings. Reworded all four
  "lints clean" assertions → "free of STRUCT01"; added an Out-of-scope note (the
  `_DOC_ID` header/filename false-positive is a separate linter concern, logged in
  the TODO).
- **F-LB2 — D-0043 collision.** Two instructions (Scope "In"; File-structure table)
  still said D-0043 (the merged bugfix's number); an implementer would have logged a
  colliding decision. Both fixed to **D-0044**.

**Result:** ready
