---
name: submit-feedback
description: >-
  Use when a bug, defect, documentation error, or improvement idea must be captured. Follow the active repository's declared tracker and authorization; search before filing and use safe GitHub body-file mechanics. Record the source project and classify the finding as real-use or review.
---

# Submit feedback

> Muse-local instance of the submit-feedback workflow. Engine-agnostic wording follows
> `framework/skills/submit-feedback/` (itself adapted from the canon
> `aidoc-flow-claude-agents-config/skills/submit-feedback/SKILL.md`); where the canon
> names a Claude-specific agent type or path, use the Muse equivalent below and
> keep the independence contract.

An actionable finding must survive the session that found it. Capture it on the
owning repository's declared backlog surface; never leave it only in chat,
scratch, a commit message, or a session handoff.

A finding also has to carry **where it came from**. A defect a real project hit
and a defect a review pass went looking for read identically once written up,
and the reader cannot recover the difference. Record it at capture time.

## 1. Establish authority and destination

Read the active repository's `AGENTS.md` chain and any linked governance contract.
Determine:

- the owning repository;
- its declared backlog or tracker;
- whether you may write there;
- required labels, project state, or issue template;
- whether it declares a priority label, and its form.

Filing in the active repository is allowed only when its instructions or the
user authorize it. Writing to a different repository or external system needs
explicit authorization. Never infer permission from common ownership, a nearby
checkout, or an old hardcoded roster.

If the repository declares a file backlog, use that file. If it declares GitHub
issues, use the workflow below. Do not create a second queue.

## 2. Promotion bar

Capture when any of these is true:

- another person or session could act on it;
- it reproduces at `file:line` and has a plausible fix shape;
- it is user-visible or blocks a consumer.

Do not file speculation, a problem already fixed by the current change, or a
duplicate. A local workaround does not remove the need to capture the owning
defect.

## 3. Classify the origin

Every finding carries one of two origin classes, decided by a single
falsifiable test — **name what broke, or it is a review finding**:

- **`real-use`** — a project hit this while doing its own work. Something
  broke, blocked, or shipped wrong, and you can name it: the run, the PR, the
  command, the consumer.
- **`review`** — a review, audit, scan, self-check, or reading pass went
  looking and found it. Nothing was blocked.

These rules keep the class honest:

- **The class is evidence, not a severity rating.** "It would break X" is
  `review`. A `review` finding can be critical, correct, and urgent and is
  still `review`. Do not promote one by arguing about its impact.
- **A repro you built to prove your own hypothesis is still `review`.** Every
  filed finding carries a reproduction, so "a command that failed" cannot be
  the test — it is true of both classes by construction. `real-use` requires
  the break to have happened in the project's own work, before and independent
  of the investigation that found it.
- **`real-use` outranks every `review` finding in the same queue.** It is
  never deferred behind one, and it is what a fresh session picks up first.
- **Name the source project, not the session.** The project that generated
  the finding is the one whose work surfaced it, which is often not the
  repository that owns the fix.

## 4. Search before filing

Search both issues and pull requests, open and closed:

```bash
gh issue list --repo OWNER/REPO --state all --search 'distinctive terms'
gh pr list --repo OWNER/REPO --state all --search 'distinctive terms'
```

- Open matching issue: add evidence in a comment.
- Open matching `review` issue you have now hit in real use: add the
  `real-use` evidence as a comment **and upgrade the `Origin:` line in its
  body** by the mechanic in §6. A review finding that reproduced in a real
  project is no longer a review finding. The upgrade is a write to an entry
  this session may not own — it needs the same authority as filing.
- Closed matching issue with a recurrence: file a new regression and cross-link.
- Matching PR already fixes it: link the PR instead of filing another issue.

## 5. Body contract

The issue or backlog entry carries the analysis itself:

```markdown
## Source
Origin: real-use | review
Project: <the repository or consumer that generated this>
Trigger: <the run, PR, command, or session where it surfaced>
What it blocked: <concrete impact, or "nothing — found by looking">

## Summary
One falsifiable statement of the defect and impact.

## Reproduction
Exact command, input, environment, and `file:line` evidence.

## Blast radius
What was inspected or executed, what is affected, and what is not.

## Why diagnosis was difficult
The misleading signal, silent failure, or interaction that hid the cause.

## Fix shape
A bounded implementation direction, including constraints.

## What is not broken
Nearby behavior verified as unaffected.
```

`Origin:` is the priority signal that travels to every tracker. On a file
backlog it is the only one: record it in the entry and do not invent a
labelling convention the repository has not declared.

Move existing analysis without contracting it. Do not replace evidence with a
pointer to chat, scratch, a local path, or an inaccessible artifact.

## 6. Safe GitHub publication

Use stdin as a body file, never as a literal body argument:

```bash
gh issue create --repo OWNER/REPO --title '...' --body-file - <<'EOF'
...
EOF
```

For a comment:

```bash
gh issue comment N --repo OWNER/REPO --body-file - <<'EOF'
...
EOF
```

Read the write back before reporting success:

```bash
gh issue view N --repo OWNER/REPO --json body --jq '.body | length'
```

A URL or exit code alone is not proof that the intended body published.

When step 1 confirmed write authority **and** the repository declares a
priority label, apply that label to a `real-use` finding so it sorts:

```bash
gh issue edit N --repo OWNER/REPO --add-label '<priority-label-from-step-1>'
gh issue view N --repo OWNER/REPO --json labels --jq '.labels[].name'
```

The label name is whatever step 1 found, not a fixed string. Read it back from
`gh issue view`, never from `gh issue list --label`, which reads a lagging
index and reports a state that is already stale.

To upgrade an existing issue's origin (§4), rewrite only its `Origin:` line.
`--body-file` replaces the **whole** body, so fetch the body first or the edit
discards the original analysis:

```bash
BODY=$(mktemp)
gh issue view N --repo OWNER/REPO --json body --jq '.body' > "$BODY"
# change only the Origin: line inside the ## Source block, then:
gh issue edit N --repo OWNER/REPO --body-file "$BODY"
gh issue view N --repo OWNER/REPO --json body --jq '.body' | head -6
rm -f "$BODY"
```

An issue filed before this convention has no `## Source` block and no
`Origin:` line to rewrite. Prepend the block rather than editing a line that
is not there.

## 7. Report

Return the origin class, the source project, the owner, the destination, the
issue or entry identifier, and the read-back result. If publication was not
authorized, return a complete ready-to-file draft — `## Source` block included
— and state exactly which approval is missing.
