# ADR-008: OTEL Gen-AI Semantic Conventions for Observability

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires observability for AI agent operations. Options include:

1. Custom logging/metrics
2. OpenTelemetry (OTEL) standard conventions
3. Vendor-specific solutions (Datadog, New Relic)
4. LangSmith/LangFuse (LLM-specific)

## Decision

**Use OpenTelemetry with Gen-AI Semantic Conventions** for all observability.

## Rationale

| Factor | OTEL Gen-AI | Custom | Vendor-Specific |
|--------|-------------|--------|----------------|
| Standardization | Industry standard | None | Proprietary |
| AI-specific attrs | Yes (2024+) | Manual | Varies |
| Vendor lock-in | No | No | Yes |
| GCP integration | Native | Manual | Varies |
| Community | Large | None | Medium |

### Key Benefits

1. **Standardized AI Tracing**: Token usage, model names, latency in standard format
2. **Vendor Neutral**: Export to any backend (Cloud Monitoring, Jaeger, etc.)
3. **Future-Proof**: Growing industry adoption
4. **Native GCP**: Cloud Trace accepts OTEL directly

### Gen-AI Semantic Conventions

```
gen_ai.system: "openai" | "anthropic" | "google"
gen_ai.request.model: "gpt-4" | "claude-3" | "gemini-pro"
gen_ai.usage.input_tokens: 150
gen_ai.usage.output_tokens: 200
gen_ai.response.finish_reason: "stop" | "length"
```

## Consequences

### Positive
- Consistent observability across all agents
- Easy integration with existing monitoring
- Industry-standard approach

### Negative
- Gen-AI conventions still evolving (2024-2025)
- Some manual instrumentation required
- Learning curve for OTEL concepts

## References

- [OTEL Gen-AI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Cloud Trace Documentation](https://cloud.google.com/trace/docs)
