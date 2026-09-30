# Changelog — SDD Framework

All notable changes to the shared engine-agnostic specification are documented here.
This file is the project's document-of-record for spec changes (GATE-SPEC-E008).

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.3 |
| Status | Approved |
| Last Updated | 2026-09-30 |
| Author | Framework Maintainer |
| Framework Version | 0.67.0 |

---

## [0.67.0] — 2026-09-30

### Removed — Tier-1 consumer feedback log retired (C2 MINOR, CHG-23 + IPLAN-23)

- `FRAMEWORK_FEEDBACK_LOG.md` v1.0 → v2.0: Tier-1 consumer-project section,
  consumer template section, examples-corpus Tier-2 bullet, and dead tags
  (`[harness]`, `[example-corpus]`, `[platform-parity]`) removed. Filing
  discipline + open-items surface retained (SELF_LEARNING.md §7.4 dependency);
  doc retained (`test_governance.py` census).
- `framework/templates/framework-feedback-log.template.md` deleted (no
  in-repo references; external copiers directed here).
- `DOC_GOVERNANCE_CORE.md` v1.2 → v1.3: Principle 9 rewritten tracker-only.
- GD-41 records both rulings.

### Changed — per-task worktree unconditional (C2, CHG-23)

- AGENTS.md quick-path exception removed; post-merge cleanup codified
  (worktree remove BEFORE branch delete, §3.7 order guard).
- `framework/VERSION` bumped from `0.66.0` to `0.67.0` with mechanical pin sweep.

## [0.66.0] — 2026-09-29

### Added — self-learn Two-Tier Project Knowledge Architecture + vendor-neutral skill (C3 MINOR, CHG-18 + IPLAN-18, issue #779 phase-b)

- `SELF_LEARNING.md` v1.1 → v2.0: Tier model (Tier 1 invariants by reference,
  Tier 2 on-demand `.aidoc/learning/` knowledge, Tier 3 the §7.4 upstream
  feedback contract by reference — no Tier-3 storage, no universal log) plus a
  truthfulness pass (harness hooks/stores illustrative, portable fallback).
- `framework/skills/self-learn/` decoupled from MiMoCode-only
  paths/schemas (ported from the hardened `.agents` copy; header untouched).
- GD-40: folder decision (KEEP `.aidoc/learning/`, draft rename declined) +
  architecture adoption.
- `tests/conformance/test_self_learning.py` extended: decoupling-token absence
  + Tier markers + learning/-folder pins, each proven live on the originals.
- `framework/VERSION` bumped from `0.65.2` to `0.66.0` with mechanical pin sweep.

## [0.65.2] — 2026-09-29

### Fixed — self-learn solo direct-write loophole closed (C2 PATCH, CHG-17 + IPLAN-17, issue #779 phase-a)

- `SELF_LEARNING.md` v1.0 → v1.1: the solo-project direct-write exemption is
  removed (promotion section + Prevention Rule 2). Every governance write —
  solo or multi-contributor — rides an authorizing CHG and an In-Progress
  IPLAN (always-traced); solo projects use self-approved C3 (owner as
  Technical Lead), never silent direct write. Additive/cited/small kept.
- New `tests/conformance/test_self_learning.py`: exemption-absence +
  authorization-presence pins.
- Out of scope (CHG-18 C3 later): two-tier rewrite, knowledge/ vs learning/
  folder decision + BOOTSTRAP.md reconciliation, framework skill decoupling,
  universal tier.
- `framework/VERSION` bumped from `0.65.1` to `0.65.2` with mechanical pin sweep.

## [0.65.1] — 2026-09-29

### Fixed — docs/deploy batch: approval rule, aidoc bootstrap, upgrade runbook (C2 PATCH, CHG-16 + IPLAN-16, issues #784/#785/#786/#787)

- C3/spec-gate approval codified as judge-then-human (#784, Option A):
  mandatory independent `second-opinion` review BEFORE the human surfacing;
  an AI verdict may satisfy a review gate, never an approval gate. Bounded
  AI-approver tier (Option B) explicitly declined. `chg/README.md` v1.2 → v1.3
  (+ byte-identical twin `layers/09_CHG/README.md`).
- Aidoc scaffold `cp` path fixed from the repo root (#785, `framework/` prefix);
  `aidoc/README.md` v1.0 → v1.1 wires the two new runbooks.
- New `aidoc/BOOTSTRAP.md`: ordered bootstrap procedure (scaffold copy,
  profile knobs, symlink, version pin, smoke-verify) + shape validation (#786).
- New `aidoc/UPGRADE-RUNBOOK.md`: consumer re-adoption procedure (re-point,
  override diff, conformance, changelog) behind the GATE-SPEC box (#787).
  Script halves (shape check, stale detector) stay open as follow-ups.
- Out of scope: #779 (self-learn two-tier, P1) ships alone in its own vehicle.
- `framework/VERSION` bumped from `0.65.0` to `0.65.1` with mechanical pin sweep.

## [0.65.0] — 2026-09-29

### Added — per-flow Phase-3 closeout rule (C2 MINOR, CHG-14 + IPLAN-14, issue #776)

- Deployable scope mandates live closeout (deploy DEV, smoke suite, authentic
  Layer-10 EVAL) before `Completed`; non-deployable scope (docs-only,
  governance sync, SDD-only) closes via the static battery with no deployment
  and no EVAL owed — fabricated EVALs forbidden; mixed scope follows the
  deployable path (manifest decides). Rule names the evidence, not consumer commands.
- DOC_GOVERNANCE_CORE §3.3 rules 10–11, flows §1 verification-column closeout
  pointers per flow, GD-39; stale §1-table F2 cell repaired (always-traced).
  Enforcement is reviewer-lens (closeout adequacy is judgement over evidence).
- `framework/VERSION` bumped from `0.64.0` to `0.65.0` with mechanical pin sweep.

## [0.64.0] — 2026-09-29

### Added — first-class documentation_sync phase; CHG-L003 scoped to code steps (C2 MINOR, CHG-13 + IPLAN-13, issue #775)

- New legal CHG step phase `documentation_sync` for documentation-only milestones
  (the F2 docs-only C1 shape): `sdd_lifecycle` stays reserved for versioned SDD
  rewrites, `iplan_creation` for IPLAN authoring. Canonical layout + `_allowed_phases`
  in both CHG-TEMPLATE copies; Phase-2 zone in both 09_CHG READMEs; LINT_RULES
  L003/GOV-010 rows, governance core §3.4 items 13–14 + E25 + L003 row, GD-38.
- CHG-L003 keeps erroring on `code` / `implementation` / `code_implementation`
  and on missing phases, but its message now names the legal phases including the
  doc alternative; CHG-L005 orders `documentation_sync` in the execution zone;
  CHG-L004 still requires an IPLAN reference (doc-sync alone satisfies nothing).
- Explicitly NOT shipped: no IPLAN exemption for doc edits (CHG-12 always-traced
  holds); consumer Type-D taxonomy not adopted.
- New `DocumentationSyncPhaseTests` unit pins (L003 pass/message, L004
  non-satisfaction, L005 ordering); mirror twins stay byte-identical.
- `framework/VERSION` bumped from `0.63.0` to `0.64.0` with mechanical pin sweep.

## [0.63.0] — 2026-09-28

### Changed — mandatory CHG+IPLAN for every post-seed activity (C2 MINOR, CHG-12 + IPLAN-12, issues #772/#773)

- Always-traced rule: every post-seed C1 requires a C1 CHG + scoped IPLAN for
  every author (agents and humans). Retired: F2.2 docs-only direct commit, the
  AGENTS.md (i) bug-fix and (ii) docs-only-C1 exceptions, the §3.13 repeats,
  router step 5's direct-commit branch, and both CHG-TEMPLATE C1 rows.
- Sole exception: seed-phase drafting before the first BRD is authored against
  seed vN (`SEED_CONTRACT.md` R1), when no other documents exist yet.
- Supersedes the F2-UNIFY-PLAN D2 human-only exception (rejected candidate
  retain-human-exception recorded in CHG-12). Enforcement is reviewer-lens —
  the PR reviewer verifies every commit rides the authorizing CHG/IPLAN
  manifest, backstopped by branch protection; GOV-018/CHG-L013 stay syntactic
  by design (scope note in `LINT_RULES.md`).
- `DOC_GOVERNANCE_CORE.md` v1.0 → v1.1 (§3.1.3 F2 row, §3.13);
  `CHG_REQUEST_FLOWS.md` v1.1 → v1.2 (F2.2, router step 5, §8(c), F2.4);
  `LINT_RULES.md` v1.0 → v1.1; GD-37 entered in `DECISIONS.md`.
- Guard: new `AlwaysTracedAgreement` pins the unified wording in
  `tests/conformance/test_chg_flows_router.py`; mirror twins stay
  byte-identical (`diff -q` clean on both pairs).
- `framework/VERSION` bumped from `0.62.7` to `0.63.0` with mechanical pin sweep.

## [0.62.7] — 2026-09-28

### Fixed — 09_CHG README mirror twins byte-identical + dead link repaired (C2 PATCH)

- Mirror twins (#770): both 09_CHG READMEs carry one perspective-neutral
  `Canonical home` paragraph (governance copy canonical, wins on conflict) —
  the byte-identical claim is true again (verified with `diff -q`).
- Dead link (#770): the layer copy's `../governance/CHG_REQUEST_FLOWS.md`
  (resolved to nonexistent `framework/layers/governance/`) is now the
  location-independent `framework/governance/CHG_REQUEST_FLOWS.md` in both
  copies. A single relative string cannot resolve from both mirror
  directories (same structural tension as closed #700), so the reference
  ships link-free and greppable.
- Guard: new `test_readme_copies_identical` pins the README twins in
  `tests/conformance/test_chg_flows_router.py` (failed before the fix, passes
  after); the `Canonical home` paragraph now names both pinning tests.
- `framework/VERSION` bumped from `0.62.6` to `0.62.7` with mechanical pin sweep.

## [0.62.6] — 2026-09-28

### Fixed — review-sweep batch: workflow chain, CHG status hardening, ID obligations, saga cleanup (C2 PATCH)

- Workflow chain (#759): L1–L5 `**Workflow**` lines now read `… IPLAN → EVAL → Code`
  (were `… IPLAN → Code`); L6 SPEC / L7 TDD / L8 IPLAN gain the canonical chain
  line. Canonical chain stays `TRACEABILITY.md:16` with the EVAL return edge
  (`PASS → IPLAN Verified`) defined in `10_EVAL/README.md`.
- CHG overlay naming (#760): glossary, CHG template definition, post-mortem root-cause
  row, EVAL README + index diagram, and registry description stop calling CHG `L9` —
  CHG is the `09` operational namespace (governance overlay, GD-01), lifecycle layers
  are L1–L8 + L10. Mirror twins edited identically. Qualified `(L9, overlay)` mentions
  in top-level guides left untouched.
- ID obligations (#761): `ID_NAMING_STANDARDS.md` exemption section now accounts all ten
  layers — 6 MUST + SPEC/IPLAN MAY + **EVAL MUST** (every `test_cases[]` entry carries
  `EVAL.NN.SS.xxxx`) + CHG exempt/NA. Matching MUST lines in `10_EVAL/README.md` and
  `EVAL-TEMPLATE.yaml` §3 guidance. Presence is an author/auditor obligation; the
  linter pins format only (`EVAL-ID-001`).
- SPEC README (#762): new Element-ID exemption + Upstream Traceability sections
  (ADR pattern); readiness cell now states the normative threshold
  (`TDD-Ready >= 90%`, GATE-06).
- ADR wording (#763): overview synthesizes EARS and BDD (which transitively carry
  PRD context); `required_tags: [ears, bdd]` unchanged.
- Phantom pointer (#764): §3.4 item 12 now cites `§3.4.1 E25–E27` (were nonexistent
  `C13–C14`).
- CHG status hardening (#765): §3.3 gains rules 5–9 (issue-level match,
  ship-in-same-change, In-Progress resumption, step-status invariant, zero-work
  Completed ban) and §3.4.1 gains **E28** (no `Completed` step before its code is
  written and verified). Deterministic half enforced by new rule **CHG-L017**
  (`Proposed` / `Approved` + `Completed` step errors; `In-Progress`+ passes);
  catalog updates (`CODES` 1..17, `LINT_RULES.md` L017 row, `test_lint_catalog`
  pin, `AGENTS.md` catalog line) + 5 new unit tests (`PrematureCompletionTests`).
- Rewrite hygiene (#766): §3.4 item 11 states the purge obligation — rewrites drop
  stale content so v2 reads as written from scratch.
- Agent conduct (#767): new `AI_ASSISTANT_RULES.md` prohibition — no `--no-verify`
  (or equivalents), no hook bypasses, auto-merge only on all-green. Boundary
  detection stays the backstop, not the permission.
- Gate hygiene (#768): `REVIEW_REMEDIATION_FLOW.md` `pre_merge` section states the
  load-proof rule — every required gate proven to execute, full set enumerated in
  one list. No tool names ported (D-0013).
- Saga cleanup (#701): `REVIEW_SAGA.md` drops dead `docs/PARITY.md` + `platforms/`
  references, rewrites the spec-version section engine-agnostic, matches the
  `layer` enum and `transitions[]` required fields to `saga.schema.json`.
  D-0031/D-0005 cites and the parity test already resolve (stale sub-claims).
- `framework/VERSION` bumped from `0.62.5` to `0.62.6` with mechanical pin sweep.

## [0.62.5] — 2026-09-27

### Fixed — CHG-L016 archive-snapshot existence + EVAL template parses (C2 PATCH)

- New rule **CHG-L016** (`§3.4.1 C18`): every cited `archive_path` must
  resolve to a file on disk (repo-root- or CHG-relative) and be git-tracked.
  Unresolvable paths warn (fixtures/out-of-tree refs are unverifiable, not
  fabrications); resolvable-but-ignored paths error (the #757 swallow shape —
  never lands without `-f`); resolvable-but-unstaged paths warn. Closes the
  cited-but-missing hole the #757 transfer reports against the L001–L005-era
  tool (L007/L008/L010 already cover non-null/shape/parity; the adopter
  `.gitignore` half is N/A here; `--diff`/`archive_sdd.py` are adopter-side).
- Catalog updates: `CODES` 1..16, `LINT_RULES.md` L016 row, `test_lint_catalog`
  pin, `AGENTS.md` catalog line, DOC_GOVERNANCE_CORE C18 clause + rule-table
  row. 4 new unit tests (`ArchiveSnapshotTests`); L016 verified passing on
  live CHG-11 (3 snapshots exist and are committable).
- #753: `EVAL-REPORT-TEMPLATE.yaml` §4/§5/§8 list sections carry `_example`
  lists beside `_guidance` (BRD convention) — the file parses as a plain
  mapping; `test_validator_example_uses_template_keys` and
  `test_report_has_test_results_section` upgraded from textual to parsed
  assertions.
- `framework/VERSION` bumped from `0.62.4` to `0.62.5` with mechanical pin sweep.

## [0.62.4] — 2026-09-27

### Fixed — docs-truthfulness batch (C2 PATCH)

- Playbook rot (#709): `10_IPVERIFY/validator.md` Example Usage + Output
  Example replaced with a real EVAL-RPT §3/§4/§5/§9 skeleton (`results`,
  `test_results`, `findings`, `verdict`; severities stop at P2) — the old
  `validation_summary:`/`recommendations:`/`p3_count:` shape existed in no
  template. `README.md` script rows marked archived/nonexistent;
  `report_generator.md` unbuilt-CLI block replaced with manual-authoring steps.
  New `test_validator_example_uses_template_keys` pins example ⊆ template keys.
- Dead tool paths (#686): `SPEC-00_index.TEMPLATE.md` cites the in-tree
  `sdd_doc_lint._check_forward_coverage` (COV01) instead of
  `tools/sdd_coverage.py`; vendored-copy remnants fixed in
  `sdd_doc_lint/__init__.py` + test comments + `test_lint.py` run instruction.
- Plan statuses (#692): CLEANUP-001/STALE-REVIEW/IPLAN-TERMINAL/TYPE-R headers
  SHIPPED/RATIFIED with evidence; CLEANUP-001 gains a per-step disposition table.
- Census (#707): `REVIEW_TEAM.md` — 58 files (53 layer+lens), IPVERIFY
  `layer: 10_EVAL` exception documented, CHG+EVAL upstream rows, auditor at
  IPLAN+CHG, 9 crews with EVAL verdict-graded not crew-scored.
- Anchors (#694): §3.7 cites → §"IPLAN Lifecycle" (+ LEARNED_LESSONS era
  caveat); §SDD/§CHG-Rules → C13–C14/C16 (both CHG-TEMPLATE twins + both
  09_CHG READMEs); GOV-018 → flows §1; Emergency line-number cites dropped.
- Hygiene (#695): `framework/README.md` layout gains LEARNED_LESSONS.md;
  `tests/conformance/README.md` 10 dense layers + exact `required_tags`.
- Decision log (#720): D-series annex (14 cited IDs with commit evidence +
  live equivalents); D-0065/D-0070/D-0078/D-0084/D-0085 recorded in
  `plans/DECISIONS.md` (authority line fixed); REVIEW_SAGA, TRACEABILITY,
  STARTUP_HANDOFF, pin-currency pointers repointed.
- `framework/VERSION` bumped from `0.62.3` to `0.62.4` with mechanical pin sweep.

## [0.62.3] — 2026-09-27

### Fixed — adaptation knob parity: template documents sixth knob (C2 PATCH)

- `governance/PROFILE-TEMPLATE.yaml` declared 5 knobs while
  `governance/ADAPTATION_SURFACE.yaml` declares 6 — `quality_loop_max_iterations`
  had no override row, so adapters starting from the template silently lost it
  (#704). Count header 5→6; new commented override row (`3`, range 1–10,
  malformed-falls-back-to-default per `ADAPTATION.md` §4.6).
- New `test_profile_template_covers_surface_knobs`
  (`tests/conformance/test_governance.py`) pins three-way parity: every surface
  knob has a template override row, the template count header equals the surface
  knob count, and the `ADAPTATION.md` §4 subsections match the surface knob set.
- `framework/VERSION` bumped from `0.62.2` to `0.62.3` with mechanical pin sweep.

## [0.62.2] — 2026-09-27

### Fixed — linter pair: CHG rule coverage + SEED01 per-file pins (C2 PATCH)

- Four CHG rules gain first unit tests (#717): L005 ordering half (SddOrderTests;
  IPLAN-only half already pinned by #733), L008 date-vs-CHG-ID paths, L009
  equal-vs-differing versions, L012 attested/unattested/diverged attestations
  (13 tests: 10 in `test_chg_lint.py`, 3 help-exit in `test_bugfix_lint.py`).
  Two output-contract minors fixed alongside: L009 no longer prints the
  "N new_version(s) differ" PASS on runs where it errored; `bugfix_lint -h`
  exits 0 instead of 2.
- `SEED01` resolves `seed_version` pins per file (#723): new optional
  `seed_file:` row field (BRD template `_guidance` + `_example`,
  `SEED_CONTRACT.md` Rule 2 + enforcement split, `LINT_RULES.md` SEED01 row);
  rows naming it resolve against that file's version, rows without it keep
  legacy set-membership (never a per-file guess), unresolvable names skip.
  The legacy diagnostic reports the whole corpus set instead of an arbitrary
  `sorted(...)[0]`. 5 new conformance tests pin the behavior.
- `framework/VERSION` bumped from `0.62.0` to `0.62.2` with mechanical pin sweep
  (0.62.1 ships on #744 — merge first).

## [0.62.1] — 2026-09-27

### Fixed — governance pair: Document Control backfill + downstream semantics (C2 PATCH)

- `GD-24` Document Control blocks backfilled on the 13 governance docs missing
  them (#706): AUTHORING_STYLE, DEFINITION_OF_DONE, DIAGRAM_STANDARDS,
  DOC_GOVERNANCE_CORE, ID_NAMING_STANDARDS, LINT_RULES, REVIEW_REMEDIATION_FLOW,
  REVIEW_SAGA, REVIEW_TEAM, SECURITY_REVIEW, TAG_SYNTAX, THRESHOLD_NAMING_RULES,
  TRACEABILITY; new `tests/conformance/test_document_control.py` guard pins the
  block, its five fields, and the Framework Version pin on every
  `framework/governance/*.md`.
- `downstream` semantics decided as primary-successor chain, not the inverse of
  `required_tags` (#708): `framework/README.md` no longer calls it the full
  traceability graph, `LAYER_REGISTRY.yaml` header records the decision, the
  CODE sink is documented as a terminal (not a layer), and
  `test_downstream_is_primary_successor_not_inverse` pins the EARS asymmetry.
- `framework/VERSION` bumped from `0.62.0` to `0.62.1` with mechanical pin sweep.

## [0.62.0] — 2026-09-27

### Added — framework skills library (MINOR)

- New `framework/skills/` (12 engine-agnostic skills adapted from private canon `aidoc-flow-claude-agents-config/skills` 2026-09-27): approval-gate, context-handoff, memory-hygiene (+`lint.py`), preprod-review (+lens briefs), recall, second-opinion, self-learn, ship-it, start-session, submit-feedback, verified-planning (+`check_plan.py` gate), wrap-session; shared judges/lens in `_shared/agents/`, shadowing check in `_shared/scripts/`; index in `README.md` + `SKILLS-REGISTRY.yaml` (#719 skills leg).
- `hooks/sync-version-refs.sh` `OLD_VERSIONS` extended with `0.61.8` (sweep was vacuous without it).
- `framework/VERSION` bumped from `0.61.8` to `0.62.0` with mechanical pin sweep.

## [0.61.8] — 2026-09-26

### Removed — dead framework/scripts/ directory (C1 PATCH)

- Deleted `framework/scripts/generate_validation_report.sh` +
  `verify_iplan_status.sh` (#740): self-deprecated drivers of the retired
  IPLAN-VERIFY flow, zero callers repo-wide, reading a tombstoned template.
- `framework/VERSION` bumped from `0.61.7` to `0.61.8` with mechanical pin sweep.

## [0.61.7] — 2026-09-26

### Fixed — enforcement-scope pair: L011 resolver repair + L005 Type-F gap (C2 PATCH)

- `CHG-L011` reference resolution repaired (#713): nearby-heuristic globs
  `{BASE}-*.yaml/yml/md` (real documents are `EARS-01.yaml`, never files
  named `EARS.*`); with `--sdd-root` but an empty lifecycle the pool falls
  back to the root's EARS/BDD layer directories, and missing directories
  warn as unverifiable rather than erroring as false fabrications. 6 new
  unit tests total (negative control: 4 fail pre-fix, 2 are boundary pins).
- `CHG-L005` no longer passes vacuously on lifecycle-carrying flows (#733):
  IPLAN creation with zero SDD steps errors for
  upstream/midstream/design/spec/reconciliation sources; `direct` (F2 empty
  lifecycle), execution/external/feedback, and missing sources keep the
  historic pass. `AGENTS.md` gate names Seed → Module → SDD explicitly.
  3 new unit tests; no existing-test regressions.
- Catalog (`LINT_RULES.md` L005/L011 rows) and §3.14 (L005) reworded to match.
- `framework/VERSION` bumped from `0.61.6` to `0.61.7` with mechanical pin sweep.

## [0.61.6] — 2026-09-26

### Fixed — governance truthfulness batch: phantom pointers, IPLAN-VERIFY retirement, phase casing, mirror pin (C1 PATCH)

- Phantom `GOVERNANCE_RULES.md` pointers repointed at `DOC_GOVERNANCE_CORE.md`
  §3.4 (checklist heading numbered), override rows retargeted, and a
  phantom-recurrence guard added (#697). Full path-resolution scan measured
  56 dangling shorthand/consumer refs — separate cleanup, not this guard.
- `IPLAN-VERIFY-TEMPLATE.yaml` tombstoned; validation sections of
  `AI_ASSISTANT_RULES.md`, `IPLAN-TEMPLATE.yaml`, and `DOC_GOVERNANCE_CORE.md`
  retargeted to the EVAL-cycle + `bugfix`-IPLAN canon; dry-run test follows
  the Migration VERIFY rule (#698). `framework/scripts/*.sh` still cite the
  template but have no callers — left for their own stale issue.
- `CHG-L013` phase comparison case-normalized like its siblings (#714) with
  uppercase/mixed-case regression tests.
- Gate mirror re-pinned (#700 option b): `GATE-08` re-mirrored from the
  governance canon (both depths resolve the up-three link), link-authoring
  rule recorded in both READMEs, `test_gate_copies_identical` pins all 8.
- `framework/VERSION` bumped from `0.61.5` to `0.61.6` with mechanical pin sweep.

## [0.61.5] — 2026-09-26

### Fixed — lint truthfulness batch: severity fork, L014/L015 source gate, stale vendoring docstrings (C2 PATCH)

- `DOC_GOVERNANCE_CORE.md` §3.14 resynced to emitter reality (#716):
  `CHG-L004` warning → error, table extended `L006`–`L015` with verified
  severities, stale `python scripts/chg_lint.py` path fixed.
- `CHG-L014`/`L015` source gate widened (#722): `spec` (framework
  self-changes) and `reconciliation` (Type-R) join the lifecycle-carrying
  family — the guards had never fired on any archived CHG. Other sources
  still pass through; `direct`-skip pinned by tests. Catalog + `AGENTS.md`
  rows reworded to match; 3 new unit tests.
- Stale vendoring docstrings rewritten (#696): `sdd_doc_lint/__init__.py`,
  `trace_graph.py` (canonical single copy; `tools/` gone with CLEANUP-001),
  `test_repo_scripts.py` unregistration rationale (subject retired with the
  platform archive, not coming back).
- `framework/VERSION` bumped from `0.61.4` to `0.61.5` with mechanical pin sweep.

## [0.61.4] — 2026-09-26

### Fixed — lint catalog single source of truth + codes-vs-catalog guard (C1 PATCH)

- `framework/governance/LINT_RULES.md` is now the exhaustive catalog (#715):
  new `CHG-L001`–`L015` registry table (severity verified against emitter
  code), every `GOV-*` row marked **Alias of** its enforcing check or
  **Reserved**, and 18 unimplemented IDs honestly marked **Reserved**
  (`TDD-SYNC-A..E`, `EVAL-001/002/003`, `EVAL-COV-001/002/003`, `IPLAN01`,
  `REG01`, `GOV-008/009/010/013/015`). Census corrected the filed list:
  `EVAL-ID-001`/`SRC-001`/`COV-004` are emitted after all.
- New `tests/conformance/test_lint_catalog.py` guard: linter `CODES`
  registries ⊆ catalog, every catalog row grounded (emitted, aliased, or
  reserved), reserved set pinned. Header now names the real guard; the
  "vendored byte-identical by each platform" claim retired with the archive.
- `sdd_doc_lint/chg_lint.py` + `bugfix_lint.py` declare `CODES` registries
  (`CHG-L001`–`L015`, `BGF-00`–`07`); `GOVERNANCE.md`/`AGENTS.md` pointers
  repointed at the catalog (incl. new `L014`/`L015` rows).
- `framework/VERSION` bumped from `0.61.3` to `0.61.4` with mechanical pin sweep.

## [0.61.3] — 2026-09-26

### Fixed — GATE-SPEC criteria engine-agnostic; archive-tier exemption (C1 PATCH)

- GATE-SPEC rewritten engine-agnostic (#702): "both platforms re-declare
  `FRAMEWORK_SPEC_VERSION`" and "both platform owners" approval (unsatisfiable
  since the 2026-09-07 platform archive) become consumer-neutral criteria —
  spec-version pins re-declared, conformance green, maintainer + reviewers.
  Applied across the gate definition + twin, error catalog + twin, interaction
  diagram + twin, approval form + twin, CHG template + twin, both CHG READMEs,
  `framework/README.md`, governance README, gate-spec playbook, and the
  `archive/platforms` pointers in root README and `docs/PROJECT.md`.
- `tests/chg/spec_gate.py`: edits confined to `framework/archive/**` are not
  spec changes — no VERSION/CHANGELOG obligation (#725), with conformance tests.
- `framework/VERSION` bumped from `0.61.2` to `0.61.3` with mechanical pin sweep.

## [0.61.2] — 2026-09-26

### Added — Validate-before-work agent rule (C1 PATCH)

- `AI_ASSISTANT_RULES.md`: new "Issue Validation Before Work" section — re-validate picked-up issues live (open, reproducible, applicable), keep changes behavior-safe, CHG first for breaking/significant changes.
- `framework/VERSION` bumped from `0.61.1` to `0.61.2` with mechanical pin sweep.

## [0.61.1] — 2026-09-25

### Fixed — Archive VERSION snapshots cited by CHG-03/05/11 manifests (C1 PATCH)

- Ship the three missing pre-bump snapshots cited by archived manifests: `framework/archive/CHG-03/VERSION` = `0.53.3`, `framework/archive/CHG-05/VERSION` = `0.55.0`, `framework/archive/CHG-11/VERSION` = `0.60.0` (closes #721).
- `framework/VERSION` bumped from `0.61.0` to `0.61.1` with mechanical pin sweep.

## [0.61.0] — 2026-09-24

### Added — Versioned seed tier + GOV-021 AI document-control rule (CHG-11, C2 MINOR)

- Seed tier joins the SDD lifecycle: archive → rewrite → bump + `supersedes`, affected files only, frozen per version (GD-08 stays historical; GD-36 carries the update). F3 Phase 0a `seed_scope` gains `supersede` with non-empty `entries`; the review checkpoint verifies ledger re-points. F1/F2/F4/Emergency/Type-R untouched.
- BRD `seed_disposition` rows pin `seed_version`; `SEED01` fails stale pins (unpinned rows pass as before; absent seed file skips). Template carrier stays `_required: false`.
- New rule GOV-021: any AI-created/modified versioned document carries `document_control` + metadata, backfilled by the agent when missing; lifecycle-entry half enforced as CHG-L015; both CHG templates carry attribution fields.
- `framework/VERSION` bumped from `0.60.0` to `0.61.0` with mechanical pin sweep.

## [0.60.0] — 2026-09-23

### Added — Modules-first F3 extension (CHG-10, C2 MINOR)

- F3 Phase 0 splits into 0a seed_scope (record, usually no-change, never rewrite seed) + 0b module_lifecycle (archive → sync → version, affected modules only) + 0c SDD cascade, with a seed → modules review checkpoint gating SDD rewrites and IPLAN authoring. F1/F2/F4/Emergency/Type-R untouched.
- Both CHG templates carry §4A module_lifecycle + §4B seed_scope (F3-gated, `_required: false` optional); GOV-020 enforced as CHG-L014 for F3 seed/module touches.
- `framework/VERSION` bumped from `0.59.2` to `0.60.0` with mechanical pin sweep.

## [0.59.2] — 2026-09-23

### Fixed — AGENTS.md authority-flip (CHG-09, C1 PATCH)

- `AGENTS.md` header declares the single working agreement; `CLAUDE.md` deprecated (legacy detail, never authority; this file wins on conflict).
- Dropped the two self-contained CLAUDE.md pointers; closing reframed as deprecated legacy detail; worktree pointer added.
- `framework/VERSION` bumped from `0.59.1` to `0.59.2` with mechanical pin sweep.

## [0.59.1] — 2026-09-23

### Fixed — STALE P2 sweeps + T1 remedy (CHG-08, C2 PATCH)

- P2 doc sweeps D1–D6: point-in-time snapshots grandfathered with rationale, dead paths framed-or-fixed, `.github` push leg → dev, layer language unified on 09 operational namespace (#670).
- T1 remedy: 8 unrunnable `tests/unit` modules deleted (subjects archived), sync test re-anchored to `hooks/sync-version-refs.sh` — 41 tests, zero skips (#665).
- D5/D6: CHG/EVAL acceptance goldens + layer tests; linter covers CHG/EVAL (known-artifact set, section-target fallback); case-type vocabulary derived from TDD template; required-section pins extended; fixture validator delegates to the shared harness; deleted-dir path inserts removed; dead scripts retired (#670).
- `framework/VERSION` bumped from `0.59.0` to `0.59.1` with mechanical pin sweep.

## [0.59.0] — 2026-09-23

### Added — STALE P1 canons: one canonical surface per fork (CHG-08, GD-34, C2 MINOR)

- EVAL report canon REPORT + RPT tombstone + `test_results` pin + old-ID ban (#664).
- CHG template canon `governance/chg/` (KEEP §7 validation block, 8-layer enumeration, byte-identical twins, canon-home pins) (#667).
- Playbook split: 10_EVAL authoring vs 10_IPVERIFY execution; `validator.md` retargeted to EVAL-RPT; framework README folder count fixed (#672).
- MVP: 8 retired-schema templates tombstoned with pointers, 7 index skeleton links retargeted, one-template claim fixed, carrier/seed tests re-anchored (#666).
- Verification vehicle retargeted to EVAL-RPT flow + bugfix-subtype repairs; `tmp/` retired; scripts deprecated with headers (#662).
- Triple-lock one-pass EVAL/CHG rows (schema enum, naming prefixes/lifecycles, scope 1–10, traceability chain/table); File Naming general slug form + carve-outs + bugfix row (#671 #669).
- `framework/VERSION` bumped from `0.58.0` to `0.59.0` with mechanical pin sweep.

## [0.58.0] — 2026-09-23

### Fixed — STALE P0 remediation: tests, linter, hooks (CHG-08, C2 MINOR)

- `tests/unit` quarantine: red modules skip with cited issue until the delete-or-reanchor remedy (#665).
- `sdd_doc_lint/chg_lint.py` contradictions fixed (Proposed early-pass per GOV-012, L001 C3-duplicate dropped, missing-phase error, L004 canon steps-scan escalated under new GOV-019, L005 code arm folded) + L001–L005/CHG-04/CHG-05 fixtures; shared guard/loader extracted to `sdd_doc_lint/_common.py` (#668, GD-33).
- Hook gates: CHG gate watches `*.sh`, skips `*TEMPLATE*`, reads the commit message, wired into pre-commit (warn-only); docs list resynced (AGENTS.md replaces deprecated CLAUDE.md); `sync-version-refs.sh` refactored to one `OLD_VERSIONS` list + conformance pin; pre-push paths fixed; `sdd-doc-review.sh` repointed (#663).
- `framework/VERSION` bumped from `0.57.1` to `0.58.0` with mechanical pin sweep.

## [0.57.1] — 2026-09-22

### Fixed — AGENTS.md freshness post-0.57.0 (CHG-07, C1 PATCH)

- Root working agreement brought current with the 0.56.0/0.57.0 canon: dead-file
  mandates dropped (`plans/HANDOFF.md`, `ROADMAP.md`), gate exceptions corrected
  (active-IPLAN bugfixes, docs-only C1, bugfix vehicle, F2 C1-direct), SDD-first
  scoped to F1/F3, `python3` invocation, CHG-L013/GOV-018 line, flows-router pointer.
- `hooks/sync-version-refs.sh`: 0.57.0 sweep lines (E005/E008 compliance for this bump).

## [0.57.0] — 2026-09-22

### Added — GD-32: CHG request flows router (CHG-06, C2 MINOR)

- New `governance/CHG_REQUEST_FLOWS.md` (canonical): F1 greenfield, F2 direct, F3 brownfield,
  F4 bugfix vehicle, Emergency/Type-R yields, C1/IPLAN-gate ruling, GOV-018 guard.
- `DOC_GOVERNANCE_CORE.md`: §3.1.3 router kernel + §3.13 F2.2 sentence (code-touching C1
  requires C1 CHG + scoped IPLAN with covering tests).
- `LINT_RULES.md`: GOV-018 row. CHG twins: `direct` source row (GATE-CODE) + C1 bound +
  enum comments (identical — #667 fork untouched).
- `sdd_doc_lint/chg_lint.py`: CHG-L013 misclassification check + fixtures; new
  `tests/conformance/test_chg_flows_router.py` agreement test; 09_CHG READMEs gain
  the selector table; `hooks/sync-version-refs.sh` gains 0.56.0 sweep lines.

## [0.56.0] — 2026-09-22

### Added — GD-31: scoped bugfix IPLAN vehicle (CHG-05, C2 MINOR)

- `IPLAN-TEMPLATE.yaml`: `bugfix` subtype (parented repair, step order, rollback markers,
  naming + minter, no-fix-on-fix); `parent_iplan`/`source_chg` homes; bugfix section set
  (manifest, commands, handoff, traceability, rollback).
- `08_IPLAN/README.md`, `IPLAN-VERIFY-TEMPLATE.yaml`, `IPLAN-00_index.TEMPLATE.yaml`:
  terminal semantics, migration dry-run requirement, pending-`validated_by`, parent linkage.
- `DOC_GOVERNANCE_CORE.md`: §3.13 active definition + bugfix authorisation, post-completion
  pattern, post-merge VERIFY obligation, migration VERIFY rule.
- `LINT_RULES.md`: GOV-013 carve-out + `BGF-01..07` rows. `DECISIONS.md`: GD-31.
- GATE-08/GATE-CODE twins: `IPLAN/tmp/` retired, bugfix routing, migration smoke note.
  `LAYER_REGISTRY.yaml`: `tmp/` sentence resolved (no new layer, no shape change).
- New `sdd_doc_lint/bugfix_lint.py` + `test_bugfix_lint.py` + conformance contract test.

## [0.55.0] — 2026-09-21

### Added — GD-30: Type-R code-to-doc reconciliation flow (CHG-04, C2 MINOR)

- `DOC_GOVERNANCE_CORE.md`: §3.1.2 Type-R section (trigger, Phase 0–3 flow, guardrails
  incl. Emergency disambiguation — Emergency-qualifying work never uses Type-R).
- CHG twins (`governance/chg/` + `layers/09_CHG/`): `reconciliation` change_source value
  (entry GATE-CODE), Dual Lifecycle section + routing rows in READMEs, §1.3/§6.3 notes in
  `GATE-CODE_IMPLEMENTATION.md`. Docs + template enum only — no new lint rules.

## [0.54.0] — 2026-09-20

### Added — GD-29: 17 donor-hardening addons (CHG-03, C2 MINOR)

- `DOC_GOVERNANCE_CORE.md`: SDD-first implementation order (§3.1.1), §3.13 bootstrap
  exemption, IPLAN Lifecycle bundle, `## Status Propagation (§4.1)`, `WORKTREE_FLOW.md`
  pointer (twin EVAL blocks deduped; canonical `EVAL.NN.SS.xxxx` survives).
- `IPLAN-TEMPLATE.yaml`: `completion_gates` + `completion_spec_sync` blocks,
  `breaking_change` block, `audit_fix` fourth subtype, realtime-manifest + DONE-must-exist
  rules; `08_IPLAN/README.md`: `## IPLAN Subtypes`.
- `LAYER_REGISTRY.yaml` + `registry/README.md`: new-layer registration checklist;
  `LINT_RULES.md`: `REG01`, `CHG-L012`, `IPLAN01`, `TDD-SYNC-A..E` (all advisory).
- `sdd_doc_lint/chg_lint.py`: CHG-L012 completion-sync warning;
  `sdd_doc_lint/__main__.py`: SKIPPED-vs-clean warning; `.gitignore`: scoped
  governed-archive negation.
- `03_EARS/README.md`: pattern decision tree; `requirements_specialist.md`: lens note;
  `TDD-00_index` + `IPLAN-00_index` templates: TDD-SYNC-E source-of-truth notes.
- `NOTICES.md`: delegation greps, genericized Rule 5, `## Concurrency traps`, advisory
  `TDD-SYNC-A..E`; `ID_NAMING_STANDARDS.md`: red-flag box (outside digest-pinned lines);
  `SELF_LEARNING.md`: §7.4 feedback-submit contract; `AI_ASSISTANT_RULES.md`:
  delegation/concurrency pointers.
- NEW `framework/governance/WORKTREE_FLOW.md` v1.0 (generic git/gh; order guard load-bearing).
- `framework/VERSION` bumped from `0.53.3` to `0.54.0` with mechanical pin sweep.

---

## [0.53.0] — 2026-09-07

### Added

- **GD-25: `.aidoc/` redefined as project override layer.** The `.aidoc/`
  directory now holds the project profile and project-specific overrides
  (`.aidoc/project/`) instead of unused AI provenance subdirectories.
  New discovery rule: `.aidoc/project/` first, fall back to
  `.aidoc/framework/`. (`CHG-02`, GATE-SPEC, C2, minor)

### Changed

- `governance/aidoc/AIDOC.md` rewritten — new purpose, directory structure, discovery
  rule, symlink convention. Moved from `docs/AIDOC.md`.
- `README.md` four-tier model updated — "AI provenance" → "Project overrides".
- `governance/ADAPTATION.md` §10 added — project overrides contract.
- `layers/09_CHG/gates/GATE-SPEC_FRAMEWORK.md` — fixed `.aidoc/learnings.md`
  reference to `.aidoc/project/governance/SELF_LEARNING.md`.
- `framework/VERSION` bumped from `0.52.0` to `0.53.0`.

---

## [0.52.0] — 2026-09-07

### Added

- **GD-24: `document_control` for all framework governance documents.** All governance docs,
  gate definitions, layer READMEs, root-level reference docs, playbook READMEs, and YAML data
  files now carry version tracking metadata. 66 files modified, 67 originals archived to
  `archive/CHG-01/`. (`CHG-01`, GATE-SPEC, C2, minor)

### Changed

- `framework/VERSION` bumped from `0.51.0` to `0.52.0`.
- `governance/DECISIONS.md` updated with GD-24 entry.
- `registry/LAYER_REGISTRY.yaml` metadata gains `last_updated` and `framework_version`.
- `governance/ADAPTATION_SURFACE.yaml` metadata gains `last_updated` and `framework_version`.
- `governance/REVIEW_CREWS.yaml` metadata gains `last_updated` and `framework_version`.
- `governance/PROFILE-TEMPLATE.yaml` metadata gains `last_updated` and `framework_version`.

## [0.51.0] — 2026-01-20

### Added

- **GD-23: Per-document `framework_version` tracking.** Every SDD document template gains
  `metadata.framework_version` following software versioning conventions. CHG template gains
  `version_action: keep | upgrade`. GATE-SPEC gains warning check W004 for stale
  `framework_version`.

## [0.47.0] — 2026-08-29

### Added

- **GD-22: Non-C4 diagram kinds valid on every layer.** `state-*` and `flow-*` join
  `sequence-*` as diagram kinds valid on all layers. EARS and BDD gain diagram authoring slots.
- **GD-21: `total_sections` counts NUMBERED sections.** Documented the distinction between
  `total_sections` (numbered sections) and STRUCT01's derived required set (includes unnumbered
  backmatter).
- **GD-20: Carrier-aware rule dispatch.** `sdd_doc_lint` reads `LAYER_REGISTRY.yaml`
  `extensions` for instance format. Structured hash algorithm defined for YAML carrier.
- **GD-19: FR cap becomes measurable.** `FRCAP01` warning check enforces GD-14's 5-FR
  advisory cap on BRDs.

## [0.46.0] — 2026-08-28

### Added

- **GD-18: Four independent template fixes.** Derived test paths (#550), threshold carriers
  (#551), IPLAN status ownership (#569), GD-13 erratum (#532). Language-generic TDD/IPLAN
  templates, `threshold_references` carrier for SPEC/TDD.
- **GD-17: Instance format normative source.** `LAYER_REGISTRY.yaml` `extensions` is the
  single authority for instance format. Effective condition: rule-applicability parity with
  Markdown carrier.
- **GD-16: IPLAN `tdd_ref` carrier.** File-manifest entries carry `tdd_ref` field for
  element-level TDD test-case traceability.

## [0.44.0] — 2026-08-28

### Added

- **GD-15: YAML mandatory instance format.** YAML is the mandatory format and source of truth
  for layer artifacts. Markdown is optional and descriptive.

## [0.42.0] — 2026-08-25

### Added

- **GD-14: BRD 5-FR cap.** A BRD document SHOULD carry at most 5 functional requirements.
  Cycle total remains 5-15 per cycle.

## [0.41.3] — 2026-08-23

### Fixed

- **GD-13: Citation granularity reconciliation.** Six authoring surfaces reconciled to
  GD-03's element-level citation rule. Erratum, not a rule change (patch).
