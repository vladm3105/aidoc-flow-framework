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

> Reference Template — For learning and small specs only. Real SPECs use a monolithic YAML per component for code generation. When narrative grows, split the Markdown only per `../DOCUMENT_SPLITTING_RULES.md` and `10_SPEC/SPEC_SPLITTING_RULES.md`.

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

**Threshold Naming Convention**: `@threshold: PRD.NN.category.subcategory.key`

**Format Reference**: See [THRESHOLD_NAMING_RULES.md](../THRESHOLD_NAMING_RULES.md) for complete naming standards.

**Thresholds Used in This Document**:
```yaml
performance:
  - "@threshold: PRD.NN.perf.api.p50_latency"        # p50 latency requirement
  - "@threshold: PRD.NN.perf.api.p95_latency"        # p95 latency requirement
  - "@threshold: PRD.NN.perf.api.p99_latency"        # p99 latency requirement
  - "@threshold: PRD.NN.perf.throughput.rps"         # Throughput requirement

sla:
  - "@threshold: PRD.NN.sla.uptime.target"           # Uptime SLA target
  - "@threshold: PRD.NN.sla.error_rate.max"          # Maximum error rate

timeout:
  - "@threshold: PRD.NN.timeout.request.sync"        # Synchronous request timeout
  - "@threshold: PRD.NN.timeout.request.async"       # Asynchronous request timeout
  - "@threshold: PRD.NN.timeout.connection.default"  # Connection timeout

limits:
  - "@threshold: PRD.NN.limit.api.requests_per_second"  # Rate limit
  - "@threshold: PRD.NN.limit.batch.size"               # Maximum batch size
  - "@threshold: PRD.NN.limit.batch.concurrent"         # Concurrent batch limit

resource:
  - "@threshold: PRD.NN.resource.cpu.max_utilization"   # CPU utilization limit
  - "@threshold: PRD.NN.resource.memory.max_mb"         # Memory limit
```

**Example Usage in Specification**:
```yaml
# Performance Requirements
performance_requirements:
  api_latency:
    p95_target: "@threshold: PRD.NN.perf.api.p95_latency"
    p99_target: "@threshold: PRD.NN.perf.api.p99_latency"
  throughput:
    target_rps: "@threshold: PRD.NN.perf.throughput.rps"

# Configuration Parameters
configuration:
  timeouts:
    request_timeout: "@threshold: PRD.NN.timeout.request.sync"
    connection_timeout: "@threshold: PRD.NN.timeout.connection.default"
```

**Note**: For the full SPEC structure with all traceability fields, see `SPEC-TEMPLATE.yaml`.
## File Size Limits

- Target (Markdown): 300–500 lines per section file
- Maximum (Markdown): 600 lines per section file (absolute)
- YAML (monolithic): Warnings at ~1000 lines, errors at ~2000 lines in linter; keep YAML monolithic and move narrative to Markdown sections if readability suffers.

## Document Splitting Standard

Split Markdown when the narrative becomes large or logically separable by audience/domain:
- Create `SPEC-{DOC_NUM}.0_index.md` and one or more `SPEC-{DOC_NUM}.{S}_{slug}.md` files
- Keep the SPEC YAML as a single file; move explanatory content to Markdown
- Validate links and cross-references; ensure YAML traceability remains complete
