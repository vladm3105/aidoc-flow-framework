---
title: "Threshold Naming and Usage Rules"
tags:
  - reference
  - standards
  - shared-architecture
  - required-both-approaches
custom_fields:
  document_type: REF
  artifact_type: REF
  layer: null
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
---

# Threshold Naming and Usage Rules

## 1. Overview

This document defines the naming conventions and usage rules for platform thresholds, limits, and timing parameters. All projects using this framework MUST follow these standards to ensure consistency, traceability, and maintainability across different projects and teams.

### 1.1 Scope

This framework provides:

- **Universal rules** for threshold key naming
- **Predefined categories** applicable to all projects
- **Guidelines** for creating domain-specific categories
- **Standards** for boundary specification, reference formats, and environment overrides

### 1.2 Threshold Definition Strategy

Thresholds are defined in **source documents** (BRD/PRD/ADR) and referenced via **`@threshold:` tags** in downstream artifacts:

**Source Documents** (define thresholds in YAML blocks):

- **BRD**: Business-level thresholds (compliance limits, risk scores, SLAs)
- **PRD**: Product-level thresholds (feature limits, user quotas, pricing tiers)
- **ADR**: Technical thresholds (circuit breakers, pool sizes, performance targets, timeouts)

**Consumer Documents** (reference thresholds using `@threshold:` tags):

- **EARS, BDD, SYS, REQ, CTR, SPEC**: Reference thresholds from BRD/PRD/ADR
- **ADR**: May also reference BRD/PRD thresholds when satisfying business/product requirements
- **Code/Config**: Reference source document thresholds for implementation

> **Note**: ADR has a dual role - it can define technical thresholds AND reference business/product thresholds from BRD/PRD.

This approach eliminates separate registry documents while maintaining full traceability.

### 1.3 Defining Thresholds in Source Documents

#### 1.3.1 YAML Block Format in Source Documents

Define thresholds in a dedicated section using YAML code blocks:

```markdown
## Thresholds

```yaml
# BRD-01, PRD-01, or ADR-01 Thresholds
thresholds:
  kyc:
    l1:
      daily: 1000          # USD, single transaction max
      monthly: 5000        # USD, cumulative
    l2:
      daily: 5000
      monthly: 25000
  risk:
    low:
      min: 0
      max: 39              # score, inclusive
    medium:
      min: 40
      max: 74
    high:
      min: 75
      max: 100
  perf:
    api:
      p95: 200             # ms
      p99: 500             # ms
  timeout:
    partner:
      default: 30          # seconds
      max: 60              # seconds
```
```

**Required Metadata per Threshold**:

| Element | Required | Description | Example |
|---------|----------|-------------|---------|
| Key | Yes | Follows naming convention | `kyc.l1.daily` |
| Value | Yes | Numeric value | `1000` |
| Unit (comment) | Yes | Unit specification | `# USD`, `# ms`, `# score` |
| Boundary (comment) | Conditional | For ranges | `# inclusive`, `# cumulative` |

#### 1.3.2 @threshold: Tag Format

Downstream documents reference thresholds using the `@threshold:` tag:

```text
@threshold: {DOC_TYPE}.{DOC_NUM}.{threshold_key}
```

**Components**:

| Component | Description | Example |
|-----------|-------------|---------|
| `DOC_TYPE` | Source document type | `BRD`, `PRD`, `ADR` |
| `DOC_NUM` | Document number (2+ digits, starts at 01) | `01`, `35`, `100` |
| `threshold_key` | Full threshold key | `kyc.l1.daily`, `circuit.failure.count` |

**Examples**:

```markdown
@threshold: PRD.01.kyc.l1.daily
@threshold: BRD.02.risk.low.max
@threshold: ADR.15.circuit.failure.count
@threshold: ADR.15.pool.db.max
@threshold: ADR.20.perf.api.p95
```

#### 1.3.3 Usage in Downstream Documents

**In EARS Requirements**:

```markdown
## Thresholds Referenced

@threshold: PRD.01.kyc.l1.daily
@threshold: PRD.01.kyc.l1.monthly

EARS-01: WHEN a L1 user initiates a transaction,
THE system SHALL validate the amount against @threshold: PRD.01.kyc.l1.daily
WITHIN 100ms.
```

**In BDD Scenarios**:

```gherkin
# @threshold: PRD.01.kyc.l1.daily
# @threshold: PRD.01.risk.high.min

Scenario: L1 user exceeds daily limit
  Given a L1 verified user
  And the daily limit is $1,000 per @threshold: PRD.01.kyc.l1.daily
  When the user attempts a $1,500 transaction
  Then the transaction is blocked
```

**In SPEC Documents**:

```yaml
# @threshold: PRD.01.perf.api.p95
# @threshold: PRD.01.timeout.partner.default

performance:
  response_time:
    p95_ms: 200  # per @threshold: PRD.01.perf.api.p95
  timeouts:
    partner_api: 30  # per @threshold: PRD.01.timeout.partner.default
```

**In ADR Documents** (defining AND referencing thresholds):

```markdown
# ADR-NN: Circuit Breaker Architecture (example)

## Thresholds Referenced

@threshold: PRD.01.perf.api.p95
@threshold: BRD.02.timeout.partner.max

## Thresholds Defined

```yaml
thresholds:
  circuit:
    failure:
      count: 5             # failures before open
      window: 60           # seconds
    reset:
      timeout: 30          # seconds before half-open
  pool:
    db:
      min: 5               # connections
      max: 20              # connections
      idle: 300            # seconds before reclaim
`` `

## Decision

To meet the p95 latency requirement of 200ms (per @threshold: PRD.01.perf.api.p95),
we implement circuit breakers with @threshold: ADR.15.circuit.failure.count = 5.
```

**In Code**:

```python
"""Transaction validation service.

@brd: BRD.01.01.30
@prd: PRD.01.07.05
@adr: ADR-NN
@threshold: PRD.01.kyc.l1.daily
@threshold: ADR.15.circuit.failure.count
@impl-status: complete
"""

# Values loaded from configuration
KYC_L1_DAILY = config.get("thresholds.kyc.l1.daily")  # 1000 USD
CIRCUIT_FAILURE_COUNT = config.get("thresholds.circuit.failure.count")  # 5
```

#### 1.3.4 Threshold Traceability Chain

```text
Source Documents (define thresholds):
├── BRD (business thresholds)     → defines: @threshold: BRD.01.risk.high.min
├── PRD (product thresholds)      → defines: @threshold: PRD.01.kyc.l1.daily
└── ADR (technical thresholds)    → defines: @threshold: ADR.15.circuit.failure.count
         ↓
Consumer Documents (reference via @threshold: tags):
├── EARS  → references: @threshold: PRD.01.kyc.l1.daily
├── BDD   → references: @threshold: PRD.01.kyc.l1.daily
├── SYS   → references: @threshold: ADR.15.pool.db.max
├── ADR   → references: @threshold: PRD.01.perf.api.p95 (to satisfy product SLA)
├── REQ   → references: @threshold: BRD.01.risk.high.min
├── CTR   → references: @threshold: PRD.01.rate.api.user
└── SPEC  → references: @threshold: ADR.15.circuit.failure.count
         ↓
Code (implements with config reference)
```

> **ADR Dual Role**: An ADR can define its own technical thresholds (e.g., `ADR.15.circuit.failure.count`) while also referencing business/product thresholds from BRD/PRD (e.g., `@threshold: PRD.01.perf.api.p95`) that the architecture must satisfy.

---

## 2. Naming Convention Structure

### 2.1 Key Format

```text
{category}.{subcategory}.{attribute}[.{qualifier}]
```

| Component | Required | Description | Example |
|-----------|----------|-------------|---------|
| `category` | Yes | Top-level domain | `kyc`, `risk`, `perf` |
| `subcategory` | Yes | Feature/scope within category | `l1`, `api`, `partner` |
| `attribute` | Yes | Specific metric/limit | `daily`, `p95`, `timeout` |
| `qualifier` | No | Additional specificity | `max`, `min`, `warning` |

### 2.2 Category Creation Rules

#### 2.2.1 Category Naming Rules

| Rule ID | Rule | Correct | Incorrect |
|---------|------|---------|-----------|
| CR-01 | Use 3-12 lowercase characters | `perf`, `auth`, `cache` | `p`, `performancemetrics` |
| CR-02 | Use domain nouns, not verbs | `rate`, `timeout` | `limiting`, `waiting` |
| CR-03 | Avoid generic terms | `auth`, `payment` | `data`, `config`, `setting` |
| CR-04 | One category per domain | `cache` for all caching | `memcache`, `rediscache` |
| CR-05 | No overlapping scope | Separate `rate` and `quota` | Both limiting same resource |

#### 2.2.2 Universal Categories (Predefined)

These categories apply to ALL projects and SHOULD be used when applicable:

| Category | Purpose | Scope | Example Keys |
|----------|---------|-------|--------------|
| `perf` | Performance timing targets | Response times, latencies | `perf.api.p95`, `perf.db.query.p50` |
| `timeout` | Timeout configurations | Operation timeouts | `timeout.http.default`, `timeout.job.max` |
| `rate` | Rate limiting | Request/operation limits | `rate.api.user`, `rate.job.concurrent` |
| `retry` | Retry policy parameters | Retry counts, delays | `retry.http.max`, `retry.db.delay` |
| `circuit` | Circuit breaker configuration | Failure thresholds | `circuit.failure.count`, `circuit.reset` |
| `alert` | Alert/monitoring thresholds | Warning/critical levels | `alert.cpu.warning`, `alert.memory.critical` |
| `cache` | Cache configuration | TTL, size limits | `cache.ttl.default`, `cache.size.max` |
| `pool` | Connection/resource pools | Pool sizes, timeouts | `pool.db.max`, `pool.http.idle` |
| `queue` | Queue configuration | Sizes, delays | `queue.size.max`, `queue.retry.delay` |
| `batch` | Batch processing | Sizes, intervals | `batch.size.max`, `batch.interval` |

#### 2.2.3 Domain-Specific Categories (Project-Defined)

Projects define domain-specific categories in the BRD/PRD Thresholds section. Document new categories with a comment:

```yaml
thresholds:
  # Domain: Financial - Category: kyc
  # Purpose: KYC verification tier limits
  # Owner: Compliance Team
  kyc:
    l1:
      daily: 1000
```

**Examples by Domain**:

| Domain | Suggested Categories | Example Keys |
|--------|---------------------|--------------|
| Authentication | `auth`, `session`, `token` | `auth.attempts.max`, `session.idle.timeout` |
| Financial | `amount`, `fee`, `limit` | `amount.tx.max`, `fee.tier1.flat` |
| ML/AI | `ml`, `model`, `inference` | `ml.confidence.min`, `model.drift.threshold` |
| Compliance | `compliance`, `audit` | `compliance.report.retention` |
| Risk | `risk`, `score`, `velocity` | `risk.high.min`, `velocity.tx.hourly` |
| Storage | `storage`, `file`, `upload` | `storage.file.maxsize`, `upload.chunk.size` |
| Messaging | `msg`, `notification` | `msg.retry.max`, `notification.batch.size` |

#### 2.2.4 Category Registration Process

1. **Check Universal Categories** - Use predefined if applicable
2. **Check Existing Project Categories** - Review BRD/PRD threshold sections for duplicates
3. **Define New Category** - Add to appropriate BRD/PRD with YAML comment metadata:
   - Name (3-12 chars, lowercase)
   - Purpose (one sentence)
   - Domain scope
   - Owner (team responsible)
4. **Review** - Ensure no overlap with existing categories
5. **Document** - Add threshold keys under the new category in YAML block

---

## 3. Naming Rules

### 3.1 General Rules

| Rule ID | Rule | Correct | Incorrect |
|---------|------|---------|-----------|
| NR-01 | Use lowercase letters only | `kyc.l1.daily` | `KYC.L1.Daily` |
| NR-02 | Use dots as separators | `risk.low.max` | `risk_low_max`, `risk-low-max` |
| NR-03 | Use singular nouns | `alert.cpu` | `alerts.cpus` |
| NR-04 | Avoid abbreviations except standard ones | `perf.api` | `prf.a` |
| NR-05 | Maximum 5 segments | `perf.api.standard.p95` | `perf.api.standard.endpoint.response.p95` |
| NR-06 | No numeric prefixes in segments | `tier1`, `l1` | `1tier`, `1l` |

### 3.2 Standard Abbreviations

#### 3.2.1 Universal Abbreviations (Use Across All Projects)

| Abbreviation | Meaning | Usage Context |
|--------------|---------|---------------|
| `p50`, `p95`, `p99`, `p999` | Percentiles | Performance metrics |
| `l1`, `l2`, `l3` | Level/Tier 1, 2, 3 | Tiered limits, verification levels |
| `api` | API endpoint | Performance, rate limits |
| `db` | Database | Database operations |
| `http` | HTTP operations | Timeouts, retries |
| `tx` | Transaction | Transaction processing |
| `msg` | Message | Messaging systems |
| `req` | Request | Rate limiting |
| `res` | Response | Performance metrics |
| `max` | Maximum | Upper bounds |
| `min` | Minimum | Lower bounds |
| `ttl` | Time to live | Cache, token expiration |
| `ms` | Milliseconds | Time units |
| `sec` | Seconds | Time units |

#### 3.2.2 Domain-Specific Abbreviations (Define Per Project)

Projects MAY define additional abbreviations in BRD/PRD threshold sections using YAML comments:

```yaml
thresholds:
  # Project Abbreviations:
  # - aml: Anti-Money Laundering (Compliance domain)
  # - ctr: Currency Transaction Report (Compliance domain)
  aml:
    threshold:
      daily: 10000
```

**Abbreviation Rules**:

- Maximum 5 characters
- Lowercase only
- Must be documented in BRD/PRD threshold section comments
- Avoid conflicts with universal abbreviations

**Common Domain Abbreviations** (examples):

| Domain | Common Abbreviations |
|--------|---------------------|
| Authentication | `auth`, `otp`, `mfa`, `jwt` |
| Financial | `fx`, `amt`, `fee` |
| ML/AI | `ml`, `inf`, `conf` |
| Compliance | `aml`, `ctr`, `sar` |

### 3.3 Time Period Qualifiers

| Qualifier | Duration | Reset Boundary |
|-----------|----------|----------------|
| `hourly` | 1 hour | Top of each hour (UTC) |
| `daily` | 24 hours | 00:00:00 UTC |
| `weekly` | 7 days | 00:00:00 UTC Monday |
| `monthly` | Calendar month | 00:00:00 UTC 1st of month |
| `yearly` | Calendar year | 00:00:00 UTC January 1st |

### 3.4 Range Qualifiers

| Qualifier | Purpose | Boundary Type |
|-----------|---------|---------------|
| `min` | Lower bound | Inclusive |
| `max` | Upper bound | Inclusive by default |
| `low` | Low severity/tier | Context-dependent |
| `medium` | Medium severity/tier | Context-dependent |
| `high` | High severity/tier | Context-dependent |
| `critical` | Critical severity | Context-dependent |
| `warning` | Warning level | Alert threshold |

---

## 4. Type Specifications

### 4.1 Data Types

| Type | Description | Example Values |
|------|-------------|----------------|
| `integer` | Whole numbers | `1000`, `300`, `5` |
| `decimal` | Floating-point numbers | `0.85`, `1.5`, `0.015` |
| `ratio` | Value between 0 and 1 | `0.25`, `0.95` |
| `percent` | Value between 0 and 100 | `75`, `95.5` |
| `score` | Scaled score (0-100 typical) | `39`, `75` |

### 4.2 Unit Standards

| Unit Category | Standard Units | Conversion Reference |
|---------------|----------------|---------------------|
| Time (short) | `ms` (milliseconds) | 1000ms = 1s |
| Time (medium) | `seconds` | 60s = 1min |
| Time (long) | `hours` | 3600s = 1h |
| Currency | `USD` | Base currency |
| Count | `count` | Dimensionless |
| Rate | `req/sec`, `req/min`, `tx/hour` | Composite |
| Percentage | `percent` | 0-100 scale |
| Ratio | `ratio` | 0-1 scale |
| Score | `score` | 0-100 scale (typical) |

---

## 5. Boundary Specification Rules

### 5.1 Default Boundary Convention

**Default**: All ranges use `[inclusive, exclusive)` unless explicitly noted in threshold documentation.

| Boundary Type | Symbol | Meaning | When to Use |
|---------------|--------|---------|-------------|
| Inclusive-Inclusive | `[a, b]` | Both endpoints included | Score ranges, risk levels |
| Inclusive-Exclusive | `[a, b)` | Start included, end excluded | **Default convention** |
| Exclusive-Inclusive | `(a, b]` | Start excluded, end included | Must be explicitly stated |
| Exclusive-Exclusive | `(a, b)` | Neither endpoint included | Must be explicitly stated |

### 5.2 Boundary Clarification Requirements

Every threshold with range semantics MUST include explicit boundary clarification:

**Required Documentation Format**:

```markdown
**Boundary Specification**:
- {period} limit: Resets at {reset_time} {timezone}
- Inclusive boundary: {action} at exactly {boundary_value} is {ALLOWED|BLOCKED}
- Exceeds boundary: {action} causing cumulative total > limit is {BLOCKED|FLAGGED}

```

**Example - Velocity Limits**:

```markdown
**Boundary Specification**:
- Daily limit: Resets at 00:00:00 UTC
- Monthly limit: Resets at 00:00:00 UTC on 1st of month
- Inclusive boundary: Transaction at exactly $1,000 is ALLOWED for L1
- Exceeds boundary: Transaction causing cumulative total > limit is BLOCKED

```

### 5.3 Risk Score Boundary Rules

| Score | Category | Boundary Type | Action |
|-------|----------|---------------|--------|
| 0 | Low | Minimum (inclusive) | Auto-approve |
| 39 | Low | Maximum (inclusive) | Auto-approve |
| 40 | Medium | Minimum (inclusive) | Manual review |
| 74 | Medium | Maximum (inclusive) | Manual review |
| 75 | High | Minimum (inclusive) | Escalate |
| 100 | High | Maximum (inclusive) | Block + escalate |

**Boundary Clarification Example**:

```text
risk.low: [0, 39] → Score 39 = LOW (auto-approve)
risk.medium: [40, 74] → Score 40 = MEDIUM (manual review)
risk.high: [75, 100] → Score 75 = HIGH (escalate)
```

### 5.4 Cumulative vs. Single Transaction Boundaries

| Boundary Type | Key Suffix | Behavior |
|---------------|------------|----------|
| Single transaction | `.daily`, `.max` | Maximum per individual transaction |
| Cumulative period | `.monthly`, `.yearly` | Sum of all transactions in period |
| Rolling window | `.velocity`, `.window` | Sum within sliding time window |

**Example**:

```yaml
kyc.l1.daily: 1000      # Single transaction max: $1,000
kyc.l1.monthly: 5000    # Cumulative monthly: $5,000 total
rate.tx.user.velocity: 5  # Rolling: 5 transactions per 5-minute window
```

### 5.5 Reset Boundary Rules

| Period | Reset Time | Timezone | Notes |
|--------|------------|----------|-------|
| Hourly | HH:00:00 | UTC | Top of each hour |
| Daily | 00:00:00 | UTC | Midnight UTC |
| Weekly | 00:00:00 Monday | UTC | Start of week |
| Monthly | 00:00:00 1st | UTC | First day of month |
| Quarterly | 00:00:00 Q1/Q2/Q3/Q4 start | UTC | Jan 1, Apr 1, Jul 1, Oct 1 |
| Yearly | 00:00:00 Jan 1 | UTC | Start of calendar year |

---

## 6. @threshold: Tag Reference Rules

### 6.1 Tag Format

**Standard @threshold: Tag**:

```text
@threshold: {DOC_TYPE}.{DOC_NUM}.{threshold_key}
```

**Components**:

| Component | Format | Example |
|-----------|--------|---------|
| `DOC_TYPE` | BRD, PRD, or ADR | `PRD`, `ADR` |
| `DOC_NUM` | 2+ digit number (starts at 01) | `01`, `15`, `100` |
| `threshold_key` | Dot-separated key | `kyc.l1.daily`, `circuit.failure.count` |

### 6.2 Reference Formats by Context

| Context | Format | Example |
|---------|--------|---------|
| @threshold: tag | `@threshold: {TYPE}.{NUM}.{key}` | `@threshold: PRD.01.kyc.l1.daily` |
| Inline citation | `per @threshold: {TYPE}.{NUM}.{key}` | `1,000 USD per @threshold: PRD.01.kyc.l1.daily` |
| Code constant | `THRESHOLD_{CATEGORY}_{KEY}` | `THRESHOLD_KYC_L1_DAILY` |
| Config path | `thresholds.{key}` | `thresholds.kyc.l1.daily` |
| Environment var | `THRESHOLD_{CATEGORY}_{KEY}` | `THRESHOLD_KYC_L1_DAILY=1000` |

### 6.3 Consumer Document Requirements

All downstream documents referencing thresholds MUST:

1. **Declare threshold dependencies** in a dedicated section:

   ```markdown
   ## Thresholds Referenced

   @threshold: PRD.01.kyc.l1.daily
   @threshold: PRD.01.kyc.l1.monthly
   @threshold: BRD.02.risk.high.min
   ```

2. **Reference values inline** with tag:

   ```markdown
   L1 users limited to 1,000 USD daily (per @threshold: PRD.01.kyc.l1.daily)
   ```

3. **Never hardcode values** - always use @threshold: tags

### 6.4 Source Resolution

When multiple documents could define similar thresholds, establish clear ownership:

| Threshold Domain | Source Document | Rationale |
|------------------|-----------------|-----------|
| Compliance limits (KYC/AML) | BRD | Regulatory/business authority |
| Product feature limits | PRD | Product-level decisions |
| Risk scores | BRD | Platform-level risk framework |
| Circuit breakers, pools | ADR | Technical architecture decisions |
| Performance SLAs (p95/p99) | ADR | Technical performance targets |
| API rate limits | PRD or ADR | Product (user quotas) or Technical (system protection) |

**Conflict Resolution Rules**:

1. **Business vs Technical**: BRD/PRD own business thresholds; ADR owns technical thresholds
2. **Platform vs Product**: BRD takes precedence over PRD for platform-level thresholds
3. **When unclear**: The document where the threshold is first justified owns it

---

## 7. Definition Rules

### 7.1 Percentile Definitions

| Qualifier | Percentile | Statistical Definition | Operational Purpose |
|-----------|------------|------------------------|---------------------|
| `p50` | 50th | Median - 50% of requests faster | Typical/expected performance |
| `p90` | 90th | 90% of requests faster | Near-worst case baseline |
| `p95` | 95th | 95% of requests faster | **Performance target (SLO)** |
| `p99` | 99th | 99% of requests faster | **Alert threshold** |
| `p999` | 99.9th | 99.9% of requests faster | SLA boundary / critical |

**Usage Rules**:

- `p50`: Use for capacity planning and baseline monitoring
- `p95`: Use for SLO definitions and performance targets
- `p99`: Use for alerting thresholds
- `p999`: Use for SLA commitments (rarely needed)

### 7.2 Risk Level Definitions

| Level | Score Range | Definition | Required Action |
|-------|-------------|------------|-----------------|
| Low | 0-39 | Minimal risk indicators | Auto-approve |
| Medium | 40-74 | Some risk indicators present | Manual review required |
| High | 75-100 | Significant risk indicators | Block + escalate to compliance |

### 7.3 Verification Tier Definitions

| Tier | KYC (B2C) | KYB (B2B) | Requirements |
|------|-----------|-----------|--------------|
| L1 (Basic) | Name, DOB, Address | Business name, Registration | Self-declaration |
| L2 (Verified) | + ID verification | + Director verification | Document verification |
| L3 (Enhanced) | + Source of funds | + UBO verification (>25%) | Enhanced due diligence |

**Scaling Convention**: B2B limits are typically 10x B2C limits at each tier.

### 7.4 Alert Severity Definitions

| Severity | Definition | Response Time | Escalation |
|----------|------------|---------------|------------|
| `info` | Informational, no action | None | None |
| `warning` | Approaching threshold | 1 hour | On-call engineer |
| `critical` | Threshold exceeded | 15 minutes | Incident manager |
| `emergency` | System-wide impact | Immediate | Executive escalation |

### 7.5 Timeout Category Definitions

| Category | Typical Range | Use Case |
|----------|---------------|----------|
| `partner.*` | 15-60 seconds | External API calls |
| `session.*` | 300-86400 seconds | User session management |
| `job.*` | 1800-7200 seconds | Background batch processing |
| `validity.*` | 60-300 seconds | Token/quote expiration |

### 7.6 Rate Limit Window Definitions

| Window Type | Duration | Reset Behavior |
|-------------|----------|----------------|
| `burst` | 1 second | Rolling window |
| `standard` | 60 seconds (1 min) | Rolling window |
| `hourly` | 3600 seconds | Fixed hourly reset |
| `daily` | 86400 seconds | Fixed daily reset (UTC) |

---

## 8. Environment Override Rules

### 8.1 Override Permission Matrix

| Environment | Override Allowed | Scope | Approval Required |
|-------------|------------------|-------|-------------------|
| Development | **Yes** | All thresholds | None |
| Testing | **Yes** | All thresholds | None |
| Staging | **Limited** | Non-compliance only | Engineering lead |
| Production | **Controlled** | Emergency only | Multi-party approval |

### 8.2 Override Categories

| Category | Dev Override | Staging Override | Prod Override |
|----------|--------------|------------------|---------------|
| `kyc.*`, `kyb.*` | Yes | Yes (match prod for testing) | Requires Compliance |
| `risk.*` | Yes | Yes | Requires Risk + Compliance |
| `compliance.*` | Yes | **No** | Requires Legal + Compliance |
| `perf.*` | Yes | Yes | Requires Engineering |
| `timeout.*` | Yes | Yes | Requires Engineering |
| `rate.*` | Yes | Yes | Requires Product |
| `alert.*` | Yes | Yes | Requires SRE |

### 8.3 Override Documentation Requirements

All environment overrides MUST be documented:

```yaml
# config/thresholds.{env}.yaml
overrides:
  kyc.l1.daily:
    value: 500            # Override value
    reason: "Testing low-limit flows"
    ticket: "JIRA-1234"
    expires: "2025-12-31"
    approver: "jane.doe@company.com"
```

### 8.4 Production Override Workflow

1. **Request**: Create change request with justification
2. **Risk Assessment**: Document impact analysis
3. **Approval**: Obtain required approvals per category
4. **Implementation**: Apply via configuration management
5. **Monitoring**: Enable enhanced monitoring for 24 hours
6. **Rollback Plan**: Document rollback procedure

### 8.5 Override Constraints

| Constraint | Rule |
|------------|------|
| **No compliance relaxation in prod** | `compliance.*` thresholds cannot be increased in production |
| **Staging matches production** | Staging should mirror production for integration testing |
| **Expiration required** | All overrides MUST have expiration date |
| **Audit trail mandatory** | All overrides logged with approver, timestamp, reason |

### 8.6 Environment-Specific Scaling

| Threshold Type | Dev Scale | Staging Scale | Prod Scale |
|----------------|-----------|---------------|------------|
| Rate limits | 10x higher | 1x (match prod) | Baseline |
| Timeouts | 2x longer | 1x (match prod) | Baseline |
| Alert thresholds | Disabled | 1x (match prod) | Baseline |
| Velocity limits | Unrestricted | 1x (match prod) | Baseline |

---

## 9. Weight Factor Rules

### 9.1 Sum Constraint Rules

| Rule | Requirement |
|------|-------------|
| Sum constraint | All weights in a category MUST sum to 1.0 |
| Precision | Use maximum 2 decimal places (0.25, not 0.2534) |
| Documentation | Document percentage contribution alongside ratio |

**Example**:

```yaml
risk.weight:
  velocity: 0.25   # 25% contribution
  amount: 0.20     # 20% contribution
  geography: 0.20  # 20% contribution
  recipient: 0.15  # 15% contribution
  behavior: 0.10   # 10% contribution
  device: 0.10     # 10% contribution
  # Total: 1.00
```

---

## 10. Configuration Structure

### 10.1 YAML Format

```yaml
thresholds:
  {category}:
    {subcategory}:
      {attribute}: {value}
```

**Example**:

```yaml
thresholds:
  kyc:
    l1:
      daily: 1000
      monthly: 5000
    l2:
      daily: 5000
      monthly: 25000
  risk:
    low:
      min: 0
      max: 39
    medium:
      min: 40
      max: 74
    high:
      min: 75
      max: 100
```

---

## 11. Validation Rules

### 11.1 Required Validations

| Validation | Rule |
|------------|------|
| Type safety | Value MUST match declared type |
| Range validation | Value MUST be within min/max bounds |
| Unit consistency | All values in a category MUST use same unit |
| Reference integrity | Cross-references MUST point to valid keys |
| Sum constraints | Weight factors MUST sum to 1.0 |

### 11.2 Logical Consistency

| Constraint | Example |
|------------|---------|
| Range ordering | `risk.low.max` < `risk.medium.min` |
| Tier progression | `kyc.l1.daily` < `kyc.l2.daily` < `kyc.l3.daily` |
| Alert ordering | `alert.*.warning` < `alert.*.critical` |
| Percentile ordering | `perf.*.p50` < `perf.*.p95` < `perf.*.p99` |

---

## 12. Governance

### 12.1 Change Management

| Aspect | Requirement |
|--------|-------------|
| Update latency | Configuration changes propagate within 60 seconds |
| Rollback capability | Previous configuration restorable within 30 seconds |
| Audit trail | All changes logged with user, timestamp, before/after values |
| Versioning | Semantic versioning (MAJOR.MINOR.PATCH) |

### 12.2 Approval Matrix

| Change Type | Approvers |
|-------------|-----------|
| New threshold | Product + Engineering |
| Value adjustment | Product + Risk |
| Compliance threshold | Product + Risk + Compliance |
| Category addition | Product + Engineering + Architecture |

---

## 13. Anti-Patterns

### 13.1 Naming Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| `maxDailyLimit` | CamelCase, redundant | `kyc.l1.daily` |
| `threshold_1` | Meaningless identifier | `risk.low.max` |
| `KYC_DAILY_L1` | Wrong case, wrong separator | `kyc.l1.daily` |
| `perf.api.response.time.milliseconds.p95` | Too verbose | `perf.api.standard.p95` |
| `limit` | No context | `rate.api.user.standard` |

### 13.2 Usage Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Hardcoded values | No single source of truth | Use `@threshold:` tag |
| Inline magic numbers | Unmaintainable | Use `@threshold:` tag with key |
| Duplicate definitions | Conflicts | Single BRD/PRD definition |
| Missing units | Ambiguous | Comment with unit in YAML |
| No @threshold: tags | Broken traceability | Always reference source doc |

---

## 14. Quick Reference

### 14.1 Key Construction Template

```text
{category}.{scope}.{metric}[.{qualifier}]
     │        │       │         │
     │        │       │         └── Optional: min/max/p50/p95/warning/critical
     │        │       └── Required: daily/monthly/timeout/threshold/rate
     │        └── Required: l1/l2/l3/api/partner/user/session
     └── Required: kyc/kyb/risk/perf/timeout/rate/amount/compliance/alert
```

### 14.2 Common Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| `{domain}.l{n}.{period}` | Tiered velocity limits | `kyc.l1.daily` |
| `{domain}.{scope}.p{nn}` | Percentile metrics | `perf.api.standard.p95` |
| `{domain}.{target}.{action}` | External service config | `timeout.partner.bridge` |
| `{domain}.{level}.{boundary}` | Risk/alert ranges | `risk.medium.max` |
| `{domain}.{type}.{tier}` | Fee structures | `fee.flat.tier1` |

### 14.3 Checklist for New Thresholds

- [ ] Key follows `category.subcategory.attribute` format
- [ ] Uses lowercase with dot separators
- [ ] Defined in appropriate BRD/PRD with YAML block
- [ ] Type specified (integer/decimal/ratio/percent/score)
- [ ] Unit specified in YAML comment
- [ ] Boundary behavior documented in comment
- [ ] `@threshold:` tags added to downstream documents
- [ ] Logical consistency validated
- [ ] Approval obtained per governance matrix

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-16 | AI Dev Flow Team | Initial creation based on PRD-NN analysis |
| 1.1 | 2025-12-16 | AI Dev Flow Team | Added detailed Boundary Specification, Reference Format, Definition, and Environment Override rules |
| 1.2 | 2025-12-16 | AI Dev Flow Team | Converted to framework: replaced fixed categories with category creation rules; added universal vs domain-specific categories and abbreviations |
| 1.3 | 2025-12-16 | AI Dev Flow Team | Removed Threshold Registry requirement; thresholds now defined in BRD/PRD/ADR YAML blocks; introduced `@threshold:` tags for traceability; ADR added as source for technical thresholds (circuit breakers, pools, performance SLAs) |

---

## End of Document
