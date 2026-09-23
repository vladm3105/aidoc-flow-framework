# CLEANUP-001 Plan — framework-only repo: remove stale suites, fix dangling refs, restore conformance

| Field | Value |
|-------|-------|
| Task | CLEANUP-001 |
| Type | cleanup / bugfix |
| Status | PLANNED — 2026-09-20T00:00:00Z |
| Depends on | `bd32a927` (feat/clean-up: deleted `archive/`, `examples/`, `tmp/` — 1027 files); prior removal of top-level `platforms/`, `tools/`, `plans/` |
| Feeds | green conformance on `feat/clean-up`; subsequent breaking-change work |
| Version impact | none for the pure-cleanup steps (test/hook/tooling repair only); PATCH `0.53.2 → 0.53.3` if the #652 archive-scope text fix ships in the same PR (governance doc change). Point-in-time (frozen 2026-09-20; spec is at 0.59.0 — CHG-08 #670): version literals in this plan record are history, not live pins. |

## GitHub issues — triage (2026-09-20)

Only 3 issues are open; the rest are closed. Applicable ones are wired into the decisions below.

| Issue | State | Verdict | Wired into |
|-------|-------|---------|------------|
| #652 CHG lifecycle unenforced (chg_lint omits C16–C20/D21/D22; archive→rewrite contradicted by practice) | OPEN | **In scope** — the plan already touches both linter copies; consolidating the duplicate without addressing the missing rules would enshrine the false-negative green | Decision 1b (new); Steps 1b, 8 |
| #648 CHG linter + IPLAN Gate (GOV-011/012/013) | OPEN | **In scope as provenance** — this is the issue that created the `scripts/chg_lint.py` + `sdd_doc_lint/chg_lint.py` duplicate; closing it requires naming the single canonical copy | Decision 1 |
| #644 EVAL template gaps + EVAL-COV-002/003/004 | OPEN | **Context only** — already applied per its body; explains why `10_EVAL`/`10_IPVERIFY` playbooks are the ones missing frontmatter keys. No new EVAL rule work in this plan | Decision 8 |
| #574 SYNC-HOOK-FRAMEWORK-VERSION-DEAD (+ #405, the `replace_in_file_counted` expected-count guard it regressed) | CLOSED | **Applicable** — the dead-trigger class Decision 4 must not reintroduce; R2 names both | Decision 4, R2 |
| #556 SYNC-FWPREV-TRAP-STALE | CLOSED | **Applicable** — `fw_prev` source must be `docs/PARITY.md`... but `docs/PARITY.md` no longer exists; the restore must not re-derive the stale source | Decision 4 |
| #548 vendored-mirror trap contradiction (PARKED) | CLOSED | **Applicable** — 'No script does it' vs `sync-vendored.sh`; deletion resolves the contradiction rather than rewording it | Decision 2 |
| #577 COV01-UNTESTED | CLOSED | **Applicable** — forward coverage firing on zero targets is the failure mode Decision 7 must not reproduce when repointing the coverage test | Decision 7 |
| #588 IDENTITY-CARRIER-SPLIT | CLOSED | **Applicable** — background for `test_instance_format_ssot` / carrier-parity failures | Step 3 |
| #558 SPEC-RELEASE-PROVENANCE (+ guard #617) | CLOSED | **Applicable** — background for `test_release_record_integrity` failures; do not "fix" by weakening the phantom-release guard (#620) | Step 3 |
| #604 pin-census wrong | CLOSED | **Applicable** — `CLAUDE.md` pin census must be re-derived, not copied, when touching docs | Step 7 |
| #633 prose guards can't tell instruction from description | CLOSED | **Applicable** — prose-guard failures in the 186F bucket must be fixed by rewording the guard or the prose, never by deleting the guard | Step 3 |
| #567 PLATFORM-INSTANCE-FORMAT-LOCK, #563 REFGRAN-SKILL-DRIFT | CLOSED | **Moot by deletion** — platform authoring surfaces are gone; cited as rationale for deleting (not repairing) platform-coupled tests | Decision 5/6 |
| Remaining ~100 closed issues (representative high-risk subset reviewed: ai-review/D-0084 family #596/#597/#599/#600/#611/#623, #585, #613, #553, #602, #550–#552, #554/#555/#557, #564–#566, #569, #601/#621/#632/#635–#637/#639–#642, #603/#606/#609/#614/#617/#620; 150 total issues, 3 open) | CLOSED | **Not applicable** — spec debt, platform agents, CI canon, or already-shipped fixes; no cleanup action | — |

## Objective

Commit `bd32a927` deleted `archive/` (897 files), `examples/` (129 files), and `tmp/` (1 file), completing the reduction to a framework-only repo (`docs/`, `framework/`, `hooks/`, `scripts/`, `sdd_doc_lint/`, `tests/`). The code that referenced the deleted world was not updated: conformance is red (355 tests, 186 failures + 40 errors on 2026-09-20), one hook fails closed on every Python commit, one hook is a stub the suite expects to be a full sync script, and four test suites have no subject. This plan repairs the repo to match its new shape without changing the framework spec.

## Scope

**In:**

- Dead/duplicate scripts (`sdd_doc_lint/sync-vendored.sh`, `scripts/chg_lint.py`).
- `hooks/ch-gate-check.sh` wrong `CHG_DIR`; `hooks/sync-version-refs.sh` stub vs `test_sync_version_refs_counts.py` expectations; `hooks/check-docs-updated.sh` `examples/*` pattern.
- `tests/conformance/_spec.py` duplicate `plugin_bundle_root()` (`:95` overrides `:45`); `platforms/`-coupled tests (`test_plugin_hook_safety.py`, `test_sync_version_refs_counts.py`, `test_coverage_engine.py`, `test_carrier_parity.py`, `test_release_record_integrity.py`, `test_ref_granularity_parity.py`, `test_required_section_sets.py`, `test_spec_gate.py`, `test_precommit_trigger_reachability.py` docstring).
- `tools/`-coupled refs (`tests/packaging/test_bundle_integrity.py`, `tests/conformance/test_carrier_parity.py`, `test_forward_coverage_is_exercised.py`, `test_iplan_code_inventory_lifecycle.py`, `test_diagram_allowlist_source.py`, `tests/chg/spec_gate.py:120`, `.github/workflows/doc-review.yml:69`, `sdd_doc_lint/tests/test_lint.py:3`, `test_sdd_trace_graph.py:1`, `test_threshold_quoted_scalar.py:16`, `test_threshold_resolution.py:14`, `trace_graph.py:10-13`, `__init__.py:4-6`, `tests/acceptance/_id_coordinator.py:19-21`).
- Subject-less suites: `tests/smoke/`, `tests/review/`, `tests/packaging/`, `tests/release/` (delete or quarantine — decision per suite, §Approach).
- `tests/unit/` registration gap (4 of 18 registered in `test_repo_scripts.py:31`).
- Playbook frontmatter: 16 files lacking `framework_spec_version` (10 × layer `README.md`, 6 × `10_EVAL`/`10_IPVERIFY` playbooks), 51 playbooks pinned at `"0.50.0"` vs `VERSION 0.53.2`.
- Doc/config drift: `docs/REPO_STRUCTURE.md:69,93-94`, `docs/STARTUP_HANDOFF.md` header, `README.md:80,336,346`, `CLAUDE.md:138,828,838`, `CONTRIBUTING.md:41`, `framework/governance/DOC_GOVERNANCE_CORE.md:12,174,188,191,221`, `GOVERNANCE.md:58,66`, `docs/TAGGING.md` high-water (still claims `framework/v0.51.0`, spec at `0.51.0`; VERSION is `0.53.2`, tag `framework/v0.53.1` exists), `.pre-commit-config.yaml` comments, `.github/workflows/markdown-lint.yml:59,71`, `.gitignore` (`examples/*/logs/`, `.claude/commands/bmad/`, `ai_dev_flow/...`).
- `hooks/hooks.json` still interpolates `${CLAUDE_PLUGIN_ROOT}` for both hook commands — a platform-bundle variable with no meaning in the framework-only repo.
- `hooks/pre_push_check.sh:53-56,166` computes changed-files against `origin/main`, but this repo works `feat/*` → `dev` (`origin/HEAD` → `origin/dev`); on a branch off `dev` the BASE range mismeasures the diff.
- After `scripts/chg_lint.py` deletion the `scripts/` dir is empty — delete the dir, don't leave an empty shell.

**Out of scope (deferred):**

- Any `framework/` spec change beyond Step 1b's conditional PATCH (no template/layer edits beyond frontmatter version pins and the archive-scope text fix).
- `framework/archive/CHG-01`, `CHG-02` — pre-existing spec-history snapshots, not the deleted top-level `archive/`; untouched.
- Restoring `examples/url-shortener` as a live corpus — deleted deliberately; coverage tests must stop requiring it, not resurrect it.
- Restoring `tools/sdd_coverage.py` / `tools/sync-plugin-framework.sh` — deleted deliberately; consumers must be repointed or removed.
- `framework/scripts/` IPLAN helpers — present and referenced correctly; verify only.
- New features or breaking changes queued behind this cleanup.

## Approach / Design

### Decision 1 — one `chg_lint.py`, not two

`scripts/chg_lint.py` and `sdd_doc_lint/chg_lint.py` are byte-identical. Keep `sdd_doc_lint/chg_lint.py` (importable, tested), delete `scripts/chg_lint.py`, repoint the ~10 doc references (`CLAUDE.md:138`, `DOC_GOVERNANCE_CORE.md:174,188,191,221`, `GOVERNANCE.md:58,66`, both files' own usage strings) at `python -m sdd_doc_lint.chg_lint` / `python sdd_doc_lint/chg_lint.py`. This resolves the duplication #648 introduced; comment on #648 naming the canonical copy when the PR lands.

### Decision 1b — #652: implement C16–C20 + D21/D22, fix archive-scope text (OPEN issue)

#652 proves the consolidated linter green-lights CHGs with 20× null `archive_path` / null `new_version`, empty `supersedes`, and no `archive/CHG-XX/` directory: the C16–C20/D21/D22 rules from `DOC_GOVERNANCE_CORE.md:113-124` exist in prose only (zero matches in either linter copy). Consolidating the duplicate without adding the rules would bless the false negative. So in the same step: (a) implement null-`archive_path`/`new_version` on non-IPLAN-create `sdd_lifecycle` entries = error, `supersedes` completeness, cited EARS/BDD ID existence; needs #652's grandfathering decision for CHG-22/23/24-style docs — record it in `framework/governance/DECISIONS.md`; (b) fix the archive-scope text (`framework/layers/09_CHG/README.md:176` lists only `06_SPEC`/`07_TDD`/`08_IPLAN`, but real CHGs modify `03_EARS`/`04_BDD`); (c) resolve rewrite-vs-extend (docs demand clean rewrites + version → 2.0, every merged CHG does minor-bump appends with CHG tags) — bless one, enforce it in the linter. (b) is a governance doc change, so shipping it moves version impact to PATCH `0.53.2 → 0.53.3`; (a)+(c) alone are linter-only.

### Decision 2 — `sync-vendored.sh`: delete, not repair

Its only destinations were `archive/platforms/*` (commented out; loop body copies nothing). No live consumer. Delete the file and its `__init__.py:6` / `trace_graph.py` mentions. Deletion (not rewording) also resolves the #548 PARKED contradiction ('No script does it' vs naming the script) — cite #548 in the commit.

### Decision 3 — `ch-gate-check.sh`: repoint, keep enforcing

`CHG_DIR="docs/sdd/09-CHG"` never exists in this repo (real template dir: `framework/layers/09_CHG/`; no instance CHG dir exists at all). Fails closed on every `*.py` commit. Fix the path per the actual CHG instance location the governance process defines; if no instance dir exists by design in the framework-only repo, convert to warn-only until the CHG workflow lands. Do not leave a gate that can never pass.

### Decision 4 — `sync-version-refs.sh`: restore or retire the contract

`hooks/sync-version-refs.sh` is a 28-line echo stub; `test_sync_version_refs_counts.py:27` expects `scripts/sync-version-refs.sh` with `replace_in_file_counted` and three VERSION sources (`framework`, `platforms/claude-code-plugin`, `platforms/hermes`). Two of three sources are gone. Either restore a real framework-only sync (single source `framework/VERSION`, real `replace_in_file_counted` calls, test repointed at `hooks/`) or delete both script and test. No stub-with-a-test-that-expects-the-real-thing middle state. Constraints from closed issues: the restored trigger must not reintroduce the #574 dead half (global `exclude:` applied after `files:`); the `fw_prev` detector source per #556 is `docs/PARITY.md` — which no longer exists — so the restore must name the new source explicitly rather than re-deriving the stale one.

### Decision 5 — subject-less suites: delete

`tests/smoke/` (marketplace install via `claude` CLI), `tests/review/` (LLM review), `tests/packaging/` (bundle byte-identity, `claude plugin validate --strict`), `tests/release/` (bundle size, marketplace gate) test artifacts that no longer exist. No workflow invokes them (verified 2026-09-20). Delete the four dirs. If any guard is still wanted (e.g. version alignment), re-home the single assertion into conformance rather than keeping the suite.

### Decision 6 — `_spec.py`: one `plugin_bundle_root`, no `platforms/`

Delete the second definition (`:95`, `PLATFORMS_ROOT`-based); keep `:45` (`sdd_doc_lint`). Rehome `platform_dirs()` / `platform_version_file()` / `platform_framework_spec_version_file()` or delete with their consumers (`test_release_record_integrity.py:247`, `test_skill_manifests.py`, `test_nonlayer_skills.py`, `test_sync_scripts.py`). `test_plugin_hook_safety.py:39-41` repoints at `hooks/sdd-doc-review.sh` + `hooks/hooks.json`. #567/#563 (platform authoring-surface locks) are moot — the surfaces are gone — and are cited as the rationale for deleting rather than repairing these tests. #588 is background for the carrier-parity failures fixed in Step 3; #558/#617 background for the release-record failures — do not weaken the phantom-release guard (#620) to go green.

### Decision 7 — coverage engine without the example corpus

`test_coverage_engine.py:30` requires `examples/url-shortener/docs` + `tools/sdd_coverage.py`. Since both are gone by design, the test must either drive the engine over `sdd_doc_lint/tests/lint_fixtures/` (or another in-tree fixture) or be deleted with the engine. Do not resurrect the corpus to satisfy the test. Per #577, the repointed test must exercise fixtures whose BRD §7 the scanner can actually see — otherwise forward coverage passes on zero targets again.

### Decision 8 — playbook frontmatter: pin to 0.53.2

Add `framework_spec_version: "0.53.2"` to the 6 playbooks missing it (`10_EVAL/author.md`, `10_IPVERIFY/evaluator.md`, `report_generator.md`, `validator.md`, `verifier.md`, plus check `10_EVAL` remainder — #644 is why these EVAL playbooks are the ones behind); decide README-vs-playbook contract for the 10 layer `README.md` files (exempt READMEs in the test or give them frontmatter — one rule, applied to all 10). Bump the 51 `"0.50.0"` pins to `"0.53.2"`. This is the largest failure bucket (53 + 5) and the cheapest fix.

### Decision 9 — `tests/unit/`: register all or wire the dir

14 of 18 modules run nowhere (no hook, no workflow; `test_repo_scripts.py` names 4). Either extend `REGISTERED` to all runnable modules (fixing `test_sync_scripts.py` / `test_skill_manifests.py` / `test_sdd_coverage.py` stale paths first) or wire `tests/unit` into `.pre-commit-config.yaml` + CI. The file's own docstring (references `tests/scripts/test-plugin.sh`) gets corrected either way.

## Step sequence

1. **Dead scripts** — delete `sdd_doc_lint/sync-vendored.sh`, `scripts/chg_lint.py` (or keep as shim — one rule); repoint doc usage strings; fix `__init__.py:4-6`, `trace_graph.py:10-13` comments.
1b. **#652 (OPEN)** — implement C16–C20 + D21/D22 in the surviving linter; fix `09_CHG/README.md:176` archive scope (`03_EARS`/`04_BDD`); resolve rewrite-vs-extend; record grandfathering in `framework/governance/DECISIONS.md`. Run `python sdd_doc_lint/chg_lint.py` over the in-tree CHG fixtures as the check.
2. **Hooks** — fix `ch-gate-check.sh` `CHG_DIR`; resolve `sync-version-refs.sh` stub-vs-test (restore or retire both); drop `examples/*` from `check-docs-updated.sh`; repoint `hooks.json` `${CLAUDE_PLUGIN_ROOT}` at the repo-local `hooks/` dir; repoint `pre_push_check.sh` BASE from `origin/main` to `origin/dev` (with fallback chain preserved).
3. **`_spec.py` + hook/coverage tests** — dedupe `plugin_bundle_root()`; repoint `test_plugin_hook_safety.py`, `test_sync_version_refs_counts.py`, `test_coverage_engine.py`, `test_carrier_parity.py`, `test_release_record_integrity.py`, `test_ref_granularity_parity.py`, `test_required_section_sets.py`, `test_spec_gate.py`; fix `tests/chg/spec_gate.py:120`, `doc-review.yml:69`, `sdd_doc_lint/tests/*tools*` comments, `_id_coordinator.py:19-21`. Prose-guard failures (#633 pattern: instruction vs description) are fixed by rewording guard or prose, never by deleting the guard (R4).
4. **Subject-less suites** — delete `tests/smoke/`, `tests/review/`, `tests/packaging/`, `tests/release/` (re-homing any kept assertion into conformance).
5. **`tests/unit/`** — fix stale paths in `test_sync_scripts.py`, `test_skill_manifests.py`, `test_nonlayer_skills.py`, `test_sdd_coverage.py`; extend `REGISTERED` (or wire the dir); fix the `test-plugin.sh` docstring.
6. **Playbooks** — add missing `framework_spec_version`, bump `0.50.0` → `0.53.2`, settle README contract.
7. **Docs/config** — `REPO_STRUCTURE.md`, `STARTUP_HANDOFF.md` header, `README.md`, `CLAUDE.md:138,828,838`, `CONTRIBUTING.md:41`, `DOC_GOVERNANCE_CORE.md`, `GOVERNANCE.md`, `docs/TAGGING.md` high-water refresh (re-derive cut marks from `git tag -l`, don't copy the `v0.51.0` snapshot), `.pre-commit-config.yaml` comments, `markdown-lint.yml:59,71`, `.gitignore`. Re-derive the `CLAUDE.md` pin census from the tree (#604), don't copy the old figures.
8. **Verify** (see below). `chg_lint` C16–C20/D21/D22 check on in-tree fixtures included.
9. **Land:** commit on `feat/clean-up`; PR `feat/clean-up` → `dev`. VERSION bump only if Step 1b's governance-doc half ships (PATCH `0.53.2 → 0.53.3` + mechanical fanout); pure-cleanup steps are tooling-only. Include the OPS-0065 self-review phrase in the commit message (`call / verify` greps it literally). `plans/` is currently untracked (`?? plans/` in `git status`; no `plans/` in `origin/dev`) — `git add` the plan in the same branch so it lands with the work.

## Verification

- `python -m unittest discover -s tests/conformance` — green (baseline 2026-09-20: 355 tests, 186F + 40E; target 0F/0E).
- `python -m unittest discover -s sdd_doc_lint/tests` — green.
- `python -m unittest discover -s tests/acceptance/deterministic` — green.
- `python -m unittest discover -s tests/unit` — green (post-registration).
- `grep -rn "platforms/\|tools/\|examples/" --exclude-dir=.git --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" . | grep -v "archive/platforms"` — only historical mentions in changelogs/decisions remain; zero live path references.
- `bash hooks/ch-gate-check.sh` on a staged `*.py` file — passes or warns per Decision 3, never fails on a missing dir.
- `pre-commit run --all-files` — clean.
- `git ls-files | grep -E "^(tests/smoke|tests/review|tests/packaging|tests/release)/"` — empty.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Deleting a suite that a workflow still needs | Verified 2026-09-20 no workflow references the four suites; re-verify at impl time with the same grep |
| R2 | `sync-version-refs` restore vs retire re-opens the #405/#574 debate | Keep the decision binary (full restore or full retire); record it in `framework/governance/DECISIONS.md` |
| R3 | Playbook bulk version bump masks real drift | Bump is mechanical (`0.50.0` → `0.53.2`); any semantic playbook change stays a separate commit |
| R4 | Fixing tests to match the repo instead of the spec (weakening checks to go green) | Each test change cites the deleted path it tracked; conformance stays a contract on `framework/`, never loosened for convenience |
| R5 | `ch-gate-check.sh` path fix authorizes the wrong CHG location | Derive the path from `DOC_GOVERNANCE_CORE.md`, not by invention; warn-only until the CHG workflow exists |

## Review log

### Pass 1 — 2026-09-20T00:00:00Z (pre-issue-triage)

- Drafted 9 decisions + 9 steps from tree evidence + conformance baseline (355 tests, 186F + 40E).

### Pass 2 — 2026-09-20 (GitHub issue triage: 3 open + closed backlog)

- Census: only #652, #648, #644 are open (150 total issues).
- #652 (OPEN) folded in as Decision 1b + Step 1b: C16–C20/D21/D22 implementation, archive-scope text fix, rewrite-vs-extend resolution, grandfathering record. Version impact updated to conditional PATCH.
- #648 (OPEN) cited as provenance for the linter duplicate (Decision 1); close by naming canonical copy.
- #644 (OPEN) noted as context for EVAL playbook frontmatter lag (Decision 8); no new EVAL work.
- Closed issues wired: #574 + #556 → Decision 4 constraints; #548 → Decision 2; #577 → Decision 7; #588/#558/#617/#620 → Step 3; #633 → Step 3/R4; #567/#563 → Decisions 5/6 rationale; #604 → Step 7.
- Ruled out: ai-review/D-0084 family, CI canon, platform agents, already-shipped spec fixes — no cleanup action.

### Pass 3 — 2026-09-20 (final review)

- F1 — Step 9 said "No VERSION bump (tooling-only)" while the header + Decision 1b say conditional PATCH `0.53.2 → 0.53.3`. Fixed Step 9 to the conditional form; "Out of scope" now reads "beyond Step 1b's conditional PATCH".
- F2 — `hooks/hooks.json` `${CLAUDE_PLUGIN_ROOT}` (both hook commands) was unmentioned. Added to Scope + Step 2: repoint at repo-local `hooks/`.
- F3 — `hooks/pre_push_check.sh:53-56,166` diffs against `origin/main`, but work flows `feat/*` → `dev`. Added to Scope + Step 2.
- F4 — Deleting `scripts/chg_lint.py` empties `scripts/`; plan now says delete the dir, not leave the shell.
- F5 — `docs/TAGGING.md` high-water (`framework/v0.51.0`, spec `0.51.0`) vs VERSION `0.53.2` / tag `framework/v0.53.1` was missing. Added to Scope + Step 7 with a re-derive-from-`git-tag` rule.
- F6 — Triage table implied a full closed-issue census from a `--limit 200` sample of named issues; actual total is 150. Table now states the total and frames the list as a reviewed high-risk subset; #405 named alongside #574 in R2.
- F7 — `framework/archive/CHG-01|CHG-02` (spec-history snapshots) could be misread as the deleted top-level `archive/`. Explicitly untouched in "Out of scope".
- F8 — `plans/` is untracked (`?? plans/`, absent from `origin/dev`). Step 9 now stages the plan with the work.
- No new findings beyond F1–F8. Plan is final; implementation may start at Step 1.
