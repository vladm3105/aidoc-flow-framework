# Environment Specification

**Project**: AI Cloud Cost Monitoring
**Version**: 1.0
**Last Updated**: {DATE}

---

## Environment Overview

| Environment | GCP Project | Purpose | Access |
|:------------|:------------|:--------|:-------|
| Development | `{GCP_PROJECT_DEV}` | Integration testing, feature validation | Team |
| Staging | `{GCP_PROJECT_STAGING}` | Pre-prod validation, E2E testing | Team |
| Production | `{GCP_PROJECT_PROD}` | Live system | Restricted |

---

## Auto-Deploy Policy

| Environment | Trigger | Workflow | Condition |
|:------------|:--------|:---------|:----------|
| Development | Phase issues closed | `check-phase-completion.yml` → `deploy-dev.yml` | Per-phase (incremental) |
| Staging | All phases on dev | `check-all-phases-dev.yml` → `deploy-staging.yml` | All 8 phases dev_deployed |
| Production | Manual dispatch | `deploy-prod.yml` | Staging tests pass + 2 reviewer approval |

### Unified Phase-Gated Deployment

Dev receives incremental deployments; staging deploys only when complete:

**Dev Deployment (Per-Phase)**:
1. `check-phase-completion.yml` runs hourly and on issue close events
2. When phase N issues are closed → triggers `deploy-dev.yml` for phase N
3. Dev deployment runs smoke tests (health, readiness, version, config)
4. Phase marked `dev_deployed` on success
5. `check-all-phases-dev.yml` runs to check overall status

**Staging Deployment (All Phases Complete)**:
1. `check-all-phases-dev.yml` verifies all 8 phases are `dev_deployed`
2. When all complete → triggers `deploy-staging.yml` with final image
3. Staging receives Phase 8 image (includes all functionality)
4. Full acceptance tests run (all phases)
5. Test failures create regression issues labeled `ai:ready`

**Why**: Partial staging deployments don't make sense. Staging should always be a complete, production-like environment.

**Reference**: [IPLAN-011](../../governance/plans/IPLAN-011_unified-phase-gated-deployment.md)

---

## Resource Configuration

### Cloud Run Services

| Resource | Development | Staging | Production |
|:---------|:------------|:--------|:-----------|
| Min instances | 0 | 1 | 2 |
| Max instances | 2 | 5 | 10 |
| CPU | 1 | 1 | 2 |
| Memory | 512Mi | 1Gi | 2Gi |
| Concurrency | 80 | 80 | 100 |
| Timeout | 60s | 60s | 60s |
| CPU allocation | Request-based | Always-on | Always-on |

### BigQuery Datasets

| Resource | Development | Staging | Production |
|:---------|:------------|:--------|:-----------|
| Dataset ID | `{PROJECT_PREFIX}_dev` | `{PROJECT_PREFIX}_staging` | `{PROJECT_PREFIX}_prod` |
| Location | `{GCP_REGION}` | `{GCP_REGION}` | `{GCP_REGION}` |
| Default expiration | 30 days | 90 days | None |
| Access | Team | Team | Restricted |

### Pub/Sub Topics

| Topic | Development | Staging | Production |
|:------|:------------|:--------|:-----------|
| Budget alerts | `budget-alerts-dev` | `budget-alerts-staging` | `budget-alerts` |
| Cost events | `cost-events-dev` | `cost-events-staging` | `cost-events` |
| Remediation | `remediation-dev` | `remediation-staging` | `remediation` |

### Firestore

| Resource | Development | Staging | Production |
|:---------|:------------|:--------|:-----------|
| Database | `(default)` | `(default)` | `(default)` |
| Location | `nam5` | `nam5` | `nam5` |
| Collections | `*-dev` suffix | `*-staging` suffix | No suffix |

---

## Network Configuration

### VPC

| Environment | VPC | Subnet |
|:------------|:----|:-------|
| Development | `{GCP_PROJECT_DEV}-vpc` | `10.0.0.0/24` |
| Staging | `{GCP_PROJECT_STAGING}-vpc` | `10.1.0.0/24` |
| Production | `{GCP_PROJECT_PROD}-vpc` | `10.2.0.0/24` |

### Serverless VPC Connector

Each environment has a dedicated connector for Cloud Run → VPC communication:

| Environment | Connector | IP Range |
|:------------|:----------|:---------|
| Development | `{GCP_PROJECT_DEV}-connector` | `10.8.0.0/28` |
| Staging | `{GCP_PROJECT_STAGING}-connector` | `10.9.0.0/28` |
| Production | `{GCP_PROJECT_PROD}-connector` | `10.10.0.0/28` |

---

## IAM Configuration

### Service Accounts

| Environment | Service Account | Roles |
|:------------|:----------------|:------|
| Development | `{GCP_PROJECT_DEV}-sa@{GCP_PROJECT_DEV}.iam.gserviceaccount.com` | Cloud Run Invoker, BigQuery User, Firestore User |
| Staging | `{GCP_PROJECT_STAGING}-sa@{GCP_PROJECT_STAGING}.iam.gserviceaccount.com` | Cloud Run Invoker, BigQuery User, Firestore User |
| Production | `{GCP_PROJECT_PROD}-sa@{GCP_PROJECT_PROD}.iam.gserviceaccount.com` | Cloud Run Invoker, BigQuery User, Firestore User |

### Workload Identity Federation

All CI/CD authentication uses WIF (no service account keys):

| Environment | WIF Pool | Provider |
|:------------|:---------|:---------|
| Development | `github-pool` | `{WIF_PROVIDER_NAME}` |
| Staging | `github-pool` | `{WIF_PROVIDER_NAME}` |
| Production | `github-pool` | `{WIF_PROVIDER_NAME}` |

---

## Secrets Configuration

### GitHub Repository Secrets

| Secret | Scope | Purpose |
|:-------|:------|:--------|
| `WIF_PROVIDER` | All | WIF provider resource name |
| `WIF_SA_EMAIL_DEV` | Dev | Dev service account email |
| `WIF_SA_EMAIL_STAGING` | Staging | Staging service account email |
| `WIF_SA_EMAIL_PROD` | Prod | Prod service account email |
| `GCP_PROJECT_DEV` | Dev | Dev project ID |
| `GCP_PROJECT_STAGING` | Staging | Staging project ID |
| `GCP_PROJECT_PROD` | Prod | Prod project ID |

### GCP Secret Manager

| Secret | Environments | Purpose |
|:-------|:-------------|:--------|
| `auth0-client-secret` | All | Auth0 authentication |
| `llm-api-key` | All | LiteLLM API key |
| `database-password` | All | PostgreSQL password (Phase 7) |

---

## GitHub Environment Configuration

### Development

| Setting | Value |
|:--------|:------|
| Protection rules | None |
| Deployment branches | `main` |
| Required reviewers | 0 |
| Wait timer | 0 minutes |

### Staging

| Setting | Value |
|:--------|:------|
| Protection rules | Wait timer |
| Deployment branches | `main` |
| Required reviewers | 0 |
| Wait timer | 5 minutes |

### Production

| Setting | Value |
|:--------|:------|
| Protection rules | Required reviewers + Wait timer |
| Deployment branches | `main`, `release/*` |
| Required reviewers | 2 |
| Wait timer | 10 minutes |

---

## Monitoring Configuration

### Cloud Monitoring

| Environment | Alert Policy | Notification Channel |
|:------------|:-------------|:---------------------|
| Development | Errors only | None |
| Staging | Errors + latency | Team email |
| Production | Full monitoring | PagerDuty + Teams |

### Log Retention

| Environment | Retention | Export |
|:------------|:----------|:-------|
| Development | 7 days | None |
| Staging | 30 days | BigQuery (sampled) |
| Production | 90 days | BigQuery (full) |

---

## Cost Controls

### Budget Alerts

| Environment | Monthly Budget | Alert Thresholds |
|:------------|:---------------|:-----------------|
| Development | $100 | 50%, 80%, 100% |
| Staging | $200 | 50%, 80%, 100% |
| Production | $2,000 | 50%, 80%, 90%, 100% |

### Resource Quotas

| Resource | Development | Staging | Production |
|:---------|:------------|:--------|:-----------|
| Cloud Run instances | 5 | 10 | 20 |
| BigQuery slots | 100 | 500 | 2000 |
| Pub/Sub throughput | 10 MB/s | 50 MB/s | 100 MB/s |

---

## Environment Parity

To minimize production surprises, staging mirrors production except:

| Aspect | Staging | Production |
|:-------|:--------|:-----------|
| Instance count | Reduced | Full |
| Data | Anonymized copy | Real data |
| External services | Sandbox/test | Production |
| Budget alerts | Test channel | Real channel |

---

## References

- [04-deployment-strategy.md](04-deployment-strategy.md) — Deployment procedures
- [ADR-002](../../docs/adr/002-gcp-only-first.md) — GCP-first architecture
- [GCP-DEPLOYMENT.md](../../GCP-DEPLOYMENT.md) — Detailed GCP setup
