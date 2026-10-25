---
name: sdd-chg-triage
description: >-
  Validate a picked-up issue live against the tree (still open, reproducible, applicable) before any CHG or code, and stop with evidence when it is stale, superseded, or declined.
---

# SDD CHG Triage (Pre-Implementation Validation)

> Framework skill — the engine-agnostic half of issue validation. For the
> repo-specific workflow (labels, triage notes, memory write-back), dispatch
> the local `aidoc-triage` skill alongside this one.
> Paths below use `<skills-root>` = this `framework/skills/` directory.

Triage answers "may I implement now" (go/no-go). It NEVER implements,
closes, or rewrites history.

## 1. Fetch live, read the whole thread

`gh issue view <N>` with state, labels, body, and every comment, oldest
first. Corrections inside the thread supersede the body — triage the
corrected claim and name what it superseded. Filed line numbers rot fast:
treat them as hints, never facts.

## 2. Verify each claim against the tree

For every load-bearing claim, run the check: file and line exist (`grep -n`,
`git log --oneline -3 -- <file>`), counts reproduced by re-measuring (record
when a recount corrects the filing), CI behavior read from `gh pr checks` /
`gh run view --log-failed`. "Never held" claims need full-history
enumeration, not a spot check.

## 3. Supersede scan, then verdict

Search later `framework/archive/CHG-*/`, decisions, merged PRs, and open
branches for anything that already fixed, scoped, or declined the claim —
name links or record "none found", never assume. Exactly one verdict:
GO (all load-bearing claims alive, no superseder), SCOPED-GO (name the
surviving subset; the rest is not authorized), STALE, SUPERSEDED, or
ALREADY-FIXED. On the last three, report with evidence and stop — do not
open a vehicle around the verdict.

## 4. Hand off

On GO, classify with `sdd-chg-flow` and re-check blast radius against the
current tree (the filing-time radius may have shifted). The verdict is
perishable: record the `dev` SHA it was verified against.
