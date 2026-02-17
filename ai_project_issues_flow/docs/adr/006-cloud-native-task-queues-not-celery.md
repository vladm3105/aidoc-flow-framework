# ADR-006: Cloud Tasks for Queues (Not Celery)

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires task queue infrastructure for async processing. Options include:

1. Celery + Redis
2. Cloud Tasks (GCP managed)
3. Cloud Pub/Sub
4. AWS SQS

## Decision

**Use Cloud Tasks** as the primary task queue for async operations.

## Rationale

| Factor | Cloud Tasks | Celery + Redis | Pub/Sub |
|--------|-------------|----------------|--------|
| Managed | Fully | Self-managed | Fully |
| Redis dependency | No | Yes | No |
| HTTP targets | Native | Via worker | Push subscription |
| Scheduling | Built-in | Celery Beat | Cloud Scheduler |
| Cost | Pay-per-task | Redis instance | Pay-per-message |

### Key Benefits

1. **No Redis**: Eliminates Redis infrastructure and costs
2. **HTTP Native**: Tasks invoke Cloud Run services directly
3. **Built-in Scheduling**: Delayed execution without additional services
4. **Managed Retries**: Automatic retry with exponential backoff

## Consequences

### Positive
- Reduced infrastructure complexity
- Lower operational costs
- Native GCP integration

### Negative
- GCP-specific (no multi-cloud portability)
- Less flexible than Celery for complex workflows
- Limited to HTTP task handlers

## References

- [Cloud Tasks Documentation](https://cloud.google.com/tasks/docs)
- [07-deployment-infrastructure.md](../core/07-deployment-infrastructure.md)
