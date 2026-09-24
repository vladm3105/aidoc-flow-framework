# Seed Contract

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-09-24 |
| Author | Framework Maintainer (AI agent + owner, CHG-11) |
| Framework Version | 0.61.0 |


The normative contract over the `seed/` input tier — the human-authored source
material a cycle's first BRD is written from. The spec names the seed as an
input (`README.md` inputs row; `governance/aidoc/AIDOC.md` tier diagram + table) but
defined no obligation over it: nothing required the SDD chain to account for
what the seed says, and nothing forbade "fixing" the seed when an audit found a
gap. This document closes that gap. It is engine-agnostic — it constrains the
artifacts, not any platform's runtime.

## Scope

`<project>/seed/` holds the raw, human-authored requirements a cycle starts
from (a brief, a stakeholder note, a prior-art dump). It is **not** a chain
artifact in the SDD sense: it carries no element IDs and is not linted as an
SDD document. It is *input* to the first BRD of a
cycle — and since CHG-11 it is a **versioned** input tier: each seed file
carries a `document_control` block (see §Seed document control) and versions
via archive → rewrite → bump + `supersedes`, affected files only, exactly like
the SDD layers and modules.

The second human-input tier, `<project>/chg/`, is out of this contract's scope
— it is governed by the CHG gates (`chg/`). The seed is the *initial* input;
`chg/` is the *ongoing* one.

## The three rules

### 1. Frozen per version

A **published** seed version is immutable: once the first BRD of a cycle is
authored against seed vN, the vN files of that cycle are **historical input**
and are not edited to resolve findings. A finding of the
form "the seed says X, the chain does not" is resolved **in the BRD** (by
absorbing, rejecting, or deferring the claim — Rule 2), never by amending the
published version until the gap disappears. Editing a published version to make
an audit pass destroys the record of what was actually asked for.

The seed **tier**, however, versions like every other tier. When an assumption
the seed records genuinely changes, the change ships as a **supersede** —
archive vN, author vN+1 clean, link `supersedes` — authorized by a CHG
(`seed_scope` decision `supersede`, flows doc §4 Phase 0a), affected files
only. New human input that genuinely arrives mid-cycle and forms no part of
the standing seed arrives through `<project>/chg/`, which already has a gate.
In short: the seed captures the cycle's starting point **per version**;
`chg/` captures everything after it; a supersede moves the starting point
forward without rewriting history.

### 2. Total disposition

Every claim the seed makes has **exactly one** disposition in the BRD set of
that cycle:

| Disposition | Meaning | Required carrier fields |
| --- | --- | --- |
| `absorbed` | The claim is realized by the chain. | names **≥1 BRD element ID** that carries it, **and** pins `seed_version:` — the seed file version the claim was absorbed from |
| `rejected` | The claim is deliberately not carried. | a `rationale` |
| `deferred` | The claim is carried by a later cycle. | a `rationale` **and** a `target_cycle` |

"Total" means no seed claim is silently dropped: a claim with no ledger row is
a defect, not an omission. The ledger lives in the BRD's `seed_disposition:`
section (a `_required: false` carrier — see the BRD template) so that adding
the contract does not retroactively break BRDs authored before it. Rows
authored before the pin exist carry no `seed_version` and keep passing —
pins are required only for rows authored or re-pointed after a supersede.

When a seed file is superseded (vN → vN+1), every ledger row pinned to vN
**must** be re-pointed or re-disposed in the same CHG lifecycle: re-read the
claim against vN+1, update the pin, and confirm the disposition still holds.
A row pinned to an archived version after its supersede has landed is stale —
`SEED01` fails it deterministically (see Enforcement split).

### 3. BRD is the absorption point

A seed claim first surfacing at PRD or later — with no BRD row accounting for
it — is a **gap**, not a shortcut. The BRD is where the chain first accounts
for the seed; a claim that skips it has no traceable origin. A `deferred` claim
SHOULD also appear in the BRD's `out_of_scope:` declaration, and the ledger row
is what makes that deferral traceable back to its seed input.

## Seed document control

Every seed file carries a control header — frontmatter, not prose — so the
tier versions without disturbing its human-readable form:

```yaml
document_control:
  document_id: "SEED-<slug>"
  version: "2.0"
  status: Approved          # Draft | Approved | Superseded
  author: "ai-agent: <id> + human: <name>"
  created_date: "2026-09-01"
  last_updated: "2026-09-24"
  framework_version: "0.61.0"
  supersedes:
    - "seed/architecture/auth.md v1.0 (docs/sdd/09-CHG/archive/CHG-NN/seed/auth-v1.md)"
  revision_history:
    - version: "2.0"
      date: "2026-09-24"
      author: "ai-agent: <id>"
      chg_ref: "CHG-NN"
      description: "one line: what changed and why"
```

`author` names the AI agent that authored the version **and** the supervising
human; `chg_ref` names the authorizing CHG; each `revision_history` entry
describes the change in one line. A published version's control block is as
immutable as its prose.

## AI-attribution rule (GOV-021)

Any document an AI agent creates or modifies in a versioned tier **must**
carry `document_control` + metadata naming the agent, the supervising human,
the authorizing CHG, and the change. If the original document lacks the
carrier, the AI agent **creates it in the next version during update** —
backfill is mandatory, not courtesy. Rationale: AI agents do the mechanical
sync work that keeps the chain actual; without per-version attribution a
future reader cannot tell curated history from drift. The deterministic half
(lifecycle entries carry `author`/`chg_ref`; `CHG-L015`) is machine-checked;
carrier completeness on tiers whose shape the linter cannot parse stays with
the reviewer lens — the same split as the seed contract's own enforcement.

## Enforcement split

The contract is enforced by mechanisms with deliberately different reach.
Reading any gate as stronger than it is invites treating a green lint as
proof the seed was fully absorbed, which no lint can be:

| Question | Enforcer |
| --- | --- |
| Is every ledger row well-formed, and does each `absorbed` row's target element resolve? | `SEED01` — deterministic lint (`LINT_RULES.md`) |
| Does each pinned row's `seed_version` match the corpus seed file's `document_control.version`? | `SEED01` — deterministic lint (skip when the row is unpinned or the seed file is absent from the corpus) |
| Did the ledger *miss* a claim the seed makes, or does a re-pointed row misread the new version? | the BRD auditor lens (check **C8**) — requires reading the seed prose against the ledger; not machine-checkable |

`SEED01` guarantees the ledger is *structurally* sound and *version-current*; it cannot know whether
a claim the seed prose makes is absent from the ledger. Completeness is a
reading judgement and lives with the auditor lens. Authoring the ledger is the
business-analyst lens's check **C8**.

## Authority

This contract; `layers/01_BRD/BRD-TEMPLATE.yaml` (`seed_disposition:` carrier
with `seed_version` pin); `LINT_RULES.md` (`SEED01`, `GOV-020`, `GOV-021`);
`playbooks/01_BRD/business_analyst.md` (C8 — author
the ledger) + `playbooks/01_BRD/auditor.md` (C8 — completeness against the
seed, including stale-pin reading); `DECISIONS.md` **GD-08** (historical —
frozen-forever) as updated by **GD-36** (frozen-per-version).

---

## Seed Gap Review Gate

### When it fires

**Primary:** After BRD generation, before PRD generation. All BRDs must be
generated before running the review. This is the earliest point where seed
coverage can be validated.

**Secondary:** After any seed doc supersede. A supersede changes architectural terms
that propagate through the entire SDD chain. The secondary gate catches stale
references before they accumulate.

### What it checks

1. Cross-reference every BRD's functional requirements against `seed/architecture/`
   and `seed/agent-surface/`
2. Identify any architectural domain with no seed document
3. Check existing seed docs for uncovered sub-domains
4. After seed supersedes: confirm every vN-pinned ledger row was re-pointed or
   re-disposed, then grep all SDD files for stale terms

### Decision

| Outcome | Action |
|---------|--------|
| **No gaps** | Proceed to PRD generation |
| **Gaps found (missing dispositions)** | Fix BRD seed_disposition sections |
| **Gaps found (missing seed docs)** | Start new SDD iteration: create missing seed docs → update module docs → regenerate affected BRDs |
| **Stale pins found** | Re-point or re-dispose the rows in the same CHG lifecycle (`SEED01` fails them until fixed) |
| **Stale references found** | Grep and fix all affected SDD files |

### Why after BRD, not after IPLAN

- BRDs are the first formal SDD layer — gaps caught here propagate to zero downstream files
- By IPLAN completion, the full SDD chain has embedded the gaps
- Fixing after IPLAN requires touching 14+ files; fixing after BRD requires touching 9 files

### Scope of regeneration

When a seed gap review triggers a new SDD iteration:
- Only affected layers are regenerated, not the entire chain
- New seed docs are created in `seed/architecture/` or `seed/agent-surface/`
- Changed seed docs are superseded (archive vN, author vN+1, link `supersedes`) — never rewritten in place
- Corresponding module docs are created or updated in `modules/`
- Existing BRDs are updated with new seed_disposition entries (with current `seed_version` pins)
- Downstream SDD layers are regenerated only if the new seed changes their scope
- A CHG record is created if existing SDD documents are rewritten
