# doc-tasks - Quick Reference

**Skill ID:** doc-tasks
**Layer:** 11 (Task Breakdown)
**Purpose:** Decompose SPEC into AI-structured TODO tasks

## Quick Start

```bash
# Invoke skill
skill: "doc-tasks"

# Common requests
- "Create task breakdown from SPEC-001"
- "Decompose specification into actionable tasks"
- "Generate Layer 11 TODO tasks for implementation"
```

## What This Skill Does

1. Break SPEC into actionable tasks by phase
2. Define task dependencies and effort estimates
3. Create dependencies graph (Mermaid)
4. Calculate effort summary by phase
5. Document implementation contracts

## Output Location

```
ai_dev_flow/TASKS/TASKS-NNN_{slug}.md
```

## Task Format

```markdown
**TASK-001-003: Implement DataRequest Model**
- **Action**: Create Pydantic model per CTR-001 schema
- **Files to Modify**: `src/models/data_request.py`
- **Dependencies**: TASK-001-002
- **Estimated Effort**: 1 hour
- **SPEC Reference**: SPEC-001:interfaces.data_models
- **Success Criteria**: Model validates, unit tests pass
```

## Task ID Format

`TASK-{SPEC-ID}-{Task-Number}` → e.g., `TASK-001-003`

## Typical Phases (8)

1. Project Setup, 2. Data Models, 3. Business Logic, 4. API Layer
5. Error Handling, 6. Configuration, 7. Testing, 8. Deployment

## Required Fields per Task

- Task ID, Title, Action
- Files to Create/Modify
- Dependencies (or "None")
- Estimated Effort
- SPEC Reference
- Success Criteria

## Upstream/Downstream

```
BRD through SPEC → TASKS → IPLAN, Code
```

## Quick Validation

- [ ] Tasks organized into phases
- [ ] Each task has TASK-{SPEC-ID}-{Number} ID
- [ ] Dependencies identified
- [ ] Effort estimates provided
- [ ] SPEC references included
- [ ] Dependencies Graph (Mermaid) created
- [ ] Section 8: Implementation Contracts completed
- [ ] Cumulative tags: @brd through @spec (8-10 tags)

## Template Location

```
ai_dev_flow/TASKS/TASKS-TEMPLATE.md
```

## Related Skills

- `doc-spec` - Technical specifications (upstream)
- `doc-iplan` - Implementation plans (downstream)
