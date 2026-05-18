# P1-T5 Plan — Shared Conformance Suite under `tests/conformance/`

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T5                                      |
| Depends on | P1-T2/T3/T4 (`framework/` populated)       |
| Status     | PLANNED — 2026-05-18T20:50:00Z             |
| Feeds      | Phase 4 (platform conformance), P1-T6      |

## Objective

Create the shared conformance suite — the runnable contract that defines what
it means to conform to the `framework/` spec. P1-T5 delivers the **framework
self-consistency** tests (runnable now, green against the current `framework/`)
and the documented **platform-conformance contract** that Phase 4 fills in per
platform.

## Scope

**In:** `tests/conformance/` — Python test modules covering registry, layers,
governance, and spec hygiene; a spec-loading helper; a README documenting how
to run the suite and the platform-conformance contract.
**Out:** platform-conformance *test implementations* (no platform exists yet —
Phase 4); `framework/VERSION` (P1-T6); CI wiring (Phase 4).

## Approach

### Test framework — D-0008 (recommended)

Use Python **`unittest`** (standard library) + **`pyyaml`** (already present).
**No `pytest` dependency** — `pytest` is not installed, and a zero-install,
stdlib-only suite is what an engine-agnostic conformance contract needs:
`python -m unittest discover` runs it anywhere with Python 3.11+. `unittest`
test classes are also discoverable by `pytest` if a platform prefers it
(by construction; not separately verified here since `pytest` is absent).

### Files

| File | Purpose |
|------|---------|
| `tests/conformance/README.md` | what conformance is, how to run, the platform contract |
| `tests/conformance/__init__.py` | package marker |
| `tests/conformance/_spec.py` | helper: locate `framework/`, load `LAYER_REGISTRY.yaml`, enumerate layer files |
| `tests/conformance/test_registry.py` | registry self-consistency + registry↔filesystem |
| `tests/conformance/test_layers.py` | layer templates, index templates, metadata vs registry |
| `tests/conformance/test_governance.py` | governance + CHG files present and parseable |
| `tests/conformance/test_spec_hygiene.py` | no engine tokens / stale version strings in `framework/` |
| `tests/conformance/requirements.txt` | `pyyaml` (the only external dep) |

### Test inventory

**`test_registry.py`** — registry parses; has `layers`/`metadata`/`layer_groups`/
`c4_mapping`/`id_patterns`; exactly 8 layers; `number`s are `1..8` dense;
`metadata.total_layers` == layer count; each layer has all required keys;
`error_prefix` == `artifact`; `downstream` chain correct (layer n → artifact of
n+1; layer 8 → `CODE`); `required_tags` cumulative & monotonic (layer n ==
layer n-1's tags + artifact of n-1 lowercased; layer 1 == `[]`); `can_reference`
== uppercased `required_tags`; every `folder`+`template` resolves to a real file
under `framework/`; `id_patterns` compile as regexes; `c4_mapping` artifacts all
exist in `layers` (or are `CODE`); every layer number appears in exactly one
`layer_groups` entry.

**`test_layers.py`** — all 8 layer dirs exist with `{TYPE}-TEMPLATE.yaml` +
`README.md` + `{TYPE}-00_index.TEMPLATE.{md,yaml}`; each template parses as
YAML; template `metadata.layer` == registry layer number; `metadata.document_type`
present.

**`test_governance.py`** — the 5 governance docs and the `chg/` tree (README,
`CHG-TEMPLATE.yaml`, `CHG-00_index.TEMPLATE.md`, 7 gates, 2 companion templates)
are present; `CHG-TEMPLATE.yaml` parses.

**`test_spec_hygiene.py`** — scan every file under `framework/` (only) for
engine tokens with **precise** patterns: `hermes`, `ucx_`, `.claude/`,
`\bmcp\b`, `mermaid-gen`, `charts-flow`, and `sdd_(validate|create|
score_validate|consistency|preflight|next_action|review|remediate)` — assert
none. `sdd_layer`/`sdd_layers` are agnostic and deliberately NOT matched. Also
assert no stale version strings (`SDD v3`, `v3.\d`, `framework_version`).

### Platform-conformance contract

`tests/conformance/README.md` documents the contract a platform must satisfy in
Phase 4 (its generated artifacts validate against the templates and registry;
it declares a `framework_spec_version`). No platform test code in P1-T5 — a
documented contract, not pretend stubs.

## Step sequence

1. Create `tests/conformance/` with `_spec.py`, `__init__.py`, the 4 test
   modules, `requirements.txt`, `README.md`.
2. **Verify** (see below).
3. **Land:** record D-0008; commit; tick P1-T5; update `CHANGELOG.md`,
   `HANDOFF.md`.

## Verification

- `python3 -m unittest discover -s tests/conformance -v` → all tests pass.
- The run reports a non-trivial test count (suite actually asserts — a green
  empty suite is a failure of this task).
- If the suite surfaces a genuine `framework/` defect, that is a real finding:
  fix `framework/` (or record it) and re-run — do not weaken a test to pass.
- `python3 -c "import yaml"` confirms the one dependency is available.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | `pytest` absent → suite unrunnable | use stdlib `unittest`; zero external test dep (D-0008) |
| R2 | Hygiene patterns mis-flag agnostic `sdd_layer` (P1-T3 G1 repeat) | verb-specific `sdd_(validate\|create\|…)` pattern; `sdd_layer` not matched |
| R3 | Hygiene scan flags the test files themselves (they contain the token literals) | scan scope is `framework/` only, never `tests/` |
| R4 | Suite finds a real `framework/` defect on first run | treat as a finding — fix `framework/`, never weaken the test |

## Review log

> ≥2 passes required before implementation. Each pass also cross-checks the
> Verification section against the approach (no false positive / false negative).

### Pass 1 — 2026-05-18T20:55:00Z

- **G1.** `pytest` is not installed; an engine-agnostic conformance suite must
  be runnable with no install. → Approach fixed to stdlib `unittest` +
  `pyyaml`; recorded as decision D-0008.
- **G2.** A naive engine-token scan would mis-flag the agnostic `sdd_layer` /
  `sdd_layers` registry fields (the exact P1-T3 G1 false positive). → Hygiene
  patterns are verb-specific (`sdd_(validate|create|…)`); R2.
- **G3.** The hygiene test files contain the engine-token strings as literal
  patterns; scanning `tests/` would flag the suite itself. → Scan scope pinned
  to `framework/`; R3.
- **G4.** Platform-conformance tests cannot run (no platform yet). → P1-T5
  scope is framework self-consistency + a *documented* contract; platform test
  code is Phase 4. Stated in Scope and the README deliverable.

### Pass 2 — 2026-05-18T21:00:00Z

Cross-checked the Verification section against the approach:

- **Verification audit.** "All tests pass" alone is insufficient — a green
  suite that asserts nothing would pass vacuously. → Added the explicit
  non-trivial-test-count check and the R4 rule (a defect found = fix
  `framework/`, never weaken the test). No false-positive risk in the
  verification itself (it runs the suite, not a grep).
- **G5 (noted).** The suite may legitimately fail on first run if `framework/`
  has a real inconsistency (e.g. a template `metadata.layer` mismatch). That
  is the suite working. Implementation will fix the `framework/` source and
  re-run; if a fix is non-trivial it is recorded as a finding, not silently
  patched. Captured in R4.
- **G6 (confirmed).** Suite location is repo-root `tests/conformance/` (per
  ROADMAP), not `framework/tests/` — the suite is shared infrastructure that
  *tests* `framework/`, not part of the spec.
- No new blockers. Ready to implement on approval.
