# MCP Cutover and UCX_v1 Archive Policy

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 2.0 |
| Date | 2026-05-03 |
| Scope | Cutover policy for MCP canonical runtime and archival treatment of UCX_v1 references |

---

## 1. Policy Objective

Establish MCP as the canonical runtime and documentation source for active operations and restrict UCX_v1 to archival reference usage.

---

## 2. Policy Statements

1. MCP command contracts and runtime behavior are authoritative for active operations.
2. UCX_v1 documentation is archival and non-authoritative for MCP runtime behavior.
3. Runtime and operator procedures must be executable from `ucx_hermes/docs` artifacts without UCX_v1 dependencies.
4. New MCP changes must not introduce active operational dependencies on UCX_v1 references.

---

## 3. Allowed UCX_v1 References

Allowed:

- historical mapping notes
- migration record references
- archive index cross-links

Disallowed:

- active command procedures requiring UCX_v1 docs
- operational fallback instructions that depend on UCX_v1 runtime semantics

---

## 4. Release Gate Checks

Required checks:

- `rg -n "UCX_v1|UCX v1|ucx_v1|UCX" ucx_hermes/docs --glob "*.md" --glob "!ucx_hermes/docs/policies/MCP_CUTOVER_AND_UCXV1_ARCHIVE_POLICY.md"`
- documentation link validation for updated MCP docs
- command/test evidence linked in migration closure report

---

## 5. Non-Compliance Response

1. Block release readiness status.
2. Add remediation entry to migration closure report.
3. Re-run release gate checks after correction.
