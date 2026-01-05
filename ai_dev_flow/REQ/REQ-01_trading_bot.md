<!--
AI_CONTEXT_START
Role: AI Requirements Engineer
Objective: Create a streamlined MVP Atomic Requirement.
Constraints:
- Define exactly ONE atomic requirement.
- Ensure SPEC-ready clarity (Inputs, Processing, Outputs).
- Use distinct P1/P2 priorities.
- Do not create external references to non-existent files.
AI_CONTEXT_END
-->
---
title: "REQ-MVP-TEMPLATE: Atomic Requirements Document (MVP Version)"
tags:
  - req-template
  - mvp-template
  - layer-7-artifact
custom_fields:
  document_type: template
  artifact_type: REQ
  layer: 7
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  template_variant: mvp
---

> **MVP Template** — Single-file, streamlined REQ for rapid MVP development.
> Use this template for MVP atomic requirements (10-20 core requirements).
> For comprehensive requirements (50+ detailed specs), use `REQ-TEMPLATE.md`.

> **Validation Note**: MVP templates are intentionally streamlined and will show validation errors when run against full template validators (e.g., `validate_req_template.sh`). This is expected behavior. See `scripts/README.md` → "MVP Template Validation" for guidance.

# REQ-01: [Requirement Title]

**⚠️ MVP Scope**: This requirement document focuses on essential, SPEC-ready requirements for MVP delivery.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Implemented |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DD |
| **Last Updated** | YYYY-MM-DD |
| **Author** | [Author name] |
| **Priority** | P1 (Critical) / P2 (High) / P3 (Medium) |
| **Category** | Functional / Security / Performance |
| **Source Document** | [PRD-NN / SYS-NN / EARS-NN reference] |
| **Verification Method** | BDD / Unit Test / Integration Test |
| **SPEC-Ready Score** | [Score]/100 (Target: ≥85 for MVP) |

---

## 2. Requirement Description

### 2.1 Statement

**The system SHALL** [precise, atomic requirement statement that defines exactly one specific behavior].

### 2.2 Context

[1-2 paragraphs: Why this requirement exists and what problem it solves]

### 2.3 Use Case

**Primary Flow**:
1. [Actor] initiates [action/trigger]
2. System validates [precondition]
3. System executes [core behavior]
4. System returns [outcome]

**Error Flow**:
- When [error condition], system SHALL [error behavior]

---

## 3. Functional Specification

### 3.1 Core Functionality

**Required Capabilities**:
- [Capability 1]: [Specific behavior with measurable outcome]
- [Capability 2]: [Specific behavior with measurable outcome]

### 3.2 Business Rules

**ID Format**: `REQ-01.21.SS` (Validation Rule)

| Rule ID | Condition | Action |
|---------|-----------|--------|
| REQ-01.21.01 | IF [condition] | THEN [action/outcome] |
| REQ-01.21.02 | IF [condition] | THEN [action/outcome] |

### 3.3 Input/Output Specification

**Inputs**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| [param1] | [string/int/etc] | Yes/No | [rules] | [what it is] |
| [param2] | [string/int/etc] | Yes/No | [rules] | [what it is] |

**Outputs**:

| Field | Type | Description |
|-------|------|-------------|
| [field1] | [string/int/etc] | [what it contains] |
| [field2] | [string/int/etc] | [what it contains] |

---

## 4. Interface Definition

### 4.1 API Contract (if applicable)

**Endpoint**: `[METHOD] /api/v1/[resource]`

**Request**:
```json
{
  "field1": "value",
  "field2": 123
}
```

**Response (Success)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "result": "value"
  }
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Description"
  }
}
```

### 4.2 Data Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime

class RequestModel(BaseModel):
    """Request data structure."""
    field1: str = Field(..., min_length=1, max_length=100)
    field2: int = Field(..., ge=0)

class ResponseModel(BaseModel):
    """Response data structure."""
    id: str
    result: str
    timestamp: datetime
```

---

## 5. Error Handling

### 5.1 Error Catalog

| Error Code | HTTP Status | Condition | User Message | System Action |
|------------|-------------|-----------|--------------|---------------|
| [ERR_001] | 400 | Invalid input | [Message] | Log, return error |
| [ERR_002] | 404 | Resource not found | [Message] | Log, return error |
| [ERR_003] | 500 | Processing failed | [Message] | Log, alert, retry |

### 5.2 Recovery Strategy

| Error Type | Retry? | Fallback | Alert |
|------------|--------|----------|-------|
| Validation error | No | Return error | No |
| Transient failure | Yes (3x) | Queue/Cache | After retries |
| Permanent failure | No | Graceful error | Yes |

---

## 6. Quality Attributes

**ID Format**: `REQ-01.02.SS` (Quality Attribute)

### 6.1 Performance (REQ-01.02.01)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time (p95) | < [X]ms | APM traces |
| Throughput | [X] req/sec | Load test |

### 6.2 Security (REQ-01.02.02)

- [ ] Input validation: All inputs validated
- [ ] Authentication: [Required/Optional]
- [ ] Authorization: [Role-based check]
- [ ] Data protection: [PII handling]

### 6.3 Reliability (REQ-01.02.03)

- Error rate: < [X]% of operations
- Idempotency: [Required for POST/PUT operations]

---

## 7. Configuration

### 7.1 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| [CONFIG_1] | [type] | [default] | [what it controls] |
| [CONFIG_2] | [type] | [default] | [what it controls] |

### 7.2 Feature Flags (if applicable)

| Flag | Default | Description |
|------|---------|-------------|
| [FLAG_NAME] | false | [When to enable] |

---

## 8. Testing Requirements

### 8.1 Unit Tests

| Test Case | Input | Expected Output | Coverage |
|-----------|-------|-----------------|----------|
| [Happy path] | [valid input] | [expected result] | Core logic |
| [Edge case] | [boundary input] | [expected behavior] | Boundary |
| [Error case] | [invalid input] | [error response] | Error handling |

### 8.2 Integration Tests

- [ ] API endpoint responds correctly
- [ ] Database operations work
- [ ] External service integration works

### 8.3 BDD Scenarios

**Feature**: [Feature name]
**File**: `BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature`

| Scenario | Priority | Status |
|----------|----------|--------|
| [Scenario 1] | P1 | [Pending/Passed] |
| [Scenario 2] | P1 | [Pending/Passed] |

---

## 9. Acceptance Criteria

**ID Format**: `REQ-01.06.SS` (Acceptance Criteria)

### 9.1 Functional Acceptance

| Criteria ID | Criterion | Measurable Outcome | Status |
|-------------|-----------|-------------------|--------|
| REQ-01.06.01 | [Criterion 1] | [Measurable outcome] | [ ] |
| REQ-01.06.02 | [Criterion 2] | [Measurable outcome] | [ ] |
| REQ-01.06.03 | [Criterion 3] | [Measurable outcome] | [ ] |

### 9.2 Quality Acceptance

| Criteria ID | Criterion | Target | Status |
|-------------|-----------|--------|--------|
| REQ-01.06.04 | Performance target | p95 < [X]ms | [ ] |
| REQ-01.06.05 | Security | No critical vulnerabilities | [ ] |
| REQ-01.06.06 | Test coverage | ≥ [X]% | [ ] |

---

## 10. Traceability

### 10.1 Upstream References

| Source | Document | Section |
|--------|----------|---------|
| BRD | BRD.NN | [Relevant section] |
| PRD | PRD.NN | [Relevant section] |
| SYS | SYS.NN | [Relevant section] |
| EARS | EARS.NN | [Relevant requirement] |

### 10.2 Downstream Artifacts

| Artifact | Status | Relationship |
|----------|--------|--------------|
| SPEC-NN | TBD | Technical specification |
| TASKS-NN | TBD | Implementation tasks |

### 10.3 Traceability Tags

```markdown
@brd: BRD.NN.TT.SS
@prd: PRD.NN.TT.SS
@sys: SYS.NN.TT.SS
@ears: EARS.NN.24.SS
@adr: ADR.NN.TT.SS
```

> **Note**: Document references use dash notation (`ADR-NN`). Element references within documents use 4-segment dot notation (`ADR.NN.TT.SS`).

---

## 11. Implementation Notes

### 11.1 Technical Approach

[Brief description of recommended implementation approach]

### 11.2 Code Location

- **Primary**: `src/[module]/[component].py`
- **Tests**: `tests/[module]/test_[component].py`

### 11.3 Dependencies

| Package/Service | Version | Purpose |
|-----------------|---------|---------|
| [dependency1] | [version] | [why needed] |
| [dependency2] | [version] | [why needed] |

---

## Migration to Full REQ Template

### When to Migrate

Migrate from MVP REQ to full `REQ-TEMPLATE.md` when:
- [ ] Requirement complexity requires 12-section format
- [ ] Need comprehensive interface protocols (Python)
- [ ] Full error catalog with state machines required
- [ ] SPEC generation requires maximum detail
- [ ] Compliance requires comprehensive test coverage

### Migration Steps

1. **Create new document**: Copy `REQ-TEMPLATE.md` to `REQ-01_{slug}.md`
2. **Transfer core content**: Map MVP sections to full template
3. **Expand detailed sections**:
   - Full interface protocols (Python classes)
   - Complete data schemas (JSON, Pydantic, SQLAlchemy)
   - Comprehensive error catalogs with circuit breakers
   - Detailed configuration specifications
4. **Add missing sections**: EARS statements, verification matrix
5. **Update traceability**: Ensure SPEC documents reference new REQ
6. **Archive MVP version**: Move to archive with "superseded" note
7. **Run validation**: Execute `./scripts/validate_req_template.sh` on new document

### Section Mapping (MVP → Full)

| MVP Section | Full Template Section |
|-------------|-----------------------|
| 1. Document Control | 1. Document Control |
| 2. Requirement Description | 2. Requirement Statements (expand) |
| 3. Functional Specification | 3. Functional Specification (expand) |
| 4. Interface Definition | 4. Interface Specifications (full protocols) |
| 5. Error Handling | 5. Error Handling (full catalog) |
| 6. Quality Attributes | 6. Configuration Specifications (expand) |
| 7. Configuration | 7. Quality Attributes |
| 8. Testing Requirements | 8. Implementation Guidance |
| 9. Acceptance Criteria | 9. Acceptance Criteria |
| 10. Traceability | 10. Verification Methods + 11. Traceability |
| 11. Implementation Notes | 12. Change History |

---

**Document Version**: 0.1.0
**Template Version**: 1.0 (MVP)
**Last Updated**: YYYY-MM-DD

---

> **MVP Template Notes**:
> - This template is ~350 lines (vs 1,394 lines for full REQ)
> - Single file - no sectioning
> - Focus on SPEC-ready, atomic requirements
> - Maintains ai_dev_flow framework compliance
> - Expands to full REQ-TEMPLATE.md structure for complex requirements
