# Phase 1 benchmark — raw results and gate computation

Model (all passes): Muse Code, powered by Meta Muse Spark.
Run date: 2026-10-26. Task set frozen in `benchmark-tasks.md` before any arm ran.
Each pass: fresh-context runner, exactly 2 tool calls (read arm file, read task file),
no other reads/searches. Task order shuffled per pass (A1 forward, B1 reverse,
C1 interleaved, A2/B2/C2 rotated, A3/B3/C3 rotated).

## Per-pass accuracy (majority vote inputs)

| Pass | Arm | Accuracy |
|------|-----|----------|
| A1 | current MD | 100.0% (30/30) |
| A2 | current MD | 100.0% (30/30) |
| A3 | current MD | 100.0% (30/30) |
| B1 | structured MD | 100.0% (30/30) |
| B2 | structured MD | 100.0% (30/30) |
| B3 | structured MD | 100.0% (30/30) |
| C1 | YAML | 100.0% (30/30) |
| C2 | YAML | 100.0% (30/30) |
| C3 | YAML | 100.0% (30/30) |

Majority-vote accuracy: A_s = 100.0%, A_y = 100.0%. No misses on any task in
any pass, including T15/T16 (spec → SEED2C / GATE-SPEC decided unanimously via
the change_source column) and all 6 retrieval tasks.

## Retrieval steps

Median reported tool calls per pass: 2 for every arm (the two file reads).
No discrimination; arms are single-block extracts, so lookup depth cannot
differ. Full-document retrieval remains unmeasured by design.

## Tokens (deterministic file-size accounting)

| Arm | File bytes | Est. input tokens/pass (prompt + arm + tasks, ÷4 heuristic) |
|-----|-----------|--------------------------------------------------------------|
| A current MD | 4118 | ~2530 |
| B structured MD | 4384 | ~2600 |
| C YAML | 4036 | ~2510 |

YAML vs structured MD: (2600 − 2510) / 2600 ≈ 3.4% fewer tokens.
The 30% bar is missed by an order of magnitude; no measurement refinement
can change the verdict. Output tokens are negligible and symmetric.

## Gate computation (pre-registered)

- Floor: both arms ≥90% → satisfied (100.0%, 100.0%). Run is conclusive.
- Accuracy clause: A_y − A_s = 0.0pp < 15pp → not met.
- Token clause: |100.0 − 100.0| = 0 ≤ 2pp, but 3.4% < 30% → not met.
- **Verdict: GATE FAILS. Per the plan, the conversion plan ends after
  Phase 2a (structured Markdown). No Phase 2b YAML pilot.**

## Analysis

Format is not the lever on this contract: a clean six-row router plus a
ten-row gate table is classified perfectly in all three formats. The
measured YAML advantage is ~3% tokens and 0pp accuracy. The T15/T16
SEED2C-vs-DIR2C ambiguity resolved identically across arms, confirming that
residual difficulty lives in rule overlap, not in format. The rational
residual value is drift elimination (single-source generation), not agent
comprehension — and the plan's gate prices only the latter, so the plan
stops here by its own rule.
