# FRAMEWORK-0.54.0 Plan — donor-hardening addons (b-local-privy → framework) + MINOR bump

| Field | Value |
|-------|-------|
| Task | FRAMEWORK-0.54.0-DONOR-ADDONS |
| Type | feature (governance hardening, engine-agnostic) |
| Status | FINAL — 2026-09-20T00:00:00Z (two self-review cycles + OPS-0065 3-agent review folded; Pass 3 clean) |
| Base | `feat/clean-up` @ `d3503df4` (post CLEANUP-001, conformance 354 OK skipped=1) |
| Depends on | CLEANUP-001 merged; `framework/VERSION` = `0.53.3` |
| Feeds | `0.54.0` release; donor `.aidoc/framework` refresh (`e30ad21` → new tag) |
| Version impact | **MINOR `0.53.3 → 0.54.0`** — new governance rules + template fields + one new doc; no instance-format break (GD-17 untouched); change-level **C2** per GATE-SPEC |

## Objective

Port the operational hardening learned in `b-local-privy` `.aidoc/project/governance/` (8 files, 1851 lines incl. `.aidoc/README.md` + `profile.yaml` — fully read 2026-09-20, cache in `/tmp/bprivy-gov/`) into the engine-agnostic spec. Donor `dev` has since moved (cites up to 2026-11-06); the `/tmp` snapshot is the frozen source — do NOT chase donor HEAD during implementation. The framework already owns the concepts (DECISION_WORKFLOW, MODULE_LAYOUT, SELF_LEARNING, NOTICES incl. Rule 6 TDD↔IPLAN, §3.4/A1-E27, §3.13); the donor delta is **checklists, gates, concurrency traps, and verification commands** that prevent measured rework (CHG-04 16 gaps, SPEC-09 18 fake IDs, CHG-10/CHG-32 clobbers). This plan implements every migratable addon, excludes project-only material, and ships the MINOR bump with mechanical fanout.

Donor sources (dev branch, `.aidoc/`):

- `.aidoc/README.md` v3.0 + `profile.yaml` (10 active_layers, team, 3 iters) — override-layer contract, already GD-28; no change.
- `project/governance/GOVERNANCE_RULES.md` 538 lines (§1–§8)
- `project/governance/DECISION_WORKFLOW.md` 128 lines
- `project/governance/MODULE_LAYOUT.md` 147 lines
- `project/governance/WORKTREE_FLOW.md` 117 lines
- `project/governance/SELF_LEARNING.md` 272 lines
- `project/governance/notices.md` 526 lines (top-level §§1–5 + 8–12: Issue Registry §1, Prevention Rules §2 with Rules 1–5, Verification Checklist §3, `audit_fix` subtype §4, CHG-04 16-gap RCA §5, IPLAN violations §8, dead-CI-gates §11, CHG-32 incidents §12; plus project-only §§9–10 P0-Card/wire which stay OUT)

## Scope

**In (17 migratable addons, ranked by rework-prevented):**

| # | Donor rule | Target framework path(s) | Change class |
|---|-----------|--------------------------|--------------|
| 1 | §3.1.1 What-Goes-Where table (CHG/IPLAN/SDD) + 4 violations | `framework/governance/DOC_GOVERNANCE_CORE.md` §3.1.1 (append table, genericize `docs/sdd/` → `<project>/sdd/`) | prose, PATCH-leg of MINOR |
| 2 | §3.13 bootstrap exemption (#383: CHG→SDD→IPLAN authoring order is the exempt path) | `DOC_GOVERNANCE_CORE.md` §3.13 + `framework/AI_ASSISTANT_RULES.md` gate restatement | prose |
| 3 | §3.2 SDD-sync on IPLAN `Completed` (SPEC/TDD version check ships in same change) | `DOC_GOVERNANCE_CORE.md` IPLAN lifecycle + `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` (`completion_spec_sync:`) + `sdd_doc_lint/chg_lint.py` new CHG-L012 (warning) + `LINT_RULES.md` catalog entry (CHG-L012 lands in BOTH — code and catalog ship together per Step 4; the "or" in the draft was an error) | template + lint |
| 4 | §3.5 DONE-must-exist + §3.9 status gates (incl. notices §8 two failure modes: Draft≠authorized, Approved≠implementing) + §3.10 realtime manifest + §3.11 CHG-tracks-IPLAN bundle | `IPLAN-TEMPLATE.yaml` (`file_manifest` status enum note + `completion_gates:`) + `DOC_GOVERNANCE_CORE.md` IPLAN lifecycle | template + prose |
| 5 | §3.8 breaking-change docs (current sig / new sig / callers) | `IPLAN-TEMPLATE.yaml` (`breaking_change:` block per step) + `LINT_RULES.md` new `IPLAN01` advisory (severity advisory, NOT error — Decision C) | template + lint catalog |
| 6 | §2.7 new-layer registration checklist | `framework/registry/LAYER_REGISTRY.yaml` header comment + `framework/registry/README.md` + `LINT_RULES.md` (new `REG01` advisory) + `tests/conformance/test_registry.py` assertion (registry test exists; `test_layer_registry_necessary_upstream.py` is the sibling precedent) | registry + test |
| 7 | §4.1 upstream status propagation (downstream start ⇒ upstream Approved; ADR uses Accepted) | `DOC_GOVERNANCE_CORE.md` new §4.1 + `framework/governance/TRACEABILITY.md` cross-ref APPENDED OUTSIDE the digest-pinned `Reference Granularity Principle` bullet (`65cb30a4…` — anchor file:lines verified before edit; never edit the anchor) | prose |
| 8 | §6.1/6.2 delegation integrity (pass real IDs; post-delegation grep validation) | `framework/governance/NOTICES.md` Rule 1–2 harden (add `@prd/@brd/@adr` greps + `sort\|uniq -d`) + `framework/AI_ASSISTANT_RULES.md` one-line pointer | prose |
| 9 | §6.3 ID red-flags (`00/01` sections never exist) + §6.4 manual ID tracking + §6.6 archive-before-reuse | `NOTICES.md` + `framework/governance/ID_NAMING_STANDARDS.md` red-flag box — prose box APPENDED OUTSIDE the digest-pinned lines (`:517–520` + `:1253–1271`); NO re-pin/re-hash of element IDs in this release | prose |
| 10 | §6.5 EARS pattern decision tree (WHILE/WHEN/IF/WHERE/THE-SHALL) | `framework/layers/03_EARS/README.md` (append tree; pattern table already at :49) + `framework/playbooks/03_EARS/requirements_specialist.md` (lens note, NOT new `author.md` — no such file; role files are chaos_engineer/qa_lead/requirements_specialist/security_engineer/tech_lead) | prose/playbook |
| 11 | §6.10 TDD↔IPLAN Rules A–E (status propagation, ownership, fn names, language, index sync) | `LINT_RULES.md` CREATE new `TDD-SYNC` entries covering Rules A–E as advisory (NOT "extend TDD-SYNC-001–004" — no `TDD-SYNC` string exists in LINT_RULES today, verified 2026-09-20; Rules A–E live only in donor notices + framework NOTICES Rule 6) + `framework/layers/07_TDD/` + `08_IPLAN/` index templates note | lint + templates |
| 12 | §3.6/3.6a/3.6b/3.6c concurrency traps (verify-3, no whole-tree git, force-add archives, layer-detection) | `NOTICES.md` new traps + `AI_ASSISTANT_RULES.md` + `.gitignore` scoped negation for governed archives only (exact pattern TBD in impl, e.g. `!examples/*/docs/**` or named paths — never a broad `!archive/**`) + `sdd_doc_lint/__main__.py` SKIPPED-vs-clean warning | prose + tool + gitignore |
| 13 | WORKTREE_FLOW (invariants → cleanup + verify commands, engine-generic half) | **NEW** `framework/governance/WORKTREE_FLOW.md` v1.0 (generic git/gh halves only; Go/npm/ports stay donor-local) + `DOC_GOVERNANCE_CORE.md` pointer | new doc |
| 14 | SELF_LEARNING hardening (§6.9/§7.4 feedback-submit contract, §8 checklist — 13 boxes at `:184–196`, additive-only + cite-source, 3KB cap) | `framework/governance/SELF_LEARNING.md` + `framework/governance/FRAMEWORK_FEEDBACK_LOG.md` cross-ref (full path — never a bare filename) | prose |
| 15 | notices donor-only deltas: §4 `audit_fix` table (feeds #16), §5 CHG-04 RCA → GOVERNANCE already has §3.4 (verify no gap), index-drift + coverage-count Issues 5–6 (already upstreamed — fold remaining grep one-liners) | `NOTICES.md` prevention rules (idempotent append, no duplicate sections) | prose |
| 16 | `audit_fix` vs `code_build` IPLAN subtype (donor: `combined` REMOVED, `deploy` merged into planned `devops`; framework today: `code_build \| deploy \| combined`, default `combined` — Decision F resolves) | `IPLAN-TEMPLATE.yaml` `_required_when_subtype:` + `framework/layers/08_IPLAN/README.md` | template |
| 17 | §3.7 SQL-vs-schema + §6.7-RCA pointer (genericize: verify queries against declared schema artifact) | `IPLAN-TEMPLATE.yaml` guidance + `NOTICES.md` pointer (no Atlas/HCL names in spec) | guidance only |

**Out (PROJECT-ONLY, never migrates):**

- §1 infra (Debian/Atlas/Nginx, `ADMIN_BIND`, SSL blocks), §8 wire invariants (RPC envelope, KYC schema, Privy headers) — stack-specific.
- Verify commands (`go vet/test`, `npm run verify:product`, `secret_scan.py`, boundary checks), LAN IPs, Docker `-p`/ports, `docs/sdd/` literal paths, CHG/PLAN next-IDs (§2.1), CI same-repo reusables/gate-doctor, P0-Card product gate (§3.12), `schema.hcl`/`Atlas` names, `.mimocode/`/`MEMORY.md` tool paths.

## Approach / Design

- **Decision A — genericize, don't vendor.** Every donor snippet citing `docs/sdd/`, Go structs, Atlas, Privy, or `.mimocode/` is rewritten to `<project>/…` / "declared schema artifact" / "learning store" before landing. Engine-token hygiene (`test_spec_hygiene.py`) stays green.
- **Decision B — one bundle, one MINOR.** 17 addons ship as a single `0.54.0` (not 17 patches): all are additive governance/template guidance; none changes instance `extensions`, `realizing_layers`, or digest-pinned prose (TRACEABILITY COV02 bullet stays deferred per digest-regen decision).
- **Decision C — lint where it prevents rework, prose elsewhere.** New checks are advisory/warning ONLY — no new hard errors that could red-line existing corpus: CHG-L012 (completion sync, warning), REG01 (registration checklist, advisory), TDD-SYNC A–E (advisory, NOT error). Everything else is auditor-lens prose.
- **Decision D — governance gate first.** Framework `**` change ⇒ CHG + IPLAN per AGENTS.md/CLAUDE.md before code. Plan PR → two review cycles → impl PR `feat/0.54.0-donor-addons` → `dev`.
- **Decision E — TRACEABILITY digest untouched.** `test_ref_granularity_parity.py` pins stay; no COV02 prose edit in this release.
- **Decision F — `combined` stays, `audit_fix` adds.** The donor removed `combined` ("too broad") and merged `deploy` into a planned `devops`, but the framework's `combined` is the backward-compat default (pre-0.19.1 IPLANs) wired through 11 `_required_when_subtype` markers — removing it is a breaking instance-format change, out of scope for a hardening MINOR. #16 therefore ADDS `audit_fix` alongside the existing three (`code_build | deploy | combined | audit_fix`) and documents the donor's `devops` direction as a future consideration, not a rename.

## Step sequence

0. **Govern** — CHG (authorize 0.54.0 scope above) + IPLAN (`In Progress`, file_manifest = all target paths) + `python sdd_doc_lint/chg_lint.py <chg-file.yaml>` green (bare `python -m sdd_doc_lint.chg_lint` with no operand exits 2 — always pass the CHG file).
1. **DOC_GOVERNANCE_CORE** — FIRST dedup the twin EVAL blocks (`:259–318` vs `:319–378`; second block carries stale dash-ID formats `EVAL-01.BDD-01.TC-01.3`) as a prerequisite, THEN land #1, #2, #4-lifecycle-half, #7 (§3.1.1 table, §3.13 exemption, IPLAN lifecycle, §4.1).
2. **IPLAN template** — land #3-field, #4-enum, #5-block, #16-subtype (`audit_fix` ADDS as fourth subtype; verify no golden churn — see Verification), #17-guidance in `IPLAN-TEMPLATE.yaml` + `08_IPLAN/README.md`.
3. **Registry** — land #6 (`LAYER_REGISTRY.yaml` comment + `registry/README.md`).
4. **Lint + tooling** — land CHG-L012, REG01, TDD-SYNC A–E (all advisory/warning per Decision C) in `chg_lint.py` + `LINT_RULES.md` (code and catalog ship together); SKIPPED-vs-clean warning in `sdd_doc_lint/__main__.py`; `.gitignore` scoped archive negation (#12-half) + verify with `git check-ignore -v <governed-path>` and `git status --porcelain`.
5. **EARS + indexes** — land #10 (EARS README + `requirements_specialist.md` lens note) + #11 index-template notes.
6. **NOTICES / SELF_LEARNING / rules pointer** — land #8, #9, #12-prose-half, #14, #15.
7. **New doc** — create #13 `framework/governance/WORKTREE_FLOW.md` v1.0 (Document Control table, framework 0.54.0; git/gh ordering: worktree-remove runs BEFORE branch-delete — donor WORKTREE_FLOW order-guard) + pointer from `DOC_GOVERNANCE_CORE.md`.
8. **Version fanout** — `framework/VERSION` → `0.54.0`; `hooks/sync-version-refs.sh` (NOT `scripts/` — no such file; note: the sweep rewrites only stale `0.53.0` literals, so verify `LAYER_REGISTRY.yaml` `framework_version` explicitly); new GD entry (GD-29) in `framework/governance/DECISIONS.md`; `CHANGELOG.md` `## [0.54.0]` entry; `framework/registry/LAYER_REGISTRY.yaml` `framework_version`.
9. **Land** — branch `feat/0.54.0-donor-addons` → PR → `dev`; commit carries `Multi-agent self-review per OPS-0065 (<agents>): <verdict>` (literal, `call / verify` greps it).

## Verification

- `python -m unittest discover -s tests/conformance` — green (baseline 354 OK skipped=1; new REG01/TDD-SYNC assertions included, no weakened guards per R4).
- `python -m unittest discover -s sdd_doc_lint/tests` — green (CHG-L012 fixtures pass).
- `python -m unittest discover -s tests/acceptance/deterministic` — green; IPLAN subtype addition (`audit_fix`) and new template sections MUST be checked against `tests/acceptance/_harness.py:230–288` section-validity + `fullpath/iplan` goldens — if any golden churns, update goldens explicitly in the impl PR (no silent regeneration).
- `grep -riE 'hermes|mcp|plugin|\.claude/|Atlas|Privy|mimocode|192\.168\.' framework/` on every touched file — empty, case-insensitive per `test_spec_hygiene.py:20–31` (widen beyond the three new/edited governance docs; `\.claude/` and ci-hermes-style tokens included).
- `git tag -l 'framework/*' | sort -V | tail -3` + cross-check against `framework/VERSION` at impl time (do NOT trust a stale high-water); new `framework/v0.54.0` tag cut separately per `docs/TAGGING.md` (not in this PR).

## Review log

- Pass 1 (self, 2026-09-20): verified every target path + donor citation against the tree. 7 gaps found and folded: (1) #10 target `playbooks/03_EARS/author.md` does not exist — retargeted to `requirements_specialist.md` lens note (role files: chaos_engineer/qa_lead/requirements_specialist/security_engineer/tech_lead + README:36); (2) #6 test file glob `test_*registry*.py` made concrete — `test_registry.py` exists, `test_layer_registry_necessary_upstream.py` is the sibling precedent; (3) #11 "extend TDD-SYNC-001–004" overstated — no `TDD-SYNC` string in LINT_RULES today, Rules A–E live only in donor notices + framework NOTICES Rule 6, so the step CREATES them; (4) #16 vs donor `combined`-removal conflict unacknowledged — added Decision F (`combined` stays as backward-compat default with 11 `_required_when_subtype` markers; `audit_fix` adds as fourth subtype; donor `devops` direction documented as future); (5) Step 8 sync-script path wrong (`scripts/sync-version-refs.sh` does not exist — corrected to `hooks/sync-version-refs.sh`); (6) donor line count "6 files, 1728 lines" miscounted the surface actually read (8 files incl. `.aidoc/README.md` + `profile.yaml` = 1851 lines — corrected in Objective); (7) duplicate EVAL block in DOC_GOVERNANCE_CORE (:259–318 vs :319–378, second block carries stale dash-ID formats `EVAL-01.BDD-01.TC-01.3`) — Step 1 now dedups as a prerequisite to landing #1/#2/#4/#7. Also confirmed: DOC_GOVERNANCE_CORE has NO §3.1.1/§3.2/§3.5–§3.11/§4.1 headings (only 3.4.1/3.3/3.13/3.14 refs — gaps genuine); IPLAN subtypes today `code_build | deploy | combined` default `combined`; SELF_LEARNING already at Framework Version 0.53.3 (no version correction needed); `.gitignore` carries only `tests/results/archive/` (governed-archive negation for #12 confirmed missing).
- Pass 2 (re-review, 2026-09-20): re-read the patched plan + re-validated new claims. 4 gaps found and folded: (1) donor-sources line said "RCA Issues 1–6, Rules 1–6" but the frozen snapshot's notices.md carries §§1–7 + 10–12 (incl. CHG-32 §12 concurrency RCA, §4 `audit_fix` table, §5 CHG-04 RCA, §8 IPLAN violations) — retitled accurately, project-only §§8–9 confirmed OUT; (2) #15 "RCA Issues 5–6" was ambiguous (framework NOTICES Issues 5–6 = TDD↔IPLAN/index-drift/coverage-count, already upstreamed; donor §§5/8/12 each feed a different numbered addon) — rewrote #15 to name the donor→framework routing explicitly; (3) #4 cited "§3.9 status gates" without the donor's sharpest content (notices §8 two failure modes: Draft≠authorized, Approved≠implementing) — folded into #4; (4) #3 said "CHG-L012 … or TDD-SYNC extension" (either/orUnspecified) — resolved to BOTH (code + catalog ship together per Step 4). Incidental confirmations: framework NOTICES already has Rule 6 (TDD↔IPLAN) + Issues 5–6 deltas; donor SELF §8 "12-item" checklist is actually 13 boxes (:184–196); hygiene gate is `tests/conformance/test_spec_hygiene.py`.
- Pass 3 (re-review post-OPS-0065-fold, 2026-09-20): re-read the fully folded plan. All 4 docs-reviewer majors folded (Objective 8-file/1851 + Rule 6; #11 CREATE wording; Decision C all-advisory; Step 0 `<chg-file.yaml>` operand; Step 1 EVAL-dedup prerequisite) and all 8 silent-hunter findings folded (F1 operand, F2 fanout no-op note, F3/F4 anchor guards on #7/#9, F5 BOTH, F6 scoped-negation + check-ignore verification, F7 golden-churn caveat, F8 `\.claude/` + `-i` + VERSION cross-check). 1 new micro-gap found and folded: hygiene grep claimed case-insensitivity but the command lacked `-i` — added. Step 2 now cross-refs the golden caveat; Step 7 carries the WORKTREE order-guard; #12 carries scoped-negation; #14 carries 13-box count + full feedback-log path. No further gaps — plan is FINAL, ready for plan PR.
