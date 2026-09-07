# Documentation Quality Gates

| Field | Value |
| --- | --- |
| Policy ID | DOC-QUALITY-GATES-001 |
| Status | Active |
| Version | 2.0 |
| Date | 2026-05-03 |
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
  - Required when files under `ucx_hermes/src/mcp_server` affecting CLI, prompt assembly, review runner, remediation runner, or project loader are changed.
  - Hermes is the default orchestration agent for pull-request governance from PR submission through escalation or merge.
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
| GATE-07 | PR deterministic validation | Final-round `sdd_validate` not PASS blocks merge | validate report artifacts per round |
| GATE-08 | PR persona review/remediation completion | Missing `sdd_review` + `sdd_remediate` sequence in an executed round blocks merge | review/remediation report artifacts per round |
| GATE-09 | Hermes final blocker-gap check | Hermes final review not PASS blocks merge | Hermes final review report/check output |
| GATE-10 | Escalation lock | Escalation status `REQUIRED` blocks merge until human approval | escalation status artifact and approval record |

---

## 5. PASS Criteria

A release passes this policy only when all gate results are PASS and:

- unresolved conflict count = 0
- critical mismatch count = 0
- broken link count = 0
- ownership coverage = 100 percent

Pull-request merge passes this policy only when all PR gates are PASS and:

- Round 1 or Round 2 has complete gate evidence.
- If Round 1 fails, Round 2 runs with the same gate sequence.
- If Round 2 fails, human review is mandatory before merge.

---

## 6. Failure Handling

When any gate fails:

1. Record failure in compliance report.
2. Assign remediation owner.
3. Block release progression.
4. Re-run gates after remediation.

For pull-request governance failures:

1. Round 1 failure triggers Round 2 automatically or by orchestrator policy.
2. Round 2 failure sets escalation status to `REQUIRED`.
3. Hermes alerts a human developer for review (alert channel is implementation-defined).
4. Merge remains blocked until either gates pass in a subsequent round or human approval clears escalation.

---

## 7. Resource Requirements and Constraints

- Contributors: docs-maintainer, runtime-maintainer, release-approver
- Runtime cost: low to moderate
- Constraint: gate evidence must be reproducible and persisted in plans directory
