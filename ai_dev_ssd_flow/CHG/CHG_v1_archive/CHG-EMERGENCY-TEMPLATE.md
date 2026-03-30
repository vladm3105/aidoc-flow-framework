---
id: CHG-EMG-{YYYYMMDD-HHMM}
title: "EMERGENCY: {Brief Description}"
tags:
  - change-document
  - emergency
  - p1-incident
  - shared-architecture
custom_fields:
  document_type: change-record
  artifact_type: CHG
  change_level: EMERGENCY
  change_source: emergency
  development_status: in-progress
  gate_entry: BYPASS
status: In Progress
date: {YYYY-MM-DDTHH:MM:SS}
author: {On-call Engineer}
incident_ticket: {INC-XXX}
incident_commander: {Name}
bypass_authorized_by: {Name}
bypass_authorization_time: {YYYY-MM-DDTHH:MM:SS HH:MM TZ}
---

# CHG-EMG-{YYYYMMDD-HHMM}: EMERGENCY - {Brief Description}

> **Change Level**: EMERGENCY (Bypass)
> **Authorization**: {Incident Commander Name}
> **Incident Ticket**: {INC-XXX}

## 1. Incident Summary

### 1.1 Declaration

| Field | Value |
|-------|-------|
| **Incident Declared** | {YYYY-MM-DDTHH:MM:SS HH:MM TZ} |
| **Incident Commander** | {Name} |
| **Severity** | P1 / Critical Security |
| **Bypass Authorized By** | {Name} |
| **Bypass Authorization Time** | {YYYY-MM-DDTHH:MM:SS HH:MM TZ} |

### 1.2 Classification

| Criterion | Value |
|-----------|-------|
| **Emergency Type** | [ ] P1 Production Incident / [ ] Critical Security (CVSS >= 9.0) / [ ] Data Breach |
| **CVSS Score** | {N/A or 9.0-10.0} |
| **CVE Reference** | {CVE-YYYY-NNNNN or N/A} |
| **Active Exploitation** | Yes / No |

## 2. Problem Statement

### 2.1 Impact

| Metric | Value |
|--------|-------|
| **Users Affected** | {number or "all"} |
| **Revenue Impact** | {Yes/No, estimated amount} |
| **Services Down** | {list of services} |
| **Data at Risk** | {Yes/No, description} |

### 2.2 Description

{Brief description of the problem - what is happening and what is the impact}

### 2.3 Reproduction

```
{Steps to reproduce if applicable, or monitoring alerts}
```

## 3. Timeline

| Time (TZ) | Event | Actor |
|-----------|-------|-------|
| {HH:MM} | Incident detected | {Monitoring/User} |
| {HH:MM} | P1/Emergency declared | {Name} |
| {HH:MM} | Bypass authorized | {IC Name} |
| {HH:MM} | Hotfix started | {Engineer} |
| {HH:MM} | Hotfix deployed | {Engineer} |
| {HH:MM} | Resolution confirmed | {Name} |

## 4. Immediate Actions

### 4.1 Triage Phase (Complete within 30 min)

- [ ] Incident detected and confirmed
- [ ] Severity assessed (P1/Critical Security)
- [ ] Incident commander assigned
- [ ] Emergency bypass authorized
- [ ] This emergency stub created
- [ ] War room/channel established

### 4.2 Hotfix Phase (Complete within 4 hours)

- [ ] Root cause hypothesis formed
- [ ] Hotfix implementation started
- [ ] Second engineer reviewing
- [ ] Smoke test passed
- [ ] Rollback plan ready
- [ ] Deployment notification sent
- [ ] Hotfix deployed to production
- [ ] Resolution confirmed

### 4.3 Monitoring

- [ ] Error rates returned to baseline
- [ ] Response times returned to baseline
- [ ] No new critical errors
- [ ] Affected users can access service

## 5. Hotfix Details

### 5.1 Changes Made

| # | File/Component | Change | Reviewer |
|---|----------------|--------|----------|
| 1 | | | |
| 2 | | | |

### 5.2 Deployment Details

| Field | Value |
|-------|-------|
| **Branch** | {branch name} |
| **Commit** | {commit SHA} |
| **Deploy Time** | {HH:MM TZ} |
| **Deploy Method** | {direct/pipeline} |

### 5.3 Rollback Plan

If hotfix fails:

```bash
# Rollback commands
{git revert/deployment rollback commands}
```

## 6. Post-Incident Requirements (Complete within 72 hours)

### 6.1 Documentation (24 hours)

- [ ] Update this CHG with complete details
- [ ] Document all affected layers
- [ ] Document all changed artifacts
- [ ] Complete root cause analysis

### 6.2 Post-Mortem (72 hours)

- [ ] Create POST_MORTEM-{CHG-ID}.md
- [ ] Conduct post-mortem meeting
- [ ] Document timeline
- [ ] Complete 5-Whys analysis
- [ ] Identify contributing factors
- [ ] Document lessons learned

### 6.3 Retroactive Validation

- [ ] Validate GATE-12 requirements
- [ ] Validate GATE-09 requirements (if applicable)
- [ ] Validate GATE-05 requirements (if applicable)
- [ ] Validate GATE-01 requirements (if applicable)

### 6.4 Follow-Up CHGs

| Preventive Measure | CHG ID | Priority | Owner |
|--------------------|--------|----------|-------|
| | | | |
| | | | |

## 7. Root Cause Analysis (To Complete)

### 7.1 5-Whys

1. Why? {Complete after incident}
2. Why?
3. Why?
4. Why?
5. Why? (Root cause)

### 7.2 Root Cause Layer

**Layer**: L{N} - {Layer Name}
**Description**: {To complete}

## 8. Affected Artifacts (To Complete)

| Layer | Artifact | Impact | Status |
|-------|----------|--------|--------|
| L12 | | | |
| L13 | | | |
| | | | |

## 9. Closure

### 9.1 Emergency Resolution

| Criterion | Status |
|-----------|--------|
| Incident resolved | [ ] Yes |
| Services restored | [ ] Yes |
| Users can access | [ ] Yes |
| Monitoring normal | [ ] Yes |

### 9.2 Post-Incident Completion

| Criterion | Status | Due |
|-----------|--------|-----|
| Full CHG documentation | [ ] | +24h |
| Post-mortem document | [ ] | +72h |
| Post-mortem meeting | [ ] | +72h |
| Retroactive gate validation | [ ] | +72h |
| Follow-up CHGs created | [ ] | +72h |

### 9.3 Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| On-Call Engineer | | | [ ] |
| Incident Commander | | | [ ] |
| Technical Lead | | | [ ] |

---

## References

- **Post-Mortem**: `POST_MORTEM-{CHG-ID}.md` (to be created)
- **Incident Ticket**: {INC-XXX}
- **Monitoring Dashboard**: {link}
- **War Room Channel**: {link}
