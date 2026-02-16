# ADR-002: GCP as First Home Cloud (Not Multi-Cloud Day 1)

## Status
Accepted

## Date
2026-01-20

## Context

We have detailed specifications for two different architectures:

1. **Full multi-cloud platform** - Support AWS, Azure, GCP, and Kubernetes from day 1
   - 4-layer agent hierarchy
   - Multiple cloud-specific agents
   - Complex routing and coordination
   - Estimated timeline: 9 months

2. **GCP as first home cloud** - Single cloud deployment with multi-cloud monitoring
   - GCP hosts the platform infrastructure
   - Platform can monitor AWS, Azure, GCP, Kubernetes costs
   - Simplified architecture
   - Estimated timeline: 6 weeks

The question: Which should we build first?

## Decision

We will **build GCP as the first home cloud** for the platform deployment, while supporting multi-cloud cost monitoring from day 1. The platform architecture is designed to support AWS/Azure as alternative home clouds later.

## Rationale

**Important Distinction:**
- **Home Cloud**: Where the platform itself runs (GCP initially)
- **Monitored Clouds**: What clouds the platform can monitor (AWS, Azure, GCP, K8s from day 1)

### Why GCP as First Home Cloud?

**Faster Time to Market:**
- 6 weeks to MVP vs 9 months for multi-home-cloud support
- Can validate product-market fit quickly
- Start generating revenue/feedback sooner

**Lower Complexity:**
- Single cloud infrastructure to manage
- No multi-cloud deployment complexity
- Simpler testing and operations

**Market Validation:**
- Prove the value prop with one deployment cloud first
- Many SMBs prefer single-cloud operations
- Can test pricing and features with real users

**GCP Advantages for Home Cloud:**
- Excellent built-in tools (BigQuery, Secret Manager, Cloud Tasks)
- Best developer experience (compared to AWS/Azure)
- Serverless-first (Cloud Run, Cloud Functions)
- We know GCP best

**Financial Prudence:**
- Lower infrastructure costs during beta
- Smaller team size needed (2-3 devs vs 6-8)
- Less risk if product doesn't work

### Why Not Multi-Cloud Immediately?

**Over-engineering Risk:**
- Building complex orchestration before proving need
- 9 months of development with zero user feedback
- Risk of building wrong features

**Resource Constraints:**
- Small team can't maintain 3 cloud integrations
- Quality would suffer trying to do all clouds at once

**Market Reality:**
- Most SMBs use primarily one cloud
- Multi-cloud users are enterprise (different segment)
- Can add clouds incrementally as demand grows

## Home Cloud Expansion Path

We're not abandoning multi-home-cloud support, just deferring it:

**Phase 1: GCP Home Cloud (Weeks 1-6)**
- Platform runs on GCP (Cloud Run, BigQuery, Cloud SQL)
- Monitors AWS, Azure, GCP, Kubernetes costs
- 6 core features
- Beta with 10-20 companies

**Phase 2: Production-ready GCP (Weeks 7-12)**
- Security hardening
- Multi-tenant support
- Polish UI/UX
- Scale to 100+ companies

**Phase 3: AWS Home Cloud Option (Months 4-6)**
- Create AWS deployment guide (ECS Fargate, RDS, Athena)
- Terraform modules for AWS
- Users can choose GCP or AWS as home cloud

**Phase 4: Azure Home Cloud Option (Months 7-9)**
- Create Azure deployment guide (Container Apps, PostgreSQL, Synapse)
- Terraform modules for Azure
- Users can choose GCP, AWS, or Azure as home cloud

## Consequences

### Positive

- ✅ **Ship in 6 weeks** instead of 9 months
- ✅ **Simpler codebase** easier to maintain
- ✅ **Focus on quality** over breadth
- ✅ **Learn from users** before investing in other clouds
- ✅ **Lower burn rate** during validation phase

### Negative

- ⚠️ **Smaller addressable market** initially (GCP-only companies)
- ⚠️ **May lose multi-cloud deals** to competitors
- ⚠️ **Architectural pivot needed** for multi-cloud (but designed for it)

### Mitigation

To make multi-cloud expansion easier later:

**1. Design Abstraction:**
```python
# Generic cost interface (works for any cloud)
class CloudCostProvider(ABC):
    @abstractmethod
    def get_cost_summary(self, **params) -> CostSummary:
        pass
    
# GCP implementation
class GCPCostProvider(CloudCostProvider):
    def get_cost_summary(self, **params):
        # BigQuery-specific logic
        pass

# Future: AWS implementation
class AWSCostProvider(CloudCostProvider):
    def get_cost_summary(self, **params):
        # Cost Explorer-specific logic
        pass
```

**2. MCP Server Pattern:**
- Each cloud gets its own MCP server
- Same tool signatures across clouds
- Agent doesn't care which cloud

**3. Database Schema:**
- `cloud_provider` column in all tables
- Already multi-tenant ready
- Easy to add AWS/Azure data

## Target Customers

GCP-only MVP targets:

✅ **Good fit:**
- SMBs primarily on GCP
- Google Workspace users (natural GCP affinity)
- AI/ML companies (heavy GCP users)
- Startups in Google Cloud credits program

❌ **Not a fit yet:**
- Multi-cloud enterprises
- AWS-primary companies
- Azure-primary companies

We can expand to these segments in Phases 3-4.

## Success Criteria

We'll know this decision was right if:

- 🎯 Ship MVP in <8 weeks
- 🎯 Get 50+ beta sign-ups (GCP users)
- 🎯 10+ paying customers by Month 3
- 🎯 Customer satisfaction score >8/10
- 🎯 AWS/Azure requests validate multi-cloud demand

We'll know we need to pivot if:
- ⚠️ Can't find enough GCP-only customers
- ⚠️ Lose deals primarily due to lack of AWS/Azure
- ⚠️ GCP-only companies don't have cost pain

## Alternatives Considered

| Alternative | Timeline | Complexity | Risk | Decision |
|-------------|----------|------------|------|----------|
| Multi-cloud from day 1 | 9 months | High | High | Rejected |
| AWS-only first | 6 weeks | Medium | Medium | Rejected (we know GCP better) |
| GCP + AWS (2 clouds) | 3 months | Medium | Medium | Rejected (still too slow) |
| **GCP-only MVP** | **6 weeks** | **Low** | **Low** | **Accepted** ✅ |

## Related Decisions

- [ADR-001: Use MCP Servers](001-use-mcp-servers.md) - Makes multi-cloud expansion easier
- [ADR-003: Use BigQuery, Not TimescaleDB](003-no-custom-database.md) - GCP-specific decision
- [ADR-004: Cloud Run Deployment](004-cloud-run-not-kubernetes.md) - GCP-specific deployment

## References

- [GCP Cost Monitoring Spec (GCP-only)](../GCP-only/gcp-agent-complete-specification.md)
- [Multi-Cloud Architecture](../ai-cost-monitoring-description.md)
- [MVP Prioritization](../project_review_recommendations.md#6-recommended-mvp-scope)

## Review

Revisit this decision:
- After 3 months of GCP-only product
- If 30%+ of sales conversations request multi-cloud
- When we have 5+ FTEs to support multi-cloud development
