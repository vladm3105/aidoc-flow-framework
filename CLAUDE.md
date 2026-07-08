# CLAUDE.md — Project Memory

Persistent context for the **AI Doc Flow Framework**. Auto-loaded every
session. Keep it short and current.

## What this project is

The document-flow framework, delivered as **one engine-agnostic specification
(`framework/`) with two independent platforms**:

- **Platform A — Hermes AI** — MCP-server engine (`platforms/hermes/`).
- **Platform B — Claude Code plugin** — native Claude Code engine, no MCP
  (`platforms/claude-code-plugin/`).

The platforms share the `framework/` spec and nothing else. Both pass the same
shared conformance suite (`tests/conformance/`). The `framework/` spec defines
the 8-layer SDD flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code).

**Current state (as of 2026-07-08):** framework spec `0.35.1`, Claude Code plugin `0.23.2` (pre-1.0 preview, 52 skills = 50 active + 2 deprecated stubs), Hermes `0.7.3`. **YAML-BDD arc complete** (BDD authored as structured `scenarios:` YAML, not Gherkin-in-markdown) and the **CONSUMER-FEEDBACK P1 wave shipped**: element-level COV01/COV02 coverage (D-0039 — `REALIZING_LAYERS` map; catches orphaned requirement elements), manual-mode provisional IDs + normative SHA-256 algorithm (D-0040 — `id_state`/`PROV01`; element IDs are LLM-generated stable strings, NOT verified content-hashes), and first-class reuse / satisfied-by-reference (D-0041 — `reuse:` frontmatter; `REUSE01`/`REUSE02`). **PROVISIONAL-IDS-002 Phase 1 shipped** (D-0061/D-0062, spec `0.35.0`): the element-ID hash-input contract (normalization transform + BRD §7 extraction boundary) is formalized in `ID_NAMING_STANDARDS.md`, and `python -m sdd_doc_lint.rehash --check` verifies a canonical BRD's §7 FR IDs against it on demand (`IDDRIFT01` — advisory, opt-in, NOT in the default lint). Scoped "verifiable on demand," not "verified"; `rehash --fix` + all-layer extraction + corpus reconciliation are founder-decided Phase 2+. Plugin also ships full 8-layer playbook injection + preemptive saga driver across all 8 autopilots (SAGA-PARITY-001) + per-layer model-recommendation precheck (MODEL-PRECHECK-ROLLOUT) + review-quality calibration + necessary-upstream contract (NECESSARY-UPSTREAM-001) + threshold-resolution gate (TH-RES-001) + per-PR doc-of-record discipline (DOC_GOVERNANCE_CORE.md Principle 8). 8-layer development sequence complete. **Next major arc: Hermes parity** (Hermes lags the plugin on the recent spec) — plugin-first sequencing, tracked in [`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md). The example corpus is regenerated wholesale after framework changes (so corpus-remediation findings are deferred to that regen). IPLAN ↔ iplanic integration deferred — see `plans/IPLAN-IPLANIC-DEFERRED.md`.

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
  [`CONTRIBUTING.md`](CONTRIBUTING.md#documentation-discipline-update-docs-of-record-per-pr).

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
     (CHANGELOG, ROADMAP, HANDOFF, HERMES-BACKLOG, …), prints a
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
| TODO / backlog | `plans/FRAMEWORK-TODO.md` |
| Decisions log | `plans/DECISIONS.md` |
| Plans | `plans/` (per-initiative `PLAN-NNN-<slug>.md` files) |
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
- `ROADMAP.md` — phased delivery plan (Phase 0 → cutover `v1.0.0`).
- `CHANGELOG.md` — project-level changelog.
- `docs/PROJECT.md` — versioning, branching, conformance, change management.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/TAGGING.md` — git-tag policy. `docs/PARITY.md` — platform comparison.
- `plans/` — the migration record (per-task plans, audits, verify records,
  `DECISIONS.md`, `HANDOFF.md`, `MIGRATION_TODO.md`).

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

**Per-repo state (2026-06-22):** **public repo; GitHub-hosted runners
(per "## CI host policy" — do not self-host).** Current standalone
`.github/workflows/ai-review.yml` is LIVE (codex reviewer). Migrates
to `uses: aidoc-flow-ci/...@ci/v1.0.0` in **Phase A** of IPLAN-0017
rollout — the eat-our-own-dogfood proof point (smallest cost; public-repo
iteration speed; fork-safe `pull_request` trigger). 🔴 Phase 0 (founder
creates `aidoc-flow-ci` repo) is the prerequisite.

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

A **governance PR** is any PR that touches `DECISIONS.md`, plan files
(`plans/PLAN-*.md` or `ops/iplans/IPLAN-*.md` per this repo's convention),
`CLAUDE.md`, `.github/ai-review/` or `.github/workflows/ai-review.yml`,
or supersedes a locked decision. Two rules apply to every governance
PR — no exceptions without explicit founder OK and an audit-trail
note in the commit message.

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
- **PRs that touch this repo's CLAUDE.md / plans/PLAN-*.md /
  `.github/ai-review/` / `.github/workflows/ai-review.yml`** (this repo's
  governance PR list per the "Governance PR discipline" section above).

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
