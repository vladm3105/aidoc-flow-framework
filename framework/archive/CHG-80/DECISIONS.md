# Decisions — repo working log

Non-obvious choices made during implementation work. ISO-stamped, newest first.
Spec-governance decisions live in `framework/governance/DECISIONS.md` (GD series,
plus the retired D-series annex); this file records repo-process choices that
do not belong in the spec.

## 2026-09-30 — D-0086: agent auto-merge authorized by default on own green PRs (#812)

- **Decision.** On a PR the agent itself opened, once all required checks
  pass and the PR is mergeable (`mergeStateStatus` CLEAN on the current
  head — confirm `headRefOid`), the agent enables auto-merge
  (`gh pr merge <N> --auto --squash --delete-branch`, the repo's
  squash-only convention) and reads the merge back. Authorizer: the repo
  working agreement (`AGENTS.md` "Watching your PR"); this entry is the
  provenance record #812 found missing.
- **Carve-outs (unchanged).** Withhold auto-merge when the user said hold,
  required checks are incomplete or red, a repo rule reserves the merge for
  a human, or the PR is not the agent's own — tool access is not merge
  authority.
- **Why the head re-check.** The green run belongs to a commit, not to the
  PR: confirming `mergeStateStatus` CLEAN on the current `headRefOid`
  makes the merge decision atomic against the checked head, so a
  previous run's green is never this commit's. Branch-protection required
  checks gate every merge regardless of this default.
- **Cited by** `AGENTS.md` ("Watching your PR").

## 2026-09-26 — D-0078: phantom versions are recorded, never tagged (#731)

- **Decision.** A version documented as released that `framework/VERSION`
  never held is an accepted phantom: recorded in the release ledger, never
  tagged (tagging one would put a tag on a commit that contradicts it)
  (`0d588c7c`). `test_release_record_integrity.py` fails on any new one.
- **Known permanent phantoms:** framework `0.42.0`, `0.52.0`, `0.53.3`
  (per `docs/TAGGING.md`). A missing tag is a different defect.
- **Cited by** `docs/TAGGING.md`.

## 2026-09-22 — CHG-05 implementation (bugfix vehicle, #656/#657)

- **Vehicle choice A (new `bugfix` subtype, not extended `audit_fix`).**
  `audit_fix` guidance is audit-shaped (severity-ordered findings, no TDD); contorting
  it to cover field defects would blur both contracts. New subtype keeps each
  contract readable; `combined` default untouched.
- **Greenfield `sdd_doc_lint/bugfix_lint.py` over extending `chg_lint.py`.**
  BGF checks validate IPLAN docs, not CHG docs; folding them into the CHG linter
  would couple two lifecycles. `chg_lint.py` untouched by design.
- **Linter wiring: CI-only, no pre-commit entry.**
  A pre-commit hook scoped to `IPLAN-*_bugfix_*` filenames would match zero tracked
  files, tripping `test_precommit_trigger_reachability.py` unless exempted in
  `KNOWN_UNREACHABLE` — an exemption that weakens the guard for a hook with no
  current consumers. Enforcement runs in CI instead: `sdd_doc_lint/tests` (BGF unit)
  via `doc-review.yml`, and the BGF catalog-agreement guard inside
  `tests/conformance` (runs on every PR via `chg-gate.yml`/`conformance.yml`).
  Authors run `bugfix_lint.py` manually. Revisit when the first real bugfix IPLAN
  lands in-tree.
- **TMP promise removed, not built.**
  Building a real `layers/08_IPLAN/tmp/` contract alongside the bugfix subtype would
  leave two competing lightweight vehicles. `tmp/` references now point at the
  bugfix vehicle with a retirement note.
- **Version confirm: MINOR `0.55.0 → 0.56.0`.**
  Additive template fields + governance prose + new lint checks; no removals, no
  registry shape change. Fanout via `hooks/sync-version-refs.sh` (+0.55.0 sweep
  lines); 107 pin-only files (every changed version literal verified as a pin
  form; `framework/VERSION` itself is the one exception). Branch total is 130
  files = 107 pins + 23 semantic/record files.
- **Corpus cross-check vacuous.**
  `examples/` was deleted by CLEANUP-001, so the `sdd_doc_lint examples/` check has
  no corpus. Coverage comes from `tests/acceptance/deterministic` (64 green, no
  golden churn) instead. Recorded so a future reader does not file it as a miss.

## 2026-08-31 — D-0084: ai-review and composition stop gating merges (#598)

- **Decision.** `call / ai-review` and `call / composition` removed from
  `main`'s required status checks (`e2a10ef5`). Both workflows still run;
  ai-review still submits its verdict as an issue comment plus COMMENT-state
  review on the canon gov-lock path.
- **"NOT REQUIRED" is not "CANNOT BLOCK".** `required_conversation_resolution`
  and `required_pull_request_reviews` still exist — an inline thread or a
  REQUEST_CHANGES review would still block. Both are inert only because canon
  submits COMMENT-state and opens no inline threads (measured, not assumed).
- **Branch protection is server state.** It lives in no repo file; re-derive
  via `gh api repos/vladm3105/aidoc-flow-framework/branches/main/protection`.
  Cited authoritatively by `.github/workflows/ai-review.yml`,
  `composition.yml`, `auto-merge-ai-prs.yml`, `standards-drift.yml`.

## 2026-08-31 — D-0085: canon pin census correction + semver-major hold (#603/#604/#607)

- **Decision.** Eliminate doc-maintainer, re-arm the canon semver-major hold
  on `vladm3105/aidoc-flow-ci/*` (`fecb4595`), and correct CLAUDE.md's canon
  pin census including D-0085's own inverted detector claim (`794aa573`).
- **Durable direction.** The hold belongs upstream in canon's template, not in
  this repo's `dependabot.yml` — pushing it there is the recorded follow-up.
  Cited by `.github/dependabot.yml`.

## 2026-07-30 — D-0070: concurrency rationale recorded where sweeps grep (#392/#395)

- **Decision.** The pin-currency `concurrency:` rationale lives in
  `.github/workflows/pin-currency-reader.yml` itself — "at the level a
  `concurrency:` sweep actually greps" (`d3d7f845`, `7cfcf4a0`).
- **Why.** A future sweep reading only the workflow file would otherwise delete
  the block and reintroduce the duplicate-issue race (the repo once shipped no
  `concurrency:` block at all on exactly that justification).

## 2026-07-25 — D-0065: CI PRs get CHANGELOG entries (#333)

- **Decision.** CI-only PRs carry CHANGELOG entries like any other change
  (`ce953f09`, alongside the docs-sync permission-prerequisite fix).
- **Cited by** `.github/workflows/audit-trail.yml` for the labeled-trigger
  incident (the `labeled`/`unlabeled` types are load-bearing: without them the
  two-signal override cannot re-fire the check).
