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

**Current state (as of 2026-06-11):** framework spec `0.21.0`, Claude Code plugin `0.17.0` (pre-1.0 preview, 52 skills = 50 active + 2 deprecated stubs). Plugin ships full 8-layer playbook injection (LAYER-PLAYBOOKS-001, 45 of 45 playbooks across all 8 layers) + preemptive saga driver across all 8 layers (SAGA-PARITY-001) + review-quality calibration with No-findings rationale + strip-self-claim + fixer-introduced regression detection (FRAMEWORK-CLEANUP-001 PR-B) + necessary-upstream contract (NECESSARY-UPSTREAM-001) + IPLAN sub-types (PR-E) + threshold-resolution gate TH-RES-001 (PR-D) + per-PR doc-of-record discipline (DOC_GOVERNANCE_CORE.md Principle 8 with mechanical + warning hooks). 8-layer development sequence complete; FRAMEWORK-CLEANUP-001 workstream complete (18/19 items, 2 deferred follow-ups). Plugin-first development sequencing; Hermes follow-on tracked in [`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md). IPLAN ↔ iplanic integration deferred — see `plans/IPLAN-IPLANIC-DEFERRED.md`.

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
