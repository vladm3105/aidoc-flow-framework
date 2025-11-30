# doc-iplan - Quick Reference

**Skill ID:** doc-iplan
**Layer:** 12 (Implementation Plans)
**Purpose:** Convert TASKS into session-based bash command execution plans

## Quick Start

```bash
# Invoke skill
skill: "doc-iplan"

# Common requests
- "Create implementation plan from TASKS-001"
- "Generate executable session plan"
- "Document Layer 12 bash commands for tasks"
```

## What This Skill Does

1. Convert TASKS into executable bash commands
2. Organize into session-based execution plan
3. Provide validation commands per session
4. Document rollback procedures
5. Support copy-paste execution

## Output Location

```
docs/IPLAN/IPLAN-NNN_{slug}.md
```

## File Naming Convention

`IPLAN-NNN_{descriptive_slug}.md`

Examples:
- `IPLAN-001_gateway_connection.md`
- `IPLAN-002_trade_validation.md`

## Session Format

```markdown
### Session 1: Project Setup (Estimated: 1.5 hours)

**Tasks**: TASK-001-001, TASK-001-002

**Commands**:
```bash
# TASK-001-001: Initialize Project Structure
mkdir -p src/controllers src/services
touch src/services/validator.py
```

**Validation**:
```bash
test -f src/services/validator.py && echo "✓ Created"
```

**Rollback**:
```bash
rm -rf src/
```
```

## Typical Sessions (8)

1. Project Setup, 2. Data Models, 3. Business Logic, 4. API Layer
5. Error Handling, 6. Configuration, 7. Testing, 8. Deployment

## Required Frontmatter

```yaml
---
tags:
  - implementation-plan
  - layer-12-artifact  # REQUIRED for validation
  - active
title: "IPLAN-NNN: Description"
---
```

## Upstream/Downstream

```
BRD through TASKS → IPLAN → Code (Layer 13)
```

## Quick Validation

- [ ] File naming: IPLAN-NNN_{slug}.md
- [ ] Frontmatter includes `layer-12-artifact` tag
- [ ] Sessions organized by task groups
- [ ] Bash commands are copy-paste ready
- [ ] Validation commands for each session
- [ ] Rollback procedures documented
- [ ] Cumulative tags: @brd through @tasks (9-11 tags)

## Template Location

```
ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md
```

## Related Skills

- `doc-tasks` - Task breakdown (upstream)
- Code Implementation (Layer 13 - downstream)

## Tag Format

Use `@iplan: IPLAN-001` (ID only, not full filename)
