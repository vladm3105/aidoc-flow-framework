# Framework Feedback Log — `<PROJECT-NAME>`

> Consumer-side log of framework friction discovered while applying the
> aidoc-flow framework to this project. Per
> [`framework/governance/FRAMEWORK_FEEDBACK_LOG.md`] Tier 1 —
> consumer projects keep this log inline as friction surfaces; the
> framework maintainer aggregates surfaced items into
> `plans/FRAMEWORK-TODO.md` (Tier 2) upstream.
>
> **Rules:**
>
> - Append entries the moment friction surfaces. No "later PR".
> - Entry format: tag + one-line title + Context + Fix shape. ≤ 3 lines.
> - Tags: `[lint]` / `[harness]` / `[skill]` / `[template]` / `[sync]` /
>   `[plan-review]` / `[docs]` / `[platform-parity]` / `[example-corpus]` /
>   `[governance]`.
> - When entries are surfaced upstream (via PR or issue), move them to
>   **Surfaced** with the upstream link.
> - When an upstream fix lands, move the entry to **Closed** with the
>   merge-commit SHA.
> - Don't double-track. If an upstream plan exists, cross-reference it.

## Open

*(start logging here)*

<!--
Example shape (delete or replace once you have real entries):

- **[lint] sdd_doc_lint TRACE-RES-001 fires on `@tdd:` downstream pointer.**
  *Context:* cascade run 2026-06-10, SPEC-01 emits `@tdd: TDD-01` before TDD layer exists.
  *Fix shape:* TRACE-RES-001 should skip downstream-direction tags.

- **[harness] `--force` undocumented when re-running cascade after pre-cleanup.**
  *Context:* TRACE-RES-FIXUP-001 first cascade attempt aborted at "tree-safety FAIL".
  *Fix shape:* document the cleanup-then-`--force` pattern in plan templates or auto-stage in the harness.
-->

## Surfaced

*(entries moved here when surfaced upstream — include upstream PR/issue URL)*

## Closed

*(entries moved here when the upstream fix lands — include merge-commit SHA)*
