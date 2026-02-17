# ADR-001: Use MCP Servers for Integration Pattern

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The project requires an integration pattern for AI agents to access cloud provider data and execute operations. Options include:

1. REST APIs with custom wrappers
2. GraphQL federation
3. MCP (Model Context Protocol) Servers

## Decision

**Use MCP Servers** as the primary integration pattern for AI-to-cloud communication.

## Rationale

| Factor | MCP Servers | REST APIs | GraphQL |
|--------|-------------|-----------|--------|
| AI-native tool calling | Native support | Requires adapter | Requires adapter |
| Type safety | Schema-defined | OpenAPI optional | Strong typing |
| Streaming | Built-in | Manual implementation | Subscriptions |
| Multi-provider | Unified interface | Per-provider clients | Federation complexity |
| Ecosystem | Growing (2025+) | Mature | Mature |

### Key Benefits

1. **Native AI Integration**: MCP is designed for LLM tool calling
2. **Unified Interface**: Single protocol for AWS, Azure, GCP, Kubernetes
3. **Real-time Data**: No ETL required for most queries
4. **Vendor Support**: AWS, Azure, GCP releasing official MCP servers (2025-2026)

## Consequences

### Positive
- Simplified agent architecture (direct MCP calls)
- Reduced integration code
- Future-proof as MCP adoption grows

### Negative
- Newer protocol (less community knowledge)
- Custom server needed for OpenCost (no native available)
- Learning curve for team

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [02-mcp-tool-contracts.md](../core/02-mcp-tool-contracts.md)
