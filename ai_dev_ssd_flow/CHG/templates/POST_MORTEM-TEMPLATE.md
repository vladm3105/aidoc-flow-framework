---
title: "Post-Mortem: {CHG-ID}"
tags:
  - post-mortem
  - incident-review
  - change-management
  - shared-architecture
custom_fields:
  document_type: post-mortem
  chg_reference: CHG-EMG-{YYYYMMDD-HHMM}
  incident_ticket: INC-XXX
  post_mortem_date: YYYY-MM-DDTHH:MM:SS
  post_mortem_facilitator: {Name}
  blameless: true
---

# Post-Mortem: {CHG-ID}

> **Incident**: {Brief description}
> **CHG Reference**: CHG-EMG-{YYYYMMDD-HHMM}
> **Incident Ticket**: INC-XXX

## 1. Executive Summary

### 1.1 Incident Overview

| Field | Value |
|-------|-------|
| **Incident Type** | P1 / Critical Security / Data Breach |
| **Start Time** | {YYYY-MM-DDTHH:MM:SS HH:MM TZ} |
| **End Time** | {YYYY-MM-DDTHH:MM:SS HH:MM TZ} |
| **Duration** | {X hours Y minutes} |
| **Detection Method** | {Monitoring/User Report/Security Scan} |
| **Time to Detect (TTD)** | {X minutes} |
| **Time to Mitigate (TTM)** | {X minutes} |
| **Time to Resolve (TTR)** | {X hours} |

### 1.2 Impact Summary

| Metric | Value |
|--------|-------|
| **Users Affected** | {number} |
| **Transactions Affected** | {number or N/A} |
| **Revenue Impact** | {$ amount or "None quantified"} |
| **SLA Breach** | Yes / No |
| **Data Exposure** | Yes / No |

### 1.3 Quick Summary

{2-3 sentence summary of what happened, what broke, how it was fixed}

## 2. Timeline

### 2.1 Detailed Timeline

| Time (TZ) | Event | Actor | Notes |
|-----------|-------|-------|-------|
| {HH:MM} | {First symptom observed} | {Monitoring} | |
| {HH:MM} | {Alert triggered} | {System} | |
| {HH:MM} | {On-call paged} | {PagerDuty} | |
| {HH:MM} | {On-call acknowledged} | {Name} | |
| {HH:MM} | {P1 declared} | {Name} | |
| {HH:MM} | {Incident commander assigned} | {Name} | |
| {HH:MM} | {Root cause identified} | {Name} | |
| {HH:MM} | {Hotfix developed} | {Name} | |
| {HH:MM} | {Hotfix deployed} | {Name} | |
| {HH:MM} | {Resolution confirmed} | {Name} | |
| {HH:MM} | {All-clear announced} | {IC} | |

### 2.2 Timeline Visualization

```
{time}  ┌──────────────────┐
        │ Incident Start   │
        └────────┬─────────┘
                 │
{time}  ┌────────▼─────────┐
        │ Detection        │ TTD: {X min}
        └────────┬─────────┘
                 │
{time}  ┌────────▼─────────┐
        │ P1 Declared      │
        └────────┬─────────┘
                 │
{time}  ┌────────▼─────────┐
        │ RCA Complete     │
        └────────┬─────────┘
                 │
{time}  ┌────────▼─────────┐
        │ Mitigation       │ TTM: {X min}
        └────────┬─────────┘
                 │
{time}  ┌────────▼─────────┐
        │ Resolution       │ TTR: {X hours}
        └──────────────────┘
```

## 3. Root Cause Analysis

### 3.1 5-Whys Analysis

**Problem Statement**: {What was the observed problem?}

1. **Why** did {symptom} occur?
   - Because {first-level cause}

2. **Why** did {first-level cause} happen?
   - Because {second-level cause}

3. **Why** did {second-level cause} happen?
   - Because {third-level cause}

4. **Why** did {third-level cause} happen?
   - Because {fourth-level cause}

5. **Why** did {fourth-level cause} happen?
   - Because {ROOT CAUSE}

### 3.2 Root Cause Statement

**Root Cause**: {Clear, specific statement of the root cause}

**Root Cause Layer**: L{N} - {Layer Name}

### 3.3 Contributing Factors

| Factor | Impact | Layer |
|--------|--------|-------|
| {Factor 1} | {How it contributed} | L{N} |
| {Factor 2} | {How it contributed} | L{N} |
| {Factor 3} | {How it contributed} | L{N} |

### 3.4 Trigger vs. Root Cause

| Aspect | Description |
|--------|-------------|
| **Trigger** | {What initiated the incident} |
| **Root Cause** | {Underlying flaw that allowed trigger to cause incident} |
| **Why the difference matters** | {Fixing only trigger would leave system vulnerable} |

## 4. Impact Assessment

### 4.1 User Impact

| User Segment | Impact | Duration |
|--------------|--------|----------|
| {Segment 1} | {What they experienced} | {How long} |
| {Segment 2} | {What they experienced} | {How long} |

### 4.2 Business Impact

| Metric | Impact | Quantification |
|--------|--------|----------------|
| Revenue | {Description} | {$ or %} |
| Reputation | {Description} | {Qualitative} |
| Operations | {Description} | {Hours/cost} |
| Compliance | {Description} | {SLA breach?} |

### 4.3 Technical Impact

| System/Service | Impact | Recovery Time |
|----------------|--------|---------------|
| {Service 1} | {Down/Degraded} | {Time} |
| {Service 2} | {Down/Degraded} | {Time} |

## 5. Resolution Details

### 5.1 Immediate Fix (Hotfix)

| Aspect | Details |
|--------|---------|
| **What was changed** | {Description} |
| **Why this fixed it** | {Explanation} |
| **Files/Components** | {List} |
| **Commit/PR** | {Reference} |

### 5.2 Fix Verification

| Verification | Result |
|--------------|--------|
| Smoke test passed | Yes / No |
| Error rates normalized | Yes / No |
| User access restored | Yes / No |
| Monitoring alerts cleared | Yes / No |

### 5.3 Permanent Fix (if different from hotfix)

| Aspect | Details |
|--------|---------|
| **CHG Reference** | CHG-XX for permanent fix |
| **Planned Changes** | {Description} |
| **Timeline** | {When} |

## 6. Lessons Learned

### 6.1 What Went Well

| # | Observation | Impact |
|---|-------------|--------|
| 1 | {Something that worked well} | {Positive impact} |
| 2 | {Something that worked well} | {Positive impact} |
| 3 | {Something that worked well} | {Positive impact} |

### 6.2 What Went Poorly

| # | Observation | Impact | Improvement |
|---|-------------|--------|-------------|
| 1 | {Something that didn't work} | {Negative impact} | {How to improve} |
| 2 | {Something that didn't work} | {Negative impact} | {How to improve} |
| 3 | {Something that didn't work} | {Negative impact} | {How to improve} |

### 6.3 Where We Got Lucky

| # | Lucky Break | If We Hadn't Been Lucky |
|---|-------------|------------------------|
| 1 | {Something fortunate} | {What could have happened} |
| 2 | {Something fortunate} | {What could have happened} |

## 7. Action Items

### 7.1 Preventive Actions (Must Do)

| ID | Action | Owner | Priority | Due Date | CHG | Status |
|----|--------|-------|----------|----------|-----|--------|
| 1 | {Action to prevent recurrence} | {Name} | High | {Date} | CHG-XX | Pending |
| 2 | {Action to prevent recurrence} | {Name} | High | {Date} | CHG-YY | Pending |
| 3 | {Action to prevent recurrence} | {Name} | High | {Date} | CHG-ZZ | Pending |

### 7.2 Detective Actions (Should Do)

| ID | Action | Owner | Priority | Due Date | CHG | Status |
|----|--------|-------|----------|----------|-----|--------|
| 4 | {Better detection/monitoring} | {Name} | Medium | {Date} | CHG-AA | Pending |
| 5 | {Better alerting} | {Name} | Medium | {Date} | CHG-BB | Pending |

### 7.3 Process Improvements (Nice to Have)

| ID | Action | Owner | Priority | Due Date | Status |
|----|--------|-------|----------|----------|--------|
| 6 | {Process improvement} | {Name} | Low | {Date} | Pending |
| 7 | {Documentation update} | {Name} | Low | {Date} | Pending |

## 8. Appendices

### 8.1 Related Documents

| Document | Link |
|----------|------|
| CHG Document | CHG-EMG-{timestamp}.md |
| Incident Ticket | INC-XXX |
| Hotfix PR | PR-XXX |
| Monitoring Dashboard | {link} |

### 8.2 Participants

| Role | Name | Participation |
|------|------|---------------|
| Incident Commander | {Name} | Coordinated response |
| On-Call Engineer | {Name} | Initial response |
| Subject Matter Expert | {Name} | Root cause analysis |
| Post-Mortem Facilitator | {Name} | Facilitated review |

### 8.3 Post-Mortem Meeting Details

| Field | Value |
|-------|-------|
| **Date** | {YYYY-MM-DDTHH:MM:SS} |
| **Duration** | {X hours} |
| **Attendees** | {List} |
| **Format** | {In-person/Video} |

---

## Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Post-Mortem Facilitator | | | [ ] |
| Technical Lead | | | [ ] |
| Engineering Manager | | | [ ] |

---

**Blameless Reminder**: This post-mortem follows blameless principles. Focus on systems and processes, not individuals. The goal is learning and improvement, not blame assignment.
