# Deployment Strategy

**Project**: AI Cloud Cost Monitoring
**Version**: 1.0
**Last Updated**: {DATE}

---

## Environment Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Development │────►│   Staging   │────►│ Production  │
│  (auto)     │     │   (auto)    │     │  (manual)   │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
  Per-phase          All phases          Manual dispatch
  incremental        complete            + approval
```

### Trigger Mechanisms

| Environment | Workflow | Trigger | Condition |
|:------------|:---------|:--------|:----------|
| Development | `check-phase-completion.yml` → `deploy-dev.yml` | Automatic | Phase issues closed (incremental) |
| Staging | `check-all-phases-dev.yml` → `deploy-staging.yml` | Automatic | All 8 phases deployed to dev |
| Production | `deploy-prod.yml` | Manual | `workflow_dispatch` + 2 reviewers |

### Unified Phase-Gated Model

This project uses an **AI-first development approach** where AI agents create PRs rapidly. Per-PR deployments are wasteful; dev and staging use phase-gated triggers:

**Development (Incremental)**: Each phase deploys independently when its issues close. The `check-phase-completion.yml` workflow triggers `deploy-dev.yml` per phase. Smoke tests validate each phase before marking `dev_deployed`.

**Staging (Complete Only)**: Deploys only when ALL 8 phases are `dev_deployed`. The `check-all-phases-dev.yml` workflow runs after each dev deployment and triggers staging when complete. Staging is always a complete environment, never partial.

**Production**: Requires manual trigger with deployment window enforcement (Mon-Fri 10am-4pm EST).

**Reference**: [IPLAN-011](../../governance/plans/IPLAN-011_unified-phase-gated-deployment.md)

---

## Promotion Criteria

### Development → Staging

| Criterion | Check | Automated |
|:----------|:------|:----------|
| CI pipeline passes | All stages green | Yes |
| No critical vulnerabilities | Security scan | Yes |
| Smoke tests pass | Health endpoint | Yes |
| Image scanned | Trivy | Yes |

### Staging → Production

| Criterion | Check | Automated |
|:----------|:------|:----------|
| E2E tests pass | Full test suite | Yes |
| No new critical CVEs | Daily scan | Yes |
| Deployment window | Weekdays 10am-4pm EST | Yes |
| Approval received | 2 reviewers | No |

---

## Deployment Windows

| Environment | Window | Restrictions |
|:------------|:-------|:-------------|
| Development | 24/7 | None |
| Staging | 24/7 | None |
| Production | Mon-Fri 10am-4pm EST | No Friday deployments |

### Deployment Freeze Periods

- **Code freeze**: 48 hours before major releases
- **Holiday freeze**: Dec 20 - Jan 3
- **Incident freeze**: During active P1/P2 incidents

---

## Rollback Procedures

### Automatic Rollback

Triggered when health checks fail after deployment:

```bash
# Cloud Run automatically routes traffic to previous revision
# if new revision fails health checks
gcloud run services update-traffic ${SERVICE} \
  --region {GCP_REGION} \
  --to-revisions=REVISION_ID=100
```

### Manual Rollback

```bash
# List revisions
gcloud run revisions list --service ${SERVICE} --region {GCP_REGION}

# Route all traffic to previous revision
gcloud run services update-traffic ${SERVICE} \
  --region {GCP_REGION} \
  --to-revisions=${PREVIOUS_REVISION}=100

# Delete failed revision (optional)
gcloud run revisions delete ${FAILED_REVISION} --region {GCP_REGION}
```

### Rollback Decision Matrix

| Symptom | Severity | Action |
|:--------|:---------|:-------|
| Health check failure | Critical | Auto-rollback |
| Error rate >5% | High | Manual rollback |
| Latency p99 >5s | Medium | Investigate, consider rollback |
| Feature bug (non-critical) | Low | Hotfix forward |

---

## Blue-Green Deployment

Cloud Run native traffic splitting:

### Gradual Rollout

```bash
# Deploy new revision with no traffic
gcloud run deploy ${SERVICE} \
  --image gcr.io/${PROJECT}/${SERVICE}:${VERSION} \
  --no-traffic

# Route 10% traffic to new revision
gcloud run services update-traffic ${SERVICE} \
  --to-revisions=LATEST=10

# Monitor metrics for 5 minutes
# If healthy, increase to 50%
gcloud run services update-traffic ${SERVICE} \
  --to-revisions=LATEST=50

# Monitor metrics for 5 minutes
# If healthy, route 100%
gcloud run services update-traffic ${SERVICE} \
  --to-latest
```

### Traffic Split Monitoring

| Metric | Threshold | Action |
|:-------|:----------|:-------|
| Error rate | >1% delta | Pause rollout |
| Latency p50 | >20% increase | Pause rollout |
| CPU usage | >80% | Pause rollout |
| Memory usage | >85% | Pause rollout |

---

## Hotfix Process

For critical production issues that cannot wait for normal release cycle:

### Hotfix Flow

```
main ─────────────────────────────────────────►
       \                     /
        hotfix/issue-xxx ───►
              │
              ├── Fix implemented
              ├── Unit tests added
              ├── PR reviewed (expedited)
              ├── Merge to main
              └── Direct deploy to prod (skip staging)
```

### Hotfix Criteria

| Criterion | Requirement |
|:----------|:------------|
| Severity | P1 (Critical) or P2 (High) |
| Approval | 1 senior engineer |
| Testing | Unit tests covering fix |
| Documentation | Incident ticket linked |

### Hotfix Commands

```bash
# Create hotfix branch
git checkout -b hotfix/critical-fix main

# After fix and PR merge
# Deploy directly to production
gcloud run deploy ${SERVICE} \
  --image gcr.io/${PROJECT}/${SERVICE}:${HOTFIX_SHA} \
  --region {GCP_REGION} \
  --project ${PROD_PROJECT}
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] CI pipeline passed
- [ ] Security scan clean
- [ ] Dependencies updated (if applicable)
- [ ] Database migrations ready (if applicable)
- [ ] Feature flags configured (if applicable)
- [ ] Runbook updated (if new features)

### During Deployment

- [ ] Monitor error rates
- [ ] Monitor latency metrics
- [ ] Check health endpoints
- [ ] Verify logs for errors

### Post-Deployment

- [ ] Smoke test critical paths
- [ ] Verify external integrations
- [ ] Update deployment log
- [ ] Notify stakeholders (for major releases)

---

## Deployment Monitoring

### Key Metrics

| Metric | Source | Alert Threshold |
|:-------|:-------|:----------------|
| Request error rate | Cloud Run | >1% for 5 min |
| Request latency p99 | Cloud Run | >3s for 5 min |
| Instance count | Cloud Run | Max instances for 10 min |
| Memory usage | Cloud Run | >85% for 5 min |
| Cold start latency | Cloud Run | >10s |

### Dashboards

| Dashboard | Purpose |
|:----------|:--------|
| Deployment Overview | Real-time deployment status |
| Service Health | Per-service metrics |
| Error Analysis | Error breakdown by type |

---

## References

- [05-environment-spec.md](05-environment-spec.md) — Environment configuration
- [ADR-004](../../docs/adr/004-cloud-run-not-kubernetes.md) — Cloud Run deployment target
- [GCP-DEPLOYMENT.md](../../GCP-DEPLOYMENT.md) — GCP deployment guide
