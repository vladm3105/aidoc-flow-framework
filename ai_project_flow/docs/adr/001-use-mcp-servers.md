# ADR-001: Use MCP Servers Instead of REST APIs

## Status
Accepted

## Date
2026-01-15

## Context

We needed to choose an integration pattern for connecting our AI agent to GCP APIs. The main options were:

1. **Direct REST API calls** - Traditional approach using HTTP requests
2. **MCP (Model Context Protocol) servers** - Newer protocol designed for AI-to-service integration  
3. **GraphQL API** - Single endpoint with schema-based queries
4. **gRPC services** - High-performance binary protocol

## Decision

We will use **MCP servers** as the primary integration layer between our conversational agent and GCP services.

## Rationale

### Why MCP?

**Designed for AI Agents:**
- MCP was built specifically for LLM-to-service communication
- Native tool/function calling support
- Structured responses optimized for LLM consumption

**Better Developer Experience:**
- FastMCP framework makes server implementation trivial
- Automatic OpenAPI-like schema generation
- Built-in validation and error handling

**Stateless & Cacheable:**
- Each tool call is independent
- Responses can be cached easily
- No session management overhead

**Future-proof:**
- Emerging standard backed by Anthropic
- Growing ecosystem of MCP servers
- Can wrap any API (GCP, AWS, Azure) uniformly

### Why Not REST APIs Directly?

- Much more boilerplate code needed
- LLM would need to construct HTTP requests
- Error handling and retries fall on agent logic
- No standard tool definition format

### Why Not gRPC?

- Requires proto file generation
- LLMs don't work well with binary protocols
- Overkill for our moderate throughput needs

### Why Not GraphQL?

- Query construction is complex for LLMs
- Schema stitching across multiple GCP services difficult
- Less tooling support in Python ecosystem

## Consequences

### Positive

- ✅ **Fast development** - Can wrap GCP APIs in hours, not days
- ✅ **Unified interface** - All tools look the same to the agent
- ✅ **Easy testing** - Tools can be tested independently with simple HTTP calls
- ✅ **Multi-cloud ready** - Same pattern works for AWS/Azure later
- ✅ **Caching friendly** - Tool responses cache naturally in Redis

### Negative

- ⚠️ **New technology** - MCP is relatively new (2024), fewer resources
- ⚠️ **Small ecosystem** - Fewer pre-built MCP servers vs REST clients
- ⚠️ **Extra layer** - MCP server sits between agent and GCP APIs (minor latency)

### Neutral

- 📝 Need to maintain MCP server code alongside agent
- 📝 Requires running MCP server process (deployed to Cloud Run)

## Implementation Notes

### MCP Server Structure

```python
# Example: GCP Cost MCP Server
from fastmcp import FastMCP

mcp = FastMCP("GCP Cost Monitoring")

@mcp.tool()
def get_cost_summary(
    project_id: str,
    days: int = 30,
    group_by: str = "service"
) -> dict:
    """
    Get cost summary from BigQuery billing export.
    """
    # Query BigQuery
    # Return structured response
    pass

# 9 more tools...
```

### Agent Integration

```python
# Agent automatically discovers and calls MCP tools
from langchain.agents import create_tool_calling_agent

agent = create_tool_calling_agent(
    llm=gemini_model,
    tools=mcp.get_tools(),  # Auto-discovered from MCP server
    prompt=cost_agent_prompt
)
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| REST APIs directly | Mature, well-documented | Too much boilerplate | Rejected |
| GraphQL | Single endpoint | Complex for LLMs | Rejected |
| gRPC | High performance | Binary protocol | Rejected |
| **MCP** | **Built for AI** | **Newer tech** | **Accepted** ✅ |

## Related Decisions

- [ADR-002: GCP-Only First](002-gcp-only-first.md) - Start with single cloud
- [ADR-004: Cloud Run for Deployment](004-cloud-run-not-kubernetes.md) - Where MCP server runs

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Anthropic MCP Announcement](https://www.anthropic.com/news/model-context-protocol)

## Review

This decision should be reviewed if:
- MCP protocol becomes deprecated or abandoned
- Performance becomes a bottleneck (latency >500ms per call)
- We discover significant limitations in MCP for our use case
