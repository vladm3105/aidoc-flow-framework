# REQ V2 to V3 Migration Plan

**Version**: 1.0.0
**Date**: 2025-11-19
**Purpose**: Complete migration strategy for REQ framework from V2 to V3
**Status**: Draft

---

## Executive Summary

**Current State**:
- REQ-TEMPLATE.md (V2.0) exists as baseline
- REQ-TEMPLATE-V3.md (V3.0) exists as target
- 14 REQ files total (including templates, examples, archived)
- Example files currently use V2.0 format
- Validation script (validate_req_template_v3.sh) enforces V3 standards

**Migration Scope**:
- **Additive migration**: V2 files remain valid, V3 adds enhancements
- **No breaking changes**: Existing V2 content preserved
- **New requirements**: 11 Document Control fields, Template Version field, enhanced traceability

**Timeline**: Single migration session (1-2 hours)

---

## V2 vs V3 Key Differences

### 1. Document Control Fields

**V2.0 (10 fields)**:
- Status, Version, Date Created, Last Updated, Author, Priority, Category, Source Document, Verification Method, Assigned Team, SPEC-Ready Score

**V3.0 (11 fields)** - ADDED:
- **Template Version** (NEW) - Must be `3.0`

**Enhanced Fields**:
- **Priority**: Now requires P-level → `High (P2)` instead of `High`
- **Source Document**: Now requires section → `SYS-002 Section 3.1.1` instead of `SYS-002`
- **SPEC-Ready Score**: Now requires emoji → `✅ 95% (Target: ≥90%)` instead of `95%`

### 2. Path References

**V2.0**: Relative paths from REQ directory
```markdown
[SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
```

**V3.0**: Absolute paths from project root
```markdown
[SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../../docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
```

### 3. Layer Numbering

**V2.0**: Layer 4
**V3.0**: Layer 7 (corrected to match 16-layer architecture)

### 4. Section Enhancements

**V3.0 Added Subsections**:
- **Section 3.3**: REST API Endpoints (if applicable)
- **Section 4.3**: Database Schema (if applicable)
- **Section 5.4**: Circuit Breaker Configuration
- **Section 8.3**: Dependency Injection

### 5. Cumulative Tagging Hierarchy

**V3.0 Enforcement**: All 6 upstream tags required in Section 11
```markdown
@brd: BRD-NNN:REQ-ID
@prd: PRD-NNN:REQ-ID
@ears: EARS-NNN:REQ-ID
@bdd: BDD-NNN:scenario-name
@adr: ADR-NNN
@sys: SYS-NNN:REQ-ID
```

### 6. Resource Tags in H1

**V2.0**: Optional
**V3.0**: Required for Template 2.0+
```markdown
# REQ-001: [EXTERNAL_SERVICE_GATEWAY] API Integration
```

---

## Migration Strategy

### Phase 1: Template Updates (Completed ✅)

**Status**: Already complete
- REQ-TEMPLATE-V3.md created
- REQ-VALIDATION-RULES.md created
- validate_req_template_v3.sh script created

### Phase 2: Example File Migration

**Scope**: 4 example files in `/examples/` directory
- `examples/api/REQ-001_api_integration_example.md`
- `examples/api/av/REQ-001_alpha_vantage_integration.md`
- `examples/api/ib/REQ-002_ib_gateway_integration.md`
- `examples/auth/REQ-003_access_control_example.md`
- `examples/data/REQ-002_data_validation_example.md`
- `examples/risk/lim/REQ-003_position_limit_enforcement.md`

**Migration Steps**:
1. Update Document Control to 11 fields
2. Add Template Version field
3. Update path references (relative → absolute)
4. Update layer number (4 → 7)
5. Enhance priority format (add P-level)
6. Enhance source document (add section)
7. Enhance SPEC-Ready Score (add ✅ emoji)
8. Add cumulative tags (if missing)
9. Add resource tags to H1 (if missing)
10. Validate with v3 script

### Phase 3: README.md Update

**Updates Required**:
- Add V3.0 migration guide section
- Update template comparison table
- Add validation command examples
- Link to REQ-VALIDATION-RULES.md

### Phase 4: Archive Legacy Files

**Files to Archive**:
- Move outdated templates to `archived/`
- Keep REQ-TEMPLATE.md (V2.0) for reference
- Add deprecation notice to V1 templates

---

## Migration Checklist

### Per-File Migration Tasks

For each REQ file being migrated:

- [ ] **Document Control**
  - [ ] Add Template Version: `3.0`
  - [ ] Update Priority format: `High (P2)`
  - [ ] Update Source Document: Add section reference
  - [ ] Update SPEC-Ready Score: Add ✅ emoji

- [ ] **Path Updates**
  - [ ] Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md path
  - [ ] Update index.md path
  - [ ] Update all cross-reference paths

- [ ] **Layer Numbering**
  - [ ] Change Layer 4 → Layer 7

- [ ] **H1 Header**
  - [ ] Add resource tag: `[RESOURCE_TYPE]`

- [ ] **Traceability (Section 11)**
  - [ ] Add @brd tag
  - [ ] Add @prd tag
  - [ ] Add @ears tag
  - [ ] Add @bdd tag
  - [ ] Add @adr tag
  - [ ] Add @sys tag

- [ ] **Validation**
  - [ ] Run validate_req_template_v3.sh
  - [ ] Fix all errors
  - [ ] Address warnings

---

## Automated Migration Script

### Script Requirements

**Purpose**: Automate repetitive V2→V3 transformations

**Transformations**:
1. Add Template Version field to Document Control
2. Update priority format (detect and add P-level)
3. Update SPEC-Ready Score format (add ✅)
4. Update path references (relative → absolute)
5. Update layer numbers (4 → 7)

**Not Automated** (requires manual review):
- Adding resource tags to H1 (context-specific)
- Adding cumulative tags (document-specific)
- Adding section-specific content enhancements
- Validating link targets exist

### Script Location

`/opt/data/docs_flow_framework/ai_dev_flow/scripts/migrate_req_v2_to_v3.py`

---

## Validation Process

### Pre-Migration Validation

```bash
# Backup existing files
cp -r /opt/data/docs_flow_framework/ai_dev_flow/REQ/examples /tmp/req_examples_backup

# Document current state
find /opt/data/docs_flow_framework/ai_dev_flow/REQ/examples -name "*.md" -exec head -50 {} \; > /tmp/req_v2_state.txt
```

### Post-Migration Validation

```bash
# Run V3 validation on all example files
find /opt/data/docs_flow_framework/ai_dev_flow/REQ/examples -name "REQ-*.md" \
  -exec /opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_req_template_v3.sh {} \;

# Expected: All files pass with 0 errors
```

### Validation Criteria

**Success Criteria**:
- ✅ All 18 validation checks pass
- ✅ Zero blocking errors
- ✅ Warnings addressed or documented
- ✅ All links resolve correctly
- ✅ All cumulative tags present
- ✅ SPEC-Ready Score ≥ 90% with supporting content

---

## Risk Assessment

### Low Risk

**Additive Migration**: V3 adds fields, doesn't remove V2 content
- **Mitigation**: Existing V2 files remain valid
- **Rollback**: Simple (restore from backup)

### Medium Risk

**Path Updates**: Broken links if paths incorrect
- **Mitigation**: Validation script checks link resolution
- **Rollback**: Automated script can revert paths

### High Risk

**Example Files**: Used as reference by other projects
- **Mitigation**: Thorough validation before commit
- **Rollback**: Git revert available

---

## Migration Execution Plan

### Step 1: Create Migration Script

**File**: `scripts/migrate_req_v2_to_v3.py`
**Duration**: 30 minutes
**Dependencies**: Python 3.8+, regex

### Step 2: Migrate Example Files

**Duration**: 20 minutes (6 files × 3 min each + validation)
**Order**:
1. `examples/api/REQ-001_api_integration_example.md` (baseline)
2. `examples/api/av/REQ-001_alpha_vantage_integration.md`
3. `examples/api/ib/REQ-002_ib_gateway_integration.md`
4. `examples/data/REQ-002_data_validation_example.md`
5. `examples/auth/REQ-003_access_control_example.md`
6. `examples/risk/lim/REQ-003_position_limit_enforcement.md`

### Step 3: Update README.md

**Duration**: 15 minutes
**Sections to Update**:
- Template Evolution table
- Migration Guide section
- Validation Tools section
- Best Practices section

### Step 4: Validation and Testing

**Duration**: 15 minutes
**Activities**:
- Run v3 validation on all files
- Fix any errors
- Document warnings
- Verify all links resolve

### Step 5: Documentation

**Duration**: 10 minutes
**Deliverables**:
- Migration summary report
- Known issues document
- Update CHANGELOG.md

---

## Post-Migration Actions

### Immediate

- [ ] Commit migrated files
- [ ] Update project documentation
- [ ] Notify team of V3 availability

### Short-term (1 week)

- [ ] Monitor for migration issues
- [ ] Address feedback
- [ ] Refine migration script

### Long-term (1 month)

- [ ] Deprecate V1 templates completely
- [ ] Create migration guide for project-specific REQ files
- [ ] Add V3 training materials

---

## Known Limitations

### Manual Steps Required

**Cannot be automated**:
1. **Resource tags**: Context-specific, requires domain knowledge
2. **Cumulative tags**: Document-specific, requires traceability analysis
3. **Content enhancements**: Sections 3.3, 4.3, 5.4, 8.3 require technical input
4. **Link validation**: Broken links require manual fixing

### Template Coexistence

**V2 and V3 coexist**:
- REQ-TEMPLATE.md (V2.0) remains for reference
- REQ-TEMPLATE-V3.md (V3.0) is recommended
- Migration is optional but recommended

---

## Migration Script Specification

### Input Parameters

```python
migrate_req_v2_to_v3(
    input_file: str,           # Path to V2 REQ file
    output_file: str = None,   # Optional output path (default: overwrite)
    dry_run: bool = False,     # Preview changes without writing
    validate: bool = True       # Run v3 validation after migration
)
```

### Transformation Rules

**Rule 1: Document Control**
```python
# Add Template Version field after SPEC-Ready Score
| **Template Version** | 3.0 |
```

**Rule 2: Priority Enhancement**
```python
# Transform priority values
"Critical" → "Critical (P1)"
"High" → "High (P2)"
"Medium" → "Medium (P3)"
"Low" → "Low (P4)"
```

**Rule 3: SPEC-Ready Score Enhancement**
```python
# Add checkmark emoji
"95%" → "✅ 95% (Target: ≥90%)"
"92% (Target: ≥90%)" → "✅ 92% (Target: ≥90%)"
```

**Rule 4: Path Updates**
```python
# Update relative paths to absolute
"../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md" → "../../../docs_flow_framework/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md"
"../index.md" → "../../../docs_flow_framework/ai_dev_flow/index.md"
```

**Rule 5: Layer Number**
```python
# Update layer references
"Layer 4" → "Layer 7"
```

### Error Handling

**Scenarios**:
1. Missing Document Control section → Error (manual fix required)
2. Invalid priority format → Warning (suggest format)
3. Missing SPEC-Ready Score → Error (manual fix required)
4. Broken links → Warning (list for manual review)

---

## Success Metrics

### Quantitative

- **Migration Rate**: 6/6 example files migrated (100%)
- **Validation Pass Rate**: 6/6 files pass v3 validation (100%)
- **Error Rate**: 0 blocking errors
- **Completion Time**: < 2 hours total

### Qualitative

- **Documentation Quality**: README.md updated with migration guide
- **Automation Level**: 70% of transformations automated
- **Maintainability**: Migration script reusable for project REQ files

---

## Appendix A: Template Comparison Matrix

| Feature | V2.0 | V3.0 | Change Type |
|---------|------|------|-------------|
| Document Control Fields | 10 | 11 | Additive |
| Priority Format | `High` | `High (P2)` | Enhancement |
| Source Document | `SYS-002` | `SYS-002 Section 3.1.1` | Enhancement |
| SPEC-Ready Score | `95%` | `✅ 95% (Target: ≥90%)` | Enhancement |
| Template Version | N/A | `3.0` | New |
| Layer Number | 4 | 7 | Correction |
| Path References | Relative | Absolute | Update |
| Resource Tags | Optional | Required | Enforcement |
| Cumulative Tags | Recommended | Required | Enforcement |
| REST API Section | N/A | Section 3.3 | New |
| Database Schema | N/A | Section 4.3 | New |
| Circuit Breaker | N/A | Section 5.4 | New |
| Dependency Injection | N/A | Section 8.3 | New |

---

## Appendix B: File Inventory

### Framework Files

| File | Type | Version | Status | Migration |
|------|------|---------|--------|-----------|
| REQ-TEMPLATE.md | Template | 2.0 | Active | Reference only |
| REQ-TEMPLATE-V3.md | Template | 3.0 | Recommended | N/A |
| README.md | Guide | Mixed | Active | Update required |
| REQ-VALIDATION-RULES.md | Rules | 3.0 | Active | N/A |
| REQ-000_index.md | Index | Mixed | Active | Review |
| REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md | Template | 3.0 | Active | N/A |

### Example Files (Migration Required)

| File | Type | Current Version | Target | Complexity |
|------|------|----------------|--------|------------|
| examples/api/REQ-001_api_integration_example.md | Example | 2.0 | 3.0 | High |
| examples/api/av/REQ-001_alpha_vantage_integration.md | Example | 2.0 | 3.0 | Medium |
| examples/api/ib/REQ-002_ib_gateway_integration.md | Example | 2.0 | 3.0 | Medium |
| examples/data/REQ-002_data_validation_example.md | Example | 2.0 | 3.0 | Medium |
| examples/auth/REQ-003_access_control_example.md | Example | 2.0 | 3.0 | Medium |
| examples/risk/lim/REQ-003_position_limit_enforcement.md | Example | 2.0 | 3.0 | Low |

### Archived Files

| File | Type | Version | Status |
|------|------|---------|--------|
| archived/REQ-TEMPLATE-V1-ARCHIVED.md | Template | 1.0 | Deprecated |

---

## Appendix C: Validation Command Reference

### Single File Validation

```bash
/opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_req_template_v3.sh \
  /opt/data/docs_flow_framework/ai_dev_flow/REQ/examples/api/REQ-001_api_integration_example.md
```

### Batch Validation

```bash
find /opt/data/docs_flow_framework/ai_dev_flow/REQ/examples -name "REQ-*.md" \
  -exec /opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_req_template_v3.sh {} \;
```

### Validation with Summary

```bash
for file in $(find /opt/data/docs_flow_framework/ai_dev_flow/REQ/examples -name "REQ-*.md"); do
  echo "=== Validating: $(basename "$file") ==="
  /opt/data/docs_flow_framework/ai_dev_flow/scripts/validate_req_template_v3.sh "$file"
  echo ""
done
```

---

**Document Status**: Draft
**Review Date**: 2025-11-19
**Next Update**: After migration execution
**Maintained By**: System Architect
