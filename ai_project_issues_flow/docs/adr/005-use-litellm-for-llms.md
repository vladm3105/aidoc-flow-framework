# ADR-005: LiteLLM for LLM Abstraction (Vendor-Neutral)

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires LLM integration for AI agents. Options include:

1. Direct vendor SDKs (OpenAI, Anthropic, Google)
2. LiteLLM (unified interface)
3. LangChain (framework with LLM support)
4. Vertex AI only (GCP-native)

## Decision

**Use LiteLLM** as the LLM abstraction layer for all AI agent interactions.

## Rationale

| Factor | LiteLLM | Direct SDKs | LangChain |
|--------|---------|-------------|----------|
| Vendor switching | Config change | Code change | Config change |
| API compatibility | OpenAI-compatible | Varies | Varies |
| Overhead | Minimal | None | Heavy |
| Cost tracking | Built-in | Manual | Manual |
| Fallback support | Yes | Manual | Yes |

### Key Benefits

1. **Vendor Flexibility**: Switch between GPT-4, Claude, Gemini without code changes
2. **OpenAI Compatibility**: Use familiar OpenAI SDK syntax
3. **Cost Tracking**: Built-in token usage and cost monitoring
4. **Fallback Chains**: Automatic retry with alternative models

## Consequences

### Positive
- No vendor lock-in for LLM providers
- Easy A/B testing between models
- Unified logging and monitoring

### Negative
- Additional dependency
- Slight latency overhead
- May lag behind latest vendor features

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [03-agent-routing-spec.md](../core/03-agent-routing-spec.md)
