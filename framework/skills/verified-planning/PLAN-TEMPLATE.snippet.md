## Claim ledger

> Every load-bearing claim (file path, signature, field/key, event/enum value,
> behavioral assertion) cites the `file:line` you actually read. `UNVERIFIED`
> rows must be resolved before the plan is ready.
> `framework/skills/verified-planning/check_plan.py` checks each citation resolves.
>
> A claim source CANNOT settle — a live setting, an API behaviour, a runtime
> observation — is `PROBE: <command>`, and its claim text must name the phase it
> **blocks** — a phase that EXISTS (the gate checks it resolves). The command
> must SETTLE the claim, not merely relate to it: if the claim is "X permits Y",
> the command attempts Y. Run it on a throwaway, never on the repo you care
> about. It reaches ready; the phase it gates does not. Do not answer an
> unmeasurable claim in prose: that is how one plan answered the same question
> three different ways across three review passes.

| #   | Claim                              | Symbol     | Citation           |
| --- | ---------------------------------- | ---------- | ------------------ |
| 1   | <claim>                            | `<symbol>` | <path>:<line>      |
| 2   | <claim> — **blocks Phase \<N\>**    | `n/a`      | PROBE: <command>   |

## Review log

> ≥2 passes before ready. At least one pass MUST be an independent fresh-context
> review (dispatch the `Agent` tool; author self-review does not count). The
> final pass must state zero findings.

### Pass 1 - <ISO-date>

- <finding → how the plan changed>

### Pass 2 - <ISO-date> - independent

- <findings from the fresh-context reviewer; fold each fix back in>

> **Fold subtractively.** Deleting or narrowing a claim is free; ADDING one
> needs its own citation and a `NEW@passN` marker, because new prose is new
> review surface. If the ledger grew, or pass N+1 raises more load-bearing
> findings than pass N, **cut scope instead of folding again** — the loop does
> not converge while each fold manufactures its own next round. When a reviewer
> refutes a claim, delete it or mark it `PROBE`; do not assert the opposite.

> When the final independent pass is clean, end it with an explicit marker the
> gate recognizes unambiguously: **Result:** ready — no further findings.
