---
title: "Emergency Bypass Workflow"
tags:
  - change-management
  - workflow
  - emergency
  - incident-response
  - shared-architecture
custom_fields:
  document_type: workflow
  artifact_type: CHG
  change_source: emergency
  entry_gate: BYPASS
  development_status: active
---

# Emergency Bypass Workflow

> **Entry Gate**: BYPASS (Skip all gates)
> **Triggers**: P1 Incidents, Critical Security (CVSS >= 9.0)
> **Post-Requirement**: Post-mortem within 72 hours

## 1. Overview

This workflow handles critical incidents and security vulnerabilities that require immediate action. The normal gate process is bypassed for rapid response, but must be followed by comprehensive post-incident documentation.

### 1.1 Emergency Criteria

| Category | Criteria | Response Time |
|----------|----------|---------------|
| **P1 Incident** | Production down, revenue impact | < 30 minutes to triage |
| **Critical Security** | CVSS >= 9.0, active exploitation | < 30 minutes to triage |
| **Data Breach** | Customer data exposed | Immediate |

### 1.2 Workflow Path

```
EMERGENCY TRIGGER
       │
       ▼
┌─────────────────────────────────────┐
│          PHASE 1: TRIAGE            │
│           (0-30 minutes)            │
│  1. Incident declared               │
│  2. Severity confirmed              │
│  3. Bypass authorized               │
│  4. Emergency stub created          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│          PHASE 2: HOTFIX            │
│         (30 min - 4 hours)          │
│  1. Implement hotfix                │
│  2. Minimal smoke test              │
│  3. Deploy to production            │
│  4. Monitor for resolution          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│       PHASE 3: POST-INCIDENT        │
│          (24-72 hours)              │
│  1. Complete CHG document           │
│  2. Conduct post-mortem             │
│  3. Pass applicable gates           │
│  4. Create preventive CHGs          │
│  5. Close emergency CHG             │
└─────────────────────────────────────┘
```

## 2. Phase 1: Triage (0-30 minutes)

### 2.1 Incident Declaration

| Step | Action | Responsible |
|------|--------|-------------|
| 1 | Detect incident | Monitoring/User report |
| 2 | Declare P1/Security | On-call engineer |
| 3 | Confirm severity | Incident commander |
| 4 | Authorize bypass | Incident commander |

### 2.2 Create Emergency Stub

Create minimal CHG document immediately:

**Filename**: `CHG-EMG-{YYYYMMDD-HHMM}.md`

```markdown
---
id: CHG-EMG-{timestamp}
title: "EMERGENCY: {brief description}"
tags:
  - change-document
  - emergency
  - p1-incident
custom_fields:
  document_type: change-record
  artifact_type: CHG
  change_level: EMERGENCY
  change_source: emergency
  development_status: in-progress
status: In Progress
date: {YYYY-MM-DD}
author: {On-call engineer}
incident_ticket: {INC-XXX}
---

# CHG-EMG-{timestamp}: EMERGENCY - {Brief Description}

## Incident Summary
- **Declared**: {timestamp}
- **Incident Commander**: {name}
- **Severity**: P1 / Critical Security
- **Bypass Authorized By**: {name}

## Problem Statement
{Brief description of the incident}

## Immediate Actions
- [ ] Hotfix in progress
- [ ] Monitoring active

## To Complete (Post-Incident)
- [ ] Full CHG documentation
- [ ] Post-mortem
- [ ] Gate validation
```

### 2.3 Authorization Requirements

| Severity | Authorizer | Documentation |
|----------|------------|---------------|
| P1 Incident | Incident Commander | Verbal + Stub |
| Critical Security | Security + IC | Verbal + Stub |
| Data Breach | Legal + IC + Security | Verbal + Stub |

## 3. Phase 2: Hotfix (30 min - 4 hours)

### 3.1 Implementation Rules

| Rule | Description |
|------|-------------|
| Minimal scope | Fix only what's necessary |
| No feature creep | No enhancements during hotfix |
| Pair programming | Two engineers minimum |
| Direct deploy | Skip staging if necessary |

### 3.2 Testing Requirements

| Test Type | Required | Notes |
|-----------|----------|-------|
| Smoke test | Yes | Critical path only |
| Full regression | No | Deferred to post-incident |
| Security scan | Conditional | If security incident |

### 3.3 Deployment Process

```markdown
## Emergency Deployment Checklist
- [ ] Code change reviewed by second engineer
- [ ] Smoke test passed
- [ ] Deployment notification sent
- [ ] Rollback plan ready
- [ ] Monitoring dashboards open
- [ ] On-call team notified
```

### 3.4 Rollback Trigger

If hotfix fails:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Error rate | > 5% increase | Rollback |
| Response time | > 2x baseline | Evaluate |
| New errors | Any critical | Rollback |

## 4. Phase 3: Post-Incident (24-72 hours)

### 4.1 Complete CHG Documentation

Update the emergency stub to full CHG document within 24 hours:

```markdown
## Full Documentation Requirements
- [ ] Complete problem statement
- [ ] Root cause analysis
- [ ] Impact assessment
- [ ] Timeline of events
- [ ] All affected artifacts listed
- [ ] Resolution details
- [ ] Lessons learned
```

### 4.2 Post-Mortem Document

Create `POST_MORTEM-{CHG-ID}.md` within 72 hours:

```markdown
---
title: "Post-Mortem: {CHG-ID}"
tags:
  - post-mortem
  - incident-review
custom_fields:
  chg_reference: CHG-EMG-YYYYMMDD-HHMM
  incident_ticket: INC-XXX
  post_mortem_date: YYYY-MM-DD
---

# Post-Mortem: {CHG-ID}

## Incident Summary
- **Duration**: {start} to {end}
- **Impact**: {users affected, revenue impact}
- **Severity**: P1 / Critical Security

## Timeline
| Time | Event |
|------|-------|
| HH:MM | Incident detected |
| HH:MM | P1 declared |
| HH:MM | Bypass authorized |
| HH:MM | Hotfix deployed |
| HH:MM | Resolution confirmed |

## Root Cause Analysis

### 5-Whys
1. Why?
2. Why?
3. Why?
4. Why?
5. Why? (Root cause)

### Contributing Factors
- Factor 1
- Factor 2

## Impact Assessment
- Users affected: {number}
- Duration: {hours}
- Revenue impact: {if applicable}
- Reputational impact: {if applicable}

## Resolution
{Description of the hotfix}

## Lessons Learned
1. What went well
2. What went poorly
3. Where we got lucky

## Action Items
| ID | Action | Owner | Due Date | Status |
|----|--------|-------|----------|--------|
| 1 | | | | Pending |
| 2 | | | | Pending |

## Preventive Measures
| Measure | CHG Reference | Priority |
|---------|---------------|----------|
| | CHG-XX | High |
| | CHG-YY | Medium |
```

### 4.3 Retroactive Gate Validation

After incident resolution, validate all applicable gates:

```bash
# Run all gate validations retroactively
./CHG/scripts/validate_all_gates.sh CHG-EMG-YYYYMMDD-HHMM/CHG-EMG-YYYYMMDD-HHMM.md --retroactive

# Individual gates as applicable
./CHG/scripts/validate_gate12.sh CHG-EMG-YYYYMMDD-HHMM/CHG-EMG-YYYYMMDD-HHMM.md
./CHG/scripts/validate_gate09.sh CHG-EMG-YYYYMMDD-HHMM/CHG-EMG-YYYYMMDD-HHMM.md
# etc.
```

### 4.4 Create Follow-Up CHGs

For each preventive measure, create a proper CHG:

```markdown
## Follow-Up CHG Requirements
- [ ] CHG for monitoring improvements
- [ ] CHG for code hardening
- [ ] CHG for test coverage
- [ ] CHG for documentation updates
- [ ] CHG for process improvements
```

### 4.5 Emergency CHG Closure

```markdown
## Emergency CHG Closure Checklist
- [ ] Full CHG document complete
- [ ] Post-mortem conducted
- [ ] Post-mortem document created
- [ ] All gates retroactively validated
- [ ] Follow-up CHGs created
- [ ] Stakeholders notified
- [ ] Status set to "Completed"
```

## 5. Error Codes

### 5.1 Emergency-Specific Errors

| Code | Description | Resolution |
|------|-------------|------------|
| EMG-E001 | Emergency not authorized | Obtain IC authorization |
| EMG-E002 | Non-critical using bypass | Use standard gate process |
| EMG-E003 | Emergency stub missing | Create CHG-EMG stub |
| EMG-E004 | Post-mortem overdue | Complete within 72h |
| EMG-E005 | Emergency CHG not closed | Complete closure checklist |

### 5.2 Warnings

| Code | Description | Resolution |
|------|-------------|------------|
| EMG-W001 | Incident reference missing | Add INC-XXX |
| EMG-W002 | Preventive CHG not created | Create follow-up CHG |
| EMG-W003 | Post-mortem missing RCA | Complete 5-Whys |

## 6. Decision Matrix

### 6.1 When to Use Emergency Bypass

| Situation | Use Bypass? | Reason |
|-----------|-------------|--------|
| Production down | Yes | Revenue/user impact |
| Critical security (CVSS >= 9.0) | Yes | Active threat |
| High security (CVSS 7.0-8.9) | No | Expedited GATE-05 |
| P2 incident | No | Standard process |
| "Urgent" feature | No | Never |

### 6.2 Emergency vs. Expedited

| Type | SLA | Gates | Documentation |
|------|-----|-------|---------------|
| Emergency | < 4 hours | Bypass | Post-incident |
| Expedited | 24-72 hours | All gates (fast-tracked) | Before deploy |
| Standard | 5-20 days | All gates | Before deploy |

## 7. Validation Script Integration

```bash
# Validate emergency stub
./CHG/scripts/validate_emergency_bypass.sh CHG-EMG-YYYYMMDD-HHMM/

# Check post-mortem completion
./CHG/scripts/validate_emergency_bypass.sh CHG-EMG-YYYYMMDD-HHMM/ --check-postmortem

# Retroactive full validation
./CHG/scripts/validate_all_gates.sh CHG-EMG-YYYYMMDD-HHMM/ --retroactive
```

## 8. Templates

### 8.1 Emergency Stub Location

`templates/CHG-EMERGENCY-TEMPLATE.md`

### 8.2 Post-Mortem Location

`templates/POST_MORTEM-TEMPLATE.md`

---

**Related Documents**:
- [../templates/CHG-EMERGENCY-TEMPLATE.md](../templates/CHG-EMERGENCY-TEMPLATE.md)
- [../templates/POST_MORTEM-TEMPLATE.md](../templates/POST_MORTEM-TEMPLATE.md)
- [../gates/GATE_ERROR_CATALOG.md](../gates/GATE_ERROR_CATALOG.md)
- [DOWNSTREAM_WORKFLOW.md](./DOWNSTREAM_WORKFLOW.md) (for P2+ incidents)
