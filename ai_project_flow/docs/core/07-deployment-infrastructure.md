# AI Cost Monitoring — Deployment & Infrastructure Architecture

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 07 — Deployment & Infrastructure Architecture |
| **Version** | 2.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, DevOps Engineers, SRE |

---

## 1. Infrastructure Overview

### 1.1 Target Environment (Cloud-Native, Serverless-First)

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| **Home Cloud** | GCP first, AWS/Azure later | GCP for MVP, cloud-agnostic architecture (see ADR-002) |
| **Container Platform** | Serverless containers | Cloud Run / ECS Fargate / Azure Container Apps (see ADR-004) |
| **Analytics Database** | Cloud-native | BigQuery / Athena / Synapse (see ADR-003) |
| **Task Queue** | Cloud-native | Cloud Tasks / SQS / Service Bus (see ADR-006) |
| **Infrastructure as Code** | Terraform | Multi-cloud capability, state management |
| **CI/CD** | GitHub Actions | Integrated with repo, cloud deployment actions |

**Architecture Principles:**
- ✅ Serverless-first (zero infrastructure management)
- ✅ Cloud-native services (managed, pay-per-use)
- ✅ No Kubernetes (too complex for team size)
- ✅ No self-hosted databases (TimescaleDB, InfluxDB)
- ✅ No Celery/Redis task queues (use cloud services)

### 1.2 Environment Strategy

| Environment | Purpose | Infra Scale | Data |
|-------------|---------|-------------|------|
| **dev** | Developer testing, feature branches | Minimal (zero-scale serverless) | Synthetic / sample data |
| **staging** | Pre-production validation, integration tests | Production-like (scaled down) | Anonymized production snapshot |
| **production** | Live customer traffic | Auto-scales with load | Real tenant data |

---

## 2. GCP Deployment Architecture (First Home Cloud)

### 2.1 Component Mapping

| Component | GCP Service | Scaling | Purpose |
|-----------|-------------|---------|----------|
| **Frontend** | Cloud Run | Auto (0-100) | Next.js + CopilotKit UI |
| **Backend API** | Cloud Run | Auto (1-50) | FastAPI orchestrator/AG-UI server |
| **MCP Servers** | Cloud Run | Auto (0-20 each) | AWS, Azure, GCP, OpenCost, Forecast, Policy MCPs |
| **Relational DB** | Cloud SQL PostgreSQL | Managed | Tenants, users, accounts, metadata |
| **Analytics DB** | BigQuery | Serverless | Cost metrics from billing export |
| **Task Queue** | Cloud Tasks | Serverless | Background jobs (sync, anomaly detection) |
| **Scheduler** | Cloud Scheduler | Managed | Trigger scheduled jobs (every 4 hours) |
| **Secret Manager** | GCP Secret Manager | Managed | Cloud credentials, API keys |
| **Object Storage** | Cloud Storage | Serverless | Reports, exports |
| **Cache** (optional) | Cloud Memorystore Redis | Managed | L2 query cache |
| **CDN** | Cloud CDN | Global | Static assets |
| **Load Balancer** | Cloud Load Balancing | Global | HTTPS termination, routing |
| **Traces** | Cloud Trace | Serverless | OTEL Gen-AI distributed tracing ([09-observability-spec](09-observability-spec.md)) |
| **Metrics** | Cloud Monitoring | Serverless | Gen-AI metrics, custom dashboards |
| **Logs** | Cloud Logging | Serverless | Structured logs with trace ID correlation |

### 2.2 Architecture Diagram

```
Internet
  ↓
Cloud Load Balancer (HTTPS)
  ↓
┌─────────────────────────────────────────────┐
│ Cloud Run Services (Auto-scaling)           │
├─────────────────────────────────────────────┤
│ Frontend (Next.js)                          │
│ Backend API (FastAPI + CopilotKit)         │
│ MCP Servers (AWS, Azure, GCP, OpenCost...) │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ Data Layer                                  │
├─────────────────────────────────────────────┤
│ Cloud SQL PostgreSQL (managed HA)          │
│ BigQuery (billing export)                  │
│ Cloud Storage (reports)                    │
│ Secret Manager (credentials)               │
│ Cloud Memorystore Redis (optional cache)   │
└─────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────┐
│ Background Jobs                             │
├─────────────────────────────────────────────┤
│ Cloud Scheduler → Cloud Tasks → Cloud Run  │
│ (cost sync, anomaly detection, forecasts)  │
└─────────────────────────────────────────────┘
```

### 2.3 Scaling Strategy (GCP)

All Cloud Run services auto-scale based on:
- Request concurrency (default: 80 concurrent requests/instance)
- CPU utilization
- Minimum instances (0 for cost savings, 1 for latency-sensitive)

| Service | Min Instances | Max Instances | Concurrency |
|---------|---------------|---------------|-------------|
| Frontend | 0 | 100 | 80 |
| Backend API | 1 | 50 | 80 |
| MCP Servers | 0 | 20 each | 80 |

**Cost Optimization:**
- Most services scale to zero when idle
- Backend API keeps 1 warm instance (low latency)
- Billed only for actual CPU/memory usage

---

## 3. AWS Deployment Architecture (Alternative Home Cloud)

### 3.1 Component Mapping

| Component | AWS Service | GCP Equivalent |
|-----------|-------------|----------------|
| **Containers** | ECS Fargate or App Runner | Cloud Run |
| **Relational DB** | RDS PostgreSQL | Cloud SQL |
| **Analytics DB** | Athena + S3 (CUR export) | BigQuery |
| **Task Queue** | SQS + Lambda | Cloud Tasks |
| **Scheduler** | EventBridge Scheduler | Cloud Scheduler |
| **Secrets** | AWS Secrets Manager | GCP Secret Manager |
| **Object Storage** | S3 | Cloud Storage |
| **Cache** (optional) | ElastiCache Redis | Cloud Memorystore |
| **CDN** | CloudFront | Cloud CDN |
| **Load Balancer** | ALB | Cloud Load Balancing |

### 3.2 Background Jobs Pattern (AWS)

```
EventBridge Scheduler (cron)
  → SQS Queue
    → Lambda Function
      → Calls ECS Fargate task (long-running jobs)
```

**Why this pattern:**
- Lambda for orchestration (< 15 min)
- ECS Fargate for long-running sync jobs (can run hours)

---

## 4. Azure Deployment Architecture (Alternative Home Cloud)

### 4.1 Component Mapping

| Component | Azure Service | GCP Equivalent |
|-----------|---------------|----------------|
| **Containers** | Azure Container Apps | Cloud Run |
| **Relational DB** | Azure Database for PostgreSQL | Cloud SQL |
| **Analytics DB** | Synapse Analytics (serverless SQL) | BigQuery |
| **Task Queue** | Service Bus + Azure Functions | Cloud Tasks |
| **Scheduler** | Azure Functions (timer trigger) | Cloud Scheduler |
| **Secrets** | Azure Key Vault | GCP Secret Manager |
| **Object Storage** | Blob Storage | Cloud Storage |
| **Cache** (optional) | Azure Cache for Redis | Cloud Memorystore |
| **CDN** | Azure CDN | Cloud CDN |
| **Load Balancer** | Application Gateway | Cloud Load Balancing |

---

## 5. Multi-Cloud Deployment (Terraform Modules)

### 5.1 Terraform Structure

```
terraform/
  ├── environments/
  │     ├── gcp-dev/
  │     ├── gcp-staging/
  │     ├── gcp-production/
  │     ├── aws-production/         (future)
  │     └── azure-production/       (future)
  │
  ├── modules/
  │     ├── cloud_run_services/     (GCP)
  │     ├── ecs_fargate_services/   (AWS)
  │     ├── container_apps/         (Azure)
  │     ├── analytics_db/           (multi-cloud)
  │     ├── relational_db/          (multi-cloud)
  │     ├── task_queue/             (multi-cloud)
  │     ├── secrets/                (multi-cloud)
  │     ├── storage/                (multi-cloud)
  │     ├── auth/                   (Auth0, cloud-agnostic)
  │     ├── monitoring/             (cloud-specific)
  │     └── dns/                    (cloud-agnostic)
  │
  └── shared/
        ├── providers.tf
        └── backend.tf              (Remote state in GCS/S3)
```

### 5.2 Example: Cloud Run Service Module (GCP)

```hcl
resource "google_cloud_run_service" "backend_api" {
  name     = "backend-api"
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }

        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_url.secret_id
              key  = "latest"
            }
          }
        }
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "50"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
```

---

## 6. CI/CD Pipeline

### 6.1 Pipeline Stages

```
Developer pushes to feature branch
  → Lint & Type Check (Python: ruff, mypy / JS: eslint, tsc)
    → Unit Tests (pytest / jest)
      → Build Docker Images (multi-stage builds)
        → Integration Tests (against test containers)
          → Security Scan (Trivy for container images)
            → Push to Container Registry
              (Artifact Registry/ECR/ACR - tagged with commit SHA)

Merge to main
  → All above +
    → Deploy to staging (automatic, Cloud Run)
      → E2E Tests against staging
        → Manual approval gate
          → Deploy to production (Cloud Run rolling update)
            → Smoke tests
              → Monitor for 15 minutes
                → Promote or rollback (instant via Cloud Run revisions)
```

### 6.2 Deployment Strategy

| Strategy | Used For | Rollback Time |
|----------|----------|---------------|
| **Rolling update** | All Cloud Run services | < 1 minute (revision traffic split) |
| **Blue-green** | Database schema changes | Instant (traffic switch) |
| **Canary** | Prompt/model changes | 1-5 minutes (gradual traffic shift) |

### 6.3 Docker Image Strategy

```
Base images:
  ├── python:3.12-slim     ← Backend API, MCP servers
  ├── node:20-alpine       ← Frontend
  └── postgres:16          ← Local dev only

Shared layers:
  ├── finops-python-base   ← Common Python deps (FastAPI, LiteLLM, etc.)
  └── finops-mcp-base      ← MCP SDK, cloud provider SDKs
```

**Image naming:**
```
gcr.io/PROJECT_ID/backend-api:main-a1b2c3d
gcr.io/PROJECT_ID/mcp-gcp:main-a1b2c3d
gcr.io/PROJECT_ID/frontend:main-a1b2c3d
```

---

## 7. Network Architecture (GCP Example)

### 7.1 VPC Design

```
VPC: finops-prod (10.0.0.0/16)
  │
  ├── Subnet: public (10.0.1.0/24)
  │     └── Cloud Load Balancer
  │
  ├── Subnet: private (10.0.2.0/24)
  │     ├── Cloud Run services (VPC connector)
  │     ├── Cloud SQL (private IP)
  │     └── Cloud Memorystore Redis (private IP)
  │
  └── Subnet: admin (10.0.3.0/24)
        └── Cloud SQL proxy for admin access
```

### 7.2 Network Rules

| Source → Destination | Allowed | Notes |
|---------------------|---------|-------|
| Internet → Load Balancer | HTTPS only (443) | CloudFlare WAF recommended |
| Load Balancer → Cloud Run | Yes | Serverless VPC connector |
| Cloud Run → Cloud SQL | Yes (private IP) | VPC peering |
| Cloud Run → BigQuery | Yes | Google API endpoint |
| Cloud Run → Secret Manager | Yes | IAM-based |
| Cloud Run → Cloud APIs (AWS, Azure) | Yes (egress) | For monitoring multi-cloud |
| Cloud SQL → Internet | No | Blocked |

---

## 8. Secrets Management

### 8.1 GCP Secret Manager Usage

| Secret Type | Storage | Access Pattern |
|-------------|---------|----------------|
| Tenant cloud credentials | Secret Manager | Runtime API call per request (IAM-authorized) |
| Database connection string | Secret Manager | Mounted as env var in Cloud Run |
| LLM API keys (LiteLLM) | Secret Manager | Mounted as env var |
| Auth0 client secrets | Secret Manager | Mounted as env var |

**No OpenBao needed** - Cloud-native secret management is sufficient.

---

## 9. Monitoring & Observability

### 9.1 GCP Monitoring Stack

| Pillar | Tool | What It Covers |
|--------|------|----------------|
| **Metrics** | Cloud Monitoring | Cloud Run metrics, BigQuery query performance, API latencies |
| **Logs** | Cloud Logging | Structured JSON logs from all services, correlated by request_id |
| **Traces** | Cloud Trace | End-to-end request tracing through MCP servers |
| **Dashboards** | Grafana (optional) | Custom dashboards, cost analytics |
| **Alerts** | Cloud Monitoring Alerts → Slack/PagerDuty | Service health, error rates |

### 9.2 Key Metrics

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Cloud Run request latency (p95) | > 5 seconds | Warning |
| Cloud Run error rate | > 5% | Critical |
| Cloud SQL connection pool | > 90% | Warning |
| BigQuery query cost | > $100/day | Warning |
| Cloud Run cold starts | > 1 second | Info |

---

## 10. Disaster Recovery

| Aspect | Strategy | Target |
|--------|----------|--------|
| **RPO** (Recovery Point Objective) | 1 hour | Maximum data loss |
| **RTO** (Recovery Time Objective) | 2 hours | Maximum downtime |
| Cloud SQL backup | Automated daily + continuous WAL | Point-in-time recovery |
| BigQuery | Automatic dataset versioning | 7-day time travel |
| Secret Manager | Automatic versioning | Restore previous version |
| Object Storage | Versioning enabled | 30-day retention |
| Configuration | All in Git (Terraform + Dockerfiles) | Rebuild from scratch in < 1 hour |

---

## 11. Cost Estimates

### 11.1 GCP Monthly Costs (MVP, 100 tenants)

| Component | Cost | Notes |
|-----------|------|-------|
| Cloud Run (frontend + backend + MCPs) | $50-200 | Pay-per-use, depends on traffic |
| Cloud SQL PostgreSQL (db-n1-standard-2) | $100 | Includes HA, backups |
| BigQuery | $0-50 | Billing export is free, queries minimal |
| Cloud Tasks | $0 | Free tier covers MVP |
| Cloud Scheduler | $0.50 | $0.10/job × 5 jobs |
| Secret Manager | $5 | ~50 secrets |
| Cloud Storage | $10 | Reports, exports |
| Cloud Memorystore Redis (optional) | $0-30 | 1GB instance |
| Cloud Monitoring/Logging | $50 | Log ingestion |
| **Total** | **$215-445/month** | Scales with usage |

**Compare to Kubernetes:**
- K8s cluster: $150-300/month (3 nodes minimum)
- TimescaleDB: $50-100/month (self-managed or RDS)
- Redis: $30-50/month
- Celery workers: $50-100/month
- **Total Kubernetes**: **$280-550/month** (PLUS operational complexity)

**Serverless is cheaper AND simpler!**

---

## Developer Notes

> **DEV-INF-001:** Use cloud-native managed services for everything. Self-hosting (Kubernetes, TimescaleDB, Celery) adds operational burden with no benefit at our scale.

> **DEV-INF-002:** Every Cloud Run service must have a `/health` endpoint that returns 200 when healthy. Critical for load balancer health checks.

> **DEV-INF-003:** Terraform state must be stored remotely (GCS/S3 + locking) from day one. Never commit state files to Git.

> **DEV-INF-004:** Docker images should use pinned base image versions with digest hashes, not `:latest`. Run Trivy scanning on every build.

> **DEV-INF-005:** Cloud Run services should use minimum instances = 0 for cost savings, except latency-critical services (backend API = 1).

> **DEV-INF-006:** BigQuery billing export is automatic in GCP. For AWS/Azure monitoring, configure Cost and Usage Reports (CUR) and Cost Management exports respectively.

> **DEV-INF-007:** See ADR-003 (BigQuery), ADR-004 (Serverless Containers), ADR-006 (Cloud-Native Task Queues) for architectural decisions.

---

## Related ADRs


- [ADR-002: GCP as First Home Cloud](../docs/adr/002-gcp-only-first.md)
- [ADR-003: Use BigQuery, Not TimescaleDB](../docs/adr/003-use-bigquery-not-timescaledb.md)
- [ADR-004: Serverless Containers, Not Kubernetes](../docs/adr/004-cloud-run-not-kubernetes.md)
- [ADR-006: Cloud-Native Task Queues, Not Celery](../docs/adr/006-cloud-native-task-queues-not-celery.md)
- [ADR-008: OTEL Gen-AI Semantic Conventions](../docs/adr/008-otel-gen-ai-conventions.md)
