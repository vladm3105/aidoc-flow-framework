# AI Cost Monitoring

## Project Overview

**AI Cost Monitoring** is an enterprise-grade, multi-cloud FinOps platform that leverages AI agents to provide intelligent cost analysis, optimization recommendations, and automated remediation across AWS, Azure, GCP, and Kubernetes environments.

The platform uses a hierarchical multi-agent architecture built on Google ADK (Agent Development Kit), enabling natural language interactions for cloud cost management with real-time streaming UI responses.

---

## Key Features

### 🤖 Intelligent AI Agents
- **Natural Language Interface** - Ask questions like "Why did our AWS bill spike last week?" or "Show me idle resources across all clouds"
- **Multi-Agent Orchestration** - Specialized agents collaborate to handle complex queries
- **Context-Aware Responses** - Agents understand tenant context, user roles, and permissions

### 💰 Cost Management
- **Unified Cost View** - Single dashboard for AWS, Azure, GCP, and Kubernetes costs
- **Real-Time Cost Tracking** - Live cost data with anomaly detection
- **Budget Alerts** - Proactive notifications when spending exceeds thresholds
- **Cost Allocation** - Tag-based cost attribution by team, project, or environment

### ⚡ Optimization
- **Rightsizing Recommendations** - AI-powered instance sizing suggestions
- **Idle Resource Detection** - Identify and flag unused resources
- **Reserved Instance Planning** - Savings plan optimization
- **Cross-Cloud Arbitrage** - Compare pricing across cloud providers

### 🔧 Automated Remediation
- **One-Click Actions** - Execute optimizations directly from the UI
- **Approval Workflows** - Role-based approval chains for sensitive actions
- **Scheduled Operations** - Automate resource start/stop schedules
- **Rollback Capability** - Safely revert changes if needed

### 📊 Reporting & Forecasting
- **Cost Forecasting** - ML-powered spend predictions
- **Executive Dashboards** - High-level summaries for leadership
- **Team Chargeback** - Department-level cost reports
- **Export & Integration** - PDF reports, Slack notifications, API access

---

## Architecture

### 4-Layer Hierarchical Agent Design

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: COORDINATOR AGENT                                  │
│  Intent classification • Routing • A2UI rendering            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  LAYER 2: DOMAIN AGENTS (6 Agents)                           │
│  Cost • Optimization • Remediation • Reporting • Tenant      │
│  Cross-Cloud                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  LAYER 3: CLOUD PROVIDER AGENTS (4 Agents)                   │
│  AWS Agent • Azure Agent • GCP Agent • Kubernetes Agent      │
│  Each owns its MCP server exclusively                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│  LAYER 4: MCP SERVERS (8 Servers)                            │
│  AWS MCP • Azure MCP • GCP MCP • OpenCost MCP                │
│  Forecast MCP • Remediation MCP • Policy MCP • Tenant MCP    │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Benefits

| Benefit | Description |
|---------|-------------|
| **Parallel Execution** | Cloud agents query all providers simultaneously |
| **Clean Separation** | Domain logic separated from cloud-specific implementation |
| **Better Caching** | Per-cloud credential and response caching |
| **Fault Isolation** | One cloud failure doesn't affect others |
| **Scalability** | Add new cloud providers without changing domain logic |

---

## Technology Stack

### Frontend
- **Next.js 14** - React framework
- **CopilotKit** - AI chat interface with AG-UI protocol
- **A2UI Components** - Real-time streaming UI components
- **Tailwind CSS + shadcn/ui** - Styling
- **Auth0 React SDK** - Authentication

### Agent Layer
- **Google ADK** - Agent Development Kit
- **Google A2A Protocol** - Agent-to-Agent communication
- **Gemini 2.0 / Claude** - LLM backbone
- **AG-UI Protocol** - Agent-to-UI streaming

### Backend Infrastructure:
- **Serverless Containers (Cloud Run / ECS Fargate / Azure Container Apps)** - All services
- **Cloud-native Task Queues (Cloud Tasks / SQS / Service Bus)** - Background jobs
- **Cloud Scheduler (GCP) / EventBridge (AWS) / Azure Functions** - Job scheduling

**Backend Data:**
- **PostgreSQL** - Relational data (tenants, users, accounts, policies)
- **BigQuery / Athena / Synapse** - Time-series cost metrics (billing export)
- **Redis** (optional) - L2 query cacheage for reports

### Authentication & Security
- **Auth0** - Identity provider (OAuth 2.0/OIDC, SSO, MFA)
- **GCP Secret Manager / AWS Secrets Manager / Azure Key Vault** - Cloud-native secrets management
- **JWT/OIDC** - Token-based authentication
- **RBAC** - Role-based access control

### Data Layer
- **Cloud SQL PostgreSQL 16** (GCP) / **RDS** (AWS) / **Azure Database** - Relational data with Row-Level Security
- **BigQuery** (GCP) / **Athena+S3** (AWS) / **Synapse** (Azure) - Time-series cost metrics (billing export)
- **Cloud Memorystore Redis** (optional) - L2 query cache
- **Cloud Storage / S3 / Blob** - Object storage for reports

### Infrastructure
- **Serverless Containers** (Cloud Run / ECS Fargate / Azure Container Apps) - No cluster management
- **Terraform** - Infrastructure as Code
- **Cloud Monitoring** (GCP) / **CloudWatch** (AWS) / **Azure Monitor** - Observability
- **Cloud Trace / X-Ray / App Insights** - Distributed tracing

---

## Operational Modes

AI Cost Monitoring operates in **four distinct modes** that work together to provide comprehensive cloud cost management:

### Mode 1: Interactive (User-Driven, On-Demand)

The conversational AI interface where users ask natural language questions and receive real-time streaming responses.

**Flow:** User → CopilotKit → AG-UI Server → Coordinator → Domain Agent → Cloud Agents (parallel) → MCP Servers → Cloud APIs → Aggregate → Stream A2UI Response

**Characteristics:**
- Trigger: User action (natural language query)
- Latency: 2-5 seconds (parallel cloud queries)
- Data source: Local DB (pre-synced by Mode 2), with fallback to live API calls
- Auth: JWT + Tenant Context per request

**Examples:**
- "Why did our AWS bill increase by 40% last month?"
- "Show me all idle resources across clouds"
- "Compare our GCP vs Azure compute costs"

### Mode 2: Scheduled (Background Pipeline)

Automated data pipeline that runs continuously, keeping the local database fresh so interactive queries return instant results.

**Flow:** Cloud Scheduler → Cloud Tasks → Serverless Function → Cloud APIs → Data Processing → BigQuery (cost data) / PostgreSQL (metadata) / Redis (cache)

**Schedule:**

| Job | Frequency | Purpose |
|-----|-----------|---------|
| Cost Data Sync | Every 4 hours | Pull latest cost metrics from all clouds |
| Resource Inventory | Every 6 hours | Discover new/terminated resources |
| Anomaly Detection | Every 4 hours (after sync) | Flag spending spikes and deviations |
| Recommendation Refresh | Daily at 2 AM | Recalculate optimization suggestions |
| Forecast Update | Daily at 3 AM | Re-run ML spend prediction models |
| Report Generation | Weekly / Monthly | Executive summaries, chargeback reports |
| Credential Rotation Check | Daily at midnight | Verify Secret Manager credential health |
| Data Rollup / Compress | Daily at 4 AM | Aggregate old data, refresh BigQuery materialized views |

**Characteristics:**
- Trigger: Cron schedule (Cloud Scheduler / EventBridge)
- Runs 24/7 per tenant, no user action needed
- Credentials from **Secret Manager**
- Results feed all other modes

### Mode 3: Event-Driven (Reactive, Real-Time)

Real-time response to events happening in cloud environments, delivered via webhooks from cloud provider monitoring systems.

**Flow:** Cloud Event → Webhook Endpoint → Event Processor → Evaluate Policies → Notify / Recommend / Auto-Remediate

**Event Sources:**

| Cloud | Mechanism | Events |
|-------|-----------|--------|
| AWS | CloudWatch Alarms → SNS → Webhook | Budget threshold, anomaly, instance state change |
| Azure | Azure Monitor → Action Group → Webhook | Budget alerts, Advisor recommendations, resource health |
| GCP | Cloud Monitoring → Pub/Sub → Push | Budget notifications, billing anomaly, quota warnings |
| Kubernetes | Prometheus Alertmanager → Webhook | Pod OOM, node pressure, namespace quota exceeded |

**Threshold Actions:**
- Below threshold: Log and store (no action)
- Above threshold:
  - Send notification (Slack / Email / PagerDuty)
  - Create recommendation
  - Auto-remediate (if tenant policy allows)

### Mode 4: A2A — Agent-to-Agent (External Agent-Initiated)

External AI agents initiate queries through the Google A2A Protocol gateway. This is functionally similar to Mode 1 but initiated by another AI agent rather than a human user.

**Flow:** External Agent → A2A Gateway → Auth Check (mTLS/API Key) → Coordinator → Domain Agents → Cloud Agents → Response

**External Agent Types:**
- **SlackBot Agent** — Team members ask cost questions in Slack
- **Compliance Auditor** — Nightly policy violation scans
- **Vendor Advisor** — Periodically checks for new savings opportunities
- **Security Scanner** — Cost-related security checks

**Security Controls:**
- All external agents must be pre-registered and approved by tenant admin
- Read-only permissions by default (no write/execute)
- Rate limited: 10 requests/min per external agent
- Tenant context determined by agent registration (cannot specify arbitrary tenant)

### How All Modes Work Together

A real-world example demonstrating all four modes:

1. **Mode 2 (Scheduled, 2:00 AM):** Data Collector syncs AWS costs. Anomaly Detector flags a 40% spend increase on EC2 in us-east-1. Stores anomaly and generates recommendations in database.

2. **Mode 3 (Event-Driven, 7:30 AM):** AWS Budget alarm fires at 80% threshold. Webhook received, Event Processor evaluates against tenant policy, threshold exceeded. Slack alert sent to Org Admin and finance team.

3. **Mode 1 (Interactive, 9:00 AM):** Admin opens AI Cost Monitoring, asks "Why did our AWS spend spike?" Agent instantly has data from Mode 2 plus the anomaly already flagged. Shows 12 over-provisioned instances with one-click remediation.

4. **Remediation (9:05 AM):** Admin clicks "Rightsize all 12." Approval workflow triggers. Operator approves. AWS Agent executes via MCP. All actions audit logged.

**Result:** $12,400/month savings identified and applied — all modes contributed.

---

## Multi-Tenant Architecture

### Tenant Isolation Model

```
┌─────────────────────────────────────────────────────────────┐
│  DATA ISOLATION                                              │
│  • PostgreSQL RLS on tenant_id                               │
│  • BigQuery filters by authorized cloud accounts             │
│  • Redis namespacing: tenant:{id}:* (optional L2 cache)      │
│  • Object storage path isolation: /{tenant_id}/              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  CREDENTIAL ISOLATION                                        │
│  • Secret Manager paths: tenant-{id}-{provider}-{account}    │
│  • Per-tenant cloud credentials                              │
│  • Dynamic credential injection per request                  │
│  • 90-day automatic rotation                                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ACCESS CONTROL                                              │
│  • Auth0 Organizations for tenant management                 │
│  • RBAC with 5 roles: Super Admin → Org Admin → Operator     │
│    → Analyst → Viewer                                        │
│  • Permission-based tool access                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Features

### Authentication
- **Single Sign-On (SSO)** - Google, Microsoft, Okta, SAML
- **Multi-Factor Authentication (MFA)** - TOTP, WebAuthn
- **Session Management** - Secure token handling with refresh

### Authorization
- **Role-Based Access Control (RBAC)** - Granular permissions
- **Permission Enforcement** - Every API call validated
- **Approval Workflows** - Multi-level approval for sensitive actions

### Data Protection
- **Encryption at Rest** - AES-256 for all stored data
- **Encryption in Transit** - TLS 1.3 for all communications
- **Secrets Management** - Cloud-native secrets services with auto-rotation

### Compliance
- **Audit Logging** - Immutable 7-year retention
- **SOC 2 Ready** - Security controls aligned
- **GDPR Compliant** - Data privacy controls

---

## Integration Capabilities

### Cloud Providers
| Provider | Integration Method | Capabilities |
|----------|-------------------|--------------|
| **AWS** | IAM AssumeRole | Cost Explorer, Compute Optimizer, Trusted Advisor, CloudWatch |
| **Azure** | Service Principal | Cost Management, Advisor, Resource Graph, Monitor |
| **GCP** | Service Account | Cloud Billing, Recommender, Asset Inventory, Monitoring |
| **Kubernetes** | Kubeconfig | OpenCost, VPA/HPA, Resource Metrics |

### External Systems
- **Slack** - Notifications and bot integration
- **Email** - Alerts and reports
- **PagerDuty** - Incident escalation
- **JIRA** - Ticket creation for remediation
- **Webhooks** - Custom integrations

### A2A Gateway (Agent-to-Agent)
- **External Agent Integration** - Connect third-party AI agents
- **SlackBot Agents** - Conversational cost queries
- **Compliance Auditors** - Automated policy checks
- **Vendor Advisors** - Cost optimization recommendations

---

## User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Super Admin** | Platform administrator | Full system access |
| **Org Admin** | Tenant administrator | Manage users, roles, cloud accounts |
| **Operator** | Operations team | Execute remediation actions |
| **Analyst** | Finance/FinOps team | View costs, create reports |
| **Viewer** | Read-only access | View dashboards only |

---

## Sample Use Cases

### 1. Cost Investigation
```
User: "Why did our AWS bill increase by 40% last month?"

AI Cost Monitoring:
→ Coordinator routes to Cost Agent
→ Cost Agent delegates to AWS Agent
→ AWS Agent queries Cost Explorer via MCP
→ Returns breakdown with anomaly detection
→ Renders interactive A2UI chart with drill-down
```

### 2. Optimization Discovery
```
User: "Find all idle resources across our cloud accounts"

AI Cost Monitoring:
→ Coordinator routes to Optimization Agent
→ Optimization Agent fans out to all Cloud Agents (parallel)
→ Each Cloud Agent queries its MCP for idle resources
→ Results aggregated and ranked by savings potential
→ Renders A2UI recommendation cards with one-click actions
```

### 3. Automated Remediation
```
User: "Stop all dev EC2 instances every night at 8 PM"

AI Cost Monitoring:
→ Coordinator routes to Remediation Agent
→ Remediation Agent creates scheduled workflow
→ Requires Operator role approval
→ Temporal.io manages execution schedule
→ AWS Agent executes stop commands via MCP
→ Audit log captures all actions
```

---

## Project Metrics

| Metric | Value |
|--------|-------|
| **Total Agents** | 11 |
| **Domain Agents** | 6 |
| **Cloud Agents** | 4 |
| **MCP Servers** | 8 |
| **Cloud Providers** | 4 (AWS, Azure, GCP, K8s) |
| **RBAC Roles** | 5 |
| **Development Timeline** | ~9 months |

---

## Development Phases

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 1** | 5 weeks | Foundation (Auth0, Secret Manager, PostgreSQL, Redis) |
| **Phase 2** | 5 weeks | MCP Servers (AWS, Azure, GCP, OpenCost) |
| **Phase 3** | 5 weeks | Cloud Agents (AWS, Azure, GCP, K8s) |
| **Phase 4** | 5 weeks | Domain Agents (Cost, Optimization, Remediation) |
| **Phase 5** | 4 weeks | AG-UI/A2UI Integration |
| **Phase 6** | 4 weeks | Multi-Tenant & A2A Gateway |
| **Phase 7** | 4 weeks | Security Hardening |
| **Phase 8** | 4 weeks | Testing & Documentation |

---

## Deliverables

### Architecture Documents
1. **finops-architecture-final.svg** - Main system architecture (4-layer hierarchy)
2. **finops-auth-flow.svg** - Authentication flow diagram
3. **finops-agent-a2ui-flow.svg** - AG-UI streaming sequence
4. **finops-agent-mcp-detail.svg** - MCP server specifications
5. **ai-cost-monitoring-operational-modes.svg** - Operational modes and interactions

### Review Documents
6. **ai-cost-monitoring-review.md** - Performance & security recommendations
7. **ai-cost-monitoring-description.md** - Project description (this document)

---

## Contact

**Project:** AI Cost Monitoring  
**Version:** 1.0  
**Date:** January 2026

---

*AI Cost Monitoring - Intelligent Multi-Cloud Cost Management*
