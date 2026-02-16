# ADR-004: Use Serverless Containers, Not Kubernetes

## Status
Accepted

## Date
2026-01-25

## Context

For deploying the MCP server and conversational agent, we need a container orchestration platform. Options:

1. **Kubernetes (GKE, EKS, AKS)** - Full Kubernetes cluster
2. **Serverless Containers** - Cloud Run / ECS Fargate / Azure Container Apps
3. **Compute Engine VMs** - Traditional VMs
4. **Functions** - Function-as-a-Service

## Decision

We will deploy containers to **serverless container platforms**, not Kubernetes. For GCP as the first home cloud, this means **Cloud Run**.

## Rationale

### Why Cloud Run?

**Simplicity:**
- Deploy with a single command: `gcloud run deploy`
- No cluster management, no node pools, no kubectl
- Perfect for team of 2-3 developers

**Cost-Effective:**
- Pay per request, not per server
- Scales to zero when idle
- Estimated cost: $10-50/month (vs $100+ for always-on GKE)

**Auto-Scaling:**
- 0 to 1000 instances automatically
- Handles traffic spikes without config
- No capacity planning needed

**Fully Managed:**
- Google handles: OS patches, security, load balancing, SSL
- We just push containers
- Built-in monitoring and logging

**Fast Deployments:**
- New version deployed in <2 minutes
- Easy rollbacks with revision history
- Gradual rollouts supported

### Why Not Kubernetes?

**Over-engineering for MVP:**
- Kubernetes is overkill for 2 microservices
- Adds weeks of setup and learning curve
- Complex YAML configuration

**Higher Costs:**
- GKE cluster: $70/month minimum (control plane)
- 3 nodes × $30/month = $90/month
- Total: $160/month just to run 2 containers

**Operational Burden:**
- Need DevOps expertise
- Cluster upgrades, node management
- Monitoring, logging configuration
- Security hardening

**Slower Development:**
- kubectl, helm charts, ingress controllers
- Local development complexity (minikube/kind)
- Learning curve for team

### Why Not VMs?

- Manual scaling required
- OS maintenance overhead
- Less secure (more attack surface)
- No built-in load balancing

### Why Not Cloud Functions?

- Better for event-driven, not HTTP servers
- 9-minute timeout limit
- Less control over runtime environment
- Cold start issues for MCP server

## Cloud Alternatives

This pattern applies across all home cloud options:

| Home Cloud | Serverless Container Platform | Notes |
|------------|-------------------------------|-------|
| **GCP** | **Cloud Run** | Knative-based, simplest deployment |
| **AWS** | **ECS Fargate** or **App Runner** | Fargate for control, App Runner for simplicity |
| **Azure** | **Azure Container Apps** | Similar to Cloud Run, built on KEDA |

All three offer:
- Pay-per-use pricing (vs always-on Kubernetes)
- Auto-scaling from zero
- Managed infrastructure (no node pools, no kubectl)
- Fast deployments (< 2 minutes)

## Implementation

### Cloud Run Configuration

```yaml
# service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: gcp-cost-mcp-server
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"    # Scale to zero
        autoscaling.knative.dev/maxScale: "10"   # Max 10 instances
    spec:
      serviceAccountName: gcp-cost-agent@project.iam.gserviceaccount.com
      containers:
      - image: gcr.io/project/gcp-cost-mcp-server:latest
        env:
        - name: GCP_ORG_ID
          value: "123456789"
        resources:
          limits:
            memory: 512Mi
            cpu: "1"
```

### Deployment Command

```bash
# Build and push
gcloud builds submit --tag gcr.io/project/gcp-cost-mcp-server

# Deploy
gcloud run deploy gcp-cost-mcp-server \
  --image gcr.io/project/gcp-cost-mcp-server \
  --platform managed \
  --region us-central1 \
  --service-account gcp-cost-agent@project.iam.gserviceaccount.com \
  --max-instances 10 \
  --memory 512Mi \
  --timeout 60s \
  --allow-unauthenticated  # or use IAM auth
```

Done in 2 minutes! No YAML, no kubectl, no cluster.

## Consequences

### Positive

- ✅ **Deploy in minutes** vs days for GKE setup
- ✅ **$10-50/month** vs $160+/month for Kubernetes
- ✅ **Zero ops burden** - Google manages everything
- ✅ **Perfect for MVP** - Can always migrate to GKE later if needed
- ✅ **Auto-scaling** handles traffic without configuration

### Negative

- ⚠️ **Less control** - Can't customize load balancing, networking
- ⚠️ **Vendor lock-in** - Cloud Run is GCP-specific (but so is everything else in our stack)
- ⚠️ **Request timeout** - Max 60 minutes per request (fine for our use case)
- ⚠️ **Cold starts** - First request after idle has ~1 second latency

### Mitigation

**Cold Starts:**
- Solution: Set `minScale: 1` for production (1 instance always warm)
- Cost: +$5/month
- Result: <100ms latency for all requests

**Limited Control:**
- For MVP, Cloud Run features are sufficient
- If we need advanced networking, can migrate to GKE later
- Migration path exists (both use containers)

## When to Reconsider

Move to Kubernetes when:
- ❌ Traffic exceeds 1000 requests/second sustained
- ❌ Need custom load balancing (geo-routing, advanced A/B testing)
- ❌ Need stateful services (databases, caches) in cluster
- ❌ Custom networking requirements (VPC peering, VPN)
- ❌ Multi-region active-active deployment

For MVP and likely first 1-2 years: **None of these apply**.

## Cost Comparison

### Cloud Run (Our Choice)

```
Assumptions:
- 100,000 requests/month
- 500ms average request time
- 512 MB memory per instance

Costs:
- Requests: 100K × $0.40/million = $0.04
- CPU time: 50,000 seconds × $0.00002400/sec = $1.20
- Memory: 50,000 sec × 512MB × $0.00000250/sec/MB = $0.64
- Total: ~$2/month

With minScale=1 (always warm):
- +$5/month
- Total: ~$7/month
```

### GKE Alternative

```
Cluster:
- Control plane: $70/month
- 3 nodes (n1-standard-1): 3 × $30 = $90/month
- Total: $160/month minimum

Even at zero traffic, we pay $160/month.
```

**Cloud Run is 20x cheaper** for our traffic levels.

## Migration Path

If we outgrow Cloud Run:

**Phase 1: Cloud Run** (now)
- Simple deployment
- $10-50/month

**Phase 2: Cloud Run + uptime monitoring** (6-12 months)
- Add uptime checks to keep instances warm
- Set minScale=2 for HA
- Add load testing
- Cost: $50-100/month

**Phase 3: GKE Autopilot** (12-24 months if needed)
- Managed Kubernetes (easier than full GKE)
- Same containers, different orchestrator  
- Cost: $100-300/month

**Phase 4: Full GKE** (24+ months if needed)
- Complete control
- Multi-region, advanced networking
- When we have dedicated DevOps team
- Cost: $500-2000/month

Right now we're in Phase 1. No rush.

## Alternatives Considered

| Alternative | Cost/Month | Complexity | Scalability | Decision |
|-------------|------------|------------|-------------|----------|
| GKE | $160+ | High | Excellent | Rejected (over-engineering) |
| GKE Autopilot | $100+ | Medium | Excellent | Deferred (Phase 3) |
| **Cloud Run** | **$10-50** | **Low** | **Good** | **Accepted** ✅ |
| Compute Engine | $50+ | Medium | Manual | Rejected |
| Cloud Functions | $5-20 | Low | Good | Rejected (timeout limits) |

## Related Decisions

- [ADR-001: Use MCP Servers](001-use-mcp-servers.md) - What we're deploying
- [ADR-002: GCP-Only First](002-gcp-only-first.md) - Allows GCP-specific deployment
- [ADR-003: Use BigQuery](003-use-bigquery-not-timescaledb.md) - Consistent with GCP-native approach

## References

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run vs GKE](https://cloud.google.com/blog/products/serverless/when-to-use-google-cloud-run-over-kubernetes)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)

## Review

Revisit this decision when:
- Traffic exceeds 500 requests/second sustained
- Cold start latency becomes a user complaint
- We need features Cloud Run doesn't support
- Team grows to 8+ engineers (can afford DevOps focus)
