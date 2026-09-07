# LINT-DOCID-HEADER-FALSE-POSITIVE Plan — narrow the ID02 doc-id scan to digit-leading tokens (stop flagging `PRD-Ready` / `BRD-TEMPLATE` prose)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | LINT-DOCID-HEADER-FALSE-POSITIVE            |
| Type           | fix (linter bugfix)                         |
| Status         | READY — 2026-07-06 (Pass 2 independent; Pass 3 self) |
| Depends on     | none                                        |
| Feeds          | consumers' filled-in index docs stop carrying spurious ID02 errors |
| Version impact | **NONE** — a pure `sdd_doc_lint` bugfix in `tools/` (vendored to both mirrors). No `framework/` change → no GATE-SPEC, no version bump. Follows the [[D-0043]] STRUCT01-INDEX-EXEMPTION precedent (linter bugfix, no bump). Auto-mergeable. |

## Objective

The ID02 malformed-doc-id scan (`_DOC_ID` = `\b(TYPE)-([A-Za-z0-9]+)\b`) flags **any**
`<KNOWN-TYPE>-<token>` that is not `TYPE-<digits>` (or, post-D-0043, ends in `-INDEX`). So
legitimate prose tokens trip it: on `framework/layers/01_BRD/BRD-00_index.TEMPLATE.md` the
scan reports **`PRD-Ready`** (a readiness-gate name in a table header), **`BRD-TEMPLATE`** (a
quick-link, ×2), and **`BRD-NN`** (a template placeholder) as malformed document ids — four
false-positive ID02 errors. Templates aren't CI-linted, but a **consumer's filled-in index**
that keeps a `PRD-Ready` column or a `BRD-TEMPLATE` link carries the same standing errors.

**Root cause:** a real document id is `TYPE-<digits>` (`BRD-01`); a `TYPE-<letter-leading>`
token is a **compound word / marker** (`Ready`, `TEMPLATE`, `NN`, `INDEX`, `Final`), never a
doc-id attempt. The scan doesn't distinguish the two.

## Scope

**In:**

- **Narrow the ID02 check** (`tools/sdd_doc_lint/__init__.py`): flag a `_DOC_ID` match as
  malformed **only when its second segment is digit-leading** (`m.group(2)[0].isdigit()`) and
  fails the valid doc form (`doc_re`). A letter-leading token is prose, skipped. This
  **generalizes** D-0043's special-cased `-INDEX` exemption to *any* non-id-like token (so the
  explicit `-INDEX` clause is subsumed and removed).
- **Propagate** to the vendored mirrors via `tools/sdd_doc_lint/sync-vendored.sh`
  (drift-guarded).
- **Tests:** a canonical unit test (`tools/sdd_doc_lint/tests/`) asserting the four
  false-positive tokens (`PRD-Ready`, `BRD-TEMPLATE`, `BRD-NN`, `SPEC-Final`) draw **no**
  ID02, while digit-leading malformed ids (`BRD-2`, `BRD-007x`) **still** draw ID02; the
  existing `test_lint.py` broken-fixture assertion (which trips ID02 on `BRD-2`) stays green.
- Close `LINT-DOCID-HEADER-FALSE-POSITIVE` in `plans/FRAMEWORK-TODO.md`; `plans/HANDOFF.md`
  note. No CHANGELOG/version bump (no `framework/` change); record the rationale as a
  `plans/DECISIONS.md` D-0056 (behavioral narrowing of a lint rule, for the audit trail).

**Out of scope (deferred):**

- **Inline-code / link-target context parsing** (an alternative fix the TODO floated) —
  strictly weaker here: `PRD-Ready` is a *bare* table-cell token (not in code or a link), so a
  context parser would miss it. The digit-leading discriminator catches all four FPs and is
  simpler.
- **Masking letter-leading typos** (`BRD-O1` with a letter O) — the digit-leading rule would
  not flag these. Accepted: they are rare, and the pervasive `-Ready`/`-TEMPLATE` FPs on every
  consumer index far outweigh the theoretical letter-typo miss (the TODO explicitly sanctions
  "narrow … require the doc-id to be id-like"). *If this class ever matters,* a targeted
  follow-up could flag a token that is all-alphanumeric with **≥1 digit** (a mixed
  letter/digit id-like token, e.g. `BRD-O1`) while still skipping the all-letter prose tokens
  (`Ready`/`TEMPLATE`) — without reintroducing the FPs.

## Approach / Design (D-0056)

The valid doc-id form is `TYPE-<digits>` (`doc_re`, from `LAYER_REGISTRY.yaml`
`id_patterns.doc`). A `_DOC_ID` match whose captured second segment (`m.group(2)`) starts with
a **letter** cannot be a malformed instance of that form — it is a compound word. So the check
only needs to validate **digit-leading** candidates:

```python
# before:  if not doc_re.match(tok) and not tok.upper().endswith("-INDEX"):
# after:
seg = m.group(2)
# Only a digit-leading second segment is a plausible doc-id attempt (TYPE-NN); a
# letter-leading token (PRD-Ready, BRD-TEMPLATE, BRD-NN, <X>-INDEX) is a compound
# word/marker, not a malformed id (LINT-DOCID-HEADER-FALSE-POSITIVE, generalizes D-0043).
if seg[0].isdigit() and not doc_re.match(tok):
    findings.append(Finding(rel, i, "ID02", f"malformed document id '{tok}'"))
```

Validated against the token set:

| token | current ID02 | new ID02 | correct? |
| ----- | ------------ | -------- | -------- |
| `PRD-Ready` | flags (FP) | — | ✅ FP removed |
| `BRD-TEMPLATE` | flags (FP) | — | ✅ FP removed |
| `BRD-NN` | flags (FP) | — | ✅ FP removed |
| `SPEC-Final` | flags (FP) | — | ✅ FP removed |
| `BRD-2` | flags | flags | ✅ real malformed id kept (broken fixture) |
| `BRD-007x` | flags | flags | ✅ real malformed id kept |
| `BRD-00` / `BRD-01` | ok | ok | ✅ valid, unaffected |
| `BRD-INDEX` | ok (exempted) | ok (letter-leading) | ✅ D-0043 behavior preserved + generalized |

**Not a framework-spec change.** ID02 is not documented normatively in `framework/` (grep-
confirmed); the rule's contract ("malformed doc-ids are flagged") is unchanged — only the
false-positive scope is narrowed. Lint code is in `tools/` (vendored), so no `framework/**`
path is touched → GATE-SPEC does not fire and no version bump is due (the D-0043 precedent).

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `tools/sdd_doc_lint/__init__.py` | ID02 check: digit-leading discriminator (subsumes the `-INDEX` clause) |
| `platforms/hermes/sdd_doc_lint/__init__.py`, `platforms/claude-code-plugin/sdd_doc_lint/__init__.py` | regenerated by `sync-vendored.sh` (byte-identical) |
| `tools/sdd_doc_lint/tests/test_lint.py` | new ID02 false-positive / true-positive cases |
| `plans/DECISIONS.md` (D-0056) / `plans/FRAMEWORK-TODO.md` (close) / `plans/HANDOFF.md` | docs |

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | lint `framework/layers/01_BRD/BRD-00_index.TEMPLATE.md` | zero ID02 on `PRD-Ready` / `BRD-TEMPLATE` / `BRD-NN` | Objective |
| V2 | unit: `PRD-Ready`, `BRD-TEMPLATE`, `BRD-NN`, `SPEC-Final` → no ID02 | correct | FP removal |
| V3 | unit: `BRD-2`, `BRD-007x` → ID02 still fires | real malformed ids kept | no over-narrowing |
| V4 | `python -m pytest tools/sdd_doc_lint/tests -q` (incl. `test_broken_fixtures_trip_each_check` — ID02 on `BRD-2`) | green | existing tests |
| V5 | `diff` canonical vs both `platforms/*/sdd_doc_lint/__init__.py` | byte-identical | vendoring |
| V6 | `python -m pytest tests/conformance -q` (incl. `test_index_template_lint` `-INDEX` exemption + vendoring drift guard) | green | no regression |
| V7 | run the linter over `examples/*/docs/` | no NEW ID02 findings introduced/removed vs baseline (the corpus uses only real ids) | corpus cross-check |

## Docs to update

- [ ] `plans/DECISIONS.md` — D-0056 (digit-leading ID02 narrowing; generalizes D-0043)
- [ ] `plans/FRAMEWORK-TODO.md` — close `LINT-DOCID-HEADER-FALSE-POSITIVE`
- [ ] `plans/HANDOFF.md` — progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Narrowing masks a real malformed id | low | only letter-leading tokens are skipped; a doc-id is `TYPE-<digits>` — no real id is letter-leading (V3 keeps digit-leading malformed ids flagged; the broken fixture's `BRD-2` stays) |
| R2 | Editing a vendored mirror instead of canonical → drift-guard fail | low | edit `tools/` only; run `sync-vendored.sh`; V5 + V6 verify |
| R3 | Removing the explicit `-INDEX` clause regresses D-0043 | low | `-INDEX` is letter-leading → still skipped by the digit-leading rule; V6 (`test_index_template_lint`) confirms |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | `_DOC_ID` matches any `TYPE-<word>` token | `_DOC_ID = re.compile(rf"\b({_KNOWN})-([A-Za-z0-9]+)\b")` | tools/sdd_doc_lint/**init**.py:131 |
| 2  | The ID02 check flags any non-doc-form, non-`-INDEX` match (the bug) | `not tok.upper().endswith("-INDEX")` | tools/sdd_doc_lint/**init**.py:554 |
| 3  | `_KNOWN` is the closed type-code set | `_KNOWN = "BRD` | tools/sdd_doc_lint/**init**.py:130 |
| 4  | `doc_re` (the valid doc form) is passed into the scan | `doc_re,` | tools/sdd_doc_lint/**init**.py:472 |
| 5  | The broken fixture trips ID02 on a digit-leading `BRD-2` (must stay flagged) | `@brd: BRD-2` | tools/sdd_doc_lint/fixtures/broken/docs/03_EARS/EARS-02_bad.md:11 |
| 6  | The unit test asserts the broken fixtures trip ID02 | `"ID02",` | tools/sdd_doc_lint/tests/test_lint.py:26 |
| 7  | The conformance test asserts `-INDEX` tokens draw no ID02 (preserve) | `index_id02 = [f for f in findings if f.code == "ID02" and "-INDEX'" in f.message]` | tests/conformance/test_index_template_lint.py:59 |
| 8  | D-0043 precedent: a `sdd_doc_lint` bugfix that shipped with no version bump | `## D-0043 —` | plans/DECISIONS.md:414 |
| 9  | The vendor sync script copies canonical → each mirror | `cp "$canonical/__init__.py" "$dest/__init__.py"` | tools/sdd_doc_lint/sync-vendored.sh:16 |
| 10 | The vendoring drift guard (CI enforces byte-identity) | `class DocLintVendoring` | tests/conformance/platforms/test_doc_lint_vendoring.py:27 |

## Review log

### Pass 1 — 2026-07-06 — self-review

Draft after reproducing the four FPs on the BRD-00 index template + validating the
digit-leading discriminator against a token set (FPs removed; `BRD-2`/`BRD-007x` kept; the
broken-fixture `BRD-2` stays flagged; `-INDEX` behavior preserved and generalized). Confirmed
ID02 is not documented in `framework/` → pure linter bugfix, no GATE-SPEC, no bump (D-0043
precedent) → auto-mergeable. Pending: independent Pass 2.

### Pass 2 — 2026-07-06 — independent (fresh-context adversarial)

All 10 citations verified exact. Fix correctness confirmed against source: `doc_re` =
`^[A-Z]+-\d{2,}$`, so **a valid doc-id's post-hyphen segment is always all-digits → always
digit-leading**; therefore the digit-leading gate can never skip a valid id nor a
digit-leading malformed id — the sole behavioral delta is that letter-leading non-doc tokens
(which by construction can never satisfy `doc_re`) stop being flagged, exactly the FP class.
Token walk reconfirmed (`BRD-2` kept, `PRD-Ready`/`BRD-TEMPLATE`/`BRD-NN`/`SPEC-Final`/`BRD-INDEX`
skipped, `BRD-01` unaffected). No test breakage — only two ID02 assertion sites exist
(`test_lint.py` broken-fixture aggregate incl. `BRD-2`; `test_index_template_lint.py` filters
only `-INDEX'`), both survive. Framework-boundary confirmed: `grep -rn ID02 framework/` is
empty; modified paths are `tools/` + the two mirrors + `tests/` + `plans/` only → no
GATE-SPEC, D-0043 no-bump precedent applies. **One MINOR (acknowledged tradeoff, not a
defect):** the fix masks letter-leading typos (`BRD-O1`); already documented + accepted; added
a one-line follow-up note (a ≥1-digit heuristic) for completeness. 0 load-bearing.

### Pass 3 — 2026-07-06 — self-review (re-validate the Pass-2 fold)

Re-checked: the added Out-of-scope note is advisory only (does not expand scope); the
digit-leading invariant (valid id ⇒ digit-leading) is the load-bearing correctness argument and
holds; V2/V3/V4 exercise both the FP-removal and the kept-malformed-id branches; D-0056 is the
next free decision number (D-0055 = COV03). No new gaps.

**Result:** ready
