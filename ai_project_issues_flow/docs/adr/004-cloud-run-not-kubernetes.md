# ADR-004: Cloud Run for Compute (Not Kubernetes)

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires compute infrastructure for running services. Options include:

1. Kubernetes (GKE)
2. Cloud Run (serverless containers)
3. Cloud Functions (FaaS)
4. Compute Engine (VMs)

## Decision

**Use Cloud Run** as the primary compute platform for all services.

## Rationale

| Factor | Cloud Run | GKE | Cloud Functions |
|--------|-----------|-----|----------------|
| Scale-to-zero | Yes | No (min nodes) | Yes |
| Container support | Full Docker | Full Docker | Limited |
| Ops overhead | Minimal | High (cluster mgmt) | Minimal |
| Cost at low scale | Near-zero | ~$70/month min | Per-invocation |
| Request timeout | 60 min | Unlimited | 9 min |

### Key Benefits

1. **Zero Idle Cost**: Scale-to-zero when not in use
2. **No Cluster Management**: No nodes, upgrades, or networking to manage
3. **Container Flexibility**: Run any Docker container
4. **Auto-scaling**: Handles traffic spikes automatically

## Consequences

### Positive
- Significant cost savings during MVP (no idle cluster)
- Faster deployment (no cluster provisioning)
- Simpler operations (managed platform)

### Negative
- Cold start latency (mitigated with min instances)
- Limited to HTTP workloads
- No persistent local storage

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [07-deployment-infrastructure.md](../core/07-deployment-infrastructure.md)
