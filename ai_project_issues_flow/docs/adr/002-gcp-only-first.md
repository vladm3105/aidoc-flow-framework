# ADR-002: GCP as Home Cloud (GCP-First Strategy)

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires a "home cloud" for hosting infrastructure. Options include:

1. AWS (largest market share)
2. Azure (enterprise integration)
3. GCP (AI/ML focus, generous free tier)
4. Multi-cloud from day one

## Decision

**Use GCP as the home cloud** for all platform infrastructure. Other clouds (AWS, Azure) are monitored but not used for hosting.

## Rationale

| Factor | GCP | AWS | Azure |
|--------|-----|-----|-------|
| Free tier | $300 credit + always-free | 12-month limited | $200 credit |
| Scale-to-zero | Cloud Run native | Fargate (limited) | Container Apps |
| BigQuery | Native, 1TB free/month | Athena (pay-per-query) | Synapse (complex) |
| AI/ML services | Vertex AI, Gemini | Bedrock | Azure OpenAI |
| Serverless | Cloud Functions v2 | Lambda | Functions |

### Key Benefits

1. **Cost Efficiency**: Scale-to-zero Cloud Run reduces idle costs
2. **BigQuery**: Native billing export, 1TB free queries/month
3. **AI-First**: Strong Vertex AI and Gemini integration
4. **Simplicity**: Single cloud for MVP reduces complexity

## Consequences

### Positive
- Lower operational costs during MVP
- Simpler infrastructure management
- Native GCP billing integration

### Negative
- Team may need GCP upskilling
- Some enterprise customers prefer AWS/Azure hosting
- Potential vendor lock-in concerns

## References

- [GCP Free Tier Documentation](https://cloud.google.com/free)
- [07-deployment-infrastructure.md](../core/07-deployment-infrastructure.md)
