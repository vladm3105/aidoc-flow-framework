# PRD-000: Platform Threshold Registry Template

| Item | Details |
|------|---------|
| **Document ID** | PRD-000 |
| **Title** | Platform Threshold Registry Template |
| **Version** | 1.0 |
| **Status** | Template |
| **Layer** | 2 (Product Requirements Document) |
| **Created** | {DATE} |
| **Author** | {AUTHOR} |

---

## Document Control

| Item | Details |
|------|---------|
| **Purpose** | Centralized threshold registry for {PROJECT_NAME} |
| **Authority** | This registry is authoritative for all threshold values referenced via `@threshold` tags |
| **Scope** | All business-critical quantitative values used across SDD documentation |

### Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {DATE} | {AUTHOR} | Initial threshold registry |

---

## Threshold Registry Overview

### Purpose

This document serves as the **single source of truth** for all configurable, business-critical values across the project documentation. All SDD artifacts (EARS, BDD, SYS, REQ, SPEC) **MUST** reference this registry using `@threshold` tags instead of hardcoding numeric values.

### Governance Rules

1. **No Magic Numbers**: All quantitative business-critical values in requirements documents MUST use `@threshold` references
2. **Single Source**: This registry is the authoritative source - conflicting values elsewhere are invalid
3. **Change Control**: All threshold changes require version update and change log entry
4. **Traceability**: All `@threshold` references must use format `@threshold: PRD.NNN.category.key`

### @threshold Tag Format

```markdown
@threshold: PRD.NNN.category.subcategory.key
```

**Examples**:
- `@threshold: PRD.035.perf.api.p95_latency`
- `@threshold: PRD.035.timeout.circuit_breaker.threshold`
- `@threshold: PRD.035.compliance.travel_rule.amount`

---

## Threshold Key Naming Convention

| Level | Format | Example |
|-------|--------|---------|
| Category | lowercase | `perf`, `timeout`, `sla`, `compliance`, `limit` |
| Subcategory | dot-separated | `perf.api`, `timeout.circuit_breaker` |
| Key | dot-separated | `perf.api.p95_latency`, `timeout.circuit_breaker.threshold` |

### Standard Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `perf.*` | Performance thresholds | Latency (p50/p95/p99), throughput, IOPS |
| `timeout.*` | Timeout configurations | Connection, read, write, circuit breaker |
| `sla.*` | SLA targets | Uptime, availability, recovery time |
| `limit.*` | Rate limits, resource limits | Requests/sec, connections, memory |
| `compliance.*` | Regulatory thresholds | Transaction limits, reporting thresholds |
| `resource.*` | Resource utilization limits | CPU, memory, storage, bandwidth |
| `retry.*` | Retry configurations | Max attempts, backoff multipliers, delays |
| `batch.*` | Batch processing limits | Batch sizes, processing windows |

---

## 1. Performance Thresholds

### 1.1 API Response Times

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `perf.api.p50_latency` | {VALUE} | ms | Median response time |
| `perf.api.p95_latency` | {VALUE} | ms | 95th percentile |
| `perf.api.p99_latency` | {VALUE} | ms | 99th percentile |
| `perf.api.max_latency` | {VALUE} | ms | Maximum acceptable |

### 1.2 Database Query Times

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `perf.db.query.p95_latency` | {VALUE} | ms | 95th percentile query time |
| `perf.db.query.max_latency` | {VALUE} | ms | Maximum query time |
| `perf.db.connection.timeout` | {VALUE} | ms | Connection timeout |

### 1.3 Throughput Targets

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `perf.throughput.target_rps` | {VALUE} | req/s | Target requests per second |
| `perf.throughput.peak_rps` | {VALUE} | req/s | Peak capacity |
| `perf.throughput.sustained_rps` | {VALUE} | req/s | Sustained capacity |

---

## 2. Reliability Thresholds

### 2.1 SLA Targets

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `sla.uptime.target` | {VALUE} | % | Monthly uptime target |
| `sla.availability.target` | {VALUE} | % | Service availability |
| `sla.rto` | {VALUE} | minutes | Recovery Time Objective |
| `sla.rpo` | {VALUE} | minutes | Recovery Point Objective |

### 2.2 Error Rate Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `sla.error_rate.max` | {VALUE} | % | Maximum error rate |
| `sla.success_rate.min` | {VALUE} | % | Minimum success rate |

---

## 3. Timeout Configurations

### 3.1 Circuit Breaker

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `timeout.circuit_breaker.threshold` | {VALUE} | failures | Failures before open |
| `timeout.circuit_breaker.reset` | {VALUE} | ms | Reset timeout |
| `timeout.circuit_breaker.half_open_requests` | {VALUE} | count | Requests in half-open |

### 3.2 Connection Timeouts

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `timeout.connection.default` | {VALUE} | ms | Default connection timeout |
| `timeout.read.default` | {VALUE} | ms | Default read timeout |
| `timeout.write.default` | {VALUE} | ms | Default write timeout |
| `timeout.idle.max` | {VALUE} | ms | Maximum idle time |

### 3.3 Request Timeouts

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `timeout.request.sync` | {VALUE} | ms | Synchronous request timeout |
| `timeout.request.async` | {VALUE} | ms | Async request timeout |
| `timeout.request.long_running` | {VALUE} | ms | Long-running operations |

---

## 4. Rate Limits

### 4.1 API Rate Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `limit.api.requests_per_second` | {VALUE} | req/s | Per-client rate limit |
| `limit.api.requests_per_minute` | {VALUE} | req/min | Per-client per minute |
| `limit.api.burst_size` | {VALUE} | requests | Burst allowance |

### 4.2 Connection Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `limit.connection.max_per_client` | {VALUE} | count | Max connections per client |
| `limit.connection.max_total` | {VALUE} | count | Max total connections |
| `limit.connection.pool_size` | {VALUE} | count | Connection pool size |

---

## 5. Resource Limits

### 5.1 Memory Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `resource.memory.max_heap` | {VALUE} | MB | Maximum heap size |
| `resource.memory.warning_threshold` | {VALUE} | % | Warning at % usage |
| `resource.memory.critical_threshold` | {VALUE} | % | Critical at % usage |

### 5.2 CPU Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `resource.cpu.max_utilization` | {VALUE} | % | Maximum CPU utilization |
| `resource.cpu.warning_threshold` | {VALUE} | % | Warning threshold |

### 5.3 Storage Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `resource.storage.max_size` | {VALUE} | GB | Maximum storage |
| `resource.storage.warning_threshold` | {VALUE} | % | Warning at % usage |

---

## 6. Retry Configurations

### 6.1 Retry Policy

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `retry.max_attempts` | {VALUE} | count | Maximum retry attempts |
| `retry.initial_delay` | {VALUE} | ms | Initial retry delay |
| `retry.max_delay` | {VALUE} | ms | Maximum retry delay |
| `retry.backoff_multiplier` | {VALUE} | multiplier | Exponential backoff factor |
| `retry.jitter_factor` | {VALUE} | multiplier | Jitter factor (0.0-1.0) |

---

## 7. Batch Processing

### 7.1 Batch Sizes

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `batch.default_size` | {VALUE} | records | Default batch size |
| `batch.max_size` | {VALUE} | records | Maximum batch size |
| `batch.processing_window` | {VALUE} | ms | Processing window |

---

## 8. Business/Compliance Thresholds

### 8.1 Compliance Thresholds

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `compliance.{regulation}.{threshold}` | {VALUE} | {UNIT} | {DESCRIPTION} |

**Example entries**:

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `compliance.travel_rule.amount` | 3000 | USD | Travel Rule reporting threshold |
| `compliance.kyc.verification_timeout` | 24 | hours | KYC verification deadline |

### 8.2 Business Limits

| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `limit.transaction.max_amount` | {VALUE} | USD | Maximum transaction amount |
| `limit.daily.max_transactions` | {VALUE} | count | Daily transaction limit |

---

## 9. Environment-Specific Overrides

### 9.1 Development Overrides

| Key | Override Value | Production Value | Notes |
|-----|----------------|------------------|-------|
| `perf.api.p95_latency` | 1000 | {PROD_VALUE} | Relaxed for dev |
| `timeout.connection.default` | 30000 | {PROD_VALUE} | Extended for debugging |

### 9.2 Staging Overrides

| Key | Override Value | Production Value | Notes |
|-----|----------------|------------------|-------|
| `limit.api.requests_per_second` | 10 | {PROD_VALUE} | Reduced for staging |

---

## 10. Threshold Change Log

| Date | Key | Old Value | New Value | Reason | Author |
|------|-----|-----------|-----------|--------|--------|
| {DATE} | {KEY} | {OLD} | {NEW} | {REASON} | {AUTHOR} |

---

## 11. Usage Examples

### 11.1 EARS Statement

```markdown
WHEN the API receives a request,
THE system SHALL respond
WITHIN @threshold: PRD.NNN.perf.api.p95_latency.
```

### 11.2 BDD Scenario

```gherkin
@threshold: PRD.NNN.perf.api.p95_latency
Scenario: API responds within performance threshold
  Given the system is under normal load
  When a client sends a request
  Then the response time SHOULD be less than @threshold: PRD.NNN.perf.api.p95_latency
```

### 11.3 SYS Requirement

```markdown
**SYS.NNN.001**: API Response Time
- p95 latency: @threshold: PRD.NNN.perf.api.p95_latency
- p99 latency: @threshold: PRD.NNN.perf.api.p99_latency
```

### 11.4 REQ Requirement

```markdown
**Performance Target**: Response time < @threshold: PRD.NNN.perf.api.p95_latency
**Timeout**: @threshold: PRD.NNN.timeout.request.sync
```

### 11.5 SPEC Configuration

```yaml
performance:
  p95_latency_ms: "@threshold: PRD.NNN.perf.api.p95_latency"
timeout:
  request_ms: "@threshold: PRD.NNN.timeout.request.sync"
```

---

## 12. Traceability

### 12.1 Upstream References

| Tag | Reference | Description |
|-----|-----------|-------------|
| @brd | BRD-NNN:REQUIREMENT-ID | Business requirements driving thresholds |

### 12.2 Downstream Consumers

This threshold registry is consumed by:

| Document Type | Layer | How Thresholds Are Used |
|--------------|-------|------------------------|
| EARS | 3 | WITHIN clauses, boundary conditions |
| BDD | 4 | Performance scenarios, SLA validation |
| SYS | 6 | Quality Attributes, SLAs, resource limits |
| REQ | 7 | Performance targets, configurations |
| SPEC | 10 | Implementation configurations |

---

## 13. Validation

### 13.1 Pre-commit Validation

Run `detect_magic_numbers.py` to validate:
1. No hardcoded quantitative values in requirements documents
2. All `@threshold` references resolve to valid keys in this registry
3. All keys in registry have corresponding values (no {VALUE} placeholders in production)

### 13.2 Registry Completeness Check

- [ ] All performance thresholds defined
- [ ] All timeout values defined
- [ ] All rate limits defined
- [ ] All compliance thresholds defined
- [ ] Environment overrides documented
- [ ] Change log maintained

---

## Document Metadata

```yaml
---
title: "Platform Threshold Registry Template"
document_id: PRD-000
version: "1.0"
status: template
layer: 2
tags:
  - threshold-registry
  - governance
  - magic-number-prevention
  - sdd-workflow
cumulative_tags:
  brd: "BRD-NNN:REQUIREMENT-ID"
---
```
