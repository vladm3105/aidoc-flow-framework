# Implementation Plan - Create Artifact Schema Files

**Created**: 2025-11-29 16:35:30 EST
**Status**: Ready for Implementation

## Objective

Create `_SCHEMA.yaml` validation schema files for Tier 1 (4 files) and Tier 2 (5 files) SDD artifact types, following the established pattern from `EARS_SCHEMA.yaml`. Update related documentation including README and Claude skills.

## Context

### Background
- `EARS_SCHEMA.yaml` is the only existing schema file in the framework
- It provides comprehensive validation rules for EARS documents (Layer 3)
- Other artifact types rely on templates and shell validation scripts but lack formal schemas
- Schemas enable automated validation with standardized error codes

### Schema Purpose
Each schema file defines:
- YAML frontmatter requirements (required/optional fields)
- Document structure requirements (sections, headings)
- Content patterns specific to the artifact type
- Validation rules with severity levels (error/warning)
- Traceability requirements (upstream/downstream)
- Error message codes (E001-ENNN, W001-WNNN)

### Reference File
- Template: `/opt/data/docs_flow_framework/ai_dev_flow/EARS/EARS_SCHEMA.yaml`

## Task List

### Completed
- [x] Review EARS_SCHEMA.yaml structure and patterns
- [x] Analyze all 12 artifact types for schema value
- [x] Prioritize into Tier 1 (High) and Tier 2 (Medium)
- [x] Create implementation plan

### Pending

#### Phase 1: Tier 1 Schemas (High Priority)
- [ ] Create `ai_dev_flow/BDD/BDD_SCHEMA.yaml` - Gherkin Given/When/Then syntax
- [ ] Create `ai_dev_flow/REQ/REQ_SCHEMA.yaml` - 12 sections, SPEC-Ready scoring
- [ ] Create `ai_dev_flow/CTR/CTR_SCHEMA.yaml` - OpenAPI/JSON Schema validation
- [ ] Create `ai_dev_flow/SPEC/SPEC_SCHEMA.yaml` - YAML structure, 12 sections

#### Phase 2: Tier 2 Schemas (Medium Priority)
- [ ] Create `ai_dev_flow/PRD/PRD_SCHEMA.yaml` - FR/NFR numbering format
- [ ] Create `ai_dev_flow/ADR/ADR_SCHEMA.yaml` - Context-Decision-Consequences
- [ ] Create `ai_dev_flow/SYS/SYS_SCHEMA.yaml` - FR-NNN/NFR-NNN IDs
- [ ] Create `ai_dev_flow/TASKS/TASKS_SCHEMA.yaml` - TASK-{SPEC}-{N} format
- [ ] Create `ai_dev_flow/IPLAN/IPLAN_SCHEMA.yaml` - Session format

#### Phase 3: Documentation Updates
- [ ] Update `ai_dev_flow/README.md` - Add schema file references
- [ ] Update `.claude/skills/doc-validator/SKILL.md` - Reference new schemas
- [ ] Consider updating individual doc-* skills if needed

### Notes
- Each schema should follow EARS_SCHEMA.yaml structure
- Use layer-specific patterns (e.g., BDD uses Gherkin, REQ uses 12-section format)
- Include error codes unique to each artifact type
- Maintain traceability chain references

## Implementation Guide

### Prerequisites
- Read EARS_SCHEMA.yaml to understand the template structure
- Read each artifact type's TEMPLATE file for pattern requirements
- Review existing validation scripts for validation logic to incorporate

### Schema Structure Template
```yaml
# {TYPE}_SCHEMA.yaml v1.0
schema_version: "1.0"
artifact_type: {TYPE}
layer: {N}
last_updated: "YYYY-MM-DD"

metadata:
  required_custom_fields: {...}
  optional_custom_fields: {...}
  required_tags: [...]
  forbidden_tag_patterns: [...]

structure:
  required_sections: [...]
  document_control: {...}
  section_numbering: {...}

{type}_patterns:  # Type-specific patterns
  pattern_types: {...}
  required_statement_components: [...]

validation_rules:
  metadata: [...]
  structure: [...]
  content: [...]

traceability:
  upstream: {...}
  downstream: {...}

error_messages:
  E001: "..."
  W001: "..."
```

### Execution Steps

1. **Read reference files** for each artifact type:
   - `ai_dev_flow/{TYPE}/{TYPE}-TEMPLATE.md` (or .yaml/.feature)
   - `ai_dev_flow/{TYPE}/{TYPE}_CREATION_RULES.md`
   - `ai_dev_flow/{TYPE}/{TYPE}_VALIDATION_RULES.md`

2. **Create Tier 1 schemas** (BDD, REQ, CTR, SPEC):
   - BDD: Focus on Gherkin syntax (Given/When/Then/And)
   - REQ: Focus on 12 sections, SPEC-Ready Score calculation
   - CTR: Focus on OpenAPI 3.0 / JSON Schema formats
   - SPEC: Focus on YAML structure, 12 required sections

3. **Create Tier 2 schemas** (PRD, ADR, SYS, TASKS, IPLAN):
   - PRD: FR/NFR numbering (FR-001, NFR-001)
   - ADR: Status, Context, Decision, Consequences sections
   - SYS: FR-NNN/NFR-NNN ID format
   - TASKS: TASK-{SPEC-ID}-{Number} format
   - IPLAN: Session format with bash commands

4. **Update documentation**:
   - Add schema references to ai_dev_flow/README.md
   - Update doc-validator skill to reference schemas

### Verification
- Each schema file is valid YAML (parseable)
- Schema follows EARS_SCHEMA.yaml structure
- All required sections present
- Error codes are unique per schema
- Traceability references correct upstream/downstream

## References

- Reference schema: `/opt/data/docs_flow_framework/ai_dev_flow/EARS/EARS_SCHEMA.yaml`
- Template files: `/opt/data/docs_flow_framework/ai_dev_flow/{TYPE}/{TYPE}-TEMPLATE.*`
- Previous plan: `/home/ya/.claude/plans/polymorphic-swinging-dragon.md`

## Artifact Type Quick Reference

| Type | Layer | Key Patterns | Upstream | Downstream |
|------|-------|--------------|----------|------------|
| BDD | 4 | Given/When/Then | PRD, EARS | SYS, REQ |
| REQ | 7 | 12 sections, SPEC-Ready | SYS, ADR | CTR, SPEC |
| CTR | 9 | OpenAPI, JSON Schema | REQ, IMPL | SPEC |
| SPEC | 10 | YAML, 12 sections | REQ, CTR | TASKS |
| PRD | 2 | FR/NFR lists | BRD | EARS, BDD |
| ADR | 5 | Context-Decision | BRD, PRD | SYS, REQ |
| SYS | 6 | FR-NNN/NFR-NNN | ADR, BDD | REQ |
| TASKS | 11 | TASK-XXX-NNN | SPEC | IPLAN |
| IPLAN | 12 | Sessions, bash | TASKS | Code |
