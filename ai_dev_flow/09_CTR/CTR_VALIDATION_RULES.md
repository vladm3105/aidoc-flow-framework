---
title: "CTR Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: CTR
  layer: 9
  priority: shared
  development_status: active
---

# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of CTR-TEMPLATE.md
# - Authority: CTR-TEMPLATE.md is the single source of truth for CTR structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from CTR_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to CTR-TEMPLATE.md
# =============================================================================
---
title: "CTR Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - shared-architecture
custom_fields:
  document_type: validation_rules
  artifact_type: CTR
  layer: 9
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for CTR documents.
> - Apply these rules after CTR creation or modification
> - **Authority**: Validates compliance with `CTR-TEMPLATE.md` (the primary standard) and OpenAPI 3.x for YAML schemas
> - **Scope**: Use for quality gates before committing CTR changes

# CTR Validation Rules

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

Rules for validating Data Contracts (CTR) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

### Reserved ID Exemption (CTR-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `CTR-00_*.md` or `CTR-00_*.yaml`

**Document Types**:
- Index documents (`CTR-00_index.md`)
- Traceability matrix templates (`CTR-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `CTR-00_*` pattern.

---

## 1. Filename Validation

### Pattern

```regex
^CTR-[0-9]{2,}(_[a-z0-9_]+)?\.(md|yaml)$
```

### Rules

| Rule | Check | Error Level |
|------|-------|-------------|
| CTR prefix | Must start with "CTR-" | ERROR |
| ID format | NN or NNN digits | ERROR |
| Slug format | lowercase, underscores only | ERROR |
| Extension | .md or .yaml | ERROR |
| Dual files | Both .md and .yaml should exist | WARNING |

### Examples

| Filename | Valid | Reason |
|----------|-------|--------|
| `CTR-01_user_api.md` | ✅ | Correct format |
| `CTR-01_user_api.yaml` | ✅ | Correct format |
| `ctr-001_user_api.md` | ❌ | Lowercase prefix |
| `CTR-1_user_api.md` | ❌ | Single digit ID |
| `CTR-01-user-api.md` | ❌ | Hyphens in slug |

---

## 2. Frontmatter Validation

### Required Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | Yes | Must match "CTR-NN: [Name]" |
| tags | array | Yes | Must include layer-9-artifact |
| custom_fields.artifact_type | string | Yes | Must equal "CTR" |
| custom_fields.layer | integer | Yes | Must equal 9 |
| custom_fields.contract_version | string | Yes | Semantic version format |

### Validation Script

```bash
# Check frontmatter presence
if ! grep -q "^---" "$CTR_FILE"; then
  echo "ERROR: Missing YAML frontmatter"
fi

# Check artifact type
if ! grep -q "artifact_type: CTR" "$CTR_FILE"; then
  echo "ERROR: artifact_type must be CTR"
fi
```

---

## 3. Document Control Table Validation

### Required Fields

| Field | Required | Format |
|-------|----------|--------|
| Contract ID | Yes | CTR-NN |
| Title | Yes | Non-empty string |
| Version | Yes | X.Y.Z (semantic) |
| Status | Yes | Draft/Active/Deprecated |
| Created | Yes | YYYY-MM-DD |
| Last Updated | Yes | YYYY-MM-DD |
| Author | Yes | Non-empty string |
| Consumers | Yes | List or "None" |
| Providers | Yes | List or "None" |

### Validation Rules

1. **Contract ID** must match filename pattern
2. **Version** must follow semantic versioning
3. **Status** must be valid enum value
4. **Dates** must be valid ISO 8601 format
5. **Last Updated** >= Created date

---

## 4. Section Structure Validation (12-Section Format)

### Required Sections (Markdown)

| Section | Required | Validation | Notes |
|---------|----------|------------|-------|
| 1. Document Control | Yes | Contract ID, version, status defined | Absorbs old Status section |
| 2. Context | Yes | Business problem documented | Absorbs old Consequences/Trade-offs |
| 3. Contract Definition | Yes | Format, naming conventions | - |
| 4. Requirements Satisfied | Yes | Upstream requirements linked | - |
| 5. Interface Definition | Yes | At least one endpoint/schema | Absorbs old Schema Reference |
| 6. Error Handling | Yes | Error codes documented | - |
| 7. Quality Attributes | Yes | Performance, security defined | Absorbs old Monitoring section |
| 8. Versioning Strategy | Yes | Strategy documented | - |
| 9. Examples | Yes | At least one request/response | - |
| 10. Verification | Yes | Testing criteria defined | Absorbs old Impact Analysis |
| 11. Traceability | Yes | Valid tag format | Absorbs old Related Contracts |
| 12. References | Yes | Internal/external links | - |

**Optional Appendices**: Appendix A (Alternatives Considered), Appendix B (Implementation Notes)

### Validation Commands

```bash
# Check required sections (12-section structure)
required_sections=(
  "## 1. Document Control"
  "## 2. Context"
  "## 3. Contract Definition"
  "## 4. Requirements Satisfied"
  "## 5. Interface Definition"
  "## 6. Error Handling"
  "## 7. Quality Attributes"
  "## 8. Versioning Strategy"
  "## 9. Examples"
  "## 10. Verification"
  "## 11. Traceability"
  "## 12. References"
)

for section in "${required_sections[@]}"; do
  if ! grep -q "$section" "$CTR_FILE"; then
    echo "ERROR: Missing section: $section"
  fi
done
```

---

## 5. YAML Schema Validation

### OpenAPI Requirements

| Component | Required | Validation |
|-----------|----------|------------|
| openapi | Yes | Must be "3.0.x" or "3.1.x" |
| info.title | Yes | Must match .md title |
| info.version | Yes | Must match contract version |
| paths | Yes | At least one path |
| components.schemas | Conditional | If data models exist |

### Validation Commands

```bash
# Validate OpenAPI schema
openapi-generator-cli validate -i "$CTR_YAML_FILE"

# Check version consistency
md_version=$(grep "Version" "$CTR_MD_FILE" | head -1)
yaml_version=$(grep "version:" "$CTR_YAML_FILE" | head -1)
```

---

## 6. Traceability Tag Validation

### Required Tags

| Tag | Required | Format |
|-----|----------|--------|
| @req | Yes | REQ.NN.EE.SS (unified format) |
| @adr | Conditional | ADR-NN (if architecture decisions exist) |
| @spec | Conditional | SPEC-NN (if specifications exist) |

### Tag Format Rules

```markdown
# Correct formats
@req: REQ.01.26.01, REQ.02.26.01
@adr: ADR-03
@spec: SPEC-01

# Incorrect formats
@req: REQ-01         # Old format (use unified REQ.NN.EE.SS)
@req: REQ001          # Missing separators
@req REQ.01.26.01     # Missing colon
@requirement: REQ-01 # Wrong tag name
```

### Validation Commands

```bash
# Check for required @req tag
if ! grep -qE "^@req:" "$CTR_FILE"; then
  echo "ERROR: Missing @req traceability tag"
fi

# Validate tag format
if grep -qE "@req:\s*$" "$CTR_FILE"; then
  echo "ERROR: @req tag has no references"
fi
```

---

## 7. Cross-Reference Validation

### Link Resolution

| Link Type | Validation | Error Level |
|-----------|------------|-------------|
| Internal links | File must exist | ERROR |
| Anchor links | Anchor must exist | WARNING |
| External URLs | HTTP 200 response | WARNING |

### Validation Commands

```bash
# Extract and validate internal links
grep -oE '\[.*?\]\([^)]+\)' "$CTR_FILE" | while read -r link; do
  path=$(echo "$link" | sed -E 's/.*\(([^)]+)\).*/\1/')

  # Skip external URLs
  if [[ "$path" =~ ^https?:// ]]; then
    continue
  fi

  # Check file exists
  resolved_path="$(dirname "$CTR_FILE")/$path"
  if [ ! -f "$resolved_path" ]; then
    echo "ERROR: Broken link: $path"
  fi
done
```

---

## 8. Consumer/Provider Validation

### Rules

1. **At least one consumer** - Contract must have consumers
2. **At least one provider** - Contract must have providers
3. **Valid references** - Referenced systems must exist
4. **Bidirectional links** - Consumers should reference this contract

### Validation Commands

```bash
# Check consumers exist
if grep -q "| \*\*Consumers\*\* | None |" "$CTR_FILE"; then
  echo "WARNING: No consumers defined"
fi

# Check providers exist
if grep -q "| \*\*Providers\*\* | None |" "$CTR_FILE"; then
  echo "WARNING: No providers defined"
fi
```

---

## 9. Versioning Validation

### Semantic Version Rules

| Change Type | Version Bump | Description |
|-------------|--------------|-------------|
| Breaking | Major (X.0.0) | Incompatible API changes |
| Feature | Minor (0.X.0) | Backwards-compatible additions |
| Fix | Patch (0.0.X) | Backwards-compatible fixes |

### Validation

```bash
# Extract version
version=$(grep -oE "[0-9]+\.[0-9]+\.[0-9]+" "$CTR_FILE" | head -1)

# Validate format
if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: Invalid semantic version format: $version"
fi
```

---

## 10. Error Severity Levels

### Error Levels

| Level | Action Required | Examples |
|-------|-----------------|----------|
| ERROR | Must fix before merge | Missing sections, invalid format |
| WARNING | Should fix | Missing consumers, incomplete docs |
| INFO | Optional improvement | Style suggestions |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Errors found |
| 2 | Warnings only |

---

## 11. Validation Script Usage

### Command

```bash
./scripts/validate_ctr.sh <CTR_FILE>
```

### Options

```bash
./scripts/validate_ctr.sh --help
./scripts/validate_ctr.sh --verbose CTR-01_api.md
./scripts/validate_ctr.sh --strict CTR-01_api.md  # Treat warnings as errors
```

### Output Format

```
=========================================
CTR Validation Report
=========================================
File: CTR-01_user_api.md
Version: 1.0.0

CHECK 1: Filename Format
  ✅ Filename format valid

CHECK 2: Frontmatter
  ✅ YAML frontmatter present
  ✅ Required fields present

CHECK 3: Required Sections
  ✅ All 12 required sections found

CHECK 4: YAML Schema (if .yaml exists)
  ✅ OpenAPI schema valid

CHECK 5: Traceability Tags
  ✅ @req tag present
  ⚠️  WARNING: @adr tag missing

=========================================
SUMMARY
=========================================
Errors: 0
Warnings: 1
Result: PASSED WITH WARNINGS
```

---

## 13. Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `CTR.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `IF-XXX` | ❌ Fail - use CTR.NN.16.SS |
| Removed pattern | `DM-XXX` | ❌ Fail - use CTR.NN.17.SS |
| Removed pattern | `CC-XXX` | ❌ Fail - use CTR.NN.20.SS |

**Regex**: `^###?\s+CTR\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for CTR**:
| Element Type | Code | Example |
|--------------|------|---------|
| Interface | 16 | CTR.02.16.01 |
| Data Model | 17 | CTR.02.17.01 |
| Contract Clause | 20 | CTR.02.20.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `IF-XXX` → Use `CTR.NN.16.SS`
> - `DM-XXX` → Use `CTR.NN.17.SS`
> - `CC-XXX` → Use `CTR.NN.20.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

**Fix**: Replace `### IF-01: Interface` with `### CTR.02.16.01: Interface`

---

## 14. Common Validation Errors

### Error: Missing @req Tag

**Symptom**: Validation fails on traceability check
**Fix**: Add `@req: REQ.NN.EE.SS` tag with valid requirement references (unified format)

### Error: Version Mismatch

**Symptom**: .md and .yaml versions differ
**Fix**: Ensure both files have identical version numbers

### Error: Broken Internal Links

**Symptom**: Referenced files not found
**Fix**: Verify file paths are correct relative to CTR location

### Warning: No Consumers Defined

**Symptom**: Consumers field is empty or "None"
**Fix**: Identify and list systems that consume this contract

---

## References

- [CTR_CREATION_RULES.md](./CTR_CREATION_RULES.md) - Creation guidelines
- [CTR-TEMPLATE.md](./CTR-TEMPLATE.md) - Contract template (primary standard)
- [CTR_SCHEMA.yaml](./CTR_SCHEMA.yaml) - Validation schema (OpenAPI 3.x format)
- [validate_ctr.sh](../scripts/validate_ctr.sh) - Validation script
- [README.md](./README.md) - Directory overview

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27
