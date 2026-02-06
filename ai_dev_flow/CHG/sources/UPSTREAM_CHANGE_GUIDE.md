---
title: "Upstream Change Guide"
tags:
  - change-management
  - change-source
  - upstream
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: CHG
  change_source: upstream
  origin_layers: [1, 2, 3, 4]
  development_status: active
---

# Upstream Change Guide

**Change Source**: Upstream (Business-Driven)
**Origin Layers**: L1-L4 (BRD, PRD, EARS, BDD)
**Direction**: Top-down cascade to L14
**Entry Gate**: GATE-01 (Business/Product)

---

## Gate Entry Point

| Attribute | Value |
|-----------|-------|
| **Entry Gate** | GATE-01 |
| **Gate Layers** | L1-L4 (BRD, PRD, EARS, BDD) |
| **Cascade Path** | GATE-01 → GATE-05 → GATE-09 → GATE-12 |
| **Validation Script** | `./CHG/scripts/validate_gate01.sh` |
| **Full Workflow** | `workflows/UPSTREAM_WORKFLOW.md` |

**Before proceeding, run gate validation:**
```bash
./CHG/scripts/validate_gate01.sh <CHG_FILE>
```

---

## 1. Overview

Upstream changes originate from business, product, or market inputs and cascade downward through all affected layers.

```
┌─────────────────────────────────────────────────────────────┐
│                    UPSTREAM CHANGE FLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────┐                   │
│  │         CHANGE TRIGGERS             │                   │
│  │  • Market feedback                  │                   │
│  │  • Stakeholder request              │                   │
│  │  • Regulatory change                │                   │
│  │  • Competitive pressure             │                   │
│  │  • User story refinement            │                   │
│  └──────────────┬──────────────────────┘                   │
│                 │                                           │
│                 ▼                                           │
│  ┌─────────────────────────────────────┐                   │
│  │  L1 BRD  →  L2 PRD  →  L3 EARS  →  L4 BDD              │
│  └──────────────┬──────────────────────┘                   │
│                 │                                           │
│                 ▼ CASCADE                                   │
│  ┌─────────────────────────────────────┐                   │
│  │  L5-L11 Architecture/Design/Tasks   │                   │
│  └──────────────┬──────────────────────┘                   │
│                 │                                           │
│                 ▼ CASCADE                                   │
│  ┌─────────────────────────────────────┐                   │
│  │  L12-L14 Code/Tests/Validation      │                   │
│  └─────────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. Common Triggers

| Trigger | Example | Typical Level | Entry Point |
|---------|---------|---------------|-------------|
| Market feedback | "Customers want mobile app" | L2-L3 | BRD or PRD |
| Stakeholder request | "Add compliance dashboard" | L2-L3 | BRD |
| Regulatory change | "GDPR requires data export" | L3 | BRD |
| Competitive response | "Competitor has feature X" | L2 | PRD |
| User story refinement | "Clarify acceptance criteria" | L1-L2 | BDD |
| Feature deprecation | "Remove legacy workflow" | L3 | PRD |

## 3. Impact Assessment

### 3.1 Cascade Analysis

When an upstream change occurs, assess impact at each layer:

| Layer | Assessment Question | If Yes |
|-------|---------------------|--------|
| L1 BRD | Does this change business objectives? | Update BRD |
| L2 PRD | Does this change product features? | Update PRD |
| L3 EARS | Does this change formal requirements? | Update EARS |
| L4 BDD | Does this change acceptance criteria? | Update BDD |
| L5 ADR | Does this change architecture decisions? | Create new ADR |
| L6 SYS | Does this change system requirements? | Update SYS |
| L7 REQ | Does this change atomic requirements? | Update REQ |
| L8 CTR | Does this change API contracts? | Update CTR |
| L9 SPEC | Does this change technical specs? | Update SPEC |
| L10 TSPEC | Does this change test specifications? | Update TSPEC |
| L11 TASKS | Does this change implementation tasks? | Update TASKS |
| L12+ | Does this require code changes? | Regenerate |

### 3.2 Scope Boundaries

**Additive Changes** (New features):
- Create new element IDs in existing documents
- Extend existing contracts/specs
- Typical Level: L2

**Modifying Changes** (Change existing):
- Assess downstream impact first
- May require versioning
- Typical Level: L2-L3

**Removing Changes** (Deprecate):
- Always requires traceability repair
- Typical Level: L3

## 4. Workflow by Change Type

### 4.1 New Feature Request

```
1. Document in PRD (or BRD if business-level)
   - Add new user story / feature section
   - Increment document version

2. Generate EARS requirements
   - WHEN-THE-SHALL-WITHIN for new feature
   - Link to PRD

3. Create BDD scenarios
   - Given-When-Then for acceptance
   - Link to EARS

4. Assess architecture impact
   - If new patterns needed → Create ADR
   - If extending existing → Update SYS

5. Create atomic requirements (REQ)
   - Granular, testable requirements
   - Link to upstream

6. Update contracts if needed (CTR)
   - New endpoints or data models

7. Generate SPEC
   - Technical implementation details

8. Create TSPEC (TDD)
   - Test specifications BEFORE code
   - UTEST, ITEST, STEST, FTEST as needed

9. Generate TASKS
   - Implementation steps

10. Implement and validate
```

### 4.2 Requirement Clarification

```
1. Identify source document (BRD/PRD/EARS/BDD)

2. Classify change level
   - Typo/wording only → L1
   - Behavior clarification → L2

3. Update source document
   - Increment patch or minor version

4. Check downstream impact
   - If behavior unchanged → Done
   - If behavior clarified → Update affected layers
```

### 4.3 Feature Deprecation

```
1. Create L3 CHG document
   - Document deprecation reason
   - List all affected artifacts

2. Archive deprecated artifacts
   - Move to CHG archive/
   - Add deprecation notices

3. Update references
   - Remove from indexes
   - Update traceability matrices

4. Update TSPEC
   - Remove or mark deprecated tests

5. Remove code
   - Delete implementations
   - Clean up dependencies

6. Validate
   - Ensure no broken references
```

## 5. BRD Change Specifics

### 5.1 When BRD Changes

BRD changes are the highest-impact upstream changes:

| BRD Change Type | Impact Scope | Required Actions |
|-----------------|--------------|------------------|
| New business objective | Full cascade L1-L14 | L3 CHG, full regeneration |
| Objective refinement | L2-L14 | L2 CHG, partial regeneration |
| Stakeholder update | L1 only | L1, version bump |
| Constraint change | Varies | Assess each layer |

### 5.2 BRD Change Checklist

- [ ] Document change in BRD with version increment
- [ ] Notify PRD owners of cascading impact
- [ ] Update traceability tags in downstream docs
- [ ] Schedule regeneration of affected layers
- [ ] Update project timeline if significant

## 6. PRD Change Specifics

### 6.1 When PRD Changes

PRD changes affect features and user stories:

| PRD Change Type | Impact Scope | Required Actions |
|-----------------|--------------|------------------|
| New feature | L2-L14 | L2-L3 CHG, generate downstream |
| Feature modification | L2-L14 | L2 CHG, update downstream |
| Feature removal | L2-L14 | L3 CHG, deprecation process |
| User story update | L3-L14 | L1-L2, update EARS/BDD |

### 6.2 PRD Change Checklist

- [ ] Update PRD with version increment
- [ ] Update/create EARS requirements
- [ ] Update/create BDD scenarios
- [ ] Assess ADR impact
- [ ] Flow changes through L5-L14

## 7. EARS/BDD Change Specifics

### 7.1 EARS Changes

EARS formalizes requirements - changes here affect testing:

- Update WHEN-THE-SHALL-WITHIN statements
- Ensure BDD scenarios align
- Update REQ atomic requirements
- Regenerate TSPEC for affected tests

### 7.2 BDD Changes

BDD defines acceptance criteria:

- Update Given-When-Then scenarios
- Ensure EARS alignment
- Update TSPEC (especially FTEST)
- Regenerate acceptance tests

## 8. Traceability Repair

After upstream changes, verify:

```bash
# Check for broken references
python ai_dev_flow/scripts/validate_forward_references.py

# Verify traceability matrix
python ai_dev_flow/scripts/validate_traceability_matrix.py

# Run test suite to verify TSPEC coverage
pytest tests/
```

### 8.1 Common Traceability Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Orphaned REQ | PRD element removed | Remove or reassign REQ |
| Missing @prd tag | New PRD element | Add tag to downstream docs |
| BDD without EARS | EARS not created | Create EARS first |
| TSPEC mismatch | SPEC changed | Update TSPEC |

## 9. Examples

### 9.1 Example: New Feature Request

**Trigger**: "Add export to PDF functionality"

```
Change Level: L2 Minor
Entry Point: PRD-05 (Product Features)

Actions:
1. Add feature to PRD-05 Section 3
2. Create EARS.05.15.xx requirements
3. Create BDD scenarios for PDF export
4. Update SYS if system requirements affected
5. Create REQ atomic requirements
6. Update CTR if new API endpoint
7. Create SPEC for implementation
8. Create TSPEC (UTEST, ITEST, FTEST)
9. Generate TASKS
10. Implement
```

### 9.2 Example: Regulatory Compliance Change

**Trigger**: "GDPR requires user data export within 30 days"

```
Change Level: L3 Major
Entry Point: BRD-01 (Business Requirements)

Actions:
1. Create CHG-05_gdpr_data_export/
2. Update BRD-01 with compliance requirement
3. Create PRD feature for data export
4. Generate EARS formal requirements
5. Create BDD acceptance scenarios
6. Create ADR for compliance architecture
7. Update SYS with quality attributes
8. Create REQ atomic requirements
9. Update CTR with export API
10. Generate SPEC
11. Create TSPEC with compliance tests
12. Generate TASKS
13. Implement and validate
14. Close CHG
```

---

**Related Documents**:
- [CHANGE_MANAGEMENT_GUIDE.md](../CHANGE_MANAGEMENT_GUIDE.md)
- [CHANGE_CLASSIFICATION_GUIDE.md](../CHANGE_CLASSIFICATION_GUIDE.md)
