# Minimal End-to-End Tagging Example (TYPE-NN)

## Purpose
- Demonstrate a compact, vendor-neutral, end-to-end traceability chain using TYPE-NN placeholders.
- Show only what’s necessary to understand cumulative tagging across layers.

## Layers and Artifacts (One Chain)

### Layer 1: BRD (Business Requirements)
- BRD-NN: Business objective to process user requests reliably and quickly.
- Tags: none (top level).

### Layer 2: PRD (Product Requirements)
- PRD-NN: Product requirement to expose request submission via UI/API.
- Tags:
  - @brd: BRD-NN

### Layer 3: EARS (Formal Requirements)
- EARS-NN:
  - WHEN a user submits a valid request, THE system SHALL validate fields WITHIN 100ms.
  - WHEN validation succeeds, THE system SHALL accept and enqueue the request WITHIN 200ms.
- Tags:
  - @brd: BRD-NN
  - @prd: PRD-NN

### Layer 4: BDD (Acceptance Tests)
```gherkin
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS.NN.24.NN

Feature: Request processing
  Scenario: Accept valid request
    Given a logged-in user
    When the user submits a valid request
    Then the request is accepted
```

### Layer 5: ADR (Architecture Decisions)
- ADR-NN: Choose event-driven queue for request intake.
- Tags:
  - @brd: BRD-NN, @prd: PRD-NN, @ears: EARS.NN.24.NN, @bdd: BDD.NN.13.NN

### Layer 6: SYS (System Requirements)
- SYS-NN:
  - Provide POST /api/v1/requests.
  - Validate request in ≤100ms p95.
- Tags:
  - @brd: BRD-NN, @prd: PRD-NN, @ears: EARS.NN.24.NN, @bdd: BDD.NN.13.NN, @adr: ADR-NN

### Layer 7: REQ (Atomic Requirement)
- REQ-NN: Provide API endpoint to submit requests with required fields.
- Tags:
  - @brd: BRD-NN, @prd: PRD-NN, @ears: EARS.NN.24.NN, @bdd: BDD.NN.13.NN, @adr: ADR-NN, @sys: SYS.NN.25.NN

### Layer 10: SPEC (Technical Specification)
```yaml
spec_id: SPEC-NN
title: "Request Service"
status: active
cumulative_tags:
  brd: BRD-NN
  prd: PRD-NN
  ears: EARS.NN.24.NN
  bdd: BDD.NN.13.NN
  adr: ADR-NN
  sys: SYS.NN.25.NN
  req: REQ.NN.NN.NN
implementation:
  language: python
  framework: fastapi
  rest_api:
    endpoint: /api/v1/requests
    method: POST
```

### Layer 11: TASKS (Implementation Tasks)
```markdown
# TASKS-NN: Implement submission endpoint
## Plan
- Add handler `POST /api/v1/requests` per SPEC-NN
- Validate fields, return 202 on success
## Tags
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS.NN.24.NN
@bdd: BDD.NN.13.NN
@adr: ADR-NN
@sys: SYS.NN.25.NN
@req: REQ.NN.NN.NN
@spec: SPEC-NN
```

### Layer 13: Code (Implementation)
```python
"""Request service implementation
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS.NN.24.NN
@bdd: BDD.NN.13.NN
@adr: ADR-NN
@sys: SYS.NN.25.NN
@req: REQ.NN.NN.NN
@spec: SPEC-NN
@tasks: TASKS.NN.NN.NN
@impl-status: complete
"""
from fastapi import APIRouter
router = APIRouter()

@router.post("/api/v1/requests")
async def submit_request(payload: dict):
    return {"status": "accepted", "id": "REQ-123"}
```

### Layer 14: Tests (Test Suites)
```python
"""Test: Request processing
@brd: BRD-NN
@prd: PRD-NN
@ears: EARS.NN.24.NN
@bdd: BDD.NN.13.NN
@adr: ADR-NN
@sys: SYS.NN.25.NN
@req: REQ.NN.NN.NN
@spec: SPEC-NN
@tasks: TASKS.NN.NN.NN
@code: src/services/request_service.py
"""
def test_submit_request_accepts_valid_payload():
    assert True
```

### Layer 15: Validation (Results)
- All cumulative tags present from BRD through Tests.
- No gaps detected; coverage acceptable.

## Tag Progression Summary
```
Layer 1  BRD  -> 0 tags
Layer 2  PRD  -> @brd
Layer 3  EARS -> @brd, @prd
Layer 4  BDD  -> @brd, @prd, @ears
Layer 5  ADR  -> +@bdd
Layer 6  SYS  -> +@adr
Layer 7  REQ  -> +@sys
Layer 10 SPEC -> +@req (+@impl/@ctr if exist)
Layer 11 TASKS-> +@spec
Layer 13 Code -> +@tasks
Layer 14 Tests-> +@code
Layer 15 Valid-> all upstream tags
```

