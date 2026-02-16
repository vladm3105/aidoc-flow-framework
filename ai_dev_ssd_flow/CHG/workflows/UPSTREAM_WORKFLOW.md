---
title: "Upstream Change Workflow"
tags:
  - change-management
  - workflow
  - upstream
  - shared-architecture
custom_fields:
  document_type: workflow
  artifact_type: CHG
  change_source: upstream
  entry_gate: GATE-01
  development_status: active
---

# Upstream Change Workflow

> **Entry Gate**: GATE-01 (Business/Product)
> **Source Layers**: L1-L4 (BRD, PRD, EARS, BDD)
> **Cascade Direction**: Top-down to L14

## 1. Overview

This workflow handles changes originating from business requirements, product decisions, market feedback, or stakeholder requests. These changes enter at GATE-01 and cascade through all downstream layers.

### 1.1 Typical Triggers

- Market research insights
- Stakeholder feature requests
- Regulatory/compliance changes
- Strategic business pivots
- User research findings

### 1.2 Workflow Path

```
UPSTREAM TRIGGER
       │
       ▼
   GATE-01 ──────────────────────────────────────┐
   (L1-L4)                                       │
       │                                         │
       ▼                                         │
   GATE-05 ──────────────────────────────┐       │
   (L5-L8)                               │       │
       │                                 │       │
       ▼                                 │       │ Full
   GATE-09 ──────────────────┐           │       │ Cascade
   (L9-L11)                  │           │       │ (L3)
       │                     │           │       │
       ▼                     │           │       │
   GATE-12                   │           │       │
   (L12-L14)                 │           │       │
       │                     │           │       │
       ▼                     ▼           ▼       ▼
   DEPLOYED              Partial     Partial   Full
                        Cascade     Cascade  Cascade
```

## 2. Pre-Workflow Checklist

Before initiating the upstream change workflow:

```markdown
- [ ] Business justification documented
- [ ] Sponsoring stakeholder identified
- [ ] Initial impact assessment completed
- [ ] Change level proposed (L1/L2/L3)
- [ ] Timeline expectations set
```

## 3. Step-by-Step Process

### Step 1: Change Request Initialization

| Action | Details |
|--------|---------|
| Create CHG directory | `docs/CHG/CHG-XX_short_name/` |
| Use template | L2: `CHG-MVP-TEMPLATE.md`, L3: `CHG-TEMPLATE.md` |
| Set change source | `upstream` |
| Identify entry point | Layer 1-4 where change originates |

```yaml
# CHG frontmatter
custom_fields:
  change_source: upstream
  entry_gate: GATE-01
```

### Step 2: GATE-01 Entry

**Validation Requirements**:

| Check | L1 | L2 | L3 |
|-------|----|----|---|
| Business justification | - | Yes | Yes |
| Stakeholder approval | - | PO | PO + Stakeholder |
| Impact assessment | - | Yes | Yes |
| Rollback plan | - | - | Yes |

**Run validation**:
```bash
./CHG/scripts/validate_gate01.sh CHG-XX_change/CHG-XX_change.md
```

### Step 3: Update Source Layers (L1-L4)

| Layer | Artifact | Update Type | TDD Note |
|-------|----------|-------------|----------|
| L1 | BRD | Edit or Archive+New | - |
| L2 | PRD | Edit or Archive+New | - |
| L3 | EARS | Edit or Archive+New | - |
| L4 | BDD | Edit or Archive+New | Defines acceptance tests |

**L3 Major Change**: Archive old artifacts, create new versions
```
docs/CHG/CHG-XX/
├── CHG-XX.md
├── archive/
│   ├── BRD-old.md
│   └── PRD-old.md
└── implementation_plan.md
```

### Step 4: GATE-05 Cascade

After GATE-01 passes, proceed to GATE-05 if architecture/contracts affected:

**Validation**:
```bash
./CHG/scripts/validate_gate05.sh CHG-XX_change/CHG-XX_change.md
```

**Update Layers L5-L8**:

| Layer | Artifact | Considerations |
|-------|----------|----------------|
| L5 | ADR | New decision? Create new ADR |
| L6 | SYS | Update quality attributes |
| L7 | REQ | Update atomic requirements |
| L8 | CTR | Update contracts if API affected |

### Step 5: GATE-09 Cascade

**Validation**:
```bash
./CHG/scripts/validate_gate09.sh CHG-XX_change/CHG-XX_change.md
```

**Update Layers L9-L11 (TDD Order)**:

| Order | Layer | Artifact | TDD Compliance |
|-------|-------|----------|----------------|
| 1 | L10 | TSPEC | Update test specs FIRST |
| 2 | L9 | SPEC | Then update specifications |
| 3 | L11 | TASKS | Finally update task breakdown |

### Step 6: GATE-12 Implementation

**Validation**:
```bash
./CHG/scripts/validate_gate12.sh CHG-XX_change/CHG-XX_change.md
```

**Implement Layers L12-L14**:

| Layer | Artifact | Validation |
|-------|----------|------------|
| L12 | Code | Implement to pass TSPEC tests |
| L13 | Tests | Run TSPEC-defined tests |
| L14 | Validation | Complete validation checklist |

### Step 7: Closure

```markdown
## Closure Checklist
- [ ] All gates passed
- [ ] All affected artifacts updated
- [ ] Traceability matrix updated
- [ ] Tests passing
- [ ] CHG status set to "Completed"
- [ ] Stakeholder sign-off obtained (L2/L3)
```

## 4. Change Level Specifics

### 4.1 L1 Patch (Upstream)

L1 is rare for upstream changes; typically used for:
- Typo corrections in BRD/PRD
- Clarification without behavior change

**Process**: Direct edit, no CHG document required

### 4.2 L2 Minor (Upstream)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-MVP-TEMPLATE.md |
| Approvals | PO + TL |
| Cascade | Partial (affected layers only) |
| Timeline | 2-5 business days |

### 4.3 L3 Major (Upstream)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-TEMPLATE.md |
| Approvals | PO + Architect + Stakeholder |
| Cascade | Full (L1-L14) |
| Archive Required | Yes |
| Timeline | 5-20 business days |

## 5. Common Scenarios

### Scenario 1: New Feature Request

```
Trigger: Stakeholder requests "Mobile support"
Change Level: L2 or L3 (depends on scope)

1. Create CHG-XX_mobile_support/
2. GATE-01: Update PRD with mobile requirements
3. GATE-05: Create ADR for mobile architecture
4. GATE-09: Create SPEC/TSPEC for mobile features
5. GATE-12: Implement mobile code/tests
```

### Scenario 2: Regulatory Compliance

```
Trigger: New GDPR data export requirement
Change Level: L3 (impacts architecture)

1. Create CHG-XX_gdpr_export/
2. GATE-01: Update BRD with compliance requirement
3. GATE-01: Update PRD with data export feature
4. GATE-05: Update REQ for data handling
5. GATE-05: Update CTR for export API
6. GATE-09: Full SPEC/TSPEC cascade
7. GATE-12: Implementation
```

### Scenario 3: User Story Refinement

```
Trigger: QA feedback on acceptance criteria clarity
Change Level: L1 (clarification only)

1. Direct edit to BDD scenarios
2. No CHG document required
3. Commit with reference to feedback
```

## 6. Rollback Procedure

If change fails verification at any gate:

### 6.1 L2 Rollback

```markdown
1. Revert artifact changes (git revert)
2. Update CHG status to "Cancelled"
3. Document reason for rollback
4. Notify stakeholders
```

### 6.2 L3 Rollback

```markdown
1. Restore archived artifacts from CHG/archive/
2. Revert all cascaded changes
3. Update CHG status to "Cancelled"
4. Complete post-mortem
5. Create follow-up CHG if needed
```

## 7. Validation Script Integration

```bash
# Full workflow validation
./CHG/scripts/validate_all_gates.sh CHG-XX_change/CHG-XX_change.md --source=upstream

# Individual gate validation
./CHG/scripts/validate_gate01.sh CHG-XX_change/CHG-XX_change.md
./CHG/scripts/validate_gate05.sh CHG-XX_change/CHG-XX_change.md
./CHG/scripts/validate_gate09.sh CHG-XX_change/CHG-XX_change.md
./CHG/scripts/validate_gate12.sh CHG-XX_change/CHG-XX_change.md
```

---

**Related Documents**:
- [../gates/GATE-01_BUSINESS_PRODUCT.md](../gates/GATE-01_BUSINESS_PRODUCT.md)
- [../sources/UPSTREAM_CHANGE_GUIDE.md](../sources/UPSTREAM_CHANGE_GUIDE.md)
- [../CHG-TEMPLATE.md](../CHG-TEMPLATE.md)
- [../CHG-MVP-TEMPLATE.md](../CHG-MVP-TEMPLATE.md)
