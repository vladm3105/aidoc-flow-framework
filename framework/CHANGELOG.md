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
| Framework Version | 0.55.0 |

---

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
