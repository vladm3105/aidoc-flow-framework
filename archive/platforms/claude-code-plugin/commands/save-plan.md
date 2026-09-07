---
title: "Save Plan Command"
description: Save current plan and tasks to implementation file
tags:
  - utility
  - workflow
  - active
custom_fields:
  document_type: command
  priority: shared
  development_status: active
---

# Save Plan Command

Extract the current conversation plan and task list, save to a timestamped implementation file, and provide instructions for starting implementation in a new context window.

## Instructions

1. **Extract Current Context**:
   - Identify all TodoWrite entries from the conversation
   - Extract the overall plan or goal statement
   - Capture any important decisions or constraints discussed
   - Note current progress state (what's completed, what's pending)

2. **Determine Work Plans Directory** (resolution order per `docs/CONFIG.md`):
   - **First**, read `work_plans_dir` from `.claude/aidoc-flow.config.yaml`
     (the current home for this setting — see `docs/CONFIG.md`).
   - **Else**, fall back to the legacy `Work Plans Directory` line in
     `.claude/CLAUDE.md`.
   - If neither is set: Use AskUserQuestion to prompt for the directory, then
     store it as `work_plans_dir:` in `.claude/aidoc-flow.config.yaml` (new
     projects prefer the config file; the legacy CLAUDE.md line still works).
   - Create the directory structure if it doesn't exist.

3. **Prompt for Plan Name**:
   - Use AskUserQuestion to ask user for meaningful plan name
   - Example prompts: "implement-user-auth", "refactor-api-layer", "fix-database-performance"
   - Sanitize input: lowercase, replace spaces with hyphens, remove special characters
   - Keep alphanumeric characters and hyphens only

4. **Create Implementation File**:
   - Generate filename format: `{sanitized-plan-name}_YYYYMMDD_HHMMSS.md`
   - Example: `implement-oauth_20260709_143022.md`
   - Save to the work-plans directory resolved in step 2
   - Ensure directory exists before writing

5. **File Structure**:

```markdown
# Implementation Plan - [Brief Title]

**Created**: YYYY-MM-DDTHH:MM:SSZ
**Status**: Ready for Implementation

## Objective

[Clear statement of the overall goal]

## Context

[Important background, decisions, and constraints from the conversation]

## Task List

### Completed
- [x] Task 1
- [x] Task 2

### Pending
- [ ] Task 3 (IN PROGRESS)
- [ ] Task 4
- [ ] Task 5

### Notes
- [Any important notes about specific tasks]

## Implementation Guide

### Prerequisites
- [Required files, tools, or setup]

### Execution Steps
1. [Ordered steps for implementation]
2. [Include file paths and specific commands]

### Verification
- [How to verify each step is complete]
- [Expected outcomes]

## References

- Related files: [List key files]
- Documentation: [Relevant docs]
- Previous work: [Related plans or completed tasks]
```

6. **Output to User**:
   - Confirm file location with full path and filename
   - Provide command to start new context:

   ```
   To continue implementation in a new context:
   1. Open new Claude Code session
   2. Run: cat [full-path-to-saved-file]
   3. Say: "Implement this plan"
   ```

7. **Error Handling**:
   - If no tasks exist: Create plan with conversation summary
   - If work plans directory not configured: Prompt user for path
   - If plan name not provided: Prompt user for meaningful name
   - If directory doesn't exist: Create it with proper permissions
   - If no clear objective: Ask user to clarify before saving

8. **Configuration Format**:
   - **Preferred** — `.claude/aidoc-flow.config.yaml` (see `docs/CONFIG.md`):

   ```yaml
   work_plans_dir: work_plans/
   ```

   - **Legacy** (still honored) — a line in `.claude/CLAUDE.md`:

   ```markdown
   ### Project Configuration
   **Work Plans Directory**: /path/to/plans/
   ```
