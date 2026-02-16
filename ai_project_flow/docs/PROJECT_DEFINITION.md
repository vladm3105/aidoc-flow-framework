# AI Cloud Cost Monitoring — Project Definition

**Document:** PROJECT_DEFINITION.md
**Version:** 1.0.0
**Date:** {DATE}
**Status:** Approved

---

## Strategic Context

This project definition describes a standalone FinOps platform. Within TechTrend's AI Operations strategy, this specification serves as the **Phase 3 productization blueprint** — to be implemented only if the decision gate at month 24+ passes. See the [ai-factory](https://{GITHUB_HOST}/{GITHUB_ORG}/ai-factory) repo for the authoritative strategy:

- [ADR-002: AI Operations Monitoring Strategy](https://{GITHUB_HOST}/{GITHUB_ORG}/ai-factory/blob/main/docs/adr/ADR-002-AI-Operations-Monitoring-Strategy.md)
- [Unified Roadmap](https://{GITHUB_HOST}/{GITHUB_ORG}/ai-factory/blob/main/docs/strategy/UNIFIED-ROADMAP-AI-Ops.md)

---

## Executive Summary

**AI Cloud Cost Monitoring** is an AI-agent-powered FinOps platform that provides intelligent cloud cost analysis, optimization recommendations, and automated remediation across AWS, Azure, GCP, and Kubernetes.

**Core Differentiator:** The platform uses **AI agents with MCP (Model Context Protocol) servers** as the primary integration pattern—not traditional REST API calls. Users interact with the system through natural language, and AI agents orchestrate all cloud operations.

---

## Project Purpose

### Problem Statement

Organizations face challenges with multi-cloud cost management:

| Challenge | Impact |
|-----------|--------|
| Fragmented visibility | Costs scattered across AWS, Azure, GCP consoles |
| Manual analysis | Time-consuming, requires deep expertise |
| Reactive optimization | Issues discovered after budget overruns |
| No unified interface | Different tools for different clouds |

### Solution

An AI-driven platform where:

1. **Users ask questions in natural language** → "Why did AWS costs spike last week?"
2. **AI agents analyze and respond** → Coordinator routes to specialized agents
3. **Agents use MCP tools** → Not REST APIs, but AI-native MCP protocol
4. **Real-time streaming UI** → Progressive updates as agents work

---

## Architecture Philosophy

### AI Agents as First-Class Citizens

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                     Natural Language Chat (CopilotKit)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AI AGENT LAYER (5 Agents)                               │
│                                                                              │
│  ┌─────────────────┐                                                        │
│  │   COORDINATOR   │ ← Single entry point, intent classification            │
│  └────────┬────────┘   Routes directly to MCP servers                       │
│           │                                                                  │
│  ┌────────┴────────────────────────────────────────────────────────────┐   │
│  │                      DOMAIN AGENTS (4)                               │   │
│  │                                                                      │   │
│  │  Cost Agent        → Analysis, forecasting, optimization, reporting  │   │
│  │  Remediation Agent → Action decisions, executes via MCP              │   │
│  │  Cross-Cloud Agent → Multi-cloud data aggregation                    │   │
│  │  Tenant Agent      → (Phase 7 only - multi-tenancy)                  │   │
│  │                                                                      │   │
│  └────────┬────────────────────────────────────────────────────────────┘   │
│           │  Agents call MCP servers directly (no Cloud Agent layer)        │
└───────────┼─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MCP SERVER LAYER (Data Access Only)                      │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   AWS MCP   │  │  Azure MCP  │  │   GCP MCP   │  │ OpenCost MCP│        │
│  │  (native)   │  │  (native)   │  │  (native)   │  │  (custom)   │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │                │
│  Architecture: MCP servers provide DATA ACCESS only.                        │
│  AI Agents (Layer 2) handle forecasting, remediation, and policy logic.     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CLOUD PROVIDER APIs                                  │
│       AWS Cost Explorer │ Azure Cost Management │ GCP Billing │ OpenCost    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MCP Servers — Not REST APIs

**Why MCP instead of REST?**

| Aspect | REST API | MCP Server |
|--------|----------|------------|
| Designed for | Web applications | AI agents |
| Schema | OpenAPI (manual) | Auto-generated from code |
| State | Session-based | Stateless, cacheable |
| Error handling | HTTP status codes | Structured error envelopes |
| AI integration | Requires wrapper | Native tool calling |

**MCP Server Strategy:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MCP SERVER SOURCING                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  OPTION 1: Provider-Native MCP Servers (Preferred)                          │
│  ────────────────────────────────────────────────                           │
│  When cloud providers offer official MCP servers, use them directly:        │
│  • Maintained by provider                                                   │
│  • Automatic API updates                                                    │
│  • Official support                                                         │
│                                                                              │
│  OPTION 2: Custom-Developed MCP Servers (Fallback)                          │
│  ─────────────────────────────────────────────────                          │
│  When no provider MCP exists, we build our own:                             │
│  • Wrap provider REST APIs in MCP protocol                                  │
│  • Use FastMCP framework                                                    │
│  • Maintain parity across all cloud MCP servers                             │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  MCP Servers (4 total) - Data Access Only:                           │   │
│  │                                                                       │   │
│  │  AWS MCP     → Native (@awslabs/mcp-server-aws-core, GA Jan 2026)    │   │
│  │  Azure MCP   → Native (Azure.Mcp.Server, GA in VS 2026)              │   │
│  │  GCP MCP     → Native (gcloud-mcp + BigQuery MCP, GA)                │   │
│  │  OpenCost MCP→ Custom (wraps OpenCost API for Kubernetes)            │   │
│  │                                                                       │   │
│  │  AI Agents handle (not MCP):                                         │   │
│  │  • Forecasting    → Cost Agent analyzes data, makes predictions      │   │
│  │  • Remediation    → Remediation Agent decides and executes actions   │   │
│  │  • Policy logic   → Domain Agents evaluate rules                     │   │
│  │  • Tenant mgmt    → Backend service / Tenant Agent                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Unified MCP Tool Contracts

All cloud MCP servers implement identical tool signatures for agent interoperability:

```python
# Every cloud MCP server exposes these tools:
tools = [
    "get_costs",           # Retrieve cost data with filters
    "get_resources",       # List cloud resources
    "get_recommendations", # Fetch optimization recommendations
    "execute_remediation", # Perform corrective actions
    "get_budget_status",   # Check budget thresholds
    "get_forecast",        # Predict future costs
    "get_usage_metrics",   # Resource utilization data
    "compare_periods",     # Period-over-period analysis
]
```

---

## Infrastructure Architecture

### Home Cloud vs Monitored Clouds

| Concept | Definition | Current Choice |
|---------|------------|----------------|
| **Home Cloud** | Where platform infrastructure runs | GCP |
| **Monitored Clouds** | What clouds the platform analyzes | AWS, Azure, GCP, Kubernetes |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOME CLOUD: GCP                                      │
│              (Platform Infrastructure - AI Agents Run Here)                  │
│                                                                              │
│  Cloud Run (Agents + MCP Servers) │ BigQuery │ Firestore │ Secret Manager   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       │ AI Agents query via MCP
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        ▼                              ▼                              ▼
┌───────────────┐             ┌───────────────┐             ┌───────────────┐
│     AWS       │             │    AZURE      │             │  KUBERNETES   │
│  (Monitored)  │             │  (Monitored)  │             │  (Monitored)  │
│               │             │               │             │               │
│ Cost Explorer │             │Cost Management│             │   OpenCost    │
│ Compute Opt.  │             │    Advisor    │             │   Metrics     │
└───────────────┘             └───────────────┘             └───────────────┘

        ▲
        │
┌───────────────┐
│     GCP       │  ◄── GCP is BOTH home cloud AND monitored
│  (Monitored)  │
│               │
│ Billing Export│
│  Recommender  │
└───────────────┘
```

---

## Operational Modes

The platform operates in **four distinct modes** that work together:

### Mode 1: Interactive (On-Demand via UX)

User-driven queries through natural language chat interface.

```text
User Query → CopilotKit → AG-UI Server → Coordinator Agent
                                              │
                                              ▼
                                        Domain Agents
                                              │
                                              ▼
                                    Cloud Agents (parallel)
                                              │
                                              ▼
                                        MCP Servers
                                              │
                                              ▼
                                        Cloud APIs
                                              │
                                              ▼
                                   Streaming Response (A2UI)
```

**Characteristics:**
- Trigger: User action (natural language query)
- Latency: 2-5 seconds
- Data source: Pre-synced local DB (from Mode 2), fallback to live API
- Examples: "Why did AWS costs spike?", "Show idle resources"

### Mode 2: Scheduled (Background Data Export)

Automated pipeline that syncs cloud data on schedule, keeping local database fresh.

```text
Cloud Scheduler → Cloud Tasks → Sync Service → Cloud APIs
                                                    │
                                                    ▼
                                    BigQuery (cost data)
                                    Firestore (metadata)
```

**Schedule:**

| Job | Frequency | Purpose |
|-----|-----------|---------|
| Cost Data Sync | Every 4 hours | Pull latest cost metrics |
| Resource Inventory | Every 6 hours | Discover resources |
| Anomaly Detection | Every 4 hours | Flag spending spikes |
| Recommendation Refresh | Daily 2 AM | Recalculate optimizations |
| Forecast Update | Daily 3 AM | ML spend predictions |

**Why This Mode Exists:**
- Cloud billing APIs have 4-24 hour data delay
- Pre-syncing enables instant interactive responses
- Reduces API calls and costs

### Mode 3: Event-Driven (Push Alerts from Clouds)

Real-time response to cloud provider alerts via webhooks.

```text
Cloud Event → Webhook Endpoint → Event Processor → Policy Check
                                                        │
                                          ┌─────────────┴─────────────┐
                                          ▼                           ▼
                                    Notification              Auto-Remediate
                                  (Slack/Email)              (if policy allows)
```

**Event Sources:**

| Cloud | Mechanism | Events |
|-------|-----------|--------|
| AWS | CloudWatch → SNS → Webhook | Budget threshold, anomaly |
| Azure | Azure Monitor → Action Group | Budget alerts, Advisor |
| GCP | Cloud Monitoring → Pub/Sub | Budget notifications |
| K8s | Prometheus Alertmanager | Pod OOM, quota exceeded |

### Mode 4: A2A (Agent-to-Agent Requests)

External AI agents initiate queries through A2A Protocol gateway.

```text
External Agent → A2A Gateway → Auth Check (mTLS/API Key)
                                        │
                                        ▼
                              Coordinator Agent
                                        │
                                        ▼
                              (Same flow as Mode 1)
```

**External Agent Types:**
- SlackBot Agent — Team cost questions in Slack
- Compliance Auditor — Nightly policy scans
- Vendor Advisor — Savings opportunity checks

**Security:**
- Pre-registered agents only
- Read-only by default
- Rate limited: 10 req/min per agent

### How Modes Work Together

```text
Example Scenario: AWS Cost Spike

1. MODE 2 (2:00 AM): Scheduled sync detects 40% EC2 cost increase
   └── Stores anomaly in database, generates recommendations

2. MODE 3 (7:30 AM): AWS Budget alarm fires at 80% threshold
   └── Webhook received, Slack alert sent to finance team

3. MODE 1 (9:00 AM): Admin asks "Why did AWS costs spike?"
   └── Agent instantly has data from Mode 2 + anomaly flagged
   └── Shows 12 over-provisioned instances with one-click fix

4. REMEDIATION: Admin clicks "Rightsize all 12"
   └── Approval workflow triggers, operator approves
   └── AWS Agent executes via MCP, audit logged

Result: $12,400/month savings — all modes contributed
```

---

## User Interaction Model

### AI-First Interface

Users interact with the platform through natural language:

```
User: "Why did our AWS costs increase 40% last month?"

┌─────────────────────────────────────────────────────────────────────────────┐
│ COORDINATOR AGENT                                                            │
│ → Classifies intent: cost_analysis                                          │
│ → Routes to: Cost Agent                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ COST AGENT                                                                   │
│ → Needs AWS-specific data                                                   │
│ → Delegates to: AWS Agent                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ AWS AGENT                                                                    │
│ → Calls MCP tools: get_costs(), compare_periods()                           │
│ → Uses: AWS MCP Server                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ AWS MCP SERVER                                                               │
│ → Retrieves credentials from Secret Manager                                 │
│ → Calls AWS Cost Explorer API                                               │
│ → Returns structured cost data                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ RESPONSE (Streaming via AG-UI)                                               │
│                                                                              │
│ "Your AWS costs increased 40% ($12,400 → $17,360) primarily due to:         │
│  1. EC2 instances: +$3,200 (new production cluster launched 2/15)           │
│  2. S3 storage: +$1,100 (video assets bucket grew 2TB)                      │
│  3. Data transfer: +$660 (API traffic spike during campaign)                │
│                                                                              │
│  Recommendations:                                                            │
│  • Consider Reserved Instances for the new EC2 cluster (save ~$800/mo)      │
│  • Enable S3 Intelligent Tiering for video assets (save ~$200/mo)"          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dual Interface Strategy

| Interface | Purpose | Technology |
|-----------|---------|------------|
| **CopilotKit Chat** | Natural language queries, ad-hoc analysis | AG-UI protocol, SSE streaming |
| **Grafana Dashboards** | Pre-built visualizations, monitoring | Native BigQuery connector |

---

## Key Capabilities

### Cost Monitoring

- Unified view across AWS, Azure, GCP, Kubernetes
- Real-time cost tracking with 4-hour sync
- Anomaly detection and spike alerts
- Tag-based cost allocation
- ML-powered forecasting

### Optimization

- AI-driven rightsizing recommendations
- Idle resource detection
- Reserved instance planning
- Cross-cloud price comparison

### Remediation

- One-click optimization actions
- Approval workflows for sensitive changes
- Scheduled resource operations
- Rollback capability

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI** | CopilotKit + Next.js | Natural language chat interface |
| **Agents** | Google ADK + LiteLLM | AI agent orchestration |
| **MCP Servers** | FastMCP | Cloud integration via MCP protocol |
| **Analytics** | BigQuery | Cost data storage and queries |
| **Config** | Firestore (MVP) → PostgreSQL | Operational data |
| **Secrets** | GCP Secret Manager | Cloud credentials |
| **Compute** | Cloud Run | Serverless container hosting |
| **Dashboards** | Grafana | Pre-built cost visualizations |

---

## MVP Scope

| Aspect | Decision |
|--------|----------|
| Tenancy | Single-tenant |
| Home Cloud | GCP |
| Database | Firestore + BigQuery (no PostgreSQL) |
| Monitored Clouds | AWS, Azure, GCP, Kubernetes |
| Monthly Cost | ~$0-10 (free tiers) |

---

## Scope Clarification

### What This Project IS

| Category | Description |
|----------|-------------|
| **AI-Agent Platform** | AI agents handle all user interactions and cloud operations |
| **MCP-First Integration** | Cloud integrations via MCP servers, not direct REST calls |
| **Cost Monitoring Tool** | Tracks, analyzes, and optimizes cloud costs |
| **Multi-Cloud Capable** | Monitors AWS, Azure, GCP, Kubernetes from single interface |
| **Natural Language Interface** | Users ask questions in plain English |
| **Self-Hosted** | Runs on your own GCP project |

### What This Project is NOT

| Category | Clarification |
|----------|---------------|
| **Not a SaaS product** | Self-hosted on your infrastructure (MVP) |
| **Not a REST API backend** | Agents use MCP protocol, not traditional APIs |
| **Not cloud-agnostic deployment** | Home cloud is GCP (monitoring is multi-cloud) |
| **Not real-time streaming costs** | Cost sync every 4 hours (cloud API limitation) |
| **Not a replacement for cloud consoles** | Complements, doesn't replace native tools |

### Key Decisions (Locked)

| Decision | Choice | Rationale | ADR |
|----------|--------|-----------|-----|
| Integration Pattern | MCP Servers | AI-native, better DX than REST | ADR-001 |
| Home Cloud | GCP | Best free tier, scale-to-zero | ADR-002 |
| Analytics DB | BigQuery | Native billing export, 1TB free | ADR-003 |
| Compute | Cloud Run | Serverless, scale-to-zero | ADR-004 |
| MVP Database | Firestore | No PostgreSQL until multi-tenant | ADR-008 |
| Agent Framework | Google ADK + LiteLLM | Vendor-neutral LLM support | — |
| UI Framework | CopilotKit + Next.js | AG-UI protocol support | — |

### Open Questions (To Be Decided)

| Question | Options | Status |
|----------|---------|--------|
| Default LLM provider | Gemini 2.0, Claude 3.5, GPT-4 | User configurable via LiteLLM |
| Authentication provider | Auth0, GCP Identity Platform, Okta | To be decided |
| Grafana deployment | Self-hosted vs Grafana Cloud | To be decided |
| OpenCost integration | Prometheus vs direct API | To be decided |

### MVP Success Criteria

| Criterion | Metric |
|-----------|--------|
| **Cost Query** | User asks "What's my AWS spend this month?" → Agent responds with data |
| **Multi-Cloud** | Single query returns data from 2+ cloud providers |
| **Streaming UI** | Response streams progressively (not all-at-once) |
| **Recommendations** | Agent provides at least 1 optimization suggestion |
| **Cost Threshold** | System within $10/month infrastructure cost |

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Agents call REST APIs directly" | Agents call MCP servers; MCP servers wrap REST APIs |
| "Need PostgreSQL for MVP" | Firestore + BigQuery sufficient for single-tenant |
| "Need many agents" | MVP needs only 5 agents (Coordinator + 4 Domain), no Cloud Agent layer |
| "Real-time cost updates" | Cloud APIs have 4-24 hour delay; we sync every 4 hours |
| "Runs on any cloud" | Platform runs on GCP; monitors any cloud |

### Terminology

| Term | Definition |
|------|------------|
| **Home Cloud** | Where platform infrastructure runs (GCP) |
| **Monitored Cloud** | Clouds being analyzed for costs (AWS, Azure, GCP, K8s) |
| **MCP Server** | Tool server that agents call (Model Context Protocol) |
| **AG-UI** | Agent-to-UI streaming protocol (SSE-based) |
| **Domain Agent** | High-level agent for a capability (Cost, Optimization, etc.) |
| **Cloud Agent** | Cloud-specific agent (AWS Agent, Azure Agent, etc.) |

---

## Related Documents

- [MVP_ARCHITECTURE.md](docs/architecture/MVP_ARCHITECTURE.md) — Simplified MVP stack
- [ADR-001](docs/adr/001-use-mcp-servers.md) — MCP over REST decision
- [ADR-002](docs/adr/002-gcp-only-first.md) — GCP as home cloud
- [docs/core/02-mcp-tool-contracts.md](docs/core/02-mcp-tool-contracts.md) — MCP tool specifications
- [docs/core/03-agent-routing-spec.md](docs/core/03-agent-routing-spec.md) — Agent hierarchy
