# AI Cost Monitoring — Database Schema & Data Model

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 01 — Database Schema & Data Model |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Backend Developers |

---

## 1. Storage Strategy

AI Cost Monitoring uses cloud-native storage, each chosen for a specific access pattern:

| Engine | Purpose | Why This Engine |
|--------|---------|-----------------|
| **BigQuery** (GCP) / **Athena+S3** (AWS) / **Synapse** (Azure) | Time-series cost metrics, analytics | Serverless, auto-scaling, native billing export integration, columnar storage for fast aggregation. See [ADR-003](../docs/adr/003-use-bigquery-not-timescaledb.md). |
| **Cloud SQL PostgreSQL 16** (GCP) / **RDS** (AWS) / **Azure Database** (Azure) | Relational data — tenants, users, cloud accounts, recommendations, audit | ACID compliance, Row-Level Security (RLS), managed HA and backups. |
| **Firestore** (GCP) — *single-tenant only* | Configuration, users, task progress, agent messages | Real-time sync, free tier (50K reads/day), no PostgreSQL needed for single-tenant. |
| **Identity Platform** (GCP) | Authentication (Google/Microsoft SSO) | Free tier (50K MAU), replaces Auth0 for single-tenant. |
| **Cloud Logging** (GCP) | Agent logs, audit trail | Free tier (50GB/mo), integrated with Cloud Run. |
| **Pub/Sub** (GCP) — *optional* | Budget alerts, webhook events | Free tier (10GB/mo), decouples event producers and consumers. |
| **Cloud Memorystore Redis** (optional) | L2 query cache | Optional performance optimization for high-traffic deployments. Not required for MVP. |

All storage enforces tenant isolation at the database level — no application-level filtering alone.

---

## 2. Entity Relationship Overview

### Core Entities

```
tenants
  ├── users (many)
  ├── cloud_accounts (many)
  │     ├── cost_metrics (many, time-series)
  │     ├── resources (many)
  │     └── events (many)
  ├── recommendations (many)
  ├── remediation_actions (many)
  ├── anomalies (many)
  ├── reports (many)
  ├── policies (many)
  ├── a2a_agents (many, registered external agents)
  └── audit_log (many, immutable)
```

### Relationship Rules

- Every table except `tenants` itself carries a `tenant_id` foreign key
- All queries are scoped by `tenant_id` through PostgreSQL RLS — no exceptions
- Cross-tenant queries are structurally impossible at the database level
- `audit_log` is append-only — no UPDATE or DELETE operations permitted

---

## 3. Entity Definitions

### 3.1 tenants

The root entity. One tenant = one customer organization.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | String | Organization name |
| slug | String | URL-friendly identifier (unique) |
| auth0_org_id | String | Auth0 Organization ID (unique) |
| plan | Enum | free / pro / enterprise |
| status | Enum | active / suspended / onboarding |
| settings | JSONB | Tenant-specific configuration (alert thresholds, notification preferences, timezone) |
| created_at | Timestamp | |
| updated_at | Timestamp | |

**Business Rules:**
- Created during onboarding workflow
- `auth0_org_id` links to Auth0 Organization for SSO/user management
- `plan` determines rate limits, feature access, data retention period
- `settings` is schema-flexible for per-tenant customization

### 3.2 users

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| auth0_user_id | String | Auth0 user identifier |
| email | String | |
| name | String | |
| role | Enum | super_admin / org_admin / operator / analyst / viewer |
| status | Enum | active / invited / disabled |
| last_login_at | Timestamp | |
| created_at | Timestamp | |

**Business Rules:**
- Role determines which agent tools are accessible (RBAC enforcement)
- `super_admin` is platform-level, all other roles are tenant-scoped
- User creation happens through Auth0 invitation flow, synced to this table

### 3.3 cloud_accounts

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| provider | Enum | aws / azure / gcp / kubernetes |
| account_identifier | String | AWS Account ID / Azure Subscription ID / GCP Project ID / K8s Cluster Name |
| display_name | String | Human-friendly label |
| credential_path | String | Secret Manager path (e.g., GCP: `projects/{project}/secrets/tenant-{id}-aws`) |
| status | Enum | active / disconnected / error / pending_verification |
| last_sync_at | Timestamp | Last successful data sync |
| config | JSONB | Provider-specific settings (regions to monitor, excluded services, etc.) |
| created_at | Timestamp | |

**Business Rules:**
- One tenant can have multiple accounts per provider (e.g., 5 AWS accounts)
- `credential_path` points to home cloud Secret Manager — actual credentials never stored in PostgreSQL
- `status` updated by scheduled sync jobs; `error` triggers notification
- `config.regions` controls which regions the Cloud Agent queries

### 3.4 cost_metrics (Analytics Database - Cloud-Native)

**Storage**: BigQuery (GCP) / Athena + S3 (AWS) / Synapse (Azure)

Time-series cost data from cloud billing exports. This is **not** stored in PostgreSQL.

**GCP (BigQuery)**:
Cloud billing automatically exports to a BigQuery dataset. Query directly:
```sql
SELECT 
  DATE(usage_start_time) as date,
  project.id as project_id,
  service.description as service,
  SUM(cost) as total_cost
FROM `billing_export.gcp_billing_export_v1_*`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND project.id IN (SELECT project_id FROM authorized_projects WHERE tenant_id = @tenant_id)
GROUP BY date, project_id, service
```

**AWS (Athena + S3)**:
Cost and Usage Report (CUR) stored in S3, queried via Athena:
```sql
SELECT 
  line_item_usage_start_date as date,
  line_item_usage_account_id as account_id,
  product_product_name as service,
  SUM(line_item_unblended_cost) as total_cost
FROM cur_database.cur_table
WHERE line_item_usage_start_date >= DATE_ADD('day', -30, CURRENT_DATE)
GROUP BY date, account_id, service
```

**Azure (Synapse Analytics)**:
Cost Management exports to Storage Account, queried via Synapse serverless SQL:
```sql
SELECT 
  usageDate as date,
  subscriptionGuid as subscription_id,
  consumedService as service,
  SUM(cost) as total_cost
FROM OPENROWSET(
  BULK 'https://storage.blob.core.windows.net/exports/*.csv',
  FORMAT = 'CSV'
) AS costs
WHERE usageDate >= DATEADD(day, -30, GETDATE())
GROUP BY date, subscription_id, service
```

**Tenant Isolation**:
- Query filters by authorized project_id/account_id/subscription_id
- List of authorized cloud accounts stored in PostgreSQL `cloud_accounts` table
- MCP servers enforce tenant context before querying

**Performance**:
- Queries cached in Redis (L2) for 5-30 minutes
- Pre-computed daily/monthly rollups for common queries
- Partitioned by date for fast time-range queries

**Note:** Cost metrics are stored in the cloud-native analytics database (BigQuery/Athena/Synapse), **not** in PostgreSQL. The schema above describes the conceptual fields available for querying; the actual implementation uses the billing export schema native to each cloud provider.

**Business Rules:**
- Synced by Mode 2 (Scheduled) — Cloud billing export updated every 4 hours
- Pre-computed rollups (daily/monthly) via scheduled queries or materialized views
- Retention policy: based on tenant plan (free: 90 days, pro: 1 year, enterprise: 3 years)
- Interactive queries (Mode 1) read from pre-computed aggregates for performance

### 3.5 resources

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| cloud_account_id | UUID | FK → cloud_accounts |
| provider | Enum | aws / azure / gcp / kubernetes |
| resource_id | String | Cloud-native resource identifier (ARN, resource ID, etc.) |
| resource_type | String | e.g., "ec2_instance", "azure_vm", "gke_node" |
| region | String | |
| status | Enum | running / stopped / terminated / idle |
| is_idle | Boolean | Flagged by optimization analysis |
| idle_since | Timestamp | When resource was first detected as idle |
| monthly_cost | Decimal | Estimated monthly cost |
| utilization | JSONB | CPU, memory, network, disk metrics |
| tags | JSONB | Cloud provider tags/labels |
| last_seen_at | Timestamp | Last inventory sync that found this resource |
| created_at | Timestamp | |

**Business Rules:**
- Synced by Mode 2 — Resource Inventory job every 6 hours
- `is_idle` set by Anomaly Detection job based on utilization thresholds
- Resources not seen in 2 consecutive syncs are marked `terminated`
- `utilization` stores latest metrics snapshot for quick idle analysis

### 3.6 recommendations

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| cloud_account_id | UUID | FK → cloud_accounts |
| resource_id | UUID | FK → resources (nullable for account-level recs) |
| type | Enum | rightsize / terminate / reserve / schedule / migrate |
| provider | Enum | aws / azure / gcp / kubernetes |
| title | String | Human-readable summary |
| description | Text | Detailed explanation |
| estimated_savings_monthly | Decimal | Projected USD savings per month |
| confidence | Enum | high / medium / low |
| status | Enum | pending / approved / executed / dismissed / expired |
| current_config | JSONB | Current resource configuration |
| recommended_config | JSONB | Proposed configuration |
| approved_by | UUID | FK → users (nullable) |
| executed_at | Timestamp | |
| expires_at | Timestamp | Recommendation validity window |
| created_at | Timestamp | |

**Business Rules:**
- Generated by Mode 2 — Recommendation Refresh job daily at 2 AM
- Also generated reactively by Mode 3 events
- `status` lifecycle: pending → approved → executed OR pending → dismissed
- Expired recommendations are auto-archived after 30 days
- `estimated_savings_monthly` used for ROI tracking and prioritization
- Only `operator` and above roles can approve; `analyst` can dismiss

### 3.7 anomalies

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| cloud_account_id | UUID | FK → cloud_accounts |
| type | Enum | cost_spike / cost_drop / usage_anomaly / new_service / budget_breach |
| severity | Enum | critical / high / medium / low |
| title | String | Summary |
| description | Text | Detailed analysis |
| metric_name | String | What was anomalous |
| expected_value | Decimal | Baseline/predicted value |
| actual_value | Decimal | Observed value |
| deviation_pct | Decimal | Percentage deviation |
| detected_at | Timestamp | When anomaly was flagged |
| resolved_at | Timestamp | When anomaly was resolved (nullable) |
| status | Enum | open / acknowledged / resolved / false_positive |
| related_recommendation_id | UUID | FK → recommendations (nullable) |

**Business Rules:**
- Detected by Mode 2 — Anomaly Detection job every 4 hours
- Also created by Mode 3 — Event-Driven alerts from cloud providers
- `false_positive` feedback feeds back into detection model tuning (self-learning)
- Critical anomalies trigger immediate Mode 3 notifications
- Linked to recommendations when an optimization fix exists

### 3.8 remediation_actions

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| recommendation_id | UUID | FK → recommendations |
| action_type | Enum | resize / stop / terminate / modify / schedule |
| provider | Enum | aws / azure / gcp / kubernetes |
| target_resource_id | String | Cloud resource identifier |
| parameters | JSONB | Action-specific parameters |
| status | Enum | pending_approval / approved / executing / completed / failed / rolled_back |
| requested_by | UUID | FK → users |
| approved_by | UUID | FK → users (nullable) |
| executed_at | Timestamp | |
| completed_at | Timestamp | |
| rollback_data | JSONB | State snapshot for rollback |
| error_message | Text | Failure details (nullable) |
| created_at | Timestamp | |

**Business Rules:**
- Created when user clicks "Execute" on a recommendation
- Approval required based on action risk level and user role
- `rollback_data` captures pre-action state for safe reversal
- Failed actions trigger Mode 3 notification to operator
- All state transitions are audit-logged

### 3.9 events

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| cloud_account_id | UUID | FK → cloud_accounts |
| provider | Enum | aws / azure / gcp / kubernetes |
| event_type | String | Provider-specific event type |
| source | String | CloudWatch / Azure Monitor / GCP Monitoring / Alertmanager |
| severity | Enum | critical / warning / info |
| payload | JSONB | Raw event data from provider |
| processed | Boolean | Whether event processor has handled this |
| action_taken | String | What the platform did in response (nullable) |
| received_at | Timestamp | |
| processed_at | Timestamp | |

**Business Rules:**
- Ingested by Mode 3 — Event-Driven webhook endpoints
- Raw payload preserved for forensics; processed flag prevents re-processing
- High-severity events with `processed = false` trigger alerts after 5-minute timeout

### 3.10 policies

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| name | String | Policy name |
| type | Enum | budget / alert / auto_remediation / scheduling / tagging |
| conditions | JSONB | Rule conditions (thresholds, schedules, tag requirements) |
| actions | JSONB | What to do when triggered (notify, remediate, block) |
| enabled | Boolean | |
| created_by | UUID | FK → users |
| created_at | Timestamp | |
| updated_at | Timestamp | |

**Business Rules:**
- Policies govern Mode 3 event processing behavior
- Auto-remediation policies require `operator` approval to enable
- Budget policies define threshold percentages and notification targets
- Tagging policies enforce required tags on new resources

### 3.11 a2a_agents

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| name | String | Agent display name |
| type | Enum | slackbot / compliance_auditor / vendor_advisor / security_scanner / custom |
| auth_method | Enum | mtls / api_key |
| api_key_hash | String | Hashed API key (nullable) |
| certificate_fingerprint | String | mTLS cert fingerprint (nullable) |
| permissions | JSONB | Allowed tool scopes (e.g., ["read:costs", "read:recommendations"]) |
| rate_limit | Integer | Requests per minute (default: 10) |
| status | Enum | active / suspended / pending_approval |
| registered_by | UUID | FK → users |
| last_request_at | Timestamp | |
| created_at | Timestamp | |

**Business Rules:**
- All external agents must be registered and approved by `org_admin`
- Read-only by default; write permissions require explicit approval
- Rate limit enforced at A2A Gateway level
- Tenant context derived from registration — agent cannot request data for other tenants

### 3.12 audit_log

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| timestamp | Timestamp | Event time |
| event_type | Enum | query / tool_call / remediation / login / config_change / approval / a2a_request |
| actor_type | Enum | user / agent / system / a2a_agent |
| actor_id | String | User ID, agent name, or system identifier |
| action | String | Specific action performed |
| target_type | String | Entity type affected |
| target_id | String | Entity ID affected |
| details | JSONB | Action parameters, results, metadata |
| ip_address | String | Source IP |
| session_id | String | |
| outcome | Enum | success / failure / denied |

**Business Rules:**
- Append-only — no UPDATE or DELETE operations at database level
- 7-year retention for compliance
- Streamed to external SIEM in real-time (Splunk/Datadog)
- Every agent tool call, every remediation action, every login, every config change

### 3.13 reports

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| tenant_id | UUID | FK → tenants |
| type | Enum | executive_summary / chargeback / forecast / custom |
| period | String | e.g., "2026-01", "2026-W05", "2026-Q1" |
| generated_at | Timestamp | |
| storage_path | String | Object storage path (/{tenant_id}/reports/{id}.pdf) |
| parameters | JSONB | Generation parameters (filters, groupings) |
| status | Enum | generating / ready / failed |
| requested_by | UUID | FK → users (nullable for scheduled) |

---

## 4. Pre-Computed Aggregates (Analytics Database)

For performance, create materialized views or scheduled queries for common aggregations:

**GCP (BigQuery Scheduled Queries)**:
```sql
-- Daily rollup (runs every 4 hours)
CREATE OR REPLACE TABLE cost_daily AS
SELECT 
  DATE(usage_start_time) as date,
  project.id as project_id,
  service.description as service,
  SUM(cost) as total_cost
FROM `billing_export.gcp_billing_export_v1_*`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY date, project_id, service;

-- Monthly rollup (runs daily)
CREATE OR REPLACE TABLE cost_monthly AS
SELECT 
  FORMAT_DATE('%Y-%m', DATE(usage_start_time)) as month,
  project.id as project_id,
  service.description as service,
  SUM(cost) as total_cost
FROM `billing_export.gcp_billing_export_v1_*`
GROUP BY month, project_id, service;
```

**AWS (Athena CREATE TABLE AS SELECT)**:
Similar pattern, materialized views updated via Lambda on schedule.

**Azure (Synapse Materialized Views)**:
Use Synapse serverless SQL materialized views or Azure Data Factory pipelines.

Pre-computed rollups that make Mode 1 interactive queries fast:

| Aggregate | Source | Grouping | Refresh |
|-----------|--------|----------|---------|
| `cost_daily` | cost_metrics | tenant, account, provider, service, region, day | Every 4 hours (after sync) |
| `cost_monthly` | cost_daily | tenant, account, provider, service, month | Daily at 4 AM |
| `cost_by_tag_daily` | cost_metrics | tenant, tag_key, tag_value, day | Daily at 4 AM |
| `resource_utilization_daily` | cost_metrics | tenant, resource_type, provider, day | Every 6 hours |

**Why this matters:** When a user asks "What's our monthly AWS spend?", the query hits `cost_monthly` (pre-computed) instead of scanning millions of hourly rows.

---

## 5. Redis Key Namespace Design (Optional L2 Cache)

**Note**: Redis is **optional** for performance optimization. Not required for MVP.

If using Redis for L2 caching, all keys are namespaced by tenant to prevent cross-tenant data leakage:

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `tenant:{id}:cost:summary:{params_hash}` | 30 min | Cost summary query results |
| `tenant:{id}:recommendations:{cloud}:{account}` | 1 hour | Cloud provider recommendations |
| `tenant:{id}:resources:{cloud}:{account}` | 30 min | Resource inventory snapshot |
| `tenant:{id}:session:{session_id}` | 30 min | User session data (CopilotKit conversation) |

**No task queue keys** - Background jobs use cloud-native services (Cloud Tasks/SQS/Service Bus per ADR-006).

| Pattern | Purpose | TTL |
|---------|---------|-----|
| `tenant:{id}:cache:costs:{hash}` | L2 cost query cache | 5 min |
| `tenant:{id}:cache:resources:{hash}` | L2 resource query cache | 15 min |
| `tenant:{id}:cache:recommendations` | L2 recommendations cache | 30 min |
| `tenant:{id}:session:{session_id}` | User session data | 24 hours |
| `tenant:{id}:ratelimit:{user_id}` | Per-user rate limiting counter | 1 hour |
| `tenant:{id}:ratelimit:a2a:{agent_id}` | Per-agent A2A rate limiting | 1 min |
| `tenant:{id}:lock:sync:{provider}` | Distributed lock for sync jobs | 30 min |
| `tenant:{id}:events:queue` | Event processing queue | Until consumed |
| `global:ratelimit:cloud:{provider}` | Cloud API rate limit tracking | 1 sec |

---

## 6. Row-Level Security (RLS) Strategy

Every table with `tenant_id` has RLS policies enforced at the database level:

| Layer | Mechanism | Description |
|-------|-----------|-------------|
| **PostgreSQL RLS** | `SET app.current_tenant = '{tenant_id}'` | Set per-connection from JWT org_id |
| **BigQuery Views** | Query filters by authorized `project_id`/`account_id` | Authorized accounts stored in PostgreSQL `cloud_accounts` table |
| **Redis Namespacing** (optional) | Key prefix `tenant:{id}:*` | Application-level, enforced by MCP servers |
| **Object Storage** | Path isolation `/{tenant_id}/` | Bucket policy per tenant prefix |
| **Secret Manager** | Path/name isolation (cloud-specific) | IAM/RBAC policy per tenant |

**The guarantee:** Even if application code has a bug, the database will not return another tenant's data.

---

## 7. Data Retention & Lifecycle

| Data Type | Hot (Fast Query) | Warm (Compressed) | Cold (Archive) | Delete |
|-----------|-----------------|-------------------|----------------|--------|
| cost_metrics (hourly) | 7 days | 90 days | 1 year | Per plan |
| cost_daily aggregate | 90 days | 1 year | 3 years | Per plan |
| cost_monthly aggregate | Forever | — | — | Never |
| resources | Current state | — | — | 30 days after terminated |
| recommendations | Active | — | Archived after 30 days | 1 year |
| anomalies | 90 days | 1 year | — | 3 years |
| audit_log | 90 days | 1 year | 7 years | Never (compliance) |
| events | 30 days | 90 days | — | 1 year |

---

## Developer Notes

> **DEV-DB-001:** BigQuery billing export is automatic in GCP. For AWS/Azure, configure Cost and Usage Reports (CUR) and Cost Management exports respectively. Query costs are pay-per-scan; use materialized views to reduce scan volume.

> **DEV-DB-002:** RLS must be tested with a dedicated integration test suite that attempts cross-tenant reads. This is a security-critical path — every new table needs an RLS policy before it goes to production.

> **DEV-DB-003:** Redis L2 cache is optional. If used, key TTLs in the table above are starting points. Tune based on actual query patterns after beta launch. The L2 cache hit ratio target is >80%.

> **DEV-DB-004:** The `audit_log` table should be partitioned by month for query performance. Consider using pg_partman for automatic partition management.

> **DEV-DB-005:** JSONB fields (`settings`, `config`, `tags`, `payload`, `details`) should have GIN indexes for queries that filter on specific JSON keys. Don't index all JSONB fields — only the ones that appear in WHERE clauses.

> **DEV-DB-006:** BigQuery handles cost data storage efficiently. Estimate ~500K rows per cloud account per month at hourly granularity. Use table partitioning by date and clustering for query performance.
