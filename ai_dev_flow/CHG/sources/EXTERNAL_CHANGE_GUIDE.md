---
title: "External Change Guide"
tags:
  - change-management
  - change-source
  - external
  - security
  - dependencies
  - shared-architecture
custom_fields:
  document_type: guide
  artifact_type: CHG
  change_source: external
  origin_layers: null
  development_status: active
---

# External Change Guide

**Change Source**: External (Environment-Driven)
**Origin Layers**: Outside the 15-layer system
**Direction**: Inject at appropriate layer based on impact
**Entry Gate**: GATE-05 (typically) or EMERGENCY BYPASS

---

## Gate Entry Point

| Trigger Type | Severity | Entry Gate | Process |
|--------------|----------|------------|---------|
| Security (CVSS >= 9.0) | Critical | **EMERGENCY BYPASS** | Hotfix → Post-mortem |
| Security (CVSS 7.0-8.9) | High | **GATE-05** (Expedited) | 72h SLA |
| Security (CVSS < 7.0) | Medium/Low | **GATE-05** | Standard |
| Dependency Update | Varies | **GATE-05** | Standard |
| API Change | Varies | **GATE-05** | Standard |
| Infrastructure EOL | Varies | **GATE-05** or **GATE-01** | Depends on scope |

| Attribute | Value |
|-----------|-------|
| **Primary Entry Gate** | GATE-05 |
| **Emergency Entry** | BYPASS (for CVSS >= 9.0 or active exploit) |
| **Validation Script** | `./CHG/scripts/validate_gate05.sh` |
| **Emergency Script** | `./CHG/scripts/validate_emergency_bypass.sh` |
| **Full Workflow** | `workflows/MIDSTREAM_WORKFLOW.md` or `workflows/EMERGENCY_WORKFLOW.md` |

**Security vulnerability response:**
```bash
# For critical security (CVSS >= 9.0)
./CHG/scripts/validate_emergency_bypass.sh <CHG_DIR>

# For standard external changes
./CHG/scripts/validate_gate05.sh <CHG_FILE>
```

---

## 1. Overview

External changes originate from outside the project - dependencies, security vulnerabilities, third-party APIs, infrastructure changes, or compliance mandates. They must be analyzed to determine which layer to inject the change.

```
┌─────────────────────────────────────────────────────────────┐
│                   EXTERNAL CHANGE FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              EXTERNAL TRIGGERS                       │   │
│  │  • Security vulnerability (CVE)                     │   │
│  │  • Dependency deprecation                           │   │
│  │  • Third-party API change                          │   │
│  │  • Infrastructure EOL                               │   │
│  │  • Compliance mandate                               │   │
│  │  • License change                                   │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│             ┌─────────────────────────┐                    │
│             │   IMPACT ASSESSMENT     │                    │
│             │   Which layer affected? │                    │
│             └───────────┬─────────────┘                    │
│                         │                                   │
│    ┌────────────────────┼────────────────────┐             │
│    │                    │                    │             │
│    ▼                    ▼                    ▼             │
│ ┌──────┐          ┌──────────┐         ┌──────────┐       │
│ │ L1-L4│          │  L5-L11  │         │ L12-L14  │       │
│ │Policy│          │Architecture│       │  Code    │       │
│ │Impact│          │  Impact   │         │  Impact │       │
│ └──┬───┘          └────┬─────┘         └────┬────┘       │
│    │                   │                    │             │
│    ▼                   ▼                    ▼             │
│ L3 Major          L2-L3              L1-L2               │
│ Full cascade      Partial cascade    Limited scope       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 2. External Trigger Types

### 2.1 Security Vulnerabilities

| Trigger | Example | Urgency | Typical Level |
|---------|---------|---------|---------------|
| Critical CVE | RCE in framework | Immediate | L1-L3 |
| High CVE | Auth bypass | 24 hours | L1-L2 |
| Medium CVE | Info disclosure | 1 week | L1 |
| Low CVE | Minor issue | Next release | L1 |

### 2.2 Dependency Changes

| Trigger | Example | Urgency | Typical Level |
|---------|---------|---------|---------------|
| Library EOL | Python 2.7 sunset | Planned | L3 |
| Major version | Django 3→4 | Planned | L2-L3 |
| Minor version | requests 2.28→2.29 | Normal | L1-L2 |
| Patch version | Security fix | Normal | L1 |

### 2.3 Third-Party API Changes

| Trigger | Example | Urgency | Typical Level |
|---------|---------|---------|---------------|
| API sunset | v1 deprecated | Planned | L3 |
| Breaking change | Response format | Planned | L2-L3 |
| New endpoint | Additional capability | Normal | L2 |
| Rate limit change | Throttling added | Normal | L1-L2 |

### 2.4 Infrastructure Changes

| Trigger | Example | Urgency | Typical Level |
|---------|---------|---------|---------------|
| Cloud service EOL | Service deprecated | Planned | L3 |
| Region change | Data residency | Planned | L2-L3 |
| Capacity change | Scale requirements | Normal | L2 |
| Config change | Env vars | Normal | L1 |

### 2.5 Compliance Mandates

| Trigger | Example | Urgency | Typical Level |
|---------|---------|---------|---------------|
| New regulation | GDPR, CCPA | Deadline | L3 |
| Certification | SOC2, ISO27001 | Planned | L2-L3 |
| Audit finding | Security gap | Urgent | L1-L3 |
| Policy update | Internal security | Normal | L1-L2 |

## 3. Impact Assessment

### 3.1 Determining Injection Point

Ask these questions to find where to inject the change:

| Question | If Yes → Inject At |
|----------|-------------------|
| Does it change business requirements? | L1 BRD |
| Does it change product features? | L2 PRD |
| Does it change acceptance criteria? | L4 BDD |
| Does it change architecture? | L5 ADR |
| Does it change system requirements? | L6 SYS |
| Does it change API contracts? | L8 CTR |
| Does it change implementation design? | L9 SPEC |
| Does it only affect code? | L12 Code |

### 3.2 Impact Matrix by External Type

| External Type | Injection Point | Cascade |
|---------------|-----------------|---------|
| Security (critical) | Varies | Emergency process |
| Dependency (major) | ADR (L5) | Full (L5-L14) |
| Dependency (minor) | SPEC (L9) | Partial (L9-L14) |
| Dependency (patch) | Code (L12) | None |
| Third-party API | CTR (L8) | L8-L14 |
| Infrastructure | ADR/SYS (L5-L6) | L5-L14 |
| Compliance | BRD (L1) | Full (L1-L14) |

## 4. Security Response Process

### 4.1 Security Severity Classification

| CVSS Score | Severity | Response Time | Process |
|------------|----------|---------------|---------|
| 9.0-10.0 | Critical | Immediate | Emergency CHG |
| 7.0-8.9 | High | 24 hours | Fast-track CHG |
| 4.0-6.9 | Medium | 1 week | Normal CHG |
| 0.1-3.9 | Low | Next release | L1 patch |

### 4.2 Emergency Security Response

```
┌─────────────────────────────────────────────────────────────┐
│            EMERGENCY SECURITY RESPONSE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PHASE 1: TRIAGE (1-4 hours)                               │
│  ───────────────────────────                                │
│  1. Assess vulnerability severity                          │
│  2. Determine if exploitable                               │
│  3. Identify affected components                           │
│  4. Decide: patch, workaround, or disable                  │
│                                                             │
│  PHASE 2: MITIGATE (4-24 hours)                            │
│  ─────────────────────────────                              │
│  1. Apply immediate workaround if possible                 │
│  2. Create emergency CHG (minimal documentation)           │
│  3. Implement fix                                          │
│  4. Deploy to production                                   │
│                                                             │
│  PHASE 3: DOCUMENT (24-72 hours)                           │
│  ──────────────────────────────                             │
│  1. Complete CHG documentation                             │
│  2. Update affected artifacts                              │
│  3. Run full test suite                                    │
│  4. Conduct post-mortem                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Security CHG Template Additions

For security-related CHGs, include:

```markdown
## Security Details

### Vulnerability Information
| Field | Value |
|-------|-------|
| CVE ID | CVE-XXXX-XXXXX |
| CVSS Score | X.X |
| Severity | Critical/High/Medium/Low |
| Attack Vector | Network/Local/Physical |
| Exploitability | Proven/Theoretical/Unknown |

### Affected Components
- Component A: [version range]
- Component B: [version range]

### Remediation
- [ ] Patch applied
- [ ] Workaround implemented
- [ ] Component disabled
- [ ] Mitigating controls added

### Disclosure
- [ ] Internal notification sent
- [ ] Customer notification (if required)
- [ ] Public disclosure (if required)
```

## 5. Dependency Update Process

### 5.1 Major Version Update (L3)

```
┌─────────────────────────────────────────────────────────────┐
│            MAJOR DEPENDENCY UPDATE (L3)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CREATE CHG                                              │
│     - CHG-XX_dependency_upgrade/                           │
│     - Document breaking changes                            │
│                                                             │
│  2. ASSESS ARCHITECTURE IMPACT                              │
│     - Review ADRs for affected patterns                    │
│     - Update ADR if architecture changes                   │
│                                                             │
│  3. UPDATE CONTRACTS                                        │
│     - Review CTR for API changes                           │
│     - Update contracts if affected                         │
│                                                             │
│  4. UPDATE SPEC                                             │
│     - Modify implementation details                        │
│     - Update to new API patterns                           │
│                                                             │
│  5. UPDATE TSPEC                                            │
│     - Update tests for new behavior                        │
│     - Add migration tests                                  │
│                                                             │
│  6. UPDATE TASKS                                            │
│     - Include migration steps                              │
│                                                             │
│  7. IMPLEMENT & TEST                                        │
│     - Apply changes                                        │
│     - Run full test suite                                  │
│     - Performance testing                                  │
│                                                             │
│  8. CLOSE CHG                                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Minor/Patch Update (L1-L2)

```
1. Review changelog for breaking changes
2. Update dependency version
3. Run test suite
4. If tests pass → L1 commit
5. If tests fail → L2 CHG with fixes
```

## 6. Third-Party API Changes

### 6.1 API Migration Process

```
┌─────────────────────────────────────────────────────────────┐
│              THIRD-PARTY API MIGRATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ASSESS CHANGES                                          │
│     - Review API changelog                                 │
│     - Identify breaking vs non-breaking                    │
│     - Map old → new endpoints/fields                       │
│                                                             │
│  2. UPDATE CTR                                              │
│     - Modify contract definitions                          │
│     - Update request/response schemas                      │
│     - Version contract if breaking                         │
│                                                             │
│  3. UPDATE SPEC                                             │
│     - Modify integration code design                       │
│     - Handle backward compatibility if needed              │
│                                                             │
│  4. UPDATE TSPEC                                            │
│     - Update ITEST for new API                            │
│     - Add migration tests                                  │
│     - Mock new API responses                               │
│                                                             │
│  5. IMPLEMENT                                               │
│     - Update integration code                              │
│     - Handle deprecation warnings                          │
│                                                             │
│  6. VALIDATE                                                │
│     - Test against sandbox/staging                         │
│     - Verify production compatibility                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 7. Compliance Change Process

### 7.1 Regulatory Compliance (L3)

New regulations typically require full cascade:

```
1. Update BRD with compliance requirement
2. Update PRD with affected features
3. Generate EARS for compliance rules
4. Create BDD acceptance scenarios
5. Create/update ADR for compliance architecture
6. Update SYS with quality attributes
7. Create REQ atomic requirements
8. Update CTR (data handling, APIs)
9. Update SPEC (implementation)
10. Update TSPEC (compliance tests)
11. Generate TASKS
12. Implement and validate
13. Document compliance evidence
```

### 7.2 Audit Finding Response

| Finding Severity | Response | Level |
|------------------|----------|-------|
| Critical | Immediate remediation | L2-L3 |
| High | 30-day remediation | L2 |
| Medium | 90-day remediation | L1-L2 |
| Low | Next release | L1 |

## 8. Examples

### 8.1 Example: Critical CVE in Dependency

**Trigger**: CVE-2024-XXXXX in logging library (CVSS 9.8)

```
Response: Emergency Process
Level: L1-L2 (depending on fix complexity)

Actions:
1. Assess exploitability (is our code vulnerable?)
2. Apply workaround (disable affected feature)
3. Create emergency CHG-07_cve_logging/
4. Update dependency to patched version
5. Run security-focused tests
6. Deploy to production
7. Complete documentation post-deployment
8. Notify stakeholders
```

### 8.2 Example: Major Framework Update

**Trigger**: Django 4.x to Django 5.x migration

```
Level: L3 Major
Entry Point: ADR (architecture patterns)

Actions:
1. Create CHG-08_django5_migration/
2. Review Django 5.x breaking changes
3. Update ADR with new patterns
4. Update SPEC for new APIs
5. Update TSPEC with deprecation handling
6. Migrate code incrementally
7. Run full test suite
8. Performance testing
9. Staged rollout
10. Close CHG
```

### 8.3 Example: GDPR Compliance

**Trigger**: GDPR data export requirement

```
Level: L3 Major
Entry Point: BRD (business requirement)

Actions:
1. Create CHG-09_gdpr_compliance/
2. Update BRD-01 with GDPR requirement
3. Create PRD feature for data export
4. Generate EARS compliance rules
5. Create BDD acceptance scenarios
6. Create ADR for data handling architecture
7. Update SYS with privacy requirements
8. Create REQ atomic requirements
9. Update CTR with export API
10. Generate SPEC
11. Create TSPEC with compliance tests
12. Generate TASKS
13. Implement
14. Validate and document evidence
15. Close CHG
```

---

**Related Documents**:
- [CHANGE_MANAGEMENT_GUIDE.md](../CHANGE_MANAGEMENT_GUIDE.md)
- [SECURITY_RESPONSE_TEMPLATE.md](../SECURITY_RESPONSE_TEMPLATE.md) (if exists)
