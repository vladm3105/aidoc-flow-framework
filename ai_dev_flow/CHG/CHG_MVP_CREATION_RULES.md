---
title: "CHG MVP Creation Rules"
tags:
  - creation-rules
  - change-management
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: CHG
  priority: shared
  development_status: active
---

# CHG Creation Rules

Create a **Change Artifact (CHG)** when:
1.  **Architectural Pivot**: Switching core technologies (e.g., DB switch, Language switch).
2.  **Strategy Shift**: Changing fundamental patterns (e.g., Monolith to Microservices).
3.  **Mass Deprecation**: Retiring a significant set of requirements or capabilities.

## 2. Lifecycle & Status
The `status` field in the CHG header tracks the pivot's progress:
- **Proposed**: Impact analysis and planning in progress.
- **Implemented**: Migration steps (Archival, Supersession) complete; new TASKS defined.
- **Completed**: New TASKS executed and verified; Change is live.

*Do NOT create a CHG for standard iterative updates or minor refactors.*

> [!IMPORTANT]
> **Rule of Immutability**: You must **NEVER** modify an existing, approved artifact to reflect a fundamental change. You must **ALWAYS** Deprecate/Archive the old file and Create a **NEW** file (New ID or Version). This ensures the history of the project is preserved and the change is explicit.

## 2. File Organization (Strict)
CHG artifacts live in their own directory to serve as a self-contained record.
```
docs/CHG/CHG-XX_{slug}/
├── CHG-XX_{slug}.md        # The Definition (Derived from CHG-TEMPLATE)
├── implementation_plan.md  # The Audit Log (Frozen Plan)
└── archive/                # The Graveyard (Moved Artifacts)
```

### Common Pitfalls (Anti-Patterns)
1.  **Over-Scoping**: Assuming "Unified" means "Replace Everything". Always check `Retaining` lists.
2.  **Skipping Layers**: Ignoring 03_EARS/04_BDD/SYS artifacts because they are "middle layers". They MUST be replaced to maintain V-Model integrity.
3.  **Missing Artifacts**: Failing to grep/search for all files related to a technology (e.g., REQ files in subfolders).
4.  **Implicit Replacement**: Editing files instead of Archiving + Creating New. (Violates Immutable History).

## 3. The Workflow (The "5 Steps")

### Step 1: Initialize
- Create the directory.
- Create `CHG-XX_{slug}.md` using `CHG-TEMPLATE.md`.
- Create `implementation_plan.md` listing the specific execution steps.

### Step 2: Archive & Deprecate
- Move obsolete files to the `archive/` subfolder.
- **CRITICAL**: You MUST edit every archived file to add this header after the YAML frontmatter:
  ```markdown
  > [!WARNING]
  > **DEPRECATED**: This document has been archived by [CHG-XX](../CHG-XX_{slug}.md).
  > **Reason**: [Brief Reason]
  > **Status**: Archived
  ```

### Step 3: Supersede
- Create new replacement artifacts in their standard locations (`docs/ADR`, `docs/PRD`).
- Refer to the new artifacts in the `CHG` document.

### Step 4: Repair & Audit
- **Traceability**: Update all downstream documents (`DEVELOPMENT_PLAN.md`, `task.md`) to point to the new direction.
- **Development Plan Update**: You MUST add a specific sub-phase entry in `IMPLEMENTATION_PLAN.md` (project-specific file created from `10_TASKS/IMPLEMENTATION_PLAN_TEMPLATE.md`) to track the change execution.
  - Format: `Phase X.Y: {Change Title} (Implementation)`
  - Link: Must reference the frozen `implementation_plan.md` inside the CHG directory.
  - Example: `Phase 1.1: CHG-01 Unified Postgres (implementation_plan.md)`

### Step 5: Validate
- Ensure the `CHG` document accurately maps Old -> New.
