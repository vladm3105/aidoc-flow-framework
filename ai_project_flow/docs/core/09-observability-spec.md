# AI Cost Monitoring — Observability & OTEL Gen-AI Semantic Conventions

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 09 — Observability & OTEL Gen-AI Specification |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Backend Developers, SRE |

---

## 1. Overview

This specification defines how the AI Cost Monitoring platform implements [OpenTelemetry Gen-AI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) across all agent operations, LLM calls, and MCP tool executions.

### 1.1 Why OTEL Gen-AI?

| Challenge | OTEL Gen-AI Solution |
|-----------|---------------------|
| Debugging agent routing across 4 layers | Distributed traces with agent span hierarchy |
| Tracking LLM costs per call | `gen_ai.usage.input_tokens` + `gen_ai.usage.output_tokens` |
| Monitoring agent latency | `gen_ai.client.operation.duration` histogram |
| Identifying slow MCP tools | `gen_ai.tool.call.id` with duration spans |
| Multi-model cost attribution | `gen_ai.system` + `gen_ai.request.model` attributes |

### 1.2 Standards Compliance

| Standard | Version | Status |
|----------|---------|--------|
| OpenTelemetry Specification | v1.36.0+ | Stable |
| Gen-AI Semantic Conventions | Latest experimental | Development |
| W3C Trace Context | v1.0 | Stable |

---

## 2. OTEL Infrastructure

### 2.1 GCP-Native Exporters

| Signal | Exporter | GCP Service | Cost |
|--------|----------|-------------|------|
| Traces | `opentelemetry-exporter-gcp-trace` | Cloud Trace | Free (first 2.5M spans/month) |
| Metrics | `opentelemetry-exporter-gcp-monitoring` | Cloud Monitoring | Free (first 150MB) |
| Logs | `google-cloud-logging` + trace correlation | Cloud Logging | Free (first 50GB) |

### 2.2 Resource Attributes

Every telemetry signal includes these resource attributes:

```python
from opentelemetry.sdk.resources import Resource

resource = Resource.create({
    "service.name": "ai-cost-monitoring",
    "service.version": "1.0.0",
    "service.namespace": "finops",
    "deployment.environment": "production",  # dev, staging, production
    "cloud.provider": "gcp",
    "cloud.region": "us-central1",
    "cloud.platform": "gcp_cloud_run",
})
```

### 2.3 Initialization

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter

def init_otel():
    """Initialize OTEL with GCP exporters and Gen-AI conventions."""
    
    # Traces
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(CloudTraceSpanExporter())
    )
    trace.set_tracer_provider(tracer_provider)
    
    # Metrics
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[PeriodicExportingMetricReader(
            CloudMonitoringMetricsExporter(),
            export_interval_millis=60000
        )]
    )
    metrics.set_meter_provider(meter_provider)
```

---

## 3. Gen-AI Attribute Mapping

### 3.1 Core LLM Call Attributes

These attributes are set on every LLM call span:

| OTEL Attribute | Type | Required | Example | Source |
|----------------|------|----------|---------|--------|
| `gen_ai.system` | string | ✅ | `"gemini"`, `"openai"`, `"anthropic"` | LLM provider config |
| `gen_ai.request.model` | string | ✅ | `"gemini-2.0-flash"` | Request param |
| `gen_ai.response.model` | string | ✅ | `"gemini-2.0-flash-001"` | Response metadata |
| `gen_ai.operation.name` | string | ✅ | `"chat"`, `"embedding"` | Operation type |
| `gen_ai.usage.input_tokens` | int | ✅ | `1250` | Response metadata |
| `gen_ai.usage.output_tokens` | int | ✅ | `340` | Response metadata |
| `gen_ai.request.temperature` | float | | `0.7` | Request param |
| `gen_ai.request.max_tokens` | int | | `4096` | Request param |
| `gen_ai.request.top_p` | float | | `0.9` | Request param |
| `gen_ai.request.stop_sequences` | string[] | | `["\n"]` | Request param |

### 3.2 Agent Attributes

These attributes are set on agent-level spans:

| OTEL Attribute | Type | Required | Example |
|----------------|------|----------|---------|
| `gen_ai.agent.name` | string | ✅ | `"coordinator"`, `"cost_agent"` |
| `gen_ai.agent.description` | string | | `"Routes queries to domain agents"` |
| `gen_ai.operation.name` | string | ✅ | `"route"`, `"analyze"`, `"remediate"` |

### 3.3 Tool Call Attributes

These attributes are set on MCP tool call spans:

| OTEL Attribute | Type | Required | Example |
|----------------|------|----------|---------|
| `gen_ai.tool.call.id` | string | ✅ | `"call_abc123"` |
| `gen_ai.tool.name` | string | ✅ | `"get_costs"`, `"get_recommendations"` |
| `gen_ai.tool.call.result` | string | ✅ | `"success"`, `"error"` |
| `rpc.system` | string | ✅ | `"mcp"` |
| `rpc.method` | string | ✅ | `"tools/call"` |

### 3.4 Custom Cost Attributes

Extended attributes for FinOps-specific tracking:

| Custom Attribute | Type | Description |
|-----------------|------|-------------|
| `gen_ai.cost.input` | float | Dollar cost for input tokens |
| `gen_ai.cost.output` | float | Dollar cost for output tokens |
| `gen_ai.cost.total` | float | Total dollar cost for this call |
| `gen_ai.cost.currency` | string | `"USD"` |
| `finops.tenant_id` | string | Tenant identifier |
| `finops.query.intent` | string | Classified intent from Coordinator |
| `finops.cloud.providers` | string[] | Cloud providers queried |

---

## 4. Span Hierarchy

### 4.1 Mapping to Agent Architecture

The span hierarchy directly mirrors the 4-layer agent design:

```
[Root Span] HTTP POST /api/copilotkit
│
├── [Agent Span] coordinator
│   ├── gen_ai.agent.name = "coordinator"
│   ├── gen_ai.operation.name = "route"
│   ├── finops.query.intent = "COST_QUERY.cost_breakdown"
│   │
│   └── [Agent Span] cost_agent
│       ├── gen_ai.agent.name = "cost_agent"
│       ├── gen_ai.operation.name = "analyze"
│       │
│       ├── [Model Span] LLM call (intent analysis)
│       │   ├── gen_ai.system = "gemini"
│       │   ├── gen_ai.request.model = "gemini-2.0-flash"
│       │   ├── gen_ai.usage.input_tokens = 850
│       │   ├── gen_ai.usage.output_tokens = 120
│       │   └── gen_ai.cost.total = 0.0023
│       │
│       └── [Agent Span] gcp_cloud_agent
│           ├── gen_ai.agent.name = "gcp_cloud_agent"
│           │
│           ├── [Tool Span] get_costs
│           │   ├── gen_ai.tool.call.id = "call_xyz789"
│           │   ├── gen_ai.tool.name = "get_costs"
│           │   ├── rpc.system = "mcp"
│           │   └── gen_ai.tool.call.result = "success"
│           │
│           └── [Tool Span] get_recommendations
│               ├── gen_ai.tool.call.id = "call_abc456"
│               ├── gen_ai.tool.name = "get_recommendations"
│               ├── rpc.system = "mcp"
│               └── gen_ai.tool.call.result = "success"
```

### 4.2 Multi-Agent Fan-Out

For cross-cloud queries, Cloud Agents execute in parallel:

```
[Agent Span] cross_cloud_agent
├── gen_ai.operation.name = "compare"
│
├── [Agent Span] aws_cloud_agent (parallel)
│   └── [Tool Span] get_costs (AWS MCP)
│
├── [Agent Span] azure_cloud_agent (parallel)
│   └── [Tool Span] get_costs (Azure MCP)
│
└── [Agent Span] gcp_cloud_agent (parallel)
    └── [Tool Span] get_costs (GCP MCP)
```

### 4.3 Span Naming Convention

| Layer | Span Name Format | Example |
|-------|-----------------|---------|
| API | `HTTP {method} {path}` | `HTTP POST /api/copilotkit` |
| Agent | `{agent_name}.{operation}` | `cost_agent.analyze` |
| LLM | `{gen_ai.system}.{operation}` | `gemini.chat` |
| Tool | `{tool_name}` | `get_costs` |
| MCP | `mcp.{method}` | `mcp.tools/call` |

---

## 5. Gen-AI Metrics

### 5.1 Standard OTEL Gen-AI Metrics

| Metric Name | Type | Unit | Description |
|-------------|------|------|-------------|
| `gen_ai.client.token.usage` | Histogram | `{token}` | Token count per request (input + output) |
| `gen_ai.client.operation.duration` | Histogram | `s` | Time from request to response |
| `gen_ai.server.request.count` | Counter | `{request}` | Total LLM requests |

**Metric Attributes (labels):**

| Attribute | Applied To |
|-----------|------------|
| `gen_ai.system` | All metrics |
| `gen_ai.request.model` | All metrics |
| `gen_ai.operation.name` | All metrics |
| `gen_ai.token.type` | `token.usage` only (`input` or `output`) |

### 5.2 Custom FinOps Metrics

| Metric Name | Type | Unit | Description |
|-------------|------|------|-------------|
| `finops.llm.cost` | Counter | `USD` | Cumulative LLM cost |
| `finops.agent.invocations` | Counter | `{invocation}` | Agent invocations by type |
| `finops.tool.calls` | Counter | `{call}` | MCP tool calls by name |
| `finops.tool.errors` | Counter | `{error}` | MCP tool errors by type |
| `finops.query.latency` | Histogram | `s` | End-to-end query latency |

### 5.3 Cost Calculation

Token cost is calculated using model-specific pricing:

```python
MODEL_PRICING = {
    "gemini-2.0-flash": {"input": 0.075 / 1_000_000, "output": 0.30 / 1_000_000},
    "gemini-2.0-pro": {"input": 1.25 / 1_000_000, "output": 5.00 / 1_000_000},
    "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
    "claude-sonnet-4-20250514": {"input": 3.00 / 1_000_000, "output": 15.00 / 1_000_000},
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gemini-2.0-flash"])
    return (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])
```

---

## 6. Gen-AI Events

### 6.1 Prompt and Completion Events

OTEL Gen-AI defines events for capturing LLM inputs/outputs:

| Event Name | When Emitted | Content |
|------------|--------------|---------|
| `gen_ai.content.prompt` | Before LLM call | System prompt + user message (redacted in production) |
| `gen_ai.content.completion` | After LLM call | LLM response text (redacted in production) |
| `gen_ai.tool.message` | During tool use | Tool call parameters and results |

### 6.2 Privacy Controls

| Environment | Prompt Logging | Completion Logging |
|-------------|---------------|-------------------|
| Development | Full content | Full content |
| Staging | First 200 chars | First 200 chars |
| Production | Hash only | Hash only |

```python
import hashlib

def redact_for_production(content: str, environment: str) -> str:
    if environment == "production":
        return f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    elif environment == "staging":
        return content[:200] + "..." if len(content) > 200 else content
    return content  # full content in dev
```

---

## 7. Instrumentation Patterns

### 7.1 LLM Call Decorator

```python
from opentelemetry import trace
from functools import wraps

tracer = trace.get_tracer("ai-cost-monitoring.gen_ai")

def trace_llm_call(func):
    """Decorator that auto-instruments LLM calls with OTEL Gen-AI attributes."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        model = kwargs.get("model", "gemini-2.0-flash")
        system = model.split("-")[0]  # "gemini", "gpt", "claude"
        
        with tracer.start_as_current_span(
            f"{system}.chat",
            kind=trace.SpanKind.CLIENT,
            attributes={
                "gen_ai.system": system,
                "gen_ai.request.model": model,
                "gen_ai.operation.name": "chat",
            }
        ) as span:
            response = await func(*args, **kwargs)
            
            # Set response attributes
            span.set_attribute("gen_ai.response.model", response.model)
            span.set_attribute("gen_ai.usage.input_tokens", response.usage.prompt_tokens)
            span.set_attribute("gen_ai.usage.output_tokens", response.usage.completion_tokens)
            
            # Calculate and record cost
            cost = calculate_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens)
            span.set_attribute("gen_ai.cost.total", cost)
            
            return response
    return wrapper
```

### 7.2 Agent Span Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def agent_span(agent_name: str, operation: str, tenant_id: str = None):
    """Create an OTEL span for agent operations."""
    with tracer.start_as_current_span(
        f"{agent_name}.{operation}",
        kind=trace.SpanKind.INTERNAL,
        attributes={
            "gen_ai.agent.name": agent_name,
            "gen_ai.operation.name": operation,
            "finops.tenant_id": tenant_id or "",
        }
    ) as span:
        try:
            yield span
        except Exception as e:
            span.set_status(trace.StatusCode.ERROR, str(e))
            span.record_exception(e)
            raise
```

### 7.3 MCP Tool Instrumentation

```python
import uuid

def trace_mcp_tool(tool_name: str):
    """Decorator for MCP tool calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            call_id = f"call_{uuid.uuid4().hex[:12]}"
            
            with tracer.start_as_current_span(
                tool_name,
                kind=trace.SpanKind.CLIENT,
                attributes={
                    "gen_ai.tool.call.id": call_id,
                    "gen_ai.tool.name": tool_name,
                    "rpc.system": "mcp",
                    "rpc.method": "tools/call",
                }
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("gen_ai.tool.call.result", "success")
                    return result
                except Exception as e:
                    span.set_attribute("gen_ai.tool.call.result", "error")
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
```

---

## 8. Sampling Strategy

### 8.1 Per-Environment Sampling

| Environment | Trace Sampling | Metric Interval | Log Level |
|-------------|---------------|-----------------|-----------|
| Development | 100% (all traces) | 10s | DEBUG |
| Staging | 50% | 30s | INFO |
| Production | 10% + errors always | 60s | WARN |

### 8.2 Head-Based Sampling Rules

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, ParentBased

sampling_rates = {
    "development": 1.0,
    "staging": 0.5,
    "production": 0.1,
}

sampler = ParentBased(
    root=TraceIdRatioBased(sampling_rates[ENVIRONMENT])
)
```

**Exception:** LLM calls exceeding cost thresholds are always sampled:
- Any single call > $1.00 → always trace
- Any call with error → always trace
- Budget alert triggers → always trace

---

## 9. Dashboard Templates

### 9.1 Cloud Monitoring Queries

**LLM Cost per Model (daily):**
```
fetch generic_task
| metric 'custom.googleapis.com/finops/llm/cost'
| align rate(1h)
| group_by [metric.gen_ai_request_model], [value_cost_aggregate: aggregate(value.cost)]
```

**Token Usage by Agent:**
```
fetch generic_task
| metric 'custom.googleapis.com/gen_ai/client/token/usage'
| align delta(1h)
| group_by [metric.gen_ai_agent_name, metric.gen_ai_token_type],
    [value_usage_aggregate: aggregate(value.usage)]
```

**Agent Latency (p50, p95, p99):**
```
fetch generic_task
| metric 'custom.googleapis.com/gen_ai/client/operation/duration'
| align delta(1h)
| group_by [metric.gen_ai_agent_name],
    [p50: percentile(value.duration, 50),
     p95: percentile(value.duration, 95),
     p99: percentile(value.duration, 99)]
```

### 9.2 Alert Policies

| Alert | Condition | Notification |
|-------|-----------|--------------|
| High LLM cost | `finops.llm.cost` > $50/hour | PagerDuty P2 |
| Agent latency spike | `gen_ai.client.operation.duration` p95 > 30s | Slack warning |
| Tool error rate | `finops.tool.errors` / `finops.tool.calls` > 5% | Slack + email |
| Token usage anomaly | `gen_ai.client.token.usage` > 3x daily avg | Slack warning |

---

## 10. Python Dependencies

```
# requirements.txt additions
opentelemetry-api>=1.27.0
opentelemetry-sdk>=1.27.0
opentelemetry-exporter-gcp-trace>=1.8.0
opentelemetry-exporter-gcp-monitoring>=1.8.0
opentelemetry-instrumentation-fastapi>=0.48b0
opentelemetry-instrumentation-httpx>=0.48b0
opentelemetry-semantic-conventions>=0.48b0
```

---

*Document Version: 1.0 | February 2026*
