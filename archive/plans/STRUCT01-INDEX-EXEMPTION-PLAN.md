# STRUCT01-INDEX-EXEMPTION Plan — recognize index/registry docs in the linter so they lint clean

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | STRUCT01-INDEX-EXEMPTION                     |
| Type           | bugfix                                       |
| Status         | PLANNED — 2026-06-30T09:21:11-04:00         |
| Depends on     | none |
| Feeds          | ENG-BRD-SKETCH-ROADMAP (unblocks "BRD-00 index as roadmap home") |
| Version impact | **none** — pure `sdd_doc_lint` tooling fix (`tools/` + `tests/` + re-vendored copies); no `framework/**` change, so no spec bump (GATE-SPEC not triggered) |

## Objective

`sdd_doc_lint` is supposed to exempt index/registry docs (`<TYPE>-00_index`) from
the instance-doc structural checks — STRUCT01 (required sections) and the
trace-resolution skip both look for a **top-level** `artifact_type` ending in
`-INDEX`. But every layer index **template** declares `artifact_type` only under
`custom_fields` (and 6 of 7 `.md` ones use a bare value), and the IPLAN registry
is a `.yaml` with no `---` frontmatter at all — so the exemption **never fires**.
A consumer who copies an index template into `docs/` and lints it gets STRUCT01
errors (BRD-00 alone: 17). Separately, the `-INDEX` token the exemption keys on is
itself flagged by the ID02 doc-id scan as a "malformed document id". Fix both in
the linter so every index/registry doc lints clean, with **no template changes**.

## Scope

**In:**

- `tools/sdd_doc_lint/__init__.py`:
  1. a `_is_index_doc(rel, fm)` helper that recognizes an index doc by the
     `<TYPE>-00_index` **filename** (reliable even for the `.yaml` registry whose
     body doesn't parse as `---` frontmatter), OR a top-level `artifact_type`
     ending in `-INDEX` (back-compat);
  2. use it in the STRUCT01 exemption (`_check_required_template_sections`) and the
     trace-resolution INDEX skip — replacing the two `artifact_type…endswith("-INDEX")`
     reads;
  3. the ID02 doc-id scan skips `<X>-INDEX` tokens (they are index artifact-type
     markers, not malformed doc-ids — consistent with the `-INDEX` convention the
     other two checks already honor).
- Re-vendor the byte-identical copies (`bash tools/sdd_doc_lint/sync-vendored.sh`).
- A regression test: lint each of the **8** real index templates → zero STRUCT01
  and zero `-INDEX`-token ID02 (the guard the existing synthetic-fixture unit test
  failed to provide).
- CHANGELOG `[Unreleased]` tooling entry + D-0043; close the new TODO entry; HANDOFF.

**Out of scope (deferred):**

- No version bump (no `framework/**` change). The index **templates** are left
  byte-unchanged — the fix is entirely in the linter that reads them.
- Touching `custom_fields.artifact_type` / `document_type` placement — left as-is;
  the filename signal makes them unnecessary for detection.
- The placeholder findings index templates emit (PH01 `YYYY-MM-DD`, other ID02 from
  `BRD-NN`/`PRD-XX` example rows, TAG01) — those are normal template placeholders a
  consumer replaces; not structural blockers. The fix targets STRUCT01 + the
  `-INDEX` ID02 false-positive only.

## Approach / Design (D-0043)

### Root cause (two independent linter gaps)

1. **Exemption never fires.** STRUCT01 (`__init__.py:1079`) and the trace skip
   (`:1453`) read `fm.get("artifact_type")` (top-level) and test `endswith("-INDEX")`.
   But the 7 `.md` index templates nest `artifact_type` under `custom_fields` (6 with
   a bare value), and IPLAN-00 is a `.yaml` whose body isn't `---`-delimited so
   `_extract_frontmatter` returns `None`. None of the 8 is recognized.
2. **ID02 self-flag.** The doc-id scan (`:552-555`) flags any `_DOC_ID` token that
   isn't `TYPE-<digits>`; `BRD-INDEX` matches the token shape but not the doc form,
   so the very `-INDEX` marker the exemption needs is reported "malformed".

### Fix — detect by filename; stop self-flagging `-INDEX`

`_is_index_doc(rel, fm)` keys primarily on the **filename** (`<TYPE>-00_index`),
the one signal present and reliable on all 8 templates (and on a consumer's copied
files) regardless of frontmatter shape or file type. Back-compat: a top-level
`artifact_type` ending in `-INDEX` still counts (so the existing
`test_struct01_skipped_for_brd_index` unit test — which uses both that field and a
`BRD-00_index.md` filename — keeps passing). The ID02 scan gains
`and not tok.upper().endswith("-INDEX")`, matching the `-INDEX` convention the
other checks already special-case.

### Empirically validated (prototype, reverted)

Applied to the real linter + re-vendored: all **8** index templates →
**STRUCT01 = 0** and **0** `-INDEX`-token ID02 (as-is counts were BRD 17 / PRD 15 /
EARS 6 / BDD 4 / ADR 12 / SPEC 8 / TDD 7 / IPLAN 2). The STRUCT01 counts are the
widespread half; the **`-INDEX` ID02 self-flag is a single finding on BRD-00 only**
(the lone template whose `artifact_type` value is the token-form `BRD-INDEX`; the
other 6 `.md` templates use bare values and IPLAN has no frontmatter) — the ID02
edit still belongs in the fix so a *consumer's* index (or a future `-INDEX`-valued
one) doesn't self-flag. Full conformance + unit suites pass after re-vendoring (the
only failures pre-re-vendor are the 3 vendoring/sync-idempotency guards — expected,
resolved by `sync-vendored.sh`). The
example-corpus lint is **byte-unchanged** (16 COV02 / 5 REFGRAN01 / 6 STY02 / 1
TH-RES-001 — no STRUCT01/ID02 delta), because the corpus has no `<TYPE>-00_index`
under a layer with section targets (`09_CHG/CHG-00_index.md` exists but CHG has no
template targets, so STRUCT01 already returns early there).

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `tools/sdd_doc_lint/__init__.py` | add `_is_index_doc` + `_INDEX_FILENAME`; use in STRUCT01 (`:1078`) + trace skip (`:1453`); ID02 skips `-INDEX` tokens (`:554`) |
| `platforms/claude-code-plugin/sdd_doc_lint/__init__.py`, `platforms/hermes/sdd_doc_lint/__init__.py` | re-vendored byte-identical (`sync-vendored.sh`) |
| `CHANGELOG.md` | `[Unreleased]` tooling entry (no spec version change) |
| `plans/DECISIONS.md` | D-0043 |
| `plans/FRAMEWORK-TODO.md` | add + close `STRUCT01-INDEX-EXEMPTION-NESTED` (now incl. the IPLAN-00 `.yaml` case + the ID02 self-flag) |
| `plans/HANDOFF.md` | banner |

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/test_index_template_lint.py` | lint each of the 8 real `<TYPE>-00_index.TEMPLATE.*` → assert zero STRUCT01 + zero `-INDEX` ID02 |

## Implementation sequence

### Task 1: regression test first — [CODE]

- Write the conformance test (imports `sdd_doc_lint` via the established
  `sys.path.insert(0, REPO_ROOT/"tools")` pattern). Confirm it **fails** on `main`
  (STRUCT01 present on the templates) before the fix.

### Task 2: linter fix + re-vendor

- Add `_is_index_doc` + the three call-site edits; `bash tools/sdd_doc_lint/sync-vendored.sh`.
- New test → green; full conformance + unit → green.

### Task 3: docs

- CHANGELOG tooling entry; D-0043; TODO close; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | new test on `main` (pre-fix) | **fails** (STRUCT01 on the templates) — proves it catches the bug | test validity |
| V2 | `python -m pytest tests/conformance tests/unit -q` (post-fix + re-vendor) | green incl. new test, vendoring guard, sync-idempotency | scope |
| V3 | lint all 8 `<TYPE>-00_index.TEMPLATE.*` | zero STRUCT01 + zero `-INDEX` ID02 | fix |
| V4 | `python -m sdd_doc_lint examples/url-shortener/docs/` | unchanged vs baseline (16 COV02 / 5 REFGRAN01 / 6 STY02 / 1 TH-RES-001) | no regression |
| V5 | `diff tools/sdd_doc_lint/__init__.py platforms/*/sdd_doc_lint/__init__.py` | identical (re-vendored) | vendoring |
| V6 | existing `test_sdd_doc_lint_struct01.py` | still green (back-compat path) | no regression |

## Docs to update

- [ ] `CHANGELOG.md` — `[Unreleased]` tooling entry (no spec bump)
- [ ] `plans/DECISIONS.md` — D-0043
- [ ] `plans/FRAMEWORK-TODO.md` — `STRUCT01-INDEX-EXEMPTION-NESTED` (add + close)
- [ ] `plans/HANDOFF.md` — banner
- [ ] `ROADMAP.md` — n/a

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Filename detector over-matches a non-index doc | low | pattern `[A-Z]+-00_index` is the specific registry convention; it is NOT restricted to the 8 `_KNOWN` layer types (also matches `CHG-00_index`, any future `<UPPER>-00_index`) — harmless because a non-`_KNOWN` type never enters the linted corpus (`detect_layer` → None), and only an index would ever carry the `-00_index` name; V4 confirms corpus delta = 0. Revisit only if a future layer ships a `-00` *instance* doc. |
| R2 | ID02 `-INDEX` skip hides a real malformed id elsewhere | low | only suppresses tokens ending exactly in `-INDEX` (an index marker, never a valid `TYPE-<digits>` doc-id); element-id scan unaffected |
| R3 | Vendored copies drift | med | V5 + the vendoring byte-identity guard + sync-idempotency test; explicit `sync-vendored.sh` step |
| R4 | A test runs `sync-vendored.sh` as a side-effect and dirties the tree | known | observed during prototyping; commit the re-vendored copies so the guard sees identity |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | STRUCT01 exemption reads top-level `artifact_type` + `endswith("-INDEX")` | `_check_required_template_sections` | tools/sdd_doc_lint/**init**.py:1058 |
| 2  | …the exemption test line | `endswith` | tools/sdd_doc_lint/**init**.py:1080 |
| 3  | trace-resolution INDEX skip uses the same top-level `-INDEX` test | `-INDEX` | tools/sdd_doc_lint/**init**.py:1453 |
| 4  | ID02 doc-id scan flags any `_DOC_ID` token failing `doc_re` (so `BRD-INDEX` self-flags) | `malformed document id` | tools/sdd_doc_lint/**init**.py:555 |
| 5  | STRUCT01 receives `rel` (so a filename detector is feasible) | `rel: str` | tools/sdd_doc_lint/**init**.py:1059 |
| 6  | The 7 `.md` index templates nest `artifact_type` under `custom_fields` | `artifact_type` | framework/layers/01_BRD/BRD-00_index.TEMPLATE.md:9 |
| 7  | IPLAN-00 is a `.yaml` registry with no `---` frontmatter (filename is the only reliable signal) | `iplan-registry` | framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml:13 |
| 8  | `lint_path` lints `.md`, `.yaml`, `.yml` (so consumer indexes are lint targets) | `.yaml` | tools/sdd_doc_lint/**init**.py:1976 |
| 9  | The existing STRUCT01 unit test uses BOTH `artifact_type: BRD-INDEX` and filename `BRD-00_index.md` (back-compat holds) | `BRD-00_index.md` | tests/unit/test_sdd_doc_lint_struct01.py:80 |
| 10 | `sync-vendored.sh` is the re-vendor mechanism for the linter copies | `Re-sync the vendored` | tools/sdd_doc_lint/sync-vendored.sh:2 |
| 11 | Conformance tests may import `sdd_doc_lint` via `sys.path.insert(0, tools)` | `sys.path.insert` | tests/conformance/test_coverage_engine.py:19 |
| 12 | Most recent decision is D-0042 → next free is D-0043 | `D-0042` | plans/DECISIONS.md:13 |

## Review log

### Pass 1 — 2026-06-30T09:03:41-04:00 — self-review (original docs-only approach)

- Drafted a docs-only fix (add top-level `artifact_type: <X>-INDEX` to the 7 `.md`
  templates) + a regression test; empirically zeroed STRUCT01; deferred IPLAN-00.

### Pass 2 — 2026-06-30T09:10:00-04:00 — independent (fresh-context)

- Independent reviewer confirmed the docs-only fix zeroed STRUCT01 on all 7 **but
  found a [LOAD-BEARING] regression**: adding top-level `artifact_type: <X>-INDEX`
  makes the ID02 doc-id scan flag the value itself ("malformed document id
  'PRD-INDEX'") on all 7 — the literal fix line becomes a permanent finding, and the
  "no linter code change needed" premise was false. Minor: "corpus has no layer
  index" imprecise (CHG-00 exists but has no section targets); Claim-2 line off by 1.
- **Pivot:** abandoned the docs-only approach. Redesigned as a **pure linter fix** —
  detect index docs by filename (`_is_index_doc`), and stop ID02 self-flagging
  `-INDEX` tokens. This needs **no template change** (so no new ID02), fixes all
  **8** index docs including the IPLAN-00 `.yaml` (filename works where frontmatter
  doesn't), and requires no spec bump. Re-validated empirically: all 8 → 0 STRUCT01
  / 0 `-INDEX` ID02; full suite green post-re-vendor; corpus byte-unchanged.

### Pass 3 — 2026-06-30T09:35:00-04:00 — independent (fresh-context, on the revised linter design)

A fresh `code-reviewer` re-verified all 12 ledger citations, then **implemented the
full fix itself**, ran `sync-vendored.sh`, and confirmed: all 8 templates → 0
STRUCT01 / 0 `-INDEX` ID02 (pre-fix counts matched the plan exactly);
`pytest tests/conformance tests/unit` → **314 passed, 847 subtests**; corpus
**byte-identical** to clean `main` (28 findings, same breakdown). Regression hunt:
filename regex matches only genuine indexes; the `-INDEX` ID02 skip suppresses
nothing live (the only such tokens are in un-linted `logs/*.log`); trace membership
unchanged; no other yaml-path check consumes `_is_index_doc`. "No version bump"
confirmed correct + consistent with precedent (#198/#200 — pure `feat(tools)`
re-vendor PRs, no platform bump). Test design sound; V1 holds. **Verdict: 0
load-bearing findings.** Two MINOR clarifications folded: (M1) the `-INDEX` ID02
self-flag is BRD-00-only today (clause added to Approach); (M2) the filename regex
isn't `_KNOWN`-restricted (note added to R1).

**Result:** ready
