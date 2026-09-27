# GitHub Actions deep-review checklist

The knowledge that makes a CI review find real bugs instead of generic lint.
Lens 1 and 2 agents read this file themselves (routed via `lens-briefs.md`);
the dispatch prompt only names it — never paste sections into a brief. A reviewer who starts already holding these patterns
doesn't burn its budget rediscovering GHA semantics — and doesn't miss the bug
that hides behind the semantics it never learned.

## Table of contents
1. Reusable-workflow topology (read first — everything else depends on it)
2. Trust boundary & `pull_request_target`
3. Untrusted-input injection
4. Action pinning
5. Least privilege & token scope
6. Auto-merge / label bypass
7. Fork-PR token downgrade
8. Silent-failure patterns
9. Concurrency & triggers
10. Secrets

## 1. Reusable-workflow topology — read first

A `workflow_call` reusable has **no `on:` trigger of its own that fires it** —
the trigger lives in the **consumer's caller workflow**. This single fact
reframes half the review:

- A bug in "which events fire this" is a **caller-template** bug
  (`install/templates/workflows/*.yml`), *not* a bug in the reusable
  (`.github/workflows/*.yml`). Point fork-safety, trigger, and `paths:`
  findings at the caller.
- The reusable's `permissions:` is a **ceiling the caller can't exceed** — if
  the caller's repo default is `read`, the reusable's `write` request causes a
  `startup_failure`. Check both layers.
- `secrets: inherit` in the caller is what makes the reusable's
  `secrets.FOO` resolve. A reusable that reads a secret the caller doesn't
  inherit silently gets empty string.
- **Source-vs-template drift:** the repo's own `.github/workflows/foo.yml` and
  the shipped `install/templates/workflows/foo.yml` should agree except for
  deliberate public/private variance. Diff them.

## 2. Trust boundary & `pull_request_target`

`pull_request_target` runs with the **base repo's secrets and a write token**,
against the **base ref's workflow definition** — but the PR is from a
potentially hostile fork. The lethal mistake: checking out and executing
**PR head code** under that privileged context (RCE with your secrets).

Safe pattern to confirm: the workflow reads only PR **metadata/diff**, never
checks out or runs head code; or it splits into a disposable "trust decision"
job (metadata only) that gates a privileged job. Flag any
`actions/checkout` with `ref: ${{ github.event.pull_request.head.sha }}` under
`pull_request_target`.

## 3. Untrusted-input injection

Any `${{ github.event.* }}` value an outsider controls —
`pull_request.title`, `.body`, `.head.ref`, `issue.title`, `comment.body`,
commit messages — interpolated **directly into a `run:` shell block** is
CVE-class shell injection. `${{ inputs.* }}` on a `workflow_call` reusable is
consumer-controlled, so lower-trust but still injectable if a consumer wires it
to event data.

Safe pattern: env-var indirection — `env: TITLE: ${{ … }}` then `"$TITLE"` in
the shell (GHA sets it as a real env var, no re-parsing). Flag every raw
`${{ … }}` inside `run:`.

## 4. Action pinning

Every non-first-party (`actions/*`, `github/*`) action **must** pin to a full
40-char commit SHA, not a tag — a tag is mutable and a compromised upstream can
repoint it. This matters most for actions that **mint tokens or touch secrets**
(e.g. `create-github-app-token`, deploy actions).

**Verify the SHA is real.** Research and search snippets fabricate
plausible-looking SHAs. Confirm with
`gh api repos/<owner>/<repo>/git/refs/tags/<tag> --jq '.object.sha'` before
trusting one. `actionlint`'s "Unable to resolve action" diagnostic is the
canary for a fabricated pin.

Also flag: `npm install -g <pkg>` / `pip install <pkg>` / `curl … | bash`
without a version pin or checksum — same supply-chain surface, run as root on a
runner where secrets are in scope.

## 5. Least privilege & token scope

- Top-level `permissions: write-all` (or a broad default with no per-job
  narrowing) is a smell. Prefer `permissions: {}` at top level + minimal
  per-job grants.
- A job with **no** `permissions:` block inherits the workflow/repo default —
  often broader than it needs. Flag jobs that mint tokens or merge while
  running under an unscoped default.

## 6. Auto-merge / label bypass

Trace the **full** path from trigger → author/trust check → label check →
merge. The classic holes:

- A **label** an ordinary collaborator can self-apply is treated as
  authorization (e.g. hand-apply `approved` → enforcer merges). Labels are
  writable by anyone with triage; they are not an auth signal unless the label
  *write* is itself gated.
- An **enforcement check that is INERT** (returns success when unconfigured)
  combined with a downstream step that treats `mergeStateStatus=CLEAN` as
  sufficient → merge with no real review during the install-order window before
  the check becomes required.
- **Arm-then-push TOCTOU:** native auto-merge armed at HEAD1 merges HEAD2 after
  a push if the review gate isn't a *required branch-protection check*. The
  only real fix is the required-check, not workflow logic.
- **Multi-label combinations:** a "skip review" label + an "approved" label
  together may satisfy a carry-forward path that neither alone would.

## 7. Fork-PR token downgrade

On `pull_request` from a **fork**, `GITHUB_TOKEN` is **read-only regardless of
the `permissions:` block**. So a caller using `on: pull_request` for a job that
needs write (labeler applying labels, SARIF upload for CodeQL/gitleaks) **fails
on fork PRs**. If that check is required, fork PRs become unmergeable. Options:
`pull_request_target` (only if no head-code execution), or keep `pull_request`
and `if:`-skip the write step on forks, or split internal/external variants.
Weigh the security cost each way — `pull_request_target` on a scanner that
needs to see PR code defeats the scan's purpose.

## 8. Silent-failure patterns

These make a check *look* green while doing nothing:

- **`exit 0` in a `run:` step ends the STEP, not the JOB.** Subsequent steps
  still run. If a later step is gated on an *unset* output from a *skipped*
  earlier step, `'' != 'true'` is TRUE → it runs anyway. (This exact chain
  fired a whole pipeline on cron when only a reconcile step was meant to.)
- `|| true` / `continue-on-error: true` on a line that gates real behavior —
  swallows the failure that was supposed to block.
- Shell scripts without `set -euo pipefail` (or a documented reason) — an
  unset var or failed pipe segment passes silently.
- `grep` in a boolean whose *absence* of match is silently ignored.
- `if:` using `always()` where `success()` was meant; string comparisons with
  quoting bugs that always evaluate true.
- A retry loop that captures `2>&1` and then parses the blob as JSON — mixed
  stderr corrupts the parse on the first transient retry.

## 9. Concurrency & triggers

- PR-check workflows want `concurrency: { group: …-${{ github.ref }},
  cancel-in-progress: true }`. Missing → wasted runs + ordering races. A
  **global** group (no ref/PR key) serializes everything — sometimes
  intentional, often a bug.
- `push` on all branches when tags should be excluded; missing
  `paths:`/`paths-ignore:` causing runs on irrelevant diffs.
- `workflow_run` triggers must not blindly trust artifacts from the triggering
  run.
- Reusables should set `timeout-minutes` (default cap is 360 = 6h of a wedged
  CLI idling).

## 10. Secrets

- Never echoed into logs; never passed to a third-party action without cause.
- `secrets.FOO` is **not** available in a step-level `if:` — only in job `env:`
  or `with:`. Code that gates a step on secret presence must hoist it to
  job-level `env: PRESENT: ${{ secrets.FOO != '' && '1' || '' }}`.
- A minted installation token should be scoped to the single repo and expire at
  job end; confirm it's never logged.
