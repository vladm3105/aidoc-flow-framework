---
title: "Threshold Naming and Usage Rules"
tags:
  - reference
  - standards
  - shared-architecture
custom_fields:
  document_type: REF
  artifact_type: REF
  layer: null
  priority: shared
  development_status: active
---

# Threshold Naming and Usage Rules

## 1. Overview

This document defines the naming conventions and usage rules for thresholds,
limits, and timing parameters. Projects using this framework follow these
standards so that quantitative values stay consistent, traceable, and
maintainable across documents and teams.

> **Scope.** This is an engine-agnostic *naming and traceability* standard. It
> defines how thresholds are keyed, referenced, and bounded — not how a runtime
> stores, overrides, or deploys them. Runtime configuration, environment
> overrides, and operational rollout policy belong to a consuming project's own
> config, not to this spec.

### 1.1 What this standard provides

- **Universal rules** for threshold key naming.
- **Predefined categories** applicable to all projects.
- **Guidelines** for creating domain-specific categories.
- **Standards** for boundary specification and `@threshold:` reference format.

### 1.2 Threshold Definition Strategy

Thresholds are defined in **source documents** (BRD / PRD / ADR) and referenced
via **`@threshold:` tags** in downstream artifacts:

**Source documents** (define thresholds in YAML blocks):

- **BRD**: Business-level thresholds (compliance limits, risk scores, SLAs).
- **PRD**: Product-level thresholds (feature limits, user quotas, tiers).
- **ADR**: Technical thresholds (circuit breakers, pool sizes, performance
  targets, timeouts).

**Consumer documents** (reference thresholds using `@threshold:` tags):

- **EARS, BDD, SPEC, TDD, IPLAN**: reference thresholds from BRD / PRD / ADR.
- **ADR**: may also reference BRD / PRD thresholds when satisfying a
  business/product requirement.
- **Code/Config**: reference source-document thresholds for implementation.

> **Note**: ADR has a dual role — it can define technical thresholds AND
> reference business/product thresholds from BRD/PRD.

This approach eliminates separate registry documents while maintaining full
traceability.

### 1.3 Defining Thresholds in Source Documents

#### 1.3.1 YAML Block Format in Source Documents

Define thresholds in a dedicated section using YAML code blocks. The examples
below use a neutral `quota` domain; replace it with your project's categories.

```markdown
## Thresholds

```yaml
# BRD-01, PRD-01, or ADR-01 Thresholds
thresholds:
  quota:
    l1:
      daily: 1000          # units, single-operation max
      monthly: 5000        # units, cumulative
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

**Required metadata per threshold**:

| Element | Required | Description | Example |
|---------|----------|-------------|---------|
| Key | Yes | Follows naming convention | `quota.l1.daily` |
| Value | Yes | Numeric value | `1000` |
| Unit (comment) | Yes | Unit specification | `# units`, `# ms`, `# score` |
| Boundary (comment) | Conditional | For ranges | `# inclusive`, `# cumulative` |

#### 1.3.2 @threshold: Tag Format

Downstream documents reference thresholds using the `@threshold:` tag:

```text
@threshold: {DOC_TYPE}.{DOC_NUM}.{threshold_key}
```

| Component | Description | Example |
|-----------|-------------|---------|
| `DOC_TYPE` | Source document type | `BRD`, `PRD`, `ADR` |
| `DOC_NUM` | Document number (2+ digits, starts at 01) | `01`, `35`, `100` |
| `threshold_key` | Full threshold key | `quota.l1.daily`, `circuit.failure.count` |

**Examples**:

```markdown
@threshold: PRD.01.quota.l1.daily
@threshold: BRD.02.risk.low.max
@threshold: ADR.15.circuit.failure.count
@threshold: ADR.15.pool.db.max
@threshold: ADR.20.perf.api.p95
```

#### 1.3.3 Usage in Downstream Documents

Downstream documents cite a defined threshold with an `@threshold:` tag rather
than hardcoding its value. A representative example (EARS):

```markdown
## Thresholds Referenced

@threshold: PRD.01.quota.l1.daily

EARS-01: WHEN an L1 user initiates an operation,
THE system SHALL validate the amount against @threshold: PRD.01.quota.l1.daily
WITHIN 100ms.
```

The same pattern applies in BDD (comment tags above the scenario), SPEC/TDD
(inline `# per @threshold: …` beside the value), ADR (which both defines and
references), and code (a module docstring tag + a `config.get("thresholds.…")`
lookup). See §6 for the full per-context format table.

#### 1.3.4 Threshold Traceability Chain

```text
Source Documents (define thresholds):
 BRD (business thresholds)     → defines: @threshold: BRD.01.risk.high.min
 PRD (product thresholds)      → defines: @threshold: PRD.01.quota.l1.daily
 ADR (technical thresholds)    → defines: @threshold: ADR.15.circuit.failure.count
         ↓
Consumer Documents (reference via @threshold: tags):
 EARS  → references: @threshold: PRD.01.quota.l1.daily
 BDD   → references: @threshold: PRD.01.quota.l1.daily
 ADR   → references: @threshold: PRD.01.perf.api.p95 (to satisfy product SLA)
 SPEC  → references: @threshold: ADR.15.circuit.failure.count
 TDD   → references: @threshold: ADR.15.pool.db.max
 IPLAN → references: @threshold: ADR.15.circuit.failure.count
         ↓
Code (implements with config reference)
```

> **ADR dual role**: an ADR can define its own technical thresholds (e.g.
> `ADR.15.circuit.failure.count`) while also referencing business/product
> thresholds from BRD/PRD (e.g. `@threshold: PRD.01.perf.api.p95`) that the
> architecture must satisfy.

---

## 2. Naming Convention Structure

### 2.1 Key Format

```text
{category}[.{subcategory}].{attribute}[.{qualifier}]
```

| Component | Required | Description | Example |
|-----------|----------|-------------|---------|
| `category` | Yes | Top-level domain | `quota`, `risk`, `perf` |
| `subcategory` | No | Feature/scope within category (omit when the category alone scopes the metric) | `l1`, `api`, `partner` |
| `attribute` | Yes | Specific metric/limit | `daily`, `p95`, `timeout`, `p95_latency` |
| `qualifier` | No | Additional specificity | `max`, `min`, `warning` |

The **key** (the part after `{TYPE}.{NN}.`) is therefore a **minimum of two
dot-separated segments** (`{category}.{attribute}`), making the entire threshold
tag a minimum of 4 dotted segments (`{TYPE}.{NN}.{category}.{attribute}`),
matching the authoritative `id_patterns.threshold` regex in
`registry/LAYER_REGISTRY.yaml` (the registry wins on any width discrepancy). A single
underscore *within* a segment name (e.g. `p95_latency`) is a legal attribute token;
NR-02 governs the *separators* between segments (dots), not characters inside a segment.

### 2.2 Category Creation Rules

#### 2.2.1 Category Naming Rules

| Rule ID | Rule | Correct | Incorrect |
|---------|------|---------|-----------|
| CR-01 | Use 3-12 lowercase characters | `perf`, `auth`, `cache` | `p`, `performancemetrics` |
| CR-02 | Use domain nouns, not verbs | `rate`, `timeout` | `limiting`, `waiting` |
| CR-03 | Avoid generic terms | `auth`, `quota` | `data`, `config`, `setting` |
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
| `quota` | Tiered usage/velocity limits | Per-tier ceilings | `quota.l1.daily`, `quota.l2.monthly` |

#### 2.2.3 Domain-Specific Categories (Project-Defined)

Projects define domain-specific categories in the BRD/PRD Thresholds section.
Document each new category with a YAML comment:

```yaml
thresholds:
  # Domain: <project domain> - Category: quota
  # Purpose: tiered usage limits
  # Owner: <owning team>
  quota:
    l1:
      daily: 1000
```

**Examples by domain** (illustrative — projects choose their own):

| Domain | Suggested Categories | Example Keys |
|--------|---------------------|--------------|
| Authentication | `auth`, `session`, `token` | `auth.attempts.max`, `session.idle.timeout` |
| ML/AI | `ml`, `model`, `inference` | `ml.confidence.min`, `model.drift.threshold` |
| Risk | `risk`, `score`, `velocity` | `risk.high.min`, `velocity.tx.hourly` |
| Storage | `storage`, `file`, `upload` | `storage.file.maxsize`, `upload.chunk.size` |
| Messaging | `msg`, `notification` | `msg.retry.max`, `notification.batch.size` |

#### 2.2.4 Category Registration Process

1. **Check universal categories** — use a predefined one if applicable.
2. **Check existing project categories** — review BRD/PRD threshold sections for
   duplicates.
3. **Define the new category** — add to the appropriate BRD/PRD with YAML
   comment metadata: name (3-12 chars, lowercase), purpose (one sentence),
   domain scope, owner (team responsible).
4. **Review** — ensure no overlap with an existing category.
5. **Document** — add threshold keys under the new category in the YAML block.

---

## 3. Naming Rules

### 3.1 General Rules

| Rule ID | Rule | Correct | Incorrect |
|---------|------|---------|-----------|
| NR-01 | Use lowercase letters only | `quota.l1.daily` | `QUOTA.L1.DAILY` |
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
| `l1`, `l2`, `l3` | Level/Tier 1, 2, 3 | Tiered limits |
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

Projects MAY define additional abbreviations in BRD/PRD threshold sections using
YAML comments. Each abbreviation: maximum 5 characters, lowercase only,
documented in the BRD/PRD threshold-section comments, and not in conflict with a
universal abbreviation.

```yaml
thresholds:
  # Project abbreviations:
  # - inf: inference (ML/AI domain)
  ml:
    inf:
      confidence:
        min: 0.85
```

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
| Currency | project base currency | Declared per project |
| Count | `count` | Dimensionless |
| Rate | `req/sec`, `req/min`, `tx/hour` | Composite |
| Percentage | `percent` | 0-100 scale |
| Ratio | `ratio` | 0-1 scale |
| Score | `score` | 0-100 scale (typical) |

---

## 5. Boundary Specification Rules

### 5.1 Default Boundary Convention

**Default**: all ranges use `[inclusive, exclusive)` unless explicitly noted in
threshold documentation.

| Boundary Type | Symbol | Meaning | When to Use |
|---------------|--------|---------|-------------|
| Inclusive-Inclusive | `[a, b]` | Both endpoints included | Score ranges, tier levels |
| Inclusive-Exclusive | `[a, b)` | Start included, end excluded | **Default convention** |
| Exclusive-Inclusive | `(a, b]` | Start excluded, end included | Must be explicitly stated |
| Exclusive-Exclusive | `(a, b)` | Neither endpoint included | Must be explicitly stated |

### 5.2 Boundary Clarification Requirements

Every threshold with range semantics MUST include explicit boundary clarification:

```markdown
**Boundary Specification**:
- {period} limit: Resets at {reset_time} {timezone}
- Inclusive boundary: {action} at exactly {boundary_value} is {ALLOWED|BLOCKED}
- Exceeds boundary: {action} causing cumulative total > limit is {BLOCKED|FLAGGED}
```

**Example — velocity limits**:

```markdown
**Boundary Specification**:
- Daily limit: Resets at 00:00:00 UTC
- Monthly limit: Resets at 00:00:00 UTC on 1st of month
- Inclusive boundary: An operation at exactly the L1 daily limit is ALLOWED
- Exceeds boundary: An operation causing cumulative total > limit is BLOCKED
```

### 5.3 Score Boundary Rules

Tiered score ranges use inclusive-inclusive boundaries. Example (a 3-tier risk
score):

| Score | Tier | Boundary Type | Action (project-defined) |
|-------|------|---------------|--------------------------|
| 0 | Low | Minimum (inclusive) | Auto-approve |
| 39 | Low | Maximum (inclusive) | Auto-approve |
| 40 | Medium | Minimum (inclusive) | Manual review |
| 74 | Medium | Maximum (inclusive) | Manual review |
| 75 | High | Minimum (inclusive) | Escalate |
| 100 | High | Maximum (inclusive) | Block + escalate |

```text
risk.low: [0, 39] → Score 39 = LOW
risk.medium: [40, 74] → Score 40 = MEDIUM
risk.high: [75, 100] → Score 75 = HIGH
```

### 5.4 Cumulative vs. Single-Operation Boundaries

| Boundary Type | Key Suffix | Behavior |
|---------------|------------|----------|
| Single operation | `.daily`, `.max` | Maximum per individual operation |
| Cumulative period | `.monthly`, `.yearly` | Sum of all operations in period |
| Rolling window | `.velocity`, `.window` | Sum within sliding time window |

```yaml
quota.l1.daily: 1000      # Single-operation max
quota.l1.monthly: 5000    # Cumulative monthly total
rate.tx.user.velocity: 5  # Rolling: 5 operations per window
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

```text
@threshold: {DOC_TYPE}.{DOC_NUM}.{threshold_key}
```

| Component | Format | Example |
|-----------|--------|---------|
| `DOC_TYPE` | BRD, PRD, or ADR | `PRD`, `ADR` |
| `DOC_NUM` | 2+ digit number (starts at 01) | `01`, `15`, `100` |
| `threshold_key` | Dot-separated key | `quota.l1.daily`, `circuit.failure.count` |

### 6.2 Reference Formats by Context

| Context | Format | Example |
|---------|--------|---------|
| @threshold: tag | `@threshold: {TYPE}.{NUM}.{key}` | `@threshold: PRD.01.quota.l1.daily` |
| Inline citation | `per @threshold: {TYPE}.{NUM}.{key}` | `the daily limit per @threshold: PRD.01.quota.l1.daily` |
| Code constant | `THRESHOLD_{CATEGORY}_{KEY}` | `THRESHOLD_QUOTA_L1_DAILY` |
| Config path | `thresholds.{key}` | `thresholds.quota.l1.daily` |
| Environment var | `THRESHOLD_{CATEGORY}_{KEY}` | `THRESHOLD_QUOTA_L1_DAILY=1000` |

### 6.3 Consumer Document Requirements

All downstream documents referencing thresholds MUST:

1. **Declare threshold dependencies** in a dedicated section:

   ```markdown
   ## Thresholds Referenced

   @threshold: PRD.01.quota.l1.daily
   @threshold: PRD.01.quota.l1.monthly
   @threshold: BRD.02.risk.high.min
   ```

2. **Reference values inline** with the tag:

   ```markdown
   L1 users limited to the L1 daily ceiling (per @threshold: PRD.01.quota.l1.daily)
   ```

3. **Never hardcode values** — always use `@threshold:` tags.

### 6.4 Source Resolution

When multiple documents could define similar thresholds, establish clear
ownership:

| Threshold Domain | Source Document | Rationale |
|------------------|-----------------|-----------|
| Compliance/business limits | BRD | Regulatory/business authority |
| Product feature limits | PRD | Product-level decisions |
| Risk scores | BRD | Platform-level risk framework |
| Circuit breakers, pools | ADR | Technical architecture decisions |
| Performance SLAs (p95/p99) | ADR | Technical performance targets |
| API rate limits | PRD or ADR | Product (user quotas) or technical (system protection) |

**Conflict resolution rules**:

1. **Business vs technical**: BRD/PRD own business thresholds; ADR owns technical thresholds.
2. **Platform vs product**: BRD takes precedence over PRD for platform-level thresholds.
3. **When unclear**: the document where the threshold is first justified owns it.

---

## 7. Definition Rules

### 7.1 Percentile Definitions

| Qualifier | Percentile | Statistical Definition | Operational Purpose |
|-----------|------------|------------------------|---------------------|
| `p50` | 50th | Median — 50% of requests faster | Typical/expected performance |
| `p90` | 90th | 90% of requests faster | Near-worst-case baseline |
| `p95` | 95th | 95% of requests faster | **Performance target (SLO)** |
| `p99` | 99th | 99% of requests faster | **Alert threshold** |
| `p999` | 99.9th | 99.9% of requests faster | SLA boundary / critical |

### 7.2 Tiered Level Definitions

Tier qualifiers (`low`/`medium`/`high`, or `l1`/`l2`/`l3`) name escalating
levels of a score, limit, or capability. The number of tiers, their numeric
ranges, and the action each triggers are **project-defined** in the source
document. Example (a 3-tier risk score):

| Level | Score Range | Required Action (project-defined) |
|-------|-------------|-----------------------------------|
| Low | 0-39 | Auto-approve |
| Medium | 40-74 | Manual review |
| High | 75-100 | Block + escalate |

Tiered limits (`l1`/`l2`/`l3`) follow the same shape — higher tiers carry higher
ceilings; the scaling factor between tiers is a project decision documented in
the source YAML.

### 7.3 Alert Severity Definitions

| Severity | Definition | Response Time | Escalation |
|----------|------------|---------------|------------|
| `info` | Informational, no action | None | None |
| `warning` | Approaching threshold | 1 hour | On-call |
| `critical` | Threshold exceeded | 15 minutes | Incident manager |
| `emergency` | System-wide impact | Immediate | Executive escalation |

### 7.4 Timeout Category Definitions

| Category | Typical Range | Use Case |
|----------|---------------|----------|
| `partner.*` | 15-60 seconds | External API calls |
| `session.*` | 300-86400 seconds | User session management |
| `job.*` | 1800-7200 seconds | Background batch processing |
| `validity.*` | 60-300 seconds | Token/quote expiration |

### 7.5 Rate Limit Window Definitions

| Window Type | Duration | Reset Behavior |
|-------------|----------|----------------|
| `burst` | 1 second | Rolling window |
| `standard` | 60 seconds (1 min) | Rolling window |
| `hourly` | 3600 seconds | Fixed hourly reset |
| `daily` | 86400 seconds | Fixed daily reset (UTC) |

---

## 8. Weight Factor Rules

### 8.1 Sum Constraint Rules

| Rule | Requirement |
|------|-------------|
| Sum constraint | All weights in a category MUST sum to 1.0 |
| Precision | Use a maximum of 2 decimal places (0.25, not 0.2534) |
| Documentation | Document percentage contribution alongside the ratio |

```yaml
risk.weight:
  factor_a: 0.25   # 25% contribution
  factor_b: 0.20   # 20% contribution
  factor_c: 0.20   # 20% contribution
  factor_d: 0.15   # 15% contribution
  factor_e: 0.10   # 10% contribution
  factor_f: 0.10   # 10% contribution
  # Total: 1.00
```

---

## 9. Configuration Structure

```yaml
thresholds:
  {category}:
    {subcategory}:        # optional level — omit when the category alone scopes the metric
      {attribute}: {value}
```

**Example**:

```yaml
thresholds:
  quota:
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

## 10. Validation Rules

### 10.1 Required Validations

| Validation | Rule |
|------------|------|
| Type safety | Value MUST match declared type |
| Range validation | Value MUST be within min/max bounds |
| Unit consistency | All values in a category MUST use the same unit |
| Reference integrity | Cross-references MUST point to valid keys |
| Sum constraints | Weight factors MUST sum to 1.0 |

### 10.2 Logical Consistency

| Constraint | Example |
|------------|---------|
| Range ordering | `risk.low.max` < `risk.medium.min` |
| Tier progression | `quota.l1.daily` < `quota.l2.daily` < `quota.l3.daily` |
| Alert ordering | `alert.*.warning` < `alert.*.critical` |
| Percentile ordering | `perf.*.p50` < `perf.*.p95` < `perf.*.p99` |

---

## 11. Governance

Thresholds are governed as part of the source document that defines them. A
change to a threshold value is a change to its BRD/PRD/ADR, and follows the
normal readiness gates and (post-cutover) change-management process for that
document — including its audit trail and approver set.

> **Out of scope.** Runtime concerns — how fast a configuration change
> propagates, environment-specific overrides, rollback timing, and operational
> approval workflows — are a consuming project's deployment/config policy, not
> part of this naming standard. Define them in the project's own configuration
> governance, not here.

---

## 12. Anti-Patterns

### 12.1 Naming Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| `maxDailyLimit` | CamelCase, redundant | `quota.l1.daily` |
| `threshold_1` | Meaningless identifier | `risk.low.max` |
| `QUOTA_DAILY_L1` | Wrong case, wrong separator | `quota.l1.daily` |
| `perf.api.response.time.milliseconds.p95` | Too verbose | `perf.api.standard.p95` |
| `limit` | No context | `rate.api.user.standard` |

### 12.2 Usage Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Hardcoded values | No single source of truth | Use `@threshold:` tag |
| Inline magic numbers | Unmaintainable | Use `@threshold:` tag with key |
| Duplicate definitions | Conflicts | Single BRD/PRD definition |
| Missing units | Ambiguous | Comment with unit in YAML |
| No @threshold: tags | Broken traceability | Always reference the source doc |

---

## 13. Quick Reference

### 13.1 Key Construction Template

```text
{category}[.{scope}].{metric}[.{qualifier}]
                              │
                              └─ Optional: min/max/p50/p95/warning/critical
                      └──────── Required: daily/monthly/timeout/rate
              └───────────────── Optional: l1/l2/l3/api/partner/user/session
      └─────────────────────── Required: quota/risk/perf/timeout/rate/alert
```

The `{scope}` (subcategory) segment is **optional** — omit it when the category
alone scopes the metric (e.g. `perf.p95_latency`). The key is a minimum of two
dot-separated segments (`{category}.{metric}`), per §2.1 and the authoritative
`id_patterns.threshold` regex.

### 13.2 Common Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| `{domain}.l{n}.{period}` | Tiered velocity limits | `quota.l1.daily` |
| `{domain}.{scope}.p{nn}` | Percentile metrics | `perf.api.standard.p95` |
| `{domain}.{target}.{action}` | External service config | `timeout.partner.default` |
| `{domain}.{level}.{boundary}` | Risk/alert ranges | `risk.medium.max` |

### 13.3 Checklist for New Thresholds

- [ ] Key follows `category[.subcategory].attribute` format (subcategory optional; key is ≥2 dot-separated segments)
- [ ] Uses lowercase with dot separators
- [ ] Defined in the appropriate BRD/PRD/ADR with a YAML block
- [ ] Type specified (integer/decimal/ratio/percent/score)
- [ ] Unit specified in a YAML comment
- [ ] Boundary behavior documented in a comment
- [ ] `@threshold:` tags added to downstream documents
- [ ] Logical consistency validated

---

*Provenance: extracted into the engine-agnostic framework spec from the
pre-migration SDD governance set; domain-specific (financial) examples were
genericized and runtime/operational override policy removed during the
pre-production review. Versioned with the framework spec (`framework/VERSION`);
changes are tracked in the project `CHANGELOG.md` under GATE-SPEC.*
