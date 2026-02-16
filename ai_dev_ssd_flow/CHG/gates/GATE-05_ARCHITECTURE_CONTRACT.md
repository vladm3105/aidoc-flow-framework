---
title: "GATE-05: Architecture/Contract Gate"
tags:
  - change-management
  - gate-system
  - layer-boundary
  - shared-architecture
custom_fields:
  document_type: gate-definition
  artifact_type: CHG
  gate_number: 5
  layer_range: "L5-L8"
  layer_names: ["ADR", "SYS", "REQ", "CTR"]
  development_status: active
---

# GATE-05: Architecture/Contract Gate (L5-L8)

> **Position**: Before Layers 5-8 (ADR, SYS, REQ, CTR)
> **Change Sources**: Midstream, External (technical)
> **Purpose**: Validate architecture and contract changes before cascading to design

## 1. Purpose & Scope

GATE-05 validates changes to architectural decisions, system requirements, atomic requirements, and API contracts. These changes have significant downstream impact and require technical review to prevent integration issues.

### 1.1 Layers Covered

| Layer | Artifact | Description |
|-------|----------|-------------|
| L5 | ADR | Architecture Decision Record |
| L6 | SYS | System Requirements |
| L7 | REQ | Atomic Requirements |
| L8 | CTR | API/Data Contracts |

### 1.2 Typical Change Sources

- **Midstream**: Technology decisions, design optimization, architecture pivots
- **External**: Security vulnerabilities, dependency updates, third-party API changes
- **Upstream (Cascaded)**: Business requirements flowing from GATE-01

## 2. Entry Criteria

Before entering GATE-05, the change request must satisfy:

| Criterion | Required | Validation |
|-----------|----------|------------|
| Technical rationale documented | Yes | Context-Decision-Consequences format for ADR |
| Impact on downstream layers assessed | Yes | CTR/SPEC/TSPEC impact analysis |
| Breaking change status determined | Yes | API compatibility assessment |
| Security review (if external) | Conditional | CVE reference or security assessment |
| GATE-01 passed (if upstream cascade) | Conditional | GATE-01 approval documented |

### 2.1 Pre-Gate Checklist

```markdown
- [ ] Technical rationale documented
- [ ] Downstream impact analysis completed
- [ ] Breaking change status determined
- [ ] If external security: CVE/advisory referenced
- [ ] If from GATE-01: upstream approval confirmed
- [ ] For L3: Architecture board notified
```

## 3. Validation Checklist

### 3.1 Error Checks (Blocking)

| Check ID | Description | Severity | Validation |
|----------|-------------|----------|------------|
| GATE-05-E001 | ADR must document context, decision, consequences | ERROR | Section presence check |
| GATE-05-E002 | SYS quality attributes must be measurable | ERROR | Quantified threshold check |
| GATE-05-E003 | REQ must have 6 upstream traceability tags | ERROR | `@brd:`, `@prd:`, `@ears:`, `@bdd:`, `@adr:`, `@sys:` |
| GATE-05-E004 | CTR schema must validate (YAML + MD sync) | ERROR | Schema validation script |
| GATE-05-E005 | Breaking API change without L3 classification | ERROR | Change level validation |
| GATE-05-E006 | Missing security review for external change | ERROR | Security assessment present |

### 3.2 Warning Checks (Non-Blocking)

| Check ID | Description | Severity | Recommendation |
|----------|-------------|----------|----------------|
| GATE-05-W001 | External security change without CVE reference | WARNING | Add CVE-YYYY-NNNN reference |
| GATE-05-W002 | CTR version increment without changelog | WARNING | Document API changes |
| GATE-05-W003 | ADR alternatives section missing | WARNING | Document considered alternatives |
| GATE-05-W004 | REQ SPEC-Ready score < 90% | WARNING | Improve requirement completeness |

## 4. Approval Workflow

### 4.1 Approval Matrix

| Change Level | Required Approvers | SLA |
|--------------|-------------------|-----|
| **L1** | Self (author) | Immediate |
| **L2** | Technical Lead + Domain Expert | 3 business days |
| **L3** | Architect + Security (if external) | 5 business days |

### 4.2 Special Approval Requirements

| Change Type | Additional Approvers |
|-------------|---------------------|
| Breaking API change | API consumers affected |
| Security vulnerability fix | Security team |
| Architecture pivot (ADR change) | Architecture board |
| Contract deprecation | All contract consumers |

### 4.3 Escalation Path

```
L1 (Self-approved)
     │
     ▼ (if contract change)
L2 (TL + Domain)
     │
     ▼ (if breaking or security)
L3 (Architect + Security)
```

## 5. Exit Criteria

To pass GATE-05, the change must satisfy:

| Criterion | L1 | L2 | L3 |
|-----------|----|----|---|
| All E-level checks pass | Yes | Yes | Yes |
| W-level checks addressed | No | Review | Must address |
| Technical rationale documented | Yes | Yes | Yes |
| Contract compatibility verified | N/A | Yes | Yes |
| Security review complete | N/A | If external | Yes |
| Migration plan documented | No | No | Yes |

### 5.1 Exit Checklist

```markdown
- [ ] GATE-05-E* checks all pass
- [ ] GATE-05-W* checks reviewed
- [ ] ADR has Context-Decision-Consequences
- [ ] SYS has measurable quality attributes
- [ ] REQ has 6 upstream traceability tags
- [ ] CTR validates (if present)
- [ ] Security review complete (if external)
- [ ] Approvals obtained per matrix
```

## 6. Routing Rules

After passing GATE-05:

| Scenario | Next Step |
|----------|-----------|
| Change affects L9-L11 (SPEC, TSPEC, TASKS) | Proceed to GATE-09 |
| Change affects L12-L14 only (Code, Tests, Val) | Proceed to GATE-12 |
| L1 Patch (single layer fix) | Direct implementation |
| CTR change requiring consumer notification | Consumer notification + GATE-09 |

### 6.1 Routing Flowchart

```
                    GATE-05 PASSED
                          │
                          ▼
            ┌─────────────────────────┐
            │ Does change affect SPEC?│
            └───────────┬─────────────┘
                        │
         ┌──────────────┼──────────────┐
         │ Yes          │              │ No
         ▼              │              ▼
    ┌─────────┐         │       ┌─────────────────┐
    │ GATE-09 │         │       │ Code-only fix?  │
    └─────────┘         │       └────────┬────────┘
                        │                │
                        │     ┌──────────┼──────────┐
                        │     │ Yes      │          │ No (Tests)
                        │     ▼          │          ▼
                        │ ┌─────────┐    │    ┌─────────┐
                        │ │ GATE-12 │    │    │ GATE-09 │
                        │ └─────────┘    │    └─────────┘
```

## 7. Error Catalog

### 7.1 GATE-05 Error Codes

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-05-E001 | Structure | ADR missing required sections | Add Context, Decision, Consequences sections |
| GATE-05-E002 | Quality | SYS attributes not measurable | Add quantified thresholds (e.g., "< 100ms") |
| GATE-05-E003 | Traceability | REQ missing upstream tags | Add all 6 traceability tags |
| GATE-05-E004 | Validation | CTR schema invalid | Fix YAML schema or MD sync |
| GATE-05-E005 | Classification | Breaking API misclassified | Escalate to L3 |
| GATE-05-E006 | Security | External change missing security review | Complete security assessment |
| GATE-05-W001 | Documentation | CVE reference missing | Add CVE-YYYY-NNNN to change document |
| GATE-05-W002 | Documentation | CTR changelog missing | Document version changes |
| GATE-05-W003 | Completeness | ADR alternatives not documented | Add "Considered Alternatives" section |
| GATE-05-W004 | Readiness | REQ SPEC-Ready score low | Improve requirement completeness |

### 7.2 Common Resolutions

```markdown
## GATE-05-E001 Resolution
ADR must contain:

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Decision
[What is the change that we're proposing and/or doing?]

## Consequences
[What becomes easier or more difficult to do because of this change?]

## GATE-05-E003 Resolution
REQ must have all 6 upstream tags:

@brd: BRD-XXX
@prd: PRD-XXX.YY
@ears: EARS.XXX.YY.ZZ
@bdd: SCEN-XXX
@adr: ADR-XXX
@sys: SYS-XXX-XXX
```

## 8. Special Considerations

### 8.1 Contract Deprecation Process

For CTR deprecation (L3):

1. Notify all contract consumers
2. Document deprecation timeline
3. Provide migration guide
4. Set sunset date (minimum 30 days)
5. Create replacement contract if applicable

### 8.2 Security Vulnerability Response

For external security changes:

| CVSS Score | Response Time | Gate Process |
|------------|---------------|--------------|
| Critical (9.0-10.0) | 24 hours | Emergency Bypass |
| High (7.0-8.9) | 72 hours | Expedited GATE-05 |
| Medium (4.0-6.9) | 7 days | Standard GATE-05 |
| Low (0.1-3.9) | 30 days | Standard GATE-05 |

## 9. Validation Script

Validation is performed by `scripts/validate_gate05.sh`:

```bash
# Usage
./CHG/scripts/validate_gate05.sh <CHG_FILE> [--verbose]

# Exit Codes
# 0 = Pass (no errors, no warnings)
# 1 = Pass with warnings (non-blocking)
# 2 = Fail (blocking errors)
```

---

**Related Documents**:
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
- [../workflows/MIDSTREAM_WORKFLOW.md](../workflows/MIDSTREAM_WORKFLOW.md)
- [../workflows/UPSTREAM_WORKFLOW.md](../workflows/UPSTREAM_WORKFLOW.md) (cascaded changes)
