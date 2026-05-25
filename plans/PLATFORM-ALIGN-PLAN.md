# PLATFORM-ALIGN Plan — vendor the doc-linter + migrate Hermes IDs to the framework hash form

| Field      | Value                          |
|------------|--------------------------------|
| Task       | PLATFORM-ALIGN                 |
| Depends on | DOC-CHECK (PRs #17/#18 merged); framework spec `0.7.0`; the 4-segment element-ID standard (`LAYER_REGISTRY.yaml` `id_patterns`) |
| Status     | COMPLETE (pending PR-3 merge) — Part A merged (PR #19); B1+B2 merged (PR #20, Hermes `0.2.0`); B3 full-removal implemented (PR-3, branch `claude/hermes-legacy-layer-removal`, Hermes `0.3.0`) per user decision |
| Feeds      | a consumer-runnable doc-linter on both platforms (Part A); Hermes element-IDs aligned to the framework hash form + legacy-layer prompts handled (Part B) |

## Objective

Two platform follow-ups flagged after DOC-CHECK:

- **Part A (#1) — vendor `sdd_doc_lint` into both platforms** so the plugin's
  `on_author` hook (and a Hermes-side equivalent) can run the deterministic
  structural check at consumer runtime, not just best-effort.
- **Part B (#2) — migrate Hermes element-IDs to the framework 4-segment hash
  form** (`TYPE.NN.SS.xxxx`), across the 8-layer prompts *and* the runtime
  regexes + their tests, and **handle the off-model legacy-layer prompts**
  (SYS/REQ/CTR/TSPEC).

Both are **platform/tooling changes — no `framework/` edit, no GATE-SPEC bump.**
Part B changes Hermes runtime behavior ⇒ a Hermes platform version bump.

## Current state (grounding)

- The canonical linter is `tools/sdd_doc_lint/` (used by the conformance/CI side).
  It resolves the registry via `REPO_ROOT = parents[2]` — a **hardcoded relative
  path** that only works from that location.
- The plugin hook runs the linter **best-effort** (`python3 -c "import sdd_doc_lint"`);
  in a real consumer it is almost never importable → hook is nudge-only in practice.
- **Three element-ID schemes** coexist in Hermes:
  1. framework canonical **4-segment** `TYPE.NN.SS.xxxx` (e.g. `EARS.01.03.c4d8`);
  2. Hermes **runtime 3-segment** `TYPE.NN.xxxx` — `validation/cross_section.py:18-19`
     (`_ELEMENT_ID_RE`, `_ELEMENT_ID_INLINE_RE`) and `remediation/runner.py:640`
     (`_ID_PATTERN`), with tests in `tests/unit/test_cross_section.py`,
     `tests/unit/test_remediation_runner.py`;
  3. legacy **type-code** `TYPE.NN.<CODE>.<seq>` (UB/EV/ST/OP/UW/CX/FR…) in the
     prompts (`UCC/UCR/UCRem_PROMPT_{EARS,BDD,…}` + the legacy-layer prompts).
- **12 legacy-layer prompt files** (SYS/REQ/CTR/TSPEC × creation/review/remediation)
  for layers absent from the 8-layer framework. They have **runtime coupling**
  (e.g. `validation/runner.py:334` has a `ctr` branch; prompts load per-layer
  from `templates/{creation,review,remediation}/`).

## Scope

**In:** Part A (vendor linter + make it location-independent + drift guard +
wire the hook to the vendored copy + Hermes-side entry). Part B (prompt IDs →
4-seg hash; runtime regex 3-seg → 4-seg + tests; legacy-layer prompts handled).

**Out:** changing the framework spec or the registry `id_patterns` (already
correct at 4-segment); the finding-ID schemes (`P0-hash`, `ACT-hash` in
`reporting/contracts.py` — those are finding/action IDs, not element IDs);
re-implementing the LLM audits.

## Part A — vendor the linter into both platforms

### Decisions (recommendations)

- **A-D1 — canonical source.** Keep `tools/sdd_doc_lint/` canonical (conformance
  - CI use it). Vendor **byte-identical** copies into
  `platforms/claude-code-plugin/sdd_doc_lint/` and
  `platforms/hermes/sdd_doc_lint/` (or a `tools/`/`scripts/` subdir within each).
- **A-D2 — location independence (prerequisite for byte-identical copies).**
  Refactor registry resolution: instead of `parents[2]`, **search upward from the
  CWD (and from the module file) for `framework/registry/LAYER_REGISTRY.yaml`**,
  with an optional `--registry PATH` / `SDD_REGISTRY` override. Then the same code
  runs unchanged from any vendored location (it finds the consumer's `framework/`).
- **A-D3 — drift guard.** A conformance test asserts the two vendored copies are
  **byte-identical** to the canonical `tools/sdd_doc_lint/` (`__init__.py`,
  `__main__.py`) — prevents divergence (the D-0013 single-source ethos applied to
  a deliberate vendoring). A `make`/script target re-syncs them.
- **A-D4 — wiring.** The plugin hook calls the vendored copy via
  `PYTHONPATH="${CLAUDE_PLUGIN_ROOT}"` (so `import sdd_doc_lint` resolves
  out-of-box). Hermes exposes it (CLI entry or a thin `validation` call).

### Steps

1. Refactor the canonical linter's registry resolution to upward-search + override
   (A-D2); re-run its unit tests + the fixtures.
2. Vendor byte-identical copies into both platforms; add the drift-guard
   conformance test (A-D3).
3. Update the plugin hook to set `PYTHONPATH` to the vendored copy (drop the
   best-effort import guard → deterministic findings now reliably available);
   keep advisory/exit-0.
4. Hermes: add a CLI/use entry for the vendored linter; note it in the README.

## Part B — Hermes element-IDs → framework 4-segment hash

### B1 — prompts (8-layer)

Migrate type-code element-ID examples + the `UB/EV/ST/OP/UW/CX` legends in the
8-layer prompts (`UCC/UCR/UCRem_PROMPT_{EARS,BDD,...}`, `UCC_OUTPUT_SCHEMA`) to the
4-segment hash form `TYPE.NN.SS.xxxx` (e.g. `EARS.01.EV.05` → `EARS.01.03.c4d8`).
Remove the type-code legend (the hash form has no per-pattern code).

### B2 — runtime regexes + tests

Change the Hermes element-ID validators from 3-segment to 4-segment:

- `validation/cross_section.py:18-19` `^[A-Z]{2,8}\.\d{2,}\.[0-9a-f]{4,8}$`
  → `^[A-Z]{2,8}\.\d{2,}\.\d{2,}\.[0-9a-f]{4,8}$`;
- `remediation/runner.py:640` `_ID_PATTERN` likewise;
- update `tests/unit/test_cross_section.py` + `tests/unit/test_remediation_runner.py`
  fixtures/assertions to the 4-segment form;
- run the full Hermes pytest suite — it must stay green (this is the risk gate).

### B3 — legacy-layer prompts (SYS/REQ/CTR/TSPEC) — **remove** (B-D1 resolved)

**Decision: remove.** Delete the 12 off-model prompt files (SYS/REQ/CTR/TSPEC ×
creation/review/remediation) **and** their runtime coupling — they are not part of
the 8-layer framework (the framework absorbed SYS→SPEC, REQ→EARS, CTR→SPEC,
TSPEC→TDD; the plugin already retired them). Method:

1. Map the coupling first: the `validation/runner.py` `ctr` branch + any
   SYS/REQ/CTR/TSPEC arms in the per-layer prompt loader / `tool_registry` /
   layer-name allowlists.
2. Remove the prompt files + the dead runtime arms together, so the layer→prompt
   loader only resolves the 8 framework layers.
3. Update/trim any Hermes tests that assert the legacy layers.
4. If the coupling check reveals a legacy layer still backs a *currently
   advertised* Hermes capability (not expected), stop and escalate rather than
   break it — but the default is full removal.

### Versioning

Part B changes Hermes runtime behavior + removes the off-model legacy-layer
prompts ⇒ **bump `platforms/hermes/VERSION` (minor)** + a Hermes CHANGELOG
`Removed`/`Changed` entry. Minor (not major): the removed layers were never part
of the conformant 8-layer surface, so no 8-layer consumer capability is lost; the
4-segment ID move aligns Hermes to the framework it already declares conformance
to. (Escalate to major only if step B3.4 finds an advertised dependency.) No
framework/spec change.

## Sequencing

- **PR-1 = Part A** (vendor linter) — independent, lower-risk, unblocks the
  hook's deterministic check.
- **PR-2 = Part B** (Hermes IDs + legacy prompts) — cut after PR-1; the bigger,
  runtime+test-touching change with the B-D1 removal decision.

## Verification

- Part A: canonical + both vendored copies pass `python -m sdd_doc_lint` on the
  fixtures from each location; drift guard green; conformance suite green; the
  plugin hook (manual test) now emits deterministic findings, still exit 0.
- Part B: full Hermes pytest suite green after the regex/test changes; no
  type-code element IDs remain in the 8-layer prompts (grep clean); no 3-segment
  element-ID regex remains in `src/`; legacy-layer prompts removed/deprecated with
  no broken layer→prompt loads; `validate`/`remediate` smoke run on a 4-seg doc.
- `pre-commit run --all-files` clean (Hermes vendored content excluded from
  markdownlint as today).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Vendoring duplicates the linter → drift | Byte-identical copies + a conformance drift guard (A-D3) + a re-sync script; canonical stays `tools/`. |
| R2 | Registry not found from a vendored location | Upward-search + `--registry`/env override (A-D2); test from each location. |
| R3 | 3→4-segment regex change breaks Hermes tests/behavior | Update tests in lockstep; run the full pytest suite as the gate; the 4-seg form is a superset-stricter match, so audit any doc fixtures using 3-seg IDs. |
| R4 | Removing legacy-layer prompts breaks runtime (CTR branch, loader) | B3 investigates coupling first; remove only if safe, else deprecate-in-place + track (B-D1). |
| R5 | Hermes version/semver | Bump `platforms/hermes/VERSION` + CHANGELOG; classify minor vs major by whether prompt removal is breaking for consumers. |
| R6 | Scope creep (Part B touching the whole prompt corpus) | Limit B1 to element-ID forms + the type-code legend; do not rewrite prompt prose. |

## Review log

> ≥2 passes before implementation (CLAUDE.md).

### Pass 1 — 2026-05-25

- **Vendoring needs location-independence first.** Byte-identical copies are
  impossible while the linter hardcodes `parents[2]` for the registry — added
  A-D2 (upward-search + override) as a prerequisite, enabling A-D3's identical-copy
  drift guard.
- **Three ID schemes, not two.** Surfaced the Hermes runtime's *3-segment* regex
  as distinct from both the legacy type-code prompts and the framework 4-segment
  form; Part B must fix the runtime regex + tests (B2), not just prompt examples.
- **Legacy prompts have runtime coupling.** `validation/runner.py` has a `ctr`
  branch and prompts load per-layer — so B3 is "investigate then remove-or-deprecate,"
  not a blind file delete (R4, B-D1).
- **Split the PRs.** Part A (low-risk) lands before Part B (runtime+tests).

### Pass 2 — 2026-05-25

- **Don't touch finding-ID schemes.** Scoped out `P0-hash`/`ACT-hash` in
  `reporting/contracts.py` — those are finding/action IDs, not element IDs;
  conflating them would break reporting. Added to Scope-Out.
- **Hermes semver.** Part B is runtime-behavior-changing + removes prompt files ⇒
  a Hermes VERSION bump (R5); framework spec untouched (no GATE-SPEC).
- **Prose-rewrite guard.** B1 is strictly element-ID-form + legend; the EARS
  pattern prose was already aligned in the prior Hermes PR, so B1 won't re-touch it
  (R6). No change.
- No further findings — implementable pending approval.

### Pass 3 — 2026-05-25 (decisions firmed for implementation)

- **All parts in scope, no deferrals.** Per the go-ahead: Part A (vendor +
  location-independence + drift guard + hook wiring), Part B1 (prompt IDs), B2
  (runtime regex 3→4 segment + tests), and B3 (**remove** legacy-layer prompts +
  coupling) are all in scope.
- **B-D1 resolved = remove** (was "remove-or-deprecate"). Default is full removal
  of the 12 SYS/REQ/CTR/TSPEC prompts + their runtime arms; escalate only if a
  legacy layer is found to back a currently-advertised capability.
- **Hermes semver fixed = minor** + a `Removed`/`Changed` CHANGELOG entry
  (rationale recorded under Versioning).
- **Sequencing unchanged:** PR-1 = Part A, PR-2 = Part B (cut after A merges).
- No further findings — proceeding to implement Part A.

## Implementation log

### Part A — 2026-05-25 (PR-1, branch `claude/platform-align`)

- Made `tools/sdd_doc_lint` **location-independent** (upward-search for
  `framework/registry/` + `$SDD_REGISTRY`/`--registry`; CLI exits 2 when the
  registry is unavailable). Vendored **byte-identical** copies into
  `platforms/claude-code-plugin/sdd_doc_lint/` and `platforms/hermes/sdd_doc_lint/`;
  `tools/sdd_doc_lint/sync-vendored.sh` re-syncs them; a conformance guard
  (`tests/conformance/platforms/test_doc_lint_vendoring.py`) enforces the match
  (suite **49 → 50**). The plugin `on_author` hook now derives its plugin root and
  runs the vendored linter on `PYTHONPATH` — deterministic findings are reliable
  (not best-effort), still advisory/exit-0, and skip silently with no `framework/`.
  Both platform READMEs document the vendoring. Verified: linter tests + fixtures
  pass from canonical and vendored locations; registry-unavailable → exit 2 (clean,
  no traceback); hook end-to-end emits nudge + findings; `pre-commit` clean.
- **Next:** Part B (B1 prompt IDs, B2 runtime regex 3→4 + tests, B3 remove
  legacy-layer prompts + coupling, Hermes VERSION bump) — PR-2 after PR-1 merges.

### Part B1 + B2 — 2026-05-25 (PR-2, branch `claude/platform-align-b`)

- **B2 (runtime):** `validation/cross_section.py` (`_ELEMENT_ID_RE`,
  `_ELEMENT_ID_INLINE_RE`) + `remediation/runner.py` (`_ID_PATTERN`) changed from
  3-segment `TYPE.NN.xxxx` → 4-segment `TYPE.NN.SS.xxxx`; the 12 three-segment ID
  literals in `test_cross_section.py`/`test_tdd_rules.py` (+ one docstring)
  migrated. Local suite **383 passed** (mcp-gated files excluded; CI runs them).
- **B1 (prompts):** EARS/BDD creation+remediation prompts' type-code IDs
  (`EARS.NN.<CODE>.<seq>`, `PRD.NN.US.NN`, 3-seg refs) → 4-segment hash; rewrote
  the `UCC_PROMPT_EARS` ID-convention legend. Hermes `VERSION 0.1.0 → 0.2.0` +
  CHANGELOG. Conformance **50**; `pre-commit` clean.

### B3 — ESCALATED (not implemented)

The coupling check (B3.4) found the legacy layers are **not orphan files** but an
**intentional, documented "legacy compatibility" surface**:
`src/mcp_server/skills/registry.py` `LAYER_PREFIXES` lists `sys/req/ctr/tspec/tasks`
with the comment *"plus legacy compatibility prefixes"*; `skills/persona_mappings.yaml`
maps them (create/review/remediation); several persona docs + `skills/README.md`
describe them. That coupling is covered only by **mcp-gated tests** (not runnable
locally). Per B3.4 ("if a legacy layer still backs a currently-advertised
capability, stop and escalate"), removal is **paused for an explicit decision** —
full removal would tear out a deliberate compat feature and is CI-only verifiable.
Options surfaced to the user: full-remove / deprecate-in-place / leave.

**Resolution: full-remove (user decision).** PR-3 (`claude/hermes-legacy-layer-removal`,
Hermes `0.2.0 → 0.3.0`) removed the **operative** compat surface: 12 prompt
templates; `registry.py` `LAYER_PREFIXES` sys/req/ctr/tspec (kept `tasks`);
`persona_mappings.yaml` creation+review entries; the `ctr` branch in
`validation/runner.py`; the `skills/README.md` mention; the legacy-layer tests in
`test_validation_runner.py` (dropped/trimmed). Local suite **382**; conformance
**50**; the registry alias self-consistency test stays green (count derived from
`LAYER_PREFIXES`); the mcp-gated tests carry no legacy-layer assertion (CI gate).
**Deliberately retained:** vendored persona-profile `doc_types`/allocation
mentions + `agent-skills/` historical notes ("cut from v3"/"deprecated") — these
are descriptive (not the operative router) and the history is accurate; a
percentage-table rewrite of 10 vendored persona docs was out of proportion.
`tasks` (IPLAN rename-alias) kept by design.
