# Implementation Plan - Schema-Template Enhancement

**Created**: 2025-11-30 12:22:13 EST
**Status**: Ready for Implementation

## Objective

Improve the relationship between document templates and schemas in the SDD framework by adding explicit cross-references, version synchronization, and unified validation tooling.

## Context

**Problem**: Templates (`{TYPE}-TEMPLATE.md`) and schemas (`{TYPE}_SCHEMA.yaml`) exist separately, leading to potential confusion and drift.

**Decision**: Keep separate files (templates for humans/AI authoring, schemas for machine validation) but add explicit cross-references and tooling.

**Key Points**:
- Schemas are 3,000-5,000+ lines each - too complex to embed
- BRD does not need a schema (Layer 1 entry point, human-authored)
- IMPL is missing a schema and needs one created
- Clean break migration - no backward compatibility needed

## Task List

### Pending
- [ ] Phase 1: Add cross-references to all 12 templates (schema_reference, schema_version fields)
- [ ] Phase 2: Add references section to all 10 existing schemas
- [ ] Phase 3: Create IMPL_SCHEMA.yaml based on IMPL-TEMPLATE.md
- [ ] Phase 4: Create scripts/validate_schema_sync.py
- [ ] Phase 5: Create scripts/validate_artifact.py
- [ ] Phase 6: Create ai_dev_flow/SCHEMA_TEMPLATE_GUIDE.md documentation

## Implementation Guide

### Prerequisites
- Access to `/opt/data/docs_flow_framework/ai_dev_flow/` directory
- Understanding of existing schema structure (use PRD_SCHEMA.yaml as reference)

### Phase 1: Template Cross-References

Add to each template's YAML frontmatter:
```yaml
custom_fields:
  # ... existing fields ...
  schema_reference: "{TYPE}_SCHEMA.yaml"  # or "none" for BRD
  schema_version: "1.0"
```

Update Document Authority block in each template:
```markdown
> **Document Authority**: This is the PRIMARY STANDARD for {TYPE} structure.
> - **Schema**: `{TYPE}_SCHEMA.yaml v1.0` - Validation rules
> - **Creation Rules**: `{TYPE}_CREATION_RULES.md` - Usage guidance
```

**Files to modify**:
- `ai_dev_flow/ADR/ADR-TEMPLATE.md`
- `ai_dev_flow/BDD/BDD-TEMPLATE.feature`
- `ai_dev_flow/BRD/BRD-TEMPLATE.md` (schema_reference: "none")
- `ai_dev_flow/CTR/CTR-TEMPLATE.md`
- `ai_dev_flow/EARS/EARS-TEMPLATE.md`
- `ai_dev_flow/IMPL/IMPL-TEMPLATE.md`
- `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md`
- `ai_dev_flow/PRD/PRD-TEMPLATE.md`
- `ai_dev_flow/REQ/REQ-TEMPLATE.md`
- `ai_dev_flow/SPEC/SPEC-TEMPLATE.md`
- `ai_dev_flow/SYS/SYS-TEMPLATE.md`
- `ai_dev_flow/TASKS/TASKS-TEMPLATE.md`

### Phase 2: Schema Cross-References

Add to top of each schema file:
```yaml
schema_version: "1.0"
artifact_type: {TYPE}
layer: {N}
last_updated: "2025-11-30"

references:
  template: "{TYPE}-TEMPLATE.md"
  creation_rules: "{TYPE}_CREATION_RULES.md"
```

**Files to modify**:
- `ai_dev_flow/ADR/ADR_SCHEMA.yaml`
- `ai_dev_flow/BDD/BDD_SCHEMA.yaml`
- `ai_dev_flow/CTR/CTR_SCHEMA.yaml`
- `ai_dev_flow/EARS/EARS_SCHEMA.yaml`
- `ai_dev_flow/IPLAN/IPLAN_SCHEMA.yaml`
- `ai_dev_flow/PRD/PRD_SCHEMA.yaml`
- `ai_dev_flow/REQ/REQ_SCHEMA.yaml`
- `ai_dev_flow/SPEC/SPEC_SCHEMA.yaml`
- `ai_dev_flow/SYS/SYS_SCHEMA.yaml`
- `ai_dev_flow/TASKS/TASKS_SCHEMA.yaml`

### Phase 3: Create IMPL_SCHEMA.yaml

Based on IMPL-TEMPLATE.md structure:
- Layer 8 artifact
- Upstream: REQ
- Downstream: CTR, SPEC, TASKS
- Use PRD_SCHEMA.yaml as structural reference

### Phase 4: Create validate_schema_sync.py

Script to verify template schema_version matches schema schema_version for all types.

### Phase 5: Create validate_artifact.py

Unified document validator that:
- Auto-detects schema from document's schema_reference field
- Runs validation rules from schema
- Returns structured errors/warnings

### Phase 6: Create Documentation

Create `ai_dev_flow/SCHEMA_TEMPLATE_GUIDE.md` explaining:
1. Purpose of separation
2. Cross-reference conventions
3. Version synchronization rules
4. When to update schema vs template
5. Validation tooling usage

### Verification

- [ ] All 12 templates have schema_reference and schema_version fields
- [ ] All 11 schemas have references section (BRD excluded)
- [ ] IMPL_SCHEMA.yaml created and valid
- [ ] validate_schema_sync.py passes for all types
- [ ] validate_artifact.py validates documents correctly
- [ ] Documentation complete

## References

- Plan file: `/home/ya/.claude/plans/purrfect-hopping-valley.md`
- Reference schema: `ai_dev_flow/PRD/PRD_SCHEMA.yaml`
- Reference template: `ai_dev_flow/PRD/PRD-TEMPLATE.md`
