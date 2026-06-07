---
name: verified-planning
description: Use when creating or reviewing an implementation plan (any PLAN-*.md or design plan). Enforces a cited Claim ledger and a mandatory fresh-context independent review before the plan is called ready, so plan review is verification, not ritual. The user's own conventions take priority over generic plan skills.
---

# Verified Planning

Plan-review rules get ritualized: the author writes "Pass 1/Pass 2" from memory
and finds nothing, because the author cannot see their own wrong assumption. This
skill replaces ritual with two forcing functions.

## 0. Where the plan lives

A development plan lives in the **owning repo's `plans/`** directory, named per
that repo's convention (`PLAN-NNN_slug.md`) — never in `docs/superpowers/` and
never in the `aidoc-flow` umbrella (which holds no development). This convention
takes priority over any generic plan skill's default location.

## 1. Draft with a Claim ledger

Every **load-bearing claim** in the plan — a file path, a function/method
signature, a field or key name, an event/enum value, or a behavioral assertion
("validator X ignores unknown keys", "the loop reads only Y") — goes in a
`## Claim ledger` table with the `file:line` you actually opened and read:

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | completion is recorded as a log event | `task_completed` | platforms/hermes/src/iops_hermes/orchestrator/loop.py:223 |

A claim you have not verified is written `UNVERIFIED` in the Citation column and
**cannot survive to ready**. Do not guess a line number — open the file.

## 2. Mandatory independent review (the part that actually works)

Before the plan is ready, dispatch a **fresh-context subagent** (the `Agent`
tool) to review the plan adversarially against the real source and any external
contracts. Your own re-read does NOT count. Tell it to verify every Claim-ledger
citation, find load-bearing claims missing from the ledger, and hunt for wrong
assumptions. Record the result as `### Pass N - <date> - independent`.

Fold in its findings, then re-dispatch until an independent pass returns **zero
load-bearing findings**. Only then is the plan ready / may the PR open.

## 3. Run the gate

Before declaring ready: `python .claude/skills/verified-planning/check_plan.py
<plan>`. On success it prints `ok <plan> — verified N citation(s), M review
pass(es)`. It checks *form and citation-resolution*; it cannot check that the
review was genuinely independent or that the ledger is complete — that is step
2's job. Fix anything it flags.

- **Scaffold a new plan:** `check_plan.py --init <plan>` appends the
  `## Claim ledger` + `## Review log` sections (idempotent).
- **Cite paths relative to the plan's own repo root** (nearest `.git` ancestor).
  For **cross-repo** citations (a sibling repo), add `--root <dir>` — citations
  resolve against the plan's repo first, then each `--root` in order.

## What "ready" means

Claim ledger has zero `UNVERIFIED` rows and the gate passes; the Review log has
≥2 passes, ≥1 independent, and the final pass states zero findings — end it with
an explicit `**Result:** ready` line (or "no new/further/load-bearing findings").
This layers on top of `superpowers:writing-plans` — it does not replace it.
