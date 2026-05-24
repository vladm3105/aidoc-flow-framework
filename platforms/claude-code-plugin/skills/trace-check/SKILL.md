---
name: trace-check
description: Validate bidirectional traceability across the 8-layer SDD flow - link resolution, ID format, cumulative tagging, coverage, and orphan detection - and optionally repair broken links. Use before committing or auditing SDD documentation.
metadata:
  tags:
    - sdd-workflow
    - utility
    - quality-assurance
  custom_fields:
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: []
    version: "0.2.0"
    framework_spec_version: "0.3.1"
    last_updated: "2026-05-23"
    adapts: [active_layers]
---

# trace-check

## Purpose

Validate traceability across all SDD artifacts (BRD → PRD → EARS → BDD → ADR →
SPEC → TDD → IPLAN → Code) and report — or optionally repair — gaps. It checks
bidirectional link symmetry, ID-format compliance, cumulative tagging, link and
anchor resolution, coverage, and orphans. The framework ships no runtime code:
**this skill IS the checker**, applying the declarative checks below against the
governance spec.

## When to Use

Use `trace-check` when:

- Before committing documentation changes, or after creating/updating artifacts.
- Running a periodic audit (sprint/release) of traceability completeness.
- Verifying ID-format or cumulative-tag compliance, or detecting orphans.

Do **not** use it for code-implementation review, non-SDD documentation, or
in-creation single-document feedback (use `../quality-advisor/SKILL.md`).

## Behavior

Given a `project_root` (default `{project_root}/docs/`) and optional
`artifact_types`, `strictness_level` (permissive / strict (default) / pedantic),
`auto_fix`, and `report_format` (markdown / json / text):

1. **Discover artifacts** — scan `docs/<NN>_<X>/` (01_BRD … 08_IPLAN), parse
   document IDs from filenames, build an ID → path inventory, flag duplicate IDs
   and non-conformant `docs/<NN>_<X>/` structure.
2. **Parse traceability** — read each artifact's Traceability section and the
   `@brd:`…`@iplan:`/`@impl-status:` tags in docs and code into a bidirectional
   upstream/downstream graph.
3. **Validate ID format** — document refs `TYPE-NN`; element refs 4-segment
   `TYPE.NN.SS.xxxx`; two-digit zero-padding; valid TYPE; no collisions. Reject
   legacy 3-segment IDs and placeholders (TBD/XXX/NNN).
4. **Validate cumulative tagging** — confirm each artifact carries exactly the
   upstream tag families its layer requires (BRD 0 → … → IPLAN 7) per the
   `can_reference` set in `framework/registry/LAYER_REGISTRY.yaml`; report gaps
   and any downstream-tag leakage.
5. **Resolve links** — confirm every markdown link path and `#anchor` resolves
   (markdown H1, YAML `id:`, feature `Scenario:`).
6. **Check bidirectional consistency** — for each A→B link verify B→A exists;
   score `(matched pairs / total) × 100` (target ≥ 95%).
7. **Compute coverage and orphans** — upstream is required for every artifact
   except BRD; downstream is optional; flag mid-chain artifacts with no
   downstream and unexpected orphans.
8. **Report** — summary (pass/fail, coverage %, consistency %), broken links
   with file:line, missing-traceability and bidirectional gaps, orphans,
   coverage-by-type table, and prioritized fixes.

**Auto-fix (`auto_fix: true`)**: create a timestamped backup first, then repair
relative paths, add missing downstream references, and log changes to revision
history; provide a rollback command. Never invent placeholder IDs.

**Quality gates**: 100% link resolution and ID compliance, ≥ 95% bidirectional
consistency, no orphaned mid-chain artifacts, Traceability section present on
every artifact.

## Adaptation

Before checking references, read the project adaptation profile
(`.aidoc/profile.yaml`). Honor `active_layers`: treat a disabled skippable
layer as absent by design — do not report a missing reference to it (apply
the cascade rule). Ignore any unknown or out-of-surface key.
Authority: `framework/governance/ADAPTATION.md`.

## Related Resources

- Traceability & cumulative tagging: `framework/governance/TRACEABILITY.md`
- ID & tag standards: `framework/governance/ID_NAMING_STANDARDS.md`
- Layer registry (`can_reference`/`downstream`):
  `framework/registry/LAYER_REGISTRY.yaml`
- Governance core: `framework/governance/DOC_GOVERNANCE_CORE.md`
- Related skills: `../doc-flow/SKILL.md` · `../adr-roadmap/SKILL.md` ·
  `../quality-advisor/SKILL.md` · `../context-analyzer/SKILL.md`
