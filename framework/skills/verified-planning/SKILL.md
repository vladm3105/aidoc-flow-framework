---
name: verified-planning
description: >-
  Use when creating or reviewing an implementation or design plan. Require a cited claim ledger, a passing deterministic gate, and bounded fresh-context independent review before calling the plan ready.
---

# Verified Planning

> Framework adaptation — engine-agnostic copy of the canon global skill.
> Source: `aidoc-flow-claude-agents-config/skills/verified-planning/SKILL.md` (private, 2026-09-27).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Engine mapping: Claude Code `<skills-root>/<name>/`, Codex `<skills-root>/<name>/`, generic `<skills-root>/<name>/`.
> Where the canon names a Claude-specific agent type, use your engine's focused read-only subagent equivalent and keep the independence contract.


Plan-review rules get ritualized: the author writes "Pass 1/Pass 2" from memory
and finds nothing, because the author cannot see their own wrong assumption. This
skill replaces ritual with two forcing functions.

## 0. Where the plan lives

A development plan lives in the **owning repo's `plans/`** directory, named per
that repo's convention (`PLAN-NNN_slug.md`) — never in `docs/superpowers/` and
never in an aggregator/umbrella repo that holds no development of its own (the
`aidoc-flow` umbrella is one instance, not the rule). This convention
takes priority over any generic plan skill's default location.

## 1. Draft with a Claim ledger

Every **load-bearing claim** in the plan — a file path, a function/method
signature, a field or key name, an event/enum value, or a behavioral assertion
("validator X ignores unknown keys", "the loop reads only Y") — goes in a
`## Claim ledger` table with the `file:line` you actually opened and read:

| #   | Claim                                 | Symbol           | Citation                                                  |
| --- | ------------------------------------- | ---------------- | --------------------------------------------------------- |
| 1   | completion is recorded as a log event | `task_completed` | src/orchestrator/loop.py:223 |

A claim you have not verified is written `UNVERIFIED` in the Citation column and
**cannot survive to ready**. Do not guess a line number — open the file.

**A claim that source CANNOT settle is written `PROBE: <command>`.** Some claims
are live facts — a server-side setting, an API behaviour, a runtime observation.
Reading the repository harder will never answer them, and before this state
existed the only options were to guess in prose or to stall the plan forever.
Authors guessed: one plan answered the same unmeasurable question **three
different ways across three review passes**, each fold retracting the last.

A probe is not a free pass. The gate requires the command that would settle it,
**and** that the claim text names what it **blocks** — a phase, not the plan, and
**a phase that exists**. That is the point: a probe gates the phase that depends
on it and leaves the rest of the plan free to be ready.

Two rules learned from this mechanism's own first use, where both were broken:

- **The command must SETTLE the claim, not merely relate to it.** The first
  probe written under this rule asked *which bypass permits a fast-forward
  push* and gave a command that **applied a protection payload** — it never
  attempted the push, so it could not produce the answer. Write the command that
  ends the argument. If a claim is "X permits Y", the command must attempt Y.
- **Probe on a throwaway, not on the repo you care about.** That same command
  targeted the live canon repo. A probe is an experiment; run it where a wrong
  answer costs nothing.

| Citation | Means | Can reach ready? |
| --- | --- | --- |
| `path:line` | verified against source | yes |
| `UNVERIFIED` | you did not look | **no** |
| `PROBE: <cmd>` | looking cannot answer it | yes — the phase is blocked |

The **symbol is authoritative; the line is an advisory hint.** If a later edit shifts a cited line, the gate
still passes (the symbol is found elsewhere) and only **warns** that the line drifted — only a genuinely
**absent** symbol fails. Run `check_plan.py --fix <plan>` to re-point drifted line numbers (unambiguous
symbols) automatically.

## 2. Run the gate (before dispatching any review)

```sh
python3 <skills-root>/verified-planning/check_plan.py <plan>      # canonical — always present
python3 framework/skills/verified-planning/check_plan.py <plan>  # in-tree copy — what CI and the hook run
```

**Prefer the canonical path.** The repo copy exists so `plan-gate.yml` and the
pre-commit hook can run inside a checkout; it is a committed *gate*, not a
second home for this skill. A repo must never carry its own `SKILL.md`: the user
skill masks that project copy, leaving a duplicate that can drift while appearing
authoritative.

On success it prints `ok <plan> — verified N citation(s), M review pass(es)`. It
checks *form and citation-resolution*; it cannot check that the review was
genuinely independent or that the ledger is complete — that is step 3's job.

Run it **before** dispatching the independent review, and re-run it after any
fold that edits the plan: a broken citation costs this script milliseconds and
a reviewer a full pass.

- **Scaffold a new plan:** `check_plan.py --init <plan>` appends the
  `## Claim ledger` + `## Review log` sections (idempotent).
- **Cite paths relative to the plan's own repo root** (nearest `.git` ancestor).
  For **cross-repo** citations (a sibling repo), add `--root <dir>` — citations
  resolve against the plan's repo first, then each `--root` in order.

## 3. Mandatory independent review (the part that actually works)

Once the gate is green, dispatch the **`verified-planning-reviewer` agent** (a
fresh-context subagent). Your own re-read does NOT count. The independence
contract this rests on — judge ≠ generator, the reviewer never sees your
reasoning, never re-author the prompt ad hoc — is owned by the `second-opinion`
skill; this step applies it to plans. If the agent type is unavailable, fall
back to the `Agent` tool with an explicit `model` rather than reviewing it
yourself. The gate has already
proven every citation resolves to a real symbol — the reviewer must **not**
re-verify existence. Its job is the three things a script cannot do:

1. **Semantic truth** — does each cited symbol actually mean what its claim
   asserts, read in context;
2. **Completeness** — load-bearing claims missing from the ledger;
3. **Wrong assumptions** — the adversarial hunt for what the author cannot see.

**Define the unit once: a *pass* is a dispatched review** — the
`verified-planning-reviewer` agent, or the logged fallback (Agent tool + explicit
`model`) when the agent type was unavailable. Your own re-read is **never** a
pass, in either form.

Record the result as `### Pass N - <date> - independent` (`- fallback` when the
logged fallback was used). Fold in findings,
then re-dispatch until a pass returns **zero load-bearing
findings** — capped at **3 passes** (a circuit-breaker; where the workspace keeps
decision records this is OPS-0066). If
pass 3 still has load-bearing findings, STOP and surface the open items to the
human instead of dispatching a fourth.

### 3.1 Fold discipline — the loop only converges if the fold is bounded

**Measured, across 23 plans in one workspace: the median plan reached ready at
4.5 passes, and only 5 of 12 made it inside the cap of 3.** The cap was firing on
the *median* case, which turns a real escalation signal into noise. The cause is
not reviewer zeal — it is that **a fold writes new prose, and new prose is new
review surface**. Two consecutive passes on one plan each reported that *most* of
their findings were introduced by the previous fold: ~10 retired, ~9 created, net
progress ≈1 per pass.

Contrast the same loop over **code**: it converged in 3, because a code fix is
checked by a test the same session. The gate here checks that citations
*resolve*; nothing checks that the prose around them is *true*. So:

1. **Subtractive by default.** Deleting a claim, narrowing it, or striking a
   phase is free. **Adding** one costs: it needs its own citation and a
   `NEW@passN` marker, so the next reviewer knows exactly where the unreviewed
   surface is.
2. **Growth is a defect signal, not progress.** If the ledger or the plan grew
   between passes, the fold over-corrected. The gate prints the citation count
   every run — compare it to last pass. **If pass N+1 raises more load-bearing
   findings than pass N, stop folding and CUT SCOPE.** Split the plan, or drop a
   phase to its own plan. Do not fold a fourth time.
3. **Retract without over-swinging.** The commonest fold defect is replacing a
   wrong certainty with a *new, unmeasured* certainty. When a reviewer refutes a
   claim, the safe fold deletes it or marks it `PROBE` — it does not assert the
   opposite.
4. **Fix the ledger, not just the prose.** A retraction in the body while the
   ledger row still asserts the old claim leaves the plan's own instrument of
   record carrying the thing you just retracted. Both move together.
5. **A scope cut breaks REFERENCES, not facts — re-check them by hand.**
   Measured: after a cut, an independent pass found **no** surviving semantic
   falsehood in the source-cited body — the place every previous pass had found
   them — and instead found the plan's internal wiring in pieces. Renumbering
   collided ledger IDs and left nine prose references resolving to the wrong
   row; a phase lost its entire body when the section it pointed at was deleted;
   two decisions were orphaned. **Subtractive folding is safer on facts and more
   dangerous to references**, which is the opposite of what you would predict.

   After any cut, verify: ledger IDs are unique; every `Claim N` in prose
   resolves to the row you mean; every `§N` pointer exists; every phase still
   owns its deliverable. The gate checks none of this — it verifies each row's
   own citation and is blind to the plan's internal consistency.
6. **A cut can break things OUTSIDE the plan.** Shipped documents delegate to
   plans by name. A cut that deleted a section and a phase left merged canon
   pointing at `PLAN-NNN §3` and `PLAN-NNN A4`, neither of which still existed.
   Grep the repo for references to the plan before cutting, and move them in the
   same change.

### 3.2 What must converge

**Zero findings over the whole artifact is the wrong target** for a document that
grows. Converge the **decision set**: the claims that change what gets built.
A finding of the form "the plan should also mention X" is not load-bearing unless
X changes an action. Say so in the fold and move on — folding it grows the
surface for no decision.

## What "ready" means

Claim ledger has zero `UNVERIFIED` rows (a `PROBE` row is fine — it blocks its
named phase, not the plan) and the gate passes; the Review log has
**≥2 passes** (each one dispatched, per the definition above) and the final pass
states zero findings — end it with
an explicit `**Result:** ready` line (or "no new/further/load-bearing findings").
This layers on top of `superpowers:writing-plans` — it does not replace it.
