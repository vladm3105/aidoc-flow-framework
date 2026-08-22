# CLAUDE.md — Project Memory

Persistent context for the **AI Doc Flow Framework**. Auto-loaded every
session. Keep it short and current.

Non-Claude agents (Codex, Gemini CLI, Copilot, Hermes) start at
[`AGENTS.md`](AGENTS.md) — the short cross-agent orientation. This file remains
the full working agreement; where the two disagree, this one wins.

## What this project is

The document-flow framework, delivered as **one engine-agnostic specification
(`framework/`) with two independent platforms**:

- **Platform A — Hermes AI** — MCP-server engine (`platforms/hermes/`).
- **Platform B — Claude Code plugin** — native Claude Code engine, no MCP
  (`platforms/claude-code-plugin/`).

The platforms share the `framework/` spec and nothing else. Both pass the same
shared conformance suite (`tests/conformance/`). The `framework/` spec defines
the 8-layer SDD flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code).

**Current state (as of 2026-08-16):** framework spec `0.41.1`, Claude Code plugin `0.25.0` (pre-1.0 preview, 52 skills = 50 active + 2 deprecated stubs), Hermes `0.12.1`. **YAML-BDD arc complete** (BDD authored as structured `scenarios:` YAML, not Gherkin-in-markdown) and the **CONSUMER-FEEDBACK P1 wave shipped**: element-level COV01/COV02 coverage (D-0039 — `REALIZING_LAYERS` map; catches orphaned requirement elements), manual-mode provisional IDs + normative SHA-256 algorithm (D-0040 — `id_state`/`PROV01`; element IDs are LLM-generated stable strings, NOT verified content-hashes), and first-class reuse / satisfied-by-reference (D-0041 — `reuse:` frontmatter; `REUSE01`/`REUSE02`). **PROVISIONAL-IDS-002 Phase 1 shipped** (D-0061/D-0062, spec `0.35.0`): the element-ID hash-input contract (normalization transform + BRD §7 extraction boundary) is formalized in `ID_NAMING_STANDARDS.md`, and `python -m sdd_doc_lint.rehash --check` verifies a canonical BRD's §7 FR IDs against it on demand (`IDDRIFT01` — advisory, opt-in, NOT in the default lint). Scoped "verifiable on demand," not "verified"; `rehash --fix` + all-layer extraction + corpus reconciliation are founder-decided Phase 2+. **ELEMENT-ID-LAYER-CONTRACT-001 shipped** (GD-09/D-0067, spec `0.39.0`): that transform had reached only `BRD-TEMPLATE.yaml`, so the re-specified algorithm is now **deleted** from the other four layer templates + three layer READMEs in favour of a cross-reference to `ID_NAMING_STANDARDS.md`; TDD gains the element-ID contract it never had; the inert `placeholder: "0000"` key is removed; `tests/conformance/test_element_id_layer_contract.py` locks all of it over `framework/layers/**` — **spec only** at the time, leaving the 19 plugin/Hermes authoring surfaces ([#342](https://github.com/vladm3105/aidoc-flow-framework/issues/342)) and the acceptance harness's second hash implementation ([#351](https://github.com/vladm3105/aidoc-flow-framework/issues/351)) open. **Both have since closed** (2026-07-26/27): the element-ID generator shipped as `python -m sdd_doc_lint.rehash --compute` (PR #363, D-0068), and the acceptance harness now delegates to that one implementation (PR #366). The guard that locks the negative property (`tests/conformance/platforms/test_no_inprompt_hashing.py`) scans less than its name implies and one unscanned surface still hashes — [#385](https://github.com/vladm3105/aidoc-flow-framework/issues/385) closed the plugin-SKILL and Hermes-reference halves, but `agent-skills/**/SKILL.md` is still reached by no root — so a green run of it is not evidence that no surface hashes. Plugin also ships full 8-layer playbook injection + preemptive saga driver across all 8 autopilots (SAGA-PARITY-001) + per-layer model-recommendation precheck (MODEL-PRECHECK-ROLLOUT) + review-quality calibration + necessary-upstream contract (NECESSARY-UPSTREAM-001) + threshold-resolution gate (TH-RES-001) + per-PR doc-of-record discipline (DOC_GOVERNANCE_CORE.md Principle 8). 8-layer development sequence complete. **Hermes has since advanced substantially** (from `0.7.3`): the `audit_threshold` raise-only gate (HERMES-ADAPT-ENFORCE-001), `.aidoc/profile.yaml` runtime consumption, and the opt-in bounded review→remediate→re-review **quality loop** (HERMES-REVIEW-LOOP-001 Phase 1, D-0063). **Residual arc: Hermes parity** — remaining plugin-vs-Hermes deltas + quality-loop Phase 2 (cross-invocation resume / G-R1, parallel-review lock fix), tracked in [`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md). The example corpus is regenerated wholesale after framework changes (so corpus-remediation findings are deferred to that regen). IPLAN ↔ iplanic integration deferred — see `plans/IPLAN-IPLANIC-DEFERRED.md`.

## Durable conventions

- **Submit only finalized work.** Any PR (plan or impl) must already
  have completed its review-and-fix cycles locally — what gets pushed
  is the *final* version, not a draft awaiting later amendment. The
  pattern of "submit, then review post-merge, then patch via amendment
  PR" is explicitly forbidden (see §"Development workflow" item 2 for
  plan-specific cycles; the same principle applies to impl PRs:
  self-review locally, fix, re-review, only then push). Amendment PRs
  to recently-merged work are a smell that the original PR was
  submitted prematurely. **Exception**: real new work that emerges
  AFTER a PR lands (a bug discovered during user-facing testing, a
  feature request that builds on the merged work, a follow-up phase)
  is legitimate as a NEW plan + impl pair — not as a retroactive
  "amendment" to plug gaps that should have been caught pre-PR.
- **Minimal-and-realistic plans.** A plan should be sized to the
  problem it addresses, not "a perfect plan to do everything." A plan
  that addresses N substantive issues should propose ~N fixes, not N
  speculative features bundled with them. **Signal that you've
  over-engineered:** Pass 1 review surfaces more gaps than the original
  problem had substantive issues, and most of those gaps trace to
  speculative scope (designs without a named issue) rather than the
  core fixes. When you catch this mid-draft, cut to the minimum
  sufficient design that catches every discovered issue, and park the
  speculative items as a one-line backlog enumeration in the plan's
  "Out of scope" section. Do NOT draft those speculative items here.
  The next iteration can build on this one if the deferred items
  actually surface in practice. *Origin:* REVIEW-CALIBRATION-001
  (2026-06-06) — 5 missed BRD review findings drafted as 9 designs
  (532 lines); Pass 1 surfaced 18 gaps, 14 of which originated from
  speculative scope; slim rewrite to 3 designs (315 lines) caught the
  same 5 findings and eliminated 14 of 18 gaps, dropping plugin SemVer
  from MINOR + framework MINOR (GATE-SPEC) to plugin PATCH alone.
- **Update docs of record per PR.** Every PR must keep the
  documents-of-record in sync with the change it ships — do not let a
  separate "doc-refresh" PR be the catch-up mechanism. The matrix of
  which docs to touch lives in
  [`CONTRIBUTING.md`](CONTRIBUTING.md#documentation-discipline--update-docs-of-record-per-pr).

  The discipline is enforced by **two pre-commit hooks** (no manual
  step required; both run automatically on `git commit`):

  1. **Mechanical doc-sync** (`scripts/sync-version-refs.sh`) — runs
     when a `VERSION` file changes (any of `framework/VERSION`,
     `platforms/<name>/VERSION`). Auto-propagates the new version
     string into the docs that quote it: `plugin.json`,
     `marketplace.json`, 52 × SKILL.md frontmatter, `README.md`,
     `platforms/<name>/README.md`, `docs/SKILL_AUTHORING.md`,
     `docs/PARITY.md` current-state row. Re-stages on its own;
     idempotent.
  2. **Semantic doc-reminder** (`scripts/check-docs-updated.sh`) —
      runs on every commit. When the staged change touches
      code/spec/skills but does NOT touch any document-of-record
      (CHANGELOG, ROADMAP, HANDOFF, …), prints a
      checklist of likely-stale docs. Warning-only; never blocks the
      commit. Contributor decides whether to update or proceed.

  The mechanical sync handles every doc whose update is deterministic
  (a version string changed; propagate). The semantic reminder
  handles every doc whose update needs human authoring (changelog
  entry text, handoff narrative, roadmap bullet). The framework spec
  contract documenting this discipline at the project-wide level
  lives in
  [`framework/governance/DOC_GOVERNANCE_CORE.md`](framework/governance/DOC_GOVERNANCE_CORE.md)
  Principle 8.

  *Origin:* PR #98 was a "catch-up doc-refresh" needed because the
  preceding 5 PRs did not each update CLAUDE.md / README.md /
  ROADMAP.md / root CHANGELOG.md / HANDOFF.md inline. The two-hook
  enforcement mechanism prevents that recurrence: mechanical sync
  makes the cheap updates invisible, and the reminder hook flags
  the expensive ones.
- **Never hand-edit example artifacts.** Files under `examples/<name>/docs/`
  and `examples/<name>/.aidoc/` are test fixtures for the plugin + SDD
  framework — the entire point of every cascade run is to prove the
  framework can produce, audit, remediate, and converge on those
  artifacts on its own. Hand-editing them (to fix STY03, add missing
  rules, rename IDs, etc.) bypasses the system under test: the
  artifact then represents a human-rescued output, not a framework
  output. Any subsequent claim "the framework works end-to-end" is
  invalid. When example artifacts need remediation, dispatch the
  appropriate framework skill (`doc-<layer>-audit` to surface the
  finding, `doc-<layer>-fixer` to apply a lens-validated patch). If
  a framework skill can't handle a class of remediation (e.g., the
  cascade bootstrap's lint-smoke gate blocks before the audit/fixer
  cycle runs), that is a **framework workflow gap** — fix the skill
  or the workflow, never the artifact. *Origin:* EARS-RT-001 +
  BDD-RT-001 (2026-06-08): hand-edited EARS-01.md across three
  iterations (SE-001 P1 abuse-case pairs, STRUCT-001 ID rename,
  STY03 trims) before the user stopped the pattern. The hand-edits
  contaminated the test fixture; the SE-001 + STRUCT-001 finds were
  the framework's own playbook calibrations working correctly, and
  the framework's fixer should have been the one applying patches.
- **The framework spec is the contract.** Engine-agnostic; carries no platform
  names or runtime code. Each platform declares the spec version it conforms to
  in `platforms/<name>/FRAMEWORK_SPEC_VERSION`, which must match
  `framework/VERSION`.
- **Conformance must stay green.** `tests/conformance/` is the runnable
  contract; never weaken a check to make it pass — fix the spec or the
  platform.
- **Single source of truth for templates (D-0013).** Platforms consume
  `framework/layers/<NN>_<X>/`; they never ship their own copies.
- **Tagging:** `docs/TAGGING.md` — release tags `vX.Y.Z` (project),
  `framework/vX.Y.Z`, `<platform>/vX.Y.Z`; `mark/<slug>` bookmarks. `VERSION`
  files hold bare SemVer; the tag adds the `v` + namespace.
- **Versioning streams are independent** (`docs/PROJECT.md` §2): project,
  framework spec, and each platform version separately.

## Development workflow (guidance)

Recommended flow for non-trivial changes — plan → review → implement →
verify → land:

1. **Plan** into `plans/` (start from `plans/PLAN-TEMPLATE.md`) before touching
   code.
2. **Two-cycle gap review (mandatory, BEFORE the plan PR opens)** —
   once a plan draft exists, it MUST complete at least **two full review
   cycles BEFORE the plan PR is opened**. Each cycle =
   *review to identify gaps → patch the plan to address every gap →
   re-review the patched plan*. The plan PR opens ONLY when a review
   pass has surfaced no new substantive gaps. Implementation begins
   ONLY after the plan PR has been merged.

   Record every cycle in the plan's `## Review log` with an ISO-stamped
   `Pass N` entry that lists the gaps found and how each was resolved.
   Cycle N+1 must always re-validate that cycle N's patches did not
   introduce new inconsistencies. Continue cycling until a review
   surfaces nothing; minimum is two cycles.

   **Corpus cross-check** (CLEANUP-PR-B item 5): if the plan changes a
   lint rule, `@`-tag semantics, registry shape, or playbook content,
   one of the review passes MUST run `python3 -m sdd_doc_lint
   examples/<NAME>/docs/` against the example corpus and verify zero
   *unexpected* findings (TH01/TRACE-RES-001/etc.). Catches drift
   between the plan's claims and the regenerated corpus's reality —
   the gap that bit NECESSARY-UPSTREAM-001 (PR #121 Pass 4 missed the
   example corpus and shipped 107 orphan `@prd:` tags into the cascade).

   **Empirical pass-count baseline** (CLEANUP-PR-B item 6, advisory):
   framework-level / cross-cutting plans typically converge in 4-5
   review cycles; per-layer rollout plans converge in 2-3. The "≥ 2"
   floor stays the rule; the 4-5 figure is an *upper-bound estimate*
   for cross-cutting work and is not normative — a plan that converges
   in 2 cycles still ships even if it's framework-level.

   **What is forbidden:**
   - Opening a plan PR with a draft that has not completed at least
     two review cycles.
   - Performing post-merge review of a plan and then opening
     "amendment" PRs against that plan to patch gaps that should have
     been caught pre-PR. Such amendments amount to merging unreviewed
     plans, which defeats the rule's purpose.
   - Starting implementation while gap-review cycles are still open.

   **Worked sequence:**

   ```
   draft plan → Pass 1 (self-review, fold in gaps)
              → Pass 2 (re-review, may surface new gaps from Pass 1 patches)
              → Pass 3 (codebase cross-check, fold in)
              → [continue if any pass surfaces gaps]
              → final pass surfaces zero substantive gaps
              → OPEN plan PR
              → review/merge
              → impl PR (with TodoWrite, code changes, verification)
   ```

   The rule exists because every plan touched in this repo so far has
   surfaced material gaps in the second-or-later pass that the first
   pass missed. Merging an under-reviewed plan and amending later
   wastes PR overhead and obscures the design history. All cycles
   happen against the draft, in the same branch, before PR submission.
3. **Implement**, updating the plan with ISO-stamped progress.
4. **Verify** — run the conformance suite + the platform's own tests; nothing
   is "done" until they pass.
5. **Land** — one logical change per commit, conventional prefix (`docs:`,
   `feat:`, `fix:`, `refactor:`, `chore:`); update `CHANGELOG.md` / `ROADMAP.md`
   as needed. **Submit only the final, reviewed-and-fixed version**
   (see §"Durable conventions" — no intermediate WIP submissions
   awaiting follow-up amendment PRs).

Record non-obvious choices in `plans/DECISIONS.md` (ISO-stamped).

## Session handoff

Sessions run in ephemeral containers — preserve continuity in the repo:

- Maintain `plans/HANDOFF.md` — progress, achievements, next steps, open
  questions; refresh at milestones and before any context compaction.
- Start each session by reading `plans/HANDOFF.md`.
- **Only committed + pushed work survives.** Commit messages must not contain
  model identifiers.

## Per-repo governance — this repo owns its own continuity

The `aidoc-flow` workspace is **multi-repo**. Each repo governs its own
activity tracking; cross-session continuity is per-repo. The durable
surfaces for **this** repo:

| Surface | Path (in this repo) |
|---|---|
| Live HANDOFF | `plans/HANDOFF.md` |
| TODO / backlog | **GitHub issues** — `plans/FRAMEWORK-TODO.md` is a retired tombstone; never add to it |
| Decisions log | `plans/DECISIONS.md` |
| Plans | `plans/` (per-initiative `<NAME>-PLAN.md` files) |
| Changelog | `CHANGELOG.md` |
| Roadmap | `ROADMAP.md` |
| *(repo-specific rows below — same table, optional)* | |
| Spec governance decisions | `framework/governance/DECISIONS.md` |
| Hermes per-package changelog | `platforms/hermes/CHANGELOG.md` |
| Plugin per-package changelog | `platforms/claude-code-plugin/CHANGELOG.md` |

**Never put any of these in `tmp/`** — `tmp/` is for transient working
files; nothing in it survives a context-clear or new session.
**Never centralize in the umbrella `aidoc-flow/`** — the umbrella holds
no dev; plans, decisions, and tracking live in the owning submodule (this
rule predates this section and remains binding).

A future session entered through **this** repo must find that repo's
state here, without needing to read other repos. Cross-repo coordination
(e.g., a multi-submodule initiative like IPLAN-0008) is captured in the
most-affected repo's `plans/`, references sibling repos by path, and
never relocates their state.

## Where things are

- `framework/` — the engine-agnostic SDD specification (layers, registry,
  governance). `framework/README.md` is the spec overview.
- `platforms/hermes/` — Platform A (MCP server).
- `platforms/claude-code-plugin/` — Platform B (Claude Code plugin).
- `tests/conformance/` — the shared conformance suite (framework + platform
  checks).
- `ROADMAP.md` — post-cutover Now/Next/Later roadmap (recently-shipped log + planned work).
- `CHANGELOG.md` — project-level changelog.
- `docs/PROJECT.md` — versioning, branching, conformance, change management.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/TAGGING.md` — git-tag policy. `docs/PARITY.md` — platform comparison.
- `plans/` — the active planning surface (per-initiative plans, audits, verify
  records, `DECISIONS.md`, `HANDOFF.md`). The backlog is **not** here: it is
  GitHub issues. `FRAMEWORK-TODO.md` remains only as a retired tombstone
  carrying the entry → issue mapping.

## Pre-migration history

This project was migrated from the pre-migration `ucx_framework` (v0.20.4).
The pristine pre-migration project is preserved on the protected, read-only
branch **`legacy-ucx-v3.2-read-only`**. Change management (the gated CHG
process) returns post-cutover to govern `framework/` spec changes — see
`docs/PROJECT.md` §6.

## GitHub operations

Use the **GitHub CLI (`gh`)** as the default for all GitHub operations — PRs,
issues, reviews, releases, repo queries — not the GitHub MCP servers
(`github-tt`, `github-vl`) or raw API calls. If `gh` is unauthenticated, run
`gh auth login` rather than falling back to MCP/API.

## Own-repo gaps — open a GitHub issue (supersedes GOV-TODO-ISSUE-SPLIT)

The sibling of the cross-repo rule below, for defects **this repo owns**. There
is now **one surface**: the tracker.

**Filing on the repo you are working in is not cross-repo** and needs no special
authorisation. Capture and publish are the same act: open the issue. Never keep a
local queue file shadowing this repo's own tracker — two records of one truth is
how they come to disagree, and it is why the previous file-based queue was
retired.

**An issue body carries the same evidence the cross-repo rule demands** (below):
reproduction at `file:line`, blast radius *run* rather than assumed, why it was
hard to diagnose, a suggested fix, and what is NOT broken. Same `--body-file -`
plus read-back verification. Same one-issue-per-defect granularity. **The merge
closes the issue** — the PR body carries `Closes #N`, one keyword per reference
(`Closes #A and #B` closes only `#A`). Never close by hand afterwards, and clear
the in-progress marker yourself: the merge does not.

**Never summarise a finding into an issue.** Move the analysis verbatim; a
re-derived finding silently contracts.

**Why the split was dropped.** `GOV-TODO-ISSUE-SPLIT` (2026-07-26) ran a two-
surface model: `plans/FRAMEWORK-TODO.md` as the triage queue, an issue only when
an entry cleared a three-test bar. Measured on 2026-08-15, that produced **48
open entries of which 41 had no issue** — findings visible only to a session
already inside this repo, which is the exact latency the rule was written to fix.
The queue file was retired, all **42** untracked entries migrated verbatim
(#466–#504, #505–#507), and the file left as a tombstone carrying the entry →
issue mapping. (#465 was filed separately, beforehand, and is not one of them.
42 rather than 41 because one entry was a bold pseudo-heading nested inside its
neighbour, so it had never been independently trackable.)

**The spec still names this file, and that is now a dead reference — tracked, not
waved away.** `framework/governance/DOC_GOVERNANCE_CORE.md:13` (Principle 9 — a
list item, not a `###` heading) names `plans/FRAMEWORK-TODO.md` **by path** as the
Tier-2 framework-repo surface, and `FRAMEWORK_FEEDBACK_LOG.md:55/59/87` does the
same, with `:51` carrying a consumer-facing instruction to add entries to it
directly. The census is **five** `framework/**` files, not two — those plus
`governance/REVIEW_TEAM.md:149`, `layers/02_PRD/PRD-TEMPLATE.yaml:353` and
`templates/framework-feedback-log.template.md:8` — and **four** ship vendored in
the plugin bundle. This repo's new rule also drops the
three-test bar and the two-surface split, which **GD-10** ratified at spec
`0.40.0` — so this is a divergence from the spec model, not merely a file rename.
Editing `framework/**` trips GATE-SPEC-E005 (version bump + fanout) and warrants a
GD entry, so it is deferred to **#508**, which owns it. Until #508 lands, this
section governs **for this repository's own gaps**; the spec remains the contract
for everything else.

## Cross-repo feedback — file it as a GitHub issue on the owning repo

When work here surfaces a defect **owned by another repo** — the CI canon
(`aidoc-flow-ci`), a sibling submodule, an upstream spec — **file it there as a
GitHub issue**. Recording it only in this repo's `DECISIONS.md` / `HANDOFF.md` /
`plans/` is not sufficient: those files are read by sessions entering *this*
repo, never by the people or agents who own the fix, so the defect stays latent
for every other consumer.

**When it applies.** The test is ownership, not severity: if the fix belongs in
another repo's files, it gets an issue there. A local workaround does not
discharge the obligation — ship the workaround *and* file the issue.

**What a filed issue needs** (all of these; a bare symptom report wastes the
owner's time):

- **Reproduction against their source** — `file:line` for the defect, and the
  command or run that exercised it.
- **Blast radius** — who else is affected. Check the fleet rather than assuming
  this repo is special; `gh secret list` / a `uses:` grep across sibling repos
  usually settles it in one command.
- **Why it was hard to diagnose**, when the symptom misnames the cause. This is
  often the most valuable part — it argues for a better error message, which is
  usually the real fix.
- **A suggested fix**, concrete enough to act on.
- **What is NOT broken**, when you checked and it was fine. It saves the owner
  re-deriving it, and it keeps the report honest.

**Granularity.** One issue per defect. Group only trivially-related items (e.g.
several doc-accuracy corrections) into one, and say so up front. Do not open an
issue for something already covered by an existing one — add the new evidence as
a **comment** on that issue instead.

**Then link it back.** Record the issue number in this repo's `DECISIONS.md` or
`HANDOFF.md` so a future session finds the upstream thread instead of
rediscovering the defect as a fresh bug.

**Verify what you published.** Use `gh issue create --body-file -` (and
`gh pr create --body-file -`). **`--body -` sets the body to a literal `-`** —
it exits 0 and prints a URL, so it looks like it worked. Read the artifact back:

```sh
gh issue view <N> -R <owner>/<repo> --json body --jq '.body | length'
```

*Origin:* CI-CANON-V2-001 (2026-07-25). Migrating this repo to `ci/v2.14.0`
surfaced five `aidoc-flow-ci` defects — filed as
[#305](https://github.com/vladm3105/aidoc-flow-ci/issues/305)–[#309](https://github.com/vladm3105/aidoc-flow-ci/issues/309).
The most serious (#305) had broken the AI review gate on **seven** repos for
~9 days behind a symptom (`no parseable verdict — fail-closed`) that named
neither cause nor owner; this repo's own `HANDOFF.md` had recorded a wrong
cause, and that misdiagnosis survived multiple sessions precisely because it
was only ever written down locally. All five issues were also initially
published **empty** via `--body -`, and were caught only because the founder
looked — hence the verify-what-you-published step.

## Unified CI — consume from `aidoc-flow-ci`

This repo's CI workflows (ai-review, composition, doc-gate, secret-scan,
markdown-lint, internal-links) **will consume reusable workflows** from the
**`vladm3105/aidoc-flow-ci`** library repo. The library is the
source-of-truth for CI logic shared across the aidoc-flow workspace and
future company projects; it ships independently semver-tagged
(`ci/v1.0.0`, `ci/v1.0.1`, …). Plan + charter live in
**`aidoc-flow-operations`** at
`ops/iplans/IPLAN-0017_unified-ci-flows.md` +
`ops/iplans/IPLAN-0017-CHARTER_aidoc-flow-ci.md`.

**Per-repo state (2026-07-29):** **public repo, but NOT purely
GitHub-hosted.** All **seventeen** `aidoc-flow-ci` call sites across sixteen
files are pinned `@ci/v2.16.0` (was eleven across ten until
CANON-PARITY-001 adopted five more, then #382 added `doc-maintainer.yml`;
`links.yml` holds two). Re-count rather than copying that figure —
`grep -rho 'aidoc-flow-ci/\.github/workflows/[^@]*@ci/v[0-9.]*' .github/workflows/ | wc -l`
for sites, `grep -rl 'aidoc-flow-ci/\.github/workflows/.*@ci/v' .github/workflows/ | wc -l`
for files. Pins:
CI-CANON-V2.16-001, plan `plans/CI-CANON-V2.16-MIGRATION-PLAN.md`,
PRs #374/#375, `plans/DECISIONS.md` D-0070 — which supersedes D-0066's
`@ci/v2.14.0` position from CI-CANON-V2-001, PRs #334/#335.

**Re-pinning and adopting are different dimensions, and only the first was
ever automated.** A `--repin` rewrites `uses:` strings; it cannot adopt a
canon surface this repo does not call, so an absent surface stays absent
through any number of green bumps. CANON-PARITY-001 (PR #378, D-0071)
closed that gap: `codeql` became a canon caller — which is what actually
closed [#373](https://github.com/vladm3105/aidoc-flow-framework/issues/373),
since canon's reusable already SHA-pins the actions — and `dep-scan`,
`sast-scan`, `trivy-scan`, `markdown-lint` were adopted. Scaffold new
surfaces with canon's `install/deploy-ci-wizard.sh scaffold <repo> <dir>
[wf…]`: it writes byte-exact callers at the pin into a scratch dir and
never commits, so it cannot clobber a customized caller the way `--update`
would. **The manifest's presence check is case-sensitive** — it lists
`.github/pull_request_template.md`, and this repo's equally-valid
`.github/PULL_REQUEST_TEMPLATE.md` reads as absent; do not conclude a
surface is missing from that alone.

**A canon bump is a migration, not a dependency update — do not leave it to
Dependabot.** It rewrites `uses:` lines and nothing else, so it can never
deliver a caller-**body** change and never notices a comment it falsified.
Both failure modes were live here: the eleven sites had drifted into **two**
tags because one caller was bumped by hand and a Dependabot group PR carried
five of the ten distinct reusables, leaving four behind. Use canon's
`--repin` — `CI_TAG=ci/vX.Y.Z bash install/install.sh <repo> --repin`, which
rewrites the tag string only; **never `--update`**, which replaces whole caller
bodies and would clobber this repo's
self-hosted `runner_labels_*`, `litellm_allow_insecure_http`, `secret-scan`'s
`config-path: .gitleaks.toml`, `docs-sync`'s `pull-requests: write`, and
`links`'s two-job split.

**The #329 concurrency allowlist is scoped by required-context, not by
ownership.** `pre-commit`, `conformance` and `acceptance` all carry it: a
cancelled required check is not success, and an untyped `pull_request` admits
`reopened`, which fires at the current head. The last two are locally owned and
call no reusable. **Seven local workflows still carry
`cancel-in-progress: true` and are exempt only because they feed no required
context** (`codeql`, `chg-gate`, `doc-review`, `hermes`, `plugin`, `labeler`,
`links`) — a snapshot, not a property. `acceptance` was exempt by that same
reasoning, defended by a comment arguing it was safe, until it became required
on 2026-07-27. **Any change that makes one of the seven required must take the
allowlist in the same PR.**

"Does it cancel?" is a **four**-way question, not two, and the shapes arrived
from different work: CANON-PARITY-001's adopted surfaces added two, and
`pin-currency-reader.yml` (#392) added the fourth. `markdown-lint` already ships
canon's `#329` allowlist (it is a required context *for other consumers*, and the
template is uniform), while `dep-scan`, `sast-scan` and `trivy-scan` carry **no
`concurrency:` block at all** — they never cancel, which is the safest state and
needs no allowlist. `codeql` keeps plain `cancel-in-progress: true`, which is why
it stays in the seven above.

**The fourth shape is `cancel-in-progress: false` under a fixed group, and it is
serialization — not an absent block written out longhand.**
`pin-currency-reader.yml:55-57` pins `group: pin-currency-reader` so that a
`workflow_run` and a concurrent `workflow_dispatch` cannot both find no open
issue and both create one. **Never re-derive it as "nothing to cancel, so
nothing to fix"** — that is verbatim the argument this repo uses to justify
carrying **no** `concurrency:` block at all, so a sweep reading it that way
deletes the block and reintroduces the duplicate-issue race. Rationale:
`plans/DECISIONS.md` D-0073 §7, and the workflow file states it at the block —
including the caveat that serialization is **not** a guarantee every upstream
verdict is read, since GitHub queues at most one *pending* run per group.

**Count the exemption by shape, not by filename:** absent block ≠ `#329`
allowlist ≠ bare `true` ≠ `false` under a fixed group.

Runner split — deliberate, do not "normalize":

- **`ai-review` runs entirely on the self-hosted single-use pool**
  (`["self-hosted", "ci-runner", "single-use"]`, **both** the trust and
  review jobs) per the PLAN-013 uniform-protected model. It has to: the
  LiteLLM proxy is host-local with no public or TLS listener, so a
  GitHub-hosted runner cannot reach it. Safe on a public repo because forks
  are never trusted, so a fork PR reaches only the no-PR-code trust job.
  The caller also sets `litellm_allow_insecure_http: true` — the bridge URL
  is `http://`, and canon's client refuses non-HTTPS without it.
- **`dep-scan` and `trivy-scan` also run self-hosted** — canon's PLAN-014
  uniform-protected model, adopted byte-exact. Safe on a public repo because
  the reusable's own fork guard (`if: …head.repo.fork != true`) skips fork PRs,
  so untrusted code never reaches the host; the label is canon's trust design,
  not a tooling requirement (both `curl` a pinned static binary). This means the
  pool now serves up to five jobs per PR against **two** slots — it
  self-replenishes (`ci-runner@.service` is `Restart=always`/`RestartSec=5`), so
  they serialize rather than starve the required `ai-review`.
- **`sast-scan` is the exception and must stay on `ubuntu-latest`.** semgrep
  installs into a `python3 -m venv` and the `aidoc-flow-runner` image ships no
  Python, so on the self-hosted pool it dies at *"ensurepip is not available"*
  before any findings logic — and `fail-on-findings: false` gates the verdict,
  not the install, so report-only does not keep it green. Filed as
  [aidoc-flow-ci#349](https://github.com/vladm3105/aidoc-flow-ci/issues/349);
  revert the override only once that lands.
- **Everything else stays on `ubuntu-latest`**, including the
  fork-code-executing lint callers (`links`, `pre-commit`) and `codeql`.

Four operational facts that cost a session when unrecorded:

- **`LITELLM_BASE_URL` must be the Docker-bridge address**
  (`http://172.17.0.1:4001/v1`), never loopback — jobs run inside a
  container, where `localhost` is the container. LiteLLM publishes host
  4001 → container 4000, and is a different service from `llm_router`.
- **`secret-scan` at v2 scans full git history** (`gitleaks git`), not the
  working tree (`gitleaks dir`). Validate locally with `git`, or a clean local
  run will still fail CI. Suppressions live in `.gitleaks.toml`. *(The rider
  that canon's own header comment "still claims `dir`" was true at
  `ci/v2.14.0` and is **no longer**. The scope change itself landed at
  `ci/v2.0.0` (CI-0016); what `ci/v2.16.0` fixed is the header that had gone on
  describing the old behaviour. Upstream `aidoc-flow-ci#307` is closed.)*
- **A `GITHUB_TOKEN`-triggered event creates no workflow run** (the documented
  exceptions are `workflow_dispatch` and `repository_dispatch`), which is why
  `labeler`'s and `ai-review`'s own label writes start nothing. Only a
  **human** or App-token label write reaches a `labeled` trigger. Measured on
  PR #375; do not reason about label-driven CI without it (D-0070).
- **Check-runs are retained alongside each other with the rollup keeping the
  worst, and a job skipped by `if:` does not degrade a **required** context that
  already succeeded at that SHA.** Measured on scratch PR #376, not assumed: a `skipped`
  `call / verify` alongside an earlier success left the PR `CLEAN`, while a
  `failure` and a later `success` for that context at one SHA left it `BLOCKED`.
  **So labelling cannot clear a red required check** — on this repo's branch
  protection; canon settled the general mechanism in `REPO_STANDARDS` §23.1
  (`aidoc-flow-ci#330`, closed). ⚠️ **Not tested: a required context whose
  *only* run at a SHA job-skips.** A workflow that never triggers at all is a
  different and worse case — it stays pending and blocks forever (D-0065).

### Local overrides shared — the foundational rule

GitHub Actions runs whatever's in this repo's `.github/workflows/*.yml`.
A shared workflow from `aidoc-flow-ci` only runs when this repo
explicitly calls it via `uses:`. So **local always wins** — by GitHub's
default, not by engineering.

Three override modes (preferred order):

| Mode | When | How |
|---|---|---|
| **Parameter override** | Change one knob (runner labels, label colors, human-approval count) | Edit `with:` block in the local workflow; keep the `uses:` call |
| **Full replacement** | Local logic genuinely differs from canonical | Drop the `uses:` call; write the local jobs/steps |
| **Add a custom workflow** | New check the shared CI doesn't have | Create a new `.github/workflows/<custom>.yml`; siblings the shared callers |

There is no merge/inheritance/diamond pattern — GitHub doesn't support
one. "Override" means this repo's workflow file is what runs.

### Drift detection — warning-only, never blocks

The `aidoc-flow-ci/sync/check-drift.sh` script (run as a pre-commit
hook or periodic GitHub Action) compares each workflow file against
the canonical template at the pinned `ci/vX.Y.Z` tag and reports any
diff as a warning. **Never blocks the commit or the PR.** Same shape
as the existing `scripts/check-docs-updated.sh` doc-currency
reminder — see "## Durable conventions" item 3 above. Contributor
decides: bring back to canonical, intentionally keep, or push the
divergence upstream as a new shared default.

### When this repo edits a shared workflow

If a change is broadly useful (every consumer would want it): open a PR
on `aidoc-flow-ci`, tag a new `ci/vX.Y.Z`, then bump this repo's `uses:`
pin in a separate PR. If the change is genuinely local: keep it in
this repo's `.github/workflows/` and accept the drift warning.

## Governance PR discipline (mandatory)

A **governance PR** is any PR that touches one of these surfaces, or that
supersedes a locked decision:

- `CLAUDE.md`
- `plans/DECISIONS.md` and `framework/governance/DECISIONS.md`
- **`plans/*-PLAN.md`**, plus the `plans/*-DESIGN.md` companions some
  initiatives carry (e.g. `LAYER-PLAYBOOKS-001-DESIGN.md` beside its
  `-PLAN.md`). The plan glob is a **suffix**: every plan here is
  `<NAME>-PLAN.md` per §"Per-repo governance" above, so the prefix form
  `plans/PLAN-*.md` matches only `PLAN-TEMPLATE.md` — no real plan at all.
  Sibling repos such as `aidoc-flow-operations` use `ops/iplans/IPLAN-*.md`.
- `.github/ai-review/` and `.github/workflows/ai-review.yml`

Two rules apply to every governance PR — no exceptions without explicit
founder OK and an audit-trail note in the commit message.

### Rule 1 — Small scope (≤3 doc surfaces per PR)

A governance PR touches **at most 3 distinct doc surfaces** in one PR.
If more surfaces need updating, **split into sequential PRs** — e.g.,
DECISIONS first → plan citing it → CLAUDE.md propagation.

**Reconciliation with the existing doc-currency rule:** Rule 1 does NOT
supersede doc-currency; it scopes how the rule applies. Each split PR
is a self-contained smaller change with its own affected docs fully
updated within that PR. Doc-currency applies per-PR-scope, not
per-overall-change.

### Rule 2 — Mandatory adversarial self-review before every push

Before `git push` on any governance PR, dispatch a code-reviewer agent
on the diff. Required focus areas:

- **Dead refs** — for every quoted path/file in the diff, grep and
  verify the target exists (or qualify as a forward-reference)
- **Supersession completeness** — when "supersedes X" appears, read
  X end-to-end and name ALL parts superseded vs ALL parts carried
  forward
- **Internal consistency** — every DECIDED / open / Status status
  matches across files in the diff

Fix every load-bearing finding **BEFORE push**. Skip only with explicit
founder OK + commit-message audit line (`Self-review skipped per founder
OK <reason>`).

**Origin:** operations 2026-06-23 (after 22+ ai-reviewer findings across
operations PRs #107-109 in one session). Full reasoning + formal record
in `aidoc-flow-operations` `CLAUDE.md` "Governance PR discipline" section,
plus `ops/DECISIONS.md` `OPS-0061`.

## AI agent auto-merge default (OPS-0062)

**Applies to ALL AI agents (Claude, Codex, Gemini, GitHub Copilot, etc.) —
not just one model.** For PRs the AI agent opens itself in this repository:

1. **Auto-watch + auto-merge when green.** After opening a PR, the AI
   watches the PR's check rollup until all checks complete. If
   `mergeStateStatus = CLEAN` AND all required checks are SUCCESS, the AI
   attempts `gh pr merge --squash --delete-branch` without asking the human
   for explicit per-PR authorization (the act of directing the AI to ship
   the work constitutes the merge intent). Stale-check recovery uses the
   documented patterns (label-cycle per `aidoc-flow-ci/docs/troubleshooting.md
   §15`; `--admin` flag only when authorized).
2. **Escalate to human at 10 attempts.** If the PR still hasn't merged
   after 10 distinct merge-or-recovery actions, the AI STOPS and requests
   human confirmation with a summary of what was tried, what's blocking,
   and next-step options.

**One attempt =** each distinct merge-or-recovery action: each `gh pr merge`
invocation, each `skip-ai-review` label-cycle (add+remove = one logical
action), each `gh run rerun`, each `gh workflow run` retrigger. Polling
(`gh pr view`) does not count. **Counter is per-PR cumulative, not
per-session.**

**Visibility — AI announces each merge attempt in-session.** Before each
`gh pr merge` / label-cycle / rerun, the AI emits a brief chat line
("auto-merging PR #N now"; "label-cycling PR #N attempt 3/10"). The rule
reduces per-PR PROMPT overhead, not VISIBILITY.

**Session-boundary:** the AI watches checks only while in-session. If the
session ends before checks settle, the PR stays OPEN; the next AI session
resuming the work picks up the counter (per-PR cumulative).

**Exceptions (AI never auto-merges these; always asks):**

- **🟡 / 🔴 actions per autonomy tiers** (see operations CLAUDE.md for the
  canonical autonomy-tier table; this repo inherits the same tiers via the
  governance discipline rollout).
- **Spec / governance tier PRs** (already excluded from auto-merge by the
  reusable `ai-review.yml` workflow's `tier=spec` check; AI must not
  bypass).
- **Cross-repo coordinated changes** — synchronized merges across
  repositories where ordering matters.
- **PRs that touch any governance surface named in the "Governance PR
  discipline" section above.** That list is the definition — **do not
  restate it here.** A second copy is how the two drift apart: this bullet
  used to carry its own enumeration, which wrote the plan glob as
  `plans/PLAN-*.md` (matching no real plan) and omitted `DECISIONS.md`
  entirely, so the exception silently under-covered what it was defined to
  cover.

**Human-opened PRs are unaffected** — the human controls merge timing for
their own PRs.

**Origin:** OPS-0062 (2026-06-27). Codified after a session shipping 12+
AI-opened PRs on operations where the per-PR "merge if it is green" prompt
added overhead without signal. Full reasoning + scope clauses + reconciliation
with the `auto_merge.repos` allowlist (server-side action of `ai-review.yml`)
in `aidoc-flow-operations` `ops/DECISIONS.md` OPS-0062.

**Deferred companion (not in scope of OPS-0062):** a reusable
`auto-merge-ai-prs.yml` GitHub Actions workflow on aidoc-flow-ci that serves
as a server-side enforcer. To be tracked in operations HANDOFF backlog;
queued post-current-tasks per founder direction.

## Multi-agent automated review (aidoc-flow standard — OPS-0065 + OPS-0067)

This repo follows the **aidoc-flow standard** for author-side AI-team multi-
agent review BEFORE push/commit. Note: this is the **AI-employees standard**
for internal review discipline; it is separate from the framework's own
spec-governance via GATE-SPEC / GD-NN. The canonical rules + diff-class →
agents table + parameterized prompt templates live in `aidoc-flow-operations`:

- **Rules:** `aidoc-flow-operations/CLAUDE.md` → "Multi-agent automated review
  (OPS-0065 — generalizes the CI ai-reviewer pattern to ALL internal flow)"
  section.
- **Prompt templates:** `aidoc-flow-operations/.claude/agents/review-prompts/`
  — diff-class skeletons (`workflow-yaml.md` / `governance-docs.md` /
  `docs.md` / `scripts.md` / `cross-repo.md` / `adversarial-judge.md` +
  `INDEX.md`).
- **Empirical default (OPS-0067):** 3-agent parallel dispatch + single fold
  cycle for ≤300-line diffs. Re-dispatch only on NEW load-bearing surfaces
  or structural pivots. Cap at 3 cycles per OPS-0066 circuit-breaker.
- **Standard scope:** all aidoc-flow workspace repos — this one included.

The CI `ai-review.yml` gate (merge-side) is unchanged; multi-agent review
strengthens the author-side review pattern.

**Skip discipline:** Stop using `SKIP_LOCAL_AI_REVIEW=1` indiscriminately
per OPS-0065. Acceptable cases: (a) mechanical content (pin bumps with no
logic edits); (b) AI-side review already done via dispatched agent (commit-
message audit-trail line names the agents + verdict); (c) explicit founder
OK per governance PR-discipline Rule 2.

**Framework-vs-AI-employees separation:** framework spec-governance (GATE-
SPEC ratifications, GD-NN framework decisions, etc.) has its own governance
gate documented in `GOVERNANCE.md`. This OPS-0065/0067 section covers only
AI-side dev-workflow review discipline (which agents are dispatched on a
diff), not framework spec ratification.

**Origin:** OPS-0065/0067 in `aidoc-flow-operations` `ops/DECISIONS.md`;
cross-repo rollout runbook at
`aidoc-flow-operations` `ops/inbox/2026-06-30_cto-platform_ops-0067-multi-agent-review-rollout.md`.

## Durable traps — do not re-derive these

Every entry below cost a session real time at least once. They are **facts about
this repo and its toolchain**, not status — which is why they live here and not in
`plans/HANDOFF.md`. The handoff is rewritten wholesale at every merge, so anything
durable parked there is re-verified, re-summarised, or silently dropped on each
regeneration; here it is written once and loaded automatically.

**The boundary:** a trap graduates to this section once it has settled (measured,
reproduced, and not expected to change). `plans/HANDOFF.md` carries only traps too
fresh to have settled, and never repeats one that is already here.

### Merging and CI mechanics

- **`call / verify` greps the commit body for a literal phrase**, and it is a
  *required* context — so a missing or paraphrased phrase blocks the merge. Exactly
  one of: `Multi-agent self-review per OPS-0065 (<agents>): <verdict>` or
  `Self-review skipped per founder OK — <reason>`. It is `grep -qF`; nothing else
  matches, and the phrase belongs in the **commit message**, not the PR body.
- **Stacked PRs: retarget the child before merging the parent.** Merging #357 with
  `--delete-branch` deleted #358's base, which **auto-closed #358**, and GitHub
  refuses to retarget a closed PR — it had to be rebuilt by cherry-picking onto
  `main`. Prefer branching each PR from `main` when the files don't overlap.
- **`Closes #A and #B` closes only `#A`.** The keyword is needed before *each*
  reference.
- **`report-only` protects the verdict, not the toolchain.** A `fail-on-findings:
  false` caller can still go red by failing *before* any findings logic runs — see
  `sast-scan` under § "Unified CI" for the concrete instance. **A report-only flag is
  never evidence that a new caller cannot fail.**
- **Never truth-test a `jq` scalar that can be absent — and do not pattern-match the
  failure string either.** `gh api …/contents/<missing> --jq '.name'` puts the full
  error JSON (`{"message":"Not Found",…,"status":"404"}`) on **stdout**; re-measured
  2026-07-30, it is *not* the bare string `null`, so even a guard written as
  `case "$n" in ''|null)` — which looks like it handles the documented form — reads a
  missing file as **present**. This has inverted a blast-radius finding twice: once
  from "no sibling repo adopts this" to "all seven do", and again to "10 of 10
  workspace repos call `standards-drift`" when the truth is **7 of 10**. **List the
  directory instead:**
  `gh api repos/<r>/contents/.github/workflows --jq '.[].name'`.

### Reading CI output

- **A downloaded log contains `##[warning]`, never `::warning::`.**
  `gh run view --log` renders the workflow command. On a log where `##[warning]`
  returns 22, `grep -c '::warning::'` returns **0** — so a grep-based reader written
  against the emitted form silently matches nothing.
- **Counting drift annotations: grep `::warning::drift-check:`, not `::warning::`.**
  A bare grep returns 12 for 10 annotations — `standards-drift.yml`'s canon header
  quotes the literal string, so its own drift body reproduces it twice. (Distinct
  from the trap above: this one is about the *annotation* text, that one about the
  *log* rendering.)
- **`check-standards-drift:` is a PREFIX, not a completion marker.** The drift script
  emits an opening `repo=… tier=…` header and a `cannot check <family>` warning per
  unreadable family under that same prefix — the first of them **24 lines ahead** of
  the pin-currency section, so a log truncated in that window still satisfies a
  prefix test. The terminal markers are the summary line
  (`check-standards-drift: N drift,`) and `check-standards-drift: coverage —`, the
  latter emitted by `emit_coverage` at normal termination *and* from every
  `stop_uncheckable` early exit. This shipped as a real silent-failure path and was
  caught in review, not by a test.
- **A measurement is dated to the canon version that RAN, not the one checked out.**
  Run `30257877863` executed `check-standards-drift.sh` at **`ci/v2.14.0`** (380
  lines) while the local checkout was `v2.16.0` (523 lines) — `emit_coverage` shipped
  in `v2.15.0` and does not exist in what ran. Cost most of a review cycle: a
  reviewer correctly derived a **23rd** warning from the v2.16.0 source and concluded
  the measured **22** was wrong. **Read the `adopted canon pin` notice in the run's
  own log before citing line numbers at it.**
- **The check-run annotations API truncates at 10 per annotation level, keeping the
  earliest — so it is not a substitute for the log when what you want is emitted
  late.** Check-run `89950624082` emitted **22** `##[warning]` lines and the API
  returned **10 warnings**; **none** of the ten `pin-currency:` lines survived, because
  they are emitted at the drift script's tail. Below the cap the API is complete and is
  the cheaper surface — **a level returning exactly 10 is the truncation signal; fewer
  than 10 at a level means that level is whole.**
  - **Verify with
    `--jq 'group_by(.annotation_level)|map({(.[0].annotation_level):length})|add'`,
    never bare `length`** — the response length is **11**, 10 `warning` plus 1
    `notice`, so a bare count reads as off-by-one and the trap gets discarded as false.
  - **"Earliest" is which annotations survive, not the order they come back in.** The
    response is sorted by *descending* `start_line`, so `.[0]` is the **last** survivor
    (measured: `.[0]` at line 88; the earliest survivor, line 79, is second-to-last).
    Check "keeps the earliest" against `.[-1]`, or it reads as refuted and a true trap
    gets discarded.
  - That surviving `notice` is also the evidence the cap applies **per annotation
    level**: a full 10 warnings did not crowd it out. **Per-step vs per-job vs per-run
    stays unattributable** from this measurement — the whole drift script is one `run:`
    step, so the three are indistinguishable here. Claim per-level; do not claim
    per-step.
  - The `22` is dated to `ci/v2.14.0` per the bullet above and **does not travel**;
    `v2.16.0` emits more, so the truncation conclusion holds a fortiori.
- **Canon's pin-currency check false-greens two ways, and one would make a reader
  close a tracking issue.** `check-pin-currency.sh:62` greps `@ci/v…` literally, so a
  **SHA-pinned** caller is invisible and it reports `all pins current ✅` — while the
  *fleet* path at `:71` **does** match `@<40hex> # ci/v…`, i.e. two paths in one
  script disagree. Second: if the `curl` of canon `main`'s `VERSION` returns an error
  page instead of failing, `ver_cmp` (`:39`) compares non-numeric fields under
  `2>/dev/null`, every comparison falls through to equal, and `:101` prints the same
  green. `:87` is the only validation there is — an emptiness guard — and an
  error-page body is non-empty. **Validate a resolved canon token against
  `^ci/v[0-9]+\.[0-9]+\.[0-9]+$` before trusting any verdict built on it.** Both were
  filed upstream by `PIN-CURRENCY-READER-PLAN.md` Task 3; cite `:39` + `:101` for the
  second, not `:87`.

### Local hooks and tooling

- **`tests/unit/` is executed by no hook and no workflow.**
  `.pre-commit-config.yaml:106` discovers `tests/conformance` only, and the workflows
  run `tests/conformance`, `tests/acceptance/deterministic`,
  `tools/sdd_doc_lint/tests` and Hermes' own suite; `pre_push_check.sh` invokes no
  `unittest` at all. So ~30 modules under `tests/unit/` (including
  `test_sync_scripts.py`) are **unguarded after merge** — a test placed there proves
  something once, locally, and never again. The registration shim is
  `tests/conformance/test_repo_scripts.py` — add new modules to its `REGISTERED`
  tuple. Wiring `tests/unit` into the existing `conformance` hook
  (`.pre-commit-config.yaml:104-106`) is reuse, not authoring.
  - ⚠️ **This bullet used to carry two wrong claims about the one runner that
    does exist; both are corrected here (2026-08-02), because each was reassuring
    in the wrong direction.** (a) It said `tests/scripts/test-plugin.sh:257`/`:302`
    "both end in `|| true`, so even the manual path cannot fail." **The `|| true`
    suppresses nothing.** The script sets `set -uo pipefail` with **no `-e`**
    (`:52`), `FAILED` is `declare -i` (`:114`), and `run()` increments it *before*
    returning (`:123-137`), which `:369-376` turns into `exit 1`. (b) It said
    "nothing calls that script" — **refuted by the umbrella.** The nuances matter
    more than the refutation: the umbrella **pins this repo at `0ffa153c`
    (2026-06-15)**, so *no* umbrella run is evidence about current `main`; and it
    reaches `tests/unit/` two ways — `release.yml:32` (this harness, `v*` tags) and
    `pr-checks.yml:36` (`unittest discover tests/unit -v` directly, on **every
    umbrella PR**). Neither guards *this* repo's PR path, which is the real gap.
    **Before writing "nothing runs X", check the umbrella — then check what SHA it
    pins.** *(`pr-checks.yml:28` also mentions this script in a comment, at the
    wrong path — `framework/scripts/` rather than `framework/tests/scripts/`.)*
- **Local `pre-commit` on changed files ≠ CI's `--all-files`.** A rebase conflict
  resolution once dropped a blank line before a CHANGELOG heading; local hooks never
  re-linted the seam and CI failed on MD022. **Run `pre-commit run --all-files` after
  any manual conflict resolution.**
- **markdownlint autofix corrupts prose in two specific ways.** A line starting
  `#NNN` becomes an H1 (`# NNN`) — write `Issue #NNN` or backtick it; and
  `__init__.py` becomes `**init**.py`, silently breaking claim-ledger citations —
  backtick any path containing underscores. **Seven** older plan files still carry the
  `**init**.py` corruption from before this was documented (re-measure with
  `grep -rl '\*\*init\*\*\.py' plans/`; the figure was recorded as eight and was wrong).
  Two further facts, and **they are two different rules** — disabling one does not stop
  the other. The corruption makes the citation gate fail with the **misleading**
  `path '.py' does not exist`; the workaround (#408) is
  `<!-- markdownlint-disable MD050 -->` scoped around the ledger — **MD050** is
  strong-style, the `__x__` case. Separately **MD049** (emphasis-style) normalizes
  `_x_` → `*x*` across a **whole** changelog file you touch, not just the lines you
  edited, and MD050 does not cover it.
- **`sync-version-refs` reporting "files were modified" is usually a knock-on**, not
  a second defect — it re-stages whatever an earlier autofix touched. Verify by
  running it alone against a clean HEAD.
- **Editing `tools/sdd_doc_lint/*.py` requires re-copying both vendored platform
  mirrors by hand.** No script does it, and `ruff-format` may rewrite the file
  *after* you copy — re-copy and re-run until two consecutive `--all-files` runs are
  clean. The linter's own sync script is `tools/sdd_doc_lint/sync-vendored.sh`,
  **not** `tools/sync-plugin-framework.sh` (which vendors `framework/` subtrees plus
  three named tools files and does not touch `sdd_doc_lint`).
- **Propagation order for a framework version bump is load-bearing:**
  `framework/VERSION` → `scripts/sync-version-refs.sh` → **then**
  `tools/sync-plugin-framework.sh`. Reversing it lands 51 drifted bundled playbooks
  and a red bundle guard.
- **The plugin and Hermes `CLAUDE.md` current-state tokens self-heal; the
  framework-spec token does not.** Since #389, `sync-version-refs.sh` detects the
  previous plugin and Hermes values **from `CLAUDE.md` itself**, so a stale token is
  fixed even when every other surface is current — the state that had let `CLAUDE.md`
  sit at Hermes `0.11.1` against a `0.12.0` `VERSION` for four days, and that the
  plugin token had carried latently since `SYNC-CLAUDE-PLUGIN-VERSION-GAP`.
  `fw_prev` is different: it is read
  from `CLAUDE.md` **and** gates propagation to `README.md`, `docs/PARITY.md`, both
  platform READMEs and a conformance-test literal — so **hand-editing the
  framework-spec token in `CLAUDE.md` before running the sync strands those five
  files, silently, at exit 0.** Measured, not inferred; filed as
  [#386](https://github.com/vladm3105/aidoc-flow-framework/issues/386). The 52 SKILL
  frontmatters, the playbooks and `platforms/*/FRAMEWORK_SPEC_VERSION` are **not** in
  that blast radius — each has its own detector.
- **Run a sync-script reproduction in a throwaway clone, never in the working tree.**
  Proving #386 meant bumping `framework/VERSION`, which fired the three independent
  detectors and rewrote **100+** SKILL / playbook / `FRAMEWORK_SPEC_VERSION` files —
  and the script's closing `git add -u` **staged all of them**. Restoring the two
  files the test targeted is not enough; the collateral is elsewhere and already in
  the index.

### Acceptance harness

- **Manifests live OUTSIDE `fixtures/`** (`tests/acceptance/expected_warnings/`).
  Inside a `NN_LAYER/` dir the linter ingests one as an artifact — measured at
  13 → 31 findings and `rc` 0 → 1, i.e. it *manufactures* errors. Latent for the live
  tier, since `live/_live_harness.py:stage_upstreams_into` copies `valid/` contents
  into exactly such a dir and live is `skipUnless(LIVE=1)`.
- **The pinned warning set measures trace-graph visibility, not fixture debt.** Six
  goldens have an unterminated frontmatter fence (one `---`, no `doc_id`) and are
  invisible to `build_edge_graph`. Repairing one is benign and **moves the manifest**
  — adding the fence to `layer_06_spec/valid` takes it 0 → 6.
- **`ELEM_FORM` cannot search a message** — it is fully anchored, so extraction is two
  steps: take the single-quoted token, then validate. And the linter's `file` key is
  CWD-relative or absolute, so a manifest loader **must** normalize to
  target-relative or every entry mismatches.
- **A *leading* `---` is only a document-start marker.** All six `fullpath` YAML
  goldens have one; only the three under `golden_chain/` carry a *closing* fence and
  are genuinely two documents. Walk them with `safe_load_all`, not `safe_load`.

### Writing to GitHub from a script

Each of these cost a real defect in merged code, and each was found only by looking
at the published artifact — never by a test asserting on the call sequence.

- **`gh run view --log` renders ANSI as the two literal characters `^` `[`, never a
  raw ESC byte.** Measured on run `30257877863`: **0** occurrences of `0x1b`, **68**
  of `^[`. A filter written as `grep -v $'\x1b'` therefore matches nothing — it looks
  like a guard and is dead code. Filter on `'\^\['` instead. The same fact means a
  fixture built from a real download is byte-faithful even though it *looks*
  re-rendered; do not "fix" it.
- **In a single-quoted `printf` format, `` \` `` is a literal backslash, not an
  escape** — it publishes as `` \` `` to anyone reading the issue. In an **unquoted**
  heredoc (`<<EOF`) the opposite holds: a bare backtick is command substitution, so
  the backslash there is required. The two rules are inverted, and one script can
  contain both. Shipped in #392, caught on issue #393's real close comment, fixed in
  #394.
- **Command substitution strips trailing newlines**, so a helper ending in
  `printf '\n'` cannot supply the blank line that terminates a GFM table when
  consumed as `$(helper)` inside a heredoc — the following paragraph is absorbed into
  the table as junk rows. The blank line has to be literal *in the heredoc*.
- **`gh --jq` uses gh's own built-in jq**, so a `|| die` on the `gh` call proves
  nothing about a *separate* external `jq` invocation on its output. Guard each
  extraction, and treat an unparseable id as fatal — an empty id is
  indistinguishable from "no such issue" and will route a read failure into a
  **create**.
- **`gh issue create --assignee` and `--label` both hard-error on an unknown value.**
  Apply the label by *retry* (labelled, then unlabelled + `::warning::`) — never
  `|| true`, which makes the whole creation non-fatal. Set the assignee *after*
  creation, so its failure cannot take the create with it.
- **The prescribed comment-readback can report a published comment as empty.**
  `gh issue view <N> --json comments --jq '.comments[-1].body|length'` returned **0**
  for a comment that had published in full (3,629 chars via
  `gh api …/issues/comments/<id>`), and the correct value on a later read —
  read-after-write lag. The feedback contract calls a non-zero length "the only proof
  it published", and the symptom is **identical to the `--body -` bug**, so the
  natural reaction is to re-post and duplicate. Anchor the check to the id in the URL
  `gh` returned, or retry before concluding anything. Filed as
  [aidoc-flow-operations#290](https://github.com/vladm3105/aidoc-flow-operations/issues/290).
- **`gh issue list` defaults to `--limit 30`**, and this repo is past #390. A
  tracking issue that has aged off page 1 is invisible to an exact-title lookup, and
  the run creates a duplicate. Use `--state all --limit 200`, and never `--search`
  (tokenized and eventually consistent, so a just-created issue can be missing).

### Process

- **Verify a blocker before escalating it** (**D-0068**). `IDGEN-NO-GENERATOR`'s
  merged plan declared a founder decision was required over `state: canonical` vs
  `id_state: provisional`. There was no conflict — `id_standard.state` is template
  metadata with no code consumer, and the linter says so at
  `tools/sdd_doc_lint/__init__.py:558`. An unverified blocker in a merged plan stalls
  work on a decision nobody needs to make.
- **Write the scan before the census.** A surface count went 9 → 19 → the truth of
  **25**, because both manual passes sampled one file instead of the tree. A
  hand-built census of a class is a sample that gets reported as a total.
- **A root cause is a claim about a distribution — derive the distribution first**
  (**D-0072 §3**). A sampled read of `doc-maintainer`'s failures named `ci#352` "the
  blocker" and that framing reached three files; the full census put #352 at 3 of 23
  and #353 at 15. Both are true in their own sense, but conflating them produced a
  **resume condition that would have returned a majority-red pilot**. Loop every
  failing run and bucket the errors before naming a cause.
- **When an error names a condition, check the named artifact actually violates it**
  (**D-0072 §2**). Canon's `duplicate or non-allowlisted plan path: <path>` covers two
  conditions in one string, and its most frequent instance named a path that **is**
  allowlisted. An allowlist-shaped message about an allowlisted path read as a config
  mismatch, and that misdiagnosis was written into the backlog as this repo's bug.
  One `jq '.allowed_paths'` falsified it.
- **An absence is the easiest defect to assert and the hardest to verify.**
  `NO-PIN-CURRENCY-CHECK` named an absence as the cause of a mixed-pin state
  surviving two days. The check *does* run — canon's `check-standards-drift.sh` tail
  invokes it on every weekly `standards-drift` run — and it had fired on 2026-07-27
  naming all ten stale pins **and** the `--repin` remedy. The proposed fix would have added a
  **second copy of a check that was already running and already right**; the real gap
  was that a warning-only annotation on a weekly job has no reader. One
  `gh run view --log | grep pin-currency` falsified it. **Read the log before writing
  an absence down.**
- **Mutation-test a negative-property guard.** `test_no_inprompt_hashing.py` passed a
  live reintroduction on first write: markdownlint reflows those surfaces into single
  long lines, so the correction and the regression shared a line and a line-scoped
  negation skip masked it.
- **Measure blast radius before shipping an operation over shared state.**
  `rehash --fix` was cut on measurement, not principle — it would rewrite all four of
  BRD-01's §7 FR IDs and break citations in 8 downstream files.
- **Before fixing a defect in a hand-rolled surface, check whether canon owns that
  surface** (**D-0071 §2**). #373 asked to SHA-pin an action; adopting canon's caller
  closed it and removed the class of defect, where editing the `uses:` lines would
  have fixed the symptom and left the workflow to drift at the next release.
- **A registration rule and a resolution rule live in different tables, and you find
  the reassuring one first.** "Installing it shadows nothing" ≠ "a bare name resolves
  to it". Ask what resolves the name *at call time*. No test and no green CI catches a
  wrong reassurance — the plugin agent case (`PREPROD-L7` / #417) is the worked example:
  agents register under a scoped identifier, so installation overwrites nothing, but
  every dispatch the plugin ships is *bare*, and a bare name resolves by scope
  precedence where a plugin ranks lowest of five.
- **Your own test can enshrine the defect you just introduced.** Written beside its
  fix, a test inherits the fix's misconception, and mutation testing is blind to it
  because the mutant and the test agree. When a fix has a *direction*, state it as an
  invariant in code, not only as an assertion about one case.
- **A surviving mutant usually indicts the test, not the fix.** Assert the
  *classification*, not the downstream outcome, whenever the outcome has more than one
  possible cause — otherwise the test passes for the wrong reason and the mutant lives.
- **A fix can silently disarm an existing regression test, and the suite stays green
  because nothing happened.** When a change alters an exit code, a return value or an
  error type, **grep for tests that arrange the OLD behaviour** — they now pass
  vacuously. (Sibling of the gate-greps-a-literal lesson in **D-0074 §1**: a check
  named for an invariant stops measuring it the moment the implementation is renamed.)
- **A "documentation-only" closure needs a named owner for the mechanism, or it is not
  a closure** (**D-0074 §3**). `PREPROD-L7` allowed either a rename or documenting the
  collision; documentation shipped, and that was defensible *only* because the live
  half went to `PREPROD-L7-BARE-DISPATCH` (#417). Without the successor entry it would
  have been closing a partial finding.
