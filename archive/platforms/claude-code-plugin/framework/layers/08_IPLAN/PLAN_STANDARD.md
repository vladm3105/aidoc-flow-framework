# Plan Standard — unified development/work plan

Authority for the structure of a **development/work plan**: the markdown
plan an execution agent writes before it touches code, lands in a repository's
`plans/` directory, and updates with dated progress as it implements. One
template serves every kind of change, from a one-commit bugfix to a multi-phase
feature; the agent keeps only the chapters its work type needs and deletes the
rest. This standard defines the section catalog, the work-type applicability
rules, and the review discipline once, so every repository that adopts the
template inherits the same shape. It is engine-agnostic and repository-agnostic.

The working instance of this standard is the repository's
`plans/PLAN-TEMPLATE.md`, copied to start each new plan.

## Scope and boundary

This standard governs **markdown `plans/*.md` development/work plans** — a third,
orthogonal concept that is distinct from BOTH formal IPLAN artifacts the layer
defines:

| Concept | Form | Governs |
| ------- | ---- | ------- |
| Permanent IPLAN | `IPLAN-NN_{slug}.yaml` | One SPEC component's file-creation order, executable steps, and session handoff. |
| Temporary IPLAN | `tmp/TMP-IPLAN-*.yaml` | A disposable bugfix/investigation with no SPEC upstream. |
| **Development/work plan** | **`plans/*.md`** | **The human-and-agent-readable plan-of-record for a change: objective, scope, approach, task sequence, verification, review trail.** |

Neither YAML artifact changes because this standard exists. A development plan
may *spawn* a Permanent or Temporary IPLAN as one of its tasks, but the two are
not interchangeable: the YAML IPLAN is an execution manifest consumed by an
agent step-by-step; the markdown plan is the design-and-review record a reviewer
reads to approve the change. See [`README.md`](README.md) for the YAML artifacts.

## Authoring rules

1. **Keep the chapters your work type needs; delete the rest.** Read the
   [applicability matrix](#applicability-matrix) for the plan's `Type`, keep the
   listed sections, and **delete** every section the matrix marks `—`. No empty
   headings and no `N/A` stubs survive into a real plan.
2. **Section tags** declare when a section applies:
   - `[REQUIRED]` — present in every plan, every work type. Never deleted.
   - `[CODE]` — keep only when the change touches executable code or tests;
     delete for a documentation or chore plan.
   - `[IF APPLICABLE]` — keep only when the section has real content; delete
     when it would be empty.
3. **Verification is `[REQUIRED]` for every work type** — only its *kind* varies.
   A code plan verifies with runnable commands; a documentation plan verifies
   with lint, link-check, render, or a review pass. A plan may drop the
   test-first chapter but never drops Verification.
4. **Two review passes minimum, at least one independent.** See
   [review discipline](#review-discipline).
5. **No magic version strings.** The plan's `Version impact` field describes
   *which* version stream moves and by what increment (PATCH/MINOR/MAJOR); it
   does not pin an absolute number that drifts before the change lands.

## Section catalog

| Section | Tag | Purpose |
| ------- | --- | ------- |
| Metadata table | `[REQUIRED]` | `Task`, `Type`, `Status` (state + ISO-8601 timestamp), `Depends on`, `Feeds`, `Version impact`. |
| Objective | `[REQUIRED]` | One paragraph: what the change delivers and why. |
| Scope (In / Out) | `[REQUIRED]` | What is in scope; what is explicitly deferred. Park speculative ideas as one-line backlog entries under Out of scope — do not design them here. |
| Approach / Design | `[REQUIRED]` | Source→target maps, transformation rules, design decisions. |
| File structure (Created / Modified) | `[IF APPLICABLE]` | The files the change adds or edits, one row each. |
| Implementation sequence | `[REQUIRED]` | Ordered `### Task N` steps. |
| Test-first step | `[CODE]` | A failing test precedes implementation for each behavior changed. One line inside the relevant Task; deleted for documentation/chore plans. |
| Verification | `[REQUIRED]` | A table of concrete checks (command or observable) → expected result. Runnable commands for code; lint/link/render/review for documentation. |
| Docs to update | `[REQUIRED]` | Checklist of documents-of-record the change must keep in sync within the same change (changelog, roadmap, handoff, decisions, and any version-quoting doc). |
| Risks | `[IF APPLICABLE]` | Table of risk → mitigation for non-trivial changes. |
| Claim ledger | `[IF APPLICABLE]` | Each load-bearing claim (a path, a symbol, a behavioral assertion) with the `file:line` actually read. Required when the plan rests on claims about existing source. |
| Review log | `[REQUIRED]` | Dated `### Pass N` entries recording findings and how each was resolved. |

## Applicability matrix

`✓` keep the section; `—` delete it (unless it has genuine content, for an
`[IF APPLICABLE]` row). The confirmed work-type set is `feature` / `bugfix` /
`documentation` / `refactor` / `chore`.

| Section | feature | bugfix | documentation | refactor | chore |
| ------- | :-----: | :----: | :-----------: | :------: | :---: |
| Metadata table | ✓ | ✓ | ✓ | ✓ | ✓ |
| Objective | ✓ | ✓ | ✓ | ✓ | ✓ |
| Scope (In / Out) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Approach / Design | ✓ | ✓ | ✓ | ✓ | ✓ |
| File structure | ✓ | ✓ | ✓ | ✓ | — |
| Implementation sequence | ✓ | ✓ | ✓ | ✓ | ✓ |
| Test-first step `[CODE]` | ✓ | ✓ | — | ✓ | — |
| Verification | ✓ | ✓ | ✓ | ✓ | ✓ |
| Docs to update | ✓ | ✓ | ✓ | ✓ | ✓ |
| Risks | ✓ | ✓ | — | ✓ | — |
| Claim ledger | ✓ | ✓ | — | ✓ | — |
| Review log | ✓ | ✓ | ✓ | ✓ | ✓ |

A `documentation` plan therefore drops the test-first step, Risks, and Claim
ledger but keeps Verification (lint/link-check/render). A `chore` plan is the
leanest: metadata, objective, scope, approach, a short task sequence,
verification, docs-to-update, and a review log.

## Review discipline

A plan completes **at least two review passes before it is presented or
implemented**, and **at least one pass is an independent fresh-context review**
(a reviewer that re-derives every claim against the real source, not the
author's own re-read). Each pass:

1. Re-read the whole plan.
2. List findings — wrong assumptions, missing load-bearing claims, sections that
   do not match the work type.
3. Fold every fix back into the sections above.
4. Re-validate that the prior pass's edits introduced no new inconsistency.

Continue until a pass surfaces zero load-bearing findings; the final pass states
that result explicitly. A plan whose Claim ledger still holds an unverified row
is not ready. The review trail lives in the Review log, one dated `### Pass N`
entry per pass.
