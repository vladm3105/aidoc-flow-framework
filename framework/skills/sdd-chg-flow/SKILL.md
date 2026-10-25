---
name: sdd-chg-flow
description: >-
  Classify any artifact change into exactly one CHG flow (HOTFIX, CODE2S, CODE2C, SEED2C, DIR2C, SDD2C) before authoring the CHG, so the vehicle matches the router instead of the guess.
---

# SDD CHG Flow Classifier

> Framework skill — routes to `framework/governance/CHG_REQUEST_FLOWS.md` §1 (normative router).
> Paths below use `<skills-root>` = this `framework/skills/` directory.

Every artifact change MUST be classified into exactly one flow — or a governed
non-flow path — before a CHG is authored. Classify in router order; the first
matching row wins.

## 1. The router (first match wins)

| Code | Flow | Traversal | Trigger |
|---|---|---|---|
| HOTFIX | `hotfix` | Code → Prod (post-hoc Doc) | Critical production issue needing a fix before authorization |
| CODE2S | `code_to_sdd` | Code → IPLAN → SDD | Working code preceding its specs (reverse-authored) |
| CODE2C | `code_to_code` | Defect → IPLAN → Code | Defect traceable to a Completed/Verified parent IPLAN |
| SEED2C | `seed_to_code` | Seed → Module → SDD → Code | Product/design change to an implemented product |
| DIR2C | `iplan_to_code` | IPLAN → Code/Docs | Request unrelated to any prior IPLAN, no product-behavior change |
| SDD2C | `sdd_to_code` | BRD → … → Code → EVAL | New product or layer chain, no prior implementation |

Legacy aliases: HOTFIX = Emergency, CODE2S = Type-R, CODE2C = F4, SEED2C = F3, DIR2C = F2, SDD2C = F1.

## 2. Read the row, not just the code

Each router row fixes `change_source`, `change_level`, entry gate, SDD-cascade
duty, and IPLAN shape. DIR2C takes `change_source: direct`, C1, GATE-CODE,
`sdd_lifecycle: []`, and a scoped IPLAN (manifest + steps only) — and nothing
else satisfies CHG-L013. A fast-path flow touching 03_EARS/04_BDD/05_ADR/06_SPEC
trips CHG-L019: that change is SDD2C whether it feels small or not.

## 3. Hand off, don't author here

Classification is the whole job. The CHG itself belongs to `sdd-chg-author`;
issue validation before any of this belongs to `sdd-chg-triage`. State the
verdict as one line — `Flow: DIR2C (F2), C1, direct, GATE-CODE` — and stop.
