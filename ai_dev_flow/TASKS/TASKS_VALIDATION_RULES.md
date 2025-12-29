# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of TASKS-TEMPLATE.md
# - Authority: TASKS-TEMPLATE.md is the single source of truth for TASKS structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from TASKS_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to TASKS-TEMPLATE.md
# =============================================================================
---
title: "TASKS Validation Rules"
tags:
  - validation-rules
  - layer-11-artifact
  - shared-architecture
custom_fields:
  document_type: validation_rules
  artifact_type: TASKS
  layer: 11
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for TASKS documents.
> - Apply these rules after TASKS creation or modification
> - **Authority**: Validates compliance with `TASKS-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing TASKS changes

# TASKS Validation Rules

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

Rules for validating AI Tasks (TASKS) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

### Reserved ID Exemption (TASKS-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `TASKS-000_*.md`

**Document Types**:
- Index documents (`TASKS-000_index.md`)
- Traceability matrix templates (`TASKS-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Implementation contracts checklists (`TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md`)
- Glossaries, registries

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `TASKS-000_*` pattern.

---

## 1. Filename Validation

### Pattern

```regex
^TASKS-[0-9]{2,}_[a-z0-9_]+_tasks\.md$
```

### Rules

| Rule | Check | Error Level |
|------|-------|-------------|
| TASKS prefix | Must start with "TASKS-" | ERROR |
| ID format | NN or NNN digits | ERROR |
| Slug format | lowercase, underscores only | ERROR |
| _tasks suffix | Must end with "_tasks" | ERROR |
| Extension | .md only | ERROR |

### Examples

| Filename | Valid | Reason |
|----------|-------|--------|
| `TASKS-01_gateway_service_tasks.md` | ✅ | Correct format |
| `tasks-001_gateway_service_tasks.md` | ❌ | Lowercase prefix |
| `TASKS-1_gateway_service_tasks.md` | ❌ | Single digit ID |
| `TASKS-01_gateway_service.md` | ❌ | Missing _tasks suffix |
| `TASKS-01-gateway-service-tasks.md` | ❌ | Hyphens in slug |

---

## 2. Frontmatter Validation

### Required Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | Yes | Must match "TASKS-NN: [Name]" |
| tags | array | Yes | Must include layer-11-artifact |
| custom_fields.artifact_type | string | Yes | Must equal "TASKS" |
| custom_fields.layer | integer | Yes | Must equal 11 |
| custom_fields.parent_spec | string | Yes | SPEC-NN format |

### Validation Script

```bash
# Check frontmatter presence
if ! grep -q "^---" "$TASKS_FILE"; then
  echo "ERROR: Missing YAML frontmatter"
fi

# Check artifact type
if ! grep -q "artifact_type: TASKS" "$TASKS_FILE"; then
  echo "ERROR: artifact_type must be TASKS"
fi

# Check parent_spec
if ! grep -q "parent_spec: SPEC-" "$TASKS_FILE"; then
  echo "ERROR: Missing parent_spec field"
fi
```

---

## 3. Document Control Table Validation

### Required Fields

| Field | Required | Format |
|-------|----------|--------|
| TASKS ID | Yes | TASKS-NN |
| Title | Yes | Non-empty string |
| Status | Yes | Draft/Ready/In Progress/Completed |
| Version | Yes | X.Y.Z (semantic) |
| Created | Yes | YYYY-MM-DD |
| Author | Yes | Non-empty string |
| Parent SPEC | Yes | SPEC-NN |
| Complexity | Yes | 1-5 integer |

### Validation Rules

1. **TASKS ID** must match filename pattern
2. **Status** must be valid enum value
3. **Parent SPEC** must reference existing SPEC file
4. **Complexity** must be 1-5 integer

---

## 4. Section Structure Validation

### Required Sections

| Section | Required | Validation |
|---------|----------|------------|
| 1. Scope | Yes | Non-empty, has exclusions |
| 2. Plan | Yes | Numbered steps exist |
| 3. Constraints | Yes | At least 3 constraints |
| 4. Acceptance | Yes | Checkboxes present |
| 5. Dependencies | Yes | Upstream/downstream listed |
| 6. Traceability Tags | Yes | Valid tag format |
| 7. File Structure | Yes | Output files listed |
| 8. Implementation Contracts | Yes | ICON integration documented |

### Validation Commands

```bash
required_sections=(
  "## 1. Scope"
  "## 2. Plan"
  "## 3. Constraints"
  "## 4. Acceptance"
  "## 5. Dependencies"
  "## 6. Traceability"
  "## 7. File Structure"
  "## 8. Implementation Contracts"
)

for section in "${required_sections[@]}"; do
  if ! grep -q "$section" "$TASKS_FILE"; then
    echo "ERROR: Missing section: $section"
  fi
done
```

---

## 5. Scope Section Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| Non-empty content | ERROR |
| Contains boundary statement | WARNING |
| Contains exclusions | WARNING |

### Validation

```bash
# Check scope has content
scope_content=$(sed -n '/## 1. Scope/,/## 2. Plan/p' "$TASKS_FILE")
if [ -z "$scope_content" ]; then
  echo "ERROR: Scope section is empty"
fi

# Check for exclusions
if ! echo "$scope_content" | grep -qi "exclusion\|exclude\|not include"; then
  echo "WARNING: Scope should document exclusions"
fi
```

---

## 6. Plan Section Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| Numbered steps exist | ERROR |
| At least 3 steps | WARNING |
| SPEC references present | WARNING |
| Time estimates present | INFO |

### Validation

```bash
# Check numbered steps
step_count=$(grep -cE "^[0-9]+\." "$TASKS_FILE")
if [ "$step_count" -lt 1 ]; then
  echo "ERROR: No numbered steps in Plan section"
elif [ "$step_count" -lt 3 ]; then
  echo "WARNING: Plan has fewer than 3 steps"
fi

# Check SPEC references
if ! grep -qE "SPEC-[0-9]+:[0-9]+" "$TASKS_FILE"; then
  echo "WARNING: No SPEC line references found"
fi
```

---

## 7. Section 8 (Implementation Contracts) Validation

### CRITICAL: Mandatory Section

| Check | Error Level |
|-------|-------------|
| Section 8 exists | ERROR |
| Has 8.1, 8.2, or 8.3 subsection | ERROR |
| @icon tags if provider/consumer | ERROR |
| @icon-role tag if @icon present | WARNING |

### Validation Commands

```bash
# Section 8 MUST exist
if ! grep -q "## 8. Implementation Contracts" "$TASKS_FILE"; then
  echo "ERROR: Missing MANDATORY Section 8: Implementation Contracts"
  exit 1
fi

# Check for proper subsections
if ! grep -qE "### 8\.[123]" "$TASKS_FILE"; then
  echo "ERROR: Section 8 must have 8.1, 8.2, or 8.3 subsection"
fi

# If @icon tag present, @icon-role should also be present
if grep -q "@icon:" "$TASKS_FILE"; then
  if ! grep -q "@icon-role:" "$TASKS_FILE"; then
    echo "WARNING: @icon tag found but @icon-role missing"
  fi
fi
```

---

## 8. Traceability Tag Validation

### Required Tags (Layer 11)

| Tag | Required | Format |
|-----|----------|--------|
| @brd | Yes | BRD.NN.EE.SS |
| @prd | Yes | PRD.NN.EE.SS |
| @ears | Yes | EARS.NN.EE.SS |
| @bdd | Yes | BDD.NN.EE.SS |
| @adr | Yes | ADR-NN |
| @sys | Yes | SYS.NN.EE.SS |
| @req | Yes | REQ.NN.EE.SS |
| @spec | Yes | SPEC-NN |

### Optional Tags

| Tag | Required | Format |
|-----|----------|--------|
| @impl | Conditional | IMPL-NN (if project uses IMPL) |
| @ctr | Conditional | CTR-NN (if contracts defined) |
| @icon | Conditional | ICON-NN:ContractName |

### Validation Commands

```bash
required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec")

for tag in "${required_tags[@]}"; do
  if ! grep -q "^$tag:" "$TASKS_FILE"; then
    echo "ERROR: Missing required tag: $tag"
  fi
done

# Validate tag format
if grep -qE "@[a-z]+:\s*$" "$TASKS_FILE"; then
  echo "ERROR: Empty tag value found"
fi
```

---

## 9. Acceptance Criteria Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| Checkbox format present | ERROR |
| At least 3 criteria | WARNING |
| BDD reference present | WARNING |
| Coverage targets present | WARNING |

### Validation

```bash
# Check for checkboxes
checkbox_count=$(grep -c "^\s*- \[ \]" "$TASKS_FILE")
if [ "$checkbox_count" -lt 1 ]; then
  echo "ERROR: No acceptance criteria checkboxes found"
elif [ "$checkbox_count" -lt 3 ]; then
  echo "WARNING: Fewer than 3 acceptance criteria"
fi

# Check for BDD reference
if ! grep -qi "BDD-[0-9]" "$TASKS_FILE"; then
  echo "WARNING: No BDD scenario reference in acceptance criteria"
fi
```

---

## 10. Cross-Reference Validation

### Link Resolution

| Link Type | Validation | Error Level |
|-----------|------------|-------------|
| SPEC references | SPEC-NN file exists | ERROR |
| BDD references | BDD-NN file exists | WARNING |
| REQ references | REQ-NN file exists | WARNING |
| ICON references | ICON-NN file exists | ERROR |

### Validation Commands

```bash
# Validate SPEC reference
parent_spec=$(grep "parent_spec:" "$TASKS_FILE" | grep -oE "SPEC-[0-9]+")
if [ -n "$parent_spec" ]; then
  spec_file=$(find ../SPEC -name "${parent_spec}*.yaml" 2>/dev/null)
  if [ -z "$spec_file" ]; then
    echo "ERROR: Parent SPEC file not found: $parent_spec"
  fi
fi

# Validate ICON references
grep -oE "ICON-[0-9]+" "$TASKS_FILE" | while read -r icon_ref; do
  icon_file=$(find ../ICON -name "${icon_ref}*.md" 2>/dev/null)
  if [ -z "$icon_file" ]; then
    echo "ERROR: Referenced ICON file not found: $icon_ref"
  fi
done
```

---

## 11. Error Severity Levels

### Error Levels

| Level | Action Required | Examples |
|-------|-----------------|----------|
| ERROR | Must fix before merge | Missing sections, invalid format |
| WARNING | Should fix | Missing references, incomplete docs |
| INFO | Optional improvement | Style suggestions |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Errors found |
| 2 | Warnings only |

---

## 12. Validation Script Usage

### Command

```bash
./scripts/validate_tasks.sh <TASKS_FILE>
```

### Options

```bash
./scripts/validate_tasks.sh --help
./scripts/validate_tasks.sh --verbose TASKS-01.md
./scripts/validate_tasks.sh --strict TASKS-01.md  # Treat warnings as errors
```

### Output Format

```
=========================================
TASKS Validation Report
=========================================
File: TASKS-01_gateway_service_tasks.md
Version: 1.0.0

CHECK 1: Filename Format
  ✅ Filename format valid

CHECK 2: Frontmatter
  ✅ YAML frontmatter present
  ✅ Required fields present

CHECK 3: Required Sections
  ✅ All 8 required sections found

CHECK 4: Section 8 Implementation Contracts
  ✅ Section 8 exists
  ✅ Proper subsections present

CHECK 5: Traceability Tags
  ✅ All 8 required tags present
  ⚠️  WARNING: @impl tag missing (optional)

CHECK 6: Cross-References
  ✅ Parent SPEC exists
  ✅ All ICON references valid

=========================================
SUMMARY
=========================================
Errors: 0
Warnings: 1
Result: PASSED WITH WARNINGS
```

---

## 14. Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `TASKS.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `TASK-XXX` | ❌ Fail - use TASKS.NN.18.SS |
| Removed pattern | `T-XXX` | ❌ Fail - use TASKS.NN.18.SS |

**Regex**: `^###?\s+TASKS\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for TASKS**:
| Element Type | Code | Example |
|--------------|------|---------|
| Task | 18 | TASKS.02.18.01 |
| Task Item | 30 | TASKS.02.30.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `TASK-XXX` → Use `TASKS.NN.18.SS`
> - `T-XXX` → Use `TASKS.NN.18.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

**Fix**: Replace `### TASK-01: Implementation` with `### TASKS.02.18.01: Implementation`

---

## 15. Common Validation Errors

### Error: Missing Section 8

**Symptom**: "ERROR: Missing MANDATORY Section 8"
**Fix**: Add complete Section 8 with 8.1, 8.2, or 8.3 subsection

### Error: Invalid Parent SPEC

**Symptom**: "ERROR: Parent SPEC file not found"
**Fix**: Verify SPEC-NN exists in SPEC directory

### Error: Empty Traceability Tags

**Symptom**: "ERROR: Empty tag value found"
**Fix**: Add valid references after each tag colon

### Warning: Missing BDD Reference

**Symptom**: "WARNING: No BDD scenario reference"
**Fix**: Add BDD.NN.EE.SS to acceptance criteria

---

## References

- [TASKS_CREATION_RULES.md](./TASKS_CREATION_RULES.md) - Creation guidelines
- [TASKS-TEMPLATE.md](./TASKS-TEMPLATE.md) - Tasks template
- [validate_tasks.sh](../scripts/validate_tasks.sh) - Validation script
- [README.md](./README.md) - Directory overview

---

**Document Version**: 1.0.0
**Last Updated**: 2025-11-27
