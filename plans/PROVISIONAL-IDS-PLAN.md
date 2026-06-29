# PROVISIONAL-IDS-001 Plan — manual-mode provisional IDs + hash-algo parity

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| Task           | PROVISIONAL-IDS-001 (D54-F01, CONSUMER-FEEDBACK-001 PR-4)    |
| Type           | feature                                                      |
| Status         | IMPLEMENTED — 2026-06-29 (spec 0.31.0; 306 conformance+unit green; corpus baseline unchanged) |
| Depends on     | ELEMENT-COVERAGE-001 (#209, element-level COV01/COV02), REFGRAN01 (#194) — the independence caveat resolves against these |
| Feeds          | PROVISIONAL-IDS-002 (`rehash` follow-on); CONSUMER-FEEDBACK-001 PR-5 (reuse manifest) coexists on the `state` field |
| Version impact | framework MINOR (normative ID-standard change + template change) |

## Implementation notes (2026-06-29 — refinements discovered during impl)

Two design points the plan under-specified, resolved during implementation
(both validated by the new `tests/unit/test_provisional_ids.py`, 11 tests):

1. **`state` lives in produced-doc frontmatter as `id_state`, not
   `metadata.id_standard.state`.** Produced `.md` docs carry NO `id_standard`
   block (that's template-only scaffolding), so the keystone flag has no home
   there. Implemented as a frontmatter key `id_state: provisional|canonical`
   (default canonical) read by `_extract_frontmatter`; the linter emits a
   doc-level `PROV01` advisory on `provisional` (and flags an unknown value).
   Templates' `id_standard.state` documents the convention; the artifact-level
   flag is `id_state`.
2. **HASH01 catches duplicate IDs only in element-DEFINITION shapes** —
   `- **ID**`, `## ID`, YAML `id:` (`_ELEM_DEF_*`) — NOT the BRD FR-bullet
   `- **ID — title**`. So "duplicate `0000` → HASH01" (claim 6 / R3) holds for
   the definition shapes (which cover BDD scenario `id:`, headings, etc.) but
   NOT for BRD §7 FR-bullets (a pre-existing uniqueness-scope gap, not introduced
   here). The convention relies on author discipline + the documented
   ordinal-hex increment there; HASH01 backs the definition-shape layers.

## Objective

Give **manual authors** (working without the plugin's ID generator) a sanctioned
way to write element IDs the linter accepts, and publish the hash algorithm where
they look so they can canonicalize to plugin-identical hashes by hand. Today the
template placeholder `xxxx` is regex-invalid (fails `ELEM_FORM`, surfacing a
confusing **ID03 "malformed element id"** when copied), the placeholder lint
(`PH01`) silently misses bare lowercase `xxxx`, and the SHA-256 algorithm lives
only in template `_guidance` prose — not in `ID_NAMING_STANDARDS.md`. This
delivers: a doc-level `provisional|canonical` state flag, a regex-valid
provisional ID form, a lint fix for the lowercase blind spot, and the hash
algorithm promoted to normative spec. (Automated `rehash` is a separate
follow-on — see Out of scope.)

## Scope

**In:**

- **`metadata.id_standard.state: provisional | canonical`** (keystone) — a
  once-per-doc flag meaning "the element IDs here are placeholders; canonicalize
  before downstream consumption." Defaults to `canonical` when omitted
  (back-compatible). Added to every layer template's `id_standard` block +
  documented in `ID_NAMING_STANDARDS.md`. A `provisional` doc emits a single
  doc-level **advisory** ("provisional IDs — canonicalize before downstream
  consumption"), not a per-element error.
- **Regex-valid provisional ID form** — section-ordinal hex (`BRD.01.07.0001`,
  `.0002`, … distinct per element within a section). Templates ship the literal
  `0000` so a copied-but-unfilled single-element placeholder is `ELEM_FORM`-valid
  and FR-scanner-visible. Multi-element sections increment (`0001`, `0002`) —
  provisional docs still require **unique** IDs (HASH01 applies; duplicate `0000`
  is correctly flagged, forcing distinct ordinals).
- **Lint fix** — `PH01` flags **bare** lowercase `xxxx`/`xxx+` via
  `(?<!\.)\bx{3,}\b` (the uppercase-only `\bXX+\b` blind spot). The look-behind
  leaves a full-element-id hash segment (`BRD.01.07.xxxx`, always `.`-preceded)
  to ID03, avoiding a double-report (Pass-2 F4). This is the only
  structurally-unambiguous placeholder signal (see "why not detect canonical
  leaks by shape" below).
- **Normative hash algorithm** — lift the SHA-256 spec from
  `EARS-TEMPLATE.yaml:94` into `ID_NAMING_STANDARDS.md`: pin the exact input
  string `"{doc_id}:{section_id}:{title}:{description}"`, the `[:4]` truncation,
  and the 4→8 collision rule, plus a "hand-authored hashes are placeholders
  until canonicalized" statement.

**Out of scope (deferred):**

- **`rehash` subcommand → PROVISIONAL-IDS-002 (fast-follow).** Reference-aware
  auto-canonicalization (recompute hashes, rewrite declarations + downstream
  citations, flip `state`) is the largest/most complex piece — it needs to parse
  each element's title/description to reconstruct the hash input, and rewrite
  citations corpus-wide. The TODO's F-03 fold note states the no-tooling need is
  met by "the published hash algorithm + this placeholder convention + a trivial
  plugin install" — i.e. the *normative algorithm* (in scope here) is the
  parity anchor; `rehash` is convenience automation that builds on it. Splitting
  keeps this plan minimal and lets `rehash` land with its own
  determinism/reference-awareness review.
- The plugin's own ID generator (unchanged).
- F-03 "offline readiness score" (the score stays the LLM `-audit` skill).
- PR-5 reuse manifest — separate plan; this plan only avoids colliding with it on
  the `state` field.
- Retroactive canonicalization of the example corpus — regenerated wholesale
  (see [[project-examples-regenerated-wholesale]]).

## Approach / Design

### The three concrete defects (grounded)

1. **Template placeholder is regex-invalid.** `ELEM_FORM =
   ^([A-Z]+)\.\d+\.\d+\.[a-f0-9]+$` rejects `xxxx` (`x` ∉ `[a-f0-9]`), so a
   copied `BRD.01.07.xxxx` trips **ID03** ("malformed element id", since
   `tok.count(".") >= 3 and not elem_re.match(tok)`) — a confusing message for an
   unfilled placeholder. Ship `0000` instead: `ELEM_FORM`-valid and
   FR-scanner-visible (`_FR_BULLET` requires `[a-f0-9]+`).
2. **`PH01` lowercase blind spot.** `_PLACEHOLDERS` has `\bXX+\b` (uppercase
   only); a bare lowercase `xxxx` (in a `hash:`/`placeholder:` field, not in full
   `TYPE.NN.SS.xxxx` element position where ID03 catches it) passes silently. Add
   a lowercase placeholder pattern.
3. **Algorithm not where authors look.** `ID_NAMING_STANDARDS.md` states only
   "4-character hex content hash (SHA256, first 4 chars)"; the input string +
   collision rule live only in `EARS-TEMPLATE.yaml:94`. Promote to normative.

### The `state` keystone + provisional form + uniqueness (F1)

`state` defaults to `canonical` (omitted ⇒ canonical; back-compatible). The
provisional ID form is **section-ordinal hex** (`0001`, `0002`, … distinct per
element), which is `ELEM_FORM`-valid so provisional docs lint cleanly *as
documents*. **Provisional docs still require unique IDs** — `_check_id_uniqueness`
(HASH01) applies unchanged, so the template's bare `0000` repeated across two
elements in one section is correctly flagged, forcing the author to assign
distinct ordinals. (`state` governs ID *stability*, not uniqueness.)

### Why not detect "canonical leaks" by hash shape (F2)

An ordinal like `0001` is a valid hex hash — indistinguishable by shape from a
real content hash that happens to be `0001`. So the lint **cannot** reliably flag
"a `000N` under `state: canonical`" as a non-canonicalized leak. The only
structurally-unambiguous placeholder is non-hex `xxxx` (flagged by the new
`PH01` pattern under any state). Verifying that a `canonical` doc's hashes are
*actually* the content hashes requires recomputation — that is `rehash --check`,
which lands with the deferred `rehash` (PROVISIONAL-IDS-002). This plan's
canonical-correctness signal is therefore the `state` flag (authoritative,
author-asserted) plus the unambiguous `xxxx` catch — not a shape heuristic.

### Independence caveat resolution (vs ELEMENT-COVERAGE-001 + REFGRAN01)

The orchestration plan requires resolving how provisional IDs interact with the
(now element-level) coverage gate and REFGRAN01:

- **Coverage (COV01/COV02):** a provisional element is a real requirement and is
  **counted normally** — no coverage carve-out for `provisional` (avoids a hole
  where draft docs escape the gate). Because the ordinal-hex form is
  `ELEM_FORM`-valid and `_FR_BULLET`-matchable, provisional FRs/elements are
  scanned and gated exactly like canonical ones.
- **REFGRAN01:** an element-level provisional citation (`@brd: BRD.01.07.0001`)
  is element-form (3 dots, hex) ⇒ REFGRAN01 does NOT fire (it flags only doc-form
  `@brd: BRD-01`). The provisional form is already accepted; no REFGRAN change.
- **The deferred risk:** a downstream citation to a provisional ID breaks when
  that ID is later canonicalized to a different hash. The `provisional` advisory
  warns authors to canonicalize before downstream consumption; the reference-aware
  rewrite that makes canonicalization safe is the deferred `rehash`'s job. Until
  then, the documented guidance is: canonicalize a doc (by hand via the normative
  algorithm, or the plugin) *before* downstream layers cite its elements.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `framework/governance/ID_NAMING_STANDARDS.md` | promote the normative SHA-256 algorithm (input string + `[:4]` + 4→8 collision); add `state: provisional\|canonical` + the ordinal-hex provisional form + "hand-authored hashes are placeholders until canonicalized" |
| `framework/layers/*/[A-Z]*-TEMPLATE.yaml` (8 layer templates) | add `id_standard.state: canonical`; replace the `xxxx` placeholder literal with `0000` |
| `tools/sdd_doc_lint/__init__.py` | add a lowercase-`xxxx` pattern to `_PLACEHOLDERS` (PH01); read `id_standard.state` and emit the doc-level `provisional` advisory |
| `platforms/{claude-code-plugin,hermes}/sdd_doc_lint/__init__.py` | re-vendored byte-identical |
| `tests/unit/test_provisional_ids.py` (new) | PH01 lowercase catch; `0000` is `ELEM_FORM`-valid + FR-scanned; duplicate `0000` → HASH01; `provisional` advisory; provisional element still COV-counted |
| `tests/conformance/` | `state` field recognized in templates; normative-algorithm-present guard on `ID_NAMING_STANDARDS.md` |
| `framework/VERSION` + FSV pins + fanout | MINOR bump via `bump_version.py` |
| `CHANGELOG.md`, `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md`, `plans/DECISIONS.md` | docs of record |

## Implementation sequence

### Task 1: normative hash algorithm in the standard

- Promote the algorithm from `EARS-TEMPLATE.yaml:94` into
  `ID_NAMING_STANDARDS.md` (normative): the exact input string, `[:4]`
  truncation, 4→8 collision rule, + the placeholders-until-canonical statement.
- **Test-first — [CODE]:** a conformance guard asserts `ID_NAMING_STANDARDS.md`
  carries the input-string spec + collision rule (not just "4-char hex").

### Task 2: `state` flag + provisional form + template literal

- Add `id_standard.state: canonical` to the 8 layer templates. Replace `xxxx`
  with `0000` **in the two copied-into-the-authored-doc positions** (Pass-2
  minor): (1) the `id_standard.placeholder` field value, and (2) the
  content-skeleton element-id slots an author fills (e.g. the FR-bullet /
  scenario-id hash segment). Illustrative `_guidance`-prose `@tag` examples are
  not linted (templates aren't linted as documents) and may stay as illustration
  — the per-template decision is surfaced during impl. (Note: the swap fixes the
  *hash* segment; an instantiated element id is `ELEM_FORM`-valid only once the
  author also fills the `NN`/`SS` doc/section ordinals, which is the normal
  authoring step.)
- Document `state` + the ordinal-hex provisional form in
  `ID_NAMING_STANDARDS.md`. Read `state` in `sdd_doc_lint`; emit a doc-level
  `provisional` advisory.
- **Test-first — [CODE]:** a `provisional` doc with distinct `000N` IDs lints
  clean + carries the advisory; a `0000` repeated in one section → HASH01;
  a provisional FR is COV01/COV02-counted (independence caveat, V5).

### Task 3: `PH01` lowercase fix

- Add the lowercase placeholder pattern **`(?<!\.)\bx{3,}\b`** to `_PLACEHOLDERS`.
  The negative look-behind is load-bearing (Pass-2 F4): a bare `\bx{3,}\b` would
  also match the `xxxx` hash segment of a full `BRD.01.07.xxxx` (word boundary at
  the `.`→`x` transition) and, since the ID03 and PH01 scans share one per-line
  loop, double-report with ID03. `(?<!\.)` means the run is matched only when NOT
  immediately preceded by a `.` — so a bare `xxxx`/`hash: xxxx` (space/quote/`:`/
  line-start preceded) is caught, while a full-element-id hash segment (always
  `.`-preceded; its only word-boundary start is right after the `.`) is left to
  ID03. (Verify empirically — see V3.)
- **Test-first — [CODE]:** bare lowercase `xxxx` flagged by PH01; a valid hex
  hash (`a7f3`) and an ordinal (`0001`) are not; a full `BRD.01.07.xxxx` yields
  **ID03 only** (no PH01 double-report).

### Task 4: MINOR bump + re-vendor + docs of record

- `bump_version.py <MINOR>`; re-vendor byte-identical; update the release-metadata
  hard-pin; CHANGELOG / HANDOFF / FRAMEWORK-TODO (D54-F01 → in-progress, `rehash`
  split to PROVISIONAL-IDS-002) / DECISIONS (provisional≠coverage-exempt;
  leaks-not-shape-detected; rehash-split).

## Verification

| #  | Check (command) | Expected | Maps to |
| -- | --------------- | -------- | ------- |
| V1 | `pytest tests/unit/test_provisional_ids.py -q` | PH01 lowercase, `0000` validity, HASH01-on-dup, advisory cases green | Tasks 2-3 |
| V2 | `pytest tests/conformance tests/unit -q` | all green | regression |
| V3 | `(?<!\.)\bx{3,}\b`: bare `xxxx` → PH01; `a7f3`/`0001` → no PH01; full `BRD.01.07.xxxx` → ID03 only (PH01 does NOT also fire) | per case | Task 3 / F4 |
| V4 | a `provisional` doc with `000N` IDs is COV01/COV02-visible (counted, not exempt) | counted | independence caveat |
| V5 | REFGRAN01 silent on `@brd: BRD.01.07.0001` (element-form) | no REFGRAN01 | independence caveat |
| V6 | `0000` matches `ELEM_FORM` + `_FR_BULLET`; `xxxx` matches neither | as stated | Task 2 |
| V7 | byte-identity canonical ↔ both vendored copies; FSV pins match | identical / match | D-0022 / bump |

## Docs to update

- [ ] `CHANGELOG.md`, `plans/HANDOFF.md`, `plans/FRAMEWORK-TODO.md` (D54-F01 → in-progress; log PROVISIONAL-IDS-002 for `rehash`)
- [ ] `plans/DECISIONS.md` (D-number: provisional≠coverage-exempt; canonical-leaks-not-shape-detected; rehash split)
- [ ] `ID_NAMING_STANDARDS.md` (normative algorithm + `state` + provisional form)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | the lowercase pattern false-positives on prose ("xxx") OR double-reports with ID03 on a full `TYPE.NN.SS.xxxx` (Pass-2 F4) | med | `(?<!\.)\bx{3,}\b` (3+, not `.`-preceded) — leaves element-id hash segments to ID03; corpus has zero bare `x{3,}` runs (reviewer-confirmed); V3 asserts ordinal/hex not flagged AND no ID03 double-report |
| R2 | `state: provisional` is read as a coverage exemption (a hole) | low | explicit decision (D-number) + V4 asserts provisional elements ARE counted |
| R3 | template `0000` repeated across multi-element sections trips HASH01 and confuses authors | med | document the ordinal-hex increment (`0001`,`0002`) as the convention; HASH01-on-dup is intended (forces distinctness); test in V1 |
| R4 | the normative algorithm in the standard drifts from `EARS-TEMPLATE.yaml`/the plugin generator | med | Task-1 conformance guard ties the standard's spec to the template; the byte-identity demonstration lands with `rehash` (PROVISIONAL-IDS-002) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | strict element form rejects non-hex hash (`xxxx`) — hash segment is `[a-f0-9]+` (NOT `{4,8}` as the TODO states) | `ELEM_FORM` | tools/sdd_doc_lint/trace_graph.py:37 |
| 2  | placeholder lint is uppercase-only (`\bXX+\b`) — misses bare lowercase `xxxx` | `_PLACEHOLDERS` | `tools/sdd_doc_lint/__init__.py:73` |
| 3  | ID03 fires on a ≥3-dot element id that fails the strict form (so `BRD.01.07.xxxx` is flagged, not silent) | `ID03` | `tools/sdd_doc_lint/__init__.py:526` |
| 4  | PH01 is the placeholder-leak finding emitted from the `_PLACEHOLDERS` scan | `PH01` | `tools/sdd_doc_lint/__init__.py:533` |
| 5  | the FR-bullet scanner requires a `[a-f0-9]+` hash — so `0000`/`000N` FRs scan but `xxxx` FRs do not | `_FR_BULLET` | `tools/sdd_doc_lint/__init__.py:670` |
| 6  | provisional docs still require unique element IDs — HASH01 flags duplicate ids regardless of `state` | `_check_id_uniqueness` | `tools/sdd_doc_lint/__init__.py:826` |
| 7  | the SHA-256 algorithm (input string + `[:4]` + 4→8 collision) is published only in template `_guidance`, not the standard | `Hash algorithm (SHA256` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:94 |
| 8  | `ID_NAMING_STANDARDS.md` states only "4-character hex content hash (SHA256, first 4 chars)" — no input string/collision rule | `4-character hex content hash` | framework/governance/ID_NAMING_STANDARDS.md:60 |
| 9  | REFGRAN01 fires only on doc-form trace tags to element-declaring layers (an element-form provisional citation is accepted) | `_REFGRAN_ELEMENT_DECLARING` | `tools/sdd_doc_lint/__init__.py:1716` |
| 10 | element-level COV01/COV02 count any declared element (provisional elements are not exempt) | `_check_backward_coverage` | `tools/sdd_doc_lint/__init__.py:1644` |
| 11 | templates carry an `id_standard` block (format/hash_algorithm/placeholder) — where `state` is added | `id_standard` | framework/layers/03_EARS/EARS-TEMPLATE.yaml:88 |
| 12 | the orchestration plan scopes PR-4 + names the independence caveat to resolve | `Independence caveat` | plans/CONSUMER-FEEDBACK-001-PLAN.md:167 |
| 13 | the triaged issue + fix shape (a)-(d), incl. the F-03 fold note that the no-tooling need is met by algo+convention+plugin | `D54-F01-PROVISIONAL-IDS` | plans/FRAMEWORK-TODO.md:268 |

## Review log

### Pass 1 — 2026-06-29T00:00:00Z — self-review

- **F1 — HASH01/uniqueness interaction.** The `0000` template literal repeated
  across multiple elements in a section trips HASH01. Folded: documented the
  ordinal-hex increment as the convention, stated provisional docs still require
  unique IDs (HASH01 applies), added claim 6 + R3 + a V1 case.
- **F2 — canonical leaks aren't shape-detectable.** An ordinal `0001` is a valid
  hex hash, indistinguishable from a real content hash; the original "flag `000N`
  under canonical" check was unsound. Folded: only non-hex `xxxx` is flagged
  (PH01); canonical-correctness verification deferred to `rehash --check`; the
  `state` flag is the authoritative signal. Added the "why not detect by shape"
  subsection.
- **F3 — scope: split `rehash` to a follow-on (PROVISIONAL-IDS-002).** `rehash`
  is the largest/most complex piece (per-element title/description parsing +
  corpus-wide citation rewrite), and the TODO's F-03 fold note says the
  no-tooling need is met by the *normative algorithm* + convention + plugin —
  so `rehash` is separable convenience automation. Folded: moved out of scope,
  removed Task 4/test_rehash/V-rehash/rehash-risks; the normative algorithm
  (Task 1) still ships as the parity anchor. Slimmed to minimal-and-realistic.

### Pass 2 — 2026-06-29T00:00:00Z — independent (fresh-context)

Independent reviewer verified all 13 citations (open + correct), ran the regexes
empirically (confirmed `0000`/`0001` match `ELEM_FORM`+`_FR_BULLET`, `xxxx`
matches neither, `\bXX+\b` misses lowercase, ID03 flags `BRD.01.07.xxxx`),
confirmed the independence-caveat resolution (provisional COV-counted via
`element_host`; REFGRAN01 `continue`s unless `_DOC_FORM` matches — element-form
never does), the HASH01-on-duplicate-`0000` claim, the scope split (no broken
state — the normative algorithm gives a complete by-hand canonicalization path),
and no dangling `rehash` refs from the slimming. One load-bearing finding, folded:

- **F4 (load-bearing) — PH01 pattern double-reports with ID03.** `\bx{3,}\b`
  matches the `xxxx` segment of `BRD.01.07.xxxx` (word boundary at `.`→`x`), and
  the ID03 + PH01 scans share one per-line loop, so a full element id would emit
  BOTH — contradicting Task-3/V3's no-double-report. Folded: pattern changed to
  `(?<!\.)\bx{3,}\b` (matches only bare runs not `.`-preceded; element-id hash
  segments, always `.`-preceded, are left to ID03). Updated Scope lint-fix bullet,
  Task 3, R1, V3 to specify the look-behind + the explicit "ID03 only" assertion.
- *(minor, folded)* clarified Task 2's `xxxx`→`0000` scope (the `placeholder`
  field + content-skeleton element-id slots; `_guidance` examples not linted) and
  the "ELEM_FORM-valid once NN/SS also filled" wording precision.

### Pass 3 — 2026-06-29T00:00:00Z — independent (fresh-context, confirming)

Confirmed the F4 fix empirically: `(?<!\.)\bx{3,}\b` returns `[]` inside
`BRD.01.07.xxxx` (no ID03 double-report) and matches every bare-context
placeholder claimed (line-start / space / comma / slash / dash / quote / colon
preceded), including the `.xxxxx` subtlety — the only `\b` in a contiguous x-run
is the `.`→`x` transition, which `(?<!\.)` rejects, so there is no alternate
start position to leak through. The fold is internally consistent across all
four sites (Scope lint-fix bullet, Task 3, V3, R1) with no stale unqualified
pattern; the Task-2 minor clarification and the Pass-2 log match the diff; no
dangling refs.

**No new load-bearing findings.**

**Result:** ready
