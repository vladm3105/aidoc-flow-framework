---
title: "IMPL-000: IMPL Index"
tags:
  - index-document
  - layer-8-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: IMPL
  layer: 8
  priority: shared
---

# IMPL-000: Implementation Plans Master Index

Note: Some examples in this index show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

## Purpose

This document serves as the master index for all Implementation Plans (IMPL) in the project. Use this index to:

- **Discover** existing implementation plans
- **Track** project status across multiple features
- **Coordinate** work between teams
- **Reference** deliverables and their status

## Position in Document Workflow

```mermaid
flowchart LR
    REQ[REQ] --> IMPL[IMPL]
    IMPL --> CTR[CTR]
    IMPL --> SPEC[SPEC]
    CTR --> SPEC
    SPEC --> TASKS[TASKS]
    TASKS --> Code

    style IMPL fill:#fff9c4,stroke:#f57f17,stroke-width:3px
```

> **Note on Diagram Labels**: The above flowchart shows the sequential workflow. For formal layer numbers used in cumulative tagging, always reference the 16-layer architecture (Layers 0-15) defined in README.md. Diagram groupings are for visual clarity only.

## Implementation Plans Index

| IMPL ID | Title | Status | Related REQs | Deliverables | Timeline | Owner | Last Updated |
|---------|-------|--------|--------------|--------------|----------|-------|--------------|
| [IMPL_IMPLEMENTATION_PLAN](./IMPL_IMPLEMENTATION_PLAN.md) | Create IMPL/ System | In Progress | N/A | IMPL/ folder, templates | 4-5 hours | Documentation Team | 2025-11-02 |
| [IMPL-01](./examples/IMPL-01_risk_management_system.md) | resource management System | Planned | REQ-03, REQ-05, REQ-08 | CTR-03, SPEC-03, TASKS-03, CTR-05, SPEC-05, TASKS-05, CTR-08, SPEC-08, TASKS-08 | 3 sprints (6 weeks) | Agent Team | 2025-11-02 |

## Status Definitions

| Status | Meaning | Description |
|--------|---------|-------------|
| **Planned** | Not started | IMPL Plan created, waiting to begin |
| **In Progress** | Active work | Currently implementing phases |
| **On Hold** | Temporarily paused | Blocked or deprioritized |
| **Completed** | Finished | All deliverables created and validated |
| **Cancelled** | Abandoned | Work stopped, requirements changed |

## Adding New Implementation Plans

When creating a new IMPL Plan:

1. **Copy Template**:
   ```bash
   cp ai_dev_flow/IMPL/IMPL-TEMPLATE.md \
      ai_dev_flow/IMPL/IMPL-NN_feature_name.md
   ```

2. **Assign IMPL ID**: Use next sequential number (IMPL-02, IMPL-03, ...)

3. **Update This Index**: Add new row to table above with:
   - IMPL ID and link to file
   - Title (brief feature description)
   - Status (Planned initially)
   - Related REQ-IDs
   - Deliverables (CTR/SPEC/TASKS to be created)
   - Timeline estimate
   - Owner (team or person)
   - Last Updated date

4. **Create Cross-References**: Update related REQ documents to reference new IMPL

## Index by Status

### Planned
- IMPL-01: resource management System

### In Progress
- IMPL_IMPLEMENTATION_PLAN: Create IMPL/ System

### On Hold
- None

### Completed
- None

### Cancelled
- None

## Index by Team/Owner

| Team/Owner | IMPL Plans | Count |
|------------|-----------|-------|
| Documentation Team | IMPL_IMPLEMENTATION_PLAN | 1 |
| Agent Team | IMPL-01 | 1 |

## Index by Timeline

| Timeline | IMPL Plans |
|----------|-----------|
| < 1 week | IMPL_IMPLEMENTATION_PLAN (4-5 hours) |
| 1-4 weeks | - |
| 1-3 months | IMPL-01 (6 weeks) |
| > 3 months | - |

## Deliverables Summary

### CTR Documents to Create
- CTR-03 (IMPL-01)
- CTR-05 (IMPL-01)
- CTR-08 (IMPL-01)

### SPEC Documents to Create
- SPEC-03 (IMPL-01)
- SPEC-05 (IMPL-01)
- SPEC-08 (IMPL-01)

### TASKS Documents to Create
- TASKS-03 (IMPL-01)
- TASKS-05 (IMPL-01)
- TASKS-08 (IMPL-01)

## Related Documents

- **Template**: [IMPL-TEMPLATE.md](./IMPL-TEMPLATE.md) - Use this to create new IMPL Plans
- **README**: [README.md](./README.md) - Learn about IMPL Plans purpose and structure
- **Example**: [IMPL-01](./examples/IMPL-01_risk_management_system.md) - Reference implementation plan

## Maintenance Guidelines

### Updating This Index

**When starting work on an IMPL Plan**:
- Update Status from "Planned" to "In Progress"
- Update Last Updated date

**When completing a phase**:
- Add checkmarks to Deliverables column for created documents
- Update Last Updated date

**When completing an IMPL Plan**:
- Update Status to "Completed"
- Link all created CTR/SPEC/TASKS documents
- Update Last Updated date

**When putting work on hold**:
- Update Status to "On Hold"
- Add reason in Notes column
- Update Last Updated date

### Review Schedule

This index should be reviewed:
- **Daily**: By project managers for status updates
- **Weekly**: By team leads for resource allocation
- **Monthly**: By architects for deliverable tracking

## Quick Statistics

- **Total IMPL Plans**: 2
- **Planned**: 1
- **In Progress**: 1
- **On Hold**: 0
- **Completed**: 0
- **Cancelled**: 0

## Usage Examples

### Finding Implementation Plans for a Requirement

**Question**: "Which IMPL Plans address REQ-03?"

**Answer**: Check "Related REQs" column → IMPL-01 (resource management System)

### Checking What's Currently Being Worked On

**Question**: "What's in progress?"

**Answer**: Check "Status" column for "In Progress" → IMPL_IMPLEMENTATION_PLAN

### Identifying Upcoming Deliverables

**Question**: "What CTR documents will be created?"

**Answer**: See "Deliverables Summary" section → CTR-03, CTR-005, CTR-008

---

**Index Version**: 1.0
**Last Updated**: 2025-11-02
**Maintained By**: Documentation Team
**Next Review**: 2025-11-09 (weekly)
