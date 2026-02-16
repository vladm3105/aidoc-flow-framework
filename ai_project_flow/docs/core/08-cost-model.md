# AI Cost Monitoring — Cost Model & Unit Economics

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 08 — Cost Model & Unit Economics |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Product, Business |

---

## 1. Cost Categories

Running AI Cost Monitoring has four primary cost categories:

```
Platform Operating Cost = Infrastructure + LLM Inference + Cloud API + Operations
```

| Category | Description | Scales With |
|----------|-------------|-------------|
| **Infrastructure** | Compute, database, storage, networking | Number of tenants + data volume |
| **LLM Inference** | Gemini / Claude API calls for agent responses | Number of interactive queries |
| **Cloud API Calls** | AWS/Azure/GCP API calls for data sync + live queries | Number of cloud accounts × sync frequency |
| **Operations** | Monitoring, logging, backup, support | Relatively fixed |

---

## 2. Per-Tenant Cost Model

### 2.0 Single-Tenant / Self-Hosted Deployment

For teams deploying AI Cost Monitoring for **internal use only** (no multi-tenancy), infrastructure can be significantly minimized using a **BigQuery + Firestore** architecture (no PostgreSQL needed).

#### Ultra-Minimal Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE-TENANT STACK                          │
├─────────────────────────────────────────────────────────────────┤
│  Cloud Run (API + Agents)                                       │
│       ↓                                                         │
│  BigQuery ────────── Cost data, analytics, historical recs      │
│  Firestore ───────── Config, users, task progress, messages     │
│  Identity Platform ─ Auth (Google/Microsoft SSO)                │
│  Cloud Logging ───── Agent logs, audit trail                    │
│  Pub/Sub ─────────── Budget alerts, webhooks (optional)         │
│  Secret Manager ──── Cloud credentials                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Ultra-Minimal Infrastructure (GCP)

| Component | Specification | Monthly Cost | Notes |
|-----------|---------------|--------------|-------|
| Cloud Run (all services) | Min instances = 0 | $10-30 | Scales to zero when idle |
| BigQuery | Billing export + config tables | $0-5 | Free tier (1TB queries/mo) |
| Firestore | Config, users, task progress | $0-2 | Free tier (50K reads/day) |
| Identity Platform | Google/MS SSO | $0 | Free tier (50K MAU) |
| Cloud Logging | Agent logs, audit | $0 | Free tier (50GB/mo) |
| Cloud Tasks + Scheduler | Minimal usage | $1 | ~10 scheduled jobs |
| Cloud Storage | < 1GB | $1 | Reports only |
| Secret Manager | ~10 secrets | $1 | Fixed cost |
| **Subtotal (Ultra-Minimal)** | | **$13-40/month** | |

#### Recommended Infrastructure (GCP)

| Component | Specification | Monthly Cost | Notes |
|-----------|---------------|--------------|-------|
| Cloud Run (all services) | Min instances = 1 for API | $30-60 | Faster cold starts |
| BigQuery | Billing export + queries | $5-15 | Moderate usage |
| Firestore | Config, users, tasks | $2-5 | Standard usage |
| Identity Platform | Google/MS SSO | $0 | Free tier (50K MAU) |
| Cloud Logging | Agent logs, audit | $0 | Free tier (50GB/mo) |
| Pub/Sub | Budget alerts, webhooks | $0-2 | Free tier (10GB/mo) |
| Cloud Tasks + Scheduler | Standard usage | $2 | |
| Cloud Storage | 5GB | $2 | Reports + exports |
| Cloud Memorystore Redis | 1GB Basic | $35 | Optional L2 cache |
| Secret Manager | ~20 secrets | $2 | |
| **Subtotal (Recommended)** | | **$78-123/month** | |

#### Data Storage Split

| Data Type | Store In | Why |
|-----------|----------|-----|
| Cost metrics | BigQuery | Native billing export, analytics |
| Historical recommendations | BigQuery | Analytics queries, trends |
| **Users/roles** | Firestore | Fast reads, real-time sync |
| **Cloud accounts config** | Firestore | Configuration data |
| **Policies/thresholds** | Firestore | Frequently accessed settings |
| **Task progress** | Firestore | Real-time updates |
| **Agent messages** | Firestore | Short-lived, streaming |
| **Session state** | Firestore | TTL auto-delete |

#### LLM Costs (Self-Hosted)

| Usage Level | Queries/Month | LLM Cost | Notes |
|-------------|---------------|----------|-------|
| Light | 100 | $0.30 | Occasional queries |
| Moderate | 500 | $1.50 | Daily use |
| Heavy | 2,000 | $6.00 | Power user team |

#### Total Single-Tenant Monthly Cost

| Deployment | Infrastructure | LLM | Cloud APIs | **Total** |
|------------|----------------|-----|------------|-----------|
| **Ultra-Minimal** | $13-40 | $0.30-1.50 | $0.50 | **$14-42/month** |
| **Recommended** | $78-121 | $1.50-6.00 | $2.00 | **$82-129/month** |

> **DEV-COST-007:** For single-tenant deployment, use **GCP Identity Platform** (or Firebase Auth) for authentication. Use Firestore for real-time task progress monitoring and ephemeral agent messages. BigQuery handles all persistent data including user config.

> **DEV-COST-008:** BigQuery has 1-3 second query latency. For the chat UI, use Firestore to stream agent progress in real-time while BigQuery queries run in background. This provides perceived responsiveness.

#### Comparison: Architectures

| Architecture | Monthly Cost | Complexity | Query Latency |
|--------------|--------------|------------|---------------|
| **Ultra-Minimal** (BigQuery + Firestore) | $14-42 | Low | 1-3 sec (BigQuery) |
| **Recommended** (+ Redis) | $82-129 | Medium | <1 sec (cached) |
| **Multi-tenant SaaS** (+ PostgreSQL) | $570-690 | High | <100ms |

---

### 2.1 Infrastructure Cost per Tenant

Shared infrastructure amortized across tenants (GCP serverless example):

| Component | Monthly Cost (100 tenants) | Per Tenant | Notes |
|-----------|---------------------------|------------|-------|
| Cloud Run (all services) | $300-500 | $3.00-5.00 | Pay-per-use, scales to zero |
| Cloud SQL PostgreSQL (db-n1-standard-2) | $100 | $1.00 | Shared, RLS isolated |
| BigQuery (billing export queries) | $10-30 | $0.10-0.30 | Serverless analytics |
| Cloud Tasks + Scheduler | $10 | $0.10 | Serverless background jobs |
| Cloud Storage (reports) | $10 | $0.10 | Per-tenant path |
| Cloud Memorystore Redis (optional) | $40 | $0.40 | 1GB instance for L2 cache |
| Cloud Load Balancing + CDN | $50 | $0.50 | Shared |
| Cloud Monitoring/Logging | $50 | $0.50 | Shared |
| **Subtotal** | **$570-690** | **$5.70-6.90** | |

**Cost advantage:** Serverless saves ~$1,460/month vs Kubernetes ($2,150 - $690 = $1,460).

At scale (500 tenants), per-tenant infrastructure cost drops to ~$2-3/month.

### 2.2 LLM Inference Cost per Tenant

Based on estimated query volume and token usage:

| Metric | Free Tier | Pro Tier | Enterprise Tier |
|--------|-----------|----------|-----------------|
| Queries per month | 100 | 1,000 | 5,000+ |
| Avg input tokens per query | 2,000 | 2,000 | 3,000 |
| Avg output tokens per query | 1,000 | 1,000 | 1,500 |
| LLM model | Gemini 2.0 Flash | Gemini 2.0 Flash | Gemini 2.0 Pro / Claude |

**LLM cost per query** (estimated, Gemini 2.0 Flash pricing):

| Component | Tokens | Cost |
|-----------|--------|------|
| Input (system + context + query) | ~2,000 | ~$0.0003 |
| Output (response) | ~1,000 | ~$0.0006 |
| Multi-agent overhead (2-3 agents per query) | ×3 | ×3 |
| **Total per query** | | **~$0.003** |

**Monthly LLM cost per tenant:**

| Tier | Queries | Cost per Query | Monthly LLM Cost |
|------|---------|---------------|------------------|
| Free | 100 | $0.003 | $0.30 |
| Pro | 1,000 | $0.003 | $3.00 |
| Enterprise | 5,000 | $0.004 (Pro model mix) | $20.00 |

### 2.3 Cloud API Cost per Tenant

Cloud provider API calls for data sync (Mode 2):

| API | Calls per Sync | Syncs per Day | Monthly Calls | Cost per 1K | Monthly Cost |
|-----|---------------|---------------|---------------|-------------|--------------|
| AWS Cost Explorer | 10-50 | 6 | 1,800-9,000 | $0.01 | $0.09 |
| AWS CloudWatch | 50-200 | 6 | 9,000-36,000 | Free tier | $0.00 |
| Azure Cost Management | 10-30 | 6 | 1,800-5,400 | Free | $0.00 |
| GCP Cloud Billing | 10-30 | 6 | 1,800-5,400 | Free | $0.00 |
| **Total per account** | | | | | **~$0.10 - $1.00** |

**Note:** AWS Cost Explorer is the most expensive API at ~$0.01 per request. Other providers have free/low-cost billing APIs. A tenant with 5 AWS accounts ≈ $0.50-5.00/month in cloud API costs.

### 2.4 Total Per-Tenant Cost Summary

| Cost Component | Free Tier | Pro Tier | Enterprise Tier |
|---------------|-----------|----------|-----------------|
| Infrastructure (shared) | $21.50 | $21.50 | $25.00 |
| LLM inference | $0.30 | $3.00 | $20.00 |
| Cloud API calls | $0.50 | $2.00 | $10.00 |
| Operations overhead | $2.00 | $2.00 | $5.00 |
| **Total cost per tenant** | **$24.30** | **$28.50** | **$60.00** |

At scale (500 tenants), infrastructure share drops significantly:

| Cost Component | Free (at scale) | Pro (at scale) | Enterprise (at scale) |
|---------------|-----------------|----------------|----------------------|
| Infrastructure | $8.00 | $10.00 | $15.00 |
| LLM inference | $0.30 | $3.00 | $20.00 |
| Cloud API calls | $0.50 | $2.00 | $10.00 |
| Operations | $1.00 | $1.00 | $3.00 |
| **Total** | **$9.80** | **$16.00** | **$48.00** |

---

## 3. Pricing Tiers

### 3.1 Proposed Pricing

| Feature | Free | Pro ($49/mo) | Enterprise ($199/mo) |
|---------|------|-------------|---------------------|
| Cloud accounts | 1 | 5 | Unlimited |
| Cloud providers | 1 | All 4 | All 4 |
| Interactive queries | 100/mo | 1,000/mo | 5,000/mo |
| Data retention | 90 days | 1 year | 3 years |
| Users | 2 | 10 | Unlimited |
| Scheduled sync | Every 12 hours | Every 4 hours | Every 1 hour |
| Anomaly detection | Basic | Advanced | Advanced + custom |
| Recommendations | View only | View + execute | View + execute + auto |
| Reports | Basic dashboard | PDF + scheduled | Custom + API export |
| A2A Gateway | — | — | ✓ |
| Alert channels | Email only | Email + Slack | All channels |
| SSO | — | — | ✓ |
| Support | Community | Email | Dedicated |

### 3.2 Margin Analysis

| Tier | Price | Cost (at scale) | Gross Margin |
|------|-------|-----------------|--------------|
| Free | $0 | $9.80 | -$9.80 (acquisition cost) |
| Pro | $49 | $16.00 | $33.00 (67%) |
| Enterprise | $199 | $48.00 | $151.00 (76%) |

**Free tier economics:** The free tier is an acquisition channel. Target: 10% conversion to Pro within 3 months. At 10% conversion, the blended acquisition cost is ~$98 per Pro customer ($9.80 × 10 free users).

### 3.3 Breakeven Analysis

| Metric | Value |
|--------|-------|
| Fixed monthly cost (team + infrastructure base) | ~$15,000 (estimated) |
| Breakeven at Pro-only pricing | 455 Pro tenants |
| Breakeven at 70% Pro + 30% Enterprise mix | 165 paid tenants |
| Target Year 1 | 200 paid tenants |

---

## 4. Cost Optimization Levers

### 4.1 LLM Cost Reduction

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| Response caching | 30-40% | Cache identical query results per tenant (Redis L2) |
| Prompt optimization | 15-20% | Reduce system prompt size, use fewer tokens |
| Model routing | 20-30% | Use Flash for simple queries, Pro only for complex |
| Batch processing | 10-15% | Batch Mode 2 agent calls where possible |

### 4.2 Infrastructure Cost Reduction

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| Scale to zero | 40-60% | Cloud Run services scale to 0 during off-peak hours |
| Minimum instances = 0 | 20-30% | Only backend API keeps 1 warm instance |
| BigQuery slot reservations | 30-40% | For predictable query workloads |
| Committed use discounts | 20-30% | 1-year commit for Cloud SQL, Redis |

### 4.3 Cloud API Cost Reduction

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| Adaptive sync frequency | 30-50% | Less frequent sync for low-activity accounts |
| Delta sync | 40-60% | Only query changed data since last sync |
| Aggregated queries | 20-30% | Batch multiple metrics in single API call |

---

## 5. Revenue Projections (Year 1)

### 5.1 Growth Assumptions

| Month | Free Tenants | Pro Tenants | Enterprise Tenants | MRR |
|-------|-------------|-------------|-------------------|-----|
| 1 | 50 | 5 | 0 | $245 |
| 3 | 200 | 25 | 2 | $1,623 |
| 6 | 500 | 75 | 8 | $5,267 |
| 9 | 800 | 150 | 15 | $10,335 |
| 12 | 1,000 | 250 | 30 | $18,220 |

**Year 1 total revenue (cumulative):** ~$100,000 (estimated)

### 5.2 Key Assumptions

- Free → Pro conversion: 10% within 3 months
- Pro → Enterprise upgrade: 5% within 6 months
- Monthly churn: 3% (Free), 2% (Pro), 1% (Enterprise)
- Average cloud accounts per Pro tenant: 3
- Average cloud accounts per Enterprise tenant: 10+

---

## 6. Value Metrics for Customers

The strongest selling point is demonstrable ROI:

| Metric | How We Track It | Customer Impact |
|--------|-----------------|-----------------|
| Total savings identified | Sum of recommendation estimated_savings | "We found $X in savings" |
| Total savings realized | Sum of executed recommendation actual_savings | "You saved $X" |
| Time to insight | Average query response time | "Answers in seconds, not hours" |
| Anomaly detection speed | Time from cost change to alert | "Caught a $5K/day leak in 4 hours" |
| Coverage | % of cloud accounts monitored | "100% visibility across 3 clouds" |

**Target value proposition:** Platform pays for itself within the first month. A single rightsizing recommendation can save more than the annual subscription cost.

---

## Developer Notes

> **DEV-COST-001:** Implement LLM token counting and cost tracking from day one. Store per-query token usage in the query_interactions table. This is essential for monitoring margin per tenant.

> **DEV-COST-002:** The free tier rate limit (100 queries/month) should be enforced at the AG-UI server level with a simple counter in Redis. Show the user their remaining quota in the UI.

> **DEV-COST-003:** Cloud API costs are the hardest to predict because they depend on tenant account size. Implement metering for cloud API calls per tenant to identify outliers that might need usage-based pricing adjustments.

> **DEV-COST-004:** Cloud Run with min instances = 0 is safe for most services because startup time is < 1 second. Only backend API needs min = 1 for low latency. Background jobs via Cloud Tasks automatically retry on failure.

> **DEV-COST-005:** The savings tracking feature (recommendation estimated vs. actual) is the most important business metric. It directly proves platform ROI to customers. Build this measurement pipeline in Phase 5 alongside the self-learning Loop 2.

> **DEV-COST-006:** Consider usage-based pricing as a future option for Enterprise tier — charge per cloud account monitored rather than a flat fee. This aligns cost with value better for large customers with 50+ accounts.
