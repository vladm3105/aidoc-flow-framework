# UCX — Unified Context Framework

> **Aliases**: `ucx`, `mcp_sdd`, `sdd-lifecycle`. Package directory: `mcp_sdd/`. The legacy `UCX_v1` archive is a historical predecessor, not the current system.

| Field | Value |
| --- | --- |
| Canonical Name | UCX (Unified Context Framework) |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-26 |
| Scope | UCX as canonical SDD unified-context runtime and documentation framework |

---

## 1. Purpose

Define MCP as the canonical runtime, contract, and documentation surface for SSD unified-context operations.

Implementation complexity: 3/5.

---

## 2. Framework Boundaries

In scope:

- deterministic CLI orchestration for create, review, validate, validate-fix, remediate, remediate-fix, prescreen, scan, and scoring
- project-local asset loading from `UCX`
- schema-governed JSON/TXT artifact generation under `.ucx/<stage>`
- operator runbook and policy controls under `mcp/docs`

Out of scope:

- autopilot orchestration loops
- non-deterministic automatic content rewriting of source files
- legacy archive runtime dependencies

---

## 3. Canonical Runtime Surface

Primary command groups:

- create: `create-build`
- review: `review-build`, `review`
- validate: `validate`, `validate-fix`
- remediation: `remediate`, `remediate-fix`
- diagnostics: `prescreen`, `scan`, `scoring`

Primary implementation paths:

- `mcp_sdd/src/mcp_server/cli/main.py`
- `mcp_sdd/src/mcp_server/review/runner.py`
- `mcp_sdd/src/mcp_server/validation/runner.py`
- `mcp_sdd/src/mcp_server/remediation/runner.py`
- `mcp_sdd/src/mcp_server/prescreening/runner.py`
- `mcp_sdd/src/mcp_server/scan/runner.py`
- `mcp_sdd/src/mcp_server/scoring/runner.py`

---

## 4. Contract Rules

1. Command behavior must be deterministic for identical inputs.
2. Source-protected fix flow is the default behavior.
3. Output artifact locations use `.ucx/<stage>` conventions.
4. Test-backed command behavior is required for release acceptance.
5. Documentation must track runtime behavior in the same change set.

---

## 5. Failure Modes

| Failure Mode | Detection | Required Response |
| --- | --- | --- |
| Missing project assets | loader validation | fail command with actionable path guidance |
| Invalid payload shape | parse/contract stage | fail command with deterministic error output |
| Required schema violations | validation stage | non-zero validation result with report artifacts |
| Output write failure | artifact write stage | fail command with I/O error |

---

## 6. References

- `mcp_sdd/docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`
- `mcp_sdd/docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- `mcp_sdd/docs/specs/SPEC-008_mcp_output_schema_contracts.md`
- `mcp_sdd/docs/policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md`
