# TRACE-RES-FIXUP-001 Implementation Plan

> Follow-up to NECESSARY-UPSTREAM-001 — two fixes uncovered when running the
> first TDD cascade against the existing url-shortener corpus.

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | TRACE-RES-FIXUP-001                         |
| Type           | bugfix (lint rule semantics + corpus regen) |
| Status         | DRAFT — 2026-06-10T13:30:00Z                |
| Depends on     | NECESSARY-UPSTREAM-001 (merged PR #121); TDD-RT-001 cascade verification |
| Blocks         | TDD-RT-001 live cascade verification; future per-layer cascades against pre-NECESSARY-UPSTREAM-001 corpora |
| Version impact | Framework PATCH (TBD); plugin PATCH (TBD) — both are bugfix scope |

## Problem statement

The TDD-RT-001 cascade aborted at Phase 0 lint-smoke with 107 `TRACE-RES-001`
errors. Diagnosis surfaced **two distinct bugs**:

### Bug 1 — TRACE-RES-001 fires on downstream tags (lint rule bug)

The TRACE-RES-001 rule (NECESSARY-UPSTREAM-001 Task 4b) checks every emitted
`@<layer>: <ID>` tag for on-disk resolution. But the necessary-upstream
contract is about **upstream** lineage; downstream pointers like
`@tdd: TDD-01` emitted from SPEC-01 are informational forward references
that:

- May not exist yet during cascade (TDD-01 is generated AFTER SPEC-01)
- Are not part of the "necessary upstream" contract being enforced
- Are tooling pointers, not trace-lineage citations

Example (from the failed TDD-RT-001 cascade output):

```
examples/url-shortener/docs/06_SPEC/SPEC-01.md:295:
  [ERROR TRACE-RES-001] trace tag '@tdd: TDD-01' references unknown document
  (no corpus member has doc_id 'TDD-01')
```

SPEC-01 line 295 reads: `TDD document: @tdd: TDD-01` — explicitly a
downstream pointer. SPEC's `required_tags=[ears, bdd, adr]` does NOT include
TDD; the tag is informational, and the cascade is about to generate TDD-01.
The rule should not block here.

### Bug 2 — Pre-NECESSARY-UPSTREAM-001 corpora carry orphan @prd cumulative-trace tags

Existing url-shortener artifacts (BRD-01, EARS-01, BDD-01, ADR-01, SPEC-01)
were generated under the OLD cumulative-trace contract. They emit `@prd:`
tags (cumulative lineage) pointing at element IDs in a PRD-01.md that
never existed in the example corpus (the example was generated with the
PRD layer skipped or with no PRD layer authored).

Under the OLD lint, presence-only TAG01 didn't catch the orphan. Under the
NEW TRACE-RES-001 rule, every emitted upstream tag must resolve — these
orphan @prd tags fire.

Example (from cascade output):

```
examples/url-shortener/docs/05_ADR/ADR-01.md:321:
  [ERROR TRACE-RES-001] trace tag '@prd: PRD.01.13.7760' unresolvable
  (host document missing; expected host 'PRD-01')
```

ADR-01 line 321 is a cumulative-trace header line citing 6 `@prd:` element
IDs, all in a PRD-01.md that doesn't exist. Same pattern repeats across
BRD-01, EARS-01, BDD-01, SPEC-01.

This is corpus drift — the example pre-dates the new contract — and it's
**correctly diagnosed** by TRACE-RES-001 (the rule is doing its job).
The fix is to regenerate the corpus, not weaken the rule.

The NECESSARY-UPSTREAM-001 PR's "backwards compatibility" claim
(*"existing url-shortener artifacts remain valid under the new contract
(their declared tags still resolve)"*) was **wrong** for this corpus —
Pass 4 cross-check verified the new rule against `tools/sdd_doc_lint/fixtures/`
but not against `examples/url-shortener/docs/`. The check should have been
extended to the example corpus during Pass 4.

## Temporary bypass already in place

To unblock TDD-RT-001 cascade verification:

- `SDD_LINT_SKIP_TRACE_RES=1` env var added to `_check_trace_resolution` —
  disables the rule entirely when set. Used by the TDD-RT-001 cascade run
  to allow the cascade to proceed past Phase 0 lint-smoke and surface
  any **other** errors in the TDD-layer generation.
- Documented inline in the function's docstring with a back-reference to
  this plan.
- NOT to be relied on in production CI — purely a migration bridge until
  this plan ships.

## Fixes

### Fix 1 — Downstream-tag skip in TRACE-RES-001 (lint rule)

Modify `_check_trace_resolution` so that for each artifact being linted:

1. Derive the artifact's own layer-number from frontmatter `artifact_type`
   (or doc_id prefix as fallback).
2. For each emitted `@<layer>: <ID>` tag, derive the tag's layer-number
   from the layer prefix (e.g., `@tdd` → 7).
3. **Skip** the resolution check if `tag_layer_number > artifact_layer_number`
   (downstream pointer) OR `tag_layer_number == artifact_layer_number`
   (self-tag).
4. Keep the existing checks for upstream tags and same-tag self-loops.

Test additions (`tests/unit/test_sdd_doc_lint_trace_resolution.py`):

- New case: SPEC-01 emits `@tdd: TDD-01` (forward pointer) where TDD-01
  doesn't exist in corpus → no TRACE-RES-001 finding (downstream-skip).
- New case: SPEC-01 emits `@spec: SPEC-01` (self-tag) → no finding
  (same-layer self-tag).
- Existing cases (missing-doc, unknown-element, index-doc-skip) continue
  to pass.

### Fix 2 — Regenerate url-shortener example corpus

Once Fix 1 lands and the harness `SDD_LINT_SKIP_TRACE_RES` bypass can be
removed:

1. Run cascade `--from-layer=brd --to-layer=spec` (or full
   `--from-layer=brd --to-layer=iplan`) against url-shortener with the
   bypass NOT set. The cascade will regenerate the existing layers under
   the new necessary-upstream contract; PRD-01.md will be generated as
   part of the chain; orphan `@prd:` tags will be removed by the per-layer
   author SKILLs (now aligned with the new contract via NECESSARY-UPSTREAM-001
   Task 4c).
2. The regenerated corpus should pass `sdd_doc_lint` clean (no
   `TRACE-RES-001` findings).
3. Commit the regenerated `examples/url-shortener/docs/` as part of this
   PR — this is a framework-generated update, not a hand-edit, so it does
   not violate the never-hand-edit-example-artifacts rule.

### Fix 3 — Remove the temporary bypass

Once Fix 1 + Fix 2 land:

1. Delete the `SDD_LINT_SKIP_TRACE_RES` early-return from
   `_check_trace_resolution` (revert to strict enforcement).
2. Update the docstring to drop the bypass mention.
3. Verify the harness `SDD_LINT_SKIP_TRACE_RES=1` invocation in
   `test-acceptance.sh` (if any) is also removed.

## Out of scope

- AUTO-REMEDIATE-001 extension to handle TRACE-RES-001 — speculative;
  Fix 1 + Fix 2 + cascade-driven regen should be sufficient.
- Adding a `--skip-lint-smoke` flag to the harness — speculative; once
  Fix 2 lands, the corpus passes lint-smoke and the bypass is unneeded.
- Hermes mirror catch-up — plugin-first; tracked in `plans/HERMES-BACKLOG.md`.

## Verification

| #  | Check | Expected |
| -- | ----- | -------- |
| 1 | Unit `test_sdd_doc_lint_trace_resolution.py` (extended) | PASS — downstream + self-tag cases added |
| 2 | Unit `test_lint.py` valid fixtures | PASS — no regression |
| 3 | Conformance `test_layer_registry_necessary_upstream` | PASS — registry shape unchanged |
| 4 | `python3 -m sdd_doc_lint examples/url-shortener/docs/` (post-regen) | 0 findings — corpus self-consistent |
| 5 | TDD-RT-001 cascade re-run with bypass REMOVED | Cascade proceeds past Phase 0; converges per TDD-RT-001 plan Task 9 |

## Notes

- The bypass `SDD_LINT_SKIP_TRACE_RES=1` is a temporary scaffold. CI should
  NEVER set it on protected branches. Document that constraint in CONTRIBUTING.md
  when this plan lands.
- Bug 1 (downstream-skip) is the spec correctness fix; Bug 2 (corpus regen)
  is the data alignment that completes the contract migration. Both ship
  in this PR.
