# =============================================================================
# 📋 Document Authority: This is the PRIMARY STANDARD for SPEC Markdown structure.
# All other documents (Schema, Creation Rules, Validation Rules) DERIVE from this template.
# - In case of conflict, this template is the single source of truth
# - Schema: SPEC_SCHEMA.yaml - Machine-readable validation (derivative)
# - Creation Rules: SPEC_CREATION_RULES.md - AI guidance for document creation (derivative)
# - Validation Rules: SPEC_VALIDATION_RULES.md - AI checklist after document creation (derivative)
#   NOTE: VALIDATION_RULES includes all CREATION_RULES and may be extended for validation
# =============================================================================
---
title: "SPEC-TEMPLATE: Technical Specification"
tags:
  - spec-template
  - layer-10-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  artifact_type: SPEC
  layer: 10
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_for: technical-specification
  schema_reference: "SPEC_SCHEMA.yaml"
  schema_version: "1.0"
---

> **📋 Document Authority**: This is the **PRIMARY STANDARD** for SPEC Markdown structure.
> - All SPEC Markdown documents must conform to this template
> - `SPEC_CREATION_RULES.md` - Helper guidance for template usage
> - `SPEC_VALIDATION_RULES.md` - Post-creation validation checks

> **⚠️ UPSTREAM ARTIFACT REQUIREMENT**: Before completing traceability tags:
> 1. **Check existing artifacts**: List what upstream documents actually exist in `docs/`
> 2. **Reference only existing documents**: Use actual document IDs, not placeholders
> 3. **Use `null` appropriately**: Only when upstream artifact type genuinely doesn't exist for this feature
> 4. **Do NOT create phantom references**: Never reference documents that don't exist
> 5. **Do NOT create missing upstream artifacts**: If upstream artifacts are missing, skip that functionality. Only create functionality for existing upstream artifacts.

---

## Thresholds Referenced

**Purpose**: SPEC documents REFERENCE thresholds defined in the PRD threshold registry. All quantitative values in performance requirements, SLA targets, and configuration parameters must use `@threshold:` tags to ensure single source of truth.

**Threshold Naming Convention**: `@threshold: PRD.NNN.category.subcategory.key`

**Format Reference**: See [THRESHOLD_NAMING_RULES.md](../THRESHOLD_NAMING_RULES.md) for complete naming standards.

**Thresholds Used in This Document**:
```yaml
performance:
  - "@threshold: PRD.NNN.perf.api.p50_latency"        # p50 latency requirement
  - "@threshold: PRD.NNN.perf.api.p95_latency"        # p95 latency requirement
  - "@threshold: PRD.NNN.perf.api.p99_latency"        # p99 latency requirement
  - "@threshold: PRD.NNN.perf.throughput.rps"         # Throughput requirement

sla:
  - "@threshold: PRD.NNN.sla.uptime.target"           # Uptime SLA target
  - "@threshold: PRD.NNN.sla.error_rate.max"          # Maximum error rate

timeout:
  - "@threshold: PRD.NNN.timeout.request.sync"        # Synchronous request timeout
  - "@threshold: PRD.NNN.timeout.request.async"       # Asynchronous request timeout
  - "@threshold: PRD.NNN.timeout.connection.default"  # Connection timeout

limits:
  - "@threshold: PRD.NNN.limit.api.requests_per_second"  # Rate limit
  - "@threshold: PRD.NNN.limit.batch.size"               # Maximum batch size
  - "@threshold: PRD.NNN.limit.batch.concurrent"         # Concurrent batch limit

resource:
  - "@threshold: PRD.NNN.resource.cpu.max_utilization"   # CPU utilization limit
  - "@threshold: PRD.NNN.resource.memory.max_mb"         # Memory limit
```

**Example Usage in Specification**:
```yaml
# Performance Requirements
performance_requirements:
  api_latency:
    p95_target: "@threshold: PRD.NNN.perf.api.p95_latency"
    p99_target: "@threshold: PRD.NNN.perf.api.p99_latency"
  throughput:
    target_rps: "@threshold: PRD.NNN.perf.throughput.rps"

# Configuration Parameters
configuration:
  timeouts:
    request_timeout: "@threshold: PRD.NNN.timeout.request.sync"
    connection_timeout: "@threshold: PRD.NNN.timeout.connection.default"
```

**Note**: For the full SPEC structure with all traceability fields, see `SPEC-TEMPLATE.yaml`.
