# Implementation Plan - Metadata Tagging Framework Rollout

**Created**: 2025-11-23 16:32:07 EST
**Status**: Ready for Implementation

## Objective

Implement comprehensive metadata tagging across ~100 files in the AI Dev Flow framework:
- 29 Claude skills (SKILL.md files)
- 70+ framework documents (guides, standards, rules, READMEs)
- 12+ templates (with example metadata)
- 3 new validation scripts

## Context

### User Requirements
1. Full 5-phase implementation (all files)
2. Create validation infrastructure first (validate_metadata.py, bulk_add_metadata.sh, pre-commit hook)
3. Use full metadata enhancement for skills (all custom fields)
4. Include example metadata in template files
5. Update CLAUDE.md with metadata standards section for future consistency
6. Ask user when metadata tags are unclear or ambiguous

### Metadata Framework
- **Reference Guides**:
  - `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_TAGGING_GUIDE.md`
  - `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_QUICK_REFERENCE.md`

- **Three-Tier Classification**:
  1. Primary (ai-agent-primary, recommended-approach)
  2. Fallback (traditional-fallback, reference-implementation)
  3. Shared (shared-architecture, required-both-approaches)

- **Key Validation Requirements**:
  - YAML frontmatter syntax
  - Required fields: title, tags, architecture_approach, priority
  - Bidirectional cross-references (primary ↔ fallback)
  - Tag taxonomy compliance
  - Agent ID uniqueness

### Important Constraints
- Do not add metadata to archived content
- Templates get example metadata (marked as examples)
- Skills must remain backward compatible
- Validate after each phase before proceeding

## Task List

### Phase 0: Update Global Instructions
- [ ] Add "Metadata Standards" section to `/home/ya/.claude/CLAUDE.md`
- [ ] Include quick reference for common tags
- [ ] Document decision protocol for unclear metadata
- [ ] Commit CLAUDE.md changes

### Phase 1: Validation Infrastructure (4-6 hours)
- [ ] Create `scripts/validate_metadata.py` with full validation logic
- [ ] Create `scripts/bulk_add_metadata.sh` for batch operations
- [ ] Create pre-commit hook for automatic validation
- [ ] Test validation scripts on metadata guide files
- [ ] Commit validation infrastructure

### Phase 2: Core Framework Documents (8-12 hours)
- [ ] Add metadata to METADATA_TAGGING_GUIDE.md
- [ ] Add metadata to METADATA_QUICK_REFERENCE.md
- [ ] Add metadata to AI_ASSISTANT_RULES.md
- [ ] Add metadata to TOOL_OPTIMIZATION_GUIDE.md
- [ ] Add metadata to ID_NAMING_STANDARDS.md
- [ ] Add metadata to TRACEABILITY.md
- [ ] Add metadata to SPEC_DRIVEN_DEVELOPMENT_GUIDE.md
- [ ] Add metadata to all 12 index files ({TYPE}-000_index.md)
- [ ] Run validation on all Phase 2 files
- [ ] Commit Phase 2 changes

### Phase 3: Claude Skills Enhancement (16-20 hours)
- [ ] Update 13 core SDD workflow skills (doc-flow through doc-iplan)
- [ ] Test skill loading after core skills updates
- [ ] Update 4 quality assurance skills
- [ ] Update 6 utility skills
- [ ] Update 6 domain-specific skills
- [ ] Run validation on all 29 skills
- [ ] Test complete skill loading compatibility
- [ ] Commit Phase 3 changes

### Phase 4: Creation/Validation Rules (12-16 hours)
- [ ] Add metadata to 12 creation rules files
- [ ] Add metadata to 12 validation rules files
- [ ] Validate consistency across artifact types
- [ ] Run validation on all Phase 4 files
- [ ] Commit Phase 4 changes

### Phase 5: Supporting Documentation (8-12 hours)
- [ ] Add metadata to 12 README files
- [ ] Add metadata to 10 additional guide files
- [ ] Add example metadata to 12+ template files
- [ ] Add metadata to example documents (optional)
- [ ] Run validation on all Phase 5 files
- [ ] Commit Phase 5 changes

### Final Validation
- [ ] Run validation across all 100+ files
- [ ] Verify no duplicate agent IDs
- [ ] Check bidirectional cross-references
- [ ] Test skill loading one final time
- [ ] Generate compliance report
- [ ] Create final summary commit

## Implementation Guide

### Prerequisites
- Git working directory clean (or committed)
- Python 3.x installed for validation scripts
- Access to both project directories:
  - `/opt/data/docs_flow_framework/` (framework)
  - `/home/ya/.claude/CLAUDE.md` (global config)

### Execution Steps

#### Phase 0: CLAUDE.md Update
1. Read `/home/ya/.claude/CLAUDE.md`
2. Add new "Metadata Standards" section after "Document Naming Conventions"
3. Include: required fields, common tags, decision protocol
4. Commit changes

#### Phase 1: Validation Scripts
1. Create `scripts/validate_metadata.py`:
   - YAML parsing and validation
   - Required fields checking
   - Tag taxonomy validation
   - Bidirectional reference checking
   - Agent ID uniqueness checking
2. Create `scripts/bulk_add_metadata.sh`:
   - Template-based injection
   - Batch processing by file type
3. Create `.git/hooks/pre-commit`:
   - Auto-run validate_metadata.py
4. Test on metadata guide files
5. Fix any issues found
6. Commit scripts

#### Phase 2-5: Document Updates
For each phase:
1. Review file list for that phase
2. Determine appropriate metadata for each file
3. **ASK USER if metadata tags unclear**
4. Apply metadata using consistent format
5. Run `scripts/validate_metadata.py` on updated files
6. Fix validation errors
7. Commit phase changes with descriptive message

### Metadata Templates by File Type

**Skills (Full Enhancement)**:
```yaml
---
name: skill-name
description: Brief description
tags:
  - sdd-workflow
  - layer-N-artifact
  - shared-architecture
  - documentation-skill
custom_fields:
  layer: N
  artifact_type: TYPE
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow|quality-assurance|utility|domain-specific
  upstream_artifacts: []
  downstream_artifacts: []
---
```

**Framework Guides**:
```yaml
---
title: "Guide Title"
tags:
  - framework-guide
  - specific-category
  - shared-architecture
custom_fields:
  document_type: guide|standard|reference
  priority: shared
  development_status: active
  applies_to: [artifact types]
  version: "1.0"
---
```

**Index Files**:
```yaml
---
title: "{TYPE}-000: {TYPE} Index"
tags:
  - index-document
  - layer-N-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: TYPE
  layer: N
  priority: shared
---
```

**Templates (Example Metadata)**:
```yaml
---
# Example metadata - customize for your document
title: "Document Title"
tags:
  - feature-doc
  - ai-agent-primary
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
---
```

### Verification

After each phase:
- ✅ Validation script passes with no errors
- ✅ Required metadata fields present
- ✅ Tags follow taxonomy
- ✅ Cross-references valid (where applicable)
- ✅ Git commit successful

After Phase 3 (Skills):
- ✅ Skills load without errors
- ✅ Backward compatibility maintained

Final verification:
- ✅ All 100+ files have metadata
- ✅ No validation errors across entire framework
- ✅ Compliance report generated
- ✅ Skills fully functional

### Decision Protocol

**When Unclear About Metadata**:
1. Check METADATA_TAGGING_GUIDE.md
2. Check METADATA_QUICK_REFERENCE.md
3. **ASK USER**: "Which metadata tags should apply to [file]?"
   - Classification: primary/fallback/shared
   - Architecture: ai-agent-based vs traditional-8layer
   - Document type and priority

**Before Bulk Operations**:
1. Show example metadata for first file
2. Confirm approach with user
3. Proceed with batch

**When Validation Fails**:
1. Report specific errors
2. Ask user for guidance on resolution
3. Fix and re-validate

## References

### Key Files
- `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_TAGGING_GUIDE.md`
- `/opt/data/docs_flow_framework/ai_dev_flow/METADATA_QUICK_REFERENCE.md`
- `/home/ya/.claude/CLAUDE.md`
- `/opt/data/docs_flow_framework/.claude/skills/` (29 SKILL.md files)

### Research Report
- Comprehensive analysis completed in conversation
- 100+ files identified for updates
- Metadata requirements documented
- Validation requirements defined
- Three-tier classification system understood

### File Inventory Summary

**Skills (29 files)**: adr-roadmap, analytics-flow, charts_flow, code-review, contract-tester, devops-flow, doc-adr, doc-bdd, doc-brd, doc-ctr, doc-ears, doc-flow, doc-impl, doc-iplan, doc-prd, doc-req, doc-spec, doc-sys, doc-tasks, doc-validator, google-adk, mermaid-gen, n8n, project-init, project-mngt, refactor-flow, security-audit, test-automation, trace-check

**Framework Guides (7 files)**: METADATA_TAGGING_GUIDE.md, METADATA_QUICK_REFERENCE.md, AI_ASSISTANT_RULES.md, TOOL_OPTIMIZATION_GUIDE.md, ID_NAMING_STANDARDS.md, TRACEABILITY.md, SPEC_DRIVEN_DEVELOPMENT_GUIDE.md

**Index Files (12 files)**: BRD-000_index.md, PRD-000_index.md, EARS-000_index.md, BDD-000_index.md, ADR-000_index.md, SYS-000_index.md, REQ-000_index.md, IMPL-000_index.md, CTR-000_index.md, SPEC-000_index.md, TASKS-000_index.md, IPLAN-000_index.md

**Creation/Validation Rules (24 files)**: {TYPE}_CREATION_RULES.md and {TYPE}_VALIDATION_RULES.md for each artifact type

**README Files (12 files)**: One for each artifact type directory

**Additional Guides (~10 files)**: PLATFORM_VS_FEATURE_BRD.md, WHEN_TO_CREATE_IMPL.md, DOMAIN_ADAPTATION_GUIDE.md, PROJECT_SETUP_GUIDE.md, COMPLETE_TAGGING_EXAMPLE.md, and others

**Templates (12+ files)**: All {TYPE}-TEMPLATE.* files across artifact types

### Estimated Effort
- Phase 0: 1 hour
- Phase 1: 4-6 hours
- Phase 2: 8-12 hours
- Phase 3: 16-20 hours
- Phase 4: 12-16 hours
- Phase 5: 8-12 hours
- **Total**: 53-73 hours (1.5-2 weeks)

## Notes

### User Decisions Made
- ✅ Scope: All 5 phases (complete implementation)
- ✅ Validation: Create infrastructure first
- ✅ Skills format: Full enhancement with all custom fields
- ✅ Templates: Include example metadata
- ✅ CLAUDE.md: Add metadata standards section

### Implementation Strategy
- Git branch: `feature/metadata-implementation`
- Incremental commits after each phase
- Tag known-good state before starting
- Test skills loading compatibility carefully
- Consult user when metadata tags unclear

### Risk Mitigation
- Validation scripts built before bulk updates
- Skills tested in isolation after Phase 3
- Backward compatibility maintained
- Rollback plan available via Git
- Pre-commit hook prevents invalid metadata

## Status Tracking

**Current Status**: Plan created, ready to begin Phase 0

**Last Updated**: 2025-11-23 16:32:07 EST

**Next Action**: Begin Phase 0 - Update CLAUDE.md with metadata standards section
