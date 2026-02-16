# AI Cost Monitoring — MCP Server Tool Contracts

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 02 — MCP Server Tool Contracts |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Agent Developers, MCP Server Developers |

---

## 1. MCP Architecture Principles

### 1.1 Ownership Model

Each Cloud Agent exclusively owns its MCP server. No agent calls another agent's MCP directly.

```
Cloud Agent ──(1:1)──► Cloud MCP Server ──► Cloud API
Domain Agent ──(1:many)──► Shared MCP Servers ──► Internal Services
```

### 1.2 Uniform Tool Interface

All four Cloud MCP servers expose the **same tool names** with identical input/output schemas. This allows Domain Agents to treat cloud providers uniformly — the Cloud Agent handles provider-specific translation.

### 1.3 Credential Flow

Every MCP tool call follows this credential path:

```
Agent receives tenant_id from Coordinator context
  → MCP Server receives tenant_id as tool parameter
    → MCP Server calls Secret Manager: GET secret for tenant-{tenant_id}-{provider}
      → Secret Manager returns short-lived credentials
        → MCP Server uses credentials for cloud API call
          → Credentials never cached longer than the request
```

### 1.4 Error Contract

All MCP tools return errors in a standard envelope:

| Error Field | Description |
|-------------|-------------|
| error_code | Standardized code (e.g., `RATE_LIMITED`, `AUTH_FAILED`, `TIMEOUT`, `NOT_FOUND`) |
| message | Human-readable error description |
| provider | Which cloud provider failed |
| retry_after | Seconds to wait before retry (for rate limits) |
| partial_data | Any data successfully retrieved before failure |

---

## 2. Cloud MCP Servers (4 Servers)

### 2.1 Common Tool Interface

All four Cloud MCP servers (AWS, Azure, GCP, OpenCost) implement these tools:

#### Tool: `get_costs`

Returns cost data for a tenant's cloud account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | Tenant identifier for credential lookup |
| account_id | UUID | Yes | Cloud account to query |
| start_date | Date | Yes | Start of date range |
| end_date | Date | Yes | End of date range |
| granularity | Enum | No | hourly / daily / monthly (default: daily) |
| group_by | List[String] | No | Dimensions to group by: service, region, tag:{key} |
| filters | Object | No | Filter by service, region, tags |

**Returns:** List of cost records with time, service, region, amount, currency, usage fields.

**Data source priority:** Local DB first (from Mode 2 sync), live API fallback if data is stale (>4 hours).

#### Tool: `get_resources`

Returns inventory of cloud resources for a tenant.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| account_id | UUID | Yes | |
| resource_type | String | No | Filter by type (e.g., "ec2_instance") |
| status | Enum | No | running / stopped / idle |
| region | String | No | |
| tags | Object | No | Tag-based filters |

**Returns:** List of resources with ID, type, region, status, utilization snapshot, estimated monthly cost, tags.

#### Tool: `get_recommendations`

Returns optimization recommendations for a cloud account.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| account_id | UUID | Yes | |
| type | Enum | No | rightsize / terminate / reserve / schedule |
| min_savings | Decimal | No | Minimum monthly savings threshold |

**Returns:** List of recommendations with resource ID, type, current config, recommended config, estimated savings, confidence level.

**Source:** Both local database (pre-computed by Mode 2) and cloud-native advisor APIs.

#### Tool: `get_anomalies`

Returns detected cost anomalies.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| account_id | UUID | Yes | |
| severity | Enum | No | critical / high / medium / low |
| status | Enum | No | open / acknowledged / resolved |
| since | Timestamp | No | Only anomalies detected after this time |

**Returns:** List of anomalies with type, severity, expected vs. actual values, deviation percentage, detection time.

#### Tool: `execute_action`

Executes a remediation action on a cloud resource. **Requires operator role or above.**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| account_id | UUID | Yes | |
| action_type | Enum | Yes | resize / stop / start / terminate / modify_config |
| resource_id | String | Yes | Cloud-native resource identifier |
| parameters | Object | Yes | Action-specific parameters (new size, schedule, etc.) |
| approved_by | UUID | Yes | User who approved this action |
| dry_run | Boolean | No | Preview changes without executing (default: false) |

**Returns:** Action result with status, previous state (for rollback), new state, execution time.

**Safety:** Always captures pre-action state in `rollback_data`. Dry run mode available for all actions.

#### Tool: `get_idle_resources`

Specialized tool for finding underutilized resources.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| account_id | UUID | Yes | |
| cpu_threshold | Decimal | No | Max CPU % to consider idle (default: 10%) |
| days_idle | Integer | No | Minimum days below threshold (default: 7) |

**Returns:** List of idle resources with utilization metrics, idle duration, estimated waste per month.

---

### 2.2 Provider-Specific Variations

While the tool interface is uniform, each MCP server translates to different cloud APIs:

#### AWS MCP Server (Port 8082)

| Tool | Cloud API | SDK |
|------|-----------|-----|
| get_costs | Cost Explorer: GetCostAndUsage | boto3 |
| get_resources | Resource Groups Tagging, EC2 Describe* | boto3 |
| get_recommendations | Compute Optimizer, Trusted Advisor | boto3 |
| get_anomalies | Cost Anomaly Detection: GetAnomalies | boto3 |
| execute_action | EC2, RDS, Lambda, ECS APIs | boto3 |
| get_idle_resources | CloudWatch GetMetricStatistics + EC2 | boto3 |

**Credential method:** Secret Manager → IAM Access Key → AssumeRole with ExternalID

#### Azure MCP Server (Port 8083)

| Tool | Cloud API | SDK |
|------|-----------|-----|
| get_costs | Cost Management: Query | azure-mgmt-costmanagement |
| get_resources | Resource Graph: Resources | azure-mgmt-resourcegraph |
| get_recommendations | Advisor: Recommendations.List | azure-mgmt-advisor |
| get_anomalies | Cost Management: Alerts | azure-mgmt-costmanagement |
| execute_action | ARM APIs per resource type | azure-mgmt-compute, etc. |
| get_idle_resources | Monitor: Metrics + Advisor | azure-mgmt-monitor |

**Credential method:** Secret Manager → Service Principal (client_id, client_secret, tenant_id)

#### GCP MCP Server (Port 8084)

| Tool | Cloud API | SDK |
|------|-----------|-----|
| get_costs | Cloud Billing: budgets.list, export tables | google-cloud-billing |
| get_resources | Cloud Asset Inventory: SearchAllResources | google-cloud-asset |
| get_recommendations | Recommender API | google-cloud-recommender |
| get_anomalies | Billing Budgets + Monitoring alerts | google-cloud-billing |
| execute_action | Compute, GKE, Cloud SQL APIs | google-cloud-compute |
| get_idle_resources | Monitoring: TimeSeries.list + Asset | google-cloud-monitoring |

**Credential method:** Secret Manager → Service Account JSON key → impersonation

#### OpenCost MCP Server (Port 8085)

| Tool | Cloud API | SDK |
|------|-----------|-----|
| get_costs | OpenCost: /allocation | HTTP client |
| get_resources | Kubernetes API: pods, nodes, namespaces | kubernetes-client |
| get_recommendations | VPA/HPA analysis + custom logic | kubernetes-client |
| get_anomalies | Prometheus alerts + custom analysis | HTTP client |
| execute_action | kubectl / Helm | kubernetes-client |
| get_idle_resources | Resource metrics + efficiency endpoint | HTTP client |

**Credential method:** Secret Manager → Kubeconfig (cluster-specific)

**Additional tool (K8s only):**

#### Tool: `get_namespace_costs`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| account_id | UUID | Yes | |
| namespace | String | No | Specific namespace (all if omitted) |
| window | String | No | Time window (e.g., "7d", "30d") |

**Returns:** Per-namespace cost breakdown with CPU, memory, storage, network costs.

---

## 3. Shared MCP Servers (4 Servers)

These serve Domain Agents directly, not through Cloud Agents.

### 3.1 Forecast MCP Server (Port 8086)

Provides ML-powered cost predictions.

#### Tool: `generate_forecast`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| scope | Enum | Yes | account / service / total |
| scope_id | String | Conditional | Required if scope is account or service |
| horizon_days | Integer | No | Prediction window (default: 30, max: 90) |
| confidence_interval | Decimal | No | e.g., 0.95 for 95% CI |

**Returns:** Daily forecast values with upper/lower bounds, trend direction, confidence score.

**Model:** Prophet (time-series) + custom features (seasonality, growth patterns).

#### Tool: `get_forecast_accuracy`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| lookback_days | Integer | No | Compare forecast vs. actuals for this period |

**Returns:** MAPE, MAE, R² for recent forecasts. Feeds self-learning loop.

### 3.2 Remediation MCP Server (Port 8087)

Manages remediation workflows through Temporal.io.

#### Tool: `create_workflow`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| recommendation_id | UUID | Yes | |
| action_type | Enum | Yes | |
| requires_approval | Boolean | Yes | Based on action risk and tenant policy |
| approvers | List[UUID] | Conditional | Required if approval needed |

**Returns:** Workflow ID, status, approval link (if applicable).

#### Tool: `get_workflow_status`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workflow_id | String | Yes | Temporal workflow ID |

**Returns:** Current status, approval state, execution history, rollback availability.

#### Tool: `rollback_action`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| workflow_id | String | Yes | |
| reason | String | Yes | Why rolling back |

**Returns:** Rollback status, restored state.

### 3.3 Policy MCP Server (Port 8088)

Manages tenant policies and compliance checks.

#### Tool: `evaluate_event`

Called by Mode 3 Event Processor to determine response.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| event_type | String | Yes | |
| event_data | Object | Yes | Event payload |

**Returns:** List of matching policies, required actions (notify/recommend/remediate), notification targets.

#### Tool: `get_policies`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| type | Enum | No | Filter by policy type |

**Returns:** List of active policies with conditions and actions.

#### Tool: `check_compliance`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| check_type | Enum | Yes | tagging / budget / security / idle_resources |

**Returns:** Compliance status per check, list of violations, remediation suggestions.

### 3.4 Tenant MCP Server (Port 8089)

Manages tenant configuration, users, and cloud accounts.

#### Tool: `get_tenant_config`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |

**Returns:** Complete tenant configuration including plan, settings, cloud accounts, user count, policies.

#### Tool: `list_cloud_accounts`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| provider | Enum | No | Filter by provider |
| status | Enum | No | Filter by status |

**Returns:** List of cloud accounts with status, last sync time, credential health.

#### Tool: `manage_users`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tenant_id | UUID | Yes | |
| action | Enum | Yes | list / invite / update_role / disable |
| user_id | UUID | Conditional | Required for update/disable |
| email | String | Conditional | Required for invite |
| role | Enum | Conditional | Required for invite/update_role |

**Returns:** User list or action result. User creation triggers Auth0 invitation.

---

## 4. MCP Server Operational Characteristics

### 4.1 Connection & Performance

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Max concurrent connections per tenant | 50 | Prevent one tenant from starving others |
| Connection timeout | 30 seconds | Cloud APIs can be slow |
| Request timeout | 25 seconds | Leave 5s buffer below agent timeout |
| Retry attempts | 3 | With exponential backoff (1s, 2s, 4s) |
| Circuit breaker threshold | 5 consecutive failures | Opens circuit for 30 seconds |

### 4.2 Rate Limiting (Cloud API Protection)

| Provider | Cloud API Limit | Our Limit (80% buffer) | Scope |
|----------|----------------|------------------------|-------|
| AWS Cost Explorer | 5 req/sec | 4 req/sec | Per tenant |
| Azure Cost Management | 30 req/min | 24 req/min | Per tenant |
| GCP Cloud Billing | 60 req/min | 48 req/min | Per tenant |
| OpenCost | 100 req/sec | 80 req/sec | Per cluster |

### 4.3 Caching Strategy (3-Tier)

| Layer | Storage | Typical TTL | What's Cached |
|-------|---------|-------------|---------------|
| L1 | Agent in-memory | 30 seconds | Current tool call results, intermediate computations |
| L2 | Redis (optional) | 5-30 min | Query results, recommendations, resources |
| L3 | PostgreSQL + BigQuery | Persistent | Historical data, pre-computed aggregates, billing exports |

**Cache key pattern:** `tenant:{id}:cache:{tool}:{param_hash}`

**Invalidation:** L1/L2 caches are invalidated when Mode 2 sync completes for a tenant.

---

## 5. Cross-Cutting Concerns

### 5.1 Every MCP Tool Call Must:

1. Validate `tenant_id` is present and valid
2. Check caller has permission for this tool (RBAC from JWT)
3. Retrieve credentials from Secret Manager (never hardcode, never cache beyond request)
4. Apply rate limiting before cloud API call
5. Check circuit breaker state before cloud API call
6. Log the call to audit_log (tool name, parameters, outcome, duration)
7. Return standard error envelope on failure
8. Include `cache_hit: true/false` in response metadata

### 5.2 Observability per MCP Server

#### OTEL Gen-AI Tool Call Attributes

Every MCP tool invocation emits an OTEL span with these attributes per [09-observability-spec.md](09-observability-spec.md):

| OTEL Attribute | Value |
|----------------|-------|
| `gen_ai.tool.call.id` | Unique ID per invocation (e.g., `call_abc123`) |
| `gen_ai.tool.name` | Tool name: `get_costs`, `get_recommendations`, etc. |
| `gen_ai.tool.call.result` | `success` or `error` |
| `rpc.system` | `mcp` |
| `rpc.method` | `tools/call` |

#### Custom FinOps Metrics

| Metric | Description |
|--------|-------------|
| `mcp_request_duration_seconds` | Histogram by tool name and provider |
| `mcp_request_total` | Counter by tool, status (success/error), tenant |
| `mcp_cache_hit_ratio` | L1 and L2 hit rates |
| `mcp_cloud_api_calls_total` | Actual cloud API calls (not cache hits) |
| `mcp_circuit_breaker_state` | Current state per provider per tenant |
| `mcp_credential_fetch_duration` | Secret Manager lookup time |

#### Trace Context

MCP servers propagate `traceparent` headers from the calling agent, ensuring tool call spans appear as children of the agent span in Cloud Trace. See [09-observability-spec.md](09-observability-spec.md) §4 for the full span hierarchy.

---

## Developer Notes

> **DEV-MCP-001:** All 4 Cloud MCP servers should share a base class / common module that handles Secret Manager credential fetch, rate limiting, circuit breaker, caching, and audit logging. Only the cloud API translation layer differs per provider.

> **DEV-MCP-002:** The `data source priority` pattern is critical for performance. Tool implementations should check local DB first (populated by Mode 2), and only call live cloud APIs if data is older than the sync interval. This is what makes interactive queries fast.

> **DEV-MCP-003:** `execute_action` is the most security-sensitive tool. It must verify: (a) the user has operator+ role, (b) the action has approval if required by policy, (c) the target resource belongs to the tenant's cloud account, (d) dry_run state is captured before execution. All of this before making any cloud API call.

> **DEV-MCP-004:** Use FastMCP framework for all MCP servers. Define tools with Pydantic models for input validation. FastMCP handles JSON-RPC protocol, tool discovery, and connection management.

> **DEV-MCP-005:** Secret Manager credential fetch adds ~50-100ms per request. Consider short-lived in-memory credential caching (60 seconds max) per tenant per provider to reduce this overhead while maintaining security.

> **DEV-MCP-006:** Test each MCP server independently with mock cloud APIs before integration with agents. Each MCP server should have its own integration test suite with provider-specific test fixtures.
