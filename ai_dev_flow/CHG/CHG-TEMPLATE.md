---
id: CHG-XX
title: Title of Change
tags:
  - change-document
  - architectural-change
  - shared-architecture
status: [Proposed/Implemented]
date: YYYY-MM-DD
author: [Author Name]
supersedes: [List, of, Artifact, IDs]
---

# CHG-XX: [Title of Change]

## 1. Overview
[Brief summary of the change. What is changing and why?]

### 1.1 Reason for Change
1.  **[Reason 1]**: [Explanation]
2.  **[Reason 2]**: [Explanation]

## 2. Scope & Impact Analysis

### 2.1 Scope Definition
> **Critical**: Explicitly define what is changing and what is *NOT* changing.
- **Replacing**: [List components/services being retired, e.g., Firestore]
- **Retaining**: [List related components staying active, e.g., BigQuery, Neo4j]
- **Reasoning**: [Why this specific scope? Explain rejection of consolidation if applicable.]

### 2.2 Impact Matrix (The "V" Model)
> **Rule**: You MUST identify impacted artifacts at EVERY layer. Do not skip layers.

| Layer | Type | Archived Artifacts (Old) | New Artifacts (Replacement) |
|-------|------|--------------------------|-----------------------------|
| 1 | **(Strategy)**  | `ADR-XX` | `ADR-YY` |
| 2 | **(Product)**   | `PRD-XX` | `PRD-YY` |
| 3 | **(Data/Event)**| `EARS-XX` | `EARS-YY` |
| 4 | **(Test)**      | `BDD-XX` | `BDD-YY` |
| 6 | **(System)**    | `SYS-XX` | `SYS-YY` |
| 7 | **(Reqs)**      | `REQ-XX` | `REQ-YY` |
| 8 | **(Plan)**      | `IMPL-XX` | `IMPL-YY` |
| 9 | **(Interface)** | `CTR-XX` | `CTR-YY` |
| 10| **(Spec)**      | `SPEC-XX` | `SPEC-YY` |
| 11| **(CodeGen)**   | `TASKS-XX` | `TASKS-YY` |
| --| **(Code)**      | `src/...` | `src/...` |

### 2.3 Dependency Check
- [ ] **Upstream**: Have I checked all documents creating requirements for these components?
- [ ] **Downstream**: Have I checked all code/configs that depend on these components?
- [ ] **Search**: Have I grepped the `docs/` folder for the keywords (e.g., "Firestore", "Chroma")?

## 3. Migration Steps (Summary)
See `implementation_plan.md` in this directory for the detailed audit log.

1.  **Archival**: [Brief description]
2.  **Deprecation**: [Brief description]
3.  **Definition**: [Brief description]
4.  **Repair**: [Brief description]
5.  **Execution**: Implement new TASKS and Verify.

## 4. Rollback Plan
If this change fails verification:
1.  [Step 1]
2.  [Step 2]
