# Implementation Plan - @threshold Tag Governance - Prevent Magic Numbers in Requirements

**Created**: 2025-11-30 11:39:49 EST
**Status**: Ready for Implementation

## Objective

Implement `@threshold` tag governance across the doc_flow SDD framework to:
1. **Prevent magic numbers** in requirements documents
2. **Ensure centralized management** of business-critical values
3. **Create reusable Platform Threshold Registry template** for projects

---

## Context

### Problem Statement

**Without @threshold tags (magic numbers):**
```markdown
WHEN a transaction exceeds $3,000,
THE system SHALL trigger Travel Rule compliance
WITHIN 500ms.
```

**With @threshold tags (centralized governance):**
```markdown
WHEN a transaction exceeds @threshold: PRD-035:compliance.travel_rule.amount,
THE system SHALL trigger Travel Rule compliance
WITHIN @threshold: PRD-035:perf.compliance.response_time.
```

**Benefits:**
- Single source of truth for all business-critical values
- Change one value → propagates to all documents
- Audit trail for threshold changes
- Prevents conflicting values across documents
- Enables environment-specific overrides

### Document Type Assessment

| Document | Layer | Contains Quantitative Values? | @threshold Required? |
|----------|-------|------------------------------|---------------------|
| **EARS** | 3 | WITHIN timing, boundary limits | Already implemented |
| **BDD** | 4 | Performance scenarios, SLA targets | Yes |
| **SYS** | 6 | NFRs (p50/p95/p99), SLAs, resource limits | Yes |
| **REQ** | 7 | Performance targets, circuit breaker configs | Yes |
| **SPEC** | 10 | Latency targets, timeout configs, rate limits | Yes |
| **PRD** | 2 | Feature thresholds | Registry source only |
| **BRD** | 1 | Business-level goals | No |
| **ADR** | 5 | Architecture constraints (rare) | Optional |

### Threshold Key Naming Convention

| Level | Format | Example |
|-------|--------|---------|
| Category | lowercase | `perf`, `timeout`, `sla`, `compliance`, `limit` |
| Subcategory | dot-separated | `perf.api`, `timeout.circuit_breaker` |
| Key | dot-separated | `perf.api.p95_latency`, `timeout.circuit_breaker.threshold` |

**Standard Categories**:
- `perf.*` - Performance thresholds (latency, throughput)
- `timeout.*` - Timeout configurations
- `sla.*` - SLA targets (uptime, recovery)
- `limit.*` - Rate limits, resource limits
- `compliance.*` - Regulatory thresholds
- `resource.*` - Resource utilization limits

---

## Task List

### Completed
- [x] Analyze document types for @threshold applicability
- [x] Create implementation plan
- [x] Get user approval on plan

### Pending
- [ ] Create `ai_dev_flow/PRD/PRD-000_threshold_registry_template.md` (foundation)
- [ ] Update `ai_dev_flow/SYS/SYS_CREATION_RULES.md` - Add Threshold Registry Integration section (v1.1 → 1.2)
- [ ] Update `ai_dev_flow/REQ/REQ_CREATION_RULES.md` - Add Threshold Registry Integration section (v3.1 → 3.2)
- [ ] Update `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md` - Add Threshold Registry Integration section (v1.1 → 1.2)
- [ ] Update `ai_dev_flow/BDD/BDD_CREATION_RULES.md` - Add Threshold Registry Integration section (v1.1 → 1.2)
- [ ] Update `ai_dev_flow/BDD/BDD-TEMPLATE.feature` - Add @threshold to tags
- [ ] Update `ai_dev_flow/SYS/SYS-TEMPLATE.md` - Add @threshold examples
- [ ] Update `ai_dev_flow/REQ/REQ-TEMPLATE.md` - Add @threshold examples
- [ ] Update `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml` - Add threshold_references
- [ ] Create `ai_dev_flow/scripts/detect_magic_numbers.py` - Validation script

---

## Implementation Guide

### Phase 1: Create Threshold Registry Template

**File**: `ai_dev_flow/PRD/PRD-000_threshold_registry_template.md`

**Structure**:
```markdown
# PRD-NNN: [Project Name] Platform Threshold Registry

## Document Control
| Item | Details |
|------|---------|
| **Purpose** | Centralized threshold registry for [project] |
| **Authority** | This registry is authoritative for all threshold values |

## 1. Performance Thresholds
### 1.1 API Response Times
| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `perf.api.p50_latency` | 50 | ms | Median |
| `perf.api.p95_latency` | 200 | ms | 95th percentile |

## 2. Reliability Thresholds
### 2.1 SLA Targets
| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `sla.uptime.target` | 99.9 | % | Monthly uptime |

## 3. Timeout Configurations
### 3.1 Circuit Breaker
| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `timeout.circuit_breaker.threshold` | 5 | failures | Before open |

## 4. Business Limits
### 4.1 Compliance Thresholds
| Key | Value | Unit | Notes |
|-----|-------|------|-------|
| `compliance.travel_rule.amount` | 3000 | USD | Travel Rule threshold |
```

### Phase 2: Update Creation Rules (4 documents)

**Files to modify:**
1. `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
2. `ai_dev_flow/SYS/SYS_CREATION_RULES.md`
3. `ai_dev_flow/REQ/REQ_CREATION_RULES.md`
4. `ai_dev_flow/SPEC/SPEC_CREATION_RULES.md`

**Add new section**: "Threshold Registry Integration"

```markdown
## N. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values that are:
- Business-critical (compliance limits, SLAs)
- Configurable (timeout values, rate limits)
- Shared across documents (performance targets)

### @threshold Tag Format

```markdown
@threshold: PRD-NNN:category.subcategory.key
```

**Examples**:
- `@threshold: PRD-035:perf.api.p95_latency`
- `@threshold: PRD-035:timeout.circuit_breaker.threshold`
- `@threshold: PRD-035:compliance.travel_rule.amount`

### Magic Number Detection

**Invalid (hardcoded values)**:
- `response time < 200ms`
- `timeout of 5000ms`
- `threshold of $3,000`

**Valid (registry references)**:
- `response time < @threshold: PRD-035:perf.api.p95_latency`
- `timeout of @threshold: PRD-035:timeout.default`
- `threshold of @threshold: PRD-035:compliance.travel_rule.amount`
```

**Update Common Mistakes Table** in each file:

| Mistake | Correct |
|---------|---------|
| `response time < 200ms` (hardcoded) | `response time < @threshold: PRD-035:perf.api.p95_latency` |
| `timeout: 5000` (magic number) | `timeout: @threshold: PRD-035:timeout.default` |
| `limit: $3000` (hardcoded compliance value) | `limit: @threshold: PRD-035:compliance.travel_rule.amount` |

**Update Traceability Requirements** - add `@threshold` to Required Tags table:

| Tag | Format | When Required |
|-----|--------|---------------|
| @threshold | PRD-NNN:category.key | When referencing timing, limits, or configurable values |

### Phase 3: Update Templates (4 templates)

**Files to modify:**
1. `ai_dev_flow/BDD/BDD-TEMPLATE.feature`
2. `ai_dev_flow/SYS/SYS-TEMPLATE.md`
3. `ai_dev_flow/REQ/REQ-TEMPLATE.md`
4. `ai_dev_flow/SPEC/SPEC-TEMPLATE.yaml`

**Additions**:
- Add `@threshold` to traceability tag examples
- Add Threshold Registry to upstream sources
- Add example usage in quantitative sections

### Phase 4: Create Validation Script

**File**: `ai_dev_flow/scripts/detect_magic_numbers.py`

**Detection patterns**:
```python
# Units that indicate magic numbers requiring @threshold
MAGIC_NUMBER_UNITS = [
    r'\d+\s*ms\b',           # milliseconds
    r'\d+\s*seconds?\b',     # seconds
    r'\d+\s*minutes?\b',     # minutes
    r'\d+\s*hours?\b',       # hours
    r'\d+(\.\d+)?\s*%',      # percentages
    r'\$\d+',                # dollar amounts
    r'\d+\s*USD\b',          # USD amounts
    r'\d+\s*req/s\b',        # requests per second
    r'\d+\s*IOPS\b',         # I/O operations
    r'\d+\s*(GB|MB|KB)\b',   # storage sizes
]

# Exceptions (allowed without @threshold)
ALLOWED_PATTERNS = [
    r'@threshold:',          # Already uses threshold reference
    r'Version:?\s*\d+',      # Version numbers
    r'Layer\s*\d+',          # Layer numbers
    r'Section\s*\d+',        # Section references
    r'NNN',                  # Template placeholders
]
```

**Output format**:
```
ERROR: Magic number detected in docs/SYS/SYS-001.md:45
  Found: "response time < 200ms"
  Suggestion: Use @threshold: PRD-NNN:perf.api.p95_latency

WARNING: Potential magic number in docs/REQ/REQ-003.md:123
  Found: "timeout of 5000ms"
  Suggestion: Use @threshold: PRD-NNN:timeout.default
```

---

## Verification

After implementation:
1. Run `python ai_dev_flow/scripts/detect_magic_numbers.py` on sample docs
2. Verify all creation rules have Threshold Registry Integration section
3. Verify all templates show @threshold examples
4. Validate PRD-000_threshold_registry_template.md is complete

---

## References

- Plan file: `/home/ya/.claude/plans/purring-jingling-minsky.md`
- Existing @threshold implementation: `ai_dev_flow/EARS/EARS_CREATION_RULES.md`
- PRD Threshold section reference: `ai_dev_flow/PRD/PRD_CREATION_RULES.md` §19

---

## Summary

**Total files**: 10 (2 new + 8 modified)
**Governance rule**: All quantitative business-critical values must use @threshold references
**Enforcement**: Pre-commit validation script blocks magic numbers
