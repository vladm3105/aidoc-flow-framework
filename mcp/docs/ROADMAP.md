# MCP Roadmap

## Overview

This roadmap defines planned documentation and governance milestones for MCP documentation under mcp/docs.

| Field | Value |
| --- | --- |
| Current Version | 1.0.0 |
| Latest Release | 1.0.0 (L0-L9 documentation coverage and IPLAN-002 closure) |
| Next Minor | 1.1.0 (automation and continuous verification baseline) |
| Next Major | 2.0.0 (contract governance expansion and release-gate hardening) |
| Timezone | America/New_York |

Versioning policy reference:
- policies/DOC_LIFECYCLE_AND_VERSIONING_POLICY.md

---

## Version Timeline

v1.0.0 (Current) -> v1.1.0 -> v1.2.0 -> v2.0.0

---

## Planned Releases

### v1.1.0 - Automation Baseline and Drift Detection

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | Documentation automation and repeatable verification |

Planned scope:
- Add scriptable internal-link integrity verification for mcp/docs artifacts.
- Add repeatable CLI contract parity checks between CLI docs and argparse definitions.
- Standardize evidence collection workflow updates for coverage and compliance reports.
- Add roadmap/changelog cross-reference requirements for future releases.

Acceptance targets:
- Deterministic verification commands documented and executable by maintainers.
- Compliance report updates use repeatable evidence outputs.
- No change to runtime behavior.

---

### v1.2.0 - Operational Readiness and Governance Refinement

| Field | Value |
| --- | --- |
| Status | Planned |
| Type | Minor |
| Scope | Release operations and documentation governance consistency |

Planned scope:
- Refine release-gate checklist for documentation-only versus runtime-impacting changes.
- Expand operator runbook scenarios for failure-mode and recovery coverage.
- Add explicit ownership mapping updates for all active artifacts.
- Align reconciliation and coverage artifacts to a single periodic review cadence.

Acceptance targets:
- Release-gate documentation distinguishes mandatory and conditional checks.
- Runbook includes complete scenario outcome expectations.
- Ownership map is complete for active MCP docs artifacts.

---

### v2.0.0 - Governance Expansion and Hard Enforcement

| Field | Value |
| --- | --- |
| Status | Future |
| Type | Major |
| Scope | Contract-governance expansion and strict release enforcement |

Planned scope:
- Introduce stronger contract-governance rules for documentation updates tied to runtime module changes.
- Define stricter evidence requirements for release readiness with explicit blocker categories.
- Consolidate policy and compliance artifacts into a normalized release reporting model.

Potential breaking considerations:
- Stronger mandatory gate enforcement may require process updates for documentation maintainers.
- Release checklist format changes may require downstream automation updates.

---

## Completed Releases

### v1.0.0 (2026-03-24)

| Field | Value |
| --- | --- |
| Status | Released |
| Type | Major |
| Summary | Initial MCP documentation program baseline |

Delivered:
- L0-L9 artifacts for architecture, specs, policies, runbook, and traceability.
- Reconciliation log and coverage matrix with PASS status.
- Compliance report updates and plan closure evidence for IPLAN-002.
- Initial changelog release record in CHANGELOG/CHANGELOG_v1.0.0.md.

References:
- plans/IPLAN-002_mcp_docs_full_layer_coverage.md
- plans/COMPLIANCE-REPORT-002_mcp_docs_layer_coverage.md
- CHANGELOG/CHANGELOG_v1.0.0.md

---

## Constraints

- This roadmap covers documentation scope under mcp/docs.
- Runtime feature changes are out of scope unless separately approved and tracked.
- Release sequencing can change based on reconciliation outcomes and policy updates.