# AI Cost Monitoring — API Endpoint Specification

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 05 — API Endpoint Specification |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Frontend Developers, Backend Developers |

---

## 1. API Architecture

### 1.1 Endpoint Groups

The platform exposes four distinct API surfaces:

| API Surface | Protocol | Port | Purpose |
|-------------|----------|------|---------|
| **AG-UI Streaming API** | SSE over HTTP | 8080 | CopilotKit → Agent communication |
| **REST Admin API** | HTTPS/JSON | 8080 | Tenant management, settings, onboarding |
| **Webhook Ingestion API** | HTTPS/JSON | 8080 | Cloud provider event reception (Mode 3) |
| **A2A Gateway API** | HTTPS/JSON (A2A Protocol) | 8090 | External agent communication (Mode 4) |

All APIs sit behind a single API Gateway (Kong/Envoy) that handles SSL termination, rate limiting, WAF, and DDoS protection.

### 1.2 Authentication

| API Surface | Auth Method | Token Source |
|-------------|-------------|--------------|
| AG-UI Streaming | Bearer JWT | Auth0 (from CopilotKit) |
| REST Admin | Bearer JWT | Auth0 (from frontend app) |
| Webhook Ingestion | HMAC Signature + Shared Secret | Per-provider secret from **Secret Manager** |
| A2A Gateway | mTLS Certificate OR API Key + HMAC | Per-agent registration |

---

## 2. AG-UI Streaming API

This is the primary conversational interface used by CopilotKit.

### 2.1 Endpoints

#### POST /api/copilotkit

The main CopilotKit streaming endpoint. Handles all conversational interactions.

| Aspect | Detail |
|--------|--------|
| Method | POST |
| Content-Type | application/json |
| Response | text/event-stream (SSE) |
| Auth | Bearer JWT (Auth0) |

**Request structure** (CopilotKit standard format):
- messages: Conversation history
- actions: Available frontend actions
- context: Frontend state (current dashboard, selected filters)

**Response:** SSE stream with AG-UI protocol events:
- `TextMessageStart` / `TextMessageContent` / `TextMessageEnd` — text responses
- `ActionExecutionStart` / `ActionExecutionEnd` — A2UI component rendering
- `ToolCallStart` / `ToolCallEnd` — agent tool calls (visible to frontend for status)

**Business logic:**
1. JWT middleware extracts tenant context
2. Passes to Coordinator Agent with full context
3. Agent executes, streams results back
4. CopilotKit renders A2UI components in real-time

#### GET /api/copilotkit/health

Health check for CopilotKit connection.

| Aspect | Detail |
|--------|--------|
| Method | GET |
| Auth | None |
| Response | `{ "status": "ok", "version": "1.0" }` |

---

## 3. REST Admin API

CRUD operations for tenant management. All endpoints require JWT authentication.

### 3.1 Tenant & Config

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/tenant | any authenticated | Get current tenant info and config |
| PATCH | /api/tenant/settings | org_admin | Update tenant settings |

### 3.2 Cloud Accounts

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/cloud-accounts | analyst+ | List all cloud accounts |
| POST | /api/cloud-accounts | org_admin | Connect new cloud account |
| GET | /api/cloud-accounts/{id} | analyst+ | Get account details + sync status |
| PATCH | /api/cloud-accounts/{id} | org_admin | Update account config |
| DELETE | /api/cloud-accounts/{id} | org_admin | Disconnect account |
| POST | /api/cloud-accounts/{id}/test | org_admin | Test credential connectivity |
| POST | /api/cloud-accounts/{id}/sync | operator+ | Trigger immediate sync |

**POST /api/cloud-accounts request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| provider | Enum | Yes | aws / azure / gcp / kubernetes |
| display_name | String | Yes | Human-friendly label |
| credentials | Object | Yes | Provider-specific (see onboarding doc) |
| config | Object | No | Regions to monitor, excluded services |

**Credential handling:** Credentials are forwarded to **Secret Manager** by the backend — never stored in PostgreSQL, never returned in GET responses. GET responses show `credential_status: valid/expired/error` instead.

### 3.3 Users & Roles

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/users | analyst+ | List tenant users |
| POST | /api/users/invite | operator+ | Invite new user |
| PATCH | /api/users/{id}/role | org_admin | Change user role |
| DELETE | /api/users/{id} | org_admin | Remove user from tenant |

### 3.4 Policies

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/policies | analyst+ | List all policies |
| POST | /api/policies | org_admin | Create policy |
| PATCH | /api/policies/{id} | org_admin | Update policy |
| DELETE | /api/policies/{id} | org_admin | Delete policy |

### 3.5 Recommendations & Remediation

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/recommendations | analyst+ | List recommendations (filtered) |
| PATCH | /api/recommendations/{id} | analyst+ | Update status (dismiss, acknowledge) |
| POST | /api/recommendations/{id}/execute | operator+ | Create remediation workflow |
| GET | /api/remediation/{id} | analyst+ | Get workflow status |
| POST | /api/remediation/{id}/approve | operator+ | Approve pending action |
| POST | /api/remediation/{id}/rollback | operator+ | Rollback executed action |

### 3.6 Reports

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/reports | analyst+ | List generated reports |
| POST | /api/reports | analyst+ | Request report generation |
| GET | /api/reports/{id}/download | analyst+ | Download report file |

### 3.7 A2A Agent Management

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/a2a-agents | org_admin | List registered external agents |
| POST | /api/a2a-agents | org_admin | Register new external agent |
| PATCH | /api/a2a-agents/{id} | org_admin | Update agent config/permissions |
| DELETE | /api/a2a-agents/{id} | org_admin | Revoke agent access |
| POST | /api/a2a-agents/{id}/rotate-key | org_admin | Rotate API key |

### 3.8 Dashboard Data (Read-Only)

These endpoints provide data for the frontend dashboard widgets. They are separate from the conversational AI interface — these are direct data queries.

| Method | Path | Role Required | Description |
|--------|------|---------------|-------------|
| GET | /api/dashboard/overview | analyst+ | KPI cards: total spend, trend, savings |
| GET | /api/dashboard/cost-trend | analyst+ | Cost over time chart data |
| GET | /api/dashboard/by-provider | analyst+ | Cost breakdown by cloud provider |
| GET | /api/dashboard/by-service | analyst+ | Cost breakdown by service |
| GET | /api/dashboard/anomalies | analyst+ | Recent anomalies list |
| GET | /api/dashboard/recommendations | analyst+ | Top recommendations |

**Common query parameters for dashboard endpoints:**

| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | Date | Range start |
| end_date | Date | Range end |
| provider | Enum | Filter by provider |
| account_id | UUID | Filter by account |
| granularity | Enum | hourly / daily / monthly |

---

## 4. Webhook Ingestion API

Receives events from cloud providers (Mode 3).

### 4.1 Endpoints

| Method | Path | Auth | Source |
|--------|------|------|--------|
| POST | /api/webhooks/aws | HMAC (SNS signature) | AWS SNS |
| POST | /api/webhooks/azure | HMAC (shared secret) | Azure Action Groups |
| POST | /api/webhooks/gcp | HMAC (Pub/Sub token) | GCP Pub/Sub Push |
| POST | /api/webhooks/k8s | Bearer token | Alertmanager |

### 4.2 Processing Flow

```
Webhook received
  → Verify signature/token (reject if invalid)
    → Extract tenant_id from webhook metadata
      → Parse provider-specific payload into common event format
        → Store in events table
          → Enqueue to Cloud Tasks (GCP) / SQS (AWS) / Service Bus (Azure)
            → Event Processor picks up (async serverless function)
              → Evaluate against tenant policies (Policy MCP)
                → Take action (notify / recommend / remediate)
```

### 4.3 Webhook Registration

During cloud account onboarding, the platform generates unique webhook URLs with embedded identifiers:

```
https://api.finops.company.com/api/webhooks/aws?tenant={tenant_id}&account={account_id}
```

The user configures their cloud provider to send events to this URL.

---

## 5. A2A Gateway API

External AI agents communicate through Google A2A Protocol.

### 5.1 Endpoint

| Method | Path | Port | Auth |
|--------|------|------|------|
| POST | /a2a/v1/query | 8090 | mTLS or API Key + HMAC |

### 5.2 Request Flow

```
External Agent sends A2A request
  → A2A Gateway validates auth (cert or API key)
    → Lookup agent registration → get tenant_id, permissions
      → Verify agent is active and not rate-limited
        → Construct TenantContext from registration (not from request)
          → Forward to Coordinator Agent (same pipeline as Mode 1)
            → Return response in A2A format
```

### 5.3 Security Constraints

| Constraint | Enforcement |
|------------|-------------|
| Tenant context from registration only | Agent cannot specify arbitrary tenant_id |
| Permission scoping | Agent can only call tools listed in its registration |
| Rate limiting | 10 req/min default (configurable per agent) |
| Read-only default | No execute_action unless explicitly granted |
| Audit logging | Every A2A request logged with agent identity |

---

## 6. API-Wide Conventions

### 6.1 Response Format

All REST endpoints return:

```
Success: { "data": {...}, "meta": { "request_id": "uuid" } }
Error:   { "error": { "code": "ERROR_CODE", "message": "..." }, "meta": { "request_id": "uuid" } }
List:    { "data": [...], "meta": { "total": 100, "page": 1, "per_page": 20, "request_id": "uuid" } }
```

### 6.2 Pagination

All list endpoints support cursor-based pagination:

| Parameter | Description |
|-----------|-------------|
| per_page | Items per page (default: 20, max: 100) |
| cursor | Opaque cursor from previous response |
| sort_by | Field to sort by |
| sort_order | asc / desc |

### 6.3 Rate Limiting (API Gateway Level)

| Scope | Limit | Response |
|-------|-------|----------|
| Per IP (unauthenticated) | 100 req/min | 429 + Retry-After header |
| Per user (authenticated) | 300 req/min | 429 + Retry-After header |
| Per tenant | 1000 req/min | 429 + Retry-After header |
| Per A2A agent | 10 req/min (configurable) | 429 + Retry-After header |

### 6.4 Standard HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Successful GET, PATCH |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE |
| 400 | Invalid request body or parameters |
| 401 | Missing or invalid authentication |
| 403 | Authenticated but insufficient permissions |
| 404 | Resource not found (within tenant scope) |
| 409 | Conflict (duplicate resource) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

---

## Developer Notes

> **DEV-API-001:** The AG-UI endpoint (`/api/copilotkit`) should be the only endpoint that streams. All REST endpoints return complete JSON responses. Don't mix SSE into REST endpoints.

> **DEV-API-002:** Dashboard endpoints should query pre-computed aggregates (BigQuery materialized views or scheduled query results), not raw billing export data. Response time target for dashboard endpoints is <200ms. Use Redis L2 cache for frequently accessed queries.

> **DEV-API-003:** Webhook endpoints must respond with 200 within 3 seconds and process asynchronously via Cloud Tasks (GCP) / SQS (AWS) / Service Bus (Azure). Cloud providers retry on timeout, and duplicate processing must be idempotent (deduplicate by event ID).

> **DEV-API-004:** All API responses must include OTEL trace headers for distributed tracing. The AG-UI streaming endpoint injects `traceparent` into SSE events for client-side trace correlation. REST endpoints include `X-Trace-ID` (from OTEL `trace_id`) and `X-Request-ID` in responses. If the client sends `traceparent` or `X-Request-ID`, propagate it; otherwise generate one. See [09-observability-spec.md](../core/09-observability-spec.md) §4 for span hierarchy.

> **DEV-API-005:** The A2A Gateway runs on a separate port (8090) intentionally — it has different auth, rate limiting, and monitoring requirements from the user-facing API. Consider separate deployment scaling.

> **DEV-API-006:** Credential-related endpoints (cloud account create/update) must never return credentials in responses. Use a separate `credential_status` field to indicate health. The "test connectivity" endpoint is the only way to verify credentials work.

> **DEV-API-007:** FastAPI auto-instrumentation (`opentelemetry-instrumentation-fastapi`) provides HTTP spans for all API endpoints. Each HTTP span becomes the root parent for all agent spans downstream. Enable with `FastAPIInstrumentor.instrument_app(app)`.
