---
title: "Gate Approval Form"
tags:
  - change-management
  - gate-system
  - approval
  - shared-architecture
custom_fields:
  document_type: approval-form
  artifact_type: CHG
  development_status: active
---

# Gate Approval Form

> **CHG Reference**: CHG-XX
> **Change Title**: {Title}
> **Date**: {YYYY-MM-DDTHH:MM:SS}

## 1. Change Summary

### 1.1 Change Identification

| Field | Value |
|-------|-------|
| **CHG ID** | CHG-XX |
| **Change Title** | {Brief title} |
| **Change Level** | L1 / L2 / L3 |
| **Change Source** | Upstream / Midstream / Downstream / External / Feedback |
| **Entry Gate** | GATE-01 / GATE-05 / GATE-09 / GATE-12 |
| **Requested By** | {Name} |
| **Request Date** | {YYYY-MM-DDTHH:MM:SS} |

### 1.2 Change Description

{2-3 sentence description of what is being changed and why}

### 1.3 Scope

| Category | Items |
|----------|-------|
| **Layers Affected** | L{N}, L{M}, ... |
| **Artifacts Affected** | {List of artifacts} |
| **Services Affected** | {List of services} |
| **Breaking Changes** | Yes / No |

## 2. Gate Validation Results

### 2.1 GATE-01: Business/Product (L1-L4)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not entry gate)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-01-E001: Business justification | [ ] Pass / [ ] Fail | |
| GATE-01-E002: PRD links to BRD | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-01-E003: EARS syntax valid | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-01-E004: BDD format valid | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-01-E005: Breaking change classified | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-01-E006: L3 stakeholder approval | [ ] Pass / [ ] Fail / [ ] N/A | |

**Warnings Addressed**:
- [ ] GATE-01-W001: Large scope reviewed
- [ ] GATE-01-W002: L2 approval obtained
- [ ] GATE-01-W003: Implementation plan created
- [ ] GATE-01-W004: External reference added

**GATE-01 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.2 GATE-05: Architecture/Contract (L5-L8)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not in cascade path)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-05-E001: ADR structure complete | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-05-E002: SYS measurable | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-05-E003: REQ 6 traceability tags | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-05-E004: CTR validates | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-05-E005: Breaking API classified L3 | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-05-E006: Security review complete | [ ] Pass / [ ] Fail / [ ] N/A | |

**Warnings Addressed**:
- [ ] GATE-05-W001: CVE reference added
- [ ] GATE-05-W002: CTR changelog updated
- [ ] GATE-05-W003: ADR alternatives documented
- [ ] GATE-05-W004: REQ SPEC-Ready score improved

**GATE-05 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.3 GATE-09: Design/Test (L9-L11)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not in cascade path)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-09-E001: SPEC readiness >= 90% | [ ] Pass / [ ] Fail | Score: ___% |
| GATE-09-E002: TSPEC covers interfaces | [ ] Pass / [ ] Fail | |
| GATE-09-E003: TASKS linked | [ ] Pass / [ ] Fail | |
| GATE-09-E004: TSPEC/SPEC aligned | [ ] Pass / [ ] Fail | |
| GATE-09-E005: TDD order followed | [ ] Pass / [ ] Fail | |
| GATE-09-E006: No dependency cycles | [ ] Pass / [ ] Fail | |

**Warnings Addressed**:
- [ ] GATE-09-W001: Performance baseline documented
- [ ] GATE-09-W002: Edge cases covered
- [ ] GATE-09-W003: Complexity acceptable
- [ ] GATE-09-W004: Effort within capacity
- [ ] GATE-09-W005: Negative tests added

**GATE-09 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.4 GATE-12: Implementation (L12-L14)

**Applicable**: [ ] Yes / [ ] No

| Check | Status | Notes |
|-------|--------|-------|
| GATE-12-E001: RCA completed | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-12-E002: Fix at correct layer | [ ] Pass / [ ] Fail | |
| GATE-12-E003: Regression tests added | [ ] Pass / [ ] Fail | |
| GATE-12-E004: Code review approved | [ ] Pass / [ ] Fail | |
| GATE-12-E005: Build passes | [ ] Pass / [ ] Fail | |
| GATE-12-E006: Coverage maintained | [ ] Pass / [ ] Fail | |

**Warnings Addressed**:
- [ ] GATE-12-W001: TSPEC updated
- [ ] GATE-12-W002: Change level appropriate
- [ ] GATE-12-W003: Performance benchmarked
- [ ] GATE-12-W004: Security reviewed
- [ ] GATE-12-W005: Dead code removed

**GATE-12 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

## 3. Risk Assessment

### 3.1 Risk Matrix

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|------|------------|--------|------------|---------------|
| {Risk 1} | Low/Med/High | Low/Med/High | {Mitigation} | Low/Med/High |
| {Risk 2} | Low/Med/High | Low/Med/High | {Mitigation} | Low/Med/High |

### 3.2 Rollback Plan

| Step | Action | Command/Procedure | Owner |
|------|--------|-------------------|-------|
| 1 | {Action} | {How} | {Who} |
| 2 | {Action} | {How} | {Who} |

### 3.3 Rollback Trigger Criteria

- [ ] Error rate exceeds {X}%
- [ ] Response time exceeds {X}ms
- [ ] Critical functionality fails
- [ ] {Other criteria}

## 4. Approval Signatures

### 4.1 Required Approvers by Change Level

| Change Level | Required Approvers |
|--------------|-------------------|
| **L1** | Self-approval (author) |
| **L2** | Product Owner + Technical Lead (GATE-01), TL + Domain (GATE-05), TL (GATE-09), TL + QA (GATE-12) |
| **L3** | Full board per gate + stakeholder |

### 4.2 Approvals

#### GATE-01 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Product Owner | | | [ ] Approve / [ ] Reject | [ ] |
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Stakeholder (L3) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-05 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Domain Expert | | | [ ] Approve / [ ] Reject | [ ] |
| Architect (L3) | | | [ ] Approve / [ ] Reject | [ ] |
| Security (L3/External) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-09 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Domain Expert (L3) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-12 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| QA Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Architect (L3) | | | [ ] Approve / [ ] Reject | [ ] |

## 5. Final Decision

### 5.1 Overall Gate Status

| Gate | Status |
|------|--------|
| GATE-01 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-05 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-09 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-12 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |

### 5.2 Final Approval

| Decision | Date | Notes |
|----------|------|-------|
| [ ] **APPROVED** - Proceed with implementation | | |
| [ ] **APPROVED WITH CONDITIONS** - Proceed with noted conditions | | |
| [ ] **REJECTED** - Return for revision | | |
| [ ] **DEFERRED** - More information needed | | |

### 5.3 Conditions (if applicable)

| # | Condition | Must be addressed by |
|---|-----------|---------------------|
| 1 | | |
| 2 | | |

### 5.4 Final Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Change Author | | | [ ] |
| Final Approver | | | [ ] |

---

## Validation Script Results

```
# Paste validation script output here
./CHG/scripts/validate_all_gates.sh CHG-XX/CHG-XX.md

Exit Code:
Errors:
Warnings:
```

---

**Related Documents**:
- CHG Document: `CHG-XX/CHG-XX.md`
- Implementation Plan: `CHG-XX/implementation_plan.md`
- Gate Documentation: `gates/GATE-*.md`
