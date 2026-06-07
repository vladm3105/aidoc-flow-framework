# Verified Planning — design spec

**Date:** 2026-06-07
**Status:** design final (model: master + per-repo independent, no parent). PLAN.md written; confirming independent review owed before build.
**Scope:** a global + per-repo mechanism that makes plan review *real* instead of
ritual, by forcing checkable claim citations and a fresh-context independent
review before a plan PR opens.

## Problem

Plan-review rules already exist in three places — both `CLAUDE.md`s,
`PLAN-TEMPLATE.md`, and the user's auto-memory all require ≥2 review passes,
problem-sizing, and codebase cross-check. They still get ritualized: the plan
author writes "Pass 1 / Pass 2" entries from memory, re-reading their own prose,
and the entries find nothing because the author cannot see their own wrong
assumption.

Concrete failure (2026-06-07, `PLAN-013`): the author wrote a Review log with
"verified" passes that contained two load-bearing factual errors — claiming
`task_completed` is not a ledger event (it is, `loop.py:223`) and that
`SANDBOX.FORBIDDEN` was reachable through conformance (it is not without changing
`engine.py:97`). Both were invisible to author self-review and were caught only
by an independent agent that re-read the source. The recurring cost: every new
session repeats the cycle — draft, ritual review, ship, discover gaps later.

**Root cause:** the rules exist; the *mechanism that distinguishes a real review
from a ritual one* does not. A fourth copy of "do 2 passes" would also be
ritualized. The fix must be mechanical where it can be, and structurally force
independence where it cannot.

## What is and isn't mechanically checkable

- **Checkable (the gate's teeth):** that every load-bearing claim cites a
  `file:line` that *resolves* — the file exists, the line is in range, and the
  referenced token appears at/near it. A false claim cannot cite a real line.
- **Checkable (structure):** that the Review log has ≥2 ISO-stamped passes, ≥1
  tagged `independent`, and a final pass declaring zero findings.
- **NOT checkable:** that a review was *genuinely* independent, or that the
  Claim ledger is *complete*. Those remain the independent reviewer's job. The
  design is honest about this split: the script catches uncited/wrong claims and
  missing structure; the fresh-context reviewer catches completeness ("what
  load-bearing claim is missing from the ledger?") and soundness.

## Components

### 1. Skill: `verified-planning`

A skill encoding the *method*. Self-contained (carries the canonical Claim-ledger
+ Review-log format, so it works even in a repo with no `PLAN-TEMPLATE.md`).

Behavioral contract:

1. **Draft with a Claim ledger.** Every load-bearing claim in the plan — file
   path, function/method signature, field or key name, event/enum value, or a
   behavioral assertion ("validator X ignores unknown keys", "the run loop
   reads only Y") — is entered in a `## Claim ledger` table with the `file:line`
   the author actually read. A claim with no citation is written `UNVERIFIED` and
   cannot survive to "ready."
2. **Mandatory independent review.** Before the plan is "ready", dispatch a
   **fresh-context subagent** (the `Agent` tool / Task) that re-reads the source
   and any external contracts adversarially and returns findings. The author's
   own re-read does **not** satisfy this step. Record the result as a
   `Pass N — independent` entry.
3. **Green gate.** Iterate (fix → re-review) until an independent pass returns
   zero load-bearing findings. Only then may the plan PR open. This operational­
   izes the existing "harden until a pass finds nothing" rule.
4. **Self-run the gate.** Before declaring ready, run
   `.claude/skills/verified-planning/check_plan.py <plan>` and fix anything it flags.

The skill does not replace `superpowers:writing-plans`; it adds the verification
discipline on top and points at it. It also fixes the storage convention: plans
live in the **owning repo's `plans/`** (PLAN-NNN), never `docs/superpowers/` or
the `aidoc-flow` umbrella.

### 2. Gate script: `.claude/skills/verified-planning/check_plan.py`

Self-contained Python (stdlib only), living inside each repo's committed skill
dir and invoked from there. Input: one or more
`PLAN-*.md`. Checks:

- **Claim ledger present and non-empty.** A `## Claim ledger` section with a
  table; ≥1 row. No `UNVERIFIED` rows remain.
- **Citations resolve.** Each row's citation is `path:line` (or `path:line-line`).
  For each: the path exists relative to repo root; the line is within the file;
  and the row's quoted token (if the row includes a backticked `symbol`) appears
  within a small window of the cited line (±3 lines, tunable). Unresolved/missing
  → failure with the row number and reason.
- **Review-log structure.** A `## Review log` with ≥2 `### Pass N - <ISO-date>`
  entries; ≥1 carrying the `independent` marker; the highest-numbered pass
  contains a zero-findings marker (e.g. `findings: none` / `no new findings` /
  `no further findings`).
- Exit nonzero with a human-readable report listing every failure; exit zero and
  print a one-line OK summary otherwise. A file with no `## Claim ledger` and no
  `## Review log` headers is treated as "not a gated plan" and skipped (so
  drafts mid-authoring don't block unrelated commits — the gate fires once the
  plan declares those sections).

### 3. Enforcement

- **Pre-commit hook** (each repo): a `local` hook `check-plan` with
  `files: (^|/)PLAN-[^/]*\.md$` (excluding `PLAN-TEMPLATE.md`), running
  `python .claude/skills/verified-planning/check_plan.py` on the staged plan(s).
  Active in repos that have plans; dormant (never triggers) in repos that don't.
- **CI** (each repo): `.github/workflows/plan-gate.yml` runs the same script on
  the PR's changed `PLAN-*.md` files (nested **and** top-level), so a local
  `--no-verify` cannot bypass it.
- **Template** (repos that have one — `framework`, `iops-framework`):
  `PLAN-TEMPLATE.md` gains the `## Claim ledger` table stub and the
  `Pass N — independent` convention, so skill, template, and gate share one
  format.

### 4. Distribution (no central source; each repo independent)

The skill must work across **Claude Code Web** (clones a single repo, no access
to the user's global `~/.claude/skills/`), **CLI**, and **Cowork**. So it is
committed *into each repo* as a self-contained `.claude/skills/verified-planning/`
**and** present globally.

- **Master = `~/.claude/skills/verified-planning/`** — the reference copy the
  user maintains, and the global copy for CLI/Cowork across all projects. Holds
  `SKILL.md`, `check_plan.py`, tests, the template snippet, the hook + CI
  snippets, `install.sh`, and this `PLAN.md` + `DESIGN.md`.
- **Each repo carries a full self-contained copy** of that skill dir, committed.
  The pre-commit hook + CI invoke `.claude/skills/verified-planning/check_plan.py`
  from that copy — **no `scripts/` duplication**, no second source.
- **No parent involvement.** The `aidoc-flow` umbrella holds nothing — there is
  no `shared/` and no central sync script. Repos are **independent** and may
  diverge (duplication is intentional, matching the org's strict-isolation ethos).
- **`install.sh`** (in the master) copies the master skill dir into a target
  repo, adds the CI workflow, and un-ignores `.claude/` where a repo gitignores
  it. Re-run to refresh a repo from the master.

## Rollout

All six aidoc-flow repos get the committed skill copy + hook + CI via `install.sh`.
Only `framework` and `iops-framework` currently have `PLAN-*.md` plans, so the
gate is *active* there and *dormant-but-ready* in `business`, `operations`,
`iplanic`, `knowledge-rag` (the hook's `files:` pattern simply never matches
until they adopt plans). The master is available in every CLI/Cowork session
immediately.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Per-repo copies drift from the master. | `install.sh` re-copies the master into a repo on demand; divergence is acceptable by design (each repo independent). The master is the reference; refresh a repo by re-running install. |
| R2 | The script's teeth are shallow (only checks citations resolve, not that the ledger is complete). | By design — completeness/soundness is the independent reviewer's job; the script + the mandatory fresh-context review are complementary, not redundant. |
| R3 | Author games the ledger (lists trivial claims). | The independent reviewer is explicitly tasked to flag missing load-bearing claims; the green gate can't pass while it has findings. |
| R4 | The gate ritualizes too (a fabricated `independent` pass). | Accepted limit: the script checks structure, not sincerity. The token-citation check still forces real reads for every claim, which is where errors hide. |
| R5 | Over-engineering this meta-tool (ironic). | Three components, stdlib-only script, no scoring/dashboards. Sized to the one failure it fixes. |
| R6 | CI cost / false failures on non-plan markdown. | The `files:` pattern + the "no ledger/review headers → skip" rule scope it to real plans only. |

## Out of scope

- A quality score or metrics dashboard for plans.
- Auto-dispatching the independent reviewer from CI (CI can't run a Claude
  agent); the reviewer is dispatched by the skill during authoring, and CI only
  verifies the recorded result + citations.
- Forcing the PLAN convention onto repos that don't use formal plans.
- Changing `superpowers:writing-plans` (we layer on top, not fork it).

## Enhancements (2026-06-07, post-merge)

- **Robust green-final detection** — replaced the brittle phrase-regex (which
  false-rejected "no load-bearing findings") with a bounded adjective list + an
  explicit `**Result:** ready` marker; tightened to avoid false-matching "no fix
  for these findings".
- **Cross-repo citations** — `check_plan.py --root <dir>` (repeatable) resolves
  citations against the plan's repo root *then* each extra root, so sibling-repo
  claims can be gated instead of hand-excluded.
- **Ledger UX** — success prints `verified N citation(s), M review pass(es)`;
  `--init <plan>` scaffolds the ledger + review sections (idempotent).

## Resolved decisions

- **No central source; each repo independent.** Master = `~/.claude/skills/
  verified-planning/` (also the global CLI/Cowork copy); each repo carries a
  self-contained committed copy; `install.sh` propagates master → repo. The
  `aidoc-flow` parent is **not** used for development and holds nothing.
  Confirmed 2026-06-07.
- **Plans live in the owning repo's `plans/`** (PLAN-NNN), never `docs/superpowers/`
  or the umbrella. The user's conventions/own skills outrank superpowers defaults.
  Confirmed 2026-06-07.
- **Gate lives in the skill dir** (`.claude/skills/verified-planning/check_plan.py`);
  hook + CI invoke it there — no `scripts/` copy. Confirmed 2026-06-07.
- **Claim citations = dedicated `## Claim ledger` table** (not inline tags),
  for parseability + conscious enumeration. Confirmed 2026-06-07.
- **Gate teeth = citation-resolution + Review-log structure**; completeness and
  genuine independence stay with the fresh-context reviewer. Confirmed.
- **Enforcement = pre-commit + CI** in all six repos; active where plans exist,
  dormant-ready elsewhere. Confirmed.
