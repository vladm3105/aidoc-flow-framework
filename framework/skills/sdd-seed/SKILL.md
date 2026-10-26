---
name: sdd-seed
description: >-
  Author and validate the Seed (Tier 1): capture the cycle's starting point per version — frozen once published, totally disposed, attributed — never amended to pass an audit.
---

# SDD Seed Author

> Framework skill — routes to `framework/governance/SEED_CONTRACT.md`
> (three rules, AI-attribution GOV-021, seed gap review gate).
> Paths below use `<skills-root>` = this `framework/skills/` directory.
> Upstream of everything: modules (`sdd-module`) decompose the seed; the
> BRD absorbs, rejects, or defers each seed claim.

## 1. Freeze the starting point

A published seed version is immutable: once the first BRD of a cycle is
authored against seed vN, vN is historical input. A finding of the form
"the seed says X, the chain does not" resolves in the BRD, never by
amending the published version. When an assumption genuinely changes, ship
a supersede — archive vN, author vN+1 clean, link `supersedes` — authorized
by a CHG with a `seed_scope` supersede decision. New mid-cycle human input
outside the standing seed arrives through `<project>/chg/`, which already
has a gate.

## 2. Attribute every AI touch

Any document an AI agent creates or modifies in a versioned tier must carry
`document_control` + metadata naming the agent, the supervising human, the
authorizing CHG, and the change. Backfill is mandatory when the carrier is
missing. Lifecycle entries carry `author` (and `chg_ref` for modules) —
the machine-checked half (CHG-L015); carrier completeness stays with the
reviewer lens.

## 3. Seal and hand off

Run the seed gap review gate before modules begin. Next: `sdd-module`,
then `sdd-brd`. Seed-phase drafting before the first BRD is the sole
change needing neither CHG nor IPLAN — everything after it rides a vehicle.
