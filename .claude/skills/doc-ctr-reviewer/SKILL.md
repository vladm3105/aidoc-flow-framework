---
name: doc-ctr-reviewer
description: Comprehensive content review and quality assurance for CTR documents - validates contract completeness, dual-file consistency, OpenAPI compliance, and identifies issues requiring manual attention
tags:
  - sdd-workflow
  - quality-assurance
  - ctr-review
  - layer-8-artifact
  - shared-architecture
custom_fields:
  layer: 8
  artifact_type: CTR
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [CTR]
  downstream_artifacts: []
  version: "1.1"
  last_updated: "2026-02-10"
---

# doc-ctr-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Data Contract (CTR) documents. This skill performs deep content analysis beyond structural validation, checking contract completeness, dual-file consistency (MD + YAML), OpenAPI compliance, REQ alignment, and identifying issues that require manual review.

**Layer**: 8 (CTR Quality Assurance)

**Upstream**: CTR (from `doc-ctr-autopilot` or `doc-ctr`)

**Downstream**: None (final QA gate before SPEC generation)

---

## When to Use This Skill

Use `doc-ctr-reviewer` when:

- **After CTR Generation**: Run immediately after `doc-ctr-autopilot` completes
- **Manual CTR Edits**: After making manual changes to CTR
- **Pre-SPEC Check**: Before running `doc-spec-autopilot`
- **API Changes**: When external APIs are modified
- **Periodic Review**: Regular quality checks on existing CTRs

**Do NOT use when**:
- CTR does not exist yet (use `doc-ctr` or `doc-ctr-autopilot` first)
- Need structural/schema validation only (use `doc-ctr-validator`)
- Generating new CTR content (use `doc-ctr`)

---

## Skill vs Validator: Key Differences

| Aspect | `doc-ctr-validator` | `doc-ctr-reviewer` |
|--------|---------------------|-------------------|
| **Focus** | Schema compliance, SPEC-Ready score | Content quality, API consistency |
| **Checks** | Required sections, OpenAPI schema | Dual-file sync, endpoint coverage |
| **Auto-Fix** | Structural issues only | Content issues (sync, formatting) |
| **Output** | SPEC-Ready score (numeric) | Review score + issue list |
| **Phase** | Phase 4 (Validation) | Phase 5 (Final Review) |
| **Blocking** | SPEC-Ready < threshold blocks | Review score < threshold flags |

---

## Review Checks

### 1. Dual-File Consistency

Validates MD and YAML files are synchronized.

**Scope**:
- Endpoint definitions match
- Schema definitions aligned
- Version numbers consistent
- Descriptions synchronized

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-DF001 | Error | Endpoint in YAML not in MD |
| REV-DF002 | Error | Schema mismatch between files |
| REV-DF003 | Warning | Version number inconsistent |
| REV-DF004 | Info | Description differs (may be intentional) |

---

### 2. OpenAPI Compliance

Validates YAML follows OpenAPI 3.x specification.

**Scope**:
- Valid OpenAPI version
- Required fields present
- Schema types correct
- Response codes documented

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-OA001 | Error | Invalid OpenAPI version |
| REV-OA002 | Error | Required OpenAPI field missing |
| REV-OA003 | Error | Invalid schema type |
| REV-OA004 | Warning | Response code not documented |
| REV-OA005 | Info | Example values missing |

---

### 3. REQ Alignment

Validates CTR traces to REQ requirements.

**Scope**:
- Every endpoint maps to REQ
- External API requirements covered
- Interface contracts complete

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-RA001 | Error | Endpoint without REQ source |
| REV-RA002 | Warning | REQ interface not in CTR |
| REV-RA003 | Info | Multiple CTRs from single REQ (acceptable) |

---

### 4. Endpoint Coverage

Validates all expected endpoints documented.

**Scope**:
- CRUD operations complete
- Error endpoints defined
- Health check endpoints present
- Versioning strategy documented

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-EC001 | Warning | Missing CRUD operation |
| REV-EC002 | Warning | No error endpoint defined |
| REV-EC003 | Info | Health check endpoint missing |
| REV-EC004 | Info | API versioning not documented |

---

### 5. Security Definition

Validates security schemes documented.

**Scope**:
- Authentication method defined
- Authorization scopes documented
- Security schemes in OpenAPI
- Rate limiting documented

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-SD001 | Error | No security scheme defined |
| REV-SD002 | Warning | Authorization scopes missing |
| REV-SD003 | Warning | Rate limiting not documented |
| REV-SD004 | Info | Security examples missing |

---

### 6. Placeholder Detection

Identifies incomplete content requiring replacement.

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-P001 | Error | [TODO] placeholder found |
| REV-P002 | Error | [TBD] placeholder found |
| REV-P003 | Warning | Template value not replaced |

---

### 7. Naming Compliance

Validates element IDs follow `doc-naming` standards.

**Scope**:
- Element IDs use `CTR.NN.TT.SS` format
- Element type codes valid for CTR (28, 29)
- Contract naming convention

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-N001 | Error | Invalid element ID format |
| REV-N002 | Error | Element type code not valid for CTR |
| REV-N003 | Error | Legacy pattern detected |

---

## Review Score Calculation

**Scoring Formula**:

| Category | Weight | Calculation |
|----------|--------|-------------|
| Dual-File Consistency | 25% | (consistent_elements / total) × 25 |
| OpenAPI Compliance | 20% | (valid_fields / required_fields) × 20 |
| REQ Alignment | 15% | (aligned_endpoints / total) × 15 |
| Endpoint Coverage | 15% | (covered / expected) × 15 |
| Security Definition | 10% | (security_score) × 10 |
| Placeholder Detection | 5% | (no_placeholders ? 5 : 5 - count) |
| Naming Compliance | 10% | (valid_ids / total_ids) × 10 |

**Total**: Sum of all categories (max 100)

**Thresholds**:
- **PASS**: ≥ 90
- **WARNING**: 80-89
- **FAIL**: < 80

---

## Command Usage

```bash
# Review specific CTR
/doc-ctr-reviewer CTR-03-001

# Review CTR by path
/doc-ctr-reviewer docs/08_CTR/CTR-03-001_provider_api/

# Review all CTRs
/doc-ctr-reviewer all
```

---

## Output Report

Review reports are stored alongside the reviewed document per project standards.

**File Naming**: `CTR-NN-SSS.R_review_report_vNNN.md`

**Location**: Same folder as the reviewed CTR document.

### Versioning Rules

1. **First Review**: Creates `CTR-NN-SSS.R_review_report_v001.md`
2. **Subsequent Reviews**: Auto-increments version (v002, v003, etc.)
3. **Same-Day Reviews**: Each review gets unique version number

**Version Detection**: Scans folder for existing `CTR-NN-SSS.R_review_report_v*.md` files and increments.

**Example**:

```
docs/08_CTR/CTR-03-001_provider_api/
├── CTR-03-001.md
├── CTR-03-001.yaml
├── CTR-03-001.R_review_report_v001.md    # First review
└── CTR-03-001.R_review_report_v002.md    # After fixes
```

### Delta Reporting

When previous reviews exist, include score comparison in the report.

See `REVIEW_DOCUMENT_STANDARDS.md` for complete versioning requirements.

---

## Integration with doc-ctr-autopilot

This skill is invoked during Phase 5 of `doc-ctr-autopilot`:

```mermaid
flowchart LR
    A[Phase 4: Validation] --> B[Phase 5: Final Review]
    B --> C{doc-ctr-reviewer}
    C --> D[Phase 6: Continue]
```

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-naming` | Naming standards for Check #7 |
| `doc-ctr-autopilot` | Invokes this skill in Phase 5 |
| `doc-ctr-validator` | Structural validation (Phase 4) |
| `doc-ctr` | CTR creation rules |
| `doc-req-reviewer` | Upstream QA |
| `doc-spec-autopilot` | Downstream consumer |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-02-10 | Added review versioning support (_vNNN pattern); Delta reporting for score comparison |
| 1.0 | 2026-02-10 | Initial skill creation with 7 review checks; Dual-file consistency; OpenAPI compliance; Security definition |
