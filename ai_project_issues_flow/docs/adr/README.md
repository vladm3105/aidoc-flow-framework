# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) documenting the key technical decisions made in the AI Cost Monitoring project.

## What are ADRs?

ADRs are documents that capture important architectural decisions along with their context and consequences. They help future developers (including future you) understand:

- **Why** a decision was made
- **What** alternatives were considered
- **What** the trade-offs are

## Current ADRs

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-use-mcp-servers.md) | Use MCP Servers Instead of REST APIs | Accepted | 2026-01-15 |
| [002](002-gcp-only-first.md) | Start with GCP-Only, Not Multi-Cloud | Accepted | 2026-01-20 |
| [003](003-use-bigquery-not-timescaledb.md) | Use BigQuery for Metrics, Not TimescaleDB | Accepted | 2026-01-22 |
| [004](004-cloud-run-not-kubernetes.md) | Deploy to Cloud Run, Not Kubernetes | Accepted | 2026-01-25 |
| [005](005-use-litellm-for-llms.md) | Use LiteLLM for LLM Abstraction | Accepted | 2026-01-28 |
| [006](006-cloud-native-task-queues-not-celery.md) | Cloud-Native Task Queues, Not Celery | Accepted | 2026-01-30 |
| [007](007-grafana-plus-agui-hybrid.md) | Grafana + AG-UI Hybrid Dashboard | Accepted | {DATE} |
| [008](008-otel-gen-ai-conventions.md) | OTEL Gen-AI Semantic Conventions | Accepted | {DATE} |

## Decision Categories

### Integration & Architecture (ADR-001, 002)
- How we integrate with cloud providers
- Whether to support single or multiple clouds

### Data & Storage (ADR-003)
- Where we store cost metrics
- Database and storage choices

### Infrastructure & Deployment (ADR-004)
- Where and how we deploy services
- Container orchestration platform

## When to Create an ADR

Create a new ADR when making a decision that:

1. **Impacts future development** - Hard to change later
2. **Has multiple viable alternatives** - Not obvious which to choose
3. **Requires explanation** - Team members will ask "why did we do it this way?"
4. **Involves trade-offs** - Pros and cons to document

## ADR Template

```markdown
# ADR-XXX: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Date
YYYY-MM-DD

## Context
What problem are we solving? What constraints exist?

## Decision
What did we decide to do?

## Rationale
Why did we make this decision? What alternatives did we consider?

## Consequences
What are the positive and negative outcomes?

## Related Decisions
Links to other ADRs

## Review
When should we revisit this decision?
```

## ADR Process

1. **Propose** - Create draft ADR with Status: Proposed
2. **Discuss** - Team reviews and provides feedback
3. **Decide** - Update Status to Accepted (or Rejected)
4. **Document** - Keep updated as situation evolves
5. **Supersede** - Mark as Superseded if decision changes

## Related Documentation

- [Project Review & Recommendations](../../project_review_recommendations.md)
- [GCP Setup Guide](../../GCP-only/setup-guide.md)
- [Sample Queries](../../GCP-only/sample-queries.md)

---

**Note:** ADRs are living documents. If a decision needs to change, don't delete the old ADR. Instead, mark it as "Superseded" and create a new ADR explaining the new direction.
