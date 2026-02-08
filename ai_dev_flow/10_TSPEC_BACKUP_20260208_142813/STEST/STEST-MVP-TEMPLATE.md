---
title: "STEST-MVP-TEMPLATE: Smoke Test Specification (MVP)"
tags:
  - stest-template
  - mvp-template
  - layer-10-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: STEST
  layer: 10
  test_type_code: 42
  template_profile: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.0"
  complexity: 1
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `STEST-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `STEST_MVP_SCHEMA.yaml`
> - **Consistency Requirement**: MD and YAML templates MUST remain consistent.

---

<!--
AI_CONTEXT_START
Role: AI Test Engineer
Objective: Create smoke test specifications for post-deployment validation.
Constraints:
- Define critical path tests for deployment verification.
- 6 sections required (aligned with MVP requirements).
- Required traceability tags: @ears, @bdd, @req.
- Total suite timeout: <5 minutes.
- 100% quality gate required (critical for deployment).
- Every test must have rollback procedure.
- Focus on fail-fast, binary pass/fail results.
AI_CONTEXT_END
-->

**MVP Template** — Single-file, streamlined STEST for rapid MVP development.
Use this template for smoke test specifications verifying deployment health.

**Validation Note**: STEST requires 100% quality gate compliance.

References: Schema `STEST_MVP_SCHEMA.yaml` | Rules `STEST_MVP_CREATION_RULES.md`, `STEST_MVP_VALIDATION_RULES.md` | Matrix `TSPEC-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# STEST-NN: [Deployment Target] Smoke Test Specification

**MVP Scope**: Smoke test specifications for [Deployment Target] with <5 minute total timeout.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author name] |
| **Deployment Target** | [Environment/service name] |
| **Total Timeout Budget** | [N] seconds (max 300s) |
| **EARS Reference** | EARS.NN.25.01 |
| **BDD Reference** | BDD.NN.01.01 |
| **TASKS-Ready Score** | [XX]% (Target: 100%) |
| **Template Version** | 1.0 |

---

## 2. Test Scope

### 2.1 Deployment Context

| Attribute | Value |
|-----------|-------|
| **Environment** | [Production/Staging/Dev] |
| **Deployment Type** | [Blue-Green/Rolling/Canary] |
| **Trigger** | [Post-deploy/Manual/Scheduled] |
| **Success Criteria** | All tests pass within timeout |

### 2.2 Timeout Budget

| Test ID | Timeout | Cumulative |
|---------|---------|------------|
| TSPEC.NN.42.01 | 30s | 30s |
| TSPEC.NN.42.02 | 45s | 75s |
| TSPEC.NN.42.03 | 60s | 135s |
| TSPEC.NN.42.04 | 30s | 165s |
| **Buffer** | 135s | **300s** |

**Total Budget**: 300 seconds (5 minutes)

### 2.3 Critical Paths

| Path | Priority | Impact |
|------|----------|--------|
| Authentication | P0 | Complete outage |
| Health endpoints | P0 | Monitoring blind |
| Core API | P0 | Service degraded |
| Database connectivity | P0 | Data unavailable |

---

## 3. Critical Path Index

| ID | Path | Timeout | Rollback Trigger | Priority |
|----|------|---------|------------------|----------|
| TSPEC.NN.42.01 | Auth Flow | 30s | Yes | P0 |
| TSPEC.NN.42.02 | Health Check | 45s | Yes | P0 |
| TSPEC.NN.42.03 | Core API | 60s | Yes | P0 |
| TSPEC.NN.42.04 | DB Connect | 30s | Yes | P0 |

---

## 4. Test Case Details

### TSPEC.NN.42.01: Authentication Flow Smoke Test

**Critical Path**: Authentication

**Traceability**:
- @ears: EARS.NN.25.01
- @bdd: BDD.NN.01.01
- @req: REQ.NN.10.01

**Timeout**: 30 seconds

**Pass/Fail Criteria**:

| Condition | Result |
|-----------|--------|
| Login returns 200 with valid token | ✅ PASS |
| Login returns non-200 | ❌ FAIL |
| Response time > 5s | ❌ FAIL |
| Token validation fails | ❌ FAIL |

**Health Check**:

```bash
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user":"smoke_test","pass":"***"}' \
  --max-time 5 \
  -w "%{http_code}"
```

**Rollback Procedure**:

| Step | Action | Command |
|------|--------|---------|
| 1 | Alert on-call | PagerDuty trigger |
| 2 | Revert deployment | `kubectl rollout undo` |
| 3 | Verify rollback | Re-run smoke test |
| 4 | Post-mortem | Create incident ticket |

---

### TSPEC.NN.42.02: Health Endpoint Smoke Test

**Critical Path**: Health Check

**Traceability**:
- @ears: EARS.NN.25.02
- @bdd: BDD.NN.01.02
- @req: REQ.NN.10.02

**Timeout**: 45 seconds

**Pass/Fail Criteria**:

| Condition | Result |
|-----------|--------|
| /health returns 200 | ✅ PASS |
| /health/ready returns 200 | ✅ PASS |
| /health/live returns 200 | ✅ PASS |
| Any health endpoint fails | ❌ FAIL |

**Health Check**:

```bash
# Liveness
curl -f https://api.example.com/health/live --max-time 10

# Readiness
curl -f https://api.example.com/health/ready --max-time 15

# Deep health
curl -f https://api.example.com/health --max-time 20
```

**Rollback Procedure**:

| Step | Action | Command |
|------|--------|---------|
| 1 | Immediate rollback | `kubectl rollout undo` |
| 2 | Check pod status | `kubectl get pods` |
| 3 | Verify health | Re-run smoke test |

---

### TSPEC.NN.42.03: Core API Smoke Test

**Critical Path**: Core API

**Traceability**:
- @ears: EARS.NN.25.03
- @bdd: BDD.NN.01.03
- @req: REQ.NN.10.03

**Timeout**: 60 seconds

**Pass/Fail Criteria**:

| Condition | Result |
|-----------|--------|
| GET /api/v1/status returns 200 | ✅ PASS |
| Response contains expected fields | ✅ PASS |
| Response time < 2s | ✅ PASS |
| Any failure | ❌ FAIL |

**Health Check**:

```bash
response=$(curl -s -w "\n%{http_code}" \
  https://api.example.com/api/v1/status \
  --max-time 2)
status_code=$(echo "$response" | tail -n1)
[ "$status_code" = "200" ] || exit 1
```

**Rollback Procedure**:

| Step | Action | Command |
|------|--------|---------|
| 1 | Traffic drain | Remove from LB |
| 2 | Rollback | `kubectl rollout undo` |
| 3 | Restore traffic | Add to LB |
| 4 | Verify | Re-run smoke test |

---

### TSPEC.NN.42.04: Database Connectivity Smoke Test

**Critical Path**: Database

**Traceability**:
- @ears: EARS.NN.25.04
- @bdd: BDD.NN.01.04
- @req: REQ.NN.10.04

**Timeout**: 30 seconds

**Pass/Fail Criteria**:

| Condition | Result |
|-----------|--------|
| DB ping succeeds | ✅ PASS |
| Read query succeeds | ✅ PASS |
| Connection pool active | ✅ PASS |
| Any DB error | ❌ FAIL |

**Health Check**:

```bash
# Via health endpoint with DB check
curl -f https://api.example.com/health/db --max-time 10

# Direct check (if available)
pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER
```

**Rollback Procedure**:

| Step | Action | Command |
|------|--------|---------|
| 1 | Check DB status | `pg_isready` |
| 2 | Check migrations | Verify schema version |
| 3 | Rollback if schema | Run down migrations |
| 4 | Rollback deployment | `kubectl rollout undo` |

---

## 5. Rollback Procedures

### Global Rollback Matrix

| Test Failure | Immediate Action | Escalation |
|--------------|------------------|------------|
| Auth | Rollback + PagerDuty | P1 Incident |
| Health | Rollback | P2 Incident |
| Core API | Rollback + PagerDuty | P1 Incident |
| Database | Rollback + DBA alert | P1 Incident |

### Rollback Commands

```bash
# Kubernetes rollback
kubectl rollout undo deployment/[service] -n [namespace]

# Verify rollback
kubectl rollout status deployment/[service] -n [namespace]

# Check previous revision
kubectl rollout history deployment/[service] -n [namespace]
```

---

## 6. Traceability

### 6.1 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @ears | EARS.NN.25.01 | Behavioral requirement |
| @bdd | BDD.NN.01.01 | Feature scenario |
| @req | REQ.NN.10.01 | Functional requirement |

### 6.2 Downstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @tasks | TASKS-NN | Implementation tasks |
| @code | `scripts/smoke_test.sh` | Test script |
| @pipeline | `.github/workflows/smoke.yml` | CI/CD integration |

---

## Appendix: Execution Configuration

### CI/CD Integration

```yaml
smoke_test:
  stage: post-deploy
  timeout: 5m
  script:
    - ./scripts/smoke_test.sh
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
  on_failure:
    - kubectl rollout undo deployment/$SERVICE
```

### Alert Configuration

| Test | Alert Channel | Severity |
|------|---------------|----------|
| Auth | #alerts-critical | Critical |
| Health | #alerts-warning | Warning |
| Core API | #alerts-critical | Critical |
| Database | #alerts-critical + DBA | Critical |
