# <TASK-ID> Plan — <short title>

> **How to use this template.** This is the unified development/work plan. It
> conforms to `framework/layers/08_IPLAN/PLAN_STANDARD.md`. Set `Type` in the
> metadata table, then read the **applicability matrix** below: keep the sections
> your work type needs and **delete the rest** — including the `[REQUIRED]` /
> `[CODE]` / `[IF APPLICABLE]` tag markers and this instruction block. No empty
> headings and no `N/A` stubs survive into a real plan.
>
> | Section | feature | bugfix | documentation | refactor | chore |
> | ------- | :-----: | :----: | :-----------: | :------: | :---: |
> | Objective / Scope / Approach | ✓ | ✓ | ✓ | ✓ | ✓ |
> | File structure | ✓ | ✓ | ✓ | ✓ | — |
> | Implementation sequence | ✓ | ✓ | ✓ | ✓ | ✓ |
> | Test-first step `[CODE]` | ✓ | ✓ | — | ✓ | — |
> | Verification | ✓ | ✓ | ✓ | ✓ | ✓ |
> | Docs to update | ✓ | ✓ | ✓ | ✓ | ✓ |
> | Risks / Claim ledger | ✓ | ✓ | — | ✓ | — |
> | Review log | ✓ | ✓ | ✓ | ✓ | ✓ |

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | <TASK-ID>                                   |
| Type           | <feature \| bugfix \| documentation \| refactor \| chore> |
| Status         | PLANNED — <YYYY-MM-DDThh:mm:ssZ>            |
| Depends on     | <prior tasks / decisions, or none>          |
| Feeds          | <downstream tasks>                          |
| Version impact | <which version stream moves + increment, e.g. "framework MINOR"; or none> |

## Objective — [REQUIRED]

<One paragraph: what this change delivers and why.>

## Scope — [REQUIRED]

**In:**

- <what is in scope>

**Out of scope (deferred):**

- <what is explicitly deferred; park speculative ideas here as one-liners — do not design them>

## Approach / Design — [REQUIRED]

<Source → target maps, transformation rules, design decisions.>

## File structure — [IF APPLICABLE]

### Created

| Path | Purpose |
| ---- | ------- |
| <path> | <why> |

### Modified

| Path | Change |
| ---- | ------ |
| <path> | <what changes> |

## Implementation sequence — [REQUIRED]

### Task 1: <name>

- <step>
- **Test-first — [CODE]:** write the failing test for this behavior before the
  implementation. (Delete this line for documentation/chore work.)

### Task 2: <name>

- <step>

## Verification — [REQUIRED]

> Verification is required for every work type; only its *kind* varies — runnable
> commands for code, lint/link-check/render/review for documentation.

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | <command> | <expected> | <objective/scope> |

## Docs to update — [REQUIRED]

- [ ] `CHANGELOG.md` — entry
- [ ] `ROADMAP.md` — bullet (if applicable)
- [ ] `plans/HANDOFF.md` — narrative + next steps
- [ ] `plans/DECISIONS.md` — any non-obvious choice
- [ ] <any version-quoting doc the change touches>

## Risks — [IF APPLICABLE]

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | <risk> | <low/med/high> | <mitigation> |

## Claim ledger — [IF APPLICABLE]

> Each load-bearing claim (a path, a symbol, a behavioral assertion) with the
> `file:line` you actually opened and read. An unverified row cannot survive to
> ready.

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | <claim> | <symbol> | <path:line> |

## Review log — [REQUIRED]

> A plan needs **at least two** passes before it is presented or implemented,
> and **at least one** must be an independent fresh-context review. Each pass:
> re-read the whole plan, list findings, fold fixes back into the sections
> above; the next pass re-validates the prior pass's edits. Stop when a pass
> surfaces zero load-bearing findings.

### Pass 1 — <YYYY-MM-DDThh:mm:ssZ> — self-review

- <finding → how the plan was changed>

### Pass 2 — <YYYY-MM-DDThh:mm:ssZ> — independent (fresh-context)

- <finding, or "no new load-bearing findings">

**Result:** <ready / not ready>
