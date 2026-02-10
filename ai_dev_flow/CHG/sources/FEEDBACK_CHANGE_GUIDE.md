---
title: "Feedback Change Guide"
tags:
  - change-management
  - change-source
  - feedback
  - production
  - user-feedback
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: CHG
  change_source: feedback
  origin_layers: null
  development_status: active
---

# Feedback Change Guide

**Change Source**: Feedback (Production-Driven)
**Origin Layers**: Post-Layer 14 (Production environment)
**Direction**: Loop back to source layer based on root cause
**Entry Gate**: GATE-12 or EMERGENCY BYPASS (for P1)

---

## Gate Entry Point

| Feedback Type | Priority | Entry Gate | Process |
|---------------|----------|------------|---------|
| P1 Incident | Critical | **EMERGENCY BYPASS** | Hotfix → Post-mortem |
| P2-P4 Incident | Standard | **GATE-12** | Standard with RCA |
| User Feedback | Varies | **GATE-12** or higher | Based on impact |
| Performance Issue | Varies | **GATE-12** or **GATE-09** | Based on RCA |
| Analytics Insight | Strategic | **GATE-01** | Full cascade |

| Attribute | Value |
|-----------|-------|
| **Primary Entry Gate** | GATE-12 |
| **Emergency Entry** | BYPASS (for P1 incidents) |
| **Validation Script** | `./CHG/scripts/validate_gate12.sh` |
| **Emergency Script** | `./CHG/scripts/validate_emergency_bypass.sh` |
| **Full Workflow** | `workflows/DOWNSTREAM_WORKFLOW.md` or `workflows/EMERGENCY_WORKFLOW.md` |

**Incident response routing:**
```bash
# For P1 incidents
./CHG/scripts/validate_emergency_bypass.sh <CHG_DIR>

# For standard feedback (P2-P4, user feedback)
./CHG/scripts/validate_gate12.sh <CHG_FILE>
```

**Root cause determines final routing** - bubble up to appropriate gate based on RCA.

---

## 1. Overview

Feedback changes originate from production operations, user feedback, and analytics insights. They loop back into the development workflow at the appropriate layer based on root cause analysis.

```
┌─────────────────────────────────────────────────────────────┐
│                   FEEDBACK CHANGE FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│            ┌─────────────────────────────┐                 │
│            │       PRODUCTION            │                 │
│            │  ┌─────────────────────┐   │                 │
│            │  │ • Monitoring/Alerts │   │                 │
│            │  │ • User Feedback     │   │                 │
│            │  │ • Support Tickets   │   │                 │
│            │  │ • Analytics Data    │   │                 │
│            │  │ • Incident Reports  │   │                 │
│            │  └──────────┬──────────┘   │                 │
│            └─────────────┼──────────────┘                 │
│                          │                                 │
│                          ▼                                 │
│            ┌─────────────────────────────┐                 │
│            │    ROOT CAUSE ANALYSIS      │                 │
│            │    Where should fix go?     │                 │
│            └─────────────┬───────────────┘                 │
│                          │                                 │
│    ┌─────────────────────┼─────────────────────┐          │
│    │                     │                     │          │
│    ▼                     ▼                     ▼          │
│ ┌──────────┐       ┌──────────┐        ┌──────────┐      │
│ │ HOTFIX   │       │ DESIGN   │        │ PRODUCT  │      │
│ │ Code bug │       │ ISSUE    │        │ CHANGE   │      │
│ │ (L12)    │       │ (L5-L11) │        │ (L1-L4)  │      │
│ └────┬─────┘       └────┬─────┘        └────┬─────┘      │
│      │                  │                   │            │
│      ▼                  ▼                   ▼            │
│   L1 Patch         L2 Minor            L2-L3            │
│                                                             │
│            ◄───── FEEDBACK LOOP ─────►                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. Feedback Types

### 2.1 Production Incidents

| Incident Type | Example | Urgency | Typical Level |
|---------------|---------|---------|---------------|
| P1 - Critical | Service down | Immediate | L1-L3 |
| P2 - High | Major feature broken | 4 hours | L1-L2 |
| P3 - Medium | Feature degraded | 24 hours | L1-L2 |
| P4 - Low | Minor issue | 1 week | L1 |

### 2.2 User Feedback

| Feedback Type | Example | Response | Typical Level |
|---------------|---------|----------|---------------|
| Bug report | "Button doesn't work" | Investigate | L1-L2 |
| Feature request | "Need export option" | Evaluate | L2-L3 |
| UX complaint | "Confusing workflow" | Analyze | L2 |
| Performance issue | "App is slow" | Profile | L1-L2 |

### 2.3 Analytics Insights

| Insight Type | Example | Action | Typical Level |
|--------------|---------|--------|---------------|
| Unused feature | "0.1% usage rate" | Deprecation eval | L2-L3 |
| High error rate | "5% failure rate" | Investigation | L1-L2 |
| Performance trend | "P95 increasing" | Optimization | L1-L2 |
| User drop-off | "80% abandon checkout" | UX review | L2 |

### 2.4 Operational Insights

| Insight Type | Example | Action | Typical Level |
|--------------|---------|--------|---------------|
| Capacity issue | "DB at 90% CPU" | Scale/optimize | L1-L2 |
| Cost anomaly | "Costs doubled" | Investigation | L1-L2 |
| Security event | "Unusual access pattern" | Security review | L1-L3 |
| Log analysis | "Recurring error pattern" | Bug fix | L1-L2 |

## 3. Incident Response Process

### 3.1 P1 Critical Incident

```
┌─────────────────────────────────────────────────────────────┐
│               P1 CRITICAL INCIDENT RESPONSE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: DETECT & ALERT (0-5 min)                         │
│  ─────────────────────────────────                          │
│  • Monitoring triggers alert                               │
│  • On-call engineer notified                               │
│  • Incident channel opened                                 │
│                                                             │
│  PHASE 2: TRIAGE (5-15 min)                                │
│  ─────────────────────────                                  │
│  • Assess impact (users affected)                          │
│  • Identify affected component                             │
│  • Determine if rollback possible                          │
│                                                             │
│  PHASE 3: MITIGATE (15-60 min)                             │
│  ─────────────────────────────                              │
│  • Rollback if possible                                    │
│  • Apply hotfix if identified                              │
│  • Enable failover if available                            │
│                                                             │
│  PHASE 4: RESOLVE (1-4 hours)                              │
│  ────────────────────────────                               │
│  • Root cause analysis                                     │
│  • Implement permanent fix                                 │
│  • Deploy fix                                              │
│                                                             │
│  PHASE 5: POST-MORTEM (24-72 hours)                        │
│  ──────────────────────────────────                         │
│  • Document incident                                       │
│  • Identify preventive measures                            │
│  • Create follow-up CHG if needed                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Incident-to-CHG Flow

```
Incident Detected
       │
       ▼
┌─────────────────┐
│ Hotfix Applied? │
└────────┬────────┘
         │
    ┌────┴────┐
    │ YES     │ NO
    ▼         ▼
┌────────┐  ┌────────────┐
│ L1     │  │ Requires   │
│ Patch  │  │ design     │
│        │  │ change?    │
└────────┘  └─────┬──────┘
                  │
             ┌────┴────┐
             │ YES     │ NO
             ▼         ▼
        ┌────────┐  ┌────────┐
        │ L2-L3  │  │ L1     │
        │ CHG    │  │ Patch  │
        └────────┘  └────────┘
```

## 4. User Feedback Process

### 4.1 Feedback Triage

```
┌─────────────────────────────────────────────────────────────┐
│                 USER FEEDBACK TRIAGE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. COLLECT                                                 │
│     • Support tickets                                      │
│     • App store reviews                                    │
│     • Social media                                         │
│     • In-app feedback                                      │
│     • User interviews                                      │
│                                                             │
│  2. CATEGORIZE                                              │
│     ┌─────────────┬─────────────┬─────────────┐            │
│     │    BUG      │  FEATURE    │     UX      │            │
│     │  REPORT     │  REQUEST    │  FEEDBACK   │            │
│     └──────┬──────┴──────┬──────┴──────┬──────┘            │
│            │             │             │                   │
│            ▼             ▼             ▼                   │
│       Downstream    Upstream      Midstream                │
│       (L12-L14)     (L1-L4)       (L5-L11)                 │
│                                                             │
│  3. PRIORITIZE                                              │
│     • Impact (users affected)                              │
│     • Frequency (how often reported)                       │
│     • Severity (workaround available?)                     │
│     • Strategic alignment                                  │
│                                                             │
│  4. ROUTE                                                   │
│     • Bug → Downstream change guide                        │
│     • Feature → Upstream change guide                      │
│     • UX → Midstream change guide                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Bug Report Workflow

```
1. Reproduce the issue
   - Verify user steps
   - Check logs for errors

2. Root cause analysis
   - Is it a code bug? → L1 fix
   - Is it a design flaw? → L2 CHG
   - Is it a requirement gap? → L2-L3 CHG

3. Fix and validate
   - Implement fix at appropriate layer
   - Test fix resolves issue
   - Verify no regression

4. Communicate
   - Update ticket
   - Notify user
   - Close feedback loop
```

### 4.3 Feature Request Workflow

```
1. Capture request
   - Document use case
   - Identify user segment

2. Evaluate
   - Aligns with product strategy?
   - Technical feasibility?
   - Resource availability?

3. If approved
   - Create PRD entry (Upstream change)
   - Follow L2-L3 process

4. Communicate
   - Acknowledge request
   - Provide timeline if approved
   - Explain rationale if declined
```

## 5. Analytics-Driven Changes

### 5.1 Usage Analytics

| Metric | Signal | Action |
|--------|--------|--------|
| Feature usage <1% | Potential deprecation | Evaluate L3 deprecation |
| Feature usage growing | Validate investment | Consider enhancement |
| Error rate >1% | Quality issue | Investigate, L1-L2 fix |
| Performance degradation | Optimization needed | L1-L2 optimization |

### 5.2 Analytics-to-Change Flow

```
Analytics Insight
       │
       ▼
┌─────────────────────────┐
│ Validate with           │
│ qualitative data        │
│ (user feedback, support)│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ Determine change type   │
│ • Optimize (L1-L2)      │
│ • Enhance (L2)          │
│ • Redesign (L2-L3)      │
│ • Deprecate (L3)        │
└───────────┬─────────────┘
            │
            ▼
   Route to appropriate
   change process
```

### 5.3 Unused Feature Deprecation

When analytics show a feature is unused:

```
1. Verify with multiple data sources
   - Analytics (quantitative)
   - User feedback (qualitative)
   - Support tickets

2. Assess impact of removal
   - Who uses it?
   - What's the workaround?
   - Dependencies?

3. If deprecation approved
   - Create L3 CHG
   - Follow deprecation timeline:
     a. Announce deprecation
     b. Disable for new users
     c. Notify existing users
     d. Remove feature
     e. Archive artifacts
```

## 6. Post-Mortem Process

### 6.1 When to Conduct Post-Mortem

- All P1 incidents
- P2 incidents lasting >1 hour
- Any incident with customer impact
- Any incident revealing systemic issues

### 6.2 Post-Mortem Template

```markdown
## Incident Post-Mortem: [Title]

**Date**: YYYY-MM-DDTHH:MM:SS
**Duration**: X hours Y minutes
**Severity**: P1/P2/P3/P4
**Impact**: [Users/revenue/systems affected]

### Timeline
| Time | Event |
|------|-------|
| HH:MM | Incident detected |
| HH:MM | Team assembled |
| HH:MM | Root cause identified |
| HH:MM | Fix deployed |
| HH:MM | Incident resolved |

### Root Cause
[Detailed explanation of what caused the incident]

### Contributing Factors
- Factor 1
- Factor 2

### Resolution
[What was done to resolve the incident]

### What Went Well
- Point 1
- Point 2

### What Could Be Improved
- Point 1
- Point 2

### Action Items
| Action | Owner | Due Date | CHG |
|--------|-------|----------|-----|
| Action 1 | Name | Date | CHG-XX |
| Action 2 | Name | Date | L1 |

### Lessons Learned
[Key takeaways for the team]
```

### 6.3 Post-Mortem to CHG

Post-mortem action items become CHG documents:

| Action Item Type | CHG Level |
|------------------|-----------|
| Monitoring improvement | L1-L2 |
| Code fix | L1 |
| Architecture change | L3 |
| Process improvement | L1-L2 |
| Documentation | L1 |

## 7. Feedback Loop Metrics

### 7.1 Key Metrics to Track

| Metric | Target | Indicates |
|--------|--------|-----------|
| Mean Time to Detect (MTTD) | <5 min | Monitoring effectiveness |
| Mean Time to Resolve (MTTR) | <1 hour | Response capability |
| Change Failure Rate | <5% | Deploy quality |
| Customer-reported bugs | Decreasing | Product quality |
| Feature adoption rate | >50% | Product-market fit |

### 7.2 Feedback Quality

| Indicator | Good | Needs Improvement |
|-----------|------|-------------------|
| Bug reproducibility | >90% | <70% |
| Feature request clarity | Clear use case | Vague need |
| Analytics actionability | Clear signal | Noise |

## 8. Examples

### 8.1 Example: Production Incident → Hotfix

**Trigger**: P1 - Login service returning 500 errors

```
Response Time: Immediate
Level: L1 Patch

Timeline:
09:00 - Alert triggered
09:05 - Engineer on call
09:15 - Root cause: null pointer in session handler
09:30 - Hotfix deployed
09:35 - Service restored

Post-mortem Action:
- Add null check in session handler (L1)
- Add integration test for edge case (L1)
- Improve monitoring (L1)
```

### 8.2 Example: User Feedback → UX Improvement

**Trigger**: "I can't find the export button" (50+ reports)

```
Level: L2 Minor
Entry Point: SPEC (L9)

Actions:
1. Analyze user journey
2. Create CHG-10_export_visibility/
3. Update SPEC with UI changes
4. Update TSPEC (FTEST for usability)
5. Update TASKS
6. Implement UI changes
7. A/B test improvement
8. Measure impact
9. Close CHG
```

### 8.3 Example: Analytics → Feature Deprecation

**Trigger**: Analytics show "Legacy Report" used by 0.5% of users

```
Level: L3 Major
Entry Point: PRD (L2)

Actions:
1. Verify with user interviews
2. Identify the 0.5% - any critical users?
3. Create CHG-11_legacy_report_deprecation/
4. Announce deprecation (30 days notice)
5. Update PRD to remove feature
6. Update EARS/BDD to remove scenarios
7. Update downstream artifacts
8. Archive related code
9. Remove from UI
10. Close CHG
```

---

**Related Documents**:
- [CHANGE_MANAGEMENT_GUIDE.md](../CHANGE_MANAGEMENT_GUIDE.md)
- [DOWNSTREAM_CHANGE_GUIDE.md](./DOWNSTREAM_CHANGE_GUIDE.md)
- [UPSTREAM_CHANGE_GUIDE.md](./UPSTREAM_CHANGE_GUIDE.md)
