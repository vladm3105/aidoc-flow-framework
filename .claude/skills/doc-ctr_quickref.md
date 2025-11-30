# doc-ctr - Quick Reference

**Skill ID:** doc-ctr
**Layer:** 9 (Data Contracts) - **OPTIONAL**
**Purpose:** Define API contracts and data schemas using dual-file format

## Quick Start

```bash
# Invoke skill
skill: "doc-ctr"

# Common requests
- "Create API contract from REQ-001"
- "Document data validation contract"
- "Generate Layer 9 OpenAPI specification"
```

## What This Skill Does

1. Define API contracts in OpenAPI 3.0 format
2. Create data schemas in JSON Schema format
3. Provide usage examples (request/response)
4. Document validation rules and error handling
5. Apply semantic versioning (Major.Minor.Patch)

## Output Location (Dual-File Format)

```
ai_dev_flow/CTR/CTR-NNN_{slug}.md    # Documentation
ai_dev_flow/CTR/CTR-NNN_{slug}.yaml  # Contract definition
```

## YAML Formats

**OpenAPI 3.0** (for REST APIs):
```yaml
openapi: 3.0.3
info:
  title: Data Validation API
  version: 1.0.0
paths:
  /api/v1/data/validate:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DataRequest'
```

**JSON Schema** (for data models):
```yaml
$schema: "http://json-schema.org/draft-07/schema#"
type: object
properties:
  field_name:
    type: string
```

## Upstream/Downstream

```
BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL → CTR → SPEC
```

## Quick Validation

- [ ] Both files created (.md AND .yaml)
- [ ] YAML contract valid (OpenAPI/JSON Schema)
- [ ] Usage examples comprehensive
- [ ] Error handling documented
- [ ] Validation rules specified
- [ ] Version number semantic (Major.Minor.Patch)
- [ ] Cumulative tags: @brd through @req/impl (7-8 tags)

## Template Location

```
ai_dev_flow/CTR/CTR-TEMPLATE.md
ai_dev_flow/CTR/CTR-TEMPLATE.yaml
```

## Related Skills

- `doc-req` - Atomic requirements (upstream)
- `doc-impl` - Implementation approach (upstream, optional)
- `doc-spec` - Technical specifications (downstream)

## Note

**This layer is OPTIONAL** - Skip if contracts are simple or embedded in REQ Section 3
