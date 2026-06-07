# <TASK-ID> Plan — <short title>

| Field      | Value                          |
|------------|--------------------------------|
| Task       | <TASK-ID>                      |
| Depends on | <prior tasks / decisions>      |
| Status     | PLANNED — <YYYY-MM-DDThh:mm:ssZ> |
| Feeds      | <downstream tasks>             |

## Objective

<One paragraph: what this task delivers and why.>

## Scope

**In:** <what is in scope>
**Out:** <what is explicitly deferred / not in scope>

## Approach

<Source → target maps, transformation rules, design choices.>

## Step sequence

1. <step>
2. <step>
3. **Verify** (see below).
4. **Land:** commit; update `CHANGELOG.md` / `ROADMAP.md` as needed; tick
   `plans/MIGRATION_TODO.md`.

## Verification

<Concrete, runnable checks. Nothing is "done" until these pass.>

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | <risk> | <mitigation> |

## Claim ledger

> Every load-bearing claim (file path, signature, field/key, event/enum value,
> behavioral assertion) cites the `file:line` you actually read. `UNVERIFIED`
> rows must be resolved before the plan is ready.
> `.claude/skills/verified-planning/check_plan.py` checks each citation resolves.

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | <claim> | `<symbol>` | <path>:<line> |

## Review log

> A plan needs **at least two** passes here before it may be presented or
> implemented (see `CLAUDE.md` § Development workflow), and **at least one MUST
> be an independent fresh-context review** (dispatch the `Agent` tool — author
> self-review does not count). Each pass: re-read the whole plan, list findings,
> fold fixes back into the sections above. Stop when a pass finds nothing; end
> the final pass with an explicit `**Result:** ready`.
>
> Every pass also cross-checks the **Verification** section against the
> transformation rules — each pattern precise, with no false positive (a rule's
> intended output trips a check) and no false negative (a check misses
> something a rule was meant to remove). Dry-run the verification commands
> against the legacy source while planning, to calibrate them.

### Pass 1 — <YYYY-MM-DDThh:mm:ssZ>

- <finding → how the plan was changed>

### Pass 2 — <YYYY-MM-DDThh:mm:ssZ> — independent

- <findings from the fresh-context reviewer, or "no new findings">
