# CI & Autonomous Change-Integration Standard

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-30 |
| Author | Framework Maintainer |
| Framework Version | 0.77.0 |

Engine-agnostic rules for continuous integration and autonomous merging of
reviewed changes. This standard fixes the integration topology the SDD layers
leave unspecified: how verification is staged between the author's workspace
and the shared integration branch, and under what authority reviewed changes
merge without a human in the loop.

Platform bindings (runner types, workflow files, branch settings, CLI
commands) are NOT specified here — each consumer declares them in its
adaptation profile (`ADAPTATION.md`). What is specified here is the
invariant shape every binding must satisfy.

## 1. Scope and non-goals

This standard governs the path from a finished change to its integration
into a shared branch. It applies at two review points:

- **Proposal review** — a CHG (or equivalent change record) in `Proposed`
  state, before gate approval.
- **Integration review** — a merge request targeting the shared integration
  branch, before merge.

It does NOT govern SDD layer content (BRD through EVAL templates are
untouched), promotion beyond the integration branch (release gating stays
human-controlled per project policy), or fiduciary/spend authorization
(which never derives from review verdicts).

Terminology: "integration branch" is the shared branch agents merge
reviewed work into (often `dev`); "merge request" is the platform's review
unit (often called a pull request). "Required check" is any verification
the branch policy mandates before merge.

## 2. The six invariants

### Invariant 1 — Single unified verification harness

A project maintains ONE executable verification suite shared by the
author's workspace and the integration pipeline. Maintaining disjoint
harnesses — a lightweight local suite plus a separate submission suite —
is prohibited: divergent doubles produce false-green escapes when the
suites disagree about what "passing" means.

Concretely: the same test entry points, the same static checks, and the
same secret scans run locally and remotely. Routing (which subset runs
where — see Invariant 3) selects subsets of the one suite; it never
selects a different suite. Verification doubles that bypass real code
paths (in-memory fakes standing in for real services where the contract
requires the real behavior) are forbidden in both halves.

### Invariant 2 — Concentric verification latency budgets

Verification is staged in concentric tiers with latency ceilings so fast
feedback stays fast and slow assurance stays out of the inner loop:

1. **Static tier (seconds).** Linters, secret scans, hygiene, and fast
   stateless unit tests. Runs on every edit or pre-commit.
2. **Integration tier (under a minute).** Full unit suites including race
   detection, stateful integration tests, and headless service checks.
   Runs before a merge request is opened.
3. **Promotion tier (minutes).** End-to-end journeys, vulnerability scans,
   and migration dry-runs. Runs at promotion out of the integration
   branch, never as a per-edit gate.

Each consumer pins its own ceilings in its adaptation profile; the
invariant is the three-tier shape and the ordering (static < integration
< promotion), not the exact numbers.

### Invariant 3 — Required checks report conclusively (anti-deadlock)

Every check the branch policy requires MUST report a conclusive pass/fail
verdict on every merge request. A required check that silently does not
run — because trigger scoping excluded the changed paths, because the
pipeline was skipped, or because the verdict was never posted — deadlocks
the merge request: the policy waits for a status that will never arrive.

Therefore:

- Trigger scoping MUST NOT silently drop required checks. If a pipeline
  narrows execution by changed paths, the narrowing happens INSIDE the
  pipeline (per-job routing with an explicit fast-pass verdict), never at
  the trigger level where the platform reports "never ran".
- Every required check context posts either a full-suite result (paths
  impacted) or an explicit fast-pass success (paths not impacted,
  typically in seconds). "No verdict" is never a legal outcome.

### Invariant 4 — Two-pass independent review before autonomous merge

A merge request merges without human approval only after two review
passes, both recorded on the request:

- **Pass 1 — author self-review.** The author runs the static and
  integration tiers, reads the full diff for scope hygiene (no stray
  files, no leftover debug output, no temporary doubles), and fixes
  findings before proceeding.
- **Pass 2 — independent judge.** An evaluator with fresh context (a
  separate agent instance or a distinct judge persona — never the author
  re-reading its own work) reviews ONLY the diff, the task requirements,
  and the acceptance criteria. The author's internal reasoning is never
  part of the judge's input. The judge evaluates correctness, real
  verification (no bypassed tests), governance conformance, and safety
  boundaries, and returns PASS, REVISE (concrete defects), or BLOCK
  (fundamental mismatch — escalate to a human).

Fix-before-merge: any finding from either pass is fixed and re-verified
before merge. No request merges with unresolved review findings, and no
verification step is bypassed to reach green. The two passes PLUS the
required checks (Invariant 3) constitute the technical verification
authority for autonomous merge — they never confer out-of-scope
architectural, fiduciary, or spend authority.

Relation to existing review machinery: this loop satisfies the
`pre_merge` independent-review gate (`REVIEW_REMEDIATION_FLOW.md`,
judge ≠ generator) and may reuse layer review crews (`REVIEW_TEAM.md`).
"Conflict resolution" in `REVIEW_TEAM.md` means reconciling disagreeing
lens verdicts — a different concept from merge-conflict authority
(Invariant 5). The terms MUST NOT be conflated.

### Invariant 5 — Merge-conflict authority classes

When the integration branch advances under a queued merge request, the
request may become unmergeable and its merge automation disarmed. Agents
hold standing authority to restore mergeability ONLY within the
deterministic class:

- **Class 1 — deterministic/additive.** Mechanical conflicts resolvable
  without judgment calls: appended registry rows, changelog entries, or
  test lists; adjacent independent edits; non-overlapping additions.
  The agent integrates the branch (history-preserving merge — history
  rewriting that invalidates already-published commits is prohibited),
  keeps both valid additions, re-runs the static and integration tiers
  locally, pushes, and re-arms merge automation (which the platform
  disarmed on conflict — re-arming is mandatory, not optional).
- **Class 2 — semantic/architectural.** Incompatible behavior, conflicting
  schema migrations, delete-vs-modify, security-policy collisions, or any
  conflict where re-verification fails and cannot be remedied in one
  attempt. The agent aborts the integration immediately, leaves the
  request unmerged, and escalates to a human with the conflicting diff.

Class membership is decided per conflicting file; a single Class 2 file
escalates the whole request.

### Invariant 6 — Anti-blind closure

A merge request that resolves a tracked issue MUST link the issue from
its description using the platform's closing keyword, so the platform —
not human memory — owns the linkage. Issues are never closed by hand
without a record. Upon confirmed merge, the author posts a closure report
to each resolved issue thread: what was built, the code manifest, and
the verification evidence (tiers run, review passes, required checks).
An issue closed without this report is reopened.

## 3. CHG lifecycle harmonization

The framework's CHG governance defines no numbered step lifecycle, so
donor formulations in terms of "CHG Step #6" do not port literally. The
mapping is:

- Donor "proposal review" (author + judge passes on a `Proposed` change
  record) maps to framework gate approval: the Pass 1 / Pass 2 evidence
  is attached to the change record before the gate approver signs.
- Donor "implementation PR review" maps to integration review above:
  Pass 1 + Pass 2 + green required checks, then merge.

No step numbering is introduced into CHG governance by this standard.

## 4. Pre-merge verification and post-merge closure discipline

- Pre-merge: the author re-verifies the request head (not a stale local
  state) — static + integration tiers green, both review passes
  recorded, required checks conclusive — immediately before merge is
  armed. A previously green request whose base advanced re-verifies
  after integration (Invariant 5).
- Post-merge: the Invariant 6 closure report is posted promptly after
  the platform confirms the merge. The report cites the merged commit,
  not the pre-merge head.

## Cross-references

- `REVIEW_REMEDIATION_FLOW.md` — the `pre_merge` independent-review gate
  this standard's Pass 2 satisfies.
- `REVIEW_TEAM.md` — lens crews reusable as Pass 2 judges; its
  "conflict resolution" (lens-verdict reconciliation) is disjoint from
  Invariant 5 (merge-conflict authority).
- `DEFINITION_OF_DONE.md` — human-in-the-loop tiers; autonomous merge
  under this standard never overrides them.
- `ADAPTATION.md` — where consumers bind these invariants to runners,
  workflows, branch policies, and latency ceilings.
- `CHG_REQUEST_FLOWS.md` — F3/spec vehicle class authorizing this
  standard (framework self-change).
