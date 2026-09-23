# STALE Remediation Plan — framework stale-review findings → implementation (report rev.2 + readiness pass 2026-09-22)

| Field | Value |
|-------|-------|
| Task | STALE-REMEDIATION |
| Type | cleanup (test/hook/linter repair + doc sweeps; spec-content decisions where flagged) |
| Status | READY FOR PLAN PR — 2 review passes complete (2026-09-22); implementation still gated on authoring CHG + IPLAN per §Step sequence |
| Depends on | `84b1b9af` (CHG-05 / 0.56.0, current `dev`); CLEANUP-001 (shipped shape: framework-only repo) |
| Feeds | green `tests/unit` + conformance signal; EVAL/CHG canon decisions recorded in `framework/governance/DECISIONS.md` |
| Version impact | SETTLED (pass 2): Steps 2–3 (T1/T2/T3) tooling/test/hook-only → none; Step 4 (P1) touches `framework/` templates + governance prose + schema → MINOR `0.56.0 → 0.57.0`; Steps 5–6 (P2/D5/D6) docs + test-fixtures only → none |

## Objective

Turn the verified stale-review findings below (P0/P1/P2, rev.2 with independent-review corrections) into an executable work plan that restores a green signal and a single canon for every forked/duplicated surface, without weakening any conformance contract to go green. Anything broader — new layers, registry shape changes, new lint rules beyond the listed contradictions — is explicitly out.

## Scope

**In:** T1 red-`tests/unit` quarantine-then-delete; T2 `chg_lint.py` vs governance contradictions; T3 hook gate defects; P1 items 1–7 (canon decisions + tombstone/delete + conformance pins); P2 doc sweeps D1–D6 (mechanical, after P0/P1).

**Out of scope (deferred):** new SDD layers / registry shape changes; restoring deleted corpora (`archive/`, `examples/`, `tools/`, `platforms/`, `scripts/`) to satisfy tests — consumers are repointed or removed, never resurrected; spec changes beyond the flagged canon rows (EVAL/CHG rows, §File Naming rewrite, CHG template §7/enumeration).

## GitHub issues — triage (2026-09-22; filed 2026-09-22, all OPEN unless noted)

Census at readiness time: **0 open issues** (`gh issue list --state all` showed #656/#657/#652/#648/#644 all CLOSED). Searched before filing (`STALE stale-review quarantine tests/unit`; `chg_lint L002 L003 L004`; `hook gate ch-gate sync-version`; `EVAL-RPT CHG fork canon IPVERIFY`; `dead paths doc sweep branch truth`) — no duplicates. Filed one issue per defect class with verbatim analysis + `file:line` reproduction + run blast radius; every body read back with non-zero length (`gh issue view <N> --json body --jq '.body | length'`). PR body carries `Closes #N`, one keyword per reference.

| Finding | Issue | State |
|---|---|---|
| T1 red `tests/unit` | #665 | OPEN |
| T2 `chg_lint.py` contradictions | #668 | OPEN |
| T3 hook gate defects | #663 | OPEN |
| P1-1 EVAL report fork | #664 | OPEN |
| P1-2 CHG template fork | #667 | OPEN |
| P1-3 10_EVAL vs 10_IPVERIFY | #672 | OPEN |
| P1-4 MVP templates | #666 | OPEN |
| P1-5 verification-vehicle split | #662 | OPEN |
| P1-6 triple-lock misses | #671 | OPEN |
| P1-7 §File Naming rewrite | #669 | OPEN |
| P2 D1–D6 sweeps | #670 | OPEN |

Step 1 gate satisfied (T1 issue #665 exists); the merge closes the issue(s).

## How to read this plan

§§P0/P1/P2 below are the **verbatim finding record** (rev.2, corrections applied) — the audit trail. The executable part is §Step sequence + §Verification + §Risks. Finding text is normative for *what is wrong*; the step sequence is normative for *order and done-criteria*. Where they disagree, the step sequence wins and the finding gets a correction-log entry.

## Ground-truth re-verified at readiness pass (2026-09-22)

- `framework/VERSION` = **0.56.0**, branch `dev` tracking `origin/dev` (`feat/* → dev → main`).
- T1 still reproduces: `python3 -m unittest discover -s tests/unit` → `Ran 83 tests — FAILED (failures=24, errors=9, skipped=15)` (exit-127 `scripts/reconcile-pin-currency-issue.sh` missing confirmed in output).
- EVAL fork still live: `framework/layers/10_EVAL/` ships both `EVAL-REPORT-TEMPLATE.yaml` and `EVAL-RPT-TEMPLATE.yaml`; `framework/playbooks/10_EVAL/` + `10_IPVERIFY/` both present (11 dirs for 10 layers).
- CHG fork still live: `framework/layers/09_CHG/` vs `framework/governance/chg/` both ship `CHG-TEMPLATE.yaml` + `README.md`.
- Original rev.2 ground truth (preserved): `origin/HEAD → origin/dev` (`feat/* → dev → main`).
Method: 4 parallel deep reviews (core docs / layers+governance+playbooks / hooks+linters+scripts / tests),
every claim verified against the live tree (`ls`, `git tag`, imports, test runs).
Counts below (365 conformance tests, ~20 `tools/` fossils, 24 failures + 9 errors) are point-in-time values —
re-derive with the commands in §Verification before quoting.

## P0 — red suite, wrong gates, linter-vs-governance contradictions (fix first)

### T1. `tests/unit` is RED on a clean tree (24 failures + 9 errors)

| File | Cause | Fix |
|---|---|---|
| `tests/unit/test_skill_manifests.py:11` | `from _spec import skill_dirs` — helper gone with plugin archival | quarantine first (skip/stub `[]`), then delete |
| `tests/unit/test_sdd_coverage.py:1,17` | `from sdd_coverage import render_matrix` — `tools/` deleted | quarantine first (skip), then delete (covered by `sdd_doc_lint` + `test_forward_coverage_is_exercised.py`) |
| `tests/unit/test_gherkin_to_bdd_yaml.py:1,17` | `gherkin_to_bdd_yaml` gone from `sdd_doc_lint/` | quarantine first (skip), then delete or restore transcoder |
| `tests/unit/test_finding_check_field.py:10,15,63` | `platforms/claude-code-plugin/tools` path gone (5 ERRORs) | quarantine first (skip), then delete or move `finding_filter` into `sdd_doc_lint/` |
| `tests/unit/test_saga_reconcile_post_audit.py:32,34` | `tools/saga_driver.py` retired by CLEANUP-001 | quarantine first (skip), then delete (not a marked tombstone) |
| `tests/unit/test_pin_currency_reader.py:29` | needs deleted root `scripts/reconcile-pin-currency-issue.sh` (~24 FAILs, exit 127) | quarantine first (skip), then delete or restore helpers |
| `tests/unit/test_nonlayer_skills.py:12-13` | `sdd_doc_lint/skills/` doesn't exist | quarantine first (skip), then delete or repoint at `framework/playbooks/` |
| `tests/unit/test_sync_scripts.py:32-33,64-65` | all `tools/…sync-*.sh` candidates gone → permanent `skipTest` dead guards | quarantine first (skip), then repoint at `hooks/sync-version-refs.sh` or delete |
**Remedy policy (applies to the whole table): quarantine/skip first, delete second** — several modules encode
re-anchorable contracts; deletion destroys the audit trail (independent-review finding 11).

### T2. `chg_lint.py` contradicts governance (false positives / false negatives)

- `sdd_doc_lint/chg_lint.py:103-130` (CHG-L002) errors on `Proposed` C3 drafts; `governance/LINT_RULES.md` GOV-012 permits them → early-pass on `Proposed`.
- `chg_lint.py:88-98` duplicates the C3-approver check inside L001 → double-report under two codes; delete L001 copy.
- `chg_lint.py:132-164` (CHG-L003) never errors on missing `phase`, keyword heuristic warns on legit titles ("implement SDD lifecycle") → add missing-phase error, drop heuristic.
- `chg_lint.py:167-199` (CHG-L004) hunts top-level `sdd_lifecycle` list, but canon `CHG-TEMPLATE.yaml:163-211` links IPLAN via `implementation.steps[]` (`phase: iplan_creation`) → scan steps. Severity escalation needs an authorizing rule: GOV-013 does **not** cover this (it is the IPLAN Gate — code-without-IPLAN, `LINT_RULES.md:131`); cite the correct rule or mint one before escalating warning→error. (Corrected per independent review: earlier rev cited GOV-013.)
- `chg_lint.py:202-247` (CHG-L005) `code_phases` arm only fires on already-noncompliant docs → fold into L003 or delete.
- `chg_lint.py:317,594` inner `import re` shadows top-level `:46` → remove.
- `chg_lint.py` ↔ `bugfix_lint.py` share parallel scaffolding (candidate for a `_common.py` extraction — verify before acting):
  PyYAML-guard `sys.exit(3)` (`chg_lint.py:55` vs `bugfix_lint.py:37`), loader (`yaml.safe_load` inline at
  `chg_lint.py:659` vs `_load()` at `bugfix_lint.py:58,66`), entry points (`lint_chg` at `chg_lint.py:651` /
  `main` at `:688` vs `lint_bugfix` at `bugfix_lint.py:307` / `main` at `:348`), and divergent element-ID
  patterns (`ELEMENT_ID_FULL/SHORT` at `chg_lint.py:394-395` vs `_ELEM_ID` at `sdd_doc_lint/__init__.py:287` and
  `ELEM_FORM` at `trace_graph.py:43`) → unify the ID pattern; extract shared load/guard/exit helpers.
- Coverage gap: `sdd_doc_lint/tests/test_chg_lint.py` has 11 test methods covering ≈L006–L011 + attestation paths, with zero cases touching L001–L005; CHG-04 `reconciliation` and CHG-05 bugfix interplay untested → add fixtures + cases.

### T3. Hook gate defects

- `hooks/ch-gate-check.sh:40,59` scans `framework/layers/09_CHG`, so the template dir is in the scan list. No false positive reproduces today — the hook only treats `status: In-Progress|Approved` as active (`:59-68`) while `CHG-TEMPLATE.yaml:30` is `Draft` (and `:102` `Proposed`), and the gate is warn-only (`exit 0` at `:50-54,70-82`). Advisory hygiene only: skip `*TEMPLATE*` or drop the template dir so a future status-value edit can't arm it. (Corrected per independent review: earlier rev claimed an active false positive.)
- `hooks/ch-gate-check.sh:23-33` watches `*.go` (nothing in tree) but not `*.sh` (all executable code) → add `*.sh`.
- `hooks/ch-gate-check.sh:81` "bug-fix exception via commit message" never reads a commit message → check `git log -1 --format=%B` or delete line.
- Gate not wired into `.pre-commit-config.yaml` (only via `hooks/hooks.json` Claude path) → pre-commit users get no CHG gate; add local hook or document split.
- `hooks/check-docs-updated.sh:20-25` list (`CHANGELOG, README, CLAUDE, DECISIONS`) contradicts pre-commit comment (`+ ROADMAP, HANDOFF` — both nonexistent as named) and omits versioned `framework/CHANGELOG.md` → resync list.
- `hooks/sync-version-refs.sh:86-102` hardcoded literals (`0.50.0/0.53.0/0.53.2/0.54.0/0.55.0`) miss `0.56.0` and `0.53.3/0.51.0/0.52.0`-era pins still in the tree → next bump silently no-ops; sweep by regex + add conformance test. `:83` ("Step 6 of CLEANUP-001 pins these at 0.53.3") is a historical note, not a live pin — leave it. Scope: `:2-17` touches only `framework/**` while the hook name promises README/CHANGELOG — rename the hook to its real scope. Do **not** extend the sweep to `README.md:303-308` / `docs/TAGGING.md:108-136`: both declare point-in-time snapshots explicitly excluded from the sync; fix those by rewording the prose, not by sweeping them. (Corrected per independent review: earlier rev recommended extending the script.)
- `hooks/pre_push_check.sh:6` cites `scripts/pre_push_check.sh` (no `scripts/` dir) → `hooks/…`; `.pre-commit-config.yaml:155` bare `entry: hooks/pre_push_check.sh` breaks on Windows checkouts → `bash hooks/…`.
- `hooks/sdd-doc-review.sh:43,78,140-189` cites `skills/project-profile/SKILL.md`, `docs/CONFIG.md` (absent), plugin-install layout (archived), unreachable no-`framework/` branch → repoint + prune.

## P1 — live duplications / forks (pick a canonical, delete or tombstone the other)

1. **EVAL report fork (highest-risk drift).** `framework/layers/10_EVAL/EVAL-REPORT-TEMPLATE.yaml` (11 sections, §4 `test_results`, `EVAL.NN.SS.xxxx`) vs `EVAL-RPT-TEMPLATE.yaml` (§4 Findings, stale `EVAL-NN.BDD-NN.TC-NN.NN` at :121, `BDD.NN.TC-NN.NN` also in `EVAL-TEMPLATE.yaml:203`). The 10_IPVERIFY playbooks are internally split — outputs are defined as EVAL-RPT (`evaluator.md:3,14,33`, `report_generator.md:3,13,32`, `10_IPVERIFY/README.md:38` "Generates EVAL-RPT") while procedure steps cite `EVAL-REPORT-TEMPLATE.yaml` as base (`evaluator.md:162`, `report_generator.md:120`); README + index template list only REPORT. **Fix:** resolve the name-vs-template contradiction first, then declare canon (REPORT recommended), delete/tombstone the other; add conformance pins on `test_results` + ban old ID form — EVAL *template-shape* pins are uncovered today (EVAL layer wiring itself exists: `_spec.py:23,25,73`, `test_acceptance_pairing.py:166-184`). (Corrected per independent review: earlier rev claimed playbooks cleanly point at REPORT and that no test covers EVAL at all.)
2. **CHG template fork.** `framework/layers/09_CHG/` vs `framework/governance/chg/` gates+templates byte-identical *except* `CHG-TEMPLATE.yaml` forked (`layer: 9` key only in layer copy `:51`; §7 `validation:` 36 lines only in governance copy `:392-427`) and READMEs forked at `:208` (layer copy: 8-layer archive enumeration `01_BRD…08_IPLAN`; governance copy: 3-layer `06_SPEC,07_TDD,08_IPLAN` — neither covers 09_CHG/10_EVAL). **Fix:** decide content first (keep or drop the §7 block; adopt the 8-layer enumeration, which matches `DOC_GOVERNANCE_CORE.md` §3.1.1), then declare canonical home (recommend `governance/chg/`), sync, leave pointer/symlink. (Corrected per independent review: earlier rev picked the home without settling the content dispute.)
3. **10_EVAL vs 10_IPVERIFY playbooks.** 11 dirs for 10 layers; both READMEs define the same "IPLAN Completed → EVAL → cycles → Verified" model over the same `docs/sdd/10_EVAL/` tree, neither names the other canonical. `10_IPVERIFY/validator.md:5` is `layer: 08_IPLAN`, drives `IPLAN-VERIFY-TEMPLATE` while siblings drive EVAL-RPT; README table lists 3 of 4 playbooks. **Fix:** 10_EVAL = authoring, 10_IPVERIFY = execution/verification (or merge); for `validator.md`, retarget to the EVAL-RPT flow first — tombstone/delete only after retargeting its live readers (`08_IPLAN/README.md:164-177`, `framework/CHANGELOG.md`, `test_iplan_bugfix_lifecycle.py`); fix `framework/README.md:81-84` (claims "10 folders … through 09_CHG plus 10_IPVERIFY", omits 10_EVAL).
4. **MVP templates (8 files) use a retired schema** (`status: draft`, `lifecycle: mvp`, flat `*_id`, bare-list manifests; `IPLAN-MVP` `session_handoff: {last_session…}` vs normative `sessions[]`). READMEs never mention MVP. **Fix:** delete or tombstone + drop from "one template per layer" claim (`DOC_GOVERNANCE_CORE.md:42-47` already false: IPLAN ships 3, EVAL ships 3).
5. **Verification vehicle split.** `08_IPLAN/README.md:164-177` + `framework/scripts/*.sh` + `PLAN_STANDARD` still teach "Create IPLAN-VERIFY" / `tmp/TMP-IPLAN-*.yaml` / `audit_fix` outputs, but registry (`LAYER_REGISTRY.yaml:155`) retired `tmp/` in 0.56.0 and canon repair is bugfix-subtype IPLAN (`parent_iplan` + `source_chg`, BGF-01..07). Generated `${id}_validation_fixes.yaml` even fails `bugfix_lint` BGF-01/02 naming. `eval-trend.sh` documented (`10_IPVERIFY/README.md:125-130`) doesn't exist; `run_validation` in `verify_iplan_status.sh:202-244` is a commented-out no-op; two `generate_validation_report()` copies already drifted. **Fix:** retarget scripts to EVAL-RPT or mark deprecated (quarantine first — `08_IPLAN/README.md:164-177` + CHANGELOG + `test_iplan_bugfix_lifecycle.py` still cite the VERIFY flow); delete Temporary-IPLAN row (`framework/layers/08_IPLAN/PLAN_STANDARD.md:24`) with pointer to bugfix naming; add `bugfix` to `IPLAN-VERIFY-TEMPLATE.yaml:30,42` subtype comment + README precedence note.
6. **Triple-lock misses.** Registry ↔ governance ↔ schema must change together; current gaps: `saga.schema.json:34-38` enum lacks `10_EVAL`; `ID_NAMING_STANDARDS.md:7-16,304-314` lacks CHG/EVAL prefixes, lifecycles, index rows + wrong IPLAN scope; `DOC_GOVERNANCE_CORE.md:6` scope "layers 1-8" excludes L10; `TRACEABILITY.md:6,21-29,63-66,102-113` chain/table/prose omit EVAL (and disagree with `TAG_SYNTAX.md:96`); `LINT_RULES.md:93` ACC01 contract cites `SEED_CONTRACT.md` alongside registry `acceptance_layers` (not instead of it — the gap is the missing EVAL/CHG rows, not the citation target). **Fix:** fill all EVAL/CHG rows in one pass.
7. **`ID_NAMING_STANDARDS.md` §File Naming is not the single source it claims to be.** (a) `:316` Document row says slugs exist only for BRD/IPLAN (`` `{TYPE}-NN.yaml` (BRD, IPLAN: `{TYPE}-NN_{slug}.yaml`) ``), but BDD (`BDD-00_index.TEMPLATE.md:60,117`), SPEC (`SPEC-00_index.TEMPLATE.md:58`), TDD (`TDD-00_index.TEMPLATE.md:79`) normatively prescribe `*-NN_{slug}.yaml`, and PRD/EARS/ADR index templates (`PRD-00_index.TEMPLATE.md:76,85`, `EARS-00_index.TEMPLATE.md:85,94`, `ADR-00_index.TEMPLATE.md:81,90`) carry slug allocation rules — while the linter enforces no filename-slug shape at all (`detect_layer`, `__init__.py:331-334`, checks only the `<ARTIFACT>-` prefix). (b) Zero bugfix naming rules anywhere in the file (verified: no match for `bugfix|FIXED|parent_iplan|audit_fix|_bugfix_`) — the live convention exists only in `IPLAN-TEMPLATE.yaml:87`, `LINT_RULES.md:139` (BGF-01), `bugfix_lint.py:89-96`. Adjacent rot in the same pass: `IPLAN-VERIFY-TEMPLATE.yaml:30,42` subtype comment omits `bugfix`; `framework/layers/08_IPLAN/PLAN_STANDARD.md:24` still documents the retired `tmp/TMP-IPLAN-*.yaml` vehicle (see item 5). **Fix:** rewrite `:316` as `{TYPE}-NN_{slug}.yaml` general form with principled carve-outs (EVAL `EVAL-{NN}.yaml` / RPT `EVAL-{NN}-RPT-{NNN}.yaml` per `10_EVAL/README.md:133-135`; CHG `CHG-{NN}.yaml` per `09_CHG/README.md:306`); add a bugfix-filename row (`IPLAN-{NEW}_bugfix_{FIXED}_{slug}.yaml`); decide whether to adopt explicit `PRD/EARS/ADR-NN_{slug}` filename forms — those templates currently carry only generic slug-allocation bullets, not normative filename rules like BDD/SPEC/TDD (VERIFY subtype comment — see item 5). (Added post-independent-review, verified by grep.)

## P2 — doc sweeps (mechanical, do after P0/P1 so docs describe the fixed tree)

### D1. Versions (truth: 0.56.0)

`README.md:301-304` (0.53.0 + v1.1.0 + 2026-09-07), `CLAUDE.md:21` (0.53.0), `docs/PROJECT.md:220` (`0.53.1` must-match), `docs/TAGGING.md:108-119,133-136` (0.51.0/0.44.0 snapshots), `framework/CHANGELOG.md:110` (`0.51.0 — 2026-01-20` breaks sequence), root `CHANGELOG.md:56` (0.53.2 dated 2026-10-23 listed above 0.54.0/2026-09-20; missing 0.55.0/0.56.0 sections that `framework/CHANGELOG.md:18,34` has), `plans/CLEANUP-001-PLAN.md` (pins 0.53.2→0.53.3 — mark point-in-time), `CLAUDE.md:429-437` pin census vs `CHANGELOG.md:100` ci/v4.0.0 claim (re-derive from `.github/workflows/`; verify `actions/checkout@v7`/`setup-python@v7` resolve — v7 series unconfirmed offline, check online).

### D2. Dead paths presented as live (all verified MISSING)

`archive/` (incl `platforms/hermes/`, `platforms/claude-code-plugin/`, `tools/`), `examples/`, root `scripts/`, `tools/`, `platforms/`, `docs/PARITY.md`, `docs/CONFIG.md`, `ROADMAP.md`, `framework/docs/AIDOC.md` (canon: `framework/governance/aidoc/AIDOC.md`), `plans/{HANDOFF,FRAMEWORK-TODO,HERMES-BACKLOG,IPLAN-IPLANIC-DEFERRED,PLAN-TEMPLATE,PLUGIN-TEST-SUITE-PLAN,ACCEPTANCE-SUITE-HISTORY}.md`, `tests/{packaging,smoke,review,live}`, `tests/scripts/{test-plugin,test-acceptance}.sh`, `tests/smoke/COMMANDS.md`, `sdd_doc_lint/sync-vendored.sh`, `scripts/{chg_lint,check-docs-updated,sync-version-refs,reconcile-pin-currency-*.sh}`, `tools/{trace_walk,sdd_coverage,gherkin_to_bdd_yaml,saga_driver,finding_filter,bump_version}.py`, `framework/scripts/eval-trend.sh`, `EVAL-01/02_*strategy.yaml`, `plugin.json`/`marketplace.json`/`52×SKILL.md`.
Sweep command: `rg 'archive/platforms|platforms/hermes|platforms/claude|tools/|examples/<NAME>|scripts/chg_lint|scripts/sync-version|scripts/check-docs|framework/docs/AIDOC|ROADMAP\.md|PARITY\.md|plans/HANDOFF|FRAMEWORK-TODO|HERMES-BACKLOG|IPLAN-IPLANIC-DEFERRED|PLAN-TEMPLATE|PLUGIN-TEST-SUITE|test-acceptance\.sh|test-plugin\.sh|cd framework|framework/tests/' --glob '!STALE*'`.
Heaviest files: `tests/ACCEPTANCE.md` (538-line deleted-system doc — move to `plans/` history or rewrite as deterministic-suite methodology, preserving the record), `tests/{README,HOWTO,ENVIRONMENT,CONTRIBUTING,TROUBLESHOOTING,SCENARIOS}.md`, `tests/conformance/README.md` ("16 modules … plugin"), `tests/unit/README.md:5,17` (`Runs: every PR` contradicts `CLAUDE.md:775` "executed by no hook and no workflow"; `cd framework` broken), `docs/{PROJECT,REPO_STRUCTURE,STARTUP_HANDOFF,SUPPORT}.md`, `CLAUDE.md` (§sync block :825-858, workflow list :510-512 incl `hermes,plugin`, `examples/` cross-check :91-92,193-196, live harness :862+, `sdd_doc_lint/tests + Hermes suite` :778), `CONTRIBUTING.md:41,44,63` (phantom sync targets, HERMES-BACKLOG, `tools/**` trigger), `SECURITY.md:5-6,15,21-22` ("two platforms", "land on main"), `GOVERNANCE.md:58,66` (`:58` also names the live `sdd_doc_lint/` path — half true; `:66` usage line fully dead) + `CLAUDE.md:138` (dual-cites live `sdd_doc_lint/` alongside dead `scripts/` path), `CLAUDE.md:630` (`scripts/check-docs-updated.sh`).

### D3. Branch truth (`feat/* → dev → main`)

Fix every `→ main` / `pull origin main` / `land on main` / `branch from main`: `docs/PROJECT.md:37-42,226`, `SECURITY.md:15,21-22`, `CLAUDE.md:681-692`, `.github/workflows/pre-commit.yml` push leg (`[main]` never fires) → `dev`. AGENTS.md:61-62,105-122 is the correct baseline (re-derived after worktree-pointer insertions).

### D4. Layer language (pick one)

Registry says CHG=L9; `framework/AI_ASSISTANT_RULES.md:38-39`, `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:79`, `framework/TESTING_STRATEGY_TDD.md:29`, `framework/QUICK_REFERENCE.md:17-21,35-36` say "outside layer numbering". Decide, sweep. Same pass: `docs/STARTUP_HANDOFF.md` "8-layer" (:24,177,324,383), `CLAUDE.md:21` "8-layer sequence", `framework/README` 10-vs-11 folders, `NOTICES.md:71,247` double "Issue 5", `NOTICES.md:176-178` vs `archive/CHG-XX` paths, `AGENTS.md:42/44` 42-vs-41 entries (port CLAUDE's pseudo-heading explanation), `10_EVAL/README.md:15` "BeeLocal's" leak, `:212-224` dead strategy-file table, `framework/LEARNED_LESSONS.md` TDD-SYNC-001..009 vs canon A..E (`LINT_RULES.md:151-155`; also `framework/TESTING_STRATEGY_TDD.md:127-134`), `framework/LEARNED_LESSONS.md:104-112,299-310,369` IPLAN-VERIFY workflow + `scripts/verify_iplan_status.sh` path, `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:44` `tools/trace_walk.py` (no `SPEC_GUIDE.md` exists in tree).

### D5. Test-harness truths (counts point-in-time — re-derive via §Suggested order before quoting)

`ARTIFACTS` (`tests/conformance/_spec.py:19`) lists 8 layers while `ACCEPTANCE.md:271` promises 10 (`chg, eval`); `tests/scripts/test-layer.sh:7` lists 8; conformance suite is ~365 tests, not 77 (`tests/CONTRIBUTING.md:55`) or 16 modules; CI is Python 3.12, no submodules (`TROUBLESHOOTING.md:47-48`). Missing coverage to add or claims to downgrade: CHG/EVAL goldens + `test_layer_chg/eval.py`, bugfix-subtype golden (`parent_iplan`/`source_chg`, rollback PENDING→DONE/SKIPPED), Type-R `change_source: reconciliation` case, EVAL `required_environment/test_data_setup/coverage_tracking/test_results` pins, `tests/acceptance/deterministic/test_layer_tdd.py:10` VALID_TYPES vs template `test_types` keys, IPLAN broken-fixture manifest-contract note, `expected_warnings/` layers-01-05 implicit-empty asymmetry (document it).

### D6. Duplicated-test ownership

Forward coverage ×3, ref-granularity ×3, required-sections ×2 (`_harness.template_sections()` vs `test_required_section_sets.py` EXPECTED incl IPLAN-subtype mismatch), CHG enforcement ×3 (add codes-vs-catalog agreement test mirroring `test_iplan_bugfix_lifecycle.py:103-116`), `test_doc_validator.py` own `run_lint` copy → delegate to `_harness`, ACC01 synthetic vs golden cross-link, `test-auto-remediate-helpers.sh` tests a deleted script's inline copy → delete or re-anchor, `test-fullpath.sh --live` + `tests/acceptance/README.md:22` crash on missing `live/` dir → remove flag or restore harness. Plus ~20 `sys.path.insert(REPO_ROOT/"tools")` / `.exists()` fossils across `tests/conformance/` + `tests/unit/` (e.g. `test_acceptance_pairing.py:17`, `test_diagram_allowlist_source.py:26`, `test_forward_coverage_is_exercised.py:29`, `test_carrier_parity.py:193`, `test_saga_reconcile_post_audit.py:32`; re-derive the full list with the D2 sweep command) — replace with repo-root/`sdd_doc_lint`.

## Suggested order

1. T1 (quarantine red unit modules — unblocks CI signal).
2. T2 (linter-vs-governance contradictions — stops false errors/negatives) + T3 (`*.sh` gate blind spot, unwired pre-commit gate, sync-script self-obsolescence).
3. P1 forks (EVAL-RPT name-vs-template contradiction first, then canon; CHG content first, then home; 10_EVAL/IPVERIFY; MVP; bugfix vehicle; triple-lock; §File Naming rewrite incl. bugfix row).
4. D2 dead-path sweep + D1 versions + D3 branches (mechanical, scriptable; snapshots reworded, not swept).
5. D5 missing fixtures/pins + D6 dedup (lock in the fixed shapes).
6. Re-run: `python -m unittest discover -s tests/unit`, `-s tests/conformance`, `-s sdd_doc_lint/tests`, `-s tests/acceptance/deterministic`; `bash hooks/sync-version-refs.sh` (after regex fix); `rg` dead-path sweep clean.

## Step sequence (executable — replaces §Suggested order as the normative order)

> One task, one worktree: feature work runs in a per-task `git worktree` + branch (`feature/<issue-or-chg>-<slug>`, branched from `origin/dev`), never in the main checkout; main checkout stays on `dev` (`WORKTREE_FLOW.md` §3.2, §3.7 order guard: `worktree remove` BEFORE branch delete). Land via PR `feature/*` → `dev`; never push to `main`. Before any code step: authoring CHG (C1 allowed for post-completion repair scope) + IPLAN `In Progress` referencing it (§3.13); run `python3 sdd_doc_lint/chg_lint.py <chg-file.yaml>` pre-commit / pre-implementation / pre-merge. Interpreter is `python3` (`python` is absent in this container).

1. **File issues (gate).** Search (`gh issue list --search … --state all`), file one issue per defect class with verbatim analysis + `file:line` reproduction + run blast radius, `gh issue create --body-file -` (never `--body -`), read back body length. Done when: issue numbers exist for T1/T2/T3/P1-items/P2-sweep. Upstream-owned defects go to the owning repo, not here.
2. **T1 — quarantine red `tests/unit` (unblocks CI signal).** Per-table-row: skip/stub first (quarantine), delete or re-anchor second (remedy policy). Re-derive the fail list at kickoff (`python3 -m unittest discover -s tests/unit`). Done when: suite is green-or-skipped with every skip citing its issue; no deleted module without a quarantine commit preceding it.
3. **T2 + T3 — linter contradictions + hook gates.** T2: early-pass `Proposed` C3 drafts (GOV-012), delete L001 C3-duplicate, missing-`phase` error + drop keyword heuristic, L004 scan `implementation.steps[]` (`phase: iplan_creation`) with correct authorising rule cited before any warning→error escalation (GOV-013 does NOT cover this), fold-or-delete L005, dedup helpers only after verifying the `_common.py` candidate, add L001–L005 + CHG-04/CHG-05 fixtures. T3: `*.sh` watch, commit-message read-or-delete, pre-commit wiring-or-documented-split, docs-list resync, `sync-version-refs.sh` regex sweep + conformance test (snapshots in `README.md:303-308` / `docs/TAGGING.md:108-136` reworded, not swept), `pre_push_check.sh` + `.pre-commit-config.yaml:155` path fixes, `sdd-doc-review.sh` repoint + prune. Done when: `chg_lint` fixtures cover L001–L005 and the hook gates fire on the fixed tree per their warn/error contracts.
4. **P1 forks — content first, then canon (one decision record each in `framework/governance/DECISIONS.md`).** Order inside the step: (a) EVAL-RPT name-vs-template contradiction, then canon (REPORT recommended) + `test_results` pin + old-ID-form ban; (b) CHG §7 + enumeration content, then home (pointer/symlink left behind); (c) 10_EVAL (authoring) vs 10_IPVERIFY (execution/verification) + `validator.md` retarget before any tombstone (live readers: `08_IPLAN/README.md:164-177`, `framework/CHANGELOG.md`, `test_iplan_bugfix_lifecycle.py`) + `framework/README.md:81-84` fix; (d) MVP delete-or-tombstone + "one template per layer" claim fix; (e) bugfix-vehicle retarget (quarantine first) + Temporary-IPLAN row removal + VERIFY subtype comment; (f) triple-lock EVAL/CHG rows in one pass; (g) §File Naming rewrite + bugfix row + PRD/EARS/ADR adopt-or-not ruling. Done when: each fork has exactly one canon path and the other is a pointer/tombstone/deletion; conformance pins the fixed shapes.
5. **P2 sweeps — D2 dead paths + D1 versions + D3 branches (mechanical, scriptable).** Snapshots reworded, not swept; `tests/ACCEPTANCE.md` moved to `plans/` history or rewritten as methodology (record preserved); counts re-derived before quoting. Done when: D2 `rg` sweep is clean except explicitly grandfathered historical mentions; version/branch claims match 0.56.0 and `feat/* → dev → main`.
6. **D5 fixtures + D6 dedup (lock in the fixed shapes).** Add-or-downgrade per item; `_harness` delegation; codes-vs-catalog agreement test; `tools/` fossils → repo-root/`sdd_doc_lint`. Done when: new pins cover CHG/EVAL goldens, bugfix-subtype golden, Type-R reconciliation case, and EVAL required-keys.
7. **Verify + land.** Re-run (see §Verification); stage this plan file in the same branch (`plans/` is untracked: `?? plans/STALE-REVIEW-REPORT.md`); PR `feature/*` → `dev` with `Closes #N` (one keyword per reference); record canon decisions in `framework/governance/DECISIONS.md` + repo-process choices in `plans/DECISIONS.md`.

## Verification (re-derive counts at run time — never quote the point-in-time figures)

- `python3 -m unittest discover -s tests/unit` — green-or-skipped (baseline 2026-09-22: 83 tests, 24F + 9E + 15S).
- `python3 -m unittest discover -s tests/conformance` — green (baseline: ~365 tests; re-derive).
- `python3 -m unittest discover -s sdd_doc_lint/tests` — green (incl. new L001–L005 + CHG-04/CHG-05 + catalog-agreement cases).
- `python3 -m unittest discover -s tests/acceptance/deterministic` — green.
- `bash hooks/sync-version-refs.sh` (after regex fix) — pins current version; no silent no-ops.
- D2 `rg` sweep (see §D2 command) — clean except grandfathered history.
- `git ls-files | grep -E "^(tests/smoke|tests/review|tests/packaging|tests/release)/"` — re-derive; any deletion accounted for.
- `pre-commit run --all-files` — clean (or documented split if the CHG gate stays Claude-path-only).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Quarantine (skip) becomes permanent — red stays hidden | Every skip cites its issue; Step 7 requires zero unexplained skips |
| R2 | Weakening a conformance check to go green | Each test change cites the deleted path it tracked; conformance stays a contract on `framework/`, never loosened for convenience |
| R3 | Canon decision made without content settlement (CHG home before §7; EVAL name before template) | Content-first order enforced in Step 4a/4b; decision recorded before sync |
| R4 | Tombstone/delete destroys the audit trail | Quarantine-first policy (T1 table, items 3/5, D2); `tests/ACCEPTANCE.md` preserved as history/methodology |
| R5 | Point-in-time counts (365 tests, ~20 fossils, 24F+9E) quoted as live | Re-derive at kickoff and at verify; plan states baselines with dates |
| R6 | `plans/` untracked — work lost in ephemeral container | `git add` the plan in the feature branch; only committed + pushed work survives |

## Review log

### Pass 1 — readiness pass 2026-09-22 (this edit)

- Added plan header (Task/Type/Status/Depends/Feeds/Version), Objective, Scope, issue-triage gate (0 open — filing required pre-implementation), reading guide, re-verified ground truth (`0.56.0`, `dev`→`origin/dev`, T1 24F+9E+15S over 83 tests via `python3`, EVAL + CHG forks still live).
- Promoted §Suggested order to normative §Step sequence with worktree/branch/CHG/IPLAN gates, per-step done-criteria, and `python3` interpreter fix; added §Verification + §Risks (R1–R6).
- No finding text altered — audit trail preserved verbatim. Still required before implementation: file the §GitHub-issues rows, then run review pass 2 (AGENTS.md: plans get two review cycles before the plan PR opens). Suggested pass-2 checks: issue numbers filled in, Step 4 canon recommendations confirmed or overturned with reasons, version impact (PATCH/MINOR/none) settled.

### Pass 2 — canon + version review 2026-09-22 (issues #662–#672 filed; live re-checks via `grep`, bodies read back non-zero)

Step 4 canon recommendations ruled with reasons (CONFIRM = stands, OVERTURN/REFINE = changed):

- (a) EVAL canon: **CONFIRM REPORT.** 6 files cite `EVAL-REPORT-TEMPLATE` as base (index, `10_EVAL/README`, `evaluator.md:162`, `report_generator.md:120` ×2 refs); only output *names* say EVAL-RPT (`evaluator.md:3,14,33`, `report_generator.md:3,13,32`, `10_IPVERIFY/README.md:38`). REPORT carries the newer ID grammar + §4 `test_results`; RPT carries the stale ID form. Canon REPORT minimizes churn (output declarations + one template file change) and the `EVAL-{NN}-RPT-{NNN}.yaml` filename shorthand survives as the report *filename* carve-out (see P1-7). → #664.
- (b) CHG home + content: **CONFIRM home (`governance/chg/`), RULE content: KEEP the §7 `validation:` block.** Dropping 36 lines of normative validation text would weaken the template contract (violates R2 — never loosen to go green); keeping it is additive. Adopt the 8-layer enumeration (matches `DOC_GOVERNANCE_CORE.md` §3.1.1). Then sync + pointer/symlink. → #667.
- (c) 10_EVAL vs 10_IPVERIFY: **CONFIRM split (authoring vs execution/verification), reject merge.** Merge would churn both READMEs + all playbook frontmatter + the index; the split matches the existing file layout. `validator.md` retargets to the EVAL-RPT flow first; tombstone only after live readers retargeted. → #672.
- (d) MVP: **REFINE — tombstone-with-pointer, NOT delete; retarget 7 index links.** Pass-2 `grep` overturns "no live readers": 7 layer index templates (01–07) carry live `MVP skeleton` links (`BRD-00_index.TEMPLATE.md:83`, `PRD:116`, `EARS:105`, `BDD:52,153`, `ADR:102`, `SPEC:40`, `TDD:54`) plus a `framework/governance/DECISIONS.md:312` mention. (The "READMEs never mention MVP" half stands — README hits are the MVP *lifecycle concept*, e.g. `01_BRD/README.md:79`, not file links.) Silent deletion breaks 7 index templates. Fix: tombstone the 8 files with pointers to the normative templates + retarget the 7 skeleton links + fix the "one template per layer" claim. Filed as #666; the finding text above is preserved verbatim and this log entry is the correction.
- (e) Bugfix vehicle: **CONFIRM** (canon already landed via CHG-05, 0.56.0). Retarget-or-deprecate scripts, quarantine first; Temporary-IPLAN row removal with pointer; VERIFY subtype comment gains `bugfix`. → #662.
- (f) Triple-lock: **CONFIRM one-pass fill** of all EVAL/CHG rows (schema enum, naming prefixes/lifecycles/index rows + IPLAN scope, governance scope, traceability chain/table/prose, ACC01 `acceptance_layers` rows). → #671.
- (g) §File Naming: **CONFIRM with scope ruling — minimal rewrite, NO new PRD/EARS/ADR filename rules.** General `{TYPE}-NN_{slug}.yaml` form + EVAL/RPT/CHG carve-outs + bugfix row ships; minting normative `PRD/EARS/ADR-NN_{slug}` filename forms would create new contract (those templates carry only generic slug-allocation bullets) — out of scope for a cleanup. → #669.

Version impact settled (precedent: CHG-05 additive template fields + prose + lint = MINOR; CLEANUP-001 pure-cleanup steps = none): Steps 2–3 (T1 quarantine, T2 missing-phase error as stricter enforcement of existing contract, T3 hooks) → **none**; Step 4 (P1: template canonization incl. tombstoning dead duplicates with contract preserved via canon, governance prose, schema rows) → **MINOR `0.56.0 → 0.57.0`**; Steps 5–6 (P2 doc sweeps, D5/D6 fixtures) → **none**. Single MINOR covers the P1 batch; fanout via `hooks/sync-version-refs.sh` after its Step-3 regex fix.

Line-ref spot-checks re-verified live at pass 2 (`ls`/`grep`/`sed` outputs above); `rg` is absent in this container — use `grep -rn` (D2 sweep command to be translated at kickoff).

Plan PR may now open (`feature/*` → `dev`, carrying `Closes #662–#672` as one keyword per reference). Implementation afterward still requires the authoring CHG (C1 allowed) + IPLAN `In Progress` per §Step sequence.

## Corrections log (independent review, same session)

1. T3 CHG-template "false positive" → advisory hygiene (hook guards `In-Progress|Approved`, template is `Draft`/`Proposed`; gate is warn-only).
2. "No test covers EVAL" → EVAL *template-shape* pins uncovered (layer wiring exists).
3. Playbooks "point at REPORT" → playbooks internally split (RPT outputs, REPORT base template).
4. "Extend sync script to README/TAGGING" → reword snapshots (explicitly excluded from sync by design).
5. "Declare `governance/chg/` canonical" → decide §7 + enumeration content first, then home.
6. CHG-L004 "per GOV-013" → authority removed (GOV-013 is the IPLAN Gate); needs correct rule before escalating.
7. `:83` 0.53.3 comment → historical note, not a defect.
8. `test_chg_lint` "L006–L012" → ≈L006–L011 + attestation.
9. chg/bugfix dedup → file:line evidence added (`chg_lint.py:55,394-395,651,659,688` vs `bugfix_lint.py:37,58,66,307,348`; `_ELEM_ID` `:287`, `ELEM_FORM` `trace_graph.py:43`).
10. Point-in-time counts flagged re-derive; D6 fossil pointer concretized.
11. Remedy policy: quarantine/skip first, delete second (T1 table, items 3/5, D2).
12. Post-review addition: P1 item 7 (§File Naming slug-row staleness + missing bugfix row + VERIFY subtype comment), wired into suggested order step 3.
13. Build-session review round (2026-09-22): ACC01 premise corrected (`LINT_RULES.md:93` cites `SEED_CONTRACT.md` alongside, not instead of, registry); item 7 fix reframed as adopt-or-not decision (PRD/EARS/ADR carry only generic slug bullets); `SPEC_GUIDE.md` host replaced with live `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md:44`; `framework/` prefixes added (D4, PLAN_STANDARD, `test_layer_tdd.py` path); line refs fixed (T1 `:10`/`:12-13`, L005 `:202-247`, pairing `:166-184`, AGENTS `105-122` after worktree-pointer insertions); `tests/unit/README.md:5` vs `CLAUDE.md:775` contradiction added; GOVERNANCE/CLAUDE dual-cites hedged; v7 pin check flagged online-only. Dropped as non-gaps after live re-check: `chg_lint.py:317,594`, `IPLAN-TEMPLATE.yaml:87,103`, `CLAUDE.md:21` "8-layer", `CLAUDE.md:510-512`, LEARNED_LESSONS range, `framework/README.md:81-84`.
