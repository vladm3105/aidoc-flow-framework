---
name: doc-ctr
description: Create Data Contracts (CTR) - Optional Layer 9 artifact using dual-file format (.md + .yaml) for API/data contracts
tags:
  - sdd-workflow
  - layer-9-artifact
  - shared-architecture
  - documentation-skill
custom_fields:
  layer: 9
  artifact_type: CTR
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [IMPL]
  downstream_artifacts: [SPEC]
---

# doc-ctr

## Purpose

Create **Data Contracts (CTR)** - Optional Layer 9 artifact in the SDD workflow that defines API contracts, data schemas, and interface specifications using dual-file format (markdown + YAML).

**Layer**: 9 (Optional)

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SYS (Layer 6), REQ (Layer 7), IMPL (Layer 8)

**Downstream Artifacts**: SPEC (Layer 10), TASKS (Layer 11), Code (Layer 13)

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/BRD/ docs/PRD/ docs/EARS/ docs/BDD/ docs/ADR/ docs/SYS/ docs/REQ/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating CTR, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream REQ**: Read atomic requirements (especially Section 3: Interface Specifications, Section 4: Data Schemas)
3. **Template**: `ai_dev_flow/CTR/CTR-TEMPLATE.md` and `CTR-TEMPLATE.yaml`
4. **Creation Rules**: `ai_dev_flow/CTR/CTR_CREATION_RULES.md`
5. **Validation Rules**: `ai_dev_flow/CTR/CTR_VALIDATION_RULES.md`
6. **Validation Script**: `./ai_dev_flow/scripts/validate_ctr.sh`

## When to Use This Skill

Use `doc-ctr` when:
- Have completed BRD through REQ (Layers 1-7)
- Need to define API contracts or data schemas
- Multiple teams/services need shared contracts
- Building microservices or distributed systems
- REQ Section 3 (Interface Specifications) needs formal contract
- This layer is **OPTIONAL** - skip if contracts are simple

## CTR-Specific Guidance

### 1. Mandatory Dual-File Format

**Two files required** for each contract (mandatory dual-file format: `.md` file + companion `.yaml` file):

**Markdown File** (`.md`):
- Document Control section
- Contract overview
- Business context
- Usage examples
- Traceability

**YAML File** (`.yaml`):
- OpenAPI 3.0 or JSON Schema
- Formal contract definition
- Validation rules
- Example payloads

**Example**:
```
ai_dev_flow/CTR/CTR-001_data_validation.md
ai_dev_flow/CTR/CTR-001_data_validation.yaml
```

### 2. Required Sections (Markdown File)

**Document Control** (MANDATORY - First section before all numbered sections)

**Core Sections**:
1. **Contract Overview**: Purpose, scope, version
2. **Business Context**: Why this contract exists (link to REQ)
3. **Contract Definition**: Reference to YAML file
4. **Usage Examples**: Request/response examples
5. **Validation Rules**: Schema validation, business rules
6. **Error Handling**: Error codes and responses
7. **Traceability**: Section 7 format with cumulative tags

### 3. YAML Contract Format

**OpenAPI 3.0 Format** (for APIs):
```yaml
openapi: 3.0.3
info:
  title: Data Validation API
  version: 1.0.0
  description: Contract for data validation

paths:
  /api/v1/data/validate:
    post:
      summary: Validate data record
      operationId: validateDataRecord
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DataRequest'
      responses:
        '200':
          description: Validation successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationResponse'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

components:
  schemas:
    DataRequest:
      type: object
      required:
        - record_type
        - record_id
        - data
        - account_id
      properties:
        record_type:
          type: string
          pattern: ^[A-Z]{1,10}$
          example: "METRIC"
        record_id:
          type: string
          format: uuid
          example: "abc123"
        data:
          type: object
          example: {}
        account_id:
          type: string
          format: uuid
          example: "123e4567-e89b-12d3-a456-426614174000"

    ValidationResponse:
      type: object
      required:
        - valid
        - order_id
      properties:
        valid:
          type: boolean
          example: true
        order_id:
          type: string
          format: uuid
          example: "987f6543-e21c-43d2-b654-426614174111"
        warnings:
          type: array
          items:
            type: string
          example: ["Price near market close"]

    ErrorResponse:
      type: object
      required:
        - error_code
        - message
      properties:
        error_code:
          type: string
          example: "INVALID_SYMBOL"
        message:
          type: string
          example: "Symbol 'XYZ' not found in approved list"
        details:
          type: object
          additionalProperties: true
```

**JSON Schema Format** (for data models):
```yaml
$schema: "http://json-schema.org/draft-07/schema#"
title: DataProcessingConfig
description: Configuration schema for data processing

type: object
required:
  - max_batch_size
  - timeout_seconds
  - check_frequency

properties:
  max_batch_size:
    type: integer
    minimum: 1
    maximum: 10000
    description: Maximum records per batch
    example: 1000

  timeout_seconds:
    type: integer
    minimum: 1
    maximum: 300
    description: Processing timeout in seconds
    example: 60

  check_frequency:
    type: string
    enum: ["realtime", "1min", "5min", "15min"]
    description: How often to check processing status
    example: "1min"

  alert_threshold:
    type: number
    minimum: 0
    maximum: 1.0
    description: Alert when queue depth exceeds this fraction
    default: 0.80
    example: 0.80
```

### 4. Usage Examples Section

**Format**:
```markdown
## Usage Examples

### Example 1: Successful Validation

**Request**:
```json
{
  "record_type": "METRIC",
  "record_id": "abc123",
  "data": {"value": 100},
  "account_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response**:
```json
{
  "valid": true,
  "order_id": "987f6543-e21c-43d2-b654-426614174111",
  "warnings": []
}
```

### Example 2: Invalid Record Type

**Request**:
```json
{
  "record_type": "invalid",
  "record_id": "abc123",
  "data": {"value": 100},
  "account_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Response** (400 Bad Request):
```json
{
  "error_code": "INVALID_RECORD_TYPE",
  "message": "Record type 'invalid' not found in approved list",
  "details": {
    "record_type": "invalid",
    "approved_types": ["METRIC", "EVENT", "LOG"]
  }
}
```
```

### 5. Contract Versioning

**Semantic Versioning**: Major.Minor.Patch

**Version Policy**:
- **Major**: Breaking changes (incompatible)
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

**Example**:
```yaml
openapi: 3.0.3
info:
  title: Data Validation API
  version: 2.1.0  # Major.Minor.Patch
  description: |
    Version 2.1.0 (2025-01-15)
    - Added: optional 'warnings' field in response (minor)
    - Fixed: validation error for edge case data (patch)

    Breaking changes from v1.x:
    - Changed: account_id now requires UUID format (was string)
```

## Cumulative Tagging Requirements

**Layer 9 (CTR)**: Must include tags from Layers 1-8 (BRD through IMPL)

**Tag Count**: 7-8 tags (7 if IMPL skipped, 8 if IMPL included)

**Format** (if IMPL included):
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 9):
```markdown
@brd: BRD-001:section-3
@prd: PRD-001:feature-2
@ears: EARS-001:E01
@bdd: BDD-001:scenario-validation
@adr: ADR-033, ADR-045
@sys: SYS-001:FR-001
@req: REQ-data-validation-001:section-3
@impl: IMPL-001:technical-approach
```

**Format** (if IMPL skipped):
```markdown
@brd: BRD-001:section-3
@prd: PRD-001:feature-2
@ears: EARS-001:E01
@bdd: BDD-001:scenario-validation
@adr: ADR-033, ADR-045
@sys: SYS-001:FR-001
@req: REQ-data-validation-001:section-3
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions
- **SYS** (Layer 6) - System requirements
- **REQ** (Layer 7) - Atomic requirements (PRIMARY SOURCE - especially Section 3)
- **IMPL** (Layer 8) - Implementation approach (optional)

**Downstream Artifacts**:
- **SPEC** (Layer 10) - Technical specifications
- **TASKS** (Layer 11) - Task breakdown
- **Code** (Layer 13) - Implementation

**Same-Type Document Relationships** (conditional):
- `@related-ctr: CTR-NNN` - CTRs sharing API context
- `@depends-ctr: CTR-NNN` - CTR that must be completed first

## Creation Process

### Step 1: Read Upstream Artifacts

Focus on REQ Section 3 (Interface Specifications) and Section 4 (Data Schemas).

### Step 2: Reserve ID Number

Check `ai_dev_flow/CTR/` for next available ID number.

### Step 3: Create CTR Files (Dual Format)

**Markdown file**: `ai_dev_flow/CTR/CTR-NNN_{slug}.md`
**YAML file**: `ai_dev_flow/CTR/CTR-NNN_{slug}.yaml`

**Example**:
- `ai_dev_flow/CTR/CTR-001_data_validation.md`
- `ai_dev_flow/CTR/CTR-001_data_validation.yaml`

### Step 4: Fill Document Control Section (Markdown)

Complete metadata and Document Revision History table.

### Step 5: Write Contract Overview (Markdown)

Summarize purpose, scope, and version.

### Step 6: Define YAML Contract

Choose format:
- **OpenAPI 3.0** for REST APIs
- **JSON Schema** for data models
- **AsyncAPI** for event-driven systems (if applicable)

### Step 7: Add Usage Examples (Markdown)

Provide request/response examples with explanations.

### Step 8: Document Validation Rules (Markdown)

Explain schema validation and business rules.

### Step 9: Specify Error Handling (Markdown)

Document error codes and responses.

### Step 10: Add Cumulative Tags

Include all 7-8 upstream tags (@brd through @req/impl).

### Step 11: Create/Update Traceability Matrix

**MANDATORY**: Update `ai_dev_flow/CTR/CTR-000_TRACEABILITY_MATRIX.md`

### Step 12: Validate CTR

```bash
# YAML schema validation
yamllint ai_dev_flow/CTR/CTR-001_*.yaml

# OpenAPI validation
openapi-spec-validator ai_dev_flow/CTR/CTR-001_*.yaml

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact CTR-001 --expected-layers brd,prd,ears,bdd,adr,sys,req,impl --strict
```

### Step 13: Commit Changes

Commit both files (.md and .yaml) and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
./scripts/validate_quality_gates.sh ai_dev_flow/CTR/CTR-001_*.md

# YAML validation
yamllint ai_dev_flow/CTR/CTR-001_*.yaml

# OpenAPI validation (if using OpenAPI)
openapi-spec-validator ai_dev_flow/CTR/CTR-001_*.yaml

# Dual-file check
python ai_dev_flow/scripts/check_dual_files.py CTR-001

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact CTR-001 \
  --expected-layers brd,prd,ears,bdd,adr,sys,req,impl \
  --strict
```

### Manual Checklist

- [ ] Both files created (.md and .yaml)
- [ ] Document Control in markdown file
- [ ] Contract Overview clear
- [ ] Business Context explains why (links to REQ)
- [ ] YAML contract valid (OpenAPI/JSON Schema)
- [ ] Usage Examples comprehensive
- [ ] Error handling documented
- [ ] Validation rules specified
- [ ] Version number semantic (Major.Minor.Patch)
- [ ] Cumulative tags: @brd through @req/impl (7-8 tags)
- [ ] Traceability matrix updated

## Common Pitfalls

1. **Single file only**: Must create BOTH .md and .yaml files
2. **Invalid YAML**: Must validate with yamllint and openapi-spec-validator
3. **Missing examples**: Usage Examples section critical for adoption
4. **Vague validation**: Schema validation must be precise and testable
5. **Missing cumulative tags**: Layer 9 must include all 7-8 upstream tags
6. **Skipping when needed**: Don't skip if multiple teams need shared contract

## Next Skill

After creating CTR (or skipping this optional layer), use:

**`doc-spec`** - Create Technical Specifications (Layer 10)

The SPEC will:
- Reference CTR (if created) or REQ as upstream source
- Include all 8-9 upstream tags
- Use YAML format
- Define implementation details
- Achieve 100% implementation-readiness

## Related Resources

- **CTR Creation Rules**: `ai_dev_flow/CTR/CTR_CREATION_RULES.md`
- **CTR Validation Rules**: `ai_dev_flow/CTR/CTR_VALIDATION_RULES.md`
- **CTR README**: `ai_dev_flow/CTR/README.md`
- **OpenAPI Specification**: https://spec.openapis.org/oas/v3.0.3
- **JSON Schema**: https://json-schema.org/
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**CTR Purpose**: Define API contracts and data schemas

**Layer**: 9 (Optional)

**Tags Required**: @brd through @req/impl (7-8 tags)

**Format**: Dual-file (.md + .yaml)

**YAML Standards**:
- OpenAPI 3.0 for REST APIs
- JSON Schema for data models
- AsyncAPI for event-driven (if applicable)

**Key Sections**:
- Contract Overview
- Business Context (link to REQ Section 3)
- YAML contract definition
- Usage Examples
- Validation Rules
- Error Handling

**Optional**: Skip this layer if contracts are simple or embedded in REQ

**Next**: doc-spec
