# ADR-003: Use BigQuery for Metrics, Not TimescaleDB

## Status
Accepted

## Date
2026-01-22

## Context

For storing and querying cost metrics over time, we need a time-series database. Options considered:

1. **TimescaleDB** - PostgreSQL extension for time-series data
2. **BigQuery (GCP native)** - GCP's data warehouse
3. **InfluxDB** - Purpose-built time-series database
4. **Prometheus** - Monitoring time-series database

## Decision

We will use **BigQuery** as the primary storage and query engine for cost metrics, not a custom time-series database.

## Rationale

### Why BigQuery?

**It's Where the Data Already Is:**
- GCP billing export goes directly to BigQuery
- No ETL pipeline needed - zero sync lag
- Data is always up-to-date (GCP handles updates)

**Zero Infrastructure:**
- Fully managed by Google
- Auto-scaling query engine
- No servers to maintain
- Pay only for queries run

**Powerful Query Engine:**
- SQL interface familiar to developers
- Supports complex aggregations naturally
- Window functions for anomaly detection
- Materialized views for pre-aggregation

**Cost-Effective:**
- Storage: $0.02/GB/month (vs $0.10+ for Postgres storage)
- Queries: $5-20/month for our scale
- No compute costs when idle
- Built-in compression

**Time-Series Features:**
- Partitioning by date (automatic with billing export)
- Clustering for query performance
- Continuous queries for rollups
- Column-based storage (efficient for time-series)

### Why Not TimescaleDB?

**Redundant Data Storage:**
- Would need to sync from BigQuery → TimescaleDB
- Data exists in 2 places (synchronization complexity)
- 24-48 hour delay for billing data anyway

**Infrastructure Overhead:**
- Need to run and maintain PostgreSQL server
- Backup and HA complexity
- Monitoring and alerting setup
- Costs money even when idle

**Limited Value-Add:**
- TimescaleDB excels at high-frequency metrics (seconds)
- Our data is daily/hourly granularity (not real-time)
- BigQuery already optimized for this use case

### Why Not InfluxDB / Prometheus?

**Wrong Data Source:**
- These databases expect metrics pushed to them
- Our data comes from GCP billing (pull from BigQuery)
- Would need custom ingestion pipeline

**Over-engineering:**
- InfluxDB great for IoT/monitoring (millisecond precision)
- We have business metrics (hourly/daily precision)
- BigQuery is perfect for this scale

## Implementation

### BigQuery Schema

```sql
-- GCP automatically creates this table
-- gcp_billing_export_v1_<BILLING_ACCOUNT_ID>

SELECT 
  DATE(usage_start_time) as date,
  project.id as project_id,
  service.description as service,
  SUM(cost) as total_cost
FROM `billing_export.gcp_billing_export_v1_*`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY date, project_id, service
ORDER BY date DESC, total_cost DESC
```

### Pre-computed Aggregates

Use BigQuery scheduled queries to create rollups:

```sql
-- Daily rollup (runs every 4 hours)
CREATE OR REPLACE TABLE cost_daily AS
SELECT 
  DATE(usage_start_time) as date,
  project.id as project_id,
 service.description as service,
  location.region as region,
  SUM(cost) as total_cost
FROM `billing_export.gcp_billing_export_v1_*`
WHERE DATE(usage_start_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY date, project_id, service, region;

-- Monthly rollup (runs daily)
CREATE OR REPLACE TABLE cost_monthly AS
SELECT 
  FORMAT_DATE('%Y-%m', DATE(usage_start_time)) as month,
  project.id as project_id,
  service.description as service,
  SUM(cost) as total_cost
FROM `billing_export.gcp_billing_export_v1_*`
GROUP BY month, project_id, service;
```

### Query Performance

- Raw table: milliseconds (with partitioning)
- Daily rollup: <100ms for 90 days
- Monthly rollup: <50ms for 3 years

Plenty fast for interactive queries!

## Consequences

### Positive

- ✅ **No sync lag** - Data is always current
- ✅ **Zero infrastructure** - One less service to manage
- ✅ **Lower costs** - $5-20/month vs $50-100/month for TimescaleDB
- ✅ **Simpler architecture** - Fewer moving parts
- ✅ **Native GCP integration** - Uses platform tools

### Negative

- ⚠️ **GCP lock-in** - Adds another GCP dependency
- ⚠️ **Query costs** - Pay per query (though minimal at our scale)
- ⚠️ **Less control** - Can't optimize schema beyond partitioning

### Mitigation

**GCP Lock-in:**
- When we add AWS/Azure, keep same pattern:
  - AWS: Use Athena (query S3-based Cost & Usage Reports)
  - Azure: Use Azure Data Explorer / Log Analytics
- MCP server abstracts the difference from agent

**Query Costs:**
- Use materialized views for common queries
- Cache results in Redis (L2 cache)
- Monitor query costs in billing dashboard
- At 1000s of queries/day, still <$50/month

## Cost Comparison

| Solution | Monthly Cost | Complexity | Maintenance |
|----------|--------------|------------|-------------|
| BigQuery | $5-20 | Low | Zero |
| TimescaleDB (managed) | $50-150 | Medium | Low |
| TimescaleDB (self-hosted) | $30-80 | High | High |
| InfluxDB (managed) | $80-200 | High | Low |

For our scale (10-100 companies, 100-1000 projects), BigQuery is the clear winner.

## Multi-Cloud Considerations

This decision is GCP-specific and intentional:

- **AWS**: Will use Athena (query CUR files in S3)
- **Azure**: Will use Azure Monitor Logs or Data Explorer
- **Pattern**: MCP server for each cloud uses that cloud's native query engine

No need to force a single database across all clouds.

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| TimescaleDB | Good for real-time metrics | Redundant, complex | Rejected |
| InfluxDB | High write throughput | Overkill for our use case | Rejected |
| Prometheus | Great for monitoring | Wrong data model | Rejected |
| **BigQuery** | **Native, zero-ops** | **GCP lock-in (acceptable)** | **Accepted** ✅ |

## Related Decisions

- [ADR-002: GCP-Only First](002-gcp-only-first.md) - Allows GCP-specific choices
- [ADR-004: Cloud Run Deployment](004-cloud-run-not-kubernetes.md) - Consistent with GCP-native approach

## References

- [BigQuery Billing Export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery)
- [BigQuery Cost Optimization](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [GCP Setup Guide](../../GCP-only/setup-guide.md)

## Review

Revisit this if:
- BigQuery costs exceed $100/month
- Query latency becomes problematic (>2 seconds)
- Multi-cloud expansion requires unified database
- We need millisecond-granularity data
