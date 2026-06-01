# Plugin Test Suite — Final Review

**Date:** 2026-05-31
**Reviewer:** code-reviewer (Phase 13)
**Diff scope:**

- Framework branch `feat/plugin-test-suite` — 54 commits ahead of `main`, HEAD before this record `35d7807d`
- Parent branch `feat/plugin-test-suite` — 9 commits ahead of `main`, HEAD `5465eae0`

## Verdict

**APPROVED.** 154 deterministic tests pass; 12 opt-in tests skip cleanly.

## Test counts

| Suite | Result |
|-------|--------|
| `tests/conformance` | 78/78 OK |
| `tests/unit` | 15/15 OK |
| `tests/acceptance/deterministic` | 48/48 OK |
| `tests/packaging` | 5/5 OK |
| `tests/release` | 8/8 OK |
| `tests/acceptance/live` | 10 skipped (LIVE != 1) |
| `tests/smoke` | 1 skipped (no MARKETPLACE_URL) |
| `tests/review` | 1 skipped (REVIEW != 1) |

## Findings — 8 MINOR (no BLOCKER / CRITICAL / MAJOR)

| ID | Severity | File | Finding | Disposition |
|----|----------|------|---------|-------------|
| F1 | MINOR | `tests/acceptance/_harness.py:131` | Docstring claims `IPLAN — DASH form only` but DOT_ONLY excludes IPLAN; harness actually accepts dot-or-dash for IPLAN refs. Misleading docstring; behavior latent (IPLAN never appears as upstream). | Fixed in this commit |
| F2 | MINOR | `tests/acceptance/deterministic/test_fullpath.py:40` | Stale "deferred to Phase 13" comment; `_id_coordinator.py` committed but never imported. Empty `ID_REGISTRY.yaml`. | Deferred follow-up (wire `_id_coordinator` into a real closure test, or remove both files). Tracked here. |
| F3 | MINOR | `tests/release/test_changelog_entry.py:19` | TODO says "Phase 12: re-introduce current-version assertion"; Phase 12 done but the strict assertion wasn't re-added. | Fixed in this commit |
| F4 | MINOR | `tests/unit/test_nonlayer_skills.py:25-33` | Tolerates up to 2 missing non-layer skills via `assertLessEqual(2)`; could silently allow regression. | Fixed in this commit (tightened to assertEqual([])) |
| F5 | MINOR | `.github/workflows/pr-checks.yml:26` | Step label says "Tier 3" but discovery covers Tiers 3+4 (test_fullpath.py). Cosmetic mislabel. | Fixed in this commit |
| F6 | MINOR | `tests/acceptance/_harness.py:44-47` | `run_lint()` swallows `JSONDecodeError` silently. If lint ever produced malformed stdout while exit-0, callers see "no findings" with no diagnostic. | Deferred — current sdd_doc_lint always emits valid JSON; defensive logging is a polish item |
| F7 | MINOR | `tests/CONTRIBUTING.md:25` | Doc command uses `bash framework/tools/sdd_doc_lint/sync-vendored.sh` (parent-relative) but the framework's own docs should be framework-relative. | Fixed in this commit |
| F8 | MINOR | `tests/smoke/COMMANDS.md:36` | Verification log is empty; `install-from-marketplace.sh` calls unverified `claude plugin install` syntax. | Deferred — smoke is workflow_dispatch only, won't trigger unintentionally |

## Disposition summary

- **5 MINOR findings fixed in this commit** (F1, F3, F4, F5, F7).
- **3 MINOR findings deferred as documented follow-ups** (F2, F6, F8). Each has a one-line note in this record and a corresponding inline comment marker in the source.

No findings blocked merge. The branch is ready to land.

## How to run the suite

See `framework/tests/README.md` (navigation hub) and `framework/tests/HOWTO.md` (commands).
