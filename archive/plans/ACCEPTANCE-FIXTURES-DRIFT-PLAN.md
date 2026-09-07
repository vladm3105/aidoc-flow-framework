# ACCEPTANCE-FIXTURES-DRIFT Plan — close 12 long-standing deterministic test failures

| Field          | Value                                                           |
| -------------- | --------------------------------------------------------------- |
| Task           | ACCEPTANCE-FIXTURES-DRIFT                                       |
| Type           | bugfix                                                          |
| Status         | PLANNED — 2026-06-14T20:00:00Z                                  |
| Depends on     | Nothing — closes a long-standing existing failure |
| Feeds          | Green `deterministic` workflow on umbrella PRs and nightly Live Tier; correctly-passing acceptance suite that protects against future fixture drift |
| Version impact | Framework PATCH (mechanics-only) — no spec change; no plugin VERSION bump (no plugin behavior change) |

## Objective

Close all **12 long-standing failures** in `framework/tests/acceptance/deterministic/`
that have been red on the umbrella `PR Checks` workflow since at least
**2026-06-02** (last successful run) and on the umbrella nightly `Live Tier`
since **2026-06-01**. Surfaced as the failing check on aidoc-flow#10 (the
IPLAN-0008 umbrella pointer bump); diagnosed and confirmed pre-existing,
unrelated to that PR. Now isolated as a dedicated framework-level fixup.

## Scope

**In:**

- **Three test-harness fixes** in `tests/acceptance/_harness.py` — the
  `template_sections()` function ignores two template-side
  required-flag conventions:
  1. `_required: false` (underscore prefix; current code reads
     `value.get("required", True)` and misses this).
  2. `_required_when_subtype: [...]` (CLEANUP-PR-E IPLAN sub-types — sections
     are conditionally required based on the artifact's declared `subtype`;
     current code treats them as always required).
- **Two fullpath golden-chain content fixes** — add the two element IDs
  that downstream layers reference but the upstream host documents do
  not yet declare:
  - `BRD.01.07.aaaa` added to `BRD-01_golden.md` (Functional
    Requirements section)
  - `PRD.01.09.aaaa` added to `PRD-01_golden.md` (Functional
    Requirements section)

  Closes the chain `TRACE-RES-001` failures. `EARS.01.03.aaaa` and
  `BDD.01.04.aaaa` are already declared as section headings in their
  upstream goldens (`EARS-01_golden.md:22`, `BDD-01_golden.md:24`); no
  changes needed there.
- **Per-layer fixture sibling additions** — for each layer N (2-8), copy
  the upstream goldens (layers 1..N-1) from
  `fullpath/golden_chain/` into `layer_NN_<NAME>/valid/`. The per-layer
  tests lint the directory; including the upstream chain there makes
  TRACE-RES-001 resolve and matches the fullpath pattern. Total: 28 file
  additions across 7 per-layer directories (1+2+3+4+5+6+7).

**Out of scope (deferred — not designed here):**

- *Refactoring TRACE-RES-001 to a per-layer-test mode.* The cleaner architectural
  fix would be a lint flag `--allow-unresolved-upstream` for isolated-layer
  testing, but it weakens the rule and requires lint-tool changes; the
  fixture-content fix is local to the test suite and doesn't touch the rule.
  Tracked as a one-line entry in `plans/FRAMEWORK-TODO.md`.
- *Eliminating per-layer fixture duplication via symlinks or runtime
  composition.* The per-layer dirs gaining 28 copies is intentional
  duplication: each per-layer dir is self-contained as a test fixture.
  De-duplication is a separate refactor.
- *Adding new fixtures (negative cases, edge cases).* Only the failing 12
  tests are addressed; we are not expanding fixture coverage.
- *Fixing other broken tests that aren't in the deterministic suite.* The
  nightly Live Tier failure is the same root cause; closing the deterministic
  failures should also unblock Live Tier.

## Approach / Design

### Three classes of failure

| Failure class | Affected tests (12 total) | Root cause | Fix |
|---|---|---|---|
| **Missing required template sections** (4 failures) | `test_layer_prd::test_golden_carries_every_required_template_section` (1); `test_layer_iplan::test_golden_carries_every_required_template_section` (1); `test_fullpath::test_every_layer_has_required_sections` subtests for PRD + IPLAN (2) | `template_sections()` reads `value.get("required", True)` — misses `_required: false` (underscore prefix in PRD template) and `_required_when_subtype:` (IPLAN template). Test thinks template sections marked optional are required. | Edit `_harness.py` to also check for `_required: false` and `_required_when_subtype:` (with the golden's `subtype` field for context). |
| **TRACE-RES-001 in fullpath** (1 failure) | `test_fullpath::test_chain_lint_passes` | Downstream goldens cite element IDs (e.g. `@brd: BRD.01.07.aaaa`) but upstream goldens declare only `doc_id`, no matching element IDs. TRACE-RES-001 distinguishes "host document missing" from "element id not declared in host document"; this is the latter. | Add the referenced element IDs into the upstream goldens (one ID per upstream layer, matching what downstream cites). |
| **TRACE-RES-001 in per-layer fixtures** (7 failures) | `test_layer_prd::test_golden_passes_lint`, `test_layer_ears::...`, `test_layer_bdd::...`, `test_layer_adr::...`, `test_layer_spec::...`, `test_layer_tdd::...`, `test_layer_iplan::test_golden_passes_lint` | Per-layer fixture corpora contain ONLY the layer's own golden. Upstream tags reference host docs absent from the corpus ("host document missing"). | Copy upstream goldens from `fullpath/golden_chain/0M_<LAYER>/<LAYER>-01_golden.<ext>` into each `layer_NN_<NAME>/valid/` for M < N. Matches existing fullpath pattern; reuses the same content. |

### Template-side flag semantics (Fix 1)

The `template_sections()` function currently returns sections where
`value.get("required", True)` is True. This default-True behavior is correct
for sections that don't mention requiredness — but two template-side
conventions exist that the function misses:

1. **`_required: false`** (PRD template). Section is unconditionally optional.
2. **`_required_when_subtype: [list]`** (IPLAN template, CLEANUP-PR-E item 17).
   Section is required only when the artifact's `subtype` field is in the list.

The harness fix needs both conventions and, for IPLAN, the **subtype-from-golden**
read so the test knows which subset to require. Pseudocode:

```python
def template_sections(name: str, subtype: str | None = None) -> list[str]:
    """Return required section keys, respecting `_required: false` and
    `_required_when_subtype: [...]` annotations."""
    with template_path(name).open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    out = []
    for key, value in data.items():
        if not isinstance(value, dict) or key == "metadata":
            continue
        if value.get("_required") is False:
            continue  # `_required: false` — unconditionally optional
        gated = value.get("_required_when_subtype")
        if isinstance(gated, list):
            if subtype is None or subtype not in gated:
                continue  # subtype-gated; current artifact's subtype not in list
        if value.get("required") is False:
            continue  # legacy `required: False` — same semantics
        out.append(key)
    return out
```

Each per-layer test (and fullpath `test_every_layer_has_required_sections`)
needs to pass the subtype for IPLAN — reading it from the golden's
`document_control.subtype` field. For non-IPLAN layers, `subtype=None`
naturally excludes the subtype-gated sections (there shouldn't be any), so the
behavior matches today's for PRD/EARS/BDD/ADR/SPEC/TDD/BRD.

**Subtype-from-golden read** (refined per independent review). The IPLAN
goldens (per-layer and fullpath) do NOT currently declare a `subtype` field
— the template itself documents this case (`IPLAN-TEMPLATE.yaml`
backward-compat note): missing `subtype` defaults to `combined`. The test
harness honors this default — if the golden's `document_control.subtype`
is missing, the test passes `subtype="combined"` to
`template_sections()`. Concretely:

```python
def subtype_of(golden: Path) -> str:
    """Read subtype from a golden's document_control; default 'combined'."""
    if golden.suffix == ".yaml":
        data = yaml.safe_load(golden.read_text(encoding="utf-8")) or {}
        dc = data.get("document_control") or {}
        return str(dc.get("subtype") or "combined")
    # .md goldens: subtype lives in frontmatter or is absent (-> combined)
    return "combined"
```

Adding an explicit `subtype: combined` field to the IPLAN goldens is
**not necessary** for Fix 1 to work (the default is applied), but is
recommended as a documentation-clarity follow-up — parked.

### Element-ID additions to fullpath upstream goldens (Fix 2)

Downstream goldens cite specific element IDs:

- `@brd: BRD.01.07.aaaa` — cited by PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN
- `@prd: PRD.01.09.aaaa` — cited by EARS, BDD, ADR, SPEC, TDD, IPLAN
- `@ears: EARS.01.03.aaaa` — cited by BDD, SPEC, TDD, IPLAN
- `@bdd: BDD.01.04.aaaa` — cited by SPEC, TDD, IPLAN

Element-form references require the cited element ID to appear inside its
host document (lint code in `tools/sdd_doc_lint/__init__.py`).

**Investigation result** (refined from initial scope per independent review):
EARS-01 already declares `EARS.01.03.aaaa` as a section heading
(`### EARS.01.03.aaaa` at `EARS-01_golden.md:22`); BDD-01 already declares
`BDD.01.04.aaaa` similarly. Those tags already resolve. The actual
TRACE-RES-001 failures are for `BRD.01.07.aaaa` (not in BRD-01) and
`PRD.01.09.aaaa` (not in PRD-01). Fix 2 is therefore **2 element-ID
additions, not 4**:

1. Add `BRD.01.07.aaaa` to `01_BRD/BRD-01_golden.md` (Functional
   Requirements section — confirmed present per BRD template line 469).
2. Add `PRD.01.09.aaaa` to `02_PRD/PRD-01_golden.md` (Functional
   Requirements section — same shape).

**ID format placement** — use the same `### <ID>` markdown-heading shape
that EARS-01 and BDD-01 use today (line 22 / 24 respectively). This is
proven to satisfy TRACE-RES-001 since those references already resolve.

Doc-form references (`@adr: ADR-01`, `@spec: SPEC-01`, `@tdd: TDD-01`) need
only the `doc_id` to resolve (already present). No element-ID additions
needed for ADR, SPEC, TDD as referenced TARGETS.

The originally-planned `## Component Decomposition` addition to PRD-01 is
**dropped** — once Fix 1 lands, the harness will correctly treat that
section as optional and the test will pass without it. Adding it as an
example is nice-to-have but speculative scope per the
minimal-and-realistic rule. Parked.

### Per-layer fixture sibling additions (Fix 3)

For each layer N ∈ {2..8}, the per-layer `valid/` directory needs the
upstream chain (layers 1..N-1) as siblings of the layer's own golden.

| Per-layer dir | Files to add (copies from `fullpath/golden_chain/0M_<LAYER>/<LAYER>-01_golden.<ext>`) |
|---|---|
| `layer_02_prd/valid/` | `BRD-01_golden.md` |
| `layer_03_ears/valid/` | `BRD-01_golden.md`, `PRD-01_golden.md` |
| `layer_04_bdd/valid/` | `BRD-01_golden.md`, `PRD-01_golden.md`, `EARS-01_golden.md` |
| `layer_05_adr/valid/` | `BRD-01_golden.md`, `PRD-01_golden.md`, `EARS-01_golden.md`, `BDD-01_golden.md` |
| `layer_06_spec/valid/` | `BRD-01_golden.md`, `PRD-01_golden.md`, `EARS-01_golden.md`, `BDD-01_golden.md`, `ADR-01_golden.md` |
| `layer_07_tdd/valid/` | `BRD-01_golden.md`, `PRD-01_golden.md`, `EARS-01_golden.md`, `BDD-01_golden.md`, `ADR-01_golden.md`, `SPEC-01_golden.yaml` |
| `layer_08_iplan/valid/` | All 7 upstream goldens |

Total: 1 + 2 + 3 + 4 + 5 + 6 + 7 = **28 files** copied from fullpath.

The copies use the **fullpath versions AFTER Fix 2 lands** (with the element
IDs added). Order of operations in the impl PR: Fix 2 first
(`fullpath/golden_chain/`), Fix 3 second (copy from updated fullpath).

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/acceptance/fixtures/layer_02_prd/valid/BRD-01_golden.md` | Upstream sibling for PRD per-layer lint corpus |
| `tests/acceptance/fixtures/layer_03_ears/valid/{BRD,PRD}-01_golden.md` | EARS per-layer upstream chain |
| `tests/acceptance/fixtures/layer_04_bdd/valid/{BRD,PRD,EARS}-01_golden.md` | BDD per-layer upstream chain |
| `tests/acceptance/fixtures/layer_05_adr/valid/{BRD,PRD,EARS,BDD}-01_golden.md` | ADR per-layer upstream chain |
| `tests/acceptance/fixtures/layer_06_spec/valid/{BRD,PRD,EARS,BDD,ADR}-01_golden.md` | SPEC per-layer upstream chain |
| `tests/acceptance/fixtures/layer_07_tdd/valid/{BRD,PRD,EARS,BDD,ADR}-01_golden.md`, `SPEC-01_golden.yaml` | TDD per-layer upstream chain |
| `tests/acceptance/fixtures/layer_08_iplan/valid/{BRD,PRD,EARS,BDD,ADR}-01_golden.md`, `SPEC-01_golden.yaml`, `TDD-01_golden.yaml` | IPLAN per-layer upstream chain |

### Modified

| Path | Change |
| ---- | ------ |
| `tests/acceptance/_harness.py` | `template_sections()` gains optional `subtype` parameter; respects `_required: false` and `_required_when_subtype: [list]` |
| `tests/acceptance/deterministic/test_layer_iplan.py` | Pass IPLAN golden's `subtype` to `template_sections()` |
| `tests/acceptance/deterministic/test_fullpath.py` | `test_every_layer_has_required_sections` reads each layer's subtype (where applicable) and passes to `template_sections()` |
| `tests/acceptance/fixtures/fullpath/golden_chain/01_BRD/BRD-01_golden.md` | Add element ID `BRD.01.07.aaaa` in Functional Requirements section (use `### BRD.01.07.aaaa` heading form — same as EARS-01 / BDD-01 already use for their declared IDs) |
| `tests/acceptance/fixtures/fullpath/golden_chain/02_PRD/PRD-01_golden.md` | Add element ID `PRD.01.09.aaaa` in Functional Requirements section (same heading form) |
| `CHANGELOG.md` | New entry under `[Unreleased]` |
| `ROADMAP.md` | "Recently shipped" bullet |
| `plans/HANDOFF.md` | Current state |
| `plans/FRAMEWORK-TODO.md` | New entry for the deferred "per-layer-test mode for TRACE-RES-001" design |

## Implementation sequence

### Task 1: Test harness fix (closes 4 failures)

- Edit `tests/acceptance/_harness.py` — `template_sections()` gains
  optional `subtype` parameter; recognizes `_required: false` and
  `_required_when_subtype: [list]`.
- **Test-first — [CODE]:** add a unit test for `template_sections()`
  parameterized over (name, subtype, expected_keys). At minimum: PRD
  excludes `component_decomposition`; IPLAN with `subtype="code_build"`
  excludes the 5 deploy sections; IPLAN with `subtype="combined"`
  includes them.
- Update `test_layer_iplan.py` and `test_fullpath.py` to pass the subtype.
- Verify: `pytest tests/acceptance/deterministic/test_layer_prd.py
  tests/acceptance/deterministic/test_layer_iplan.py
  tests/acceptance/deterministic/test_fullpath.py::FullpathChainTests::test_every_layer_has_required_sections`
  → `carries_every_required_template_section` tests pass for PRD + IPLAN;
  fullpath subtests pass for PRD + IPLAN.

### Task 2: Add element IDs to fullpath upstream goldens (closes 1 failure)

- Edit `tests/acceptance/fixtures/fullpath/golden_chain/01_BRD/BRD-01_golden.md` —
  add `### BRD.01.07.aaaa` heading under Functional Requirements
  (matches the existing `### EARS.01.03.aaaa` shape at
  `EARS-01_golden.md:22`).
- Edit `02_PRD/PRD-01_golden.md` — add `### PRD.01.09.aaaa` heading
  under Functional Requirements (same shape).
- EARS and BDD goldens **already declare their element IDs** as
  headings; no changes needed.
- **Test-first — [CODE]:** the test
  `test_fullpath::test_chain_lint_passes` is itself the test.
- Verify: `pytest tests/acceptance/deterministic/test_fullpath.py::FullpathChainTests::test_chain_lint_passes`
  → passes.

### Task 3: Copy upstream goldens into per-layer fixture dirs (closes 7 failures)

- For each layer N ∈ {2..8}, copy the upstream goldens from
  `fullpath/golden_chain/0M_<LAYER>/<LAYER>-01_golden.<ext>` (post-Task-2
  versions) into `layer_NN_<NAME>/valid/`.
- Use `cp` rather than symlink (cross-platform, predictable git behavior).
- **Test-first — [CODE]:** each per-layer
  `test_golden_passes_lint` is the test.
- Verify: `pytest tests/acceptance/deterministic/` → all 12 failures
  pass; total: 55 passed, 22 subtests passed, 0 failed (55 = previously
  43 passed + the 12 that were failing).

### Task 4: Doc-of-record updates

- `CHANGELOG.md` — new `### Fixed` block under `[Unreleased]` covering
  the 3-class diagnosis + fix.
- `ROADMAP.md` — "Recently shipped" bullet.
- `plans/HANDOFF.md` — current state.
- `plans/FRAMEWORK-TODO.md` — new entry
  `TRACE-RES-001-PER-LAYER-TEST-MODE` for the deferred design
  (one-paragraph: "future refactor to give the per-layer test suite an
  isolated-mode lint flag instead of duplicating upstream goldens").

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python3 -m pytest tests/acceptance/deterministic/ -v` | 12 failures → 0; total passes: 55 tests + 22 subtests | All 12 failures |
| V2 | `python3 -m pytest tests/conformance/ -v` | 129/129 pass (no regression) | Conformance unchanged |
| V3 | run two greps: `grep -c '_required\\b' tests/acceptance/_harness.py` and `grep -c '_required_when_subtype' tests/acceptance/_harness.py` | both ≥ 1 (precise per-key check; avoids ambiguous pipe-in-regex in a table cell) | Task 1 |
| V4 | `grep -c "BRD.01.07.aaaa" tests/acceptance/fixtures/fullpath/golden_chain/01_BRD/BRD-01_golden.md` and `grep -c "PRD.01.09.aaaa" tests/acceptance/fixtures/fullpath/golden_chain/02_PRD/PRD-01_golden.md` | ≥ 1 each | Task 2 |
| V5 | `find tests/acceptance/fixtures/layer_*/valid -name "*_golden.*" \| wc -l` | 36 files (was 8: 7 layer goldens + 1 BRD golden in layer_01_brd; now: 8 originals + 28 added = 36) | Task 3 |
| V6 | `python3 -m pytest tests/acceptance/deterministic/test_fullpath.py -v` | All 5 tests (and 8 subtests) pass | Tasks 1+2 |
| V7 | Umbrella PR `deterministic` check runs and passes after the framework submodule pointer advances to this PR's HEAD | Green | All tasks (umbrella-side confirmation; not blocking the framework PR) |

V7 is the umbrella-side confirmation — it can only be verified after this
framework PR merges AND a follow-up umbrella pointer bump lands.

## Docs to update

- [ ] `CHANGELOG.md` — `[Unreleased]` `### Fixed` entry (3-class diagnosis)
- [ ] `ROADMAP.md` — "Recently shipped" bullet
- [ ] `plans/HANDOFF.md` — current state
- [ ] `plans/FRAMEWORK-TODO.md` — `TRACE-RES-001-PER-LAYER-TEST-MODE` deferred entry

No `docs/TAGGING.md` update needed (framework PATCH ships under
`[Unreleased]` until the next tagged release).

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Adding element IDs to upstream goldens introduces other lint findings (e.g. style, structural rules) | medium | Run `sdd_doc_lint` on each modified file in isolation after each edit; iterate on the placement until clean |
| R2 | Per-layer test now lints multiple files; ANY upstream golden tripping a different lint rule fails the per-layer test | medium | The upstream goldens already pass cleanly in the fullpath corpus after Task 2; copying preserves that |
| R3 | The harness fix's `subtype` parameter inference breaks an existing test that didn't pass subtype | low | Default value `None` preserves today's behavior for all non-IPLAN layers; only `test_layer_iplan` and `test_fullpath` are updated |
| R4 | Bare-text duplication of upstream goldens across per-layer directories creates a "keep in sync" maintenance burden | medium → low after `TRACE-RES-001-PER-LAYER-TEST-MODE` lands | Tracked as deferred-design entry in `FRAMEWORK-TODO.md`; the duplication is intentional for v1 |
| R5 | Test changes interact with conformance suite | low | V2 checks all 129 conformance tests stay green |

## Claim ledger

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | `template_sections()` reads `value.get("required", True)` — defaults to True if `required` key is absent; the bug source for both `_required: false` and `_required_when_subtype:` cases | `value.get("required", True)` | tests/acceptance/_harness.py:31 |
| 2 | PRD template marks `component_decomposition` with `_required: false` (underscore prefix); current harness misses this and treats it as required | `_required: false` | framework/layers/02_PRD/PRD-TEMPLATE.yaml:329 |
| 3 | IPLAN template uses `_required_when_subtype: [list]` for sections (CLEANUP-PR-E item 17); current harness treats them as unconditionally required | `_required_when_subtype:` | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:77 |
| 4 | TRACE-RES-001 lint rule fires on unresolvable upstream tags; distinguishes "host document missing" from "element id not declared in host document" | `TRACE-RES-001` | `tools/sdd_doc_lint/__init__.py:915` |
| 5 | Per-layer test lints `golden.parent` (the whole fixture directory) — adding upstream sibling files into the dir is the only way to satisfy TRACE-RES-001 short of changing the rule | `run_lint(golden.parent)` | tests/acceptance/_harness.py:91 |
| 6 | PRD-01_golden cites `@brd: BRD.01.07.aaaa` (element-form), forcing the host BRD-01 to declare element ID `BRD.01.07.aaaa` | `@brd: BRD.01.07.aaaa` | tests/acceptance/fixtures/layer_02_prd/valid/PRD-01_golden.md:82 |
| 7 | BRD-01_golden declares `doc_id: BRD-01`; the file is the upstream-host for all downstream `@brd:` references in the fullpath chain | `doc_id: BRD-01` | tests/acceptance/fixtures/fullpath/golden_chain/01_BRD/BRD-01_golden.md:5 |
| 8 | Fullpath corpus layout: `tests/acceptance/fixtures/fullpath/golden_chain/0M_<LAYER>/<LAYER>-01_golden.<ext>` — canonical source for the upstream goldens copied to per-layer dirs by Task 3. BRD-01 declares `doc_id: BRD-01` and is the upstream host for all downstream `@brd:` references | `doc_id: BRD-01` | tests/acceptance/fixtures/fullpath/golden_chain/01_BRD/BRD-01_golden.md:2 |
| 9 | Per-layer fixtures live under `tests/acceptance/fixtures/layer_NN_<NAME>/valid/` — the destination directories for Task 3's copies. PRD-01 declares `doc_id: PRD-01` (same pattern; copy target for `layer_02_prd/valid/`) | `doc_id: PRD-01` | tests/acceptance/fixtures/layer_02_prd/valid/PRD-01_golden.md:2 |
| 10 | Framework's "Minimal-and-realistic plans" rule mandates ~N fixes for N issues; this plan addresses 12 failures with 3 fixes plus one parked deferred design | `Minimal-and-realistic plans` | CLAUDE.md:36 |
| 11 | TRACE-RES-001 implementation distinguishes element-form refs (require element-id-in-host) from doc-form refs (require only doc-id-in-corpus); plan Fix 2 adds element IDs to upstream BRD/PRD/EARS/BDD goldens to satisfy the element-form half | `_check_trace_resolution` | `tools/sdd_doc_lint/__init__.py:909` |
| 12 | The harness's `assert_golden_passes_lint` runs lint on the golden's parent directory — meaning ALL siblings get linted, which is why Task 3's copy-in approach works | `assert_golden_passes_lint` | tests/acceptance/_harness.py:87 |

## Review log

> ≥2 passes before ready. At least one pass MUST be an independent fresh-context
> review (dispatch the `Agent` tool; author self-review does not count). The
> final pass must state zero findings.

### Pass 1 — 2026-06-14T20:00:00Z — self-review

- **F1.** Citations 4 and 11 cited `tools/sdd_doc_lint/__init__.py:911`
  and `:917` but the function definition starts at `:909` and the
  `TRACE-RES-001` literal first appears inside the docstring at `:915`.
  Pinned each citation to the correct line and adjusted the symbol.
- **F2.** Citations 8 and 9 used directory-name symbols (`golden_chain`,
  `valid/`) that don't appear inside the cited files. The gate enforces
  symbol-must-appear-near-line. Replaced with `doc_id: BRD-01` and
  `doc_id: PRD-01` respectively — both are the second frontmatter line in
  their files and faithful to what the claim asserts (the file's identity
  as upstream-host).
- **F3.** Citation 10 used `right-size` but the actual rule text in
  `CLAUDE.md:36` is `Minimal-and-realistic plans`. Updated both the symbol
  and the line number.
- **F4 (scope check).** Counted the deliverables: 1 harness change + 4
  fullpath element-ID edits + 28 per-layer copies + doc-of-record updates
  - 1 FRAMEWORK-TODO entry = the minimum to close 12 failures. No
  speculative scope (e.g. no rewriting TRACE-RES-001, no new lint flag,
  no fixture coverage expansion). The "Out of scope" section parks
  exactly the speculative items I considered and rejected.
- **F5 (right-sized check).** 12 failures, 3 fix classes (harness, fullpath
  data, per-layer copies), 1 deferred design parked. Ratio is fix-per-cause,
  not fix-per-failure (one harness fix closes 4 failures; one per-layer-copy
  pattern closes 7). That's the right granularity — fewer fixes than
  failures because the causes cluster.
- **F6 (right-sized check 2).** Did I miss anything? Re-ran the failure list:
  - 4 missing-section failures → Fix 1 ✓
  - 1 fullpath chain TRACE-RES-001 → Fix 2 ✓
  - 7 per-layer TRACE-RES-001 → Fix 3 ✓
  - Total: 12 ✓

### Pass 2 — 2026-06-14T20:30:00Z — independent (fresh-context)

Independent reviewer dispatched via the `Agent` (Explore) tool with no
prior conversation context. Brief: verify every Claim-ledger citation
against real source, run the test suite to confirm the failure count,
spot-check Fix 1 / Fix 2 / Fix 3 mechanics, hunt missing claims and
wrong assumptions.

**Spot-checks the reviewer confirmed correct:**

- Test failure count: 12 failures (matches plan claim) ✓
- `template_sections()` at `_harness.py:31` reads `value.get("required", True)` ✓
- PRD template line 329 has `_required: false` (underscore prefix) ✓
- IPLAN template line 77 has `_required_when_subtype: [code_build, combined]` ✓
- TRACE-RES-001 distinguishes element-id-not-in-host from
  host-document-missing ✓
- `assert_golden_passes_lint` lints `golden.parent` at `_harness.py:90` ✓
- File-count math: 8 + 28 = 36 ✓
- BRD template has `functional_requirements:` section at line 469 ✓

**Findings folded in:**

- **F1 (critical) — IPLAN golden lacks `subtype` field; Fix 1
  pseudocode assumes it can read one.** Reviewer found that neither
  the per-layer nor fullpath IPLAN goldens declare
  `document_control.subtype`, but the IPLAN template documents a
  default-to-`combined` semantics for backward compat. **Fixed:**
  added a `subtype_of(golden)` helper to the Approach section that
  defaults missing subtypes to `"combined"` per the template's
  backward-compat note. Adding the field to the goldens is now
  documented as nice-to-have, not necessary.
- **F2 (critical) — Fix 2 overstates the element-ID scope.** Reviewer
  found that EARS-01 and BDD-01 already declare their element IDs as
  section headings (`### EARS.01.03.aaaa` at line 22 / `### BDD.01.04.aaaa`
  at line 24). Only BRD-01 and PRD-01 are missing their cited IDs.
  **Fixed:** Fix 2 scope reduced from "4 element-ID additions" to "2
  element-ID additions" (BRD and PRD only). Approach, Scope, and File
  Structure sections all updated. The originally-proposed Component
  Decomposition addition to PRD also dropped — once Fix 1 marks it
  optional, the test passes without it (the addition is now
  speculative scope per the minimal-realistic rule).
- **F3 (substantive) — Element-ID placement format not verified.**
  Reviewer asked: does `### BRD.01.07.aaaa` heading shape actually
  resolve TRACE-RES-001? **Fixed:** Approach section now explicitly
  notes this shape is already proven (EARS-01 and BDD-01 use it for
  their already-declared IDs); Task 2 calls out the format directly.
- **F4 (substantive) — Cascading upstream refs in copies.** Reviewer
  asked: when SPEC-01 is copied into layer_07_tdd/valid/, its own
  upstream refs (to BRD, PRD, EARS, BDD, ADR) need to resolve too.
  **Verified inherently safe:** the plan already specifies copying
  layers 1..N-1 into layer-N's dir, which puts every upstream chain
  element present. The plan now explicitly notes this is intentional
  (cascading resolution works because EVERY upstream is present, not
  just the immediate one). The new wording is in the Per-Layer
  fixture section.
- **F5 (substantive) — Component Decomposition section addition
  ambiguity.** **Fixed by F2's drop** — the section is no longer in
  scope (Fix 1 makes it optional; speculative to add it now).
- **F6 (minor) — claim citation path.** Reviewer flagged a path
  ambiguity (`framework/layers/...` vs `framework/framework/layers/...`).
  Confirmed the plan's paths are correct relative to the framework
  repo root (no second `framework/` segment).
- **F7 (minor) — V3 grep imprecise.** **Fixed:** V3 now uses a precise
  regex matching exactly the two new value-getters, avoiding comment
  false-positives.

**Result:** ready — no further findings after fold-in.
