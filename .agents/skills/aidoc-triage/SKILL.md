---
name: aidoc-triage
description: Triage GitHub issues on vladm3105/aidoc-flow-framework (the SDD framework repo) — validate claims live, assess priority, label, and post a triage note. Use when asked to triage, review, or scope issues, or before starting issue work.
---

# aidoc-flow-framework Issue Triage

> Framework-local instance of the triage workflow (repo-specific taxonomy, defect classes, and standing rules inline). The generic parameterized `issue-triage` is tracked for canon curation in `aidoc-flow-claude-agents-config#114`; this file stays in use regardless of that outcome.

Triage = assess + label + comment. Triage NEVER implements, closes, or rewrites history.

## 0. Preconditions

- `gh` authenticated (`gh auth status`). Work from the framework checkout, on `dev`, clean tree.
- Project memory holds standing rules and the session handoff — read them first (the repo `AGENTS.md` chain plus the memory store); they override anything stale below. If absent (fresh machine), proceed without it.

## 1. Fetch the issue live

```sh
gh issue view <N> --repo vladm3105/aidoc-flow-framework \
  --json state,title,labels,body,comments
```

Record: state, current labels, existing comments, every factual claim (file paths, line numbers, counts, error text). Filed line numbers rot fast — treat them as hints, never facts.

If the issue is already CLOSED, stop and report that with evidence — never triage a corpse, never re-triage into a closed thread.

### Review the full comment thread

The body is only the opening claim — read every comment, oldest first:

- Attribute each follow-up claim (correction, reproduction, "+1", proposed fix) to its author and date; verify load-bearing ones under §2 exactly like body claims.
- Corrections inside the thread supersede the body — triage the corrected claim, and name what it supersedes in the note.
- A prior triage note changes the job: post a delta per §4, never a duplicate full note. If an earlier verdict's evidence rotted (file moved, rule renumbered, VERSION advanced), say so with the fresh check.
- Stale or resolved sub-threads get one line in the note ("comment dated YYYY-MM-DD no longer reproduces — <fresh check>"), never an in-thread argument with the commenter.

## 2. Verify each claim against the tree (the core discipline)

For every claim, run the check; never trust the issue text:

- File/line exists? `grep -n`, `sed -n`, `git log --oneline -3 -- <file>`
- "X never held / never ran"? Full-history enumeration, e.g. `git log --format=%H dev -- <file>` + `git show <sha>:<file>`, or `gh run list`
- Counts ("70 errors", "39× spec")? Reproduce the measurement, note when your recount corrects the filing
- CI behavior? `gh pr checks <n>` / `gh run view --job=<id> --log-failed`

## 3. Assess

**Priority rubric** (a linter `error` severity is NOT an issue priority — judge by blast radius, not by the word in the rule)

- P0 — CI red/blocked merges, security exposure, data loss. On a live P0, say so prominently in the note and ask the owner whether to start the fix immediately — triage alone underserves it.
- P1 — governance/linter falsehoods that misroute agents (wrong severity, dead gates, phantom pointers), broken contracts
- P2 — real gaps with workarounds, unimplemented-but-documented rules, mirror/structural traps
- P3 — stale prose, nits, dead code with no callers

**Labels**: list first (`gh label list`), reuse — create only for a genuinely new class (`gh label create <name> --color <hex> --description "<text>"`). Compose triples: priority + area + class, e.g. `P1,linter` or `bug,P2,release`. Discriminators: `bug` = behavior contradicts its contract; `gap` = contract missing, nothing contradicts yet; `stale` = once-true prose/code the tree outgrew; `linter` = `sdd_doc_lint/` behavior, `docs` = prose only. Remove a clearly wrong label rather than stacking around it; when unsure, leave it and note the question in the comment.

**Cluster**: link related issues (`#700` before `#726`'s live subset; catalog `#715` before severity `#716`/`#722`/`#696`; behavior pairs `#713`+`#733`).

**Ownership — transfer when another repo owns it**: the test is ownership, not severity. If the defect lives in another repo (the CI canon `aidoc-flow-ci`, a sibling submodule, an upstream spec), the issue belongs THERE, not here. Record the ownership verdict in the triage note; execution per §8.

## 4. Post the triage note + label

Comments post as the owner (`vladm3105`), not a bot: factual, concise, no chitchat, no raw tool dumps — evidence, not transcripts.

If a triage note already exists, post a delta (`## Re-triage note (YYYY-MM-DD)` — what changed, per-claim verdict), never a duplicate full note and never an edit of the old one. Otherwise post one comment in this shape:

```md
## Triage note (YYYY-MM-DD)
- Priority: P1 · Area: linter
- Assessment: <what's actually wrong, with verification evidence>
- Cluster: <related issues + order>
- Next step: <smallest safe fix direction, incl. what NOT to touch>
- Suggested labels: `P1`, `linter`
```

Then apply labels directly — including priority (`gh issue edit <N> --repo vladm3105/aidoc-flow-framework --add-label "P1,linter"`). Triage owns the labels; suggesting without applying just moves the work. Do not close, do not implement.

## 5. Known defect classes (check first — they recur)

- **Phantom versions** (D-0078): a version cited but never held by `framework/VERSION`. Correct forward, never retag, never rewrite published records.
- **Forged consensus**: catalog/docs claim a guard exists — verify the test file exists and runs.
- **Mirror twins**: `governance/chg/` ↔ `layers/09_CHG/` must stay byte-identical; both sit 3-deep under `framework/`, so links must go up-three-then-down. Silent divergence is the failure mode — pin it.
- **Archive tier**: `framework/archive/**` is frozen history; repairs there carry no VERSION obligation and must not "fix" history.
- **Path-filtered required gates**: a required check whose workflow has `paths:` filters deadlocks PRs outside those paths — required feeders must trigger unconditionally.
- **Flaky pool**: `curl: (6) Could not resolve host: github.com` on trivy/dep-scan = DNS flake — `gh run rerun <run-id> --failed`, don't chase.
- **Outage window**: `error connecting to api.github.com` on `gh` reads — sleep with backoff and re-read fresh before acting; a badge seen in the window may be stale. Read-back discipline: a URL or exit code alone never proves a write — verify the field that matters (body length, labels, state).
- **Zero-job runs**: workflows failing instantly with zero jobs, no logs, and `gh run rerun` refusing ("cannot be retried") never executed — platform-side scheduling failure, not a code defect. Re-trigger with a fresh head, don't chase the "failure".
- **`pull_request_target` (ai-review)**: evaluates the BASE file — red on the PR by design; validate the caller contract mechanically instead.
- **Secrets hook**: `detect-secrets` flags `framework/archive/…` path literals — false positive, use `# pragma: allowlist secret` (repo convention).
- **Sync collateral**: `sync-version-refs` "files were modified" is its trailing `git add -u` staging earlier work — verify on a clean tree before chasing drift.

## 6. Write back to memory

Triage results must outlive the session: record the ordering decisions (what goes first and why), any new defect class with its Why/How-to-apply, and corrected counts in project memory (memory index + one file per topic). The next session starts from memory, not from re-reading the backlog.

## 7. Handoff to implementation (for later, not triage)

Batch docs-truthfulness separately from enforcement-behavior changes; behavior pairs need fixture matrices + negative controls. Vehicle: docs-only → C1 PATCH; tightened enforcement → C2 PATCH; both cut both CHANGELOGs with a pin sweep. Every PR body carries `Closes #N`; every commit carries the OPS-0065 self-review phrase. Branch protection on `dev` requires six contexts — never add a required check whose workflow can skip a PR.

## 8. Transfer to another repo (forwarding)

Only after §§1–4 are done on the local issue — the triage note carrying the ownership verdict posts here first, so the trail survives the move.

1. Cite the ownership evidence in the note (which repo owns the file/workflow, with `file:line` or workflow path).
2. Run the `approval-gate` check — transfer is an external action; never self-approve.
3. Transfer: `gh issue transfer <N> <OWNER/REPO> --repo vladm3105/aidoc-flow-framework`.
4. Read the transfer back (`gh issue view <N> --repo <OWNER/REPO> --json state,title --jq .`) — a printed URL is not proof it landed.
5. Record the move in project memory (§6) with the reason. The transfer itself closes out the local item — never close the local issue as completed, and never re-triage into the moved thread.

## Examples

- "Triage #733" → fetch, verify L005 vacuity against `chg_lint.py`, confirm F2 interplay, note P1 + `bug,framework,governance`, comment, label, stop.
- "Are #716/#722/#696 one PR?" → validate all three, judge docs-vs-behavior coupling and rollback risk, recommend the split before implementing.
- "Is #726 still valid?" → re-check each claim (scan green? protection set? links resolving?), report per-claim verdict, don't fix.
