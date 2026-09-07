# Changelog

All notable changes to the AI Doc Flow Framework are documented here. Format
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed — Platforms archived, framework becomes self-sufficient (2026-09-07)

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
