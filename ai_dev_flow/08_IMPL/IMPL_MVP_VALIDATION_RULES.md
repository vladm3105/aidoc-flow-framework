---
title: "IMPL Validation Rules"
tags:
  - validation-rules
  - layer-8-artifact
  - shared-architecture
custom_fields:
  document_type: validation-rules
  artifact_type: IMPL
  layer: 8
  priority: shared
  development_status: active
---

# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of IMPL-TEMPLATE.md
# - Authority: IMPL-TEMPLATE.md is the single source of truth for IMPL structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from IMPL_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to IMPL-TEMPLATE.md
# =============================================================================
---
title: "IMPL Validation Rules"
tags:
  - validation-rules
  - layer-8-artifact
  - shared-architecture
custom_fields:
  document_type: validation_rules
  artifact_type: IMPL
  layer: 8
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for IMPL documents.
> - Apply these rules after IMPL creation or modification
> - **Authority**: Validates compliance with `IMPL-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing IMPL changes

# IMPL Validation Rules

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. See README → "Using This Repo" for path mapping.

Rules for validating Implementation Plans (IMPL) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-27 |
| **Status** | Active |

### Reserved ID Exemption (IMPL-00_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `IMPL-00_*.md`

**Document Types**:
- Index documents (`IMPL-00_index.md`)
- Traceability matrix templates (`IMPL-00_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `IMPL-00_*` pattern.

---

## 1. Filename Validation

### Pattern

```regex
^IMPL-[0-9]{2,}_[a-z0-9_]+\.md$
```

### Rules

| Rule | Check | Error Level |
|------|-------|-------------|
| IMPL prefix | Must start with "IMPL-" | ERROR |
| ID format | NN or NNN digits | ERROR |
| Slug format | lowercase, underscores only | ERROR |
| Extension | .md only | ERROR |

### Examples

| Filename | Valid | Reason |
|----------|-------|--------|
| `IMPL-01_risk_management_system.md` | ✅ | Correct format |
| `impl-01_risk_management.md` | ❌ | Lowercase prefix |
| `IMPL-1_risk_management.md` | ❌ | Single digit ID |
| `IMPL-01-risk-management.md` | ❌ | Hyphens in slug |
| `IMPL-01_risk_management.yaml` | ❌ | Wrong extension |

---

## 2. Frontmatter Validation

### Required Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | Yes | Must match "IMPL-NN: [Name]" |
| tags | array | Yes | Must include layer-8-artifact |
| custom_fields.artifact_type | string | Yes | Must equal "IMPL" |
| custom_fields.layer | integer | Yes | Must equal 8 |

### Validation Script

```bash
# Check frontmatter presence
if ! grep -q "^---" "$IMPL_FILE"; then
  echo "ERROR: Missing YAML frontmatter"
fi

# Check artifact type
if ! grep -q "artifact_type: IMPL" "$IMPL_FILE"; then
  echo "ERROR: artifact_type must be IMPL"
fi

# Check layer
if ! grep -q "layer: 8" "$IMPL_FILE"; then
  echo "ERROR: layer must be 8"
fi
```

---

## 3. Document Control Table Validation

### Required Fields

| Field | Required | Format |
|-------|----------|--------|
| IMPL ID | Yes | IMPL-NN |
| Title | Yes | Non-empty string |
| Status | Yes | Draft/Planned/In Progress/On Hold/Completed/Cancelled |
| Version | Yes | X.Y.Z (semantic) |
| Created | Yes | YYYY-MM-DD |
| Author | Yes | Non-empty string |
| Owner | Yes | Non-empty string |
| Last Updated | Yes | YYYY-MM-DD |
| Related REQs | Yes | REQ-NN references |
| Deliverables | Yes | 09_CTR/10_SPEC/TASKS list |

### Validation Rules

1. **IMPL ID** must match filename pattern
2. **Status** must be valid enum value
3. **Version** must follow semantic versioning
4. **Dates** must be valid ISO 8601 format
5. **Related REQs** must reference at least one requirement

---

## 4. Section Structure Validation

### Required Sections (Updated 2026-01-13)

| Section | Required | Validation |
|---------|----------|------------|
| ## 1. Document Control | Yes | Metadata table present |
| ## 2. Position in Document Workflow | Yes | Workflow diagram present |
| ## 3. Project Context and Strategy (PART 1) | Yes | Contains Overview, Objectives, Scope |
| ## 4. Phased Implementation (PART 2) | Yes | At least one phase with element ID |
| ## 5. Project Management and Risk (PART 3) | Yes | Resources, timeline, risks, escalation |
| ## 6. Tracking and Completion (PART 4) | Yes | Deliverables checklist, operational acceptance, sign-off |
| ## 7. Traceability | Yes | Upstream/downstream references, cumulative tags |
| ## 8. References | Yes | Internal and template links |
| ## 9. Template Instructions | Optional | Usage guidance (template files only) |

### Validation Commands

```bash
required_sections=(
  "## 1\. Document Control"
  "## 2\. Position in Document Workflow"
  "## 3\. Project Context and Strategy (PART 1)"
  "## 4\. Phased Implementation (PART 2)"
  "## 5\. Project Management and Risk (PART 3)"
  "## 6\. Tracking and Completion (PART 4)"
  "## 7\. Traceability"
  "## 8\. References"
)

for section in "${required_sections[@]}"; do
  if ! grep -qE "$section" "$IMPL_FILE"; then
    echo "ERROR: Missing section: $section"
  fi
done
```

---

## 5. Section 3 (PART 1) Validation

### Required Subsections (Updated 2026-01-13)

| Section | Required | Validation |
|---------|----------|------------|
| 3.1 Overview | Yes | Non-empty content |
| 3.2 Business Objectives | Yes | REQ references present |
| 3.3 Scope | Yes | In/Out of scope lists |
| 3.4 Upstream Dependencies | Yes | Dependencies listed |

### Validation

```bash
# Check for required subsections in Section 3 (PART 1)
for section in "### 3.1" "### 3.2" "### 3.3" "### 3.4"; do
  if ! grep -q "$section" "$IMPL_FILE"; then
    echo "WARNING: Missing Part 1 subsection: $section"
  fi
done

# Check scope has in/out sections
if ! grep -qi "in scope\|out of scope" "$IMPL_FILE"; then
  echo "WARNING: Scope section should define in/out of scope"
fi
```

---

## 6. Section 4 (PART 2 Phases) Validation

### Requirements (Updated 2026-01-13)

| Check | Error Level |
|-------|-------------|
| At least 1 phase with element ID format | ERROR |
| Phase uses IMPL.NN.29.SS element ID | ERROR |
| Each phase has Purpose | ERROR |
| Each phase has Owner | WARNING |
| Each phase has Deliverables | ERROR |
| Each phase has Timeline | WARNING |
| Each phase has Dependencies | WARNING |
| Each phase has Success Criteria | WARNING |

### Element ID Format

Phases MUST use 4-segment element ID format: `IMPL.NN.29.SS`
- `NN` = Document number (e.g., 01, 02)
- `29` = Element type code for Implementation Phase
- `SS` = Sequence number (e.g., 01, 02)

Example: `### IMPL.01.29.01: Phase 1 - Core Risk Engine`

### Validation Commands

```bash
# Count phases using element ID format (preferred)
phase_count=$(grep -cE "^### IMPL\.[0-9]{2,}\.29\.[0-9]{2,}:" "$IMPL_FILE")

# Fall back to legacy format check
if [ "$phase_count" -lt 1 ]; then
  legacy_count=$(grep -cE "^### Phase [0-9]+" "$IMPL_FILE")
  if [ "$legacy_count" -gt 0 ]; then
    echo "WARNING: $legacy_count phases use deprecated format. Use IMPL.NN.29.SS element IDs."
  else
    echo "ERROR: No phases defined in Section 4 (PART 2)"
  fi
fi

# Check each phase has deliverables
phases=$(grep -cE "^### (IMPL\.[0-9]+\.29\.[0-9]+|Phase [0-9]+)" "$IMPL_FILE")
deliverables=$(grep -cE "(CTR-[0-9]+|SPEC-[0-9]+|TASKS-[0-9]+)" "$IMPL_FILE")
if [ "$deliverables" -lt "$phases" ]; then
  echo "WARNING: Some phases may be missing deliverables"
fi
```

---

## 7. Deliverables Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| At least one 09_CTR/10_SPEC/TASKS referenced | ERROR |
| Deliverables have IDs | ERROR |
| Deliverables in checklist format | WARNING |

### Validation Commands

```bash
# Check for deliverable references
if ! grep -qE "(CTR-[0-9]+|SPEC-[0-9]+|TASKS-[0-9]+)" "$IMPL_FILE"; then
  echo "ERROR: No deliverables (09_CTR/10_SPEC/TASKS) referenced"
fi

# Check for checklist format
if ! grep -q "\[ \]" "$IMPL_FILE"; then
  echo "WARNING: No deliverables checklist found (use [ ] format)"
fi
```

---

## 8. Section 5 (PART 3) Validation

### Required Subsections (Updated 2026-01-13)

| Section | Required | Validation |
|---------|----------|------------|
| 5.1 Resources, Timeline, and Dependencies | Yes | Team assignments present |
| 5.2 Risk Register | Yes | Risk table with contingency plans |
| 5.3 Communication Plan | Yes | Escalation matrix present |

### Risk Register Format

```bash
# Check risk register exists
if ! grep -qE "R-[0-9]+" "$IMPL_FILE"; then
  echo "WARNING: No risk IDs found (use R-001 format)"
fi

# Check for contingency plans section
if ! grep -qi "contingency" "$IMPL_FILE"; then
  echo "WARNING: No contingency plans section found"
fi

# Check for escalation matrix
if ! grep -qi "escalation" "$IMPL_FILE"; then
  echo "WARNING: No escalation matrix found"
fi

# Verify risks are project management focused
if grep -qiE "algorithm|architecture|data structure|class" "$IMPL_FILE" | grep -i "risk"; then
  echo "INFO: Verify technical risks are in 05_ADR/SPEC, not IMPL"
fi
```

---

## 9. Section 6 (PART 4) Validation

### Required Subsections (Updated 2026-01-13)

| Section | Required | Validation |
|---------|----------|------------|
| 6.1 Deliverables Checklist | Yes | [ ] checkboxes present |
| 6.2 Project Validation | Yes | Operational acceptance, validation methods |
| 6.3 Project Completion Criteria | Yes | Completion definition present |
| 6.4 Lessons Learned | Optional | Retrospective section |
| 6.5 Sign-off | Yes | Sign-off table present |

### Validation Commands

```bash
# Check for sign-off table
if ! grep -q "Sign-off" "$IMPL_FILE"; then
  echo "WARNING: No sign-off section found"
fi

# Check for completion criteria
if ! grep -qi "completion criteria\|project complete" "$IMPL_FILE"; then
  echo "WARNING: No completion criteria defined"
fi

# Check for operational acceptance
if ! grep -qi "operational acceptance" "$IMPL_FILE"; then
  echo "WARNING: No operational acceptance section found"
fi

# Check for validation methods
if ! grep -qi "validation methods\|validation type" "$IMPL_FILE"; then
  echo "WARNING: No validation methods table found"
fi
```

---

## 10. Traceability Tag Validation

### Required Upstream Tags (Layer 8)

| Tag | Required | Format |
|-----|----------|--------|
| @brd | Yes | BRD.NN.EE.SS |
| @prd | Yes | PRD.NN.EE.SS |
| @ears | Yes | EARS.NN.EE.SS |
| @bdd | Yes | BDD.NN.EE.SS |
| @adr | Yes | ADR-NN |
| @sys | Yes | SYS.NN.EE.SS |
| @req | Yes | REQ.NN.EE.SS |

### Downstream Tags (Deliverables Produced)

| Tag | Required | Format |
|-----|----------|--------|
| @ctr | When applicable | CTR.NN.EE.SS |
| @spec | When applicable | SPEC.NN.EE.SS |
| @tasks | When applicable | TASKS.NN.EE.SS |

### Validation Commands

```bash
# Required upstream tags
required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req")

for tag in "${required_tags[@]}"; do
  if ! grep -q "^$tag:" "$IMPL_FILE"; then
    echo "ERROR: Missing required tag: $tag"
  fi
done

# Optional downstream tags (check if deliverables exist but tags missing)
downstream_tags=("@ctr" "@spec" "@tasks")

for tag in "${downstream_tags[@]}"; do
  artifact_type="${tag:1}"  # Remove @ prefix
  artifact_upper=$(echo "$artifact_type" | tr '[:lower:]' '[:upper:]')

  # Check if document references this artifact type
  if grep -qE "${artifact_upper}-[0-9]+" "$IMPL_FILE"; then
    if ! grep -q "^$tag:" "$IMPL_FILE"; then
      echo "WARNING: Deliverable ${artifact_upper} referenced but missing $tag traceability tag"
    fi
  fi
done

# Validate tag format
if grep -qE "@[a-z]+:\s*$" "$IMPL_FILE"; then
  echo "ERROR: Empty tag value found"
fi
```

---

## 11. Scope Boundary Validation

### Project Management Focus Check

IMPL should contain project management content, NOT technical details:

```bash
# Check for technical content that belongs in SPEC
technical_patterns=(
  "class [A-Z]"
  "def [a-z]"
  "import "
  "function "
  "algorithm"
  "data structure"
)

for pattern in "${technical_patterns[@]}"; do
  count=$(grep -c "$pattern" "$IMPL_FILE" 2>/dev/null || echo "0")
  if [ "$count" -gt 5 ]; then
    echo "WARNING: Technical content found - consider moving to SPEC"
    echo "  Pattern: $pattern found $count times"
  fi
done

# Check for required project management content
pm_patterns=(
  "Phase"
  "Timeline"
  "Owner"
  "Deliverable"
  "Team"
)

found=0
for pattern in "${pm_patterns[@]}"; do
  if grep -qi "$pattern" "$IMPL_FILE"; then
    ((found++))
  fi
done

if [ "$found" -lt 3 ]; then
  echo "WARNING: Insufficient project management content"
fi
```

---

## 12. Cross-Reference Validation

### Link Resolution

| Link Type | Validation | Error Level |
|-----------|------------|-------------|
| REQ references | File must exist | WARNING |
| ADR references | File must exist | WARNING |
| CTR references | Future deliverable OK | INFO |
| SPEC references | Future deliverable OK | INFO |
| TASKS references | Future deliverable OK | INFO |

### Validation Commands

```bash
# Validate REQ references
grep -oE "REQ-[0-9]+" "$IMPL_FILE" | sort -u | while read -r req_ref; do
  req_file=$(find ../REQ -name "${req_ref}*.md" 2>/dev/null | head -1)
  if [ -z "$req_file" ]; then
    echo "WARNING: Referenced REQ file not found: $req_ref"
  fi
done

# Validate ADR references
grep -oE "ADR-[0-9]+" "$IMPL_FILE" | sort -u | while read -r adr_ref; do
  adr_file=$(find ../ADR -name "${adr_ref}*.md" 2>/dev/null | head -1)
  if [ -z "$adr_file" ]; then
    echo "WARNING: Referenced ADR file not found: $adr_ref"
  fi
done
```

---

## 13. Error Severity Levels

### Error Levels

| Level | Action Required | Examples |
|-------|-----------------|----------|
| ERROR | Must fix before merge | Missing parts, no deliverables |
| WARNING | Should fix | Missing subsections, no timeline |
| INFO | Optional improvement | Style suggestions |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Errors found |
| 2 | Warnings only |

---

## 14. Validation Script Usage

### Command

```bash
./scripts/validate_impl.sh <IMPL_FILE>
```

### Options

```bash
./scripts/validate_impl.sh --help
./scripts/validate_impl.sh --verbose IMPL-01.md
./scripts/validate_impl.sh --strict IMPL-01.md  # Treat warnings as errors
```

### Output Format

```
=========================================
IMPL Validation Report
=========================================
File: IMPL-01_risk_management_system.md
Version: 1.0.0

CHECK 1: Filename Format
  ✅ Filename format valid

CHECK 2: Frontmatter
  ✅ YAML frontmatter present
  ✅ Required fields present

CHECK 3: Required Sections
  ✅ Section 3: Project Context and Strategy (PART 1) present
  ✅ Section 4: Phased Implementation (PART 2) present
  ✅ Section 5: Project Management and Risk (PART 3) present
  ✅ Section 6: Tracking and Completion (PART 4) present
  ✅ Section 7: Traceability present

CHECK 4: Phases (Element ID Format)
  ✅ 3 phases defined using IMPL.NN.29.SS format
  ✅ All phases have deliverables
  ⚠️  WARNING: IMPL.01.29.02 missing timeline

CHECK 5: Deliverables
  ✅ 9 deliverables referenced
  ✅ Checklist format used

CHECK 6: Traceability Tags
  ✅ All 7 required tags present

CHECK 7: Scope Boundaries
  ✅ Project management focused
  ⚠️  WARNING: Some technical content detected

=========================================
SUMMARY
=========================================
Errors: 0
Warnings: 2
Result: PASSED WITH WARNINGS
```

---

## 16. Element ID Format Compliance ⭐ NEW

**Purpose**: Verify element IDs use unified 4-segment format, flag removed patterns.
**Type**: Error

| Check | Pattern | Result |
|-------|---------|--------|
| Valid format | `IMPL.NN.TT.SS:` | ✅ Pass |
| Removed pattern | `Phase-XXX` | ❌ Fail - use IMPL.NN.29.SS |
| Removed pattern | `IP-XXX` | ❌ Fail - use IMPL.NN.29.SS |

**Regex**: `^###?\s+IMPL\.[0-9]{2,}\.[0-9]{2,}\.[0-9]{2,}:\s+.+$`

**Common Element Types for IMPL**:
| Element Type | Code | Example |
|--------------|------|---------|
| Implementation Phase | 29 | IMPL.02.29.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `Phase-XXX` → Use `IMPL.NN.29.SS`
> - `IP-XXX` → Use `IMPL.NN.29.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

**Fix**: Replace `### Phase-01: Setup` with `### IMPL.02.29.01: Setup`

---

## 17. Common Validation Errors

### Error: No Phases Defined

**Symptom**: "ERROR: No phases defined in Section 4 (PART 2)"
**Fix**: Add phases using element ID format `### IMPL.NN.29.SS: Phase N - [Name]` with deliverables, owner, timeline

### Error: Invalid Phase Format

**Symptom**: "ERROR: Phase uses deprecated format"
**Fix**: Replace `### Phase N:` or `### 4.N Phase N:` with `### IMPL.NN.29.SS: Phase N - [Name]`
- Element type code 29 = Implementation Phase
- Example: `### IMPL.01.29.01: Phase 1 - Foundation`

### Error: No Deliverables Referenced

**Symptom**: "ERROR: No deliverables (09_CTR/10_SPEC/TASKS) referenced"
**Fix**: Each phase must list CTR-NN, SPEC-NN, TASKS-NN deliverables

### Error: Missing Required Tag

**Symptom**: "ERROR: Missing required tag: @req"
**Fix**: Add all 7 required upstream traceability tags (@brd, @prd, @ears, @bdd, @adr, @sys, @req)

### Warning: Missing Downstream Tags

**Symptom**: "WARNING: Deliverable CTR referenced but missing @ctr traceability tag"
**Fix**: Add downstream tags (@ctr, @spec, @tasks) in Section 7 Traceability for deliverables listed

### Warning: Technical Content

**Symptom**: "WARNING: Technical content found - consider moving to SPEC"
**Fix**: IMPL should focus on WHO/WHAT/WHEN, not HOW (technical details go in SPEC)

### Warning: Missing Timeline

**Symptom**: "WARNING: IMPL.01.29.02 missing timeline"
**Fix**: Add timeline with dates or sprint references to each phase

---

## References

- [IMPL_CREATION_RULES.md](./IMPL_CREATION_RULES.md) - Creation guidelines
- [IMPL-TEMPLATE.md](./IMPL-TEMPLATE.md) - Implementation plan template
- [IMPL-00_index.md](./IMPL-00_index.md) - Plan registry
- [validate_impl.sh](../scripts/validate_impl.sh) - Validation script
- [README.md](./README.md) - Directory overview

---

**Document Version**: 1.1.0
**Last Updated**: 2026-01-13
