# Lens briefs — fixed dispatch prompts for the five lenses

Shipped templates so briefs are deterministic, not re-authored per run. The
orchestrator sends each lens agent a 3-line dispatch prompt (see SKILL.md)
naming this file and the section to follow; the agent reads its section here.
Placeholders the dispatch prompt must supply: the ARTIFACT under review, the
GOAL (ship / tag / elevate / roll out), and the lens's FILE LIST.

**Each lens has a generic hunt list that applies to any artifact; some add a
domain block for one kind.** Work the generic list always, and a domain block
only when the artifact is that kind. If your artifact matches no domain block
here and no checklist in `references/`, **say so in your report** — a missing
checklist is a known gap to name, not something to improvise around.

**Read-only, all lenses.** You are reviewing an artifact, not repairing it:
read, grep and glob only — do not edit, write, or run anything that mutates the
tree, even to demonstrate a fix. Sketch fixes in prose instead. All five lens
agents are held to this by their frontmatter (`tools: Read, Grep, Glob`), which
is the enforcement; the rule is restated here because it also tells you what to
do instead. A docs lens that "helpfully" rewrites the docs it was dispatched to
judge has destroyed the evidence for the synthesis step, and done it while the
other four lenses were still reading.

Common contract (all lenses): return a ranked findings report — each finding
with `file:line`, a one-line defect, a **concrete failure scenario** (inputs →
wrong outcome; "unpinned action" is a category, "hostile tag ships code that
exfiltrates the minted App token" is a finding), and a fix sketch. Close with
a lens-local verdict (BLOCKER / SHIP-WITH-FIXES / READY) and 2-3 **strong
positives** (correct patterns synthesis must not undo). Cap ~1500 words;
prefer signal over completeness. Your final text is a raw report for
synthesis, not a human-facing message. Do not file issues from a lens — the
orchestrator owns promotion of surviving findings via `submit-feedback`
(SKILL.md step 5).

## Lens 1 — Security

Hunt, in your FILE LIST only:

- **least privilege**: what credentials/permissions does this grant, and is
  each one needed? Default scopes that were never narrowed
- **untrusted input reaching a privileged path**: anything an outsider controls
  (titles, branch names, labels, request bodies, filenames) interpolated into a
  command, query, path or template
- **credential handling**: secrets echoed, written to artifacts/logs, or
  reachable from a less-trusted context than the one that owns them
- **supply chain**: unpinned or mutable-tag dependencies; a pin that doesn't
  match the tag it claims
- **authorization bypass**: can an unprivileged actor reach a privileged
  outcome — skip a gate, cause a merge or deploy, escalate via a side door?
- **blast radius of a stolen credential**: what can it do, and for how long?

**If the artifact is GitHub Actions**, first read
`github-actions-review.md` — the file next to this one (auth, tokens, triggers), then add:
`permissions:` blocks and default token scope · `pull_request_target` misuse and
fork-PR token abuse · third-party actions pinned by tag rather than SHA ·
auto-merge / label bypass (who can add a label, who can approve) · token-minting
flows.

## Lens 2 — Correctness

Hunt, in your FILE LIST only:

- **silent failures**: an error path that returns success — swallowed
  exceptions, `|| true`, ignored exit codes, a "continue on error" that masks a
  required gate, unquoted shell variables
- **conditions that never fire or always fire**: filters, guards and
  truthiness bugs; the check that looks like a gate and is a no-op
- **ordering and concurrency**: races, deadlocks, retries that double-apply,
  partial failure leaving inconsistent state
- **dependency graphs**: a downstream step that runs — or is skipped — when its
  upstream did not do what its name implies
- **source-vs-copy drift**: does the installed, vendored or generated copy still
  match what it was generated from?
- **the rollback path**: if this fails halfway, what state is left behind?

**If the artifact is GitHub Actions**, first read
`github-actions-review.md` — the file next to this one (trigger semantics, silent failures), then
add: event/path/branch filters · `workflow_call` vs `workflow_dispatch`
confusion · `exit 0` ending a step rather than a job · `set -e` absent from
multi-command `run:` blocks · `always()` swallowing cancellation · `needs:`
chains skipping verification on partial failure · concurrency groups and
cancel-in-progress.

## Lens 3 — Docs

Hunt, in your FILE LIST only:

- adopter cold-start: can a new user follow the docs to a working result
  without tribal knowledge? **Enumerate every undocumented prerequisite** —
  credentials, installs, access grants, environment assumptions
- version staleness: docs citing a version, tag or endpoint that is no longer
  current
- dead refs: files, anchors, decision IDs, flag and option names that do not
  exist
- documented interface vs actual: names, defaults and signatures in the docs
  against what the artifact really exposes
- cross-doc consistency: README vs CHANGELOG vs install/upgrade guide telling
  different stories

## Lens 4 — Portability

Read as a deployment engineer would: hold a consumer in mind whose environment
differs from the author's in one respect — runtime version, OS, network
position, tier, an existing local customization — and ask which item below that
one difference breaks.

Hunt, in your FILE LIST only:

- language/stack assumptions (pinned runtime versions, package managers,
  directory shapes) that break a consumer who differs
- **environment variants**: does this behave differently by tier, visibility or
  network position — and is the difference handled or merely unnoticed?
  Anything reachable from one environment and not another
- **install vs update**: does re-running the installer clobber a consumer's
  local customizations? (A wholesale-replace update is the classic form.)
- **escape valves**: can a consumer opt out of a step, or override a default,
  without forking?
- hardcoded owner names, hostnames, absolute paths, single-machine assumptions

**If the artifact is GitHub Actions**, add: public vs private repo differences
in runner labels, secret availability and API reachability · whether an update
overwrites `runner_labels`, `permissions` or trigger blocks a consumer had
tuned.

## Lens 5 — Governance

Hunt, in your FILE LIST only:

- cross-doc reference integrity across CHANGELOG / ROADMAP / HANDOFF /
  DECISIONS: does every shipped behavior have its paper trail?
- freshness: does the changelog cover the diff being elevated? Does the
  roadmap reflect what this release actually delivers?
- plan-status accuracy: plans marked complete whose deliverables are absent,
  or shipped work with no plan/decision coverage
- decision-log coverage: policy choices embedded in workflows (auto-merge
  rules, review gates, skip labels) that no decision record authorizes
