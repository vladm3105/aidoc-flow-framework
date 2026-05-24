# Documentation Compatibility and Deprecation Policy

| Field | Value |
| --- | --- |
| Policy ID | DOC-COMPAT-DEPRECATION-001 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Compatibility and deprecation behavior for MCP documentation artifacts |

---

## 1. Objective

Define compatibility expectations, deprecation handling, and replacement requirements for MCP documentation artifacts.

Implementation complexity: 3/5.

---

## 2. Compatibility Model

Compatibility classes:

- read-compatible: older artifact remains accepted as historical input
- write-compatible: current workflows may emit artifact format
- non-compatible: artifact must not be produced by canonical workflows

Policy rules:

- Legacy artifacts may remain read-compatible during deprecation period.
- New canonical workflows must not emit deprecated formats.
- Canonical active artifacts must define replacement mapping for deprecated predecessors.

---

## 3. Deprecation Procedure

Required steps:

1. Register artifact in reconciliation log with status deprecate.
2. Declare replacement artifact path or explicit no-replacement rationale.
3. Add sunset date and owner.
4. Keep deprecation notice in deprecated file header until archived.
5. Archive only after sunset criteria are met.

Failure modes:

- Deprecation without replacement or rationale.
- Removal before sunset criteria.
- Canonical workflow still writes deprecated artifact format.

---

## 4. Legacy Artifact Constraints

Legacy policy alignment:

- Existing legacy report policy remains active.
- Legacy UCX report naming remains read-compatible when policy permits.
- Canonical MCP flows do not allocate new legacy report names.

---

## 5. Evidence Requirements

For each deprecation action provide:

- reconciliation log entry
- replacement mapping
- owner assignment
- sunset date
- quality gate check result

---

## 6. Resource Requirements and Constraints

- Contributors: docs-maintainer and release-approver
- Storage: negligible
- Constraint: compatibility state must be explicit and deterministic in policy and logs
