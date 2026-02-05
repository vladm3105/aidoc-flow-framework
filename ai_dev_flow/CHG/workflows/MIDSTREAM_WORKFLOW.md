---
title: "Midstream Change Workflow"
tags:
  - change-management
  - workflow
  - midstream
  - shared-architecture
custom_fields:
  document_type: workflow
  artifact_type: CHG
  change_source: midstream
  entry_gate: GATE-05
  development_status: active
---

# Midstream Change Workflow

> **Entry Gate**: GATE-05 (Architecture/Contract)
> **Source Layers**: L5-L8 (ADR, SYS, REQ, CTR)
> **Cascade Direction**: Bi-directional (may bubble up or cascade down)

## 1. Overview

This workflow handles changes originating from architectural decisions, system requirements, atomic requirements, or API contracts. These changes enter at GATE-05 and may require upstream escalation or downstream cascade.

### 1.1 Typical Triggers

- Architecture decisions (new ADR)
- Technology stack changes
- API contract modifications
- Design optimization discoveries
- Integration requirement changes

### 1.2 Workflow Path

```
MIDSTREAM TRIGGER (L5-L8)
          │
          ▼
     ┌────────────────────────────────┐
     │ Does change affect L1-L4?      │
     │ (Business requirements impact) │
     └────────────┬───────────────────┘
                  │
      ┌───────────┼───────────┐
      │ Yes       │           │ No
      ▼           │           ▼
   GATE-01        │       GATE-05
   (Bubble Up)    │       (Entry)
      │           │           │
      ▼           │           ▼
   Update L1-L4   │       Update L5-L8
      │           │           │
      ▼           │           ▼
   GATE-05 ◄──────┘       GATE-09
      │                       │
      ▼                       ▼
   GATE-09               GATE-12
      │                       │
      ▼                       ▼
   GATE-12               DEPLOYED
      │
      ▼
   DEPLOYED
```

## 2. Pre-Workflow Checklist

Before initiating the midstream change workflow:

```markdown
- [ ] Technical rationale documented
- [ ] Upstream impact assessed (does this affect L1-L4?)
- [ ] Downstream impact assessed (which L9-L14 affected?)
- [ ] Change level proposed (L1/L2/L3)
- [ ] Breaking change status determined
- [ ] Security implications reviewed (if external trigger)
```

## 3. Bubble-Up Assessment

**Critical Decision Point**: Before proceeding with GATE-05, assess if change requires upstream escalation.

### 3.1 Bubble-Up Indicators

| Indicator | Action |
|-----------|--------|
| Change contradicts BRD objective | MUST bubble up to GATE-01 |
| Change requires PRD amendment | MUST bubble up to GATE-01 |
| Architecture pivot changes product scope | MUST bubble up to GATE-01 |
| Contract change affects external consumers | MAY bubble up (stakeholder decision) |

### 3.2 Bubble-Up Process

```
Midstream Change Identified
         │
         ▼
┌─────────────────────────────────┐
│ Impact Assessment:              │
│ - Does this change business     │
│   requirements?                 │
│ - Does this change product      │
│   features?                     │
│ - Does this affect stakeholder  │
│   commitments?                  │
└─────────────────┬───────────────┘
                  │
        ┌─────────┼─────────┐
        │ Any Yes │         │ All No
        ▼         │         ▼
    GATE-01       │     GATE-05
    Entry         │     Entry
        │         │         │
        ▼         │         ▼
    Continue      │     Continue
    Full Cascade  │     Midstream
```

## 4. Step-by-Step Process

### Step 1: Change Request Initialization

| Action | Details |
|--------|---------|
| Create CHG directory | `docs/CHG/CHG-XX_short_name/` |
| Use template | L2: `CHG-MVP-TEMPLATE.md`, L3: `CHG-TEMPLATE.md` |
| Set change source | `midstream` |
| Identify entry layer | Layer 5-8 where change originates |

```yaml
# CHG frontmatter
custom_fields:
  change_source: midstream
  entry_gate: GATE-05
  bubble_up_required: false  # or true if upstream impact
```

### Step 2: GATE-05 Entry

**Validation Requirements**:

| Check | L1 | L2 | L3 |
|-------|----|----|---|
| Technical rationale | Yes | Yes | Yes |
| Upstream impact check | Yes | Yes | Yes |
| Breaking change status | - | Yes | Yes |
| Security review (external) | - | Conditional | Yes |

**Run validation**:
```bash
./CHG/scripts/validate_gate05.sh CHG-XX_change/CHG-XX_change.md
```

### Step 3: Update Source Layers (L5-L8)

| Layer | Artifact | Common Changes | Special Requirements |
|-------|----------|----------------|---------------------|
| L5 | ADR | New decision, status change | Context-Decision-Consequences |
| L6 | SYS | Quality attribute update | Measurable thresholds |
| L7 | REQ | Atomic requirement change | 6 traceability tags |
| L8 | CTR | API contract modification | YAML + MD sync |

**ADR Specific**:
```markdown
For new ADR:
- Create ADR-XXX with proper status
- Link to existing ADRs if superseding

For ADR status change:
- Update status field (Proposed → Accepted/Deprecated)
- Document consequences in CHG
```

**CTR Specific**:
```markdown
For breaking API change (L3):
- Notify all consumers
- Document deprecation timeline
- Provide migration guide
- Set minimum notice period (30 days)
```

### Step 4: GATE-09 Cascade

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

### Step 5: GATE-12 Implementation

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

### Step 6: Closure

```markdown
## Closure Checklist
- [ ] All gates passed
- [ ] Upstream impact resolved (if bubble-up was required)
- [ ] All affected artifacts updated
- [ ] Contract consumers notified (if CTR changed)
- [ ] Traceability matrix updated
- [ ] CHG status set to "Completed"
```

## 5. Change Level Specifics

### 5.1 L1 Patch (Midstream)

Common for:
- SPEC typo corrections
- TSPEC test case clarifications
- TASKS estimation adjustments

**Process**: Direct edit, no CHG document required

### 5.2 L2 Minor (Midstream)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-MVP-TEMPLATE.md |
| Approvals | TL + Domain Expert |
| Cascade | L5-L14 (affected layers) |
| Timeline | 2-5 business days |

### 5.3 L3 Major (Midstream)

| Requirement | Details |
|-------------|---------|
| CHG Document | CHG-TEMPLATE.md |
| Approvals | Architect + Security (if external) |
| Cascade | Full (may include L1-L4 via bubble-up) |
| Archive Required | Yes |
| Timeline | 5-15 business days |

## 6. Common Scenarios

### Scenario 1: New Architecture Decision

```
Trigger: Team decides to use GraphQL instead of REST
Change Level: L3 (architecture pivot)

1. Create CHG-XX_graphql_migration/
2. Assess: Does this affect product scope? → Yes
3. GATE-01: Update PRD with GraphQL capabilities
4. GATE-05: Create ADR-XXX for GraphQL decision
5. GATE-05: Update CTR with GraphQL schema
6. GATE-09: Update SPEC/TSPEC for new API
7. GATE-12: Implement GraphQL endpoints
```

### Scenario 2: Contract Extension

```
Trigger: New API endpoint needed for integration
Change Level: L2 (non-breaking addition)

1. Create CHG-XX_api_extension/
2. Assess: Does this affect product scope? → No
3. GATE-05: Update CTR with new endpoint
4. GATE-09: Create SPEC/TSPEC for endpoint
5. GATE-12: Implement endpoint
```

### Scenario 3: Requirement Optimization

```
Trigger: Better algorithm discovered during design review
Change Level: L2 (design optimization)

1. Create CHG-XX_algorithm_improvement/
2. Assess: Does this affect product scope? → No
3. GATE-05: Update REQ with performance improvement
4. GATE-09: Update SPEC with new algorithm
5. GATE-09: Update TSPEC with performance baseline
6. GATE-12: Implement optimized algorithm
```

## 7. External Trigger Handling

When midstream change is triggered by external source:

### 7.1 Security Vulnerability

| CVSS Score | Process |
|------------|---------|
| 9.0-10.0 | EMERGENCY BYPASS |
| 7.0-8.9 | Expedited GATE-05 (72h) |
| 4.0-6.9 | Standard GATE-05 |
| 0.1-3.9 | Standard GATE-05 |

### 7.2 Dependency Update

```markdown
1. Assess breaking changes in dependency
2. If breaking: L3 with full cascade
3. If non-breaking: L2 with targeted cascade
4. Update CTR if dependency exposes APIs
```

## 8. Validation Script Integration

```bash
# Full workflow validation
./CHG/scripts/validate_all_gates.sh CHG-XX_change/CHG-XX_change.md --source=midstream

# Check if bubble-up required
python CHG/scripts/validate_chg_routing.py CHG-XX_change/CHG-XX_change.md --check-bubble-up

# Individual gate validation
./CHG/scripts/validate_gate05.sh CHG-XX_change/CHG-XX_change.md
./CHG/scripts/validate_gate09.sh CHG-XX_change/CHG-XX_change.md
./CHG/scripts/validate_gate12.sh CHG-XX_change/CHG-XX_change.md
```

---

**Related Documents**:
- [../gates/GATE-05_ARCHITECTURE_CONTRACT.md](../gates/GATE-05_ARCHITECTURE_CONTRACT.md)
- [../sources/MIDSTREAM_CHANGE_GUIDE.md](../sources/MIDSTREAM_CHANGE_GUIDE.md)
- [../sources/EXTERNAL_CHANGE_GUIDE.md](../sources/EXTERNAL_CHANGE_GUIDE.md)
- [UPSTREAM_WORKFLOW.md](./UPSTREAM_WORKFLOW.md) (for bubble-up cases)
