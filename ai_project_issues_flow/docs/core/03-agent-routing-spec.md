# AI Cost Monitoring — Agent Prompt Engineering & Tool Routing

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 03 — Agent Prompt Engineering & Tool Routing |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Agent Developers, Prompt Engineers |

---

## 1. Agent Communication Flow

### 1.1 Request Lifecycle

```
User Query (natural language)
  → AG-UI Server (JWT validation, tenant context extraction)
    → Coordinator Agent (intent classification, routing)
      → Domain Agent (business logic, multi-cloud orchestration)
        → Cloud Agent(s) (provider-specific translation, parallel execution)
          → MCP Server(s) (tool execution, cloud API calls)
            → Response aggregation (bottom-up)
              → A2UI Component Selection (charts, tables, cards, text)
                → SSE Stream to CopilotKit (real-time rendering)
```

### 1.2 Context Object

Every agent in the chain receives and passes a `TenantContext` object:

| Field | Source | Description |
|-------|--------|-------------|
| tenant_id | JWT `org_id` claim | Which customer organization |
| user_id | JWT `sub` claim | Which user |
| roles | JWT `roles` claim | User's RBAC roles |
| permissions | JWT `permissions` claim | Granular permission list |
| cloud_accounts | DB lookup by tenant_id | Available cloud accounts for this tenant |
| plan | DB lookup by tenant_id | Tenant's plan (affects feature access) |
| timezone | Tenant settings | For date/time interpretation |

This context is **injected by the AG-UI Server** after JWT validation — never provided by the user or derived from the query.

---

## 2. Coordinator Agent

### 2.1 Role

The Coordinator is the single entry point for all interactive and A2A queries. It:

1. Classifies user intent
2. Routes to the correct Domain Agent(s)
3. Handles multi-agent orchestration for complex queries
4. Selects A2UI response components
5. Manages conversation context across turns

### 2.2 Intent Taxonomy

| Intent Category | Sub-Intents | Route To | Example Queries |
|-----------------|-------------|----------|-----------------|
| **COST_QUERY** | cost_breakdown, cost_comparison, cost_trend, cost_by_tag | Cost Agent | "What's our AWS spend this month?", "Compare GCP vs Azure costs" |
| **OPTIMIZATION** | idle_resources, rightsizing, savings_opportunities, reserved_planning | Optimization Agent | "Find idle resources", "What can we save on EC2?" |
| **ANOMALY** | anomaly_investigate, anomaly_list, budget_status | Cost Agent + Optimization Agent | "Why did our bill spike?", "Show open anomalies" |
| **REMEDIATION** | execute_action, schedule_action, rollback, approval_status | Remediation Agent | "Rightsize these instances", "Stop dev instances at 8 PM" |
| **REPORTING** | generate_report, forecast, chargeback, executive_summary | Reporting Agent | "Generate monthly report", "Forecast next quarter spend" |
| **TENANT_ADMIN** | manage_users, manage_accounts, manage_policies, view_config | Tenant Agent | "Add a new AWS account", "Invite user as analyst" |
| **CROSS_CLOUD** | multi_cloud_compare, migration_analysis, total_spend | Cross-Cloud Agent | "Compare our total cloud spend by provider", "Where should we run this workload?" |
| **CONVERSATIONAL** | greeting, clarification, help, feedback | Coordinator (self) | "Hi", "What can you do?", "Help" |

### 2.3 Routing Logic

The Coordinator uses these rules in order:

**Rule 1 — Single Domain Match:**
If the intent maps to exactly one Domain Agent → route directly.

**Rule 2 — Multi-Domain Query:**
If the query spans multiple domains → fan out to multiple Domain Agents in parallel, aggregate results.

Examples:
- "Why did our bill spike and what can we save?" → Cost Agent + Optimization Agent (parallel)
- "Show me all anomalies and generate a report" → Cost Agent, then Reporting Agent (sequential)

**Rule 3 — Cross-Cloud Explicit:**
If the query explicitly compares providers or asks about total spend → Cross-Cloud Agent (which internally fans out to all Cloud Agents).

**Rule 4 — Ambiguous Query:**
If intent is unclear, the Coordinator asks a single clarifying question. It does not guess.

Examples:
- "Show me everything" → "I can show you cost overview, optimization opportunities, or recent anomalies. Which would be most helpful?"
- "Fix it" (without context) → "What would you like me to fix? I can see these open recommendations: [list top 3]"

**Rule 5 — Permission Check Before Routing:**
If the query requires a permission the user doesn't have → explain what's needed.

- Viewer asks to execute remediation → "Remediation actions require Operator role. Your current role is Viewer. Contact your Org Admin to request access."

### 2.4 Multi-Turn Conversation

The Coordinator maintains a conversation buffer (last 10 turns) to handle follow-up queries:

| Scenario | Behavior |
|----------|----------|
| User: "Show AWS costs" → "Now show Azure" | Coordinator uses same date range, grouping from previous turn |
| User: "Find idle EC2" → "Rightsize all of them" | Coordinator links to previous results, passes resource IDs to Remediation Agent |
| User: "Why the spike?" → "When did it start?" | Coordinator re-queries with time dimension added |
| User changes topic completely | Coordinator resets context, routes to new Domain Agent |

---

## 3. Domain Agent Specifications

### 3.1 Cost Agent

**Purpose:** Unified cost queries, budget tracking, anomaly investigation.

**Receives from Coordinator:** Intent, tenant context, date range, filters, conversation context.

**Decision logic:**

```
1. Determine scope: single cloud or multi-cloud?
   → Single cloud: delegate to one Cloud Agent
   → Multi-cloud: fan out to all relevant Cloud Agents (parallel)

2. Determine data freshness need:
   → Current/real-time: instruct Cloud Agent to check live API
   → Historical: instruct Cloud Agent to use local DB only

3. Determine response detail level:
   → Summary: aggregate totals
   → Breakdown: group by service/region/tag
   → Investigation: drill-down with anomaly correlation

4. If anomaly investigation:
   → Query anomalies table first
   → Correlate with cost data changes
   → Identify root cause (new service? usage spike? pricing change?)
```

**A2UI component suggestions returned to Coordinator:**
- Cost trend → Line chart
- Cost breakdown → Bar chart or pie chart
- Comparison → Side-by-side bar chart
- Anomaly → Alert card + trend chart with highlighted deviation

### 3.2 Optimization Agent

**Purpose:** Find savings opportunities, manage recommendations.

**Decision logic:**

```
1. Fan out to all Cloud Agents: get_idle_resources + get_recommendations (parallel)

2. Aggregate results across providers

3. Rank by estimated_savings_monthly (descending)

4. Filter by user's permission level:
   → Viewer: show recommendations only
   → Analyst: show with "request approval" option
   → Operator+: show with "execute now" option

5. Group by recommendation type if multiple results
```

**A2UI component suggestions:**
- Recommendations list → Card grid with savings amounts
- Idle resources → Table with utilization sparklines
- Savings summary → KPI card with total potential savings

### 3.3 Remediation Agent

**Purpose:** Execute optimization actions safely through approval workflows.

**Decision logic:**

```
1. Validate user has operator+ role (abort if not)

2. Determine action risk level from tenant policies:
   → Low risk (stop dev instance): may auto-approve per policy
   → Medium risk (rightsize production): requires operator approval
   → High risk (terminate resource): requires org_admin approval

3. If approval needed:
   → Create Temporal workflow via Remediation MCP
   → Return approval request with link
   → Wait for approval event

4. If approved or auto-approved:
   → Execute via Cloud Agent's execute_action tool (with dry_run first)
   → Capture rollback state
   → Confirm execution and return results

5. If user requests rollback:
   → Verify rollback data exists
   → Execute rollback via Cloud Agent
   → Log reversal
```

**A2UI component suggestions:**
- Action preview → Diff card (current vs. proposed)
- Approval status → Status tracker component
- Execution result → Success/failure card with details

### 3.4 Reporting Agent

**Purpose:** Generate reports, forecasts, and chargeback summaries.

**Decision logic:**

```
1. Determine report type:
   → Real-time dashboard data: query via Cost Agent pattern
   → Generated report (PDF): trigger Forecast MCP / aggregate data
   → Chargeback: group costs by tag (team/department/project)

2. For forecasts:
   → Call Forecast MCP with scope and horizon
   → Overlay historical actuals for comparison
   → Include confidence intervals

3. For scheduled reports:
   → Check if report already exists for this period
   → If exists: return link to stored report
   → If not: generate and store to object storage
```

**A2UI component suggestions:**
- Forecast → Area chart with confidence bands
- Executive summary → KPI cards + trend charts
- Chargeback → Grouped bar chart by team/department

### 3.5 Tenant Agent

**Purpose:** Administrative operations — user management, cloud account management, policy configuration.

**Decision logic:**

```
1. Verify user has org_admin+ role (abort if not)

2. Route to Tenant MCP for the requested operation

3. For cloud account operations:
   → Adding account: validate credential format, test connectivity
   → Removing account: confirm no active recommendations, warn about data loss
   → Updating: apply changes, trigger immediate sync

4. For user operations:
   → All changes synced to Auth0 Organizations
   → Role changes take effect on next JWT refresh
```

### 3.6 Cross-Cloud Agent

**Purpose:** Queries that span multiple cloud providers or compare between them.

**Decision logic:**

```
1. Fan out to ALL active Cloud Agents for this tenant (parallel)

2. Normalize data to common format:
   → All costs in USD
   → Common resource type taxonomy (compute, storage, network, database, etc.)
   → Common region naming

3. Aggregate and compare:
   → Total by provider
   → Service category mapping across providers
   → Efficiency comparison (cost per workload unit)

4. For migration analysis:
   → Get current workload specs from source Cloud Agent
   → Get equivalent pricing from target Cloud Agent
   → Calculate delta with caveats
```

---

## 4. Cloud Agent Behavior

All four Cloud Agents (AWS, Azure, GCP, K8s) follow the same pattern:

```
1. Receive request from Domain Agent with:
   → Tool to call (get_costs, get_resources, etc.)
   → Parameters (already validated by Domain Agent)
   → Tenant context

2. Check L1 cache (in-memory, 60 sec)
   → Hit: return cached result

3. Check L2 cache (Redis, 5-30 min) - optional
   → Hit: populate L1, return cached result

4. Check circuit breaker state
   → Open: return cached data (if available) OR error with retry_after

5. Call MCP Server tool
   → MCP handles: Secret Manager creds, rate limiting, cloud API call

6. On success:
   → Populate L2 cache, L1 cache
   → Return result to Domain Agent

7. On failure:
   → If partial data: return with warning
   → If retryable: retry per backoff policy
   → If circuit breaker trips: mark provider degraded
```

---

## 5. A2UI Component Selection Guide

The Coordinator selects response components based on data type and user query:

| Data Pattern | A2UI Component | When to Use |
|-------------|----------------|-------------|
| Single number | KPI Card | "What's our total spend?" |
| Number with trend | KPI Card + Sparkline | "What's our spend trend?" |
| Time series | Line Chart | Cost over time, forecast |
| Category breakdown | Bar Chart (horizontal) | Cost by service, cost by team |
| Proportion | Donut Chart | Cost distribution by provider |
| Comparison | Grouped Bar Chart | Provider vs. provider, month vs. month |
| Forecast | Area Chart with bands | Predicted spend with confidence interval |
| Resource list | Data Table | Idle resources, recommendations |
| Action preview | Diff Card | Before/after configuration |
| Alert | Alert Banner | Anomaly notification, budget warning |
| Status tracking | Progress Steps | Remediation workflow status |
| Multiple metrics | Dashboard Grid | Executive overview |
| Narrative | Formatted Text | Explanation of anomaly root cause |

**Rule:** Always prefer a visual component over plain text when data is structured. Use text only for narrative explanations.

---

## 6. Error Handling & Graceful Degradation

| Scenario | Agent Behavior |
|----------|----------------|
| One cloud provider times out | Return partial results from other providers + warning message |
| All cloud providers fail | Return most recent cached data + "Data may be stale" warning |
| User lacks permission | Clear explanation + who to contact for access |
| Rate limit hit | Return cached data if available + "Refreshing in background" |
| Ambiguous query | Ask ONE clarifying question with options |
| Empty results | Confirm the query was understood, suggest alternative queries |
| Large result set (>100 items) | Show top 10 + "Showing top results. Want me to show more?" |

---

## Developer Notes

> **DEV-AGT-001:** The Coordinator's intent classifier should be tested with at least 200 sample queries covering all intent categories. Track classification accuracy and routing correctness as a metric.

> **DEV-AGT-002:** Multi-turn conversation context is stored in Redis (if available) or in-memory with session TTL of 30 minutes. The last 10 turns are included in the Coordinator's prompt. Older turns are summarized. Redis is **optional** — use in-memory storage for MVP; add Redis L2 cache for production horizontal scaling.

> **DEV-AGT-003:** Domain Agents should never call Cloud APIs directly. They always go through Cloud Agents, which go through MCP Servers. This ensures caching, rate limiting, and circuit breaking are consistently applied.

> **DEV-AGT-004:** A2UI component selection can be overridden by the user: "Show that as a table instead of a chart." The Coordinator should honor explicit format requests.

> **DEV-AGT-005:** The parallel fan-out pattern (Domain Agent → multiple Cloud Agents) should use `asyncio.gather()` with `return_exceptions=True` so that one cloud failure doesn't block the entire response.

> **DEV-AGT-006:** Agent prompts should be versioned and stored separately from code. Changes to prompts should be treated as configuration changes with rollback capability, not code deployments.

> **DEV-AGT-007:** Each agent must emit OTEL Gen-AI spans with attributes defined in [09-observability-spec.md](09-observability-spec.md). The span hierarchy mirrors the agent hierarchy:
>
> ```
> [Root] HTTP POST /api/copilotkit
> └── [Agent] coordinator (gen_ai.agent.name, gen_ai.operation.name=route)
>     └── [Agent] cost_agent (gen_ai.operation.name=analyze)
>         ├── [Model] gemini.chat (gen_ai.usage.input_tokens, gen_ai.usage.output_tokens)
>         └── [Agent] gcp_cloud_agent
>             └── [Tool] get_costs (gen_ai.tool.call.id, rpc.system=mcp)
> ```
>
> Every agent span must include: `gen_ai.agent.name`, `gen_ai.operation.name`, `finops.tenant_id`, and duration. LLM calls must include all `gen_ai.usage.*` and `gen_ai.cost.*` attributes. See [09-observability-spec.md](09-observability-spec.md) §4 for full span hierarchy and §7 for instrumentation patterns.

---

## 7. Observability & OTEL Gen-AI Integration

All agent operations are instrumented with [OpenTelemetry Gen-AI Semantic Conventions](09-observability-spec.md).

### 7.1 Agent Span Attributes

Every agent emits these OTEL attributes:

| OTEL Attribute | Value | Set By |
|----------------|-------|--------|
| `gen_ai.agent.name` | `coordinator`, `cost_agent`, `optimization_agent`, etc. | Agent init |
| `gen_ai.agent.description` | Agent purpose | Agent init |
| `gen_ai.operation.name` | `route`, `analyze`, `optimize`, `remediate`, `report` | Per operation |
| `finops.tenant_id` | Tenant UUID | TenantContext |
| `finops.query.intent` | Classified intent | Coordinator |
| `finops.cloud.providers` | Queried providers | Domain Agent |

### 7.2 LLM Call Attributes

When agents make LLM calls (e.g., intent classification, response generation):

| OTEL Attribute | Description |
|----------------|-------------|
| `gen_ai.system` | `gemini`, `openai`, `anthropic` |
| `gen_ai.request.model` | Model requested |
| `gen_ai.response.model` | Model actually used |
| `gen_ai.usage.input_tokens` | Prompt tokens consumed |
| `gen_ai.usage.output_tokens` | Completion tokens generated |
| `gen_ai.cost.total` | Dollar cost per call |

### 7.3 Trace Context Propagation

The `TenantContext` (§1.2) is extended with trace context:

| Field | Source | Description |
|-------|--------|-------------|
| `trace_id` | W3C `traceparent` header | Links all spans in a request |
| `span_id` | Current span | Parent span for child agents |

This enables end-to-end tracing from HTTP request → Coordinator → Domain Agent → Cloud Agent → MCP Server.

**Full specification:** [09-observability-spec.md](09-observability-spec.md)
