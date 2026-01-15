# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of CTR-TEMPLATE.md
# - Authority: CTR-TEMPLATE.md is the single source of truth for CTR structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to CTR-TEMPLATE.md
# =============================================================================
---
title: "CTR Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: CTR
  layer: 9
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is a **CREATION HELPER** for CTR-TEMPLATE.md.
> - **Authority**: `CTR-TEMPLATE.md` is the source of truth for CTR structure; YAML schemas must follow OpenAPI 3.x
> - **Validation**: Use `CTR_VALIDATION_RULES.md` after CTR creation/changes

# CTR Creation Rules

## Index-Only Generation Workflow

- Maintain `CTR-00_index.md` as the authoritative source of planned and active CTR files (mark planned items with Status: Planned).
- Generators use: `CTR-00_index.md` + selected template profile (MVP by default; full when explicitly requested in settings or prompt).

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

Rules for creating Data Contracts (CTR) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

---

## Table of Contents

1. [When to Create a CTR Document](#1-when-to-create-a-ctr-document)
2. [File Naming Convention](#2-file-naming-convention)
3. [Required Sections (Markdown)](#3-required-sections-markdown)
4. [Required Sections (YAML)](#4-required-sections-yaml)
5. [Traceability Requirements](#5-traceability-requirements)
6. [Quality Checklist](#6-quality-checklist)
7. [Common Anti-Patterns](#7-common-anti-patterns)
8. [Validation](#8-validation)
9. [Upstream Artifact Verification Process](#9-upstream-artifact-verification-process)
10. [Cross-Document Validation](#10-cross-document-validation-mandatory)

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
CTR-NN_{descriptive_slug}.md
CTR-NN_{descriptive_slug}.yaml
```

### Rules

1. **CTR-NN**: Sequential numbering starting from 001
2. **descriptive_slug**: Lowercase with underscores
3. **Extension**: `.md` for documentation, `.yaml` for schema
4. **Dual-file**: Create both `.md` and `.yaml` for complete contracts

### Examples

- `CTR-01_user_authentication_api.md`
- `CTR-01_user_authentication_api.yaml`
- `CTR-02_market_data_feed.md`
- `CTR-03_order_execution_service.md`

### 2.1 Element ID Format (MANDATORY)

**Pattern**: `CTR.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Interface | 16 | CTR.02.16.01 |
| Data Model | 17 | CTR.02.17.01 |
| Contract Clause | 20 | CTR.02.20.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `INT-XXX` → Use `CTR.NN.16.SS`
> - `MODEL-XXX` → Use `CTR.NN.17.SS`
> - `CLAUSE-XXX` → Use `CTR.NN.20.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 3. Required Sections (Markdown)

### 3.1 Frontmatter

```yaml
---
title: "CTR-NN: [Contract Name]"
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
| Contract ID | Yes | CTR-NN format |
| Title | Yes | Descriptive contract name |
| Version | Yes | Semantic version (X.Y.Z) |
| Status | Yes | Draft/Active/Deprecated |
| Created | Yes | YYYY-MM-DD |
| Last Updated | Yes | YYYY-MM-DD |
| Author | Yes | Creator name |
| Consumers | Yes | List of consuming systems |
| Providers | Yes | List of providing systems |

### 3.3 Mandatory Sections (12-Section Structure)

1. **Document Control** - Contract metadata, status, version (absorbs old Status section)
2. **Context** - Business problem, contract scope, trade-offs (absorbs old Consequences section)
3. **Contract Definition** - Format, naming conventions, thresholds
4. **Requirements Satisfied** - Upstream requirements this contract addresses
5. **Interface Definition** - Schema reference, endpoints, data models (absorbs old Schema Reference section)
6. **Error Handling** - Error codes and response formats
7. **Quality Attributes** - Performance, security, reliability, observability (absorbs old Monitoring section)
8. **Versioning Strategy** - Version policy, backwards compatibility
9. **Examples** - Request/response examples
10. **Verification** - Contract testing, BDD scenarios, validation criteria (absorbs old Impact Analysis section)
11. **Traceability** - Upstream/downstream artifacts, related contracts, tags (absorbs old Related Contracts section)
12. **References** - Internal/external links, additional context

**Optional Appendices**:
- **Appendix A**: Alternatives Considered
- **Appendix B**: Implementation Notes

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
- `@req: REQ.NN.EE.SS` - Atomic requirements (unified format)
- `@spec: SPEC-NN` - Technical specifications
- `@adr: ADR-NN` - Architecture decisions

### 5.2 Downstream References

CTR is referenced by:
- `@tasks: TASKS.NN.EE.SS` - Implementation tasks
- `@iplan: IPLAN-NN` - Implementation plans
- Code implementations

### 5.3 Tag Format

```markdown
## Traceability Tags

@req: REQ.01.26.01, REQ.02.26.01
@adr: ADR-03
@spec: SPEC-01
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
- [ ] Update CTR-00_index.md
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
./scripts/validate_ctr.sh /path/to/CTR-NN_name.md
```

### Manual Checklist

- [ ] Filename follows convention
- [ ] All required sections present
- [ ] YAML validates against OpenAPI schema
- [ ] Traceability tags complete
- [ ] Registered in CTR-00_index.md

---

## 9. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/01_BRD/    # Layer 1
ls -la docs/02_PRD/    # Layer 2
ls -la docs/03_EARS/   # Layer 3
ls -la docs/04_BDD/    # Layer 4
ls -la docs/05_ADR/    # Layer 5
ls -la docs/06_SYS/    # Layer 6
ls -la docs/07_REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-01 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-01 or null | Reference/Create/Skip |
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

### Same-Type References (Conditional)

Include ONLY if relationships exist between CTR documents sharing API context or dependencies.

| Relationship | Document ID | Document Title | Purpose |
|--------------|-------------|----------------|---------|
| Related | CTR-NN | [Related CTR title] | Shared API context |
| Depends | CTR-NN | [Prerequisite CTR title] | Must complete before this |

**Tags**:
```markdown
@related-ctr: CTR-NN
@depends-ctr: CTR-NN
```


## References

- [CTR-TEMPLATE.md](./CTR-TEMPLATE.md) - Contract template (primary standard)
- [CTR_SCHEMA.yaml](./CTR_SCHEMA.yaml) - Validation schema (OpenAPI 3.x format)
- [CTR-00_index.md](./CTR-00_index.md) - Contract registry
- [README.md](./README.md) - Directory overview
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Workflow guide

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27

---

## 10. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any CTR document. Do NOT proceed to downstream artifacts until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/09_CTR/CTR-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all CTR documents complete
python scripts/validate_cross_document.py --layer CTR --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| CTR (Layer 9) | @brd through @req (+ optional @impl) | 7-8 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd through @req tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to SPEC creation until Phase 1 validation passes with 0 errors.
