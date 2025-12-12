# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of ICON-TEMPLATE.md
# - Authority: ICON-TEMPLATE.md is the single source of truth for ICON structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from ICON_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to ICON-TEMPLATE.md
# =============================================================================
---
title: "ICON Validation Rules"
tags:
  - validation-rules
  - layer-11-artifact
  - shared-architecture
custom_fields:
  document_type: validation_rules
  artifact_type: ICON
  layer: 11
  priority: shared
  development_status: active
---

# ICON Validation Rules

Rules for validating Implementation Contracts (ICON) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

### Reserved ID Exemption (ICON-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `ICON-000_*.md`

**Document Types**:
- Index documents (`ICON-000_index.md`)
- Traceability matrix templates (`ICON-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `ICON-000_*` pattern.

---

## 1. Filename Validation

### Pattern

```regex
^ICON-[0-9]{3,4}_[a-z0-9_]+\.md$
```

### Rules

| Rule | Check | Error Level |
|------|-------|-------------|
| ICON prefix | Must start with "ICON-" | ERROR |
| ID format | NNN or NNNN digits | ERROR |
| Slug format | lowercase, underscores only | ERROR |
| Extension | .md only | ERROR |

### Examples

| Filename | Valid | Reason |
|----------|-------|--------|
| `ICON-001_gateway_connector_protocol.md` | ✅ | Correct format |
| `icon-001_gateway_connector.md` | ❌ | Lowercase prefix |
| `ICON-1_gateway_connector.md` | ❌ | Single digit ID |
| `ICON-001-gateway-connector.md` | ❌ | Hyphens in slug |
| `ICON-001_gateway_connector.yaml` | ❌ | Wrong extension |

---

## 2. Frontmatter Validation

### Required Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | Yes | Must match "ICON-NNN: [Name]" |
| tags | array | Yes | Must include layer-11-artifact |
| custom_fields.artifact_type | string | Yes | Must equal "ICON" |
| custom_fields.layer | integer | Yes | Must equal 11 |
| custom_fields.contract_type | string | Yes | Valid enum value |
| custom_fields.provider_tasks | string | Yes | TASKS-NNN format |

### Contract Type Enum

Valid values for `contract_type`:
- `protocol`
- `exception`
- `state-machine`
- `data-model`
- `di-interface`

### Validation Script

```bash
# Check frontmatter presence
if ! grep -q "^---" "$ICON_FILE"; then
  echo "ERROR: Missing YAML frontmatter"
fi

# Check artifact type
if ! grep -q "artifact_type: ICON" "$ICON_FILE"; then
  echo "ERROR: artifact_type must be ICON"
fi

# Check contract_type
if ! grep -qE "contract_type: (protocol|exception|state-machine|data-model|di-interface)" "$ICON_FILE"; then
  echo "ERROR: Invalid or missing contract_type"
fi

# Check provider_tasks
if ! grep -q "provider_tasks: TASKS-" "$ICON_FILE"; then
  echo "ERROR: Missing provider_tasks field"
fi
```

---

## 3. Document Control Table Validation

### Required Fields

| Field | Required | Format |
|-------|----------|--------|
| Contract ID | Yes | ICON-NNN |
| Contract Name | Yes | Non-empty string |
| Version | Yes | X.Y.Z (semantic) |
| Status | Yes | Draft/Active/Deprecated |
| Created | Yes | YYYY-MM-DD |
| Last Updated | Yes | YYYY-MM-DD |
| Author | Yes | Non-empty string |
| Provider | Yes | TASKS-NNN reference |
| Consumers | Yes | List of TASKS-NNN or "None" |

### Validation Rules

1. **Contract ID** must match filename pattern
2. **Version** must follow semantic versioning
3. **Status** must be valid enum value
4. **Dates** must be valid ISO 8601 format
5. **Last Updated** >= Created date
6. **Provider** must reference valid TASKS file
7. **Consumers** must reference valid TASKS files (if any)

---

## 4. Section Structure Validation

### Required Sections

| Section | Required | Validation |
|---------|----------|------------|
| 1. Contract Overview | Yes | Non-empty, describes purpose |
| 2. Protocol/Interface Definition | Yes | Code block with type hints |
| 3. Provider Requirements | Yes | Implementation constraints |
| 4. Consumer Requirements | Yes | Usage requirements |
| 5. Type Definitions | Conditional | Required for data models |
| 6. Exception Hierarchy | Conditional | Required for exception contracts |
| 7. State Transitions | Conditional | Required for state machines |
| 8. Traceability Tags | Yes | Valid tag format |

### Validation Commands

```bash
required_sections=(
  "## 1. Contract Overview"
  "## 2. Protocol"
  "## 3. Provider Requirements"
  "## 4. Consumer Requirements"
  "## Traceability"
)

for section in "${required_sections[@]}"; do
  if ! grep -q "$section" "$ICON_FILE"; then
    echo "ERROR: Missing section: $section"
  fi
done
```

---

## 5. Protocol Definition Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| Python code block present | ERROR |
| typing.Protocol used | WARNING |
| Type hints on all methods | ERROR |
| Docstrings present | WARNING |
| @runtime_checkable decorator | WARNING |

### Validation

```bash
# Check for Python code block
if ! grep -q '```python' "$ICON_FILE"; then
  echo "ERROR: Missing Python code block"
fi

# Check for Protocol class
if ! grep -qi 'Protocol' "$ICON_FILE"; then
  echo "WARNING: No Protocol class definition found"
fi

# Check for type hints
if ! grep -qE '-> [A-Za-z\[\]]+:' "$ICON_FILE"; then
  echo "WARNING: No return type hints found"
fi
```

---

## 6. Provider/Consumer Validation

### CRITICAL: Bidirectional Reference Check

| Check | Error Level |
|-------|-------------|
| Exactly 1 provider | ERROR |
| Provider TASKS references this ICON | ERROR |
| Consumer TASKS reference this ICON | WARNING |
| No orphaned ICON (0 references) | ERROR |

### Validation Commands

```bash
# Get ICON ID from filename
ICON_ID=$(basename "$ICON_FILE" | grep -oE "ICON-[0-9]+")

# Check provider exists
provider=$(grep -oE "TASKS-[0-9]+" "$ICON_FILE" | head -1)
if [ -z "$provider" ]; then
  echo "ERROR: No provider TASKS referenced"
fi

# Verify provider references this ICON
if [ -n "$provider" ]; then
  tasks_file=$(find ../TASKS -name "${provider}*.md" 2>/dev/null | head -1)
  if [ -n "$tasks_file" ]; then
    if ! grep -q "@icon: $ICON_ID" "$tasks_file"; then
      echo "ERROR: Provider $provider does not reference $ICON_ID"
    fi
  fi
fi

# Count total references in TASKS directory
ref_count=$(grep -r "@icon: $ICON_ID" ../TASKS/ 2>/dev/null | wc -l)
if [ "$ref_count" -eq 0 ]; then
  echo "ERROR: Orphaned ICON - no TASKS references found"
fi
```

---

## 7. Role Validation

### Tag Format

| Tag Pattern | Description | Validation |
|-------------|-------------|------------|
| `@icon: ICON-NNN:ContractName` | Contract reference | Required in TASKS |
| `@icon-role: provider` | Implements contract | Exactly 1 per ICON |
| `@icon-role: consumer` | Uses contract | 0 or more per ICON |

### Validation Commands

```bash
ICON_ID=$(basename "$ICON_FILE" | grep -oE "ICON-[0-9]+")

# Count providers (must be exactly 1)
provider_count=$(grep -r "@icon-role: provider" ../TASKS/ | grep "$ICON_ID" | wc -l)
if [ "$provider_count" -ne 1 ]; then
  echo "ERROR: Expected 1 provider, found $provider_count"
fi

# Count consumers (informational)
consumer_count=$(grep -r "@icon-role: consumer" ../TASKS/ | grep "$ICON_ID" | wc -l)
echo "INFO: Found $consumer_count consumer(s)"
```

---

## 8. Traceability Tag Validation

### Required Tags (Layer 11)

| Tag | Required | Format |
|-----|----------|--------|
| @brd | Yes | BRD.NNN.NNN (sub-ID) or BRD-NNN (doc-level) |
| @prd | Yes | PRD.NNN.NNN (sub-ID) or PRD-NNN (doc-level) |
| @ears | Yes | EARS.NNN.NNN |
| @bdd | Yes | BDD.NNN.NNN (sub-ID) or BDD-NNN (doc-level) |
| @adr | Yes | ADR-NNN |
| @sys | Yes | SYS.NNN.NNN (sub-ID) or SYS-NNN (doc-level) |
| @req | Yes | REQ.NNN.NNN (sub-ID) or REQ-NNN (doc-level) |
| @spec | Yes | SPEC.NNN.NNN (sub-ID) or SPEC-NNN (doc-level) |

### Optional Tags

| Tag | Required | Format |
|-----|----------|--------|
| @impl | Conditional | IMPL-NNN (if project uses IMPL) |
| @ctr | Conditional | CTR-NNN (if contracts defined) |

### Validation Commands

```bash
required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec")

for tag in "${required_tags[@]}"; do
  if ! grep -q "^$tag:" "$ICON_FILE"; then
    echo "ERROR: Missing required tag: $tag"
  fi
done

# Validate tag format
if grep -qE "@[a-z]+:\s*$" "$ICON_FILE"; then
  echo "ERROR: Empty tag value found"
fi
```

---

## 9. Contract Type-Specific Validation

### Protocol Contracts

```bash
# Must have Protocol class
if grep -q "contract_type: protocol" "$ICON_FILE"; then
  if ! grep -qE "class [A-Z][A-Za-z]+\(Protocol\)" "$ICON_FILE"; then
    echo "ERROR: Protocol contract must define Protocol class"
  fi
fi
```

### Exception Contracts

```bash
# Must have Exception hierarchy
if grep -q "contract_type: exception" "$ICON_FILE"; then
  if ! grep -qE "class [A-Z][A-Za-z]+Exception" "$ICON_FILE"; then
    echo "ERROR: Exception contract must define Exception classes"
  fi
fi
```

### State Machine Contracts

```bash
# Must have Enum states
if grep -q "contract_type: state-machine" "$ICON_FILE"; then
  if ! grep -qE "class [A-Z][A-Za-z]+State.*Enum" "$ICON_FILE"; then
    echo "ERROR: State machine contract must define State Enum"
  fi
  if ! grep -qiE "transition|valid_transitions" "$ICON_FILE"; then
    echo "WARNING: State machine should document transitions"
  fi
fi
```

### Data Model Contracts

```bash
# Must have type definitions
if grep -q "contract_type: data-model" "$ICON_FILE"; then
  if ! grep -qE "(TypedDict|BaseModel|dataclass)" "$ICON_FILE"; then
    echo "ERROR: Data model contract must define typed structures"
  fi
fi
```

---

## 10. Cross-Reference Validation

### Link Resolution

| Link Type | Validation | Error Level |
|-----------|------------|-------------|
| TASKS references | File must exist | ERROR |
| SPEC references | File must exist | WARNING |
| REQ references | File must exist | WARNING |

### Validation Commands

```bash
# Validate TASKS references
grep -oE "TASKS-[0-9]+" "$ICON_FILE" | sort -u | while read -r tasks_ref; do
  tasks_file=$(find ../TASKS -name "${tasks_ref}*.md" 2>/dev/null | head -1)
  if [ -z "$tasks_file" ]; then
    echo "ERROR: Referenced TASKS file not found: $tasks_ref"
  fi
done

# Validate SPEC references
grep -oE "SPEC-[0-9]+" "$ICON_FILE" | sort -u | while read -r spec_ref; do
  spec_file=$(find ../SPEC -name "${spec_ref}*.yaml" 2>/dev/null | head -1)
  if [ -z "$spec_file" ]; then
    echo "WARNING: Referenced SPEC file not found: $spec_ref"
  fi
done
```

---

## 11. Creation Criteria Validation

### Standalone ICON Criteria Check

ICON should only be standalone if ALL criteria met:

| Criterion | Required | Validation |
|-----------|----------|------------|
| 5+ consumer TASKS | Yes | Count consumer references |
| >500 lines | Yes | Contract complexity check |
| Platform-level interface | Yes | Manual review |
| Cross-project usage | Yes | Manual review |

### Warning for Premature Standalone ICON

```bash
# Count consumers
ICON_ID=$(basename "$ICON_FILE" | grep -oE "ICON-[0-9]+")
consumer_count=$(grep -r "@icon-role: consumer" ../TASKS/ | grep "$ICON_ID" | wc -l)

if [ "$consumer_count" -lt 5 ]; then
  echo "WARNING: Standalone ICON with <5 consumers ($consumer_count found)"
  echo "  Consider embedding contract in TASKS file instead"
fi
```

---

## 12. Error Severity Levels

### Error Levels

| Level | Action Required | Examples |
|-------|-----------------|----------|
| ERROR | Must fix before merge | Missing sections, invalid format, orphaned ICON |
| WARNING | Should fix | Missing consumers, incomplete docs |
| INFO | Optional improvement | Style suggestions |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Errors found |
| 2 | Warnings only |

---

## 13. Validation Script Usage

### Command

```bash
./scripts/validate_icon.sh <ICON_FILE>
```

### Options

```bash
./scripts/validate_icon.sh --help
./scripts/validate_icon.sh --verbose ICON-001.md
./scripts/validate_icon.sh --strict ICON-001.md  # Treat warnings as errors
```

### Output Format

```
=========================================
ICON Validation Report
=========================================
File: ICON-001_gateway_connector_protocol.md
Version: 1.0.0

CHECK 1: Filename Format
  ✅ Filename format valid

CHECK 2: Frontmatter
  ✅ YAML frontmatter present
  ✅ Required fields present

CHECK 3: Required Sections
  ✅ All required sections found

CHECK 4: Protocol Definition
  ✅ Protocol class present
  ✅ Type hints present

CHECK 5: Provider/Consumer
  ✅ Exactly 1 provider found
  ✅ Provider references this ICON
  ⚠️  WARNING: Only 2 consumers (recommend 5+ for standalone)

CHECK 6: Traceability Tags
  ✅ All 8 required tags present

CHECK 7: Cross-References
  ✅ All TASKS references valid
  ✅ All SPEC references valid

=========================================
SUMMARY
=========================================
Errors: 0
Warnings: 1
Result: PASSED WITH WARNINGS
```

---

## 14. Common Validation Errors

### Error: Orphaned ICON

**Symptom**: "ERROR: Orphaned ICON - no TASKS references found"
**Fix**: Update provider TASKS with @icon tag or delete standalone ICON and embed in TASKS

### Error: Multiple Providers

**Symptom**: "ERROR: Expected 1 provider, found 2"
**Fix**: Each ICON must have exactly one provider. Remove duplicate @icon-role: provider tags

### Error: Missing Protocol Class

**Symptom**: "ERROR: Protocol contract must define Protocol class"
**Fix**: Add typing.Protocol class definition with method signatures

### Warning: Few Consumers

**Symptom**: "WARNING: Standalone ICON with <5 consumers"
**Fix**: Consider embedding contract in TASKS file if not truly cross-project

### Error: Empty Traceability Tags

**Symptom**: "ERROR: Empty tag value found"
**Fix**: Add valid references after each tag colon

---

## References

- [ICON_CREATION_RULES.md](./ICON_CREATION_RULES.md) - Creation guidelines
- [ICON-TEMPLATE.md](./ICON-TEMPLATE.md) - Contract template
- [ICON-000_index.md](./ICON-000_index.md) - Contract registry
- [validate_icon.sh](../scripts/validate_icon.sh) - Validation script
- [README.md](./README.md) - Directory overview
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md) - Contracts guide

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27
