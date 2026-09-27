---
name: approval-gate
description: >-
  Use before an external or irreversible action such as sending, publishing, spending, deleting, overwriting, force-pushing, or writing outside the active repository. Classify risk, require human approval where needed, and never self-approve.
---

# Approval gate

Before acting on the outside world, classify the action and route it. **Never
self-approve:** an agent drafts and proposes; a human authorizes anything
external or irreversible.

**Standing authorization is not self-approval.** Where the human or the active
repository has authorized a class of action in advance and in writing, acting
within it executes that decision. Merge-on-green exists only where the active
repository explicitly grants it; the global rules supply safety carve-outs but
not merge authority. Red or incomplete CI always means do not merge.

## Tiers

| Tier | Examples | Do |
|---|---|---|
| 🟢 **Act directly** | commits on your own branch · drafts · internal messages · research and analysis · anything reversible inside your own workspace | proceed |
| 🟡 **Needs human OK** | send external email · public posts · publish a site or docs · spend, pricing or contract changes · anything a stranger will see | prepare the artifact below, then **stop** and surface it |
| 🔴 **Never autonomous** | financial commitments · legal execution · hiring · force-push · destructive data operations · writes to a repo you are not working in | flag to the human; do **not** prepare it for auto-execution |

**When unsure which tier, treat it as the higher one.** The cost of over-routing
is a few minutes; the cost of under-routing is unrecoverable.

Two distinctions that get missed:

- **Reversibility is not the only test.** An action can be technically
  reversible and still 🟡 because someone already saw it — a deleted post was
  still read, a sent email was still received.
- **Verbal authorization in chat does not by itself make a durable record.**
  Where an audit trail matters, the artifact *is* the record; a transcript is
  not one. (Some projects make this a hard rule — see the workspace section.)

## How to prepare a 🟡 action

Don't reduce approval to a bare "Approve?" — that invites a rubber stamp. Give
the human a **challenge-and-response** artifact they can acknowledge item by
item:

- **Action** — exactly what should happen.
- **Tier** — 🟡, or 🔴 if you are flagging rather than preparing.
- **Why (intent)** — the goal, and which objective or decision it serves.
- **Data lineage** — what sources this draws on, and whether any is unverified
  or externally sourced (therefore untrusted).
- **Permissions / account** — which tool, channel or account executes it, under
  whose credentials. **Least privilege** — nothing broader than the task needs.
- **Payload** — the full content, ready to use as-is.
- **Blast radius** — who sees it, what is affected if it goes out. Public?
  External party? One recipient?
- **Reversibility / rollback** — what breaks if it is wrong, and the concrete
  undo.

**Run `second-opinion` on the item before surfacing it, unless the item is trivial — its granularity rule governs.** An independent judge
checks payload and rationale and returns pass / revise / block. Fix on *revise*;
on *block* or judge dissent, surface that to the human **alongside** the item
rather than resolving it yourself. The judge raises quality; it never approves.

End with a checklist the human ticks before it ships:

```
## Approver checklist
- [ ] Intent is correct and worth doing now
- [ ] Data/sources verified (no unvetted external content)
- [ ] Right account + least-privilege scope
- [ ] Payload is exactly what should go out
- [ ] Blast radius understood and acceptable
- [ ] Rollback path is clear
```

Then tell the human an item is waiting. **Do not send, publish or spend.** After
approval and execution, keep the record — archive the artifact rather than
deleting it — and log anything decision-worthy wherever the repo keeps
decisions.

## Where the artifact goes

Whatever the repo declares for pending-human-action items. If it declares
nothing, put the artifact in the session report and say plainly that no durable
queue exists — that absence is itself worth surfacing, and inventing a directory
nobody reads is not a fix.

## Repository-specific contracts

If the active repository declares an approval inbox, autonomy tiers, or a
cross-repository feedback grant, that contract governs its locations and
exceptions. Read it at execution time; do not rely on a cached workspace roster
or path in this global skill. `submit-feedback` handles authorized issue filing.
