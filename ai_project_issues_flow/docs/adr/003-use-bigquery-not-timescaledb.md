# ADR-003: BigQuery for Analytics (Not TimescaleDB)

**Status**: Accepted
**Date**: {DATE}
**Decision Makers**: {DECISION_MAKERS}

## Context

The platform requires a database for cost analytics and billing data. Options include:

1. TimescaleDB (time-series optimized PostgreSQL)
2. BigQuery (serverless data warehouse)
3. ClickHouse (OLAP database)
4. Standard PostgreSQL

## Decision

**Use BigQuery** as the primary analytics database for billing and cost data.

## Rationale

| Factor | BigQuery | TimescaleDB | ClickHouse |
|--------|----------|-------------|------------|
| GCP Billing Export | Native | Manual ETL | Manual ETL |
| Serverless | Yes | No (managed instance) | No |
| Free tier | 1TB queries/month | None | None |
| Scaling | Automatic | Manual | Manual |
| Setup complexity | Console click | Provision + configure | Provision + configure |

### Key Benefits

1. **Native Billing Integration**: GCP billing exports directly to BigQuery
2. **Zero Infrastructure**: No database servers to manage
3. **Cost Efficiency**: 1TB free queries/month covers MVP usage
4. **SQL Standard**: Familiar query language

## Consequences

### Positive
- Immediate access to GCP billing data
- No database administration overhead
- Scales automatically with data volume

### Negative
- Query latency higher than TimescaleDB for small queries
- Limited real-time streaming (use Pub/Sub for events)
- GCP-specific (no multi-cloud portability)

## References

- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [GCP Billing Export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery)
