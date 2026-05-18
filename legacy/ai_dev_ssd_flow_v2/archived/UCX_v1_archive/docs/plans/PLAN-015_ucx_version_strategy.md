# PLAN-015: UCX Version Strategy

**Document ID**: PLAN-015_ucx_version_strategy
**Created**: 2026-03-23
**Updated**: 2026-03-23
**Status**: Completed
**Target Version**: UCX v2.0.0
**Related Plans**: PLAN-012_prd_derived_artifact_flow.md, PLAN-014_prd_mcp_tool_namespace.md

---

## Objective

Define a single release and versioning strategy for UCX that covers:

1. How breaking changes are classified
2. Whether UCX v2.0.0 should use a separate source folder
3. How v1.x and v2.x coexist during migration
4. Which file is authoritative for the package version
5. How plans, changelogs, roadmap entries, and migration guides map to releases

---

## Decision Summary

### Primary Decision

Do **not** create a separate source folder such as `UCX.2.0.0/`.

UCX should remain a **single codebase** rooted at `UCX/`, with semantic-versioned releases managed through:

- one package name: `ucx`
- one source tree: `UCX/ucx/`
- one docs tree: `UCX/docs/`
- git tags/releases for published versions
- optional release branches only when parallel maintenance is required

### Version Boundary Decision

The PRD derived-artifact workflow becomes **UCX v2.0.0** if the release includes contract enforcement that breaks existing callers.

These changes are major-version changes when shipped without compatibility shims:

- `ucx remediate` rejects source-stage PRDs and requires `_validation` PRDs
- API remediation rejects non-`validation-fixed` PRDs
- remediation requires `*.UCX_review_report_vNNN.md` instead of accepting looser historical inputs
- PRD workflow becomes stage-aware and artifact-driven rather than source-document-driven

The MCP namespace addition itself is additive, but the workflow enforcement behind it is not.

---

## Problem Statement

UCX currently has version drift across repo surfaces:

| Source | Reported Version |
| --- | --- |
| `ucx/version.py` | `1.19.2` |
| `pyproject.toml` | `1.1.0` |
| `README.md` / `ROADMAP.md` | `1.21.7` current, `1.22.0` planned |

This means UCX does not currently have a single authoritative release version.

Separately, PLAN-012 introduced a new PRD workflow that changes runtime contracts for CLI and API users. Without a clear release strategy, the project risks shipping breaking behavior under a minor version.

---

## Why Not `UCX.2.0.0/`

Creating a versioned folder such as `UCX.2.0.0/` would create two release mechanisms at once:

1. filesystem versioning
2. semantic package versioning

That creates unnecessary duplication and drift.

### Operational Problems with a Separate Folder

| Problem | Effect |
| --- | --- |
| Duplicate source trees | Bug fixes must be copied manually between trees |
| Duplicate docs and tests | Release notes, plans, and tests diverge quickly |
| Import ambiguity | Tooling and scripts may import the wrong package tree |
| Packaging ambiguity | `pyproject.toml`, entrypoints, and build paths become harder to reason about |
| Git history fragmentation | Breaking-change history is split between folders instead of tags/branches |

### Correct Place for Version Separation

Use these mechanisms instead:

- `main` branch for the next release line
- optional `release/1.x` branch if patch support for v1.x is needed after v2.0 ships
- tags such as `v1.22.0`, `v2.0.0`
- changelog files and migration guides for release-specific behavior

---

## Release Model

UCX follows semantic versioning:

| Component | Meaning |
| --- | --- |
| **MAJOR** | Breaking CLI/API/file-format behavior |
| **MINOR** | New backward-compatible features |
| **PATCH** | Bug fixes, documentation corrections, non-breaking hardening |

### What Counts as a Breaking Change in UCX

A change is **major** if any of the following occur:

1. A previously valid CLI invocation now errors
2. A previously accepted API input now raises an exception
3. Output filenames or locations change in a way that breaks automation
4. Report schemas or metadata contracts change incompatibly
5. Default behavior changes from permissive to enforced with no compatibility path
6. Deprecated commands/flags/functions are removed

### Current Classification of the PRD Workflow Changes

| Change | Classification |
| --- | --- |
| Add `prd_*` MCP tools | Minor |
| Add `ucx validate-fix prd` | Minor |
| Add `ucx remediate-apply prd` | Minor |
| Make `ucx remediate` reject source PRDs | Major |
| Make API remediation reject source PRDs | Major |
| Require UCX review-report naming for PRD remediation | Major |
| Change automation assumptions from source PRD to `_validation` PRD | Major |

---

## Version Strategy

### Strategy A: Transitional Minor Then Major

Use this if backward compatibility for existing PRD automation is required.

#### v1.22.x

Ship additive changes only:

- add `validate-fix` and `remediate-apply`
- add `prd_*` MCP tools
- add docs and lineage metadata helpers
- keep old remediation entrypoints working
- emit deprecation warnings for source-PRD remediation usage

#### v1.23.x

Continue warnings and migration guidance:

- preserve compatibility
- add migration tooling or auto-redirect helpers where possible
- update examples to the new workflow only

#### v2.0.0 Compatibility Removal

Remove legacy compatibility:

- enforce `_validation` PRD input for remediation
- enforce UCX review report contract
- remove legacy PRD remediation assumptions
- publish migration guide and explicit breaking-change release notes

### Strategy B: Direct Major Release

Use this if the current implementation is intended to ship as-is.

#### v2.0.0

Ship the PRD workflow contract directly as the new baseline:

- immutable source PRD model
- `_validation` required for PRD review/remediation flow
- stage-aware artifact contract
- PRD MCP namespace as the first layer-specific agent surface

This is the recommended path if the existing enforcement changes remain in place.

---

## Recommended Path

### Recommendation

Treat the current PRD workflow enforcement work as **v2.0.0 scope**, not `v1.22.0`, unless compatibility shims are added first.

Reasoning:

- the current CLI/API behavior already rejects previously valid inputs
- the repo already documents that major version bumps are the place for removals and breaking behavior
- forcing these changes into `v1.22.0` would violate UCX's own semver policy

### Release Line Recommendation

| Release | Purpose |
| --- | --- |
| `v1.21.x` | Current stable line |
| `v1.22.x` | Optional compatibility/minor bridge only if legacy PRD remediation behavior is preserved |
| `v2.0.0` | First release that enforces PLAN-012 PRD workflow contract |

---

## Repository Structure Strategy

### Keep

```text
UCX/
  pyproject.toml
  README.md
  docs/
  ucx/
```

### Do Not Add

```text
UCX.2.0.0/
UCX_v2/
UCX-next/
```

### If Parallel Maintenance Is Needed

Use git branches, not folders:

- `main` → next active release line
- `release/1.x` → patch-only maintenance for v1.x after v2 ships
- `release/2.x` → optional if later needed

---

## Source of Truth for Version Number

UCX needs one authoritative version source.

### Current Problem

The version is duplicated and inconsistent across:

- `ucx/version.py`
- `pyproject.toml`
- `README.md`
- `docs/ROADMAP.md`
- changelog filenames

### Decision

Use **one runtime/package source of truth** and generate or sync the rest from it.

### Recommended Authority

Authoritative version file:

- `UCX/ucx/version.py`

Derived/synchronized surfaces:

- `pyproject.toml`
- `README.md`
- `docs/ROADMAP.md`
- `docs/CHANGELOG/CHANGELOG_vX.Y.Z.md`

### Required Follow-Up

1. Align `pyproject.toml` with `ucx/version.py`
2. Align `ucx/version.py` with the actual current release line
3. Add a release checklist that updates README, ROADMAP, and changelog references from the authoritative version

---

## Documentation Release Contract

Each release must update the following artifacts:

| Artifact | Purpose |
| --- | --- |
| `docs/plans/PLAN-NNN_*.md` | Design and scope before implementation |
| `docs/CHANGELOG/CHANGELOG_vX.Y.Z.md` | Release contents |
| `docs/ROADMAP.md` | Current, next minor, next major |
| `README.md` | Public version summary |
| `docs/MIGRATION_v2.md` | Required for the next major release |

### Major Release Requirements

For `v2.0.0`, do all of the following:

1. Add `docs/MIGRATION_v2.md`
2. Add explicit `Breaking Changes` section to `CHANGELOG_v2.0.0.md`
3. Keep deprecation tables in docs until removal is complete
4. Update all CLI/API examples to the new baseline
5. Document legacy-to-new command mapping

---

## Migration Contract for PLAN-012 / PLAN-014

If UCX v2.0.0 ships the current PRD workflow, the migration guide must document:

| Legacy Behavior (v1.x) | New Behavior (v2.0.0) |
| --- | --- |
| `ucx remediate <source-prd>` may be used directly | `ucx remediate` requires `_validation` PRD |
| report selection may be looser | PRD remediation requires `*.UCX_review_report_vNNN.md` |
| generic MCP tools only | PRD-agent uses `prd_*` namespace |
| automation may infer paths ad hoc | tools return `output_path` and `next_step` explicitly |

### CLI Migration Pattern

```text
v1.x:
  ucx validate prd PRD-01.md
  ucx review prd PRD-01.md
  ucx remediate PRD-01.md --report review.md

v2.0.0:
  ucx validate prd PRD-01.md
  ucx validate-fix prd PRD-01.md --report PRD-01_validation_report.md
  ucx review prd PRD-01_validation.md
  ucx remediate PRD-01_validation.md --report PRD-01_validation.UCX_review_report_v001.md
  ucx remediate-apply prd PRD-01_validation.md --report PRD-01_validation.UCX_remediation_report_v001.md
```

---

## Acceptance Criteria

### Strategic

- UCX v2.0.0 uses the existing `UCX/` root, not a parallel versioned folder
- Breaking workflow-enforcement changes are not released under a minor version unless compatibility is restored
- Version authority is defined explicitly
- The roadmap and future release documents align to this strategy

### Operational

- A migration guide is required before `v2.0.0` release
- Release branches are used only for parallel maintenance, not for architectural versioning
- The package version is synchronized across runtime, packaging, and documentation surfaces

---

## Immediate Follow-Up Actions

1. Reclassify PLAN-012 workflow enforcement scope to `v2.0.0` unless compatibility shims are added
2. Fix current version drift across `version.py`, `pyproject.toml`, and docs
3. Create `docs/MIGRATION_v2.md`
4. Add a release checklist for version synchronization and changelog generation

---

## Revision History

| Version | Date | Author | Changes Made |
| --- | --- | --- | --- |
| 0.1.0 | 2026-03-23 | UCX Framework | Initial version strategy: no parallel source folder, semver classification, v2.0.0 recommendation for breaking PRD workflow enforcement |
