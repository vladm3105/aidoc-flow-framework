# ADR-008: Use OpenTelemetry Gen-AI Semantic Conventions

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | {DATE} |
| **Deciders** | Platform Team |
| **Supersedes** | N/A |
| **Related** | ADR-002 (GCP-first), ADR-005 (LiteLLM) |

## Context

The AI Cost Monitoring platform has a 4-layer agent hierarchy (Coordinator → Domain Agents → Cloud Agents → MCP Servers) that makes LLM calls across multiple providers (Gemini, OpenAI, Anthropic). Without standardized observability:

- **Debugging is difficult** — tracing a user query through 4 agent layers requires manual log correlation
- **LLM cost tracking is ad-hoc** — no consistent way to record tokens + cost per call
- **Performance monitoring lacks granularity** — can't pinpoint if latency is in the agent, LLM, or MCP layer

The OpenTelemetry Gen-AI Semantic Conventions provide a vendor-neutral standard for instrumenting generative AI operations with attributes like `gen_ai.system`, `gen_ai.usage.input_tokens`, `gen_ai.agent.name`, and `gen_ai.tool.call.id`.

## Decision

**Adopt OpenTelemetry Gen-AI Semantic Conventions as the observability standard for all AI operations in the platform.**

Specifically:

1. **Agent spans** use `gen_ai.agent.name` and `gen_ai.operation.name`
2. **LLM calls** use `gen_ai.system`, `gen_ai.request.model`, `gen_ai.usage.*` attributes
3. **MCP tool calls** use `gen_ai.tool.call.id`, `gen_ai.tool.name`, `rpc.system=mcp`
4. **Custom cost attributes** extend the convention with `gen_ai.cost.total` for dollar tracking
5. **GCP-native exporters** send traces to Cloud Trace and metrics to Cloud Monitoring

## Alternatives Considered

### 1. Custom Structured Logging Only

- **Pros:** Simple, no new dependencies, works with Cloud Logging
- **Cons:** No distributed tracing, no standard attribute names, no trace correlation across services
- **Rejected:** Doesn't scale with multi-agent fan-out patterns

### 2. Datadog APM

- **Pros:** Excellent Gen-AI support, built-in LLM monitoring
- **Cons:** $15-30/host/month, vendor lock-in, duplicates GCP-native services
- **Rejected:** Cost-prohibitive and violates GCP-first strategy (ADR-002)

### 3. LangSmith / LangFuse

- **Pros:** Purpose-built for LLM observability, prompt tracking
- **Cons:** Another SaaS dependency, limited to LLM layer only, doesn't cover MCP/agent layers
- **Rejected:** Doesn't provide full-stack observability; OTEL covers all layers

### 4. Raw OpenTelemetry (without Gen-AI conventions)

- **Pros:** Stable, well-supported
- **Cons:** Requires custom attribute names, no standardization for LLM-specific data
- **Rejected:** Gen-AI conventions provide the standardization we need

## Consequences

### Positive

- **End-to-end tracing:** Every user query traceable through all 4 agent layers
- **Standardized LLM metrics:** Token usage, cost, and latency in consistent format
- **Vendor-neutral:** Can switch from GCP exporters to any OTEL-compatible backend
- **Free tier coverage:** Cloud Trace (2.5M spans/month), Cloud Monitoring (150MB) — sufficient for MVP
- **Community alignment:** Following the same conventions as LiteLLM, LangChain, and other AI frameworks

### Negative

- **Gen-AI conventions are experimental:** Subject to breaking changes (mitigated by pinning versions)
- **Additional dependencies:** 7 new Python packages (~5MB)
- **Slight latency overhead:** ~1-2ms per span (negligible for LLM calls that take 500ms+)

## Implementation

See [docs/core/09-observability-spec.md](../core/09-observability-spec.md) for the complete specification including:
- Full attribute mapping (§3)
- Span hierarchy (§4)
- Metrics definitions (§5)
- Instrumentation patterns (§7)
- Sampling strategy (§8)
- Dashboard templates (§9)
