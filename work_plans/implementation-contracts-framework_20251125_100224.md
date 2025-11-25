# Implementation Plan - Implementation Contracts Framework with @icon Tag

**Created**: 2025-11-25 10:02:24 EST
**Status**: Ready for Implementation
**Project**: docs_flow_framework
**Work Plan Location**: `/opt/data/docs_flow_framework/work_plans/implementation-contracts-framework_20251125_100224.md`

---

## Objective

Rename "Integration Contracts" to "Implementation Contracts" across the framework and implement the `@icon` traceability tag and optional `ICON-NNN` file prefix for standalone implementation contract artifacts. This enhances clarity by distinguishing TASKS-level implementation contracts (Layer 11) from CTR API contracts (Layer 9) and emphasizes their purpose of enabling parallel implementation.

---

## Context

### Background

The Integration Contracts framework was successfully implemented in the previous session with the following deliverables:
- INTEGRATION_CONTRACTS_GUIDE.md (~30KB, ~7,400 tokens)
- TASKS-000_INTEGRATION_CONTRACTS_CHECKLIST.md (~15KB, ~3,700 tokens)
- Updated TASKS-TEMPLATE.md with Integration Contracts section
- Updated CLAUDE.md with Integration Contracts Strategy section

### Key Decisions

1. **Terminology Change**: "Integration Contracts" → "Implementation Contracts"
   - **Rationale**: Better emphasizes purpose (parallel implementation), distinguishes from Layer 9 CTR (API Integration Contracts)

2. **Traceability Tag**: `@icon` (4 characters - concise!)
   - **Format**: `@icon: TASKS-XXX:ContractName`
   - **Optional Role**: `@icon-role: provider|consumer`

3. **File Prefix**: `ICON-NNN_{slug}.md` for standalone contracts
   - **When to create**: 5+ consumers, >500 lines, platform-level interfaces
   - **Default**: Embed contracts in TASKS files (most common)

4. **SDD Workflow Integration**:
   - Implementation contracts belong to **Layer 11 (TASKS)**
   - CTR (Layer 9) remains for external API contracts
   - Clear distinction maintained in all documentation

### Completed Tasks (Previous Session)

- [x] Created INTEGRATION_CONTRACTS_GUIDE.md with comprehensive documentation
- [x] Created TASKS-000_INTEGRATION_CONTRACTS_CHECKLIST.md
- [x] Updated TASKS-TEMPLATE.md with Integration Contracts section
- [x] Updated CLAUDE.md with Integration Contracts Strategy section
- [x] Validated all cross-references, metadata, and code examples
- [x] Analyzed SDD workflow for proper placement of contracts
- [x] Designed @icon tag and ICON prefix naming convention

---

## Task List

### Phase 1: Rename Framework Files ✅ READY

#### Task 1.1: Rename Documentation Files
- [ ] Rename `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/INTEGRATION_CONTRACTS_GUIDE.md`
  - New name: `IMPLEMENTATION_CONTRACTS_GUIDE.md`
- [ ] Rename `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/TASKS-000_INTEGRATION_CONTRACTS_CHECKLIST.md`
  - New name: `TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md`

#### Task 1.2: Update File Content - Terminology
- [ ] **IMPLEMENTATION_CONTRACTS_GUIDE.md** (~50 occurrences):
  - Update YAML frontmatter title
  - Update H1 header
  - Find/replace "Integration Contract" → "Implementation Contract"
  - Update all section headers
- [ ] **TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md** (~20 occurrences):
  - Update YAML frontmatter title
  - Update H1 header
  - Find/replace terminology
- [ ] **TASKS-TEMPLATE.md** (~15 occurrences):
  - Section: "Integration Contracts" → "Implementation Contracts"
  - Update all references within section
  - Update reference link to new filename
- [ ] **/home/ya/.claude/CLAUDE.md** (~10 occurrences):
  - Section: "Integration Contracts Strategy" → "Implementation Contracts Strategy"
  - Update all references
  - Update reference link to new filename

### Phase 2: Implement @icon Tag System ✅ READY

#### Task 2.1: Add @icon Tag Documentation
- [ ] **IMPLEMENTATION_CONTRACTS_GUIDE.md**:
  - Add Section 12: "Traceability with @icon Tags"
  - Document tag format: `@icon: TASKS-XXX:ContractName`
  - Document optional `@icon-role: provider|consumer`
  - Provide usage examples in TASKS, Code, IPLAN contexts
- [ ] **TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md**:
  - Add Section 11: "@icon Tag Quick Reference"
  - Provider/consumer examples
  - Standalone ICON file reference
- [ ] **TASKS-TEMPLATE.md**:
  - Add @icon tag examples in Traceability section
  - Show provider and consumer usage patterns
- [ ] **CLAUDE.md**:
  - Add @icon tag reference to Implementation Contracts Strategy
  - Update reference to guide

### Phase 3: Create ICON Artifact Support ✅ READY

#### Task 3.1: Create ICON Directory Structure
- [ ] Create directory: `/opt/data/docs_flow_framework/ai_dev_flow/ICON/`
- [ ] Create `ICON-TEMPLATE.md` with full contract template structure
- [ ] Create `ICON-000_index.md` with contract registry
- [ ] Create `ICON/README.md` with usage guidelines
- [ ] Create `ICON_CREATION_RULES.md` with decision criteria

#### Task 3.2: Add ICON File Guidance to Contracts Documentation
- [ ] **IMPLEMENTATION_CONTRACTS_GUIDE.md**:
  - Add Section 13: "Standalone ICON Files (Optional)"
  - Document when to create ICON vs embed in TASKS
  - Add decision matrix table
  - Reference ICON-TEMPLATE.md
- [ ] **TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md**:
  - Add ICON file decision criteria
  - Add file naming examples

### Phase 4: Update SDD Workflow Documentation ✅ READY

#### Task 4.1: Update TRACEABILITY.md
- [ ] Add `@icon:` tag section under Layer 11
- [ ] Document format: `@icon: TASKS-XXX:ContractName` or `@icon: ICON-XXX:ContractName`
- [ ] Document optional `@icon-role:` tag
- [ ] Show relationship to `@ctr:` (Layer 9 API contracts)
- [ ] Provide comprehensive examples

#### Task 4.2: Update SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
- [ ] Add Section 11.5: "Define Implementation Contracts [WITHIN TASKS]"
- [ ] Document when to create implementation contracts
- [ ] List 5 contract types
- [ ] Embedded vs standalone decision criteria
- [ ] Reference IMPLEMENTATION_CONTRACTS_GUIDE.md

#### Task 4.3: Update ID_NAMING_STANDARDS.md
- [ ] Add ICON section with format specification
- [ ] Provide examples: `ICON-001_gateway_connector_protocol.md`
- [ ] Document location: `ai_dev_flow/ICON/` or `docs/ICON/`
- [ ] Note: Most contracts should be embedded in TASKS

#### Task 4.4: Update CTR-000_index.md (Optional)
- [ ] Populate empty index with contract registry structure
- [ ] Add distinction between CTR (external APIs) and ICON (internal implementation)
- [ ] Reference Implementation Contracts framework

### Phase 5: Validation & Quality Assurance ✅ READY

#### Task 5.1: Cross-Reference Validation
- [ ] Verify all links to renamed files resolve correctly
- [ ] Check for broken markdown links
- [ ] Validate YAML frontmatter syntax
- [ ] Verify terminology consistency

#### Task 5.2: Content Validation
- [ ] Grep for remaining "Integration Contract" references (should be zero)
- [ ] Verify @icon tag examples are consistent
- [ ] Validate ICON file naming examples
- [ ] Check code block syntax

#### Task 5.3: Documentation Review
- [ ] Review distinction between CTR and ICON is clear
- [ ] Verify Layer 11 positioning is documented
- [ ] Check that embedded vs standalone guidance is clear
- [ ] Validate all cross-references between documents

---

## Implementation Guide

### Prerequisites

**Files to Modify** (existing):
1. `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/INTEGRATION_CONTRACTS_GUIDE.md`
2. `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/TASKS-000_INTEGRATION_CONTRACTS_CHECKLIST.md`
3. `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/TASKS-TEMPLATE.md`
4. `/home/ya/.claude/CLAUDE.md`

**Files to Create** (new):
1. `/opt/data/docs_flow_framework/ai_dev_flow/ICON/` directory
2. `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON-TEMPLATE.md`
3. `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON-000_index.md`
4. `/opt/data/docs_flow_framework/ai_dev_flow/ICON/README.md`
5. `/opt/data/docs_flow_framework/ai_dev_flow/ICON/ICON_CREATION_RULES.md`

**Files to Update** (SDD workflow):
1. `/opt/data/ibmcp/ai_dev_flow/TRACEABILITY.md`
2. `/opt/data/ibmcp/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
3. `/opt/data/ibmcp/ai_dev_flow/ID_NAMING_STANDARDS.md`
4. `/opt/data/ibmcp/docs/CONTRACTS/CTR-000_index.md` (optional)

**Tools Required**:
- File rename capability
- Text editor for find/replace
- Bash for validation commands

### Execution Steps

#### Step 1: Rename Files (5 minutes)
```bash
cd /opt/data/docs_flow_framework/ai_dev_flow/TASKS

# Rename guide
mv INTEGRATION_CONTRACTS_GUIDE.md IMPLEMENTATION_CONTRACTS_GUIDE.md

# Rename checklist
mv TASKS-000_INTEGRATION_CONTRACTS_CHECKLIST.md TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md

# Verify renames
ls -la | grep -E "(IMPLEMENTATION_CONTRACTS|TASKS-000)"
```

#### Step 2: Update Terminology in Files (30 minutes)

For each file, perform find/replace:
- "Integration Contracts" → "Implementation Contracts" (title case)
- "integration contracts" → "implementation contracts" (lowercase)
- "Integration Contract" → "Implementation Contract" (singular)

Update cross-reference links to point to new filenames.

**Files to update**:
1. IMPLEMENTATION_CONTRACTS_GUIDE.md
2. TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md
3. TASKS-TEMPLATE.md
4. CLAUDE.md

#### Step 3: Add @icon Tag Sections (20 minutes)

**IMPLEMENTATION_CONTRACTS_GUIDE.md** - Add Section 12:
```markdown
## 12. Traceability with @icon Tags

### Tag Format
**Format**: `@icon: TASKS-XXX:ContractName`
**Optional Role**: `@icon-role: provider|consumer`

[Include examples and usage patterns]
```

**TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md** - Add Section 11:
```markdown
## 11. Traceability Tags Quick Reference

### @icon Tag Format
[Include provider/consumer examples]
```

**TASKS-TEMPLATE.md** - Add to Traceability section:
```markdown
@icon: TASKS-001:IBGatewayConnector
@icon-role: provider
```

#### Step 4: Create ICON Artifact Structure (20 minutes)

```bash
# Create ICON directory
mkdir -p /opt/data/docs_flow_framework/ai_dev_flow/ICON

# Create template files (use Write tool)
# - ICON-TEMPLATE.md
# - ICON-000_index.md
# - README.md
# - ICON_CREATION_RULES.md
```

#### Step 5: Add ICON Documentation to Contracts Guide (15 minutes)

**IMPLEMENTATION_CONTRACTS_GUIDE.md** - Add Section 13:
```markdown
## 13. Standalone ICON Files (Optional)

### When to Create ICON Files
[Decision criteria]

### ICON File Naming
Format: `ICON-NNN_{descriptive_slug}.md`

### Embedded vs Standalone Decision Matrix
[Table showing when to use each approach]
```

#### Step 6: Update SDD Workflow Documentation (10 minutes)

**TRACEABILITY.md** - Add @icon section:
```markdown
### @icon: Implementation Contracts (Layer 11)
[Full documentation of tag format and usage]
```

**SPEC_DRIVEN_DEVELOPMENT_GUIDE.md** - Add Section 11.5:
```markdown
### 11.5. Define Implementation Contracts [WITHIN TASKS]
[When to create, contract types, traceability]
```

**ID_NAMING_STANDARDS.md** - Add ICON section:
```markdown
### ICON (Implementation Contracts) - OPTIONAL
[Format, examples, when to use]
```

#### Step 7: Validation (10 minutes)

```bash
# Check for remaining old terminology
grep -r "Integration Contract" \
  /opt/data/docs_flow_framework/ai_dev_flow/TASKS/*.md \
  /home/ya/.claude/CLAUDE.md

# Should return: 0 matches

# Verify renamed files exist
ls -la /opt/data/docs_flow_framework/ai_dev_flow/TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md
ls -la /opt/data/docs_flow_framework/ai_dev_flow/TASKS/TASKS-000_IMPLEMENTATION_CONTRACTS_CHECKLIST.md

# Verify ICON directory created
ls -la /opt/data/docs_flow_framework/ai_dev_flow/ICON/

# Check for broken links (manual review)
```

### Verification

**After Step 1 (Renames)**:
- ✅ Two files renamed successfully
- ✅ Original files no longer exist
- ✅ New filenames follow conventions

**After Step 2 (Terminology)**:
- ✅ No "Integration Contract" references remain
- ✅ All "Implementation Contract" references correct
- ✅ Cross-reference links updated

**After Step 3 (@icon Tags)**:
- ✅ @icon tag format documented in guide
- ✅ @icon examples in checklist
- ✅ @icon examples in template
- ✅ Role indicators documented

**After Step 4 (ICON Structure)**:
- ✅ ICON directory exists
- ✅ ICON-TEMPLATE.md created
- ✅ ICON-000_index.md created
- ✅ README and rules files created

**After Step 5 (ICON Documentation)**:
- ✅ Section 13 added to guide
- ✅ Decision criteria documented
- ✅ Examples provided

**After Step 6 (SDD Workflow)**:
- ✅ TRACEABILITY.md includes @icon
- ✅ SPEC_DRIVEN_DEVELOPMENT_GUIDE.md Section 11.5 added
- ✅ ID_NAMING_STANDARDS.md includes ICON

**After Step 7 (Validation)**:
- ✅ No broken links
- ✅ Terminology consistent
- ✅ All files validated

---

## Key Concepts

### Terminology Distinction

| Term | Layer | Purpose | Files |
|------|-------|---------|-------|
| **Implementation Contracts** | 11 (TASKS) | Enable parallel implementation | Embedded in TASKS or standalone ICON |
| **CTR (API Contracts)** | 9 (Interface) | External service interfaces | Dual-file (.md + .yaml) |

### @icon Tag Usage

**Provider Example**:
```markdown
@icon: TASKS-001:IBGatewayConnector
@icon: TASKS-001:GatewayConnectionError
@icon-role: provider
```

**Consumer Example**:
```markdown
@icon: TASKS-001:IBGatewayConnector
@icon-role: consumer
```

**In Code**:
```python
"""
@tasks: TASKS-002
@icon: TASKS-001:IBGatewayConnector
@icon-role: consumer
"""
```

### ICON File Decision

**Create ICON-NNN file when**:
- 5+ consuming TASKS
- >500 lines documentation
- Platform-level interface
- Independent versioning

**Embed in TASKS when**:
- 2-4 consuming TASKS
- <200 lines documentation
- Feature-specific contract
- Simple lifecycle

---

## References

### Created in Previous Session
- `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/INTEGRATION_CONTRACTS_GUIDE.md` (to be renamed)
- `/opt/data/docs_flow_framework/ai_dev_flow/TASKS/TASKS-000_INTEGRATION_CONTRACTS_CHECKLIST.md` (to be renamed)
- Updated TASKS-TEMPLATE.md with Integration Contracts section
- Updated CLAUDE.md with Integration Contracts Strategy

### To Be Updated
- `/opt/data/ibmcp/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- `/opt/data/ibmcp/ai_dev_flow/TRACEABILITY.md`
- `/opt/data/ibmcp/ai_dev_flow/ID_NAMING_STANDARDS.md`

### To Be Created
- `/opt/data/docs_flow_framework/ai_dev_flow/ICON/` directory structure
- ICON-TEMPLATE.md, ICON-000_index.md, README.md, ICON_CREATION_RULES.md

### Documentation
- Original work plan: `/opt/data/docs_flow_framework/work_plans/integration-contracts-framework_20251124_201908.md`
- Global instructions: `/home/ya/.claude/CLAUDE.md`

---

## Estimated Effort

**Total Time**: ~90 minutes

- **Phase 1** (Renames): 5 minutes
- **Phase 2** (Terminology): 30 minutes
- **Phase 3** (@icon Tags): 20 minutes
- **Phase 4** (ICON Structure): 20 minutes
- **Phase 5** (ICON Documentation): 15 minutes
- **Phase 6** (SDD Workflow): 10 minutes
- **Phase 7** (Validation): 10 minutes

---

## Success Criteria

✅ All files renamed with no broken references
✅ Terminology consistently updated to "Implementation Contracts"
✅ @icon tag fully documented and exemplified
✅ ICON artifact structure created with templates
✅ SDD workflow documentation updated with Layer 11 positioning
✅ Clear distinction maintained between ICON and CTR
✅ All cross-references validated
✅ No broken links or syntax errors

---

## Notes

- **Plan mode was active** during this session - no files were modified
- All analysis and planning complete - ready for execution
- Framework already validated in previous session (token counts, code syntax, metadata)
- This plan focuses purely on renaming and @icon tag integration
- Maintains backward compatibility - no breaking changes to existing code

---

## Next Steps

To implement this plan:

1. **Exit plan mode** and confirm execution
2. **Run Phase 1**: Rename files
3. **Run Phase 2-7**: Follow execution steps sequentially
4. **Validate**: Run verification commands
5. **Commit**: Create git commit with changes

Or in a new context:
```bash
cat /opt/data/docs_flow_framework/work_plans/implementation-contracts-framework_20251125_100224.md
```
Then say: "Implement this plan"
