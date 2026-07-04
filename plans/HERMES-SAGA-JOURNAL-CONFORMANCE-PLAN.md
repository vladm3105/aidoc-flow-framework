# HERMES-SAGA-JOURNAL-CONFORMANCE Plan (H-12) — real Hermes saga journals conform to saga.schema.json

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | HERMES-SAGA-JOURNAL-CONFORMANCE (H-12)       |
| Type           | bugfix                                       |
| Status         | IMPLEMENTED — 2026-07-03 (3 review passes, 1 independent; all V-checks green) |
| Depends on     | none (independent) |
| Feeds          | closes the "saga journal parity" claim for real output; sanctions CHG review |
| Version impact | **framework spec PATCH** (`0.32.6 → 0.32.7`, add `09_CHG` to `saga.schema.json`) + **Hermes PATCH** (`0.5.0 → 0.5.1`, journal now conforms). GATE-SPEC applies (framework change). |

## Objective

Hermes's **real** saga journal (serialized from `SagaRunState` via `asdict`) is
missing 4 `saga.schema.json`-required fields — `artifact_id`, `layer`, `iteration`,
`transitions` — and it never records `transitions` at all (`update_run_status`
only replaces `status`). The Phase-1 conformance guard
(`test_saga_lifecycle_parity.py`) validates only **hand-authored fixtures** (written
*with* those fields), so the "both platforms' saga journals conform to the shared
schema" parity claim (D-0031) is **aspirational for Hermes**, not enforced against
real output. This fixes the real journal to conform (populate the 3 scalar fields +
record schema-shaped transitions), adds `09_CHG` to the schema enum so CHG review
journals also validate (completing the Phase-3 CHG sanctioning), and adds a
conformance test that validates a **real** Hermes journal — not a fixture.

## Scope

**In:**

- **`SagaRunState`** (`saga_models.py:25`) — add `artifact_id: str = ""`,
  `layer: str = ""`, `iteration: int = 1`, `transitions: list[dict[str, object]] =
  field(default_factory=list)` (all defaulted → backward-compatible).
- **`saga_journal.py`** — `_to_run_state` deserializes the 4 new fields;
  `create_saga_journal` seeds the initial `{ts, from: null, to: "PREPARED", scope:
  "run"}` transition; `update_run_status` appends `{ts, from: <prev>, to: <target>,
  scope: "run"}`; `set_branch_state` appends `{ts, from: <prev branch status|null>,
  to: <branch.status>, scope: "branch:<persona>"}` (scope matches the schema's
  `^(run|branch:[a-z_]+)$`).
- **Orchestrator** (`saga_orchestrator.py:603`) — build the initial `SagaRunState`
  with `artifact_id=doc_id` (`_extract_doc_id`, `:581`), `iteration=1`, and a
  **derived** `layer` — `normalize_layer(layer or doc_type)[1]` (the existing helper
  at `playbook_loader.py:61`, already imported from that module). This sources the
  enum-form layer from the **required** `doc_type` when the **optional** `--layer`
  is omitted (its default is `None`, `cli/main.py:89`), so the default invocation
  still emits a schema-valid `layer` — see "Deriving `layer` robustly" below.
- **Framework** — add `"09_CHG"` to the `saga.schema.json` `layer` enum
  (`:35-36`) so a CHG review journal (`layer: "09_CHG"`) validates → framework PATCH
  bump; re-vendor.
- **Conformance test** — validate a **real** Hermes journal (generated in-test end
  to end for a lifecycle layer AND a CHG run) against `saga.schema.json`; extend or
  sibling `test_saga_lifecycle_parity.py`. This is the guard that would have caught
  H-12.
- Update any affected Hermes tests. The only file constructing `SagaRunState` /
  asserting journal shape is `test_saga_review_journal.py` (keyword construction, no
  exact key-set assert) — it likely needs **no** change since the new fields are
  defaulted and appended last; V5 confirms. Framework `0.32.6 → 0.32.7` + Hermes
  `0.5.0 → 0.5.1`; CHANGELOGs; PARITY;
  D-0048; close H-12 in `HERMES-BACKLOG.md`; HANDOFF.

**Out of scope (deferred):**

- **`from: PARTIAL_TIMEOUT` / resume-walk semantics (G-R1).** H-12 records
  schema-*shaped* transitions; the break-circuit resume semantics (walk transitions
  backward, never `from: PARTIAL_TIMEOUT`) are Phase-1b / H-1, untouched here.
- **Multi-iteration `iteration` tracking.** Hermes runs a single review pass;
  `iteration` is fixed at 1 (schema requires ≥1). A real audit→fix→re-review loop
  incrementing it is a later concern.
- **Whether the *plugin's* real journals conform** — H-12 is Hermes-side; the
  plugin's `saga_driver` journal conformance is a separate check if needed.
- H-6/H-2 calibration deltas; `prompt_only` injection; H-11.

## Approach / Design (D-0048)

### The four gaps, and how each is filled

| Schema-required | Today | Fix |
|---|---|---|
| `artifact_id` | absent | `doc_id` from `_extract_doc_id` into `SagaRunState`. The regex is `([A-Z]+-\d+)` (`saga_orchestrator.py:66`); it conforms to the schema `^[A-Z]+-[0-9]{2}$` for standard `TYPE-NN` filenames (per `ID_NAMING_STANDARDS`) and the `f"{doc_type.upper()}-00"` fallback — see R4 for the non-standard-filename edge |
| `layer` | absent | `normalize_layer(layer or doc_type)[1]` → enum-form dir (e.g. `01_BRD`, `09_CHG`); **derived from the required `doc_type`**, not the optional `--layer` — see "Deriving `layer` robustly" |
| `iteration` | absent | `1` (single review pass; ≥1 per schema) |
| `transitions` | **never recorded** | append a schema-shaped entry on each run/branch state change |

### Transitions — the substantive part

Currently no transition history exists. Record it where state changes:

- **run scope:** `update_run_status` appends `{ts, from: run.status, to: target,
  scope: "run"}` before writing.
- **branch scope:** `set_branch_state` appends `{ts, from: <prior branch status or
  null>, to: branch.status, scope: "branch:<persona>"}`.
- **seed:** `create_saga_journal` writes the initial `{ts, from: null, to:
  "PREPARED", scope: "run"}` (schema allows `from: null`).
- `ts` uses the existing `_utc_now_iso()`. This makes the journal replay the state
  machine, matching the plugin's `saga.json` transition list + the schema.

Two precision points (from the schema): (a) `transitions` items are
`additionalProperties: false`, so each appended entry carries **exactly**
`{ts, from, to, scope}` — no extra keys. (b) A transition is appended **only on a
successful state change** — inside `update_run_status` *after* the `can_transition`
check passes (never on the idempotent-retry `ValueError` path that `_safe_transition`
swallows), and in `set_branch_state` only when the branch status actually changes.

### Deriving `layer` robustly (the default-path trap)

The naive fix — `layer=layer` from the saga call — is **insufficient** and would
re-create the exact "test passes, real output doesn't" defect H-12 exists to kill.
`--layer` is **optional** (`default=None`, `cli/main.py:89`; `tool_registry.py:1549`
`arguments.get("layer")`) and free-text, whereas `--doc-type` is **required**
(`cli/main.py:84`). If a test passes an explicit valid `layer="01_BRD"` it goes
green while the real default invocation (layer omitted) emits `layer: null` →
fails the schema `type:string`+enum. So derive from the reliable signal:
`normalize_layer(layer or doc_type)[1]` — the existing helper
(`playbook_loader.py:61`) already maps **either** the doc-type form (`brd`) **or**
the directory form (`01_BRD`) to the enum-form dir, so it conforms whether `--layer`
is supplied (enum-form) or omitted (falls back to the required `doc_type`). V2b
below explicitly exercises the **layer-omitted** path.

Scope caveat (low-likelihood): the branch `scope` `^(run|branch:[a-z_]+)$` requires
`[a-z_]+` personas. All `REVIEW_CREWS.yaml` lenses + the extra Hermes personas
(`fact_checker`, `chairperson`) are lowercase-snake and conform; a user-supplied
`--personas` value with digits/uppercase/hyphens would emit a non-conforming
`scope`. Enforcing/normalizing arbitrary persona names is out of scope (default
path conforms); noted so a future reviewer doesn't re-flag it.

### `09_CHG` in the schema

Phase 3 made CHG a review target (crew parity) and CHG review runs end to end; its
journal carries `layer: "09_CHG"`, which the enum lacks. Add `"09_CHG"` to the
`saga.schema.json` `layer` enum — a one-line framework change (PATCH) that lets a
real CHG journal validate, completing the CHG sanctioning the H-12 finding promised.

### Backward-compatibility

All new `SagaRunState` fields are defaulted, so existing constructors/deserialization
keep working; `_to_run_state` reads them with defaults. The journal gains keys
(additive) — the schema is `additionalProperties: true`, so extra keys never fail.
Existing tests that assert an exact journal key-set or `SagaRunState` shape are
updated.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/src/mcp_server/review/saga_models.py` | `SagaRunState` gains `artifact_id`/`layer`/`iteration`/`transitions` (`:25`) |
| `platforms/hermes/src/mcp_server/review/saga_journal.py` | `_to_run_state` reads the 4 fields; `create_saga_journal` seeds initial transition; `update_run_status` + `set_branch_state` append transitions |
| `platforms/hermes/src/mcp_server/review/saga_orchestrator.py` | initial `SagaRunState(...)` (`:603`) passes `artifact_id`/`iteration` + `layer=normalize_layer(layer or doc_type)[1]` (imports `normalize_layer` alongside the existing `load_playbook` import, `:21`) |
| `framework/governance/saga.schema.json` | add `"09_CHG"` to the `layer` enum (`:35-36`) |
| `tests/conformance/test_saga_lifecycle_parity.py` (or a sibling) | validate a **real** Hermes journal (lifecycle + CHG) against the schema |
| `platforms/hermes/tests/…/test_saga_review_journal.py` | the only shape/roundtrip test constructing `SagaRunState` — inspect; likely no change (keyword ctor, defaulted fields) |
| `framework/VERSION` (→ `0.32.7`) + `platforms/hermes/VERSION` (→ `0.5.1`) + both CHANGELOGs + root CHANGELOG | version + entries |
| `docs/PARITY.md` / `plans/HERMES-BACKLOG.md` (H-12 closed) / `HANDOFF.md` / `DECISIONS.md` (D-0048) | docs |

## Implementation sequence

### Task 1: real-journal conformance test (test-first) — [CODE]

- Add a test that runs a real Hermes saga end to end (mocked executor/build, per the
  Phase-2 integration pattern) for a lifecycle layer, and validates
  `journal_path`'s content against `saga.schema.json` (reuse the hand-rolled subset
  validator `validate()` in `test_saga_lifecycle_parity.py:75` — Python has no stdlib
  JSON-Schema validator; it checks `required`/`type`/`enum`/`pattern` but treats
  `additionalProperties:false` as a no-op, so V3 asserts the **required** transition
  keys + `scope` pattern, and exact `{ts,from,to,scope}` shape is a coding
  convention, not a test guarantee). Confirm it **fails** on `main` (missing
  `artifact_id`/`layer`/`iteration`/`transitions`).

### Task 2: journal conformance — [CODE]

- Add the 4 `SagaRunState` fields; wire `_to_run_state` + `create_saga_journal` +
  `update_run_status` + `set_branch_state` (transitions); populate at construction.
  Re-run: the new test passes; fix any journal-shape test fallout.

### Task 3: `09_CHG` schema + CHG conformance — [CODE]

- Add `"09_CHG"` to `saga.schema.json`; extend the test with a real CHG-review
  journal validating. `bump_version.py 0.32.7` (framework, re-vendors); GATE-SPEC.
  The FSV hard-pin in `test_plugin_release_metadata.py:139`
  (`assertEqual(_plugin_framework_spec_version(), "0.32.6")`) is **auto-rewritten**
  to `"0.32.7"`: `bump_version.py:137,140` invokes `sync-version-refs.sh`, which at
  `:218-221` replaces `"$fw_prev"` → `"$fw_ver"` (sourcing `fw_prev=0.32.6` from
  CLAUDE.md's not-yet-synced prose). No manual edit of line 139 is needed;
  `bump_version.py`'s own "manual step remains" reminder text (`:152-156`) is stale.
  V6 confirms the pin post-bump.

### Task 4: version + docs

- Hermes `0.5.1`; both CHANGELOGs + root; PARITY (saga journals now conform for
  real); close H-12; D-0048; HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | real-journal conformance test on `main` (pre-fix) | **fails** (4 fields missing) — proves it catches H-12 | test validity |
| V2 | same test post-fix: a real lifecycle-layer Hermes journal validates against `saga.schema.json` | green — `artifact_id`/`layer`/`iteration`/`transitions` present + valid | core fix |
| V2b | run the saga with `--layer` **omitted** (default `None`), only `--doc-type` supplied | green — `layer` still enum-valid (derived from `doc_type` via `normalize_layer`) | F1 default-path |
| V3 | transitions replay the state machine (`PREPARED → … → CLOSED`), each `scope` matches `^(run\|branch:[a-z_]+)$` | valid | transitions |
| V4 | a real CHG-review journal (`layer: "09_CHG"`) validates | green (enum extended) | CHG sanction |
| V5 | `python -m pytest platforms/hermes/tests -q` | green (updated shape tests) | no regression |
| V6 | `python -m pytest tests/conformance -q` | green incl. the new real-journal check + the Phase-1 fixture check | no regression |
| V7 | `python tests/chg/spec_gate.py --base main` | pass — VERSION + CHANGELOG present (framework change) | GATE-SPEC |
| V8 | plugin bundle re-vendored; `FRAMEWORK_SPEC_VERSION` pins == `0.32.7` | consistent | bump |

## Docs to update

- [ ] `framework/CHANGELOG.md` / root `CHANGELOG.md` — `0.32.6 → 0.32.7` (schema)
- [ ] `platforms/hermes/CHANGELOG.md` — `[0.5.1]`
- [ ] `docs/PARITY.md` — saga-journal parity now enforced against real output
- [ ] `plans/HERMES-BACKLOG.md` — H-12 closed
- [ ] `plans/DECISIONS.md` — D-0048
- [ ] `plans/HANDOFF.md` — arc progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Adding `SagaRunState` fields breaks a test that asserts exact shape / constructs it positionally | med | fields are defaulted + appended last (keyword construction); V5 catches; update the shape tests |
| R2 | `_to_run_state` roundtrip drops the new fields (load→save loses them) | med | V2/V5 exercise a real end-to-end journal that is written, transitioned, and re-loaded; add the fields to `_to_run_state` |
| R3 | Recording transitions on every `set_branch_state` bloats the journal / changes deterministic outputs a fixture test snapshots | low | additive; the only exact-snapshot is the Phase-1 fixture (hand-authored, unaffected); real-journal test asserts validity not byte-equality |
| R4 | `artifact_id` from `_extract_doc_id` fails `^[A-Z]+-[0-9]{2}$` for a non-standard filename | low | the regex `([A-Z]+-\d+)` captures 1-or-more digits, so `BRD-1` (1-digit) or `BRD-123` (3-digit) filenames would fail the schema pattern. Standard `TYPE-NN` doc filenames (mandated by `ID_NAMING_STANDARDS`) are 2-digit, and the `f"{doc_type.upper()}-00"` fallback is 2-digit, so real corpus docs conform; V2 validates the pattern. A non-standard-named doc is already an ID-naming violation and out of H-12's scope (H-12 does not add a width guard) |
| R5 | `09_CHG` in the enum is rejected by a plugin-side saga test | low | additive enum value; the plugin's fixtures use lifecycle layers; V6 runs the full conformance suite |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | The journal is `asdict(run)` of `SagaRunState` (so its fields ARE the journal keys) | `create_saga_journal` | platforms/hermes/src/mcp_server/review/saga_journal.py:45 |
| 2  | `SagaRunState` lacks `artifact_id`/`layer`/`iteration`/`transitions` | `class SagaRunState` | platforms/hermes/src/mcp_server/review/saga_models.py:25 |
| 3  | `update_run_status` only replaces `status` — no transition is recorded | `update_run_status` | platforms/hermes/src/mcp_server/review/saga_journal.py:66 |
| 4  | `set_branch_state` only updates `branches` — no branch transition recorded | `set_branch_state` | platforms/hermes/src/mcp_server/review/saga_journal.py:75 |
| 5  | `_to_run_state` deserializes a fixed field set (must add the 4) | `_to_run_state` | platforms/hermes/src/mcp_server/review/saga_journal.py:23 |
| 6  | The schema requires `artifact_id`/`layer`/`iteration`/`transitions` | `required` | framework/governance/saga.schema.json:8 |
| 7  | The `layer` enum is `01_BRD..08_IPLAN` (no `09_CHG`) | `08_IPLAN` | framework/governance/saga.schema.json:36 |
| 8  | `transitions` items require `{ts, to, scope}`, scope `^(run\|branch:[a-z_]+)$` | `pattern` | framework/governance/saga.schema.json:93 |
| 9  | `artifact_id` must match `^[A-Z]+-[0-9]{2}$`; `_extract_doc_id`'s regex is `([A-Z]+-\d+)` (conforms for 2-digit `TYPE-NN` filenames) | `_DOC_ID_RE` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:66 |
| 10 | The initial `SagaRunState(...)` is built here (add the scalar fields) | `SagaRunState(` | platforms/hermes/src/mcp_server/review/saga_orchestrator.py:603 |
| 11 | `_utc_now_iso()` is the timestamp helper for `ts` | `_utc_now_iso` | platforms/hermes/src/mcp_server/review/saga_models.py:8 |
| 12 | The Phase-1 conformance guard validates hand-authored fixtures (not real journals) | `SagaJournalFixtureParity` | tests/conformance/test_saga_lifecycle_parity.py:152 |
| 13 | Current framework spec is `0.32.6` (→ `0.32.7` PATCH); Hermes `0.5.0` (→ `0.5.1`) | `0.32.6` | framework/VERSION:1 |
| 14 | Most recent decision is D-0047 → next free is D-0048 | `D-0047` | plans/DECISIONS.md:13 |
| 15 | `--layer` is optional (`default=None`); `--doc-type` is required — so `layer` must derive from `doc_type` | `"--layer"` | platforms/hermes/src/mcp_server/cli/main.py:89 |
| 16 | `normalize_layer(...)` maps doc-type OR dir form → enum-form layer dir (the derivation helper) | `normalize_layer` | platforms/hermes/src/mcp_server/review/playbook_loader.py:61 |
| 17 | The FSV hard-pin is auto-synced by `sync-version-refs.sh` (invoked by `bump_version.py`), not a manual step | `replace_in_file` | scripts/sync-version-refs.sh:218 |
| 18 | `bump_version.py` runs `sync-version-refs.sh` in-process | `subprocess.run` | tools/bump_version.py:140 |

## Review log

### Pass 1 — 2026-07-03T21:44:27-04:00 — self-review

- **Design fully grounded empirically:** the real-journal gap (4 missing fields, no
  `transitions` recorded) was reproduced by running `run_project_review_build_saga`
  end-to-end and dumping `journal_path`; the fix maps 1:1 to the four gaps.
- **Two schema-precision clarifications folded** (see Transitions §): entries are
  `additionalProperties:false` → exactly `{ts,from,to,scope}`; a transition is
  appended only on a *successful* change (after `can_transition`, never on
  `_safe_transition`'s swallowed retry).
- **Version streams:** framework PATCH (schema) via `bump_version.py` (fans FSV pins
  - re-vendor); Hermes PATCH manual — both independent per `docs/PROJECT.md` §2.
- Citation gate: 14 rows resolve (`--fix` re-pointed 2 drifted lines).

### Pass 2 — 2026-07-03 — independent (fresh-context code-reviewer)

An adversarial fresh-context reviewer verified all citations against source and
built the real journal shape end-to-end against the schema. Verdict: 2 load-bearing
findings; 1 confirmed + fixed, 1 refuted with evidence; 4 minors folded.

- **F1 (load-bearing, CONFIRMED → fixed).** The draft set `layer=layer` from the
  saga call. But `--layer` is optional (`default=None`, `cli/main.py:89`;
  `tool_registry.py:1549`) and free-text, while `--doc-type` is required. A test
  passing an explicit valid `layer` would go green while the real default invocation
  (layer omitted) emits `layer: null` → schema failure — re-creating the exact
  fixture-masks-reality trap H-12 kills. **Fix:** derive `layer` from the required
  `doc_type` via the existing `normalize_layer(layer or doc_type)[1]` helper
  (`playbook_loader.py:61`); added the "Deriving `layer` robustly" design section,
  updated Scope/table/file-structure/ledger (rows 15–16), and added **V2b** (run
  with `--layer` omitted → still enum-valid).
- **F2 (load-bearing, REFUTED with evidence).** Reviewer claimed the FSV hard-pin
  (`test_plugin_release_metadata.py:139`) needs a manual bump or V6 fails, citing
  `bump_version.py`'s reminder text. Refuted: `bump_version.py:137,140` invokes
  `sync-version-refs.sh`, which at `:218-221` auto-rewrites that literal
  (`"$fw_prev"`→`"$fw_ver"`). The reviewer inspected `bump_version.py`'s own code +
  its (stale) reminder but missed the subprocess call. Documented the auto-handling
  in Task 3 + ledger rows 17–18 so it isn't re-flagged.
- **Minor 3 (fixed).** `_DOC_ID_RE` is `([A-Z]+-\d+)` (1-or-more digits), not
  `\d{2}` — `BRD-1`/`BRD-123` would fail the `^[A-Z]+-[0-9]{2}$` pattern. Corpus
  docs are standard 2-digit `TYPE-NN` so conform; reworded design table + R4 to state
  this honestly (no width guard added — non-standard filenames are ID-naming
  violations, out of scope).
- **Minor 4 (fixed).** Citation drift: ledger row 5 `_to_run_state` `:25`→`:23`;
  row 8 scope `:100`→`:93`.
- **Minor 5 (fixed).** "stdlib validator" → hand-rolled subset `validate()`
  (`test_saga_lifecycle_parity.py:75`) that ignores bool `additionalProperties:false`;
  clarified V3 checks required keys + `scope` pattern, exact `{ts,from,to,scope}` is a
  coding convention not a test guarantee (Task 1).
- **Minor 6 (fixed).** Added the `branch:<persona>` scope caveat: conforms for the
  `[a-z_]+` framework crews + Hermes extras; arbitrary `--personas` out of scope.
- **Reviewer-confirmed correct, no change:** transitions accumulate correctly across
  main-thread sequential `set_branch_state`/`update_run_status` calls; `_safe_transition`
  idempotent retry raises before the append (no corruption); `09_CHG` enum add is
  additive and breaks no plugin test (`saga_driver.py:117` already carries it;
  `test_registry.py:33` asserts the 8-layer lifecycle registry, not the saga enum);
  framework PATCH + Hermes PATCH defensible; `branches`/`personas_requested`/
  `review_run_id` sub-schemas satisfied. Rows 1–4, 6–7, 10–14 resolve exactly.

### Pass 3 — 2026-07-03 — self-review (re-validate Pass-2 patches)

Re-validated that the Pass-2 F1 fix introduced no new inconsistency, empirically:
`normalize_layer(layer or doc_type)[1]` returns the correct enum-form dir for every
path — `01_BRD` (explicit dir form), `01_BRD` (doc-type `brd`), `09_CHG` (doc-type
`chg`, the default `--layer`-omitted path), `08_IPLAN` (`iplan`) — and
`normalize_layer` is a module-level importable symbol (`playbook_loader.py:61`). The
CHG case resolves to `09_CHG`, consistent with the schema-enum addition (Task 3), so
V2b + V4 align. No new substantive gaps.

**Result:** ready

## Implementation record — 2026-07-03

Implemented on `fix/hermes-saga-journal-conformance-h12` after the plan PR (#236)
merged. All 8 V-checks green:

- **Task 2 (journal conformance):** added `artifact_id`/`layer`/`iteration`/
  `transitions` to `SagaRunState` (defaulted); `saga_journal.py` gains
  `_transition_entry` helper + seeds/records schema-shaped transitions in
  `create_saga_journal`/`update_run_status`/`set_branch_state` (branch entry only on
  status change); `_to_run_state` reads the 4 fields. Orchestrator derives
  `layer=normalize_layer(layer or doc_type)[1]` + `artifact_id=doc_id` + `iteration=1`.
- **Task 1 (test-first):** `SagaRealJournalConformance` in
  `test_saga_lifecycle_parity.py` drives a real journal through the actual functions
  (real `_extract_doc_id`/`normalize_layer`) for a lifecycle layer, the
  `--layer`-omitted path (V2b), and a CHG run (V4). **V1 confirmed:** reverting the
  source fixes makes the class fail (`SagaRunState` has no `artifact_id`).
- **Task 3 (`09_CHG` + bump):** added `"09_CHG"` to `saga.schema.json`;
  `bump_version.py 0.32.7` re-vendored the plugin bundle + synced FSV pins + **auto-
  rewrote the FSV hard-pin** to `0.32.7` (confirming F2's refutation — no manual
  edit). Hermes `VERSION → 0.5.1` (manual, platform-independent stream).
- **Task 4 (docs):** root `CHANGELOG.md` (framework-spec + Hermes entry), Hermes
  `CHANGELOG.md`, `DECISIONS.md` (D-0048), `HERMES-BACKLOG.md` (H-12 CLOSED + table
  row 3b), `PARITY.md` (real-journal conformance), `HANDOFF.md`.
- **Verification:** V5 = 17 Hermes saga tests green; V6 = 160 conformance + 644
  subtests green; V8 = FSV pins all `0.32.7`, vendored schema carries `09_CHG`.
  `test_saga_review_journal.py` needed no change (as predicted).
