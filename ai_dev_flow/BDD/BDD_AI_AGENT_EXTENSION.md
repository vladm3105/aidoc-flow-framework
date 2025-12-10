# =============================================================================
# 📋 Document Role: This is an EXTENSION to BDD-TEMPLATE.feature
# - Authority: BDD-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: Additional requirements for AI-Agent Primary architecture BDD files
# - Scope: Applies to BDD files with AGENT-NNN identifiers
# - On conflict: Defer to BDD-TEMPLATE.feature for base requirements
# =============================================================================
---
title: "BDD AI-Agent Extension"
tags:
  - extension-rules
  - layer-4-artifact
  - ai-agent-primary
custom_fields:
  document_type: extension-rules
  artifact_type: BDD
  layer: 4
  priority: ai-agent-primary
  development_status: active
---

# BDD AI-Agent Extension

**Version**: 1.0
**Date**: 2025-11-30
**Purpose**: Additional standards for AI-Agent Primary architecture BDD files
**Applies To**: BDD-022, BDD-023, BDD-025, and future AI-agent BDD documents
**Base Template**: BDD-TEMPLATE.feature (all base requirements apply)

---

## 1. Scope

This extension applies to BDD feature files that document AI-Agent Primary architecture components:

| BDD ID | Agent ID | Agent Name | Description |
|--------|----------|------------|-------------|
| BDD-022 | AGENT-001 | Fraud Detection Agent | ML-based risk scoring |
| BDD-023 | AGENT-002 | Compliance AML Agent | SAR automation, KYT monitoring |
| BDD-025 | AGENT-004 | Transaction Orchestrator | Payment FSM, partner routing |

---

## 2. Required Metadata Fields

### 2.1 Document Control Extension

AI-Agent BDD files MUST include the following additional field in Document Control:

```markdown
| **Architecture** | AI-Agent Primary (AGENT-NNN) |
```

**Full Document Control Example**:
```markdown
## Document Control

| Item | Details |
|------|---------|
| **Project Name** | [Project Name] |
| **Document Version** | 1.0.0 |
| **Date** | YYYY-MM-DD |
| **Document Owner** | [Team Name] |
| **Prepared By** | [Author Name] |
| **Status** | Draft |
| **Architecture** | AI-Agent Primary (AGENT-NNN) |
| **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
```

### 2.2 Feature-Level Tags

AI-Agent BDD files MUST include the `@ctr:CTR-005` tag for A2A Protocol compliance:

```gherkin
@brd:BRD.NNN.001
@prd:PRD.NNN.001
@ears:EARS.NNN.001
@ctr:CTR-005
Feature: [Agent Feature Title]
  Architecture: AI-Agent Primary (AGENT-NNN)
```

---

## 3. Agent-Specific Scenario Categories

In addition to the standard 8 scenario categories, AI-Agent BDD files SHOULD include:

### 3.1 A2A Communication Scenarios

```gherkin
# ===================
# A2A COMMUNICATION SCENARIOS
# ===================

@primary @functional @a2a_protocol
Scenario: Successfully send request via A2A Protocol
  Given AGENT-NNN is active
  And A2A Protocol messaging is enabled per @ctr:CTR-005
  When AGENT-NNN sends request to AGENT-YYY
  Then A2A message is delivered within @threshold:PRD-NNN:timeout.a2a.delivery
  And acknowledgment is received
```

### 3.2 ML Inference Scenarios (for ML-based agents)

```gherkin
# ===================
# ML INFERENCE SCENARIOS
# ===================

@primary @functional @ml_inference
Scenario: Successfully execute ML model inference
  Given ML model is loaded and ready
  When inference request is submitted
  Then prediction is returned within @threshold:PRD-NNN:perf.ml.p95_latency
  And confidence score is above @threshold:PRD-NNN:ml.confidence.min
```

### 3.3 Model Drift Detection Scenarios

```gherkin
@negative @error_handling @model_drift
Scenario: Detect and alert on model drift
  Given daily model performance metrics are calculated
  And precision has dropped below @threshold:PRD-NNN:ml.drift.alert
  When model drift detection executes
  Then drift alert is emitted
  And data science team is notified
```

### 3.4 Agent Fallback Scenarios

```gherkin
@failure_recovery @resilience @fallback
Scenario: Activate fallback on agent failure
  Given AGENT-NNN primary service fails
  When fallback detection triggers
  Then traditional fallback system activates
  And service continuity is maintained
```

---

## 4. Entity Reference Requirements

AI-Agent BDD files SHOULD use `@entity` tags to reference PRD-004 entities:

```gherkin
And RiskEvaluationUnit entity is constructed per @entity: PRD.004.RiskEvaluationUnit
And ComplianceCase entity is created per @entity: PRD.004.ComplianceCase
And BusinessTransaction entity is updated per @entity: PRD.004.BusinessTransaction
```

---

## 5. Threshold Categories for AI Agents

AI-Agent BDD files SHOULD reference these threshold categories:

| Category | Usage | Example Key |
|----------|-------|-------------|
| `perf.ml.*` | ML inference latency | `perf.ml.fraud.p95` |
| `ml.confidence.*` | Model confidence thresholds | `ml.confidence.min` |
| `ml.drift.*` | Model drift detection | `ml.drift.alert` |
| `timeout.a2a.*` | A2A message delivery | `timeout.a2a.delivery` |
| `risk.*` | Risk score thresholds | `risk.high.min` |
| `compliance.*` | Compliance thresholds | `compliance.sar.filing_deadline` |

---

## 6. Header Comment Block

AI-Agent BDD files MUST include the architecture identifier in the header:

```gherkin
# =============================================================================
# BDD-NNN: [Agent Feature Title]
# =============================================================================
# POSITION: BDD is in Layer 4 (Testing Layer) - defines acceptance criteria
#
# ARCHITECTURE: AI-Agent Primary (AGENT-NNN)
# This document covers AI agent-based [description] via A2A Protocol.
#
# REQUIREMENTS VERIFIED:
#   - EARS-NNN: [Requirement description]
#   - BRD-NNN: [Business requirement reference]
#
# TRACEABILITY:
#   Upstream: BRD-NNN, PRD-NNN, EARS-NNN
#   Downstream: ADR, SYS, REQ, SPEC, Code, Tests
# =============================================================================
```

---

## 7. Validation Checklist

For AI-Agent BDD files, verify:

- [ ] Document Control includes `Architecture: AI-Agent Primary (AGENT-NNN)`
- [ ] Feature-level tags include `@ctr:CTR-005`
- [ ] A2A Communication scenarios present
- [ ] ML Inference scenarios present (for ML-based agents)
- [ ] Model Drift scenarios present (for ML-based agents)
- [ ] Agent Fallback scenarios present
- [ ] Entity references use `@entity: PRD.NNN.EntityName` format
- [ ] Threshold references use agent-specific categories
- [ ] Header includes ARCHITECTURE line

---

## 8. Agent ID Registry

| Agent ID | Name | BDD Document | Primary Function |
|----------|------|--------------|------------------|
| AGENT-001 | Fraud Detection Agent | BDD-022 | ML-based risk scoring |
| AGENT-002 | Compliance AML Agent | BDD-023 | SAR automation |
| AGENT-003 | (Reserved) | - | - |
| AGENT-004 | Transaction Orchestrator | BDD-025 | Payment FSM |

**ID Assignment Rules**:
- Sequential numbering (AGENT-001, AGENT-002, etc.)
- Never reuse IDs
- Stable once assigned
- Document in this registry when creating new agent BDD files

---

**Maintained By**: BeeLocal Engineering Team
**Review Frequency**: Updated with AI-agent architecture changes
