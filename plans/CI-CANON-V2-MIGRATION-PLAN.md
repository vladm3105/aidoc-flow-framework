# CI-CANON-V2-001 Plan — migrate this repo's CI callers from `ci/v1.9.5` to the `ci/v2.x` canon

| Field          | Value                                                            |
| -------------- | ---------------------------------------------------------------- |
| Task           | CI-CANON-V2-001                                                   |
| Type           | chore                                                             |
| Status         | PLANNED — 2026-07-25T19:31:24Z                                    |
| Depends on     | 🔴 founder prerequisites (Wave 0 below); upstream `aidoc-flow-ci` `plans/PLAN-009_fleet-v2-cutover.md` Phase 2 |
| Feeds          | removal of the `.github/dependabot.yml` `semver-major` hold on `vladm3105/aidoc-flow-ci/*` |
| Version impact | none — no `VERSION` stream moves (CI infrastructure only)          |

## Objective

This repo consumes the workspace CI canon (`vladm3105/aidoc-flow-ci`) via ten
`uses:` call sites across nine workflow files, all pinned at **`@ci/v1.9.5`**.
Canon has since shipped **`ci/v2.14.0`**. The v1→v2 step is a documented
breaking change (vendor CLIs replaced by a single LiteLLM proxy), so the pins
have been deliberately held — `.github/dependabot.yml` carries a `semver-major`
`ignore` for `vladm3105/aidoc-flow-ci/*` whose in-file removal condition is
exactly this plan's completion criterion.

This plan is **this repo's execution of upstream PLAN-009 Phase 2**
(`aidoc-flow-ci/plans/PLAN-009_fleet-v2-cutover.md` §"Phase 2 — Remaining public
(framework, iplan-runner, iplan-standard)"). It brings every canon caller to a
single `ci/v2.x` tag in one PR, adopts the one canon surface this repo currently
hand-rolls (`standards-drift`), and records what stays deliberately local.

## Scope

**In:**

- **Wave 0 (🔴 founder, blocking):** provision `LITELLM_BASE_URL` +
  `LITELLM_REVIEW_API_KEY` on this repo; register a self-hosted
  `ci-runner,single-use` runner reachable from the LiteLLM proxy host.
- **Wave 1 (🟢 AI, one PR):** bump all ten `uses:` call sites `@ci/v1.9.5` →
  `@ci/v2.14.0`; move **both** `ai-review` jobs onto the self-hosted pool per the
  PLAN-013 uniform-protected model; tidy the now-false vendor-CLI header comments; add
  `litellm.model` to `.github/ai-review/config.json`; audit secret-scan fixtures
  against the v2 allowlist removal; drop the `dependabot.yml` major-hold.
- **Wave 2 (🟢 AI, same PR or a follow-up):** replace the hand-rolled
  `.github/workflows/standards-drift.yml` (a `curl`-and-execute of
  `check-standards-drift.sh` pinned at a `ci/v1.6.0` commit SHA) with a thin
  caller of the canon `standards-drift.yml` reusable at `tier: governance`.
- **Wave 3 (🔴 founder, post-merge):** apply the CI-0011 `actions-permissions`
  narrowing so the newly-adopted `standards-drift` reports clean; delete the
  now-unreferenced `CLAUDE_CODE_OAUTH_TOKEN` secret.

**Out of scope (deferred):**

- **`dep-scan` / `trivy-scan` / `sast-scan`** — canon's three opt-in scanner
  surfaces. All three ship "uniform protected" caller templates hard-set to
  `runner_labels: '["self-hosted", "ci-runner", "single-use"]'`; adopting them
  needs a pool with spare capacity beyond the Wave 0 review runner. Revisit once
  Wave 0 is live and the pool is sized.
- **`doc-maintainer.yml`** — supersedes `docs-sync.yml` at `ci/v2.0.0`, but needs
  `LITELLM_DOC_API_KEY` and is `⏸ per-need` for this repo in canon's own
  applicability matrix (`aidoc-flow-ci/docs/WORKFLOWS.md` §2). `docs-sync` stays
  in dry-run.
- **`markdown-lint.yml`** — deliberately not adopted; this repo lints markdown
  through its own pre-commit hook. Recorded as `🕳 own` in canon's matrix, not a
  gap.
- **`codeql.yml`** — stays local. Canon ships a reusable, but the local file
  carries a customized `languages` surface and canon itself marks `codeql.yml`
  `safe_to_replace: false` for that reason.
- **Removing `auto-merge-ai-prs.yml`** — see Risk R4.
- **`markdown-lint` report-only → blocking**, and **`docs-sync` dry-run → live**
  — canon graduations, each founder-gated and independent of this migration.

## Approach / Design

### Current state (verified live 2026-07-25)

Ten call sites, nine files, all `@ci/v1.9.5`:

| File | Canon reusable | Call sites |
| --- | --- | --- |
| `ai-review.yml` | `ai-review.yml` | 1 |
| `composition.yml` | `composition.yml` | 1 |
| `auto-merge-ai-prs.yml` | `auto-merge-ai-prs.yml` | 1 |
| `docs-sync.yml` | `docs-sync.yml` | 1 |
| `secret-scan.yml` | `secret-scan.yml` | 1 |
| `links.yml` | `links.yml` | 2 (`internal` + `external`) |
| `labeler.yml` | `labeler.yml` | 1 |
| `pre-commit.yml` | `pre-commit.yml` | 1 |
| `audit-trail.yml` | `audit-trail-check.yml` | 1 |

Local, non-canon workflows (unchanged by this plan): `chg-gate.yml`,
`codeql.yml`, `conformance.yml`, `doc-review.yml`, `hermes.yml`, `plugin.yml`.
Plus `standards-drift.yml`, which Wave 2 converts.

Live prerequisite state on `vladm3105/aidoc-flow-framework`:

| Prerequisite | State |
| --- | --- |
| `APP_REVIEWER_1_ID` / `APP_REVIEWER_1_KEY` | ✅ present |
| `APP_REVIEWER_1_BOT_ID` (repo variable) | ✅ `294948438` |
| `LITELLM_BASE_URL` | ✅ set 2026-07-25T19:52:52Z (Wave 0 #1 done) |
| `LITELLM_REVIEW_API_KEY` | ✅ set 2026-07-25T19:52:52Z (Wave 0 #1 done) |
| Self-hosted runners | ❌ **`total_count: 0`** — Wave 0 #2 outstanding |
| LiteLLM proxy reachability | ⚠️ `172.17.0.1:4001` + `127.0.0.1:4001` only; no public/TLS listener (`ss -tlnp`, 2026-07-25) → forces both Edit D and Wave 0 #2 |

### Target tag — `ci/v2.14.0`, not PLAN-009's `ci/v2.8.0`

Upstream PLAN-009 names `ci/v2.8.0` as the fleet target; that banner dates to
2026-07-18 and canon has since shipped through `ci/v2.14.0`, which is the
current `Latest` release and the tag canon's own `install/templates/` reference.
Re-pinning to a six-minors-stale tag would require a second bump immediately.
**Target `ci/v2.14.0`.** Everything PLAN-009 Phase 2 specifies (Edits A, C, F)
applies unchanged; only the tag string differs.

### Why one PR, not an incremental sweep

Ten call sites bumped a few at a time yields a **mixed-major CI canon inside one
repo** — the v1 `ai-review` reading vendor-CLI credentials while the v2
`composition` expects the LiteLLM contract. That is precisely why Dependabot
PRs #321–#324 were closed and the `dependabot.yml` major-hold was added
(`e2622ee8`, PR #329). The hold's own removal condition reads: *"REMOVE THIS ENTRY
when the LiteLLM secrets are provisioned and the fleet re-pin is armed; then bump
all ten call sites in one PR."* This plan honors that.

### Wave 0 — 🔴 founder prerequisites

Neither item is executable by an AI agent: one needs the LiteLLM master key, the
other needs shell access to the proxy host.

1. **LiteLLM secrets.** `LITELLM_BASE_URL` + `LITELLM_REVIEW_API_KEY`, set
   per-repo (`vladm3105` is a personal account — there is no org-secret tier to
   inherit from; PLAN-009 Phase 0 #1). Canon ships
   `install/set-litellm-secrets.sh` with a `--mint` mode that generates a
   review-scoped virtual key from the master key.
2. **Self-hosted pool for the AI flow.** The proxy is host-local
   (`http://172.17.0.1:4001`, private by founder decision), so a GitHub-hosted
   `ubuntu-latest` runner cannot reach it. Register
   `self-hosted,ci-runner,single-use` on this repo per
   `aidoc-flow-ci/docs/runners.md` §3/§5a.

   **Size for the full ai-review flow, not one job.** PLAN-009 Phase 0 #2 (dated
   against `ci/v2.0.1`) says only the heavy *review* job needs the pool. That is
   superseded by the **PLAN-013 uniform-protected AI-flow model** shipped in
   `ci/v2.2.0`: canon's `install/templates/workflows/ai-review.yml` is now a
   single template with no public/private split, setting **both**
   `runner_labels_routine` and `runner_labels_review` to
   `'["self-hosted", "ci-runner", "single-use"]'` — safe because the trust job
   runs no PR code (canon `ai-review.yml` input description, lines 18-24).
   PLAN-009's own superseded-target banner states this correction; its Phase 2
   body was never updated. Both jobs run serially per supervisor instance, so
   register enough instances that a PR does not serialize.

3. **Drop the deprecated vendor-CLI secret** (`MIGRATION_v2.0.0.md` §2;
   PLAN-009 Phase 0 #5) — **post-cutover**, not before: `CLAUDE_CODE_OAUTH_TOKEN`
   is no longer referenced by any v2 reusable. **Keep `AI_REVIEW_TOKEN`** — it is
   on PLAN-009 Phase 0 #3's *verify-it-did-not-lapse* list, not the deprecated
   list. Keep `APP_REVIEWER_1_ID` / `_KEY` and the `APP_REVIEWER_1_BOT_ID`
   variable.

**Verification gate:** `gh secret list` shows both LiteLLM secrets, and `gh api
repos/vladm3105/aidoc-flow-framework/actions/runners` shows ≥1 online runner
carrying all three labels. Wave 1 does not start until both hold.

`litellm-smoke.yml` lives only in canon (it is not an install template), so a
green canon smoke proves the **proxy and the `ai-reviewer` alias** are healthy —
it does **not** prove this repo's pool can reach the proxy. That last hop is
proven only by an actual `ai-review` run here, which per "Verification" below
cannot happen on the migration PR itself.

### Wave 1 — the re-pin PR

| Edit | PLAN-009 ref | Detail |
| --- | --- | --- |
| **A** | Edit A | All ten `uses:` lines `@ci/v1.9.5` → `@ci/v2.14.0`. Use `CI_TAG=ci/v2.14.0 bash install.sh vladm3105/aidoc-flow-framework --repin` — **never `--update`**, which replaces caller bodies and would discard this repo's `runner_labels_*`, `permissions:` blocks, and trigger customizations. |
| **F** | Edit F, as corrected by PLAN-013 | On `ai-review.yml`, set **both** `runner_labels_routine` **and** `runner_labels_review` to `'["self-hosted", "ci-runner", "single-use"]'`, matching canon's single `install/templates/workflows/ai-review.yml`. Do **not** follow PLAN-009 Phase 2's literal "keep routine on `ubuntu-latest`" — that predates `ci/v2.2.0`. Every other caller stays on `ubuntu-latest`: per `aidoc-flow-ci/docs/UPDATE_GUIDE.md`, on public repos the fork-code-executing lint callers (`links`, `pre-commit`) must stay GitHub-hosted, and only the AI flow moves to the pool. |
| **D** | Edit D, extended to this repo | On `ai-review.yml`: `litellm_allow_insecure_http: true`. PLAN-009 scopes Edit D to the private trio, on the assumption public repos reach the proxy over HTTPS. **That does not hold here.** Verified 2026-07-25: the proxy listens only on `172.17.0.1:4001` and `127.0.0.1:4001` — there is no public or TLS listener — so this repo's `LITELLM_BASE_URL` is necessarily an `http://` Docker-bridge URL. Canon's `litellm_client.py:49-51` refuses any non-HTTPS scheme unless `LITELLM_ALLOW_INSECURE_HTTP=true`, failing with *"LITELLM_BASE_URL must use HTTPS (or explicitly allow HTTP)"*. Without this input the review job dies on every PR. |
| **G** | §"Tidy" | Delete the now-false header comments in `ai-review.yml` naming `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / the config-driven `reviewer:` selection, and the commented-out `# reviewer: claude` line. v2 removed the input; leaving the comment misdocuments the contract. |
| **H** | MIGRATION §3 | Add `"litellm": {"model": "ai-reviewer"}` to `.github/ai-review/config.json`. The reusable defaults to `ai-reviewer` when absent, so this is explicitness, not a functional change. |
| **I** | Phase 1 bullet | **secret-scan fixture audit.** v2 drops the blanket `tests/` / `fixtures/` / `vectors/` / `.secrets.baseline` allowlist. This repo has a `.secrets.baseline` (~12 KB) and **no `.gitleaks.toml`**, so a re-pinned `secret-scan` can flip green→red. Run gitleaks locally against the v2 config before pushing; ship a repo-local `.gitleaks.toml` if it finds fixture placeholders. |
| **J** | — | Remove the `semver-major` `ignore` entry for `vladm3105/aidoc-flow-ci/*` from `.github/dependabot.yml`, per its own in-file removal condition. |

**`docs-sync.yml` carries an unmerged prerequisite.** Its caller was raised to
`pull-requests: write` precisely so the upstream permission raise takes effect on
re-pin — but that change is commit `3f9467a5` on branch
`ci/docs-sync-comment-permission`, which is **pushed and has no open PR; it is not
on `main`** (verified 2026-07-25). If Wave 1 branches from `main` as-is, the
re-pinned `docs-sync` gets caller `pull-requests: read`, GitHub intersects caller
and callee permissions, and the dry-run comment step dies on
`GraphQL: Resource not accessible by integration (addComment)` under
`set -euo pipefail`. **Land `3f9467a5` before Wave 1, or cherry-pick it into the
Wave 1 branch.** No other `permissions:` change is needed.

**Runner routing after the re-pin is correct by default for every non-AI
caller.** All eight non-`ai-review` reusables declare `runner_labels` with
`default: '"ubuntu-latest"'`, and `--repin` does not touch caller bodies — so
`composition`, `auto-merge-ai-prs`, `secret-scan`, `links`, `labeler`,
`pre-commit`, and `audit-trail` keep GitHub-hosted runners with no edit. One
deliberate divergence to record rather than "fix": canon's `docs-sync` **caller
template** sets the self-hosted pool, but this repo's `docs-sync.yml` passes no
`runner_labels` and so resolves to the `ubuntu-latest` default. That is correct
here — `docs-sync` runs in dry-run and needs no proxy access.

No `tier:` change is needed for the human-merge floor — it is enforced
server-side via canon `composition.yml` plus this repo's omission from the
`auto_merge.repos` allowlist (PLAN-009 Phase 2, framework row).

### Wave 2 — `standards-drift` local → canon reusable

The local file predates canon's reusable (first shipped `ci/v2.8.0`). It
`curl`s `sync/check-standards-drift.sh` from a hardcoded `ci/v1.6.0` commit SHA
and runs it — so it validates against a canon nine minors stale, and its pin
never moves when the repo re-pins.

Replace with canon's `install/templates/workflows/standards-drift.yml`, adapted:

- `uses: vladm3105/aidoc-flow-ci/.github/workflows/standards-drift.yml@ci/v2.14.0`
- **`tier: governance`** — **not** the template's default `product`. This repo is
  Governance tier per `aidoc-flow-ci/docs/REPO_STANDARDS.md` §1 line 63
  (*"`aidoc-flow-framework`, `aidoc-flow-iplan-standard` — Public spec/schema
  repo; human-merge only"*), matching the local file's existing
  `--tier governance`. Passing `product` would compare against the wrong
  branch-protection template.
- Keep `runner_labels` at the default `'"ubuntu-latest"'` — the reusable only
  reads GitHub API state and needs no proxy access.
- Keep warning-only (`strict: false` default), preserving current behavior.

This also retires the SHA-pinning rationale in the local file's comments: the
reusable is invoked by `uses:` (which GitHub resolves from an immutable tag under
canon's `ci/v*` ruleset `19687369`), not by `curl`-and-execute, so the
stricter-posture argument no longer applies.

### Wave 3 — 🔴 CI-0011 settings application

`ci/v2.13.0` narrowed canon's `actions-permissions.json`
(`verified_allowed: false`; `patterns_allowed` → `vladm3105/*`). Those are
**template** values, applied per-repo. Re-pinning without applying them makes the
newly-adopted `standards-drift` emit two warnings
(`verified_allowed: canon=false actual=true`, `patterns_allowed: MISSING`).

**This is expected and not a regression** — `strict` defaults to `false`, so it
warns and exits 0. Before applying, scan this repo's `uses:` lines: the narrowed
allowlist admits only `actions/*`, `github/*`, `vladm3105/*`, and anything
outside that set `startup_failure`s **silently, with no logs**. `conformance.yml`,
`codeql.yml`, `hermes.yml`, and `plugin.yml` must be checked before the PUT.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `.gitleaks.toml` | Only if Wave 1 Edit I finds fixture placeholders under the v2 allowlist. |

### Modified

| Path | Change |
| ---- | ------ |
| `.github/workflows/ai-review.yml` | Edit A (pin), D (`litellm_allow_insecure_http`), F (`runner_labels_routine` **and** `runner_labels_review` → pool), G (comment tidy) |
| `.github/workflows/composition.yml` | Edit A |
| `.github/workflows/auto-merge-ai-prs.yml` | Edit A |
| `.github/workflows/docs-sync.yml` | Edit A |
| `.github/workflows/secret-scan.yml` | Edit A |
| `.github/workflows/links.yml` | Edit A (×2 call sites) |
| `.github/workflows/labeler.yml` | Edit A |
| `.github/workflows/pre-commit.yml` | Edit A |
| `.github/workflows/audit-trail.yml` | Edit A |
| `.github/workflows/standards-drift.yml` | Wave 2 — replaced with a canon caller |
| `.github/ai-review/config.json` | Edit H (`litellm.model`) |
| `.github/dependabot.yml` | Edit J (drop the major-hold) |

## Implementation sequence

1. **Wave 0 gate** — confirm both secrets + ≥1 labelled online runner + green
   canon `litellm-smoke.yml`. Stop here if any fails.
0. **Land the unmerged `docs-sync` permission raise** (`3f9467a5`, branch
   `ci/docs-sync-comment-permission`) — or cherry-pick it into the Wave 1 branch.
   See the `docs-sync.yml` note under Wave 1.
2. Branch `ci/canon-v2-migration` from the resulting `main`.
3. Run `install.sh --repin` at `CI_TAG=ci/v2.14.0`; `grep` to confirm exactly ten
   `@ci/v2.14.0` and zero `@ci/v1.9.5` remain.
4. Apply Edits D, F, G, H, J by hand.
5. Edit I — run gitleaks with the v2 config locally; add `.gitleaks.toml` if
   needed.
6. Wave 2 — rewrite `standards-drift.yml` as a canon caller at
   `tier: governance`.
7. Verification (below).
8. Author-side multi-agent review per OPS-0065/0067 — this is a
   workflow-YAML + governance diff, so dispatch at minimum code-reviewer +
   security-auditor; fold findings; cap at 3 cycles (OPS-0066).
9. Update docs of record (below); open the PR. Expect `call / composition` to
   block (see "The migration PR cannot verify its own `ai-review`"); merge is a
   founder `--admin` action, flagged as such in the PR body.
10. **Post-merge: open a throwaway PR and watch `ai-review` to live green.** This
    is the real pass criterion. If it fails, the fix is forward — do not revert
    the pins without re-checking Wave 0.
11. Wave 3 — hand the founder the CI-0011 settings PUT and the
    `CLAUDE_CODE_OAUTH_TOKEN` deletion.

## Verification

| Check | Command / criterion |
| --- | --- |
| Pin sweep complete | `grep -rho "@ci/v[0-9.]*" .github/workflows/ \| sort \| uniq -c` → exactly one row, `11 @ci/v2.14.0`. **Eleven, not ten**: Wave 1 re-pins the ten pre-existing call sites and Wave 2 adds an eleventh (the new `standards-drift` caller). If Wave 2 ships separately, the Wave 1 count is 10. |
| YAML valid | `yamllint .github/workflows/` clean. Note this repo carries **both** `.yamllint` and `.yamllint.yaml`; confirm which one the run picks up (pre-existing condition, not introduced here). |
| No unregistered runner label | `grep -rn "runner-self\|ci-ephemeral" .github/workflows/` → empty |
| Conformance unaffected | `python -m unittest discover -s tests/conformance -v` — 239 ✓ (the exact command `conformance.yml` runs) |
| secret-scan not flipped | `secret-scan` green on the PR |
| No job stuck queued | every job starts; a permanently `queued` job means the runner label is wrong |
| standards-drift runs | `workflow_dispatch` the new caller; expect ≤2 CI-0011 warnings, exit 0 |
| ai-review live-green | **Post-merge only — see below.** `ai-review` ran and passed (not skipped, not `startup_failure`) |
| composition satisfied | **Post-merge only.** `call / composition` reports a counting reviewer-App approval at head |

### The migration PR cannot verify its own `ai-review`

`ai-review.yml` triggers on `pull_request_target`, and `composition.yml` on
`pull_request_review` + `workflow_run`. All three run the workflow definition
from the **base branch**, not the PR head — so on the migration PR they execute
the *old* `@ci/v1.9.5` callers. The new pins take effect only once merged.

Two consequences, neither optional:

1. **The migration PR will hit the current `BLOCKED` state.** As recorded in
   `plans/HANDOFF.md`, `ai-review` is presently 401 (no working reviewer key),
   so `call / composition` correctly fails with *"no counting reviewer-App
   approval (bot id 294948438) at head"*. That is a **verdict, not an
   infrastructure failure**. Merging it needs a founder `--admin` merge, and
   that merge knowingly bypasses a live approval gate — call it out in the PR
   body rather than treating `--admin` as routine.
2. **Verification moves to a throwaway PR after the merge.** This is the pattern
   `operations` used (its throwaway PR #266 confirmed the v2 reviewer posts a
   real `CHANGES_REQUESTED`). Open a trivial PR post-merge, confirm `ai-review`
   runs on the pool, reaches LiteLLM, and posts a verdict, then close it.
   **Until that throwaway PR is green, this migration is not done** — a green
   migration PR proves only that the YAML parses.

## Docs to update

Per `CONTRIBUTING.md` §"Documentation discipline":

- `CHANGELOG.md` — CI entry under `## [Unreleased]`.
- `plans/DECISIONS.md` — new `D-00NN`: target `ci/v2.14.0` rather than
  PLAN-009's stale `ci/v2.8.0`; `standards-drift` moved from hand-rolled `curl`
  to the canon reusable at `tier: governance`.
- `plans/HANDOFF.md` — replace the "CI `ai-review` is 401 / no working reviewer
  key" banner with the post-migration state.
- `CLAUDE.md` §"Unified CI — consume from `aidoc-flow-ci`" — the per-repo state
  paragraph still reads *"Current standalone `.github/workflows/ai-review.yml`
  is LIVE (codex reviewer). Migrates to `uses: aidoc-flow-ci/...@ci/v1.0.0` in
  **Phase A**"*. That is stale on two counts today (the callers migrated long
  ago; the reviewer is no longer codex) and must be corrected as part of this
  work.

**Governance-PR discipline** (`CLAUDE.md` §"Governance PR discipline" Rule 1,
≤3 doc surfaces per PR). This work is a governance PR by definition — it touches
`.github/workflows/ai-review.yml` and `.github/ai-review/`. Split into three
sequential PRs so no single one exceeds the cap:

| PR | Surfaces | Count |
| --- | --- | --- |
| 1 — plan | this plan file | 1 |
| 2 — implementation | `.github/workflows/*` (incl. `ai-review.yml`), `.github/ai-review/config.json`, `.github/dependabot.yml`, `CHANGELOG.md` | 3 governance surfaces + changelog |
| 3 — governance records | `plans/DECISIONS.md`, `plans/HANDOFF.md`, `CLAUDE.md` | 3 |

PR 1 → merge → PR 2 → merge → PR 3 is also what `CLAUDE.md` §"Development
workflow" item 2 already requires (plan PR merges before implementation starts).

## Risks

| ID | Risk | Mitigation |
| --- | --- | --- |
| **R1** | Re-pin lands without Wave 0 → `ai-review` hard-exits on the missing LiteLLM secret, and every gate this repo has is dead rather than merely 401-broken. | Wave 0 is an explicit blocking gate with three live checks. Never re-pin on a partial provision. |
| **R2** | The review job is routed to a pool with no capacity → jobs sit `queued` forever with green-looking config. | Verification includes "no job stuck queued". Size supervisor instances per `runners.md` §5. |
| **R3** | v2 secret-scan allowlist removal flips `secret-scan` green→red on a repo carrying a `.secrets.baseline` and no `.gitleaks.toml`. | Edit I audits locally **before** push. |
| **R4** | `auto-merge-ai-prs.yml` exists here, but canon's matrix records this repo as `⏸ (spec tier — human-merge)`. Re-pinning it carries an arguably-unwanted surface forward. | Re-pin it (inert either way: human-merge is enforced server-side via `composition` + omission from `auto_merge.repos`). Removing a workflow is a separate governance decision, deliberately not bundled here. |
| **R5** | `install.sh --repin` reaches for `--update` semantics by operator error, wiping `runner_labels_*` / `permissions:`. | Step 3 fixes the flag; step 7's `grep`-based verification catches a body swap. |
| **R6** | PLAN-009's per-repo detail could drift further from canon before Wave 0 clears. | Re-read `aidoc-flow-ci/HANDOFF.md` + `plans/PLAN-009` at Wave 1 start; this plan pins the tag, not the upstream narrative. |
| **R7** | Wave 1 branches from `main` and silently loses the unmerged `docs-sync` permission raise (`3f9467a5`), breaking the dry-run comment on the first post-merge push. | Land or cherry-pick `3f9467a5` first — called out under Wave 1 and added to the implementation sequence as step 0. |

## Review log

Per `CLAUDE.md` §"Development workflow" item 2: ≥2 full cycles before the plan
PR opens.

### Pass 1 — 2026-07-25T19:31:24Z — claims verified against canon source

Every load-bearing claim was checked against the live `aidoc-flow-ci` checkout
and live `gh` state rather than against upstream prose. Four defects found:

1. **Edit F was wrong (load-bearing).** The draft copied PLAN-009 Phase 2
   literally — "`runner_labels_review` → self-hosted, keep `runner_labels_routine`
   on `ubuntu-latest`". Canon's
   `install/templates/workflows/ai-review.yml` is now a **single** template (the
   public/private split is gone) setting **both** to the self-hosted pool, per the
   PLAN-013 uniform-protected model shipped in `ci/v2.2.0`. PLAN-009's own
   superseded-target banner states this; its Phase 2 body was never updated.
   Following the draft would have left the trust job on a GitHub-hosted runner,
   diverging from canon and under-sizing the Wave 0 pool request by half.
   → Corrected in Scope, Wave 0 item 2, Edit F, and the Modified-files table.
2. **Pin-count inconsistency.** Verification asserted ten `@ci/v2.14.0` call
   sites, but Wave 2 adds an eleventh (the new `standards-drift` caller). A
   literal reading would fail its own check. → Verification now states 11 (or 10
   if Wave 2 ships separately).
3. **Wrong conformance command.** Draft used
   `python3 -m unittest discover tests/conformance`; `conformance.yml:33` runs
   `python -m unittest discover -s tests/conformance -v`. → Corrected to match CI.
4. **Unstated runner-routing assumption.** The draft never established what
   happens to the other eight callers' runners on re-pin. Verified: every non-AI
   reusable declares `runner_labels` with `default: '"ubuntu-latest"'` and
   `--repin` does not touch bodies, so they are correct with no edit. One
   deliberate divergence surfaced — canon's `docs-sync` *template* sets the pool
   while this repo's caller passes nothing and resolves to `ubuntu-latest`
   (correct: dry-run needs no proxy). → Recorded so a later reviewer does not
   "fix" it.

Also confirmed as correct and left unchanged: `install.sh --repin` exists with
`CI_TAG=` and is mutually exclusive with `--update` (`install.sh:91,105`);
framework is **Governance** tier, so the `standards-drift` caller needs
`tier: governance`, not the template's default `product`
(`REPO_STANDARDS.md` §1 line 63); all three opt-in scanners hard-set the
self-hosted pool, so deferring them is justified rather than merely convenient.

### Pass 2 — 2026-07-25T19:31:24Z — re-review of the patched plan

Three further gaps, one of them structural:

5. **The migration PR cannot verify its own `ai-review` (structural).**
   `ai-review.yml` triggers on `pull_request_target` and `composition.yml` on
   `pull_request_review`/`workflow_run` — all of which execute the **base
   branch's** workflow definition. The new pins therefore do not apply to the
   PR that introduces them: the migration PR is reviewed by the old `@ci/v1.9.5`
   caller, which is currently 401. So (a) the PR will hit the `BLOCKED`
   composition verdict recorded in `HANDOFF.md` and needs a founder `--admin`
   merge, and (b) step 9's "watch to live green" was unachievable as written.
   → Added a dedicated verification subsection; live-green verification moved to
   a post-merge throwaway PR, mirroring what `operations` did with its PR #266.
   The plan now states explicitly that a green migration PR proves only that the
   YAML parses.
6. **Deprecated-secret handling was missing.** `MIGRATION_v2.0.0.md` §2 requires
   dropping vendor-CLI credentials. This repo holds `CLAUDE_CODE_OAUTH_TOKEN`
   (deprecated → delete post-cutover) and `AI_REVIEW_TOKEN` (**not** deprecated —
   it is on PLAN-009 Phase 0 #3's verify-it-did-not-lapse list). Conflating the
   two would have deleted a live credential. → Added as Wave 0 item 3 + Wave 3.
7. **Wave 0's smoke-test gate over-claimed.** `litellm-smoke.yml` ships only in
   canon, so a green run proves the proxy and the `ai-reviewer` alias are healthy
   — not that *this repo's* pool can reach the proxy. → Gate narrowed to the two
   checks that are actually verifiable here, with the remaining hop explicitly
   deferred to the post-merge throwaway PR.

### Pass 3 — 2026-07-25T19:31:24Z — post-patch consistency sweep

Swept every cross-reference the Pass 1/2 patches could have desynchronized
(call-site counts, `Edit A`–`J` labels, file-table entries, wave numbering).
One residual found and fixed: the Modified-files row for `ai-review.yml` still
described Edit F as `runner_labels_review` alone, contradicting the corrected
Edit F two sections above. Ten/eleven call-site usages now read consistently.

### Pass 4 — 2026-07-25T19:31:24Z — git-provenance check before push

Every commit SHA the plan cites was verified with `git log -- <path>` rather
than trusted from session narrative. Two errors, one of them load-bearing:

8. **Misattributed the `dependabot.yml` major-hold** to `3f9467a5`; it is
   `e2622ee8` (PR #329). `3f9467a5` is a different change — the docs-sync
   permission raise plus D-0065. → Corrected.
9. **Cited an unmerged commit as if it were landed state (load-bearing).** The
   draft asserted "no `permissions:` change is needed on `docs-sync.yml`" because
   the caller "was already pre-positioned". The raise is real but lives in
   `3f9467a5` on `ci/docs-sync-comment-permission` — **pushed, no open PR, not on
   `main`**. A Wave 1 branch cut from `main` would re-pin `docs-sync` with caller
   `pull-requests: read`; GitHub intersects caller and callee permissions, so the
   dry-run comment step would die on `addComment` not accessible. → Added as
   implementation step 0, a Wave 1 warning, and risk R7.

Finding 9 is the same class as Pass 2's finding 5: both are cases where the
draft described an intended end-state as though it were the live one. Worth
carrying into the next plan as a review lens — *check whether each asserted
precondition is on `main`, not merely written down somewhere.*

### Pass 5 — 2026-07-25T20:00Z — Wave 0 provisioning check (post-PR)

Ran while verifying the founder's Wave 0 work, against live host + repo state.
The LiteLLM secrets are confirmed set (`LITELLM_BASE_URL` +
`LITELLM_REVIEW_API_KEY`, 2026-07-25T19:52:52Z). One further defect:

10. **Edit D was wrongly scoped out (load-bearing).** The draft followed
    PLAN-009 in applying `litellm_allow_insecure_http: true` only to the private
    trio, implicitly assuming public repos reach the proxy over HTTPS. Live
    check: `ss -tlnp` shows port 4001 bound to `172.17.0.1` and `127.0.0.1`
    **only** — no public and no TLS listener — so this repo's `LITELLM_BASE_URL`
    must be an `http://` bridge URL. Canon's `litellm_client.py:49-51` refuses a
    non-HTTPS scheme unless `LITELLM_ALLOW_INSECURE_HTTP=true`. Without the
    input, the review job would fail on every PR with *"LITELLM_BASE_URL must
    use HTTPS (or explicitly allow HTTP)"* — and, per Pass 2's finding 5, that
    would not have surfaced until the post-merge throwaway PR. → Added as
    Edit D in Wave 1, the file table, and the implementation sequence.

The same host check independently confirms Wave 0 item 2 is **not** optional:
with no public listener, a GitHub-hosted runner cannot reach the proxy by any
route, so the self-hosted pool is load-bearing rather than a preference.

**No new substantive gaps.** Per `CLAUDE.md`, the ≥2-cycle floor is met and this
plan is ready for its plan PR. The empirical 4–5-cycle figure for cross-cutting
plans is advisory, not normative; this plan converged at 5, inside that band —
its scope is mechanical (a pin bump plus one caller replacement) and every claim
was verifiable against a local canon checkout or `git log` rather than inferred.
