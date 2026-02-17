# ADR-007: CopilotKit MVP, Grafana Post-MVP (Hybrid UI)

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires user interfaces for cost visualization and interaction. Options include:

1. CopilotKit only (AI chat interface)
2. Grafana only (traditional dashboards)
3. Hybrid approach (CopilotKit MVP, Grafana post-MVP)
4. Custom dashboard from scratch

## Decision

**Use CopilotKit for MVP**, defer Grafana dashboards to post-MVP.

## Rationale

| Factor | CopilotKit | Grafana | Custom |
|--------|------------|---------|--------|
| AI-native | Yes | No | Depends |
| Setup time | Days | Weeks | Months |
| Natural language | Built-in | No | Manual |
| Traditional charts | Limited | Extensive | Manual |
| Learning curve | Low | Medium | High |

### Key Benefits

1. **AI-First Differentiator**: Natural language cost queries
2. **Faster MVP**: CopilotKit deploys quickly
3. **User Experience**: Conversational interface more intuitive
4. **Future Flexibility**: Add Grafana later for power users

## Consequences

### Positive
- Faster time to MVP
- Unique AI-first user experience
- Lower initial development cost

### Negative
- No traditional dashboard views in MVP
- Power users may want charts/graphs
- Two UI technologies to maintain long-term

## References

- [CopilotKit Documentation](https://docs.copilotkit.ai/)
- [UX/FINAL-implementation-guide.md](../UX/FINAL-implementation-guide.md)
