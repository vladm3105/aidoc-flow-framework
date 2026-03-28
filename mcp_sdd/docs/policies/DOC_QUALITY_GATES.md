# Documentation Quality Gates

| Field | Value |
| --- | --- |
| Policy ID | DOC-QUALITY-GATES-001 |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | Release-blocking quality gates for MCP documentation |

---

## 1. Objective

Define mandatory and enforceable quality gates for documentation release readiness.

Implementation complexity: 4/5.

---

## 2. Gate Ownership Model

| Role | Responsibility |
| --- | --- |
| docs-maintainer | Execute documentation checks and update reconciliation evidence |
| runtime-maintainer | Verify documentation statements against implemented runtime behavior |
| release-approver | Validate gate outcomes and authorize release gate pass |

---

## 3. Enforcement Points

- Pull request enforcement:
  - Required when files under mcp_sdd/src/mcp_server affecting CLI, prompt assembly, review runner, or project loader are changed.
- Release enforcement:
  - Required before release tag or release cutover decision for MCP documentation scope.

---

## 4. Mandatory Gates

| Gate ID | Gate Name | Blocking Rule | Evidence Artifact |
| --- | --- | --- | --- |
| GATE-01 | Coverage completeness | Any layer L0-L9 not PASS blocks release | DOC-COVERAGE-MATRIX-001 |
| GATE-02 | Reconciliation closure | Any unresolved conflict blocks release | DOC-RECONCILIATION-LOG-001 |
| GATE-03 | CLI parity | Any mismatch between CLI docs and argparse contract blocks release | MCP_CLI_REFERENCE plus cli/main.py check |
| GATE-04 | Ingestion behavior alignment | Any mismatch between source-ingestion docs and implemented behavior blocks release | SPEC-005, SPEC-006, runtime module review |
| GATE-05 | Link integrity | Any broken link in active canonical docs blocks release | link verification report |
| GATE-06 | Failure mode coverage | Missing failure mode sections in canonical specs blocks release | SPEC-005 through SPEC-007 |

---

## 5. PASS Criteria

A release passes this policy only when all gate results are PASS and:
- unresolved conflict count = 0
- critical mismatch count = 0
- broken link count = 0
- ownership coverage = 100 percent

---

## 6. Failure Handling

When any gate fails:
1. Record failure in compliance report.
2. Assign remediation owner.
3. Block release progression.
4. Re-run gates after remediation.

---

## 7. Resource Requirements and Constraints

- Contributors: docs-maintainer, runtime-maintainer, release-approver
- Runtime cost: low to moderate
- Constraint: gate evidence must be reproducible and persisted in plans directory
