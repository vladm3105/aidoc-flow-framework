# GD15-CARRIER-CENSUS — what a `.yaml` instance actually looks like, and which primitives see it

| Field | Value |
| --- | --- |
| Task | GD15-CARRIER-CENSUS |
| Type | **measurement artifact — not a design, and not an implementation plan** |
| Status | MEASURED — 2026-08-28 |
| Feeds | #564. Prerequisite for any third design attempt. |
| Version impact | **none** — `plans/` only |

## Why this file exists, and why it is not a plan

**Three designs for #564 have now been refuted, all for the same reason.**
`GD15-CARRIER-LINT-001` died at the OPS-0066 fold cap after two — both because
the instance-format mandate was diffuse and no surface census existed (that gap
was closed by #566, for *spec surfaces*). A third, `GD15-CARRIER-002`, was
drafted and refuted in a single independent pass. Its seam table had **four rows
and all four were wrong**, and its central design step would have **turned the
acceptance suite red**.

The pattern is now unambiguous: *the designs keep failing on facts, not on
judgement*. So this file records the facts and proposes nothing. It is the same
move #566 made for the surface count, one layer down.

**Do not turn this file into a plan.** A plan cites it.

## What refuted the third design — recorded so it is not repeated

Each was measured, not argued.

1. **`_extract_frontmatter` does NOT return `None` on a `.yaml` instance.** Six
   fixtures return a **dict with a real `doc_id`** today. The design's seam table
   asserted `None`, generalising from one file the author wrote for the purpose.
2. **`yaml.safe_load(text)` — the design's proposed replacement — raises on those
   same six**, because they are genuine two-document streams. Under the design's
   own contract that returns `None`, so `doc_id` is *lost*, `build_edge_graph`
   drops the document, and **7 pinned `REFGRAN01` warnings stop firing**. The
   acceptance match is a bidirectional multiset, so that is a hard failure. The
   design would have broken the suite it claimed not to touch.
   ⚠️ `CLAUDE.md` § "Acceptance harness" already records this: *"Walk them with
   `safe_load_all`, not `safe_load`."* It was written down and still walked into.
3. **`_section_word_counts` does NOT return `[]`** — 15 of the 24 `.yaml`
   fixtures carry 5–8 `##` lines, which are YAML comments that read as headings.
4. **`scan_fr_elements` is not consumed by `ACC01`.** Its real consumers are
   `COV01` (`tools/sdd_doc_lint/__init__.py:2071`), **`COV03`** (`:2150`) and `tools/sdd_coverage.py:78`.
5. **`rehash --check` cannot see a `.yaml` file at all** (`tools/sdd_doc_lint/rehash.py:53` globs
   `*.md`), and it uses `scan_fr_content`, not `scan_fr_elements`. The design's
   stated coupling between seam 3 and element-ID hashing is impossible.
6. **It cited `plans/DECISIONS.md` D-0080, which does not exist on `main`** — it
   is in an unmerged PR. Same class as the GD-13 "shipped as…" error caught
   earlier in the same session: a citation that is true only on another branch.

## Census 1 — a `.yaml` instance has THREE shapes in this repo, not one

All 24 `.yaml` files under `tests/acceptance/fixtures/`, measured:

| Shape | `---` fences | `safe_load` | `_extract_frontmatter` | `##` lines | Count |
| --- | --- | --- | --- | --- | --- |
| **A — plain** | 0 | ok | `None` | 0 | **9** |
| **B — document-start only** | 1 | ok | **`None`** (unterminated) | 5–8 | **9** |
| **C — two-document stream** | 2 | **raises `ComposerError`** | **dict, with `doc_id`** | 6–8 | **6** |

Shape **C** is the one any design must not break: it is the only shape currently
visible to the trace graph, and every pinned `REFGRAN01` on a `.yaml` file comes
from it.

Shape **B** is the recorded "invisible to `build_edge_graph`" population. Its
files carry `##` lines *and* no `doc_id`, so they are simultaneously
heading-bearing and graph-invisible.

**No shape matches a naive "the whole file is one YAML mapping" model**, which is
the model all three refuted designs assumed.

## Census 2 — carrier-sensitive primitives and their real consumers

Counts are occurrences in `tools/sdd_doc_lint/__init__.py`, then in the two
sibling tools. **`tools/sdd_coverage.py` is outside the package's main module and
is missed by every `tools/sdd_doc_lint/__init__.py`-scoped grep** — it imports `_extract_frontmatter`
(`:38`, called `:68`) and `scan_fr_elements` (`:41`, called `:78`), and it is
**not vendored to either platform mirror**, so `tools/sdd_doc_lint/sync-vendored.sh` does not
surface it either. Its own docstring (`:32-34`) states the invariant a
carrier-blind copy would break: *"the matrix and the linter's forward-coverage
gate read the SAME graph + classifier, so they never disagree."*

| Primitive | `tools/sdd_doc_lint/__init__.py` | sibling tools | Rules that depend on it |
| --- | --- | --- | --- |
| `_extract_frontmatter` | 18 (incl. 1 def → **17 call sites**) | `tools/sdd_coverage.py:68` | doc identity → the whole trace graph, `COV01/02`, `CSC01`, `SEED01`, `STALE01`, `REUSE01/02`, `ACC01` |
| `_split_frontmatter` | 5 | — | **`FM01` calls it DIRECTLY** (`:439`) and returns early with no fence — so `FM01` is a seam that threading `_extract_frontmatter` does **not** reach |
| `_section_word_counts` | 4 (**2 call sites**: `:583` STY02, `:1480` STRUCT01) | — | `STRUCT01`, and `STY02` — changing it at the function level changes size budgets too |
| `scan_fr_elements` | 4 (**2 call sites**) | `tools/sdd_coverage.py:78` | `COV01` (`:2071`), **`COV03`** (`:2150`) |
| `scan_fr_content` | 2 | — | `rehash_check` (`:1143`) — a *separate* Markdown-only scanner |
| `_YAML_FENCE` | 4 (**3 call sites**) | — | `:1622` `_bdd_yaml_scenarios`, `:1651` `_seed_disposition_rows`, `:2548` ledger strip |

**Six primitives, not four.** `FM01` and `scan_fr_content` are seams no refuted
design named.

## Census 3 — what GD-17 already requires, which no design has produced

`framework/governance/DECISIONS.md` (GD-17, ratified) states that the effective
condition is evaluated by a **per-layer carrier-parity assertion in the
conformance or acceptance tier**, and that its state is carried by a **successor
GD entry** — *"no surface may infer it from an issue being closed."*

Neither artifact exists, and no refuted design proposed either. Any third attempt
owes both, and its version-impact must include
`framework/governance/DECISIONS.md`.

## Open normative questions — decisions, not measurements

Recorded because a design that treats them as implementation detail will be
refuted a fourth time.

1. **There is no normative hash input for a structured FR entry.**
   `framework/governance/ID_NAMING_STANDARDS.md` defines title/description extraction byte-exactly
   over a **Markdown bullet** and scopes Phase 1 to that form. Element IDs on a
   YAML-authored BRD have no defined derivation. This is a
   `framework/governance/` change with GATE-SPEC weight, not a code change.
2. **`covered_state_of` reads `band` and `realized_by`; the structured
   `requirements[]` shape has neither.** `framework/layers/01_BRD/BRD-TEMPLATE.yaml` gives it `priority:`
   and no `realized_by` key, and prescribes the escape hatch only inside the
   *Markdown* band parenthetical. So on a YAML BRD every FR would classify
   `AUTHORED` and `COV01` becomes unconditionally blocking, with no way to
   declare a legitimately ADR-realized requirement.
3. **`COV01` has no acceptance signal at all** — filed as **#577**. Any design
   using the manifests as its "the `.md` path did not drift" check has no such
   check for forward coverage.

## What is NOT broken

- **The linter is correct on Markdown.** Every finding here is about a carrier it
  was never asked to read.
- **The example corpus is conformant** and yields real FR elements; it is the
  fixtures that do not (#577).
- **#566's spec-surface census stands** and is not superseded by this file. This
  one counts *code* seams; that one counted *spec* surfaces.
- **GD-17 is sound.** Its effective condition is precisely what stops the
  mandate from binding while these seams are open.

*Origin:* independent review of the refuted `GD15-CARRIER-002` draft, 2026-08-28.
Every row above was measured against `main` at `2c69a402`, not inherited.
