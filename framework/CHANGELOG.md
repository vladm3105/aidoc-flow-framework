# Changelog — SDD Framework

All notable changes to the shared engine-agnostic specification are documented here.
This file is the project's document-of-record for spec changes (GATE-SPEC-E008).

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-07 |
| Author | Framework Maintainer |
| Framework Version | 0.60.0 |

---

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
