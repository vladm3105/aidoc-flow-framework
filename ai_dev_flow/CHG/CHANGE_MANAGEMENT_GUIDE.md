---
title: "Change Management Guide"
tags:
  - framework-guide
  - change-management
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Change Management & Architectural Pivots

This guide defines the universal standard workflow for managing major architectural changes, pivots, or strategic shifts in any AI Development Flow project.

## 1. Principles

## 1. Principles

1.  **Immutable History (CRITICAL)**: **NEVER** edit an approved artifact to reflect a major architectural change. **ALWAYS** archive the old one and create a new one with a new ID or version.
    - *Incorrect*: Editing `ADR-10` to say "We now use Postgres".
    - *Correct*: Archiving `ADR-10` and creating `ADR-23_unified_postgres`.
2.  **Formal Audit Trail**: Every major change must be tracked via a `CHG` (Change) artifact.
3.  **Preserve History**: Never delete major artifacts. Archive them to retain decision context.
4.  **Auditable Plan**: The specific steps taken to execute the change must be saved as a frozen plan.
5.  **Traceability**: Migration is not complete until all upstream and downstream links are repaired.

## 2. Trigger Conditions

Use this workflow when:
- **Technology Stack Pivot**: Replacing a core component (e.g., Database choice, Framework).
- **Strategy Shift**: Changing the fundamental approach (e.g., from Monolith to Microservices).
- **Deprecation**: Retiring a significant feature or layer.

## 3. The Migration Workflow

### Step 1: Initialize Change (CHG Artifacts)
**What to do**: Formalize the intent and the plan.
1.  **Create Directory**:
    ```bash
    mkdir -p docs/CHG/CHG-XX_{slug_reason}
    # Example: docs/CHG/CHG-01_unified_postgres
    ```
2.  **Create CHG Document**: `docs/CHG/CHG-XX.../CHG-XX_{slug}.md`.
    - **Header**: Standard frontmatter.
    - **Content**: Reason for change, Impact Analysis, Rollback Plan.
3.  **Create Change Plan**: `docs/CHG/CHG-XX.../implementation_plan.md`.
    - **Content**: The specific checklist of files to move, edit, and create. This serves as the audit log for the execution steps.

### Step 2: Archival & Deprecation
**What to do**: Move and mark old documents.
1.  **Create Archive Subfolder**:
    ```bash
    mkdir -p docs/CHG/CHG-XX_{slug}/archive
    ```
2.  **Move Artifacts**: Move obsolete documents (`ADR`, `PRD`, `TASKS`) to this archive folder.
3.  **Update Archived Files**: Open *each* archived file and add a Deprecation Note immediately after the frontmatter (YAML) block.
    ```markdown
    > [!WARNING]
    > **DEPRECATED**: This document has been archived by [CHG-XX](../CHG-XX_reason.md).
    > **Reason**: [Brief reason for deprecation]
    > **Status**: Archived
    ```

### Step 3: Strategic Definition (Supersession)
**What to do**: Define the new "Source of Truth".
1.  **Create New Artifacts**:
    - **Header**: Add "Supersedes: [Link to Archived Doc]" in metadata.
2.  **Update Project Plan**:
    - Update `DEVELOPMENT_PLAN.md` (created from `11_TASKS/DEVELOPMENT_PLAN_TEMPLATE.md`) to link to new artifacts.

### Step 4: Traceability Repair & Audit
**What to do**: Re-stitch the documentation web and audit the change.
1.  **Update Downstream**: Find documents linking to old artifacts; update them to point to new ones (or the CHG doc).
2.  **Update Development Plan**: You **MUST** add a specific sub-phase entry in `DEVELOPMENT_PLAN.md` to track the change execution.
    - **Format**: `Phase X.Y: {Change Title} (Architectural Pivot)`
    - **Link**: Must reference the frozen `implementation_plan.md` inside the CHG folder.
    - **Example**: `Phase 1.1: CHG-01 Unified Postgres (implementation_plan.md)`

### Step 5: Revalidation
**What to do**: Ensure quality is maintained.
1.  **Validate Structure**: Ensure new files follow `*_CREATION_RULES.md`.
2.  **Verify CHG Completeness**: Ensure the `CHG` folder contains the Definition, the Plan, and the Archive.

### Step 6: Execution & Closure
**What to do**: Execute the new direction and close the change.
1.  **Implement**: Execute the new `TASKS` artifacts created in Step 3.
2.  **Verify**: Run tests and validate the new architecture.
3.  **Close**: Update `CHG-XX_{slug}.md` status to `Completed` and record the final verification in `implementation_plan.md`.

## 4. CHG Folder Structure

```
docs/CHG/CHG-01_unified_postgres/
├── CHG-01_unified_postgres.md   # The High-Level Change Definition
├── implementation_plan.md       # The Audit Log of Steps
└── archive/                     # The "Graveyard" of old files
    ├── ADR-10_old_db.md
    └── ...
```
