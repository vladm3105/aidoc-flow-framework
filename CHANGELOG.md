# Changelog

All notable changes to the AI Doc Flow Framework are documented here. Format
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> Scope (#687): this log records project releases and mirrors each framework
> spec release cut in `framework/CHANGELOG.md` (same version, same date).
> Spec-level detail lives in `framework/CHANGELOG.md`; this file carries the
> project-level entry.

## [0.67.1] — 2026-09-30

> The two entries after the batch entry were relocated from below `0.62.4`
> (CHG-24 #806) — content unchanged, Keep-a-Changelog order restored.

### Fixed — triage batch #798–#808 (C1 PATCH → 0.67.1, CHG-24 + IPLAN-24)

- Docs-truthfulness (#801, #802, #804, #806, #808): `F2-UNIFY-PLAN.md` marked achieved via CHG-12 (#772/#773 closed); `PROJECT.md` branching + symlink sections annotated as superseded by `AGENTS.md` and the binding symlink convention; frozen-era pins qualified; `SELF_LEARNING.md` store table rewritten to the implemented surface; `README.md` status snapshot refreshed to 0.67.0
- Template consistency (#805): EVAL schema normalized to 1.0, future date replaced, CHG `framework_version` literal replaced with `[X.Y.Z]` (both mirror twins)
- Skills registry + engine-neutrality (#807): phantom `DESIGN.md`/`PLAN.md` entries dropped, `AGENTS.md`-chain wording ported from the `.agents` copies
- CI gate coverage (#798, #799, #803): pre-push CHG gate invoked in CI, `tests/unit` wired into CI, three scanner `fail-on-findings` flipped after a clean window (0 open alerts)

### Fixed — required CI checks vendored locally: canon went private (#746)

- `.github/workflows/pre-commit.yml` + `links.yml` run vendored inline jobs (copied from canon `@ci/v4.0.0`, source tag + date in header comments) — the `uses: ...aidoc-flow-ci...` calls load-fail while canon is private, leaving both required contexts permanently Expected. No framework version change (CI-only, no `framework/` files touched)

### Fixed — P0 CI batch: ai-review v4 caller contract + pin-currency reader (#705, #710)

- `ai-review.yml` caller migrated to the canon `ci/v4.0.0` contract (CI-0051): input renamed to `llm_allow_insecure_http`, `secrets:` remapped to `LLM_URL` / `LLM_API_KEY`. The stale map named undeclared inputs/secrets, so GitHub load-rejected the workflow (`startup_failure`, zero jobs). No framework version change (CI-only, no `framework/` files touched)
- Pin-currency reader restored: `hooks/read-pin-currency-log.sh` + `hooks/reconcile-pin-currency-issue.sh` (were root `scripts/`, archived in `0af49fac`), `pin-currency-reader.yml` repointed, archived plan citation dropped; 18-test unit module restored and re-registered in the conformance suite

## [0.67.0] — 2026-09-30

### Removed — Tier-1 consumer feedback log retired (C2 MINOR → 0.67.0)

- Tracker-only capture: Tier-1 consumer-project log retired (no operator);
  `FRAMEWORK_FEEDBACK_LOG.md` v1.0 → v2.0, Principle 9 rewritten, scaffold
  template deleted (CHG-23 + IPLAN-23 in `framework/archive/CHG-23/`;
  GD-41 records both rulings)

### Changed — per-task worktree unconditional (C2, CHG-23)

- AGENTS.md quick-path exception removed: every feature/defect change runs
  in a per-task worktree + branch, post-merge cleanup removes the worktree
  BEFORE branch delete (WORKTREE_FLOW.md §3.7 order guard)

## [0.66.0] — 2026-09-29

### Added — self-learn two-tier architecture (C3 MINOR → 0.66.0)

- Tier model + vendor-neutral skill (#779 phase-b; CHG-18 + IPLAN-18 in
  `framework/archive/CHG-18/`); GD-40 records the keep-`learning/` decision
- `framework/VERSION` bumped from `0.65.2` to `0.66.0` with mechanical pin sweep

## [0.65.2] — 2026-09-29

### Fixed — self-learn loophole closure (C2 PATCH → 0.65.2)

- Solo-project direct-write exemption removed (#779 phase-a; CHG-17 + IPLAN-17
  in `framework/archive/CHG-17/`): all governance writes ride authorizing
  CHG + In-Progress IPLAN
- `framework/VERSION` bumped from `0.65.1` to `0.65.2` with mechanical pin sweep

## [0.65.1] — 2026-09-29

### Fixed — docs/deploy batch (C2 PATCH → 0.65.1)

- Approval, bootstrap, and upgrade gaps (#784/#785/#786/#787; CHG-16 + IPLAN-16
  in `framework/archive/CHG-16/`): judge-then-human C3 rule, aidoc `cp` fix,
  new `BOOTSTRAP.md` + `UPGRADE-RUNBOOK.md` runbooks
- `framework/VERSION` bumped from `0.65.0` to `0.65.1` with mechanical pin sweep

## [0.65.0] — 2026-09-29

### Added — per-flow Phase-3 closeout rule (C2 MINOR → 0.65.0)

- Closeout bifurcation (#776; CHG-14 + IPLAN-14 in `framework/archive/CHG-14/`):
  deployable changes close live (deploy + smoke + authentic EVAL), non-deployable
  changes close via static battery with no EVAL owed, mixed scope follows deployable
- §3.3 rules 10–11, flows verification-column pointers, GD-39, F2-cell stale repair
- `framework/VERSION` bumped from `0.64.0` to `0.65.0` with mechanical pin sweep

## [0.64.0] — 2026-09-29

### Added — first-class documentation_sync phase; CHG-L003 scoped to code steps (C2 MINOR → 0.64.0)

- Doc-sync vocabulary (#775; CHG-13 + IPLAN-13 in `framework/archive/CHG-13/`):
  new legal `documentation_sync` step phase for doc-only milestones; L003 message
  names the legal phases, L005 orders doc-sync in the execution zone, L004 still
  requires an IPLAN reference — no IPLAN exemption ships (CHG-12 holds)
- LINT_RULES L003/GOV-010 rows, core §3.4 items 13–14 + E25 + L003 row, both
  templates (`_allowed_phases` + canonical F2-C1 layout), both READMEs (Phase 2),
  GD-38; new `DocumentationSyncPhaseTests` unit pins; twins byte-identical
- `framework/VERSION` bumped from `0.63.0` to `0.64.0` with mechanical pin sweep

## [0.63.0] — 2026-09-28

### Changed — mandatory CHG+IPLAN for every post-seed activity (C2 MINOR → 0.63.0)

- Trackability rule (#772, #773; CHG-12 + IPLAN-12 in `framework/archive/CHG-12/`):
  every post-seed C1 requires a C1 CHG + scoped IPLAN for every author (agents and
  humans) — F2.2 docs-only direct commit, the AGENTS.md (i)/(ii) exceptions, router
  step 5, and both template C1 rows retired; sole exception is seed-phase drafting
  pre-first-BRD (`SEED_CONTRACT.md` R1)
- Supersedes the F2-UNIFY-PLAN D2 human-only exception (rejected candidate recorded
  in CHG-12); enforcement is reviewer-lens — the PR reviewer verifies every commit
  rides the authorizing CHG/IPLAN manifest — GOV-018 stays syntactic by design
- New `AlwaysTracedAgreement` conformance pins (unified C1/F2 wording, no live-path
  direct-commit refs); mirror twins stay byte-identical
- `framework/VERSION` bumped from `0.62.7` to `0.63.0` with mechanical pin sweep

## [0.62.7] — 2026-09-28

### Fixed — 09_CHG README twins byte-identical + dead link repaired (C2 PATCH → 0.62.7)

- Mirror twins (#770): one perspective-neutral `Canonical home` paragraph in both
  09_CHG READMEs; layer copy's dead flows link repaired location-independent;
  new `test_readme_copies_identical` guard pins the twins
- `framework/VERSION` bumped from `0.62.6` to `0.62.7` with mechanical pin sweep

## [0.62.6] — 2026-09-28

### Fixed — review-sweep batch: workflow chain, CHG status hardening, ID obligations, saga cleanup (C2 PATCH → 0.62.6)

- Docs-truthfulness batch (#759, #760, #762, #763, #764, #701): EVAL restored to the
  workflow chain in all layer READMEs; CHG de-labeled from L9 to the 09 overlay
  namespace; SPEC README gains Element-ID + Traceability sections and the normative
  TDD-Ready threshold pointer; ADR overview matches `required_tags`; §3.4 item 12
  cites live E25–E27; REVIEW_SAGA matches `saga.schema.json` with platform-era refs removed
- Governance hardening (#765, #766, #761): §3.3 rules 5–9 + §3.4.1 E28 with new
  lint rule CHG-L017 (5 new tests); rewrite purge obligation in §3.4 item 11; EVAL
  test-case IDs MUST (6 MUST + 2 MAY + EVAL MUST + CHG exempt)
- Agent conduct + gate hygiene (#767, #768): `--no-verify`/hook-bypass prohibition;
  required gates must prove they load
- `framework/VERSION` bumped from `0.62.5` to `0.62.6` with mechanical pin sweep

## [0.62.5] — 2026-09-27

### Fixed — CHG-L016 archive-snapshot existence + EVAL template parses (C2 PATCH → 0.62.5)

- New rule CHG-L016 (#757): cited `archive_path` must resolve on disk and be git-tracked (unresolvable warns, ignored errors, unstaged warns); catalog, CODES, and §3.4.1 C18 updated
- EVAL-REPORT-TEMPLATE.yaml list sections gain `_example` lists — file parses; validator/report-canon tests upgraded to parsed assertions (#753)
- `framework/VERSION` bumped from `0.62.4` to `0.62.5` with mechanical pin sweep

## [0.62.4] — 2026-09-27

### Fixed — docs-truthfulness batch: playbook rot, plan statuses, census, anchors, D-series log (C2 PATCH → 0.62.4)

- Playbook rot (#709): IPVERIFY validator example replaced with the real EVAL-RPT §3/§4/§5/§9 skeleton; dead-script rows marked archived; unbuilt `generate-rpt` CLI removed. SPEC index template repoints `tools/sdd_coverage.py` at the in-tree COV01 gate (#686)
- Stale statuses (#692): four plan headers SHIPPED/RATIFIED with a per-step CLEANUP-001 disposition. Stale counts fixed: REVIEW_TEAM census (58 files, 9 crews, auditor IPLAN+CHG) (#707); conformance README 10 layers; README layout gains LEARNED_LESSONS (#695)
- Dangling anchors repaired (#694): DOC_GOVERNANCE_CORE §3.7 → §"IPLAN Lifecycle"; §SDD/§CHG-Rules → C13–C14/C16; LINT_RULES GOV-018 → flows §1; Emergency line-number cites dropped
- D-series log (#720): retired-ID annex in `governance/DECISIONS.md`; D-0065/D-0070/D-0078/D-0084/D-0085 recorded in `plans/DECISIONS.md`; live pointers repointed
- New regression test: `test_validator_example_uses_template_keys`
- `framework/VERSION` bumped from `0.62.3` to `0.62.4` with mechanical pin sweep

## [0.62.3] — 2026-09-27

### Fixed — adaptation knob parity: template documents sixth knob (C2 PATCH → 0.62.3)

- `PROFILE-TEMPLATE.yaml` declared 5 knobs while `ADAPTATION_SURFACE.yaml` declares 6; `quality_loop_max_iterations` gains its override row and the count header reads 6 (#704)
- New `test_profile_template_covers_surface_knobs` pins three-way parity (template rows == surface knobs == `ADAPTATION.md` §4 sections)
- `framework/VERSION` bumped from `0.62.2` to `0.62.3` with mechanical pin sweep

## [0.62.2] — 2026-09-27

### Fixed — linter pair: CHG rule coverage + SEED01 per-file pins (C2 PATCH → 0.62.2)

- First unit tests for CHG-L005/L008/L009/L012 + L009 PASS-suppression + `bugfix_lint -h` exit 0 (#717); `SEED01` per-file `seed_file:` resolution + honest set message (#723)
- `framework/VERSION` bumped from `0.62.0` to `0.62.2` with mechanical pin sweep (0.62.1 ships on #744 — merge first)

## [0.62.1] — 2026-09-27

### Fixed — governance pair: Document Control backfill + downstream semantics (C2 PATCH → 0.62.1)

- `GD-24` blocks backfilled on 13 governance docs + conformance guard (#706); `downstream` decided as primary-successor chain (#708)
- `framework/VERSION` bumped from `0.62.0` to `0.62.1` with mechanical pin sweep

## [0.62.0] — 2026-09-27

### Added — framework skills library (MINOR → 0.62.0)

- `framework/skills/` ships 12 engine-agnostic skills adapted from canon (#719 skills leg); `AGENTS.md` points at them
- `framework/VERSION` bumped from `0.61.8` to `0.62.0` with mechanical pin sweep

## [0.61.8] — 2026-09-26

### Removed — dead framework/scripts/ directory (C1 PATCH → 0.61.8)

- Uncalled DEPRECATED drivers of the retired IPLAN-VERIFY flow (#740)
- `framework/VERSION` bumped from `0.61.7` to `0.61.8` with mechanical pin sweep

## [0.61.7] — 2026-09-26

### Fixed — enforcement-scope pair: L011 resolver + L005 Type-F gap (C2 PATCH → 0.61.7)

- `CHG-L011` glob repair + empty-lifecycle root-scan fallback (#713); `CHG-L005` fires on IPLAN-only lifecycle flows, F2-direct preserved (#733)
- `framework/VERSION` bumped from `0.61.6` to `0.61.7` with mechanical pin sweep

## [0.61.6] — 2026-09-26

### Fixed — governance truthfulness batch (C1 PATCH → 0.61.6)

- Phantom governance pointers, IPLAN-VERIFY retirement, phase casing, mirror pin (#697, #698, #714, #700)
- `framework/VERSION` bumped from `0.61.5` to `0.61.6` with mechanical pin sweep

## [0.61.5] — 2026-09-26

### Fixed — lint truthfulness batch: severity fork, L014/L015 source gate, stale docstrings (C2 PATCH → 0.61.5)

- §3.14 severity table resynced to emitter reality (#716); `CHG-L014`/`L015` cover `spec` + `reconciliation` sources (#722); vendoring docstrings rewritten (#696)
- `framework/VERSION` bumped from `0.61.4` to `0.61.5` with mechanical pin sweep

## [0.61.4] — 2026-09-26

### Fixed — lint catalog single source of truth + codes-vs-catalog guard (C1 PATCH → 0.61.4)

- `LINT_RULES.md` now catalogues all `CHG-L001`–`L015` with verified severities; every `GOV-*` row marked **Alias of** its enforcing check or **Reserved** (18 unimplemented IDs honest); new `test_lint_catalog.py` guard enforces both directions (#715)
- `framework/VERSION` bumped from `0.61.3` to `0.61.4` with mechanical pin sweep

## [0.61.3] — 2026-09-26

### Fixed — GATE-SPEC criteria engine-agnostic; archive-tier exemption (C1 PATCH → 0.61.3)

- GATE-SPEC entry/exit criteria no longer require "both platforms re-declare `FRAMEWORK_SPEC_VERSION`" or "both platform owners" approval — unsatisfiable since the 2026-09-07 platform archive (#702). Consumer-neutral criteria (pins re-declared, conformance green, maintainer + reviewers) applied across the gate, catalog, diagram, approval form, CHG template, READMEs, playbook, and `archive/platforms` pointers
- Archive-tier-only repairs (`framework/archive/**`) exempt from VERSION/CHANGELOG obligations in `tests/chg/spec_gate.py` with conformance tests (#725)
- `framework/VERSION` bumped from `0.61.2` to `0.61.3` with mechanical pin sweep

## [0.61.2] — 2026-09-26

### Added — Validate-before-work agent rule (C1 PATCH → 0.61.2)

- New governance rule across `AGENTS.md`, `GOVERNANCE.md`, `framework/AI_ASSISTANT_RULES.md`: agents re-validate picked-up issues live before acting, keep changes behavior-safe, file a CHG first for breaking/significant changes
- `framework/VERSION` bumped from `0.61.1` to `0.61.2` with mechanical pin sweep

## [0.61.1] — 2026-09-25

### Fixed — Archive VERSION snapshots cited by CHG-03/05/11 manifests (C1 PATCH → 0.61.1)

- Ship the three missing pre-bump snapshots cited by archived manifests: `framework/archive/CHG-03/VERSION` = `0.53.3`, `framework/archive/CHG-05/VERSION` = `0.55.0`, `framework/archive/CHG-11/VERSION` = `0.60.0` (closes #721)
- `framework/VERSION` bumped from `0.61.0` to `0.61.1` with mechanical pin sweep (E005/E008: archive vehicle under `framework/archive/` counts as framework change)

## [0.61.0] — 2026-09-24

### Added — Versioned seed tier + GOV-021 AI document-control rule (CHG-11, C2 MINOR → 0.61.0)

- Seed tier versions via archive → rewrite → bump + supersedes (frozen per version, affected files only); `seed_scope` gains the `supersede` decision with entries; BRD ledger rows pin `seed_version` with SEED01 failing stale pins (GD-36, #684)
- GOV-021: every AI-created/modified versioned document carries `document_control` + metadata (backfilled when missing); deterministic half enforced as CHG-L015, seed carrier schema in SEED_CONTRACT
- `framework/VERSION` bumped from `0.60.0` to `0.61.0` with mechanical pin sweep

## [0.60.0] — 2026-09-23

### Added — Modules-first F3 extension (CHG-10, C2 MINOR → 0.60.0)

- F3 Phase 0a seed_scope + 0b module_lifecycle + review checkpoint (F3-only); GOV-020/CHG-L014 enforcement, template §4A/§4B, router-matrix agreement
- `framework/VERSION` bumped from `0.59.2` to `0.60.0` with mechanical pin sweep

## [0.59.2] — 2026-09-23

### Fixed — AGENTS.md authority-flip (CHG-09, C1 PATCH → 0.59.2)

- Working agreement declares the single agreement (this file wins), CLAUDE.md deprecated/never-authority, self-contained CLAUDE.md pointers dropped, worktree pointer added
- `framework/VERSION` bumped from `0.59.1` to `0.59.2` with mechanical pin sweep

## [0.59.1] — 2026-09-23

### Fixed — STALE P2 sweeps + T1 remedy (CHG-08, C2 PATCH → 0.59.1)

- P2 doc sweeps D1–D6: versions reworded-not-swept, dead paths framed-or-fixed, push leg → dev, one layer language (09 operational namespace) (#670)
- T1 remedy: 8 unrunnable unit modules deleted, sync test re-anchored to the live hook — suite green with zero skips (#665)
- D5/D6 harness: CHG/EVAL goldens + layer tests, linter CHG/EVAL coverage (section fallback, `_KNOWN`), VALID_TYPES derived from template, section pins extended, validator delegation, fossil repoint (#670)
- `framework/VERSION` bumped from `0.59.0` to `0.59.1` with mechanical pin sweep

## [0.59.0] — 2026-09-23

### Added — STALE P1 canons: one canonical surface per fork (CHG-08, C2 MINOR → 0.59.0)

- EVAL report canon REPORT + RPT tombstone; CHG template canon `governance/chg/` (KEEP §7, 8-layer enum, byte-identical twins); playbook split + `validator.md` retarget; 8 MVP tombstones + index retargets; vehicle → EVAL-RPT + bugfix canon (`tmp/` retired); triple-lock rows + File Naming rewrite (#664 #667 #672 #666 #662 #671 #669)
- `framework/VERSION` bumped from `0.58.0` to `0.59.0` with mechanical pin sweep

## [0.58.0] — 2026-09-23

### Fixed — STALE P0 remediation: tests, linter, hooks (CHG-08, C2 MINOR → 0.58.0)

- `tests/unit` quarantine: red modules skip with cited issue until the delete-or-reanchor remedy (#665)
- `sdd_doc_lint/chg_lint.py` contradictions fixed (Proposed early-pass, L001 dedup, missing-phase error, steps-scan L004 + GOV-019, L005 fold) + L001–L005 fixtures + `_common.py` extraction (#668)
- Hook gates: `*.sh` watch, TEMPLATE skip, commit-message check, pre-commit wiring, docs-list resync, `OLD_VERSIONS` + pin test, pre-push/review fixes (#663)
- `framework/VERSION` bumped from `0.57.1` to `0.58.0` with mechanical pin sweep

## [0.57.1] — 2026-09-22

### Fixed — AGENTS.md freshness post-0.57.0 (CHG-07, C1 PATCH → 0.57.1)

- Root working agreement: dead-file mandates dropped, gate exceptions corrected,
  SDD-first scoped, `python3` invocation, CHG-L013 line, flows-router pointer (#675)
- `framework/VERSION` bumped from `0.57.0` to `0.57.1` with mechanical pin sweep
  (E005/E008: archive vehicle under `framework/archive/CHG-07/` counts as framework change)

## [0.57.0] — 2026-09-22

### Added — CHG request flows router (CHG-06, GD-32, C2 MINOR → 0.57.0)

- New `framework/governance/CHG_REQUEST_FLOWS.md` (canonical, ratified): F1 greenfield,
  F2 direct, F3 brownfield, F4 bugfix vehicle, Emergency/Type-R yields, C1/IPLAN-gate
  ruling (code-touching C1 requires C1 CHG + scoped IPLAN), GOV-018 guard
- `DOC_GOVERNANCE_CORE.md`: §3.1.3 router kernel + §3.13 F2.2 sentence; `LINT_RULES.md`:
  GOV-018 row; CHG twins: `direct` source row (GATE-CODE) + C1 bound + enum comments
- `sdd_doc_lint/chg_lint.py`: CHG-L013 misclassification check + fixtures; new
  `tests/conformance/test_chg_flows_router.py` agreement test; 09_CHG READMEs gain
  the selector table; `hooks/sync-version-refs.sh` gains 0.56.0 sweep lines
- `framework/VERSION` bumped from `0.56.0` to `0.57.0` with mechanical pin sweep

## [0.56.0] — 2026-09-22

### Added — Scoped bugfix IPLAN vehicle for post-completion defects (CHG-05, GD-31, C2 MINOR → 0.56.0)

- `bugfix` IPLAN subtype (`parent_iplan`/`source_chg` homes, scope-limited manifest,
  normative order fix → regression → rollback → revision entry last, mandatory rollback
  with PENDING→DONE/SKIPPED markers, no-fix-on-fix, parent immutable) in
  `IPLAN-TEMPLATE.yaml`; `## IPLAN Subtypes` + Completed-validatable vs Verified-terminal
  - active-definition pointer in `08_IPLAN/README.md`
- Terminal semantics fixed canon-wide (`Completed` validatable with `validated_by: pending`
  after pre-VERIFY merge; only `Verified` terminal); **active** defined as
  `Draft | Approved | In Progress` (§3.13 exception covers active only); migration VERIFY
  requires fresh-rebuild + live-DB dry-run
- `IPLAN/tmp/` promise retired (GATE-08/GATE-CODE twins + registry sentence point at
  the bugfix vehicle); GOV-013 carve-out + `BGF-01..07` catalog rows in `LINT_RULES.md`
- New `sdd_doc_lint/bugfix_lint.py` (BGF-01..07) + `test_bugfix_lint.py` (10/10) +
  `tests/conformance/test_iplan_bugfix_lifecycle.py` (10/10, incl. BGF catalog-agreement guard)
- Rejects: both-terminal, mandatory `detection_gap`, `Related-IPLAN` bypass,
  `revision_history`-on-IPLAN, new layer/registry/template fork (issues #656/#657)

## [0.55.0] — 2026-09-21

### Added — Type-R code-to-doc reconciliation flow (CHG-04, GD-30, C2 MINOR → 0.55.0)

- `DOC_GOVERNANCE_CORE.md` §3.1.2: Type-R bounded exception to SDD-first (trigger, Phase 0–3 flow, guardrails incl. Emergency disambiguation)
- CHG twins: `reconciliation` change_source (entry GATE-CODE), Dual Lifecycle section, routing rows; GATE-CODE §1.3/§6.3 notes

## [0.54.0] — 2026-09-20

### Added — 17 donor-hardening addons ported into the spec (CHG-03, GD-29, C2 MINOR)

- SDD-first implementation order table (§3.1.1), §3.13 bootstrap exemption, IPLAN Lifecycle
  bundle (status-gate table, failure modes, DONE-must-exist, realtime manifest, CHG-tracks-IPLAN,
  SDD-sync-on-completion with `completion_spec_sync` + CHG-L012), `## Status Propagation (§4.1)`,
  and `WORKTREE_FLOW.md` pointer in `DOC_GOVERNANCE_CORE.md` (twin EVAL blocks deduped first)
- `completion_gates` + `completion_spec_sync` blocks, `breaking_change` block, `audit_fix`
  fourth subtype, and realtime-manifest rules in `IPLAN-TEMPLATE.yaml`; `## IPLAN Subtypes`
  in `08_IPLAN/README.md`
- New-layer registration checklist in `LAYER_REGISTRY.yaml` + `registry/README.md`;
  `REG01`, `CHG-L012`, `IPLAN01`, `TDD-SYNC-A..E` catalog rows in `LINT_RULES.md` (all advisory)
- CHG-L012 warning check in `chg_lint.py`; SKIPPED-vs-clean warning in `__main__.py`;
  scoped governed-archive negation in `.gitignore`
- EARS pattern decision tree in `03_EARS/README.md` + lens note in `requirements_specialist.md`;
  TDD-SYNC-E index-sync notes in `TDD-00_index` + `IPLAN-00_index` templates
- Delegation grep validation, genericized Rule 5, `## Concurrency traps`, advisory
  `TDD-SYNC-A..E` rename in `NOTICES.md`; ID red-flag box in `ID_NAMING_STANDARDS.md`;
  §7.4 feedback-submit contract in `SELF_LEARNING.md`; delegation/concurrency pointers
  in `AI_ASSISTANT_RULES.md`
- NEW `framework/governance/WORKTREE_FLOW.md` v1.0 (worktree-remove-before-branch-delete order guard)
- `framework/VERSION` bumped from `0.53.3` to `0.54.0` with mechanical pin sweep

## [0.53.2] — 2026-09-08

### Fixed — CHG template phase enforcement, governance sync, AI_ASSISTANT_RULES fix

**CHG template (CHG-FW-001):**

- Added mandatory `phase` field to `implementation.steps` — every step MUST declare `sdd_lifecycle` or `iplan_creation`; `code_implementation` is FORBIDDEN in CHG
- Added `_allowed_phases` reference block to template
- Updated creation checklist items 13-14 to reference phase field
- Updated `_guidance` in Section 4 with explicit phase enforcement rules
- Synced stale `governance/chg/` directory from `layers/09_CHG/` (12 files were out of date)
- Archived originals to `archive/CHG-FW-001/`

**Lint rules:**

- Added `GOV-010` — error when CHG steps lack `phase` field or use `code_implementation`

**DOC_GOVERNANCE_CORE.md:**

- Updated checklist items 13-14 to reference phase field

**AI_ASSISTANT_RULES.md:**

- Rewrote "What NOT to Reference" section — moved CHG gates out of the "do not reference" list into a dedicated "When to Reference" section (self-learn 2026-09-08 found the original actively undermined governance)

## [0.53.1] — 2026-09-08

### Fixed — P0 governance, acceptance fixtures, CI repin, template alignment (#620, #637, #635, #636, #588, #393, #641, #642, #596, #565)

**Governance & test fixes:**

- Phantom-release guard now reads working tree VERSION to avoid false phantoms on staged-but-uncommitted bumps (#620)
- Ported GOV-008/GOV-009 lint rules and MANDATORY PROCESS GATE from archived governance into active DOC_GOVERNANCE_CORE.md and LINT_RULES.md (#641)
- Ported EVAL-001/002/003/EVAL-COV-001 lint rules into active LINT_RULES.md; added EVAL downstream to BDD-00_index.TEMPLATE.md (#642)
- Fixed three stale D-0084 comments in auto-merge-ai-prs.yml, ai-review/config.json, and standards-drift.yml (#596)

**Acceptance fixtures:**

- Renamed BDD.01.04.*→ BDD.01.03.* (scenarios in section 3) and BDD.01.04.aaaa → BDD.01.02.aaaa (feature in section 2) across 33 files (#637)
- Added element declarations to ADR golden fixtures; re-cited doc-level @adr/@tdd as element-level in downstream goldens; removed 5 REFGRAN01 manifest entries (#635)
- Added closing frontmatter fence and doc_id to 3 broken_chain YAML golden fixtures (#636)

**Infrastructure:**

- Repinned all 12 stale CI workflow pins from ci/v2.16.0/v3.0.0 to ci/v4.0.0 (#393)
- Added doc_id: field to all 9 layer templates — the key the linter actually reads (#588)
- Added conformance test locking extensions to [.yaml] for all layers per GD-15 (#565)

### Changed — Platforms archived, framework becomes self-sufficient (2026-09-07)

### Fixed — the acceptance goldens never adopted the normative TDD acceptance-pairing form; 8 pinned findings clear (#478) (2026-09-04)

`TDD-01_golden.yaml` carried `test_mapping.coverage_table.columns` but **omitted the
`test_mapping.scenarios:` list entirely**, which `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
declares normative for GD-08 acceptance pairing. `_check_acceptance_pairing` pairs a BDD
scenario only when a TDD line carries a real `@bdd:` tag beside a test-case id or a
`bdd_scenario`/`bdd_ref` carrier, so every scenario read as unpaired — and the fixture also
wrote `bdd_ref: BDD.01.03.bbbb` without the `@bdd:` prefix the template prescribes.
Separately `EARS.01.03.cccc` (checkout) was realized by nothing: the BDD covered sign-in and
catalog search only.

**These were errors, not warnings, in `gate-code`** — so the acceptance tier's `valid/`
positive controls could not pass the framework's own code gate.

Authoring the normative `scenarios:` list clears `ACC01` ×4 and `COV02` ×3; a new
`BDD.01.03.eeee` checkout scenario citing `@ears: EARS.01.03.cccc` clears the fourth `COV02`.

```
fullpath/golden_chain  {COV02:4, ACC01:4, REFGRAN01:5} -> {REFGRAN01:5}
layer_07_tdd/valid     {ACC01:4, COV02:4, REFGRAN01:3} -> {REFGRAN01:3}
layer_08_iplan/valid   {ACC01:4, COV02:4, REFGRAN01:5} -> {REFGRAN01:5}
layer_06_spec/valid    {COV02:4, REFGRAN01:2}          -> unchanged
```

Manifests go from **39 entries / 43 warnings to 15 / 19**. `layer_06_spec/valid` is net-zero
by design, not by omission: it stages a SPEC and no TDD, and `SPEC-01_golden.yaml` cites only
`@bdd: BDD.01.02.aaaa` element-level, so `BDD.01.03.eeee` takes the departing
`EARS.01.03.cccc` slot for the same structural reason its three siblings were already pinned.

**The remaining five `REFGRAN01` are split out to #635** — they cannot be cleared by re-citing,
because `ADR-01_golden.md` declares no `ADR.01.SS.xxxx` element, and they are sequenced
behind issue #563. **The three remaining `broken_chain` fences are split out to #636.**

Two source comments that misdescribed current state were corrected in the same change:
`tests/conformance/test_forward_coverage_is_exercised.py` still attributed the per-layer
targets' invisibility to a fence defect PR #580 had already fixed (`layer_08_iplan/valid` is a
second live `COV01` target; `layer_06`/`layer_07` stage no IPLAN, so `COV01` there is
inapplicable, not blind), and `tests/acceptance/deterministic/test_doc_validator.py` claimed a
single HTML-comment marker was the whole difference between `golden_chain` and `broken_chain`
when five files differ and always have.

Tests only — no framework spec, platform or tooling surface is touched.

### Changed — Framework Spec `0.50.0` → `0.51.0`: a Draft IPLAN's §5 `session_handoff.sessions` is empty (GD-26, #621) (2026-09-04)

**Platforms archived.** Hermes MCP server and Claude Code plugin moved to
`archive/platforms/`. Any capable AI agent derives its behavior from the
framework spec, templates, and playbooks directly — no platform-specific
wrapper needed.

**Tooling reorganized.**

- `sdd_doc_lint/` — moved to repo root (structural linter, 296+ checks)
- `hooks/` — PostToolUse advisory hook + pre-commit/pre-push hooks
- `tools/` — archived (saga_driver.py, finding_filter.py, etc.)
- `plans/` — archived (migration plans)
- `legacy/` — moved to `archive/legacy/`
- `.claude-plugin/` — archived (plugin marketplace config)
- `scripts/` — hooks moved to `hooks/`, utilities archived

**Tests cleaned up.**

- Linter-specific tests moved to `sdd_doc_lint/tests/` (14 files)
- Platform-specific conformance tests archived
- Stale acceptance live harnesses archived
- All path references updated

**Docs updated.** All core docs (README, CLAUDE.md, AGENTS.md, CONTRIBUTING.md,
SECURITY.md, etc.) updated to reflect new structure.

**Framework is now ~90% self-sufficient.** Agents can author, review, and
validate artifacts from the spec alone.

### Changed — Framework Spec `0.51.0` → `0.53.0` (2026-09-07)

**GD-24: `document_control` for all framework governance documents.** All
governance docs, gate definitions, layer READMEs, root-level reference docs,
playbook READMEs, and YAML data files now carry version tracking metadata.
66 files modified, 67 originals archived to `archive/CHG-01/`. (`CHG-01`,
GATE-SPEC, C2, minor)

**GD-25: `.aidoc/` redefined as project override layer.** The `.aidoc/`
directory now holds the project profile and project-specific overrides
(`.aidoc/project/`) instead of unused AI provenance subdirectories. New
discovery rule: `.aidoc/project/` first, fall back to framework defaults.
(`CHG-02`, GATE-SPEC, C2, minor)

**10-layer model.** CHG promoted from governance overlay to Layer 9; EVAL
added as Layer 10. All layer templates, READMEs, and the layer registry updated.

## [0.53.0] — 2026-09-07

- GD-25: `.aidoc/` redefined as project override layer
- `governance/aidoc/AIDOC.md` rewritten with new purpose and discovery rule
- `README.md` four-tier model updated
- `governance/ADAPTATION.md` §10 added — project overrides contract

## [0.52.0] — 2026-09-07

- GD-24: `document_control` added to all 66 framework governance documents
- 67 original files archived to `archive/CHG-01/`
- New playbooks: `gate_spec_change.md`, `document_control.md`
- `PROFILE-TEMPLATE.yaml` duplicate metadata key fixed

## [0.51.0] — 2026-09-04

- GD-26: Draft IPLAN's §5 `session_handoff.sessions` is empty (`sessions: []`)
- Template and layer README updated with guidance

## [0.50.0] — 2026-09-04

- GD-25: IPLAN `code_inventory` seeds `planned` at Draft

## [0.49.0] — 2026-08-30

- Framework spec consolidation and cleanup

## [0.48.0] — 2026-08-28

- GD-23: Three layer templates declare no title

## [0.47.0] — 2026-08-25

- GD-19, GD-20, GD-21, GD-22 shipped as one release

## [0.46.0] — 2026-08-20

- GD-18: Derived test paths, threshold carriers, IPLAN status contract
