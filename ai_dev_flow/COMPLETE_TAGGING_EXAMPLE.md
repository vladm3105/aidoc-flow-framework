---
title: "Complete Cumulative Tagging Example"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Complete Cumulative Tagging Example

**Version**: 1.1
**Purpose**: End-to-end example of cumulative tagging from BRD through Code
**Created**: 2025-11-13
**Updated**: 2025-11-26
**Status**: Reference Example

---

## Overview

This document demonstrates complete cumulative tagging through all 16 layers of the SDD workflow, from Strategy (Layer 0) through Validation (Layer 15). Each artifact shows:

- Required upstream tags for its layer
- Cumulative tag accumulation pattern
- Tag format (markdown, YAML, or Gherkin)
- Traceability to all upstream sources

**Example Feature**: Notification Service

---

## Layer 0: Strategy (External)

**Artifact**: `{domain_strategy}/product_strategy_v5.md`
**Required Tags**: None (0 tags)
**Format**: External document (not part of formal SDD workflow)

**Content Example**:
```markdown
## 4.2 Notification Logic

When notification criteria satisfied:
1. Determine notification channel (email, SMS, push)
2. Format message based on template
3. Send notification via provider integration
4. Track delivery status
5. Update notification history
```

**Note**: Strategy documents are external business logic. BRD references them but does not tag them.

---

## Layer 1: BRD (Business Requirements Document)

**Artifact**: `docs/BRD/BRD-009_notification_system.md`
**Required Tags**: None (0 tags)
**Format**: Markdown

**Content Example**:
```markdown
# BRD-009: Notification System Business Requirements

## 1. Executive Summary

Enable automated notification delivery through external provider APIs to support user communication.

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 1):
```markdown
# No upstream tags required for BRD (Layer 1 - top level)
```

**Upstream Sources**:
- Strategy: `{domain_strategy}/product_strategy_v5.md` section 4.2

**Downstream Artifacts**:
- PRD-016 (Product requirements for notification service)
- EARS-012 (Formal requirements)
```

**Tag Analysis**:
- Tag count: 0 (BRD is top-level artifact)
- No upstream dependencies
- Serves as traceability anchor for downstream artifacts

---

## Layer 2: PRD (Product Requirements Document)

**Artifact**: `docs/PRD/PRD-016_notification_service.md`
**Required Tags**: `@brd` (1 tag)
**Format**: Markdown

**Content Example**:
```markdown
# PRD-016: Notification Service Product Requirements

## 2. Problem Statement

Need UI and API for sending notifications through multiple channels.

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 2):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
```

**Tag Explanation**:
- BRD-009:FR-015 - Functional requirement for provider integration
- BRD-009:NFR-006 - Non-functional requirement for delivery performance

**Upstream Sources**:
- BRD-009 (Notification System Business Requirements)

**Downstream Artifacts**:
- EARS-012 (Formal WHEN-THE-SHALL-WITHIN requirements)
```

**Tag Analysis**:
- Tag count: 1 (cumulative: @brd)
- Includes ALL upstream tags from Layer 1
- References specific BRD functional and non-functional requirements

---

## Layer 3: EARS (Easy Approach to Requirements Syntax)

**Artifact**: `docs/EARS/EARS-012_notification_validation.md`
**Required Tags**: `@brd`, `@prd` (2 tags)
**Format**: Markdown

**Content Example**:
```markdown
# EARS-012: Notification Validation Requirements

## 3.1 Event-Driven Requirements

### EARS-012:EVENT-001
**WHEN** user selects "Send Notification" button
**THE** system **SHALL** validate notification parameters
**WITHIN** 100 milliseconds

### EARS-012:EVENT-002
**WHEN** notification validation succeeds
**THE** system **SHALL** submit notification to provider API
**WITHIN** 200 milliseconds

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 3):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
```

**Tag Explanation**:
- BRD-009:FR-015 - Provider integration capability
- BRD-009:NFR-006 - Performance requirements
- PRD-016:FEATURE-003 - Notification UI feature

**Upstream Sources**:
- BRD-009 (Business requirements)
- PRD-016 (Product requirements)

**Downstream Artifacts**:
- BDD-015 (Test scenarios for notification service)
```

**Tag Analysis**:
- Tag count: 2 (cumulative: @brd, @prd)
- Includes ALL upstream tags from Layers 1-2
- No gaps in tag chain

---

## Layer 4: BDD (Behavior-Driven Development)

**Artifact**: `docs/BDD/BDD-015_notification_service.feature`
**Required Tags**: `@brd`, `@prd`, `@ears` (3+ tags)
**Format**: Gherkin with tags

**Content Example**:
```gherkin
# BDD-015: Notification Service Test Scenarios

@brd:BRD-009:FR-015
@brd:BRD-009:NFR-006
@prd:PRD-016:FEATURE-003
@ears:EARS-012:EVENT-001
@ears:EARS-012:EVENT-002
Feature: Notification Service

  Scenario: Send valid email notification
    Given user is authenticated
    And notification service is available
    When user sends email notification with:
      | Recipient  | user@example.com |
      | Subject    | Test Message     |
      | Channel    | EMAIL            |
      | Priority   | HIGH             |
    Then notification validation completes within 100ms
    And notification is submitted to provider within 200ms
    And delivery confirmation is displayed

  Scenario: Reject invalid notification (missing recipient)
    Given user is authenticated
    And notification service is available
    When user attempts to send notification without recipient
    Then system rejects notification with error "MISSING_RECIPIENT"
    And error message is displayed within 100ms
```

**Tag Analysis**:
- Tag count: 3+ (cumulative: @brd, @prd, @ears)
- Gherkin format uses `@tag:value` syntax
- Tags appear before Feature declaration
- Includes ALL upstream tags from Layers 1-3

---

## Layer 5: ADR (Architecture Decision Record)

**Artifact**: `docs/ADR/ADR-033_notification_routing.md`
**Required Tags**: `@brd`, `@prd`, `@ears`, `@bdd` (4 tags)
**Format**: Markdown

**Content Example**:
```markdown
# ADR-033: Notification Routing Architecture

## Status
Accepted

## Context
Need architectural approach for routing notifications to appropriate providers.

## Decision
Implement asynchronous routing layer between API and provider integrations.

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 5):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
```

**Tag Explanation**:
- BRD-009:FR-015, NFR-006 - Business and performance requirements
- PRD-016:FEATURE-003 - Product feature specification
- EARS-012:EVENT-001, EVENT-002 - Formal behavioral requirements
- BDD-015:scenario-send-notification, scenario-reject-invalid - Test coverage

**Upstream Sources**:
- BRD-009, PRD-016, EARS-012, BDD-015

**Downstream Artifacts**:
- SYS-012 (System requirements)
```

**Tag Analysis**:
- Tag count: 4 (cumulative: @brd through @bdd)
- Includes ALL upstream tags from Layers 1-4
- Multiple requirement IDs per tag type
- No gaps in tag chain

---

## Layer 6: SYS (System Requirements)

**Artifact**: `docs/SYS/SYS-012_notification_service_system.md`
**Required Tags**: `@brd` through `@adr` (5 tags)
**Format**: Markdown

**Content Example**:
```markdown
# SYS-012: Notification Service System Requirements

## 2. Functional Requirements

### SYS-012:FUNC-001
System shall provide REST API endpoint for notification submission.

### SYS-012:PERF-001
Notification validation latency shall not exceed 100ms at 95th percentile.

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 6):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
@adr: ADR-033
```

**Tag Explanation**:
- All upstream tags from Layers 1-5
- ADR-033 defines architectural constraints for this system

**Upstream Sources**:
- BRD-009, PRD-016, EARS-012, BDD-015, ADR-033

**Downstream Artifacts**:
- REQ-045 (Atomic requirements)
```

**Tag Analysis**:
- Tag count: 5 (cumulative: @brd through @adr)
- Includes ALL upstream tags from Layers 1-5
- Complete chain validation: all layers present

---

## Layer 7: REQ (Atomic Requirements)

**Artifact**: `docs/REQ/api/notification/REQ-045_send_notification.md`
**Required Tags**: `@brd` through `@sys` (6 tags)
**Format**: Markdown

**Content Example**:
```markdown
# REQ-045: Send Notification Atomic Requirement

## 1. Requirement Statement

The system SHALL provide an API endpoint to send notifications with the following parameters:
- Recipient (required, string, format: EMAIL or PHONE)
- Subject (required, string, max 200 characters)
- Body (required, string, max 5000 characters)
- Channel (required, enum: EMAIL, SMS, PUSH)
- Priority (required, enum: LOW, NORMAL, HIGH)

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 7):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
```

**Tag Explanation**:
- All upstream tags from Layers 1-6
- SYS-012:FUNC-001 - API endpoint requirement
- SYS-012:PERF-001 - Performance constraint

**Upstream Sources**:
- BRD-009, PRD-016, EARS-012, BDD-015, ADR-033, SYS-012

**Downstream Artifacts**:
- SPEC-018 (Technical specification)
- TASKS-015 (Implementation tasks)
```

**Tag Analysis**:
- Tag count: 6 (cumulative: @brd through @sys)
- Includes ALL upstream tags from Layers 1-6
- Ready for SPEC creation (may skip IMPL for single-component task)
- Complete audit trail from business to technical requirement

---

## Layer 8: IMPL (Implementation Plan) [OPTIONAL]

**Artifact**: `docs/IMPL/IMPL-003_notification_integration_phase2.md`
**Required Tags**: `@brd` through `@req` (7 tags)
**Format**: Markdown

**Content Example**:
```markdown
# IMPL-003: Notification Integration Phase 2 Implementation Plan

## 2. Implementation Phases

### Phase 2.1: Notification Service Development
- Team: Backend Team
- Deliverables: SPEC-018, TASKS-015, notification_service.py

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 8):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec, REQ-045:validation-logic
```

**Tag Explanation**:
- All upstream tags from Layers 1-7
- REQ-045:interface-spec, validation-logic - Atomic requirements being implemented

**Note**: IMPL is optional layer. Include @impl tags in downstream only if IMPL exists.
```

**Tag Analysis**:
- Tag count: 7 (cumulative: @brd through @req)
- Optional layer - only created for complex multi-team projects
- If present, downstream artifacts must include @impl tags

---

## Layer 9: CTR (API Contracts) [OPTIONAL]

**Artifact**: `docs/CTR/CTR-005_notification_service_api.md` + `.yaml`
**Required Tags**: `@brd` through `@impl` (8 tags)
**Format**: Markdown + YAML (dual-file)

**Content Example** (CTR-005_notification_service_api.md):
```markdown
# CTR-005: Notification Service API Contract

## 1. Contract Overview

REST API contract for notification service.

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 9):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec
@impl: IMPL-003:phase2
```

**Tag Explanation**:
- All upstream tags from Layers 1-8
- IMPL-003:phase2 - Implementation phase containing this contract

**Note**: CTR is optional layer. Include @ctr tags in downstream only if CTR exists.
```

**YAML Schema** (CTR-005_notification_service_api.yaml):
```yaml
openapi: 3.0.0
info:
  title: Notification Service API
  version: 1.0.0

# Traceability embedded in description
description: |
  Notification API for external provider integration.

  Traceability:
  - @brd: BRD-009:FR-015, BRD-009:NFR-006
  - @prd: PRD-016:FEATURE-003
  - @ears: EARS-012:EVENT-001, EARS-012:EVENT-002
  - @bdd: BDD-015:scenario-send-notification
  - @adr: ADR-033
  - @sys: SYS-012:FUNC-001, SYS-012:PERF-001
  - @req: REQ-045:interface-spec
  - @impl: IMPL-003:phase2

paths:
  /api/v1/notifications:
    post:
      summary: Send notification
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [recipient, subject, body, channel, priority]
```

**Tag Analysis**:
- Tag count: 8 (cumulative: @brd through @impl)
- Optional layer - only for interface requirements
- Dual-file format required (.md + .yaml)
- If present, downstream artifacts must include @ctr tags

---

## Layer 10: SPEC (Technical Specification)

**Artifact**: `docs/SPEC/services/SPEC-018_notification_service.yaml`
**Required Tags**: `@brd` through `@req` + optional `@impl`, `@ctr` (7-9 tags)
**Format**: YAML with `cumulative_tags` section

**Content Example**:
```yaml
# SPEC-018: Notification Service Technical Specification

spec_id: SPEC-018
title: "Notification Service Technical Specification"
version: "1.0.0"
status: active

# Cumulative Tagging Hierarchy (Layer 10)
# Required: 7 upstream tags (BRD through REQ)
# Optional: IMPL, CTR (include if they exist in chain)
cumulative_tags:
  brd: "BRD-009:FR-015, BRD-009:NFR-006"
  prd: "PRD-016:FEATURE-003"
  ears: "EARS-012:EVENT-001, EARS-012:EVENT-002"
  bdd: "BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid"
  adr: "ADR-033"
  sys: "SYS-012:FUNC-001, SYS-012:PERF-001"
  req: "REQ-045:interface-spec, REQ-045:validation-logic"
  impl: "IMPL-003:phase2"  # Optional - included because IMPL-003 exists
  ctr: "CTR-005"  # Optional - included because CTR-005 exists

implementation:
  service_name: notification_service
  language: python
  framework: fastapi

  interfaces:
    rest_api:
      contract_ref: CTR-005  # References optional CTR layer
      endpoint: /api/v1/notifications
      method: POST

  validation:
    - Validate recipient format (EMAIL or PHONE pattern)
    - Check subject length <= 200 characters
    - Verify body length <= 5000 characters
    - Validate channel enum
    - Check priority enum

  error_handling:
    - MISSING_RECIPIENT: 400
    - INVALID_CHANNEL: 400
    - PROVIDER_ERROR: 502
    - TIMEOUT: 504
```

**Tag Analysis**:
- Tag count: 9 (cumulative: @brd through @req + optional @impl, @ctr)
- SPEC uses YAML `cumulative_tags:` mapping (not markdown tags)
- Includes optional layers because they exist in this example
- Contract reference: `contract_ref: CTR-005` links to optional CTR layer

---

## Layer 11: TASKS (Code Generation Plans)

**Artifact**: `docs/TASKS/TASKS-015_notification_service_implementation.md`
**Required Tags**: `@brd` through `@spec` (8-10 tags)
**Format**: Markdown

**Content Example**:
```markdown
# TASKS-015: Notification Service Implementation Tasks

## 2. Implementation Plan

### Task 1: REST API Endpoint
**File**: `src/services/notification_service.py`
**Function**: `send_notification()`
**Dependencies**: SPEC-018, CTR-005
**Acceptance**: BDD-015:scenario-send-notification passes

### Task 2: Validation Logic
**File**: `src/services/notification_validator.py`
**Function**: `validate_notification_params()`
**Dependencies**: REQ-045, SPEC-018
**Acceptance**: All validation rules enforced

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 11):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec, REQ-045:validation-logic
@impl: IMPL-003:phase2
@ctr: CTR-005
@spec: SPEC-018
```

**Tag Explanation**:
- All upstream tags from Layers 1-10
- SPEC-018 - Technical specification being implemented
- CTR-005, IMPL-003 - Optional layers included because they exist
```

**Tag Analysis**:
- Tag count: 10 (cumulative: @brd through @spec including optionals)
- Includes optional layers (@impl, @ctr) because they exist in chain
- Ready for code implementation

---

## Layer 12: IPLAN (Implementation Work Plans)

**Artifact**: `work_plans/implement_notification_service_20251113_120000.md`
**Required Tags**: `@brd` through `@tasks` (9-11 tags)
**Format**: Markdown

**Content Example**:
```markdown
# Implementation Work Plan: Notification Service
**Session**: 2025-11-13 12:00:00
**Duration**: 2 hours
**Engineer**: Backend Team

## Phase 1: Setup (15 min)
```bash
cd src/services
touch notification_service.py notification_validator.py
```

## Phase 2: Implementation (90 min)
- Implement send_notification() per SPEC-018
- Implement validate_notification_params() per REQ-045
- Add error handling per SPEC-018 error codes

## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 12):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec, REQ-045:validation-logic
@impl: IMPL-003:phase2
@ctr: CTR-005
@spec: SPEC-018
@tasks: TASKS-015
```

**Tag Explanation**:
- All upstream tags from Layers 1-11
- TASKS-015 - Implementation tasks for this session
```

**Tag Analysis**:
- Tag count: 11 (cumulative: @brd through @tasks including optionals)
- Session-specific implementation plan
- Includes ALL upstream tags from previous layers

---

## Layer 13: Code (Implementation)

**Artifact**: `src/services/notification_service.py`
**Required Tags**: `@brd` through `@tasks` (9-11 tags)
**Format**: Python docstrings

**Content Example**:
```python
"""Notification service implementation.

@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec, REQ-045:validation-logic
@impl: IMPL-003:phase2
@ctr: CTR-005
@spec: SPEC-018
@tasks: TASKS-015
@impl-status: complete
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter()


class NotificationRequest(BaseModel):
    """Notification request model.

    Implements: CTR-005 (API Contract)
    Validates: REQ-045 (Atomic Requirement)
    """
    recipient: str
    subject: str
    body: str
    channel: Literal["EMAIL", "SMS", "PUSH"]
    priority: Literal["LOW", "NORMAL", "HIGH"]


@router.post("/api/v1/notifications")
async def send_notification(notification: NotificationRequest):
    """Send notification endpoint.

    Implements SPEC-018 notification service specification.
    Satisfies BDD-015:scenario-send-notification acceptance criteria.
    Enforces SYS-012:PERF-001 latency requirement (100ms).

    Args:
        notification: Notification parameters per CTR-005

    Returns:
        Notification confirmation with notification ID

    Raises:
        HTTPException: 400 for validation errors per SPEC-018
        HTTPException: 502 for provider errors per SPEC-018
    """
    # Implementation omitted for brevity
    pass
```

**Tag Analysis**:
- Tag count: 11 (cumulative: @brd through @tasks including optionals)
- Tags in module docstring (top of file)
- `@impl-status: complete` indicates implementation finished
- Includes ALL upstream tags from Layers 1-11

---

## Layer 14: Tests (Test Suites)

**Artifact**: `tests/services/test_notification_service.py`
**Required Tags**: `@brd` through `@code` (10-12 tags)
**Format**: Python docstrings

**Content Example**:
```python
"""Test suite for notification service.

@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec, REQ-045:validation-logic
@impl: IMPL-003:phase2
@ctr: CTR-005
@spec: SPEC-018
@tasks: TASKS-015
@code: src/services/notification_service.py
@impl-status: complete
"""

import pytest
from fastapi.testclient import TestClient
from src.services.notification_service import router, NotificationRequest

client = TestClient(router)


def test_send_valid_notification():
    """Test sending valid notification.

    Validates: BDD-015:scenario-send-notification
    Contract: CTR-005 request/response format
    Performance: SYS-012:PERF-001 (< 100ms)
    """
    notification = {
        "recipient": "user@example.com",
        "subject": "Test Message",
        "body": "This is a test notification.",
        "channel": "EMAIL",
        "priority": "HIGH"
    }

    response = client.post("/api/v1/notifications", json=notification)

    assert response.status_code == 200
    assert response.json()["notification_id"]
    # Performance assertion omitted for brevity


def test_reject_missing_recipient():
    """Test rejection of missing recipient.

    Validates: BDD-015:scenario-reject-invalid
    Contract: CTR-005 error response format
    Requirement: REQ-045:validation-logic
    """
    notification = {
        "recipient": "",
        "subject": "Test Message",
        "body": "This is a test notification.",
        "channel": "EMAIL",
        "priority": "HIGH"
    }

    response = client.post("/api/v1/notifications", json=notification)

    assert response.status_code == 400
    assert response.json()["error"] == "MISSING_RECIPIENT"
```

**Tag Analysis**:
- Tag count: 12 (cumulative: @brd through @code including optionals)
- Includes `@code:` tag referencing implementation file
- Tags in module docstring
- Validates BDD scenarios (BDD-015)
- Tests contract compliance (CTR-005)

---

## Layer 15: Validation (Validation Results)

**Artifact**: `docs/validation/VALIDATION-015_notification_service.md`
**Required Tags**: All upstream (10-15 tags)
**Format**: Markdown

**Content Example**:
```markdown
# VALIDATION-015: Notification Service Validation Results

**Validation Date**: 2025-11-13
**Engineer**: QA Team
**Status**: PASSED

## 1. BDD Scenario Execution

### BDD-015:scenario-send-notification
- **Status**: PASSED
- **Execution Time**: 87ms (< 100ms requirement per SYS-012:PERF-001)
- **Contract Compliance**: CTR-005 validated
- **Requirement Coverage**: REQ-045:interface-spec satisfied

### BDD-015:scenario-reject-invalid
- **Status**: PASSED
- **Error Handling**: SPEC-018 error codes validated
- **Contract Compliance**: CTR-005 error schema validated

## 2. Contract Testing

### CTR-005 Compliance
- **Request Schema**: PASSED
- **Response Schema**: PASSED
- **Error Schema**: PASSED

## 3. Traceability Validation

**Traceability Check**: PASSED
- All tags validated from BRD-009 through test_notification_service.py
- No gaps in cumulative tag chain
- Tag count compliance: 12 tags in test layer

## 7. Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 15):
```markdown
@brd: BRD-009:FR-015, BRD-009:NFR-006
@prd: PRD-016:FEATURE-003
@ears: EARS-012:EVENT-001, EARS-012:EVENT-002
@bdd: BDD-015:scenario-send-notification, BDD-015:scenario-reject-invalid
@adr: ADR-033
@sys: SYS-012:FUNC-001, SYS-012:PERF-001
@req: REQ-045:interface-spec, REQ-045:validation-logic
@impl: IMPL-003:phase2
@ctr: CTR-005
@spec: SPEC-018
@tasks: TASKS-015
@iplan: implement_notification_service_20251113_120000.md
@code: src/services/notification_service.py
@tests: tests/services/test_notification_service.py
```

**Validation Summary**:
- Complete audit trail from BRD-009 through validation
- All 14 layers validated (Layers 0-15, excluding Strategy)
- 14 cumulative tags verified
- No gaps in traceability chain
- Regulatory compliance: audit trail complete
```

**Tag Analysis**:
- Tag count: 14 (cumulative: all layers excluding Strategy)
- Includes ALL upstream tags from Layers 1-14
- Complete end-to-end traceability validation
- Ready for production deployment

---

## Summary: Complete Cumulative Tagging Chain

### Tag Progression by Layer

```
Layer 0  (Strategy)      ->  0 tags  [External]
Layer 1  (BRD)           ->  0 tags  [Top level]
Layer 2  (PRD)           ->  1 tag   [@brd]
Layer 3  (EARS)          ->  2 tags  [@brd, @prd]
Layer 4  (BDD)           ->  3 tags  [@brd, @prd, @ears]
Layer 5  (ADR)           ->  4 tags  [+ @bdd]
Layer 6  (SYS)           ->  5 tags  [+ @adr]
Layer 7  (REQ)           ->  6 tags  [+ @sys]
Layer 8  (IMPL)          ->  7 tags  [+ @req] *optional*
Layer 9  (CTR)           ->  8 tags  [+ @impl] *optional*
Layer 10 (SPEC)          ->  7-9 tags [+ optional @impl, @ctr]
Layer 11 (TASKS)         ->  8-10 tags [+ @spec]
Layer 12 (IPLAN)   ->  9-11 tags [+ @tasks]
Layer 13 (Code)          ->  9-11 tags [+ @IPLAN]
Layer 14 (Tests)         ->  10-12 tags [+ @code]
Layer 15 (Validation)    ->  10-15 tags [all upstream]
```

### Cumulative Tagging Benefits Demonstrated

1. **Complete Audit Trail**
   - Every artifact traces back to BRD-009 business requirement
   - Full justification chain from business need to production code

2. **Impact Analysis**
   - If BRD-009:FR-015 changes, immediately identify affected:
     * PRD-016 (product requirements)
     * EARS-012 (formal requirements)
     * BDD-015 (test scenarios)
     * ADR-033 (architecture)
     * SYS-012, REQ-045, SPEC-018, TASKS-015
     * notification_service.py (code)
     * test_notification_service.py (tests)

3. **Regulatory Compliance**
   - Audit requirements satisfied for regulated industries
   - Complete traceability from business requirements to validation
   - No orphaned code or requirements

4. **Automated Validation**
   - `validate_tags_against_docs.py --validate-cumulative --strict`
   - Enforces no gaps in tag chain
   - Verifies tag count per layer
   - Pre-commit hooks prevent non-compliant code

5. **Change Management**
   - Know exactly what breaks when upstream changes occur
   - Update propagation is traceable
   - Version control of traceability tags

---

## Validation Commands

### Extract Tags
```bash
python scripts/extract_tags.py \
  --source src/ docs/ tests/ \
  --output docs/generated/tags.json
```

### Validate Cumulative Tagging
```bash
python scripts/validate_tags_against_docs.py \
  --source src/ docs/ tests/ \
  --docs docs/ \
  --validate-cumulative \
  --strict
```

### Expected Output
```
Indexed 15 documents
Validated 15 artifacts
No validation errors found
Cumulative tagging validation passed

COVERAGE METRICS
================
Documents Referenced: 15/15 (100%)
Requirements Referenced: 24/24 (100%)
Files with Tags: 15/15 (100%)
```

---

## References

- **Core Documentation**: [TRACEABILITY.md](./TRACEABILITY.md#cumulative-tagging-hierarchy)
- **Workflow Guide**: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
- **Validation Setup**: [TRACEABILITY_SETUP.md](./TRACEABILITY_SETUP.md#cumulative-tagging-validation)
- **Doc-Flow Skill**: [.claude/skills/doc-flow/SKILL.md](../.claude/skills/doc-flow/SKILL.md#25-cumulative-tagging-hierarchy)
- **Validation Script**: [scripts/validate_tags_against_docs.py](./scripts/validate_tags_against_docs.py)

---

**Document Status**: Reference Example
**Purpose**: End-to-end cumulative tagging demonstration
**Usage**: Training, validation pattern reference, CI/CD setup guidance
