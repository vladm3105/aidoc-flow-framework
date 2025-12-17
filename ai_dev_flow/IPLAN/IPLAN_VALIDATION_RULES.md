# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of IPLAN-TEMPLATE.md
# - Authority: IPLAN-TEMPLATE.md is the single source of truth for IPLAN structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from IPLAN_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to IPLAN-TEMPLATE.md
# =============================================================================
---
title: "IPLAN Validation Rules"
tags:
  - validation-rules
  - layer-12-artifact
  - shared-architecture
custom_fields:
  document_type: validation_rules
  artifact_type: IPLAN
  layer: 12
  priority: shared
  development_status: active
---

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for IPLAN documents.
> - Apply these rules after IPLAN creation or modification
> - **Authority**: Validates compliance with `IPLAN-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing IPLAN changes

# IPLAN Validation Rules

Rules for validating Implementation Plans (IPLAN) documents in the SDD framework.

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Created** | 2025-11-27 |
| **Last Updated** | 2025-11-29 |
| **Status** | Active |

### Reserved ID Exemption (IPLAN-000_*)

**Scope**: Documents with reserved ID `000` are FULLY EXEMPT from validation.

**Pattern**: `IPLAN-000_*.md`

**Document Types**:
- Index documents (`IPLAN-000_index.md`)
- Traceability matrix templates (`IPLAN-000_TRACEABILITY_MATRIX-TEMPLATE.md`)
- Glossaries, registries, checklists

**Rationale**: Reserved ID 000 documents are framework infrastructure (indexes, templates, reference materials), not project artifacts requiring traceability or quality gates.

**Validation Behavior**: Skip all checks when filename matches `IPLAN-000_*` pattern.

---

## 1. Filename Validation

### Pattern

```regex
^IPLAN-[0-9]{3,4}_[a-z0-9_]+\.md$
```

### Rules

| Rule | Check | Error Level |
|------|-------|-------------|
| IPLAN prefix | Must start with "IPLAN-" | ERROR |
| ID format | NNN or NNNN digits | ERROR |
| Slug format | lowercase, underscores only | ERROR |
| Extension | .md only | ERROR |

### Examples

| Filename | Valid | Reason |
|----------|-------|--------|
| `IPLAN-001_gateway_connection.md` | ✅ | Correct format |
| `IPLAN-001_trade_validation.md` | ✅ | Correct format |
| `iplan-001_gateway_connection.md` | ❌ | Lowercase prefix |
| `IPLAN-1_gateway_connection.md` | ❌ | Single digit ID |
| `IPLAN-001-gateway-connection.md` | ❌ | Hyphens in slug |
| `IPLAN-001_Gateway_Connection.md` | ❌ | Uppercase in slug |

---

## 2. Frontmatter Validation

### Required Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | Yes | Must match "IPLAN-NNN: [Name]" |
| tags | array | Yes | Must include layer-12-artifact |
| custom_fields.artifact_type | string | Yes | Must equal "IPLAN" |
| custom_fields.layer | integer | Yes | Must equal 12 |
| custom_fields.parent_tasks | string | Yes | TASKS-NNN format |

### Validation Script

```bash
# Check frontmatter presence
if ! grep -q "^---" "$IPLAN_FILE"; then
  echo "ERROR: Missing YAML frontmatter"
fi

# Check artifact type
if ! grep -q "artifact_type: IPLAN" "$IPLAN_FILE"; then
  echo "ERROR: artifact_type must be IPLAN"
fi

# Check layer
if ! grep -q "layer: 12" "$IPLAN_FILE"; then
  echo "ERROR: layer must be 12"
fi

# Check parent_tasks
if ! grep -q "parent_tasks: TASKS-" "$IPLAN_FILE"; then
  echo "ERROR: Missing parent_tasks field"
fi
```

---

## 3. Document Control Table Validation

### Required Fields

| Field | Required | Format |
|-------|----------|--------|
| ID | Yes | IPLAN-NNN |
| Status | Yes | Draft/Ready/In Progress/Completed/Blocked |
| Version | Yes | X.Y.Z (semantic) |
| Created | Yes | YYYY-MM-DD HH:MM:SS TZ |
| Last Updated | Yes | YYYY-MM-DD HH:MM:SS TZ |
| Author | Yes | Non-empty string |
| Estimated Effort | Yes | Hours format |
| Complexity | Yes | 1-5 integer |
| Parent TASKS | Yes | TASKS-NNN |

### Validation Rules

1. **IPLAN ID** must match filename pattern
2. **Status** must be valid enum value
3. **Timestamps** must be valid ISO 8601 with timezone
4. **Complexity** must be 1-5 integer
5. **Parent TASKS** must reference valid TASKS file

---

## 4. Section Structure Validation

### Required Sections

| Section | Required | Validation |
|---------|----------|------------|
| Position in Workflow | Yes | Layer 12 context documented |
| Objective | Yes | Goal and deliverables |
| Context | Yes | Current state analysis |
| Task List | Yes | Phase-based with checkboxes |
| Implementation Guide | Yes | Bash commands present |
| Traceability Tags | Yes | All 9 mandatory tags |
| Traceability | Yes | Upstream/downstream refs |
| Risk Mitigation | Yes | Risks documented |
| Success Criteria | Yes | Metrics defined |

### Validation Commands

```bash
required_sections=(
  "## Position in"
  "## Objective"
  "## Context"
  "## Task List"
  "## Implementation Guide"
  "## Traceability Tags"
  "## Traceability"
  "## Risk"
  "## Success Criteria"
)

for section in "${required_sections[@]}"; do
  if ! grep -q "$section" "$IPLAN_FILE"; then
    echo "ERROR: Missing section: $section"
  fi
done
```

---

## 5. Task List Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| Phase structure present | ERROR |
| Checkboxes present | ERROR |
| At least 1 phase defined | ERROR |
| Time estimates present | WARNING |
| Status markers present | WARNING |

### Validation Commands

```bash
# Check for phases
phase_count=$(grep -cE "^### Phase [0-9]+" "$IPLAN_FILE")
if [ "$phase_count" -lt 1 ]; then
  echo "ERROR: No phases defined in Task List"
fi

# Check for checkboxes
checkbox_count=$(grep -c "\[[ x]\]" "$IPLAN_FILE")
if [ "$checkbox_count" -lt 1 ]; then
  echo "ERROR: No task checkboxes found"
fi

# Check for time estimates
if ! grep -qE "[0-9]+ hours?" "$IPLAN_FILE"; then
  echo "WARNING: No time estimates found"
fi

# Check for status markers
if ! grep -qE "(COMPLETED|PENDING|IN PROGRESS)" "$IPLAN_FILE"; then
  echo "WARNING: No phase status markers found"
fi
```

---

## 6. Implementation Guide Validation

### CRITICAL: Bash Command Requirements

| Check | Error Level |
|-------|-------------|
| Bash code blocks present | ERROR |
| At least 3 bash blocks | WARNING |
| Verification commands present | ERROR |
| Expected output documented | WARNING |
| No relative paths | ERROR |

### Validation Commands

```bash
# Check for bash code blocks
bash_count=$(grep -c '```bash' "$IPLAN_FILE")
if [ "$bash_count" -lt 1 ]; then
  echo "ERROR: No bash code blocks found"
elif [ "$bash_count" -lt 3 ]; then
  echo "WARNING: Only $bash_count bash blocks (recommend 3+)"
fi

# Check for verification sections
if ! grep -qi "verification\|verify\|expected" "$IPLAN_FILE"; then
  echo "ERROR: No verification steps found"
fi

# Check for relative paths (should be absolute)
if grep -qE '(cd|touch|mkdir) \.\.' "$IPLAN_FILE"; then
  echo "ERROR: Relative paths found - use absolute paths"
fi

if grep -qE '(cd|touch|mkdir) [^/~$]' "$IPLAN_FILE" | grep -v "cd \$"; then
  echo "WARNING: Potential relative paths - prefer absolute paths"
fi
```

---

## 7. Traceability Tags Validation

### Required Tags (Layer 12 - All 9 Mandatory)

| Tag | Required | Format |
|-----|----------|--------|
| @brd | Yes | BRD.NN.EE.SS (sub-ID) or BRD-NNN (doc-level) |
| @prd | Yes | PRD.NN.EE.SS (sub-ID) or PRD-NNN (doc-level) |
| @ears | Yes | EARS.NN.EE.SS |
| @bdd | Yes | BDD.NN.EE.SS (sub-ID) or BDD-NNN (doc-level) |
| @adr | Yes | ADR-NNN |
| @sys | Yes | SYS.NN.EE.SS (sub-ID) or SYS-NNN (doc-level) |
| @req | Yes | REQ.NN.EE.SS (sub-ID) or REQ-NNN (doc-level) |
| @spec | Yes | SPEC-NNN |
| @tasks | Yes | TASKS-NNN |

### Optional Tags (If present in project)

| Tag | Required | Format |
|-----|----------|--------|
| @impl | Conditional | IMPL-NNN (if project uses IMPL) |
| @ctr | Conditional | CTR-NNN (if contracts defined) |

### Validation Commands

```bash
required_tags=("@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req" "@spec" "@tasks")

for tag in "${required_tags[@]}"; do
  if ! grep -q "$tag:" "$IPLAN_FILE"; then
    echo "ERROR: Missing required tag: $tag"
  fi
done

# Validate tag format
if grep -qE "@[a-z]+:\s*$" "$IPLAN_FILE"; then
  echo "ERROR: Empty tag value found"
fi

# Count total tags
tag_count=$(grep -cE "^- \`@[a-z]+:" "$IPLAN_FILE")
echo "INFO: Found $tag_count traceability tags"
if [ "$tag_count" -lt 9 ]; then
  echo "ERROR: Only $tag_count tags found (minimum 9 required)"
fi
```

---

## 8. Prerequisites Validation

### Required Prerequisites Sections

| Section | Required | Validation |
|---------|----------|------------|
| Required Tools | Yes | Tool list present |
| Required Files Access | Yes | Paths documented |
| Environment Setup | Yes | Setup steps present |

### Validation Commands

```bash
# Check for prerequisites section
if ! grep -qi "prerequisites" "$IPLAN_FILE"; then
  echo "WARNING: No Prerequisites section found"
fi

# Check for tools
if ! grep -qi "required tools\|tools:" "$IPLAN_FILE"; then
  echo "WARNING: Required tools not documented"
fi

# Check for file access
if ! grep -qi "file.* access\|required files" "$IPLAN_FILE"; then
  echo "WARNING: Required file access not documented"
fi
```

---

## 9. Cross-Reference Validation

### Link Resolution

| Link Type | Validation | Error Level |
|-----------|------------|-------------|
| TASKS references | File must exist | ERROR |
| SPEC references | File must exist | WARNING |
| REQ references | File must exist | WARNING |
| ADR references | File must exist | WARNING |
| BDD references | File must exist | WARNING |

### Validation Commands

```bash
# Validate parent TASKS reference
parent_tasks=$(grep -oE "TASKS-[0-9]+" "$IPLAN_FILE" | head -1)
if [ -n "$parent_tasks" ]; then
  tasks_file=$(find ../TASKS -name "${parent_tasks}*.md" 2>/dev/null | head -1)
  if [ -z "$tasks_file" ]; then
    echo "ERROR: Parent TASKS file not found: $parent_tasks"
  fi
fi

# Validate SPEC references
grep -oE "SPEC-[0-9]+" "$IPLAN_FILE" | sort -u | while read -r spec_ref; do
  spec_file=$(find ../SPEC -name "${spec_ref}*.yaml" 2>/dev/null | head -1)
  if [ -z "$spec_file" ]; then
    echo "WARNING: Referenced SPEC file not found: $spec_ref"
  fi
done

# Validate BDD references
grep -oE "BDD-[0-9]+" "$IPLAN_FILE" | sort -u | while read -r bdd_ref; do
  bdd_file=$(find ../BDD -name "${bdd_ref}*.feature" -o -name "${bdd_ref}*.md" 2>/dev/null | head -1)
  if [ -z "$bdd_file" ]; then
    echo "WARNING: Referenced BDD file not found: $bdd_ref"
  fi
done
```

---

## 10. Token Size Validation

### Size Limits

| Tool | Optimal | Maximum | Error Level |
|------|---------|---------|-------------|
| Claude Code | 25-40KB | 100KB | WARNING/ERROR |
| Gemini CLI | 10KB | Use file tool | INFO |

### Validation Commands

```bash
# Get file size in bytes
file_size=$(wc -c < "$IPLAN_FILE")
file_kb=$((file_size / 1024))

if [ "$file_kb" -gt 400 ]; then
  echo "ERROR: File size ${file_kb}KB exceeds 400KB maximum"
elif [ "$file_kb" -gt 200 ]; then
  echo "WARNING: File size ${file_kb}KB exceeds 200KB optimal"
elif [ "$file_kb" -gt 100 ]; then
  echo "INFO: File size ${file_kb}KB - consider optimization"
fi

# Estimate token count (rough: 1 token ≈ 4 chars)
char_count=$(wc -c < "$IPLAN_FILE")
token_estimate=$((char_count / 4))
echo "INFO: Estimated token count: ~$token_estimate"
```

---

## 11. Verification Checklist Validation

### Requirements

| Check | Error Level |
|-------|-------------|
| Verification section exists | ERROR |
| Checkboxes in verification | WARNING |
| Coverage metrics present | WARNING |
| Phase-based verification | WARNING |

### Validation Commands

```bash
# Check verification section
if ! grep -qi "verification checklist" "$IPLAN_FILE"; then
  echo "WARNING: No Verification Checklist section found"
fi

# Check for coverage metrics
if ! grep -qE "[0-9]+%" "$IPLAN_FILE"; then
  echo "WARNING: No coverage percentages found"
fi

# Check for phase verification
if ! grep -qi "after phase" "$IPLAN_FILE"; then
  echo "WARNING: No phase-based verification found"
fi
```

---

## 12. Error Severity Levels

### Error Levels

| Level | Action Required | Examples |
|-------|-----------------|----------|
| ERROR | Must fix before merge | Missing tags, no bash commands, invalid format |
| WARNING | Should fix | Missing verification, no time estimates |
| INFO | Optional improvement | Token optimization, style suggestions |

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
./scripts/validate_iplan.sh <IPLAN_FILE>
```

### Options

```bash
./scripts/validate_iplan.sh --help
./scripts/validate_iplan.sh --verbose IPLAN-001.md
./scripts/validate_iplan.sh --strict IPLAN-001.md  # Treat warnings as errors
```

### Output Format

```
=========================================
IPLAN Validation Report
=========================================
File: IPLAN-001_gateway_connection.md
Version: 1.0.0

CHECK 1: Filename Format
  ✅ Filename format valid

CHECK 2: Frontmatter
  ✅ YAML frontmatter present
  ✅ Required fields present
  ✅ Parent TASKS specified

CHECK 3: Required Sections
  ✅ All 9 required sections found

CHECK 4: Task List
  ✅ 4 phases defined
  ✅ 24 task checkboxes found
  ✅ Time estimates present

CHECK 5: Implementation Guide
  ✅ 12 bash code blocks found
  ✅ Verification commands present
  ✅ No relative paths detected

CHECK 6: Traceability Tags
  ✅ All 9 mandatory tags present
  ✅ 2 optional tags present (@impl, @ctr)
  ✅ Total: 11 tags

CHECK 7: Cross-References
  ✅ Parent TASKS exists
  ✅ All SPEC references valid
  ⚠️  WARNING: BDD-007 file not found

CHECK 8: Token Size
  ✅ File size: 35KB (optimal range)
  ✅ Estimated tokens: ~8,750

=========================================
SUMMARY
=========================================
Errors: 0
Warnings: 1
Result: PASSED WITH WARNINGS
```

---

## 14. Code Quality Validation Rules

### 15. Import Verification

**Severity**: ERROR

**Rule**: All implementation phases must include import verification step.

**Required Command**:
```bash
python -m py_compile src/module/__init__.py
python -c "from module import *; print('Imports OK')"
```

**Validation**:
- [ ] `py_compile` check present in verification steps
- [ ] Import test command present after file creation

### 16. Input Validation Gate

**Severity**: ERROR

**Rule**: Functions accepting external input must validate:

**Checklist**:
- [ ] String parameters: empty check, length limit
- [ ] Numeric parameters: range validation with Pydantic `Field(ge=, le=)`
- [ ] Identifier parameters: format validation (no empty strings)
- [ ] File paths: existence check, path traversal prevention

**Prohibited**:
```python
# No validation
def process(data: str):
    return data.upper()

# With validation
def process(data: str):
    if not data or not data.strip():
        raise ValueError("Data cannot be empty")
    return data.upper()
```

### 17. Exception Handling Gate

**Severity**: ERROR

**Rule**: Exception handlers must not silently swallow errors.

**Prohibited Patterns** (will fail validation):
- `except Exception: pass`
- `except: return None`
- `except ValueError: return default` (without logging)

**Required Pattern**:
```python
except SpecificError as e:
    logger.warning("Handled error: %s", e)
    return fallback_value
```

**Validation Command**:
```bash
# Search for silent exception handlers
grep -nE "except.*:\s*(pass|return)" src/**/*.py
# Each match must have logging before return
```

### 18. Async Lock Verification

**Severity**: WARNING

**Rule**: Async code must use `asyncio.Lock`, not `threading.Lock`.

**Check Command**:
```bash
grep -n "threading.Lock" src/**/*.py
# Should return empty for async modules
```

**Exception**: Sync-only modules may use threading locks (document reason).

**Validation**:
- [ ] No `threading.Lock` in files with `async def`
- [ ] Lock type documented in code comments

### 19. Resource Cleanup Verification

**Severity**: WARNING

**Rule**: Classes managing resources must implement cleanup.

**Required for**:
- Classes with `_cache` attributes
- Classes with `_connection` attributes
- Classes with background tasks
- Classes implementing `__aenter__`

**Verification Command**:
```bash
# Classes with cache should have clear_cache or cleanup method
grep -l "_cache" src/**/*.py | xargs grep -L "clear\|cleanup"
# Should return empty
```

**Validation**:
- [ ] Classes with `_cache` have `clear()` or `cleanup()` method
- [ ] Classes with `__aenter__` have `__aexit__` with cleanup
- [ ] Background task classes have task cancellation in cleanup

### 20. Type Hint Quality Gate

**Severity**: WARNING

**Rule**: Minimize use of `Any` type.

**Check Command**:
```bash
grep -n "Optional\[Any\]" src/**/*.py
grep -n ": Any" src/**/*.py
# Each occurrence must have documented justification
```

**Acceptable Uses**:
- Third-party library objects without stubs
- Dynamic plugin systems
- Must add comment: `# Any: reason`

**Validation**:
- [ ] `Any` type usage documented with comment
- [ ] No `Optional[Any]` without justification
- [ ] Prefer `Protocol` for duck typing

### 21. Code Duplication Check

**Severity**: INFO

**Rule**: Before implementing utility functions, search for existing implementations.

**Required Step**:
```bash
# Search for similar function names
grep -r "function_name" src/

# Search for similar patterns
grep -r "pattern" src/
```

**Document**: If similar code exists, document why new implementation needed.

**Validation**:
- [ ] Pre-implementation search documented in IPLAN
- [ ] Duplication justification provided if applicable

---

## 15. Common Validation Errors

### Error: Invalid Filename Format

**Symptom**: "ERROR: Filename does not match IPLAN-NNN_{slug}.md format"
**Fix**: Ensure filename follows `IPLAN-NNN_{descriptive_slug}.md` pattern

**Examples**:
- ✅ `IPLAN-001_gateway_connection.md`
- ❌ `IPLAN-001-gateway-connection.md` (hyphens in slug)
- ❌ `IPLAN_001_gateway.md` (missing hyphen after IPLAN)

### Error: Missing Required Tags

**Symptom**: "ERROR: Missing required tag: @tasks"
**Fix**: Add all 9 mandatory tags in Traceability Tags section

### Error: No Bash Commands

**Symptom**: "ERROR: No bash code blocks found"
**Fix**: Add executable bash commands in Implementation Guide section

### Error: Relative Paths

**Symptom**: "ERROR: Relative paths found - use absolute paths"
**Fix**: Change `cd ../src` to `cd /opt/data/project/src`

### Error: Missing Parent TASKS

**Symptom**: "ERROR: Parent TASKS file not found"
**Fix**: Verify parent_tasks field references existing TASKS document

### Warning: Missing Verification

**Symptom**: "WARNING: No verification steps found"
**Fix**: Add verification commands after each bash step

### Warning: File Size

**Symptom**: "WARNING: File size exceeds 200KB"
**Fix**: Split into multiple IPLAN files or use external references

---

## References

- [IPLAN_CREATION_RULES.md](./IPLAN_CREATION_RULES.md) - Creation guidelines
- [IPLAN-TEMPLATE.md](./IPLAN-TEMPLATE.md) - Implementation plan template
- [IPLAN-000_index.md](./IPLAN-000_index.md) - Plan registry
- [validate_iplan.sh](../scripts/validate_iplan.sh) - Validation script
- [README.md](./README.md) - Directory overview
- [TRACEABILITY.md](../TRACEABILITY.md) - Cumulative tagging hierarchy

---

**Document Version**: 1.1.0
**Last Updated**: 2025-11-29
