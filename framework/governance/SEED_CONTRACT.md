# Seed Contract

The normative contract over the `seed/` input tier — the human-authored source
material a cycle's first BRD is written from. The spec names the seed as an
input (`README.md` inputs row; `docs/AIDOC.md` tier diagram + table) but
defined no obligation over it: nothing required the SDD chain to account for
what the seed says, and nothing forbade "fixing" the seed when an audit found a
gap. This document closes that gap. It is engine-agnostic — it constrains the
artifacts, not any platform's runtime.

## Scope

`<project>/seed/` holds the raw, human-authored requirements a cycle starts
from (a brief, a stakeholder note, a prior-art dump). It is **not** a chain
artifact: it is not versioned by the BRD→Code cascade, carries no element IDs,
and is not linted as an SDD document. It is *input* to the first BRD of a
cycle.

The second human-input tier, `<project>/chg/`, is out of this contract's scope
— it is governed by the CHG gates (`chg/`). The seed is the *initial* input;
`chg/` is the *ongoing* one.

## The three rules

### 1. Frozen input

Once the first BRD of a cycle is authored, the seed files of that cycle are
**historical input** and are not edited to resolve findings. A finding of the
form "the seed says X, the chain does not" is resolved **in the BRD** (by
absorbing, rejecting, or deferring the claim — Rule 2), never by amending the
seed until the gap disappears. Editing the seed to make an audit pass destroys
the record of what was actually asked for.

New human input that genuinely arrives mid-cycle does not go into the seed
either — it arrives through `<project>/chg/`, which already has a gate. The
seed captures the cycle's starting point; `chg/` captures everything after it.

### 2. Total disposition

Every claim the seed makes has **exactly one** disposition in the BRD set of
that cycle:

| Disposition | Meaning | Required carrier fields |
| --- | --- | --- |
| `absorbed` | The claim is realized by the chain. | names **≥1 BRD element ID** that carries it |
| `rejected` | The claim is deliberately not carried. | a `rationale` |
| `deferred` | The claim is carried by a later cycle. | a `rationale` **and** a `target_cycle` |

"Total" means no seed claim is silently dropped: a claim with no ledger row is
a defect, not an omission. The ledger lives in the BRD's `seed_disposition:`
section (a `_required: false` carrier — see the BRD template) so that adding
the contract does not retroactively break BRDs authored before it.

### 3. BRD is the absorption point

A seed claim first surfacing at PRD or later — with no BRD row accounting for
it — is a **gap**, not a shortcut. The BRD is where the chain first accounts
for the seed; a claim that skips it has no traceable origin. A `deferred` claim
SHOULD also appear in the BRD's `out_of_scope:` declaration, and the ledger row
is what makes that deferral traceable back to its seed input.

## Enforcement split

The contract is enforced by two mechanisms with deliberately different reach.
Reading the gate as stronger than it is invites treating a green `SEED01` as
proof the seed was fully absorbed, which it cannot be:

| Question | Enforcer |
| --- | --- |
| Is every ledger row well-formed, and does each `absorbed` row's target element resolve? | `SEED01` — deterministic lint (`LINT_RULES.md`) |
| Did the ledger *miss* a claim the seed makes? | the BRD auditor lens (check **C8**) — requires reading the seed prose against the ledger; not machine-checkable |

`SEED01` guarantees the ledger is *structurally* sound; it cannot know whether
a claim the seed prose makes is absent from the ledger. Completeness is a
reading judgement and lives with the auditor lens. Authoring the ledger is the
business-analyst lens's check **C8**.

## Authority

This contract; `layers/01_BRD/BRD-TEMPLATE.yaml` (`seed_disposition:` carrier);
`LINT_RULES.md` (`SEED01`); `playbooks/01_BRD/business_analyst.md` (C8 — author
the ledger) + `playbooks/01_BRD/auditor.md` (C8 — completeness against the
seed); `DECISIONS.md` **GD-08**.
