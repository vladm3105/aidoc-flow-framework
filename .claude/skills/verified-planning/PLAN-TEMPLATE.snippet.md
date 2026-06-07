## Claim ledger

> Every load-bearing claim (file path, signature, field/key, event/enum value,
> behavioral assertion) cites the `file:line` you actually read. `UNVERIFIED`
> rows must be resolved before the plan is ready.
> `.claude/skills/verified-planning/check_plan.py` checks each citation resolves.

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | <claim> | `<symbol>` | <path>:<line> |

## Review log

> ≥2 passes before ready. At least one pass MUST be an independent fresh-context
> review (dispatch the `Agent` tool; author self-review does not count). The
> final pass must state zero findings.

### Pass 1 - <ISO-date>

- <finding → how the plan changed>

### Pass 2 - <ISO-date> - independent

- <findings from the fresh-context reviewer; fold each fix back in>

> When the final independent pass is clean, end it with an explicit marker the
> gate recognizes unambiguously: **Result:** ready — no further findings.
