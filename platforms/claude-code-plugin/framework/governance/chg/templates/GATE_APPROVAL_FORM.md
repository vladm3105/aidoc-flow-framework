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
| **Change Level** | C1 / C2 / C3 |
| **Change Source** | Upstream / Midstream / Design / Execution / External / Feedback / Spec |
| **Entry Gate** | GATE-01 / GATE-03 / GATE-06 / GATE-08 / GATE-CODE / GATE-SPEC |
| **SemVer Impact** | major / minor / patch (`Spec` change_source only) |
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

### 2.1 GATE-01: Business/Product (L1-L2)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not entry gate)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-01-E001: Business justification | [ ] Pass / [ ] Fail | |
| GATE-01-E002: PRD links to BRD | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-01-E003: Breaking change classified | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-01-E004: C3 stakeholder approval | [ ] Pass / [ ] Fail / [ ] N/A | |

**Warnings Addressed**:
- [ ] GATE-01-W001: Large scope reviewed
- [ ] GATE-01-W002: C2 approval obtained
- [ ] GATE-01-W003: Implementation plan created

**GATE-01 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.2 GATE-03: Requirements & Architecture (L3-L5)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not in cascade path)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-03-E001: ADR structure complete | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-03-E002: Security review complete | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-03-E003: EARS syntax valid | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-03-E004: BDD format valid | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-03-E005: EARS 2 upstream tags | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-03-E006: BDD 3 upstream tags | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-03-E007: ADR 4 upstream tags | [ ] Pass / [ ] Fail / [ ] N/A | |

**Warnings Addressed**:
- [ ] GATE-03-W001: CVE reference added
- [ ] GATE-03-W002: ADR alternatives documented
- [ ] GATE-03-W003: BDD edge cases covered
- [ ] GATE-03-W004: EARS boundary values covered

**GATE-03 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.3 GATE-06: Design & Test (L6-L7)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not in cascade path)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-06-E001: SPEC TDD-Ready >= 90% | [ ] Pass / [ ] Fail | Score: ___% |
| GATE-06-E002: TDD covers BDD scenarios | [ ] Pass / [ ] Fail | |
| GATE-06-E003: TDD/SPEC aligned | [ ] Pass / [ ] Fail | |
| GATE-06-E004: SPEC change → TDD updated | [ ] Pass / [ ] Fail | |

**Warnings Addressed**:
- [ ] GATE-06-W001: Performance baseline documented
- [ ] GATE-06-W002: Complexity acceptable

**GATE-06 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.4 GATE-08: IPLAN (L8)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not in cascade path)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-08-E001: File manifest complete | [ ] Pass / [ ] Fail | |
| GATE-08-E002: Test-first order enforced | [ ] Pass / [ ] Fail | |
| GATE-08-E003: @spec/@tdd tags present | [ ] Pass / [ ] Fail | |
| GATE-08-E004: Session handoff documented | [ ] Pass / [ ] Fail | |

**Warnings Addressed**:
- [ ] GATE-08-W001: Manifest size acceptable
- [ ] GATE-08-W002: Implementation contracts defined
- [ ] GATE-08-W003: Rollback procedure documented

**GATE-08 Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.5 GATE-CODE: Implementation (Code)

**Applicable**: [ ] Yes / [ ] No

| Check | Status | Notes |
|-------|--------|-------|
| GATE-CODE-E001: RCA completed | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-CODE-E002: Fix at correct layer | [ ] Pass / [ ] Fail | |
| GATE-CODE-E003: TDD test suite passes | [ ] Pass / [ ] Fail | |
| GATE-CODE-E004: Code review approved | [ ] Pass / [ ] Fail | |

**Warnings Addressed**:
- [ ] GATE-CODE-W001: Performance benchmarked
- [ ] GATE-CODE-W002: Build warnings addressed
- [ ] GATE-CODE-W003: Tech debt tracked

**GATE-CODE Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

### 2.6 GATE-SPEC: Framework Specification (meta — `Spec` change_source)

**Applicable**: [ ] Yes / [ ] No / [ ] N/A (not a `framework/` spec change)

| Check | Status | Notes |
|-------|--------|-------|
| GATE-SPEC-E001: Provenance (`why` + `trigger`) | [ ] Pass / [ ] Fail | |
| GATE-SPEC-E002: `semver_impact` set; `major` ⇒ C3 | [ ] Pass / [ ] Fail | |
| GATE-SPEC-E003: Not C1 (≥ C2) | [ ] Pass / [ ] Fail | |
| GATE-SPEC-E004: C3 human approval recorded | [ ] Pass / [ ] Fail / [ ] N/A | |
| GATE-SPEC-E005: `framework/VERSION` bumped (CI) | [ ] Pass / [ ] Fail | |
| GATE-SPEC-E006: both `FRAMEWORK_SPEC_VERSION` match (CI) | [ ] Pass / [ ] Fail | |
| GATE-SPEC-E007: conformance suite green (CI) | [ ] Pass / [ ] Fail | |
| GATE-SPEC-E008: `CHANGELOG.md` updated (CI) | [ ] Pass / [ ] Fail | |

**Warnings Addressed**:
- [ ] GATE-SPEC-W001: `major` change has a per-platform migration note
- [ ] GATE-SPEC-W002: both platforms track the new spec version (no parity drift)

**GATE-SPEC Result**: [ ] PASS / [ ] PASS WITH WARNINGS / [ ] FAIL

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
| **C1** | Self-approval (author) |
| **C2** | PO + TL (GATE-01), TL + Domain (GATE-03), TL (GATE-06), TL (GATE-08), TL + QA (GATE-CODE) |
| **C3** | Full board per gate + stakeholder |

### 4.2 Approvals

#### GATE-01 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Product Owner | | | [ ] Approve / [ ] Reject | [ ] |
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Stakeholder (C3) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-03 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Domain Expert | | | [ ] Approve / [ ] Reject | [ ] |
| Architect (C3) | | | [ ] Approve / [ ] Reject | [ ] |
| Security (C3/External) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-06 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Domain Expert (C3) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-08 Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Domain Expert (C3) | | | [ ] Approve / [ ] Reject | [ ] |

#### GATE-CODE Approval (if applicable)

| Role | Name | Date | Decision | Signature |
|------|------|------|----------|-----------|
| Technical Lead | | | [ ] Approve / [ ] Reject | [ ] |
| QA Lead | | | [ ] Approve / [ ] Reject | [ ] |
| Architect (C3) | | | [ ] Approve / [ ] Reject | [ ] |

## 5. Final Decision

### 5.1 Overall Gate Status

| Gate | Status |
|------|--------|
| GATE-01 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-03 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-06 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-08 | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-CODE | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |
| GATE-SPEC | [ ] Pass / [ ] Pass w/Warnings / [ ] Fail / [ ] N/A |

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

**Related Documents**:
- CHG Document: `CHG-XX/CHG-XX.yaml`
- Gate Documentation: `gates/GATE-*.md`
