# Documentation Lifecycle and Versioning Policy

| Field | Value |
| --- | --- |
| Policy ID | DOC-LIFECYCLE-POLICY-001 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | MCP documentation lifecycle, version changes, and update triggers |

---

## 1. Objective

Define mandatory lifecycle states, versioning rules, and update triggers for MCP documentation artifacts.

Implementation complexity: 3/5.

---

## 2. Lifecycle States

Allowed lifecycle states:
- draft
- active
- deprecated
- archived

State transition rules:
- draft to active requires quality gate PASS.
- active to deprecated requires replacement reference or explicit no-replacement rationale.
- deprecated to archived requires deprecation window completion and final reconciliation entry.

---

## 3. Versioning Rules

Version increments:
- patch: typo, formatting, non-normative clarifications with no contract impact
- minor: added sections, added examples, expanded validation guidance without breaking contract
- major: normative rule change, precedence change, compatibility behavior change, or gate behavior change

Required update behavior:
- Every version increment must update revision history in the artifact.
- Major version changes must include a compatibility note and migration note.

---

## 4. Mandatory Review Triggers

A documentation review is required when changes affect:
- mcp_ucx/src/mcp_server/cli/main.py (CLI surface contract)
- mcp_ucx/src/mcp_server/prompts/context_builder.py (source mapping and prompt assembly contracts)
- mcp_ucx/src/mcp_server/review/runner.py (artifact emission and run result contracts)
- mcp_ucx/src/mcp_server/skills/project_ucx_loader.py (project asset loading and missing-asset behavior)
- prompt artifact schema or sidecar output structure

---

## 5. Compatibility and Deprecation Constraints

Mandatory constraints:
- Deprecated artifacts must remain readable during deprecation period when policy requires compatibility.
- New canonical artifacts must not silently change semantics of existing active docs.
- Deprecation entry must specify start date, planned sunset date, and replacement artifact.

Failure modes:
- Contract-impacting change published as patch.
- Deprecated artifact removed without replacement or rationale.
- Runtime behavior changes with no triggered doc update.

---

## 6. Evidence Requirements

Required evidence for lifecycle compliance:
- Updated revision history entries
- Reconciliation log update in DOC-RECONCILIATION-LOG-001
- Coverage matrix update in DOC-COVERAGE-MATRIX-001
- Compliance report update in COMPLIANCE-REPORT-002 when gates are re-evaluated

---

## 7. Resource Requirements and Constraints

- Contributors: docs-maintainer plus runtime-maintainer reviewer
- Storage: negligible
- Constraint: lifecycle status and version must remain machine-parseable and deterministic
