# Plan: Modernize ADR-00_index to YAML with Embedded Technology Stack & Security Registry

## Metadata

| Field | Value |
| --- | --- |
| Author | Framework Maintainer |
| Authority | Decision GD-73, Layer 05 ADR Technology Selection Gate |
| Framework Version | 0.91.5 |
| Target Version | 0.91.6 |
| Date | 2026-10-11 |
| Status | Proposed |

## Objective

Modernize the Layer 05 Architecture Decision Record index template from Markdown (`ADR-00_index.TEMPLATE.md`) to a unified, agent-readable YAML specification (`ADR-00_index.TEMPLATE.yaml`), mirroring the YAML index pattern established in Layer 08 (`IPLAN-00_index.TEMPLATE.yaml`).

Establish a canonical, machine-validatable **Project Technology Stack & Security Monitoring Registry** directly within `ADR-00_index.TEMPLATE.yaml` to serve as the project's single source of truth for:

1. Architecture decision cataloging and lifecycle tracking (`adrs`).
2. Adopted technology inventory (`technologies`) with explicit domain mapping, stack tier classification, version constraints, and authorizing ADR references.
3. Automated security monitoring attributes (Software Composition Analysis / SCA, Package URLs / PURLs, Common Platform Enumerations / CPEs, vulnerability scanning thresholds).
4. Automated tool update policies (Dependabot / Renovate cadences, patch auto-merge rules, manifest bindings).

## Scope

In scope:

- Replace `framework/layers/05_ADR/ADR-00_index.TEMPLATE.md` with `framework/layers/05_ADR/ADR-00_index.TEMPLATE.yaml`.
- Define declarative YAML schemas for `adrs`, `backlog`, `technologies`, and `update_triggers`.
- Update `framework/layers/05_ADR/README.md` to reference `ADR-00_index.TEMPLATE.yaml`.
- Update `framework/layers/05_ADR/ADR_WORKFLOW_STANDARD.md` and `framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md` to reference the unified YAML index as the canonical project technology registry.
- Ratify Decision `GD-74` (DEC-CHG-87) in `framework/governance/DECISIONS.md`.
- Author authorizing change vehicle: `CHG-87.yaml` and `IPLAN-87.yaml` in `framework/archive/CHG-87/`.
- Advance framework spec version to `0.91.6` via `hooks/sync-version-refs.sh`.
- Validate with `sdd_doc_lint`, `test_index_template_lint.py`, `chg_lint.py`, and full test suites.

Out of scope:

- Adding standalone technology registries in other layers (Layer 05 remains the single selection gate).
- Modifying other layer index templates (Layers 01–04, 06, 07, 09, 10).

## Proposed Design for ADR-00_index.TEMPLATE.yaml

The unified index template provides four core YAML blocks:

```yaml
metadata:
  schema_version: "1.0"
  framework_version: "[X.Y.Z]"
  document_type: "adr-registry"
  artifact_type: "ADR-INDEX"
  layer: 5
  total_adrs: 0
  total_technologies: 0
  last_updated: "YYYY-MM-DD"

adrs: []          # Catalog of active/proposed/deprecated ADRs
backlog: []       # Backlog of upcoming architecture decisions
technologies: []  # Active technology stack inventory with security & update policies
update_triggers:  # Standard rules when to update the index
```

Each entry in `technologies` carries:

- `id`: Unique component slug (e.g., `postgres-db`, `nats-messaging`).
- `technology`: Canonical technology name.
- `category`: Architectural domain (`Runtime`, `Data Architecture`, `Event Messaging`, etc.).
- `stack_tier`: Enterprise stack classification (`Tier-0-Core`, `Approved-Contained`, `Specialized-Domain`, `Approved-Exception`).
- `version_constraint`: SemVer constraint expression.
- `authorizing_decision`: Direct citation to Layer 05 ADR or enterprise baseline decision (`ADR-XX`, `GD-XX`).
- `security_monitoring`:
  - `enabled`: boolean.
  - `purl`: Package URL standard identifier (`pkg:docker/...`, `pkg:golang/...`).
  - `cpe`: Common Platform Enumeration identifier.
  - `ecosystem`: Package/container ecosystem.
  - `vulnerability_scanners`: Scanners targeting this component (`trivy`, `osv`, `dependabot`).
  - `severity_alert_threshold`: Maximum tolerated CVE severity before build breakage (`CRITICAL`, `HIGH`).
  - `license`: Software license string.
  - `license_approved`: boolean.
- `update_policy`:
  - `tool`: Automated updater (`renovate`, `dependabot`, `manual`).
  - `cadence`: Review frequency (`weekly`, `monthly`, `quarterly`).
  - `auto_merge_patches`: boolean.
  - `manifest_path`: Lockfile / deployment manifest tracking the dependency.
- `lifecycle_status`: Status (`Active`, `Evaluating`, `Deprecated`, `Sunset`).

## Execution Phases

### Phase 1: Authoring ADR-00_index.TEMPLATE.yaml & Retiring Markdown Template

1. Create `framework/layers/05_ADR/ADR-00_index.TEMPLATE.yaml` with metadata, `adrs`, `backlog`, `technologies`, and `update_triggers`.
2. Remove `framework/layers/05_ADR/ADR-00_index.TEMPLATE.md`.
3. Verify `tests/conformance/test_index_template_lint.py` discovers exactly 10 index templates and lints clean.

### Phase 2: Standards & Documentation Synchronization

1. Update `framework/layers/05_ADR/README.md` file table and dual-template architecture section.
2. Update `framework/layers/05_ADR/ADR_WORKFLOW_STANDARD.md` with explicit instructions for registering accepted ADR technologies in `ADR-00_index.yaml`.
3. Update `framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md` §3 to cite `ADR-00_index.yaml` as the project-level technology stack registry.

### Phase 3: Change Control, Decision Ratification & Version Bump

1. Ratify Decision `GD-74` in `framework/governance/DECISIONS.md`.
2. Create `framework/archive/CHG-87/CHG-87.yaml` and `framework/archive/CHG-87/IPLAN-87.yaml`.
3. Bump `framework/VERSION` to `0.91.6` and update `framework/CHANGELOG.md`.
4. Update `OLD_VERSIONS` in `hooks/sync-version-refs.sh` and run version fanout.

### Phase 4: Verification Battery

1. Run `python3 sdd_doc_lint/chg_lint.py framework/archive/CHG-87/CHG-87.yaml`.
2. Run `pytest tests/conformance/test_index_template_lint.py`.
3. Run `python3 -m sdd_doc_lint.swf_lint framework/`.
4. Run full test suites (`pytest tests/conformance/`, `pytest tests/acceptance/`).

## Claim ledger

| # | Claim | Symbol | Citation |
|---|---|---|---|
| 1 | Index template discovery matches `<TYPE>-00_index.TEMPLATE.*` | `_index_templates` | tests/conformance/test_index_template_lint.py:32 |
| 2 | Index template test asserts exactly 10 templates exist | `test_all_ten_index_templates_present` | tests/conformance/test_index_template_lint.py:41 |
| 3 | Index templates are exempt from STRUCT01 and -INDEX ID02 | `test_index_templates_emit_no_struct01_or_index_id02` | tests/conformance/test_index_template_lint.py:49 |
| 4 | ADR README lists ADR-00_index.TEMPLATE.md in files table | `ADR-00_index.TEMPLATE.md` | framework/layers/05_ADR/README.md:46 |
| 5 | IPLAN YAML index establishes the metadata structure for YAML index templates | `metadata` | framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml:15 |
| 6 | Index filename regex recognizes any `TYPE-00_index` file in `sdd_doc_lint` | `_INDEX_FILENAME` | `sdd_doc_lint/__init__.py:1612` |
| 7 | Index doc exemption recognizes `artifact_type` ending with -INDEX | `_is_index_doc` | `sdd_doc_lint/__init__.py:1615` |
| 8 | Progressive Refinement Model established across architectural tiers | `Progressive Refinement Model` | framework/governance/TECHNOLOGY_STACK_USAGE_GUIDE.md:30 |
| 9 | Layer 05 ADR is formalized as the Technology Selection Gate | `Technology Selection Gate` | framework/layers/05_ADR/ADR_WORKFLOW_STANDARD.md:21 |
| 10 | Decision GD-73 ratified enterprise approved technology stack governance | `GD-73` | framework/governance/DECISIONS.md:26 |

## Review log

### Pass 1 - 2026-10-11T16:50:00Z - independent

Reviewer: Spec Auditor (Subagent)

Findings:

1. Gaps: Verified that `_index_templates` in `test_index_template_lint.py` relies on globbing `layers/0*/[A-Z]*-00_index.TEMPLATE.*`, which naturally supports `.yaml` extension alongside `.md`.
2. Linter compatibility: Confirmed that `sdd_doc_lint._is_index_doc` parses both `.md` and `.yaml` filename patterns starting with uppercase letters followed by `-00_index`, ensuring `STRUCT01` exemption remains active.
3. Single Source of Truth: Confirmed removing `ADR-00_index.TEMPLATE.md` prevents duplicate index templates and maintains total template count of 10.

Resolution: All citations verified against source tree. 0 open findings.

### Pass 2 - 2026-10-11T16:52:00Z - independent

Reviewer: Lead Architect (Subagent)

Findings:

1. Schema verification: Ensure the `technologies` mapping includes both security monitoring (PURL, CPE, severity alert threshold) and automated update policies (updater tool, cadence, patch auto-merge) to satisfy all user requirements.
2. Workflow Standard integration: Confirmed `ADR_WORKFLOW_STANDARD.md` will document updating `ADR-00_index.yaml` upon ADR ratification.

Resolution: Incorporated complete schema into plan specification. 0 open findings.

**Result:** ready
