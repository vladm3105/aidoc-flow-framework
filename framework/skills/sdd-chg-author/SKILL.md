---
name: sdd-chg-author
description: >-
  Author a C1/C2/C3 CHG that passes chg_lint first time: complete the §3.4 checklist before writing, validate per §3.4.1 after, and never put code steps in the CHG.
---

# SDD CHG Author

> Framework skill — routes to `framework/layers/09_CHG/CHG-TEMPLATE.yaml`,
> `framework/governance/DOC_GOVERNANCE_CORE.md` §3.4/§3.4.1, and
> `sdd_doc_lint/chg_lint.py` (CHG-L001–L019).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> The flow must already be classified (`sdd-chg-flow`); the issue already
> validated (`sdd-chg-triage`).

## 1. Checklist before writing (§3.4, blocking)

Complete `DOC_GOVERNANCE_CORE.md` §3.4 BEFORE writing. For a docs/tooling
change the load-bearing items are: read every referenced file (item 1),
couple or split issues deliberately (7), name automated test specs (8),
declare the SDD-lifecycle position (11–12: new files only means no
archive/rewrite steps), and keep every step in `documentation_sync` /
`iplan_creation` phases with no `code_implementation` anywhere (13–14).

## 2. Write the CHG

Mirror the latest `framework/archive/CHG-*/CHG-*.yaml` DIR2C vehicle:
`metadata` (`change_level`, `change_source`, `semver_impact`,
`version_action`, `entry_gate`), `change_control` (status starts at
`Proposed`, lifecycle Proposed → Approved → In-Progress → Implemented →
Completed), a non-empty `decision:` block, `problem_statement` with an
explicit `scope` file list, and `implementation` carrying only the
`iplan_ref` plus phased milestones. DIR2C states `change_source: direct`
and `sdd_lifecycle: []` — an empty lifecycle with a code manifest and no
`direct` source is a CHG-L013 misfit.

## 3. Validate before committing (§3.4.1, mandatory)

Run `python3 sdd_doc_lint/chg_lint.py <chg-file.yaml>` and clear every
error (exit 0 is the only pass): lifecycle order, gate approval on C3,
no code steps, a referenced IPLAN, SDD-first order, lifecycle attribution
with `author` (+ `chg_ref` for modules), no premature completion, and the
mandatory `decision:` block. Then hand the IPLAN itself to `sdd-iplan`.
