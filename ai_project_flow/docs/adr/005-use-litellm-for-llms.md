# ADR-005: Use LiteLLM for Vendor-Neutral LLM Access

## Status
Accepted

## Date
{DATE}

## Context

The platform's AI agents need access to Large Language Models (LLMs) for natural language understanding and cost analysis. Options:

1. **Direct provider SDKs** - Use Gemini SDK, Claude SDK, OpenAI SDK directly
2. **LangChain LLM abstractions** - Use LangChain's LLM wrappers
3. **LiteLLM** - Vendor-neutral LLM proxy supporting 100+ providers
4. **Cloud provider LLM gateways only** - Lock into Vertex AI or Azure OpenAI

## Decision

We will use **LiteLLM** as the primary abstraction layer for accessing LLMs across all providers.

## Rationale

### Why LiteLLM?

**Vendor-Neutral:**
- Single API works with 100+ LLM providers
- Easy to switch between Gemini, Claude, GPT-4, Llama, Mistral
- Avoids vendor lock-in at the LLM layer
- Can compare models easily

**Simple Integration:**
- Drop-in replacement for OpenAI SDK
- Minimal code changes to switch providers
- Unified error handling across providers

**Cost Optimization:**
- Compare pricing across providers
- Switch to cheapest model for each use case
- Set fallback providers if primary fails

**Compliance Support:**
- Optionally use cloud provider gateways (Vertex AI, Azure OpenAI, Bedrock)
- Data stays within cloud environment for compliance
- Still vendor-neutral at code level

### Why Not Direct SDKs?

**Vendor Lock-In:**
- Code tied to specific provider API
- Hard to switch providers
- Different error handling per provider

**Code Duplication:**
- Need separate code paths for each provider
- More testing surface area
- Higher maintenance burden

### Why Not LangChain?

**Heavier Framework:**
- LangChain is opinionated, includes chains/agents
- We only need LLM access, not full framework
- LiteLLM is lighter, focused

**Flexibility:**
- LangChain can still be used on top of LiteLLM if needed
- LiteLLM doesn't force architectural choices

## Implementation

### Basic Usage

```python
from litellm import completion

# Works with any provider
response = completion(
    model=os.getenv("LLM_MODEL"),  # e.g., "gemini-2.0-flash-exp"
    messages=[{"role": "user", "content": "Analyze AWS costs"}]
)
```

### Configuration

```bash
#.env

# Option 1: Direct to provider
LLM_MODEL=gemini-2.0-flash-exp
GEMINI_API_KEY=<key>

# Option 2: Via cloud gateway (compliance)
LLM_MODEL=vertex_ai/gemini-2.0-flash-exp
GOOGLE_APPLICATION_CREDENTIALS=<path>

# Option 3: Anthropic Claude
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=<key>

# Option 4: Via AWS Bedrock (compliance)
LLM_MODEL=bedrock/anthropic.claude-3-5-sonnet-v2
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
```

### Switching Providers

To switch LLM providers, just change environment variable:

```bash
# Currently using Gemini
export LLM_MODEL=gemini-2.0-flash-exp

# Switch to Claude
export LLM_MODEL=claude-3-5-sonnet-20241022

# Switch to GPT-4
export LLM_MODEL=gpt-4

# Zero code changes needed!
```

## Consequences

### Positive

- ✅ **Vendor-neutral** - Not locked into any LLM provider
- ✅ **Easy switching** - Change provider via config
- ✅ **Cost optimization** - Compare and choose cheapest
- ✅ **Compliance option** - Use cloud gateways when needed
- ✅ **Future-proof** - New providers added by LiteLLM team

### Negative

- ⚠️ **Abstraction layer** - Extra dependency in stack
- ⚠️ **Provider-specific features** - May not support all advanced features
- ⚠️ **Community dependency** - Relies on LiteLLM maintenance

### Mitigation

**Provider-Specific Features:**
- Use LiteLLM for 95% of use cases
- Can still use native SDK for advanced features if needed
- Most common features supported across providers

**Community Dependency:**
- LiteLLM is actively maintained (backed by Anthropic)
- Growing adoption in AI community
- Open source - can fork if needed

## Cloud Provider Gateway Support

LiteLLM supports compliance-focused cloud gateways:

**GCP: Vertex AI**
```python
model="vertex_ai/gemini-2.0-flash-exp"
# Data stays in GCP, uses IAM auth
```

**Azure: Azure OpenAI**
```python
model="azure/gpt-4"
# Data stays in Azure, uses managed identity
```

**AWS: Bedrock**
```python
model="bedrock/anthropic.claude-3-5-sonnet-v2"
# Data stays in AWS, uses IAM roles
```

## Cost Comparison (Example)

| Provider | Model | Cost per 1M tokens | LiteLLM Config |
|----------|-------|-------------------|----------------|
| Google (Vertex AI) | Gemini 2.0 Flash | $0.075 | `vertex_ai/gemini-2.0-flash-exp` |
| Anthropic | Claude 3.5 Sonnet | $3.00 | `claude-3-5-sonnet-20241022` |
| OpenAI | GPT-4 Turbo | $10.00 | `gpt-4-turbo` |
| Meta (Ollama) | Llama 3 8B | Free (local) | `ollama/llama3` |

Easy to test different providers and optimize costs!

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Direct SDKs | Native features | Vendor lock-in | Rejected |
| LangChain | Full framework | Heavy, opinionated | Rejected |
| **LiteLLM** | **Vendor-neutral, simple** | **Abstraction layer** | **Accepted** ✅ |
| Cloud gateways only | Compliance | Single-cloud lock-in | Rejected (but supported via LiteLLM) |

## Related Decisions

- [ADR-002: GCP as First Home Cloud](002-gcp-only-first.md) - Cloud independence applies to LLMs too
- [ADR-001: Use MCP Servers](001-use-mcp-servers.md) - Similar vendor-neutral pattern

## References

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Supported Providers](https://docs.litellm.ai/docs/providers)
- [LiteLLM GitHub](https://github.com/BerriAI/litellm)

## Review

Revisit this decision if:
- LiteLLM project becomes unmaintained
- Provider-specific features become critical
- Abstraction layer adds measurable latency (>100ms overhead)
- Better abstraction layer emerges
