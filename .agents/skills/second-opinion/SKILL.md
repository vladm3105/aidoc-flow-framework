---
name: second-opinion
description: >-
  Run an independent fresh-context judgment of a high-stakes output, recommendation, plan, approval item, or status rollup before it reaches a decision-maker. Judge and generator must be different; this never replaces human approval.
---

# Second opinion (LLM-as-judge)

> Muse project skill — port of the canon global skill (`aidoc-flow-claude-agents-config/skills/second-opinion/SKILL.md`).
> Where the canon names a Claude-specific agent type, dispatch your engine's focused read-only subagent equivalent and keep the independence contract.

An independent review pass that raises decision **quality** before work leaves
your hands. It **does not replace a human gate** — where a human authorizes an
action, nothing the judge passes is thereby authorized.

## The independence rule — judge ≠ generator

This is the whole mechanism; everything else is packaging.

- The reviewer gets the **artifact plus its cited sources** — **not** the
  generator's reasoning or chain-of-thought. Handing over the reasoning invites
  the judge to grade the rationalization instead of the work.
- **Dispatch a fresh-context read-only subagent as judge.** Fresh context by
  construction; give it the rubric, output format, and independence rules in the
  delegation prompt. **Do not re-author a judge prompt ad hoc** — prompt
  variance silently weakens the judge, and a weakened judge still returns
  confident-looking verdicts.
- **The rubric lives in the delegation prompt, not here.** One source;
  duplicated rubrics drift. Rubric changes are edits to the delegation prompt,
  versioned by its `rubric vN` output stamp.
- Diversity axes, in increasing strength: same model fresh context (default) →
  a different model tier via the `model` override → a different vendor.

**This skill owns the independent-review contract.** `verified-planning` and
`preprod-review` apply it to their own artifacts; where any of them disagree on
what independence means, this file governs.

## When to run

- Any **high-stakes or irreversible** recommendation before it is acted on.
- Before an **approval item is surfaced to a human** (see `approval-gate`).
- Before a **status rollup** reaches whoever will act on it.
- **Granularity:** judge the *plan*, the *final*, and any *irreversible step* —
  not every micro-step. Skip trivial green chatter.

## Output

The judge emits a `SECOND-OPINION — <artifact>` block carrying verdict /
confidence / issues / fix, stamped with its rubric version. The block's
authoritative shape lives in the delegation prompt — do not copy it here; the
skill's copy would stale on the next rubric bump.

- **pass** → proceed, and stamp the provenance line (reviewer + rubric version)
  on the artifact so an audit can tell which judge saw it.
- **revise** → return to the generator with the issues named; re-review.
- **block, low confidence, or judge-vs-generator disagreement** → **escalate
  with the dissent stated**. Do not bury a disagreement by re-running until it
  agrees.

## Cost and limits — be honest about these

- **Single judge** by default. A jury (diverse panel) is for the highest-stakes
  cases only.
- The judge **is itself an LLM** — injectable, and biased by position, verbosity
  and self-preference. It can *introduce* errors as well as catch them.
- **Agreement ≠ correctness** for unverifiable claims. Two models liking a
  strategy call is not evidence the call is right.
- Don't judge trivial work. A judge that runs on everything gets skimmed, and a
  skimmed judge is worse than none because it launders work as reviewed.

## Measure it, or drop it

**Log every real run** — date · item · verdict · confidence · reviewer ·
outcome — and mark each one **catch / false-positive / redundant / miss**. Every
~5–10 cycles, read the tally and make a **keep / narrow / drop** decision.

This ledger is the guard against cargo-culting the judge. A review pass that
cannot show catches is costing tokens and lending false confidence, and the
honest response is to narrow its scope or stop running it. **A skill that cannot
be shown to earn its keep should be retired** — including this one.

Where the log lives is the repo's call: whatever its governance table declares
for decision records, or a simple ledger file. If a repo declares nothing, create
the ledger file — or, where even that is unwanted, keep the tally as a memory
(`metadata.type: project`).

**Not the session report.** A tally read at cycle 10 cannot live in something
discarded at cycle 1, which makes the keep / narrow / drop decision unrunnable
and this whole section decorative.

## `[workspace]` — aidoc-flow specifics

In the aidoc-flow workspace this implements **ADR-0003 (judge-v0)** for the
Crew, and:

- Run it before a `/weekly` rollup or `/supervisor-brief` reaches the founder,
  and before staging an `ops/inbox/` 🟡/🔴 item (it extends `approval-gate`).
- **Fixed-primary for governance:** governance and decision outputs use one
  primary generator plus this judge — no divergent hybrid candidates.
- The run log is `ops/judge-log.md`; the founder or `ceo` marks the outcome
  column, and the tally drives the keep/narrow/drop call.
- The rubric extends the `weekly-cadence` quality bar.
