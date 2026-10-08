# Architecture & Operational Standard: Quality Assurance & Acceptance Testing Protocol

## Document Control

| Field | Value |
|---|---|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-06 |
| Author | Framework Maintainer |
| Framework Version | 0.91.0 |

**Scope:** Acceptance Testing, Staging Verification & Defect Reporting for `[Project Name]`
**Governing Rules:** `GOVERNANCE_WORKFLOW_STANDARD.md`, `REVIEW_REMEDIATION_FLOW.md`, `CI_AUTONOMOUS_PR_STANDARD.md`
**Canonical Template:** `framework/governance/aidoc/AIDOC-QA-PROTOCOL-TEMPLATE.md`

---

## 1. Purpose & Tripartite Separation of Concerns

High-reliability autonomous software delivery requires distinct boundaries between implementation, test authoring, and acceptance verification. Conforming projects enforce three discrete engineering roles:

| Role | Responsibility | Code Mutation Authority |
|---|---|---|
| **DEV (Developer)** | Implements features, fixes bugs, refactors code | Authorized to modify application source and internal unit test fixtures |
| **SDET (Test Engineer)** | Authors automated test suites, mocks, and benchmarks | Authorized to modify test directories (`tests/**`) and test scaffolding |
| **QA (Acceptance Verifier)** | Executes end-to-end user journeys, runs acceptance scenarios, audits compliance | **STRICT HARD BLOCK: ZERO CODE MUTATIONS** (Read-only observation and reporting) |

---

## 2. Strict Non-Code-Modifying Invariant (HARD BLOCK for QA)

When executing acceptance runs or diagnosing failures:
1. **Zero Source Edits:** QA agents MUST NOT edit production application code under any circumstance.
2. **Zero Test Masking:** QA agents MUST NOT modify test assertions, loosen thresholds, or comment out checks to simulate a green run.
3. **Structured Defect Emittance:** When a failure occurs, QA must capture complete reproduction telemetry (logs, network traces, request payloads, stack traces) and emit an actionable defect report for the DEV persona.

---

## 3. Stateful User Journey Acceptance Protocol

Acceptance runs execute against living deployment environments (e.g. local Docker Compose or dedicated staging instances) following Layer 04 BDD scenarios:

### Step 1: Environment Readiness Healthcheck
Before dispatching tests, the QA agent verifies that all dependent services are healthy:
```bash
curl -f http://localhost:8080/healthz || exit 1
```

### Step 2: Seed Clean Test State
Execute isolated database migrations and seed test datasets:
```bash
task test:seed-acceptance
```

### Step 3: Run Acceptance Journey
Execute scenario suites using the project test orchestrator:
```bash
pytest tests/acceptance/ -v -m "acceptance"
```

---

## 4. Defect Ticket & Reproduction Report Standard

When an acceptance test fails, the QA agent emits a standardized defect report containing:

```markdown
### Defect Report: [Brief Failure Title]

- **Timestamp:** YYYY-MM-DDTHH:MM:SSZ
- **Failing Scenario / Test:** `tests/acceptance/test_checkout_journey.py::test_user_payment_timeout`
- **Upstream Requirements:** `REQ-088`, `BDD-SCN-042`
- **Expected Outcome:** System returns HTTP 408 with retry header.
- **Actual Outcome:** System returned HTTP 500 with unhandled NullReferenceException.

#### Reproduction Steps
```bash
curl -X POST http://localhost:8080/api/v1/checkout \
  -H "Content-Type: application/json" \
  -d '{"user_id": "usr_123", "items": []}'
```

#### Service Telemetry & Stack Trace
```text
[ERROR] 2026-10-06T02:00:12Z PaymentService: panic in processPayment: nil pointer dereference
...
```
```

---

## 5. Mandatory Post-Merge Issue Closure & Implementation Report Contract

Upon successful PR merge into `dev`, the delivering agent completes the delivery lifecycle:

1. **Verify PR Merge:** Confirm `mergeCommit.oid` is present on `origin/dev`.
2. **Post Implementation & Verification Report on Issue:**
   ```markdown
   ### Implementation & Verification Report

   - **Delivered PR:** #<PR_NUMBER>
   - **Merge Commit:** `<COMMIT_SHA>`
   - **Summary of Changes:**
     - Implemented user payment timeout handling per SPEC-042.
     - Added integration test coverage exercising gateway timeouts.
   - **Verification Evidence:**
     - CI Suite: [Run #12345](https://ci.example.com/runs/12345) — GREEN
     - Acceptance Suite: 14 scenarios passed, 0 failed.
   - **Artifact Links:**
     - `docs/sdd/06_SPEC/SPEC-042.yaml`
     - `docs/sdd/08_IPLAN/IPLAN-042.yaml`
   ```
3. **Safe Publish:** Publish report using `gh issue comment <ISSUE_NUMBER> --body-file <FILE>` and verify non-zero response length.
