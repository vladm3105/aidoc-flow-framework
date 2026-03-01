---
title: "RISKSPEC-MVP-TEMPLATE: Risk Analysis Specification (MVP)"
tags:
  - riskspec-template
  - mvp-template
  - layer-9-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  instance_document_type: riskspec-document
  deliverable_type: risk
  artifact_type: RISKSPEC
  layer: 9
  subtype_code: 53
  parent_type: SPEC
  ctr_required: false
  readiness_score: RISK-Ready
  schema_reference: "RISKSPEC_MVP_SCHEMA.yaml"
  schema_version: "1.0"
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `RISKSPEC-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `RISKSPEC_MVP_SCHEMA.yaml`
> - **Parent**: SPEC (orchestrator) - routes here when `deliverable_type == 'risk'`

---

> **Document Authority**: This is the STANDARD for RISKSPEC (Risk Analysis Specification) structure.
> Schema: `RISKSPEC_MVP_SCHEMA.yaml v1.0` | Rules: `RISKSPEC_MVP_CREATION_RULES.md`, `RISKSPEC_MVP_VALIDATION_RULES.md`

<!--
AI_CONTEXT_START
Role: AI Risk Analyst
Objective: Create risk analysis specification for system components.
Constraints:
- One RISKSPEC per risk domain or component.
- Define risks, impacts, controls, and mitigations.
- CTR (Contract) is NOT required - no external interface.
- RISK-Ready threshold: >= 90%.
- Use established risk frameworks (ISO31000, NIST, FAIR).
- Include quantitative or qualitative assessments.
- Element IDs use codes 65-68 for risks, controls, mitigations, assessments.
AI_CONTEXT_END
-->

**MVP Template** - Risk Analysis Specification for risk assessment and control.

References: Schema `RISKSPEC_MVP_SCHEMA.yaml` | Rules `RISKSPEC_MVP_CREATION_RULES.md`, `RISKSPEC_MVP_VALIDATION_RULES.md`

# RISKSPEC-NN: [Component/Domain Name] Risk Specification

**Deliverable Type**: `risk`
**CTR Required**: No (no external interface)

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 1.0.0 |
| **Date Created** | YYYY-MM-DDTHH:MM:SS |
| **Last Updated** | YYYY-MM-DDTHH:MM:SS |
| **Author** | [Author name] |
| **Risk Domain** | [Domain/component name] |
| **Deliverable Type** | risk |
| **Risk Framework** | ISO31000 / NIST / FAIR / custom |
| **RISK-Ready Score** | [XX]% (Target: >= 90%) |

---

## 2. Traceability

### 2.1 Upstream Sources

| Type | ID | Title | Relevant Sections |
|------|-----|-------|-------------------|
| REQ | REQ-NN | [Requirements title] | [Sections] |
| ADR | ADR-NN | [Architecture decision] | [Sections] |
| SYS | SYS-NN | [System design] | [Risk-related sections] |

### 2.2 Cumulative Tags

```yaml
brd: "@brd: BRD.NN.EE.SS"
prd: "@prd: PRD.NN.EE.SS"
ears: "@ears: EARS.NN.EE.SS"
bdd: "@bdd: BDD.NN.EE.SS"
adr: "@adr: ADR-NN"
sys: "@sys: SYS.NN.EE.SS"
req: "@req: REQ.NN.EE.SS"
```

### 2.3 Downstream Consumers

| Type | ID | Purpose |
|------|-----|---------|
| TASKS | TASKS-NN | Risk mitigation tasks |
| Policies | policies/[domain]/ | Policy documents |
| Controls | controls/[domain]/ | Control implementation |

---

## 3. Risk Specification

### 3.1 Risk Framework

| Property | Value |
|----------|-------|
| Framework | ISO31000 / NIST / FAIR / custom |
| Assessment Type | qualitative / quantitative / hybrid |
| Risk Tolerance | low / medium / high |

### 3.2 Risk Matrix

| Likelihood | 1 (Rare) | 2 (Unlikely) | 3 (Possible) | 4 (Likely) | 5 (Almost Certain) |
|------------|----------|--------------|--------------|------------|---------------------|
| **5 (Catastrophic)** | Medium | High | Critical | Critical | Critical |
| **4 (Major)** | Low | Medium | High | Critical | Critical |
| **3 (Moderate)** | Low | Medium | Medium | High | High |
| **2 (Minor)** | Low | Low | Medium | Medium | High |
| **1 (Insignificant)** | Low | Low | Low | Medium | Medium |

### 3.3 Risk Register

| ID | Category | Description | Likelihood | Impact | Risk Score | Strategy |
|----|----------|-------------|------------|--------|------------|----------|
| RISKSPEC.NN.65.01 | operational | [Risk description] | [1-5] | [1-5] | [L x I] | avoid/transfer/mitigate/accept |
| RISKSPEC.NN.65.02 | financial | [Risk description] | [1-5] | [1-5] | [L x I] | avoid/transfer/mitigate/accept |
| RISKSPEC.NN.65.03 | compliance | [Risk description] | [1-5] | [1-5] | [L x I] | avoid/transfer/mitigate/accept |
| RISKSPEC.NN.65.04 | security | [Risk description] | [1-5] | [1-5] | [L x I] | avoid/transfer/mitigate/accept |
| RISKSPEC.NN.65.05 | strategic | [Risk description] | [1-5] | [1-5] | [L x I] | avoid/transfer/mitigate/accept |

---

## 4. Controls

### 4.1 Control Register

| ID | Risk ID | Control Type | Description | Owner | Status |
|----|---------|--------------|-------------|-------|--------|
| RISKSPEC.NN.66.01 | RISKSPEC.NN.65.01 | preventive | [Control description] | [Owner] | planned/implemented/verified |
| RISKSPEC.NN.66.02 | RISKSPEC.NN.65.01 | detective | [Control description] | [Owner] | planned/implemented/verified |
| RISKSPEC.NN.66.03 | RISKSPEC.NN.65.02 | corrective | [Control description] | [Owner] | planned/implemented/verified |

### 4.2 Control Types

| Type | Purpose | Examples |
|------|---------|----------|
| Preventive | Stop risk from occurring | Access controls, validation, encryption |
| Detective | Identify when risk occurs | Monitoring, logging, auditing |
| Corrective | Respond after risk occurs | Incident response, recovery procedures |

---

## 5. Mitigations

### 5.1 Mitigation Strategies

| ID | Risk ID | Strategy | Implementation | Timeline | Cost |
|----|---------|----------|----------------|----------|------|
| RISKSPEC.NN.67.01 | RISKSPEC.NN.65.01 | mitigate | [Implementation details] | [Timeline] | [Cost estimate] |
| RISKSPEC.NN.67.02 | RISKSPEC.NN.65.02 | transfer | [Insurance/contract details] | [Timeline] | [Cost estimate] |
| RISKSPEC.NN.67.03 | RISKSPEC.NN.65.03 | avoid | [Process change details] | [Timeline] | [Cost estimate] |

### 5.2 Strategy Definitions

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| Avoid | Eliminate the risk by removing the cause | High impact, can change approach |
| Transfer | Shift risk to third party | Can be insured or contracted |
| Mitigate | Reduce likelihood or impact | Risk acceptable with controls |
| Accept | Acknowledge and monitor | Low risk, cost exceeds benefit |

---

## 6. Assessments

### 6.1 Impact Assessments

| ID | Risk ID | Impact Area | Current State | Target State | Gap |
|----|---------|-------------|---------------|--------------|-----|
| RISKSPEC.NN.68.01 | RISKSPEC.NN.65.01 | operations | [Current] | [Target] | [Gap] |
| RISKSPEC.NN.68.02 | RISKSPEC.NN.65.01 | financial | [Current] | [Target] | [Gap] |
| RISKSPEC.NN.68.03 | RISKSPEC.NN.65.01 | reputation | [Current] | [Target] | [Gap] |

### 6.2 Residual Risk

| Risk ID | Inherent Score | Controls Applied | Residual Score | Acceptable |
|---------|----------------|------------------|----------------|------------|
| RISKSPEC.NN.65.01 | [Score] | RISKSPEC.NN.66.01, RISKSPEC.NN.66.02 | [Score] | Yes/No |
| RISKSPEC.NN.65.02 | [Score] | RISKSPEC.NN.66.03 | [Score] | Yes/No |

---

## 7. Monitoring

### 7.1 Key Risk Indicators (KRIs)

| KRI | Risk ID | Threshold | Frequency | Owner |
|-----|---------|-----------|-----------|-------|
| [Indicator name] | RISKSPEC.NN.65.01 | [Threshold value] | daily/weekly/monthly | [Owner] |

### 7.2 Review Schedule

| Activity | Frequency | Responsible | Last Review | Next Review |
|----------|-----------|-------------|-------------|-------------|
| Risk register review | quarterly | Risk Owner | YYYY-MM-DD | YYYY-MM-DD |
| Control effectiveness | semi-annual | Control Owner | YYYY-MM-DD | YYYY-MM-DD |
| Framework assessment | annual | Risk Committee | YYYY-MM-DD | YYYY-MM-DD |

---

## 8. Verification

### 8.1 BDD Scenarios

- `04_BDD/BDD-NN_{suite}/BDD-NN.SS_risk_controls.feature#control-verification`

### 8.2 Audit Tests

| Type | Coverage | Path |
|------|----------|------|
| Control Testing | >= 100% critical controls | audits/controls/[domain]/ |
| Compliance Audit | >= 90% | audits/compliance/[domain]/ |

---

**Template Version**: 1.0
**Last Updated**: 2026-03-01
