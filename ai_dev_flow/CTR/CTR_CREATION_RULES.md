---
title: "CTR Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: creation_rules
  artifact_type: CTR
  layer: 9
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for CTR-TEMPLATE.md/.yaml.
> - **Authority**: `CTR-TEMPLATE.md` and `CTR-TEMPLATE.yaml` are the sources of truth for CTR structure
> - **Validation**: Use `CTR_VALIDATION_RULES.md` after CTR creation/changes

# CTR Creation Rules

Rules for creating Data Contracts (CTR) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

---

## 1. When to Create a CTR Document

### Create CTR When

- [ ] External API integration requires formal interface definition
- [ ] Service-to-service communication needs contract enforcement
- [ ] Multiple consumers depend on consistent data structures
- [ ] Schema evolution must be managed across versions
- [ ] API versioning strategy requires documentation

### Do NOT Create CTR When

- [ ] Internal-only data structures (use SPEC instead)
- [ ] Implementation contracts between TASKS (use ICON instead)
- [ ] Temporary or experimental interfaces
- [ ] Simple configuration without external consumers

---

## 2. File Naming Convention

### Format

```
CTR-NNN_{descriptive_slug}.md
CTR-NNN_{descriptive_slug}.yaml
```

### Rules

1. **CTR-NNN**: Sequential numbering starting from 001
2. **descriptive_slug**: Lowercase with underscores
3. **Extension**: `.md` for documentation, `.yaml` for schema
4. **Dual-file**: Create both `.md` and `.yaml` for complete contracts

### Examples

- `CTR-001_user_authentication_api.md`
- `CTR-001_user_authentication_api.yaml`
- `CTR-002_market_data_feed.md`
- `CTR-003_order_execution_service.md`

---

## 3. Required Sections (Markdown)

### 3.1 Frontmatter

```yaml
---
title: "CTR-NNN: [Contract Name]"
tags:
  - contract
  - layer-9-artifact
  - api-contract
custom_fields:
  document_type: contract
  artifact_type: CTR
  layer: 9
  contract_version: "1.0.0"
---
```

### 3.2 Document Control Table

| Field | Required | Description |
|-------|----------|-------------|
| Contract ID | Yes | CTR-NNN format |
| Title | Yes | Descriptive contract name |
| Version | Yes | Semantic version (X.Y.Z) |
| Status | Yes | Draft/Active/Deprecated |
| Created | Yes | YYYY-MM-DD |
| Last Updated | Yes | YYYY-MM-DD |
| Author | Yes | Creator name |
| Consumers | Yes | List of consuming systems |
| Providers | Yes | List of providing systems |

### 3.3 Mandatory Sections

1. **Executive Summary** - Contract purpose and scope
2. **API Endpoints** - Complete endpoint documentation
3. **Data Models** - Request/response schemas
4. **Authentication** - Security requirements
5. **Error Handling** - Error codes and responses
6. **Versioning Strategy** - How versions evolve
7. **SLA Requirements** - Performance and availability targets
8. **Traceability Tags** - Links to upstream artifacts

---

## 4. Required Sections (YAML)

### 4.1 OpenAPI Structure

```yaml
openapi: "3.0.3"
info:
  title: "[Contract Name]"
  version: "1.0.0"
  description: "[Contract description]"
  contact:
    name: "[Team name]"
paths:
  /endpoint:
    get:
      summary: "[Endpoint summary]"
      responses:
        '200':
          description: "Success"
components:
  schemas:
    ModelName:
      type: object
      properties:
        field_name:
          type: string
```

### 4.2 Required Components

| Component | Required | Description |
|-----------|----------|-------------|
| openapi | Yes | Version specification |
| info | Yes | Contract metadata |
| paths | Yes | API endpoints |
| components/schemas | Yes | Data models |
| components/responses | Recommended | Reusable responses |
| components/securitySchemes | Conditional | If auth required |

---

## 5. Traceability Requirements

### 5.1 Upstream References

CTR must reference:
- `@req: REQ-NNN` - Atomic requirements
- `@spec: SPEC-NNN` - Technical specifications
- `@adr: ADR-NNN` - Architecture decisions

### 5.2 Downstream References

CTR is referenced by:
- `@tasks: TASKS-NNN` - Implementation tasks
- `@iplan: IPLAN-NNN` - Implementation plans
- Code implementations

### 5.3 Tag Format

```markdown
## Traceability Tags

@req: REQ-001, REQ-002
@adr: ADR-003
@spec: SPEC-001:api_client
```

---

## 6. Quality Checklist

### Before Creating

- [ ] Verify contract is needed (not just internal interface)
- [ ] Check for existing similar contracts
- [ ] Identify all consumers and providers
- [ ] Determine versioning strategy

### During Creation

- [ ] Use CTR-TEMPLATE.md as starting point
- [ ] Follow OpenAPI 3.0+ specification
- [ ] Include complete error handling
- [ ] Document all data models
- [ ] Add authentication requirements
- [ ] Define SLA targets

### After Creation

- [ ] Validate YAML against OpenAPI schema
- [ ] Verify all endpoints documented
- [ ] Test example requests/responses
- [ ] Update CTR-000_index.md
- [ ] Notify consumers of new contract
- [ ] Run validation script

---

## 7. Common Anti-Patterns

### Avoid

1. **Incomplete error handling** - Document all error codes
2. **Missing versioning** - Always include version strategy
3. **No authentication** - Security must be defined
4. **Orphaned contracts** - Must have consumers
5. **Duplicate contracts** - Check for existing before creating
6. **Missing traceability** - Always link to upstream artifacts

---

## 8. Validation

### Automated Validation

```bash
./scripts/validate_ctr.sh /path/to/CTR-NNN_name.md
```

### Manual Checklist

- [ ] Filename follows convention
- [ ] All required sections present
- [ ] YAML validates against OpenAPI schema
- [ ] Traceability tags complete
- [ ] Registered in CTR-000_index.md

---

## 9. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-001 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-001 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable


## References

- [CTR-TEMPLATE.md](./CTR-TEMPLATE.md) - Contract template
- [CTR-TEMPLATE.yaml](./CTR-TEMPLATE.yaml) - YAML template
- [CTR-000_index.md](./CTR-000_index.md) - Contract registry
- [README.md](./README.md) - Directory overview
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27
