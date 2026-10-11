# Plan: Standardized Dual-Template Selection Guides Across Layers 01–08 and Governance (CHG-90, GD-77)

## Document Control

| Field | Value |
|---|---|
| Version | 1.0 |
| Status | Ready |
| Last Updated | 2026-10-11 |
| Author | Framework Architect |
| Framework Version | 0.91.9 |
| Authority | [Decision GD-77](../framework/governance/DECISIONS.md#gd-77) & [CHG-90](../framework/archive/CHG-90/CHG-90.yaml) |

## Problem Statement

The framework maintains dual-template support across Layers 01–08 and Governance (Layer 09 CHG):

- `*-SWF-TEMPLATE.yaml` — **Primary Standard** (machine-executable CNCF Serverless Workflow DSL v0.8 wrapped in SDD Hybrid Envelope).
- `*-TEMPLATE.yaml` — **Companion Standard** (static, linear declarative requirements and specifications).

While the dual-template selection matrix is documented in layer READMEs and governance decisions (GD-61, GD-73), the template files themselves lacked in-file selection guidance in their comment headers. Consequently, AI agents and engineers authoring new artifacts had to consult external docs to decide between the primary SWF template and the static companion template.

## Scope of Work

1. Author Change Request `framework/archive/CHG-90/CHG-90.yaml` and Implementation Plan `framework/archive/CHG-90/IPLAN-90.yaml`.
2. Add tailored, unambiguous `TEMPLATE SELECTION GUIDE` comment blocks directly into the file headers of:
   - Layer 01: `BRD-SWF-TEMPLATE.yaml` & `BRD-TEMPLATE.yaml`
   - Layer 02: `PRD-SWF-TEMPLATE.yaml` & `PRD-TEMPLATE.yaml`
   - Layer 03: `EARS-SWF-TEMPLATE.yaml` & `EARS-TEMPLATE.yaml`
   - Layer 04: `BDD-SWF-TEMPLATE.yaml` & `BDD-TEMPLATE.yaml`
   - Layer 05: `ADR-SWF-TEMPLATE.yaml` & `ADR-TEMPLATE.yaml`
   - Layer 06: `SPEC-SWF-TEMPLATE.yaml` & `SPEC-TEMPLATE.yaml`
   - Layer 07: `TDD-SWF-TEMPLATE.yaml` & `TDD-TEMPLATE.yaml`
   - Layer 08: `IPLAN-SWF-TEMPLATE.yaml` & `IPLAN-TEMPLATE.yaml`
   - Layer 09 / Governance: `CHG-SWF-TEMPLATE.yaml`, `governance/chg/CHG-TEMPLATE.yaml`, and `layers/09_CHG/CHG-TEMPLATE.yaml`.
3. Ratify Decision **GD-77** (`DEC-CHG-90`) in `framework/governance/DECISIONS.md`.
4. Bump framework specification version to **0.91.9**, record in `framework/CHANGELOG.md`, update `hooks/sync-version-refs.sh`, and synchronize version references.
5. Validate all conformance tests (`pytest tests/conformance/`), `chg_lint.py`, and `swf_lint.py`.

## Out of Scope

- Modifying existing YAML keys or schema rules (`STRUCT01`, `TAG01`).
- Retiring `*-TEMPLATE.yaml` (companion templates are explicitly preserved under dual-template discipline).
- Introducing new workflow linters or changing existing DSL rules.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Decision GD-77 ratifies in-file selection guides across Layers 01-08 and Governance | GD-77 | framework/governance/DECISIONS.md:26 |
| 2 | Authorizing Change Request CHG-90 governs dual-template guidance additions | CHG-90 | framework/archive/CHG-90/CHG-90.yaml:30 |
| 3 | BRD primary template carries CNCF SWF selection guide | TEMPLATE SELECTION GUIDE: | framework/layers/01_BRD/BRD-SWF-TEMPLATE.yaml:13 |
| 4 | BRD companion template carries static linear selection guide | TEMPLATE SELECTION GUIDE: | framework/layers/01_BRD/BRD-TEMPLATE.yaml:8 |
| 5 | Version hook tracks 0.91.8 for mechanical version fanout | 0.91.8 | hooks/sync-version-refs.sh:128 |

## Review log

### Pass 1: 2026-10-11T19:46:00Z - independent

- **Reviewer**: Architect & Spec Auditor
- **Findings**:
  1. *Header consistency*: Ensure the selection comment block clearly specifies both when to use *this* template and when to use the *companion* template, creating a bidirectional cross-reference in every template pair.
  2. *Domain specificity*: A generic copy-paste comment across all 18 files would miss layer-specific value. Each layer's guide should name layer-specific characteristics (e.g. BRD value stream graphs vs linear business objectives; ADR candidate MCDA trees vs single ADRs; SPEC distributed choreography vs atomic component specs; IPLAN executable task DAGs vs linear checklist).
  3. *Byte-identical requirement*: `framework/governance/chg/CHG-TEMPLATE.yaml` and `framework/layers/09_CHG/CHG-TEMPLATE.yaml` must remain byte-identical per CHG-08 #667.
- **Resolution**:
  - Implemented bidirectional selection guidance tailored to each layer's concrete domain primitives.
  - Kept both CHG-TEMPLATE copies strictly synchronized.

### Pass 2: 2026-10-11T19:47:00Z - independent

- **Reviewer**: QA Lead & Governance Officer
- **Findings**:
  1. *Linter safety check*: Verify that adding YAML comment headers does not affect `sdd_doc_lint` line-parsing or `swf_lint` root node validation.
  2. *Version fanout check*: Verify that `0.91.8` is added to `OLD_VERSIONS` in `hooks/sync-version-refs.sh` to pass `test_sync_version_refs.py`.
- **Resolution**:
  - Confirmed YAML comments are completely ignored by AST parsers and `sdd_doc_lint` regex scanners.
  - Added `0.91.8` to `OLD_VERSIONS` ahead of version synchronization.
  - **Result:** ready, no new findings.
