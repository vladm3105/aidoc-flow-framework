# ADR-007: Grafana + AG-UI Hybrid Interface (Not Either/Or)

## Status
Accepted

## Date
{DATE}

## Context

Users need to interact with cost data in different ways. Options for UI:

1. **Grafana dashboards only** - Pre-built, static dashboards
2. **Conversational AI only** - CopilotKit AG-UI chat interface
3. **Custom dashboard framework** - Build from scratch (React, D3.js)
4. **Hybrid approach** - Both Grafana AND AG-UI

## Decision

We will provide **both Grafana dashboards AND conversational AG-UI interface** as complementary, loosely-coupled systems.

## Rationale

### Why Both?

**Different Use Cases:**
- Grafana: Quick scanning, reliable visualizations, alerts
- AG-UI: Ad-hoc questions, root cause analysis, complex queries

**Different User Personas:**
- Finance team: Prefers dashboards (Grafana)
- Engineers: Prefers conversational queries (AG-UI)
- Executives: Needs both (dashboard overview, then drill-down via chat)

**Complementary Strengths:**

| Feature | Grafana | AG-UI Chat | Winner |
|---------|---------|------------|--------|
| **Speed** | Instant (cached) | ~1-5 seconds (LLM) | Grafana |
| **Flexibility** | Limited (pre-built) | Unlimited (natural language) | AG-UI |
| **Reliability** | Very high (SQL) | High (LLM dependent) | Grafana |
| **Discoverability** | Excellent (visual) | Poor (text-based) | Grafana |
| **Complex queries** | Hard (dashboard limits) | Easy (just ask) | AG-UI |
| **Sharing** | Easy (URL, export) | Medium (conversation log) | Grafana |

### Why Not Grafana Only?

**Limited Flexibility:**
- Can't answer arbitrary questions
- Dashboard creation requires expertise
- Hard to express complex multi-step queries

**Example Questions Grafana Can't Handle:**
- *"Why did AWS costs spike last Tuesday, and which specific service caused it?"*
- *"Show me idle resources that haven't been touched in 90 days AND cost > $100/month"*
- *"Compare our GCP spend pattern vs industry benchmarks"*

These need AI agents with multi-step reasoning.

### Why Not AG-UI Only?

**Slower for Routine Checks:**
- Every query needs LLM thinking (1-5 seconds)
- Dashboards load instantly
- Users want quick glances

**Less Visual:**
- Text-based responses harder to scan
- Dashboards show trends visually
- Harder to spot patterns in text

**Alert Fatigue:**
- Dashboards can trigger automated alerts
- AG-UI requires active querying

### Why Not Custom Dashboard?

**Reinventing the Wheel:**
- Grafana is mature, feature-rich
- Would take months to build equivalent
- Active open-source community

**Opportunity Cost:**
- Time better spent on AI agents
- Dashboard building isn't our core value prop

## Implementation

### Architecture

```
┌─────────────────────────────────────────┐
│             USER                        │
└────────┬─────────────────────┬──────────┘
         │                     │
         ↓                     ↓
   ┌─────────┐          ┌──────────────┐
   │ Grafana │          │ CopilotKit   │
   │Dashboard│          │   AG-UI      │
   └────┬────┘          └──────┬───────┘
        │                      │
        ↓                      ↓
   ┌────────────────────────────────────┐
   │          DATA LAYER                │
   │  BigQuery (metrics)                │
   │  PostgreSQL (metadata)             │
   └────────────────────────────────────┘
```

**Loose Coupling:**
- Each UI is independent
- Both query same data layer
- No direct integration needed
- Can evolve separately

### User Flow Examples

**Daily Monitoring (Grafana):**
1. User opens `/dashboards`
2. Scans cost overview dashboard
3. Sees AWS spike
4. Clicks "Ask AI about this" → Opens AG-UI with context

**Ad-hoc Investigation (AG-UI):**
1. User opens `/` (chat widget)
2. Asks: *"Why did our AWS bill increase?"*
3. AG-UI shows analysis
4. User asks follow-up questions
5. AG-UI generates report

**Executive Review (Both):**
1. Weekly report dashboard (Grafana)
2. Unexpected anomaly found
3. "Ask AI" for root cause (AG-UI)
4. Decision made based on AI analysis

### Data Source Sharing

Both UIs use the same data:

**Grafana Data Sources:**
- BigQuery (cost metrics, forecasts)
- PostgreSQL (tenants, accounts, workflow state)

**AG-UI Data Access:**
- MCP servers query same BigQuery tables
- Same PostgreSQL database for metadata
- Results cached in Redis (optional)

**No Duplication:** Data is stored once, queried by both UIs.

## Consequences

### Positive

- ✅ **Best of both worlds** - Speed + flexibility
- ✅ **User choice** - Different personas use different UI
- ✅ **Gradual adoption** - Grafana users can try AG-UI when ready
- ✅ **Familiar tools** - Grafana widely known
- ✅ **Innovation layer** - AG-UI is where we differentiate

### Negative

- ⚠️ **Two systems to maintain** - More code, more testing
- ⚠️ **Potential confusion** - Users might not know which to use
- ⚠️ **Inconsistency risk** - Data might look different in each UI

### Mitigation

**Maintenance:**
- Grafana is  low-maintenance (just SQL queries and configs)
- AG-UI is where we invest engineering effort
- Shared data layer reduces duplication

**User Confusion:**
- Clear guidance in docs: "Dashboard for monitoring, Chat for investigation"
- In-dashboard "Ask AI" buttons link to AG-UI with context
- Optional: Embed chat widget in Grafana sidebar

**Consistency:**
- Both UIs query same source of truth (BigQuery, PostgreSQL)
- No derived data in either UI
- Schema changes update both automatically

## Integration Points

**Cross-linking:**
- Grafana panels have "Ask AI about this" button
- Opens AG-UI with pre-filled context
- AG-UI can reference Grafana dashboards in responses

**Example:**
```
User: "What's causing the spike on February 1?"
AG-UI: "AWS Lambda costs increased 40%. Here's the breakdown:
        [detailed analysis]
        View trends: /dashboards/aws-lambda"
```

**Optional Embedding:**
- Can embed AG-UI chat widget in Grafana sidebar
- Allows asking questions without leaving dashboard
- Low priority for MVP

## Comparison to Alternatives

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Grafana Only | Simple, fast | Not flexible | Rejected |
| AG-UI Only | Flexible, AI-powered | Slow for routine checks | Rejected |
| **Hybrid** | **Best of both** | **Two systems** | **Accepted** ✅ |
| Custom Dashboard | Full control | Months to build | Rejected |

## Related Decisions

- [ADR-001: Use MCP Servers](001-use-mcp-servers.md) - AG-UI backend architecture
- [ADR-003: Use BigQuery](003-use-bigquery-not-timescaledb.md) - Shared data layer

## References

- [Grafana Documentation](https://grafana.com/docs/)
- [CopilotKit](https://copilotkit.ai/)
- [AG-UI Protocol](https://modelcontextprotocol.io/)

## Review

Revisit this if:
- 90%+ of users use only one UI (consolidate to that one)
- Grafana becomes a maintenance burden
- AG-UI response time drops to <500ms consistently (might replace Grafana)
- User feedback strongly prefers single interface
